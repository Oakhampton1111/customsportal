"""
Test script to validate tariff routes implementation.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

def test_tariff_routes_import():
    """Test that tariff routes can be imported correctly."""
    try:
        # Test individual components first
        print("Testing database import...")
        from database import get_async_session
        print("✓ Database import successful")
        
        print("Testing models import...")
        from models.tariff import TariffCode
        from models.hierarchy import TariffSection, TariffChapter
        print("✓ Models import successful")
        
        print("Testing schemas import...")
        from schemas.tariff import TariffTreeResponse, TariffDetailResponse
        from schemas.common import PaginationMeta
        print("✓ Schemas import successful")
        
        print("Testing tariff routes import...")
        from routes.tariff import router
        print("✓ Tariff routes import successful")
        
        # Test router configuration
        print(f"Router prefix: {router.prefix}")
        print(f"Router tags: {router.tags}")
        print(f"Number of routes: {len(router.routes)}")
        
        # List all routes
        print("\nImplemented routes:")
        for route in router.routes:
            print(f"  {route.methods} {route.path}")
        
        return True
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_tariff_routes_import()
    if success:
        print("\n✓ All tariff routes tests passed!")
    else:
        print("\n✗ Tariff routes tests failed!")
        sys.exit(1)