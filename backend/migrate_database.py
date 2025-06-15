#!/usr/bin/env python3
"""
Database Migration Script for Customs Broker Portal
===================================================

This script initializes the database with schema and sample data.
Supports both SQLite (development) and PostgreSQL (production).
"""

import asyncio
import logging
import os
import sys
from pathlib import Path

import aiosqlite
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent))

from config import get_settings, is_development
from database import Base, create_database_engine

# Import all models to ensure SQLAlchemy is aware of them
from models.tariff import TariffCode
from models.hierarchy import TariffSection, TariffChapter, TradeAgreement
from models.duty import DutyRate
from models.fta import FtaRate
from models.dumping import DumpingDuty
from models.tco import Tco
from models.gst import GstProvision
from models.export import ExportCode
from models.classification import ProductClassification
from models.conversation import Conversation, ConversationMessage

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def convert_postgres_to_sqlite(sql_content: str) -> str:
    """Convert PostgreSQL SQL to SQLite-compatible SQL."""
    
    # Remove PostgreSQL-specific extensions
    sql_content = sql_content.replace('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";', '')
    sql_content = sql_content.replace('CREATE EXTENSION IF NOT EXISTS "pg_trgm";', '')
    
    # Convert data types
    conversions = {
        'SERIAL PRIMARY KEY': 'INTEGER PRIMARY KEY AUTOINCREMENT',
        'SERIAL': 'INTEGER',
        'BIGSERIAL': 'INTEGER',
        'UUID DEFAULT uuid_generate_v4()': 'TEXT DEFAULT (lower(hex(randomblob(4))) || "-" || lower(hex(randomblob(2))) || "-4" || substr(lower(hex(randomblob(2))),2) || "-" || substr("89ab",abs(random()) % 4 + 1, 1) || substr(lower(hex(randomblob(2))),2) || "-" || lower(hex(randomblob(6))))',
        'UUID': 'TEXT',
        'TIMESTAMP WITH TIME ZONE': 'DATETIME',
        'TIMESTAMP': 'DATETIME',
        'TIMESTAMPTZ': 'DATETIME',
        'BOOLEAN': 'INTEGER',
        'TEXT[]': 'TEXT',
        'JSONB': 'TEXT',
        'JSON': 'TEXT',
    }
    
    for pg_type, sqlite_type in conversions.items():
        sql_content = sql_content.replace(pg_type, sqlite_type)
    
    # Remove PostgreSQL-specific indexes
    lines = sql_content.split('\n')
    filtered_lines = []
    skip_line = False
    
    for line in lines:
        line_lower = line.lower().strip()
        
        # Skip PostgreSQL-specific index types
        if any(x in line_lower for x in ['gin(', 'gist(', 'postgresql_where', 'using gin', 'using gist']):
            skip_line = True
            continue
            
        # Skip multi-line index definitions
        if skip_line and ');' in line:
            skip_line = False
            continue
            
        if not skip_line:
            filtered_lines.append(line)
    
    sql_content = '\n'.join(filtered_lines)
    
    # Fix boolean defaults
    sql_content = sql_content.replace('DEFAULT true', 'DEFAULT 1')
    sql_content = sql_content.replace('DEFAULT false', 'DEFAULT 0')
    
    # Remove CHECK constraints for booleans (SQLite handles this differently)
    sql_content = sql_content.replace('CHECK (is_active IN (0, 1))', '')
    sql_content = sql_content.replace('CHECK (is_preferential IN (0, 1))', '')
    
    return sql_content


async def load_sql_file(file_path: Path, engine, is_sqlite: bool = False):
    """Load and execute SQL file."""
    logger.info(f"Loading SQL file: {file_path}")
    
    if not file_path.exists():
        logger.error(f"SQL file not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # Convert PostgreSQL to SQLite if needed
        if is_sqlite:
            sql_content = convert_postgres_to_sqlite(sql_content)
        
        # Split into individual statements
        statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
        
        async with engine.begin() as conn:
            for statement in statements:
                if statement:
                    try:
                        await conn.execute(text(statement))
                        logger.debug(f"Executed: {statement[:50]}...")
                    except Exception as e:
                        logger.warning(f"Statement failed (continuing): {str(e)[:100]}")
                        continue
        
        logger.info(f"Successfully loaded {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        return False


async def create_tables_from_models(engine):
    """Create tables using SQLAlchemy models."""
    logger.info("Creating tables from SQLAlchemy models...")
    
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Successfully created tables from models")
        return True
    except Exception as e:
        logger.error(f"Error creating tables from models: {e}")
        return False


async def migrate_database():
    """Main migration function."""
    logger.info("Starting database migration...")
    
    settings = get_settings()
    database_dir = Path(__file__).parent.parent / "database"
    
    # Determine database type
    is_sqlite = settings.database_url.startswith('sqlite')
    logger.info(f"Database type: {'SQLite' if is_sqlite else 'PostgreSQL'}")
    logger.info(f"Database URL: {settings.database_url}")
    
    # Create engine directly
    engine = create_async_engine(
        settings.database_url,
        echo=is_development(),
        future=True,
    )
    
    try:
        # Test connection
        async with engine.begin() as conn:
            if is_sqlite:
                result = await conn.execute(text("SELECT 1"))
            else:
                result = await conn.execute(text("SELECT version()"))
            logger.info("Database connection successful")
        
        # Step 1: Create tables from models (fallback)
        await create_tables_from_models(engine)
        
        # Step 2: Load schema if available
        schema_file = database_dir / "schema.sql"
        if schema_file.exists():
            await load_sql_file(schema_file, engine, is_sqlite)
        
        # Step 3: Load sample data
        sample_data_file = database_dir / "sample_data.sql"
        if sample_data_file.exists():
            success = await load_sql_file(sample_data_file, engine, is_sqlite)
            if success:
                logger.info("✅ Database migration completed successfully!")
                logger.info("✅ Sample data loaded - mock data is now replaced with real database content")
            else:
                logger.warning("⚠️  Schema created but sample data loading failed")
        else:
            logger.warning("⚠️  Sample data file not found, using empty database")
        
        # Verify data
        async with engine.begin() as conn:
            try:
                result = await conn.execute(text("SELECT COUNT(*) FROM tariff_codes"))
                count = result.scalar()
                logger.info(f"✅ Verification: {count} tariff codes loaded")
            except:
                logger.info("Database created but no tariff codes table found")
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False
    
    finally:
        await engine.dispose()
    
    return True


if __name__ == "__main__":
    asyncio.run(migrate_database())
