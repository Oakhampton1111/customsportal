"""
Customs Broker Portal Backend Package

This package provides the FastAPI backend for the Australian Customs Broker Portal,
including database management, API endpoints, and AI-powered classification services.
"""

__version__ = "1.0.0"
__author__ = "Customs Broker Portal Team"
__description__ = "FastAPI backend for Australian customs brokerage platform"

# Import main components for easy access
from config import settings, get_settings
from database import get_async_session, init_database, close_database

# Note: Main app import moved to avoid circular import issues during testing
# Import app conditionally to prevent issues during test discovery
try:
    from main import app
    __all__ = [
        "app",
        "settings",
        "get_settings",
        "get_async_session",
        "init_database",
        "close_database",
    ]
except ImportError:
    # If main app can't be imported (e.g., during testing), exclude it
    __all__ = [
        "settings",
        "get_settings",
        "get_async_session",
        "init_database",
        "close_database",
    ]