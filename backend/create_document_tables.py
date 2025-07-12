"""
Create document management tables for the Customs Broker Portal.

This script creates the document management tables including:
- documents: Main document storage table
- document_categories: Category definitions
- document_category_mappings: Document-category relationships
- document_shares: Document sharing and permissions

Run this script to add document management functionality to the database.
"""

import asyncio
import logging
from sqlalchemy import text
from database import init_database, get_db_session, Base, engine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def create_document_tables():
    """Create all document management tables."""
    try:
        logger.info("Starting document tables creation...")
        
        # Initialize database connection
        await init_database()
        
        # Import the engine from database module
        from database import engine
        
        if not engine:
            raise RuntimeError("Database engine not initialized")
        
        # Import models to register them with Base
        from models.documents import (
            Document, 
            DocumentCategoryDefinition, 
            DocumentCategoryMapping, 
            DocumentShare
        )
        
        logger.info("Creating document management tables...")
        
        # Create all tables defined in the models
        async with engine.begin() as conn:
            # Create tables
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Document tables created successfully")
            
            # Verify tables were created
            async with get_db_session() as session:
                # Check if tables exist
                if "postgresql" in str(engine.url):
                    # PostgreSQL query
                    result = await session.execute(text("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name IN ('documents', 'document_categories', 'document_category_mappings', 'document_shares')
                        ORDER BY table_name
                    """))
                else:
                    # SQLite query
                    result = await session.execute(text("""
                        SELECT name 
                        FROM sqlite_master 
                        WHERE type='table' 
                        AND name IN ('documents', 'document_categories', 'document_category_mappings', 'document_shares')
                        ORDER BY name
                    """))
                
                tables = [row[0] for row in result.fetchall()]
                logger.info(f"Created tables: {tables}")
                
                if len(tables) == 4:
                    logger.info("✅ All document tables created successfully!")
                else:
                    logger.warning(f"⚠️ Expected 4 tables, but found {len(tables)}: {tables}")
        
        # Create some default categories
        await create_default_categories()
        
        logger.info("Document management tables setup completed successfully!")
        
    except Exception as e:
        logger.error(f"Failed to create document tables: {e}")
        raise


async def create_default_categories():
    """Create default document categories."""
    try:
        logger.info("Creating default document categories...")
        
        from models.documents import DocumentCategoryDefinition
        
        default_categories = [
            {
                "name": "Import Documents",
                "description": "Documents related to import operations",
                "color": "#2563eb",
                "icon": "import",
                "sort_order": 1
            },
            {
                "name": "Export Documents", 
                "description": "Documents related to export operations",
                "color": "#dc2626",
                "icon": "export",
                "sort_order": 2
            },
            {
                "name": "Compliance Documents",
                "description": "Regulatory and compliance documentation",
                "color": "#059669",
                "icon": "shield-check",
                "sort_order": 3
            },
            {
                "name": "Client Documents",
                "description": "Client-specific documentation",
                "color": "#7c3aed",
                "icon": "users",
                "sort_order": 4
            },
            {
                "name": "Regulatory Documents",
                "description": "Government and regulatory documentation",
                "color": "#ea580c",
                "icon": "document-text",
                "sort_order": 5
            }
        ]
        
        async with get_db_session() as session:
            for cat_data in default_categories:
                # Check if category already exists
                result = await session.execute(
                    text("SELECT id FROM document_categories WHERE name = :name"),
                    {"name": cat_data["name"]}
                )
                
                if not result.fetchone():
                    # Create new category
                    category = DocumentCategoryDefinition(**cat_data)
                    session.add(category)
                    logger.info(f"Created category: {cat_data['name']}")
                else:
                    logger.info(f"Category already exists: {cat_data['name']}")
            
            await session.commit()
            logger.info("Default categories created successfully!")
            
    except Exception as e:
        logger.error(f"Failed to create default categories: {e}")
        # Don't raise - categories are optional


async def verify_document_tables():
    """Verify that document tables are working correctly."""
    try:
        logger.info("Verifying document tables...")
        
        async with get_db_session() as session:
            # Test basic queries on each table
            tables_to_test = [
                ("documents", "SELECT COUNT(*) FROM documents"),
                ("document_categories", "SELECT COUNT(*) FROM document_categories"),
                ("document_category_mappings", "SELECT COUNT(*) FROM document_category_mappings"),
                ("document_shares", "SELECT COUNT(*) FROM document_shares")
            ]
            
            for table_name, query in tables_to_test:
                try:
                    result = await session.execute(text(query))
                    count = result.scalar()
                    logger.info(f"✅ {table_name}: {count} records")
                except Exception as e:
                    logger.error(f"❌ {table_name}: {e}")
                    raise
            
            logger.info("All document tables verified successfully!")
            
    except Exception as e:
        logger.error(f"Table verification failed: {e}")
        raise


async def main():
    """Main function to create document tables."""
    try:
        await create_document_tables()
        await verify_document_tables()
        logger.info("🎉 Document management system setup completed!")
        
    except Exception as e:
        logger.error(f"Setup failed: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)