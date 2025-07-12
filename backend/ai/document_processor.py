"""
AI Document Processing Service for the Customs Broker Portal.

This module provides AI-powered document processing capabilities using Claude 3.5 Sonnet
for intelligent customs document analysis, OCR, field extraction, and classification.
"""

import asyncio
import base64
import io
import json
import logging
import os
import tempfile
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any, Union

import aiofiles
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
from PIL import Image, ImageEnhance, ImageFilter
import anthropic
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload

from models.documents import Document
from models.ai_document_processing import (
    AIDocumentProcessing, ExtractedField, ProcessingTemplate,
    ProcessingStatus, DocumentTypeDetection, ExtractionConfidence
)
from schemas.ai_document_processing import (
    DocumentProcessingRequest, DocumentProcessingResponse,
    ExtractedFieldData, AIAnalysisResult
)


logger = logging.getLogger(__name__)


class DocumentProcessingError(Exception):
    """Custom exception for document processing errors."""
    pass


class OCRProcessor:
    """OCR processing utilities for document text extraction."""
    
    def __init__(self):
        """Initialize OCR processor with optimal settings."""
        self.tesseract_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:-/$%()[]{}@#&*+= '
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: PIL Image object
            
        Returns:
            Preprocessed PIL Image
        """
        try:
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Convert PIL to OpenCV format
            cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
            
            # Apply noise reduction
            cv_image = cv2.medianBlur(cv_image, 3)
            
            # Apply adaptive thresholding
            cv_image = cv2.adaptiveThreshold(
                cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY),
                255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY,
                11,
                2
            )
            
            # Convert back to PIL
            processed_image = Image.fromarray(cv_image)
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(processed_image)
            processed_image = enhancer.enhance(1.5)
            
            # Sharpen image
            processed_image = processed_image.filter(ImageFilter.SHARPEN)
            
            return processed_image
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}, using original image")
            return image
    
    async def extract_text_from_image(self, image: Image.Image) -> Tuple[str, float]:
        """
        Extract text from image using OCR.
        
        Args:
            image: PIL Image object
            
        Returns:
            Tuple of (extracted_text, confidence_score)
        """
        try:
            # Preprocess image
            processed_image = self.preprocess_image(image)
            
            # Extract text with confidence data
            data = pytesseract.image_to_data(
                processed_image,
                config=self.tesseract_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            # Extract text
            text = pytesseract.image_to_string(processed_image, config=self.tesseract_config)
            
            return text.strip(), avg_confidence / 100.0  # Convert to 0-1 scale
            
        except Exception as e:
            logger.error(f"OCR text extraction failed: {e}")
            raise DocumentProcessingError(f"OCR failed: {str(e)}")
    
    async def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, float]:
        """
        Extract text from PDF using OCR.
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Tuple of (extracted_text, average_confidence)
        """
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            
            all_text = []
            all_confidences = []
            
            for page_num, image in enumerate(images, 1):
                try:
                    text, confidence = await self.extract_text_from_image(image)
                    if text.strip():
                        all_text.append(f"--- Page {page_num} ---\n{text}")
                        all_confidences.append(confidence)
                except Exception as e:
                    logger.warning(f"Failed to process page {page_num}: {e}")
                    continue
            
            combined_text = "\n\n".join(all_text)
            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
            
            return combined_text, avg_confidence
            
        except Exception as e:
            logger.error(f"PDF OCR processing failed: {e}")
            raise DocumentProcessingError(f"PDF OCR failed: {str(e)}")


class ClaudeDocumentAnalyzer:
    """Claude AI integration for document analysis and field extraction."""
    
    def __init__(self, api_key: str):
        """Initialize Claude analyzer with API key."""
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-5-sonnet-20241022"
    
    def _get_document_type_prompt(self, text: str) -> str:
        """Generate prompt for document type detection."""
        return f"""
Analyze the following document text and determine the document type. 

Document types to classify:
- commercial_invoice: Commercial invoices for goods
- packing_list: Packing lists or shipping manifests
- bill_of_lading: Bills of lading or shipping documents
- certificate_of_origin: Certificates of origin
- airway_bill: Air waybills or air cargo documents
- customs_declaration: Customs declarations or forms
- insurance_certificate: Insurance certificates
- purchase_order: Purchase orders
- proforma_invoice: Proforma invoices
- unknown: If the document type cannot be determined

Document text:
{text[:3000]}...

Respond with ONLY a JSON object in this format:
{{
    "document_type": "detected_type",
    "confidence": 0.95,
    "reasoning": "Brief explanation of why this classification was chosen"
}}
"""
    
    def _get_field_extraction_prompt(self, text: str, document_type: str) -> str:
        """Generate prompt for field extraction based on document type."""
        
        field_definitions = {
            "commercial_invoice": [
                "invoice_number", "invoice_date", "seller_name", "seller_address",
                "buyer_name", "buyer_address", "total_amount", "currency",
                "payment_terms", "incoterms", "country_of_origin", "hs_codes",
                "item_descriptions", "quantities", "unit_prices", "line_totals"
            ],
            "packing_list": [
                "packing_list_number", "date", "shipper_name", "consignee_name",
                "total_packages", "total_weight", "total_volume", "package_types",
                "item_descriptions", "quantities", "weights", "dimensions"
            ],
            "bill_of_lading": [
                "bl_number", "date", "vessel_name", "voyage_number", "port_of_loading",
                "port_of_discharge", "shipper_name", "consignee_name", "notify_party",
                "container_numbers", "seal_numbers", "freight_terms"
            ],
            "certificate_of_origin": [
                "certificate_number", "issue_date", "exporter_name", "exporter_address",
                "consignee_name", "country_of_origin", "destination_country",
                "goods_description", "hs_codes", "issuing_authority"
            ]
        }
        
        fields = field_definitions.get(document_type, [
            "document_number", "date", "parties_involved", "amounts", "descriptions"
        ])
        
        return f"""
Extract structured data from this {document_type} document. Focus on accuracy and provide confidence scores.

Document text:
{text}

Extract the following fields (if present):
{', '.join(fields)}

For each field found, provide:
1. The exact value as it appears in the document
2. A normalized/cleaned version if applicable
3. Confidence score (0.0 to 1.0)
4. Location information if possible

Respond with ONLY a JSON object in this format:
{{
    "extracted_fields": [
        {{
            "field_name": "invoice_number",
            "field_type": "text",
            "field_value": "INV-2024-001",
            "field_value_normalized": "INV-2024-001",
            "confidence_score": 0.95,
            "page_number": 1,
            "bounding_box": null
        }}
    ],
    "overall_confidence": 0.87,
    "extraction_notes": "Brief notes about extraction quality"
}}
"""
    
    def _get_analysis_prompt(self, text: str, document_type: str) -> str:
        """Generate prompt for comprehensive document analysis."""
        return f"""
Perform a comprehensive analysis of this {document_type} document for customs compliance and processing.

Document text:
{text}

Provide analysis including:
1. Suggested HS codes for any goods mentioned
2. Compliance flags or potential issues
3. Key insights for customs processing
4. Risk assessment
5. Recommendations

Respond with ONLY a JSON object in this format:
{{
    "suggested_hs_codes": [
        {{
            "code": "8471.30.01",
            "description": "Portable digital automatic data processing machines",
            "confidence": 0.85,
            "reasoning": "Based on product description"
        }}
    ],
    "compliance_flags": [
        {{
            "flag": "missing_country_of_origin",
            "severity": "medium",
            "description": "Country of origin not clearly specified"
        }}
    ],
    "risk_assessment": {{
        "overall_risk": "low",
        "risk_factors": ["incomplete_documentation"],
        "risk_score": 0.3
    }},
    "key_insights": [
        "Document appears complete and well-formatted",
        "All required commercial invoice fields present"
    ],
    "recommendations": [
        "Verify country of origin with supplier",
        "Confirm HS code classification with customs expert"
    ]
}}
"""
    
    async def detect_document_type(self, text: str) -> Tuple[DocumentTypeDetection, float, str]:
        """
        Detect document type using Claude AI.
        
        Args:
            text: Extracted document text
            
        Returns:
            Tuple of (document_type, confidence, reasoning)
        """
        try:
            prompt = self._get_document_type_prompt(text)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            result = json.loads(response_text)
            
            document_type = DocumentTypeDetection(result["document_type"])
            confidence = float(result["confidence"])
            reasoning = result.get("reasoning", "")
            
            return document_type, confidence, reasoning
            
        except Exception as e:
            logger.error(f"Document type detection failed: {e}")
            return DocumentTypeDetection.UNKNOWN, 0.0, f"Error: {str(e)}"
    
    async def extract_fields(self, text: str, document_type: str) -> Tuple[List[Dict], float]:
        """
        Extract structured fields from document using Claude AI.
        
        Args:
            text: Extracted document text
            document_type: Detected document type
            
        Returns:
            Tuple of (extracted_fields_list, overall_confidence)
        """
        try:
            prompt = self._get_field_extraction_prompt(text, document_type)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            result = json.loads(response_text)
            
            extracted_fields = result.get("extracted_fields", [])
            overall_confidence = float(result.get("overall_confidence", 0.0))
            
            return extracted_fields, overall_confidence
            
        except Exception as e:
            logger.error(f"Field extraction failed: {e}")
            return [], 0.0
    
    async def analyze_document(self, text: str, document_type: str) -> Dict[str, Any]:
        """
        Perform comprehensive document analysis using Claude AI.
        
        Args:
            text: Extracted document text
            document_type: Detected document type
            
        Returns:
            Analysis results dictionary
        """
        try:
            prompt = self._get_analysis_prompt(text, document_type)
            
            message = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                temperature=0.1,
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_text = message.content[0].text
            result = json.loads(response_text)
            
            return result
            
        except Exception as e:
            logger.error(f"Document analysis failed: {e}")
            return {
                "suggested_hs_codes": [],
                "compliance_flags": [{"flag": "analysis_error", "severity": "high", "description": str(e)}],
                "risk_assessment": {"overall_risk": "unknown", "risk_factors": ["analysis_failed"], "risk_score": 1.0},
                "key_insights": [],
                "recommendations": ["Manual review required due to analysis error"]
            }


class AIDocumentProcessor:
    """Main AI document processing service."""
    
    def __init__(self, claude_api_key: str):
        """Initialize the AI document processor."""
        self.ocr_processor = OCRProcessor()
        self.claude_analyzer = ClaudeDocumentAnalyzer(claude_api_key)
    
    async def process_document(
        self,
        db: AsyncSession,
        document_id: int,
        force_reprocess: bool = False
    ) -> AIDocumentProcessing:
        """
        Process a document with AI analysis.
        
        Args:
            db: Database session
            document_id: ID of document to process
            force_reprocess: Whether to reprocess if already processed
            
        Returns:
            AIDocumentProcessing record
        """
        # Get document
        result = await db.execute(
            select(Document)
            .options(selectinload(Document.ai_processing))
            .where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise DocumentProcessingError(f"Document {document_id} not found")
        
        # Check if already processed
        existing_processing = None
        if document.ai_processing:
            existing_processing = document.ai_processing[0]
            if existing_processing.is_completed and not force_reprocess:
                return existing_processing
        
        # Create or update processing record
        if existing_processing:
            processing = existing_processing
            processing.processing_status = ProcessingStatus.PROCESSING
            processing.processing_started_at = datetime.utcnow()
            processing.error_message = None
            processing.error_details = None
        else:
            processing = AIDocumentProcessing(
                document_id=document_id,
                processing_status=ProcessingStatus.PROCESSING,
                processing_started_at=datetime.utcnow()
            )
            db.add(processing)
        
        await db.commit()
        await db.refresh(processing)
        
        try:
            # Extract text using OCR
            start_time = datetime.utcnow()
            
            if document.mime_type.startswith('image/'):
                # Process image file
                async with aiofiles.open(document.file_path, 'rb') as f:
                    image_data = await f.read()
                image = Image.open(io.BytesIO(image_data))
                ocr_text, ocr_confidence = await self.ocr_processor.extract_text_from_image(image)
            
            elif document.mime_type == 'application/pdf':
                # Process PDF file
                ocr_text, ocr_confidence = await self.ocr_processor.extract_text_from_pdf(document.file_path)
            
            else:
                raise DocumentProcessingError(f"Unsupported file type: {document.mime_type}")
            
            # Update processing record with OCR results
            processing.ocr_text = ocr_text
            processing.ocr_confidence = Decimal(str(ocr_confidence))
            
            # Detect document type
            doc_type, type_confidence, reasoning = await self.claude_analyzer.detect_document_type(ocr_text)
            processing.detected_document_type = doc_type
            processing.document_type_confidence = Decimal(str(type_confidence))
            
            # Extract fields
            extracted_fields_data, extraction_confidence = await self.claude_analyzer.extract_fields(
                ocr_text, doc_type.value
            )
            
            # Determine extraction confidence level
            if extraction_confidence >= 0.8:
                confidence_level = ExtractionConfidence.HIGH
            elif extraction_confidence >= 0.5:
                confidence_level = ExtractionConfidence.MEDIUM
            else:
                confidence_level = ExtractionConfidence.LOW
            
            processing.extraction_confidence = confidence_level
            
            # Store extracted data
            processing.extracted_data = {
                "fields": extracted_fields_data,
                "extraction_confidence": extraction_confidence,
                "document_type_reasoning": reasoning
            }
            
            # Create extracted field records
            for field_data in extracted_fields_data:
                extracted_field = ExtractedField(
                    processing_id=processing.id,
                    field_name=field_data.get("field_name", ""),
                    field_type=field_data.get("field_type", "text"),
                    field_value=field_data.get("field_value"),
                    field_value_normalized=field_data.get("field_value_normalized"),
                    confidence_score=Decimal(str(field_data.get("confidence_score", 0.0))),
                    page_number=field_data.get("page_number"),
                    bounding_box=field_data.get("bounding_box")
                )
                db.add(extracted_field)
            
            # Perform comprehensive analysis
            analysis_result = await self.claude_analyzer.analyze_document(ocr_text, doc_type.value)
            processing.ai_analysis = analysis_result
            
            # Extract suggested HS codes and compliance flags
            processing.suggested_hs_codes = [
                hs_code["code"] for hs_code in analysis_result.get("suggested_hs_codes", [])
            ]
            processing.compliance_flags = [
                flag["flag"] for flag in analysis_result.get("compliance_flags", [])
            ]
            
            # Determine if manual review is required
            risk_score = analysis_result.get("risk_assessment", {}).get("risk_score", 0.0)
            has_compliance_flags = len(processing.compliance_flags) > 0
            low_confidence = extraction_confidence < 0.7
            
            processing.requires_manual_review = (
                risk_score > 0.5 or has_compliance_flags or low_confidence
            )
            
            # Complete processing
            end_time = datetime.utcnow()
            processing.processing_completed_at = end_time
            processing.processing_duration_seconds = Decimal(
                str((end_time - start_time).total_seconds())
            )
            processing.processing_status = ProcessingStatus.COMPLETED
            
            await db.commit()
            await db.refresh(processing)
            
            logger.info(f"Successfully processed document {document_id}")
            return processing
            
        except Exception as e:
            # Handle processing error
            processing.processing_status = ProcessingStatus.FAILED
            processing.error_message = str(e)
            processing.error_details = {
                "error_type": type(e).__name__,
                "timestamp": datetime.utcnow().isoformat()
            }
            processing.processing_completed_at = datetime.utcnow()
            
            await db.commit()
            
            logger.error(f"Document processing failed for document {document_id}: {e}")
            raise DocumentProcessingError(f"Processing failed: {str(e)}")
    
    async def get_processing_status(
        self,
        db: AsyncSession,
        document_id: int
    ) -> Optional[AIDocumentProcessing]:
        """
        Get processing status for a document.
        
        Args:
            db: Database session
            document_id: Document ID
            
        Returns:
            AIDocumentProcessing record or None
        """
        result = await db.execute(
            select(AIDocumentProcessing)
            .options(selectinload(AIDocumentProcessing.extracted_fields))
            .where(AIDocumentProcessing.document_id == document_id)
            .order_by(AIDocumentProcessing.created_at.desc())
        )
        return result.scalar_one_or_none()
    
    async def reprocess_document(
        self,
        db: AsyncSession,
        document_id: int
    ) -> AIDocumentProcessing:
        """
        Reprocess a document (force reprocessing).
        
        Args:
            db: Database session
            document_id: Document ID
            
        Returns:
            AIDocumentProcessing record
        """
        return await self.process_document(db, document_id, force_reprocess=True)


# Initialize global processor instance
_processor_instance: Optional[AIDocumentProcessor] = None


def get_document_processor() -> AIDocumentProcessor:
    """Get the global document processor instance."""
    global _processor_instance
    
    if _processor_instance is None:
        claude_api_key = os.getenv("ANTHROPIC_API_KEY")
        if not claude_api_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is required")
        
        _processor_instance = AIDocumentProcessor(claude_api_key)
    
    return _processor_instance


async def process_document_async(document_id: int, db: AsyncSession) -> AIDocumentProcessing:
    """
    Async function for processing documents (can be used with Celery).
    
    Args:
        document_id: Document ID to process
        db: Database session
        
    Returns:
        AIDocumentProcessing record
    """
    processor = get_document_processor()
    return await processor.process_document(db, document_id)