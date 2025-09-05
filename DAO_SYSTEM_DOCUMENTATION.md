# 📋 ĐÁO SYSTEM DOCUMENTATION

## 🎯 BUSINESS MODEL OVERVIEW

**7ty.vn CRM** phục vụ doanh nghiệp cung cấp 2 dịch vụ chính:
1. **Đáo Thẻ Tín Dụng** (rút tiền mặt từ thẻ)
2. **Bán Bill Điện** (để rút tiền từ thẻ)

---

## 🔄 TRANSACTION TYPES

### **CREDIT_DAO_POS** (Đáo Thẻ POS):
- **Mô tả**: Đáo thẻ tín dụng bằng thiết bị POS
- **Logic**: 1 giao dịch đơn giản
- **Fields**: `pos_code`, `payment_method: "POS"`
- **Display**: "Đáo Thẻ POS"
- **Process**: 
  1. Tạo DAO transaction
  2. Update credit card status
  3. Update customer stats

### **CREDIT_DAO_BILL** (Đáo Thẻ Bill):
- **Mô tả**: Đáo thẻ bằng bán bill điện
- **Logic**: Phức tạp - tạo DAO transaction + bill sale transaction
- **Fields**: `bill_code`, `payment_method: "BILL"`
- **Display**: "Đáo Thẻ Bill"
- **Process**:
  1. Tạo DAO transaction
  2. Tạo Bill sale transaction
  3. Update bills trong kho: status → "đã bán"
  4. Update credit card status
  5. Update customer stats

### **BILL_SALE** (Bán Bill):
- **Mô tả**: Bán bill điện thông thường
- **Logic**: Standard bill sale transaction
- **Display**: "Bán Bill"

---

## 🎮 FRONTEND UI FLOW

### **Credit Card Modal - DAO Function:**
```
Credit Card Detail Modal
├── [Đáo] Button Click
├── DAO Modal Opens
├── 2 Tabs:
│   ├── [Thanh Toán POS] → payment_method: "POS" → CREDIT_DAO_POS
│   └── [Thanh Toán Bill Điện] → payment_method: "BILL" → CREDIT_DAO_BILL
├── Form Fields:
│   ├── Số Tiền Đáo
│   ├── % Lợi Nhuận  
│   ├── POS Code (for POS) / Bill Selection (for BILL)
│   └── Ghi Chú
└── [Xác Nhận] → API Call
```

---

## 🔧 BACKEND API ENDPOINTS

### **1. DAO by Card ID:**
```http
POST /api/credit-cards/{card_id}/dao
{
  "amount": 1500000,
  "profit_value": 45000,  
  "payment_method": "POS",  // "POS" or "BILL"
  "pos_code": "POS001",     // for POS method
  "bill_code": "PA220...",  // for BILL method
  "notes": "..."
}
```

### **2. General DAO:**
```http
POST /api/credit-cards/dao
{
  "customer_id": "uuid...",
  "amount": 800000,
  "profit_value": 24000,
  "payment_method": "BILL",
  "bill_code": "PA220404446450825",
  "notes": "..."
}
```

---

## 📊 DATABASE SCHEMA

### **DAO Transactions Collection:**
```javascript
{
  id: "uuid...",
  customer_id: "uuid...",
  credit_card_id: "uuid...",
  amount: 1500000,
  profit_value: 45000,
  payment_method: "POS", // "POS" or "BILL"
  transaction_type: "CREDIT_DAO_POS", // or "CREDIT_DAO_BILL"
  pos_code: "POS001",
  bill_code: "PA220...",
  status: "COMPLETED",
  created_at: "2025-09-05T...",
  updated_at: "2025-09-05T..."
}
```

---

## 🎯 BUSINESS LOGIC UPDATES

### **When DAO Transaction Created:**

#### **Credit Card Updates:**
- `current_balance` += dao_amount
- `available_credit` = credit_limit - current_balance
- `status` = calculated status ("Cần đáo", "Đã đáo", etc.)
- `last_dao_date` = transaction timestamp

#### **Customer Stats Updates:**
- `total_dao_amount` += dao_amount
- `total_dao_transactions` += 1
- `total_dao_profit` += profit_value
- `total_spent` += dao_amount (for customer list display)
- `total_profit_generated` += profit_value

#### **For CREDIT_DAO_BILL Additional Logic:**
- Select bills from inventory
- Update bill status: "available" → "sold"
- Create bill sale transaction
- Link bills to DAO transaction

---

## 📈 REPORTING & ANALYTICS

### **Transaction Type Analytics:**
- **CREDIT_DAO_POS**: Phân tích dịch vụ đáo POS
- **CREDIT_DAO_BILL**: Phân tích dịch vụ đáo bill điện  
- **BILL_SALE**: Phân tích bán bill thông thường

### **Revenue Streams:**
1. **POS DAO Revenue**: profit_value từ CREDIT_DAO_POS
2. **Bill DAO Revenue**: profit_value từ CREDIT_DAO_BILL
3. **Direct Bill Sales**: profit_value từ BILL_SALE

---

## 🔍 TROUBLESHOOTING

### **Common Issues:**
1. **Transaction Type Mismatch**: Ensure payment_method maps correctly
2. **Bill Inventory**: For CREDIT_DAO_BILL, verify bill availability
3. **Customer Stats**: Verify all customer totals include DAO amounts
4. **UI Display**: Check getTransactionTypeLabel functions

### **Testing Scenarios:**
1. Test POS DAO: payment_method="POS" → CREDIT_DAO_POS
2. Test Bill DAO: payment_method="BILL" → CREDIT_DAO_BILL  
3. Verify transaction lists show correct types
4. Check customer stats include all DAO amounts

---

## 📝 TODO / FUTURE ENHANCEMENTS

### **CREDIT_DAO_BILL Implementation:**
- [ ] Bill selection UI in frontend
- [ ] Inventory update logic
- [ ] Bill status management
- [ ] Complex transaction linking

### **Status Management:**
- [ ] Auto status update based on dates
- [ ] Status notification system
- [ ] Customer care workflow integration

### **Analytics:**
- [ ] DAO vs Bill sales comparison
- [ ] Customer DAO patterns
- [ ] Revenue optimization insights

---

*Last Updated: 2025-09-05*
*Version: 1.0*