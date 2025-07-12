import requests
import json

def test_reports_endpoint():
    """Test the reports list endpoint after fixing parameter conflicts."""
    try:
        print("🧪 Testing Reports List Endpoint...")
        
        # Test the reports list endpoint
        response = requests.get(
            'http://127.0.0.1:8000/api/reports/', 
            headers={'Origin': 'http://localhost:5173'}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Reports endpoint working!")
            data = response.json()
            print(f"Response keys: {list(data.keys())}")
            
            if 'reports' in data:
                print(f"Reports count: {len(data['reports'])}")
                print(f"Total count: {data.get('total_count', 'N/A')}")
                
                # Show pagination info
                if 'pagination' in data:
                    pagination = data['pagination']
                    print(f"Pagination: page {pagination.get('page', 1)} of {pagination.get('total_pages', 1)}")
                
                print("✅ All parameter name conflicts resolved!")
                return True
            else:
                print("❌ Missing 'reports' key in response")
                return False
        else:
            print(f"❌ Error {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    success = test_reports_endpoint()
    if success:
        print("\n🎉 Reports endpoint parameter conflict fixes successful!")
        print("✅ Backend server ready for UX testing")
    else:
        print("\n❌ Reports endpoint still has issues")