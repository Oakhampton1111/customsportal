"""
FTA rate schemas for the Customs Broker Portal.

This module contains Pydantic schemas for FtaRate and TradeAgreement models,
including request/response schemas, rate calculations, and origin requirements.
"""

from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, model_validator

from .common import (
    BaseSchema, HSCodeValidator, CountryCodeValidator, 
    FTACodeValidator, RateValidator
)


class TradeAgreementBase(BaseModel):
    """
    Base schema for TradeAgreement with core fields.
    
    Contains the essential fields for trade agreement information.
    """
    
    fta_code: str = Field(
        ...,
        min_length=3,
        max_length=10,
        description="Unique FTA code",
        example="AUSFTA"
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Full name of the trade agreement",
        example="Australia-United States Free Trade Agreement"
    )
    entry_force_date: Optional[date] = Field(
        None,
        description="Date when the agreement entered into force",
        example="2005-01-01"
    )
    status: str = Field(
        default="active",
        max_length=20,
        description="Current status of the agreement",
        example="active"
    )
    agreement_url: Optional[str] = Field(
        None,
        description="URL to the official agreement document"
    )
    
    @field_validator('fta_code')

    
    @classmethod
    def validate_fta_code(cls, v):
        """Validate FTA code format."""
        return FTACodeValidator.validate_fta_code(v)
    
    @field_validator('status')

    
    @classmethod
    def validate_status(cls, v):
        """Validate status is one of allowed values."""
        allowed_statuses = ['active', 'suspended', 'terminated', 'pending']
        if v not in allowed_statuses:
            raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v
    
    @field_validator('agreement_url')

    
    @classmethod
    def validate_agreement_url(cls, v):
        """Validate agreement URL format."""
        if v is not None:
            if not v.startswith(('http://', 'https://')):
                raise ValueError("Agreement URL must start with http:// or https://")
        return v


class TradeAgreementCreate(TradeAgreementBase):
    """
    Schema for creating new trade agreements.
    
    Inherits from TradeAgreementBase with any creation-specific validations.
    """
    pass


class TradeAgreementUpdate(BaseModel):
    """
    Schema for updating existing trade agreements.
    
    All fields are optional to support partial updates.
    """
    
    full_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=200,
        description="Full name of the trade agreement"
    )
    entry_force_date: Optional[date] = Field(
        None,
        description="Date when the agreement entered into force"
    )
    status: Optional[str] = Field(
        None,
        max_length=20,
        description="Current status of the agreement"
    )
    agreement_url: Optional[str] = Field(
        None,
        description="URL to the official agreement document"
    )
    
    @field_validator('status')

    
    @classmethod
    def validate_status(cls, v):
        """Validate status is one of allowed values."""
        if v is not None:
            allowed_statuses = ['active', 'suspended', 'terminated', 'pending']
            if v not in allowed_statuses:
                raise ValueError(f"Status must be one of: {', '.join(allowed_statuses)}")
        return v


class TradeAgreementResponse(TradeAgreementBase, BaseSchema):
    """
    Complete response schema for trade agreements.
    
    Includes all fields plus computed properties.
    """
    
    # Computed properties from the model
    is_active: Optional[bool] = Field(
        None,
        description="Whether the trade agreement is currently active"
    )
    is_in_force: Optional[bool] = Field(
        None,
        description="Whether the agreement has entered into force"
    )
    
    # Related data counts
    fta_rates_count: Optional[int] = Field(
        None,
        description="Number of FTA rates under this agreement"
    )
    countries_count: Optional[int] = Field(
        None,
        description="Number of countries covered by this agreement"
    )


class FtaRateBase(BaseModel):
    """
    Base schema for FtaRate with core fields.
    
    Contains the essential fields shared across create, update, and response schemas.
    """
    
    hs_code: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="HS code this FTA rate applies to",
        example="0101210000"
    )
    fta_code: str = Field(
        ...,
        min_length=3,
        max_length=10,
        description="FTA code",
        example="AUSFTA"
    )
    country_code: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="ISO 3166-1 alpha-3 country code",
        example="USA"
    )
    preferential_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=1000,
        description="Preferential duty rate as decimal percentage",
        example=0.00
    )
    rate_type: Optional[str] = Field(
        None,
        max_length=20,
        description="Type of preferential rate",
        example="ad_valorem"
    )
    staging_category: Optional[str] = Field(
        None,
        max_length=10,
        description="FTA staging category for tariff elimination",
        example="A"
    )
    effective_date: Optional[date] = Field(
        None,
        description="Date when the preferential rate becomes effective",
        example="2005-01-01"
    )
    elimination_date: Optional[date] = Field(
        None,
        description="Date when tariff reaches zero under FTA",
        example="2015-01-01"
    )
    quota_quantity: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Quota quantity if applicable",
        example=1000000.00
    )
    quota_unit: Optional[str] = Field(
        None,
        max_length=20,
        description="Unit for quota quantity",
        example="tonnes"
    )
    safeguard_applicable: bool = Field(
        default=False,
        description="Whether safeguard measures apply"
    )
    rule_of_origin: Optional[str] = Field(
        None,
        description="FTA-specific rules of origin requirements"
    )
    
    @field_validator('hs_code')

    
    @classmethod
    def validate_hs_code(cls, v):
        """Validate HS code format."""
        return HSCodeValidator.validate_hs_code(v)
    
    @field_validator('fta_code')

    
    @classmethod
    def validate_fta_code(cls, v):
        """Validate FTA code format."""
        return FTACodeValidator.validate_fta_code(v)
    
    @field_validator('country_code')

    
    @classmethod
    def validate_country_code(cls, v):
        """Validate country code format."""
        return CountryCodeValidator.validate_country_code(v)
    
    @field_validator('preferential_rate')

    
    @classmethod
    def validate_preferential_rate(cls, v):
        """Validate preferential rate value."""
        return RateValidator.validate_rate(v)
    
    @field_validator('staging_category')

    
    @classmethod
    def validate_staging_category(cls, v):
        """Validate staging category."""
        if v is not None:
            allowed_categories = ['Base', 'A', 'B', 'C', 'D', 'E']
            if v not in allowed_categories:
                raise ValueError(f"Staging category must be one of: {', '.join(allowed_categories)}")
        return v
    
    @model_validator(mode='after')
    def validate_date_consistency(self):
        """Validate date consistency."""
        effective_date = self.effective_date
        elimination_date = self.elimination_date
        
        if effective_date and elimination_date:
            if elimination_date <= effective_date:
                raise ValueError("Elimination date must be after effective date")
        
        return self
    
    @model_validator(mode='after')
    def validate_quota_consistency(self):
        """Validate quota fields consistency."""
        quota_quantity = self.quota_quantity
        quota_unit = self.quota_unit
        
        if quota_quantity is not None and quota_quantity > 0:
            if not quota_unit:
                raise ValueError("Quota unit is required when quota quantity is specified")
        
        return self


class FtaRateCreate(FtaRateBase):
    """
    Schema for creating new FTA rates.
    
    Inherits from FtaRateBase with any creation-specific validations.
    """
    pass


class FtaRateUpdate(BaseModel):
    """
    Schema for updating existing FTA rates.
    
    All fields are optional to support partial updates.
    """
    
    preferential_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        le=1000,
        description="Preferential duty rate as decimal percentage"
    )
    rate_type: Optional[str] = Field(
        None,
        max_length=20,
        description="Type of preferential rate"
    )
    staging_category: Optional[str] = Field(
        None,
        max_length=10,
        description="FTA staging category for tariff elimination"
    )
    effective_date: Optional[date] = Field(
        None,
        description="Date when the preferential rate becomes effective"
    )
    elimination_date: Optional[date] = Field(
        None,
        description="Date when tariff reaches zero under FTA"
    )
    quota_quantity: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Quota quantity if applicable"
    )
    quota_unit: Optional[str] = Field(
        None,
        max_length=20,
        description="Unit for quota quantity"
    )
    safeguard_applicable: Optional[bool] = Field(
        None,
        description="Whether safeguard measures apply"
    )
    rule_of_origin: Optional[str] = Field(
        None,
        description="FTA-specific rules of origin requirements"
    )
    
    @field_validator('preferential_rate')

    
    @classmethod
    def validate_preferential_rate(cls, v):
        """Validate preferential rate value."""
        return RateValidator.validate_rate(v)


class FtaRateResponse(FtaRateBase, BaseSchema):
    """
    Complete response schema for FTA rates.
    
    Includes all fields plus computed properties.
    """
    
    id: int = Field(description="Primary key")
    
    # Computed properties from the model
    is_currently_effective: Optional[bool] = Field(
        None,
        description="Whether the FTA rate is currently effective"
    )
    is_eliminated: Optional[bool] = Field(
        None,
        description="Whether the tariff has been eliminated (reached zero)"
    )
    is_quota_applicable: Optional[bool] = Field(
        None,
        description="Whether quota restrictions apply to this rate"
    )
    effective_rate: Optional[Decimal] = Field(
        None,
        description="Effective preferential rate, considering elimination"
    )
    staging_description: Optional[str] = Field(
        None,
        description="Human-readable description of the staging category"
    )
    
    # Related data
    tariff_code_description: Optional[str] = Field(
        None,
        description="Description of the associated tariff code"
    )
    trade_agreement_name: Optional[str] = Field(
        None,
        description="Full name of the trade agreement"
    )


class FtaRateSummary(BaseModel):
    """
    Summary schema for FTA rates in lists.
    
    Contains minimal fields for efficient list responses.
    """
    
    model_config = {"from_attributes": True}
    
    id: int = Field(description="Primary key")
    hs_code: str = Field(description="HS code")
    fta_code: str = Field(description="FTA code")
    country_code: str = Field(description="Country code")
    preferential_rate: Optional[Decimal] = Field(None, description="Preferential rate")
    effective_date: Optional[date] = Field(None, description="Effective date")
    is_currently_effective: Optional[bool] = Field(None, description="Currently effective")


class FtaRateSearchRequest(BaseModel):
    """
    Search request schema for FTA rates.
    
    Provides filtering and search capabilities for FTA rates.
    """
    
    # Basic filters
    hs_code: Optional[str] = Field(
        None,
        description="Filter by HS code"
    )
    fta_code: Optional[str] = Field(
        None,
        description="Filter by FTA code"
    )
    country_code: Optional[str] = Field(
        None,
        description="Filter by country code"
    )
    
    # Rate filters
    max_rate: Optional[Decimal] = Field(
        None,
        ge=0,
        description="Maximum preferential rate"
    )
    staging_category: Optional[str] = Field(
        None,
        description="Filter by staging category"
    )
    
    # Date filters
    effective_on_date: Optional[date] = Field(
        None,
        description="Filter rates effective on specific date"
    )
    currently_effective: Optional[bool] = Field(
        None,
        description="Filter currently effective rates"
    )
    
    # Special filters
    has_quota: Optional[bool] = Field(
        None,
        description="Filter rates with quota restrictions"
    )
    safeguard_applicable: Optional[bool] = Field(
        None,
        description="Filter rates with safeguard measures"
    )
    
    @field_validator('hs_code')

    
    @classmethod
    def validate_hs_code(cls, v):
        """Validate HS code format."""
        if v:
            return HSCodeValidator.validate_hs_code(v)
        return v


class FtaRateComparison(BaseModel):
    """
    Schema for comparing FTA rates across agreements.
    
    Used for finding the best available FTA rate for a product.
    """
    
    hs_code: str = Field(description="HS code")
    tariff_description: Optional[str] = Field(None, description="Tariff description")
    
    # Available rates
    available_rates: List[FtaRateSummary] = Field(
        description="All available FTA rates for this HS code"
    )
    
    # Best rate
    best_rate: Optional[FtaRateSummary] = Field(
        None,
        description="Best available FTA rate"
    )
    best_rate_savings: Optional[Decimal] = Field(
        None,
        description="Savings compared to general duty rate"
    )
    
    # Analysis
    total_agreements: int = Field(
        description="Total number of agreements with rates for this code"
    )
    currently_effective_count: int = Field(
        description="Number of currently effective rates"
    )
    
    # Recommendations
    recommended_country: Optional[str] = Field(
        None,
        description="Recommended country for sourcing"
    )
    recommendation_reason: Optional[str] = Field(
        None,
        description="Reason for the recommendation"
    )


class OriginRequirement(BaseModel):
    """
    Schema for rules of origin requirements.
    
    Represents origin requirements for FTA rates.
    """
    
    fta_code: str = Field(description="FTA code")
    hs_code: str = Field(description="HS code")
    requirement_text: str = Field(description="Full text of origin requirement")
    
    # Parsed requirements (if available)
    change_in_classification: Optional[bool] = Field(
        None,
        description="Whether change in tariff classification is required"
    )
    regional_value_content: Optional[Decimal] = Field(
        None,
        description="Required regional value content percentage"
    )
    specific_processes: Optional[List[str]] = Field(
        None,
        description="Specific manufacturing processes required"
    )
    
    # Compliance
    complexity_score: Optional[int] = Field(
        None,
        ge=1,
        le=5,
        description="Complexity score (1=simple, 5=complex)"
    )
    documentation_required: Optional[List[str]] = Field(
        None,
        description="Required documentation for compliance"
    )


class FtaRateCalculationRequest(BaseModel):
    """
    Request schema for FTA rate calculation.
    
    Contains parameters needed to calculate FTA duty amounts.
    """
    
    hs_code: str = Field(
        ...,
        description="HS code to calculate FTA duty for",
        example="0101210000"
    )
    country_of_origin: str = Field(
        ...,
        min_length=3,
        max_length=3,
        description="Country of origin (ISO 3166-1 alpha-3)",
        example="USA"
    )
    customs_value: Decimal = Field(
        ...,
        gt=0,
        description="Customs value in AUD",
        example=10000.00
    )
    calculation_date: Optional[date] = Field(
        None,
        description="Date for calculation (default: today)",
        example="2024-01-01"
    )
    
    @field_validator('hs_code')

    
    @classmethod
    def validate_hs_code(cls, v):
        """Validate HS code format."""
        return HSCodeValidator.validate_hs_code(v)
    
    @field_validator('country_of_origin')

    
    @classmethod
    def validate_country_of_origin(cls, v):
        """Validate country code format."""
        return CountryCodeValidator.validate_country_code(v)


class FtaRateCalculationResult(BaseModel):
    """
    Result schema for FTA rate calculation.
    
    Contains calculated FTA duty amounts and details.
    """
    
    hs_code: str = Field(description="HS code")
    country_of_origin: str = Field(description="Country of origin")
    customs_value: Decimal = Field(description="Customs value used")
    calculation_date: date = Field(description="Date of calculation")
    
    # Available FTA rates
    available_fta_rates: List[FtaRateSummary] = Field(
        description="All available FTA rates for this country"
    )
    
    # Best rate
    best_fta_rate: Optional[FtaRateSummary] = Field(
        None,
        description="Best available FTA rate"
    )
    fta_duty_amount: Optional[Decimal] = Field(
        None,
        description="Calculated FTA duty amount in AUD"
    )
    
    # Comparison with general duty
    general_duty_rate: Optional[Decimal] = Field(
        None,
        description="General duty rate for comparison"
    )
    general_duty_amount: Optional[Decimal] = Field(
        None,
        description="General duty amount for comparison"
    )
    potential_savings: Optional[Decimal] = Field(
        None,
        description="Potential savings using FTA rate"
    )
    
    # Origin requirements
    origin_requirements: Optional[OriginRequirement] = Field(
        None,
        description="Rules of origin requirements"
    )
    
    # Status
    is_fta_applicable: bool = Field(
        description="Whether FTA rate is applicable"
    )
    compliance_notes: Optional[str] = Field(
        None,
        description="Notes about FTA compliance requirements"
    )


class FtaRateListResponse(BaseModel):
    """
    Response schema for FTA rate lists.
    
    Contains list of FTA rates with metadata.
    """
    
    rates: List[FtaRateSummary] = Field(
        description="List of FTA rates"
    )
    total: int = Field(
        description="Total number of rates"
    )
    
    # Aggregations
    agreements_represented: List[str] = Field(
        description="List of FTA codes represented in results"
    )
    countries_represented: List[str] = Field(
        description="List of country codes represented in results"
    )
    
    # Statistics
    average_rate: Optional[Decimal] = Field(
        None,
        description="Average preferential rate"
    )
    free_rates_count: int = Field(
        description="Number of free (0%) rates"
    )
    currently_effective_count: int = Field(
        description="Number of currently effective rates"
    )


class TradeAgreementSummary(BaseModel):
    """
    Summary schema for trade agreements in lists.
    
    Contains minimal fields for efficient list responses.
    """
    
    model_config = {"from_attributes": True}
    
    fta_code: str = Field(description="FTA code")
    full_name: str = Field(description="Full name")
    status: str = Field(description="Status")
    entry_force_date: Optional[date] = Field(None, description="Entry into force date")
    is_active: Optional[bool] = Field(None, description="Is currently active")
    fta_rates_count: Optional[int] = Field(None, description="Number of FTA rates")