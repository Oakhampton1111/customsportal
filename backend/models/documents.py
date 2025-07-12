"""
Document management models for the Customs Broker Portal.

This module contains models for document storage, categorization, sharing,
and metadata management for the customs broker document management system.
"""

from datetime import datetime
from typing import List, Optional
from enum import Enum

from sqlalchemy import (
    String, Integer, Text, Boolean, DateTime, CheckConstraint, Index,
    ForeignKey, func, BigInteger, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class DocumentType(str, Enum):
    """Document type enumeration."""
    INVOICE = "invoice"
    PACKING_LIST = "packing_list"
    CERTIFICATE = "certificate"
    PERMIT = "permit"
    DECLARATION = "declaration"
    RULING = "ruling"
    CORRESPONDENCE = "correspondence"
    OTHER = "other"


class DocumentCategory(str, Enum):
    """Document category enumeration."""
    IMPORT = "import"
    EXPORT = "export"
    COMPLIANCE = "compliance"
    REGULATORY = "regulatory"
    CLIENT = "client"


class DocumentStatus(str, Enum):
    """Document status enumeration."""
    DRAFT = "draft"
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"
    ARCHIVED = "archived"


class ComplianceStatus(str, Enum):
    """Compliance status enumeration."""
    COMPLIANT = "compliant"
    NON_COMPLIANT = "non_compliant"
    PENDING_REVIEW = "pending_review"
    NOT_APPLICABLE = "not_applicable"


class SharePermission(str, Enum):
    """Share permission enumeration."""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class Document(Base):
    """
    Document model for storing document metadata and file information.
    
    This model stores comprehensive document information including file metadata,
    categorization, status tracking, and compliance information.
    """
    
    __tablename__ = "documents"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # File information
    filename: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    mime_type: Mapped[str] = mapped_column(String(100), nullable=False)
    file_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, index=True)  # SHA-256 hash
    
    # Document metadata
    title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_type: Mapped[DocumentType] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[DocumentCategory] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[DocumentStatus] = mapped_column(String(50), nullable=False, index=True, default=DocumentStatus.DRAFT)
    
    # Business context
    client_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    client_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    hs_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    shipment_ref: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Tags and classification
    tags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    document_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)  # Additional flexible metadata
    
    # Compliance and security
    is_confidential: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    compliance_status: Mapped[ComplianceStatus] = mapped_column(
        String(50), 
        nullable=False, 
        index=True, 
        default=ComplianceStatus.NOT_APPLICABLE
    )
    compliance_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Version control
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    parent_document_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("documents.id", ondelete="SET NULL"),
        nullable=True
    )
    
    # Dates
    upload_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False,
        index=True
    )
    expiry_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    last_accessed: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # User tracking
    uploaded_by: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    last_modified_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Status flags
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    parent_document: Mapped[Optional["Document"]] = relationship(
        "Document",
        remote_side=[id],
        back_populates="child_documents",
        lazy="select"
    )
    
    child_documents: Mapped[List["Document"]] = relationship(
        "Document",
        back_populates="parent_document",
        lazy="select"
    )
    
    document_categories: Mapped[List["DocumentCategoryMapping"]] = relationship(
        "DocumentCategoryMapping",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    document_shares: Mapped[List["DocumentShare"]] = relationship(
        "DocumentShare",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    ai_processing: Mapped[List["AIDocumentProcessing"]] = relationship(
        "AIDocumentProcessing",
        back_populates="document",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Ensure valid document types
        CheckConstraint(
            f"document_type IN {tuple(dt.value for dt in DocumentType)}",
            name="ck_documents_type"
        ),
        
        # Ensure valid categories
        CheckConstraint(
            f"category IN {tuple(cat.value for cat in DocumentCategory)}",
            name="ck_documents_category"
        ),
        
        # Ensure valid status
        CheckConstraint(
            f"status IN {tuple(status.value for status in DocumentStatus)}",
            name="ck_documents_status"
        ),
        
        # Ensure valid compliance status
        CheckConstraint(
            f"compliance_status IN {tuple(cs.value for cs in ComplianceStatus)}",
            name="ck_documents_compliance_status"
        ),
        
        # File size constraint
        CheckConstraint(
            "file_size > 0",
            name="ck_documents_file_size"
        ),
        
        # Version constraint
        CheckConstraint(
            "version > 0",
            name="ck_documents_version"
        ),
        
        # Composite indexes for performance
        Index("ix_documents_type_category", "document_type", "category"),
        Index("ix_documents_status_compliance", "status", "compliance_status"),
        Index("ix_documents_client_shipment", "client_id", "shipment_ref"),
        Index("ix_documents_upload_date_status", "upload_date", "status"),
        Index("ix_documents_expiry_active", "expiry_date", "is_active"),
        Index("ix_documents_confidential_active", "is_confidential", "is_active"),
        Index("ix_documents_full_text", "filename", "original_name", "description"),
    )
    
    def __repr__(self) -> str:
        """String representation of Document."""
        return (
            f"<Document(id={self.id}, filename='{self.filename}', "
            f"type='{self.document_type}', status='{self.status}')>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.original_name} ({self.document_type})"
    
    @property
    def is_expired(self) -> bool:
        """Check if document has expired."""
        if not self.expiry_date:
            return False
        return datetime.utcnow() > self.expiry_date
    
    @property
    def is_expiring_soon(self, days: int = 30) -> bool:
        """Check if document is expiring within specified days."""
        if not self.expiry_date:
            return False
        from datetime import timedelta
        threshold = datetime.utcnow() + timedelta(days=days)
        return self.expiry_date <= threshold
    
    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return round(self.file_size / (1024 * 1024), 2)
    
    def get_display_name(self) -> str:
        """Get display name for the document."""
        return self.title or self.original_name
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the document."""
        if not self.tags:
            self.tags = []
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the document."""
        if self.tags and tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if document has a specific tag."""
        return self.tags is not None and tag in self.tags


class DocumentCategoryMapping(Base):
    """
    Document category mapping for flexible categorization.
    
    Allows documents to belong to multiple categories and subcategories.
    """
    
    __tablename__ = "document_category_mappings"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("document_categories.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Metadata
    assigned_by: Mapped[str] = mapped_column(String(100), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="document_categories",
        lazy="select"
    )
    
    category: Mapped["DocumentCategoryDefinition"] = relationship(
        "DocumentCategoryDefinition",
        back_populates="document_mappings",
        lazy="select"
    )
    
    # Table constraints
    __table_args__ = (
        # Unique constraint to prevent duplicate mappings
        Index("ix_document_category_unique", "document_id", "category_id", unique=True),
    )


class DocumentCategoryDefinition(Base):
    """
    Document category definitions for flexible categorization system.
    
    Allows for hierarchical and custom document categories.
    """
    
    __tablename__ = "document_categories"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Category information
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)  # Hex color code
    icon: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Hierarchy
    parent_category_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("document_categories.id", ondelete="CASCADE"),
        nullable=True
    )
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    parent_category: Mapped[Optional["DocumentCategoryDefinition"]] = relationship(
        "DocumentCategoryDefinition",
        remote_side=[id],
        back_populates="child_categories",
        lazy="select"
    )
    
    child_categories: Mapped[List["DocumentCategoryDefinition"]] = relationship(
        "DocumentCategoryDefinition",
        back_populates="parent_category",
        lazy="select"
    )
    
    document_mappings: Mapped[List["DocumentCategoryMapping"]] = relationship(
        "DocumentCategoryMapping",
        back_populates="category",
        cascade="all, delete-orphan",
        lazy="select"
    )


class DocumentShare(Base):
    """
    Document sharing and permissions model.
    
    Manages document access permissions and sharing with users or groups.
    """
    
    __tablename__ = "document_shares"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Sharing information
    shared_with_user: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    shared_with_group: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    shared_with_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    
    # Permissions
    permission: Mapped[SharePermission] = mapped_column(String(20), nullable=False)
    can_download: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    can_share: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Expiry and limits
    expires_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    access_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_access_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Tracking
    shared_by: Mapped[str] = mapped_column(String(100), nullable=False)
    last_accessed: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    document: Mapped["Document"] = relationship(
        "Document",
        back_populates="document_shares",
        lazy="select"
    )
    
    # Table constraints
    __table_args__ = (
        # Ensure valid permissions
        CheckConstraint(
            f"permission IN {tuple(perm.value for perm in SharePermission)}",
            name="ck_document_shares_permission"
        ),
        
        # Ensure at least one sharing target is specified
        CheckConstraint(
            "shared_with_user IS NOT NULL OR shared_with_group IS NOT NULL OR shared_with_email IS NOT NULL",
            name="ck_document_shares_target"
        ),
        
        # Access count constraints
        CheckConstraint(
            "access_count >= 0",
            name="ck_document_shares_access_count"
        ),
        
        CheckConstraint(
            "max_access_count IS NULL OR max_access_count > 0",
            name="ck_document_shares_max_access_count"
        ),
        
        # Composite indexes
        Index("ix_document_shares_document_user", "document_id", "shared_with_user"),
        Index("ix_document_shares_document_group", "document_id", "shared_with_group"),
        Index("ix_document_shares_expires_active", "expires_at", "is_active"),
    )
    
    @property
    def is_expired(self) -> bool:
        """Check if share has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    @property
    def is_access_limit_reached(self) -> bool:
        """Check if access limit has been reached."""
        if not self.max_access_count:
            return False
        return self.access_count >= self.max_access_count
    
    @property
    def can_access(self) -> bool:
        """Check if share can be accessed."""
        return (
            self.is_active and 
            not self.is_expired and 
            not self.is_access_limit_reached
        )
    
    def increment_access_count(self) -> None:
        """Increment access count and update last accessed time."""
        self.access_count += 1
        self.last_accessed = datetime.utcnow()