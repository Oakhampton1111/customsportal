# =====================================================
# Customs Broker Portal - Configuration Management
# =====================================================
# 
# Configuration management for different environments with database connections,
# API keys, rate limiting settings, and scraper-specific configurations.
# 
# Supports: Development, Staging, Production environments
# Features: Environment variables, secure credential management, validation
# =====================================================

import os
import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from pathlib import Path
from pydantic import validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import toml
from urllib.parse import urlparse

# =====================================================
# ENVIRONMENT DETECTION
# =====================================================

def get_environment() -> str:
    """Detect current environment from environment variables."""
    return os.getenv('ENVIRONMENT', os.getenv('ENV', 'development')).lower()

def is_production() -> bool:
    """Check if running in production environment."""
    return get_environment() == 'production'

def is_development() -> bool:
    """Check if running in development environment."""
    return get_environment() == 'development'

# =====================================================
# DATABASE CONFIGURATION
# =====================================================

@dataclass
class DatabaseConfig:
    """Database connection configuration."""
    host: str = "localhost"
    port: int = 5432
    database: str = "customs_broker"
    username: str = "customs_user"
    password: str = ""
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    
    @property
    def connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        return f"postgresql://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
    
    @property
    def async_connection_string(self) -> str:
        """Generate async PostgreSQL connection string."""
        return f"postgresql+asyncpg://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"

# =====================================================
# RATE LIMITING CONFIGURATION
# =====================================================

@dataclass
class RateLimitConfig:
    """Rate limiting configuration for respectful scraping."""
    requests_per_minute: int = 30
    requests_per_hour: int = 1000
    concurrent_requests: int = 5
    delay_between_requests: float = 2.0
    exponential_backoff_base: float = 2.0
    max_retry_delay: int = 300
    jitter: bool = True
    respect_robots_txt: bool = True
    
    def get_delay(self) -> float:
        """Get delay between requests with jitter if enabled."""
        import random
        delay = self.delay_between_requests
        if self.jitter:
            # Add ±25% jitter to avoid thundering herd
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        return max(0.1, delay)  # Minimum 100ms delay

# =====================================================
# BROWSERLESS API CONFIGURATION
# =====================================================

@dataclass
class BrowserlessConfig:
    """Browserless API configuration for modern web scraping."""
    api_url: str = "https://chrome.browserless.io"
    api_key: str = ""
    timeout: int = 60
    max_retries: int = 3
    retry_delay: float = 2.0
    max_concurrent_sessions: int = 3
    enable_stealth: bool = True
    enable_adblock: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080
    user_agent: str = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    
    # BrowserQL specific settings
    default_wait_for: str = "networkidle2"
    default_timeout: int = 30000  # 30 seconds in milliseconds
    enable_javascript: bool = True
    enable_images: bool = False  # Optimize for speed
    enable_css: bool = True
    
    # Anti-detection settings
    block_resources: List[str] = field(default_factory=lambda: [
        "image", "media", "font", "texttrack", "object", "beacon", "csp_report", "imageset"
    ])
    extra_headers: Dict[str, str] = field(default_factory=lambda: {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0"
    })
    
    @property
    def session_url(self) -> str:
        """Get the session endpoint URL."""
        return f"{self.api_url.rstrip('/')}/session"
    
    @property
    def content_url(self) -> str:
        """Get the content endpoint URL."""
        return f"{self.api_url.rstrip('/')}/content"
    
    @property
    def function_url(self) -> str:
        """Get the function endpoint URL."""
        return f"{self.api_url.rstrip('/')}/function"
    
    @property
    def auth_headers(self) -> Dict[str, str]:
        """Get authentication headers."""
        if self.api_key:
            return {"Authorization": f"Bearer {self.api_key}"}
        return {}
    
    def get_launch_options(self) -> Dict[str, Any]:
        """Get browser launch options for Browserless."""
        return {
            "args": [
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                "--disable-gpu",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--disable-features=TranslateUI",
                "--disable-ipc-flooding-protection",
                f"--window-size={self.viewport_width},{self.viewport_height}"
            ] + (["--disable-web-security", "--disable-features=VizDisplayCompositor"] if self.enable_stealth else []),
            "defaultViewport": {
                "width": self.viewport_width,
                "height": self.viewport_height
            },
            "ignoreHTTPSErrors": True,
            "ignoreDefaultArgs": ["--enable-automation"],
        }

# =====================================================
# SCRAPER-SPECIFIC CONFIGURATIONS
# =====================================================

@dataclass
class ABFScraperConfig:
    """Australian Border Force scraper configuration."""
    base_url: str = "https://www.abf.gov.au"
    tariff_url: str = "https://www.abf.gov.au/importing-exporting-and-manufacturing/tariff-classification/current-tariff"
    tco_url: str = "https://www.abf.gov.au/importing-exporting-and-manufacturing/tariff-concessions-system"
    timeout: int = 30
    max_retries: int = 3
    user_agent: str = "CustomsBrokerPortal/1.0 (+https://example.com/contact)"
    headers: Dict[str, str] = field(default_factory=lambda: {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-AU,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    })

@dataclass
class FTAScraperConfig:
    """Free Trade Agreement scraper configuration."""
    dfat_base_url: str = "https://www.dfat.gov.au"
    fta_portal_url: str = "https://www.dfat.gov.au/trade/agreements"
    timeout: int = 30
    max_retries: int = 3
    supported_agreements: List[str] = field(default_factory=lambda: [
        'AUSFTA', 'CPTPP', 'KAFTA', 'ChAFTA', 'JAEPA', 'AANZFTA', 'MAFTA', 'TAFTA', 'IACEPA', 'PACER'
    ])

@dataclass
class AntiDumpingScraperConfig:
    """Anti-dumping scraper configuration."""
    base_url: str = "https://www.industry.gov.au/anti-dumping-commission"
    dcr_url: str = "https://www.industry.gov.au/anti-dumping-commission/current-measures-dumping-commodity-register-dcr"
    timeout: int = 30
    max_retries: int = 3

@dataclass
class LegislationScraperConfig:
    """Federal legislation scraper configuration."""
    base_url: str = "https://www.legislation.gov.au"
    priority_acts: List[str] = field(default_factory=lambda: [
        "C1901A00006",  # Customs Act 1901
        "C2020C00251",  # Customs Tariff Act 1995
        "F2015L00375",  # Customs Regulation 2015
    ])
    timeout: int = 45
    max_retries: int = 2

# =====================================================
# LOGGING CONFIGURATION
# =====================================================

@dataclass
class LoggingConfig:
    """Logging configuration for monitoring scraping activities."""
    level: str = "INFO"
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_path: Optional[str] = None
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5
    structured_logging: bool = True
    log_to_console: bool = True
    log_to_file: bool = True
    
    def get_log_level(self) -> int:
        """Convert string log level to logging constant."""
        return getattr(logging, self.level.upper(), logging.INFO)

# =====================================================
# MAIN CONFIGURATION CLASS
# =====================================================

class ScraperSettings(BaseSettings):
    """Main configuration class using Pydantic for validation."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False,
        extra='ignore'
    )
    
    # Environment
    environment: str = Field(default="development", description="Current environment")
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # Database
    db_host: str = Field(default="localhost", description="Database host")
    db_port: int = Field(default=5432, description="Database port")
    db_name: str = Field(default="customs_broker", description="Database name")
    db_user: str = Field(default="customs_user", description="Database username")
    db_password: str = Field(default="", description="Database password")
    db_pool_size: int = Field(default=10, description="Database connection pool size")
    
    # Redis (for Celery)
    redis_url: str = Field(default="redis://localhost:6379/0", description="Redis connection URL")
    
    # API Keys (optional for AI features)
    anthropic_api_key: Optional[str] = Field(default=None, description="Anthropic API key")
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    
    # Browserless API
    browserless_api_url: str = Field(default="https://chrome.browserless.io", description="Browserless API URL")
    browserless_api_key: str = Field(default="", description="Browserless API key")
    browserless_timeout: int = Field(default=60, description="Browserless request timeout")
    browserless_max_sessions: int = Field(default=3, description="Maximum concurrent Browserless sessions")
    
    # Rate Limiting
    global_rate_limit: int = Field(default=30, description="Global requests per minute")
    concurrent_requests: int = Field(default=5, description="Maximum concurrent requests")
    request_delay: float = Field(default=2.0, description="Delay between requests in seconds")
    
    # Monitoring
    sentry_dsn: Optional[str] = Field(default=None, description="Sentry DSN for error tracking")
    log_level: str = Field(default="INFO", description="Logging level")
    
    # Security
    user_agent: str = Field(
        default="CustomsBrokerPortal/1.0 (+https://example.com/contact)",
        description="User agent for HTTP requests"
    )
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment value."""
        valid_envs = ['development', 'staging', 'production']
        if v.lower() not in valid_envs:
            raise ValueError(f'Environment must be one of: {valid_envs}')
        return v.lower()
    
    @validator('db_password')
    def validate_db_password(cls, v, values):
        """Validate database password is provided in production."""
        if values.get('environment') == 'production' and not v:
            raise ValueError('Database password is required in production')
        return v
    
    @validator('browserless_api_key')
    def validate_browserless_api_key(cls, v, values):
        """Validate Browserless API key is provided in production."""
        if values.get('environment') == 'production' and not v:
            raise ValueError('Browserless API key is required in production')
        return v
    
    @property
    def database_config(self) -> DatabaseConfig:
        """Get database configuration."""
        return DatabaseConfig(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            username=self.db_user,
            password=self.db_password,
            pool_size=self.db_pool_size,
            echo=self.debug
        )
    
    @property
    def rate_limit_config(self) -> RateLimitConfig:
        """Get rate limiting configuration."""
        return RateLimitConfig(
            requests_per_minute=self.global_rate_limit,
            concurrent_requests=self.concurrent_requests,
            delay_between_requests=self.request_delay
        )
    
    @property
    def browserless_config(self) -> BrowserlessConfig:
        """Get Browserless API configuration."""
        return BrowserlessConfig(
            api_url=self.browserless_api_url,
            api_key=self.browserless_api_key,
            timeout=self.browserless_timeout,
            max_concurrent_sessions=self.browserless_max_sessions,
            enable_stealth=True,
            enable_adblock=True,
            user_agent=self.user_agent
        )
    
    @property
    def logging_config(self) -> LoggingConfig:
        """Get logging configuration."""
        return LoggingConfig(
            level=self.log_level,
            structured_logging=not self.debug,
            file_path=f"logs/scrapers_{self.environment}.log" if not self.debug else None
        )

# =====================================================
# CONFIGURATION FACTORY
# =====================================================

class ConfigurationManager:
    """Centralized configuration management."""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self._settings: Optional[ScraperSettings] = None
        self._scrapers_config: Dict[str, Any] = {}
        
    @property
    def settings(self) -> ScraperSettings:
        """Get main settings, loading if necessary."""
        if self._settings is None:
            self._settings = ScraperSettings()
        return self._settings
    
    def get_abf_config(self) -> ABFScraperConfig:
        """Get ABF scraper configuration."""
        if 'abf' not in self._scrapers_config:
            config = ABFScraperConfig()
            # Override with environment-specific settings
            if self.settings.environment == 'production':
                config.max_retries = 5
                config.timeout = 60
            self._scrapers_config['abf'] = config
        return self._scrapers_config['abf']
    
    def get_fta_config(self) -> FTAScraperConfig:
        """Get FTA scraper configuration."""
        if 'fta' not in self._scrapers_config:
            config = FTAScraperConfig()
            if self.settings.environment == 'production':
                config.max_retries = 5
                config.timeout = 60
            self._scrapers_config['fta'] = config
        return self._scrapers_config['fta']
    
    def get_anti_dumping_config(self) -> AntiDumpingScraperConfig:
        """Get anti-dumping scraper configuration."""
        if 'anti_dumping' not in self._scrapers_config:
            config = AntiDumpingScraperConfig()
            if self.settings.environment == 'production':
                config.max_retries = 5
                config.timeout = 60
            self._scrapers_config['anti_dumping'] = config
        return self._scrapers_config['anti_dumping']
    
    def get_legislation_config(self) -> LegislationScraperConfig:
        """Get legislation scraper configuration."""
        if 'legislation' not in self._scrapers_config:
            config = LegislationScraperConfig()
            if self.settings.environment == 'production':
                config.max_retries = 3
                config.timeout = 90
            self._scrapers_config['legislation'] = config
        return self._scrapers_config['legislation']
    
    def get_browserless_config(self) -> BrowserlessConfig:
        """Get Browserless API configuration."""
        if 'browserless' not in self._scrapers_config:
            config = self.settings.browserless_config
            # Environment-specific overrides
            if self.settings.environment == 'production':
                config.max_retries = 5
                config.timeout = 90
                config.max_concurrent_sessions = 5
            elif self.settings.environment == 'development':
                config.enable_images = True  # Enable images in dev for debugging
                config.timeout = 30
            self._scrapers_config['browserless'] = config
        return self._scrapers_config['browserless']
    
    def load_from_file(self, file_path: str) -> None:
        """Load configuration from TOML file."""
        if Path(file_path).exists():
            with open(file_path, 'r') as f:
                config_data = toml.load(f)
                # Update environment variables with file data
                for key, value in config_data.items():
                    if isinstance(value, dict):
                        for sub_key, sub_value in value.items():
                            env_key = f"{key}_{sub_key}".upper()
                            os.environ.setdefault(env_key, str(sub_value))
                    else:
                        os.environ.setdefault(key.upper(), str(value))
    
    def validate_configuration(self) -> List[str]:
        """Validate configuration and return list of issues."""
        issues = []
        
        # Check database connectivity
        try:
            db_config = self.settings.database_config
            parsed_url = urlparse(db_config.connection_string)
            if not all([parsed_url.hostname, parsed_url.port, parsed_url.path]):
                issues.append("Invalid database connection string")
        except Exception as e:
            issues.append(f"Database configuration error: {e}")
        
        # Check Browserless API configuration
        try:
            browserless_config = self.settings.browserless_config
            if self.settings.environment == 'production' and not browserless_config.api_key:
                issues.append("Browserless API key is required in production")
            
            # Validate API URL format
            parsed_url = urlparse(browserless_config.api_url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                issues.append("Invalid Browserless API URL format")
                
        except Exception as e:
            issues.append(f"Browserless configuration error: {e}")
        
        # Check required directories
        log_config = self.settings.logging_config
        if log_config.file_path:
            log_dir = Path(log_config.file_path).parent
            if not log_dir.exists():
                try:
                    log_dir.mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    issues.append(f"Cannot create log directory: {e}")
        
        # Check production requirements
        if self.settings.environment == 'production':
            if not self.settings.db_password:
                issues.append("Database password required in production")
            if self.settings.debug:
                issues.append("Debug mode should be disabled in production")
        
        return issues

# =====================================================
# GLOBAL CONFIGURATION INSTANCE
# =====================================================

# Global configuration manager instance
config_manager = ConfigurationManager()

# Convenience functions for accessing configuration
def get_settings() -> ScraperSettings:
    """Get main application settings."""
    return config_manager.settings

def get_database_config() -> DatabaseConfig:
    """Get database configuration."""
    return config_manager.settings.database_config

def get_rate_limit_config() -> RateLimitConfig:
    """Get rate limiting configuration."""
    return config_manager.settings.rate_limit_config

def get_abf_config() -> ABFScraperConfig:
    """Get ABF scraper configuration."""
    return config_manager.get_abf_config()

def get_fta_config() -> FTAScraperConfig:
    """Get FTA scraper configuration."""
    return config_manager.get_fta_config()

def get_anti_dumping_config() -> AntiDumpingScraperConfig:
    """Get anti-dumping scraper configuration."""
    return config_manager.get_anti_dumping_config()

def get_legislation_config() -> LegislationScraperConfig:
    """Get legislation scraper configuration."""
    return config_manager.get_legislation_config()

def get_browserless_config() -> BrowserlessConfig:
    """Get Browserless API configuration."""
    return config_manager.get_browserless_config()

def get_logging_config() -> LoggingConfig:
    """Get logging configuration."""
    return config_manager.settings.logging_config

# =====================================================
# CONFIGURATION VALIDATION
# =====================================================

def validate_all_configurations() -> None:
    """Validate all configurations and raise exception if invalid."""
    issues = config_manager.validate_configuration()
    if issues:
        raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"- {issue}" for issue in issues))

# =====================================================
# EXAMPLE USAGE
# =====================================================

if __name__ == "__main__":
    # Example usage and testing
    print("Customs Broker Portal - Configuration Test")
    print("=" * 50)
    
    try:
        # Load and validate configuration
        validate_all_configurations()
        
        # Display current configuration
        settings = get_settings()
        print(f"Environment: {settings.environment}")
        print(f"Database: {settings.database_config.connection_string}")
        print(f"Rate Limit: {settings.rate_limit_config.requests_per_minute} req/min")
        print(f"Log Level: {settings.logging_config.level}")
        
        # Test scraper configurations
        abf_config = get_abf_config()
        print(f"ABF Base URL: {abf_config.base_url}")
        
        # Test Browserless configuration
        browserless_config = get_browserless_config()
        print(f"Browserless API URL: {browserless_config.api_url}")
        print(f"Browserless Sessions: {browserless_config.max_concurrent_sessions}")
        
        print("\n✅ Configuration validation successful!")
        
    except Exception as e:
        print(f"\n❌ Configuration validation failed: {e}")