"""
Unit tests for specialized models: DumpingDuty, Tco, and GstProvision.

This module tests the specialized duty and provision models including validation,
relationships, business logic, and date-based functionality.
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models import DumpingDuty, Tco, GstProvision, TariffCode
from tests.utils.test_helpers import TestDataFactory, DatabaseTestHelper


@pytest.mark.database
@pytest.mark.unit
class TestDumpingDuty:
    """Test cases for DumpingDuty model."""

    async def test_create_dumping_duty(self, test_session):
        """Test creating a basic dumping duty."""
        # Create tariff code first
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        data = TestDataFactory.create_dumping_duty_data(
            hs_code="0101010000",
            country_code="CHN",
            duty_type="dumping",
            duty_rate=Decimal("25.50"),
            case_number="ADC2023-001"
        )
        
        dumping_duty = DumpingDuty(**data)
        test_session.add(dumping_duty)
        await test_session.commit()
        await test_session.refresh(dumping_duty)
        
        assert dumping_duty.id is not None
        assert dumping_duty.hs_code == "0101010000"
        assert dumping_duty.country_code == "CHN"
        assert dumping_duty.duty_type == "dumping"
        assert dumping_duty.duty_rate == Decimal("25.50")
        assert dumping_duty.case_number == "ADC2023-001"
        assert dumping_duty.is_active is True
        assert dumping_duty.created_at is not None

    async def test_dumping_duty_foreign_key_constraint(self, test_session):
        """Test foreign key constraint to tariff codes."""
        data = TestDataFactory.create_dumping_duty_data(
            hs_code="9999999999"  # Non-existent HS code
        )
        
        dumping_duty = DumpingDuty(**data)
        test_session.add(dumping_duty)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_dumping_duty_positive_constraint(self, test_session):
        """Test that duty rates must be positive."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        data = TestDataFactory.create_dumping_duty_data(
            hs_code="0101010000",
            duty_rate=Decimal("-5.00")  # Negative rate
        )
        
        dumping_duty = DumpingDuty(**data)
        test_session.add(dumping_duty)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_dumping_duty_relationship(self, test_session):
        """Test relationship with tariff code."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        dumping_duty = await DatabaseTestHelper.create_dumping_duty(
            test_session,
            hs_code="0101010000"
        )
        
        # Test relationship
        assert dumping_duty.tariff_code == tariff_code
        assert dumping_duty in tariff_code.dumping_duties

    async def test_dumping_duty_active_status_methods(self, test_session):
        """Test active status checking methods."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Test currently active duty
        active_duty = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN",
            duty_rate=Decimal("25.00"),
            effective_date=yesterday,
            expiry_date=tomorrow,
            is_active=True
        )
        
        assert active_duty.is_currently_active() is True
        assert active_duty.is_effective is True
        assert active_duty.is_expired is False
        
        # Test inactive duty (flag set to False)
        inactive_duty = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN",
            duty_rate=Decimal("25.00"),
            effective_date=yesterday,
            expiry_date=tomorrow,
            is_active=False
        )
        
        assert inactive_duty.is_currently_active() is False
        
        # Test future effective duty
        future_duty = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN",
            duty_rate=Decimal("25.00"),
            effective_date=tomorrow,
            is_active=True
        )
        
        assert future_duty.is_currently_active() is False
        assert future_duty.is_effective is False
        
        # Test expired duty
        expired_duty = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN",
            duty_rate=Decimal("25.00"),
            effective_date=yesterday,
            expiry_date=yesterday,
            is_active=True
        )
        
        assert expired_duty.is_currently_active() is False
        assert expired_duty.is_effective is False
        assert expired_duty.is_expired is True

    async def test_dumping_duty_days_until_expiry(self, test_session):
        """Test days until expiry calculation."""
        today = date.today()
        future_date = today + timedelta(days=30)
        
        # Test duty with expiry date
        duty_with_expiry = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN",
            expiry_date=future_date
        )
        
        days_until_expiry = duty_with_expiry.days_until_expiry()
        assert days_until_expiry == 30
        
        # Test duty without expiry date
        duty_no_expiry = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN"
        )
        
        days_until_expiry = duty_no_expiry.days_until_expiry()
        assert days_until_expiry is None

    async def test_dumping_duty_calculation_string(self, test_session):
        """Test effective duty calculation string formatting."""
        # Test ad valorem only
        ad_valorem_duty = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN",
            duty_rate=Decimal("25.50")
        )
        
        calculation = ad_valorem_duty.effective_duty_calculation()
        assert calculation == "25.5000% ad valorem"
        
        # Test specific duty only
        specific_duty = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN",
            duty_amount=Decimal("10.00"),
            unit="kg"
        )
        
        calculation = specific_duty.effective_duty_calculation()
        assert calculation == "$10.00 per kg"
        
        # Test compound duty
        compound_duty = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN",
            duty_rate=Decimal("15.00"),
            duty_amount=Decimal("5.00"),
            unit="tonne"
        )
        
        calculation = compound_duty.effective_duty_calculation()
        assert calculation == "15.0000% ad valorem + $5.00 per tonne"
        
        # Test no duty specified
        no_duty = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN"
        )
        
        calculation = no_duty.effective_duty_calculation()
        assert calculation == "No duty specified"

    async def test_dumping_duty_string_representations(self, test_session):
        """Test string representation methods."""
        dumping_duty = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN",
            duty_type="dumping",
            duty_rate=Decimal("25.00"),
            is_active=True
        )
        
        repr_str = repr(dumping_duty)
        assert "DumpingDuty" in repr_str
        assert "0101010000" in repr_str
        assert "CHN" in repr_str
        assert "dumping" in repr_str
        
        str_repr = str(dumping_duty)
        assert "0101010000 - CHN: 25.0000%" == str_repr
        
        # Test with compound duty
        compound_duty = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN",
            duty_rate=Decimal("15.00"),
            duty_amount=Decimal("5.00"),
            unit="kg"
        )
        
        str_repr = str(compound_duty)
        assert "0101010000 - CHN: 15.0000% + $5.00/kg" == str_repr

    async def test_dumping_duty_cascade_delete(self, test_session):
        """Test cascade delete when tariff code is deleted."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        dumping_duty = await DatabaseTestHelper.create_dumping_duty(
            test_session,
            hs_code="0101010000"
        )
        
        dumping_duty_id = dumping_duty.id
        
        # Delete tariff code
        await test_session.delete(tariff_code)
        await test_session.commit()
        
        # Check that dumping duty is also deleted
        result = await test_session.execute(
            select(DumpingDuty).where(DumpingDuty.id == dumping_duty_id)
        )
        remaining_duty = result.scalar_one_or_none()
        assert remaining_duty is None


@pytest.mark.database
@pytest.mark.unit
class TestTco:
    """Test cases for Tco model."""

    async def test_create_tco(self, test_session):
        """Test creating a basic TCO."""
        # Create tariff code first
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        data = TestDataFactory.create_tco_data(
            tco_number="TCO2023001",
            hs_code="0101010000",
            description="Test TCO for live horses",
            applicant_name="Test Company Pty Ltd"
        )
        
        tco = Tco(**data)
        test_session.add(tco)
        await test_session.commit()
        await test_session.refresh(tco)
        
        assert tco.id is not None
        assert tco.tco_number == "TCO2023001"
        assert tco.hs_code == "0101010000"
        assert tco.description == "Test TCO for live horses"
        assert tco.applicant_name == "Test Company Pty Ltd"
        assert tco.is_current is True
        assert tco.created_at is not None

    async def test_tco_unique_constraint(self, test_session):
        """Test that TCO numbers must be unique."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Create first TCO
        tco1 = await DatabaseTestHelper.create_tco(
            test_session,
            tco_number="TCO2023001",
            hs_code="0101010000"
        )
        
        # Try to create second TCO with same number
        data = TestDataFactory.create_tco_data(
            tco_number="TCO2023001",  # Same number
            hs_code="0101010000"
        )
        
        tco2 = Tco(**data)
        test_session.add(tco2)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_tco_foreign_key_constraint(self, test_session):
        """Test foreign key constraint to tariff codes."""
        data = TestDataFactory.create_tco_data(
            hs_code="9999999999"  # Non-existent HS code
        )
        
        tco = Tco(**data)
        test_session.add(tco)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_tco_relationship(self, test_session):
        """Test relationship with tariff code."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        tco = await DatabaseTestHelper.create_tco(
            test_session,
            hs_code="0101010000"
        )
        
        # Test relationship
        assert tco.tariff_code == tariff_code
        assert tco in tariff_code.tcos

    async def test_tco_validity_methods(self, test_session):
        """Test TCO validity checking methods."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Test currently valid TCO
        valid_tco = Tco(
            tco_number="TCO2023001",
            hs_code="0101010000",
            description="Test TCO",
            effective_date=yesterday,
            expiry_date=tomorrow,
            is_current=True
        )
        
        assert valid_tco.is_currently_valid() is True
        
        # Test non-current TCO
        non_current_tco = Tco(
            tco_number="TCO2023002",
            hs_code="0101010000",
            description="Test TCO",
            effective_date=yesterday,
            expiry_date=tomorrow,
            is_current=False
        )
        
        assert non_current_tco.is_currently_valid() is False
        
        # Test future effective TCO
        future_tco = Tco(
            tco_number="TCO2023003",
            hs_code="0101010000",
            description="Test TCO",
            effective_date=tomorrow,
            is_current=True
        )
        
        assert future_tco.is_currently_valid() is False
        
        # Test expired TCO
        expired_tco = Tco(
            tco_number="TCO2023004",
            hs_code="0101010000",
            description="Test TCO",
            effective_date=yesterday,
            expiry_date=yesterday,
            is_current=True
        )
        
        assert expired_tco.is_currently_valid() is False

    async def test_tco_days_until_expiry(self, test_session):
        """Test days until expiry calculation."""
        today = date.today()
        future_date = today + timedelta(days=45)
        
        # Test TCO with expiry date
        tco_with_expiry = Tco(
            tco_number="TCO2023001",
            hs_code="0101010000",
            description="Test TCO",
            expiry_date=future_date
        )
        
        days_until_expiry = tco_with_expiry.days_until_expiry()
        assert days_until_expiry == 45
        
        # Test TCO without expiry date
        tco_no_expiry = Tco(
            tco_number="TCO2023002",
            hs_code="0101010000",
            description="Test TCO"
        )
        
        days_until_expiry = tco_no_expiry.days_until_expiry()
        assert days_until_expiry is None

    async def test_tco_gazette_reference(self, test_session):
        """Test gazette reference formatting."""
        gazette_date = date(2023, 6, 15)
        
        # Test with both gazette number and date
        tco_full_gazette = Tco(
            tco_number="TCO2023001",
            hs_code="0101010000",
            description="Test TCO",
            gazette_number="G2023-123",
            gazette_date=gazette_date
        )
        
        reference = tco_full_gazette.gazette_reference()
        assert reference == "Gazette G2023-123 (15/06/2023)"
        
        # Test with gazette number only
        tco_number_only = Tco(
            tco_number="TCO2023002",
            hs_code="0101010000",
            description="Test TCO",
            gazette_number="G2023-124"
        )
        
        reference = tco_number_only.gazette_reference()
        assert reference == "Gazette G2023-124"
        
        # Test with gazette date only
        tco_date_only = Tco(
            tco_number="TCO2023003",
            hs_code="0101010000",
            description="Test TCO",
            gazette_date=gazette_date
        )
        
        reference = tco_date_only.gazette_reference()
        assert reference == "Gazette dated 15/06/2023"
        
        # Test with no gazette information
        tco_no_gazette = Tco(
            tco_number="TCO2023004",
            hs_code="0101010000",
            description="Test TCO"
        )
        
        reference = tco_no_gazette.gazette_reference()
        assert reference == ""

    async def test_tco_string_representations(self, test_session):
        """Test string representation methods."""
        tco = Tco(
            tco_number="TCO2023001",
            hs_code="0101010000",
            description="Test TCO for live horses used in breeding programs",
            is_current=True
        )
        
        repr_str = repr(tco)
        assert "Tco" in repr_str
        assert "TCO2023001" in repr_str
        assert "0101010000" in repr_str
        assert "is_current=True" in repr_str
        
        str_repr = str(tco)
        assert "TCO TCO2023001: Test TCO for live horses used in breeding..." == str_repr

    async def test_tco_cascade_delete(self, test_session):
        """Test cascade delete when tariff code is deleted."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        tco = await DatabaseTestHelper.create_tco(
            test_session,
            hs_code="0101010000"
        )
        
        tco_id = tco.id
        
        # Delete tariff code
        await test_session.delete(tariff_code)
        await test_session.commit()
        
        # Check that TCO is also deleted
        result = await test_session.execute(
            select(Tco).where(Tco.id == tco_id)
        )
        remaining_tco = result.scalar_one_or_none()
        assert remaining_tco is None


@pytest.mark.database
@pytest.mark.unit
class TestGstProvision:
    """Test cases for GstProvision model."""

    async def test_create_gst_provision(self, test_session):
        """Test creating a basic GST provision."""
        # Create tariff code first
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        gst_provision = GstProvision(
            hs_code="0101010000",
            schedule_reference="Schedule 4",
            exemption_type="GST-free",
            description="Live animals for breeding purposes",
            value_threshold=Decimal("1000.00"),
            conditions="Must be certified breeding stock",
            is_active=True
        )
        
        test_session.add(gst_provision)
        await test_session.commit()
        await test_session.refresh(gst_provision)
        
        assert gst_provision.id is not None
        assert gst_provision.hs_code == "0101010000"
        assert gst_provision.schedule_reference == "Schedule 4"
        assert gst_provision.exemption_type == "GST-free"
        assert gst_provision.value_threshold == Decimal("1000.00")
        assert gst_provision.is_active is True
        assert gst_provision.created_at is not None

    async def test_gst_provision_optional_hs_code(self, test_session):
        """Test GST provision with no HS code (general provision)."""
        gst_provision = GstProvision(
            schedule_reference="Schedule 1",
            exemption_type="Input-taxed",
            description="General financial services",
            is_active=True
        )
        
        test_session.add(gst_provision)
        await test_session.commit()
        await test_session.refresh(gst_provision)
        
        assert gst_provision.id is not None
        assert gst_provision.hs_code is None
        assert gst_provision.tariff_code is None

    async def test_gst_provision_foreign_key_constraint(self, test_session):
        """Test foreign key constraint to tariff codes."""
        gst_provision = GstProvision(
            hs_code="9999999999",  # Non-existent HS code
            exemption_type="GST-free"
        )
        
        test_session.add(gst_provision)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_gst_provision_relationship(self, test_session):
        """Test relationship with tariff code."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        gst_provision = GstProvision(
            hs_code="0101010000",
            exemption_type="GST-free"
        )
        
        test_session.add(gst_provision)
        await test_session.commit()
        await test_session.refresh(gst_provision)
        
        # Test relationship
        assert gst_provision.tariff_code == tariff_code
        assert gst_provision in tariff_code.gst_provisions

    async def test_gst_provision_applies_to_value(self, test_session):
        """Test value threshold application logic."""
        # Test provision with threshold
        provision_with_threshold = GstProvision(
            exemption_type="GST-free",
            value_threshold=Decimal("1000.00"),
            is_active=True
        )
        
        assert provision_with_threshold.applies_to_value(Decimal("1500.00")) is True
        assert provision_with_threshold.applies_to_value(Decimal("1000.00")) is True
        assert provision_with_threshold.applies_to_value(Decimal("500.00")) is False
        
        # Test provision without threshold
        provision_no_threshold = GstProvision(
            exemption_type="GST-free",
            is_active=True
        )
        
        assert provision_no_threshold.applies_to_value(Decimal("100.00")) is True
        assert provision_no_threshold.applies_to_value(Decimal("0.01")) is True
        
        # Test inactive provision
        inactive_provision = GstProvision(
            exemption_type="GST-free",
            value_threshold=Decimal("100.00"),
            is_active=False
        )
        
        assert inactive_provision.applies_to_value(Decimal("1000.00")) is False

    async def test_gst_provision_exemption_details(self, test_session):
        """Test exemption details formatting."""
        # Test provision with all details
        full_provision = GstProvision(
            exemption_type="GST-free",
            schedule_reference="Schedule 4",
            value_threshold=Decimal("1000.00"),
            conditions="Must be certified breeding stock"
        )
        
        details = full_provision.exemption_details()
        expected_parts = [
            "Type: GST-free",
            "Schedule: Schedule 4",
            "Threshold: $1,000.00",
            "Conditions: Must be certified breeding stock"
        ]
        expected_details = " | ".join(expected_parts)
        assert details == expected_details
        
        # Test provision with minimal details
        minimal_provision = GstProvision(
            exemption_type="Input-taxed"
        )
        
        details = minimal_provision.exemption_details()
        assert details == "Type: Input-taxed"
        
        # Test provision with no details
        empty_provision = GstProvision()
        
        details = empty_provision.exemption_details()
        assert details == "No exemption details available"

    async def test_gst_provision_string_representations(self, test_session):
        """Test string representation methods."""
        gst_provision = GstProvision(
            hs_code="0101010000",
            exemption_type="GST-free",
            description="Live animals for breeding purposes",
            is_active=True
        )
        
        repr_str = repr(gst_provision)
        assert "GstProvision" in repr_str
        assert "0101010000" in repr_str
        assert "GST-free" in repr_str
        assert "is_active=True" in repr_str
        
        str_repr = str(gst_provision)
        assert "GST Provision: Live animals for breeding purposes" == str_repr
        
        # Test with long description
        long_description = "A" * 100
        long_provision = GstProvision(
            description=long_description
        )
        
        str_repr = str(long_provision)
        assert len(str_repr) <= len("GST Provision: ") + 53  # 50 chars + "..."
        assert str_repr.endswith("...")

    async def test_gst_provision_cascade_delete(self, test_session):
        """Test cascade delete when tariff code is deleted."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        gst_provision = GstProvision(
            hs_code="0101010000",
            exemption_type="GST-free"
        )
        
        test_session.add(gst_provision)
        await test_session.commit()
        await test_session.refresh(gst_provision)
        
        provision_id = gst_provision.id
        
        # Delete tariff code
        await test_session.delete(tariff_code)
        await test_session.commit()
        
        # Check that GST provision is also deleted
        result = await test_session.execute(
            select(GstProvision).where(GstProvision.id == provision_id)
        )
        remaining_provision = result.scalar_one_or_none()
        assert remaining_provision is None

    async def test_gst_provision_decimal_precision(self, test_session):
        """Test decimal precision for value thresholds."""
        gst_provision = GstProvision(
            exemption_type="GST-free",
            value_threshold=Decimal("1234567890.99")  # Large value with decimals
        )
        
        test_session.add(gst_provision)
        await test_session.commit()
        await test_session.refresh(gst_provision)
        
        assert gst_provision.value_threshold == Decimal("1234567890.99")
        
        # Test threshold application with precise values
        assert gst_provision.applies_to_value(Decimal("1234567890.99")) is True
        assert gst_provision.applies_to_value(Decimal("1234567890.98")) is False