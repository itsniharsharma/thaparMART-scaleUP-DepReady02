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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    email: str
    name: str
    picture: Optional[str] = None

class UserUpdate(BaseModel):
    phone: str  # Now mandatory
    bio: Optional[str] = None
    picture: Optional[str] = None

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
async def authenticate_session(session_id: str, response: Response):
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

# Product routes
@api_router.post("/products", response_model=Product)
async def create_product(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    category: str = Form(...),
    images: List[UploadFile] = File([]),
    user: User = Depends(get_current_user)
):
    """Create a new product"""
    
    if category not in ["Electronics", "Clothes", "Stationery", "Notes"]:
        raise HTTPException(status_code=400, detail="Invalid category")
    
    # Process images
    image_data = []
    for image in images:
        content = await image.read()
        # Convert to base64
        base64_image = base64.b64encode(content).decode('utf-8')
        image_data.append(f"data:{image.content_type};base64,{base64_image}")
    
    product = Product(
        title=title,
        description=description,
        price=price,
        category=category,
        images=image_data,
        seller_id=user.id,
        seller_name=user.name,
        seller_email=user.email
    )
    
    await db.products.insert_one(product.dict())
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
    return [Product(**products) for product in products]

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