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
from pydantic import BaseModel, Field, validator, EmailStr

# Authentication imports
from passlib.context import CryptContext
import jwt
from datetime import timedelta

# UUID utilities
from uuid_utils import generate_uuid, is_valid_uuid, uuid_processor

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
    except jwt.JWTError:
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
        # For now, return empty stats - to be implemented
        return {
            "total": 0,
            "active": 0,
            "expired": 0,
            "this_month": 0
        }
    except Exception as e:
        logger.error(f"Error fetching credit card stats: {e}")
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
    """Single bill check - UUID only system"""
    try:
        logger.info(f"Checking bill: {customer_code} in {provider_region}")
        
        # Check if bill exists in database
        bill = await db.bills.find_one({
            "customer_code": customer_code,
            "provider_region": provider_region
        })
        
        if bill:
            # Bill found
            bill_clean = uuid_processor.clean_response(bill)
            return {
                "success": True,
                "status": "OK",
                "message": "Bill found",
                "customer_code": customer_code,
                "amount": bill.get("amount", 0),
                "billing_cycle": bill.get("billing_cycle", "N/A"),
                "bill_status": bill.get("status", "UNKNOWN"),
                "bill": bill_clean
            }
        else:
            # Bill not found - this is normal, not an error
            return {
                "success": True,
                "status": "NOT_FOUND", 
                "message": "Bill not found",
                "customer_code": customer_code,
                "amount": 0,
                "billing_cycle": "N/A",
                "bill_status": "NOT_FOUND",
                "bill": None
            }
            
    except Exception as e:
        logger.error(f"Error checking bill {customer_code}: {e}")
        return {
            "success": True,
            "status": "ERROR",
            "message": f"Error checking bill: {str(e)}",
            "customer_code": customer_code,
            "amount": 0,
            "billing_cycle": "N/A",
            "status": "ERROR", 
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

@app.get("/api/customers/{customer_id}/transactions")
async def get_customer_transactions(customer_id: str):
    """Get transactions for specific customer"""
    try:
        if not is_valid_uuid(customer_id):
            raise HTTPException(status_code=400, detail="Invalid UUID format")
        
        # Get sales for this customer
        sales = await db.sales.find({"customer_id": customer_id}).to_list(100)
        
        # Clean responses
        cleaned_sales = [uuid_processor.clean_response(sale) for sale in sales]
        return cleaned_sales
        
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
                bill_codes = [bill.get("customer_code", "N/A") for bill in bills]
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
                        code=bill.get("customer_code"),
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