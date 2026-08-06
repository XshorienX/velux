#!/usr/bin/env python3
"""
Backend API Test Suite - DELETE Saved CCs Endpoints
Tests DELETE /api/checker/saved/all and DELETE /api/checker/saved/{hit_id}
Verifies correct filtering by user_id and security isolation
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
        self.admin_token = None
        self.user1_token = None
        self.user2_token = None
        self.user1_id = None
        self.user2_id = None
        self.user1_hits = []
        self.user2_hits = []
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
            
    def assert_true(self, condition, test_name):
        if condition:
            self.passed += 1
            self.log(f"✅ PASS: {test_name}", "PASS")
            return True
        else:
            self.failed += 1
            error_msg = f"❌ FAIL: {test_name}"
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
    
    def login(self, username, password):
        """Login and return access token"""
        try:
            response = requests.post(
                f"{BASE_URL}/auth/login",
                json={"username": username, "password": password},
                timeout=10
            )
            
            if response.status_code == 200 and 'access_token' in response.cookies:
                return response.cookies['access_token']
            else:
                self.log(f"Login failed for {username}: {response.status_code} - {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Exception during login for {username}: {str(e)}", "ERROR")
            return None
    
    def test_admin_login(self):
        """Test admin login"""
        self.log("=" * 60)
        self.log("TEST: Admin Login")
        self.log("=" * 60)
        
        self.admin_token = self.login(ADMIN_USERNAME, ADMIN_PASSWORD)
        return self.assert_not_none(self.admin_token, "Admin login successful")
    
    def create_test_user(self, username, password):
        """Create a test user and return user_id"""
        try:
            user_data = {
                "username": username,
                "password": password,
                "role": "user",
                "credits": 1000,
                "plan": "premium"
            }
            
            response = requests.post(
                f"{BASE_URL}/admin/users",
                json=user_data,
                cookies={"access_token": self.admin_token},
                timeout=10
            )
            
            if response.status_code == 200:
                user = response.json()
                self.log(f"Created user: {username} with ID: {user.get('_id')}")
                return user.get('_id')
            else:
                self.log(f"Failed to create user {username}: {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Exception creating user {username}: {str(e)}", "ERROR")
            return None
    
    def test_create_test_users(self):
        """Create two test users for testing"""
        self.log("\n" + "=" * 60)
        self.log("TEST: Create Test Users")
        self.log("=" * 60)
        
        if not self.admin_token:
            self.log("Skipping - no admin token", "SKIP")
            return False
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        user1_name = f"testuser1_{timestamp}"
        user2_name = f"testuser2_{timestamp}"
        
        self.user1_id = self.create_test_user(user1_name, "TestPass123!")
        self.user2_id = self.create_test_user(user2_name, "TestPass123!")
        
        success = self.assert_not_none(self.user1_id, "User1 created successfully")
        success = self.assert_not_none(self.user2_id, "User2 created successfully") and success
        
        if success:
            # Login as both users
            self.user1_token = self.login(user1_name, "TestPass123!")
            self.user2_token = self.login(user2_name, "TestPass123!")
            
            success = self.assert_not_none(self.user1_token, "User1 login successful")
            success = self.assert_not_none(self.user2_token, "User2 login successful") and success
        
        return success
    
    def insert_saved_cc(self, user_token, card_data):
        """Insert a saved CC directly into database by calling the saved endpoint"""
        # Since we need to insert directly, we'll use MongoDB directly
        # But for testing purposes, we'll create mock data
        import pymongo
        from bson import ObjectId
        
        try:
            client = pymongo.MongoClient("mongodb://localhost:27017")
            db = client["test_database"]
            
            result = db.saved_ccs.insert_one(card_data)
            return str(result.inserted_id)
        except Exception as e:
            self.log(f"Exception inserting saved CC: {str(e)}", "ERROR")
            return None
    
    def test_insert_test_data(self):
        """Insert test saved CCs for both users"""
        self.log("\n" + "=" * 60)
        self.log("TEST: Insert Test Saved CCs")
        self.log("=" * 60)
        
        if not self.user1_id or not self.user2_id:
            self.log("Skipping - no test users", "SKIP")
            return False
        
        try:
            import pymongo
            client = pymongo.MongoClient("mongodb://localhost:27017")
            db = client["test_database"]
            
            # Insert 3 saved CCs for user1
            for i in range(3):
                doc = {
                    "user_id": self.user1_id,
                    "card": f"4532********{1000+i}",
                    "gateway": f"test_gateway_{i+1}",
                    "response": "APPROVED",
                    "created_at": datetime.utcnow()
                }
                result = db.saved_ccs.insert_one(doc)
                self.user1_hits.append(str(result.inserted_id))
                self.log(f"Inserted saved CC for user1: {result.inserted_id}")
            
            # Insert 2 saved CCs for user2
            for i in range(2):
                doc = {
                    "user_id": self.user2_id,
                    "card": f"5555********{2000+i}",
                    "gateway": f"test_gateway_{i+1}",
                    "response": "APPROVED",
                    "created_at": datetime.utcnow()
                }
                result = db.saved_ccs.insert_one(doc)
                self.user2_hits.append(str(result.inserted_id))
                self.log(f"Inserted saved CC for user2: {result.inserted_id}")
            
            self.assert_equal(len(self.user1_hits), 3, "User1 has 3 saved CCs")
            self.assert_equal(len(self.user2_hits), 2, "User2 has 2 saved CCs")
            
            return True
            
        except Exception as e:
            self.log(f"Exception inserting test data: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Failed to insert test data: {str(e)}")
            return False
    
    def get_saved_ccs(self, user_token):
        """Get saved CCs for a user"""
        try:
            response = requests.get(
                f"{BASE_URL}/checker/saved",
                cookies={"access_token": user_token},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                self.log(f"Failed to get saved CCs: {response.status_code} - {response.text}", "ERROR")
                return None
                
        except Exception as e:
            self.log(f"Exception getting saved CCs: {str(e)}", "ERROR")
            return None
    
    def test_verify_initial_data(self):
        """Verify that both users can see their saved CCs"""
        self.log("\n" + "=" * 60)
        self.log("TEST: Verify Initial Saved CCs")
        self.log("=" * 60)
        
        if not self.user1_token or not self.user2_token:
            self.log("Skipping - no user tokens", "SKIP")
            return False
        
        # Check user1's saved CCs
        user1_saved = self.get_saved_ccs(self.user1_token)
        if user1_saved is not None:
            self.log(f"User1 has {len(user1_saved)} saved CCs")
            self.assert_equal(len(user1_saved), 3, "User1 can see 3 saved CCs")
        else:
            self.failed += 1
            self.errors.append("Failed to get user1's saved CCs")
        
        # Check user2's saved CCs
        user2_saved = self.get_saved_ccs(self.user2_token)
        if user2_saved is not None:
            self.log(f"User2 has {len(user2_saved)} saved CCs")
            self.assert_equal(len(user2_saved), 2, "User2 can see 2 saved CCs")
        else:
            self.failed += 1
            self.errors.append("Failed to get user2's saved CCs")
        
        return user1_saved is not None and user2_saved is not None
    
    def test_delete_single_hit_own_user(self):
        """Test DELETE /api/checker/saved/{hit_id} - user deletes their own hit"""
        self.log("\n" + "=" * 60)
        self.log("TEST: DELETE Single Hit (Own User)")
        self.log("=" * 60)
        
        if not self.user1_token or len(self.user1_hits) == 0:
            self.log("Skipping - no user1 token or hits", "SKIP")
            return False
        
        hit_to_delete = self.user1_hits[0]
        self.log(f"User1 deleting their own hit: {hit_to_delete}")
        
        try:
            response = requests.delete(
                f"{BASE_URL}/checker/saved/{hit_to_delete}",
                cookies={"access_token": self.user1_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.assert_equal(data.get("message"), "Hit deleted", "Correct response message")
                
                # Verify the hit was deleted
                user1_saved = self.get_saved_ccs(self.user1_token)
                if user1_saved is not None:
                    self.log(f"User1 now has {len(user1_saved)} saved CCs")
                    self.assert_equal(len(user1_saved), 2, "User1 now has 2 saved CCs (1 deleted)")
                    
                    # Verify the deleted hit is not in the list
                    hit_ids = [hit["_id"] for hit in user1_saved]
                    self.assert_true(hit_to_delete not in hit_ids, "Deleted hit is not in user1's list")
                    
                    return True
                else:
                    self.failed += 1
                    self.errors.append("Failed to verify deletion")
                    return False
            else:
                self.failed += 1
                self.errors.append(f"Delete failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"Exception during delete: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Delete exception: {str(e)}")
            return False
    
    def test_delete_single_hit_other_user(self):
        """Test DELETE /api/checker/saved/{hit_id} - user tries to delete another user's hit (security check)"""
        self.log("\n" + "=" * 60)
        self.log("TEST: DELETE Single Hit (Other User - Security Check)")
        self.log("=" * 60)
        
        if not self.user1_token or len(self.user2_hits) == 0:
            self.log("Skipping - no user1 token or user2 hits", "SKIP")
            return False
        
        user2_hit = self.user2_hits[0]
        self.log(f"User1 attempting to delete User2's hit: {user2_hit}")
        
        try:
            # User1 tries to delete User2's hit
            response = requests.delete(
                f"{BASE_URL}/checker/saved/{user2_hit}",
                cookies={"access_token": self.user1_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            # The endpoint should return 200 but not actually delete the hit
            # because the filter includes user_id
            if response.status_code == 200:
                # Verify User2's hit is still there
                user2_saved = self.get_saved_ccs(self.user2_token)
                if user2_saved is not None:
                    self.log(f"User2 still has {len(user2_saved)} saved CCs")
                    self.assert_equal(len(user2_saved), 2, "User2 still has 2 saved CCs (not deleted by User1)")
                    
                    # Verify the hit is still in user2's list
                    hit_ids = [hit["_id"] for hit in user2_saved]
                    self.assert_true(user2_hit in hit_ids, "User2's hit was NOT deleted by User1 (security working)")
                    
                    return True
                else:
                    self.failed += 1
                    self.errors.append("Failed to verify User2's hits")
                    return False
            else:
                self.failed += 1
                self.errors.append(f"Unexpected response status {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"Exception during delete: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Delete exception: {str(e)}")
            return False
    
    def test_delete_all_hits(self):
        """Test DELETE /api/checker/saved/all - user deletes all their hits"""
        self.log("\n" + "=" * 60)
        self.log("TEST: DELETE All Hits (Own User)")
        self.log("=" * 60)
        
        if not self.user1_token:
            self.log("Skipping - no user1 token", "SKIP")
            return False
        
        self.log("User1 deleting all their hits")
        
        try:
            response = requests.delete(
                f"{BASE_URL}/checker/saved/all",
                cookies={"access_token": self.user1_token},
                timeout=10
            )
            
            self.log(f"Response Status: {response.status_code}")
            self.log(f"Response: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                self.assert_equal(data.get("message"), "All saved hits cleared", "Correct response message")
                
                # Verify user1's hits are all deleted
                user1_saved = self.get_saved_ccs(self.user1_token)
                if user1_saved is not None:
                    self.log(f"User1 now has {len(user1_saved)} saved CCs")
                    self.assert_equal(len(user1_saved), 0, "User1 has 0 saved CCs (all deleted)")
                else:
                    self.failed += 1
                    self.errors.append("Failed to verify user1's deletion")
                    return False
                
                # Verify user2's hits are still intact
                user2_saved = self.get_saved_ccs(self.user2_token)
                if user2_saved is not None:
                    self.log(f"User2 still has {len(user2_saved)} saved CCs")
                    self.assert_equal(len(user2_saved), 2, "User2 still has 2 saved CCs (not affected by User1's delete all)")
                    return True
                else:
                    self.failed += 1
                    self.errors.append("Failed to verify user2's hits")
                    return False
            else:
                self.failed += 1
                self.errors.append(f"Delete all failed with status {response.status_code}")
                return False
                
        except Exception as e:
            self.log(f"Exception during delete all: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Delete all exception: {str(e)}")
            return False
    
    def cleanup(self):
        """Clean up test users and data"""
        self.log("\n" + "=" * 60)
        self.log("CLEANUP: Deleting Test Users and Data")
        self.log("=" * 60)
        
        if not self.admin_token:
            self.log("Skipping cleanup - no admin token", "SKIP")
            return
        
        # Delete user2's saved CCs
        if self.user2_token:
            try:
                requests.delete(
                    f"{BASE_URL}/checker/saved/all",
                    cookies={"access_token": self.user2_token},
                    timeout=10
                )
                self.log("✅ Deleted User2's saved CCs")
            except Exception as e:
                self.log(f"⚠️  Failed to delete User2's saved CCs: {str(e)}", "WARN")
        
        # Delete test users
        for user_id, user_name in [(self.user1_id, "User1"), (self.user2_id, "User2")]:
            if user_id:
                try:
                    response = requests.delete(
                        f"{BASE_URL}/admin/users/{user_id}",
                        cookies={"access_token": self.admin_token},
                        timeout=10
                    )
                    
                    if response.status_code == 200:
                        self.log(f"✅ {user_name} deleted successfully")
                    else:
                        self.log(f"⚠️  Failed to delete {user_name}: {response.text}", "WARN")
                        
                except Exception as e:
                    self.log(f"⚠️  Exception deleting {user_name}: {str(e)}", "WARN")
    
    def run_all_tests(self):
        """Run all tests"""
        self.log("\n" + "=" * 80)
        self.log("BACKEND API TEST SUITE - DELETE SAVED CCS ENDPOINTS")
        self.log("=" * 80)
        self.log(f"Backend URL: {BASE_URL}")
        self.log(f"Testing DELETE /api/checker/saved/all and DELETE /api/checker/saved/{{hit_id}}")
        self.log("")
        
        # Run tests in sequence
        if self.test_admin_login():
            if self.test_create_test_users():
                if self.test_insert_test_data():
                    if self.test_verify_initial_data():
                        self.test_delete_single_hit_own_user()
                        self.test_delete_single_hit_other_user()
                        self.test_delete_all_hits()
            
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
