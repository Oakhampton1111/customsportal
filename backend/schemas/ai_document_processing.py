"""
Pydantic schemas for AI document processing API endpoints.

This module contains request/response schemas for AI-powered document processing,
including field extraction, document analysis, and processing status.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Any, Union
from enum import Enum

from pydantic import BaseModel, Field, validator, ConfigDict

from models.ai_document_processing import (
    ProcessingStatus, DocumentTypeDetection, ExtractionConfidence
)


class ProcessingStatusEnum(str, Enum):
    """Processing status enumeration for API responses."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DocumentTypeEnum(str, Enum):
    """Document type enumeration for API responses."""
    COMMERCIAL_INVOICE = "commercial_invoice"
    PACKING_LIST = "packing_list"
    BILL_OF_LADING = "bill_of_lading"
    CERTIFICATE_OF_ORIGIN = "certificate_of_origin"
    AIRWAY_BILL = "airway_bill"
    CUSTOMS_DECLARATION = "customs_declaration"
    INSURANCE_CERTIFICATE = "insurance_certificate"
    PURCHASE_ORDER = "purchase_order"
    PROFORMA_INVOICE = "proforma_invoice"
    UNKNOWN = "unknown"


class ExtractionConfidenceEnum(str, Enum):
    """Extraction confidence enumeration for API responses."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


# Request Schemas

class DocumentProcessingRequest(BaseModel):
    """Request schema for initiating document processing."""
    
    document_id: int = Field(..., description="ID of the document to process")
    force_reprocess: bool = Field(
        default=False, 
        description="Whether to reprocess if already processed"
    )
    processing_options: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional processing options"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_id": 123,
                "force_reprocess": False,
                "processing_options": {
                    "extract_tables": True,
                    "high_accuracy_mode": True
                }
            }
        }
    )


class BatchProcessingRequest(BaseModel):
    """Request schema for batch document processing."""
    
    document_ids: List[int] = Field(
        ..., 
        min_length=1, 
        max_length=50,
        description="List of document IDs to process (max 50)"
    )
    force_reprocess: bool = Field(
        default=False,
        description="Whether to reprocess documents that are already processed"
    )
    processing_priority: Optional[str] = Field(
        default="normal",
        description="Processing priority: low, normal, high"
    )
    
    @validator('processing_priority')
    def validate_priority(cls, v):
        if v not in ['low', 'normal', 'high']:
            raise ValueError('Priority must be low, normal, or high')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "document_ids": [123, 124, 125],
                "force_reprocess": False,
                "processing_priority": "normal"
            }
        }
    )


class FieldCorrectionRequest(BaseModel):
    """Request schema for correcting extracted field values."""
    
    field_id: int = Field(..., description="ID of the extracted field to correct")
    corrected_value: str = Field(..., description="Corrected field value")
    correction_notes: Optional[str] = Field(
        default=None,
        description="Notes about the correction"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "field_id": 456,
                "corrected_value": "INV-2024-001-CORRECTED",
                "correction_notes": "Fixed typo in invoice number"
            }
        }
    )


# Response Schemas

class BoundingBoxData(BaseModel):
    """Bounding box coordinates for extracted fields."""
    
    x: float = Field(..., description="X coordinate")
    y: float = Field(..., description="Y coordinate")
    width: float = Field(..., description="Width")
    height: float = Field(..., description="Height")
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "x": 100.5,
                "y": 200.3,
                "width": 150.0,
                "height": 25.0
            }
        }
    )


class ExtractedFieldData(BaseModel):
    """Schema for extracted field data."""
    
    id: Optional[int] = Field(default=None, description="Field ID (if saved)")
    field_name: str = Field(..., description="Name of the extracted field")
    field_type: str = Field(..., description="Type of the field (text, number, date, etc.)")
    field_value: Optional[str] = Field(default=None, description="Original extracted value")
    field_value_normalized: Optional[str] = Field(
        default=None, 
        description="Normalized/cleaned value"
    )
    confidence_score: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence score (0.0 to 1.0)"
    )
    is_validated: bool = Field(default=False, description="Whether field has been validated")
    validation_method: Optional[str] = Field(
        default=None,
        description="Method used for validation"
    )
    bounding_box: Optional[BoundingBoxData] = Field(
        default=None,
        description="Bounding box coordinates"
    )
    page_number: Optional[int] = Field(default=None, description="Page number where field was found")
    corrected_value: Optional[str] = Field(
        default=None,
        description="Manually corrected value"
    )
    corrected_by: Optional[str] = Field(default=None, description="User who made the correction")
    corrected_at: Optional[datetime] = Field(
        default=None,
        description="When the correction was made"
    )
    correction_notes: Optional[str] = Field(
        default=None,
        description="Notes about the correction"
    )
    
    @property
    def final_value(self) -> Optional[str]:
        """Get the final value (corrected if available, otherwise original)."""
        return self.corrected_value or self.field_value
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 789,
                "field_name": "invoice_number",
                "field_type": "text",
                "field_value": "INV-2024-001",
                "field_value_normalized": "INV-2024-001",
                "confidence_score": 0.95,
                "is_validated": True,
                "validation_method": "format_check",
                "bounding_box": {
                    "x": 100.5,
                    "y": 200.3,
                    "width": 150.0,
                    "height": 25.0
                },
                "page_number": 1,
                "corrected_value": None,
                "corrected_by": None,
                "corrected_at": None,
                "correction_notes": None
            }
        }
    )


class HSCodeSuggestion(BaseModel):
    """Schema for HS code suggestions."""
    
    code: str = Field(..., description="HS code")
    description: str = Field(..., description="Description of the HS code")
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for this suggestion"
    )
    reasoning: Optional[str] = Field(
        default=None,
        description="Reasoning for this HS code suggestion"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "code": "8471.30.01",
                "description": "Portable digital automatic data processing machines",
                "confidence": 0.85,
                "reasoning": "Based on product description mentioning laptops"
            }
        }
    )


class ComplianceFlag(BaseModel):
    """Schema for compliance flags."""
    
    flag: str = Field(..., description="Flag identifier")
    severity: str = Field(..., description="Severity level (low, medium, high)")
    description: str = Field(..., description="Description of the compliance issue")
    recommendation: Optional[str] = Field(
        default=None,
        description="Recommended action to address the flag"
    )
    
    @validator('severity')
    def validate_severity(cls, v):
        if v not in ['low', 'medium', 'high']:
            raise ValueError('Severity must be low, medium, or high')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "flag": "missing_country_of_origin",
                "severity": "medium",
                "description": "Country of origin not clearly specified",
                "recommendation": "Verify country of origin with supplier"
            }
        }
    )


class RiskAssessment(BaseModel):
    """Schema for risk assessment results."""
    
    overall_risk: str = Field(..., description="Overall risk level (low, medium, high)")
    risk_factors: List[str] = Field(default=[], description="List of identified risk factors")
    risk_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Numerical risk score (0.0 to 1.0)"
    )
    mitigation_suggestions: Optional[List[str]] = Field(
        default=None,
        description="Suggestions for risk mitigation"
    )
    
    @validator('overall_risk')
    def validate_overall_risk(cls, v):
        if v not in ['low', 'medium', 'high', 'unknown']:
            raise ValueError('Overall risk must be low, medium, high, or unknown')
        return v
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "overall_risk": "low",
                "risk_factors": ["incomplete_documentation"],
                "risk_score": 0.3,
                "mitigation_suggestions": [
                    "Verify all required documents are present",
                    "Double-check HS code classifications"
                ]
            }
        }
    )


class AIAnalysisResult(BaseModel):
    """Schema for comprehensive AI analysis results."""
    
    suggested_hs_codes: List[HSCodeSuggestion] = Field(
        default=[],
        description="Suggested HS codes for goods in the document"
    )
    compliance_flags: List[ComplianceFlag] = Field(
        default=[],
        description="Identified compliance issues or flags"
    )
    risk_assessment: Optional[RiskAssessment] = Field(
        default=None,
        description="Risk assessment results"
    )
    key_insights: List[str] = Field(
        default=[],
        description="Key insights from document analysis"
    )
    recommendations: List[str] = Field(
        default=[],
        description="Recommendations for processing"
    )
    processing_notes: Optional[str] = Field(
        default=None,
        description="Additional processing notes"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "suggested_hs_codes": [
                    {
                        "code": "8471.30.01",
                        "description": "Portable digital automatic data processing machines",
                        "confidence": 0.85,
                        "reasoning": "Based on product description"
                    }
                ],
                "compliance_flags": [
                    {
                        "flag": "missing_country_of_origin",
                        "severity": "medium",
                        "description": "Country of origin not clearly specified"
                    }
                ],
                "risk_assessment": {
                    "overall_risk": "low",
                    "risk_factors": ["incomplete_documentation"],
                    "risk_score": 0.3
                },
                "key_insights": [
                    "Document appears complete and well-formatted",
                    "All required commercial invoice fields present"
                ],
                "recommendations": [
                    "Verify country of origin with supplier",
                    "Confirm HS code classification"
                ]
            }
        }
    )


class DocumentProcessingResponse(BaseModel):
    """Response schema for document processing results."""
    
    id: int = Field(..., description="Processing record ID")
    document_id: int = Field(..., description="Document ID")
    processing_status: ProcessingStatusEnum = Field(..., description="Current processing status")
    processing_started_at: Optional[datetime] = Field(
        default=None,
        description="When processing started"
    )
    processing_completed_at: Optional[datetime] = Field(
        default=None,
        description="When processing completed"
    )
    processing_duration_seconds: Optional[float] = Field(
        default=None,
        description="Processing duration in seconds"
    )
    
    # AI model information
    ai_model_used: str = Field(..., description="AI model used for processing")
    ai_model_version: Optional[str] = Field(default=None, description="AI model version")
    
    # Document type detection
    detected_document_type: Optional[DocumentTypeEnum] = Field(
        default=None,
        description="AI-detected document type"
    )
    document_type_confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Confidence in document type detection"
    )
    
    # OCR results
    ocr_text: Optional[str] = Field(default=None, description="Extracted text from OCR")
    ocr_confidence: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="OCR confidence score"
    )
    
    # Extracted data
    extracted_fields: List[ExtractedFieldData] = Field(
        default=[],
        description="Extracted structured fields"
    )
    extraction_confidence: Optional[ExtractionConfidenceEnum] = Field(
        default=None,
        description="Overall extraction confidence level"
    )
    
    # AI analysis
    ai_analysis: Optional[AIAnalysisResult] = Field(
        default=None,
        description="Comprehensive AI analysis results"
    )
    
    # Processing metadata
    requires_manual_review: bool = Field(
        default=False,
        description="Whether manual review is required"
    )
    reviewed_by: Optional[str] = Field(default=None, description="User who reviewed the results")
    reviewed_at: Optional[datetime] = Field(default=None, description="When review was completed")
    
    # Error handling
    error_message: Optional[str] = Field(default=None, description="Error message if processing failed")
    error_details: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Detailed error information"
    )
    
    # Timestamps
    created_at: datetime = Field(..., description="When processing record was created")
    updated_at: datetime = Field(..., description="When processing record was last updated")
    
    @property
    def is_completed(self) -> bool:
        """Check if processing is completed."""
        return self.processing_status == ProcessingStatusEnum.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if processing failed."""
        return self.processing_status == ProcessingStatusEnum.FAILED
    
    @property
    def processing_duration_minutes(self) -> Optional[float]:
        """Get processing duration in minutes."""
        if self.processing_duration_seconds:
            return self.processing_duration_seconds / 60.0
        return None
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 123,
                "document_id": 456,
                "processing_status": "completed",
                "processing_started_at": "2024-01-15T10:30:00Z",
                "processing_completed_at": "2024-01-15T10:32:30Z",
                "processing_duration_seconds": 150.5,
                "ai_model_used": "claude-3.5-sonnet",
                "ai_model_version": "20241022",
                "detected_document_type": "commercial_invoice",
                "document_type_confidence": 0.95,
                "ocr_confidence": 0.87,
                "extraction_confidence": "high",
                "requires_manual_review": False,
                "created_at": "2024-01-15T10:30:00Z",
                "updated_at": "2024-01-15T10:32:30Z"
            }
        }
    )


class BatchProcessingResponse(BaseModel):
    """Response schema for batch processing requests."""
    
    batch_id: str = Field(..., description="Unique batch processing ID")
    total_documents: int = Field(..., description="Total number of documents in batch")
    processing_status: str = Field(..., description="Overall batch processing status")
    documents: List[DocumentProcessingResponse] = Field(
        default=[],
        description="Individual document processing results"
    )
    started_at: datetime = Field(..., description="When batch processing started")
    estimated_completion: Optional[datetime] = Field(
        default=None,
        description="Estimated completion time"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "batch_id": "batch_2024_001",
                "total_documents": 3,
                "processing_status": "processing",
                "documents": [],
                "started_at": "2024-01-15T10:30:00Z",
                "estimated_completion": "2024-01-15T10:35:00Z"
            }
        }
    )


class ProcessingStatsResponse(BaseModel):
    """Response schema for processing statistics."""
    
    total_processed: int = Field(..., description="Total documents processed")
    successful_processing: int = Field(..., description="Successfully processed documents")
    failed_processing: int = Field(..., description="Failed processing attempts")
    pending_processing: int = Field(..., description="Documents pending processing")
    average_processing_time: Optional[float] = Field(
        default=None,
        description="Average processing time in seconds"
    )
    success_rate: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Success rate (0.0 to 1.0)"
    )
    document_type_breakdown: Dict[str, int] = Field(
        default={},
        description="Breakdown by document type"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "total_processed": 150,
                "successful_processing": 142,
                "failed_processing": 8,
                "pending_processing": 5,
                "average_processing_time": 45.2,
                "success_rate": 0.947,
                "document_type_breakdown": {
                    "commercial_invoice": 85,
                    "packing_list": 35,
                    "bill_of_lading": 22,
                    "certificate_of_origin": 8
                }
            }
        }
    )


class FieldCorrectionResponse(BaseModel):
    """Response schema for field correction operations."""
    
    field_id: int = Field(..., description="ID of the corrected field")
    original_value: Optional[str] = Field(default=None, description="Original extracted value")
    corrected_value: str = Field(..., description="Corrected value")
    corrected_by: str = Field(..., description="User who made the correction")
    corrected_at: datetime = Field(..., description="When the correction was made")
    correction_notes: Optional[str] = Field(
        default=None,
        description="Notes about the correction"
    )
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "field_id": 789,
                "original_value": "INV-2024-001",
                "corrected_value": "INV-2024-001-CORRECTED",
                "corrected_by": "john.doe",
                "corrected_at": "2024-01-15T11:00:00Z",
                "correction_notes": "Fixed typo in invoice number"
            }
        }
    )