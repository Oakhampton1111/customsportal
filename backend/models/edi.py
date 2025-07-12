"""
EDI (Electronic Data Interchange) models for the Customs Broker Portal.

This module contains models for EDI message processing, job registration,
customs declarations, and ABF Integrated Cargo System (ICS) integration.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from enum import Enum

from sqlalchemy import (
    String, Integer, Text, Boolean, DateTime, CheckConstraint, Index,
    ForeignKey, func, JSON, UniqueConstraint
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class EDIMessageType(str, Enum):
    """EDI message type enumeration."""
    CUSCAR = "CUSCAR"  # Customs Cargo Report
    CUSRES = "CUSRES"  # Customs Response
    CUSDEC = "CUSDEC"  # Customs Declaration
    CUSREP = "CUSREP"  # Customs Report
    JOBMAN = "JOBMAN"  # Job Management
    JOBRES = "JOBRES"  # Job Response
    INVOIC = "INVOIC"  # Invoice
    PAXLST = "PAXLST"  # Passenger List
    CODECO = "CODECO"  # Container Discharge/Loading Order
    COPRAR = "COPRAR"  # Container Pre-Arrival Report


class EDIMessageStatus(str, Enum):
    """EDI message processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    PROCESSED = "processed"
    FAILED = "failed"
    REJECTED = "rejected"
    ACKNOWLEDGED = "acknowledged"
    ERROR = "error"


class EDIDirection(str, Enum):
    """EDI message direction enumeration."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class JobStatus(str, Enum):
    """Job status enumeration."""
    REGISTERED = "registered"
    IN_PROGRESS = "in_progress"
    PENDING_DOCUMENTS = "pending_documents"
    UNDER_EXAMINATION = "under_examination"
    CLEARED = "cleared"
    RELEASED = "released"
    CANCELLED = "cancelled"
    ON_HOLD = "on_hold"


class DeclarationType(str, Enum):
    """Declaration type enumeration."""
    IMPORT = "import"
    EXPORT = "export"
    TRANSIT = "transit"
    WAREHOUSE = "warehouse"
    TEMPORARY_IMPORT = "temporary_import"
    RE_EXPORT = "re_export"


class DeclarationStatus(str, Enum):
    """Declaration status enumeration."""
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_ASSESSMENT = "under_assessment"
    ASSESSED = "assessed"
    CLEARED = "cleared"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class EDIMessage(Base):
    """
    EDI Message model for storing all EDI communications.
    
    This model handles all types of EDI messages including job registration,
    customs declarations, and responses from ABF systems.
    """
    
    __tablename__ = "edi_messages"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Message identification
    message_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    message_type: Mapped[EDIMessageType] = mapped_column(String(20), nullable=False, index=True)
    direction: Mapped[EDIDirection] = mapped_column(String(10), nullable=False, index=True)
    
    # Message content
    raw_message: Mapped[str] = mapped_column(Text, nullable=False)
    parsed_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Processing information
    status: Mapped[EDIMessageStatus] = mapped_column(String(20), nullable=False, index=True, default=EDIMessageStatus.PENDING)
    processing_attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3, nullable=False)
    
    # Error handling
    error_code: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    error_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    
    # Business context
    customer_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey('customers.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    job_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('edi_jobs.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    declaration_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('customs_declarations.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # External references
    external_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    abf_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Timestamps
    received_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True
    )
    processed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Standard timestamps
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
    customer: Mapped[Optional["Customer"]] = relationship(
        "Customer",
        lazy="select"
    )
    
    job: Mapped[Optional["EDIJob"]] = relationship(
        "EDIJob",
        back_populates="messages",
        lazy="select"
    )
    
    declaration: Mapped[Optional["CustomsDeclaration"]] = relationship(
        "CustomsDeclaration",
        back_populates="edi_messages",
        lazy="select"
    )
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            f"message_type IN {tuple(mt.value for mt in EDIMessageType)}",
            name="ck_edi_messages_type"
        ),
        CheckConstraint(
            f"direction IN {tuple(d.value for d in EDIDirection)}",
            name="ck_edi_messages_direction"
        ),
        CheckConstraint(
            f"status IN {tuple(s.value for s in EDIMessageStatus)}",
            name="ck_edi_messages_status"
        ),
        CheckConstraint(
            "processing_attempts >= 0",
            name="ck_edi_messages_attempts"
        ),
        CheckConstraint(
            "max_attempts > 0",
            name="ck_edi_messages_max_attempts"
        ),
        
        # Composite indexes for performance
        Index("ix_edi_messages_type_status", "message_type", "status"),
        Index("ix_edi_messages_customer_type", "customer_id", "message_type"),
        Index("ix_edi_messages_received_status", "received_at", "status"),
        Index("ix_edi_messages_external_ref", "external_reference", "abf_reference"),
    )


class EDIJob(Base):
    """
    EDI Job model for tracking customs clearance jobs.
    
    This model represents a customs clearance job that may involve
    multiple EDI messages and declarations.
    """
    
    __tablename__ = "edi_jobs"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Job identification
    job_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    external_job_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    
    # Job details
    job_type: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # import, export, transit
    status: Mapped[JobStatus] = mapped_column(String(30), nullable=False, index=True, default=JobStatus.REGISTERED)
    priority: Mapped[str] = mapped_column(String(20), default='normal', nullable=False)  # low, normal, high, urgent
    
    # Customer and shipment information
    customer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('customers.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    shipment_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey('customer_shipments.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # Cargo details
    consignment_reference: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    vessel_voyage: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    port_of_loading: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    port_of_discharge: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Cargo description
    cargo_description: Mapped[str] = mapped_column(Text, nullable=False)
    total_packages: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_weight_kg: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    total_value_aud: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Dates
    estimated_arrival: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    actual_arrival: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    clearance_deadline: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Processing information
    assigned_to: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    processing_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Standard timestamps
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
    customer: Mapped["Customer"] = relationship(
        "Customer",
        lazy="select"
    )
    
    shipment: Mapped[Optional["CustomerShipment"]] = relationship(
        "CustomerShipment",
        lazy="select"
    )
    
    messages: Mapped[List["EDIMessage"]] = relationship(
        "EDIMessage",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    declarations: Mapped[List["CustomsDeclaration"]] = relationship(
        "CustomsDeclaration",
        back_populates="job",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            f"status IN {tuple(s.value for s in JobStatus)}",
            name="ck_edi_jobs_status"
        ),
        CheckConstraint(
            "priority IN ('low', 'normal', 'high', 'urgent')",
            name="ck_edi_jobs_priority"
        ),
        CheckConstraint(
            "total_packages IS NULL OR total_packages > 0",
            name="ck_edi_jobs_packages"
        ),
        
        # Composite indexes
        Index("ix_edi_jobs_customer_status", "customer_id", "status"),
        Index("ix_edi_jobs_arrival_deadline", "estimated_arrival", "clearance_deadline"),
        Index("ix_edi_jobs_type_priority", "job_type", "priority"),
    )


class CustomsDeclaration(Base):
    """
    Customs Declaration model for import/export declarations.
    
    This model represents formal customs declarations submitted to ABF.
    """
    
    __tablename__ = "customs_declarations"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Declaration identification
    declaration_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    declaration_type: Mapped[DeclarationType] = mapped_column(String(30), nullable=False, index=True)
    status: Mapped[DeclarationStatus] = mapped_column(String(30), nullable=False, index=True, default=DeclarationStatus.DRAFT)
    
    # Business references
    job_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('edi_jobs.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    customer_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('customers.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Declaration details
    consignment_reference: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    commercial_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Parties
    importer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    importer_abn: Mapped[Optional[str]] = mapped_column(String(11), nullable=True, index=True)
    exporter_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    exporter_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Transport details
    vessel_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    voyage_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    port_of_loading: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    port_of_discharge: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Financial information
    total_invoice_value: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='AUD', nullable=False)
    exchange_rate: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Duty and tax calculations
    total_duty: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    total_gst: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    total_charges: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Processing information
    submitted_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    assessed_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Dates
    submitted_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True
    )
    assessed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    cleared_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    
    # Additional data
    declaration_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)
    processing_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Standard timestamps
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
    job: Mapped["EDIJob"] = relationship(
        "EDIJob",
        back_populates="declarations",
        lazy="select"
    )
    
    customer: Mapped["Customer"] = relationship(
        "Customer",
        lazy="select"
    )
    
    edi_messages: Mapped[List["EDIMessage"]] = relationship(
        "EDIMessage",
        back_populates="declaration",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    declaration_items: Mapped[List["DeclarationItem"]] = relationship(
        "DeclarationItem",
        back_populates="declaration",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Table constraints
    __table_args__ = (
        CheckConstraint(
            f"declaration_type IN {tuple(dt.value for dt in DeclarationType)}",
            name="ck_declarations_type"
        ),
        CheckConstraint(
            f"status IN {tuple(s.value for s in DeclarationStatus)}",
            name="ck_declarations_status"
        ),
        CheckConstraint(
            "currency IN ('AUD', 'USD', 'EUR', 'GBP', 'JPY', 'CNY', 'NZD')",
            name="ck_declarations_currency"
        ),
        
        # Composite indexes
        Index("ix_declarations_customer_type", "customer_id", "declaration_type"),
        Index("ix_declarations_job_status", "job_id", "status"),
        Index("ix_declarations_submitted_status", "submitted_at", "status"),
    )


class DeclarationItem(Base):
    """
    Declaration Item model for individual items within a customs declaration.
    
    This model represents individual line items in a customs declaration.
    """
    
    __tablename__ = "declaration_items"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # References
    declaration_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('customs_declarations.id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Item identification
    item_number: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # Product details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    hs_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    country_of_origin: Mapped[str] = mapped_column(String(3), nullable=False)  # ISO country code
    
    # Quantities
    quantity: Mapped[str] = mapped_column(String(20), nullable=False)
    unit_of_measure: Mapped[str] = mapped_column(String(10), nullable=False)
    net_weight_kg: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    gross_weight_kg: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Financial details
    unit_price: Mapped[str] = mapped_column(String(20), nullable=False)
    total_value: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default='AUD', nullable=False)
    
    # Duty and tax
    duty_rate: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    duty_amount: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    gst_amount: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Additional information
    brand: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    serial_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Processing status
    is_examined: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    examination_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Standard timestamps
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
    declaration: Mapped["CustomsDeclaration"] = relationship(
        "CustomsDeclaration",
        back_populates="declaration_items",
        lazy="select"
    )
    
    # Table constraints
    __table_args__ = (
        # Unique constraint for item number within declaration
        UniqueConstraint('declaration_id', 'item_number', name='uq_declaration_item_number'),
        
        CheckConstraint(
            "item_number > 0",
            name="ck_declaration_items_number"
        ),
        CheckConstraint(
            "currency IN ('AUD', 'USD', 'EUR', 'GBP', 'JPY', 'CNY', 'NZD')",
            name="ck_declaration_items_currency"
        ),
        
        # Indexes
        Index("ix_declaration_items_country", "country_of_origin"),
    )