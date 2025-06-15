"""
Search and classification API routes for the Customs Broker Portal.

This module implements AI-powered search and classification endpoints including
product classification, similarity search, batch processing, and analytics.
"""

import asyncio
import logging
import time
import uuid
from datetime import datetime, date
from typing import List, Optional, Dict, Any, Union
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Path, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func, text, desc
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy.exc import SQLAlchemyError
import structlog

from database import get_async_session
from ai.tariff_ai import TariffAIService
from models.classification import ProductClassification
from models.tariff import TariffCode
from models.hierarchy import TariffSection, TariffChapter
from schemas.search import (
    # Classification schemas
    ProductClassificationRequest, ProductClassificationResponse,
    BatchClassificationRequest, BatchClassificationResponse,
    ClassificationFeedbackRequest, ClassificationFeedbackResponse,
    
    # Search schemas
    ProductSearchRequest, ProductSearchResponse, ProductSearchResult,
    TariffSearchRequest, TariffSearchResponse, TariffSearchResult,
    SimilaritySearchRequest, SimilaritySearchResponse, SimilaritySearchResult,
    
    # Analytics schemas
    ClassificationHistory, ClassificationStatistics,
    
    # Supporting schemas
    ClassificationResult, SearchFilters, ClassificationFilters,
    AdvancedSearchParams, VerificationStatus, ClassificationSource,
    SearchSortBy
)
from schemas.common import PaginationMeta, PaginationParams, SuccessResponse

# Configure structured logging
logger = structlog.get_logger(__name__)

# Create router
router = APIRouter(prefix="/api/search", tags=["Search & Classification"])

# Initialize AI service
ai_service = TariffAIService()


# Dependency for AI service
async def get_ai_service() -> TariffAIService:
    """Get AI service instance."""
    return ai_service


# Classification Endpoints

@router.post("/classify", response_model=ProductClassificationResponse)
async def classify_product(
    request: ProductClassificationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    ai_service: TariffAIService = Depends(get_ai_service)
) -> ProductClassificationResponse:
    """
    AI-powered product classification.
    
    Classifies a product description into an HS code using AI with confidence scoring
    and verification tracking. Supports alternative HS code suggestions and stores
    results for future similarity matching.
    
    Args:
        request: Product classification request with description and options
        background_tasks: FastAPI background tasks for async operations
        db: Database session
        ai_service: AI service instance
        
    Returns:
        Classification result with primary HS code and alternatives
        
    Raises:
        HTTPException: 400 for invalid input, 500 for AI service errors
    """
    try:
        start_time = time.time()
        logger.info(
            "Starting product classification",
            product_description=request.product_description[:100],
            confidence_threshold=request.confidence_threshold
        )
        
        # Prepare additional context
        additional_context = {}
        if request.additional_details:
            additional_context["additional_details"] = request.additional_details
        if request.country_of_origin:
            additional_context["country_of_origin"] = request.country_of_origin
        
        # Perform AI classification
        classification_result = await ai_service.classify_product(
            product_description=request.product_description,
            additional_context=additional_context,
            confidence_threshold=request.confidence_threshold
        )
        
        if not classification_result.get("hs_code"):
            raise HTTPException(
                status_code=422,
                detail="Unable to classify product. Please provide more specific details or try manual classification."
            )
        
        # Get tariff description
        tariff_query = select(TariffCode).where(
            TariffCode.hs_code == classification_result["hs_code"]
        )
        tariff_result = await db.execute(tariff_query)
        tariff_code = tariff_result.scalar_one_or_none()
        
        if not tariff_code:
            raise HTTPException(
                status_code=404,
                detail=f"HS code {classification_result['hs_code']} not found in tariff database"
            )
        
        # Build alternative codes
        alternative_codes = []
        for alt_code in classification_result.get("alternative_codes", []):
            if isinstance(alt_code, str):
                # Simple string format
                alt_query = select(TariffCode).where(TariffCode.hs_code == alt_code)
                alt_result = await db.execute(alt_query)
                alt_tariff = alt_result.scalar_one_or_none()
                
                if alt_tariff:
                    alternative_codes.append(ClassificationResult(
                        hs_code=alt_code,
                        confidence_score=0.5,  # Default confidence for alternatives
                        tariff_description=alt_tariff.description,
                        classification_source=ClassificationSource.AI,
                        reasoning="Alternative classification option"
                    ))
        
        # Determine if verification is required
        confidence = classification_result.get("confidence", 0.0)
        verification_required = confidence < 0.8 or classification_result.get("requires_manual_review", False)
        
        # Store classification if requested
        classification_id = None
        if request.store_result:
            classification_id = await ai_service.store_classification(
                classification_result={
                    **classification_result,
                    "product_description": request.product_description
                }
            )
        
        processing_time = (time.time() - start_time) * 1000
        
        logger.info(
            "Product classification completed",
            hs_code=classification_result["hs_code"],
            confidence=confidence,
            processing_time_ms=processing_time,
            classification_id=classification_id
        )
        
        return ProductClassificationResponse(
            hs_code=classification_result["hs_code"],
            confidence_score=confidence,
            classification_source=ClassificationSource(classification_result.get("classification_source", "ai")),
            tariff_description=tariff_code.description,
            alternative_codes=alternative_codes,
            verification_required=verification_required,
            classification_id=classification_id,
            processing_time_ms=processing_time,
            model_version="claude-3.5-sonnet"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Product classification failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Classification failed: {str(e)}"
        )


@router.post("/classify/batch", response_model=BatchClassificationResponse)
async def classify_products_batch(
    request: BatchClassificationRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session),
    ai_service: TariffAIService = Depends(get_ai_service)
) -> BatchClassificationResponse:
    """
    Batch product classification with concurrent processing.
    
    Classifies multiple products in a single request with progress tracking
    and concurrent processing for improved performance.
    
    Args:
        request: Batch classification request with products list
        background_tasks: FastAPI background tasks
        db: Database session
        ai_service: AI service instance
        
    Returns:
        Batch results with statistics and individual classifications
        
    Raises:
        HTTPException: 400 for invalid input, 500 for processing errors
    """
    try:
        start_time = time.time()
        batch_id = request.batch_id or str(uuid.uuid4())
        
        logger.info(
            "Starting batch classification",
            batch_id=batch_id,
            product_count=len(request.products)
        )
        
        # Prepare products for classification
        products_for_ai = []
        for i, product in enumerate(request.products):
            products_for_ai.append({
                "description": product["description"],
                "context": product.get("additional_details"),
                "index": i,
                "id": product.get("id", f"product_{i}")
            })
        
        # Perform batch classification
        classification_results = await ai_service.classify_batch(
            products=products_for_ai,
            confidence_threshold=request.confidence_threshold,
            max_concurrent=5
        )
        
        # Process results
        results = []
        successful_count = 0
        failed_count = 0
        total_confidence = 0.0
        
        for i, result in enumerate(classification_results):
            product_data = request.products[i]
            
            if result.get("hs_code"):
                successful_count += 1
                total_confidence += result.get("confidence", 0.0)
                
                # Get tariff description
                tariff_query = select(TariffCode).where(
                    TariffCode.hs_code == result["hs_code"]
                )
                tariff_result = await db.execute(tariff_query)
                tariff_code = tariff_result.scalar_one_or_none()
                
                classification_response = {
                    "product_id": product_data.get("id"),
                    "product_description": product_data["description"],
                    "hs_code": result["hs_code"],
                    "confidence_score": result.get("confidence", 0.0),
                    "tariff_description": tariff_code.description if tariff_code else "Unknown",
                    "classification_source": result.get("classification_source", "ai"),
                    "verification_required": result.get("confidence", 0.0) < 0.8,
                    "reasoning": result.get("reasoning"),
                    "status": "success"
                }
                
                # Store if requested
                if request.store_results:
                    classification_id = await ai_service.store_classification({
                        **result,
                        "product_description": product_data["description"]
                    })
                    classification_response["classification_id"] = classification_id
                    
            else:
                failed_count += 1
                classification_response = {
                    "product_id": product_data.get("id"),
                    "product_description": product_data["description"],
                    "error": result.get("error", "Classification failed"),
                    "status": "failed"
                }
            
            results.append(classification_response)
        
        processing_time = (time.time() - start_time) * 1000
        average_confidence = total_confidence / successful_count if successful_count > 0 else 0.0
        
        logger.info(
            "Batch classification completed",
            batch_id=batch_id,
            successful=successful_count,
            failed=failed_count,
            processing_time_ms=processing_time
        )
        
        return BatchClassificationResponse(
            batch_id=batch_id,
            results=results,
            total_products=len(request.products),
            successful_classifications=successful_count,
            failed_classifications=failed_count,
            average_confidence=average_confidence,
            processing_time_ms=processing_time,
            created_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error("Batch classification failed", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Batch classification failed: {str(e)}"
        )


@router.post("/feedback", response_model=ClassificationFeedbackResponse)
async def submit_classification_feedback(
    request: ClassificationFeedbackRequest,
    db: AsyncSession = Depends(get_async_session),
    ai_service: TariffAIService = Depends(get_ai_service)
) -> ClassificationFeedbackResponse:
    """Store broker feedback for learning and improvement."""
    try:
        logger.info(
            "Processing classification feedback",
            classification_id=request.classification_id,
            verification_status=request.verification_status
        )
        
        # Get the original classification
        classification_query = select(ProductClassification).where(
            ProductClassification.id == request.classification_id
        )
        classification_result = await db.execute(classification_query)
        classification = classification_result.scalar_one_or_none()
        
        if not classification:
            raise HTTPException(
                status_code=404,
                detail=f"Classification with ID {request.classification_id} not found"
            )
        
        # Process feedback
        if request.verification_status == VerificationStatus.VERIFIED:
            classification.verified_by_broker = True
            if request.broker_id:
                classification.broker_user_id = int(request.broker_id) if request.broker_id.isdigit() else None
        
        await db.commit()
        
        feedback_id = int(time.time() * 1000)
        
        return ClassificationFeedbackResponse(
            success=True,
            message="Feedback recorded successfully",
            feedback_id=feedback_id,
            updated_classification=None,
            training_impact="Feedback recorded for model improvement"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to process classification feedback", error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process feedback: {str(e)}"
        )


# Search Endpoints

@router.get("/products", response_model=ProductSearchResponse)
async def search_products(
    search_term: str = Query(..., min_length=1, max_length=200, description="Search term for product descriptions"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Results per page"),
    sort_by: SearchSortBy = Query(SearchSortBy.RELEVANCE, description="Sort field"),
    min_confidence: Optional[float] = Query(None, ge=0.0, le=1.0, description="Minimum confidence filter"),
    verification_status: Optional[VerificationStatus] = Query(None, description="Filter by verification status"),
    db: AsyncSession = Depends(get_async_session)
) -> ProductSearchResponse:
    """Full-text search across product descriptions and classifications."""
    try:
        start_time = time.time()
        offset = (page - 1) * limit
        
        # Build base query
        base_query = (
            select(ProductClassification)
            .options(selectinload(ProductClassification.tariff_code))
            .where(ProductClassification.product_description.ilike(f"%{search_term}%"))
        )
        
        # Apply filters
        conditions = []
        if min_confidence is not None:
            conditions.append(ProductClassification.confidence_score >= min_confidence)
        if verification_status == VerificationStatus.VERIFIED:
            conditions.append(ProductClassification.verified_by_broker == True)
        elif verification_status == VerificationStatus.PENDING:
            conditions.append(ProductClassification.verified_by_broker == False)
        
        if conditions:
            base_query = base_query.where(and_(*conditions))
        
        # Apply sorting
        if sort_by == SearchSortBy.CONFIDENCE:
            base_query = base_query.order_by(desc(ProductClassification.confidence_score))
        elif sort_by == SearchSortBy.DATE:
            base_query = base_query.order_by(desc(ProductClassification.created_at))
        elif sort_by == SearchSortBy.HS_CODE:
            base_query = base_query.order_by(ProductClassification.hs_code)
        else:  # RELEVANCE
            base_query = base_query.order_by(
                func.length(ProductClassification.product_description),
                desc(ProductClassification.confidence_score)
            )
        
        # Get total count
        count_query = select(func.count()).select_from(base_query.subquery())
        count_result = await db.execute(count_query)
        total_count = count_result.scalar()
        
        # Apply pagination and execute
        search_query = base_query.offset(offset).limit(limit)
        search_result = await db.execute(search_query)
        classifications = search_result.scalars().all()
        
        # Build search results
        results = []
        for classification in classifications:
            relevance_score = 1.0
            if search_term.lower() in classification.product_description.lower():
                relevance_score = 0.9
            
            highlighted_description = classification.product_description.replace(
                search_term, f"<mark>{search_term}</mark>"
            ) if search_term else classification.product_description
            
            result = ProductSearchResult(
                product_id=classification.id,
                product_description=classification.product_description,
                highlighted_description=highlighted_description,
                hs_code=classification.hs_code,
                confidence_score=float(classification.confidence_score or 0),
                tariff_description=classification.tariff_code.description if classification.tariff_code else "Unknown",
                classification_source=ClassificationSource(classification.classification_source or "unknown"),
                verification_status=VerificationStatus.VERIFIED if classification.verified_by_broker else VerificationStatus.PENDING,
                relevance_score=relevance_score,
                match_type="description",
                classified_at=classification.created_at
            )
            results.append(result)
        
        pagination = PaginationMeta.create(total_count, limit, offset)
        search_time = (time.time() - start_time) * 1000
        
        return ProductSearchResponse(
            results=results,
            pagination=pagination,
            search_term=search_term,
            total_results=total_count,
            search_time_ms=search_time,
            suggestions=[],
            facets={},
            related_terms=[]
        )
        
    except Exception as e:
        logger.error("Product search failed", error=str(e))
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")


@router.get("/stats", response_model=ClassificationStatistics)
async def get_classification_stats(
    db: AsyncSession = Depends(get_async_session),
    ai_service: TariffAIService = Depends(get_ai_service)
) -> ClassificationStatistics:
    """Get classification statistics and analytics."""
    try:
        stats = await ai_service.get_classification_stats()
        
        return ClassificationStatistics(
            total_classifications=stats.get("total_classifications", 0),
            verified_classifications=stats.get("verified_classifications", 0),
            rejected_classifications=0,
            pending_classifications=stats.get("total_classifications", 0) - stats.get("verified_classifications", 0),
            verification_rate=stats.get("verification_rate", 0.0),
            average_confidence=stats.get("average_confidence_by_source", {}).get("ai", 0.0),
            accuracy_by_confidence={},
            source_distribution=stats.get("classifications_by_source", {}),
            date_range={},
            classifications_per_day={},
            most_classified_codes=[],
            ai_performance={}
        )
        
    except Exception as e:
        logger.error("Failed to get classification stats", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")