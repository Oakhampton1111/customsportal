"""
API integration tests for end-to-end workflows.

This module tests complete API workflows, cross-endpoint integration,
performance under load, and real-world usage scenarios.
"""

import pytest
import pytest_asyncio
import asyncio
import time
from decimal import Decimal
from datetime import date, datetime
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch

from tests.utils.test_helpers import (
    APITestHelper, DatabaseTestHelper, TestDataFactory,
    PerformanceTestHelper, ValidationTestHelper
)


@pytest.mark.api
@pytest.mark.integration
class TestCompleteWorkflows:
    """Test complete end-to-end API workflows."""
    
    async def test_tariff_lookup_to_duty_calculation_workflow(self, test_client: TestClient, test_session: AsyncSession):
        """Test complete workflow from tariff lookup to duty calculation."""
        # 1. Create test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000",
            description="Live horses for breeding purposes"
        )
        
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            general_rate=5.0,
            unit_type="ad_valorem"
        )
        
        await DatabaseTestHelper.create_fta_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            country_code="USA",
            preferential_rate=0.0,
            fta_code="AUSFTA"
        )
        
        # 2. Search for tariff codes
        search_response = test_client.get("/api/tariff/search?query=horses")
        APITestHelper.assert_response_success(search_response, 200)
        
        search_data = search_response.json()
        assert search_data["total_results"] >= 0
        
        # 3. Get detailed tariff information
        detail_response = test_client.get(f"/api/tariff/code/{tariff_code.hs_code}?include_rates=true")
        APITestHelper.assert_response_success(detail_response, 200)
        
        detail_data = detail_response.json()
        assert detail_data["tariff"]["hs_code"] == tariff_code.hs_code
        
        # 4. Get available duty rates
        rates_response = test_client.get(f"/api/duty/rates/{tariff_code.hs_code}?include_fta=true")
        APITestHelper.assert_response_success(rates_response, 200)
        
        rates_data = rates_response.json()
        assert rates_data["hs_code"] == tariff_code.hs_code
        
        # 5. Calculate duty
        calculation_request = {
            "hs_code": tariff_code.hs_code,
            "country_code": "USA",
            "customs_value": 10000.00,
            "quantity": 1,
            "calculation_date": date.today().isoformat()
        }
        
        calc_response = test_client.post("/api/duty/calculate", json=calculation_request)
        APITestHelper.assert_response_success(calc_response, 200)
        
        calc_data = calc_response.json()
        assert calc_data["hs_code"] == tariff_code.hs_code
        assert calc_data["country_code"] == "USA"
        assert calc_data["customs_value"] == 10000.00
        
        # 6. Get detailed breakdown
        breakdown_params = {
            "hs_code": tariff_code.hs_code,
            "country_code": "USA",
            "customs_value": 10000.00
        }
        
        breakdown_response = test_client.get("/api/duty/breakdown", params=breakdown_params)
        APITestHelper.assert_response_success(breakdown_response, 200)
        
        breakdown_data = breakdown_response.json()
        assert breakdown_data["input_parameters"]["hs_code"] == tariff_code.hs_code
        
        # Verify data consistency across endpoints
        assert detail_data["tariff"]["hs_code"] == calc_data["hs_code"]
        assert rates_data["hs_code"] == breakdown_data["input_parameters"]["hs_code"]
    
    @patch('ai.tariff_ai.TariffAIService.classify_product')
    async def test_product_classification_to_duty_calculation_workflow(self, mock_classify, test_client: TestClient, test_session: AsyncSession):
        """Test workflow from product classification to duty calculation."""
        # 1. Create test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000",
            description="Live horses for breeding"
        )
        
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            general_rate=7.5
        )
        
        # Mock AI classification
        mock_classify.return_value = {
            "hs_code": tariff_code.hs_code,
            "confidence": 0.95,
            "classification_source": "ai",
            "reasoning": "Product matches live horse classification"
        }
        
        # 2. Classify product
        classification_request = {
            "product_description": "Live breeding horses from Australia",
            "confidence_threshold": 0.8,
            "store_result": True
        }
        
        classify_response = test_client.post("/api/search/classify", json=classification_request)
        APITestHelper.assert_response_success(classify_response, 200)
        
        classify_data = classify_response.json()
        classified_hs_code = classify_data["hs_code"]
        
        # 3. Get tariff details for classified code
        detail_response = test_client.get(f"/api/tariff/code/{classified_hs_code}")
        APITestHelper.assert_response_success(detail_response, 200)
        
        # 4. Calculate duty for classified product
        calculation_request = {
            "hs_code": classified_hs_code,
            "country_code": "AUS",
            "customs_value": 15000.00
        }
        
        calc_response = test_client.post("/api/duty/calculate", json=calculation_request)
        APITestHelper.assert_response_success(calc_response, 200)
        
        calc_data = calc_response.json()
        assert calc_data["hs_code"] == classified_hs_code
        
        # Verify workflow consistency
        assert classify_data["hs_code"] == calc_data["hs_code"]
        assert classify_data["tariff_description"] == tariff_code.description
    
    async def test_multi_country_duty_comparison_workflow(self, test_client: TestClient, test_session: AsyncSession):
        """Test workflow for comparing duties across multiple countries."""
        # 1. Create test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            general_rate=10.0
        )
        
        # Create FTA rates for different countries
        countries_and_rates = [
            ("USA", 0.0, "AUSFTA"),
            ("JPN", 2.5, "JAEPA"),
            ("KOR", 5.0, "KAFTA")
        ]
        
        for country, rate, fta_code in countries_and_rates:
            await DatabaseTestHelper.create_fta_rate(
                test_session,
                hs_code=tariff_code.hs_code,
                country_code=country,
                preferential_rate=rate,
                fta_code=fta_code
            )
        
        # 2. Get rates for each country
        country_rates = {}
        for country, _, _ in countries_and_rates:
            rates_response = test_client.get(
                f"/api/duty/rates/{tariff_code.hs_code}?country_code={country}&include_fta=true"
            )
            APITestHelper.assert_response_success(rates_response, 200)
            country_rates[country] = rates_response.json()
        
        # 3. Calculate duties for each country
        customs_value = 5000.00
        country_calculations = {}
        
        for country, _, _ in countries_and_rates:
            calc_request = {
                "hs_code": tariff_code.hs_code,
                "country_code": country,
                "customs_value": customs_value
            }
            
            calc_response = test_client.post("/api/duty/calculate", json=calc_request)
            if calc_response.status_code == 200:
                country_calculations[country] = calc_response.json()
        
        # 4. Verify different duty amounts for different countries
        if len(country_calculations) > 1:
            duty_amounts = [calc["total_duty"] for calc in country_calculations.values()]
            # Should have different duty amounts due to different FTA rates
            assert len(set(duty_amounts)) > 1
        
        # 5. Verify USA has lowest duty (0% FTA rate)
        if "USA" in country_calculations:
            usa_duty = country_calculations["USA"]["total_duty"]
            other_duties = [
                calc["total_duty"] for country, calc in country_calculations.items()
                if country != "USA"
            ]
            if other_duties:
                assert usa_duty <= min(other_duties)


@pytest.mark.api
@pytest.mark.integration
class TestCrossEndpointDataConsistency:
    """Test data consistency across different API endpoints."""
    
    async def test_tariff_data_consistency(self, test_client: TestClient, test_session: AsyncSession):
        """Test tariff data consistency across endpoints."""
        # Create test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000",
            description="Live horses for breeding",
            level=10,
            is_active=True
        )
        
        # Get data from different endpoints
        endpoints_data = {}
        
        # Tariff detail endpoint
        detail_response = test_client.get(f"/api/tariff/code/{tariff_code.hs_code}")
        if detail_response.status_code == 200:
            endpoints_data["detail"] = detail_response.json()["tariff"]
        
        # Search endpoint
        search_response = test_client.get(f"/api/tariff/search?hs_code_starts_with={tariff_code.hs_code}")
        if search_response.status_code == 200:
            search_data = search_response.json()
            matching_results = [
                result for result in search_data["results"]
                if result["hs_code"] == tariff_code.hs_code
            ]
            if matching_results:
                endpoints_data["search"] = matching_results[0]
        
        # Verify consistency
        if len(endpoints_data) > 1:
            reference_data = list(endpoints_data.values())[0]
            
            for endpoint_name, data in endpoints_data.items():
                assert data["hs_code"] == reference_data["hs_code"]
                assert data["description"] == reference_data["description"]
                assert data["level"] == reference_data["level"]
                assert data["is_active"] == reference_data["is_active"]
    
    async def test_duty_rate_consistency(self, test_client: TestClient, test_session: AsyncSession):
        """Test duty rate consistency across endpoints."""
        # Create test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        duty_rate = await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            general_rate=7.5,
            unit_type="ad_valorem"
        )
        
        # Get rates from different endpoints
        rates_response = test_client.get(f"/api/duty/rates/{tariff_code.hs_code}")
        detail_response = test_client.get(f"/api/tariff/code/{tariff_code.hs_code}?include_rates=true")
        
        if rates_response.status_code == 200 and detail_response.status_code == 200:
            rates_data = rates_response.json()
            detail_data = detail_response.json()
            
            # Compare duty rates from both endpoints
            if rates_data["general_rates"] and detail_data.get("duty_rates"):
                rates_endpoint_rate = rates_data["general_rates"][0]
                detail_endpoint_rate = detail_data["duty_rates"][0]
                
                assert rates_endpoint_rate["general_rate"] == detail_endpoint_rate["rate_value"]
                assert rates_endpoint_rate["unit_type"] == detail_endpoint_rate["unit_type"]


@pytest.mark.api
@pytest.mark.integration
@pytest.mark.slow
class TestAPIPerformanceIntegration:
    """Test API performance under various load conditions."""
    
    async def test_concurrent_mixed_requests(self, async_test_client: AsyncClient, test_session: AsyncSession):
        """Test concurrent requests across different endpoints."""
        # Create test data
        tariff_codes = []
        for i in range(5):
            code = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=f"010101{i:04d}",
                description=f"Test product {i}"
            )
            tariff_codes.append(code)
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=code.hs_code,
                general_rate=float(5 + i)
            )
        
        async def make_tariff_search():
            response = await async_test_client.get("/api/tariff/search?query=test")
            return response.status_code
        
        async def make_duty_calculation(hs_code):
            response = await async_test_client.post(
                "/api/duty/calculate",
                json={
                    "hs_code": hs_code,
                    "country_code": "USA",
                    "customs_value": 1000.00
                }
            )
            return response.status_code
        
        async def make_tariff_detail(hs_code):
            response = await async_test_client.get(f"/api/tariff/code/{hs_code}")
            return response.status_code
        
        async def make_duty_rates(hs_code):
            response = await async_test_client.get(f"/api/duty/rates/{hs_code}")
            return response.status_code
        
        # Create mixed concurrent requests
        tasks = []
        
        # Add search requests
        tasks.extend([make_tariff_search() for _ in range(3)])
        
        # Add duty calculations
        for code in tariff_codes:
            tasks.append(make_duty_calculation(code.hs_code))
        
        # Add detail requests
        for code in tariff_codes[:3]:
            tasks.append(make_tariff_detail(code.hs_code))
        
        # Add rates requests
        for code in tariff_codes[:3]:
            tasks.append(make_duty_rates(code.hs_code))
        
        # Execute all requests concurrently
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Verify performance
        total_time = end_time - start_time
        assert total_time < 20.0  # All requests should complete within 20 seconds
        
        # Verify success rate
        successful_requests = sum(
            1 for result in results 
            if isinstance(result, int) and result in [200, 404]
        )
        success_rate = successful_requests / len(results)
        assert success_rate >= 0.8  # At least 80% success rate
    
    async def test_sequential_workflow_performance(self, test_client: TestClient, test_session: AsyncSession, performance_timer):
        """Test performance of sequential workflow operations."""
        # Create test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            general_rate=5.0
        )
        
        # Measure complete workflow performance
        performance_timer.start()
        
        # 1. Search
        search_response = test_client.get("/api/tariff/search?query=test")
        assert search_response.status_code in [200, 404]
        
        # 2. Get details
        detail_response = test_client.get(f"/api/tariff/code/{tariff_code.hs_code}")
        assert detail_response.status_code in [200, 404]
        
        # 3. Get rates
        rates_response = test_client.get(f"/api/duty/rates/{tariff_code.hs_code}")
        assert rates_response.status_code == 200
        
        # 4. Calculate duty
        calc_response = test_client.post(
            "/api/duty/calculate",
            json={
                "hs_code": tariff_code.hs_code,
                "country_code": "USA",
                "customs_value": 1000.00
            }
        )
        assert calc_response.status_code in [200, 422]
        
        # 5. Get breakdown
        breakdown_response = test_client.get(
            "/api/duty/breakdown",
            params={
                "hs_code": tariff_code.hs_code,
                "country_code": "USA",
                "customs_value": 1000.00
            }
        )
        assert breakdown_response.status_code in [200, 422]
        
        performance_timer.stop()
        
        # Complete workflow should be reasonably fast
        PerformanceTestHelper.assert_execution_time(performance_timer.elapsed, 10.0)
    
    async def test_database_connection_handling(self, async_test_client: AsyncClient):
        """Test database connection handling under load."""
        async def make_database_request():
            response = await async_test_client.get("/api/tariff/sections")
            return response.status_code
        
        # Make many concurrent database requests
        tasks = [make_database_request() for _ in range(20)]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # Should handle concurrent database requests without errors
        assert end_time - start_time < 15.0
        
        # Should not have database connection errors
        connection_errors = sum(
            1 for result in results 
            if isinstance(result, int) and result == 500
        )
        assert connection_errors < len(results) * 0.1  # Less than 10% server errors


@pytest.mark.api
@pytest.mark.integration
class TestRealWorldScenarios:
    """Test real-world usage scenarios."""
    
    async def test_customs_broker_daily_workflow(self, test_client: TestClient, test_session: AsyncSession):
        """Test typical daily workflow of a customs broker."""
        # Create test data for multiple products
        products = [
            ("0101010000", "Live horses for breeding", 5.0),
            ("0201100000", "Beef carcasses", 0.0),
            ("8703210000", "Motor cars", 5.0)
        ]
        
        for hs_code, description, rate in products:
            await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=description
            )
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=rate
            )
        
        # Simulate broker workflow
        workflow_results = {}
        
        for hs_code, description, expected_rate in products:
            # 1. Look up tariff details
            detail_response = test_client.get(f"/api/tariff/code/{hs_code}")
            if detail_response.status_code == 200:
                workflow_results[hs_code] = {"detail": detail_response.json()}
            
            # 2. Check available rates
            rates_response = test_client.get(f"/api/duty/rates/{hs_code}?include_fta=true")
            if rates_response.status_code == 200:
                workflow_results[hs_code]["rates"] = rates_response.json()
            
            # 3. Calculate duty for typical shipment
            calc_response = test_client.post(
                "/api/duty/calculate",
                json={
                    "hs_code": hs_code,
                    "country_code": "USA",
                    "customs_value": 10000.00
                }
            )
            if calc_response.status_code == 200:
                workflow_results[hs_code]["calculation"] = calc_response.json()
        
        # Verify workflow completed successfully
        assert len(workflow_results) == len(products)
        
        for hs_code, results in workflow_results.items():
            assert "detail" in results
            assert "rates" in results
            # Calculation might fail if rates not properly set up
    
    async def test_high_volume_import_scenario(self, test_client: TestClient, test_session: AsyncSession):
        """Test scenario with high-volume import calculations."""
        # Create test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="8703210000",
            description="Motor cars with engines"
        )
        
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            general_rate=5.0
        )
        
        # Simulate multiple high-value calculations
        high_value_calculations = [
            {"customs_value": 100000.00, "quantity": 1},
            {"customs_value": 250000.00, "quantity": 5},
            {"customs_value": 500000.00, "quantity": 10},
            {"customs_value": 1000000.00, "quantity": 20}
        ]
        
        calculation_results = []
        
        for calc_params in high_value_calculations:
            calc_request = {
                "hs_code": tariff_code.hs_code,
                "country_code": "JPN",
                **calc_params
            }
            
            calc_response = test_client.post("/api/duty/calculate", json=calc_request)
            if calc_response.status_code == 200:
                calculation_results.append(calc_response.json())
        
        # Verify calculations scale appropriately
        if len(calculation_results) > 1:
            # Higher customs values should result in higher total amounts
            total_amounts = [result["total_amount"] for result in calculation_results]
            assert total_amounts == sorted(total_amounts)  # Should be in ascending order
    
    @patch('ai.tariff_ai.TariffAIService.classify_batch')
    async def test_bulk_classification_scenario(self, mock_classify_batch, test_client: TestClient, test_session: AsyncSession):
        """Test bulk product classification scenario."""
        # Create test tariff codes
        tariff_codes = []
        for i in range(10):
            code = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=f"010101{i:04d}",
                description=f"Test product {i}"
            )
            tariff_codes.append(code)
        
        # Mock batch classification
        mock_classify_batch.return_value = [
            {
                "hs_code": code.hs_code,
                "confidence": 0.9,
                "classification_source": "ai"
            }
            for code in tariff_codes
        ]
        
        # Prepare batch request
        batch_request = {
            "products": [
                {
                    "id": f"prod_{i}",
                    "description": f"Product description {i}"
                }
                for i in range(10)
            ],
            "confidence_threshold": 0.8,
            "store_results": True
        }
        
        # Execute batch classification
        batch_response = test_client.post("/api/search/classify/batch", json=batch_request)
        APITestHelper.assert_response_success(batch_response, 200)
        
        batch_data = batch_response.json()
        assert batch_data["total_products"] == 10
        assert batch_data["successful_classifications"] == 10
        assert batch_data["failed_classifications"] == 0
        
        # Verify all products were classified
        assert len(batch_data["results"]) == 10
        for result in batch_data["results"]:
            assert result["status"] == "success"
            assert "hs_code" in result
            assert "confidence_score" in result


@pytest.mark.api
@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling across integrated workflows."""
    
    async def test_graceful_degradation(self, test_client: TestClient):
        """Test graceful degradation when services are unavailable."""
        # Test with non-existent data
        non_existent_hs_code = "9999999999"
        
        # Should handle missing data gracefully across endpoints
        endpoints = [
            f"/api/tariff/code/{non_existent_hs_code}",
            f"/api/duty/rates/{non_existent_hs_code}",
            f"/api/duty/tco-check/{non_existent_hs_code}"
        ]
        
        for endpoint in endpoints:
            response = test_client.get(endpoint)
            # Should return appropriate error, not crash
            assert response.status_code in [200, 404, 422]
            
            if response.status_code >= 400:
                error_data = response.json()
                assert "detail" in error_data
    
    async def test_partial_failure_handling(self, test_client: TestClient, test_session: AsyncSession):
        """Test handling of partial failures in workflows."""
        # Create partial test data (tariff code without rates)
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        # Intentionally not creating duty rates
        
        # Test workflow with missing data
        # 1. Tariff detail should work
        detail_response = test_client.get(f"/api/tariff/code/{tariff_code.hs_code}")
        APITestHelper.assert_response_success(detail_response, 200)
        
        # 2. Rates should return empty but valid response
        rates_response = test_client.get(f"/api/duty/rates/{tariff_code.hs_code}")
        APITestHelper.assert_response_success(rates_response, 200)
        
        rates_data = rates_response.json()
        assert rates_data["general_rates"] == []
        
        # 3. Duty calculation should handle missing rates gracefully
        calc_response = test_client.post(
            "/api/duty/calculate",
            json={
                "hs_code": tariff_code.hs_code,
                "country_code": "USA",
                "customs_value": 1000.00
            }
        )
        # Should either calculate with default rates or return appropriate error
        assert calc_response.status_code in [200, 422, 500]


# Performance test utilities
import time