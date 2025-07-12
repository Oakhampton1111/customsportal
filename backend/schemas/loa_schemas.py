from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class LOAStatusEnum(str, Enum):
    DRAFT = "draft"
    PENDING_SIGNATURE = "pending_signature"
    SIGNED = "signed"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    REVOKED = "revoked"
    EXPIRED = "expired"

class SignatureMethodEnum(str, Enum):
    DIGITAL_CERTIFICATE = "digital_certificate"
    ELECTRONIC_SIGNATURE = "electronic_signature"
    BIOMETRIC = "biometric"
    TWO_FACTOR = "two_factor"

# Request Schemas
class LOACreateRequest(BaseModel):
    reference_number: Optional[str] = Field(None, max_length=100, description="Customer's internal reference")
    company_name: str = Field(..., max_length=255, description="Company name")
    company_abn: str = Field(..., min_length=11, max_length=11, description="Australian Business Number")
    company_address: str = Field(..., description="Company address")
    authorized_person_name: str = Field(..., max_length=255, description="Name of authorized person")
    authorized_person_title: str = Field(..., max_length=100, description="Title of authorized person")
    authorized_person_email: EmailStr = Field(..., description="Email of authorized person")
    authorized_person_phone: Optional[str] = Field(None, max_length=20, description="Phone of authorized person")
    authority_scope: str = Field(..., description="Scope of authority granted")
    customs_broker_license: str = Field(..., max_length=50, description="Customs broker license number")
    loa_content: Optional[str] = Field(None, description="Custom LOA content (uses template if not provided)")
    terms_and_conditions: Optional[str] = Field(None, description="Additional terms and conditions")
    special_instructions: Optional[str] = Field(None, description="Special instructions")
    signature_method: SignatureMethodEnum = Field(SignatureMethodEnum.ELECTRONIC_SIGNATURE, description="Signature method")
    effective_date: Optional[datetime] = Field(None, description="Effective date of the LOA")
    expiry_date: Optional[datetime] = Field(None, description="Expiry date of the LOA")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    @validator('company_abn')
    def validate_abn(cls, v):
        if not v.isdigit():
            raise ValueError('ABN must contain only digits')
        return v

    @validator('expiry_date')
    def validate_expiry_date(cls, v, values):
        if v and 'effective_date' in values and values['effective_date']:
            if v <= values['effective_date']:
                raise ValueError('Expiry date must be after effective date')
        return v

class LOAUpdateRequest(BaseModel):
    reference_number: Optional[str] = Field(None, max_length=100)
    company_name: Optional[str] = Field(None, max_length=255)
    company_abn: Optional[str] = Field(None, min_length=11, max_length=11)
    company_address: Optional[str] = Field(None)
    authorized_person_name: Optional[str] = Field(None, max_length=255)
    authorized_person_title: Optional[str] = Field(None, max_length=100)
    authorized_person_email: Optional[EmailStr] = Field(None)
    authorized_person_phone: Optional[str] = Field(None, max_length=20)
    authority_scope: Optional[str] = Field(None)
    customs_broker_license: Optional[str] = Field(None, max_length=50)
    loa_content: Optional[str] = Field(None)
    terms_and_conditions: Optional[str] = Field(None)
    special_instructions: Optional[str] = Field(None)
    effective_date: Optional[datetime] = Field(None)
    expiry_date: Optional[datetime] = Field(None)
    metadata: Optional[Dict[str, Any]] = Field(None)

    @validator('company_abn')
    def validate_abn(cls, v):
        if v and not v.isdigit():
            raise ValueError('ABN must contain only digits')
        return v

class LOASignRequest(BaseModel):
    signature_method: Optional[SignatureMethodEnum] = Field(SignatureMethodEnum.ELECTRONIC_SIGNATURE)
    signature_data: Optional[str] = Field(None, description="Custom signature data (base64 encoded)")
    confirm_authority: bool = Field(..., description="Confirmation that signatory has authority to sign")
    
    @validator('confirm_authority')
    def validate_authority(cls, v):
        if not v:
            raise ValueError('Must confirm authority to sign')
        return v

class LOAVerificationRequest(BaseModel):
    loa_number: str = Field(..., description="LOA number to verify")
    verification_code: str = Field(..., description="Verification code")

class LOARevokeRequest(BaseModel):
    reason: str = Field(..., min_length=10, description="Reason for revocation")

# Response Schemas
class LOASignatureResponse(BaseModel):
    id: int
    signatory_name: str
    signatory_email: str
    signatory_role: str
    signature_method: str
    signed_at: datetime
    verification_status: str
    certificate_serial: Optional[str]
    certificate_issuer: Optional[str]
    is_valid: bool

    class Config:
        from_attributes = True

class LOAAuditLogResponse(BaseModel):
    id: int
    action: str
    actor_type: str
    actor_name: Optional[str]
    description: str
    field_changed: Optional[str]
    old_value: Optional[str]
    new_value: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class LOAResponse(BaseModel):
    id: int
    loa_number: str
    reference_number: Optional[str]
    company_name: str
    company_abn: str
    company_address: str
    authorized_person_name: str
    authorized_person_title: str
    authorized_person_email: str
    authorized_person_phone: Optional[str]
    authority_scope: str
    customs_broker_license: str
    signature_method: str
    status: LOAStatusEnum
    is_active: bool
    verification_code: Optional[str]
    effective_date: Optional[datetime]
    expiry_date: Optional[datetime]
    signed_at: Optional[datetime]
    activated_at: Optional[datetime]
    revoked_at: Optional[datetime]
    revocation_reason: Optional[str]
    revoked_by: Optional[str]
    pdf_file_path: Optional[str]
    signed_pdf_path: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class LOADetailResponse(BaseModel):
    id: int
    loa_number: str
    reference_number: Optional[str]
    company_name: str
    company_abn: str
    company_address: str
    authorized_person_name: str
    authorized_person_title: str
    authorized_person_email: str
    authorized_person_phone: Optional[str]
    authority_scope: str
    customs_broker_license: str
    signature_method: str
    status: LOAStatusEnum
    is_active: bool
    verification_code: Optional[str]
    effective_date: Optional[datetime]
    expiry_date: Optional[datetime]
    signed_at: Optional[datetime]
    activated_at: Optional[datetime]
    revoked_at: Optional[datetime]
    revocation_reason: Optional[str]
    revoked_by: Optional[str]
    pdf_file_path: Optional[str]
    signed_pdf_path: Optional[str]
    created_at: datetime
    updated_at: datetime
    signatures: List[LOASignatureResponse] = []
    audit_logs: List[LOAAuditLogResponse] = []

    class Config:
        from_attributes = True

class LOAListResponse(BaseModel):
    id: int
    loa_number: str
    reference_number: Optional[str]
    company_name: str
    authorized_person_name: str
    status: LOAStatusEnum
    is_active: bool
    effective_date: Optional[datetime]
    expiry_date: Optional[datetime]
    signed_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True

class LOAVerificationResponse(BaseModel):
    valid: bool
    error: Optional[str] = None
    loa_number: Optional[str] = None
    company_name: Optional[str] = None
    company_abn: Optional[str] = None
    authorized_person: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    signed_at: Optional[str] = None
    effective_date: Optional[str] = None
    expiry_date: Optional[str] = None
    signature_valid: Optional[bool] = None
    revoked: Optional[bool] = None
    revocation_reason: Optional[str] = None

class LOAStatsResponse(BaseModel):
    total_loas: int
    draft_count: int
    signed_count: int
    active_count: int
    revoked_count: int
    expired_count: int

# Template Schemas
class LOATemplateResponse(BaseModel):
    id: int
    template_name: str
    template_code: str
    description: Optional[str]
    template_content: str
    legal_text: str
    terms_conditions: Optional[str]
    required_fields: List[str]
    optional_fields: Optional[List[str]]
    is_active: bool
    is_default: bool
    version: str
    created_at: datetime

    class Config:
        from_attributes = True

# Pagination
class LOAPaginatedResponse(BaseModel):
    items: List[LOAListResponse]
    total: int
    page: int
    size: int
    pages: int

# Error Schemas
class LOAErrorResponse(BaseModel):
    error: str
    message: str
    details: Optional[Dict[str, Any]] = None

# Success Schemas
class LOASuccessResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None