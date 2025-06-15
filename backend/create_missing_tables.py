import asyncio
import sys
import os

# Add the backend directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import create_database_engine, Base

async def create_missing_tables():
    """Create only the missing tables."""
    try:
        # Import the specific missing models
        from models.export import ExportCode
        from models.classification import ProductClassification
        
        print("Successfully imported missing models")
        print(f"ExportCode table name: {ExportCode.__tablename__}")
        print(f"ProductClassification table name: {ProductClassification.__tablename__}")
        
        # Get the async engine
        engine = await create_database_engine()
        
        # Create only these specific tables
        async with engine.begin() as conn:
            # Create tables for these specific models
            await conn.run_sync(ExportCode.metadata.create_all)
            await conn.run_sync(ProductClassification.metadata.create_all)
            
        print("Missing tables created successfully!")
        
        # Verify tables were created
        async with engine.begin() as conn:
            result = await conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('export_codes', 'product_classifications')")
            tables = result.fetchall()
            print(f"Verified tables: {[table[0] for table in tables]}")
            
    except Exception as e:
        print(f"Error creating missing tables: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(create_missing_tables())
