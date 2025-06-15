"""
Duty calculation service for the Customs Broker Portal.

This service handles comprehensive duty calculations including general rates,
FTA rates, anti-dumping duties, TCO exemptions, and GST calculations.
"""

import logging
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload

from models.duty import DutyRate
from models.fta import FtaRate
from models.dumping import DumpingDuty
from models.tco import Tco
from models.gst import GstProvision
from models.hierarchy import TradeAgreement

logger = logging.getLogger(__name__)


@dataclass
class DutyCalculationInput:
    """Input parameters for duty calculation."""
    hs_code: str
    country_code: str
    customs_value: Decimal
    quantity: Optional[Decimal] = None
    calculation_date: Optional[date] = None
    exporter_name: Optional[str] = None
    value_basis: str = "CIF"  # FOB, CIF, etc.


@dataclass
class DutyComponent:
    """Individual duty component calculation."""
    duty_type: str
    rate: Optional[Decimal]
    amount: Decimal
    description: str
    basis: str
    calculation_details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DutyCalculationResult:
    """Comprehensive duty calculation result."""
    hs_code: str
    country_code: str
    customs_value: Decimal
    
    # Duty components
    general_duty: Optional[DutyComponent] = None
    fta_duty: Optional[DutyComponent] = None
    anti_dumping_duty: Optional[DutyComponent] = None
    tco_exemption: Optional[DutyComponent] = None
    
    # GST calculation
    gst_component: Optional[DutyComponent] = None
    
    # Totals
    total_duty: Decimal = Decimal('0.00')
    duty_inclusive_value: Decimal = Decimal('0.00')
    total_gst: Decimal = Decimal('0.00')
    total_amount: Decimal = Decimal('0.00')
    
    # Best rate analysis
    best_rate_type: str = "general"
    potential_savings: Decimal = Decimal('0.00')
    
    # Calculation breakdown
    calculation_steps: List[str] = field(default_factory=list)
    compliance_notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class DutyCalculatorService:
    """
    Service for calculating comprehensive duty amounts including all Australian duty types.
    
    This service handles:
    - General/MFN duty rates
    - FTA preferential rates
    - Anti-dumping and countervailing duties
    - TCO (Tariff Concession Order) exemptions
    - GST calculations on duty-inclusive values
    """
    
    def __init__(self):
        """Initialize the duty calculator service."""
        self.gst_rate = Decimal('0.10')  # 10% standard GST rate
        self.gst_threshold = Decimal('1000.00')  # GST threshold for imports
    
    async def calculate_comprehensive_duty(
        self,
        session: AsyncSession,
        calculation_input: DutyCalculationInput
    ) -> DutyCalculationResult:
        """
        Calculate comprehensive duty including all applicable duties and taxes.
        
        Args:
            session: Database session
            calculation_input: Input parameters for calculation
            
        Returns:
            Comprehensive duty calculation result
        """
        try:
            result = DutyCalculationResult(
                hs_code=calculation_input.hs_code,
                country_code=calculation_input.country_code,
                customs_value=calculation_input.customs_value
            )
            
            calc_date = calculation_input.calculation_date or date.today()
            
            # Step 1: Get general duty rate
            result.calculation_steps.append("Step 1: Calculating general duty rate")
            general_rate = await self.get_general_duty_rate(session, calculation_input.hs_code)
            
            if general_rate:
                result.general_duty = await self._calculate_duty_component(
                    general_rate, calculation_input, "General Duty (MFN)"
                )
                result.calculation_steps.append(
                    f"General duty: {result.general_duty.rate}% = ${result.general_duty.amount}"
                )
            
            # Step 2: Check for best FTA rate
            result.calculation_steps.append("Step 2: Checking FTA preferential rates")
            fta_rate = await self.get_best_fta_rate(
                session, calculation_input.hs_code, calculation_input.country_code, calc_date
            )
            
            if fta_rate:
                result.fta_duty = await self._calculate_fta_component(
                    fta_rate, calculation_input
                )
                result.calculation_steps.append(
                    f"FTA duty ({fta_rate.fta_code}): {result.fta_duty.rate}% = ${result.fta_duty.amount}"
                )
            
            # Step 3: Check TCO exemptions
            result.calculation_steps.append("Step 3: Checking TCO exemptions")
            tco_exemption = await self.check_tco_exemption(
                session, calculation_input.hs_code, calc_date
            )
            
            if tco_exemption:
                result.tco_exemption = DutyComponent(
                    duty_type="TCO Exemption",
                    rate=Decimal('0.00'),
                    amount=Decimal('0.00'),
                    description=f"TCO {tco_exemption.tco_number}: {tco_exemption.description[:100]}...",
                    basis="Exemption",
                    calculation_details={"tco_number": tco_exemption.tco_number}
                )
                result.calculation_steps.append(f"TCO exemption applies: {tco_exemption.tco_number}")
            
            # Step 4: Calculate anti-dumping duties
            result.calculation_steps.append("Step 4: Checking anti-dumping duties")
            dumping_duty = await self.calculate_anti_dumping_duty(
                session, calculation_input.hs_code, calculation_input.country_code,
                calculation_input.exporter_name, calc_date
            )
            
            if dumping_duty:
                result.anti_dumping_duty = await self._calculate_dumping_component(
                    dumping_duty, calculation_input
                )
                result.calculation_steps.append(
                    f"Anti-dumping duty: {result.anti_dumping_duty.description} = ${result.anti_dumping_duty.amount}"
                )
            
            # Step 5: Determine best applicable duty
            result.calculation_steps.append("Step 5: Determining best applicable duty rate")
            best_duty = await self._determine_best_duty(result)
            
            # Step 6: Calculate total duty
            result.total_duty = best_duty.amount if best_duty else Decimal('0.00')
            
            # Add anti-dumping duty if applicable
            if result.anti_dumping_duty:
                result.total_duty += result.anti_dumping_duty.amount
            
            result.duty_inclusive_value = calculation_input.customs_value + result.total_duty
            result.calculation_steps.append(
                f"Total duty: ${result.total_duty}, Duty-inclusive value: ${result.duty_inclusive_value}"
            )
            
            # Step 7: Calculate GST
            result.calculation_steps.append("Step 6: Calculating GST")
            result.gst_component = await self.calculate_gst(
                session, calculation_input.hs_code, result.duty_inclusive_value
            )
            
            if result.gst_component:
                result.total_gst = result.gst_component.amount
                result.calculation_steps.append(f"GST: {result.gst_component.rate}% = ${result.total_gst}")
            
            # Step 8: Calculate totals and savings analysis
            result.total_amount = result.duty_inclusive_value + result.total_gst
            await self._calculate_savings_analysis(result)
            
            result.calculation_steps.append(f"Total amount payable: ${result.total_amount}")
            
            # Add compliance notes
            await self._add_compliance_notes(result, fta_rate, tco_exemption)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in comprehensive duty calculation: {str(e)}")
            raise
    
    async def get_general_duty_rate(
        self,
        session: AsyncSession,
        hs_code: str
    ) -> Optional[DutyRate]:
        """
        Get the general/MFN duty rate for an HS code.
        
        Args:
            session: Database session
            hs_code: HS code to lookup
            
        Returns:
            DutyRate object or None if not found
        """
        try:
            # Try exact match first
            stmt = select(DutyRate).where(DutyRate.hs_code == hs_code)
            result = await session.execute(stmt)
            duty_rate = result.scalar_one_or_none()
            
            if duty_rate:
                return duty_rate
            
            # Try hierarchical lookup (8-digit, 6-digit, 4-digit, 2-digit)
            for length in [8, 6, 4, 2]:
                if len(hs_code) > length:
                    truncated_code = hs_code[:length]
                    stmt = select(DutyRate).where(DutyRate.hs_code == truncated_code)
                    result = await session.execute(stmt)
                    duty_rate = result.scalar_one_or_none()
                    
                    if duty_rate:
                        return duty_rate
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting general duty rate for {hs_code}: {str(e)}")
            return None
    
    async def get_best_fta_rate(
        self,
        session: AsyncSession,
        hs_code: str,
        country_code: str,
        calculation_date: date
    ) -> Optional[FtaRate]:
        """
        Find the best FTA rate for a specific HS code and country.
        
        Args:
            session: Database session
            hs_code: HS code to lookup
            country_code: Country code
            calculation_date: Date for rate validity
            
        Returns:
            Best FtaRate object or None if not found
        """
        try:
            stmt = (
                select(FtaRate)
                .options(selectinload(FtaRate.trade_agreement))
                .where(
                    and_(
                        FtaRate.hs_code == hs_code,
                        FtaRate.country_code == country_code,
                        or_(
                            FtaRate.effective_date.is_(None),
                            FtaRate.effective_date <= calculation_date
                        ),
                        or_(
                            FtaRate.elimination_date.is_(None),
                            FtaRate.elimination_date > calculation_date
                        )
                    )
                )
                .order_by(FtaRate.preferential_rate.asc())
            )
            
            result = await session.execute(stmt)
            fta_rates = result.scalars().all()
            
            if not fta_rates:
                # Try hierarchical lookup
                for length in [8, 6, 4, 2]:
                    if len(hs_code) > length:
                        truncated_code = hs_code[:length]
                        stmt = (
                            select(FtaRate)
                            .options(selectinload(FtaRate.trade_agreement))
                            .where(
                                and_(
                                    FtaRate.hs_code == truncated_code,
                                    FtaRate.country_code == country_code,
                                    or_(
                                        FtaRate.effective_date.is_(None),
                                        FtaRate.effective_date <= calculation_date
                                    ),
                                    or_(
                                        FtaRate.elimination_date.is_(None),
                                        FtaRate.elimination_date > calculation_date
                                    )
                                )
                            )
                            .order_by(FtaRate.preferential_rate.asc())
                        )
                        
                        result = await session.execute(stmt)
                        fta_rates = result.scalars().all()
                        
                        if fta_rates:
                            break
            
            # Return the best (lowest) rate
            return fta_rates[0] if fta_rates else None
            
        except Exception as e:
            logger.error(f"Error getting FTA rate for {hs_code}, {country_code}: {str(e)}")
            return None
    
    async def check_tco_exemption(
        self,
        session: AsyncSession,
        hs_code: str,
        calculation_date: date
    ) -> Optional[Tco]:
        """
        Check for TCO exemptions applicable to an HS code.
        
        Args:
            session: Database session
            hs_code: HS code to check
            calculation_date: Date for TCO validity
            
        Returns:
            Applicable Tco object or None if not found
        """
        try:
            stmt = (
                select(Tco)
                .where(
                    and_(
                        Tco.hs_code == hs_code,
                        Tco.is_current == True,
                        or_(
                            Tco.effective_date.is_(None),
                            Tco.effective_date <= calculation_date
                        ),
                        or_(
                            Tco.expiry_date.is_(None),
                            Tco.expiry_date > calculation_date
                        )
                    )
                )
                .order_by(Tco.effective_date.desc())
            )
            
            result = await session.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error checking TCO exemption for {hs_code}: {str(e)}")
            return None
    
    async def calculate_anti_dumping_duty(
        self,
        session: AsyncSession,
        hs_code: str,
        country_code: str,
        exporter_name: Optional[str],
        calculation_date: date
    ) -> Optional[DumpingDuty]:
        """
        Calculate anti-dumping duties for specific country and exporter.
        
        Args:
            session: Database session
            hs_code: HS code
            country_code: Country of origin
            exporter_name: Specific exporter (optional)
            calculation_date: Date for duty validity
            
        Returns:
            Applicable DumpingDuty object or None if not found
        """
        try:
            # Build query conditions
            conditions = [
                DumpingDuty.hs_code == hs_code,
                DumpingDuty.country_code == country_code,
                DumpingDuty.is_active == True,
                or_(
                    DumpingDuty.effective_date.is_(None),
                    DumpingDuty.effective_date <= calculation_date
                ),
                or_(
                    DumpingDuty.expiry_date.is_(None),
                    DumpingDuty.expiry_date > calculation_date
                )
            ]
            
            # If exporter specified, try to find exporter-specific duty first
            if exporter_name:
                exporter_stmt = (
                    select(DumpingDuty)
                    .where(
                        and_(
                            *conditions,
                            DumpingDuty.exporter_name.ilike(f"%{exporter_name}%")
                        )
                    )
                    .order_by(DumpingDuty.effective_date.desc())
                )
                
                result = await session.execute(exporter_stmt)
                exporter_duty = result.scalar_one_or_none()
                
                if exporter_duty:
                    return exporter_duty
            
            # Fall back to general country duty
            general_stmt = (
                select(DumpingDuty)
                .where(
                    and_(
                        *conditions,
                        DumpingDuty.exporter_name.is_(None)
                    )
                )
                .order_by(DumpingDuty.effective_date.desc())
            )
            
            result = await session.execute(general_stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"Error calculating anti-dumping duty: {str(e)}")
            return None
    
    async def calculate_gst(
        self,
        session: AsyncSession,
        hs_code: str,
        duty_inclusive_value: Decimal
    ) -> Optional[DutyComponent]:
        """
        Calculate GST on duty-inclusive value.
        
        Args:
            session: Database session
            hs_code: HS code for GST exemption checking
            duty_inclusive_value: Value including duties
            
        Returns:
            GST DutyComponent or None if exempt/below threshold
        """
        try:
            # Check for GST exemptions
            stmt = (
                select(GstProvision)
                .where(
                    and_(
                        or_(
                            GstProvision.hs_code == hs_code,
                            GstProvision.hs_code.is_(None)  # General provisions
                        ),
                        GstProvision.is_active == True
                    )
                )
            )
            
            result = await session.execute(stmt)
            gst_provisions = result.scalars().all()
            
            # Check if any exemption applies
            for provision in gst_provisions:
                if provision.exemption_type and provision.applies_to_value(duty_inclusive_value):
                    return DutyComponent(
                        duty_type="GST",
                        rate=Decimal('0.00'),
                        amount=Decimal('0.00'),
                        description=f"GST Exempt: {provision.exemption_type}",
                        basis="Exemption",
                        calculation_details={
                            "exemption_type": provision.exemption_type,
                            "schedule_reference": provision.schedule_reference
                        }
                    )
            
            # Check GST threshold
            if duty_inclusive_value < self.gst_threshold:
                return DutyComponent(
                    duty_type="GST",
                    rate=Decimal('0.00'),
                    amount=Decimal('0.00'),
                    description=f"GST not applicable (below ${self.gst_threshold} threshold)",
                    basis="Threshold",
                    calculation_details={"threshold": str(self.gst_threshold)}
                )
            
            # Calculate standard GST
            gst_amount = (duty_inclusive_value * self.gst_rate).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            
            return DutyComponent(
                duty_type="GST",
                rate=self.gst_rate * 100,  # Convert to percentage
                amount=gst_amount,
                description="Goods and Services Tax (10%)",
                basis="Standard Rate",
                calculation_details={
                    "duty_inclusive_value": str(duty_inclusive_value),
                    "gst_rate": str(self.gst_rate)
                }
            )
            
        except Exception as e:
            logger.error(f"Error calculating GST: {str(e)}")
            return None
    
    async def get_calculation_breakdown(
        self,
        session: AsyncSession,
        calculation_input: DutyCalculationInput
    ) -> Dict[str, Any]:
        """
        Get detailed calculation breakdown with all steps and alternatives.
        
        Args:
            session: Database session
            calculation_input: Input parameters
            
        Returns:
            Detailed breakdown dictionary
        """
        try:
            result = await self.calculate_comprehensive_duty(session, calculation_input)
            
            breakdown = {
                "input_parameters": {
                    "hs_code": calculation_input.hs_code,
                    "country_code": calculation_input.country_code,
                    "customs_value": str(calculation_input.customs_value),
                    "quantity": str(calculation_input.quantity) if calculation_input.quantity else None,
                    "calculation_date": calculation_input.calculation_date.isoformat() if calculation_input.calculation_date else None,
                    "value_basis": calculation_input.value_basis
                },
                "duty_components": {},
                "totals": {
                    "total_duty": str(result.total_duty),
                    "duty_inclusive_value": str(result.duty_inclusive_value),
                    "total_gst": str(result.total_gst),
                    "total_amount": str(result.total_amount)
                },
                "best_rate_analysis": {
                    "best_rate_type": result.best_rate_type,
                    "potential_savings": str(result.potential_savings)
                },
                "calculation_steps": result.calculation_steps,
                "compliance_notes": result.compliance_notes,
                "warnings": result.warnings
            }
            
            # Add duty components
            if result.general_duty:
                breakdown["duty_components"]["general_duty"] = self._component_to_dict(result.general_duty)
            
            if result.fta_duty:
                breakdown["duty_components"]["fta_duty"] = self._component_to_dict(result.fta_duty)
            
            if result.anti_dumping_duty:
                breakdown["duty_components"]["anti_dumping_duty"] = self._component_to_dict(result.anti_dumping_duty)
            
            if result.tco_exemption:
                breakdown["duty_components"]["tco_exemption"] = self._component_to_dict(result.tco_exemption)
            
            if result.gst_component:
                breakdown["duty_components"]["gst"] = self._component_to_dict(result.gst_component)
            
            return breakdown
            
        except Exception as e:
            logger.error(f"Error getting calculation breakdown: {str(e)}")
            raise
    
    # Private helper methods
    
    async def _calculate_duty_component(
        self,
        duty_rate: DutyRate,
        calculation_input: DutyCalculationInput,
        description: str
    ) -> DutyComponent:
        """Calculate duty component from DutyRate."""
        if duty_rate.is_ad_valorem and duty_rate.general_rate:
            amount = (calculation_input.customs_value * duty_rate.general_rate / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            return DutyComponent(
                duty_type="General Duty",
                rate=duty_rate.general_rate,
                amount=amount,
                description=description,
                basis="Ad Valorem",
                calculation_details={
                    "unit_type": duty_rate.unit_type,
                    "rate_text": duty_rate.rate_text
                }
            )
        elif duty_rate.is_specific and duty_rate.general_rate and calculation_input.quantity:
            amount = (calculation_input.quantity * duty_rate.general_rate).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            return DutyComponent(
                duty_type="General Duty",
                rate=duty_rate.general_rate,
                amount=amount,
                description=f"{description} (Specific)",
                basis="Specific",
                calculation_details={
                    "unit_type": duty_rate.unit_type,
                    "quantity": str(calculation_input.quantity)
                }
            )
        else:
            return DutyComponent(
                duty_type="General Duty",
                rate=Decimal('0.00'),
                amount=Decimal('0.00'),
                description="Free",
                basis="Free",
                calculation_details={"rate_text": duty_rate.rate_text or "Free"}
            )
    
    async def _calculate_fta_component(
        self,
        fta_rate: FtaRate,
        calculation_input: DutyCalculationInput
    ) -> DutyComponent:
        """Calculate FTA duty component."""
        effective_rate = fta_rate.effective_rate or Decimal('0.00')
        amount = (calculation_input.customs_value * effective_rate / 100).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
        
        return DutyComponent(
            duty_type="FTA Duty",
            rate=effective_rate,
            amount=amount,
            description=f"FTA Preferential Rate ({fta_rate.fta_code})",
            basis="FTA Preferential",
            calculation_details={
                "fta_code": fta_rate.fta_code,
                "staging_category": fta_rate.staging_category,
                "rule_of_origin": fta_rate.rule_of_origin
            }
        )
    
    async def _calculate_dumping_component(
        self,
        dumping_duty: DumpingDuty,
        calculation_input: DutyCalculationInput
    ) -> DutyComponent:
        """Calculate anti-dumping duty component."""
        total_amount = Decimal('0.00')
        description_parts = []
        
        # Ad valorem component
        if dumping_duty.duty_rate:
            ad_valorem_amount = (calculation_input.customs_value * dumping_duty.duty_rate / 100).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            total_amount += ad_valorem_amount
            description_parts.append(f"{dumping_duty.duty_rate}% ad valorem")
        
        # Specific component
        if dumping_duty.duty_amount and calculation_input.quantity:
            specific_amount = (calculation_input.quantity * dumping_duty.duty_amount).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
            total_amount += specific_amount
            unit_str = f"per {dumping_duty.unit}" if dumping_duty.unit else "per unit"
            description_parts.append(f"${dumping_duty.duty_amount} {unit_str}")
        
        description = f"Anti-dumping duty: {' + '.join(description_parts)}" if description_parts else "Anti-dumping duty"
        
        return DutyComponent(
            duty_type="Anti-dumping Duty",
            rate=dumping_duty.duty_rate,
            amount=total_amount,
            description=description,
            basis="Anti-dumping",
            calculation_details={
                "case_number": dumping_duty.case_number,
                "exporter_name": dumping_duty.exporter_name,
                "duty_type": dumping_duty.duty_type
            }
        )
    
    async def _determine_best_duty(self, result: DutyCalculationResult) -> Optional[DutyComponent]:
        """Determine the best applicable duty rate."""
        # TCO exemption takes precedence
        if result.tco_exemption:
            result.best_rate_type = "tco_exemption"
            return result.tco_exemption
        
        # Compare FTA vs General duty
        if result.fta_duty and result.general_duty:
            if result.fta_duty.amount < result.general_duty.amount:
                result.best_rate_type = "fta"
                return result.fta_duty
            else:
                result.best_rate_type = "general"
                return result.general_duty
        elif result.fta_duty:
            result.best_rate_type = "fta"
            return result.fta_duty
        elif result.general_duty:
            result.best_rate_type = "general"
            return result.general_duty
        
        return None
    
    async def _calculate_savings_analysis(self, result: DutyCalculationResult):
        """Calculate potential savings analysis."""
        if result.best_rate_type == "fta" and result.general_duty:
            result.potential_savings = result.general_duty.amount - (result.fta_duty.amount if result.fta_duty else Decimal('0.00'))
        elif result.best_rate_type == "tco_exemption" and result.general_duty:
            result.potential_savings = result.general_duty.amount
    
    async def _add_compliance_notes(
        self,
        result: DutyCalculationResult,
        fta_rate: Optional[FtaRate],
        tco_exemption: Optional[Tco]
    ):
        """Add compliance notes and warnings."""
        if fta_rate:
            if fta_rate.rule_of_origin:
                result.compliance_notes.append(
                    f"FTA rate requires compliance with rules of origin: {fta_rate.get_origin_requirements_summary()}"
                )
            
            if fta_rate.is_quota_applicable:
                result.warnings.append(
                    f"FTA rate subject to quota restrictions: {fta_rate.quota_quantity} {fta_rate.quota_unit}"
                )
        
        if tco_exemption:
            result.compliance_notes.append(
                f"TCO exemption applies - ensure goods match TCO description: {tco_exemption.description}"
            )
            
            if tco_exemption.days_until_expiry() and tco_exemption.days_until_expiry() < 90:
                result.warnings.append(
                    f"TCO expires in {tco_exemption.days_until_expiry()} days"
                )
    
    def _component_to_dict(self, component: DutyComponent) -> Dict[str, Any]:
        """Convert DutyComponent to dictionary."""
        return {
            "duty_type": component.duty_type,
            "rate": str(component.rate) if component.rate else None,
            "amount": str(component.amount),
            "description": component.description,
            "basis": component.basis,
            "calculation_details": component.calculation_details
        }