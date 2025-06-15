"""
Validation script for Pydantic schemas.

This script validates that all Pydantic schemas work correctly with the SQLAlchemy models
and that the validation rules are functioning as expected.
"""

import sys
import traceback
from datetime import datetime, date
from decimal import Decimal
from typing import Dict, Any

# Add the backend directory to the Python path
sys.path.insert(0, '.')

def test_schema_imports():
    """Test that all schemas can be imported successfully."""
    print("Testing schema imports...")
    
    try:
        # Test common schemas
        from schemas.common import (
            BaseSchema, PaginationParams, PaginationMeta, SearchParams,
            ErrorResponse, SuccessResponse, HSCodeValidator, CountryCodeValidator,
            FTACodeValidator, RateValidator
        )
        print("✓ Common schemas imported successfully")
        
        # Test tariff schemas
        from schemas.tariff import (
            TariffCodeBase, TariffCodeCreate, TariffCodeUpdate, TariffCodeResponse,
            TariffCodeSummary, TariffTreeNode, TariffSearchRequest, TariffSearchResponse
        )
        print("✓ Tariff schemas imported successfully")
        
        # Test duty schemas
        from schemas.duty import (
            DutyRateBase, DutyRateCreate, DutyRateUpdate, DutyRateResponse,
            DutyCalculationRequest, DutyCalculationResult
        )
        print("✓ Duty schemas imported successfully")
        
        # Test FTA schemas
        from schemas.fta import (
            TradeAgreementBase, FtaRateBase, FtaRateCreate, FtaRateResponse,
            FtaRateCalculationRequest, FtaRateCalculationResult
        )
        print("✓ FTA schemas imported successfully")
        
        # Test response schemas
        from schemas.responses import (
            TariffDetailResponse, TariffTreeResponse, TariffSectionListResponse,
            SearchResultsResponse, RateComparisonResponse
        )
        print("✓ Response schemas imported successfully")
        
        # Test main package import
        from schemas import (
            TariffCodeResponse, DutyRateResponse, FtaRateResponse,
            ENDPOINT_SCHEMAS, VALIDATION_CONFIG
        )
        print("✓ Main package imports working")
        
        return True
        
    except Exception as e:
        print(f"✗ Import error: {e}")
        traceback.print_exc()
        return False


def test_validators():
    """Test the custom validators."""
    print("\nTesting validators...")
    
    try:
        from schemas.common import (
            HSCodeValidator, CountryCodeValidator, FTACodeValidator, RateValidator
        )
        
        # Test HS Code Validator
        print("Testing HS Code Validator...")
        
        # Valid HS codes
        valid_codes = ["01", "0101", "010121", "01012100", "0101210000"]
        for code in valid_codes:
            result = HSCodeValidator.validate_hs_code(code)
            assert result == code, f"Expected {code}, got {result}"
        print("✓ Valid HS codes passed")
        
        # Invalid HS codes
        invalid_codes = ["", "1", "123", "12345", "123456789", "12345678901"]
        for code in invalid_codes:
            try:
                HSCodeValidator.validate_hs_code(code)
                print(f"✗ Invalid HS code {code} should have failed")
                return False
            except ValueError:
                pass  # Expected
        print("✓ Invalid HS codes properly rejected")
        
        # Test Country Code Validator
        print("Testing Country Code Validator...")
        
        valid_countries = ["USA", "AUS", "CHN", "JPN"]
        for country in valid_countries:
            result = CountryCodeValidator.validate_country_code(country)
            assert result == country, f"Expected {country}, got {result}"
        print("✓ Valid country codes passed")
        
        # Test FTA Code Validator
        print("Testing FTA Code Validator...")
        
        valid_fta_codes = ["AUSFTA", "CPTPP", "RCEP"]
        for fta_code in valid_fta_codes:
            result = FTACodeValidator.validate_fta_code(fta_code)
            assert result == fta_code, f"Expected {fta_code}, got {result}"
        print("✓ Valid FTA codes passed")
        
        # Test Rate Validator
        print("Testing Rate Validator...")
        
        valid_rates = [0, 5.5, 10.25, 100.0]
        for rate in valid_rates:
            result = RateValidator.validate_rate(rate)
            assert result == Decimal(str(rate)), f"Expected {rate}, got {result}"
        print("✓ Valid rates passed")
        
        # Invalid rates
        invalid_rates = [-1, 1001]
        for rate in invalid_rates:
            try:
                RateValidator.validate_rate(rate)
                print(f"✗ Invalid rate {rate} should have failed")
                return False
            except ValueError:
                pass  # Expected
        print("✓ Invalid rates properly rejected")
        
        return True
        
    except Exception as e:
        print(f"✗ Validator error: {e}")
        traceback.print_exc()
        return False


def test_schema_validation():
    """Test schema validation with sample data."""
    print("\nTesting schema validation...")
    
    try:
        from schemas.tariff import TariffCodeCreate, TariffCodeResponse
        from schemas.duty import DutyRateCreate
        from schemas.fta import FtaRateCreate, TradeAgreementCreate
        
        # Test TariffCode schema
        print("Testing TariffCode schema...")
        
        valid_tariff_data = {
            "hs_code": "0101210000",
            "description": "Live horses - Pure-bred breeding animals",
            "unit_description": "Number (No.)",
            "parent_code": "01012100",
            "level": 10,
            "is_active": True
        }
        
        tariff_schema = TariffCodeCreate(**valid_tariff_data)
        assert tariff_schema.hs_code == "0101210000"
        assert tariff_schema.level == 10
        print("✓ Valid tariff code schema created")
        
        # Test invalid tariff data
        invalid_tariff_data = {
            "hs_code": "123",  # Invalid length
            "description": "Test",
            "level": 3  # Invalid level
        }
        
        try:
            TariffCodeCreate(**invalid_tariff_data)
            print("✗ Invalid tariff data should have failed")
            return False
        except ValueError:
            pass  # Expected
        print("✓ Invalid tariff data properly rejected")
        
        # Test DutyRate schema
        print("Testing DutyRate schema...")
        
        valid_duty_data = {
            "hs_code": "0101210000",
            "general_rate": Decimal("5.00"),
            "unit_type": "ad_valorem",
            "rate_text": "5%"
        }
        
        duty_schema = DutyRateCreate(**valid_duty_data)
        assert duty_schema.general_rate == Decimal("5.00")
        print("✓ Valid duty rate schema created")
        
        # Test FtaRate schema
        print("Testing FtaRate schema...")
        
        valid_fta_data = {
            "hs_code": "0101210000",
            "fta_code": "AUSFTA",
            "country_code": "USA",
            "preferential_rate": Decimal("0.00"),
            "staging_category": "A",
            "effective_date": date(2005, 1, 1)
        }
        
        fta_schema = FtaRateCreate(**valid_fta_data)
        assert fta_schema.country_code == "USA"
        print("✓ Valid FTA rate schema created")
        
        # Test TradeAgreement schema
        print("Testing TradeAgreement schema...")
        
        valid_agreement_data = {
            "fta_code": "AUSFTA",
            "full_name": "Australia-United States Free Trade Agreement",
            "entry_force_date": date(2005, 1, 1),
            "status": "active"
        }
        
        agreement_schema = TradeAgreementCreate(**valid_agreement_data)
        assert agreement_schema.fta_code == "AUSFTA"
        print("✓ Valid trade agreement schema created")
        
        return True
        
    except Exception as e:
        print(f"✗ Schema validation error: {e}")
        traceback.print_exc()
        return False


def test_response_schemas():
    """Test response schemas with mock data."""
    print("\nTesting response schemas...")
    
    try:
        from schemas.responses import (
            TariffDetailResponse, SearchResultsResponse, RateComparisonResponse
        )
        from schemas.tariff import TariffCodeResponse
        from schemas.common import PaginationMeta
        
        # Test TariffDetailResponse
        print("Testing TariffDetailResponse...")
        
        mock_tariff_data = {
            "id": 1,
            "hs_code": "0101210000",
            "description": "Live horses - Pure-bred breeding animals",
            "level": 10,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        tariff_response = TariffCodeResponse(**mock_tariff_data)
        
        detail_response_data = {
            "tariff": tariff_response,
            "duty_rates": [],
            "fta_rates": [],
            "children": [],
            "breadcrumbs": [
                {"level": "section", "id": 1, "title": "Live Animals"},
                {"level": "chapter", "id": 1, "title": "Live Animals"}
            ]
        }
        
        detail_response = TariffDetailResponse(**detail_response_data)
        assert detail_response.tariff.hs_code == "0101210000"
        print("✓ TariffDetailResponse created successfully")
        
        # Test SearchResultsResponse
        print("Testing SearchResultsResponse...")
        
        pagination_data = {
            "total": 100,
            "limit": 50,
            "offset": 0,
            "page": 1,
            "pages": 2,
            "has_next": True,
            "has_prev": False
        }
        
        search_response_data = {
            "results": [],
            "pagination": PaginationMeta(**pagination_data),
            "total_results": 100,
            "search_time_ms": 45.2,
            "facets": {},
            "suggestions": []
        }
        
        search_response = SearchResultsResponse(**search_response_data)
        assert search_response.total_results == 100
        print("✓ SearchResultsResponse created successfully")
        
        return True
        
    except Exception as e:
        print(f"✗ Response schema error: {e}")
        traceback.print_exc()
        return False


def test_orm_integration():
    """Test ORM integration with model_config."""
    print("\nTesting ORM integration...")
    
    try:
        from schemas.tariff import TariffCodeResponse
        from schemas.duty import DutyRateResponse
        from schemas.fta import FtaRateResponse
        
        # Check that schemas have proper ORM configuration
        schemas_to_check = [TariffCodeResponse, DutyRateResponse, FtaRateResponse]
        
        for schema_class in schemas_to_check:
            config = schema_class.model_config
            assert config.get("from_attributes") == True, f"{schema_class.__name__} missing from_attributes=True"
            print(f"✓ {schema_class.__name__} has proper ORM configuration")
        
        return True
        
    except Exception as e:
        print(f"✗ ORM integration error: {e}")
        traceback.print_exc()
        return False


def test_endpoint_schemas():
    """Test that endpoint schemas are properly defined."""
    print("\nTesting endpoint schemas...")
    
    try:
        from schemas import ENDPOINT_SCHEMAS
        
        required_endpoints = [
            "GET /api/tariff/tree/{section_id}",
            "GET /api/tariff/code/{hs_code}",
            "GET /api/tariff/search",
            "GET /api/tariff/sections",
            "GET /api/tariff/chapters/{section_id}"
        ]
        
        for endpoint in required_endpoints:
            assert endpoint in ENDPOINT_SCHEMAS, f"Missing endpoint schema: {endpoint}"
            schema_info = ENDPOINT_SCHEMAS[endpoint]
            assert "response" in schema_info, f"Missing response schema for {endpoint}"
            print(f"✓ {endpoint} schema defined")
        
        print(f"✓ All {len(required_endpoints)} required endpoint schemas found")
        return True
        
    except Exception as e:
        print(f"✗ Endpoint schema error: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all validation tests."""
    print("=" * 60)
    print("PYDANTIC SCHEMAS VALIDATION")
    print("=" * 60)
    
    tests = [
        ("Schema Imports", test_schema_imports),
        ("Validators", test_validators),
        ("Schema Validation", test_schema_validation),
        ("Response Schemas", test_response_schemas),
        ("ORM Integration", test_orm_integration),
        ("Endpoint Schemas", test_endpoint_schemas),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'-' * 40}")
        print(f"Running {test_name} tests...")
        print(f"{'-' * 40}")
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {e}")
            traceback.print_exc()
            results[test_name] = False
    
    # Summary
    print(f"\n{'=' * 60}")
    print("VALIDATION SUMMARY")
    print(f"{'=' * 60}")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All schema validation tests passed!")
        print("\nThe Pydantic schemas are ready for use with the FastAPI backend.")
        return True
    else:
        print(f"\n❌ {total - passed} test(s) failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)