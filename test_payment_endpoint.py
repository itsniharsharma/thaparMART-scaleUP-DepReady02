#!/usr/bin/env python3
"""
Direct Payment Endpoint Test
Test the exact scenario that causes "Failed to create payment order" error
"""

import asyncio
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import requests
import json

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

async def test_payment_scenarios():
    """Test different payment creation scenarios"""
    
    print("🧪 TESTING: Different Payment Creation Scenarios")
    print("=" * 60)
    
    base_url = "http://localhost:8001/api"
    
    # Scenario 1: No authentication
    print("\n📋 SCENARIO 1: No authentication")
    try:
        response = requests.post(f"{base_url}/payment/create-order", json={})
        print(f"    Status: {response.status_code}")
        print(f"    Response: {response.json()}")
    except Exception as e:
        print(f"    Error: {e}")
    
    # Scenario 2: Create a user and session, but incomplete profile
    print("\n📋 SCENARIO 2: Authenticated user with incomplete profile")
    
    # First register user without phone
    try:
        register_data = {
            "first_name": "Test",
            "last_name": "Payment",
            "thapar_email_prefix": "testpayment",
            "is_faculty": False,
            "branch": "Computer Science",
            "roll_number": "123456789",
            "batch": "2021-2025"
        }
        
        response = requests.post(f"{base_url}/auth/register", json=register_data)
        print(f"    Registration Status: {response.status_code}")
        
        if response.status_code == 200:
            # Now try to create payment order (this should fail due to incomplete profile)
            # Note: In real app, user would be authenticated through Emergent auth
            # For testing, we'll simulate what happens with incomplete profile
            print("    ✅ User registered successfully")
            print("    ❌ Cannot test payment creation without full auth flow")
            print("    💡 Real issue: User needs to complete profile with phone number")
        
    except Exception as e:
        print(f"    Error: {e}")
    
    # Scenario 3: Check database for users without phone numbers
    print("\n📋 SCENARIO 3: Check existing users profile completeness")
    
    try:
        mongo_client = AsyncIOMotorClient(os.environ['MONGO_URL'])
        db = mongo_client[os.environ['DB_NAME']]
        
        # Find users without phone numbers
        users_without_phone = await db.users.find({
            "$or": [
                {"phone": {"$exists": False}},
                {"phone": ""},
                {"phone": None}
            ]
        }).to_list(length=10)
        
        print(f"    Users with incomplete profiles: {len(users_without_phone)}")
        
        if users_without_phone:
            for user in users_without_phone[:3]:  # Show first 3
                print(f"    - User: {user.get('name', 'Unknown')} | Phone: '{user.get('phone', 'None')}' | Email: {user.get('email', 'None')}")
        
        # Find users with complete profiles
        users_with_phone = await db.users.find({
            "phone": {"$ne": "", "$exists": True, "$ne": None}
        }).to_list(length=5)
        
        print(f"    Users with complete profiles: {len(users_with_phone)}")
        
        mongo_client.close()
        
    except Exception as e:
        print(f"    Database check error: {e}")
    
    print("\n💡 KEY INSIGHTS:")
    print("   1. Backend Razorpay integration is working (confirmed by testing agent)")
    print("   2. Payment creation requires authenticated user with phone number")
    print("   3. Frontend error likely due to:")
    print("      a) User not completing profile (adding phone number)")
    print("      b) Authentication issue during payment flow")
    print("      c) Frontend not handling 400 error properly when profile incomplete")

if __name__ == "__main__":
    asyncio.run(test_payment_scenarios())
