"""
Unit tests for DutyRate model.

This module tests the DutyRate model including validation, relationships,
and business logic for duty calculations.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models import DutyRate, TariffCode
from tests.utils.test_helpers import TestDataFactory, DatabaseTestHelper


@pytest.mark.database
@pytest.mark.unit
class TestDutyRate:
    """Test cases for DutyRate model."""

    async def test_create_duty_rate(self, test_session):
        """Test creating a basic duty rate."""
        # Create tariff code first
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        data = TestDataFactory.create_duty_rate_data(
            hs_code="0101010000",
            general_rate=Decimal("5.00"),
            unit_type="ad_valorem",
            rate_text="5%"
        )
        
        duty_rate = DutyRate(**data)
        test_session.add(duty_rate)
        await test_session.commit()
        await test_session.refresh(duty_rate)
        
        assert duty_rate.id is not None
        assert duty_rate.hs_code == "0101010000"
        assert duty_rate.general_rate == Decimal("5.00")
        assert duty_rate.unit_type == "ad_valorem"
        assert duty_rate.rate_text == "5%"
        assert duty_rate.created_at is not None

    async def test_duty_rate_foreign_key_constraint(self, test_session):
        """Test foreign key constraint to tariff codes."""
        data = TestDataFactory.create_duty_rate_data(
            hs_code="9999999999"  # Non-existent HS code
        )
        
        duty_rate = DutyRate(**data)
        test_session.add(duty_rate)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_duty_rate_positive_constraint(self, test_session):
        """Test that general rate must be positive."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        data = TestDataFactory.create_duty_rate_data(
            hs_code="0101010000",
            general_rate=Decimal("-5.00")  # Negative rate
        )
        
        duty_rate = DutyRate(**data)
        test_session.add(duty_rate)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_duty_rate_tariff_code_relationship(self, test_session):
        """Test relationship with tariff code."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        duty_rate = await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code="0101010000"
        )
        
        # Test relationship
        assert duty_rate.tariff_code == tariff_code
        assert duty_rate in tariff_code.duty_rates

    async def test_duty_rate_unit_type_properties(self, test_session):
        """Test unit type property methods."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Test ad valorem duty
        ad_valorem_duty = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("5.00"),
            unit_type="ad_valorem",
            rate_text="5%"
        )
        
        assert ad_valorem_duty.is_ad_valorem is True
        assert ad_valorem_duty.is_specific is False
        assert ad_valorem_duty.is_compound is False
        
        # Test specific duty
        specific_duty = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("10.00"),
            unit_type="specific",
            rate_text="$10 per unit"
        )
        
        assert specific_duty.is_ad_valorem is False
        assert specific_duty.is_specific is True
        assert specific_duty.is_compound is False
        
        # Test compound duty
        compound_duty = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("5.00"),
            unit_type="compound",
            rate_text="5% + $2 per unit"
        )
        
        assert compound_duty.is_ad_valorem is False
        assert compound_duty.is_specific is False
        assert compound_duty.is_compound is True

    async def test_duty_rate_effective_rate_text_property(self, test_session):
        """Test effective rate text property."""
        # Test with rate_text
        duty_with_text = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("5.00"),
            rate_text="5% or $10 per unit, whichever is greater"
        )
        
        assert duty_with_text.effective_rate_text == "5% or $10 per unit, whichever is greater"
        
        # Test with general_rate only
        duty_with_rate = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("7.50")
        )
        
        assert duty_with_rate.effective_rate_text == "7.50%"
        
        # Test with no rate
        duty_free = DutyRate(
            hs_code="0101010000"
        )
        
        assert duty_free.effective_rate_text == "Free"

    async def test_duty_rate_calculate_duty_amount(self, test_session):
        """Test duty amount calculation methods."""
        # Test ad valorem calculation
        ad_valorem_duty = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("5.00"),
            unit_type="ad_valorem"
        )
        
        value = Decimal("1000.00")
        calculated_duty = ad_valorem_duty.calculate_duty_amount(value)
        expected_duty = Decimal("50.00")  # 5% of 1000
        assert calculated_duty == expected_duty
        
        # Test specific calculation
        specific_duty = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("10.00"),
            unit_type="specific"
        )
        
        quantity = Decimal("5")
        calculated_duty = specific_duty.calculate_duty_amount(value, quantity)
        expected_duty = Decimal("50.00")  # 10 * 5
        assert calculated_duty == expected_duty
        
        # Test specific without quantity
        calculated_duty = specific_duty.calculate_duty_amount(value)
        assert calculated_duty is None
        
        # Test compound duty (should return None)
        compound_duty = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("5.00"),
            unit_type="compound"
        )
        
        calculated_duty = compound_duty.calculate_duty_amount(value)
        assert calculated_duty is None
        
        # Test free duty
        free_duty = DutyRate(
            hs_code="0101010000"
        )
        
        calculated_duty = free_duty.calculate_duty_amount(value)
        assert calculated_duty == Decimal("0.00")

    async def test_duty_rate_string_representations(self, test_session):
        """Test string representation methods."""
        duty_rate = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("5.00"),
            unit_type="ad_valorem",
            rate_text="5%"
        )
        
        repr_str = repr(duty_rate)
        assert "DutyRate" in repr_str
        assert "0101010000" in repr_str
        assert "general_rate=5.00" in repr_str
        
        str_repr = str(duty_rate)
        assert "0101010000: 5%" == str_repr
        
        # Test with general rate only
        duty_rate_no_text = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("7.50")
        )
        
        str_repr = str(duty_rate_no_text)
        assert "0101010000: 7.50%" == str_repr
        
        # Test with no rate
        duty_rate_free = DutyRate(
            hs_code="0101010000"
        )
        
        str_repr = str(duty_rate_free)
        assert "0101010000: No rate specified" == str_repr

    async def test_duty_rate_multiple_rates_per_tariff(self, test_session):
        """Test multiple duty rates for the same tariff code."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Create multiple duty rates
        duty_rate1 = await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code="0101010000",
            general_rate=Decimal("5.00"),
            statistical_code="01"
        )
        
        duty_rate2 = await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code="0101010000",
            general_rate=Decimal("10.00"),
            statistical_code="02"
        )
        
        # Verify both rates are associated with the tariff code
        assert len(tariff_code.duty_rates) == 2
        assert duty_rate1 in tariff_code.duty_rates
        assert duty_rate2 in tariff_code.duty_rates

    async def test_duty_rate_cascade_delete(self, test_session):
        """Test cascade delete when tariff code is deleted."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        duty_rate = await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code="0101010000"
        )
        
        duty_rate_id = duty_rate.id
        
        # Delete tariff code
        await test_session.delete(tariff_code)
        await test_session.commit()
        
        # Check that duty rate is also deleted
        result = await test_session.execute(
            select(DutyRate).where(DutyRate.id == duty_rate_id)
        )
        remaining_duty_rate = result.scalar_one_or_none()
        assert remaining_duty_rate is None

    async def test_duty_rate_decimal_precision(self, test_session):
        """Test decimal precision for duty rates."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Test with high precision rate
        duty_rate = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("12.75"),  # 2 decimal places
            unit_type="ad_valorem"
        )
        
        test_session.add(duty_rate)
        await test_session.commit()
        await test_session.refresh(duty_rate)
        
        assert duty_rate.general_rate == Decimal("12.75")
        
        # Test calculation precision
        value = Decimal("1000.00")
        calculated_duty = duty_rate.calculate_duty_amount(value)
        expected_duty = Decimal("127.50")  # 12.75% of 1000
        assert calculated_duty == expected_duty

    async def test_duty_rate_edge_cases(self, test_session):
        """Test edge cases for duty rate calculations."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Test zero rate
        zero_duty = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("0.00"),
            unit_type="ad_valorem"
        )
        
        value = Decimal("1000.00")
        calculated_duty = zero_duty.calculate_duty_amount(value)
        assert calculated_duty == Decimal("0.00")
        
        # Test very small value
        small_value = Decimal("0.01")
        duty_rate = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("5.00"),
            unit_type="ad_valorem"
        )
        
        calculated_duty = duty_rate.calculate_duty_amount(small_value)
        expected_duty = Decimal("0.0005")  # 5% of 0.01
        assert calculated_duty == expected_duty

    async def test_duty_rate_validation_constraints(self, test_session):
        """Test various validation constraints."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Test valid duty rate
        valid_duty = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("5.00"),
            unit_type="ad_valorem",
            rate_text="5%",
            statistical_code="01"
        )
        
        test_session.add(valid_duty)
        await test_session.commit()
        await test_session.refresh(valid_duty)
        
        assert valid_duty.id is not None
        
        # Test with minimal required fields
        minimal_duty = DutyRate(
            hs_code="0101010000"
        )
        
        test_session.add(minimal_duty)
        await test_session.commit()
        await test_session.refresh(minimal_duty)
        
        assert minimal_duty.id is not None
        assert minimal_duty.general_rate is None
        assert minimal_duty.unit_type is None