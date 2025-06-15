"""
Tariff Concession Orders (TCO) models for the Customs Broker Portal.
"""

from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import (
    String, Integer, Boolean, DateTime, Date, Text,
    Index, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Tco(Base):
    """
    Tco model representing Tariff Concession Orders.
    
    This model stores Tariff Concession Orders (TCOs) which provide duty concessions
    for specific goods under certain conditions. TCOs are linked to HS codes and
    have validity periods and specific applicant information.
    
    Attributes:
        id: Primary key
        tco_number: Unique TCO number identifier
        hs_code: Foreign key to tariff_codes.hs_code
        description: Description of the goods covered by the TCO
        applicant_name: Name of the applicant for the TCO
        effective_date: Date when the TCO becomes effective
        expiry_date: Date when the TCO expires
        gazette_date: Date when the TCO was published in the gazette
        gazette_number: Gazette number where the TCO was published
        substitutable_goods_determination: Details about substitutable goods
        is_current: Whether the TCO is currently active
        created_at: Timestamp when record was created
    """
    
    __tablename__ = "tcos"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Core fields
    tco_number: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    hs_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("tariff_codes.hs_code", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    applicant_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    
    # Date fields
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gazette_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    gazette_number: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Additional fields
    substitutable_goods_determination: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    tariff_code: Mapped["TariffCode"] = relationship(
        "TariffCode",
        back_populates="tcos",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Composite indexes for performance
        Index("ix_tcos_hs_code_current", "hs_code", "is_current"),
        Index("ix_tcos_effective_expiry", "effective_date", "expiry_date"),
        Index("ix_tcos_tco_number", "tco_number"),
    )
    
    def __repr__(self) -> str:
        """String representation of Tco."""
        return (
            f"<Tco(id={self.id}, tco_number='{self.tco_number}', "
            f"hs_code='{self.hs_code}', is_current={self.is_current})>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"TCO {self.tco_number}: {self.description[:50]}..."
    
    def is_currently_valid(self) -> bool:
        """
        Check if TCO is currently valid based on dates and is_current flag.
        
        Returns:
            bool: True if TCO is currently valid, False otherwise
        """
        if not self.is_current:
            return False
        
        today = date.today()
        
        # Check if effective date has passed (if set)
        if self.effective_date and today < self.effective_date:
            return False
        
        # Check if expiry date has not passed (if set)
        if self.expiry_date and today > self.expiry_date:
            return False
        
        return True
    
    def days_until_expiry(self) -> Optional[int]:
        """
        Calculate days until expiry.
        
        Returns:
            int: Number of days until expiry, None if no expiry date set
        """
        if not self.expiry_date:
            return None
        
        today = date.today()
        delta = self.expiry_date - today
        return delta.days
    
    def gazette_reference(self) -> str:
        """
        Return formatted gazette reference string.
        
        Returns:
            str: Formatted gazette reference or empty string if no gazette info
        """
        if self.gazette_number and self.gazette_date:
            return f"Gazette {self.gazette_number} ({self.gazette_date.strftime('%d/%m/%Y')})"
        elif self.gazette_number:
            return f"Gazette {self.gazette_number}"
        elif self.gazette_date:
            return f"Gazette dated {self.gazette_date.strftime('%d/%m/%Y')}"
        else:
            return ""


# Note: TariffCode import is handled in __init__.py to avoid circular imports
# Forward references are resolved using string-based type annotations