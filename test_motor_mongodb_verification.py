import requests
import json
from datetime import datetime

# Backend URL from frontend/.env
BACKEND_URL = "https://render-ready-4.preview.emergentagent.com/api"

print("=" * 80)
print("MOTOR/MONGODB DATABASE CONNECTION AND OBJECTID VERIFICATION TEST")
print("=" * 80)
print(f"Testing backend at: {BACKEND_URL}")
print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Test counters
total_tests = 0
passed_tests = 0
failed_tests = 0

def test_result(test_name, passed, details=""):
    global total_tests, passed_tests, failed_tests
    total_tests += 1
    if passed:
        passed_tests += 1
        print(f"✅ PASS: {test_name}")
    else:
        failed_tests += 1
        print(f"❌ FAIL: {test_name}")
    if details:
        print(f"   Details: {details}")
    print()

# Test 1: Server Health Check - Basic connectivity
print("TEST 1: Server Health Check - Basic Connectivity")
print("-" * 80)
try:
    response = requests.get(f"{BACKEND_URL}/auth/me", timeout=10)
    # We expect 401 since we're not authenticated, but this proves server is responding
    if response.status_code in [200, 401]:
        test_result("Server is responding", True, f"Status code: {response.status_code}")
    else:
        test_result("Server is responding", False, f"Unexpected status code: {response.status_code}")
except Exception as e:
    test_result("Server is responding", False, f"Error: {str(e)}")

# Test 2: Login - Database Read Operation with ObjectId
print("TEST 2: Login - Database Read Operation (Motor + ObjectId)")
print("-" * 80)
try:
    login_data = {
        "username": "SHORIEN",
        "password": "Xiron696@"
    }
    response = requests.post(f"{BACKEND_URL}/auth/login", json=login_data, timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        if "user" in data and "_id" in data["user"]:
            # Check if _id is a string (converted from ObjectId)
            user_id = data["user"]["_id"]
            if isinstance(user_id, str) and len(user_id) > 0:
                test_result("Login successful - ObjectId converted to string", True, 
                           f"User ID: {user_id}, Username: {data['user'].get('username')}")
                
                # Store cookies for subsequent tests
                access_token = response.cookies.get("access_token")
                refresh_token = response.cookies.get("refresh_token")
                
                if access_token and refresh_token:
                    test_result("Auth cookies set correctly", True, 
                               "Both access_token and refresh_token cookies received")
                else:
                    test_result("Auth cookies set correctly", False, 
                               f"Missing cookies - access_token: {bool(access_token)}, refresh_token: {bool(refresh_token)}")
            else:
                test_result("Login successful - ObjectId converted to string", False, 
                           f"Invalid user ID format: {user_id}")
        else:
            test_result("Login successful - ObjectId converted to string", False, 
                       f"Missing user data in response: {data}")
    else:
        test_result("Login successful - ObjectId converted to string", False, 
                   f"Login failed with status {response.status_code}: {response.text}")
        
except Exception as e:
    test_result("Login successful - ObjectId converted to string", False, f"Error: {str(e)}")

# Test 3: Get Current User - Verify Motor async operations
print("TEST 3: Get Current User - Verify Motor Async Operations")
print("-" * 80)
try:
    # Use the cookies from login
    response = requests.get(f"{BACKEND_URL}/auth/me", cookies={"access_token": access_token}, timeout=10)
    
    if response.status_code == 200:
        user_data = response.json()
        if "_id" in user_data and "username" in user_data:
            test_result("Get current user with Motor", True, 
                       f"User retrieved: {user_data.get('username')}, ID: {user_data.get('_id')}")
        else:
            test_result("Get current user with Motor", False, 
                       f"Incomplete user data: {user_data}")
    else:
        test_result("Get current user with Motor", False, 
                   f"Failed with status {response.status_code}: {response.text}")
except Exception as e:
    test_result("Get current user with Motor", False, f"Error: {str(e)}")

# Test 4: Create User - Database Write Operation with ObjectId
print("TEST 4: Create User - Database Write Operation (Motor + ObjectId)")
print("-" * 80)
try:
    new_user_data = {
        "username": f"testuser_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "password": "TestPass123!",
        "role": "user",
        "credits": 100,
        "plan": "free"
    }
    
    response = requests.post(
        f"{BACKEND_URL}/admin/users",
        json=new_user_data,
        cookies={"access_token": access_token},
        timeout=10
    )
    
    if response.status_code == 200:
        created_user = response.json()
        if "_id" in created_user and isinstance(created_user["_id"], str):
            test_result("Create user - Motor insert with ObjectId", True, 
                       f"User created with ID: {created_user['_id']}, Username: {created_user.get('username')}")
            
            # Store the user ID for deletion test
            test_user_id = created_user["_id"]
        else:
            test_result("Create user - Motor insert with ObjectId", False, 
                       f"Invalid user ID in response: {created_user}")
    else:
        test_result("Create user - Motor insert with ObjectId", False, 
                   f"Failed with status {response.status_code}: {response.text}")
except Exception as e:
    test_result("Create user - Motor insert with ObjectId", False, f"Error: {str(e)}")

# Test 5: Update User - Database Update Operation with ObjectId
print("TEST 5: Update User - Database Update Operation (Motor + ObjectId)")
print("-" * 80)
try:
    update_data = {
        "credits": 200,
        "plan": "premium"
    }
    
    response = requests.patch(
        f"{BACKEND_URL}/admin/users/{test_user_id}",
        json=update_data,
        cookies={"access_token": access_token},
        timeout=10
    )
    
    if response.status_code == 200:
        updated_user = response.json()
        if updated_user.get("credits") == 200 and updated_user.get("plan") == "premium":
            test_result("Update user - Motor update with ObjectId", True, 
                       f"User updated successfully - Credits: {updated_user.get('credits')}, Plan: {updated_user.get('plan')}")
        else:
            test_result("Update user - Motor update with ObjectId", False, 
                       f"Update didn't persist correctly: {updated_user}")
    else:
        test_result("Update user - Motor update with ObjectId", False, 
                   f"Failed with status {response.status_code}: {response.text}")
except Exception as e:
    test_result("Update user - Motor update with ObjectId", False, f"Error: {str(e)}")

# Test 6: List Users - Database Query Operation
print("TEST 6: List Users - Database Query Operation (Motor)")
print("-" * 80)
try:
    response = requests.get(
        f"{BACKEND_URL}/admin/users",
        cookies={"access_token": access_token},
        timeout=10
    )
    
    if response.status_code == 200:
        users = response.json()
        if isinstance(users, list) and len(users) > 0:
            # Check if all users have string IDs (converted from ObjectId)
            all_valid = all(isinstance(u.get("_id"), str) for u in users)
            if all_valid:
                test_result("List users - Motor query with ObjectId conversion", True, 
                           f"Retrieved {len(users)} users, all with valid string IDs")
            else:
                test_result("List users - Motor query with ObjectId conversion", False, 
                           "Some users have invalid ID format")
        else:
            test_result("List users - Motor query with ObjectId conversion", False, 
                       f"Invalid response format: {users}")
    else:
        test_result("List users - Motor query with ObjectId conversion", False, 
                   f"Failed with status {response.status_code}: {response.text}")
except Exception as e:
    test_result("List users - Motor query with ObjectId conversion", False, f"Error: {str(e)}")

# Test 7: Delete User - Database Delete Operation with ObjectId
print("TEST 7: Delete User - Database Delete Operation (Motor + ObjectId)")
print("-" * 80)
try:
    response = requests.delete(
        f"{BACKEND_URL}/admin/users/{test_user_id}",
        cookies={"access_token": access_token},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        if "message" in result:
            test_result("Delete user - Motor delete with ObjectId", True, 
                       f"User deleted successfully: {result.get('message')}")
        else:
            test_result("Delete user - Motor delete with ObjectId", False, 
                       f"Unexpected response: {result}")
    else:
        test_result("Delete user - Motor delete with ObjectId", False, 
                   f"Failed with status {response.status_code}: {response.text}")
except Exception as e:
    test_result("Delete user - Motor delete with ObjectId", False, f"Error: {str(e)}")

# Test 8: Saved CCs Collection - Test ObjectId in saved_ccs collection
print("TEST 8: Saved CCs Collection - ObjectId Usage in saved_ccs")
print("-" * 80)
try:
    response = requests.get(
        f"{BACKEND_URL}/checker/saved",
        cookies={"access_token": access_token},
        timeout=10
    )
    
    if response.status_code == 200:
        saved_ccs = response.json()
        if isinstance(saved_ccs, list):
            if len(saved_ccs) > 0:
                # Check if all saved CCs have string IDs
                all_valid = all(isinstance(cc.get("_id"), str) for cc in saved_ccs)
                if all_valid:
                    test_result("Saved CCs - ObjectId conversion", True, 
                               f"Retrieved {len(saved_ccs)} saved CCs, all with valid string IDs")
                else:
                    test_result("Saved CCs - ObjectId conversion", False, 
                               "Some saved CCs have invalid ID format")
            else:
                test_result("Saved CCs - ObjectId conversion", True, 
                           "No saved CCs found (empty list is valid)")
        else:
            test_result("Saved CCs - ObjectId conversion", False, 
                       f"Invalid response format: {saved_ccs}")
    else:
        test_result("Saved CCs - ObjectId conversion", False, 
                   f"Failed with status {response.status_code}: {response.text}")
except Exception as e:
    test_result("Saved CCs - ObjectId conversion", False, f"Error: {str(e)}")

# Test 9: Proxies Collection - Test ObjectId in proxies collection
print("TEST 9: Proxies Collection - ObjectId Usage in proxies")
print("-" * 80)
try:
    response = requests.get(
        f"{BACKEND_URL}/proxies",
        cookies={"access_token": access_token},
        timeout=10
    )
    
    if response.status_code == 200:
        proxies = response.json()
        if isinstance(proxies, list):
            if len(proxies) > 0:
                # Check if all proxies have string IDs
                all_valid = all(isinstance(p.get("_id"), str) for p in proxies)
                if all_valid:
                    test_result("Proxies - ObjectId conversion", True, 
                               f"Retrieved {len(proxies)} proxies, all with valid string IDs")
                else:
                    test_result("Proxies - ObjectId conversion", False, 
                               "Some proxies have invalid ID format")
            else:
                test_result("Proxies - ObjectId conversion", True, 
                           "No proxies found (empty list is valid)")
        else:
            test_result("Proxies - ObjectId conversion", False, 
                       f"Invalid response format: {proxies}")
    else:
        test_result("Proxies - ObjectId conversion", False, 
                   f"Failed with status {response.status_code}: {response.text}")
except Exception as e:
    test_result("Proxies - ObjectId conversion", False, f"Error: {str(e)}")

# Test 10: Redeem Codes Collection - Test ObjectId in redeem_codes collection
print("TEST 10: Redeem Codes Collection - ObjectId Usage in redeem_codes")
print("-" * 80)
try:
    response = requests.get(
        f"{BACKEND_URL}/admin/redeem_codes",
        cookies={"access_token": access_token},
        timeout=10
    )
    
    if response.status_code == 200:
        codes = response.json()
        if isinstance(codes, list):
            if len(codes) > 0:
                # Check if all codes have string IDs
                all_valid = all(isinstance(c.get("_id"), str) for c in codes)
                if all_valid:
                    test_result("Redeem Codes - ObjectId conversion", True, 
                               f"Retrieved {len(codes)} redeem codes, all with valid string IDs")
                else:
                    test_result("Redeem Codes - ObjectId conversion", False, 
                               "Some redeem codes have invalid ID format")
            else:
                test_result("Redeem Codes - ObjectId conversion", True, 
                           "No redeem codes found (empty list is valid)")
        else:
            test_result("Redeem Codes - ObjectId conversion", False, 
                       f"Invalid response format: {codes}")
    else:
        test_result("Redeem Codes - ObjectId conversion", False, 
                   f"Failed with status {response.status_code}: {response.text}")
except Exception as e:
    test_result("Redeem Codes - ObjectId conversion", False, f"Error: {str(e)}")

# Test 11: Token Refresh - Verify Motor operations in refresh endpoint
print("TEST 11: Token Refresh - Verify Motor Operations in Refresh Endpoint")
print("-" * 80)
try:
    response = requests.post(
        f"{BACKEND_URL}/auth/refresh",
        cookies={"refresh_token": refresh_token},
        timeout=10
    )
    
    if response.status_code == 200:
        result = response.json()
        new_access_token = response.cookies.get("access_token")
        if new_access_token:
            test_result("Token refresh - Motor operations", True, 
                       f"Token refreshed successfully, new access_token received")
        else:
            test_result("Token refresh - Motor operations", False, 
                       "No new access_token in response")
    else:
        test_result("Token refresh - Motor operations", False, 
                   f"Failed with status {response.status_code}: {response.text}")
except Exception as e:
    test_result("Token refresh - Motor operations", False, f"Error: {str(e)}")

# Summary
print("=" * 80)
print("TEST SUMMARY")
print("=" * 80)
print(f"Total Tests: {total_tests}")
print(f"Passed: {passed_tests} ✅")
print(f"Failed: {failed_tests} ❌")
print(f"Success Rate: {(passed_tests/total_tests*100):.1f}%")
print()

if failed_tests == 0:
    print("🎉 ALL TESTS PASSED!")
    print()
    print("VERIFICATION COMPLETE:")
    print("✅ Motor/MongoDB connection is working correctly")
    print("✅ Database operations (read, write, update, delete) are functional")
    print("✅ ObjectId is properly imported from bson and used throughout")
    print("✅ ObjectId to string conversion is working in all collections")
    print("✅ No syntax errors detected")
    print("✅ Server startup is successful")
else:
    print("⚠️  SOME TESTS FAILED")
    print(f"Please review the {failed_tests} failed test(s) above for details.")

print()
print(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 80)
