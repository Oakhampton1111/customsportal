"""
End-to-End User Journey Tests for Customs Broker Portal.

This module tests complete user journeys from login to task completion,
including error recovery, session management, and real-world usage patterns.
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
from unittest.mock import patch

from tests.utils.test_helpers import (
    APITestHelper, DatabaseTestHelper, TestDataFactory,
    PerformanceTestHelper, ValidationTestHelper
)


@pytest.mark.e2e
@pytest.mark.integration
class TestCompleteUserJourneys:
    """Test complete user journeys from start to finish."""
    
    async def test_new_customs_broker_onboarding_journey(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test complete journey of a new customs broker using the system."""
        # 1. Setup realistic product data for new broker
        onboarding_products = [
            {
                "hs_code": "8471300000",
                "description": "Portable digital automatic data processing machines",
                "general_rate": 0.0,
                "common_queries": ["laptop", "computer", "notebook"]
            },
            {
                "hs_code": "6203420000",
                "description": "Men's or boys' trousers of cotton",
                "general_rate": 17.5,
                "common_queries": ["jeans", "pants", "trousers"]
            },
            {
                "hs_code": "8703210000",
                "description": "Motor cars with spark-ignition engines",
                "general_rate": 5.0,
                "common_queries": ["car", "vehicle", "automobile"]
            },
            {
                "hs_code": "0201100000",
                "description": "Beef carcasses and half-carcasses",
                "general_rate": 0.0,
                "common_queries": ["beef", "meat", "carcass"]
            }
        ]
        
        # Create comprehensive test data
        for product in onboarding_products:
            await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=product["hs_code"],
                description=product["description"],
                level=10,
                is_active=True
            )
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=product["hs_code"],
                general_rate=product["general_rate"],
                unit_type="ad_valorem"
            )
            
            # Add FTA rates for common countries
            fta_countries = [
                ("USA", 0.0, "AUSFTA"),
                ("JPN", product["general_rate"] * 0.5, "JAEPA"),
                ("KOR", product["general_rate"] * 0.3, "KAFTA")
            ]
            
            for country, rate, fta_code in fta_countries:
                await DatabaseTestHelper.create_fta_rate(
                    test_session,
                    hs_code=product["hs_code"],
                    country_code=country,
                    preferential_rate=rate,
                    fta_code=fta_code
                )
        
        # 2. Simulate new broker's first session - exploration phase
        exploration_results = {}
        
        # New broker starts with general searches
        general_searches = ["electronics", "clothing", "automotive", "food"]
        
        for search_term in general_searches:
            search_response = test_client.get(f"/api/tariff/search?query={search_term}&limit=10")
            APITestHelper.assert_response_success(search_response, 200)
            
            search_data = search_response.json()
            exploration_results[search_term] = {
                "total_results": search_data["total_results"],
                "results_count": len(search_data["results"])
            }
            
            # Verify search returns reasonable results
            assert search_data["total_results"] >= 0
            assert len(search_data["results"]) <= 10
        
        # 3. Simulate learning phase - specific product lookups
        learning_results = {}
        
        for product in onboarding_products:
            # Try different search approaches a new broker might use
            for query in product["common_queries"]:
                search_response = test_client.get(f"/api/tariff/search?query={query}&limit=5")
                
                if search_response.status_code == 200:
                    search_data = search_response.json()
                    
                    # Look for the expected product in results
                    found_product = None
                    for result in search_data["results"]:
                        if result["hs_code"] == product["hs_code"]:
                            found_product = result
                            break
                    
                    learning_results[f"{product['hs_code']}_{query}"] = {
                        "found": found_product is not None,
                        "total_results": search_data["total_results"]
                    }
        
        # 4. Simulate working phase - detailed analysis
        working_results = {}
        
        for product in onboarding_products:
            # Get detailed product information
            detail_response = test_client.get(
                f"/api/tariff/code/{product['hs_code']}?include_rates=true"
            )
            APITestHelper.assert_response_success(detail_response, 200)
            
            detail_data = detail_response.json()
            
            # Get rates for multiple countries
            countries_analysis = {}
            for country in ["USA", "JPN", "KOR", "GBR"]:
                rates_response = test_client.get(
                    f"/api/duty/rates/{product['hs_code']}?country_code={country}&include_fta=true"
                )
                
                if rates_response.status_code == 200:
                    rates_data = rates_response.json()
                    countries_analysis[country] = rates_data
            
            # Calculate duties for typical scenarios
            calculation_scenarios = [
                {"value": 1000.00, "country": "USA"},
                {"value": 5000.00, "country": "JPN"},
                {"value": 10000.00, "country": "KOR"},
                {"value": 2500.00, "country": "GBR"}
            ]
            
            calculations = {}
            for scenario in calculation_scenarios:
                calc_response = test_client.post(
                    "/api/duty/calculate",
                    json={
                        "hs_code": product["hs_code"],
                        "country_code": scenario["country"],
                        "customs_value": scenario["value"]
                    }
                )
                
                if calc_response.status_code == 200:
                    calc_data = calc_response.json()
                    calculations[f"{scenario['country']}_{scenario['value']}"] = calc_data
            
            working_results[product["hs_code"]] = {
                "detail": detail_data,
                "rates": countries_analysis,
                "calculations": calculations
            }
        
        # 5. Verify complete journey success
        # Exploration phase should return results
        assert len(exploration_results) == len(general_searches)
        
        # Learning phase should find most products
        successful_searches = sum(1 for result in learning_results.values() if result["found"])
        total_searches = len(learning_results)
        search_success_rate = successful_searches / total_searches if total_searches > 0 else 0
        
        # Should find at least 50% of products through common search terms
        assert search_success_rate >= 0.5, f"Search success rate {search_success_rate} too low"
        
        # Working phase should provide comprehensive data
        assert len(working_results) == len(onboarding_products)
        
        for hs_code, results in working_results.items():
            assert "detail" in results
            assert "rates" in results
            assert "calculations" in results
            
            # Should have detail data
            assert results["detail"]["tariff"]["hs_code"] == hs_code
            
            # Should have rates for multiple countries
            assert len(results["rates"]) > 0
            
            # Should have successful calculations
            assert len(results["calculations"]) > 0
    
    async def test_experienced_broker_daily_workflow(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test typical daily workflow of an experienced customs broker."""
        # 1. Setup data for experienced broker workflow
        daily_products = [
            ("8471300000", "Laptops for corporate client", 15000.00),
            ("6203420000", "Fashion import batch", 25000.00),
            ("8703210000", "Vehicle import", 45000.00),
            ("0201100000", "Meat products", 8000.00),
            ("8517120000", "Mobile phones", 30000.00)
        ]
        
        for hs_code, description, _ in daily_products:
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
            
            # Add FTA rates
            await DatabaseTestHelper.create_fta_rate(
                test_session,
                hs_code=hs_code,
                country_code="USA",
                preferential_rate=0.0,
                fta_code="AUSFTA"
            )
        
        # 2. Simulate morning routine - quick status checks
        morning_routine = {}
        
        # Quick searches for pending shipments
        pending_shipments = ["8471", "6203", "8703"]
        
        for shipment_code in pending_shipments:
            search_response = test_client.get(f"/api/tariff/search?hs_code_starts_with={shipment_code}")
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                morning_routine[shipment_code] = {
                    "found_codes": len(search_data["results"]),
                    "search_time": "morning"
                }
        
        # 3. Simulate active work period - detailed calculations
        active_work = {}
        
        for hs_code, description, customs_value in daily_products:
            # Experienced broker checks multiple countries quickly
            countries = ["USA", "JPN", "CHN", "GBR"]
            country_comparisons = {}
            
            for country in countries:
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
                    country_comparisons[country] = {
                        "total_duty": calc_data["total_duty"],
                        "total_amount": calc_data["total_amount"]
                    }
            
            # Get detailed breakdown for best option
            if country_comparisons:
                # Find country with lowest total cost
                best_country = min(
                    country_comparisons.keys(),
                    key=lambda c: country_comparisons[c]["total_amount"]
                )
                
                breakdown_response = test_client.get(
                    "/api/duty/breakdown",
                    params={
                        "hs_code": hs_code,
                        "country_code": best_country,
                        "customs_value": customs_value
                    }
                )
                
                breakdown_data = None
                if breakdown_response.status_code == 200:
                    breakdown_data = breakdown_response.json()
                
                active_work[hs_code] = {
                    "comparisons": country_comparisons,
                    "best_country": best_country,
                    "breakdown": breakdown_data,
                    "customs_value": customs_value
                }
        
        # 4. Simulate end-of-day review - batch operations
        end_of_day = {}
        
        # Review all calculations for the day
        daily_summary = {
            "total_shipments": len(daily_products),
            "total_value": sum(value for _, _, value in daily_products),
            "countries_analyzed": set(),
            "total_duties": 0.0
        }
        
        for hs_code, work_data in active_work.items():
            if work_data["comparisons"]:
                daily_summary["countries_analyzed"].update(work_data["comparisons"].keys())
                
                # Add duty from best option
                best_country = work_data["best_country"]
                if best_country in work_data["comparisons"]:
                    daily_summary["total_duties"] += work_data["comparisons"][best_country]["total_duty"]
        
        end_of_day["summary"] = daily_summary
        
        # 5. Verify experienced broker workflow efficiency
        # Morning routine should be quick and effective
        assert len(morning_routine) == len(pending_shipments)
        
        # Active work should cover all products
        assert len(active_work) == len(daily_products)
        
        # Each product should have country comparisons
        for hs_code, work_data in active_work.items():
            assert len(work_data["comparisons"]) > 0
            assert "best_country" in work_data
            
            # Should identify cost savings through FTA
            usa_comparison = work_data["comparisons"].get("USA")
            other_comparisons = [
                comp for country, comp in work_data["comparisons"].items()
                if country != "USA"
            ]
            
            if usa_comparison and other_comparisons:
                # USA should often be competitive due to FTA
                usa_total = usa_comparison["total_amount"]
                other_totals = [comp["total_amount"] for comp in other_comparisons]
                
                # USA should be among the better options
                assert usa_total <= max(other_totals)
        
        # End of day summary should be comprehensive
        assert daily_summary["total_shipments"] == len(daily_products)
        assert daily_summary["total_value"] > 0
        assert len(daily_summary["countries_analyzed"]) >= 2
    
    async def test_error_recovery_and_graceful_degradation(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test user journey with errors and system recovery."""
        # 1. Setup partial data to simulate real-world incomplete scenarios
        partial_products = [
            ("8471300000", "Complete product", True, True),  # Complete data
            ("6203420000", "No rates product", True, False),  # No duty rates
            ("8703210000", "Inactive product", False, True),  # Inactive
        ]
        
        for hs_code, description, is_active, has_rates in partial_products:
            await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=description,
                is_active=is_active
            )
            
            if has_rates:
                await DatabaseTestHelper.create_duty_rate(
                    test_session,
                    hs_code=hs_code,
                    general_rate=5.0
                )
        
        # 2. Test graceful handling of missing data
        error_scenarios = {}
        
        for hs_code, description, is_active, has_rates in partial_products:
            scenario_results = {}
            
            # Test tariff lookup
            detail_response = test_client.get(f"/api/tariff/code/{hs_code}")
            scenario_results["detail_status"] = detail_response.status_code
            
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                scenario_results["detail_data"] = detail_data
            
            # Test rates lookup
            rates_response = test_client.get(f"/api/duty/rates/{hs_code}")
            scenario_results["rates_status"] = rates_response.status_code
            
            if rates_response.status_code == 200:
                rates_data = rates_response.json()
                scenario_results["rates_data"] = rates_data
            
            # Test duty calculation
            calc_response = test_client.post(
                "/api/duty/calculate",
                json={
                    "hs_code": hs_code,
                    "country_code": "USA",
                    "customs_value": 1000.00
                }
            )
            scenario_results["calc_status"] = calc_response.status_code
            
            if calc_response.status_code == 200:
                calc_data = calc_response.json()
                scenario_results["calc_data"] = calc_data
            
            error_scenarios[hs_code] = scenario_results
        
        # 3. Test invalid input handling
        invalid_scenarios = {}
        
        # Invalid HS codes
        invalid_codes = ["invalid", "123", "99999999999", ""]
        
        for invalid_code in invalid_codes:
            if invalid_code:  # Skip empty string for URL
                detail_response = test_client.get(f"/api/tariff/code/{invalid_code}")
                invalid_scenarios[f"detail_{invalid_code}"] = detail_response.status_code
                
                calc_response = test_client.post(
                    "/api/duty/calculate",
                    json={
                        "hs_code": invalid_code,
                        "country_code": "USA",
                        "customs_value": 1000.00
                    }
                )
                invalid_scenarios[f"calc_{invalid_code}"] = calc_response.status_code
        
        # Invalid calculation parameters
        invalid_calc_scenarios = [
            {"hs_code": "8471300000", "country_code": "INVALID", "customs_value": 1000.00},
            {"hs_code": "8471300000", "country_code": "USA", "customs_value": -1000.00},
            {"hs_code": "8471300000", "country_code": "USA", "customs_value": 0},
        ]
        
        for i, invalid_params in enumerate(invalid_calc_scenarios):
            calc_response = test_client.post("/api/duty/calculate", json=invalid_params)
            invalid_scenarios[f"invalid_calc_{i}"] = calc_response.status_code
        
        # 4. Test search with no results
        no_results_searches = ["nonexistentproduct", "zzzzzzz", "12345678901234567890"]
        
        for search_term in no_results_searches:
            search_response = test_client.get(f"/api/tariff/search?query={search_term}")
            
            if search_response.status_code == 200:
                search_data = search_response.json()
                invalid_scenarios[f"search_{search_term}"] = {
                    "status": search_response.status_code,
                    "results": search_data["total_results"]
                }
        
        # 5. Verify error handling and recovery
        # Complete product should work fully
        complete_results = error_scenarios["8471300000"]
        assert complete_results["detail_status"] == 200
        assert complete_results["rates_status"] == 200
        assert complete_results["calc_status"] == 200
        
        # Partial products should handle gracefully
        no_rates_results = error_scenarios["6203420000"]
        assert no_rates_results["detail_status"] == 200  # Should still show tariff info
        assert no_rates_results["rates_status"] == 200  # Should return empty rates
        # Calculation might fail or return default - either is acceptable
        assert no_rates_results["calc_status"] in [200, 422, 404]
        
        # Invalid inputs should return appropriate error codes
        for scenario, status_code in invalid_scenarios.items():
            if isinstance(status_code, int):
                assert status_code in [400, 404, 422], f"Scenario {scenario} returned unexpected status {status_code}"
            elif isinstance(status_code, dict):
                # Search scenarios
                assert status_code["status"] == 200
                assert status_code["results"] == 0
        
        # System should remain stable throughout error scenarios
        # Test that system still works after errors
        recovery_response = test_client.get("/api/tariff/code/8471300000")
        APITestHelper.assert_response_success(recovery_response, 200)
    
    async def test_session_management_and_data_persistence(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test user session management and data persistence across requests."""
        # 1. Setup test data
        session_products = [
            ("8471300000", "Session test product 1"),
            ("6203420000", "Session test product 2")
        ]
        
        for hs_code, description in session_products:
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
        
        # 2. Test data consistency across multiple requests
        consistency_results = {}
        
        for hs_code, description in session_products:
            # Make multiple requests for the same data
            requests = []
            
            for i in range(5):
                detail_response = test_client.get(f"/api/tariff/code/{hs_code}")
                
                if detail_response.status_code == 200:
                    detail_data = detail_response.json()
                    requests.append({
                        "request_num": i,
                        "hs_code": detail_data["tariff"]["hs_code"],
                        "description": detail_data["tariff"]["description"]
                    })
            
            consistency_results[hs_code] = requests
        
        # 3. Test concurrent session simulation
        concurrent_results = {}
        
        # Simulate multiple users accessing the same data
        async def simulate_concurrent_user(user_id: int):
            user_results = {}
            
            for hs_code, _ in session_products:
                # Each user performs typical operations
                search_response = test_client.get(f"/api/tariff/search?query={hs_code[:4]}")
                detail_response = test_client.get(f"/api/tariff/code/{hs_code}")
                calc_response = test_client.post(
                    "/api/duty/calculate",
                    json={
                        "hs_code": hs_code,
                        "country_code": "USA",
                        "customs_value": 1000.00 * (user_id + 1)
                    }
                )
                
                user_results[hs_code] = {
                    "search_status": search_response.status_code,
                    "detail_status": detail_response.status_code,
                    "calc_status": calc_response.status_code
                }
            
            return {"user_id": user_id, "results": user_results}
        
        # Simulate 3 concurrent users
        user_tasks = [simulate_concurrent_user(i) for i in range(3)]
        
        # Execute concurrently (simulated since we're using sync client)
        for task in user_tasks:
            result = task  # In real async, this would be awaited
            concurrent_results[result["user_id"]] = result["results"]
        
        # 4. Verify session management
        # Data consistency across requests
        for hs_code, requests in consistency_results.items():
            if len(requests) > 1:
                # All requests should return the same data
                first_request = requests[0]
                
                for request in requests[1:]:
                    assert request["hs_code"] == first_request["hs_code"]
                    assert request["description"] == first_request["description"]
        
        # Concurrent access should work without conflicts
        for user_id, user_results in concurrent_results.items():
            for hs_code, statuses in user_results.items():
                # All operations should succeed or fail consistently
                assert statuses["search_status"] == 200
                assert statuses["detail_status"] == 200
                assert statuses["calc_status"] in [200, 422]  # 422 acceptable for missing rates
        
        # No user should affect another user's results
        user_0_results = concurrent_results[0]
        user_1_results = concurrent_results[1]
        
        # Results should be independent (different customs values should give different calculations)
        for hs_code in session_products:
            hs_code_val = hs_code[0]
            
            # Both users should get the same tariff data
            assert user_0_results[hs_code_val]["detail_status"] == user_1_results[hs_code_val]["detail_status"]
            
            # But calculations might differ due to different customs values
            # This is expected and correct behavior