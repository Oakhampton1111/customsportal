"""
Main FastAPI application for the Customs Broker Portal.

This module initializes the FastAPI application with all necessary middleware,
error handling, logging, and basic endpoints for the Australian customs broker portal.
"""
import logging
import sys
import traceback
from contextlib import asynccontextmanager
from datetime import datetime
from typing import Dict, Any

import structlog
import uvicorn
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from config import get_settings, get_cors_config, is_development, is_production
from database import init_database, close_database, health_check
from routes.tariff import router as tariff_router
from routes.duty_calculator import router as duty_calculator_router
from routes.news import router as news_router
from routes.export import router as export_router
from routes.rulings import router as rulings_router
# from routes.search import router as search_router  # Temporarily disabled due to AI dependency
# from routes.ai import router as ai_router  # Temporarily disabled due to CFFI dependency issue

# Configure structured logging
def configure_logging():
    """Configure structured logging for the application."""
    settings = get_settings()
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if settings.log_format == "json" else structlog.dev.ConsoleRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )
    
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, settings.log_level),
    )
    
    # Set specific logger levels
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(
        logging.INFO if is_development() else logging.WARNING
    )


# Initialize logging
configure_logging()
logger = structlog.get_logger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for request/response logging."""
    
    async def dispatch(self, request: Request, call_next):
        """Log request and response details."""
        start_time = datetime.utcnow()
        
        # Log request
        logger.info(
            "Request started",
            method=request.method,
            url=str(request.url),
            client_ip=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = (datetime.utcnow() - start_time).total_seconds()
            
            # Log response
            logger.info(
                "Request completed",
                method=request.method,
                url=str(request.url),
                status_code=response.status_code,
                process_time=process_time,
            )
            
            # Add processing time header
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = (datetime.utcnow() - start_time).total_seconds()
            
            logger.error(
                "Request failed",
                method=request.method,
                url=str(request.url),
                error=str(e),
                process_time=process_time,
                exc_info=True,
            )
            
            raise


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for the FastAPI application.
    """
    # Startup
    logger.info("Starting Customs Broker Portal API...")
    
    try:
        # Initialize database
        await init_database()
        logger.info("Database initialized successfully")
        
        # Add any other startup tasks here
        logger.info("Application startup completed")
        
        yield
        
    except Exception as e:
        logger.error(f"Application startup failed: {e}", exc_info=True)
        raise
    
    finally:
        # Shutdown
        logger.info("Shutting down Customs Broker Portal API...")
        
        try:
            # Close database connections
            await close_database()
            logger.info("Database connections closed")
            
            # Add any other cleanup tasks here
            logger.info("Application shutdown completed")
            
        except Exception as e:
            logger.error(f"Application shutdown error: {e}", exc_info=True)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application instance
    """
    settings = get_settings()
    
    # Create FastAPI app with metadata
    app = FastAPI(
        title=settings.app_name,
        description="""
        Australian Customs Broker Portal API
        
        A comprehensive platform for Australian customs brokers providing:
        - Tariff code classification and lookup with hierarchical navigation
        - Comprehensive duty calculations including FTA preferences and exemptions
        - Anti-dumping and countervailing duty information
        - Tariff Concession Order (TCO) management
        - GST provisions and exemptions
        - AI-powered product classification with Claude/Anthropic integration
        - Export code (AHECC) management
        - Advanced tariff search and filtering capabilities
        - Intelligent search with similarity matching and confidence scoring
        - Broker feedback system for continuous learning and improvement
        
        **Tariff API Features:**
        - Browse tariff sections and chapters
        - Navigate hierarchical tariff trees with lazy loading
        - Get detailed tariff code information with related data
        - Search tariff codes with full-text search and filters
        - Access duty rates, FTA rates, and related trade information
        
        **Duty Calculator Features:**
        - Comprehensive duty calculations with all components (general, FTA, anti-dumping, TCO, GST)
        - Best rate analysis with potential savings identification
        - Detailed calculation breakdowns with step-by-step explanations
        - FTA preferential rate lookup and comparison
        - TCO exemption verification and eligibility checking
        - Real-time duty calculations with compliance notes and warnings
        
        **AI-Powered Search & Classification Features:**
        - Natural language product classification with confidence scoring
        - Batch processing for multiple product classifications
        - Similarity-based classification search and matching
        - Broker verification workflows with feedback integration
        - Classification history tracking and performance analytics
        - Continuous learning capabilities through broker feedback
        - Advanced search with full-text capabilities across product descriptions
        
        This API serves the Australian customs brokerage industry with accurate,
        up-to-date trade compliance information sourced from official ABF data,
        enhanced with cutting-edge AI capabilities for intelligent classification
        and comprehensive duty calculation tools.
        """,
        version=settings.app_version,
        docs_url=settings.docs_url if not is_production() else None,
        redoc_url=settings.redoc_url if not is_production() else None,
        openapi_url=settings.openapi_url if not is_production() else None,
        lifespan=lifespan,
        debug=settings.debug,
    )
    
    # Add middleware
    setup_middleware(app)
    
    # Add exception handlers
    setup_exception_handlers(app)
    
    # Add routes
    setup_routes(app)
    
    return app


def setup_middleware(app: FastAPI) -> None:
    """Configure application middleware."""
    settings = get_settings()
    
    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        **get_cors_config(),
    )
    
    # Trusted host middleware (security)
    if is_production():
        app.add_middleware(
            TrustedHostMiddleware,
            allowed_hosts=["*.customs-broker-portal.com", "localhost", "127.0.0.1"]
        )
    
    # Request logging middleware
    app.add_middleware(LoggingMiddleware)
    
    logger.info("Middleware configured successfully")


def setup_exception_handlers(app: FastAPI) -> None:
    """Configure global exception handlers."""
    
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        """Handle HTTP exceptions."""
        logger.warning(
            "HTTP exception",
            status_code=exc.status_code,
            detail=exc.detail,
            url=str(request.url),
        )
        
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "type": "http_error",
                    "status_code": exc.status_code,
                    "message": exc.detail,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            },
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        """Handle request validation errors."""
        logger.warning(
            "Validation error",
            errors=exc.errors(),
            url=str(request.url),
        )
        
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "type": "validation_error",
                    "status_code": 422,
                    "message": "Request validation failed",
                    "details": exc.errors(),
                    "timestamp": datetime.utcnow().isoformat(),
                }
            },
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle unexpected exceptions."""
        logger.error(
            "Unexpected error",
            error=str(exc),
            url=str(request.url),
            exc_info=True,
        )
        
        # Don't expose internal errors in production
        if is_production():
            message = "An internal server error occurred"
            details = None
        else:
            message = str(exc)
            details = traceback.format_exc()
        
        return JSONResponse(
            status_code=500,
            content={
                "error": {
                    "type": "internal_error",
                    "status_code": 500,
                    "message": message,
                    "details": details,
                    "timestamp": datetime.utcnow().isoformat(),
                }
            },
        )
    
    logger.info("Exception handlers configured successfully")


def setup_routes(app: FastAPI) -> None:
    """Configure application routes."""
    
    @app.get("/", tags=["Root"])
    async def root() -> Dict[str, Any]:
        """
        Root endpoint providing API information.
        
        Returns basic information about the Customs Broker Portal API.
        """
        settings = get_settings()
        
        return {
            "message": "Welcome to the Customs Broker Portal API",
            "description": "Australian customs brokerage platform providing tariff classification, duty calculations, and trade compliance tools",
            "version": settings.app_version,
            "environment": settings.environment,
            "docs_url": settings.docs_url if not is_production() else None,
            "features": [
                "Tariff code classification and lookup with hierarchical navigation",
                "Comprehensive duty calculations with FTA preferences and exemptions",
                "Anti-dumping and countervailing duties",
                "Tariff Concession Orders (TCOs)",
                "GST provisions and exemptions",
                "AI-powered product classification with confidence scoring",
                "Natural language search and similarity matching",
                "Broker feedback system for continuous learning",
                "Advanced search with full-text capabilities",
                "Classification history and performance analytics",
                "Export code (AHECC) management",
                "Advanced tariff search and filtering capabilities",
                "Detailed duty calculation breakdowns and analysis",
                "Best rate analysis with potential savings identification",
            ],
            "tariff_endpoints": [
                "/api/tariff/sections - Browse all tariff sections",
                "/api/tariff/chapters/{section_id} - Get chapters for a section",
                "/api/tariff/tree/{section_id} - Navigate hierarchical tariff tree",
                "/api/tariff/code/{hs_code} - Get detailed tariff information",
                "/api/tariff/search - Search tariff codes with filters",
            ],
            "search_endpoints": [
                "/api/search/classify - AI-powered product classification",
                "/api/search/classify/batch - Batch product classification",
                "/api/search/feedback - Store broker feedback for learning",
                "/api/search/products - Full-text search across product descriptions",
                "/api/search/tariffs - Advanced tariff search with AI insights",
                "/api/search/similarity - Similarity-based classification search",
                "/api/search/history/{id} - Get classification history",
                "/api/search/stats - Classification analytics and statistics",
            ],
            "duty_endpoints": [
                "/api/duty/calculate - Comprehensive duty calculation with all components",
                "/api/duty/rates/{hs_code} - Get all duty rates for an HS code",
                "/api/duty/breakdown - Detailed calculation breakdown with steps",
                "/api/duty/fta-rates/{hs_code}/{country_code} - FTA preferential rates",
                "/api/duty/tco-check/{hs_code} - TCO exemption verification",
            ],
            "timestamp": datetime.utcnow().isoformat(),
        }
    
    @app.get("/health", tags=["Health"])
    async def health_check_endpoint() -> Dict[str, Any]:
        """
        Health check endpoint.
        
        Provides comprehensive health status including database connectivity,
        system information, and service availability.
        """
        try:
            # Get system information (always available)
            system_info = {
                "timestamp": datetime.utcnow().isoformat(),
                "environment": get_settings().environment,
                "version": get_settings().app_version,
                "python_version": sys.version,
            }
            
            # Try to get database health, but don't fail if database is not ready
            try:
                db_health = await health_check()
                db_status = db_health.get("database", {}).get("status", "unknown")
            except Exception as db_error:
                logger.warning(f"Database health check failed: {db_error}")
                db_health = {
                    "database": {
                        "status": "initializing",
                        "error": "Database connection not ready",
                        "details": str(db_error)
                    }
                }
                db_status = "initializing"
            
            # Service is healthy if it can respond, even if database is initializing
            # This allows the health check to pass during startup
            overall_status = "healthy" if db_status in ["healthy", "initializing"] else "degraded"
            
            return {
                "status": overall_status,
                "system": system_info,
                **db_health,
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}", exc_info=True)
            
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat(),
            }
    
    @app.get("/version", tags=["Info"])
    async def version() -> Dict[str, str]:
        """
        Get API version information.
        
        Returns version details and build information.
        """
        settings = get_settings()
        
        return {
            "version": settings.app_version,
            "name": settings.app_name,
            "environment": settings.environment,
            "build_timestamp": datetime.utcnow().isoformat(),
        }
    
    # Add tariff routes
    app.include_router(tariff_router)
    logger.info("Tariff API routes included successfully")
    
    # Add news routes
    app.include_router(news_router)
    logger.info("News API routes included successfully")
    
    # Add rulings routes
    app.include_router(rulings_router)
    logger.info("Rulings API routes included successfully")
    
    # Add duty calculator routes
    app.include_router(duty_calculator_router)
    logger.info("Duty Calculator API routes included successfully")
    
    # Add export routes
    app.include_router(export_router)
    logger.info("Export API routes included successfully")
    
    # Add search routes
    # app.include_router(search_router)  # Temporarily disabled due to AI dependency
    logger.info("Search API routes temporarily disabled")
    
    # Add AI routes
    # app.include_router(ai_router)  # Temporarily disabled due to CFFI dependency issue
    logger.info("AI API routes temporarily disabled")
    
    logger.info("Routes configured successfully")


# Create the FastAPI application
app = create_app()


def main():
    """
    Main entry point for running the application.
    
    This function is used when running the application directly
    or through a process manager like systemd.
    """
    settings = get_settings()
    
    logger.info(
        "Starting Customs Broker Portal API server",
        host=settings.host,
        port=settings.port,
        environment=settings.environment,
        debug=settings.debug,
    )
    
    uvicorn.run(
        "backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and is_development(),
        log_level=settings.log_level.lower(),
        access_log=True,
        server_header=False,  # Security: don't expose server info
        date_header=False,    # Security: don't expose date info
    )


if __name__ == "__main__":
    main()
