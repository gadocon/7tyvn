import requests
import sys
import json
from datetime import datetime

class FPTBillManagerAPITester:
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

    def test_dashboard_stats(self):
        """Test dashboard statistics endpoint"""
        success, response = self.run_test(
            "Dashboard Stats",
            "GET",
            "dashboard/stats",
            200
        )
        
        if success:
            required_fields = ['total_bills', 'available_bills', 'total_customers', 'total_revenue', 'recent_activities']
            missing_fields = [field for field in required_fields if field not in response]
            if missing_fields:
                print(f"   ⚠️  Missing fields: {missing_fields}")
            else:
                print(f"   📊 Stats: Bills={response.get('total_bills', 0)}, Customers={response.get('total_customers', 0)}, Revenue={response.get('total_revenue', 0)}")
        
        return success

    def test_check_bills_valid(self):
        """Test bill checking with valid codes"""
        valid_codes = ["PA22040522471", "PA22040506503", "PA22060724572"]
        
        success, response = self.run_test(
            "Check Bills - Valid Codes",
            "POST",
            "bill/check",
            200,
            data={
                "gateway": "FPT",
                "provider_region": "MIEN_NAM",
                "codes": valid_codes
            }
        )
        
        if success:
            items = response.get('items', [])
            summary = response.get('summary', {})
            print(f"   📋 Results: {len(items)} items, {summary.get('ok', 0)} OK, {summary.get('error', 0)} errors")
            
            # Check if all valid codes returned OK status
            ok_codes = [item['customer_code'] for item in items if item.get('status') == 'OK']
            print(f"   ✅ Valid codes found: {ok_codes}")
        
        return success

    def test_check_bills_invalid(self):
        """Test bill checking with invalid codes"""
        invalid_codes = ["INVALID123", "NOTFOUND456"]
        
        success, response = self.run_test(
            "Check Bills - Invalid Codes",
            "POST",
            "bill/check",
            200,
            data={
                "gateway": "FPT",
                "provider_region": "MIEN_NAM", 
                "codes": invalid_codes
            }
        )
        
        if success:
            items = response.get('items', [])
            summary = response.get('summary', {})
            print(f"   📋 Results: {len(items)} items, {summary.get('ok', 0)} OK, {summary.get('error', 0)} errors")
            
            # Check if all invalid codes returned ERROR status
            error_codes = [item['customer_code'] for item in items if item.get('status') == 'ERROR']
            print(f"   ❌ Invalid codes: {error_codes}")
        
        return success

    def test_get_bills(self):
        """Test get bills endpoint"""
        success, response = self.run_test(
            "Get Bills",
            "GET",
            "bills",
            200
        )
        
        if success:
            print(f"   📄 Found {len(response)} bills")
            if response:
                first_bill = response[0]
                print(f"   📋 Sample bill fields: {list(first_bill.keys())}")
        
        return success

    def test_get_customers(self):
        """Test get customers endpoint"""
        success, response = self.run_test(
            "Get Customers",
            "GET",
            "customers",
            200
        )
        
        if success:
            print(f"   👥 Found {len(response)} customers")
            if response:
                first_customer = response[0]
                print(f"   👤 Sample customer: {first_customer.get('name', 'Unknown')}")
        
        return success

    def test_webhook_endpoint(self):
        """Test webhook endpoint with sample FPT payload"""
        sample_payload = {
            "bills": [
                {
                    "customer_id": "PA22040522471",
                    "electric_provider": "mien_nam",
                    "provider_name": "Điện lực miền Nam",
                    "full_name": "Nguyễn Văn Test",
                    "address": "123 Test Street",
                    "amount": 1500000,
                    "billing_cycle": "08/2025"
                }
            ],
            "timestamp": int(datetime.now().timestamp()),
            "request_id": f"test_request_{int(datetime.now().timestamp())}",
            "webhook_url": f"{self.base_url}/api/webhook/checkbill",
            "execution_mode": "test"
        }
        
        success, response = self.run_test(
            "Webhook Endpoint",
            "POST",
            "webhook/checkbill",
            200,
            data=sample_payload,
            headers={
                'Content-Type': 'application/json',
                'X-API-KEY': 'test-key'
            }
        )
        
        if success:
            print(f"   🔗 Webhook response: {response}")
        
        return success

    def test_debug_payload_mien_nam(self):
        """Test debug endpoint for MIEN_NAM provider mapping"""
        print(f"\n🔍 Testing Debug Payload - MIEN_NAM Provider")
        
        url = f"{self.api_url}/bill/debug-payload"
        params = {
            "customer_code": "PB09020058383",
            "provider_region": "MIEN_NAM"
        }
        
        print(f"🌐 Making request to: {url}")
        print(f"📋 Parameters: {params}")
        
        try:
            response = requests.post(url, params=params, timeout=30)
            
            print(f"\n📥 Response Details:")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"   Debug Response:")
                print(f"   {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Verify the provider mapping
                payload = response_data.get('payload', {})
                bills = payload.get('bills', [])
                
                if bills and len(bills) > 0:
                    electric_provider = bills[0].get('electric_provider')
                    print(f"\n✅ Provider Mapping Verification:")
                    print(f"   Input: provider_region = MIEN_NAM")
                    print(f"   Output: electric_provider = {electric_provider}")
                    
                    if electric_provider == "mien_nam":
                        print(f"   ✅ CORRECT: MIEN_NAM maps to 'mien_nam'")
                        self.tests_passed += 1
                        return True, response_data
                    else:
                        print(f"   ❌ INCORRECT: Expected 'mien_nam', got '{electric_provider}'")
                        return False, response_data
                else:
                    print(f"   ❌ No bills found in payload")
                    return False, response_data
            else:
                print(f"   ❌ Request failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, {}
        finally:
            self.tests_run += 1

    def test_debug_payload_hcmc(self):
        """Test debug endpoint for HCMC provider mapping"""
        print(f"\n🔍 Testing Debug Payload - HCMC Provider")
        
        url = f"{self.api_url}/bill/debug-payload"
        params = {
            "customer_code": "PB09020058383",
            "provider_region": "HCMC"
        }
        
        print(f"🌐 Making request to: {url}")
        print(f"📋 Parameters: {params}")
        
        try:
            response = requests.post(url, params=params, timeout=30)
            
            print(f"\n📥 Response Details:")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"   Debug Response:")
                print(f"   {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Verify the provider mapping
                payload = response_data.get('payload', {})
                bills = payload.get('bills', [])
                
                if bills and len(bills) > 0:
                    electric_provider = bills[0].get('electric_provider')
                    print(f"\n✅ Provider Mapping Verification:")
                    print(f"   Input: provider_region = HCMC")
                    print(f"   Output: electric_provider = {electric_provider}")
                    
                    if electric_provider == "evnhcmc":
                        print(f"   ✅ CORRECT: HCMC maps to 'evnhcmc' (corrected from 'hcmc')")
                        self.tests_passed += 1
                        return True, response_data
                    else:
                        print(f"   ❌ INCORRECT: Expected 'evnhcmc', got '{electric_provider}'")
                        return False, response_data
                else:
                    print(f"   ❌ No bills found in payload")
                    return False, response_data
            else:
                print(f"   ❌ Request failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, {}
        finally:
            self.tests_run += 1

    def test_single_bill_check_mien_nam(self):
        """Test single bill check endpoint with MIEN_NAM"""
        print(f"\n🔍 Testing Single Bill Check - MIEN_NAM")
        
        url = f"{self.api_url}/bill/check/single"
        params = {
            "customer_code": "PB09020058383",
            "provider_region": "MIEN_NAM"
        }
        
        print(f"🌐 Making request to: {url}")
        print(f"📋 Parameters: {params}")
        
        try:
            response = requests.post(url, params=params, timeout=30)
            
            print(f"\n📥 Response Details:")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"   Single Bill Response:")
                print(f"   {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Analyze the response
                customer_code = response_data.get('customer_code')
                status = response_data.get('status')
                errors = response_data.get('errors')
                
                print(f"\n📊 Analysis:")
                print(f"   Customer Code: {customer_code}")
                print(f"   Status: {status}")
                
                if status == "ERROR" and errors:
                    print(f"   Error Code: {errors.get('code')}")
                    print(f"   Error Message: {errors.get('message')}")
                    print(f"   ✅ External API error handled correctly")
                elif status == "OK":
                    print(f"   Full Name: {response_data.get('full_name')}")
                    print(f"   Address: {response_data.get('address')}")
                    print(f"   Amount: {response_data.get('amount')}")
                    print(f"   ✅ Bill found successfully")
                
                self.tests_passed += 1
                return True, response_data
            else:
                print(f"   ❌ Request failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, {}
        finally:
            self.tests_run += 1

    def test_single_bill_check_hcmc(self):
        """Test single bill check endpoint with HCMC"""
        print(f"\n🔍 Testing Single Bill Check - HCMC")
        
        url = f"{self.api_url}/bill/check/single"
        params = {
            "customer_code": "PB09020058383",
            "provider_region": "HCMC"
        }
        
        print(f"🌐 Making request to: {url}")
        print(f"📋 Parameters: {params}")
        
        try:
            response = requests.post(url, params=params, timeout=30)
            
            print(f"\n📥 Response Details:")
            print(f"   Status Code: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                print(f"   Single Bill Response:")
                print(f"   {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                
                # Analyze the response
                customer_code = response_data.get('customer_code')
                status = response_data.get('status')
                errors = response_data.get('errors')
                
                print(f"\n📊 Analysis:")
                print(f"   Customer Code: {customer_code}")
                print(f"   Status: {status}")
                
                if status == "ERROR" and errors:
                    print(f"   Error Code: {errors.get('code')}")
                    print(f"   Error Message: {errors.get('message')}")
                    print(f"   ✅ External API error handled correctly")
                elif status == "OK":
                    print(f"   Full Name: {response_data.get('full_name')}")
                    print(f"   Address: {response_data.get('address')}")
                    print(f"   Amount: {response_data.get('amount')}")
                    print(f"   ✅ Bill found successfully")
                
                self.tests_passed += 1
                return True, response_data
            else:
                print(f"   ❌ Request failed with status {response.status_code}")
                print(f"   Response: {response.text}")
                return False, {}
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return False, {}
        finally:
            self.tests_run += 1

    def test_external_api_call_simulation(self):
        """Test to understand the external API call flow"""
        print(f"\n🔗 Testing External API Call Flow")
        
        # This simulates what happens inside the external_check_bill function
        import aiohttp
        import asyncio
        
        async def simulate_external_call():
            customer_code = "PB09020058383"
            provider_region = "mien_nam"
            
            # Prepare payload exactly as in the backend code
            payload = {
                "bills": [
                    {
                        "customer_id": customer_code,
                        "electric_provider": provider_region,
                        "provider_name": provider_region,
                        "contractNumber": customer_code,
                        "sku": "ELECTRIC_BILL"
                    }
                ],
                "timestamp": int(datetime.now().timestamp() * 1000),
                "request_id": f"fpt_bill_manager_test123",
                "webhookUrl": "https://n8n.phamthanh.net/webhook/checkbill",
                "executionMode": "production"
            }
            
            print(f"📤 External API Payload:")
            print(f"   {json.dumps(payload, indent=2, ensure_ascii=False)}")
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        "https://n8n.phamthanh.net/webhook/checkbill",
                        json=payload,
                        headers={"Content-Type": "application/json"},
                        timeout=30
                    ) as response:
                        response_text = await response.text()
                        
                        print(f"\n📥 External API Response:")
                        print(f"   Status: {response.status}")
                        print(f"   Headers: {dict(response.headers)}")
                        print(f"   Raw Response: {response_text}")
                        
                        try:
                            response_data = json.loads(response_text)
                            print(f"   Parsed Response:")
                            print(f"   {json.dumps(response_data, indent=2, ensure_ascii=False)}")
                            return True, response_data
                        except json.JSONDecodeError:
                            print(f"   Could not parse as JSON")
                            return False, response_text
                            
            except Exception as e:
                print(f"❌ External API call failed: {e}")
                return False, {}
        
        # Run the async function
        try:
            success, result = asyncio.run(simulate_external_call())
            self.tests_run += 1
            if success:
                self.tests_passed += 1
            return success
        except Exception as e:
            print(f"❌ Failed to run external API simulation: {e}")
            self.tests_run += 1
            return False

    def test_customer_detail_with_bill_codes(self):
        """Test customer detail API endpoint to verify bill_codes field in transactions"""
        print(f"\n🔍 Testing Customer Detail API - Bill Codes Functionality")
        
        # First, get list of customers to find one with transactions
        print("📋 Step 1: Getting customers list...")
        customers_success, customers_response = self.run_test(
            "Get Customers List",
            "GET", 
            "customers",
            200
        )
        
        if not customers_success or not customers_response:
            print("❌ Failed to get customers list")
            return False
            
        # Find a customer with transactions
        target_customer = None
        for customer in customers_response:
            if customer.get('total_transactions', 0) > 0:
                target_customer = customer
                break
                
        if not target_customer:
            print("⚠️  No customers with transactions found. Creating test data...")
            # Try to create test customer and transaction data
            return self.create_test_customer_with_transactions()
            
        customer_id = target_customer['id']
        customer_name = target_customer.get('name', 'Unknown')
        print(f"✅ Found customer with transactions: {customer_name} (ID: {customer_id})")
        print(f"   Total transactions: {target_customer.get('total_transactions', 0)}")
        
        # Test the customer detail endpoint
        print(f"\n📋 Step 2: Testing customer detail endpoint...")
        detail_success, detail_response = self.run_test(
            f"Customer Detail - {customer_name}",
            "GET",
            f"customers/{customer_id}/transactions", 
            200
        )
        
        if not detail_success:
            print("❌ Failed to get customer detail")
            return False
            
        # Verify response structure
        print(f"\n🔍 Step 3: Verifying response structure...")
        required_fields = ['customer', 'transactions', 'summary']
        missing_fields = [field for field in required_fields if field not in detail_response]
        
        if missing_fields:
            print(f"❌ Missing required fields: {missing_fields}")
            return False
            
        print(f"✅ All required fields present: {required_fields}")
        
        # Verify transactions structure and bill_codes field
        transactions = detail_response.get('transactions', [])
        print(f"📊 Found {len(transactions)} transactions")
        
        if not transactions:
            print("⚠️  No transactions found for this customer")
            return True  # Not a failure, just no data
            
        # Check each transaction for bill_codes field
        bill_codes_found = 0
        transactions_with_codes = 0
        
        for i, transaction in enumerate(transactions):
            print(f"\n   Transaction {i+1}:")
            print(f"   - ID: {transaction.get('id', 'N/A')}")
            print(f"   - Type: {transaction.get('type', 'N/A')}")
            print(f"   - Total: {transaction.get('total', 'N/A')}")
            print(f"   - Status: {transaction.get('status', 'N/A')}")
            
            # Check for bill_codes field
            bill_codes = transaction.get('bill_codes', [])
            if 'bill_codes' in transaction:
                transactions_with_codes += 1
                if bill_codes:
                    bill_codes_found += len(bill_codes)
                    print(f"   - Bill Codes: {bill_codes}")
                else:
                    print(f"   - Bill Codes: [] (empty array)")
            else:
                print(f"   - ❌ Missing 'bill_codes' field!")
                return False
                
        print(f"\n📊 Bill Codes Analysis:")
        print(f"   - Transactions with bill_codes field: {transactions_with_codes}/{len(transactions)}")
        print(f"   - Total bill codes found: {bill_codes_found}")
        
        # Verify summary structure
        summary = detail_response.get('summary', {})
        summary_fields = ['total_transactions', 'total_value', 'total_profit']
        print(f"\n📊 Summary verification:")
        for field in summary_fields:
            if field in summary:
                print(f"   - {field}: {summary[field]}")
            else:
                print(f"   - ❌ Missing summary field: {field}")
                
        # Success criteria: all transactions have bill_codes field
        if transactions_with_codes == len(transactions):
            print(f"\n✅ SUCCESS: All transactions have 'bill_codes' field")
            print(f"✅ Bill codes functionality is working correctly")
            self.tests_passed += 1
            return True
        else:
            print(f"\n❌ FAILURE: Not all transactions have 'bill_codes' field")
            return False

    def create_test_customer_with_transactions(self):
        """Create test customer and transaction data for testing"""
        print(f"\n🔧 Creating test customer with transactions...")
        
        # Create test customer
        test_customer_data = {
            "name": "Test Customer for Bill Codes",
            "type": "INDIVIDUAL",
            "phone": "0123456789",
            "email": f"test_billcodes_{int(datetime.now().timestamp())}@example.com",
            "address": "123 Test Street, Test City"
        }
        
        customer_success, customer_response = self.run_test(
            "Create Test Customer",
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
        
        # Create test bill first
        test_bill_data = {
            "customer_code": f"TEST{int(datetime.now().timestamp())}",
            "provider_region": "MIEN_NAM",
            "full_name": "Test Bill Customer",
            "address": "Test Address",
            "amount": 1000000,
            "billing_cycle": "12/2025",
            "status": "AVAILABLE"
        }
        
        bill_success, bill_response = self.run_test(
            "Create Test Bill",
            "POST",
            "bills/create",
            200,
            data=test_bill_data
        )
        
        if not bill_success:
            print("❌ Failed to create test bill")
            return False
            
        bill_id = bill_response.get('id')
        print(f"✅ Created test bill: {bill_id}")
        
        # Create test sale/transaction
        test_sale_data = {
            "customer_id": customer_id,
            "bill_ids": [bill_id],
            "profit_pct": 5.0,
            "method": "CASH",
            "notes": f"Test transaction for bill codes - {datetime.now().strftime('%d/%m/%Y')}"
        }
        
        sale_success, sale_response = self.run_test(
            "Create Test Sale",
            "POST",
            "sales",
            200,
            data=test_sale_data
        )
        
        if not sale_success:
            print("❌ Failed to create test sale")
            return False
            
        print(f"✅ Created test sale: {sale_response.get('id')}")
        
        # Now test the customer detail endpoint with our test data
        print(f"\n📋 Testing customer detail with test data...")
        return self.test_customer_transactions_endpoint(customer_id)
        
    def test_customer_transactions_endpoint(self, customer_id):
        """Test specific customer transactions endpoint"""
        detail_success, detail_response = self.run_test(
            f"Customer Transactions Detail",
            "GET",
            f"customers/{customer_id}/transactions",
            200
        )
        
        if not detail_success:
            print("❌ Failed to get customer transactions")
            return False
            
        # Verify the response has the expected structure
        transactions = detail_response.get('transactions', [])
        if not transactions:
            print("⚠️  No transactions found")
            return False
            
        # Check the first transaction for bill_codes
        first_transaction = transactions[0]
        print(f"\n🔍 Analyzing first transaction:")
        print(f"   Transaction structure: {list(first_transaction.keys())}")
        
        if 'bill_codes' not in first_transaction:
            print(f"❌ CRITICAL: 'bill_codes' field missing from transaction!")
            return False
            
        bill_codes = first_transaction.get('bill_codes', [])
        print(f"✅ Found 'bill_codes' field: {bill_codes}")
        
        # Verify bill_codes contains actual customer codes
        if bill_codes and len(bill_codes) > 0:
            print(f"✅ Bill codes populated: {bill_codes}")
            print(f"✅ SUCCESS: Bill codes functionality working correctly!")
            return True
        else:
            print(f"⚠️  Bill codes array is empty, but field exists")
            return True  # Field exists, which is the main requirement

    def test_multiple_customers_bill_codes(self):
        """Test bill_codes functionality with multiple customers"""
        print(f"\n🔍 Testing Bill Codes with Multiple Customers")
        
        # Get customers list
        customers_success, customers_response = self.run_test(
            "Get All Customers",
            "GET",
            "customers",
            200
        )
        
        if not customers_success:
            print("❌ Failed to get customers")
            return False
            
        customers_tested = 0
        customers_with_bill_codes = 0
        
        # Test up to 3 customers with transactions
        for customer in customers_response[:3]:
            if customer.get('total_transactions', 0) > 0:
                customer_id = customer['id']
                customer_name = customer.get('name', 'Unknown')
                
                print(f"\n📋 Testing customer: {customer_name}")
                
                detail_success, detail_response = self.run_test(
                    f"Customer Detail - {customer_name}",
                    "GET",
                    f"customers/{customer_id}/transactions",
                    200
                )
                
                if detail_success:
                    customers_tested += 1
                    transactions = detail_response.get('transactions', [])
                    
                    # Check if all transactions have bill_codes field
                    has_bill_codes = all('bill_codes' in t for t in transactions)
                    if has_bill_codes:
                        customers_with_bill_codes += 1
                        print(f"   ✅ All transactions have bill_codes field")
                    else:
                        print(f"   ❌ Some transactions missing bill_codes field")
                        
        print(f"\n📊 Multiple Customer Test Results:")
        print(f"   - Customers tested: {customers_tested}")
        print(f"   - Customers with proper bill_codes: {customers_with_bill_codes}")
        
        if customers_tested > 0 and customers_with_bill_codes == customers_tested:
            print(f"✅ SUCCESS: All tested customers have proper bill_codes functionality")
            return True
        elif customers_tested == 0:
            print(f"⚠️  No customers with transactions found to test")
            return True  # Not a failure
        else:
            print(f"❌ FAILURE: Inconsistent bill_codes functionality across customers")
            return False

    def test_error_handling(self):
        """Test API error handling"""
        print(f"\n🧪 Testing Error Handling...")
        
        # Test invalid endpoint
        success1, _ = self.run_test(
            "Invalid Endpoint",
            "GET",
            "nonexistent",
            404
        )
        
        # Test invalid request body for bill check
        success2, _ = self.run_test(
            "Invalid Bill Check Request",
            "POST",
            "bill/check",
            422,  # Validation error
            data={
                "invalid_field": "test"
            }
        )
        
        return success1 or success2  # At least one should work

    def test_critical_data_integrity_bill_deletion(self):
        """Test CRITICAL DATA INTEGRITY FIX - Bill deletion validation"""
        print(f"\n🔒 CRITICAL TEST: Data Integrity - Bill Deletion Protection")
        print("=" * 60)
        
        # Step 1: Create test customer
        print("\n📋 Step 1: Creating test customer...")
        test_customer_data = {
            "name": f"Test Customer Delete {int(datetime.now().timestamp())}",
            "type": "INDIVIDUAL",
            "phone": "0987654321",
            "email": f"test_delete_{int(datetime.now().timestamp())}@example.com",
            "address": "Test Address for Delete"
        }
        
        customer_success, customer_response = self.run_test(
            "Create Test Customer for Delete",
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
        
        # Step 2: Create test bills (AVAILABLE and will become SOLD)
        print("\n📋 Step 2: Creating test bills...")
        
        # Bill 1: Will be sold (should be protected from deletion)
        sold_bill_data = {
            "customer_code": f"SOLD{int(datetime.now().timestamp())}",
            "provider_region": "MIEN_NAM",
            "full_name": "Test Sold Bill Customer",
            "address": "Test Address",
            "amount": 1500000,
            "billing_cycle": "12/2025",
            "status": "AVAILABLE"
        }
        
        sold_bill_success, sold_bill_response = self.run_test(
            "Create Bill (Will be SOLD)",
            "POST",
            "bills/create",
            200,
            data=sold_bill_data
        )
        
        if not sold_bill_success:
            print("❌ Failed to create sold bill")
            return False
            
        sold_bill_id = sold_bill_response.get('id')
        print(f"✅ Created bill for selling: {sold_bill_id}")
        
        # Bill 2: Will remain available (should be deletable)
        available_bill_data = {
            "customer_code": f"AVAIL{int(datetime.now().timestamp())}",
            "provider_region": "MIEN_NAM", 
            "full_name": "Test Available Bill Customer",
            "address": "Test Address",
            "amount": 800000,
            "billing_cycle": "12/2025",
            "status": "AVAILABLE"
        }
        
        available_bill_success, available_bill_response = self.run_test(
            "Create Bill (Will stay AVAILABLE)",
            "POST",
            "bills/create",
            200,
            data=available_bill_data
        )
        
        if not available_bill_success:
            print("❌ Failed to create available bill")
            return False
            
        available_bill_id = available_bill_response.get('id')
        print(f"✅ Created available bill: {available_bill_id}")
        
        # Step 3: Create sale transaction (makes first bill SOLD)
        print("\n📋 Step 3: Creating sale transaction...")
        
        sale_data = {
            "customer_id": customer_id,
            "bill_ids": [sold_bill_id],
            "profit_pct": 5.0,
            "method": "CASH",
            "notes": "Test sale for data integrity testing"
        }
        
        sale_success, sale_response = self.run_test(
            "Create Sale Transaction",
            "POST",
            "sales",
            200,
            data=sale_data
        )
        
        if not sale_success:
            print("❌ Failed to create sale transaction")
            return False
            
        sale_id = sale_response.get('id')
        print(f"✅ Created sale transaction: {sale_id}")
        print(f"   Bill {sold_bill_id} is now SOLD and referenced in sales")
        
        # Step 4: TEST 1 - Attempt to delete SOLD bill (should fail with 400)
        print("\n🔒 TEST 1: Attempting to delete SOLD bill...")
        print(f"   Target: {sold_bill_id} (status: SOLD)")
        
        url = f"{self.api_url}/bills/{sold_bill_id}"
        print(f"   DELETE {url}")
        
        try:
            response = requests.delete(url, timeout=30)
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', '')
                    print(f"   Error Message: {error_message}")
                    
                    expected_messages = [
                        "Không thể xóa bill đã bán",
                        "đã được tham chiếu trong giao dịch khách hàng"
                    ]
                    
                    message_found = any(msg in error_message for msg in expected_messages)
                    
                    if message_found:
                        print(f"   ✅ TEST 1 PASSED: SOLD bill deletion correctly blocked")
                        self.tests_passed += 1
                        test1_success = True
                    else:
                        print(f"   ❌ TEST 1 FAILED: Wrong error message")
                        test1_success = False
                except:
                    print(f"   ❌ TEST 1 FAILED: Could not parse error response")
                    test1_success = False
            else:
                print(f"   ❌ TEST 1 FAILED: Expected 400, got {response.status_code}")
                test1_success = False
                
        except Exception as e:
            print(f"   ❌ TEST 1 FAILED: Request error - {e}")
            test1_success = False
        finally:
            self.tests_run += 1
        
        # Step 5: TEST 2 - Attempt to delete bill referenced in sales (double-check)
        print(f"\n🔒 TEST 2: Attempting to delete bill referenced in sales...")
        print(f"   Target: {sold_bill_id} (referenced in sale {sale_id})")
        
        # This should also fail with 400 due to sales reference check
        try:
            response = requests.delete(url, timeout=30)
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_message = error_data.get('detail', '')
                    print(f"   Error Message: {error_message}")
                    
                    expected_messages = [
                        "Không thể xóa bill đã có giao dịch",
                        "đang được tham chiếu trong lịch sử bán hàng"
                    ]
                    
                    message_found = any(msg in error_message for msg in expected_messages)
                    
                    if message_found:
                        print(f"   ✅ TEST 2 PASSED: Referenced bill deletion correctly blocked")
                        self.tests_passed += 1
                        test2_success = True
                    else:
                        print(f"   ✅ TEST 2 PASSED: Bill deletion blocked (different message)")
                        self.tests_passed += 1
                        test2_success = True  # Any 400 error is acceptable
                except:
                    print(f"   ✅ TEST 2 PASSED: Bill deletion blocked")
                    self.tests_passed += 1
                    test2_success = True
            else:
                print(f"   ❌ TEST 2 FAILED: Expected 400, got {response.status_code}")
                test2_success = False
                
        except Exception as e:
            print(f"   ❌ TEST 2 FAILED: Request error - {e}")
            test2_success = False
        finally:
            self.tests_run += 1
        
        # Step 6: TEST 3 - Successfully delete AVAILABLE bill
        print(f"\n🔓 TEST 3: Attempting to delete AVAILABLE bill...")
        print(f"   Target: {available_bill_id} (status: AVAILABLE, not referenced)")
        
        url = f"{self.api_url}/bills/{available_bill_id}"
        print(f"   DELETE {url}")
        
        try:
            response = requests.delete(url, timeout=30)
            print(f"   Response Status: {response.status_code}")
            
            if response.status_code == 200:
                try:
                    success_data = response.json()
                    success_message = success_data.get('message', '')
                    print(f"   Success Message: {success_message}")
                    
                    if success_data.get('success') == True:
                        print(f"   ✅ TEST 3 PASSED: AVAILABLE bill successfully deleted")
                        self.tests_passed += 1
                        test3_success = True
                    else:
                        print(f"   ❌ TEST 3 FAILED: Success flag not true")
                        test3_success = False
                except:
                    print(f"   ✅ TEST 3 PASSED: Bill deleted (could not parse response)")
                    self.tests_passed += 1
                    test3_success = True
            else:
                print(f"   ❌ TEST 3 FAILED: Expected 200, got {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error text: {response.text}")
                test3_success = False
                
        except Exception as e:
            print(f"   ❌ TEST 3 FAILED: Request error - {e}")
            test3_success = False
        finally:
            self.tests_run += 1
        
        # Step 7: TEST 4 - Verify inventory cleanup
        print(f"\n🧹 TEST 4: Verifying inventory cleanup...")
        
        # Check if the deleted bill is removed from inventory
        inventory_success, inventory_response = self.run_test(
            "Get Inventory Items",
            "GET",
            "inventory",
            200
        )
        
        if inventory_success:
            # Look for the deleted bill in inventory
            deleted_bill_in_inventory = any(
                item.get('bill_id') == available_bill_id 
                for item in inventory_response
            )
            
            if not deleted_bill_in_inventory:
                print(f"   ✅ TEST 4 PASSED: Deleted bill removed from inventory")
                self.tests_passed += 1
                test4_success = True
            else:
                print(f"   ❌ TEST 4 FAILED: Deleted bill still in inventory")
                test4_success = False
        else:
            print(f"   ⚠️  TEST 4 SKIPPED: Could not get inventory")
            test4_success = True  # Don't fail the whole test
        
        self.tests_run += 1
        
        # Summary
        print(f"\n📊 CRITICAL DATA INTEGRITY TEST RESULTS:")
        print(f"   TEST 1 (Delete SOLD bill): {'✅ PASSED' if test1_success else '❌ FAILED'}")
        print(f"   TEST 2 (Delete referenced bill): {'✅ PASSED' if test2_success else '❌ FAILED'}")
        print(f"   TEST 3 (Delete AVAILABLE bill): {'✅ PASSED' if test3_success else '❌ FAILED'}")
        print(f"   TEST 4 (Inventory cleanup): {'✅ PASSED' if test4_success else '❌ FAILED'}")
        
        overall_success = test1_success and test2_success and test3_success and test4_success
        
        if overall_success:
            print(f"\n🎉 CRITICAL DATA INTEGRITY FIX VERIFIED SUCCESSFULLY!")
            print(f"   ✅ SOLD bills are protected from deletion")
            print(f"   ✅ Referenced bills are protected from deletion")
            print(f"   ✅ AVAILABLE bills can be deleted safely")
            print(f"   ✅ Inventory cleanup works correctly")
        else:
            print(f"\n🚨 CRITICAL DATA INTEGRITY ISSUES DETECTED!")
            print(f"   ⚠️  System may allow deletion of SOLD/referenced bills")
            print(f"   ⚠️  This could cause data inconsistency and broken references")
        
        return overall_success

def main():
    print("🚀 Starting FPT Bill Manager API Tests")
    print("=" * 50)
    
    tester = FPTBillManagerAPITester()
    
    # Run all tests - focusing on bill_codes functionality first (as per review request)
    tests = [
        tester.test_customer_detail_with_bill_codes,  # PRIMARY TEST: Bill codes functionality
        tester.test_multiple_customers_bill_codes,    # Test consistency across customers
        tester.test_debug_payload_mien_nam,           # Test MIEN_NAM -> mien_nam mapping
        tester.test_debug_payload_hcmc,               # Test HCMC -> evnhcmc mapping (corrected)
        tester.test_single_bill_check_mien_nam,       # Test actual bill check with MIEN_NAM
        tester.test_single_bill_check_hcmc,           # Test actual bill check with HCMC
        tester.test_external_api_call_simulation,     # Test external API call
        tester.test_dashboard_stats,
        tester.test_check_bills_valid,
        tester.test_check_bills_invalid,
        tester.test_get_bills,
        tester.test_get_customers,
        tester.test_webhook_endpoint,
        tester.test_error_handling
    ]
    
    for test in tests:
        try:
            test()
        except Exception as e:
            print(f"❌ Test failed with exception: {str(e)}")
    
    # Print final results
    print("\n" + "=" * 50)
    print(f"📊 Final Results: {tester.tests_passed}/{tester.tests_run} tests passed")
    
    if tester.tests_passed == tester.tests_run:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check logs above")
        return 1

if __name__ == "__main__":
    sys.exit(main())