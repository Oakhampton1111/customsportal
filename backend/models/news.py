"""
News and Intelligence Models for Customs Broker Portal
====================================================
SQLAlchemy models for news items, system alerts, and analytics.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, JSON, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Dict, Any
import enum

Base = declarative_base()

class NewsPriority(enum.Enum):
    """News priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class NewsCategory(enum.Enum):
    """News categories."""
    TARIFF = "tariff"
    CUSTOMS = "customs"
    TRADE_AGREEMENT = "trade_agreement"
    REGULATION = "regulation"
    MARKET_UPDATE = "market_update"
    TECHNOLOGY = "technology"
    COMPLIANCE = "compliance"
    INDUSTRY = "industry"

class AlertType(enum.Enum):
    """System alert types."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"

class NewsItem(Base):
    """News items for the dashboard feed."""
    __tablename__ = "news_items"
    
    id = Column(String(50), primary_key=True)
    title = Column(String(500), nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    category = Column(Enum(NewsCategory), nullable=False)
    source = Column(String(200), nullable=False)
    published_date = Column(DateTime, nullable=False)
    url = Column(String(1000), nullable=True)
    tags = Column(JSON, nullable=False, default=list)  # List of strings
    priority = Column(Enum(NewsPriority), nullable=False, default=NewsPriority.MEDIUM)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

class SystemAlert(Base):
    """System alerts and notifications."""
    __tablename__ = "system_alerts"
    
    id = Column(String(50), primary_key=True)
    type = Column(Enum(AlertType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=func.now())
    read = Column(Boolean, nullable=False, default=False)
    action_url = Column(String(500), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())

class TradeSummary(Base):
    """Trade statistics and summaries."""
    __tablename__ = "trade_summaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    period = Column(String(50), nullable=False)  # e.g., "2024-Q1", "2024-05"
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime, nullable=False)
    
    # Trade values (in AUD millions)
    total_trade_value = Column(Float, nullable=False)
    import_value = Column(Float, nullable=False)
    export_value = Column(Float, nullable=False)
    trade_balance = Column(Float, nullable=False)
    
    # JSON data for complex structures
    top_trading_partners = Column(JSON, nullable=False, default=list)
    commodity_highlights = Column(JSON, nullable=False, default=list)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

class NewsAnalytics(Base):
    """News analytics and trends."""
    __tablename__ = "news_analytics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(DateTime, nullable=False)
    
    # Counts
    total_articles = Column(Integer, nullable=False, default=0)
    
    # JSON data for breakdowns
    categories_breakdown = Column(JSON, nullable=False, default=dict)
    sources_breakdown = Column(JSON, nullable=False, default=dict)
    trending_topics = Column(JSON, nullable=False, default=list)
    
    # Metadata
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
