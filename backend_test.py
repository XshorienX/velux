#!/usr/bin/env python3
"""
Backend API Test Suite
Tests admin user creation and patch endpoints for 'plan' field handling
"""

import requests
import json
import sys
from datetime import datetime

# Backend URL from frontend/.env
BASE_URL = "https://render-ready-4.preview.emergentagent.com/api"

# Admin credentials from backend/.env
ADMIN_USERNAME = "SHORIEN"
ADMIN_PASSWORD = "Xiron696@"

class TestRunner:
    def __init__(self):
        self.access_token = None
        self.test_user_id = None
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
    
    def test_admin_login(self):
        """Test admin login and get access token"""
        self.log("=" * 60)
        self.log("TEST: Admin Login")
        self.log("=" * 60)
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": ADMIN_USERNAME, "password": ADMIN_PASSWORD},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Response: {json.dumps(data, indent=2)}")
                
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
    
    def test_create_user_with_plan(self):
        """Test creating a user with 'plan' field"""
        self.log("\n" + "=" * 60)
        self.log("TEST: Create User with Plan Field")
        self.log("=" * 60)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
        
        # Generate unique username
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        test_username = f"testuser_{timestamp}"
        
        try:
            # Test creating user with 'premium' plan
            user_data = {
                "username": test_username,
                "password": "TestPass123!",
                "role": "user",
                "credits": 500,
                "plan": "premium"
            }
            
            self.log(f"Creating user: {test_username} with plan: premium")
            
            response = requests.post(
                f"{BASE_URL}/admin/users",
                json=user_data,
                cookies={"access_token": self.access_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            if response.status_code == 200:
                created_user = response.json()
                self.log(f"Created user data: {json.dumps(created_user, indent=2)}")
                
                # Store user ID for later tests
                self.test_user_id = created_user.get('_id')
                
                # Verify plan field
                self.assert_equal(created_user.get('plan'), 'premium', "User created with correct plan field")
                self.assert_equal(created_user.get('username'), test_username, "User created with correct username")
                self.assert_equal(created_user.get('credits'), 500, "User created with correct credits")
                self.assert_not_none(self.test_user_id, "User ID is present")
                
                return True
            else:
                self.log(f"User creation failed: {response.text}", "ERROR")
                self.failed += 1
                self.errors.append(f"User creation failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"Exception during user creation: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"User creation exception: {str(e)}")
            return False
    
    def test_patch_user_plan(self):
        """Test patching a user's plan field"""
        self.log("\n" + "=" * 60)
        self.log("TEST: Patch User Plan Field")
        self.log("=" * 60)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
            
        if not self.test_user_id:
            self.log("Skipping test - no test user created", "SKIP")
            return False
        
        try:
            # Test 1: Update plan from 'premium' to 'free'
            self.log(f"Updating user {self.test_user_id} plan from 'premium' to 'free'")
            
            patch_data = {
                "plan": "free"
            }
            
            response = requests.patch(
                f"{BASE_URL}/admin/users/{self.test_user_id}",
                json=patch_data,
                cookies={"access_token": self.access_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            if response.status_code == 200:
                updated_user = response.json()
                self.log(f"Updated user data: {json.dumps(updated_user, indent=2)}")
                
                # Verify plan was updated
                self.assert_equal(updated_user.get('plan'), 'free', "User plan updated to 'free'")
                
                # Test 2: Update plan back to 'premium'
                self.log(f"\nUpdating user {self.test_user_id} plan from 'free' to 'premium'")
                
                patch_data = {
                    "plan": "premium"
                }
                
                response2 = requests.patch(
                    f"{BASE_URL}/admin/users/{self.test_user_id}",
                    json=patch_data,
                    cookies={"access_token": self.access_token},
                    timeout=10
                )
                
                self.log(f"Response Status: {response2.status_code}")
                self.log(f"Response: {response2.text}")
                
                if response2.status_code == 200:
                    updated_user2 = response2.json()
                    self.log(f"Updated user data: {json.dumps(updated_user2, indent=2)}")
                    
                    # Verify plan was updated again
                    self.assert_equal(updated_user2.get('plan'), 'premium', "User plan updated back to 'premium'")
                    
                    return True
                else:
                    self.log(f"Second patch failed: {response2.text}", "ERROR")
                    self.failed += 1
                    self.errors.append(f"Second patch failed with status {response2.status_code}")
                    return False
            else:
                self.log(f"First patch failed: {response.text}", "ERROR")
                self.failed += 1
                self.errors.append(f"First patch failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"Exception during user patch: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"User patch exception: {str(e)}")
            return False
    
    def test_verify_plan_persistence(self):
        """Verify that plan changes are persisted by fetching user list"""
        self.log("\n" + "=" * 60)
        self.log("TEST: Verify Plan Persistence")
        self.log("=" * 60)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
            
        if not self.test_user_id:
            self.log("Skipping test - no test user created", "SKIP")
            return False
        
        try:
            self.log(f"Fetching user list to verify plan persistence for user {self.test_user_id}")
            
            response = requests.get(
                f"{BASE_URL}/admin/users",
                cookies={"access_token": self.access_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                users = response.json()
                self.log(f"Retrieved {len(users)} users")
                
                # Find our test user
                test_user = None
                for user in users:
                    if user.get('_id') == self.test_user_id:
                        test_user = user
                        break
                
                if test_user:
                    self.log(f"Found test user: {json.dumps(test_user, indent=2)}")
                    # Should be 'premium' from the last patch
                    self.assert_equal(test_user.get('plan'), 'premium', "Plan persisted correctly as 'premium'")
                    return True
                else:
                    self.log(f"Test user {self.test_user_id} not found in user list", "ERROR")
                    self.failed += 1
                    self.errors.append("Test user not found in user list")
                    return False
            else:
                self.log(f"Failed to fetch users: {response.text}", "ERROR")
                self.failed += 1
                self.errors.append(f"Failed to fetch users with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"Exception during verification: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Verification exception: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up test user"""
        self.log("\n" + "=" * 60)
        self.log("CLEANUP: Deleting Test User")
        self.log("=" * 60)
        
        if not self.access_token or not self.test_user_id:
            self.log("Skipping cleanup - no user to delete", "SKIP")
            return
        
        try:
            response = requests.delete(
                f"{BASE_URL}/admin/users/{self.test_user_id}",
                cookies={"access_token": self.access_token},
                timeout=10
            )
            
            if response.status_code == 200:
                self.log(f"✅ Test user {self.test_user_id} deleted successfully")
            else:
                self.log(f"⚠️  Failed to delete test user: {response.text}", "WARN")
                
        except Exception as e:
            self.log(f"⚠️  Exception during cleanup: {str(e)}", "WARN")
    
    def run_all_tests(self):
        """Run all tests"""
        self.log("\n" + "=" * 80)
        self.log("BACKEND API TEST SUITE - PLAN FIELD TESTING")
        self.log("=" * 80)
        self.log(f"Backend URL: {BASE_URL}")
        self.log(f"Admin User: {ADMIN_USERNAME}")
        self.log("")
        
        # Run tests in sequence
        if self.test_admin_login():
            self.test_create_user_with_plan()
            self.test_patch_user_plan()
            self.test_verify_plan_persistence()
            self.cleanup()
        
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
        
        return self.failed == 0

if __name__ == "__main__":
    runner = TestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
