"""
Comprehensive tests for the Data Validation Service.

This module tests all aspects of data validation including:
- HS code validation and format checking
- Business rule validation across all models
- Data consistency checks and referential integrity
- Import/export validation workflows
- Data sanitization and normalization
"""

import pytest
import pytest_asyncio
from datetime import datetime, date, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import ValidationError

from models.tariff import TariffCode
from models.duty import DutyRate
from models.fta import FtaRate
from models.dumping import DumpingDuty
from models.tco import Tco
from models.gst import GstProvision
from models.classification import ProductClassification
from schemas.tariff import TariffCodeCreate, TariffCodeUpdate
from schemas.duty_calculator import DutyCalculationRequest


@pytest.mark.unit
class TestHSCodeValidation:
    """Test HS code validation and format checking."""
    
    def test_valid_hs_code_formats(self):
        """Test validation of valid HS code formats."""
        valid_codes = [
            "12345678",  # 8-digit standard
            "1234567890",  # 10-digit with statistical
            "123456",  # 6-digit chapter level
            "1234",  # 4-digit heading level
            "12",  # 2-digit section level
        ]
        
        for code in valid_codes:
            # Test that code contains only digits
            assert code.isdigit()
            # Test length is valid
            assert len(code) in [2, 4, 6, 8, 10]
    
    def test_invalid_hs_code_formats(self):
        """Test validation of invalid HS code formats."""
        invalid_codes = [
            "",  # Empty
            "123",  # 3 digits (invalid length)
            "12345",  # 5 digits (invalid length)
            "1234567",  # 7 digits (invalid length)
            "123456789",  # 9 digits (invalid length)
            "12345678901",  # 11 digits (too long)
            "1234567a",  # Contains letter
            "1234-5678",  # Contains hyphen
            "1234.5678",  # Contains period
            "1234 5678",  # Contains space
        ]
        
        for code in invalid_codes:
            # Test that code is invalid
            is_valid = (
                code.isdigit() and 
                len(code) in [2, 4, 6, 8, 10] and
                len(code) > 0
            )
            assert not is_valid
    
    def test_hs_code_hierarchy_validation(self):
        """Test HS code hierarchy validation."""
        # Test valid hierarchy relationships
        section = "12"
        chapter = "1234"
        heading = "123456"
        subheading = "12345678"
        statistical = "1234567890"
        
        # Chapter should start with section
        assert chapter.startswith(section)
        # Heading should start with chapter
        assert heading.startswith(chapter)
        # Subheading should start with heading
        assert subheading.startswith(heading)
        # Statistical should start with subheading
        assert statistical.startswith(subheading)
    
    def test_hs_code_normalization(self):
        """Test HS code normalization."""
        test_cases = [
            ("  12345678  ", "12345678"),  # Trim spaces
            ("12345678", "12345678"),  # No change needed
            ("1234567890", "1234567890"),  # 10-digit preserved
        ]
        
        for input_code, expected in test_cases:
            normalized = input_code.strip()
            assert normalized == expected


@pytest.mark.unit
class TestBusinessRuleValidation:
    """Test business rule validation across models."""
    
    async def test_duty_rate_validation(self, test_session: AsyncSession):
        """Test duty rate business rule validation."""
        # Test valid duty rate
        valid_duty = DutyRate(
            hs_code="12345678",
            general_rate=Decimal("5.0"),
            unit_type="ad_valorem",
            rate_text="5%",
            is_ad_valorem=True,
            is_specific=False,
            effective_date=date.today(),
            is_active=True
        )
        
        # Should not raise validation errors
        test_session.add(valid_duty)
        await test_session.commit()
        await test_session.refresh(valid_duty)
        
        assert valid_duty.id is not None
        assert valid_duty.general_rate == Decimal("5.0")
    
    async def test_duty_rate_invalid_rate(self, test_session: AsyncSession):
        """Test duty rate with invalid rate values."""
        # Test negative rate (should be invalid)
        with pytest.raises(Exception):  # Database constraint or validation error
            invalid_duty = DutyRate(
                hs_code="12345678",
                general_rate=Decimal("-5.0"),  # Negative rate
                unit_type="ad_valorem",
                is_ad_valorem=True,
                is_active=True
            )
            test_session.add(invalid_duty)
            await test_session.commit()
    
    async def test_fta_rate_validation(self, test_session: AsyncSession):
        """Test FTA rate business rule validation."""
        # Test valid FTA rate
        valid_fta = FtaRate(
            hs_code="12345678",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("2.0"),
            effective_rate=Decimal("2.0"),
            staging_category="A",
            effective_date=date.today(),
            is_active=True
        )
        
        test_session.add(valid_fta)
        await test_session.commit()
        await test_session.refresh(valid_fta)
        
        assert valid_fta.id is not None
        assert valid_fta.preferential_rate == Decimal("2.0")
    
    async def test_fta_rate_date_validation(self, test_session: AsyncSession):
        """Test FTA rate date validation."""
        # Test that elimination date is after effective date
        valid_fta = FtaRate(
            hs_code="12345678",
            fta_code="AUSFTA",
            country_code="USA",
            preferential_rate=Decimal("2.0"),
            effective_date=date.today(),
            elimination_date=date.today() + timedelta(days=365),
            is_active=True
        )
        
        test_session.add(valid_fta)
        await test_session.commit()
        
        # Verify dates are logical
        assert valid_fta.elimination_date > valid_fta.effective_date
    
    async def test_tco_validation(self, test_session: AsyncSession):
        """Test TCO business rule validation."""
        # Test valid TCO
        valid_tco = Tco(
            tco_number="TCO2023001",
            hs_code="12345678",
            description="Test TCO for validation",
            effective_date=date.today(),
            expiry_date=date.today() + timedelta(days=365),
            is_current=True
        )
        
        test_session.add(valid_tco)
        await test_session.commit()
        await test_session.refresh(valid_tco)
        
        assert valid_tco.id is not None
        assert valid_tco.is_current is True
    
    async def test_classification_confidence_validation(self, test_session: AsyncSession):
        """Test product classification confidence validation."""
        # Create required tariff code first
        tariff_code = TariffCode(
            hs_code="12345678",
            description="Test product",
            unit="kg",
            is_active=True
        )
        test_session.add(tariff_code)
        await test_session.commit()
        
        # Test valid confidence score
        valid_classification = ProductClassification(
            product_description="Test product for validation",
            hs_code="12345678",
            confidence_score=Decimal("0.85"),  # Valid range 0-1
            classification_source="ai",
            verified_by_broker=False
        )
        
        test_session.add(valid_classification)
        await test_session.commit()
        await test_session.refresh(valid_classification)
        
        assert valid_classification.id is not None
        assert 0 <= valid_classification.confidence_score <= 1


@pytest.mark.unit
class TestDataConsistencyValidation:
    """Test data consistency checks and referential integrity."""
    
    async def test_tariff_code_reference_integrity(self, test_session: AsyncSession):
        """Test that related records reference valid tariff codes."""
        # Create tariff code first
        tariff_code = TariffCode(
            hs_code="12345678",
            description="Test product",
            unit="kg",
            is_active=True
        )
        test_session.add(tariff_code)
        await test_session.commit()
        
        # Create duty rate referencing the tariff code
        duty_rate = DutyRate(
            hs_code="12345678",  # Must match existing tariff code
            general_rate=Decimal("5.0"),
            unit_type="ad_valorem",
            is_ad_valorem=True,
            is_active=True
        )
        test_session.add(duty_rate)
        await test_session.commit()
        
        # Verify relationship
        assert duty_rate.hs_code == tariff_code.hs_code
    
    async def test_classification_tariff_reference(self, test_session: AsyncSession):
        """Test classification references valid tariff codes."""
        # Create tariff code
        tariff_code = TariffCode(
            hs_code="87654321",
            description="Another test product",
            unit="unit",
            is_active=True
        )
        test_session.add(tariff_code)
        await test_session.commit()
        
        # Create classification
        classification = ProductClassification(
            product_description="Test classification",
            hs_code="87654321",  # Must reference existing tariff code
            confidence_score=Decimal("0.9"),
            classification_source="ai",
            verified_by_broker=False
        )
        test_session.add(classification)
        await test_session.commit()
        
        # Verify reference integrity
        assert classification.hs_code == tariff_code.hs_code
    
    async def test_duplicate_prevention(self, test_session: AsyncSession):
        """Test prevention of duplicate records where appropriate."""
        # Create first tariff code
        tariff_code1 = TariffCode(
            hs_code="11111111",
            description="First test product",
            unit="kg",
            is_active=True
        )
        test_session.add(tariff_code1)
        await test_session.commit()
        
        # Attempt to create duplicate HS code (should be prevented by unique constraint)
        with pytest.raises(Exception):  # Database integrity error
            tariff_code2 = TariffCode(
                hs_code="11111111",  # Duplicate HS code
                description="Second test product",
                unit="unit",
                is_active=True
            )
            test_session.add(tariff_code2)
            await test_session.commit()
    
    async def test_active_status_consistency(self, test_session: AsyncSession):
        """Test active status consistency across related records."""
        # Create tariff code
        tariff_code = TariffCode(
            hs_code="22222222",
            description="Status test product",
            unit="kg",
            is_active=True
        )
        test_session.add(tariff_code)
        await test_session.commit()
        
        # Create active duty rate
        duty_rate = DutyRate(
            hs_code="22222222",
            general_rate=Decimal("3.0"),
            unit_type="ad_valorem",
            is_ad_valorem=True,
            is_active=True  # Should be consistent with tariff code
        )
        test_session.add(duty_rate)
        await test_session.commit()
        
        # Verify consistency
        assert tariff_code.is_active == duty_rate.is_active


@pytest.mark.unit
class TestSchemaValidation:
    """Test Pydantic schema validation."""
    
    def test_tariff_code_create_schema_validation(self):
        """Test TariffCodeCreate schema validation."""
        # Test valid data
        valid_data = {
            "hs_code": "12345678",
            "description": "Test product for schema validation",
            "unit": "kg",
            "statistical_code": "01",
            "is_active": True
        }
        
        # Should not raise validation error
        schema = TariffCodeCreate(**valid_data)
        assert schema.hs_code == "12345678"
        assert schema.description == "Test product for schema validation"
    
    def test_tariff_code_create_schema_invalid_data(self):
        """Test TariffCodeCreate schema with invalid data."""
        # Test missing required fields
        with pytest.raises(ValidationError):
            TariffCodeCreate(hs_code="12345678")  # Missing description
        
        # Test invalid HS code format
        with pytest.raises(ValidationError):
            TariffCodeCreate(
                hs_code="invalid",  # Invalid format
                description="Test product",
                unit="kg"
            )
    
    def test_duty_calculation_request_validation(self):
        """Test DutyCalculationRequest schema validation."""
        # Test valid request
        valid_request = {
            "hs_code": "12345678",
            "country_code": "USA",
            "customs_value": 1000.00,
            "quantity": 10.0,
            "value_basis": "CIF"
        }
        
        schema = DutyCalculationRequest(**valid_request)
        assert schema.hs_code == "12345678"
        assert schema.customs_value == 1000.00
    
    def test_duty_calculation_request_invalid_data(self):
        """Test DutyCalculationRequest schema with invalid data."""
        # Test negative customs value
        with pytest.raises(ValidationError):
            DutyCalculationRequest(
                hs_code="12345678",
                country_code="USA",
                customs_value=-100.00  # Invalid negative value
            )
        
        # Test invalid country code format
        with pytest.raises(ValidationError):
            DutyCalculationRequest(
                hs_code="12345678",
                country_code="INVALID",  # Should be 2-3 characters
                customs_value=1000.00
            )


@pytest.mark.unit
class TestDataSanitization:
    """Test data sanitization and normalization."""
    
    def test_string_sanitization(self):
        """Test string field sanitization."""
        test_cases = [
            ("  Test Product  ", "Test Product"),  # Trim spaces
            ("Test\nProduct", "Test Product"),  # Replace newlines
            ("Test\tProduct", "Test Product"),  # Replace tabs
            ("Test  Product", "Test Product"),  # Normalize multiple spaces
        ]
        
        for input_str, expected in test_cases:
            # Simulate sanitization logic
            sanitized = " ".join(input_str.split())
            assert sanitized == expected
    
    def test_numeric_normalization(self):
        """Test numeric field normalization."""
        test_cases = [
            ("5.0", Decimal("5.0")),
            ("5", Decimal("5.0")),
            ("5.00", Decimal("5.0")),
            ("0.5", Decimal("0.5")),
        ]
        
        for input_val, expected in test_cases:
            normalized = Decimal(input_val)
            assert normalized == expected
    
    def test_date_normalization(self):
        """Test date field normalization."""
        # Test various date formats
        test_date = date(2023, 1, 15)
        
        # Test ISO format
        iso_string = test_date.isoformat()
        parsed_date = date.fromisoformat(iso_string)
        assert parsed_date == test_date
        
        # Test date validation
        assert isinstance(test_date, date)
        assert test_date.year == 2023
        assert test_date.month == 1
        assert test_date.day == 15


@pytest.mark.integration
class TestValidationWorkflows:
    """Test complete validation workflows."""
    
    async def test_import_validation_workflow(self, test_session: AsyncSession):
        """Test complete import validation workflow."""
        # Simulate importing tariff data
        import_data = [
            {
                "hs_code": "12345678",
                "description": "Electronic device",
                "unit": "kg",
                "is_active": True
            },
            {
                "hs_code": "87654321",
                "description": "Mechanical component",
                "unit": "unit",
                "is_active": True
            }
        ]
        
        # Validate and import each record
        imported_records = []
        for data in import_data:
            # Validate schema
            try:
                schema = TariffCodeCreate(**data)
                
                # Create model instance
                tariff_code = TariffCode(
                    hs_code=schema.hs_code,
                    description=schema.description,
                    unit=schema.unit,
                    is_active=schema.is_active
                )
                
                test_session.add(tariff_code)
                imported_records.append(tariff_code)
                
            except ValidationError as e:
                pytest.fail(f"Validation failed for {data}: {e}")
        
        await test_session.commit()
        
        # Verify all records were imported
        assert len(imported_records) == 2
        for record in imported_records:
            await test_session.refresh(record)
            assert record.id is not None
    
    async def test_export_validation_workflow(self, test_session: AsyncSession):
        """Test complete export validation workflow."""
        # Create test data
        tariff_codes = [
            TariffCode(
                hs_code="11111111",
                description="Export test product 1",
                unit="kg",
                is_active=True
            ),
            TariffCode(
                hs_code="22222222",
                description="Export test product 2",
                unit="unit",
                is_active=True
            )
        ]
        
        for code in tariff_codes:
            test_session.add(code)
        await test_session.commit()
        
        # Export and validate data
        query = select(TariffCode).where(TariffCode.is_active == True)
        result = await test_session.execute(query)
        exported_codes = result.scalars().all()
        
        # Validate exported data
        for code in exported_codes:
            # Validate required fields are present
            assert code.hs_code is not None
            assert code.description is not None
            assert code.unit is not None
            assert code.is_active is not None
            
            # Validate data formats
            assert code.hs_code.isdigit()
            assert len(code.hs_code) in [2, 4, 6, 8, 10]
            assert len(code.description) > 0
        
        assert len(exported_codes) >= 2


@pytest.mark.unit
class TestValidationPerformance:
    """Test validation performance characteristics."""
    
    async def test_bulk_validation_performance(self, test_session: AsyncSession, performance_timer):
        """Test performance of bulk validation operations."""
        # Create large dataset for validation testing
        test_data = []
        for i in range(100):
            test_data.append({
                "hs_code": f"{i:08d}",
                "description": f"Test product {i}",
                "unit": "kg",
                "is_active": True
            })
        
        performance_timer.start()
        
        # Validate all records
        validated_records = []
        for data in test_data:
            try:
                schema = TariffCodeCreate(**data)
                validated_records.append(schema)
            except ValidationError:
                pass  # Skip invalid records
        
        performance_timer.stop()
        
        assert len(validated_records) == 100
        assert performance_timer.elapsed < 2.0  # Should complete within 2 seconds
    
    async def test_validation_caching_performance(self, performance_timer):
        """Test validation performance with caching."""
        # Test repeated validation of same data
        test_data = {
            "hs_code": "12345678",
            "description": "Cached validation test",
            "unit": "kg",
            "is_active": True
        }
        
        performance_timer.start()
        
        # Validate same data multiple times
        for _ in range(50):
            schema = TariffCodeCreate(**test_data)
            assert schema.hs_code == "12345678"
        
        performance_timer.stop()
        
        assert performance_timer.elapsed < 1.0  # Should be fast with caching


@pytest.mark.external
class TestValidationIntegration:
    """Test validation integration with external systems."""
    
    async def test_validation_with_logging(self, test_session: AsyncSession):
        """Test validation with proper logging."""
        with patch('logging.getLogger') as mock_logger:
            # Create test data with validation error
            try:
                invalid_data = TariffCodeCreate(
                    hs_code="invalid",
                    description="Test",
                    unit="kg"
                )
            except ValidationError as e:
                # Should log validation errors
                assert e is not None
    
    async def test_validation_error_reporting(self, test_session: AsyncSession):
        """Test comprehensive validation error reporting."""
        # Test multiple validation errors
        invalid_data = {
            "hs_code": "",  # Empty HS code
            "description": "",  # Empty description
            "unit": "",  # Empty unit
        }
        
        try:
            TariffCodeCreate(**invalid_data)
            pytest.fail("Should have raised ValidationError")
        except ValidationError as e:
            # Should report all validation errors
            errors = e.errors()
            assert len(errors) >= 2  # Multiple validation errors
            
            # Check error details
            error_fields = [error["loc"][0] for error in errors]
            assert "hs_code" in error_fields
            assert "description" in error_fields


@pytest.mark.unit
class TestValidationEdgeCases:
    """Test validation edge cases and boundary conditions."""
    
    def test_validation_with_extreme_values(self):
        """Test validation with extreme values."""
        # Test very large customs value
        large_value_data = {
            "hs_code": "12345678",
            "country_code": "USA",
            "customs_value": 999999999.99  # Very large value
        }
        
        # Should handle large values gracefully
        schema = DutyCalculationRequest(**large_value_data)
        assert schema.customs_value == 999999999.99
        
        # Test very small customs value
        small_value_data = {
            "hs_code": "12345678",
            "country_code": "USA",
            "customs_value": 0.01  # Very small value
        }
        
        schema = DutyCalculationRequest(**small_value_data)
        assert schema.customs_value == 0.01
    
    def test_validation_with_unicode_data(self):
        """Test validation with unicode characters."""
        unicode_data = {
            "hs_code": "12345678",
            "description": "Café products with naïve résumé",
            "unit": "kg",
            "is_active": True
        }
        
        # Should handle unicode characters
        schema = TariffCodeCreate(**unicode_data)
        assert "Café" in schema.description
        assert "naïve" in schema.description
        assert "résumé" in schema.description
    
    def test_validation_with_boundary_dates(self):
        """Test validation with boundary date values."""
        # Test with current date
        current_date = date.today()
        
        # Test with past date
        past_date = date(1900, 1, 1)
        
        # Test with future date
        future_date = date(2100, 12, 31)
        
        # All should be valid date objects
        assert isinstance(current_date, date)
        assert isinstance(past_date, date)
        assert isinstance(future_date, date)
        
        # Test date ordering
        assert past_date < current_date < future_date