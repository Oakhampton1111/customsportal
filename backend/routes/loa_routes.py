from fastapi import APIRouter, Depends, HTTPException, status, Request, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
import math

from database import get_async_session
from .customer_auth import get_current_customer
from services.loa_service import LOAService, LOATemplateService
from schemas.loa_schemas import (
    LOACreateRequest, LOAUpdateRequest, LOASignRequest, LOAVerificationRequest,
    LOARevokeRequest, LOAResponse, LOADetailResponse, LOAListResponse, LOAVerificationResponse,
    LOAStatsResponse, LOATemplateResponse, LOAPaginatedResponse,
    LOAErrorResponse, LOASuccessResponse
)
from models.customer import Customer
from models.digital_loa import DigitalLetterOfAuthority

router = APIRouter(prefix="/api/loa", tags=["Digital Letter of Authority"])

# Initialize services
loa_service = LOAService()
template_service = LOATemplateService()

@router.post("/create", response_model=LOAResponse)
async def create_loa(
    request: LOACreateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_customer: Customer = Depends(get_current_customer)
):
    """
    Create a new Digital Letter of Authority.
    
    Creates a new LOA in draft status. The LOA can be edited until it's signed.
    """
    try:
        # If no custom LOA content provided, use default template
        if not request.loa_content:
            template = await template_service.get_default_template(db)
            if template:
                # Replace placeholders in template
                loa_content = template.template_content.format(
                    company_name=request.company_name,
                    company_abn=request.company_abn,
                    authorized_person_name=request.authorized_person_name,
                    authorized_person_title=request.authorized_person_title,
                    authorized_person_email=request.authorized_person_email,
                    customs_broker_license=request.customs_broker_license
                )
                request.loa_content = loa_content
            else:
                # Use default content from service
                default_content = template_service.get_default_loa_content()
                request.loa_content = default_content.format(
                    company_name=request.company_name,
                    company_abn=request.company_abn,
                    authorized_person_name=request.authorized_person_name,
                    authorized_person_title=request.authorized_person_title,
                    authorized_person_email=request.authorized_person_email,
                    customs_broker_license=request.customs_broker_license
                )
        
        loa = await loa_service.create_loa(
            db=db,
            customer_id=current_customer.id,
            loa_data=request.dict()
        )
        
        return LOAResponse.model_validate(loa)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create LOA: {str(e)}"
        )

@router.get("/list", response_model=LOAPaginatedResponse)
async def list_customer_loas(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    status_filter: Optional[str] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_async_session),
    current_customer: Customer = Depends(get_current_customer)
):
    """
    List customer's Digital Letters of Authority with pagination.
    """
    try:
        offset = (page - 1) * size
        
        loas = await loa_service.get_customer_loas(
            db=db,
            customer_id=current_customer.id,
            status=status_filter,
            limit=size,
            offset=offset
        )
        
        # Get total count for pagination
        total_loas = await loa_service.get_customer_loas(
            db=db,
            customer_id=current_customer.id,
            status=status_filter,
            limit=1000,  # Large number to get all
            offset=0
        )
        total = len(total_loas)
        pages = math.ceil(total / size)
        
        return LOAPaginatedResponse(
            items=[LOAListResponse.model_validate(loa) for loa in loas],
            total=total,
            page=page,
            size=size,
            pages=pages
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve LOAs: {str(e)}"
        )

@router.get("/templates", response_model=List[LOATemplateResponse])
async def get_templates(
    db: AsyncSession = Depends(get_async_session),
    current_customer: Customer = Depends(get_current_customer)
):
    """
    Get all available LOA templates.
    """
    templates = await template_service.get_all_templates(db)
    
    if not templates:
        # Return a basic template structure
        return [{
            "id": 0,
            "template_name": "Default LOA Template",
            "template_code": "default",
            "description": "Standard Letter of Authority template",
            "template_content": template_service.get_default_loa_content(),
            "legal_text": "This Letter of Authority is governed by Australian customs law.",
            "terms_conditions": None,
            "required_fields": [
                "company_name", "company_abn", "authorized_person_name",
                "authorized_person_title", "authorized_person_email",
                "customs_broker_license", "authority_scope"
            ],
            "optional_fields": ["reference_number", "authorized_person_phone"],
            "is_active": True,
            "is_default": True,
            "version": "1.0",
            "created_at": "2024-01-01T00:00:00Z"
        }]
    
    return [LOATemplateResponse.model_validate(template) for template in templates]

@router.get("/{loa_id}", response_model=LOAResponse)
async def get_loa(
    loa_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_customer: Customer = Depends(get_current_customer)
):
    """
    Get a specific Digital Letter of Authority by ID.
    """
    loa = await loa_service.get_loa_by_id(db, loa_id, current_customer.id)
    
    if not loa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LOA not found"
        )
    
    return LOAResponse.model_validate(loa)

@router.put("/{loa_id}", response_model=LOAResponse)
async def update_loa(
    loa_id: int,
    request: LOAUpdateRequest,
    db: AsyncSession = Depends(get_async_session),
    current_customer: Customer = Depends(get_current_customer)
):
    """
    Update a Digital Letter of Authority (only if in draft status).
    """
    try:
        # Filter out None values
        update_data = {k: v for k, v in request.dict().items() if v is not None}
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No update data provided"
            )
        
        loa = await loa_service.update_loa(
            db=db,
            loa_id=loa_id,
            customer_id=current_customer.id,
            update_data=update_data,
            actor_name=f"{current_customer.first_name} {current_customer.last_name}"
        )
        
        if not loa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LOA not found or cannot be updated (not in draft status)"
            )
        
        return LOAResponse.model_validate(loa)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update LOA: {str(e)}"
        )

@router.post("/{loa_id}/sign", response_model=LOAResponse)
async def sign_loa(
    loa_id: int,
    request: LOASignRequest,
    http_request: Request,
    db: AsyncSession = Depends(get_async_session),
    current_customer: Customer = Depends(get_current_customer)
):
    """
    Digitally sign a Letter of Authority.
    
    This action is irreversible and moves the LOA to signed status.
    """
    try:
        # Get client IP and user agent for audit trail
        client_ip = http_request.client.host if http_request.client else None
        user_agent = http_request.headers.get("user-agent")
        
        loa = await loa_service.sign_loa(
            db=db,
            loa_id=loa_id,
            customer_id=current_customer.id,
            signature_data=request.dict(),
            ip_address=client_ip,
            user_agent=user_agent
        )
        
        if not loa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LOA not found or cannot be signed"
            )
        
        return LOAResponse.model_validate(loa)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to sign LOA: {str(e)}"
        )

@router.post("/{loa_id}/revoke", response_model=LOAResponse)
async def revoke_loa(
    loa_id: int,
    request: LOARevokeRequest,
    db: AsyncSession = Depends(get_async_session),
    current_customer: Customer = Depends(get_current_customer)
):
    """
    Revoke a Digital Letter of Authority.
    
    This action is irreversible and deactivates the LOA.
    """
    try:
        loa = await loa_service.revoke_loa(
            db=db,
            loa_id=loa_id,
            reason=request.reason,
            revoked_by=f"{current_customer.first_name} {current_customer.last_name}",
            actor_type="customer"
        )
        
        if not loa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LOA not found or cannot be revoked"
            )
        
        return LOAResponse.model_validate(loa)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to revoke LOA: {str(e)}"
        )

@router.get("/{loa_id}/download")
async def download_loa_pdf(
    loa_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_customer: Customer = Depends(get_current_customer)
):
    """
    Download the signed PDF of a Letter of Authority.
    """
    loa = await loa_service.get_loa_by_id(db, loa_id, current_customer.id)
    
    if not loa:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="LOA not found"
        )
    
    if not loa.signed_pdf_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Signed PDF not available"
        )
    
    try:
        return FileResponse(
            path=loa.signed_pdf_path,
            filename=f"LOA_{loa.loa_number}.pdf",
            media_type="application/pdf"
        )
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="PDF file not found"
        )

@router.post("/verify", response_model=LOAVerificationResponse)
async def verify_loa(
    request: LOAVerificationRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Verify the authenticity of a Digital Letter of Authority.
    
    This is a public endpoint that doesn't require authentication.
    """
    try:
        verification_result = await loa_service.verify_loa(
            db=db,
            loa_number=request.loa_number,
            verification_code=request.verification_code
        )
        
        return LOAVerificationResponse(**verification_result)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Verification failed: {str(e)}"
        )

@router.get("/stats/summary", response_model=LOAStatsResponse)
async def get_loa_stats(
    db: AsyncSession = Depends(get_async_session),
    current_customer: Customer = Depends(get_current_customer)
):
    """
    Get statistics summary for customer's LOAs.
    """
    try:
        # Get all LOAs for the customer
        all_loas = await loa_service.get_customer_loas(
            db=db,
            customer_id=current_customer.id,
            limit=1000,  # Large number to get all
            offset=0
        )
        
        # Calculate statistics
        total_loas = len(all_loas)
        draft_count = len([loa for loa in all_loas if loa.status == "draft"])
        signed_count = len([loa for loa in all_loas if loa.status == "signed"])
        active_count = len([loa for loa in all_loas if loa.status == "active"])
        revoked_count = len([loa for loa in all_loas if loa.status == "revoked"])
        expired_count = len([loa for loa in all_loas if loa.status == "expired"])
        
        return LOAStatsResponse(
            total_loas=total_loas,
            draft_count=draft_count,
            signed_count=signed_count,
            active_count=active_count,
            revoked_count=revoked_count,
            expired_count=expired_count
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get statistics: {str(e)}"
        )


# Admin endpoints (would require admin authentication in production)
@router.post("/{loa_id}/activate", response_model=LOAResponse)
async def activate_loa_admin(
    loa_id: int,
    db: AsyncSession = Depends(get_async_session),
    current_customer: Customer = Depends(get_current_customer)  # In production, use admin auth
):
    """
    Activate a signed LOA (Admin function).
    
    Note: In production, this should require admin authentication.
    """
    try:
        loa = await loa_service.activate_loa(
            db=db,
            loa_id=loa_id,
            admin_user=f"{current_customer.first_name} {current_customer.last_name}"
        )
        
        if not loa:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="LOA not found or cannot be activated"
            )
        
        return LOAResponse.model_validate(loa)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to activate LOA: {str(e)}"
        )

@router.get("/public/verify/{loa_number}")
async def public_verify_loa(
    loa_number: str,
    verification_code: str = Query(..., description="Verification code"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Public verification endpoint for LOA authenticity.
    
    This endpoint can be used by third parties to verify LOA authenticity.
    """
    try:
        verification_result = await loa_service.verify_loa(
            db=db,
            loa_number=loa_number,
            verification_code=verification_code
        )
        
        return verification_result
        
    except Exception as e:
        return {
            "valid": False,
            "error": f"Verification failed: {str(e)}"
        }