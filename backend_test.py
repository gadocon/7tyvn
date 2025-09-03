import requests
import sys
import json
from datetime import datetime
import pymongo
from pymongo import MongoClient

class FPTBillManagerAPITester:
    def __init__(self, base_url="https://crm7ty.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
        # MongoDB connection for direct database debugging
        try:
            self.mongo_client = MongoClient("mongodb://localhost:27017")
            self.db = self.mongo_client["test_database"]
            self.mongo_connected = True
            print("✅ MongoDB connection established for database debugging")
        except Exception as e:
            print(f"⚠️ MongoDB connection failed: {e}")
            self.mongo_connected = False

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

    def test_customer_lookup_fix_verification(self):
        """Test customer lookup fix và phân tích ObjectId vs UUID issue"""
        print(f"\n🎯 CUSTOMER LOOKUP FIX VERIFICATION - REVIEW REQUEST")
        print("=" * 80)
        print("🔍 TESTING OBJECTIVES:")
        print("   1. Test customer ID 68b86b157a314c251c8c863b với fix mới (should work now)")
        print("   2. Test một vài customers khác để ensure compatibility")
        print("   3. Analyze database để hiểu khi nào ObjectId vs UUID được dùng")
        print("   4. Kiểm tra bills/transactions có tương tự vấn đề không")
        
        target_customer_id = "68b86b157a314c251c8c863b"
        test_results = {
            "target_customer_working": False,
            "other_customers_working": 0,
            "database_analysis": {},
            "bills_transactions_check": {},
            "total_tests": 0,
            "passed_tests": 0
        }
        
        # Step 1: Test the specific customer ID that was failing
        print(f"\n🔍 STEP 1: Testing Target Customer ID {target_customer_id}")
        print("=" * 60)
        print(f"   Expected: Should return 200 instead of 404 after fix")
        
        # Test detailed-profile endpoint
        detailed_profile_success, detailed_profile_response = self.run_test(
            f"Customer Detailed Profile - {target_customer_id}",
            "GET",
            f"customers/{target_customer_id}/detailed-profile",
            200
        )
        
        if detailed_profile_success:
            print(f"✅ SUCCESS: Customer {target_customer_id} now returns 200!")
            print(f"   Customer name: {detailed_profile_response.get('customer', {}).get('name', 'Unknown')}")
            print(f"   Response structure: {list(detailed_profile_response.keys())}")
            test_results["target_customer_working"] = True
            test_results["passed_tests"] += 1
        else:
            print(f"❌ FAILED: Customer {target_customer_id} still returns error")
            print(f"   Fix may not be working correctly")
        
        test_results["total_tests"] += 1
        
        # Test basic customer endpoint too
        customer_success, customer_response = self.run_test(
            f"Customer Basic Info - {target_customer_id}",
            "GET",
            f"customers/{target_customer_id}",
            200
        )
        
        if customer_success:
            print(f"✅ Basic customer endpoint also working for {target_customer_id}")
            print(f"   Customer name: {customer_response.get('name', 'Unknown')}")
            test_results["passed_tests"] += 1
        else:
            print(f"❌ Basic customer endpoint still failing for {target_customer_id}")
        
        test_results["total_tests"] += 1
        
        # Step 2: Test other customers to ensure compatibility
        print(f"\n🔍 STEP 2: Testing Other Customers for Compatibility")
        print("=" * 60)
        
        # Get list of customers to test
        all_customers_success, all_customers_response = self.run_test(
            "Get All Customers for Compatibility Testing",
            "GET",
            "customers?page_size=50",
            200
        )
        
        if all_customers_success and all_customers_response:
            print(f"✅ Found {len(all_customers_response)} customers for testing")
            
            # Test first 5 customers with different ID formats
            test_customers = all_customers_response[:5]
            
            for i, customer in enumerate(test_customers):
                customer_id = customer.get('id', '')
                customer_name = customer.get('name', 'Unknown')
                
                print(f"\n   Test {i+1}: {customer_name} (ID: {customer_id})")
                print(f"   ID Length: {len(customer_id)} chars")
                print(f"   ID Format: {'ObjectId' if len(customer_id) == 24 else 'UUID' if len(customer_id) == 36 else 'Other'}")
                
                # Test detailed-profile endpoint
                test_success, test_response = self.run_test(
                    f"Compatibility Test - {customer_name}",
                    "GET",
                    f"customers/{customer_id}/detailed-profile",
                    200
                )
                
                if test_success:
                    print(f"   ✅ SUCCESS: Detailed-profile working for {customer_name}")
                    test_results["other_customers_working"] += 1
                    test_results["passed_tests"] += 1
                else:
                    print(f"   ❌ FAILED: Detailed-profile not working for {customer_name}")
                
                test_results["total_tests"] += 1
        
        # Step 3: Database Analysis - ObjectId vs UUID
        print(f"\n🔍 STEP 3: Database Analysis - ObjectId vs UUID Usage")
        print("=" * 60)
        
        if self.mongo_connected:
            try:
                # Analyze customers collection
                customers_cursor = self.db.customers.find({}, {"_id": 1, "id": 1, "name": 1}).limit(20)
                customers_sample = list(customers_cursor)
                
                print(f"✅ Database connection successful - analyzing {len(customers_sample)} customers")
                
                objectid_customers = []
                uuid_customers = []
                mixed_customers = []
                
                for customer in customers_sample:
                    mongo_id = str(customer.get('_id', ''))
                    uuid_id = customer.get('id', '')
                    name = customer.get('name', 'Unknown')
                    
                    # Check if customer has both _id and id fields
                    if mongo_id and uuid_id:
                        if len(uuid_id) == 24 and all(c in '0123456789abcdef' for c in uuid_id.lower()):
                            # UUID field contains ObjectId format
                            mixed_customers.append({
                                "name": name,
                                "_id": mongo_id,
                                "id": uuid_id,
                                "issue": "UUID field contains ObjectId"
                            })
                        elif len(uuid_id) == 36 and uuid_id.count('-') == 4:
                            # Proper UUID format
                            uuid_customers.append({
                                "name": name,
                                "_id": mongo_id,
                                "id": uuid_id
                            })
                        else:
                            # Other format
                            mixed_customers.append({
                                "name": name,
                                "_id": mongo_id,
                                "id": uuid_id,
                                "issue": "Unknown ID format"
                            })
                    elif mongo_id and not uuid_id:
                        # Only has _id, no id field
                        objectid_customers.append({
                            "name": name,
                            "_id": mongo_id,
                            "id": None
                        })
                
                print(f"\n📊 DATABASE ANALYSIS RESULTS:")
                print(f"   Customers with proper UUID format: {len(uuid_customers)}")
                print(f"   Customers with only ObjectId: {len(objectid_customers)}")
                print(f"   Customers with mixed/problematic IDs: {len(mixed_customers)}")
                
                # Show examples
                if uuid_customers:
                    example = uuid_customers[0]
                    print(f"\n   UUID Example: {example['name']}")
                    print(f"      _id: {example['_id']}")
                    print(f"      id:  {example['id']}")
                
                if mixed_customers:
                    example = mixed_customers[0]
                    print(f"\n   Mixed/Problematic Example: {example['name']}")
                    print(f"      _id: {example['_id']}")
                    print(f"      id:  {example['id']}")
                    print(f"      Issue: {example['issue']}")
                
                # Check if target customer is in mixed category
                target_in_mixed = any(c.get('id') == target_customer_id for c in mixed_customers)
                if target_in_mixed:
                    print(f"\n🎯 TARGET CUSTOMER ANALYSIS:")
                    print(f"   Customer {target_customer_id} found in mixed/problematic category")
                    print(f"   This explains why the fix was needed!")
                
                test_results["database_analysis"] = {
                    "uuid_customers": len(uuid_customers),
                    "objectid_customers": len(objectid_customers),
                    "mixed_customers": len(mixed_customers),
                    "target_in_mixed": target_in_mixed
                }
                
            except Exception as e:
                print(f"❌ Database analysis failed: {e}")
        else:
            print(f"⚠️ MongoDB connection not available for database analysis")
        
        # Step 4: Check bills/transactions for similar issues
        print(f"\n🔍 STEP 4: Checking Bills/Transactions for Similar Issues")
        print("=" * 60)
        
        # Test bills endpoint
        bills_success, bills_response = self.run_test(
            "Get Bills for ID Analysis",
            "GET",
            "bills?limit=10",
            200
        )
        
        if bills_success and bills_response:
            print(f"✅ Found {len(bills_response)} bills")
            
            # Analyze bill ID formats
            bill_id_formats = {"uuid": 0, "objectid": 0, "other": 0}
            
            for bill in bills_response[:5]:
                bill_id = bill.get('id', '')
                if len(bill_id) == 36 and bill_id.count('-') == 4:
                    bill_id_formats["uuid"] += 1
                elif len(bill_id) == 24 and all(c in '0123456789abcdef' for c in bill_id.lower()):
                    bill_id_formats["objectid"] += 1
                else:
                    bill_id_formats["other"] += 1
            
            print(f"   Bill ID formats: UUID={bill_id_formats['uuid']}, ObjectId={bill_id_formats['objectid']}, Other={bill_id_formats['other']}")
            
            # Test individual bill lookup if endpoint exists
            if bills_response:
                test_bill_id = bills_response[0].get('id')
                # Note: There might not be a GET /bills/{id} endpoint, so we'll test if it exists
                try:
                    bill_lookup_success, bill_lookup_response = self.run_test(
                        f"Individual Bill Lookup Test",
                        "GET",
                        f"bills/{test_bill_id}",
                        200
                    )
                    
                    if bill_lookup_success:
                        print(f"   ✅ Individual bill lookup working")
                    else:
                        print(f"   ⚠️ Individual bill lookup endpoint may not exist or has issues")
                except:
                    print(f"   ⚠️ Individual bill lookup endpoint not available")
            
            test_results["bills_transactions_check"]["bills_working"] = bills_success
        
        # Test credit cards endpoint
        credit_cards_success, credit_cards_response = self.run_test(
            "Get Credit Cards for ID Analysis",
            "GET",
            "credit-cards?limit=5",
            200
        )
        
        if credit_cards_success and credit_cards_response:
            print(f"✅ Found {len(credit_cards_response)} credit cards")
            
            # Test individual credit card lookup
            if credit_cards_response:
                test_card_id = credit_cards_response[0].get('id')
                card_lookup_success, card_lookup_response = self.run_test(
                    f"Individual Credit Card Lookup Test",
                    "GET",
                    f"credit-cards/{test_card_id}",
                    200
                )
                
                if card_lookup_success:
                    print(f"   ✅ Individual credit card lookup working")
                else:
                    print(f"   ❌ Individual credit card lookup failing - similar issue to customers!")
            
            test_results["bills_transactions_check"]["credit_cards_working"] = credit_cards_success
        
        # Step 5: Final Analysis and Recommendations
        print(f"\n📊 STEP 5: Final Analysis and Recommendations")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"🔍 CRITICAL VERIFICATION RESULTS:")
        print(f"   Target Customer 68b86b157a314c251c8c863b: {'✅ WORKING' if test_results['target_customer_working'] else '❌ STILL FAILING'}")
        print(f"   Other customers compatibility: {test_results['other_customers_working']}/5 working")
        print(f"   Overall success rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        print(f"\n🔍 ROOT CAUSE ANALYSIS:")
        if test_results["database_analysis"]:
            analysis = test_results["database_analysis"]
            print(f"   Mixed ID format customers: {analysis['mixed_customers']}")
            print(f"   Target customer in mixed category: {'Yes' if analysis['target_in_mixed'] else 'No'}")
            
            if analysis['mixed_customers'] > 0:
                print(f"   🚨 ISSUE: Database has {analysis['mixed_customers']} customers with mixed ID formats")
                print(f"   💡 SOLUTION: Backend now queries both 'id' and '_id' fields")
        
        print(f"\n🔍 BILLS/TRANSACTIONS IMPACT:")
        bills_check = test_results["bills_transactions_check"]
        print(f"   Bills endpoint: {'✅ Working' if bills_check.get('bills_working') else '❌ Issues detected'}")
        print(f"   Credit cards endpoint: {'✅ Working' if bills_check.get('credit_cards_working') else '❌ Issues detected'}")
        
        # Final recommendation
        if test_results["target_customer_working"] and test_results["other_customers_working"] >= 4:
            print(f"\n✅ CONCLUSION: Customer lookup fix is working correctly!")
            print(f"   - Target customer now accessible")
            print(f"   - Compatibility maintained with other customers")
            print(f"   - Mixed ObjectId/UUID issue resolved")
            return True
        else:
            print(f"\n❌ CONCLUSION: Customer lookup fix needs more work")
            print(f"   - Target customer: {'Working' if test_results['target_customer_working'] else 'Still failing'}")
            print(f"   - Compatibility issues detected")
            return False

    def run_all_tests(self):
        """Run all tests for the review request"""
        print(f"\n🚀 STARTING CUSTOMER LOOKUP FIX TESTING")
        print("=" * 80)
        print(f"🎯 Review Request: Test customer lookup fix và phân tích ObjectId vs UUID issue")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API Base URL: {self.base_url}")
        
        # Run the main test
        success = self.test_customer_lookup_fix_verification()
        
        # Print final summary
        print(f"\n📊 FINAL TEST SUMMARY")
        print("=" * 50)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if success:
            print(f"\n✅ OVERALL RESULT: Customer lookup fix verification PASSED")
            print(f"   - Customer ID 68b86b157a314c251c8c863b is now working")
            print(f"   - Other customers remain compatible")
            print(f"   - ObjectId vs UUID issue has been resolved")
        else:
            print(f"\n❌ OVERALL RESULT: Customer lookup fix verification FAILED")
            print(f"   - Further investigation needed")
            print(f"   - Check backend implementation")
        
        return success

if __name__ == "__main__":
    tester = FPTBillManagerAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)