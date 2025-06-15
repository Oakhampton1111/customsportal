"""
Export code models for the Customs Broker Portal.

This module contains the ExportCode model which represents AHECC 
(Australian Harmonized Export Commodity Classification) codes used 
for export classification and their relationships with import tariff codes.
"""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String, Integer, Text, Boolean, DateTime, ForeignKey, Index, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class ExportCode(Base):
    """
    ExportCode model representing AHECC (Australian Harmonized Export Commodity Classification) codes.
    
    This model stores Australian export classification codes and their relationships
    with corresponding import tariff codes for trade classification purposes.
    
    Attributes:
        id: Primary key
        ahecc_code: The AHECC export code (up to 10 characters)
        description: Description of the export code
        statistical_unit: Unit of measurement for statistical purposes
        corresponding_import_code: Reference to corresponding HS import code
        is_active: Whether the code is currently active
        created_at: Timestamp when record was created
        corresponding_import_tariff: Relationship to corresponding TariffCode
    """
    
    __tablename__ = "export_codes"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Core fields
    ahecc_code: Mapped[str] = mapped_column(String(10), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    statistical_unit: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    corresponding_import_code: Mapped[Optional[str]] = mapped_column(
        String(10), 
        ForeignKey("tariff_codes.hs_code", ondelete="SET NULL"),
        nullable=True,
        index=True
    )
    
    # Status and timestamps
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    corresponding_import_tariff: Mapped[Optional["TariffCode"]] = relationship(
        "TariffCode",
        foreign_keys=[corresponding_import_code],
        back_populates="export_codes",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Composite indexes for performance
        Index("ix_export_codes_ahecc", "ahecc_code"),
        Index("ix_export_codes_import", "corresponding_import_code"),
        Index("ix_export_codes_active", "is_active"),
    )
    
    def __repr__(self) -> str:
        """String representation of ExportCode."""
        return (
            f"<ExportCode(id={self.id}, ahecc_code='{self.ahecc_code}', "
            f"description='{self.description[:50]}...')>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.ahecc_code}: {self.description}"
    
    def has_import_equivalent(self) -> bool:
        """
        Check if this export code has a corresponding import tariff code.
        
        Returns:
            bool: True if corresponding_import_code is not None
        """
        return self.corresponding_import_code is not None
    
    def get_statistical_info(self) -> str:
        """
        Get the statistical unit information for this export code.
        
        Returns:
            str: Statistical unit or default message if not specified
        """
        return self.statistical_unit or "No unit specified"
    
    def is_currently_active(self) -> bool:
        """
        Check if this export code is currently active.
        
        Returns:
            bool: The is_active status
        """
        return self.is_active