import asyncio
import sys
import traceback
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from database import get_async_session, init_database
from models.hierarchy import TariffSection, TariffChapter

async def test_tariff_sections_query():
    """Test the exact query that's failing in the API."""
    try:
        # Initialize database
        await init_database()
        
        # Get database session
        async for db in get_async_session():
            print("Database session created successfully")
            
            # Test the exact query from the API
            print("Testing the tariff sections query...")
            stmt = (
                select(
                    TariffSection,
                    func.count(TariffChapter.id).label("chapter_count")
                )
                .outerjoin(TariffChapter)
                .group_by(TariffSection.id)
                .order_by(TariffSection.section_number)
            )
            
            print("Query statement created, executing...")
            result = await db.execute(stmt)
            sections_with_counts = result.all()
            
            print(f"Query executed successfully! Found {len(sections_with_counts)} sections")
            
            # Process results
            for i, (section, chapter_count) in enumerate(sections_with_counts[:3]):
                print(f"Section {i+1}: {section.section_number} - {section.title} ({chapter_count} chapters)")
            
            break
            
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tariff_sections_query())
