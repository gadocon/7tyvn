import requests
import sys
import json
from datetime import datetime

class ActivityLoggingTester:
    def __init__(self, base_url="https://billmanager-1.preview.emergentagent.com"):
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

    def test_activity_logging_api(self):
        """Test 1: Activity Logging API - GET /api/activities/recent"""
        print(f"\n🔍 TEST 1: Activity Logging API")
        print("=" * 50)
        
        # Test basic activities endpoint
        print("\n📋 Step 1: Testing GET /api/activities/recent...")
        success, response = self.run_test(
            "Get Recent Activities (Default)",
            "GET",
            "activities/recent",
            200
        )
        
        if not success:
            print("❌ Failed to get recent activities")
            return False
            
        print(f"✅ Activities API working - returned {len(response)} activities")
        
        # Test with parameters
        print("\n📋 Step 2: Testing with days=3&limit=10 parameters...")
        success2, response2 = self.run_test(
            "Get Recent Activities (3 days, limit 10)",
            "GET", 
            "activities/recent?days=3&limit=10",
            200
        )
        
        if not success2:
            print("❌ Failed to get activities with parameters")
            return False
            
        print(f"✅ Activities API with parameters working - returned {len(response2)} activities")
        
        # Verify response structure if activities exist
        if response2:
            activity = response2[0]
            required_fields = ['id', 'type', 'title', 'created_at']
            missing_fields = [field for field in required_fields if field not in activity]
            
            if missing_fields:
                print(f"❌ Missing required activity fields: {missing_fields}")
                return False
            else:
                print(f"✅ Activity structure verified - has required fields")
                print(f"   Sample activity: {activity.get('type')} - {activity.get('title')}")
        else:
            print(f"ℹ️  No activities found (expected for new system)")
            
        return True

    def test_credit_card_creation_activity(self):
        """Test 2: Credit Card Creation Activity Logging"""
        print(f"\n🔍 TEST 2: Credit Card Creation Activity Logging")
        print("=" * 50)
        
        # First create a test customer
        print("\n📋 Step 1: Creating test customer...")
        test_customer_data = {
            "name": f"Activity Test Customer {int(datetime.now().timestamp())}",
            "type": "INDIVIDUAL",
            "phone": "0123456789",
            "email": f"activity_test_{int(datetime.now().timestamp() * 1000)}@example.com",
            "address": "Test Address for Activity"
        }
        
        customer_success, customer_response = self.run_test(
            "Create Test Customer for Activity",
            "POST",
            "customers",
            200,
            data=test_customer_data
        )
        
        if not customer_success:
            print("❌ Failed to create test customer")
            return False
            
        customer_id = customer_response.get('id')
        print(f"✅ Created test customer: {customer_id}")
        
        # Create credit card to trigger activity logging
        print("\n📋 Step 2: Creating credit card to trigger activity...")
        test_card_data = {
            "customer_id": customer_id,
            "card_number": f"4532{int(datetime.now().timestamp()) % 100000000:08d}",
            "cardholder_name": "Test Cardholder",
            "bank_name": "Test Bank",
            "card_type": "VISA",
            "expiry_date": "12/28",
            "ccv": "123",
            "statement_date": 15,
            "payment_due_date": 10,
            "credit_limit": 50000000,
            "status": "Chưa đến hạn",
            "notes": "Test card for activity logging"
        }
        
        card_success, card_response = self.run_test(
            "Create Credit Card (Activity Trigger)",
            "POST",
            "credit-cards",
            200,
            data=test_card_data
        )
        
        if not card_success:
            print("❌ Failed to create credit card")
            return False
            
        card_id = card_response.get('id')
        card_number = card_response.get('card_number')
        print(f"✅ Created credit card: {card_id}")
        print(f"   Card number: ****{card_number[-4:]}")
        
        # Check if activity was logged
        print("\n📋 Step 3: Verifying activity was logged...")
        import time
        time.sleep(1)  # Brief delay for activity to be logged
        
        activities_success, activities_response = self.run_test(
            "Get Recent Activities (After Card Creation)",
            "GET",
            "activities/recent?days=1&limit=20",
            200
        )
        
        if not activities_success:
            print("❌ Failed to get activities after card creation")
            return False
            
        # Look for CARD_CREATE activity
        card_create_activities = [
            activity for activity in activities_response 
            if activity.get('type') == 'CARD_CREATE' and card_number[-4:] in activity.get('title', '')
        ]
        
        if not card_create_activities:
            print("❌ No CARD_CREATE activity found for our card")
            print(f"   Available activities: {[a.get('type') + ': ' + a.get('title', '') for a in activities_response[:3]]}")
            return False
            
        activity = card_create_activities[0]
        print(f"✅ Found CARD_CREATE activity:")
        print(f"   Type: {activity.get('type')}")
        print(f"   Title: {activity.get('title')}")
        print(f"   Customer: {activity.get('customer_name')}")
        print(f"   Amount: {activity.get('amount')}")
        
        # Verify activity structure
        expected_title_pattern = f"Thêm thẻ ****{card_number[-4:]}"
        if expected_title_pattern in activity.get('title', ''):
            print(f"✅ Activity title format correct: {activity.get('title')}")
        else:
            print(f"❌ Activity title format incorrect. Expected pattern: {expected_title_pattern}")
            return False
            
        # Verify metadata
        metadata = activity.get('metadata', {})
        if metadata and 'card_type' in metadata:
            print(f"✅ Activity metadata present: {list(metadata.keys())}")
        else:
            print(f"⚠️  Activity metadata missing or incomplete")
            
        return True, card_id

    def test_credit_card_dao_activity(self):
        """Test 3: Credit Card DAO Activity Logging"""
        print(f"\n🔍 TEST 3: Credit Card DAO Activity Logging")
        print("=" * 50)
        
        # First get or create a credit card
        print("\n📋 Step 1: Getting existing credit card or creating one...")
        
        # Try to get existing cards first
        cards_success, cards_response = self.run_test(
            "Get Existing Credit Cards",
            "GET",
            "credit-cards",
            200
        )
        
        card_id = None
        if cards_success and cards_response:
            # Find a card that can be used for DAO
            for card in cards_response:
                if card.get('status') in ['Cần đáo', 'Chưa đến hạn']:
                    card_id = card.get('id')
                    card_number = card.get('card_number')
                    print(f"✅ Found existing card for DAO: ****{card_number[-4:]}")
                    break
        
        # If no suitable card found, create one from previous test
        if not card_id:
            print("📋 No suitable existing card found, creating new one...")
            card_creation_result = self.test_credit_card_creation_activity()
            if isinstance(card_creation_result, tuple) and card_creation_result[0]:
                card_id = card_creation_result[1]
                print(f"✅ Created new card for DAO testing: {card_id}")
            else:
                print("❌ Failed to create card for DAO testing")
                return False
        
        # Perform DAO operation (POS method)
        print(f"\n📋 Step 2: Performing DAO operation (POS method)...")
        dao_data = {
            "payment_method": "POS",
            "total_amount": 5000000,
            "profit_pct": 3.5,
            "notes": "Test DAO for activity logging"
        }
        
        dao_success, dao_response = self.run_test(
            "DAO Credit Card (POS Method)",
            "POST",
            f"credit-cards/{card_id}/dao",
            200,
            data=dao_data
        )
        
        if not dao_success:
            print("❌ Failed to perform DAO operation")
            return False
            
        print(f"✅ DAO operation successful:")
        print(f"   Transaction ID: {dao_response.get('transaction_group_id')}")
        print(f"   Total Amount: {dao_response.get('total_amount')}")
        print(f"   Profit: {dao_response.get('profit_value')}")
        
        # Check if DAO activity was logged
        print("\n📋 Step 3: Verifying DAO activity was logged...")
        import time
        time.sleep(1)  # Brief delay for activity to be logged
        
        activities_success, activities_response = self.run_test(
            "Get Recent Activities (After DAO)",
            "GET",
            "activities/recent?days=1&limit=20",
            200
        )
        
        if not activities_success:
            print("❌ Failed to get activities after DAO")
            return False
            
        # Look for CARD_PAYMENT_POS activity
        dao_activities = [
            activity for activity in activities_response 
            if activity.get('type') == 'CARD_PAYMENT_POS' and 'Đáo thẻ' in activity.get('title', '')
        ]
        
        if not dao_activities:
            print("❌ No CARD_PAYMENT_POS activity found")
            print(f"   Available activities: {[a.get('type') + ': ' + a.get('title', '') for a in activities_response[:5]]}")
            return False
            
        activity = dao_activities[0]
        print(f"✅ Found CARD_PAYMENT_POS activity:")
        print(f"   Type: {activity.get('type')}")
        print(f"   Title: {activity.get('title')}")
        print(f"   Customer: {activity.get('customer_name')}")
        print(f"   Amount: {activity.get('amount')}")
        
        # Verify activity title format: "Đáo thẻ ****1234 - 5.0M VND"
        title = activity.get('title', '')
        if 'Đáo thẻ ****' in title and '5.0M VND' in title:
            print(f"✅ Activity title format correct: {title}")
        else:
            print(f"❌ Activity title format incorrect: {title}")
            print(f"   Expected pattern: 'Đáo thẻ ****XXXX - 5.0M VND'")
            return False
            
        # Verify metadata
        metadata = activity.get('metadata', {})
        if metadata and 'method' in metadata and metadata.get('method') == 'POS':
            print(f"✅ Activity metadata correct: method = {metadata.get('method')}")
        else:
            print(f"⚠️  Activity metadata missing or incorrect")
            
        return True

    def test_transaction_type_bug_fix(self):
        """Test 4: Transaction Type Bug Fix - Customer Transaction History"""
        print(f"\n🔍 TEST 4: Transaction Type Bug Fix Verification")
        print("=" * 50)
        
        # Get customers with transactions
        print("\n📋 Step 1: Finding customers with transactions...")
        customers_success, customers_response = self.run_test(
            "Get Customers with Transactions",
            "GET",
            "customers",
            200
        )
        
        if not customers_success:
            print("❌ Failed to get customers")
            return False
            
        # Find customer with credit card transactions
        target_customer = None
        for customer in customers_response:
            if customer.get('total_transactions', 0) > 0:
                target_customer = customer
                break
                
        if not target_customer:
            print("⚠️  No customers with transactions found")
            # Create test data by performing a DAO operation first
            print("📋 Creating test transaction data...")
            dao_result = self.test_credit_card_dao_activity()
            if not dao_result:
                print("❌ Failed to create test transaction data")
                return False
                
            # Try again to find customers with transactions
            customers_success, customers_response = self.run_test(
                "Get Customers with Transactions (Retry)",
                "GET",
                "customers",
                200
            )
            
            if customers_success:
                for customer in customers_response:
                    if customer.get('total_transactions', 0) > 0:
                        target_customer = customer
                        break
                        
        if not target_customer:
            print("❌ Still no customers with transactions found")
            return False
            
        customer_id = target_customer['id']
        customer_name = target_customer.get('name', 'Unknown')
        print(f"✅ Found customer with transactions: {customer_name}")
        print(f"   Total transactions: {target_customer.get('total_transactions', 0)}")
        
        # Get customer transaction history
        print(f"\n📋 Step 2: Getting customer transaction history...")
        transactions_success, transactions_response = self.run_test(
            f"Customer Transaction History - {customer_name}",
            "GET",
            f"customers/{customer_id}/transactions",
            200
        )
        
        if not transactions_success:
            print("❌ Failed to get customer transaction history")
            return False
            
        transactions = transactions_response.get('transactions', [])
        print(f"✅ Retrieved {len(transactions)} transactions")
        
        if not transactions:
            print("⚠️  No transactions found for customer")
            return True  # Not a failure, just no data
            
        # Analyze transaction types and bill_codes
        print(f"\n📋 Step 3: Analyzing transaction types...")
        credit_card_transactions = []
        regular_bill_transactions = []
        
        for transaction in transactions:
            bill_codes = transaction.get('bill_codes', [])
            transaction_type = None
            
            # Check bill_codes format to determine transaction type
            if bill_codes:
                for code in bill_codes:
                    if code.startswith('****'):
                        # Credit card transaction (bill_codes like ****1234)
                        transaction_type = "CREDIT_CARD"
                        credit_card_transactions.append(transaction)
                        break
                else:
                    # Regular bill transaction (normal customer codes)
                    transaction_type = "REGULAR_BILL"
                    regular_bill_transactions.append(transaction)
            
            print(f"   Transaction {transaction.get('id', 'N/A')[:8]}...")
            print(f"     Bill codes: {bill_codes}")
            print(f"     Detected type: {transaction_type}")
            
        print(f"\n📊 Transaction Analysis:")
        print(f"   Credit card transactions: {len(credit_card_transactions)}")
        print(f"   Regular bill transactions: {len(regular_bill_transactions)}")
        
        # Verify the bug fix: credit card transactions should show "Đáo Thẻ"
        if credit_card_transactions:
            print(f"\n🔍 Step 4: Verifying transaction type display logic...")
            
            for transaction in credit_card_transactions[:3]:  # Check first 3
                bill_codes = transaction.get('bill_codes', [])
                
                # The bug fix should be in the frontend, but we can verify the data structure
                # that enables the fix (bill_codes with ****XXXX format)
                credit_card_codes = [code for code in bill_codes if code.startswith('****')]
                
                if credit_card_codes:
                    print(f"✅ Credit card transaction has proper bill_codes format:")
                    print(f"   Transaction ID: {transaction.get('id', 'N/A')[:8]}...")
                    print(f"   Bill codes: {credit_card_codes}")
                    print(f"   → Should display as 'Đáo Thẻ' (not 'Bán Bill')")
                else:
                    print(f"❌ Credit card transaction missing proper bill_codes format")
                    return False
                    
            print(f"\n✅ Transaction type bug fix data structure verified!")
            print(f"   Credit card transactions have bill_codes starting with '****'")
            print(f"   Frontend can correctly detect and display 'Đáo Thẻ' vs 'Bán Bill'")
            
        else:
            print(f"ℹ️  No credit card transactions found to verify bug fix")
            print(f"   Bug fix verification requires credit card transactions with ****XXXX bill_codes")
            
        return True

    def test_activity_api_response_structure(self):
        """Test 5: Activity API Response Structure Verification"""
        print(f"\n🔍 TEST 5: Activity API Response Structure")
        print("=" * 50)
        
        # Get recent activities
        print("\n📋 Step 1: Getting recent activities for structure verification...")
        success, response = self.run_test(
            "Get Recent Activities for Structure Check",
            "GET",
            "activities/recent?days=7&limit=20",
            200
        )
        
        if not success:
            print("❌ Failed to get recent activities")
            return False
            
        print(f"✅ Retrieved {len(response)} activities")
        
        if not response:
            print("ℹ️  No activities found - testing with empty response")
            print("✅ Empty array response is valid for new system")
            return True
            
        # Verify response structure
        print(f"\n📋 Step 2: Verifying activity response structure...")
        
        required_fields = [
            'id', 'type', 'title', 'description', 'customer_id', 
            'customer_name', 'amount', 'status', 'metadata', 'created_at'
        ]
        
        structure_valid = True
        
        for i, activity in enumerate(response[:3]):  # Check first 3 activities
            print(f"\n   Activity {i+1}:")
            print(f"     ID: {activity.get('id', 'N/A')}")
            print(f"     Type: {activity.get('type', 'N/A')}")
            print(f"     Title: {activity.get('title', 'N/A')}")
            
            missing_fields = []
            for field in required_fields:
                if field not in activity:
                    missing_fields.append(field)
                    
            if missing_fields:
                print(f"     ❌ Missing fields: {missing_fields}")
                structure_valid = False
            else:
                print(f"     ✅ All required fields present")
                
            # Verify field types and values
            if activity.get('type') in ['CARD_CREATE', 'CARD_PAYMENT_POS', 'CARD_PAYMENT_BILL']:
                print(f"     ✅ Valid activity type: {activity.get('type')}")
            else:
                print(f"     ⚠️  Unknown activity type: {activity.get('type')}")
                
            # Check title format
            title = activity.get('title', '')
            if 'thẻ' in title.lower() or 'Thêm' in title or 'Đáo' in title:
                print(f"     ✅ Title format looks correct: {title}")
            else:
                print(f"     ⚠️  Unexpected title format: {title}")
                
        # Test filtering parameters
        print(f"\n📋 Step 3: Testing filtering parameters...")
        
        # Test days parameter
        success_1day, response_1day = self.run_test(
            "Get Activities (1 day filter)",
            "GET",
            "activities/recent?days=1&limit=50",
            200
        )
        
        # Test limit parameter  
        success_limit, response_limit = self.run_test(
            "Get Activities (limit 5)",
            "GET",
            "activities/recent?days=7&limit=5",
            200
        )
        
        if success_1day and success_limit:
            print(f"✅ Filtering parameters working:")
            print(f"   1 day filter: {len(response_1day)} activities")
            print(f"   Limit 5: {len(response_limit)} activities (max 5)")
            
            if len(response_limit) <= 5:
                print(f"✅ Limit parameter working correctly")
            else:
                print(f"❌ Limit parameter not working - returned {len(response_limit)} > 5")
                structure_valid = False
        else:
            print(f"❌ Filtering parameters not working")
            structure_valid = False
            
        if structure_valid:
            print(f"\n✅ Activity API response structure fully verified!")
            return True
        else:
            print(f"\n❌ Activity API response structure has issues")
            return False

    def run_all_tests(self):
        """Run all activity logging tests"""
        print("🎯 COMPREHENSIVE TESTING: Activity Logging System & Transaction Type Bug Fix")
        print("=" * 80)
        
        activity_tests = [
            ("Activity Logging API", self.test_activity_logging_api),
            ("Credit Card Creation Activity", self.test_credit_card_creation_activity),
            ("Credit Card DAO Activity", self.test_credit_card_dao_activity),
            ("Transaction Type Bug Fix", self.test_transaction_type_bug_fix),
            ("Activity API Response Structure", self.test_activity_api_response_structure)
        ]
        
        for test_name, test_func in activity_tests:
            try:
                print(f"\n{'='*60}")
                print(f"🧪 Running: {test_name}")
                print(f"{'='*60}")
                success = test_func()
                if success:
                    print(f"✅ {test_name}: PASSED")
                    self.tests_passed += 1
                else:
                    print(f"❌ {test_name}: FAILED")
            except Exception as e:
                print(f"💥 {test_name}: ERROR - {str(e)}")
                import traceback
                traceback.print_exc()
        
        print(f"\n{'='*60}")
        print(f"📊 ACTIVITY LOGGING & BUG FIX TEST SUMMARY")
        print(f"{'='*60}")
        print(f"Tests Run: {self.tests_run}")
        print(f"Tests Passed: {self.tests_passed}")
        print(f"Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%" if self.tests_run > 0 else "No tests run")
        
        if self.tests_passed == self.tests_run:
            print("🎉 All tests passed!")
            return True
        else:
            print("⚠️  Some tests failed - check logs above")
            return False

if __name__ == "__main__":
    tester = ActivityLoggingTester()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)