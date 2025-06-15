"""
Search and classification schemas for the Customs Broker Portal.

This module contains Pydantic schemas for AI-powered search and classification
functionality, including product classification, similarity search, and
comprehensive search filtering capabilities.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union, Literal
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, Field, field_validator, model_validator

from .common import (
    BaseSchema, HSCodeValidator, CountryCodeValidator, ConfidenceScoreValidator,
    PaginationParams, PaginationMeta, SearchParams, ErrorDetail, SuccessResponse
)


class ClassificationSource(str, Enum):
    """Source of classification result."""
    AI = "ai"
    SIMILARITY = "similarity"
    BROKER = "broker"
    MANUAL = "manual"


class VerificationStatus(str, Enum):
    """Verification status for classifications."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    REQUIRES_REVIEW = "requires_review"


class SearchSortBy(str, Enum):
    """Available sort options for search results."""
    RELEVANCE = "relevance"
    CONFIDENCE = "confidence"
    DATE = "date"
    HS_CODE = "hs_code"
    DESCRIPTION = "description"


# Classification Schemas

class ProductClassificationRequest(BaseModel):
    """
    Request schema for AI product classification.
    
    Used to request classification of a product description into an HS code.
    """
    
    product_description: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Text description of the product to classify",
        example="Wireless bluetooth headphones with noise cancellation"
    )
    additional_details: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional context like material, use, manufacturing process",
        example="Made of plastic and metal, used for personal audio entertainment"
    )
    country_of_origin: Optional[str] = Field(
        None,
        min_length=3,
        max_length=3,
        description="ISO 3166-1 alpha-3 country code for origin-specific classification",
        example="CHN"
    )
    store_result: bool = Field(
        default=True,
        description="Whether to store the classification result in the database"
    )
    confidence_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for accepting classification",
        example=0.7
    )
    
    @field_validator('country_of_origin')
    @classmethod
    def validate_country_code(cls, v):
        """Validate country code format if provided."""
        if v:
            return CountryCodeValidator.validate_country_code(v)
        return v
    
    @field_validator('confidence_threshold')
    @classmethod
    def validate_confidence_threshold(cls, v):
        """Validate confidence threshold."""
        return ConfidenceScoreValidator.validate_confidence_score(v)


class ClassificationResult(BaseModel):
    """
    Individual classification result with confidence and metadata.
    
    Represents a single classification option with associated confidence.
    """
    
    hs_code: str = Field(
        ...,
        description="Classified HS code",
        example="8518300000"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="AI confidence score (0.0-1.0)",
        example=0.85
    )
    tariff_description: str = Field(
        ...,
        description="Description of the classified tariff code",
        example="Headphones and earphones, whether or not combined with a microphone"
    )
    classification_source: ClassificationSource = Field(
        ...,
        description="Source of this classification result"
    )
    reasoning: Optional[str] = Field(
        None,
        description="AI reasoning for this classification",
        example="Product matches audio equipment category based on 'headphones' and 'audio' keywords"
    )
    
    @field_validator('hs_code')
    @classmethod
    def validate_hs_code(cls, v):
        """Validate HS code format."""
        return HSCodeValidator.validate_hs_code(v)
    
    @field_validator('confidence_score')
    @classmethod
    def validate_confidence_score(cls, v):
        """Validate confidence score."""
        return ConfidenceScoreValidator.validate_confidence_score(v)


class ProductClassificationResponse(BaseModel):
    """
    Response schema for product classification with primary result and alternatives.
    
    Contains the main classification result plus alternative options.
    """
    
    # Primary classification
    hs_code: str = Field(
        ...,
        description="Primary classified HS code",
        example="8518300000"
    )
    confidence_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score for primary classification",
        example=0.85
    )
    classification_source: ClassificationSource = Field(
        ...,
        description="Source of primary classification"
    )
    tariff_description: str = Field(
        ...,
        description="Description of the primary classified tariff code"
    )
    
    # Alternative classifications
    alternative_codes: List[ClassificationResult] = Field(
        default_factory=list,
        description="List of alternative HS codes with confidence scores"
    )
    
    # Verification and storage
    verification_required: bool = Field(
        ...,
        description="Whether broker verification is needed for this classification"
    )
    classification_id: Optional[int] = Field(
        None,
        description="Database ID of stored classification (if stored)"
    )
    
    # Processing metadata
    processing_time_ms: Optional[float] = Field(
        None,
        description="Time taken to process classification in milliseconds"
    )
    model_version: Optional[str] = Field(
        None,
        description="Version of the AI model used for classification"
    )
    
    @field_validator('hs_code')
    @classmethod
    def validate_hs_code(cls, v):
        """Validate primary HS code format."""
        return HSCodeValidator.validate_hs_code(v)
    
    @field_validator('confidence_score')
    @classmethod
    def validate_confidence_score(cls, v):
        """Validate confidence score."""
        return ConfidenceScoreValidator.validate_confidence_score(v)


class ClassificationFeedbackRequest(BaseModel):
    """
    Schema for broker feedback and corrections on classifications.
    
    Allows brokers to provide feedback to improve AI classification accuracy.
    """
    
    classification_id: int = Field(
        ...,
        description="ID of the classification being reviewed"
    )
    correct_hs_code: Optional[str] = Field(
        None,
        description="Correct HS code if the classification was wrong"
    )
    verification_status: VerificationStatus = Field(
        ...,
        description="Broker's verification decision"
    )
    feedback_notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Additional notes or reasoning for the feedback"
    )
    broker_id: Optional[str] = Field(
        None,
        description="ID of the broker providing feedback"
    )
    confidence_assessment: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Broker's confidence assessment of the original classification"
    )
    
    @field_validator('correct_hs_code')
    @classmethod
    def validate_correct_hs_code(cls, v):
        """Validate correct HS code format if provided."""
        if v:
            return HSCodeValidator.validate_hs_code(v)
        return v
    
    @field_validator('confidence_assessment')
    @classmethod
    def validate_confidence_assessment(cls, v):
        """Validate confidence assessment."""
        if v is not None:
            return ConfidenceScoreValidator.validate_confidence_score(v)
        return v


class ClassificationFeedbackResponse(SuccessResponse):
    """
    Response for feedback submission.
    
    Confirms feedback was recorded and provides any updates.
    """
    
    feedback_id: int = Field(
        ...,
        description="ID of the recorded feedback"
    )
    updated_classification: Optional[ProductClassificationResponse] = Field(
        None,
        description="Updated classification if changes were made"
    )
    training_impact: Optional[str] = Field(
        None,
        description="Description of how this feedback will impact model training"
    )


class BatchClassificationRequest(BaseModel):
    """
    Schema for batch product classification.
    
    Allows classification of multiple products in a single request.
    """
    
    products: List[Dict[str, Any]] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of products to classify, each with 'description' and optional 'id'"
    )
    confidence_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Minimum confidence threshold for all classifications"
    )
    store_results: bool = Field(
        default=True,
        description="Whether to store all classification results"
    )
    batch_id: Optional[str] = Field(
        None,
        description="Optional batch identifier for tracking"
    )
    
    @field_validator('products')
    @classmethod
    def validate_products(cls, v):
        """Validate product list format."""
        for i, product in enumerate(v):
            if not isinstance(product, dict):
                raise ValueError(f"Product {i} must be a dictionary")
            if 'description' not in product:
                raise ValueError(f"Product {i} must have a 'description' field")
            if not isinstance(product['description'], str) or len(product['description'].strip()) < 5:
                raise ValueError(f"Product {i} description must be at least 5 characters")
        return v
    
    @field_validator('confidence_threshold')
    @classmethod
    def validate_confidence_threshold(cls, v):
        """Validate confidence threshold."""
        return ConfidenceScoreValidator.validate_confidence_score(v)


class BatchClassificationResponse(BaseModel):
    """
    Response for batch classification results.
    
    Contains results for all products in the batch with summary statistics.
    """
    
    batch_id: str = Field(
        ...,
        description="Unique identifier for this batch"
    )
    results: List[Dict[str, Any]] = Field(
        ...,
        description="Classification results for each product"
    )
    
    # Batch statistics
    total_products: int = Field(
        ...,
        description="Total number of products in the batch"
    )
    successful_classifications: int = Field(
        ...,
        description="Number of successful classifications"
    )
    failed_classifications: int = Field(
        ...,
        description="Number of failed classifications"
    )
    average_confidence: float = Field(
        ...,
        description="Average confidence score across all successful classifications"
    )
    
    # Processing metadata
    processing_time_ms: float = Field(
        ...,
        description="Total processing time for the batch"
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the batch was processed"
    )


# Search Schemas

class SearchFilters(BaseModel):
    """
    Common search filters for classification and tariff searches.
    
    Provides standardized filtering options across search endpoints.
    """
    
    # Date range filters
    date_from: Optional[date] = Field(
        None,
        description="Filter results from this date"
    )
    date_to: Optional[date] = Field(
        None,
        description="Filter results to this date"
    )
    
    # Confidence filters
    min_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Minimum confidence score filter"
    )
    max_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Maximum confidence score filter"
    )
    
    # Status filters
    verification_status: Optional[List[VerificationStatus]] = Field(
        None,
        description="Filter by verification status"
    )
    classification_source: Optional[List[ClassificationSource]] = Field(
        None,
        description="Filter by classification source"
    )
    
    # HS code filters
    hs_code_prefix: Optional[str] = Field(
        None,
        description="Filter by HS code prefix"
    )
    chapter_codes: Optional[List[str]] = Field(
        None,
        description="Filter by specific chapter codes"
    )
    
    @field_validator('min_confidence', 'max_confidence')
    @classmethod
    def validate_confidence_scores(cls, v):
        """Validate confidence score filters."""
        if v is not None:
            return ConfidenceScoreValidator.validate_confidence_score(v)
        return v
    
    @field_validator('hs_code_prefix')
    @classmethod
    def validate_hs_code_prefix(cls, v):
        """Validate HS code prefix format."""
        if v:
            cleaned = ''.join(c for c in v if c.isdigit())
            if not cleaned or len(cleaned) > 8:
                raise ValueError("HS code prefix must be 1-8 digits")
            return cleaned
        return v
    
    @model_validator(mode='after')
    def validate_date_range(self):
        """Validate date range consistency."""
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from must be before or equal to date_to")
        return self
    
    @model_validator(mode='after')
    def validate_confidence_range(self):
        """Validate confidence range consistency."""
        if (self.min_confidence is not None and self.max_confidence is not None 
            and self.min_confidence > self.max_confidence):
            raise ValueError("min_confidence must be less than or equal to max_confidence")
        return self


class ClassificationFilters(SearchFilters):
    """
    Specific filters for classification searches.
    
    Extends base search filters with classification-specific options.
    """
    
    # Product-specific filters
    product_description_contains: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Filter by product description content"
    )
    
    # Broker filters
    broker_id: Optional[str] = Field(
        None,
        description="Filter by specific broker"
    )
    requires_verification: Optional[bool] = Field(
        None,
        description="Filter classifications that require verification"
    )
    
    # AI model filters
    model_version: Optional[str] = Field(
        None,
        description="Filter by AI model version"
    )


class AdvancedSearchParams(SearchParams):
    """
    Extended search parameters with sorting and advanced options.
    
    Provides comprehensive search configuration for complex queries.
    """
    
    # Advanced sorting
    sort_by: SearchSortBy = Field(
        default=SearchSortBy.RELEVANCE,
        description="Field to sort results by"
    )
    include_alternatives: bool = Field(
        default=False,
        description="Include alternative classifications in results"
    )
    include_reasoning: bool = Field(
        default=False,
        description="Include AI reasoning in results"
    )
    
    # Search behavior
    fuzzy_matching: bool = Field(
        default=True,
        description="Enable fuzzy matching for search terms"
    )
    highlight_matches: bool = Field(
        default=True,
        description="Highlight matching terms in results"
    )
    
    # Result limits
    max_alternatives: int = Field(
        default=3,
        ge=0,
        le=10,
        description="Maximum number of alternative classifications to return"
    )


class ProductSearchRequest(AdvancedSearchParams):
    """
    Request schema for full-text product search.
    
    Searches across product descriptions and classifications.
    """
    
    search_term: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Search term for product descriptions",
        example="bluetooth headphones"
    )
    filters: Optional[ClassificationFilters] = Field(
        None,
        description="Additional filters to apply to search"
    )
    search_scope: List[str] = Field(
        default=["descriptions", "classifications", "tariff_descriptions"],
        description="Scope of search (descriptions, classifications, tariff_descriptions)"
    )


class ProductSearchResult(BaseModel):
    """
    Individual product search result.
    
    Contains product information with search relevance metadata.
    """
    
    model_config = {"from_attributes": True}
    
    # Product information
    product_id: Optional[int] = Field(
        None,
        description="Product ID if stored in database"
    )
    product_description: str = Field(
        ...,
        description="Original product description"
    )
    highlighted_description: Optional[str] = Field(
        None,
        description="Description with search terms highlighted"
    )
    
    # Classification information
    hs_code: str = Field(
        ...,
        description="Classified HS code"
    )
    confidence_score: float = Field(
        ...,
        description="Classification confidence score"
    )
    tariff_description: str = Field(
        ...,
        description="Tariff code description"
    )
    classification_source: ClassificationSource = Field(
        ...,
        description="Source of classification"
    )
    verification_status: VerificationStatus = Field(
        ...,
        description="Verification status"
    )
    
    # Search metadata
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Search relevance score"
    )
    match_type: str = Field(
        ...,
        description="Type of match (exact, partial, fuzzy, etc.)"
    )
    
    # Optional additional data
    alternative_codes: Optional[List[ClassificationResult]] = Field(
        None,
        description="Alternative classifications if requested"
    )
    reasoning: Optional[str] = Field(
        None,
        description="AI reasoning if requested"
    )
    
    # Timestamps
    classified_at: Optional[datetime] = Field(
        None,
        description="When the classification was made"
    )


class ProductSearchResponse(BaseModel):
    """
    Response schema for product search results.
    
    Contains search results with pagination and metadata.
    """
    
    results: List[ProductSearchResult] = Field(
        ...,
        description="Search results"
    )
    pagination: PaginationMeta = Field(
        ...,
        description="Pagination metadata"
    )
    
    # Search metadata
    search_term: str = Field(
        ...,
        description="Original search term"
    )
    total_results: int = Field(
        ...,
        description="Total number of matching results"
    )
    search_time_ms: float = Field(
        ...,
        description="Search execution time in milliseconds"
    )
    
    # Search enhancements
    suggestions: Optional[List[str]] = Field(
        None,
        description="Search term suggestions"
    )
    facets: Optional[Dict[str, Any]] = Field(
        None,
        description="Search facets for filtering"
    )
    related_terms: Optional[List[str]] = Field(
        None,
        description="Related search terms"
    )


class TariffSearchRequest(AdvancedSearchParams):
    """
    Advanced tariff search with comprehensive filters.
    
    Extends existing tariff search with enhanced filtering capabilities.
    """
    
    search_query: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Search query for tariff descriptions"
    )
    filters: Optional[SearchFilters] = Field(
        None,
        description="Search filters to apply"
    )
    
    # Tariff-specific filters
    include_inactive: bool = Field(
        default=False,
        description="Include inactive tariff codes in results"
    )
    hierarchy_level: Optional[int] = Field(
        None,
        ge=2,
        le=10,
        description="Filter by specific hierarchy level"
    )
    section_ids: Optional[List[int]] = Field(
        None,
        description="Filter by specific section IDs"
    )
    chapter_ids: Optional[List[int]] = Field(
        None,
        description="Filter by specific chapter IDs"
    )


class TariffSearchResult(BaseModel):
    """
    Enhanced tariff search result with classification context.
    
    Combines tariff information with classification usage statistics.
    """
    
    model_config = {"from_attributes": True}
    
    # Core tariff information
    id: int = Field(description="Tariff code ID")
    hs_code: str = Field(description="HS code")
    description: str = Field(description="Tariff description")
    highlighted_description: Optional[str] = Field(
        None,
        description="Description with search terms highlighted"
    )
    level: int = Field(description="Hierarchy level")
    is_active: bool = Field(description="Whether the code is active")
    
    # Hierarchy context
    section_title: Optional[str] = Field(
        None,
        description="Parent section title"
    )
    chapter_title: Optional[str] = Field(
        None,
        description="Parent chapter title"
    )
    
    # Classification usage statistics
    classification_count: int = Field(
        default=0,
        description="Number of times this code has been used in classifications"
    )
    average_confidence: Optional[float] = Field(
        None,
        description="Average confidence score for classifications using this code"
    )
    verification_rate: Optional[float] = Field(
        None,
        description="Percentage of classifications that were verified by brokers"
    )
    
    # Search metadata
    relevance_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Search relevance score"
    )
    match_type: str = Field(
        ...,
        description="Type of match"
    )


class TariffSearchResponse(BaseModel):
    """
    Response for advanced tariff search.
    
    Contains enhanced tariff search results with classification insights.
    """
    
    results: List[TariffSearchResult] = Field(
        ...,
        description="Search results"
    )
    pagination: PaginationMeta = Field(
        ...,
        description="Pagination metadata"
    )
    
    # Search metadata
    search_query: Optional[str] = Field(
        None,
        description="Original search query"
    )
    total_results: int = Field(
        ...,
        description="Total number of matching results"
    )
    search_time_ms: float = Field(
        ...,
        description="Search execution time in milliseconds"
    )
    
    # Enhanced metadata
    classification_insights: Optional[Dict[str, Any]] = Field(
        None,
        description="Insights about classification usage patterns"
    )
    popular_codes: Optional[List[str]] = Field(
        None,
        description="Most frequently classified HS codes in results"
    )


class SimilaritySearchRequest(BaseModel):
    """
    Request for similarity-based classification search.
    
    Finds similar products and their classifications.
    """
    
    reference_description: str = Field(
        ...,
        min_length=5,
        max_length=2000,
        description="Reference product description to find similarities for"
    )
    reference_hs_code: Optional[str] = Field(
        None,
        description="Reference HS code to find similar classifications"
    )
    similarity_threshold: float = Field(
        default=0.6,
        ge=0.0,
        le=1.0,
        description="Minimum similarity score threshold"
    )
    max_results: int = Field(
        default=20,
        ge=1,
        le=100,
        description="Maximum number of similar results to return"
    )
    filters: Optional[ClassificationFilters] = Field(
        None,
        description="Additional filters to apply"
    )
    
    @field_validator('reference_hs_code')
    @classmethod
    def validate_reference_hs_code(cls, v):
        """Validate reference HS code format if provided."""
        if v:
            return HSCodeValidator.validate_hs_code(v)
        return v
    
    @field_validator('similarity_threshold')
    @classmethod
    def validate_similarity_threshold(cls, v):
        """Validate similarity threshold."""
        return ConfidenceScoreValidator.validate_confidence_score(v)


class SimilaritySearchResult(BaseModel):
    """
    Individual similarity search result.
    
    Contains similar product with similarity metrics.
    """
    
    model_config = {"from_attributes": True}
    
    # Product information
    product_description: str = Field(
        ...,
        description="Similar product description"
    )
    hs_code: str = Field(
        ...,
        description="HS code for similar product"
    )
    tariff_description: str = Field(
        ...,
        description="Tariff description"
    )
    
    # Similarity metrics
    similarity_score: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Similarity score to reference product"
    )
    classification_confidence: float = Field(
        ...,
        description="Original classification confidence"
    )
    verification_status: VerificationStatus = Field(
        ...,
        description="Verification status of this classification"
    )
    
    # Metadata
    classification_id: int = Field(
        ...,
        description="ID of the classification record"
    )
    classified_at: datetime = Field(
        ...,
        description="When this classification was made"
    )
    classification_source: ClassificationSource = Field(
        ...,
        description="Source of this classification"
    )


class SimilaritySearchResponse(BaseModel):
    """
    Response for similarity search results.
    
    Contains similar products with aggregated insights.
    """
    
    results: List[SimilaritySearchResult] = Field(
        ...,
        description="Similar classification results"
    )
    
    # Search metadata
    reference_description: str = Field(
        ...,
        description="Original reference description"
    )
    total_results: int = Field(
        ...,
        description="Total number of similar results found"
    )
    search_time_ms: float = Field(
        ...,
        description="Search execution time in milliseconds"
    )
    
    # Similarity insights
    most_common_hs_codes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Most common HS codes in similar results with counts"
    )
    average_similarity: float = Field(
        ...,
        description="Average similarity score across all results"
    )
    confidence_distribution: Optional[Dict[str, int]] = Field(
        None,
        description="Distribution of confidence scores in results"
    )
    
    # Recommendations
    recommended_hs_code: Optional[str] = Field(
        None,
        description="Recommended HS code based on similarity analysis"
    )
    recommendation_confidence: Optional[float] = Field(
        None,
        description="Confidence in the recommendation"
    )


# Classification History and Statistics

class ClassificationHistory(BaseModel):
    """
    Historical classification data for a product.
    
    Tracks classification changes and improvements over time.
    """
    
    model_config = {"from_attributes": True}
    
    classification_id: int = Field(
        ...,
        description="Classification record ID"
    )
    product_description: str = Field(
        ...,
        description="Product description"
    )
    hs_code: str = Field(
        ...,
        description="Classified HS code"
    )
    confidence_score: float = Field(
        ...,
        description="Classification confidence"
    )
    classification_source: ClassificationSource = Field(
        ...,
        description="Source of classification"
    )
    verification_status: VerificationStatus = Field(
        ...,
        description="Current verification status"
    )
    
    # History metadata
    classified_at: datetime = Field(
        ...,
        description="When classification was made"
    )
    verified_at: Optional[datetime] = Field(
        None,
        description="When classification was verified"
    )
    verified_by: Optional[str] = Field(
        None,
        description="Who verified the classification"
    )
    
    # Changes tracking
    previous_hs_code: Optional[str] = Field(
        None,
        description="Previous HS code if this was a correction"
    )
    correction_reason: Optional[str] = Field(
        None,
        description="Reason for correction if applicable"
    )


class ClassificationStatistics(BaseModel):
    """
    Statistics and analytics for classification performance.
    
    Provides insights into classification accuracy and usage patterns.
    """
    
    # Overall statistics
    total_classifications: int = Field(
        ...,
        description="Total number of classifications"
    )
    verified_classifications: int = Field(
        ...,
        description="Number of verified classifications"
    )
    rejected_classifications: int = Field(
        ...,
        description="Number of rejected classifications"
    )
    pending_classifications: int = Field(
        ...,
        description="Number of pending classifications"
    )
    
    # Accuracy metrics
    verification_rate: float = Field(
        ...,
        description="Percentage of classifications that were verified"
    )
    average_confidence: float = Field(
        ...,
        description="Average confidence score across all classifications"
    )
    accuracy_by_confidence: Dict[str, float] = Field(
        default_factory=dict,
        description="Accuracy rates by confidence score ranges"
    )
    
    # Source breakdown
    source_distribution: Dict[ClassificationSource, int] = Field(
        default_factory=dict,
        description="Distribution of classifications by source"
    )
    
    # Time-based metrics
    date_range: Dict[str, date] = Field(
        default_factory=dict,
        description="Date range for these statistics"
    )
    classifications_per_day: Optional[Dict[str, int]] = Field(
        None,
        description="Daily classification counts"
    )
    
    # Popular codes
    most_classified_codes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Most frequently classified HS codes"
    )
    
    # AI model performance
    ai_performance: Optional[Dict[str, Any]] = Field(
        None,
        description="AI model performance metrics"
    )


# Verification Status Schema

class VerificationStatusUpdate(BaseModel):
    """
    Schema for updating verification status and tracking.
    
    Used to track broker verification decisions and workflow.
    """
    
    classification_id: int = Field(
        ...,
        description="ID of classification being updated"
    )
    new_status: VerificationStatus = Field(
        ...,
        description="New verification status"
    )
    verified_by: str = Field(
        ...,
        description="ID or name of person making verification"
    )
    verification_notes: Optional[str] = Field(
        None,
        max_length=1000,
        description="Notes about the verification decision"
    )
    corrected_hs_code: Optional[str] = Field(
        None,
        description="Corrected HS code if verification resulted in a change"
    )
    
    @field_validator('corrected_hs_code')
    @classmethod
    def validate_corrected_hs_code(cls, v):
        """Validate corrected HS code format if provided."""
        if v:
            return HSCodeValidator.validate_hs_code(v)
        return v