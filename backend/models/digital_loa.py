from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from enum import Enum

# Import the shared Base from database.py to ensure all models use the same metadata
from database import Base

class LOAStatus(str, Enum):
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    SIGNED = "signed"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"

class SignatureMethod(str, Enum):
    DIGITAL_CERTIFICATE = "digital_certificate"
    ELECTRONIC_SIGNATURE = "electronic_signature"
    BIOMETRIC = "biometric"
    TWO_FACTOR = "two_factor"

class DigitalLetterOfAuthority(Base):
    __tablename__ = "digital_letters_of_authority"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    
    # LOA Identification
    loa_number = Column(String(50), unique=True, nullable=False, index=True)
    reference_number = Column(String(100), nullable=True)  # Customer's internal reference
    
    # Company Information
    company_name = Column(String(255), nullable=False)
    company_abn = Column(String(11), nullable=False)
    company_address = Column(Text, nullable=False)
    
    # Authorized Person Details
    authorized_person_name = Column(String(255), nullable=False)
    authorized_person_title = Column(String(100), nullable=False)
    authorized_person_email = Column(String(255), nullable=False)
    authorized_person_phone = Column(String(20), nullable=True)
    
    # Authority Scope
    authority_scope = Column(Text, nullable=False)  # What the broker is authorized to do
    customs_broker_license = Column(String(50), nullable=False)  # Broker's license number
    
    # LOA Content and Legal Text
    loa_content = Column(Text, nullable=False)  # The full LOA text
    terms_and_conditions = Column(Text, nullable=True)
    special_instructions = Column(Text, nullable=True)
    
    # Digital Signature Information
    signature_method = Column(String(30), nullable=False, default=SignatureMethod.ELECTRONIC_SIGNATURE)
    signature_data = Column(Text, nullable=True)  # Base64 encoded signature image or certificate
    signature_certificate = Column(Text, nullable=True)  # Digital certificate data
    signature_timestamp = Column(DateTime(timezone=True), nullable=True)
    signature_ip_address = Column(String(45), nullable=True)
    signature_user_agent = Column(Text, nullable=True)
    
    # Verification and Security
    document_hash = Column(String(256), nullable=True)  # SHA-256 hash of the signed document
    verification_code = Column(String(50), nullable=True)  # Unique verification code
    blockchain_hash = Column(String(256), nullable=True)  # Optional blockchain verification
    
    # Status and Lifecycle
    status = Column(String(20), nullable=False, default=LOAStatus.DRAFT)
    is_active = Column(Boolean, default=False)
    
    # Important Dates
    effective_date = Column(DateTime(timezone=True), nullable=True)
    expiry_date = Column(DateTime(timezone=True), nullable=True)
    signed_at = Column(DateTime(timezone=True), nullable=True)
    activated_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    
    # Revocation Information
    revocation_reason = Column(Text, nullable=True)
    revoked_by = Column(String(255), nullable=True)
    
    # File Storage
    pdf_file_path = Column(String(500), nullable=True)  # Path to generated PDF
    original_file_path = Column(String(500), nullable=True)  # Path to original uploaded file
    signed_pdf_path = Column(String(500), nullable=True)  # Path to signed PDF
    
    # Additional Data
    additional_data = Column(JSON, nullable=True)  # Additional metadata as JSON
    
    # Audit Trail
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="digital_loas")
    audit_logs = relationship("LOAAuditLog", back_populates="loa", cascade="all, delete-orphan")
    signatures = relationship("LOASignature", back_populates="loa", cascade="all, delete-orphan")

class LOASignature(Base):
    __tablename__ = "loa_signatures"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    loa_id = Column(Integer, ForeignKey('digital_letters_of_authority.id', ondelete='CASCADE'), nullable=False)
    
    # Signatory Information
    signatory_name = Column(String(255), nullable=False)
    signatory_email = Column(String(255), nullable=False)
    signatory_role = Column(String(100), nullable=False)  # e.g., "Company Director", "Authorized Representative"
    
    # Signature Details
    signature_method = Column(String(30), nullable=False)
    signature_data = Column(Text, nullable=False)  # Base64 encoded signature or certificate
    signature_coordinates = Column(String(100), nullable=True)  # X,Y coordinates on PDF
    
    # Verification
    certificate_serial = Column(String(100), nullable=True)
    certificate_issuer = Column(String(255), nullable=True)
    certificate_subject = Column(String(255), nullable=True)
    certificate_valid_from = Column(DateTime(timezone=True), nullable=True)
    certificate_valid_to = Column(DateTime(timezone=True), nullable=True)
    
    # Security and Audit
    signature_hash = Column(String(256), nullable=False)  # Hash of the signature data
    timestamp_server = Column(String(255), nullable=True)  # Timestamp authority
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Status
    is_valid = Column(Boolean, default=True)
    verification_status = Column(String(20), default='pending')  # pending, verified, invalid
    
    # Timestamps
    signed_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    loa = relationship("DigitalLetterOfAuthority", back_populates="signatures")

class LOAAuditLog(Base):
    __tablename__ = "loa_audit_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    loa_id = Column(Integer, ForeignKey('digital_letters_of_authority.id', ondelete='CASCADE'), nullable=False)
    
    # Action Details
    action = Column(String(50), nullable=False)  # created, updated, signed, activated, revoked, etc.
    actor_type = Column(String(20), nullable=False)  # customer, admin, system
    actor_id = Column(String(100), nullable=True)  # ID of the person/system performing action
    actor_name = Column(String(255), nullable=True)
    
    # Change Details
    field_changed = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    
    # Context
    description = Column(Text, nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    
    # Additional Data
    additional_data = Column(JSON, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    loa = relationship("DigitalLetterOfAuthority", back_populates="audit_logs")

class LOATemplate(Base):
    __tablename__ = "loa_templates"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Template Information
    template_name = Column(String(255), nullable=False)
    template_code = Column(String(50), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Template Content
    template_content = Column(Text, nullable=False)  # HTML/text template with placeholders
    legal_text = Column(Text, nullable=False)  # Standard legal text
    terms_conditions = Column(Text, nullable=True)
    
    # Template Configuration
    required_fields = Column(JSON, nullable=False)  # List of required fields
    optional_fields = Column(JSON, nullable=True)  # List of optional fields
    validation_rules = Column(JSON, nullable=True)  # Validation rules for fields
    
    # Template Settings
    is_active = Column(Boolean, default=True)
    is_default = Column(Boolean, default=False)
    version = Column(String(10), default='1.0')
    
    # Metadata
    created_by = Column(String(255), nullable=True)
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())