#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend_test import FPTBillManagerAPITester

def main():
    """Run only the credit card transaction system tests"""
    print("🚀 Starting Credit Card Transaction System Tests...")
    print("=" * 60)
    
    tester = FPTBillManagerAPITester()
    
    # Run the credit card transaction tests
    success = tester.run_credit_card_tests_only()
    
    if success:
        print("\n🎉 All Credit Card Transaction Tests Passed!")
        return 0
    else:
        print("\n⚠️  Some Credit Card Transaction Tests Failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())