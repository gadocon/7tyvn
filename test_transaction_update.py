#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from backend_test import FPTBillManagerAPITester

def main():
    print("🎯 TRANSACTION UPDATE OBJECTID SERIALIZATION FIX VERIFICATION")
    print("=" * 80)
    
    tester = FPTBillManagerAPITester()
    
    # Run the transaction update test
    success = tester.test_transaction_update_objectid_serialization_fix()
    
    print(f"\n{'='*80}")
    print(f"🏁 TRANSACTION UPDATE TEST SUMMARY")
    print(f"{'='*80}")
    print(f"📊 Tests Run: {tester.tests_run}")
    print(f"📊 Tests Passed: {tester.tests_passed}")
    print(f"📊 Success Rate: {(tester.tests_passed/tester.tests_run)*100:.1f}%" if tester.tests_run > 0 else "No tests run")
    
    if success:
        print(f"\n🎉 TRANSACTION UPDATE TEST PASSED!")
        print(f"✅ ObjectId serialization fix is working correctly")
        print(f"✅ No JSON serialization errors detected")
        print(f"✅ Transaction update endpoints are functional")
        return 0
    else:
        print(f"\n❌ TRANSACTION UPDATE TEST FAILED!")
        print(f"⚠️  ObjectId serialization issues detected")
        print(f"🚨 JSON serialization errors may be present")
        return 1

if __name__ == "__main__":
    sys.exit(main())