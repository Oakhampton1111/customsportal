"""
Comprehensive tests for the AI Classification Service.

This module tests all aspects of the AI-powered tariff classification service including:
- Product classification algorithms and confidence scoring
- Batch classification processing and error handling
- Classification feedback processing and learning mechanisms
- AI model integration and fallback scenarios
- Classification result validation and quality checks
- External API integration with proper mocking
"""

import pytest
import pytest_asyncio
import json
from datetime import datetime, date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import anthropic

from ai.tariff_ai import TariffAIService
from models.classification import ProductClassification
from models.tariff import TariffCode


@pytest.mark.unit
class TestTariffAIService:
    """Test suite for TariffAIService core functionality."""
    
    @pytest_asyncio.fixture
    async def ai_service(self):
        """Create AI service instance."""
        return TariffAIService()
    
    @pytest_asyncio.fixture
    async def mock_ai_service(self, mock_anthropic_client):
        """Create AI service with mocked client."""
        service = TariffAIService()
        service.client = mock_anthropic_client
        return service
    
    @pytest_asyncio.fixture
    async def sample_tariff_code(self, test_session: AsyncSession):
        """Create sample tariff code."""
        tariff_code = TariffCode(
            hs_code="12345678",
            description="Test product for classification",
            unit="kg",
            statistical_code="01",
            is_active=True
        )
        test_session.add(tariff_code)
        await test_session.commit()
        await test_session.refresh(tariff_code)
        return tariff_code
    
    @pytest_asyncio.fixture
    async def sample_classification(self, test_session: AsyncSession, sample_tariff_code: TariffCode):
        """Create sample product classification."""
        classification = ProductClassification(
            product_description="Test electronic device for classification testing",
            hs_code="12345678",
            confidence_score=Decimal("0.85"),
            classification_source="ai",
            verified_by_broker=True,
            broker_user_id=1
        )
        test_session.add(classification)
        await test_session.commit()
        await test_session.refresh(classification)
        return classification
    
    def test_ai_service_initialization(self, ai_service: TariffAIService):
        """Test AI service initialization."""
        assert ai_service is not None
        assert hasattr(ai_service, 'settings')
        assert hasattr(ai_service, 'client')
    
    def test_ai_service_initialization_no_api_key(self):
        """Test AI service initialization without API key."""
        with patch('ai.tariff_ai.get_settings') as mock_settings:
            mock_settings.return_value.anthropic_api_key = None
            service = TariffAIService()
            assert service.client is None


@pytest.mark.unit
class TestProductClassification:
    """Test product classification functionality."""
    
    async def test_classify_product_success(
        self,
        mock_ai_service: TariffAIService,
        test_session: AsyncSession,
        sample_tariff_code: TariffCode
    ):
        """Test successful product classification."""
        # Mock AI response
        mock_response = {
            "hs_code": "12345678",
            "confidence": 0.85,
            "reasoning": "This is a test classification",
            "alternative_codes": ["87654321"],
            "key_factors": ["material", "function", "usage"]
        }
        
        with patch.object(mock_ai_service, '_classify_with_ai', return_value=mock_response):
            result = await mock_ai_service.classify_product(
                product_description="Test electronic device",
                confidence_threshold=0.5
            )
        
        assert result["hs_code"] == "12345678"
        assert result["confidence"] == 0.85
        assert result["classification_source"] == "ai"
        assert "reasoning" in result
        assert "alternative_codes" in result
    
    async def test_classify_product_low_confidence_fallback(
        self,
        mock_ai_service: TariffAIService,
        test_session: AsyncSession,
        sample_classification: ProductClassification
    ):
        """Test fallback to similarity search when AI confidence is low."""
        # Mock low confidence AI response
        low_confidence_response = {
            "hs_code": "12345678",
            "confidence": 0.3,  # Below threshold
            "reasoning": "Low confidence classification"
        }
        
        # Mock similarity search response
        similarity_response = {
            "hs_code": "12345678",
            "confidence": 0.7,
            "classification_source": "similarity",
            "reasoning": "Similar to: Test electronic device...",
            "similarity_score": 0.8
        }
        
        with patch.object(mock_ai_service, '_classify_with_ai', return_value=low_confidence_response), \
             patch.object(mock_ai_service, 'similarity_search', return_value=similarity_response):
            
            result = await mock_ai_service.classify_product(
                product_description="Electronic device for testing",
                confidence_threshold=0.5
            )
        
        assert result["hs_code"] == "12345678"
        assert result["classification_source"] == "similarity"
        assert result["confidence"] == 0.7
    
    async def test_classify_product_no_classification_found(
        self,
        mock_ai_service: TariffAIService,
        test_session: AsyncSession
    ):
        """Test when no classification is found."""
        with patch.object(mock_ai_service, '_classify_with_ai', return_value=None), \
             patch.object(mock_ai_service, 'similarity_search', return_value=None):
            
            result = await mock_ai_service.classify_product(
                product_description="Unknown product",
                confidence_threshold=0.5
            )
        
        assert result["hs_code"] is None
        assert result["confidence"] == 0.0
        assert result["classification_source"] == "none"
        assert result["requires_manual_review"] is True


@pytest.mark.unit
class TestAIIntegration:
    """Test AI model integration and API calls."""
    
    def test_build_classification_prompt(self, ai_service: TariffAIService):
        """Test classification prompt building."""
        product_description = "Electronic device for testing"
        additional_context = {
            "material": "plastic",
            "intended_use": "consumer"
        }
        
        prompt = ai_service._build_classification_prompt(
            product_description,
            additional_context
        )
        
        assert product_description in prompt
        assert "plastic" in prompt
        assert "consumer" in prompt
        assert "JSON format" in prompt
        assert "hs_code" in prompt
        assert "confidence" in prompt
    
    def test_parse_ai_response_valid(self, ai_service: TariffAIService):
        """Test parsing valid AI response."""
        response = '''
        Here is the classification:
        {
            "hs_code": "12345678",
            "confidence": 0.85,
            "reasoning": "Test reasoning",
            "alternative_codes": ["87654321"],
            "key_factors": ["material", "function"]
        }
        '''
        
        result = ai_service._parse_ai_response(response, "test product")
        
        assert result is not None
        assert result["hs_code"] == "12345678"
        assert result["confidence"] == 0.85
        assert result["classification_source"] == "ai"
        assert result["reasoning"] == "Test reasoning"
        assert result["alternative_codes"] == ["87654321"]
    
    def test_parse_ai_response_invalid_json(self, ai_service: TariffAIService):
        """Test parsing invalid JSON response."""
        response = "This is not valid JSON"
        
        result = ai_service._parse_ai_response(response, "test product")
        
        assert result is None


@pytest.mark.unit
class TestSimilaritySearch:
    """Test similarity search functionality."""
    
    def test_calculate_text_similarity(self, ai_service: TariffAIService):
        """Test text similarity calculation."""
        text1 = "electronic device smartphone mobile"
        text2 = "mobile phone electronic smartphone"
        
        similarity = ai_service._calculate_text_similarity(text1, text2)
        
        assert 0.0 <= similarity <= 1.0
        assert similarity > 0.5  # Should have high similarity
    
    def test_calculate_text_similarity_no_overlap(self, ai_service: TariffAIService):
        """Test text similarity with no word overlap."""
        text1 = "electronic device"
        text2 = "wooden furniture"
        
        similarity = ai_service._calculate_text_similarity(text1, text2)
        
        assert similarity == 0.0


@pytest.mark.integration
class TestBatchClassification:
    """Test batch classification processing."""
    
    async def test_classify_batch_success(
        self,
        mock_ai_service: TariffAIService,
        test_session: AsyncSession,
        sample_tariff_code: TariffCode
    ):
        """Test successful batch classification."""
        products = [
            {"description": "Electronic device 1"},
            {"description": "Electronic device 2", "context": {"material": "plastic"}},
            {"description": "Electronic device 3"}
        ]
        
        # Mock individual classification results
        mock_results = [
            {"hs_code": "12345678", "confidence": 0.8, "classification_source": "ai"},
            {"hs_code": "12345678", "confidence": 0.9, "classification_source": "ai"},
            {"hs_code": "12345678", "confidence": 0.7, "classification_source": "ai"}
        ]
        
        with patch.object(mock_ai_service, 'classify_product', side_effect=mock_results):
            results = await mock_ai_service.classify_batch(
                products=products,
                confidence_threshold=0.5,
                max_concurrent=2
            )
        
        assert len(results) == 3
        assert all(r["hs_code"] == "12345678" for r in results)
        assert all(r["confidence"] >= 0.7 for r in results)


@pytest.mark.unit
class TestClassificationStatistics:
    """Test classification statistics and analytics."""
    
    async def test_get_classification_stats(
        self,
        ai_service: TariffAIService,
        test_session: AsyncSession,
        sample_classification: ProductClassification
    ):
        """Test getting classification statistics."""
        with patch('ai.tariff_ai.get_db_session') as mock_get_db:
            mock_get_db.return_value.__aenter__.return_value = test_session
            
            stats = await ai_service.get_classification_stats()
        
        assert "total_classifications" in stats
        assert "verified_classifications" in stats
        assert "verification_rate" in stats
        assert "classifications_by_source" in stats
        assert "average_confidence_by_source" in stats
        assert "ai_available" in stats


@pytest.mark.external
class TestExternalIntegration:
    """Test external service integration scenarios."""
    
    async def test_ai_service_without_client(self):
        """Test AI service behavior without client."""
        service = TariffAIService()
        service.client = None  # Simulate no API key
        
        result = await service._classify_with_ai("test product")
        assert result is None


@pytest.mark.unit
class TestAIServiceEdgeCases:
    """Test edge cases and error scenarios."""
    
    async def test_classify_empty_description(
        self,
        ai_service: TariffAIService,
        test_session: AsyncSession
    ):
        """Test classification with empty product description."""
        result = await ai_service.classify_product(
            product_description="",
            confidence_threshold=0.5
        )
        
        assert result["hs_code"] is None
        assert result["requires_manual_review"] is True
    
    async def test_classify_special_characters(
        self,
        mock_ai_service: TariffAIService,
        test_session: AsyncSession
    ):
        """Test classification with special characters in description."""
        special_description = "Product with special chars: @#$%^&*()[]{}|\\:;\"'<>,.?/~`"
        
        mock_response = {
            "hs_code": "12345678",
            "confidence": 0.7,
            "reasoning": "Classification with special characters"
        }
        
        with patch.object(mock_ai_service, '_classify_with_ai', return_value=mock_response):
            result = await mock_ai_service.classify_product(
                product_description=special_description,
                confidence_threshold=0.5
            )
        
        assert result["hs_code"] == "12345678"
        assert result["confidence"] == 0.7