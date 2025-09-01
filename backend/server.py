from fastapi import FastAPI, APIRouter, HTTPException, Header
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum
import re
import json


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI(title="FPT Bill Manager API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class Gateway(str, Enum):
    FPT = "FPT"
    SHOPEE = "SHOPEE"

class ProviderRegion(str, Enum):
    MIEN_BAC = "MIEN_BAC"
    MIEN_NAM = "MIEN_NAM"
    HCMC = "HCMC"

class BillStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    PENDING = "PENDING"
    SOLD = "SOLD"
    ERROR = "ERROR"

class CustomerType(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    BUSINESS = "BUSINESS"

class PaymentMethod(str, Enum):
    CASH = "CASH"
    BANK_TRANSFER = "BANK_TRANSFER"
    OTHER = "OTHER"

# Models
class Bill(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    gateway: Gateway
    customer_code: str
    provider_region: ProviderRegion
    provider_name: Optional[str] = None
    full_name: Optional[str] = None
    address: Optional[str] = None
    amount: Optional[float] = None
    billing_cycle: Optional[str] = None
    raw_status: Optional[str] = None
    status: BillStatus = BillStatus.AVAILABLE
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Customer(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: CustomerType = CustomerType.INDIVIDUAL
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class Sale(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    total: float
    profit_pct: float
    profit_value: float
    payback: float
    method: PaymentMethod
    status: str = "COMPLETED"
    notes: Optional[str] = None
    bill_ids: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Request/Response Models
class CheckBillRequest(BaseModel):
    gateway: Gateway
    provider_region: ProviderRegion
    codes: List[str]

class CheckBillResult(BaseModel):
    customer_code: str
    full_name: Optional[str] = None
    address: Optional[str] = None
    amount: Optional[float] = None
    billing_cycle: Optional[str] = None
    status: str
    errors: Optional[Dict[str, str]] = None

class CheckBillResponse(BaseModel):
    items: List[CheckBillResult]
    summary: Dict[str, int]

class DashboardStats(BaseModel):
    total_bills: int
    available_bills: int
    sold_bills: int
    total_customers: int
    total_revenue: float
    recent_activities: List[Dict[str, Any]]

class WebhookPayload(BaseModel):
    bills: List[Dict[str, Any]]
    timestamp: int
    request_id: str
    webhook_url: str
    execution_mode: str

# Utility functions
def clean_customer_code(code: str) -> str:
    """Clean customer code by removing fees and extra characters"""
    # Remove everything after comma (fees)
    code = code.split(',')[0].strip()
    # Remove any non-alphanumeric characters except specific ones
    code = re.sub(r'[^\w]', '', code)
    return code.upper()

def map_provider_region(electric_provider: str) -> ProviderRegion:
    """Map electric provider string to enum"""
    mapping = {
        "mien_bac": ProviderRegion.MIEN_BAC,
        "mien_nam": ProviderRegion.MIEN_NAM,
        "hcmc": ProviderRegion.HCMC
    }
    return mapping.get(electric_provider.lower(), ProviderRegion.MIEN_NAM)

def prepare_for_mongo(data):
    """Convert datetime objects to ISO strings for MongoDB storage"""
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            elif isinstance(value, dict):
                result[key] = prepare_for_mongo(value)
            elif isinstance(value, list):
                result[key] = [prepare_for_mongo(item) if isinstance(item, dict) else item for item in value]
            else:
                result[key] = value
        return result
    return data

def parse_from_mongo(item):
    """Parse datetime strings from MongoDB"""
    if isinstance(item, dict):
        for key, value in item.items():
            if isinstance(value, str) and key.endswith('_at'):
                try:
                    item[key] = datetime.fromisoformat(value.replace('Z', '+00:00'))
                except:
                    pass
    return item

# Mock bill checking function
async def mock_check_bill(customer_code: str, provider_region: ProviderRegion) -> CheckBillResult:
    """Mock function to simulate bill checking"""
    # Mock data for demonstration
    mock_data = {
        "PA22040522471": {
            "full_name": "Nguyễn Văn A",
            "address": "123 Đường ABC, Quận 1, TP.HCM",
            "amount": 1250000,
            "billing_cycle": "08/2025"
        },
        "PA22040506503": {
            "full_name": "Trần Thị B", 
            "address": "456 Đường XYZ, Quận 2, TP.HCM",
            "amount": 890000,
            "billing_cycle": "08/2025"
        },
        "PA22060724572": {
            "full_name": "Lê Văn C",
            "address": "789 Đường DEF, Quận 3, TP.HCM", 
            "amount": 1560000,
            "billing_cycle": "08/2025"
        }
    }
    
    if customer_code in mock_data:
        data = mock_data[customer_code]
        # Create bill record in database
        bill_data = {
            "id": str(uuid.uuid4()),
            "gateway": Gateway.FPT,
            "customer_code": customer_code,
            "provider_region": provider_region,
            "provider_name": provider_region.value,
            "full_name": data["full_name"],
            "address": data["address"],
            "amount": data["amount"],
            "billing_cycle": data["billing_cycle"],
            "status": BillStatus.AVAILABLE,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Upsert bill (update if exists, create if not)
        await db.bills.update_one(
            {"customer_code": customer_code, "gateway": Gateway.FPT},
            {"$set": bill_data},
            upsert=True
        )
        
        return CheckBillResult(
            customer_code=customer_code,
            full_name=data["full_name"],
            address=data["address"],
            amount=data["amount"],
            billing_cycle=data["billing_cycle"],
            status="OK"
        )
    else:
        return CheckBillResult(
            customer_code=customer_code,
            status="ERROR",
            errors={"code": "NOT_FOUND", "message": "Mã hóa đơn không tồn tại"}
        )

# API Routes
@api_router.get("/dashboard/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Count bills by status
        total_bills = await db.bills.count_documents({})
        available_bills = await db.bills.count_documents({"status": BillStatus.AVAILABLE})
        sold_bills = await db.bills.count_documents({"status": BillStatus.SOLD})
        
        # Count customers
        total_customers = await db.customers.count_documents({})
        
        # Calculate total revenue from sales
        pipeline = [
            {"$group": {"_id": None, "total": {"$sum": "$profit_value"}}}
        ]
        revenue_result = await db.sales.aggregate(pipeline).to_list(1)
        total_revenue = revenue_result[0]["total"] if revenue_result else 0
        
        # Get recent activities (latest 5 sales)
        recent_sales = await db.sales.find().sort("created_at", -1).limit(5).to_list(5)
        recent_activities = []
        
        for sale in recent_sales:
            customer = await db.customers.find_one({"id": sale["customer_id"]})
            customer_name = customer["name"] if customer else "Không xác định"
            
            recent_activities.append({
                "id": sale["id"],
                "type": "sale",
                "description": f"Bán bill cho {customer_name}",
                "amount": sale["total"],
                "profit": sale["profit_value"],
                "created_at": sale["created_at"]
            })
        
        return DashboardStats(
            total_bills=total_bills,
            available_bills=available_bills,
            sold_bills=sold_bills,
            total_customers=total_customers,
            total_revenue=total_revenue,
            recent_activities=recent_activities
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bill/check", response_model=CheckBillResponse)
async def check_bills(request: CheckBillRequest):
    """Check multiple bills"""
    try:
        results = []
        ok_count = 0
        error_count = 0
        
        for code in request.codes:
            if not code.strip():
                continue
                
            cleaned_code = clean_customer_code(code)
            result = await mock_check_bill(cleaned_code, request.provider_region)
            results.append(result)
            
            if result.status == "OK":
                ok_count += 1
            else:
                error_count += 1
        
        return CheckBillResponse(
            items=results,
            summary={"ok": ok_count, "error": error_count}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/bills", response_model=List[Bill])
async def get_bills(status: Optional[BillStatus] = None, limit: int = 50):
    """Get bills with optional status filter"""
    try:
        query = {}
        if status:
            query["status"] = status
            
        bills = await db.bills.find(query).limit(limit).to_list(limit)
        return [Bill(**parse_from_mongo(bill)) for bill in bills]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/customers", response_model=List[Customer])
async def get_customers(limit: int = 50):
    """Get customers"""
    try:
        customers = await db.customers.find({}).limit(limit).to_list(limit)
        return [Customer(**parse_from_mongo(customer)) for customer in customers]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/webhook/checkbill")
async def webhook_checkbill(
    payload: WebhookPayload,
    x_api_key: str = Header(None, alias="X-API-KEY")
):
    """Webhook endpoint for receiving bill check results from FPT/Shopee"""
    try:
        # Log the webhook (in production, verify API key and signature)
        webhook_log = {
            "id": str(uuid.uuid4()),
            "gateway": Gateway.FPT,  # Default to FPT
            "request_id": payload.request_id,
            "payload": payload.dict(),
            "status": "RECEIVED",
            "received_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.webhook_logs.insert_one(webhook_log)
        
        # Process bills
        for bill_data in payload.bills:
            customer_code = bill_data.get("customer_id") or bill_data.get("contractNumber")
            electric_provider = bill_data.get("electric_provider", "mien_nam")
            provider_region = map_provider_region(electric_provider)
            
            # Create/update bill record
            bill_record = {
                "id": str(uuid.uuid4()),
                "gateway": Gateway.FPT,
                "customer_code": customer_code,
                "provider_region": provider_region,
                "provider_name": bill_data.get("provider_name", electric_provider),
                "status": BillStatus.AVAILABLE,
                "meta": bill_data,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.bills.update_one(
                {"customer_code": customer_code, "gateway": Gateway.FPT},
                {"$set": bill_record},
                upsert=True
            )
        
        # Update webhook log status
        await db.webhook_logs.update_one(
            {"request_id": payload.request_id},
            {"$set": {"status": "PROCESSED", "processed_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return {"accepted": True}
    except Exception as e:
        logger.error(f"Webhook processing error: {str(e)}")
        return {"accepted": False, "error": str(e)}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

# Seed some sample data on startup
@app.on_event("startup")
async def seed_data():
    """Seed sample data for development"""
    try:
        # Check if data already exists
        existing_customers = await db.customers.count_documents({})
        if existing_customers > 0:
            return
            
        # Create sample customers
        sample_customers = [
            {
                "id": str(uuid.uuid4()),
                "type": CustomerType.INDIVIDUAL,
                "name": "Nguyễn Văn A",
                "phone": "0901234567",
                "email": "nguyenvana@example.com",
                "address": "123 Đường ABC, Quận 1, TP.HCM",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "type": CustomerType.INDIVIDUAL,
                "name": "Trần Thị B",
                "phone": "0907654321",
                "email": "tranthib@example.com",
                "address": "456 Đường XYZ, Quận 2, TP.HCM",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "type": CustomerType.BUSINESS,
                "name": "Công ty TNHH ABC",
                "phone": "0281234567",
                "email": "info@abc.com",
                "address": "789 Đường DEF, Quận 3, TP.HCM",
                "is_active": True,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        await db.customers.insert_many(sample_customers)
        logger.info("Sample data seeded successfully")
        
    except Exception as e:
        logger.error(f"Error seeding data: {str(e)}")