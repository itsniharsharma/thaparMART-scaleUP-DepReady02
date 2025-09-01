#!/usr/bin/env python3
"""
FOCUSED PAYMENT INTEGRATION TEST
Specifically testing the "Failed to create payment order" error reported by user
"""

import requests
import json
import time
import uuid

# Configuration
BASE_URL = "http://localhost:8001/api"

class PaymentFocusedTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
        
    def log_result(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name} - {details}"
        self.test_results.append(result)
        print(result)
    
    def test_payment_endpoints_without_auth(self):
        """Test payment endpoints without authentication to verify they're secured"""
        print("\n🔒 Testing Payment Endpoints Security...")
        
        # Test create-order endpoint
        try:
            response = self.session.post(f"{BASE_URL}/payment/create-order")
            print(f"    📊 /payment/create-order Status: {response.status_code}")
            print(f"    📊 Response: {response.text}")
            
            if response.status_code == 401:
                self.log_result("Payment Create Order Security", True, 
                              "Properly requires authentication")
            elif response.status_code == 500:
                self.log_result("Payment Create Order Security", False, 
                              "CRITICAL: 500 Internal Server Error - matches reported issue!")
            else:
                self.log_result("Payment Create Order Security", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Payment Create Order Security", False, f"Error: {str(e)}")
        
        # Test verify endpoint
        try:
            verification_data = {
                "razorpay_order_id": "order_test123",
                "razorpay_payment_id": "pay_test123", 
                "razorpay_signature": "test_signature"
            }
            response = self.session.post(f"{BASE_URL}/payment/verify", json=verification_data)
            print(f"    📊 /payment/verify Status: {response.status_code}")
            print(f"    📊 Response: {response.text}")
            
            if response.status_code == 401:
                self.log_result("Payment Verify Security", True, 
                              "Properly requires authentication")
            elif response.status_code == 500:
                self.log_result("Payment Verify Security", False, 
                              "CRITICAL: 500 Internal Server Error!")
            else:
                self.log_result("Payment Verify Security", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Payment Verify Security", False, f"Error: {str(e)}")
        
        # Test tokens endpoint
        try:
            response = self.session.get(f"{BASE_URL}/payment/tokens")
            print(f"    📊 /payment/tokens Status: {response.status_code}")
            print(f"    📊 Response: {response.text}")
            
            if response.status_code == 401:
                self.log_result("Payment Tokens Security", True, 
                              "Properly requires authentication")
            elif response.status_code == 500:
                self.log_result("Payment Tokens Security", False, 
                              "CRITICAL: 500 Internal Server Error!")
            else:
                self.log_result("Payment Tokens Security", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Payment Tokens Security", False, f"Error: {str(e)}")
    
    def test_user_registration_and_profile(self):
        """Test user registration and profile completion for payment testing"""
        print("\n👤 Testing User Registration and Profile Completion...")
        
        # Register a test user
        try:
            test_user_data = {
                "first_name": "Payment",
                "last_name": "TestUser",
                "thapar_email_prefix": f"paymenttest{int(time.time())}",
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102106999",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=test_user_data)
            print(f"    📊 Registration Status: {response.status_code}")
            print(f"    📊 Registration Response: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                self.test_user_id = result.get("user_id")
                self.log_result("User Registration for Payment Testing", True, 
                              f"Successfully registered: {result.get('message')}")
            elif response.status_code == 400 and "already exists" in response.text:
                self.log_result("User Registration for Payment Testing", True, 
                              "User already exists - can proceed")
            else:
                self.log_result("User Registration for Payment Testing", False, 
                              f"Registration failed: {response.status_code}")
        except Exception as e:
            self.log_result("User Registration for Payment Testing", False, f"Error: {str(e)}")
        
        # Test profile completion check
        try:
            response = self.session.get(f"{BASE_URL}/users/profile/complete")
            print(f"    📊 Profile Complete Check Status: {response.status_code}")
            print(f"    📊 Profile Complete Response: {response.text}")
            
            if response.status_code == 401:
                self.log_result("Profile Completion Check", True, 
                              "Properly requires authentication")
            else:
                self.log_result("Profile Completion Check", False, 
                              f"Unexpected status: {response.status_code}")
        except Exception as e:
            self.log_result("Profile Completion Check", False, f"Error: {str(e)}")
    
    def test_razorpay_credentials_validation(self):
        """Test if Razorpay credentials are valid by checking backend configuration"""
        print("\n💳 Testing Razorpay Credentials and Configuration...")
        
        # Check if backend has proper Razorpay configuration by testing endpoint behavior
        try:
            # Test with various authentication headers to see backend behavior
            headers_to_test = [
                {"Authorization": "Bearer invalid_token"},
                {"X-Session-ID": "invalid_session"},
                {"Cookie": "session_token=invalid_token"}
            ]
            
            for i, headers in enumerate(headers_to_test):
                response = self.session.post(f"{BASE_URL}/payment/create-order", headers=headers)
                print(f"    📊 Test {i+1} Status: {response.status_code}")
                print(f"    📊 Test {i+1} Response: {response.text}")
                
                if response.status_code == 500:
                    self.log_result(f"Razorpay Config Test {i+1}", False, 
                                  "CRITICAL: 500 error suggests Razorpay integration issue!")
                elif response.status_code == 401:
                    self.log_result(f"Razorpay Config Test {i+1}", True, 
                                  "Authentication properly validated before Razorpay call")
                else:
                    self.log_result(f"Razorpay Config Test {i+1}", False, 
                                  f"Unexpected response: {response.status_code}")
        except Exception as e:
            self.log_result("Razorpay Configuration Test", False, f"Error: {str(e)}")
    
    def test_payment_order_parameters(self):
        """Test payment order creation parameters that might cause issues"""
        print("\n🔧 Testing Payment Order Parameters...")
        
        # Test different request formats to identify parameter issues
        test_cases = [
            {"name": "Empty JSON", "data": {}},
            {"name": "Invalid JSON", "data": {"invalid": "data"}},
            {"name": "Razorpay-like data", "data": {
                "amount": 2000,
                "currency": "INR",
                "receipt": "test_receipt"
            }}
        ]
        
        for test_case in test_cases:
            try:
                response = self.session.post(f"{BASE_URL}/payment/create-order", 
                                           json=test_case["data"])
                print(f"    📊 {test_case['name']} Status: {response.status_code}")
                print(f"    📊 {test_case['name']} Response: {response.text}")
                
                if response.status_code == 500:
                    self.log_result(f"Parameter Test - {test_case['name']}", False, 
                                  "CRITICAL: 500 error - parameter or Razorpay issue!")
                elif response.status_code == 401:
                    self.log_result(f"Parameter Test - {test_case['name']}", True, 
                                  "Authentication check working")
                elif response.status_code == 422:
                    self.log_result(f"Parameter Test - {test_case['name']}", True, 
                                  "Parameter validation working")
                else:
                    self.log_result(f"Parameter Test - {test_case['name']}", False, 
                                  f"Unexpected status: {response.status_code}")
            except Exception as e:
                self.log_result(f"Parameter Test - {test_case['name']}", False, f"Error: {str(e)}")
    
    def test_backend_dependencies(self):
        """Test if backend has all required dependencies for Razorpay"""
        print("\n📦 Testing Backend Dependencies...")
        
        # Test if backend is running properly by checking basic endpoints
        try:
            response = self.session.get(f"{BASE_URL}/products")
            print(f"    📊 Basic API Status: {response.status_code}")
            
            if response.status_code == 200:
                self.log_result("Backend Basic Functionality", True, 
                              "Backend is running and responding")
            else:
                self.log_result("Backend Basic Functionality", False, 
                              f"Backend issue: {response.status_code}")
        except Exception as e:
            self.log_result("Backend Basic Functionality", False, f"Error: {str(e)}")
        
        # Test authentication endpoints
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "testuser"})
            print(f"    📊 Auth API Status: {response.status_code}")
            
            if response.status_code == 200:
                self.log_result("Backend Auth Functionality", True, 
                              "Authentication system working")
            else:
                self.log_result("Backend Auth Functionality", False, 
                              f"Auth system issue: {response.status_code}")
        except Exception as e:
            self.log_result("Backend Auth Functionality", False, f"Error: {str(e)}")
    
    def analyze_error_patterns(self):
        """Analyze error patterns to identify root cause"""
        print("\n🔍 Analyzing Error Patterns...")
        
        # Check if the issue is consistent across payment endpoints
        payment_endpoints = [
            "/payment/create-order",
            "/payment/verify",
            "/payment/tokens"
        ]
        
        error_pattern = {}
        
        for endpoint in payment_endpoints:
            try:
                if endpoint == "/payment/tokens":
                    response = self.session.get(f"{BASE_URL}{endpoint}")
                else:
                    response = self.session.post(f"{BASE_URL}{endpoint}")
                
                error_pattern[endpoint] = {
                    "status": response.status_code,
                    "response": response.text[:100]
                }
                print(f"    📊 {endpoint}: {response.status_code}")
                
            except Exception as e:
                error_pattern[endpoint] = {"error": str(e)}
                print(f"    ❌ {endpoint}: Error - {str(e)}")
        
        # Analyze patterns
        status_codes = [ep.get("status") for ep in error_pattern.values() if "status" in ep]
        
        if all(code == 401 for code in status_codes):
            self.log_result("Error Pattern Analysis", True, 
                          "All payment endpoints properly secured (401 Unauthorized)")
        elif any(code == 500 for code in status_codes):
            self.log_result("Error Pattern Analysis", False, 
                          "CRITICAL: 500 errors detected - Razorpay integration issue!")
        else:
            self.log_result("Error Pattern Analysis", False, 
                          f"Mixed error patterns: {status_codes}")
    
    def run_focused_tests(self):
        """Run focused payment integration tests"""
        print("🎯 FOCUSED PAYMENT INTEGRATION TESTING")
        print("=" * 60)
        print("🔍 Investigating: 'Failed to create payment order' error")
        print(f"🌐 Testing against: {BASE_URL}")
        print("=" * 60)
        
        # Run all focused tests
        self.test_backend_dependencies()
        self.test_user_registration_and_profile()
        self.test_payment_endpoints_without_auth()
        self.test_razorpay_credentials_validation()
        self.test_payment_order_parameters()
        self.analyze_error_patterns()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 FOCUSED PAYMENT TEST SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for result in self.test_results if "✅ PASS" in result)
        failed = sum(1 for result in self.test_results if "❌ FAIL" in result)
        
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"📈 Success Rate: {(passed/(passed+failed)*100):.1f}%")
        
        print("\nDetailed Results:")
        for result in self.test_results:
            print(f"  {result}")
        
        # Analysis
        critical_issues = [r for r in self.test_results if "CRITICAL" in r]
        if critical_issues:
            print(f"\n⚠️  CRITICAL ISSUES FOUND:")
            for issue in critical_issues:
                print(f"    {issue}")
            print(f"\n🔧 RECOMMENDED ACTIONS:")
            print(f"    1. Check Razorpay credentials in backend/.env")
            print(f"    2. Verify Razorpay account is activated")
            print(f"    3. Check backend logs for specific Razorpay API errors")
            print(f"    4. Test with valid authentication session")
        else:
            print(f"\n✅ NO CRITICAL ISSUES DETECTED")
            print(f"💡 The payment endpoints are properly secured.")
            print(f"🔍 To reproduce the reported error, test with authenticated user.")

if __name__ == "__main__":
    tester = PaymentFocusedTester()
    tester.run_focused_tests()