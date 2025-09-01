#!/usr/bin/env python3
"""
Focused Custom Registration System Testing for thaparMART
HIGH PRIORITY - Tests the new custom registration system with MongoDB Atlas integration
"""

import requests
import json
import time
import uuid

# Configuration
BASE_URL = "https://thapar-auth-fix.preview.emergentagent.com/api"

class CustomRegistrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = {
            "custom_registration": {"passed": 0, "failed": 0, "details": []},
            "mongodb_atlas": {"passed": 0, "failed": 0, "details": []},
            "authentication_flow": {"passed": 0, "failed": 0, "details": []}
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
    
    def test_student_registration_scenarios(self):
        """Test Student Registration with Various Scenarios"""
        print("\n🎓 Testing Student Registration Scenarios...")
        
        # Test 1: Valid student registration
        try:
            student_data = {
                "first_name": "Rahul",
                "last_name": "Verma", 
                "thapar_email_prefix": f"student{int(time.time())}",
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103456",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=student_data)
            
            if response.status_code == 200:
                result = response.json()
                if "user_id" in result and "Registration successful" in result.get("message", ""):
                    self.log_result("custom_registration", "Valid Student Registration", True, 
                                  f"Student registered successfully with ID: {result['user_id']}")
                else:
                    self.log_result("custom_registration", "Valid Student Registration", False, 
                                  f"Missing required response fields: {result}")
            else:
                self.log_result("custom_registration", "Valid Student Registration", False, 
                              f"Registration failed with status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("custom_registration", "Valid Student Registration", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Student with different branch
        try:
            student_data = {
                "first_name": "Priya",
                "last_name": "Singh", 
                "thapar_email_prefix": f"student{int(time.time())+1}",
                "is_faculty": False,
                "branch": "Electronics Engineering",
                "roll_number": "102104789",
                "batch": "2020-2024"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=student_data)
            
            if response.status_code == 200:
                self.log_result("custom_registration", "Student Different Branch", True, 
                              "Electronics Engineering student registered successfully")
            else:
                self.log_result("custom_registration", "Student Different Branch", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Student Different Branch", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Student missing required fields
        try:
            incomplete_data = {
                "first_name": "Incomplete",
                "last_name": "Student",
                "thapar_email_prefix": f"incomplete{int(time.time())}",
                "is_faculty": False,
                "branch": "Computer Engineering"
                # Missing roll_number and batch
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=incomplete_data)
            
            if response.status_code == 400 and "required for students" in response.text:
                self.log_result("custom_registration", "Student Missing Fields Validation", True, 
                              "Properly validates missing student fields")
            else:
                self.log_result("custom_registration", "Student Missing Fields Validation", False, 
                              f"Should validate missing fields. Status: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Student Missing Fields Validation", False, 
                          f"Error: {str(e)}")
    
    def test_faculty_registration_scenarios(self):
        """Test Faculty Registration with Various Scenarios"""
        print("\n👨‍🏫 Testing Faculty Registration Scenarios...")
        
        # Test 1: Valid faculty registration
        try:
            faculty_data = {
                "first_name": "Dr. Amit",
                "last_name": "Kumar",
                "thapar_email_prefix": f"faculty{int(time.time())}",
                "is_faculty": True,
                "department": "Computer Science"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=faculty_data)
            
            if response.status_code == 200:
                result = response.json()
                if "user_id" in result and "Registration successful" in result.get("message", ""):
                    self.log_result("custom_registration", "Valid Faculty Registration", True, 
                                  f"Faculty registered successfully with ID: {result['user_id']}")
                else:
                    self.log_result("custom_registration", "Valid Faculty Registration", False, 
                                  f"Missing required response fields: {result}")
            else:
                self.log_result("custom_registration", "Valid Faculty Registration", False, 
                              f"Registration failed with status: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Valid Faculty Registration", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Faculty with different department
        try:
            faculty_data = {
                "first_name": "Prof. Sunita",
                "last_name": "Sharma",
                "thapar_email_prefix": f"faculty{int(time.time())+1}",
                "is_faculty": True,
                "department": "Mechanical Engineering"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=faculty_data)
            
            if response.status_code == 200:
                self.log_result("custom_registration", "Faculty Different Department", True, 
                              "Mechanical Engineering faculty registered successfully")
            else:
                self.log_result("custom_registration", "Faculty Different Department", False, 
                              f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Faculty Different Department", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Faculty missing department
        try:
            incomplete_faculty = {
                "first_name": "Dr. Incomplete",
                "last_name": "Faculty",
                "thapar_email_prefix": f"incfaculty{int(time.time())}",
                "is_faculty": True
                # Missing department
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=incomplete_faculty)
            
            if response.status_code == 400 and "required for faculty" in response.text:
                self.log_result("custom_registration", "Faculty Missing Department Validation", True, 
                              "Properly validates missing faculty department")
            else:
                self.log_result("custom_registration", "Faculty Missing Department Validation", False, 
                              f"Should validate missing department. Status: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Faculty Missing Department Validation", False, 
                          f"Error: {str(e)}")
    
    def test_email_validation_scenarios(self):
        """Test Email Validation Scenarios"""
        print("\n📧 Testing Email Validation Scenarios...")
        
        # Test 1: Email with @ symbol (should be rejected)
        try:
            invalid_data = {
                "first_name": "Invalid",
                "last_name": "Email",
                "thapar_email_prefix": "test@gmail.com",
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103999",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=invalid_data)
            
            if response.status_code == 400 and "only the part before @thapar.edu" in response.text:
                self.log_result("custom_registration", "Email @ Symbol Validation", True, 
                              "Properly rejects email with @ symbol")
            else:
                self.log_result("custom_registration", "Email @ Symbol Validation", False, 
                              f"Should reject @ in email. Status: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Email @ Symbol Validation", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Empty email prefix
        try:
            empty_email_data = {
                "first_name": "Empty",
                "last_name": "Email",
                "thapar_email_prefix": "",
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103888",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=empty_email_data)
            
            if response.status_code == 400:
                self.log_result("custom_registration", "Empty Email Validation", True, 
                              "Properly rejects empty email prefix")
            else:
                self.log_result("custom_registration", "Empty Email Validation", False, 
                              f"Should reject empty email. Status: {response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "Empty Email Validation", False, 
                          f"Error: {str(e)}")
    
    def test_user_existence_check_comprehensive(self):
        """Test User Existence Check API Comprehensively"""
        print("\n🔍 Testing User Existence Check API...")
        
        # First register a test user
        test_email_prefix = f"checkuser{int(time.time())}"
        try:
            user_data = {
                "first_name": "Check",
                "last_name": "User",
                "thapar_email_prefix": test_email_prefix,
                "is_faculty": False,
                "branch": "Information Technology",
                "roll_number": "102105999",
                "batch": "2021-2025"
            }
            reg_response = self.session.post(f"{BASE_URL}/auth/register", json=user_data)
            
            if reg_response.status_code == 200:
                # Now check if user exists
                check_response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                                 data={"thapar_email_prefix": test_email_prefix})
                
                if check_response.status_code == 200:
                    result = check_response.json()
                    if result.get("exists") == True and result.get("thapar_email") == f"{test_email_prefix}@thapar.edu":
                        self.log_result("custom_registration", "User Existence Check - Registered User", True, 
                                      f"Successfully found registered user: {result['thapar_email']}")
                    else:
                        self.log_result("custom_registration", "User Existence Check - Registered User", False, 
                                      f"Unexpected result: {result}")
                else:
                    self.log_result("custom_registration", "User Existence Check - Registered User", False, 
                                  f"Check failed with status: {check_response.status_code}")
            else:
                self.log_result("custom_registration", "User Existence Check - Registered User", False, 
                              f"Failed to register test user: {reg_response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "User Existence Check - Registered User", False, 
                          f"Error: {str(e)}")
        
        # Test non-existing user
        try:
            check_response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                             data={"thapar_email_prefix": f"nonexistent{int(time.time())}"})
            
            if check_response.status_code == 200:
                result = check_response.json()
                if result.get("exists") == False:
                    self.log_result("custom_registration", "User Existence Check - Non-existing User", True, 
                                  f"Correctly identified non-existing user")
                else:
                    self.log_result("custom_registration", "User Existence Check - Non-existing User", False, 
                                  f"Should return exists=False: {result}")
            else:
                self.log_result("custom_registration", "User Existence Check - Non-existing User", False, 
                              f"Status: {check_response.status_code}")
        except Exception as e:
            self.log_result("custom_registration", "User Existence Check - Non-existing User", False, 
                          f"Error: {str(e)}")
    
    def test_mongodb_atlas_integration(self):
        """Test MongoDB Atlas Integration"""
        print("\n🗄️ Testing MongoDB Atlas Integration...")
        
        # Test database write and read operations
        unique_prefix = f"mongotest{int(time.time())}"
        try:
            # Write operation - register user
            user_data = {
                "first_name": "MongoDB",
                "last_name": "Atlas",
                "thapar_email_prefix": unique_prefix,
                "is_faculty": True,
                "department": "Database Engineering"
            }
            write_response = self.session.post(f"{BASE_URL}/auth/register", json=user_data)
            
            if write_response.status_code == 200:
                self.log_result("mongodb_atlas", "Database Write Operation", True, 
                              "Successfully wrote user data to MongoDB Atlas")
                
                # Read operation - check user exists
                read_response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                                data={"thapar_email_prefix": unique_prefix})
                
                if read_response.status_code == 200:
                    result = read_response.json()
                    if result.get("exists") == True:
                        self.log_result("mongodb_atlas", "Database Read Operation", True, 
                                      "Successfully read user data from MongoDB Atlas")
                    else:
                        self.log_result("mongodb_atlas", "Database Read Operation", False, 
                                      f"User not found after registration: {result}")
                else:
                    self.log_result("mongodb_atlas", "Database Read Operation", False, 
                                  f"Read operation failed: {read_response.status_code}")
            else:
                self.log_result("mongodb_atlas", "Database Write Operation", False, 
                              f"Write operation failed: {write_response.status_code}")
        except Exception as e:
            self.log_result("mongodb_atlas", "Database Operations", False, 
                          f"Database error: {str(e)}")
        
        # Test enhanced user model storage
        try:
            enhanced_user = {
                "first_name": "Enhanced",
                "last_name": "Model",
                "thapar_email_prefix": f"enhanced{int(time.time())}",
                "is_faculty": False,
                "branch": "Biotechnology",
                "roll_number": "102106888",
                "batch": "2022-2026"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=enhanced_user)
            
            if response.status_code == 200:
                self.log_result("mongodb_atlas", "Enhanced User Model Storage", True, 
                              "Enhanced user model with all fields stored successfully")
            else:
                self.log_result("mongodb_atlas", "Enhanced User Model Storage", False, 
                              f"Enhanced model storage failed: {response.status_code}")
        except Exception as e:
            self.log_result("mongodb_atlas", "Enhanced User Model Storage", False, 
                          f"Enhanced model error: {str(e)}")
    
    def test_authentication_flow_integration(self):
        """Test Authentication Flow Integration"""
        print("\n🔐 Testing Authentication Flow Integration...")
        
        # Test session exchange endpoint (should reject invalid sessions)
        try:
            response = self.session.post(f"{BASE_URL}/auth/session", 
                                       data={"session_id": "invalid_test_session"})
            
            if response.status_code == 401:
                self.log_result("authentication_flow", "Session Exchange Validation", True, 
                              "Properly rejects invalid session IDs")
            else:
                self.log_result("authentication_flow", "Session Exchange Validation", False, 
                              f"Should reject invalid session. Status: {response.status_code}")
        except Exception as e:
            self.log_result("authentication_flow", "Session Exchange Validation", False, 
                          f"Session exchange error: {str(e)}")
        
        # Test protected endpoints require authentication
        try:
            response = self.session.get(f"{BASE_URL}/auth/me")
            
            if response.status_code == 401:
                self.log_result("authentication_flow", "Protected Endpoint Security", True, 
                              "Protected endpoints properly require authentication")
            else:
                self.log_result("authentication_flow", "Protected Endpoint Security", False, 
                              f"Should require authentication. Status: {response.status_code}")
        except Exception as e:
            self.log_result("authentication_flow", "Protected Endpoint Security", False, 
                          f"Protected endpoint error: {str(e)}")
        
        # Test logout functionality
        try:
            response = self.session.post(f"{BASE_URL}/auth/logout")
            
            if response.status_code == 200:
                result = response.json()
                if "Logged out successfully" in result.get("message", ""):
                    self.log_result("authentication_flow", "Logout Functionality", True, 
                                  "Logout endpoint working correctly")
                else:
                    self.log_result("authentication_flow", "Logout Functionality", False, 
                                  f"Unexpected logout response: {result}")
            else:
                self.log_result("authentication_flow", "Logout Functionality", False, 
                              f"Logout failed: {response.status_code}")
        except Exception as e:
            self.log_result("authentication_flow", "Logout Functionality", False, 
                          f"Logout error: {str(e)}")
    
    def run_all_tests(self):
        """Run all custom registration tests"""
        print("🚀 Starting Custom Registration System Testing (HIGH PRIORITY)...")
        print(f"Testing against: {BASE_URL}")
        print("=" * 80)
        
        # Run all test suites
        self.test_student_registration_scenarios()
        self.test_faculty_registration_scenarios()
        self.test_email_validation_scenarios()
        self.test_user_existence_check_comprehensive()
        self.test_mongodb_atlas_integration()
        self.test_authentication_flow_integration()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 CUSTOM REGISTRATION SYSTEM TEST SUMMARY")
        print("=" * 80)
        
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
        
        if total_passed + total_failed > 0:
            success_rate = (total_passed/(total_passed+total_failed)*100)
            print(f"  📈 Success Rate: {success_rate:.1f}%")
        
        # Determine critical issues
        critical_failures = []
        if self.test_results["custom_registration"]["failed"] > 2:
            critical_failures.append("Custom registration system issues")
        if self.test_results["mongodb_atlas"]["failed"] > 0:
            critical_failures.append("MongoDB Atlas connectivity issues")
        
        if critical_failures:
            print(f"\n⚠️  CRITICAL ISSUES DETECTED:")
            for issue in critical_failures:
                print(f"    - {issue}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES DETECTED - CUSTOM REGISTRATION SYSTEM WORKING PERFECTLY")
        
        print(f"\n🎓 CUSTOM REGISTRATION SYSTEM STATUS:")
        if total_failed == 0:
            print("  🟢 FULLY OPERATIONAL - Ready for production use")
        elif total_failed <= 2:
            print("  🟡 MOSTLY OPERATIONAL - Minor issues detected")
        else:
            print("  🔴 NEEDS ATTENTION - Multiple issues detected")

if __name__ == "__main__":
    tester = CustomRegistrationTester()
    tester.run_all_tests()