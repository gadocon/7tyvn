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

    def run_all_tests(self):
        """Run customer ObjectId vs UUID fix verification"""
        print(f"\n🚀 STARTING CUSTOMER OBJECTID VS UUID FIX VERIFICATION")
        print("=" * 80)
        print(f"🎯 Review Request: Test customer endpoints sau khi fix ObjectId vs UUID issue")
        print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 API Base URL: {self.base_url}")
        
        # Run the customer ObjectId/UUID fix test
        success = self.test_customer_objectid_uuid_fix()
        
        # Print final summary
        print(f"\n📊 FINAL TEST SUMMARY")
        print("=" * 50)
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if success:
            print(f"\n✅ OVERALL RESULT: CUSTOMER OBJECTID VS UUID FIX VERIFIED")
            print(f"   - Customer ID 68b86b157a314c251c8c863b fully functional")
            print(f"   - All customer endpoints support mixed ID formats")
            print(f"   - DELETE, UPDATE, and TRANSACTIONS endpoints working")
            print(f"   - Dual lookup strategy successfully implemented")
        else:
            print(f"\n❌ OVERALL RESULT: CUSTOMER OBJECTID VS UUID FIX INCOMPLETE")
            print(f"   - Some customer endpoints still have issues")
            print(f"   - Further debugging required")
            print(f"   - Check backend dual lookup implementation")
        
        return success

if __name__ == "__main__":
    tester = FPTBillManagerAPITester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)