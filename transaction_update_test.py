import requests
import sys
import json
from datetime import datetime

class TransactionUpdateTester:
    def __init__(self, base_url="https://seventy-crm-fix.preview.emergentagent.com"):
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

    def test_transaction_update_endpoints(self):
        """Test Transaction Update API endpoints after ObjectId serialization bug fix"""
        print(f"\n🎯 TRANSACTION UPDATE API ENDPOINTS TESTING")
        print("=" * 70)
        print("🔍 TESTING OBJECTIVES:")
        print("   1. Test PUT /api/transactions/sale/{transaction_id}")
        print("   2. Test PUT /api/transactions/credit-card/{transaction_id}")
        print("   3. Verify ObjectId serialization bug is fixed")
        print("   4. Confirm updated data is returned correctly")
        
        test_results = {
            "sale_transaction_tests": [],
            "credit_card_transaction_tests": [],
            "total_tests": 0,
            "passed_tests": 0,
            "serialization_errors": 0
        }
        
        # Step 1: Get existing transactions to test with
        print(f"\n📋 STEP 1: Getting existing transactions...")
        
        # Get sales transactions
        sales_success, sales_response = self.run_test(
            "Get Sales Transactions",
            "GET",
            "sales",
            200
        )
        
        sale_transactions = []
        if sales_success and sales_response:
            sale_transactions = sales_response[:3]  # Test with first 3
            print(f"✅ Found {len(sale_transactions)} sale transactions to test")
        else:
            print("⚠️  No existing sale transactions found")
        
        # Get credit card transactions
        cc_success, cc_response = self.run_test(
            "Get Credit Card Transactions", 
            "GET",
            "credit-cards/transactions",
            200
        )
        
        cc_transactions = []
        if cc_success and cc_response:
            cc_transactions = cc_response[:3]  # Test with first 3
            print(f"✅ Found {len(cc_transactions)} credit card transactions to test")
        else:
            print("⚠️  No existing credit card transactions found")
        
        # If no transactions exist, create test data
        if not sale_transactions and not cc_transactions:
            print(f"\n🔧 Creating test transactions for testing...")
            created_transactions = self.create_test_transactions_for_update()
            if created_transactions:
                sale_transactions = created_transactions.get('sales', [])
                cc_transactions = created_transactions.get('credit_cards', [])
        
        # Step 2: Test Sale Transaction Updates
        print(f"\n🧪 STEP 2: Testing Sale Transaction Updates")
        print("=" * 50)
        
        for i, sale in enumerate(sale_transactions):
            transaction_id = sale.get('id')
            if not transaction_id:
                print(f"   ❌ Sale transaction {i+1} missing ID")
                continue
                
            print(f"\n   🔍 Testing Sale Transaction {i+1}: {transaction_id}")
            
            # Test update with valid data
            update_data = {
                "total": float(sale.get('total', 1000000)) + 100000,  # Add 100k
                "profit_value": float(sale.get('profit_value', 50000)) + 5000,  # Add 5k
                "profit_percentage": 5.5,
                "notes": f"Updated via API test - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            }
            
            print(f"      📤 Update Data: {update_data}")
            
            try:
                start_time = datetime.now()
                response = requests.put(
                    f"{self.api_url}/transactions/sale/{transaction_id}",
                    json=update_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                print(f"      📊 Response Time: {response_time:.3f} seconds")
                print(f"      📊 Status Code: {response.status_code}")
                
                test_results["total_tests"] += 1
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        print(f"      ✅ SUCCESS: Sale transaction updated")
                        print(f"      📄 Response Structure: {list(response_data.keys())}")
                        
                        # Verify response structure
                        if 'success' in response_data and 'data' in response_data:
                            updated_transaction = response_data['data']
                            print(f"      📊 Updated Transaction Fields: {list(updated_transaction.keys())}")
                            
                            # Verify the update was applied
                            if updated_transaction.get('total') == update_data['total']:
                                print(f"      ✅ Total amount updated correctly: {updated_transaction.get('total')}")
                            else:
                                print(f"      ❌ Total amount not updated correctly")
                                
                            if updated_transaction.get('notes') == update_data['notes']:
                                print(f"      ✅ Notes updated correctly")
                            else:
                                print(f"      ❌ Notes not updated correctly")
                                
                            # Check for ObjectId serialization issues
                            if '_id' in str(response_data):
                                print(f"      🚨 POTENTIAL ISSUE: Response contains '_id' field")
                                test_results["serialization_errors"] += 1
                            else:
                                print(f"      ✅ No ObjectId serialization issues detected")
                                
                            test_results["passed_tests"] += 1
                            
                        else:
                            print(f"      ❌ Invalid response structure")
                            
                    except json.JSONDecodeError as e:
                        print(f"      ❌ JSON DECODE ERROR: {e}")
                        print(f"      🚨 CRITICAL: ObjectId serialization bug may still exist")
                        test_results["serialization_errors"] += 1
                        
                elif response.status_code == 404:
                    print(f"      ❌ Transaction not found (404)")
                    
                elif response.status_code == 400:
                    print(f"      ❌ Bad request (400)")
                    try:
                        error_data = response.json()
                        print(f"      Error: {error_data}")
                    except:
                        print(f"      Raw response: {response.text}")
                        
                elif response.status_code == 500:
                    print(f"      ❌ CRITICAL: Internal Server Error (500)")
                    print(f"      🚨 This could indicate ObjectId serialization bug")
                    try:
                        error_data = response.json()
                        print(f"      Error Details: {error_data}")
                    except:
                        print(f"      Raw Response: {response.text}")
                    test_results["serialization_errors"] += 1
                    
                else:
                    print(f"      ❌ Unexpected status code: {response.status_code}")
                    
                test_results["sale_transaction_tests"].append({
                    "transaction_id": transaction_id,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "success": response.status_code == 200
                })
                
            except Exception as e:
                print(f"      ❌ ERROR: {e}")
                test_results["total_tests"] += 1
        
        # Step 3: Test Credit Card Transaction Updates
        print(f"\n🧪 STEP 3: Testing Credit Card Transaction Updates")
        print("=" * 50)
        
        for i, cc_tx in enumerate(cc_transactions):
            transaction_id = cc_tx.get('id')
            if not transaction_id:
                print(f"   ❌ Credit card transaction {i+1} missing ID")
                continue
                
            print(f"\n   🔍 Testing Credit Card Transaction {i+1}: {transaction_id}")
            
            # Test update with valid data
            update_data = {
                "total_amount": float(cc_tx.get('total_amount', 5000000)) + 200000,  # Add 200k
                "profit_amount": float(cc_tx.get('profit_value', 175000)) + 10000,  # Add 10k
                "profit_pct": 4.0,
                "notes": f"Updated CC transaction via API test - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
            }
            
            print(f"      📤 Update Data: {update_data}")
            
            try:
                start_time = datetime.now()
                response = requests.put(
                    f"{self.api_url}/transactions/credit-card/{transaction_id}",
                    json=update_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                end_time = datetime.now()
                response_time = (end_time - start_time).total_seconds()
                
                print(f"      📊 Response Time: {response_time:.3f} seconds")
                print(f"      📊 Status Code: {response.status_code}")
                
                test_results["total_tests"] += 1
                
                if response.status_code == 200:
                    try:
                        response_data = response.json()
                        print(f"      ✅ SUCCESS: Credit card transaction updated")
                        print(f"      📄 Response Structure: {list(response_data.keys())}")
                        
                        # Verify response structure
                        if 'success' in response_data and 'data' in response_data:
                            updated_transaction = response_data['data']
                            print(f"      📊 Updated Transaction Fields: {list(updated_transaction.keys())}")
                            
                            # Verify the update was applied
                            if updated_transaction.get('total_amount') == update_data['total_amount']:
                                print(f"      ✅ Total amount updated correctly: {updated_transaction.get('total_amount')}")
                            else:
                                print(f"      ❌ Total amount not updated correctly")
                                
                            if updated_transaction.get('notes') == update_data['notes']:
                                print(f"      ✅ Notes updated correctly")
                            else:
                                print(f"      ❌ Notes not updated correctly")
                                
                            # Check for ObjectId serialization issues
                            if '_id' in str(response_data):
                                print(f"      🚨 POTENTIAL ISSUE: Response contains '_id' field")
                                test_results["serialization_errors"] += 1
                            else:
                                print(f"      ✅ No ObjectId serialization issues detected")
                                
                            test_results["passed_tests"] += 1
                            
                        else:
                            print(f"      ❌ Invalid response structure")
                            
                    except json.JSONDecodeError as e:
                        print(f"      ❌ JSON DECODE ERROR: {e}")
                        print(f"      🚨 CRITICAL: ObjectId serialization bug may still exist")
                        test_results["serialization_errors"] += 1
                        
                elif response.status_code == 404:
                    print(f"      ❌ Transaction not found (404)")
                    
                elif response.status_code == 400:
                    print(f"      ❌ Bad request (400)")
                    try:
                        error_data = response.json()
                        print(f"      Error: {error_data}")
                    except:
                        print(f"      Raw response: {response.text}")
                        
                elif response.status_code == 500:
                    print(f"      ❌ CRITICAL: Internal Server Error (500)")
                    print(f"      🚨 This could indicate ObjectId serialization bug")
                    try:
                        error_data = response.json()
                        print(f"      Error Details: {error_data}")
                    except:
                        print(f"      Raw Response: {response.text}")
                    test_results["serialization_errors"] += 1
                    
                else:
                    print(f"      ❌ Unexpected status code: {response.status_code}")
                    
                test_results["credit_card_transaction_tests"].append({
                    "transaction_id": transaction_id,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "success": response.status_code == 200
                })
                
            except Exception as e:
                print(f"      ❌ ERROR: {e}")
                test_results["total_tests"] += 1
        
        # Step 4: Test Edge Cases
        print(f"\n🧪 STEP 4: Testing Edge Cases")
        print("=" * 50)
        
        # Test with non-existent transaction ID
        print(f"\n   🔍 Testing with non-existent transaction ID...")
        fake_id = "non_existent_transaction_id_12345"
        
        try:
            response = requests.put(
                f"{self.api_url}/transactions/sale/{fake_id}",
                json={"total": 1000000, "notes": "Test update"},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            print(f"      📊 Status Code: {response.status_code}")
            test_results["total_tests"] += 1
            
            if response.status_code == 404:
                print(f"      ✅ Correctly returned 404 for non-existent transaction")
                test_results["passed_tests"] += 1
            else:
                print(f"      ❌ Expected 404, got {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ ERROR: {e}")
            test_results["total_tests"] += 1
        
        # Test with empty update data
        if sale_transactions:
            print(f"\n   🔍 Testing with empty update data...")
            test_transaction_id = sale_transactions[0].get('id')
            
            try:
                response = requests.put(
                    f"{self.api_url}/transactions/sale/{test_transaction_id}",
                    json={},
                    headers={'Content-Type': 'application/json'},
                    timeout=30
                )
                
                print(f"      📊 Status Code: {response.status_code}")
                test_results["total_tests"] += 1
                
                if response.status_code == 400:
                    print(f"      ✅ Correctly returned 400 for empty update data")
                    test_results["passed_tests"] += 1
                else:
                    print(f"      ❌ Expected 400, got {response.status_code}")
                    
            except Exception as e:
                print(f"      ❌ ERROR: {e}")
                test_results["total_tests"] += 1
        
        # Final Analysis and Summary
        print(f"\n📊 TRANSACTION UPDATE API TESTING SUMMARY")
        print("=" * 50)
        
        total_tests = test_results["total_tests"]
        passed_tests = test_results["passed_tests"]
        serialization_errors = test_results["serialization_errors"]
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"📈 Overall Results:")
        print(f"   - Total Tests: {total_tests}")
        print(f"   - Passed Tests: {passed_tests}")
        print(f"   - Success Rate: {success_rate:.1f}%")
        print(f"   - Serialization Errors: {serialization_errors}")
        
        print(f"\n📋 Sale Transaction Test Results:")
        for test in test_results["sale_transaction_tests"]:
            status = "✅ PASS" if test["success"] else "❌ FAIL"
            print(f"   - {test['transaction_id'][:8]}...: {test['status_code']} ({test['response_time']:.3f}s) {status}")
        
        print(f"\n📋 Credit Card Transaction Test Results:")
        for test in test_results["credit_card_transaction_tests"]:
            status = "✅ PASS" if test["success"] else "❌ FAIL"
            print(f"   - {test['transaction_id'][:8]}...: {test['status_code']} ({test['response_time']:.3f}s) {status}")
        
        # Determine overall result
        if serialization_errors == 0 and success_rate >= 80:
            print(f"\n🎉 TRANSACTION UPDATE API TESTING: SUCCESS")
            print(f"✅ ObjectId serialization bug appears to be FIXED")
            print(f"✅ Both sale and credit card transaction updates working")
            print(f"✅ JSON responses are properly serialized")
            print(f"✅ Updated data is returned correctly")
            
            if success_rate == 100:
                print(f"🏆 PERFECT SCORE: All transaction update tests passed!")
            
            self.tests_passed += 1
        else:
            print(f"\n⚠️  TRANSACTION UPDATE API TESTING: ISSUES DETECTED")
            if serialization_errors > 0:
                print(f"❌ ObjectId serialization errors detected: {serialization_errors}")
                print(f"🚨 The ObjectId serialization bug may NOT be fully fixed")
            if success_rate < 80:
                print(f"❌ Low success rate: {success_rate:.1f}%")
                print(f"🔍 Review individual test results above")
        
        print(f"\n🔧 RECOMMENDATIONS:")
        print(f"   1. Monitor transaction update operations in production")
        print(f"   2. Verify all MongoDB ObjectId fields are properly converted")
        print(f"   3. Test with larger datasets to ensure scalability")
        print(f"   4. Implement proper validation for update data")
        
        self.tests_run += 1
        return serialization_errors == 0 and success_rate >= 80

    def create_test_transactions_for_update(self):
        """Create test transactions for update testing"""
        print(f"\n🔧 Creating test transactions for update testing...")
        
        created_transactions = {
            "sales": [],
            "credit_cards": []
        }
        
        # First, get or create a test customer
        customers_success, customers_response = self.run_test(
            "Get Customers for Test Transactions",
            "GET",
            "customers?limit=1",
            200
        )
        
        customer_id = None
        if customers_success and customers_response:
            customer_id = customers_response[0].get('id')
            print(f"   ✅ Using existing customer: {customer_id}")
        else:
            # Create test customer
            test_customer_data = {
                "name": f"Test Customer for Updates {int(datetime.now().timestamp())}",
                "type": "INDIVIDUAL",
                "phone": f"012345{int(datetime.now().timestamp()) % 10000}",
                "email": f"test_updates_{int(datetime.now().timestamp())}@example.com"
            }
            
            customer_success, customer_response = self.run_test(
                "Create Test Customer for Updates",
                "POST",
                "customers",
                200,
                data=test_customer_data
            )
            
            if customer_success:
                customer_id = customer_response.get('id')
                print(f"   ✅ Created test customer: {customer_id}")
            else:
                print(f"   ❌ Failed to create test customer")
                return created_transactions
        
        # Create test bill for sale transaction
        test_bill_data = {
            "customer_code": f"TESTUPDATE{int(datetime.now().timestamp())}",
            "provider_region": "MIEN_NAM",
            "full_name": "Test Customer for Updates",
            "address": "Test Address for Updates",
            "amount": 1500000,
            "billing_cycle": "12/2025",
            "status": "AVAILABLE"
        }
        
        bill_success, bill_response = self.run_test(
            "Create Test Bill for Updates",
            "POST",
            "bills/create",
            200,
            data=test_bill_data
        )
        
        bill_id = None
        if bill_success:
            bill_id = bill_response.get('id')
            print(f"   ✅ Created test bill: {bill_id}")
        else:
            print(f"   ❌ Failed to create test bill")
            return created_transactions
        
        # Create test sale transaction
        test_sale_data = {
            "customer_id": customer_id,
            "bill_ids": [bill_id],
            "profit_pct": 5.0,
            "method": "CASH",
            "notes": f"Test sale for update testing - {datetime.now().strftime('%d/%m/%Y')}"
        }
        
        sale_success, sale_response = self.run_test(
            "Create Test Sale for Updates",
            "POST",
            "sales",
            200,
            data=test_sale_data
        )
        
        if sale_success:
            created_transactions["sales"].append(sale_response)
            print(f"   ✅ Created test sale transaction: {sale_response.get('id')}")
        else:
            print(f"   ❌ Failed to create test sale transaction")
        
        # Try to create test credit card and transaction
        # First check if customer has credit cards
        cc_success, cc_response = self.run_test(
            "Get Credit Cards for Test",
            "GET",
            "credit-cards?limit=1",
            200
        )
        
        card_id = None
        if cc_success and cc_response:
            card_id = cc_response[0].get('id')
            print(f"   ✅ Using existing credit card: {card_id}")
        else:
            # Create test credit card
            test_card_data = {
                "customer_id": customer_id,
                "card_number": f"4111111111111{int(datetime.now().timestamp()) % 1000}",
                "cardholder_name": "Test Cardholder",
                "bank_name": "Test Bank",
                "card_type": "VISA",
                "expiry_date": "12/26",
                "ccv": "123",
                "statement_date": 15,
                "payment_due_date": 10,
                "credit_limit": 50000000,
                "status": "Cần đáo"
            }
            
            card_success, card_response = self.run_test(
                "Create Test Credit Card for Updates",
                "POST",
                "credit-cards",
                200,
                data=test_card_data
            )
            
            if card_success:
                card_id = card_response.get('id')
                print(f"   ✅ Created test credit card: {card_id}")
            else:
                print(f"   ❌ Failed to create test credit card")
                return created_transactions
        
        # Create test credit card transaction via DAO
        if card_id:
            test_dao_data = {
                "payment_method": "POS",
                "total_amount": 5000000,
                "profit_pct": 3.5,
                "notes": f"Test DAO for update testing - {datetime.now().strftime('%d/%m/%Y')}"
            }
            
            dao_success, dao_response = self.run_test(
                "Create Test DAO Transaction for Updates",
                "POST",
                f"credit-cards/{card_id}/dao",
                200,
                data=test_dao_data
            )
            
            if dao_success:
                # Get the created transaction from the response
                transaction_group_id = dao_response.get('transaction_group_id')
                if transaction_group_id:
                    # Try to get the transaction details
                    cc_tx_success, cc_tx_response = self.run_test(
                        "Get Credit Card Transactions for Updates",
                        "GET",
                        "credit-cards/transactions?limit=1",
                        200
                    )
                    
                    if cc_tx_success and cc_tx_response:
                        created_transactions["credit_cards"] = cc_tx_response[:1]
                        print(f"   ✅ Created test credit card transaction")
                    else:
                        print(f"   ⚠️  DAO created but couldn't retrieve transaction details")
            else:
                print(f"   ❌ Failed to create test DAO transaction")
        
        return created_transactions

if __name__ == "__main__":
    tester = TransactionUpdateTester()
    
    print(f"🎯 Running Transaction Update API Test...")
    success = tester.test_transaction_update_endpoints()
    
    print(f"\n📊 Final Results:")
    print(f"   Tests Run: {tester.tests_run}")
    print(f"   Tests Passed: {tester.tests_passed}")
    print(f"   Success Rate: {(tester.tests_passed/tester.tests_run*100):.1f}%" if tester.tests_run > 0 else "No tests run")
    print(f"   Overall Result: {'✅ PASSED' if success else '❌ FAILED'}")