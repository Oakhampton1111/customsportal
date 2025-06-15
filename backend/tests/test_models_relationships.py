"""
Unit tests for cross-model relationships and database operations.

This module tests complex relationships between models, cascade operations,
referential integrity, and advanced database functionality across the entire
model ecosystem.
"""

import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal
from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError

from database import Base
from models import (
    TariffCode, TariffSection, TariffChapter, TradeAgreement,
    DutyRate, FtaRate, DumpingDuty, Tco, GstProvision,
    ExportCode, ProductClassification
)
from tests.utils.test_helpers import TestDataFactory, DatabaseTestHelper


@pytest.mark.database
@pytest.mark.unit
class TestModelRelationships:
    """Test complex relationships between models."""

    async def test_complete_tariff_ecosystem(self, test_session):
        """Test creating a complete tariff ecosystem with all related models."""
        # Create hierarchy
        section = TariffSection(
            section_number=1,
            title="Live Animals; Animal Products",
            chapter_range="01-05"
        )
        test_session.add(section)
        await test_session.commit()
        await test_session.refresh(section)
        
        chapter = TariffChapter(
            chapter_number=1,
            title="Live animals",
            section_id=section.id
        )
        test_session.add(chapter)
        await test_session.commit()
        await test_session.refresh(chapter)
        
        # Create trade agreement
        trade_agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Australia-United States Free Trade Agreement",
            status="active"
        )
        test_session.add(trade_agreement)
        await test_session.commit()
        await test_session.refresh(trade_agreement)
        
        # Create tariff code
        tariff_code = TariffCode(
            hs_code="0101010000",
            description="Live horses for breeding purposes",
            level=10,
            section_id=section.id,
            chapter_id=chapter.id,
            is_active=True
        )
        test_session.add(tariff_code)
        await test_session.commit()
        await test_session.refresh(tariff_code)
        
        # Create all related models
        duty_rate = DutyRate(
            hs_code="0101010000",
            general_rate=Decimal("5.00"),
            unit_type="ad_valorem",
            rate_text="5%"
        )
        test_session.add(duty_rate)
        
        fta_rate = FtaRate(
            hs_code="0101010000",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("0.00"),
            staging_category="A"
        )
        test_session.add(fta_rate)
        
        dumping_duty = DumpingDuty(
            hs_code="0101010000",
            country_code="CHN",
            duty_type="dumping",
            duty_rate=Decimal("25.00"),
            case_number="ADC2023-001"
        )
        test_session.add(dumping_duty)
        
        tco = Tco(
            tco_number="TCO2023001",
            hs_code="0101010000",
            description="Breeding horses under TCO",
            is_current=True
        )
        test_session.add(tco)
        
        gst_provision = GstProvision(
            hs_code="0101010000",
            exemption_type="GST-free",
            description="Live animals exemption"
        )
        test_session.add(gst_provision)
        
        export_code = ExportCode(
            ahecc_code="0101010000",
            description="Live horses - export classification",
            corresponding_import_code="0101010000"
        )
        test_session.add(export_code)
        
        classification = ProductClassification(
            product_description="Live breeding horses from Ireland",
            hs_code="0101010000",
            confidence_score=0.95,
            classification_source="ai"
        )
        test_session.add(classification)
        
        await test_session.commit()
        
        # Refresh all objects to load relationships
        await test_session.refresh(tariff_code)
        await test_session.refresh(section)
        await test_session.refresh(chapter)
        await test_session.refresh(trade_agreement)
        
        # Test all relationships
        assert tariff_code.section == section
        assert tariff_code.chapter == chapter
        assert len(tariff_code.duty_rates) == 1
        assert len(tariff_code.fta_rates) == 1
        assert len(tariff_code.dumping_duties) == 1
        assert len(tariff_code.tcos) == 1
        assert len(tariff_code.gst_provisions) == 1
        assert len(tariff_code.export_codes) == 1
        assert len(tariff_code.product_classifications) == 1
        
        assert duty_rate in tariff_code.duty_rates
        assert fta_rate in tariff_code.fta_rates
        assert dumping_duty in tariff_code.dumping_duties
        assert tco in tariff_code.tcos
        assert gst_provision in tariff_code.gst_provisions
        assert export_code in tariff_code.export_codes
        assert classification in tariff_code.product_classifications
        
        # Test reverse relationships
        assert fta_rate in trade_agreement.fta_rates
        assert tariff_code in section.tariff_codes
        assert tariff_code in chapter.tariff_codes

    async def test_cascade_delete_operations(self, test_session):
        """Test cascade delete operations across the model hierarchy."""
        # Create complete hierarchy
        section = TariffSection(section_number=1, title="Test Section")
        test_session.add(section)
        await test_session.commit()
        await test_session.refresh(section)
        
        chapter = TariffChapter(
            chapter_number=1,
            title="Test Chapter",
            section_id=section.id
        )
        test_session.add(chapter)
        await test_session.commit()
        await test_session.refresh(chapter)
        
        tariff_code = TariffCode(
            hs_code="0101010000",
            description="Test tariff code",
            level=10,
            section_id=section.id,
            chapter_id=chapter.id,
            is_active=True
        )
        test_session.add(tariff_code)
        await test_session.commit()
        await test_session.refresh(tariff_code)
        
        # Create dependent models
        duty_rate = await DatabaseTestHelper.create_duty_rate(
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
        
        dumping_duty = await DatabaseTestHelper.create_dumping_duty(
            test_session,
            hs_code="0101010000"
        )
        
        tco = await DatabaseTestHelper.create_tco(
            test_session,
            hs_code="0101010000"
        )
        
        # Store IDs for verification
        duty_rate_id = duty_rate.id
        fta_rate_id = fta_rate.id
        dumping_duty_id = dumping_duty.id
        tco_id = tco.id
        chapter_id = chapter.id
        
        # Delete section (should cascade to chapter but not tariff codes)
        await test_session.delete(section)
        await test_session.commit()
        
        # Check that chapter is deleted
        result = await test_session.execute(
            select(TariffChapter).where(TariffChapter.id == chapter_id)
        )
        remaining_chapter = result.scalar_one_or_none()
        assert remaining_chapter is None
        
        # Refresh tariff code and check that section/chapter references are NULL
        await test_session.refresh(tariff_code)
        assert tariff_code.section_id is None
        assert tariff_code.chapter_id is None
        
        # Delete tariff code (should cascade to all dependent models)
        await test_session.delete(tariff_code)
        await test_session.commit()
        
        # Check that all dependent models are deleted
        for model_class, model_id in [
            (DutyRate, duty_rate_id),
            (FtaRate, fta_rate_id),
            (DumpingDuty, dumping_duty_id),
            (Tco, tco_id)
        ]:
            result = await test_session.execute(
                select(model_class).where(model_class.id == model_id)
            )
            remaining_model = result.scalar_one_or_none()
            assert remaining_model is None

    async def test_referential_integrity_constraints(self, test_session):
        """Test referential integrity constraints across models."""
        # Test that creating models with non-existent foreign keys fails
        
        # Test duty rate with non-existent HS code
        with pytest.raises(IntegrityError):
            duty_rate = DutyRate(
                hs_code="9999999999",
                general_rate=Decimal("5.00")
            )
            test_session.add(duty_rate)
            await test_session.commit()
        
        await test_session.rollback()
        
        # Test FTA rate with non-existent trade agreement
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        with pytest.raises(IntegrityError):
            fta_rate = FtaRate(
                hs_code="0101010000",
                fta_code="NONEXISTENT",
                country_code="USA"
            )
            test_session.add(fta_rate)
            await test_session.commit()
        
        await test_session.rollback()
        
        # Test chapter with non-existent section
        with pytest.raises(IntegrityError):
            chapter = TariffChapter(
                chapter_number=99,
                title="Invalid Chapter",
                section_id=99999  # Non-existent section
            )
            test_session.add(chapter)
            await test_session.commit()

    async def test_complex_queries_across_models(self, test_session):
        """Test complex queries that span multiple models."""
        # Set up test data
        section = TariffSection(section_number=1, title="Test Section")
        test_session.add(section)
        await test_session.commit()
        await test_session.refresh(section)
        
        chapter = TariffChapter(
            chapter_number=1,
            title="Test Chapter",
            section_id=section.id
        )
        test_session.add(chapter)
        await test_session.commit()
        await test_session.refresh(chapter)
        
        # Create multiple tariff codes
        tariff_codes = []
        for i in range(3):
            tc = TariffCode(
                hs_code=f"010101000{i}",
                description=f"Test product {i}",
                level=10,
                section_id=section.id,
                chapter_id=chapter.id,
                is_active=True
            )
            test_session.add(tc)
            tariff_codes.append(tc)
        
        await test_session.commit()
        
        # Create duty rates for each
        for i, tc in enumerate(tariff_codes):
            duty_rate = DutyRate(
                hs_code=tc.hs_code,
                general_rate=Decimal(f"{5 + i}.00"),
                unit_type="ad_valorem"
            )
            test_session.add(duty_rate)
        
        await test_session.commit()
        
        # Query: Find all tariff codes in section 1 with duty rates > 5%
        result = await test_session.execute(
            select(TariffCode)
            .join(DutyRate)
            .join(TariffSection)
            .where(
                and_(
                    TariffSection.section_number == 1,
                    DutyRate.general_rate > Decimal("5.00")
                )
            )
        )
        high_duty_codes = result.scalars().all()
        assert len(high_duty_codes) == 2  # Should exclude the 5.00% rate
        
        # Query: Count duty rates by section
        result = await test_session.execute(
            select(TariffSection.title, func.count(DutyRate.id))
            .join(TariffCode, TariffSection.id == TariffCode.section_id)
            .join(DutyRate)
            .group_by(TariffSection.title)
        )
        section_counts = result.all()
        assert len(section_counts) == 1
        assert section_counts[0][1] == 3  # 3 duty rates in the section

    async def test_model_validation_across_relationships(self, test_session):
        """Test validation constraints that span multiple models."""
        # Create base data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        trade_agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Test Agreement",
            status="active"
        )
        test_session.add(trade_agreement)
        await test_session.commit()
        
        # Test that FTA rates must have positive preferential rates
        with pytest.raises(IntegrityError):
            fta_rate = FtaRate(
                hs_code="0101010000",
                fta_code="AUSFTA",
                country_code="USA",
                preferential_rate=Decimal("-1.00")  # Negative rate
            )
            test_session.add(fta_rate)
            await test_session.commit()
        
        await test_session.rollback()
        
        # Test that dumping duties must have positive rates
        with pytest.raises(IntegrityError):
            dumping_duty = DumpingDuty(
                hs_code="0101010000",
                country_code="CHN",
                duty_rate=Decimal("-10.00")  # Negative rate
            )
            test_session.add(dumping_duty)
            await test_session.commit()
        
        await test_session.rollback()
        
        # Test that product classifications must have valid confidence scores
        with pytest.raises(IntegrityError):
            classification = ProductClassification(
                product_description="Test product",
                hs_code="0101010000",
                confidence_score=1.50  # > 1.00
            )
            test_session.add(classification)
            await test_session.commit()

    async def test_bulk_operations_and_performance(self, test_session):
        """Test bulk operations and performance considerations."""
        # Create base tariff code
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Bulk create duty rates
        duty_rates = []
        for i in range(10):
            duty_rate = DutyRate(
                hs_code="0101010000",
                general_rate=Decimal(f"{i + 1}.00"),
                statistical_code=f"0{i}"
            )
            duty_rates.append(duty_rate)
        
        test_session.add_all(duty_rates)
        await test_session.commit()
        
        # Test bulk query
        result = await test_session.execute(
            select(DutyRate).where(DutyRate.hs_code == "0101010000")
        )
        all_duty_rates = result.scalars().all()
        assert len(all_duty_rates) == 10
        
        # Test bulk update
        await test_session.execute(
            DutyRate.__table__.update()
            .where(DutyRate.hs_code == "0101010000")
            .values(unit_type="ad_valorem")
        )
        await test_session.commit()
        
        # Verify bulk update
        result = await test_session.execute(
            select(DutyRate).where(DutyRate.hs_code == "0101010000")
        )
        updated_rates = result.scalars().all()
        for rate in updated_rates:
            assert rate.unit_type == "ad_valorem"

    async def test_lazy_loading_and_eager_loading(self, test_session):
        """Test lazy loading and eager loading behavior."""
        # Create test data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        duty_rate = await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code="0101010000"
        )
        
        # Test lazy loading (default behavior)
        result = await test_session.execute(
            select(DutyRate).where(DutyRate.hs_code == "0101010000")
        )
        duty_rate_lazy = result.scalar_one()
        
        # Access related tariff code (should trigger lazy load)
        related_tariff = duty_rate_lazy.tariff_code
        assert related_tariff.hs_code == "0101010000"
        
        # Test that the relationship is properly loaded
        assert related_tariff == tariff_code

    async def test_transaction_rollback_behavior(self, test_session):
        """Test transaction rollback behavior across related models."""
        # Create base data
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Start a transaction that will be rolled back
        try:
            # Create valid duty rate
            duty_rate = DutyRate(
                hs_code="0101010000",
                general_rate=Decimal("5.00")
            )
            test_session.add(duty_rate)
            
            # Create invalid dumping duty (negative rate)
            dumping_duty = DumpingDuty(
                hs_code="0101010000",
                country_code="CHN",
                duty_rate=Decimal("-10.00")  # This will cause constraint violation
            )
            test_session.add(dumping_duty)
            
            await test_session.commit()
        except IntegrityError:
            await test_session.rollback()
        
        # Verify that neither model was created due to rollback
        result = await test_session.execute(
            select(DutyRate).where(DutyRate.hs_code == "0101010000")
        )
        duty_rates = result.scalars().all()
        assert len(duty_rates) == 0
        
        result = await test_session.execute(
            select(DumpingDuty).where(DumpingDuty.hs_code == "0101010000")
        )
        dumping_duties = result.scalars().all()
        assert len(dumping_duties) == 0

    async def test_model_inheritance_and_polymorphism(self, test_session):
        """Test any inheritance patterns and polymorphic behavior."""
        # All models inherit from Base, test common functionality
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        duty_rate = await DatabaseTestHelper.create_duty_rate(
            test_session,
            hs_code="0101010000"
        )
        
        # Test that all models have common Base functionality
        assert hasattr(tariff_code, '__tablename__')
        assert hasattr(duty_rate, '__tablename__')
        
        # Test that models can be queried through their base class
        assert isinstance(tariff_code, Base)
        assert isinstance(duty_rate, Base)

    async def test_index_usage_and_query_optimization(self, test_session):
        """Test that indexes are properly used for query optimization."""
        # Create test data that would benefit from indexes
        tariff_codes = []
        for i in range(5):
            tc = await DatabaseTestHelper.create_tariff_code(
                test_session,
                hs_code=f"010101000{i}"
            )
            tariff_codes.append(tc)
        
        # Create duty rates for each
        for tc in tariff_codes:
            await DatabaseTestHelper.create_duty_rate(
                test_session,
                hs_code=tc.hs_code
            )
        
        # Query using indexed fields
        result = await test_session.execute(
            select(TariffCode).where(TariffCode.hs_code == "0101010000")
        )
        found_tariff = result.scalar_one()
        assert found_tariff.hs_code == "0101010000"
        
        # Query using indexed foreign key
        result = await test_session.execute(
            select(DutyRate).where(DutyRate.hs_code == "0101010000")
        )
        found_duty = result.scalar_one()
        assert found_duty.hs_code == "0101010000"
        
        # Query using composite index
        result = await test_session.execute(
            select(TariffCode).where(
                and_(
                    TariffCode.is_active == True,
                    TariffCode.level == 10
                )
            )
        )
        active_codes = result.scalars().all()
        assert len(active_codes) == 5  # All our test codes are active and level 10