"""
Simple test script to verify document categories endpoint works
"""
import asyncio
from sqlalchemy import select
from database import init_database, get_async_session
from models.documents import DocumentCategoryDefinition

async def test_categories():
    """Test the categories query directly"""
    # Initialize database first
    await init_database()
    
    async for session in get_async_session():
        try:
            # Test basic select
            query = select(DocumentCategoryDefinition)
            query = query.where(DocumentCategoryDefinition.is_active == True)
            query = query.order_by(DocumentCategoryDefinition.sort_order, DocumentCategoryDefinition.name)
            
            result = await session.execute(query)
            categories = result.scalars().all()
            
            print(f"Found {len(categories)} categories:")
            for cat in categories:
                print(f"  - {cat.name}: {cat.description}")
                
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(test_categories())