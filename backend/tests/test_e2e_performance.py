"""
End-to-End Performance and Load Testing for Customs Broker Portal.

This module tests system performance under various load conditions,
including response times, throughput, and resource usage validation.
"""

import pytest
import pytest_asyncio
import asyncio
import time
import statistics
from decimal import Decimal
from datetime import date, datetime, timedelta
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import patch
import psutil
import gc

from tests.utils.test_helpers import (
    APITestHelper, DatabaseTestHelper, TestDataFactory,
    PerformanceTestHelper, AsyncTestHelper
)


@pytest.mark.e2e
@pytest.mark.performance
@pytest.mark.slow
class TestSystemPerformanceUnderLoad:
    """Test system performance under realistic user loads."""
    
    async def test_api_response_times_under_normal_load(
        self, async_test_client: AsyncClient, test_session: AsyncSession, performance_timer
    ):
        """Test API response times under normal load conditions."""
        # 1. Create substantial test dataset
        test_data_size = 100
        created_codes = []
        
        for i in range(test_data_size):
            hs_code = f"8471{i:06d}"
            
            tariff_code = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=f"Performance test product {i}",
                level=10
            )
            created_codes.append(tariff_code)
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=float(i % 20)
            )
            
            # Add FTA rates for some products
            if i % 5 == 0:
                await DatabaseTestHelper.create_fta_rate(
                    test_session,
                    hs_code=hs_code,
                    country_code="USA",
                    preferential_rate=0.0,
                    fta_code="AUSFTA"
                )
        
        # 2. Test individual endpoint performance
        endpoint_performance = {}
        
        # Test tariff detail endpoint
        detail_times = []
        for i in range(20):  # Test 20 random products
            code = created_codes[i * 5]  # Every 5th product
            
            start_time = time.time()
            response = await async_test_client.get(f"/api/tariff/code/{code.hs_code}")
            end_time = time.time()
            
            if response.status_code == 200:
                detail_times.append(end_time - start_time)
        
        endpoint_performance["tariff_detail"] = {
            "avg_time": statistics.mean(detail_times),
            "max_time": max(detail_times),
            "min_time": min(detail_times),
            "total_requests": len(detail_times)
        }
        
        # Test search endpoint performance
        search_times = []
        search_queries = ["test", "product", "performance", "8471", "machine"]
        
        for query in search_queries:
            start_time = time.time()
            response = await async_test_client.get(f"/api/tariff/search?query={query}&limit=10")
            end_time = time.time()
            
            if response.status_code == 200:
                search_times.append(end_time - start_time)
        
        endpoint_performance["search"] = {
            "avg_time": statistics.mean(search_times),
            "max_time": max(search_times),
            "min_time": min(search_times),
            "total_requests": len(search_times)
        }
        
        # Test duty calculation performance
        calc_times = []
        for i in range(15):
            code = created_codes[i * 6]  # Every 6th product
            
            calc_request = {
                "hs_code": code.hs_code,
                "country_code": "USA",
                "customs_value": 1000.00 * (i + 1)
            }
            
            start_time = time.time()
            response = await async_test_client.post("/api/duty/calculate", json=calc_request)
            end_time = time.time()
            
            if response.status_code == 200:
                calc_times.append(end_time - start_time)
        
        endpoint_performance["duty_calculation"] = {
            "avg_time": statistics.mean(calc_times),
            "max_time": max(calc_times),
            "min_time": min(calc_times),
            "total_requests": len(calc_times)
        }
        
        # 3. Verify performance benchmarks
        # Tariff detail should be fast (< 1 second average)
        assert endpoint_performance["tariff_detail"]["avg_time"] < 1.0, \
            f"Tariff detail avg time {endpoint_performance['tariff_detail']['avg_time']}s too slow"
        
        # Search should be reasonable (< 2 seconds average)
        assert endpoint_performance["search"]["avg_time"] < 2.0, \
            f"Search avg time {endpoint_performance['search']['avg_time']}s too slow"
        
        # Duty calculation should be efficient (< 1.5 seconds average)
        assert endpoint_performance["duty_calculation"]["avg_time"] < 1.5, \
            f"Duty calculation avg time {endpoint_performance['duty_calculation']['avg_time']}s too slow"
        
        # No single request should take more than 5 seconds
        for endpoint, metrics in endpoint_performance.items():
            assert metrics["max_time"] < 5.0, \
                f"{endpoint} max time {metrics['max_time']}s exceeds threshold"
    
    async def test_concurrent_user_scenarios(
        self, async_test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test system performance with concurrent users."""
        # 1. Create test data
        test_products = []
        for i in range(50):
            hs_code = f"8703{i:06d}"
            
            tariff_code = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=f"Concurrent test product {i}"
            )
            test_products.append(tariff_code)
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=5.0
            )
        
        # 2. Define user scenarios
        async def simulate_user_session(user_id: int, products: list):
            """Simulate a typical user session."""
            session_operations = []
            user_products = products[user_id * 5:(user_id + 1) * 5]  # 5 products per user
            
            for product in user_products:
                # 1. Search for product
                search_task = async_test_client.get(f"/api/tariff/search?query={product.hs_code[:4]}")
                session_operations.append(("search", search_task))
                
                # 2. Get product details
                detail_task = async_test_client.get(f"/api/tariff/code/{product.hs_code}")
                session_operations.append(("detail", detail_task))
                
                # 3. Calculate duty
                calc_task = async_test_client.post(
                    "/api/duty/calculate",
                    json={
                        "hs_code": product.hs_code,
                        "country_code": "USA",
                        "customs_value": 1000.00 * (user_id + 1)
                    }
                )
                session_operations.append(("calculation", calc_task))
            
            # Execute all operations for this user
            start_time = time.time()
            results = await asyncio.gather(*[op[1] for op in session_operations], return_exceptions=True)
            end_time = time.time()
            
            return {
                "user_id": user_id,
                "session_duration": end_time - start_time,
                "operations": len(session_operations),
                "results": results
            }
        
        # 3. Simulate concurrent users
        num_concurrent_users = 10
        
        start_time = time.time()
        
        user_tasks = [
            simulate_user_session(user_id, test_products)
            for user_id in range(num_concurrent_users)
        ]
        
        user_results = await asyncio.gather(*user_tasks)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # 4. Analyze concurrent performance
        session_durations = [result["session_duration"] for result in user_results]
        total_operations = sum(result["operations"] for result in user_results)
        
        avg_session_duration = statistics.mean(session_durations)
        max_session_duration = max(session_durations)
        
        # Performance assertions
        assert total_duration < 60.0, f"Total concurrent test took {total_duration}s, expected < 60s"
        assert avg_session_duration < 30.0, f"Average session duration {avg_session_duration}s too long"
        assert max_session_duration < 45.0, f"Max session duration {max_session_duration}s too long"
        
        # Check success rates
        total_successful_operations = 0
        total_failed_operations = 0
        
        for result in user_results:
            for operation_result in result["results"]:
                if isinstance(operation_result, Exception):
                    total_failed_operations += 1
                elif hasattr(operation_result, 'status_code') and operation_result.status_code == 200:
                    total_successful_operations += 1
                else:
                    total_failed_operations += 1
        
        success_rate = total_successful_operations / (total_successful_operations + total_failed_operations)
        assert success_rate >= 0.85, f"Success rate {success_rate} below threshold"
        
        # Calculate throughput
        throughput = total_operations / total_duration
        assert throughput >= 5.0, f"Throughput {throughput} operations/second too low"
    
    async def test_memory_usage_and_resource_cleanup(
        self, async_test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test memory usage and resource cleanup during operations."""
        # 1. Get baseline memory usage
        gc.collect()  # Force garbage collection
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # 2. Create test data
        memory_test_size = 50
        
        for i in range(memory_test_size):
            hs_code = f"8888{i:06d}"
            
            await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=f"Memory test product {i}"
            )
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=float(i % 30)
            )
        
        # 3. Perform memory-intensive operations
        memory_intensive_operations = []
        
        # Large search operations
        for i in range(10):
            memory_intensive_operations.append(
                async_test_client.get("/api/tariff/search?query=memory&limit=20")
            )
        
        # Multiple detail lookups
        for i in range(15):
            hs_code = f"8888{i:06d}"
            memory_intensive_operations.append(
                async_test_client.get(f"/api/tariff/code/{hs_code}")
            )
        
        # Multiple calculations
        for i in range(15):
            hs_code = f"8888{i:06d}"
            memory_intensive_operations.append(
                async_test_client.post(
                    "/api/duty/calculate",
                    json={
                        "hs_code": hs_code,
                        "country_code": "USA",
                        "customs_value": 1000.00 * (i + 1)
                    }
                )
            )
        
        # Execute all operations
        start_time = time.time()
        results = await asyncio.gather(*memory_intensive_operations, return_exceptions=True)
        end_time = time.time()
        
        operation_duration = end_time - start_time
        
        # 4. Check memory usage during operations
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # 5. Force cleanup and check final memory
        gc.collect()
        await asyncio.sleep(1)  # Allow cleanup time
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # 6. Analyze memory usage
        memory_increase = peak_memory - initial_memory
        memory_after_cleanup = final_memory - initial_memory
        
        # Memory usage should be reasonable
        assert memory_increase < 200, f"Memory increase {memory_increase}MB too high"
        
        # Operations should complete in reasonable time
        assert operation_duration < 20.0, f"Memory-intensive operations took {operation_duration}s"
        
        # Verify operation success rate
        successful_operations = [
            result for result in results
            if not isinstance(result, Exception) and 
            hasattr(result, 'status_code') and result.status_code == 200
        ]
        
        success_rate = len(successful_operations) / len(results)
        assert success_rate >= 0.8, f"Success rate {success_rate} during memory test too low"


@pytest.mark.e2e
@pytest.mark.performance
@pytest.mark.slow
class TestScalabilityAndLoadLimits:
    """Test system scalability and load limits."""
    
    async def test_maximum_concurrent_connections(
        self, async_test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test system behavior at maximum concurrent connections."""
        # 1. Create test data
        for i in range(20):
            hs_code = f"7777{i:06d}"
            
            await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=f"Scalability test product {i}"
            )
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=5.0
            )
        
        # 2. Test increasing levels of concurrency
        concurrency_levels = [10, 25, 50]
        performance_results = {}
        
        for concurrency in concurrency_levels:
            # Create concurrent operations
            concurrent_operations = []
            
            for i in range(concurrency):
                hs_code = f"7777{i % 20:06d}"
                
                if i % 3 == 0:
                    # Search operation
                    concurrent_operations.append(
                        async_test_client.get("/api/tariff/search?query=scalability&limit=10")
                    )
                elif i % 3 == 1:
                    # Detail lookup
                    concurrent_operations.append(
                        async_test_client.get(f"/api/tariff/code/{hs_code}")
                    )
                else:
                    # Duty calculation
                    concurrent_operations.append(
                        async_test_client.post(
                            "/api/duty/calculate",
                            json={
                                "hs_code": hs_code,
                                "country_code": "USA",
                                "customs_value": 1000.00
                            }
                        )
                    )
            
            # Execute concurrent operations
            start_time = time.time()
            results = await asyncio.gather(*concurrent_operations, return_exceptions=True)
            end_time = time.time()
            
            duration = end_time - start_time
            
            # Analyze results
            successful_ops = [
                result for result in results
                if not isinstance(result, Exception) and 
                hasattr(result, 'status_code') and result.status_code == 200
            ]
            
            failed_ops = len(results) - len(successful_ops)
            success_rate = len(successful_ops) / len(results)
            throughput = len(successful_ops) / duration
            
            performance_results[concurrency] = {
                "duration": duration,
                "success_rate": success_rate,
                "failed_operations": failed_ops,
                "throughput": throughput
            }
            
            # Basic performance requirements
            assert duration < 60.0, f"Concurrency {concurrency} took {duration}s"
            assert success_rate >= 0.7, f"Success rate {success_rate} too low at concurrency {concurrency}"
        
        # 3. Verify scalability characteristics
        # Throughput should generally increase with concurrency (up to a point)
        throughputs = [performance_results[c]["throughput"] for c in concurrency_levels]
        
        # At least some improvement in throughput with increased concurrency
        max_throughput = max(throughputs)
        min_throughput = min(throughputs)
        
        assert max_throughput > min_throughput * 1.2, "System doesn't scale with increased concurrency"
        
        # Success rate shouldn't degrade too much with increased load
        success_rates = [performance_results[c]["success_rate"] for c in concurrency_levels]
        min_success_rate = min(success_rates)
        
        assert min_success_rate >= 0.6, f"Minimum success rate {min_success_rate} too low under load"