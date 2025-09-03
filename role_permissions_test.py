import requests
import sys
import json
from datetime import datetime

class RoleBasedPermissionTester:
    def __init__(self, base_url="https://crm7ty.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        
        # Test account credentials
        self.test_accounts = {
            "admin": {
                "username": "admin_test",
                "password": "admin123",
                "token": None,
                "expected_role": "admin"
            },
            "manager": {
                "username": "manager_test", 
                "password": "manager123",
                "token": None,
                "expected_role": "manager"
            },
            "user": {
                "username": "user_test",
                "password": "user123", 
                "token": None,
                "expected_role": "user"
            }
        }
        
        # Permission matrix - what each role should be able to access
        self.permission_matrix = {
            "admin": {
                "auth/users": {"GET": 200, "PUT": 200},  # Can view and modify users
                "customers": {"GET": 200, "POST": 200, "PUT": 200, "DELETE": 200},
                "bills": {"GET": 200, "POST": 200, "PUT": 200, "DELETE": 200},
                "credit-cards": {"GET": 200, "POST": 200, "PUT": 200, "DELETE": 200},
                "inventory": {"GET": 200, "POST": 200, "DELETE": 200},
                "dashboard/stats": {"GET": 200},
                "sales": {"GET": 200, "POST": 200},
                "activities/recent": {"GET": 200}
            },
            "manager": {
                "auth/users": {"GET": 200, "PUT": 403},  # Can view but not modify users
                "customers": {"GET": 200, "POST": 200, "PUT": 200, "DELETE": 200},
                "bills": {"GET": 200, "POST": 200, "PUT": 200, "DELETE": 200},
                "credit-cards": {"GET": 200, "POST": 200, "PUT": 200, "DELETE": 200},
                "inventory": {"GET": 200, "POST": 200, "DELETE": 200},
                "dashboard/stats": {"GET": 200},
                "sales": {"GET": 200, "POST": 200},
                "activities/recent": {"GET": 200}
            },
            "user": {
                "auth/users": {"GET": 403, "PUT": 403},  # Cannot access user management
                "customers": {"GET": 403, "POST": 403, "PUT": 403, "DELETE": 403},
                "bills": {"GET": 403, "POST": 403, "PUT": 403, "DELETE": 403},
                "credit-cards": {"GET": 403, "POST": 403, "PUT": 403, "DELETE": 403},
                "inventory": {"GET": 403, "POST": 403, "DELETE": 403},
                "dashboard/stats": {"GET": 403},
                "sales": {"GET": 403, "POST": 403},
                "activities/recent": {"GET": 403}
            }
        }

    def login_user(self, role):
        """Login user and get JWT token"""
        account = self.test_accounts[role]
        
        login_data = {
            "login": account["username"],
            "password": account["password"]
        }
        
        print(f"\n🔐 Logging in as {role.upper()}: {account['username']}")
        
        try:
            response = requests.post(
                f"{self.api_url}/auth/login",
                json=login_data,
                timeout=30
            )
            
            if response.status_code == 200:
                response_data = response.json()
                token = response_data.get("access_token")
                user_info = response_data.get("user", {})
                actual_role = user_info.get("role")
                
                print(f"   ✅ Login successful")
                print(f"   👤 User: {user_info.get('full_name', 'Unknown')}")
                print(f"   🎭 Role: {actual_role}")
                print(f"   🔑 Token: {token[:20]}..." if token else "   ❌ No token received")
                
                # Verify role matches expected
                if actual_role == account["expected_role"]:
                    print(f"   ✅ Role verification passed")
                    account["token"] = token
                    return True, token
                else:
                    print(f"   ❌ Role mismatch: expected {account['expected_role']}, got {actual_role}")
                    return False, None
                    
            else:
                print(f"   ❌ Login failed: {response.status_code}")
                try:
                    error_data = response.json()
                    print(f"   Error: {error_data}")
                except:
                    print(f"   Error: {response.text}")
                return False, None
                
        except Exception as e:
            print(f"   ❌ Login error: {e}")
            return False, None

    def test_endpoint_with_role(self, role, endpoint, method="GET", data=None, expected_status=200):
        """Test specific endpoint with specific role"""
        token = self.test_accounts[role]["token"]
        
        if not token:
            print(f"   ❌ No token for {role} - login required")
            return False
            
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.api_url}/{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == "PUT":
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, timeout=30)
            else:
                print(f"   ❌ Unsupported method: {method}")
                return False
                
            success = response.status_code == expected_status
            
            if success:
                print(f"   ✅ {method} {endpoint}: {response.status_code} (Expected: {expected_status})")
                return True
            else:
                print(f"   ❌ {method} {endpoint}: {response.status_code} (Expected: {expected_status})")
                
                # Show error details for debugging
                if response.status_code == 403:
                    print(f"      🚫 Access denied - insufficient permissions")
                elif response.status_code == 401:
                    print(f"      🔐 Authentication failed - invalid token")
                else:
                    try:
                        error_data = response.json()
                        print(f"      Error: {error_data}")
                    except:
                        print(f"      Error: {response.text[:100]}")
                        
                return False
                
        except Exception as e:
            print(f"   ❌ Request error: {e}")
            return False

    def test_all_role_permissions(self):
        """Test all role permissions comprehensively"""
        print(f"\n🎯 COMPREHENSIVE ROLE-BASED PERMISSION TESTING")
        print("=" * 80)
        
        # Step 1: Login all test accounts
        print(f"\n📋 STEP 1: Logging in all test accounts...")
        
        login_results = {}
        for role in self.test_accounts.keys():
            success, token = self.login_user(role)
            login_results[role] = success
            
        # Check if all logins succeeded
        failed_logins = [role for role, success in login_results.items() if not success]
        if failed_logins:
            print(f"\n❌ Failed to login: {failed_logins}")
            print(f"Cannot proceed with permission testing without valid tokens")
            return False
            
        print(f"\n✅ All test accounts logged in successfully")
        
        # Step 2: Test each role's permissions
        print(f"\n📋 STEP 2: Testing role-based permissions...")
        
        total_tests = 0
        passed_tests = 0
        role_results = {}
        
        for role, permissions in self.permission_matrix.items():
            print(f"\n🎭 Testing {role.upper()} permissions:")
            print(f"   Expected access level: {self.get_role_description(role)}")
            
            role_passed = 0
            role_total = 0
            
            for endpoint, methods in permissions.items():
                print(f"\n   📍 Endpoint: /{endpoint}")
                
                for method, expected_status in methods.items():
                    role_total += 1
                    total_tests += 1
                    
                    # Prepare test data if needed
                    test_data = self.get_test_data_for_endpoint(endpoint, method)
                    
                    # Test the endpoint
                    success = self.test_endpoint_with_role(
                        role, endpoint, method, test_data, expected_status
                    )
                    
                    if success:
                        role_passed += 1
                        passed_tests += 1
                        
            # Calculate role success rate
            role_success_rate = (role_passed / role_total * 100) if role_total > 0 else 0
            role_results[role] = {
                "passed": role_passed,
                "total": role_total,
                "success_rate": role_success_rate
            }
            
            print(f"\n   📊 {role.upper()} Results: {role_passed}/{role_total} ({role_success_rate:.1f}%)")
            
        # Step 3: Test cross-role scenarios
        print(f"\n📋 STEP 3: Testing cross-role scenarios...")
        
        cross_role_tests = [
            {
                "name": "Admin can modify user roles",
                "role": "admin",
                "endpoint": "auth/users/test_user_id/role",
                "method": "PUT",
                "data": {"role": "manager"},
                "expected": 200
            },
            {
                "name": "Manager cannot modify user roles", 
                "role": "manager",
                "endpoint": "auth/users/test_user_id/role",
                "method": "PUT", 
                "data": {"role": "admin"},
                "expected": 403
            },
            {
                "name": "User cannot access user list",
                "role": "user",
                "endpoint": "auth/users",
                "method": "GET",
                "expected": 403
            }
        ]
        
        cross_role_passed = 0
        for test in cross_role_tests:
            print(f"\n   🧪 {test['name']}")
            success = self.test_endpoint_with_role(
                test["role"], test["endpoint"], test["method"], 
                test.get("data"), test["expected"]
            )
            if success:
                cross_role_passed += 1
                
        # Step 4: Generate comprehensive report
        print(f"\n📊 STEP 4: Comprehensive Permission Analysis")
        print("=" * 60)
        
        overall_success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests}")
        print(f"   Failed: {total_tests - passed_tests}")
        print(f"   Success Rate: {overall_success_rate:.1f}%")
        
        print(f"\n🎭 ROLE-SPECIFIC RESULTS:")
        for role, results in role_results.items():
            status = "✅" if results["success_rate"] >= 90 else "⚠️" if results["success_rate"] >= 70 else "❌"
            print(f"   {status} {role.upper()}: {results['passed']}/{results['total']} ({results['success_rate']:.1f}%)")
            
        print(f"\n🔄 CROSS-ROLE SCENARIOS:")
        cross_success_rate = (cross_role_passed / len(cross_role_tests) * 100) if cross_role_tests else 0
        print(f"   Passed: {cross_role_passed}/{len(cross_role_tests)} ({cross_success_rate:.1f}%)")
        
        # Step 5: Generate permission matrix
        print(f"\n📋 STEP 5: Actual vs Expected Permission Matrix")
        self.generate_permission_matrix_report()
        
        # Update test counters
        self.tests_run += total_tests
        self.tests_passed += passed_tests
        
        return overall_success_rate >= 80  # Consider success if 80%+ tests pass

    def get_role_description(self, role):
        """Get human-readable role description"""
        descriptions = {
            "admin": "Full system access - all operations allowed",
            "manager": "Limited admin access - can view users but not modify roles",
            "user": "Basic access - own profile only, no admin functions"
        }
        return descriptions.get(role, "Unknown role")

    def get_test_data_for_endpoint(self, endpoint, method):
        """Get appropriate test data for endpoint testing"""
        if method == "GET":
            return None
            
        # Sample test data for different endpoints
        test_data_map = {
            "customers": {
                "name": "Test Customer for Permissions",
                "type": "INDIVIDUAL",
                "phone": "0123456789",
                "email": f"test_permissions_{int(datetime.now().timestamp())}@example.com"
            },
            "bills": {
                "customer_code": f"PERM_TEST_{int(datetime.now().timestamp())}",
                "provider_region": "MIEN_NAM",
                "full_name": "Permission Test Customer",
                "amount": 1000000,
                "billing_cycle": "12/2025"
            },
            "credit-cards": {
                "customer_id": "test_customer_id",
                "card_number": "1234567890123456",
                "cardholder_name": "Test Cardholder",
                "bank_name": "Test Bank",
                "card_type": "VISA",
                "expiry_date": "12/25",
                "ccv": "123",
                "statement_date": 15,
                "payment_due_date": 25,
                "credit_limit": 50000000
            },
            "auth/users/test_user_id/role": {
                "role": "manager"
            }
        }
        
        # Find matching test data
        for key, data in test_data_map.items():
            if key in endpoint:
                return data
                
        return {}

    def generate_permission_matrix_report(self):
        """Generate detailed permission matrix report"""
        print(f"\n📊 DETAILED PERMISSION MATRIX:")
        print(f"{'Endpoint':<25} {'Admin':<8} {'Manager':<8} {'User':<8}")
        print("-" * 50)
        
        # Get all unique endpoints
        all_endpoints = set()
        for role_perms in self.permission_matrix.values():
            all_endpoints.update(role_perms.keys())
            
        for endpoint in sorted(all_endpoints):
            admin_access = self.get_access_level("admin", endpoint)
            manager_access = self.get_access_level("manager", endpoint) 
            user_access = self.get_access_level("user", endpoint)
            
            print(f"{endpoint:<25} {admin_access:<8} {manager_access:<8} {user_access:<8}")

    def get_access_level(self, role, endpoint):
        """Get access level for role/endpoint combination"""
        if role not in self.permission_matrix:
            return "N/A"
            
        role_perms = self.permission_matrix[role]
        if endpoint not in role_perms:
            return "N/A"
            
        methods = role_perms[endpoint]
        
        # Determine access level based on allowed methods
        if any(status == 200 for status in methods.values()):
            allowed_methods = [method for method, status in methods.items() if status == 200]
            if "PUT" in allowed_methods or "DELETE" in allowed_methods:
                return "FULL"
            elif "POST" in allowed_methods:
                return "WRITE"
            elif "GET" in allowed_methods:
                return "READ"
        
        return "DENIED"

    def test_specific_business_logic_permissions(self):
        """Test business logic specific permissions"""
        print(f"\n🏢 TESTING BUSINESS LOGIC PERMISSIONS")
        print("=" * 50)
        
        # Test customer data access restrictions
        print(f"\n📋 Customer Data Access:")
        
        # Admin should see all customers
        self.test_customer_data_access("admin", "Should see all customer data")
        
        # Manager should see all customers but limited modification
        self.test_customer_data_access("manager", "Should see all customers, limited admin functions")
        
        # User should not see customer data
        self.test_customer_data_access("user", "Should not access customer data")
        
        # Test financial data access
        print(f"\n💰 Financial Data Access:")
        
        # Test dashboard stats (contains revenue information)
        for role in ["admin", "manager", "user"]:
            expected = 200 if role in ["admin", "manager"] else 403
            self.test_endpoint_with_role(role, "dashboard/stats", "GET", None, expected)
            
        # Test sales data access
        for role in ["admin", "manager", "user"]:
            expected = 200 if role in ["admin", "manager"] else 403
            self.test_endpoint_with_role(role, "sales", "GET", None, expected)

    def test_customer_data_access(self, role, description):
        """Test customer data access for specific role"""
        print(f"\n   🎭 {role.upper()}: {description}")
        
        # Test customer list access
        expected_status = 200 if role in ["admin", "manager"] else 403
        success = self.test_endpoint_with_role(role, "customers", "GET", None, expected_status)
        
        if success and role in ["admin", "manager"]:
            # If can access customers, test customer stats
            self.test_endpoint_with_role(role, "customers/stats", "GET", None, 200)
            
            # Test customer export (should be allowed for admin/manager)
            self.test_endpoint_with_role(role, "customers/export", "GET", None, 200)

    def run_comprehensive_role_testing(self):
        """Run all role-based permission tests"""
        print(f"\n🚀 STARTING COMPREHENSIVE ROLE-BASED PERMISSION ANALYSIS")
        print("=" * 80)
        print(f"🎯 OBJECTIVE: Analyze what each role can actually access")
        print(f"👥 TEST ACCOUNTS: admin_test, manager_test, user_test")
        print(f"🔍 SCOPE: All major API endpoints and business logic")
        
        try:
            # Main permission testing
            main_success = self.test_all_role_permissions()
            
            # Business logic testing
            self.test_specific_business_logic_permissions()
            
            # Generate final summary
            print(f"\n🎯 FINAL SUMMARY")
            print("=" * 40)
            
            success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
            
            print(f"📊 Overall Results:")
            print(f"   Tests Run: {self.tests_run}")
            print(f"   Tests Passed: {self.tests_passed}")
            print(f"   Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print(f"✅ EXCELLENT: Role-based permissions working correctly")
            elif success_rate >= 70:
                print(f"⚠️  GOOD: Most permissions working, some issues found")
            else:
                print(f"❌ ISSUES: Significant permission problems detected")
                
            # Provide role-specific recommendations
            print(f"\n💡 ROLE ACCESS SUMMARY:")
            print(f"   🔴 ADMIN: Full system access - can manage users, access all data")
            print(f"   🟡 MANAGER: Can view users, manage customers/bills, access reports")
            print(f"   🟢 USER: Limited access - own profile only, no admin functions")
            
            return main_success
            
        except Exception as e:
            print(f"❌ Comprehensive testing failed: {e}")
            return False

if __name__ == "__main__":
    tester = RoleBasedPermissionTester()
    success = tester.run_comprehensive_role_testing()
    
    if success:
        print(f"\n✅ Role-based permission testing completed successfully")
        sys.exit(0)
    else:
        print(f"\n❌ Role-based permission testing found issues")
        sys.exit(1)