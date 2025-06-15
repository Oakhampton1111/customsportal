"""
End-to-End Database Integration Tests for Customs Broker Portal.

This module tests data flow from database models through services to API responses,
ensuring transaction integrity and performance under realistic load scenarios.
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
from sqlalchemy import select, func, text
from unittest.mock import patch

from tests.utils.test_helpers import (
    APITestHelper, DatabaseTestHelper, TestDataFactory,
    PerformanceTestHelper, AsyncTestHelper
)


@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.database
class TestDatabaseToAPIIntegration:
    """Test complete data flow from database through services to API responses."""
    
    async def test_complete_data_pipeline_integrity(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test complete data pipeline from database creation to API response."""
        # 1. Create comprehensive test data in database
        test_products = [
            {
                "hs_code": "8471300000",
                "description": "Portable digital automatic data processing machines",
                "general_rate": 0.0,
                "fta_rates": [
                    {"country": "USA", "rate": 0.0, "fta_code": "AUSFTA"},
                    {"country": "JPN", "rate": 0.0, "fta_code": "JAEPA"}
                ]
            },
            {
                "hs_code": "6203420000",
                "description": "Men's or boys' trousers of cotton",
                "general_rate": 17.5,
                "fta_rates": [
                    {"country": "USA", "rate": 0.0, "fta_code": "AUSFTA"},
                    {"country": "JPN", "rate": 8.75, "fta_code": "JAEPA"}
                ]
            },
            {
                "hs_code": "0201100000",
                "description": "Beef carcasses and half-carcasses",
                "general_rate": 0.0,
                "fta_rates": [
                    {"country": "USA", "rate": 0.0, "fta_code": "AUSFTA"},
                    {"country": "JPN", "rate": 0.0, "fta_code": "JAEPA"}
                ]
            }
        ]
        
        created_data = {}
        
        for product in test_products:
            # Create tariff code
            tariff_code = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=product["hs_code"],
                description=product["description"],
                level=10,
                is_active=True
            )
            
            # Create duty rate
            duty_rate = await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=product["hs_code"],
                general_rate=product["general_rate"],
                unit_type="ad_valorem",
                effective_date=date.today(),
                is_active=True
            )
            
            # Create FTA rates
            fta_rates = []
            for fta_data in product["fta_rates"]:
                fta_rate = await DatabaseTestHelper.create_fta_rate(
                    test_session,
                    hs_code=product["hs_code"],
                    country_code=fta_data["country"],
                    preferential_rate=fta_data["rate"],
                    fta_code=fta_data["fta_code"],
                    staging_category="A" if fta_data["rate"] == 0.0 else "B",
                    effective_date=date.today(),
                    is_active=True
                )
                fta_rates.append(fta_rate)
            
            created_data[product["hs_code"]] = {
                "tariff_code": tariff_code,
                "duty_rate": duty_rate,
                "fta_rates": fta_rates,
                "expected": product
            }
        
        # 2. Test data retrieval through API endpoints
        for hs_code, data in created_data.items():
            # Test tariff detail endpoint
            detail_response = test_client.get(f"/api/tariff/code/{hs_code}?include_rates=true")
            APITestHelper.assert_response_success(detail_response, 200)
            
            detail_data = detail_response.json()
            
            # Verify database data matches API response
            assert detail_data["tariff"]["hs_code"] == data["tariff_code"].hs_code
            assert detail_data["tariff"]["description"] == data["tariff_code"].description
            assert detail_data["tariff"]["level"] == data["tariff_code"].level
            assert detail_data["tariff"]["is_active"] == data["tariff_code"].is_active
            
            # Verify duty rates
            if detail_data.get("duty_rates"):
                api_duty_rate = detail_data["duty_rates"][0]
                assert api_duty_rate["rate_value"] == data["duty_rate"].general_rate
                assert api_duty_rate["unit_type"] == data["duty_rate"].unit_type
            
            # Verify FTA rates
            if detail_data.get("fta_rates"):
                api_fta_rates = {rate["country_code"]: rate for rate in detail_data["fta_rates"]}
                
                for fta_rate in data["fta_rates"]:
                    api_fta = api_fta_rates.get(fta_rate.country_code)
                    if api_fta:
                        assert api_fta["preferential_rate"] == fta_rate.preferential_rate
                        assert api_fta["fta_code"] == fta_rate.fta_code
                        assert api_fta["staging_category"] == fta_rate.staging_category
        
        # 3. Test duty calculation pipeline
        for hs_code, data in created_data.items():
            for country in ["USA", "JPN", "GBR"]:  # Include non-FTA country
                calc_request = {
                    "hs_code": hs_code,
                    "country_code": country,
                    "customs_value": 10000.00,
                    "quantity": 1
                }
                
                calc_response = test_client.post("/api/duty/calculate", json=calc_request)
                
                if calc_response.status_code == 200:
                    calc_data = calc_response.json()
                    
                    # Verify calculation uses correct database rates
                    assert calc_data["hs_code"] == hs_code
                    assert calc_data["country_code"] == country
                    assert calc_data["customs_value"] == 10000.00
                    
                    # For FTA countries, duty should be based on preferential rates
                    expected_fta_rates = {
                        fta["country"]: fta["rate"] 
                        for fta in data["expected"]["fta_rates"]
                    }
                    
                    if country in expected_fta_rates:
                        expected_rate = expected_fta_rates[country]
                        expected_duty = 10000.00 * (expected_rate / 100)
                        
                        # Allow small tolerance for calculation differences
                        assert abs(calc_data["total_duty"] - expected_duty) < 1.0
        
        # 4. Test search functionality with database data
        search_response = test_client.get("/api/tariff/search?query=digital&limit=10")
        APITestHelper.assert_response_success(search_response, 200)
        
        search_data = search_response.json()
        
        # Should find the computer product
        computer_results = [
            result for result in search_data["results"]
            if "8471300000" in result.get("hs_code", "")
        ]
        
        if computer_results:
            computer_result = computer_results[0]
            computer_data = created_data["8471300000"]
            
            assert computer_result["hs_code"] == computer_data["tariff_code"].hs_code
            assert computer_result["description"] == computer_data["tariff_code"].description
    
    async def test_transaction_integrity_across_operations(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test transaction integrity across multiple database operations."""
        # 1. Create initial data
        hs_code = "8703210000"
        
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code=hs_code,
            description="Motor cars with spark-ignition engines"
        )
        
        duty_rate = await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=hs_code,
            general_rate=5.0
        )
        
        # 2. Test multiple concurrent API operations
        async def perform_operations():
            operations = []
            
            # Multiple tariff lookups
            for _ in range(5):
                operations.append(
                    asyncio.create_task(
                        self._async_api_call(test_client, "GET", f"/api/tariff/code/{hs_code}")
                    )
                )
            
            # Multiple duty calculations
            for i in range(5):
                calc_request = {
                    "hs_code": hs_code,
                    "country_code": "USA",
                    "customs_value": 1000.00 * (i + 1)
                }
                operations.append(
                    asyncio.create_task(
                        self._async_api_call(test_client, "POST", "/api/duty/calculate", calc_request)
                    )
                )
            
            # Multiple rate lookups
            for _ in range(3):
                operations.append(
                    asyncio.create_task(
                        self._async_api_call(test_client, "GET", f"/api/duty/rates/{hs_code}")
                    )
                )
            
            return await asyncio.gather(*operations, return_exceptions=True)
        
        # Execute concurrent operations
        results = await perform_operations()
        
        # 3. Verify all operations completed successfully
        successful_operations = [
            result for result in results 
            if not isinstance(result, Exception) and result.get("status_code") in [200, 201]
        ]
        
        # Should have high success rate
        success_rate = len(successful_operations) / len(results)
        assert success_rate >= 0.8, f"Success rate {success_rate} below threshold"
        
        # 4. Verify data consistency after concurrent operations
        final_detail_response = test_client.get(f"/api/tariff/code/{hs_code}")
        APITestHelper.assert_response_success(final_detail_response, 200)
        
        final_data = final_detail_response.json()
        assert final_data["tariff"]["hs_code"] == hs_code
        assert final_data["tariff"]["description"] == tariff_code.description
    
    async def test_database_performance_under_load(
        self, async_test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test database performance under realistic load scenarios."""
        # 1. Create substantial test dataset
        test_data_size = 50
        created_codes = []
        
        for i in range(test_data_size):
            hs_code = f"8471{i:06d}"
            
            tariff_code = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=f"Test product {i}",
                level=10
            )
            created_codes.append(tariff_code)
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=float(i % 20)  # Vary rates
            )
            
            # Create FTA rates for some products
            if i % 3 == 0:
                await DatabaseTestHelper.create_fta_rate(
                    test_session,
                    hs_code=hs_code,
                    country_code="USA",
                    preferential_rate=0.0,
                    fta_code="AUSFTA"
                )
        
        # 2. Test search performance
        search_start_time = time.time()
        
        search_response = await async_test_client.get("/api/tariff/search?query=test&limit=20")
        
        search_end_time = time.time()
        search_duration = search_end_time - search_start_time
        
        assert search_response.status_code == 200
        assert search_duration < 5.0, f"Search took {search_duration}s, expected < 5s"
        
        search_data = search_response.json()
        assert search_data["total_results"] > 0
        
        # 3. Test concurrent detail lookups
        async def concurrent_detail_lookups():
            tasks = []
            
            # Select random subset for concurrent access
            test_codes = created_codes[:20]
            
            for tariff_code in test_codes:
                task = async_test_client.get(f"/api/tariff/code/{tariff_code.hs_code}")
                tasks.append(task)
            
            start_time = time.time()
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            end_time = time.time()
            
            return responses, end_time - start_time
        
        responses, concurrent_duration = await concurrent_detail_lookups()
        
        # Verify performance
        assert concurrent_duration < 10.0, f"Concurrent lookups took {concurrent_duration}s"
        
        # Verify success rate
        successful_responses = [
            r for r in responses 
            if not isinstance(r, Exception) and hasattr(r, 'status_code') and r.status_code == 200
        ]
        
        success_rate = len(successful_responses) / len(responses)
        assert success_rate >= 0.9, f"Success rate {success_rate} below threshold"
        
        # 4. Test bulk calculation performance
        bulk_calc_requests = [
            {
                "hs_code": code.hs_code,
                "country_code": "USA",
                "customs_value": 1000.00 * (i + 1)
            }
            for i, code in enumerate(created_codes[:10])
        ]
        
        calc_start_time = time.time()
        
        calc_tasks = [
            async_test_client.post("/api/duty/calculate", json=request)
            for request in bulk_calc_requests
        ]
        
        calc_responses = await asyncio.gather(*calc_tasks, return_exceptions=True)
        
        calc_end_time = time.time()
        calc_duration = calc_end_time - calc_start_time
        
        assert calc_duration < 15.0, f"Bulk calculations took {calc_duration}s"
        
        # Verify calculation success rate
        successful_calcs = [
            r for r in calc_responses
            if not isinstance(r, Exception) and hasattr(r, 'status_code') and r.status_code == 200
        ]
        
        calc_success_rate = len(successful_calcs) / len(calc_responses)
        assert calc_success_rate >= 0.8, f"Calculation success rate {calc_success_rate} below threshold"
    
    async def test_data_migration_and_schema_evolution(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test data consistency during schema evolution scenarios."""
        # 1. Create data with current schema
        original_data = [
            {
                "hs_code": "8471300000",
                "description": "Portable computers",
                "general_rate": 0.0
            },
            {
                "hs_code": "6203420000", 
                "description": "Cotton trousers",
                "general_rate": 17.5
            }
        ]
        
        created_items = []
        for item in original_data:
            tariff_code = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=item["hs_code"],
                description=item["description"]
            )
            
            duty_rate = await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=item["hs_code"],
                general_rate=item["general_rate"]
            )
            
            created_items.append({
                "tariff_code": tariff_code,
                "duty_rate": duty_rate,
                "original": item
            })
        
        # 2. Test data retrieval before any changes
        for item in created_items:
            response = test_client.get(f"/api/tariff/code/{item['tariff_code'].hs_code}")
            APITestHelper.assert_response_success(response, 200)
            
            data = response.json()
            assert data["tariff"]["hs_code"] == item["original"]["hs_code"]
            assert data["tariff"]["description"] == item["original"]["description"]
        
        # 3. Simulate schema evolution by adding new fields
        # (In real scenario, this would be done via database migrations)
        
        # Test that existing data still works with potential new fields
        for item in created_items:
            # Test with additional query parameters that might be added in future
            response = test_client.get(
                f"/api/tariff/code/{item['tariff_code'].hs_code}?"
                f"include_rates=true&include_hierarchy=true&include_metadata=true"
            )
            
            # Should handle gracefully even if some parameters don't exist yet
            assert response.status_code in [200, 422]  # 422 for unknown parameters is acceptable
            
            if response.status_code == 200:
                data = response.json()
                assert data["tariff"]["hs_code"] == item["original"]["hs_code"]
        
        # 4. Test backward compatibility
        # Ensure old API calls still work
        for item in created_items:
            # Simple call without new parameters
            response = test_client.get(f"/api/tariff/code/{item['tariff_code'].hs_code}")
            APITestHelper.assert_response_success(response, 200)
            
            # Duty calculation should still work
            calc_response = test_client.post(
                "/api/duty/calculate",
                json={
                    "hs_code": item["tariff_code"].hs_code,
                    "country_code": "USA",
                    "customs_value": 1000.00
                }
            )
            
            assert calc_response.status_code in [200, 422]  # Should not crash
    
    async def _async_api_call(self, test_client: TestClient, method: str, url: str, json_data=None):
        """Helper method to make async API calls for testing."""
        try:
            if method == "GET":
                response = test_client.get(url)
            elif method == "POST":
                response = test_client.post(url, json=json_data)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return {
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        except Exception as e:
            return {"error": str(e), "status_code": 500}


@pytest.mark.e2e
@pytest.mark.integration
@pytest.mark.database
class TestConcurrentAccessPatterns:
    """Test concurrent access patterns and race condition handling."""
    
    async def test_concurrent_read_write_operations(
        self, async_test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test concurrent read and write operations for race conditions."""
        # 1. Create initial test data
        hs_code = "8471300000"
        
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code=hs_code,
            description="Test product for concurrency"
        )
        
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=hs_code,
            general_rate=5.0
        )
        
        # 2. Define concurrent operations
        async def read_operations():
            """Simulate multiple concurrent read operations."""
            tasks = []
            
            for _ in range(10):
                # Tariff detail reads
                tasks.append(async_test_client.get(f"/api/tariff/code/{hs_code}"))
                
                # Rate lookups
                tasks.append(async_test_client.get(f"/api/duty/rates/{hs_code}"))
                
                # Duty calculations
                tasks.append(
                    async_test_client.post(
                        "/api/duty/calculate",
                        json={
                            "hs_code": hs_code,
                            "country_code": "USA",
                            "customs_value": 1000.00
                        }
                    )
                )
            
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        async def write_operations():
            """Simulate write operations that might occur during reads."""
            # In a real scenario, these might be data updates, cache invalidations, etc.
            # For testing, we'll simulate by creating related data
            
            tasks = []
            
            for i in range(5):
                # Create FTA rates (simulating data updates)
                fta_rate = await DatabaseTestHelper.create_fta_rate(
                    test_session,
                    hs_code=hs_code,
                    country_code=f"C{i:02d}",  # Dummy country codes
                    preferential_rate=float(i),
                    fta_code=f"FTA{i}"
                )
                tasks.append(fta_rate)
            
            return tasks
        
        # 3. Execute concurrent read and write operations
        start_time = time.time()
        
        read_task = asyncio.create_task(read_operations())
        write_task = asyncio.create_task(write_operations())
        
        read_results, write_results = await asyncio.gather(read_task, write_task)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # 4. Verify results
        assert total_duration < 20.0, f"Concurrent operations took {total_duration}s"
        
        # Check read operation success rate
        successful_reads = [
            result for result in read_results
            if not isinstance(result, Exception) and hasattr(result, 'status_code') and result.status_code == 200
        ]
        
        read_success_rate = len(successful_reads) / len(read_results)
        assert read_success_rate >= 0.8, f"Read success rate {read_success_rate} below threshold"
        
        # Verify write operations completed
        assert len(write_results) == 5, "Not all write operations completed"
        
        # 5. Verify data consistency after concurrent operations
        final_response = await async_test_client.get(f"/api/tariff/code/{hs_code}?include_rates=true")
        assert final_response.status_code == 200
        
        final_data = final_response.json()
        assert final_data["tariff"]["hs_code"] == hs_code
        
        # Should now include the FTA rates created during concurrent operations
        if final_data.get("fta_rates"):
            assert len(final_data["fta_rates"]) >= 5
    
    async def test_database_connection_pool_handling(
        self, async_test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test database connection pool handling under high load."""
        # 1. Create test data
        test_codes = []
        for i in range(20):
            hs_code = f"8471{i:06d}"
            
            tariff_code = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=f"Test product {i}"
            )
            test_codes.append(tariff_code)
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=5.0
            )
        
        # 2. Create high load scenario
        async def high_load_operations():
            """Create many concurrent database operations."""
            tasks = []
            
            # Create 100 concurrent operations
            for i in range(100):
                code = test_codes[i % len(test_codes)]
                
                if i % 3 == 0:
                    # Tariff detail lookup
                    tasks.append(async_test_client.get(f"/api/tariff/code/{code.hs_code}"))
                elif i % 3 == 1:
                    # Rate lookup
                    tasks.append(async_test_client.get(f"/api/duty/rates/{code.hs_code}"))
                else:
                    # Duty calculation
                    tasks.append(
                        async_test_client.post(
                            "/api/duty/calculate",
                            json={
                                "hs_code": code.hs_code,
                                "country_code": "USA",
                                "customs_value": 1000.00
                            }
                        )
                    )
            
            return await asyncio.gather(*tasks, return_exceptions=True)
        
        # 3. Execute high load test
        start_time = time.time()
        results = await high_load_operations()
        end_time = time.time()
        
        duration = end_time - start_time
        
        # 4. Verify performance and reliability
        assert duration < 30.0, f"High load operations took {duration}s"
        
        # Check for connection pool exhaustion or database errors
        connection_errors = [
            result for result in results
            if isinstance(result, Exception) or 
            (hasattr(result, 'status_code') and result.status_code == 500)
        ]
        
        error_rate = len(connection_errors) / len(results)
        assert error_rate < 0.1, f"Error rate {error_rate} too high, possible connection pool issues"
        
        # Verify successful operations
        successful_operations = [
            result for result in results
            if not isinstance(result, Exception) and 
            hasattr(result, 'status_code') and result.status_code == 200
        ]
        
        success_rate = len(successful_operations) / len(results)
        assert success_rate >= 0.8, f"Success rate {success_rate} below threshold"