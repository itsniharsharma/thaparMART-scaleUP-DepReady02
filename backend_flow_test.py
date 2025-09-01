#!/usr/bin/env python3
"""
Backend Flow Simulation Test
Simulate the exact backend flow to identify where the payment order creation fails
"""

import asyncio
import os
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from dotenv import load_dotenv
import razorpay
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
import logging

# Load environment variables
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Models (simplified versions from backend)
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str = ""
    name: str = ""
    phone: str = ""  # This is the key field for payment
    first_name: str = ""
    last_name: str = ""
    thapar_email: str = ""
    is_faculty: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PaymentToken(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    payment_id: str
    order_id: str
    amount: int
    status: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class BackendFlowTester:
    def __init__(self):
        self.mongo_client = None
        self.db = None
        self.razorpay_client = None
        
    async def setup(self):
        """Setup database and Razorpay connections"""
        print("🔧 Setting up connections...")
        
        try:
            # Setup MongoDB connection
            mongo_url = os.environ['MONGO_URL']
            self.mongo_client = AsyncIOMotorClient(mongo_url)
            self.db = self.mongo_client[os.environ['DB_NAME']]
            print("    ✅ MongoDB connection established")
            
            # Setup Razorpay client
            self.razorpay_client = razorpay.Client(auth=(
                os.environ['RAZORPAY_KEY_ID'], 
                os.environ['RAZORPAY_KEY_SECRET']
            ))
            print("    ✅ Razorpay client initialized")
            
            return True
            
        except Exception as e:
            print(f"    ❌ Setup failed: {str(e)}")
            return False
    
    async def create_test_user(self):
        """Create a test user for payment testing"""
        print("\n👤 Creating test user...")
        
        try:
            # Create user with phone number (complete profile)
            user_data = {
                "id": str(uuid.uuid4()),
                "email": "test@thapar.edu",
                "name": "Payment Test User",
                "phone": "+91-9876543210",  # Complete profile
                "first_name": "Payment",
                "last_name": "Test",
                "thapar_email": "paymenttest@thapar.edu",
                "is_faculty": False,
                "created_at": datetime.now(timezone.utc)
            }
            
            # Insert into database
            await self.db.users.insert_one(user_data)
            
            user = User(**user_data)
            print(f"    ✅ Test user created: {user.id}")
            print(f"    📊 Phone: {user.phone}")
            print(f"    📊 Profile complete: {bool(user.phone and user.phone.strip())}")
            
            return user
            
        except Exception as e:
            print(f"    ❌ Failed to create test user: {str(e)}")
            return None
    
    async def create_test_user_incomplete(self):
        """Create a test user with incomplete profile (no phone)"""
        print("\n👤 Creating test user with incomplete profile...")
        
        try:
            user_data = {
                "id": str(uuid.uuid4()),
                "email": "incomplete@thapar.edu",
                "name": "Incomplete Test User",
                "phone": "",  # Incomplete profile
                "first_name": "Incomplete",
                "last_name": "Test",
                "thapar_email": "incompletetest@thapar.edu",
                "is_faculty": False,
                "created_at": datetime.now(timezone.utc)
            }
            
            await self.db.users.insert_one(user_data)
            
            user = User(**user_data)
            print(f"    ✅ Incomplete test user created: {user.id}")
            print(f"    📊 Phone: '{user.phone}'")
            print(f"    📊 Profile complete: {bool(user.phone and user.phone.strip())}")
            
            return user
            
        except Exception as e:
            print(f"    ❌ Failed to create incomplete test user: {str(e)}")
            return None
    
    async def simulate_payment_order_creation(self, user):
        """Simulate the exact payment order creation flow from backend"""
        print(f"\n💳 Simulating payment order creation for user: {user.id}")
        
        try:
            # Step 1: Check if user has completed profile (same as backend)
            if not user.phone or user.phone.strip() == "":
                print("    ❌ Profile incomplete - phone number required")
                return False, "Please complete your profile with phone number first"
            
            print("    ✅ Profile complete - proceeding with payment order")
            
            # Step 2: Generate receipt ID (same as backend)
            receipt_id = f"fee_{user.id[:8]}_{str(uuid.uuid4())[:8]}"
            print(f"    📊 Receipt ID: {receipt_id} (length: {len(receipt_id)})")
            
            # Step 3: Prepare order data (same as backend)
            order_data = {
                "amount": 2000,  # 20 Rs in paise
                "currency": "INR",
                "receipt": receipt_id,
                "payment_capture": 1
            }
            print(f"    📊 Order data: {order_data}")
            
            # Step 4: Create Razorpay order (same as backend)
            razorpay_order = self.razorpay_client.order.create(order_data)
            print(f"    ✅ Razorpay order created successfully!")
            print(f"    📊 Order ID: {razorpay_order['id']}")
            print(f"    📊 Amount: {razorpay_order['amount']}")
            print(f"    📊 Status: {razorpay_order['status']}")
            
            # Step 5: Create payment token (same as backend)
            payment_token = PaymentToken(
                user_id=user.id,
                payment_id="",  # Will be updated after successful payment
                order_id=razorpay_order["id"],
                amount=2000,
                status="created",
                expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
            )
            
            # Step 6: Store in database (same as backend)
            await self.db.payment_tokens.insert_one(payment_token.dict())
            print(f"    ✅ Payment token stored in database")
            
            # Step 7: Return response (same as backend)
            response = {
                "order_id": razorpay_order["id"],
                "amount": razorpay_order["amount"],
                "currency": razorpay_order["currency"],
                "key": os.environ['RAZORPAY_KEY_ID']
            }
            print(f"    ✅ Response prepared: {response}")
            
            return True, response
            
        except Exception as e:
            error_msg = f"Failed to create Razorpay order: {str(e)}"
            print(f"    ❌ CRITICAL ERROR: {error_msg}")
            print(f"    📊 Error Type: {type(e).__name__}")
            
            # Log the exact error (same as backend)
            logger.error(error_msg)
            
            return False, "Failed to create payment order"
    
    async def test_complete_flow(self):
        """Test the complete payment flow"""
        print("🎯 TESTING COMPLETE PAYMENT ORDER CREATION FLOW")
        print("=" * 60)
        
        # Setup connections
        if not await self.setup():
            print("❌ Setup failed - cannot continue")
            return
        
        # Test 1: Complete user profile
        print("\n🧪 TEST 1: User with complete profile")
        complete_user = await self.create_test_user()
        if complete_user:
            success, result = await self.simulate_payment_order_creation(complete_user)
            if success:
                print("    ✅ PASS: Payment order creation successful")
            else:
                print(f"    ❌ FAIL: {result}")
        
        # Test 2: Incomplete user profile
        print("\n🧪 TEST 2: User with incomplete profile")
        incomplete_user = await self.create_test_user_incomplete()
        if incomplete_user:
            success, result = await self.simulate_payment_order_creation(incomplete_user)
            if not success and "phone number" in result:
                print("    ✅ PASS: Correctly rejected incomplete profile")
            else:
                print(f"    ❌ FAIL: Unexpected result - {result}")
        
        # Cleanup
        await self.cleanup()
    
    async def cleanup(self):
        """Cleanup connections"""
        if self.mongo_client:
            self.mongo_client.close()
            print("\n🧹 Cleanup completed")

async def main():
    """Run the backend flow test"""
    tester = BackendFlowTester()
    await tester.test_complete_flow()

if __name__ == "__main__":
    asyncio.run(main())