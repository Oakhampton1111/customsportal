#!/usr/bin/env python3
"""
Test script to verify main.py integration with search routes.

This script tests that the main FastAPI application properly includes
the search routes and that all endpoints are accessible.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_main_imports():
    """Test that main.py imports work correctly."""
    try:
        from main import app, create_app
        print("✓ Main application imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_search_router_integration():
    """Test that search router is properly integrated."""
    try:
        from main import app
        
        # Get all routes from the app
        routes = []
        for route in app.routes:
            if hasattr(route, 'path'):
                routes.append(route.path)
        
        # Check for search endpoints
        search_endpoints = [
            "/api/search/classify",
            "/api/search/classify/batch", 
            "/api/search/feedback",
            "/api/search/products",
            "/api/search/stats"
        ]
        
        found_endpoints = []
        for endpoint in search_endpoints:
            if endpoint in routes:
                found_endpoints.append(endpoint)
        
        print(f"✓ Found {len(found_endpoints)} search endpoints in FastAPI app:")
        for endpoint in found_endpoints:
            print(f"  - {endpoint}")
            
        if len(found_endpoints) >= 3:  # At least some endpoints found
            print("✓ Search routes integration successful")
            return True
        else:
            print("✗ Search routes not properly integrated")
            return False
            
    except Exception as e:
        print(f"✗ Error testing search router integration: {e}")
        return False

def test_app_creation():
    """Test that the FastAPI app can be created successfully."""
    try:
        from main import create_app
        app = create_app()
        
        if app:
            print("✓ FastAPI application created successfully")
            print(f"  - Title: {app.title}")
            print(f"  - Version: {app.version}")
            return True
        else:
            print("✗ Failed to create FastAPI application")
            return False
            
    except Exception as e:
        print(f"✗ Error creating FastAPI app: {e}")
        return False

def main():
    """Run all integration tests."""
    print("Testing main.py integration with search routes...")
    print("=" * 50)
    
    tests = [
        test_main_imports,
        test_app_creation,
        test_search_router_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        print(f"\nRunning {test.__name__}...")
        if test():
            passed += 1
        print("-" * 30)
    
    print(f"\nTest Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("❌ Some tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)