"""
Validation script for tariff routes implementation.

This script validates the tariff routes structure and implementation
without importing the models that have relative import issues.
"""

import ast
import os
from typing import List, Dict, Any

def analyze_tariff_routes() -> Dict[str, Any]:
    """Analyze the tariff routes file for completeness and correctness."""
    
    routes_file = "routes/tariff.py"
    
    if not os.path.exists(routes_file):
        return {"error": "Tariff routes file not found"}
    
    with open(routes_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    try:
        tree = ast.parse(content)
    except SyntaxError as e:
        return {"error": f"Syntax error in tariff routes: {e}"}
    
    analysis = {
        "file_exists": True,
        "syntax_valid": True,
        "imports": [],
        "functions": [],
        "routes": [],
        "classes": [],
        "required_endpoints": [
            "/api/tariff/tree/{section_id}",
            "/api/tariff/code/{hs_code}",
            "/api/tariff/search",
            "/api/tariff/sections",
            "/api/tariff/chapters/{section_id}"
        ],
        "implemented_endpoints": []
    }
    
    # Analyze AST nodes
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                analysis["imports"].append(alias.name)
        
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                analysis["imports"].append(f"{module}.{alias.name}")
        
        elif isinstance(node, ast.FunctionDef):
            analysis["functions"].append(node.name)
            
            # Check for route decorators
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Attribute):
                    if (isinstance(decorator.value, ast.Name) and 
                        decorator.value.id == "router"):
                        
                        method = decorator.attr
                        # Try to extract path from decorator arguments
                        if decorator.parent and hasattr(decorator.parent, 'args'):
                            for arg in decorator.parent.args:
                                if isinstance(arg, ast.Constant):
                                    path = arg.value
                                    endpoint = f"{method.upper()} {path}"
                                    analysis["routes"].append(endpoint)
                                    analysis["implemented_endpoints"].append(path)
        
        elif isinstance(node, ast.ClassDef):
            analysis["classes"].append(node.name)
    
    # Check for required imports
    required_imports = [
        "fastapi.APIRouter",
        "database.get_async_session",
        "models.tariff.TariffCode",
        "schemas.tariff"
    ]
    
    analysis["missing_imports"] = []
    for req_import in required_imports:
        found = any(req_import in imp for imp in analysis["imports"])
        if not found:
            analysis["missing_imports"].append(req_import)
    
    # Check endpoint coverage
    analysis["missing_endpoints"] = []
    for req_endpoint in analysis["required_endpoints"]:
        # Extract path pattern from required endpoint
        path_pattern = req_endpoint.split(" ")[-1] if " " in req_endpoint else req_endpoint
        found = any(path_pattern.replace("{", "").replace("}", "") in impl 
                   for impl in analysis["implemented_endpoints"])
        if not found:
            analysis["missing_endpoints"].append(req_endpoint)
    
    return analysis

def validate_route_functions() -> Dict[str, Any]:
    """Validate that all required route functions are implemented."""
    
    required_functions = [
        "get_tariff_sections",
        "get_chapters_by_section", 
        "get_tariff_tree",
        "get_tariff_detail",
        "search_tariff_codes"
    ]
    
    routes_file = "routes/tariff.py"
    
    if not os.path.exists(routes_file):
        return {"error": "Tariff routes file not found"}
    
    with open(routes_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    validation = {
        "required_functions": required_functions,
        "implemented_functions": [],
        "missing_functions": [],
        "function_details": {}
    }
    
    try:
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                func_name = node.name
                validation["implemented_functions"].append(func_name)
                
                # Analyze function details
                validation["function_details"][func_name] = {
                    "args": [arg.arg for arg in node.args.args],
                    "decorators": len(node.decorator_list),
                    "docstring": ast.get_docstring(node) is not None,
                    "lines": node.end_lineno - node.lineno if hasattr(node, 'end_lineno') else 0
                }
        
        # Check for missing functions
        for req_func in required_functions:
            if req_func not in validation["implemented_functions"]:
                validation["missing_functions"].append(req_func)
        
    except Exception as e:
        validation["error"] = str(e)
    
    return validation

def check_file_structure() -> Dict[str, Any]:
    """Check that the routes file structure is correct."""
    
    structure = {
        "routes_dir_exists": os.path.exists("routes"),
        "routes_init_exists": os.path.exists("routes/__init__.py"),
        "tariff_routes_exists": os.path.exists("routes/tariff.py"),
        "file_sizes": {}
    }
    
    if structure["routes_init_exists"]:
        structure["file_sizes"]["__init__.py"] = os.path.getsize("routes/__init__.py")
    
    if structure["tariff_routes_exists"]:
        structure["file_sizes"]["tariff.py"] = os.path.getsize("routes/tariff.py")
    
    return structure

def main():
    """Run all validations and print results."""
    
    print("🔍 Validating Tariff Routes Implementation")
    print("=" * 50)
    
    # Check file structure
    print("\n📁 File Structure:")
    structure = check_file_structure()
    for key, value in structure.items():
        if key != "file_sizes":
            status = "✓" if value else "✗"
            print(f"  {status} {key}: {value}")
    
    if structure["file_sizes"]:
        print("  📊 File sizes:")
        for file, size in structure["file_sizes"].items():
            print(f"    {file}: {size:,} bytes")
    
    # Analyze routes
    print("\n🔍 Route Analysis:")
    analysis = analyze_tariff_routes()
    
    if "error" in analysis:
        print(f"  ✗ Error: {analysis['error']}")
        return
    
    print(f"  ✓ Syntax valid: {analysis['syntax_valid']}")
    print(f"  ✓ Imports found: {len(analysis['imports'])}")
    print(f"  ✓ Functions found: {len(analysis['functions'])}")
    print(f"  ✓ Routes found: {len(analysis['routes'])}")
    
    if analysis["missing_imports"]:
        print(f"  ⚠️  Missing imports: {analysis['missing_imports']}")
    
    if analysis["missing_endpoints"]:
        print(f"  ⚠️  Missing endpoints: {analysis['missing_endpoints']}")
    else:
        print("  ✓ All required endpoints implemented")
    
    # Validate functions
    print("\n🔧 Function Validation:")
    validation = validate_route_functions()
    
    if "error" in validation:
        print(f"  ✗ Error: {validation['error']}")
        return
    
    print(f"  ✓ Required functions: {len(validation['required_functions'])}")
    print(f"  ✓ Implemented functions: {len(validation['implemented_functions'])}")
    
    if validation["missing_functions"]:
        print(f"  ✗ Missing functions: {validation['missing_functions']}")
    else:
        print("  ✓ All required functions implemented")
    
    # Function details
    print("\n📋 Function Details:")
    for func_name, details in validation["function_details"].items():
        if func_name in validation["required_functions"]:
            doc_status = "✓" if details["docstring"] else "✗"
            print(f"  {func_name}:")
            print(f"    Args: {len(details['args'])}")
            print(f"    Decorators: {details['decorators']}")
            print(f"    Docstring: {doc_status}")
            print(f"    Lines: {details['lines']}")
    
    # Summary
    print("\n📊 Summary:")
    total_issues = len(analysis.get("missing_imports", [])) + len(analysis.get("missing_endpoints", [])) + len(validation.get("missing_functions", []))
    
    if total_issues == 0:
        print("  ✅ Tariff routes implementation is complete!")
    else:
        print(f"  ⚠️  Found {total_issues} issues that need attention")
    
    print(f"  📈 Implementation coverage: {len(validation['implemented_functions'])}/{len(validation['required_functions'])} functions")
    print(f"  🛣️  Route coverage: {len(analysis['implemented_endpoints'])}/{len(analysis['required_endpoints'])} endpoints")

if __name__ == "__main__":
    main()