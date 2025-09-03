#!/usr/bin/env python3

import sys
import os
sys.path.append('/app')

from backend_test import FPTBillManagerAPITester

def main():
    """Create test accounts with different roles for permission testing"""
    print("🚀 Creating Test Accounts for Role-Based Permission Testing")
    print("=" * 70)
    
    tester = FPTBillManagerAPITester()
    
    # Run the account creation test
    success = tester.test_create_role_based_test_accounts()
    
    if success:
        print("\n🎉 Test account creation completed successfully!")
        return 0
    else:
        print("\n❌ Test account creation had some issues")
        return 1

if __name__ == "__main__":
    exit(main())