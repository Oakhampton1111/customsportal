"""
Anti-dumping duties models for the Customs Broker Portal.
"""

from datetime import datetime, date
from typing import Optional
from decimal import Decimal

from sqlalchemy import (
    String, Integer, DECIMAL, Boolean, DateTime, Date,
    CheckConstraint, Index, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from models.tariff import TariffCode


class DumpingDuty(Base):
    """
    DumpingDuty model representing anti-dumping and countervailing duties.
    
    This model stores anti-dumping and countervailing duties administered by
    the Anti-Dumping Commission, including duty rates, effective periods,
    and case information.
    
    Attributes:
        id: Primary key
        hs_code: The HS code this duty applies to
        country_code: ISO 3166-1 alpha-3 country code
        exporter_name: Specific exporter if applicable
        duty_type: Type of duty (dumping, countervailing, both)
        duty_rate: Percentage rate for ad valorem duties
        duty_amount: Specific duty amount for per-unit duties
        unit: Unit for specific duties (kg, tonne, etc.)
        effective_date: Date when duty becomes effective
        expiry_date: Date when duty expires (if applicable)
        case_number: Anti-Dumping Commission case number
        investigation_type: Type of investigation
        notice_number: Government Gazette notice number
        is_active: Whether the duty is currently active
        created_at: Timestamp when record was created
    """
    
    __tablename__ = "dumping_duties"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Core fields
    hs_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("tariff_codes.hs_code", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    country_code: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    exporter_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    duty_type: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    duty_rate: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 4), nullable=True)
    duty_amount: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(8, 2), nullable=True)
    unit: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    
    # Date fields
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Case information
    case_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    investigation_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    notice_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Status and timestamps
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    tariff_code: Mapped["TariffCode"] = relationship(
        "TariffCode",
        back_populates="dumping_duties",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Check constraints for data validation
        CheckConstraint(
            "duty_rate >= 0 AND duty_amount >= 0",
            name="ck_dumping_duties_positive_rates"
        ),
        
        # Composite indexes for performance
        Index("ix_dumping_duties_hs_active_effective", "hs_code", "is_active", "effective_date"),
        Index("ix_dumping_duties_country_active", "country_code", "is_active"),
        Index("ix_dumping_duties_expiry", "expiry_date", postgresql_where="expiry_date IS NOT NULL"),
    )
    
    def __repr__(self) -> str:
        """String representation of DumpingDuty."""
        return (
            f"<DumpingDuty(id={self.id}, hs_code='{self.hs_code}', "
            f"country_code='{self.country_code}', duty_type='{self.duty_type}', "
            f"is_active={self.is_active})>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        duty_info = []
        if self.duty_rate:
            duty_info.append(f"{self.duty_rate}%")
        if self.duty_amount and self.unit:
            duty_info.append(f"${self.duty_amount}/{self.unit}")
        
        duty_str = " + ".join(duty_info) if duty_info else "No duty specified"
        return f"{self.hs_code} - {self.country_code}: {duty_str}"
    
    def is_currently_active(self) -> bool:
        """
        Check if duty is currently active based on dates and is_active flag.
        
        Returns:
            bool: True if duty is currently active
        """
        if not self.is_active:
            return False
        
        today = date.today()
        
        # Check if effective date has passed
        if self.effective_date and self.effective_date > today:
            return False
        
        # Check if expiry date has passed
        if self.expiry_date and self.expiry_date <= today:
            return False
        
        return True
    
    def days_until_expiry(self) -> Optional[int]:
        """
        Calculate days until expiry.
        
        Returns:
            int: Days until expiry, or None if no expiry date
        """
        if not self.expiry_date:
            return None
        
        today = date.today()
        delta = self.expiry_date - today
        return delta.days
    
    def effective_duty_calculation(self) -> str:
        """
        Return formatted string of duty calculation.
        
        Returns:
            str: Formatted duty calculation string
        """
        if not self.duty_rate and not self.duty_amount:
            return "No duty specified"
        
        parts = []
        
        if self.duty_rate:
            parts.append(f"{self.duty_rate}% ad valorem")
        
        if self.duty_amount:
            unit_str = f"per {self.unit}" if self.unit else "per unit"
            parts.append(f"${self.duty_amount} {unit_str}")
        
        if len(parts) > 1:
            return f"{parts[0]} + {parts[1]}"
        else:
            return parts[0] if parts else "No duty specified"
    
    @property
    def is_expired(self) -> bool:
        """Check if the duty has expired."""
        if not self.expiry_date:
            return False
        return self.expiry_date <= date.today()
    
    @property
    def is_effective(self) -> bool:
        """Check if the duty is currently effective (within date range)."""
        today = date.today()
        
        # Check if effective date has passed
        if self.effective_date and self.effective_date > today:
            return False
        
        # Check if not yet expired
        if self.expiry_date and self.expiry_date <= today:
            return False
        
        return True