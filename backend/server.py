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

class InventoryItem(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    bill_id: str
    bill: Optional[Bill] = None
    note: Optional[str] = None
    added_by: Optional[str] = "system"  # user who added to inventory
    batch_id: Optional[str] = None  # group bills added together
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
class AddToInventoryRequest(BaseModel):
    bill_ids: List[str]
    note: Optional[str] = None
    batch_name: Optional[str] = None

class InventoryStats(BaseModel):
    total_bills: int
    available_bills: int
    pending_bills: int
    sold_bills: int
    total_value: float

class InventoryResponse(BaseModel):
    id: str
    bill_id: str
    customer_code: str
    full_name: Optional[str] = None
    address: Optional[str] = None
    amount: Optional[float] = None
    billing_cycle: Optional[str] = None
    provider_region: str
    status: str
    note: Optional[str] = None
    batch_id: Optional[str] = None
    created_at: datetime

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

# External API bill checking function
async def external_check_bill(customer_code: str, provider_region: ProviderRegion) -> CheckBillResult:
    """Check bill via external n8n webhook"""
    import aiohttp
    import json as json_lib
    
    # Map provider region to external format
    provider_mapping = {
        ProviderRegion.MIEN_BAC: "mien_bac",
        ProviderRegion.MIEN_NAM: "mien_nam", 
        ProviderRegion.HCMC: "hcmc"
    }
    
    external_provider = provider_mapping.get(provider_region, "mien_nam")
    
    # Prepare payload for external webhook
    payload = {
        "bills": [
            {
                "customer_id": customer_code,
                "electric_provider": external_provider,
                "provider_name": external_provider,
                "contractNumber": customer_code,
                "sku": "ELECTRIC_BILL"
            }
        ],
        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
        "request_id": f"fpt_bill_manager_{str(uuid.uuid4())[:8]}",
        "webhookUrl": "https://n8n.phamthanh.net/webhook/checkbill",
        "executionMode": "production"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://n8n.phamthanh.net/webhook/checkbill",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=30
            ) as response:
                response_text = await response.text()
                
                # Parse response - n8n returns array format
                try:
                    response_data = json_lib.loads(response_text)
                    if isinstance(response_data, list) and len(response_data) > 0:
                        first_item = response_data[0]
                        
                        # Check if successful response (has bill data)
                        if "error" not in first_item and "customer_code" in str(first_item):
                            # Successful bill found
                            bill_data = {
                                "id": str(uuid.uuid4()),
                                "gateway": Gateway.FPT,
                                "customer_code": customer_code,
                                "provider_region": provider_region,
                                "provider_name": external_provider,
                                "full_name": first_item.get("full_name"),
                                "address": first_item.get("address"),
                                "amount": first_item.get("amount"),
                                "billing_cycle": first_item.get("billing_cycle"),
                                "status": BillStatus.AVAILABLE,
                                "meta": first_item,
                                "created_at": datetime.now(timezone.utc).isoformat(),
                                "updated_at": datetime.now(timezone.utc).isoformat()
                            }
                            
                            # Save to database
                            await db.bills.update_one(
                                {"customer_code": customer_code, "gateway": Gateway.FPT},
                                {"$set": bill_data},
                                upsert=True
                            )
                            
                            return CheckBillResult(
                                customer_code=customer_code,
                                full_name=first_item.get("full_name"),
                                address=first_item.get("address"),
                                amount=first_item.get("amount"),
                                billing_cycle=first_item.get("billing_cycle"),
                                status="OK"
                            )
                        else:
                            # Error response - extract message from nested error
                            error_message = "Mã không tồn tại"
                            
                            if "error" in first_item and "message" in first_item["error"]:
                                full_message = first_item["error"]["message"]
                                
                                # Method 1: Try to extract Vietnamese error message using regex
                                import re
                                vietnamese_patterns = [
                                    r'"message":"([^"]*(?:không nợ cước)[^"]*)"',
                                    r'"message":"([^"]*(?:không tồn tại)[^"]*)"', 
                                    r'"message":"([^"]*(?:không hợp lệ)[^"]*)"',
                                    r'"message":"([^"]*(?:lỗi)[^"]*)"'
                                ]
                                
                                for pattern in vietnamese_patterns:
                                    match = re.search(pattern, full_message, re.IGNORECASE)
                                    if match:
                                        error_message = match.group(1)
                                        break
                                        
                                # Method 2: If no Vietnamese message found, try JSON parsing
                                if error_message == "Mã không tồn tại":
                                    try:
                                        # Handle escaped JSON string
                                        clean_message = full_message
                                        if '400 - "' in clean_message:
                                            # Extract JSON part after "400 - "
                                            json_start = clean_message.find('400 - "') + 7
                                            json_part = clean_message[json_start:-1]  # Remove trailing quote
                                            json_part = json_part.replace('\\"', '"')  # Unescape quotes
                                            
                                            nested_data = json_lib.loads(json_part)
                                            if "error" in nested_data and "message" in nested_data["error"]:
                                                error_message = nested_data["error"]["message"]
                                    except Exception as e:
                                        logger.debug(f"JSON parsing failed, using regex fallback: {e}")
                                        
                            return CheckBillResult(
                                customer_code=customer_code,
                                status="ERROR",
                                errors={"code": "EXTERNAL_API_ERROR", "message": error_message}
                            )
                    else:
                        return CheckBillResult(
                            customer_code=customer_code,
                            status="ERROR", 
                            errors={"code": "INVALID_RESPONSE", "message": "Phản hồi không hợp lệ từ hệ thống"}
                        )
                        
                except json_lib.JSONDecodeError:
                    return CheckBillResult(
                        customer_code=customer_code,
                        status="ERROR",
                        errors={"code": "PARSE_ERROR", "message": "Không thể phân tích phản hồi"}
                    )
                    
    except Exception as e:
        logger.error(f"Error calling external webhook for {customer_code}: {str(e)}")
        return CheckBillResult(
            customer_code=customer_code,
            status="ERROR",
            errors={"code": "CONNECTION_ERROR", "message": f"Lỗi kết nối: {str(e)}"}
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
            result = await external_check_bill(cleaned_code, request.provider_region)
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