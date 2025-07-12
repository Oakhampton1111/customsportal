from pydantic_settings import BaseSettings
from typing import Dict, Any

class SSOConfig(BaseSettings):
    # Google OAuth 2.0
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:3000/auth/google/callback"
    
    # Microsoft Azure AD
    MICROSOFT_CLIENT_ID: str = ""
    MICROSOFT_CLIENT_SECRET: str = ""
    MICROSOFT_TENANT_ID: str = "common"  # Multi-tenant
    MICROSOFT_REDIRECT_URI: str = "http://localhost:3000/auth/microsoft/callback"
    
    # LinkedIn OAuth
    LINKEDIN_CLIENT_ID: str = ""
    LINKEDIN_CLIENT_SECRET: str = ""
    LINKEDIN_REDIRECT_URI: str = "http://localhost:3000/auth/linkedin/callback"
    
    # Facebook Login
    FACEBOOK_APP_ID: str = ""
    FACEBOOK_APP_SECRET: str = ""
    FACEBOOK_REDIRECT_URI: str = "http://localhost:3000/auth/facebook/callback"
    
    # JWT Configuration
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Encryption for SSO tokens
    ENCRYPTION_KEY: str = "your-encryption-key-32-chars-long"  # Must be 32 characters for Fernet
    
    # Session Configuration
    SESSION_EXPIRE_HOURS: int = 24
    MAX_SESSIONS_PER_USER: int = 5
    
    # Security Settings
    ALLOWED_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    SECURE_COOKIES: bool = False  # Set to True in production with HTTPS
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables

# OAuth Provider URLs
OAUTH_URLS = {
    "google": {
        "auth_url": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_url": "https://oauth2.googleapis.com/token",
        "userinfo_url": "https://www.googleapis.com/oauth2/v2/userinfo",
        "scope": "openid email profile"
    },
    "microsoft": {
        "auth_url": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/authorize",
        "token_url": "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token",
        "userinfo_url": "https://graph.microsoft.com/v1.0/me",
        "scope": "openid email profile User.Read"
    },
    "linkedin": {
        "auth_url": "https://www.linkedin.com/oauth/v2/authorization",
        "token_url": "https://www.linkedin.com/oauth/v2/accessToken",
        "userinfo_url": "https://api.linkedin.com/v2/people/~:(id,firstName,lastName,emailAddress,profilePicture(displayImage~:playableStreams))",
        "scope": "r_liteprofile r_emailaddress"
    },
    "facebook": {
        "auth_url": "https://www.facebook.com/v18.0/dialog/oauth",
        "token_url": "https://graph.facebook.com/v18.0/oauth/access_token",
        "userinfo_url": "https://graph.facebook.com/v18.0/me",
        "scope": "email public_profile"
    }
}

# Document verification point values for 100-point check
DOCUMENT_POINT_VALUES = {
    # Primary Documents (70 points)
    "passport": 70,
    "birth_certificate": 70,
    "citizenship_certificate": 70,
    
    # Secondary Documents (40 points)
    "drivers_license": 40,
    "proof_of_age_card": 40,
    "student_id": 40,
    "employee_id": 40,
    
    # Address Proof Documents (25 points)
    "utility_bill": 25,
    "bank_statement": 25,
    "rental_agreement": 25,
    "council_rates": 25,
    "medicare_card": 25,
    
    # Additional Documents (25 points)
    "credit_card": 25,
    "pension_card": 25,
    "health_care_card": 25,
    "seniors_card": 25
}

# Verification status mappings
VERIFICATION_STATUS = {
    "PENDING": "pending",
    "IN_REVIEW": "in_review", 
    "VERIFIED": "verified",
    "REJECTED": "rejected"
}

# Auth method mappings
AUTH_METHODS = {
    "EMAIL": "email",
    "GOOGLE": "google",
    "MICROSOFT": "microsoft",
    "LINKEDIN": "linkedin",
    "FACEBOOK": "facebook"
}

sso_config = SSOConfig()