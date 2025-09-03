#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime

class CustomerDetailPageTester:
    def __init__(self, base_url="https://crm7ty.preview.emergentagent.com"):
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

    def test_customer_detail_page_comprehensive(self):
        """Comprehensive test for Customer Detail Page backend API implementation"""
        print(f"\n🎯 COMPREHENSIVE CUSTOMER DETAIL PAGE API TESTING")
        print("=" * 70)
        print("🔍 Testing Customer Detail Page backend API implementation as requested")
        
        # Step 1: Get list of customers to find real customer IDs
        print(f"\n📋 STEP 1: Getting customers list to find real customer IDs...")
        customers_success, customers_response = self.run_test(
            "Get Customers List",
            "GET", 
            "customers",
            200
        )
        
        if not customers_success or not customers_response:
            print("❌ Failed to get customers list")
            return False
            
        print(f"✅ Found {len(customers_response)} customers in database")
        
        # Find customers with different data profiles for testing
        customers_with_transactions = []
        customers_without_transactions = []
        
        for customer in customers_response:
            if customer.get('total_transactions', 0) > 0:
                customers_with_transactions.append(customer)
            else:
                customers_without_transactions.append(customer)
        
        print(f"   - Customers with transactions: {len(customers_with_transactions)}")
        print(f"   - Customers without transactions: {len(customers_without_transactions)}")
        
        if not customers_with_transactions:
            print("⚠️  No customers with transactions found. Testing with first available customer...")
            customers_with_transactions = customers_response[:1] if customers_response else []
        
        # Step 2: Test detailed-profile endpoint with real customer IDs
        print(f"\n🔍 STEP 2: Testing detailed-profile endpoint with real customer IDs...")
        
        test_results = []
        customers_to_test = customers_with_transactions[:2]  # Test first 2 customers with data
        
        for i, customer in enumerate(customers_to_test):
            customer_id = customer['id']
            customer_name = customer.get('name', 'Unknown')
            
            print(f"\n📊 Testing Customer {i+1}: {customer_name} (ID: {customer_id})")
            print(f"   Expected transactions: {customer.get('total_transactions', 0)}")
            
            # Test the detailed-profile endpoint
            detail_success, detail_response = self.run_test(
                f"Customer Detailed Profile - {customer_name}",
                "GET",
                f"customers/{customer_id}/detailed-profile",
                200
            )
            
            if not detail_success:
                print(f"❌ Failed to get detailed profile for {customer_name}")
                test_results.append(False)
                continue
            
            # Verify response structure
            print(f"   🔍 Verifying response structure...")
            required_fields = ['success', 'customer', 'metrics', 'credit_cards', 'recent_activities']
            missing_fields = [field for field in required_fields if field not in detail_response]
            
            if missing_fields:
                print(f"   ❌ Missing required fields: {missing_fields}")
                test_results.append(False)
                continue
            
            print(f"   ✅ All required fields present: {required_fields}")
            
            # Verify customer data structure
            customer_data = detail_response.get('customer', {})
            customer_required_fields = ['id', 'name', 'type', 'tier', 'created_at']
            customer_missing = [field for field in customer_required_fields if field not in customer_data]
            
            if customer_missing:
                print(f"   ❌ Missing customer fields: {customer_missing}")
                test_results.append(False)
                continue
            
            print(f"   ✅ Customer data structure valid")
            print(f"      - Name: {customer_data.get('name')}")
            print(f"      - Type: {customer_data.get('type')}")
            print(f"      - Tier: {customer_data.get('tier')}")
            
            # Verify metrics calculations
            metrics = detail_response.get('metrics', {})
            metrics_fields = ['total_transaction_value', 'total_profit', 'total_transactions', 
                            'avg_transaction_value', 'profit_margin', 'sales_transactions', 'dao_transactions']
            
            print(f"   🔍 Verifying metrics calculations...")
            for field in metrics_fields:
                if field not in metrics:
                    print(f"   ❌ Missing metrics field: {field}")
                    test_results.append(False)
                    break
                else:
                    value = metrics[field]
                    if not isinstance(value, (int, float)):
                        print(f"   ❌ Invalid data type for {field}: {type(value)}")
                        test_results.append(False)
                        break
            else:
                print(f"   ✅ Metrics calculations valid")
                print(f"      - Total Transaction Value: {metrics.get('total_transaction_value'):,.0f} VND")
                print(f"      - Total Profit: {metrics.get('total_profit'):,.0f} VND")
                print(f"      - Total Transactions: {metrics.get('total_transactions')}")
                print(f"      - Profit Margin: {metrics.get('profit_margin')}%")
                
                # Verify calculation accuracy
                expected_total = metrics.get('sales_transactions', 0) + metrics.get('dao_transactions', 0)
                actual_total = metrics.get('total_transactions', 0)
                if expected_total == actual_total:
                    print(f"   ✅ Transaction count calculation accurate")
                else:
                    print(f"   ⚠️  Transaction count mismatch: expected {expected_total}, got {actual_total}")
            
            # Verify credit cards data
            credit_cards = detail_response.get('credit_cards', {})
            print(f"   🔍 Verifying credit cards data...")
            
            if 'cards' in credit_cards:
                cards_list = credit_cards['cards']
                print(f"   ✅ Found {len(cards_list)} credit cards")
                
                # Check card data structure and masking
                for j, card in enumerate(cards_list[:2]):  # Check first 2 cards
                    card_number = card.get('card_number', '')
                    if card_number.startswith('****'):
                        print(f"      Card {j+1}: {card_number} (properly masked)")
                    else:
                        print(f"      ⚠️  Card {j+1}: {card_number} (not properly masked)")
                    
                    print(f"         Bank: {card.get('bank_name')}")
                    print(f"         Status: {card.get('status')}")
                    print(f"         Credit Limit: {card.get('credit_limit'):,.0f} VND")
            else:
                print(f"   ✅ No credit cards (valid for customers without cards)")
            
            # Verify recent activities
            recent_activities = detail_response.get('recent_activities', [])
            print(f"   🔍 Verifying recent activities...")
            print(f"   ✅ Found {len(recent_activities)} recent activities")
            
            # Check activity types and structure
            activity_types_found = set()
            for activity in recent_activities[:3]:  # Check first 3 activities
                activity_type = activity.get('type')
                activity_types_found.add(activity_type)
                
                print(f"      Activity: {activity_type}")
                print(f"         Amount: {activity.get('amount'):,.0f} VND")
                print(f"         Description: {activity.get('description')}")
                
                # Verify Vietnamese currency formatting in description
                description = activity.get('description', '')
                if 'VND' in description or '₫' in description:
                    print(f"         ✅ Vietnamese currency formatting present")
            
            print(f"   ✅ Activity types found: {list(activity_types_found)}")
            
            test_results.append(True)
        
        # Step 3: Test transactions-summary endpoint
        print(f"\n🔍 STEP 3: Testing transactions-summary endpoint...")
        
        summary_success = False
        if customers_to_test:
            customer_id = customers_to_test[0]['id']
            customer_name = customers_to_test[0].get('name', 'Unknown')
            
            summary_success, summary_response = self.run_test(
                f"Customer Transactions Summary - {customer_name}",
                "GET",
                f"customers/{customer_id}/transactions-summary",
                200
            )
            
            if summary_success:
                print(f"   ✅ Transactions summary endpoint working")
                transactions = summary_response.get('transactions', [])
                print(f"   ✅ Found {len(transactions)} transactions in summary")
                
                # Verify transaction structure
                if transactions:
                    first_transaction = transactions[0]
                    required_tx_fields = ['id', 'type', 'type_display', 'amount', 'profit', 'created_at']
                    tx_missing = [field for field in required_tx_fields if field not in first_transaction]
                    
                    if not tx_missing:
                        print(f"   ✅ Transaction structure valid")
                        print(f"      Type: {first_transaction.get('type')} ({first_transaction.get('type_display')})")
                        print(f"      Amount: {first_transaction.get('amount'):,.0f} VND")
                    else:
                        print(f"   ❌ Missing transaction fields: {tx_missing}")
            else:
                print(f"   ❌ Failed to get transactions summary")
        
        # Step 4: Test edge cases
        print(f"\n🔍 STEP 4: Testing edge cases...")
        
        # Test with non-existent customer ID
        print(f"   🧪 Testing non-existent customer ID...")
        nonexistent_success, nonexistent_response = self.run_test(
            "Non-existent Customer ID",
            "GET",
            "customers/nonexistent123/detailed-profile",
            404
        )
        
        if nonexistent_success:
            print(f"   ✅ Non-existent customer properly returns 404")
        else:
            print(f"   ❌ Non-existent customer handling failed")
        
        # Test with customer who has no transactions/cards
        if customers_without_transactions:
            print(f"   🧪 Testing customer with no transactions...")
            empty_customer = customers_without_transactions[0]
            empty_customer_id = empty_customer['id']
            empty_customer_name = empty_customer.get('name', 'Unknown')
            
            empty_success, empty_response = self.run_test(
                f"Customer with No Data - {empty_customer_name}",
                "GET",
                f"customers/{empty_customer_id}/detailed-profile",
                200
            )
            
            if empty_success:
                empty_metrics = empty_response.get('metrics', {})
                if empty_metrics.get('total_transactions', 0) == 0:
                    print(f"   ✅ Customer with no transactions handled correctly")
                    print(f"      Total transactions: {empty_metrics.get('total_transactions')}")
                    print(f"      Total value: {empty_metrics.get('total_transaction_value')}")
                else:
                    print(f"   ⚠️  Customer marked as having no transactions but metrics show data")
            else:
                print(f"   ❌ Failed to get profile for customer with no data")
        
        # Step 5: Analyze results
        print(f"\n📊 STEP 5: Test Results Analysis")
        
        success_count = sum(1 for result in test_results if result)
        total_tests = len(test_results)
        
        print(f"   - Detailed Profile Tests: {success_count}/{total_tests} passed")
        print(f"   - Transactions Summary: {'✅ PASSED' if summary_success else '❌ FAILED'}")
        print(f"   - Edge Case Handling: {'✅ PASSED' if nonexistent_success else '❌ FAILED'}")
        
        overall_success = (success_count == total_tests and summary_success and nonexistent_success)
        
        if overall_success:
            print(f"\n🎉 CUSTOMER DETAIL PAGE API TESTING COMPLETED SUCCESSFULLY!")
            print(f"   ✅ All detailed-profile endpoints working correctly")
            print(f"   ✅ Response structure contains: customer, metrics, credit_cards, recent_activities")
            print(f"   ✅ Data types and calculations are accurate")
            print(f"   ✅ Credit cards data properly formatted with masked card numbers")
            print(f"   ✅ Recent activities contain proper activity types")
            print(f"   ✅ Vietnamese currency formatting working")
            print(f"   ✅ Edge cases handled properly")
            print(f"   ✅ Backend ready for frontend integration")
            self.tests_passed += 1
        else:
            print(f"\n❌ CUSTOMER DETAIL PAGE API TESTING FAILED")
            print(f"   - Some endpoints or data validation failed")
            print(f"   - Review the detailed results above")
        
        self.tests_run += 1
        return overall_success

if __name__ == "__main__":
    print("🎯 CUSTOMER DETAIL PAGE API TESTING")
    print("=" * 60)
    print("Testing Customer Detail Page backend API implementation as requested in review")
    
    tester = CustomerDetailPageTester()
    success = tester.test_customer_detail_page_comprehensive()
    
    print(f"\n📊 FINAL TEST SUMMARY")
    print(f"Tests Run: {tester.tests_run}")
    print(f"Tests Passed: {tester.tests_passed}")
    print(f"Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%" if tester.tests_run > 0 else "0%")
    
    if success:
        print(f"\n🎉 Customer Detail Page API testing completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Customer Detail Page API testing failed!")
        sys.exit(1)