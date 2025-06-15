"""
API response schemas for the Customs Broker Portal.

This module contains comprehensive response schemas that combine multiple models
for specific API endpoints, providing complete data structures for the frontend.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal

from pydantic import BaseModel, Field

from .common import PaginationMeta, SuccessResponse
from .tariff import TariffCodeResponse, TariffCodeSummary, TariffTreeNode
from .duty import DutyRateResponse, DutyRateSummary
from .fta import FtaRateResponse, FtaRateSummary, TradeAgreementResponse


class TariffSectionResponse(BaseModel):
    """
    Response schema for tariff sections.
    
    Contains section information with optional chapter details.
    """
    
    model_config = {"from_attributes": True}
    
    id: int = Field(description="Primary key")
    section_number: int = Field(description="Section number")
    title: str = Field(description="Section title")
    description: Optional[str] = Field(None, description="Section description")
    chapter_range: Optional[str] = Field(None, description="Chapter range")
    
    # Optional chapter details
    chapters: Optional[List["TariffChapterResponse"]] = Field(
        None,
        description="Chapters in this section"
    )
    
    # Statistics
    total_chapters: Optional[int] = Field(
        None,
        description="Total number of chapters in this section"
    )
    total_codes: Optional[int] = Field(
        None,
        description="Total number of tariff codes in this section"
    )


class TariffChapterResponse(BaseModel):
    """
    Response schema for tariff chapters.
    
    Contains chapter information with optional section and code details.
    """
    
    model_config = {"from_attributes": True}
    
    id: int = Field(description="Primary key")
    chapter_number: int = Field(description="Chapter number")
    title: str = Field(description="Chapter title")
    chapter_notes: Optional[str] = Field(None, description="Chapter notes")
    section_id: int = Field(description="Parent section ID")
    
    # Optional section details
    section: Optional[TariffSectionResponse] = Field(
        None,
        description="Parent section information"
    )
    
    # Optional code summaries
    tariff_codes: Optional[List[TariffCodeSummary]] = Field(
        None,
        description="Tariff codes in this chapter"
    )
    
    # Statistics
    total_codes: Optional[int] = Field(
        None,
        description="Total number of tariff codes in this chapter"
    )


class TariffDetailResponse(BaseModel):
    """
    Comprehensive tariff detail response for GET /api/tariff/code/{hs_code}.
    
    Contains complete tariff information with all related data.
    """
    
    # Core tariff information
    tariff: TariffCodeResponse = Field(
        description="Core tariff code information"
    )
    
    # Hierarchy context
    section: Optional[TariffSectionResponse] = Field(
        None,
        description="Parent section information"
    )
    chapter: Optional[TariffChapterResponse] = Field(
        None,
        description="Parent chapter information"
    )
    parent: Optional[TariffCodeSummary] = Field(
        None,
        description="Parent tariff code"
    )
    
    # Related rates
    duty_rates: List[DutyRateResponse] = Field(
        default_factory=list,
        description="General duty rates for this tariff code"
    )
    fta_rates: List[FtaRateResponse] = Field(
        default_factory=list,
        description="FTA preferential rates for this tariff code"
    )
    
    # Child codes (for navigation)
    children: List[TariffCodeSummary] = Field(
        default_factory=list,
        description="Direct child tariff codes"
    )
    
    # Navigation aids
    breadcrumbs: List[Dict[str, Union[str, int]]] = Field(
        default_factory=list,
        description="Breadcrumb navigation path",
        example=[
            {"level": "section", "id": 1, "title": "Live Animals; Animal Products"},
            {"level": "chapter", "id": 1, "title": "Live Animals"},
            {"level": "heading", "code": "0101", "description": "Live horses, asses, mules and hinnies"}
        ]
    )
    
    # Related information
    related_codes: List[TariffCodeSummary] = Field(
        default_factory=list,
        description="Related or similar tariff codes"
    )
    
    # Rate analysis
    rate_analysis: Optional[Dict[str, Any]] = Field(
        None,
        description="Analysis of available rates and recommendations"
    )
    
    # Metadata
    last_updated: Optional[datetime] = Field(
        None,
        description="When this tariff information was last updated"
    )


class TariffTreeResponse(BaseModel):
    """
    Response schema for GET /api/tariff/tree/{section_id}.
    
    Contains hierarchical tariff tree structure for navigation.
    """
    
    # Tree structure
    nodes: List[TariffTreeNode] = Field(
        description="Tree nodes in hierarchical order"
    )
    
    # Context information
    section: Optional[TariffSectionResponse] = Field(
        None,
        description="Section information if filtered by section"
    )
    chapter: Optional[TariffChapterResponse] = Field(
        None,
        description="Chapter information if filtered by chapter"
    )
    
    # Tree metadata
    total_nodes: int = Field(
        description="Total number of nodes in the tree"
    )
    max_depth: int = Field(
        description="Maximum depth of the tree"
    )
    expanded_levels: List[int] = Field(
        default_factory=list,
        description="Levels that are expanded in this response"
    )
    
    # Navigation state
    root_level: int = Field(
        default=2,
        description="Root level of the tree (2=chapter, 4=heading, etc.)"
    )
    show_inactive: bool = Field(
        default=False,
        description="Whether inactive codes are included"
    )
    
    # Performance metadata
    load_time_ms: Optional[float] = Field(
        None,
        description="Time taken to load the tree in milliseconds"
    )


class TariffSectionListResponse(BaseModel):
    """
    Response schema for GET /api/tariff/sections.
    
    Contains list of all tariff sections with summary information.
    """
    
    sections: List[TariffSectionResponse] = Field(
        description="List of tariff sections"
    )
    
    # Summary statistics
    total_sections: int = Field(
        description="Total number of sections"
    )
    total_chapters: int = Field(
        description="Total number of chapters across all sections"
    )
    total_codes: int = Field(
        description="Total number of tariff codes across all sections"
    )
    
    # Metadata
    last_updated: Optional[datetime] = Field(
        None,
        description="When the section data was last updated"
    )


class TariffChapterListResponse(BaseModel):
    """
    Response schema for GET /api/tariff/chapters/{section_id}.
    
    Contains list of chapters for a specific section.
    """
    
    chapters: List[TariffChapterResponse] = Field(
        description="List of chapters in the section"
    )
    
    # Context
    section: TariffSectionResponse = Field(
        description="Parent section information"
    )
    
    # Summary statistics
    total_chapters: int = Field(
        description="Total number of chapters in this section"
    )
    total_codes_in_section: int = Field(
        description="Total number of tariff codes in this section"
    )


class SearchResultsResponse(BaseModel):
    """
    Response schema for GET /api/tariff/search.
    
    Contains paginated search results with metadata and facets.
    """
    
    # Search results
    results: List[TariffCodeSummary] = Field(
        description="Search results"
    )
    
    # Pagination
    pagination: PaginationMeta = Field(
        description="Pagination metadata"
    )
    
    # Search metadata
    query: Optional[str] = Field(
        None,
        description="Original search query"
    )
    total_results: int = Field(
        description="Total number of matching results"
    )
    search_time_ms: float = Field(
        description="Search execution time in milliseconds"
    )
    
    # Search facets for filtering
    facets: Dict[str, Any] = Field(
        default_factory=dict,
        description="Search facets for filtering",
        example={
            "sections": [
                {"id": 1, "title": "Live Animals", "count": 45},
                {"id": 2, "title": "Vegetable Products", "count": 123}
            ],
            "levels": [
                {"level": 6, "count": 234},
                {"level": 8, "count": 456}
            ],
            "has_duty_rates": {"true": 567, "false": 89},
            "has_fta_rates": {"true": 345, "false": 311}
        }
    )
    
    # Search suggestions
    suggestions: List[str] = Field(
        default_factory=list,
        description="Search suggestions for query improvement"
    )
    
    # Applied filters
    applied_filters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Filters that were applied to this search"
    )


class RateComparisonResponse(BaseModel):
    """
    Response schema for rate comparison endpoints.
    
    Compares general duty rates with available FTA rates.
    """
    
    hs_code: str = Field(description="HS code")
    tariff_description: str = Field(description="Tariff description")
    
    # General duty information
    general_duty: Optional[DutyRateResponse] = Field(
        None,
        description="General duty rate information"
    )
    
    # FTA rates
    fta_rates: List[FtaRateResponse] = Field(
        default_factory=list,
        description="Available FTA rates"
    )
    
    # Best rate analysis
    best_rate: Optional[Union[DutyRateResponse, FtaRateResponse]] = Field(
        None,
        description="Best available rate (general or FTA)"
    )
    best_rate_type: Optional[str] = Field(
        None,
        description="Type of best rate (general or fta)"
    )
    
    # Savings analysis
    potential_savings: Optional[Decimal] = Field(
        None,
        description="Potential savings using best FTA rate vs general"
    )
    savings_percentage: Optional[Decimal] = Field(
        None,
        description="Savings as percentage of general duty"
    )
    
    # Recommendations
    recommended_countries: List[str] = Field(
        default_factory=list,
        description="Recommended countries for sourcing"
    )
    
    # Trade agreements
    applicable_agreements: List[TradeAgreementResponse] = Field(
        default_factory=list,
        description="Trade agreements with rates for this code"
    )


class DashboardStatsResponse(BaseModel):
    """
    Response schema for dashboard statistics.
    
    Provides overview statistics for the dashboard.
    """
    
    # Tariff code statistics
    total_tariff_codes: int = Field(description="Total number of tariff codes")
    active_tariff_codes: int = Field(description="Number of active tariff codes")
    
    # Hierarchy statistics
    total_sections: int = Field(description="Total number of sections")
    total_chapters: int = Field(description="Total number of chapters")
    
    # Rate statistics
    total_duty_rates: int = Field(description="Total number of duty rates")
    total_fta_rates: int = Field(description="Total number of FTA rates")
    active_trade_agreements: int = Field(description="Number of active trade agreements")
    
    # Coverage statistics
    codes_with_duty_rates: int = Field(description="Codes with duty rates")
    codes_with_fta_rates: int = Field(description="Codes with FTA rates")
    duty_rate_coverage: Decimal = Field(description="Duty rate coverage percentage")
    fta_rate_coverage: Decimal = Field(description="FTA rate coverage percentage")
    
    # Recent activity
    recently_updated_codes: List[TariffCodeSummary] = Field(
        default_factory=list,
        description="Recently updated tariff codes"
    )
    
    # Rate distribution
    rate_distribution: Dict[str, int] = Field(
        default_factory=dict,
        description="Distribution of duty rates",
        example={
            "free": 123,
            "0-5%": 456,
            "5-10%": 234,
            "10-20%": 123,
            "20%+": 45
        }
    )
    
    # Last update information
    last_data_update: Optional[datetime] = Field(
        None,
        description="When the data was last updated"
    )
    stats_generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When these statistics were generated"
    )


class HealthCheckResponse(BaseModel):
    """
    Response schema for health check endpoints.
    
    Provides system health and status information.
    """
    
    status: str = Field(description="Overall system status", example="healthy")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Health check timestamp"
    )
    version: str = Field(description="API version", example="1.0.0")
    
    # Component health
    database: Dict[str, Any] = Field(
        description="Database health status",
        example={
            "status": "healthy",
            "connection_time_ms": 12.5,
            "total_connections": 5,
            "active_connections": 2
        }
    )
    
    # Data freshness
    data_freshness: Dict[str, Any] = Field(
        description="Data freshness information",
        example={
            "tariff_codes_last_update": "2024-01-15T10:30:00Z",
            "duty_rates_last_update": "2024-01-15T10:30:00Z",
            "fta_rates_last_update": "2024-01-15T10:30:00Z"
        }
    )
    
    # Performance metrics
    performance: Dict[str, Any] = Field(
        description="Performance metrics",
        example={
            "avg_response_time_ms": 45.2,
            "requests_per_minute": 120,
            "cache_hit_rate": 0.85
        }
    )


class ErrorDetailResponse(BaseModel):
    """
    Detailed error response for API errors.
    
    Provides comprehensive error information for debugging.
    """
    
    error: str = Field(description="Main error message")
    error_code: str = Field(description="Error code for programmatic handling")
    details: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Detailed error information"
    )
    
    # Request context
    request_id: Optional[str] = Field(None, description="Request ID for tracking")
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Error timestamp"
    )
    path: Optional[str] = Field(None, description="API path that caused the error")
    method: Optional[str] = Field(None, description="HTTP method")
    
    # Validation errors (if applicable)
    validation_errors: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Field validation errors"
    )
    
    # Suggestions
    suggestions: Optional[List[str]] = Field(
        None,
        description="Suggestions for fixing the error"
    )


# Update forward references
TariffSectionResponse.model_rebuild()
TariffChapterResponse.model_rebuild()