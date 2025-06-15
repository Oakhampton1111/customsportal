"""
Duty rate schemas for the Customs Broker Portal.

This module contains Pydantic schemas for DutyRate model validation,
including request/response schemas and rate calculations.
"""

from datetime import datetime
from typing import Optional, List, Dict, Union
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator

from .common import BaseSchema, HSCodeValidator, RateValidator


class DutyRateBase(BaseModel):
    """
    Base schema for DutyRate with core fields.
    
    Contains the essential fields shared across create, update, and response schemas.
    """
    
    hs_code: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="HS code this duty rate applies to",
        example="0101210000"
    )
    general_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=1000,
        description="MFN (Most Favoured Nation) rate as decimal percentage",
        example=5.00
    )
    unit_type: Optional[str] = Field(
        None,
        max_length=20,
        description="Type of duty (ad_valorem, specific, compound)",
        example="ad_valorem"
    )
    rate_text: Optional[str] = Field(
        None,
        max_length=200,
        description="Full rate text for complex rate structures",
        example="5% or $2.50 per kg, whichever is greater"
    )
    statistical_code: Optional[str] = Field(
        None,
        max_length=15,
        description="Statistical code for reporting",
        example="01012100001"
    )
    
    @field_validator('hs_code')
    @classmethod
    def validate_hs_code(cls, v):
        """Validate HS code format."""
        return HSCodeValidator.validate_hs_code(v)
    
    @field_validator('general_rate')
    @classmethod
    def validate_general_rate(cls, v):
        """Validate general rate value."""
        return RateValidator.validate_rate(v)
    
    @field_validator('unit_type')
    @classmethod
    def validate_unit_type(cls, v):
        """Validate unit type is one of allowed values."""
        if v is not None:
            allowed_types = ['ad_valorem', 'specific', 'compound']
            if v not in allowed_types:
                raise ValueError(f"Unit type must be one of: {', '.join(allowed_types)}")
        return v
    
    @field_validator('statistical_code')
    @classmethod
    def validate_statistical_code(cls, v):
        """Validate statistical code format."""
        if v is not None:
            # Remove any non-digit characters
            cleaned = ''.join(c for c in v if c.isdigit())
            if len(cleaned) < 8 or len(cleaned) > 15:
                raise ValueError("Statistical code must be 8-15 digits")
            return cleaned
        return v


class DutyRateCreate(DutyRateBase):
    """
    Schema for creating new duty rates.
    
    Inherits from DutyRateBase with any creation-specific validations.
    """
    pass


class DutyRateUpdate(BaseModel):
    """
    Schema for updating existing duty rates.
    
    All fields are optional to support partial updates.
    """
    
    general_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=1000,
        description="MFN (Most Favoured Nation) rate as decimal percentage"
    )
    unit_type: Optional[str] = Field(
        None,
        max_length=20,
        description="Type of duty (ad_valorem, specific, compound)"
    )
    rate_text: Optional[str] = Field(
        None,
        max_length=200,
        description="Full rate text for complex rate structures"
    )
    statistical_code: Optional[str] = Field(
        None,
        max_length=15,
        description="Statistical code for reporting"
    )
    
    @field_validator('general_rate')
    @classmethod
    def validate_general_rate(cls, v):
        """Validate general rate value."""
        return RateValidator.validate_rate(v)
    
    @field_validator('unit_type')
    @classmethod
    def validate_unit_type(cls, v):
        """Validate unit type is one of allowed values."""
        if v is not None:
            allowed_types = ['ad_valorem', 'specific', 'compound']
            if v not in allowed_types:
                raise ValueError(f"Unit type must be one of: {', '.join(allowed_types)}")
        return v


class DutyRateResponse(DutyRateBase, BaseSchema):
    """
    Complete response schema for duty rates.
    
    Includes all fields plus computed properties.
    """
    
    id: int = Field(description="Primary key")
    
    # Computed properties from the model
    is_ad_valorem: Optional[bool] = Field(
        None,
        description="Whether this is an ad valorem duty (percentage-based)"
    )
    is_specific: Optional[bool] = Field(
        None,
        description="Whether this is a specific duty (per-unit based)"
    )
    is_compound: Optional[bool] = Field(
        None,
        description="Whether this is a compound duty (combination)"
    )
    effective_rate_text: Optional[str] = Field(
        None,
        description="Effective rate text for display purposes"
    )
    
    # Related data
    tariff_code_description: Optional[str] = Field(
        None,
        description="Description of the associated tariff code"
    )


class DutyRateSummary(BaseModel):
    """
    Summary schema for duty rates in lists.
    
    Contains minimal fields for efficient list responses.
    """
    
    model_config = {"from_attributes": True}
    
    id: int = Field(description="Primary key")
    hs_code: str = Field(description="HS code")
    general_rate: Optional[Decimal] = Field(None, description="General duty rate")
    unit_type: Optional[str] = Field(None, description="Type of duty")
    rate_text: Optional[str] = Field(None, description="Rate text")
    effective_rate_text: Optional[str] = Field(None, description="Effective rate for display")


class DutyCalculationRequest(BaseModel):
    """
    Request schema for duty calculation.
    
    Contains parameters needed to calculate duty amounts.
    """
    
    hs_code: str = Field(
        ...,
        description="HS code to calculate duty for",
        example="0101210000"
    )
    customs_value: Decimal = Field(
        ...,
        gt=0,
        description="Customs value in AUD",
        example=10000.00
    )
    quantity: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Quantity for specific duties",
        example=100.0
    )
    quantity_unit: Optional[str] = Field(
        None,
        description="Unit of quantity (kg, litres, etc.)",
        example="kg"
    )
    
    @field_validator('hs_code')
    @classmethod
    def validate_hs_code(cls, v):
        """Validate HS code format."""
        return HSCodeValidator.validate_hs_code(v)
    
    @field_validator('customs_value')
    @classmethod
    def validate_customs_value(cls, v):
        """Validate customs value is positive."""
        if v <= 0:
            raise ValueError("Customs value must be positive")
        return v.quantize(Decimal('0.01'))
    
    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v):
        """Validate quantity is positive if provided."""
        if v is not None and v <= 0:
            raise ValueError("Quantity must be positive")
        return v


class DutyCalculationResult(BaseModel):
    """
    Result schema for duty calculation.
    
    Contains calculated duty amounts and details.
    """
    
    hs_code: str = Field(description="HS code")
    customs_value: Decimal = Field(description="Customs value used")
    quantity: Optional[Decimal] = Field(None, description="Quantity used")
    
    # Duty rate information
    general_rate: Optional[Decimal] = Field(None, description="General duty rate applied")
    unit_type: Optional[str] = Field(None, description="Type of duty")
    rate_text: Optional[str] = Field(None, description="Rate text")
    
    # Calculated amounts
    duty_amount: Optional[Decimal] = Field(
        None,
        description="Calculated duty amount in AUD"
    )
    effective_rate: Optional[Decimal] = Field(
        None,
        description="Effective rate as percentage of customs value"
    )
    
    # Calculation details
    calculation_method: Optional[str] = Field(
        None,
        description="Method used for calculation (ad_valorem, specific, etc.)"
    )
    calculation_notes: Optional[str] = Field(
        None,
        description="Additional notes about the calculation"
    )
    
    # Status
    is_calculable: bool = Field(
        description="Whether duty could be calculated"
    )
    error_message: Optional[str] = Field(
        None,
        description="Error message if calculation failed"
    )


class DutyCalculationResponse(BaseModel):
    """
    Complete response for duty calculation requests.
    
    Contains calculation results and metadata.
    """
    
    request: DutyCalculationRequest = Field(
        description="Original calculation request"
    )
    result: DutyCalculationResult = Field(
        description="Calculation result"
    )
    
    # Additional context
    tariff_description: Optional[str] = Field(
        None,
        description="Description of the tariff code"
    )
    alternative_rates: Optional[List[DutyRateSummary]] = Field(
        None,
        description="Alternative duty rates (e.g., FTA rates)"
    )
    
    # Metadata
    calculation_timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="When the calculation was performed"
    )


class DutyRateComparison(BaseModel):
    """
    Schema for comparing multiple duty rates.
    
    Used for comparing general rates with FTA rates.
    """
    
    hs_code: str = Field(description="HS code")
    tariff_description: Optional[str] = Field(None, description="Tariff description")
    
    # General duty
    general_rate: Optional[Decimal] = Field(None, description="General duty rate")
    general_amount: Optional[Decimal] = Field(None, description="General duty amount")
    
    # Best FTA rate
    best_fta_rate: Optional[Decimal] = Field(None, description="Best available FTA rate")
    best_fta_amount: Optional[Decimal] = Field(None, description="Best FTA duty amount")
    best_fta_agreement: Optional[str] = Field(None, description="Best FTA agreement")
    best_fta_country: Optional[str] = Field(None, description="Best FTA country")
    
    # Savings
    potential_savings: Optional[Decimal] = Field(
        None,
        description="Potential savings using FTA rate"
    )
    savings_percentage: Optional[Decimal] = Field(
        None,
        description="Savings as percentage of general duty"
    )
    
    # Recommendation
    recommended_rate_type: str = Field(
        description="Recommended rate type (general or fta)"
    )
    recommendation_reason: Optional[str] = Field(
        None,
        description="Reason for the recommendation"
    )


class DutyRateListResponse(BaseModel):
    """
    Response schema for duty rate lists.
    
    Contains list of duty rates with pagination.
    """
    
    rates: List[DutyRateSummary] = Field(
        description="List of duty rates"
    )
    total: int = Field(
        description="Total number of rates"
    )
    
    # Filters applied
    hs_code_filter: Optional[str] = Field(
        None,
        description="HS code filter applied"
    )
    rate_range_filter: Optional[Dict[str, Decimal]] = Field(
        None,
        description="Rate range filter applied"
    )
    unit_type_filter: Optional[str] = Field(
        None,
        description="Unit type filter applied"
    )


class DutyRateStatistics(BaseModel):
    """
    Statistics schema for duty rates.
    
    Provides aggregate statistics about duty rates.
    """
    
    total_rates: int = Field(description="Total number of duty rates")
    
    # Rate distribution
    ad_valorem_count: int = Field(description="Number of ad valorem rates")
    specific_count: int = Field(description="Number of specific rates")
    compound_count: int = Field(description="Number of compound rates")
    free_rates_count: int = Field(description="Number of free (0%) rates")
    
    # Rate statistics
    average_rate: Optional[Decimal] = Field(None, description="Average duty rate")
    median_rate: Optional[Decimal] = Field(None, description="Median duty rate")
    min_rate: Optional[Decimal] = Field(None, description="Minimum duty rate")
    max_rate: Optional[Decimal] = Field(None, description="Maximum duty rate")
    
    # Coverage
    codes_with_rates: int = Field(description="Number of HS codes with duty rates")
    codes_without_rates: int = Field(description="Number of HS codes without duty rates")
    coverage_percentage: Decimal = Field(description="Percentage of codes with rates")
    
    # Last updated
    last_updated: Optional[datetime] = Field(
        None,
        description="When statistics were last calculated"
    )