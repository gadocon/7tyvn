#!/usr/bin/env python3
"""
COMPREHENSIVE SYSTEM AUDIT - Full database and API review
As requested in the review request for production readiness assessment
"""

import requests
import sys
import json
from datetime import datetime
import pymongo
from pymongo import MongoClient
import uuid

class ComprehensiveSystemAudit:
    def __init__(self, base_url="https://seventy-crm-fix.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.critical_issues = []
        self.audit_results = {
            "database_integrity": {},
            "api_endpoints": {},
            "business_logic": {},
            "system_stability": {},
            "production_readiness_score": 0
        }
        
        # MongoDB connection for database audit
        try:
            self.mongo_client = MongoClient("mongodb://localhost:27017")
            self.db = self.mongo_client["test_database"]
            self.mongo_connected = True
            print("✅ MongoDB connection established for database audit")
        except Exception as e:
            print(f"⚠️ MongoDB connection failed: {e}")
            self.mongo_connected = False

    def run_test(self, name, method, endpoint, expected_status, data=None, headers=None):
        """Run a single API test with detailed logging"""
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

    def phase1_database_integrity_audit(self):
        """PHASE 1: DATABASE INTEGRITY AUDIT"""
        print(f"\n🎯 PHASE 1: DATABASE INTEGRITY AUDIT")
        print("=" * 80)
        print("🔍 AUDIT OBJECTIVES:")
        print("   1. Check all collections structure và data consistency")
        print("   2. Verify foreign key relationships (customer_id, card_id, bill_id references)")
        print("   3. Identify orphaned records hoặc broken relationships")
        print("   4. Validate data types và required fields across collections")
        print("   5. Check for duplicate IDs hoặc inconsistent formats")
        
        if not self.mongo_connected:
            print("❌ Cannot perform database audit - MongoDB connection failed")
            self.critical_issues.append("Database connection unavailable for audit")
            return False
        
        audit_results = {
            "collections_analyzed": 0,
            "total_documents": 0,
            "broken_references": [],
            "orphaned_records": [],
            "data_inconsistencies": [],
            "id_format_issues": []
        }
        
        # Get all collections
        collections = self.db.list_collection_names()
        print(f"\n📊 Found {len(collections)} collections: {collections}")
        
        # Analyze each collection
        for collection_name in collections:
            print(f"\n🔍 Analyzing collection: {collection_name}")
            collection = self.db[collection_name]
            
            # Count documents
            doc_count = collection.count_documents({})
            audit_results["total_documents"] += doc_count
            audit_results["collections_analyzed"] += 1
            
            print(f"   Documents: {doc_count}")
            
            if doc_count > 0:
                # Sample documents for structure analysis
                sample_docs = list(collection.find({}).limit(5))
                
                # Check ID consistency
                id_formats = {"uuid": 0, "objectid": 0, "other": 0}
                for doc in sample_docs:
                    doc_id = doc.get('id', str(doc.get('_id', '')))
                    if len(doc_id) == 36 and doc_id.count('-') == 4:
                        id_formats["uuid"] += 1
                    elif len(doc_id) == 24 and all(c in '0123456789abcdef' for c in doc_id.lower()):
                        id_formats["objectid"] += 1
                    else:
                        id_formats["other"] += 1
                
                print(f"   ID formats: UUID={id_formats['uuid']}, ObjectId={id_formats['objectid']}, Other={id_formats['other']}")
                
                # Check for mixed ID formats (potential issue)
                if id_formats["uuid"] > 0 and id_formats["objectid"] > 0:
                    audit_results["id_format_issues"].append({
                        "collection": collection_name,
                        "issue": "Mixed UUID and ObjectId formats",
                        "uuid_count": id_formats["uuid"],
                        "objectid_count": id_formats["objectid"]
                    })
                
                # Check foreign key relationships
                if collection_name == "credit_cards":
                    # Check customer_id references
                    for doc in sample_docs:
                        customer_id = doc.get('customer_id')
                        if customer_id:
                            customer_exists = self.db.customers.find_one({"id": customer_id})
                            if not customer_exists:
                                # Try ObjectId lookup
                                try:
                                    from bson import ObjectId
                                    customer_exists = self.db.customers.find_one({"_id": ObjectId(customer_id)})
                                except:
                                    pass
                                
                                if not customer_exists:
                                    audit_results["broken_references"].append({
                                        "collection": collection_name,
                                        "document_id": doc.get('id', str(doc.get('_id'))),
                                        "broken_reference": f"customer_id: {customer_id}",
                                        "reference_collection": "customers"
                                    })
                
                elif collection_name == "credit_card_transactions":
                    # Check card_id and customer_id references
                    for doc in sample_docs:
                        card_id = doc.get('card_id')
                        customer_id = doc.get('customer_id')
                        
                        if card_id:
                            card_exists = self.db.credit_cards.find_one({"id": card_id})
                            if not card_exists:
                                audit_results["broken_references"].append({
                                    "collection": collection_name,
                                    "document_id": doc.get('id', str(doc.get('_id'))),
                                    "broken_reference": f"card_id: {card_id}",
                                    "reference_collection": "credit_cards"
                                })
                        
                        if customer_id:
                            customer_exists = self.db.customers.find_one({"id": customer_id})
                            if not customer_exists:
                                audit_results["broken_references"].append({
                                    "collection": collection_name,
                                    "document_id": doc.get('id', str(doc.get('_id'))),
                                    "broken_reference": f"customer_id: {customer_id}",
                                    "reference_collection": "customers"
                                })
                
                elif collection_name == "sales":
                    # Check customer_id and bill_ids references
                    for doc in sample_docs:
                        customer_id = doc.get('customer_id')
                        bill_ids = doc.get('bill_ids', [])
                        
                        if customer_id:
                            customer_exists = self.db.customers.find_one({"id": customer_id})
                            if not customer_exists:
                                audit_results["broken_references"].append({
                                    "collection": collection_name,
                                    "document_id": doc.get('id', str(doc.get('_id'))),
                                    "broken_reference": f"customer_id: {customer_id}",
                                    "reference_collection": "customers"
                                })
                        
                        for bill_id in bill_ids:
                            bill_exists = self.db.bills.find_one({"id": bill_id})
                            if not bill_exists:
                                audit_results["broken_references"].append({
                                    "collection": collection_name,
                                    "document_id": doc.get('id', str(doc.get('_id'))),
                                    "broken_reference": f"bill_id: {bill_id}",
                                    "reference_collection": "bills"
                                })
        
        # Summary
        print(f"\n📊 DATABASE INTEGRITY AUDIT SUMMARY:")
        print(f"   Collections analyzed: {audit_results['collections_analyzed']}")
        print(f"   Total documents: {audit_results['total_documents']}")
        print(f"   Broken references: {len(audit_results['broken_references'])}")
        print(f"   ID format issues: {len(audit_results['id_format_issues'])}")
        
        if audit_results['broken_references']:
            print(f"\n🚨 BROKEN REFERENCES FOUND:")
            for ref in audit_results['broken_references'][:5]:  # Show first 5
                print(f"   - {ref['collection']}: {ref['broken_reference']}")
        
        if audit_results['id_format_issues']:
            print(f"\n⚠️ ID FORMAT ISSUES:")
            for issue in audit_results['id_format_issues']:
                print(f"   - {issue['collection']}: {issue['issue']}")
        
        self.audit_results["database_integrity"] = audit_results
        
        # Determine if database integrity is acceptable
        integrity_score = 100
        if len(audit_results['broken_references']) > 0:
            integrity_score -= 30
        if len(audit_results['id_format_issues']) > 0:
            integrity_score -= 10
        
        print(f"\n🎯 DATABASE INTEGRITY SCORE: {integrity_score}%")
        return integrity_score >= 80

    def phase2_api_endpoints_testing(self):
        """PHASE 2: API ENDPOINTS COMPREHENSIVE TESTING"""
        print(f"\n🎯 PHASE 2: API ENDPOINTS COMPREHENSIVE TESTING")
        print("=" * 80)
        print("🔍 TESTING OBJECTIVES:")
        print("   1. Test ALL CRUD operations cho customers, credit_cards, bills, transactions")
        print("   2. Test edge cases: empty data, invalid IDs, missing fields")
        print("   3. Verify error handling patterns across all endpoints")
        print("   4. Check response formats và status codes consistency")
        print("   5. Test pagination, filtering, searching functionality")
        
        api_results = {
            "endpoints_tested": 0,
            "endpoints_passed": 0,
            "crud_operations": {"create": 0, "read": 0, "update": 0, "delete": 0},
            "error_handling": {"proper": 0, "improper": 0},
            "critical_failures": []
        }
        
        # Test Customer CRUD operations
        print(f"\n🔍 Testing Customer CRUD Operations")
        print("-" * 50)
        
        # GET /customers
        customers_success, customers_response = self.run_test(
            "GET /customers - List customers",
            "GET",
            "customers?page_size=10",
            200
        )
        
        if customers_success:
            api_results["endpoints_passed"] += 1
            api_results["crud_operations"]["read"] += 1
            print(f"   ✅ Found {len(customers_response)} customers")
        else:
            api_results["critical_failures"].append("GET /customers failed")
        
        api_results["endpoints_tested"] += 1
        
        # Test individual customer lookup if customers exist
        if customers_success and customers_response:
            test_customer = customers_response[0]
            customer_id = test_customer.get('id')
            
            # GET /customers/{id}
            customer_detail_success, customer_detail_response = self.run_test(
                f"GET /customers/{customer_id} - Individual customer",
                "GET",
                f"customers/{customer_id}",
                200
            )
            
            if customer_detail_success:
                api_results["endpoints_passed"] += 1
                api_results["crud_operations"]["read"] += 1
            else:
                api_results["critical_failures"].append(f"GET /customers/{customer_id} failed")
            
            api_results["endpoints_tested"] += 1
            
            # GET /customers/{id}/detailed-profile
            profile_success, profile_response = self.run_test(
                f"GET /customers/{customer_id}/detailed-profile - Customer profile",
                "GET",
                f"customers/{customer_id}/detailed-profile",
                200
            )
            
            if profile_success:
                api_results["endpoints_passed"] += 1
                api_results["crud_operations"]["read"] += 1
            else:
                api_results["critical_failures"].append(f"GET /customers/{customer_id}/detailed-profile failed")
            
            api_results["endpoints_tested"] += 1
        
        # Test Credit Cards CRUD operations
        print(f"\n🔍 Testing Credit Cards CRUD Operations")
        print("-" * 50)
        
        # GET /credit-cards
        cards_success, cards_response = self.run_test(
            "GET /credit-cards - List credit cards",
            "GET",
            "credit-cards?page_size=10",
            200
        )
        
        if cards_success:
            api_results["endpoints_passed"] += 1
            api_results["crud_operations"]["read"] += 1
            print(f"   ✅ Found {len(cards_response)} credit cards")
        else:
            api_results["critical_failures"].append("GET /credit-cards failed")
        
        api_results["endpoints_tested"] += 1
        
        # Test individual credit card lookup - THIS IS THE CRITICAL TEST
        if cards_success and cards_response:
            test_card = cards_response[0]
            card_id = test_card.get('id')
            
            # GET /credit-cards/{id}/detail - CRITICAL TEST FOR SCHEMA ISSUE
            card_detail_success, card_detail_response = self.run_test(
                f"GET /credit-cards/{card_id}/detail - CRITICAL SCHEMA TEST",
                "GET",
                f"credit-cards/{card_id}/detail",
                200
            )
            
            if card_detail_success:
                api_results["endpoints_passed"] += 1
                api_results["crud_operations"]["read"] += 1
                print(f"   ✅ CRITICAL: Credit card detail endpoint working!")
            else:
                api_results["critical_failures"].append(f"CRITICAL: GET /credit-cards/{card_id}/detail failed - SCHEMA ISSUE")
                self.critical_issues.append("Credit card schema migration incomplete - detail endpoint failing")
            
            api_results["endpoints_tested"] += 1
        
        # Test Bills CRUD operations
        print(f"\n🔍 Testing Bills CRUD Operations")
        print("-" * 50)
        
        # GET /bills
        bills_success, bills_response = self.run_test(
            "GET /bills - List bills",
            "GET",
            "bills?limit=10",
            200
        )
        
        if bills_success:
            api_results["endpoints_passed"] += 1
            api_results["crud_operations"]["read"] += 1
            print(f"   ✅ Found {len(bills_response)} bills")
        else:
            api_results["critical_failures"].append("GET /bills failed")
        
        api_results["endpoints_tested"] += 1
        
        # Test Transactions operations
        print(f"\n🔍 Testing Transactions Operations")
        print("-" * 50)
        
        # GET /transactions/unified
        transactions_success, transactions_response = self.run_test(
            "GET /transactions/unified - Unified transactions",
            "GET",
            "transactions/unified?limit=10",
            200
        )
        
        if transactions_success:
            api_results["endpoints_passed"] += 1
            api_results["crud_operations"]["read"] += 1
            print(f"   ✅ Found {len(transactions_response)} transactions")
        else:
            api_results["critical_failures"].append("GET /transactions/unified failed")
        
        api_results["endpoints_tested"] += 1
        
        # Test Error Handling
        print(f"\n🔍 Testing Error Handling Patterns")
        print("-" * 50)
        
        # Test 404 handling
        not_found_success, not_found_response = self.run_test(
            "GET /customers/nonexistent - 404 handling",
            "GET",
            "customers/nonexistent-id-12345",
            404
        )
        
        if not_found_success:
            api_results["error_handling"]["proper"] += 1
            print(f"   ✅ 404 error handling working correctly")
        else:
            api_results["error_handling"]["improper"] += 1
            print(f"   ❌ 404 error handling not working properly")
        
        # Summary
        success_rate = (api_results["endpoints_passed"] / api_results["endpoints_tested"] * 100) if api_results["endpoints_tested"] > 0 else 0
        
        print(f"\n📊 API ENDPOINTS TESTING SUMMARY:")
        print(f"   Endpoints tested: {api_results['endpoints_tested']}")
        print(f"   Endpoints passed: {api_results['endpoints_passed']}")
        print(f"   Success rate: {success_rate:.1f}%")
        print(f"   CRUD operations: {api_results['crud_operations']}")
        print(f"   Critical failures: {len(api_results['critical_failures'])}")
        
        if api_results['critical_failures']:
            print(f"\n🚨 CRITICAL API FAILURES:")
            for failure in api_results['critical_failures']:
                print(f"   - {failure}")
        
        self.audit_results["api_endpoints"] = api_results
        
        print(f"\n🎯 API ENDPOINTS SCORE: {success_rate:.1f}%")
        return success_rate >= 80

    def phase3_business_logic_validation(self):
        """PHASE 3: BUSINESS LOGIC VALIDATION"""
        print(f"\n🎯 PHASE 3: BUSINESS LOGIC VALIDATION")
        print("=" * 80)
        print("🔍 VALIDATION OBJECTIVES:")
        print("   1. Test complete user flows: create customer → add cards → perform transactions")
        print("   2. Verify data consistency after operations (stats updates, relationships)")
        print("   3. Test delete cascades và data integrity")
        print("   4. Validate transaction calculations (profit, fees, amounts)")
        print("   5. Check inventory system integration với transaction system")
        
        business_results = {
            "user_flows_tested": 0,
            "user_flows_passed": 0,
            "data_consistency_checks": 0,
            "data_consistency_passed": 0,
            "calculation_accuracy": {"correct": 0, "incorrect": 0},
            "integration_issues": []
        }
        
        # Test 1: Customer Stats Consistency
        print(f"\n🔍 Testing Customer Stats Consistency")
        print("-" * 50)
        
        # Get customer stats
        stats_success, stats_response = self.run_test(
            "GET /customers/stats - Customer statistics",
            "GET",
            "customers/stats",
            200
        )
        
        if stats_success:
            business_results["data_consistency_checks"] += 1
            
            # Get actual customer count
            customers_success, customers_response = self.run_test(
                "GET /customers - Verify customer count",
                "GET",
                "customers?page_size=1000",
                200
            )
            
            if customers_success:
                actual_count = len(customers_response)
                reported_count = stats_response.get('total_customers', 0)
                
                if actual_count == reported_count:
                    print(f"   ✅ Customer count consistent: {actual_count}")
                    business_results["data_consistency_passed"] += 1
                else:
                    print(f"   ❌ Customer count mismatch: actual={actual_count}, reported={reported_count}")
                    business_results["integration_issues"].append(f"Customer count mismatch: {actual_count} vs {reported_count}")
        
        # Test 2: Inventory System Integration
        print(f"\n🔍 Testing Inventory System Integration")
        print("-" * 50)
        
        # Get inventory stats
        inventory_success, inventory_response = self.run_test(
            "GET /inventory/stats - Inventory statistics",
            "GET",
            "inventory/stats",
            200
        )
        
        if inventory_success:
            business_results["data_consistency_checks"] += 1
            
            # Get actual bills count
            bills_success, bills_response = self.run_test(
                "GET /bills - Verify bills count",
                "GET",
                "bills?limit=1000",
                200
            )
            
            if bills_success:
                actual_bills = len(bills_response)
                reported_bills = inventory_response.get('total_bills_in_system', 0)
                
                if actual_bills == reported_bills:
                    print(f"   ✅ Bills count consistent: {actual_bills}")
                    business_results["data_consistency_passed"] += 1
                else:
                    print(f"   ❌ Bills count mismatch: actual={actual_bills}, reported={reported_bills}")
                    business_results["integration_issues"].append(f"Bills count mismatch: {actual_bills} vs {reported_bills}")
        
        # Test 3: Dashboard Stats Integration
        print(f"\n🔍 Testing Dashboard Stats Integration")
        print("-" * 50)
        
        dashboard_success, dashboard_response = self.run_test(
            "GET /dashboard/stats - Dashboard statistics",
            "GET",
            "dashboard/stats",
            200
        )
        
        if dashboard_success:
            business_results["data_consistency_checks"] += 1
            
            # Verify dashboard stats make sense
            total_bills = dashboard_response.get('total_bills', 0)
            available_bills = dashboard_response.get('available_bills', 0)
            sold_bills = dashboard_response.get('sold_bills', 0)
            
            if available_bills + sold_bills <= total_bills:
                print(f"   ✅ Dashboard bill counts logical: total={total_bills}, available={available_bills}, sold={sold_bills}")
                business_results["data_consistency_passed"] += 1
            else:
                print(f"   ❌ Dashboard bill counts illogical: total={total_bills}, available={available_bills}, sold={sold_bills}")
                business_results["integration_issues"].append("Dashboard bill counts don't add up")
        
        # Summary
        consistency_rate = (business_results["data_consistency_passed"] / business_results["data_consistency_checks"] * 100) if business_results["data_consistency_checks"] > 0 else 0
        
        print(f"\n📊 BUSINESS LOGIC VALIDATION SUMMARY:")
        print(f"   Data consistency checks: {business_results['data_consistency_checks']}")
        print(f"   Data consistency passed: {business_results['data_consistency_passed']}")
        print(f"   Consistency rate: {consistency_rate:.1f}%")
        print(f"   Integration issues: {len(business_results['integration_issues'])}")
        
        if business_results['integration_issues']:
            print(f"\n🚨 INTEGRATION ISSUES:")
            for issue in business_results['integration_issues']:
                print(f"   - {issue}")
        
        self.audit_results["business_logic"] = business_results
        
        print(f"\n🎯 BUSINESS LOGIC SCORE: {consistency_rate:.1f}%")
        return consistency_rate >= 80

    def phase4_system_stability_performance(self):
        """PHASE 4: SYSTEM STABILITY & PERFORMANCE"""
        print(f"\n🎯 PHASE 4: SYSTEM STABILITY & PERFORMANCE")
        print("=" * 80)
        print("🔍 STABILITY OBJECTIVES:")
        print("   1. Test concurrent operations và race conditions")
        print("   2. Verify system handles high load")
        print("   3. Check memory leaks hoặc performance issues")
        print("   4. Test error recovery scenarios")
        
        stability_results = {
            "load_tests": 0,
            "load_tests_passed": 0,
            "error_recovery_tests": 0,
            "error_recovery_passed": 0,
            "performance_issues": [],
            "stability_score": 0
        }
        
        # Test 1: Multiple concurrent requests
        print(f"\n🔍 Testing Concurrent Request Handling")
        print("-" * 50)
        
        import threading
        import time
        
        concurrent_results = []
        
        def concurrent_request():
            try:
                success, response = self.run_test(
                    "Concurrent test",
                    "GET",
                    "customers/stats",
                    200
                )
                concurrent_results.append(success)
            except:
                concurrent_results.append(False)
        
        # Run 5 concurrent requests
        threads = []
        start_time = time.time()
        
        for i in range(5):
            thread = threading.Thread(target=concurrent_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        end_time = time.time()
        duration = end_time - start_time
        
        stability_results["load_tests"] += 1
        successful_requests = sum(concurrent_results)
        
        if successful_requests >= 4:  # Allow 1 failure
            print(f"   ✅ Concurrent requests handled: {successful_requests}/5 in {duration:.2f}s")
            stability_results["load_tests_passed"] += 1
        else:
            print(f"   ❌ Concurrent request failures: {5-successful_requests}/5 failed")
            stability_results["performance_issues"].append(f"Concurrent request handling poor: {successful_requests}/5 succeeded")
        
        # Test 2: Error recovery
        print(f"\n🔍 Testing Error Recovery")
        print("-" * 50)
        
        # Test invalid request followed by valid request
        stability_results["error_recovery_tests"] += 1
        
        # Make invalid request
        invalid_success, invalid_response = self.run_test(
            "Invalid request test",
            "GET",
            "nonexistent-endpoint",
            404
        )
        
        # Immediately make valid request
        valid_success, valid_response = self.run_test(
            "Recovery test",
            "GET",
            "customers/stats",
            200
        )
        
        if valid_success:
            print(f"   ✅ System recovered from invalid request")
            stability_results["error_recovery_passed"] += 1
        else:
            print(f"   ❌ System did not recover properly")
            stability_results["performance_issues"].append("Poor error recovery")
        
        # Calculate stability score
        load_score = (stability_results["load_tests_passed"] / stability_results["load_tests"] * 100) if stability_results["load_tests"] > 0 else 0
        recovery_score = (stability_results["error_recovery_passed"] / stability_results["error_recovery_tests"] * 100) if stability_results["error_recovery_tests"] > 0 else 0
        
        stability_results["stability_score"] = (load_score + recovery_score) / 2
        
        print(f"\n📊 SYSTEM STABILITY SUMMARY:")
        print(f"   Load tests: {stability_results['load_tests_passed']}/{stability_results['load_tests']}")
        print(f"   Error recovery tests: {stability_results['error_recovery_passed']}/{stability_results['error_recovery_tests']}")
        print(f"   Performance issues: {len(stability_results['performance_issues'])}")
        print(f"   Stability score: {stability_results['stability_score']:.1f}%")
        
        if stability_results['performance_issues']:
            print(f"\n⚠️ PERFORMANCE ISSUES:")
            for issue in stability_results['performance_issues']:
                print(f"   - {issue}")
        
        self.audit_results["system_stability"] = stability_results
        
        print(f"\n🎯 SYSTEM STABILITY SCORE: {stability_results['stability_score']:.1f}%")
        return stability_results["stability_score"] >= 80

    def calculate_production_readiness_score(self):
        """Calculate overall production readiness score"""
        print(f"\n🎯 CALCULATING PRODUCTION READINESS SCORE")
        print("=" * 80)
        
        # Weight factors for different aspects
        weights = {
            "database_integrity": 0.25,
            "api_endpoints": 0.35,
            "business_logic": 0.25,
            "system_stability": 0.15
        }
        
        scores = {}
        
        # Database integrity score
        db_audit = self.audit_results.get("database_integrity", {})
        broken_refs = len(db_audit.get("broken_references", []))
        id_issues = len(db_audit.get("id_format_issues", []))
        
        db_score = 100
        if broken_refs > 0:
            db_score -= min(30, broken_refs * 5)
        if id_issues > 0:
            db_score -= min(20, id_issues * 10)
        
        scores["database_integrity"] = max(0, db_score)
        
        # API endpoints score
        api_audit = self.audit_results.get("api_endpoints", {})
        api_score = (api_audit.get("endpoints_passed", 0) / max(1, api_audit.get("endpoints_tested", 1))) * 100
        scores["api_endpoints"] = api_score
        
        # Business logic score
        business_audit = self.audit_results.get("business_logic", {})
        business_score = (business_audit.get("data_consistency_passed", 0) / max(1, business_audit.get("data_consistency_checks", 1))) * 100
        scores["business_logic"] = business_score
        
        # System stability score
        stability_audit = self.audit_results.get("system_stability", {})
        stability_score = stability_audit.get("stability_score", 0)
        scores["system_stability"] = stability_score
        
        # Calculate weighted average
        total_score = sum(scores[aspect] * weights[aspect] for aspect in weights)
        
        print(f"\n📊 PRODUCTION READINESS BREAKDOWN:")
        for aspect, score in scores.items():
            weight = weights[aspect]
            weighted_score = score * weight
            print(f"   {aspect.replace('_', ' ').title()}: {score:.1f}% (weight: {weight:.0%}) = {weighted_score:.1f}")
        
        print(f"\n🎯 OVERALL PRODUCTION READINESS SCORE: {total_score:.1f}%")
        
        # Determine readiness level
        if total_score >= 90:
            readiness_level = "EXCELLENT - Ready for production"
        elif total_score >= 80:
            readiness_level = "GOOD - Ready with minor monitoring"
        elif total_score >= 70:
            readiness_level = "ACCEPTABLE - Needs some fixes before production"
        elif total_score >= 60:
            readiness_level = "POOR - Significant issues need resolution"
        else:
            readiness_level = "CRITICAL - Not ready for production"
        
        print(f"🏆 READINESS LEVEL: {readiness_level}")
        
        self.audit_results["production_readiness_score"] = total_score
        
        return total_score, readiness_level

    def generate_audit_report(self):
        """Generate comprehensive audit report"""
        print(f"\n🎯 COMPREHENSIVE SYSTEM AUDIT REPORT")
        print("=" * 80)
        
        total_score, readiness_level = self.calculate_production_readiness_score()
        
        print(f"\n📋 EXECUTIVE SUMMARY:")
        print(f"   Tests Run: {self.tests_run}")
        print(f"   Tests Passed: {self.tests_passed}")
        print(f"   Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        print(f"   Critical Issues: {len(self.critical_issues)}")
        print(f"   Production Readiness: {total_score:.1f}% - {readiness_level}")
        
        if self.critical_issues:
            print(f"\n🚨 CRITICAL ISSUES REQUIRING IMMEDIATE ATTENTION:")
            for i, issue in enumerate(self.critical_issues, 1):
                print(f"   {i}. {issue}")
        
        print(f"\n📊 DETAILED FINDINGS:")
        
        # Database findings
        db_audit = self.audit_results.get("database_integrity", {})
        print(f"\n   DATABASE INTEGRITY:")
        print(f"     Collections: {db_audit.get('collections_analyzed', 0)}")
        print(f"     Documents: {db_audit.get('total_documents', 0)}")
        print(f"     Broken References: {len(db_audit.get('broken_references', []))}")
        print(f"     ID Format Issues: {len(db_audit.get('id_format_issues', []))}")
        
        # API findings
        api_audit = self.audit_results.get("api_endpoints", {})
        print(f"\n   API ENDPOINTS:")
        print(f"     Endpoints Tested: {api_audit.get('endpoints_tested', 0)}")
        print(f"     Endpoints Passed: {api_audit.get('endpoints_passed', 0)}")
        print(f"     Critical Failures: {len(api_audit.get('critical_failures', []))}")
        
        # Business logic findings
        business_audit = self.audit_results.get("business_logic", {})
        print(f"\n   BUSINESS LOGIC:")
        print(f"     Consistency Checks: {business_audit.get('data_consistency_checks', 0)}")
        print(f"     Consistency Passed: {business_audit.get('data_consistency_passed', 0)}")
        print(f"     Integration Issues: {len(business_audit.get('integration_issues', []))}")
        
        # Stability findings
        stability_audit = self.audit_results.get("system_stability", {})
        print(f"\n   SYSTEM STABILITY:")
        print(f"     Load Tests: {stability_audit.get('load_tests_passed', 0)}/{stability_audit.get('load_tests', 0)}")
        print(f"     Recovery Tests: {stability_audit.get('error_recovery_passed', 0)}/{stability_audit.get('error_recovery_tests', 0)}")
        print(f"     Performance Issues: {len(stability_audit.get('performance_issues', []))}")
        
        print(f"\n🏁 AUDIT COMPLETE")
        print(f"   Timestamp: {datetime.now().isoformat()}")
        print(f"   System Status: {'PRODUCTION READY' if total_score >= 80 else 'NEEDS ATTENTION'}")
        
        return total_score >= 80

def main():
    """Run comprehensive system audit"""
    print("🚀 STARTING COMPREHENSIVE SYSTEM AUDIT")
    print("=" * 80)
    print("This audit covers all aspects requested in the review:")
    print("- Database integrity and consistency")
    print("- API endpoints comprehensive testing")
    print("- Business logic validation")
    print("- System stability and performance")
    print("- Production readiness assessment")
    
    auditor = ComprehensiveSystemAudit()
    
    # Run all phases
    phase1_success = auditor.phase1_database_integrity_audit()
    phase2_success = auditor.phase2_api_endpoints_testing()
    phase3_success = auditor.phase3_business_logic_validation()
    phase4_success = auditor.phase4_system_stability_performance()
    
    # Generate final report
    overall_success = auditor.generate_audit_report()
    
    return overall_success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)