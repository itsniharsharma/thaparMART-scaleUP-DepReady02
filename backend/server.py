from fastapi import FastAPI, APIRouter, HTTPException, Request, Response, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timezone, timedelta
import httpx
import base64
import json
import boto3
from botocore.exceptions import ClientError
import razorpay

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# AWS S3 configuration
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
    aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
    region_name=os.environ['AWS_REGION']
)
S3_BUCKET_NAME = os.environ['S3_BUCKET_NAME']

# Razorpay configuration
razorpay_client = razorpay.Client(auth=(os.environ['RAZORPAY_KEY_ID'], os.environ['RAZORPAY_KEY_SECRET']))

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: str
    name: str
    picture: Optional[str] = None
    phone: str  # Now mandatory
    bio: Optional[str] = None
    # New fields for custom registration
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    thapar_email: Optional[str] = None
    is_faculty: bool = False
    # Student specific fields
    branch: Optional[str] = None
    roll_number: Optional[str] = None
    batch: Optional[str] = None
    # Faculty specific fields
    department: Optional[str] = None
    # Registration status
    is_registered: bool = False  # Track if user completed custom registration
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str
    name: str
    picture: Optional[str] = None

class UserUpdate(BaseModel):
    phone: str  # Now mandatory
    bio: Optional[str] = None
    picture: Optional[str] = None

class UserRegistration(BaseModel):
    first_name: str
    last_name: str
    thapar_email_prefix: str  # Just the XXXX part before @thapar.edu
    is_faculty: bool = False
    # Student fields (required if not faculty)
    branch: Optional[str] = None
    roll_number: Optional[str] = None
    batch: Optional[str] = None
    # Faculty fields (required if faculty)
    department: Optional[str] = None

class Product(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    price: float
    category: str  # Electronics, Clothes, Stationery, Notes
    images: List[str] = []  # S3 image URLs
    seller_id: str
    seller_name: str
    seller_email: str
    seller_phone: str  # Added seller phone number
    is_sold: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ProductCreate(BaseModel):
    title: str
    description: str
    price: float
    category: str

class Session(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    session_token: str
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PaymentOrder(BaseModel):
    amount: int  # Amount in paise (20 Rs = 2000 paise)
    currency: str = "INR"
    receipt: str

class PaymentToken(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    payment_id: str
    order_id: str
    amount: int
    status: str  # 'created', 'paid', 'used'
    expires_at: datetime
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class PaymentVerification(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

# Authentication helpers
async def upload_image_to_s3(image_content: bytes, filename: str, content_type: str) -> str:
    """Upload image to S3 and return the public URL"""
    try:
        # Generate unique filename
        unique_filename = f"products/{uuid.uuid4()}_{filename}"
        
        # Upload to S3
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=unique_filename,
            Body=image_content,
            ContentType=content_type,
            ACL='public-read'  # Make images publicly accessible
        )
        
        # Return public URL
        return f"https://{S3_BUCKET_NAME}.s3.{os.environ['AWS_REGION']}.amazonaws.com/{unique_filename}"
    
    except ClientError as e:
        logging.error(f"Failed to upload image to S3: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload image")

async def get_current_user(request: Request):
    # Check for session token in cookies first
    session_token = request.cookies.get('session_token')
    
    # Fallback to Authorization header
    if not session_token:
        auth_header = request.headers.get('authorization', '')
        if auth_header.startswith('Bearer '):
            session_token = auth_header.split(' ')[1]
    
    if not session_token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Check if session exists and is not expired
    session = await db.sessions.find_one({
        "session_token": session_token,
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not session:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    # Get user data
    user = await db.users.find_one({"id": session["user_id"]})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return User(**user)

# Authentication routes
@api_router.post("/auth/session", response_model=User)
async def authenticate_session(session_id: str = Form(...), response: Response = Response()):
    """Exchange Emergent session ID for user data and create local session"""
    
    # Call Emergent auth API
    async with httpx.AsyncClient() as client:
        try:
            auth_response = await client.get(
                "https://demobackend.emergentagent.com/auth/v1/env/oauth/session-data",
                headers={"X-Session-ID": session_id}
            )
            auth_response.raise_for_status()
            user_data = auth_response.json()
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Failed to authenticate: {str(e)}")
    
    # Check if user exists
    existing_user = await db.users.find_one({"email": user_data["email"]})
    
    if not existing_user:
        # Create new user with empty phone - they'll need to complete profile
        user_dict = {
            "id": str(uuid.uuid4()),
            "email": user_data["email"],
            "name": user_data["name"],
            "picture": user_data.get("picture"),
            "phone": "",  # Empty phone - needs to be completed
            "bio": None,
            "created_at": datetime.now(timezone.utc)
        }
        await db.users.insert_one(user_dict)
        user = User(**user_dict)
    else:
        user = User(**existing_user)
    
    # Create session
    session_token = str(uuid.uuid4())
    session = Session(
        user_id=user.id,
        session_token=session_token,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    
    await db.sessions.insert_one(session.dict())
    
    # Set HTTP-only cookie
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=7 * 24 * 60 * 60,  # 7 days
        httponly=True,
        secure=True,
        samesite="none",
        path="/"
    )
    
    return user

@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(user: User = Depends(get_current_user)):
    """Get current user information"""
    return user

@api_router.post("/auth/logout")
async def logout(request: Request, response: Response):
    """Logout current user"""
    session_token = request.cookies.get('session_token')
    if session_token:
        # Delete session from database
        await db.sessions.delete_one({"session_token": session_token})
    
    # Clear cookie
    response.delete_cookie(key="session_token", path="/")
    return {"message": "Logged out successfully"}

# User routes
@api_router.put("/users/profile", response_model=User)
async def update_profile(
    profile_data: UserUpdate,
    user: User = Depends(get_current_user)
):
    """Update user profile"""
    update_data = {k: v for k, v in profile_data.dict().items() if v is not None}
    
    if update_data:
        await db.users.update_one(
            {"id": user.id},
            {"$set": update_data}
        )
    
    # Return updated user
    updated_user = await db.users.find_one({"id": user.id})
    return User(**updated_user)

@api_router.get("/users/{user_id}", response_model=User)
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    user = await db.users.find_one({"id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return User(**user)

@api_router.get("/users/profile/complete")
async def check_profile_complete(user: User = Depends(get_current_user)):
    """Check if user profile is complete (has phone number)"""
    is_complete = bool(user.phone and user.phone.strip())
    return {"complete": is_complete, "missing_fields": [] if is_complete else ["phone"]}

# Payment routes
@api_router.post("/payment/create-order")
async def create_payment_order(user: User = Depends(get_current_user)):
    """Create a Razorpay order for product upload payment (20 Rs)"""
    
    # Check if user has completed profile
    if not user.phone or user.phone.strip() == "":
        raise HTTPException(status_code=400, detail="Please complete your profile with phone number first")
    
    try:
        # Create Razorpay order for 20 Rs (2000 paise)
        # Generate short receipt ID (max 40 chars)
        receipt_id = f"fee_{user.id[:8]}_{str(uuid.uuid4())[:8]}"
        
        order_data = {
            "amount": 2000,  # 20 Rs in paise
            "currency": "INR",
            "receipt": receipt_id,
            "payment_capture": 1
        }
        
        razorpay_order = razorpay_client.order.create(order_data)
        
        # Store payment token in database
        payment_token = PaymentToken(
            user_id=user.id,
            payment_id="",  # Will be updated after successful payment
            order_id=razorpay_order["id"],
            amount=2000,
            status="created",
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1)  # 1 hour expiry
        )
        
        await db.payment_tokens.insert_one(payment_token.dict())
        
        return {
            "order_id": razorpay_order["id"],
            "amount": razorpay_order["amount"],
            "currency": razorpay_order["currency"],
            "key": os.environ['RAZORPAY_KEY_ID']
        }
        
    except Exception as e:
        logging.error(f"Failed to create Razorpay order: {e}")
        raise HTTPException(status_code=500, detail="Failed to create payment order")

@api_router.post("/payment/verify")
async def verify_payment(
    verification: PaymentVerification,
    user: User = Depends(get_current_user)
):
    """Verify payment and activate upload token"""
    
    try:
        # Verify payment signature
        razorpay_client.utility.verify_payment_signature({
            'razorpay_order_id': verification.razorpay_order_id,
            'razorpay_payment_id': verification.razorpay_payment_id,
            'razorpay_signature': verification.razorpay_signature
        })
        
        # Update payment token status
        await db.payment_tokens.update_one(
            {
                "user_id": user.id,
                "order_id": verification.razorpay_order_id,
                "status": "created"
            },
            {
                "$set": {
                    "payment_id": verification.razorpay_payment_id,
                    "status": "paid"
                }
            }
        )
        
        return {"status": "success", "message": "Payment verified successfully. You can now upload products!"}
        
    except Exception as e:
        logging.error(f"Payment verification failed: {e}")
        raise HTTPException(status_code=400, detail="Payment verification failed")

@api_router.get("/payment/tokens")
async def get_user_payment_tokens(user: User = Depends(get_current_user)):
    """Get user's payment tokens"""
    
    tokens = await db.payment_tokens.find({
        "user_id": user.id,
        "status": "paid",
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    }).sort("created_at", -1).to_list(length=None)
    
    return [PaymentToken(**token) for token in tokens]

async def check_valid_upload_token(user: User = Depends(get_current_user)):
    """Check if user has a valid upload token"""
    
    valid_token = await db.payment_tokens.find_one({
        "user_id": user.id,
        "status": "paid",
        "expires_at": {"$gt": datetime.now(timezone.utc)}
    })
    
    if not valid_token:
        raise HTTPException(
            status_code=402, 
            detail="Payment required. Please pay ₹20 to upload products."
        )
    
    return valid_token

# Product routes
@api_router.post("/products", response_model=Product)
async def create_product(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    images: List[UploadFile] = File([]),
    user: User = Depends(get_current_user),
    payment_token: dict = Depends(check_valid_upload_token)
):
    """Create a new product (requires payment token)"""
    
    # Check if user has completed their profile (phone number required)
    if not user.phone or user.phone.strip() == "":
        raise HTTPException(status_code=400, detail="Please complete your profile with phone number before creating products")
    
    if category not in ["Electronics", "Clothes", "Stationery", "Notes"]:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Process images - upload to S3
    image_urls = []
    for image in images:
        if image.size > 10 * 1024 * 1024:  # 10MB limit
            raise HTTPException(status_code=400, detail=f"Image {image.filename} is too large. Max size is 10MB")
        
        content = await image.read()
        # Upload to S3 and get URL
        image_url = await upload_image_to_s3(content, image.filename, image.content_type)
        image_urls.append(image_url)
    
    product = Product(
        title=title,
        description=description,
        price=price,
        category=category,
        images=image_urls,  # Store S3 URLs instead of base64
        seller_id=user.id,
        seller_name=user.name,
        seller_email=user.email,
        seller_phone=user.phone  # Include seller phone
    )
    
    await db.products.insert_one(product.dict())
    
    # Mark payment token as used
    await db.payment_tokens.update_one(
        {"_id": payment_token["_id"]},
        {"$set": {"status": "used"}}
    )
    
    return product

@api_router.get("/products", response_model=List[Product])
async def get_products(category: Optional[str] = None):
    """Get all products, optionally filtered by category"""
    query = {"is_sold": False}
    if category and category in ["Electronics", "Clothes", "Stationery", "Notes"]:
        query["category"] = category
    
    products = await db.products.find(query).sort("created_at", -1).to_list(length=None)
    return [Product(**product) for product in products]

@api_router.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get product by ID"""
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return Product(**product)

@api_router.get("/products/user/{user_id}", response_model=List[Product])
async def get_user_products(user_id: str):
    """Get all products by a specific user"""
    products = await db.products.find({"seller_id": user_id}).sort("created_at", -1).to_list(length=None)
    return [Product(**product) for product in products]

@api_router.put("/products/{product_id}/sold")
async def mark_product_sold(
    product_id: str,
    user: User = Depends(get_current_user)
):
    """Mark a product as sold"""
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["seller_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to modify this product")
    
    await db.products.update_one(
        {"id": product_id},
        {"$set": {"is_sold": True}}
    )
    
    return {"message": "Product marked as sold"}

@api_router.delete("/products/{product_id}")
async def delete_product(
    product_id: str,
    user: User = Depends(get_current_user)
):
    """Delete a product"""
    product = await db.products.find_one({"id": product_id})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if product["seller_id"] != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this product")
    
    await db.products.delete_one({"id": product_id})
    return {"message": "Product deleted successfully"}

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