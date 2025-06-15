"""
Tariff code models for the Customs Broker Portal.

This module contains the TariffCode model which represents the hierarchical
HS (Harmonized System) code structure used in customs classification.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    String, Integer, Text, Boolean, DateTime, CheckConstraint, Index,
    ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, foreign

from database import Base


class TariffCode(Base):
    """
    TariffCode model representing the hierarchical HS code structure.
    
    This model stores Harmonized System (HS) codes used for customs classification.
    The codes are organized in a hierarchical structure with different levels
    (2, 4, 6, 8, 10 digits) representing increasing specificity.
    
    Attributes:
        id: Primary key
        hs_code: The HS code (2-10 digits)
        description: Description of the tariff code
        unit_description: Unit of measurement description
        parent_code: Reference to parent HS code for hierarchy
        level: Hierarchy level (2, 4, 6, 8, or 10 digits)
        chapter_notes: Additional notes for the chapter
        section_id: Foreign key to tariff_sections
        chapter_id: Foreign key to tariff_chapters
        is_active: Whether the code is currently active
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """
    
    __tablename__ = "tariff_codes"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Core fields
    hs_code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    unit_description: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    parent_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)
    level: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    chapter_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Foreign keys
    section_id: Mapped[Optional[int]] = mapped_column(
        Integer, 
        ForeignKey("tariff_sections.id", ondelete="SET NULL"),
        nullable=True
    )
    chapter_id: Mapped[Optional[int]] = mapped_column(
        Integer,
        ForeignKey("tariff_chapters.id", ondelete="SET NULL"), 
        nullable=True
    )
    
    # Status and timestamps
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    section: Mapped[Optional["TariffSection"]] = relationship(
        "TariffSection",
        back_populates="tariff_codes",
        lazy="select"
    )
    
    chapter: Mapped[Optional["TariffChapter"]] = relationship(
        "TariffChapter", 
        back_populates="tariff_codes",
        lazy="select"
    )
    
    # Self-referential relationships for hierarchy
    parent: Mapped[Optional["TariffCode"]] = relationship(
        "TariffCode",
        primaryjoin="TariffCode.parent_code == foreign(TariffCode.hs_code)",
        remote_side=[hs_code],
        lazy="select"
    )
    
    children: Mapped[List["TariffCode"]] = relationship(
        "TariffCode",
        primaryjoin="foreign(TariffCode.parent_code) == TariffCode.hs_code",
        lazy="select"
    )
    
    # Duty and FTA rate relationships
    duty_rates: Mapped[List["DutyRate"]] = relationship(
        "DutyRate",
        back_populates="tariff_code",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    fta_rates: Mapped[List["FtaRate"]] = relationship(
        "FtaRate",
        back_populates="tariff_code",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    dumping_duties: Mapped[List["DumpingDuty"]] = relationship(
        "DumpingDuty",
        back_populates="tariff_code",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    tcos: Mapped[List["Tco"]] = relationship(
        "Tco",
        back_populates="tariff_code",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    gst_provisions: Mapped[List["GstProvision"]] = relationship(
        "GstProvision",
        back_populates="tariff_code",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Export code relationships
    export_codes: Mapped[List["ExportCode"]] = relationship(
        "ExportCode",
        back_populates="corresponding_import_tariff",
        foreign_keys="ExportCode.corresponding_import_code",
        lazy="select"
    )
    
    # Product classification relationships
    product_classifications: Mapped[List["ProductClassification"]] = relationship(
        "ProductClassification",
        back_populates="tariff_code",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    # Table constraints and indexes
    __table_args__ = (
        # Level constraint - only allow valid HS code levels
        CheckConstraint(
            "level IN (2, 4, 6, 8, 10)",
            name="ck_tariff_codes_level"
        ),
        
        # Composite indexes for performance
        Index("ix_tariff_codes_hierarchy", "parent_code", "level"),
        Index("ix_tariff_codes_section_chapter", "section_id", "chapter_id"),
        Index("ix_tariff_codes_active_level", "is_active", "level"),
    )
    
    def __repr__(self) -> str:
        """String representation of TariffCode."""
        return (
            f"<TariffCode(id={self.id}, hs_code='{self.hs_code}', "
            f"level={self.level}, description='{self.description[:50]}...')>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.hs_code}: {self.description}"
    
    @property
    def is_chapter_level(self) -> bool:
        """Check if this is a chapter-level code (2 digits)."""
        return self.level == 2
    
    @property
    def is_heading_level(self) -> bool:
        """Check if this is a heading-level code (4 digits)."""
        return self.level == 4
    
    @property
    def is_subheading_level(self) -> bool:
        """Check if this is a subheading-level code (6 digits)."""
        return self.level == 6
    
    @property
    def is_statistical_level(self) -> bool:
        """Check if this is a statistical-level code (8 or 10 digits)."""
        return self.level in (8, 10)
    
    def get_hierarchy_path(self) -> List[str]:
        """
        Get the full hierarchy path from root to this code.
        
        Returns:
            List of HS codes from root to current code
        """
        path = []
        current = self
        
        while current:
            path.insert(0, current.hs_code)
            current = current.parent
            
        return path
    
    def get_chapter_code(self) -> Optional[str]:
        """
        Get the chapter-level code (2 digits) for this tariff code.
        
        Returns:
            Chapter code or None if not found
        """
        if self.level == 2:
            return self.hs_code
        elif len(self.hs_code) >= 2:
            return self.hs_code[:2]
        return None
    
    def get_heading_code(self) -> Optional[str]:
        """
        Get the heading-level code (4 digits) for this tariff code.
        
        Returns:
            Heading code or None if not applicable
        """
        if self.level <= 4 and len(self.hs_code) >= 4:
            return self.hs_code[:4]
        return None


# Circular imports removed to prevent SQLAlchemy table redefinition errors
# Forward references are automatically resolved in SQLAlchemy ORM