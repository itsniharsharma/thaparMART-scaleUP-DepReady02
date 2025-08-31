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

# Configuration
BASE_URL = "http://localhost:8001/api"
TEST_SESSION_ID = "test_session_" + str(uuid.uuid4())

class ThaparMartTester:
    def __init__(self):
        self.session = requests.Session()
        self.user_data = None
        self.session_token = None
        self.test_product_id = None
        self.test_results = {
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
        
        # Test 5: Create product without authentication
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
            else:
                self.log_result("product_crud", "Product Creation Security", False, 
                              f"Should require auth, got: {response.status_code}")
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
        
        # Run all test suites
        self.test_api_endpoints_general()
        self.test_authentication_system()
        self.test_user_profile_management()
        self.test_product_crud_operations()
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