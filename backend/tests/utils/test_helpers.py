"""
Test helper utilities for Customs Broker Portal Backend.

This module provides common helper functions, mock factories, and utilities
that are used across different test modules to reduce code duplication
and improve test maintainability.
"""

import asyncio
import random
import string
from datetime import date, datetime, timedelta
from typing import Dict, Any, List, Optional
from unittest.mock import AsyncMock, MagicMock

from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import models for test data creation
from models.tariff import TariffCode
from models.hierarchy import TariffSection, TariffChapter, TradeAgreement
from models.duty import DutyRate
from models.fta import FtaRate
from models.dumping import DumpingDuty
from models.tco import Tco


class TestDataFactory:
    """Factory class for creating test data objects."""
    
    @staticmethod
    def random_string(length: int = 10) -> str:
        """Generate a random string of specified length."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))
    
    @staticmethod
    def random_hs_code() -> str:
        """Generate a random 10-digit HS code."""
        return ''.join(random.choices(string.digits, k=10))
    
    @staticmethod
    def random_email() -> str:
        """Generate a random email address."""
        username = TestDataFactory.random_string(8).lower()
        domain = TestDataFactory.random_string(6).lower()
        return f"{username}@{domain}.com"
    
    @staticmethod
    def create_tariff_code_data(**overrides) -> Dict[str, Any]:
        """Create sample tariff code data."""
        data = {
            "hs_code": TestDataFactory.random_hs_code(),
            "description": f"Test product {TestDataFactory.random_string(5)}",
            "unit": "Number",
            "statistical_code": "01",
            "is_active": True,
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def create_duty_rate_data(**overrides) -> Dict[str, Any]:
        """Create sample duty rate data."""
        data = {
            "hs_code": TestDataFactory.random_hs_code(),
            "general_rate": round(random.uniform(0, 20), 2),
            "unit_type": "ad_valorem",
            "rate_text": "5%",
            "effective_date": date.today(),
            "is_active": True,
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def create_fta_rate_data(**overrides) -> Dict[str, Any]:
        """Create sample FTA rate data."""
        data = {
            "hs_code": TestDataFactory.random_hs_code(),
            "fta_code": "AUSFTA",
            "country_code": "USA",
            "preferential_rate": 0.0,
            "staging_category": "A",
            "effective_date": date.today(),
            "is_active": True,
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def create_dumping_duty_data(**overrides) -> Dict[str, Any]:
        """Create sample dumping duty data."""
        data = {
            "hs_code": TestDataFactory.random_hs_code(),
            "country_code": "CHN",
            "duty_type": "dumping",
            "duty_rate": round(random.uniform(5, 50), 2),
            "case_number": f"ADC{random.randint(2020, 2025)}-{random.randint(1, 999):03d}",
            "is_active": True,
        }
        data.update(overrides)
        return data
    
    @staticmethod
    def create_tco_data(**overrides) -> Dict[str, Any]:
        """Create sample TCO data."""
        data = {
            "tco_number": f"TCO{random.randint(2020, 2025)}{random.randint(1, 999):03d}",
            "hs_code": TestDataFactory.random_hs_code(),
            "description": f"Test TCO item {TestDataFactory.random_string(5)}",
            "applicant_name": f"Test Applicant {TestDataFactory.random_string(3)} Pty Ltd",
            "effective_date": date.today(),
            "expiry_date": date.today() + timedelta(days=365),
            "is_current": True,
        }
        data.update(overrides)
        return data


class DatabaseTestHelper:
    """Helper class for database operations in tests."""
    
    @staticmethod
    async def create_tariff_code(session: AsyncSession, **kwargs) -> TariffCode:
        """Create a tariff code in the test database."""
        data = TestDataFactory.create_tariff_code_data(**kwargs)
        tariff_code = TariffCode(**data)
        session.add(tariff_code)
        await session.commit()
        await session.refresh(tariff_code)
        return tariff_code
    
    @staticmethod
    async def create_duty_rate(session: AsyncSession, **kwargs) -> DutyRate:
        """Create a duty rate in the test database."""
        data = TestDataFactory.create_duty_rate_data(**kwargs)
        duty_rate = DutyRate(**data)
        session.add(duty_rate)
        await session.commit()
        await session.refresh(duty_rate)
        return duty_rate
    
    @staticmethod
    async def create_fta_rate(session: AsyncSession, **kwargs) -> FtaRate:
        """Create an FTA rate in the test database."""
        data = TestDataFactory.create_fta_rate_data(**kwargs)
        fta_rate = FtaRate(**data)
        session.add(fta_rate)
        await session.commit()
        await session.refresh(fta_rate)
        return fta_rate
    
    @staticmethod
    async def create_dumping_duty(session: AsyncSession, **kwargs) -> DumpingDuty:
        """Create a dumping duty in the test database."""
        data = TestDataFactory.create_dumping_duty_data(**kwargs)
        dumping_duty = DumpingDuty(**data)
        session.add(dumping_duty)
        await session.commit()
        await session.refresh(dumping_duty)
        return dumping_duty
    
    @staticmethod
    async def create_tco(session: AsyncSession, **kwargs) -> Tco:
        """Create a TCO in the test database."""
        data = TestDataFactory.create_tco_data(**kwargs)
        tco = Tco(**data)
        session.add(tco)
        await session.commit()
        await session.refresh(tco)
        return tco
    
    @staticmethod
    async def count_records(session: AsyncSession, model_class) -> int:
        """Count records of a specific model in the database."""
        from sqlalchemy import select, func
        result = await session.execute(select(func.count(model_class.id)))
        return result.scalar()
    
    @staticmethod
    async def clear_table(session: AsyncSession, model_class):
        """Clear all records from a specific table."""
        from sqlalchemy import delete
        await session.execute(delete(model_class))
        await session.commit()


class APITestHelper:
    """Helper class for API testing operations."""
    
    @staticmethod
    def assert_response_success(response, expected_status: int = 200):
        """Assert that an API response is successful."""
        assert response.status_code == expected_status, (
            f"Expected status {expected_status}, got {response.status_code}. "
            f"Response: {response.text}"
        )
    
    @staticmethod
    def assert_response_error(response, expected_status: int = 400):
        """Assert that an API response contains an error."""
        assert response.status_code == expected_status, (
            f"Expected error status {expected_status}, got {response.status_code}. "
            f"Response: {response.text}"
        )
    
    @staticmethod
    def assert_json_response(response, expected_keys: List[str] = None):
        """Assert that response is valid JSON with expected keys."""
        APITestHelper.assert_response_success(response)
        data = response.json()
        assert isinstance(data, dict), "Response should be a JSON object"
        
        if expected_keys:
            for key in expected_keys:
                assert key in data, f"Expected key '{key}' not found in response"
        
        return data
    
    @staticmethod
    def assert_pagination_response(response, expected_keys: List[str] = None):
        """Assert that response follows pagination format."""
        data = APITestHelper.assert_json_response(response)
        
        # Check pagination structure
        pagination_keys = ["items", "total", "page", "size", "pages"]
        for key in pagination_keys:
            assert key in data, f"Pagination key '{key}' not found in response"
        
        assert isinstance(data["items"], list), "Items should be a list"
        assert isinstance(data["total"], int), "Total should be an integer"
        assert isinstance(data["page"], int), "Page should be an integer"
        assert isinstance(data["size"], int), "Size should be an integer"
        assert isinstance(data["pages"], int), "Pages should be an integer"
        
        if expected_keys:
            for item in data["items"]:
                for key in expected_keys:
                    assert key in item, f"Expected key '{key}' not found in item"
        
        return data


class MockHelper:
    """Helper class for creating mock objects."""
    
    @staticmethod
    def create_mock_anthropic_response(text: str = "Mock AI response"):
        """Create a mock Anthropic API response."""
        mock_response = AsyncMock()
        mock_content = MagicMock()
        mock_content.text = text
        mock_response.content = [mock_content]
        return mock_response
    
    @staticmethod
    def create_mock_external_api_response(
        status_code: int = 200,
        json_data: Dict[str, Any] = None,
        text_data: str = None
    ):
        """Create a mock external API response."""
        mock_response = MagicMock()
        mock_response.status_code = status_code
        
        if json_data:
            mock_response.json.return_value = json_data
        
        if text_data:
            mock_response.text = text_data
        
        return mock_response


class AsyncTestHelper:
    """Helper class for async testing operations."""
    
    @staticmethod
    async def run_with_timeout(coro, timeout: float = 5.0):
        """Run an async coroutine with a timeout."""
        try:
            return await asyncio.wait_for(coro, timeout=timeout)
        except asyncio.TimeoutError:
            raise AssertionError(f"Operation timed out after {timeout} seconds")
    
    @staticmethod
    async def assert_async_raises(exception_class, coro):
        """Assert that an async coroutine raises a specific exception."""
        try:
            await coro
            raise AssertionError(f"Expected {exception_class.__name__} to be raised")
        except exception_class:
            pass  # Expected exception was raised
        except Exception as e:
            raise AssertionError(
                f"Expected {exception_class.__name__}, but got {type(e).__name__}: {e}"
            )


class PerformanceTestHelper:
    """Helper class for performance testing."""
    
    @staticmethod
    async def measure_execution_time(coro):
        """Measure the execution time of an async coroutine."""
        import time
        start_time = time.time()
        result = await coro
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    
    @staticmethod
    def assert_execution_time(execution_time: float, max_time: float):
        """Assert that execution time is within acceptable limits."""
        assert execution_time <= max_time, (
            f"Execution took {execution_time:.3f}s, expected <= {max_time}s"
        )


class ValidationTestHelper:
    """Helper class for validation testing."""
    
    @staticmethod
    def assert_validation_error(response, field_name: str = None):
        """Assert that response contains validation errors."""
        APITestHelper.assert_response_error(response, 422)
        data = response.json()
        
        assert "detail" in data, "Validation error should contain 'detail'"
        errors = data["detail"]
        assert isinstance(errors, list), "Validation errors should be a list"
        assert len(errors) > 0, "Should have at least one validation error"
        
        if field_name:
            field_errors = [
                error for error in errors 
                if error.get("loc") and field_name in error["loc"]
            ]
            assert len(field_errors) > 0, f"No validation error found for field '{field_name}'"
        
        return errors
    
    @staticmethod
    def create_invalid_data_variants(valid_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create variants of data with invalid values for testing."""
        variants = []
        
        for key, value in valid_data.items():
            # Create variant with missing field
            missing_field_data = valid_data.copy()
            del missing_field_data[key]
            variants.append(missing_field_data)
            
            # Create variant with None value
            none_value_data = valid_data.copy()
            none_value_data[key] = None
            variants.append(none_value_data)
            
            # Create variant with wrong type
            if isinstance(value, str) and value:
                wrong_type_data = valid_data.copy()
                wrong_type_data[key] = 123  # Number instead of string
                variants.append(wrong_type_data)
            elif isinstance(value, (int, float)):
                wrong_type_data = valid_data.copy()
                wrong_type_data[key] = "not_a_number"
                variants.append(wrong_type_data)
        
        return variants


# Export all helper classes
__all__ = [
    "TestDataFactory",
    "DatabaseTestHelper", 
    "APITestHelper",
    "MockHelper",
    "AsyncTestHelper",
    "PerformanceTestHelper",
    "ValidationTestHelper",
]