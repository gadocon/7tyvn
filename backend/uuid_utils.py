"""
UUID Utilities - Clean UUID-only system utilities
Eliminates all ObjectId handling and dual lookup complexity
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List

def generate_uuid() -> str:
    """Generate clean UUID string for all entities"""
    return str(uuid.uuid4())

def is_valid_uuid(uuid_string: str) -> bool:
    """Validate UUID format - no ObjectId checking"""
    try:
        uuid.UUID(uuid_string)
        return True
    except (ValueError, TypeError):
        return False

def is_valid_composite_bill_id(bill_id: str) -> bool:
    """Check if string is valid composite bill_id format (customer_code + MMYY)"""
    try:
        # Should be at least customer_code (10+ chars) + MMYY (4 chars) = 14+ chars
        if len(bill_id) < 14:
            return False
        
        # Extract MMYY from end (last 4 characters)
        mmyy = bill_id[-4:]
        
        # Check if MMYY is numeric
        if not mmyy.isdigit():
            return False
        
        # Extract MM and YY
        mm = int(mmyy[:2])
        yy = int(mmyy[2:])
        
        # Validate month (01-12)
        if mm < 1 or mm > 12:
            return False
        
        # Validate year (basic range check, e.g., 23-30 for 2023-2030)
        if yy < 23 or yy > 30:
            return False
        
        return True
        
    except (ValueError, TypeError):
        return False

def generate_composite_bill_id(customer_code: str, billing_cycle: str) -> str:
    """Generate composite bill_id from customer_code and billing_cycle"""
    try:
        # Extract month/year from billing_cycle (e.g., "08/2025" -> "0825")
        if "/" in billing_cycle:
            month, year = billing_cycle.split("/")
            mmyy = f"{month.zfill(2)}{year[-2:]}"  # MM + YY
        else:
            # Fallback to current date if cycle format is unexpected
            from datetime import datetime
            now = datetime.now()
            mmyy = f"{now.month:02d}{str(now.year)[-2:]}"
        
        return f"{customer_code}{mmyy}"
        
    except Exception:
        # Fallback to current date
        from datetime import datetime
        now = datetime.now()
        mmyy = f"{now.month:02d}{str(now.year)[-2:]}"
        return f"{customer_code}{mmyy}"

class UUIDProcessor:
    """Clean UUID processing - NO ObjectId handling"""
    
    @staticmethod
    def prepare_document(data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare document with UUID and timestamps"""
        now = datetime.now(timezone.utc)
        
        # Force UUID if no id exists
        if 'id' not in data or not data['id']:
            data['id'] = generate_uuid()
        
        # Validate UUID format
        if not is_valid_uuid(data['id']):
            raise ValueError(f"Invalid UUID format: {data['id']}")
        
        # Add timestamps
        if 'created_at' not in data:
            data['created_at'] = now
        data['updated_at'] = now
        
        # Remove any ObjectId references
        data.pop('_id', None)
        
        return data
    
    @staticmethod
    def clean_response(document: Dict[str, Any]) -> Dict[str, Any]:
        """Clean response document - remove ObjectId, ensure UUID"""
        if not document:
            return document
            
        # Ensure UUID id exists
        if 'id' not in document and '_id' in document:
            # Last resort: convert ObjectId to UUID (migration scenario)
            document['id'] = generate_uuid()
            print(f"⚠️ WARNING: Found ObjectId, generated new UUID: {document['id']}")
        
        # Remove ObjectId from response
        document.pop('_id', None)
        
        # Validate UUID format
        if 'id' in document and not is_valid_uuid(document['id']):
            raise ValueError(f"Response contains invalid UUID: {document['id']}")
        
        return document
    
    @staticmethod
    def clean_list_response(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Clean list of documents"""
        return [UUIDProcessor.clean_response(doc) for doc in documents]
    
    @staticmethod
    def validate_foreign_key(entity_id: str, field_name: str = "id") -> str:
        """Validate foreign key is proper UUID"""
        if not entity_id:
            raise ValueError(f"Missing {field_name}")
        
        if not is_valid_uuid(entity_id):
            raise ValueError(f"Invalid UUID format for {field_name}: {entity_id}")
        
        return entity_id

# Global UUID processor instance
uuid_processor = UUIDProcessor()