"""
Product classification models for the Customs Broker Portal.

This module contains the ProductClassification model which represents AI-generated
product classifications with confidence scores and broker verification capabilities,
establishing a relationship with the existing TariffCode model.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String, Integer, Text, Boolean, DateTime, DECIMAL, CheckConstraint, Index,
    ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ProductClassification(Base):
    """
    ProductClassification model representing AI-generated product classifications.
    
    This model stores AI-generated product classifications with confidence scores
    and broker verification capabilities, establishing relationships with tariff codes
    for customs classification purposes.
    
    Attributes:
        id: Primary key
        product_description: Description of the product being classified
        hs_code: The classified HS code (references tariff_codes.hs_code)
        confidence_score: AI confidence score (0.00-1.00)
        classification_source: Source of classification (ai, broker, ruling)
        verified_by_broker: Whether the classification has been verified by a broker
        broker_user_id: Reference to user who verified the classification
        created_at: Timestamp when record was created
        tariff_code: Relationship to corresponding TariffCode
    """
    
    __tablename__ = "product_classifications"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Core fields
    product_description: Mapped[str] = mapped_column(Text, nullable=False)
    hs_code: Mapped[str] = mapped_column(
        String(10), 
        ForeignKey("tariff_codes.hs_code", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    confidence_score: Mapped[Optional[float]] = mapped_column(
        DECIMAL(3, 2), 
        nullable=True
    )
    classification_source: Mapped[Optional[str]] = mapped_column(
        String(50), 
        nullable=True,
        index=True
    )
    verified_by_broker: Mapped[bool] = mapped_column(
        Boolean, 
        default=False, 
        nullable=False,
        index=True
    )
    broker_user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    tariff_code: Mapped["TariffCode"] = relationship(
        "TariffCode",
        foreign_keys=[hs_code],
        back_populates="product_classifications",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Confidence score constraint - must be between 0.00 and 1.00
        CheckConstraint(
            "confidence_score >= 0.00 AND confidence_score <= 1.00",
            name="chk_confidence_score"
        ),
        
        # Composite indexes for performance
        Index("ix_product_class_hs_code", "hs_code"),
        Index("ix_product_class_verified", "verified_by_broker", "confidence_score"),
        Index("ix_product_class_source", "classification_source"),
    )
    
    def __repr__(self) -> str:
        """String representation of ProductClassification."""
        return (
            f"<ProductClassification(id={self.id}, hs_code='{self.hs_code}', "
            f"confidence={self.confidence_score}, verified={self.verified_by_broker}, "
            f"description='{self.product_description[:50]}...')>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.hs_code}: {self.product_description[:100]}..."
    
    def confidence_level_description(self) -> str:
        """
        Get a human-readable description of the confidence level.
        
        Returns:
            str: "High" (>0.8), "Medium" (0.5-0.8), "Low" (<0.5), or "Unknown" (None)
        """
        if self.confidence_score is None:
            return "Unknown"
        elif self.confidence_score > 0.8:
            return "High"
        elif self.confidence_score >= 0.5:
            return "Medium"
        else:
            return "Low"
    
    def is_verified(self) -> bool:
        """
        Check if this classification has been verified by a broker.
        
        Returns:
            bool: The verified_by_broker status
        """
        return self.verified_by_broker
    
    def needs_verification(self) -> bool:
        """
        Check if this classification needs broker verification.
        
        Returns:
            bool: True if confidence_score < 0.8 and not verified_by_broker
        """
        if self.verified_by_broker:
            return False
        if self.confidence_score is None:
            return True
        return self.confidence_score < 0.8
    
    def confidence_percentage(self) -> str:
        """
        Get the confidence score as a percentage string.
        
        Returns:
            str: Confidence score as percentage (e.g., "85%") or "N/A" if None
        """
        if self.confidence_score is None:
            return "N/A"
        return f"{int(self.confidence_score * 100)}%"