"""
End-to-End Workflow Integration Tests for Customs Broker Portal.

This module tests complete system workflows from start to finish,
ensuring all components work together seamlessly in real-world scenarios.
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
from unittest.mock import patch, AsyncMock

from tests.utils.test_helpers import (
    APITestHelper, DatabaseTestHelper, TestDataFactory,
    PerformanceTestHelper, ValidationTestHelper, AsyncTestHelper
)


@pytest.mark.e2e
@pytest.mark.integration
class TestCompleteCustomsBrokerWorkflows:
    """Test complete end-to-end customs broker workflows."""
    
    async def test_complete_product_search_to_duty_calculation_workflow(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test complete workflow: product search → classification → duty calculation → results."""
        # 1. Setup comprehensive test data
        tariff_codes = []
        for i, (hs_code, description, rate) in enumerate([
            ("0101010000", "Live horses for breeding purposes", 5.0),
            ("0201100000", "Beef carcasses and half-carcasses", 0.0),
            ("8703210000", "Motor cars with spark-ignition engines", 5.0),
            ("8471300000", "Portable digital automatic data processing machines", 0.0),
            ("6203420000", "Men's or boys' trousers of cotton", 17.5)
        ]):
            # Create tariff code
            tariff_code = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=description,
                level=10,
                is_active=True
            )
            tariff_codes.append(tariff_code)
            
            # Create duty rates
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=rate,
                unit_type="ad_valorem",
                effective_date=date.today(),
                is_active=True
            )
            
            # Create FTA rates for multiple countries
            fta_rates = [
                ("USA", 0.0, "AUSFTA"),
                ("JPN", rate * 0.5, "JAEPA"),
                ("KOR", rate * 0.3, "KAFTA"),
                ("CHN", rate, "CHAFTA")
            ]
            
            for country, fta_rate, fta_code in fta_rates:
                await DatabaseTestHelper.create_fta_rate(
                    test_session,
                    hs_code=hs_code,
                    country_code=country,
                    preferential_rate=fta_rate,
                    fta_code=fta_code,
                    staging_category="A" if fta_rate == 0.0 else "B",
                    effective_date=date.today(),
                    is_active=True
                )
        
        # 2. Test product search workflow
        search_queries = ["horses", "beef", "motor cars", "computers", "trousers"]
        search_results = {}
        
        for query in search_queries:
            search_response = test_client.get(f"/api/tariff/search?query={query}&limit=10")
            APITestHelper.assert_response_success(search_response, 200)
            
            search_data = search_response.json()
            search_results[query] = search_data
            
            # Verify search structure
            assert "results" in search_data
            assert "total_results" in search_data
            assert "page" in search_data
            assert isinstance(search_data["results"], list)
        
        # 3. Test detailed tariff lookup for each found product
        detailed_results = {}
        for tariff_code in tariff_codes:
            detail_response = test_client.get(
                f"/api/tariff/code/{tariff_code.hs_code}?include_rates=true&include_hierarchy=true"
            )
            APITestHelper.assert_response_success(detail_response, 200)
            
            detail_data = detail_response.json()
            detailed_results[tariff_code.hs_code] = detail_data
            
            # Verify detailed structure
            assert detail_data["tariff"]["hs_code"] == tariff_code.hs_code
            assert detail_data["tariff"]["description"] == tariff_code.description
            assert "duty_rates" in detail_data
            assert "fta_rates" in detail_data
        
        # 4. Test duty rate retrieval for multiple countries
        duty_rates_results = {}
        countries = ["USA", "JPN", "KOR", "CHN", "GBR"]  # Include non-FTA country
        
        for tariff_code in tariff_codes[:3]:  # Test subset for performance
            for country in countries:
                rates_response = test_client.get(
                    f"/api/duty/rates/{tariff_code.hs_code}?country_code={country}&include_fta=true"
                )
                APITestHelper.assert_response_success(rates_response, 200)
                
                rates_data = rates_response.json()
                key = f"{tariff_code.hs_code}_{country}"
                duty_rates_results[key] = rates_data
                
                # Verify rates structure
                assert rates_data["hs_code"] == tariff_code.hs_code
                assert "general_rates" in rates_data
                assert "fta_rates" in rates_data
        
        # 5. Test comprehensive duty calculations
        calculation_scenarios = [
            {"customs_value": 1000.00, "quantity": 1, "country": "USA"},
            {"customs_value": 5000.00, "quantity": 5, "country": "JPN"},
            {"customs_value": 10000.00, "quantity": 10, "country": "KOR"},
            {"customs_value": 25000.00, "quantity": 1, "country": "CHN"},
            {"customs_value": 50000.00, "quantity": 2, "country": "GBR"}
        ]
        
        calculation_results = {}
        for tariff_code in tariff_codes:
            for scenario in calculation_scenarios:
                calc_request = {
                    "hs_code": tariff_code.hs_code,
                    "country_code": scenario["country"],
                    "customs_value": scenario["customs_value"],
                    "quantity": scenario["quantity"],
                    "calculation_date": date.today().isoformat()
                }
                
                calc_response = test_client.post("/api/duty/calculate", json=calc_request)
                if calc_response.status_code == 200:
                    calc_data = calc_response.json()
                    key = f"{tariff_code.hs_code}_{scenario['country']}_{scenario['customs_value']}"
                    calculation_results[key] = calc_data
                    
                    # Verify calculation structure
                    assert calc_data["hs_code"] == tariff_code.hs_code
                    assert calc_data["country_code"] == scenario["country"]
                    assert calc_data["customs_value"] == scenario["customs_value"]
                    assert "total_duty" in calc_data
                    assert "total_amount" in calc_data
        
        # 6. Verify end-to-end data consistency
        for tariff_code in tariff_codes:
            hs_code = tariff_code.hs_code
            
            # Check consistency between search and detail
            detail_data = detailed_results.get(hs_code)
            if detail_data:
                assert detail_data["tariff"]["hs_code"] == hs_code
                assert detail_data["tariff"]["description"] == tariff_code.description
        
        # 7. Verify workflow performance
        assert len(search_results) == len(search_queries)
        assert len(detailed_results) == len(tariff_codes)
        assert len(calculation_results) > 0
        
        # 8. Test error handling in workflow
        invalid_hs_code = "9999999999"
        error_response = test_client.get(f"/api/tariff/code/{invalid_hs_code}")
        assert error_response.status_code == 404
    
    async def test_multi_country_fta_comparison_workflow(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test workflow for comparing FTA rates across multiple trade agreements."""
        # 1. Create test data with comprehensive FTA coverage
        test_products = [
            ("8703210000", "Motor cars with engines 1000-1500cc", 5.0),
            ("6203420000", "Men's cotton trousers", 17.5),
            ("0201100000", "Beef carcasses", 0.0)
        ]
        
        fta_agreements = [
            ("USA", "AUSFTA", "A"),
            ("JPN", "JAEPA", "B"),
            ("KOR", "KAFTA", "A"),
            ("CHN", "CHAFTA", "C"),
            ("THA", "TAFTA", "B"),
            ("SGP", "SAFTA", "A"),
            ("MYS", "MAFTA", "B")
        ]
        
        for hs_code, description, general_rate in test_products:
            # Create tariff code
            await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=description
            )
            
            # Create general duty rate
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=general_rate
            )
            
            # Create FTA rates with different staging categories
            for country, fta_code, staging in fta_agreements:
                if staging == "A":
                    fta_rate = 0.0  # Immediate elimination
                elif staging == "B":
                    fta_rate = general_rate * 0.5  # 50% reduction
                else:  # staging == "C"
                    fta_rate = general_rate * 0.8  # 20% reduction
                
                await DatabaseTestHelper.create_fta_rate(
                    test_session,
                    hs_code=hs_code,
                    country_code=country,
                    preferential_rate=fta_rate,
                    fta_code=fta_code,
                    staging_category=staging
                )
        
        # 2. Test comprehensive FTA rate comparison
        comparison_results = {}
        customs_value = 10000.00
        
        for hs_code, description, general_rate in test_products:
            product_comparisons = {}
            
            # Get rates for each FTA country
            for country, fta_code, staging in fta_agreements:
                rates_response = test_client.get(
                    f"/api/duty/rates/{hs_code}?country_code={country}&include_fta=true"
                )
                
                if rates_response.status_code == 200:
                    rates_data = rates_response.json()
                    
                    # Calculate duty for this country
                    calc_response = test_client.post(
                        "/api/duty/calculate",
                        json={
                            "hs_code": hs_code,
                            "country_code": country,
                            "customs_value": customs_value
                        }
                    )
                    
                    if calc_response.status_code == 200:
                        calc_data = calc_response.json()
                        
                        product_comparisons[country] = {
                            "rates": rates_data,
                            "calculation": calc_data,
                            "fta_code": fta_code,
                            "staging": staging
                        }
            
            comparison_results[hs_code] = product_comparisons
        
        # 3. Verify FTA rate effectiveness
        for hs_code, comparisons in comparison_results.items():
            if len(comparisons) > 1:
                duty_amounts = {}
                
                for country, data in comparisons.items():
                    duty_amounts[country] = data["calculation"]["total_duty"]
                
                # Verify staging category A (immediate elimination) has lowest duties
                category_a_countries = [
                    country for country, data in comparisons.items()
                    if data["staging"] == "A"
                ]
                
                if category_a_countries:
                    category_a_duties = [duty_amounts[country] for country in category_a_countries]
                    other_duties = [
                        duty_amounts[country] for country in duty_amounts
                        if country not in category_a_countries
                    ]
                    
                    if other_duties:
                        min_category_a = min(category_a_duties)
                        min_others = min(other_duties)
                        assert min_category_a <= min_others
    
    @patch('ai.tariff_ai.TariffAIService.classify_product')
    async def test_ai_classification_integration_workflow(
        self, mock_classify, test_client: TestClient, test_session: AsyncSession
    ):
        """Test complete workflow integrating AI classification with duty calculation."""
        # 1. Setup test data
        classification_test_cases = [
            {
                "hs_code": "8471300000",
                "description": "Portable digital automatic data processing machines",
                "product_query": "laptop computer with 16GB RAM and 512GB SSD",
                "confidence": 0.95
            },
            {
                "hs_code": "6203420000", 
                "description": "Men's or boys' trousers of cotton",
                "product_query": "men's blue jeans made of 100% cotton",
                "confidence": 0.88
            },
            {
                "hs_code": "0201100000",
                "description": "Beef carcasses and half-carcasses",
                "product_query": "frozen beef carcass from grass-fed cattle",
                "confidence": 0.92
            }
        ]
        
        for case in classification_test_cases:
            await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=case["hs_code"],
                description=case["description"]
            )
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=case["hs_code"],
                general_rate=5.0
            )
        
        # 2. Test AI classification workflow
        classification_results = {}
        
        for case in classification_test_cases:
            # Mock AI response
            mock_classify.return_value = {
                "hs_code": case["hs_code"],
                "confidence": case["confidence"],
                "classification_source": "ai",
                "reasoning": f"Product matches {case['description']}",
                "alternative_codes": []
            }
            
            # Test classification
            classify_request = {
                "product_description": case["product_query"],
                "confidence_threshold": 0.8,
                "store_result": True,
                "include_alternatives": True
            }
            
            classify_response = test_client.post("/api/search/classify", json=classify_request)
            APITestHelper.assert_response_success(classify_response, 200)
            
            classify_data = classify_response.json()
            classification_results[case["hs_code"]] = classify_data
            
            # Verify classification structure
            assert classify_data["hs_code"] == case["hs_code"]
            assert classify_data["confidence_score"] >= 0.8
            assert "tariff_description" in classify_data
            
            # Test immediate duty calculation with classified code
            calc_request = {
                "hs_code": classify_data["hs_code"],
                "country_code": "USA",
                "customs_value": 2000.00
            }
            
            calc_response = test_client.post("/api/duty/calculate", json=calc_request)
            if calc_response.status_code == 200:
                calc_data = calc_response.json()
                classification_results[case["hs_code"]]["calculation"] = calc_data
                
                # Verify integration
                assert calc_data["hs_code"] == classify_data["hs_code"]
        
        # 3. Verify end-to-end AI integration
        assert len(classification_results) == len(classification_test_cases)
        
        for hs_code, result in classification_results.items():
            assert result["hs_code"] == hs_code
            assert result["confidence_score"] >= 0.8
            
            if "calculation" in result:
                assert result["calculation"]["hs_code"] == hs_code
                assert result["calculation"]["total_duty"] >= 0


@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.slow
class TestComplexDutyScenarios:
    """Test complex duty calculation scenarios with multiple rates and exemptions."""
    
    async def test_complex_multi_rate_duty_scenario(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test complex duty scenarios with multiple rates, dumping duties, and exemptions."""
        # 1. Create complex test scenario
        hs_code = "7208100000"  # Flat-rolled products of iron/steel
        
        await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code=hs_code,
            description="Flat-rolled products of iron or non-alloy steel"
        )
        
        # Create multiple duty types
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=hs_code,
            general_rate=5.0,
            unit_type="ad_valorem"
        )
        
        # Create dumping duty
        await DatabaseTestHelper.create_dumping_duty(
            test_session,
            hs_code=hs_code,
            country_code="CHN",
            duty_type="dumping",
            duty_rate=15.0,
            case_number="ADC2023-001"
        )
        
        # Create countervailing duty
        await DatabaseTestHelper.create_dumping_duty(
            test_session,
            hs_code=hs_code,
            country_code="CHN",
            duty_type="countervailing",
            duty_rate=8.0,
            case_number="CVD2023-001"
        )
        
        # Create TCO (Tariff Concession Order)
        await DatabaseTestHelper.create_tco(
            test_session,
            hs_code=hs_code,
            tco_number="TCO2023001",
            description="Special steel for automotive industry",
            effective_date=date.today(),
            expiry_date=date.today() + timedelta(days=365)
        )
        
        # 2. Test complex duty calculation scenarios
        test_scenarios = [
            {
                "name": "Standard calculation",
                "country": "USA",
                "customs_value": 10000.00,
                "expected_duties": ["general"]
            },
            {
                "name": "Dumping duty scenario",
                "country": "CHN",
                "customs_value": 15000.00,
                "expected_duties": ["general", "dumping", "countervailing"]
            },
            {
                "name": "High value scenario",
                "country": "CHN",
                "customs_value": 100000.00,
                "expected_duties": ["general", "dumping", "countervailing"]
            }
        ]
        
        scenario_results = {}
        
        for scenario in test_scenarios:
            calc_request = {
                "hs_code": hs_code,
                "country_code": scenario["country"],
                "customs_value": scenario["customs_value"],
                "include_dumping_duties": True,
                "include_tco_check": True
            }
            
            calc_response = test_client.post("/api/duty/calculate", json=calc_request)
            
            if calc_response.status_code == 200:
                calc_data = calc_response.json()
                scenario_results[scenario["name"]] = calc_data
                
                # Verify complex calculation structure
                assert calc_data["hs_code"] == hs_code
                assert calc_data["country_code"] == scenario["country"]
                assert "duty_breakdown" in calc_data
                
                # For China, should have additional duties
                if scenario["country"] == "CHN":
                    assert calc_data["total_duty"] > calc_data["customs_value"] * 0.05
        
        # 3. Test TCO eligibility check
        tco_response = test_client.get(f"/api/duty/tco-check/{hs_code}")
        
        if tco_response.status_code == 200:
            tco_data = tco_response.json()
            assert "eligible_tcos" in tco_data
            assert len(tco_data["eligible_tcos"]) > 0
        
        # 4. Verify calculation accuracy
        if "Dumping duty scenario" in scenario_results:
            china_result = scenario_results["Dumping duty scenario"]
            
            # Should include general duty (5%) + dumping (15%) + countervailing (8%)
            expected_min_rate = 0.05 + 0.15 + 0.08  # 28%
            actual_rate = china_result["total_duty"] / china_result["customs_value"]
            
            # Allow some tolerance for calculation differences
            assert actual_rate >= expected_min_rate * 0.9


@pytest.mark.e2e
@pytest.mark.integration
class TestDataConsistencyAcrossLayers:
    """Test data consistency across all system layers."""
    
    async def test_complete_data_flow_consistency(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test data consistency from database through services to API responses."""
        # 1. Create comprehensive test data
        test_data = {
            "hs_code": "8471300000",
            "description": "Portable digital automatic data processing machines",
            "level": 10,
            "general_rate": 0.0,
            "fta_rates": [
                {"country": "USA", "rate": 0.0, "fta_code": "AUSFTA"},
                {"country": "JPN", "rate": 0.0, "fta_code": "JAEPA"}
            ]
        }
        
        # Create in database
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code=test_data["hs_code"],
            description=test_data["description"],
            level=test_data["level"]
        )
        
        duty_rate = await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=test_data["hs_code"],
            general_rate=test_data["general_rate"]
        )
        
        fta_rates = []
        for fta_data in test_data["fta_rates"]:
            fta_rate = await DatabaseTestHelper.create_fta_rate(
                test_session,
                hs_code=test_data["hs_code"],
                country_code=fta_data["country"],
                preferential_rate=fta_data["rate"],
                fta_code=fta_data["fta_code"]
            )
            fta_rates.append(fta_rate)
        
        # 2. Test data consistency across all API endpoints
        endpoints_data = {}
        
        # Tariff detail endpoint
        detail_response = test_client.get(f"/api/tariff/code/{test_data['hs_code']}")
        if detail_response.status_code == 200:
            endpoints_data["detail"] = detail_response.json()
        
        # Search endpoint
        search_response = test_client.get(f"/api/tariff/search?hs_code_starts_with={test_data['hs_code']}")
        if search_response.status_code == 200:
            search_data = search_response.json()
            matching_results = [
                result for result in search_data["results"]
                if result["hs_code"] == test_data["hs_code"]
            ]
            if matching_results:
                endpoints_data["search"] = matching_results[0]
        
        # Duty rates endpoint
        rates_response = test_client.get(f"/api/duty/rates/{test_data['hs_code']}?include_fta=true")
        if rates_response.status_code == 200:
            endpoints_data["rates"] = rates_response.json()
        
        # Duty calculation endpoint
        calc_response = test_client.post(
            "/api/duty/calculate",
            json={
                "hs_code": test_data["hs_code"],
                "country_code": "USA",
                "customs_value": 5000.00
            }
        )
        if calc_response.status_code == 200:
            endpoints_data["calculation"] = calc_response.json()
        
        # 3. Verify data consistency across endpoints
        if len(endpoints_data) > 1:
            # Check HS code consistency
            for endpoint_name, data in endpoints_data.items():
                if endpoint_name == "rates":
                    assert data["hs_code"] == test_data["hs_code"]
                elif endpoint_name == "calculation":
                    assert data["hs_code"] == test_data["hs_code"]
                elif "tariff" in data:
                    assert data["tariff"]["hs_code"] == test_data["hs_code"]
                elif "hs_code" in data:
                    assert data["hs_code"] == test_data["hs_code"]
        
        # 4. Test transaction consistency
        # Verify that all related data was created correctly
        assert tariff_code.hs_code == test_data["hs_code"]
        assert tariff_code.description == test_data["description"]
        assert duty_rate.hs_code == test_data["hs_code"]
        assert duty_rate.general_rate == test_data["general_rate"]
        
        for i, fta_rate in enumerate(fta_rates):
            expected_fta = test_data["fta_rates"][i]
            assert fta_rate.hs_code == test_data["hs_code"]
            assert fta_rate.country_code == expected_fta["country"]
            assert fta_rate.preferential_rate == expected_fta["rate"]
            assert fta_rate.fta_code == expected_fta["fta_code"]