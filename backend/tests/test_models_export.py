"""
Unit tests for ExportCode and ProductClassification models.

This module tests the export classification and product classification models
including validation, relationships, and business logic.
"""

import pytest
from datetime import datetime
from decimal import Decimal
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from models import ExportCode, ProductClassification, TariffCode
from tests.utils.test_helpers import TestDataFactory, DatabaseTestHelper


@pytest.mark.database
@pytest.mark.unit
class TestExportCode:
    """Test cases for ExportCode model."""

    async def test_create_export_code(self, test_session):
        """Test creating a basic export code."""
        # Create corresponding import tariff code
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        export_code = ExportCode(
            ahecc_code="0101010000",
            description="Live horses for breeding purposes - export classification",
            statistical_unit="Number",
            corresponding_import_code="0101010000",
            is_active=True
        )
        
        test_session.add(export_code)
        await test_session.commit()
        await test_session.refresh(export_code)
        
        assert export_code.id is not None
        assert export_code.ahecc_code == "0101010000"
        assert export_code.description == "Live horses for breeding purposes - export classification"
        assert export_code.statistical_unit == "Number"
        assert export_code.corresponding_import_code == "0101010000"
        assert export_code.is_active is True
        assert export_code.created_at is not None

    async def test_export_code_without_import_equivalent(self, test_session):
        """Test creating export code without corresponding import code."""
        export_code = ExportCode(
            ahecc_code="9999999999",
            description="Export-only commodity",
            statistical_unit="Tonnes",
            is_active=True
        )
        
        test_session.add(export_code)
        await test_session.commit()
        await test_session.refresh(export_code)
        
        assert export_code.id is not None
        assert export_code.corresponding_import_code is None
        assert export_code.corresponding_import_tariff is None

    async def test_export_code_foreign_key_constraint(self, test_session):
        """Test foreign key constraint to tariff codes."""
        export_code = ExportCode(
            ahecc_code="0101010000",
            description="Test export code",
            corresponding_import_code="9999999999"  # Non-existent HS code
        )
        
        test_session.add(export_code)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_export_code_relationship(self, test_session):
        """Test relationship with corresponding import tariff code."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        export_code = ExportCode(
            ahecc_code="0101010000",
            description="Test export code",
            corresponding_import_code="0101010000"
        )
        
        test_session.add(export_code)
        await test_session.commit()
        await test_session.refresh(export_code)
        
        # Test relationship
        assert export_code.corresponding_import_tariff == tariff_code
        assert export_code in tariff_code.export_codes

    async def test_export_code_has_import_equivalent(self, test_session):
        """Test has_import_equivalent method."""
        # Test export code with import equivalent
        export_with_import = ExportCode(
            ahecc_code="0101010000",
            description="Test export code",
            corresponding_import_code="0101010000"
        )
        
        assert export_with_import.has_import_equivalent() is True
        
        # Test export code without import equivalent
        export_without_import = ExportCode(
            ahecc_code="9999999999",
            description="Export-only commodity"
        )
        
        assert export_without_import.has_import_equivalent() is False

    async def test_export_code_statistical_info(self, test_session):
        """Test get_statistical_info method."""
        # Test with statistical unit
        export_with_unit = ExportCode(
            ahecc_code="0101010000",
            description="Test export code",
            statistical_unit="Number"
        )
        
        assert export_with_unit.get_statistical_info() == "Number"
        
        # Test without statistical unit
        export_without_unit = ExportCode(
            ahecc_code="0101010000",
            description="Test export code"
        )
        
        assert export_without_unit.get_statistical_info() == "No unit specified"

    async def test_export_code_is_currently_active(self, test_session):
        """Test is_currently_active method."""
        # Test active export code
        active_export = ExportCode(
            ahecc_code="0101010000",
            description="Active export code",
            is_active=True
        )
        
        assert active_export.is_currently_active() is True
        
        # Test inactive export code
        inactive_export = ExportCode(
            ahecc_code="0101010000",
            description="Inactive export code",
            is_active=False
        )
        
        assert inactive_export.is_currently_active() is False

    async def test_export_code_string_representations(self, test_session):
        """Test string representation methods."""
        export_code = ExportCode(
            ahecc_code="0101010000",
            description="Live horses for breeding purposes - export classification"
        )
        
        repr_str = repr(export_code)
        assert "ExportCode" in repr_str
        assert "0101010000" in repr_str
        assert "Live horses for breeding purposes - export" in repr_str
        
        str_repr = str(export_code)
        assert "0101010000: Live horses for breeding purposes - export classification" == str_repr

    async def test_export_code_set_null_on_delete(self, test_session):
        """Test SET NULL behavior when corresponding import tariff is deleted."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        export_code = ExportCode(
            ahecc_code="0101010000",
            description="Test export code",
            corresponding_import_code="0101010000"
        )
        
        test_session.add(export_code)
        await test_session.commit()
        await test_session.refresh(export_code)
        
        # Delete tariff code
        await test_session.delete(tariff_code)
        await test_session.commit()
        await test_session.refresh(export_code)
        
        # Check that export code still exists but corresponding_import_code is NULL
        assert export_code.corresponding_import_code is None
        assert export_code.corresponding_import_tariff is None

    async def test_export_code_multiple_exports_per_import(self, test_session):
        """Test multiple export codes referencing the same import code."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Create multiple export codes for the same import code
        export_code1 = ExportCode(
            ahecc_code="0101010001",
            description="Live horses - breeding stock",
            corresponding_import_code="0101010000"
        )
        
        export_code2 = ExportCode(
            ahecc_code="0101010002",
            description="Live horses - racing stock",
            corresponding_import_code="0101010000"
        )
        
        test_session.add_all([export_code1, export_code2])
        await test_session.commit()
        await test_session.refresh(export_code1)
        await test_session.refresh(export_code2)
        
        # Verify both export codes are associated with the tariff code
        assert len(tariff_code.export_codes) == 2
        assert export_code1 in tariff_code.export_codes
        assert export_code2 in tariff_code.export_codes


@pytest.mark.database
@pytest.mark.unit
class TestProductClassification:
    """Test cases for ProductClassification model."""

    async def test_create_product_classification(self, test_session):
        """Test creating a basic product classification."""
        # Create tariff code first
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        classification = ProductClassification(
            product_description="Live breeding horses imported from Ireland",
            hs_code="0101010000",
            confidence_score=0.95,
            classification_source="ai",
            verified_by_broker=False
        )
        
        test_session.add(classification)
        await test_session.commit()
        await test_session.refresh(classification)
        
        assert classification.id is not None
        assert classification.product_description == "Live breeding horses imported from Ireland"
        assert classification.hs_code == "0101010000"
        assert classification.confidence_score == 0.95
        assert classification.classification_source == "ai"
        assert classification.verified_by_broker is False
        assert classification.created_at is not None

    async def test_product_classification_foreign_key_constraint(self, test_session):
        """Test foreign key constraint to tariff codes."""
        classification = ProductClassification(
            product_description="Test product",
            hs_code="9999999999",  # Non-existent HS code
            confidence_score=0.80
        )
        
        test_session.add(classification)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_product_classification_confidence_constraint(self, test_session):
        """Test confidence score constraint (0.00-1.00)."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Test invalid confidence score > 1.00
        classification_high = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=1.50  # Invalid - too high
        )
        
        test_session.add(classification_high)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()
        
        await test_session.rollback()
        
        # Test invalid confidence score < 0.00
        classification_low = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=-0.10  # Invalid - negative
        )
        
        test_session.add(classification_low)
        
        with pytest.raises(IntegrityError):
            await test_session.commit()

    async def test_product_classification_relationship(self, test_session):
        """Test relationship with tariff code."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        classification = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=0.85
        )
        
        test_session.add(classification)
        await test_session.commit()
        await test_session.refresh(classification)
        
        # Test relationship
        assert classification.tariff_code == tariff_code
        assert classification in tariff_code.product_classifications

    async def test_product_classification_confidence_level_description(self, test_session):
        """Test confidence level description method."""
        # Test high confidence
        high_confidence = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=0.95
        )
        
        assert high_confidence.confidence_level_description() == "High"
        
        # Test medium confidence
        medium_confidence = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=0.65
        )
        
        assert medium_confidence.confidence_level_description() == "Medium"
        
        # Test low confidence
        low_confidence = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=0.35
        )
        
        assert low_confidence.confidence_level_description() == "Low"
        
        # Test unknown confidence
        unknown_confidence = ProductClassification(
            product_description="Test product",
            hs_code="0101010000"
        )
        
        assert unknown_confidence.confidence_level_description() == "Unknown"

    async def test_product_classification_verification_methods(self, test_session):
        """Test verification-related methods."""
        # Test verified classification
        verified_classification = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=0.75,
            verified_by_broker=True,
            broker_user_id=123
        )
        
        assert verified_classification.is_verified() is True
        assert verified_classification.needs_verification() is False
        
        # Test unverified high confidence classification
        high_confidence_unverified = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=0.95,
            verified_by_broker=False
        )
        
        assert high_confidence_unverified.is_verified() is False
        assert high_confidence_unverified.needs_verification() is False
        
        # Test unverified low confidence classification
        low_confidence_unverified = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=0.65,
            verified_by_broker=False
        )
        
        assert low_confidence_unverified.is_verified() is False
        assert low_confidence_unverified.needs_verification() is True
        
        # Test classification with no confidence score
        no_confidence = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            verified_by_broker=False
        )
        
        assert no_confidence.needs_verification() is True

    async def test_product_classification_confidence_percentage(self, test_session):
        """Test confidence percentage formatting."""
        # Test with confidence score
        classification_with_score = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=0.85
        )
        
        assert classification_with_score.confidence_percentage() == "85%"
        
        # Test with no confidence score
        classification_no_score = ProductClassification(
            product_description="Test product",
            hs_code="0101010000"
        )
        
        assert classification_no_score.confidence_percentage() == "N/A"
        
        # Test edge cases
        perfect_confidence = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=1.00
        )
        
        assert perfect_confidence.confidence_percentage() == "100%"
        
        zero_confidence = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=0.00
        )
        
        assert zero_confidence.confidence_percentage() == "0%"

    async def test_product_classification_string_representations(self, test_session):
        """Test string representation methods."""
        classification = ProductClassification(
            product_description="Live breeding horses imported from Ireland for agricultural purposes",
            hs_code="0101010000",
            confidence_score=0.95,
            verified_by_broker=True
        )
        
        repr_str = repr(classification)
        assert "ProductClassification" in repr_str
        assert "0101010000" in repr_str
        assert "confidence=0.95" in repr_str
        assert "verified=True" in repr_str
        assert "Live breeding horses imported from Ireland" in repr_str
        
        str_repr = str(classification)
        assert "0101010000: Live breeding horses imported from Ireland for agricultural purposes..." == str_repr

    async def test_product_classification_cascade_delete(self, test_session):
        """Test cascade delete when tariff code is deleted."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        classification = ProductClassification(
            product_description="Test product",
            hs_code="0101010000",
            confidence_score=0.85
        )
        
        test_session.add(classification)
        await test_session.commit()
        await test_session.refresh(classification)
        
        classification_id = classification.id
        
        # Delete tariff code
        await test_session.delete(tariff_code)
        await test_session.commit()
        
        # Check that classification is also deleted
        result = await test_session.execute(
            select(ProductClassification).where(ProductClassification.id == classification_id)
        )
        remaining_classification = result.scalar_one_or_none()
        assert remaining_classification is None

    async def test_product_classification_multiple_per_tariff(self, test_session):
        """Test multiple classifications for the same tariff code."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Create multiple classifications for the same HS code
        classification1 = ProductClassification(
            product_description="Live breeding horses from Ireland",
            hs_code="0101010000",
            confidence_score=0.95,
            classification_source="ai"
        )
        
        classification2 = ProductClassification(
            product_description="Racing horses for competition",
            hs_code="0101010000",
            confidence_score=0.88,
            classification_source="broker",
            verified_by_broker=True
        )
        
        test_session.add_all([classification1, classification2])
        await test_session.commit()
        await test_session.refresh(classification1)
        await test_session.refresh(classification2)
        
        # Verify both classifications are associated with the tariff code
        assert len(tariff_code.product_classifications) == 2
        assert classification1 in tariff_code.product_classifications
        assert classification2 in tariff_code.product_classifications

    async def test_product_classification_edge_cases(self, test_session):
        """Test edge cases for product classifications."""
        tariff_code = await DatabaseTestHelper.create_tariff_code(
            test_session,
            hs_code="0101010000"
        )
        
        # Test classification with minimal data
        minimal_classification = ProductClassification(
            product_description="Minimal product description",
            hs_code="0101010000"
        )
        
        test_session.add(minimal_classification)
        await test_session.commit()
        await test_session.refresh(minimal_classification)
        
        assert minimal_classification.id is not None
        assert minimal_classification.confidence_score is None
        assert minimal_classification.classification_source is None
        assert minimal_classification.verified_by_broker is False
        assert minimal_classification.broker_user_id is None
        
        # Test boundary confidence scores
        boundary_classification = ProductClassification(
            product_description="Boundary test product",
            hs_code="0101010000",
            confidence_score=0.80  # Exactly at the verification threshold
        )
        
        test_session.add(boundary_classification)
        await test_session.commit()
        await test_session.refresh(boundary_classification)
        
        assert boundary_classification.confidence_level_description() == "Medium"
        assert boundary_classification.needs_verification() is False  # 0.8 is not < 0.8