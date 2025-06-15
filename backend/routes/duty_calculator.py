"""
Duty calculator API routes for the Customs Broker Portal.

This module implements comprehensive duty calculation endpoints including
general rates, FTA rates, anti-dumping duties, TCO exemptions, and GST calculations.
"""

import logging
import time
from typing import List, Optional, Dict, Any
from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import SQLAlchemyError

from database import get_async_session
from services.duty_calculator import DutyCalculatorService, DutyComponent
from models.duty import DutyRate
from models.fta import FtaRate
from models.dumping import DumpingDuty
from models.tco import Tco
from models.hierarchy import TradeAgreement
from models.tariff import TariffCode
from schemas.duty_calculator import (
    DutyCalculationRequest, DutyCalculationResponse, DutyComponentResponse,
    DutyBreakdownResponse, DutyRatesListResponse, DutyRateResponse,
    FtaRateResponse, TcoExemptionResponse, AntiDumpingDutyResponse,
    FtaRateRequest, TcoCheckRequest, ErrorResponse
)

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/duty", tags=["Duty Calculator"])


@router.post("/calculate", response_model=DutyCalculationResponse)
async def calculate_duty(
    request: DutyCalculationRequest,
    db: AsyncSession = Depends(get_async_session)
) -> DutyCalculationResponse:
    """
    Calculate comprehensive duty amount for customs value.
    
    Performs complete duty calculation including:
    - General/MFN duty rates
    - FTA preferential rates
    - Anti-dumping duties
    - TCO exemptions
    - GST calculations
    - Best rate analysis and potential savings
    
    Args:
        request: Duty calculation request parameters
        
    Returns:
        Comprehensive duty calculation result with all components
        
    Raises:
        HTTPException: 400 for validation errors, 500 for calculation errors
    """
    try:
        start_time = time.time()
        logger.info(f"Calculating duty for HS code {request.hs_code}, country {request.country_code}")
        
        # Initialize duty calculator service
        calculator = DutyCalculatorService()
        
        # Convert request to service input
        calculation_input = DutyCalculationInput(
            hs_code=request.hs_code,
            country_code=request.country_code,
            customs_value=request.customs_value,
            quantity=request.quantity,
            calculation_date=request.calculation_date or date.today(),
            exporter_name=request.exporter_name,
            value_basis=request.value_basis
        )
        
        # Perform calculation
        result = await calculator.calculate_comprehensive_duty(db, calculation_input)
        
        # Convert service result to response schema
        response = DutyCalculationResponse(
            hs_code=result.hs_code,
            country_code=result.country_code,
            customs_value=result.customs_value,
            general_duty=_convert_duty_component(result.general_duty) if result.general_duty else None,
            fta_duty=_convert_duty_component(result.fta_duty) if result.fta_duty else None,
            anti_dumping_duty=_convert_duty_component(result.anti_dumping_duty) if result.anti_dumping_duty else None,
            tco_exemption=_convert_duty_component(result.tco_exemption) if result.tco_exemption else None,
            gst_component=_convert_duty_component(result.gst_component) if result.gst_component else None,
            total_duty=result.total_duty,
            duty_inclusive_value=result.duty_inclusive_value,
            total_gst=result.total_gst,
            total_amount=result.total_amount,
            best_rate_type=result.best_rate_type,
            potential_savings=result.potential_savings,
            calculation_steps=result.calculation_steps,
            compliance_notes=result.compliance_notes,
            warnings=result.warnings
        )
        
        execution_time = time.time() - start_time
        logger.info(f"Duty calculation completed in {execution_time:.3f}s")
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in duty calculation: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input parameters: {str(e)}"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error in duty calculation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred during duty calculation"
        )
    except Exception as e:
        logger.error(f"Unexpected error in duty calculation: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during duty calculation"
        )


@router.get("/rates/{hs_code}", response_model=DutyRatesListResponse)
async def get_duty_rates(
    hs_code: str = Path(..., description="HS code to get rates for"),
    country_code: Optional[str] = Query(None, description="Country code for FTA rates"),
    include_fta: bool = Query(True, description="Include FTA rates"),
    include_dumping: bool = Query(True, description="Include anti-dumping duties"),
    include_tco: bool = Query(True, description="Include TCO exemptions"),
    db: AsyncSession = Depends(get_async_session)
) -> DutyRatesListResponse:
    """
    Get all available duty rates for an HS code.
    
    Returns comprehensive rate information including general rates,
    FTA preferential rates, anti-dumping duties, and TCO exemptions.
    
    Args:
        hs_code: HS code to lookup rates for
        country_code: Optional country filter for FTA rates
        include_fta: Whether to include FTA rates
        include_dumping: Whether to include anti-dumping duties
        include_tco: Whether to include TCO exemptions
        
    Returns:
        Complete list of available rates and exemptions
        
    Raises:
        HTTPException: 404 if HS code not found, 500 for database errors
    """
    try:
        start_time = time.time()
        logger.info(f"Getting duty rates for HS code {hs_code}")
        
        # Clean HS code
        clean_hs_code = ''.join(c for c in hs_code if c.isdigit())
        
        response = DutyRatesListResponse(hs_code=clean_hs_code)
        
        # Get general duty rates
        general_stmt = select(DutyRate).where(DutyRate.hs_code == clean_hs_code)
        general_result = await db.execute(general_stmt)
        general_rates = general_result.scalars().all()
        
        response.general_rates = [
            DutyRateResponse(
                id=rate.id,
                hs_code=rate.hs_code,
                rate_type=rate.rate_type,
                general_rate=rate.general_rate,
                rate_text=rate.rate_text,
                unit_type=rate.unit_type,
                is_ad_valorem=rate.is_ad_valorem,
                is_specific=rate.is_specific,
                effective_date=rate.effective_date,
                expiry_date=rate.expiry_date
            )
            for rate in general_rates
        ]
        
        # Get FTA rates if requested
        if include_fta:
            fta_conditions = [FtaRate.hs_code == clean_hs_code]
            if country_code:
                fta_conditions.append(FtaRate.country_code == country_code.upper())
            
            fta_stmt = (
                select(FtaRate)
                .options(selectinload(FtaRate.trade_agreement))
                .where(and_(*fta_conditions))
            )
            fta_result = await db.execute(fta_stmt)
            fta_rates = fta_result.scalars().all()
            
            response.fta_rates = [
                FtaRateResponse(
                    id=rate.id,
                    hs_code=rate.hs_code,
                    country_code=rate.country_code,
                    fta_code=rate.fta_code,
                    preferential_rate=rate.preferential_rate,
                    rate_text=rate.rate_text,
                    staging_category=rate.staging_category,
                    effective_date=rate.effective_date,
                    elimination_date=rate.elimination_date,
                    trade_agreement={
                        "fta_code": rate.trade_agreement.fta_code,
                        "full_name": rate.trade_agreement.full_name
                    } if rate.trade_agreement else None
                )
                for rate in fta_rates
            ]
        
        # Get anti-dumping duties if requested
        if include_dumping:
            dumping_conditions = [DumpingDuty.hs_code == clean_hs_code]
            if country_code:
                dumping_conditions.append(DumpingDuty.country_code == country_code.upper())
            
            dumping_stmt = select(DumpingDuty).where(and_(*dumping_conditions))
            dumping_result = await db.execute(dumping_stmt)
            dumping_duties = dumping_result.scalars().all()
            
            response.anti_dumping_duties = [
                AntiDumpingDutyResponse(
                    id=duty.id,
                    case_number=duty.case_number,
                    hs_code=duty.hs_code,
                    country_code=duty.country_code,
                    duty_type=duty.duty_type,
                    duty_rate=duty.duty_rate,
                    duty_amount=duty.duty_amount,
                    unit=duty.unit,
                    exporter_name=duty.exporter_name,
                    effective_date=duty.effective_date,
                    expiry_date=duty.expiry_date,
                    is_active=duty.is_active
                )
                for duty in dumping_duties
            ]
        
        # Get TCO exemptions if requested
        if include_tco:
            tco_stmt = select(Tco).where(Tco.hs_code == clean_hs_code)
            tco_result = await db.execute(tco_stmt)
            tco_exemptions = tco_result.scalars().all()
            
            response.tco_exemptions = [
                TcoExemptionResponse(
                    id=tco.id,
                    tco_number=tco.tco_number,
                    hs_code=tco.hs_code,
                    description=tco.description,
                    is_current=tco.is_current,
                    effective_date=tco.effective_date,
                    expiry_date=tco.expiry_date,
                    days_until_expiry=tco.days_until_expiry() if hasattr(tco, 'days_until_expiry') else None
                )
                for tco in tco_exemptions
            ]
        
        execution_time = time.time() - start_time
        logger.info(f"Retrieved duty rates for {clean_hs_code} in {execution_time:.3f}s")
        
        return response
        
    except SQLAlchemyError as e:
        logger.error(f"Database error getting duty rates for {hs_code}: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while retrieving duty rates"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting duty rates for {hs_code}: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


@router.get("/breakdown", response_model=DutyBreakdownResponse)
async def get_calculation_breakdown(
    hs_code: str = Query(..., description="HS code"),
    country_code: str = Query(..., description="Country code"),
    customs_value: Decimal = Query(..., gt=0, description="Customs value in AUD"),
    quantity: Optional[Decimal] = Query(None, gt=0, description="Quantity"),
    calculation_date: Optional[date] = Query(None, description="Calculation date"),
    exporter_name: Optional[str] = Query(None, description="Exporter name"),
    value_basis: str = Query("CIF", description="Value basis"),
    db: AsyncSession = Depends(get_async_session)
) -> DutyBreakdownResponse:
    """
    Get detailed calculation breakdown with all steps and alternatives.
    
    Provides comprehensive breakdown of duty calculation process including
    all considered rates, calculation steps, and compliance requirements.
    
    Args:
        hs_code: HS code for calculation
        country_code: Country of origin
        customs_value: Customs value in AUD
        quantity: Optional quantity for specific duties
        calculation_date: Optional calculation date
        exporter_name: Optional exporter name
        value_basis: Value basis (default: CIF)
        
    Returns:
        Detailed calculation breakdown with all components
        
    Raises:
        HTTPException: 400 for validation errors, 500 for calculation errors
    """
    try:
        start_time = time.time()
        logger.info(f"Getting calculation breakdown for {hs_code}, {country_code}")
        
        # Initialize duty calculator service
        calculator = DutyCalculatorService()
        
        # Create calculation input
        calculation_input = DutyCalculationInput(
            hs_code=hs_code,
            country_code=country_code,
            customs_value=customs_value,
            quantity=quantity,
            calculation_date=calculation_date or date.today(),
            exporter_name=exporter_name,
            value_basis=value_basis
        )
        
        # Get detailed breakdown
        breakdown = await calculator.get_calculation_breakdown(db, calculation_input)
        
        # Convert to response schema
        response = DutyBreakdownResponse(
            input_parameters=breakdown["input_parameters"],
            duty_components={
                key: DutyComponentResponse(**component)
                for key, component in breakdown["duty_components"].items()
            },
            totals=breakdown["totals"],
            best_rate_analysis=breakdown["best_rate_analysis"],
            calculation_steps=breakdown["calculation_steps"],
            compliance_notes=breakdown["compliance_notes"],
            warnings=breakdown["warnings"]
        )
        
        execution_time = time.time() - start_time
        logger.info(f"Generated calculation breakdown in {execution_time:.3f}s")
        
        return response
        
    except ValueError as e:
        logger.error(f"Validation error in breakdown calculation: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Invalid input parameters: {str(e)}"
        )
    except SQLAlchemyError as e:
        logger.error(f"Database error in breakdown calculation: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred during breakdown calculation"
        )
    except Exception as e:
        logger.error(f"Unexpected error in breakdown calculation: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


@router.get("/fta-rates/{hs_code}/{country_code}", response_model=List[FtaRateResponse])
async def get_fta_rates(
    hs_code: str = Path(..., description="HS code"),
    country_code: str = Path(..., description="Country code"),
    calculation_date: Optional[date] = Query(None, description="Date for rate validity"),
    db: AsyncSession = Depends(get_async_session)
) -> List[FtaRateResponse]:
    """
    Get FTA preferential rates for specific HS code and country.
    
    Returns all applicable FTA rates for the specified HS code and country,
    filtered by the calculation date for validity.
    
    Args:
        hs_code: HS code to lookup
        country_code: Country code for FTA rates
        calculation_date: Optional date for rate validity check
        
    Returns:
        List of applicable FTA rates
        
    Raises:
        HTTPException: 404 if no rates found, 500 for database errors
    """
    try:
        start_time = time.time()
        logger.info(f"Getting FTA rates for {hs_code}, {country_code}")
        
        # Clean inputs
        clean_hs_code = ''.join(c for c in hs_code if c.isdigit())
        clean_country_code = country_code.upper()
        calc_date = calculation_date or date.today()
        
        # Initialize duty calculator service
        calculator = DutyCalculatorService()
        
        # Get best FTA rate (this will also do hierarchical lookup)
        best_rate = await calculator.get_best_fta_rate(db, clean_hs_code, clean_country_code, calc_date)
        
        if not best_rate:
            raise HTTPException(
                status_code=404,
                detail=f"No FTA rates found for HS code {clean_hs_code} and country {clean_country_code}"
            )
        
        # Get all applicable FTA rates for comprehensive view
        stmt = (
            select(FtaRate)
            .options(selectinload(FtaRate.trade_agreement))
            .where(
                and_(
                    FtaRate.hs_code == clean_hs_code,
                    FtaRate.country_code == clean_country_code,
                    or_(
                        FtaRate.effective_date.is_(None),
                        FtaRate.effective_date <= calc_date
                    ),
                    or_(
                        FtaRate.elimination_date.is_(None),
                        FtaRate.elimination_date > calc_date
                    )
                )
            )
            .order_by(FtaRate.preferential_rate.asc())
        )
        
        result = await db.execute(stmt)
        fta_rates = result.scalars().all()
        
        # Convert to response schema
        response = [
            FtaRateResponse(
                id=rate.id,
                hs_code=rate.hs_code,
                country_code=rate.country_code,
                fta_code=rate.fta_code,
                preferential_rate=rate.preferential_rate,
                rate_text=rate.rate_text,
                staging_category=rate.staging_category,
                effective_date=rate.effective_date,
                elimination_date=rate.elimination_date,
                trade_agreement={
                    "fta_code": rate.trade_agreement.fta_code,
                    "full_name": rate.trade_agreement.full_name
                } if rate.trade_agreement else None
            )
            for rate in fta_rates
        ]
        
        execution_time = time.time() - start_time
        logger.info(f"Retrieved {len(response)} FTA rates in {execution_time:.3f}s")
        
        return response
        
    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error getting FTA rates: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while retrieving FTA rates"
        )
    except Exception as e:
        logger.error(f"Unexpected error getting FTA rates: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


@router.get("/tco-check/{hs_code}", response_model=List[TcoExemptionResponse])
async def check_tco_exemptions(
    hs_code: str = Path(..., description="HS code"),
    calculation_date: Optional[date] = Query(None, description="Date for TCO validity"),
    db: AsyncSession = Depends(get_async_session)
) -> List[TcoExemptionResponse]:
    """
    Check for TCO exemptions applicable to an HS code.
    
    Returns all current and applicable TCO exemptions for the specified
    HS code, filtered by the calculation date.
    
    Args:
        hs_code: HS code to check for exemptions
        calculation_date: Optional date for TCO validity check
        
    Returns:
        List of applicable TCO exemptions
        
    Raises:
        HTTPException: 500 for database errors
    """
    try:
        start_time = time.time()
        logger.info(f"Checking TCO exemptions for {hs_code}")
        
        # Clean HS code
        clean_hs_code = ''.join(c for c in hs_code if c.isdigit())
        calc_date = calculation_date or date.today()
        
        # Initialize duty calculator service
        calculator = DutyCalculatorService()
        
        # Check for TCO exemption
        tco_exemption = await calculator.check_tco_exemption(db, clean_hs_code, calc_date)
        
        # Get all TCO exemptions for comprehensive view
        stmt = (
            select(Tco)
            .where(
                and_(
                    Tco.hs_code == clean_hs_code,
                    or_(
                        Tco.effective_date.is_(None),
                        Tco.effective_date <= calc_date
                    ),
                    or_(
                        Tco.expiry_date.is_(None),
                        Tco.expiry_date > calc_date
                    )
                )
            )
            .order_by(Tco.effective_date.desc())
        )
        
        result = await db.execute(stmt)
        tco_exemptions = result.scalars().all()
        
        # Convert to response schema
        response = [
            TcoExemptionResponse(
                id=tco.id,
                tco_number=tco.tco_number,
                hs_code=tco.hs_code,
                description=tco.description,
                is_current=tco.is_current,
                effective_date=tco.effective_date,
                expiry_date=tco.expiry_date,
                days_until_expiry=tco.days_until_expiry() if hasattr(tco, 'days_until_expiry') else None
            )
            for tco in tco_exemptions
        ]
        
        execution_time = time.time() - start_time
        logger.info(f"Found {len(response)} TCO exemptions in {execution_time:.3f}s")
        
        return response
        
    except SQLAlchemyError as e:
        logger.error(f"Database error checking TCO exemptions: {e}")
        raise HTTPException(
            status_code=500,
            detail="Database error occurred while checking TCO exemptions"
        )
    except Exception as e:
        logger.error(f"Unexpected error checking TCO exemptions: {e}")
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred"
        )


@router.post("/calculate-comprehensive", response_model=dict)
async def calculate_comprehensive_duties(
    hs_code: str,
    country_of_origin: str,
    customs_value: float,
    currency: str = "AUD",
    vehicle_details: Optional[dict] = None,
    alcohol_details: Optional[dict] = None,
    tobacco_details: Optional[dict] = None,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Comprehensive duty calculation including all Australian import taxes:
    - Customs duties (general and preferential)
    - GST (10%)
    - Luxury Car Tax (33% over threshold)
    - Wine Equalisation Tax (29%)
    - Tobacco Excise (complex rates)
    - Fuel Excise
    - Other applicable levies
    """
    try:
        # Calculate customs duty using existing service
        calculator = DutyCalculatorService()
        calculation_input = DutyCalculationInput(
            hs_code=hs_code,
            country_code=country_of_origin,
            customs_value=customs_value,
            quantity=1,
            calculation_date=date.today()
        )
        
        duty_result = await calculator.calculate_comprehensive_duty(db, calculation_input)
        
        # Calculate additional taxes
        lct_result = calculate_lct(hs_code, customs_value, vehicle_details)
        wet_result = calculate_wet(hs_code, customs_value, alcohol_details)
        tobacco_result = calculate_tobacco_excise(hs_code, tobacco_details)
        fuel_result = calculate_fuel_excise(hs_code, fuel_details=tobacco_details)
        other_levies = calculate_other_levies(hs_code, customs_value, product_details=tobacco_details)
        
        # Calculate GST on dutiable value
        dutiable_value = customs_value + duty_result.total_duty
        gst_amount = dutiable_value * 0.10
        
        total_landed_cost = (
            customs_value + 
            duty_result.total_duty + 
            gst_amount +
            lct_result.get('amount', 0) +
            wet_result.get('amount', 0) +
            tobacco_result.get('amount', 0) +
            fuel_result.get('amount', 0) +
            other_levies.get('total_amount', 0)
        )
        
        result = {
            'customs_value': customs_value,
            'customs_duty': {
                'amount': duty_result.total_duty,
                'rate_type': duty_result.best_rate_type,
                'details': duty_result.calculation_steps
            },
            'gst': {
                'amount': gst_amount,
                'rate': 0.10,
                'dutiable_value': dutiable_value
            },
            'luxury_car_tax': lct_result,
            'wine_equalisation_tax': wet_result,
            'tobacco_excise': tobacco_result,
            'fuel_excise': fuel_result,
            'other_levies': other_levies,
            'total_landed_cost': total_landed_cost,
            'optimization_tips': generate_enhanced_tax_optimization_tips(hs_code, customs_value, duty_result)
        }
        
        return result
        
    except Exception as e:
        logger.error(f"Error in comprehensive duty calculation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def calculate_tobacco_excise(hs_code: str, tobacco_details: dict = None) -> dict:
    """
    Calculate tobacco excise with full rate implementation.
    
    Australian tobacco excise rates (2024-25):
    - Cigarettes: $1.24780 per stick + 12.5% of value
    - Cigars: $2,495.60 per kg + 12.5% of value  
    - Other tobacco: $2,495.60 per kg + 12.5% of value
    - Loose leaf tobacco: $49.91 per kg + 12.5% of value
    """
    # Tobacco HS codes (Chapter 24)
    tobacco_hs_codes = ['2401', '2402', '2403', '2404']
    
    if not any(hs_code.startswith(code) for code in tobacco_hs_codes):
        return {'applicable': False, 'amount': 0, 'details': 'Not tobacco product'}
    
    if not tobacco_details:
        tobacco_details = {}
    
    # Default values if not provided
    quantity = tobacco_details.get('quantity', 1000)  # Default 1000 units/kg
    product_type = tobacco_details.get('product_type', 'other_tobacco')
    customs_value = tobacco_details.get('customs_value', 10000)
    
    # 2024-25 Australian tobacco excise rates
    EXCISE_RATES = {
        'cigarettes': {
            'per_stick': 1.24780,  # AUD per stick
            'ad_valorem': 0.125,   # 12.5% of value
            'unit': 'stick'
        },
        'cigars': {
            'per_kg': 2495.60,     # AUD per kg
            'ad_valorem': 0.125,   # 12.5% of value
            'unit': 'kg'
        },
        'other_tobacco': {
            'per_kg': 2495.60,     # AUD per kg
            'ad_valorem': 0.125,   # 12.5% of value
            'unit': 'kg'
        },
        'loose_leaf': {
            'per_kg': 49.91,       # AUD per kg (significantly lower rate)
            'ad_valorem': 0.125,   # 12.5% of value
            'unit': 'kg'
        },
        'chewing_tobacco': {
            'per_kg': 2495.60,     # AUD per kg
            'ad_valorem': 0.125,   # 12.5% of value
            'unit': 'kg'
        },
        'snuff': {
            'per_kg': 2495.60,     # AUD per kg
            'ad_valorem': 0.125,   # 12.5% of value
            'unit': 'kg'
        }
    }
    
    # Determine product type based on HS code if not specified
    if product_type == 'auto_detect':
        if hs_code.startswith('2402.10'):  # Cigars containing tobacco
            product_type = 'cigars'
        elif hs_code.startswith('2402.20'):  # Cigarettes containing tobacco
            product_type = 'cigarettes'
        elif hs_code.startswith('2403.1'):   # Smoking tobacco
            product_type = 'other_tobacco'
        elif hs_code.startswith('2403.91'):  # Homogenised or reconstituted tobacco
            product_type = 'other_tobacco'
        elif hs_code.startswith('2403.99'):  # Other manufactured tobacco
            if 'chewing' in tobacco_details.get('description', '').lower():
                product_type = 'chewing_tobacco'
            elif 'snuff' in tobacco_details.get('description', '').lower():
                product_type = 'snuff'
            else:
                product_type = 'other_tobacco'
        elif hs_code.startswith('2401'):     # Unmanufactured tobacco; tobacco refuse
            product_type = 'loose_leaf'
        else:
            product_type = 'other_tobacco'
    
    if product_type not in EXCISE_RATES:
        product_type = 'other_tobacco'  # Default fallback
    
    rate_info = EXCISE_RATES[product_type]
    
    # Calculate specific duty (per unit/kg)
    if product_type == 'cigarettes':
        # For cigarettes: per stick rate
        specific_duty = quantity * rate_info['per_stick']
        calculation_basis = f"{quantity} sticks × ${rate_info['per_stick']}"
    else:
        # For other tobacco: per kg rate
        weight_kg = quantity if tobacco_details.get('unit') == 'kg' else quantity / 1000  # Convert if needed
        specific_duty = weight_kg * rate_info['per_kg']
        calculation_basis = f"{weight_kg} kg × ${rate_info['per_kg']}"
    
    # Calculate ad valorem duty (percentage of value)
    ad_valorem_duty = customs_value * rate_info['ad_valorem']
    
    # Total excise = specific duty + ad valorem duty
    total_excise = specific_duty + ad_valorem_duty
    
    # Additional calculations for compliance
    effective_rate = (total_excise / customs_value) * 100 if customs_value > 0 else 0
    
    # Generate detailed breakdown
    breakdown = {
        'specific_duty': {
            'amount': specific_duty,
            'calculation': calculation_basis,
            'rate': rate_info.get('per_stick') or rate_info.get('per_kg'),
            'unit': rate_info['unit']
        },
        'ad_valorem_duty': {
            'amount': ad_valorem_duty,
            'calculation': f"${customs_value:,.2f} × {rate_info['ad_valorem']*100}%",
            'rate': rate_info['ad_valorem'],
            'basis': 'customs_value'
        },
        'total_excise': total_excise,
        'effective_rate_percent': effective_rate
    }
    
    # Compliance notes and warnings
    compliance_notes = []
    
    if product_type == 'cigarettes' and quantity > 50000:  # Large quantity
        compliance_notes.append("Large quantity import may require additional licensing and security arrangements")
    
    if total_excise > 100000:  # High value excise
        compliance_notes.append("High-value excise requires monthly payment arrangements with ATO")
        compliance_notes.append("Consider excise warehouse licensing for deferred payment")
    
    if product_type == 'loose_leaf' and total_excise > 10000:
        compliance_notes.append("Loose leaf tobacco may qualify for manufacturer licensing benefits")
    
    # Indexation warning
    compliance_notes.append("Tobacco excise rates are indexed twice yearly (March and September)")
    
    return {
        'applicable': True,
        'amount': total_excise,
        'product_type': product_type,
        'breakdown': breakdown,
        'compliance_notes': compliance_notes,
        'indexation_schedule': 'Rates indexed twice yearly (March 1 and September 1)',
        'next_indexation': 'September 1, 2024' if date.today().month < 9 else 'March 1, 2025',
        'details': f'Total tobacco excise: ${total_excise:,.2f} (Specific: ${specific_duty:,.2f} + Ad valorem: ${ad_valorem_duty:,.2f})'
    }


def calculate_fuel_excise(hs_code: str, fuel_details: dict = None) -> dict:
    """
    Calculate fuel excise for petroleum products.
    
    Australian fuel excise rates (2024-25):
    - Petrol: 48.8 cents per litre
    - Diesel: 48.8 cents per litre  
    - Aviation gasoline: 3.556 cents per litre
    - Aviation turbine fuel: 3.556 cents per litre
    - Heating oil: 48.8 cents per litre
    - Fuel oil: 10.057 cents per litre
    - LPG: 14.6 cents per litre
    """
    # Fuel HS codes (Chapter 27 - Mineral fuels, oils)
    fuel_hs_codes = ['2710', '2711', '2712', '2713', '2714', '2715']
    
    if not any(hs_code.startswith(code) for code in fuel_hs_codes):
        return {'applicable': False, 'amount': 0, 'details': 'Not petroleum fuel product'}
    
    if not fuel_details:
        fuel_details = {}
    
    # Default values if not provided
    volume_litres = fuel_details.get('volume_litres', 1000)  # Default 1000 litres
    fuel_type = fuel_details.get('fuel_type', 'auto_detect')
    end_use = fuel_details.get('end_use', 'general')  # general, aviation, marine, mining, etc.
    customs_value = fuel_details.get('customs_value', 1500)  # Default value
    
    # 2024-25 Australian fuel excise rates (cents per litre)
    EXCISE_RATES = {
        'petrol': {
            'rate_per_litre': 0.488,  # 48.8 cents per litre
            'description': 'Motor spirit (petrol)',
            'exemptions': ['aviation', 'marine_recreational']
        },
        'diesel': {
            'rate_per_litre': 0.488,  # 48.8 cents per litre  
            'description': 'Diesel fuel',
            'exemptions': ['aviation', 'marine_commercial', 'mining_off_road', 'rail']
        },
        'aviation_gasoline': {
            'rate_per_litre': 0.03556,  # 3.556 cents per litre
            'description': 'Aviation gasoline',
            'exemptions': ['international_flights']
        },
        'aviation_turbine_fuel': {
            'rate_per_litre': 0.03556,  # 3.556 cents per litre
            'description': 'Aviation turbine fuel (jet fuel)',
            'exemptions': ['international_flights']
        },
        'heating_oil': {
            'rate_per_litre': 0.488,  # 48.8 cents per litre
            'description': 'Heating oil',
            'exemptions': ['industrial_heating']
        },
        'fuel_oil': {
            'rate_per_litre': 0.10057,  # 10.057 cents per litre
            'description': 'Heavy fuel oil',
            'exemptions': ['marine_commercial', 'electricity_generation']
        },
        'lpg': {
            'rate_per_litre': 0.146,  # 14.6 cents per litre
            'description': 'Liquefied petroleum gas',
            'exemptions': ['domestic_heating', 'industrial_process']
        },
        'kerosene': {
            'rate_per_litre': 0.488,  # 48.8 cents per litre
            'description': 'Kerosene (other than aviation)',
            'exemptions': ['heating', 'lighting']
        },
        'biodiesel': {
            'rate_per_litre': 0.488,  # Same as diesel
            'description': 'Biodiesel blend',
            'exemptions': ['pure_biodiesel_b100']  # B100 may have different treatment
        }
    }
    
    # Auto-detect fuel type based on HS code if not specified
    if fuel_type == 'auto_detect':
        if hs_code.startswith('2710.12.1'):  # Motor spirit (petrol)
            fuel_type = 'petrol'
        elif hs_code.startswith('2710.12.2'):  # Aviation spirit
            fuel_type = 'aviation_gasoline'
        elif hs_code.startswith('2710.19.1'):  # Kerosene, jet fuel
            if 'jet' in fuel_details.get('description', '').lower() or 'aviation' in fuel_details.get('description', '').lower():
                fuel_type = 'aviation_turbine_fuel'
            else:
                fuel_type = 'kerosene'
        elif hs_code.startswith('2710.19.2'):  # Gas oil (diesel)
            fuel_type = 'diesel'
        elif hs_code.startswith('2710.19.3'):  # Fuel oil
            fuel_type = 'fuel_oil'
        elif hs_code.startswith('2710.19.9'):  # Other petroleum oils
            if 'heating' in fuel_details.get('description', '').lower():
                fuel_type = 'heating_oil'
            else:
                fuel_type = 'diesel'  # Default for other oils
        elif hs_code.startswith('2711.1'):  # LPG
            fuel_type = 'lpg'
        elif hs_code.startswith('2711.2'):  # Propane/Butane
            fuel_type = 'lpg'
        else:
            fuel_type = 'diesel'  # Default fallback
    
    if fuel_type not in EXCISE_RATES:
        fuel_type = 'diesel'  # Default fallback
    
    rate_info = EXCISE_RATES[fuel_type]
    
    # Check for exemptions based on end use
    is_exempt = False
    exemption_reason = None
    
    if end_use in rate_info['exemptions']:
        is_exempt = True
        exemption_reason = f"Exempt for {end_use} use"
    
    # Additional exemption checks
    exemption_details = []
    
    if end_use == 'aviation' and fuel_type in ['petrol', 'diesel']:
        is_exempt = True
        exemption_reason = "Aviation use exempt from excise"
        exemption_details.append("Aviation fuel used in aircraft is generally excise-free")
    
    elif end_use == 'marine_commercial' and fuel_type in ['diesel', 'fuel_oil']:
        is_exempt = True
        exemption_reason = "Commercial marine use exempt"
        exemption_details.append("Fuel used in commercial vessels may qualify for excise exemption")
    
    elif end_use == 'mining_off_road' and fuel_type == 'diesel':
        is_exempt = True
        exemption_reason = "Off-road mining use exempt"
        exemption_details.append("Diesel used in off-road mining operations is excise-free")
    
    elif end_use == 'electricity_generation':
        is_exempt = True
        exemption_reason = "Electricity generation exempt"
        exemption_details.append("Fuel used for electricity generation may be excise-free")
    
    # Calculate excise amount
    if is_exempt:
        excise_amount = 0
        effective_rate = 0
    else:
        excise_amount = volume_litres * rate_info['rate_per_litre']
        effective_rate = (excise_amount / customs_value) * 100 if customs_value > 0 else 0
    
    # Generate detailed breakdown
    breakdown = {
        'volume_litres': volume_litres,
        'rate_per_litre': rate_info['rate_per_litre'],
        'gross_excise': volume_litres * rate_info['rate_per_litre'],
        'exemption_applied': is_exempt,
        'exemption_amount': (volume_litres * rate_info['rate_per_litre']) if is_exempt else 0,
        'net_excise': excise_amount,
        'effective_rate_percent': effective_rate
    }
    
    # Compliance notes and credits information
    compliance_notes = []
    
    if is_exempt:
        compliance_notes.append(f"EXEMPT: {exemption_reason}")
        compliance_notes.append("Exemption requires proper documentation and end-use verification")
        
        if end_use in ['mining_off_road', 'marine_commercial', 'aviation']:
            compliance_notes.append("May be eligible for fuel tax credits if excise was paid")
    
    if not is_exempt and excise_amount > 10000:
        compliance_notes.append("High-value excise requires monthly payment arrangements")
        compliance_notes.append("Consider fuel tax credit eligibility for business use")
    
    if fuel_type in ['biodiesel', 'lpg']:
        compliance_notes.append("Alternative fuels may qualify for reduced rates or incentives")
    
    # Fuel tax credits information
    fuel_tax_credits = []
    
    if end_use in ['mining', 'agriculture', 'forestry', 'fishing', 'manufacturing']:
        fuel_tax_credits.append(f"Eligible for fuel tax credits: {rate_info['rate_per_litre']:.3f} cents/L")
        fuel_tax_credits.append("Business use in these industries qualifies for fuel tax credit scheme")
    
    if end_use == 'heavy_vehicle' and fuel_type == 'diesel':
        fuel_tax_credits.append("Heavy vehicles (>4.5t GVM) eligible for partial fuel tax credits")
    
    # Indexation information
    indexation_info = {
        'schedule': 'Fuel excise rates are indexed twice yearly (February and August)',
        'next_indexation': 'August 1, 2024' if date.today().month < 8 else 'February 1, 2025',
        'mechanism': 'Consumer Price Index (CPI) based indexation'
    }
    
    return {
        'applicable': True,
        'amount': excise_amount,
        'fuel_type': fuel_type,
        'is_exempt': is_exempt,
        'exemption_reason': exemption_reason,
        'breakdown': breakdown,
        'compliance_notes': compliance_notes,
        'exemption_details': exemption_details,
        'fuel_tax_credits': fuel_tax_credits,
        'indexation_info': indexation_info,
        'details': f'Fuel excise: ${excise_amount:,.2f} for {volume_litres:,} litres of {rate_info["description"]} @ {rate_info["rate_per_litre"]:.3f} cents/L' + (f' (EXEMPT: {exemption_reason})' if is_exempt else '')
    }


def calculate_other_levies(hs_code: str, customs_value: float, product_details: dict = None):
    """
    Calculate other applicable levies and charges.
    
    Includes:
    - ACMA charges (telecommunications equipment)
    - Container deposits (beverage containers)
    - Stevedoring charges
    - Quarantine charges
    - Other industry-specific levies
    """
    if not product_details:
        product_details = {}
    
    levies = []
    total_levies = 0
    
    # ACMA Charges (Australian Communications and Media Authority)
    # Telecommunications equipment HS codes
    telecom_hs_codes = [
        '8517',  # Telephone sets, other apparatus for transmission/reception
        '8518',  # Microphones, loudspeakers, headphones
        '8519',  # Sound recording/reproducing apparatus
        '8521',  # Video recording/reproducing apparatus
        '8525',  # Transmission apparatus for radio-broadcasting/television
        '8526',  # Radar apparatus, radio navigational aid apparatus
        '8527',  # Reception apparatus for radio-broadcasting
        '8528'   # Monitors, projectors, television receivers
    ]
    
    if any(hs_code.startswith(code) for code in telecom_hs_codes):
        # ACMA charges based on equipment type and value
        equipment_type = product_details.get('equipment_type', 'general_telecom')
        quantity = product_details.get('quantity', 1)
        
        acma_rates = {
            'mobile_phone': {'per_unit': 0.50, 'min_charge': 25, 'max_charge': 500},
            'radio_transmitter': {'per_unit': 2.00, 'min_charge': 50, 'max_charge': 1000},
            'broadcasting_equipment': {'per_unit': 5.00, 'min_charge': 100, 'max_charge': 2000},
            'satellite_equipment': {'per_unit': 10.00, 'min_charge': 200, 'max_charge': 5000},
            'general_telecom': {'per_unit': 1.00, 'min_charge': 25, 'max_charge': 500}
        }
        
        if equipment_type not in acma_rates:
            equipment_type = 'general_telecom'
        
        rate_info = acma_rates[equipment_type]
        acma_charge = max(
            rate_info['min_charge'],
            min(quantity * rate_info['per_unit'], rate_info['max_charge'])
        )
        
        levies.append({
            'type': 'ACMA Charge',
            'amount': acma_charge,
            'description': f'ACMA regulatory charge for {equipment_type}',
            'calculation': f'{quantity} units × ${rate_info["per_unit"]} (min ${rate_info["min_charge"]}, max ${rate_info["max_charge"]})',
            'authority': 'Australian Communications and Media Authority',
            'mandatory': True
        })
        total_levies += acma_charge
    
    # Container Deposit Schemes (beverage containers)
    beverage_hs_codes = [
        '2201',  # Waters, including natural/artificial mineral waters
        '2202',  # Waters with added sugar/sweetening matter
        '2203',  # Beer made from malt
        '2204',  # Wine of fresh grapes
        '2205',  # Vermouth and other wine of fresh grapes
        '2206',  # Other fermented beverages
        '2207',  # Undenatured ethyl alcohol
        '2208',  # Undenatured ethyl alcohol; spirits, liqueurs
        '2209'   # Vinegar and substitutes for vinegar
    ]
    
    if any(hs_code.startswith(code) for code in beverage_hs_codes):
        container_type = product_details.get('container_type', 'bottle')
        container_size_ml = product_details.get('container_size_ml', 500)
        quantity = product_details.get('quantity', 100)
        
        # Container deposit rates vary by state - using average
        deposit_rates = {
            'bottle_glass': 0.10,      # 10 cents per bottle
            'bottle_plastic': 0.10,    # 10 cents per bottle  
            'can_aluminium': 0.10,     # 10 cents per can
            'can_steel': 0.10,         # 10 cents per can
            'carton_liquid': 0.10,     # 10 cents per carton
            'bottle': 0.10             # Default bottle rate
        }
        
        # Only containers 150ml-3L eligible in most states
        if 150 <= container_size_ml <= 3000:
            deposit_rate = deposit_rates.get(container_type, 0.10)
            container_deposit = quantity * deposit_rate
            
            levies.append({
                'type': 'Container Deposit',
                'amount': container_deposit,
                'description': f'Container deposit scheme - {container_type}',
                'calculation': f'{quantity} containers × ${deposit_rate}',
                'authority': 'State Container Deposit Schemes',
                'mandatory': True,
                'refundable': True,
                'notes': 'Refundable through state recycling schemes'
            })
            total_levies += container_deposit
    
    # Quarantine Charges (AQIS)
    quarantine_hs_codes = [
        '01',  # Live animals
        '02',  # Meat and edible meat offal
        '03',  # Fish and crustaceans
        '04',  # Dairy produce
        '05',  # Products of animal origin
        '06',  # Live trees and other plants
        '07',  # Edible vegetables
        '08',  # Edible fruit and nuts
        '09',  # Coffee, tea, mate and spices
        '10',  # Cereals
        '11',  # Products of the milling industry
        '12',  # Oil seeds and oleaginous fruits
        '13',  # Lac, gums, resins
        '14',  # Vegetable plaiting materials
        '15',  # Animal or vegetable fats and oils
        '16',  # Preparations of meat, fish or crustaceans
        '17',  # Sugars and sugar confectionery
        '18',  # Cocoa and cocoa preparations
        '19',  # Preparations of cereals, flour, starch or milk
        '20',  # Preparations of vegetables, fruit, nuts
        '21',  # Miscellaneous edible preparations
        '22',  # Beverages, spirits and vinegar
        '23',  # Residues and waste from the food industries
        '24'   # Tobacco and manufactured tobacco substitutes
    ]
    
    if any(hs_code.startswith(code) for code in quarantine_hs_codes):
        inspection_type = product_details.get('inspection_type', 'standard')
        risk_category = product_details.get('risk_category', 'medium')
        
        quarantine_rates = {
            'low_risk': {'standard': 150, 'intensive': 300, 'laboratory': 500},
            'medium_risk': {'standard': 250, 'intensive': 500, 'laboratory': 800},
            'high_risk': {'standard': 400, 'intensive': 800, 'laboratory': 1200}
        }
        
        if risk_category not in quarantine_rates:
            risk_category = 'medium_risk'
        if inspection_type not in quarantine_rates[risk_category]:
            inspection_type = 'standard'
        
        quarantine_charge = quarantine_rates[risk_category][inspection_type]
        
        levies.append({
            'type': 'Quarantine Charge',
            'amount': quarantine_charge,
            'description': f'AQIS quarantine inspection - {risk_category} risk, {inspection_type}',
            'calculation': f'{risk_category} risk category, {inspection_type} inspection',
            'authority': 'Australian Quarantine and Inspection Service',
            'mandatory': True
        })
        total_levies += quarantine_charge
    
    # Stevedoring Industry Levy
    # Applied to certain containerized imports
    if customs_value > 5000 and product_details.get('containerized', True):
        stevedoring_levy = min(customs_value * 0.0001, 50)  # 0.01% capped at $50
        
        levies.append({
            'type': 'Stevedoring Levy',
            'amount': stevedoring_levy,
            'description': 'Stevedoring industry levy on containerized imports',
            'calculation': f'${customs_value:,.2f} × 0.01% (max $50)',
            'authority': 'Stevedoring Industry Finance Committee',
            'mandatory': True
        })
        total_levies += stevedoring_levy
    
    # Textile, Clothing and Footwear (TCF) Import Credit Scheme
    tcf_hs_codes = ['50', '51', '52', '53', '54', '55', '56', '57', '58', '59', '60', '61', '62', '63', '64']
    
    if any(hs_code.startswith(code) for code in tcf_hs_codes):
        # TCF scheme provides credits rather than charges, but note for completeness
        levies.append({
            'type': 'TCF Scheme Note',
            'amount': 0,
            'description': 'May be eligible for TCF Import Credit Scheme benefits',
            'calculation': 'Credit scheme - reduces duty liability',
            'authority': 'Department of Industry, Science and Resources',
            'mandatory': False,
            'credit': True,
            'notes': 'Check eligibility for duty reduction credits'
        })
    
    # Wine Industry Levy (for wine imports)
    if hs_code.startswith('2204'):  # Wine of fresh grapes
        volume_litres = product_details.get('volume_litres', 0)
        if volume_litres > 0:
            wine_levy = volume_litres * 0.05  # 5 cents per litre
            
            levies.append({
                'type': 'Wine Industry Levy',
                'amount': wine_levy,
                'description': 'Wine industry development levy',
                'calculation': f'{volume_litres} litres × $0.05',
                'authority': 'Wine Australia',
                'mandatory': True
            })
            total_levies += wine_levy
    
    # Dairy Industry Levy (for dairy imports)
    if hs_code.startswith('04'):  # Dairy produce
        dairy_value = product_details.get('dairy_value', customs_value)
        dairy_levy = dairy_value * 0.001  # 0.1% of value
        
        levies.append({
            'type': 'Dairy Industry Levy',
            'amount': dairy_levy,
            'description': 'Dairy industry service levy',
            'calculation': f'${dairy_value:,.2f} × 0.1%',
            'authority': 'Dairy Australia',
            'mandatory': True
        })
        total_levies += dairy_levy
    
    # Marine Safety Levy (for vessels and marine equipment)
    marine_hs_codes = ['8901', '8902', '8903', '8904', '8905', '8906', '8907', '8908']
    
    if any(hs_code.startswith(code) for code in marine_hs_codes):
        vessel_length = product_details.get('vessel_length_m', 10)
        marine_levy = vessel_length * 50  # $50 per metre
        
        levies.append({
            'type': 'Marine Safety Levy',
            'amount': marine_levy,
            'description': 'Australian Maritime Safety Authority levy',
            'calculation': f'{vessel_length}m × $50/m',
            'authority': 'Australian Maritime Safety Authority',
            'mandatory': True
        })
        total_levies += marine_levy
    
    # Summary information
    summary = {
        'total_levies': total_levies,
        'number_of_levies': len([l for l in levies if l['amount'] > 0]),
        'refundable_amount': sum(l['amount'] for l in levies if l.get('refundable', False)),
        'credit_opportunities': len([l for l in levies if l.get('credit', False)])
    }
    
    return {
        'applicable': len(levies) > 0,
        'total_amount': total_levies,
        'levies': levies,
        'summary': summary,
        'details': f'Total other levies: ${total_levies:,.2f} across {len(levies)} applicable charges'
    }


def calculate_lct(hs_code: str, customs_value: float, vehicle_details: dict = None):
    """Calculate Luxury Car Tax for vehicles over threshold"""
    LCT_THRESHOLD_2024_25 = 71849  # Updated annually
    LCT_RATE = 0.33
    
    # Check if product is a motor vehicle subject to LCT
    vehicle_hs_codes = ['8703', '8704', '8705']  # Passenger cars, commercial vehicles
    
    if not any(hs_code.startswith(code) for code in vehicle_hs_codes):
        return {'applicable': False, 'amount': 0, 'details': 'Not a motor vehicle'}
    
    if customs_value <= LCT_THRESHOLD_2024_25:
        return {
            'applicable': True, 
            'amount': 0, 
            'details': f'Under LCT threshold of ${LCT_THRESHOLD_2024_25:,}'
        }
    
    excess_amount = customs_value - LCT_THRESHOLD_2024_25
    lct_amount = excess_amount * LCT_RATE
    
    return {
        'applicable': True,
        'amount': lct_amount,
        'threshold': LCT_THRESHOLD_2024_25,
        'excess_amount': excess_amount,
        'rate': LCT_RATE,
        'details': f'LCT of ${lct_amount:,.2f} on excess amount of ${excess_amount:,}'
    }


def calculate_wet(hs_code: str, customs_value: float, alcohol_details: dict = None):
    """Calculate Wine Equalisation Tax"""
    WET_RATE = 0.29
    
    # Wine HS codes (Chapter 22)
    wine_hs_codes = ['2204', '2205', '2206']
    
    if not any(hs_code.startswith(code) for code in wine_hs_codes):
        return {'applicable': False, 'amount': 0, 'details': 'Not wine or alcoholic beverage'}
    
    wet_amount = customs_value * WET_RATE
    
    return {
        'applicable': True,
        'amount': wet_amount,
        'rate': WET_RATE,
        'details': f'WET of ${wet_amount:,.2f} at {WET_RATE*100}%'
    }


def generate_enhanced_tax_optimization_tips(hs_code: str, customs_value: float, calculation_result: dict) -> List[str]:
    """
    Generate enhanced tax optimization tips based on calculation results.
    """
    tips = []
    
    # Extract key values from calculation result
    total_duty = calculation_result.get('total_duty', 0)
    gst_amount = calculation_result.get('gst_amount', 0)
    lct_amount = calculation_result.get('lct_amount', 0)
    wet_amount = calculation_result.get('wet_amount', 0)
    tobacco_excise = calculation_result.get('tobacco_excise', {}).get('amount', 0)
    fuel_excise = calculation_result.get('fuel_excise', {}).get('amount', 0)
    other_levies = calculation_result.get('other_levies', {}).get('total_amount', 0)
    
    total_taxes = total_duty + gst_amount + lct_amount + wet_amount + tobacco_excise + fuel_excise + other_levies
    
    # 1. Free Trade Agreement Optimization
    if total_duty > 100:  # Significant duty liability
        tips.append({
            'category': 'Free Trade Agreements',
            'priority': 'High',
            'title': 'Explore FTA Preferential Rates',
            'description': 'Australia has comprehensive FTAs that may reduce or eliminate duties.',
            'action_items': [
                'Check if goods qualify for CPTPP (11 countries) preferential rates',
                'Verify KAFTA (Korea), JAEPA (Japan), or ChAFTA (China) eligibility',
                'Ensure proper Certificate of Origin documentation',
                'Consider supply chain restructuring to qualify for FTA benefits'
            ],
            'potential_savings': f'Up to ${total_duty:,.2f} in duty reduction',
            'complexity': 'Medium',
            'timeframe': '2-4 weeks for documentation'
        })
    
    # 2. Tariff Classification Optimization
    if total_duty > 50:
        tips.append({
            'category': 'Tariff Classification',
            'priority': 'High',
            'title': 'Review HS Code Classification',
            'description': 'Accurate classification can significantly impact duty rates.',
            'action_items': [
                'Obtain binding tariff advice (BTA) for complex classifications',
                'Review product specifications for alternative classifications',
                'Consider product modifications to qualify for lower-duty categories',
                'Engage customs broker for professional classification review'
            ],
            'potential_savings': 'Variable - depends on alternative classifications',
            'complexity': 'High',
            'timeframe': '4-8 weeks for BTA process'
        })
    
    # 3. Temporary Importation and TCO
    if hs_code.startswith(('84', '85', '90')):  # Machinery, electrical, precision instruments
        tips.append({
            'category': 'Duty Exemptions',
            'priority': 'Medium',
            'title': 'Tariff Concession Order (TCO) Opportunities',
            'description': 'TCOs provide duty-free treatment for goods not commercially manufactured in Australia.',
            'action_items': [
                'Search existing TCO database for applicable orders',
                'Apply for new TCO if no local manufacturer exists',
                'Consider temporary importation for short-term use',
                'Evaluate ATA Carnet for trade shows or demonstrations'
            ],
            'potential_savings': f'Up to ${total_duty:,.2f} if TCO approved',
            'complexity': 'Medium',
            'timeframe': '8-12 weeks for TCO application'
        })
    
    # 4. GST and Input Tax Credits
    if gst_amount > 100:
        tips.append({
            'category': 'GST Optimization',
            'priority': 'Medium',
            'title': 'Maximize GST Input Tax Credits',
            'description': 'Registered businesses can claim GST paid on imports as input tax credits.',
            'action_items': [
                'Ensure business is registered for GST if turnover >$75,000',
                'Maintain proper import documentation for BAS claims',
                'Consider deferred GST scheme for cash flow benefits',
                'Review mixed supply rules for complex transactions'
            ],
            'potential_savings': f'${gst_amount:,.2f} recoverable through input tax credits',
            'complexity': 'Low',
            'timeframe': 'Next BAS period'
        })
    
    # 5. Luxury Car Tax Optimization
    if lct_amount > 0:
        tips.append({
            'category': 'Luxury Car Tax',
            'priority': 'High',
            'title': 'LCT Minimization Strategies',
            'description': 'Several strategies can reduce or eliminate LCT liability.',
            'action_items': [
                'Consider fuel-efficient vehicle threshold ($84,916 vs $71,849)',
                'Review vehicle specifications and optional equipment',
                'Evaluate separate importation of accessories',
                'Consider commercial vehicle classification if applicable'
            ],
            'potential_savings': f'Up to ${lct_amount:,.2f} through strategic planning',
            'complexity': 'Medium',
            'timeframe': '2-4 weeks for restructuring'
        })
    
    # 6. Wine Equalisation Tax Strategies
    if wet_amount > 0:
        tips.append({
            'category': 'Wine Equalisation Tax',
            'priority': 'Medium',
            'title': 'WET Optimization for Wine Imports',
            'description': 'WET rebate scheme and exemptions can reduce wine tax burden.',
            'action_items': [
                'Apply for WET producer rebate if eligible (up to $500,000 annually)',
                'Consider cellar door sales exemption for small producers',
                'Review wholesale vs retail pricing strategies',
                'Evaluate blending operations for tax efficiency'
            ],
            'potential_savings': f'Up to ${min(wet_amount, 500000):,.2f} through rebate scheme',
            'complexity': 'Medium',
            'timeframe': '4-6 weeks for rebate application'
        })
    
    # 7. Tobacco and Fuel Excise Strategies
    if tobacco_excise > 0 or fuel_excise > 0:
        excise_tips = {
            'category': 'Excise Optimization',
            'priority': 'High',
            'title': 'Excise Exemptions and Credits',
            'description': 'Various exemptions and credit schemes can reduce excise burden.',
            'action_items': [],
            'potential_savings': '',
            'complexity': 'Medium',
            'timeframe': '2-8 weeks depending on scheme'
        }
        
        if tobacco_excise > 0:
            excise_tips['action_items'].extend([
                'Review tobacco product classification for optimal rates',
                'Consider small manufacturer concessions if applicable',
                'Evaluate duty-free shop opportunities for eligible retailers'
            ])
            excise_tips['potential_savings'] += f'Tobacco: Variable based on classification; '
        
        if fuel_excise > 0:
            excise_tips['action_items'].extend([
                'Apply for fuel tax credits for business use',
                'Consider off-road use exemptions for mining/agriculture',
                'Evaluate aviation fuel exemptions for aircraft operations',
                'Review marine fuel exemptions for commercial vessels'
            ])
            excise_tips['potential_savings'] += f'Fuel: Up to ${fuel_excise:,.2f} through credits/exemptions'
        
        tips.append(excise_tips)
    
    # 8. Warehousing and Logistics Optimization
    if customs_value > 10000:
        tips.append({
            'category': 'Logistics & Warehousing',
            'priority': 'Medium',
            'title': 'Duty Deferral and Warehousing',
            'description': 'Strategic use of customs warehouses can defer duty payments.',
            'action_items': [
                'Consider licensed warehouse storage for duty deferral',
                'Evaluate free trade zone opportunities',
                'Review consolidation options to reduce per-shipment costs',
                'Consider monthly payment arrangements for large importers'
            ],
            'potential_savings': f'Cash flow benefit on ${total_taxes:,.2f} in deferred payments',
            'complexity': 'Medium',
            'timeframe': '4-6 weeks to establish arrangements'
        })
    
    # 9. Anti-Dumping and Countervailing Duty Management
    if 'anti_dumping' in calculation_result and calculation_result['anti_dumping'].get('amount', 0) > 0:
        tips.append({
            'category': 'Anti-Dumping',
            'priority': 'High',
            'title': 'Anti-Dumping Duty Mitigation',
            'description': 'Several strategies can reduce anti-dumping duty exposure.',
            'action_items': [
                'Review country of origin and supplier selection',
                'Consider value-added processing to change classification',
                'Evaluate new shipper review applications',
                'Monitor sunset review processes for duty expiry'
            ],
            'potential_savings': f'Up to ${calculation_result["anti_dumping"]["amount"]:,.2f}',
            'complexity': 'High',
            'timeframe': '6-12 months for formal reviews'
        })
    
    # 10. Compliance and Documentation
    tips.append({
        'category': 'Compliance',
        'priority': 'Critical',
        'title': 'Ensure Compliance Excellence',
        'description': 'Proper compliance prevents penalties and enables optimization.',
        'action_items': [
            'Maintain accurate and complete import documentation',
            'Implement robust record-keeping systems',
            'Consider voluntary disclosure for any past errors',
            'Engage qualified customs broker for complex transactions',
            'Stay updated on regulatory changes and new opportunities'
        ],
        'potential_savings': 'Avoid penalties and enable all optimization strategies',
        'complexity': 'Low to Medium',
        'timeframe': 'Ongoing'
    })
    
    # 11. Technology and Automation
    if customs_value > 50000:  # Large importers
        tips.append({
            'category': 'Technology',
            'priority': 'Medium',
            'title': 'Leverage Technology for Efficiency',
            'description': 'Modern systems can reduce costs and improve compliance.',
            'action_items': [
                'Implement integrated customs management software',
                'Use electronic lodgement for faster processing',
                'Consider blockchain for supply chain transparency',
                'Automate classification and valuation processes'
            ],
            'potential_savings': '5-15% reduction in administrative costs',
            'complexity': 'Medium to High',
            'timeframe': '3-6 months for implementation'
        })
    
    # 12. Supply Chain Optimization
    if total_taxes > 1000:
        tips.append({
            'category': 'Supply Chain',
            'priority': 'Medium',
            'title': 'Strategic Supply Chain Design',
            'description': 'Optimize your supply chain for tax efficiency.',
            'action_items': [
                'Review supplier locations and FTA eligibility',
                'Consider regional distribution hubs',
                'Evaluate make vs buy decisions for components',
                'Assess transfer pricing implications for related parties'
            ],
            'potential_savings': f'10-30% of total tax burden (${total_taxes * 0.1:,.2f} - ${total_taxes * 0.3:,.2f})',
            'complexity': 'High',
            'timeframe': '6-18 months for restructuring'
        })
    
    # Sort tips by priority
    priority_order = {'Critical': 0, 'High': 1, 'Medium': 2, 'Low': 3}
    tips.sort(key=lambda x: priority_order.get(x['priority'], 3))
    
    return tips


def _convert_duty_component(component: DutyComponent) -> DutyComponentResponse:
    """Convert service DutyComponent to response schema."""
    return DutyComponentResponse(
        duty_type=component.duty_type,
        rate=component.rate,
        amount=component.amount,
        description=component.description,
        basis=component.basis,
        calculation_details=component.calculation_details
    )