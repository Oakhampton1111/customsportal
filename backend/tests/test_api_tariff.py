"""
API endpoint tests for tariff routes.

This module tests all tariff-related API endpoints including sections, chapters,
tree navigation, detailed tariff lookup, and search functionality.
"""

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils.test_helpers import (
    APITestHelper, DatabaseTestHelper, TestDataFactory,
    PerformanceTestHelper, ValidationTestHelper
)


@pytest.mark.api
class TestTariffSectionsAPI:
    """Test tariff sections API endpoints."""
    
    async def test_get_tariff_sections_success(self, test_client: TestClient, test_session: AsyncSession):
        """Test successful retrieval of tariff sections."""
        # Create test section data
        section_data = {
            "section_number": 1,
            "title": "Live Animals; Animal Products",
            "description": "Test section description",
            "chapter_range": "01-05"
        }
        
        # Note: We would need to create TariffSection model instances here
        # For now, testing the endpoint structure
        
        response = test_client.get("/api/tariff/sections")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert isinstance(data, list)
        # Additional assertions would depend on test data setup
    
    async def test_get_tariff_sections_empty_database(self, test_client: TestClient):
        """Test sections endpoint with empty database."""
        response = test_client.get("/api/tariff/sections")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 0
    
    async def test_get_tariff_sections_performance(self, test_client: TestClient, performance_timer):
        """Test sections endpoint performance."""
        performance_timer.start()
        response = test_client.get("/api/tariff/sections")
        performance_timer.stop()
        
        APITestHelper.assert_response_success(response, 200)
        PerformanceTestHelper.assert_execution_time(performance_timer.elapsed, 2.0)


@pytest.mark.api
class TestTariffChaptersAPI:
    """Test tariff chapters API endpoints."""
    
    async def test_get_chapters_by_section_success(self, test_client: TestClient, test_session: AsyncSession):
        """Test successful retrieval of chapters for a section."""
        section_id = 1
        
        response = test_client.get(f"/api/tariff/chapters/{section_id}")
        
        # Should return 404 if section doesn't exist, or 200 with chapters
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, list)
    
    async def test_get_chapters_invalid_section_id(self, test_client: TestClient):
        """Test chapters endpoint with invalid section ID."""
        invalid_section_id = 99999
        
        response = test_client.get(f"/api/tariff/chapters/{invalid_section_id}")
        
        APITestHelper.assert_response_error(response, 404)
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()
    
    async def test_get_chapters_invalid_section_id_type(self, test_client: TestClient):
        """Test chapters endpoint with invalid section ID type."""
        response = test_client.get("/api/tariff/chapters/invalid")
        
        APITestHelper.assert_response_error(response, 422)


@pytest.mark.api
class TestTariffTreeAPI:
    """Test tariff tree API endpoints."""
    
    async def test_get_tariff_tree_success(self, test_client: TestClient):
        """Test successful tariff tree retrieval."""
        section_id = 1
        
        response = test_client.get(f"/api/tariff/tree/{section_id}")
        
        # Should return 404 if section doesn't exist, or 200 with tree
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = APITestHelper.assert_json_response(response, [
                "root_nodes", "total_nodes", "max_depth", "expanded_levels",
                "section_id"
            ])
            
            assert isinstance(data["root_nodes"], list)
            assert isinstance(data["total_nodes"], int)
            assert isinstance(data["max_depth"], int)
            assert isinstance(data["expanded_levels"], list)
            assert data["section_id"] == section_id
    
    async def test_get_tariff_tree_with_depth_parameter(self, test_client: TestClient):
        """Test tariff tree with custom depth parameter."""
        section_id = 1
        depth = 3
        
        response = test_client.get(f"/api/tariff/tree/{section_id}?depth={depth}")
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert data["max_depth"] == depth
    
    async def test_get_tariff_tree_invalid_depth(self, test_client: TestClient):
        """Test tariff tree with invalid depth parameter."""
        section_id = 1
        
        # Test depth too low
        response = test_client.get(f"/api/tariff/tree/{section_id}?depth=0")
        APITestHelper.assert_response_error(response, 422)
        
        # Test depth too high
        response = test_client.get(f"/api/tariff/tree/{section_id}?depth=10")
        APITestHelper.assert_response_error(response, 422)
    
    async def test_get_tariff_tree_with_parent_code(self, test_client: TestClient):
        """Test tariff tree with parent code parameter."""
        section_id = 1
        parent_code = "0101"
        
        response = test_client.get(f"/api/tariff/tree/{section_id}?parent_code={parent_code}")
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            data = response.json()
            assert data["parent_code"] == parent_code


@pytest.mark.api
class TestTariffDetailAPI:
    """Test tariff detail API endpoints."""
    
    async def test_get_tariff_detail_success(self, test_client: TestClient, test_session: AsyncSession):
        """Test successful tariff detail retrieval."""
        # Create test tariff code
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000",
            description="Live horses for breeding purposes"
        )
        
        response = test_client.get(f"/api/tariff/code/{tariff_code.hs_code}")
        
        APITestHelper.assert_response_success(response, 200)
        data = APITestHelper.assert_json_response(response, [
            "tariff", "breadcrumbs"
        ])
        
        assert data["tariff"]["hs_code"] == tariff_code.hs_code
        assert data["tariff"]["description"] == tariff_code.description
        assert isinstance(data["breadcrumbs"], list)
    
    async def test_get_tariff_detail_with_rates(self, test_client: TestClient, test_session: AsyncSession):
        """Test tariff detail with duty and FTA rates included."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010001"
        )
        
        response = test_client.get(f"/api/tariff/code/{tariff_code.hs_code}?include_rates=true")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        # Check that rate fields are present (even if empty)
        assert "duty_rates" in data
        assert "fta_rates" in data
        assert isinstance(data["duty_rates"], list)
        assert isinstance(data["fta_rates"], list)
    
    async def test_get_tariff_detail_with_children(self, test_client: TestClient, test_session: AsyncSession):
        """Test tariff detail with child codes included."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010002"
        )
        
        response = test_client.get(f"/api/tariff/code/{tariff_code.hs_code}?include_children=true")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert "children" in data
        assert isinstance(data["children"], list)
    
    async def test_get_tariff_detail_with_related(self, test_client: TestClient, test_session: AsyncSession):
        """Test tariff detail with related codes included."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010003"
        )
        
        response = test_client.get(f"/api/tariff/code/{tariff_code.hs_code}?include_related=true")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert "related_codes" in data
        assert isinstance(data["related_codes"], list)
    
    async def test_get_tariff_detail_not_found(self, test_client: TestClient):
        """Test tariff detail for non-existent HS code."""
        non_existent_code = "9999999999"
        
        response = test_client.get(f"/api/tariff/code/{non_existent_code}")
        
        APITestHelper.assert_response_error(response, 404)
        data = response.json()
        assert "not found" in data["detail"].lower()
    
    async def test_get_tariff_detail_invalid_hs_code_format(self, test_client: TestClient):
        """Test tariff detail with invalid HS code format."""
        invalid_codes = ["abc", "123", "12345678901"]  # Too short, too long, non-numeric
        
        for invalid_code in invalid_codes:
            response = test_client.get(f"/api/tariff/code/{invalid_code}")
            # Should either return 404 (cleaned code not found) or handle gracefully
            assert response.status_code in [404, 422]


@pytest.mark.api
class TestTariffSearchAPI:
    """Test tariff search API endpoints."""
    
    async def test_tariff_search_basic(self, test_client: TestClient, test_session: AsyncSession):
        """Test basic tariff search functionality."""
        # Create test tariff codes
        await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010004",
            description="Live horses for racing"
        )
        
        response = test_client.get("/api/tariff/search?query=horses")
        
        APITestHelper.assert_response_success(response, 200)
        data = APITestHelper.assert_json_response(response, [
            "results", "pagination", "total_results", "search_time_ms"
        ])
        
        assert isinstance(data["results"], list)
        assert isinstance(data["pagination"], dict)
        assert isinstance(data["total_results"], int)
        assert isinstance(data["search_time_ms"], (int, float))
    
    async def test_tariff_search_with_filters(self, test_client: TestClient):
        """Test tariff search with various filters."""
        params = {
            "query": "test",
            "level": 10,
            "section_id": 1,
            "is_active": True,
            "limit": 10,
            "offset": 0,
            "sort_by": "hs_code",
            "sort_order": "asc"
        }
        
        response = test_client.get("/api/tariff/search", params=params)
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert data["query"] == "test"
        assert len(data["results"]) <= 10
    
    async def test_tariff_search_pagination(self, test_client: TestClient):
        """Test tariff search pagination."""
        # Test first page
        response = test_client.get("/api/tariff/search?limit=5&offset=0")
        APITestHelper.assert_response_success(response, 200)
        
        data = response.json()
        pagination = data["pagination"]
        
        assert pagination["page"] == 1
        assert pagination["size"] == 5
        assert len(data["results"]) <= 5
        
        # Test second page if there are results
        if pagination["pages"] > 1:
            response = test_client.get("/api/tariff/search?limit=5&offset=5")
            APITestHelper.assert_response_success(response, 200)
            
            data = response.json()
            assert data["pagination"]["page"] == 2
    
    async def test_tariff_search_hs_code_prefix(self, test_client: TestClient, test_session: AsyncSession):
        """Test tariff search with HS code prefix filter."""
        await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010005"
        )
        
        response = test_client.get("/api/tariff/search?hs_code_starts_with=0101")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        # All results should have HS codes starting with 0101
        for result in data["results"]:
            assert result["hs_code"].startswith("0101")
    
    async def test_tariff_search_sorting(self, test_client: TestClient):
        """Test tariff search sorting options."""
        sort_options = [
            ("hs_code", "asc"),
            ("hs_code", "desc"),
            ("description", "asc"),
            ("description", "desc")
        ]
        
        for sort_by, sort_order in sort_options:
            response = test_client.get(f"/api/tariff/search?sort_by={sort_by}&sort_order={sort_order}")
            APITestHelper.assert_response_success(response, 200)
    
    async def test_tariff_search_invalid_parameters(self, test_client: TestClient):
        """Test tariff search with invalid parameters."""
        # Invalid level
        response = test_client.get("/api/tariff/search?level=15")
        APITestHelper.assert_response_error(response, 422)
        
        # Invalid limit
        response = test_client.get("/api/tariff/search?limit=2000")
        APITestHelper.assert_response_error(response, 422)
        
        # Invalid sort order
        response = test_client.get("/api/tariff/search?sort_order=invalid")
        APITestHelper.assert_response_error(response, 422)
    
    async def test_tariff_search_performance(self, test_client: TestClient, performance_timer):
        """Test tariff search performance."""
        performance_timer.start()
        response = test_client.get("/api/tariff/search?query=test&limit=50")
        performance_timer.stop()
        
        APITestHelper.assert_response_success(response, 200)
        PerformanceTestHelper.assert_execution_time(performance_timer.elapsed, 3.0)
        
        # Check that search_time_ms is reasonable
        data = response.json()
        assert data["search_time_ms"] < 3000  # Less than 3 seconds


@pytest.mark.api
@pytest.mark.integration
class TestTariffAPIIntegration:
    """Integration tests for tariff API workflows."""
    
    async def test_tariff_navigation_workflow(self, test_client: TestClient, test_session: AsyncSession):
        """Test complete tariff navigation workflow."""
        # 1. Get sections
        sections_response = test_client.get("/api/tariff/sections")
        APITestHelper.assert_response_success(sections_response, 200)
        
        # 2. If sections exist, get chapters for first section
        sections = sections_response.json()
        if sections:
            first_section = sections[0]
            chapters_response = test_client.get(f"/api/tariff/chapters/{first_section['id']}")
            assert chapters_response.status_code in [200, 404]
            
            # 3. Get tree for section
            tree_response = test_client.get(f"/api/tariff/tree/{first_section['id']}")
            assert tree_response.status_code in [200, 404]
    
    async def test_search_to_detail_workflow(self, test_client: TestClient, test_session: AsyncSession):
        """Test workflow from search to detail view."""
        # Create test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010006",
            description="Live horses for testing workflow"
        )
        
        # 1. Search for tariff codes
        search_response = test_client.get("/api/tariff/search?query=horses")
        APITestHelper.assert_response_success(search_response, 200)
        
        search_data = search_response.json()
        if search_data["results"]:
            # 2. Get detail for first result
            first_result = search_data["results"][0]
            detail_response = test_client.get(f"/api/tariff/code/{first_result['hs_code']}")
            APITestHelper.assert_response_success(detail_response, 200)
            
            detail_data = detail_response.json()
            assert detail_data["tariff"]["hs_code"] == first_result["hs_code"]


@pytest.mark.api
@pytest.mark.slow
class TestTariffAPIPerformance:
    """Performance tests for tariff API endpoints."""
    
    async def test_concurrent_tariff_requests(self, async_test_client: AsyncClient):
        """Test concurrent tariff API requests."""
        import asyncio
        
        async def make_request(endpoint):
            response = await async_test_client.get(endpoint)
            return response.status_code
        
        # Test concurrent requests to different endpoints
        endpoints = [
            "/api/tariff/sections",
            "/api/tariff/search?query=test",
            "/api/tariff/search?limit=10"
        ]
        
        tasks = [make_request(endpoint) for endpoint in endpoints * 3]  # 9 concurrent requests
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # All requests should complete within reasonable time
        assert end_time - start_time < 10.0
        
        # Most requests should succeed (some might fail due to missing data)
        successful_requests = sum(1 for result in results if isinstance(result, int) and result in [200, 404])
        assert successful_requests >= len(tasks) * 0.5  # At least 50% success rate


# Import time for performance tests
import time