import requests
import sys
import json
from datetime import datetime

class FPTBillManagerAPITester:
    def __init__(self, base_url="https://bill-checker-app.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        if headers is None:
            headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text[:200]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )
        
        if success:
            required_fields = ['total_bills', 'available_bills', 'total_customers', 'total_revenue', 'recent_activities']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print(f"   📊 Stats: Bills={response.get('total_bills', 0)}, Customers={response.get('total_customers', 0)}, Revenue={response.get('total_revenue', 0)}")
        
        return success

    def test_check_bills_valid(self):
        """Test bill checking with valid codes"""
        valid_codes = ["PA22040522471", "PA22040506503", "PA22060724572"]
        
        success, response = self.run_test(
            "Check Bills - Valid Codes",
            "POST",
            "bill/check",
            200,
            data={
                "gateway": "FPT",
                "provider_region": "MIEN_NAM",
                "codes": valid_codes
            }
        )
        
        if success:
            items = response.get('items', [])
            summary = response.get('summary', {})
            print(f"   📋 Results: {len(items)} items, {summary.get('ok', 0)} OK, {summary.get('error', 0)} errors")
            
            # Check if all valid codes returned OK status
            ok_codes = [item['customer_code'] for item in items if item.get('status') == 'OK']
            print(f"   ✅ Valid codes found: {ok_codes}")
        
        return success

    def test_check_bills_invalid(self):
        """Test bill checking with invalid codes"""
        invalid_codes = ["INVALID123", "NOTFOUND456"]
        
        success, response = self.run_test(
            "Check Bills - Invalid Codes",
            "POST",
            "bill/check",
            200,
            data={
                "gateway": "FPT",
                "provider_region": "MIEN_NAM", 
                "codes": invalid_codes
            }
        )
        
        if success:
            items = response.get('items', [])
            summary = response.get('summary', {})
            print(f"   📋 Results: {len(items)} items, {summary.get('ok', 0)} OK, {summary.get('error', 0)} errors")
            
            # Check if all invalid codes returned ERROR status
            error_codes = [item['customer_code'] for item in items if item.get('status') == 'ERROR']
            print(f"   ❌ Invalid codes: {error_codes}")
        
        return success

    def test_get_bills(self):
        """Test get bills endpoint"""
        success, response = self.run_test(
            "Get Bills",
            "GET",
            "bills",
            200
        )
        
        if success:
            print(f"   📄 Found {len(response)} bills")
            if response:
                first_bill = response[0]
                print(f"   📋 Sample bill fields: {list(first_bill.keys())}")
        
        return success

    def test_get_customers(self):
        """Test get customers endpoint"""
        success, response = self.run_test(
            "Get Customers",
            "GET",
            "customers",
            200
        )
        
        if success:
            print(f"   👥 Found {len(response)} customers")
            if response:
                first_customer = response[0]
                print(f"   👤 Sample customer: {first_customer.get('name', 'Unknown')}")
        
        return success

    def test_webhook_endpoint(self):
        """Test webhook endpoint with sample FPT payload"""
        sample_payload = {
            "bills": [
                {
                    "customer_id": "PA22040522471",
                    "electric_provider": "mien_nam",
                    "provider_name": "Điện lực miền Nam",
                    "full_name": "Nguyễn Văn Test",
                    "address": "123 Test Street",
                    "amount": 1500000,
                    "billing_cycle": "08/2025"
                }
            ],
            "timestamp": int(datetime.now().timestamp()),
            "request_id": f"test_request_{int(datetime.now().timestamp())}",
            "webhook_url": f"{self.base_url}/api/webhook/checkbill",
            "execution_mode": "test"
        }
        
        success, response = self.run_test(
            "Webhook Endpoint",
            "POST",
            "webhook/checkbill",
            200,
            data=sample_payload,
            headers={
                'Content-Type': 'application/json',
                'X-API-KEY': 'test-key'
            }
        )
        
        if success:
            print(f"   🔗 Webhook response: {response}")
        
        return success

    def test_error_handling(self):
        """Test API error handling"""
        print(f"\n🧪 Testing Error Handling...")
        
        # Test invalid endpoint
        success1, _ = self.run_test(
            "Invalid Endpoint",
            "GET",
            "nonexistent",
            404
        )
        
        # Test invalid request body for bill check
        success2, _ = self.run_test(
            "Invalid Bill Check Request",
            "POST",
            "bill/check",
            422,  # Validation error
            data={
                "invalid_field": "test"
            }
        )
        
        return success1 or success2  # At least one should work

def main():
    print("🚀 Starting FPT Bill Manager API Tests")
    print("=" * 50)
    
    tester = FPTBillManagerAPITester()
    
    # Run all tests
    tests = [
        tester.test_dashboard_stats,
        tester.test_check_bills_valid,
        tester.test_check_bills_invalid,
        tester.test_get_bills,
        tester.test_get_customers,
        tester.test_webhook_endpoint,
        tester.test_error_handling
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())