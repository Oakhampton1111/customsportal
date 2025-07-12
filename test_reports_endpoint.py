import requests
import sys

try:
    # Test the reports list endpoint
    response = requests.get('http://127.0.0.1:8000/api/reports/', 
                          headers={'Origin': 'http://localhost:5173'})
    print(f'Status Code: {response.status_code}')
    print(f'Headers: {dict(response.headers)}')
    if response.status_code == 200:
        print('✅ Reports endpoint working!')
        data = response.json()
        print(f'Response keys: {list(data.keys()) if isinstance(data, dict) else "Not a dict"}')
    else:
        print(f'❌ Error: {response.text}')
except Exception as e:
    print(f'❌ Request failed: {e}')