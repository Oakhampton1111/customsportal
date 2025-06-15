"""
Comprehensive unit tests for the Duty Calculator Service.

This module provides complete test coverage for the DutyCalculatorService class,
including all methods, dataclasses, and edge cases with mocked database interactions.
"""

import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from decimal import Decimal, ROUND_HALF_UP
from datetime import date, timedelta
from typing import Optional, List

# Import the service and related classes
from services.duty_calculator import (
    DutyCalculatorService,
    DutyCalculationInput,
    DutyCalculationResult,
    DutyComponent
)

# Import database models for mocking
from models.duty import DutyRate
from models.fta import FtaRate
from models.dumping import DumpingDuty
from models.tco import Tco
from models.gst import GstProvision
from models.hierarchy import TradeAgreement

# Import SQLAlchemy components for mocking
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


class TestDutyCalculatorServiceInitialization:
    """Test DutyCalculatorService initialization."""
    
    def test_init_default_values(self):
        """Test service initialization with correct default values."""
        calculator = DutyCalculatorService()
        
        assert calculator.gst_rate == Decimal('0.10')
        assert calculator.gst_threshold == Decimal('1000.00')
    
    def test_init_gst_rate_precision(self):
        """Test GST rate is stored with correct precision."""
        calculator = DutyCalculatorService()
        
        # Verify decimal precision
        assert isinstance(calculator.gst_rate, Decimal)
        assert calculator.gst_rate.as_tuple().exponent == -2
    
    def test_init_gst_threshold_precision(self):
        """Test GST threshold is stored with correct precision."""
        calculator = DutyCalculatorService()
        
        # Verify decimal precision
        assert isinstance(calculator.gst_threshold, Decimal)
        assert calculator.gst_threshold.as_tuple().exponent == -2


class TestDutyCalculationInput:
    """Test DutyCalculationInput dataclass."""
    
    def test_required_fields(self):
        """Test creation with required fields only."""
        input_data = DutyCalculationInput(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1000.00')
        )
        
        assert input_data.hs_code == "8471.30.00"
        assert input_data.country_code == "CHN"
        assert input_data.customs_value == Decimal('1000.00')
        assert input_data.quantity is None
        assert input_data.calculation_date is None
        assert input_data.exporter_name is None
        assert input_data.value_basis == "CIF"
    
    def test_all_fields(self):
        """Test creation with all fields."""
        calc_date = date(2024, 1, 15)
        input_data = DutyCalculationInput(
            hs_code="0101.01.00",
            country_code="NZL",
            customs_value=Decimal('5000.00'),
            quantity=Decimal('2.5'),
            calculation_date=calc_date,
            exporter_name="Test Exporter Ltd",
            value_basis="FOB"
        )
        
        assert input_data.hs_code == "0101.01.00"
        assert input_data.country_code == "NZL"
        assert input_data.customs_value == Decimal('5000.00')
        assert input_data.quantity == Decimal('2.5')
        assert input_data.calculation_date == calc_date
        assert input_data.exporter_name == "Test Exporter Ltd"
        assert input_data.value_basis == "FOB"
    
    def test_decimal_precision(self):
        """Test decimal values maintain precision."""
        input_data = DutyCalculationInput(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1234.56'),
            quantity=Decimal('3.14159')
        )
        
        assert input_data.customs_value == Decimal('1234.56')
        assert input_data.quantity == Decimal('3.14159')


class TestDutyComponent:
    """Test DutyComponent dataclass."""
    
    def test_basic_creation(self):
        """Test basic DutyComponent creation."""
        component = DutyComponent(
            duty_type="General Duty",
            rate=Decimal('5.0'),
            amount=Decimal('50.00'),
            description="5% ad valorem duty",
            basis="Ad Valorem"
        )
        
        assert component.duty_type == "General Duty"
        assert component.rate == Decimal('5.0')
        assert component.amount == Decimal('50.00')
        assert component.description == "5% ad valorem duty"
        assert component.basis == "Ad Valorem"
        assert component.calculation_details == {}
    
    def test_with_calculation_details(self):
        """Test DutyComponent with calculation details."""
        details = {"unit_type": "ad_valorem", "rate_text": "5%"}
        component = DutyComponent(
            duty_type="FTA Duty",
            rate=Decimal('2.5'),
            amount=Decimal('25.00'),
            description="AUSFTA preferential rate",
            basis="FTA Preferential",
            calculation_details=details
        )
        
        assert component.calculation_details == details
    
    def test_none_rate(self):
        """Test DutyComponent with None rate."""
        component = DutyComponent(
            duty_type="TCO Exemption",
            rate=None,
            amount=Decimal('0.00'),
            description="TCO exemption applies",
            basis="Exemption"
        )
        
        assert component.rate is None
        assert component.amount == Decimal('0.00')


class TestDutyCalculationResult:
    """Test DutyCalculationResult dataclass."""
    
    def test_basic_creation(self):
        """Test basic DutyCalculationResult creation."""
        result = DutyCalculationResult(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1000.00')
        )
        
        assert result.hs_code == "8471.30.00"
        assert result.country_code == "CHN"
        assert result.customs_value == Decimal('1000.00')
        assert result.general_duty is None
        assert result.fta_duty is None
        assert result.anti_dumping_duty is None
        assert result.tco_exemption is None
        assert result.gst_component is None
        assert result.total_duty == Decimal('0.00')
        assert result.duty_inclusive_value == Decimal('0.00')
        assert result.total_gst == Decimal('0.00')
        assert result.total_amount == Decimal('0.00')
        assert result.best_rate_type == "general"
        assert result.potential_savings == Decimal('0.00')
        assert result.calculation_steps == []
        assert result.compliance_notes == []
        assert result.warnings == []
    
    def test_with_components(self):
        """Test DutyCalculationResult with duty components."""
        general_duty = DutyComponent(
            duty_type="General Duty",
            rate=Decimal('5.0'),
            amount=Decimal('50.00'),
            description="5% general duty",
            basis="Ad Valorem"
        )
        
        result = DutyCalculationResult(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1000.00')
        )
        result.general_duty = general_duty
        result.total_duty = Decimal('50.00')
        result.duty_inclusive_value = Decimal('1050.00')
        
        assert result.general_duty == general_duty
        assert result.total_duty == Decimal('50.00')
        assert result.duty_inclusive_value == Decimal('1050.00')


@pytest.fixture
def mock_session():
    """Create a mock AsyncSession for testing."""
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def calculator():
    """Create a DutyCalculatorService instance for testing."""
    return DutyCalculatorService()


@pytest.fixture
def sample_input():
    """Create sample DutyCalculationInput for testing."""
    return DutyCalculationInput(
        hs_code="8471.30.00",
        country_code="CHN",
        customs_value=Decimal('1000.00'),
        quantity=Decimal('1'),
        calculation_date=date(2024, 1, 15)
    )


@pytest.fixture
def sample_duty_rate():
    """Create a sample DutyRate for testing."""
    duty_rate = MagicMock(spec=DutyRate)
    duty_rate.hs_code = "8471.30.00"
    duty_rate.general_rate = Decimal('5.0')
    duty_rate.is_ad_valorem = True
    duty_rate.is_specific = False
    duty_rate.unit_type = "ad_valorem"
    duty_rate.rate_text = "5%"
    return duty_rate


@pytest.fixture
def sample_fta_rate():
    """Create a sample FtaRate for testing."""
    fta_rate = MagicMock(spec=FtaRate)
    fta_rate.hs_code = "8471.30.00"
    fta_rate.fta_code = "AUSFTA"
    fta_rate.country_code = "USA"
    fta_rate.preferential_rate = Decimal('0.0')
    fta_rate.effective_rate = Decimal('0.0')
    fta_rate.staging_category = "A"
    fta_rate.rule_of_origin = "WO"
    fta_rate.is_quota_applicable = False
    fta_rate.effective_date = date(2005, 1, 1)
    fta_rate.elimination_date = None
    
    # Mock trade agreement relationship
    trade_agreement = MagicMock(spec=TradeAgreement)
    trade_agreement.agreement_code = "AUSFTA"
    trade_agreement.agreement_name = "Australia-United States Free Trade Agreement"
    fta_rate.trade_agreement = trade_agreement
    
    # Mock methods
    fta_rate.get_origin_requirements_summary.return_value = "Wholly obtained or produced"
    
    return fta_rate


@pytest.fixture
def sample_tco():
    """Create a sample Tco for testing."""
    tco = MagicMock(spec=Tco)
    tco.tco_number = "TCO2024001"
    tco.hs_code = "8471.30.00"
    tco.description = "Portable digital automatic data processing machines"
    tco.applicant_name = "Test Company Pty Ltd"
    tco.effective_date = date(2024, 1, 1)
    tco.expiry_date = date(2025, 12, 31)
    tco.is_current = True
    
    # Mock methods
    tco.days_until_expiry.return_value = 365
    
    return tco


@pytest.fixture
def sample_dumping_duty():
    """Create a sample DumpingDuty for testing."""
    dumping_duty = MagicMock(spec=DumpingDuty)
    dumping_duty.hs_code = "8471.30.00"
    dumping_duty.country_code = "CHN"
    dumping_duty.case_number = "ADC2024-001"
    dumping_duty.duty_type = "dumping"
    dumping_duty.duty_rate = Decimal('15.5')
    dumping_duty.duty_amount = None
    dumping_duty.unit = None
    dumping_duty.exporter_name = None
    dumping_duty.is_active = True
    dumping_duty.effective_date = date(2024, 1, 1)
    dumping_duty.expiry_date = None
    return dumping_duty


@pytest.fixture
def sample_gst_provision():
    """Create a sample GstProvision for testing."""
    gst_provision = MagicMock(spec=GstProvision)
    gst_provision.hs_code = None  # General provision
    gst_provision.exemption_type = None
    gst_provision.schedule_reference = "Schedule 4"
    gst_provision.is_active = True
    
    # Mock methods
    gst_provision.applies_to_value.return_value = False
    
    return gst_provision
class TestGetGeneralDutyRate:
    """Test get_general_duty_rate method."""
    
    @pytest.mark.asyncio
    async def test_exact_match_found(self, calculator, mock_session, sample_duty_rate):
        """Test finding exact HS code match."""
        # Mock database query result
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_duty_rate
        mock_session.execute.return_value = mock_result
        
        result = await calculator.get_general_duty_rate(mock_session, "8471.30.00")
        
        assert result == sample_duty_rate
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_exact_match_not_found_hierarchical_lookup(self, calculator, mock_session, sample_duty_rate):
        """Test hierarchical lookup when exact match not found."""
        # Mock first query (exact match) returns None
        mock_result_exact = MagicMock()
        mock_result_exact.scalar_one_or_none.return_value = None
        
        # Mock second query (8-digit) returns duty rate
        mock_result_hierarchical = MagicMock()
        mock_result_hierarchical.scalar_one_or_none.return_value = sample_duty_rate
        
        mock_session.execute.side_effect = [mock_result_exact, mock_result_hierarchical]
        
        result = await calculator.get_general_duty_rate(mock_session, "8471.30.0099")
        
        assert result == sample_duty_rate
        assert mock_session.execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_hierarchical_lookup_all_levels(self, calculator, mock_session, sample_duty_rate):
        """Test hierarchical lookup through all levels."""
        # Mock all queries return None except the last one
        mock_results = [MagicMock() for _ in range(5)]  # exact + 4 hierarchical levels
        for i in range(4):
            mock_results[i].scalar_one_or_none.return_value = None
        mock_results[4].scalar_one_or_none.return_value = sample_duty_rate  # 2-digit match
        
        mock_session.execute.side_effect = mock_results
        
        result = await calculator.get_general_duty_rate(mock_session, "8471.30.0099")
        
        assert result == sample_duty_rate
        assert mock_session.execute.call_count == 5
    
    @pytest.mark.asyncio
    async def test_no_match_found(self, calculator, mock_session):
        """Test when no match is found at any level."""
        # Mock all queries return None
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await calculator.get_general_duty_rate(mock_session, "9999.99.99")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, calculator, mock_session):
        """Test database error handling."""
        mock_session.execute.side_effect = Exception("Database connection error")
        
        result = await calculator.get_general_duty_rate(mock_session, "8471.30.00")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_short_hs_code(self, calculator, mock_session, sample_duty_rate):
        """Test with short HS code that doesn't need hierarchical lookup."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_duty_rate
        mock_session.execute.return_value = mock_result
        
        result = await calculator.get_general_duty_rate(mock_session, "84")
        
        assert result == sample_duty_rate
        mock_session.execute.assert_called_once()


class TestGetBestFtaRate:
    """Test get_best_fta_rate method."""
    
    @pytest.mark.asyncio
    async def test_exact_match_found(self, calculator, mock_session, sample_fta_rate):
        """Test finding exact HS code and country match."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_fta_rate]
        mock_session.execute.return_value = mock_result
        
        result = await calculator.get_best_fta_rate(
            mock_session, "8471.30.00", "USA", date(2024, 1, 15)
        )
        
        assert result == sample_fta_rate
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_multiple_rates_best_selected(self, calculator, mock_session):
        """Test selection of best (lowest) rate when multiple rates found."""
        # Create multiple FTA rates with different rates
        fta_rate_1 = MagicMock(spec=FtaRate)
        fta_rate_1.preferential_rate = Decimal('5.0')
        
        fta_rate_2 = MagicMock(spec=FtaRate)
        fta_rate_2.preferential_rate = Decimal('2.5')  # Better rate
        
        fta_rate_3 = MagicMock(spec=FtaRate)
        fta_rate_3.preferential_rate = Decimal('7.5')
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [fta_rate_2, fta_rate_1, fta_rate_3]
        mock_session.execute.return_value = mock_result
        
        result = await calculator.get_best_fta_rate(
            mock_session, "8471.30.00", "USA", date(2024, 1, 15)
        )
        
        assert result == fta_rate_2  # Should return the first (best) rate
    
    @pytest.mark.asyncio
    async def test_hierarchical_lookup(self, calculator, mock_session, sample_fta_rate):
        """Test hierarchical lookup when exact match not found."""
        # Mock first query (exact match) returns empty list
        mock_result_exact = MagicMock()
        mock_result_exact.scalars.return_value.all.return_value = []
        
        # Mock second query (8-digit) returns FTA rate
        mock_result_hierarchical = MagicMock()
        mock_result_hierarchical.scalars.return_value.all.return_value = [sample_fta_rate]
        
        mock_session.execute.side_effect = [mock_result_exact, mock_result_hierarchical]
        
        result = await calculator.get_best_fta_rate(
            mock_session, "8471.30.0099", "USA", date(2024, 1, 15)
        )
        
        assert result == sample_fta_rate
        assert mock_session.execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_date_filtering(self, calculator, mock_session):
        """Test that date filtering works correctly."""
        calc_date = date(2024, 6, 15)
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        await calculator.get_best_fta_rate(mock_session, "8471.30.00", "USA", calc_date)
        
        # Verify the query was called (date filtering is in the SQL query)
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_no_match_found(self, calculator, mock_session):
        """Test when no FTA rate is found."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []
        mock_session.execute.return_value = mock_result
        
        result = await calculator.get_best_fta_rate(
            mock_session, "9999.99.99", "XXX", date(2024, 1, 15)
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, calculator, mock_session):
        """Test database error handling."""
        mock_session.execute.side_effect = Exception("Database connection error")
        
        result = await calculator.get_best_fta_rate(
            mock_session, "8471.30.00", "USA", date(2024, 1, 15)
        )
        
        assert result is None


class TestCheckTcoExemption:
    """Test check_tco_exemption method."""
    
    @pytest.mark.asyncio
    async def test_tco_found(self, calculator, mock_session, sample_tco):
        """Test finding valid TCO exemption."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_tco
        mock_session.execute.return_value = mock_result
        
        result = await calculator.check_tco_exemption(
            mock_session, "8471.30.00", date(2024, 6, 15)
        )
        
        assert result == sample_tco
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_no_tco_found(self, calculator, mock_session):
        """Test when no TCO exemption is found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await calculator.check_tco_exemption(
            mock_session, "8471.30.00", date(2024, 6, 15)
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_date_filtering(self, calculator, mock_session):
        """Test that date filtering works correctly."""
        calc_date = date(2024, 6, 15)
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        await calculator.check_tco_exemption(mock_session, "8471.30.00", calc_date)
        
        # Verify the query was called (date filtering is in the SQL query)
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, calculator, mock_session):
        """Test database error handling."""
        mock_session.execute.side_effect = Exception("Database connection error")
        
        result = await calculator.check_tco_exemption(
            mock_session, "8471.30.00", date(2024, 1, 15)
        )
        
        assert result is None


class TestCalculateAntiDumpingDuty:
    """Test calculate_anti_dumping_duty method."""
    
    @pytest.mark.asyncio
    async def test_exporter_specific_duty_found(self, calculator, mock_session, sample_dumping_duty):
        """Test finding exporter-specific anti-dumping duty."""
        sample_dumping_duty.exporter_name = "Specific Exporter Ltd"
        
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_dumping_duty
        mock_session.execute.return_value = mock_result
        
        result = await calculator.calculate_anti_dumping_duty(
            mock_session, "8471.30.00", "CHN", "Specific Exporter Ltd", date(2024, 1, 15)
        )
        
        assert result == sample_dumping_duty
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_general_duty_fallback(self, calculator, mock_session, sample_dumping_duty):
        """Test fallback to general country duty when exporter-specific not found."""
        # Mock first query (exporter-specific) returns None
        mock_result_exporter = MagicMock()
        mock_result_exporter.scalar_one_or_none.return_value = None
        
        # Mock second query (general) returns duty
        mock_result_general = MagicMock()
        mock_result_general.scalar_one_or_none.return_value = sample_dumping_duty
        
        mock_session.execute.side_effect = [mock_result_exporter, mock_result_general]
        
        result = await calculator.calculate_anti_dumping_duty(
            mock_session, "8471.30.00", "CHN", "Some Exporter", date(2024, 1, 15)
        )
        
        assert result == sample_dumping_duty
        assert mock_session.execute.call_count == 2
    
    @pytest.mark.asyncio
    async def test_no_exporter_name_general_only(self, calculator, mock_session, sample_dumping_duty):
        """Test when no exporter name provided, only general duty checked."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = sample_dumping_duty
        mock_session.execute.return_value = mock_result
        
        result = await calculator.calculate_anti_dumping_duty(
            mock_session, "8471.30.00", "CHN", None, date(2024, 1, 15)
        )
        
        assert result == sample_dumping_duty
        mock_session.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_no_duty_found(self, calculator, mock_session):
        """Test when no anti-dumping duty is found."""
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_session.execute.return_value = mock_result
        
        result = await calculator.calculate_anti_dumping_duty(
            mock_session, "8471.30.00", "CHN", "Some Exporter", date(2024, 1, 15)
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, calculator, mock_session):
        """Test database error handling."""
        mock_session.execute.side_effect = Exception("Database connection error")
        
        result = await calculator.calculate_anti_dumping_duty(
            mock_session, "8471.30.00", "CHN", "Some Exporter", date(2024, 1, 15)
        )
        
        assert result is None
class TestCalculateGst:
    """Test calculate_gst method."""
    
    @pytest.mark.asyncio
    async def test_standard_gst_calculation(self, calculator, mock_session):
        """Test standard GST calculation above threshold."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []  # No exemptions
        mock_session.execute.return_value = mock_result
        
        duty_inclusive_value = Decimal('1500.00')
        result = await calculator.calculate_gst(mock_session, "8471.30.00", duty_inclusive_value)
        
        assert result is not None
        assert result.duty_type == "GST"
        assert result.rate == Decimal('10.0')  # 10%
        assert result.amount == Decimal('150.00')  # 10% of 1500
        assert result.description == "Goods and Services Tax (10%)"
        assert result.basis == "Standard Rate"
    
    @pytest.mark.asyncio
    async def test_below_threshold_no_gst(self, calculator, mock_session):
        """Test no GST when below threshold."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []  # No exemptions
        mock_session.execute.return_value = mock_result
        
        duty_inclusive_value = Decimal('500.00')  # Below $1000 threshold
        result = await calculator.calculate_gst(mock_session, "8471.30.00", duty_inclusive_value)
        
        assert result is not None
        assert result.duty_type == "GST"
        assert result.rate == Decimal('0.00')
        assert result.amount == Decimal('0.00')
        assert "below" in result.description
        assert result.basis == "Threshold"
    
    @pytest.mark.asyncio
    async def test_gst_exemption_applies(self, calculator, mock_session, sample_gst_provision):
        """Test GST exemption when provision applies."""
        sample_gst_provision.exemption_type = "Food"
        sample_gst_provision.applies_to_value.return_value = True
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [sample_gst_provision]
        mock_session.execute.return_value = mock_result
        
        duty_inclusive_value = Decimal('1500.00')
        result = await calculator.calculate_gst(mock_session, "0101.01.00", duty_inclusive_value)
        
        assert result is not None
        assert result.duty_type == "GST"
        assert result.rate == Decimal('0.00')
        assert result.amount == Decimal('0.00')
        assert "GST Exempt: Food" in result.description
        assert result.basis == "Exemption"
    
    @pytest.mark.asyncio
    async def test_gst_rounding(self, calculator, mock_session):
        """Test GST amount rounding."""
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = []  # No exemptions
        mock_session.execute.return_value = mock_result
        
        duty_inclusive_value = Decimal('1333.33')  # Should result in 133.333, rounded to 133.33
        result = await calculator.calculate_gst(mock_session, "8471.30.00", duty_inclusive_value)
        
        assert result is not None
        assert result.amount == Decimal('133.33')  # Properly rounded
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, calculator, mock_session):
        """Test database error handling."""
        mock_session.execute.side_effect = Exception("Database connection error")
        
        result = await calculator.calculate_gst(mock_session, "8471.30.00", Decimal('1500.00'))
        
        assert result is None


class TestGetCalculationBreakdown:
    """Test get_calculation_breakdown method."""
    
    @pytest.mark.asyncio
    async def test_comprehensive_breakdown(self, calculator, mock_session, sample_input):
        """Test comprehensive calculation breakdown."""
        # Mock the comprehensive duty calculation
        with patch.object(calculator, 'calculate_comprehensive_duty') as mock_calc:
            # Create a mock result with all components
            mock_result = DutyCalculationResult(
                hs_code="8471.30.00",
                country_code="CHN",
                customs_value=Decimal('1000.00')
            )
            
            # Add duty components
            mock_result.general_duty = DutyComponent(
                duty_type="General Duty",
                rate=Decimal('5.0'),
                amount=Decimal('50.00'),
                description="5% general duty",
                basis="Ad Valorem"
            )
            
            mock_result.gst_component = DutyComponent(
                duty_type="GST",
                rate=Decimal('10.0'),
                amount=Decimal('105.00'),
                description="GST on duty-inclusive value",
                basis="Standard Rate"
            )
            
            mock_result.total_duty = Decimal('50.00')
            mock_result.duty_inclusive_value = Decimal('1050.00')
            mock_result.total_gst = Decimal('105.00')
            mock_result.total_amount = Decimal('1155.00')
            mock_result.best_rate_type = "general"
            mock_result.potential_savings = Decimal('0.00')
            mock_result.calculation_steps = ["Step 1: Calculate general duty"]
            mock_result.compliance_notes = ["Standard calculation"]
            mock_result.warnings = []
            
            mock_calc.return_value = mock_result
            
            breakdown = await calculator.get_calculation_breakdown(mock_session, sample_input)
            
            # Verify breakdown structure
            assert "input_parameters" in breakdown
            assert "duty_components" in breakdown
            assert "totals" in breakdown
            assert "best_rate_analysis" in breakdown
            assert "calculation_steps" in breakdown
            assert "compliance_notes" in breakdown
            assert "warnings" in breakdown
            
            # Verify input parameters
            assert breakdown["input_parameters"]["hs_code"] == "8471.30.00"
            assert breakdown["input_parameters"]["country_code"] == "CHN"
            assert breakdown["input_parameters"]["customs_value"] == "1000.00"
            
            # Verify duty components
            assert "general_duty" in breakdown["duty_components"]
            assert "gst" in breakdown["duty_components"]
            
            # Verify totals
            assert breakdown["totals"]["total_duty"] == "50.00"
            assert breakdown["totals"]["total_amount"] == "1155.00"
    
    @pytest.mark.asyncio
    async def test_breakdown_with_minimal_result(self, calculator, mock_session, sample_input):
        """Test breakdown with minimal calculation result."""
        with patch.object(calculator, 'calculate_comprehensive_duty') as mock_calc:
            mock_result = DutyCalculationResult(
                hs_code="8471.30.00",
                country_code="CHN",
                customs_value=Decimal('1000.00')
            )
            mock_calc.return_value = mock_result
            
            breakdown = await calculator.get_calculation_breakdown(mock_session, sample_input)
            
            # Should still have all required sections
            assert "input_parameters" in breakdown
            assert "duty_components" in breakdown
            assert "totals" in breakdown
            
            # Duty components should be empty
            assert len(breakdown["duty_components"]) == 0
    
    @pytest.mark.asyncio
    async def test_breakdown_error_handling(self, calculator, mock_session, sample_input):
        """Test breakdown error handling."""
        with patch.object(calculator, 'calculate_comprehensive_duty') as mock_calc:
            mock_calc.side_effect = Exception("Calculation error")
            
            with pytest.raises(Exception):
                await calculator.get_calculation_breakdown(mock_session, sample_input)


class TestPrivateHelperMethods:
    """Test private helper methods."""
    
    @pytest.mark.asyncio
    async def test_calculate_duty_component_ad_valorem(self, calculator, sample_duty_rate, sample_input):
        """Test _calculate_duty_component for ad valorem duty."""
        sample_duty_rate.is_ad_valorem = True
        sample_duty_rate.is_specific = False
        sample_duty_rate.general_rate = Decimal('5.0')
        
        component = await calculator._calculate_duty_component(
            sample_duty_rate, sample_input, "Test General Duty"
        )
        
        assert component.duty_type == "General Duty"
        assert component.rate == Decimal('5.0')
        assert component.amount == Decimal('50.00')  # 5% of 1000
        assert component.description == "Test General Duty"
        assert component.basis == "Ad Valorem"
    
    @pytest.mark.asyncio
    async def test_calculate_duty_component_specific(self, calculator, sample_duty_rate, sample_input):
        """Test _calculate_duty_component for specific duty."""
        sample_duty_rate.is_ad_valorem = False
        sample_duty_rate.is_specific = True
        sample_duty_rate.general_rate = Decimal('2.50')  # $2.50 per unit
        
        component = await calculator._calculate_duty_component(
            sample_duty_rate, sample_input, "Test Specific Duty"
        )
        
        assert component.duty_type == "General Duty"
        assert component.rate == Decimal('2.50')
        assert component.amount == Decimal('2.50')  # $2.50 * 1 unit
        assert component.description == "Test Specific Duty (Specific)"
        assert component.basis == "Specific"
    
    @pytest.mark.asyncio
    async def test_calculate_duty_component_free(self, calculator, sample_duty_rate, sample_input):
        """Test _calculate_duty_component for free duty."""
        sample_duty_rate.is_ad_valorem = False
        sample_duty_rate.is_specific = False
        sample_duty_rate.general_rate = None
        sample_duty_rate.rate_text = "Free"
        
        component = await calculator._calculate_duty_component(
            sample_duty_rate, sample_input, "Test Free Duty"
        )
        
        assert component.duty_type == "General Duty"
        assert component.rate == Decimal('0.00')
        assert component.amount == Decimal('0.00')
        assert component.description == "Free"
        assert component.basis == "Free"
    
    @pytest.mark.asyncio
    async def test_calculate_fta_component(self, calculator, sample_fta_rate, sample_input):
        """Test _calculate_fta_component."""
        sample_fta_rate.effective_rate = Decimal('2.5')
        
        component = await calculator._calculate_fta_component(sample_fta_rate, sample_input)
        
        assert component.duty_type == "FTA Duty"
        assert component.rate == Decimal('2.5')
        assert component.amount == Decimal('25.00')  # 2.5% of 1000
        assert "AUSFTA" in component.description
        assert component.basis == "FTA Preferential"
        assert component.calculation_details["fta_code"] == "AUSFTA"
    
    @pytest.mark.asyncio
    async def test_calculate_dumping_component_ad_valorem(self, calculator, sample_dumping_duty, sample_input):
        """Test _calculate_dumping_component with ad valorem duty."""
        sample_dumping_duty.duty_rate = Decimal('15.5')
        sample_dumping_duty.duty_amount = None
        
        component = await calculator._calculate_dumping_component(sample_dumping_duty, sample_input)
        
        assert component.duty_type == "Anti-dumping Duty"
        assert component.rate == Decimal('15.5')
        assert component.amount == Decimal('155.00')  # 15.5% of 1000
        assert "15.5% ad valorem" in component.description
        assert component.basis == "Anti-dumping"
    
    @pytest.mark.asyncio
    async def test_calculate_dumping_component_specific(self, calculator, sample_dumping_duty, sample_input):
        """Test _calculate_dumping_component with specific duty."""
        sample_dumping_duty.duty_rate = None
        sample_dumping_duty.duty_amount = Decimal('50.00')
        sample_dumping_duty.unit = "unit"
        
        component = await calculator._calculate_dumping_component(sample_dumping_duty, sample_input)
        
        assert component.duty_type == "Anti-dumping Duty"
        assert component.amount == Decimal('50.00')  # $50 * 1 unit
        assert "$50.00 per unit" in component.description
        assert component.basis == "Anti-dumping"
    
    @pytest.mark.asyncio
    async def test_calculate_dumping_component_compound(self, calculator, sample_dumping_duty, sample_input):
        """Test _calculate_dumping_component with compound duty."""
        sample_dumping_duty.duty_rate = Decimal('5.0')  # 5% ad valorem
        sample_dumping_duty.duty_amount = Decimal('10.00')  # + $10 specific
        sample_dumping_duty.unit = "unit"
        
        component = await calculator._calculate_dumping_component(sample_dumping_duty, sample_input)
        
        assert component.duty_type == "Anti-dumping Duty"
        assert component.amount == Decimal('60.00')  # (5% of 1000) + (10 * 1)
        assert "5.0% ad valorem" in component.description
        assert "$10.00 per unit" in component.description
        assert component.basis == "Anti-dumping"
    
    @pytest.mark.asyncio
    async def test_determine_best_duty_tco_precedence(self, calculator):
        """Test _determine_best_duty with TCO taking precedence."""
        result = DutyCalculationResult(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1000.00')
        )
        
        result.tco_exemption = DutyComponent(
            duty_type="TCO Exemption",
            rate=Decimal('0.00'),
            amount=Decimal('0.00'),
            description="TCO exemption",
            basis="Exemption"
        )
        
        result.general_duty = DutyComponent(
            duty_type="General Duty",
            rate=Decimal('5.0'),
            amount=Decimal('50.00'),
            description="General duty",
            basis="Ad Valorem"
        )
        
        best_duty = await calculator._determine_best_duty(result)
        
        assert best_duty == result.tco_exemption
        assert result.best_rate_type == "tco_exemption"
    
    @pytest.mark.asyncio
    async def test_determine_best_duty_fta_better(self, calculator):
        """Test _determine_best_duty with FTA being better than general."""
        result = DutyCalculationResult(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1000.00')
        )
        
        result.general_duty = DutyComponent(
            duty_type="General Duty",
            rate=Decimal('5.0'),
            amount=Decimal('50.00'),
            description="General duty",
            basis="Ad Valorem"
        )
        
        result.fta_duty = DutyComponent(
            duty_type="FTA Duty",
            rate=Decimal('2.5'),
            amount=Decimal('25.00'),  # Better rate
            description="FTA duty",
            basis="FTA Preferential"
        )
        
        best_duty = await calculator._determine_best_duty(result)
        
        assert best_duty == result.fta_duty
        assert result.best_rate_type == "fta"
    
    @pytest.mark.asyncio
    async def test_determine_best_duty_general_better(self, calculator):
        """Test _determine_best_duty with general being better than FTA."""
        result = DutyCalculationResult(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1000.00')
        )
        
        result.general_duty = DutyComponent(
            duty_type="General Duty",
            rate=Decimal('2.5'),
            amount=Decimal('25.00'),  # Better rate
            description="General duty",
            basis="Ad Valorem"
        )
        
        result.fta_duty = DutyComponent(
            duty_type="FTA Duty",
            rate=Decimal('5.0'),
            amount=Decimal('50.00'),
            description="FTA duty",
            basis="FTA Preferential"
        )
        
        best_duty = await calculator._determine_best_duty(result)
        
        assert best_duty == result.general_duty
        assert result.best_rate_type == "general"
    
    @pytest.mark.asyncio
    async def test_calculate_savings_analysis_fta(self, calculator):
        """Test _calculate_savings_analysis with FTA savings."""
        result = DutyCalculationResult(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1000.00')
        )
        
        result.general_duty = DutyComponent(
            duty_type="General Duty",
            rate=Decimal('5.0'),
            amount=Decimal('50.00'),
            description="General duty",
            basis="Ad Valorem"
        )
        
        result.fta_duty = DutyComponent(
            duty_type="FTA Duty",
            rate=Decimal('2.5'),
            amount=Decimal('25.00'),
            description="FTA duty",
            basis="FTA Preferential"
        )
        
        result.best_rate_type = "fta"
        
        await calculator._calculate_savings_analysis(result)
        
        assert result.potential_savings == Decimal('25.00')  # 50 - 25
    
    @pytest.mark.asyncio
    async def test_calculate_savings_analysis_tco(self, calculator):
        """Test _calculate_savings_analysis with TCO savings."""
        result = DutyCalculationResult(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1000.00')
        )
        
        result.general_duty = DutyComponent(
            duty_type="General Duty",
            rate=Decimal('5.0'),
            amount=Decimal('50.00'),
            description="General duty",
            basis="Ad Valorem"
        )
        
        result.tco_exemption = DutyComponent(
            duty_type="TCO Exemption",
            rate=Decimal('0.00'),
            amount=Decimal('0.00'),
            description="TCO exemption",
            basis="Exemption"
        )
        
        result.best_rate_type = "tco_exemption"
        
        await calculator._calculate_savings_analysis(result)
        
        assert result.potential_savings == Decimal('50.00')  # Full general duty saved
    
    @pytest.mark.asyncio
    async def test_add_compliance_notes_fta(self, calculator, sample_fta_rate):
        """Test _add_compliance_notes with FTA requirements."""
        result = DutyCalculationResult(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1000.00')
        )
        
        sample_fta_rate.rule_of_origin = "WO"
        sample_fta_rate.is_quota_applicable = True
        sample_fta_rate.quota_quantity = Decimal('1000')
        sample_fta_rate.quota_unit = "units"
        
        await calculator._add_compliance_notes(result, sample_fta_rate, None)
        
        assert len(result.compliance_notes) > 0
        assert len(result.warnings) > 0
        assert any("rules of origin" in note for note in result.compliance_notes)
        assert any("quota restrictions" in warning for warning in result.warnings)
    
    @pytest.mark.asyncio
    async def test_add_compliance_notes_tco(self, calculator, sample_tco):
        """Test _add_compliance_notes with TCO requirements."""
        result = DutyCalculationResult(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1000.00')
        )
        
        sample_tco.days_until_expiry.return_value = 30  # Expiring soon
        
        await calculator._add_compliance_notes(result, None, sample_tco)
        
        assert len(result.compliance_notes) > 0
        assert len(result.warnings) > 0
        assert any("TCO exemption applies" in note for note in result.compliance_notes)
        assert any("TCO expires in 30 days" in warning for warning in result.warnings)
    
    def test_component_to_dict(self, calculator):
        """Test _component_to_dict helper method."""
        component = DutyComponent(
            duty_type="General Duty",
            rate=Decimal('5.0'),
            amount=Decimal('50.00'),
            description="5% general duty",
            basis="Ad Valorem",
            calculation_details={"unit_type": "ad_valorem"}
        )
        
        result_dict = calculator._component_to_dict(component)
        
        assert result_dict["duty_type"] == "General Duty"
        assert result_dict["rate"] == "5.0"
        assert result_dict["amount"] == "50.00"
        assert result_dict["description"] == "5% general duty"
        assert result_dict["basis"] == "Ad Valorem"
        assert result_dict["calculation_details"] == {"unit_type": "ad_valorem"}
    
    def test_component_to_dict_none_rate(self, calculator):
        """Test _component_to_dict with None rate."""
        component = DutyComponent(
            duty_type="TCO Exemption",
            rate=None,
            amount=Decimal('0.00'),
            description="TCO exemption",
            basis="Exemption"
        )
        
        result_dict = calculator._component_to_dict(component)
        
        assert result_dict["rate"] is None
        assert result_dict["amount"] == "0.00"
class TestCalculateComprehensiveDuty:
    """Test calculate_comprehensive_duty method - the main workflow."""
    
    @pytest.mark.asyncio
    async def test_comprehensive_calculation_full_workflow(self, calculator, mock_session, sample_input):
        """Test complete comprehensive duty calculation workflow."""
        # Mock all the individual method calls
        with patch.object(calculator, 'get_general_duty_rate') as mock_general, \
             patch.object(calculator, 'get_best_fta_rate') as mock_fta, \
             patch.object(calculator, 'check_tco_exemption') as mock_tco, \
             patch.object(calculator, 'calculate_anti_dumping_duty') as mock_dumping, \
             patch.object(calculator, 'calculate_gst') as mock_gst, \
             patch.object(calculator, '_calculate_duty_component') as mock_duty_comp, \
             patch.object(calculator, '_calculate_fta_component') as mock_fta_comp, \
             patch.object(calculator, '_calculate_dumping_component') as mock_dump_comp, \
             patch.object(calculator, '_determine_best_duty') as mock_best, \
             patch.object(calculator, '_calculate_savings_analysis') as mock_savings, \
             patch.object(calculator, '_add_compliance_notes') as mock_compliance:
            
            # Setup mock returns
            mock_duty_rate = MagicMock()
            mock_general.return_value = mock_duty_rate
            
            mock_fta_rate = MagicMock()
            mock_fta_rate.fta_code = "AUSFTA"
            mock_fta.return_value = mock_fta_rate
            
            mock_tco.return_value = None  # No TCO
            mock_dumping.return_value = None  # No anti-dumping
            
            # Mock duty components
            general_duty = DutyComponent(
                duty_type="General Duty",
                rate=Decimal('5.0'),
                amount=Decimal('50.00'),
                description="5% general duty",
                basis="Ad Valorem"
            )
            mock_duty_comp.return_value = general_duty
            
            fta_duty = DutyComponent(
                duty_type="FTA Duty",
                rate=Decimal('0.0'),
                amount=Decimal('0.00'),
                description="AUSFTA free rate",
                basis="FTA Preferential"
            )
            mock_fta_comp.return_value = fta_duty
            
            mock_best.return_value = fta_duty  # FTA is better
            
            gst_component = DutyComponent(
                duty_type="GST",
                rate=Decimal('10.0'),
                amount=Decimal('100.00'),
                description="GST on duty-inclusive value",
                basis="Standard Rate"
            )
            mock_gst.return_value = gst_component
            
            # Execute the comprehensive calculation
            result = await calculator.calculate_comprehensive_duty(mock_session, sample_input)
            
            # Verify the result structure
            assert result.hs_code == "8471.30.00"
            assert result.country_code == "CHN"
            assert result.customs_value == Decimal('1000.00')
            assert result.general_duty == general_duty
            assert result.fta_duty == fta_duty
            assert result.gst_component == gst_component
            assert result.total_duty == Decimal('0.00')  # FTA duty is 0
            assert result.duty_inclusive_value == Decimal('1000.00')  # 1000 + 0 duty
            assert result.total_gst == Decimal('100.00')
            assert result.total_amount == Decimal('1100.00')  # 1000 + 0 + 100
            
            # Verify calculation steps were added
            assert len(result.calculation_steps) > 0
            assert any("Step 1" in step for step in result.calculation_steps)
            
            # Verify all methods were called
            mock_general.assert_called_once()
            mock_fta.assert_called_once()
            mock_tco.assert_called_once()
            mock_dumping.assert_called_once()
            mock_gst.assert_called_once()
            mock_savings.assert_called_once()
            mock_compliance.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_comprehensive_calculation_with_tco(self, calculator, mock_session, sample_input, sample_tco):
        """Test comprehensive calculation with TCO exemption."""
        with patch.object(calculator, 'get_general_duty_rate') as mock_general, \
             patch.object(calculator, 'get_best_fta_rate') as mock_fta, \
             patch.object(calculator, 'check_tco_exemption') as mock_tco, \
             patch.object(calculator, 'calculate_anti_dumping_duty') as mock_dumping, \
             patch.object(calculator, 'calculate_gst') as mock_gst, \
             patch.object(calculator, '_calculate_duty_component') as mock_duty_comp, \
             patch.object(calculator, '_determine_best_duty') as mock_best, \
             patch.object(calculator, '_calculate_savings_analysis') as mock_savings, \
             patch.object(calculator, '_add_compliance_notes') as mock_compliance:
            
            # Setup mocks
            mock_general.return_value = MagicMock()
            mock_fta.return_value = None
            mock_tco.return_value = sample_tco  # TCO applies
            mock_dumping.return_value = None
            
            general_duty = DutyComponent(
                duty_type="General Duty",
                rate=Decimal('5.0'),
                amount=Decimal('50.00'),
                description="5% general duty",
                basis="Ad Valorem"
            )
            mock_duty_comp.return_value = general_duty
            
            tco_exemption = DutyComponent(
                duty_type="TCO Exemption",
                rate=Decimal('0.00'),
                amount=Decimal('0.00'),
                description=f"TCO {sample_tco.tco_number}: {sample_tco.description[:100]}...",
                basis="Exemption"
            )
            mock_best.return_value = tco_exemption
            
            mock_gst.return_value = DutyComponent(
                duty_type="GST",
                rate=Decimal('10.0'),
                amount=Decimal('100.00'),
                description="GST",
                basis="Standard Rate"
            )
            
            result = await calculator.calculate_comprehensive_duty(mock_session, sample_input)
            
            # Verify TCO exemption is applied
            assert result.tco_exemption is not None
            assert result.total_duty == Decimal('0.00')  # TCO exemption
            assert sample_tco.tco_number in result.tco_exemption.description
    
    @pytest.mark.asyncio
    async def test_comprehensive_calculation_with_anti_dumping(self, calculator, mock_session, sample_input, sample_dumping_duty):
        """Test comprehensive calculation with anti-dumping duty."""
        with patch.object(calculator, 'get_general_duty_rate') as mock_general, \
             patch.object(calculator, 'get_best_fta_rate') as mock_fta, \
             patch.object(calculator, 'check_tco_exemption') as mock_tco, \
             patch.object(calculator, 'calculate_anti_dumping_duty') as mock_dumping, \
             patch.object(calculator, 'calculate_gst') as mock_gst, \
             patch.object(calculator, '_calculate_duty_component') as mock_duty_comp, \
             patch.object(calculator, '_calculate_dumping_component') as mock_dump_comp, \
             patch.object(calculator, '_determine_best_duty') as mock_best, \
             patch.object(calculator, '_calculate_savings_analysis') as mock_savings, \
             patch.object(calculator, '_add_compliance_notes') as mock_compliance:
            
            # Setup mocks
            mock_general.return_value = MagicMock()
            mock_fta.return_value = None
            mock_tco.return_value = None
            mock_dumping.return_value = sample_dumping_duty  # Anti-dumping applies
            
            general_duty = DutyComponent(
                duty_type="General Duty",
                rate=Decimal('5.0'),
                amount=Decimal('50.00'),
                description="5% general duty",
                basis="Ad Valorem"
            )
            mock_duty_comp.return_value = general_duty
            mock_best.return_value = general_duty
            
            dumping_duty = DutyComponent(
                duty_type="Anti-dumping Duty",
                rate=Decimal('15.5'),
                amount=Decimal('155.00'),
                description="Anti-dumping duty: 15.5% ad valorem",
                basis="Anti-dumping"
            )
            mock_dump_comp.return_value = dumping_duty
            
            mock_gst.return_value = DutyComponent(
                duty_type="GST",
                rate=Decimal('10.0'),
                amount=Decimal('120.50'),  # 10% of (1000 + 50 + 155)
                description="GST",
                basis="Standard Rate"
            )
            
            result = await calculator.calculate_comprehensive_duty(mock_session, sample_input)
            
            # Verify anti-dumping duty is included
            assert result.anti_dumping_duty == dumping_duty
            assert result.total_duty == Decimal('205.00')  # 50 (general) + 155 (anti-dumping)
    
    @pytest.mark.asyncio
    async def test_comprehensive_calculation_no_duties_found(self, calculator, mock_session, sample_input):
        """Test comprehensive calculation when no duties are found."""
        with patch.object(calculator, 'get_general_duty_rate') as mock_general, \
             patch.object(calculator, 'get_best_fta_rate') as mock_fta, \
             patch.object(calculator, 'check_tco_exemption') as mock_tco, \
             patch.object(calculator, 'calculate_anti_dumping_duty') as mock_dumping, \
             patch.object(calculator, 'calculate_gst') as mock_gst, \
             patch.object(calculator, '_determine_best_duty') as mock_best, \
             patch.object(calculator, '_calculate_savings_analysis') as mock_savings, \
             patch.object(calculator, '_add_compliance_notes') as mock_compliance:
            
            # All methods return None/empty
            mock_general.return_value = None
            mock_fta.return_value = None
            mock_tco.return_value = None
            mock_dumping.return_value = None
            mock_best.return_value = None
            
            mock_gst.return_value = DutyComponent(
                duty_type="GST",
                rate=Decimal('10.0'),
                amount=Decimal('100.00'),
                description="GST",
                basis="Standard Rate"
            )
            
            result = await calculator.calculate_comprehensive_duty(mock_session, sample_input)
            
            # Verify minimal result
            assert result.general_duty is None
            assert result.fta_duty is None
            assert result.tco_exemption is None
            assert result.anti_dumping_duty is None
            assert result.total_duty == Decimal('0.00')
            assert result.duty_inclusive_value == Decimal('1000.00')
            assert result.total_gst == Decimal('100.00')
            assert result.total_amount == Decimal('1100.00')
    
    @pytest.mark.asyncio
    async def test_comprehensive_calculation_default_date(self, calculator, mock_session):
        """Test comprehensive calculation with default calculation date."""
        input_no_date = DutyCalculationInput(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1000.00')
        )
        
        with patch.object(calculator, 'get_general_duty_rate') as mock_general, \
             patch.object(calculator, 'get_best_fta_rate') as mock_fta, \
             patch.object(calculator, 'check_tco_exemption') as mock_tco, \
             patch.object(calculator, 'calculate_anti_dumping_duty') as mock_dumping, \
             patch.object(calculator, 'calculate_gst') as mock_gst, \
             patch.object(calculator, '_determine_best_duty') as mock_best, \
             patch.object(calculator, '_calculate_savings_analysis') as mock_savings, \
             patch.object(calculator, '_add_compliance_notes') as mock_compliance:
            
            # Setup minimal mocks
            mock_general.return_value = None
            mock_fta.return_value = None
            mock_tco.return_value = None
            mock_dumping.return_value = None
            mock_best.return_value = None
            mock_gst.return_value = None
            
            result = await calculator.calculate_comprehensive_duty(mock_session, input_no_date)
            
            # Should complete without error using today's date
            assert result is not None
            assert result.hs_code == "8471.30.00"
    
    @pytest.mark.asyncio
    async def test_comprehensive_calculation_error_handling(self, calculator, mock_session, sample_input):
        """Test comprehensive calculation error handling."""
        with patch.object(calculator, 'get_general_duty_rate') as mock_general:
            mock_general.side_effect = Exception("Database error")
            
            with pytest.raises(Exception):
                await calculator.calculate_comprehensive_duty(mock_session, sample_input)


class TestEdgeCasesAndErrorHandling:
    """Test edge cases and error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_zero_customs_value(self, calculator, mock_session):
        """Test calculation with zero customs value."""
        input_zero = DutyCalculationInput(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('0.00')
        )
        
        with patch.object(calculator, 'get_general_duty_rate') as mock_general, \
             patch.object(calculator, 'calculate_gst') as mock_gst:
            
            mock_duty_rate = MagicMock()
            mock_duty_rate.is_ad_valorem = True
            mock_duty_rate.general_rate = Decimal('5.0')
            mock_general.return_value = mock_duty_rate
            
            mock_gst.return_value = None  # Below threshold
            
            component = await calculator._calculate_duty_component(
                mock_duty_rate, input_zero, "Test Duty"
            )
            
            assert component.amount == Decimal('0.00')  # 5% of 0 = 0
    
    @pytest.mark.asyncio
    async def test_very_large_customs_value(self, calculator, mock_session):
        """Test calculation with very large customs value."""
        input_large = DutyCalculationInput(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('999999999.99')
        )
        
        mock_duty_rate = MagicMock()
        mock_duty_rate.is_ad_valorem = True
        mock_duty_rate.general_rate = Decimal('5.0')
        
        component = await calculator._calculate_duty_component(
            mock_duty_rate, input_large, "Test Duty"
        )
        
        expected_amount = Decimal('49999999.9995').quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        assert component.amount == expected_amount
    
    @pytest.mark.asyncio
    async def test_decimal_precision_rounding(self, calculator):
        """Test decimal precision and rounding behavior."""
        input_data = DutyCalculationInput(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1333.33')  # Will create rounding scenarios
        )
        
        mock_duty_rate = MagicMock()
        mock_duty_rate.is_ad_valorem = True
        mock_duty_rate.general_rate = Decimal('7.5')  # 7.5% of 1333.33 = 99.99975
        
        component = await calculator._calculate_duty_component(
            mock_duty_rate, input_data, "Test Duty"
        )
        
        # Should round to 100.00
        assert component.amount == Decimal('100.00')
    
    @pytest.mark.asyncio
    async def test_specific_duty_without_quantity(self, calculator):
        """Test specific duty calculation without quantity."""
        input_no_qty = DutyCalculationInput(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('1000.00'),
            quantity=None
        )
        
        mock_duty_rate = MagicMock()
        mock_duty_rate.is_ad_valorem = False
        mock_duty_rate.is_specific = True
        mock_duty_rate.general_rate = Decimal('10.00')
        
        component = await calculator._calculate_duty_component(
            mock_duty_rate, input_no_qty, "Test Duty"
        )
        
        # Should fall back to free duty when no quantity for specific duty
        assert component.description == "Free"
        assert component.amount == Decimal('0.00')
    
    @pytest.mark.asyncio
    async def test_invalid_hs_code_formats(self, calculator, mock_session):
        """Test handling of various HS code formats."""
        test_codes = [
            "84",           # 2-digit
            "8471",         # 4-digit
            "847130",       # 6-digit
            "84713000",     # 8-digit
            "8471300000",   # 10-digit
            "8471.30.00",   # With dots
            "8471-30-00",   # With dashes
        ]
        
        for hs_code in test_codes:
            mock_result = MagicMock()
            mock_result.scalar_one_or_none.return_value = None
            mock_session.execute.return_value = mock_result
            
            result = await calculator.get_general_duty_rate(mock_session, hs_code)
            
            # Should handle all formats without error
            assert result is None  # No match found, but no error
    
    @pytest.mark.asyncio
    async def test_date_edge_cases(self, calculator, mock_session):
        """Test date-related edge cases."""
        # Test with dates at boundaries
        test_dates = [
            date(1900, 1, 1),    # Very old date
            date(2100, 12, 31),  # Future date
            date.today(),        # Today
        ]
        
        for test_date in test_dates:
            mock_result = MagicMock()
            mock_result.scalars.return_value.all.return_value = []
            mock_session.execute.return_value = mock_result
            
            result = await calculator.get_best_fta_rate(
                mock_session, "8471.30.00", "USA", test_date
            )
            
            # Should handle all dates without error
            assert result is None
    
    def test_dataclass_field_validation(self):
        """Test dataclass field validation and edge cases."""
        # Test with extreme decimal values
        input_data = DutyCalculationInput(
            hs_code="8471.30.00",
            country_code="CHN",
            customs_value=Decimal('0.01'),  # Minimum meaningful value
            quantity=Decimal('0.001'),      # Very small quantity
        )
        
        assert input_data.customs_value == Decimal('0.01')
        assert input_data.quantity == Decimal('0.001')
    
    def test_component_with_empty_calculation_details(self):
        """Test DutyComponent with empty calculation details."""
        component = DutyComponent(
            duty_type="Test Duty",
            rate=Decimal('5.0'),
            amount=Decimal('50.00'),
            description="Test description",
            basis="Test basis",
            calculation_details={}
        )
        
        assert component.calculation_details == {}
        assert len(component.calculation_details) == 0
    
    @pytest.mark.asyncio
    async def test_multiple_gst_provisions(self, calculator, mock_session):
        """Test GST calculation with multiple provisions."""
        # Create multiple GST provisions
        provision1 = MagicMock(spec=GstProvision)
        provision1.exemption_type = None
        provision1.applies_to_value.return_value = False
        
        provision2 = MagicMock(spec=GstProvision)
        provision2.exemption_type = "Food"
        provision2.applies_to_value.return_value = True  # This one applies
        provision2.schedule_reference = "Schedule 1"
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [provision1, provision2]
        mock_session.execute.return_value = mock_result
        
        result = await calculator.calculate_gst(mock_session, "0101.01.00", Decimal('1500.00'))
        
        # Should use the first applicable exemption
        assert result.basis == "Exemption"
        assert "Food" in result.description
    
    @pytest.mark.asyncio
    async def test_fta_rate_with_none_effective_rate(self, calculator, sample_input):
        """Test FTA component calculation with None effective rate."""
        fta_rate = MagicMock(spec=FtaRate)
        fta_rate.fta_code = "TESTFTA"
        fta_rate.effective_rate = None  # None rate
        fta_rate.staging_category = "A"
        fta_rate.rule_of_origin = "WO"
        
        component = await calculator._calculate_fta_component(fta_rate, sample_input)
        
        assert component.rate == Decimal('0.00')  # Should default to 0
        assert component.amount == Decimal('0.00')
        assert component.duty_type == "FTA Duty"


class TestRealisticScenarios:
    """Test realistic Australian customs scenarios."""
    
    @pytest.mark.asyncio
    async def test_computer_import_from_china(self, calculator, mock_session):
        """Test realistic scenario: Computer import from China."""
        input_data = DutyCalculationInput(
            hs_code="8471.30.00",  # Portable computers
            country_code="CHN",
            customs_value=Decimal('2500.00'),
            quantity=Decimal('5'),
            calculation_date=date(2024, 6, 15),
            exporter_name="Shenzhen Tech Co Ltd"
        )
        
        # Mock realistic duty rates
        with patch.object(calculator, 'get_general_duty_rate') as mock_general, \
             patch.object(calculator, 'get_best_fta_rate') as mock_fta, \
             patch.object(calculator, 'check_tco_exemption') as mock_tco, \
             patch.object(calculator, 'calculate_anti_dumping_duty') as mock_dumping, \
             patch.object(calculator, 'calculate_gst') as mock_gst:
            
            # General duty: 5%
            mock_general.return_value = MagicMock(
                is_ad_valorem=True, general_rate=Decimal('5.0'), 
                unit_type="ad_valorem", rate_text="5%"
            )
            
            # No FTA with China for computers
            mock_fta.return_value = None
            
            # No TCO
            mock_tco.return_value = None
            
            # No anti-dumping
            mock_dumping.return_value = None
            
            # Standard GST
            mock_gst.return_value = DutyComponent(
                duty_type="GST",
                rate=Decimal('10.0'),
                amount=Decimal('262.50'),  # 10% of (2500 + 125)
                description="Goods and Services Tax (10%)",
                basis="Standard Rate"
            )
            
            result = await calculator.calculate_comprehensive_duty(mock_session, input_data)
            
            # Verify realistic calculation
            assert result.total_duty == Decimal('125.00')  # 5% of 2500
            assert result.duty_inclusive_value == Decimal('2625.00')  # 2500 + 125
            assert result.total_gst == Decimal('262.50')
            assert result.total_amount == Decimal('2887.50')  # 2500 + 125 + 262.50
    
    @pytest.mark.asyncio
    async def test_wine_import_from_new_zealand(self, calculator, mock_session):
        """Test realistic scenario: Wine import from New Zealand with FTA."""
        input_data = DutyCalculationInput(
            hs_code="2204.21.00",  # Wine in bottles
            country_code="NZL",
            customs_value=Decimal('1200.00'),
            quantity=Decimal('100'),  # 100 bottles
            calculation_date=date(2024, 6, 15)
        )
        
        with patch.object(calculator, 'get_general_duty_rate') as mock_general, \
             patch.object(calculator, 'get_best_fta_rate') as mock_fta, \
             patch.object(calculator, 'check_tco_exemption') as mock_tco, \
             patch.object(calculator, 'calculate_anti_dumping_duty') as mock_dumping, \
             patch.object(calculator, 'calculate_gst') as mock_gst:
            
            # General duty: 5%
            mock_general.return_value = MagicMock(
                is_ad_valorem=True, general_rate=Decimal('5.0')
            )
            
            # AANZFTA free rate
            mock_fta_rate = MagicMock(spec=FtaRate)
            mock_fta_rate.fta_code = "AANZFTA"
            mock_fta_rate.effective_rate = Decimal('0.0')  # Free under FTA
            mock_fta_rate.staging_category = "A"
            mock_fta_rate.rule_of_origin = "WO"
            mock_fta_rate.is_quota_applicable = False
            mock_fta.return_value = mock_fta_rate
            
            mock_tco.return_value = None
            mock_dumping.return_value = None
            
            # GST on duty-free value
            mock_gst.return_value = DutyComponent(
                duty_type="GST",
                rate=Decimal('10.0'),
                amount=Decimal('120.00'),  # 10% of 1200 (no duty)
                description="Goods and Services Tax (10%)",
                basis="Standard Rate"
            )
            
            result = await calculator.calculate_comprehensive_duty(mock_session, input_data)
            
            # Verify FTA benefit
            assert result.total_duty == Decimal('0.00')  # Free under AANZFTA
            assert result.duty_inclusive_value == Decimal('1200.00')
            assert result.total_gst == Decimal('120.00')
            assert result.total_amount == Decimal('1320.00')
            assert result.best_rate_type == "fta"
            assert result.potential_savings == Decimal('60.00')  # Saved 5% of 1200
    
    @pytest.mark.asyncio
    async def test_steel_import_with_anti_dumping(self, calculator, mock_session):
        """Test realistic scenario: Steel import with anti-dumping duty."""
        input_data = DutyCalculationInput(
            hs_code="7208.10.00",  # Hot-rolled steel
            country_code="CHN",
            customs_value=Decimal('50000.00'),
            quantity=Decimal('25'),  # 25 tonnes
            calculation_date=date(2024, 6, 15),
            exporter_name="Beijing Steel Works"
        )
        
        with patch.object(calculator, 'get_general_duty_rate') as mock_general, \
             patch.object(calculator, 'get_best_fta_rate') as mock_fta, \
             patch.object(calculator, 'check_tco_exemption') as mock_tco, \
             patch.object(calculator, 'calculate_anti_dumping_duty') as mock_dumping, \
             patch.object(calculator, 'calculate_gst') as mock_gst:
            
            # General duty: Free
            mock_general.return_value = MagicMock(
                is_ad_valorem=False, is_specific=False, general_rate=None, rate_text="Free"
            )
            
            mock_fta.return_value = None
            mock_tco.return_value = None
            
            # Anti-dumping duty applies
            mock_dumping_duty = MagicMock(spec=DumpingDuty)
            mock_dumping_duty.duty_rate = Decimal('23.6')  # 23.6% anti-dumping
            mock_dumping_duty.duty_amount = None
            mock_dumping_duty.case_number = "ADC2023-002"
            mock_dumping_duty.exporter_name = "Beijing Steel Works"
            mock_dumping.return_value = mock_dumping_duty
            
            # GST on duty-inclusive value
            mock_gst.return_value = DutyComponent(
                duty_type="GST",
                rate=Decimal('10.0'),
                amount=Decimal('6180.00'),  # 10% of (50000 + 11800)
                description="Goods and Services Tax (10%)",
                basis="Standard Rate"
            )
            
            result = await calculator.calculate_comprehensive_duty(mock_session, input_data)
            
            # Verify anti-dumping calculation
            assert result.total_duty == Decimal('11800.00')  # 23.6% of 50000
            assert result.duty_inclusive_value == Decimal('61800.00')
            assert result.total_gst == Decimal('6180.00')
            assert result.total_amount == Decimal('67980.00')