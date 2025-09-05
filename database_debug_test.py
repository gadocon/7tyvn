#!/usr/bin/env python3
"""
Database Field Structure Debug Test
Debug database field structure để hiểu tại sao customer lookup fail
"""

import requests
import sys
import json
from datetime import datetime
import pymongo
from pymongo import MongoClient
from bson import ObjectId

class DatabaseFieldDebugger:
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

    def run_api_test(self, name, method, endpoint, expected_status, data=None, headers=None):
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
                except:
                    print(f"   Error text: {response.text[:200]}")
                return False, {}

        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            return False, {}

    def debug_database_field_structure(self):
        """
        Debug database field structure để hiểu tại sao customer lookup fail
        
        Debug objectives:
        1. Kiểm tra database structure của customers collection
        2. Xem customers có field `id` hay chỉ có `_id` (ObjectId)
        3. So sánh cách customers được stored vs cách được queried
        4. Test trực tiếp MongoDB query để xem tại sao find_one fail
        """
        print(f"\n🚨 DATABASE FIELD STRUCTURE DEBUG INVESTIGATION")
        print("=" * 80)
        print("🎯 DEBUG OBJECTIVES:")
        print("   1. Kiểm tra database structure của customers collection")
        print("   2. Xem customers có field `id` hay chỉ có `_id` (ObjectId)")
        print("   3. So sánh cách customers được stored vs cách được queried")
        print("   4. Test trực tiếp MongoDB query để xem tại sao find_one fail")
        print("\n🔍 ROOT CAUSE HYPOTHESIS:")
        print("   Customer records có thể được stored với `_id` (ObjectId) nhưng backend đang query bằng `id` field, hoặc ngược lại.")
        
        if not self.mongo_connected:
            print("❌ Cannot perform database debugging without MongoDB connection")
            return False
        
        # Step 1: Examine customers collection structure
        print(f"\n📊 STEP 1: Database Structure Analysis")
        print("=" * 50)
        
        try:
            # Get collection info
            customers_collection = self.db.customers
            total_customers = customers_collection.count_documents({})
            print(f"✅ Total customers in database: {total_customers}")
            
            # Get sample documents to analyze structure
            sample_customers = list(customers_collection.find({}).limit(5))
            
            if not sample_customers:
                print("❌ No customers found in database")
                return False
            
            print(f"\n🔍 Sample Customer Document Structure:")
            for i, customer in enumerate(sample_customers):
                print(f"\n   Customer {i+1}:")
                print(f"   Raw MongoDB Document Keys: {list(customer.keys())}")
                
                # Check for _id field
                if '_id' in customer:
                    _id_value = customer['_id']
                    _id_type = type(_id_value).__name__
                    print(f"   _id field: {_id_value} (type: {_id_type})")
                
                # Check for id field
                if 'id' in customer:
                    id_value = customer['id']
                    id_type = type(id_value).__name__
                    print(f"   id field: {id_value} (type: {id_type})")
                else:
                    print(f"   ❌ NO 'id' field found!")
                
                # Check customer name for identification
                name = customer.get('name', 'Unknown')
                print(f"   name: {name}")
                
                # Show all fields for first customer
                if i == 0:
                    print(f"   All fields: {json.dumps({k: str(v) for k, v in customer.items()}, indent=4, default=str)}")
            
        except Exception as e:
            print(f"❌ Database analysis failed: {e}")
            return False
        
        # Step 2: Create test customer and analyze how it's stored
        print(f"\n🧪 STEP 2: Create Test Customer and Analyze Storage")
        print("=" * 50)
        
        test_customer_name = f"Database Debug Test Customer {int(datetime.now().timestamp())}"
        
        # Create customer via API
        print(f"Creating test customer via API...")
        create_success, create_response = self.run_api_test(
            "Create Test Customer",
            "POST",
            "customers",
            200,
            data={
                "name": test_customer_name,
                "type": "INDIVIDUAL",
                "phone": f"0123456{int(datetime.now().timestamp()) % 1000}",
                "email": f"debug{int(datetime.now().timestamp())}@test.com",
                "address": "Debug Test Address"
            }
        )
        
        if not create_success:
            print("❌ Failed to create test customer via API")
            return False
        
        created_customer_id = create_response.get('id')
        print(f"✅ Created customer via API with ID: {created_customer_id}")
        
        # Now check how it's stored in database
        try:
            # Find by the API-returned ID
            db_customer_by_id = customers_collection.find_one({"id": created_customer_id})
            db_customer_by_objectid = customers_collection.find_one({"_id": ObjectId(created_customer_id) if len(created_customer_id) == 24 else None})
            
            print(f"\n🔍 Database Storage Analysis:")
            print(f"   API returned ID: {created_customer_id} (length: {len(created_customer_id)})")
            
            if db_customer_by_id:
                print(f"   ✅ Found by 'id' field query")
                print(f"   Document _id: {db_customer_by_id.get('_id')} (type: {type(db_customer_by_id.get('_id')).__name__})")
                print(f"   Document id: {db_customer_by_id.get('id')} (type: {type(db_customer_by_id.get('id')).__name__})")
            else:
                print(f"   ❌ NOT found by 'id' field query")
            
            if db_customer_by_objectid:
                print(f"   ✅ Found by '_id' ObjectId query")
                print(f"   Document _id: {db_customer_by_objectid.get('_id')} (type: {type(db_customer_by_objectid.get('_id')).__name__})")
                print(f"   Document id: {db_customer_by_objectid.get('id')} (type: {type(db_customer_by_objectid.get('id')).__name__})")
            else:
                print(f"   ❌ NOT found by '_id' ObjectId query")
            
            # Try to find by name to see the actual document
            db_customer_by_name = customers_collection.find_one({"name": test_customer_name})
            if db_customer_by_name:
                print(f"\n   ✅ Found by name query:")
                print(f"   Actual stored document:")
                print(f"   {json.dumps({k: str(v) for k, v in db_customer_by_name.items()}, indent=4, default=str)}")
            
        except Exception as e:
            print(f"❌ Database storage analysis failed: {e}")
        
        # Step 3: Test API customer lookup with the created customer
        print(f"\n🔍 STEP 3: Test API Customer Lookup")
        print("=" * 50)
        
        # Test basic customer endpoint
        print(f"Testing GET /api/customers/{created_customer_id}")
        get_success, get_response = self.run_api_test(
            f"Get Customer {created_customer_id}",
            "GET",
            f"customers/{created_customer_id}",
            200
        )
        
        if get_success:
            print(f"✅ Basic customer lookup successful")
            print(f"   Response ID: {get_response.get('id')}")
            print(f"   Response name: {get_response.get('name')}")
        else:
            print(f"❌ Basic customer lookup failed")
        
        # Test detailed profile endpoint
        print(f"\nTesting GET /api/customers/{created_customer_id}/detailed-profile")
        detailed_success, detailed_response = self.run_api_test(
            f"Get Customer Detailed Profile {created_customer_id}",
            "GET",
            f"customers/{created_customer_id}/detailed-profile",
            200
        )
        
        if detailed_success:
            print(f"✅ Detailed profile lookup successful")
            print(f"   Response keys: {list(detailed_response.keys())}")
        else:
            print(f"❌ Detailed profile lookup failed")
        
        # Step 4: Test with existing problematic customer ID
        print(f"\n🔍 STEP 4: Test Problematic Customer ID")
        print("=" * 50)
        
        problematic_id = "68b86b157a314c251c8c863b"
        print(f"Testing problematic customer ID: {problematic_id}")
        
        # Check if this ID exists in database
        try:
            # Try different query methods
            db_by_id = customers_collection.find_one({"id": problematic_id})
            db_by_objectid = None
            
            # Try as ObjectId if it's 24 hex chars
            if len(problematic_id) == 24 and all(c in '0123456789abcdef' for c in problematic_id.lower()):
                try:
                    db_by_objectid = customers_collection.find_one({"_id": ObjectId(problematic_id)})
                except:
                    pass
            
            print(f"\n   Database queries for {problematic_id}:")
            print(f"   Found by 'id' field: {'✅ YES' if db_by_id else '❌ NO'}")
            print(f"   Found by '_id' ObjectId: {'✅ YES' if db_by_objectid else '❌ NO'}")
            
            if db_by_id:
                print(f"   Document found by 'id': {db_by_id.get('name', 'Unknown')}")
            
            if db_by_objectid:
                print(f"   Document found by '_id': {db_by_objectid.get('name', 'Unknown')}")
            
            # If found in database, test API
            if db_by_id or db_by_objectid:
                print(f"\n   🔍 Customer exists in database, testing API...")
                
                api_success, api_response = self.run_api_test(
                    f"API Test - Problematic ID",
                    "GET",
                    f"customers/{problematic_id}",
                    200
                )
                
                if api_success:
                    print(f"   ✅ API lookup successful")
                else:
                    print(f"   ❌ API lookup failed - This confirms the bug!")
            
        except Exception as e:
            print(f"❌ Problematic ID analysis failed: {e}")
        
        # Step 5: Analyze parse_from_mongo function behavior
        print(f"\n🔍 STEP 5: Parse Function Analysis")
        print("=" * 50)
        
        try:
            # Get a raw document from database
            raw_doc = customers_collection.find_one({})
            if raw_doc:
                print(f"Raw MongoDB document:")
                print(f"   _id: {raw_doc.get('_id')} (type: {type(raw_doc.get('_id')).__name__})")
                print(f"   id: {raw_doc.get('id', 'NOT FOUND')} (type: {type(raw_doc.get('id', '')).__name__})")
                
                # Simulate parse_from_mongo function
                parsed_doc = dict(raw_doc)
                if '_id' in parsed_doc:
                    parsed_doc['id'] = str(parsed_doc['_id'])
                    parsed_doc.pop('_id', None)
                
                print(f"\nAfter parse_from_mongo simulation:")
                print(f"   id: {parsed_doc.get('id')} (type: {type(parsed_doc.get('id')).__name__})")
                print(f"   _id: {parsed_doc.get('_id', 'REMOVED')}")
                
        except Exception as e:
            print(f"❌ Parse function analysis failed: {e}")
        
        # Step 6: Summary and diagnosis
        print(f"\n📊 STEP 6: Summary and Diagnosis")
        print("=" * 50)
        
        print(f"🔍 FINDINGS:")
        print(f"   1. Database connection: {'✅ Working' if self.mongo_connected else '❌ Failed'}")
        print(f"   2. Total customers in DB: {total_customers}")
        print(f"   3. Test customer creation: {'✅ Success' if create_success else '❌ Failed'}")
        print(f"   4. Test customer API lookup: {'✅ Success' if get_success else '❌ Failed'}")
        print(f"   5. Test detailed profile: {'✅ Success' if detailed_success else '❌ Failed'}")
        
        print(f"\n🔧 ROOT CAUSE ANALYSIS:")
        if not get_success or not detailed_success:
            print(f"   🚨 CRITICAL: Customer lookup endpoints have issues")
            print(f"   💡 LIKELY CAUSES:")
            print(f"      - Backend query logic using wrong field ('id' vs '_id')")
            print(f"      - parse_from_mongo function not working correctly")
            print(f"      - Database field mapping inconsistency")
            print(f"      - ObjectId to string conversion issues")
        else:
            print(f"   ✅ Customer lookup endpoints working with new customers")
            print(f"   💡 POSSIBLE ISSUES:")
            print(f"      - Old customers may have different field structure")
            print(f"      - Specific customer IDs may have format issues")
            print(f"      - Database migration may have left inconsistent data")
        
        print(f"\n🎯 RECOMMENDATIONS:")
        print(f"   1. Check backend customer query logic in server.py")
        print(f"   2. Verify parse_from_mongo function implementation")
        print(f"   3. Ensure consistent use of 'id' field vs '_id' field")
        print(f"   4. Consider database migration to fix field inconsistencies")
        print(f"   5. Add logging to customer lookup endpoints for debugging")
        
        # Clean up test customer
        try:
            if created_customer_id:
                customers_collection.delete_one({"id": created_customer_id})
                print(f"\n🧹 Cleaned up test customer: {created_customer_id}")
        except:
            pass
        
        self.tests_run += 1
        if get_success and detailed_success:
            self.tests_passed += 1
            return True
        else:
            return False

    def run_comprehensive_debug(self):
        """Run comprehensive database field structure debugging"""
        print(f"\n🎯 COMPREHENSIVE DATABASE FIELD STRUCTURE DEBUG")
        print("=" * 80)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Run the main debug investigation
        success = self.debug_database_field_structure()
        
        # Final summary
        print(f"\n📊 FINAL TEST SUMMARY")
        print("=" * 50)
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        print(f"   Overall Status: {'✅ SUCCESS' if success else '❌ ISSUES FOUND'}")
        
        return success

def main():
    """Main function to run database debugging"""
    print("🚀 Starting Database Field Structure Debug Investigation...")
    
    debugger = DatabaseFieldDebugger()
    success = debugger.run_comprehensive_debug()
    
    if success:
        print(f"\n✅ Database debugging completed successfully")
        sys.exit(0)
    else:
        print(f"\n❌ Database debugging found critical issues")
        sys.exit(1)

if __name__ == "__main__":
    main()