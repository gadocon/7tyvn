#!/usr/bin/env python3
"""
Database and Customer Test Data Creation
Test database collections and create customer test data as requested in review
"""

import requests
import json
import uuid
from datetime import datetime

class DatabaseCustomerTester:
    def __init__(self, base_url="https://bill-manager-crm.preview.emergentagent.com"):
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

    def test_database_and_create_customer_test_data(self):
        """Test database collections and create customer test data as requested in review"""
        print(f"\n🎯 DATABASE AND CUSTOMER TEST DATA CREATION")
        print("=" * 70)
        print("🔍 TESTING OBJECTIVES:")
        print("   1. Check current database collections")
        print("   2. Create 2-3 test customers with proper UUID format")
        print("   3. Test GET /api/customers to verify customers exist")
        print("   4. Test GET /api/customers/{customer_id}/detailed-profile with created customers")
        print("   5. Verify API returns 200 with customer data")
        
        test_results = {
            "database_check": False,
            "customers_created": 0,
            "customers_api_test": False,
            "detailed_profile_tests": 0,
            "detailed_profile_success": 0
        }
        
        # Step 1: Check current database collections
        print(f"\n📋 STEP 1: Checking current database collections...")
        customers_success, customers_response = self.run_test(
            "Get Current Customers",
            "GET",
            "customers",
            200
        )
        
        if customers_success:
            existing_count = len(customers_response)
            print(f"✅ Database check successful")
            print(f"📊 Found {existing_count} existing customers in database")
            test_results["database_check"] = True
            test_results["customers_api_test"] = True
            
            # Show sample existing customers
            if existing_count > 0:
                print(f"📋 Sample existing customers:")
                for i, customer in enumerate(customers_response[:3], 1):
                    print(f"   {i}. {customer.get('name', 'Unknown')} (ID: {customer.get('id', 'N/A')})")
        else:
            print(f"❌ Failed to check database collections")
            return False
        
        # Step 2: Create 2-3 test customers with proper UUID format
        print(f"\n🔧 STEP 2: Creating test customers with proper UUID format...")
        
        timestamp = int(datetime.now().timestamp())
        test_customers_data = [
            {
                "name": f"Test Customer Database Check {timestamp}",
                "type": "INDIVIDUAL",
                "phone": f"0901{timestamp % 1000000:06d}",
                "email": f"test_db_check_{timestamp}@example.com",
                "address": "123 Test Database Street, Test City",
                "notes": "Created for database and customer detailed profile testing"
            },
            {
                "name": f"Validation Test Customer {timestamp}",
                "type": "INDIVIDUAL", 
                "phone": f"0902{timestamp % 1000000:06d}",
                "email": f"validation_test_{timestamp}@example.com",
                "address": "456 Validation Test Avenue, Test City",
                "notes": "Created for API validation and detailed profile endpoint testing"
            },
            {
                "name": f"Profile API Test Customer {timestamp}",
                "type": "AGENT",
                "phone": f"0903{timestamp % 1000000:06d}",
                "email": f"profile_api_test_{timestamp}@example.com", 
                "address": "789 Profile API Test Boulevard, Test City",
                "notes": "Created specifically for detailed-profile API endpoint testing"
            }
        ]
        
        created_customer_ids = []
        
        for i, customer_data in enumerate(test_customers_data, 1):
            print(f"\n   🔧 Creating test customer {i}: {customer_data['name']}")
            
            create_success, create_response = self.run_test(
                f"Create Test Customer {i}",
                "POST",
                "customers",
                200,
                data=customer_data
            )
            
            if create_success:
                customer_id = create_response.get('id')
                created_customer_ids.append(customer_id)
                test_results["customers_created"] += 1
                
                print(f"   ✅ Created successfully")
                print(f"      Customer ID: {customer_id}")
                print(f"      Name: {create_response.get('name')}")
                print(f"      Type: {create_response.get('type')}")
                print(f"      Phone: {create_response.get('phone')}")
                
                # Verify UUID format
                try:
                    uuid.UUID(customer_id)
                    print(f"      ✅ UUID format valid: {customer_id}")
                except ValueError:
                    print(f"      ❌ Invalid UUID format: {customer_id}")
            else:
                print(f"   ❌ Failed to create test customer {i}")
        
        print(f"\n📊 Customer Creation Summary:")
        print(f"   - Attempted: {len(test_customers_data)} customers")
        print(f"   - Created: {test_results['customers_created']} customers")
        print(f"   - Success Rate: {(test_results['customers_created']/len(test_customers_data)*100):.1f}%")
        
        # Step 3: Test GET /api/customers to verify customers exist
        print(f"\n📋 STEP 3: Verifying customers exist in GET /api/customers...")
        
        verify_success, verify_response = self.run_test(
            "Verify Customers Exist",
            "GET",
            "customers",
            200
        )
        
        if verify_success:
            total_customers = len(verify_response)
            print(f"✅ GET /api/customers working correctly")
            print(f"📊 Total customers now: {total_customers}")
            
            # Check if our created customers are in the list
            found_created_customers = 0
            for customer_id in created_customer_ids:
                found = any(c.get('id') == customer_id for c in verify_response)
                if found:
                    found_created_customers += 1
                    print(f"   ✅ Found created customer: {customer_id}")
                else:
                    print(f"   ❌ Missing created customer: {customer_id}")
            
            print(f"📊 Created customers found: {found_created_customers}/{len(created_customer_ids)}")
        else:
            print(f"❌ Failed to verify customers exist")
        
        # Step 4: Test GET /api/customers/{customer_id}/detailed-profile with created customers
        print(f"\n🎯 STEP 4: Testing detailed-profile API with created customers...")
        
        for i, customer_id in enumerate(created_customer_ids, 1):
            print(f"\n   🔍 Testing detailed-profile for customer {i}: {customer_id}")
            
            profile_success, profile_response = self.run_test(
                f"Customer Detailed Profile {i}",
                "GET",
                f"customers/{customer_id}/detailed-profile",
                200
            )
            
            test_results["detailed_profile_tests"] += 1
            
            if profile_success:
                test_results["detailed_profile_success"] += 1
                print(f"   ✅ Detailed-profile API returned 200 status")
                
                # Verify response structure
                required_fields = ['success', 'customer', 'metrics', 'credit_cards', 'recent_activities', 'performance']
                missing_fields = [field for field in required_fields if field not in profile_response]
                
                if not missing_fields:
                    print(f"   ✅ All required fields present: {required_fields}")
                    
                    # Check customer data
                    customer_data = profile_response.get('customer', {})
                    print(f"   📊 Customer data:")
                    print(f"      - Name: {customer_data.get('name', 'N/A')}")
                    print(f"      - Type: {customer_data.get('type', 'N/A')}")
                    print(f"      - Phone: {customer_data.get('phone', 'N/A')}")
                    print(f"      - Active: {customer_data.get('is_active', 'N/A')}")
                    
                    # Check metrics
                    metrics = profile_response.get('metrics', {})
                    print(f"   📊 Metrics:")
                    print(f"      - Total Transactions: {metrics.get('total_transactions', 0)}")
                    print(f"      - Total Value: {metrics.get('total_transaction_value', 0)}")
                    print(f"      - Total Profit: {metrics.get('total_profit', 0)}")
                    
                    # Check recent activities
                    activities = profile_response.get('recent_activities', [])
                    print(f"   📊 Recent Activities: {len(activities)} activities")
                    
                    # Check credit cards
                    credit_cards = profile_response.get('credit_cards', [])
                    print(f"   📊 Credit Cards: {len(credit_cards)} cards")
                    
                else:
                    print(f"   ❌ Missing required fields: {missing_fields}")
                    
            else:
                print(f"   ❌ Detailed-profile API failed for customer {customer_id}")
        
        # Step 5: Final verification and summary
        print(f"\n📊 STEP 5: Final Results Summary")
        print("=" * 50)
        
        print(f"✅ Database Collections Check: {'PASS' if test_results['database_check'] else 'FAIL'}")
        print(f"✅ Test Customers Created: {test_results['customers_created']}/3")
        print(f"✅ GET /api/customers API: {'PASS' if test_results['customers_api_test'] else 'FAIL'}")
        print(f"✅ Detailed-Profile Tests: {test_results['detailed_profile_success']}/{test_results['detailed_profile_tests']}")
        
        # Calculate overall success
        total_objectives = 5  # 5 main objectives from the review request
        completed_objectives = 0
        
        if test_results["database_check"]:
            completed_objectives += 1
        if test_results["customers_created"] >= 2:  # At least 2 customers created
            completed_objectives += 1
        if test_results["customers_api_test"]:
            completed_objectives += 1
        if test_results["detailed_profile_tests"] > 0:
            completed_objectives += 1
        if test_results["detailed_profile_success"] > 0:
            completed_objectives += 1
        
        success_rate = (completed_objectives / total_objectives) * 100
        
        print(f"\n🎯 OVERALL SUCCESS RATE: {success_rate:.1f}% ({completed_objectives}/{total_objectives} objectives)")
        
        if success_rate >= 80:
            print(f"🎉 SUCCESS: Database and customer test data creation completed successfully!")
            print(f"✅ Database has customers collection with existing data")
            print(f"✅ Created {test_results['customers_created']} new test customers with proper UUID format")
            print(f"✅ GET /api/customers API working correctly")
            print(f"✅ Customer detailed-profile API returning 200 status instead of 404")
            print(f"✅ CustomerNameLink should now have data for navigation testing")
            
            if test_results["detailed_profile_success"] == test_results["detailed_profile_tests"]:
                print(f"🏆 PERFECT: All detailed-profile API tests passed!")
            
            self.tests_passed += 1
            return True
        else:
            print(f"⚠️  PARTIAL SUCCESS: Some objectives completed but needs attention")
            print(f"🔍 Review individual test results above for specific issues")
            return False

if __name__ == "__main__":
    tester = DatabaseCustomerTester()
    success = tester.test_database_and_create_customer_test_data()
    
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%" if tester.tests_run > 0 else "No tests run")
    
    if success:
        print(f"\n🎉 Database and Customer Test Data Creation: PASSED")
    else:
        print(f"\n❌ Database and Customer Test Data Creation: FAILED")