"""
SQLAlchemy models for the Customs Broker Portal.

This package contains all database models for the application,
organized by functional areas.
"""

from .tariff import TariffCode
from .hierarchy import TariffSection, TariffChapter, TradeAgreement
from .duty import DutyRate
from .fta import FtaRate
from .dumping import DumpingDuty
from .tco import Tco
from .gst import GstProvision
from .export import ExportCode
from .classification import ProductClassification
from .conversation import Conversation, ConversationMessage
from .news import NewsItem, SystemAlert, TradeSummary, NewsAnalytics
from .rulings import TariffRuling, AntiDumpingDecision, RegulatoryUpdate, RulingStatistics

# All models imported and ready for use
# SQLAlchemy models don't need rebuild like Pydantic models

__all__ = [
    "TariffCode",
    "TariffSection",
    "TariffChapter",
    "TradeAgreement",
    "DutyRate",
    "FtaRate",
    "DumpingDuty",
    "Tco",
    "GstProvision",
    "ExportCode",
    "ProductClassification",
    "Conversation",
    "ConversationMessage",
    "NewsItem",
    "SystemAlert", 
    "TradeSummary",
    "NewsAnalytics",
    "TariffRuling",
    "AntiDumpingDecision",
    "RegulatoryUpdate",
    "RulingStatistics"
]