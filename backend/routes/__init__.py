"""
Routes package for the Customs Broker Portal API.

This package contains all API route modules organized by functionality.
"""

from routes.tariff import router as tariff_router
from routes.duty_calculator import router as duty_calculator_router
# from routes.search import router as search_router  # Temporarily disabled due to AI dependency
from routes.news import router as news_router
from routes.export import router as export_router
from routes.rulings import router as rulings_router
from routes.documents import router as documents_router
from routes.reports import router as reports_router
from routes.compliance import router as compliance_router
from routes.customer_auth import router as customer_auth_router
from routes.edi_routes import router as edi_router
from routes.loa_routes import router as loa_router
from routes.ai_document_processing import router as ai_document_processing_router
# from routes.ai import router as ai_router  # Temporarily disabled due to CFFI dependency issue

__all__ = [
    "tariff_router",
    "duty_calculator_router",
    # "search_router",  # Temporarily disabled
    "news_router",
    "export_router",
    "rulings_router",
    "documents_router",
    "reports_router",
    "compliance_router",
    "customer_auth_router",
    "edi_router",
    "loa_router",
    "ai_document_processing_router",
    # "ai_router"  # Temporarily disabled
]