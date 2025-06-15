"""
Unit tests for TariffCode and hierarchy models.

This module tests the TariffCode model along with TariffSection, TariffChapter,
and TradeAgreement models, including their relationships and business logic.
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError

from models import TariffCode, TariffSection, TariffChapter, TradeAgreement
from tests.utils.test_helpers import TestDataFactory, DatabaseTestHelper


@pytest.mark.database
@pytest.mark.unit
class TestTariffCode:
    """Test cases for TariffCode model."""

    async def test_create_tariff_code(self, test_session):
        """Test creating a basic tariff code."""
        data = TestDataFactory.create_tariff_code_data(
            hs_code="0101010000",
            description="Live horses for breeding purposes",
            level=10
        )
        
        tariff_code = TariffCode(**data)
        test_session.add(tariff_code)
        await test_session.commit()
        await test_session.refresh(tariff_code)
        
        assert tariff_code.id is not None
        assert tariff_code.hs_code == "0101010000"
        assert tariff_code.description == "Live horses for breeding purposes"
        assert tariff_code.level == 10
        assert tariff_code.is_active is True
        assert tariff_code.created_at is not None
        assert tariff_code.updated_at is not None

    async def test_tariff_code_unique_constraint(self, test_session):
        """Test that HS codes must be unique."""
        data = TestDataFactory.create_tariff_code_data(hs_code="0101010000")
        
        # Create first tariff code
        tariff_code1 = TariffCode(**data)
        test_session.add(tariff_code1)
        await test_session.commit()
        
        # Try to create second with same HS code
        tariff_code2 = TariffCode(**data)
        test_session.add(tariff_code2)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_tariff_code_level_constraint(self, test_session):
        """Test that level constraint only allows valid values."""
        data = TestDataFactory.create_tariff_code_data(level=3)  # Invalid level
        
        tariff_code = TariffCode(**data)
        test_session.add(tariff_code)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_tariff_code_hierarchy_properties(self, test_session):
        """Test hierarchy level properties."""
        # Test chapter level (2 digits)
        chapter_code = TariffCode(
            hs_code="01",
            description="Live animals",
            level=2,
            is_active=True
        )
        
        assert chapter_code.is_chapter_level is True
        assert chapter_code.is_heading_level is False
        assert chapter_code.is_subheading_level is False
        assert chapter_code.is_statistical_level is False
        
        # Test heading level (4 digits)
        heading_code = TariffCode(
            hs_code="0101",
            description="Live horses, asses, mules and hinnies",
            level=4,
            is_active=True
        )
        
        assert heading_code.is_chapter_level is False
        assert heading_code.is_heading_level is True
        assert heading_code.is_subheading_level is False
        assert heading_code.is_statistical_level is False
        
        # Test subheading level (6 digits)
        subheading_code = TariffCode(
            hs_code="010101",
            description="Pure-bred breeding animals",
            level=6,
            is_active=True
        )
        
        assert subheading_code.is_chapter_level is False
        assert subheading_code.is_heading_level is False
        assert subheading_code.is_subheading_level is True
        assert subheading_code.is_statistical_level is False
        
        # Test statistical level (10 digits)
        statistical_code = TariffCode(
            hs_code="0101010000",
            description="Live horses for breeding purposes",
            level=10,
            is_active=True
        )
        
        assert statistical_code.is_chapter_level is False
        assert statistical_code.is_heading_level is False
        assert statistical_code.is_subheading_level is False
        assert statistical_code.is_statistical_level is True

    async def test_tariff_code_hierarchy_methods(self, test_session):
        """Test hierarchy extraction methods."""
        tariff_code = TariffCode(
            hs_code="0101010000",
            description="Live horses for breeding purposes",
            level=10,
            is_active=True
        )
        
        assert tariff_code.get_chapter_code() == "01"
        assert tariff_code.get_heading_code() == "0101"

    async def test_tariff_code_parent_child_relationship(self, test_session):
        """Test parent-child relationships in tariff hierarchy."""
        # Create parent code
        parent_data = TestDataFactory.create_tariff_code_data(
            hs_code="0101",
            description="Live horses, asses, mules and hinnies",
            level=4
        )
        parent_code = TariffCode(**parent_data)
        test_session.add(parent_code)
        await test_session.commit()
        await test_session.refresh(parent_code)
        
        # Create child code
        child_data = TestDataFactory.create_tariff_code_data(
            hs_code="010101",
            description="Pure-bred breeding animals",
            level=6,
            parent_code="0101"
        )
        child_code = TariffCode(**child_data)
        test_session.add(child_code)
        await test_session.commit()
        await test_session.refresh(child_code)
        
        # Test relationships
        assert child_code.parent_code == "0101"
        assert child_code.parent == parent_code
        assert child_code in parent_code.children

    async def test_tariff_code_string_representations(self, test_session):
        """Test string representation methods."""
        tariff_code = TariffCode(
            hs_code="0101010000",
            description="Live horses for breeding purposes",
            level=10,
            is_active=True
        )
        
        repr_str = repr(tariff_code)
        assert "TariffCode" in repr_str
        assert "0101010000" in repr_str
        assert "level=10" in repr_str
        
        str_repr = str(tariff_code)
        assert "0101010000: Live horses for breeding purposes" == str_repr

    async def test_tariff_code_cascade_delete(self, test_session):
        """Test cascade delete behavior."""
        # Create parent and child codes
        parent_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101",
            level=4
        )
        
        child_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="010101",
            level=6,
            parent_code="0101"
        )
        
        # Delete parent
        await test_session.delete(parent_code)
        await test_session.commit()
        
        # Check that child still exists but parent_code is cleared
        result = await test_session.execute(
            select(TariffCode).where(TariffCode.hs_code == "010101")
        )
        remaining_child = result.scalar_one_or_none()
        assert remaining_child is not None
        # Note: The parent relationship should be handled by the foreign key constraint


@pytest.mark.database
@pytest.mark.unit
class TestTariffSection:
    """Test cases for TariffSection model."""

    async def test_create_tariff_section(self, test_session):
        """Test creating a tariff section."""
        section = TariffSection(
            section_number=1,
            title="Live Animals; Animal Products",
            description="This section covers live animals and products of animal origin",
            chapter_range="01-05"
        )
        
        test_session.add(section)
        await test_session.commit()
        await test_session.refresh(section)
        
        assert section.id is not None
        assert section.section_number == 1
        assert section.title == "Live Animals; Animal Products"
        assert section.chapter_range == "01-05"

    async def test_tariff_section_unique_constraint(self, test_session):
        """Test that section numbers must be unique."""
        section1 = TariffSection(
            section_number=1,
            title="Live Animals; Animal Products"
        )
        test_session.add(section1)
        await test_session.commit()
        
        section2 = TariffSection(
            section_number=1,
            title="Duplicate section"
        )
        test_session.add(section2)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_tariff_section_string_representations(self, test_session):
        """Test string representation methods."""
        section = TariffSection(
            section_number=1,
            title="Live Animals; Animal Products"
        )
        
        repr_str = repr(section)
        assert "TariffSection" in repr_str
        assert "section_number=1" in repr_str
        
        str_repr = str(section)
        assert "Section 1: Live Animals; Animal Products" == str_repr


@pytest.mark.database
@pytest.mark.unit
class TestTariffChapter:
    """Test cases for TariffChapter model."""

    async def test_create_tariff_chapter(self, test_session):
        """Test creating a tariff chapter."""
        # Create section first
        section = TariffSection(
            section_number=1,
            title="Live Animals; Animal Products"
        )
        test_session.add(section)
        await test_session.commit()
        await test_session.refresh(section)
        
        # Create chapter
        chapter = TariffChapter(
            chapter_number=1,
            title="Live animals",
            chapter_notes="This chapter covers all live animals",
            section_id=section.id
        )
        
        test_session.add(chapter)
        await test_session.commit()
        await test_session.refresh(chapter)
        
        assert chapter.id is not None
        assert chapter.chapter_number == 1
        assert chapter.title == "Live animals"
        assert chapter.section_id == section.id
        assert chapter.section == section

    async def test_tariff_chapter_unique_constraint(self, test_session):
        """Test that chapter numbers must be unique."""
        section = TariffSection(section_number=1, title="Test Section")
        test_session.add(section)
        await test_session.commit()
        await test_session.refresh(section)
        
        chapter1 = TariffChapter(
            chapter_number=1,
            title="Live animals",
            section_id=section.id
        )
        test_session.add(chapter1)
        await test_session.commit()
        
        chapter2 = TariffChapter(
            chapter_number=1,
            title="Duplicate chapter",
            section_id=section.id
        )
        test_session.add(chapter2)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_tariff_chapter_section_relationship(self, test_session):
        """Test chapter-section relationship."""
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
        
        # Test relationships
        assert chapter.section == section
        assert chapter in section.chapters

    async def test_tariff_chapter_string_representations(self, test_session):
        """Test string representation methods."""
        chapter = TariffChapter(
            chapter_number=1,
            title="Live animals",
            section_id=1
        )
        
        repr_str = repr(chapter)
        assert "TariffChapter" in repr_str
        assert "chapter_number=1" in repr_str
        
        str_repr = str(chapter)
        assert "Chapter 01: Live animals" == str_repr

    async def test_tariff_chapter_cascade_delete(self, test_session):
        """Test cascade delete from section to chapters."""
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
        
        # Delete section
        await test_session.delete(section)
        await test_session.commit()
        
        # Check that chapter is also deleted
        result = await test_session.execute(
            select(TariffChapter).where(TariffChapter.chapter_number == 1)
        )
        remaining_chapter = result.scalar_one_or_none()
        assert remaining_chapter is None


@pytest.mark.database
@pytest.mark.unit
class TestTradeAgreement:
    """Test cases for TradeAgreement model."""

    async def test_create_trade_agreement(self, test_session):
        """Test creating a trade agreement."""
        agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Australia-United States Free Trade Agreement",
            entry_force_date=date(2005, 1, 1),
            status="active",
            agreement_url="https://example.com/ausfta"
        )
        
        test_session.add(agreement)
        await test_session.commit()
        await test_session.refresh(agreement)
        
        assert agreement.fta_code == "AUSFTA"
        assert agreement.full_name == "Australia-United States Free Trade Agreement"
        assert agreement.entry_force_date == date(2005, 1, 1)
        assert agreement.status == "active"
        assert agreement.created_at is not None

    async def test_trade_agreement_unique_constraint(self, test_session):
        """Test that FTA codes must be unique."""
        agreement1 = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Australia-United States Free Trade Agreement"
        )
        test_session.add(agreement1)
        await test_session.commit()
        
        agreement2 = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Duplicate agreement"
        )
        test_session.add(agreement2)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_trade_agreement_properties(self, test_session):
        """Test trade agreement properties."""
        # Test active agreement
        active_agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Australia-United States Free Trade Agreement",
            status="active",
            entry_force_date=date(2005, 1, 1)
        )
        
        assert active_agreement.is_active is True
        assert active_agreement.is_in_force is True
        
        # Test inactive agreement
        inactive_agreement = TradeAgreement(
            fta_code="INACTIVE",
            full_name="Inactive Agreement",
            status="suspended",
            entry_force_date=date(2030, 1, 1)  # Future date
        )
        
        assert inactive_agreement.is_active is False
        assert inactive_agreement.is_in_force is False
        
        # Test agreement without entry force date
        no_date_agreement = TradeAgreement(
            fta_code="NODATE",
            full_name="No Date Agreement",
            status="active"
        )
        
        assert no_date_agreement.is_in_force is False

    async def test_trade_agreement_string_representations(self, test_session):
        """Test string representation methods."""
        agreement = TradeAgreement(
            fta_code="AUSFTA",
            full_name="Australia-United States Free Trade Agreement"
        )
        
        repr_str = repr(agreement)
        assert "TradeAgreement" in repr_str
        assert "AUSFTA" in repr_str
        
        str_repr = str(agreement)
        assert "AUSFTA: Australia-United States Free Trade Agreement" == str_repr


@pytest.mark.database
@pytest.mark.unit
class TestTariffHierarchyIntegration:
    """Test integration between tariff codes and hierarchy models."""

    async def test_complete_hierarchy_creation(self, test_session):
        """Test creating a complete tariff hierarchy."""
        # Create section
        section = TariffSection(
            section_number=1,
            title="Live Animals; Animal Products",
            chapter_range="01-05"
        )
        test_session.add(section)
        await test_session.commit()
        await test_session.refresh(section)
        
        # Create chapter
        chapter = TariffChapter(
            chapter_number=1,
            title="Live animals",
            section_id=section.id
        )
        test_session.add(chapter)
        await test_session.commit()
        await test_session.refresh(chapter)
        
        # Create tariff codes at different levels
        chapter_code = TariffCode(
            hs_code="01",
            description="Live animals",
            level=2,
            section_id=section.id,
            chapter_id=chapter.id,
            is_active=True
        )
        test_session.add(chapter_code)
        
        heading_code = TariffCode(
            hs_code="0101",
            description="Live horses, asses, mules and hinnies",
            level=4,
            parent_code="01",
            section_id=section.id,
            chapter_id=chapter.id,
            is_active=True
        )
        test_session.add(heading_code)
        
        statistical_code = TariffCode(
            hs_code="0101010000",
            description="Live horses for breeding purposes",
            level=10,
            parent_code="0101",
            section_id=section.id,
            chapter_id=chapter.id,
            is_active=True
        )
        test_session.add(statistical_code)
        
        await test_session.commit()
        await test_session.refresh(chapter_code)
        await test_session.refresh(heading_code)
        await test_session.refresh(statistical_code)
        
        # Test relationships
        assert chapter_code.section == section
        assert chapter_code.chapter == chapter
        assert heading_code.parent == chapter_code
        assert statistical_code.parent == heading_code
        
        # Test hierarchy path
        path = statistical_code.get_hierarchy_path()
        assert path == ["01", "0101", "0101010000"]

    async def test_tariff_code_section_chapter_relationships(self, test_session):
        """Test tariff code relationships with sections and chapters."""
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
        
        # Test relationships
        assert tariff_code.section == section
        assert tariff_code.chapter == chapter
        assert tariff_code in section.tariff_codes
        assert tariff_code in chapter.tariff_codes