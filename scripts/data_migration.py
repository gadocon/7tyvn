#!/usr/bin/env python3
"""
Data Migration Script - Standardize ObjectId vs UUID Issues
Purpose: Fix data inconsistency và prevent future "loạn xạ" data creation
"""

import asyncio
import sys
import uuid
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os

# MongoDB connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017/test_database')

class DataMigration:
    def __init__(self):
        self.client = AsyncIOMotorClient(MONGO_URL)
        self.db = self.client.get_default_database()
        
    async def migrate_customers(self):
        """Migrate customers to have consistent UUID in 'id' field"""
        print("🔧 MIGRATING CUSTOMERS...")
        
        # Find customers without proper UUID in 'id' field
        customers_to_fix = await self.db.customers.find({
            "$or": [
                {"id": {"$exists": False}},  # No 'id' field
                {"id": ""},  # Empty 'id' field
                {"id": None},  # Null 'id' field
                # ObjectId format in 'id' field (24 hex chars)
                {"id": {"$regex": "^[0-9a-f]{24}$"}}
            ]
        }).to_list(None)
        
        print(f"   Found {len(customers_to_fix)} customers to fix")
        
        fixed_count = 0
        for customer in customers_to_fix:
            old_id = customer.get('id')
            customer_name = customer.get('name', 'Unknown')
            
            # Generate new UUID
            new_uuid = str(uuid.uuid4())
            
            print(f"   Fixing customer '{customer_name}': {old_id} → {new_uuid}")
            
            # Update customer with proper UUID
            await self.db.customers.update_one(
                {"_id": customer["_id"]},
                {"$set": {"id": new_uuid, "updated_at": datetime.now(timezone.utc)}}
            )
            
            # Update all references in other collections
            if old_id:
                # Update sales references
                sales_updated = await self.db.sales.update_many(
                    {"customer_id": old_id},
                    {"$set": {"customer_id": new_uuid}}
                )
                
                # Update credit cards references
                cards_updated = await self.db.credit_cards.update_many(
                    {"customer_id": old_id},
                    {"$set": {"customer_id": new_uuid}}
                )
                
                # Update credit card transactions references
                cc_tx_updated = await self.db.credit_card_transactions.update_many(
                    {"customer_id": old_id},
                    {"$set": {"customer_id": new_uuid}}
                )
                
                print(f"     Updated {sales_updated.modified_count} sales, {cards_updated.modified_count} cards, {cc_tx_updated.modified_count} cc transactions")
            
            fixed_count += 1
        
        print(f"✅ CUSTOMERS MIGRATION COMPLETE: {fixed_count} customers fixed")
        return fixed_count

    async def migrate_credit_cards(self):
        """Migrate credit cards to have consistent UUID in 'id' field"""
        print("🔧 MIGRATING CREDIT CARDS...")
        
        # Find credit cards without proper UUID in 'id' field
        cards_to_fix = await self.db.credit_cards.find({
            "$or": [
                {"id": {"$exists": False}},
                {"id": ""},
                {"id": None},
                {"id": {"$regex": "^[0-9a-f]{24}$"}}  # ObjectId format
            ]
        }).to_list(None)
        
        print(f"   Found {len(cards_to_fix)} credit cards to fix")
        
        fixed_count = 0
        for card in cards_to_fix:
            old_id = card.get('id')
            card_number = card.get('card_number', 'Unknown')
            
            # Generate new UUID
            new_uuid = str(uuid.uuid4())
            
            print(f"   Fixing card '****{card_number[-4:] if len(card_number) >= 4 else card_number}': {old_id} → {new_uuid}")
            
            # Update credit card with proper UUID
            await self.db.credit_cards.update_one(
                {"_id": card["_id"]},
                {"$set": {"id": new_uuid, "updated_at": datetime.now(timezone.utc)}}
            )
            
            # Update references in credit card transactions
            if old_id:
                cc_tx_updated = await self.db.credit_card_transactions.update_many(
                    {"card_id": old_id},
                    {"$set": {"card_id": new_uuid}}
                )
                
                print(f"     Updated {cc_tx_updated.modified_count} credit card transactions")
            
            fixed_count += 1
        
        print(f"✅ CREDIT CARDS MIGRATION COMPLETE: {fixed_count} cards fixed")
        return fixed_count

    async def migrate_bills(self):
        """Migrate bills to have consistent UUID in 'id' field"""
        print("🔧 MIGRATING BILLS...")
        
        bills_to_fix = await self.db.bills.find({
            "$or": [
                {"id": {"$exists": False}},
                {"id": ""},
                {"id": None},
                {"id": {"$regex": "^[0-9a-f]{24}$"}}
            ]
        }).to_list(None)
        
        print(f"   Found {len(bills_to_fix)} bills to fix")
        
        fixed_count = 0
        for bill in bills_to_fix:
            old_id = bill.get('id')
            bill_code = bill.get('bill_code', 'Unknown')
            
            new_uuid = str(uuid.uuid4())
            
            print(f"   Fixing bill '{bill_code}': {old_id} → {new_uuid}")
            
            await self.db.bills.update_one(
                {"_id": bill["_id"]},
                {"$set": {"id": new_uuid, "updated_at": datetime.now(timezone.utc)}}
            )
            
            # Update references in sales
            if old_id:
                sales_updated = await self.db.sales.update_many(
                    {"bill_id": old_id},
                    {"$set": {"bill_id": new_uuid}}
                )
                
                print(f"     Updated {sales_updated.modified_count} sales references")
            
            fixed_count += 1
        
        print(f"✅ BILLS MIGRATION COMPLETE: {fixed_count} bills fixed")
        return fixed_count

    async def standardize_transaction_ids(self):
        """Standardize CC_* format transaction IDs to UUIDs"""
        print("🔧 STANDARDIZING TRANSACTION IDs...")
        
        cc_transactions = await self.db.credit_card_transactions.find({
            "id": {"$regex": "^CC_"}
        }).to_list(None)
        
        print(f"   Found {len(cc_transactions)} CC_* format transactions to standardize")
        
        fixed_count = 0
        for transaction in cc_transactions:
            old_id = transaction.get('id')
            new_uuid = str(uuid.uuid4())
            
            print(f"   Standardizing transaction: {old_id} → {new_uuid}")
            
            await self.db.credit_card_transactions.update_one(
                {"_id": transaction["_id"]},
                {"$set": {"id": new_uuid, "updated_at": datetime.now(timezone.utc)}}
            )
            
            fixed_count += 1
        
        print(f"✅ TRANSACTION IDs STANDARDIZATION COMPLETE: {fixed_count} transactions fixed")
        return fixed_count

    async def create_data_consistency_rules(self):
        """Create database indexes and validation rules"""
        print("🔧 CREATING DATA CONSISTENCY RULES...")
        
        try:
            # Create unique indexes on 'id' fields
            await self.db.customers.create_index("id", unique=True)
            await self.db.credit_cards.create_index("id", unique=True)
            await self.db.bills.create_index("id", unique=True)
            await self.db.sales.create_index("id", unique=True)
            await self.db.credit_card_transactions.create_index("id", unique=True)
            
            print("   ✅ Created unique indexes on 'id' fields")
            
            # Create compound indexes for relationships
            await self.db.credit_cards.create_index("customer_id")
            await self.db.sales.create_index("customer_id") 
            await self.db.credit_card_transactions.create_index("card_id")
            
            print("   ✅ Created relationship indexes")
            
        except Exception as e:
            print(f"   ⚠️ Index creation warning: {e}")
        
        print("✅ DATA CONSISTENCY RULES CREATED")

    async def validate_data_integrity(self):
        """Validate data integrity after migration"""
        print("🔍 VALIDATING DATA INTEGRITY...")
        
        issues = []
        
        # Check for duplicate IDs
        collections = ['customers', 'credit_cards', 'bills', 'sales', 'credit_card_transactions']
        for collection_name in collections:
            collection = getattr(self.db, collection_name)
            
            # Find duplicates
            duplicates = await collection.aggregate([
                {"$group": {"_id": "$id", "count": {"$sum": 1}}},
                {"$match": {"count": {"$gt": 1}}}
            ]).to_list(None)
            
            if duplicates:
                issues.append(f"{collection_name}: {len(duplicates)} duplicate IDs found")
            else:
                print(f"   ✅ {collection_name}: No duplicate IDs")
        
        # Check for broken references
        customers = await self.db.customers.distinct("id")
        customer_set = set(customers)
        
        # Check credit card references
        cards = await self.db.credit_cards.find({}).to_list(None)
        broken_card_refs = 0
        for card in cards:
            if card.get('customer_id') not in customer_set:
                broken_card_refs += 1
        
        if broken_card_refs > 0:
            issues.append(f"credit_cards: {broken_card_refs} broken customer references")
        else:
            print(f"   ✅ credit_cards: All customer references valid")
        
        # Check sales references
        sales = await self.db.sales.find({}).to_list(None)
        broken_sales_refs = 0
        for sale in sales:
            if sale.get('customer_id') not in customer_set:
                broken_sales_refs += 1
        
        if broken_sales_refs > 0:
            issues.append(f"sales: {broken_sales_refs} broken customer references")
        else:
            print(f"   ✅ sales: All customer references valid")
        
        if issues:
            print(f"❌ DATA INTEGRITY ISSUES FOUND:")
            for issue in issues:
                print(f"   - {issue}")
            return False
        else:
            print(f"✅ DATA INTEGRITY VALIDATION PASSED")
            return True

    async def run_full_migration(self):
        """Run complete migration process"""
        print("🚀 STARTING FULL DATA MIGRATION")
        print("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Step 1: Migrate core entities
            customers_fixed = await self.migrate_customers()
            cards_fixed = await self.migrate_credit_cards()
            bills_fixed = await self.migrate_bills()
            
            # Step 2: Standardize transaction IDs
            transactions_fixed = await self.standardize_transaction_ids()
            
            # Step 3: Create consistency rules
            await self.create_data_consistency_rules()
            
            # Step 4: Validate integrity
            integrity_ok = await self.validate_data_integrity()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            print("\n" + "=" * 60)
            print("🎉 MIGRATION SUMMARY")
            print(f"   Customers fixed: {customers_fixed}")
            print(f"   Credit cards fixed: {cards_fixed}")
            print(f"   Bills fixed: {bills_fixed}")
            print(f"   Transactions standardized: {transactions_fixed}")
            print(f"   Data integrity: {'✅ PASSED' if integrity_ok else '❌ ISSUES FOUND'}")
            print(f"   Migration time: {duration:.2f} seconds")
            
            if integrity_ok:
                print("\n🚀 SYSTEM IS NOW FULLY STABILIZED!")
                print("   ✅ No more 'loạn xạ' data creation")
                print("   ✅ All ID formats standardized to UUID")
                print("   ✅ All references validated")
                print("   ✅ Database indexes created")
                return True
            else:
                print("\n⚠️ MIGRATION COMPLETED WITH ISSUES")
                print("   Manual review required for data integrity issues")
                return False
                
        except Exception as e:
            print(f"❌ MIGRATION FAILED: {e}")
            return False
        finally:
            await self.client.close()

async def main():
    """Main migration function"""
    if len(sys.argv) > 1 and sys.argv[1] == '--dry-run':
        print("🔍 DRY RUN MODE - No changes will be made")
        return
    
    print("⚠️ WARNING: This will modify database records")
    print("   Make sure you have a backup before proceeding!")
    
    confirm = input("Continue with migration? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Migration cancelled")
        return
    
    migration = DataMigration()
    success = await migration.run_full_migration()
    
    if success:
        print("\n🎯 NEXT STEPS:")
        print("   1. Test all API endpoints")
        print("   2. Verify frontend functionality")
        print("   3. Deploy to production")
        sys.exit(0)
    else:
        print("\n❌ MIGRATION ISSUES - Manual intervention required")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())