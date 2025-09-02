import requests
import asyncio
import aiohttp
import time
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

class PerformanceReliabilityTester:
    def __init__(self, base_url="https://crm-overflow-fix.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"

    def test_concurrent_requests(self):
        """Test multiple concurrent API calls"""
        print("🚀 Testing Concurrent External API Calls")
        print("=" * 50)
        
        def make_request(request_id):
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_url}/bill/check",
                    json={
                        "gateway": "FPT",
                        "provider_region": "MIEN_NAM",
                        "codes": [f"TEST{request_id:03d}"]
                    },
                    headers={'Content-Type': 'application/json'},
                    timeout=40
                )
                end_time = time.time()
                duration = end_time - start_time
                
                return {
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "duration": duration,
                    "success": response.status_code == 200
                }
            except Exception as e:
                return {
                    "request_id": request_id,
                    "status_code": None,
                    "duration": None,
                    "success": False,
                    "error": str(e)
                }
        
        # Test with 3 concurrent requests
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(make_request, i) for i in range(1, 4)]
            results = [future.result() for future in futures]
        
        print(f"\n📊 Concurrent Request Results:")
        total_duration = 0
        successful_requests = 0
        
        for result in results:
            print(f"   Request {result['request_id']}: ", end="")
            if result['success']:
                print(f"✅ Success ({result['duration']:.2f}s)")
                total_duration += result['duration']
                successful_requests += 1
            else:
                print(f"❌ Failed - {result.get('error', 'Unknown error')}")
        
        if successful_requests > 0:
            avg_duration = total_duration / successful_requests
            print(f"\n📈 Average Response Time: {avg_duration:.2f} seconds")
            print(f"📈 Success Rate: {successful_requests}/{len(results)} ({successful_requests/len(results)*100:.1f}%)")
        
        return results

    def test_timeout_behavior(self):
        """Test timeout handling"""
        print("\n⏰ Testing Timeout Behavior")
        print("=" * 50)
        
        try:
            print("   Testing with very short timeout (1 second)...")
            start_time = time.time()
            
            response = requests.post(
                f"{self.api_url}/bill/check",
                json={
                    "gateway": "FPT",
                    "provider_region": "MIEN_BAC",
                    "codes": ["TIMEOUT_TEST"]
                },
                headers={'Content-Type': 'application/json'},
                timeout=1  # Very short timeout
            )
            
            end_time = time.time()
            print(f"   ⚠️  Unexpected success in {end_time - start_time:.2f}s")
            
        except requests.exceptions.Timeout:
            end_time = time.time()
            print(f"   ✅ Timeout handled correctly after {end_time - start_time:.2f}s")
            
        except Exception as e:
            print(f"   ❌ Unexpected error: {str(e)}")

    def test_error_recovery(self):
        """Test error recovery and fallback messaging"""
        print("\n🔄 Testing Error Recovery")
        print("=" * 50)
        
        # Test with invalid request data
        test_cases = [
            {
                "name": "Missing required fields",
                "data": {"invalid": "data"},
                "expected_status": 422
            },
            {
                "name": "Invalid provider region",
                "data": {
                    "gateway": "FPT",
                    "provider_region": "INVALID_REGION",
                    "codes": ["TEST123"]
                },
                "expected_status": 422
            },
            {
                "name": "Empty codes array",
                "data": {
                    "gateway": "FPT",
                    "provider_region": "MIEN_NAM",
                    "codes": []
                },
                "expected_status": 200
            }
        ]
        
        for test_case in test_cases:
            print(f"\n   🧪 {test_case['name']}")
            try:
                response = requests.post(
                    f"{self.api_url}/bill/check",
                    json=test_case['data'],
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.status_code == test_case['expected_status']:
                    print(f"      ✅ Expected status {test_case['expected_status']}")
                else:
                    print(f"      ⚠️  Got {response.status_code}, expected {test_case['expected_status']}")
                    
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        print(f"      📝 Error detail: {error_data['detail']}")
                except:
                    pass
                    
            except Exception as e:
                print(f"      ❌ Request failed: {str(e)}")

    def test_different_providers(self):
        """Test different provider regions"""
        print("\n🌏 Testing Different Provider Regions")
        print("=" * 50)
        
        providers = ["MIEN_BAC", "MIEN_NAM", "HCMC"]
        
        for provider in providers:
            print(f"\n   🧪 Testing {provider}")
            try:
                start_time = time.time()
                response = requests.post(
                    f"{self.api_url}/bill/check",
                    json={
                        "gateway": "FPT",
                        "provider_region": provider,
                        "codes": ["TEST123"]
                    },
                    headers={'Content-Type': 'application/json'},
                    timeout=35
                )
                end_time = time.time()
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"      ✅ Success ({end_time - start_time:.2f}s)")
                    print(f"      📊 Results: {data.get('summary', {})}")
                else:
                    print(f"      ❌ Failed with status {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ Request failed: {str(e)}")

    def test_database_integration(self):
        """Test database storage of external API results"""
        print("\n💾 Testing Database Integration")
        print("=" * 50)
        
        # First, make a bill check request
        print("   📤 Making bill check request...")
        try:
            response = requests.post(
                f"{self.api_url}/bill/check",
                json={
                    "gateway": "FPT",
                    "provider_region": "MIEN_NAM",
                    "codes": ["DB_TEST_123"]
                },
                headers={'Content-Type': 'application/json'},
                timeout=35
            )
            
            if response.status_code == 200:
                print("   ✅ Bill check request successful")
                
                # Wait a moment for database write
                time.sleep(2)
                
                # Check if bills were stored in database
                bills_response = requests.get(
                    f"{self.api_url}/bills",
                    timeout=10
                )
                
                if bills_response.status_code == 200:
                    bills = bills_response.json()
                    print(f"   📊 Found {len(bills)} bills in database")
                    
                    # Look for our test bill
                    test_bill = None
                    for bill in bills:
                        if bill.get('customer_code') == 'DB_TEST_123':
                            test_bill = bill
                            break
                    
                    if test_bill:
                        print("   ✅ Test bill found in database")
                        print(f"      📋 Bill ID: {test_bill.get('id')}")
                        print(f"      📋 Status: {test_bill.get('status')}")
                        print(f"      📋 Provider: {test_bill.get('provider_region')}")
                    else:
                        print("   ⚠️  Test bill not found in database")
                else:
                    print(f"   ❌ Failed to retrieve bills: {bills_response.status_code}")
            else:
                print(f"   ❌ Bill check failed: {response.status_code}")
                
        except Exception as e:
            print(f"   ❌ Database test failed: {str(e)}")

def main():
    print("🧪 FPT Bill Manager Performance & Reliability Tests")
    print("=" * 60)
    
    tester = PerformanceReliabilityTester()
    
    # Run all performance tests
    tester.test_concurrent_requests()
    tester.test_timeout_behavior()
    tester.test_error_recovery()
    tester.test_different_providers()
    tester.test_database_integration()
    
    print("\n" + "=" * 60)
    print("🏁 Performance & Reliability Testing Complete")

if __name__ == "__main__":
    main()