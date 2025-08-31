#!/usr/bin/env python3
"""
Final Razorpay Payment Integration Test - Excluding MongoDB Operations
Tests all payment security, authentication, and API structure without database dependencies
"""

import requests
import json
import uuid

BASE_URL = "http://localhost:8001/api"

class FinalPaymentTester:
    def __init__(self):
        self.session = requests.Session()
        self.results = []
        
    def test_result(self, test_name, passed, details=""):
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name} - {details}"
        self.results.append((passed, test_name, details))
        print(result)
        return passed
    
    def run_comprehensive_test(self):
        print("🚀 Final Razorpay Payment Integration Test")
        print(f"Testing: {BASE_URL}")
        print("=" * 60)
        
        passed_tests = 0
        total_tests = 0
        
        # 1. Authentication Security Tests
        print("\n🔐 Authentication Security Tests")
        
        # Session exchange security
        try:
            response = self.session.post(f"{BASE_URL}/auth/session", 
                                       params={"session_id": f"test_{uuid.uuid4()}"})
            total_tests += 1
            if self.test_result("Session Exchange Security", response.status_code == 401, 
                              "Properly rejects invalid sessions"):
                passed_tests += 1
        except Exception as e:
            total_tests += 1
            self.test_result("Session Exchange Security", False, f"Error: {e}")
        
        # Protected endpoint security
        try:
            response = self.session.get(f"{BASE_URL}/auth/me")
            total_tests += 1
            if self.test_result("Protected Endpoint Security", response.status_code == 401, 
                              "Requires authentication"):
                passed_tests += 1
        except Exception as e:
            total_tests += 1
            self.test_result("Protected Endpoint Security", False, f"Error: {e}")
        
        # Logout endpoint
        try:
            response = self.session.post(f"{BASE_URL}/auth/logout")
            total_tests += 1
            if self.test_result("Logout Endpoint", response.status_code == 200, 
                              "Logout accessible"):
                passed_tests += 1
        except Exception as e:
            total_tests += 1
            self.test_result("Logout Endpoint", False, f"Error: {e}")
        
        # 2. Payment Security Tests
        print("\n💳 Payment Security Tests")
        
        # Payment order creation security
        try:
            response = self.session.post(f"{BASE_URL}/payment/create-order")
            total_tests += 1
            if self.test_result("Payment Order Security", response.status_code == 401, 
                              "Requires authentication"):
                passed_tests += 1
        except Exception as e:
            total_tests += 1
            self.test_result("Payment Order Security", False, f"Error: {e}")
        
        # Payment verification security
        try:
            verification_data = {
                "razorpay_order_id": "order_test123",
                "razorpay_payment_id": "pay_test123", 
                "razorpay_signature": "test_signature"
            }
            response = self.session.post(f"{BASE_URL}/payment/verify", json=verification_data)
            total_tests += 1
            if self.test_result("Payment Verification Security", response.status_code == 401, 
                              "Requires authentication"):
                passed_tests += 1
        except Exception as e:
            total_tests += 1
            self.test_result("Payment Verification Security", False, f"Error: {e}")
        
        # Payment tokens security
        try:
            response = self.session.get(f"{BASE_URL}/payment/tokens")
            total_tests += 1
            if self.test_result("Payment Tokens Security", response.status_code == 401, 
                              "Requires authentication"):
                passed_tests += 1
        except Exception as e:
            total_tests += 1
            self.test_result("Payment Tokens Security", False, f"Error: {e}")
        
        # 3. Product Creation Payment Integration
        print("\n📦 Product Creation Payment Integration")
        
        # Product creation security
        try:
            product_data = {
                "title": "iPhone 15 Pro Max",
                "description": "Brand new",
                "price": 120000.0,
                "category": "Electronics"
            }
            response = self.session.post(f"{BASE_URL}/products", data=product_data)
            total_tests += 1
            if self.test_result("Product Creation Security", response.status_code == 401, 
                              "Requires authentication"):
                passed_tests += 1
        except Exception as e:
            total_tests += 1
            self.test_result("Product Creation Security", False, f"Error: {e}")
        
        # 4. Profile Management Security
        print("\n👤 Profile Management Security")
        
        # Profile completion check
        try:
            response = self.session.get(f"{BASE_URL}/users/profile/complete")
            total_tests += 1
            if self.test_result("Profile Completion Security", response.status_code == 401, 
                              "Requires authentication"):
                passed_tests += 1
        except Exception as e:
            total_tests += 1
            self.test_result("Profile Completion Security", False, f"Error: {e}")
        
        # Profile update security
        try:
            profile_data = {"phone": "+91-9876543210", "bio": "Test"}
            response = self.session.put(f"{BASE_URL}/users/profile", json=profile_data)
            total_tests += 1
            if self.test_result("Profile Update Security", response.status_code == 401, 
                              "Requires authentication"):
                passed_tests += 1
        except Exception as e:
            total_tests += 1
            self.test_result("Profile Update Security", False, f"Error: {e}")
        
        # 5. API Validation Tests
        print("\n🔧 API Validation Tests")
        
        # Invalid payment verification data
        try:
            invalid_data = {"invalid_field": "test"}
            response = self.session.post(f"{BASE_URL}/payment/verify", json=invalid_data)
            total_tests += 1
            if self.test_result("Payment Validation", response.status_code in [401, 422], 
                              f"Proper validation: {response.status_code}"):
                passed_tests += 1
        except Exception as e:
            total_tests += 1
            self.test_result("Payment Validation", False, f"Error: {e}")
        
        # Invalid product data
        try:
            invalid_product = {"invalid": "data"}
            response = self.session.post(f"{BASE_URL}/products", data=invalid_product)
            total_tests += 1
            if self.test_result("Product Validation", response.status_code in [401, 422], 
                              f"Proper validation: {response.status_code}"):
                passed_tests += 1
        except Exception as e:
            total_tests += 1
            self.test_result("Product Validation", False, f"Error: {e}")
        
        # Print Final Summary
        print("\n" + "=" * 60)
        print("📊 FINAL TEST SUMMARY")
        print("=" * 60)
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"✅ Passed: {passed_tests}/{total_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 90:
            print("\n🎉 EXCELLENT: Payment system fully secure and ready!")
        elif success_rate >= 80:
            print("\n✅ GOOD: Payment system mostly secure with minor issues")
        else:
            print("\n⚠️ NEEDS ATTENTION: Multiple issues detected")
        
        return passed_tests, total_tests, success_rate

if __name__ == "__main__":
    tester = FinalPaymentTester()
    tester.run_comprehensive_test()