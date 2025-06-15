# =====================================================
# Customs Broker Portal - Scraper Utilities
# =====================================================
# 
# Error handling utilities, logging setup, retry logic with exponential backoff,
# data validation functions, and database connection helpers.
# 
# Features:
# - Robust error handling and retry mechanisms
# - Structured logging with monitoring integration
# - Database connection management and helpers
# - Data validation and deduplication utilities
# - Rate limiting and respectful scraping utilities
# =====================================================

import asyncio
import logging
import time
import random
import hashlib
import json
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Callable, Union, Tuple
from functools import wraps
from contextlib import asynccontextmanager
from dataclasses import dataclass
from pathlib import Path

import aiohttp
import asyncpg
import pandas as pd
import structlog
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from tenacity import (
    retry, stop_after_attempt, wait_exponential, 
    retry_if_exception_type, before_sleep_log
)
try:
    from circuit_breaker import CircuitBreaker
except ImportError:
    # Fallback if circuit-breaker is not installed
    class CircuitBreaker:
        def __init__(self, *args, **kwargs):
            pass
        def __call__(self, func):
            return func
import sentry_sdk
from rich.console import Console
from rich.logging import RichHandler

from .config import get_settings, get_database_config, get_rate_limit_config, get_logging_config

# =====================================================
# LOGGING SETUP
# =====================================================

def setup_logging() -> logging.Logger:
    """Setup structured logging with rich formatting and monitoring integration."""
    log_config = get_logging_config()
    settings = get_settings()
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if log_config.structured_logging else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Setup standard logging
    logger = logging.getLogger("customs_scraper")
    logger.setLevel(log_config.get_log_level())
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler with rich formatting
    if log_config.log_to_console:
        console = Console()
        console_handler = RichHandler(
            console=console,
            show_time=True,
            show_path=True,
            rich_tracebacks=True
        )
        console_handler.setLevel(log_config.get_log_level())
        logger.addHandler(console_handler)
    
    # File handler
    if log_config.log_to_file and log_config.file_path:
        from logging.handlers import RotatingFileHandler
        
        # Ensure log directory exists
        log_path = Path(log_config.file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_config.file_path,
            maxBytes=log_config.max_file_size,
            backupCount=log_config.backup_count
        )
        file_handler.setLevel(log_config.get_log_level())
        
        formatter = logging.Formatter(log_config.format)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Setup Sentry for error tracking
    if settings.sentry_dsn:
        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.environment,
            traces_sample_rate=0.1 if settings.environment == 'production' else 1.0
        )
    
    return logger

# Global logger instance
logger = setup_logging()

# =====================================================
# ERROR HANDLING AND RETRY LOGIC
# =====================================================

@dataclass
class ScrapingError(Exception):
    """Base exception for scraping operations."""
    message: str
    source_url: Optional[str] = None
    status_code: Optional[int] = None
    retry_after: Optional[int] = None
    
    def __str__(self) -> str:
        return f"ScrapingError: {self.message} (URL: {self.source_url}, Status: {self.status_code})"

@dataclass
class RateLimitError(ScrapingError):
    """Exception for rate limiting issues."""
    pass

@dataclass
class DataValidationError(Exception):
    """Exception for data validation failures."""
    field: str
    value: Any
    message: str
    
    def __str__(self) -> str:
        return f"DataValidationError: {self.field}={self.value} - {self.message}"

def exponential_backoff_with_jitter(
    min_delay: float = 1.0,
    max_delay: float = 300.0,
    multiplier: float = 2.0,
    jitter: bool = True
) -> Callable:
    """Create exponential backoff function with optional jitter."""
    
    def backoff_func(retry_state) -> float:
        delay = min(max_delay, min_delay * (multiplier ** retry_state.attempt_number))
        
        if jitter:
            # Add ±25% jitter
            jitter_range = delay * 0.25
            delay += random.uniform(-jitter_range, jitter_range)
        
        return max(0.1, delay)
    
    return backoff_func

def retry_with_exponential_backoff(
    max_attempts: int = 3,
    min_delay: float = 1.0,
    max_delay: float = 300.0,
    exceptions: Tuple = (aiohttp.ClientError, asyncio.TimeoutError, ScrapingError)
):
    """Decorator for retry logic with exponential backoff."""
    
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=2, min=min_delay, max=max_delay),
        retry=retry_if_exception_type(exceptions),
        before_sleep=before_sleep_log(logger, logging.WARNING),
        reraise=True
    )

# =====================================================
# RATE LIMITING
# =====================================================

class RateLimiter:
    """Async rate limiter for respectful scraping."""
    
    def __init__(self, requests_per_minute: int = 30, concurrent_limit: int = 5):
        self.requests_per_minute = requests_per_minute
        self.concurrent_limit = concurrent_limit
        self.request_times: List[float] = []
        self.semaphore = asyncio.Semaphore(concurrent_limit)
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> None:
        """Acquire rate limit permission."""
        async with self.semaphore:
            async with self._lock:
                now = time.time()
                
                # Remove requests older than 1 minute
                cutoff = now - 60
                self.request_times = [t for t in self.request_times if t > cutoff]
                
                # Check if we need to wait
                if len(self.request_times) >= self.requests_per_minute:
                    sleep_time = 60 - (now - self.request_times[0])
                    if sleep_time > 0:
                        logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                        await asyncio.sleep(sleep_time)
                
                # Record this request
                self.request_times.append(now)

# Global rate limiter
rate_limiter = RateLimiter(
    requests_per_minute=get_rate_limit_config().requests_per_minute,
    concurrent_limit=get_rate_limit_config().concurrent_requests
)

# =====================================================
# DATABASE CONNECTION MANAGEMENT
# =====================================================

class DatabaseManager:
    """Async database connection manager with connection pooling."""
    
    def __init__(self):
        self.db_config = get_database_config()
        self._engine = None
        self._async_engine = None
        self._session_factory = None
        
    @property
    def engine(self):
        """Get synchronous SQLAlchemy engine."""
        if self._engine is None:
            self._engine = create_engine(
                self.db_config.connection_string,
                pool_size=self.db_config.pool_size,
                max_overflow=self.db_config.max_overflow,
                pool_timeout=self.db_config.pool_timeout,
                pool_recycle=self.db_config.pool_recycle,
                echo=self.db_config.echo
            )
        return self._engine
    
    @property
    def async_engine(self):
        """Get asynchronous SQLAlchemy engine."""
        if self._async_engine is None:
            self._async_engine = create_async_engine(
                self.db_config.async_connection_string,
                pool_size=self.db_config.pool_size,
                max_overflow=self.db_config.max_overflow,
                pool_timeout=self.db_config.pool_timeout,
                pool_recycle=self.db_config.pool_recycle,
                echo=self.db_config.echo
            )
        return self._async_engine
    
    @asynccontextmanager
    async def get_async_session(self):
        """Get async database session with automatic cleanup."""
        if self._session_factory is None:
            self._session_factory = sessionmaker(
                self.async_engine, class_=AsyncSession, expire_on_commit=False
            )
        
        async with self._session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute a query and return results as list of dictionaries."""
        async with self.get_async_session() as session:
            result = await session.execute(text(query), params or {})
            return [dict(row._mapping) for row in result.fetchall()]
    
    async def execute_insert(self, table: str, data: Dict) -> int:
        """Execute insert and return the ID of inserted record."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(f':{key}' for key in data.keys())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders}) RETURNING id"
        
        async with self.get_async_session() as session:
            result = await session.execute(text(query), data)
            return result.scalar()
    
    async def execute_upsert(self, table: str, data: Dict, conflict_columns: List[str]) -> int:
        """Execute upsert (INSERT ... ON CONFLICT) and return ID."""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(f':{key}' for key in data.keys())
        conflict_cols = ', '.join(conflict_columns)
        
        update_clause = ', '.join(f'{key} = EXCLUDED.{key}' for key in data.keys() if key not in conflict_columns)
        
        query = f"""
        INSERT INTO {table} ({columns}) 
        VALUES ({placeholders})
        ON CONFLICT ({conflict_cols}) 
        DO UPDATE SET {update_clause}
        RETURNING id
        """
        
        async with self.get_async_session() as session:
            result = await session.execute(text(query), data)
            return result.scalar()
    
    async def health_check(self) -> bool:
        """Check database connectivity."""
        try:
            await self.execute_query("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Global database manager
db_manager = DatabaseManager()

# =====================================================
# HTTP CLIENT UTILITIES
# =====================================================

class HTTPClient:
    """Async HTTP client with rate limiting and error handling."""
    
    def __init__(self):
        self.settings = get_settings()
        self.rate_config = get_rate_limit_config()
        self._session: Optional[aiohttp.ClientSession] = None
        
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            connector = aiohttp.TCPConnector(limit=self.rate_config.concurrent_requests)
            
            headers = {
                'User-Agent': self.settings.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-AU,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
            }
            
            self._session = aiohttp.ClientSession(
                timeout=timeout,
                connector=connector,
                headers=headers
            )
        
        return self._session
    
    @retry_with_exponential_backoff(max_attempts=3)
    async def get(self, url: str, **kwargs) -> aiohttp.ClientResponse:
        """Make GET request with rate limiting and retry logic."""
        await rate_limiter.acquire()
        
        session = await self.get_session()
        
        try:
            async with session.get(url, **kwargs) as response:
                if response.status == 429:  # Rate limited
                    retry_after = int(response.headers.get('Retry-After', 60))
                    raise RateLimitError(
                        message=f"Rate limited by server",
                        source_url=url,
                        status_code=response.status,
                        retry_after=retry_after
                    )
                
                if response.status >= 400:
                    raise ScrapingError(
                        message=f"HTTP error {response.status}",
                        source_url=url,
                        status_code=response.status
                    )
                
                return response
                
        except aiohttp.ClientError as e:
            raise ScrapingError(
                message=f"HTTP client error: {e}",
                source_url=url
            )
    
    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()

# Global HTTP client
http_client = HTTPClient()

# =====================================================
# DATA VALIDATION UTILITIES
# =====================================================

def validate_hs_code(hs_code: str) -> str:
    """Validate and normalize HS code format."""
    if not hs_code:
        raise DataValidationError("hs_code", hs_code, "HS code cannot be empty")
    
    # Remove dots and spaces, keep only digits
    normalized = re.sub(r'[^\d]', '', str(hs_code))
    
    # Check length (2, 4, 6, 8, or 10 digits)
    if len(normalized) not in [2, 4, 6, 8, 10]:
        raise DataValidationError("hs_code", hs_code, f"Invalid HS code length: {len(normalized)}")
    
    return normalized

def validate_duty_rate(rate: Union[str, float, None]) -> Optional[float]:
    """Validate and normalize duty rate."""
    if rate is None or rate == '':
        return None
    
    if isinstance(rate, str):
        # Handle text rates like "Free", "Nil"
        rate_lower = rate.lower().strip()
        if rate_lower in ['free', 'nil', 'n/a', '']:
            return 0.0
        
        # Extract percentage
        percent_match = re.search(r'(\d+(?:\.\d+)?)%', rate)
        if percent_match:
            return float(percent_match.group(1))
        
        # Try to convert to float
        try:
            return float(rate)
        except ValueError:
            raise DataValidationError("duty_rate", rate, f"Cannot parse duty rate: {rate}")
    
    if isinstance(rate, (int, float)):
        if rate < 0:
            raise DataValidationError("duty_rate", rate, "Duty rate cannot be negative")
        return float(rate)
    
    raise DataValidationError("duty_rate", rate, f"Invalid duty rate type: {type(rate)}")

def validate_date(date_str: Union[str, datetime, None]) -> Optional[datetime]:
    """Validate and parse date string."""
    if date_str is None or date_str == '':
        return None
    
    if isinstance(date_str, datetime):
        return date_str
    
    if isinstance(date_str, str):
        # Common date formats
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d-%m-%Y',
            '%Y/%m/%d',
            '%d %B %Y',
            '%d %b %Y',
            '%B %d, %Y'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt)
            except ValueError:
                continue
        
        raise DataValidationError("date", date_str, f"Cannot parse date: {date_str}")
    
    raise DataValidationError("date", date_str, f"Invalid date type: {type(date_str)}")

def validate_country_code(country_code: str) -> str:
    """Validate country code format."""
    if not country_code:
        raise DataValidationError("country_code", country_code, "Country code cannot be empty")
    
    # Normalize to uppercase
    normalized = country_code.strip().upper()
    
    # Check length (should be 2 or 3 characters)
    if len(normalized) not in [2, 3]:
        raise DataValidationError("country_code", country_code, f"Invalid country code length: {len(normalized)}")
    
    # Check format (letters only)
    if not normalized.isalpha():
        raise DataValidationError("country_code", country_code, "Country code must contain only letters")
    
    return normalized

# =====================================================
# DATA DEDUPLICATION UTILITIES
# =====================================================

def generate_content_hash(data: Dict) -> str:
    """Generate hash for data deduplication."""
    # Sort keys for consistent hashing
    sorted_data = {k: v for k, v in sorted(data.items()) if v is not None}
    content_str = json.dumps(sorted_data, sort_keys=True, default=str)
    return hashlib.md5(content_str.encode()).hexdigest()

async def check_duplicate_record(table: str, data: Dict, unique_fields: List[str]) -> Optional[int]:
    """Check if record already exists based on unique fields."""
    where_conditions = []
    params = {}
    
    for field in unique_fields:
        if field in data:
            where_conditions.append(f"{field} = :{field}")
            params[field] = data[field]
    
    if not where_conditions:
        return None
    
    query = f"SELECT id FROM {table} WHERE {' AND '.join(where_conditions)} LIMIT 1"
    
    try:
        results = await db_manager.execute_query(query, params)
        return results[0]['id'] if results else None
    except Exception as e:
        logger.error(f"Error checking duplicate record: {e}")
        return None

# =====================================================
# MONITORING AND HEALTH CHECK UTILITIES
# =====================================================

@dataclass
class ScrapingMetrics:
    """Metrics for scraping operations."""
    start_time: datetime
    end_time: Optional[datetime] = None
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    records_processed: int = 0
    records_inserted: int = 0
    records_updated: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
    
    @property
    def duration(self) -> Optional[timedelta]:
        """Get operation duration."""
        if self.end_time:
            return self.end_time - self.start_time
        return None
    
    @property
    def success_rate(self) -> float:
        """Get success rate percentage."""
        if self.total_requests == 0:
            return 0.0
        return (self.successful_requests / self.total_requests) * 100
    
    def to_dict(self) -> Dict:
        """Convert metrics to dictionary."""
        return {
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration.total_seconds() if self.duration else None,
            'total_requests': self.total_requests,
            'successful_requests': self.successful_requests,
            'failed_requests': self.failed_requests,
            'success_rate': self.success_rate,
            'records_processed': self.records_processed,
            'records_inserted': self.records_inserted,
            'records_updated': self.records_updated,
            'error_count': len(self.errors),
            'errors': self.errors[:10]  # Limit to first 10 errors
        }

class HealthChecker:
    """Health check utilities for monitoring system status."""
    
    @staticmethod
    async def check_database() -> Dict[str, Any]:
        """Check database connectivity and performance."""
        start_time = time.time()
        
        try:
            # Test basic connectivity
            await db_manager.execute_query("SELECT 1")
            
            # Test query performance
            query_start = time.time()
            await db_manager.execute_query("SELECT COUNT(*) FROM tariff_codes")
            query_time = time.time() - query_start
            
            total_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'response_time': total_time,
                'query_time': query_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'response_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }
    
    @staticmethod
    async def check_external_url(url: str) -> Dict[str, Any]:
        """Check external URL availability."""
        start_time = time.time()
        
        try:
            response = await http_client.get(url)
            response_time = time.time() - start_time
            
            return {
                'status': 'healthy',
                'url': url,
                'status_code': response.status,
                'response_time': response_time,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'url': url,
                'error': str(e),
                'response_time': time.time() - start_time,
                'timestamp': datetime.now().isoformat()
            }

# =====================================================
# CLEANUP AND SHUTDOWN
# =====================================================

async def cleanup_resources():
    """Cleanup all resources on shutdown."""
    logger.info("Cleaning up scraper resources...")
    
    try:
        await http_client.close()
        logger.info("HTTP client closed")
    except Exception as e:
        logger.error(f"Error closing HTTP client: {e}")
    
    try:
        if db_manager._async_engine:
            await db_manager._async_engine.dispose()
        logger.info("Database connections closed")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

# =====================================================
# EXAMPLE USAGE AND TESTING
# =====================================================

if __name__ == "__main__":
    async def test_utilities():
        """Test utility functions."""
        print("Testing Customs Broker Portal Utilities")
        print("=" * 50)
        
        # Test data validation
        try:
            hs_code = validate_hs_code("8471.30.00")
            print(f"✅ HS Code validation: {hs_code}")
            
            duty_rate = validate_duty_rate("15.5%")
            print(f"✅ Duty rate validation: {duty_rate}")
            
            date_obj = validate_date("2023-12-01")
            print(f"✅ Date validation: {date_obj}")
            
        except DataValidationError as e:
            print(f"❌ Validation error: {e}")
        
        # Test database health
        health_result = await HealthChecker.check_database()
        print(f"Database health: {health_result['status']}")
        
        # Test HTTP client
        try:
            response = await http_client.get("https://httpbin.org/get")
            print(f"✅ HTTP client test: {response.status}")
        except Exception as e:
            print(f"❌ HTTP client error: {e}")
        
        # Cleanup
        await cleanup_resources()
    
    # Run tests
    asyncio.run(test_utilities())