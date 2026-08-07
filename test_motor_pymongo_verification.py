#!/usr/bin/env python3
"""
Motor/PyMongo Backend Verification Test Suite
Verifies that changing backend to motor/pymongo works properly without syntax or 500 errors
"""

import requests
import json
import sys
from datetime import datetime
import time

# Backend URL from frontend/.env
BASE_URL = "https://render-ready-4.preview.emergentagent.com/api"

# Admin credentials from backend/.env
ADMIN_USERNAME = "SHORIEN"
ADMIN_PASSWORD = "Xiron696@"

class MotorPyMongoTestRunner:
    def __init__(self):
        self.access_token = None
        self.test_user_id = None
        self.test_proxy_id = None
        self.test_redeem_code = None
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
    def assert_equal(self, actual, expected, test_name):
        if actual == expected:
            self.passed += 1
            self.log(f"✅ PASS: {test_name}", "PASS")
            return True
        else:
            self.failed += 1
            error_msg = f"❌ FAIL: {test_name} - Expected: {expected}, Got: {actual}"
            self.log(error_msg, "FAIL")
            self.errors.append(error_msg)
            return False
            
    def assert_not_equal(self, actual, expected, test_name):
        if actual != expected:
            self.passed += 1
            self.log(f"✅ PASS: {test_name}", "PASS")
            return True
        else:
            self.failed += 1
            error_msg = f"❌ FAIL: {test_name} - Should not equal: {expected}, Got: {actual}"
            self.log(error_msg, "FAIL")
            self.errors.append(error_msg)
            return False
            
    def assert_in(self, value, container, test_name):
        if value in container:
            self.passed += 1
            self.log(f"✅ PASS: {test_name}", "PASS")
            return True
        else:
            self.failed += 1
            error_msg = f"❌ FAIL: {test_name} - {value} not in {container}"
            self.log(error_msg, "FAIL")
            self.errors.append(error_msg)
            return False
            
    def assert_not_none(self, value, test_name):
        if value is not None:
            self.passed += 1
            self.log(f"✅ PASS: {test_name}", "PASS")
            return True
        else:
            self.failed += 1
            error_msg = f"❌ FAIL: {test_name} - Value is None"
            self.log(error_msg, "FAIL")
            self.errors.append(error_msg)
            return False
    
    def assert_no_500_error(self, response, test_name):
        """Verify no 500 Internal Server Error"""
        if response.status_code != 500:
            self.passed += 1
            self.log(f"✅ PASS: {test_name} - No 500 error (status: {response.status_code})", "PASS")
            return True
        else:
            self.failed += 1
            error_msg = f"❌ FAIL: {test_name} - Got 500 Internal Server Error: {response.text}"
            self.log(error_msg, "FAIL")
            self.errors.append(error_msg)
            return False
    
    def test_admin_login(self):
        """Test 1: Admin login - verifies Motor async operations work"""
        self.log("=" * 80)
        self.log("TEST 1: Admin Login (Motor Async Read Operation)")
        self.log("=" * 80)
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            # Check for no 500 error
            self.assert_no_500_error(response, "Login endpoint - no 500 error")
            
            if response.status_code == 200:
                data = response.json()
                
                # Check if we got cookies
                if 'access_token' in response.cookies:
                    self.access_token = response.cookies['access_token']
                    self.log(f"Access token received via cookie")
                    self.assert_not_none(self.access_token, "Admin login successful with access token")
                    
                    # Verify user data
                    if 'user' in data:
                        user = data['user']
                        self.assert_equal(user.get('role'), 'admin', "Admin role verification")
                        self.assert_equal(user.get('username'), ADMIN_USERNAME, "Admin username verification")
                    return True
                else:
                    self.log("No access_token cookie received", "ERROR")
                    self.failed += 1
                    return False
            else:
                self.log(f"Login failed with status {response.status_code}: {response.text}", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during admin login: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Admin login exception: {str(e)}")
            return False
    
    def test_create_user(self):
        """Test 2: Create user - verifies Motor async insert operation"""
        self.log("\n" + "=" * 80)
        self.log("TEST 2: Create User (Motor Async Insert Operation)")
        self.log("=" * 80)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
        
        # Generate unique username
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        test_username = f"motor_test_{timestamp}"
        
        try:
            user_data = {
                "username": test_username,
                "password": "MotorTest123!",
                "role": "user",
                "credits": 100,
                "plan": "free"
            }
            
            self.log(f"Creating user: {test_username}")
            
            response = requests.post(
                f"{BASE_URL}/admin/users",
                json=user_data,
                cookies={"access_token": self.access_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            # Check for no 500 error
            self.assert_no_500_error(response, "Create user endpoint - no 500 error")
            
            if response.status_code == 200:
                created_user = response.json()
                self.log(f"Created user: {json.dumps(created_user, indent=2)}")
                
                # Store user ID for later tests
                self.test_user_id = created_user.get('_id')
                
                # Verify ObjectId was converted to string properly
                self.assert_not_none(self.test_user_id, "User ID is present (ObjectId to string conversion)")
                self.assert_equal(isinstance(self.test_user_id, str), True, "User ID is string type (not ObjectId)")
                self.assert_equal(created_user.get('username'), test_username, "User created with correct username")
                
                return True
            else:
                self.log(f"User creation failed: {response.text}", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during user creation: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"User creation exception: {str(e)}")
            return False
    
    def test_update_user(self):
        """Test 3: Update user - verifies Motor async update operation"""
        self.log("\n" + "=" * 80)
        self.log("TEST 3: Update User (Motor Async Update Operation)")
        self.log("=" * 80)
        
        if not self.access_token or not self.test_user_id:
            self.log("Skipping test - no access token or test user", "SKIP")
            return False
        
        try:
            self.log(f"Updating user {self.test_user_id} credits from 100 to 200")
            
            patch_data = {
                "credits": 200
            }
            
            response = requests.patch(
                f"{BASE_URL}/admin/users/{self.test_user_id}",
                json=patch_data,
                cookies={"access_token": self.access_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            # Check for no 500 error
            self.assert_no_500_error(response, "Update user endpoint - no 500 error")
            
            if response.status_code == 200:
                updated_user = response.json()
                self.log(f"Updated user: {json.dumps(updated_user, indent=2)}")
                
                # Verify update worked
                self.assert_equal(updated_user.get('credits'), 200, "User credits updated correctly")
                
                return True
            else:
                self.log(f"User update failed: {response.text}", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during user update: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"User update exception: {str(e)}")
            return False
    
    def test_list_users(self):
        """Test 4: List users - verifies Motor async query operation"""
        self.log("\n" + "=" * 80)
        self.log("TEST 4: List Users (Motor Async Query Operation)")
        self.log("=" * 80)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/admin/users",
                cookies={"access_token": self.access_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            # Check for no 500 error
            self.assert_no_500_error(response, "List users endpoint - no 500 error")
            
            if response.status_code == 200:
                users = response.json()
                self.log(f"Retrieved {len(users)} users")
                
                # Verify our test user is in the list
                test_user_found = False
                for user in users:
                    if user.get('_id') == self.test_user_id:
                        test_user_found = True
                        self.log(f"Found test user: {user.get('username')}")
                        # Verify ObjectId to string conversion
                        self.assert_equal(isinstance(user.get('_id'), str), True, "User ID in list is string type")
                        break
                
                self.assert_equal(test_user_found, True, "Test user found in user list")
                
                return True
            else:
                self.log(f"List users failed: {response.text}", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during list users: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"List users exception: {str(e)}")
            return False
    
    def test_delete_user(self):
        """Test 5: Delete user - verifies Motor async delete operation"""
        self.log("\n" + "=" * 80)
        self.log("TEST 5: Delete User (Motor Async Delete Operation)")
        self.log("=" * 80)
        
        if not self.access_token or not self.test_user_id:
            self.log("Skipping test - no access token or test user", "SKIP")
            return False
        
        try:
            response = requests.delete(
                f"{BASE_URL}/admin/users/{self.test_user_id}",
                cookies={"access_token": self.access_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            # Check for no 500 error
            self.assert_no_500_error(response, "Delete user endpoint - no 500 error")
            
            if response.status_code == 200:
                self.log(f"User {self.test_user_id} deleted successfully")
                self.assert_equal(response.status_code, 200, "User deleted successfully")
                
                # Verify user is actually deleted by trying to list users
                list_response = requests.get(
                    f"{BASE_URL}/admin/users",
                    cookies={"access_token": self.access_token},
                    timeout=10
                )
                
                if list_response.status_code == 200:
                    users = list_response.json()
                    test_user_found = False
                    for user in users:
                        if user.get('_id') == self.test_user_id:
                            test_user_found = True
                            break
                    
                    self.assert_equal(test_user_found, False, "Deleted user not found in user list (delete confirmed)")
                
                return True
            else:
                self.log(f"User deletion failed: {response.text}", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during user deletion: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"User deletion exception: {str(e)}")
            return False
    
    def test_token_refresh(self):
        """Test 6: Token refresh - verifies Motor async operations in auth flow"""
        self.log("\n" + "=" * 80)
        self.log("TEST 6: Token Refresh (Motor Async Auth Operations)")
        self.log("=" * 80)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
        
        try:
            # First login to get refresh token
            login_response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
                timeout=10
            )
            
            if login_response.status_code == 200 and 'refresh_token' in login_response.cookies:
                refresh_token = login_response.cookies['refresh_token']
                
                # Now try to refresh
                response = requests.post(
                    f"{BASE_URL}/auth/refresh",
                    cookies={"refresh_token": refresh_token},
                    timeout=10
                )
                
                self.log(f"Response Status: {response.status_code}")
                
                # Check for no 500 error
                self.assert_no_500_error(response, "Token refresh endpoint - no 500 error")
                
                if response.status_code == 200:
                    self.log("Token refresh successful")
                    self.assert_equal(response.status_code, 200, "Token refresh successful")
                    
                    # Verify new access token is set
                    if 'access_token' in response.cookies:
                        self.assert_not_none(response.cookies['access_token'], "New access token received")
                    
                    return True
                else:
                    self.log(f"Token refresh failed: {response.text}", "ERROR")
                    self.failed += 1
                    return False
            else:
                self.log("Failed to get refresh token from login", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during token refresh: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Token refresh exception: {str(e)}")
            return False
    
    def test_saved_ccs_collection(self):
        """Test 7: Saved CCs collection - verifies Motor operations on saved_ccs collection"""
        self.log("\n" + "=" * 80)
        self.log("TEST 7: Saved CCs Collection (Motor Async Operations)")
        self.log("=" * 80)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/checker/saved",
                cookies={"access_token": self.access_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            # Check for no 500 error
            self.assert_no_500_error(response, "Saved CCs endpoint - no 500 error")
            
            if response.status_code == 200:
                saved_ccs = response.json()
                self.log(f"Retrieved {len(saved_ccs)} saved CCs")
                self.assert_equal(response.status_code, 200, "Saved CCs endpoint working")
                
                # If there are saved CCs, verify ObjectId to string conversion
                if len(saved_ccs) > 0:
                    first_cc = saved_ccs[0]
                    if '_id' in first_cc:
                        self.assert_equal(isinstance(first_cc.get('_id'), str), True, "Saved CC ID is string type (ObjectId converted)")
                
                return True
            else:
                self.log(f"Saved CCs fetch failed: {response.text}", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during saved CCs fetch: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Saved CCs exception: {str(e)}")
            return False
    
    def test_proxies_collection(self):
        """Test 8: Proxies collection - verifies Motor operations on proxies collection"""
        self.log("\n" + "=" * 80)
        self.log("TEST 8: Proxies Collection (Motor Async Operations)")
        self.log("=" * 80)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/proxies",
                cookies={"access_token": self.access_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            # Check for no 500 error
            self.assert_no_500_error(response, "Proxies endpoint - no 500 error")
            
            if response.status_code == 200:
                proxies = response.json()
                self.log(f"Retrieved {len(proxies)} proxies")
                self.assert_equal(response.status_code, 200, "Proxies endpoint working")
                
                # If there are proxies, verify ObjectId to string conversion
                if len(proxies) > 0:
                    first_proxy = proxies[0]
                    if '_id' in first_proxy:
                        self.assert_equal(isinstance(first_proxy.get('_id'), str), True, "Proxy ID is string type (ObjectId converted)")
                
                return True
            else:
                self.log(f"Proxies fetch failed: {response.text}", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during proxies fetch: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Proxies exception: {str(e)}")
            return False
    
    def test_redeem_codes_collection(self):
        """Test 9: Redeem codes collection - verifies Motor operations on redeem_codes collection"""
        self.log("\n" + "=" * 80)
        self.log("TEST 9: Redeem Codes Collection (Motor Async Operations)")
        self.log("=" * 80)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
        
        try:
            response = requests.get(
                f"{BASE_URL}/admin/redeem_codes",
                cookies={"access_token": self.access_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            # Check for no 500 error
            self.assert_no_500_error(response, "Redeem codes endpoint - no 500 error")
            
            if response.status_code == 200:
                codes = response.json()
                self.log(f"Retrieved {len(codes)} redeem codes")
                self.assert_equal(response.status_code, 200, "Redeem codes endpoint working")
                
                # If there are codes, verify ObjectId to string conversion
                if len(codes) > 0:
                    first_code = codes[0]
                    if '_id' in first_code:
                        self.assert_equal(isinstance(first_code.get('_id'), str), True, "Redeem code ID is string type (ObjectId converted)")
                
                return True
            else:
                self.log(f"Redeem codes fetch failed: {response.text}", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during redeem codes fetch: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Redeem codes exception: {str(e)}")
            return False
    
    def test_checker_run_endpoint(self):
        """Test 10: Checker run endpoint - verifies Motor operations in checker flow"""
        self.log("\n" + "=" * 80)
        self.log("TEST 10: Checker Run Endpoint (Motor Async Operations)")
        self.log("=" * 80)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
        
        try:
            # Test with a simple card check (using correct format: "card" not "cards")
            check_data = {
                "card": "4532015112830366|12|2025|123",
                "gateway": "stripe",
                "sk_type": "api_based"
            }
            
            response = requests.post(
                f"{BASE_URL}/checker/run",
                json=check_data,
                cookies={"access_token": self.access_token},
                timeout=30
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            # Check for no 500 error
            self.assert_no_500_error(response, "Checker run endpoint - no 500 error")
            
            if response.status_code == 200:
                result = response.json()
                self.log(f"Checker run result: {json.dumps(result, indent=2)}")
                self.assert_equal(response.status_code, 200, "Checker run endpoint working")
                
                return True
            else:
                # Even if not 200, as long as it's not 500, Motor/PyMongo is working
                # Could be 400 (bad request), 401 (unauthorized), etc.
                self.log(f"Checker run response: {response.text}", "INFO")
                # Still count as pass if no 500 error (Motor/PyMongo is working)
                if response.status_code != 500:
                    self.assert_not_equal(response.status_code, 500, "Checker endpoint responding (no 500 error)")
                    return True
                else:
                    self.failed += 1
                    return False
                
        except Exception as e:
            self.log(f"Exception during checker run: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Checker run exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all Motor/PyMongo verification tests"""
        self.log("\n" + "=" * 80)
        self.log("MOTOR/PYMONGO BACKEND VERIFICATION TEST SUITE")
        self.log("=" * 80)
        self.log(f"Backend URL: {BASE_URL}")
        self.log(f"Testing Motor async operations and ObjectId handling")
        self.log("")
        
        # Run tests in sequence
        self.test_admin_login()
        self.test_create_user()
        self.test_update_user()
        self.test_list_users()
        self.test_delete_user()
        self.test_token_refresh()
        self.test_saved_ccs_collection()
        self.test_proxies_collection()
        self.test_redeem_codes_collection()
        self.test_checker_run_endpoint()
        
        # Print summary
        self.log("\n" + "=" * 80)
        self.log("TEST SUMMARY")
        self.log("=" * 80)
        self.log(f"Total Passed: {self.passed}")
        self.log(f"Total Failed: {self.failed}")
        
        if self.errors:
            self.log("\nFailed Tests:")
            for error in self.errors:
                self.log(f"  - {error}")
        
        self.log("=" * 80)
        
        if self.failed == 0:
            self.log("\n✅ ALL TESTS PASSED - Motor/PyMongo implementation is working correctly!")
            self.log("✅ No syntax errors detected")
            self.log("✅ No 500 Internal Server Errors")
            self.log("✅ All CRUD operations working")
            self.log("✅ ObjectId to string conversion working correctly")
            self.log("✅ All collections (users, saved_ccs, proxies, redeem_codes) working")
        else:
            self.log("\n❌ SOME TESTS FAILED - Please review errors above")
        
        self.log("=" * 80)
        
        return self.failed == 0

if __name__ == "__main__":
    runner = MotorPyMongoTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
