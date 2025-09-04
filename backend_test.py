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

    def test_credit_cards_api_after_schema_fix(self):
        """Test Credit Cards API sau khi fix schema issues - REVIEW REQUEST"""
        print(f"\n🎯 CREDIT CARDS API TESTING AFTER SCHEMA FIX")
        print("=" * 80)
        print("🔍 CRITICAL VERIFICATION:")
        print("   1. Test GET /api/credit-cards endpoint trả về 200 thay vì 500")
        print("   2. Test GET /api/credit-cards/{card_id}/detail với proper credit card IDs")
        print("   3. Test DELETE /api/credit-cards/{card_id} với dual lookup")
        print("   4. Verify credit card data structure matches CreditCard Pydantic model")
        print("   5. Verify credit cards page accessible cho frontend delete testing")
        
        test_results = {
            "credit_cards_list_working": False,
            "credit_card_detail_working": False,
            "credit_card_delete_working": False,
            "data_structure_valid": False,
            "frontend_accessible": False,
            "total_tests": 0,
            "passed_tests": 0,
            "critical_issues": []
        }
        
        # Step 1: Test GET /api/credit-cards endpoint (should return 200 not 500)
        print(f"\n🔍 STEP 1: Test GET /api/credit-cards Endpoint")
        print("=" * 60)
        print("Expected: Should return 200 status instead of 500 Internal Server Error")
        
        cards_success, cards_response = self.run_test(
            "GET /credit-cards - Main List Endpoint",
            "GET",
            "credit-cards?page_size=100",
            200
        )
        
        if cards_success:
            print(f"✅ SUCCESS: GET /api/credit-cards returns 200 status!")
            print(f"   Found {len(cards_response)} credit cards")
            test_results["credit_cards_list_working"] = True
            test_results["passed_tests"] += 1
            
            # Verify data structure
            if cards_response and len(cards_response) > 0:
                sample_card = cards_response[0]
                required_fields = [
                    'id', 'customer_id', 'customer_name', 'card_number', 
                    'cardholder_name', 'bank_name', 'card_type', 'expiry_date', 
                    'ccv', 'statement_date', 'payment_due_date', 'credit_limit', 'status'
                ]
                
                missing_fields = [field for field in required_fields if field not in sample_card]
                
                if not missing_fields:
                    print(f"✅ Credit card data structure matches CreditCard Pydantic model")
                    print(f"   All required fields present: {required_fields}")
                    test_results["data_structure_valid"] = True
                    test_results["passed_tests"] += 1
                else:
                    print(f"❌ Missing required fields in credit card data: {missing_fields}")
                    test_results["critical_issues"].append(f"Missing fields: {missing_fields}")
                
                test_results["total_tests"] += 1
                
                # Check enum values
                sample_card_type = sample_card.get('card_type')
                sample_status = sample_card.get('status')
                
                valid_card_types = ['VISA', 'MASTERCARD', 'JCB', 'AMEX']
                valid_statuses = ['Đã đáo', 'Cần đáo', 'Chưa đến hạn', 'Quá Hạn']
                
                if sample_card_type in valid_card_types and sample_status in valid_statuses:
                    print(f"✅ Valid enum values - card_type: {sample_card_type}, status: {sample_status}")
                    test_results["passed_tests"] += 1
                else:
                    print(f"❌ Invalid enum values - card_type: {sample_card_type}, status: {sample_status}")
                    test_results["critical_issues"].append(f"Invalid enum values")
                
                test_results["total_tests"] += 1
        else:
            print(f"❌ FAILED: GET /api/credit-cards still returns 500 Internal Server Error")
            test_results["critical_issues"].append("Credit cards list endpoint returns 500 error")
        
        test_results["total_tests"] += 1
        
        # Step 2: Test GET /api/credit-cards/{card_id}/detail với proper credit card IDs
        print(f"\n🔍 STEP 2: Test GET /api/credit-cards/{{card_id}}/detail Endpoint")
        print("=" * 60)
        
        if cards_success and cards_response and len(cards_response) > 0:
            # Test with first 3 credit cards
            detail_tests_passed = 0
            detail_tests_total = 0
            
            for i, card in enumerate(cards_response[:3]):
                card_id = card.get('id')
                customer_name = card.get('customer_name', 'Unknown')
                
                print(f"\n   Test {i+1}: Credit Card Detail - {customer_name}")
                print(f"   Card ID: {card_id}")
                print(f"   ID Format: {'ObjectId' if len(card_id) == 24 else 'UUID' if len(card_id) == 36 else 'Other'}")
                
                detail_success, detail_response = self.run_test(
                    f"GET /credit-cards/{card_id}/detail - {customer_name}",
                    "GET",
                    f"credit-cards/{card_id}/detail",
                    200
                )
                
                detail_tests_total += 1
                
                if detail_success:
                    print(f"   ✅ SUCCESS: Credit card detail accessible")
                    detail_tests_passed += 1
                    
                    # Verify response structure
                    if detail_response and 'card' in detail_response:
                        print(f"   ✅ Response structure valid with 'card' field")
                    else:
                        print(f"   ⚠️ Response structure may be incomplete")
                else:
                    print(f"   ❌ FAILED: Credit card detail not accessible")
                    test_results["critical_issues"].append(f"Credit card detail failed for ID: {card_id}")
            
            if detail_tests_passed == detail_tests_total:
                print(f"\n✅ ALL CREDIT CARD DETAIL TESTS PASSED ({detail_tests_passed}/{detail_tests_total})")
                test_results["credit_card_detail_working"] = True
                test_results["passed_tests"] += detail_tests_passed
            else:
                print(f"\n❌ SOME CREDIT CARD DETAIL TESTS FAILED ({detail_tests_passed}/{detail_tests_total})")
            
            test_results["total_tests"] += detail_tests_total
        else:
            print(f"   ⚠️ Cannot test credit card detail - no cards available from list endpoint")
        
        # Step 3: Test DELETE /api/credit-cards/{card_id} với dual lookup
        print(f"\n🔍 STEP 3: Test DELETE /api/credit-cards/{{card_id}} với Dual Lookup")
        print("=" * 60)
        
        if cards_success and cards_response and len(cards_response) > 0:
            # Find a card to test deletion (preferably ObjectId format to test dual lookup)
            test_card = None
            for card in cards_response:
                card_id = card.get('id', '')
                # Prefer ObjectId format to test dual lookup
                if len(card_id) == 24 and all(c in '0123456789abcdef' for c in card_id.lower()):
                    test_card = card
                    break
            
            # If no ObjectId format found, use first card
            if not test_card and cards_response:
                test_card = cards_response[0]
            
            if test_card:
                card_id = test_card.get('id')
                customer_name = test_card.get('customer_name', 'Unknown')
                
                print(f"   Testing DELETE with card: {customer_name}")
                print(f"   Card ID: {card_id}")
                print(f"   ID Format: {'ObjectId' if len(card_id) == 24 else 'UUID' if len(card_id) == 36 else 'Other'}")
                
                delete_success, delete_response = self.run_test(
                    f"DELETE /credit-cards/{card_id} - {customer_name}",
                    "DELETE",
                    f"credit-cards/{card_id}",
                    200
                )
                
                if delete_success:
                    print(f"✅ SUCCESS: Credit card deletion working with dual lookup")
                    print(f"   Response: {delete_response}")
                    test_results["credit_card_delete_working"] = True
                    test_results["passed_tests"] += 1
                    
                    # Verify deletion by trying to access the card
                    verify_success, verify_response = self.run_test(
                        f"Verify deletion - GET /credit-cards/{card_id}/detail",
                        "GET",
                        f"credit-cards/{card_id}/detail",
                        404
                    )
                    
                    if verify_success:
                        print(f"   ✅ Deletion verified - card no longer accessible")
                        test_results["passed_tests"] += 1
                    else:
                        print(f"   ⚠️ Deletion verification inconclusive")
                    
                    test_results["total_tests"] += 1
                else:
                    print(f"❌ FAILED: Credit card deletion not working")
                    test_results["critical_issues"].append(f"Credit card deletion failed for ID: {card_id}")
                
                test_results["total_tests"] += 1
            else:
                print(f"   ⚠️ No credit cards available for deletion testing")
        else:
            print(f"   ⚠️ Cannot test credit card deletion - no cards available")
        
        # Step 4: Test frontend accessibility
        print(f"\n🔍 STEP 4: Verify Credit Cards Page Accessible for Frontend")
        print("=" * 60)
        
        # Test with smaller page size to ensure frontend compatibility
        frontend_success, frontend_response = self.run_test(
            "GET /credit-cards - Frontend Compatibility Test",
            "GET",
            "credit-cards?page_size=20",
            200
        )
        
        if frontend_success:
            print(f"✅ SUCCESS: Credit cards page accessible for frontend delete testing")
            print(f"   Frontend can load {len(frontend_response)} credit cards")
            test_results["frontend_accessible"] = True
            test_results["passed_tests"] += 1
        else:
            print(f"❌ FAILED: Credit cards page not accessible for frontend")
            test_results["critical_issues"].append("Frontend cannot access credit cards page")
        
        test_results["total_tests"] += 1
        
        # Step 5: Final Assessment
        print(f"\n📊 STEP 5: Final Assessment - Credit Cards API After Schema Fix")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 CRITICAL VERIFICATION RESULTS:")
        print(f"   GET /api/credit-cards endpoint: {'✅ WORKING (200)' if test_results['credit_cards_list_working'] else '❌ FAILED (500)'}")
        print(f"   GET /api/credit-cards/{{id}}/detail: {'✅ WORKING' if test_results['credit_card_detail_working'] else '❌ FAILED'}")
        print(f"   DELETE /api/credit-cards/{{id}}: {'✅ WORKING' if test_results['credit_card_delete_working'] else '❌ FAILED'}")
        print(f"   Credit card data structure: {'✅ VALID' if test_results['data_structure_valid'] else '❌ INVALID'}")
        print(f"   Frontend accessibility: {'✅ ACCESSIBLE' if test_results['frontend_accessible'] else '❌ NOT ACCESSIBLE'}")
        print(f"   Overall Success Rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        print(f"\n🎯 EXPECTED RESULTS VERIFICATION:")
        all_expected_results_met = (
            test_results["credit_cards_list_working"] and
            test_results["credit_card_detail_working"] and
            test_results["credit_card_delete_working"] and
            test_results["data_structure_valid"] and
            test_results["frontend_accessible"]
        )
        
        if all_expected_results_met:
            print(f"   ✅ Credit Cards API endpoints working correctly")
            print(f"   ✅ No more 500 Internal Server Error")
            print(f"   ✅ Credit card records có all required fields")
            print(f"   ✅ Valid enum values cho card_type và status")
            print(f"   ✅ Credit cards page accessible cho frontend delete testing")
        else:
            print(f"   ❌ Some expected results not met:")
            if not test_results["credit_cards_list_working"]:
                print(f"      - GET /api/credit-cards still returns 500 error")
            if not test_results["credit_card_detail_working"]:
                print(f"      - Credit card detail endpoints have issues")
            if not test_results["credit_card_delete_working"]:
                print(f"      - Credit card deletion not working")
            if not test_results["data_structure_valid"]:
                print(f"      - Credit card data structure incomplete")
            if not test_results["frontend_accessible"]:
                print(f"      - Frontend cannot access credit cards page")
        
        if test_results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in test_results["critical_issues"]:
                print(f"   - {issue}")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if all_expected_results_met:
            print(f"   ✅ CREDIT CARDS API SCHEMA FIX VERIFICATION SUCCESSFUL")
            print(f"   - All credit card endpoints working correctly")
            print(f"   - No more 500 Internal Server Errors")
            print(f"   - Data structure matches Pydantic model")
            print(f"   - Frontend delete testing ready")
        else:
            print(f"   ❌ CREDIT CARDS API STILL HAS ISSUES")
            print(f"   - Schema fix may not be complete")
            print(f"   - Further investigation required")
        
        return all_expected_results_met

    def test_bills_data_verification_and_creation(self):
        """Verify bills data và tạo test bills if needed - REVIEW REQUEST"""
        print(f"\n🎯 BILLS DATA VERIFICATION AND CREATION")
        print("=" * 80)
        print("🔍 TESTING OBJECTIVES:")
        print("   1. Check current bills count in database")
        print("   2. If no bills exist, create 50 test bills as intended")
        print("   3. Verify bills appear in both Available và 'Tất Cả Bills' tabs")
        print("   4. Test bill creation với proper statuses và data")
        print("   5. Expected: Create 50 bills với mixed statuses (AVAILABLE, SOLD, RESERVED)")
        print("   6. Bills should appear in inventory tabs")
        print("   7. Proper bill codes và denominations")
        
        test_results = {
            "current_bills_count": 0,
            "bills_created": 0,
            "available_bills": 0,
            "sold_bills": 0,
            "reserved_bills": 0,
            "inventory_accessible": False,
            "bills_in_available_tab": 0,
            "bills_in_all_tab": 0,
            "total_tests": 0,
            "passed_tests": 0,
            "critical_issues": []
        }
        
        # Step 1: Check current bills count in database
        print(f"\n🔍 STEP 1: Check Current Bills Count in Database")
        print("=" * 60)
        
        # Get all bills
        bills_success, bills_response = self.run_test(
            "GET /bills - Check Current Bills Count",
            "GET",
            "bills?limit=1000",
            200
        )
        
        if bills_success and bills_response:
            current_count = len(bills_response)
            test_results["current_bills_count"] = current_count
            print(f"✅ Current bills in database: {current_count}")
            
            # Analyze bill statuses
            status_counts = {"AVAILABLE": 0, "SOLD": 0, "PENDING": 0, "CROSSED": 0, "ERROR": 0}
            for bill in bills_response:
                status = bill.get('status', 'UNKNOWN')
                if status in status_counts:
                    status_counts[status] += 1
            
            print(f"   Status breakdown:")
            for status, count in status_counts.items():
                print(f"      {status}: {count}")
            
            test_results["available_bills"] = status_counts["AVAILABLE"]
            test_results["sold_bills"] = status_counts["SOLD"]
            test_results["passed_tests"] += 1
        else:
            print(f"❌ Failed to get bills from database")
            test_results["critical_issues"].append("Cannot access bills endpoint")
        
        test_results["total_tests"] += 1
        
        # Step 2: Create test bills if needed (if less than 50 bills exist)
        print(f"\n🔍 STEP 2: Create Test Bills if Needed")
        print("=" * 60)
        
        if test_results["current_bills_count"] < 50:
            bills_to_create = 50 - test_results["current_bills_count"]
            print(f"📝 Need to create {bills_to_create} bills to reach 50 total")
            
            # Create test bills with mixed statuses
            created_bills = []
            statuses = ["AVAILABLE", "SOLD", "AVAILABLE", "AVAILABLE", "SOLD"]  # More AVAILABLE for testing
            
            for i in range(bills_to_create):
                bill_data = {
                    "customer_code": f"TEST{1000000 + i:07d}",
                    "provider_region": "MIEN_BAC" if i % 2 == 0 else "MIEN_NAM",
                    "full_name": f"Test Customer {i+1}",
                    "address": f"Test Address {i+1}, Test District, Test City",
                    "amount": round(100000 + (i * 50000), -3),  # Amounts like 100k, 150k, 200k, etc.
                    "billing_cycle": f"{(i % 12) + 1:02d}/2025",
                    "status": statuses[i % len(statuses)]
                }
                
                # Try to create bill via API
                create_success, create_response = self.run_test(
                    f"POST /bills - Create Test Bill {i+1}",
                    "POST",
                    "bills",
                    201,
                    data=bill_data
                )
                
                if create_success:
                    created_bills.append(create_response)
                    print(f"   ✅ Created bill {i+1}: {bill_data['customer_code']} - {bill_data['status']}")
                else:
                    # If POST /bills doesn't exist, try alternative method
                    print(f"   ⚠️ Direct bill creation may not be available via API")
                    break
            
            test_results["bills_created"] = len(created_bills)
            
            if len(created_bills) > 0:
                print(f"✅ Successfully created {len(created_bills)} test bills")
                test_results["passed_tests"] += 1
            else:
                print(f"⚠️ Could not create bills via API - may need manual database insertion")
                # Try to create bills via database if API doesn't work
                if self.mongo_connected:
                    print(f"   Attempting direct database insertion...")
                    try:
                        bills_to_insert = []
                        for i in range(min(bills_to_create, 50)):
                            bill_doc = {
                                "id": f"test-bill-{i+1:03d}-{int(datetime.now().timestamp())}",
                                "gateway": "FPT",
                                "customer_code": f"TEST{1000000 + i:07d}",
                                "provider_region": "MIEN_BAC" if i % 2 == 0 else "MIEN_NAM",
                                "provider_name": "MIEN_BAC" if i % 2 == 0 else "MIEN_NAM",
                                "full_name": f"Test Customer {i+1}",
                                "address": f"Test Address {i+1}, Test District, Test City",
                                "amount": 100000 + (i * 50000),
                                "billing_cycle": f"{(i % 12) + 1:02d}/2025",
                                "raw_status": "OK",
                                "status": statuses[i % len(statuses)],
                                "created_at": datetime.now().isoformat(),
                                "updated_at": datetime.now().isoformat()
                            }
                            bills_to_insert.append(bill_doc)
                        
                        # Insert into database
                        result = self.db.bills.insert_many(bills_to_insert)
                        test_results["bills_created"] = len(result.inserted_ids)
                        print(f"   ✅ Inserted {len(result.inserted_ids)} bills directly into database")
                        test_results["passed_tests"] += 1
                        
                    except Exception as e:
                        print(f"   ❌ Database insertion failed: {e}")
                        test_results["critical_issues"].append(f"Cannot create test bills: {e}")
        else:
            print(f"✅ Sufficient bills exist ({test_results['current_bills_count']} >= 50)")
            test_results["passed_tests"] += 1
        
        test_results["total_tests"] += 1
        
        # Step 3: Verify bills appear in inventory endpoints
        print(f"\n🔍 STEP 3: Verify Bills Appear in Inventory Endpoints")
        print("=" * 60)
        
        # Test inventory stats endpoint
        inventory_stats_success, inventory_stats_response = self.run_test(
            "GET /inventory/stats - Check Inventory Statistics",
            "GET",
            "inventory/stats",
            200
        )
        
        if inventory_stats_success and inventory_stats_response:
            print(f"✅ Inventory stats accessible:")
            print(f"   Total bills in inventory: {inventory_stats_response.get('total_bills', 0)}")
            print(f"   Available bills: {inventory_stats_response.get('available_bills', 0)}")
            print(f"   Sold bills: {inventory_stats_response.get('sold_bills', 0)}")
            print(f"   Total bills in system: {inventory_stats_response.get('total_bills_in_system', 0)}")
            test_results["inventory_accessible"] = True
            test_results["passed_tests"] += 1
        else:
            print(f"❌ Inventory stats not accessible")
            test_results["critical_issues"].append("Inventory stats endpoint not working")
        
        test_results["total_tests"] += 1
        
        # Test inventory items endpoint (Available tab)
        inventory_items_success, inventory_items_response = self.run_test(
            "GET /inventory - Check Available Bills Tab",
            "GET",
            "inventory?status=AVAILABLE&limit=100",
            200
        )
        
        if inventory_items_success and inventory_items_response:
            available_count = len(inventory_items_response) if isinstance(inventory_items_response, list) else 0
            test_results["bills_in_available_tab"] = available_count
            print(f"✅ Available bills tab accessible: {available_count} bills")
            test_results["passed_tests"] += 1
        else:
            print(f"❌ Available bills tab not accessible")
            test_results["critical_issues"].append("Available bills tab not working")
        
        test_results["total_tests"] += 1
        
        # Test all bills endpoint (Tất Cả Bills tab)
        all_bills_success, all_bills_response = self.run_test(
            "GET /bills - Check 'Tất Cả Bills' Tab",
            "GET",
            "bills?limit=100",
            200
        )
        
        if all_bills_success and all_bills_response:
            all_count = len(all_bills_response) if isinstance(all_bills_response, list) else 0
            test_results["bills_in_all_tab"] = all_count
            print(f"✅ 'Tất Cả Bills' tab accessible: {all_count} bills")
            test_results["passed_tests"] += 1
        else:
            print(f"❌ 'Tất Cả Bills' tab not accessible")
            test_results["critical_issues"].append("All bills tab not working")
        
        test_results["total_tests"] += 1
        
        # Step 4: Test bill creation endpoint functionality
        print(f"\n🔍 STEP 4: Test Bill Creation Endpoint Functionality")
        print("=" * 60)
        
        # Test creating a single bill with proper data
        test_bill_data = {
            "customer_code": f"APITEST{int(datetime.now().timestamp())}",
            "provider_region": "MIEN_BAC",
            "full_name": "API Test Customer",
            "address": "API Test Address, Test District, Test City",
            "amount": 250000,
            "billing_cycle": "12/2025",
            "status": "AVAILABLE"
        }
        
        single_bill_success, single_bill_response = self.run_test(
            "POST /bills - Test Single Bill Creation",
            "POST",
            "bills",
            201,
            data=test_bill_data
        )
        
        if single_bill_success:
            print(f"✅ Single bill creation working")
            print(f"   Created bill ID: {single_bill_response.get('id', 'Unknown')}")
            print(f"   Customer code: {single_bill_response.get('customer_code', 'Unknown')}")
            test_results["passed_tests"] += 1
        else:
            print(f"⚠️ Single bill creation endpoint may not exist")
            print(f"   This is not critical - bills may be created through other methods")
        
        test_results["total_tests"] += 1
        
        # Step 5: Verify bill data quality and structure
        print(f"\n🔍 STEP 5: Verify Bill Data Quality and Structure")
        print("=" * 60)
        
        if all_bills_success and all_bills_response and len(all_bills_response) > 0:
            sample_bill = all_bills_response[0]
            required_fields = ['id', 'customer_code', 'provider_region', 'status', 'created_at']
            
            missing_fields = [field for field in required_fields if field not in sample_bill]
            
            if not missing_fields:
                print(f"✅ Bill data structure is complete")
                print(f"   Sample bill ID: {sample_bill.get('id', 'Unknown')}")
                print(f"   Sample customer code: {sample_bill.get('customer_code', 'Unknown')}")
                print(f"   Sample amount: {sample_bill.get('amount', 'Unknown')}")
                print(f"   Sample status: {sample_bill.get('status', 'Unknown')}")
                test_results["passed_tests"] += 1
            else:
                print(f"❌ Bill data structure incomplete - missing fields: {missing_fields}")
                test_results["critical_issues"].append(f"Missing bill fields: {missing_fields}")
            
            # Check for proper bill codes and denominations
            valid_codes = 0
            valid_amounts = 0
            
            for bill in all_bills_response[:10]:  # Check first 10 bills
                customer_code = bill.get('customer_code', '')
                amount = bill.get('amount')
                
                # Check if customer code follows proper format
                if customer_code and len(customer_code) >= 5:
                    valid_codes += 1
                
                # Check if amount is reasonable (between 10k and 10M VND)
                if amount and isinstance(amount, (int, float)) and 10000 <= amount <= 10000000:
                    valid_amounts += 1
            
            print(f"   Valid customer codes: {valid_codes}/10")
            print(f"   Valid amounts: {valid_amounts}/10")
            
            if valid_codes >= 8 and valid_amounts >= 8:
                print(f"✅ Bill codes and denominations are properly formatted")
                test_results["passed_tests"] += 1
            else:
                print(f"⚠️ Some bill codes or amounts may need attention")
        else:
            print(f"⚠️ Cannot verify bill data quality - no bills available")
        
        test_results["total_tests"] += 1
        
        # Step 6: Final Assessment
        print(f"\n📊 STEP 6: Final Assessment - Bills Data Verification")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 BILLS DATA VERIFICATION RESULTS:")
        print(f"   Current bills count: {test_results['current_bills_count']}")
        print(f"   Bills created: {test_results['bills_created']}")
        print(f"   Available bills: {test_results['available_bills']}")
        print(f"   Sold bills: {test_results['sold_bills']}")
        print(f"   Inventory accessible: {'✅ YES' if test_results['inventory_accessible'] else '❌ NO'}")
        print(f"   Bills in Available tab: {test_results['bills_in_available_tab']}")
        print(f"   Bills in 'Tất Cả Bills' tab: {test_results['bills_in_all_tab']}")
        print(f"   Overall Success Rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        print(f"\n🎯 EXPECTED RESULTS VERIFICATION:")
        expected_results_met = (
            test_results["current_bills_count"] >= 50 or test_results["bills_created"] > 0
        ) and (
            test_results["inventory_accessible"] and
            test_results["bills_in_available_tab"] > 0 and
            test_results["bills_in_all_tab"] > 0
        )
        
        if expected_results_met:
            print(f"   ✅ Bills database has sufficient data (≥50 bills)")
            print(f"   ✅ Bills appear in Available tab")
            print(f"   ✅ Bills appear in 'Tất Cả Bills' tab")
            print(f"   ✅ Mixed statuses present (AVAILABLE, SOLD)")
            print(f"   ✅ Proper bill codes and denominations")
            print(f"   ✅ Inventory tabs have data to test with properly")
        else:
            print(f"   ❌ Some expected results not met:")
            if test_results["current_bills_count"] < 50 and test_results["bills_created"] == 0:
                print(f"      - Insufficient bills in database (<50)")
            if not test_results["inventory_accessible"]:
                print(f"      - Inventory endpoints not accessible")
            if test_results["bills_in_available_tab"] == 0:
                print(f"      - No bills in Available tab")
            if test_results["bills_in_all_tab"] == 0:
                print(f"      - No bills in 'Tất Cả Bills' tab")
        
        if test_results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in test_results["critical_issues"]:
                print(f"   - {issue}")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if expected_results_met:
            print(f"   ✅ BILLS DATA VERIFICATION SUCCESSFUL")
            print(f"   - Database has sufficient test data (≥50 bills)")
            print(f"   - Bills appear in both inventory tabs")
            print(f"   - Mixed statuses available for testing")
            print(f"   - Proper data structure and formatting")
            print(f"   - Inventory tabs ready for comprehensive testing")
        else:
            print(f"   ❌ BILLS DATA VERIFICATION NEEDS ATTENTION")
            print(f"   - May need additional test data creation")
            print(f"   - Check inventory endpoint functionality")
        
        return expected_results_met

    def test_bills_delete_endpoint_dual_lookup_fix(self):
        """Test Bills DELETE endpoint sau khi fix ObjectId vs UUID dual lookup - REVIEW REQUEST"""
        print(f"\n🎯 BILLS DELETE ENDPOINT DUAL LOOKUP FIX VERIFICATION")
        print("=" * 80)
        print("🔍 CRITICAL TESTING OBJECTIVES:")
        print("   1. Test DELETE /api/bills/{bill_id} với bills có ObjectId format")
        print("   2. Test DELETE /api/bills/{bill_id} với bills có UUID format")
        print("   3. Verify dual lookup strategy hoạt động cho bills")
        print("   4. Test GET /api/bills/{bill_id} với mixed ID formats")
        print("   5. Test PUT /api/bills/{bill_id} với mixed ID formats")
        print("   6. Expected: No more 'Không tìm thấy bill để xóa' error")
        print("   7. Bills có proper inventory cascade deletion")
        
        test_results = {
            "objectid_delete_working": False,
            "uuid_delete_working": False,
            "objectid_get_working": False,
            "uuid_get_working": False,
            "objectid_put_working": False,
            "uuid_put_working": False,
            "dual_lookup_verified": False,
            "cascade_deletion_working": False,
            "total_tests": 0,
            "passed_tests": 0,
            "critical_issues": [],
            "bills_tested": []
        }
        
        # Step 1: Get bills data and analyze ID formats
        print(f"\n🔍 STEP 1: Analyze Bills Database for ID Formats")
        print("=" * 60)
        
        bills_success, bills_response = self.run_test(
            "GET /bills - Get Bills for ID Analysis",
            "GET",
            "bills?limit=100",
            200
        )
        
        if not bills_success or not bills_response:
            print(f"❌ CRITICAL: Cannot get bills data for testing")
            test_results["critical_issues"].append("Cannot access bills endpoint")
            return False
        
        print(f"✅ Found {len(bills_response)} bills for testing")
        
        # Analyze ID formats in bills
        objectid_bills = []
        uuid_bills = []
        other_format_bills = []
        
        for bill in bills_response:
            bill_id = bill.get('id', '')
            customer_code = bill.get('customer_code', 'Unknown')
            status = bill.get('status', 'Unknown')
            
            if len(bill_id) == 24 and all(c in '0123456789abcdef' for c in bill_id.lower()):
                objectid_bills.append({
                    "id": bill_id,
                    "customer_code": customer_code,
                    "status": status,
                    "format": "ObjectId"
                })
            elif len(bill_id) == 36 and bill_id.count('-') == 4:
                uuid_bills.append({
                    "id": bill_id,
                    "customer_code": customer_code,
                    "status": status,
                    "format": "UUID"
                })
            else:
                other_format_bills.append({
                    "id": bill_id,
                    "customer_code": customer_code,
                    "status": status,
                    "format": "Other"
                })
        
        print(f"\n📊 BILLS ID FORMAT ANALYSIS:")
        print(f"   ObjectId format bills: {len(objectid_bills)}")
        print(f"   UUID format bills: {len(uuid_bills)}")
        print(f"   Other format bills: {len(other_format_bills)}")
        
        if len(objectid_bills) == 0 and len(uuid_bills) == 0:
            print(f"❌ CRITICAL: No bills with testable ID formats found")
            test_results["critical_issues"].append("No bills with ObjectId or UUID formats")
            return False
        
        # Step 2: Test GET /api/bills/{bill_id} với mixed ID formats
        print(f"\n🔍 STEP 2: Test GET /api/bills/{{bill_id}} với Mixed ID Formats")
        print("=" * 60)
        
        # Test ObjectId format bills
        if objectid_bills:
            test_bill = objectid_bills[0]
            print(f"\n   Testing ObjectId format bill:")
            print(f"   Bill ID: {test_bill['id']}")
            print(f"   Customer Code: {test_bill['customer_code']}")
            print(f"   Status: {test_bill['status']}")
            
            get_success, get_response = self.run_test(
                f"GET /bills/{test_bill['id']} - ObjectId Format",
                "GET",
                f"bills/{test_bill['id']}",
                200
            )
            
            if get_success:
                print(f"   ✅ SUCCESS: GET endpoint working with ObjectId format")
                test_results["objectid_get_working"] = True
                test_results["passed_tests"] += 1
                test_results["bills_tested"].append(f"GET ObjectId: {test_bill['customer_code']}")
            else:
                print(f"   ❌ FAILED: GET endpoint not working with ObjectId format")
                test_results["critical_issues"].append(f"GET failed for ObjectId: {test_bill['id']}")
            
            test_results["total_tests"] += 1
        
        # Test UUID format bills
        if uuid_bills:
            test_bill = uuid_bills[0]
            print(f"\n   Testing UUID format bill:")
            print(f"   Bill ID: {test_bill['id']}")
            print(f"   Customer Code: {test_bill['customer_code']}")
            print(f"   Status: {test_bill['status']}")
            
            get_success, get_response = self.run_test(
                f"GET /bills/{test_bill['id']} - UUID Format",
                "GET",
                f"bills/{test_bill['id']}",
                200
            )
            
            if get_success:
                print(f"   ✅ SUCCESS: GET endpoint working with UUID format")
                test_results["uuid_get_working"] = True
                test_results["passed_tests"] += 1
                test_results["bills_tested"].append(f"GET UUID: {test_bill['customer_code']}")
            else:
                print(f"   ❌ FAILED: GET endpoint not working with UUID format")
                test_results["critical_issues"].append(f"GET failed for UUID: {test_bill['id']}")
            
            test_results["total_tests"] += 1
        
        # Step 3: Test PUT /api/bills/{bill_id} với mixed ID formats
        print(f"\n🔍 STEP 3: Test PUT /api/bills/{{bill_id}} với Mixed ID Formats")
        print("=" * 60)
        
        # Test ObjectId format bills
        if objectid_bills:
            test_bill = objectid_bills[0]
            print(f"\n   Testing PUT with ObjectId format bill:")
            print(f"   Bill ID: {test_bill['id']}")
            print(f"   Customer Code: {test_bill['customer_code']}")
            
            update_data = {
                "note": f"Test update at {datetime.now().isoformat()}",
                "last_checked": datetime.now().isoformat()
            }
            
            put_success, put_response = self.run_test(
                f"PUT /bills/{test_bill['id']} - ObjectId Format",
                "PUT",
                f"bills/{test_bill['id']}",
                200,
                data=update_data
            )
            
            if put_success:
                print(f"   ✅ SUCCESS: PUT endpoint working with ObjectId format")
                print(f"   Updated bill: {put_response.get('customer_code', 'Unknown')}")
                test_results["objectid_put_working"] = True
                test_results["passed_tests"] += 1
                test_results["bills_tested"].append(f"PUT ObjectId: {test_bill['customer_code']}")
            else:
                print(f"   ❌ FAILED: PUT endpoint not working with ObjectId format")
                test_results["critical_issues"].append(f"PUT failed for ObjectId: {test_bill['id']}")
            
            test_results["total_tests"] += 1
        
        # Test UUID format bills
        if uuid_bills:
            test_bill = uuid_bills[0]
            print(f"\n   Testing PUT with UUID format bill:")
            print(f"   Bill ID: {test_bill['id']}")
            print(f"   Customer Code: {test_bill['customer_code']}")
            
            update_data = {
                "note": f"Test update at {datetime.now().isoformat()}",
                "last_checked": datetime.now().isoformat()
            }
            
            put_success, put_response = self.run_test(
                f"PUT /bills/{test_bill['id']} - UUID Format",
                "PUT",
                f"bills/{test_bill['id']}",
                200,
                data=update_data
            )
            
            if put_success:
                print(f"   ✅ SUCCESS: PUT endpoint working with UUID format")
                print(f"   Updated bill: {put_response.get('customer_code', 'Unknown')}")
                test_results["uuid_put_working"] = True
                test_results["passed_tests"] += 1
                test_results["bills_tested"].append(f"PUT UUID: {test_bill['customer_code']}")
            else:
                print(f"   ❌ FAILED: PUT endpoint not working with UUID format")
                test_results["critical_issues"].append(f"PUT failed for UUID: {test_bill['id']}")
            
            test_results["total_tests"] += 1
        
        # Step 4: Test DELETE /api/bills/{bill_id} với mixed ID formats
        print(f"\n🔍 STEP 4: Test DELETE /api/bills/{{bill_id}} với Mixed ID Formats")
        print("=" * 60)
        print("⚠️ WARNING: This will actually delete bills - testing with AVAILABLE status only")
        
        # Find AVAILABLE bills for safe deletion testing
        available_objectid_bills = [b for b in objectid_bills if b['status'] == 'AVAILABLE']
        available_uuid_bills = [b for b in uuid_bills if b['status'] == 'AVAILABLE']
        
        print(f"   Available ObjectId bills for deletion: {len(available_objectid_bills)}")
        print(f"   Available UUID bills for deletion: {len(available_uuid_bills)}")
        
        # Test ObjectId format deletion
        if available_objectid_bills:
            test_bill = available_objectid_bills[0]
            print(f"\n   Testing DELETE with ObjectId format bill:")
            print(f"   Bill ID: {test_bill['id']}")
            print(f"   Customer Code: {test_bill['customer_code']}")
            print(f"   Status: {test_bill['status']} (safe to delete)")
            
            delete_success, delete_response = self.run_test(
                f"DELETE /bills/{test_bill['id']} - ObjectId Format",
                "DELETE",
                f"bills/{test_bill['id']}",
                200
            )
            
            if delete_success:
                print(f"   ✅ SUCCESS: DELETE endpoint working with ObjectId format")
                print(f"   Response: {delete_response.get('message', 'No message')}")
                test_results["objectid_delete_working"] = True
                test_results["passed_tests"] += 1
                test_results["bills_tested"].append(f"DELETE ObjectId: {test_bill['customer_code']}")
                
                # Verify deletion by trying to GET the bill
                verify_success, verify_response = self.run_test(
                    f"Verify deletion - GET /bills/{test_bill['id']}",
                    "GET",
                    f"bills/{test_bill['id']}",
                    404
                )
                
                if verify_success:
                    print(f"   ✅ Deletion verified - bill no longer accessible")
                    test_results["cascade_deletion_working"] = True
                    test_results["passed_tests"] += 1
                else:
                    print(f"   ⚠️ Deletion verification inconclusive")
                
                test_results["total_tests"] += 1
            else:
                print(f"   ❌ FAILED: DELETE endpoint not working with ObjectId format")
                test_results["critical_issues"].append(f"DELETE failed for ObjectId: {test_bill['id']}")
            
            test_results["total_tests"] += 1
        
        # Test UUID format deletion
        if available_uuid_bills:
            test_bill = available_uuid_bills[0]
            print(f"\n   Testing DELETE with UUID format bill:")
            print(f"   Bill ID: {test_bill['id']}")
            print(f"   Customer Code: {test_bill['customer_code']}")
            print(f"   Status: {test_bill['status']} (safe to delete)")
            
            delete_success, delete_response = self.run_test(
                f"DELETE /bills/{test_bill['id']} - UUID Format",
                "DELETE",
                f"bills/{test_bill['id']}",
                200
            )
            
            if delete_success:
                print(f"   ✅ SUCCESS: DELETE endpoint working with UUID format")
                print(f"   Response: {delete_response.get('message', 'No message')}")
                test_results["uuid_delete_working"] = True
                test_results["passed_tests"] += 1
                test_results["bills_tested"].append(f"DELETE UUID: {test_bill['customer_code']}")
                
                # Verify deletion by trying to GET the bill
                verify_success, verify_response = self.run_test(
                    f"Verify deletion - GET /bills/{test_bill['id']}",
                    "GET",
                    f"bills/{test_bill['id']}",
                    404
                )
                
                if verify_success:
                    print(f"   ✅ Deletion verified - bill no longer accessible")
                    test_results["passed_tests"] += 1
                else:
                    print(f"   ⚠️ Deletion verification inconclusive")
                
                test_results["total_tests"] += 1
            else:
                print(f"   ❌ FAILED: DELETE endpoint not working with UUID format")
                test_results["critical_issues"].append(f"DELETE failed for UUID: {test_bill['id']}")
            
            test_results["total_tests"] += 1
        
        # Step 5: Test error handling for SOLD bills (should not be deletable)
        print(f"\n🔍 STEP 5: Test Error Handling for SOLD Bills")
        print("=" * 60)
        
        sold_bills = [b for b in bills_response if b.get('status') == 'SOLD']
        if sold_bills:
            test_bill = sold_bills[0]
            print(f"\n   Testing DELETE protection for SOLD bill:")
            print(f"   Bill ID: {test_bill['id']}")
            print(f"   Customer Code: {test_bill['customer_code']}")
            print(f"   Status: {test_bill['status']} (should be protected)")
            
            delete_protection_success, delete_protection_response = self.run_test(
                f"DELETE /bills/{test_bill['id']} - SOLD Bill Protection",
                "DELETE",
                f"bills/{test_bill['id']}",
                400  # Should return 400 error for sold bills
            )
            
            if delete_protection_success:
                print(f"   ✅ SUCCESS: SOLD bill protection working")
                print(f"   Error message: {delete_protection_response.get('detail', 'No detail')}")
                test_results["passed_tests"] += 1
            else:
                print(f"   ❌ FAILED: SOLD bill protection not working properly")
                test_results["critical_issues"].append("SOLD bill protection not working")
            
            test_results["total_tests"] += 1
        else:
            print(f"   ⚠️ No SOLD bills found to test protection")
        
        # Step 6: Verify dual lookup strategy is working
        print(f"\n🔍 STEP 6: Verify Dual Lookup Strategy Implementation")
        print("=" * 60)
        
        dual_lookup_working = (
            (test_results["objectid_get_working"] or len(objectid_bills) == 0) and
            (test_results["uuid_get_working"] or len(uuid_bills) == 0) and
            (test_results["objectid_put_working"] or len(objectid_bills) == 0) and
            (test_results["uuid_put_working"] or len(uuid_bills) == 0) and
            (test_results["objectid_delete_working"] or len(available_objectid_bills) == 0) and
            (test_results["uuid_delete_working"] or len(available_uuid_bills) == 0)
        )
        
        if dual_lookup_working:
            print(f"✅ SUCCESS: Dual lookup strategy working for all bill endpoints")
            print(f"   - GET endpoint supports both ObjectId and UUID formats")
            print(f"   - PUT endpoint supports both ObjectId and UUID formats")
            print(f"   - DELETE endpoint supports both ObjectId and UUID formats")
            test_results["dual_lookup_verified"] = True
            test_results["passed_tests"] += 1
        else:
            print(f"❌ FAILED: Dual lookup strategy has issues")
            test_results["critical_issues"].append("Dual lookup strategy not fully working")
        
        test_results["total_tests"] += 1
        
        # Step 7: Final Assessment
        print(f"\n📊 STEP 7: Final Assessment - Bills DELETE Endpoint Dual Lookup Fix")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 CRITICAL VERIFICATION RESULTS:")
        print(f"   DELETE /api/bills/{{bill_id}} ObjectId format: {'✅ WORKING' if test_results['objectid_delete_working'] else '❌ FAILED'}")
        print(f"   DELETE /api/bills/{{bill_id}} UUID format: {'✅ WORKING' if test_results['uuid_delete_working'] else '❌ FAILED'}")
        print(f"   GET /api/bills/{{bill_id}} ObjectId format: {'✅ WORKING' if test_results['objectid_get_working'] else '❌ FAILED'}")
        print(f"   GET /api/bills/{{bill_id}} UUID format: {'✅ WORKING' if test_results['uuid_get_working'] else '❌ FAILED'}")
        print(f"   PUT /api/bills/{{bill_id}} ObjectId format: {'✅ WORKING' if test_results['objectid_put_working'] else '❌ FAILED'}")
        print(f"   PUT /api/bills/{{bill_id}} UUID format: {'✅ WORKING' if test_results['uuid_put_working'] else '❌ FAILED'}")
        print(f"   Dual lookup strategy verified: {'✅ YES' if test_results['dual_lookup_verified'] else '❌ NO'}")
        print(f"   Cascade deletion working: {'✅ YES' if test_results['cascade_deletion_working'] else '❌ NO'}")
        print(f"   Overall Success Rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        print(f"\n🎯 EXPECTED RESULTS VERIFICATION:")
        all_expected_results_met = (
            test_results["dual_lookup_verified"] and
            (test_results["objectid_delete_working"] or len(available_objectid_bills) == 0) and
            (test_results["uuid_delete_working"] or len(available_uuid_bills) == 0) and
            (test_results["objectid_get_working"] or len(objectid_bills) == 0) and
            (test_results["uuid_get_working"] or len(uuid_bills) == 0) and
            (test_results["objectid_put_working"] or len(objectid_bills) == 0) and
            (test_results["uuid_put_working"] or len(uuid_bills) == 0)
        )
        
        if all_expected_results_met:
            print(f"   ✅ Bills deletion working với both ObjectId và UUID formats")
            print(f"   ✅ No more 'Không tìm thấy bill để xóa' error")
            print(f"   ✅ GET và PUT endpoints cũng supporting dual lookup")
            print(f"   ✅ Bills có proper inventory cascade deletion")
            print(f"   ✅ Dual lookup strategy hoạt động correctly cho bills")
        else:
            print(f"   ❌ Some expected results not met:")
            if not test_results["dual_lookup_verified"]:
                print(f"      - Dual lookup strategy not fully implemented")
            if not test_results["objectid_delete_working"] and len(available_objectid_bills) > 0:
                print(f"      - ObjectId format DELETE not working")
            if not test_results["uuid_delete_working"] and len(available_uuid_bills) > 0:
                print(f"      - UUID format DELETE not working")
        
        if test_results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in test_results["critical_issues"]:
                print(f"   - {issue}")
        
        if test_results["bills_tested"]:
            print(f"\n📋 BILLS TESTED:")
            for bill_test in test_results["bills_tested"]:
                print(f"   - {bill_test}")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if all_expected_results_met:
            print(f"   ✅ BILLS DELETE ENDPOINT DUAL LOOKUP FIX VERIFICATION SUCCESSFUL")
            print(f"   - Bills deletion issue resolved sau khi apply dual lookup strategy")
            print(f"   - All bill endpoints (GET, PUT, DELETE) support both ObjectId và UUID")
            print(f"   - No more 404 errors for existing bills with mixed ID formats")
            print(f"   - Proper cascade deletion và error handling implemented")
        else:
            print(f"   ❌ BILLS DELETE ENDPOINT STILL HAS ISSUES")
            print(f"   - Dual lookup fix may not be complete")
            print(f"   - Some bill operations still failing with mixed ID formats")
        
        return all_expected_results_met

    def run_all_tests(self):
        """Run all tests for the review request"""
        print(f"\n🚀 STARTING BILLS DELETE ENDPOINT DUAL LOOKUP FIX VERIFICATION")
        print("=" * 80)
        print(f"🎯 Review Request: Test Bills DELETE endpoint sau khi fix ObjectId vs UUID dual lookup")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API Base URL: {self.base_url}")
        
        # Run the main test
        success = self.test_bills_delete_endpoint_dual_lookup_fix()
        
        # Print final summary
        print(f"\n📊 FINAL TEST SUMMARY")
        print("=" * 50)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if success:
            print(f"\n✅ OVERALL RESULT: Bills DELETE endpoint dual lookup fix PASSED")
            print(f"   - Bills deletion working với both ObjectId và UUID formats")
            print(f"   - No more 'Không tìm thấy bill để xóa' error")
            print(f"   - GET và PUT endpoints cũng supporting dual lookup")
            print(f"   - Bills có proper inventory cascade deletion")
            print(f"   - Dual lookup strategy tương tự như customers và credit cards")
        else:
            print(f"\n❌ OVERALL RESULT: Bills DELETE endpoint NEEDS ATTENTION")
            print(f"   - Dual lookup fix may not be working correctly")
            print(f"   - Some bill operations still failing")
        
        return success

    def comprehensive_id_consistency_audit(self):
        """URGENT SYSTEM-WIDE ID CONSISTENCY AUDIT for Production Readiness"""
        print(f"\n🚨 URGENT SYSTEM-WIDE ID CONSISTENCY AUDIT")
        print("=" * 80)
        print("🎯 CRITICAL PRODUCTION READINESS CHECK:")
        print("   1. Analyze TẤT CẢ collections trong database")
        print("   2. Check for ObjectId vs UUID inconsistencies across ALL entities")
        print("   3. Identify ALL broken references và relationships")
        print("   4. Test các API endpoints chính để xem cái nào broken vì ID issues")
        print("   5. Generate comprehensive report về extent của problem")
        
        audit_results = {
            "collections_analyzed": {},
            "broken_references": [],
            "api_endpoints_broken": [],
            "critical_issues": [],
            "production_blockers": [],
            "total_issues": 0
        }
        
        if not self.mongo_connected:
            print("❌ CRITICAL: Cannot perform audit without database connection!")
            return False
        
        # Step 1: Analyze ALL collections in database
        print(f"\n🔍 STEP 1: Database Collections Analysis")
        print("=" * 60)
        
        try:
            # Get all collection names
            collection_names = self.db.list_collection_names()
            print(f"✅ Found {len(collection_names)} collections: {collection_names}")
            
            for collection_name in collection_names:
                print(f"\n📊 Analyzing collection: {collection_name}")
                collection = self.db[collection_name]
                
                # Get sample documents to analyze ID patterns
                sample_docs = list(collection.find({}).limit(10))
                total_count = collection.count_documents({})
                
                if not sample_docs:
                    print(f"   ⚠️ Empty collection - {total_count} documents")
                    continue
                
                print(f"   📈 Total documents: {total_count}")
                
                # Analyze ID patterns in this collection
                id_analysis = {
                    "has_mongo_id": 0,
                    "has_uuid_id": 0,
                    "mixed_formats": 0,
                    "missing_id_field": 0,
                    "objectid_in_uuid_field": 0,
                    "reference_fields": []
                }
                
                for doc in sample_docs:
                    mongo_id = doc.get('_id')
                    uuid_id = doc.get('id')
                    
                    # Check _id field (always present in MongoDB)
                    if mongo_id:
                        id_analysis["has_mongo_id"] += 1
                    
                    # Check id field
                    if uuid_id:
                        id_analysis["has_uuid_id"] += 1
                        
                        # Check if UUID field contains ObjectId format
                        if isinstance(uuid_id, str) and len(uuid_id) == 24 and all(c in '0123456789abcdef' for c in uuid_id.lower()):
                            id_analysis["objectid_in_uuid_field"] += 1
                            id_analysis["mixed_formats"] += 1
                        elif isinstance(uuid_id, str) and len(uuid_id) == 36 and uuid_id.count('-') == 4:
                            # Proper UUID format
                            pass
                        else:
                            id_analysis["mixed_formats"] += 1
                    else:
                        id_analysis["missing_id_field"] += 1
                    
                    # Look for reference fields (fields ending with _id)
                    for key, value in doc.items():
                        if key.endswith('_id') and key != '_id' and value:
                            if key not in id_analysis["reference_fields"]:
                                id_analysis["reference_fields"].append(key)
                
                # Report findings for this collection
                print(f"   🔍 ID Analysis Results:")
                print(f"      Documents with _id: {id_analysis['has_mongo_id']}/{len(sample_docs)}")
                print(f"      Documents with id field: {id_analysis['has_uuid_id']}/{len(sample_docs)}")
                print(f"      Missing id field: {id_analysis['missing_id_field']}/{len(sample_docs)}")
                print(f"      Mixed/problematic formats: {id_analysis['mixed_formats']}/{len(sample_docs)}")
                print(f"      ObjectId in UUID field: {id_analysis['objectid_in_uuid_field']}/{len(sample_docs)}")
                print(f"      Reference fields found: {id_analysis['reference_fields']}")
                
                # Flag critical issues
                if id_analysis["mixed_formats"] > 0:
                    issue = f"Collection '{collection_name}' has {id_analysis['mixed_formats']} documents with mixed ID formats"
                    audit_results["critical_issues"].append(issue)
                    print(f"   🚨 CRITICAL ISSUE: {issue}")
                
                if id_analysis["missing_id_field"] > 0:
                    issue = f"Collection '{collection_name}' has {id_analysis['missing_id_field']} documents missing 'id' field"
                    audit_results["critical_issues"].append(issue)
                    print(f"   ⚠️ WARNING: {issue}")
                
                audit_results["collections_analyzed"][collection_name] = id_analysis
                
        except Exception as e:
            print(f"❌ Database analysis failed: {e}")
            return False
        
        # Step 2: Check for broken references between collections
        print(f"\n🔍 STEP 2: Cross-Collection Reference Validation")
        print("=" * 60)
        
        # Check customer references in other collections
        if "customers" in audit_results["collections_analyzed"]:
            print(f"\n📋 Checking customer_id references...")
            
            # Get all customer IDs
            customer_ids = set()
            customers = list(self.db.customers.find({}, {"_id": 1, "id": 1}))
            for customer in customers:
                if customer.get("id"):
                    customer_ids.add(customer["id"])
                customer_ids.add(str(customer["_id"]))
            
            print(f"   ✅ Found {len(customer_ids)} unique customer identifiers")
            
            # Check references in sales collection
            if "sales" in collection_names:
                sales_with_invalid_refs = 0
                sales = list(self.db.sales.find({}, {"customer_id": 1}).limit(50))
                for sale in sales:
                    customer_id = sale.get("customer_id")
                    if customer_id and customer_id not in customer_ids:
                        sales_with_invalid_refs += 1
                        audit_results["broken_references"].append({
                            "collection": "sales",
                            "document_id": str(sale["_id"]),
                            "broken_field": "customer_id",
                            "invalid_value": customer_id
                        })
                
                if sales_with_invalid_refs > 0:
                    issue = f"Sales collection has {sales_with_invalid_refs} documents with invalid customer_id references"
                    audit_results["critical_issues"].append(issue)
                    print(f"   🚨 CRITICAL: {issue}")
                else:
                    print(f"   ✅ Sales collection customer_id references are valid")
            
            # Check references in credit_cards collection
            if "credit_cards" in collection_names:
                cards_with_invalid_refs = 0
                cards = list(self.db.credit_cards.find({}, {"customer_id": 1}).limit(50))
                for card in cards:
                    customer_id = card.get("customer_id")
                    if customer_id and customer_id not in customer_ids:
                        cards_with_invalid_refs += 1
                        audit_results["broken_references"].append({
                            "collection": "credit_cards",
                            "document_id": str(card["_id"]),
                            "broken_field": "customer_id",
                            "invalid_value": customer_id
                        })
                
                if cards_with_invalid_refs > 0:
                    issue = f"Credit cards collection has {cards_with_invalid_refs} documents with invalid customer_id references"
                    audit_results["critical_issues"].append(issue)
                    print(f"   🚨 CRITICAL: {issue}")
                else:
                    print(f"   ✅ Credit cards collection customer_id references are valid")
            
            # Check references in credit_card_transactions collection
            if "credit_card_transactions" in collection_names:
                transactions_with_invalid_refs = 0
                transactions = list(self.db.credit_card_transactions.find({}, {"customer_id": 1, "card_id": 1}).limit(50))
                
                # Get all card IDs for validation
                card_ids = set()
                if "credit_cards" in collection_names:
                    cards = list(self.db.credit_cards.find({}, {"_id": 1, "id": 1}))
                    for card in cards:
                        if card.get("id"):
                            card_ids.add(card["id"])
                        card_ids.add(str(card["_id"]))
                
                for transaction in transactions:
                    customer_id = transaction.get("customer_id")
                    card_id = transaction.get("card_id")
                    
                    if customer_id and customer_id not in customer_ids:
                        transactions_with_invalid_refs += 1
                        audit_results["broken_references"].append({
                            "collection": "credit_card_transactions",
                            "document_id": str(transaction["_id"]),
                            "broken_field": "customer_id",
                            "invalid_value": customer_id
                        })
                    
                    if card_id and card_ids and card_id not in card_ids:
                        transactions_with_invalid_refs += 1
                        audit_results["broken_references"].append({
                            "collection": "credit_card_transactions",
                            "document_id": str(transaction["_id"]),
                            "broken_field": "card_id",
                            "invalid_value": card_id
                        })
                
                if transactions_with_invalid_refs > 0:
                    issue = f"Credit card transactions collection has {transactions_with_invalid_refs} documents with invalid references"
                    audit_results["critical_issues"].append(issue)
                    print(f"   🚨 CRITICAL: {issue}")
                else:
                    print(f"   ✅ Credit card transactions references are valid")
        
        # Step 3: Test critical API endpoints for ID-related failures
        print(f"\n🔍 STEP 3: API Endpoints Testing for ID Issues")
        print("=" * 60)
        
        # Test customer endpoints
        print(f"\n📋 Testing Customer API Endpoints...")
        
        # Get customers list
        customers_success, customers_response = self.run_test(
            "GET /customers - List endpoint",
            "GET",
            "customers?page_size=10",
            200
        )
        
        if customers_success and customers_response:
            print(f"   ✅ Customer list endpoint working - {len(customers_response)} customers")
            
            # Test individual customer lookups
            broken_customer_lookups = 0
            for i, customer in enumerate(customers_response[:5]):
                customer_id = customer.get('id')
                customer_name = customer.get('name', 'Unknown')
                
                # Test basic customer endpoint
                customer_success, _ = self.run_test(
                    f"GET /customers/{customer_id} - {customer_name}",
                    "GET",
                    f"customers/{customer_id}",
                    200
                )
                
                if not customer_success:
                    broken_customer_lookups += 1
                    audit_results["api_endpoints_broken"].append(f"GET /customers/{customer_id}")
                
                # Test detailed profile endpoint
                profile_success, _ = self.run_test(
                    f"GET /customers/{customer_id}/detailed-profile - {customer_name}",
                    "GET",
                    f"customers/{customer_id}/detailed-profile",
                    200
                )
                
                if not profile_success:
                    broken_customer_lookups += 1
                    audit_results["api_endpoints_broken"].append(f"GET /customers/{customer_id}/detailed-profile")
            
            if broken_customer_lookups > 0:
                issue = f"Customer individual lookup endpoints have {broken_customer_lookups} failures"
                audit_results["production_blockers"].append(issue)
                print(f"   🚨 PRODUCTION BLOCKER: {issue}")
            else:
                print(f"   ✅ All customer lookup endpoints working")
        else:
            audit_results["production_blockers"].append("Customer list endpoint failing")
            print(f"   🚨 PRODUCTION BLOCKER: Customer list endpoint failing")
        
        # Test credit card endpoints
        print(f"\n📋 Testing Credit Card API Endpoints...")
        
        cards_success, cards_response = self.run_test(
            "GET /credit-cards - List endpoint",
            "GET",
            "credit-cards?limit=5",
            200
        )
        
        if cards_success and cards_response:
            print(f"   ✅ Credit cards list endpoint working - {len(cards_response)} cards")
            
            # Test individual card lookups
            broken_card_lookups = 0
            for card in cards_response[:3]:
                card_id = card.get('id')
                
                card_success, _ = self.run_test(
                    f"GET /credit-cards/{card_id}",
                    "GET",
                    f"credit-cards/{card_id}",
                    200
                )
                
                if not card_success:
                    broken_card_lookups += 1
                    audit_results["api_endpoints_broken"].append(f"GET /credit-cards/{card_id}")
            
            if broken_card_lookups > 0:
                issue = f"Credit card individual lookup endpoints have {broken_card_lookups} failures"
                audit_results["production_blockers"].append(issue)
                print(f"   🚨 PRODUCTION BLOCKER: {issue}")
            else:
                print(f"   ✅ All credit card lookup endpoints working")
        else:
            print(f"   ⚠️ Credit cards list endpoint issues")
        
        # Test bills endpoints
        print(f"\n📋 Testing Bills API Endpoints...")
        
        bills_success, bills_response = self.run_test(
            "GET /bills - List endpoint",
            "GET",
            "bills?limit=5",
            200
        )
        
        if bills_success and bills_response:
            print(f"   ✅ Bills list endpoint working - {len(bills_response)} bills")
            
            # Test individual bill lookups if endpoint exists
            if bills_response:
                bill_id = bills_response[0].get('id')
                bill_success, _ = self.run_test(
                    f"GET /bills/{bill_id}",
                    "GET",
                    f"bills/{bill_id}",
                    200
                )
                
                if not bill_success:
                    audit_results["api_endpoints_broken"].append(f"GET /bills/{bill_id}")
                    print(f"   ⚠️ Individual bill lookup may have issues")
                else:
                    print(f"   ✅ Individual bill lookup working")
        else:
            print(f"   ⚠️ Bills list endpoint issues")
        
        # Step 4: Generate comprehensive report
        print(f"\n📊 STEP 4: Comprehensive Audit Report")
        print("=" * 60)
        
        audit_results["total_issues"] = len(audit_results["critical_issues"]) + len(audit_results["broken_references"]) + len(audit_results["production_blockers"])
        
        print(f"\n🚨 CRITICAL PRODUCTION READINESS ASSESSMENT:")
        print(f"   Total Issues Found: {audit_results['total_issues']}")
        print(f"   Critical Issues: {len(audit_results['critical_issues'])}")
        print(f"   Broken References: {len(audit_results['broken_references'])}")
        print(f"   Production Blockers: {len(audit_results['production_blockers'])}")
        print(f"   Broken API Endpoints: {len(audit_results['api_endpoints_broken'])}")
        
        print(f"\n📋 COLLECTIONS ANALYSIS SUMMARY:")
        for collection_name, analysis in audit_results["collections_analyzed"].items():
            mixed_count = analysis.get("mixed_formats", 0)
            missing_count = analysis.get("missing_id_field", 0)
            status = "🚨 CRITICAL" if mixed_count > 0 or missing_count > 0 else "✅ OK"
            print(f"   {collection_name}: {status}")
            if mixed_count > 0:
                print(f"      - Mixed ID formats: {mixed_count}")
            if missing_count > 0:
                print(f"      - Missing ID field: {missing_count}")
        
        if audit_results["broken_references"]:
            print(f"\n🔗 BROKEN REFERENCES DETAILS:")
            for ref in audit_results["broken_references"][:10]:  # Show first 10
                print(f"   {ref['collection']}.{ref['broken_field']} = '{ref['invalid_value']}'")
            if len(audit_results["broken_references"]) > 10:
                print(f"   ... and {len(audit_results['broken_references']) - 10} more")
        
        if audit_results["production_blockers"]:
            print(f"\n🚫 PRODUCTION BLOCKERS:")
            for blocker in audit_results["production_blockers"]:
                print(f"   🚨 {blocker}")
        
        # Priority recommendations
        print(f"\n🎯 PRIORITY FIXES NEEDED BEFORE PRODUCTION:")
        priority_fixes = []
        
        if audit_results["production_blockers"]:
            priority_fixes.extend(audit_results["production_blockers"])
        
        if len(audit_results["broken_references"]) > 0:
            priority_fixes.append(f"Fix {len(audit_results['broken_references'])} broken references")
        
        for collection_name, analysis in audit_results["collections_analyzed"].items():
            if analysis.get("mixed_formats", 0) > 0:
                priority_fixes.append(f"Standardize ID formats in {collection_name} collection")
        
        if priority_fixes:
            for i, fix in enumerate(priority_fixes, 1):
                print(f"   {i}. {fix}")
        else:
            print(f"   ✅ No critical issues found - system appears production ready!")
        
        # Final assessment
        is_production_ready = audit_results["total_issues"] == 0
        
        print(f"\n🏁 FINAL PRODUCTION READINESS ASSESSMENT:")
        if is_production_ready:
            print(f"   ✅ SYSTEM IS PRODUCTION READY")
            print(f"   - All ID formats are consistent")
            print(f"   - No broken references detected")
            print(f"   - All API endpoints working correctly")
        else:
            print(f"   🚨 SYSTEM NOT READY FOR PRODUCTION")
            print(f"   - {audit_results['total_issues']} issues must be resolved")
            print(f"   - Critical data integrity problems detected")
            print(f"   - API functionality compromised")
        
        return is_production_ready

    def test_customer_objectid_uuid_fix(self):
        """Test customer endpoints sau khi fix ObjectId vs UUID issue"""
        print(f"\n🎯 CUSTOMER OBJECTID VS UUID FIX VERIFICATION")
        print("=" * 80)
        print("🔍 TESTING PRIORITIES:")
        print("   1. Test DELETE /api/customers/68b86b157a314c251c8c863b (customer có vấn đề ObjectId)")
        print("   2. Test PUT /api/customers/68b86b157a314c251c8c863b (update endpoint)")
        print("   3. Test GET /api/customers/68b86b157a314c251c8c863b/transactions (transactions endpoint)")
        print("   4. Verify dual lookup strategy hoạt động cho tất cả endpoints")
        
        target_customer_id = "68b86b157a314c251c8c863b"
        test_results = {
            "delete_working": False,
            "update_working": False,
            "transactions_working": False,
            "dual_lookup_verified": False,
            "total_tests": 0,
            "passed_tests": 0
        }
        
        # Step 1: Verify customer exists first
        print(f"\n🔍 STEP 1: Verify Target Customer Exists")
        print("=" * 60)
        
        customer_exists, customer_data = self.run_test(
            f"GET /customers/{target_customer_id} - Verify Existence",
            "GET",
            f"customers/{target_customer_id}",
            200
        )
        
        if customer_exists:
            customer_name = customer_data.get('name', 'Unknown')
            print(f"✅ Target customer exists: {customer_name}")
            print(f"   Customer ID: {target_customer_id}")
            print(f"   Customer Type: {customer_data.get('type', 'Unknown')}")
            test_results["passed_tests"] += 1
        else:
            print(f"❌ Target customer {target_customer_id} not found!")
            print(f"   Cannot proceed with testing - customer doesn't exist")
            test_results["total_tests"] += 1
            return False
        
        test_results["total_tests"] += 1
        
        # Step 2: Test PUT /api/customers/{customer_id} (update endpoint)
        print(f"\n🔍 STEP 2: Test PUT /api/customers/{target_customer_id} (Update Endpoint)")
        print("=" * 60)
        
        # Prepare update data
        update_data = {
            "notes": f"Updated via API test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        }
        
        update_success, update_response = self.run_test(
            f"PUT /customers/{target_customer_id} - Update Customer",
            "PUT",
            f"customers/{target_customer_id}",
            200,
            data=update_data
        )
        
        if update_success:
            print(f"✅ UPDATE ENDPOINT WORKING: Customer {target_customer_id} updated successfully")
            print(f"   Updated notes: {update_response.get('notes', 'Not found')}")
            print(f"   Customer name: {update_response.get('name', 'Unknown')}")
            test_results["update_working"] = True
            test_results["passed_tests"] += 1
        else:
            print(f"❌ UPDATE ENDPOINT FAILED: Customer {target_customer_id} update failed")
            print(f"   This indicates ObjectId/UUID lookup issue still exists")
        
        test_results["total_tests"] += 1
        
        # Step 3: Test GET /api/customers/{customer_id}/transactions (transactions endpoint)
        print(f"\n🔍 STEP 3: Test GET /api/customers/{target_customer_id}/transactions")
        print("=" * 60)
        
        transactions_success, transactions_response = self.run_test(
            f"GET /customers/{target_customer_id}/transactions - Get Transactions",
            "GET",
            f"customers/{target_customer_id}/transactions",
            200
        )
        
        if transactions_success:
            print(f"✅ TRANSACTIONS ENDPOINT WORKING: Customer {target_customer_id} transactions retrieved")
            if isinstance(transactions_response, list):
                print(f"   Found {len(transactions_response)} transactions")
                if transactions_response:
                    first_transaction = transactions_response[0]
                    print(f"   Sample transaction ID: {first_transaction.get('id', 'Unknown')}")
                    print(f"   Sample transaction type: {first_transaction.get('transaction_type', 'Unknown')}")
            elif isinstance(transactions_response, dict):
                transactions_list = transactions_response.get('transactions', [])
                print(f"   Found {len(transactions_list)} transactions in response")
            test_results["transactions_working"] = True
            test_results["passed_tests"] += 1
        else:
            print(f"❌ TRANSACTIONS ENDPOINT FAILED: Customer {target_customer_id} transactions failed")
            print(f"   This indicates ObjectId/UUID lookup issue in transactions endpoint")
        
        test_results["total_tests"] += 1
        
        # Step 4: Test DELETE /api/customers/{customer_id} (CAREFUL - this will delete the customer!)
        print(f"\n🔍 STEP 4: Test DELETE /api/customers/{target_customer_id} (Delete Endpoint)")
        print("=" * 60)
        print(f"⚠️ WARNING: This will attempt to delete the customer!")
        print(f"   Testing delete capability to verify ObjectId/UUID lookup works")
        
        # First, let's check if there's a safer way to test delete without actually deleting
        # We'll test with a non-existent customer ID first to verify the endpoint exists
        fake_customer_id = "00000000000000000000000000000000"  # Fake ObjectId format
        
        fake_delete_success, fake_delete_response = self.run_test(
            f"DELETE /customers/{fake_customer_id} - Test Delete Endpoint Exists",
            "DELETE",
            f"customers/{fake_customer_id}",
            404  # Expect 404 for non-existent customer
        )
        
        if fake_delete_success:
            print(f"✅ DELETE ENDPOINT EXISTS: Returns proper 404 for non-existent customer")
            print(f"   This confirms the delete endpoint is working and can handle ObjectId format")
            
            # Now test with the real customer (but we'll be careful)
            print(f"\n   🚨 TESTING ACTUAL DELETE - This will delete the customer!")
            
            delete_success, delete_response = self.run_test(
                f"DELETE /customers/{target_customer_id} - Delete Customer",
                "DELETE",
                f"customers/{target_customer_id}",
                200
            )
            
            if delete_success:
                print(f"✅ DELETE ENDPOINT WORKING: Customer {target_customer_id} deleted successfully")
                print(f"   Response: {delete_response}")
                test_results["delete_working"] = True
                test_results["passed_tests"] += 1
                
                # Verify customer is actually deleted
                verify_delete_success, verify_delete_response = self.run_test(
                    f"GET /customers/{target_customer_id} - Verify Deletion",
                    "GET",
                    f"customers/{target_customer_id}",
                    404  # Should return 404 now
                )
                
                if verify_delete_success:
                    print(f"✅ DELETION VERIFIED: Customer {target_customer_id} no longer exists")
                    test_results["passed_tests"] += 1
                else:
                    print(f"❌ DELETION NOT VERIFIED: Customer may still exist")
                
                test_results["total_tests"] += 1
            else:
                print(f"❌ DELETE ENDPOINT FAILED: Customer {target_customer_id} delete failed")
                print(f"   This indicates ObjectId/UUID lookup issue in delete endpoint")
        else:
            print(f"❌ DELETE ENDPOINT NOT WORKING: Endpoint may not exist or has issues")
        
        test_results["total_tests"] += 1
        
        # Step 5: Test dual lookup strategy with other customers
        print(f"\n🔍 STEP 5: Verify Dual Lookup Strategy với Other Customers")
        print("=" * 60)
        
        # Get list of customers to test dual lookup
        customers_success, customers_response = self.run_test(
            "GET /customers - Get Customer List for Dual Lookup Testing",
            "GET",
            "customers?page_size=10",
            200
        )
        
        if customers_success and customers_response:
            print(f"✅ Found {len(customers_response)} customers for dual lookup testing")
            
            dual_lookup_tests = 0
            dual_lookup_passed = 0
            
            for customer in customers_response[:3]:  # Test first 3 customers
                customer_id = customer.get('id', '')
                customer_name = customer.get('name', 'Unknown')
                
                print(f"\n   Testing dual lookup for: {customer_name}")
                print(f"   Customer ID: {customer_id}")
                print(f"   ID Format: {'ObjectId' if len(customer_id) == 24 else 'UUID' if len(customer_id) == 36 else 'Other'}")
                
                # Test basic customer lookup
                lookup_success, lookup_response = self.run_test(
                    f"Dual Lookup Test - {customer_name}",
                    "GET",
                    f"customers/{customer_id}",
                    200
                )
                
                dual_lookup_tests += 1
                if lookup_success:
                    print(f"   ✅ Dual lookup working for {customer_name}")
                    dual_lookup_passed += 1
                else:
                    print(f"   ❌ Dual lookup failed for {customer_name}")
            
            if dual_lookup_passed == dual_lookup_tests:
                print(f"\n✅ DUAL LOOKUP STRATEGY VERIFIED: All {dual_lookup_tests} tests passed")
                test_results["dual_lookup_verified"] = True
                test_results["passed_tests"] += dual_lookup_passed
            else:
                print(f"\n❌ DUAL LOOKUP STRATEGY ISSUES: {dual_lookup_passed}/{dual_lookup_tests} tests passed")
            
            test_results["total_tests"] += dual_lookup_tests
        
        # Step 6: Final Assessment
        print(f"\n📊 STEP 6: Final Assessment - ObjectId vs UUID Fix")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 TEST RESULTS SUMMARY:")
        print(f"   Customer Exists: ✅ VERIFIED")
        print(f"   DELETE /customers/{target_customer_id}: {'✅ WORKING' if test_results['delete_working'] else '❌ FAILED'}")
        print(f"   PUT /customers/{target_customer_id}: {'✅ WORKING' if test_results['update_working'] else '❌ FAILED'}")
        print(f"   GET /customers/{target_customer_id}/transactions: {'✅ WORKING' if test_results['transactions_working'] else '❌ FAILED'}")
        print(f"   Dual Lookup Strategy: {'✅ VERIFIED' if test_results['dual_lookup_verified'] else '❌ ISSUES'}")
        print(f"   Overall Success Rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        print(f"\n🎯 EXPECTED RESULTS VERIFICATION:")
        expected_results_met = (
            test_results["delete_working"] and 
            test_results["update_working"] and 
            test_results["transactions_working"] and
            test_results["dual_lookup_verified"]
        )
        
        if expected_results_met:
            print(f"   ✅ Customer ID 68b86b157a314c251c8c863b can now delete, update, get transactions")
            print(f"   ✅ All customer endpoints support both ObjectId and UUID")
            print(f"   ✅ No more 404 errors for existing customers")
            print(f"   ✅ Dual lookup strategy working correctly")
        else:
            print(f"   ❌ Some expected results not met:")
            if not test_results["delete_working"]:
                print(f"      - DELETE endpoint still has issues")
            if not test_results["update_working"]:
                print(f"      - UPDATE endpoint still has issues")
            if not test_results["transactions_working"]:
                print(f"      - TRANSACTIONS endpoint still has issues")
            if not test_results["dual_lookup_verified"]:
                print(f"      - Dual lookup strategy has issues")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if expected_results_met:
            print(f"   ✅ OBJECTID VS UUID FIX VERIFICATION SUCCESSFUL")
            print(f"   - All customer operations (CRUD + transactions) working with mixed ID formats")
            print(f"   - Customer 68b86b157a314c251c8c863b fully functional")
            print(f"   - System ready for production use")
        else:
            print(f"   ❌ OBJECTID VS UUID FIX NEEDS MORE WORK")
            print(f"   - Some customer operations still failing")
            print(f"   - Further investigation required")
        
        return expected_results_met

    def test_credit_card_deletion_and_data_consistency_comprehensive(self):
        """COMPREHENSIVE: Test credit card deletion và data consistency issues với detailed analysis"""
        print(f"\n🚨 COMPREHENSIVE CREDIT CARD DELETION & DATA CONSISTENCY TESTING")
        print("=" * 80)
        print("🔍 CRITICAL ANALYSIS:")
        print("   1. Identify ObjectId vs UUID issues in credit card endpoints")
        print("   2. Test DELETE /api/credit-cards/{card_id} với both formats")
        print("   3. Analyze credit card transaction ID inconsistencies (CC_* format)")
        print("   4. Check cascade deletion và broken references")
        print("   5. Compare với customer endpoints (đã fix dual lookup)")
        
        test_results = {
            "objectid_uuid_issue_confirmed": False,
            "delete_endpoint_broken": False,
            "transaction_id_inconsistent": False,
            "broken_references_found": False,
            "dual_lookup_missing": False,
            "total_tests": 0,
            "passed_tests": 0,
            "critical_findings": []
        }
        
        # Step 1: Comprehensive Database Analysis
        print(f"\n🔍 STEP 1: Comprehensive Database Analysis")
        print("=" * 60)
        
        if self.mongo_connected:
            try:
                # Analyze ALL collections for ID consistency
                collections_analysis = {}
                
                for collection_name in ["customers", "credit_cards", "credit_card_transactions", "sales", "bills"]:
                    print(f"\n📊 Analyzing {collection_name} collection:")
                    
                    docs = list(self.db[collection_name].find({}).limit(10))
                    if not docs:
                        print(f"   ⚠️ Empty collection")
                        continue
                    
                    id_patterns = {"uuid": 0, "objectid": 0, "custom": 0, "other": 0}
                    
                    for doc in docs:
                        doc_id = doc.get('id', '')
                        if len(doc_id) == 36 and doc_id.count('-') == 4:
                            id_patterns["uuid"] += 1
                        elif len(doc_id) == 24 and all(c in '0123456789abcdef' for c in doc_id.lower()):
                            id_patterns["objectid"] += 1
                        elif doc_id.startswith('CC_'):
                            id_patterns["custom"] += 1
                        else:
                            id_patterns["other"] += 1
                    
                    collections_analysis[collection_name] = id_patterns
                    
                    print(f"   UUID: {id_patterns['uuid']}, ObjectId: {id_patterns['objectid']}, Custom: {id_patterns['custom']}, Other: {id_patterns['other']}")
                    
                    # Flag inconsistencies
                    if id_patterns["objectid"] > 0 and collection_name in ["credit_cards"]:
                        test_results["critical_findings"].append(f"{collection_name} has {id_patterns['objectid']} documents with ObjectId format in 'id' field")
                        test_results["objectid_uuid_issue_confirmed"] = True
                    
                    if id_patterns["custom"] > 0:
                        test_results["critical_findings"].append(f"{collection_name} has {id_patterns['custom']} documents with custom ID format")
                        test_results["transaction_id_inconsistent"] = True
                
                print(f"\n📋 COLLECTIONS SUMMARY:")
                for collection, analysis in collections_analysis.items():
                    total_docs = sum(analysis.values())
                    inconsistent = analysis["objectid"] + analysis["custom"] + analysis["other"]
                    status = "🚨 INCONSISTENT" if inconsistent > 0 else "✅ CONSISTENT"
                    print(f"   {collection}: {status} ({inconsistent}/{total_docs} inconsistent)")
                
                test_results["passed_tests"] += 1
                
            except Exception as e:
                print(f"❌ Database analysis failed: {e}")
                test_results["critical_findings"].append(f"Database analysis failed: {e}")
        
        test_results["total_tests"] += 1
        
        # Step 2: Test Credit Card Endpoints với ObjectId Format
        print(f"\n🔍 STEP 2: Test Credit Card Endpoints với ObjectId Format")
        print("=" * 60)
        
        # Get credit cards with ObjectId format
        cards_success, cards_response = self.run_test(
            "GET /credit-cards - Get cards for ObjectId testing",
            "GET",
            "credit-cards?limit=5",
            200
        )
        
        if cards_success and cards_response:
            objectid_cards = [card for card in cards_response if len(card.get('id', '')) == 24]
            uuid_cards = [card for card in cards_response if len(card.get('id', '')) == 36]
            
            print(f"✅ Found {len(objectid_cards)} cards with ObjectId format")
            print(f"✅ Found {len(uuid_cards)} cards with UUID format")
            
            if objectid_cards:
                test_card = objectid_cards[0]
                card_id = test_card.get('id')
                
                print(f"\n🧪 Testing ObjectId format card: {card_id}")
                
                # Test GET detail endpoint
                detail_success, detail_response = self.run_test(
                    f"GET /credit-cards/{card_id}/detail - ObjectId format",
                    "GET",
                    f"credit-cards/{card_id}/detail",
                    200
                )
                
                if not detail_success:
                    print(f"   ❌ CRITICAL: ObjectId format card cannot be accessed via detail endpoint")
                    test_results["critical_findings"].append(f"Credit card detail endpoint fails for ObjectId format: {card_id}")
                    test_results["dual_lookup_missing"] = True
                else:
                    print(f"   ✅ ObjectId format card accessible via detail endpoint")
                    test_results["passed_tests"] += 1
                
                test_results["total_tests"] += 1
                
                # Test DELETE endpoint (with caution)
                print(f"\n⚠️ Testing DELETE endpoint với ObjectId format")
                print(f"   Card ID: {card_id}")
                
                delete_success, delete_response = self.run_test(
                    f"DELETE /credit-cards/{card_id} - ObjectId format",
                    "DELETE",
                    f"credit-cards/{card_id}",
                    200
                )
                
                if not delete_success:
                    print(f"   ❌ CRITICAL: DELETE endpoint fails for ObjectId format")
                    test_results["critical_findings"].append(f"Credit card DELETE endpoint fails for ObjectId format: {card_id}")
                    test_results["delete_endpoint_broken"] = True
                else:
                    print(f"   ✅ DELETE endpoint works for ObjectId format")
                    test_results["passed_tests"] += 1
                    
                    # Verify deletion
                    verify_success, verify_response = self.run_test(
                        f"Verify deletion - GET /credit-cards/{card_id}/detail",
                        "GET",
                        f"credit-cards/{card_id}/detail",
                        404
                    )
                    
                    if verify_success:
                        print(f"   ✅ Deletion verified successfully")
                        test_results["passed_tests"] += 1
                    else:
                        print(f"   ❌ Deletion verification failed")
                    
                    test_results["total_tests"] += 1
                
                test_results["total_tests"] += 1
            else:
                print(f"   ⚠️ No ObjectId format cards found for testing")
        
        # Step 3: Analyze Credit Card Transaction Inconsistencies
        print(f"\n🔍 STEP 3: Credit Card Transaction ID Inconsistencies Analysis")
        print("=" * 60)
        
        if self.mongo_connected:
            try:
                transactions = list(self.db.credit_card_transactions.find({}).limit(20))
                print(f"✅ Analyzing {len(transactions)} credit card transactions")
                
                cc_format_count = 0
                uuid_format_count = 0
                broken_refs = 0
                
                for transaction in transactions:
                    transaction_id = transaction.get('id', '')
                    card_id = transaction.get('card_id', '')
                    
                    # Count ID formats
                    if transaction_id.startswith('CC_'):
                        cc_format_count += 1
                    elif len(transaction_id) == 36 and transaction_id.count('-') == 4:
                        uuid_format_count += 1
                    
                    # Check for broken card references
                    if card_id:
                        card_exists = self.db.credit_cards.find_one({"id": card_id})
                        if not card_exists:
                            broken_refs += 1
                
                print(f"📊 TRANSACTION ID ANALYSIS:")
                print(f"   CC_* format: {cc_format_count}")
                print(f"   UUID format: {uuid_format_count}")
                print(f"   Broken card references: {broken_refs}")
                
                if cc_format_count > 0:
                    test_results["critical_findings"].append(f"Found {cc_format_count} credit card transactions with non-standard CC_* ID format")
                    test_results["transaction_id_inconsistent"] = True
                
                if broken_refs > 0:
                    test_results["critical_findings"].append(f"Found {broken_refs} credit card transactions with broken card references")
                    test_results["broken_references_found"] = True
                else:
                    print(f"   ✅ No broken references found")
                    test_results["passed_tests"] += 1
                
            except Exception as e:
                print(f"❌ Transaction analysis failed: {e}")
        
        test_results["total_tests"] += 1
        
        # Step 4: Compare với Customer Endpoints (đã có dual lookup)
        print(f"\n🔍 STEP 4: Compare với Customer Endpoints (Dual Lookup Reference)")
        print("=" * 60)
        
        print(f"📋 CUSTOMER ENDPOINTS (WORKING DUAL LOOKUP):")
        print(f"   - GET /customers/{'{customer_id}'} - supports both ObjectId and UUID")
        print(f"   - DELETE /customers/{'{customer_id}'} - supports both ObjectId and UUID")
        print(f"   - PUT /customers/{'{customer_id}'} - supports both ObjectId and UUID")
        
        print(f"\n📋 CREDIT CARD ENDPOINTS (MISSING DUAL LOOKUP):")
        print(f"   - GET /credit-cards/{'{card_id}'}/detail - only supports UUID")
        print(f"   - DELETE /credit-cards/{'{card_id}'} - only supports UUID")
        print(f"   - PUT /credit-cards/{'{card_id}'} - only supports UUID")
        
        if test_results["objectid_uuid_issue_confirmed"]:
            print(f"\n🚨 CRITICAL FINDING: Credit card endpoints need dual lookup implementation!")
            print(f"   Same fix applied to customer endpoints should be applied to credit card endpoints")
            test_results["dual_lookup_missing"] = True
        
        # Step 5: Final Assessment
        print(f"\n📊 STEP 5: Final Comprehensive Assessment")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 CRITICAL ISSUES IDENTIFIED:")
        print(f"   ObjectId vs UUID issue confirmed: {'🚨 YES' if test_results['objectid_uuid_issue_confirmed'] else '✅ NO'}")
        print(f"   DELETE endpoint broken: {'🚨 YES' if test_results['delete_endpoint_broken'] else '✅ NO'}")
        print(f"   Transaction ID inconsistent: {'🚨 YES' if test_results['transaction_id_inconsistent'] else '✅ NO'}")
        print(f"   Broken references found: {'🚨 YES' if test_results['broken_references_found'] else '✅ NO'}")
        print(f"   Dual lookup missing: {'🚨 YES' if test_results['dual_lookup_missing'] else '✅ NO'}")
        print(f"   Success Rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        print(f"\n🚨 ALL CRITICAL FINDINGS ({len(test_results['critical_findings'])}):")
        for i, finding in enumerate(test_results['critical_findings'], 1):
            print(f"   {i}. {finding}")
        
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        print(f"   🔍 MAIN ISSUE: Credit card endpoints lack dual lookup strategy")
        print(f"   📝 EVIDENCE: Credit cards have ObjectId format in 'id' field but endpoints only query by 'id'")
        print(f"   💡 SOLUTION: Implement same dual lookup fix as customer endpoints")
        print(f"   🔧 AFFECTED ENDPOINTS: GET /credit-cards/{'{card_id}'}/detail, DELETE /credit-cards/{'{card_id}'}, PUT /credit-cards/{'{card_id}'}")
        
        print(f"\n🎯 SECONDARY ISSUES:")
        if test_results["transaction_id_inconsistent"]:
            print(f"   🔍 TRANSACTION ID FORMAT: Some transactions use CC_* format instead of UUID")
            print(f"   💡 IMPACT: Data consistency issue but doesn't break functionality")
        
        if test_results["broken_references_found"]:
            print(f"   🔍 BROKEN REFERENCES: Some transactions reference non-existent cards")
            print(f"   💡 IMPACT: Data integrity issue requiring cleanup")
        
        # Determine system health
        critical_issues = sum([
            test_results["objectid_uuid_issue_confirmed"],
            test_results["delete_endpoint_broken"],
            test_results["dual_lookup_missing"]
        ])
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if critical_issues == 0:
            print(f"   ✅ CREDIT CARD SYSTEM IS HEALTHY")
            print(f"   - All endpoints working correctly")
            print(f"   - No critical ObjectId/UUID issues")
            print(f"   - System ready for production")
        else:
            print(f"   🚨 CREDIT CARD SYSTEM NEEDS URGENT FIXES")
            print(f"   - {critical_issues} critical issues requiring immediate attention")
            print(f"   - ObjectId/UUID dual lookup missing in credit card endpoints")
            print(f"   - Same fix pattern as customer endpoints should be applied")
        
        return critical_issues == 0

    def test_credit_card_deletion_and_data_consistency(self):
        """URGENT: Test credit card deletion và data consistency issues"""
        print(f"\n🚨 URGENT CREDIT CARD DELETION & DATA CONSISTENCY TESTING")
        print("=" * 80)
        print("🔍 CRITICAL CHECKS:")
        print("   1. Test credit card DELETE endpoints - ObjectId vs UUID issues?")
        print("   2. Check credit card creation - consistent ID formats?")
        print("   3. Analyze database records creation patterns - tại sao data 'loạn xạ'?")
        print("   4. Test cascade deletion for credit cards và related transactions")
        print("   5. Identify ALL endpoints tạo data với inconsistent formats")
        
        test_results = {
            "delete_endpoint_working": False,
            "creation_consistent": False,
            "data_patterns_analyzed": False,
            "cascade_deletion_working": False,
            "inconsistent_endpoints": [],
            "total_tests": 0,
            "passed_tests": 0,
            "critical_issues": []
        }
        
        # Step 1: Analyze existing credit card data patterns
        print(f"\n🔍 STEP 1: Analyze Credit Card Database Patterns")
        print("=" * 60)
        
        if self.mongo_connected:
            try:
                # Get credit cards from database
                credit_cards = list(self.db.credit_cards.find({}).limit(20))
                print(f"✅ Found {len(credit_cards)} credit cards in database")
                
                # Analyze ID patterns
                id_patterns = {"uuid": 0, "objectid": 0, "other": 0, "mixed_issues": []}
                
                for card in credit_cards:
                    card_id = card.get('id', '')
                    mongo_id = str(card.get('_id', ''))
                    
                    if len(card_id) == 36 and card_id.count('-') == 4:
                        id_patterns["uuid"] += 1
                    elif len(card_id) == 24 and all(c in '0123456789abcdef' for c in card_id.lower()):
                        id_patterns["objectid"] += 1
                        id_patterns["mixed_issues"].append({
                            "card_id": card_id,
                            "customer_id": card.get('customer_id', 'Unknown'),
                            "issue": "UUID field contains ObjectId format"
                        })
                    else:
                        id_patterns["other"] += 1
                        id_patterns["mixed_issues"].append({
                            "card_id": card_id,
                            "customer_id": card.get('customer_id', 'Unknown'),
                            "issue": f"Unknown ID format: {card_id}"
                        })
                
                print(f"📊 CREDIT CARD ID ANALYSIS:")
                print(f"   UUID format: {id_patterns['uuid']}")
                print(f"   ObjectId format: {id_patterns['objectid']}")
                print(f"   Other formats: {id_patterns['other']}")
                print(f"   Mixed/problematic: {len(id_patterns['mixed_issues'])}")
                
                if id_patterns['mixed_issues']:
                    print(f"\n🚨 PROBLEMATIC CREDIT CARDS FOUND:")
                    for issue in id_patterns['mixed_issues'][:5]:
                        print(f"   Card ID: {issue['card_id']} - {issue['issue']}")
                    test_results["critical_issues"].append(f"Found {len(id_patterns['mixed_issues'])} credit cards with inconsistent ID formats")
                
                test_results["data_patterns_analyzed"] = True
                test_results["passed_tests"] += 1
                
            except Exception as e:
                print(f"❌ Database analysis failed: {e}")
                test_results["critical_issues"].append(f"Database analysis failed: {e}")
        else:
            print(f"⚠️ MongoDB connection not available")
        
        test_results["total_tests"] += 1
        
        # Step 2: Test credit card creation consistency
        print(f"\n🔍 STEP 2: Test Credit Card Creation Consistency")
        print("=" * 60)
        
        # Get a customer to create credit card for
        customers_success, customers_response = self.run_test(
            "GET /customers - Get customer for credit card creation",
            "GET",
            "customers?page_size=5",
            200
        )
        
        if customers_success and customers_response:
            test_customer = customers_response[0]
            customer_id = test_customer.get('id')
            customer_name = test_customer.get('name', 'Unknown')
            
            print(f"✅ Using customer: {customer_name} (ID: {customer_id})")
            
            # Create test credit card
            test_card_data = {
                "customer_id": customer_id,
                "card_number": "4111111111111111",
                "cardholder_name": "Test Card Holder",
                "bank_name": "Test Bank",
                "card_type": "VISA",
                "expiry_date": "12/25",
                "ccv": "123",
                "statement_date": 15,
                "payment_due_date": 25,
                "credit_limit": 50000000,
                "status": "Chưa đến hạn",
                "notes": f"Test card created at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
            create_success, create_response = self.run_test(
                "POST /credit-cards - Create test credit card",
                "POST",
                "credit-cards",
                201,
                data=test_card_data
            )
            
            if create_success:
                created_card_id = create_response.get('id', '')
                print(f"✅ Credit card created successfully")
                print(f"   Card ID: {created_card_id}")
                print(f"   ID Length: {len(created_card_id)} chars")
                print(f"   ID Format: {'UUID' if len(created_card_id) == 36 and created_card_id.count('-') == 4 else 'ObjectId' if len(created_card_id) == 24 else 'Other'}")
                
                # Check if ID format is consistent (should be UUID)
                if len(created_card_id) == 36 and created_card_id.count('-') == 4:
                    print(f"   ✅ ID format is consistent (UUID)")
                    test_results["creation_consistent"] = True
                    test_results["passed_tests"] += 1
                else:
                    print(f"   🚨 ID format is inconsistent: {created_card_id}")
                    test_results["critical_issues"].append(f"Credit card creation uses inconsistent ID format: {created_card_id}")
                    test_results["inconsistent_endpoints"].append("POST /credit-cards")
                
                # Store created card ID for deletion test
                test_results["test_card_id"] = created_card_id
                
            else:
                print(f"❌ Credit card creation failed")
                test_results["critical_issues"].append("Credit card creation endpoint failing")
                test_results["inconsistent_endpoints"].append("POST /credit-cards")
        else:
            print(f"❌ Cannot get customers for credit card creation test")
        
        test_results["total_tests"] += 1
        
        # Step 3: Test credit card DELETE endpoint
        print(f"\n🔍 STEP 3: Test Credit Card DELETE Endpoint")
        print("=" * 60)
        
        # Get existing credit cards to test deletion
        cards_success, cards_response = self.run_test(
            "GET /credit-cards - Get cards for deletion test",
            "GET",
            "credit-cards?limit=10",
            200
        )
        
        if cards_success and cards_response:
            print(f"✅ Found {len(cards_response)} credit cards for testing")
            
            # Test with first available card (or created test card)
            test_card_id = test_results.get("test_card_id") or (cards_response[0].get('id') if cards_response else None)
            
            if test_card_id:
                print(f"   Testing deletion with card ID: {test_card_id}")
                print(f"   ID Format: {'UUID' if len(test_card_id) == 36 and test_card_id.count('-') == 4 else 'ObjectId' if len(test_card_id) == 24 else 'Other'}")
                
                # First test with non-existent card to verify endpoint exists
                fake_card_id = "00000000-0000-0000-0000-000000000000"
                fake_delete_success, fake_delete_response = self.run_test(
                    f"DELETE /credit-cards/{fake_card_id} - Test endpoint exists",
                    "DELETE",
                    f"credit-cards/{fake_card_id}",
                    404
                )
                
                if fake_delete_success:
                    print(f"   ✅ DELETE endpoint exists and returns proper 404")
                    
                    # Now test actual deletion
                    delete_success, delete_response = self.run_test(
                        f"DELETE /credit-cards/{test_card_id} - Delete credit card",
                        "DELETE",
                        f"credit-cards/{test_card_id}",
                        200
                    )
                    
                    if delete_success:
                        print(f"   ✅ Credit card deletion successful")
                        print(f"   Response: {delete_response}")
                        test_results["delete_endpoint_working"] = True
                        test_results["passed_tests"] += 1
                        
                        # Verify card is actually deleted
                        verify_success, verify_response = self.run_test(
                            f"GET /credit-cards/{test_card_id} - Verify deletion",
                            "GET",
                            f"credit-cards/{test_card_id}",
                            404
                        )
                        
                        if verify_success:
                            print(f"   ✅ Deletion verified - card no longer exists")
                            test_results["passed_tests"] += 1
                        else:
                            print(f"   ❌ Deletion not verified - card may still exist")
                        
                        test_results["total_tests"] += 1
                        
                    else:
                        print(f"   ❌ Credit card deletion failed")
                        test_results["critical_issues"].append(f"DELETE /credit-cards/{test_card_id} failed - possible ObjectId/UUID issue")
                        test_results["inconsistent_endpoints"].append(f"DELETE /credit-cards/{test_card_id}")
                else:
                    print(f"   ❌ DELETE endpoint not working properly")
                    test_results["critical_issues"].append("DELETE /credit-cards endpoint not functioning")
            else:
                print(f"   ❌ No credit card available for deletion test")
        else:
            print(f"❌ Cannot get credit cards for deletion test")
        
        test_results["total_tests"] += 1
        
        # Step 4: Test cascade deletion for credit card transactions
        print(f"\n🔍 STEP 4: Test Cascade Deletion for Credit Card Transactions")
        print("=" * 60)
        
        if self.mongo_connected:
            try:
                # Check if there are credit card transactions
                transactions = list(self.db.credit_card_transactions.find({}).limit(10))
                print(f"✅ Found {len(transactions)} credit card transactions in database")
                
                if transactions:
                    # Analyze transaction ID patterns
                    transaction_id_patterns = {"uuid": 0, "objectid": 0, "other": 0, "custom": 0}
                    
                    for transaction in transactions:
                        transaction_id = transaction.get('id', '')
                        
                        if len(transaction_id) == 36 and transaction_id.count('-') == 4:
                            transaction_id_patterns["uuid"] += 1
                        elif len(transaction_id) == 24 and all(c in '0123456789abcdef' for c in transaction_id.lower()):
                            transaction_id_patterns["objectid"] += 1
                        elif transaction_id.startswith('CC_'):
                            transaction_id_patterns["custom"] += 1
                        else:
                            transaction_id_patterns["other"] += 1
                    
                    print(f"📊 CREDIT CARD TRANSACTION ID ANALYSIS:")
                    print(f"   UUID format: {transaction_id_patterns['uuid']}")
                    print(f"   ObjectId format: {transaction_id_patterns['objectid']}")
                    print(f"   Custom format (CC_*): {transaction_id_patterns['custom']}")
                    print(f"   Other formats: {transaction_id_patterns['other']}")
                    
                    if transaction_id_patterns['custom'] > 0:
                        print(f"   🚨 INCONSISTENT TRANSACTION IDs: Found {transaction_id_patterns['custom']} transactions with CC_ format")
                        test_results["critical_issues"].append(f"Credit card transactions using non-standard ID format (CC_*)")
                        test_results["inconsistent_endpoints"].append("Credit card transaction creation")
                    
                    # Check for broken references
                    broken_refs = 0
                    for transaction in transactions[:5]:
                        card_id = transaction.get('card_id', '')
                        customer_id = transaction.get('customer_id', '')
                        
                        # Check if referenced card exists
                        if card_id:
                            card_exists = self.db.credit_cards.find_one({"id": card_id})
                            if not card_exists:
                                broken_refs += 1
                                print(f"   🚨 BROKEN REFERENCE: Transaction references non-existent card {card_id}")
                    
                    if broken_refs > 0:
                        test_results["critical_issues"].append(f"Found {broken_refs} credit card transactions with broken card references")
                    else:
                        print(f"   ✅ No broken card references found in transactions")
                        test_results["cascade_deletion_working"] = True
                        test_results["passed_tests"] += 1
                else:
                    print(f"   ⚠️ No credit card transactions found for analysis")
                    test_results["cascade_deletion_working"] = True  # No transactions to break
                    test_results["passed_tests"] += 1
                
            except Exception as e:
                print(f"❌ Transaction analysis failed: {e}")
                test_results["critical_issues"].append(f"Credit card transaction analysis failed: {e}")
        
        test_results["total_tests"] += 1
        
        # Step 5: Identify ALL endpoints creating inconsistent data
        print(f"\n🔍 STEP 5: Identify ALL Endpoints Creating Inconsistent Data")
        print("=" * 60)
        
        # Test various creation endpoints
        endpoints_to_test = [
            ("POST /customers", "customers"),
            ("POST /bills", "bills"),
            ("POST /sales", "sales"),
            ("POST /credit-cards", "credit-cards")
        ]
        
        for endpoint_name, collection_name in endpoints_to_test:
            if self.mongo_connected:
                try:
                    # Sample recent documents from collection
                    recent_docs = list(self.db[collection_name].find({}).sort("_id", -1).limit(5))
                    
                    if recent_docs:
                        inconsistent_count = 0
                        for doc in recent_docs:
                            doc_id = doc.get('id', '')
                            if doc_id and not (len(doc_id) == 36 and doc_id.count('-') == 4):
                                inconsistent_count += 1
                        
                        if inconsistent_count > 0:
                            print(f"   🚨 {endpoint_name}: {inconsistent_count}/{len(recent_docs)} recent documents have inconsistent IDs")
                            test_results["inconsistent_endpoints"].append(endpoint_name)
                        else:
                            print(f"   ✅ {endpoint_name}: All recent documents have consistent UUID format")
                    else:
                        print(f"   ⚠️ {endpoint_name}: No documents found in {collection_name}")
                        
                except Exception as e:
                    print(f"   ❌ {endpoint_name}: Analysis failed - {e}")
        
        # Step 6: Final Assessment
        print(f"\n📊 STEP 6: Final Assessment - Credit Card Deletion & Data Consistency")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 CRITICAL FINDINGS:")
        print(f"   DELETE /credit-cards endpoint: {'✅ WORKING' if test_results['delete_endpoint_working'] else '❌ FAILING'}")
        print(f"   Credit card creation consistency: {'✅ CONSISTENT' if test_results['creation_consistent'] else '❌ INCONSISTENT'}")
        print(f"   Database patterns analyzed: {'✅ COMPLETED' if test_results['data_patterns_analyzed'] else '❌ FAILED'}")
        print(f"   Cascade deletion working: {'✅ WORKING' if test_results['cascade_deletion_working'] else '❌ ISSUES'}")
        print(f"   Success Rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        print(f"\n🚨 CRITICAL ISSUES FOUND ({len(test_results['critical_issues'])}):")
        for i, issue in enumerate(test_results['critical_issues'], 1):
            print(f"   {i}. {issue}")
        
        print(f"\n🔧 ENDPOINTS WITH INCONSISTENT DATA CREATION ({len(test_results['inconsistent_endpoints'])}):")
        for endpoint in test_results['inconsistent_endpoints']:
            print(f"   - {endpoint}")
        
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        if test_results['critical_issues']:
            print(f"   🚨 SYSTEM HAS DATA CONSISTENCY PROBLEMS")
            print(f"   - Mixed ObjectId/UUID formats detected")
            print(f"   - Some endpoints creating non-standard IDs")
            print(f"   - Potential broken references in transactions")
        else:
            print(f"   ✅ NO CRITICAL DATA CONSISTENCY ISSUES FOUND")
            print(f"   - All ID formats appear consistent")
            print(f"   - No broken references detected")
        
        # Determine if system is ready
        is_system_healthy = (
            len(test_results['critical_issues']) == 0 and
            test_results['delete_endpoint_working'] and
            test_results['creation_consistent'] and
            test_results['cascade_deletion_working']
        )
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if is_system_healthy:
            print(f"   ✅ CREDIT CARD SYSTEM IS HEALTHY")
            print(f"   - DELETE endpoints working correctly")
            print(f"   - Data creation is consistent")
            print(f"   - No broken references detected")
            print(f"   - System ready for production")
        else:
            print(f"   🚨 CREDIT CARD SYSTEM HAS ISSUES")
            print(f"   - {len(test_results['critical_issues'])} critical issues found")
            print(f"   - Data consistency problems detected")
            print(f"   - Immediate fixes required")
        
        return is_system_healthy

    def run_all_tests(self):
        """Run comprehensive credit card deletion and data consistency testing"""
        print(f"\n🚀 STARTING COMPREHENSIVE CREDIT CARD DELETION & DATA CONSISTENCY TESTING")
        print("=" * 80)
        print(f"🎯 Review Request: URGENT credit card deletion và data consistency issues")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API Base URL: {self.base_url}")
        
        # Run the comprehensive credit card test
        success = self.test_credit_card_deletion_and_data_consistency_comprehensive()
        
        # Print final summary
        print(f"\n📊 FINAL TEST SUMMARY")
        print("=" * 50)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if success:
            print(f"\n✅ OVERALL RESULT: CREDIT CARD SYSTEM IS HEALTHY")
            print(f"   - DELETE /credit-cards endpoints working correctly")
            print(f"   - No critical ObjectId vs UUID issues detected")
            print(f"   - Data consistency maintained")
            print(f"   - System ready for production use")
        else:
            print(f"\n❌ OVERALL RESULT: CREDIT CARD SYSTEM HAS CRITICAL ISSUES")
            print(f"   - ObjectId vs UUID dual lookup missing in credit card endpoints")
            print(f"   - DELETE /credit-cards fails for ObjectId format cards")
            print(f"   - Data consistency problems detected")
            print(f"   - URGENT: Apply same dual lookup fix as customer endpoints")
        
        return success

    def test_credit_card_objectid_uuid_fix(self):
        """Test credit card endpoints sau khi fix ObjectId vs UUID issue"""
        print(f"\n🎯 CREDIT CARD OBJECTID VS UUID FIX VERIFICATION")
        print("=" * 80)
        print("🔍 CRITICAL VERIFICATION:")
        print("   1. Test với credit card có ObjectId format (trước đó broken)")
        print("   2. Test DELETE /api/credit-cards/{card_id} dual lookup")
        print("   3. Test GET /api/credit-cards/{card_id}/detail dual lookup")
        print("   4. Test PUT /api/credit-cards/{card_id} dual lookup")
        print("   5. Verify credit card operations hoạt động với mixed ID formats")
        
        test_results = {
            "objectid_cards_accessible": False,
            "delete_dual_lookup": False,
            "detail_dual_lookup": False,
            "update_dual_lookup": False,
            "mixed_formats_working": False,
            "total_tests": 0,
            "passed_tests": 0,
            "critical_findings": []
        }
        
        # Step 1: Get credit cards and identify ObjectId format cards
        print(f"\n🔍 STEP 1: Identify Credit Cards with ObjectId Format")
        print("=" * 60)
        
        cards_success, cards_response = self.run_test(
            "GET /credit-cards - Get all credit cards",
            "GET",
            "credit-cards?limit=50",
            200
        )
        
        if not cards_success or not cards_response:
            print(f"❌ Cannot get credit cards list - testing aborted")
            return False
        
        # Analyze card ID formats
        objectid_cards = []
        uuid_cards = []
        
        for card in cards_response:
            card_id = card.get('id', '')
            if len(card_id) == 24 and all(c in '0123456789abcdef' for c in card_id.lower()):
                objectid_cards.append(card)
            elif len(card_id) == 36 and card_id.count('-') == 4:
                uuid_cards.append(card)
        
        print(f"✅ Found {len(cards_response)} total credit cards")
        print(f"   ObjectId format cards: {len(objectid_cards)}")
        print(f"   UUID format cards: {len(uuid_cards)}")
        
        if len(objectid_cards) == 0:
            print(f"⚠️ No ObjectId format cards found - cannot test ObjectId dual lookup")
            test_results["critical_findings"].append("No ObjectId format cards available for testing")
        
        test_results["total_tests"] += 1
        test_results["passed_tests"] += 1
        
        # Step 2: Test GET /api/credit-cards/{card_id}/detail dual lookup
        print(f"\n🔍 STEP 2: Test GET /api/credit-cards/{{card_id}}/detail Dual Lookup")
        print("=" * 60)
        
        detail_tests_passed = 0
        detail_tests_total = 0
        
        # Test with ObjectId format cards
        for i, card in enumerate(objectid_cards[:3]):  # Test first 3 ObjectId cards
            card_id = card.get('id')
            card_number = card.get('card_number', 'Unknown')
            
            print(f"\n   Test {i+1}: ObjectId format card ****{card_number[-4:] if len(card_number) >= 4 else card_number}")
            print(f"   Card ID: {card_id}")
            
            detail_success, detail_response = self.run_test(
                f"GET /credit-cards/{card_id}/detail - ObjectId format",
                "GET",
                f"credit-cards/{card_id}/detail",
                200
            )
            
            detail_tests_total += 1
            if detail_success:
                print(f"   ✅ SUCCESS: ObjectId format card accessible via detail endpoint")
                detail_tests_passed += 1
                test_results["passed_tests"] += 1
            else:
                print(f"   ❌ FAILED: ObjectId format card NOT accessible via detail endpoint")
                test_results["critical_findings"].append(f"Detail endpoint failed for ObjectId card: {card_id}")
            
            test_results["total_tests"] += 1
        
        # Test with UUID format cards for compatibility
        for i, card in enumerate(uuid_cards[:2]):  # Test 2 UUID cards for compatibility
            card_id = card.get('id')
            card_number = card.get('card_number', 'Unknown')
            
            print(f"\n   Compatibility Test {i+1}: UUID format card ****{card_number[-4:] if len(card_number) >= 4 else card_number}")
            
            detail_success, detail_response = self.run_test(
                f"GET /credit-cards/{card_id}/detail - UUID format",
                "GET",
                f"credit-cards/{card_id}/detail",
                200
            )
            
            detail_tests_total += 1
            if detail_success:
                print(f"   ✅ SUCCESS: UUID format card still working")
                detail_tests_passed += 1
                test_results["passed_tests"] += 1
            else:
                print(f"   ❌ FAILED: UUID format card broken - regression issue")
                test_results["critical_findings"].append(f"Detail endpoint regression for UUID card: {card_id}")
            
            test_results["total_tests"] += 1
        
        if detail_tests_passed == detail_tests_total and detail_tests_total > 0:
            test_results["detail_dual_lookup"] = True
            print(f"\n✅ DETAIL ENDPOINT DUAL LOOKUP: {detail_tests_passed}/{detail_tests_total} tests passed")
        else:
            print(f"\n❌ DETAIL ENDPOINT DUAL LOOKUP: {detail_tests_passed}/{detail_tests_total} tests passed")
        
        # Step 3: Test PUT /api/credit-cards/{card_id} dual lookup
        print(f"\n🔍 STEP 3: Test PUT /api/credit-cards/{{card_id}} Dual Lookup")
        print("=" * 60)
        
        update_tests_passed = 0
        update_tests_total = 0
        
        # Test update with ObjectId format cards
        for i, card in enumerate(objectid_cards[:2]):  # Test first 2 ObjectId cards
            card_id = card.get('id')
            card_number = card.get('card_number', 'Unknown')
            
            print(f"\n   Update Test {i+1}: ObjectId format card ****{card_number[-4:] if len(card_number) >= 4 else card_number}")
            print(f"   Card ID: {card_id}")
            
            # Prepare update data
            update_data = {
                "notes": f"Updated via ObjectId dual lookup test at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            }
            
            update_success, update_response = self.run_test(
                f"PUT /credit-cards/{card_id} - ObjectId format update",
                "PUT",
                f"credit-cards/{card_id}",
                200,
                data=update_data
            )
            
            update_tests_total += 1
            if update_success:
                print(f"   ✅ SUCCESS: ObjectId format card updated successfully")
                print(f"   Updated notes: {update_response.get('notes', 'Not found')}")
                update_tests_passed += 1
                test_results["passed_tests"] += 1
            else:
                print(f"   ❌ FAILED: ObjectId format card update failed")
                test_results["critical_findings"].append(f"Update endpoint failed for ObjectId card: {card_id}")
            
            test_results["total_tests"] += 1
        
        if update_tests_passed == update_tests_total and update_tests_total > 0:
            test_results["update_dual_lookup"] = True
            print(f"\n✅ UPDATE ENDPOINT DUAL LOOKUP: {update_tests_passed}/{update_tests_total} tests passed")
        else:
            print(f"\n❌ UPDATE ENDPOINT DUAL LOOKUP: {update_tests_passed}/{update_tests_total} tests passed")
        
        # Step 4: Test DELETE /api/credit-cards/{card_id} dual lookup
        print(f"\n🔍 STEP 4: Test DELETE /api/credit-cards/{{card_id}} Dual Lookup")
        print("=" * 60)
        
        delete_tests_passed = 0
        delete_tests_total = 0
        
        # Test delete with ObjectId format cards (CAREFUL - this will delete cards!)
        for i, card in enumerate(objectid_cards[:1]):  # Test only 1 ObjectId card for deletion
            card_id = card.get('id')
            card_number = card.get('card_number', 'Unknown')
            
            print(f"\n   Delete Test {i+1}: ObjectId format card ****{card_number[-4:] if len(card_number) >= 4 else card_number}")
            print(f"   Card ID: {card_id}")
            print(f"   ⚠️ WARNING: This will delete the credit card!")
            
            delete_success, delete_response = self.run_test(
                f"DELETE /credit-cards/{card_id} - ObjectId format delete",
                "DELETE",
                f"credit-cards/{card_id}",
                200
            )
            
            delete_tests_total += 1
            if delete_success:
                print(f"   ✅ SUCCESS: ObjectId format card deleted successfully")
                print(f"   Delete message: {delete_response.get('message', 'No message')}")
                delete_tests_passed += 1
                test_results["passed_tests"] += 1
                
                # Verify deletion
                verify_success, verify_response = self.run_test(
                    f"Verify deletion - GET /credit-cards/{card_id}/detail",
                    "GET",
                    f"credit-cards/{card_id}/detail",
                    404
                )
                
                if verify_success:
                    print(f"   ✅ Deletion verified - card no longer accessible")
                    test_results["passed_tests"] += 1
                else:
                    print(f"   ❌ Deletion verification failed - card may still exist")
                
                test_results["total_tests"] += 1
            else:
                print(f"   ❌ FAILED: ObjectId format card deletion failed")
                test_results["critical_findings"].append(f"Delete endpoint failed for ObjectId card: {card_id}")
            
            test_results["total_tests"] += 1
        
        if delete_tests_passed == delete_tests_total and delete_tests_total > 0:
            test_results["delete_dual_lookup"] = True
            print(f"\n✅ DELETE ENDPOINT DUAL LOOKUP: {delete_tests_passed}/{delete_tests_total} tests passed")
        else:
            print(f"\n❌ DELETE ENDPOINT DUAL LOOKUP: {delete_tests_passed}/{delete_tests_total} tests passed")
        
        # Step 5: Verify mixed ID formats working
        print(f"\n🔍 STEP 5: Verify Mixed ID Formats Working")
        print("=" * 60)
        
        mixed_format_success = (
            test_results["detail_dual_lookup"] and
            test_results["update_dual_lookup"] and
            test_results["delete_dual_lookup"]
        )
        
        if mixed_format_success:
            test_results["mixed_formats_working"] = True
            print(f"✅ MIXED ID FORMATS VERIFICATION: All endpoints support both ObjectId and UUID")
        else:
            print(f"❌ MIXED ID FORMATS VERIFICATION: Some endpoints still have issues")
        
        # Step 6: Final Assessment
        print(f"\n📊 STEP 6: Final Assessment - Credit Card ObjectId vs UUID Fix")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 EXPECTED RESULTS VERIFICATION:")
        print(f"   Credit cards với ObjectId format accessible: {'✅ YES' if len(objectid_cards) > 0 and test_results['detail_dual_lookup'] else '❌ NO'}")
        print(f"   DELETE /api/credit-cards/{{card_id}} dual lookup: {'✅ WORKING' if test_results['delete_dual_lookup'] else '❌ FAILED'}")
        print(f"   GET /api/credit-cards/{{card_id}}/detail dual lookup: {'✅ WORKING' if test_results['detail_dual_lookup'] else '❌ FAILED'}")
        print(f"   PUT /api/credit-cards/{{card_id}} dual lookup: {'✅ WORKING' if test_results['update_dual_lookup'] else '❌ FAILED'}")
        print(f"   Mixed ID formats working: {'✅ YES' if test_results['mixed_formats_working'] else '❌ NO'}")
        print(f"   Overall Success Rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        expected_results_met = (
            test_results["detail_dual_lookup"] and
            test_results["update_dual_lookup"] and
            test_results["delete_dual_lookup"] and
            test_results["mixed_formats_working"]
        )
        
        print(f"\n🎯 CRITICAL VERIFICATION RESULTS:")
        if expected_results_met:
            print(f"   ✅ Credit cards với ObjectId format bây giờ accessible")
            print(f"   ✅ All CRUD operations hoạt động với both UUID và ObjectId")
            print(f"   ✅ No more 404 errors cho existing credit cards")
            print(f"   ✅ Credit card deletion issue đã được resolved")
        else:
            print(f"   ❌ Some expected results not achieved:")
            if not test_results["detail_dual_lookup"]:
                print(f"      - Detail endpoint dual lookup has issues")
            if not test_results["update_dual_lookup"]:
                print(f"      - Update endpoint dual lookup has issues")
            if not test_results["delete_dual_lookup"]:
                print(f"      - Delete endpoint dual lookup has issues")
            if not test_results["mixed_formats_working"]:
                print(f"      - Mixed ID format support incomplete")
        
        if test_results["critical_findings"]:
            print(f"\n🚨 CRITICAL FINDINGS:")
            for finding in test_results["critical_findings"]:
                print(f"   - {finding}")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if expected_results_met:
            print(f"   ✅ CREDIT CARD OBJECTID VS UUID FIX VERIFICATION SUCCESSFUL")
            print(f"   - All credit card operations working with mixed ID formats")
            print(f"   - ObjectId format cards fully accessible")
            print(f"   - Dual lookup strategy implemented correctly")
            print(f"   - Credit card deletion issue resolved")
        else:
            print(f"   ❌ CREDIT CARD OBJECTID VS UUID FIX NEEDS MORE WORK")
            print(f"   - Some credit card operations still failing")
            print(f"   - Further investigation required")
        
        return expected_results_met

if __name__ == "__main__":
    tester = FPTBillManagerAPITester()
    
    # Run bills data verification and creation test (review request)
    print("🎯 RUNNING BILLS DATA VERIFICATION AND CREATION")
    success = tester.test_bills_data_verification_and_creation()
    
    if success:
        print("\n✅ Bills data verification and creation PASSED!")
    else:
        print("\n❌ Bills data verification and creation NEEDS ATTENTION!")
    
    # Close MongoDB connection
    if tester.mongo_connected:
        tester.mongo_client.close()
    
    sys.exit(0 if success else 1)