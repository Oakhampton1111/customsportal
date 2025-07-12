from sqlalchemy import Column, String, Boolean, Integer, DateTime, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

# Import the shared Base from database.py to ensure all models use the same metadata
from database import Base

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # NULL for SSO-only accounts
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    phone = Column(String(20), nullable=True)
    company_name = Column(String(255), nullable=True)
    abn = Column(String(11), nullable=True)
    address_line1 = Column(String(255), nullable=True)
    address_line2 = Column(String(255), nullable=True)
    city = Column(String(100), nullable=True)
    state = Column(String(50), nullable=True)
    postcode = Column(String(10), nullable=True)
    country = Column(String(100), default='Australia')
    verification_status = Column(String(20), default='pending')  # pending, in_review, verified, rejected
    verification_points = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    email_verified = Column(Boolean, default=False)
    profile_picture_url = Column(String(500), nullable=True)  # From SSO providers
    preferred_auth_method = Column(String(20), default='email')  # email, google, microsoft, linkedin, facebook
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    sso_accounts = relationship("CustomerSSOAccount", back_populates="customer", cascade="all, delete-orphan")
    sessions = relationship("CustomerSession", back_populates="customer", cascade="all, delete-orphan")
    auth_logs = relationship("CustomerAuthLog", back_populates="customer", cascade="all, delete-orphan")
    verification = relationship("CustomerVerification", back_populates="customer", uselist=False, cascade="all, delete-orphan")
    shipments = relationship("CustomerShipment", back_populates="customer", cascade="all, delete-orphan")
    digital_authorities = relationship("CustomerDigitalAuthority", back_populates="customer", cascade="all, delete-orphan")
    digital_loas = relationship("DigitalLetterOfAuthority", back_populates="customer", cascade="all, delete-orphan")

class CustomerSSOAccount(Base):
    __tablename__ = "customer_sso_accounts"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    provider = Column(String(20), nullable=False)  # google, microsoft, linkedin, facebook
    provider_user_id = Column(String(255), nullable=False)  # Provider's unique user ID
    provider_email = Column(String(255), nullable=False)
    provider_name = Column(String(255), nullable=True)
    provider_picture_url = Column(String(500), nullable=True)
    access_token_hash = Column(String(255), nullable=True)  # Encrypted storage
    refresh_token_hash = Column(String(255), nullable=True)  # Encrypted storage
    token_expires_at = Column(DateTime(timezone=True), nullable=True)
    is_primary = Column(Boolean, default=False)  # Primary SSO account for this customer
    is_active = Column(Boolean, default=True)
    last_login_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="sso_accounts")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('provider', 'provider_user_id', name='uq_provider_user'),
    )

class CustomerSession(Base):
    __tablename__ = "customer_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    session_token = Column(String(255), unique=True, nullable=False, index=True)
    refresh_token = Column(String(255), unique=True, nullable=False, index=True)
    auth_method = Column(String(20), nullable=False)  # email, google, microsoft, linkedin, facebook
    ip_address = Column(String(45), nullable=True)  # Support IPv6
    user_agent = Column(Text, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True)
    last_activity_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="sessions")

class CustomerAuthLog(Base):
    __tablename__ = "customer_auth_logs"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=True)
    auth_method = Column(String(20), nullable=False)
    action = Column(String(20), nullable=False)  # login, logout, token_refresh, failed_login
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    success = Column(Boolean, nullable=False)
    failure_reason = Column(String(255), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="auth_logs")

class CustomerVerification(Base):
    __tablename__ = "customer_verification"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False, unique=True)
    verification_type = Column(String(20), default='100_point_check')
    status = Column(String(20), default='pending')  # pending, in_review, verified, rejected
    points_achieved = Column(Integer, default=0)
    points_required = Column(Integer, default=100)
    submitted_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(String(255), nullable=True)  # Admin user who reviewed
    rejection_reason = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="verification")
    documents = relationship("CustomerVerificationDocument", back_populates="verification", cascade="all, delete-orphan")

class CustomerVerificationDocument(Base):
    __tablename__ = "customer_verification_documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    verification_id = Column(Integer, ForeignKey('customer_verification.id', ondelete='CASCADE'), nullable=False)
    document_type = Column(String(50), nullable=False)  # passport, drivers_license, birth_certificate, etc.
    document_category = Column(String(20), nullable=False)  # primary, secondary, address_proof
    points_value = Column(Integer, nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    is_verified = Column(Boolean, default=False)
    verification_notes = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    verified_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    verification = relationship("CustomerVerification", back_populates="documents")

class CustomerShipment(Base):
    __tablename__ = "customer_shipments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    shipment_reference = Column(String(100), unique=True, nullable=False, index=True)
    consignment_number = Column(String(100), nullable=True)
    status = Column(String(30), default='pending')  # pending, in_transit, customs_clearance, cleared, delivered
    origin_country = Column(String(100), nullable=False)
    destination_country = Column(String(100), default='Australia')
    description = Column(Text, nullable=False)
    value_aud = Column(String(20), nullable=False)  # Store as string to avoid decimal issues
    weight_kg = Column(String(10), nullable=True)
    dimensions = Column(String(100), nullable=True)  # LxWxH format
    hs_code = Column(String(20), nullable=True)
    duty_rate = Column(String(10), nullable=True)
    gst_amount = Column(String(20), nullable=True)
    duty_amount = Column(String(20), nullable=True)
    total_charges = Column(String(20), nullable=True)
    estimated_delivery = Column(DateTime(timezone=True), nullable=True)
    actual_delivery = Column(DateTime(timezone=True), nullable=True)
    tracking_url = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="shipments")

class CustomerDigitalAuthority(Base):
    __tablename__ = "customer_digital_authorities"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_id = Column(Integer, ForeignKey('customers.id', ondelete='CASCADE'), nullable=False)
    authority_type = Column(String(50), nullable=False)  # customs_clearance, import_permit, etc.
    authority_number = Column(String(100), unique=True, nullable=False, index=True)
    status = Column(String(20), default='pending')  # pending, active, suspended, revoked, expired
    scope = Column(Text, nullable=True)  # Description of what this authority covers
    issued_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    revocation_reason = Column(Text, nullable=True)
    digital_signature = Column(Text, nullable=True)  # Digital signature/certificate
    certificate_path = Column(String(500), nullable=True)  # Path to certificate file
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer", back_populates="digital_authorities")