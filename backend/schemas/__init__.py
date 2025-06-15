"""
Pydantic schemas for the Customs Broker Portal FastAPI backend.

This package contains comprehensive Pydantic schemas for request/response validation,
organized by functional areas and supporting the required API endpoints.

Schema Organization:
- common.py: Base schemas, pagination, search parameters, validators
- tariff.py: TariffCode schemas for hierarchical navigation and search
- duty.py: DutyRate schemas for general duty calculations
- fta.py: FtaRate and TradeAgreement schemas for preferential rates
- responses.py: Complete API response schemas combining multiple models
- search.py: AI-powered search and classification schemas

Key Features:
- Pydantic v2 with proper field validation and documentation
- Australian customs-specific validations (HS codes, country codes, FTA codes)
- Hierarchical tree navigation support
- Search and pagination capabilities
- Rate calculation and comparison schemas
- Comprehensive error handling
- ORM integration with SQLAlchemy models
"""

# Common schemas and utilities
from .common import (
    BaseSchema,
    PaginationParams,
    PaginationMeta,
    SearchParams,
    ErrorDetail,
    ErrorResponse,
    SuccessResponse,
    HSCodeValidator,
    CountryCodeValidator,
    FTACodeValidator,
    RateValidator,
    ConfidenceScoreValidator,
)

# Tariff code schemas
from .tariff import (
    TariffCodeBase,
    TariffCodeCreate,
    TariffCodeUpdate,
    TariffCodeResponse,
    TariffCodeSummary,
    TariffTreeNode,
    TariffSearchRequest,
    TariffSearchResult,
    TariffSearchResponse,
    TariffTreeResponse,
    TariffDetailResponse,
)

# Duty rate schemas
from .duty import (
    DutyRateBase,
    DutyRateCreate,
    DutyRateUpdate,
    DutyRateResponse,
    DutyRateSummary,
    DutyCalculationRequest,
    DutyCalculationResult,
    DutyCalculationResponse,
    DutyRateComparison,
    DutyRateListResponse,
    DutyRateStatistics,
)

# Duty calculator schemas
from .duty_calculator import (
    DutyCalculationRequest as DutyCalcRequest,
    DutyCalculationResponse as DutyCalcResponse,
    DutyComponentResponse,
    DutyBreakdownResponse,
    DutyRateResponse as DutyCalcRateResponse,
    FtaRateResponse as DutyCalcFtaRateResponse,
    TcoExemptionResponse,
    AntiDumpingDutyResponse,
    DutyRatesListResponse,
    FtaRateRequest,
    TcoCheckRequest,
)

# FTA rate and trade agreement schemas
from .fta import (
    TradeAgreementBase,
    TradeAgreementCreate,
    TradeAgreementUpdate,
    TradeAgreementResponse,
    TradeAgreementSummary,
    FtaRateBase,
    FtaRateCreate,
    FtaRateUpdate,
    FtaRateResponse,
    FtaRateSummary,
    FtaRateSearchRequest,
    FtaRateComparison,
    OriginRequirement,
    FtaRateCalculationRequest,
    FtaRateCalculationResult,
    FtaRateListResponse,
)

# Search and classification schemas
from .search import (
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

# Complete API response schemas
from .responses import (
    TariffSectionResponse,
    TariffChapterResponse,
    TariffDetailResponse as APITariffDetailResponse,
    TariffTreeResponse as APITariffTreeResponse,
    TariffSectionListResponse,
    TariffChapterListResponse,
    SearchResultsResponse,
    RateComparisonResponse,
    DashboardStatsResponse,
    HealthCheckResponse,
    ErrorDetailResponse,
)

# Schema collections for easy import
TARIFF_SCHEMAS = [
    TariffCodeBase,
    TariffCodeCreate,
    TariffCodeUpdate,
    TariffCodeResponse,
    TariffCodeSummary,
    TariffTreeNode,
    TariffSearchRequest,
    TariffSearchResult,
    TariffSearchResponse,
    TariffTreeResponse,
    TariffDetailResponse,
]

DUTY_SCHEMAS = [
    DutyRateBase,
    DutyRateCreate,
    DutyRateUpdate,
    DutyRateResponse,
    DutyRateSummary,
    DutyCalculationRequest,
    DutyCalculationResult,
    DutyCalculationResponse,
    DutyRateComparison,
    DutyRateListResponse,
    DutyRateStatistics,
]

DUTY_CALCULATOR_SCHEMAS = [
    DutyCalcRequest,
    DutyCalcResponse,
    DutyComponentResponse,
    DutyBreakdownResponse,
    DutyCalcRateResponse,
    DutyCalcFtaRateResponse,
    TcoExemptionResponse,
    AntiDumpingDutyResponse,
    DutyRatesListResponse,
    FtaRateRequest,
    TcoCheckRequest,
]

FTA_SCHEMAS = [
    TradeAgreementBase,
    TradeAgreementCreate,
    TradeAgreementUpdate,
    TradeAgreementResponse,
    TradeAgreementSummary,
    FtaRateBase,
    FtaRateCreate,
    FtaRateUpdate,
    FtaRateResponse,
    FtaRateSummary,
    FtaRateSearchRequest,
    FtaRateComparison,
    OriginRequirement,
    FtaRateCalculationRequest,
    FtaRateCalculationResult,
    FtaRateListResponse,
]

SEARCH_SCHEMAS = [
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
]

API_RESPONSE_SCHEMAS = [
    TariffSectionResponse,
    TariffChapterResponse,
    APITariffDetailResponse,
    APITariffTreeResponse,
    TariffSectionListResponse,
    TariffChapterListResponse,
    SearchResultsResponse,
    RateComparisonResponse,
    DashboardStatsResponse,
    HealthCheckResponse,
    ErrorDetailResponse,
]

COMMON_SCHEMAS = [
    BaseSchema,
    PaginationParams,
    PaginationMeta,
    SearchParams,
    ErrorDetail,
    ErrorResponse,
    SuccessResponse,
]

VALIDATOR_CLASSES = [
    HSCodeValidator,
    CountryCodeValidator,
    FTACodeValidator,
    RateValidator,
    ConfidenceScoreValidator,
]

# All schemas for comprehensive export
ALL_SCHEMAS = (
    COMMON_SCHEMAS +
    TARIFF_SCHEMAS +
    DUTY_SCHEMAS +
    DUTY_CALCULATOR_SCHEMAS +
    FTA_SCHEMAS +
    SEARCH_SCHEMAS +
    API_RESPONSE_SCHEMAS
)

# Schema mapping for API endpoints
ENDPOINT_SCHEMAS = {
    # Tariff endpoints
    "GET /api/tariff/tree/{section_id}": {
        "response": APITariffTreeResponse,
        "summary": "Get hierarchical tariff tree for a section"
    },
    "GET /api/tariff/code/{hs_code}": {
        "response": APITariffDetailResponse,
        "summary": "Get detailed tariff information for an HS code"
    },
    "GET /api/tariff/search": {
        "request": TariffSearchRequest,
        "response": SearchResultsResponse,
        "summary": "Search tariff codes by description and filters"
    },
    "GET /api/tariff/sections": {
        "response": TariffSectionListResponse,
        "summary": "Get all tariff sections"
    },
    "GET /api/tariff/chapters/{section_id}": {
        "response": TariffChapterListResponse,
        "summary": "Get chapters for a specific section"
    },
    
    # Duty rate endpoints
    "POST /api/duty/calculate": {
        "request": DutyCalcRequest,
        "response": DutyCalcResponse,
        "summary": "Calculate comprehensive duty amount for customs value"
    },
    "GET /api/duty/rates/{hs_code}": {
        "response": DutyRatesListResponse,
        "summary": "Get all duty rates for an HS code"
    },
    "GET /api/duty/breakdown": {
        "response": DutyBreakdownResponse,
        "summary": "Get detailed calculation breakdown"
    },
    "GET /api/duty/fta-rates/{hs_code}/{country_code}": {
        "response": "List[DutyCalcFtaRateResponse]",
        "summary": "Get FTA rates for specific country"
    },
    "GET /api/duty/tco-check/{hs_code}": {
        "response": "List[TcoExemptionResponse]",
        "summary": "Check TCO exemptions"
    },
    
    # FTA rate endpoints
    "POST /api/fta/calculate": {
        "request": FtaRateCalculationRequest,
        "response": FtaRateCalculationResult,
        "summary": "Calculate FTA duty amount"
    },
    "GET /api/fta/rates/{hs_code}": {
        "response": FtaRateListResponse,
        "summary": "Get FTA rates for an HS code"
    },
    "GET /api/fta/comparison/{hs_code}": {
        "response": FtaRateComparison,
        "summary": "Compare FTA rates across agreements"
    },
    
    # System endpoints
    "GET /api/health": {
        "response": HealthCheckResponse,
        "summary": "System health check"
    },
    "GET /api/stats": {
        "response": DashboardStatsResponse,
        "summary": "Dashboard statistics"
    },
    
    # Search and classification endpoints
    "POST /api/search/classify": {
        "request": ProductClassificationRequest,
        "response": ProductClassificationResponse,
        "summary": "Classify a product description into HS code"
    },
    "POST /api/search/classify/batch": {
        "request": BatchClassificationRequest,
        "response": BatchClassificationResponse,
        "summary": "Classify multiple products in batch"
    },
    "POST /api/search/classify/feedback": {
        "request": ClassificationFeedbackRequest,
        "response": ClassificationFeedbackResponse,
        "summary": "Provide feedback on classification results"
    },
    "GET /api/search/products": {
        "request": ProductSearchRequest,
        "response": ProductSearchResponse,
        "summary": "Search classified products"
    },
    "GET /api/search/tariffs": {
        "request": TariffSearchRequest,
        "response": TariffSearchResponse,
        "summary": "Advanced tariff search with classification insights"
    },
    "POST /api/search/similarity": {
        "request": SimilaritySearchRequest,
        "response": SimilaritySearchResponse,
        "summary": "Find similar product classifications"
    },
    "GET /api/search/history": {
        "response": ClassificationHistory,
        "summary": "Get classification history"
    },
    "GET /api/search/statistics": {
        "response": ClassificationStatistics,
        "summary": "Get classification performance statistics"
    },
}

# Validation configuration
VALIDATION_CONFIG = {
    "hs_code_formats": [2, 4, 6, 8, 10],  # Allowed HS code lengths
    "max_rate_percentage": 1000,  # Maximum duty rate percentage
    "max_search_results": 1000,  # Maximum search results per page
    "default_page_size": 50,  # Default pagination size
    "max_page_size": 1000,  # Maximum pagination size
}

# Australian customs specific configurations
AUSTRALIAN_CUSTOMS_CONFIG = {
    "valid_fta_codes": [
        "AUSFTA", "SAFTA", "TAFTA", "AANZFTA", "ACIFTA", 
        "MAFTA", "KAFTA", "JAEPA", "CHAFTA", "CPTPP", 
        "PACER", "RCEP"
    ],
    "staging_categories": ["Base", "A", "B", "C", "D", "E"],
    "duty_unit_types": ["ad_valorem", "specific", "compound"],
    "agreement_statuses": ["active", "suspended", "terminated", "pending"],
}

__all__ = [
    # Common schemas
    "BaseSchema",
    "PaginationParams", 
    "PaginationMeta",
    "SearchParams",
    "ErrorDetail",
    "ErrorResponse",
    "SuccessResponse",
    
    # Validators
    "HSCodeValidator",
    "CountryCodeValidator",
    "FTACodeValidator", 
    "RateValidator",
    "ConfidenceScoreValidator",
    
    # Tariff schemas
    "TariffCodeBase",
    "TariffCodeCreate",
    "TariffCodeUpdate", 
    "TariffCodeResponse",
    "TariffCodeSummary",
    "TariffTreeNode",
    "TariffSearchRequest",
    "TariffSearchResult",
    "TariffSearchResponse",
    "TariffTreeResponse",
    "TariffDetailResponse",
    
    # Duty schemas
    "DutyRateBase",
    "DutyRateCreate",
    "DutyRateUpdate",
    "DutyRateResponse", 
    "DutyRateSummary",
    "DutyCalculationRequest",
    "DutyCalculationResult",
    "DutyCalculationResponse",
    "DutyRateComparison",
    "DutyRateListResponse",
    "DutyRateStatistics",
    
    # Duty calculator schemas
    "DutyCalcRequest",
    "DutyCalcResponse",
    "DutyComponentResponse",
    "DutyBreakdownResponse",
    "DutyCalcRateResponse",
    "DutyCalcFtaRateResponse",
    "TcoExemptionResponse",
    "AntiDumpingDutyResponse",
    "DutyRatesListResponse",
    "FtaRateRequest",
    "TcoCheckRequest",
    
    # FTA schemas
    "TradeAgreementBase",
    "TradeAgreementCreate",
    "TradeAgreementUpdate",
    "TradeAgreementResponse",
    "TradeAgreementSummary",
    "FtaRateBase", 
    "FtaRateCreate",
    "FtaRateUpdate",
    "FtaRateResponse",
    "FtaRateSummary",
    "FtaRateSearchRequest",
    "FtaRateComparison",
    "OriginRequirement",
    "FtaRateCalculationRequest",
    "FtaRateCalculationResult",
    "FtaRateListResponse",
    
    # Search and classification schemas
    "ClassificationSource",
    "VerificationStatus",
    "SearchSortBy",
    "ProductClassificationRequest",
    "ClassificationResult",
    "ProductClassificationResponse",
    "ClassificationFeedbackRequest",
    "ClassificationFeedbackResponse",
    "BatchClassificationRequest",
    "BatchClassificationResponse",
    "SearchFilters",
    "ClassificationFilters",
    "AdvancedSearchParams",
    "ProductSearchRequest",
    "ProductSearchResult",
    "ProductSearchResponse",
    "TariffSearchRequest",
    "TariffSearchResult",
    "TariffSearchResponse",
    "SimilaritySearchRequest",
    "SimilaritySearchResult",
    "SimilaritySearchResponse",
    "ClassificationHistory",
    "ClassificationStatistics",
    "VerificationStatusUpdate",
    
    # API response schemas
    "TariffSectionResponse",
    "TariffChapterResponse", 
    "APITariffDetailResponse",
    "APITariffTreeResponse",
    "TariffSectionListResponse",
    "TariffChapterListResponse",
    "SearchResultsResponse",
    "RateComparisonResponse",
    "DashboardStatsResponse",
    "HealthCheckResponse",
    "ErrorDetailResponse",
    
    # Schema collections
    "TARIFF_SCHEMAS",
    "DUTY_SCHEMAS",
    "DUTY_CALCULATOR_SCHEMAS",
    "FTA_SCHEMAS",
    "SEARCH_SCHEMAS",
    "API_RESPONSE_SCHEMAS",
    "COMMON_SCHEMAS",
    "VALIDATOR_CLASSES",
    "ALL_SCHEMAS",
    "ENDPOINT_SCHEMAS",
    "VALIDATION_CONFIG",
    "AUSTRALIAN_CUSTOMS_CONFIG",
]