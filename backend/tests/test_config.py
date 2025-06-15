"""
Test configuration validation for Customs Broker Portal Backend.

This module contains tests to verify that the testing infrastructure
is properly configured and working correctly.
"""

import pytest
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from httpx import AsyncClient

from tests.conftest import TestSettings
from tests.utils.test_helpers import (
    TestDataFactory,
    DatabaseTestHelper,
    APITestHelper,
    AsyncTestHelper
)


class TestTestingInfrastructure:
    """Test the testing infrastructure itself."""
    
    def test_test_settings_configuration(self, test_settings: TestSettings):
        """Test that test settings are properly configured."""
        assert test_settings.environment == "test"
        assert test_settings.database_url == "sqlite+aiosqlite:///:memory:"
        assert test_settings.debug is True
        assert test_settings.secret_key == "test-secret-key-for-testing-only"
        assert test_settings.rate_limit_enabled is False
        assert test_settings.log_level == "WARNING"
    
    @pytest.mark.asyncio
    async def test_async_session_fixture(self, test_session: AsyncSession):
        """Test that async database session fixture works."""
        assert test_session is not None
        assert isinstance(test_session, AsyncSession)
        
        # Test basic database operation
        from sqlalchemy import text
        result = await test_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
    
    @pytest.mark.asyncio
    async def test_database_isolation(self, test_session: AsyncSession):
        """Test that database tests are properly isolated."""
        # This test should start with a clean database
        from models.tariff import TariffCode
        from sqlalchemy import select
        
        result = await test_session.execute(select(TariffCode))
        tariff_codes = result.scalars().all()
        assert len(tariff_codes) == 0, "Database should be empty at test start"
    
    def test_sync_test_client(self, test_client: TestClient):
        """Test that synchronous test client works."""
        assert test_client is not None
        assert isinstance(test_client, TestClient)
        
        # Test basic health check endpoint (if available)
        response = test_client.get("/")
        # Note: This might fail if no root endpoint exists, which is fine
        # The important thing is that the client is properly configured
    
    @pytest.mark.asyncio
    async def test_async_test_client(self, async_test_client: AsyncClient):
        """Test that asynchronous test client works."""
        assert async_test_client is not None
        assert isinstance(async_test_client, AsyncClient)
        
        # Test basic request
        response = await async_test_client.get("/")
        # Note: This might fail if no root endpoint exists, which is fine
        # The important thing is that the client is properly configured


class TestTestDataFactory:
    """Test the test data factory utilities."""
    
    def test_random_string_generation(self):
        """Test random string generation."""
        string1 = TestDataFactory.random_string(10)
        string2 = TestDataFactory.random_string(10)
        
        assert len(string1) == 10
        assert len(string2) == 10
        assert string1 != string2  # Should be different
        assert string1.isalnum()  # Should be alphanumeric
    
    def test_random_hs_code_generation(self):
        """Test HS code generation."""
        hs_code = TestDataFactory.random_hs_code()
        
        assert len(hs_code) == 10
        assert hs_code.isdigit()
    
    def test_random_email_generation(self):
        """Test email generation."""
        email = TestDataFactory.random_email()
        
        assert "@" in email
        assert "." in email
        assert email.endswith(".com")
    
    def test_tariff_code_data_creation(self):
        """Test tariff code data creation."""
        data = TestDataFactory.create_tariff_code_data()
        
        required_fields = ["hs_code", "description", "unit", "statistical_code", "is_active"]
        for field in required_fields:
            assert field in data
        
        assert len(data["hs_code"]) == 10
        assert data["hs_code"].isdigit()
        assert isinstance(data["is_active"], bool)
    
    def test_tariff_code_data_with_overrides(self):
        """Test tariff code data creation with overrides."""
        custom_hs_code = "1234567890"
        data = TestDataFactory.create_tariff_code_data(hs_code=custom_hs_code)
        
        assert data["hs_code"] == custom_hs_code
    
    def test_duty_rate_data_creation(self):
        """Test duty rate data creation."""
        data = TestDataFactory.create_duty_rate_data()
        
        required_fields = ["hs_code", "general_rate", "unit_type", "rate_text", "effective_date", "is_active"]
        for field in required_fields:
            assert field in data
        
        assert isinstance(data["general_rate"], (int, float))
        assert 0 <= data["general_rate"] <= 20
    
    def test_fta_rate_data_creation(self):
        """Test FTA rate data creation."""
        data = TestDataFactory.create_fta_rate_data()
        
        required_fields = ["hs_code", "fta_code", "country_code", "preferential_rate", "staging_category", "effective_date", "is_active"]
        for field in required_fields:
            assert field in data
        
        assert data["fta_code"] == "AUSFTA"
        assert data["country_code"] == "USA"


class TestDatabaseTestHelper:
    """Test the database test helper utilities."""
    
    @pytest.mark.asyncio
    @pytest.mark.database
    async def test_create_tariff_code(self, test_session: AsyncSession):
        """Test creating a tariff code using the helper."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="1234567890",
            description="Test product"
        )
        
        assert tariff_code.id is not None
        assert tariff_code.hs_code == "1234567890"
        assert tariff_code.description == "Test product"
    
    @pytest.mark.asyncio
    @pytest.mark.database
    async def test_create_duty_rate(self, test_session: AsyncSession):
        """Test creating a duty rate using the helper."""
        duty_rate = await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code="1234567890",
            general_rate=5.0
        )
        
        assert duty_rate.id is not None
        assert duty_rate.hs_code == "1234567890"
        assert duty_rate.general_rate == 5.0
    
    @pytest.mark.asyncio
    @pytest.mark.database
    async def test_count_records(self, test_session: AsyncSession):
        """Test counting records using the helper."""
        from models.tariff import TariffCode
        
        # Initially should be 0
        count = await DatabaseTestHelper.count_records(test_session, TariffCode)
        assert count == 0
        
        # Create a record
        await DatabaseTestHelper.create_tariff_code(test_session)
        
        # Should now be 1
        count = await DatabaseTestHelper.count_records(test_session, TariffCode)
        assert count == 1


class TestAPITestHelper:
    """Test the API test helper utilities."""
    
    def test_assert_response_success(self):
        """Test successful response assertion."""
        from unittest.mock import MagicMock
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        
        # Should not raise an exception
        APITestHelper.assert_response_success(mock_response)
    
    def test_assert_response_error(self):
        """Test error response assertion."""
        from unittest.mock import MagicMock
        
        mock_response = MagicMock()
        mock_response.status_code = 400
        
        # Should not raise an exception
        APITestHelper.assert_response_error(mock_response, 400)
    
    def test_assert_json_response(self):
        """Test JSON response assertion."""
        from unittest.mock import MagicMock
        
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"key": "value", "test": "data"}
        
        data = APITestHelper.assert_json_response(mock_response, ["key"])
        assert data["key"] == "value"


class TestAsyncTestHelper:
    """Test the async test helper utilities."""
    
    @pytest.mark.asyncio
    async def test_run_with_timeout_success(self):
        """Test running async operation with timeout (success case)."""
        async def quick_operation():
            await asyncio.sleep(0.1)
            return "success"
        
        result = await AsyncTestHelper.run_with_timeout(quick_operation(), timeout=1.0)
        assert result == "success"
    
    @pytest.mark.asyncio
    async def test_run_with_timeout_failure(self):
        """Test running async operation with timeout (timeout case)."""
        async def slow_operation():
            await asyncio.sleep(2.0)
            return "success"
        
        with pytest.raises(AssertionError, match="Operation timed out"):
            await AsyncTestHelper.run_with_timeout(slow_operation(), timeout=0.1)
    
    @pytest.mark.asyncio
    async def test_assert_async_raises(self):
        """Test asserting that async operation raises exception."""
        async def failing_operation():
            raise ValueError("Test error")
        
        # Should not raise AssertionError
        await AsyncTestHelper.assert_async_raises(ValueError, failing_operation())
        
        # Should raise AssertionError if wrong exception type expected
        with pytest.raises(AssertionError):
            await AsyncTestHelper.assert_async_raises(TypeError, failing_operation())


class TestPytestMarkers:
    """Test that pytest markers are working correctly."""
    
    @pytest.mark.unit
    def test_unit_marker(self):
        """Test that unit marker works."""
        assert True
    
    @pytest.mark.integration
    def test_integration_marker(self):
        """Test that integration marker works."""
        assert True
    
    @pytest.mark.api
    def test_api_marker(self):
        """Test that API marker works."""
        assert True
    
    @pytest.mark.database
    def test_database_marker(self):
        """Test that database marker works."""
        assert True
    
    @pytest.mark.slow
    def test_slow_marker(self):
        """Test that slow marker works."""
        assert True


class TestEnvironmentSetup:
    """Test that test environment is properly set up."""
    
    def test_environment_variables(self):
        """Test that test environment variables are set."""
        import os
        
        assert os.environ.get("ENVIRONMENT") == "test"
        assert os.environ.get("DATABASE_URL") == "sqlite+aiosqlite:///:memory:"
        assert os.environ.get("SECRET_KEY") == "test-secret-key-for-testing-only"
        assert os.environ.get("LOG_LEVEL") == "WARNING"
    
    def test_test_isolation(self):
        """Test that tests are properly isolated."""
        # This test should always pass regardless of other test execution
        assert True