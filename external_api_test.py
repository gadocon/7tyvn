import requests
import json
import time
from datetime import datetime, timezone
import uuid

def test_external_api_directly():
    """Test the external n8n webhook directly"""
    print("🔗 Testing External n8n Webhook Directly")
    print("=" * 50)
    
    # Test with the known working code
    test_codes = [
        {"code": "PA22040522471", "provider": "mien_bac", "expected": "Khách hàng không nợ cước"},
        {"code": "INVALID123", "provider": "mien_nam", "expected": "Mã Khách hàng nhập vào không tồn tại"},
        {"code": "PA22040522471", "provider": "mien_nam", "expected": "Error or different response"}
    ]
    
    for test_case in test_codes:
        print(f"\n🧪 Testing code: {test_case['code']} with provider: {test_case['provider']}")
        
        payload = {
            "bills": [
                {
                    "customer_id": test_case['code'],
                    "electric_provider": test_case['provider'],
                    "provider_name": test_case['provider'],
                    "contractNumber": test_case['code'],
                    "sku": "ELECTRIC_BILL"
                }
            ],
            "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
            "request_id": f"direct_test_{str(uuid.uuid4())[:8]}",
            "webhookUrl": "https://n8n.phamthanh.net/webhook/checkbill",
            "executionMode": "production"
        }
        
        try:
            print(f"   📤 Sending request to external API...")
            start_time = time.time()
            
            response = requests.post(
                "https://n8n.phamthanh.net/webhook/checkbill",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=35
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"   ⏱️  Response time: {duration:.2f} seconds")
            print(f"   📊 Status Code: {response.status_code}")
            print(f"   📄 Response Headers: {dict(response.headers)}")
            
            try:
                response_data = response.json()
                print(f"   📋 Response Data: {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                if isinstance(response_data, list) and len(response_data) > 0:
                    first_item = response_data[0]
                    if "error" in first_item:
                        print(f"   ❌ Error found in response")
                        if "message" in first_item["error"]:
                            print(f"   💬 Error message: {first_item['error']['message']}")
                    else:
                        print(f"   ✅ Successful response (no error field)")
                        
            except json.JSONDecodeError:
                print(f"   ⚠️  Could not parse JSON response")
                print(f"   📝 Raw response: {response.text[:500]}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Request timed out after 35 seconds")
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")

def test_backend_api_detailed():
    """Test our backend API with detailed logging"""
    print("\n🏠 Testing Our Backend API with External Integration")
    print("=" * 50)
    
    base_url = "https://crm-overflow-fix.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    test_cases = [
        {
            "name": "Known Working Code (Miền Bắc)",
            "data": {
                "gateway": "FPT",
                "provider_region": "MIEN_BAC",
                "codes": ["PA22040522471"]
            }
        },
        {
            "name": "Invalid Code",
            "data": {
                "gateway": "FPT", 
                "provider_region": "MIEN_NAM",
                "codes": ["INVALID123"]
            }
        },
        {
            "name": "Mixed Codes",
            "data": {
                "gateway": "FPT",
                "provider_region": "MIEN_NAM", 
                "codes": ["PA22040522471", "INVALID123", "NOTFOUND456"]
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 {test_case['name']}")
        
        try:
            print(f"   📤 Sending request...")
            start_time = time.time()
            
            response = requests.post(
                f"{api_url}/bill/check",
                json=test_case['data'],
                headers={'Content-Type': 'application/json'},
                timeout=40  # Give extra time for external API
            )
            
            end_time = time.time()
            duration = end_time - start_time
            
            print(f"   ⏱️  Response time: {duration:.2f} seconds")
            print(f"   📊 Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                items = response_data.get('items', [])
                summary = response_data.get('summary', {})
                
                print(f"   📋 Summary: {summary}")
                
                for item in items:
                    code = item.get('customer_code')
                    status = item.get('status')
                    errors = item.get('errors', {})
                    
                    print(f"   📄 Code: {code}")
                    print(f"      Status: {status}")
                    if status == "ERROR" and errors:
                        print(f"      Error: {errors.get('message', 'Unknown error')}")
                    elif status == "OK":
                        print(f"      Name: {item.get('full_name', 'N/A')}")
                        print(f"      Amount: {item.get('amount', 'N/A')}")
            else:
                print(f"   ❌ Error response: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Request timed out after 40 seconds")
        except Exception as e:
            print(f"   ❌ Request failed: {str(e)}")

if __name__ == "__main__":
    test_external_api_directly()
    test_backend_api_detailed()