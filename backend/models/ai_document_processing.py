"""
AI Document Processing models for the Customs Broker Portal.

This module contains models for AI-powered document processing, including
OCR results, field extraction, classification, and processing history.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum
from decimal import Decimal

from sqlalchemy import (
    String, Integer, Text, Boolean, DateTime, CheckConstraint, Index,
    ForeignKey, func, BigInteger, JSON, Numeric, DECIMAL
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ProcessingStatus(str, Enum):
    """Document processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DocumentTypeDetection(str, Enum):
    """AI-detected document type enumeration."""
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


class ExtractionConfidence(str, Enum):
    """Confidence level for extracted data."""
    HIGH = "high"      # 0.8-1.0
    MEDIUM = "medium"  # 0.5-0.79
    LOW = "low"        # 0.0-0.49


class AIDocumentProcessing(Base):
    """
    AI document processing record for tracking processing status and results.
    """
    
    __tablename__ = "ai_document_processing"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to documents table
    document_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Processing metadata
    processing_status: Mapped[ProcessingStatus] = mapped_column(
        String(20), 
        nullable=False, 
        index=True,
        default=ProcessingStatus.PENDING
    )
    processing_started_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    processing_completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    processing_duration_seconds: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 3),
        nullable=True
    )
    
    # AI model information
    ai_model_used: Mapped[str] = mapped_column(String(100), nullable=False, default="claude-3.5-sonnet")
    ai_model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Document type detection
    detected_document_type: Mapped[Optional[DocumentTypeDetection]] = mapped_column(
        String(50),
        nullable=True,
        index=True
    )
    document_type_confidence: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(5, 4),
        nullable=True
    )
    
    # OCR and text extraction
    ocr_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ocr_confidence: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(5, 4),
        nullable=True
    )
    
    # Extracted structured data
    extracted_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    extraction_confidence: Mapped[Optional[ExtractionConfidence]] = mapped_column(
        String(10),
        nullable=True
    )
    
    # AI analysis results
    ai_analysis: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    suggested_hs_codes: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    compliance_flags: Mapped[Optional[List[str]]] = mapped_column(JSON, nullable=True)
    
    # Error handling
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Processing metadata
    processing_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    requires_manual_review: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    reviewed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
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
        back_populates="ai_processing",
        lazy="select"
    )
    
    extracted_fields: Mapped[List["ExtractedField"]] = relationship(
        "ExtractedField",
        back_populates="processing",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Ensure valid processing status
        CheckConstraint(
            f"processing_status IN {tuple(status.value for status in ProcessingStatus)}",
            name="ck_ai_processing_status"
        ),
        
        # Ensure valid document type
        CheckConstraint(
            f"detected_document_type IS NULL OR detected_document_type IN {tuple(dt.value for dt in DocumentTypeDetection)}",
            name="ck_ai_processing_document_type"
        ),
        
        # Ensure valid extraction confidence
        CheckConstraint(
            f"extraction_confidence IS NULL OR extraction_confidence IN {tuple(ec.value for ec in ExtractionConfidence)}",
            name="ck_ai_processing_extraction_confidence"
        ),
        
        # Confidence score constraints
        CheckConstraint(
            "document_type_confidence IS NULL OR (document_type_confidence >= 0.0 AND document_type_confidence <= 1.0)",
            name="ck_ai_processing_document_type_confidence"
        ),
        
        CheckConstraint(
            "ocr_confidence IS NULL OR (ocr_confidence >= 0.0 AND ocr_confidence <= 1.0)",
            name="ck_ai_processing_ocr_confidence"
        ),
        
        # Processing duration constraint
        CheckConstraint(
            "processing_duration_seconds IS NULL OR processing_duration_seconds >= 0",
            name="ck_ai_processing_duration"
        ),
        
        # Composite indexes for performance
        Index("ix_ai_processing_status_created", "processing_status", "created_at"),
        Index("ix_ai_processing_document_type_confidence", "detected_document_type", "document_type_confidence"),
        Index("ix_ai_processing_requires_review", "requires_manual_review", "processing_status"),
    )
    
    def __repr__(self) -> str:
        """String representation of AIDocumentProcessing."""
        return (
            f"<AIDocumentProcessing(id={self.id}, document_id={self.document_id}, "
            f"status='{self.processing_status}', type='{self.detected_document_type}')>"
        )
    
    @property
    def is_completed(self) -> bool:
        """Check if processing is completed."""
        return self.processing_status == ProcessingStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """Check if processing failed."""
        return self.processing_status == ProcessingStatus.FAILED
    
    @property
    def is_processing(self) -> bool:
        """Check if currently processing."""
        return self.processing_status == ProcessingStatus.PROCESSING
    
    @property
    def processing_duration_minutes(self) -> Optional[float]:
        """Get processing duration in minutes."""
        if self.processing_duration_seconds:
            return float(self.processing_duration_seconds) / 60.0
        return None


class ExtractedField(Base):
    """
    Individual extracted field from document processing.
    """
    
    __tablename__ = "extracted_fields"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to processing record
    processing_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("ai_document_processing.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Field information
    field_name: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    field_type: Mapped[str] = mapped_column(String(50), nullable=False)  # text, number, date, currency, etc.
    field_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    field_value_normalized: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Cleaned/normalized value
    
    # Confidence and validation
    confidence_score: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(5, 4),
        nullable=True
    )
    is_validated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    validation_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Position information (for OCR)
    bounding_box: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # x, y, width, height
    page_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Manual corrections
    corrected_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    corrected_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    corrected_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    correction_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
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
    processing: Mapped["AIDocumentProcessing"] = relationship(
        "AIDocumentProcessing",
        back_populates="extracted_fields",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Confidence score constraint
        CheckConstraint(
            "confidence_score IS NULL OR (confidence_score >= 0.0 AND confidence_score <= 1.0)",
            name="ck_extracted_field_confidence"
        ),
        
        # Page number constraint
        CheckConstraint(
            "page_number IS NULL OR page_number > 0",
            name="ck_extracted_field_page_number"
        ),
        
        # Composite indexes for performance
        Index("ix_extracted_field_name_confidence", "field_name", "confidence_score"),
        Index("ix_extracted_field_validated", "is_validated", "field_name"),
        Index("ix_extracted_field_corrected", "corrected_by", "corrected_at"),
    )
    
    def __repr__(self) -> str:
        """String representation of ExtractedField."""
        return (
            f"<ExtractedField(id={self.id}, name='{self.field_name}', "
            f"value='{self.field_value[:50] if self.field_value else None}...')>"
        )
    
    @property
    def final_value(self) -> Optional[str]:
        """Get the final value (corrected if available, otherwise original)."""
        return self.corrected_value or self.field_value
    
    @property
    def is_corrected(self) -> bool:
        """Check if field has been manually corrected."""
        return self.corrected_value is not None
    
    @property
    def has_high_confidence(self) -> bool:
        """Check if field has high confidence score."""
        return self.confidence_score is not None and self.confidence_score >= Decimal("0.8")


class ProcessingTemplate(Base):
    """
    Templates for document processing configuration.
    """
    
    __tablename__ = "processing_templates"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Template information
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_type: Mapped[DocumentTypeDetection] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    
    # Processing configuration
    field_definitions: Mapped[Dict[str, Any]] = mapped_column(JSON, nullable=False)
    validation_rules: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    extraction_prompts: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Template metadata
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[str] = mapped_column(String(20), nullable=False, default="1.0")
    created_by: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Usage statistics
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    success_rate: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(5, 4),
        nullable=True
    )
    
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
    
    # Table constraints and indexes
    __table_args__ = (
        # Ensure valid document type
        CheckConstraint(
            f"document_type IN {tuple(dt.value for dt in DocumentTypeDetection)}",
            name="ck_processing_template_document_type"
        ),
        
        # Success rate constraint
        CheckConstraint(
            "success_rate IS NULL OR (success_rate >= 0.0 AND success_rate <= 1.0)",
            name="ck_processing_template_success_rate"
        ),
        
        # Usage count constraint
        CheckConstraint(
            "usage_count >= 0",
            name="ck_processing_template_usage_count"
        ),
        
        # Composite indexes for performance
        Index("ix_processing_template_type_active", "document_type", "is_active"),
        Index("ix_processing_template_success_rate", "success_rate", "usage_count"),
    )
    
    def __repr__(self) -> str:
        """String representation of ProcessingTemplate."""
        return (
            f"<ProcessingTemplate(id={self.id}, name='{self.name}', "
            f"type='{self.document_type}', version='{self.version}')>"
        )


# Update the Document model to include the AI processing relationship
# This would be added to the existing Document model in models/documents.py
# ai_processing: Mapped[List["AIDocumentProcessing"]] = relationship(
#     "AIDocumentProcessing",
#     back_populates="document",
#     cascade="all, delete-orphan",
#     lazy="select"
# )