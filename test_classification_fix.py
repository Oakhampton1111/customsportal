import requests

print('🎯 Testing Fixed Classification Endpoint\n')

headers = {'Origin': 'http://localhost:5173'}

# Test the classification endpoint on port 8001 (the working server)
try:
    response = requests.get('http://127.0.0.1:8001/api/tariff/classification/8471', headers=headers, timeout=10)
    status = '✅' if response.status_code == 200 else '❌'
    print(f'{status} Tariff Classification: Status {response.status_code}')
    if response.status_code == 200:
        data = response.json()
        if isinstance(data, dict):
            print(f'   Keys: {list(data.keys())[:5]}')
            if 'tariff' in data:
                print(f'   Tariff HS Code: {data["tariff"].get("hs_code", "N/A")}')
                print(f'   Tariff Description: {data["tariff"].get("description", "N/A")[:50]}...')
        print('✅ Classification endpoint now working!')
    else:
        print(f'   Error: {response.text[:100]}')
except requests.exceptions.Timeout:
    print('⏰ Classification: Timeout')
except Exception as e:
    print(f'❌ Classification: Error - {str(e)[:50]}')

print('\n🎉 Classification Endpoint Test Complete!')