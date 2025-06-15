"""
Rulings and Regulatory Updates Models for Customs Broker Portal
==============================================================
SQLAlchemy models for tariff rulings, anti-dumping decisions, and regulatory updates.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Dict, Any
import enum

Base = declarative_base()

class RulingStatus(enum.Enum):
    """Ruling status types."""
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    REVOKED = "revoked"

class DecisionType(enum.Enum):
    """Anti-dumping decision types."""
    INITIATION = "initiation"
    PRELIMINARY = "preliminary"
    FINAL = "final"
    REVIEW = "review"
    TERMINATION = "termination"

class UpdateCategory(enum.Enum):
    """Regulatory update categories."""
    TARIFF = "tariff"
    CUSTOMS = "customs"
    TRADE_AGREEMENT = "trade_agreement"
    REGULATION = "regulation"
    PROCEDURE = "procedure"

class UpdateType(enum.Enum):
    """Regulatory update types."""
    NEW = "new"
    AMENDMENT = "amendment"
    REPEAL = "repeal"
    CLARIFICATION = "clarification"

class ImpactLevel(enum.Enum):
    """Impact level for regulatory updates."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TariffRuling(Base):
    """Tariff classification rulings."""
    __tablename__ = "tariff_rulings"
    
    ruling_number = Column(String(50), primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    hs_code = Column(String(20), nullable=False)
    commodity_description = Column(Text, nullable=False)
    ruling_date = Column(DateTime, nullable=False)
    effective_date = Column(DateTime, nullable=False)
    status = Column(Enum(RulingStatus), nullable=False, default=RulingStatus.ACTIVE)
    tariff_classification = Column(String(100), nullable=False)
    duty_rate = Column(String(100), nullable=False)
    origin_country = Column(String(100), nullable=True)
    applicant = Column(String(200), nullable=True)
    ruling_text = Column(Text, nullable=False)
    references = Column(JSON, nullable=False, default=list)  # List of reference documents
    related_rulings = Column(JSON, nullable=False, default=list)  # List of related ruling numbers
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

class AntiDumpingDecision(Base):
    """Anti-dumping and countervailing duty decisions."""
    __tablename__ = "anti_dumping_decisions"
    
    id = Column(String(50), primary_key=True)
    case_number = Column(String(100), nullable=False)
    title = Column(String(500), nullable=False)
    product_description = Column(Text, nullable=False)
    hs_codes = Column(JSON, nullable=False, default=list)  # List of HS codes
    countries_involved = Column(JSON, nullable=False, default=list)  # List of countries
    decision_type = Column(Enum(DecisionType), nullable=False)
    decision_date = Column(DateTime, nullable=False)
    effective_date = Column(DateTime, nullable=False)
    duty_rate = Column(String(100), nullable=True)
    status = Column(Enum(RulingStatus), nullable=False, default=RulingStatus.ACTIVE)
    summary = Column(Text, nullable=False)
    document_url = Column(String(1000), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

class RegulatoryUpdate(Base):
    """Regulatory updates and changes."""
    __tablename__ = "regulatory_updates"
    
    id = Column(String(50), primary_key=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(Enum(UpdateCategory), nullable=False)
    update_type = Column(Enum(UpdateType), nullable=False)
    published_date = Column(DateTime, nullable=False)
    effective_date = Column(DateTime, nullable=False)
    affected_codes = Column(JSON, nullable=False, default=list)  # List of HS codes affected
    impact_level = Column(Enum(ImpactLevel), nullable=False, default=ImpactLevel.MEDIUM)
    summary = Column(Text, nullable=False)
    full_text = Column(Text, nullable=True)
    document_url = Column(String(1000), nullable=True)
    contact_info = Column(String(500), nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

class RulingStatistics(Base):
    """Statistics for rulings and decisions."""
    __tablename__ = "ruling_statistics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    period = Column(String(50), nullable=False)  # e.g., "2024-Q1", "2024-05"
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Counts
    total_rulings = Column(Integer, nullable=False, default=0)
    active_rulings = Column(Integer, nullable=False, default=0)
    new_rulings = Column(Integer, nullable=False, default=0)
    superseded_rulings = Column(Integer, nullable=False, default=0)
    anti_dumping_cases = Column(Integer, nullable=False, default=0)
    regulatory_updates = Column(Integer, nullable=False, default=0)
    
    # JSON data for breakdowns
    category_breakdown = Column(JSON, nullable=False, default=dict)
    impact_level_breakdown = Column(JSON, nullable=False, default=dict)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
