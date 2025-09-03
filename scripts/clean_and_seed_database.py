#!/usr/bin/env python3
"""
Clean Database & Seed with Consistent Test Data
Purpose: Làm sạch database và tạo test data đồng bộ cho frontend testing
"""

import asyncio
import sys
import uuid
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
import random

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/test_database')

class DatabaseCleaner:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client.get_default_database()
        
    async def clean_all_collections(self):
        """Clean all collections completely"""
        print("🧹 CLEANING ALL COLLECTIONS...")
        
        collections_to_clean = [
            'customers',
            'credit_cards', 
            'credit_card_transactions',
            'bills',
            'sales',
            'inventory_items',
            'activities',
            'webhook_configs',
            'webhook_logs'
        ]
        
        cleaned_count = {}
        
        for collection_name in collections_to_clean:
            try:
                collection = getattr(self.db, collection_name)
                
                # Count existing documents
                existing_count = await collection.count_documents({})
                
                # Delete all documents
                result = await collection.delete_many({})
                
                cleaned_count[collection_name] = {
                    'existing': existing_count,
                    'deleted': result.deleted_count
                }
                
                print(f"   ✅ {collection_name}: Deleted {result.deleted_count}/{existing_count} documents")
                
            except Exception as e:
                print(f"   ❌ {collection_name}: Error - {e}")
                cleaned_count[collection_name] = {'error': str(e)}
        
        return cleaned_count

    async def create_test_users(self):
        """Create admin user for testing"""
        print("👤 CREATING TEST ADMIN USER...")
        
        # Create admin user
        admin_user = {
            "id": str(uuid.uuid4()),
            "username": "admin_test",
            "email": "admin@crm7ty.com",
            "password_hash": "$2b$12$LQv3c1yqBwEHxPuNY0TLuOrhSHDzxXcjHc6/LHGKX5Jy6JYjqB3Eq",  # admin123
            "role": "ADMIN",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc)
        }
        
        await self.db.users.insert_one(admin_user)
        print(f"   ✅ Created admin user: admin_test/admin123")
        
        return admin_user

    async def create_test_customers(self, count=20):
        """Create consistent test customers"""
        print(f"👥 CREATING {count} TEST CUSTOMERS...")
        
        customer_types = ["INDIVIDUAL", "AGENT", "BUSINESS"]
        tiers = ["BRONZE", "SILVER", "GOLD", "PLATINUM"]
        
        customers = []
        
        for i in range(count):
            customer_id = str(uuid.uuid4())
            
            customer = {
                "id": customer_id,
                "name": f"Khách Hàng Test {i+1:02d}",
                "phone": f"090{1000000 + i:07d}",
                "email": f"customer{i+1:02d}@test.com",
                "address": f"Địa chỉ số {i+1}, Phường Test, Quận Test, TP.HCM",
                "type": random.choice(customer_types),
                "tier": random.choice(tiers),
                "notes": f"Khách hàng test được tạo tự động - #{i+1}",
                "is_active": True,
                "total_transactions": 0,
                "total_spent": 0.0,
                "total_profit_generated": 0.0,
                "total_cards": 0,
                "created_at": datetime.now(timezone.utc) - timedelta(days=random.randint(1, 90)),
                "updated_at": datetime.now(timezone.utc)
            }
            
            customers.append(customer)
        
        # Insert all customers
        result = await self.db.customers.insert_many(customers)
        print(f"   ✅ Created {len(result.inserted_ids)} customers")
        
        return customers

    async def create_test_bills(self, count=50):
        """Create consistent test bills"""
        print(f"💵 CREATING {count} TEST BILLS...")
        
        denominations = [500000, 200000, 100000, 50000, 20000, 10000]
        statuses = ["AVAILABLE", "SOLD", "RESERVED"]
        conditions = ["NEW", "GOOD", "FAIR"]
        
        bills = []
        
        for i in range(count):
            bill_id = str(uuid.uuid4())
            denomination = random.choice(denominations)
            
            bill = {
                "id": bill_id,
                "bill_code": f"BILL{i+1:04d}",
                "denomination": denomination,
                "serial_number": f"VN{random.randint(10000000, 99999999)}",
                "status": random.choice(statuses),
                "condition": random.choice(conditions),
                "purchase_price": denomination * 0.98,  # 2% below face value
                "selling_price": denomination * 1.02,   # 2% above face value
                "notes": f"Bill test #{i+1} - {denomination:,} VND",
                "created_at": datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)),
                "updated_at": datetime.now(timezone.utc)
            }
            
            bills.append(bill)
        
        # Insert all bills
        result = await self.db.bills.insert_many(bills)
        print(f"   ✅ Created {len(result.inserted_ids)} bills")
        
        return bills

    async def create_test_credit_cards(self, customers, cards_per_customer=2):
        """Create consistent test credit cards with proper schema"""
        total_cards = len(customers) * cards_per_customer
        print(f"💳 CREATING {total_cards} TEST CREDIT CARDS...")
        
        banks = ["Vietcombank", "Techcombank", "BIDV", "VietinBank", "Sacombank", "ACB", "MB Bank"]
        card_types = ["VISA", "MASTERCARD", "JCB", "AMEX"]  # Valid CardType enum values
        card_statuses = ["Đã đáo", "Cần đáo", "Chưa đến hạn", "Quá Hạn"]  # Valid CardStatus enum values
        
        cards = []
        
        for customer in customers:
            for j in range(cards_per_customer):
                card_id = str(uuid.uuid4())
                bank = random.choice(banks)
                card_type = random.choice(card_types)
                card_status = random.choice(card_statuses)
                
                # Generate realistic card number based on card type
                if card_type == "VISA":
                    card_number = f"4{random.randint(100, 999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"
                elif card_type == "MASTERCARD":
                    card_number = f"5{random.randint(100, 999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"
                elif card_type == "JCB":
                    card_number = f"35{random.randint(10, 99)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}{random.randint(1000, 9999)}"
                else:  # AMEX
                    card_number = f"34{random.randint(10, 99)}{random.randint(100000, 999999)}{random.randint(10000, 99999)}"
                
                # Generate expiry date (MM/YY format)
                current_year = datetime.now().year
                expiry_month = random.randint(1, 12)
                expiry_year = random.randint(current_year, current_year + 5)
                expiry_date = f"{expiry_month:02d}/{str(expiry_year)[-2:]}"
                
                # Generate CCV
                ccv = f"{random.randint(100, 999)}" if card_type != "AMEX" else f"{random.randint(1000, 9999)}"
                
                # Generate statement and payment due dates
                statement_date = random.randint(1, 28)  # Day of month
                payment_due_date = (statement_date + 15) % 28 + 1  # 15 days after statement
                
                card = {
                    "id": card_id,
                    "customer_id": customer["id"],
                    "customer_name": customer["name"],  # Required field
                    "card_number": card_number,
                    "cardholder_name": customer["name"].upper(),  # Required field
                    "bank_name": bank,
                    "card_type": card_type,  # Valid CardType enum
                    "expiry_date": expiry_date,  # Required field in MM/YY format
                    "ccv": ccv,  # Required field
                    "statement_date": statement_date,  # Required field
                    "payment_due_date": payment_due_date,  # Required field
                    "credit_limit": random.choice([10000000, 20000000, 50000000, 100000000]),  # Required field
                    "status": card_status,  # Valid CardStatus enum
                    "notes": f"Thẻ {card_type} {bank} của {customer['name']}",
                    # Cycle tracking fields
                    "current_cycle_month": f"{datetime.now().month:02d}/{datetime.now().year}",
                    "last_payment_date": None,
                    "cycle_payment_count": 0,
                    "total_cycles": 0,
                    "created_at": datetime.now(timezone.utc) - timedelta(days=random.randint(1, 60)),
                    "updated_at": datetime.now(timezone.utc)
                }
                
                cards.append(card)
        
        # Insert all cards
        result = await self.db.credit_cards.insert_many(cards)
        print(f"   ✅ Created {len(result.inserted_ids)} credit cards with proper schema")
        
        # Update customer total_cards count
        for customer in customers:
            await self.db.customers.update_one(
                {"id": customer["id"]},
                {"$set": {"total_cards": cards_per_customer}}
            )
        
        return cards

    async def create_test_sales(self, customers, bills, count=100):
        """Create consistent test sales transactions"""
        print(f"💰 CREATING {count} TEST SALES TRANSACTIONS...")
        
        transaction_types = ["BILL_SALE"]
        payment_methods = ["CASH", "BANK_TRANSFER", "POS"]
        
        sales = []
        used_bills = set()
        
        for i in range(count):
            sale_id = str(uuid.uuid4())
            customer = random.choice(customers)
            
            # Find available bill
            available_bills = [b for b in bills if b["id"] not in used_bills and b["status"] == "AVAILABLE"]
            if not available_bills:
                break
                
            bill = random.choice(available_bills)
            used_bills.add(bill["id"])
            
            # Calculate realistic profit
            purchase_price = bill.get("purchase_price", bill["denomination"] * 0.98)
            selling_price = bill.get("selling_price", bill["denomination"] * 1.02)
            total = selling_price
            profit_value = selling_price - purchase_price
            profit_percentage = (profit_value / purchase_price) * 100 if purchase_price > 0 else 0
            
            sale = {
                "id": sale_id,
                "customer_id": customer["id"],
                "bill_id": bill["id"],
                "transaction_type": random.choice(transaction_types),
                "total": total,
                "profit_value": profit_value,
                "profit_percentage": profit_percentage,
                "payment_method": random.choice(payment_methods),
                "notes": f"Bán {bill['bill_code']} - {bill['denomination']:,} VND cho {customer['name']}",
                "status": "COMPLETED",
                "created_at": datetime.now(timezone.utc) - timedelta(days=random.randint(1, 45)),
                "updated_at": datetime.now(timezone.utc)
            }
            
            sales.append(sale)
        
        # Insert all sales
        result = await self.db.sales.insert_many(sales)
        print(f"   ✅ Created {len(result.inserted_ids)} sales transactions")
        
        # Update bill statuses to SOLD
        for sale in sales:
            await self.db.bills.update_one(
                {"id": sale["bill_id"]},
                {"$set": {"status": "SOLD", "updated_at": datetime.now(timezone.utc)}}
            )
        
        # Update customer statistics
        for customer in customers:
            customer_sales = [s for s in sales if s["customer_id"] == customer["id"]]
            if customer_sales:
                total_spent = sum(s["total"] for s in customer_sales)
                total_profit = sum(s["profit_value"] for s in customer_sales)
                
                await self.db.customers.update_one(
                    {"id": customer["id"]},
                    {"$set": {
                        "total_transactions": len(customer_sales),
                        "total_spent": total_spent,
                        "total_profit_generated": total_profit,
                        "updated_at": datetime.now(timezone.utc)
                    }}
                )
        
        return sales

    async def create_test_credit_card_transactions(self, cards, count=80):
        """Create consistent test credit card transactions"""
        print(f"💳 CREATING {count} TEST CREDIT CARD TRANSACTIONS...")
        
        transaction_types = ["CREDIT_DAO_POS", "CREDIT_DAO_BILL"]
        payment_methods = ["POS", "BILL"]
        
        transactions = []
        
        for i in range(count):
            transaction_id = str(uuid.uuid4())
            card = random.choice(cards)
            transaction_type = random.choice(transaction_types)
            payment_method = random.choice(payment_methods)
            
            # Calculate realistic amounts
            amount = random.randint(1000000, 10000000)  # 1M - 10M VND
            fee_percentage = random.uniform(2.5, 4.5)  # 2.5% - 4.5% fee
            fee = amount * (fee_percentage / 100)
            profit_amount = fee
            profit_pct = fee_percentage
            
            transaction = {
                "id": transaction_id,
                "card_id": card["id"],
                "customer_id": card["customer_id"],
                "transaction_type": transaction_type,
                "amount": amount,
                "fee": fee,
                "profit_amount": profit_amount,
                "profit_pct": profit_pct,
                "payment_method": payment_method,
                "notes": f"Đáo thẻ {payment_method} - {card['bank_name']} ****{card['card_number'][-4:]}",
                "status": "COMPLETED",
                "created_at": datetime.now(timezone.utc) - timedelta(days=random.randint(1, 30)),
                "updated_at": datetime.now(timezone.utc)
            }
            
            transactions.append(transaction)
        
        # Insert all transactions
        result = await self.db.credit_card_transactions.insert_many(transactions)
        print(f"   ✅ Created {len(result.inserted_ids)} credit card transactions")
        
        return transactions

    async def create_database_indexes(self):
        """Create database indexes for performance"""
        print("📚 CREATING DATABASE INDEXES...")
        
        try:
            # Unique indexes on ID fields  
            await self.db.customers.create_index("id", unique=True)
            await self.db.credit_cards.create_index("id", unique=True)
            await self.db.bills.create_index("id", unique=True)
            await self.db.sales.create_index("id", unique=True)
            await self.db.credit_card_transactions.create_index("id", unique=True)
            await self.db.users.create_index("id", unique=True)
            
            # Relationship indexes
            await self.db.credit_cards.create_index("customer_id")
            await self.db.sales.create_index("customer_id")
            await self.db.sales.create_index("bill_id")
            await self.db.credit_card_transactions.create_index("card_id")
            await self.db.credit_card_transactions.create_index("customer_id")
            
            # Performance indexes
            await self.db.customers.create_index("phone")
            await self.db.customers.create_index("email")
            await self.db.bills.create_index("bill_code")
            await self.db.bills.create_index("status")
            await self.db.sales.create_index("created_at")
            await self.db.credit_card_transactions.create_index("created_at")
            
            print("   ✅ All database indexes created successfully")
            
        except Exception as e:
            print(f"   ⚠️ Index creation warning: {e}")

    async def validate_data_consistency(self):
        """Validate all data relationships and consistency"""
        print("✅ VALIDATING DATA CONSISTENCY...")
        
        issues = []
        
        # Get all entities
        customers = await self.db.customers.find({}).to_list(None)
        cards = await self.db.credit_cards.find({}).to_list(None)
        bills = await self.db.bills.find({}).to_list(None)
        sales = await self.db.sales.find({}).to_list(None)
        cc_transactions = await self.db.credit_card_transactions.find({}).to_list(None)
        
        customer_ids = {c["id"] for c in customers}
        card_ids = {c["id"] for c in cards}
        bill_ids = {b["id"] for b in bills}
        
        # Validate credit card references
        for card in cards:
            if card["customer_id"] not in customer_ids:
                issues.append(f"Credit card {card['id']} references non-existent customer {card['customer_id']}")
        
        # Validate sales references
        for sale in sales:
            if sale["customer_id"] not in customer_ids:
                issues.append(f"Sale {sale['id']} references non-existent customer {sale['customer_id']}")
            if sale.get("bill_id") and sale["bill_id"] not in bill_ids:
                issues.append(f"Sale {sale['id']} references non-existent bill {sale['bill_id']}")
        
        # Validate credit card transaction references
        for transaction in cc_transactions:
            if transaction["card_id"] not in card_ids:
                issues.append(f"CC transaction {transaction['id']} references non-existent card {transaction['card_id']}")
            if transaction["customer_id"] not in customer_ids:
                issues.append(f"CC transaction {transaction['id']} references non-existent customer {transaction['customer_id']}")
        
        if issues:
            print(f"   ❌ Found {len(issues)} consistency issues:")
            for issue in issues[:10]:  # Show first 10 issues
                print(f"      - {issue}")
            return False
        else:
            print("   ✅ All data relationships are consistent")
            return True

    async def generate_summary_report(self):
        """Generate summary of created test data"""
        print("\n📊 GENERATING SUMMARY REPORT...")
        
        # Count all entities
        counts = {}
        collections = ['users', 'customers', 'credit_cards', 'bills', 'sales', 'credit_card_transactions']
        
        for collection_name in collections:
            count = await getattr(self.db, collection_name).count_documents({})
            counts[collection_name] = count
        
        # Calculate totals
        total_revenue = 0
        total_profit = 0
        
        sales = await self.db.sales.find({}).to_list(None)
        for sale in sales:
            total_revenue += sale.get("total", 0)
            total_profit += sale.get("profit_value", 0)
        
        cc_transactions = await self.db.credit_card_transactions.find({}).to_list(None)
        for transaction in cc_transactions:
            total_profit += transaction.get("profit_amount", 0)
        
        print("=" * 60)
        print("📈 TEST DATABASE SUMMARY REPORT")
        print("=" * 60)
        print(f"👤 Users: {counts['users']}")
        print(f"👥 Customers: {counts['customers']}")
        print(f"💳 Credit Cards: {counts['credit_cards']}")
        print(f"💵 Bills: {counts['bills']}")
        print(f"💰 Sales: {counts['sales']}")
        print(f"🔄 Credit Card Transactions: {counts['credit_card_transactions']}")
        print(f"💲 Total Revenue: {total_revenue:,.0f} VND")
        print(f"📈 Total Profit: {total_profit:,.0f} VND")
        print("=" * 60)
        
        return counts

    async def run_full_cleanup_and_seed(self):
        """Run complete database cleanup and seeding"""
        print("🚀 STARTING FULL DATABASE CLEANUP & SEED")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Clean all collections
            await self.clean_all_collections()
            
            # Step 2: Create test admin user
            await self.create_test_users()
            
            # Step 3: Create test customers
            customers = await self.create_test_customers(20)
            
            # Step 4: Create test bills
            bills = await self.create_test_bills(50)
            
            # Step 5: Create test credit cards
            cards = await self.create_test_credit_cards(customers, 2)
            
            # Step 6: Create test sales
            sales = await self.create_test_sales(customers, bills, 100)
            
            # Step 7: Create test credit card transactions
            cc_transactions = await self.create_test_credit_card_transactions(cards, 80)
            
            # Step 8: Create database indexes
            await self.create_database_indexes()
            
            # Step 9: Validate data consistency
            is_consistent = await self.validate_data_consistency()
            
            # Step 10: Generate summary report
            counts = await self.generate_summary_report()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print(f"\n🎉 DATABASE CLEANUP & SEED COMPLETED!")
            print(f"   Duration: {duration:.2f} seconds")
            print(f"   Data Consistency: {'✅ PASSED' if is_consistent else '❌ ISSUES FOUND'}")
            print(f"\n🔑 TEST LOGIN CREDENTIALS:")
            print(f"   Username: admin_test")
            print(f"   Password: admin123")
            print(f"\n🎯 READY FOR FRONTEND TESTING!")
            
            return True
            
        except Exception as e:
            print(f"❌ CLEANUP & SEED FAILED: {e}")
            return False
        finally:
            if self.client:
                self.client.close()

async def main():
    """Main function"""
    print("⚠️ WARNING: This will DELETE ALL existing data and create new test data")
    print("   Make sure you have a backup if needed!")
    
    if len(sys.argv) > 1 and sys.argv[1] == '--force':
        print("🚀 Force mode - proceeding without confirmation")
    else:
        confirm = input("Continue with database cleanup and seeding? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Operation cancelled")
            return
    
    cleaner = DatabaseCleaner()
    success = await cleaner.run_full_cleanup_and_seed()
    
    if success:
        print("\n✅ Database is ready for frontend testing!")
        sys.exit(0) 
    else:
        print("\n❌ Database cleanup and seeding failed")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())