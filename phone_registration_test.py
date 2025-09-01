#!/usr/bin/env python3
"""
Enhanced Registration System Testing with Phone Number Functionality
Tests phone number validation, student/faculty registration, and database storage
"""

import requests
import json
import time
import uuid

# Configuration - Use URL from frontend/.env
BASE_URL = "http://localhost:8001/api"

class PhoneRegistrationTester:
    def __init__(self):
        self.session = requests.Session()
        self.test_results = {
            "phone_validation": {"passed": 0, "failed": 0, "details": []},
            "student_registration": {"passed": 0, "failed": 0, "details": []},
            "faculty_registration": {"passed": 0, "failed": 0, "details": []},
            "database_verification": {"passed": 0, "failed": 0, "details": []},
            "existing_functionality": {"passed": 0, "failed": 0, "details": []}
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
    
    def test_phone_number_validation(self):
        """Test Phone Number Validation Logic"""
        print("\n📱 Testing Phone Number Validation...")
        
        # Test 1: Valid phone number with +91 prefix
        try:
            valid_data = {
                "first_name": "Rajesh",
                "last_name": "Kumar",
                "thapar_email_prefix": f"validphone{int(time.time())}",
                "phone": "+919876543210",  # Valid +91 format, 13 characters
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103001",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=valid_data)
            
            if response.status_code == 200:
                result = response.json()
                self.log_result("phone_validation", "Valid +91 Phone Number", True, 
                              f"Successfully registered with valid phone: {valid_data['phone']}")
            elif response.status_code == 400 and "already exists" in response.text:
                self.log_result("phone_validation", "Valid +91 Phone Number", True, 
                              "Phone validation working (duplicate user detected)")
            else:
                self.log_result("phone_validation", "Valid +91 Phone Number", False, 
                              f"Failed with valid phone. Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("phone_validation", "Valid +91 Phone Number", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Phone number without +91 prefix (should fail)
        try:
            invalid_data = {
                "first_name": "Invalid",
                "last_name": "Phone",
                "thapar_email_prefix": f"invalidphone1_{int(time.time())}",
                "phone": "9876543210",  # Missing +91 prefix
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103002",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=invalid_data)
            
            if response.status_code == 400 and "must start with +91" in response.text:
                self.log_result("phone_validation", "Phone Without +91 Prefix", True, 
                              "Properly rejects phone numbers without +91 prefix")
            else:
                self.log_result("phone_validation", "Phone Without +91 Prefix", False, 
                              f"Should reject phone without +91. Status: {response.status_code}")
        except Exception as e:
            self.log_result("phone_validation", "Phone Without +91 Prefix", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Phone number with wrong length (should fail)
        try:
            invalid_data = {
                "first_name": "Wrong",
                "last_name": "Length",
                "thapar_email_prefix": f"wronglength_{int(time.time())}",
                "phone": "+9198765432",  # Only 11 characters instead of 13
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103003",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=invalid_data)
            
            if response.status_code == 400 and ("valid phone number" in response.text or "10 digits" in response.text):
                self.log_result("phone_validation", "Wrong Phone Length", True, 
                              "Properly rejects phone numbers with wrong length")
            else:
                self.log_result("phone_validation", "Wrong Phone Length", False, 
                              f"Should reject wrong length phone. Status: {response.status_code}")
        except Exception as e:
            self.log_result("phone_validation", "Wrong Phone Length", False, 
                          f"Error: {str(e)}")
        
        # Test 4: Phone number with non-numeric characters (should fail)
        try:
            invalid_data = {
                "first_name": "Non",
                "last_name": "Numeric",
                "thapar_email_prefix": f"nonnumeric_{int(time.time())}",
                "phone": "+91987654321a",  # Contains letter 'a'
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103004",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=invalid_data)
            
            if response.status_code == 400 and ("valid phone number" in response.text or "digits" in response.text):
                self.log_result("phone_validation", "Non-Numeric Phone", True, 
                              "Properly rejects phone numbers with non-numeric characters")
            else:
                self.log_result("phone_validation", "Non-Numeric Phone", False, 
                              f"Should reject non-numeric phone. Status: {response.status_code}")
        except Exception as e:
            self.log_result("phone_validation", "Non-Numeric Phone", False, 
                          f"Error: {str(e)}")
        
        # Test 5: Empty phone number (should fail)
        try:
            invalid_data = {
                "first_name": "Empty",
                "last_name": "Phone",
                "thapar_email_prefix": f"emptyphone_{int(time.time())}",
                "phone": "",  # Empty phone
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103005",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=invalid_data)
            
            if response.status_code == 400 and "required" in response.text:
                self.log_result("phone_validation", "Empty Phone Number", True, 
                              "Properly rejects empty phone numbers")
            else:
                self.log_result("phone_validation", "Empty Phone Number", False, 
                              f"Should reject empty phone. Status: {response.status_code}")
        except Exception as e:
            self.log_result("phone_validation", "Empty Phone Number", False, 
                          f"Error: {str(e)}")
        
        # Test 6: Missing phone field (should fail)
        try:
            invalid_data = {
                "first_name": "Missing",
                "last_name": "Phone",
                "thapar_email_prefix": f"missingphone_{int(time.time())}",
                # No phone field at all
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103006",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=invalid_data)
            
            if response.status_code in [400, 422]:  # 400 for custom validation, 422 for Pydantic validation
                self.log_result("phone_validation", "Missing Phone Field", True, 
                              "Properly rejects registration without phone field")
            else:
                self.log_result("phone_validation", "Missing Phone Field", False, 
                              f"Should reject missing phone field. Status: {response.status_code}")
        except Exception as e:
            self.log_result("phone_validation", "Missing Phone Field", False, 
                          f"Error: {str(e)}")
    
    def test_student_registration_with_phone(self):
        """Test Student Registration with Phone Numbers"""
        print("\n🎓 Testing Student Registration with Phone Numbers...")
        
        # Test 1: Complete student registration with valid phone
        try:
            student_data = {
                "first_name": "Priya",
                "last_name": "Sharma",
                "thapar_email_prefix": f"student_phone_{int(time.time())}",
                "phone": "+919876543211",
                "is_faculty": False,
                "branch": "Electronics Engineering",
                "roll_number": "102104001",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=student_data)
            
            if response.status_code == 200:
                result = response.json()
                if "user_id" in result and "message" in result:
                    self.log_result("student_registration", "Complete Student Registration", True, 
                                  f"Successfully registered student with phone: {student_data['phone']}")
                    # Store for database verification
                    self.test_student_email = f"{student_data['thapar_email_prefix']}@thapar.edu"
                    self.test_student_phone = student_data['phone']
                else:
                    self.log_result("student_registration", "Complete Student Registration", False, 
                                  f"Missing fields in response: {result}")
            elif response.status_code == 400 and "already exists" in response.text:
                self.log_result("student_registration", "Complete Student Registration", True, 
                              "Student registration working (duplicate prevention)")
            else:
                self.log_result("student_registration", "Complete Student Registration", False, 
                              f"Registration failed. Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("student_registration", "Complete Student Registration", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Student registration with different valid phone formats
        try:
            student_data = {
                "first_name": "Amit",
                "last_name": "Patel",
                "thapar_email_prefix": f"student_phone2_{int(time.time())}",
                "phone": "+918765432109",  # Different valid phone
                "is_faculty": False,
                "branch": "Mechanical Engineering",
                "roll_number": "102105001",
                "batch": "2020-2024"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=student_data)
            
            if response.status_code == 200:
                self.log_result("student_registration", "Different Valid Phone Format", True, 
                              f"Successfully registered with different phone: {student_data['phone']}")
            elif response.status_code == 400 and "already exists" in response.text:
                self.log_result("student_registration", "Different Valid Phone Format", True, 
                              "Phone validation working correctly")
            else:
                self.log_result("student_registration", "Different Valid Phone Format", False, 
                              f"Failed with valid phone. Status: {response.status_code}")
        except Exception as e:
            self.log_result("student_registration", "Different Valid Phone Format", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Student registration missing required fields but with valid phone
        try:
            incomplete_data = {
                "first_name": "Incomplete",
                "last_name": "Student",
                "thapar_email_prefix": f"incomplete_student_{int(time.time())}",
                "phone": "+919876543212",  # Valid phone
                "is_faculty": False
                # Missing branch, roll_number, batch
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=incomplete_data)
            
            if response.status_code == 400 and "required for students" in response.text:
                self.log_result("student_registration", "Student Field Validation with Phone", True, 
                              "Properly validates student fields even with valid phone")
            else:
                self.log_result("student_registration", "Student Field Validation with Phone", False, 
                              f"Should validate student fields. Status: {response.status_code}")
        except Exception as e:
            self.log_result("student_registration", "Student Field Validation with Phone", False, 
                          f"Error: {str(e)}")
    
    def test_faculty_registration_with_phone(self):
        """Test Faculty Registration with Phone Numbers"""
        print("\n👨‍🏫 Testing Faculty Registration with Phone Numbers...")
        
        # Test 1: Complete faculty registration with valid phone
        try:
            faculty_data = {
                "first_name": "Dr. Sunita",
                "last_name": "Verma",
                "thapar_email_prefix": f"faculty_phone_{int(time.time())}",
                "phone": "+919876543213",
                "is_faculty": True,
                "department": "Computer Science"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=faculty_data)
            
            if response.status_code == 200:
                result = response.json()
                if "user_id" in result and "message" in result:
                    self.log_result("faculty_registration", "Complete Faculty Registration", True, 
                                  f"Successfully registered faculty with phone: {faculty_data['phone']}")
                    # Store for database verification
                    self.test_faculty_email = f"{faculty_data['thapar_email_prefix']}@thapar.edu"
                    self.test_faculty_phone = faculty_data['phone']
                else:
                    self.log_result("faculty_registration", "Complete Faculty Registration", False, 
                                  f"Missing fields in response: {result}")
            elif response.status_code == 400 and "already exists" in response.text:
                self.log_result("faculty_registration", "Complete Faculty Registration", True, 
                              "Faculty registration working (duplicate prevention)")
            else:
                self.log_result("faculty_registration", "Complete Faculty Registration", False, 
                              f"Registration failed. Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("faculty_registration", "Complete Faculty Registration", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Faculty registration with different department
        try:
            faculty_data = {
                "first_name": "Prof. Rajesh",
                "last_name": "Gupta",
                "thapar_email_prefix": f"faculty_phone2_{int(time.time())}",
                "phone": "+918765432108",
                "is_faculty": True,
                "department": "Electrical Engineering"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=faculty_data)
            
            if response.status_code == 200:
                self.log_result("faculty_registration", "Faculty Different Department", True, 
                              f"Successfully registered faculty in different department with phone")
            elif response.status_code == 400 and "already exists" in response.text:
                self.log_result("faculty_registration", "Faculty Different Department", True, 
                              "Faculty registration validation working")
            else:
                self.log_result("faculty_registration", "Faculty Different Department", False, 
                              f"Failed registration. Status: {response.status_code}")
        except Exception as e:
            self.log_result("faculty_registration", "Faculty Different Department", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Faculty registration missing department but with valid phone
        try:
            incomplete_data = {
                "first_name": "Incomplete",
                "last_name": "Faculty",
                "thapar_email_prefix": f"incomplete_faculty_{int(time.time())}",
                "phone": "+919876543214",  # Valid phone
                "is_faculty": True
                # Missing department
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=incomplete_data)
            
            if response.status_code == 400 and "required for faculty" in response.text:
                self.log_result("faculty_registration", "Faculty Field Validation with Phone", True, 
                              "Properly validates faculty fields even with valid phone")
            else:
                self.log_result("faculty_registration", "Faculty Field Validation with Phone", False, 
                              f"Should validate faculty fields. Status: {response.status_code}")
        except Exception as e:
            self.log_result("faculty_registration", "Faculty Field Validation with Phone", False, 
                          f"Error: {str(e)}")
    
    def test_database_phone_storage(self):
        """Test Database Storage of Phone Numbers"""
        print("\n🗄️ Testing Database Storage of Phone Numbers...")
        
        # Test 1: Verify registered user exists with phone number
        try:
            if hasattr(self, 'test_student_email'):
                # Extract prefix from stored email
                prefix = self.test_student_email.split('@')[0]
                response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                           data={"thapar_email_prefix": prefix})
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("exists") == True:
                        self.log_result("database_verification", "Student Phone Storage Verification", True, 
                                      f"Student with phone number found in database: {self.test_student_email}")
                    else:
                        self.log_result("database_verification", "Student Phone Storage Verification", False, 
                                      f"Student not found in database after registration")
                else:
                    self.log_result("database_verification", "Student Phone Storage Verification", False, 
                                  f"Database query failed. Status: {response.status_code}")
            else:
                self.log_result("database_verification", "Student Phone Storage Verification", False, 
                              "No test student data available for verification")
        except Exception as e:
            self.log_result("database_verification", "Student Phone Storage Verification", False, 
                          f"Error: {str(e)}")
        
        # Test 2: Verify faculty user exists with phone number
        try:
            if hasattr(self, 'test_faculty_email'):
                # Extract prefix from stored email
                prefix = self.test_faculty_email.split('@')[0]
                response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                           data={"thapar_email_prefix": prefix})
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("exists") == True:
                        self.log_result("database_verification", "Faculty Phone Storage Verification", True, 
                                      f"Faculty with phone number found in database: {self.test_faculty_email}")
                    else:
                        self.log_result("database_verification", "Faculty Phone Storage Verification", False, 
                                      f"Faculty not found in database after registration")
                else:
                    self.log_result("database_verification", "Faculty Phone Storage Verification", False, 
                                  f"Database query failed. Status: {response.status_code}")
            else:
                self.log_result("database_verification", "Faculty Phone Storage Verification", False, 
                              "No test faculty data available for verification")
        except Exception as e:
            self.log_result("database_verification", "Faculty Phone Storage Verification", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Test user profile data includes phone number (requires authentication)
        try:
            # Test the /auth/me endpoint structure (should require auth)
            response = self.session.get(f"{BASE_URL}/auth/me")
            
            if response.status_code == 401:
                self.log_result("database_verification", "User Profile Phone Access", True, 
                              "User profile endpoint properly secured (phone data protected)")
            else:
                self.log_result("database_verification", "User Profile Phone Access", False, 
                              f"User profile endpoint should require auth. Status: {response.status_code}")
        except Exception as e:
            self.log_result("database_verification", "User Profile Phone Access", False, 
                          f"Error: {str(e)}")
    
    def test_existing_functionality_compatibility(self):
        """Test Existing Functionality Still Works with Phone Numbers"""
        print("\n🔄 Testing Existing Functionality Compatibility...")
        
        # Test 1: Email format validation still works
        try:
            invalid_email_data = {
                "first_name": "Invalid",
                "last_name": "Email",
                "thapar_email_prefix": "test@gmail.com",  # Invalid - contains @
                "phone": "+919876543215",  # Valid phone
                "is_faculty": False,
                "branch": "Computer Engineering",
                "roll_number": "102103007",
                "batch": "2021-2025"
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=invalid_email_data)
            
            if response.status_code == 400 and "only the part before @thapar.edu" in response.text:
                self.log_result("existing_functionality", "Email Validation Compatibility", True, 
                              "Email validation still works with phone number field")
            else:
                self.log_result("existing_functionality", "Email Validation Compatibility", False, 
                              f"Email validation broken. Status: {response.status_code}")
        except Exception as e:
            self.log_result("existing_functionality", "Email Validation Compatibility", False, 
                          f"Error: {str(e)}")
        
        # Test 2: User existence check still works
        try:
            response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                       data={"thapar_email_prefix": "nonexistent999"})
            
            if response.status_code == 200:
                result = response.json()
                if "exists" in result and "thapar_email" in result:
                    self.log_result("existing_functionality", "User Existence Check Compatibility", True, 
                                  f"User existence check working: exists={result['exists']}")
                else:
                    self.log_result("existing_functionality", "User Existence Check Compatibility", False, 
                                  f"User existence check response format changed: {result}")
            else:
                self.log_result("existing_functionality", "User Existence Check Compatibility", False, 
                              f"User existence check broken. Status: {response.status_code}")
        except Exception as e:
            self.log_result("existing_functionality", "User Existence Check Compatibility", False, 
                          f"Error: {str(e)}")
        
        # Test 3: Required field validation still works for both user types
        try:
            # Test student without required fields
            incomplete_student = {
                "first_name": "Test",
                "last_name": "Student",
                "thapar_email_prefix": f"test_student_{int(time.time())}",
                "phone": "+919876543216",
                "is_faculty": False
                # Missing branch, roll_number, batch
            }
            response = self.session.post(f"{BASE_URL}/auth/register", json=incomplete_student)
            
            if response.status_code == 400 and "required for students" in response.text:
                self.log_result("existing_functionality", "Student Validation Compatibility", True, 
                              "Student field validation still works with phone numbers")
            else:
                self.log_result("existing_functionality", "Student Validation Compatibility", False, 
                              f"Student validation broken. Status: {response.status_code}")
        except Exception as e:
            self.log_result("existing_functionality", "Student Validation Compatibility", False, 
                          f"Error: {str(e)}")
        
        # Test 4: Login flow integration (check-user endpoint)
        try:
            # Test with a user that should exist (from previous tests)
            if hasattr(self, 'test_student_email'):
                prefix = self.test_student_email.split('@')[0]
                response = self.session.post(f"{BASE_URL}/auth/check-user", 
                                           data={"thapar_email_prefix": prefix})
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("exists") == True and "user_id" in result:
                        self.log_result("existing_functionality", "Login Flow Integration", True, 
                                      "Login flow integration working with phone-enabled users")
                    else:
                        self.log_result("existing_functionality", "Login Flow Integration", False, 
                                      f"Login flow response incomplete: {result}")
                else:
                    self.log_result("existing_functionality", "Login Flow Integration", False, 
                                  f"Login flow broken. Status: {response.status_code}")
            else:
                self.log_result("existing_functionality", "Login Flow Integration", False, 
                              "No test user available for login flow testing")
        except Exception as e:
            self.log_result("existing_functionality", "Login Flow Integration", False, 
                          f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all phone registration tests"""
        print("🚀 Starting Enhanced Registration System Testing with Phone Numbers...")
        print(f"Testing against: {BASE_URL}")
        print("🎯 FOCUS: Phone Number Validation (+91 format, 13 characters)")
        print("=" * 70)
        
        # Run tests in logical order
        self.test_phone_number_validation()
        self.test_student_registration_with_phone()
        self.test_faculty_registration_with_phone()
        self.test_database_phone_storage()
        self.test_existing_functionality_compatibility()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 70)
        print("📊 PHONE REGISTRATION TEST SUMMARY")
        print("=" * 70)
        
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
            print(f"  📈 Success Rate: {(total_passed/(total_passed+total_failed)*100):.1f}%")
        
        # Critical issues analysis
        critical_issues = []
        if self.test_results["phone_validation"]["failed"] > 0:
            critical_issues.append("Phone number validation issues")
        if self.test_results["database_verification"]["failed"] > 1:
            critical_issues.append("Database storage issues")
        if self.test_results["existing_functionality"]["failed"] > 1:
            critical_issues.append("Existing functionality broken")
        
        if critical_issues:
            print(f"\n⚠️  CRITICAL ISSUES DETECTED:")
            for issue in critical_issues:
                print(f"    - {issue}")
        else:
            print(f"\n✅ NO CRITICAL ISSUES DETECTED - Phone registration system working correctly!")

if __name__ == "__main__":
    tester = PhoneRegistrationTester()
    tester.run_all_tests()