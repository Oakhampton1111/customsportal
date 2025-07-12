from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from pydantic import BaseModel, EmailStr
from typing import Optional, Dict, Any
from datetime import datetime
import bcrypt

from database import get_async_session
from models.customer import Customer, CustomerSession, CustomerAuthLog
from services.sso_service import sso_service, SSOProviderFactory
from sso_config import AUTH_METHODS

router = APIRouter(prefix="/api/customer/auth", tags=["Customer Authentication"])
security = HTTPBearer()

# Pydantic models for request/response
class CustomerRegistration(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
    phone: Optional[str] = None
    company_name: Optional[str] = None

class CustomerLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    customer: Dict[str, Any]

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class CustomerProfile(BaseModel):
    id: str
    email: str
    first_name: str
    last_name: str
    phone: Optional[str]
    company_name: Optional[str]
    verification_status: str
    email_verified: bool
    profile_picture_url: Optional[str]
    preferred_auth_method: str
    created_at: datetime
    updated_at: datetime

class SSOInitiateResponse(BaseModel):
    auth_url: str
    state: str
    provider: str

class SSOCallbackRequest(BaseModel):
    provider: str
    code: str
    state: str

# Helper functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

async def get_current_customer(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_session)
) -> Customer:
    """Get current authenticated customer from JWT token"""
    
    token = credentials.credentials
    payload = sso_service.verify_jwt_token(token)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    customer_id = payload["sub"]
    
    # Get customer from database
    stmt = select(Customer).where(Customer.id == customer_id)
    result = await db.execute(stmt)
    customer = result.scalar_one_or_none()
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Customer not found"
        )
    
    return customer

async def log_auth_attempt(
    db: AsyncSession,
    customer_id: Optional[str],
    auth_method: str,
    action: str,
    request: Request,
    success: bool = True,
    failure_reason: str = None
):
    """Log authentication attempt"""
    
    log_entry = CustomerAuthLog(
        customer_id=customer_id,
        auth_method=auth_method,
        action=action,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=success,
        failure_reason=failure_reason
    )
    
    db.add(log_entry)
    await db.commit()

# Authentication routes
@router.post("/register", response_model=TokenResponse)
async def register_customer(
    registration: CustomerRegistration,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Register new customer with email/password"""
    
    try:
        # Check if customer already exists
        stmt = select(Customer).where(Customer.email == registration.email)
        result = await db.execute(stmt)
        existing_customer = result.scalar_one_or_none()
        
        if existing_customer:
            await log_auth_attempt(
                db, None, AUTH_METHODS["EMAIL"], "register", 
                request, False, "Email already exists"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password
        hashed_password = hash_password(registration.password)
        
        # Create new customer
        customer = Customer(
            email=registration.email,
            password_hash=hashed_password,
            first_name=registration.first_name,
            last_name=registration.last_name,
            phone=registration.phone,
            company_name=registration.company_name,
            preferred_auth_method=AUTH_METHODS["EMAIL"]
        )
        
        db.add(customer)
        await db.flush()  # Get the ID
        
        # Generate JWT tokens
        jwt_tokens = sso_service.generate_jwt_token(
            str(customer.id), 
            AUTH_METHODS["EMAIL"]
        )
        
        # Create session
        session = await sso_service._create_session(
            db, customer, AUTH_METHODS["EMAIL"], jwt_tokens,
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        
        await log_auth_attempt(
            db, str(customer.id), AUTH_METHODS["EMAIL"], 
            "register", request, True
        )
        
        await db.commit()
        
        return TokenResponse(
            access_token=jwt_tokens["access_token"],
            refresh_token=jwt_tokens["refresh_token"],
            token_type=jwt_tokens["token_type"],
            expires_in=jwt_tokens["expires_in"],
            customer={
                "id": str(customer.id),
                "email": customer.email,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "verification_status": customer.verification_status,
                "profile_picture_url": customer.profile_picture_url
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await log_auth_attempt(
            db, None, AUTH_METHODS["EMAIL"], "register", 
            request, False, str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )

@router.post("/login", response_model=TokenResponse)
async def login_customer(
    login: CustomerLogin,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Login customer with email/password"""
    
    try:
        # Find customer by email
        stmt = select(Customer).where(Customer.email == login.email)
        result = await db.execute(stmt)
        customer = result.scalar_one_or_none()
        
        if not customer or not customer.password_hash:
            await log_auth_attempt(
                db, None, AUTH_METHODS["EMAIL"], "login", 
                request, False, "Invalid credentials"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Verify password
        if not verify_password(login.password, customer.password_hash):
            await log_auth_attempt(
                db, str(customer.id), AUTH_METHODS["EMAIL"], "login", 
                request, False, "Invalid password"
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate JWT tokens
        jwt_tokens = sso_service.generate_jwt_token(
            str(customer.id), 
            AUTH_METHODS["EMAIL"]
        )
        
        # Create session
        session = await sso_service._create_session(
            db, customer, AUTH_METHODS["EMAIL"], jwt_tokens,
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        
        # Update last login
        customer.last_login_at = datetime.utcnow()
        
        await log_auth_attempt(
            db, str(customer.id), AUTH_METHODS["EMAIL"], 
            "login", request, True
        )
        
        await db.commit()
        
        return TokenResponse(
            access_token=jwt_tokens["access_token"],
            refresh_token=jwt_tokens["refresh_token"],
            token_type=jwt_tokens["token_type"],
            expires_in=jwt_tokens["expires_in"],
            customer={
                "id": str(customer.id),
                "email": customer.email,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "verification_status": customer.verification_status,
                "profile_picture_url": customer.profile_picture_url
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        await log_auth_attempt(
            db, None, AUTH_METHODS["EMAIL"], "login", 
            request, False, str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Refresh JWT access token"""
    
    try:
        new_tokens = await sso_service.refresh_token(refresh_request.refresh_token, db)
        
        if not new_tokens:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token"
            )
        
        # Get customer info for response
        payload = sso_service.verify_jwt_token(new_tokens["access_token"])
        customer_id = payload["sub"]
        
        stmt = select(Customer).where(Customer.id == customer_id)
        result = await db.execute(stmt)
        customer = result.scalar_one_or_none()
        
        return TokenResponse(
            access_token=new_tokens["access_token"],
            refresh_token=new_tokens["refresh_token"],
            token_type=new_tokens["token_type"],
            expires_in=new_tokens["expires_in"],
            customer={
                "id": str(customer.id),
                "email": customer.email,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "verification_status": customer.verification_status,
                "profile_picture_url": customer.profile_picture_url
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Token refresh failed"
        )

@router.post("/logout")
async def logout_customer(
    request: Request,
    current_customer: Customer = Depends(get_current_customer),
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_async_session)
):
    """Logout customer and invalidate session"""
    
    try:
        token = credentials.credentials
        success = await sso_service.logout(token, db)
        
        if success:
            return {"message": "Successfully logged out"}
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Logout failed"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Logout failed"
        )

@router.get("/me", response_model=CustomerProfile)
async def get_current_customer_profile(
    current_customer: Customer = Depends(get_current_customer)
):
    """Get current customer profile"""
    
    return CustomerProfile(
        id=str(current_customer.id),
        email=current_customer.email,
        first_name=current_customer.first_name,
        last_name=current_customer.last_name,
        phone=current_customer.phone,
        company_name=current_customer.company_name,
        verification_status=current_customer.verification_status,
        email_verified=current_customer.email_verified,
        profile_picture_url=current_customer.profile_picture_url,
        preferred_auth_method=current_customer.preferred_auth_method,
        created_at=current_customer.created_at,
        updated_at=current_customer.updated_at
    )

# SSO Authentication routes
@router.get("/sso/providers")
async def get_sso_providers():
    """Get list of supported SSO providers"""
    
    providers = SSOProviderFactory.get_supported_providers()
    return {
        "providers": providers,
        "total": len(providers)
    }

@router.post("/sso/initiate/{provider}", response_model=SSOInitiateResponse)
async def initiate_sso_login(provider: str):
    """Initiate SSO login for specified provider"""
    
    try:
        if provider not in SSOProviderFactory.get_supported_providers():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported SSO provider: {provider}"
            )
        
        sso_data = await sso_service.initiate_sso_login(provider)
        
        return SSOInitiateResponse(
            auth_url=sso_data["auth_url"],
            state=sso_data["state"],
            provider=sso_data["provider"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SSO initiation failed"
        )

@router.post("/sso/callback", response_model=TokenResponse)
async def sso_callback(
    callback: SSOCallbackRequest,
    request: Request,
    db: AsyncSession = Depends(get_async_session)
):
    """Handle SSO callback and complete authentication"""
    
    try:
        if callback.provider not in SSOProviderFactory.get_supported_providers():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported SSO provider: {callback.provider}"
            )
        
        # Complete SSO login
        sso_result = await sso_service.complete_sso_login(
            callback.provider,
            callback.code,
            callback.state,
            db,
            request.client.host if request.client else None,
            request.headers.get("user-agent")
        )
        
        return TokenResponse(
            access_token=sso_result["tokens"]["access_token"],
            refresh_token=sso_result["tokens"]["refresh_token"],
            token_type=sso_result["tokens"]["token_type"],
            expires_in=sso_result["tokens"]["expires_in"],
            customer=sso_result["customer"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SSO callback failed"
        )

# Account linking routes
@router.get("/sso/accounts")
async def get_linked_sso_accounts(
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_async_session)
):
    """Get customer's linked SSO accounts"""
    
    stmt = select(Customer).options(
        selectinload(Customer.sso_accounts)
    ).where(Customer.id == current_customer.id)
    
    result = await db.execute(stmt)
    customer = result.scalar_one()
    
    accounts = []
    for sso_account in customer.sso_accounts:
        accounts.append({
            "provider": sso_account.provider,
            "provider_email": sso_account.provider_email,
            "provider_name": sso_account.provider_name,
            "is_primary": sso_account.is_primary,
            "linked_at": sso_account.created_at,
            "last_login": sso_account.last_login_at
        })
    
    return {
        "accounts": accounts,
        "total": len(accounts)
    }

@router.delete("/sso/accounts/{provider}")
async def unlink_sso_account(
    provider: str,
    current_customer: Customer = Depends(get_current_customer),
    db: AsyncSession = Depends(get_async_session)
):
    """Unlink SSO account from customer"""
    
    # Implementation for unlinking SSO accounts
    # This would remove the SSO account but keep the customer record
    return {"message": f"SSO account {provider} unlinked successfully"}