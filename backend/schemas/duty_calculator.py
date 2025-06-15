"""
Duty calculator schemas for the Customs Broker Portal.

This module contains Pydantic schemas for the duty calculator service,
including request/response schemas for comprehensive duty calculations.
"""

from datetime import date, datetime
from typing import Optional, List, Dict, Any
from decimal import Decimal

from pydantic import BaseModel, Field, field_validator, ConfigDict

from .common import BaseSchema, HSCodeValidator, CountryCodeValidator


class DutyCalculationRequest(BaseModel):
    """
    Request schema for duty calculation.
    
    Based on the DutyCalculationInput dataclass from the service layer.
    """
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: str,
            date: lambda v: v.isoformat() if v else None
        }
    )
    
    hs_code: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="HS code for duty calculation",
        example="8471.30.00"
    )
    country_code: str = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Country of origin code (ISO 3166-1)",
        example="CHN"
    )
    customs_value: Decimal = Field(
        ...,
        gt=0,
        description="Customs value in AUD",
        example="1000.00"
    )
    quantity: Optional[Decimal] = Field(
        None,
        gt=0,
        description="Quantity for specific duty calculations",
        example="1.0"
    )
    calculation_date: Optional[date] = Field(
        None,
        description="Date for rate validity (defaults to today)",
        example="2024-01-15"
    )
    exporter_name: Optional[str] = Field(
        None,
        max_length=200,
        description="Exporter name for anti-dumping duty checks",
        example="ABC Manufacturing Co."
    )
    value_basis: str = Field(
        default="CIF",
        description="Value basis for customs valuation",
        example="CIF"
    )
    
    @field_validator('hs_code')
    @classmethod
    def validate_hs_code(cls, v):
        """Validate HS code format."""
        return HSCodeValidator.validate_hs_code(v)
    
    @field_validator('country_code')
    @classmethod
    def validate_country_code(cls, v):
        """Validate country code format."""
        return CountryCodeValidator.validate_country_code(v)
    
    @field_validator('value_basis')
    @classmethod
    def validate_value_basis(cls, v):
        """Validate value basis."""
        valid_bases = ["FOB", "CIF", "CFR", "EXW", "DDP", "DDU"]
        if v.upper() not in valid_bases:
            raise ValueError(f"Value basis must be one of: {', '.join(valid_bases)}")
        return v.upper()


class DutyComponentResponse(BaseModel):
    """
    Response schema for individual duty components.
    
    Based on the DutyComponent dataclass from the service layer.
    """
    
    model_config = ConfigDict(
        json_encoders={Decimal: str}
    )
    
    duty_type: str = Field(
        description="Type of duty component",
        example="General Duty"
    )
    rate: Optional[Decimal] = Field(
        None,
        description="Duty rate percentage",
        example="5.0"
    )
    amount: Decimal = Field(
        description="Calculated duty amount in AUD",
        example="50.00"
    )
    description: str = Field(
        description="Human-readable description of the duty",
        example="General Duty (MFN) - 5.0%"
    )
    basis: str = Field(
        description="Calculation basis (Ad Valorem, Specific, etc.)",
        example="Ad Valorem"
    )
    calculation_details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional calculation details and metadata"
    )


class DutyCalculationResponse(BaseModel):
    """
    Complete response schema for duty calculations.
    
    Based on the DutyCalculationResult dataclass from the service layer.
    """
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: str,
            date: lambda v: v.isoformat() if v else None
        }
    )
    
    # Input parameters
    hs_code: str = Field(description="HS code used for calculation")
    country_code: str = Field(description="Country code used for calculation")
    customs_value: Decimal = Field(description="Customs value in AUD")
    
    # Duty components
    general_duty: Optional[DutyComponentResponse] = Field(
        None,
        description="General/MFN duty component"
    )
    fta_duty: Optional[DutyComponentResponse] = Field(
        None,
        description="FTA preferential duty component"
    )
    anti_dumping_duty: Optional[DutyComponentResponse] = Field(
        None,
        description="Anti-dumping duty component"
    )
    tco_exemption: Optional[DutyComponentResponse] = Field(
        None,
        description="TCO exemption component"
    )
    
    # GST calculation
    gst_component: Optional[DutyComponentResponse] = Field(
        None,
        description="GST calculation component"
    )
    
    # Totals
    total_duty: Decimal = Field(
        description="Total duty amount in AUD",
        example="50.00"
    )
    duty_inclusive_value: Decimal = Field(
        description="Customs value plus duties in AUD",
        example="1050.00"
    )
    total_gst: Decimal = Field(
        description="Total GST amount in AUD",
        example="105.00"
    )
    total_amount: Decimal = Field(
        description="Total amount payable (duties + GST) in AUD",
        example="1155.00"
    )
    
    # Best rate analysis
    best_rate_type: str = Field(
        description="Type of best applicable rate",
        example="fta"
    )
    potential_savings: Decimal = Field(
        description="Potential savings compared to general rate in AUD",
        example="25.00"
    )
    
    # Calculation breakdown
    calculation_steps: List[str] = Field(
        default_factory=list,
        description="Step-by-step calculation breakdown"
    )
    compliance_notes: List[str] = Field(
        default_factory=list,
        description="Compliance requirements and notes"
    )
    warnings: List[str] = Field(
        default_factory=list,
        description="Important warnings and considerations"
    )


class DutyRateResponse(BaseModel):
    """
    Response schema for duty rate information.
    """
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: str,
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }
    )
    
    id: int = Field(description="Duty rate ID")
    hs_code: str = Field(description="HS code")
    rate_type: str = Field(description="Type of duty rate")
    general_rate: Optional[Decimal] = Field(None, description="General duty rate percentage")
    rate_text: Optional[str] = Field(None, description="Rate description text")
    unit_type: Optional[str] = Field(None, description="Unit type for specific duties")
    is_ad_valorem: bool = Field(description="Whether rate is ad valorem")
    is_specific: bool = Field(description="Whether rate is specific")
    effective_date: Optional[date] = Field(None, description="Effective date")
    expiry_date: Optional[date] = Field(None, description="Expiry date")


class FtaRateResponse(BaseModel):
    """
    Response schema for FTA rate information.
    """
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: str,
            date: lambda v: v.isoformat() if v else None
        }
    )
    
    id: int = Field(description="FTA rate ID")
    hs_code: str = Field(description="HS code")
    country_code: str = Field(description="Country code")
    fta_code: str = Field(description="FTA agreement code")
    preferential_rate: Optional[Decimal] = Field(None, description="Preferential rate percentage")
    rate_text: Optional[str] = Field(None, description="Rate description")
    staging_category: Optional[str] = Field(None, description="Staging category")
    effective_date: Optional[date] = Field(None, description="Effective date")
    elimination_date: Optional[date] = Field(None, description="Elimination date")
    trade_agreement: Optional[Dict[str, Any]] = Field(None, description="Trade agreement details")


class DutyBreakdownResponse(BaseModel):
    """
    Response schema for detailed duty calculation breakdown.
    """
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: str,
            date: lambda v: v.isoformat() if v else None
        }
    )
    
    input_parameters: Dict[str, Any] = Field(
        description="Input parameters used for calculation"
    )
    duty_components: Dict[str, DutyComponentResponse] = Field(
        description="All calculated duty components"
    )
    totals: Dict[str, str] = Field(
        description="Total amounts (as strings for precision)"
    )
    best_rate_analysis: Dict[str, str] = Field(
        description="Best rate analysis and savings"
    )
    calculation_steps: List[str] = Field(
        description="Step-by-step calculation process"
    )
    compliance_notes: List[str] = Field(
        description="Compliance requirements and notes"
    )
    warnings: List[str] = Field(
        description="Important warnings and considerations"
    )


class TcoExemptionResponse(BaseModel):
    """
    Response schema for TCO exemption information.
    """
    
    model_config = ConfigDict(
        json_encoders={
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }
    )
    
    id: int = Field(description="TCO ID")
    tco_number: str = Field(description="TCO number")
    hs_code: str = Field(description="HS code")
    description: str = Field(description="TCO description")
    is_current: bool = Field(description="Whether TCO is current")
    effective_date: Optional[date] = Field(None, description="Effective date")
    expiry_date: Optional[date] = Field(None, description="Expiry date")
    days_until_expiry: Optional[int] = Field(None, description="Days until expiry")


class AntiDumpingDutyResponse(BaseModel):
    """
    Response schema for anti-dumping duty information.
    """
    
    model_config = ConfigDict(
        json_encoders={
            Decimal: str,
            date: lambda v: v.isoformat() if v else None,
            datetime: lambda v: v.isoformat() if v else None
        }
    )
    
    id: int = Field(description="Anti-dumping duty ID")
    case_number: str = Field(description="Case number")
    hs_code: str = Field(description="HS code")
    country_code: str = Field(description="Country code")
    duty_type: str = Field(description="Type of duty")
    duty_rate: Optional[Decimal] = Field(None, description="Ad valorem duty rate")
    duty_amount: Optional[Decimal] = Field(None, description="Specific duty amount")
    unit: Optional[str] = Field(None, description="Unit for specific duty")
    exporter_name: Optional[str] = Field(None, description="Specific exporter")
    effective_date: Optional[date] = Field(None, description="Effective date")
    expiry_date: Optional[date] = Field(None, description="Expiry date")
    is_active: bool = Field(description="Whether duty is active")


class DutyRatesListResponse(BaseModel):
    """
    Response schema for listing duty rates for an HS code.
    """
    
    hs_code: str = Field(description="HS code")
    general_rates: List[DutyRateResponse] = Field(
        default_factory=list,
        description="General duty rates"
    )
    fta_rates: List[FtaRateResponse] = Field(
        default_factory=list,
        description="FTA preferential rates"
    )
    anti_dumping_duties: List[AntiDumpingDutyResponse] = Field(
        default_factory=list,
        description="Anti-dumping duties"
    )
    tco_exemptions: List[TcoExemptionResponse] = Field(
        default_factory=list,
        description="TCO exemptions"
    )


class ErrorResponse(BaseModel):
    """
    Error response schema.
    """
    
    error: str = Field(description="Error type")
    message: str = Field(description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")


# Request schemas for specific endpoints
class FtaRateRequest(BaseModel):
    """
    Request schema for FTA rate lookup.
    """
    
    hs_code: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="HS code"
    )
    country_code: str = Field(
        ...,
        min_length=2,
        max_length=3,
        description="Country code"
    )
    calculation_date: Optional[date] = Field(
        None,
        description="Date for rate validity"
    )
    
    @field_validator('hs_code')
    @classmethod
    def validate_hs_code(cls, v):
        return HSCodeValidator.validate_hs_code(v)
    
    @field_validator('country_code')
    @classmethod
    def validate_country_code(cls, v):
        return CountryCodeValidator.validate_country_code(v)


class TcoCheckRequest(BaseModel):
    """
    Request schema for TCO exemption check.
    """
    
    hs_code: str = Field(
        ...,
        min_length=2,
        max_length=10,
        description="HS code"
    )
    calculation_date: Optional[date] = Field(
        None,
        description="Date for TCO validity"
    )
    
    @field_validator('hs_code')
    @classmethod
    def validate_hs_code(cls, v):
        return HSCodeValidator.validate_hs_code(v)