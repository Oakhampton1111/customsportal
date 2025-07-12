"""
AI Document Processing API routes for the Customs Broker Portal.

This module provides REST API endpoints for AI-powered document processing,
including document analysis, field extraction, and processing management.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query, Path
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from database import get_async_session as get_db
from models.documents import Document
from models.ai_document_processing import (
    AIDocumentProcessing, ExtractedField, ProcessingTemplate,
    ProcessingStatus, DocumentTypeDetection, ExtractionConfidence
)
from schemas.ai_document_processing import (
    DocumentProcessingRequest, DocumentProcessingResponse,
    BatchProcessingRequest, BatchProcessingResponse,
    FieldCorrectionRequest, FieldCorrectionResponse,
    ProcessingStatsResponse, ExtractedFieldData,
    AIAnalysisResult, HSCodeSuggestion, ComplianceFlag, RiskAssessment
)
from ai.document_processor import get_document_processor, DocumentProcessingError


logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/ai/documents", tags=["AI Document Processing"])

# In-memory storage for batch processing (in production, use Redis or database)
batch_processing_status: Dict[str, Dict[str, Any]] = {}


def convert_processing_to_response(
    processing: AIDocumentProcessing,
    include_ocr_text: bool = False
) -> DocumentProcessingResponse:
    """
    Convert AIDocumentProcessing model to response schema.
    
    Args:
        processing: AIDocumentProcessing model instance
        include_ocr_text: Whether to include OCR text in response
        
    Returns:
        DocumentProcessingResponse schema
    """
    # Convert extracted fields
    extracted_fields = []
    for field in processing.extracted_fields:
        field_data = ExtractedFieldData(
            id=field.id,
            field_name=field.field_name,
            field_type=field.field_type,
            field_value=field.field_value,
            field_value_normalized=field.field_value_normalized,
            confidence_score=float(field.confidence_score) if field.confidence_score else None,
            is_validated=field.is_validated,
            validation_method=field.validation_method,
            bounding_box=field.bounding_box,
            page_number=field.page_number,
            corrected_value=field.corrected_value,
            corrected_by=field.corrected_by,
            corrected_at=field.corrected_at,
            correction_notes=field.correction_notes
        )
        extracted_fields.append(field_data)
    
    # Convert AI analysis
    ai_analysis = None
    if processing.ai_analysis:
        analysis_data = processing.ai_analysis
        
        # Convert HS code suggestions
        hs_codes = []
        for hs_data in analysis_data.get("suggested_hs_codes", []):
            hs_codes.append(HSCodeSuggestion(
                code=hs_data.get("code", ""),
                description=hs_data.get("description", ""),
                confidence=hs_data.get("confidence", 0.0),
                reasoning=hs_data.get("reasoning")
            ))
        
        # Convert compliance flags
        compliance_flags = []
        for flag_data in analysis_data.get("compliance_flags", []):
            compliance_flags.append(ComplianceFlag(
                flag=flag_data.get("flag", ""),
                severity=flag_data.get("severity", "medium"),
                description=flag_data.get("description", ""),
                recommendation=flag_data.get("recommendation")
            ))
        
        # Convert risk assessment
        risk_assessment = None
        if "risk_assessment" in analysis_data:
            risk_data = analysis_data["risk_assessment"]
            risk_assessment = RiskAssessment(
                overall_risk=risk_data.get("overall_risk", "unknown"),
                risk_factors=risk_data.get("risk_factors", []),
                risk_score=risk_data.get("risk_score", 0.0),
                mitigation_suggestions=risk_data.get("mitigation_suggestions")
            )
        
        ai_analysis = AIAnalysisResult(
            suggested_hs_codes=hs_codes,
            compliance_flags=compliance_flags,
            risk_assessment=risk_assessment,
            key_insights=analysis_data.get("key_insights", []),
            recommendations=analysis_data.get("recommendations", []),
            processing_notes=processing.processing_notes
        )
    
    return DocumentProcessingResponse(
        id=processing.id,
        document_id=processing.document_id,
        processing_status=processing.processing_status.value,
        processing_started_at=processing.processing_started_at,
        processing_completed_at=processing.processing_completed_at,
        processing_duration_seconds=float(processing.processing_duration_seconds) if processing.processing_duration_seconds else None,
        ai_model_used=processing.ai_model_used,
        ai_model_version=processing.ai_model_version,
        detected_document_type=processing.detected_document_type.value if processing.detected_document_type else None,
        document_type_confidence=float(processing.document_type_confidence) if processing.document_type_confidence else None,
        ocr_text=processing.ocr_text if include_ocr_text else None,
        ocr_confidence=float(processing.ocr_confidence) if processing.ocr_confidence else None,
        extracted_fields=extracted_fields,
        extraction_confidence=processing.extraction_confidence.value if processing.extraction_confidence else None,
        ai_analysis=ai_analysis,
        requires_manual_review=processing.requires_manual_review,
        reviewed_by=processing.reviewed_by,
        reviewed_at=processing.reviewed_at,
        error_message=processing.error_message,
        error_details=processing.error_details,
        created_at=processing.created_at,
        updated_at=processing.updated_at
    )


async def background_process_document(document_id: int, db: AsyncSession):
    """Background task for processing documents."""
    try:
        processor = get_document_processor()
        await processor.process_document(db, document_id)
        logger.info(f"Background processing completed for document {document_id}")
    except Exception as e:
        logger.error(f"Background processing failed for document {document_id}: {e}")


async def background_batch_process(batch_id: str, document_ids: List[int], db: AsyncSession):
    """Background task for batch processing documents."""
    try:
        batch_processing_status[batch_id]["status"] = "processing"
        processor = get_document_processor()
        
        completed = 0
        failed = 0
        
        for doc_id in document_ids:
            try:
                await processor.process_document(db, doc_id)
                completed += 1
                batch_processing_status[batch_id]["completed"] = completed
            except Exception as e:
                failed += 1
                batch_processing_status[batch_id]["failed"] = failed
                logger.error(f"Failed to process document {doc_id} in batch {batch_id}: {e}")
        
        batch_processing_status[batch_id]["status"] = "completed"
        batch_processing_status[batch_id]["completed_at"] = datetime.utcnow()
        
        logger.info(f"Batch processing {batch_id} completed: {completed} successful, {failed} failed")
        
    except Exception as e:
        batch_processing_status[batch_id]["status"] = "failed"
        batch_processing_status[batch_id]["error"] = str(e)
        logger.error(f"Batch processing {batch_id} failed: {e}")


@router.post("/process", response_model=DocumentProcessingResponse)
async def process_document(
    request: DocumentProcessingRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Process a document with AI analysis.
    
    This endpoint initiates AI-powered processing of a document, including:
    - OCR text extraction
    - Document type detection
    - Structured field extraction
    - Compliance analysis
    - HS code suggestions
    """
    try:
        # Check if document exists
        result = await db.execute(
            select(Document).where(Document.id == request.document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document {request.document_id} not found"
            )
        
        # Check if already processed
        existing_result = await db.execute(
            select(AIDocumentProcessing)
            .where(AIDocumentProcessing.document_id == request.document_id)
            .order_by(AIDocumentProcessing.created_at.desc())
        )
        existing_processing = existing_result.scalar_one_or_none()
        
        if existing_processing and existing_processing.is_completed and not request.force_reprocess:
            # Return existing results
            await db.refresh(existing_processing, ["extracted_fields"])
            return convert_processing_to_response(existing_processing)
        
        # Start processing in background
        background_tasks.add_task(background_process_document, request.document_id, db)
        
        # Create or update processing record
        if existing_processing and request.force_reprocess:
            processing = existing_processing
            processing.processing_status = ProcessingStatus.PENDING
            processing.error_message = None
            processing.error_details = None
        else:
            processing = AIDocumentProcessing(
                document_id=request.document_id,
                processing_status=ProcessingStatus.PENDING
            )
            db.add(processing)
        
        await db.commit()
        await db.refresh(processing)
        
        return convert_processing_to_response(processing)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing document {request.document_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Processing failed: {str(e)}"
        )


@router.post("/batch-process", response_model=BatchProcessingResponse)
async def batch_process_documents(
    request: BatchProcessingRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """
    Process multiple documents in batch.
    
    This endpoint allows processing multiple documents simultaneously,
    useful for bulk document processing operations.
    """
    try:
        # Validate documents exist
        result = await db.execute(
            select(Document.id).where(Document.id.in_(request.document_ids))
        )
        existing_ids = [row[0] for row in result.fetchall()]
        
        missing_ids = set(request.document_ids) - set(existing_ids)
        if missing_ids:
            raise HTTPException(
                status_code=404,
                detail=f"Documents not found: {list(missing_ids)}"
            )
        
        # Create batch processing record
        batch_id = f"batch_{uuid4().hex[:8]}"
        batch_processing_status[batch_id] = {
            "batch_id": batch_id,
            "total_documents": len(request.document_ids),
            "status": "pending",
            "completed": 0,
            "failed": 0,
            "started_at": datetime.utcnow(),
            "document_ids": request.document_ids
        }
        
        # Start batch processing in background
        background_tasks.add_task(
            background_batch_process,
            batch_id,
            request.document_ids,
            db
        )
        
        return BatchProcessingResponse(
            batch_id=batch_id,
            total_documents=len(request.document_ids),
            processing_status="pending",
            documents=[],
            started_at=datetime.utcnow()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting batch processing: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Batch processing failed: {str(e)}"
        )


@router.get("/batch-status/{batch_id}", response_model=BatchProcessingResponse)
async def get_batch_status(
    batch_id: str = Path(..., description="Batch processing ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the status of a batch processing operation.
    """
    if batch_id not in batch_processing_status:
        raise HTTPException(
            status_code=404,
            detail=f"Batch {batch_id} not found"
        )
    
    batch_info = batch_processing_status[batch_id]
    
    # Get individual document results if completed
    documents = []
    if batch_info["status"] in ["completed", "failed"]:
        for doc_id in batch_info["document_ids"]:
            result = await db.execute(
                select(AIDocumentProcessing)
                .options(selectinload(AIDocumentProcessing.extracted_fields))
                .where(AIDocumentProcessing.document_id == doc_id)
                .order_by(AIDocumentProcessing.created_at.desc())
            )
            processing = result.scalar_one_or_none()
            if processing:
                documents.append(convert_processing_to_response(processing))
    
    return BatchProcessingResponse(
        batch_id=batch_id,
        total_documents=batch_info["total_documents"],
        processing_status=batch_info["status"],
        documents=documents,
        started_at=batch_info["started_at"],
        estimated_completion=batch_info.get("completed_at")
    )


@router.get("/status/{document_id}", response_model=DocumentProcessingResponse)
async def get_processing_status(
    document_id: int = Path(..., description="Document ID"),
    include_ocr_text: bool = Query(False, description="Include OCR text in response"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get the processing status and results for a document.
    """
    try:
        result = await db.execute(
            select(AIDocumentProcessing)
            .options(selectinload(AIDocumentProcessing.extracted_fields))
            .where(AIDocumentProcessing.document_id == document_id)
            .order_by(AIDocumentProcessing.created_at.desc())
        )
        processing = result.scalar_one_or_none()
        
        if not processing:
            raise HTTPException(
                status_code=404,
                detail=f"No processing record found for document {document_id}"
            )
        
        return convert_processing_to_response(processing, include_ocr_text)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processing status for document {document_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get processing status: {str(e)}"
        )


@router.post("/reprocess/{document_id}", response_model=DocumentProcessingResponse)
async def reprocess_document(
    background_tasks: BackgroundTasks,
    document_id: int = Path(..., description="Document ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Reprocess a document (force reprocessing).
    """
    try:
        # Check if document exists
        result = await db.execute(
            select(Document).where(Document.id == document_id)
        )
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found"
            )
        
        # Start reprocessing in background
        background_tasks.add_task(background_process_document, document_id, db)
        
        # Update existing processing record or create new one
        result = await db.execute(
            select(AIDocumentProcessing)
            .where(AIDocumentProcessing.document_id == document_id)
            .order_by(AIDocumentProcessing.created_at.desc())
        )
        processing = result.scalar_one_or_none()
        
        if processing:
            processing.processing_status = ProcessingStatus.PENDING
            processing.error_message = None
            processing.error_details = None
        else:
            processing = AIDocumentProcessing(
                document_id=document_id,
                processing_status=ProcessingStatus.PENDING
            )
            db.add(processing)
        
        await db.commit()
        await db.refresh(processing)
        
        return convert_processing_to_response(processing)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reprocessing document {document_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Reprocessing failed: {str(e)}"
        )


@router.post("/fields/correct", response_model=FieldCorrectionResponse)
async def correct_extracted_field(
    request: FieldCorrectionRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Correct an extracted field value.
    
    This endpoint allows manual correction of AI-extracted field values,
    which helps improve the accuracy of future extractions.
    """
    try:
        # Get the extracted field
        result = await db.execute(
            select(ExtractedField).where(ExtractedField.id == request.field_id)
        )
        field = result.scalar_one_or_none()
        
        if not field:
            raise HTTPException(
                status_code=404,
                detail=f"Extracted field {request.field_id} not found"
            )
        
        # Store original value and apply correction
        original_value = field.field_value
        field.corrected_value = request.corrected_value
        field.corrected_by = "api_user"  # In production, get from authentication
        field.corrected_at = datetime.utcnow()
        field.correction_notes = request.correction_notes
        
        await db.commit()
        await db.refresh(field)
        
        return FieldCorrectionResponse(
            field_id=field.id,
            original_value=original_value,
            corrected_value=field.corrected_value,
            corrected_by=field.corrected_by,
            corrected_at=field.corrected_at,
            correction_notes=field.correction_notes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error correcting field {request.field_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Field correction failed: {str(e)}"
        )


@router.get("/stats", response_model=ProcessingStatsResponse)
async def get_processing_statistics(
    days: int = Query(30, description="Number of days to include in statistics"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get processing statistics and metrics.
    
    This endpoint provides insights into document processing performance,
    success rates, and document type distribution.
    """
    try:
        # Calculate date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Get basic counts
        total_result = await db.execute(
            select(func.count(AIDocumentProcessing.id))
            .where(AIDocumentProcessing.created_at >= cutoff_date)
        )
        total_processed = total_result.scalar() or 0
        
        successful_result = await db.execute(
            select(func.count(AIDocumentProcessing.id))
            .where(
                and_(
                    AIDocumentProcessing.created_at >= cutoff_date,
                    AIDocumentProcessing.processing_status == ProcessingStatus.COMPLETED
                )
            )
        )
        successful_processing = successful_result.scalar() or 0
        
        failed_result = await db.execute(
            select(func.count(AIDocumentProcessing.id))
            .where(
                and_(
                    AIDocumentProcessing.created_at >= cutoff_date,
                    AIDocumentProcessing.processing_status == ProcessingStatus.FAILED
                )
            )
        )
        failed_processing = failed_result.scalar() or 0
        
        pending_result = await db.execute(
            select(func.count(AIDocumentProcessing.id))
            .where(
                and_(
                    AIDocumentProcessing.created_at >= cutoff_date,
                    AIDocumentProcessing.processing_status.in_([
                        ProcessingStatus.PENDING,
                        ProcessingStatus.PROCESSING
                    ])
                )
            )
        )
        pending_processing = pending_result.scalar() or 0
        
        # Calculate average processing time
        avg_time_result = await db.execute(
            select(func.avg(AIDocumentProcessing.processing_duration_seconds))
            .where(
                and_(
                    AIDocumentProcessing.created_at >= cutoff_date,
                    AIDocumentProcessing.processing_status == ProcessingStatus.COMPLETED,
                    AIDocumentProcessing.processing_duration_seconds.isnot(None)
                )
            )
        )
        avg_processing_time = avg_time_result.scalar()
        
        # Calculate success rate
        success_rate = None
        if total_processed > 0:
            success_rate = successful_processing / total_processed
        
        # Get document type breakdown
        type_breakdown_result = await db.execute(
            select(
                AIDocumentProcessing.detected_document_type,
                func.count(AIDocumentProcessing.id)
            )
            .where(
                and_(
                    AIDocumentProcessing.created_at >= cutoff_date,
                    AIDocumentProcessing.detected_document_type.isnot(None)
                )
            )
            .group_by(AIDocumentProcessing.detected_document_type)
        )
        
        document_type_breakdown = {}
        for doc_type, count in type_breakdown_result.fetchall():
            if doc_type:
                document_type_breakdown[doc_type.value] = count
        
        return ProcessingStatsResponse(
            total_processed=total_processed,
            successful_processing=successful_processing,
            failed_processing=failed_processing,
            pending_processing=pending_processing,
            average_processing_time=float(avg_processing_time) if avg_processing_time else None,
            success_rate=success_rate,
            document_type_breakdown=document_type_breakdown
        )
        
    except Exception as e:
        logger.error(f"Error getting processing statistics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get statistics: {str(e)}"
        )


@router.get("/documents/pending", response_model=List[DocumentProcessingResponse])
async def get_pending_documents(
    limit: int = Query(50, description="Maximum number of documents to return"),
    offset: int = Query(0, description="Number of documents to skip"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get documents that require manual review.
    """
    try:
        result = await db.execute(
            select(AIDocumentProcessing)
            .options(selectinload(AIDocumentProcessing.extracted_fields))
            .where(
                or_(
                    AIDocumentProcessing.requires_manual_review == True,
                    AIDocumentProcessing.processing_status == ProcessingStatus.FAILED
                )
            )
            .order_by(AIDocumentProcessing.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        
        processing_records = result.scalars().all()
        
        return [
            convert_processing_to_response(processing)
            for processing in processing_records
        ]
        
    except Exception as e:
        logger.error(f"Error getting pending documents: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get pending documents: {str(e)}"
        )


@router.post("/documents/{document_id}/mark-reviewed")
async def mark_document_reviewed(
    document_id: int = Path(..., description="Document ID"),
    reviewer: str = Query(..., description="Reviewer username"),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark a document as reviewed.
    """
    try:
        result = await db.execute(
            select(AIDocumentProcessing)
            .where(AIDocumentProcessing.document_id == document_id)
            .order_by(AIDocumentProcessing.created_at.desc())
        )
        processing = result.scalar_one_or_none()
        
        if not processing:
            raise HTTPException(
                status_code=404,
                detail=f"No processing record found for document {document_id}"
            )
        
        processing.reviewed_by = reviewer
        processing.reviewed_at = datetime.utcnow()
        processing.requires_manual_review = False
        
        await db.commit()
        
        return {"message": "Document marked as reviewed", "reviewed_by": reviewer}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error marking document {document_id} as reviewed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to mark document as reviewed: {str(e)}"
        )


@router.get("/processing/{processing_id}")
async def get_document_processing_details(
    processing_id: int = Path(..., description="Processing ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get detailed processing information for broker review.
    """
    try:
        result = await db.execute(
            select(AIDocumentProcessing)
            .options(selectinload(AIDocumentProcessing.extracted_fields))
            .where(AIDocumentProcessing.id == processing_id)
        )
        processing = result.scalar_one_or_none()
        
        if not processing:
            raise HTTPException(
                status_code=404,
                detail=f"Processing record {processing_id} not found"
            )
        
        # Get document info
        doc_result = await db.execute(
            select(Document).where(Document.id == processing.document_id)
        )
        document = doc_result.scalar_one_or_none()
        
        # Format OCR results
        ocr_results = []
        if processing.ocr_text:
            ocr_results.append({
                "page_number": 1,
                "text_content": processing.ocr_text,
                "confidence_score": float(processing.ocr_confidence) if processing.ocr_confidence else 0.0,
                "bounding_boxes": []  # Would need to be extracted from OCR engine
            })
        
        # Format extracted fields
        extracted_fields = {}
        for field in processing.extracted_fields:
            extracted_fields[field.field_name] = {
                "value": field.field_value,
                "confidence": float(field.confidence_score) if field.confidence_score else 0.0,
                "normalized_value": field.field_value_normalized,
                "is_validated": field.is_validated,
                "corrected_value": field.corrected_value
            }
        
        return {
            "id": processing.id,
            "document_id": processing.document_id,
            "document_name": document.filename if document else "Unknown",
            "processing_status": processing.processing_status.value,
            "detected_document_type": processing.detected_document_type.value if processing.detected_document_type else "unknown",
            "extraction_confidence": processing.extraction_confidence.value if processing.extraction_confidence else "unknown",
            "extracted_fields": extracted_fields,
            "ocr_results": ocr_results,
            "validation_errors": [],  # Would be populated from validation logic
            "requires_manual_review": processing.requires_manual_review,
            "created_at": processing.created_at.isoformat(),
            "updated_at": processing.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting processing details {processing_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get processing details: {str(e)}"
        )


@router.put("/processing/{processing_id}/fields")
async def update_extracted_fields(
    processing_id: int = Path(..., description="Processing ID"),
    db: AsyncSession = Depends(get_db),
    request: Dict[str, Any] = None
):
    """
    Update extracted fields for a processing record.
    """
    try:
        result = await db.execute(
            select(AIDocumentProcessing)
            .where(AIDocumentProcessing.id == processing_id)
        )
        processing = result.scalar_one_or_none()
        
        if not processing:
            raise HTTPException(
                status_code=404,
                detail=f"Processing record {processing_id} not found"
            )
        
        extracted_fields = request.get("extracted_fields", {}) if request else {}
        
        # Update existing fields or create new ones
        for field_name, field_data in extracted_fields.items():
            # Find existing field
            field_result = await db.execute(
                select(ExtractedField)
                .where(
                    and_(
                        ExtractedField.processing_id == processing_id,
                        ExtractedField.field_name == field_name
                    )
                )
            )
            existing_field = field_result.scalar_one_or_none()
            
            if existing_field:
                # Update existing field
                existing_field.field_value = field_data.get("value", existing_field.field_value)
                existing_field.field_value_normalized = field_data.get("normalized_value")
                existing_field.is_validated = True
                existing_field.validation_method = "manual_review"
                existing_field.corrected_value = field_data.get("corrected_value")
                existing_field.corrected_by = "broker_review"
                existing_field.corrected_at = datetime.utcnow()
            else:
                # Create new field
                new_field = ExtractedField(
                    processing_id=processing_id,
                    field_name=field_name,
                    field_type="text",
                    field_value=field_data.get("value", ""),
                    field_value_normalized=field_data.get("normalized_value"),
                    confidence_score=field_data.get("confidence", 1.0),
                    is_validated=True,
                    validation_method="manual_review",
                    corrected_value=field_data.get("corrected_value"),
                    corrected_by="broker_review",
                    corrected_at=datetime.utcnow()
                )
                db.add(new_field)
        
        await db.commit()
        
        return {"message": "Fields updated successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating fields for processing {processing_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update fields: {str(e)}"
        )


@router.post("/processing/{processing_id}/approve")
async def approve_processing(
    processing_id: int = Path(..., description="Processing ID"),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a processing record.
    """
    try:
        result = await db.execute(
            select(AIDocumentProcessing)
            .where(AIDocumentProcessing.id == processing_id)
        )
        processing = result.scalar_one_or_none()
        
        if not processing:
            raise HTTPException(
                status_code=404,
                detail=f"Processing record {processing_id} not found"
            )
        
        processing.processing_status = ProcessingStatus.COMPLETED
        processing.requires_manual_review = False
        processing.reviewed_by = "broker_review"
        processing.reviewed_at = datetime.utcnow()
        
        await db.commit()
        
        return {"message": "Processing approved successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving processing {processing_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to approve processing: {str(e)}"
        )


@router.post("/processing/{processing_id}/reject")
async def reject_processing(
    processing_id: int = Path(..., description="Processing ID"),
    db: AsyncSession = Depends(get_db),
    request: Dict[str, str] = None
):
    """
    Reject a processing record.
    """
    try:
        result = await db.execute(
            select(AIDocumentProcessing)
            .where(AIDocumentProcessing.id == processing_id)
        )
        processing = result.scalar_one_or_none()
        
        if not processing:
            raise HTTPException(
                status_code=404,
                detail=f"Processing record {processing_id} not found"
            )
        
        reason = request.get("reason", "Rejected by broker") if request else "Rejected by broker"
        
        processing.processing_status = ProcessingStatus.FAILED
        processing.error_message = f"Rejected: {reason}"
        processing.requires_manual_review = False
        processing.reviewed_by = "broker_review"
        processing.reviewed_at = datetime.utcnow()
        
        await db.commit()
        
        return {"message": "Processing rejected successfully", "reason": reason}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting processing {processing_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reject processing: {str(e)}"
        )


@router.post("/processing/{processing_id}/reprocess")
async def reprocess_processing_record(
    processing_id: int = Path(..., description="Processing ID"),
    db: AsyncSession = Depends(get_db),
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    """
    Reprocess a processing record.
    """
    try:
        result = await db.execute(
            select(AIDocumentProcessing)
            .where(AIDocumentProcessing.id == processing_id)
        )
        processing = result.scalar_one_or_none()
        
        if not processing:
            raise HTTPException(
                status_code=404,
                detail=f"Processing record {processing_id} not found"
            )
        
        # Reset processing status
        processing.processing_status = ProcessingStatus.PENDING
        processing.error_message = None
        processing.error_details = None
        processing.requires_manual_review = False
        processing.reviewed_by = None
        processing.reviewed_at = None
        
        # Start reprocessing in background
        background_tasks.add_task(background_process_document, processing.document_id, db)
        
        await db.commit()
        
        return {"message": "Reprocessing started successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error reprocessing {processing_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to start reprocessing: {str(e)}"
        )


# Customs Entry Generation
@router.post("/customs/generate-entry")
async def generate_customs_entry(
    request: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Generate customs entry from extracted document data.
    """
    try:
        document_id = request.get("document_id")
        extracted_data = request.get("extracted_data", {})
        
        if not document_id:
            raise HTTPException(
                status_code=400,
                detail="document_id is required"
            )
        
        # Mock customs entry generation
        entry_id = f"CBP{datetime.utcnow().strftime('%Y%m%d')}{document_id:06d}"
        
        # Extract items from data
        items = extracted_data.get("items", [])
        if not items:
            # Create mock item from extracted data
            items = [{
                "item_number": "1",
                "hs_code": extracted_data.get("hs_code", "0000.00.00"),
                "description": extracted_data.get("description", "Unknown item"),
                "quantity": float(extracted_data.get("quantity", 1)),
                "unit_value": float(extracted_data.get("unit_value", 100)),
                "total_value": float(extracted_data.get("total_value", 100)),
                "duty_rate": 0.05,
                "duty_amount": 5.0,
                "gst_amount": 10.0,
                "total_charges": 115.0
            }]
        
        # Mock compliance checks
        compliance_checks = [
            {
                "check_type": "documentation",
                "status": "pass",
                "message": "All required documents present"
            },
            {
                "check_type": "valuation",
                "status": "warning",
                "message": "Verify commercial invoice values"
            },
            {
                "check_type": "classification",
                "status": "pass",
                "message": "HS code classification verified"
            }
        ]
        
        return {
            "entry_id": entry_id,
            "declaration_data": {
                "entry_type": "consumption",
                "port_of_entry": "AUSYD",
                "importer": extracted_data.get("importer", "Unknown"),
                "supplier": extracted_data.get("supplier", "Unknown"),
                "country_of_origin": extracted_data.get("country_of_origin", "CN"),
                "total_value": sum(item["total_value"] for item in items)
            },
            "calculated_duties": items,
            "compliance_checks": compliance_checks,
            "estimated_clearance_time": "2-4 business days"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating customs entry: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate customs entry: {str(e)}"
        )


# HS Code Validation
@router.post("/hs-codes/validate")
async def validate_hs_code(
    request: Dict[str, str],
    db: AsyncSession = Depends(get_db)
):
    """
    Validate HS code and suggest alternatives.
    """
    try:
        hs_code = request.get("hs_code", "")
        description = request.get("description", "")
        
        if not hs_code:
            raise HTTPException(
                status_code=400,
                detail="hs_code is required"
            )
        
        # Mock HS code validation
        is_valid = len(hs_code) >= 8 and hs_code.replace(".", "").isdigit()
        
        suggested_codes = [
            {
                "code": hs_code,
                "description": f"Primary classification for {description}",
                "confidence": 0.95
            },
            {
                "code": "8471.30.00",
                "description": "Portable automatic data processing machines",
                "confidence": 0.85
            },
            {
                "code": "8471.41.00",
                "description": "Data processing machines",
                "confidence": 0.75
            }
        ]
        
        duty_rates = {
            "general": 5.0,
            "preferential": {
                "US": 0.0,
                "NZ": 0.0,
                "SG": 2.5
            }
        }
        
        return {
            "is_valid": is_valid,
            "suggested_codes": suggested_codes,
            "duty_rates": duty_rates
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error validating HS code: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate HS code: {str(e)}"
        )


# Duty Calculation
@router.post("/duties/calculate")
async def calculate_duties(
    request: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Calculate duties for items.
    """
    try:
        items = request.get("items", [])
        
        if not items:
            raise HTTPException(
                status_code=400,
                detail="items list is required"
            )
        
        total_customs_value = 0
        total_duty = 0
        total_gst = 0
        item_breakdown = []
        
        for i, item in enumerate(items):
            customs_value = item["quantity"] * item["unit_value"]
            duty_rate = 0.05  # Mock 5% duty rate
            duty_amount = customs_value * duty_rate
            gst_rate = 0.10  # 10% GST
            gst_amount = (customs_value + duty_amount) * gst_rate
            total_item_charges = customs_value + duty_amount + gst_amount
            
            total_customs_value += customs_value
            total_duty += duty_amount
            total_gst += gst_amount
            
            item_breakdown.append({
                "item_number": i + 1,
                "customs_value": customs_value,
                "duty_rate": duty_rate,
                "duty_amount": duty_amount,
                "gst_rate": gst_rate,
                "gst_amount": gst_amount,
                "total_item_charges": total_item_charges,
                "applicable_concessions": []
            })
        
        total_charges = total_customs_value + total_duty + total_gst
        
        return {
            "total_customs_value": total_customs_value,
            "total_duty": total_duty,
            "total_gst": total_gst,
            "total_charges": total_charges,
            "item_breakdown": item_breakdown
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating duties: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to calculate duties: {str(e)}"
        )


# Compliance Checking
@router.post("/compliance/check")
async def check_compliance(
    entry_data: Dict[str, Any],
    db: AsyncSession = Depends(get_db)
):
    """
    Check compliance for customs entry.
    """
    try:
        # Mock compliance checking
        checks = [
            {
                "category": "documentation",
                "requirement": "Commercial Invoice",
                "status": "pass",
                "message": "Commercial invoice provided and valid",
                "severity": "medium"
            },
            {
                "category": "valuation",
                "requirement": "Transaction Value",
                "status": "warning",
                "message": "Verify transaction value is at arm's length",
                "severity": "medium",
                "required_action": "Provide additional valuation documentation"
            },
            {
                "category": "classification",
                "requirement": "HS Code Classification",
                "status": "pass",
                "message": "HS code classification appears correct",
                "severity": "high"
            },
            {
                "category": "permits",
                "requirement": "Import Permits",
                "status": "fail",
                "message": "ACMA permit required for electronic goods",
                "severity": "critical",
                "required_action": "Obtain ACMA permit before clearance",
                "supporting_documents": ["ACMA permit", "Test reports"]
            }
        ]
        
        # Determine overall status
        has_critical = any(check["severity"] == "critical" and check["status"] == "fail" for check in checks)
        has_failures = any(check["status"] == "fail" for check in checks)
        
        if has_critical:
            overall_status = "non_compliant"
        elif has_failures:
            overall_status = "requires_review"
        else:
            overall_status = "compliant"
        
        required_permits = [
            {
                "permit_type": "ACMA Equipment Registration",
                "issuing_authority": "Australian Communications and Media Authority",
                "estimated_processing_time": "5-10 business days",
                "application_url": "https://www.acma.gov.au"
            }
        ]
        
        recommendations = [
            "Verify all documentation is complete and accurate",
            "Consider using preferential duty rates where applicable",
            "Ensure all permits are obtained before goods arrival"
        ]
        
        return {
            "overall_status": overall_status,
            "checks": checks,
            "required_permits": required_permits,
            "recommendations": recommendations
        }
        
    except Exception as e:
        logger.error(f"Error checking compliance: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check compliance: {str(e)}"
        )