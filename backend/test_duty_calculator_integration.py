"""
Comprehensive integration tests for the Duty Calculator Service.

This module provides complete integration test coverage for the DutyCalculatorService class,
testing real database interactions with in-memory SQLite database (no mocking).
These tests complement the unit tests by verifying actual database operations,
hierarchical lookups, and end-to-end calculation workflows.
"""

import pytest
import pytest_asyncio
from decimal import Decimal
from datetime import date, timedelta
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

# Import the service and related classes
from services.duty_calculator import (
    DutyCalculatorService,
    DutyCalculationInput,
    DutyCalculationResult,
    DutyComponent
)

# Import database models
from models.duty import DutyRate
from models.fta import FtaRate
from models.dumping import DumpingDuty
from models.tco import Tco
from models.gst import GstProvision
from models.hierarchy import TradeAgreement
from models.tariff import TariffCode
from database import Base


# Test Database Setup
@pytest_asyncio.fixture(scope="function")
async def test_engine():
    """Create in-memory SQLite engine for testing."""
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        echo=False,
        future=True
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    # Cleanup
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def test_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Create test database session."""
    async_session = async_sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as session:
        yield session


@pytest_asyncio.fixture(scope="function")
async def populated_session(test_session: AsyncSession) -> AsyncSession:
    """Create test session with comprehensive sample data."""
    # Create tariff codes
    tariff_codes = [
        TariffCode(hs_code="84", description="Nuclear reactors, boilers, machinery"),
        TariffCode(hs_code="8471", description="Automatic data processing machines"),
        TariffCode(hs_code="847130", description="Portable digital automatic data processing machines"),
        TariffCode(hs_code="8471.30.00", description="Portable digital automatic data processing machines"),
        TariffCode(hs_code="01", description="Live animals"),
        TariffCode(hs_code="0101", description="Live horses, asses, mules and hinnies"),
        TariffCode(hs_code="0101.01.00", description="Pure-bred breeding horses"),
        TariffCode(hs_code="72", description="Iron and steel"),
        TariffCode(hs_code="7208", description="Flat-rolled products of iron"),
        TariffCode(hs_code="7208.10.00", description="Hot-rolled steel sheets"),
        TariffCode(hs_code="22", description="Beverages, spirits and vinegar"),
        TariffCode(hs_code="2204", description="Wine of fresh grapes"),
        TariffCode(hs_code="2204.21.00", description="Wine in bottles")
    ]
    
    for code in tariff_codes:
        test_session.add(code)
    
    # Create duty rates with hierarchical structure
    duty_rates = [
        # Computer equipment - hierarchical rates
        DutyRate(hs_code="84", general_rate=Decimal("5.0"), unit_type="ad_valorem", rate_text="5%"),
        DutyRate(hs_code="8471", general_rate=Decimal("0.0"), unit_type="ad_valorem", rate_text="Free"),
        DutyRate(hs_code="8471.30.00", general_rate=Decimal("0.0"), unit_type="ad_valorem", rate_text="Free"),
        
        # Live animals
        DutyRate(hs_code="01", general_rate=Decimal("0.0"), unit_type="ad_valorem", rate_text="Free"),
        DutyRate(hs_code="0101.01.00", general_rate=Decimal("0.0"), unit_type="ad_valorem", rate_text="Free"),
        
        # Steel products
        DutyRate(hs_code="72", general_rate=Decimal("5.0"), unit_type="ad_valorem", rate_text="5%"),
        DutyRate(hs_code="7208.10.00", general_rate=Decimal("0.0"), unit_type="ad_valorem", rate_text="Free"),
        
        # Wine
        DutyRate(hs_code="22", general_rate=Decimal("5.0"), unit_type="ad_valorem", rate_text="5%"),
        DutyRate(hs_code="2204.21.00", general_rate=Decimal("5.0"), unit_type="ad_valorem", rate_text="5%")
    ]
    
    for rate in duty_rates:
        test_session.add(rate)
    
    # Create trade agreements
    trade_agreements = [
        TradeAgreement(
            agreement_code="AUSFTA",
            agreement_name="Australia-United States Free Trade Agreement",
            country_codes=["USA"],
            effective_date=date(2005, 1, 1),
            is_active=True
        ),
        TradeAgreement(
            agreement_code="AANZFTA",
            agreement_name="ASEAN-Australia-New Zealand Free Trade Agreement",
            country_codes=["NZL", "SGP", "THA", "MYS"],
            effective_date=date(2010, 1, 1),
            is_active=True
        ),
        TradeAgreement(
            agreement_code="CPTPP",
            agreement_name="Comprehensive and Progressive Trans-Pacific Partnership",
            country_codes=["JPN", "CAN", "MEX", "SGP", "VNM"],
            effective_date=date(2018, 12, 30),
            is_active=True
        )
    ]
    
    for agreement in trade_agreements:
        test_session.add(agreement)
    
    await test_session.commit()
    return test_session


@pytest_asyncio.fixture
async def calculator():
    """Create DutyCalculatorService instance for testing."""
    return DutyCalculatorService()


class TestDutyCalculatorIntegration:
    """Base integration test class for duty calculator service."""
    
    @pytest.mark.asyncio
    async def test_service_initialization(self, calculator):
        """Test service initializes correctly."""
        assert calculator.gst_rate == Decimal('0.10')
        assert calculator.gst_threshold == Decimal('1000.00')
    
    @pytest.mark.asyncio
    async def test_database_connection(self, populated_session):
        """Test database connection and basic queries."""
        # Test basic query
        result = await populated_session.execute(text("SELECT 1"))
        assert result.scalar() == 1
        
        # Test data exists
        duty_count = await populated_session.execute(text("SELECT COUNT(*) FROM duty_rates"))
        assert duty_count.scalar() > 0
class TestHierarchicalHsCodeLookup:
    """Test hierarchical HS code lookup behavior across all models."""
    
    @pytest.mark.asyncio
    async def test_duty_rate_exact_match(self, calculator, populated_session):
        """Test exact HS code match for duty rates."""
        result = await calculator.get_general_duty_rate(populated_session, "8471.30.00")
        
        assert result is not None
        assert result.hs_code == "8471.30.00"
        assert result.general_rate == Decimal("0.0")
        assert result.rate_text == "Free"
    
    @pytest.mark.asyncio
    async def test_duty_rate_hierarchical_lookup(self, calculator, populated_session):
        """Test hierarchical lookup for duty rates."""
        # Test with 10-digit code that should find 8-digit match
        result = await calculator.get_general_duty_rate(populated_session, "8471.30.0099")
        
        assert result is not None
        assert result.hs_code == "8471.30.00"
        assert result.general_rate == Decimal("0.0")
    
    @pytest.mark.asyncio
    async def test_duty_rate_fallback_to_chapter(self, calculator, populated_session):
        """Test fallback to chapter level for duty rates."""
        # Test with code that should fallback to chapter 84
        result = await calculator.get_general_duty_rate(populated_session, "8499.99.99")
        
        assert result is not None
        assert result.hs_code == "84"
        assert result.general_rate == Decimal("5.0")
    
    @pytest.mark.asyncio
    async def test_no_match_found(self, calculator, populated_session):
        """Test when no match is found at any hierarchical level."""
        result = await calculator.get_general_duty_rate(populated_session, "9999.99.99")
        assert result is None


class TestFtaRateSelection:
    """Test FTA rate optimization with multiple agreements and staging categories."""
    
    @pytest.mark.asyncio
    async def test_single_fta_rate_selection(self, calculator, populated_session):
        """Test selection when only one FTA rate is available."""
        # First add FTA rates to the populated session
        fta_rates = [
            FtaRate(
                hs_code="8471.30.00",
                fta_code="AUSFTA",
                country_code="USA",
                preferential_rate=Decimal("0.0"),
                effective_rate=Decimal("0.0"),
                staging_category="A",
                rule_of_origin="WO",
                effective_date=date(2005, 1, 1),
                is_quota_applicable=False
            ),
            FtaRate(
                hs_code="2204.21.00",
                fta_code="AANZFTA",
                country_code="NZL",
                preferential_rate=Decimal("0.0"),
                effective_rate=Decimal("0.0"),
                staging_category="A",
                rule_of_origin="WO",
                effective_date=date(2010, 1, 1),
                is_quota_applicable=False
            )
        ]
        
        for rate in fta_rates:
            populated_session.add(rate)
        await populated_session.commit()
        
        calc_date = date(2024, 6, 15)
        
        result = await calculator.get_best_fta_rate(
            populated_session, "8471.30.00", "USA", calc_date
        )
        
        assert result is not None
        assert result.fta_code == "AUSFTA"
        assert result.country_code == "USA"
        assert result.effective_rate == Decimal("0.0")
    
    @pytest.mark.asyncio
    async def test_fta_rate_date_filtering(self, calculator, populated_session):
        """Test FTA rate date filtering."""
        # Add FTA rate
        fta_rate = FtaRate(
            hs_code="8471.30.00",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("0.0"),
            effective_rate=Decimal("0.0"),
            staging_category="A",
            rule_of_origin="WO",
            effective_date=date(2005, 1, 1),
            is_quota_applicable=False
        )
        populated_session.add(fta_rate)
        await populated_session.commit()
        
        # Test with date before FTA effective date
        calc_date = date(2004, 12, 31)  # Before AUSFTA
        
        result = await calculator.get_best_fta_rate(
            populated_session, "8471.30.00", "USA", calc_date
        )
        
        assert result is None  # No rate should be effective
        
        # Test with date after effective date
        calc_date = date(2024, 6, 15)
        result = await calculator.get_best_fta_rate(
            populated_session, "8471.30.00", "USA", calc_date
        )
        
        assert result is not None
        assert result.fta_code == "AUSFTA"


class TestAntiDumpingDutyIntegration:
    """Test anti-dumping duty application with complex scenarios."""
    
    @pytest.mark.asyncio
    async def test_exporter_specific_duty(self, calculator, populated_session):
        """Test exporter-specific anti-dumping duty selection."""
        # Add anti-dumping duties
        dumping_duties = [
            DumpingDuty(
                hs_code="7208.10.00",
                country_code="CHN",
                case_number="ADC2023-002",
                duty_type="dumping",
                duty_rate=Decimal("23.6"),
                is_active=True,
                effective_date=date(2023, 1, 1),
                exporter_name=None  # General duty
            ),
            DumpingDuty(
                hs_code="7208.10.00",
                country_code="CHN",
                case_number="ADC2023-002",
                duty_type="dumping",
                duty_rate=Decimal("15.5"),
                is_active=True,
                effective_date=date(2023, 1, 1),
                exporter_name="Beijing Steel Works"
            )
        ]
        
        for duty in dumping_duties:
            populated_session.add(duty)
        await populated_session.commit()
        
        calc_date = date(2024, 6, 15)
        
        result = await calculator.calculate_anti_dumping_duty(
            populated_session, "7208.10.00", "CHN", "Beijing Steel Works", calc_date
        )
        
        assert result is not None
        assert result.exporter_name == "Beijing Steel Works"
        assert result.duty_rate == Decimal("15.5")  # Exporter-specific rate
        assert result.case_number == "ADC2023-002"
    
    @pytest.mark.asyncio
    async def test_general_duty_fallback(self, calculator, populated_session):
        """Test fallback to general country duty when exporter-specific not found."""
        # Add general anti-dumping duty
        dumping_duty = DumpingDuty(
            hs_code="7208.10.00",
            country_code="CHN",
            case_number="ADC2023-002",
            duty_type="dumping",
            duty_rate=Decimal("23.6"),
            is_active=True,
            effective_date=date(2023, 1, 1),
            exporter_name=None  # General duty
        )
        populated_session.add(dumping_duty)
        await populated_session.commit()
        
        calc_date = date(2024, 6, 15)
        
        result = await calculator.calculate_anti_dumping_duty(
            populated_session, "7208.10.00", "CHN", "Unknown Exporter", calc_date
        )
        
        assert result is not None
        assert result.exporter_name is None  # General duty
        assert result.duty_rate == Decimal("23.6")  # General rate
        assert result.case_number == "ADC2023-002"


class TestTcoExemptionIntegration:
    """Test TCO exemption workflows with expiry date checking."""
    
    @pytest.mark.asyncio
    async def test_valid_tco_exemption(self, calculator, populated_session):
        """Test finding valid TCO exemption."""
        # Add TCO exemption
        tco = Tco(
            tco_number="TCO2024001",
            hs_code="8471.30.00",
            description="Portable digital automatic data processing machines weighing not more than 10 kg",
            applicant_name="Tech Import Pty Ltd",
            effective_date=date(2024, 1, 1),
            expiry_date=date(2025, 12, 31),
            is_current=True
        )
        populated_session.add(tco)
        await populated_session.commit()
        
        calc_date = date(2024, 6, 15)
        
        result = await calculator.check_tco_exemption(
            populated_session, "8471.30.00", calc_date
        )
        
        assert result is not None
        assert result.tco_number == "TCO2024001"
        assert result.hs_code == "8471.30.00"
        assert result.is_current is True
        assert result.effective_date <= calc_date
        assert result.expiry_date > calc_date
    
    @pytest.mark.asyncio
    async def test_expired_tco_not_found(self, calculator, populated_session):
        """Test that expired TCO is not found."""
        # Add expired TCO
        tco = Tco(
            tco_number="TCO2024002",
            hs_code="0101.01.00",
            description="Pure-bred breeding horses for racing purposes",
            applicant_name="Racing Australia Ltd",
            effective_date=date(2024, 1, 1),
            expiry_date=date(2024, 12, 31),  # Expires soon
            is_current=True
        )
        populated_session.add(tco)
        await populated_session.commit()
        
        calc_date = date(2025, 6, 15)  # After TCO2024002 expiry
        
        result = await calculator.check_tco_exemption(
            populated_session, "0101.01.00", calc_date
        )
        
        assert result is None  # TCO2024002 should be expired


class TestGstCalculationIntegration:
    """Test GST calculations with various exemption types."""
    
    @pytest.mark.asyncio
    async def test_standard_gst_calculation(self, calculator, populated_session):
        """Test standard GST calculation above threshold."""
        # Add GST provisions
        gst_provision = GstProvision(
            hs_code=None,
            exemption_type=None,
            schedule_reference="Schedule 4",
            is_active=True
        )
        populated_session.add(gst_provision)
        await populated_session.commit()
        
        duty_inclusive_value = Decimal('1500.00')
        
        result = await calculator.calculate_gst(
            populated_session, "8471.30.00", duty_inclusive_value
        )
        
        assert result is not None
        assert result.duty_type == "GST"
        assert result.rate == Decimal('10.0')  # 10%
        assert result.amount == Decimal('150.00')  # 10% of 1500
        assert result.description == "Goods and Services Tax (10%)"
        assert result.basis == "Standard Rate"
    
    @pytest.mark.asyncio
    async def test_below_threshold_no_gst(self, calculator, populated_session):
        """Test no GST when below threshold."""
        duty_inclusive_value = Decimal('500.00')  # Below $1000 threshold
        
        result = await calculator.calculate_gst(
            populated_session, "8471.30.00", duty_inclusive_value
        )
        
        assert result is not None
        assert result.duty_type == "GST"
        assert result.rate == Decimal('0.00')
        assert result.amount == Decimal('0.00')
        assert "below" in result.description
        assert result.basis == "Threshold"


class TestEndToEndCalculations:
    """Test complete end-to-end calculation workflows."""
    
    @pytest.mark.asyncio
    async def test_computer_import_from_usa_with_fta(self, calculator, populated_session):
        """Test realistic scenario: Computer import from USA with FTA benefit."""
        # Add FTA rate
        fta_rate = FtaRate(
            hs_code="8471.30.00",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("0.0"),
            effective_rate=Decimal("0.0"),
            staging_category="A",
            rule_of_origin="WO",
            effective_date=date(2005, 1, 1),
            is_quota_applicable=False
        )
        populated_session.add(fta_rate)
        await populated_session.commit()
        
        input_data = DutyCalculationInput(
            hs_code="8471.30.00",
            country_code="USA",
            customs_value=Decimal('2500.00'),
            quantity=Decimal('5'),
            calculation_date=date(2024, 6, 15),
            exporter_name="Dell Inc"
        )
        
        result = await calculator.calculate_comprehensive_duty(populated_session, input_data)
        
        # Verify comprehensive calculation
        assert result.hs_code == "8471.30.00"
        assert result.country_code == "USA"
        assert result.customs_value == Decimal('2500.00')
        
        # Should have general duty
        assert result.general_duty is not None
        assert result.general_duty.rate == Decimal('0.0')  # Free
        
        # Should have FTA duty (better than general)
        assert result.fta_duty is not None
        assert result.fta_duty.rate == Decimal('0.0')
        
        # Should use FTA rate as best
        assert result.best_rate_type == "fta"
        assert result.total_duty == Decimal('0.00')
        
        # GST calculation
        assert result.duty_inclusive_value == Decimal('2500.00')  # No duty
        assert result.gst_component is not None
        assert result.total_gst == Decimal('250.00')  # 10% of 2500
        assert result.total_amount == Decimal('2750.00')  # 2500 + 0 + 250
        
        # Calculation steps should be present
        assert len(result.calculation_steps) > 0
        assert any("Step 1" in step for step in result.calculation_steps)
    
    @pytest.mark.asyncio
    async def test_steel_import_with_anti_dumping(self, calculator, populated_session):
        """Test steel import with anti-dumping duty."""
        # Add anti-dumping duty
        dumping_duty = DumpingDuty(
            hs_code="7208.10.00",
            country_code="CHN",
            case_number="ADC2023-002",
            duty_type="dumping",
            duty_rate=Decimal("15.5"),
            is_active=True,
            effective_date=date(2023, 1, 1),
            exporter_name="Beijing Steel Works"
        )
        populated_session.add(dumping_duty)
        await populated_session.commit()
        
        input_data = DutyCalculationInput(
            hs_code="7208.10.00",
            country_code="CHN",
            customs_value=Decimal('50000.00'),
            quantity=Decimal('25'),
            calculation_date=date(2024, 6, 15),
            exporter_name="Beijing Steel Works"
        )
        
        result = await calculator.calculate_comprehensive_duty(populated_session, input_data)
        
        # Should have general duty (free)
        assert result.general_duty is not None
        assert result.general_duty.rate == Decimal('0.0')
        
        # Should have anti-dumping duty
        assert result.anti_dumping_duty is not None
        assert result.anti_dumping_duty.rate == Decimal('15.5')  # Exporter-specific
        
        # Total duty should include anti-dumping
        expected_dumping = Decimal('50000.00') * Decimal('15.5') / 100
        assert result.total_duty == expected_dumping
        
        # GST on duty-inclusive value
        duty_inclusive = Decimal('50000.00') + expected_dumping
        assert result.duty_inclusive_value == duty_inclusive
        assert result.total_gst == duty_inclusive * Decimal('0.10')


class TestDatabaseErrorHandling:
    """Test error handling with database connection issues."""
    
    @pytest.mark.asyncio
    async def test_database_connection_error_handling(self, calculator):
        """Test handling of database connection errors."""
        # Create a closed session to simulate connection errors
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        await engine.dispose()  # Close immediately
        
        async_session = async_sessionmaker(engine, class_=AsyncSession)
        
        async with async_session() as session:
            # These should handle errors gracefully and return None
            result = await calculator.get_general_duty_rate(session, "8471.30.00")
            assert result is None
            
            result = await calculator.get_best_fta_rate(
                session, "8471.30.00", "USA", date(2024, 6, 15)
            )
            assert result is None
            
            result = await calculator.check_tco_exemption(
                session, "8471.30.00", date(2024, 6, 15)
            )
            assert result is None
            
            result = await calculator.calculate_anti_dumping_duty(
                session, "8471.30.00", "CHN", "Test Exporter", date(2024, 6, 15)
            )
            assert result is None
            
            result = await calculator.calculate_gst(
                session, "8471.30.00", Decimal('1500.00')
            )
            assert result is None
    
    @pytest.mark.asyncio
    async def test_comprehensive_calculation_error_handling(self, calculator):
        """Test comprehensive calculation with database errors."""
        # Create a closed session
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        await engine.dispose()
        
        async_session = async_sessionmaker(engine, class_=AsyncSession)
        
        input_data = DutyCalculationInput(
            hs_code="8471.30.00",
            country_code="USA",
            customs_value=Decimal('1000.00')
        )
        
        async with async_session() as session:
            # Should raise an exception for comprehensive calculation
            with pytest.raises(Exception):
                await calculator.calculate_comprehensive_duty(session, input_data)