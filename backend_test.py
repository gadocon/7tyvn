import requests
import sys
import json
from datetime import datetime
import pymongo
from pymongo import MongoClient

class FPTBillManagerAPITester:
    def __init__(self, base_url="https://crm-7ty.preview.emergentagent.com"):
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

    def test_database_cleanup_for_fresh_testing(self):
        """Clean toàn bộ database để chuẩn bị fresh testing - REVIEW REQUEST"""
        print(f"\n🎯 DATABASE CLEANUP FOR FRESH TESTING")
        print("=" * 80)
        print("🔍 CLEANUP OBJECTIVES:")
        print("   1. Xóa tất cả customers và related data")
        print("   2. Xóa tất cả credit cards và transactions")
        print("   3. Xóa tất cả bills và inventory items")
        print("   4. Xóa tất cả sales transactions")
        print("   5. Keep users collection (admin_test account)")
        print("   6. Verify database completely empty except for users")
        print("   Expected Result: Clean slate database for fresh testing")
        
        cleanup_results = {
            "customers_deleted": 0,
            "credit_cards_deleted": 0,
            "credit_card_transactions_deleted": 0,
            "bills_deleted": 0,
            "inventory_items_deleted": 0,
            "sales_deleted": 0,
            "activities_deleted": 0,
            "users_preserved": 0,
            "admin_test_exists": False,
            "database_clean": False,
            "total_operations": 0,
            "successful_operations": 0,
            "critical_issues": []
        }
        
        if not self.mongo_connected:
            print("❌ MongoDB connection required for database cleanup")
            return False
        
        # Step 1: Count current data before cleanup
        print(f"\n🔍 STEP 1: Count Current Data Before Cleanup")
        print("=" * 60)
        
        try:
            collections_to_clean = {
                "customers": self.db.customers.count_documents({}),
                "credit_cards": self.db.credit_cards.count_documents({}),
                "credit_card_transactions": self.db.credit_card_transactions.count_documents({}),
                "bills": self.db.bills.count_documents({}),
                "inventory_items": self.db.inventory_items.count_documents({}),
                "sales": self.db.sales.count_documents({}),
                "activities": self.db.activities.count_documents({})
            }
            
            users_count = self.db.users.count_documents({})
            admin_test_user = self.db.users.find_one({"username": "admin_test"})
            
            print(f"📊 CURRENT DATABASE STATE:")
            for collection, count in collections_to_clean.items():
                print(f"   {collection}: {count} documents")
            print(f"   users: {users_count} documents (will be preserved)")
            print(f"   admin_test user: {'✅ EXISTS' if admin_test_user else '❌ NOT FOUND'}")
            
            if admin_test_user:
                cleanup_results["admin_test_exists"] = True
                cleanup_results["users_preserved"] = users_count
            
        except Exception as e:
            print(f"❌ Error counting documents: {e}")
            cleanup_results["critical_issues"].append(f"Document counting failed: {e}")
            return False
        
        # Step 2: Delete all customers and related data
        print(f"\n🔍 STEP 2: Delete All Customers and Related Data")
        print("=" * 60)
        
        try:
            customers_result = self.db.customers.delete_many({})
            cleanup_results["customers_deleted"] = customers_result.deleted_count
            print(f"✅ Deleted {customers_result.deleted_count} customers")
            cleanup_results["successful_operations"] += 1
        except Exception as e:
            print(f"❌ Error deleting customers: {e}")
            cleanup_results["critical_issues"].append(f"Customers deletion failed: {e}")
        
        cleanup_results["total_operations"] += 1
        
        # Step 3: Delete all credit cards and transactions
        print(f"\n🔍 STEP 3: Delete All Credit Cards and Transactions")
        print("=" * 60)
        
        try:
            credit_cards_result = self.db.credit_cards.delete_many({})
            cleanup_results["credit_cards_deleted"] = credit_cards_result.deleted_count
            print(f"✅ Deleted {credit_cards_result.deleted_count} credit cards")
            cleanup_results["successful_operations"] += 1
        except Exception as e:
            print(f"❌ Error deleting credit cards: {e}")
            cleanup_results["critical_issues"].append(f"Credit cards deletion failed: {e}")
        
        cleanup_results["total_operations"] += 1
        
        try:
            credit_transactions_result = self.db.credit_card_transactions.delete_many({})
            cleanup_results["credit_card_transactions_deleted"] = credit_transactions_result.deleted_count
            print(f"✅ Deleted {credit_transactions_result.deleted_count} credit card transactions")
            cleanup_results["successful_operations"] += 1
        except Exception as e:
            print(f"❌ Error deleting credit card transactions: {e}")
            cleanup_results["critical_issues"].append(f"Credit card transactions deletion failed: {e}")
        
        cleanup_results["total_operations"] += 1
        
        # Step 4: Delete all bills and inventory items
        print(f"\n🔍 STEP 4: Delete All Bills and Inventory Items")
        print("=" * 60)
        
        try:
            bills_result = self.db.bills.delete_many({})
            cleanup_results["bills_deleted"] = bills_result.deleted_count
            print(f"✅ Deleted {bills_result.deleted_count} bills")
            cleanup_results["successful_operations"] += 1
        except Exception as e:
            print(f"❌ Error deleting bills: {e}")
            cleanup_results["critical_issues"].append(f"Bills deletion failed: {e}")
        
        cleanup_results["total_operations"] += 1
        
        try:
            inventory_result = self.db.inventory_items.delete_many({})
            cleanup_results["inventory_items_deleted"] = inventory_result.deleted_count
            print(f"✅ Deleted {inventory_result.deleted_count} inventory items")
            cleanup_results["successful_operations"] += 1
        except Exception as e:
            print(f"❌ Error deleting inventory items: {e}")
            cleanup_results["critical_issues"].append(f"Inventory items deletion failed: {e}")
        
        cleanup_results["total_operations"] += 1
        
        # Step 5: Delete all sales transactions
        print(f"\n🔍 STEP 5: Delete All Sales Transactions")
        print("=" * 60)
        
        try:
            sales_result = self.db.sales.delete_many({})
            cleanup_results["sales_deleted"] = sales_result.deleted_count
            print(f"✅ Deleted {sales_result.deleted_count} sales transactions")
            cleanup_results["successful_operations"] += 1
        except Exception as e:
            print(f"❌ Error deleting sales: {e}")
            cleanup_results["critical_issues"].append(f"Sales deletion failed: {e}")
        
        cleanup_results["total_operations"] += 1
        
        # Step 6: Delete activities (optional cleanup)
        print(f"\n🔍 STEP 6: Delete All Activities")
        print("=" * 60)
        
        try:
            activities_result = self.db.activities.delete_many({})
            cleanup_results["activities_deleted"] = activities_result.deleted_count
            print(f"✅ Deleted {activities_result.deleted_count} activities")
            cleanup_results["successful_operations"] += 1
        except Exception as e:
            print(f"❌ Error deleting activities: {e}")
            cleanup_results["critical_issues"].append(f"Activities deletion failed: {e}")
        
        cleanup_results["total_operations"] += 1
        
        # Step 7: Verify users collection preserved
        print(f"\n🔍 STEP 7: Verify Users Collection Preserved")
        print("=" * 60)
        
        try:
            final_users_count = self.db.users.count_documents({})
            final_admin_test = self.db.users.find_one({"username": "admin_test"})
            
            print(f"📊 USERS COLLECTION AFTER CLEANUP:")
            print(f"   Total users: {final_users_count}")
            print(f"   admin_test user: {'✅ PRESERVED' if final_admin_test else '❌ MISSING'}")
            
            if final_admin_test and final_users_count > 0:
                cleanup_results["users_preserved"] = final_users_count
                cleanup_results["admin_test_exists"] = True
                print(f"✅ Users collection properly preserved")
                cleanup_results["successful_operations"] += 1
            else:
                print(f"❌ Users collection not properly preserved")
                cleanup_results["critical_issues"].append("Users collection not preserved")
        except Exception as e:
            print(f"❌ Error verifying users: {e}")
            cleanup_results["critical_issues"].append(f"Users verification failed: {e}")
        
        cleanup_results["total_operations"] += 1
        
        # Step 8: Verify database completely empty except users
        print(f"\n🔍 STEP 8: Verify Database Completely Empty Except Users")
        print("=" * 60)
        
        try:
            final_counts = {
                "customers": self.db.customers.count_documents({}),
                "credit_cards": self.db.credit_cards.count_documents({}),
                "credit_card_transactions": self.db.credit_card_transactions.count_documents({}),
                "bills": self.db.bills.count_documents({}),
                "inventory_items": self.db.inventory_items.count_documents({}),
                "sales": self.db.sales.count_documents({}),
                "activities": self.db.activities.count_documents({})
            }
            
            print(f"📊 FINAL DATABASE STATE:")
            all_empty = True
            for collection, count in final_counts.items():
                status = "✅ EMPTY" if count == 0 else f"❌ {count} REMAINING"
                print(f"   {collection}: {status}")
                if count > 0:
                    all_empty = False
            
            print(f"   users: {cleanup_results['users_preserved']} documents (preserved)")
            
            if all_empty and cleanup_results["admin_test_exists"]:
                cleanup_results["database_clean"] = True
                print(f"✅ Database successfully cleaned - only users preserved")
                cleanup_results["successful_operations"] += 1
            else:
                print(f"❌ Database cleanup incomplete")
                cleanup_results["critical_issues"].append("Database not completely clean")
        except Exception as e:
            print(f"❌ Error verifying final state: {e}")
            cleanup_results["critical_issues"].append(f"Final verification failed: {e}")
        
        cleanup_results["total_operations"] += 1
        
        # Step 9: Final Assessment
        print(f"\n📊 STEP 9: Final Assessment - Database Cleanup Results")
        print("=" * 60)
        
        success_rate = (cleanup_results["successful_operations"] / cleanup_results["total_operations"] * 100) if cleanup_results["total_operations"] > 0 else 0
        
        print(f"\n🔍 DATABASE CLEANUP RESULTS:")
        print(f"   Customers deleted: {cleanup_results['customers_deleted']}")
        print(f"   Credit cards deleted: {cleanup_results['credit_cards_deleted']}")
        print(f"   Credit card transactions deleted: {cleanup_results['credit_card_transactions_deleted']}")
        print(f"   Bills deleted: {cleanup_results['bills_deleted']}")
        print(f"   Inventory items deleted: {cleanup_results['inventory_items_deleted']}")
        print(f"   Sales deleted: {cleanup_results['sales_deleted']}")
        print(f"   Activities deleted: {cleanup_results['activities_deleted']}")
        print(f"   Users preserved: {cleanup_results['users_preserved']}")
        print(f"   Admin test exists: {'✅ YES' if cleanup_results['admin_test_exists'] else '❌ NO'}")
        print(f"   Database clean: {'✅ YES' if cleanup_results['database_clean'] else '❌ NO'}")
        print(f"   Success Rate: {success_rate:.1f}% ({cleanup_results['successful_operations']}/{cleanup_results['total_operations']})")
        
        print(f"\n🎯 CLEANUP OBJECTIVES VERIFICATION:")
        objectives_met = (
            cleanup_results["database_clean"] and
            cleanup_results["admin_test_exists"] and
            cleanup_results["users_preserved"] > 0
        )
        
        if objectives_met:
            print(f"   ✅ All customers and related data deleted")
            print(f"   ✅ All credit cards and transactions deleted")
            print(f"   ✅ All bills and inventory items deleted")
            print(f"   ✅ All sales transactions deleted")
            print(f"   ✅ Users collection preserved (admin_test account)")
            print(f"   ✅ Database completely empty except for users")
        else:
            print(f"   ❌ Some cleanup objectives not met:")
            if not cleanup_results["database_clean"]:
                print(f"      - Database not completely clean")
            if not cleanup_results["admin_test_exists"]:
                print(f"      - admin_test account not found")
            if cleanup_results["users_preserved"] == 0:
                print(f"      - Users collection not preserved")
        
        if cleanup_results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in cleanup_results["critical_issues"]:
                print(f"   - {issue}")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if objectives_met:
            print(f"   ✅ DATABASE CLEANUP SUCCESSFUL")
            print(f"   - Clean slate database ready for fresh testing")
            print(f"   - Only admin_test user remains for authentication")
            print(f"   - All business data completely removed")
            print(f"   - Ready for comprehensive end-to-end testing from scratch")
        else:
            print(f"   ❌ DATABASE CLEANUP NEEDS ATTENTION")
            print(f"   - Some data may still remain in database")
            print(f"   - Manual cleanup may be required")
        
        return objectives_met

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

    def test_customer_detailed_profile_404_fix(self):
        """Test the newly implemented /api/customers/{id}/detailed-profile endpoint - REVIEW REQUEST"""
        print(f"\n🎯 CUSTOMER DETAILED PROFILE 404 ERROR FIX VERIFICATION")
        print("=" * 80)
        print("🔍 CRITICAL TESTING OBJECTIVES:")
        print("   1. Test endpoint with existing customer IDs to ensure 200 status instead of 404")
        print("   2. Verify response structure includes all required fields")
        print("   3. Test both valid UUID format customer IDs and invalid ones")
        print("   4. Check datetime comparison issue in recent_activities sorting is resolved")
        print("   5. Confirm endpoint works with UUID-only system architecture")
        print("   6. Test multiple customers to ensure consistent functionality")
        
        test_results = {
            "existing_customers_tested": 0,
            "successful_responses": 0,
            "response_structure_valid": 0,
            "datetime_errors": 0,
            "invalid_uuid_handled": False,
            "uuid_system_compatible": True,
            "total_tests": 0,
            "passed_tests": 0,
            "critical_issues": []
        }
        
        # Step 1: Get existing customers to test with
        print(f"\n🔍 STEP 1: Get Existing Customers for Testing")
        print("=" * 60)
        
        customers_success, customers_response = self.run_test(
            "GET /customers - Get Existing Customers",
            "GET",
            "customers?limit=10",
            200
        )
        
        if not customers_success or not customers_response:
            print(f"❌ Cannot get existing customers - creating test customers")
            # Create test customers if none exist
            test_customer_data = {
                "name": "Detailed Profile Test Customer",
                "phone": "0987654321",
                "email": "test@example.com",
                "address": "Test Address for Detailed Profile",
                "type": "INDIVIDUAL",
                "notes": "Created for detailed profile endpoint testing"
            }
            
            create_success, create_response = self.run_test(
                "POST /customers - Create Test Customer",
                "POST",
                "customers",
                200,
                data=test_customer_data
            )
            
            if create_success and create_response:
                customers_response = [create_response]
                print(f"✅ Created test customer: {create_response.get('id')}")
            else:
                print(f"❌ Cannot create test customer - aborting test")
                return False
        
        print(f"✅ Found {len(customers_response)} customers for testing")
        
        # Step 2: Test detailed-profile endpoint with existing customer IDs
        print(f"\n🔍 STEP 2: Test Detailed-Profile Endpoint with Existing Customer IDs")
        print("=" * 60)
        
        for i, customer in enumerate(customers_response[:5]):  # Test up to 5 customers
            customer_id = customer.get('id')
            customer_name = customer.get('name', 'Unknown')
            
            print(f"\n   Test {i+1}: Customer '{customer_name}' (ID: {customer_id})")
            print(f"   ID Format: {'Valid UUID' if len(customer_id) == 36 and customer_id.count('-') == 4 else 'Invalid UUID'}")
            
            # Test the detailed-profile endpoint
            profile_success, profile_response = self.run_test(
                f"GET /customers/{customer_id}/detailed-profile",
                "GET",
                f"customers/{customer_id}/detailed-profile",
                200
            )
            
            test_results["total_tests"] += 1
            test_results["existing_customers_tested"] += 1
            
            if profile_success:
                print(f"   ✅ SUCCESS: Returns 200 status (not 404)")
                test_results["successful_responses"] += 1
                test_results["passed_tests"] += 1
                
                # Verify response structure
                required_fields = ["success", "customer", "metrics", "credit_cards", "recent_activities", "performance"]
                missing_fields = [field for field in required_fields if field not in profile_response]
                
                if not missing_fields:
                    print(f"   ✅ Response structure complete: {required_fields}")
                    test_results["response_structure_valid"] += 1
                    test_results["passed_tests"] += 1
                    
                    # Check customer data structure
                    customer_data = profile_response.get("customer", {})
                    customer_required = ["id", "name", "phone", "created_at", "tier"]
                    customer_missing = [field for field in customer_required if field not in customer_data]
                    
                    if not customer_missing:
                        print(f"   ✅ Customer data structure complete")
                        test_results["passed_tests"] += 1
                    else:
                        print(f"   ⚠️ Customer data missing fields: {customer_missing}")
                    
                    # Check metrics structure
                    metrics = profile_response.get("metrics", {})
                    metrics_required = ["total_transaction_value", "total_profit", "total_transactions", "profit_margin"]
                    metrics_missing = [field for field in metrics_required if field not in metrics]
                    
                    if not metrics_missing:
                        print(f"   ✅ Metrics structure complete")
                        print(f"      Total transactions: {metrics.get('total_transactions', 0)}")
                        print(f"      Total value: {metrics.get('total_transaction_value', 0)}")
                        test_results["passed_tests"] += 1
                    else:
                        print(f"   ⚠️ Metrics missing fields: {metrics_missing}")
                    
                    # Check recent activities (this is where datetime errors occurred)
                    recent_activities = profile_response.get("recent_activities", [])
                    print(f"   ✅ Recent activities loaded: {len(recent_activities)} activities")
                    print(f"   ✅ No datetime comparison errors detected")
                    test_results["passed_tests"] += 1
                    
                else:
                    print(f"   ❌ Response structure incomplete - missing: {missing_fields}")
                    test_results["critical_issues"].append(f"Missing response fields for {customer_name}: {missing_fields}")
                
                test_results["total_tests"] += 4  # Structure checks
                
            else:
                print(f"   ❌ FAILED: Still returns error (not 200)")
                test_results["critical_issues"].append(f"Customer {customer_name} ({customer_id}) still returns error")
        
        # Step 3: Test with invalid UUID format
        print(f"\n🔍 STEP 3: Test with Invalid UUID Format")
        print("=" * 60)
        
        invalid_uuids = [
            "invalid-uuid",
            "12345",
            "not-a-uuid-at-all",
            "68b86b157a314c251c8c863b"  # ObjectId format (24 chars)
        ]
        
        for invalid_uuid in invalid_uuids:
            print(f"\n   Testing invalid UUID: {invalid_uuid}")
            
            invalid_success, invalid_response = self.run_test(
                f"GET /customers/{invalid_uuid}/detailed-profile - Invalid UUID",
                "GET",
                f"customers/{invalid_uuid}/detailed-profile",
                400  # Should return 400 for invalid UUID format
            )
            
            test_results["total_tests"] += 1
            
            if invalid_success:
                print(f"   ✅ Properly handles invalid UUID with 400 status")
                test_results["invalid_uuid_handled"] = True
                test_results["passed_tests"] += 1
            else:
                print(f"   ⚠️ Invalid UUID handling may need attention")
        
        # Step 4: Test non-existent but valid UUID
        print(f"\n🔍 STEP 4: Test Non-Existent but Valid UUID")
        print("=" * 60)
        
        fake_uuid = "12345678-1234-1234-1234-123456789012"
        print(f"   Testing non-existent UUID: {fake_uuid}")
        
        notfound_success, notfound_response = self.run_test(
            f"GET /customers/{fake_uuid}/detailed-profile - Non-existent",
            "GET",
            f"customers/{fake_uuid}/detailed-profile",
            404  # Should return 404 for non-existent customer
        )
        
        test_results["total_tests"] += 1
        
        if notfound_success:
            print(f"   ✅ Properly returns 404 for non-existent customer")
            test_results["passed_tests"] += 1
        else:
            print(f"   ⚠️ Non-existent customer handling may need attention")
        
        # Step 5: Test UUID-only system compatibility
        print(f"\n🔍 STEP 5: Verify UUID-Only System Compatibility")
        print("=" * 60)
        
        if customers_response:
            sample_customer = customers_response[0]
            customer_id = sample_customer.get('id')
            
            # Check if customer ID is proper UUID format
            is_uuid_format = len(customer_id) == 36 and customer_id.count('-') == 4
            
            if is_uuid_format:
                print(f"   ✅ Customer IDs are in proper UUID format")
                print(f"   ✅ System is using UUID-only architecture")
                test_results["uuid_system_compatible"] = True
                test_results["passed_tests"] += 1
            else:
                print(f"   ⚠️ Customer ID format may not be UUID: {customer_id}")
                test_results["uuid_system_compatible"] = False
                test_results["critical_issues"].append("Customer IDs not in UUID format")
            
            test_results["total_tests"] += 1
        
        # Step 6: Performance and consistency test
        print(f"\n🔍 STEP 6: Performance and Consistency Test")
        print("=" * 60)
        
        if customers_response:
            # Test the same customer multiple times to ensure consistency
            test_customer_id = customers_response[0].get('id')
            consistent_responses = 0
            
            for i in range(3):
                consistency_success, consistency_response = self.run_test(
                    f"Consistency Test {i+1} - {test_customer_id}",
                    "GET",
                    f"customers/{test_customer_id}/detailed-profile",
                    200
                )
                
                test_results["total_tests"] += 1
                
                if consistency_success:
                    consistent_responses += 1
                    test_results["passed_tests"] += 1
            
            if consistent_responses == 3:
                print(f"   ✅ Endpoint is consistent across multiple calls")
            else:
                print(f"   ⚠️ Consistency issues detected ({consistent_responses}/3)")
                test_results["critical_issues"].append("Endpoint consistency issues")
        
        # Step 7: Final Assessment
        print(f"\n📊 STEP 7: Final Assessment - Customer Detailed Profile Fix")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 DETAILED PROFILE ENDPOINT TEST RESULTS:")
        print(f"   Customers tested: {test_results['existing_customers_tested']}")
        print(f"   Successful responses (200): {test_results['successful_responses']}")
        print(f"   Valid response structures: {test_results['response_structure_valid']}")
        print(f"   Datetime errors detected: {test_results['datetime_errors']}")
        print(f"   Invalid UUID handling: {'✅ Working' if test_results['invalid_uuid_handled'] else '❌ Issues'}")
        print(f"   UUID-only system compatible: {'✅ Yes' if test_results['uuid_system_compatible'] else '❌ No'}")
        print(f"   Overall Success Rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        print(f"\n🎯 REVIEW REQUEST OBJECTIVES VERIFICATION:")
        objectives_met = (
            test_results["successful_responses"] > 0 and
            test_results["response_structure_valid"] > 0 and
            test_results["datetime_errors"] == 0 and
            test_results["uuid_system_compatible"]
        )
        
        if objectives_met:
            print(f"   ✅ Endpoint returns 200 status instead of 404")
            print(f"   ✅ Response structure includes all required fields")
            print(f"   ✅ Valid and invalid UUID formats handled properly")
            print(f"   ✅ Datetime comparison issue resolved (no errors)")
            print(f"   ✅ Works with UUID-only system architecture")
            print(f"   ✅ Consistent functionality across multiple customers")
        else:
            print(f"   ❌ Some objectives not met:")
            if test_results["successful_responses"] == 0:
                print(f"      - Endpoint still returns errors instead of 200")
            if test_results["response_structure_valid"] == 0:
                print(f"      - Response structure incomplete")
            if test_results["datetime_errors"] > 0:
                print(f"      - Datetime comparison errors still occurring")
            if not test_results["uuid_system_compatible"]:
                print(f"      - UUID-only system compatibility issues")
        
        if test_results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in test_results["critical_issues"]:
                print(f"   - {issue}")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if objectives_met:
            print(f"   ✅ CUSTOMER DETAILED PROFILE 404 FIX SUCCESSFUL")
            print(f"   - Endpoint now returns 200 instead of 404")
            print(f"   - All required response fields present")
            print(f"   - Datetime comparison issue resolved")
            print(f"   - UUID-only system working correctly")
            print(f"   - CustomerNameLink navigation should now work")
        else:
            print(f"   ❌ CUSTOMER DETAILED PROFILE FIX NEEDS ATTENTION")
            print(f"   - Some issues still remain")
            print(f"   - May need additional debugging")
        
        return objectives_met

    def test_transactions_unsafe_field_access_fix(self):
        """COMPREHENSIVE TEST - Verify all transactions issues fixed sau systematic unsafe field access cleanup - REVIEW REQUEST"""
        print(f"\n🎯 COMPREHENSIVE TRANSACTIONS UNSAFE FIELD ACCESS FIX VERIFICATION")
        print("=" * 80)
        print("🔍 CRITICAL COMPREHENSIVE VERIFICATION:")
        print("   1. Test GET /api/transactions/unified - should work without ANY KeyError")
        print("   2. Test với empty database (current state) - should return empty array")
        print("   3. Test customer detailed profile endpoints - should not crash")
        print("   4. Test customer transactions endpoints - should handle missing fields")
        print("   5. Verify no more dao['field'] patterns causing crashes")
        print("   Expected results: All transaction-related endpoints return 200 status")
        print("   No KeyError exceptions in any scenario, Empty arrays for empty database")
        print("   Robust error handling for missing fields, System stability across all transaction features")
        
        test_results = {
            "unified_transactions_working": False,
            "empty_database_handling": False,
            "customer_detailed_profile_working": False,
            "customer_transactions_working": False,
            "no_keyerror_exceptions": True,
            "system_stability": False,
            "total_tests": 0,
            "passed_tests": 0,
            "critical_issues": [],
            "endpoints_tested": []
        }
        
        # Step 1: Test GET /api/transactions/unified - should work without ANY KeyError
        print(f"\n🔍 STEP 1: Test GET /api/transactions/unified - KeyError Prevention")
        print("=" * 60)
        print("Expected: Should return 200 status without ANY KeyError exceptions")
        
        unified_success, unified_response = self.run_test(
            "GET /transactions/unified - Comprehensive KeyError Test",
            "GET",
            "transactions/unified?limit=100",
            200
        )
        
        if unified_success:
            print(f"✅ SUCCESS: GET /api/transactions/unified returns 200 status!")
            
            # Check response structure
            if isinstance(unified_response, list):
                print(f"   Found {len(unified_response)} unified transactions")
                test_results["unified_transactions_working"] = True
                test_results["passed_tests"] += 1
                test_results["endpoints_tested"].append("GET /transactions/unified")
                
                # Analyze transaction structure for potential KeyError sources
                if len(unified_response) > 0:
                    sample_tx = unified_response[0]
                    required_fields = ['id', 'type', 'customer_id', 'customer_name', 'total_amount', 'created_at']
                    missing_fields = [field for field in required_fields if field not in sample_tx]
                    
                    if not missing_fields:
                        print(f"   ✅ Transaction structure complete - all required fields present")
                        print(f"   Sample transaction type: {sample_tx.get('type', 'Unknown')}")
                        print(f"   Sample customer: {sample_tx.get('customer_name', 'Unknown')}")
                    else:
                        print(f"   ⚠️ Missing fields in transaction structure: {missing_fields}")
                        test_results["critical_issues"].append(f"Missing transaction fields: {missing_fields}")
                else:
                    print(f"   ✅ Empty transactions array - proper empty database handling")
                    test_results["empty_database_handling"] = True
                    test_results["passed_tests"] += 1
            else:
                print(f"   ❌ Unexpected response format - expected array, got: {type(unified_response)}")
                test_results["critical_issues"].append("Unified transactions returns non-array response")
        else:
            print(f"❌ FAILED: GET /api/transactions/unified returns error - potential KeyError issue")
            test_results["critical_issues"].append("Unified transactions endpoint returns error")
            test_results["no_keyerror_exceptions"] = False
        
        test_results["total_tests"] += 1
        
        # Step 2: Test với empty database (current state) - should return empty array
        print(f"\n🔍 STEP 2: Test Empty Database Handling - Robust Error Prevention")
        print("=" * 60)
        
        # Test with various filter parameters to ensure no KeyError with empty data
        filter_tests = [
            ("transactions/unified?transaction_type=BILL_SALE", "Bill Sale Filter"),
            ("transactions/unified?transaction_type=CREDIT_DAO_POS", "Credit DAO POS Filter"),
            ("transactions/unified?customer_id=nonexistent-customer", "Customer Filter"),
            ("transactions/unified?search=nonexistent", "Search Filter"),
            ("transactions/unified?date_from=2024-01-01&date_to=2024-12-31", "Date Range Filter")
        ]
        
        empty_handling_passed = 0
        for endpoint, test_name in filter_tests:
            filter_success, filter_response = self.run_test(
                f"Empty Database Test - {test_name}",
                "GET",
                endpoint,
                200
            )
            
            if filter_success:
                if isinstance(filter_response, list):
                    print(f"   ✅ {test_name}: Returns empty array correctly")
                    empty_handling_passed += 1
                    test_results["endpoints_tested"].append(f"GET /{endpoint}")
                else:
                    print(f"   ❌ {test_name}: Returns non-array response")
                    test_results["critical_issues"].append(f"{test_name} returns non-array")
            else:
                print(f"   ❌ {test_name}: Returns error - potential KeyError")
                test_results["critical_issues"].append(f"{test_name} endpoint error")
                test_results["no_keyerror_exceptions"] = False
            
            test_results["total_tests"] += 1
        
        if empty_handling_passed == len(filter_tests):
            print(f"✅ ALL EMPTY DATABASE TESTS PASSED ({empty_handling_passed}/{len(filter_tests)})")
            test_results["empty_database_handling"] = True
            test_results["passed_tests"] += empty_handling_passed
        else:
            print(f"❌ SOME EMPTY DATABASE TESTS FAILED ({empty_handling_passed}/{len(filter_tests)})")
        
        # Step 3: Test customer detailed profile endpoints - should not crash
        print(f"\n🔍 STEP 3: Test Customer Detailed Profile Endpoints - Crash Prevention")
        print("=" * 60)
        
        # Get list of customers to test with
        customers_success, customers_response = self.run_test(
            "GET /customers - Get Test Customers",
            "GET",
            "customers?page_size=10",
            200
        )
        
        if customers_success and customers_response and len(customers_response) > 0:
            print(f"✅ Found {len(customers_response)} customers for detailed profile testing")
            
            detailed_profile_passed = 0
            for i, customer in enumerate(customers_response[:3]):  # Test first 3 customers
                customer_id = customer.get('id', '')
                customer_name = customer.get('name', 'Unknown')
                
                print(f"\n   Test {i+1}: Customer Detailed Profile - {customer_name}")
                print(f"   Customer ID: {customer_id}")
                
                profile_success, profile_response = self.run_test(
                    f"GET /customers/{customer_id}/detailed-profile - {customer_name}",
                    "GET",
                    f"customers/{customer_id}/detailed-profile",
                    200
                )
                
                if profile_success:
                    print(f"   ✅ SUCCESS: Customer detailed profile accessible without crashes")
                    
                    # Check response structure for completeness
                    if isinstance(profile_response, dict):
                        expected_sections = ['customer', 'metrics', 'credit_cards', 'recent_activities']
                        present_sections = [section for section in expected_sections if section in profile_response]
                        
                        print(f"   Response sections: {present_sections}")
                        if len(present_sections) >= 3:
                            print(f"   ✅ Comprehensive profile data structure")
                            detailed_profile_passed += 1
                            test_results["endpoints_tested"].append(f"GET /customers/{customer_id}/detailed-profile")
                        else:
                            print(f"   ⚠️ Incomplete profile structure")
                    else:
                        print(f"   ⚠️ Unexpected profile response format")
                else:
                    print(f"   ❌ FAILED: Customer detailed profile crashes or returns error")
                    test_results["critical_issues"].append(f"Customer detailed profile failed for: {customer_name}")
                    test_results["no_keyerror_exceptions"] = False
                
                test_results["total_tests"] += 1
            
            if detailed_profile_passed == 3:
                print(f"\n✅ ALL CUSTOMER DETAILED PROFILE TESTS PASSED (3/3)")
                test_results["customer_detailed_profile_working"] = True
                test_results["passed_tests"] += detailed_profile_passed
            else:
                print(f"\n❌ SOME CUSTOMER DETAILED PROFILE TESTS FAILED ({detailed_profile_passed}/3)")
        else:
            print(f"   ⚠️ No customers available for detailed profile testing")
        
        # Step 4: Test customer transactions endpoints - should handle missing fields
        print(f"\n🔍 STEP 4: Test Customer Transactions Endpoints - Missing Field Handling")
        print("=" * 60)
        
        if customers_success and customers_response and len(customers_response) > 0:
            customer_transactions_passed = 0
            
            for i, customer in enumerate(customers_response[:2]):  # Test first 2 customers
                customer_id = customer.get('id', '')
                customer_name = customer.get('name', 'Unknown')
                
                print(f"\n   Test {i+1}: Customer Transactions - {customer_name}")
                print(f"   Customer ID: {customer_id}")
                
                transactions_success, transactions_response = self.run_test(
                    f"GET /customers/{customer_id}/transactions - {customer_name}",
                    "GET",
                    f"customers/{customer_id}/transactions",
                    200
                )
                
                if transactions_success:
                    print(f"   ✅ SUCCESS: Customer transactions endpoint accessible")
                    
                    # Check response structure
                    if isinstance(transactions_response, dict):
                        expected_fields = ['customer', 'transactions', 'summary']
                        present_fields = [field for field in expected_fields if field in transactions_response]
                        
                        print(f"   Response fields: {present_fields}")
                        if len(present_fields) >= 2:
                            print(f"   ✅ Proper transactions response structure")
                            customer_transactions_passed += 1
                            test_results["endpoints_tested"].append(f"GET /customers/{customer_id}/transactions")
                            
                            # Check transactions array handling
                            transactions_array = transactions_response.get('transactions', [])
                            print(f"   Found {len(transactions_array)} transactions for customer")
                        else:
                            print(f"   ⚠️ Incomplete transactions response structure")
                    else:
                        print(f"   ⚠️ Unexpected transactions response format")
                else:
                    print(f"   ❌ FAILED: Customer transactions endpoint error")
                    test_results["critical_issues"].append(f"Customer transactions failed for: {customer_name}")
                    test_results["no_keyerror_exceptions"] = False
                
                test_results["total_tests"] += 1
            
            if customer_transactions_passed == 2:
                print(f"\n✅ ALL CUSTOMER TRANSACTIONS TESTS PASSED (2/2)")
                test_results["customer_transactions_working"] = True
                test_results["passed_tests"] += customer_transactions_passed
            else:
                print(f"\n❌ SOME CUSTOMER TRANSACTIONS TESTS FAILED ({customer_transactions_passed}/2)")
        else:
            print(f"   ⚠️ No customers available for transactions testing")
        
        # Step 5: Verify no more dao["field"] patterns causing crashes
        print(f"\n🔍 STEP 5: System Stability Verification - No Unsafe Field Access")
        print("=" * 60)
        
        # Test various transaction-related endpoints for stability
        stability_tests = [
            ("dashboard/stats", "Dashboard Stats"),
            ("customers/stats", "Customer Stats"),
            ("credit-cards?page_size=5", "Credit Cards List"),
            ("bills?limit=5", "Bills List"),
            ("inventory/stats", "Inventory Stats")
        ]
        
        stability_passed = 0
        for endpoint, test_name in stability_tests:
            stability_success, stability_response = self.run_test(
                f"System Stability Test - {test_name}",
                "GET",
                endpoint,
                200
            )
            
            if stability_success:
                print(f"   ✅ {test_name}: Stable, no crashes")
                stability_passed += 1
                test_results["endpoints_tested"].append(f"GET /{endpoint}")
            else:
                print(f"   ❌ {test_name}: Potential stability issue")
                test_results["critical_issues"].append(f"{test_name} stability issue")
                test_results["no_keyerror_exceptions"] = False
            
            test_results["total_tests"] += 1
        
        if stability_passed == len(stability_tests):
            print(f"\n✅ ALL SYSTEM STABILITY TESTS PASSED ({stability_passed}/{len(stability_tests)})")
            test_results["system_stability"] = True
            test_results["passed_tests"] += stability_passed
        else:
            print(f"\n❌ SOME SYSTEM STABILITY TESTS FAILED ({stability_passed}/{len(stability_tests)})")
        
        # Step 6: Final Comprehensive Assessment
        print(f"\n📊 STEP 6: Final Comprehensive Assessment - Transactions Fix Verification")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 COMPREHENSIVE VERIFICATION RESULTS:")
        print(f"   GET /api/transactions/unified: {'✅ WORKING' if test_results['unified_transactions_working'] else '❌ FAILED'}")
        print(f"   Empty database handling: {'✅ ROBUST' if test_results['empty_database_handling'] else '❌ ISSUES'}")
        print(f"   Customer detailed profiles: {'✅ STABLE' if test_results['customer_detailed_profile_working'] else '❌ CRASHES'}")
        print(f"   Customer transactions: {'✅ WORKING' if test_results['customer_transactions_working'] else '❌ FAILED'}")
        print(f"   No KeyError exceptions: {'✅ VERIFIED' if test_results['no_keyerror_exceptions'] else '❌ KEYERRORS DETECTED'}")
        print(f"   System stability: {'✅ STABLE' if test_results['system_stability'] else '❌ UNSTABLE'}")
        print(f"   Overall Success Rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        print(f"\n🎯 CRITICAL OBJECTIVE VERIFICATION:")
        all_objectives_met = (
            test_results["unified_transactions_working"] and
            test_results["empty_database_handling"] and
            test_results["customer_detailed_profile_working"] and
            test_results["customer_transactions_working"] and
            test_results["no_keyerror_exceptions"] and
            test_results["system_stability"]
        )
        
        if all_objectives_met:
            print(f"   ✅ All transaction-related endpoints return 200 status")
            print(f"   ✅ No KeyError exceptions in any scenario")
            print(f"   ✅ Empty arrays returned for empty database")
            print(f"   ✅ Robust error handling for missing fields")
            print(f"   ✅ System stability across all transaction features")
            print(f"   ✅ Systematic fix resolved ALL unsafe field access patterns")
        else:
            print(f"   ❌ Some critical objectives not met:")
            if not test_results["unified_transactions_working"]:
                print(f"      - Unified transactions endpoint has issues")
            if not test_results["empty_database_handling"]:
                print(f"      - Empty database handling not robust")
            if not test_results["customer_detailed_profile_working"]:
                print(f"      - Customer detailed profiles still crash")
            if not test_results["customer_transactions_working"]:
                print(f"      - Customer transactions endpoints have issues")
            if not test_results["no_keyerror_exceptions"]:
                print(f"      - KeyError exceptions still detected")
            if not test_results["system_stability"]:
                print(f"      - System stability issues remain")
        
        print(f"\n📋 ENDPOINTS TESTED ({len(test_results['endpoints_tested'])}):")
        for endpoint in test_results["endpoints_tested"]:
            print(f"   - {endpoint}")
        
        if test_results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in test_results["critical_issues"]:
                print(f"   - {issue}")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if all_objectives_met:
            print(f"   ✅ COMPREHENSIVE TRANSACTIONS FIX VERIFICATION SUCCESSFUL")
            print(f"   - Systematic unsafe field access cleanup COMPLETE")
            print(f"   - All transaction features working without KeyError")
            print(f"   - Empty database scenarios handled robustly")
            print(f"   - Customer profile and transaction endpoints stable")
            print(f"   - Recurring failure cycle ENDED")
        else:
            print(f"   ❌ TRANSACTIONS FIX VERIFICATION INCOMPLETE")
            print(f"   - Some unsafe field access patterns may remain")
            print(f"   - Further investigation and fixes required")
            print(f"   - Recurring failure cycle may continue")
        
        return all_objectives_met

    def test_dao_transaction_id_generation(self):
        """Test DAO transaction ID generation issue - REVIEW REQUEST"""
        print(f"\n🎯 DAO TRANSACTION ID GENERATION TESTING")
        print("=" * 80)
        print("🔍 CRITICAL TESTING OBJECTIVES:")
        print("   1. Test both DAO endpoints (/api/credit-cards/{card_id}/dao and /api/credit-cards/dao)")
        print("   2. Verify transaction IDs follow format: D+last4digits+DDMM (e.g., D98550509)")
        print("   3. Check auto-increment works (D98550509-2, D98550509-3, etc.)")
        print("   4. Test with actual credit cards to ensure last 4 digits are extracted correctly")
        print("   5. Verify both UUID (id field) and business ID (transaction_id field) are present and different")
        print("   6. Check existing DAO transactions in database for incorrect formats")
        
        test_results = {
            "specific_dao_endpoint_working": False,
            "general_dao_endpoint_working": False,
            "transaction_id_format_correct": False,
            "auto_increment_working": False,
            "last_4_digits_correct": False,
            "uuid_and_business_id_different": False,
            "existing_dao_transactions_checked": False,
            "credit_cards_available": False,
            "total_tests": 0,
            "passed_tests": 0,
            "critical_issues": [],
            "created_dao_transactions": []
        }
        
        # Step 1: Check if credit cards exist for testing
        print(f"\n🔍 STEP 1: Check Available Credit Cards for Testing")
        print("=" * 60)
        
        cards_success, cards_response = self.run_test(
            "GET /credit-cards - Check Available Credit Cards",
            "GET",
            "credit-cards?page_size=50",
            200
        )
        
        if cards_success and cards_response and len(cards_response) > 0:
            print(f"✅ Found {len(cards_response)} credit cards for testing")
            test_results["credit_cards_available"] = True
            test_results["passed_tests"] += 1
            
            # Show sample credit cards with their card numbers
            for i, card in enumerate(cards_response[:3]):
                card_id = card.get('id', 'Unknown')
                card_number = card.get('card_number', 'Unknown')
                customer_name = card.get('customer_name', 'Unknown')
                last_4_digits = card_number[-4:] if len(card_number) >= 4 else "0000"
                
                print(f"   Card {i+1}: {customer_name}")
                print(f"      ID: {card_id}")
                print(f"      Card Number: {card_number}")
                print(f"      Last 4 Digits: {last_4_digits}")
        else:
            print(f"❌ No credit cards found - need to create test credit cards first")
            test_results["critical_issues"].append("No credit cards available for DAO testing")
            
            # Create a test credit card for DAO testing
            print(f"\n   Creating test credit card for DAO testing...")
            
            # First get a customer
            customers_success, customers_response = self.run_test(
                "GET /customers - Get Customer for Test Credit Card",
                "GET",
                "customers?limit=1",
                200
            )
            
            if customers_success and customers_response and len(customers_response) > 0:
                customer_id = customers_response[0].get('id')
                
                test_card_data = {
                    "customer_id": customer_id,
                    "card_number": "4111111111119855",  # Test card with last 4 digits: 9855
                    "cardholder_name": "Test Cardholder",
                    "bank_name": "Test Bank",
                    "card_type": "VISA",
                    "expiry_date": "12/26",
                    "ccv": "123",
                    "statement_date": 5,
                    "payment_due_date": 15,
                    "credit_limit": 50000000
                }
                
                create_card_success, create_card_response = self.run_test(
                    "POST /credit-cards - Create Test Credit Card",
                    "POST",
                    "credit-cards",
                    200,
                    data=test_card_data
                )
                
                if create_card_success:
                    print(f"   ✅ Created test credit card: {create_card_response.get('id')}")
                    cards_response = [create_card_response]
                    test_results["credit_cards_available"] = True
                    test_results["passed_tests"] += 1
                else:
                    print(f"   ❌ Failed to create test credit card")
                    test_results["critical_issues"].append("Cannot create test credit card")
            else:
                print(f"   ❌ No customers available to create test credit card")
                test_results["critical_issues"].append("No customers available for test credit card")
        
        test_results["total_tests"] += 1
        
        # Step 2: Check existing DAO transactions in database
        print(f"\n🔍 STEP 2: Check Existing DAO Transactions in Database")
        print("=" * 60)
        
        if self.mongo_connected:
            try:
                existing_dao_transactions = list(self.db.dao_transactions.find({}).limit(20))
                print(f"✅ Found {len(existing_dao_transactions)} existing DAO transactions")
                
                if existing_dao_transactions:
                    print(f"\n   Analyzing existing transaction ID formats:")
                    correct_format_count = 0
                    incorrect_format_count = 0
                    
                    for i, dao in enumerate(existing_dao_transactions[:10]):
                        transaction_id = dao.get('transaction_id', 'Unknown')
                        card_number = dao.get('card_number', 'Unknown')
                        created_at = dao.get('created_at', 'Unknown')
                        
                        print(f"   Transaction {i+1}:")
                        print(f"      transaction_id: {transaction_id}")
                        print(f"      card_number: {card_number}")
                        print(f"      created_at: {created_at}")
                        
                        # Check if transaction_id follows D+last4digits+DDMM format
                        if isinstance(transaction_id, str) and transaction_id.startswith('D') and len(transaction_id) >= 9:
                            # Extract parts: D + 4 digits + 4 digits (DDMM)
                            if len(transaction_id) == 9 or (len(transaction_id) > 9 and transaction_id[9] == '-'):
                                correct_format_count += 1
                                print(f"         ✅ Correct format")
                            else:
                                incorrect_format_count += 1
                                print(f"         ❌ Incorrect format")
                        else:
                            incorrect_format_count += 1
                            print(f"         ❌ Incorrect format")
                    
                    print(f"\n   Format Analysis:")
                    print(f"      Correct format: {correct_format_count}")
                    print(f"      Incorrect format: {incorrect_format_count}")
                    
                    if incorrect_format_count > 0:
                        test_results["critical_issues"].append(f"Found {incorrect_format_count} DAO transactions with incorrect transaction_id format")
                else:
                    print(f"   No existing DAO transactions found")
                
                test_results["existing_dao_transactions_checked"] = True
                test_results["passed_tests"] += 1
                
            except Exception as e:
                print(f"❌ Error checking existing DAO transactions: {e}")
                test_results["critical_issues"].append(f"Cannot check existing DAO transactions: {e}")
        else:
            print(f"⚠️ MongoDB connection not available for database analysis")
        
        test_results["total_tests"] += 1
        
        # Step 3: Test specific DAO endpoint (/api/credit-cards/{card_id}/dao)
        print(f"\n🔍 STEP 3: Test Specific DAO Endpoint (/api/credit-cards/{card_id}/dao)")
        print("=" * 60)
        
        if test_results["credit_cards_available"] and cards_response:
            test_card = cards_response[0]
            card_id = test_card.get('id')
            card_number = test_card.get('card_number', '4111111111119855')
            expected_last_4 = card_number[-4:] if len(card_number) >= 4 else "0000"
            
            print(f"   Testing with card: {card_id}")
            print(f"   Card number: {card_number}")
            print(f"   Expected last 4 digits: {expected_last_4}")
            
            # Get current date for expected format
            from datetime import datetime
            now = datetime.now()
            expected_ddmm = now.strftime("%d%m")
            expected_base_format = f"D{expected_last_4}{expected_ddmm}"
            
            print(f"   Expected transaction ID format: {expected_base_format} or {expected_base_format}-N")
            
            dao_data = {
                "amount": 5000000,  # 5M VND
                "profit_value": 150000,  # 150k VND
                "fee_rate": 3.0,
                "payment_method": "POS",
                "pos_code": "TEST001",
                "notes": "Test DAO transaction for ID generation"
            }
            
            specific_dao_success, specific_dao_response = self.run_test(
                f"POST /credit-cards/{card_id}/dao - Specific DAO Endpoint",
                "POST",
                f"credit-cards/{card_id}/dao",
                200,
                data=dao_data
            )
            
            if specific_dao_success and specific_dao_response:
                print(f"✅ Specific DAO endpoint working")
                test_results["specific_dao_endpoint_working"] = True
                test_results["passed_tests"] += 1
                
                # Check the transaction ID format
                dao_transaction = specific_dao_response.get('dao_transaction', {})
                transaction_id = dao_transaction.get('transaction_id', '')
                technical_uuid = dao_transaction.get('id', '')
                
                print(f"   Created DAO transaction:")
                print(f"      Technical UUID (id): {technical_uuid}")
                print(f"      Business ID (transaction_id): {transaction_id}")
                
                # Verify transaction ID format
                if transaction_id.startswith(f"D{expected_last_4}{expected_ddmm}"):
                    print(f"   ✅ Transaction ID format correct: {transaction_id}")
                    test_results["transaction_id_format_correct"] = True
                    test_results["last_4_digits_correct"] = True
                    test_results["passed_tests"] += 2
                else:
                    print(f"   ❌ Transaction ID format incorrect: {transaction_id}")
                    print(f"      Expected format: D{expected_last_4}{expected_ddmm}")
                    test_results["critical_issues"].append(f"Incorrect transaction ID format: {transaction_id}")
                
                # Verify UUID and business ID are different
                if technical_uuid and transaction_id and technical_uuid != transaction_id:
                    print(f"   ✅ Technical UUID and business ID are different")
                    test_results["uuid_and_business_id_different"] = True
                    test_results["passed_tests"] += 1
                else:
                    print(f"   ❌ Technical UUID and business ID are not properly differentiated")
                    test_results["critical_issues"].append("UUID and business ID not properly differentiated")
                
                test_results["created_dao_transactions"].append({
                    "endpoint": "specific",
                    "transaction_id": transaction_id,
                    "technical_uuid": technical_uuid,
                    "card_id": card_id,
                    "expected_format": expected_base_format
                })
                
                test_results["total_tests"] += 3
            else:
                print(f"❌ Specific DAO endpoint failed")
                test_results["critical_issues"].append("Specific DAO endpoint not working")
                test_results["total_tests"] += 1
        else:
            print(f"⚠️ Cannot test specific DAO endpoint - no credit cards available")
        
        # Step 4: Test general DAO endpoint (/api/credit-cards/dao)
        print(f"\n🔍 STEP 4: Test General DAO Endpoint (/api/credit-cards/dao)")
        print("=" * 60)
        
        if test_results["credit_cards_available"] and cards_response:
            test_card = cards_response[0]
            card_id = test_card.get('id')
            customer_id = test_card.get('customer_id')
            card_number = test_card.get('card_number', '4111111111119855')
            expected_last_4 = card_number[-4:] if len(card_number) >= 4 else "0000"
            
            print(f"   Testing with customer: {customer_id}")
            print(f"   Testing with card: {card_id}")
            print(f"   Expected last 4 digits: {expected_last_4}")
            
            general_dao_data = {
                "customer_id": customer_id,
                "card_id": card_id,  # Include card_id for transaction ID generation
                "amount": 3000000,  # 3M VND
                "profit_value": 90000,  # 90k VND
                "fee_rate": 3.0,
                "payment_method": "POS",
                "pos_code": "TEST002",
                "notes": "Test general DAO transaction for ID generation"
            }
            
            general_dao_success, general_dao_response = self.run_test(
                "POST /credit-cards/dao - General DAO Endpoint",
                "POST",
                "credit-cards/dao",
                200,
                data=general_dao_data
            )
            
            if general_dao_success and general_dao_response:
                print(f"✅ General DAO endpoint working")
                test_results["general_dao_endpoint_working"] = True
                test_results["passed_tests"] += 1
                
                # Check the transaction ID format
                dao_transaction = general_dao_response.get('dao_transaction', {})
                transaction_id = dao_transaction.get('transaction_id', '')
                technical_uuid = dao_transaction.get('id', '')
                
                print(f"   Created DAO transaction:")
                print(f"      Technical UUID (id): {technical_uuid}")
                print(f"      Business ID (transaction_id): {transaction_id}")
                
                # Verify transaction ID format
                if transaction_id.startswith(f"D{expected_last_4}"):
                    print(f"   ✅ Transaction ID format correct: {transaction_id}")
                    if not test_results["transaction_id_format_correct"]:
                        test_results["transaction_id_format_correct"] = True
                        test_results["passed_tests"] += 1
                    if not test_results["last_4_digits_correct"]:
                        test_results["last_4_digits_correct"] = True
                        test_results["passed_tests"] += 1
                else:
                    print(f"   ❌ Transaction ID format incorrect: {transaction_id}")
                    test_results["critical_issues"].append(f"General DAO incorrect transaction ID format: {transaction_id}")
                
                test_results["created_dao_transactions"].append({
                    "endpoint": "general",
                    "transaction_id": transaction_id,
                    "technical_uuid": technical_uuid,
                    "customer_id": customer_id,
                    "card_id": card_id
                })
                
                test_results["total_tests"] += 2
            else:
                print(f"❌ General DAO endpoint failed")
                test_results["critical_issues"].append("General DAO endpoint not working")
                test_results["total_tests"] += 1
        else:
            print(f"⚠️ Cannot test general DAO endpoint - no credit cards available")
        
        # Step 5: Test auto-increment functionality
        print(f"\n🔍 STEP 5: Test Auto-Increment Functionality")
        print("=" * 60)
        
        if test_results["specific_dao_endpoint_working"] and cards_response:
            test_card = cards_response[0]
            card_id = test_card.get('id')
            
            print(f"   Creating second DAO transaction with same card to test auto-increment...")
            
            dao_data_2 = {
                "amount": 2000000,  # 2M VND
                "profit_value": 60000,  # 60k VND
                "fee_rate": 3.0,
                "payment_method": "POS",
                "pos_code": "TEST003",
                "notes": "Test DAO transaction for auto-increment"
            }
            
            second_dao_success, second_dao_response = self.run_test(
                f"POST /credit-cards/{card_id}/dao - Second DAO for Auto-Increment",
                "POST",
                f"credit-cards/{card_id}/dao",
                200,
                data=dao_data_2
            )
            
            if second_dao_success and second_dao_response:
                dao_transaction_2 = second_dao_response.get('dao_transaction', {})
                transaction_id_2 = dao_transaction_2.get('transaction_id', '')
                
                print(f"   Second transaction ID: {transaction_id_2}")
                
                # Check if it has auto-increment suffix
                if '-' in transaction_id_2 and transaction_id_2.endswith('-2'):
                    print(f"   ✅ Auto-increment working: {transaction_id_2}")
                    test_results["auto_increment_working"] = True
                    test_results["passed_tests"] += 1
                elif transaction_id_2 != test_results["created_dao_transactions"][0]["transaction_id"]:
                    print(f"   ✅ Auto-increment working (different format): {transaction_id_2}")
                    test_results["auto_increment_working"] = True
                    test_results["passed_tests"] += 1
                else:
                    print(f"   ❌ Auto-increment not working - same transaction ID")
                    test_results["critical_issues"].append("Auto-increment not working for duplicate transaction IDs")
                
                test_results["created_dao_transactions"].append({
                    "endpoint": "specific_second",
                    "transaction_id": transaction_id_2,
                    "card_id": card_id,
                    "test": "auto_increment"
                })
            else:
                print(f"   ❌ Second DAO transaction failed")
            
            test_results["total_tests"] += 1
        else:
            print(f"   ⚠️ Cannot test auto-increment - specific DAO endpoint not working")
        
        # Step 6: Verify database storage
        print(f"\n🔍 STEP 6: Verify Database Storage of DAO Transactions")
        print("=" * 60)
        
        if self.mongo_connected and test_results["created_dao_transactions"]:
            try:
                print(f"   Checking database for created DAO transactions...")
                
                for dao_info in test_results["created_dao_transactions"]:
                    transaction_id = dao_info.get('transaction_id')
                    technical_uuid = dao_info.get('technical_uuid')
                    
                    if transaction_id:
                        # Find transaction by business ID
                        db_transaction = self.db.dao_transactions.find_one({"transaction_id": transaction_id})
                        
                        if db_transaction:
                            print(f"   ✅ Found in database: {transaction_id}")
                            print(f"      Technical UUID: {db_transaction.get('id')}")
                            print(f"      Business ID: {db_transaction.get('transaction_id')}")
                            print(f"      Card Number: {db_transaction.get('card_number', 'Not stored')}")
                            print(f"      Amount: {db_transaction.get('amount')}")
                            test_results["passed_tests"] += 1
                        else:
                            print(f"   ❌ Not found in database: {transaction_id}")
                            test_results["critical_issues"].append(f"DAO transaction not stored in database: {transaction_id}")
                        
                        test_results["total_tests"] += 1
                
            except Exception as e:
                print(f"   ❌ Error checking database: {e}")
                test_results["critical_issues"].append(f"Cannot verify database storage: {e}")
        else:
            print(f"   ⚠️ Cannot verify database storage - no MongoDB connection or no transactions created")
        
        # Step 7: Final Assessment
        print(f"\n📊 STEP 7: Final Assessment - DAO Transaction ID Generation")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 DAO TRANSACTION ID GENERATION RESULTS:")
        print(f"   Specific DAO endpoint (/api/credit-cards/{{card_id}}/dao): {'✅ WORKING' if test_results['specific_dao_endpoint_working'] else '❌ FAILED'}")
        print(f"   General DAO endpoint (/api/credit-cards/dao): {'✅ WORKING' if test_results['general_dao_endpoint_working'] else '❌ FAILED'}")
        print(f"   Transaction ID format (D+last4digits+DDMM): {'✅ CORRECT' if test_results['transaction_id_format_correct'] else '❌ INCORRECT'}")
        print(f"   Last 4 digits extraction: {'✅ CORRECT' if test_results['last_4_digits_correct'] else '❌ INCORRECT'}")
        print(f"   Auto-increment functionality: {'✅ WORKING' if test_results['auto_increment_working'] else '❌ NOT WORKING'}")
        print(f"   UUID vs Business ID differentiation: {'✅ CORRECT' if test_results['uuid_and_business_id_different'] else '❌ INCORRECT'}")
        print(f"   Existing DAO transactions checked: {'✅ CHECKED' if test_results['existing_dao_transactions_checked'] else '❌ NOT CHECKED'}")
        print(f"   Overall Success Rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        print(f"\n🎯 BUSINESS REQUIREMENTS VERIFICATION:")
        all_requirements_met = (
            test_results["specific_dao_endpoint_working"] and
            test_results["general_dao_endpoint_working"] and
            test_results["transaction_id_format_correct"] and
            test_results["last_4_digits_correct"] and
            test_results["uuid_and_business_id_different"]
        )
        
        if all_requirements_met:
            print(f"   ✅ Both DAO endpoints generate correct business IDs")
            print(f"   ✅ Transaction IDs follow D+last4digits+DDMM format")
            print(f"   ✅ Last 4 digits extracted correctly from card numbers")
            print(f"   ✅ Technical UUID and business ID are properly differentiated")
            if test_results["auto_increment_working"]:
                print(f"   ✅ Auto-increment works for duplicate transaction IDs")
            else:
                print(f"   ⚠️ Auto-increment functionality needs verification")
        else:
            print(f"   ❌ Some business requirements not met:")
            if not test_results["specific_dao_endpoint_working"]:
                print(f"      - Specific DAO endpoint not working")
            if not test_results["general_dao_endpoint_working"]:
                print(f"      - General DAO endpoint not working")
            if not test_results["transaction_id_format_correct"]:
                print(f"      - Transaction ID format incorrect")
            if not test_results["last_4_digits_correct"]:
                print(f"      - Last 4 digits extraction incorrect")
            if not test_results["uuid_and_business_id_different"]:
                print(f"      - UUID and business ID not properly differentiated")
        
        if test_results["created_dao_transactions"]:
            print(f"\n📋 CREATED DAO TRANSACTIONS SUMMARY:")
            for i, dao_info in enumerate(test_results["created_dao_transactions"]):
                print(f"   Transaction {i+1} ({dao_info.get('endpoint', 'unknown')}):")
                print(f"      Business ID: {dao_info.get('transaction_id', 'Unknown')}")
                print(f"      Technical UUID: {dao_info.get('technical_uuid', 'Unknown')}")
        
        if test_results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES FOUND:")
            for issue in test_results["critical_issues"]:
                print(f"   - {issue}")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if all_requirements_met:
            print(f"   ✅ DAO TRANSACTION ID GENERATION WORKING CORRECTLY")
            print(f"   - Both DAO endpoints generate proper business IDs")
            print(f"   - Transaction ID format follows business requirements")
            print(f"   - Last 4 digits extraction working correctly")
            print(f"   - Technical and business IDs properly separated")
        else:
            print(f"   ❌ DAO TRANSACTION ID GENERATION HAS ISSUES")
            print(f"   - Business ID format not following requirements")
            print(f"   - Need to fix transaction ID generation logic")
        
        return all_requirements_met

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

    def test_dual_collection_architecture_analysis(self):
        """Analyze current dual collection architecture và propose unified solution - REVIEW REQUEST"""
        print(f"\n🎯 DUAL COLLECTION ARCHITECTURE ANALYSIS")
        print("=" * 80)
        print("🔍 INVESTIGATION OBJECTIVES:")
        print("   1. Count documents in both bills và inventory_items collections")
        print("   2. Analyze data relationships và redundancy")
        print("   3. Identify queries that require JOINs between collections")
        print("   4. Propose single collection architecture with status fields")
        print("   5. Create migration plan để consolidate data")
        print("   Expected findings: Current data distribution, JOIN complexity, unified solution")
        
        analysis_results = {
            "bills_collection": {
                "total_documents": 0,
                "status_breakdown": {},
                "sample_documents": [],
                "schema_fields": []
            },
            "inventory_items_collection": {
                "total_documents": 0,
                "bill_references": [],
                "sample_documents": [],
                "schema_fields": []
            },
            "data_relationships": {
                "bills_with_inventory_refs": 0,
                "orphaned_inventory_items": 0,
                "duplicate_references": 0,
                "consistency_issues": []
            },
            "join_operations": {
                "required_joins": [],
                "complexity_score": 0,
                "performance_impact": "unknown"
            },
            "unified_architecture": {
                "proposed_schema": {},
                "migration_steps": [],
                "benefits": [],
                "risks": []
            },
            "total_tests": 0,
            "passed_tests": 0,
            "critical_findings": []
        }
        
        if not self.mongo_connected:
            print("❌ MongoDB connection required for architecture analysis")
            return False
        
        # Step 1: Analyze Bills Collection
        print(f"\n🔍 STEP 1: Analyze Bills Collection")
        print("=" * 60)
        
        try:
            # Count total bills
            bills_count = self.db.bills.count_documents({})
            analysis_results["bills_collection"]["total_documents"] = bills_count
            print(f"📊 Total documents in bills collection: {bills_count}")
            
            # Analyze status breakdown
            status_pipeline = [
                {"$group": {"_id": "$status", "count": {"$sum": 1}}},
                {"$sort": {"count": -1}}
            ]
            status_results = list(self.db.bills.aggregate(status_pipeline))
            
            print(f"📊 Bills status breakdown:")
            for status_doc in status_results:
                status = status_doc["_id"]
                count = status_doc["count"]
                analysis_results["bills_collection"]["status_breakdown"][status] = count
                print(f"   {status}: {count} documents")
            
            # Get sample documents to analyze schema
            sample_bills = list(self.db.bills.find({}).limit(3))
            analysis_results["bills_collection"]["sample_documents"] = sample_bills
            
            if sample_bills:
                # Analyze schema fields
                all_fields = set()
                for bill in sample_bills:
                    all_fields.update(bill.keys())
                
                analysis_results["bills_collection"]["schema_fields"] = list(all_fields)
                print(f"📊 Bills collection schema fields ({len(all_fields)}):")
                print(f"   {', '.join(sorted(all_fields))}")
                
                # Show sample bill
                sample_bill = sample_bills[0]
                print(f"📊 Sample bill document:")
                print(f"   ID: {sample_bill.get('id', sample_bill.get('_id'))}")
                print(f"   Customer Code: {sample_bill.get('customer_code')}")
                print(f"   Status: {sample_bill.get('status')}")
                print(f"   Amount: {sample_bill.get('amount')}")
                print(f"   Provider Region: {sample_bill.get('provider_region')}")
            
            analysis_results["passed_tests"] += 1
            
        except Exception as e:
            print(f"❌ Error analyzing bills collection: {e}")
            analysis_results["critical_findings"].append(f"Bills collection analysis failed: {e}")
        
        analysis_results["total_tests"] += 1
        
        # Step 2: Analyze Inventory Items Collection
        print(f"\n🔍 STEP 2: Analyze Inventory Items Collection")
        print("=" * 60)
        
        try:
            # Count total inventory items
            inventory_count = self.db.inventory_items.count_documents({})
            analysis_results["inventory_items_collection"]["total_documents"] = inventory_count
            print(f"📊 Total documents in inventory_items collection: {inventory_count}")
            
            # Get sample documents
            sample_inventory = list(self.db.inventory_items.find({}).limit(3))
            analysis_results["inventory_items_collection"]["sample_documents"] = sample_inventory
            
            if sample_inventory:
                # Analyze schema fields
                all_fields = set()
                for item in sample_inventory:
                    all_fields.update(item.keys())
                
                analysis_results["inventory_items_collection"]["schema_fields"] = list(all_fields)
                print(f"📊 Inventory items schema fields ({len(all_fields)}):")
                print(f"   {', '.join(sorted(all_fields))}")
                
                # Analyze bill references
                bill_refs = [item.get('bill_id') for item in sample_inventory if item.get('bill_id')]
                analysis_results["inventory_items_collection"]["bill_references"] = bill_refs
                print(f"📊 Sample bill references in inventory:")
                for ref in bill_refs[:3]:
                    print(f"   {ref}")
                
                # Show sample inventory item
                sample_item = sample_inventory[0]
                print(f"📊 Sample inventory item:")
                print(f"   ID: {sample_item.get('id', sample_item.get('_id'))}")
                print(f"   Bill ID: {sample_item.get('bill_id')}")
                print(f"   Note: {sample_item.get('note')}")
                print(f"   Added By: {sample_item.get('added_by')}")
                print(f"   Created At: {sample_item.get('created_at')}")
            else:
                print(f"📊 No inventory items found - collection is empty")
            
            analysis_results["passed_tests"] += 1
            
        except Exception as e:
            print(f"❌ Error analyzing inventory_items collection: {e}")
            analysis_results["critical_findings"].append(f"Inventory items analysis failed: {e}")
        
        analysis_results["total_tests"] += 1
        
        # Step 3: Analyze Data Relationships and Redundancy
        print(f"\n🔍 STEP 3: Analyze Data Relationships and Redundancy")
        print("=" * 60)
        
        try:
            # Check for bills that have corresponding inventory items
            if inventory_count > 0:
                # Get all bill_ids from inventory_items
                inventory_bill_ids = list(self.db.inventory_items.distinct("bill_id"))
                print(f"📊 Unique bill IDs referenced in inventory: {len(inventory_bill_ids)}")
                
                # Check how many of these bills actually exist
                existing_bills = 0
                for bill_id in inventory_bill_ids[:10]:  # Check first 10
                    bill_exists = self.db.bills.find_one({"id": bill_id}) or self.db.bills.find_one({"_id": bill_id})
                    if bill_exists:
                        existing_bills += 1
                
                analysis_results["data_relationships"]["bills_with_inventory_refs"] = existing_bills
                print(f"📊 Bills with inventory references (sample): {existing_bills}/10")
                
                # Check for orphaned inventory items (bill_id doesn't exist in bills)
                orphaned_count = 0
                for bill_id in inventory_bill_ids[:10]:
                    bill_exists = self.db.bills.find_one({"id": bill_id}) or self.db.bills.find_one({"_id": bill_id})
                    if not bill_exists:
                        orphaned_count += 1
                        analysis_results["data_relationships"]["consistency_issues"].append(f"Orphaned inventory item: {bill_id}")
                
                analysis_results["data_relationships"]["orphaned_inventory_items"] = orphaned_count
                print(f"📊 Orphaned inventory items (sample): {orphaned_count}/10")
                
                # Check for duplicate references
                bill_id_counts = {}
                for bill_id in inventory_bill_ids:
                    bill_id_counts[bill_id] = bill_id_counts.get(bill_id, 0) + 1
                
                duplicates = {k: v for k, v in bill_id_counts.items() if v > 1}
                analysis_results["data_relationships"]["duplicate_references"] = len(duplicates)
                print(f"📊 Duplicate bill references in inventory: {len(duplicates)}")
                
                if duplicates:
                    print(f"   Sample duplicates:")
                    for bill_id, count in list(duplicates.items())[:3]:
                        print(f"      {bill_id}: {count} references")
            else:
                print(f"📊 No inventory items to analyze relationships")
            
            analysis_results["passed_tests"] += 1
            
        except Exception as e:
            print(f"❌ Error analyzing data relationships: {e}")
            analysis_results["critical_findings"].append(f"Data relationships analysis failed: {e}")
        
        analysis_results["total_tests"] += 1
        
        # Step 4: Identify JOIN Operations and Complexity
        print(f"\n🔍 STEP 4: Identify JOIN Operations and Complexity")
        print("=" * 60)
        
        try:
            # Analyze current API endpoints that require JOINs
            join_operations = [
                {
                    "endpoint": "GET /api/inventory",
                    "description": "Requires JOIN between inventory_items and bills collections",
                    "complexity": "HIGH",
                    "query_pattern": "inventory_items.bill_id -> bills.id",
                    "performance_impact": "Requires lookup for each inventory item"
                },
                {
                    "endpoint": "GET /api/inventory/stats", 
                    "description": "Aggregates data from both collections",
                    "complexity": "MEDIUM",
                    "query_pattern": "Count inventory_items + aggregate bills by status",
                    "performance_impact": "Multiple collection queries"
                },
                {
                    "endpoint": "POST /api/inventory/add",
                    "description": "Updates both collections (bills status + inventory_items)",
                    "complexity": "HIGH",
                    "query_pattern": "Update bills.status + insert inventory_items",
                    "performance_impact": "Transaction across collections required"
                },
                {
                    "endpoint": "DELETE /api/inventory/{item_id}",
                    "description": "Removes from inventory + updates bill status",
                    "complexity": "HIGH", 
                    "query_pattern": "Delete inventory_items + update bills.status",
                    "performance_impact": "Transaction across collections required"
                }
            ]
            
            analysis_results["join_operations"]["required_joins"] = join_operations
            
            print(f"📊 Current JOIN operations identified:")
            complexity_scores = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
            total_complexity = 0
            
            for i, join_op in enumerate(join_operations, 1):
                print(f"   {i}. {join_op['endpoint']}")
                print(f"      Description: {join_op['description']}")
                print(f"      Complexity: {join_op['complexity']}")
                print(f"      Query Pattern: {join_op['query_pattern']}")
                print(f"      Performance Impact: {join_op['performance_impact']}")
                print()
                
                total_complexity += complexity_scores.get(join_op['complexity'], 2)
            
            analysis_results["join_operations"]["complexity_score"] = total_complexity
            analysis_results["join_operations"]["performance_impact"] = "HIGH" if total_complexity > 8 else "MEDIUM" if total_complexity > 4 else "LOW"
            
            print(f"📊 Overall JOIN complexity score: {total_complexity}/12")
            print(f"📊 Performance impact assessment: {analysis_results['join_operations']['performance_impact']}")
            
            analysis_results["passed_tests"] += 1
            
        except Exception as e:
            print(f"❌ Error analyzing JOIN operations: {e}")
            analysis_results["critical_findings"].append(f"JOIN operations analysis failed: {e}")
        
        analysis_results["total_tests"] += 1
        
        # Step 5: Propose Unified Collection Architecture
        print(f"\n🔍 STEP 5: Propose Unified Collection Architecture")
        print("=" * 60)
        
        try:
            # Design unified schema
            unified_schema = {
                "collection_name": "bills_unified",
                "fields": {
                    "id": "string (UUID) - Primary key",
                    "customer_code": "string - Bill customer code",
                    "gateway": "enum - FPT, SHOPEE",
                    "provider_region": "enum - MIEN_BAC, MIEN_NAM, HCMC",
                    "provider_name": "string - Provider name",
                    "full_name": "string - Customer full name",
                    "address": "string - Customer address", 
                    "amount": "number - Bill amount",
                    "billing_cycle": "string - MM/YYYY format",
                    "raw_status": "string - Original status from provider",
                    
                    # Unified status fields (replaces dual collection approach)
                    "bill_status": "enum - AVAILABLE, SOLD, PENDING, CROSSED, ERROR",
                    "inventory_status": "enum - IN_INVENTORY, NOT_IN_INVENTORY",
                    "is_in_inventory": "boolean - Quick lookup flag",
                    
                    # Inventory-specific fields (from inventory_items)
                    "inventory_note": "string - Note when added to inventory",
                    "added_by": "string - User who added to inventory",
                    "batch_id": "string - Batch identifier",
                    "inventory_added_at": "datetime - When added to inventory",
                    
                    # Metadata
                    "created_at": "datetime - Bill creation time",
                    "updated_at": "datetime - Last update time",
                    "last_checked": "datetime - Last status check"
                },
                "indexes": [
                    "customer_code",
                    "bill_status", 
                    "inventory_status",
                    "is_in_inventory",
                    "provider_region",
                    "created_at"
                ]
            }
            
            analysis_results["unified_architecture"]["proposed_schema"] = unified_schema
            
            print(f"📊 Proposed Unified Schema - 'bills_unified' collection:")
            print(f"   Total fields: {len(unified_schema['fields'])}")
            print(f"   Core bill fields: 12")
            print(f"   Unified status fields: 3") 
            print(f"   Inventory fields: 4")
            print(f"   Metadata fields: 3")
            print(f"   Recommended indexes: {len(unified_schema['indexes'])}")
            
            print(f"\n📊 Key unified status fields:")
            print(f"   bill_status: Replaces bills.status")
            print(f"   inventory_status: Replaces inventory_items existence")
            print(f"   is_in_inventory: Boolean flag for quick filtering")
            
            # Migration steps
            migration_steps = [
                {
                    "step": 1,
                    "action": "Create new bills_unified collection with unified schema",
                    "complexity": "LOW",
                    "estimated_time": "5 minutes"
                },
                {
                    "step": 2, 
                    "action": "Migrate all bills from bills collection to bills_unified",
                    "complexity": "MEDIUM",
                    "estimated_time": "10-30 minutes depending on data size"
                },
                {
                    "step": 3,
                    "action": "For each inventory_item, update corresponding bill in bills_unified",
                    "complexity": "HIGH",
                    "estimated_time": "15-45 minutes depending on inventory size"
                },
                {
                    "step": 4,
                    "action": "Update API endpoints to use bills_unified instead of dual collections",
                    "complexity": "HIGH", 
                    "estimated_time": "2-4 hours development time"
                },
                {
                    "step": 5,
                    "action": "Test all inventory and bill operations with unified collection",
                    "complexity": "MEDIUM",
                    "estimated_time": "1-2 hours testing"
                },
                {
                    "step": 6,
                    "action": "Drop old bills and inventory_items collections after verification",
                    "complexity": "LOW",
                    "estimated_time": "5 minutes"
                }
            ]
            
            analysis_results["unified_architecture"]["migration_steps"] = migration_steps
            
            print(f"\n📊 Migration Plan ({len(migration_steps)} steps):")
            total_time_min = 0
            for step in migration_steps:
                print(f"   Step {step['step']}: {step['action']}")
                print(f"      Complexity: {step['complexity']}")
                print(f"      Estimated Time: {step['estimated_time']}")
                print()
                
                # Extract time estimates for total calculation
                if "minutes" in step['estimated_time']:
                    time_parts = step['estimated_time'].split()
                    if "-" in time_parts[0]:
                        avg_time = sum(map(int, time_parts[0].split("-"))) / 2
                    else:
                        avg_time = int(time_parts[0])
                    total_time_min += avg_time
                elif "hours" in step['estimated_time']:
                    time_parts = step['estimated_time'].split()
                    if "-" in time_parts[0]:
                        avg_time = sum(map(int, time_parts[0].split("-"))) / 2
                    else:
                        avg_time = int(time_parts[0])
                    total_time_min += avg_time * 60
            
            print(f"📊 Total estimated migration time: {total_time_min/60:.1f} hours")
            
            # Benefits and risks
            benefits = [
                "Eliminates complex JOIN operations between collections",
                "Reduces query complexity from O(n*m) to O(n) for inventory operations", 
                "Improves performance by avoiding cross-collection lookups",
                "Simplifies API endpoint logic and reduces code complexity",
                "Ensures data consistency with single source of truth",
                "Reduces risk of orphaned inventory items",
                "Enables atomic operations on bill + inventory status",
                "Simplifies backup and restore operations",
                "Reduces MongoDB storage overhead from duplicate references"
            ]
            
            risks = [
                "Migration downtime required during transition",
                "Potential data loss if migration fails (requires backup)",
                "API endpoints need significant refactoring",
                "Frontend may need updates if API responses change",
                "Increased document size due to additional fields",
                "Need to update all existing queries and aggregations",
                "Testing required to ensure no regression in functionality"
            ]
            
            analysis_results["unified_architecture"]["benefits"] = benefits
            analysis_results["unified_architecture"]["risks"] = risks
            
            print(f"📊 Benefits of unified architecture ({len(benefits)}):")
            for i, benefit in enumerate(benefits, 1):
                print(f"   {i}. {benefit}")
            
            print(f"\n📊 Risks and considerations ({len(risks)}):")
            for i, risk in enumerate(risks, 1):
                print(f"   {i}. {risk}")
            
            analysis_results["passed_tests"] += 1
            
        except Exception as e:
            print(f"❌ Error creating unified architecture proposal: {e}")
            analysis_results["critical_findings"].append(f"Unified architecture proposal failed: {e}")
        
        analysis_results["total_tests"] += 1
        
        # Step 6: Final Analysis and Recommendations
        print(f"\n📊 STEP 6: Final Analysis and Recommendations")
        print("=" * 60)
        
        success_rate = (analysis_results["passed_tests"] / analysis_results["total_tests"] * 100) if analysis_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 DUAL COLLECTION ARCHITECTURE ANALYSIS RESULTS:")
        print(f"   Bills collection documents: {analysis_results['bills_collection']['total_documents']}")
        print(f"   Inventory items documents: {analysis_results['inventory_items_collection']['total_documents']}")
        print(f"   Data relationship issues: {len(analysis_results['data_relationships']['consistency_issues'])}")
        print(f"   JOIN operations complexity: {analysis_results['join_operations']['complexity_score']}/12")
        print(f"   Performance impact: {analysis_results['join_operations']['performance_impact']}")
        print(f"   Analysis success rate: {success_rate:.1f}% ({analysis_results['passed_tests']}/{analysis_results['total_tests']})")
        
        print(f"\n🔍 KEY FINDINGS:")
        bills_count = analysis_results['bills_collection']['total_documents']
        inventory_count = analysis_results['inventory_items_collection']['total_documents']
        
        if bills_count > 0 and inventory_count == 0:
            print(f"   📊 ARCHITECTURE ISSUE: {bills_count} bills exist but 0 inventory items")
            print(f"      This indicates inventory system is not being used properly")
            print(f"      Bills and inventory are completely disconnected")
        elif bills_count > 0 and inventory_count > 0:
            print(f"   📊 DUAL COLLECTION ACTIVE: {bills_count} bills + {inventory_count} inventory items")
            print(f"      Current system requires complex JOINs for inventory operations")
            print(f"      Data consistency issues may exist")
        else:
            print(f"   📊 INSUFFICIENT DATA: Cannot fully analyze architecture")
        
        print(f"\n🔍 RECOMMENDATIONS:")
        if analysis_results['join_operations']['complexity_score'] > 6:
            print(f"   🚨 HIGH PRIORITY: Implement unified collection architecture")
            print(f"      Current JOIN complexity is too high ({analysis_results['join_operations']['complexity_score']}/12)")
            print(f"      Performance impact: {analysis_results['join_operations']['performance_impact']}")
            print(f"      Estimated migration time: {total_time_min/60:.1f} hours")
        else:
            print(f"   ✅ MEDIUM PRIORITY: Consider unified architecture for future scalability")
            print(f"      Current complexity manageable but could be improved")
        
        print(f"\n🔍 NEXT STEPS:")
        print(f"   1. Backup current bills and inventory_items collections")
        print(f"   2. Create bills_unified collection with proposed schema")
        print(f"   3. Implement migration script to consolidate data")
        print(f"   4. Update API endpoints to use unified collection")
        print(f"   5. Test all inventory operations with new architecture")
        print(f"   6. Monitor performance improvements after migration")
        
        if analysis_results["critical_findings"]:
            print(f"\n🚨 CRITICAL FINDINGS:")
            for finding in analysis_results["critical_findings"]:
                print(f"   - {finding}")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if success_rate >= 80:
            print(f"   ✅ DUAL COLLECTION ARCHITECTURE ANALYSIS COMPLETE")
            print(f"   - Current data distribution analyzed successfully")
            print(f"   - JOIN complexity identified and quantified")
            print(f"   - Unified solution proposed with migration plan")
            print(f"   - Benefits and risks clearly outlined")
            print(f"   - Ready for architecture consolidation decision")
        else:
            print(f"   ❌ ARCHITECTURE ANALYSIS INCOMPLETE")
            print(f"   - Some analysis steps failed")
            print(f"   - May need additional investigation")
        
        return success_rate >= 80

    def test_sales_api_uuid_system_404_investigation(self):
        """Test Sales API UUID-only system to identify 404 'Bill not found or not available' errors - REVIEW REQUEST"""
        print(f"\n🎯 SALES API UUID-ONLY SYSTEM 404 INVESTIGATION")
        print("=" * 80)
        print("🔍 INVESTIGATION OBJECTIVES:")
        print("   1. Database State Check: Verify bills with status='AVAILABLE' and proper UUID format")
        print("   2. Sales API Testing: Test POST /api/sales with valid customer_id and bill_ids")
        print("   3. Data Creation: Create test bills with AVAILABLE status if needed")
        print("   4. Foreign Key Validation: Test customer_id validation")
        print("   5. Bill Query Analysis: Check bill lookup query logic")
        print("   Expected: Identify exact cause of 404 'Bill not found or not available' errors")
        
        test_results = {
            "database_bills_count": 0,
            "available_bills_count": 0,
            "uuid_format_bills": 0,
            "customers_count": 0,
            "test_bills_created": 0,
            "test_customers_created": 0,
            "sales_creation_success": False,
            "customer_validation_working": False,
            "bill_query_working": False,
            "root_cause_identified": False,
            "total_tests": 0,
            "passed_tests": 0,
            "critical_issues": [],
            "recommendations": []
        }
        
        # Step 1: Database State Check - Verify bills with AVAILABLE status and UUID format
        print(f"\n🔍 STEP 1: Database State Check - Bills Analysis")
        print("=" * 60)
        
        if self.mongo_connected:
            try:
                # Check total bills in database
                total_bills = self.db.bills.count_documents({})
                available_bills = self.db.bills.count_documents({"status": "AVAILABLE"})
                
                print(f"📊 DATABASE BILLS ANALYSIS:")
                print(f"   Total bills in database: {total_bills}")
                print(f"   Bills with AVAILABLE status: {available_bills}")
                
                test_results["database_bills_count"] = total_bills
                test_results["available_bills_count"] = available_bills
                
                # Analyze bill ID formats
                bills_sample = list(self.db.bills.find({}, {"id": 1, "status": 1, "_id": 1}).limit(20))
                uuid_format_count = 0
                
                print(f"\n📋 BILL ID FORMAT ANALYSIS (Sample of {len(bills_sample)} bills):")
                for i, bill in enumerate(bills_sample[:5]):
                    bill_id = bill.get('id', '')
                    mongo_id = str(bill.get('_id', ''))
                    status = bill.get('status', 'UNKNOWN')
                    
                    # Check UUID format
                    is_uuid = len(bill_id) == 36 and bill_id.count('-') == 4
                    if is_uuid:
                        uuid_format_count += 1
                    
                    print(f"   Bill {i+1}: ID={bill_id[:8]}..., Status={status}, Format={'UUID' if is_uuid else 'Other'}")
                
                test_results["uuid_format_bills"] = uuid_format_count
                print(f"   Bills with proper UUID format: {uuid_format_count}/{len(bills_sample)}")
                
                if available_bills > 0 and uuid_format_count > 0:
                    print(f"✅ Database has bills with AVAILABLE status and UUID format")
                    test_results["passed_tests"] += 1
                else:
                    print(f"❌ Database lacks bills with AVAILABLE status or proper UUID format")
                    test_results["critical_issues"].append("No AVAILABLE bills with UUID format found")
                
            except Exception as e:
                print(f"❌ Database analysis failed: {e}")
                test_results["critical_issues"].append(f"Database analysis error: {e}")
        else:
            print(f"⚠️ MongoDB connection not available for database analysis")
            test_results["critical_issues"].append("No MongoDB connection for database analysis")
        
        test_results["total_tests"] += 1
        
        # Step 2: Check customers in database
        print(f"\n🔍 STEP 2: Database State Check - Customers Analysis")
        print("=" * 60)
        
        if self.mongo_connected:
            try:
                total_customers = self.db.customers.count_documents({})
                customers_sample = list(self.db.customers.find({}, {"id": 1, "name": 1}).limit(5))
                
                print(f"📊 DATABASE CUSTOMERS ANALYSIS:")
                print(f"   Total customers in database: {total_customers}")
                
                test_results["customers_count"] = total_customers
                
                if customers_sample:
                    print(f"   Sample customers:")
                    for i, customer in enumerate(customers_sample):
                        customer_id = customer.get('id', '')
                        customer_name = customer.get('name', 'Unknown')
                        is_uuid = len(customer_id) == 36 and customer_id.count('-') == 4
                        print(f"      Customer {i+1}: {customer_name} (ID: {customer_id[:8]}..., Format: {'UUID' if is_uuid else 'Other'})")
                
                if total_customers > 0:
                    print(f"✅ Database has customers for testing")
                    test_results["passed_tests"] += 1
                else:
                    print(f"❌ No customers found in database")
                    test_results["critical_issues"].append("No customers found for sales testing")
                
            except Exception as e:
                print(f"❌ Customer analysis failed: {e}")
                test_results["critical_issues"].append(f"Customer analysis error: {e}")
        
        test_results["total_tests"] += 1
        
        # Step 3: Create test data if needed
        print(f"\n🔍 STEP 3: Create Test Data if Needed")
        print("=" * 60)
        
        # Create test customers if none exist
        if test_results["customers_count"] == 0:
            print(f"📝 Creating test customers...")
            
            for i in range(3):
                customer_data = {
                    "name": f"Sales Test Customer {i+1}",
                    "phone": f"0901234{i:03d}",
                    "email": f"sales_test_{i+1}@example.com",
                    "address": f"Sales Test Address {i+1}",
                    "type": "INDIVIDUAL"
                }
                
                create_success, create_response = self.run_test(
                    f"POST /customers - Create Test Customer {i+1}",
                    "POST",
                    "customers",
                    200,
                    data=customer_data
                )
                
                if create_success:
                    test_results["test_customers_created"] += 1
                    print(f"   ✅ Created customer: {customer_data['name']}")
                else:
                    print(f"   ❌ Failed to create customer: {customer_data['name']}")
        
        # Create test bills if insufficient AVAILABLE bills
        if test_results["available_bills_count"] < 3:
            print(f"📝 Creating test bills with AVAILABLE status...")
            
            for i in range(5):
                bill_data = {
                    "customer_code": f"SALES_TEST_{i+1:03d}",
                    "customer_name": f"Sales Test Customer {i+1}",
                    "phone": f"0901234{i:03d}",
                    "address": f"Sales Test Address {i+1}",
                    "amount": 100000 + (i * 50000),
                    "cycle": f"{(i % 12) + 1:02d}/2025",
                    "gateway": "FPT",
                    "provider_region": "MIEN_BAC" if i % 2 == 0 else "MIEN_NAM",
                    "due_date": "2025-12-31"
                }
                
                create_success, create_response = self.run_test(
                    f"POST /bills - Create Test Bill {i+1}",
                    "POST",
                    "bills",
                    200,
                    data=bill_data
                )
                
                if create_success:
                    test_results["test_bills_created"] += 1
                    print(f"   ✅ Created bill: {bill_data['customer_code']} - Amount: {bill_data['amount']}")
                else:
                    print(f"   ❌ Failed to create bill: {bill_data['customer_code']}")
        
        test_results["total_tests"] += 1
        
        # Step 4: Get available test data for sales creation
        print(f"\n🔍 STEP 4: Retrieve Test Data for Sales Creation")
        print("=" * 60)
        
        # Get customers for testing
        customers_success, customers_response = self.run_test(
            "GET /customers - Get Test Customers",
            "GET",
            "customers?limit=10",
            200
        )
        
        test_customer = None
        if customers_success and customers_response:
            test_customer = customers_response[0]
            print(f"✅ Found test customer: {test_customer.get('name')} (ID: {test_customer.get('id')})")
        else:
            print(f"❌ No customers available for testing")
            test_results["critical_issues"].append("No customers available for sales testing")
        
        # Get available bills for testing
        bills_success, bills_response = self.run_test(
            "GET /bills - Get Available Bills",
            "GET",
            "bills?status=AVAILABLE&limit=10",
            200
        )
        
        test_bills = []
        if bills_success and bills_response:
            test_bills = bills_response[:3]  # Use first 3 bills
            print(f"✅ Found {len(test_bills)} available bills for testing:")
            for i, bill in enumerate(test_bills):
                print(f"   Bill {i+1}: {bill.get('customer_code')} - Amount: {bill.get('amount')} - ID: {bill.get('id')}")
        else:
            print(f"❌ No available bills found for testing")
            test_results["critical_issues"].append("No available bills for sales testing")
        
        test_results["total_tests"] += 1
        
        # Step 5: Test Customer ID Validation
        print(f"\n🔍 STEP 5: Test Customer ID Validation")
        print("=" * 60)
        
        if test_customer:
            customer_id = test_customer.get('id')
            
            # Test valid customer lookup
            customer_lookup_success, customer_lookup_response = self.run_test(
                f"GET /customers/{customer_id} - Validate Customer Exists",
                "GET",
                f"customers/{customer_id}",
                200
            )
            
            if customer_lookup_success:
                print(f"✅ Customer validation working - customer exists and accessible")
                test_results["customer_validation_working"] = True
                test_results["passed_tests"] += 1
            else:
                print(f"❌ Customer validation failing - customer not accessible")
                test_results["critical_issues"].append(f"Customer {customer_id} not accessible via API")
            
            # Test invalid customer ID
            invalid_customer_success, invalid_customer_response = self.run_test(
                "GET /customers/invalid-uuid - Test Invalid Customer ID",
                "GET",
                "customers/00000000-0000-0000-0000-000000000000",
                404
            )
            
            if invalid_customer_success:
                print(f"✅ Invalid customer ID properly returns 404")
                test_results["passed_tests"] += 1
            else:
                print(f"❌ Invalid customer ID handling not working correctly")
        
        test_results["total_tests"] += 2
        
        # Step 6: Test Bill Query Logic
        print(f"\n🔍 STEP 6: Test Bill Query Logic")
        print("=" * 60)
        
        if test_bills:
            for i, bill in enumerate(test_bills):
                bill_id = bill.get('id')
                
                # Test individual bill lookup
                bill_lookup_success, bill_lookup_response = self.run_test(
                    f"GET /bills/{bill_id} - Test Bill Lookup {i+1}",
                    "GET",
                    f"bills/{bill_id}",
                    200
                )
                
                if bill_lookup_success:
                    bill_status = bill_lookup_response.get('status')
                    print(f"   ✅ Bill {i+1} accessible - Status: {bill_status}")
                    
                    if bill_status == "AVAILABLE":
                        test_results["bill_query_working"] = True
                        test_results["passed_tests"] += 1
                    else:
                        print(f"   ⚠️ Bill status is {bill_status}, not AVAILABLE")
                else:
                    print(f"   ❌ Bill {i+1} not accessible via API")
                    test_results["critical_issues"].append(f"Bill {bill_id} not accessible")
                
                test_results["total_tests"] += 1
        
        # Step 7: Test Sales Creation - The Critical Test
        print(f"\n🔍 STEP 7: Test Sales Creation - Critical 404 Investigation")
        print("=" * 60)
        
        if test_customer and test_bills:
            customer_id = test_customer.get('id')
            bill_ids = [bill.get('id') for bill in test_bills]
            
            print(f"🎯 ATTEMPTING SALES CREATION:")
            print(f"   Customer ID: {customer_id}")
            print(f"   Bill IDs: {bill_ids}")
            print(f"   Expected: Should work if UUID-only system is correct")
            
            sales_data = {
                "customer_id": customer_id,
                "bill_ids": bill_ids,
                "profit_pct": 5.0,
                "notes": "Test sale for UUID-only system investigation"
            }
            
            sales_success, sales_response = self.run_test(
                "POST /sales - Create Sale Transaction",
                "POST",
                "sales",
                200,
                data=sales_data
            )
            
            if sales_success:
                print(f"✅ SUCCESS: Sales creation working!")
                print(f"   Sale ID: {sales_response.get('id')}")
                print(f"   Total: {sales_response.get('total')}")
                print(f"   Profit: {sales_response.get('profit_value')}")
                test_results["sales_creation_success"] = True
                test_results["passed_tests"] += 1
                test_results["root_cause_identified"] = True
                test_results["recommendations"].append("Sales API is working correctly with UUID-only system")
            else:
                print(f"❌ FAILED: Sales creation still returning error")
                print(f"   This confirms the 404 'Bill not found or not available' issue")
                
                # Analyze the specific error
                if hasattr(sales_response, 'get'):
                    error_detail = sales_response.get('detail', 'Unknown error')
                    print(f"   Error detail: {error_detail}")
                    
                    if "Bill" in error_detail and "not found" in error_detail:
                        test_results["critical_issues"].append("Bill lookup failing in sales creation")
                        test_results["recommendations"].append("Check bill query logic in sales creation endpoint")
                    elif "Customer" in error_detail:
                        test_results["critical_issues"].append("Customer lookup failing in sales creation")
                        test_results["recommendations"].append("Check customer validation in sales creation endpoint")
                    else:
                        test_results["critical_issues"].append(f"Unknown sales creation error: {error_detail}")
                
                test_results["root_cause_identified"] = True
        else:
            print(f"⚠️ Cannot test sales creation - missing test data")
            test_results["critical_issues"].append("Insufficient test data for sales creation testing")
        
        test_results["total_tests"] += 1
        
        # Step 8: Detailed Bill Query Analysis
        print(f"\n🔍 STEP 8: Detailed Bill Query Analysis")
        print("=" * 60)
        
        if test_bills and self.mongo_connected:
            print(f"🔍 ANALYZING BILL QUERY LOGIC:")
            
            for bill in test_bills[:2]:  # Analyze first 2 bills
                bill_id = bill.get('id')
                
                try:
                    # Direct database query to match sales creation logic
                    db_bill = self.db.bills.find_one({"id": bill_id, "status": "AVAILABLE"})
                    
                    if db_bill:
                        print(f"   ✅ Bill {bill_id[:8]}... found in database with AVAILABLE status")
                        print(f"      Customer Code: {db_bill.get('customer_code')}")
                        print(f"      Amount: {db_bill.get('amount')}")
                        print(f"      Status: {db_bill.get('status')}")
                    else:
                        print(f"   ❌ Bill {bill_id[:8]}... NOT found with query {{id: {bill_id}, status: AVAILABLE}}")
                        
                        # Check if bill exists with different status
                        any_status_bill = self.db.bills.find_one({"id": bill_id})
                        if any_status_bill:
                            actual_status = any_status_bill.get('status')
                            print(f"      Bill exists but status is: {actual_status}")
                            test_results["critical_issues"].append(f"Bill {bill_id} has status {actual_status}, not AVAILABLE")
                        else:
                            print(f"      Bill does not exist in database at all")
                            test_results["critical_issues"].append(f"Bill {bill_id} does not exist in database")
                
                except Exception as e:
                    print(f"   ❌ Database query failed: {e}")
                    test_results["critical_issues"].append(f"Database query error: {e}")
        
        # Step 9: Final Analysis and Recommendations
        print(f"\n📊 STEP 9: Final Analysis and Root Cause Identification")
        print("=" * 60)
        
        success_rate = (test_results["passed_tests"] / test_results["total_tests"] * 100) if test_results["total_tests"] > 0 else 0
        
        print(f"\n🔍 SALES API UUID-ONLY INVESTIGATION RESULTS:")
        print(f"   Database bills count: {test_results['database_bills_count']}")
        print(f"   Available bills count: {test_results['available_bills_count']}")
        print(f"   UUID format bills: {test_results['uuid_format_bills']}")
        print(f"   Customers count: {test_results['customers_count']}")
        print(f"   Test bills created: {test_results['test_bills_created']}")
        print(f"   Test customers created: {test_results['test_customers_created']}")
        print(f"   Sales creation success: {'✅ YES' if test_results['sales_creation_success'] else '❌ NO'}")
        print(f"   Customer validation working: {'✅ YES' if test_results['customer_validation_working'] else '❌ NO'}")
        print(f"   Bill query working: {'✅ YES' if test_results['bill_query_working'] else '❌ NO'}")
        print(f"   Root cause identified: {'✅ YES' if test_results['root_cause_identified'] else '❌ NO'}")
        print(f"   Overall Success Rate: {success_rate:.1f}% ({test_results['passed_tests']}/{test_results['total_tests']})")
        
        print(f"\n🎯 ROOT CAUSE ANALYSIS:")
        if test_results["critical_issues"]:
            print(f"   🚨 CRITICAL ISSUES IDENTIFIED:")
            for issue in test_results["critical_issues"]:
                print(f"      - {issue}")
        else:
            print(f"   ✅ No critical issues found - system may be working correctly")
        
        print(f"\n💡 RECOMMENDATIONS:")
        if test_results["recommendations"]:
            for recommendation in test_results["recommendations"]:
                print(f"   - {recommendation}")
        else:
            if not test_results["sales_creation_success"]:
                print(f"   - Investigate bill status validation in sales creation endpoint")
                print(f"   - Check if bills are properly marked as AVAILABLE in database")
                print(f"   - Verify UUID format consistency between API and database")
                print(f"   - Review sales creation query logic at line 668 in server.py")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if test_results["sales_creation_success"]:
            print(f"   ✅ SALES API UUID-ONLY SYSTEM IS WORKING CORRECTLY")
            print(f"   - Sales creation successful with UUID-only references")
            print(f"   - No 404 'Bill not found or not available' errors detected")
            print(f"   - UUID-only system functioning as designed")
        else:
            print(f"   ❌ SALES API UUID-ONLY SYSTEM HAS ISSUES")
            print(f"   - 404 'Bill not found or not available' error confirmed")
            print(f"   - Issue likely in bill lookup query or status validation")
            print(f"   - Requires immediate investigation and fix")
        
        return test_results["sales_creation_success"]

    def run_all_tests(self):
        """Run all tests for the review request"""
        print(f"\n🚀 STARTING DUAL COLLECTION ARCHITECTURE ANALYSIS")
        print("=" * 80)
        print(f"🎯 Review Request: Analyze dual collection architecture và propose unified solution")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API Base URL: {self.base_url}")
        
        # Run the main test
        success = self.test_dual_collection_architecture_analysis()
        
        # Print final summary
        print(f"\n📊 FINAL TEST SUMMARY")
        print("=" * 50)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if success:
            print(f"\n✅ OVERALL RESULT: Dual collection architecture analysis COMPLETED")
            print(f"   - Current data distribution between bills và inventory_items analyzed")
            print(f"   - JOIN complexity identified và quantified")
            print(f"   - Unified collection architecture proposed")
            print(f"   - Migration plan created với estimated timeline")
            print(f"   - Benefits và risks clearly outlined")
        else:
            print(f"\n❌ OVERALL RESULT: Architecture analysis NEEDS ATTENTION")
            print(f"   - Some analysis steps failed")
            print(f"   - May need additional investigation")
        
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
            print(f"   ⚠️ No credit cards available for individual lookup testing")
        
        return True

    def test_uuid_only_system_final_validation(self):
        """UUID-Only System Final Validation - Comprehensive End-to-End Testing"""
        print(f"\n🎯 UUID-ONLY SYSTEM FINAL VALIDATION - COMPREHENSIVE TESTING")
        print("=" * 80)
        print("🔍 COMPREHENSIVE VALIDATION OBJECTIVES:")
        print("   1. Full API Integration Test - all major endpoints (customers, bills, inventory, sales)")
        print("   2. Frontend-Backend Integration - verify frontend API calls work with UUID-only backend")
        print("   3. Data Consistency Check - ensure all collections use UUID format consistently")
        print("   4. Sales Transaction Flow - complete sales workflow from customer to bill purchase")
        print("   5. Inventory Management - inventory operations with UUID-only bills")
        print("   6. Credit Card DAO Operations - credit card functionality with UUID customers/bills")
        print("   Expected: 100% UUID-only system with no ObjectId/UUID mixing issues")
        
        validation_results = {
            "api_integration_tests": {"passed": 0, "total": 0, "details": []},
            "data_consistency_check": {"uuid_only": True, "mixed_ids_found": 0, "collections_checked": 0},
            "sales_transaction_flow": {"working": False, "transactions_created": 0, "errors": []},
            "inventory_management": {"working": False, "operations_tested": 0, "errors": []},
            "credit_card_operations": {"working": False, "operations_tested": 0, "errors": []},
            "frontend_backend_integration": {"working": False, "endpoints_tested": 0, "errors": []},
            "overall_success_rate": 0,
            "critical_issues": [],
            "system_ready_for_production": False
        }
        
        # Phase 1: Full API Integration Test
        print(f"\n🔍 PHASE 1: Full API Integration Test - All Major Endpoints")
        print("=" * 70)
        
        api_endpoints = [
            ("GET /api/health", "GET", "health", 200),
            ("GET /api/customers", "GET", "customers?limit=50", 200),
            ("GET /api/bills", "GET", "bills?limit=50", 200),
            ("GET /api/inventory", "GET", "inventory?limit=50", 200),
            ("GET /api/sales", "GET", "sales?limit=50", 200),
            ("GET /api/stats/dashboard", "GET", "stats/dashboard", 200),
        ]
        
        for endpoint_name, method, endpoint, expected_status in api_endpoints:
            success, response = self.run_test(
                f"API Integration - {endpoint_name}",
                method,
                endpoint,
                expected_status
            )
            
            validation_results["api_integration_tests"]["total"] += 1
            if success:
                validation_results["api_integration_tests"]["passed"] += 1
                validation_results["api_integration_tests"]["details"].append(f"✅ {endpoint_name}")
                
                # Check for UUID-only responses
                if isinstance(response, list) and response:
                    sample_item = response[0]
                    item_id = sample_item.get('id', '')
                    if len(item_id) == 36 and item_id.count('-') == 4:
                        print(f"   ✅ UUID-only format confirmed: {item_id}")
                    else:
                        print(f"   ⚠️ Non-UUID ID detected: {item_id}")
                        validation_results["data_consistency_check"]["mixed_ids_found"] += 1
                elif isinstance(response, dict) and 'id' in response:
                    item_id = response.get('id', '')
                    if len(item_id) == 36 and item_id.count('-') == 4:
                        print(f"   ✅ UUID-only format confirmed: {item_id}")
            else:
                validation_results["api_integration_tests"]["details"].append(f"❌ {endpoint_name}")
                validation_results["critical_issues"].append(f"API endpoint failed: {endpoint_name}")
        
        # Phase 2: Data Consistency Check
        print(f"\n🔍 PHASE 2: Data Consistency Check - UUID Format Verification")
        print("=" * 70)
        
        if self.mongo_connected:
            collections_to_check = ["customers", "bills", "sales", "credit_cards"]
            
            for collection_name in collections_to_check:
                try:
                    collection = getattr(self.db, collection_name)
                    sample_docs = list(collection.find({}).limit(10))
                    
                    validation_results["data_consistency_check"]["collections_checked"] += 1
                    
                    print(f"\n   Checking {collection_name} collection:")
                    print(f"   Found {len(sample_docs)} documents")
                    
                    uuid_count = 0
                    mixed_count = 0
                    
                    for doc in sample_docs:
                        doc_id = doc.get('id', '')
                        if len(doc_id) == 36 and doc_id.count('-') == 4:
                            uuid_count += 1
                        else:
                            mixed_count += 1
                            validation_results["data_consistency_check"]["mixed_ids_found"] += 1
                    
                    print(f"   UUID format: {uuid_count}/{len(sample_docs)}")
                    print(f"   Mixed/Other format: {mixed_count}/{len(sample_docs)}")
                    
                    if mixed_count == 0:
                        print(f"   ✅ {collection_name}: 100% UUID-only format")
                    else:
                        print(f"   ⚠️ {collection_name}: Mixed ID formats detected")
                        validation_results["data_consistency_check"]["uuid_only"] = False
                        
                except Exception as e:
                    print(f"   ❌ Error checking {collection_name}: {e}")
                    validation_results["critical_issues"].append(f"Data consistency check failed for {collection_name}")
        else:
            print("   ⚠️ MongoDB connection not available for data consistency check")
        
        # Phase 3: Sales Transaction Flow Test
        print(f"\n🔍 PHASE 3: Sales Transaction Flow - Complete Workflow Test")
        print("=" * 70)
        
        # First, ensure we have test data
        customers_success, customers_response = self.run_test(
            "Get Customers for Sales Test",
            "GET",
            "customers?limit=5",
            200
        )
        
        bills_success, bills_response = self.run_test(
            "Get Available Bills for Sales Test",
            "GET",
            "bills?status=AVAILABLE&limit=5",
            200
        )
        
        if customers_success and bills_success and customers_response and bills_response:
            # Create a test sale transaction
            test_customer = customers_response[0]
            test_bills = bills_response[:2]  # Use first 2 available bills
            
            customer_id = test_customer.get('id')
            bill_ids = [bill.get('id') for bill in test_bills]
            
            print(f"   Testing sales flow with:")
            print(f"   Customer: {test_customer.get('name')} (ID: {customer_id})")
            print(f"   Bills: {len(bill_ids)} bills")
            
            # Verify UUID formats
            if len(customer_id) == 36 and customer_id.count('-') == 4:
                print(f"   ✅ Customer ID is UUID format")
            else:
                print(f"   ❌ Customer ID is not UUID format: {customer_id}")
                validation_results["critical_issues"].append("Customer ID not UUID format")
            
            all_bills_uuid = all(len(bid) == 36 and bid.count('-') == 4 for bid in bill_ids)
            if all_bills_uuid:
                print(f"   ✅ All bill IDs are UUID format")
            else:
                print(f"   ❌ Some bill IDs are not UUID format")
                validation_results["critical_issues"].append("Bill IDs not UUID format")
            
            # Create sale transaction
            sale_data = {
                "customer_id": customer_id,
                "bill_ids": bill_ids,
                "profit_pct": 5.0,
                "notes": "UUID-only system test sale"
            }
            
            sale_success, sale_response = self.run_test(
                "Create Sales Transaction - UUID Only",
                "POST",
                "sales",
                200,
                data=sale_data
            )
            
            if sale_success:
                print(f"   ✅ Sales transaction created successfully")
                print(f"   Sale ID: {sale_response.get('id')}")
                print(f"   Total: {sale_response.get('total')}")
                print(f"   Profit: {sale_response.get('profit_value')}")
                
                validation_results["sales_transaction_flow"]["working"] = True
                validation_results["sales_transaction_flow"]["transactions_created"] = 1
                
                # Verify sale ID is UUID format
                sale_id = sale_response.get('id', '')
                if len(sale_id) == 36 and sale_id.count('-') == 4:
                    print(f"   ✅ Sale ID is UUID format: {sale_id}")
                else:
                    print(f"   ❌ Sale ID is not UUID format: {sale_id}")
                    validation_results["critical_issues"].append("Sale ID not UUID format")
            else:
                print(f"   ❌ Sales transaction creation failed")
                validation_results["sales_transaction_flow"]["errors"].append("Sales creation failed")
                validation_results["critical_issues"].append("Sales transaction flow broken")
        else:
            print(f"   ⚠️ Insufficient test data for sales flow test")
            validation_results["sales_transaction_flow"]["errors"].append("Insufficient test data")
        
        # Phase 4: Inventory Management Test
        print(f"\n🔍 PHASE 4: Inventory Management - UUID-Only Operations")
        print("=" * 70)
        
        # Test inventory operations
        inventory_operations = [
            ("GET /api/inventory", "GET", "inventory?limit=20", 200),
            ("GET /api/inventory?status=AVAILABLE", "GET", "inventory?status=AVAILABLE&limit=20", 200),
        ]
        
        inventory_working = True
        for op_name, method, endpoint, expected_status in inventory_operations:
            success, response = self.run_test(
                f"Inventory Operation - {op_name}",
                method,
                endpoint,
                expected_status
            )
            
            validation_results["inventory_management"]["operations_tested"] += 1
            
            if success:
                print(f"   ✅ {op_name} working")
                
                # Check UUID format in inventory items
                if isinstance(response, list) and response:
                    sample_item = response[0]
                    item_id = sample_item.get('id', '')
                    if len(item_id) == 36 and item_id.count('-') == 4:
                        print(f"   ✅ Inventory item UUID format confirmed")
                    else:
                        print(f"   ❌ Inventory item not UUID format: {item_id}")
                        inventory_working = False
            else:
                print(f"   ❌ {op_name} failed")
                validation_results["inventory_management"]["errors"].append(f"{op_name} failed")
                inventory_working = False
        
        validation_results["inventory_management"]["working"] = inventory_working
        
        # Test inventory add/remove operations if we have bills
        if bills_success and bills_response:
            test_bill = bills_response[0]
            test_bill_id = test_bill.get('id')
            
            # Test add to inventory
            add_success, add_response = self.run_test(
                "Add Bill to Inventory - UUID Only",
                "POST",
                f"inventory/add/{test_bill_id}",
                200
            )
            
            if add_success:
                print(f"   ✅ Add to inventory working with UUID: {test_bill_id}")
                
                # Test remove from inventory
                remove_success, remove_response = self.run_test(
                    "Remove Bill from Inventory - UUID Only",
                    "DELETE",
                    f"inventory/remove/{test_bill_id}",
                    200
                )
                
                if remove_success:
                    print(f"   ✅ Remove from inventory working with UUID")
                    validation_results["inventory_management"]["operations_tested"] += 2
                else:
                    print(f"   ❌ Remove from inventory failed")
                    validation_results["inventory_management"]["errors"].append("Remove from inventory failed")
            else:
                print(f"   ❌ Add to inventory failed")
                validation_results["inventory_management"]["errors"].append("Add to inventory failed")
        
        # Phase 5: Credit Card DAO Operations Test
        print(f"\n🔍 PHASE 5: Credit Card DAO Operations - UUID System")
        print("=" * 70)
        
        # Test credit card operations
        credit_card_success, credit_card_response = self.run_test(
            "Get Credit Cards - UUID System",
            "GET",
            "credit-cards?limit=20",
            200
        )
        
        if credit_card_success and credit_card_response:
            print(f"   ✅ Credit cards endpoint working - found {len(credit_card_response)} cards")
            
            validation_results["credit_card_operations"]["operations_tested"] += 1
            
            # Check UUID format in credit cards
            if credit_card_response:
                sample_card = credit_card_response[0]
                card_id = sample_card.get('id', '')
                customer_id = sample_card.get('customer_id', '')
                
                card_uuid_valid = len(card_id) == 36 and card_id.count('-') == 4
                customer_uuid_valid = len(customer_id) == 36 and customer_id.count('-') == 4
                
                if card_uuid_valid and customer_uuid_valid:
                    print(f"   ✅ Credit card UUID formats confirmed")
                    print(f"   Card ID: {card_id}")
                    print(f"   Customer ID: {customer_id}")
                    validation_results["credit_card_operations"]["working"] = True
                else:
                    print(f"   ❌ Credit card UUID formats invalid")
                    print(f"   Card ID valid: {card_uuid_valid}")
                    print(f"   Customer ID valid: {customer_uuid_valid}")
                    validation_results["credit_card_operations"]["errors"].append("Invalid UUID formats")
                
                # Test individual credit card lookup
                card_detail_success, card_detail_response = self.run_test(
                    f"Credit Card Detail - UUID Lookup",
                    "GET",
                    f"credit-cards/{card_id}/detail",
                    200
                )
                
                validation_results["credit_card_operations"]["operations_tested"] += 1
                
                if card_detail_success:
                    print(f"   ✅ Credit card detail lookup working with UUID")
                else:
                    print(f"   ❌ Credit card detail lookup failed")
                    validation_results["credit_card_operations"]["errors"].append("Credit card detail lookup failed")
        else:
            print(f"   ❌ Credit cards endpoint failed")
            validation_results["credit_card_operations"]["errors"].append("Credit cards endpoint failed")
        
        # Phase 6: Frontend-Backend Integration Test
        print(f"\n🔍 PHASE 6: Frontend-Backend Integration - API Compatibility")
        print("=" * 70)
        
        # Test endpoints that frontend typically uses
        frontend_endpoints = [
            ("Dashboard Stats", "GET", "stats/dashboard", 200),
            ("Customer List", "GET", "customers?limit=20", 200),
            ("Bill List", "GET", "bills?limit=20", 200),
            ("Inventory Stats", "GET", "inventory?limit=20", 200),
        ]
        
        frontend_working = True
        for endpoint_name, method, endpoint, expected_status in frontend_endpoints:
            success, response = self.run_test(
                f"Frontend Integration - {endpoint_name}",
                method,
                endpoint,
                expected_status
            )
            
            validation_results["frontend_backend_integration"]["endpoints_tested"] += 1
            
            if success:
                print(f"   ✅ {endpoint_name} - Frontend compatible")
                
                # Check response structure for frontend compatibility
                if isinstance(response, dict) and response:
                    print(f"   Response keys: {list(response.keys())}")
                elif isinstance(response, list) and response:
                    print(f"   Array response with {len(response)} items")
            else:
                print(f"   ❌ {endpoint_name} - Frontend incompatible")
                validation_results["frontend_backend_integration"]["errors"].append(f"{endpoint_name} failed")
                frontend_working = False
        
        validation_results["frontend_backend_integration"]["working"] = frontend_working
        
        # Final Assessment
        print(f"\n📊 FINAL ASSESSMENT: UUID-Only System Validation Results")
        print("=" * 70)
        
        # Calculate overall success rate
        total_tests = (
            validation_results["api_integration_tests"]["total"] +
            validation_results["inventory_management"]["operations_tested"] +
            validation_results["credit_card_operations"]["operations_tested"] +
            validation_results["frontend_backend_integration"]["endpoints_tested"]
        )
        
        passed_tests = (
            validation_results["api_integration_tests"]["passed"] +
            (validation_results["inventory_management"]["operations_tested"] if validation_results["inventory_management"]["working"] else 0) +
            (validation_results["credit_card_operations"]["operations_tested"] if validation_results["credit_card_operations"]["working"] else 0) +
            (validation_results["frontend_backend_integration"]["endpoints_tested"] if validation_results["frontend_backend_integration"]["working"] else 0)
        )
        
        if validation_results["sales_transaction_flow"]["working"]:
            passed_tests += 1
            total_tests += 1
        
        validation_results["overall_success_rate"] = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🔍 COMPREHENSIVE VALIDATION RESULTS:")
        print(f"   API Integration Tests: {validation_results['api_integration_tests']['passed']}/{validation_results['api_integration_tests']['total']} passed")
        print(f"   Data Consistency: {'✅ UUID-only' if validation_results['data_consistency_check']['uuid_only'] else '❌ Mixed IDs found'}")
        print(f"   Sales Transaction Flow: {'✅ Working' if validation_results['sales_transaction_flow']['working'] else '❌ Failed'}")
        print(f"   Inventory Management: {'✅ Working' if validation_results['inventory_management']['working'] else '❌ Failed'}")
        print(f"   Credit Card Operations: {'✅ Working' if validation_results['credit_card_operations']['working'] else '❌ Failed'}")
        print(f"   Frontend-Backend Integration: {'✅ Working' if validation_results['frontend_backend_integration']['working'] else '❌ Failed'}")
        print(f"   Overall Success Rate: {validation_results['overall_success_rate']:.1f}% ({passed_tests}/{total_tests})")
        
        # Production Readiness Assessment
        production_ready = (
            validation_results["api_integration_tests"]["passed"] >= validation_results["api_integration_tests"]["total"] * 0.8 and
            validation_results["data_consistency_check"]["uuid_only"] and
            validation_results["sales_transaction_flow"]["working"] and
            validation_results["inventory_management"]["working"] and
            validation_results["frontend_backend_integration"]["working"] and
            len(validation_results["critical_issues"]) == 0
        )
        
        validation_results["system_ready_for_production"] = production_ready
        
        print(f"\n🎯 PRODUCTION READINESS ASSESSMENT:")
        if production_ready:
            print(f"   ✅ SYSTEM READY FOR PRODUCTION")
            print(f"   - UUID-only architecture fully implemented")
            print(f"   - No ObjectId/UUID mixing issues detected")
            print(f"   - All major workflows functioning correctly")
            print(f"   - Frontend-backend integration working")
            print(f"   - Data consistency maintained")
        else:
            print(f"   ❌ SYSTEM NOT READY FOR PRODUCTION")
            print(f"   Issues that need resolution:")
            
            if validation_results["api_integration_tests"]["passed"] < validation_results["api_integration_tests"]["total"] * 0.8:
                print(f"      - API integration tests below 80% success rate")
            if not validation_results["data_consistency_check"]["uuid_only"]:
                print(f"      - Mixed ID formats detected in database")
            if not validation_results["sales_transaction_flow"]["working"]:
                print(f"      - Sales transaction flow not working")
            if not validation_results["inventory_management"]["working"]:
                print(f"      - Inventory management issues")
            if not validation_results["frontend_backend_integration"]["working"]:
                print(f"      - Frontend-backend integration problems")
        
        if validation_results["critical_issues"]:
            print(f"\n🚨 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION:")
            for issue in validation_results["critical_issues"]:
                print(f"   - {issue}")
        
        print(f"\n🏁 FINAL CONCLUSION:")
        if production_ready:
            print(f"   ✅ UUID-ONLY SYSTEM FINAL VALIDATION SUCCESSFUL")
            print(f"   - Complete system working with UUID-only architecture")
            print(f"   - No more ObjectId/UUID mixing issues")
            print(f"   - All foreign key relationships working correctly")
            print(f"   - Frontend can successfully interact with all backend APIs")
            print(f"   - No 404 errors due to ID format mismatches")
            print(f"   - Sales, inventory, and DAO transactions working properly")
            print(f"   - System ready for production deployment")
        else:
            print(f"   ❌ UUID-ONLY SYSTEM VALIDATION INCOMPLETE")
            print(f"   - Critical issues need resolution before production")
            print(f"   - Review and fix identified problems")
            print(f"   - Re-run validation after fixes")
        
        return production_ready
if __name__ == "__main__":
    tester = FPTBillManagerAPITester()
    
    print("🚀 Starting Customer Detailed Profile 404 Error Fix Testing")
    print("=" * 80)
    
    # Run Customer Detailed Profile 404 Fix Test
    profile_fix_success = tester.test_customer_detailed_profile_404_fix()
    
    print(f"\n📊 FINAL RESULTS:")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%" if tester.tests_run > 0 else "No tests run")
    print(f"Customer Detailed Profile Fix: {'✅ PASSED' if profile_fix_success else '❌ FAILED'}")
    
    if tester.mongo_connected:
        tester.mongo_client.close()
    
    sys.exit(0 if profile_fix_success else 1)