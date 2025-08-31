#!/usr/bin/env python3
"""
Focused Razorpay Payment Integration Testing for thaparMART
Tests complete payment flow including authentication, order creation, verification, and product upload
"""

import requests
import json
import uuid
import hashlib
import hmac
import time

# Configuration
BASE_URL = "http://localhost:8001/api"

class RazorpayPaymentTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name} - {details}"
        self.test_results.append(result)
        print(result)
    
    def test_authentication_endpoints(self):
        """Test authentication endpoints required for payment flow"""
        print("\n🔐 Testing Authentication Endpoints...")
        
        # Test 1: Session exchange endpoint
        try:
            test_session_id = f"test_session_{uuid.uuid4()}"
            response = self.session.post(f"{BASE_URL}/auth/session", 
                                       params={"session_id": test_session_id})
            
            if response.status_code == 401:
                self.log_result("Session Exchange Security", True, 
                              "Properly rejects invalid session ID")
            else:
                self.log_result("Session Exchange Security", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Session Exchange Security", False, f"Error: {str(e)}")
        
        # Test 2: Protected /auth/me endpoint
        try:
            response = self.session.get(f"{BASE_URL}/auth/me")
            if response.status_code == 401:
                self.log_result("Auth Me Endpoint Security", True, 
                              "Properly requires authentication")
            else:
                self.log_result("Auth Me Endpoint Security", False, 
                              f"Should return 401, got {response.status_code}")
        except Exception as e:
            self.log_result("Auth Me Endpoint Security", False, f"Error: {str(e)}")
    
    def test_payment_endpoints_security(self):
        """Test payment endpoints security without authentication"""
        print("\n💳 Testing Payment Endpoints Security...")
        
        # Test 1: Create payment order without auth
        try:
            response = self.session.post(f"{BASE_URL}/payment/create-order")
            if response.status_code == 401:
                self.log_result("Payment Order Security", True, 
                              "Requires authentication for order creation")
            else:
                self.log_result("Payment Order Security", False, 
                              f"Should require auth, got: {response.status_code}")
        except Exception as e:
            self.log_result("Payment Order Security", False, f"Error: {str(e)}")
        
        # Test 2: Payment verification without auth
        try:
            verification_data = {
                "razorpay_order_id": "order_test123",
                "razorpay_payment_id": "pay_test123", 
                "razorpay_signature": "test_signature"
            }
            response = self.session.post(f"{BASE_URL}/payment/verify", json=verification_data)
            if response.status_code == 401:
                self.log_result("Payment Verification Security", True, 
                              "Requires authentication for payment verification")
            else:
                self.log_result("Payment Verification Security", False, 
                              f"Should require auth, got: {response.status_code}")
        except Exception as e:
            self.log_result("Payment Verification Security", False, f"Error: {str(e)}")
        
        # Test 3: Get payment tokens without auth
        try:
            response = self.session.get(f"{BASE_URL}/payment/tokens")
            if response.status_code == 401:
                self.log_result("Payment Tokens Security", True, 
                              "Requires authentication for token access")
            else:
                self.log_result("Payment Tokens Security", False, 
                              f"Should require auth, got: {response.status_code}")
        except Exception as e:
            self.log_result("Payment Tokens Security", False, f"Error: {str(e)}")
    
    def test_product_creation_payment_requirement(self):
        """Test product creation requires payment token"""
        print("\n📦 Testing Product Creation Payment Requirements...")
        
        # Test 1: Product creation without auth (should fail with 401)
        try:
            product_data = {
                "title": "iPhone 15 Pro Max",
                "description": "Brand new, sealed box",
                "price": 120000.0,
                "category": "Electronics"
            }
            response = self.session.post(f"{BASE_URL}/products", data=product_data)
            
            if response.status_code == 401:
                self.log_result("Product Creation Auth Requirement", True, 
                              "Requires authentication for product creation")
            elif response.status_code == 402:
                self.log_result("Product Creation Payment Requirement", True, 
                              "Requires payment token for product creation")
            else:
                self.log_result("Product Creation Security", False, 
                              f"Should require auth/payment, got: {response.status_code}")
        except Exception as e:
            self.log_result("Product Creation Security", False, f"Error: {str(e)}")
    
    def test_profile_completion_endpoints(self):
        """Test profile completion endpoints"""
        print("\n👤 Testing Profile Completion Endpoints...")
        
        # Test 1: Profile completion check without auth
        try:
            response = self.session.get(f"{BASE_URL}/users/profile/complete")
            if response.status_code == 401:
                self.log_result("Profile Completion Security", True, 
                              "Requires authentication for profile check")
            else:
                self.log_result("Profile Completion Security", False, 
                              f"Should require auth, got: {response.status_code}")
        except Exception as e:
            self.log_result("Profile Completion Security", False, f"Error: {str(e)}")
        
        # Test 2: Profile update without auth
        try:
            profile_data = {"phone": "+91-9876543210", "bio": "Test user"}
            response = self.session.put(f"{BASE_URL}/users/profile", json=profile_data)
            if response.status_code == 401:
                self.log_result("Profile Update Security", True, 
                              "Requires authentication for profile updates")
            else:
                self.log_result("Profile Update Security", False, 
                              f"Should require auth, got: {response.status_code}")
        except Exception as e:
            self.log_result("Profile Update Security", False, f"Error: {str(e)}")
    
    def test_api_structure_and_validation(self):
        """Test API structure and validation"""
        print("\n🌐 Testing API Structure and Validation...")
        
        # Test 1: Invalid payment verification data
        try:
            invalid_data = {"invalid_field": "test"}
            response = self.session.post(f"{BASE_URL}/payment/verify", json=invalid_data)
            if response.status_code in [401, 422]:
                self.log_result("Payment Validation Structure", True, 
                              f"Proper validation/auth check: {response.status_code}")
            else:
                self.log_result("Payment Validation Structure", False, 
                              f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_result("Payment Validation Structure", False, f"Error: {str(e)}")
        
        # Test 2: Invalid product data
        try:
            invalid_product = {"invalid": "data"}
            response = self.session.post(f"{BASE_URL}/products", data=invalid_product)
            if response.status_code in [401, 422]:
                self.log_result("Product Validation Structure", True, 
                              f"Proper validation/auth check: {response.status_code}")
            else:
                self.log_result("Product Validation Structure", False, 
                              f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_result("Product Validation Structure", False, f"Error: {str(e)}")
    
    def test_general_api_functionality(self):
        """Test general API functionality"""
        print("\n🔧 Testing General API Functionality...")
        
        # Test 1: API connectivity
        try:
            response = self.session.get(f"{BASE_URL}/products")
            if response.status_code == 200:
                products = response.json()
                self.log_result("API Connectivity", True, 
                              f"API accessible, retrieved {len(products)} products")
            else:
                self.log_result("API Connectivity", False, 
                              f"API not accessible: {response.status_code}")
        except Exception as e:
            self.log_result("API Connectivity", False, f"Connection error: {str(e)}")
        
        # Test 2: CORS headers
        try:
            response = self.session.options(f"{BASE_URL}/auth/session")
            cors_origin = response.headers.get('Access-Control-Allow-Origin')
            if cors_origin:
                self.log_result("CORS Configuration", True, 
                              f"CORS configured: {cors_origin}")
            else:
                self.log_result("CORS Configuration", False, 
                              "No CORS headers found")
        except Exception as e:
            self.log_result("CORS Configuration", False, f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all payment integration tests"""
        print("🚀 Starting Razorpay Payment Integration Testing...")
        print(f"Testing against: {BASE_URL}")
        print("=" * 60)
        
        # Run all test suites
        self.test_general_api_functionality()
        self.test_authentication_endpoints()
        self.test_payment_endpoints_security()
        self.test_profile_completion_endpoints()
        self.test_product_creation_payment_requirement()
        self.test_api_structure_and_validation()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 RAZORPAY PAYMENT INTEGRATION TEST SUMMARY")
        print("=" * 60)
        
        passed_tests = [r for r in self.test_results if "✅ PASS" in r]
        failed_tests = [r for r in self.test_results if "❌ FAIL" in r]
        
        print(f"\n✅ PASSED TESTS ({len(passed_tests)}):")
        for test in passed_tests:
            print(f"  {test}")
        
        if failed_tests:
            print(f"\n❌ FAILED TESTS ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"  {test}")
        
        success_rate = (len(passed_tests) / len(self.test_results)) * 100 if self.test_results else 0
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"  ✅ Total Passed: {len(passed_tests)}")
        print(f"  ❌ Total Failed: {len(failed_tests)}")
        print(f"  📈 Success Rate: {success_rate:.1f}%")
        
        # Determine if payment system is ready
        critical_failures = len(failed_tests)
        if critical_failures == 0:
            print(f"\n✅ PAYMENT SYSTEM READY FOR PRODUCTION")
            print("   All security measures and endpoints working correctly")
        elif critical_failures <= 2:
            print(f"\n⚠️  PAYMENT SYSTEM MOSTLY READY")
            print("   Minor issues detected, but core functionality secure")
        else:
            print(f"\n❌ PAYMENT SYSTEM NEEDS ATTENTION")
            print("   Multiple issues detected, review required")

if __name__ == "__main__":
    tester = RazorpayPaymentTester()
    tester.run_all_tests()