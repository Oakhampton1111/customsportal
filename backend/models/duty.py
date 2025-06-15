"""
Duty rate models for the Customs Broker Portal.

This module contains the DutyRate model which represents general duty rates
and MFN (Most Favoured Nation) rates for Australian tariff codes.
"""

from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import (
    String, Integer, DECIMAL, DateTime, CheckConstraint, Index,
    ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from models.tariff import TariffCode


class DutyRate(Base):
    """
    DutyRate model representing general duty rates and MFN rates.
    
    This model stores general duty rates and Most Favoured Nation (MFN) rates
    for Australian tariff codes as specified in Schedule 3.
    
    Attributes:
        id: Primary key
        hs_code: Foreign key to tariff_codes.hs_code
        general_rate: MFN (Most Favoured Nation) rate as decimal percentage
        unit_type: Type of duty (ad_valorem, specific, compound)
        rate_text: Full rate text for complex rate structures
        statistical_code: Statistical code for reporting
        created_at: Timestamp when record was created
        
    Relationships:
        tariff_code: Many-to-one relationship with TariffCode
    """
    
    __tablename__ = "duty_rates"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key to tariff codes
    hs_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("tariff_codes.hs_code", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    # Core duty rate fields
    general_rate: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(5, 2), 
        nullable=True
    )
    unit_type: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True
    )
    rate_text: Mapped[Optional[str]] = mapped_column(
        String(200), 
        nullable=True
    )
    statistical_code: Mapped[Optional[str]] = mapped_column(
        String(15), 
        nullable=True
    )
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    tariff_code: Mapped["TariffCode"] = relationship(
        "TariffCode",
        back_populates="duty_rates",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Rate validation constraint
        CheckConstraint(
            "general_rate >= 0",
            name="chk_duty_rate_positive"
        ),
        
        # Performance indexes
        Index("idx_duty_rates_hs_code", "hs_code"),
    )
    
    def __repr__(self) -> str:
        """String representation of DutyRate."""
        return (
            f"<DutyRate(id={self.id}, hs_code='{self.hs_code}', "
            f"general_rate={self.general_rate}, unit_type='{self.unit_type}')>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        if self.rate_text:
            return f"{self.hs_code}: {self.rate_text}"
        elif self.general_rate is not None:
            return f"{self.hs_code}: {self.general_rate}%"
        else:
            return f"{self.hs_code}: No rate specified"
    
    @property
    def is_ad_valorem(self) -> bool:
        """Check if this is an ad valorem duty (percentage-based)."""
        return self.unit_type == "ad_valorem" if self.unit_type else False
    
    @property
    def is_specific(self) -> bool:
        """Check if this is a specific duty (per-unit based)."""
        return self.unit_type == "specific" if self.unit_type else False
    
    @property
    def is_compound(self) -> bool:
        """Check if this is a compound duty (combination of ad valorem and specific)."""
        return self.unit_type == "compound" if self.unit_type else False
    
    @property
    def effective_rate_text(self) -> str:
        """Get the effective rate text for display purposes."""
        if self.rate_text:
            return self.rate_text
        elif self.general_rate is not None:
            return f"{self.general_rate}%"
        else:
            return "Free"
    
    def calculate_duty_amount(self, value: Decimal, quantity: Optional[Decimal] = None) -> Optional[Decimal]:
        """
        Calculate duty amount based on value and quantity.
        
        Args:
            value: Customs value in AUD
            quantity: Quantity for specific duties
            
        Returns:
            Calculated duty amount or None if cannot calculate
        """
        if not self.general_rate:
            return Decimal('0.00')
        
        if self.is_ad_valorem:
            return value * (self.general_rate / 100)
        elif self.is_specific and quantity:
            # For specific duties, general_rate would represent per-unit amount
            return quantity * self.general_rate
        
        # For compound duties or complex rates, return None as calculation
        # would require parsing the rate_text
        return None