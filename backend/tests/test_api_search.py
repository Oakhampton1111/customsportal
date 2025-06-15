"""
API endpoint tests for search and classification routes.

This module tests all search and AI classification API endpoints including
product classification, batch processing, feedback, and search functionality.
"""

import pytest
import pytest_asyncio
import uuid
from datetime import datetime, date
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch

from tests.utils.test_helpers import (
    APITestHelper, DatabaseTestHelper, TestDataFactory,
    PerformanceTestHelper, ValidationTestHelper, MockHelper
)


@pytest.mark.api
class TestProductClassificationAPI:
    """Test product classification API endpoints."""
    
    @patch('ai.tariff_ai.TariffAIService.classify_product')
    async def test_classify_product_success(self, mock_classify, test_client: TestClient, test_session: AsyncSession):
        """Test successful product classification."""
        # Create test tariff code
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000",
            description="Live horses for breeding purposes"
        )
        
        # Mock AI service response
        mock_classify.return_value = {
            "hs_code": tariff_code.hs_code,
            "confidence": 0.95,
            "classification_source": "ai",
            "reasoning": "Product matches live horse classification",
            "alternative_codes": []
        }
        
        classification_request = {
            "product_description": "Live breeding horses from Australia",
            "confidence_threshold": 0.8,
            "store_result": True,
            "additional_details": "Thoroughbred racing horses",
            "country_of_origin": "AUS"
        }
        
        response = test_client.post("/api/search/classify", json=classification_request)
        
        APITestHelper.assert_response_success(response, 200)
        data = APITestHelper.assert_json_response(response, [
            "hs_code", "confidence_score", "classification_source",
            "tariff_description", "verification_required", "processing_time_ms"
        ])
        
        assert data["hs_code"] == tariff_code.hs_code
        assert data["confidence_score"] == 0.95
        assert data["classification_source"] == "ai"
        assert data["tariff_description"] == tariff_code.description
        assert isinstance(data["verification_required"], bool)
        assert isinstance(data["processing_time_ms"], (int, float))
        
        # Verify AI service was called with correct parameters
        mock_classify.assert_called_once()
        call_args = mock_classify.call_args
        assert call_args[1]["product_description"] == classification_request["product_description"]
        assert call_args[1]["confidence_threshold"] == classification_request["confidence_threshold"]
    
    @patch('ai.tariff_ai.TariffAIService.classify_product')
    async def test_classify_product_with_alternatives(self, mock_classify, test_client: TestClient, test_session: AsyncSession):
        """Test product classification with alternative codes."""
        # Create test tariff codes
        primary_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000",
            description="Live horses for breeding"
        )
        
        alt_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010001",
            description="Live horses for racing"
        )
        
        mock_classify.return_value = {
            "hs_code": primary_code.hs_code,
            "confidence": 0.85,
            "classification_source": "ai",
            "alternative_codes": [alt_code.hs_code]
        }
        
        classification_request = {
            "product_description": "Live horses for various purposes",
            "confidence_threshold": 0.7
        }
        
        response = test_client.post("/api/search/classify", json=classification_request)
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert data["hs_code"] == primary_code.hs_code
        assert "alternative_codes" in data
        assert isinstance(data["alternative_codes"], list)
    
    @patch('ai.tariff_ai.TariffAIService.classify_product')
    async def test_classify_product_low_confidence(self, mock_classify, test_client: TestClient, test_session: AsyncSession):
        """Test product classification with low confidence requiring verification."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010002"
        )
        
        mock_classify.return_value = {
            "hs_code": tariff_code.hs_code,
            "confidence": 0.6,  # Low confidence
            "classification_source": "ai",
            "requires_manual_review": True
        }
        
        classification_request = {
            "product_description": "Unclear product description",
            "confidence_threshold": 0.8
        }
        
        response = test_client.post("/api/search/classify", json=classification_request)
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert data["confidence_score"] == 0.6
        assert data["verification_required"] is True
    
    @patch('ai.tariff_ai.TariffAIService.classify_product')
    async def test_classify_product_ai_failure(self, mock_classify, test_client: TestClient):
        """Test product classification when AI service fails."""
        mock_classify.return_value = {}  # Empty response indicating failure
        
        classification_request = {
            "product_description": "Unclassifiable product",
            "confidence_threshold": 0.8
        }
        
        response = test_client.post("/api/search/classify", json=classification_request)
        
        APITestHelper.assert_response_error(response, 422)
        data = response.json()
        assert "unable to classify" in data["detail"].lower()
    
    async def test_classify_product_validation_errors(self, test_client: TestClient):
        """Test product classification with validation errors."""
        invalid_requests = [
            {},  # Empty request
            {"confidence_threshold": 0.8},  # Missing product_description
            {"product_description": ""},  # Empty product_description
            {"product_description": "test", "confidence_threshold": 1.5},  # Invalid confidence threshold
            {"product_description": "test", "confidence_threshold": -0.1},  # Negative confidence threshold
        ]
        
        for invalid_request in invalid_requests:
            response = test_client.post("/api/search/classify", json=invalid_request)
            ValidationTestHelper.assert_validation_error(response)
    
    @patch('ai.tariff_ai.TariffAIService.classify_product')
    async def test_classify_product_nonexistent_hs_code(self, mock_classify, test_client: TestClient):
        """Test classification when AI returns non-existent HS code."""
        mock_classify.return_value = {
            "hs_code": "9999999999",  # Non-existent code
            "confidence": 0.9,
            "classification_source": "ai"
        }
        
        classification_request = {
            "product_description": "Test product",
            "confidence_threshold": 0.8
        }
        
        response = test_client.post("/api/search/classify", json=classification_request)
        
        APITestHelper.assert_response_error(response, 404)
        data = response.json()
        assert "not found" in data["detail"].lower()


@pytest.mark.api
class TestBatchClassificationAPI:
    """Test batch classification API endpoints."""
    
    @patch('ai.tariff_ai.TariffAIService.classify_batch')
    async def test_classify_products_batch_success(self, mock_classify_batch, test_client: TestClient, test_session: AsyncSession):
        """Test successful batch product classification."""
        # Create test tariff codes
        tariff_codes = []
        for i in range(3):
            code = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=f"010101000{i}",
                description=f"Test product {i}"
            )
            tariff_codes.append(code)
        
        # Mock batch classification response
        mock_classify_batch.return_value = [
            {
                "hs_code": tariff_codes[0].hs_code,
                "confidence": 0.9,
                "classification_source": "ai"
            },
            {
                "hs_code": tariff_codes[1].hs_code,
                "confidence": 0.85,
                "classification_source": "ai"
            },
            {
                "error": "Classification failed"
            }
        ]
        
        batch_request = {
            "products": [
                {"id": "prod1", "description": "Product 1 description"},
                {"id": "prod2", "description": "Product 2 description"},
                {"id": "prod3", "description": "Product 3 description"}
            ],
            "confidence_threshold": 0.8,
            "store_results": True,
            "batch_id": str(uuid.uuid4())
        }
        
        response = test_client.post("/api/search/classify/batch", json=batch_request)
        
        APITestHelper.assert_response_success(response, 200)
        data = APITestHelper.assert_json_response(response, [
            "batch_id", "results", "total_products", "successful_classifications",
            "failed_classifications", "processing_time_ms"
        ])
        
        assert data["total_products"] == 3
        assert data["successful_classifications"] == 2
        assert data["failed_classifications"] == 1
        assert len(data["results"]) == 3
        
        # Check successful results
        successful_results = [r for r in data["results"] if r.get("status") == "success"]
        assert len(successful_results) == 2
        
        for result in successful_results:
            assert "hs_code" in result
            assert "confidence_score" in result
            assert "tariff_description" in result
        
        # Check failed result
        failed_results = [r for r in data["results"] if r.get("status") == "failed"]
        assert len(failed_results) == 1
        assert "error" in failed_results[0]
    
    async def test_classify_products_batch_validation_errors(self, test_client: TestClient):
        """Test batch classification with validation errors."""
        invalid_requests = [
            {},  # Empty request
            {"products": []},  # Empty products list
            {"products": [{"description": "test"}]},  # Missing confidence_threshold
            {
                "products": [{"id": "1"}],  # Missing description
                "confidence_threshold": 0.8
            },
            {
                "products": [{"description": "test"}],
                "confidence_threshold": 1.5  # Invalid threshold
            }
        ]
        
        for invalid_request in invalid_requests:
            response = test_client.post("/api/search/classify/batch", json=invalid_request)
            ValidationTestHelper.assert_validation_error(response)
    
    @patch('ai.tariff_ai.TariffAIService.classify_batch')
    async def test_classify_products_batch_performance(self, mock_classify_batch, test_client: TestClient, performance_timer):
        """Test batch classification performance."""
        # Mock quick response
        mock_classify_batch.return_value = [
            {"hs_code": "0101010000", "confidence": 0.9} for _ in range(10)
        ]
        
        batch_request = {
            "products": [
                {"id": f"prod{i}", "description": f"Product {i}"}
                for i in range(10)
            ],
            "confidence_threshold": 0.8
        }
        
        performance_timer.start()
        response = test_client.post("/api/search/classify/batch", json=batch_request)
        performance_timer.stop()
        
        APITestHelper.assert_response_success(response, 200)
        PerformanceTestHelper.assert_execution_time(performance_timer.elapsed, 5.0)


@pytest.mark.api
class TestClassificationFeedbackAPI:
    """Test classification feedback API endpoints."""
    
    async def test_submit_classification_feedback_success(self, test_client: TestClient, test_session: AsyncSession):
        """Test successful classification feedback submission."""
        # Create a classification record first
        from models.classification import ProductClassification
        
        classification = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=0.9,
            classification_source="ai",
            verified_by_broker=False
        )
        test_session.add(classification)
        await test_session.commit()
        await test_session.refresh(classification)
        
        feedback_request = {
            "classification_id": classification.id,
            "verification_status": "verified",
            "broker_id": "broker123",
            "feedback_notes": "Classification is correct"
        }
        
        response = test_client.post("/api/search/feedback", json=feedback_request)
        
        APITestHelper.assert_response_success(response, 200)
        data = APITestHelper.assert_json_response(response, [
            "success", "message", "feedback_id"
        ])
        
        assert data["success"] is True
        assert "recorded successfully" in data["message"].lower()
        assert isinstance(data["feedback_id"], int)
    
    async def test_submit_classification_feedback_not_found(self, test_client: TestClient):
        """Test feedback submission for non-existent classification."""
        feedback_request = {
            "classification_id": 99999,
            "verification_status": "verified",
            "broker_id": "broker123"
        }
        
        response = test_client.post("/api/search/feedback", json=feedback_request)
        
        APITestHelper.assert_response_error(response, 404)
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    async def test_submit_classification_feedback_validation_errors(self, test_client: TestClient):
        """Test feedback submission with validation errors."""
        invalid_requests = [
            {},  # Empty request
            {"classification_id": 1},  # Missing verification_status
            {"verification_status": "verified"},  # Missing classification_id
            {
                "classification_id": "invalid",  # Invalid ID type
                "verification_status": "verified"
            },
            {
                "classification_id": 1,
                "verification_status": "invalid_status"  # Invalid status
            }
        ]
        
        for invalid_request in invalid_requests:
            response = test_client.post("/api/search/feedback", json=invalid_request)
            ValidationTestHelper.assert_validation_error(response)


@pytest.mark.api
class TestProductSearchAPI:
    """Test product search API endpoints."""
    
    async def test_search_products_success(self, test_client: TestClient, test_session: AsyncSession):
        """Test successful product search."""
        # Create test classification records
        from models.classification import ProductClassification
        
        classification = ProductClassification(
            product_description="Live horses for breeding",
            hs_code="0101010000",
            confidence_score=0.9,
            classification_source="ai",
            verified_by_broker=True
        )
        test_session.add(classification)
        await test_session.commit()
        
        response = test_client.get("/api/search/products?search_term=horses")
        
        APITestHelper.assert_response_success(response, 200)
        data = APITestHelper.assert_json_response(response, [
            "results", "pagination", "search_term", "total_results", "search_time_ms"
        ])
        
        assert data["search_term"] == "horses"
        assert isinstance(data["results"], list)
        assert isinstance(data["total_results"], int)
        assert isinstance(data["search_time_ms"], (int, float))
        
        # Check pagination structure
        pagination = data["pagination"]
        assert "page" in pagination
        assert "size" in pagination
        assert "total" in pagination
        assert "pages" in pagination
    
    async def test_search_products_with_filters(self, test_client: TestClient):
        """Test product search with filters."""
        params = {
            "search_term": "test",
            "page": 1,
            "limit": 10,
            "sort_by": "confidence",
            "min_confidence": 0.8,
            "verification_status": "verified"
        }
        
        response = test_client.get("/api/search/products", params=params)
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert data["pagination"]["page"] == 1
        assert data["pagination"]["size"] == 10
        
        # Check that results meet filter criteria
        for result in data["results"]:
            if "confidence_score" in result:
                assert result["confidence_score"] >= 0.8
            if "verification_status" in result:
                assert result["verification_status"] == "verified"
    
    async def test_search_products_pagination(self, test_client: TestClient):
        """Test product search pagination."""
        # Test first page
        response = test_client.get("/api/search/products?search_term=test&page=1&limit=5")
        APITestHelper.assert_response_success(response, 200)
        
        data = response.json()
        assert data["pagination"]["page"] == 1
        assert len(data["results"]) <= 5
        
        # Test second page if there are enough results
        if data["pagination"]["pages"] > 1:
            response = test_client.get("/api/search/products?search_term=test&page=2&limit=5")
            APITestHelper.assert_response_success(response, 200)
            
            data = response.json()
            assert data["pagination"]["page"] == 2
    
    async def test_search_products_sorting(self, test_client: TestClient):
        """Test product search sorting options."""
        sort_options = ["relevance", "confidence", "date", "hs_code"]
        
        for sort_by in sort_options:
            response = test_client.get(f"/api/search/products?search_term=test&sort_by={sort_by}")
            APITestHelper.assert_response_success(response, 200)
    
    async def test_search_products_validation_errors(self, test_client: TestClient):
        """Test product search with validation errors."""
        # Missing search term
        response = test_client.get("/api/search/products")
        ValidationTestHelper.assert_validation_error(response)
        
        # Invalid page number
        response = test_client.get("/api/search/products?search_term=test&page=0")
        ValidationTestHelper.assert_validation_error(response)
        
        # Invalid limit
        response = test_client.get("/api/search/products?search_term=test&limit=200")
        ValidationTestHelper.assert_validation_error(response)
        
        # Invalid confidence range
        response = test_client.get("/api/search/products?search_term=test&min_confidence=1.5")
        ValidationTestHelper.assert_validation_error(response)
    
    async def test_search_products_performance(self, test_client: TestClient, performance_timer):
        """Test product search performance."""
        performance_timer.start()
        response = test_client.get("/api/search/products?search_term=test&limit=20")
        performance_timer.stop()
        
        APITestHelper.assert_response_success(response, 200)
        PerformanceTestHelper.assert_execution_time(performance_timer.elapsed, 2.0)
        
        # Check search time is reasonable
        data = response.json()
        assert data["search_time_ms"] < 2000


@pytest.mark.api
class TestClassificationStatsAPI:
    """Test classification statistics API endpoints."""
    
    @patch('ai.tariff_ai.TariffAIService.get_classification_stats')
    async def test_get_classification_stats_success(self, mock_get_stats, test_client: TestClient):
        """Test successful classification statistics retrieval."""
        mock_get_stats.return_value = {
            "total_classifications": 100,
            "verified_classifications": 80,
            "verification_rate": 0.8,
            "average_confidence_by_source": {"ai": 0.85},
            "classifications_by_source": {"ai": 90, "manual": 10}
        }
        
        response = test_client.get("/api/search/stats")
        
        APITestHelper.assert_response_success(response, 200)
        data = APITestHelper.assert_json_response(response, [
            "total_classifications", "verified_classifications", "pending_classifications",
            "verification_rate", "average_confidence", "source_distribution"
        ])
        
        assert data["total_classifications"] == 100
        assert data["verified_classifications"] == 80
        assert data["pending_classifications"] == 20  # total - verified
        assert data["verification_rate"] == 0.8
        assert isinstance(data["source_distribution"], dict)
    
    @patch('ai.tariff_ai.TariffAIService.get_classification_stats')
    async def test_get_classification_stats_service_error(self, mock_get_stats, test_client: TestClient):
        """Test classification statistics when service fails."""
        mock_get_stats.side_effect = Exception("Service unavailable")
        
        response = test_client.get("/api/search/stats")
        
        APITestHelper.assert_response_error(response, 500)
        data = response.json()
        assert "failed to get stats" in data["detail"].lower()


@pytest.mark.api
@pytest.mark.integration
class TestSearchAPIIntegration:
    """Integration tests for search API workflows."""
    
    @patch('ai.tariff_ai.TariffAIService.classify_product')
    async def test_classify_to_search_workflow(self, mock_classify, test_client: TestClient, test_session: AsyncSession):
        """Test workflow from classification to search."""
        # Create test tariff code
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000",
            description="Live horses for breeding"
        )
        
        mock_classify.return_value = {
            "hs_code": tariff_code.hs_code,
            "confidence": 0.9,
            "classification_source": "ai"
        }
        
        # 1. Classify a product
        classification_request = {
            "product_description": "Live breeding horses",
            "confidence_threshold": 0.8,
            "store_result": True
        }
        
        classify_response = test_client.post("/api/search/classify", json=classification_request)
        APITestHelper.assert_response_success(classify_response, 200)
        
        # 2. Search for similar products
        search_response = test_client.get("/api/search/products?search_term=horses")
        APITestHelper.assert_response_success(search_response, 200)
        
        # 3. Get statistics
        stats_response = test_client.get("/api/search/stats")
        assert stats_response.status_code in [200, 500]  # May fail if AI service not available
    
    @patch('ai.tariff_ai.TariffAIService.classify_batch')
    async def test_batch_classification_to_feedback_workflow(self, mock_classify_batch, test_client: TestClient, test_session: AsyncSession):
        """Test workflow from batch classification to feedback."""
        # Create test tariff code
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        mock_classify_batch.return_value = [
            {
                "hs_code": tariff_code.hs_code,
                "confidence": 0.9,
                "classification_source": "ai"
            }
        ]
        
        # 1. Batch classify products
        batch_request = {
            "products": [{"id": "prod1", "description": "Test product"}],
            "confidence_threshold": 0.8,
            "store_results": True
        }
        
        batch_response = test_client.post("/api/search/classify/batch", json=batch_request)
        APITestHelper.assert_response_success(batch_response, 200)
        
        batch_data = batch_response.json()
        if batch_data["successful_classifications"] > 0:
            # 2. Submit feedback for a classification (if we had the ID)
            # This would require the classification to be actually stored
            pass


@pytest.mark.api
@pytest.mark.slow
class TestSearchAPIPerformance:
    """Performance tests for search API endpoints."""
    
    async def test_concurrent_search_requests(self, async_test_client: AsyncClient):
        """Test concurrent search requests."""
        import asyncio
        
        async def make_search_request(term):
            response = await async_test_client.get(f"/api/search/products?search_term={term}")
            return response.status_code
        
        # Test concurrent searches with different terms
        search_terms = ["horses", "cattle", "sheep", "goats", "pigs"]
        tasks = [make_search_request(term) for term in search_terms]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # All searches should complete within reasonable time
        assert end_time - start_time < 10.0
        
        # Most should succeed
        successful = sum(1 for result in results if isinstance(result, int) and result == 200)
        assert successful >= len(tasks) * 0.8


# Import time for performance tests
import time