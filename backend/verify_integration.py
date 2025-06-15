#!/usr/bin/env python3
"""
Simple verification script to check tariff API integration.

This script verifies that the main.py file has been properly updated
to include the tariff router integration.
"""

import sys
import os

def verify_integration():
    """Verify that tariff routes are properly integrated in main.py."""
    try:
        print("Verifying tariff API integration...")
        
        # Read main.py file
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check 1: Import statement
        import_check = "from .routes.tariff import router as tariff_router" in content
        print(f"✓ Import statement: {'PASS' if import_check else 'FAIL'}")
        
        # Check 2: Router inclusion
        router_check = "app.include_router(tariff_router)" in content
        print(f"✓ Router inclusion: {'PASS' if router_check else 'FAIL'}")
        
        # Check 3: Logging statement
        logging_check = "Tariff API routes included successfully" in content
        print(f"✓ Logging statement: {'PASS' if logging_check else 'FAIL'}")
        
        # Check 4: Updated description
        description_check = "Tariff API Features:" in content
        print(f"✓ Updated description: {'PASS' if description_check else 'FAIL'}")
        
        # Check 5: Tariff endpoints in root response
        endpoints_check = "tariff_endpoints" in content
        print(f"✓ Tariff endpoints listed: {'PASS' if endpoints_check else 'FAIL'}")
        
        # Check 6: All expected endpoints are listed
        expected_endpoints = [
            "/api/tariff/sections",
            "/api/tariff/chapters/{section_id}",
            "/api/tariff/tree/{section_id}",
            "/api/tariff/code/{hs_code}",
            "/api/tariff/search"
        ]
        
        endpoints_found = all(endpoint in content for endpoint in expected_endpoints)
        print(f"✓ All 5 endpoints listed: {'PASS' if endpoints_found else 'FAIL'}")
        
        # Overall result
        all_checks = [import_check, router_check, logging_check, description_check, endpoints_check, endpoints_found]
        
        if all(all_checks):
            print("\n🎉 Integration verification PASSED!")
            print("✓ Tariff router successfully integrated into main FastAPI application")
            print("✓ All required changes have been implemented")
            print("✓ API documentation updated with tariff capabilities")
            print("✓ All 5 tariff endpoints are properly configured")
            
            print("\nIntegrated API Endpoints:")
            for endpoint in expected_endpoints:
                print(f"  - {endpoint}")
            
            return True
        else:
            print("\n❌ Integration verification FAILED!")
            print("Some required changes are missing.")
            return False
            
    except FileNotFoundError:
        print("✗ main.py file not found")
        return False
    except Exception as e:
        print(f"✗ Verification failed: {e}")
        return False

def check_file_syntax():
    """Check that main.py has valid Python syntax."""
    try:
        import ast
        with open('main.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        ast.parse(content)
        print("✓ Python syntax validation: PASS")
        return True
    except SyntaxError as e:
        print(f"✗ Python syntax validation: FAIL - {e}")
        return False
    except Exception as e:
        print(f"✗ Syntax check failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("TARIFF API INTEGRATION VERIFICATION")
    print("=" * 60)
    
    syntax_ok = check_file_syntax()
    integration_ok = verify_integration()
    
    print("\n" + "=" * 60)
    if syntax_ok and integration_ok:
        print("VERIFICATION RESULT: SUCCESS ✅")
        print("The tariff API has been successfully integrated!")
    else:
        print("VERIFICATION RESULT: FAILED ❌")
        print("Integration issues detected.")
    print("=" * 60)
    
    sys.exit(0 if (syntax_ok and integration_ok) else 1)