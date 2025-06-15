"""
Database connection and session management for the Customs Broker Portal.

This module provides async SQLAlchemy setup with connection pooling,
session management, and database utilities for the FastAPI application.
"""

import logging
from typing import AsyncGenerator, Optional
from contextlib import asynccontextmanager

from sqlalchemy import MetaData, event
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    create_async_engine,
    async_sessionmaker,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.pool import NullPool, AsyncAdaptedQueuePool
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import text

from config import get_settings, is_development

# Configure logging
logger = logging.getLogger(__name__)

# SQLAlchemy metadata and base class
metadata = MetaData()
Base = declarative_base(metadata=metadata)

# Global variables for database engine and session factory
engine: Optional[AsyncEngine] = None
async_session_factory: Optional[async_sessionmaker[AsyncSession]] = None


def get_engine_config() -> dict:
    """
    Get database engine configuration based on environment settings.
    
    Returns:
        dict: Engine configuration parameters
    """
    settings = get_settings()
    
    config = {
        "url": settings.database_url,
        "echo": is_development(),  # Log SQL queries in development
        "echo_pool": is_development(),  # Log connection pool events in development
        "future": True,  # Use SQLAlchemy 2.0 style
    }
    
    # Configure connection pooling
    if settings.database_url.startswith("sqlite"):
        # SQLite doesn't support connection pooling
        config["poolclass"] = NullPool
    else:
        # PostgreSQL with connection pooling
        config.update({
            "poolclass": AsyncAdaptedQueuePool,
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow,
            "pool_timeout": settings.database_pool_timeout,
            "pool_recycle": settings.database_pool_recycle,
            "pool_pre_ping": True,  # Validate connections before use
        })
    
    return config


async def create_database_engine() -> AsyncEngine:
    """
    Create and configure the async database engine.
    
    Returns:
        AsyncEngine: Configured SQLAlchemy async engine
    """
    config = get_engine_config()
    
    try:
        engine = create_async_engine(**config)
        
        # Add event listeners for connection management
        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas for better performance (if using SQLite)."""
            if "sqlite" in str(engine.url):
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=1000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
        
        @event.listens_for(engine.sync_engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout events in development."""
            if is_development():
                logger.debug(f"Connection checked out: {id(dbapi_connection)}")
        
        @event.listens_for(engine.sync_engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log connection checkin events in development."""
            if is_development():
                logger.debug(f"Connection checked in: {id(dbapi_connection)}")
        
        logger.info(f"Database engine created successfully: {engine.url}")
        return engine
        
    except Exception as e:
        logger.error(f"Failed to create database engine: {e}")
        raise


def create_session_factory(engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
    """
    Create async session factory.
    
    Args:
        engine: SQLAlchemy async engine
        
    Returns:
        async_sessionmaker: Session factory for creating database sessions
    """
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,  # Keep objects accessible after commit
        autoflush=True,  # Automatically flush before queries
        autocommit=False,  # Manual transaction control
    )


async def init_database() -> None:
    """
    Initialize the database connection and session factory.
    
    This function should be called during application startup.
    """
    global engine, async_session_factory
    
    try:
        logger.info("Initializing database connection...")
        
        # Create engine and session factory
        engine = await create_database_engine()
        async_session_factory = create_session_factory(engine)
        
        # Test the connection
        await test_database_connection()
        
        logger.info("Database initialization completed successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def close_database() -> None:
    """
    Close database connections and cleanup resources.
    
    This function should be called during application shutdown.
    """
    global engine, async_session_factory
    
    try:
        if engine:
            logger.info("Closing database connections...")
            await engine.dispose()
            engine = None
            async_session_factory = None
            logger.info("Database connections closed successfully")
            
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")
        raise


async def test_database_connection() -> bool:
    """
    Test the database connection.
    
    Returns:
        bool: True if connection is successful, False otherwise
    """
    try:
        if not engine:
            raise RuntimeError("Database engine not initialized")
            
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT 1"))
            row = result.fetchone()
            
            if row and row[0] == 1:
                logger.info("Database connection test successful")
                return True
            else:
                logger.error("Database connection test failed: unexpected result")
                return False
                
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get an async database session.
    
    This function is designed to be used as a FastAPI dependency.
    It provides proper session lifecycle management with automatic
    cleanup and error handling.
    
    Yields:
        AsyncSession: Database session
        
    Example:
        @app.get("/tariff-codes/")
        async def get_tariff_codes(
            db: AsyncSession = Depends(get_async_session)
        ):
            # Use the session
            result = await db.execute(select(TariffCode))
            return result.scalars().all()
    """
    if not async_session_factory:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_factory() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error in database session: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Context manager for database sessions.
    
    This provides an alternative way to get database sessions
    outside of FastAPI dependency injection.
    
    Example:
        async with get_db_session() as db:
            result = await db.execute(select(TariffCode))
            codes = result.scalars().all()
    """
    if not async_session_factory:
        raise RuntimeError("Database not initialized. Call init_database() first.")
    
    async with async_session_factory() as session:
        try:
            yield session
        except SQLAlchemyError as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        except Exception as e:
            logger.error(f"Unexpected error in database session: {e}")
            await session.rollback()
            raise


async def execute_raw_sql(query: str, params: Optional[dict] = None) -> any:
    """
    Execute raw SQL query.
    
    Args:
        query: SQL query string
        params: Query parameters
        
    Returns:
        Query result
    """
    async with get_db_session() as session:
        result = await session.execute(text(query), params or {})
        return result


async def get_database_info() -> dict:
    """
    Get database information for health checks and monitoring.
    
    Returns:
        dict: Database information including version, connection count, etc.
    """
    try:
        async with get_db_session() as session:
            # Get SQLite version
            version_result = await session.execute(text("SELECT sqlite_version()"))
            version = version_result.scalar()
            
            # For SQLite, we don't have current_database() function
            database_name = "customs_portal.db"
            
            # SQLite doesn't have pg_stat_activity, so we'll use a simple count
            active_connections = 1  # SQLite typically has one connection
            
            return {
                "database_name": database_name,
                "version": f"SQLite {version}",
                "active_connections": active_connections,
                "engine_url": str(engine.url) if engine else None,
                "pool_size": get_settings().database_pool_size,
                "status": "healthy"
            }
            
    except Exception as e:
        logger.error(f"Failed to get database info: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


# Health check function for the database
async def health_check() -> dict:
    """
    Perform database health check.
    
    Returns:
        dict: Health check result
    """
    try:
        connection_ok = await test_database_connection()
        db_info = await get_database_info()
        
        return {
            "database": {
                "status": "healthy" if connection_ok else "unhealthy",
                "connection_test": connection_ok,
                **db_info
            }
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "database": {
                "status": "unhealthy",
                "error": str(e)
            }
        }


# Export commonly used functions and classes
__all__ = [
    "Base",
    "metadata",
    "init_database",
    "close_database",
    "get_async_session",
    "get_db_session",
    "test_database_connection",
    "execute_raw_sql",
    "get_database_info",
    "health_check",
]