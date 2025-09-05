#!/usr/bin/env python3
"""
Customer Lookup Fix Test
Test the fix for customer lookup issues where customers stored with ObjectId _id 
cannot be found by API endpoints that query by 'id' field.
"""

import requests
import sys
import json
from datetime import datetime
import pymongo
from pymongo import MongoClient
from bson import ObjectId

class CustomerLookupFixTester:
    def __init__(self, base_url="https://seventy-crm-fix.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
        # MongoDB connection for direct database debugging
        try:
            self.mongo_client = MongoClient("mongodb://localhost:27017")
            self.db = self.mongo_client["test_database"]
            self.mongo_connected = True
            print("✅ MongoDB connection established")
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

    def test_problematic_customer_lookup(self):
        """Test the specific problematic customer ID that was failing"""
        print(f"\n🚨 TESTING PROBLEMATIC CUSTOMER LOOKUP FIX")
        print("=" * 60)
        
        problematic_id = "68b86b157a314c251c8c863b"
        print(f"🎯 Target Customer ID: {problematic_id}")
        
        if not self.mongo_connected:
            print("❌ Cannot test without MongoDB connection")
            return False
        
        # First verify the customer exists in database
        try:
            customers_collection = self.db.customers
            
            # This customer should exist with _id as ObjectId but no 'id' field matching the ObjectId string
            db_customer = customers_collection.find_one({"_id": ObjectId(problematic_id)})
            
            if not db_customer:
                print(f"❌ Customer {problematic_id} not found in database")
                return False
            
            print(f"✅ Customer found in database:")
            print(f"   Name: {db_customer.get('name', 'Unknown')}")
            print(f"   _id: {db_customer.get('_id')} (ObjectId)")
            print(f"   id field: {db_customer.get('id', 'NOT FOUND')}")
            
            # The issue: customer has ObjectId _id but different UUID in 'id' field
            # Backend should be able to find by either _id OR id field
            
        except Exception as e:
            print(f"❌ Database check failed: {e}")
            return False
        
        # Test API endpoints that should now work
        print(f"\n🔍 Testing API endpoints with problematic ID...")
        
        # Test 1: Basic customer endpoint
        basic_success, basic_response = self.run_api_test(
            f"Basic Customer Lookup - {problematic_id}",
            "GET",
            f"customers/{problematic_id}",
            200
        )
        
        # Test 2: Detailed profile endpoint  
        detailed_success, detailed_response = self.run_api_test(
            f"Detailed Profile Lookup - {problematic_id}",
            "GET", 
            f"customers/{problematic_id}/detailed-profile",
            200
        )
        
        # Test 3: Transactions summary endpoint
        transactions_success, transactions_response = self.run_api_test(
            f"Transactions Summary - {problematic_id}",
            "GET",
            f"customers/{problematic_id}/transactions-summary", 
            200
        )
        
        print(f"\n📊 RESULTS:")
        print(f"   Basic lookup: {'✅ SUCCESS' if basic_success else '❌ FAILED'}")
        print(f"   Detailed profile: {'✅ SUCCESS' if detailed_success else '❌ FAILED'}")
        print(f"   Transactions summary: {'✅ SUCCESS' if transactions_success else '❌ FAILED'}")
        
        if basic_success and detailed_success:
            print(f"\n🎉 CUSTOMER LOOKUP FIX VERIFIED!")
            print(f"   The backend can now find customers by ObjectId string")
            return True
        else:
            print(f"\n❌ CUSTOMER LOOKUP STILL BROKEN")
            print(f"   Backend still cannot find customers by ObjectId string")
            return False

    def test_parse_from_mongo_function(self):
        """Test the parse_from_mongo function behavior with real data"""
        print(f"\n🔍 TESTING PARSE_FROM_MONGO FUNCTION")
        print("=" * 50)
        
        if not self.mongo_connected:
            print("❌ Cannot test without MongoDB connection")
            return False
        
        try:
            customers_collection = self.db.customers
            
            # Get a few sample customers with different structures
            sample_customers = list(customers_collection.find({}).limit(3))
            
            print(f"Testing parse_from_mongo with {len(sample_customers)} sample customers:")
            
            for i, raw_customer in enumerate(sample_customers):
                print(f"\n   Customer {i+1}: {raw_customer.get('name', 'Unknown')}")
                print(f"   Raw _id: {raw_customer.get('_id')} (type: {type(raw_customer.get('_id')).__name__})")
                print(f"   Raw id: {raw_customer.get('id', 'NOT FOUND')} (type: {type(raw_customer.get('id', '')).__name__})")
                
                # Simulate parse_from_mongo function
                parsed_customer = dict(raw_customer)
                
                # Convert MongoDB ObjectId to string for JSON serialization
                if '_id' in parsed_customer:
                    # If there's no 'id' field, create one from _id
                    if 'id' not in parsed_customer or not parsed_customer['id']:
                        parsed_customer['id'] = str(parsed_customer['_id'])
                    parsed_customer.pop('_id', None)
                
                print(f"   Parsed id: {parsed_customer.get('id')} (type: {type(parsed_customer.get('id')).__name__})")
                print(f"   Parsed _id: {parsed_customer.get('_id', 'REMOVED')}")
                
                # Test if this parsed customer would be findable by API
                customer_id = parsed_customer.get('id')
                if customer_id:
                    # Quick API test
                    api_success, api_response = self.run_api_test(
                        f"API Test Parsed Customer {i+1}",
                        "GET",
                        f"customers/{customer_id}",
                        200
                    )
                    
                    if api_success:
                        print(f"   ✅ API can find this customer after parsing")
                    else:
                        print(f"   ❌ API still cannot find this customer")
            
            return True
            
        except Exception as e:
            print(f"❌ Parse function test failed: {e}")
            return False

    def test_customer_query_methods(self):
        """Test different methods of querying customers to verify fix"""
        print(f"\n🔍 TESTING CUSTOMER QUERY METHODS")
        print("=" * 50)
        
        if not self.mongo_connected:
            print("❌ Cannot test without MongoDB connection")
            return False
        
        try:
            customers_collection = self.db.customers
            
            # Find customers with different ID patterns
            uuid_customers = list(customers_collection.find({"id": {"$regex": "^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"}}).limit(2))
            objectid_only_customers = list(customers_collection.find({"id": {"$exists": False}}).limit(2))
            
            print(f"Found {len(uuid_customers)} customers with UUID format 'id' field")
            print(f"Found {len(objectid_only_customers)} customers with no 'id' field (ObjectId only)")
            
            # Test UUID format customers
            for customer in uuid_customers:
                customer_id = customer.get('id')
                print(f"\n   Testing UUID customer: {customer.get('name')} (ID: {customer_id})")
                
                success, response = self.run_api_test(
                    f"UUID Customer Test",
                    "GET",
                    f"customers/{customer_id}",
                    200
                )
                
                if success:
                    print(f"   ✅ UUID customer lookup successful")
                else:
                    print(f"   ❌ UUID customer lookup failed")
            
            # Test ObjectId-only customers (using _id as string)
            for customer in objectid_only_customers:
                objectid_str = str(customer.get('_id'))
                print(f"\n   Testing ObjectId customer: {customer.get('name')} (ObjectId: {objectid_str})")
                
                success, response = self.run_api_test(
                    f"ObjectId Customer Test",
                    "GET", 
                    f"customers/{objectid_str}",
                    200
                )
                
                if success:
                    print(f"   ✅ ObjectId customer lookup successful")
                else:
                    print(f"   ❌ ObjectId customer lookup failed")
            
            return True
            
        except Exception as e:
            print(f"❌ Query methods test failed: {e}")
            return False

    def test_customer_creation_and_lookup_consistency(self):
        """Test that newly created customers can be looked up consistently"""
        print(f"\n🔍 TESTING CUSTOMER CREATION AND LOOKUP CONSISTENCY")
        print("=" * 60)
        
        test_customer_name = f"Consistency Test Customer {int(datetime.now().timestamp())}"
        
        # Create customer via API
        create_success, create_response = self.run_api_test(
            "Create Consistency Test Customer",
            "POST",
            "customers",
            200,
            data={
                "name": test_customer_name,
                "type": "INDIVIDUAL", 
                "phone": f"0987654{int(datetime.now().timestamp()) % 1000}",
                "email": f"consistency{int(datetime.now().timestamp())}@test.com",
                "address": "Consistency Test Address"
            }
        )
        
        if not create_success:
            print("❌ Failed to create test customer")
            return False
        
        created_id = create_response.get('id')
        print(f"✅ Created customer with ID: {created_id}")
        
        # Test immediate lookup
        immediate_success, immediate_response = self.run_api_test(
            "Immediate Lookup After Creation",
            "GET",
            f"customers/{created_id}",
            200
        )
        
        # Test detailed profile lookup
        detailed_success, detailed_response = self.run_api_test(
            "Detailed Profile After Creation", 
            "GET",
            f"customers/{created_id}/detailed-profile",
            200
        )
        
        # Check database storage
        if self.mongo_connected:
            try:
                customers_collection = self.db.customers
                db_customer = customers_collection.find_one({"id": created_id})
                
                if db_customer:
                    print(f"✅ Customer found in database by 'id' field")
                    print(f"   Database _id: {db_customer.get('_id')}")
                    print(f"   Database id: {db_customer.get('id')}")
                else:
                    print(f"❌ Customer not found in database by 'id' field")
                
                # Clean up
                customers_collection.delete_one({"id": created_id})
                print(f"🧹 Cleaned up test customer")
                
            except Exception as e:
                print(f"⚠️ Database check failed: {e}")
        
        success = immediate_success and detailed_success
        print(f"\n📊 CONSISTENCY TEST: {'✅ SUCCESS' if success else '❌ FAILED'}")
        
        return success

    def run_comprehensive_test(self):
        """Run comprehensive customer lookup fix testing"""
        print(f"\n🎯 COMPREHENSIVE CUSTOMER LOOKUP FIX TESTING")
        print("=" * 80)
        print(f"🕐 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Test 1: Problematic customer lookup
        test1_success = self.test_problematic_customer_lookup()
        
        # Test 2: Parse function behavior
        test2_success = self.test_parse_from_mongo_function()
        
        # Test 3: Different query methods
        test3_success = self.test_customer_query_methods()
        
        # Test 4: Creation and lookup consistency
        test4_success = self.test_customer_creation_and_lookup_consistency()
        
        # Final summary
        print(f"\n📊 COMPREHENSIVE TEST SUMMARY")
        print("=" * 50)
        print(f"   1. Problematic Customer Lookup: {'✅ PASS' if test1_success else '❌ FAIL'}")
        print(f"   2. Parse Function Test: {'✅ PASS' if test2_success else '❌ FAIL'}")
        print(f"   3. Query Methods Test: {'✅ PASS' if test3_success else '❌ FAIL'}")
        print(f"   4. Creation Consistency Test: {'✅ PASS' if test4_success else '❌ FAIL'}")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "0%")
        
        overall_success = test1_success and test2_success and test3_success and test4_success
        print(f"   Overall Status: {'✅ ALL TESTS PASSED' if overall_success else '❌ SOME TESTS FAILED'}")
        
        if test1_success:
            print(f"\n🎉 CUSTOMER LOOKUP FIX VERIFICATION: SUCCESS!")
            print(f"   ✅ Problematic customer ID 68b86b157a314c251c8c863b can now be found")
            print(f"   ✅ Backend properly handles ObjectId string lookups")
            print(f"   ✅ Customer detail pages should now work correctly")
        else:
            print(f"\n❌ CUSTOMER LOOKUP FIX VERIFICATION: FAILED!")
            print(f"   ❌ Problematic customer ID still cannot be found")
            print(f"   ❌ Backend still has issues with ObjectId string lookups")
            print(f"   ❌ Customer detail pages will continue to show 404 errors")
        
        return overall_success

def main():
    """Main function to run customer lookup fix testing"""
    print("🚀 Starting Customer Lookup Fix Testing...")
    
    tester = CustomerLookupFixTester()
    success = tester.run_comprehensive_test()
    
    if success:
        print(f"\n✅ Customer lookup fix testing completed successfully")
        sys.exit(0)
    else:
        print(f"\n❌ Customer lookup fix testing found issues")
        sys.exit(1)

if __name__ == "__main__":
    main()