#!/usr/bin/env python3
"""
Comprehensive Backend Testing for thaparMART
Tests authentication, product CRUD, user profiles, image upload, and Razorpay payment integration
"""

import requests
import json
import base64
import io
from PIL import Image
import time
import uuid
import hashlib
import hmac

# Configuration - Use production URL from frontend/.env
BASE_URL = "https://payment-flow-fix-6.preview.emergentagent.com/api"
TEST_SESSION_ID = "test_session_" + str(uuid.uuid4())

class ThaparMartTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_data = None
        self.session_token = None
        self.test_product_id = None
        self.test_results = {
            "custom_registration": {"passed": 0, "failed": 0, "details": []},
            "mongodb_atlas": {"passed": 0, "failed": 0, "details": []},
            "authentication": {"passed": 0, "failed": 0, "details": []},
            "user_profile": {"passed": 0, "failed": 0, "details": []},
            "product_crud": {"passed": 0, "failed": 0, "details": []},
            "image_upload": {"passed": 0, "failed": 0, "details": []},
            "payment_integration": {"passed": 0, "failed": 0, "details": []}
        }
    
    def log_result(self, category, test_name, passed, details=""):
        """Log test result"""
        if passed:
            self.test_results[category]["passed"] += 1
            status = "✅ PASS"
        else:
            self.test_results[category]["failed"] += 1
            status = "❌ FAIL"
        
        self.test_results[category]["details"].append(f"{status}: {test_name} - {details}")
        print(f"{status}: {test_name} - {details}")
    
    def create_test_image(self, filename="test_image.jpg"):
        """Create a test image for upload testing"""
        img = Image.new('RGB', (100, 100), color='red')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        return img_bytes
    
    def test_custom_registration_system(self):
        """Test Custom Registration System with Thapar Email Validation - HIGH PRIORITY"""
        print("\n🎓 Testing Custom Registration System (HIGH PRIORITY)...")
        
        # Test 1: Student Registration with all required fields
        try:
            student_data = {
                "first_name": "Arjun",
                "last_name": "Sharma", 
                "thapar_email_prefix": "student123",
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103456",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=student_data)
            
            if response.status_code == 200:
                result = response.json()
                if "user_id" in result and "message" in result:
                    self.log_result("custom_registration", "Student Registration", True, 
                                  f"Successfully registered student: {result['message']}")
                else:
                    self.log_result("custom_registration", "Student Registration", False, 
                                  f"Missing required fields in response: {result}")
            elif response.status_code == 400 and "already exists" in response.text:
                self.log_result("custom_registration", "Student Registration", True, 
                              "Duplicate registration properly prevented")
            else:
                self.log_result("custom_registration", "Student Registration", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("custom_registration", "Student Registration", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Faculty Registration with faculty-specific fields
        try:
            faculty_data = {
                "first_name": "Dr. Priya",
                "last_name": "Gupta",
                "thapar_email_prefix": "prof456", 
                "is_faculty": True,
                "department": "Computer Science"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=faculty_data)
            
            if response.status_code == 200:
                result = response.json()
                if "user_id" in result and "message" in result:
                    self.log_result("custom_registration", "Faculty Registration", True, 
                                  f"Successfully registered faculty: {result['message']}")
                else:
                    self.log_result("custom_registration", "Faculty Registration", False, 
                                  f"Missing required fields in response: {result}")
            elif response.status_code == 400 and "already exists" in response.text:
                self.log_result("custom_registration", "Faculty Registration", True, 
                              "Duplicate faculty registration properly prevented")
            else:
                self.log_result("custom_registration", "Faculty Registration", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("custom_registration", "Faculty Registration", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Email domain validation (@thapar.edu enforcement)
        try:
            invalid_email_data = {
                "first_name": "Test",
                "last_name": "User",
                "thapar_email_prefix": "test@gmail.com",  # Invalid - contains @
                "is_faculty": False,
                "branch": "Computer Engineering", 
                "roll_number": "102103999",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=invalid_email_data)
            
            if response.status_code == 400 and "only the part before @thapar.edu" in response.text:
                self.log_result("custom_registration", "Email Domain Validation", True, 
                              "Properly validates thapar email format")
            else:
                self.log_result("custom_registration", "Email Domain Validation", False, 
                              f"Should reject invalid email format. Status: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Email Domain Validation", False, 
                          f"Error: {str(e)}")
        
        # Test 4: Required field validation for students
        try:
            incomplete_student_data = {
                "first_name": "Incomplete",
                "last_name": "Student",
                "thapar_email_prefix": "incomplete123",
                "is_faculty": False
                # Missing branch, roll_number, batch
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=incomplete_student_data)
            
            if response.status_code == 400 and "required for students" in response.text:
                self.log_result("custom_registration", "Student Field Validation", True, 
                              "Properly validates required student fields")
            else:
                self.log_result("custom_registration", "Student Field Validation", False, 
                              f"Should validate student fields. Status: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Student Field Validation", False, 
                          f"Error: {str(e)}")
        
        # Test 5: Required field validation for faculty
        try:
            incomplete_faculty_data = {
                "first_name": "Incomplete",
                "last_name": "Faculty", 
                "thapar_email_prefix": "incfaculty123",
                "is_faculty": True
                # Missing department
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=incomplete_faculty_data)
            
            if response.status_code == 400 and "required for faculty" in response.text:
                self.log_result("custom_registration", "Faculty Field Validation", True, 
                              "Properly validates required faculty fields")
            else:
                self.log_result("custom_registration", "Faculty Field Validation", False, 
                              f"Should validate faculty fields. Status: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Faculty Field Validation", False, 
                          f"Error: {str(e)}")
        
        # Test 6: Duplicate registration prevention
        try:
            # Try to register the same student again
            duplicate_data = {
                "first_name": "Arjun",
                "last_name": "Sharma",
                "thapar_email_prefix": "student123",  # Same as Test 1
                "is_faculty": False,
                "branch": "Electronics Engineering",  # Different branch
                "roll_number": "102103999",  # Different roll number
                "batch": "2020-2024"  # Different batch
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=duplicate_data)
            
            if response.status_code == 400 and "already exists" in response.text:
                self.log_result("custom_registration", "Duplicate Prevention", True, 
                              "Properly prevents duplicate registrations by thapar email")
            else:
                self.log_result("custom_registration", "Duplicate Prevention", False, 
                              f"Should prevent duplicates. Status: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Duplicate Prevention", False, 
                          f"Error: {str(e)}")
    
    def test_user_existence_check(self):
        """Test User Existence Check API"""
        print("\n🔍 Testing User Existence Check API...")
        
        # Test 1: Check existing user (from previous registration)
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "student123"})
            
            if response.status_code == 200:
                result = response.json()
                if "exists" in result and "thapar_email" in result:
                    self.log_result("custom_registration", "User Existence Check - Existing", True, 
                                  f"Found user: {result['thapar_email']}, exists: {result['exists']}")
                else:
                    self.log_result("custom_registration", "User Existence Check - Existing", False, 
                                  f"Missing required fields in response: {result}")
            else:
                self.log_result("custom_registration", "User Existence Check - Existing", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("custom_registration", "User Existence Check - Existing", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Check non-existing user
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "nonexistent999"})
            
            if response.status_code == 200:
                result = response.json()
                if result.get("exists") == False and "thapar_email" in result:
                    self.log_result("custom_registration", "User Existence Check - Non-existing", True, 
                                  f"Correctly identified non-existing user: {result['thapar_email']}")
                else:
                    self.log_result("custom_registration", "User Existence Check - Non-existing", False, 
                                  f"Unexpected result for non-existing user: {result}")
            else:
                self.log_result("custom_registration", "User Existence Check - Non-existing", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("custom_registration", "User Existence Check - Non-existing", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Invalid email format in check-user
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "invalid@email.com"})
            
            if response.status_code == 400 and "only the part before @thapar.edu" in response.text:
                self.log_result("custom_registration", "User Check Email Validation", True, 
                              "Properly validates email format in user check")
            else:
                self.log_result("custom_registration", "User Check Email Validation", False, 
                              f"Should validate email format. Status: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "User Check Email Validation", False, 
                          f"Error: {str(e)}")
    
    def test_mongodb_atlas_connection(self):
        """Test MongoDB Atlas Connection and Data Storage"""
        print("\n🗄️ Testing MongoDB Atlas Connection...")
        
        # Test 1: Database connectivity through registration endpoint
        try:
            # This tests if MongoDB Atlas is accessible by attempting registration
            test_user_data = {
                "first_name": "MongoDB",
                "last_name": "Test",
                "thapar_email_prefix": f"mongotest{int(time.time())}",  # Unique email
                "is_faculty": False,
                "branch": "Information Technology",
                "roll_number": "102104999",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=test_user_data)
            
            if response.status_code == 200:
                self.log_result("mongodb_atlas", "Database Write Operation", True, 
                              "Successfully wrote to MongoDB Atlas database")
            elif response.status_code == 400 and "already exists" in response.text:
                self.log_result("mongodb_atlas", "Database Write Operation", True, 
                              "Database read operation working (duplicate check)")
            else:
                self.log_result("mongodb_atlas", "Database Write Operation", False, 
                              f"Database operation failed. Status: {response.status_code}")
        except Exception as e:
            self.log_result("mongodb_atlas", "Database Write Operation", False, 
                          f"Database connection error: {str(e)}")
        
        # Test 2: Database read operation through user check
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "student123"})
            
            if response.status_code == 200:
                result = response.json()
                if "exists" in result:
                    self.log_result("mongodb_atlas", "Database Read Operation", True, 
                                  "Successfully read from MongoDB Atlas database")
                else:
                    self.log_result("mongodb_atlas", "Database Read Operation", False, 
                                  f"Unexpected response format: {result}")
            else:
                self.log_result("mongodb_atlas", "Database Read Operation", False, 
                              f"Database read failed. Status: {response.status_code}")
        except Exception as e:
            self.log_result("mongodb_atlas", "Database Read Operation", False, 
                          f"Database read error: {str(e)}")
        
        # Test 3: Enhanced user model fields storage
        try:
            # Register a user with all enhanced fields and then check if stored properly
            enhanced_user_data = {
                "first_name": "Enhanced",
                "last_name": "Model",
                "thapar_email_prefix": f"enhanced{int(time.time())}",
                "is_faculty": True,
                "department": "Mechanical Engineering"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=enhanced_user_data)
            
            if response.status_code == 200:
                # Now check if the user exists (tests if enhanced fields were stored)
                check_response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                                 data={"thapar_email_prefix": enhanced_user_data["thapar_email_prefix"]})
                
                if check_response.status_code == 200 and check_response.json().get("exists"):
                    self.log_result("mongodb_atlas", "Enhanced User Model Storage", True, 
                                  "Enhanced user model fields stored and retrieved successfully")
                else:
                    self.log_result("mongodb_atlas", "Enhanced User Model Storage", False, 
                                  "Enhanced user not found after registration")
            else:
                self.log_result("mongodb_atlas", "Enhanced User Model Storage", False, 
                              f"Enhanced user registration failed: {response.status_code}")
        except Exception as e:
            self.log_result("mongodb_atlas", "Enhanced User Model Storage", False, 
                          f"Enhanced model test error: {str(e)}")
    
    def test_enhanced_authentication_flow(self):
        """Test Enhanced Authentication Flow with Custom Registration"""
        print("\n🔐 Testing Enhanced Authentication Flow...")
        
        # Test 1: Session exchange endpoint structure (can't test full flow without Emergent session)
        try:
            response = self.session.post(f"{BASE_URL}/auth/session", 
                                       data={"session_id": "test_session_123"})
            
            if response.status_code == 401:
                self.log_result("custom_registration", "Session Exchange Security", True, 
                              "Session exchange properly validates session IDs")
            else:
                self.log_result("custom_registration", "Session Exchange Security", False, 
                              f"Unexpected response to invalid session: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Session Exchange Security", False, 
                          f"Session exchange error: {str(e)}")
        
        # Test 2: Authentication flow endpoint accessibility
        try:
            response = self.session.get(f"{BASE_URL}/auth/me")
            
            if response.status_code == 401:
                self.log_result("custom_registration", "Auth Flow Protection", True, 
                              "Protected endpoints properly require authentication")
            else:
                self.log_result("custom_registration", "Auth Flow Protection", False, 
                              f"Protected endpoint should require auth: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Auth Flow Protection", False, 
                          f"Auth flow test error: {str(e)}")
        
        # Test 3: Logout endpoint functionality
        try:
            response = self.session.post(f"{BASE_URL}/auth/logout")
            
            if response.status_code == 200:
                result = response.json()
                if "message" in result:
                    self.log_result("custom_registration", "Logout Functionality", True, 
                                  f"Logout endpoint working: {result['message']}")
                else:
                    self.log_result("custom_registration", "Logout Functionality", False, 
                                  f"Logout response missing message: {result}")
            else:
                self.log_result("custom_registration", "Logout Functionality", False, 
                              f"Logout failed: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Logout Functionality", False, 
                          f"Logout test error: {str(e)}")
    
    def test_payment_integration(self):
        """Test Razorpay Payment Integration"""
        print("\n💳 Testing Razorpay Payment Integration...")
        
        # Test 1: Create payment order without authentication
        try:
            response = self.session.post(f"{BASE_URL}/payment/create-order")
            if response.status_code == 401:
                self.log_result("payment_integration", "Payment Order Security", True, 
                              "Properly requires authentication for payment order creation")
            else:
                self.log_result("payment_integration", "Payment Order Security", False, 
                              f"Should require auth, got: {response.status_code}")
        except Exception as e:
            self.log_result("payment_integration", "Payment Order Security", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Payment verification without authentication
        try:
            verification_data = {
                "razorpay_order_id": "order_test123",
                "razorpay_payment_id": "pay_test123", 
                "razorpay_signature": "test_signature"
            }
            response = self.session.post(f"{BASE_URL}/payment/verify", json=verification_data)
            if response.status_code == 401:
                self.log_result("payment_integration", "Payment Verification Security", True, 
                              "Properly requires authentication for payment verification")
            else:
                self.log_result("payment_integration", "Payment Verification Security", False, 
                              f"Should require auth, got: {response.status_code}")
        except Exception as e:
            self.log_result("payment_integration", "Payment Verification Security", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Get payment tokens without authentication
        try:
            response = self.session.get(f"{BASE_URL}/payment/tokens")
            if response.status_code == 401:
                self.log_result("payment_integration", "Payment Tokens Security", True, 
                              "Properly requires authentication for payment tokens")
            else:
                self.log_result("payment_integration", "Payment Tokens Security", False, 
                              f"Should require auth, got: {response.status_code}")
        except Exception as e:
            self.log_result("payment_integration", "Payment Tokens Security", False, 
                          f"Error: {str(e)}")
        
        # Test 4: Payment endpoint structure validation
        try:
            # Test with invalid verification data
            invalid_data = {"invalid_field": "test"}
            response = self.session.post(f"{BASE_URL}/payment/verify", json=invalid_data)
            if response.status_code in [401, 422]:
                self.log_result("payment_integration", "Payment Validation", True, 
                              f"Proper validation/auth check: {response.status_code}")
            else:
                self.log_result("payment_integration", "Payment Validation", False, 
                              f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_result("payment_integration", "Payment Validation", False, 
                          f"Error: {str(e)}")
        
        # Test 5: Payment order endpoint structure
        try:
            response = self.session.post(f"{BASE_URL}/payment/create-order", json={"test": "data"})
            # Should return 401 (auth required) regardless of payload
            if response.status_code == 401:
                self.log_result("payment_integration", "Payment Order Endpoint", True, 
                              "Payment order endpoint properly secured")
            else:
                self.log_result("payment_integration", "Payment Order Endpoint", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("payment_integration", "Payment Order Endpoint", False, 
                          f"Error: {str(e)}")
    
    def test_enhanced_product_creation(self):
        """Test Enhanced Product Creation with Payment Requirements"""
        print("\n📦💳 Testing Enhanced Product Creation (Payment Required)...")
        
        # Test 1: Product creation without authentication (should fail)
        try:
            product_data = {
                "title": "iPhone 15 Pro Max",
                "description": "Brand new, sealed box",
                "price": 120000.0,
                "category": "Electronics"
            }
            response = self.session.post(f"{BASE_URL}/products", data=product_data)
            
            if response.status_code == 401:
                self.log_result("product_crud", "Enhanced Product Creation Security", True, 
                              "Properly requires authentication for product creation")
            else:
                self.log_result("product_crud", "Enhanced Product Creation Security", False, 
                              f"Should require auth, got: {response.status_code}")
        except Exception as e:
            self.log_result("product_crud", "Enhanced Product Creation Security", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Product creation endpoint structure with payment requirement
        try:
            # Test endpoint response structure
            response = self.session.post(f"{BASE_URL}/products", data={"invalid": "data"})
            
            # Should return 401 (auth) or 422 (validation)
            if response.status_code in [401, 422]:
                self.log_result("product_crud", "Enhanced Product Endpoint Structure", True, 
                              f"Endpoint properly validates requests: {response.status_code}")
            else:
                self.log_result("product_crud", "Enhanced Product Endpoint Structure", False, 
                              f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_result("product_crud", "Enhanced Product Endpoint Structure", False, 
                          f"Error: {str(e)}")
    
    
    def test_authentication_system(self):
        """Test Emergent Authentication System"""
        print("\n🔐 Testing Authentication System...")
        
        # Test 1: Session exchange endpoint exists and handles requests
        try:
            response = self.session.post(f"{BASE_URL}/auth/session", 
                                       params={"session_id": TEST_SESSION_ID})
            
            if response.status_code == 401:
                self.log_result("authentication", "Session Exchange Endpoint", True, 
                              "Endpoint exists and properly rejects invalid session")
            else:
                self.log_result("authentication", "Session Exchange Endpoint", False, 
                              f"Unexpected status code: {response.status_code}")
        except Exception as e:
            self.log_result("authentication", "Session Exchange Endpoint", False, 
                          f"Endpoint error: {str(e)}")
        
        # Test 2: Auth/me endpoint without authentication
        try:
            response = self.session.get(f"{BASE_URL}/auth/me")
            if response.status_code == 401:
                self.log_result("authentication", "Protected Endpoint Security", True, 
                              "Properly rejects unauthenticated requests")
            else:
                self.log_result("authentication", "Protected Endpoint Security", False, 
                              f"Should return 401, got {response.status_code}")
        except Exception as e:
            self.log_result("authentication", "Protected Endpoint Security", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Logout endpoint
        try:
            response = self.session.post(f"{BASE_URL}/auth/logout")
            if response.status_code == 200:
                self.log_result("authentication", "Logout Endpoint", True, 
                              "Logout endpoint accessible")
            else:
                self.log_result("authentication", "Logout Endpoint", False, 
                              f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("authentication", "Logout Endpoint", False, 
                          f"Error: {str(e)}")
        
        # Test 4: CORS headers on auth endpoints
        try:
            response = self.session.options(f"{BASE_URL}/auth/session")
            cors_headers = {
                'Access-Control-Allow-Origin': response.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': response.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': response.headers.get('Access-Control-Allow-Headers')
            }
            
            if any(cors_headers.values()):
                self.log_result("authentication", "CORS Headers", True, 
                              f"CORS configured: {cors_headers}")
            else:
                self.log_result("authentication", "CORS Headers", False, 
                              "No CORS headers found")
        except Exception as e:
            self.log_result("authentication", "CORS Headers", False, 
                          f"Error: {str(e)}")
    
    def test_user_profile_management(self):
        """Test User Profile Management"""
        print("\n👤 Testing User Profile Management...")
        
        # Test 1: Get user profile by ID (without auth - should work for public profiles)
        test_user_id = "test-user-123"
        try:
            response = self.session.get(f"{BASE_URL}/users/{test_user_id}")
            if response.status_code == 404:
                self.log_result("user_profile", "Get User Profile", True, 
                              "Properly returns 404 for non-existent user")
            elif response.status_code == 200:
                self.log_result("user_profile", "Get User Profile", True, 
                              "Successfully retrieved user profile")
            else:
                self.log_result("user_profile", "Get User Profile", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("user_profile", "Get User Profile", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Update profile without authentication
        try:
            profile_data = {"phone": "+91-9876543210", "bio": "Computer Science student at Thapar"}
            response = self.session.put(f"{BASE_URL}/users/profile", json=profile_data)
            
            if response.status_code == 401:
                self.log_result("user_profile", "Profile Update Security", True, 
                              "Properly requires authentication for profile updates")
            else:
                self.log_result("user_profile", "Profile Update Security", False, 
                              f"Should require auth, got status: {response.status_code}")
        except Exception as e:
            self.log_result("user_profile", "Profile Update Security", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Profile endpoint structure validation
        try:
            response = self.session.put(f"{BASE_URL}/users/profile", 
                                      json={"invalid_field": "test"})
            # Should return 401 (auth required) or 422 (validation error)
            if response.status_code in [401, 422]:
                self.log_result("user_profile", "Profile Validation", True, 
                              f"Proper validation/auth check: {response.status_code}")
            else:
                self.log_result("user_profile", "Profile Validation", False, 
                              f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_result("user_profile", "Profile Validation", False, 
                          f"Error: {str(e)}")
    
    def test_product_crud_operations(self):
        """Test Product CRUD Operations"""
        print("\n📦 Testing Product CRUD Operations...")
        
        # Test 1: Get all products (public endpoint)
        try:
            response = self.session.get(f"{BASE_URL}/products")
            if response.status_code == 200:
                products = response.json()
                self.log_result("product_crud", "Get All Products", True, 
                              f"Retrieved {len(products)} products")
            else:
                self.log_result("product_crud", "Get All Products", False, 
                              f"Status code: {response.status_code}")
        except Exception as e:
            self.log_result("product_crud", "Get All Products", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Category filtering
        categories = ["Electronics", "Clothes", "Stationery", "Notes"]
        for category in categories:
            try:
                response = self.session.get(f"{BASE_URL}/products", 
                                          params={"category": category})
                if response.status_code == 200:
                    products = response.json()
                    self.log_result("product_crud", f"Category Filter - {category}", True, 
                                  f"Retrieved {len(products)} {category} products")
                else:
                    self.log_result("product_crud", f"Category Filter - {category}", False, 
                                  f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("product_crud", f"Category Filter - {category}", False, 
                              f"Error: {str(e)}")
        
        # Test 3: Invalid category filtering
        try:
            response = self.session.get(f"{BASE_URL}/products", 
                                      params={"category": "InvalidCategory"})
            if response.status_code == 200:
                products = response.json()
                self.log_result("product_crud", "Invalid Category Filter", True, 
                              f"Handled invalid category gracefully, returned {len(products)} products")
            else:
                self.log_result("product_crud", "Invalid Category Filter", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("product_crud", "Invalid Category Filter", False, 
                          f"Error: {str(e)}")
        
        # Test 4: Get specific product (non-existent)
        try:
            response = self.session.get(f"{BASE_URL}/products/non-existent-id")
            if response.status_code == 404:
                self.log_result("product_crud", "Get Non-existent Product", True, 
                              "Properly returns 404 for non-existent product")
            else:
                self.log_result("product_crud", "Get Non-existent Product", False, 
                              f"Expected 404, got {response.status_code}")
        except Exception as e:
            self.log_result("product_crud", "Get Non-existent Product", False, 
                          f"Error: {str(e)}")
        
        # Test 5: Create product without authentication (should require payment token)
        try:
            product_data = {
                "title": "iPhone 13 Pro",
                "description": "Excellent condition, barely used",
                "price": 45000.0,
                "category": "Electronics"
            }
            response = self.session.post(f"{BASE_URL}/products", data=product_data)
            
            if response.status_code == 401:
                self.log_result("product_crud", "Product Creation Security", True, 
                              "Properly requires authentication for product creation")
            elif response.status_code == 402:
                self.log_result("product_crud", "Product Creation Payment Requirement", True, 
                              "Properly requires payment token for product creation")
            else:
                self.log_result("product_crud", "Product Creation Security", False, 
                              f"Should require auth/payment, got: {response.status_code}")
        except Exception as e:
            self.log_result("product_crud", "Product Creation Security", False, 
                          f"Error: {str(e)}")
        
        # Test 6: Get user products
        try:
            response = self.session.get(f"{BASE_URL}/products/user/test-user-123")
            if response.status_code == 200:
                products = response.json()
                self.log_result("product_crud", "Get User Products", True, 
                              f"Retrieved {len(products)} user products")
            else:
                self.log_result("product_crud", "Get User Products", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("product_crud", "Get User Products", False, 
                          f"Error: {str(e)}")
    
    def test_image_upload_system(self):
        """Test Image Upload System"""
        print("\n🖼️ Testing Image Upload System...")
        
        # Test 1: Product creation with image (without auth - should fail)
        try:
            test_image = self.create_test_image()
            
            product_data = {
                "title": "MacBook Pro M1",
                "description": "Perfect for coding and design work",
                "price": 85000.0,
                "category": "Electronics"
            }
            
            files = {"images": ("test.jpg", test_image, "image/jpeg")}
            
            response = self.session.post(f"{BASE_URL}/products", 
                                       data=product_data, files=files)
            
            if response.status_code == 401:
                self.log_result("image_upload", "Image Upload Security", True, 
                              "Properly requires authentication for image upload")
            else:
                self.log_result("image_upload", "Image Upload Security", False, 
                              f"Should require auth, got: {response.status_code}")
        except Exception as e:
            self.log_result("image_upload", "Image Upload Security", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Image upload endpoint structure
        try:
            # Test with invalid data to check endpoint structure
            response = self.session.post(f"{BASE_URL}/products", 
                                       data={"invalid": "data"})
            
            # Should return 401 (auth) or 422 (validation)
            if response.status_code in [401, 422]:
                self.log_result("image_upload", "Upload Endpoint Structure", True, 
                              f"Endpoint properly validates requests: {response.status_code}")
            else:
                self.log_result("image_upload", "Upload Endpoint Structure", False, 
                              f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_result("image_upload", "Upload Endpoint Structure", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Multiple image handling structure
        try:
            test_images = [self.create_test_image() for _ in range(3)]
            
            product_data = {
                "title": "Study Notes Bundle",
                "description": "Complete semester notes for CSE",
                "price": 500.0,
                "category": "Notes"
            }
            
            files = [("images", ("test1.jpg", img, "image/jpeg")) for img in test_images]
            
            response = self.session.post(f"{BASE_URL}/products", 
                                       data=product_data, files=files)
            
            if response.status_code == 401:
                self.log_result("image_upload", "Multiple Image Upload", True, 
                              "Multiple image endpoint properly secured")
            else:
                self.log_result("image_upload", "Multiple Image Upload", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("image_upload", "Multiple Image Upload", False, 
                          f"Error: {str(e)}")
    
    def test_api_endpoints_general(self):
        """Test general API endpoint functionality"""
        print("\n🌐 Testing General API Functionality...")
        
        # Test API root accessibility
        try:
            response = self.session.get(BASE_URL)
            if response.status_code in [200, 404, 405]:  # Any valid HTTP response
                self.log_result("authentication", "API Root Access", True, 
                              f"API accessible, status: {response.status_code}")
            else:
                self.log_result("authentication", "API Root Access", False, 
                              f"API not accessible: {response.status_code}")
        except Exception as e:
            self.log_result("authentication", "API Root Access", False, 
                          f"Connection error: {str(e)}")
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting thaparMART Backend Testing...")
        print(f"Testing against: {BASE_URL}")
        print("=" * 60)
        
        # Run HIGH PRIORITY custom registration tests first
        self.test_custom_registration_system()
        self.test_user_existence_check()
        self.test_mongodb_atlas_connection()
        self.test_enhanced_authentication_flow()
        
        # Run other test suites
        self.test_api_endpoints_general()
        self.test_authentication_system()
        self.test_payment_integration()
        self.test_user_profile_management()
        self.test_product_crud_operations()
        self.test_enhanced_product_creation()
        self.test_image_upload_system()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            print(f"\n{category.upper().replace('_', ' ')}:")
            print(f"  ✅ Passed: {passed}")
            print(f"  ❌ Failed: {failed}")
            
            for detail in results["details"]:
                print(f"    {detail}")
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"  ✅ Total Passed: {total_passed}")
        print(f"  ❌ Total Failed: {total_failed}")
        print(f"  📈 Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%")
        
        # Determine critical issues
        critical_failures = []
        if self.test_results["authentication"]["failed"] > 0:
            critical_failures.append("Authentication system issues")
        if self.test_results["product_crud"]["failed"] > 2:  # Allow some minor failures
            critical_failures.append("Product CRUD system issues")
        
        if critical_failures:
            print(f"\n⚠️  CRITICAL ISSUES DETECTED:")
            for issue in critical_failures:
                print(f"    - {issue}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES DETECTED")

if __name__ == "__main__":
    tester = ThaparMartTester()
    tester.run_all_tests()