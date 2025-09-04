#!/usr/bin/env python3
"""
UUID Utilities for CRM 7ty.vn UUID-Only System
Clean UUID generation and processing utilities
"""

import uuid
import re
from typing import Dict, Any, Optional
from datetime import datetime, timezone

def generate_uuid() -> str:
    """Generate a clean UUID string"""
    return str(uuid.uuid4())

def is_valid_uuid(uuid_string: str) -> bool:
    """Check if string is a valid UUID format"""
    if not uuid_string or not isinstance(uuid_string, str):
        return False
    
    # UUID format: 8-4-4-4-12 characters
    uuid_pattern = re.compile(
        r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
        re.IGNORECASE
    )
    
    return bool(uuid_pattern.match(uuid_string))

class UUIDProcessor:
    """UUID-only document processor for MongoDB operations"""
    
    def prepare_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare document for insertion with UUID"""
        if not doc.get('id'):
            doc['id'] = generate_uuid()
        
        # Ensure timestamps
        now = datetime.now(timezone.utc)
        if not doc.get('created_at'):
            doc['created_at'] = now
        if not doc.get('updated_at'):
            doc['updated_at'] = now
            
        return doc
    
    def clean_response(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Clean MongoDB document for API response"""
        if not doc:
            return {}
        
        # Remove MongoDB _id field
        cleaned = {k: v for k, v in doc.items() if k != '_id'}
        
        # Ensure datetime objects are properly formatted
        for key, value in cleaned.items():
            if isinstance(value, datetime):
                cleaned[key] = value
        
        return cleaned

# Global processor instance
uuid_processor = UUIDProcessor()