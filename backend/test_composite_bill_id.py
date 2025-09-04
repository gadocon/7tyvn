#!/usr/bin/env python3
"""
Test script for composite bill_id functions
"""

from uuid_utils import is_valid_composite_bill_id, generate_composite_bill_id

def test_composite_bill_id():
    """Test composite bill_id validation and generation"""
    
    print("Testing is_valid_composite_bill_id function:")
    
    # Valid cases
    valid_cases = [
        "CUSTOMER12340825",  # customer_code + 0825 (Aug 2025)
        "ABCDEFGHIJ1224",    # 10 char customer_code + 1224 (Dec 2024)
        "LONGCUSTOMERCODE0125",  # longer customer_code + 0125 (Jan 2025)
    ]
    
    for case in valid_cases:
        result = is_valid_composite_bill_id(case)
        print(f"  {case}: {result} (should be True)")
    
    # Invalid cases
    invalid_cases = [
        "SHORT12",           # too short
        "CUSTOMER1234",      # no MMYY
        "CUSTOMER123413",    # invalid month (13)
        "CUSTOMER123400",    # invalid month (00)
        "CUSTOMER123422",    # invalid year (22, too old)
        "CUSTOMER123431",    # invalid year (31, too far)
        "CUSTOMER1234AB",    # non-numeric MMYY
        "",                  # empty string
    ]
    
    for case in invalid_cases:
        result = is_valid_composite_bill_id(case)
        print(f"  {case}: {result} (should be False)")
    
    print("\nTesting generate_composite_bill_id function:")
    
    # Test cases
    test_cases = [
        ("CUSTOMER1234", "08/2025"),
        ("ABCDEFGHIJ", "12/2024"),
        ("SHORTCODE", "01/2025"),
        ("CUSTOMER1234", "invalid_format"),  # Should fallback to current date
    ]
    
    for customer_code, billing_cycle in test_cases:
        result = generate_composite_bill_id(customer_code, billing_cycle)
        is_valid = is_valid_composite_bill_id(result)
        print(f"  generate_composite_bill_id('{customer_code}', '{billing_cycle}') = '{result}' (valid: {is_valid})")

if __name__ == "__main__":
    test_composite_bill_id()