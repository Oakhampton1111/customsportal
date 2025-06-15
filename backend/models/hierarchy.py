"""
Hierarchy models for the Customs Broker Portal.

This module contains models for the tariff hierarchy structure including
sections, chapters, and trade agreements.
"""

from datetime import datetime, date
from typing import List, Optional

from sqlalchemy import (
    String, Integer, Text, Date, DateTime, ForeignKey, func
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class TariffSection(Base):
    """
    TariffSection model representing the highest level of tariff hierarchy.
    
    Sections group related chapters together and provide the broadest
    categorization of goods in the Harmonized System.
    
    Attributes:
        id: Primary key
        section_number: Unique section number (I, II, III, etc.)
        title: Section title/name
        description: Detailed description of the section
        chapter_range: Range of chapters in this section (e.g., "01-05")
    """
    
    __tablename__ = "tariff_sections"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Core fields
    section_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    chapter_range: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    
    # Relationships
    chapters: Mapped[List["TariffChapter"]] = relationship(
        "TariffChapter",
        back_populates="section",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    tariff_codes: Mapped[List["TariffCode"]] = relationship(
        "TariffCode",
        back_populates="section",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation of TariffSection."""
        return (
            f"<TariffSection(id={self.id}, section_number={self.section_number}, "
            f"title='{self.title}')>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Section {self.section_number}: {self.title}"


class TariffChapter(Base):
    """
    TariffChapter model representing chapters within tariff sections.
    
    Chapters provide the second level of hierarchy in the Harmonized System,
    grouping related headings together within a section.
    
    Attributes:
        id: Primary key
        chapter_number: Unique chapter number (01-99)
        title: Chapter title/name
        chapter_notes: Additional notes and explanations for the chapter
        section_id: Foreign key to tariff_sections
    """
    
    __tablename__ = "tariff_chapters"
    
    # Primary key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Core fields
    chapter_number: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    chapter_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Foreign key
    section_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("tariff_sections.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Relationships
    section: Mapped["TariffSection"] = relationship(
        "TariffSection",
        back_populates="chapters",
        lazy="select"
    )
    
    tariff_codes: Mapped[List["TariffCode"]] = relationship(
        "TariffCode",
        back_populates="chapter",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation of TariffChapter."""
        return (
            f"<TariffChapter(id={self.id}, chapter_number={self.chapter_number}, "
            f"title='{self.title}')>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"Chapter {self.chapter_number:02d}: {self.title}"


class TradeAgreement(Base):
    """
    TradeAgreement model representing Free Trade Agreements (FTAs).
    
    This model stores information about trade agreements that affect
    tariff rates and customs procedures.
    
    Attributes:
        fta_code: Primary key - unique FTA code
        full_name: Full name of the trade agreement
        entry_force_date: Date when the agreement entered into force
        status: Current status of the agreement (active, suspended, etc.)
        agreement_url: URL to the official agreement document
        created_at: Timestamp when record was created
    """
    
    __tablename__ = "trade_agreements"
    
    # Primary key
    fta_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    
    # Core fields
    full_name: Mapped[str] = mapped_column(String(200), nullable=False)
    entry_force_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    agreement_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Relationships
    fta_rates: Mapped[List["FtaRate"]] = relationship(
        "FtaRate",
        back_populates="trade_agreement",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation of TradeAgreement."""
        return (
            f"<TradeAgreement(fta_code='{self.fta_code}', "
            f"full_name='{self.full_name}', status='{self.status}')>"
        )
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"{self.fta_code}: {self.full_name}"
    
    @property
    def is_active(self) -> bool:
        """Check if the trade agreement is currently active."""
        return self.status.lower() == "active"
    
    @property
    def is_in_force(self) -> bool:
        """Check if the agreement has entered into force."""
        if not self.entry_force_date:
            return False
        return self.entry_force_date <= date.today()

# Forward references are automatically resolved in Pydantic v2
# Circular imports removed to prevent SQLAlchemy table redefinition errors