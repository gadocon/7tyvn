#!/usr/bin/env python3
"""
CRM 7ty.vn Backend - UUID-Only System (v2.0)
Complete elimination of ObjectId/UUID dual system complexity
Clean architecture with UUID-only entity identification
"""

import os
import sys
import asyncio
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from enum import Enum
import uuid

# FastAPI imports
from fastapi import FastAPI, HTTPException, status, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Database imports
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import DuplicateKeyError

# Pydantic imports
from pydantic import BaseModel, Field, validator

# UUID utilities
from uuid_utils import generate_uuid, is_valid_uuid, uuid_processor

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================================
# PYDANTIC MODELS - UUID ONLY SYSTEM
# ========================================

class CustomerType(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    AGENT = "AGENT"
    BUSINESS = "BUSINESS"

class CustomerTier(str, Enum):
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"

class BillStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    SOLD = "SOLD"
    CROSSED = "CROSSED"
    PENDING = "PENDING"

class InventoryStatus(str, Enum):
    IN_INVENTORY = "IN_INVENTORY"
    NOT_IN_INVENTORY = "NOT_IN_INVENTORY"
    SOLD_FROM_INVENTORY = "SOLD_FROM_INVENTORY"

# Customer Models
class CustomerBase(BaseModel):
    name: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    type: CustomerType = CustomerType.INDIVIDUAL
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    type: Optional[CustomerType] = None
    notes: Optional[str] = None

class Customer(CustomerBase):
    id: str = Field(default_factory=generate_uuid)
    tier: CustomerTier = CustomerTier.BRONZE
    total_transactions: int = 0
    total_spent: float = 0.0
    total_profit_generated: float = 0.0
    total_cards: int = 0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Bill Models  
class BillBase(BaseModel):
    customer_code: str
    customer_name: str
    phone: str
    address: str
    amount: float
    cycle: str
    gateway: str
    provider_region: str
    due_date: str

class BillCreate(BillBase):
    pass

class BillUpdate(BaseModel):
    customer_code: Optional[str] = None
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    amount: Optional[float] = None
    cycle: Optional[str] = None
    gateway: Optional[str] = None
    provider_region: Optional[str] = None
    due_date: Optional[str] = None
    status: Optional[BillStatus] = None

class Bill(BillBase):
    id: str = Field(default_factory=generate_uuid)
    status: BillStatus = BillStatus.AVAILABLE
    inventory_status: InventoryStatus = InventoryStatus.NOT_IN_INVENTORY
    is_in_inventory: bool = False
    added_to_inventory_at: Optional[datetime] = None
    added_by_user: Optional[str] = None
    inventory_note: Optional[str] = None
    last_checked_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Credit Card Models
class CardType(str, Enum):
    VISA = "VISA"
    MASTERCARD = "MASTERCARD"
    JCB = "JCB"
    AMEX = "AMEX"

class CardStatus(str, Enum):
    CAN_DAO = "Cần đáo"
    DA_DAO = "Đã đáo"
    CHUA_DEN_HAN = "Chưa đến hạn"
    QUA_HAN = "Quá Hạn"

class CreditCardBase(BaseModel):
    customer_id: str  # UUID only
    card_number: str
    cardholder_name: str
    bank_name: str
    card_type: CardType = CardType.VISA
    expiry_date: str
    ccv: str
    statement_date: int
    payment_due_date: int
    credit_limit: float
    status: CardStatus = CardStatus.CAN_DAO
    notes: Optional[str] = None
    
    @validator('customer_id')
    def validate_customer_id(cls, v):
        if not is_valid_uuid(v):
            raise ValueError('customer_id must be valid UUID')
        return v

class CreditCardCreate(CreditCardBase):
    pass

class CreditCardUpdate(BaseModel):
    card_number: Optional[str] = None
    cardholder_name: Optional[str] = None
    bank_name: Optional[str] = None
    card_type: Optional[CardType] = None
    expiry_date: Optional[str] = None
    ccv: Optional[str] = None
    statement_date: Optional[int] = None
    payment_due_date: Optional[int] = None
    credit_limit: Optional[float] = None
    status: Optional[CardStatus] = None
    notes: Optional[str] = None

class CreditCard(CreditCardBase):
    id: str = Field(default_factory=generate_uuid)
    customer_name: Optional[str] = None  # Denormalized
    current_cycle_month: Optional[str] = None
    last_payment_date: Optional[datetime] = None
    cycle_payment_count: int = 0
    total_cycles: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Sale Models
class SaleBase(BaseModel):
    customer_id: str  # UUID only
    bill_ids: List[str]  # UUID only
    profit_pct: float
    notes: Optional[str] = None
    
    @validator('customer_id')
    def validate_customer_id(cls, v):
        if not is_valid_uuid(v):
            raise ValueError('customer_id must be valid UUID')
        return v
    
    @validator('bill_ids')
    def validate_bill_ids(cls, v):
        for bill_id in v:
            if not is_valid_uuid(bill_id):
                raise ValueError(f'bill_id must be valid UUID: {bill_id}')
        return v

class SaleCreate(SaleBase):
    pass

class Sale(SaleBase):
    id: str = Field(default_factory=generate_uuid)
    transaction_type: str = "ELECTRIC_BILL"
    total: float = 0.0
    profit_value: float = 0.0
    payback: float = 0.0
    payment_method: str = "CASH"
    status: str = "COMPLETED"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# ========================================
# DATABASE CONNECTION - UUID OPTIMIZED
# ========================================

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/test_database')
client = AsyncIOMotorClient(MONGO_URL)
db = client.get_default_database()

async def ensure_uuid_indexes():
    """Create UUID-optimized indexes"""
    try:
        # UUID indexes for fast lookups
        await db.customers.create_index("id", unique=True)
        await db.bills.create_index("id", unique=True)
        await db.credit_cards.create_index("id", unique=True)
        await db.sales.create_index("id", unique=True)
        
        # Foreign key indexes
        await db.credit_cards.create_index("customer_id")
        await db.sales.create_index("customer_id")
        
        # Business logic indexes
        await db.bills.create_index("status")
        await db.bills.create_index("is_in_inventory")
        await db.customers.create_index("phone")
        
        logger.info("✅ UUID indexes created successfully")
    except Exception as e:
        logger.error(f"❌ Error creating indexes: {e}")

# ========================================
# FASTAPI APPLICATION SETUP
# ========================================

app = FastAPI(
    title="CRM 7ty.vn - UUID Only System",
    description="Clean UUID-only CRM system eliminating ObjectId complexity",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup event
@app.on_event("startup")
async def startup_event():
    await ensure_uuid_indexes()
    logger.info("🚀 CRM 7ty.vn UUID-Only System Started")

# Health check
@app.get("/")
async def root():
    return {
        "message": "CRM 7ty.vn UUID-Only System",
        "version": "2.0.0",
        "status": "running",
        "architecture": "uuid_only"
    }

# ========================================
# CUSTOMERS API - UUID ONLY
# ========================================

@app.post("/api/customers", response_model=Customer)
async def create_customer(customer_data: CustomerCreate):
    """Create customer with UUID only - NO ObjectId handling"""
    try:
        # Prepare document with UUID
        customer_dict = customer_data.dict()
        customer_dict = uuid_processor.prepare_document(customer_dict)
        
        # Insert to database
        result = await db.customers.insert_one(customer_dict)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create customer")
        
        # Return clean response
        created_customer = await db.customers.find_one({"id": customer_dict["id"]})
        return Customer(**uuid_processor.clean_response(created_customer))
        
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Customer ID already exists")
    except Exception as e:
        logger.error(f"Error creating customer: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers", response_model=List[Customer])
async def get_customers(skip: int = 0, limit: int = 100):
    """Get all customers - UUID only responses"""
    try:
        cursor = db.customers.find({}).skip(skip).limit(limit).sort("created_at", -1)
        customers = await cursor.to_list(length=limit)
        
        cleaned_customers = [uuid_processor.clean_response(customer) for customer in customers]
        return [Customer(**customer) for customer in cleaned_customers]
        
    except Exception as e:
        logger.error(f"Error fetching customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    """Get customer by UUID only - NO ObjectId fallback"""
    try:
        # Validate UUID format
        if not is_valid_uuid(customer_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Single lookup - no dual strategy
        customer = await db.customers.find_one({"id": customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return Customer(**uuid_processor.clean_response(customer))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer {customer_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer_data: CustomerUpdate):
    """Update customer by UUID only - NO ObjectId handling"""
    try:
        # Validate UUID format
        if not is_valid_uuid(customer_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Check if customer exists
        existing_customer = await db.customers.find_one({"id": customer_id})
        if not existing_customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Prepare update data
        update_data = customer_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            await db.customers.update_one({"id": customer_id}, {"$set": update_data})
        
        # Return updated customer
        updated_customer = await db.customers.find_one({"id": customer_id})
        return Customer(**uuid_processor.clean_response(updated_customer))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating customer {customer_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/customers/{customer_id}")
async def delete_customer(customer_id: str):
    """Delete customer by UUID only with cascade deletion"""
    try:
        # Validate UUID format
        if not is_valid_uuid(customer_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Check if customer exists
        customer = await db.customers.find_one({"id": customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Cascade delete related data - UUID only references
        await db.credit_cards.delete_many({"customer_id": customer_id})
        await db.sales.delete_many({"customer_id": customer_id})
        
        # Delete customer
        result = await db.customers.delete_one({"id": customer_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete customer")
        
        return {"success": True, "message": "Customer deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting customer {customer_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# BILLS API - UUID ONLY WITH UNIFIED INVENTORY
# ========================================

@app.post("/api/bills", response_model=Bill)
async def create_bill(bill_data: BillCreate):
    """Create bill with UUID only"""
    try:
        # Prepare document with UUID
        bill_dict = bill_data.dict()
        bill_dict = uuid_processor.prepare_document(bill_dict)
        
        # Insert to database
        result = await db.bills.insert_one(bill_dict)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create bill")
        
        # Return clean response
        created_bill = await db.bills.find_one({"id": bill_dict["id"]})
        return Bill(**uuid_processor.clean_response(created_bill))
        
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="Bill ID already exists")
    except Exception as e:
        logger.error(f"Error creating bill: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bills", response_model=List[Bill])
async def get_bills(
    skip: int = 0, 
    limit: int = 100,
    status: Optional[BillStatus] = None,
    is_in_inventory: Optional[bool] = None
):
    """Get bills with optional filtering - UUID only"""
    try:
        # Build filter
        filter_dict = {}
        if status:
            filter_dict["status"] = status
        if is_in_inventory is not None:
            filter_dict["is_in_inventory"] = is_in_inventory
        
        # Query bills
        cursor = db.bills.find(filter_dict).skip(skip).limit(limit).sort("created_at", -1)
        bills = await cursor.to_list(length=limit)
        
        # Clean responses
        cleaned_bills = [uuid_processor.clean_response(bill) for bill in bills]
        return [Bill(**bill) for bill in cleaned_bills]
        
    except Exception as e:
        logger.error(f"Error fetching bills: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/bills/{bill_id}", response_model=Bill)
async def get_bill(bill_id: str):
    """Get bill by UUID only"""
    try:
        # Validate UUID format
        if not is_valid_uuid(bill_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Single lookup - no dual strategy
        bill = await db.bills.find_one({"id": bill_id})
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        
        return Bill(**uuid_processor.clean_response(bill))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching bill {bill_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/bills/{bill_id}", response_model=Bill)
async def update_bill(bill_id: str, bill_data: BillUpdate):
    """Update bill by UUID only"""
    try:
        # Validate UUID format
        if not is_valid_uuid(bill_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Check if bill exists
        existing_bill = await db.bills.find_one({"id": bill_id})
        if not existing_bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        
        # Prepare update data
        update_data = bill_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            await db.bills.update_one({"id": bill_id}, {"$set": update_data})
        
        # Return updated bill
        updated_bill = await db.bills.find_one({"id": bill_id})
        return Bill(**uuid_processor.clean_response(updated_bill))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating bill {bill_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/bills/{bill_id}")
async def delete_bill(bill_id: str):
    """Delete bill by UUID only"""
    try:
        # Validate UUID format
        if not is_valid_uuid(bill_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Check if bill exists
        bill = await db.bills.find_one({"id": bill_id})
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        
        # Check if bill is referenced in any sales
        sales_using_bill = await db.sales.find_one({"bill_ids": bill_id})
        if sales_using_bill:
            raise HTTPException(
                status_code=400,
                detail="Cannot delete bill - it is referenced in sales transactions"
            )
        
        # Delete bill
        result = await db.bills.delete_one({"id": bill_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete bill")
        
        return {"success": True, "message": "Bill deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting bill {bill_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# INVENTORY API - UNIFIED WITH BILLS
# ========================================

@app.get("/api/inventory", response_model=List[Bill])
async def get_inventory(
    skip: int = 0,
    limit: int = 100, 
    status: Optional[BillStatus] = None
):
    """Get inventory items (bills marked as in_inventory) - UUID only"""
    try:
        # Build filter for inventory items
        filter_dict = {"is_in_inventory": True}
        if status:
            filter_dict["status"] = status
        
        # Query bills in inventory
        cursor = db.bills.find(filter_dict).skip(skip).limit(limit).sort("added_to_inventory_at", -1)
        bills = await cursor.to_list(length=limit)
        
        # Clean responses
        cleaned_bills = [uuid_processor.clean_response(bill) for bill in bills]
        return [Bill(**bill) for bill in cleaned_bills]
        
    except Exception as e:
        logger.error(f"Error fetching inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/inventory/add/{bill_id}")
async def add_to_inventory(bill_id: str, note: Optional[str] = None):
    """Add bill to inventory - UUID only"""
    try:
        # Validate UUID format
        if not is_valid_uuid(bill_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Check if bill exists and is available
        bill = await db.bills.find_one({"id": bill_id})
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        
        if bill.get("is_in_inventory"):
            raise HTTPException(status_code=400, detail="Bill already in inventory")
        
        # Add to inventory
        update_data = {
            "is_in_inventory": True,
            "inventory_status": InventoryStatus.IN_INVENTORY,
            "added_to_inventory_at": datetime.now(timezone.utc),
            "inventory_note": note,
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.bills.update_one({"id": bill_id}, {"$set": update_data})
        
        return {"success": True, "message": "Bill added to inventory successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding bill {bill_id} to inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/inventory/remove/{bill_id}")
async def remove_from_inventory(bill_id: str):
    """Remove bill from inventory - UUID only"""
    try:
        # Validate UUID format
        if not is_valid_uuid(bill_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Check if bill exists and is in inventory
        bill = await db.bills.find_one({"id": bill_id})
        if not bill:
            raise HTTPException(status_code=404, detail="Bill not found")
        
        if not bill.get("is_in_inventory"):
            raise HTTPException(status_code=400, detail="Bill not in inventory")
        
        # Remove from inventory
        update_data = {
            "is_in_inventory": False,
            "inventory_status": InventoryStatus.NOT_IN_INVENTORY,
            "added_to_inventory_at": None,
            "inventory_note": None,
            "updated_at": datetime.now(timezone.utc)
        }
        
        await db.bills.update_one({"id": bill_id}, {"$set": update_data})
        
        return {"success": True, "message": "Bill removed from inventory successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error removing bill {bill_id} from inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))