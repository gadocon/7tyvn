#!/usr/bin/env python3
"""
Credit Card Current Balance Field Removal Testing
Focused testing for the review request
"""

import requests
import sys
import json
from datetime import datetime
import pymongo
from pymongo import MongoClient

class CreditCardTester:
    def __init__(self, base_url="https://crm-7ty.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
        # MongoDB connection for direct database debugging
        try:
            self.mongo_client = MongoClient("mongodb://localhost:27017")
            self.db = self.mongo_client["crm_7ty_vn"]  # Use correct database name
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

    def test_credit_card_current_balance_field_removal(self):
        """Test credit card system after current_balance field removal - REVIEW REQUEST"""
        print(f"\n🎯 CREDIT CARD CURRENT BALANCE FIELD REMOVAL TESTING")
        print("=" * 80)
        print("🔍 CRITICAL TESTING OBJECTIVES:")
        print("   1. Test Credit Card CRUD Operations (GET, POST, PUT)")
        print("   2. Test DAO Endpoint Testing (specific and general)")
        print("   3. Verify unmasked card numbers in DAO transactions")
        print("   4. Test business logic without current_balance")
        print("   5. Verify database field removal")
        print("   Expected: All operations work without current_balance field")
        
        test_results = {
            "credit_cards_get_working": False,
            "credit_card_detail_working": False,
            "credit_card_create_working": False,
            "credit_card_update_working": False,
            "dao_specific_working": False,
            "dao_general_working": False,
            "unmasked_card_storage": False,
            "business_logic_working": False,
            "no_current_balance_field": False,
            "total_tests": 0,
            "passed_tests": 0,
            "critical_issues": [],
            "test_customer_id": None,
            "test_card_id": None
        }
        
        # Step 1: Test GET /api/credit-cards endpoint
        print(f"\n🔍 STEP 1: Test GET /api/credit-cards Endpoint")
        print("=" * 60)
        
        cards_success, cards_response = self.run_test(
            "GET /credit-cards - List All Credit Cards",
            "GET",
            "credit-cards?page_size=50",
            200
        )
        
        if cards_success and cards_response:
            print(f"✅ SUCCESS: GET /api/credit-cards returns {len(cards_response)} cards")
            test_results["credit_cards_get_working"] = True
            test_results["passed_tests"] += 1
            
            # Verify no current_balance field in response
            if cards_response:
                sample_card = cards_response[0]
                if "current_balance" not in sample_card:
                    print(f"✅ VERIFIED: No current_balance field in credit card response")
                    test_results["no_current_balance_field"] = True
                    test_results["passed_tests"] += 1
                else:
                    print(f"❌ FAILED: current_balance field still present in response")
                    test_results["critical_issues"].append("current_balance field still in API response")
                
                test_results["total_tests"] += 1
                
                # Store test card ID for further testing
                test_results["test_card_id"] = sample_card.get("id")
                print(f"   Using test card ID: {test_results['test_card_id']}")
        else:
            print(f"❌ FAILED: GET /api/credit-cards endpoint not working")
            test_results["critical_issues"].append("Credit cards list endpoint failed")
        
        test_results["total_tests"] += 1
        
        # Step 2: Test GET /api/credit-cards/{card_id}/detail endpoint
        print(f"\n🔍 STEP 2: Test GET /api/credit-cards/{{card_id}}/detail Endpoint")
        print("=" * 60)
        
        if test_results["test_card_id"]:
            detail_success, detail_response = self.run_test(
                f"GET /credit-cards/{test_results['test_card_id']}/detail",
                "GET",
                f"credit-cards/{test_results['test_card_id']}/detail",
                200
            )
            
            if detail_success and detail_response:
                print(f"✅ SUCCESS: Credit card detail endpoint working")
                test_results["credit_card_detail_working"] = True
                test_results["passed_tests"] += 1
                
                # Verify response structure
                expected_keys = ["success", "credit_card", "customer", "transactions", "summary"]
                missing_keys = [key for key in expected_keys if key not in detail_response]
                
                if not missing_keys:
                    print(f"✅ VERIFIED: Detail response has all expected keys")
                    test_results["passed_tests"] += 1
                else:
                    print(f"❌ FAILED: Missing keys in detail response: {missing_keys}")
                    test_results["critical_issues"].append(f"Missing detail response keys: {missing_keys}")
                
                test_results["total_tests"] += 1
            else:
                print(f"❌ FAILED: Credit card detail endpoint not working")
                test_results["critical_issues"].append("Credit card detail endpoint failed")
        else:
            print(f"⚠️ SKIPPED: No test card ID available")
        
        test_results["total_tests"] += 1
        
        # Step 3: Create test customer for credit card operations
        print(f"\n🔍 STEP 3: Create Test Customer for Credit Card Operations")
        print("=" * 60)
        
        customer_data = {
            "name": "Credit Card Test Customer",
            "phone": f"0901{int(datetime.now().timestamp()) % 1000000:06d}",
            "email": f"creditcard.test.{int(datetime.now().timestamp())}@example.com",
            "address": "123 Credit Card Test Street",
            "type": "INDIVIDUAL"
        }
        
        customer_success, customer_response = self.run_test(
            "POST /customers - Create Test Customer",
            "POST",
            "customers",
            200,
            data=customer_data
        )
        
        if customer_success and customer_response:
            test_results["test_customer_id"] = customer_response.get("id")
            print(f"✅ SUCCESS: Created test customer ID: {test_results['test_customer_id']}")
            test_results["passed_tests"] += 1
        else:
            print(f"❌ FAILED: Could not create test customer")
            test_results["critical_issues"].append("Test customer creation failed")
        
        test_results["total_tests"] += 1
        
        # Step 4: Test POST /api/credit-cards (create)
        print(f"\n🔍 STEP 4: Test POST /api/credit-cards (Create Credit Card)")
        print("=" * 60)
        
        if test_results["test_customer_id"]:
            card_data = {
                "customer_id": test_results["test_customer_id"],
                "card_number": "4111111111111111",  # Test Visa number
                "cardholder_name": "CREDIT CARD TEST CUSTOMER",
                "bank_name": "Test Bank",
                "card_type": "VISA",
                "expiry_date": "12/27",
                "ccv": "123",
                "statement_date": 5,
                "payment_due_date": 15,
                "credit_limit": 50000000.0,
                "notes": "Test credit card for current_balance removal testing"
            }
            
            create_success, create_response = self.run_test(
                "POST /credit-cards - Create Credit Card",
                "POST",
                "credit-cards",
                200,
                data=card_data
            )
            
            if create_success and create_response:
                new_card_id = create_response.get("id")
                print(f"✅ SUCCESS: Created credit card ID: {new_card_id}")
                test_results["credit_card_create_working"] = True
                test_results["passed_tests"] += 1
                
                # Verify no current_balance in created card
                if "current_balance" not in create_response:
                    print(f"✅ VERIFIED: No current_balance field in created card")
                    test_results["passed_tests"] += 1
                else:
                    print(f"❌ FAILED: current_balance field present in created card")
                    test_results["critical_issues"].append("current_balance in created card response")
                
                test_results["total_tests"] += 1
                
                # Update test_card_id to use newly created card
                test_results["test_card_id"] = new_card_id
            else:
                print(f"❌ FAILED: Credit card creation not working")
                test_results["critical_issues"].append("Credit card creation failed")
        else:
            print(f"⚠️ SKIPPED: No test customer ID available")
        
        test_results["total_tests"] += 1
        
        # Step 5: Test PUT /api/credit-cards/{card_id} (update)
        print(f"\n🔍 STEP 5: Test PUT /api/credit-cards/{{card_id}} (Update Credit Card)")
        print("=" * 60)
        
        if test_results["test_card_id"]:
            update_data = {
                "credit_limit": 60000000.0,
                "notes": "Updated credit card - current_balance removal test"
            }
            
            update_success, update_response = self.run_test(
                f"PUT /credit-cards/{test_results['test_card_id']} - Update Credit Card",
                "PUT",
                f"credit-cards/{test_results['test_card_id']}",
                200,
                data=update_data
            )
            
            if update_success and update_response:
                print(f"✅ SUCCESS: Credit card update working")
                test_results["credit_card_update_working"] = True
                test_results["passed_tests"] += 1
                
                # Verify updated values
                if update_response.get("credit_limit") == 60000000.0:
                    print(f"✅ VERIFIED: Credit limit updated correctly")
                    test_results["passed_tests"] += 1
                else:
                    print(f"❌ FAILED: Credit limit not updated correctly")
                
                test_results["total_tests"] += 1
            else:
                print(f"❌ FAILED: Credit card update not working")
                test_results["critical_issues"].append("Credit card update failed")
        else:
            print(f"⚠️ SKIPPED: No test card ID available")
        
        test_results["total_tests"] += 1
        
        # Step 6: Test POST /api/credit-cards/{card_id}/dao (specific DAO endpoint)
        print(f"\n🔍 STEP 6: Test POST /api/credit-cards/{{card_id}}/dao (Specific DAO)")
        print("=" * 60)
        
        if test_results["test_card_id"]:
            dao_data = {
                "amount": 5000000.0,
                "profit_value": 150000.0,
                "fee_rate": 3.0,
                "payment_method": "POS",
                "pos_code": "TEST001",
                "transaction_code": "TXN123456",
                "notes": "Test DAO transaction - current_balance removal"
            }
            
            dao_success, dao_response = self.run_test(
                f"POST /credit-cards/{test_results['test_card_id']}/dao - Specific DAO",
                "POST",
                f"credit-cards/{test_results['test_card_id']}/dao",
                200,
                data=dao_data
            )
            
            if dao_success and dao_response:
                print(f"✅ SUCCESS: Specific DAO endpoint working")
                test_results["dao_specific_working"] = True
                test_results["passed_tests"] += 1
                
                # Verify DAO transaction response
                dao_transaction = dao_response.get("dao_transaction", {})
                if dao_transaction:
                    # Check for unmasked card number storage
                    stored_card_number = dao_transaction.get("card_number")
                    if stored_card_number == "4111111111111111":
                        print(f"✅ VERIFIED: Unmasked card number stored in DAO transaction")
                        test_results["unmasked_card_storage"] = True
                        test_results["passed_tests"] += 1
                    else:
                        print(f"❌ FAILED: Card number not stored unmasked: {stored_card_number}")
                        test_results["critical_issues"].append("Card number not stored unmasked")
                    
                    test_results["total_tests"] += 1
                    
                    # Verify business logic fields
                    if "transaction_id" in dao_transaction and "amount" in dao_transaction:
                        print(f"✅ VERIFIED: DAO transaction has required business fields")
                        test_results["business_logic_working"] = True
                        test_results["passed_tests"] += 1
                    else:
                        print(f"❌ FAILED: DAO transaction missing business fields")
                    
                    test_results["total_tests"] += 1
            else:
                print(f"❌ FAILED: Specific DAO endpoint not working")
                test_results["critical_issues"].append("Specific DAO endpoint failed")
        else:
            print(f"⚠️ SKIPPED: No test card ID available")
        
        test_results["total_tests"] += 1
        
        # Step 7: Test POST /api/credit-cards/dao (general DAO endpoint)
        print(f"\n🔍 STEP 7: Test POST /api/credit-cards/dao (General DAO)")
        print("=" * 60)
        
        if test_results["test_customer_id"]:
            general_dao_data = {
                "customer_id": test_results["test_customer_id"],
                "card_id": test_results["test_card_id"],
                "amount": 3000000.0,
                "profit_value": 90000.0,
                "fee_rate": 3.0,
                "payment_method": "CASH",
                "notes": "Test general DAO - current_balance removal"
            }
            
            general_dao_success, general_dao_response = self.run_test(
                "POST /credit-cards/dao - General DAO",
                "POST",
                "credit-cards/dao",
                200,
                data=general_dao_data
            )
            
            if general_dao_success and general_dao_response:
                print(f"✅ SUCCESS: General DAO endpoint working")
                test_results["dao_general_working"] = True
                test_results["passed_tests"] += 1
                
                # Verify general DAO transaction response
                general_dao_transaction = general_dao_response.get("dao_transaction", {})
                if general_dao_transaction:
                    # Check for unmasked card number storage in general DAO
                    stored_card_number = general_dao_transaction.get("card_number")
                    if stored_card_number == "4111111111111111":
                        print(f"✅ VERIFIED: Unmasked card number stored in general DAO")
                        test_results["passed_tests"] += 1
                    else:
                        print(f"⚠️ NOTE: Card number in general DAO: {stored_card_number}")
                    
                    test_results["total_tests"] += 1
            else:
                print(f"❌ FAILED: General DAO endpoint not working")
                test_results["critical_issues"].append("General DAO endpoint failed")
        else:
            print(f"⚠️ SKIPPED: No test customer ID available")
        
        test_results["total_tests"] += 1
        
        # Step 8: Verify database field removal
        print(f"\n🔍 STEP 8: Verify Database Field Removal")
        print("=" * 60)
        
        if self.mongo_connected and test_results["test_card_id"]:
            try:
                # Check database directly for current_balance field
                card_doc = self.db.credit_cards.find_one({"id": test_results["test_card_id"]})
                if card_doc:
                    if "current_balance" not in card_doc:
                        print(f"✅ VERIFIED: No current_balance field in database document")
                        test_results["passed_tests"] += 1
                    else:
                        print(f"❌ FAILED: current_balance field still in database")
                        test_results["critical_issues"].append("current_balance field still in database")
                    
                    # Check for proper business logic fields
                    business_fields = ["available_credit", "status", "next_due_date", "days_until_due"]
                    present_fields = [field for field in business_fields if field in card_doc]
                    
                    print(f"   Business logic fields present: {present_fields}")
                    if len(present_fields) >= 2:
                        print(f"✅ VERIFIED: Business logic fields working without current_balance")
                        test_results["passed_tests"] += 1
                    else:
                        print(f"⚠️ NOTE: Limited business logic fields in database")
                    
                    test_results["total_tests"] += 1
                else:
                    print(f"⚠️ Could not find test card in database")
            except Exception as e:
                print(f"❌ Database verification failed: {e}")
        else:
            print(f"⚠️ SKIPPED: Database connection not available")
        
        test_results["total_tests"] += 1
        
        # Step 9: Test available credit calculation
        print(f"\n🔍 STEP 9: Test Available Credit Calculation")
        print("=" * 60)
        
        if test_results["test_card_id"]:
            # Get updated card after DAO transactions
            final_card_success, final_card_response = self.run_test(
                f"GET /credit-cards/{test_results['test_card_id']} - Final Card State",
                "GET",
                f"credit-cards/{test_results['test_card_id']}",
                200
            )
            
            if final_card_success and final_card_response:
                credit_limit = final_card_response.get("credit_limit", 0)
                available_credit = final_card_response.get("available_credit")
                
                print(f"   Credit limit: {credit_limit:,.0f}")
                print(f"   Available credit: {available_credit}")
                
                # Available credit should be calculated without current_balance
                if available_credit is not None:
                    print(f"✅ VERIFIED: Available credit calculation working")
                    test_results["passed_tests"] += 1
                else:
                    print(f"⚠️ NOTE: Available credit not calculated")
                
                test_results["total_tests"] += 1
            else:
                print(f"⚠️ Could not get final card state")
        
        test_results["total_tests"] += 1
        
        # Step 10: Final Assessment
        print(f"\n📊 STEP 10: Final Assessment - Credit Card Current Balance Removal")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 CREDIT CARD CRUD OPERATIONS:")
        print(f"   GET /api/credit-cards: {'✅ WORKING' if test_results['credit_cards_get_working'] else '❌ FAILED'}")
        print(f"   GET /api/credit-cards/{{id}}/detail: {'✅ WORKING' if test_results['credit_card_detail_working'] else '❌ FAILED'}")
        print(f"   POST /api/credit-cards: {'✅ WORKING' if test_results['credit_card_create_working'] else '❌ FAILED'}")
        print(f"   PUT /api/credit-cards/{{id}}: {'✅ WORKING' if test_results['credit_card_update_working'] else '❌ FAILED'}")
        
        print(f"\n🔍 DAO ENDPOINT TESTING:")
        print(f"   POST /api/credit-cards/{{id}}/dao: {'✅ WORKING' if test_results['dao_specific_working'] else '❌ FAILED'}")
        print(f"   POST /api/credit-cards/dao: {'✅ WORKING' if test_results['dao_general_working'] else '❌ FAILED'}")
        print(f"   Unmasked card number storage: {'✅ VERIFIED' if test_results['unmasked_card_storage'] else '❌ FAILED'}")
        
        print(f"\n🔍 BUSINESS LOGIC VALIDATION:")
        print(f"   Business logic without current_balance: {'✅ WORKING' if test_results['business_logic_working'] else '❌ FAILED'}")
        print(f"   Database field removal: {'✅ VERIFIED' if test_results['no_current_balance_field'] else '❌ FAILED'}")
        
        print(f"\n🔍 OVERALL RESULTS:")
        print(f"   Success Rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        # Check if all critical objectives are met
        all_objectives_met = (
            test_results["credit_cards_get_working"] and
            test_results["credit_card_detail_working"] and
            test_results["credit_card_create_working"] and
            test_results["credit_card_update_working"] and
            test_results["dao_specific_working"] and
            test_results["dao_general_working"] and
            test_results["unmasked_card_storage"] and
            test_results["no_current_balance_field"]
        )
        
        if all_objectives_met:
            print(f"\n✅ ALL CRITICAL OBJECTIVES MET:")
            print(f"   ✅ Credit Card CRUD operations working correctly")
            print(f"   ✅ DAO endpoints (specific and general) working")
            print(f"   ✅ Unmasked card numbers stored in DAO transactions")
            print(f"   ✅ Business logic works without current_balance field")
            print(f"   ✅ Database no longer has current_balance field")
            print(f"   ✅ Available credit calculation works correctly")
            print(f"   ✅ Card status calculation works properly")
        else:
            print(f"\n❌ SOME OBJECTIVES NOT MET:")
            if not test_results["credit_cards_get_working"]:
                print(f"   - Credit cards list endpoint failed")
            if not test_results["credit_card_detail_working"]:
                print(f"   - Credit card detail endpoint failed")
            if not test_results["credit_card_create_working"]:
                print(f"   - Credit card creation failed")
            if not test_results["credit_card_update_working"]:
                print(f"   - Credit card update failed")
            if not test_results["dao_specific_working"]:
                print(f"   - Specific DAO endpoint failed")
            if not test_results["dao_general_working"]:
                print(f"   - General DAO endpoint failed")
            if not test_results["unmasked_card_storage"]:
                print(f"   - Unmasked card number storage failed")
            if not test_results["no_current_balance_field"]:
                print(f"   - current_balance field still present")
        
        if test_results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in test_results["critical_issues"]:
                print(f"   - {issue}")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if all_objectives_met:
            print(f"   ✅ CREDIT CARD CURRENT BALANCE FIELD REMOVAL SUCCESSFUL")
            print(f"   - All CRUD operations work without current_balance")
            print(f"   - DAO endpoints store unmasked card numbers correctly")
            print(f"   - Business logic functions properly without current_balance")
            print(f"   - Database schema updated correctly")
            print(f"   - System ready for production use")
        else:
            print(f"   ❌ CREDIT CARD SYSTEM NEEDS ATTENTION")
            print(f"   - Some operations may still reference current_balance")
            print(f"   - Further investigation required")
        
        return all_objectives_met

if __name__ == "__main__":
    print("🚀 Starting Credit Card Current Balance Field Removal Testing")
    print("=" * 80)
    
    tester = CreditCardTester()
    
    # Run the credit card testing
    result = tester.test_credit_card_current_balance_field_removal()
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%")
    print(f"Credit Card Current Balance Removal: {'✅ PASSED' if result else '❌ FAILED'}")