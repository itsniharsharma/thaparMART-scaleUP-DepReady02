#!/usr/bin/env python3
"""
Login Validation System Testing for thaparMART
Focused testing of user existence check API and registration system
"""

import requests
import json

# Configuration - Use production URL from frontend/.env
BASE_URL = "https://access-restore-10.preview.emergentagent.com/api"

class LoginValidationTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = []
    
    def log_result(self, test_name, passed, details=""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        result = f"{status}: {test_name} - {details}"
        self.test_results.append(result)
        print(result)
    
    def test_user_existence_check_api(self):
        """Test User Existence Check API with specific test cases"""
        print("\n🔍 Testing User Existence Check API...")
        
        # Test 1: Check existing user nsharma3_be23 (should return exists: true)
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "nsharma3_be23"})
            
            if response.status_code == 200:
                result = response.json()
                if result.get("exists") == True and "thapar_email" in result:
                    self.log_result("Existing User Check - nsharma3_be23", True, 
                                  f"User exists: {result['thapar_email']}")
                else:
                    self.log_result("Existing User Check - nsharma3_be23", False, 
                                  f"User should exist but got: {result}")
            else:
                self.log_result("Existing User Check - nsharma3_be23", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Existing User Check - nsharma3_be23", False, f"Error: {str(e)}")
        
        # Test 2: Check non-existing user randomuser999 (should return exists: false)
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "randomuser999"})
            
            if response.status_code == 200:
                result = response.json()
                if result.get("exists") == False and "thapar_email" in result:
                    self.log_result("Non-existing User Check - randomuser999", True, 
                                  f"Correctly identified non-existing user: {result['thapar_email']}")
                else:
                    self.log_result("Non-existing User Check - randomuser999", False, 
                                  f"Should not exist but got: {result}")
            else:
                self.log_result("Non-existing User Check - randomuser999", False, 
                              f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Non-existing User Check - randomuser999", False, f"Error: {str(e)}")
        
        # Test 3: Test with empty email prefix (should return validation error)
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": ""})
            
            if response.status_code == 400 and "only the part before @thapar.edu" in response.text:
                self.log_result("Empty Email Prefix Validation", True, 
                              "Properly rejects empty email prefix")
            else:
                self.log_result("Empty Email Prefix Validation", False, 
                              f"Should reject empty prefix. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Empty Email Prefix Validation", False, f"Error: {str(e)}")
        
        # Test 4: Test with email containing @ symbol (should return validation error)
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "test@gmail.com"})
            
            if response.status_code == 400 and "only the part before @thapar.edu" in response.text:
                self.log_result("Email @ Symbol Validation", True, 
                              "Properly rejects email with @ symbol")
            else:
                self.log_result("Email @ Symbol Validation", False, 
                              f"Should reject @ symbol. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Email @ Symbol Validation", False, f"Error: {str(e)}")
    
    def test_registration_system(self):
        """Test Registration System"""
        print("\n📝 Testing Registration System...")
        
        # Test 1: Register a test user to verify registration works
        try:
            test_user_data = {
                "first_name": "Test",
                "last_name": "Student",
                "thapar_email_prefix": f"testuser{int(__import__('time').time())}",
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103999",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=test_user_data)
            
            if response.status_code == 200:
                result = response.json()
                if "user_id" in result and "message" in result:
                    # Now verify this user can be found via check-user API
                    check_response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                                     data={"thapar_email_prefix": test_user_data["thapar_email_prefix"]})
                    
                    if check_response.status_code == 200 and check_response.json().get("exists"):
                        self.log_result("Registration Integration Test", True, 
                                      "User registered and immediately findable via check-user API")
                    else:
                        self.log_result("Registration Integration Test", False, 
                                      "User registered but not found via check-user API")
                else:
                    self.log_result("Registration Integration Test", False, 
                                  f"Registration response missing fields: {result}")
            elif response.status_code == 400 and "already exists" in response.text:
                self.log_result("Registration Integration Test", True, 
                              "Registration properly prevents duplicates")
            else:
                self.log_result("Registration Integration Test", False, 
                              f"Registration failed. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Registration Integration Test", False, f"Error: {str(e)}")
        
        # Test 2: Test faculty registration
        try:
            faculty_data = {
                "first_name": "Test",
                "last_name": "Faculty",
                "thapar_email_prefix": f"testfaculty{int(__import__('time').time())}",
                "is_faculty": True,
                "department": "Computer Science"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=faculty_data)
            
            if response.status_code == 200:
                result = response.json()
                if "user_id" in result:
                    self.log_result("Faculty Registration Test", True, 
                                  "Faculty registration successful")
                else:
                    self.log_result("Faculty Registration Test", False, 
                                  f"Faculty registration response invalid: {result}")
            elif response.status_code == 400 and "already exists" in response.text:
                self.log_result("Faculty Registration Test", True, 
                              "Faculty registration properly prevents duplicates")
            else:
                self.log_result("Faculty Registration Test", False, 
                              f"Faculty registration failed. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Faculty Registration Test", False, f"Error: {str(e)}")
    
    def test_login_flow_integration(self):
        """Test Integration - Login Flow"""
        print("\n🔐 Testing Login Flow Integration...")
        
        # Test 1: Existing user should be allowed to proceed
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "nsharma3_be23"})
            
            if response.status_code == 200:
                result = response.json()
                if result.get("exists") == True:
                    self.log_result("Login Flow - Existing User", True, 
                                  "Existing user can proceed to Emergent auth")
                else:
                    self.log_result("Login Flow - Existing User", False, 
                                  "Existing user should be allowed to proceed")
            else:
                self.log_result("Login Flow - Existing User", False, 
                              f"Login check failed. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Login Flow - Existing User", False, f"Error: {str(e)}")
        
        # Test 2: Non-existing user should get "register first" message
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "randomuser999"})
            
            if response.status_code == 200:
                result = response.json()
                if result.get("exists") == False:
                    self.log_result("Login Flow - Non-existing User", True, 
                                  "Non-existing user gets register first message")
                else:
                    self.log_result("Login Flow - Non-existing User", False, 
                                  "Non-existing user should be prompted to register")
            else:
                self.log_result("Login Flow - Non-existing User", False, 
                              f"Login check failed. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Login Flow - Non-existing User", False, f"Error: {str(e)}")
        
        # Test 3: Invalid email formats should be rejected
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "invalid@format.com"})
            
            if response.status_code == 400:
                self.log_result("Login Flow - Invalid Email Format", True, 
                              "Invalid email formats properly rejected")
            else:
                self.log_result("Login Flow - Invalid Email Format", False, 
                              f"Should reject invalid format. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Login Flow - Invalid Email Format", False, f"Error: {str(e)}")
    
    def test_database_verification(self):
        """Test Database Verification"""
        print("\n🗄️ Testing Database Verification...")
        
        # Test 1: Verify registered users are stored in thaparMARTN database
        try:
            # Register a user and verify it's stored
            unique_prefix = f"dbtest{int(__import__('time').time())}"
            user_data = {
                "first_name": "Database",
                "last_name": "Test",
                "thapar_email_prefix": unique_prefix,
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103888",
                "batch": "2021-2025"
            }
            
            # Register user
            reg_response = self.session.post(f"{BASE_URL}/auth/register", json=user_data)
            
            if reg_response.status_code == 200:
                # Verify user exists in database
                check_response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                                 data={"thapar_email_prefix": unique_prefix})
                
                if check_response.status_code == 200 and check_response.json().get("exists"):
                    self.log_result("Database Storage Verification", True, 
                                  "User data correctly stored and retrievable from thaparMARTN database")
                else:
                    self.log_result("Database Storage Verification", False, 
                                  "User not found after registration - database storage issue")
            else:
                self.log_result("Database Storage Verification", False, 
                              f"Registration failed, cannot test database. Status: {reg_response.status_code}")
        except Exception as e:
            self.log_result("Database Storage Verification", False, f"Error: {str(e)}")
        
        # Test 2: Verify user data format matches requirements
        try:
            # Check if we can retrieve user data with all required fields
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "nsharma3_be23"})
            
            if response.status_code == 200:
                result = response.json()
                required_fields = ["exists", "thapar_email", "user_id"]
                
                if all(field in result for field in required_fields):
                    self.log_result("Database Format Verification", True, 
                                  "User data format matches requirements with all fields")
                else:
                    missing_fields = [field for field in required_fields if field not in result]
                    self.log_result("Database Format Verification", False, 
                                  f"Missing required fields: {missing_fields}")
            else:
                self.log_result("Database Format Verification", False, 
                              f"Cannot verify format. Status: {response.status_code}")
        except Exception as e:
            self.log_result("Database Format Verification", False, f"Error: {str(e)}")
    
    def run_login_validation_tests(self):
        """Run all login validation tests"""
        print("🚀 Starting Login Validation System Testing...")
        print(f"Testing against: {BASE_URL}")
        print("=" * 60)
        
        # Run focused tests as requested
        self.test_user_existence_check_api()
        self.test_registration_system()
        self.test_login_flow_integration()
        self.test_database_verification()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 LOGIN VALIDATION TEST SUMMARY")
        print("=" * 60)
        
        passed_count = sum(1 for result in self.test_results if "✅ PASS" in result)
        failed_count = sum(1 for result in self.test_results if "❌ FAIL" in result)
        
        for result in self.test_results:
            print(result)
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"  ✅ Total Passed: {passed_count}")
        print(f"  ❌ Total Failed: {failed_count}")
        
        if failed_count == 0:
            print(f"\n✅ ALL LOGIN VALIDATION TESTS PASSED")
        else:
            print(f"\n⚠️  {failed_count} LOGIN VALIDATION ISSUES DETECTED")

if __name__ == "__main__":
    tester = LoginValidationTester()
    tester.run_login_validation_tests()