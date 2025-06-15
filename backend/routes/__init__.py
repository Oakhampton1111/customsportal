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
# from routes.ai import router as ai_router  # Temporarily disabled due to CFFI dependency issue

__all__ = [
    "tariff_router", 
    "duty_calculator_router", 
    # "search_router",  # Temporarily disabled
    "news_router",
    "export_router", 
    "rulings_router",
    # "ai_router"  # Temporarily disabled
]