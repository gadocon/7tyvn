#!/usr/bin/env python3
"""
Data Standards & Prevention System
Purpose: Prevent future "loạn xạ" data creation with standardized functions
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any
from bson import ObjectId

class DataStandards:
    """Standardized data creation and validation functions"""
    
    @staticmethod
    def generate_standard_id() -> str:
        """Generate standardized UUID for all entities"""
        return str(uuid.uuid4())
    
    @staticmethod  
    def prepare_customer_data(customer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare customer data with standardized fields"""
        now = datetime.now(timezone.utc)
        
        return {
            "id": DataStandards.generate_standard_id(),
            "name": customer_data.get("name", ""),
            "phone": customer_data.get("phone", ""),
            "email": customer_data.get("email", ""),
            "address": customer_data.get("address", ""),
            "type": customer_data.get("type", "INDIVIDUAL"),
            "notes": customer_data.get("notes", ""),
            "is_active": True,
            "total_transactions": 0,
            "total_spent": 0.0,
            "total_profit_generated": 0.0,
            "tier": "BRONZE",
            "created_at": now,
            "updated_at": now
        }
    
    @staticmethod
    def prepare_credit_card_data(card_data: Dict[str, Any], customer_id: str) -> Dict[str, Any]:
        """Prepare credit card data with standardized fields"""
        now = datetime.now(timezone.utc)
        
        return {
            "id": DataStandards.generate_standard_id(),
            "customer_id": customer_id,  # MUST be valid customer UUID
            "card_number": card_data.get("card_number", ""),
            "card_holder_name": card_data.get("card_holder_name", ""),
            "bank_name": card_data.get("bank_name", ""),
            "card_type": card_data.get("card_type", "CREDIT"),
            "limit_amount": card_data.get("limit_amount", 0.0),
            "available_limit": card_data.get("available_limit", 0.0),
            "interest_rate": card_data.get("interest_rate", 0.0),
            "notes": card_data.get("notes", ""),
            "is_active": True,
            "created_at": now,
            "updated_at": now
        }
    
    @staticmethod
    def prepare_bill_data(bill_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare bill data with standardized fields"""
        now = datetime.now(timezone.utc)
        
        return {
            "id": DataStandards.generate_standard_id(),
            "bill_code": bill_data.get("bill_code", ""),
            "denomination": bill_data.get("denomination", 0),
            "serial_number": bill_data.get("serial_number", ""),
            "status": bill_data.get("status", "AVAILABLE"),
            "condition": bill_data.get("condition", "NEW"),
            "notes": bill_data.get("notes", ""),
            "created_at": now,
            "updated_at": now
        }
    
    @staticmethod
    def prepare_sale_data(sale_data: Dict[str, Any], customer_id: str, bill_id: str = None) -> Dict[str, Any]:
        """Prepare sale transaction data with standardized fields"""
        now = datetime.now(timezone.utc)
        
        return {
            "id": DataStandards.generate_standard_id(),
            "customer_id": customer_id,  # MUST be valid customer UUID
            "bill_id": bill_id,  # MUST be valid bill UUID if provided
            "transaction_type": sale_data.get("transaction_type", "BILL_SALE"),
            "total": sale_data.get("total", 0.0),
            "profit_value": sale_data.get("profit_value", 0.0),
            "profit_percentage": sale_data.get("profit_percentage", 0.0),
            "payment_method": sale_data.get("payment_method", "CASH"),
            "notes": sale_data.get("notes", ""),
            "status": "COMPLETED",
            "created_at": now,
            "updated_at": now
        }
    
    @staticmethod
    def prepare_credit_card_transaction_data(tx_data: Dict[str, Any], card_id: str) -> Dict[str, Any]:
        """Prepare credit card transaction data with standardized fields"""
        now = datetime.now(timezone.utc)
        
        return {
            "id": DataStandards.generate_standard_id(),  # UUID, not CC_* format
            "card_id": card_id,  # MUST be valid credit card UUID
            "transaction_type": tx_data.get("transaction_type", "DAO"),
            "amount": tx_data.get("amount", 0.0),
            "fee": tx_data.get("fee", 0.0),
            "profit_amount": tx_data.get("profit_amount", 0.0),
            "profit_pct": tx_data.get("profit_pct", 0.0),
            "payment_method": tx_data.get("payment_method", "POS"),
            "notes": tx_data.get("notes", ""),
            "status": "COMPLETED",
            "created_at": now,
            "updated_at": now
        }
    
    @staticmethod
    def validate_references(data: Dict[str, Any], db) -> Dict[str, Any]:
        """Validate all foreign key references before creation"""
        async def _validate():
            errors = []
            
            # Validate customer_id if present
            if "customer_id" in data:
                customer = await db.customers.find_one({"id": data["customer_id"]})
                if not customer:
                    errors.append(f"Invalid customer_id: {data['customer_id']}")
            
            # Validate card_id if present
            if "card_id" in data:
                card = await db.credit_cards.find_one({"id": data["card_id"]})
                if not card:
                    errors.append(f"Invalid card_id: {data['card_id']}")
            
            # Validate bill_id if present
            if "bill_id" in data:
                bill = await db.bills.find_one({"id": data["bill_id"]})
                if not bill:
                    errors.append(f"Invalid bill_id: {data['bill_id']}")
            
            return errors
        
        return _validate()
    
    @staticmethod
    def is_valid_uuid(uuid_string: str) -> bool:
        """Validate UUID format"""
        try:
            uuid.UUID(uuid_string)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def convert_objectid_to_string(doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert MongoDB ObjectId fields to strings for JSON serialization"""
        if isinstance(doc, dict):
            # Convert _id ObjectId to string and remove _id
            if '_id' in doc:
                if not doc.get('id'):  # Only set id if it doesn't exist
                    doc['id'] = str(doc['_id'])
                doc.pop('_id', None)
            
            # Recursively handle nested objects
            for key, value in doc.items():
                if isinstance(value, ObjectId):
                    doc[key] = str(value)
                elif isinstance(value, dict):
                    doc[key] = DataStandards.convert_objectid_to_string(value)
                elif isinstance(value, list):
                    doc[key] = [
                        DataStandards.convert_objectid_to_string(item) if isinstance(item, dict)
                        else str(item) if isinstance(item, ObjectId)
                        else item
                        for item in value
                    ]
        
        return doc

# Validation Rules
VALIDATION_RULES = {
    "customer": {
        "required_fields": ["name", "phone", "type"],
        "valid_types": ["INDIVIDUAL", "AGENT", "BUSINESS"],
        "valid_tiers": ["BRONZE", "SILVER", "GOLD", "PLATINUM"]
    },
    "credit_card": {
        "required_fields": ["customer_id", "card_number", "bank_name"],
        "valid_types": ["CREDIT", "DEBIT"],
        "min_limit": 0,
        "max_limit": 1000000000
    },
    "bill": {
        "required_fields": ["bill_code", "denomination"],
        "valid_statuses": ["AVAILABLE", "SOLD", "DAMAGED", "RESERVED"],
        "valid_conditions": ["NEW", "GOOD", "FAIR", "POOR"],
        "valid_denominations": [500000, 200000, 100000, 50000, 20000, 10000]
    },
    "transaction": {
        "required_fields": ["customer_id", "total", "transaction_type"],
        "valid_types": ["BILL_SALE", "CREDIT_DAO", "OTHER"],
        "valid_payment_methods": ["CASH", "BANK_TRANSFER", "POS", "OTHER"],
        "min_amount": 0,
        "max_amount": 1000000000
    }
}

def validate_data(data: Dict[str, Any], entity_type: str) -> list:
    """Validate data against business rules"""
    errors = []
    rules = VALIDATION_RULES.get(entity_type, {})
    
    # Check required fields
    required_fields = rules.get("required_fields", [])
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    # Entity-specific validations
    if entity_type == "customer":
        if data.get("type") not in rules["valid_types"]:
            errors.append(f"Invalid customer type: {data.get('type')}")
        
        phone = data.get("phone", "")
        if phone and not phone.startswith("0"):
            errors.append("Phone number must start with 0")
    
    elif entity_type == "credit_card":
        if not DataStandards.is_valid_uuid(data.get("customer_id", "")):
            errors.append("Invalid customer_id format - must be UUID")
        
        limit_amount = data.get("limit_amount", 0)
        if limit_amount < rules["min_limit"] or limit_amount > rules["max_limit"]:
            errors.append(f"Limit amount must be between {rules['min_limit']} and {rules['max_limit']}")
    
    elif entity_type == "bill":
        if data.get("status") not in rules["valid_statuses"]:
            errors.append(f"Invalid bill status: {data.get('status')}")
        
        if data.get("denomination") not in rules["valid_denominations"]:
            errors.append(f"Invalid denomination: {data.get('denomination')}")
    
    elif entity_type == "transaction":
        if not DataStandards.is_valid_uuid(data.get("customer_id", "")):
            errors.append("Invalid customer_id format - must be UUID")
        
        total = data.get("total", 0)
        if total < rules["min_amount"] or total > rules["max_amount"]:
            errors.append(f"Transaction amount must be between {rules['min_amount']} and {rules['max_amount']}")
    
    return errors

# Usage Examples:

# ✅ CORRECT - Standardized customer creation
"""
customer_data = {
    "name": "Nguyễn Văn A",
    "phone": "0901234567",
    "email": "nguyenvana@example.com",
    "type": "INDIVIDUAL"
}

# Validate first
errors = validate_data(customer_data, "customer")
if errors:
    raise ValueError(f"Validation errors: {errors}")

# Prepare with standards
standard_customer = DataStandards.prepare_customer_data(customer_data)

# Insert to database
result = await db.customers.insert_one(standard_customer)
"""

# ❌ WRONG - Direct insertion without standards
"""
# This will create inconsistent data!
await db.customers.insert_one({
    "name": "Test Customer",
    "phone": "123456789"
    # Missing: id, created_at, updated_at, type, tier, etc.
})
"""