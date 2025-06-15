#!/usr/bin/env python3
"""
Quick database verification script
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.append(str(Path(__file__).parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from config import get_settings

async def verify_database():
    """Verify database content."""
    settings = get_settings()
    engine = create_async_engine(settings.database_url, echo=False)
    
    try:
        async with engine.begin() as conn:
            # Check tables
            tables_query = """
            SELECT name FROM sqlite_master 
            WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ORDER BY name
            """
            result = await conn.execute(text(tables_query))
            tables = [row[0] for row in result.fetchall()]
            print(f"Tables created: {len(tables)}")
            for table in tables:
                print(f"  - {table}")
            
            print("\n" + "="*50)
            
            # Check data counts
            data_tables = ['tariff_codes', 'duty_rates', 'fta_rates', 'export_codes']
            for table in data_tables:
                if table in tables:
                    result = await conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                    count = result.scalar()
                    print(f"{table}: {count} records")
            
            print("\n" + "="*50)
            
            # Sample tariff codes
            if 'tariff_codes' in tables:
                result = await conn.execute(text("""
                    SELECT hs_code, description, level 
                    FROM tariff_codes 
                    ORDER BY hs_code 
                    LIMIT 10
                """))
                print("Sample Tariff Codes:")
                for row in result.fetchall():
                    print(f"  {row[0]} - {row[1][:50]}... (Level {row[2]})")
                    
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(verify_database())
