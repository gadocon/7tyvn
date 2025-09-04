#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class CustomersCheckboxTester:
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

    def test_customers_checkbox_functionality(self):
        """URGENT: Test customers functionality for checkbox selection feature implementation"""
        print(f"\n🎯 CUSTOMERS CHECKBOX SELECTION FEATURE TESTING")
        print("=" * 70)
        print("🔍 Testing customers endpoints for bulk actions functionality")
        
        all_tests_passed = True
        
        # Test 1: GET /customers endpoint with various filters
        print(f"\n📋 TEST 1: GET /customers endpoint")
        print("-" * 40)
        
        # Basic customers list
        customers_success, customers_response = self.run_test(
            "Get Customers List (Basic)",
            "GET",
            "customers",
            200
        )
        
        if customers_success:
            print(f"✅ Found {len(customers_response)} customers")
            if customers_response:
                sample_customer = customers_response[0]
                required_fields = ['id', 'name', 'type', 'phone', 'is_active']
                missing_fields = [field for field in required_fields if field not in sample_customer]
                if missing_fields:
                    print(f"❌ Missing required fields: {missing_fields}")
                    all_tests_passed = False
                else:
                    print(f"✅ Customer structure verified: {list(sample_customer.keys())}")
        else:
            all_tests_passed = False
        
        # Test with search parameter
        if customers_response:
            search_name = customers_response[0].get('name', '').split()[0] if customers_response[0].get('name') else 'Test'
            search_success, search_response = self.run_test(
                f"Get Customers with Search: '{search_name}'",
                "GET",
                f"customers?search={search_name}",
                200
            )
            
            if search_success:
                print(f"✅ Search functionality working: found {len(search_response)} results")
            else:
                all_tests_passed = False
        
        # Test with customer_type filter
        type_success, type_response = self.run_test(
            "Get Customers by Type (INDIVIDUAL)",
            "GET",
            "customers?customer_type=INDIVIDUAL",
            200
        )
        
        if type_success:
            individual_count = len([c for c in type_response if c.get('type') == 'INDIVIDUAL'])
            print(f"✅ Type filter working: {individual_count}/{len(type_response)} INDIVIDUAL customers")
        else:
            all_tests_passed = False
        
        # Test with is_active filter
        active_success, active_response = self.run_test(
            "Get Active Customers",
            "GET",
            "customers?is_active=true",
            200
        )
        
        if active_success:
            active_count = len([c for c in active_response if c.get('is_active') == True])
            print(f"✅ Active filter working: {active_count}/{len(active_response)} active customers")
        else:
            all_tests_passed = False
        
        # Test 2: DELETE /customers/{customer_id} endpoint
        print(f"\n🗑️  TEST 2: DELETE /customers/{{customer_id}} endpoint")
        print("-" * 40)
        
        # Create a test customer for deletion
        test_customer_data = {
            "name": f"Test Customer for Deletion {int(datetime.now().timestamp())}",
            "type": "INDIVIDUAL",
            "phone": f"098765{int(datetime.now().timestamp()) % 10000}",
            "email": f"test_delete_{int(datetime.now().timestamp())}@example.com",
            "address": "Test Address for Deletion"
        }
        
        create_success, create_response = self.run_test(
            "Create Test Customer for Deletion",
            "POST",
            "customers",
            200,
            data=test_customer_data
        )
        
        delete_success = False
        if create_success:
            customer_id = create_response.get('id')
            print(f"✅ Created test customer: {customer_id}")
            
            # Test valid deletion
            delete_success, delete_response = self.run_test(
                "Delete Valid Customer",
                "DELETE",
                f"customers/{customer_id}",
                200
            )
            
            if delete_success:
                print(f"✅ Customer deletion successful")
                # Verify customer is actually deleted
                verify_success, verify_response = self.run_test(
                    "Verify Customer Deleted",
                    "GET",
                    f"customers/{customer_id}",
                    404
                )
                if verify_success:
                    print(f"✅ Customer properly removed from database")
                else:
                    print(f"❌ Customer still exists after deletion")
                    all_tests_passed = False
            else:
                all_tests_passed = False
        else:
            all_tests_passed = False
        
        # Test invalid customer ID deletion
        invalid_delete_success, invalid_delete_response = self.run_test(
            "Delete Invalid Customer ID",
            "DELETE",
            "customers/invalid-customer-id-12345",
            404
        )
        
        if invalid_delete_success:
            print(f"✅ Invalid customer ID properly handled with 404")
        else:
            all_tests_passed = False
        
        # Test 3: GET /customers/stats endpoint
        print(f"\n📊 TEST 3: GET /customers/stats endpoint")
        print("-" * 40)
        
        stats_success, stats_response = self.run_test(
            "Get Customer Statistics",
            "GET",
            "customers/stats",
            200
        )
        
        if stats_success:
            required_stats = ['total_customers', 'individual_customers', 'agent_customers', 'active_customers', 'total_customer_value']
            missing_stats = [stat for stat in required_stats if stat not in stats_response]
            
            if missing_stats:
                print(f"❌ Missing required stats: {missing_stats}")
                all_tests_passed = False
            else:
                print(f"✅ All required statistics present:")
                for stat in required_stats:
                    print(f"   - {stat}: {stats_response.get(stat, 0)}")
        else:
            all_tests_passed = False
        
        # Test 4: GET /customers/export endpoint
        print(f"\n📤 TEST 4: GET /customers/export endpoint")
        print("-" * 40)
        
        # Test Excel export functionality
        url = f"{self.api_url}/customers/export"
        print(f"🌐 Making request to: {url}")
        
        export_success = False
        try:
            response = requests.get(url, timeout=30)
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                # Check if response is Excel file
                content_type = response.headers.get('content-type', '')
                content_disposition = response.headers.get('content-disposition', '')
                
                print(f"📋 Content-Type: {content_type}")
                print(f"📋 Content-Disposition: {content_disposition}")
                
                # Verify it's an Excel file
                if 'spreadsheet' in content_type or 'excel' in content_type:
                    print(f"✅ Excel export working: proper content type")
                    
                    # Check file size
                    content_length = len(response.content)
                    print(f"📊 File size: {content_length} bytes")
                    
                    if content_length > 0:
                        print(f"✅ Excel file has content")
                        
                        # Check filename in headers
                        if 'filename=' in content_disposition:
                            filename = content_disposition.split('filename=')[1].strip('"')
                            print(f"✅ Export filename: {filename}")
                        else:
                            print(f"⚠️  No filename in response headers")
                        
                        export_success = True
                        self.tests_passed += 1
                    else:
                        print(f"❌ Excel file is empty")
                        all_tests_passed = False
                else:
                    print(f"❌ Response is not Excel format: {content_type}")
                    all_tests_passed = False
            else:
                print(f"❌ Export failed with status {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text[:200]}")
                all_tests_passed = False
                
        except Exception as e:
            print(f"❌ Export request failed: {e}")
            all_tests_passed = False
        finally:
            self.tests_run += 1
        
        # Summary for customers checkbox functionality
        print(f"\n📊 CUSTOMERS CHECKBOX FUNCTIONALITY TEST RESULTS:")
        print(f"   GET /customers endpoint: {'✅ PASSED' if customers_success else '❌ FAILED'}")
        print(f"   DELETE /customers/{{id}} endpoint: {'✅ PASSED' if delete_success else '❌ FAILED'}")
        print(f"   GET /customers/stats endpoint: {'✅ PASSED' if stats_success else '❌ FAILED'}")
        print(f"   GET /customers/export endpoint: {'✅ PASSED' if export_success else '❌ FAILED'}")
        
        if all_tests_passed:
            print(f"\n🎉 CUSTOMERS CHECKBOX SELECTION FEATURE FULLY FUNCTIONAL!")
            print(f"   ✅ Customer list retrieval with filters working")
            print(f"   ✅ Individual customer deletion working")
            print(f"   ✅ Customer statistics for dashboard working")
            print(f"   ✅ Bulk export functionality working")
            print(f"   🚀 Ready for checkbox selection and bulk actions implementation")
        else:
            print(f"\n🚨 CUSTOMERS CHECKBOX SELECTION FEATURE HAS ISSUES!")
            print(f"   ⚠️  Some endpoints not working properly")
            print(f"   ⚠️  May affect bulk actions functionality")
        
        return all_tests_passed

def main():
    print("🎯 CUSTOMERS CHECKBOX FUNCTIONALITY TESTING (Review Request)")
    print("=" * 80)
    print("Testing customers functionality for checkbox selection feature implementation")
    
    tester = CustomersCheckboxTester()
    
    # Run the customers checkbox tests as requested in review
    checkbox_success = tester.test_customers_checkbox_functionality()
    
    if checkbox_success:
        print(f"\n🎉 Customers Checkbox Tests PASSED!")
        print(f"✅ All customers functionality working correctly")
        print(f"✅ Ready for checkbox selection and bulk actions")
    else:
        print(f"\n❌ Customers Checkbox Tests FAILED!")
        print(f"⚠️  Some customers functionality has issues")
        print(f"🚨 May affect bulk actions implementation")
    
    print(f"\n{'='*80}")
    print(f"🏁 FINAL TEST SUMMARY")
    print(f"📊 Tests Run: {tester.tests_run}")
    print(f"📊 Tests Passed: {tester.tests_passed}")
    print(f"📊 Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%" if tester.tests_run > 0 else "No tests run")
    
    if checkbox_success:
        print(f"\n🎯 REVIEW REQUEST FULFILLED: Customers checkbox testing completed successfully!")
        print(f"   ✅ GET /customers endpoint working with filters")
        print(f"   ✅ DELETE /customers/{{customer_id}} endpoint working")
        print(f"   ✅ GET /customers/stats endpoint working")
        print(f"   ✅ GET /customers/export endpoint working")
        print(f"\n🎉 Customers checkbox selection and bulk actions ready!")
    else:
        print(f"\n⚠️  REVIEW REQUEST ISSUES: Customers functionality needs attention!")
        print(f"   ❌ Some endpoints not working properly")
        print(f"   🚨 May affect bulk actions functionality")
        print(f"   🔧 Customers functionality requires fixes")
    
    return 0 if checkbox_success else 1

if __name__ == "__main__":
    exit(main())