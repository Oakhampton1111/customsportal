"""
Document management API routes for the Customs Broker Portal.

This module provides comprehensive document management functionality including:
- File upload and storage
- Document metadata management
- Search and filtering
- Sharing and permissions
- Category management
- Bulk operations
"""

import os
import hashlib
import mimetypes
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import aiofiles
import aiofiles.os
from sqlalchemy import and_, or_, func, desc, asc, select
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import (
    APIRouter, Depends, HTTPException, UploadFile, File, Form, Query,
    BackgroundTasks, Request, status
)
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.security import HTTPBearer

from database import get_async_session
from models.documents import (
    Document, DocumentCategoryDefinition, DocumentCategoryMapping, DocumentShare,
    DocumentType, DocumentCategory, DocumentStatus, ComplianceStatus, SharePermission
)
from schemas.documents import (
    DocumentCreate, DocumentUpdate, DocumentResponse, DocumentSummary,
    DocumentUploadResponse, DocumentUploadError, DocumentSearchParams,
    DocumentSearchResponse, DocumentSearchResult, DocumentCategoryCreate,
    DocumentCategoryResponse, DocumentShareCreate, DocumentShareResponse,
    DocumentStats, DocumentBulkOperation, DocumentBulkOperationResponse,
    DocumentListResponse
)
from schemas.common import PaginationMeta
import structlog

logger = structlog.get_logger(__name__)

# Router setup
router = APIRouter(prefix="/api/documents", tags=["documents"])
security = HTTPBearer()

# Configuration
UPLOAD_DIR = Path("uploads/documents")
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx',
    '.txt', '.csv', '.xml', '.json', '.zip', '.rar', '.7z',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff',
    '.mp4', '.avi', '.mov', '.wmv', '.flv'
}
ALLOWED_MIME_TYPES = {
    'application/pdf', 'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-powerpoint', 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'text/plain', 'text/csv', 'application/xml', 'application/json',
    'application/zip', 'application/x-rar-compressed', 'application/x-7z-compressed',
    'image/jpeg', 'image/png', 'image/gif', 'image/bmp', 'image/tiff',
    'video/mp4', 'video/x-msvideo', 'video/quicktime', 'video/x-ms-wmv', 'video/x-flv'
}

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


# Utility functions
async def validate_file(file: UploadFile) -> Dict[str, Any]:
    """Validate uploaded file."""
    errors = []
    
    # Check file size
    if file.size and file.size > MAX_FILE_SIZE:
        errors.append(f"File size ({file.size} bytes) exceeds maximum allowed size ({MAX_FILE_SIZE} bytes)")
    
    # Check file extension
    if file.filename:
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            errors.append(f"File extension '{file_ext}' is not allowed")
    
    # Check MIME type
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        errors.append(f"MIME type '{file.content_type}' is not allowed")
    
    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "file_ext": Path(file.filename).suffix.lower() if file.filename else "",
        "mime_type": file.content_type or "application/octet-stream"
    }


async def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash of file."""
    hash_sha256 = hashlib.sha256()
    async with aiofiles.open(file_path, 'rb') as f:
        while chunk := await f.read(8192):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


async def generate_unique_filename(original_name: str, upload_dir: Path) -> str:
    """Generate unique filename to avoid conflicts."""
    base_name = Path(original_name).stem
    extension = Path(original_name).suffix
    counter = 1
    
    filename = f"{base_name}{extension}"
    while (upload_dir / filename).exists():
        filename = f"{base_name}_{counter}{extension}"
        counter += 1
    
    return filename


async def save_uploaded_file(file: UploadFile, filename: str) -> Path:
    """Save uploaded file to disk."""
    file_path = UPLOAD_DIR / filename
    
    async with aiofiles.open(file_path, 'wb') as f:
        while chunk := await file.read(8192):
            await f.write(chunk)
    
    return file_path


def get_current_user() -> str:
    """Get current user (placeholder - integrate with your auth system)."""
    return "system_user"  # Replace with actual user from JWT token


# Document CRUD operations
@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    document_type: DocumentType = Form(...),
    category: DocumentCategory = Form(...),
    client_id: Optional[str] = Form(None),
    client_name: Optional[str] = Form(None),
    hs_code: Optional[str] = Form(None),
    shipment_ref: Optional[str] = Form(None),
    tags: Optional[str] = Form(None),  # JSON string
    is_confidential: bool = Form(False),
    compliance_status: ComplianceStatus = Form(ComplianceStatus.NOT_APPLICABLE),
    compliance_notes: Optional[str] = Form(None),
    expiry_date: Optional[datetime] = Form(None)
):
    """Upload a new document."""
    try:
        current_user = get_current_user()
        
        # Validate file
        validation = await validate_file(file)
        if not validation["valid"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"errors": validation["errors"]}
            )
        
        # Generate unique filename
        filename = await generate_unique_filename(file.filename, UPLOAD_DIR)
        
        # Save file
        file_path = await save_uploaded_file(file, filename)
        
        # Calculate file hash
        file_hash = await calculate_file_hash(file_path)
        
        # Parse tags
        tag_list = []
        if tags:
            import json
            try:
                tag_list = json.loads(tags)
            except json.JSONDecodeError:
                tag_list = [tag.strip() for tag in tags.split(',') if tag.strip()]
        
        # Create document record
        document = Document(
            filename=filename,
            original_name=file.filename,
            title=title or file.filename,
            description=description,
            document_type=document_type,
            category=category,
            file_size=file.size or 0,
            mime_type=validation["mime_type"],
            file_hash=file_hash,
            client_id=client_id,
            client_name=client_name,
            hs_code=hs_code,
            shipment_ref=shipment_ref,
            tags=tag_list,
            is_confidential=is_confidential,
            compliance_status=compliance_status,
            compliance_notes=compliance_notes,
            expiry_date=expiry_date,
            uploaded_by=current_user,
            upload_date=datetime.utcnow()
        )
        
        db.add(document)
        await db.commit()
        await db.refresh(document)
        
        logger.info(
            "Document uploaded successfully",
            document_id=document.id,
            filename=filename,
            user=current_user
        )
        
        return DocumentUploadResponse(
            document_id=document.id,
            filename=filename,
            original_name=file.filename,
            file_size=file.size or 0,
            upload_url=f"/api/documents/{document.id}/download"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Document upload failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document upload failed"
        )


# Category management - MUST come before /{document_id} route
@router.get("/categories", response_model=List[DocumentCategoryResponse])
async def list_document_categories(
    db: AsyncSession = Depends(get_async_session),
    include_inactive: bool = Query(False)
):
    """List all document categories."""
    try:
        query = select(DocumentCategoryDefinition)
        
        if not include_inactive:
            query = query.where(DocumentCategoryDefinition.is_active == True)
        
        query = query.order_by(DocumentCategoryDefinition.sort_order, DocumentCategoryDefinition.name)
        
        result = await db.execute(query)
        categories = result.scalars().all()
        
        # Convert to response format manually to avoid relationship loading issues
        response_categories = []
        for cat in categories:
            cat_dict = {
                "id": cat.id,
                "name": cat.name,
                "description": cat.description,
                "color": cat.color,
                "icon": cat.icon,
                "parent_category_id": cat.parent_category_id,
                "sort_order": cat.sort_order,
                "is_active": cat.is_active,
                "created_at": cat.created_at,
                "updated_at": cat.updated_at,
                "document_count": None,  # Can be populated later if needed
                "child_categories": None  # Avoid relationship loading
            }
            response_categories.append(DocumentCategoryResponse(**cat_dict))
        
        return response_categories
        
    except Exception as e:
        logger.error("Failed to list document categories", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document categories"
        )


# Statistics endpoint - MUST come before /{document_id} route
@router.get("/stats", response_model=DocumentStats)
async def get_document_statistics(
    db: AsyncSession = Depends(get_async_session)
):
    """Get document statistics and analytics."""
    try:
        # Total documents and size
        total_docs_result = await db.execute(
            select(func.count(Document.id), func.sum(Document.file_size))
            .where(Document.is_active == True)
        )
        total_docs, total_size = total_docs_result.first()
        total_size = total_size or 0
        
        # Documents by type
        type_stats = await db.execute(
            select(Document.document_type, func.count(Document.id))
            .where(Document.is_active == True)
            .group_by(Document.document_type)
        )
        docs_by_type = {str(doc_type): count for doc_type, count in type_stats}
        
        # Documents by category
        category_stats = await db.execute(
            select(Document.category, func.count(Document.id))
            .where(Document.is_active == True)
            .group_by(Document.category)
        )
        docs_by_category = {str(category): count for category, count in category_stats}
        
        # Documents by status
        status_stats = await db.execute(
            select(Document.status, func.count(Document.id))
            .where(Document.is_active == True)
            .group_by(Document.status)
        )
        docs_by_status = {str(status): count for status, count in status_stats}
        
        # Documents by compliance status
        compliance_stats = await db.execute(
            select(Document.compliance_status, func.count(Document.id))
            .where(Document.is_active == True)
            .group_by(Document.compliance_status)
        )
        docs_by_compliance = {str(compliance): count for compliance, count in compliance_stats}
        
        # Special counts
        pending_review = await db.scalar(
            select(func.count(Document.id))
            .where(and_(Document.is_active == True, Document.status == DocumentStatus.PENDING))
        )
        
        # Expiring this month
        next_month = datetime.utcnow() + timedelta(days=30)
        expiring_this_month = await db.scalar(
            select(func.count(Document.id))
            .where(and_(
                Document.is_active == True,
                Document.expiry_date.isnot(None),
                Document.expiry_date <= next_month
            ))
        )
        
        # Compliance issues
        compliance_issues = await db.scalar(
            select(func.count(Document.id))
            .where(and_(
                Document.is_active == True,
                Document.compliance_status.in_([ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PENDING_REVIEW])
            ))
        )
        
        # Recent uploads (last 7 days)
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_uploads = await db.scalar(
            select(func.count(Document.id))
            .where(and_(Document.is_active == True, Document.upload_date >= week_ago))
        )
        
        # Top uploaders
        uploader_stats = await db.execute(
            select(Document.uploaded_by, func.count(Document.id))
            .where(Document.is_active == True)
            .group_by(Document.uploaded_by)
            .order_by(desc(func.count(Document.id)))
            .limit(5)
        )
        top_uploaders = [
            {"user": user, "count": count}
            for user, count in uploader_stats
        ]
        
        # Storage by type
        storage_stats = await db.execute(
            select(Document.document_type, func.sum(Document.file_size))
            .where(Document.is_active == True)
            .group_by(Document.document_type)
        )
        storage_by_type = {str(doc_type): size or 0 for doc_type, size in storage_stats}
        
        return DocumentStats(
            total_documents=total_docs or 0,
            total_size_bytes=total_size,
            documents_by_type=docs_by_type,
            documents_by_category=docs_by_category,
            documents_by_status=docs_by_status,
            documents_by_compliance=docs_by_compliance,
            pending_review=pending_review or 0,
            expiring_this_month=expiring_this_month or 0,
            compliance_issues=compliance_issues or 0,
            recent_uploads=recent_uploads or 0,
            top_uploaders=top_uploaders,
            storage_by_type=storage_by_type
        )
        
    except Exception as e:
        logger.error("Failed to get document statistics", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document statistics"
        )


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    db: AsyncSession = Depends(get_async_session),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    document_type: Optional[DocumentType] = Query(None),
    category: Optional[DocumentCategory] = Query(None),
    status: Optional[DocumentStatus] = Query(None),
    compliance_status: Optional[ComplianceStatus] = Query(None),
    client_id: Optional[str] = Query(None),
    is_confidential: Optional[bool] = Query(None),
    uploaded_by: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    sort_by: str = Query("upload_date", regex="^(upload_date|title|file_size|status)$"),
    sort_order: str = Query("desc", regex="^(asc|desc)$")
):
    """List documents with filtering and pagination."""
    try:
        # Build query
        query = select(Document).where(Document.is_active == True)
        
        # Apply filters
        if document_type:
            query = query.where(Document.document_type == document_type)
        if category:
            query = query.where(Document.category == category)
        if status:
            query = query.where(Document.status == status)
        if compliance_status:
            query = query.where(Document.compliance_status == compliance_status)
        if client_id:
            query = query.where(Document.client_id == client_id)
        if is_confidential is not None:
            query = query.where(Document.is_confidential == is_confidential)
        if uploaded_by:
            query = query.where(Document.uploaded_by == uploaded_by)
        
        # Apply search
        if search:
            search_filter = or_(
                Document.title.ilike(f"%{search}%"),
                Document.description.ilike(f"%{search}%"),
                Document.original_name.ilike(f"%{search}%"),
                Document.client_name.ilike(f"%{search}%"),
                Document.hs_code.ilike(f"%{search}%"),
                Document.shipment_ref.ilike(f"%{search}%")
            )
            query = query.where(search_filter)
        
        # Get total count
        count_query = select(func.count(Document.id)).where(Document.is_active == True)
        if document_type:
            count_query = count_query.where(Document.document_type == document_type)
        if category:
            count_query = count_query.where(Document.category == category)
        if status:
            count_query = count_query.where(Document.status == status)
        if compliance_status:
            count_query = count_query.where(Document.compliance_status == compliance_status)
        if client_id:
            count_query = count_query.where(Document.client_id == client_id)
        if is_confidential is not None:
            count_query = count_query.where(Document.is_confidential == is_confidential)
        if uploaded_by:
            count_query = count_query.where(Document.uploaded_by == uploaded_by)
        if search:
            count_query = count_query.where(search_filter)
        
        total_count = await db.scalar(count_query)
        
        # Apply sorting
        sort_column = getattr(Document, sort_by)
        if sort_order == "desc":
            query = query.order_by(desc(sort_column))
        else:
            query = query.order_by(asc(sort_column))
        
        # Apply pagination
        offset = (page - 1) * limit
        query = query.offset(offset).limit(limit)
        
        # Execute query
        result = await db.execute(query)
        documents = result.scalars().all()
        
        # Create pagination metadata using the class method
        pagination = PaginationMeta.create(
            total=total_count or 0,
            limit=limit,
            offset=offset
        )
        
        # Convert to summary format
        document_summaries = [
            DocumentSummary.model_validate(doc) for doc in documents
        ]
        
        return DocumentListResponse(
            documents=document_summaries,
            pagination=pagination,
            total_count=total_count
        )
        
    except Exception as e:
        logger.error("Failed to list documents", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve documents"
        )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """Get document by ID."""
    try:
        query = select(Document).where(
            and_(Document.id == document_id, Document.is_active == True)
        )
        result = await db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Update last accessed timestamp
        document.last_accessed = datetime.utcnow()
        await db.commit()
        
        return DocumentResponse.model_validate(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get document", document_id=document_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document"
        )


@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: int,
    update_data: DocumentUpdate,
    db: AsyncSession = Depends(get_async_session)
):
    """Update document metadata."""
    try:
        current_user = get_current_user()
        
        query = select(Document).where(
            and_(Document.id == document_id, Document.is_active == True)
        )
        result = await db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Update fields
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            if hasattr(document, field):
                setattr(document, field, value)
        
        document.last_modified_by = current_user
        document.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(document)
        
        logger.info(
            "Document updated successfully",
            document_id=document_id,
            user=current_user
        )
        
        return DocumentResponse.model_validate(document)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update document", document_id=document_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update document"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_async_session),
    permanent: bool = Query(False, description="Permanently delete file")
):
    """Delete document (soft delete by default)."""
    try:
        current_user = get_current_user()
        
        query = select(Document).where(
            and_(Document.id == document_id, Document.is_active == True)
        )
        result = await db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        if permanent:
            # Delete physical file
            file_path = UPLOAD_DIR / document.filename
            if file_path.exists():
                await aiofiles.os.remove(file_path)
            
            # Delete from database
            await db.delete(document)
        else:
            # Soft delete
            document.is_active = False
            document.last_modified_by = current_user
            document.updated_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(
            "Document deleted successfully",
            document_id=document_id,
            permanent=permanent,
            user=current_user
        )
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete document", document_id=document_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document"
        )


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: AsyncSession = Depends(get_async_session),
    inline: bool = Query(False, description="Display inline instead of download")
):
    """Download document file."""
    try:
        query = select(Document).where(
            and_(Document.id == document_id, Document.is_active == True)
        )
        result = await db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        file_path = UPLOAD_DIR / document.filename
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on disk"
            )
        
        # Update last accessed timestamp
        document.last_accessed = datetime.utcnow()
        await db.commit()
        
        # Determine content disposition
        disposition = "inline" if inline else "attachment"
        
        return FileResponse(
            path=file_path,
            filename=document.original_name,
            media_type=document.mime_type,
            headers={"Content-Disposition": f'{disposition}; filename="{document.original_name}"'}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to download document", document_id=document_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to download document"
        )


# Search functionality
@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(
    search_params: DocumentSearchParams,
    db: AsyncSession = Depends(get_async_session)
):
    """Advanced document search with filtering."""
    try:
        start_time = datetime.utcnow()
        
        # Build base query
        query = select(Document).where(Document.is_active == True)
        
        # Apply filters from search params
        if search_params.document_type:
            query = query.where(Document.document_type == search_params.document_type)
        if search_params.category:
            query = query.where(Document.category == search_params.category)
        if search_params.status:
            query = query.where(Document.status == search_params.status)
        if search_params.compliance_status:
            query = query.where(Document.compliance_status == search_params.compliance_status)
        if search_params.client_id:
            query = query.where(Document.client_id == search_params.client_id)
        if search_params.client_name:
            query = query.where(Document.client_name.ilike(f"%{search_params.client_name}%"))
        if search_params.hs_code:
            query = query.where(Document.hs_code == search_params.hs_code)
        if search_params.shipment_ref:
            query = query.where(Document.shipment_ref == search_params.shipment_ref)
        if search_params.is_confidential is not None:
            query = query.where(Document.is_confidential == search_params.is_confidential)
        if search_params.uploaded_by:
            query = query.where(Document.uploaded_by == search_params.uploaded_by)
        if search_params.upload_date_from:
            query = query.where(Document.upload_date >= search_params.upload_date_from)
        if search_params.upload_date_to:
            query = query.where(Document.upload_date <= search_params.upload_date_to)
        if search_params.tags:
            for tag in search_params.tags:
                query = query.where(Document.tags.contains([tag]))
        
        # Apply text search
        if search_params.query:
            search_filter = or_(
                Document.title.ilike(f"%{search_params.query}%"),
                Document.description.ilike(f"%{search_params.query}%"),
                Document.original_name.ilike(f"%{search_params.query}%"),
                Document.client_name.ilike(f"%{search_params.query}%"),
                Document.compliance_notes.ilike(f"%{search_params.query}%")
            )
            query = query.where(search_filter)
        
        # Get total count
        count_query = select(func.count(Document.id)).where(Document.is_active == True)
        # Apply same filters to count query
        if search_params.document_type:
            count_query = count_query.where(Document.document_type == search_params.document_type)
        if search_params.category:
            count_query = count_query.where(Document.category == search_params.category)
        if search_params.status:
            count_query = count_query.where(Document.status == search_params.status)
        if search_params.compliance_status:
            count_query = count_query.where(Document.compliance_status == search_params.compliance_status)
        if search_params.client_id:
            count_query = count_query.where(Document.client_id == search_params.client_id)
        if search_params.client_name:
            count_query = count_query.where(Document.client_name.ilike(f"%{search_params.client_name}%"))
        if search_params.hs_code:
            count_query = count_query.where(Document.hs_code == search_params.hs_code)
        if search_params.shipment_ref:
            count_query = count_query.where(Document.shipment_ref == search_params.shipment_ref)
        if search_params.is_confidential is not None:
            count_query = count_query.where(Document.is_confidential == search_params.is_confidential)
        if search_params.uploaded_by:
            count_query = count_query.where(Document.uploaded_by == search_params.uploaded_by)
        if search_params.upload_date_from:
            count_query = count_query.where(Document.upload_date >= search_params.upload_date_from)
        if search_params.upload_date_to:
            count_query = count_query.where(Document.upload_date <= search_params.upload_date_to)
        if search_params.tags:
            for tag in search_params.tags:
                count_query = count_query.where(Document.tags.contains([tag]))
        if search_params.query:
            count_query = count_query.where(search_filter)
        
        total_count = await db.scalar(count_query)
        
        # Apply pagination
        offset = (search_params.page - 1) * search_params.limit
        query = query.offset(offset).limit(search_params.limit)
        
        # Execute query
        result = await db.execute(query)
        documents = result.scalars().all()
        
        # Calculate search time
        end_time = datetime.utcnow()
        search_time_ms = (end_time - start_time).total_seconds() * 1000
        
        # Convert to search results with relevance scoring
        search_results = []
        for doc in documents:
            relevance_score = 1.0  # Simplified scoring
            match_type = "metadata"
            
            if search_params.query:
                # Simple relevance scoring based on matches
                query_lower = search_params.query.lower()
                title_match = query_lower in (doc.title or "").lower()
                name_match = query_lower in doc.original_name.lower()
                
                if title_match and name_match:
                    relevance_score = 1.0
                elif title_match:
                    relevance_score = 0.8
                    match_type = "title"
                elif name_match:
                    relevance_score = 0.6
                    match_type = "filename"
                else:
                    relevance_score = 0.4
            
            search_result = DocumentSearchResult(
                **DocumentSummary.model_validate(doc).model_dump(),
                relevance_score=relevance_score,
                match_type=match_type
            )
            search_results.append(search_result)
        
        # Sort by relevance
        search_results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Create pagination metadata using the class method
        offset = (search_params.page - 1) * search_params.limit
        pagination = PaginationMeta.create(
            total=total_count or 0,
            limit=search_params.limit,
            offset=offset
        )
        
        return DocumentSearchResponse(
            results=search_results,
            pagination=pagination,
            query=search_params.query,
            total_results=total_count,
            search_time_ms=search_time_ms
        )
        
    except Exception as e:
        logger.error("Document search failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Document search failed"
        )


# Bulk operations
@router.post("/bulk", response_model=DocumentBulkOperationResponse)
async def bulk_document_operation(
    operation: DocumentBulkOperation,
    db: AsyncSession = Depends(get_async_session)
):
    """Perform bulk operations on documents."""
    try:
        current_user = get_current_user()
        
        # Get documents
        query = select(Document).where(
            and_(Document.id.in_(operation.document_ids), Document.is_active == True)
        )
        result = await db.execute(query)
        documents = result.scalars().all()
        
        if not documents:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No documents found"
            )
        
        success_count = 0
        error_count = 0
        errors = []
        
        # Perform operation
        if operation.operation == "delete":
            for doc in documents:
                try:
                    doc.is_active = False
                    doc.last_modified_by = current_user
                    doc.updated_at = datetime.utcnow()
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append({"document_id": doc.id, "error": str(e)})
        
        elif operation.operation == "update_status":
            new_status = operation.parameters.get("status")
            if not new_status:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Status parameter required"
                )
            
            for doc in documents:
                try:
                    doc.status = DocumentStatus(new_status)
                    doc.last_modified_by = current_user
                    doc.updated_at = datetime.utcnow()
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append({"document_id": doc.id, "error": str(e)})
        
        elif operation.operation == "update_category":
            new_category = operation.parameters.get("category")
            if not new_category:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Category parameter required"
                )
            
            for doc in documents:
                try:
                    doc.category = DocumentCategory(new_category)
                    doc.last_modified_by = current_user
                    doc.updated_at = datetime.utcnow()
                    success_count += 1
                except Exception as e:
                    error_count += 1
                    errors.append({"document_id": doc.id, "error": str(e)})
        
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown operation: {operation.operation}"
            )
        
        # Commit changes
        await db.commit()
        
        logger.info(
            "Bulk operation completed",
            operation=operation.operation,
            processed=len(documents),
            success=success_count,
            errors=error_count,
            user=current_user
        )
        
        return DocumentBulkOperationResponse(
            success=error_count == 0,
            processed_count=len(documents),
            success_count=success_count,
            error_count=error_count,
            errors=errors,
            message=f"Bulk {operation.operation} completed: {success_count} successful, {error_count} failed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Bulk operation failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Bulk operation failed"
        )


# Category management
@router.post("/categories", response_model=DocumentCategoryResponse)
async def create_document_category(
    category_data: DocumentCategoryCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Create a new document category."""
    try:
        category = DocumentCategoryDefinition(
            name=category_data.name,
            description=category_data.description,
            color=category_data.color,
            icon=category_data.icon,
            parent_category_id=category_data.parent_category_id,
            sort_order=category_data.sort_order
        )
        
        db.add(category)
        await db.commit()
        await db.refresh(category)
        
        logger.info("Document category created", category_id=category.id, name=category.name)
        
        return DocumentCategoryResponse.model_validate(category)
        
    except Exception as e:
        logger.error("Failed to create document category", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create document category"
        )


# Document sharing
@router.post("/{document_id}/share", response_model=DocumentShareResponse)
async def share_document(
    document_id: int,
    share_data: DocumentShareCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Share a document with users or groups."""
    try:
        current_user = get_current_user()
        
        # Check if document exists
        query = select(Document).where(
            and_(Document.id == document_id, Document.is_active == True)
        )
        result = await db.execute(query)
        document = result.scalar_one_or_none()
        
        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )
        
        # Create share record
        share = DocumentShare(
            document_id=document_id,
            shared_with_user=share_data.shared_with_user,
            shared_with_group=share_data.shared_with_group,
            shared_with_email=share_data.shared_with_email,
            permission=share_data.permission,
            can_download=share_data.can_download,
            can_share=share_data.can_share,
            expires_at=share_data.expires_at,
            max_access_count=share_data.max_access_count,
            shared_by=current_user
        )
        
        db.add(share)
        await db.commit()
        await db.refresh(share)
        
        logger.info(
            "Document shared successfully",
            document_id=document_id,
            share_id=share.id,
            shared_by=current_user
        )
        
        return DocumentShareResponse.model_validate(share)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to share document", document_id=document_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to share document"
        )


@router.get("/{document_id}/shares", response_model=List[DocumentShareResponse])
async def list_document_shares(
    document_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """List all shares for a document."""
    try:
        query = select(DocumentShare).where(
            and_(
                DocumentShare.document_id == document_id,
                DocumentShare.is_active == True
            )
        ).order_by(desc(DocumentShare.created_at))
        
        result = await db.execute(query)
        shares = result.scalars().all()
        
        return [DocumentShareResponse.model_validate(share) for share in shares]
        
    except Exception as e:
        logger.error("Failed to list document shares", document_id=document_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document shares"
        )


@router.delete("/shares/{share_id}")
async def revoke_document_share(
    share_id: int,
    db: AsyncSession = Depends(get_async_session)
):
    """Revoke a document share."""
    try:
        current_user = get_current_user()
        
        query = select(DocumentShare).where(
            and_(DocumentShare.id == share_id, DocumentShare.is_active == True)
        )
        result = await db.execute(query)
        share = result.scalar_one_or_none()
        
        if not share:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Share not found"
            )
        
        # Check permissions (only the sharer or admin can revoke)
        if share.shared_by != current_user:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to revoke this share"
            )
        
        share.is_active = False
        share.updated_at = datetime.utcnow()
        
        await db.commit()
        
        logger.info(
            "Document share revoked",
            share_id=share_id,
            revoked_by=current_user
        )
        
        return {"message": "Share revoked successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to revoke document share", share_id=share_id, error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to revoke document share"
        )