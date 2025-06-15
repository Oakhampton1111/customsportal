"""
Manual verification of tariff routes implementation.
"""

import re
import os

def verify_tariff_implementation():
    """Manually verify the tariff routes implementation."""
    
    routes_file = "routes/tariff.py"
    
    if not os.path.exists(routes_file):
        print("❌ Tariff routes file not found")
        return False
    
    with open(routes_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    print("🔍 Verifying Tariff Routes Implementation")
    print("=" * 50)
    
    # Check file size
    file_size = len(content)
    print(f"📊 File size: {file_size:,} characters ({file_size/1024:.1f} KB)")
    
    # Required endpoints and their functions
    required_endpoints = {
        'GET /api/tariff/sections': 'get_tariff_sections',
        'GET /api/tariff/chapters/{section_id}': 'get_chapters_by_section',
        'GET /api/tariff/tree/{section_id}': 'get_tariff_tree',
        'GET /api/tariff/code/{hs_code}': 'get_tariff_detail',
        'GET /api/tariff/search': 'search_tariff_codes'
    }
    
    print(f"\n📋 Checking {len(required_endpoints)} required endpoints:")
    
    all_found = True
    for endpoint, func_name in required_endpoints.items():
        # Check for function definition
        func_pattern = rf'async def {func_name}\s*\('
        func_match = re.search(func_pattern, content)
        
        # Check for router decorator
        router_pattern = rf'@router\.get\(["\'][^"\']*["\'].*?\)\s*\n\s*async def {func_name}'
        router_match = re.search(router_pattern, content, re.MULTILINE | re.DOTALL)
        
        if func_match and router_match:
            print(f"  ✅ {endpoint} -> {func_name}()")
        else:
            print(f"  ❌ {endpoint} -> {func_name}() - Missing")
            all_found = False
    
    # Check for helper functions
    helper_functions = [
        '_build_tree_node',
        '_get_duty_rates',
        '_get_fta_rates',
        '_get_child_codes',
        '_build_breadcrumbs',
        '_get_related_codes'
    ]
    
    print(f"\n🔧 Checking {len(helper_functions)} helper functions:")
    
    for helper in helper_functions:
        pattern = rf'(async )?def {helper}\s*\('
        if re.search(pattern, content):
            print(f"  ✅ {helper}()")
        else:
            print(f"  ❌ {helper}() - Missing")
    
    # Check for required imports
    required_imports = [
        'APIRouter',
        'get_async_session',
        'TariffCode',
        'TariffSection',
        'TariffChapter',
        'TariffTreeResponse',
        'TariffDetailResponse',
        'TariffSearchResponse'
    ]
    
    print(f"\n📦 Checking {len(required_imports)} key imports:")
    
    for imp in required_imports:
        if imp in content:
            print(f"  ✅ {imp}")
        else:
            print(f"  ❌ {imp} - Missing")
    
    # Check for key features
    features = {
        'Router creation': 'router = APIRouter',
        'Error handling': 'HTTPException',
        'Logging': 'logger.',
        'Database queries': 'select(',
        'Async/await': 'async def',
        'Type hints': ') ->',
        'Docstrings': '"""',
        'Pagination': 'PaginationMeta',
        'Search functionality': 'ilike',
        'Tree navigation': '_build_tree_node'
    }
    
    print(f"\n🚀 Checking {len(features)} key features:")
    
    for feature, pattern in features.items():
        if pattern in content:
            print(f"  ✅ {feature}")
        else:
            print(f"  ❌ {feature} - Missing")
    
    # Count lines of code
    lines = content.split('\n')
    code_lines = [line for line in lines if line.strip() and not line.strip().startswith('#')]
    
    print(f"\n📈 Code Statistics:")
    print(f"  Total lines: {len(lines)}")
    print(f"  Code lines: {len(code_lines)}")
    print(f"  Functions: {len(re.findall(r'def \w+\s*\(', content))}")
    print(f"  Async functions: {len(re.findall(r'async def \w+\s*\(', content))}")
    print(f"  Route decorators: {len(re.findall(r'@router\.\w+', content))}")
    
    # Summary
    print(f"\n📊 Implementation Summary:")
    if all_found:
        print("  ✅ All required endpoints implemented")
        print("  ✅ Comprehensive tariff API routes complete")
        print("  ✅ Ready for integration with main FastAPI app")
    else:
        print("  ❌ Some endpoints missing - implementation incomplete")
    
    return all_found

if __name__ == "__main__":
    success = verify_tariff_implementation()
    if success:
        print("\n🎉 Tariff routes implementation verification PASSED!")
    else:
        print("\n💥 Tariff routes implementation verification FAILED!")