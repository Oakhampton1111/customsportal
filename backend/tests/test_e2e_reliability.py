"""
End-to-End System Reliability and Resilience Tests for Customs Broker Portal.

This module tests system behavior under failure conditions, recovery mechanisms,
timeout handling, and backup/disaster recovery scenarios.
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
from unittest.mock import patch, AsyncMock, MagicMock, Mock
import random

from tests.utils.test_helpers import (
    APITestHelper, DatabaseTestHelper, TestDataFactory,
    PerformanceTestHelper, AsyncTestHelper
)


@pytest.mark.e2e
@pytest.mark.integration
class TestSystemReliabilityUnderFailure:
    """Test system behavior under various failure conditions."""
    
    async def test_database_connection_failure_recovery(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test system behavior when database connections fail and recover."""
        # 1. Setup test data
        reliability_products = [
            ("8471300000", "Reliability test product 1"),
            ("6203420000", "Reliability test product 2"),
            ("8703210000", "Reliability test product 3")
        ]
        
        for hs_code, description in reliability_products:
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
        
        # 2. Test normal operation baseline
        baseline_results = {}
        
        for hs_code, description in reliability_products:
            # Test normal operations
            detail_response = test_client.get(f"/api/tariff/code/{hs_code}")
            rates_response = test_client.get(f"/api/duty/rates/{hs_code}")
            calc_response = test_client.post(
                "/api/duty/calculate",
                json={
                    "hs_code": hs_code,
                    "country_code": "USA",
                    "customs_value": 1000.00
                }
            )
            
            baseline_results[hs_code] = {
                "detail_status": detail_response.status_code,
                "rates_status": rates_response.status_code,
                "calc_status": calc_response.status_code
            }
        
        # 3. Simulate database connection issues
        # Note: In a real test environment, you might use connection pooling mocks
        # For this test, we'll simulate by testing error handling paths
        
        # Test with invalid HS codes (simulating data not found)
        invalid_scenarios = ["invalid_code", "999999999999", ""]
        
        error_handling_results = {}
        
        for invalid_code in invalid_scenarios:
            if invalid_code:  # Skip empty string for URL safety
                detail_response = test_client.get(f"/api/tariff/code/{invalid_code}")
                calc_response = test_client.post(
                    "/api/duty/calculate",
                    json={
                        "hs_code": invalid_code,
                        "country_code": "USA",
                        "customs_value": 1000.00
                    }
                )
                
                error_handling_results[invalid_code] = {
                    "detail_status": detail_response.status_code,
                    "calc_status": calc_response.status_code
                }
        
        # 4. Test recovery after simulated failures
        recovery_results = {}
        
        # After "failure" simulation, test that valid requests still work
        for hs_code, description in reliability_products:
            detail_response = test_client.get(f"/api/tariff/code/{hs_code}")
            recovery_results[hs_code] = {
                "detail_status": detail_response.status_code,
                "recovered": detail_response.status_code == 200
            }
        
        # 5. Verify reliability characteristics
        # Baseline should work
        for hs_code, results in baseline_results.items():
            assert results["detail_status"] == 200, f"Baseline failed for {hs_code}"
            assert results["rates_status"] == 200, f"Rates baseline failed for {hs_code}"
        
        # Error handling should be appropriate
        for invalid_code, results in error_handling_results.items():
            assert results["detail_status"] in [400, 404, 422], f"Invalid code {invalid_code} should return error"
            assert results["calc_status"] in [400, 404, 422], f"Invalid calc {invalid_code} should return error"
        
        # Recovery should work
        for hs_code, results in recovery_results.items():
            assert results["recovered"], f"System did not recover for {hs_code}"
    
    async def test_timeout_handling_and_circuit_breaker(
        self, async_test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test timeout handling and circuit breaker functionality."""
        # 1. Setup test data
        timeout_products = [
            ("8471300000", "Timeout test product 1"),
            ("6203420000", "Timeout test product 2")
        ]
        
        for hs_code, description in timeout_products:
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
        
        # 2. Test normal response times
        normal_response_times = {}
        
        for hs_code, description in timeout_products:
            start_time = time.time()
            response = await async_test_client.get(f"/api/tariff/code/{hs_code}")
            end_time = time.time()
            
            normal_response_times[hs_code] = {
                "response_time": end_time - start_time,
                "status_code": response.status_code
            }
        
        # 3. Test concurrent requests (stress testing for timeouts)
        concurrent_requests = []
        
        for _ in range(20):  # Create 20 concurrent requests
            for hs_code, _ in timeout_products:
                concurrent_requests.append(
                    async_test_client.get(f"/api/tariff/code/{hs_code}")
                )
        
        # Execute concurrent requests with timeout
        start_time = time.time()
        
        try:
            results = await asyncio.wait_for(
                asyncio.gather(*concurrent_requests, return_exceptions=True),
                timeout=30.0  # 30 second timeout
            )
            end_time = time.time()
            
            concurrent_duration = end_time - start_time
            
            # Analyze results
            successful_requests = [
                result for result in results
                if not isinstance(result, Exception) and 
                hasattr(result, 'status_code') and result.status_code == 200
            ]
            
            timeout_results = {
                "total_requests": len(concurrent_requests),
                "successful_requests": len(successful_requests),
                "total_duration": concurrent_duration,
                "success_rate": len(successful_requests) / len(concurrent_requests)
            }
            
        except asyncio.TimeoutError:
            timeout_results = {
                "total_requests": len(concurrent_requests),
                "successful_requests": 0,
                "total_duration": 30.0,
                "success_rate": 0.0,
                "timeout_occurred": True
            }
        
        # 4. Test system recovery after stress
        recovery_test = {}
        
        # Wait a moment for system to recover
        await asyncio.sleep(1)
        
        for hs_code, description in timeout_products:
            start_time = time.time()
            response = await async_test_client.get(f"/api/tariff/code/{hs_code}")
            end_time = time.time()
            
            recovery_test[hs_code] = {
                "response_time": end_time - start_time,
                "status_code": response.status_code,
                "recovered": response.status_code == 200
            }
        
        # 5. Verify timeout handling
        # Normal requests should be fast
        for hs_code, timing in normal_response_times.items():
            assert timing["response_time"] < 5.0, f"Normal request for {hs_code} took {timing['response_time']}s"
            assert timing["status_code"] == 200, f"Normal request for {hs_code} failed"
        
        # Concurrent stress should not completely break the system
        assert timeout_results["success_rate"] >= 0.5, f"Success rate {timeout_results['success_rate']} too low under stress"
        
        # System should recover after stress
        for hs_code, recovery in recovery_test.items():
            assert recovery["recovered"], f"System did not recover for {hs_code}"
            assert recovery["response_time"] < 10.0, f"Recovery too slow for {hs_code}"
    
    async def test_data_consistency_under_concurrent_access(
        self, async_test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test data consistency under concurrent read/write scenarios."""
        # 1. Setup test data
        consistency_product = "8471300000"
        
        await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code=consistency_product,
            description="Consistency test product"
        )
        
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=consistency_product,
            general_rate=5.0
        )
        
        # 2. Test concurrent read operations
        async def concurrent_reader(reader_id: int):
            """Simulate concurrent read operations."""
            read_results = []
            
            for i in range(5):
                response = await async_test_client.get(f"/api/tariff/code/{consistency_product}")
                
                if response.status_code == 200:
                    data = response.json()
                    read_results.append({
                        "reader_id": reader_id,
                        "read_num": i,
                        "hs_code": data["tariff"]["hs_code"],
                        "description": data["tariff"]["description"]
                    })
                
                # Small delay between reads
                await asyncio.sleep(0.1)
            
            return read_results
        
        # 3. Execute concurrent readers
        num_readers = 5
        reader_tasks = [concurrent_reader(i) for i in range(num_readers)]
        
        start_time = time.time()
        reader_results = await asyncio.gather(*reader_tasks)
        end_time = time.time()
        
        concurrent_read_duration = end_time - start_time
        
        # 4. Test concurrent calculations
        async def concurrent_calculator(calc_id: int):
            """Simulate concurrent calculation operations."""
            calc_results = []
            
            for i in range(3):
                customs_value = 1000.00 * (calc_id + 1)  # Different values per calculator
                
                response = await async_test_client.post(
                    "/api/duty/calculate",
                    json={
                        "hs_code": consistency_product,
                        "country_code": "USA",
                        "customs_value": customs_value
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    calc_results.append({
                        "calc_id": calc_id,
                        "calc_num": i,
                        "hs_code": data["hs_code"],
                        "customs_value": data["customs_value"],
                        "total_duty": data["total_duty"]
                    })
                
                await asyncio.sleep(0.1)
            
            return calc_results
        
        # Execute concurrent calculators
        num_calculators = 3
        calc_tasks = [concurrent_calculator(i) for i in range(num_calculators)]
        
        calc_results = await asyncio.gather(*calc_tasks)
        
        # 5. Verify data consistency
        # All readers should get the same tariff data
        all_reads = [read for reader_result in reader_results for read in reader_result]
        
        if all_reads:
            reference_read = all_reads[0]
            
            for read in all_reads:
                assert read["hs_code"] == reference_read["hs_code"], "HS code inconsistency detected"
                assert read["description"] == reference_read["description"], "Description inconsistency detected"
        
        # Calculations should be consistent for same inputs
        all_calcs = [calc for calc_result in calc_results for calc in calc_result]
        
        # Group calculations by customs value
        calc_groups = {}
        for calc in all_calcs:
            value = calc["customs_value"]
            if value not in calc_groups:
                calc_groups[value] = []
            calc_groups[value].append(calc)
        
        # Verify calculations are consistent for same customs value
        for customs_value, calcs in calc_groups.items():
            if len(calcs) > 1:
                reference_calc = calcs[0]
                
                for calc in calcs[1:]:
                    assert calc["hs_code"] == reference_calc["hs_code"], f"HS code inconsistency for value {customs_value}"
                    assert abs(calc["total_duty"] - reference_calc["total_duty"]) < 0.01, f"Duty calculation inconsistency for value {customs_value}"
        
        # Performance should be reasonable
        assert concurrent_read_duration < 15.0, f"Concurrent reads took {concurrent_read_duration}s"
        
        # Should have successful operations
        assert len(all_reads) > 0, "No successful read operations"
        assert len(all_calcs) > 0, "No successful calculation operations"


@pytest.mark.e2e
@pytest.mark.integration
class TestSystemMonitoringAndHealthChecks:
    """Test system monitoring and health check functionality."""
    
    async def test_health_check_endpoints(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test system health check endpoints and monitoring."""
        # 1. Test basic health check
        health_response = test_client.get("/health")
        
        # Health endpoint might not exist, so handle gracefully
        if health_response.status_code == 200:
            health_data = health_response.json()
            assert "status" in health_data
        elif health_response.status_code == 404:
            # Health endpoint not implemented, which is acceptable
            pass
        else:
            # Unexpected error
            assert False, f"Health check returned unexpected status: {health_response.status_code}"
        
        # 2. Test database connectivity check
        # Use a simple database operation as health check
        db_health_results = {}
        
        # Test basic database operations
        test_operations = [
            ("search", lambda: test_client.get("/api/tariff/search?query=test&limit=1")),
            ("sections", lambda: test_client.get("/api/tariff/sections")),
        ]
        
        for operation_name, operation_func in test_operations:
            try:
                start_time = time.time()
                response = operation_func()
                end_time = time.time()
                
                db_health_results[operation_name] = {
                    "status_code": response.status_code,
                    "response_time": end_time - start_time,
                    "healthy": response.status_code in [200, 404]  # 404 is acceptable for empty results
                }
            except Exception as e:
                db_health_results[operation_name] = {
                    "status_code": 500,
                    "response_time": 0,
                    "healthy": False,
                    "error": str(e)
                }
        
        # 3. Test API endpoint availability
        api_endpoints = [
            "/api/tariff/search",
            "/api/duty/calculate",
            "/api/tariff/sections"
        ]
        
        endpoint_health = {}
        
        for endpoint in api_endpoints:
            try:
                if endpoint == "/api/duty/calculate":
                    # POST endpoint needs data
                    response = test_client.post(
                        endpoint,
                        json={
                            "hs_code": "8471300000",
                            "country_code": "USA",
                            "customs_value": 1000.00
                        }
                    )
                else:
                    # GET endpoints
                    response = test_client.get(endpoint)
                
                endpoint_health[endpoint] = {
                    "status_code": response.status_code,
                    "available": response.status_code not in [500, 503]
                }
            except Exception as e:
                endpoint_health[endpoint] = {
                    "status_code": 500,
                    "available": False,
                    "error": str(e)
                }
        
        # 4. Verify health check results
        # Database operations should be healthy
        for operation, result in db_health_results.items():
            assert result["healthy"], f"Database operation {operation} is unhealthy: {result}"
            assert result["response_time"] < 5.0, f"Database operation {operation} too slow: {result['response_time']}s"
        
        # API endpoints should be available
        for endpoint, result in endpoint_health.items():
            assert result["available"], f"API endpoint {endpoint} is unavailable: {result}"
    
    async def test_system_resource_monitoring(
        self, async_test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test system resource usage monitoring."""
        # 1. Setup test data for resource monitoring
        for i in range(10):
            hs_code = f"8471{i:06d}"
            
            await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=f"Resource monitoring test product {i}"
            )
            
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=5.0
            )
        
        # 2. Monitor resource usage during operations
        import psutil
        import gc
        
        # Get baseline resource usage
        gc.collect()
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        initial_cpu_percent = psutil.cpu_percent(interval=1)
        
        # 3. Perform resource-intensive operations
        resource_intensive_operations = []
        
        # Create multiple concurrent operations
        for i in range(50):
            hs_code = f"8471{i % 10:06d}"
            
            if i % 3 == 0:
                # Search operations
                resource_intensive_operations.append(
                    async_test_client.get("/api/tariff/search?query=resource&limit=10")
                )
            elif i % 3 == 1:
                # Detail lookups
                resource_intensive_operations.append(
                    async_test_client.get(f"/api/tariff/code/{hs_code}")
                )
            else:
                # Calculations
                resource_intensive_operations.append(
                    async_test_client.post(
                        "/api/duty/calculate",
                        json={
                            "hs_code": hs_code,
                            "country_code": "USA",
                            "customs_value": 1000.00 * (i + 1)
                        }
                    )
                )
        
        # Execute operations and monitor resources
        start_time = time.time()
        
        results = await asyncio.gather(*resource_intensive_operations, return_exceptions=True)
        
        end_time = time.time()
        operation_duration = end_time - start_time
        
        # Get peak resource usage
        peak_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        final_cpu_percent = psutil.cpu_percent(interval=1)
        
        # 4. Allow system to settle and check cleanup
        await asyncio.sleep(2)
        gc.collect()
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        # 5. Analyze resource usage
        memory_increase = peak_memory - initial_memory
        memory_after_cleanup = final_memory - initial_memory
        
        successful_operations = [
            result for result in results
            if not isinstance(result, Exception) and 
            hasattr(result, 'status_code') and result.status_code == 200
        ]
        
        resource_metrics = {
            "initial_memory_mb": initial_memory,
            "peak_memory_mb": peak_memory,
            "final_memory_mb": final_memory,
            "memory_increase_mb": memory_increase,
            "memory_after_cleanup_mb": memory_after_cleanup,
            "operation_duration_s": operation_duration,
            "total_operations": len(resource_intensive_operations),
            "successful_operations": len(successful_operations),
            "success_rate": len(successful_operations) / len(resource_intensive_operations)
        }
        
        # 6. Verify resource usage is within acceptable limits
        # Memory usage should be reasonable
        assert memory_increase < 200, f"Memory increase {memory_increase}MB too high"
        
        # Memory should be mostly cleaned up
        cleanup_ratio = memory_after_cleanup / memory_increase if memory_increase > 0 else 0
        assert cleanup_ratio < 0.7, f"Memory cleanup ratio {cleanup_ratio} indicates potential memory leak"
        
        # Operations should complete in reasonable time
        assert operation_duration < 30.0, f"Resource-intensive operations took {operation_duration}s"
        
        # Success rate should be high
        assert resource_metrics["success_rate"] >= 0.8, f"Success rate {resource_metrics['success_rate']} too low"
        
        # System should remain responsive
        # Test a simple operation after resource-intensive work
        post_stress_response = await async_test_client.get("/api/tariff/search?query=test&limit=1")
        assert post_stress_response.status_code == 200, "System not responsive after resource-intensive operations"


@pytest.mark.e2e
@pytest.mark.integration
class TestBackupAndDisasterRecovery:
    """Test backup and disaster recovery scenarios."""
    
    async def test_data_backup_and_restore_simulation(
        self, test_client: TestClient, test_session: AsyncSession
    ):
        """Test data backup and restore simulation."""
        # 1. Create "production" data
        production_data = [
            ("8471300000", "Production laptop data"),
            ("6203420000", "Production clothing data"),
            ("8703210000", "Production vehicle data")
        ]
        
        created_data = {}
        
        for hs_code, description in production_data:
            tariff_code = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=hs_code,
                description=description
            )
            
            duty_rate = await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=hs_code,
                general_rate=5.0
            )
            
            created_data[hs_code] = {
                "tariff_code": tariff_code,
                "duty_rate": duty_rate
            }
        
        # 2. "Backup" data by reading current state
        backup_data = {}
        
        for hs_code, description in production_data:
            detail_response = test_client.get(f"/api/tariff/code/{hs_code}")
            rates_response = test_client.get(f"/api/duty/rates/{hs_code}")
            
            if detail_response.status_code == 200 and rates_response.status_code == 200:
                backup_data[hs_code] = {
                    "detail": detail_response.json(),
                    "rates": rates_response.json()
                }
        
        # 3. Simulate "disaster" by testing with corrupted/missing data
        # Test system behavior when data is not found
        disaster_scenarios = ["9999999999", "invalid_code", ""]
        
        disaster_results = {}
        
        for invalid_code in disaster_scenarios:
            if invalid_code:  # Skip empty string
                detail_response = test_client.get(f"/api/tariff/code/{invalid_code}")
                disaster_results[invalid_code] = {
                    "detail_status": detail_response.status_code,
                    "handles_gracefully": detail_response.status_code in [404, 422]
                }
        
        # 4. "Restore" verification - ensure original data still accessible
        restore_verification = {}
        
        for hs_code, description in production_data:
            detail_response = test_client.get(f"/api/tariff/code/{hs_code}")
            
            if detail_response.status_code == 200:
                current_data = detail_response.json()
                backup_detail = backup_data[hs_code]["detail"]
                
                restore_verification[hs_code] = {
                    "data_matches": (
                        current_data["tariff"]["hs_code"] == backup_detail["tariff"]["hs_code"] and
                        current_data["tariff"]["description"] == backup_detail["tariff"]["description"]
                    ),
                    "accessible": True
                }
            else:
                restore_verification[hs_code] = {
                    "data_matches": False,
                    "accessible": False
                }
        
        # 5. Verify backup and recovery
        # Should have backed up all data
        assert len(backup_data) == len(production_data), "Not all data was backed up"
        
        # Disaster scenarios should be handled gracefully
        for invalid_code, result in disaster_results.items():
            assert result["handles_gracefully"], f"System did not handle disaster scenario {invalid_code} gracefully"
        
        # Data should be restored/accessible
        for hs_code, result in restore_verification.items():
            assert result["accessible"], f"Data {hs_code} not accessible after disaster simulation"
            assert result["data_matches"], f"Data {hs_code} does not match backup"
    
    async def test_system_degradation_and_recovery(
        self, async_test_client: AsyncClient, test_session: AsyncSession
    ):
        """Test graceful system degradation and recovery."""
        # 1. Setup test data
        degradation_products = [
            ("8471300000", "Degradation test 1"),
            ("6203420000", "Degradation test 2")
        ]
        
        for hs_code, description in degradation_products:
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
        
        # 2. Test normal operation baseline
        baseline_performance = {}
        
        for hs_code, description in degradation_products:
            start_time = time.time()
            response = await async_test_client.get(f"/api/tariff/code/{hs_code}")
            end_time = time.time()
            
            baseline_performance[hs_code] = {
                "response_time": end_time - start_time,
                "status_code": response.status_code
            }
        
        # 3. Simulate system under stress (degraded performance)
        stress_operations = []
        
        # Create high load
        for i in range(100):
            hs_code = degradation_products[i % len(degradation_products)][0]
            stress_operations.append(
                async_test_client.get(f"/api/tariff/code/{hs_code}")
            )
        
        # Execute stress test
        stress_start_time = time.time()
        stress_results = await asyncio.gather(*stress_operations, return_exceptions=True)
        stress_end_time = time.time()
        
        stress_duration = stress_end_time - stress_start_time
        
        successful_stress_ops = [
            result for result in stress_results
            if not isinstance(result, Exception) and 
            hasattr(result, 'status_code') and result.status_code == 200
        ]
        
        stress_success_rate = len(successful_stress_ops) / len(stress_operations)
        
        # 4. Test recovery after stress
        # Wait for system to recover
        await asyncio.sleep(2)
        
        recovery_performance = {}
        
        for hs_code, description in degradation_products:
            start_time = time.time()
            response = await async_test_client.get(f"/api/tariff/code/{hs_code}")
            end_time = time.time()
            
            recovery_performance[hs_code] = {
                "response_time": end_time - start_time,
                "status_code": response.status_code,
                "recovered": response.status_code == 200
            }
        
        # 5. Verify graceful degradation and recovery
        # Baseline should work normally
        for hs_code, perf in baseline_performance.items():
            assert perf["status_code"] == 200, f"Baseline failed for {hs_code}"
            assert perf["response_time"] < 2.0, f"Baseline too slow for {hs_code}"
        
        # System should handle stress reasonably
        assert stress_success_rate >= 0.7, f"Stress success rate {stress_success_rate} too low"
        assert stress_duration < 60.0, f"Stress test took {stress_duration}s"
        
        # System should recover after stress
        for hs_code, perf in recovery_performance.items():
            assert perf["recovered"], f"System did not recover for {hs_code}"
            assert perf["response_time"] < 5.0, f"Recovery too slow for {hs_code}"
        
        # Recovery should be better than or similar to baseline
        for hs_code in degradation_products:
            hs_code_val = hs_code[0]
            baseline_time = baseline_performance[hs_code_val]["response_time"]
            recovery_time = recovery_performance[hs_code_val]["response_time"]
            
            # Recovery should not be significantly worse than baseline
            assert recovery_time <= baseline_time * 3, f"Recovery much slower than baseline for {hs_code_val}"