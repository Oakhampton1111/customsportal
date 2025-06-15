"""
API Endpoint Verification for Customs Broker Portal
==================================================
Comprehensive verification of all API endpoints with statistical codes support
"""

import asyncio
import aiohttp
import json
from datetime import datetime
from typing import Dict, List, Any

# Base URL for the API
BASE_URL = "http://localhost:8000"

class APIVerifier:
    """API endpoint verification utility."""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.results = []
        
    async def verify_endpoint(self, session: aiohttp.ClientSession, method: str, 
                            endpoint: str, expected_status: int = 200, 
                            params: Dict = None, data: Dict = None) -> Dict[str, Any]:
        """Verify a single API endpoint."""
        url = f"{self.base_url}{endpoint}"
        
        try:
            if method.upper() == "GET":
                async with session.get(url, params=params) as response:
                    status = response.status
                    content = await response.text()
                    
            elif method.upper() == "POST":
                async with session.post(url, json=data, params=params) as response:
                    status = response.status
                    content = await response.text()
                    
            # Try to parse JSON response
            try:
                json_content = json.loads(content)
            except:
                json_content = None
                
            result = {
                "endpoint": endpoint,
                "method": method.upper(),
                "status": status,
                "expected_status": expected_status,
                "success": status == expected_status,
                "response_size": len(content),
                "has_json": json_content is not None,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add sample data for successful responses
            if status == expected_status and json_content:
                if isinstance(json_content, list) and len(json_content) > 0:
                    result["sample_count"] = len(json_content)
                    result["sample_item"] = json_content[0] if json_content else None
                elif isinstance(json_content, dict):
                    result["response_keys"] = list(json_content.keys())
                    
            return result
            
        except Exception as e:
            return {
                "endpoint": endpoint,
                "method": method.upper(),
                "status": 0,
                "expected_status": expected_status,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def verify_all_endpoints(self):
        """Verify all API endpoints."""
        print("🔍 CUSTOMS BROKER PORTAL API VERIFICATION")
        print("=" * 50)
        
        async with aiohttp.ClientSession() as session:
            # Core system endpoints
            print("\n📋 CORE SYSTEM ENDPOINTS:")
            endpoints = [
                ("GET", "/", 200),
                ("GET", "/health", 200),
                ("GET", "/version", 200),
            ]
            
            for method, endpoint, expected_status in endpoints:
                result = await self.verify_endpoint(session, method, endpoint, expected_status)
                self.results.append(result)
                status_icon = "✅" if result["success"] else "❌"
                print(f"  {status_icon} {method} {endpoint} - {result['status']}")
            
            # Tariff hierarchy endpoints
            print("\n📊 TARIFF HIERARCHY ENDPOINTS:")
            tariff_endpoints = [
                ("GET", "/api/tariff/sections", 200),
                ("GET", "/api/tariff/chapters/1", 200),  # Section 1
                ("GET", "/api/tariff/tree", 200),
                ("GET", "/api/tariff/0101211010", 200),  # Statistical code
                ("GET", "/api/tariff/01012110", 200),    # 8-digit code
                ("GET", "/api/tariff/010121", 200),      # 6-digit code
                ("GET", "/api/tariff/0101", 200),        # 4-digit code
                ("GET", "/api/tariff/01", 200),          # 2-digit code
            ]
            
            for method, endpoint, expected_status in tariff_endpoints:
                result = await self.verify_endpoint(session, method, endpoint, expected_status)
                self.results.append(result)
                status_icon = "✅" if result["success"] else "❌"
                print(f"  {status_icon} {method} {endpoint} - {result['status']}")
                
                # Show sample data for successful responses
                if result["success"] and "sample_count" in result:
                    print(f"    📦 {result['sample_count']} items returned")
            
            # Search endpoints
            print("\n🔍 SEARCH ENDPOINTS:")
            search_endpoints = [
                ("GET", "/api/search/tariff", 200, {"q": "horse"}),
                ("GET", "/api/search/tariff", 200, {"q": "0101", "level": "8"}),
                ("GET", "/api/search/tariff", 200, {"q": "breeding", "section": "1"}),
            ]
            
            for method, endpoint, expected_status, params in search_endpoints:
                result = await self.verify_endpoint(session, method, endpoint, expected_status, params=params)
                self.results.append(result)
                status_icon = "✅" if result["success"] else "❌"
                query_str = "&".join([f"{k}={v}" for k, v in params.items()])
                print(f"  {status_icon} {method} {endpoint}?{query_str} - {result['status']}")
            
            # Export endpoints
            print("\n📤 EXPORT ENDPOINTS:")
            export_endpoints = [
                ("GET", "/api/export/ahecc-tree", 200),
                ("GET", "/api/export/search", 200, {"query": "horse"}),
                ("GET", "/api/export/0101211010", 200),  # Statistical export code
                ("GET", "/api/export/requirements/0101211010/china", 200),
                ("GET", "/api/export/market-access/china", 200),
            ]
            
            for item in export_endpoints:
                if len(item) == 3:
                    method, endpoint, expected_status = item
                    params = None
                else:
                    method, endpoint, expected_status, params = item
                    
                result = await self.verify_endpoint(session, method, endpoint, expected_status, params=params)
                self.results.append(result)
                status_icon = "✅" if result["success"] else "❌"
                
                if params:
                    query_str = "&".join([f"{k}={v}" for k, v in params.items()])
                    print(f"  {status_icon} {method} {endpoint}?{query_str} - {result['status']}")
                else:
                    print(f"  {status_icon} {method} {endpoint} - {result['status']}")
            
            # Duty calculator endpoints
            print("\n💰 DUTY CALCULATOR ENDPOINTS:")
            duty_endpoints = [
                ("GET", "/api/duty/calculate/0101211010", 200, {"value": "10000", "origin": "NZ"}),
                ("GET", "/api/duty/rates/0101211010", 200),
                ("GET", "/api/duty/fta-rates/0101211010/NZ", 200),
                ("GET", "/api/duty/tco-check/0101211010", 200),
            ]
            
            for method, endpoint, expected_status, params in duty_endpoints:
                result = await self.verify_endpoint(session, method, endpoint, expected_status, params=params)
                self.results.append(result)
                status_icon = "✅" if result["success"] else "❌"
                
                if params:
                    query_str = "&".join([f"{k}={v}" for k, v in params.items()])
                    print(f"  {status_icon} {method} {endpoint}?{query_str} - {result['status']}")
                else:
                    print(f"  {status_icon} {method} {endpoint} - {result['status']}")
            
            # News and analytics endpoints
            print("\n📰 NEWS & ANALYTICS ENDPOINTS:")
            news_endpoints = [
                ("GET", "/api/news/latest", 200),
                ("GET", "/api/news/analytics", 200),
                ("GET", "/api/news/alerts", 200),
            ]
            
            for method, endpoint, expected_status in news_endpoints:
                result = await self.verify_endpoint(session, method, endpoint, expected_status)
                self.results.append(result)
                status_icon = "✅" if result["success"] else "❌"
                print(f"  {status_icon} {method} {endpoint} - {result['status']}")
            
            # Rulings endpoints
            print("\n⚖️ RULINGS ENDPOINTS:")
            rulings_endpoints = [
                ("GET", "/api/rulings/search", 200, {"query": "classification"}),
                ("GET", "/api/rulings/statistics", 200),
                ("GET", "/api/rulings/recent", 200),
            ]
            
            for method, endpoint, expected_status, params in rulings_endpoints:
                result = await self.verify_endpoint(session, method, endpoint, expected_status, params=params)
                self.results.append(result)
                status_icon = "✅" if result["success"] else "❌"
                
                if params:
                    query_str = "&".join([f"{k}={v}" for k, v in params.items()])
                    print(f"  {status_icon} {method} {endpoint}?{query_str} - {result['status']}")
                else:
                    print(f"  {status_icon} {method} {endpoint} - {result['status']}")
            
            # AI endpoints
            print("\n🤖 AI ENDPOINTS:")
            ai_endpoints = [
                ("POST", "/api/ai/classify", 200, {"description": "Pure-bred racing horse"}),
                ("POST", "/api/ai/chat", 200, {"message": "What is the tariff code for horses?"}),
            ]
            
            for method, endpoint, expected_status, data in ai_endpoints:
                result = await self.verify_endpoint(session, method, endpoint, expected_status, data=data)
                self.results.append(result)
                status_icon = "✅" if result["success"] else "❌"
                print(f"  {status_icon} {method} {endpoint} - {result['status']}")
    
    def generate_report(self):
        """Generate comprehensive verification report."""
        print("\n" + "=" * 60)
        print("📊 API VERIFICATION SUMMARY REPORT")
        print("=" * 60)
        
        total_endpoints = len(self.results)
        successful = sum(1 for r in self.results if r["success"])
        failed = total_endpoints - successful
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"  Total Endpoints Tested: {total_endpoints}")
        print(f"  ✅ Successful: {successful}")
        print(f"  ❌ Failed: {failed}")
        print(f"  📈 Success Rate: {(successful/total_endpoints)*100:.1f}%")
        
        if failed > 0:
            print(f"\n❌ FAILED ENDPOINTS:")
            for result in self.results:
                if not result["success"]:
                    print(f"  {result['method']} {result['endpoint']} - Status: {result['status']}")
                    if "error" in result:
                        print(f"    Error: {result['error']}")
        
        print(f"\n🔍 STATISTICAL CODES VERIFICATION:")
        statistical_tests = [r for r in self.results if "0101211010" in r["endpoint"]]
        stat_success = sum(1 for r in statistical_tests if r["success"])
        print(f"  Statistical Code Tests: {stat_success}/{len(statistical_tests)} passed")
        
        print(f"\n📤 EXPORT CODES VERIFICATION:")
        export_tests = [r for r in self.results if "/api/export/" in r["endpoint"]]
        export_success = sum(1 for r in export_tests if r["success"])
        print(f"  Export Code Tests: {export_success}/{len(export_tests)} passed")
        
        print(f"\n💰 DUTY CALCULATION VERIFICATION:")
        duty_tests = [r for r in self.results if "/api/duty/" in r["endpoint"]]
        duty_success = sum(1 for r in duty_tests if r["success"])
        print(f"  Duty Calculator Tests: {duty_success}/{len(duty_tests)} passed")
        
        if successful == total_endpoints:
            print(f"\n🎉 ALL ENDPOINTS OPERATIONAL!")
            print(f"🚀 FRONTEND-BACKEND INTEGRATION READY")
            print(f"✅ STATISTICAL CODES FULLY SUPPORTED")
            print(f"✅ EXPORT CODES FULLY SUPPORTED")
            print(f"✅ COMPREHENSIVE API COVERAGE")
        else:
            print(f"\n⚠️ Some endpoints need attention before production deployment")
        
        print(f"\n📅 Verification completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

async def main():
    """Main verification function."""
    print("Starting Customs Broker Portal API verification...")
    print("Ensure the backend server is running on http://localhost:8000")
    print()
    
    verifier = APIVerifier()
    await verifier.verify_all_endpoints()
    verifier.generate_report()

if __name__ == "__main__":
    asyncio.run(main())
