#!/usr/bin/env python3
import asyncio
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient
from passlib.context import CryptContext
from dotenv import load_dotenv

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

# Setup password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_admin_user():
    """Create admin user for 7ty.vn CRM"""
    try:
        # Connect to MongoDB
        mongo_url = os.environ['MONGO_URL']
        client = AsyncIOMotorClient(mongo_url)
        db = client[os.environ['DB_NAME']]
        
        print("🔗 Connected to MongoDB...")
        
        # Check if admin already exists
        existing_admin = await db.users.find_one({"role": "admin"})
        if existing_admin:
            print(f"✅ Admin user already exists: {existing_admin['username']}")
            return
        
        # Create admin user
        admin_data = {
            "id": str(uuid.uuid4()),
            "username": "admin",
            "email": "admin@7ty.vn", 
            "phone": "0901234567",
            "password": pwd_context.hash("admin123"),  # Default password
            "full_name": "Quản trị viên hệ thống",
            "role": "admin",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "last_login": None
        }
        
        # Insert admin user
        await db.users.insert_one(admin_data)
        print("✅ Admin user created successfully!")
        print(f"   Username: admin")
        print(f"   Email: admin@7ty.vn")
        print(f"   Phone: 0901234567")
        print(f"   Password: admin123")
        print(f"   Role: admin")
        
        # Create a manager user for testing
        manager_data = {
            "id": str(uuid.uuid4()),
            "username": "manager",
            "email": "manager@7ty.vn",
            "phone": "0907654321", 
            "password": pwd_context.hash("manager123"),
            "full_name": "Quản lý hệ thống",
            "role": "manager",
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "last_login": None
        }
        
        await db.users.insert_one(manager_data)
        print("✅ Manager user created successfully!")
        print(f"   Username: manager")
        print(f"   Email: manager@7ty.vn") 
        print(f"   Phone: 0907654321")
        print(f"   Password: manager123")
        print(f"   Role: manager")
        
        # Create a regular user for testing
        user_data = {
            "id": str(uuid.uuid4()),
            "username": "user",
            "email": "user@7ty.vn",
            "phone": "0909876543",
            "password": pwd_context.hash("user123"),
            "full_name": "Người dùng thường",
            "role": "user", 
            "is_active": True,
            "created_at": datetime.now(timezone.utc),
            "last_login": None
        }
        
        await db.users.insert_one(user_data)
        print("✅ Regular user created successfully!")
        print(f"   Username: user")
        print(f"   Email: user@7ty.vn")
        print(f"   Phone: 0909876543") 
        print(f"   Password: user123")
        print(f"   Role: user")
        
        print("\n🎉 All test users created! You can now login with:")
        print("   • admin/admin123 (Quản trị viên)")
        print("   • manager/manager123 (Quản lý)")  
        print("   • user/user123 (Người dùng)")
        
        await client.close()
        
    except Exception as e:
        print(f"❌ Error creating admin user: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(create_admin_user())