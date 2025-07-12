import asyncio
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from urllib.parse import urlencode
import httpx
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from models.customer import (
    Customer, CustomerSSOAccount, CustomerSession, CustomerAuthLog
)
from sso_config import sso_config, OAUTH_URLS, AUTH_METHODS
import jwt

class SSOProviderBase:
    """Base class for SSO providers"""
    
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.config = sso_config
        self.oauth_config = OAUTH_URLS[provider_name]
        
    def generate_state(self) -> str:
        """Generate secure state parameter for OAuth"""
        return secrets.token_urlsafe(32)
    
    def get_auth_url(self, state: str) -> str:
        """Generate OAuth authorization URL"""
        raise NotImplementedError
    
    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        """Exchange authorization code for access token"""
        raise NotImplementedError
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        """Get user information from provider"""
        raise NotImplementedError

class GoogleSSOProvider(SSOProviderBase):
    """Google OAuth 2.0 provider"""
    
    def __init__(self):
        super().__init__("google")
    
    def get_auth_url(self, state: str) -> str:
        params = {
            "client_id": self.config.GOOGLE_CLIENT_ID,
            "redirect_uri": self.config.GOOGLE_REDIRECT_URI,
            "scope": self.oauth_config["scope"],
            "response_type": "code",
            "state": state,
            "access_type": "offline",
            "prompt": "consent"
        }
        return f"{self.oauth_config['auth_url']}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            data = {
                "client_id": self.config.GOOGLE_CLIENT_ID,
                "client_secret": self.config.GOOGLE_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.config.GOOGLE_REDIRECT_URI
            }
            
            response = await client.post(self.oauth_config["token_url"], data=data)
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(self.oauth_config["userinfo_url"], headers=headers)
            response.raise_for_status()
            
            user_data = response.json()
            return {
                "provider_user_id": user_data["id"],
                "email": user_data["email"],
                "first_name": user_data.get("given_name", ""),
                "last_name": user_data.get("family_name", ""),
                "name": user_data.get("name", ""),
                "picture": user_data.get("picture", ""),
                "email_verified": user_data.get("verified_email", False)
            }

class MicrosoftSSOProvider(SSOProviderBase):
    """Microsoft Azure AD provider"""
    
    def __init__(self):
        super().__init__("microsoft")
    
    def get_auth_url(self, state: str) -> str:
        auth_url = self.oauth_config["auth_url"].format(tenant=self.config.MICROSOFT_TENANT_ID)
        params = {
            "client_id": self.config.MICROSOFT_CLIENT_ID,
            "redirect_uri": self.config.MICROSOFT_REDIRECT_URI,
            "scope": self.oauth_config["scope"],
            "response_type": "code",
            "state": state,
            "response_mode": "query"
        }
        return f"{auth_url}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            token_url = self.oauth_config["token_url"].format(tenant=self.config.MICROSOFT_TENANT_ID)
            data = {
                "client_id": self.config.MICROSOFT_CLIENT_ID,
                "client_secret": self.config.MICROSOFT_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.config.MICROSOFT_REDIRECT_URI
            }
            
            response = await client.post(token_url, data=data)
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            response = await client.get(self.oauth_config["userinfo_url"], headers=headers)
            response.raise_for_status()
            
            user_data = response.json()
            return {
                "provider_user_id": user_data["id"],
                "email": user_data.get("mail") or user_data.get("userPrincipalName", ""),
                "first_name": user_data.get("givenName", ""),
                "last_name": user_data.get("surname", ""),
                "name": user_data.get("displayName", ""),
                "picture": "",  # Microsoft Graph requires separate call for photo
                "email_verified": True  # Azure AD emails are verified
            }

class LinkedInSSOProvider(SSOProviderBase):
    """LinkedIn OAuth provider"""
    
    def __init__(self):
        super().__init__("linkedin")
    
    def get_auth_url(self, state: str) -> str:
        params = {
            "client_id": self.config.LINKEDIN_CLIENT_ID,
            "redirect_uri": self.config.LINKEDIN_REDIRECT_URI,
            "scope": self.oauth_config["scope"],
            "response_type": "code",
            "state": state
        }
        return f"{self.oauth_config['auth_url']}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            data = {
                "client_id": self.config.LINKEDIN_CLIENT_ID,
                "client_secret": self.config.LINKEDIN_CLIENT_SECRET,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.config.LINKEDIN_REDIRECT_URI
            }
            
            response = await client.post(self.oauth_config["token_url"], data=data)
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Get profile info
            profile_response = await client.get(self.oauth_config["userinfo_url"], headers=headers)
            profile_response.raise_for_status()
            profile_data = profile_response.json()
            
            # Get email separately
            email_response = await client.get(
                "https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))",
                headers=headers
            )
            email_response.raise_for_status()
            email_data = email_response.json()
            
            email = ""
            if email_data.get("elements"):
                email = email_data["elements"][0]["handle~"]["emailAddress"]
            
            first_name = profile_data.get("firstName", {}).get("localized", {}).get("en_US", "")
            last_name = profile_data.get("lastName", {}).get("localized", {}).get("en_US", "")
            
            return {
                "provider_user_id": profile_data["id"],
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "name": f"{first_name} {last_name}".strip(),
                "picture": "",  # LinkedIn profile pictures require additional permissions
                "email_verified": True  # LinkedIn emails are verified
            }

class FacebookSSOProvider(SSOProviderBase):
    """Facebook Login provider"""
    
    def __init__(self):
        super().__init__("facebook")
    
    def get_auth_url(self, state: str) -> str:
        params = {
            "client_id": self.config.FACEBOOK_APP_ID,
            "redirect_uri": self.config.FACEBOOK_REDIRECT_URI,
            "scope": self.oauth_config["scope"],
            "response_type": "code",
            "state": state
        }
        return f"{self.oauth_config['auth_url']}?{urlencode(params)}"
    
    async def exchange_code_for_token(self, code: str, state: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            params = {
                "client_id": self.config.FACEBOOK_APP_ID,
                "client_secret": self.config.FACEBOOK_APP_SECRET,
                "code": code,
                "redirect_uri": self.config.FACEBOOK_REDIRECT_URI
            }
            
            response = await client.get(self.oauth_config["token_url"], params=params)
            response.raise_for_status()
            return response.json()
    
    async def get_user_info(self, access_token: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            params = {
                "fields": "id,email,first_name,last_name,name,picture",
                "access_token": access_token
            }
            
            response = await client.get(self.oauth_config["userinfo_url"], params=params)
            response.raise_for_status()
            
            user_data = response.json()
            return {
                "provider_user_id": user_data["id"],
                "email": user_data.get("email", ""),
                "first_name": user_data.get("first_name", ""),
                "last_name": user_data.get("last_name", ""),
                "name": user_data.get("name", ""),
                "picture": user_data.get("picture", {}).get("data", {}).get("url", ""),
                "email_verified": True  # Facebook emails are verified
            }

class SSOProviderFactory:
    """Factory for creating SSO providers"""
    
    _providers = {
        "google": GoogleSSOProvider,
        "microsoft": MicrosoftSSOProvider,
        "linkedin": LinkedInSSOProvider,
        "facebook": FacebookSSOProvider
    }
    
    @classmethod
    def create_provider(cls, provider_name: str) -> SSOProviderBase:
        if provider_name not in cls._providers:
            raise ValueError(f"Unsupported SSO provider: {provider_name}")
        
        return cls._providers[provider_name]()
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        return list(cls._providers.keys())

class SSOService:
    """Main SSO service for handling authentication"""
    
    def __init__(self):
        self.config = sso_config
        # Generate a proper Fernet key from the encryption key
        import base64
        key = base64.urlsafe_b64encode(self.config.ENCRYPTION_KEY.encode()[:32].ljust(32, b'0'))
        self.cipher = Fernet(key)
    
    def encrypt_token(self, token: str) -> str:
        """Encrypt token for secure storage"""
        return self.cipher.encrypt(token.encode()).decode()
    
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt stored token"""
        return self.cipher.decrypt(encrypted_token.encode()).decode()
    
    def generate_jwt_token(self, customer_id: str, auth_method: str) -> Dict[str, str]:
        """Generate JWT access and refresh tokens"""
        now = datetime.utcnow()
        
        # Access token payload
        access_payload = {
            "sub": str(customer_id),
            "auth_method": auth_method,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(minutes=self.config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        }
        
        # Refresh token payload
        refresh_payload = {
            "sub": str(customer_id),
            "auth_method": auth_method,
            "type": "refresh",
            "iat": now,
            "exp": now + timedelta(days=self.config.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
        }
        
        access_token = jwt.encode(access_payload, self.config.JWT_SECRET_KEY, algorithm=self.config.JWT_ALGORITHM)
        refresh_token = jwt.encode(refresh_payload, self.config.JWT_SECRET_KEY, algorithm=self.config.JWT_ALGORITHM)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": self.config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(token, self.config.JWT_SECRET_KEY, algorithms=[self.config.JWT_ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    async def initiate_sso_login(self, provider: str) -> Dict[str, str]:
        """Initiate SSO login process"""
        sso_provider = SSOProviderFactory.create_provider(provider)
        state = sso_provider.generate_state()
        auth_url = sso_provider.get_auth_url(state)
        
        return {
            "auth_url": auth_url,
            "state": state,
            "provider": provider
        }
    
    async def complete_sso_login(
        self, 
        provider: str, 
        code: str, 
        state: str, 
        db: AsyncSession,
        ip_address: str = None,
        user_agent: str = None
    ) -> Dict[str, Any]:
        """Complete SSO login process"""
        
        # Log authentication attempt
        await self._log_auth_attempt(db, None, provider, "login", ip_address, user_agent, True)
        
        try:
            sso_provider = SSOProviderFactory.create_provider(provider)
            
            # Exchange code for token
            token_data = await sso_provider.exchange_code_for_token(code, state)
            access_token = token_data["access_token"]
            
            # Get user info
            user_info = await sso_provider.get_user_info(access_token)
            
            # Find or create customer
            customer = await self._find_or_create_customer(db, user_info, provider)
            
            # Create or update SSO account
            sso_account = await self._create_or_update_sso_account(
                db, customer, provider, user_info, token_data
            )
            
            # Generate JWT tokens
            jwt_tokens = self.generate_jwt_token(str(customer.id), provider)
            
            # Create session
            session = await self._create_session(
                db, customer, provider, jwt_tokens, ip_address, user_agent
            )
            
            # Update last login
            sso_account.last_login_at = datetime.utcnow()
            await db.commit()
            
            return {
                "customer": {
                    "id": str(customer.id),
                    "email": customer.email,
                    "first_name": customer.first_name,
                    "last_name": customer.last_name,
                    "verification_status": customer.verification_status,
                    "profile_picture_url": customer.profile_picture_url
                },
                "tokens": jwt_tokens,
                "session_id": str(session.id)
            }
            
        except Exception as e:
            await self._log_auth_attempt(db, None, provider, "login", ip_address, user_agent, False, str(e))
            raise
    
    async def _find_or_create_customer(
        self, 
        db: AsyncSession, 
        user_info: Dict[str, Any], 
        provider: str
    ) -> Customer:
        """Find existing customer or create new one"""
        
        # First, try to find by SSO account
        stmt = select(Customer).join(CustomerSSOAccount).where(
            and_(
                CustomerSSOAccount.provider == provider,
                CustomerSSOAccount.provider_user_id == user_info["provider_user_id"]
            )
        )
        result = await db.execute(stmt)
        customer = result.scalar_one_or_none()
        
        if customer:
            return customer
        
        # Try to find by email
        stmt = select(Customer).where(Customer.email == user_info["email"])
        result = await db.execute(stmt)
        customer = result.scalar_one_or_none()
        
        if customer:
            return customer
        
        # Create new customer
        customer = Customer(
            email=user_info["email"],
            first_name=user_info["first_name"],
            last_name=user_info["last_name"],
            email_verified=user_info.get("email_verified", False),
            profile_picture_url=user_info.get("picture", ""),
            preferred_auth_method=provider
        )
        
        db.add(customer)
        await db.flush()  # Get the ID
        return customer
    
    async def _create_or_update_sso_account(
        self,
        db: AsyncSession,
        customer: Customer,
        provider: str,
        user_info: Dict[str, Any],
        token_data: Dict[str, Any]
    ) -> CustomerSSOAccount:
        """Create or update SSO account"""
        
        # Check if SSO account exists
        stmt = select(CustomerSSOAccount).where(
            and_(
                CustomerSSOAccount.customer_id == customer.id,
                CustomerSSOAccount.provider == provider,
                CustomerSSOAccount.provider_user_id == user_info["provider_user_id"]
            )
        )
        result = await db.execute(stmt)
        sso_account = result.scalar_one_or_none()
        
        if sso_account:
            # Update existing account
            sso_account.provider_email = user_info["email"]
            sso_account.provider_name = user_info["name"]
            sso_account.provider_picture_url = user_info.get("picture", "")
            sso_account.access_token_hash = self.encrypt_token(token_data["access_token"])
            if "refresh_token" in token_data:
                sso_account.refresh_token_hash = self.encrypt_token(token_data["refresh_token"])
            sso_account.token_expires_at = datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600))
            sso_account.updated_at = datetime.utcnow()
        else:
            # Create new SSO account
            sso_account = CustomerSSOAccount(
                customer_id=customer.id,
                provider=provider,
                provider_user_id=user_info["provider_user_id"],
                provider_email=user_info["email"],
                provider_name=user_info["name"],
                provider_picture_url=user_info.get("picture", ""),
                access_token_hash=self.encrypt_token(token_data["access_token"]),
                refresh_token_hash=self.encrypt_token(token_data.get("refresh_token", "")) if "refresh_token" in token_data else None,
                token_expires_at=datetime.utcnow() + timedelta(seconds=token_data.get("expires_in", 3600)),
                is_primary=True  # First SSO account is primary
            )
            db.add(sso_account)
        
        return sso_account
    
    async def _create_session(
        self,
        db: AsyncSession,
        customer: Customer,
        auth_method: str,
        jwt_tokens: Dict[str, str],
        ip_address: str = None,
        user_agent: str = None
    ) -> CustomerSession:
        """Create customer session"""
        
        session = CustomerSession(
            customer_id=customer.id,
            session_token=jwt_tokens["access_token"],
            refresh_token=jwt_tokens["refresh_token"],
            auth_method=auth_method,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=datetime.utcnow() + timedelta(hours=self.config.SESSION_EXPIRE_HOURS)
        )
        
        db.add(session)
        return session
    
    async def _log_auth_attempt(
        self,
        db: AsyncSession,
        customer_id: Optional[str],
        auth_method: str,
        action: str,
        ip_address: str = None,
        user_agent: str = None,
        success: bool = True,
        failure_reason: str = None
    ):
        """Log authentication attempt"""
        
        log_entry = CustomerAuthLog(
            customer_id=customer_id,
            auth_method=auth_method,
            action=action,
            ip_address=ip_address,
            user_agent=user_agent,
            success=success,
            failure_reason=failure_reason
        )
        
        db.add(log_entry)
    
    async def refresh_token(self, refresh_token: str, db: AsyncSession) -> Optional[Dict[str, str]]:
        """Refresh JWT token"""
        
        payload = self.verify_jwt_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None
        
        customer_id = payload["sub"]
        auth_method = payload["auth_method"]
        
        # Generate new tokens
        new_tokens = self.generate_jwt_token(customer_id, auth_method)
        
        # Update session
        stmt = select(CustomerSession).where(
            and_(
                CustomerSession.customer_id == customer_id,
                CustomerSession.refresh_token == refresh_token,
                CustomerSession.is_active == True
            )
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if session:
            session.session_token = new_tokens["access_token"]
            session.refresh_token = new_tokens["refresh_token"]
            session.last_activity_at = datetime.utcnow()
            await db.commit()
        
        return new_tokens
    
    async def logout(self, session_token: str, db: AsyncSession) -> bool:
        """Logout user and invalidate session"""
        
        stmt = select(CustomerSession).where(
            and_(
                CustomerSession.session_token == session_token,
                CustomerSession.is_active == True
            )
        )
        result = await db.execute(stmt)
        session = result.scalar_one_or_none()
        
        if session:
            session.is_active = False
            await self._log_auth_attempt(
                db, str(session.customer_id), session.auth_method, "logout"
            )
            await db.commit()
            return True
        
        return False

# Global SSO service instance
sso_service = SSOService()