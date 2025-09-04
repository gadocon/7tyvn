"""
UUID Utilities - Clean UUID-only system utilities
Eliminates all ObjectId handling and dual lookup complexity
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from bson import ObjectId

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