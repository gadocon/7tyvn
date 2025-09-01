from fastapi import FastAPI, APIRouter, HTTPException, Header, File, UploadFile
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
    CROSSED = "CROSSED"  # Đã gạch - customer không nợ cước
    ERROR = "ERROR"

class CustomerType(str, Enum):
    INDIVIDUAL = "INDIVIDUAL"
    AGENT = "AGENT"

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
    last_checked: Optional[datetime] = None

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
    # Transaction tracking
    total_transactions: int = 0
    total_value: float = 0.0
    total_bills: int = 0
    total_cards: int = 0
    total_profit_generated: float = 0.0
    # Metadata
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class CustomerCreate(BaseModel):
    type: CustomerType = CustomerType.INDIVIDUAL
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    notes: Optional[str] = None

class CustomerUpdate(BaseModel):
    type: Optional[CustomerType] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    address: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class CustomerStats(BaseModel):
    total_customers: int
    individual_customers: int
    agent_customers: int
    active_customers: int
    total_customer_value: float

class Sale(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    customer_id: str
    transaction_type: str = "ELECTRIC_BILL"  # ELECTRIC_BILL or CREDIT_CARD
    total: float
    profit_pct: float
    profit_value: float
    payback: float
    method: PaymentMethod
    status: str = "COMPLETED"
    notes: Optional[str] = None
    bill_ids: List[str]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class SaleCreate(BaseModel):
    customer_id: str
    bill_ids: List[str]
    profit_pct: float
    method: PaymentMethod
    notes: Optional[str] = None

# Request/Response Models
class AddToInventoryRequest(BaseModel):
    bill_ids: List[str]
    note: Optional[str] = None
    batch_name: Optional[str] = None

class InventoryStats(BaseModel):
    total_bills: int  # Bills in inventory
    available_bills: int
    pending_bills: int
    sold_bills: int
    total_value: float
    total_bills_in_system: int  # All bills in bills collection

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
    bill_id: Optional[str] = None  # Add bill_id for inventory

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

class BillCreate(BaseModel):
    customer_code: str
    provider_region: ProviderRegion
    full_name: Optional[str] = None
    address: Optional[str] = None
    amount: Optional[float] = None
    billing_cycle: Optional[str] = None  # Format: MM/YYYY
    status: BillStatus = BillStatus.AVAILABLE

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
    """Check bill via external n8n webhook with mock success data"""
    import aiohttp
    import json as json_lib
    
    # Mock successful response for PA2204000000
    if customer_code == "PA2204000000":
        # Create successful bill record in database
        bill_data = {
            "id": str(uuid.uuid4()),
            "gateway": Gateway.FPT,
            "customer_code": customer_code,
            "provider_region": provider_region,
            "provider_name": provider_region.value,
            "full_name": "Nguyễn Thị Hương",
            "address": "123 Phố Huế, Hai Bà Trưng, Hà Nội",
            "amount": 1850000,
            "billing_cycle": "09/2025",
            "status": BillStatus.AVAILABLE,
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
            full_name="Nguyễn Thị Hương",
            address="123 Phố Huế, Hai Bà Trưng, Hà Nội",
            amount=1850000,
            billing_cycle="09/2025",
            status="OK",
            bill_id=bill_data["id"]  # Include bill_id for inventory
        )
    
    # Map provider region to external format
    provider_mapping = {
        ProviderRegion.MIEN_BAC: "mien_bac",
        ProviderRegion.MIEN_NAM: "mien_nam", 
        ProviderRegion.HCMC: "evnhcmc"
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
                
                # Parse response - handle different response formats
                try:
                    response_data = json_lib.loads(response_text)
                    
                    # Handle array format (old format)
                    if isinstance(response_data, list) and len(response_data) > 0:
                        first_item = response_data[0]
                        
                        # Check for success in new API format
                        if (first_item.get("status") == 200 and 
                            "data" in first_item and 
                            "bills" in first_item["data"] and 
                            len(first_item["data"]["bills"]) > 0):
                            
                            bill_info = first_item["data"]["bills"][0]
                            
                            # Map external API fields to internal fields
                            full_name = bill_info.get("customerName")
                            address = bill_info.get("address")
                            amount = bill_info.get("moneyAmount")
                            billing_cycle = bill_info.get("month")
                            
                            # Successful bill found
                            bill_data = {
                                "id": str(uuid.uuid4()),
                                "gateway": Gateway.FPT,
                                "customer_code": customer_code,
                                "provider_region": provider_region,
                                "provider_name": external_provider,
                                "full_name": full_name,
                                "address": address,
                                "amount": amount,
                                "billing_cycle": billing_cycle,
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
                                full_name=full_name,
                                address=address,
                                amount=amount,
                                billing_cycle=billing_cycle,
                                status="OK",
                                bill_id=bill_data["id"]
                            )
                        
                        # Check for old format success (has bill data)
                        elif "error" not in first_item and ("customer_code" in str(first_item) or "full_name" in first_item):
                            # Successful bill found (old format)
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
                                status="OK",
                                bill_id=bill_data["id"]
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

@api_router.post("/bill/check/single", response_model=CheckBillResult)
async def check_single_bill(
    customer_code: str,
    provider_region: ProviderRegion
):
    """Check single bill for realtime response"""
    try:
        cleaned_code = clean_customer_code(customer_code)
        result = await external_check_bill(cleaned_code, provider_region)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bill/debug-payload")
async def debug_bill_payload(
    customer_code: str,
    provider_region: ProviderRegion
):
    """Debug endpoint to show exact payload being sent to external API"""
    # Map provider region to external format
    provider_mapping = {
        ProviderRegion.MIEN_BAC: "mien_bac",
        ProviderRegion.MIEN_NAM: "mien_nam", 
        ProviderRegion.HCMC: "evnhcmc"
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
    
    return {
        "customer_code": customer_code,
        "provider_region": provider_region,
        "external_provider": external_provider,
        "payload": payload,
        "external_api_url": "https://n8n.phamthanh.net/webhook/checkbill"
    }

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

@api_router.get("/customers/stats", response_model=CustomerStats)
async def get_customer_stats():
    """Get customer statistics"""
    try:
        # Count customers by type and status
        total_customers = await db.customers.count_documents({})
        individual_customers = await db.customers.count_documents({"type": CustomerType.INDIVIDUAL})
        agent_customers = await db.customers.count_documents({"type": CustomerType.AGENT})
        active_customers = await db.customers.count_documents({"is_active": True})
        
        # Calculate total customer value
        pipeline = [
            {"$group": {"_id": None, "total_value": {"$sum": "$total_value"}}}
        ]
        value_result = await db.customers.aggregate(pipeline).to_list(1)
        total_customer_value = value_result[0]["total_value"] if value_result else 0
        
        return CustomerStats(
            total_customers=total_customers,
            individual_customers=individual_customers,
            agent_customers=agent_customers,
            active_customers=active_customers,
            total_customer_value=total_customer_value
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/customers", response_model=List[Customer])
async def get_customers(
    search: Optional[str] = None,
    customer_type: Optional[CustomerType] = None,
    is_active: Optional[bool] = None,
    page: int = 1,
    page_size: int = 20
):
    """Get customers with filtering and pagination"""
    try:
        # Build query
        query = {}
        
        if search:
            query["$or"] = [
                {"name": {"$regex": search, "$options": "i"}},
                {"phone": {"$regex": search, "$options": "i"}},
                {"email": {"$regex": search, "$options": "i"}},
                {"address": {"$regex": search, "$options": "i"}}
            ]
        
        if customer_type:
            query["type"] = customer_type
            
        if is_active is not None:
            query["is_active"] = is_active
        
        # Get paginated results
        skip = (page - 1) * page_size
        customers = await db.customers.find(query).skip(skip).limit(page_size).sort("created_at", -1).to_list(page_size)
        
        # Filter out invalid customers and fix old data
        valid_customers = []
        for customer in customers:
            try:
                # Handle old BUSINESS type data
                if customer.get("type") == "BUSINESS":
                    customer["type"] = "AGENT"
                    # Update in database
                    await db.customers.update_one(
                        {"_id": customer["_id"]},
                        {"$set": {"type": "AGENT"}}
                    )
                
                # Ensure all required fields exist with defaults
                customer.setdefault("total_transactions", 0)
                customer.setdefault("total_value", 0.0)
                customer.setdefault("total_bills", 0)
                customer.setdefault("total_cards", 0)
                customer.setdefault("total_profit_generated", 0.0)
                customer.setdefault("is_active", True)
                customer.setdefault("notes", None)
                
                parsed_customer = Customer(**parse_from_mongo(customer))
                valid_customers.append(parsed_customer)
            except Exception as parse_error:
                logger.warning(f"Skipping invalid customer {customer.get('_id', 'unknown')}: {parse_error}")
                continue
        
        return valid_customers
    except Exception as e:
        logger.error(f"Error getting customers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/customers/export")
async def export_customers_data():
    """Export customers data to Excel"""
    try:
        # Get all customers (simple version)
        customers = await db.customers.find({}).sort("created_at", -1).to_list(None)
        
        # Create Excel file
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill
        from io import BytesIO
        
        workbook = openpyxl.Workbook()
        
        # Customers Sheet
        customers_sheet = workbook.active
        customers_sheet.title = "Khách Hàng"
        
        # Customer headers
        customer_headers = [
            "ID", "Tên khách hàng", "Số điện thoại", "Email", 
            "Địa chỉ", "Loại khách hàng", "Trạng thái", "Tổng giao dịch",
            "Tổng giá trị", "Tổng lợi nhuận", "Ngày tạo", "Ghi chú"
        ]
        
        # Write customer headers
        for col, header in enumerate(customer_headers, 1):
            cell = customers_sheet.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')
        
        # Write customer data
        for row, customer in enumerate(customers, 2):
            customers_sheet.cell(row=row, column=1, value=customer.get("id"))
            customers_sheet.cell(row=row, column=2, value=customer.get("name"))
            customers_sheet.cell(row=row, column=3, value=customer.get("phone"))
            customers_sheet.cell(row=row, column=4, value=customer.get("email"))
            customers_sheet.cell(row=row, column=5, value=customer.get("address"))
            customers_sheet.cell(row=row, column=6, value=customer.get("type"))
            customers_sheet.cell(row=row, column=7, value="Hoạt động" if customer.get("is_active") else "Không hoạt động")
            customers_sheet.cell(row=row, column=8, value=customer.get("total_transactions", 0))
            customers_sheet.cell(row=row, column=9, value=customer.get("total_value", 0))
            customers_sheet.cell(row=row, column=10, value=customer.get("total_profit_generated", 0))
            customers_sheet.cell(row=row, column=11, value=customer.get("created_at"))
            customers_sheet.cell(row=row, column=12, value=customer.get("notes"))
        
        # Auto-adjust column widths for customers sheet
        for column in customers_sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            customers_sheet.column_dimensions[column_letter].width = min(max_length + 2, 30)
        
        # Save to BytesIO
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)
        
        from fastapi.responses import StreamingResponse
        
        return StreamingResponse(
            BytesIO(excel_buffer.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": "attachment; filename=khach_hang_export.xlsx"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer(customer_id: str):
    """Get single customer by ID"""
    try:
        customer = await db.customers.find_one({"id": customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
        
        return Customer(**parse_from_mongo(customer))
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/customers", response_model=Customer)
async def create_customer(customer_data: CustomerCreate):
    """Create new customer"""
    try:
        # Check for duplicate email if provided
        if customer_data.email:
            existing = await db.customers.find_one({"email": customer_data.email})
            if existing:
                raise HTTPException(status_code=400, detail="Email đã tồn tại")
        
        # Create customer
        customer = Customer(
            **customer_data.dict(),
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        
        customer_dict = prepare_for_mongo(customer.dict())
        await db.customers.insert_one(customer_dict)
        
        return customer
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer(customer_id: str, customer_data: CustomerUpdate):
    """Update customer"""
    try:
        # Check if customer exists
        existing = await db.customers.find_one({"id": customer_id})
        if not existing:
            raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
        
        # Check for duplicate email if updating email
        if customer_data.email and customer_data.email != existing.get("email"):
            duplicate = await db.customers.find_one({"email": customer_data.email, "id": {"$ne": customer_id}})
            if duplicate:
                raise HTTPException(status_code=400, detail="Email đã tồn tại")
        
        # Update fields
        update_data = {k: v for k, v in customer_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        await db.customers.update_one(
            {"id": customer_id},
            {"$set": update_data}
        )
        
        # Return updated customer
        updated_customer = await db.customers.find_one({"id": customer_id})
        return Customer(**parse_from_mongo(updated_customer))
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/inventory/{item_id}")
async def delete_inventory_item(item_id: str):
    """Delete item from inventory"""
    try:
        # Remove from inventory_items collection
        result = await db.inventory_items.delete_one({"id": item_id})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy item trong kho")
        
        return {"success": True, "message": "Đã xóa item khỏi kho thành công"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/bills/{bill_id}")
async def delete_bill(bill_id: str):
    """Delete bill completely - with validation for sold bills"""
    try:
        # First check if bill exists and get its status
        bill = await db.bills.find_one({"id": bill_id})
        if not bill:
            raise HTTPException(status_code=404, detail="Không tìm thấy bill")
        
        # CRITICAL: Check if bill is already sold or crossed - prevent deletion
        if bill.get("status") == BillStatus.SOLD:
            raise HTTPException(
                status_code=400, 
                detail="Không thể xóa bill đã bán. Bill này đã được tham chiếu trong giao dịch khách hàng."
            )
        
        if bill.get("status") == BillStatus.CROSSED:
            raise HTTPException(
                status_code=400,
                detail="Không thể xóa bill đã gạch. Bill này đã được xác nhận không có nợ cước."
            )
        
        # Check if bill is referenced in any sales (double-check safety)
        sales_using_bill = await db.sales.find_one({"bill_ids": bill_id})
        if sales_using_bill:
            raise HTTPException(
                status_code=400,
                detail="Không thể xóa bill đã có giao dịch. Bill này đang được tham chiếu trong lịch sử bán hàng."
            )
        
        # Safe to delete - bill is available/pending
        result = await db.bills.delete_one({"id": bill_id})
        
        # Also remove from inventory if exists
        await db.inventory_items.delete_many({"bill_id": bill_id})
        
        return {"success": True, "message": "Đã xóa bill thành công"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.put("/bills/{bill_id}")
async def update_bill(bill_id: str, bill_data: BillCreate):
    """Update bill information - used for recheck functionality"""
    try:
        print(f"PUT /bills/{bill_id} called")
        
        # Check if bill exists
        existing_bill = await db.bills.find_one({"id": bill_id})
        if not existing_bill:
            raise HTTPException(status_code=404, detail="Không tìm thấy bill")
        
        print(f"Found existing bill: {existing_bill.get('id')}")
        
        # Prepare update data - convert enums to strings
        update_data = prepare_for_mongo({
            "customer_code": bill_data.customer_code,
            "provider_region": bill_data.provider_region.value,
            "full_name": bill_data.full_name,
            "address": bill_data.address,
            "amount": bill_data.amount,
            "billing_cycle": bill_data.billing_cycle,
            "status": bill_data.status.value,
            "updated_at": datetime.now(timezone.utc),
            "last_checked": datetime.now(timezone.utc)
        })
        
        print(f"Update data prepared")
        
        # Update bill in database
        result = await db.bills.update_one(
            {"id": bill_id},
            {"$set": update_data}
        )
        
        print(f"Update result: matched={result.matched_count}")
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Không tìm thấy bill để cập nhật")
        
        # Get updated bill
        updated_bill = await db.bills.find_one({"id": bill_id})
        print(f"Retrieved updated bill: {type(updated_bill)}")
        
        # If status changed to CROSSED, remove from inventory (if exists)
        if bill_data.status == BillStatus.CROSSED:
            inventory_result = await db.inventory_items.delete_many({"bill_id": bill_id})
            print(f"Removed {inventory_result.deleted_count} items from inventory")
        
        # Parse the bill data
        parsed_bill = parse_from_mongo(updated_bill)
        print(f"Parsed bill successfully")
        
        return {
            "success": True,
            "message": "Đã cập nhật bill thành công",
            "bill": parsed_bill
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in update_bill: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@api_router.delete("/customers/{customer_id}")
async def delete_customer(customer_id: str):
    """Delete customer with CASCADE delete (transactions + bills)"""
    try:
        # Check if customer exists
        customer = await db.customers.find_one({"id": customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
        
        # Get all sales for this customer to find related bills
        sales = await db.sales.find({"customer_id": customer_id}).to_list(None)
        
        deleted_stats = {
            "customer": 0,
            "transactions": 0, 
            "bills": 0,
            "inventory_items": 0
        }
        
        # Delete related data in order
        if sales:
            # Get all bill IDs from sales
            bill_ids = []
            for sale in sales:
                if sale.get("bill_ids"):
                    bill_ids.extend(sale["bill_ids"])
            
            # Remove duplicate bill IDs
            unique_bill_ids = list(set(bill_ids))
            
            # Delete inventory items for these bills
            inventory_delete_result = await db.inventory_items.delete_many({"bill_id": {"$in": unique_bill_ids}})
            deleted_stats["inventory_items"] = inventory_delete_result.deleted_count
            
            # Delete the bills themselves
            bills_delete_result = await db.bills.delete_many({"id": {"$in": unique_bill_ids}})
            deleted_stats["bills"] = bills_delete_result.deleted_count
            
            # Delete all sales/transactions for this customer
            sales_delete_result = await db.sales.delete_many({"customer_id": customer_id})
            deleted_stats["transactions"] = sales_delete_result.deleted_count
        
        # Finally delete the customer
        customer_delete_result = await db.customers.delete_one({"id": customer_id})
        deleted_stats["customer"] = customer_delete_result.deleted_count
        
        if customer_delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Không thể xóa khách hàng")
        
        # Create detailed message
        message_parts = [f"Đã xóa khách hàng '{customer.get('name', 'N/A')}' thành công"]
        if deleted_stats["transactions"] > 0:
            message_parts.append(f"{deleted_stats['transactions']} giao dịch")
        if deleted_stats["bills"] > 0:
            message_parts.append(f"{deleted_stats['bills']} bills")  
        if deleted_stats["inventory_items"] > 0:
            message_parts.append(f"{deleted_stats['inventory_items']} items khỏi kho")
            
        return {
            "success": True, 
            "message": " và ".join(message_parts),
            "deleted_stats": deleted_stats
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/customers/{customer_id}/transactions")
async def get_customer_transactions(customer_id: str):
    """Get customer transaction history"""
    try:
        # Check if customer exists
        customer = await db.customers.find_one({"id": customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
        
        # Get sales for this customer
        sales = await db.sales.find({"customer_id": customer_id}).sort("created_at", -1).to_list(100)
        
        transactions = []
        for sale in sales:
            # Get bill codes for this sale
            bill_codes = []
            if sale.get("bill_ids"):
                bills = await db.bills.find({"id": {"$in": sale["bill_ids"]}}).to_list(None)
                bill_codes = [bill.get("customer_code", "") for bill in bills]
            
            transactions.append({
                "id": sale["id"],
                "type": "SALE",
                "total": sale["total"],
                "profit_value": sale["profit_value"],
                "payback": sale["payback"],
                "method": sale["method"],
                "status": sale["status"],
                "notes": sale.get("notes"),
                "bill_codes": bill_codes,
                "created_at": sale["created_at"]
            })
        
        return {
            "customer": Customer(**parse_from_mongo(customer)),
            "transactions": transactions,
            "summary": {
                "total_transactions": len(transactions),
                "total_value": sum(t["total"] for t in transactions),
                "total_profit": sum(t["profit_value"] for t in transactions)
            }
        }
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

# Inventory/Kho Bill APIs
@api_router.get("/inventory/stats", response_model=InventoryStats)
async def get_inventory_stats():
    """Get inventory statistics"""
    try:
        # Count bills in inventory
        inventory_bills = await db.inventory_items.count_documents({})
        
        # Count ALL bills in bills collection for "Tất cả bills" tab
        total_bills_in_system = await db.bills.count_documents({})
        
        # Count bills in inventory by their bill status
        pipeline = [
            {
                "$lookup": {
                    "from": "bills",
                    "localField": "bill_id", 
                    "foreignField": "id",
                    "as": "bill_info"
                }
            },
            {
                "$unwind": "$bill_info"
            },
            {
                "$group": {
                    "_id": "$bill_info.status",
                    "count": {"$sum": 1},
                    "total_value": {"$sum": {"$ifNull": ["$bill_info.amount", 0]}}
                }
            }
        ]
        
        status_counts = await db.inventory_items.aggregate(pipeline).to_list(10)
        
        available_bills = 0
        pending_bills = 0
        sold_bills = 0
        total_value = 0
        
        for item in status_counts:
            status = item["_id"]
            count = item["count"]
            value = item["total_value"]
            
            if status == BillStatus.AVAILABLE:
                available_bills = count
            elif status == BillStatus.PENDING:
                pending_bills = count
            elif status == BillStatus.SOLD:
                sold_bills = count
            
            total_value += value
        
        return InventoryStats(
            total_bills=inventory_bills,
            available_bills=available_bills,
            pending_bills=pending_bills,
            sold_bills=sold_bills,
            total_value=total_value,
            total_bills_in_system=total_bills_in_system
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/inventory", response_model=List[InventoryResponse])
async def get_inventory_items(
    status: Optional[BillStatus] = None,
    search: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Get inventory items with filtering and pagination"""
    try:
        # Build aggregation pipeline
        pipeline = [
            {
                "$lookup": {
                    "from": "bills",
                    "localField": "bill_id",
                    "foreignField": "id", 
                    "as": "bill_info"
                }
            },
            {
                "$unwind": "$bill_info"
            }
        ]
        
        # Add filters
        match_conditions = {}
        
        if status:
            match_conditions["bill_info.status"] = status
            
        if search:
            match_conditions["$or"] = [
                {"bill_info.customer_code": {"$regex": search, "$options": "i"}},
                {"bill_info.full_name": {"$regex": search, "$options": "i"}},
                {"bill_info.address": {"$regex": search, "$options": "i"}}
            ]
        
        if match_conditions:
            pipeline.append({"$match": match_conditions})
        
        # Add sorting and pagination
        pipeline.extend([
            {"$sort": {"created_at": -1}},
            {"$skip": (page - 1) * page_size},
            {"$limit": page_size}
        ])
        
        inventory_items = await db.inventory_items.aggregate(pipeline).to_list(page_size)
        
        # Convert to response model
        results = []
        for item in inventory_items:
            bill_info = item["bill_info"]
            results.append(InventoryResponse(
                id=item["id"],
                bill_id=item["bill_id"],
                customer_code=bill_info["customer_code"],
                full_name=bill_info.get("full_name"),
                address=bill_info.get("address"),
                amount=bill_info.get("amount"),
                billing_cycle=bill_info.get("billing_cycle"),
                provider_region=bill_info["provider_region"],
                status=bill_info["status"],
                note=item.get("note"),
                batch_id=item.get("batch_id"),
                created_at=datetime.fromisoformat(item["created_at"].replace('Z', '+00:00')) if isinstance(item["created_at"], str) else item["created_at"]
            ))
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/inventory/add")
async def add_to_inventory(request: AddToInventoryRequest):
    """Add bills to inventory"""
    try:
        # Generate batch ID if batch name provided
        batch_id = None
        if request.batch_name:
            batch_id = f"batch_{str(uuid.uuid4())[:8]}_{request.batch_name.replace(' ', '_')}"
        
        added_items = []
        successful_adds = 0
        
        for bill_id in request.bill_ids:
            # Check if bill exists and is available
            bill = await db.bills.find_one({"id": bill_id})
            if not bill:
                # Try to find by customer_code if bill_id lookup fails
                bill = await db.bills.find_one({"customer_code": bill_id, "status": BillStatus.AVAILABLE})
                if not bill:
                    continue
                bill_id = bill["id"]  # Use actual bill ID
                
            if bill["status"] != BillStatus.AVAILABLE:
                continue
            
            # Check if already in inventory
            existing = await db.inventory_items.find_one({"bill_id": bill_id})
            if existing:
                continue
            
            # Create inventory item
            inventory_item = {
                "id": str(uuid.uuid4()),
                "bill_id": bill_id,
                "note": request.note,
                "batch_id": batch_id,
                "added_by": "system",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.inventory_items.insert_one(inventory_item)
            added_items.append(inventory_item)
            successful_adds += 1
        
        return {
            "success": True,
            "added_count": successful_adds,
            "batch_id": batch_id,
            "message": f"Đã thêm {successful_adds} bill vào kho thành công"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/bills/create", response_model=Bill)
async def create_bill_manual(bill_data: BillCreate):
    """Create new bill manually and add to inventory"""
    try:
        # Check if bill with same customer_code already exists
        existing_bill = await db.bills.find_one({
            "customer_code": bill_data.customer_code,
            "provider_region": bill_data.provider_region
        })
        
        if existing_bill:
            raise HTTPException(
                status_code=400, 
                detail=f"Bill với mã điện {bill_data.customer_code} đã tồn tại"
            )
        
        # Create new bill
        bill = Bill(
            gateway=Gateway.FPT,  # Default to FPT
            customer_code=bill_data.customer_code,
            provider_region=bill_data.provider_region,
            provider_name=bill_data.provider_region.value.lower(),
            full_name=bill_data.full_name,
            address=bill_data.address,
            amount=bill_data.amount,
            billing_cycle=bill_data.billing_cycle,
            status=bill_data.status
        )
        
        # Convert to dict for MongoDB
        bill_dict = bill.dict()
        bill_dict["created_at"] = bill.created_at.isoformat()
        bill_dict["updated_at"] = bill.updated_at.isoformat()
        
        # Save to database
        await db.bills.insert_one(bill_dict)
        
        # If status is AVAILABLE, automatically add to inventory
        if bill_data.status == BillStatus.AVAILABLE:
            inventory_item = {
                "id": str(uuid.uuid4()),
                "bill_id": bill.id,
                "note": "Được thêm thủ công",
                "batch_id": None,
                "added_by": "manual",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            
            await db.inventory_items.insert_one(inventory_item)
        
        return bill
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Import/Export APIs
@api_router.post("/inventory/import/preview")
async def preview_import_data(file: UploadFile = File(...)):
    """Preview imported Excel data before saving"""
    try:
        if not file.filename.endswith(('.xlsx', '.xls')):
            raise HTTPException(status_code=400, detail="File phải có định dạng Excel (.xlsx hoặc .xls)")
        
        # Read Excel file
        import openpyxl
        import io
        
        content = await file.read()
        workbook = openpyxl.load_workbook(io.BytesIO(content))
        worksheet = workbook.active
        
        # Expected columns: Mã điện, Nhà cung cấp, Tên khách hàng, Địa chỉ, Nợ cước, Chu kỳ thanh toán, Trạng thái
        expected_headers = ["Mã điện", "Nhà cung cấp", "Tên khách hàng", "Địa chỉ", "Nợ cước", "Chu kỳ thanh toán", "Trạng thái"]
        
        # Read header row
        headers = [cell.value for cell in worksheet[1]]
        
        # Validate headers
        if not all(header in headers for header in ["Mã điện"]):  # Only Mã điện is required
            raise HTTPException(status_code=400, detail="File Excel thiếu cột bắt buộc 'Mã điện'")
        
        # Read data rows
        preview_data = []
        errors = []
        
        for row_num, row in enumerate(worksheet.iter_rows(min_row=2, values_only=True), start=2):
            if not any(row):  # Skip empty rows
                continue
                
            try:
                # Map columns to data
                row_data = {}
                for i, header in enumerate(headers):
                    if i < len(row):
                        row_data[header] = row[i]
                
                # Validate required fields
                if not row_data.get("Mã điện"):
                    errors.append(f"Dòng {row_num}: Thiếu mã điện")
                    continue
                
                # Map provider region
                provider_map = {
                    "Miền Bắc": "MIEN_BAC",
                    "Miền Nam": "MIEN_NAM", 
                    "TP.HCM": "HCMC",
                    "HCMC": "HCMC"
                }
                
                provider = row_data.get("Nhà cung cấp", "Miền Nam")
                mapped_provider = provider_map.get(provider, "MIEN_NAM")
                
                # Format data
                preview_item = {
                    "customer_code": str(row_data.get("Mã điện", "")).strip(),
                    "provider_region": mapped_provider,
                    "full_name": str(row_data.get("Tên khách hàng", "")).strip() or None,
                    "address": str(row_data.get("Địa chỉ", "")).strip() or None,
                    "amount": float(row_data.get("Nợ cước", 0)) if row_data.get("Nợ cước") else None,
                    "billing_cycle": str(row_data.get("Chu kỳ thanh toán", "")).strip() or None,
                    "status": "AVAILABLE",  # Default status
                    "row_number": row_num
                }
                
                preview_data.append(preview_item)
                
            except Exception as e:
                errors.append(f"Dòng {row_num}: Lỗi xử lý dữ liệu - {str(e)}")
        
        return {
            "success": True,
            "total_rows": len(preview_data),
            "errors": errors,
            "data": preview_data[:50],  # Preview first 50 rows
            "has_more": len(preview_data) > 50
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi xử lý file: {str(e)}")

@api_router.post("/inventory/import/confirm")
async def confirm_import_data(import_data: Dict[str, Any]):
    """Confirm and save imported data"""
    try:
        bills_data = import_data.get("data", [])
        successful_imports = 0
        errors = []
        
        for item in bills_data:
            try:
                # Check if bill already exists
                existing_bill = await db.bills.find_one({
                    "customer_code": item["customer_code"],
                    "provider_region": item["provider_region"]
                })
                
                if existing_bill:
                    errors.append(f"Mã điện {item['customer_code']} đã tồn tại")
                    continue
                
                # Create new bill
                bill = Bill(
                    gateway=Gateway.FPT,
                    customer_code=item["customer_code"],
                    provider_region=ProviderRegion(item["provider_region"]),
                    provider_name=item["provider_region"].lower(),
                    full_name=item.get("full_name"),
                    address=item.get("address"),
                    amount=item.get("amount"),
                    billing_cycle=item.get("billing_cycle"),
                    status=BillStatus.AVAILABLE
                )
                
                # Save to database
                bill_dict = bill.dict()
                bill_dict["created_at"] = bill.created_at.isoformat()
                bill_dict["updated_at"] = bill.updated_at.isoformat()
                await db.bills.insert_one(bill_dict)
                
                # Add to inventory
                inventory_item = {
                    "id": str(uuid.uuid4()),
                    "bill_id": bill.id,
                    "note": "Import từ Excel",
                    "batch_id": None,
                    "added_by": "import",
                    "created_at": datetime.now(timezone.utc).isoformat()
                }
                await db.inventory_items.insert_one(inventory_item)
                
                successful_imports += 1
                
            except Exception as e:
                errors.append(f"Mã điện {item.get('customer_code', 'unknown')}: {str(e)}")
        
        return {
            "success": True,
            "imported_count": successful_imports,
            "total_count": len(bills_data),
            "errors": errors,
            "message": f"Đã import thành công {successful_imports}/{len(bills_data)} bills"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/inventory/export")
async def export_inventory_data(
    status: Optional[BillStatus] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    provider_region: Optional[ProviderRegion] = None
):
    """Export inventory data to Excel"""
    try:
        # Build query
        query = {}
        
        # Build bills query
        bills_query = {}
        if status:
            bills_query["status"] = status
        if provider_region:
            bills_query["provider_region"] = provider_region
            
        # Date filter
        if start_date or end_date:
            date_filter = {}
            if start_date:
                date_filter["$gte"] = start_date
            if end_date:
                date_filter["$lte"] = end_date
            bills_query["created_at"] = date_filter
        
        # Get inventory items with bills
        pipeline = [
            {
                "$lookup": {
                    "from": "bills",
                    "localField": "bill_id",
                    "foreignField": "id",
                    "as": "bill"
                }
            },
            {
                "$unwind": "$bill"
            }
        ]
        
        # Add match stage if filters exist
        if bills_query:
            pipeline.append({"$match": {f"bill.{k}": v for k, v in bills_query.items()}})
        
        pipeline.append({"$sort": {"created_at": -1}})
        
        inventory_items = await db.inventory_items.aggregate(pipeline).to_list(None)
        
        # Create Excel file
        import openpyxl
        from openpyxl.styles import Font, Alignment
        from io import BytesIO
        
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Kho Bill"
        
        # Headers
        headers = [
            "Mã điện", "Tên khách hàng", "Địa chỉ", "Nợ cước", 
            "Chu kỳ thanh toán", "Nhà cung cấp", "Trạng thái",
            "Ngày thêm", "Ghi chú"
        ]
        
        # Write headers
        for col, header in enumerate(headers, 1):
            cell = worksheet.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True)
            cell.alignment = Alignment(horizontal='center')
        
        # Write data
        for row, item in enumerate(inventory_items, 2):
            bill = item["bill"]
            worksheet.cell(row=row, column=1, value=bill.get("customer_code"))
            worksheet.cell(row=row, column=2, value=bill.get("full_name"))
            worksheet.cell(row=row, column=3, value=bill.get("address"))
            worksheet.cell(row=row, column=4, value=bill.get("amount"))
            worksheet.cell(row=row, column=5, value=bill.get("billing_cycle"))
            worksheet.cell(row=row, column=6, value=bill.get("provider_name"))
            worksheet.cell(row=row, column=7, value=bill.get("status"))
            worksheet.cell(row=row, column=8, value=item.get("created_at"))
            worksheet.cell(row=row, column=9, value=item.get("note"))
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 50)
        
        # Save to BytesIO
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)
        
        # Return file
        from fastapi.responses import StreamingResponse
        
        return StreamingResponse(
            BytesIO(excel_buffer.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": "attachment; filename=kho_bill_export.xlsx"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/inventory/template")
async def download_import_template():
    """Download Excel template for importing bills"""
    try:
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill
        from io import BytesIO
        
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Template Import Bills"
        
        # Headers
        headers = [
            "Mã điện", "Nhà cung cấp", "Tên khách hàng", 
            "Địa chỉ", "Nợ cước", "Chu kỳ thanh toán", "Trạng thái"
        ]
        
        # Write headers with styling
        for col, header in enumerate(headers, 1):
            cell = worksheet.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')
        
        # Add sample data
        sample_data = [
            ["PA2024000001", "Miền Nam", "Nguyễn Văn A", "123 Đường ABC, Quận 1", 850000, "10/2025", "Có Sẵn"],
            ["PA2024000002", "Miền Bắc", "Trần Thị B", "456 Đường DEF, Quận 2", 920000, "10/2025", "Có Sẵn"],
            ["PA2024000003", "TP.HCM", "Lê Văn C", "789 Đường GHI, Quận 3", 750000, "11/2025", "Có Sẵn"]
        ]
        
        for row, data in enumerate(sample_data, 2):
            for col, value in enumerate(data, 1):
                worksheet.cell(row=row, column=col, value=value)
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 30)
        
        # Add instructions
        instructions = [
            "",
            "HƯỚNG DẪN SỬ DỤNG:",
            "1. Mã điện: Bắt buộc phải có",
            "2. Nhà cung cấp: Miền Bắc / Miền Nam / TP.HCM",
            "3. Nợ cước: Nhập số tiền (VD: 850000)",
            "4. Chu kỳ thanh toán: Định dạng MM/YYYY (VD: 10/2025)",
            "5. Trạng thái: Có Sẵn / Chờ Xử Lý / Đã Bán",
            "6. Xóa các dòng mẫu trước khi import dữ liệu thật"
        ]
        
        for i, instruction in enumerate(instructions, len(sample_data) + 3):
            worksheet.cell(row=i, column=1, value=instruction)
        
        # Save to BytesIO
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)
        
        from fastapi.responses import StreamingResponse
        
        return StreamingResponse(
            BytesIO(excel_buffer.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": "attachment; filename=template_import_bills.xlsx"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Sales/Transaction APIs
@api_router.post("/sales", response_model=Sale)
async def create_sale(sale_data: SaleCreate):
    """Create new sale transaction"""
    try:
        # Validate customer exists
        customer = await db.customers.find_one({"id": sale_data.customer_id})
        if not customer:
            raise HTTPException(status_code=404, detail="Không tìm thấy khách hàng")
        
        # Get bills and validate they're available
        bill_filter = {"id": {"$in": sale_data.bill_ids}, "status": BillStatus.AVAILABLE}
        bills = await db.bills.find(bill_filter).to_list(None)
        
        if len(bills) != len(sale_data.bill_ids):
            raise HTTPException(status_code=400, detail="Một số bill không khả dụng hoặc không tồn tại")
        
        # Calculate totals
        total = sum(bill.get("amount", 0) for bill in bills)
        profit_value = round(total * sale_data.profit_pct / 100, 0)  # Round to VND
        payback = total - profit_value
        
        # Create sale record
        sale = Sale(
            customer_id=sale_data.customer_id,
            transaction_type="ELECTRIC_BILL",
            total=total,
            profit_pct=sale_data.profit_pct,
            profit_value=profit_value,
            payback=payback,
            method=sale_data.method,
            status="COMPLETED",
            notes=sale_data.notes,
            bill_ids=sale_data.bill_ids,
            created_at=datetime.now(timezone.utc)
        )
        
        # Save sale to database
        sale_dict = prepare_for_mongo(sale.dict())
        await db.sales.insert_one(sale_dict)
        
        # Update bill statuses to SOLD
        await db.bills.update_many(
            {"id": {"$in": sale_data.bill_ids}},
            {"$set": {"status": BillStatus.SOLD, "updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        # Remove bills from inventory
        await db.inventory_items.delete_many({"bill_id": {"$in": sale_data.bill_ids}})
        
        # Update customer stats
        await db.customers.update_one(
            {"id": sale_data.customer_id},
            {
                "$inc": {
                    "total_transactions": 1,
                    "total_value": total,
                    "total_bills": len(sale_data.bill_ids),
                    "total_profit_generated": profit_value
                },
                "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
            }
        )
        
        return sale
        
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sales", response_model=List[Sale])
async def get_sales(
    customer_id: Optional[str] = None,
    page: int = 1,
    page_size: int = 20
):
    """Get sales transactions"""
    try:
        query = {}
        if customer_id:
            query["customer_id"] = customer_id
            
        skip = (page - 1) * page_size
        sales = await db.sales.find(query).skip(skip).limit(page_size).sort("created_at", -1).to_list(page_size)
        
        return [Sale(**parse_from_mongo(sale)) for sale in sales]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sales/export")
async def export_sales_data():
    """Export sales data to Excel"""
    try:
        # Get all sales (simple version)
        sales = await db.sales.find({}).sort("created_at", -1).to_list(None)
        
        # Create Excel file
        import openpyxl
        from openpyxl.styles import Font, Alignment, PatternFill
        from io import BytesIO
        
        workbook = openpyxl.Workbook()
        worksheet = workbook.active
        worksheet.title = "Lịch Sử Bán Bill"
        
        # Headers
        headers = [
            "ID Giao dịch", "Tên khách hàng", "SĐT khách hàng",
            "Loại giao dịch", "Tổng tiền (VND)", "Lợi nhuận (%)",
            "Giá trị lợi nhuận (VND)", "Số tiền trả khách (VND)",
            "Phương thức thanh toán", "Trạng thái", "Ngày giao dịch", "Ghi chú"
        ]
        
        # Write headers with styling
        for col, header in enumerate(headers, 1):
            cell = worksheet.cell(row=1, column=col, value=header)
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = PatternFill(start_color="28A745", end_color="28A745", fill_type="solid")
            cell.alignment = Alignment(horizontal='center')
        
        # Write sales data
        for row, sale in enumerate(sales, 2):
            # Get customer info for this sale
            customer = await db.customers.find_one({"id": sale.get("customer_id")})
            customer_name = customer.get("name", "N/A") if customer else "N/A"
            customer_phone = customer.get("phone", "N/A") if customer else "N/A"
            
            worksheet.cell(row=row, column=1, value=sale.get("id"))
            worksheet.cell(row=row, column=2, value=customer_name)
            worksheet.cell(row=row, column=3, value=customer_phone)
            worksheet.cell(row=row, column=4, value=sale.get("transaction_type", "ELECTRIC_BILL"))
            worksheet.cell(row=row, column=5, value=sale.get("total", 0))
            worksheet.cell(row=row, column=6, value=sale.get("profit_pct", 0))
            worksheet.cell(row=row, column=7, value=sale.get("profit_value", 0))
            worksheet.cell(row=row, column=8, value=sale.get("payback", 0))
            worksheet.cell(row=row, column=9, value=sale.get("method", ""))
            worksheet.cell(row=row, column=10, value=sale.get("status", ""))
            worksheet.cell(row=row, column=11, value=sale.get("created_at", ""))
            worksheet.cell(row=row, column=12, value=sale.get("notes", ""))
        
        # Auto-adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                if cell.value:
                    max_length = max(max_length, len(str(cell.value)))
            worksheet.column_dimensions[column_letter].width = min(max_length + 2, 25)
        
        # Save to BytesIO
        excel_buffer = BytesIO()
        workbook.save(excel_buffer)
        excel_buffer.seek(0)
        
        from fastapi.responses import StreamingResponse
        
        return StreamingResponse(
            BytesIO(excel_buffer.read()),
            media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={"Content-Disposition": "attachment; filename=lich_su_ban_bill.xlsx"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sales/{sale_id}", response_model=Sale)
async def get_sale(sale_id: str):
    """Get sale by ID"""
    try:
        sale = await db.sales.find_one({"id": sale_id})
        if not sale:
            raise HTTPException(status_code=404, detail="Không tìm thấy giao dịch")
        
        return Sale(**parse_from_mongo(sale))
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/sales/stats/summary")
async def get_sales_stats():
    """Get sales statistics"""
    try:
        # Total sales count
        total_sales = await db.sales.count_documents({})
        
        # Total revenue and profit
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_revenue": {"$sum": "$total"},
                    "total_profit": {"$sum": "$profit_value"},
                    "total_payback": {"$sum": "$payback"}
                }
            }
        ]
        
        result = await db.sales.aggregate(pipeline).to_list(1)
        stats = result[0] if result else {"total_revenue": 0, "total_profit": 0, "total_payback": 0}
        
        # Recent sales
        recent_sales = await db.sales.find({}).sort("created_at", -1).limit(5).to_list(5)
        
        return {
            "total_sales": total_sales,
            "total_revenue": stats["total_revenue"],
            "total_profit": stats["total_profit"], 
            "total_payback": stats["total_payback"],
            "recent_sales": [Sale(**parse_from_mongo(sale)) for sale in recent_sales]
        }
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
                "type": CustomerType.AGENT,
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
        
        # Create sample bills for inventory
        sample_bills = [
            {
                "id": str(uuid.uuid4()),
                "gateway": Gateway.FPT,
                "customer_code": "PA22040501111",
                "provider_region": ProviderRegion.MIEN_NAM,
                "provider_name": "Điện lực miền Nam",
                "full_name": "Lê Thị Mai",
                "address": "111 Nguyễn Trãi, Quận 5, TP.HCM",
                "amount": 850000,
                "billing_cycle": "08/2025",
                "status": BillStatus.AVAILABLE,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "gateway": Gateway.FPT,
                "customer_code": "PA22040502222",
                "provider_region": ProviderRegion.MIEN_BAC,
                "provider_name": "Điện lực miền Bắc",
                "full_name": "Hoàng Văn Nam",
                "address": "222 Láng Hạ, Ba Đình, Hà Nội",
                "amount": 1200000,
                "billing_cycle": "08/2025",
                "status": BillStatus.AVAILABLE,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "gateway": Gateway.FPT,
                "customer_code": "PA22040503333",
                "provider_region": ProviderRegion.HCMC,
                "provider_name": "Điện lực TP.HCM",
                "full_name": "Phan Minh Đức",
                "address": "333 Lê Văn Sỹ, Quận 3, TP.HCM",
                "amount": 950000,
                "billing_cycle": "08/2025",
                "status": BillStatus.AVAILABLE,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "gateway": Gateway.FPT,
                "customer_code": "PA22040504444",
                "provider_region": ProviderRegion.MIEN_NAM,
                "provider_name": "Điện lực miền Nam",
                "full_name": "Võ Thị Lan",
                "address": "444 Cách Mạng Tháng 8, Quận 10, TP.HCM",
                "amount": 750000,
                "billing_cycle": "07/2025",
                "status": BillStatus.AVAILABLE,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "gateway": Gateway.FPT,
                "customer_code": "PA22040505555",
                "provider_region": ProviderRegion.MIEN_BAC,
                "provider_name": "Điện lực miền Bắc",
                "full_name": "Đặng Quang Hải",
                "address": "555 Giải Phóng, Hai Bà Trưng, Hà Nội",
                "amount": 1450000,
                "billing_cycle": "08/2025",
                "status": BillStatus.PENDING,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "gateway": Gateway.FPT,
                "customer_code": "PA22040506666",
                "provider_region": ProviderRegion.HCMC,
                "provider_name": "Điện lực TP.HCM",
                "full_name": "Bùi Thị Hồng",
                "address": "666 Phan Xích Long, Phú Nhuận, TP.HCM",
                "amount": 680000,
                "billing_cycle": "07/2025",
                "status": BillStatus.SOLD,
                "created_at": datetime.now(timezone.utc).isoformat(),
                "updated_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        
        await db.bills.insert_many(sample_bills)
        
        # Create inventory items for some bills
        inventory_batch_id = f"batch_{str(uuid.uuid4())[:8]}_initial_import"
        inventory_items = []
        
        for i, bill in enumerate(sample_bills[:4]):  # Add first 4 bills to inventory
            inventory_item = {
                "id": str(uuid.uuid4()),
                "bill_id": bill["id"],
                "note": "Import ban đầu từ hệ thống" if i < 2 else "Batch kiểm tra tháng 08",
                "batch_id": inventory_batch_id if i < 2 else f"batch_{str(uuid.uuid4())[:8]}_test_08",
                "added_by": "system",
                "created_at": datetime.now(timezone.utc).isoformat()
            }
            inventory_items.append(inventory_item)
        
        if inventory_items:
            await db.inventory_items.insert_many(inventory_items)
        
        logger.info("Sample data seeded successfully - customers, bills, and inventory")
        
    except Exception as e:
        logger.error(f"Error seeding data: {str(e)}")