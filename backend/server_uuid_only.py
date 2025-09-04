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