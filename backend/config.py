"""
Configuration management for the Customs Broker Portal FastAPI backend.

This module uses Pydantic Settings for type-safe configuration management
with support for environment variables and validation.
"""

import os
from typing import Optional, List
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings with environment variable support.
    
    All settings can be overridden via environment variables.
    For nested settings, use double underscores (e.g., DATABASE__URL).
    """
    
    # Application settings
    app_name: str = Field(default="Customs Broker Portal API", description="Application name")
    app_version: str = Field(default="1.0.0", description="Application version")
    debug: bool = Field(default=False, description="Debug mode")
    environment: str = Field(default="development", description="Environment (development, staging, production)")
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    reload: bool = Field(default=True, description="Auto-reload on code changes")
    
    # Database settings
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:password@localhost:5432/customs_broker_portal",
        description="PostgreSQL database URL with asyncpg driver"
    )
    database_pool_size: int = Field(default=20, description="Database connection pool size")
    database_max_overflow: int = Field(default=30, description="Database connection pool max overflow")
    database_pool_timeout: int = Field(default=30, description="Database connection pool timeout")
    database_pool_recycle: int = Field(default=3600, description="Database connection pool recycle time")
    
    # Security settings
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Secret key for JWT token signing"
    )
    algorithm: str = Field(default="HS256", description="JWT algorithm")
    access_token_expire_minutes: int = Field(default=30, description="Access token expiration time")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:*", "http://127.0.0.1:*", "https://localhost:*", "https://127.0.0.1:*"],
        description="Allowed CORS origins"
    )
    cors_allow_credentials: bool = Field(default=True, description="Allow CORS credentials")
    cors_allow_methods: List[str] = Field(default=["*"], description="Allowed CORS methods")
    cors_allow_headers: List[str] = Field(default=["*"], description="Allowed CORS headers")
    
    # AI Integration settings
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key for AI features")
    anthropic_model: str = Field(default="claude-3-sonnet-20240229", description="Anthropic model to use")
    anthropic_max_tokens: int = Field(default=4000, description="Maximum tokens for AI responses")
    anthropic_temperature: float = Field(default=0.1, description="AI response temperature")
    
    # Logging settings
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(default="json", description="Log format (json, text)")
    log_file: Optional[str] = Field(default=None, description="Log file path")
    
    # API settings
    api_v1_prefix: str = Field(default="/api/v1", description="API v1 prefix")
    docs_url: str = Field(default="/docs", description="API documentation URL")
    redoc_url: str = Field(default="/redoc", description="ReDoc documentation URL")
    openapi_url: str = Field(default="/openapi.json", description="OpenAPI schema URL")
    
    # Rate limiting settings
    rate_limit_enabled: bool = Field(default=True, description="Enable rate limiting")
    rate_limit_requests: int = Field(default=100, description="Rate limit requests per minute")
    rate_limit_window: int = Field(default=60, description="Rate limit window in seconds")
    
    # Cache settings
    redis_url: Optional[str] = Field(default=None, description="Redis URL for caching")
    cache_ttl: int = Field(default=300, description="Default cache TTL in seconds")
    
    # File upload settings
    max_file_size: int = Field(default=10 * 1024 * 1024, description="Maximum file upload size (10MB)")
    allowed_file_types: List[str] = Field(
        default=[".pdf", ".xlsx", ".xls", ".csv", ".txt"],
        description="Allowed file upload types"
    )
    
    # External API settings
    abf_api_base_url: str = Field(
        default="https://www.abf.gov.au",
        description="Australian Border Force API base URL"
    )
    abf_api_timeout: int = Field(default=30, description="ABF API timeout in seconds")
    
    # Monitoring and health check settings
    health_check_interval: int = Field(default=30, description="Health check interval in seconds")
    metrics_enabled: bool = Field(default=True, description="Enable metrics collection")
    
    @field_validator("database_url")
    def validate_database_url(cls, v):
        """Validate database URL format."""
        valid_schemes = (
            "postgresql://", "postgresql+asyncpg://",  # PostgreSQL
            "sqlite://", "sqlite+aiosqlite:///"        # SQLite for development
        )
        if not v.startswith(valid_schemes):
            raise ValueError("Database URL must use PostgreSQL with asyncpg driver or SQLite with aiosqlite for development")
        return v
    
    @field_validator("cors_origins")
    def validate_cors_origins(cls, v):
        """Validate CORS origins format."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @field_validator("log_level")
    def validate_log_level(cls, v):
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of: {valid_levels}")
        return v.upper()
    
    @field_validator("environment")
    def validate_environment(cls, v):
        """Validate environment setting."""
        valid_environments = ["development", "staging", "production"]
        if v.lower() not in valid_environments:
            raise ValueError(f"Environment must be one of: {valid_environments}")
        return v.lower()
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Allow environment variables to override settings
        env_nested_delimiter = "__"
        
        # Example environment variables:
        # DATABASE_URL=postgresql+asyncpg://user:pass@localhost/db
        # ANTHROPIC_API_KEY=your_api_key
        # CORS_ORIGINS=http://localhost:3000,http://localhost:3001
        # LOG_LEVEL=DEBUG
        # ENVIRONMENT=production


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """
    Get application settings.
    
    This function can be used as a dependency in FastAPI routes
    to inject configuration settings.
    
    Returns:
        Settings: Application configuration settings
    """
    return settings


def is_development() -> bool:
    """Check if running in development environment."""
    return settings.environment == "development"


def is_production() -> bool:
    """Check if running in production environment."""
    return settings.environment == "production"


def get_database_url() -> str:
    """Get the database URL for SQLAlchemy."""
    return settings.database_url


def get_cors_config() -> dict:
    """Get CORS configuration for FastAPI."""
    if is_development():
        # In development, allow all origins for flexibility
        return {
            "allow_origins": ["*"],
            "allow_credentials": False,  # Can't use credentials with allow_origins=["*"]
            "allow_methods": settings.cors_allow_methods,
            "allow_headers": settings.cors_allow_headers,
        }
    else:
        # In production, use specific origins
        return {
            "allow_origins": settings.cors_origins,
            "allow_credentials": settings.cors_allow_credentials,
            "allow_methods": settings.cors_allow_methods,
            "allow_headers": settings.cors_allow_headers,
        }


def get_logging_config() -> dict:
    """Get logging configuration."""
    return {
        "level": settings.log_level,
        "format": settings.log_format,
        "file": settings.log_file,
    }


# Export commonly used settings
__all__ = [
    "Settings",
    "settings",
    "get_settings",
    "is_development",
    "is_production",
    "get_database_url",
    "get_cors_config",
    "get_logging_config",
]