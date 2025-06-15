"""
End-to-End Cross-Component Integration Tests for Customs Broker Portal.

This module tests integration between different system components,
including AI classification, duty calculation, search functionality,
and external service integration.
"""

import pytest
import pytest_asyncio
import asyncio
import time
from decimal import Decimal
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch, AsyncMock, MagicMock

from tests.utils.test_helpers import (
    APITestHelper, DatabaseTestHelper, TestDataFactory,
    PerformanceTestHelper, MockHelper
)


@pytest.mark.e2e
@pytest.mark.integration
class TestAIClassificationIntegration:
    """Test AI classification integration with other system components."""
    
    @patch('ai.tariff_ai.TariffAIService.classify_product')
    async def test_ai_to_duty_calculation_pipeline(
        self, mock_classify, test_client: TestClient, test_session: AsyncSession
    ):
        """Test complete pipeline from AI classification to duty calculation."""
        # 1. Setup test data
        classification_scenarios = [
            {
                "product_description": "Apple MacBook Pro 16-inch laptop with M2 chip",
                "expected_hs_code": "8471300000",
                "confidence": 0.95,
                "customs_value": 2500.00
            },
            {
                "product_description": "Men's blue denim jeans 100% cotton",
                "expected_hs_code": "6203420000", 
                "confidence": 0.88,
                "customs_value": 50.00
            },
            {
                "product_description": "Toyota Camry sedan 2.5L engine",
                "expected_hs_code": "8703210000",
                "confidence": 0.92,
                "customs_value": 25000.00
            }
        ]
        
        # Create corresponding tariff data
        for scenario in classification_scenarios:
            await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=scenario["expected_hs_code"],
                description=f"Test product for {scenario['product_description'][:20]}..."
            )
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=scenario["expected_hs_code"],
                general_rate=5.0
            )
            
            # Add FTA rates
            await DatabaseTestHelper.create_fta_rate(
                test_session,
                hs_code=scenario["expected_hs_code"],
                country_code="USA",
                preferential_rate=0.0,
                fta_code="AUSFTA"
            )
        
        # 2. Test AI classification to duty calculation pipeline
        pipeline_results = {}
        
        for scenario in classification_scenarios:
            # Mock AI classification response
            mock_classify.return_value = {
                "hs_code": scenario["expected_hs_code"],
                "confidence": scenario["confidence"],
                "classification_source": "ai",
                "reasoning": f"Product matches classification for {scenario['expected_hs_code']}",
                "alternative_codes": []
            }
            
            # Step 1: AI Classification
            classify_request = {
                "product_description": scenario["product_description"],
                "confidence_threshold": 0.8,
                "store_result": True
            }
            
            classify_response = test_client.post("/api/search/classify", json=classify_request)
            APITestHelper.assert_response_success(classify_response, 200)
            
            classify_data = classify_response.json()
            
            # Step 2: Immediate duty calculation using classified HS code
            calc_request = {
                "hs_code": classify_data["hs_code"],
                "country_code": "USA",
                "customs_value": scenario["customs_value"]
            }
            
            calc_response = test_client.post("/api/duty/calculate", json=calc_request)
            
            # Step 3: Get detailed breakdown
            breakdown_response = None
            if calc_response.status_code == 200:
                calc_data = calc_response.json()
                
                breakdown_response = test_client.get(
                    "/api/duty/breakdown",
                    params={
                        "hs_code": classify_data["hs_code"],
                        "country_code": "USA",
                        "customs_value": scenario["customs_value"]
                    }
                )
            
            # Store pipeline results
            pipeline_results[scenario["expected_hs_code"]] = {
                "classification": classify_data,
                "calculation": calc_response.json() if calc_response.status_code == 200 else None,
                "breakdown": breakdown_response.json() if breakdown_response and breakdown_response.status_code == 200 else None,
                "scenario": scenario
            }
        
        # 3. Verify pipeline integration
        for hs_code, results in pipeline_results.items():
            scenario = results["scenario"]
            
            # Classification should match expected
            assert results["classification"]["hs_code"] == scenario["expected_hs_code"]
            assert results["classification"]["confidence_score"] >= 0.8
            
            # Calculation should use classified HS code
            if results["calculation"]:
                assert results["calculation"]["hs_code"] == scenario["expected_hs_code"]
                assert results["calculation"]["customs_value"] == scenario["customs_value"]
                
                # For USA (FTA), duty should be 0 or minimal
                assert results["calculation"]["total_duty"] >= 0
            
            # Breakdown should provide detailed analysis
            if results["breakdown"]:
                assert "input_parameters" in results["breakdown"]
                assert results["breakdown"]["input_parameters"]["hs_code"] == scenario["expected_hs_code"]
    
    @patch('ai.tariff_ai.TariffAIService.classify_product')
    async def test_ai_search_integration(
        self, mock_classify, test_client: TestClient, test_session: AsyncSession
    ):
        """Test AI classification integration with search functionality."""
        # 1. Setup diverse product data
        search_products = [
            ("8471300000", "Portable computers and laptops"),
            ("8471300001", "Desktop computers and workstations"),
            ("6203420000", "Men's cotton trousers and jeans"),
            ("8703210000", "Passenger motor vehicles")
        ]
        
        for hs_code, description in search_products:
            await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=description
            )
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=5.0
            )
        
        # 2. Test AI-enhanced search scenarios
        search_scenarios = [
            {
                "query": "laptop computer for business use",
                "expected_category": "8471",
                "ai_suggestion": "8471300000"
            },
            {
                "query": "men's casual pants cotton material",
                "expected_category": "6203",
                "ai_suggestion": "6203420000"
            },
            {
                "query": "family car sedan 4-door",
                "expected_category": "8703",
                "ai_suggestion": "8703210000"
            }
        ]
        
        search_integration_results = {}
        
        for scenario in search_scenarios:
            # Step 1: Traditional search
            search_response = test_client.get(f"/api/tariff/search?query={scenario['query']}&limit=10")
            APITestHelper.assert_response_success(search_response, 200)
            
            search_data = search_response.json()
            
            # Step 2: AI classification for comparison
            mock_classify.return_value = {
                "hs_code": scenario["ai_suggestion"],
                "confidence": 0.90,
                "classification_source": "ai",
                "reasoning": f"AI classified as {scenario['ai_suggestion']}"
            }
            
            classify_request = {
                "product_description": scenario["query"],
                "confidence_threshold": 0.8
            }
            
            classify_response = test_client.post("/api/search/classify", json=classify_request)
            
            # Step 3: Enhanced search with AI suggestion
            if classify_response.status_code == 200:
                classify_data = classify_response.json()
                ai_hs_code = classify_data["hs_code"]
                
                # Search for products in the same category as AI suggestion
                category_search = test_client.get(f"/api/tariff/search?hs_code_starts_with={ai_hs_code[:4]}&limit=10")
                
                search_integration_results[scenario["query"]] = {
                    "traditional_search": search_data,
                    "ai_classification": classify_data,
                    "category_search": category_search.json() if category_search.status_code == 200 else None
                }
        
        # 3. Verify search-AI integration
        for query, results in search_integration_results.items():
            # AI should provide relevant suggestions
            ai_hs_code = results["ai_classification"]["hs_code"]
            
            # AI suggestion should be in expected category
            expected_category = next(
                s["expected_category"] for s in search_scenarios 
                if s["query"] == query
            )
            assert ai_hs_code.startswith(expected_category)
            
            # Category search should find related products
            if results["category_search"]:
                category_results = results["category_search"]["results"]
                
                # Should find multiple products in the same category
                assert len(category_results) > 0
                
                # All results should be in the same category
                for result in category_results:
                    assert result["hs_code"].startswith(expected_category)


@pytest.mark.e2e
@pytest.mark.integration
class TestSearchDutyCalculationIntegration:
    """Test integration between search functionality and duty calculation."""
    
    async def test_search_to_calculation_workflow(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test complete workflow from search to duty calculation."""
        # 1. Setup comprehensive product data
        workflow_products = [
            {
                "hs_code": "8471300000",
                "description": "Portable digital automatic data processing machines",
                "keywords": ["laptop", "computer", "notebook", "portable"],
                "general_rate": 0.0
            },
            {
                "hs_code": "6203420000",
                "description": "Men's or boys' trousers of cotton",
                "keywords": ["jeans", "pants", "trousers", "cotton"],
                "general_rate": 17.5
            },
            {
                "hs_code": "8703210000",
                "description": "Motor cars with spark-ignition engines",
                "keywords": ["car", "vehicle", "automobile", "sedan"],
                "general_rate": 5.0
            }
        ]
        
        for product in workflow_products:
            await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=product["hs_code"],
                description=product["description"]
            )
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=product["hs_code"],
                general_rate=product["general_rate"]
            )
            
            # Add FTA rates for workflow testing
            fta_rates = [
                ("USA", 0.0, "AUSFTA"),
                ("JPN", product["general_rate"] * 0.5, "JAEPA"),
                ("KOR", product["general_rate"] * 0.3, "KAFTA")
            ]
            
            for country, rate, fta_code in fta_rates:
                await DatabaseTestHelper.create_fta_rate(
                    test_session,
                    hs_code=product["hs_code"],
                    country_code=country,
                    preferential_rate=rate,
                    fta_code=fta_code
                )
        
        # 2. Test search-to-calculation workflows
        workflow_results = {}
        
        for product in workflow_products:
            product_workflows = {}
            
            # Test each keyword search leading to calculation
            for keyword in product["keywords"]:
                # Step 1: Search by keyword
                search_response = test_client.get(f"/api/tariff/search?query={keyword}&limit=5")
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    
                    # Find the target product in search results
                    target_result = None
                    for result in search_data["results"]:
                        if result["hs_code"] == product["hs_code"]:
                            target_result = result
                            break
                    
                    if target_result:
                        # Step 2: Get detailed information
                        detail_response = test_client.get(
                            f"/api/tariff/code/{target_result['hs_code']}?include_rates=true"
                        )
                        
                        # Step 3: Calculate duties for multiple scenarios
                        calculation_scenarios = [
                            {"country": "USA", "value": 1000.00},
                            {"country": "JPN", "value": 2500.00},
                            {"country": "KOR", "value": 5000.00}
                        ]
                        
                        calculations = {}
                        for scenario in calculation_scenarios:
                            calc_response = test_client.post(
                                "/api/duty/calculate",
                                json={
                                    "hs_code": target_result["hs_code"],
                                    "country_code": scenario["country"],
                                    "customs_value": scenario["value"]
                                }
                            )
                            
                            if calc_response.status_code == 200:
                                calculations[f"{scenario['country']}_{scenario['value']}"] = calc_response.json()
                        
                        product_workflows[keyword] = {
                            "search_found": True,
                            "search_position": search_data["results"].index(target_result),
                            "detail_available": detail_response.status_code == 200,
                            "calculations": calculations
                        }
                    else:
                        product_workflows[keyword] = {
                            "search_found": False,
                            "search_results_count": len(search_data["results"])
                        }
            
            workflow_results[product["hs_code"]] = product_workflows
        
        # 3. Verify search-to-calculation integration
        for hs_code, workflows in workflow_results.items():
            product = next(p for p in workflow_products if p["hs_code"] == hs_code)
            
            # At least some keywords should find the product
            found_keywords = [k for k, w in workflows.items() if w.get("search_found", False)]
            assert len(found_keywords) > 0, f"No keywords found product {hs_code}"
            
            # Calculations should work for found products
            for keyword, workflow in workflows.items():
                if workflow.get("search_found", False):
                    assert workflow.get("detail_available", False), f"Detail not available for {hs_code} via {keyword}"
                    
                    calculations = workflow.get("calculations", {})
                    assert len(calculations) > 0, f"No calculations for {hs_code} via {keyword}"
                    
                    # Verify FTA benefits
                    usa_calc = next((calc for key, calc in calculations.items() if "USA" in key), None)
                    other_calcs = [calc for key, calc in calculations.items() if "USA" not in key]
                    
                    if usa_calc and other_calcs:
                        # USA should often have lower or equal duty due to FTA
                        usa_duty_rate = usa_calc["total_duty"] / usa_calc["customs_value"]
                        other_duty_rates = [calc["total_duty"] / calc["customs_value"] for calc in other_calcs]
                        
                        min_other_rate = min(other_duty_rates) if other_duty_rates else float('inf')
                        assert usa_duty_rate <= min_other_rate + 0.01  # Small tolerance for rounding


@pytest.mark.e2e
@pytest.mark.integration
class TestExternalServiceIntegration:
    """Test integration with external services and APIs."""
    
    async def test_caching_and_performance_optimization(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test caching mechanisms and performance optimization across components."""
        # 1. Setup test data for caching tests
        cache_test_products = [
            ("8471300000", "Cached product 1"),
            ("6203420000", "Cached product 2"),
            ("8703210000", "Cached product 3")
        ]
        
        for hs_code, description in cache_test_products:
            await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=description
            )
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=5.0
            )
        
        # 2. Test response time improvements with repeated requests
        cache_performance = {}
        
        for hs_code, description in cache_test_products:
            request_times = []
            
            # Make multiple identical requests
            for i in range(3):
                start_time = time.time()
                
                # Test tariff detail caching
                detail_response = test_client.get(f"/api/tariff/code/{hs_code}")
                
                end_time = time.time()
                request_time = end_time - start_time
                
                if detail_response.status_code == 200:
                    request_times.append(request_time)
            
            if request_times:
                cache_performance[hs_code] = {
                    "first_request": request_times[0],
                    "avg_subsequent": sum(request_times[1:]) / len(request_times[1:]) if len(request_times) > 1 else 0,
                    "all_times": request_times
                }
        
        # 3. Verify caching effectiveness
        for hs_code, performance in cache_performance.items():
            # All requests should complete in reasonable time
            first_time = performance["first_request"]
            avg_subsequent = performance["avg_subsequent"]
            
            assert first_time < 2.0, f"First request for {hs_code} took {first_time}s"
            if avg_subsequent > 0:
                assert avg_subsequent < 2.0, f"Subsequent requests for {hs_code} averaged {avg_subsequent}s"
    
    async def test_error_propagation_and_handling(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test error propagation and handling across system boundaries."""
        # 1. Setup test data with some missing components
        error_test_scenarios = [
            ("8471300000", "Complete data", True, True),    # Complete
            ("6203420000", "Missing rates", True, False),   # No duty rates
            ("9999999999", "Non-existent", False, False)    # Doesn't exist
        ]
        
        for hs_code, description, has_tariff, has_duty in error_test_scenarios:
            if has_tariff:
                await DatabaseTestHelper.create_tariff_code(
                    test_session,
                    hs_code=hs_code,
                    description=description
                )
                
                if has_duty:
                    await DatabaseTestHelper.create_duty_rate(
                        test_session,
                        hs_code=hs_code,
                        general_rate=5.0
                    )
        
        # 2. Test error handling across component boundaries
        error_handling_results = {}
        
        for hs_code, description, has_tariff, has_duty in error_test_scenarios:
            scenario_results = {}
            
            # Test detail lookup error handling
            detail_response = test_client.get(f"/api/tariff/code/{hs_code}")
            scenario_results["detail"] = {
                "status": detail_response.status_code
            }
            
            # Test rates lookup error handling
            rates_response = test_client.get(f"/api/duty/rates/{hs_code}")
            scenario_results["rates"] = {
                "status": rates_response.status_code
            }
            
            # Test calculation error handling
            calc_response = test_client.post(
                "/api/duty/calculate",
                json={
                    "hs_code": hs_code,
                    "country_code": "USA",
                    "customs_value": 1000.00
                }
            )
            scenario_results["calculation"] = {
                "status": calc_response.status_code
            }
            
            error_handling_results[hs_code] = scenario_results
        
        # 3. Verify appropriate error handling
        for hs_code, results in error_handling_results.items():
            scenario = next(s for s in error_test_scenarios if s[0] == hs_code)
            _, description, has_tariff, has_duty = scenario
            
            if has_tariff:
                # Should find in detail lookup
                assert results["detail"]["status"] == 200
                assert results["rates"]["status"] == 200
                
                # Calculation should work or fail gracefully
                assert results["calculation"]["status"] in [200, 422]
            else:
                # Non-existent products should return 404
                assert results["detail"]["status"] == 404
                assert results["calculation"]["status"] in [404, 422]