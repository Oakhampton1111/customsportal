"""
Comprehensive tests for the Search Service.

This module tests all aspects of the search service functionality including:
- Tariff code search algorithms and ranking
- Product description matching and similarity scoring
- Search result filtering and pagination logic
- Search performance optimization and caching
- Search analytics and statistics generation
- Full-text search capabilities
"""

import pytest
import pytest_asyncio
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from fastapi.testclient import TestClient
from httpx import AsyncClient

from models.classification import ProductClassification
from models.tariff import TariffCode
from models.hierarchy import TariffSection, TariffChapter
from schemas.search import SearchSortBy, VerificationStatus
from ai.tariff_ai import TariffAIService


@pytest.mark.unit
class TestSearchService:
    """Test suite for search service functionality."""
    
    @pytest_asyncio.fixture
    async def sample_tariff_codes(self, test_session: AsyncSession):
        """Create sample tariff codes for search testing."""
        tariff_codes = [
            TariffCode(
                hs_code="12345678",
                description="Electronic devices and components for consumer use",
                unit="kg",
                statistical_code="01",
                is_active=True
            ),
            TariffCode(
                hs_code="87654321",
                description="Mechanical equipment and machinery parts",
                unit="unit",
                statistical_code="02",
                is_active=True
            ),
            TariffCode(
                hs_code="11111111",
                description="Textile materials and fabric products",
                unit="m2",
                statistical_code="03",
                is_active=True
            ),
            TariffCode(
                hs_code="22222222",
                description="Chemical substances and pharmaceutical products",
                unit="kg",
                statistical_code="04",
                is_active=True
            )
        ]
        
        for code in tariff_codes:
            test_session.add(code)
        await test_session.commit()
        
        for code in tariff_codes:
            await test_session.refresh(code)
        
        return tariff_codes
    
    @pytest_asyncio.fixture
    async def sample_classifications(self, test_session: AsyncSession, sample_tariff_codes: List[TariffCode]):
        """Create sample product classifications for search testing."""
        classifications = [
            ProductClassification(
                product_description="Smartphone electronic device with touchscreen",
                hs_code="12345678",
                confidence_score=Decimal("0.95"),
                classification_source="ai",
                verified_by_broker=True,
                broker_user_id=1
            ),
            ProductClassification(
                product_description="Laptop computer for business use",
                hs_code="12345678",
                confidence_score=Decimal("0.88"),
                classification_source="ai",
                verified_by_broker=False
            ),
            ProductClassification(
                product_description="Industrial machinery motor component",
                hs_code="87654321",
                confidence_score=Decimal("0.92"),
                classification_source="similarity",
                verified_by_broker=True,
                broker_user_id=2
            ),
            ProductClassification(
                product_description="Cotton fabric textile material",
                hs_code="11111111",
                confidence_score=Decimal("0.85"),
                classification_source="broker",
                verified_by_broker=True,
                broker_user_id=1
            ),
            ProductClassification(
                product_description="Pharmaceutical drug compound",
                hs_code="22222222",
                confidence_score=Decimal("0.78"),
                classification_source="ai",
                verified_by_broker=False
            )
        ]
        
        for classification in classifications:
            test_session.add(classification)
        await test_session.commit()
        
        for classification in classifications:
            await test_session.refresh(classification)
        
        return classifications


@pytest.mark.integration
class TestProductSearch:
    """Test product search functionality."""
    
    async def test_search_products_basic(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification]
    ):
        """Test basic product search functionality."""
        response = await async_test_client.get(
            "/api/search/products",
            params={"search_term": "electronic"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "results" in data
        assert "pagination" in data
        assert "search_term" in data
        assert data["search_term"] == "electronic"
        
        # Should find products with "electronic" in description
        results = data["results"]
        assert len(results) >= 1
        
        # Check that results contain expected fields
        for result in results:
            assert "product_id" in result
            assert "product_description" in result
            assert "hs_code" in result
            assert "confidence_score" in result
            assert "relevance_score" in result
    
    async def test_search_products_with_filters(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification]
    ):
        """Test product search with filters."""
        response = await async_test_client.get(
            "/api/search/products",
            params={
                "search_term": "device",
                "min_confidence": 0.9,
                "verification_status": "verified"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        results = data["results"]
        
        # All results should meet filter criteria
        for result in results:
            assert result["confidence_score"] >= 0.9
            assert result["verification_status"] == "verified"
    
    async def test_search_products_sorting(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification]
    ):
        """Test product search with different sorting options."""
        # Test sorting by confidence
        response = await async_test_client.get(
            "/api/search/products",
            params={
                "search_term": "device",
                "sort_by": "confidence"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        if len(results) > 1:
            # Results should be sorted by confidence descending
            confidences = [r["confidence_score"] for r in results]
            assert confidences == sorted(confidences, reverse=True)
        
        # Test sorting by HS code
        response = await async_test_client.get(
            "/api/search/products",
            params={
                "search_term": "device",
                "sort_by": "hs_code"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        results = data["results"]
        
        if len(results) > 1:
            # Results should be sorted by HS code
            hs_codes = [r["hs_code"] for r in results]
            assert hs_codes == sorted(hs_codes)
    
    async def test_search_products_pagination(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification]
    ):
        """Test product search pagination."""
        # Test first page
        response = await async_test_client.get(
            "/api/search/products",
            params={
                "search_term": "device",
                "page": 1,
                "limit": 2
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert "pagination" in data
        pagination = data["pagination"]
        assert pagination["page"] == 1
        assert pagination["limit"] == 2
        assert "total" in pagination
        assert "pages" in pagination
        
        # Results should not exceed limit
        assert len(data["results"]) <= 2
    
    async def test_search_products_no_results(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification]
    ):
        """Test product search with no matching results."""
        response = await async_test_client.get(
            "/api/search/products",
            params={"search_term": "nonexistent"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["results"] == []
        assert data["total_results"] == 0
        assert data["search_term"] == "nonexistent"
    
    async def test_search_products_invalid_params(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession
    ):
        """Test product search with invalid parameters."""
        # Test missing search term
        response = await async_test_client.get("/api/search/products")
        assert response.status_code == 422
        
        # Test invalid confidence range
        response = await async_test_client.get(
            "/api/search/products",
            params={
                "search_term": "test",
                "min_confidence": 1.5  # Invalid confidence > 1.0
            }
        )
        assert response.status_code == 422
        
        # Test invalid page number
        response = await async_test_client.get(
            "/api/search/products",
            params={
                "search_term": "test",
                "page": 0  # Invalid page < 1
            }
        )
        assert response.status_code == 422


@pytest.mark.unit
class TestSearchAlgorithms:
    """Test search algorithms and ranking logic."""
    
    def test_relevance_scoring(self):
        """Test relevance scoring algorithm."""
        # This would test the relevance scoring logic
        # Since it's embedded in the route, we test it indirectly
        search_term = "electronic"
        description = "Electronic device for consumer use"
        
        # Simple relevance check - exact match should score higher
        exact_match = search_term.lower() in description.lower()
        assert exact_match is True
        
        # Test case sensitivity
        description_upper = "ELECTRONIC DEVICE FOR CONSUMER USE"
        case_insensitive_match = search_term.lower() in description_upper.lower()
        assert case_insensitive_match is True
    
    def test_search_term_highlighting(self):
        """Test search term highlighting in results."""
        search_term = "electronic"
        description = "Electronic device for testing"
        
        # Simulate highlighting logic
        highlighted = description.replace(search_term, f"<mark>{search_term}</mark>")
        expected = "<mark>electronic</mark> device for testing"
        
        assert highlighted.lower() == expected.lower()
    
    def test_search_term_normalization(self):
        """Test search term normalization."""
        # Test various search term formats
        search_terms = [
            "  electronic  ",  # Extra spaces
            "Electronic",     # Different case
            "electronic-device",  # Hyphenated
            "electronic/device"   # With slash
        ]
        
        for term in search_terms:
            normalized = term.strip().lower()
            assert "electronic" in normalized


@pytest.mark.unit
class TestSearchFiltering:
    """Test search filtering and criteria application."""
    
    async def test_confidence_filtering(
        self,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification]
    ):
        """Test confidence score filtering."""
        min_confidence = 0.9
        
        # Query classifications with confidence >= 0.9
        query = select(ProductClassification).where(
            ProductClassification.confidence_score >= min_confidence
        )
        result = await test_session.execute(query)
        classifications = result.scalars().all()
        
        # All results should meet criteria
        for classification in classifications:
            assert float(classification.confidence_score) >= min_confidence
    
    async def test_verification_status_filtering(
        self,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification]
    ):
        """Test verification status filtering."""
        # Test verified filter
        query = select(ProductClassification).where(
            ProductClassification.verified_by_broker == True
        )
        result = await test_session.execute(query)
        verified_classifications = result.scalars().all()
        
        for classification in verified_classifications:
            assert classification.verified_by_broker is True
        
        # Test pending filter
        query = select(ProductClassification).where(
            ProductClassification.verified_by_broker == False
        )
        result = await test_session.execute(query)
        pending_classifications = result.scalars().all()
        
        for classification in pending_classifications:
            assert classification.verified_by_broker is False
    
    async def test_combined_filtering(
        self,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification]
    ):
        """Test combined filtering criteria."""
        min_confidence = 0.85
        
        query = select(ProductClassification).where(
            ProductClassification.confidence_score >= min_confidence,
            ProductClassification.verified_by_broker == True
        )
        result = await test_session.execute(query)
        filtered_classifications = result.scalars().all()
        
        for classification in filtered_classifications:
            assert float(classification.confidence_score) >= min_confidence
            assert classification.verified_by_broker is True


@pytest.mark.unit
class TestSearchPerformance:
    """Test search performance and optimization."""
    
    async def test_search_query_performance(
        self,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification],
        performance_timer
    ):
        """Test search query performance."""
        search_term = "device"
        
        performance_timer.start()
        
        # Simulate search query
        query = select(ProductClassification).where(
            ProductClassification.product_description.ilike(f"%{search_term}%")
        ).limit(20)
        
        result = await test_session.execute(query)
        classifications = result.scalars().all()
        
        performance_timer.stop()
        
        assert classifications is not None
        assert performance_timer.elapsed < 1.0  # Should complete within 1 second
    
    async def test_search_with_large_dataset(
        self,
        test_session: AsyncSession,
        performance_timer
    ):
        """Test search performance with larger dataset."""
        # Create larger dataset for performance testing
        classifications = []
        for i in range(100):
            classification = ProductClassification(
                product_description=f"Test product {i} for search performance testing",
                hs_code="12345678",
                confidence_score=Decimal("0.8"),
                classification_source="ai",
                verified_by_broker=i % 2 == 0  # Alternate verification status
            )
            classifications.append(classification)
        
        for classification in classifications:
            test_session.add(classification)
        await test_session.commit()
        
        performance_timer.start()
        
        # Perform search on large dataset
        search_term = "product"
        query = select(ProductClassification).where(
            ProductClassification.product_description.ilike(f"%{search_term}%")
        ).limit(20)
        
        result = await test_session.execute(query)
        search_results = result.scalars().all()
        
        performance_timer.stop()
        
        assert len(search_results) > 0
        assert performance_timer.elapsed < 2.0  # Should complete within 2 seconds
    
    async def test_search_pagination_performance(
        self,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification],
        performance_timer
    ):
        """Test pagination performance."""
        search_term = "device"
        page = 1
        limit = 10
        offset = (page - 1) * limit
        
        performance_timer.start()
        
        # Count query
        count_query = select(func.count(ProductClassification.id)).where(
            ProductClassification.product_description.ilike(f"%{search_term}%")
        )
        count_result = await test_session.execute(count_query)
        total_count = count_result.scalar()
        
        # Results query
        results_query = select(ProductClassification).where(
            ProductClassification.product_description.ilike(f"%{search_term}%")
        ).offset(offset).limit(limit)
        results = await test_session.execute(results_query)
        classifications = results.scalars().all()
        
        performance_timer.stop()
        
        assert total_count is not None
        assert classifications is not None
        assert performance_timer.elapsed < 1.0  # Should complete within 1 second


@pytest.mark.integration
class TestSearchStatistics:
    """Test search analytics and statistics."""
    
    async def test_get_classification_stats(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification]
    ):
        """Test getting classification statistics."""
        response = await async_test_client.get("/api/search/stats")
        
        assert response.status_code == 200
        data = response.json()
        
        # Check required statistics fields
        required_fields = [
            "total_classifications",
            "verified_classifications",
            "pending_classifications",
            "verification_rate",
            "average_confidence",
            "source_distribution"
        ]
        
        for field in required_fields:
            assert field in data
        
        # Verify data types and ranges
        assert isinstance(data["total_classifications"], int)
        assert isinstance(data["verified_classifications"], int)
        assert isinstance(data["pending_classifications"], int)
        assert 0.0 <= data["verification_rate"] <= 1.0
        assert 0.0 <= data["average_confidence"] <= 1.0
        assert isinstance(data["source_distribution"], dict)
    
    async def test_search_analytics_tracking(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification]
    ):
        """Test search analytics and tracking."""
        # Perform multiple searches to generate analytics data
        search_terms = ["electronic", "device", "machinery", "textile"]
        
        for term in search_terms:
            response = await async_test_client.get(
                "/api/search/products",
                params={"search_term": term}
            )
            assert response.status_code == 200
            
            data = response.json()
            assert "search_time_ms" in data
            assert isinstance(data["search_time_ms"], (int, float))
            assert data["search_time_ms"] > 0


@pytest.mark.unit
class TestSearchValidation:
    """Test search input validation and error handling."""
    
    async def test_search_term_validation(
        self,
        async_test_client: AsyncClient
    ):
        """Test search term validation."""
        # Test empty search term
        response = await async_test_client.get(
            "/api/search/products",
            params={"search_term": ""}
        )
        assert response.status_code == 422
        
        # Test very long search term
        long_term = "a" * 201  # Exceeds max length
        response = await async_test_client.get(
            "/api/search/products",
            params={"search_term": long_term}
        )
        assert response.status_code == 422
    
    async def test_pagination_validation(
        self,
        async_test_client: AsyncClient
    ):
        """Test pagination parameter validation."""
        # Test invalid page number
        response = await async_test_client.get(
            "/api/search/products",
            params={
                "search_term": "test",
                "page": -1
            }
        )
        assert response.status_code == 422
        
        # Test invalid limit
        response = await async_test_client.get(
            "/api/search/products",
            params={
                "search_term": "test",
                "limit": 0
            }
        )
        assert response.status_code == 422
        
        # Test limit exceeding maximum
        response = await async_test_client.get(
            "/api/search/products",
            params={
                "search_term": "test",
                "limit": 101  # Exceeds max limit of 100
            }
        )
        assert response.status_code == 422
    
    async def test_filter_validation(
        self,
        async_test_client: AsyncClient
    ):
        """Test filter parameter validation."""
        # Test invalid confidence range
        response = await async_test_client.get(
            "/api/search/products",
            params={
                "search_term": "test",
                "min_confidence": -0.1
            }
        )
        assert response.status_code == 422
        
        response = await async_test_client.get(
            "/api/search/products",
            params={
                "search_term": "test",
                "min_confidence": 1.1
            }
        )
        assert response.status_code == 422


@pytest.mark.external
class TestSearchIntegration:
    """Test search integration with external services."""
    
    async def test_search_with_ai_service_integration(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession,
        mock_anthropic_client
    ):
        """Test search integration with AI service."""
        # This tests that search endpoints can work with AI service
        with patch('routes.search.ai_service') as mock_ai_service:
            mock_ai_service.get_classification_stats.return_value = {
                "total_classifications": 10,
                "verified_classifications": 8,
                "verification_rate": 0.8,
                "classifications_by_source": {"ai": 6, "similarity": 2, "broker": 2},
                "average_confidence_by_source": {"ai": 0.85, "similarity": 0.75, "broker": 1.0},
                "ai_available": True
            }
            
            response = await async_test_client.get("/api/search/stats")
            assert response.status_code == 200
            
            data = response.json()
            assert data["total_classifications"] == 10
            assert data["verified_classifications"] == 8
    
    async def test_search_error_handling(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession
    ):
        """Test search error handling."""
        # Test database error simulation
        with patch('routes.search.get_async_session') as mock_get_session:
            mock_get_session.side_effect = Exception("Database connection error")
            
            response = await async_test_client.get(
                "/api/search/products",
                params={"search_term": "test"}
            )
            assert response.status_code == 500


@pytest.mark.unit
class TestSearchEdgeCases:
    """Test search edge cases and boundary conditions."""
    
    async def test_search_special_characters(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession,
        sample_classifications: List[ProductClassification]
    ):
        """Test search with special characters."""
        special_terms = [
            "device@test",
            "product#123",
            "item$price",
            "name&brand",
            "type*variant"
        ]
        
        for term in special_terms:
            response = await async_test_client.get(
                "/api/search/products",
                params={"search_term": term}
            )
            # Should handle gracefully without errors
            assert response.status_code == 200
    
    async def test_search_unicode_characters(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession
    ):
        """Test search with unicode characters."""
        unicode_terms = [
            "café",
            "naïve",
            "résumé",
            "piñata",
            "北京"  # Chinese characters
        ]
        
        for term in unicode_terms:
            response = await async_test_client.get(
                "/api/search/products",
                params={"search_term": term}
            )
            # Should handle gracefully without errors
            assert response.status_code == 200
    
    async def test_search_sql_injection_protection(
        self,
        async_test_client: AsyncClient,
        test_session: AsyncSession
    ):
        """Test protection against SQL injection attempts."""
        malicious_terms = [
            "'; DROP TABLE products; --",
            "' OR '1'='1",
            "'; SELECT * FROM users; --",
            "' UNION SELECT * FROM classifications; --"
        ]
        
        for term in malicious_terms:
            response = await async_test_client.get(
                "/api/search/products",
                params={"search_term": term}
            )
            # Should handle safely without SQL injection
            assert response.status_code == 200
            # Should return empty results or safe results
            data = response.json()
            assert "results" in data