# 7ty.vn CRM - Comprehensive System Documentation

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Project Architecture](#project-architecture)
3. [Business Logic Flow](#business-logic-flow)
4. [Database Structure](#database-structure)
5. [API Endpoints](#api-endpoints)
6. [Technical Guidelines](#technical-guidelines)
7. [System Objectives](#system-objectives)
8. [Deployment & Configuration](#deployment--configuration)

---

## 🎯 System Overview

**7ty.vn CRM** là hệ thống quản lý khách hàng mini-CRM chuyên dụng cho việc quản lý bill điện FPT/Shopee và dịch vụ đáo thẻ tín dụng.

### Core Features
- **Bill Management**: Quản lý bill điện FPT/Shopee
- **Customer 360°**: Tổng quan khách hàng toàn diện
- **Credit Card DAO**: Dịch vụ đáo thẻ tín dụng (POS & Bill)
- **Transaction Tracking**: Theo dõi giao dịch với business ID
- **Inventory Management**: Quản lý kho bill
- **Analytics & Reports**: Báo cáo và phân tích

---

## 🏗️ Project Architecture

### Technology Stack
```
Frontend: React.js + TailwindCSS + Recharts
Backend: FastAPI (Python) + Motor (MongoDB Driver)
Database: MongoDB
Authentication: JWT + bcrypt
UI Components: Shadcn/ui
```

### Architecture Pattern
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │────│   Backend       │────│   Database      │
│   React.js      │    │   FastAPI       │    │   MongoDB       │
│   Port: 3000    │    │   Port: 8001    │    │   Port: 27017   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Directory Structure
```
/app/
├── backend/
│   ├── server.py           # Main FastAPI application
│   ├── uuid_utils.py       # UUID utilities and validation
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Backend environment variables
├── frontend/
│   ├── src/
│   │   ├── App.js         # Main React application
│   │   ├── components/    # UI components
│   │   └── contexts/      # React contexts
│   ├── package.json       # Node.js dependencies
│   └── .env              # Frontend environment variables
├── scripts/
│   ├── clean_and_seed_database.py
│   ├── data_migration.py
│   └── data_standards.py
└── docs/                  # Documentation files
```

---

## 🔄 Business Logic Flow

### 1. User Authentication Flow
```mermaid
graph TD
    A[Login Page] --> B{Validate Credentials}
    B -->|Valid| C[Generate JWT Token]
    B -->|Invalid| D[Show Error]
    C --> E[Set Auth Context]
    E --> F[Navigate to Dashboard]
    D --> A
```

### 2. Bill Management Flow
```mermaid
graph TD
    A[Bill Import/Create] --> B[Validate Bill Data]
    B --> C[Store in Bills Collection]
    C --> D[Add to Inventory]
    D --> E[Update Stats]
    E --> F[Available for Sale]
    F --> G{Customer Purchase}
    G -->|Yes| H[Update Status: SOLD]
    G -->|No| I[Remain: AVAILABLE]
    H --> J[Update Customer Metrics]
```

### 3. Credit Card DAO Flow
```mermaid
graph TD
    A[Customer Request DAO] --> B{DAO Method}
    B -->|POS| C[POS DAO Transaction]
    B -->|BILL| D[Bill DAO Transaction]
    C --> E[Generate Business ID: D+last4+DDMM]
    D --> F[Select Bills from Inventory]
    F --> G[Update Bill Status: SOLD]
    E --> H[Update Card Status]
    G --> H
    H --> I[Update Customer Metrics]
    I --> J[Record Transaction]
```

### 4. Customer 360° View Flow
```mermaid
graph TD
    A[Customer Selection] --> B[Fetch Customer Data]
    B --> C[Fetch Credit Cards]
    C --> D[Fetch Transactions History]
    D --> E[Fetch Recent Activities]
    E --> F[Calculate Metrics]
    F --> G[Determine Customer Tier]
    G --> H[Display 360° View]
```

---

## 🗄️ Database Structure

### MongoDB Collections

#### 1. Users Collection
```javascript
{
  "_id": ObjectId,
  "id": "uuid-string",           // UUID primary key
  "username": "string",
  "email": "string",
  "phone": "string",
  "password": "hashed-password",
  "full_name": "string",
  "role": "ADMIN|MANAGER|USER",
  "is_active": boolean,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### 2. Customers Collection
```javascript
{
  "_id": ObjectId,
  "id": "uuid-string",           // UUID primary key
  "name": "string",
  "phone": "string",
  "email": "string",
  "address": "string",
  "type": "INDIVIDUAL|AGENCY",
  "tier": "Regular|Premium|VIP",
  "is_active": boolean,
  "total_spent": number,
  "total_profit_generated": number,
  "total_transactions": number,
  "total_dao_amount": number,
  "total_dao_transactions": number,
  "total_dao_profit": number,
  "notes": "string",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### 3. Credit Cards Collection
```javascript
{
  "_id": ObjectId,
  "id": "uuid-string",           // UUID primary key
  "customer_id": "uuid-string",  // Foreign key to customers
  "card_number": "string",       // Full card number (unmasked in DB)
  "cardholder_name": "string",
  "bank_name": "string",
  "card_type": "VISA|MASTERCARD|JCB|AMEX",
  "expiry_date": "string",       // MM/YY format
  "ccv": "string",
  "statement_date": number,      // Day of month (1-31)
  "payment_due_date": number,    // Day of month (1-31)
  "credit_limit": number,
  "available_credit": number,    // Calculated field
  "last_dao_date": ISODate,
  "next_due_date": "string",     // YYYY-MM-DD format
  "days_until_due": number,
  "status": "CHUA_DEN_HAN|CAN_DAO|DA_DAO|QUA_HAN",
  "notes": "string",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### 4. Bills Collection
```javascript
{
  "_id": ObjectId,
  "id": "composite-id",          // Format: customer_code+MMYY
  "gateway": "FPT|SHOPEE",
  "customer_code": "string",     // TEST1000000-TEST1000049
  "provider_region": "MIEN_BAC|MIEN_NAM|HCMC",
  "amount": number,
  "billing_cycle": "string",     // MM/YYYY
  "status": "AVAILABLE|SOLD",
  "sold_at": ISODate,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### 5. Sales Collection
```javascript
{
  "_id": ObjectId,
  "id": "uuid-string",           // UUID primary key
  "customer_id": "uuid-string",  // Foreign key to customers
  "bill_ids": ["composite-id"],  // Array of bill IDs
  "total": number,               // Total sale amount
  "profit_value": number,        // Profit amount
  "profit_pct": number,          // Profit percentage
  "notes": "string",
  "status": "COMPLETED",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### 6. DAO Transactions Collection
```javascript
{
  "_id": ObjectId,
  "id": "uuid-string",           // Technical UUID
  "transaction_id": "string",    // Business ID: D+last4+DDMM
  "customer_id": "uuid-string",  // Foreign key to customers
  "credit_card_id": "uuid-string", // Foreign key to credit_cards
  "card_number": "string",       // Full card number
  "bank_name": "string",
  "amount": number,              // DAO amount
  "profit_value": number,        // Profit from DAO
  "fee_rate": number,            // Fee percentage (default: 3.0)
  "payment_method": "POS|BILL",
  "transaction_type": "CREDIT_DAO_POS|CREDIT_DAO_BILL",
  "bill_ids": ["composite-id"],  // For BILL method
  "pos_code": "string",          // For POS method
  "transaction_code": "string",
  "notes": "string",
  "status": "COMPLETED",
  "created_at": ISODate,
  "updated_at": ISODate
}
```

#### 7. Inventory Items Collection
```javascript
{
  "_id": ObjectId,
  "id": "uuid-string",           // UUID primary key
  "bill_id": "composite-id",     // Reference to bills
  "added_at": ISODate,
  "status": "AVAILABLE"
}
```

---

## 🔌 API Endpoints

### Authentication Endpoints
```
POST   /api/auth/login                    # User login
GET    /api/auth/me                       # Get current user info
```

### Customer Management
```
GET    /api/customers                     # List customers with pagination
POST   /api/customers                     # Create new customer
GET    /api/customers/{id}                # Get customer by ID
PUT    /api/customers/{id}                # Update customer
DELETE /api/customers/{id}                # Delete customer
GET    /api/customers/{id}/detailed-profile # Customer 360° view
GET    /api/customers/{id}/transactions-summary # Customer transaction history
GET    /api/customers/stats               # Customer statistics
```

### Credit Card Management
```
GET    /api/credit-cards                  # List credit cards
POST   /api/credit-cards                  # Create credit card
GET    /api/credit-cards/{id}/detail      # Credit card detail with transactions
PUT    /api/credit-cards/{id}             # Update credit card
DELETE /api/credit-cards/{id}             # Delete credit card
GET    /api/credit-cards/stats            # Credit card statistics
```

### DAO (Credit Card Advance) Operations
```
POST   /api/credit-cards/{id}/dao         # Specific card DAO transaction
POST   /api/credit-cards/dao              # General DAO transaction
GET    /api/dao-transactions              # List DAO transactions
```

### Bill Management
```
GET    /api/bills                         # List bills
POST   /api/bills                         # Create bill
GET    /api/bills/{id}                    # Get bill by ID
PUT    /api/bills/{id}                    # Update bill
DELETE /api/bills/{id}                    # Delete bill
POST   /api/bill/check/single             # Bill validation
```

### Inventory Management
```
GET    /api/inventory                     # List inventory items
POST   /api/inventory                     # Add bill to inventory
DELETE /api/inventory/{id}                # Remove from inventory
GET    /api/inventory/stats               # Inventory statistics
```

### Sales Operations
```
GET    /api/sales                         # List sales
POST   /api/sales                         # Create sale transaction
GET    /api/sales/{id}                    # Get sale by ID
PUT    /api/sales/{id}                    # Update sale
```

### Transaction Management
```
GET    /api/transactions/unified          # Unified transaction view
PUT    /api/transactions/sale/{id}        # Update sale transaction
PUT    /api/transactions/credit-card/{id} # Update credit card transaction
GET    /api/transactions/stats            # Transaction statistics
```

### Dashboard & Analytics
```
GET    /api/stats/dashboard               # Dashboard statistics
GET    /api/activities/recent             # Recent activities
GET    /api/reports/charts/top-customers  # Top customers chart data
GET    /api/reports/charts/profit-loss    # Profit/loss chart data
```

---

## ⚙️ Technical Guidelines

### 1. UUID-Only System
```python
# All entity IDs use UUID format
import uuid
from uuid_utils import generate_uuid, is_valid_uuid

# Generate new UUID
entity_id = generate_uuid()

# Validate UUID
if not is_valid_uuid(entity_id):
    raise ValueError("Invalid UUID format")
```

### 2. Composite Bill IDs
```python
# Bills use composite ID format: customer_code+MMYY
# Example: TEST1000000+0125 = TEST10000000125
from uuid_utils import generate_composite_bill_id, is_valid_composite_bill_id

bill_id = generate_composite_bill_id(customer_code, month, year)
```

### 3. Business Transaction IDs for DAO
```python
# DAO transactions use business-friendly IDs
# Format: D + last4digits + DDMM + optional increment
# Example: D98550509, D98550509-2, D98550509-3

async def generate_dao_transaction_id(card_number: str) -> str:
    last_4_digits = card_number[-4:] if card_number else "0000"
    today = datetime.now(timezone.utc)
    day = today.strftime("%d")
    month = today.strftime("%m")
    base_id = f"D{last_4_digits}{day}{month}"
    
    # Check for existing IDs and increment if needed
    existing_count = await db.dao_transactions.count_documents({
        "transaction_id": {"$regex": f"^{base_id}"}
    })
    
    return base_id if existing_count == 0 else f"{base_id}-{existing_count + 1}"
```

### 4. MongoDB Serialization
```python
# Handle ObjectId serialization
def parse_from_mongo(item):
    """Convert MongoDB document to API response"""
    if item is None:
        return None
    
    # Remove MongoDB ObjectId
    item.pop("_id", None)
    
    # Convert datetime objects to ISO strings
    for key, value in item.items():
        if isinstance(value, datetime):
            item[key] = value.isoformat()
        elif isinstance(value, date):
            item[key] = value.isoformat()
        elif isinstance(value, time):
            item[key] = value.strftime('%H:%M:%S')
    
    return item
```

### 5. Credit Card Business Logic
```python
def calculate_card_status(next_due_date: str, last_dao_date: datetime = None) -> CardStatus:
    """Calculate card status based on due date"""
    today = datetime.now(timezone.utc).date()
    due_date = datetime.fromisoformat(next_due_date).date()
    days_until_due = (due_date - today).days
    
    if days_until_due > 7:
        return CardStatus.CHUA_DEN_HAN
    elif days_until_due > 0:
        return CardStatus.CAN_DAO
    else:
        return CardStatus.QUA_HAN

def update_card_after_dao(card_dict: dict, dao_amount: float) -> dict:
    """Update card fields after DAO transaction"""
    card_dict["available_credit"] = card_dict.get("credit_limit", 0) - dao_amount
    card_dict["last_dao_date"] = datetime.now(timezone.utc)
    card_dict["status"] = calculate_card_status(
        card_dict["next_due_date"],
        card_dict["last_dao_date"]
    ).value
    return card_dict
```

### 6. Frontend API Integration
```javascript
// Use environment variable for API URL
const API = process.env.REACT_APP_BACKEND_URL;

// Standard API call pattern
const fetchData = async () => {
  try {
    const response = await axios.get(`${API}/endpoint`);
    return response.data;
  } catch (error) {
    console.error("API Error:", error);
    toast.error("Có lỗi xảy ra");
    throw error;
  }
};
```

### 7. Error Handling
```python
# Backend error handling
try:
    # Business logic
    result = await process_data()
    return {"success": True, "data": result}
except HTTPException:
    raise  # Re-raise HTTP exceptions
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail=str(e))
```

### 8. Database Queries with UUID
```python
# Always use dual lookup for backward compatibility
async def find_customer(customer_id: str):
    """Find customer by UUID with dual lookup support"""
    return await db.customers.find_one({
        "$or": [
            {"id": customer_id},      # UUID field
            {"_id": ObjectId(customer_id)}  # MongoDB ObjectId (legacy)
        ]
    })
```

---

## 🎯 System Objectives

### Primary Objectives
1. **Efficient Bill Management**: Streamline FPT/Shopee bill handling
2. **Customer Relationship Management**: 360° customer view and analytics
3. **Credit Card DAO Services**: Automated đáo thẻ process with business IDs
4. **Transaction Tracking**: Comprehensive transaction history with proper IDs
5. **Inventory Management**: Real-time bill inventory tracking
6. **Data Consistency**: UUID-only architecture for clean data management

### Key Performance Indicators (KPIs)
- **Transaction Processing Time**: < 2 seconds per transaction
- **System Uptime**: 99.9% availability
- **Data Accuracy**: 100% transaction recording accuracy
- **User Experience**: < 3 clicks for common operations
- **Business ID Generation**: 100% unique business-friendly transaction IDs

### Business Value Propositions
1. **Reduced Manual Work**: Automated bill and transaction management
2. **Improved Customer Service**: Quick access to customer 360° view
3. **Business Intelligence**: Analytics and reporting for decision making
4. **Scalability**: Handle growing transaction volumes
5. **Compliance**: Proper transaction recording and audit trails

---

## 🚀 Deployment & Configuration

### Environment Variables

#### Backend (.env)
```bash
# Database Configuration
MONGO_URL=mongodb://localhost:27017/crm_7ty_vn

# Authentication
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# API Configuration
API_HOST=0.0.0.0
API_PORT=8001
```

#### Frontend (.env)
```bash
# Backend API URL
REACT_APP_BACKEND_URL=http://localhost:8001

# App Configuration
REACT_APP_NAME=7ty.vn CRM
REACT_APP_VERSION=2.0
```

### Service Management
```bash
# Start all services
sudo supervisorctl start all

# Restart specific service
sudo supervisorctl restart backend
sudo supervisorctl restart frontend

# Check service status
sudo supervisorctl status
```

### Database Initialization
```bash
# Run database setup
python scripts/clean_and_seed_database.py

# Create indexes for performance
python scripts/create_indexes.py
```

### Monitoring & Logs
```bash
# Backend logs
tail -f /var/log/supervisor/backend.*.log

# Frontend logs
tail -f /var/log/supervisor/frontend.*.log

# MongoDB logs
tail -f /var/log/mongodb/mongod.log
```

---

## 📊 Performance Metrics

### Database Performance
- **Query Response Time**: < 100ms for simple queries
- **Aggregation Pipeline**: < 500ms for complex analytics
- **Index Usage**: 95% of queries use indexes
- **Connection Pool**: Max 100 concurrent connections

### API Performance
- **Response Time**: < 200ms for CRUD operations
- **Throughput**: 1000+ requests per minute
- **Error Rate**: < 0.1%
- **Authentication**: < 50ms JWT validation

### Frontend Performance
- **Page Load Time**: < 2 seconds initial load
- **Component Rendering**: < 100ms per component
- **Bundle Size**: < 2MB compressed
- **Memory Usage**: < 50MB per session

---

## 🔒 Security Considerations

### Authentication & Authorization
- JWT-based authentication with refresh tokens
- Role-based access control (Admin/Manager/User)
- Password hashing with bcrypt
- Session timeout management

### Data Security
- Credit card numbers stored unmasked in database (business requirement)
- Frontend displays masked card numbers only
- Input validation and sanitization
- SQL injection prevention through MongoDB ODM

### API Security
- CORS configuration for frontend domain
- Rate limiting on authentication endpoints
- Request size limits
- Error message sanitization

---

## 📈 Future Enhancements

### Planned Features
1. **Advanced Analytics**: Machine learning insights
2. **Mobile App**: React Native mobile application
3. **API Integrations**: Third-party payment gateways
4. **Automated Workflows**: Business process automation
5. **Multi-tenant**: Support for multiple organizations

### Technical Improvements
1. **Caching Layer**: Redis for performance optimization
2. **Search Engine**: Elasticsearch for advanced search
3. **Message Queue**: RabbitMQ for background tasks
4. **Microservices**: Break down monolith architecture
5. **Container Orchestration**: Docker + Kubernetes deployment

---

## 📝 Maintenance Guidelines

### Regular Tasks
- **Daily**: Monitor system health and logs
- **Weekly**: Database performance analysis
- **Monthly**: Security updates and patches
- **Quarterly**: Performance optimization review

### Backup Strategy
- **Database**: Daily automated backups with 30-day retention
- **Application**: Code repository with version control
- **Configuration**: Environment files backup
- **Recovery**: Tested disaster recovery procedures

### Update Process
1. Development environment testing
2. Staging environment validation
3. Production deployment with rollback plan
4. Post-deployment monitoring
5. User communication and training

---

## 📞 Support & Contact

### Technical Support
- **System Admin**: admin@7ty.vn
- **Development Team**: dev@7ty.vn
- **Database Issues**: dba@7ty.vn

### Documentation Updates
This documentation should be updated whenever:
- New features are added
- API endpoints change
- Database schema modifications
- Configuration changes
- Business logic updates

---

*Last Updated: December 2024*
*Version: 2.0*
*Author: 7ty.vn Development Team*