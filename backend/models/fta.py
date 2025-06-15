"""
FTA rate models for the Customs Broker Portal.

This module contains the FtaRate model which represents preferential tariff rates
under Australian Free Trade Agreements.
"""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import (
    String, Integer, DECIMAL, Boolean, Date, DateTime, Text, CheckConstraint, Index,
    ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base
from models.tariff import TariffCode
from models.hierarchy import TradeAgreement


class FtaRate(Base):
    """
    FtaRate model representing preferential tariff rates under Free Trade Agreements.
    
    This model stores preferential tariff rates available under Australian Free Trade
    Agreements, including staging categories, rules of origin, and quota information.
    
    Attributes:
        id: Primary key
        hs_code: Foreign key to tariff_codes.hs_code
        fta_code: Foreign key to trade_agreements.fta_code
        country_code: ISO 3166-1 alpha-3 country code
        preferential_rate: Preferential duty rate as decimal percentage
        rate_type: Type of preferential rate
        staging_category: FTA staging category for tariff elimination
        effective_date: Date when the preferential rate becomes effective
        elimination_date: Date when tariff reaches zero under FTA
        quota_quantity: Quota quantity if applicable
        quota_unit: Unit for quota quantity
        safeguard_applicable: Whether safeguard measures apply
        rule_of_origin: FTA-specific rules of origin requirements
        created_at: Timestamp when record was created
        
    Relationships:
        tariff_code: Many-to-one relationship with TariffCode
        trade_agreement: Many-to-one relationship with TradeAgreement
    """
    
    __tablename__ = "fta_rates"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    hs_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("tariff_codes.hs_code", ondelete="CASCADE"),
        nullable=False
    )
    fta_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("trade_agreements.fta_code", ondelete="CASCADE"),
        nullable=False
    )
    
    # Core identification fields
    country_code: Mapped[str] = mapped_column(
        String(3), 
        nullable=False
    )
    
    # Rate and type information
    preferential_rate: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(5, 2), 
        nullable=True
    )
    rate_type: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True
    )
    staging_category: Mapped[Optional[str]] = mapped_column(
        String(10), 
        nullable=True
    )
    
    # Date fields
    effective_date: Mapped[Optional[date]] = mapped_column(
        Date, 
        nullable=True
    )
    elimination_date: Mapped[Optional[date]] = mapped_column(
        Date, 
        nullable=True
    )
    
    # Quota information
    quota_quantity: Mapped[Optional[Decimal]] = mapped_column(
        DECIMAL(15, 2), 
        nullable=True
    )
    quota_unit: Mapped[Optional[str]] = mapped_column(
        String(20), 
        nullable=True
    )
    
    # Additional provisions
    safeguard_applicable: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False
    )
    rule_of_origin: Mapped[Optional[str]] = mapped_column(
        Text, 
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
        back_populates="fta_rates",
        lazy="select"
    )
    
    trade_agreement: Mapped["TradeAgreement"] = relationship(
        "TradeAgreement",
        back_populates="fta_rates",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Rate validation constraint
        CheckConstraint(
            "preferential_rate >= 0",
            name="chk_fta_rate_positive"
        ),
        
        # Performance indexes
        Index("idx_fta_rates_lookup", "hs_code", "fta_code", "country_code"),
        Index("idx_fta_rates_country", "country_code", "effective_date"),
        Index("idx_fta_rates_effective", "effective_date", "elimination_date"),
    )
    
    def __repr__(self) -> str:
        """String representation of FtaRate."""
        return (
            f"<FtaRate(id={self.id}, hs_code='{self.hs_code}', "
            f"fta_code='{self.fta_code}', country_code='{self.country_code}', "
            f"preferential_rate={self.preferential_rate})>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        rate_text = f"{self.preferential_rate}%" if self.preferential_rate is not None else "Free"
        return f"{self.hs_code} ({self.fta_code}-{self.country_code}): {rate_text}"
    
    @property
    def is_currently_effective(self) -> bool:
        """Check if the FTA rate is currently effective."""
        today = date.today()
        
        # Check if effective date has passed (or is None)
        if self.effective_date and self.effective_date > today:
            return False
            
        # Check if elimination date has not passed (or is None)
        if self.elimination_date and self.elimination_date <= today:
            return False
            
        return True
    
    @property
    def is_eliminated(self) -> bool:
        """Check if the tariff has been eliminated (reached zero)."""
        if self.elimination_date:
            return self.elimination_date <= date.today()
        return False
    
    @property
    def is_quota_applicable(self) -> bool:
        """Check if quota restrictions apply to this rate."""
        return self.quota_quantity is not None and self.quota_quantity > 0
    
    @property
    def effective_rate(self) -> Optional[Decimal]:
        """Get the effective preferential rate, considering elimination."""
        if self.is_eliminated:
            return Decimal('0.00')
        return self.preferential_rate
    
    @property
    def staging_description(self) -> str:
        """Get a human-readable description of the staging category."""
        staging_descriptions = {
            'Base': 'Base rate - no reduction',
            'A': 'Immediate elimination',
            'B': 'Staged elimination over multiple years',
            'C': 'Staged elimination over extended period',
            'D': 'Special staging arrangement',
            'E': 'Excluded from tariff elimination',
        }
        
        if self.staging_category:
            return staging_descriptions.get(
                self.staging_category, 
                f"Category {self.staging_category}"
            )
        return "No staging category specified"
    
    def calculate_preferential_duty(self, value: Decimal) -> Optional[Decimal]:
        """
        Calculate preferential duty amount based on customs value.
        
        Args:
            value: Customs value in AUD
            
        Returns:
            Calculated preferential duty amount or None if rate not available
        """
        effective_rate = self.effective_rate
        if effective_rate is None:
            return None
            
        return value * (effective_rate / 100)
    
    def get_origin_requirements_summary(self) -> str:
        """
        Get a summary of rules of origin requirements.
        
        Returns:
            Summary text of origin requirements
        """
        if not self.rule_of_origin:
            return "No specific origin requirements specified"
        
        # Truncate long rules of origin for summary
        if len(self.rule_of_origin) > 200:
            return self.rule_of_origin[:197] + "..."
        
        return self.rule_of_origin
    
    def is_rate_better_than(self, general_rate: Optional[Decimal]) -> bool:
        """
        Check if this FTA rate is better than the general duty rate.
        
        Args:
            general_rate: General duty rate to compare against
            
        Returns:
            True if FTA rate is lower than general rate
        """
        if not self.is_currently_effective:
            return False
            
        effective_rate = self.effective_rate
        if effective_rate is None or general_rate is None:
            return False
            
        return effective_rate < general_rate
    
    @classmethod
    def get_best_rate_for_country(
        cls, 
        session, 
        hs_code: str, 
        country_code: str
    ) -> Optional["FtaRate"]:
        """
        Get the best available FTA rate for a specific HS code and country.
        
        Args:
            session: SQLAlchemy session
            hs_code: HS code to search for
            country_code: Country code to search for
            
        Returns:
            FtaRate with the lowest preferential rate, or None if not found
        """
        from sqlalchemy import and_
        
        today = date.today()
        
        query = session.query(cls).filter(
            and_(
                cls.hs_code == hs_code,
                cls.country_code == country_code,
                # Rate is currently effective
                cls.effective_date <= today,
                # Rate has not been eliminated
                (cls.elimination_date.is_(None) | (cls.elimination_date > today))
            )
        ).order_by(cls.preferential_rate.asc())
        
        return query.first()