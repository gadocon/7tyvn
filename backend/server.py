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
from datetime import datetime, timezone, timedelta, date
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
from pydantic import BaseModel, Field, validator, EmailStr

# Authentication imports
from passlib.context import CryptContext
import jwt
from datetime import timedelta

# UUID utilities
from uuid_utils import generate_uuid, is_valid_uuid, uuid_processor, is_valid_composite_bill_id, generate_composite_bill_id

# HTTP client for external API calls
import aiohttp
import asyncio

# ========================================
# AUTHENTICATION UTILITY FUNCTIONS
# ========================================

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ========================================
# AUTHENTICATION CONSTANTS
# ========================================

SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here-change-in-production')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# ========================================
# AUTHENTICATION MODELS
# ========================================

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    MANAGER = "MANAGER"
    USER = "USER"

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    phone: Optional[str] = Field(None, min_length=10, max_length=15)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=100)
    role: UserRole = UserRole.USER

class UserLogin(BaseModel):
    login: str  # Can be username, email, or phone
    password: str

class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str] = None
    phone: Optional[str] = None
    full_name: Optional[str] = None
    role: UserRole
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

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
    # DAO specific stats
    total_dao_amount: float = 0.0
    total_dao_transactions: int = 0
    total_dao_profit: float = 0.0
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Bill Models  
class BillBase(BaseModel):
    customer_code: str
    customer_name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    amount: Optional[float] = 0
    cycle: Optional[str] = None
    gateway: Optional[str] = None
    provider_region: Optional[str] = None
    due_date: Optional[str] = None

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
    statement_date: int  # Day of month for statement (1-31)
    payment_due_date: int  # Day of month for payment due (1-31)
    credit_limit: float
    # CRITICAL BUSINESS LOGIC FIELDS:
    available_credit: Optional[float] = None  # Calculated field
    current_balance: float = 0.0  # Current outstanding balance
    last_dao_date: Optional[datetime] = None  # Last DAO transaction date
    next_due_date: Optional[str] = None  # Next actual payment due date (YYYY-MM-DD)
    days_until_due: Optional[int] = None  # Calculated field
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
            if not is_valid_composite_bill_id(bill_id):
                raise ValueError(f'bill_id must be valid composite format (customer_code+MMYY): {bill_id}')
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

MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(MONGO_URL)
db = client.crm_7ty_vn  # Use crm_7ty_vn database where user exists

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

def calculate_next_due_date(statement_date: int, payment_due_date: int) -> str:
    """Calculate next payment due date based on statement date and payment due date"""
    today = datetime.now(timezone.utc).date()
    current_month = today.month
    current_year = today.year
    
    # If we haven't passed this month's due date, use this month
    if today.day <= payment_due_date:
        due_date = date(current_year, current_month, payment_due_date)
    else:
        # Use next month's due date
        if current_month == 12:
            due_date = date(current_year + 1, 1, payment_due_date)
        else:
            due_date = date(current_year, current_month + 1, payment_due_date)
    
    return due_date.isoformat()

def calculate_card_status(current_balance: float, next_due_date: str, last_dao_date: datetime = None) -> CardStatus:
    """Calculate card status based on business logic"""
    today = datetime.now(timezone.utc).date()
    
    # Parse next due date
    try:
        due_date = datetime.fromisoformat(next_due_date).date()
        days_until_due = (due_date - today).days
    except:
        days_until_due = 0
    
    # Business Logic for Card Status:
    if current_balance <= 0:
        return CardStatus.CHUA_DEN_HAN  # No balance, not due yet
    elif days_until_due > 3:
        return CardStatus.CAN_DAO  # More than 3 days until due, can DAO
    elif days_until_due >= 0:
        return CardStatus.CAN_DAO  # Due soon but not overdue, can still DAO
    else:
        return CardStatus.QUA_HAN  # Overdue, need immediate attention

def update_card_after_dao(card_dict: dict, dao_amount: float) -> dict:
    """Update card fields after DAO transaction"""
    # Update current balance (increase by DAO amount)
    card_dict["current_balance"] = card_dict.get("current_balance", 0) + dao_amount
    
    # Update available credit
    card_dict["available_credit"] = card_dict.get("credit_limit", 0) - card_dict["current_balance"]
    
    # Update last DAO date
    card_dict["last_dao_date"] = datetime.now(timezone.utc)
    
    # Calculate next due date if not set
    if not card_dict.get("next_due_date"):
        card_dict["next_due_date"] = calculate_next_due_date(
            card_dict.get("statement_date", 5), 
            card_dict.get("payment_due_date", 15)
        )
    
    # Calculate and update status
    card_dict["status"] = calculate_card_status(
        card_dict["current_balance"], 
        card_dict["next_due_date"],
        card_dict["last_dao_date"]
    ).value  # Get enum value
    
    # Calculate days until due
    try:
        due_date = datetime.fromisoformat(card_dict["next_due_date"]).date()
        today = datetime.now(timezone.utc).date()
        card_dict["days_until_due"] = (due_date - today).days
    except:
        card_dict["days_until_due"] = 0
    
    return card_dict

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

@app.get("/api/customers/stats")
async def get_customers_stats():
    """Customer stats for dashboard"""
    try:
        total_customers = await db.customers.count_documents({})
        active_customers = await db.customers.count_documents({"is_active": True})
        
        return {
            "total": total_customers,
            "active": active_customers,
            "inactive": total_customers - active_customers,
            "this_month": 0  # Placeholder
        }
    except Exception as e:
        logger.error(f"Error fetching customer stats: {e}")
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
        # Validate composite bill_id format
        if not is_valid_composite_bill_id(bill_id):
            raise HTTPException(status_code=400, detail="Invalid composite bill_id format")
        
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
        # Validate composite bill_id format
        if not is_valid_composite_bill_id(bill_id):
            raise HTTPException(status_code=400, detail="Invalid composite bill_id format")
        
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
        # Validate composite bill_id format
        if not is_valid_composite_bill_id(bill_id):
            raise HTTPException(status_code=400, detail="Invalid composite bill_id format")
        
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
        
        # Clean responses - bypass UUID processor for composite bill_ids
        cleaned_bills = []
        for bill in bills:
            # Remove ObjectId _id field if present
            bill_dict = dict(bill)
            bill_dict.pop("_id", None)
            cleaned_bills.append(bill_dict)
        
        return [Bill(**bill) for bill in cleaned_bills]
        
    except Exception as e:
        logger.error(f"Error fetching inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/inventory/add/{bill_id}")
async def add_to_inventory(bill_id: str, note: Optional[str] = None):
    """Add bill to inventory - UUID only"""
    try:
        # Validate composite bill_id format
        if not is_valid_composite_bill_id(bill_id):
            raise HTTPException(status_code=400, detail="Invalid composite bill_id format")
        
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
        # Validate composite bill_id format
        if not is_valid_composite_bill_id(bill_id):
            raise HTTPException(status_code=400, detail="Invalid composite bill_id format")
        
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

@app.post("/api/inventory/add")
async def add_bills_to_inventory(request_data: dict):
    """Add multiple bills to inventory - UUID only"""
    try:
        bill_ids = request_data.get("bill_ids", [])
        note = request_data.get("note", "")
        batch_name = request_data.get("batch_name", "")
        
        if not bill_ids:
            raise HTTPException(status_code=400, detail="No bill IDs provided")
        
        added_count = 0
        errors = []
        
        for bill_id in bill_ids:
            try:
                # Validate composite bill_id format
                if not is_valid_composite_bill_id(bill_id):
                    errors.append(f"Invalid composite bill_id format: {bill_id}")
                    continue
                
                # Check if bill exists
                bill = await db.bills.find_one({"id": bill_id})
                if not bill:
                    errors.append(f"Bill not found: {bill_id}")
                    continue
                
                if bill.get("is_in_inventory"):
                    errors.append(f"Bill already in inventory: {bill_id}")
                    continue
                
                # Add to inventory
                await db.bills.update_one(
                    {"id": bill_id},
                    {"$set": {
                        "is_in_inventory": True,
                        "inventory_status": "IN_INVENTORY",
                        "added_to_inventory_at": datetime.now(timezone.utc),
                        "inventory_note": note,
                        "batch_name": batch_name
                    }}
                )
                added_count += 1
                
            except Exception as e:
                errors.append(f"Error processing {bill_id}: {str(e)}")
        
        return {
            "success": True,
            "message": f"Added {added_count} bills to inventory",
            "added_count": added_count,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Error adding bills to inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# SALES API - UUID ONLY
# ========================================

@app.post("/api/sales", response_model=Sale)
async def create_sale(sale_data: SaleCreate):
    """Create sale transaction - UUID only system"""
    try:
        # Validate customer exists
        customer = await db.customers.find_one({"id": sale_data.customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Validate bills exist and are available
        bills = []
        for bill_id in sale_data.bill_ids:
            bill = await db.bills.find_one({"id": bill_id, "status": BillStatus.AVAILABLE})
            if not bill:
                raise HTTPException(
                    status_code=404, 
                    detail=f"Bill {bill_id} not found or not available"
                )
            bills.append(bill)
        
        # Calculate totals
        total = sum(bill.get("amount", 0) for bill in bills)
        profit_value = round(total * sale_data.profit_pct / 100, 0)
        payback = total - profit_value
        
        # Prepare sale document
        sale_dict = sale_data.dict()
        sale_dict.update({
            "total": total,
            "profit_value": profit_value,
            "payback": payback,
            "payment_method": "CASH",
            "status": "COMPLETED"
        })
        sale_dict = uuid_processor.prepare_document(sale_dict)
        
        # Create sale
        result = await db.sales.insert_one(sale_dict)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create sale")
        
        # Update bills to SOLD status
        await db.bills.update_many(
            {"id": {"$in": sale_data.bill_ids}},
            {"$set": {
                "status": BillStatus.SOLD,
                "is_in_inventory": False,
                "inventory_status": InventoryStatus.SOLD_FROM_INVENTORY,
                "updated_at": datetime.now(timezone.utc)
            }}
        )
        
        # Update customer stats
        await db.customers.update_one(
            {"id": sale_data.customer_id},
            {"$inc": {
                "total_transactions": 1,
                "total_spent": total,
                "total_profit_generated": profit_value
            }}
        )
        
        # Return created sale
        created_sale = await db.sales.find_one({"id": sale_dict["id"]})
        return Sale(**uuid_processor.clean_response(created_sale))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating sale: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sales", response_model=List[Sale])
async def get_sales(skip: int = 0, limit: int = 100, customer_id: Optional[str] = None):
    """Get sales transactions - UUID only"""
    try:
        # Build filter
        filter_dict = {}
        if customer_id:
            if not is_valid_uuid(customer_id):
                raise HTTPException(status_code=400, detail="Invalid customer UUID format")
            filter_dict["customer_id"] = customer_id
        
        # Query sales
        cursor = db.sales.find(filter_dict).skip(skip).limit(limit).sort("created_at", -1)
        sales = await cursor.to_list(length=limit)
        
        # Clean responses
        cleaned_sales = [uuid_processor.clean_response(sale) for sale in sales]
        return [Sale(**sale) for sale in cleaned_sales]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sales: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/sales/{sale_id}", response_model=Sale)
async def get_sale(sale_id: str):
    """Get sale by UUID only"""
    try:
        # Validate UUID format
        if not is_valid_uuid(sale_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Single lookup
        sale = await db.sales.find_one({"id": sale_id})
        if not sale:
            raise HTTPException(status_code=404, detail="Sale not found")
        
        return Sale(**uuid_processor.clean_response(sale))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching sale {sale_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# DASHBOARD STATS API - UUID ONLY
# ========================================

@app.get("/api/stats/dashboard")
async def get_dashboard_stats():
    """Get dashboard statistics - UUID only system"""
    try:
        # Customer stats
        total_customers = await db.customers.count_documents({})
        active_customers = await db.customers.count_documents({"is_active": True})
        
        # Bill stats
        total_bills = await db.bills.count_documents({})
        available_bills = await db.bills.count_documents({"status": BillStatus.AVAILABLE})
        inventory_bills = await db.bills.count_documents({"is_in_inventory": True})
        sold_bills = await db.bills.count_documents({"status": BillStatus.SOLD})
        
        # Sales stats
        total_sales = await db.sales.count_documents({})
        
        # Calculate revenue and profit
        sales_pipeline = [
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$total"},
                "total_profit": {"$sum": "$profit_value"}
            }}
        ]
        
        sales_stats = await db.sales.aggregate(sales_pipeline).to_list(1)
        total_revenue = sales_stats[0]["total_revenue"] if sales_stats else 0
        total_profit = sales_stats[0]["total_profit"] if sales_stats else 0
        
        return {
            "customers": {
                "total": total_customers,
                "active": active_customers
            },
            "bills": {
                "total": total_bills,
                "available": available_bills,
                "in_inventory": inventory_bills,
                "sold": sold_bills
            },
            "sales": {
                "total_transactions": total_sales,
                "total_revenue": total_revenue,
                "total_profit": total_profit
            },
            "system": {
                "architecture": "uuid_only",
                "version": "2.0.0"
            }
        }
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# AUTHENTICATION ENDPOINTS - UUID ONLY
# ========================================

@app.post("/api/auth/login", response_model=TokenResponse)
async def login_user(login_data: UserLogin):
    """Login user with username/email/phone and password"""
    try:
        # Find user by username, email, or phone
        logger.info(f"Login attempt for: {login_data.login}")
        user = await db.users.find_one({
            "$or": [
                {"username": login_data.login},
                {"email": login_data.login},
                {"phone": login_data.login}
            ]
        })
        
        if not user:
            logger.warning(f"User not found: {login_data.login}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email/phone or password"
            )
        
        logger.info(f"User found: {user.get('username')}")
        
        # Verify password
        if not verify_password(login_data.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username/email/phone or password"  
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account is deactivated"
            )
        
        # Update last login
        await db.users.update_one(
            {"username": user["username"]},
            {"$set": {"last_login": datetime.now(timezone.utc)}}
        )
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.get("id", user["username"]), "role": user["role"]}, 
            expires_delta=access_token_expires
        )
        
        # Prepare user response (without password)
        user_dict = dict(user)
        user_dict.pop("password", None)
        
        # Use the UUID id field we created, not ObjectId
        if "id" in user_dict:
            # User already has UUID id field
            pass
        elif "_id" in user_dict:
            # Fallback to ObjectId as string (shouldn't happen with updated user)
            user_dict["id"] = str(user_dict["_id"])
        
        # Remove ObjectId to avoid confusion
        user_dict.pop("_id", None)
        
        # Handle datetime fields
        if "created_at" in user_dict and isinstance(user_dict["created_at"], str):
            user_dict["created_at"] = datetime.fromisoformat(user_dict["created_at"].replace('Z', '+00:00'))
        
        # Don't use uuid_processor for user response as it may have ObjectId references
        user_response = UserResponse(**user_dict)
        
        return TokenResponse(
            access_token=access_token,
            token_type="bearer",
            user=user_response
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during login: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    """Get current user from JWT token"""
    try:
        # Decode JWT token
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
        # Find user by UUID id
        user = await db.users.find_one({"id": user_id})
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Prepare user response (without password)
        user_dict = dict(user)
        user_dict.pop("password", None)
        user_dict.pop("_id", None)  # Remove ObjectId
        
        # Handle datetime fields
        if "created_at" in user_dict and isinstance(user_dict["created_at"], str):
            user_dict["created_at"] = datetime.fromisoformat(user_dict["created_at"].replace('Z', '+00:00'))
        
        return UserResponse(**user_dict)
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except (jwt.InvalidTokenError, jwt.DecodeError, jwt.InvalidSignatureError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    except Exception as e:
        logger.error(f"Error validating token: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats") 
async def get_dashboard_stats_redirect():
    """Redirect old dashboard stats endpoint to new one"""
    return await get_dashboard_stats()

@app.get("/api/credit-cards/stats")
async def get_credit_cards_stats():
    """Credit cards stats for dashboard (placeholder)"""
    try:
        total_cards = await db.credit_cards.count_documents({})
        active_cards = await db.credit_cards.count_documents({"status": {"$ne": "Hết hạn"}})
        
        return {
            "total": total_cards,
            "active": active_cards,
            "expired": total_cards - active_cards,
            "this_month": 0
        }
    except Exception as e:
        logger.error(f"Error fetching credit card stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/credit-cards", response_model=List[CreditCard])
async def get_credit_cards(
    skip: int = 0, 
    limit: int = 100,
    page_size: int = Query(100, alias="page_size")
):
    """Get all credit cards - UUID only responses"""
    try:
        # Use page_size if provided, otherwise use limit
        actual_limit = page_size if page_size != 100 or limit == 100 else limit
        
        cursor = db.credit_cards.find({}).skip(skip).limit(actual_limit).sort("created_at", -1)
        credit_cards = await cursor.to_list(length=actual_limit)
        
        # Clean responses - UUID only system
        cleaned_cards = []
        for card in credit_cards:
            card_dict = dict(card)
            card_dict.pop("_id", None)  # Remove ObjectId
            cleaned_cards.append(card_dict)
        
        return [CreditCard(**card) for card in cleaned_cards]
        
    except Exception as e:
        logger.error(f"Error fetching credit cards: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/credit-cards", response_model=CreditCard)
async def create_credit_card(card_data: CreditCardCreate):
    """Create credit card with UUID only"""
    try:
        # Validate customer exists
        customer = await db.customers.find_one({"id": card_data.customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Prepare document with UUID
        card_dict = card_data.dict()
        card_dict = uuid_processor.prepare_document(card_dict)
        
        # Add customer name for denormalization
        card_dict["customer_name"] = customer.get("name")
        
        # Insert to database
        result = await db.credit_cards.insert_one(card_dict)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create credit card")
        
        # Update customer total cards count
        await db.customers.update_one(
            {"id": card_data.customer_id},
            {"$inc": {"total_cards": 1}}
        )
        
        # Return clean response
        created_card = await db.credit_cards.find_one({"id": card_dict["id"]})
        card_response = dict(created_card)
        card_response.pop("_id", None)
        return CreditCard(**card_response)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating credit card: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/credit-cards/{card_id}/detail")
async def get_credit_card_detail(card_id: str):
    """Get credit card detail with transactions - UUID only"""
    try:
        # Validate UUID format
        if not is_valid_uuid(card_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Get credit card
        card = await db.credit_cards.find_one({"id": card_id})
        if not card:
            raise HTTPException(status_code=404, detail="Credit card not found")
        
        # Get customer info
        customer = await db.customers.find_one({"id": card.get("customer_id")})
        
        # Get DAO transactions for this credit card - UUID only
        dao_transactions = await db.dao_transactions.find({"credit_card_id": card_id}).to_list(100)
        
        # Clean DAO transactions - remove ObjectId
        cleaned_transactions = []
        for dao in dao_transactions:
            dao_dict = dict(dao)
            dao_dict.pop("_id", None)  # Remove ObjectId
            cleaned_transactions.append(dao_dict)
        
        # Calculate summary
        total_transactions = len(cleaned_transactions)
        total_amount = sum(dao.get("amount", 0) for dao in cleaned_transactions)
        total_profit = sum(dao.get("profit_value", 0) for dao in cleaned_transactions)
        
        # Clean card response
        card_dict = dict(card)
        card_dict.pop("_id", None)
        
        # Clean customer response
        customer_dict = dict(customer) if customer else {}
        customer_dict.pop("_id", None)
        
        return {
            "success": True,
            "credit_card": card_dict,
            "customer": customer_dict,
            "transactions": cleaned_transactions,  # DAO transactions
            "summary": {
                "total_transactions": total_transactions,
                "total_amount": total_amount,
                "total_profit": total_profit
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching credit card detail {card_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/credit-cards/{card_id}", response_model=CreditCard)
async def get_credit_card(card_id: str):
    """Get credit card by UUID only"""
    try:
        # Validate UUID format
        if not is_valid_uuid(card_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Single lookup - no dual strategy
        card = await db.credit_cards.find_one({"id": card_id})
        if not card:
            raise HTTPException(status_code=404, detail="Credit card not found")
        
        card_dict = dict(card)
        card_dict.pop("_id", None)
        return CreditCard(**card_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching credit card {card_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/credit-cards/{card_id}", response_model=CreditCard)
async def update_credit_card(card_id: str, card_data: CreditCardUpdate):
    """Update credit card by UUID only"""
    try:
        # Validate UUID format
        if not is_valid_uuid(card_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Check if card exists
        existing_card = await db.credit_cards.find_one({"id": card_id})
        if not existing_card:
            raise HTTPException(status_code=404, detail="Credit card not found")
        
        # Prepare update data
        update_data = card_data.dict(exclude_unset=True)
        if update_data:
            update_data["updated_at"] = datetime.now(timezone.utc)
            await db.credit_cards.update_one({"id": card_id}, {"$set": update_data})
        
        # Return updated card
        updated_card = await db.credit_cards.find_one({"id": card_id})
        card_dict = dict(updated_card)
        card_dict.pop("_id", None)
        return CreditCard(**card_dict)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating credit card {card_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/credit-cards/{card_id}")
async def delete_credit_card(card_id: str):
    """Delete credit card by UUID only"""
    try:
        # Validate UUID format
        if not is_valid_uuid(card_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Check if card exists
        card = await db.credit_cards.find_one({"id": card_id})
        if not card:
            raise HTTPException(status_code=404, detail="Credit card not found")
        
        # Delete card
        result = await db.credit_cards.delete_one({"id": card_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete credit card")
        
        # Update customer total cards count
        await db.customers.update_one(
            {"id": card.get("customer_id")},
            {"$inc": {"total_cards": -1}}
        )
        
        return {"success": True, "message": "Credit card deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting credit card {card_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/credit-cards/{card_id}/dao")
async def dao_credit_card_by_id(card_id: str, dao_data: dict):
    """DAO (Credit Card Advance) transaction by specific card ID - UUID only"""
    try:
        # Validate UUID format
        if not is_valid_uuid(card_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Get credit card info
        card = await db.credit_cards.find_one({"id": card_id})
        if not card:
            raise HTTPException(status_code=404, detail="Credit card not found")
        
        # Get customer info
        customer = await db.customers.find_one({"id": card.get("customer_id")})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Create DAO transaction record with UUID
        dao_transaction = {
            "id": generate_uuid(),
            "customer_id": card.get("customer_id"),
            "credit_card_id": card_id,
            "card_number": f"****{card.get('card_number', '0000')[-4:]}",
            "bank_name": card.get("bank_name"),
            "amount": dao_data.get("amount", 0),
            "profit_value": dao_data.get("profit_value", 0),
            "fee_rate": dao_data.get("fee_rate", 3.0),  # Default 3% fee
            "payment_method": dao_data.get("payment_method", "POS"),
            "pos_code": dao_data.get("pos_code", ""),
            "transaction_code": dao_data.get("transaction_code", ""),
            "notes": dao_data.get("notes", f"Đáo thẻ {card.get('bank_name')} - {datetime.now().strftime('%d/%m/%Y')}"),
            "status": "COMPLETED",
            "transaction_type": "DAO",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        # Insert DAO transaction
        result = await db.dao_transactions.insert_one(dao_transaction)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create DAO transaction")
        
        # CRITICAL: Update credit card status and business logic after DAO
        card_dict = dict(card)
        card_dict = update_card_after_dao(card_dict, dao_data.get("amount", 0))
        
        # Update the credit card in database with new business logic
        await db.credit_cards.update_one(
            {"id": card_id},
            {
                "$set": {
                    "current_balance": card_dict["current_balance"],
                    "available_credit": card_dict["available_credit"],
                    "last_dao_date": card_dict["last_dao_date"],
                    "next_due_date": card_dict["next_due_date"],
                    "status": card_dict["status"],
                    "days_until_due": card_dict["days_until_due"],
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        await db.customers.update_one(
            {"id": card.get("customer_id")},
            {
                "$inc": {
                    "total_dao_amount": dao_data.get("amount", 0),
                    "total_dao_transactions": 1,
                    "total_dao_profit": dao_data.get("profit_value", 0),
                    # CRITICAL: Update main customer totals for customer list display
                    "total_spent": dao_data.get("amount", 0),
                    "total_profit_generated": dao_data.get("profit_value", 0),
                    "total_transactions": 1
                },
                "$set": {
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Clean response
        dao_response = dict(dao_transaction)
        dao_response.pop("_id", None)
        
        return {
            "success": True,
            "message": "Đáo thẻ thành công",
            "dao_transaction": dao_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing DAO for card {card_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/credit-cards/dao")
async def dao_credit_card_general(dao_data: dict):
    """DAO (Credit Card Advance) transaction - General endpoint - UUID only"""
    try:
        # Validate required fields
        customer_id = dao_data.get("customer_id")
        if not customer_id or not is_valid_uuid(customer_id):
            raise HTTPException(status_code=400, detail="Valid customer_id (UUID) is required")
        
        # Get customer info
        customer = await db.customers.find_one({"id": customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get credit card info if card_id provided
        card_info = {}
        if dao_data.get("card_id"):
            card = await db.credit_cards.find_one({"id": dao_data["card_id"]})
            if card:
                card_info = {
                    "credit_card_id": card["id"],
                    "card_number": f"****{card.get('card_number', '0000')[-4:]}",
                    "bank_name": card.get("bank_name")
                }
        
        # Create DAO transaction record with UUID
        dao_transaction = {
            "id": generate_uuid(),
            "customer_id": customer_id,
            "amount": dao_data.get("amount", 0),
            "profit_value": dao_data.get("profit_value", 0),
            "fee_rate": dao_data.get("fee_rate", 3.0),
            "payment_method": dao_data.get("payment_method", "CASH"),
            "bill_code": dao_data.get("bill_code", ""),  # For đáo bằng bill điện
            "pos_code": dao_data.get("pos_code", ""),    # For đáo bằng POS
            "transaction_code": dao_data.get("transaction_code", ""),
            "notes": dao_data.get("notes", f"Đáo thẻ - {datetime.now().strftime('%d/%m/%Y')}"),
            "status": "COMPLETED",
            "transaction_type": "DAO",
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            **card_info  # Add credit card info if available
        }
        
        # Insert DAO transaction
        result = await db.dao_transactions.insert_one(dao_transaction)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create DAO transaction")
        
        # Update customer stats - CRITICAL: Include DAO in total_spent and total_profit_generated  
        await db.customers.update_one(
            {"id": customer_id},
            {
                "$inc": {
                    "total_dao_amount": dao_data.get("amount", 0),
                    "total_dao_transactions": 1,
                    "total_dao_profit": dao_data.get("profit_value", 0),
                    # CRITICAL: Update main customer totals for customer list display
                    "total_spent": dao_data.get("amount", 0),
                    "total_profit_generated": dao_data.get("profit_value", 0),
                    "total_transactions": 1
                },
                "$set": {
                    "updated_at": datetime.now(timezone.utc)
                }
            }
        )
        
        # Clean response
        dao_response = dict(dao_transaction)
        dao_response.pop("_id", None)
        
        return {
            "success": True,
            "message": "Đáo thẻ thành công",
            "dao_transaction": dao_response
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing general DAO: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dao-transactions", response_model=List[dict])
async def get_dao_transactions(
    skip: int = 0, 
    limit: int = 100,
    customer_id: Optional[str] = None
):
    """Get DAO transactions - UUID only responses"""
    try:
        # Build query filter
        filter_query = {}
        if customer_id:
            if not is_valid_uuid(customer_id):
                raise HTTPException(status_code=400, detail="Invalid customer_id UUID format")
            filter_query["customer_id"] = customer_id
        
        # Get DAO transactions
        cursor = db.dao_transactions.find(filter_query).skip(skip).limit(limit).sort("created_at", -1)
        dao_transactions = await cursor.to_list(length=limit)
        
        # Clean responses - UUID only system
        cleaned_transactions = []
        for transaction in dao_transactions:
            transaction_dict = dict(transaction)
            transaction_dict.pop("_id", None)  # Remove ObjectId
            cleaned_transactions.append(transaction_dict)
        
        return cleaned_transactions
        
    except Exception as e:
        logger.error(f"Error fetching DAO transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}/transactions-summary")
async def get_customer_transactions_summary(
    customer_id: str,
    limit: int = Query(100, alias="limit")
):
    """Get customer transactions summary - UUID only"""
    try:
        # Validate UUID format
        if not is_valid_uuid(customer_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Get customer info
        customer = await db.customers.find_one({"id": customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get bill sales for this customer (limited)
        sales = await db.sales.find({"customer_id": customer_id}).limit(limit).to_list(limit)
        
        # Get DAO transactions for this customer (limited)
        dao_transactions = await db.dao_transactions.find({"customer_id": customer_id}).limit(limit).to_list(limit)
        
        # Combine all transactions
        all_transactions = []
        
        # Add sales as transactions
        for sale in sales:
            sale_dict = dict(sale)
            sale_dict.pop("_id", None)
            sale_dict["transaction_type"] = "BILL_SALE"
            all_transactions.append(sale_dict)
        
        # Add DAO transactions
        for dao in dao_transactions:
            dao_dict = dict(dao)
            dao_dict.pop("_id", None)
            dao_dict["transaction_type"] = "DAO"
            all_transactions.append(dao_dict)
        
        # Sort by created_at descending
        all_transactions.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        
        # Calculate summary
        total_transactions = len(all_transactions)
        total_amount = sum(tx.get("total", 0) + tx.get("amount", 0) for tx in all_transactions)
        total_profit = sum(tx.get("profit_value", 0) for tx in all_transactions)
        
        # Clean customer response
        customer_dict = dict(customer)
        customer_dict.pop("_id", None)
        
        return {
            "success": True,
            "customer": customer_dict,
            "transactions": all_transactions[:limit],  # Apply limit
            "summary": {
                "total_transactions": total_transactions,
                "total_amount": total_amount,
                "total_profit": total_profit,
                "bill_sales": len(sales),
                "dao_transactions": len(dao_transactions)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer transactions summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/activities/recent")
async def get_recent_activities(days: int = 3, limit: int = 20):
    """Recent activities for dashboard (placeholder)"""
    try:
        # For now, return empty activities - to be implemented  
        return []
    except Exception as e:
        logger.error(f"Error fetching recent activities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bill/check/single")
async def check_single_bill(customer_code: str = Query(...), provider_region: str = Query(...)):
    """Single bill check - REAL N8N Webhook Call"""
    try:
        logger.info(f"Calling REAL webhook for: {customer_code} in {provider_region}")
        
        # REAL N8N Webhook URL  
        webhook_url = "https://n8n.phamthanh.net/webhook/checkbill"
        
        # Map provider_region to SKU codes
        sku_mapping = {
            "MIEN_BAC": "00906819",
            "MIEN_NAM": "00906815", 
            "TPHCM": "00906818"
        }
        
        sku = sku_mapping.get(provider_region, "00906819")  # Default to MIEN_BAC
        
        # Prepare payload for N8N webhook - only contractNumber and sku
        payload = {
            "contractNumber": customer_code,  # Use customer_code as contractNumber
            "sku": sku
        }
        
        # Configure timeout for external API call (30 seconds)
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            logger.info(f"Making REAL API call to: {webhook_url}")
            logger.info(f"Payload: {payload}")
            
            async with session.post(
                webhook_url,
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                response_text = await response.text()
                logger.info(f"External API response status: {response.status}")
                logger.info(f"External API response: {response_text[:500]}...")
                
                if response.status == 200:
                    try:
                        response_data = await response.json()
                        
                        # Handle array response from N8N webhook
                        if isinstance(response_data, list) and len(response_data) > 0:
                            # Find success response (prioritize success over errors)
                            success_response = None
                            error_response = None
                            
                            for item in response_data:
                                if "status" in item and item.get("status") == 200 and item.get("message") == "success":
                                    success_response = item
                                    break  # Prioritize success response
                                elif "error" in item:
                                    error_response = item
                            
                            # Use success response if available, otherwise use error
                            if success_response:
                                data = success_response
                                logger.info(f"Using SUCCESS response from N8N webhook")
                            elif error_response:
                                data = error_response
                                logger.info(f"Using ERROR response from N8N webhook")
                            else:
                                data = response_data[0]
                                logger.info(f"Using FIRST response from N8N webhook")
                        else:
                            data = response_data
                        
                        # Check if webhook returned error and classify properly
                        if "error" in data:
                            error_msg = data["error"].get("message", "Unknown webhook error")
                            
                            # Classify error types based on FPT business logic
                            if "reCAPTCHA required" in error_msg or "Too many requests" in error_msg:
                                # System rate limiting - real error
                                return {
                                    "success": True,
                                    "status": "ERROR",
                                    "message": "Quá nhiều requests - cần chờ một lúc",
                                    "customer_code": customer_code,
                                    "full_name": "N/A",
                                    "address": "N/A",
                                    "amount": 0,
                                    "billing_cycle": "N/A",
                                    "bill_status": "ERROR",
                                    "provider_region": provider_region,
                                    "bill": None
                                }
                            elif "Mã Khách hàng nhập vào không tồn tại" in error_msg or "Đầu vào không hợp lệ" in error_msg:
                                # Invalid customer code or wrong region - normal business case
                                return {
                                    "success": True,
                                    "status": "NOT_FOUND",
                                    "message": "Không tìm thấy mã khách hàng hoặc sai miền",
                                    "customer_code": customer_code,
                                    "full_name": "N/A",
                                    "address": "N/A",
                                    "amount": 0,
                                    "billing_cycle": "N/A",
                                    "bill_status": "NOT_FOUND",
                                    "provider_region": provider_region,
                                    "bill": None
                                }
                            elif "không nợ cước" in error_msg or "đã thanh toán" in error_msg.lower():
                                # Bill already paid - normal business case
                                return {
                                    "success": True,
                                    "status": "NOT_FOUND", 
                                    "message": "Bill đã được thanh toán",
                                    "customer_code": customer_code,
                                    "full_name": "N/A",
                                    "address": "N/A",
                                    "amount": 0,
                                    "billing_cycle": "N/A",
                                    "bill_status": "PAID",
                                    "provider_region": provider_region,
                                    "bill": None
                                }
                            else:
                                # Other unknown errors
                                return {
                                    "success": True,
                                    "status": "ERROR",
                                    "message": f"Lỗi hệ thống: {error_msg[:50]}...",
                                    "customer_code": customer_code,
                                    "full_name": "N/A",
                                    "address": "N/A",
                                    "amount": 0,
                                    "billing_cycle": "N/A",
                                    "bill_status": "ERROR",
                                    "provider_region": provider_region,
                                    "bill": None
                                }
                        
                        # Process successful N8N response format
                        if data.get("status") == 200 and data.get("message") == "success":
                            # Extract bill data from N8N response
                            bill_data = data.get("data", {})
                            bills = bill_data.get("bills", [])
                            
                            if bills and len(bills) > 0:
                                bill = bills[0]  # Take first bill
                                
                                # Generate composite bill_id (customer_code + MMYY)
                                billing_cycle = bill.get("month", "N/A")
                                composite_bill_id = generate_composite_bill_id(customer_code, billing_cycle)
                                
                                # Create or update bill in database for inventory management
                                bill_record = {
                                    "id": composite_bill_id,  # Use composite bill_id
                                    "customer_code": customer_code,
                                    "customer_name": bill.get("customerName", "N/A"),
                                    "address": bill.get("address", "N/A"),
                                    "amount": bill.get("moneyAmount", 0),
                                    "billing_cycle": billing_cycle,
                                    "provider_region": provider_region,
                                    "status": BillStatus.AVAILABLE,
                                    "is_in_inventory": False,
                                    "external_bill_id": bill.get("billId"),
                                    "gateway": "FPT_N8N",
                                    "created_at": datetime.now(timezone.utc)
                                }
                                
                                # Save to database - check for duplicates
                                existing_bill = await db.bills.find_one({"id": composite_bill_id})
                                if existing_bill:
                                    return {
                                        "success": True,
                                        "status": "OK",  # Change to OK since bill data is valid
                                        "message": f"Bill {customer_code} for cycle {billing_cycle} already exists (cached)",
                                        "id": composite_bill_id,
                                        "customer_code": customer_code,
                                        "full_name": existing_bill.get("customer_name", "N/A"),
                                        "address": existing_bill.get("address", "N/A"),
                                        "amount": existing_bill.get("amount", 0),
                                        "billing_cycle": existing_bill.get("billing_cycle", "N/A"),
                                        "bill_status": "AVAILABLE",  # Use existing bill status
                                        "provider_region": provider_region,
                                        "bill": {
                                            "id": composite_bill_id,
                                            "customerName": existing_bill.get("customer_name"),
                                            "address": existing_bill.get("address"),
                                            "amount": existing_bill.get("amount", 0),
                                            "gateway": "CACHED"
                                        }
                                    }
                                
                                # Insert new bill
                                await db.bills.insert_one(bill_record)
                                
                                return {
                                    "success": True,
                                    "status": "OK", 
                                    "message": "Bill found via N8N Webhook",
                                    "id": composite_bill_id,  # Return composite bill_id
                                    "customer_code": customer_code,
                                    "full_name": bill.get("customerName", "N/A"),
                                    "address": bill.get("address", "N/A"),
                                    "amount": bill.get("moneyAmount", 0),
                                    "billing_cycle": billing_cycle,
                                    "bill_status": "AVAILABLE",
                                    "provider_region": provider_region,
                                    "bill": {
                                        "id": composite_bill_id,
                                        "billId": bill.get("billId"),
                                        "contractNumber": bill.get("contractNumber"),
                                        "customerName": bill.get("customerName"),
                                        "address": bill.get("address"),
                                        "amount": bill.get("moneyAmount", 0),
                                        "month": bill.get("month"),
                                        "totalAmount": bill_data.get("totalContractAmount", 0),
                                        "gateway": "FPT_N8N"
                                    }
                                }
                            else:
                                # No bills found in response
                                return {
                                    "success": True,
                                    "status": "NOT_FOUND",
                                    "message": "No bills found in N8N response",
                                    "customer_code": customer_code,
                                    "customer_name": "N/A",
                                    "customer_address": "N/A", 
                                    "amount": 0,
                                    "billing_cycle": "N/A",
                                    "bill_status": "NOT_FOUND",
                                    "provider_region": provider_region,
                                    "bill": None
                                }
                        else:
                            # Unexpected response format
                            return {
                                "success": True,
                                "status": "ERROR",
                                "message": f"Unexpected N8N response format",
                                "customer_code": customer_code,
                                "customer_name": "N/A",
                                "customer_address": "N/A", 
                                "amount": 0,
                                "billing_cycle": "N/A",
                                "bill_status": "ERROR",
                                "provider_region": provider_region,
                                "bill": None
                            }
                            
                    except Exception as parse_error:
                        logger.error(f"Error parsing webhook response: {parse_error}")
                        # Try to parse as text response
                        return {
                            "success": True,
                            "status": "ERROR", 
                            "message": f"Webhook response parse error: {str(parse_error)}",
                            "customer_code": customer_code,
                            "customer_name": "N/A",
                            "customer_address": "N/A",
                            "amount": 0,
                            "billing_cycle": "N/A",
                            "bill_status": "ERROR",
                            "provider_region": provider_region,
                            "bill": None
                        }
                else:
                    logger.error(f"Webhook returned status {response.status}: {response_text}")
                    return {
                        "success": True,
                        "status": "ERROR",
                        "message": f"Webhook error (Status {response.status})",
                        "customer_code": customer_code,
                        "customer_name": "N/A",
                        "customer_address": "N/A",
                        "amount": 0,
                        "billing_cycle": "N/A", 
                        "bill_status": "ERROR",
                        "provider_region": provider_region,
                        "bill": None
                    }
                    
    except asyncio.TimeoutError:
        logger.error(f"Timeout calling webhook for {customer_code}")
        return {
            "success": True,
            "status": "ERROR",
            "message": "Webhook timeout (30s)",
            "customer_code": customer_code,
            "customer_name": "N/A",
            "customer_address": "N/A",
            "amount": 0,
            "billing_cycle": "N/A",
            "bill_status": "ERROR",
            "provider_region": provider_region,
            "bill": None
        }
    except Exception as e:
        logger.error(f"Error calling webhook for {customer_code}: {e}")
        return {
            "success": True,
            "status": "ERROR",
            "message": f"Webhook API error: {str(e)}",
            "customer_code": customer_code,
            "customer_name": "N/A", 
            "customer_address": "N/A",
            "amount": 0,
            "billing_cycle": "N/A",
            "bill_status": "ERROR",
            "provider_region": provider_region,
            "bill": None
        }
@app.get("/api/inventory/stats")
async def get_inventory_stats():
    """Inventory stats for dashboard"""
    try:
        # Count bills in inventory
        available_count = await db.bills.count_documents({"status": BillStatus.AVAILABLE, "is_in_inventory": True})
        sold_count = await db.bills.count_documents({"status": BillStatus.SOLD, "is_in_inventory": False})
        
        return {
            "total": available_count + sold_count,
            "available": available_count,
            "sold": sold_count,
            "pending": 0
        }
    except Exception as e:
        logger.error(f"Error fetching inventory stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/bills/create")
async def create_bill_from_frontend(bill_data: dict):
    """Create bill from frontend (redirect to main create endpoint)"""
    try:
        # Convert to Bill model and use existing endpoint
        bill_create = BillCreate(**bill_data)
        return await create_bill(bill_create)
    except Exception as e:
        logger.error(f"Error creating bill: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/transactions/stats")
async def get_transactions_stats():
    """Transaction stats for dashboard"""
    try:
        total_sales = await db.sales.count_documents({})
        total_revenue = 0
        total_profit = 0
        
        # Calculate revenue and profit
        pipeline = [
            {"$group": {
                "_id": None,
                "total_revenue": {"$sum": "$total"},
                "total_profit": {"$sum": "$profit_value"}
            }}
        ]
        
        result = await db.sales.aggregate(pipeline).to_list(1)
        if result:
            total_revenue = result[0].get("total_revenue", 0)
            total_profit = result[0].get("total_profit", 0)
        
        return {
            "total_transactions": total_sales,
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "today": 0  # Placeholder
        }
    except Exception as e:
        logger.error(f"Error fetching transaction stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}/detailed-profile")
async def get_customer_detailed_profile(customer_id: str):
    """Get comprehensive customer profile with all related data - UUID only system"""
    try:
        # Validate UUID format
        if not is_valid_uuid(customer_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Get customer info
        customer = await db.customers.find_one({"id": customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
        
        # Get customer's credit cards (UUID only system)
        cards_cursor = db.credit_cards.find({"customer_id": customer_id})
        cards = await cards_cursor.to_list(None)
        
        # Get customer's bill sales (UUID only)
        sales_pipeline = [
            {"$match": {"customer_id": customer_id}},
            {
                "$lookup": {
                    "from": "bills",
                    "localField": "bill_ids", 
                    "foreignField": "id",
                    "as": "bills"
                }
            },
            {"$sort": {"created_at": -1}}
        ]
        sales_cursor = db.sales.aggregate(sales_pipeline)
        sales = await sales_cursor.to_list(None)
        
        # Get customer's DAO transactions (placeholder - not implemented in UUID system yet)
        dao_transactions = []  # TODO: Implement when credit card transactions are added
        
        # Calculate customer metrics
        total_sales_value = sum(sale.get("total", 0) for sale in sales)
        total_sales_profit = sum(sale.get("profit_value", 0) for sale in sales)
        total_dao_value = 0  # TODO: sum(dao.get("total_amount", 0) for dao in dao_transactions)
        total_dao_profit = 0  # TODO: sum(dao.get("profit_value", 0) for dao in dao_transactions)
        
        total_transaction_value = total_sales_value + total_dao_value
        total_profit = total_sales_profit + total_dao_profit
        total_transactions = len(sales) + len(dao_transactions)
        
        avg_transaction_value = total_transaction_value / total_transactions if total_transactions > 0 else 0
        profit_margin = (total_profit / total_transaction_value * 100) if total_transaction_value > 0 else 0
        
        # Customer tier calculation
        if total_transaction_value >= 50000000:  # 50M VND
            tier = "VIP"
        elif total_transaction_value >= 20000000:  # 20M VND  
            tier = "Premium"
        elif total_transaction_value >= 5000000:   # 5M VND
            tier = "Regular"
        else:
            tier = "New"
        
        # Calculate credit cards metrics
        total_credit_limit = sum(card.get("credit_limit", 0) for card in cards)
        active_cards = [card for card in cards if card.get("status") != "Hết hạn"]
        
        # Recent activity (last 10 transactions) - with proper datetime handling
        recent_activities = []
        
        # Add recent sales
        for sale in sales[:5]:
            recent_activities.append({
                "id": sale["id"],
                "type": "BILL_SALE",
                "amount": sale.get("total", 0),
                "profit": sale.get("profit_value", 0),
                "created_at": sale["created_at"],
                "description": f"Bán {len(sale.get('bills', []))} bills",
                "bills_count": len(sale.get("bills", []))
            })
        
        # Sort recent activities by date - handle mixed timezone datetime objects safely
        def safe_activity_sort_key(activity):
            created_at = activity.get("created_at")
            # Convert all datetime objects to timezone-aware UTC for consistent comparison
            if isinstance(created_at, datetime):
                if created_at.tzinfo is None:
                    # Timezone-naive datetime - assume UTC
                    created_at = created_at.replace(tzinfo=timezone.utc)
                else:
                    # Already timezone-aware - convert to UTC
                    created_at = created_at.astimezone(timezone.utc)
            elif isinstance(created_at, str):
                # String datetime - parse and make timezone-aware
                try:
                    created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                    if created_at.tzinfo is None:
                        created_at = created_at.replace(tzinfo=timezone.utc)
                except:
                    # Fallback to current time if parsing fails
                    created_at = datetime.now(timezone.utc)
            else:
                # Fallback to current time for unknown types
                created_at = datetime.now(timezone.utc)
            
            return created_at
        
        recent_activities.sort(key=safe_activity_sort_key, reverse=True)
        recent_activities = recent_activities[:10]
        
        # Clean customer response
        customer_dict = dict(customer)
        customer_dict.pop("_id", None)
        
        return {
            "success": True,
            "customer": {
                "id": customer_dict["id"],
                "name": customer_dict["name"],
                "phone": customer_dict.get("phone"),
                "email": customer_dict.get("email"),
                "address": customer_dict.get("address"),
                "type": customer_dict.get("type", "INDIVIDUAL"),
                "is_active": customer_dict.get("is_active", True),
                "created_at": customer_dict["created_at"],
                "tier": tier,
                "notes": customer_dict.get("notes", "")
            },
            "metrics": {
                "total_transaction_value": total_transaction_value,
                "total_profit": total_profit,
                "total_transactions": total_transactions,
                "avg_transaction_value": avg_transaction_value,
                "profit_margin": round(profit_margin, 1),
                "sales_transactions": len(sales),
                "dao_transactions": len(dao_transactions),
                "sales_value": total_sales_value,
                "dao_value": total_dao_value
            },
            "credit_cards": {
                "total_cards": len(cards),
                "active_cards": len(active_cards),
                "total_credit_limit": total_credit_limit,
                "cards": [{
                    "id": card["id"],
                    "card_number": f"****{card.get('card_number', '0000')[-4:]}",
                    "bank_name": card.get("bank_name"),
                    "card_type": card.get("card_type"),
                    "credit_limit": card.get("credit_limit", 0),
                    "status": card.get("status"),
                    "expiry_date": card.get("expiry_date")
                } for card in cards]
            },
            "recent_activities": recent_activities,
            "performance": {
                "best_month_revenue": 0,  # TODO: Calculate from monthly data
                "growth_rate": 0,         # TODO: Calculate YoY growth
                "success_rate": 100,      # TODO: Calculate based on transaction success
                "avg_days_between_transactions": 0  # TODO: Calculate
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting customer detailed profile: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/{customer_id}/transactions")
async def get_customer_transactions(customer_id: str):
    """Get customer detail with transactions - FORMAT FOR FRONTEND MODAL"""
    try:
        if not is_valid_uuid(customer_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Get customer info
        customer = await db.customers.find_one({"id": customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get sales for this customer with bill details
        sales_pipeline = [
            {"$match": {"customer_id": customer_id}},
            {
                "$lookup": {
                    "from": "bills",
                    "localField": "bill_ids", 
                    "foreignField": "id",
                    "as": "bills"
                }
            },
            {"$sort": {"created_at": -1}}
        ]
        sales_cursor = db.sales.aggregate(sales_pipeline)
        sales = await sales_cursor.to_list(100)
        
        # Process transactions to include bill codes
        cleaned_transactions = []
        for sale in sales:
            sale_dict = dict(sale)
            sale_dict.pop("_id", None)  # Remove ObjectId from sale
            
            # Clean bills data and add bill_codes for display in frontend
            bill_codes = []
            bills = sale_dict.get("bills", [])
            cleaned_bills = []
            
            for bill in bills:
                # Clean ObjectId from each bill
                bill_dict = dict(bill)
                bill_dict.pop("_id", None)  # Remove ObjectId from bill
                cleaned_bills.append(bill_dict)
                
                # Use the full composite bill_id instead of just customer_code
                bill_id = bill_dict.get("id", "N/A")  # This is the composite bill_id (customer_code + MMYY)
                bill_codes.append(bill_id)
            
            sale_dict["bills"] = cleaned_bills  # Replace with cleaned bills
            sale_dict["bill_codes"] = bill_codes
            sale_dict["transaction_type"] = "BILL_SALE"  # Mark as bill sale
            cleaned_transactions.append(sale_dict)
        
        # CRITICAL: Add DAO transactions for this customer
        dao_transactions = await db.dao_transactions.find({"customer_id": customer_id}).to_list(100)
        for dao in dao_transactions:
            dao_dict = dict(dao)
            dao_dict.pop("_id", None)  # Remove ObjectId
            
            # Add bill_codes for consistency with sales display
            if dao_dict.get("card_number"):
                dao_dict["bill_codes"] = [f"{dao_dict.get('bank_name', '')} {dao_dict.get('card_number')}"]
            elif dao_dict.get("bill_code"):
                dao_dict["bill_codes"] = [dao_dict.get("bill_code")]
            elif dao_dict.get("pos_code"):
                dao_dict["bill_codes"] = [f"POS: {dao_dict.get('pos_code')}"]
            else:
                dao_dict["bill_codes"] = ["Đáo thẻ"]
            
            dao_dict["transaction_type"] = "DAO"  # Mark as DAO
            # Map DAO fields to transaction fields for consistent display
            dao_dict["total"] = dao_dict.get("amount", 0)
            dao_dict["profit_value"] = dao_dict.get("profit_value", 0)
            dao_dict["payback"] = dao_dict.get("amount", 0) - dao_dict.get("profit_value", 0)
            dao_dict["status"] = dao_dict.get("status", "COMPLETED")
            
            cleaned_transactions.append(dao_dict)
        
        # Sort all transactions by created_at descending
        cleaned_transactions.sort(key=lambda x: x.get("created_at", datetime.min), reverse=True)
        
        # TODO: Add credit card transactions when implemented
        # Get customer's credit card transactions (DAO)
        # credit_card_transactions = await db.credit_card_transactions.find({"customer_id": customer_id}).to_list(100)
        # for cc_transaction in credit_card_transactions:
        #     # Add card codes for display
        #     card_codes = [f"****{card_number[-4:]}"]
        #     cc_transaction["bill_codes"] = card_codes  # Reuse bill_codes field for consistency
        #     cleaned_transactions.append(cc_transaction)
        
        # Calculate summary
        total_transactions = len(cleaned_transactions)
        total_spent = sum(transaction.get("total", 0) for transaction in cleaned_transactions)
        total_profit = sum(transaction.get("profit_value", 0) for transaction in cleaned_transactions)
        
        # Clean customer response
        customer_dict = dict(customer)
        customer_dict.pop("_id", None)
        
        # Return format expected by frontend modal
        return {
            "customer": customer_dict,
            "transactions": cleaned_transactions,
            "summary": {
                "total_transactions": total_transactions,
                "total_spent": total_spent,
                "total_profit": total_profit,
                "avg_transaction": total_spent / total_transactions if total_transactions > 0 else 0
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching customer transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/customers/export")
async def export_customers():
    """Export customers (placeholder)"""
    try:
        return {"message": "Customer export not implemented yet"}
    except Exception as e:
        logger.error(f"Error exporting customers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/template")
async def get_inventory_template():
    """Get inventory template (placeholder)"""
    try:
        return {"message": "Inventory template not implemented yet"}
    except Exception as e:
        logger.error(f"Error getting template: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/inventory/export")
async def export_inventory():
    """Export inventory (placeholder)"""
    try:
        return {"message": "Inventory export not implemented yet"}
    except Exception as e:
        logger.error(f"Error exporting inventory: {e}")
        raise HTTPException(status_code=500, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))

# ========================================
# SYSTEM HEALTH API
# ========================================

@app.get("/api/health")
async def health_check():
    """System health check - UUID only"""
    try:
        # Test database connection
        await db.command("ping")
        
        # Check collections exist
        collections = await db.list_collection_names()
        required_collections = ["customers", "bills", "sales"]
        
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "database": "connected",
            "architecture": "uuid_only",
            "version": "2.0.0",
            "collections": {
                collection: collection in collections 
                for collection in required_collections
            }
        }
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e)
        }

# ========================================
# UNIFIED TRANSACTIONS MODELS - UUID ONLY
# ========================================

class TransactionType(str, Enum):
    BILL_SALE = "BILL_SALE"
    CREDIT_DAO_POS = "CREDIT_DAO_POS"
    CREDIT_DAO_BILL = "CREDIT_DAO_BILL"

class TransactionItem(BaseModel):
    id: str
    code: Optional[str] = None
    amount: float = 0.0
    type: str = "BILL"

class UnifiedTransaction(BaseModel):
    id: str
    type: TransactionType
    customer_id: str
    customer_name: str
    customer_phone: Optional[str] = None
    total_amount: float = 0.0
    profit_amount: float = 0.0
    profit_percentage: float = 0.0
    payback: Optional[float] = None
    items: List[TransactionItem] = []
    item_codes: List[str] = []
    item_display: str = ""
    payment_method: Optional[str] = None
    status: str = "COMPLETED"
    notes: Optional[str] = None
    created_at: datetime

# ========================================
# UNIFIED TRANSACTIONS API - UUID ONLY
# ========================================

@app.get("/api/transactions/unified", response_model=List[UnifiedTransaction])
async def get_unified_transactions(
    limit: int = 50,
    offset: int = 0,
    transaction_type: Optional[str] = None,
    customer_id: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    search: Optional[str] = None
):
    """Get unified transactions from Sales (UUID only system)"""
    try:
        unified_transactions = []
        
        # Query filters
        match_filters = {}
        if date_from or date_to:
            date_filter = {}
            if date_from:
                date_filter["$gte"] = datetime.fromisoformat(date_from.replace('Z', '+00:00'))
            if date_to:  
                date_filter["$lte"] = datetime.fromisoformat(date_to.replace('Z', '+00:00'))
            match_filters["created_at"] = date_filter
        
        if customer_id and is_valid_uuid(customer_id):
            match_filters["customer_id"] = customer_id
        
        # Get Bill Sales (UUID only)
        if not transaction_type or transaction_type == "BILL_SALE":
            sales_pipeline = [
                {"$match": match_filters},
                {
                    "$lookup": {
                        "from": "customers",
                        "localField": "customer_id", 
                        "foreignField": "id",
                        "as": "customer"
                    }
                },
                {
                    "$lookup": {
                        "from": "bills",
                        "localField": "bill_ids",
                        "foreignField": "id", 
                        "as": "bills"
                    }
                },
                {"$sort": {"created_at": -1}},
                {"$limit": limit + offset},
                {"$skip": offset}
            ]
            
            sales_cursor = db.sales.aggregate(sales_pipeline)
            sales_results = await sales_cursor.to_list(length=None)
            
            for sale in sales_results:
                # Safe array access for customer
                customer_data = sale.get("customer", [])
                customer = customer_data[0] if customer_data else {}
                
                # Safe array access for bills
                bills = sale.get("bills", [])
                
                # Create bill codes display
                bill_codes = [bill.get("id", "N/A") for bill in bills]  # Use composite bill_id
                item_display = ", ".join(bill_codes[:3])
                if len(bill_codes) > 3:
                    item_display += f" (+{len(bill_codes)-3} khác)"
                
                transaction = UnifiedTransaction(
                    id=sale["id"],
                    type=TransactionType.BILL_SALE,
                    customer_id=sale["customer_id"],
                    customer_name=customer.get("name", "N/A"),
                    customer_phone=customer.get("phone"),
                    total_amount=sale.get("total", 0),
                    profit_amount=sale.get("profit_value", 0),
                    profit_percentage=sale.get("profit_pct", 0),
                    payback=sale.get("payback"),
                    items=[TransactionItem(
                        id=bill["id"],
                        code=bill.get("id"),  # Use composite bill_id as code
                        amount=bill.get("amount", 0),
                        type="BILL"
                    ) for bill in bills],
                    item_codes=bill_codes,
                    item_display=item_display,
                    payment_method=sale.get("payment_method", "CASH"),
                    status=sale.get("status", "COMPLETED"),
                    notes=sale.get("notes"),
                    created_at=sale["created_at"]
                )
                unified_transactions.append(transaction)
        
        # Get DAO Transactions (UUID only)
        if not transaction_type or transaction_type == "DAO":
            dao_pipeline = [
                {"$match": match_filters},
                {
                    "$lookup": {
                        "from": "customers",
                        "localField": "customer_id", 
                        "foreignField": "id",
                        "as": "customer"
                    }
                },
                {"$sort": {"created_at": -1}},
                {"$limit": limit + offset},
                {"$skip": offset}
            ]
            
            dao_cursor = db.dao_transactions.aggregate(dao_pipeline)
            dao_results = await dao_cursor.to_list(length=None)
            
            for dao in dao_results:
                # Safe array access for customer
                customer_data = dao.get("customer", [])
                customer = customer_data[0] if customer_data else {}
                
                # Create item display for DAO
                card_info = ""
                if dao.get("card_number"):
                    card_info = f"{dao.get('bank_name', '')} {dao.get('card_number')}"
                elif dao.get("bill_code"):
                    card_info = dao.get("bill_code")
                elif dao.get("pos_code"):
                    card_info = f"POS: {dao.get('pos_code')}"
                else:
                    card_info = "Đáo thẻ"
                
                transaction = UnifiedTransaction(
                    id=dao["id"],
                    type=TransactionType.DAO,
                    customer_id=dao["customer_id"],
                    customer_name=customer.get("name", "N/A"),
                    customer_phone=customer.get("phone"),
                    total_amount=dao.get("amount", 0),
                    profit_amount=dao.get("profit_value", 0),
                    profit_percentage=dao.get("fee_rate", 3.0),
                    payback=dao.get("amount", 0) - dao.get("profit_value", 0),  # Amount minus profit
                    items=[TransactionItem(
                        id=dao["id"],
                        code=card_info,
                        amount=dao.get("amount", 0),
                        type="DAO"
                    )],
                    item_codes=[card_info],
                    item_display=card_info,
                    payment_method=dao.get("payment_method", "CASH"),
                    status=dao.get("status", "COMPLETED"),
                    notes=dao.get("notes"),
                    created_at=dao["created_at"]
                )
                unified_transactions.append(transaction)

        # Sort by created_at descending
        unified_transactions.sort(key=lambda x: x.created_at, reverse=True)
        
        # Apply search filter if provided
        if search:
            search_lower = search.lower()
            unified_transactions = [
                tx for tx in unified_transactions
                if (search_lower in tx.customer_name.lower() or
                    search_lower in (tx.customer_phone or "").lower() or
                    any(search_lower in code.lower() for code in tx.item_codes))
            ]
        
        # Apply pagination
        start_idx = offset
        end_idx = offset + limit
        paginated_transactions = unified_transactions[start_idx:end_idx]
        
        # Clean responses for UUID-only system
        cleaned_transactions = []
        for tx in paginated_transactions:
            tx_dict = tx.dict()
            cleaned_tx = uuid_processor.clean_response(tx_dict)
            cleaned_transactions.append(UnifiedTransaction(**cleaned_tx))
        
        return cleaned_transactions
        
    except Exception as e:
        logger.error(f"Error fetching unified transactions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ========================================  
# MAIN APPLICATION MOUNT
# ========================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )