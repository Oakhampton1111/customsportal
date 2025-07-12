"""
Document management schemas for the Customs Broker Portal.

This module contains Pydantic schemas for document management API endpoints,
including request/response models, validation, and serialization.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Union
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field
from pydantic.types import PositiveInt

from schemas.common import BaseSchema, PaginationMeta, SearchParams
from models.documents import (
    DocumentType, DocumentCategory, DocumentStatus, 
    ComplianceStatus, SharePermission
)


# Base document schemas
class DocumentBase(BaseModel):
    """Base document schema with common fields."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    title: Optional[str] = Field(None, max_length=255, description="Document title")
    description: Optional[str] = Field(None, description="Document description")
    document_type: DocumentType = Field(..., description="Type of document")
    category: DocumentCategory = Field(..., description="Document category")
    status: DocumentStatus = Field(DocumentStatus.DRAFT, description="Document status")
    
    # Business context
    client_id: Optional[str] = Field(None, max_length=100, description="Client identifier")
    client_name: Optional[str] = Field(None, max_length=255, description="Client name")
    hs_code: Optional[str] = Field(None, max_length=10, description="HS code")
    shipment_ref: Optional[str] = Field(None, max_length=100, description="Shipment reference")
    
    # Tags and metadata
    tags: Optional[List[str]] = Field(default_factory=list, description="Document tags")
    document_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Additional metadata")
    
    # Compliance
    is_confidential: bool = Field(False, description="Whether document is confidential")
    compliance_status: ComplianceStatus = Field(
        ComplianceStatus.NOT_APPLICABLE, 
        description="Compliance status"
    )
    compliance_notes: Optional[str] = Field(None, description="Compliance notes")
    
    # Dates
    expiry_date: Optional[datetime] = Field(None, description="Document expiry date")
    
    @field_validator('hs_code')
    @classmethod
    def validate_hs_code(cls, v):
        """Validate HS code format."""
        if v:
            # Remove any spaces or special characters
            cleaned = ''.join(c for c in v if c.isdigit())
            if len(cleaned) not in [2, 4, 6, 8, 10]:
                raise ValueError("HS code must be 2, 4, 6, 8, or 10 digits")
            return cleaned
        return v
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate and clean tags."""
        if v:
            # Remove duplicates and empty tags
            cleaned_tags = list(set(tag.strip().lower() for tag in v if tag.strip()))
            return cleaned_tags
        return []


class DocumentCreate(DocumentBase):
    """Schema for creating a new document."""
    
    original_name: str = Field(..., max_length=255, description="Original filename")
    uploaded_by: str = Field(..., max_length=100, description="User who uploaded the document")


class DocumentUpdate(BaseModel):
    """Schema for updating document metadata."""
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        use_enum_values=True
    )
    
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = Field(None)
    document_type: Optional[DocumentType] = Field(None)
    category: Optional[DocumentCategory] = Field(None)
    status: Optional[DocumentStatus] = Field(None)
    
    client_id: Optional[str] = Field(None, max_length=100)
    client_name: Optional[str] = Field(None, max_length=255)
    hs_code: Optional[str] = Field(None, max_length=10)
    shipment_ref: Optional[str] = Field(None, max_length=100)
    
    tags: Optional[List[str]] = Field(None)
    document_metadata: Optional[Dict[str, Any]] = Field(None)
    
    is_confidential: Optional[bool] = Field(None)
    compliance_status: Optional[ComplianceStatus] = Field(None)
    compliance_notes: Optional[str] = Field(None)
    
    expiry_date: Optional[datetime] = Field(None)
    last_modified_by: Optional[str] = Field(None, max_length=100)


class DocumentResponse(DocumentBase):
    """Schema for document response."""
    
    id: int = Field(..., description="Document ID")
    filename: str = Field(..., description="Stored filename")
    original_name: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    mime_type: str = Field(..., description="MIME type")
    file_hash: Optional[str] = Field(None, description="File hash (SHA-256)")
    
    version: int = Field(..., description="Document version")
    parent_document_id: Optional[int] = Field(None, description="Parent document ID")
    
    upload_date: datetime = Field(..., description="Upload timestamp")
    last_accessed: Optional[datetime] = Field(None, description="Last access timestamp")
    uploaded_by: str = Field(..., description="User who uploaded")
    last_modified_by: Optional[str] = Field(None, description="User who last modified")
    
    is_active: bool = Field(..., description="Whether document is active")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    @computed_field
    @property
    def file_size_mb(self) -> float:
        """File size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2)
    
    @computed_field
    @property
    def is_expired(self) -> bool:
        """Whether document has expired."""
        if not self.expiry_date:
            return False
        return datetime.utcnow() > self.expiry_date
    
    @computed_field
    @property
    def is_expiring_soon(self) -> bool:
        """Whether document is expiring within 30 days."""
        if not self.expiry_date:
            return False
        from datetime import timedelta
        threshold = datetime.utcnow() + timedelta(days=30)
        return self.expiry_date <= threshold
    
    @computed_field
    @property
    def display_name(self) -> str:
        """Display name for the document."""
        return self.title or self.original_name


class DocumentSummary(BaseModel):
    """Summary schema for document lists."""
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    id: int
    filename: str
    original_name: str
    title: Optional[str]
    document_type: DocumentType
    category: DocumentCategory
    status: DocumentStatus
    file_size: int
    upload_date: datetime
    uploaded_by: str
    is_confidential: bool
    compliance_status: ComplianceStatus
    
    @computed_field
    @property
    def display_name(self) -> str:
        """Display name for the document."""
        return self.title or self.original_name
    
    @computed_field
    @property
    def file_size_mb(self) -> float:
        """File size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2)


# Upload schemas
class DocumentUploadResponse(BaseModel):
    """Response schema for document upload."""
    
    model_config = ConfigDict(from_attributes=True)
    
    success: bool = Field(True, description="Upload success status")
    document_id: int = Field(..., description="Created document ID")
    filename: str = Field(..., description="Stored filename")
    original_name: str = Field(..., description="Original filename")
    file_size: int = Field(..., description="File size in bytes")
    upload_url: Optional[str] = Field(None, description="URL for accessing the document")
    message: str = Field("Document uploaded successfully", description="Success message")


class DocumentUploadError(BaseModel):
    """Error schema for document upload failures."""
    
    success: bool = Field(False, description="Upload success status")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


# Search and filter schemas
class DocumentSearchParams(SearchParams):
    """Extended search parameters for documents."""
    
    document_type: Optional[DocumentType] = Field(None, description="Filter by document type")
    category: Optional[DocumentCategory] = Field(None, description="Filter by category")
    status: Optional[DocumentStatus] = Field(None, description="Filter by status")
    compliance_status: Optional[ComplianceStatus] = Field(None, description="Filter by compliance status")
    
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    client_name: Optional[str] = Field(None, description="Filter by client name")
    hs_code: Optional[str] = Field(None, description="Filter by HS code")
    shipment_ref: Optional[str] = Field(None, description="Filter by shipment reference")
    
    is_confidential: Optional[bool] = Field(None, description="Filter by confidential status")
    is_expired: Optional[bool] = Field(None, description="Filter by expiry status")
    is_expiring_soon: Optional[bool] = Field(None, description="Filter by expiring soon")
    
    uploaded_by: Optional[str] = Field(None, description="Filter by uploader")
    upload_date_from: Optional[datetime] = Field(None, description="Filter by upload date from")
    upload_date_to: Optional[datetime] = Field(None, description="Filter by upload date to")
    
    tags: Optional[List[str]] = Field(None, description="Filter by tags")
    
    @field_validator('tags')
    @classmethod
    def validate_tags(cls, v):
        """Validate and clean tags."""
        if v:
            return [tag.strip().lower() for tag in v if tag.strip()]
        return v


class DocumentSearchResult(DocumentSummary):
    """Document search result with relevance scoring."""
    
    relevance_score: float = Field(..., description="Search relevance score (0.0-1.0)")
    match_type: str = Field(..., description="Type of match (filename, content, metadata)")
    highlighted_text: Optional[str] = Field(None, description="Highlighted matching text")


class DocumentSearchResponse(BaseModel):
    """Response schema for document search."""
    
    model_config = ConfigDict(from_attributes=True)
    
    results: List[DocumentSearchResult] = Field(..., description="Search results")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
    query: Optional[str] = Field(None, description="Search query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Applied filters")
    total_results: int = Field(..., description="Total number of results")
    search_time_ms: float = Field(..., description="Search execution time in milliseconds")


# Category schemas
class DocumentCategoryCreate(BaseModel):
    """Schema for creating document categories."""
    
    name: str = Field(..., max_length=100, description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    color: Optional[str] = Field(None, max_length=7, description="Hex color code")
    icon: Optional[str] = Field(None, max_length=50, description="Icon name")
    parent_category_id: Optional[int] = Field(None, description="Parent category ID")
    sort_order: int = Field(0, description="Sort order")
    
    @field_validator('color')
    @classmethod
    def validate_color(cls, v):
        """Validate hex color code."""
        if v and not v.startswith('#'):
            v = f"#{v}"
        if v and len(v) != 7:
            raise ValueError("Color must be a valid hex code (e.g., #FF0000)")
        return v


class DocumentCategoryResponse(BaseModel):
    """Schema for document category response."""
    
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    name: str
    description: Optional[str]
    color: Optional[str]
    icon: Optional[str]
    parent_category_id: Optional[int]
    sort_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Computed fields
    document_count: Optional[int] = Field(None, description="Number of documents in category")
    child_categories: Optional[List["DocumentCategoryResponse"]] = Field(None, description="Child categories")


# Share schemas
class DocumentShareCreate(BaseModel):
    """Schema for creating document shares."""
    
    shared_with_user: Optional[str] = Field(None, max_length=100, description="Username to share with")
    shared_with_group: Optional[str] = Field(None, max_length=100, description="Group to share with")
    shared_with_email: Optional[str] = Field(None, max_length=255, description="Email to share with")
    
    permission: SharePermission = Field(..., description="Share permission level")
    can_download: bool = Field(True, description="Allow download")
    can_share: bool = Field(False, description="Allow resharing")
    
    expires_at: Optional[datetime] = Field(None, description="Share expiry date")
    max_access_count: Optional[int] = Field(None, description="Maximum access count")
    
    @field_validator('shared_with_email')
    @classmethod
    def validate_email(cls, v):
        """Basic email validation."""
        if v and '@' not in v:
            raise ValueError("Invalid email format")
        return v
    
    def model_post_init(self, __context):
        """Validate that at least one sharing target is specified."""
        if not any([self.shared_with_user, self.shared_with_group, self.shared_with_email]):
            raise ValueError("At least one sharing target must be specified")


class DocumentShareResponse(BaseModel):
    """Schema for document share response."""
    
    model_config = ConfigDict(from_attributes=True, use_enum_values=True)
    
    id: int
    document_id: int
    shared_with_user: Optional[str]
    shared_with_group: Optional[str]
    shared_with_email: Optional[str]
    permission: SharePermission
    can_download: bool
    can_share: bool
    expires_at: Optional[datetime]
    access_count: int
    max_access_count: Optional[int]
    shared_by: str
    last_accessed: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    @computed_field
    @property
    def is_expired(self) -> bool:
        """Whether share has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @computed_field
    @property
    def is_access_limit_reached(self) -> bool:
        """Whether access limit has been reached."""
        if not self.max_access_count:
            return False
        return self.access_count >= self.max_access_count
    
    @computed_field
    @property
    def can_access(self) -> bool:
        """Whether share can be accessed."""
        return (
            self.is_active and 
            not self.is_expired and 
            not self.is_access_limit_reached
        )


# Statistics schemas
class DocumentStats(BaseModel):
    """Document statistics schema."""
    
    total_documents: int = Field(..., description="Total number of documents")
    total_size_bytes: int = Field(..., description="Total storage used in bytes")
    documents_by_type: Dict[str, int] = Field(..., description="Document count by type")
    documents_by_category: Dict[str, int] = Field(..., description="Document count by category")
    documents_by_status: Dict[str, int] = Field(..., description="Document count by status")
    documents_by_compliance: Dict[str, int] = Field(..., description="Document count by compliance status")
    
    pending_review: int = Field(..., description="Documents pending review")
    expiring_this_month: int = Field(..., description="Documents expiring this month")
    compliance_issues: int = Field(..., description="Documents with compliance issues")
    recent_uploads: int = Field(..., description="Documents uploaded in last 7 days")
    
    top_uploaders: List[Dict[str, Union[str, int]]] = Field(..., description="Top document uploaders")
    storage_by_type: Dict[str, int] = Field(..., description="Storage usage by document type")
    
    @computed_field
    @property
    def total_size_mb(self) -> float:
        """Total storage in megabytes."""
        return round(self.total_size_bytes / (1024 * 1024), 2)
    
    @computed_field
    @property
    def total_size_gb(self) -> float:
        """Total storage in gigabytes."""
        return round(self.total_size_bytes / (1024 * 1024 * 1024), 2)


# Bulk operation schemas
class DocumentBulkOperation(BaseModel):
    """Schema for bulk document operations."""
    
    document_ids: List[int] = Field(..., min_length=1, description="List of document IDs")
    operation: str = Field(..., description="Operation to perform")
    parameters: Optional[Dict[str, Any]] = Field(None, description="Operation parameters")


class DocumentBulkOperationResponse(BaseModel):
    """Response schema for bulk operations."""
    
    success: bool = Field(..., description="Overall operation success")
    processed_count: int = Field(..., description="Number of documents processed")
    success_count: int = Field(..., description="Number of successful operations")
    error_count: int = Field(..., description="Number of failed operations")
    errors: List[Dict[str, Any]] = Field(..., description="List of errors")
    message: str = Field(..., description="Operation summary message")


# List response schemas
class DocumentListResponse(BaseModel):
    """Response schema for document lists."""
    
    documents: List[DocumentSummary] = Field(..., description="List of documents")
    pagination: PaginationMeta = Field(..., description="Pagination metadata")
    filters: Optional[Dict[str, Any]] = Field(None, description="Applied filters")
    total_count: int = Field(..., description="Total number of documents")


# Forward reference resolution
DocumentCategoryResponse.model_rebuild()