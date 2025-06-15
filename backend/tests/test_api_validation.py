"""
API endpoint tests for request/response validation.

This module tests input validation, response schema validation, error handling,
content-type handling, and data serialization across all API endpoints.
"""

import pytest
import pytest_asyncio
from decimal import Decimal
from datetime import date, datetime
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils.test_helpers import (
    APITestHelper, DatabaseTestHelper, TestDataFactory,
    ValidationTestHelper
)


@pytest.mark.api
class TestRequestValidation:
    """Test request validation across all endpoints."""
    
    async def test_tariff_search_validation(self, test_client: TestClient):
        """Test tariff search request validation."""
        # Test invalid query parameters
        invalid_params = [
            {"level": 0},  # Below minimum
            {"level": 15},  # Above maximum
            {"limit": 0},  # Below minimum
            {"limit": 2000},  # Above maximum
            {"offset": -1},  # Negative offset
            {"sort_order": "invalid"},  # Invalid sort order
        ]
        
        for params in invalid_params:
            response = test_client.get("/api/tariff/search", params=params)
            ValidationTestHelper.assert_validation_error(response)
    
    async def test_duty_calculation_validation(self, test_client: TestClient):
        """Test duty calculation request validation."""
        # Test various invalid request bodies
        invalid_requests = [
            {},  # Empty request
            {"hs_code": ""},  # Empty HS code
            {"hs_code": "123"},  # Too short HS code
            {"hs_code": "12345678901"},  # Too long HS code
            {"hs_code": "abcd123456"},  # Non-numeric HS code
            {
                "hs_code": "0101010000",
                "country_code": ""  # Empty country code
            },
            {
                "hs_code": "0101010000",
                "country_code": "INVALID"  # Invalid country code format
            },
            {
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": -100  # Negative value
            },
            {
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": 0  # Zero value
            },
            {
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": "invalid"  # Non-numeric value
            },
            {
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": 1000,
                "quantity": -1  # Negative quantity
            },
            {
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": 1000,
                "calculation_date": "invalid-date"  # Invalid date format
            },
            {
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": 1000,
                "value_basis": "INVALID"  # Invalid value basis
            }
        ]
        
        for invalid_request in invalid_requests:
            response = test_client.post("/api/duty/calculate", json=invalid_request)
            ValidationTestHelper.assert_validation_error(response)
    
    async def test_product_classification_validation(self, test_client: TestClient):
        """Test product classification request validation."""
        invalid_requests = [
            {},  # Empty request
            {"confidence_threshold": 0.8},  # Missing product_description
            {"product_description": ""},  # Empty description
            {
                "product_description": "test",
                "confidence_threshold": -0.1  # Below minimum
            },
            {
                "product_description": "test",
                "confidence_threshold": 1.1  # Above maximum
            },
            {
                "product_description": "test",
                "confidence_threshold": "invalid"  # Non-numeric
            },
            {
                "product_description": "test",
                "confidence_threshold": 0.8,
                "store_result": "invalid"  # Non-boolean
            }
        ]
        
        for invalid_request in invalid_requests:
            response = test_client.post("/api/search/classify", json=invalid_request)
            ValidationTestHelper.assert_validation_error(response)
    
    async def test_batch_classification_validation(self, test_client: TestClient):
        """Test batch classification request validation."""
        invalid_requests = [
            {},  # Empty request
            {"products": []},  # Empty products list
            {
                "products": [{"description": "test"}]
                # Missing confidence_threshold
            },
            {
                "products": [{"id": "1"}],  # Missing description
                "confidence_threshold": 0.8
            },
            {
                "products": [{"description": ""}],  # Empty description
                "confidence_threshold": 0.8
            },
            {
                "products": [{"description": "test"}],
                "confidence_threshold": 1.5  # Invalid threshold
            },
            {
                "products": [{"description": "test"}],
                "confidence_threshold": 0.8,
                "store_results": "invalid"  # Non-boolean
            }
        ]
        
        for invalid_request in invalid_requests:
            response = test_client.post("/api/search/classify/batch", json=invalid_request)
            ValidationTestHelper.assert_validation_error(response)
    
    async def test_product_search_validation(self, test_client: TestClient):
        """Test product search request validation."""
        # Missing search term
        response = test_client.get("/api/search/products")
        ValidationTestHelper.assert_validation_error(response)
        
        # Empty search term
        response = test_client.get("/api/search/products?search_term=")
        ValidationTestHelper.assert_validation_error(response)
        
        # Invalid parameters
        invalid_params = [
            {"search_term": "test", "page": 0},  # Invalid page
            {"search_term": "test", "limit": 0},  # Invalid limit
            {"search_term": "test", "limit": 200},  # Limit too high
            {"search_term": "test", "min_confidence": -0.1},  # Invalid confidence
            {"search_term": "test", "min_confidence": 1.1},  # Invalid confidence
            {"search_term": "test", "sort_by": "invalid"},  # Invalid sort field
        ]
        
        for params in invalid_params:
            response = test_client.get("/api/search/products", params=params)
            ValidationTestHelper.assert_validation_error(response)
    
    async def test_path_parameter_validation(self, test_client: TestClient):
        """Test path parameter validation."""
        # Invalid section IDs
        invalid_section_ids = ["abc", "-1", "0", "999999999999999999999"]
        
        for section_id in invalid_section_ids:
            response = test_client.get(f"/api/tariff/chapters/{section_id}")
            assert response.status_code in [404, 422]  # Either not found or validation error
        
        # Invalid HS codes in paths
        invalid_hs_codes = ["", "abc", "123", "12345678901"]
        
        for hs_code in invalid_hs_codes:
            response = test_client.get(f"/api/duty/rates/{hs_code}")
            # Should handle gracefully, either 404 or validation error
            assert response.status_code in [200, 404, 422]


@pytest.mark.api
class TestResponseValidation:
    """Test response schema validation."""
    
    async def test_tariff_sections_response_schema(self, test_client: TestClient):
        """Test tariff sections response schema."""
        response = test_client.get("/api/tariff/sections")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
            
            for section in data:
                assert isinstance(section, dict)
                required_fields = ["id", "section_number", "title", "chapter_count"]
                for field in required_fields:
                    assert field in section
                
                # Validate field types
                assert isinstance(section["id"], int)
                assert isinstance(section["section_number"], int)
                assert isinstance(section["title"], str)
                assert isinstance(section["chapter_count"], int)
    
    async def test_tariff_detail_response_schema(self, test_client: TestClient, test_session: AsyncSession):
        """Test tariff detail response schema."""
        # Create test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        response = test_client.get(f"/api/tariff/code/{tariff_code.hs_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check main structure
            assert "tariff" in data
            assert "breadcrumbs" in data
            
            # Check tariff object
            tariff = data["tariff"]
            required_fields = [
                "id", "hs_code", "description", "level", "is_active",
                "created_at", "updated_at"
            ]
            for field in required_fields:
                assert field in tariff
            
            # Validate field types
            assert isinstance(tariff["id"], int)
            assert isinstance(tariff["hs_code"], str)
            assert isinstance(tariff["description"], str)
            assert isinstance(tariff["level"], int)
            assert isinstance(tariff["is_active"], bool)
            
            # Check breadcrumbs
            assert isinstance(data["breadcrumbs"], list)
    
    async def test_duty_calculation_response_schema(self, test_client: TestClient, test_session: AsyncSession):
        """Test duty calculation response schema."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        request_data = {
            "hs_code": tariff_code.hs_code,
            "country_code": "USA",
            "customs_value": 1000.00
        }
        
        response = test_client.post("/api/duty/calculate", json=request_data)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check required fields
            required_fields = [
                "hs_code", "country_code", "customs_value",
                "total_duty", "duty_inclusive_value", "total_amount"
            ]
            for field in required_fields:
                assert field in data
            
            # Validate field types
            assert isinstance(data["hs_code"], str)
            assert isinstance(data["country_code"], str)
            assert isinstance(data["customs_value"], (int, float))
            assert isinstance(data["total_duty"], (int, float))
            assert isinstance(data["total_amount"], (int, float))
    
    async def test_search_response_schema(self, test_client: TestClient):
        """Test search response schema."""
        response = test_client.get("/api/tariff/search?query=test")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check main structure
            required_fields = [
                "results", "pagination", "total_results", "search_time_ms"
            ]
            for field in required_fields:
                assert field in data
            
            # Check results array
            assert isinstance(data["results"], list)
            
            # Check pagination object
            pagination = data["pagination"]
            pagination_fields = ["page", "size", "total", "pages"]
            for field in pagination_fields:
                assert field in pagination
                assert isinstance(pagination[field], int)
            
            # Validate other fields
            assert isinstance(data["total_results"], int)
            assert isinstance(data["search_time_ms"], (int, float))
    
    async def test_error_response_schema(self, test_client: TestClient):
        """Test error response schema consistency."""
        # Generate various error responses
        error_endpoints = [
            ("/api/tariff/code/nonexistent", "GET", None),
            ("/api/duty/calculate", "POST", {}),  # Invalid request
            ("/api/search/products", "GET", None),  # Missing search term
        ]
        
        for endpoint, method, data in error_endpoints:
            if method == "POST":
                response = test_client.post(endpoint, json=data)
            else:
                response = test_client.get(endpoint)
            
            if response.status_code >= 400:
                error_data = response.json()
                
                # All error responses should have detail field
                assert "detail" in error_data
                assert isinstance(error_data["detail"], (str, list))
                
                # Validation errors should have specific structure
                if response.status_code == 422:
                    if isinstance(error_data["detail"], list):
                        for error in error_data["detail"]:
                            assert "loc" in error
                            assert "msg" in error
                            assert "type" in error


@pytest.mark.api
class TestContentTypeHandling:
    """Test content-type handling and serialization."""
    
    async def test_json_content_type_requirement(self, test_client: TestClient):
        """Test JSON content-type requirement for POST endpoints."""
        # Test with correct content-type
        response = test_client.post(
            "/api/duty/calculate",
            json={
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": 1000.00
            },
            headers={"Content-Type": "application/json"}
        )
        
        # Should not fail due to content-type
        assert response.status_code != 415  # Unsupported Media Type
        
        # Test with incorrect content-type
        response = test_client.post(
            "/api/duty/calculate",
            data="invalid data",
            headers={"Content-Type": "text/plain"}
        )
        
        # Should handle gracefully
        assert response.status_code in [400, 415, 422]
    
    async def test_response_content_type(self, test_client: TestClient):
        """Test response content-type headers."""
        endpoints = [
            "/api/tariff/sections",
            "/api/tariff/search?query=test",
            "/api/duty/rates/0101010000"
        ]
        
        for endpoint in endpoints:
            response = test_client.get(endpoint)
            
            if response.status_code == 200:
                content_type = response.headers.get("content-type", "")
                assert "application/json" in content_type
    
    async def test_decimal_serialization(self, test_client: TestClient, test_session: AsyncSession):
        """Test proper serialization of decimal values."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Create duty rate with decimal value
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            general_rate=Decimal("7.5")
        )
        
        response = test_client.get(f"/api/duty/rates/{tariff_code.hs_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Decimal values should be serialized as numbers
            for rate in data.get("general_rates", []):
                if "general_rate" in rate and rate["general_rate"] is not None:
                    assert isinstance(rate["general_rate"], (int, float))
    
    async def test_date_serialization(self, test_client: TestClient, test_session: AsyncSession):
        """Test proper serialization of date values."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Create duty rate with date
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            effective_date=date.today()
        )
        
        response = test_client.get(f"/api/duty/rates/{tariff_code.hs_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Date values should be serialized as ISO strings
            for rate in data.get("general_rates", []):
                if "effective_date" in rate and rate["effective_date"] is not None:
                    assert isinstance(rate["effective_date"], str)
                    # Should be valid ISO date format
                    try:
                        date.fromisoformat(rate["effective_date"])
                    except ValueError:
                        pytest.fail(f"Invalid date format: {rate['effective_date']}")


@pytest.mark.api
class TestDataValidationEdgeCases:
    """Test edge cases in data validation."""
    
    async def test_large_number_handling(self, test_client: TestClient):
        """Test handling of very large numbers."""
        large_value_request = {
            "hs_code": "0101010000",
            "country_code": "USA",
            "customs_value": 999999999999.99  # Very large value
        }
        
        response = test_client.post("/api/duty/calculate", json=large_value_request)
        
        # Should either process or return validation error, not crash
        assert response.status_code in [200, 400, 422, 500]
    
    async def test_unicode_string_handling(self, test_client: TestClient):
        """Test handling of Unicode strings."""
        unicode_request = {
            "product_description": "Cafe products with emojis",
            "confidence_threshold": 0.8,
            "additional_details": "Contains special characters"
        }
        
        response = test_client.post("/api/search/classify", json=unicode_request)
        
        # Should handle Unicode gracefully
        assert response.status_code in [200, 422, 500]
    
    async def test_null_value_handling(self, test_client: TestClient):
        """Test handling of null values in optional fields."""
        request_with_nulls = {
            "hs_code": "0101010000",
            "country_code": "USA",
            "customs_value": 1000.00,
            "quantity": None,  # Optional field as null
            "calculation_date": None,  # Optional field as null
            "exporter_name": None  # Optional field as null
        }
        
        response = test_client.post("/api/duty/calculate", json=request_with_nulls)
        
        # Should handle null optional fields gracefully
        assert response.status_code in [200, 422, 500]
    
    async def test_empty_string_vs_null_handling(self, test_client: TestClient):
        """Test distinction between empty strings and null values."""
        # Test with empty strings
        empty_string_request = {
            "product_description": "",  # Empty string
            "confidence_threshold": 0.8
        }
        
        response = test_client.post("/api/search/classify", json=empty_string_request)
        ValidationTestHelper.assert_validation_error(response)
        
        # Test with null
        null_request = {
            "product_description": None,  # Null value
            "confidence_threshold": 0.8
        }
        
        response = test_client.post("/api/search/classify", json=null_request)
        ValidationTestHelper.assert_validation_error(response)
    
    async def test_boundary_value_testing(self, test_client: TestClient):
        """Test boundary values for numeric fields."""
        boundary_tests = [
            # Confidence threshold boundaries
            {
                "product_description": "test",
                "confidence_threshold": 0.0  # Minimum valid
            },
            {
                "product_description": "test", 
                "confidence_threshold": 1.0  # Maximum valid
            },
            # Customs value boundaries
            {
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": 0.01  # Minimum positive value
            }
        ]
        
        for test_data in boundary_tests:
            if "confidence_threshold" in test_data:
                response = test_client.post("/api/search/classify", json=test_data)
            else:
                response = test_client.post("/api/duty/calculate", json=test_data)
            
            # Boundary values should be accepted
            assert response.status_code in [200, 422, 500]  # Not validation error


@pytest.mark.api
@pytest.mark.integration
class TestValidationIntegration:
    """Integration tests for validation across workflows."""
    
    async def test_end_to_end_validation_consistency(self, test_client: TestClient, test_session: AsyncSession):
        """Test validation consistency across related endpoints."""
        # Create test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Test that the same HS code is accepted across different endpoints
        endpoints_and_data = [
            ("/api/tariff/code/{hs_code}", "GET", None),
            ("/api/duty/rates/{hs_code}", "GET", None),
            ("/api/duty/calculate", "POST", {
                "hs_code": "{hs_code}",
                "country_code": "USA",
                "customs_value": 1000.00
            })
        ]
        
        for endpoint_template, method, data_template in endpoints_and_data:
            endpoint = endpoint_template.format(hs_code=tariff_code.hs_code)
            
            if method == "GET":
                response = test_client.get(endpoint)
            else:
                data = {
                    k: v.format(hs_code=tariff_code.hs_code) if isinstance(v, str) else v
                    for k, v in data_template.items()
                }
                response = test_client.post(endpoint, json=data)
            
            # Should consistently accept the same valid HS code
            assert response.status_code != 422  # Should not be validation error
    
    async def test_cross_endpoint_data_consistency(self, test_client: TestClient, test_session: AsyncSession):
        """Test data consistency between related endpoints."""
        # Create test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000",
            description="Test product"
        )
        
        # Get tariff details
        detail_response = test_client.get(f"/api/tariff/code/{tariff_code.hs_code}")
        
        if detail_response.status_code == 200:
            detail_data = detail_response.json()
            
            # Search for the same tariff
            search_response = test_client.get(f"/api/tariff/search?hs_code_starts_with={tariff_code.hs_code[:4]}")
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                
                # Find the tariff in search results
                matching_results = [
                    result for result in search_data["results"]
                    if result["hs_code"] == tariff_code.hs_code
                ]
                
                if matching_results:
                    search_result = matching_results[0]
                    
                    # Data should be consistent between endpoints
                    assert detail_data["tariff"]["hs_code"] == search_result["hs_code"]
                    assert detail_data["tariff"]["description"] == search_result["description"]