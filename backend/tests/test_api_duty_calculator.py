"""
API endpoint tests for duty calculator routes.

This module tests all duty calculator API endpoints including comprehensive
duty calculations, rate lookups, FTA rates, TCO exemptions, and breakdowns.
"""

import pytest
import pytest_asyncio
from decimal import Decimal
from datetime import date, timedelta
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests.utils.test_helpers import (
    APITestHelper, DatabaseTestHelper, TestDataFactory,
    PerformanceTestHelper, ValidationTestHelper
)


@pytest.mark.api
class TestDutyCalculationAPI:
    """Test duty calculation API endpoints."""
    
    async def test_calculate_duty_success(self, test_client: TestClient, test_session: AsyncSession):
        """Test successful duty calculation."""
        # Create test tariff code and duty rate
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000",
            description="Live horses for breeding"
        )
        
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            general_rate=5.0,
            unit_type="ad_valorem"
        )
        
        calculation_request = {
            "hs_code": tariff_code.hs_code,
            "country_code": "USA",
            "customs_value": 10000.00,
            "quantity": 1,
            "calculation_date": date.today().isoformat(),
            "value_basis": "CIF"
        }
        
        response = test_client.post("/api/duty/calculate", json=calculation_request)
        
        APITestHelper.assert_response_success(response, 200)
        data = APITestHelper.assert_json_response(response, [
            "hs_code", "country_code", "customs_value", "total_duty",
            "duty_inclusive_value", "total_amount"
        ])
        
        assert data["hs_code"] == tariff_code.hs_code
        assert data["country_code"] == "USA"
        assert data["customs_value"] == 10000.00
        assert isinstance(data["total_duty"], (int, float))
        assert isinstance(data["total_amount"], (int, float))
    
    async def test_calculate_duty_with_fta_rate(self, test_client: TestClient, test_session: AsyncSession):
        """Test duty calculation with FTA preferential rate."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010001"
        )
        
        # Create general duty rate
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            general_rate=10.0
        )
        
        # Create FTA rate
        await DatabaseTestHelper.create_fta_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            country_code="USA",
            preferential_rate=0.0,
            fta_code="AUSFTA"
        )
        
        calculation_request = {
            "hs_code": tariff_code.hs_code,
            "country_code": "USA",
            "customs_value": 5000.00
        }
        
        response = test_client.post("/api/duty/calculate", json=calculation_request)
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        # Should have both general and FTA duty components
        assert "general_duty" in data
        assert "fta_duty" in data
        assert data["best_rate_type"] in ["general", "fta"]
    
    async def test_calculate_duty_validation_errors(self, test_client: TestClient):
        """Test duty calculation with validation errors."""
        # Test missing required fields
        invalid_requests = [
            {},  # Empty request
            {"hs_code": "0101010000"},  # Missing country_code and customs_value
            {"country_code": "USA"},  # Missing hs_code and customs_value
            {"customs_value": 1000},  # Missing hs_code and country_code
            {
                "hs_code": "0101010000",
                "country_code": "USA",
                "customs_value": -1000  # Negative value
            },
            {
                "hs_code": "invalid",  # Invalid HS code format
                "country_code": "USA",
                "customs_value": 1000
            },
            {
                "hs_code": "0101010000",
                "country_code": "INVALID",  # Invalid country code
                "customs_value": 1000
            }
        ]
        
        for invalid_request in invalid_requests:
            response = test_client.post("/api/duty/calculate", json=invalid_request)
            ValidationTestHelper.assert_validation_error(response)
    
    async def test_calculate_duty_nonexistent_hs_code(self, test_client: TestClient):
        """Test duty calculation with non-existent HS code."""
        calculation_request = {
            "hs_code": "9999999999",
            "country_code": "USA",
            "customs_value": 1000.00
        }
        
        response = test_client.post("/api/duty/calculate", json=calculation_request)
        
        # Should handle gracefully - either 404 or return calculation with warnings
        assert response.status_code in [200, 404, 422]
    
    async def test_calculate_duty_performance(self, test_client: TestClient, test_session: AsyncSession, performance_timer):
        """Test duty calculation performance."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010002"
        )
        
        calculation_request = {
            "hs_code": tariff_code.hs_code,
            "country_code": "USA",
            "customs_value": 1000.00
        }
        
        performance_timer.start()
        response = test_client.post("/api/duty/calculate", json=calculation_request)
        performance_timer.stop()
        
        assert response.status_code in [200, 404, 422]  # Allow for missing rates
        PerformanceTestHelper.assert_execution_time(performance_timer.elapsed, 3.0)


@pytest.mark.api
class TestDutyRatesAPI:
    """Test duty rates lookup API endpoints."""
    
    async def test_get_duty_rates_success(self, test_client: TestClient, test_session: AsyncSession):
        """Test successful duty rates retrieval."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010003"
        )
        
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            general_rate=7.5
        )
        
        response = test_client.get(f"/api/duty/rates/{tariff_code.hs_code}")
        
        APITestHelper.assert_response_success(response, 200)
        data = APITestHelper.assert_json_response(response, [
            "hs_code", "general_rates"
        ])
        
        assert data["hs_code"] == tariff_code.hs_code
        assert isinstance(data["general_rates"], list)
        
        if data["general_rates"]:
            rate = data["general_rates"][0]
            assert "rate_type" in rate
            assert "general_rate" in rate
            assert "unit_type" in rate
    
    async def test_get_duty_rates_with_fta_rates(self, test_client: TestClient, test_session: AsyncSession):
        """Test duty rates retrieval including FTA rates."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010004"
        )
        
        await DatabaseTestHelper.create_fta_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            country_code="USA",
            preferential_rate=2.5
        )
        
        response = test_client.get(f"/api/duty/rates/{tariff_code.hs_code}?include_fta=true")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert "fta_rates" in data
        assert isinstance(data["fta_rates"], list)
    
    async def test_get_duty_rates_with_country_filter(self, test_client: TestClient, test_session: AsyncSession):
        """Test duty rates with country code filter."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010005"
        )
        
        # Create FTA rates for different countries
        await DatabaseTestHelper.create_fta_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            country_code="USA",
            preferential_rate=0.0
        )
        
        await DatabaseTestHelper.create_fta_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            country_code="JPN",
            preferential_rate=5.0
        )
        
        response = test_client.get(f"/api/duty/rates/{tariff_code.hs_code}?country_code=USA&include_fta=true")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        # Should only return FTA rates for USA
        for fta_rate in data.get("fta_rates", []):
            assert fta_rate["country_code"] == "USA"
    
    async def test_get_duty_rates_with_dumping_duties(self, test_client: TestClient, test_session: AsyncSession):
        """Test duty rates including anti-dumping duties."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010006"
        )
        
        await DatabaseTestHelper.create_dumping_duty(
            test_session,
            hs_code=tariff_code.hs_code,
            country_code="CHN",
            duty_rate=25.0
        )
        
        response = test_client.get(f"/api/duty/rates/{tariff_code.hs_code}?include_dumping=true")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert "anti_dumping_duties" in data
        assert isinstance(data["anti_dumping_duties"], list)
    
    async def test_get_duty_rates_with_tco_exemptions(self, test_client: TestClient, test_session: AsyncSession):
        """Test duty rates including TCO exemptions."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010007"
        )
        
        await DatabaseTestHelper.create_tco(
            test_session,
            hs_code=tariff_code.hs_code,
            tco_number="TCO2024001"
        )
        
        response = test_client.get(f"/api/duty/rates/{tariff_code.hs_code}?include_tco=true")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert "tco_exemptions" in data
        assert isinstance(data["tco_exemptions"], list)
    
    async def test_get_duty_rates_not_found(self, test_client: TestClient):
        """Test duty rates for non-existent HS code."""
        non_existent_code = "9999999999"
        
        response = test_client.get(f"/api/duty/rates/{non_existent_code}")
        
        # Should return empty rates structure, not 404
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert data["hs_code"] == non_existent_code
        assert data["general_rates"] == []


@pytest.mark.api
class TestDutyBreakdownAPI:
    """Test duty calculation breakdown API endpoints."""
    
    async def test_get_calculation_breakdown_success(self, test_client: TestClient, test_session: AsyncSession):
        """Test successful calculation breakdown retrieval."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010008"
        )
        
        params = {
            "hs_code": tariff_code.hs_code,
            "country_code": "USA",
            "customs_value": 5000.00,
            "calculation_date": date.today().isoformat()
        }
        
        response = test_client.get("/api/duty/breakdown", params=params)
        
        APITestHelper.assert_response_success(response, 200)
        data = APITestHelper.assert_json_response(response, [
            "input_parameters", "duty_components", "totals",
            "best_rate_analysis", "calculation_steps"
        ])
        
        assert isinstance(data["input_parameters"], dict)
        assert isinstance(data["duty_components"], dict)
        assert isinstance(data["totals"], dict)
        assert isinstance(data["calculation_steps"], list)
    
    async def test_get_calculation_breakdown_with_quantity(self, test_client: TestClient, test_session: AsyncSession):
        """Test calculation breakdown with quantity parameter."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010009"
        )
        
        params = {
            "hs_code": tariff_code.hs_code,
            "country_code": "USA",
            "customs_value": 2000.00,
            "quantity": 5
        }
        
        response = test_client.get("/api/duty/breakdown", params=params)
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert data["input_parameters"]["quantity"] == 5
    
    async def test_get_calculation_breakdown_validation_errors(self, test_client: TestClient):
        """Test calculation breakdown with validation errors."""
        # Missing required parameters
        response = test_client.get("/api/duty/breakdown")
        ValidationTestHelper.assert_validation_error(response)
        
        # Invalid customs value
        params = {
            "hs_code": "0101010000",
            "country_code": "USA",
            "customs_value": -1000
        }
        response = test_client.get("/api/duty/breakdown", params=params)
        ValidationTestHelper.assert_validation_error(response)


@pytest.mark.api
class TestFtaRatesAPI:
    """Test FTA rates API endpoints."""
    
    async def test_get_fta_rates_success(self, test_client: TestClient, test_session: AsyncSession):
        """Test successful FTA rates retrieval."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010010"
        )
        
        await DatabaseTestHelper.create_fta_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            country_code="USA",
            preferential_rate=0.0,
            fta_code="AUSFTA"
        )
        
        response = test_client.get(f"/api/duty/fta-rates/{tariff_code.hs_code}/USA")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert isinstance(data, list)
        if data:
            rate = data[0]
            assert rate["hs_code"] == tariff_code.hs_code
            assert rate["country_code"] == "USA"
            assert "preferential_rate" in rate
            assert "fta_code" in rate
    
    async def test_get_fta_rates_with_calculation_date(self, test_client: TestClient, test_session: AsyncSession):
        """Test FTA rates with calculation date filter."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010011"
        )
        
        # Create FTA rate with future effective date
        future_date = date.today() + timedelta(days=30)
        await DatabaseTestHelper.create_fta_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            country_code="USA",
            preferential_rate=0.0,
            effective_date=future_date
        )
        
        # Request with today's date - should not return future rate
        today = date.today().isoformat()
        response = test_client.get(f"/api/duty/fta-rates/{tariff_code.hs_code}/USA?calculation_date={today}")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        # Should be empty or not include the future-dated rate
        for rate in data:
            if rate.get("effective_date"):
                effective_date = date.fromisoformat(rate["effective_date"])
                assert effective_date <= date.today()
    
    async def test_get_fta_rates_not_found(self, test_client: TestClient):
        """Test FTA rates for non-existent HS code or country combination."""
        response = test_client.get("/api/duty/fta-rates/9999999999/XXX")
        
        APITestHelper.assert_response_error(response, 404)
        data = response.json()
        assert "not found" in data["detail"].lower()


@pytest.mark.api
class TestTcoExemptionsAPI:
    """Test TCO exemptions API endpoints."""
    
    async def test_check_tco_exemptions_success(self, test_client: TestClient, test_session: AsyncSession):
        """Test successful TCO exemptions check."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010012"
        )
        
        await DatabaseTestHelper.create_tco(
            test_session,
            hs_code=tariff_code.hs_code,
            tco_number="TCO2024002",
            is_current=True
        )
        
        response = test_client.get(f"/api/duty/tco-check/{tariff_code.hs_code}")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert isinstance(data, list)
        if data:
            tco = data[0]
            assert tco["hs_code"] == tariff_code.hs_code
            assert "tco_number" in tco
            assert "is_current" in tco
    
    async def test_check_tco_exemptions_with_date_filter(self, test_client: TestClient, test_session: AsyncSession):
        """Test TCO exemptions with calculation date filter."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010013"
        )
        
        # Create expired TCO
        past_date = date.today() - timedelta(days=30)
        await DatabaseTestHelper.create_tco(
            test_session,
            hs_code=tariff_code.hs_code,
            tco_number="TCO2023001",
            expiry_date=past_date
        )
        
        today = date.today().isoformat()
        response = test_client.get(f"/api/duty/tco-check/{tariff_code.hs_code}?calculation_date={today}")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        # Should not include expired TCOs
        for tco in data:
            if tco.get("expiry_date"):
                expiry_date = date.fromisoformat(tco["expiry_date"])
                assert expiry_date > date.today()
    
    async def test_check_tco_exemptions_empty_result(self, test_client: TestClient):
        """Test TCO exemptions check with no exemptions."""
        response = test_client.get("/api/duty/tco-check/9999999999")
        
        APITestHelper.assert_response_success(response, 200)
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) == 0


@pytest.mark.api
@pytest.mark.integration
class TestDutyCalculatorAPIIntegration:
    """Integration tests for duty calculator API workflows."""
    
    async def test_complete_duty_calculation_workflow(self, test_client: TestClient, test_session: AsyncSession):
        """Test complete duty calculation workflow."""
        # Setup test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010014",
            description="Test product for workflow"
        )
        
        await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            general_rate=10.0
        )
        
        await DatabaseTestHelper.create_fta_rate(
            test_session,
            hs_code=tariff_code.hs_code,
            country_code="USA",
            preferential_rate=5.0
        )
        
        # 1. Get available rates
        rates_response = test_client.get(f"/api/duty/rates/{tariff_code.hs_code}?include_fta=true")
        APITestHelper.assert_response_success(rates_response, 200)
        
        # 2. Calculate duty
        calculation_request = {
            "hs_code": tariff_code.hs_code,
            "country_code": "USA",
            "customs_value": 10000.00
        }
        
        calc_response = test_client.post("/api/duty/calculate", json=calculation_request)
        APITestHelper.assert_response_success(calc_response, 200)
        
        # 3. Get detailed breakdown
        breakdown_params = {
            "hs_code": tariff_code.hs_code,
            "country_code": "USA",
            "customs_value": 10000.00
        }
        
        breakdown_response = test_client.get("/api/duty/breakdown", params=breakdown_params)
        APITestHelper.assert_response_success(breakdown_response, 200)
        
        # Verify consistency across responses
        calc_data = calc_response.json()
        breakdown_data = breakdown_response.json()
        
        assert calc_data["hs_code"] == breakdown_data["input_parameters"]["hs_code"]
        assert calc_data["country_code"] == breakdown_data["input_parameters"]["country_code"]
    
    async def test_multi_country_comparison_workflow(self, test_client: TestClient, test_session: AsyncSession):
        """Test workflow for comparing duty rates across multiple countries."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010015"
        )
        
        # Create FTA rates for different countries
        countries = ["USA", "JPN", "KOR"]
        rates = [0.0, 2.5, 5.0]
        
        for country, rate in zip(countries, rates):
            await DatabaseTestHelper.create_fta_rate(
                test_session,
                hs_code=tariff_code.hs_code,
                country_code=country,
                preferential_rate=rate
            )
        
        # Calculate duty for each country
        calculations = []
        for country in countries:
            calculation_request = {
                "hs_code": tariff_code.hs_code,
                "country_code": country,
                "customs_value": 5000.00
            }
            
            response = test_client.post("/api/duty/calculate", json=calculation_request)
            if response.status_code == 200:
                calculations.append((country, response.json()))
        
        # Verify calculations are different for different countries
        if len(calculations) > 1:
            duty_amounts = [calc[1]["total_duty"] for calc in calculations]
            assert len(set(duty_amounts)) > 1  # Should have different duty amounts


@pytest.mark.api
@pytest.mark.slow
class TestDutyCalculatorAPIPerformance:
    """Performance tests for duty calculator API endpoints."""
    
    async def test_concurrent_duty_calculations(self, async_test_client: AsyncClient, test_session: AsyncSession):
        """Test concurrent duty calculations."""
        import asyncio
        
        # Create test data
        tariff_codes = []
        for i in range(5):
            tariff_code = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=f"010101{i:04d}"
            )
            tariff_codes.append(tariff_code)
        
        async def calculate_duty(hs_code):
            calculation_request = {
                "hs_code": hs_code,
                "country_code": "USA",
                "customs_value": 1000.00
            }
            response = await async_test_client.post("/api/duty/calculate", json=calculation_request)
            return response.status_code
        
        # Run concurrent calculations
        tasks = [calculate_duty(tc.hs_code) for tc in tariff_codes]
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        # All calculations should complete within reasonable time
        assert end_time - start_time < 15.0
        
        # Most should succeed (some might fail due to missing rates)
        successful = sum(1 for result in results if isinstance(result, int) and result in [200, 404, 422])
        assert successful >= len(tasks) * 0.5


# Import time for performance tests
import time