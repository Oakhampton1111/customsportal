#!/usr/bin/env python3
"""
Test script to verify EDI endpoints are working correctly.
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_endpoint(method, endpoint, data=None, headers=None):
    """Test an endpoint and return the result."""
    url = f"{BASE_URL}{endpoint}"
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=headers)
        elif method.upper() == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method.upper() == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method.upper() == "DELETE":
            response = requests.delete(url, headers=headers)
        
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": response.status_code,
            "success": response.status_code < 400,
            "response": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        }
    except Exception as e:
        return {
            "endpoint": endpoint,
            "method": method,
            "status_code": None,
            "success": False,
            "error": str(e)
        }

def main():
    """Test all EDI endpoints."""
    print("🧪 Testing EDI Endpoints")
    print("=" * 50)
    
    # Test basic endpoints first
    basic_tests = [
        ("GET", "/"),
        ("GET", "/health"),
        ("GET", "/version"),
    ]
    
    print("\n📋 Basic Endpoints:")
    for method, endpoint in basic_tests:
        result = test_endpoint(method, endpoint)
        status = "✅" if result["success"] else "❌"
        print(f"{status} {method} {endpoint} - Status: {result['status_code']}")
    
    # Test EDI endpoints (these should return 403 without authentication)
    edi_tests = [
        ("GET", "/api/edi/jobs"),
        ("POST", "/api/edi/jobs/register"),
        ("GET", "/api/edi/declarations"),
        ("POST", "/api/edi/declarations"),
        ("GET", "/api/edi/messages"),
        ("POST", "/api/edi/messages/process"),
    ]
    
    print("\n🔐 EDI Endpoints (Authentication Required):")
    for method, endpoint in edi_tests:
        result = test_endpoint(method, endpoint)
        # 403 is expected for protected endpoints without auth
        expected_403 = result["status_code"] == 403
        status = "✅" if expected_403 else "❌"
        print(f"{status} {method} {endpoint} - Status: {result['status_code']} {'(Auth Required - Expected)' if expected_403 else ''}")
    
    # Test OpenAPI documentation
    print("\n📚 API Documentation:")
    openapi_result = test_endpoint("GET", "/openapi.json")
    if openapi_result["success"]:
        openapi_data = openapi_result["response"]
        edi_paths = [path for path in openapi_data.get("paths", {}).keys() if "/api/edi/" in path]
        print(f"✅ OpenAPI JSON - Found {len(edi_paths)} EDI endpoints:")
        for path in sorted(edi_paths):
            print(f"   • {path}")
    else:
        print(f"❌ OpenAPI JSON - Status: {openapi_result['status_code']}")
    
    print("\n🎉 EDI Integration Test Complete!")
    print(f"Timestamp: {datetime.now().isoformat()}")

if __name__ == "__main__":
    main()