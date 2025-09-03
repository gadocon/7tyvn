#!/usr/bin/env python3
"""
DELETE Bill Functionality Verification Test
Testing DELETE /api/bills/{bill_id} endpoint after frontend improvements
"""

import requests
import json
from datetime import datetime

class DeleteBillTester:
    def __init__(self, base_url="https://bill-manager-19.preview.emergentagent.com"):
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
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    return True, response_data
                except:
                    return True, {}
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                    return False, error_data
                except:
                    print(f"   Error text: {response.text[:200]}")
                    return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def test_delete_bill_functionality_verification(self):
        """VERIFICATION: Test DELETE bill functionality after frontend improvements"""
        print(f"\n🎯 VERIFICATION: DELETE Bill Functionality After Frontend Improvements")
        print("=" * 70)
        print("🔍 Testing DELETE /api/bills/{bill_id} endpoint with all scenarios")
        print("📋 Verifying error response structure matches frontend expectations")
        
        # Step 1: Create test bills for different scenarios
        print(f"\n📋 Step 1: Creating test bills for all scenarios...")
        
        # Create AVAILABLE bill (should be deletable)
        available_bill_data = {
            "customer_code": f"AVAIL{int(datetime.now().timestamp())}",
            "provider_region": "MIEN_NAM",
            "full_name": "Test Available Bill Customer",
            "address": "Test Address",
            "amount": 1200000,
            "billing_cycle": "12/2025",
            "status": "AVAILABLE"
        }
        
        available_success, available_response = self.run_test(
            "Create AVAILABLE Bill",
            "POST",
            "bills/create",
            200,
            data=available_bill_data
        )
        
        if not available_success:
            print("❌ Failed to create AVAILABLE bill")
            return False
            
        available_bill_id = available_response.get('id')
        print(f"✅ Created AVAILABLE bill: {available_bill_id}")
        
        # Create SOLD bill (should be protected)
        sold_bill_data = {
            "customer_code": f"SOLD{int(datetime.now().timestamp())}",
            "provider_region": "MIEN_NAM",
            "full_name": "Test Sold Bill Customer", 
            "address": "Test Address",
            "amount": 1500000,
            "billing_cycle": "12/2025",
            "status": "SOLD"
        }
        
        sold_success, sold_response = self.run_test(
            "Create SOLD Bill",
            "POST",
            "bills/create",
            200,
            data=sold_bill_data
        )
        
        if not sold_success:
            print("❌ Failed to create SOLD bill")
            return False
            
        sold_bill_id = sold_response.get('id')
        print(f"✅ Created SOLD bill: {sold_bill_id}")
        
        # Create CROSSED bill (should be protected)
        crossed_bill_data = {
            "customer_code": f"CROSSED{int(datetime.now().timestamp())}",
            "provider_region": "MIEN_NAM",
            "full_name": "Test Crossed Bill Customer",
            "address": "Test Address", 
            "amount": 0,
            "billing_cycle": "12/2025",
            "status": "CROSSED"
        }
        
        crossed_success, crossed_response = self.run_test(
            "Create CROSSED Bill",
            "POST",
            "bills/create",
            200,
            data=crossed_bill_data
        )
        
        if not crossed_success:
            print("❌ Failed to create CROSSED bill")
            return False
            
        crossed_bill_id = crossed_response.get('id')
        print(f"✅ Created CROSSED bill: {crossed_bill_id}")
        
        # Test results tracking
        test_results = []
        
        # Step 2: TEST SCENARIO 1 - AVAILABLE bill deletion (should succeed)
        print(f"\n🟢 SCENARIO 1: Delete AVAILABLE bill (should succeed with 200)")
        print(f"   Target: {available_bill_id} (status: AVAILABLE)")
        
        url = f"{self.api_url}/bills/{available_bill_id}"
        
        try:
            response = requests.delete(url, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    response_data = response.json()
                    print(f"   Response: {response_data}")
                    
                    # Verify success response structure
                    has_success_flag = 'success' in response_data
                    has_message = 'message' in response_data
                    success_value = response_data.get('success')
                    message = response_data.get('message', '')
                    
                    print(f"   ✅ Success flag present: {has_success_flag}")
                    print(f"   ✅ Message present: {has_message}")
                    print(f"   ✅ Success value: {success_value}")
                    print(f"   ✅ Message: {message}")
                    
                    if has_success_flag and has_message and success_value:
                        print(f"   🎉 SCENARIO 1 PASSED: AVAILABLE bill deleted successfully")
                        test_results.append({"scenario": 1, "passed": True, "details": "AVAILABLE bill deletion successful"})
                        self.tests_passed += 1
                    else:
                        print(f"   ❌ SCENARIO 1 FAILED: Invalid success response structure")
                        test_results.append({"scenario": 1, "passed": False, "details": "Invalid response structure"})
                        
                except Exception as e:
                    print(f"   ❌ SCENARIO 1 FAILED: Could not parse response - {e}")
                    test_results.append({"scenario": 1, "passed": False, "details": f"Parse error: {e}"})
            else:
                print(f"   ❌ SCENARIO 1 FAILED: Expected 200, got {response.status_code}")
                test_results.append({"scenario": 1, "passed": False, "details": f"Wrong status code: {response.status_code}"})
                
        except Exception as e:
            print(f"   ❌ SCENARIO 1 FAILED: Request error - {e}")
            test_results.append({"scenario": 1, "passed": False, "details": f"Request error: {e}"})
        finally:
            self.tests_run += 1
        
        # Step 3: TEST SCENARIO 2 - SOLD bill deletion (should return 400)
        print(f"\n🔴 SCENARIO 2: Delete SOLD bill (should return 400 with Vietnamese detail)")
        print(f"   Target: {sold_bill_id} (status: SOLD)")
        
        url = f"{self.api_url}/bills/{sold_bill_id}"
        
        try:
            response = requests.delete(url, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"   Error Response: {error_data}")
                    
                    # Verify error response structure for frontend
                    has_detail = 'detail' in error_data
                    detail_message = error_data.get('detail', '')
                    
                    print(f"   ✅ Detail field present: {has_detail}")
                    print(f"   ✅ Detail message: {detail_message}")
                    
                    # Check for Vietnamese error message
                    expected_vietnamese_phrases = [
                        "Không thể xóa bill đã bán",
                        "đã được tham chiếu trong giao dịch khách hàng"
                    ]
                    
                    vietnamese_found = any(phrase in detail_message for phrase in expected_vietnamese_phrases)
                    print(f"   ✅ Vietnamese message: {vietnamese_found}")
                    
                    if has_detail and vietnamese_found:
                        print(f"   🎉 SCENARIO 2 PASSED: SOLD bill deletion properly blocked with Vietnamese message")
                        test_results.append({"scenario": 2, "passed": True, "details": "SOLD bill protection working"})
                        self.tests_passed += 1
                    else:
                        print(f"   ❌ SCENARIO 2 FAILED: Missing detail field or Vietnamese message")
                        test_results.append({"scenario": 2, "passed": False, "details": "Missing detail or Vietnamese"})
                        
                except Exception as e:
                    print(f"   ❌ SCENARIO 2 FAILED: Could not parse error response - {e}")
                    test_results.append({"scenario": 2, "passed": False, "details": f"Parse error: {e}"})
            else:
                print(f"   ❌ SCENARIO 2 FAILED: Expected 400, got {response.status_code}")
                test_results.append({"scenario": 2, "passed": False, "details": f"Wrong status code: {response.status_code}"})
                
        except Exception as e:
            print(f"   ❌ SCENARIO 2 FAILED: Request error - {e}")
            test_results.append({"scenario": 2, "passed": False, "details": f"Request error: {e}"})
        finally:
            self.tests_run += 1
        
        # Step 4: TEST SCENARIO 3 - CROSSED bill deletion (should return 400)
        print(f"\n🟡 SCENARIO 3: Delete CROSSED bill (should return 400 with Vietnamese detail)")
        print(f"   Target: {crossed_bill_id} (status: CROSSED)")
        
        url = f"{self.api_url}/bills/{crossed_bill_id}"
        
        try:
            response = requests.delete(url, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    print(f"   Error Response: {error_data}")
                    
                    # Verify error response structure for frontend
                    has_detail = 'detail' in error_data
                    detail_message = error_data.get('detail', '')
                    
                    print(f"   ✅ Detail field present: {has_detail}")
                    print(f"   ✅ Detail message: {detail_message}")
                    
                    # Check for Vietnamese error message
                    expected_vietnamese_phrases = [
                        "Không thể xóa bill đã gạch",
                        "đã được xác nhận không có nợ cước"
                    ]
                    
                    vietnamese_found = any(phrase in detail_message for phrase in expected_vietnamese_phrases)
                    print(f"   ✅ Vietnamese message: {vietnamese_found}")
                    
                    if has_detail and vietnamese_found:
                        print(f"   🎉 SCENARIO 3 PASSED: CROSSED bill deletion properly blocked with Vietnamese message")
                        test_results.append({"scenario": 3, "passed": True, "details": "CROSSED bill protection working"})
                        self.tests_passed += 1
                    else:
                        print(f"   ❌ SCENARIO 3 FAILED: Missing detail field or Vietnamese message")
                        test_results.append({"scenario": 3, "passed": False, "details": "Missing detail or Vietnamese"})
                        
                except Exception as e:
                    print(f"   ❌ SCENARIO 3 FAILED: Could not parse error response - {e}")
                    test_results.append({"scenario": 3, "passed": False, "details": f"Parse error: {e}"})
            else:
                print(f"   ❌ SCENARIO 3 FAILED: Expected 400, got {response.status_code}")
                test_results.append({"scenario": 3, "passed": False, "details": f"Wrong status code: {response.status_code}"})
                
        except Exception as e:
            print(f"   ❌ SCENARIO 3 FAILED: Request error - {e}")
            test_results.append({"scenario": 3, "passed": False, "details": f"Request error: {e}"})
        finally:
            self.tests_run += 1
        
        # Step 5: TEST SCENARIO 4 - Non-existent bill deletion (should return 404)
        print(f"\n⚫ SCENARIO 4: Delete non-existent bill (should return 404)")
        
        fake_bill_id = f"nonexistent_{int(datetime.now().timestamp())}"
        print(f"   Target: {fake_bill_id} (non-existent)")
        
        url = f"{self.api_url}/bills/{fake_bill_id}"
        
        try:
            response = requests.delete(url, timeout=30)
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 404:
                try:
                    error_data = response.json()
                    print(f"   Error Response: {error_data}")
                    
                    # Verify error response structure for frontend
                    has_detail = 'detail' in error_data
                    detail_message = error_data.get('detail', '')
                    
                    print(f"   ✅ Detail field present: {has_detail}")
                    print(f"   ✅ Detail message: {detail_message}")
                    
                    if has_detail:
                        print(f"   🎉 SCENARIO 4 PASSED: Non-existent bill returns 404 with detail field")
                        test_results.append({"scenario": 4, "passed": True, "details": "404 error handling working"})
                        self.tests_passed += 1
                    else:
                        print(f"   ❌ SCENARIO 4 FAILED: Missing detail field in 404 response")
                        test_results.append({"scenario": 4, "passed": False, "details": "Missing detail field"})
                        
                except Exception as e:
                    print(f"   ❌ SCENARIO 4 FAILED: Could not parse error response - {e}")
                    test_results.append({"scenario": 4, "passed": False, "details": f"Parse error: {e}"})
            else:
                print(f"   ❌ SCENARIO 4 FAILED: Expected 404, got {response.status_code}")
                test_results.append({"scenario": 4, "passed": False, "details": f"Wrong status code: {response.status_code}"})
                
        except Exception as e:
            print(f"   ❌ SCENARIO 4 FAILED: Request error - {e}")
            test_results.append({"scenario": 4, "passed": False, "details": f"Request error: {e}"})
        finally:
            self.tests_run += 1
        
        # Step 6: Summary and verification
        print(f"\n📊 DELETE BILL FUNCTIONALITY VERIFICATION RESULTS:")
        print("=" * 60)
        
        passed_scenarios = [r for r in test_results if r["passed"]]
        failed_scenarios = [r for r in test_results if not r["passed"]]
        
        print(f"✅ PASSED SCENARIOS: {len(passed_scenarios)}/4")
        for result in passed_scenarios:
            print(f"   - Scenario {result['scenario']}: {result['details']}")
            
        if failed_scenarios:
            print(f"\n❌ FAILED SCENARIOS: {len(failed_scenarios)}/4")
            for result in failed_scenarios:
                print(f"   - Scenario {result['scenario']}: {result['details']}")
        
        # Overall assessment
        all_passed = len(passed_scenarios) == 4
        
        if all_passed:
            print(f"\n🎉 DELETE BILL FUNCTIONALITY FULLY WORKING!")
            print(f"✅ AVAILABLE bills can be deleted successfully (200 status, success message)")
            print(f"✅ SOLD bills deletion properly blocked with 400 error and Vietnamese message")
            print(f"✅ CROSSED bills deletion properly blocked with 400 error and Vietnamese message")
            print(f"✅ Non-existent bills return 404 error with proper 'detail' field")
            print(f"✅ Error structure: All error responses contain 'detail' field as expected by frontend")
            print(f"✅ Vietnamese messages: Error messages are user-friendly in Vietnamese")
            print(f"✅ Success responses: Contain success flag and message")
            print(f"✅ HTTP status codes: All scenarios return appropriate status codes")
            print(f"\n🔧 FRONTEND COMPATIBILITY: Backend DELETE functionality is working as designed")
        else:
            print(f"\n⚠️  DELETE BILL FUNCTIONALITY HAS ISSUES!")
            print(f"❌ Some scenarios failed - check individual test results above")
            print(f"🔧 RECOMMENDED ACTIONS:")
            print(f"   - Fix any failing scenarios")
            print(f"   - Ensure all error responses have 'detail' field")
            print(f"   - Verify Vietnamese error messages")
            print(f"   - Test frontend error handling with these responses")
        
        return all_passed

def main():
    print("🎯 DELETE BILL FUNCTIONALITY VERIFICATION TEST")
    print("=" * 80)
    print("Testing DELETE /api/bills/{bill_id} endpoint after frontend improvements")
    
    tester = DeleteBillTester()
    
    # Run the DELETE bill verification test
    success = tester.test_delete_bill_functionality_verification()
    
    print(f"\n{'='*80}")
    print(f"📊 FINAL TEST SUMMARY")
    print(f"📊 Tests Run: {tester.tests_run}")
    print(f"📊 Tests Passed: {tester.tests_passed}")
    print(f"📊 Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%" if tester.tests_run > 0 else "No tests run")
    
    if success:
        print(f"\n🎉 DELETE BILL VERIFICATION PASSED!")
        print(f"✅ All DELETE bill scenarios working correctly")
        print(f"✅ Error response structure matches frontend expectations")
        print(f"✅ Vietnamese error messages are user-friendly")
        print(f"✅ Success responses contain proper flags and messages")
        return 0
    else:
        print(f"\n❌ DELETE BILL VERIFICATION FAILED!")
        print(f"⚠️  Some DELETE bill scenarios have issues")
        print(f"🔧 Backend DELETE functionality needs attention")
        return 1

if __name__ == "__main__":
    exit(main())