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
from .documents import (
    Document, DocumentCategoryMapping, DocumentCategoryDefinition, DocumentShare,
    DocumentType, DocumentCategory, DocumentStatus, ComplianceStatus, SharePermission
)
from .reports import (
    Report, ReportTemplate, ReportSchedule, AnalyticsMetric,
    ReportType, ReportStatus, ReportFormat, ScheduleFrequency, MetricType
)
from .customer import (
    Customer, CustomerSSOAccount, CustomerSession, CustomerAuthLog,
    CustomerVerification, CustomerVerificationDocument, CustomerShipment, CustomerDigitalAuthority
)
from .edi import (
    EDIMessage, EDIJob, CustomsDeclaration, DeclarationItem
)
from .digital_loa import (
    DigitalLetterOfAuthority, LOASignature, LOAAuditLog, LOATemplate
)
from .ai_document_processing import (
    AIDocumentProcessing, ExtractedField, ProcessingTemplate
)

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
    "RulingStatistics",
    # Document models
    "Document",
    "DocumentCategoryMapping",
    "DocumentCategoryDefinition",
    "DocumentShare",
    "DocumentType",
    "DocumentCategory",
    "DocumentStatus",
    "ComplianceStatus",
    "SharePermission",
    # Report models
    "Report",
    "ReportTemplate",
    "ReportSchedule",
    "AnalyticsMetric",
    "ReportType",
    "ReportStatus",
    "ReportFormat",
    "ScheduleFrequency",
    "MetricType",
    # Customer models
    "Customer",
    "CustomerSSOAccount",
    "CustomerSession",
    "CustomerAuthLog",
    "CustomerVerification",
    "CustomerVerificationDocument",
    "CustomerShipment",
    "CustomerDigitalAuthority",
    # EDI models
    "EDIMessage",
    "EDIJob",
    "CustomsDeclaration",
    "DeclarationItem",
    # Digital LOA models
    "DigitalLetterOfAuthority",
    "LOASignature",
    "LOAAuditLog",
    "LOATemplate",
    # AI Document Processing models
    "AIDocumentProcessing",
    "ExtractedField",
    "ProcessingTemplate"
]