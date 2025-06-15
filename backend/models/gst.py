"""
GST provisions and exemptions models for the Customs Broker Portal.
"""

from datetime import datetime
from typing import Optional
from decimal import Decimal

from sqlalchemy import (
    String, Integer, DECIMAL, Boolean, DateTime, Text,
    Index, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class GstProvision(Base):
    """
    GstProvision model representing GST provisions and exemptions.
    
    This model stores GST provisions that may apply to specific HS codes,
    including exemptions, special rates, and conditions for GST application.
    
    Attributes:
        id: Primary key
        hs_code: Foreign key to tariff_codes.hs_code (nullable)
        schedule_reference: Reference to GST schedule
        exemption_type: Type of exemption or provision
        description: Description of the provision
        value_threshold: Minimum value threshold for provision to apply
        conditions: Additional conditions for the provision
        is_active: Whether the provision is currently active
        created_at: Timestamp when record was created
    """
    
    __tablename__ = "gst_provisions"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Core fields
    hs_code: Mapped[Optional[str]] = mapped_column(
        String(10), 
        ForeignKey("tariff_codes.hs_code", ondelete="CASCADE"),
        nullable=True,
        index=True
    )
    schedule_reference: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    exemption_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    value_threshold: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(10, 2), 
        nullable=True,
        index=True
    )
    conditions: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status and timestamps
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    tariff_code: Mapped[Optional["TariffCode"]] = relationship(
        "TariffCode",
        back_populates="gst_provisions",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Composite indexes for performance
        Index("ix_gst_provisions_hs_code_active", "hs_code", "is_active"),
        Index("ix_gst_provisions_value_threshold", "value_threshold"),
    )
    
    def __repr__(self) -> str:
        """String representation of GstProvision."""
        return (
            f"<GstProvision(id={self.id}, hs_code='{self.hs_code}', "
            f"exemption_type='{self.exemption_type}', is_active={self.is_active})>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        desc = self.description[:50] + "..." if self.description and len(self.description) > 50 else self.description or "No description"
        return f"GST Provision: {desc}"
    
    def applies_to_value(self, value: Decimal) -> bool:
        """
        Check if provision applies to given value based on value_threshold.
        
        Args:
            value: The value to check against the threshold
            
        Returns:
            bool: True if provision applies to the given value, False otherwise
        """
        if not self.is_active:
            return False
        
        if self.value_threshold is None:
            # No threshold means it applies to all values
            return True
        
        return value >= self.value_threshold
    
    def exemption_details(self) -> str:
        """
        Return formatted exemption details string.
        
        Returns:
            str: Formatted string with exemption details
        """
        details = []
        
        if self.exemption_type:
            details.append(f"Type: {self.exemption_type}")
        
        if self.schedule_reference:
            details.append(f"Schedule: {self.schedule_reference}")
        
        if self.value_threshold:
            details.append(f"Threshold: ${self.value_threshold:,.2f}")
        
        if self.conditions:
            details.append(f"Conditions: {self.conditions}")
        
        return " | ".join(details) if details else "No exemption details available"


# Note: TariffCode import is handled in __init__.py to avoid circular imports
# Forward references are resolved using string-based type annotations