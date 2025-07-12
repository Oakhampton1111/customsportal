import asyncio
import aiohttp
import json

async def test_loa_endpoints():
    """Test LOA endpoints after fixing Pydantic serialization issues."""
    
    base_url = "http://localhost:8000"
    
    # Test data for authentication
    auth_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    # Test data for LOA creation
    loa_data = {
        "company_name": "Test Company Pty Ltd",
        "company_abn": "12345678901",
        "company_address": "123 Test Street, Sydney NSW 2000",
        "authorized_person_name": "John Smith",
        "authorized_person_title": "Managing Director",
        "authorized_person_email": "john.smith@testcompany.com.au",
        "authorized_person_phone": "+61 2 1234 5678",
        "authority_scope": "Full customs clearance authority for all imports and exports",
        "customs_broker_license": "CB12345"
    }
    
    async with aiohttp.ClientSession() as session:
        print("🔐 Testing Authentication...")
        
        # Test login
        async with session.post(f"{base_url}/api/customer/auth/login", json=auth_data) as response:
            if response.status == 200:
                auth_response = await response.json()
                token = auth_response.get("access_token")
                print(f"✅ Authentication successful - Token: {token[:20]}...")
                
                headers = {"Authorization": f"Bearer {token}"}
                
                print("\n📄 Testing LOA Creation...")
                
                # Test LOA creation
                async with session.post(f"{base_url}/api/loa/create", json=loa_data, headers=headers) as loa_response:
                    print(f"LOA Creation Status: {loa_response.status}")
                    
                    if loa_response.status == 200:
                        loa_result = await loa_response.json()
                        print("✅ LOA created successfully!")
                        print(f"LOA Number: {loa_result.get('loa_number')}")
                        print(f"Status: {loa_result.get('status')}")
                        print(f"Company: {loa_result.get('company_name')}")
                        
                        loa_id = loa_result.get('id')
                        
                        print("\n📋 Testing LOA List...")
                        
                        # Test LOA list
                        async with session.get(f"{base_url}/api/loa/list", headers=headers) as list_response:
                            print(f"LOA List Status: {list_response.status}")
                            
                            if list_response.status == 200:
                                list_result = await list_response.json()
                                print("✅ LOA list retrieved successfully!")
                                print(f"Total LOAs: {list_result.get('total', 0)}")
                                print(f"Items in page: {len(list_result.get('items', []))}")
                            else:
                                error_text = await list_response.text()
                                print(f"❌ LOA list failed: {error_text}")
                        
                        print("\n🔍 Testing LOA Details...")
                        
                        # Test LOA details
                        async with session.get(f"{base_url}/api/loa/{loa_id}", headers=headers) as detail_response:
                            print(f"LOA Details Status: {detail_response.status}")
                            
                            if detail_response.status == 200:
                                detail_result = await detail_response.json()
                                print("✅ LOA details retrieved successfully!")
                                print(f"LOA Number: {detail_result.get('loa_number')}")
                                print(f"Status: {detail_result.get('status')}")
                                print(f"Created: {detail_result.get('created_at')}")
                            else:
                                error_text = await detail_response.text()
                                print(f"❌ LOA details failed: {error_text}")
                        
                        print("\n📊 Testing LOA Statistics...")
                        
                        # Test LOA statistics
                        async with session.get(f"{base_url}/api/loa/stats/summary", headers=headers) as stats_response:
                            print(f"LOA Stats Status: {stats_response.status}")
                            
                            if stats_response.status == 200:
                                stats_result = await stats_response.json()
                                print("✅ LOA statistics retrieved successfully!")
                                print(f"Total LOAs: {stats_result.get('total_loas')}")
                                print(f"Draft: {stats_result.get('draft_count')}")
                                print(f"Signed: {stats_result.get('signed_count')}")
                            else:
                                error_text = await stats_response.text()
                                print(f"❌ LOA statistics failed: {error_text}")
                        
                        print("\n📝 Testing LOA Templates...")
                        
                        # Test LOA templates
                        async with session.get(f"{base_url}/api/loa/templates", headers=headers) as template_response:
                            print(f"LOA Templates Status: {template_response.status}")
                            
                            if template_response.status == 200:
                                template_result = await template_response.json()
                                print("✅ LOA templates retrieved successfully!")
                                print(f"Available templates: {len(template_result)}")
                                if template_result:
                                    print(f"Default template: {template_result[0].get('template_name')}")
                            else:
                                error_text = await template_response.text()
                                print(f"❌ LOA templates failed: {error_text}")
                        
                    else:
                        error_text = await loa_response.text()
                        print(f"❌ LOA creation failed: {error_text}")
                
            else:
                error_text = await response.text()
                print(f"❌ Authentication failed: {error_text}")
        
        print("\n🌐 Testing Public Endpoints...")
        
        # Test public verification endpoint (should work without auth)
        test_verification = {
            "loa_number": "LOA-2024-123456",
            "verification_code": "TEST123"
        }
        
        async with session.post(f"{base_url}/api/loa/verify", json=test_verification) as verify_response:
            print(f"Public Verification Status: {verify_response.status}")
            
            if verify_response.status == 200:
                verify_result = await verify_response.json()
                print("✅ Public verification endpoint working!")
                print(f"Valid: {verify_result.get('valid')}")
                if not verify_result.get('valid'):
                    print(f"Error: {verify_result.get('error')}")
            else:
                error_text = await verify_response.text()
                print(f"❌ Public verification failed: {error_text}")

if __name__ == "__main__":
    print("🧪 Testing LOA Endpoints After Pydantic Fixes")
    print("=" * 50)
    asyncio.run(test_loa_endpoints())
    print("\n✨ Test completed!")