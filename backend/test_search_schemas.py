#!/usr/bin/env python3
"""
Test script to validate search and classification schemas.

This script tests the import and basic functionality of all search schemas
to ensure they are properly defined and can be used in the application.
"""

import sys
from datetime import datetime, date
from typing import Dict, Any

def test_search_schema_imports():
    """Test that all search schemas can be imported successfully."""
    print("Testing search schema imports...")
    
    try:
        from schemas.search import (
            ClassificationSource,
            VerificationStatus,
            SearchSortBy,
            ProductClassificationRequest,
            ClassificationResult,
            ProductClassificationResponse,
            ClassificationFeedbackRequest,
            ClassificationFeedbackResponse,
            BatchClassificationRequest,
            BatchClassificationResponse,
            SearchFilters,
            ClassificationFilters,
            AdvancedSearchParams,
            ProductSearchRequest,
            ProductSearchResult,
            ProductSearchResponse,
            TariffSearchRequest,
            TariffSearchResult,
            TariffSearchResponse,
            SimilaritySearchRequest,
            SimilaritySearchResult,
            SimilaritySearchResponse,
            ClassificationHistory,
            ClassificationStatistics,
            VerificationStatusUpdate,
        )
        print("✓ All search schemas imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


def test_enum_values():
    """Test that enum values are properly defined."""
    print("\nTesting enum values...")
    
    try:
        from schemas.search import ClassificationSource, VerificationStatus, SearchSortBy
        
        # Test ClassificationSource enum
        assert ClassificationSource.AI == "ai"
        assert ClassificationSource.SIMILARITY == "similarity"
        assert ClassificationSource.BROKER == "broker"
        assert ClassificationSource.MANUAL == "manual"
        
        # Test VerificationStatus enum
        assert VerificationStatus.PENDING == "pending"
        assert VerificationStatus.VERIFIED == "verified"
        assert VerificationStatus.REJECTED == "rejected"
        assert VerificationStatus.REQUIRES_REVIEW == "requires_review"
        
        # Test SearchSortBy enum
        assert SearchSortBy.RELEVANCE == "relevance"
        assert SearchSortBy.CONFIDENCE == "confidence"
        assert SearchSortBy.DATE == "date"
        assert SearchSortBy.HS_CODE == "hs_code"
        assert SearchSortBy.DESCRIPTION == "description"
        
        print("✓ All enum values are correctly defined")
        return True
    except (ImportError, AssertionError) as e:
        print(f"✗ Enum test error: {e}")
        return False


def test_schema_instantiation():
    """Test that schemas can be instantiated with valid data."""
    print("\nTesting schema instantiation...")
    
    try:
        from schemas.search import (
            ProductClassificationRequest,
            ClassificationResult,
            ProductClassificationResponse,
            ClassificationSource,
            VerificationStatus,
            SearchFilters,
            ProductSearchRequest,
            SimilaritySearchRequest
        )
        
        # Test ProductClassificationRequest
        classification_request = ProductClassificationRequest(
            product_description="Wireless bluetooth headphones with noise cancellation",
            additional_details="Made of plastic and metal",
            country_of_origin="CHN",
            store_result=True,
            confidence_threshold=0.7
        )
        assert classification_request.product_description == "Wireless bluetooth headphones with noise cancellation"
        assert classification_request.confidence_threshold == 0.7
        
        # Test ClassificationResult
        classification_result = ClassificationResult(
            hs_code="8518300000",
            confidence_score=0.85,
            tariff_description="Headphones and earphones",
            classification_source=ClassificationSource.AI,
            reasoning="Product matches audio equipment category"
        )
        assert classification_result.hs_code == "8518300000"
        assert classification_result.confidence_score == 0.85
        
        # Test ProductClassificationResponse
        classification_response = ProductClassificationResponse(
            hs_code="8518300000",
            confidence_score=0.85,
            classification_source=ClassificationSource.AI,
            tariff_description="Headphones and earphones",
            alternative_codes=[classification_result],
            verification_required=False
        )
        assert classification_response.hs_code == "8518300000"
        assert len(classification_response.alternative_codes) == 1
        
        # Test SearchFilters
        search_filters = SearchFilters(
            date_from=date(2024, 1, 1),
            date_to=date(2024, 12, 31),
            min_confidence=0.5,
            max_confidence=1.0,
            verification_status=[VerificationStatus.VERIFIED],
            hs_code_prefix="85"
        )
        assert search_filters.min_confidence == 0.5
        assert search_filters.hs_code_prefix == "85"
        
        # Test ProductSearchRequest
        product_search = ProductSearchRequest(
            search_term="bluetooth headphones",
            query="audio equipment",
            sort_by="relevance"
        )
        assert product_search.search_term == "bluetooth headphones"
        
        # Test SimilaritySearchRequest
        similarity_search = SimilaritySearchRequest(
            reference_description="Wireless audio device",
            similarity_threshold=0.6,
            max_results=20
        )
        assert similarity_search.similarity_threshold == 0.6
        
        print("✓ All schemas can be instantiated successfully")
        return True
    except Exception as e:
        print(f"✗ Schema instantiation error: {e}")
        return False


def test_validation():
    """Test that schema validation works correctly."""
    print("\nTesting schema validation...")
    
    try:
        from schemas.search import ProductClassificationRequest
        from pydantic import ValidationError
        
        # Test valid data
        valid_request = ProductClassificationRequest(
            product_description="Valid product description",
            confidence_threshold=0.8
        )
        assert valid_request.confidence_threshold == 0.8
        
        # Test invalid confidence threshold
        try:
            invalid_request = ProductClassificationRequest(
                product_description="Valid product description",
                confidence_threshold=1.5  # Invalid: > 1.0
            )
            print("✗ Validation should have failed for confidence_threshold > 1.0")
            return False
        except ValidationError:
            pass  # Expected validation error
        
        # Test invalid product description (too short)
        try:
            invalid_request = ProductClassificationRequest(
                product_description="Hi",  # Invalid: < 5 characters
                confidence_threshold=0.8
            )
            print("✗ Validation should have failed for short product description")
            return False
        except ValidationError:
            pass  # Expected validation error
        
        print("✓ Schema validation works correctly")
        return True
    except Exception as e:
        print(f"✗ Validation test error: {e}")
        return False


def test_schema_integration():
    """Test that schemas integrate properly with the main schemas module."""
    print("\nTesting schema integration...")
    
    try:
        from schemas import (
            ProductClassificationRequest,
            ProductClassificationResponse,
            ClassificationResult,
            SearchFilters,
            SEARCH_SCHEMAS
        )
        
        # Test that schemas are available from main module
        assert ProductClassificationRequest is not None
        assert ProductClassificationResponse is not None
        assert ClassificationResult is not None
        assert SearchFilters is not None
        
        # Test that SEARCH_SCHEMAS collection exists and contains schemas
        assert SEARCH_SCHEMAS is not None
        assert len(SEARCH_SCHEMAS) > 0
        assert ProductClassificationRequest in SEARCH_SCHEMAS
        
        print("✓ Schema integration with main module works correctly")
        return True
    except Exception as e:
        print(f"✗ Schema integration error: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("SEARCH SCHEMAS VALIDATION TEST")
    print("=" * 60)
    
    tests = [
        test_search_schema_imports,
        test_enum_values,
        test_schema_instantiation,
        test_validation,
        test_schema_integration,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ All search schemas are working correctly!")
        return 0
    else:
        print("✗ Some tests failed. Please check the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())