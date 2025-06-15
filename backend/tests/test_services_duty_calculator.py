"""
Comprehensive tests for the Duty Calculator Service.

This module tests all aspects of the duty calculation service including:
- General duty rate calculations (ad valorem, specific, compound)
- FTA rate application and preferential duty calculations
- Anti-dumping duty calculations and exemption logic
- TCO (Tariff Concession Order) exemption checking
- GST calculation integration
- Complex multi-rate scenarios and edge cases
"""

import pytest
import pytest_asyncio
from datetime import date, datetime, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from services.duty_calculator import (
    DutyCalculatorService,
    DutyCalculationInput,
    DutyCalculationResult,
    DutyComponent
)
from models.duty import DutyRate
from models.fta import FtaRate
from models.dumping import DumpingDuty
from models.tco import Tco
from models.gst import GstProvision
from models.hierarchy import TradeAgreement


@pytest.mark.unit
class TestDutyCalculatorService:
    """Test suite for DutyCalculatorService core functionality."""
    
    @pytest_asyncio.fixture
    async def duty_service(self):
        """Create a duty calculator service instance."""
        return DutyCalculatorService()
    
    @pytest_asyncio.fixture
    async def sample_calculation_input(self):
        """Create sample calculation input."""
        return DutyCalculationInput(
            hs_code="12345678",
            country_code="USA",
            customs_value=Decimal("1000.00"),
            quantity=Decimal("10.0"),
            calculation_date=date.today(),
            exporter_name="Test Exporter",
            value_basis="CIF"
        )
    
    @pytest_asyncio.fixture
    async def sample_duty_rate(self, test_session: AsyncSession):
        """Create sample duty rate."""
        duty_rate = DutyRate(
            hs_code="12345678",
            general_rate=Decimal("5.0"),
            unit_type="ad_valorem",
            rate_text="5%",
            is_ad_valorem=True,
            is_specific=False,
            effective_date=date.today() - timedelta(days=30),
            is_active=True
        )
        test_session.add(duty_rate)
        await test_session.commit()
        await test_session.refresh(duty_rate)
        return duty_rate
    
    @pytest_asyncio.fixture
    async def sample_fta_rate(self, test_session: AsyncSession):
        """Create sample FTA rate."""
        fta_rate = FtaRate(
            hs_code="12345678",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("2.0"),
            effective_rate=Decimal("2.0"),
            staging_category="A",
            effective_date=date.today() - timedelta(days=30),
            rule_of_origin="WO",
            is_active=True
        )
        test_session.add(fta_rate)
        await test_session.commit()
        await test_session.refresh(fta_rate)
        return fta_rate
    
    @pytest_asyncio.fixture
    async def sample_dumping_duty(self, test_session: AsyncSession):
        """Create sample anti-dumping duty."""
        dumping_duty = DumpingDuty(
            hs_code="12345678",
            country_code="USA",
            duty_rate=Decimal("10.0"),
            duty_amount=Decimal("50.0"),
            unit="kg",
            case_number="ADN2023001",
            duty_type="anti_dumping",
            effective_date=date.today() - timedelta(days=30),
            is_active=True
        )
        test_session.add(dumping_duty)
        await test_session.commit()
        await test_session.refresh(dumping_duty)
        return dumping_duty
    
    @pytest_asyncio.fixture
    async def sample_tco(self, test_session: AsyncSession):
        """Create sample TCO exemption."""
        tco = Tco(
            tco_number="TCO2023001",
            hs_code="12345678",
            description="Test TCO exemption for testing purposes",
            effective_date=date.today() - timedelta(days=30),
            expiry_date=date.today() + timedelta(days=365),
            is_current=True
        )
        test_session.add(tco)
        await test_session.commit()
        await test_session.refresh(tco)
        return tco
    
    @pytest_asyncio.fixture
    async def sample_gst_provision(self, test_session: AsyncSession):
        """Create sample GST provision."""
        gst_provision = GstProvision(
            hs_code="12345678",
            exemption_type=None,  # Standard GST applies
            schedule_reference="Standard",
            is_active=True
        )
        test_session.add(gst_provision)
        await test_session.commit()
        await test_session.refresh(gst_provision)
        return gst_provision


@pytest.mark.unit
class TestGeneralDutyCalculation:
    """Test general duty rate calculations."""
    
    async def test_get_general_duty_rate_exact_match(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_duty_rate: DutyRate
    ):
        """Test exact HS code match for general duty rate."""
        result = await duty_service.get_general_duty_rate(test_session, "12345678")
        
        assert result is not None
        assert result.hs_code == "12345678"
        assert result.general_rate == Decimal("5.0")
        assert result.is_ad_valorem is True
    
    async def test_get_general_duty_rate_hierarchical_lookup(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession
    ):
        """Test hierarchical lookup for general duty rate."""
        # Create duty rates at different hierarchy levels
        duty_rates = [
            DutyRate(hs_code="12", general_rate=Decimal("2.0"), unit_type="ad_valorem", is_ad_valorem=True, is_active=True),
            DutyRate(hs_code="1234", general_rate=Decimal("3.0"), unit_type="ad_valorem", is_ad_valorem=True, is_active=True),
            DutyRate(hs_code="123456", general_rate=Decimal("4.0"), unit_type="ad_valorem", is_ad_valorem=True, is_active=True),
        ]
        
        for rate in duty_rates:
            test_session.add(rate)
        await test_session.commit()
        
        # Test lookup for non-exact code
        result = await duty_service.get_general_duty_rate(test_session, "12345999")
        
        assert result is not None
        assert result.hs_code == "123456"  # Should find 6-digit match
        assert result.general_rate == Decimal("4.0")
    
    async def test_get_general_duty_rate_not_found(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession
    ):
        """Test when no general duty rate is found."""
        result = await duty_service.get_general_duty_rate(test_session, "99999999")
        assert result is None
    
    async def test_calculate_ad_valorem_duty(
        self,
        duty_service: DutyCalculatorService,
        sample_calculation_input: DutyCalculationInput,
        sample_duty_rate: DutyRate
    ):
        """Test ad valorem duty calculation."""
        component = await duty_service._calculate_duty_component(
            sample_duty_rate,
            sample_calculation_input,
            "General Duty (MFN)"
        )
        
        assert component.duty_type == "General Duty"
        assert component.rate == Decimal("5.0")
        assert component.amount == Decimal("50.00")  # 5% of 1000
        assert component.basis == "Ad Valorem"
        assert component.description == "General Duty (MFN)"
    
    async def test_calculate_specific_duty(
        self,
        duty_service: DutyCalculatorService,
        sample_calculation_input: DutyCalculationInput,
        test_session: AsyncSession
    ):
        """Test specific duty calculation."""
        specific_rate = DutyRate(
            hs_code="12345678",
            general_rate=Decimal("5.0"),  # $5 per unit
            unit_type="specific",
            rate_text="$5 per kg",
            is_ad_valorem=False,
            is_specific=True,
            is_active=True
        )
        
        component = await duty_service._calculate_duty_component(
            specific_rate,
            sample_calculation_input,
            "Specific Duty"
        )
        
        assert component.duty_type == "General Duty"
        assert component.rate == Decimal("5.0")
        assert component.amount == Decimal("50.00")  # 5 * 10 units
        assert component.basis == "Specific"
        assert "Specific" in component.description
    
    async def test_calculate_free_duty(
        self,
        duty_service: DutyCalculatorService,
        sample_calculation_input: DutyCalculationInput,
        test_session: AsyncSession
    ):
        """Test free duty calculation."""
        free_rate = DutyRate(
            hs_code="12345678",
            general_rate=None,
            unit_type="free",
            rate_text="Free",
            is_ad_valorem=False,
            is_specific=False,
            is_active=True
        )
        
        component = await duty_service._calculate_duty_component(
            free_rate,
            sample_calculation_input,
            "Free Duty"
        )
        
        assert component.duty_type == "General Duty"
        assert component.rate == Decimal("0.00")
        assert component.amount == Decimal("0.00")
        assert component.basis == "Free"
        assert component.description == "Free"
@pytest.mark.unit
class TestFTADutyCalculation:
    """Test FTA preferential duty calculations."""
    
    async def test_get_best_fta_rate_exact_match(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_fta_rate: FtaRate
    ):
        """Test exact match for FTA rate."""
        result = await duty_service.get_best_fta_rate(
            test_session,
            "12345678",
            "USA",
            date.today()
        )
        
        assert result is not None
        assert result.hs_code == "12345678"
        assert result.country_code == "USA"
        assert result.preferential_rate == Decimal("2.0")
    
    async def test_get_best_fta_rate_multiple_rates(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession
    ):
        """Test selection of best (lowest) FTA rate when multiple exist."""
        fta_rates = [
            FtaRate(
                hs_code="12345678",
                fta_code="AUSFTA",
                country_code="USA",
                preferential_rate=Decimal("3.0"),
                effective_rate=Decimal("3.0"),
                effective_date=date.today() - timedelta(days=30),
                is_active=True
            ),
            FtaRate(
                hs_code="12345678",
                fta_code="TPP",
                country_code="USA",
                preferential_rate=Decimal("1.0"),
                effective_rate=Decimal("1.0"),
                effective_date=date.today() - timedelta(days=30),
                is_active=True
            )
        ]
        
        for rate in fta_rates:
            test_session.add(rate)
        await test_session.commit()
        
        result = await duty_service.get_best_fta_rate(
            test_session,
            "12345678",
            "USA",
            date.today()
        )
        
        assert result is not None
        assert result.preferential_rate == Decimal("1.0")  # Should get the lowest rate
        assert result.fta_code == "TPP"
    
    async def test_get_fta_rate_date_filtering(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession
    ):
        """Test FTA rate date filtering."""
        # Future effective date
        future_rate = FtaRate(
            hs_code="12345678",
            fta_code="FUTURE",
            country_code="USA",
            preferential_rate=Decimal("0.0"),
            effective_rate=Decimal("0.0"),
            effective_date=date.today() + timedelta(days=30),
            is_active=True
        )
        
        # Expired rate
        expired_rate = FtaRate(
            hs_code="12345678",
            fta_code="EXPIRED",
            country_code="USA",
            preferential_rate=Decimal("0.0"),
            effective_rate=Decimal("0.0"),
            effective_date=date.today() - timedelta(days=365),
            elimination_date=date.today() - timedelta(days=30),
            is_active=True
        )
        
        test_session.add(future_rate)
        test_session.add(expired_rate)
        await test_session.commit()
        
        result = await duty_service.get_best_fta_rate(
            test_session,
            "12345678",
            "USA",
            date.today()
        )
        
        assert result is None  # No valid rates for today
    
    async def test_calculate_fta_component(
        self,
        duty_service: DutyCalculatorService,
        sample_calculation_input: DutyCalculationInput,
        sample_fta_rate: FtaRate
    ):
        """Test FTA duty component calculation."""
        component = await duty_service._calculate_fta_component(
            sample_fta_rate,
            sample_calculation_input
        )
        
        assert component.duty_type == "FTA Duty"
        assert component.rate == Decimal("2.0")
        assert component.amount == Decimal("20.00")  # 2% of 1000
        assert component.basis == "FTA Preferential"
        assert "AUSFTA" in component.description
        assert component.calculation_details["fta_code"] == "AUSFTA"


@pytest.mark.unit
class TestAntiDumpingDuty:
    """Test anti-dumping duty calculations."""
    
    async def test_calculate_anti_dumping_duty_general(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_dumping_duty: DumpingDuty
    ):
        """Test general anti-dumping duty calculation."""
        result = await duty_service.calculate_anti_dumping_duty(
            test_session,
            "12345678",
            "USA",
            None,  # No specific exporter
            date.today()
        )
        
        assert result is not None
        assert result.hs_code == "12345678"
        assert result.country_code == "USA"
        assert result.duty_rate == Decimal("10.0")
        assert result.duty_amount == Decimal("50.0")
    
    async def test_calculate_anti_dumping_duty_exporter_specific(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession
    ):
        """Test exporter-specific anti-dumping duty."""
        # Create exporter-specific duty
        exporter_duty = DumpingDuty(
            hs_code="12345678",
            country_code="USA",
            exporter_name="Specific Exporter Inc",
            duty_rate=Decimal("15.0"),
            case_number="ADN2023002",
            duty_type="anti_dumping",
            effective_date=date.today() - timedelta(days=30),
            is_active=True
        )
        test_session.add(exporter_duty)
        await test_session.commit()
        
        result = await duty_service.calculate_anti_dumping_duty(
            test_session,
            "12345678",
            "USA",
            "Specific Exporter Inc",
            date.today()
        )
        
        assert result is not None
        assert result.exporter_name == "Specific Exporter Inc"
        assert result.duty_rate == Decimal("15.0")
    
    async def test_calculate_dumping_component_combined(
        self,
        duty_service: DutyCalculatorService,
        sample_calculation_input: DutyCalculationInput,
        test_session: AsyncSession
    ):
        """Test anti-dumping component with both ad valorem and specific duties."""
        combined_duty = DumpingDuty(
            hs_code="12345678",
            country_code="USA",
            duty_rate=Decimal("5.0"),  # 5% ad valorem
            duty_amount=Decimal("10.0"),  # $10 per unit
            unit="unit",
            case_number="ADN2023003",
            duty_type="anti_dumping",
            effective_date=date.today() - timedelta(days=30),
            is_active=True
        )
        
        component = await duty_service._calculate_dumping_component(
            combined_duty,
            sample_calculation_input
        )
        
        assert component.duty_type == "Anti-dumping Duty"
        assert component.rate == Decimal("5.0")
        # Total: 5% of 1000 + $10 * 10 units = 50 + 100 = 150
        assert component.amount == Decimal("150.00")
        assert "5% ad valorem" in component.description
        assert "$10.0 per unit" in component.description


@pytest.mark.unit
class TestTCOExemptions:
    """Test TCO (Tariff Concession Order) exemption logic."""
    
    async def test_check_tco_exemption_valid(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_tco: Tco
    ):
        """Test valid TCO exemption check."""
        result = await duty_service.check_tco_exemption(
            test_session,
            "12345678",
            date.today()
        )
        
        assert result is not None
        assert result.tco_number == "TCO2023001"
        assert result.hs_code == "12345678"
        assert result.is_current is True
    
    async def test_check_tco_exemption_expired(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession
    ):
        """Test expired TCO exemption."""
        expired_tco = Tco(
            tco_number="TCO2022001",
            hs_code="12345678",
            description="Expired TCO",
            effective_date=date.today() - timedelta(days=365),
            expiry_date=date.today() - timedelta(days=30),
            is_current=False
        )
        test_session.add(expired_tco)
        await test_session.commit()
        
        result = await duty_service.check_tco_exemption(
            test_session,
            "12345678",
            date.today()
        )
        
        assert result is None  # Should not find expired TCO
    
    async def test_check_tco_exemption_future(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession
    ):
        """Test future TCO exemption."""
        future_tco = Tco(
            tco_number="TCO2024001",
            hs_code="12345678",
            description="Future TCO",
            effective_date=date.today() + timedelta(days=30),
            expiry_date=date.today() + timedelta(days=365),
            is_current=True
        )
        test_session.add(future_tco)
        await test_session.commit()
        
        result = await duty_service.check_tco_exemption(
            test_session,
            "12345678",
            date.today()
        )
        
        assert result is None  # Should not find future TCO


@pytest.mark.unit
class TestGSTCalculation:
    """Test GST calculation logic."""
    
    async def test_calculate_gst_standard_rate(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_gst_provision: GstProvision
    ):
        """Test standard GST calculation."""
        duty_inclusive_value = Decimal("1100.00")  # Above threshold
        
        result = await duty_service.calculate_gst(
            test_session,
            "12345678",
            duty_inclusive_value
        )
        
        assert result is not None
        assert result.duty_type == "GST"
        assert result.rate == Decimal("10.0")  # 10%
        assert result.amount == Decimal("110.00")  # 10% of 1100
        assert result.basis == "Standard Rate"
    
    async def test_calculate_gst_below_threshold(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession
    ):
        """Test GST below threshold."""
        duty_inclusive_value = Decimal("500.00")  # Below $1000 threshold
        
        result = await duty_service.calculate_gst(
            test_session,
            "12345678",
            duty_inclusive_value
        )
        
        assert result is not None
        assert result.duty_type == "GST"
        assert result.rate == Decimal("0.00")
        assert result.amount == Decimal("0.00")
        assert result.basis == "Threshold"
        assert "below $1000.00 threshold" in result.description
    
    async def test_calculate_gst_exemption(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession
    ):
        """Test GST exemption."""
        # Create GST exemption
        exemption = GstProvision(
            hs_code="12345678",
            exemption_type="Food",
            schedule_reference="Schedule 1",
            is_active=True
        )
        test_session.add(exemption)
        await test_session.commit()
        
        duty_inclusive_value = Decimal("1100.00")
        
        result = await duty_service.calculate_gst(
            test_session,
            "12345678",
            duty_inclusive_value
        )
        
        assert result is not None
        assert result.duty_type == "GST"
        assert result.rate == Decimal("0.00")
        assert result.amount == Decimal("0.00")
        assert result.basis == "Exemption"
        assert "GST Exempt: Food" in result.description


@pytest.mark.integration
class TestComprehensiveDutyCalculation:
    """Test comprehensive duty calculation scenarios."""
    
    async def test_comprehensive_calculation_general_only(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_calculation_input: DutyCalculationInput,
        sample_duty_rate: DutyRate,
        sample_gst_provision: GstProvision
    ):
        """Test comprehensive calculation with general duty only."""
        result = await duty_service.calculate_comprehensive_duty(
            test_session,
            sample_calculation_input
        )
        
        assert result.hs_code == "12345678"
        assert result.country_code == "USA"
        assert result.customs_value == Decimal("1000.00")
        
        # General duty: 5% of 1000 = 50
        assert result.general_duty is not None
        assert result.general_duty.amount == Decimal("50.00")
        
        # No FTA, dumping, or TCO
        assert result.fta_duty is None
        assert result.anti_dumping_duty is None
        assert result.tco_exemption is None
        
        # Total duty = 50
        assert result.total_duty == Decimal("50.00")
        assert result.duty_inclusive_value == Decimal("1050.00")
        
        # GST: 10% of 1050 = 105
        assert result.gst_component is not None
        assert result.total_gst == Decimal("105.00")
        
        # Total amount: 1050 + 105 = 1155
        assert result.total_amount == Decimal("1155.00")
        
        assert result.best_rate_type == "general"
        assert len(result.calculation_steps) > 0
    
    async def test_comprehensive_calculation_with_fta(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_calculation_input: DutyCalculationInput,
        sample_duty_rate: DutyRate,
        sample_fta_rate: FtaRate,
        sample_gst_provision: GstProvision
    ):
        """Test comprehensive calculation with FTA preferential rate."""
        result = await duty_service.calculate_comprehensive_duty(
            test_session,
            sample_calculation_input
        )
        
        # Should choose FTA rate (2%) over general rate (5%)
        assert result.fta_duty is not None
        assert result.fta_duty.amount == Decimal("20.00")  # 2% of 1000
        
        assert result.general_duty is not None
        assert result.general_duty.amount == Decimal("50.00")  # 5% of 1000
        
        # Best rate should be FTA
        assert result.best_rate_type == "fta"
        assert result.total_duty == Decimal("20.00")  # FTA rate used
        assert result.potential_savings == Decimal("30.00")  # 50 - 20
    
    async def test_comprehensive_calculation_with_tco(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_calculation_input: DutyCalculationInput,
        sample_duty_rate: DutyRate,
        sample_fta_rate: FtaRate,
        sample_tco: Tco,
        sample_gst_provision: GstProvision
    ):
        """Test comprehensive calculation with TCO exemption."""
        result = await duty_service.calculate_comprehensive_duty(
            test_session,
            sample_calculation_input
        )
        
        # TCO should take precedence
        assert result.tco_exemption is not None
        assert result.tco_exemption.amount == Decimal("0.00")
        
        assert result.best_rate_type == "tco_exemption"
        assert result.total_duty == Decimal("0.00")  # TCO exemption
        assert result.potential_savings == Decimal("50.00")  # Full general duty saved
    
    async def test_comprehensive_calculation_with_dumping(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_calculation_input: DutyCalculationInput,
        sample_duty_rate: DutyRate,
        sample_fta_rate: FtaRate,
        sample_dumping_duty: DumpingDuty,
        sample_gst_provision: GstProvision
    ):
        """Test comprehensive calculation with anti-dumping duty."""
        result = await duty_service.calculate_comprehensive_duty(
            test_session,
            sample_calculation_input
        )
        
        # Should use FTA rate (2%) + anti-dumping duty
        assert result.fta_duty is not None
        assert result.anti_dumping_duty is not None
        
        # Anti-dumping: 10% of 1000 + $50 * 10 units = 100 + 500 = 600
        assert result.anti_dumping_duty.amount == Decimal("600.00")
        
        # Total duty: FTA (20) + Anti-dumping (600) = 620
        assert result.total_duty == Decimal("620.00")
        assert result.duty_inclusive_value == Decimal("1620.00")


@pytest.mark.unit
class TestDutyCalculatorEdgeCases:
    """Test edge cases and error scenarios."""
    
    async def test_calculation_with_zero_value(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_duty_rate: DutyRate
    ):
        """Test calculation with zero customs value."""
        zero_input = DutyCalculationInput(
            hs_code="12345678",
            country_code="USA",
            customs_value=Decimal("0.00")
        )
        
        result = await duty_service.calculate_comprehensive_duty(
            test_session,
            zero_input
        )
        
        assert result.customs_value == Decimal("0.00")
        assert result.total_duty == Decimal("0.00")
        assert result.total_amount == Decimal("0.00")
    
    async def test_calculation_with_no_quantity_specific_duty(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession
    ):
        """Test calculation with specific duty but no quantity provided."""
        specific_rate = DutyRate(
            hs_code="12345678",
            general_rate=Decimal("5.0"),
            unit_type="specific",
            is_specific=True,
            is_active=True
        )
        test_session.add(specific_rate)
        await test_session.commit()
        
        no_quantity_input = DutyCalculationInput(
            hs_code="12345678",
            country_code="USA",
            customs_value=Decimal("1000.00"),
            quantity=None  # No quantity provided
        )
        
        component = await duty_service._calculate_duty_component(
            specific_rate,
            no_quantity_input,
            "Specific Duty"
        )
        
        # Should default to free when quantity is missing for specific duty
        assert component.amount == Decimal("0.00")
        assert component.basis == "Free"
    
    async def test_calculation_breakdown(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_calculation_input: DutyCalculationInput,
        sample_duty_rate: DutyRate,
        sample_fta_rate: FtaRate
    ):
        """Test detailed calculation breakdown."""
        breakdown = await duty_service.get_calculation_breakdown(
            test_session,
            sample_calculation_input
        )
        
        assert "input_parameters" in breakdown
        assert "duty_components" in breakdown
        assert "totals" in breakdown
        assert "best_rate_analysis" in breakdown
        assert "calculation_steps" in breakdown
        
        # Check input parameters
        input_params = breakdown["input_parameters"]
        assert input_params["hs_code"] == "12345678"
        assert input_params["country_code"] == "USA"
        assert input_params["customs_value"] == "1000.00"
        
        # Check duty components
        duty_components = breakdown["duty_components"]
        assert "general_duty" in duty_components
        assert "fta_duty" in duty_components
        
        # Check calculation steps
        assert len(breakdown["calculation_steps"]) > 0
        assert any("Step 1" in step for step in breakdown["calculation_steps"])


@pytest.mark.unit
class TestDutyCalculatorPerformance:
    """Test performance characteristics of duty calculations."""
    
    async def test_calculation_performance_timing(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_calculation_input: DutyCalculationInput,
        sample_duty_rate: DutyRate,
        performance_timer
    ):
        """Test calculation performance timing."""
        performance_timer.start()
        
        result = await duty_service.calculate_comprehensive_duty(
            test_session,
            sample_calculation_input
        )
        
        performance_timer.stop()
        
        assert result is not None
        assert performance_timer.elapsed < 1.0  # Should complete within 1 second
    
    async def test_batch_calculation_performance(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_duty_rate: DutyRate,
        performance_timer
    ):
        """Test batch calculation performance."""
        # Create multiple calculation inputs
        inputs = []
        for i in range(10):
            inputs.append(DutyCalculationInput(
                hs_code="12345678",
                country_code="USA",
                customs_value=Decimal(f"{1000 + i}.00")
            ))
        
        performance_timer.start()
        
        # Process batch
        results = []
        for calc_input in inputs:
            result = await duty_service.calculate_comprehensive_duty(
                test_session,
                calc_input
            )
            results.append(result)
        
        performance_timer.stop()
        
        assert len(results) == 10
        assert all(r is not None for r in results)
        assert performance_timer.elapsed < 5.0  # Should complete batch within 5 seconds


@pytest.mark.external
class TestDutyCalculatorExternalIntegration:
    """Test external service integration scenarios."""
    
    @patch('services.duty_calculator.logger')
    async def test_calculation_with_logging(
        self,
        mock_logger,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession,
        sample_calculation_input: DutyCalculationInput,
        sample_duty_rate: DutyRate
    ):
        """Test calculation with proper logging."""
        result = await duty_service.calculate_comprehensive_duty(
            test_session,
            sample_calculation_input
        )
        
        assert result is not None
        # Verify logging was called (mock_logger.info should have been called)
        assert mock_logger.info.called or mock_logger.error.called
    
    async def test_calculation_error_handling(
        self,
        duty_service: DutyCalculatorService,
        test_session: AsyncSession
    ):
        """Test calculation error handling with invalid input."""
        invalid_input = DutyCalculationInput(
            hs_code="",  # Invalid empty HS code
            country_code="",
            customs_value=Decimal("-100.00")  # Invalid negative value
        )
        
        # Should handle gracefully and not crash
        try:
            result = await duty_service.calculate_comprehensive_duty(
                test_session,
                invalid_input
            )
            # If it doesn't raise an exception, result should be valid
            assert result is not None
        except Exception as e:
            # If it raises an exception, it should be a known type
            assert isinstance(e, (ValueError, TypeError))