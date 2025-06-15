"""
AI-powered tariff classification service for the Customs Broker Portal.

This module provides the TariffAIService class that integrates with Anthropic's Claude API
to perform intelligent product classification, similarity search, and learning from broker feedback.
"""

import asyncio
import json
import re
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from decimal import Decimal

import anthropic
import structlog
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from config import get_settings
from database import get_db_session
from models.classification import ProductClassification
from models.tariff import TariffCode

# Configure structured logging
logger = structlog.get_logger(__name__)


class TariffAIService:
    """
    AI-powered tariff classification service using Anthropic Claude.
    
    This service provides intelligent product classification capabilities including:
    - AI-powered HS code classification using Claude
    - Similarity search for fallback classification
    - Classification result storage and management
    - Learning from broker corrections and feedback
    - Batch processing for multiple products
    """
    
    def __init__(self):
        """Initialize the TariffAIService with configuration and clients."""
        self.settings = get_settings()
        self.client = None
        self._initialize_client()
        
    def _initialize_client(self) -> None:
        """Initialize the Anthropic client with API key validation."""
        if not self.settings.anthropic_api_key:
            logger.warning("Anthropic API key not configured - AI features will be disabled")
            return
            
        try:
            self.client = anthropic.AsyncAnthropic(
                api_key=self.settings.anthropic_api_key
            )
            logger.info("Anthropic client initialized successfully")
        except Exception as e:
            logger.error("Failed to initialize Anthropic client", error=str(e))
            self.client = None
    
    async def classify_product(
        self,
        product_description: str,
        additional_context: Optional[Dict[str, Any]] = None,
        confidence_threshold: float = 0.5
    ) -> Dict[str, Any]:
        """
        Classify a product using AI and return the classification result.
        
        Args:
            product_description: Description of the product to classify
            additional_context: Optional additional product details (materials, usage, etc.)
            confidence_threshold: Minimum confidence score to accept AI classification
            
        Returns:
            Dict containing classification result with HS code, confidence, and metadata
        """
        logger.info(
            "Starting product classification",
            product_description=product_description[:100],
            has_context=bool(additional_context)
        )
        
        try:
            # First attempt AI classification
            if self.client:
                ai_result = await self._classify_with_ai(product_description, additional_context)
                
                if ai_result and ai_result.get("confidence", 0) >= confidence_threshold:
                    logger.info(
                        "AI classification successful",
                        hs_code=ai_result.get("hs_code"),
                        confidence=ai_result.get("confidence")
                    )
                    return ai_result
                else:
                    logger.info(
                        "AI classification below threshold, falling back to similarity search",
                        ai_confidence=ai_result.get("confidence") if ai_result else None
                    )
            
            # Fallback to similarity search
            similarity_result = await self.similarity_search(product_description)
            
            if similarity_result:
                logger.info(
                    "Similarity search classification found",
                    hs_code=similarity_result.get("hs_code"),
                    confidence=similarity_result.get("confidence")
                )
                return similarity_result
            
            # No classification found
            logger.warning("No classification found for product", product_description=product_description[:100])
            return {
                "hs_code": None,
                "confidence": 0.0,
                "classification_source": "none",
                "reasoning": "No suitable classification found",
                "requires_manual_review": True
            }
            
        except Exception as e:
            logger.error("Product classification failed", error=str(e), product_description=product_description[:100])
            return {
                "hs_code": None,
                "confidence": 0.0,
                "classification_source": "error",
                "error": str(e),
                "requires_manual_review": True
            }
    
    async def _classify_with_ai(
        self,
        product_description: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Perform AI classification using Anthropic Claude.
        
        Args:
            product_description: Product description to classify
            additional_context: Additional product details
            
        Returns:
            Classification result or None if failed
        """
        if not self.client:
            return None
            
        try:
            # Build the classification prompt
            prompt = self._build_classification_prompt(product_description, additional_context)
            
            # Make API call with retry logic
            response = await self._make_api_call_with_retry(prompt)
            
            if not response:
                return None
                
            # Parse and validate the response
            return self._parse_ai_response(response, product_description)
            
        except Exception as e:
            logger.error("AI classification failed", error=str(e))
            return None
    
    def _build_classification_prompt(
        self,
        product_description: str,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build a structured prompt for AI classification.
        
        Args:
            product_description: Product description
            additional_context: Additional context information
            
        Returns:
            Formatted prompt string
        """
        context_info = ""
        if additional_context:
            context_parts = []
            for key, value in additional_context.items():
                if value:
                    context_parts.append(f"- {key.replace('_', ' ').title()}: {value}")
            if context_parts:
                context_info = f"\n\nAdditional Context:\n" + "\n".join(context_parts)
        
        prompt = f"""You are an expert customs classifier specializing in Australian tariff classification using the Harmonized System (HS) codes.

Your task is to classify the following product and provide the most appropriate 8-digit HS code used in Australia.

Product Description: {product_description}{context_info}

Please analyze this product and provide your classification in the following JSON format:
{{
    "hs_code": "XXXXXXXX",
    "confidence": 0.XX,
    "reasoning": "Detailed explanation of why this HS code is appropriate",
    "alternative_codes": ["XXXXXXXX", "XXXXXXXX"],
    "key_factors": ["factor1", "factor2", "factor3"]
}}

Guidelines:
1. Use 8-digit HS codes as used in Australian customs classification
2. Confidence should be between 0.00 and 1.00 (1.00 = completely certain)
3. Provide clear reasoning based on the product's material, function, and intended use
4. Include up to 3 alternative codes if applicable
5. List key classification factors that influenced your decision
6. Consider the product's primary function and material composition
7. If uncertain, provide a lower confidence score

Respond only with the JSON object, no additional text."""

        return prompt
    
    async def _make_api_call_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        base_delay: float = 1.0
    ) -> Optional[str]:
        """
        Make API call to Claude with exponential backoff retry logic.
        
        Args:
            prompt: The prompt to send to Claude
            max_retries: Maximum number of retry attempts
            base_delay: Base delay for exponential backoff
            
        Returns:
            API response content or None if failed
        """
        for attempt in range(max_retries + 1):
            try:
                logger.debug(f"Making API call attempt {attempt + 1}")
                
                message = await self.client.messages.create(
                    model=self.settings.anthropic_model,
                    max_tokens=self.settings.anthropic_max_tokens,
                    temperature=self.settings.anthropic_temperature,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                
                if message.content and len(message.content) > 0:
                    return message.content[0].text
                    
                logger.warning("Empty response from API")
                return None
                
            except anthropic.RateLimitError as e:
                delay = base_delay * (2 ** attempt)
                logger.warning(
                    f"Rate limit hit, retrying in {delay}s",
                    attempt=attempt + 1,
                    max_retries=max_retries
                )
                if attempt < max_retries:
                    await asyncio.sleep(delay)
                    continue
                raise
                
            except anthropic.APIError as e:
                logger.error(f"API error on attempt {attempt + 1}", error=str(e))
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                raise
                
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}", error=str(e))
                if attempt < max_retries:
                    delay = base_delay * (2 ** attempt)
                    await asyncio.sleep(delay)
                    continue
                raise
        
        return None
    
    def _parse_ai_response(
        self,
        response: str,
        product_description: str
    ) -> Optional[Dict[str, Any]]:
        """
        Parse and validate AI response.
        
        Args:
            response: Raw response from Claude
            product_description: Original product description
            
        Returns:
            Parsed classification result or None if invalid
        """
        try:
            # Extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if not json_match:
                logger.error("No JSON found in AI response")
                return None
                
            response_data = json.loads(json_match.group())
            
            # Validate required fields
            required_fields = ["hs_code", "confidence", "reasoning"]
            for field in required_fields:
                if field not in response_data:
                    logger.error(f"Missing required field: {field}")
                    return None
            
            # Validate HS code format (8 digits)
            hs_code = response_data["hs_code"]
            if not re.match(r'^\d{8}$', str(hs_code)):
                logger.error(f"Invalid HS code format: {hs_code}")
                return None
            
            # Validate confidence score
            confidence = float(response_data["confidence"])
            if not 0.0 <= confidence <= 1.0:
                logger.error(f"Invalid confidence score: {confidence}")
                return None
            
            # Build result
            result = {
                "hs_code": hs_code,
                "confidence": confidence,
                "classification_source": "ai",
                "reasoning": response_data["reasoning"],
                "alternative_codes": response_data.get("alternative_codes", []),
                "key_factors": response_data.get("key_factors", []),
                "product_description": product_description,
                "classified_at": datetime.utcnow().isoformat()
            }
            
            logger.debug("AI response parsed successfully", hs_code=hs_code, confidence=confidence)
            return result
            
        except json.JSONDecodeError as e:
            logger.error("Failed to parse JSON from AI response", error=str(e))
            return None
        except Exception as e:
            logger.error("Failed to parse AI response", error=str(e))
            return None
    
    async def similarity_search(
        self,
        product_description: str,
        limit: int = 5,
        min_confidence: float = 0.6
    ) -> Optional[Dict[str, Any]]:
        """
        Perform similarity search using existing classifications.
        
        Args:
            product_description: Product description to find similar classifications for
            limit: Maximum number of similar products to consider
            min_confidence: Minimum confidence for similarity match
            
        Returns:
            Best matching classification or None if no good match found
        """
        try:
            async with get_db_session() as db:
                # Get verified classifications with high confidence
                query = (
                    select(ProductClassification)
                    .options(selectinload(ProductClassification.tariff_code))
                    .where(
                        ProductClassification.verified_by_broker == True,
                        ProductClassification.confidence_score >= min_confidence
                    )
                    .order_by(ProductClassification.confidence_score.desc())
                    .limit(limit * 2)  # Get more to improve matching
                )
                
                result = await db.execute(query)
                existing_classifications = result.scalars().all()
                
                if not existing_classifications:
                    logger.info("No existing verified classifications found for similarity search")
                    return None
                
                # Calculate similarity scores
                best_match = None
                best_similarity = 0.0
                
                for classification in existing_classifications:
                    similarity = self._calculate_text_similarity(
                        product_description.lower(),
                        classification.product_description.lower()
                    )
                    
                    if similarity > best_similarity and similarity >= min_confidence:
                        best_similarity = similarity
                        best_match = classification
                
                if best_match:
                    logger.info(
                        "Similarity match found",
                        hs_code=best_match.hs_code,
                        similarity=best_similarity,
                        original_confidence=float(best_match.confidence_score or 0)
                    )
                    
                    # Adjust confidence based on similarity
                    adjusted_confidence = float(best_match.confidence_score or 0) * best_similarity
                    
                    return {
                        "hs_code": best_match.hs_code,
                        "confidence": adjusted_confidence,
                        "classification_source": "similarity",
                        "reasoning": f"Similar to: {best_match.product_description[:100]}...",
                        "similarity_score": best_similarity,
                        "original_classification_id": best_match.id,
                        "product_description": product_description,
                        "classified_at": datetime.utcnow().isoformat()
                    }
                
                logger.info("No suitable similarity match found")
                return None
                
        except Exception as e:
            logger.error("Similarity search failed", error=str(e))
            return None
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two text strings using simple word overlap.
        
        Args:
            text1: First text string
            text2: Second text string
            
        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Simple word-based similarity calculation
        words1 = set(re.findall(r'\w+', text1.lower()))
        words2 = set(re.findall(r'\w+', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def store_classification(
        self,
        classification_result: Dict[str, Any],
        broker_user_id: Optional[int] = None
    ) -> Optional[int]:
        """
        Store classification result in the database.
        
        Args:
            classification_result: Classification result from classify_product
            broker_user_id: ID of broker user if manually verified
            
        Returns:
            ID of created ProductClassification record or None if failed
        """
        try:
            async with get_db_session() as db:
                # Validate HS code exists in tariff_codes table
                hs_code = classification_result.get("hs_code")
                if not hs_code:
                    logger.error("No HS code in classification result")
                    return None
                
                tariff_query = select(TariffCode).where(TariffCode.hs_code == hs_code)
                tariff_result = await db.execute(tariff_query)
                tariff_code = tariff_result.scalar_one_or_none()
                
                if not tariff_code:
                    logger.error(f"HS code {hs_code} not found in tariff_codes table")
                    return None
                
                # Create ProductClassification record
                classification = ProductClassification(
                    product_description=classification_result["product_description"],
                    hs_code=hs_code,
                    confidence_score=Decimal(str(classification_result["confidence"])),
                    classification_source=classification_result["classification_source"],
                    verified_by_broker=bool(broker_user_id),
                    broker_user_id=broker_user_id
                )
                
                db.add(classification)
                await db.commit()
                await db.refresh(classification)
                
                logger.info(
                    "Classification stored successfully",
                    classification_id=classification.id,
                    hs_code=hs_code,
                    confidence=classification_result["confidence"]
                )
                
                return classification.id
                
        except Exception as e:
            logger.error("Failed to store classification", error=str(e))
            return None
    
    async def learn_from_feedback(
        self,
        classification_id: int,
        correct_hs_code: str,
        broker_user_id: int,
        feedback_notes: Optional[str] = None
    ) -> bool:
        """
        Process broker feedback and corrections for continuous learning.
        
        Args:
            classification_id: ID of the original classification
            correct_hs_code: The correct HS code as determined by broker
            broker_user_id: ID of the broker providing feedback
            feedback_notes: Optional notes about the correction
            
        Returns:
            True if feedback processed successfully, False otherwise
        """
        try:
            async with get_db_session() as db:
                # Get the original classification
                query = select(ProductClassification).where(
                    ProductClassification.id == classification_id
                )
                result = await db.execute(query)
                original_classification = result.scalar_one_or_none()
                
                if not original_classification:
                    logger.error(f"Classification {classification_id} not found")
                    return False
                
                # Validate the correct HS code exists
                tariff_query = select(TariffCode).where(TariffCode.hs_code == correct_hs_code)
                tariff_result = await db.execute(tariff_query)
                tariff_code = tariff_result.scalar_one_or_none()
                
                if not tariff_code:
                    logger.error(f"Correct HS code {correct_hs_code} not found in tariff_codes table")
                    return False
                
                # Update the original classification if it was wrong
                if original_classification.hs_code != correct_hs_code:
                    # Create a new verified classification with the correct code
                    corrected_classification = ProductClassification(
                        product_description=original_classification.product_description,
                        hs_code=correct_hs_code,
                        confidence_score=Decimal("1.00"),  # Broker verification = 100% confidence
                        classification_source="broker",
                        verified_by_broker=True,
                        broker_user_id=broker_user_id
                    )
                    
                    db.add(corrected_classification)
                    
                    logger.info(
                        "Broker correction processed",
                        original_id=classification_id,
                        original_hs_code=original_classification.hs_code,
                        correct_hs_code=correct_hs_code,
                        broker_user_id=broker_user_id
                    )
                else:
                    # Mark the original as verified if it was correct
                    original_classification.verified_by_broker = True
                    original_classification.broker_user_id = broker_user_id
                    
                    logger.info(
                        "Classification verified as correct",
                        classification_id=classification_id,
                        hs_code=correct_hs_code,
                        broker_user_id=broker_user_id
                    )
                
                await db.commit()
                return True
                
        except Exception as e:
            logger.error("Failed to process broker feedback", error=str(e))
            return False
    
    async def classify_batch(
        self,
        products: List[Dict[str, Any]],
        confidence_threshold: float = 0.5,
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Classify multiple products in batch with concurrency control.
        
        Args:
            products: List of product dictionaries with 'description' and optional 'context'
            confidence_threshold: Minimum confidence threshold for AI classification
            max_concurrent: Maximum number of concurrent API calls
            
        Returns:
            List of classification results in the same order as input
        """
        logger.info(f"Starting batch classification of {len(products)} products")
        
        # Create semaphore to limit concurrent API calls
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def classify_single(product: Dict[str, Any]) -> Dict[str, Any]:
            async with semaphore:
                return await self.classify_product(
                    product_description=product["description"],
                    additional_context=product.get("context"),
                    confidence_threshold=confidence_threshold
                )
        
        try:
            # Process all products concurrently
            tasks = [classify_single(product) for product in products]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle any exceptions in results
            processed_results = []
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Batch classification failed for product {i}", error=str(result))
                    processed_results.append({
                        "hs_code": None,
                        "confidence": 0.0,
                        "classification_source": "error",
                        "error": str(result),
                        "requires_manual_review": True
                    })
                else:
                    processed_results.append(result)
            
            logger.info(f"Batch classification completed: {len(processed_results)} results")
            return processed_results
            
        except Exception as e:
            logger.error("Batch classification failed", error=str(e))
            # Return error results for all products
            return [
                {
                    "hs_code": None,
                    "confidence": 0.0,
                    "classification_source": "error",
                    "error": str(e),
                    "requires_manual_review": True
                }
                for _ in products
            ]
    
    async def get_classification_stats(self) -> Dict[str, Any]:
        """
        Get statistics about classification performance and usage.
        
        Returns:
            Dictionary containing classification statistics
        """
        try:
            async with get_db_session() as db:
                # Total classifications
                total_query = select(func.count(ProductClassification.id))
                total_result = await db.execute(total_query)
                total_classifications = total_result.scalar() or 0
                
                # Verified classifications
                verified_query = select(func.count(ProductClassification.id)).where(
                    ProductClassification.verified_by_broker == True
                )
                verified_result = await db.execute(verified_query)
                verified_classifications = verified_result.scalar() or 0
                
                # AI vs similarity vs broker classifications
                source_query = select(
                    ProductClassification.classification_source,
                    func.count(ProductClassification.id)
                ).group_by(ProductClassification.classification_source)
                source_result = await db.execute(source_query)
                source_stats = dict(source_result.fetchall())
                
                # Average confidence by source
                confidence_query = select(
                    ProductClassification.classification_source,
                    func.avg(ProductClassification.confidence_score)
                ).group_by(ProductClassification.classification_source)
                confidence_result = await db.execute(confidence_query)
                confidence_stats = {
                    source: float(avg_conf) if avg_conf else 0.0
                    for source, avg_conf in confidence_result.fetchall()
                }
                
                return {
                    "total_classifications": total_classifications,
                    "verified_classifications": verified_classifications,
                    "verification_rate": verified_classifications / total_classifications if total_classifications > 0 else 0.0,
                    "classifications_by_source": source_stats,
                    "average_confidence_by_source": confidence_stats,
                    "ai_available": self.client is not None
                }
                
        except Exception as e:
            logger.error("Failed to get classification stats", error=str(e))
            return {
                "total_classifications": 0,
                "verified_classifications": 0,
                "verification_rate": 0.0,
                "classifications_by_source": {},
                "average_confidence_by_source": {},
                "ai_available": self.client is not None,
                "error": str(e)
            }