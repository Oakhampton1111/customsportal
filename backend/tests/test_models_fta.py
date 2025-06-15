"""
Unit tests for FtaRate model and trade agreement models.

This module tests the FtaRate model including validation, relationships,
business logic for preferential duty calculations, and trade agreement integration.
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models import FtaRate, TariffCode, TradeAgreement
from tests.utils.test_helpers import TestDataFactory, DatabaseTestHelper


@pytest.mark.database
@pytest.mark.unit
class TestFtaRate:
    """Test cases for FtaRate model."""

    async def test_create_fta_rate(self, test_session):
        """Test creating a basic FTA rate."""
        # Create dependencies
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        trade_agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Australia-United States Free Trade Agreement",
            status="active"
        )
        test_session.add(trade_agreement)
        await test_session.commit()
        await test_session.refresh(trade_agreement)
        
        # Create FTA rate
        data = TestDataFactory.create_fta_rate_data(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("0.00"),
            staging_category="A"
        )
        
        fta_rate = FtaRate(**data)
        test_session.add(fta_rate)
        await test_session.commit()
        await test_session.refresh(fta_rate)
        
        assert fta_rate.id is not None
        assert fta_rate.hs_code == "0101010000"
        assert fta_rate.fta_code == "AUSFTA"
        assert fta_rate.country_code == "USA"
        assert fta_rate.preferential_rate == Decimal("0.00")
        assert fta_rate.staging_category == "A"
        assert fta_rate.created_at is not None

    async def test_fta_rate_foreign_key_constraints(self, test_session):
        """Test foreign key constraints."""
        # Test invalid HS code
        trade_agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Test Agreement"
        )
        test_session.add(trade_agreement)
        await test_session.commit()
        
        data = TestDataFactory.create_fta_rate_data(
            hs_code="9999999999",  # Non-existent HS code
            fta_code="AUSFTA"
        )
        
        fta_rate = FtaRate(**data)
        test_session.add(fta_rate)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()
        
        await test_session.rollback()
        
        # Test invalid FTA code
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        data = TestDataFactory.create_fta_rate_data(
            hs_code="0101010000",
            fta_code="INVALID"  # Non-existent FTA code
        )
        
        fta_rate = FtaRate(**data)
        test_session.add(fta_rate)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_fta_rate_positive_constraint(self, test_session):
        """Test that preferential rate must be positive."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        trade_agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Test Agreement"
        )
        test_session.add(trade_agreement)
        await test_session.commit()
        
        data = TestDataFactory.create_fta_rate_data(
            hs_code="0101010000",
            fta_code="AUSFTA",
            preferential_rate=Decimal("-5.00")  # Negative rate
        )
        
        fta_rate = FtaRate(**data)
        test_session.add(fta_rate)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_fta_rate_relationships(self, test_session):
        """Test relationships with tariff code and trade agreement."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        trade_agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Australia-United States Free Trade Agreement"
        )
        test_session.add(trade_agreement)
        await test_session.commit()
        await test_session.refresh(trade_agreement)
        
        fta_rate = await DatabaseTestHelper.create_fta_rate(
            test_session,
            hs_code="0101010000",
            fta_code="AUSFTA"
        )
        
        # Test relationships
        assert fta_rate.tariff_code == tariff_code
        assert fta_rate.trade_agreement == trade_agreement
        assert fta_rate in tariff_code.fta_rates
        assert fta_rate in trade_agreement.fta_rates

    async def test_fta_rate_effective_properties(self, test_session):
        """Test effective date and elimination properties."""
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)
        
        # Test currently effective rate
        effective_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("5.00"),
            effective_date=yesterday,
            elimination_date=tomorrow
        )
        
        assert effective_rate.is_currently_effective is True
        assert effective_rate.is_eliminated is False
        assert effective_rate.effective_rate == Decimal("5.00")
        
        # Test future effective rate
        future_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("3.00"),
            effective_date=tomorrow
        )
        
        assert future_rate.is_currently_effective is False
        assert future_rate.is_eliminated is False
        
        # Test eliminated rate
        eliminated_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("10.00"),
            effective_date=yesterday,
            elimination_date=yesterday
        )
        
        assert eliminated_rate.is_currently_effective is False
        assert eliminated_rate.is_eliminated is True
        assert eliminated_rate.effective_rate == Decimal("0.00")

    async def test_fta_rate_quota_properties(self, test_session):
        """Test quota-related properties."""
        # Test rate with quota
        quota_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            quota_quantity=Decimal("1000.00"),
            quota_unit="tonnes"
        )
        
        assert quota_rate.is_quota_applicable is True
        
        # Test rate without quota
        no_quota_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA"
        )
        
        assert no_quota_rate.is_quota_applicable is False
        
        # Test rate with zero quota
        zero_quota_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            quota_quantity=Decimal("0.00")
        )
        
        assert zero_quota_rate.is_quota_applicable is False

    async def test_fta_rate_staging_description(self, test_session):
        """Test staging category descriptions."""
        test_cases = [
            ("A", "Immediate elimination"),
            ("B", "Staged elimination over multiple years"),
            ("C", "Staged elimination over extended period"),
            ("D", "Special staging arrangement"),
            ("E", "Excluded from tariff elimination"),
            ("Base", "Base rate - no reduction"),
            ("X", "Category X"),  # Unknown category
            (None, "No staging category specified")
        ]
        
        for category, expected_description in test_cases:
            fta_rate = FtaRate(
                hs_code="0101010000",
                fta_code="AUSFTA",
                country_code="USA",
                staging_category=category
            )
            
            assert fta_rate.staging_description == expected_description

    async def test_fta_rate_duty_calculation(self, test_session):
        """Test preferential duty calculation."""
        # Test normal calculation
        fta_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("5.00"),
            effective_date=date.today() - timedelta(days=1)
        )
        
        value = Decimal("1000.00")
        calculated_duty = fta_rate.calculate_preferential_duty(value)
        expected_duty = Decimal("50.00")  # 5% of 1000
        assert calculated_duty == expected_duty
        
        # Test eliminated rate (should be 0)
        eliminated_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("10.00"),
            elimination_date=date.today() - timedelta(days=1)
        )
        
        calculated_duty = eliminated_rate.calculate_preferential_duty(value)
        expected_duty = Decimal("0.00")
        assert calculated_duty == expected_duty
        
        # Test rate with no preferential rate
        no_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA"
        )
        
        calculated_duty = no_rate.calculate_preferential_duty(value)
        assert calculated_duty is None

    async def test_fta_rate_origin_requirements(self, test_session):
        """Test rules of origin requirements."""
        # Test with short origin requirements
        short_origin = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            rule_of_origin="Wholly obtained or produced"
        )
        
        summary = short_origin.get_origin_requirements_summary()
        assert summary == "Wholly obtained or produced"
        
        # Test with long origin requirements (should be truncated)
        long_origin_text = "A" * 250  # 250 characters
        long_origin = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            rule_of_origin=long_origin_text
        )
        
        summary = long_origin.get_origin_requirements_summary()
        assert len(summary) == 200  # 197 + "..."
        assert summary.endswith("...")
        
        # Test with no origin requirements
        no_origin = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA"
        )
        
        summary = no_origin.get_origin_requirements_summary()
        assert summary == "No specific origin requirements specified"

    async def test_fta_rate_comparison_with_general_rate(self, test_session):
        """Test comparison with general duty rates."""
        today = date.today()
        
        # Test better FTA rate
        better_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("3.00"),
            effective_date=today - timedelta(days=1)
        )
        
        general_rate = Decimal("5.00")
        assert better_rate.is_rate_better_than(general_rate) is True
        
        # Test worse FTA rate
        worse_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("7.00"),
            effective_date=today - timedelta(days=1)
        )
        
        assert worse_rate.is_rate_better_than(general_rate) is False
        
        # Test non-effective rate
        future_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("1.00"),
            effective_date=today + timedelta(days=1)
        )
        
        assert future_rate.is_rate_better_than(general_rate) is False
        
        # Test with None rates
        no_pref_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            effective_date=today - timedelta(days=1)
        )
        
        assert no_pref_rate.is_rate_better_than(general_rate) is False
        assert better_rate.is_rate_better_than(None) is False

    async def test_fta_rate_string_representations(self, test_session):
        """Test string representation methods."""
        fta_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("5.00")
        )
        
        repr_str = repr(fta_rate)
        assert "FtaRate" in repr_str
        assert "0101010000" in repr_str
        assert "AUSFTA" in repr_str
        assert "USA" in repr_str
        
        str_repr = str(fta_rate)
        assert "0101010000 (AUSFTA-USA): 5.00%" == str_repr
        
        # Test with free rate
        free_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA"
        )
        
        str_repr = str(free_rate)
        assert "0101010000 (AUSFTA-USA): Free" == str_repr

    async def test_fta_rate_multiple_rates_per_tariff(self, test_session):
        """Test multiple FTA rates for the same tariff code."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Create trade agreements
        ausfta = TradeAgreement(fta_code="AUSFTA", full_name="Australia-US FTA")
        cptpp = TradeAgreement(fta_code="CPTPP", full_name="CPTPP Agreement")
        test_session.add_all([ausfta, cptpp])
        await test_session.commit()
        
        # Create multiple FTA rates
        fta_rate1 = await DatabaseTestHelper.create_fta_rate(
            test_session,
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA"
        )
        
        fta_rate2 = await DatabaseTestHelper.create_fta_rate(
            test_session,
            hs_code="0101010000",
            fta_code="CPTPP",
            country_code="JPN"
        )
        
        # Verify both rates are associated with the tariff code
        assert len(tariff_code.fta_rates) == 2
        assert fta_rate1 in tariff_code.fta_rates
        assert fta_rate2 in tariff_code.fta_rates

    async def test_fta_rate_cascade_delete(self, test_session):
        """Test cascade delete behavior."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        trade_agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Test Agreement"
        )
        test_session.add(trade_agreement)
        await test_session.commit()
        
        fta_rate = await DatabaseTestHelper.create_fta_rate(
            test_session,
            hs_code="0101010000",
            fta_code="AUSFTA"
        )
        
        fta_rate_id = fta_rate.id
        
        # Delete tariff code
        await test_session.delete(tariff_code)
        await test_session.commit()
        
        # Check that FTA rate is also deleted
        result = await test_session.execute(
            select(FtaRate).where(FtaRate.id == fta_rate_id)
        )
        remaining_fta_rate = result.scalar_one_or_none()
        assert remaining_fta_rate is None

    async def test_fta_rate_decimal_precision(self, test_session):
        """Test decimal precision for FTA rates."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        trade_agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Test Agreement"
        )
        test_session.add(trade_agreement)
        await test_session.commit()
        
        # Test with high precision rate
        fta_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("12.75"),  # 2 decimal places
            quota_quantity=Decimal("1234567890123.45")  # Large quota with decimals
        )
        
        test_session.add(fta_rate)
        await test_session.commit()
        await test_session.refresh(fta_rate)
        
        assert fta_rate.preferential_rate == Decimal("12.75")
        assert fta_rate.quota_quantity == Decimal("1234567890123.45")
        
        # Test calculation precision
        value = Decimal("1000.00")
        calculated_duty = fta_rate.calculate_preferential_duty(value)
        expected_duty = Decimal("127.50")  # 12.75% of 1000
        assert calculated_duty == expected_duty

    async def test_fta_rate_edge_cases(self, test_session):
        """Test edge cases for FTA rates."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        trade_agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Test Agreement"
        )
        test_session.add(trade_agreement)
        await test_session.commit()
        
        # Test zero rate
        zero_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("0.00"),
            effective_date=date.today() - timedelta(days=1)
        )
        
        value = Decimal("1000.00")
        calculated_duty = zero_rate.calculate_preferential_duty(value)
        assert calculated_duty == Decimal("0.00")
        
        # Test very small value
        small_value = Decimal("0.01")
        normal_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("5.00"),
            effective_date=date.today() - timedelta(days=1)
        )
        
        calculated_duty = normal_rate.calculate_preferential_duty(small_value)
        expected_duty = Decimal("0.0005")  # 5% of 0.01
        assert calculated_duty == expected_duty

    async def test_fta_rate_safeguard_provisions(self, test_session):
        """Test safeguard-related functionality."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        trade_agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Test Agreement"
        )
        test_session.add(trade_agreement)
        await test_session.commit()
        
        # Test rate with safeguard
        safeguard_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("2.00"),
            safeguard_applicable=True
        )
        
        test_session.add(safeguard_rate)
        await test_session.commit()
        await test_session.refresh(safeguard_rate)
        
        assert safeguard_rate.safeguard_applicable is True
        
        # Test rate without safeguard (default)
        no_safeguard_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="CAN",
            preferential_rate=Decimal("3.00")
        )
        
        test_session.add(no_safeguard_rate)
        await test_session.commit()
        await test_session.refresh(no_safeguard_rate)
        
        assert no_safeguard_rate.safeguard_applicable is False