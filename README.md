# FPT Bill Manager - Mini CRM & Electric Bill Checker

Ứng dụng quản lý hóa đơn điện và CRM mini với tích hợp cổng FPT để kiểm tra bill điện tự động.

## 🎯 **Tổng Quan Dự Án**

FPT Bill Manager là một hệ thống full-stack giúp:
- ✅ **Kiểm tra mã điện** qua external API (FPT Gateway)
- ✅ **Quản lý kho bill** với batch tracking
- ✅ **Quản lý khách hàng** (CRM) với tracking giao dịch
- ✅ **Bán bill** với tính toán lợi nhuận tự động
- ✅ **Dashboard** thống kê tổng quan

## 🏗️ **Tech Stack**

### **Frontend:**
- React 19 + React Router v7
- Tailwind CSS + shadcn/ui components
- Axios cho API calls
- Sonner cho toast notifications
- Lucide React cho icons

### **Backend:**
- FastAPI + Python 3.11
- MongoDB + Motor (async driver)
- Pydantic cho data validation
- aiohttp cho external API calls
- JWT authentication (placeholder)

### **Database:**
- MongoDB với collections:
  - `customers` - Thông tin khách hàng
  - `bills` - Hóa đơn điện
  - `inventory_items` - Bills trong kho
  - `sales` - Giao dịch bán bill
  - `webhook_logs` - Log webhook calls

## 📊 **Database Schema**

### **Collections Structure:**

```javascript
// customers
{
  "id": "uuid",
  "type": "INDIVIDUAL" | "AGENT",
  "name": "string",
  "phone": "string?",
  "email": "string?",
  "address": "string?",
  "is_active": boolean,
  "total_transactions": number,
  "total_value": number,
  "total_bills": number,
  "total_cards": number,
  "total_profit_generated": number,
  "notes": "string?",
  "created_at": "datetime",
  "updated_at": "datetime"
}

// bills
{
  "id": "uuid",
  "gateway": "FPT" | "SHOPEE",
  "customer_code": "string", // Mã điện
  "provider_region": "MIEN_BAC" | "MIEN_NAM" | "HCMC",
  "provider_name": "string?",
  "full_name": "string?", // Tên khách hàng trên bill
  "address": "string?",
  "amount": number,
  "billing_cycle": "string", // MM/YYYY
  "status": "AVAILABLE" | "PENDING" | "SOLD" | "ERROR",
  "error_code": "string?",
  "error_message": "string?",
  "meta": object,
  "created_at": "datetime",
  "updated_at": "datetime"
}

// inventory_items
{
  "id": "uuid",
  "bill_id": "string", // Reference to bills.id
  "note": "string?",
  "batch_id": "string?", // Group bills added together
  "added_by": "string",
  "created_at": "datetime"
}

// sales
{
  "id": "uuid",
  "customer_id": "string", // Reference to customers.id
  "transaction_type": "ELECTRIC_BILL" | "CREDIT_CARD",
  "total": number, // Tổng giá trị bills
  "profit_pct": number, // % lợi nhuận
  "profit_value": number, // Tiền lợi nhuận
  "payback": number, // Tiền trả khách
  "method": "CASH" | "BANK_TRANSFER" | "OTHER",
  "status": "COMPLETED" | "CANCELLED",
  "notes": "string?",
  "bill_ids": ["string"], // List of bill IDs
  "created_at": "datetime"
}
```

## 🚀 **API Endpoints**

### **Dashboard APIs:**
```
GET /api/dashboard/stats - Thống kê tổng quan
```

### **Bill Checking APIs:**
```
POST /api/bill/check - Check multiple bills (bulk)
POST /api/bill/check/single - Check single bill (realtime)
GET /api/bills - List bills with filters
```

### **Inventory APIs:**
```
GET /api/inventory/stats - Thống kê kho
GET /api/inventory - List inventory items
POST /api/inventory/add - Add bills to inventory
DELETE /api/inventory/{id} - Remove from inventory
```

### **Customer APIs:**
```
GET /api/customers/stats - Customer statistics
GET /api/customers - List customers with filters
GET /api/customers/{id} - Get single customer
POST /api/customers - Create customer
PUT /api/customers/{id} - Update customer
DELETE /api/customers/{id} - Delete customer
GET /api/customers/{id}/transactions - Customer transaction history
```

### **Webhook API:**
```
POST /api/webhook/checkbill - Receive webhook from external systems
```

## 🎨 **Frontend Pages**

### **1. Dashboard (/):**
- 📊 **Stats Cards**: Tổng bills, available, customers, revenue
- 🎯 **Quick Actions**: Tra cứu, thêm kho, quản lý KH, bán bill
- 📈 **Recent Activities**: Hoạt động gần đây

### **2. Kiểm Tra Mã Điện (/check-bill):**
- 🔍 **Bulk Input**: Textarea nhập nhiều mã cùng lúc
- ⚡ **Realtime Processing**: Hiển thị kết quả từng bill ngay lập tức
- 📊 **Progress Animation**: Progress bar với step-by-step status
- ✅ **Check All**: Checkbox chọn tất cả bills hợp lệ
- 🏪 **Add to Inventory**: Nút thêm vào kho khi có selection

### **3. Kho Bill (/inventory):**
- 📊 **Stats Cards**: Tổng bill, có sẵn, chờ thanh toán, tổng giá trị
- 📋 **Inventory Table**: Danh sách bills với đầy đủ thông tin
- 🔍 **Filters & Search**: Lọc theo status, tìm kiếm
- 📂 **Tabs**: "Bills Có Sẵn" vs "Tất Cả Bills"

### **4. Quản Lý Khách Hàng (/customers):**
- 📊 **Stats Cards**: Tổng KH, cá nhân, đại lý, hoạt động, tổng giá trị
- 👥 **Customer Table**: Danh sách với filters & search
- ➕ **Add/Edit Modal**: Form tạo/sửa khách hàng
- 👁️ **Detail Modal**: Chi tiết KH + lịch sử giao dịch

### **5. Bán Bill (/sales): [ĐANG PHÁT TRIỂN]**
- 💰 Modal bán bill với customer selection
- 📊 Real-time profit calculation
- 💳 Payment method selection

## 🔧 **Setup & Installation**

### **Prerequisites:**
```bash
- Python 3.11+
- Node.js 18+
- MongoDB 4.4+
- yarn (không dùng npm)
```

### **Backend Setup:**
```bash
cd /app/backend
pip install -r requirements.txt

# Environment variables
cp .env.example .env
# Edit .env với MongoDB URL và các config cần thiết

# Start backend
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### **Frontend Setup:**
```bash
cd /app/frontend  
yarn install

# Environment variables
cp .env.example .env
# Edit .env với REACT_APP_BACKEND_URL

# Start frontend
yarn start
```

### **Database Setup:**
- MongoDB sẽ tự động tạo collections khi start app
- Sample data được seed tự động trong `@app.on_event("startup")`

## 🎯 **Key Features Completed**

### ✅ **External API Integration:**
- **N8N Webhook**: https://n8n.phamthanh.net/webhook/checkbill
- **Mock Success**: PA2204000000 → Nguyễn Thị Hương, 1,850,000₫
- **Error Handling**: Parse Vietnamese error messages
- **Timeout Management**: 30s với proper fallback

### ✅ **Realtime Bill Checking:**
- Process bills one-by-one với live updates
- Progress animation với step tracking
- Real-time counter: "X thành công • Y lỗi"
- Individual bill status updates

### ✅ **Inventory Management:**
- Add bills with batch tracking
- Stats calculation với aggregation
- Filter & search functionality
- Remove items với validation

### ✅ **Customer Management:**
- Full CRUD operations
- Stats tracking (transactions, value, profit)
- Data migration (BUSINESS → AGENT)
- Transaction history display

### ✅ **Database Operations:**
- MongoDB với proper schema validation
- UUID primary keys (không dùng ObjectId)
- Datetime handling với timezone awareness
- Data seeding với sample records

## 🎨 **UI/UX Highlights**

### **Design Principles:**
- ✅ **Modern Color Palette**: Professional blues, greens, purples
- ✅ **Typography**: Inter font family cho readability
- ✅ **Cards Design**: Subtle shadows với hover effects  
- ✅ **Animations**: Smooth transitions, loading states
- ✅ **Icons**: Lucide React cho consistency
- ✅ **Responsive**: Mobile-first approach

### **Components Used:**
- **shadcn/ui**: Card, Button, Input, Table, Badge, Dialog
- **Toast Notifications**: Sonner library
- **Loading States**: Skeleton placeholders
- **Empty States**: Helpful messaging với call-to-action

## 🧪 **Testing**

### **API Testing:**
```bash
# Test customer creation
curl -X POST "http://localhost:8001/api/customers" \
  -H "Content-Type: application/json" \
  -d '{"name": "Test User", "type": "INDIVIDUAL"}'

# Test bill checking
curl -X POST "http://localhost:8001/api/bill/check/single" \
  "?customer_code=PA2204000000&provider_region=MIEN_NAM"
```

### **Frontend Testing:**
- Manual testing của all user workflows
- Realtime updates verification
- Error handling validation
- Responsive design testing

## 📈 **Business Logic**

### **Profit Calculation:**
```
Example: Bill 1,500,000 VND, profit 10%
- Lợi nhuận = 1,500,000 * 10% = 150,000 VND  
- Trả khách = 1,500,000 - 150,000 = 1,350,000 VND
```

### **Bill Status Flow:**
```
AVAILABLE → (Add to Inventory) → AVAILABLE
AVAILABLE → (Sell) → SOLD
ERROR → (Cannot process)
```

### **Customer Stats Tracking:**
- `total_transactions`: Số giao dịch
- `total_value`: Tổng giá trị bills đã mua
- `total_profit_generated`: Tổng lợi nhuận đã tạo
- `total_bills`: Số lượng bills điện
- `total_cards`: Số lượng thẻ tín dụng (future)

## 🔮 **Roadmap**

### **Phase 2 - Sell Bill:**
- [ ] Sell modal với customer selection
- [ ] Real-time profit calculation
- [ ] Transaction recording
- [ ] Customer stats auto-update

### **Phase 3 - Credit Card:**
- [ ] Credit card database structure
- [ ] Add thẻ form với đầy đủ fields
- [ ] Đáo hạn thẻ workflow
- [ ] Separate transaction types

### **Phase 4 - Advanced:**
- [ ] User authentication & authorization
- [ ] Export functionality (Excel)
- [ ] Advanced reporting & analytics
- [ ] Webhook signature verification
- [ ] Rate limiting & security

## 🚨 **Known Issues & Solutions**

### **Issue**: Select component validation errors
**Solution**: Replaced shadcn Select with HTML select temporarily

### **Issue**: Database type migration (BUSINESS → AGENT)  
**Solution**: Auto-migration trong API endpoint với graceful handling

### **Issue**: External API rate limiting
**Solution**: Proper timeout handling với fallback messaging

## 🎯 **Quick Start**

### **Prerequisites**
- Python 3.11+
- Node.js 18+
- MongoDB
- yarn

### **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8001
```

### **Frontend Setup**
```bash
cd frontend
yarn install
yarn start
```

The frontend will be available at http://localhost:3000 and backend at http://localhost:8001.

## 🤝 **Contributing**

1. Follow existing code structure
2. Use TypeScript/Python type hints
3. Add proper error handling
4. Test thoroughly before commit
5. Update documentation

## 📞 **Support**

- **External API**: https://n8n.phamthanh.net/webhook/checkbill
- **Mock Success Code**: PA2204000000
- **Database**: MongoDB collections tự động tạo
- **Logs**: `/var/log/supervisor/backend.*.log`

---

**© 2025 FPT Bill Manager - Built with ❤️ using FastAPI + React + MongoDB**
