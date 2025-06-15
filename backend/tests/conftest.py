"""
Test configuration and fixtures for Customs Broker Portal Backend.

This module provides comprehensive test fixtures for database setup,
async session management, test client configuration, and common test utilities.
All fixtures are designed to provide proper test isolation and cleanup.
"""

import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator, Generator
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import application components
from backend.config import Settings
from database import Base, get_async_session

# Import main app with error handling to avoid circular imports
try:
    from main import app
    # Models will be imported through the app if needed
    models_available = True
except ImportError as e:
    # Create a minimal FastAPI app for testing if main app can't be imported
    from fastapi import FastAPI
    app = FastAPI(title="Test App")
    models_available = False
    print(f"Warning: Using minimal test app due to import error: {e}")


# Test Settings Configuration
class TestSettings:
    """Test-specific settings that override production settings."""
    
    # Override database to use SQLite in-memory for tests
    database_url: str = "sqlite+aiosqlite:///:memory:"
    
    # Test environment settings
    environment: str = "test"
    debug: bool = True
    
    # Disable external services for testing
    anthropic_api_key: str = "test-api-key"
    redis_url: str = "redis://localhost:6379"  # Default redis URL for tests
    
    # Test security settings
    secret_key: str = "test-secret-key-for-testing-only"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 5  # Short expiry for tests
    
    # Disable rate limiting in tests
    rate_limit_enabled: bool = False
    
    # Test logging configuration
    log_level: str = "WARNING"  # Reduce log noise in tests
    
    # Additional test-specific settings
    app_name: str = "Test Customs Broker Portal API"
    app_version: str = "1.0.0-test"


@pytest.fixture(scope="session")
def test_settings() -> TestSettings:
    """Provide test-specific settings."""
    return TestSettings()


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """
    Create an event loop for the test session.
    
    This fixture ensures that async tests have a consistent event loop
    throughout the test session.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine(test_settings: TestSettings):
    """
    Create a test database engine using SQLite in-memory.
    
    This fixture provides a fresh database engine for each test function,
    ensuring complete test isolation.
    """
    engine = create_async_engine(
        test_settings.database_url,
        echo=False,  # Set to True for SQL debugging
        poolclass=StaticPool,
        connect_args={
            "check_same_thread": False,
        },
        future=True,
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session_factory(test_engine):
    """
    Create a test session factory.
    
    This fixture provides a session factory that creates isolated
    database sessions for testing.
    """
    return async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=True,
        autocommit=False,
    )


@pytest_asyncio.fixture(scope="function")
async def test_session(test_session_factory) -> AsyncGenerator[AsyncSession, None]:
    """
    Provide a test database session.
    
    This fixture provides a clean database session for each test,
    with automatic rollback to ensure test isolation.
    """
    async with test_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()
            await session.close()


@pytest.fixture(scope="function")
def override_get_async_session(test_session: AsyncSession):
    """
    Override the database session dependency for testing.
    
    This fixture replaces the production database session with
    the test session in FastAPI dependency injection.
    """
    async def _get_test_session():
        yield test_session
    
    app.dependency_overrides[get_async_session] = _get_test_session
    yield
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_client(override_get_async_session) -> TestClient:
    """
    Provide a test client for synchronous API testing.
    
    This fixture creates a FastAPI test client with the test database
    session dependency override applied.
    """
    return TestClient(app)


@pytest_asyncio.fixture(scope="function")
async def async_test_client(override_get_async_session) -> AsyncGenerator[AsyncClient, None]:
    """
    Provide an async test client for asynchronous API testing.
    
    This fixture creates an async HTTP client for testing FastAPI
    endpoints that require async operations.
    """
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


# Database Test Utilities
@pytest_asyncio.fixture(scope="function")
async def clean_database(test_session: AsyncSession):
    """
    Ensure a clean database state before each test.
    
    This fixture can be used to explicitly clean the database
    before running tests that require a pristine state.
    """
    # Clear all tables in reverse order to handle foreign key constraints
    for table in reversed(Base.metadata.sorted_tables):
        await test_session.execute(table.delete())
    await test_session.commit()
    yield
    # Cleanup after test
    for table in reversed(Base.metadata.sorted_tables):
        await test_session.execute(table.delete())
    await test_session.commit()


# Mock Fixtures
@pytest.fixture(scope="function")
def mock_anthropic_client():
    """
    Mock Anthropic AI client for testing AI features.
    
    This fixture provides a mock client that can be used to test
    AI integration without making actual API calls.
    """
    mock_client = AsyncMock()
    mock_response = AsyncMock()
    mock_response.content = [
        MagicMock(text="Mocked AI response for testing")
    ]
    mock_client.messages.create.return_value = mock_response
    return mock_client


@pytest.fixture(scope="function")
def mock_external_api():
    """
    Mock external API responses for testing.
    
    This fixture provides mock responses for external API calls
    to ensure tests don't depend on external services.
    """
    return MagicMock()


# Test Data Fixtures
@pytest.fixture(scope="function")
def sample_tariff_data():
    """
    Provide sample tariff data for testing.
    
    This fixture returns a dictionary of sample data that can be
    used to create test tariff codes and related entities.
    """
    return {
        "hs_code": "0101010000",
        "description": "Live horses for breeding purposes",
        "unit": "Number",
        "general_rate": 5.0,
        "statistical_code": "01",
        "is_active": True,
    }


@pytest.fixture(scope="function")
def sample_duty_data():
    """
    Provide sample duty rate data for testing.
    """
    return {
        "hs_code": "0101010000",
        "general_rate": 5.0,
        "unit_type": "ad_valorem",
        "rate_text": "5%",
        "effective_date": "2023-01-01",
        "is_active": True,
    }


@pytest.fixture(scope="function")
def sample_fta_data():
    """
    Provide sample FTA rate data for testing.
    """
    return {
        "hs_code": "0101010000",
        "fta_code": "AUSFTA",
        "country_code": "USA",
        "preferential_rate": 0.0,
        "staging_category": "A",
        "effective_date": "2023-01-01",
        "is_active": True,
    }


@pytest.fixture(scope="function")
def sample_user_data():
    """
    Provide sample user data for authentication testing.
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpassword123",
        "is_active": True,
        "is_verified": True,
    }


# Authentication Fixtures
@pytest.fixture(scope="function")
def auth_headers(test_settings: TestSettings):
    """
    Provide authentication headers for API testing.
    
    This fixture creates valid JWT tokens for testing
    authenticated endpoints.
    """
    from datetime import datetime, timedelta
    from jose import jwt
    
    # Create a test token
    expire = datetime.utcnow() + timedelta(minutes=test_settings.access_token_expire_minutes)
    token_data = {
        "sub": "testuser",
        "exp": expire,
        "type": "access"
    }
    
    token = jwt.encode(
        token_data,
        test_settings.secret_key,
        algorithm=test_settings.algorithm
    )
    
    return {"Authorization": f"Bearer {token}"}


# Environment Setup
@pytest.fixture(autouse=True)
def setup_test_environment(test_settings: TestSettings):
    """
    Set up test environment variables.
    
    This fixture automatically sets up the test environment
    for all tests, ensuring consistent configuration.
    """
    # Set environment variables for testing
    os.environ["ENVIRONMENT"] = "test"
    os.environ["DATABASE_URL"] = test_settings.database_url
    os.environ["SECRET_KEY"] = test_settings.secret_key
    os.environ["LOG_LEVEL"] = test_settings.log_level
    
    yield
    
    # Cleanup environment variables
    test_env_vars = [
        "ENVIRONMENT",
        "DATABASE_URL", 
        "SECRET_KEY",
        "LOG_LEVEL"
    ]
    for var in test_env_vars:
        if var in os.environ:
            del os.environ[var]


# Performance Testing Fixtures
@pytest.fixture(scope="function")
def performance_timer():
    """
    Provide a performance timer for testing execution time.
    
    This fixture can be used to measure and assert on
    the performance of specific operations.
    """
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.end_time = None
        
        def start(self):
            self.start_time = time.time()
        
        def stop(self):
            self.end_time = time.time()
        
        @property
        def elapsed(self):
            if self.start_time and self.end_time:
                return self.end_time - self.start_time
            return None
    
    return Timer()


# Logging Fixtures
@pytest.fixture(scope="function")
def capture_logs():
    """
    Capture log messages for testing logging functionality.
    
    This fixture provides a way to capture and assert on
    log messages generated during tests.
    """
    import logging
    from io import StringIO
    
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    handler.setLevel(logging.DEBUG)
    
    # Add handler to root logger
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)
    
    yield log_capture
    
    # Cleanup
    root_logger.removeHandler(handler)


# Pytest Hooks
def pytest_configure(config):
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )
    config.addinivalue_line(
        "markers", "database: mark test as requiring database access"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "external: mark test as requiring external services"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test location."""
    for item in items:
        # Add markers based on test file location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "api" in str(item.fspath):
            item.add_marker(pytest.mark.api)
        
        # Add database marker for tests using database fixtures
        if any(fixture in item.fixturenames for fixture in [
            "test_session", "clean_database", "test_engine"
        ]):
            item.add_marker(pytest.mark.database)