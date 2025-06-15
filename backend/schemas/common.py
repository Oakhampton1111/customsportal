"""
Common base schemas and utilities for the Customs Broker Portal.

This module contains base schemas, pagination utilities, search parameters,
and error response schemas used across the application.
"""

from datetime import datetime, date
from typing import Optional, List, Any, Dict, Union
from decimal import Decimal

from pydantic import BaseModel, Field, ConfigDict, field_validator
from pydantic.types import PositiveInt


class BaseSchema(BaseModel):
    """
    Base schema with common fields and configuration.
    
    Provides common timestamp fields and ORM integration configuration
    for all schemas in the application.
    """
    
    model_config = ConfigDict(
        from_attributes=True,
        validate_assignment=True,
        arbitrary_types_allowed=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v),
        }
    )
    
    created_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the record was created"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the record was last updated"
    )


class PaginationParams(BaseModel):
    """
    Pagination parameters for list endpoints.
    
    Provides standardized pagination with limit, offset, and total count.
    """
    
    limit: PositiveInt = Field(
        default=50,
        le=1000,
        description="Maximum number of items to return (1-1000)"
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Number of items to skip"
    )
    
    @property
    def page(self) -> int:
        """Calculate current page number (1-based)."""
        return (self.offset // self.limit) + 1
    
    @property
    def skip(self) -> int:
        """Alias for offset for SQLAlchemy compatibility."""
        return self.offset


class PaginationMeta(BaseModel):
    """
    Pagination metadata for responses.
    
    Contains information about the current page, total items, and navigation.
    """
    
    total: int = Field(
        description="Total number of items available"
    )
    limit: int = Field(
        description="Maximum items per page"
    )
    offset: int = Field(
        description="Number of items skipped"
    )
    page: int = Field(
        description="Current page number (1-based)"
    )
    pages: int = Field(
        description="Total number of pages"
    )
    has_next: bool = Field(
        description="Whether there is a next page"
    )
    has_prev: bool = Field(
        description="Whether there is a previous page"
    )
    
    @classmethod
    def create(
        cls,
        total: int,
        limit: int,
        offset: int
    ) -> "PaginationMeta":
        """
        Create pagination metadata from total count and pagination params.
        
        Args:
            total: Total number of items
            limit: Items per page
            offset: Items skipped
            
        Returns:
            PaginationMeta instance
        """
        page = (offset // limit) + 1
        pages = (total + limit - 1) // limit  # Ceiling division
        
        return cls(
            total=total,
            limit=limit,
            offset=offset,
            page=page,
            pages=pages,
            has_next=offset + limit < total,
            has_prev=offset > 0
        )


class SearchParams(BaseModel):
    """
    Search parameters for search endpoints.
    
    Provides flexible search with query string, filters, and sorting.
    """
    
    query: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Search query string"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=dict,
        description="Additional filters to apply"
    )
    sort_by: Optional[str] = Field(
        None,
        description="Field to sort by"
    )
    sort_order: str = Field(
        default="asc",
        pattern="^(asc|desc)$",
        description="Sort order: 'asc' or 'desc'"
    )
    
    @field_validator('query')
    @classmethod
    def validate_query(cls, v):
        """Validate and clean search query."""
        if v:
            # Remove extra whitespace and ensure minimum length
            cleaned = ' '.join(v.strip().split())
            if len(cleaned) < 1:
                return None
            return cleaned
        return v


class ErrorDetail(BaseModel):
    """
    Detailed error information.
    
    Provides structured error details for API responses.
    """
    
    type: str = Field(
        description="Error type or category"
    )
    message: str = Field(
        description="Human-readable error message"
    )
    field: Optional[str] = Field(
        None,
        description="Field name if error is field-specific"
    )
    code: Optional[str] = Field(
        None,
        description="Error code for programmatic handling"
    )


class ErrorResponse(BaseModel):
    """
    Standardized error response schema.
    
    Provides consistent error responses across all API endpoints.
    """
    
    success: bool = Field(
        default=False,
        description="Always false for error responses"
    )
    error: str = Field(
        description="Main error message"
    )
    details: Optional[List[ErrorDetail]] = Field(
        None,
        description="Detailed error information"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the error occurred"
    )
    request_id: Optional[str] = Field(
        None,
        description="Request ID for tracking"
    )


class SuccessResponse(BaseModel):
    """
    Standardized success response wrapper.
    
    Provides consistent success responses with optional data payload.
    """
    
    success: bool = Field(
        default=True,
        description="Always true for success responses"
    )
    message: Optional[str] = Field(
        None,
        description="Success message"
    )
    data: Optional[Any] = Field(
        None,
        description="Response data payload"
    )


class HSCodeValidator:
    """
    Validator for Australian HS codes.
    
    Provides validation for HS code format and structure.
    """
    
    @staticmethod
    def validate_hs_code(hs_code: str) -> str:
        """
        Validate HS code format.
        
        Args:
            hs_code: HS code to validate
            
        Returns:
            Validated HS code
            
        Raises:
            ValueError: If HS code format is invalid
        """
        if not hs_code:
            raise ValueError("HS code cannot be empty")
        
        # Remove any spaces or special characters
        cleaned = ''.join(c for c in hs_code if c.isdigit())
        
        # Check length (2, 4, 6, 8, or 10 digits)
        if len(cleaned) not in [2, 4, 6, 8, 10]:
            raise ValueError(
                f"HS code must be 2, 4, 6, 8, or 10 digits, got {len(cleaned)}"
            )
        
        # Validate chapter range (01-99)
        if len(cleaned) >= 2:
            chapter = int(cleaned[:2])
            if chapter < 1 or chapter > 99:
                raise ValueError(f"Invalid chapter number: {chapter:02d}")
        
        return cleaned


class CountryCodeValidator:
    """
    Validator for ISO 3166-1 alpha-3 country codes.
    
    Provides validation for country codes used in FTA rates.
    """
    
    # Common country codes for Australian trade
    VALID_COUNTRY_CODES = {
        'AUS', 'USA', 'CHN', 'JPN', 'KOR', 'SGP', 'THA', 'VNM',
        'MYS', 'IDN', 'PHL', 'IND', 'NZL', 'CAN', 'MEX', 'CHL',
        'PER', 'GBR', 'DEU', 'FRA', 'ITA', 'ESP', 'NLD', 'BEL',
        'CHE', 'AUT', 'SWE', 'DNK', 'NOR', 'FIN', 'POL', 'CZE',
        'HUN', 'SVK', 'SVN', 'EST', 'LVA', 'LTU', 'BGR', 'ROU',
        'HRV', 'GRC', 'CYP', 'MLT', 'LUX', 'IRL', 'PRT'
    }
    
    @staticmethod
    def validate_country_code(country_code: str) -> str:
        """
        Validate ISO 3166-1 alpha-3 country code.
        
        Args:
            country_code: Country code to validate
            
        Returns:
            Validated country code in uppercase
            
        Raises:
            ValueError: If country code format is invalid
        """
        if not country_code:
            raise ValueError("Country code cannot be empty")
        
        cleaned = country_code.strip().upper()
        
        if len(cleaned) != 3:
            raise ValueError("Country code must be exactly 3 characters")
        
        if not cleaned.isalpha():
            raise ValueError("Country code must contain only letters")
        
        # Note: We don't enforce the valid codes list as it may be incomplete
        # and new codes may be added. This is just for reference.
        
        return cleaned


class FTACodeValidator:
    """
    Validator for Australian FTA codes.
    
    Provides validation for Free Trade Agreement codes.
    """
    
    # Known Australian FTA codes
    VALID_FTA_CODES = {
        'AUSFTA',    # Australia-United States FTA
        'SAFTA',     # Singapore-Australia FTA
        'TAFTA',     # Thailand-Australia FTA
        'AANZFTA',   # ASEAN-Australia-New Zealand FTA
        'ACIFTA',    # Australia-Chile FTA
        'MAFTA',     # Malaysia-Australia FTA
        'KAFTA',     # Korea-Australia FTA
        'JAEPA',     # Japan-Australia Economic Partnership Agreement
        'CHAFTA',    # China-Australia FTA
        'CPTPP',     # Comprehensive and Progressive Trans-Pacific Partnership
        'PACER',     # Pacific Agreement on Closer Economic Relations
        'RCEP',      # Regional Comprehensive Economic Partnership
    }
    
    @staticmethod
    def validate_fta_code(fta_code: str) -> str:
        """
        Validate FTA code format.
        
        Args:
            fta_code: FTA code to validate
            
        Returns:
            Validated FTA code in uppercase
            
        Raises:
            ValueError: If FTA code format is invalid
        """
        if not fta_code:
            raise ValueError("FTA code cannot be empty")
        
        cleaned = fta_code.strip().upper()
        
        if len(cleaned) < 3 or len(cleaned) > 10:
            raise ValueError("FTA code must be between 3 and 10 characters")
        
        if not cleaned.replace('-', '').isalnum():
            raise ValueError("FTA code must contain only letters, numbers, and hyphens")
        
        return cleaned


class RateValidator:
    """
    Validator for duty and FTA rates.
    
    Provides validation for rate values and formats.
    """
    
    @staticmethod
    def validate_rate(rate: Union[Decimal, float, int, None]) -> Optional[Decimal]:
        """
        Validate duty rate value.
        
        Args:
            rate: Rate value to validate
            
        Returns:
            Validated rate as Decimal or None
            
        Raises:
            ValueError: If rate is invalid
        """
        if rate is None:
            return None
        
        try:
            decimal_rate = Decimal(str(rate))
        except (ValueError, TypeError):
            raise ValueError(f"Invalid rate value: {rate}")
        
        if decimal_rate < 0:
            raise ValueError("Rate cannot be negative")
        
        if decimal_rate > 1000:
            raise ValueError("Rate cannot exceed 1000%")
        
        # Round to 2 decimal places
        return decimal_rate.quantize(Decimal('0.01'))


class ConfidenceScoreValidator:
    """
    Validator for AI classification confidence scores.
    
    Provides validation for confidence scores used in product classification.
    """
    
    @staticmethod
    def validate_confidence_score(score: Union[float, int, None]) -> Optional[float]:
        """
        Validate confidence score.
        
        Args:
            score: Confidence score to validate (0.0 to 1.0)
            
        Returns:
            Validated confidence score
            
        Raises:
            ValueError: If score is invalid
        """
        if score is None:
            return None
        
        try:
            float_score = float(score)
        except (ValueError, TypeError):
            raise ValueError(f"Invalid confidence score: {score}")
        
        if float_score < 0.0 or float_score > 1.0:
            raise ValueError("Confidence score must be between 0.0 and 1.0")
        
        return round(float_score, 4)  # Round to 4 decimal places