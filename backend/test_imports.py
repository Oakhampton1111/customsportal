#!/usr/bin/env python3
"""
Simple import test for the models package.
"""

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing basic imports...")
    
    # Test individual model imports
    from models.export import ExportCode
    print("✓ ExportCode imported successfully")
    
    from models.classification import ProductClassification
    print("✓ ProductClassification imported successfully")
    
    from models.tariff import TariffCode
    print("✓ TariffCode imported successfully")
    
    # Test package import
    from models import ExportCode as EC, ProductClassification as PC, TariffCode as TC
    print("✓ Package imports successful")
    
    # Test __all__ availability
    from models import __all__
    print(f"✓ __all__ contains: {__all__}")
    
    print("\n🎉 All imports successful!")
    
except Exception as e:
    print(f"❌ Import failed: {e}")
    import traceback
    traceback.print_exc()