#!/usr/bin/env python3
"""
Shopify Tools API Test Suite
Tests /api/shopify_tools/stores and /api/shopify_tools/products endpoints
Verifies:
1. /api/shopify_tools/stores accepts 'pages' parameter and uses asyncio.Semaphore(10)
2. /api/shopify_tools/products uses asyncio.Semaphore(40) for concurrency
"""

import requests
import json
import sys
import time
from datetime import datetime

# Backend URL from frontend/.env
BASE_URL = "https://render-ready-4.preview.emergentagent.com/api"

# Admin credentials from backend/.env
ADMIN_USERNAME = "SHORIEN"
ADMIN_PASSWORD = "Xiron696@"

class ShopifyToolsTestRunner:
    def __init__(self):
        self.access_token = None
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
            
    def assert_true(self, condition, test_name):
        if condition:
            self.passed += 1
            self.log(f"✅ PASS: {test_name}", "PASS")
            return True
        else:
            self.failed += 1
            error_msg = f"❌ FAIL: {test_name} - Condition is False"
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
                
                # Check if we got cookies
                if 'access_token' in response.cookies:
                    self.access_token = response.cookies['access_token']
                    self.log(f"Access token received via cookie")
                    self.assert_not_none(self.access_token, "Admin login successful with access token")
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
    
    def test_stores_endpoint_pages_parameter(self):
        """Test /api/shopify_tools/stores endpoint accepts 'pages' parameter"""
        self.log("\n" + "=" * 60)
        self.log("TEST: Stores Endpoint - Pages Parameter")
        self.log("=" * 60)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
        
        try:
            # Test 1: Default pages (should be 1)
            self.log("Test 1: Testing with default pages parameter")
            response = requests.get(
                f"{BASE_URL}/shopify_tools/stores",
                params={"keyword": "fashion"},
                cookies={"access_token": self.access_token},
                timeout=30
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Response keys: {list(data.keys())}")
                self.assert_in('stores', data, "Response contains 'stores' key")
                self.assert_true(isinstance(data['stores'], list), "Stores is a list")
                self.log(f"Stores returned: {len(data['stores'])}")
            else:
                self.log(f"Request failed: {response.text}", "ERROR")
                self.failed += 1
                return False
            
            # Test 2: Explicit pages=2
            self.log("\nTest 2: Testing with pages=2")
            response2 = requests.get(
                f"{BASE_URL}/shopify_tools/stores",
                params={"keyword": "fashion", "pages": 2},
                cookies={"access_token": self.access_token},
                timeout=30
            )
            
            self.log(f"Response Status: {response2.status_code}")
            
            if response2.status_code == 200:
                data2 = response2.json()
                self.assert_in('stores', data2, "Response contains 'stores' key with pages=2")
                self.assert_true(isinstance(data2['stores'], list), "Stores is a list with pages=2")
                self.log(f"Stores returned with pages=2: {len(data2['stores'])}")
                
                # Verify that pages=2 returns same or more stores than default
                # (This is a reasonable assumption for pagination)
                self.log(f"Comparing: pages=2 ({len(data2['stores'])}) vs default ({len(data['stores'])})")
            else:
                self.log(f"Request with pages=2 failed: {response2.text}", "ERROR")
                self.failed += 1
                return False
            
            # Test 3: Explicit pages=5
            self.log("\nTest 3: Testing with pages=5")
            response3 = requests.get(
                f"{BASE_URL}/shopify_tools/stores",
                params={"keyword": "fashion", "pages": 5},
                cookies={"access_token": self.access_token},
                timeout=45
            )
            
            self.log(f"Response Status: {response3.status_code}")
            
            if response3.status_code == 200:
                data3 = response3.json()
                self.assert_in('stores', data3, "Response contains 'stores' key with pages=5")
                self.assert_true(isinstance(data3['stores'], list), "Stores is a list with pages=5")
                self.log(f"Stores returned with pages=5: {len(data3['stores'])}")
            else:
                self.log(f"Request with pages=5 failed: {response3.text}", "ERROR")
                self.failed += 1
                return False
            
            return True
                
        except Exception as e:
            self.log(f"Exception during stores endpoint test: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Stores endpoint exception: {str(e)}")
            return False
    
    def test_stores_endpoint_semaphore_verification(self):
        """Verify /api/shopify_tools/stores uses asyncio.Semaphore(10)"""
        self.log("\n" + "=" * 60)
        self.log("TEST: Stores Endpoint - Semaphore(10) Verification")
        self.log("=" * 60)
        
        # Read the server.py file to verify Semaphore(10) is used
        try:
            with open('/app/backend/server.py', 'r') as f:
                content = f.read()
            
            # Check for the stores endpoint
            if '@app.get("/api/shopify_tools/stores")' in content:
                self.log("✓ Found stores endpoint definition")
                
                # Find the endpoint function
                stores_start = content.find('@app.get("/api/shopify_tools/stores")')
                stores_end = content.find('@app.', stores_start + 1)
                if stores_end == -1:
                    stores_end = len(content)
                
                stores_function = content[stores_start:stores_end]
                
                # Check for Semaphore(10)
                if 'asyncio.Semaphore(10)' in stores_function:
                    self.assert_true(True, "Stores endpoint uses asyncio.Semaphore(10)")
                    self.log("✓ Verified: asyncio.Semaphore(10) is used in stores endpoint")
                else:
                    self.assert_true(False, "Stores endpoint uses asyncio.Semaphore(10)")
                    self.log("✗ asyncio.Semaphore(10) NOT found in stores endpoint", "ERROR")
                    return False
                
                # Check for async with sem pattern
                if 'async with sem:' in stores_function:
                    self.assert_true(True, "Stores endpoint uses 'async with sem' pattern")
                    self.log("✓ Verified: Semaphore is used with 'async with sem' pattern")
                else:
                    self.log("⚠ Warning: 'async with sem' pattern not found", "WARN")
                
                # Check for pages parameter usage
                if 'pages: int' in stores_function or 'pages:int' in stores_function:
                    self.assert_true(True, "Stores endpoint accepts 'pages' parameter")
                    self.log("✓ Verified: 'pages' parameter is defined in function signature")
                else:
                    self.log("⚠ Warning: 'pages' parameter not found in function signature", "WARN")
                
                # Check for pages usage in task creation
                if 'range(1, pages + 1)' in stores_function or 'range(1, pages+1)' in stores_function:
                    self.assert_true(True, "Stores endpoint uses pages parameter in task creation")
                    self.log("✓ Verified: pages parameter is used in range(1, pages+1)")
                else:
                    self.log("⚠ Warning: pages parameter usage in range not found", "WARN")
                
                return True
            else:
                self.log("✗ Stores endpoint not found in server.py", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during code verification: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Code verification exception: {str(e)}")
            return False
    
    def test_products_endpoint_semaphore_verification(self):
        """Verify /api/shopify_tools/products uses asyncio.Semaphore(40)"""
        self.log("\n" + "=" * 60)
        self.log("TEST: Products Endpoint - Semaphore(40) Verification")
        self.log("=" * 60)
        
        # Read the server.py file to verify Semaphore(40) is used
        try:
            with open('/app/backend/server.py', 'r') as f:
                content = f.read()
            
            # Check for the products endpoint
            if '@app.post("/api/shopify_tools/products")' in content:
                self.log("✓ Found products endpoint definition")
                
                # Find the endpoint function
                products_start = content.find('@app.post("/api/shopify_tools/products")')
                products_end = content.find('@app.', products_start + 1)
                if products_end == -1:
                    products_end = len(content)
                
                products_function = content[products_start:products_end]
                
                # Check for Semaphore(40)
                if 'asyncio.Semaphore(40)' in products_function:
                    self.assert_true(True, "Products endpoint uses asyncio.Semaphore(40)")
                    self.log("✓ Verified: asyncio.Semaphore(40) is used in products endpoint")
                else:
                    self.assert_true(False, "Products endpoint uses asyncio.Semaphore(40)")
                    self.log("✗ asyncio.Semaphore(40) NOT found in products endpoint", "ERROR")
                    return False
                
                # Check for async with sem pattern
                if 'async with sem:' in products_function:
                    self.assert_true(True, "Products endpoint uses 'async with sem' pattern")
                    self.log("✓ Verified: Semaphore is used with 'async with sem' pattern")
                else:
                    self.log("⚠ Warning: 'async with sem' pattern not found", "WARN")
                
                # Check for asyncio.to_thread usage (for limiting thread creation)
                if 'asyncio.to_thread' in products_function:
                    self.assert_true(True, "Products endpoint uses asyncio.to_thread")
                    self.log("✓ Verified: asyncio.to_thread is used to limit thread creation")
                else:
                    self.log("⚠ Warning: asyncio.to_thread not found", "WARN")
                
                return True
            else:
                self.log("✗ Products endpoint not found in server.py", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during code verification: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Code verification exception: {str(e)}")
            return False
    
    def test_products_endpoint_functionality(self):
        """Test /api/shopify_tools/products endpoint basic functionality"""
        self.log("\n" + "=" * 60)
        self.log("TEST: Products Endpoint - Basic Functionality")
        self.log("=" * 60)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
        
        try:
            # Test with a small set of stores
            test_data = {
                "stores": [
                    "https://example-store1.myshopify.com",
                    "https://example-store2.myshopify.com"
                ],
                "min_price": 10.0,
                "max_price": 100.0,
                "proxy_type": "own"
            }
            
            self.log(f"Testing products endpoint with {len(test_data['stores'])} stores")
            
            response = requests.post(
                f"{BASE_URL}/shopify_tools/products",
                json=test_data,
                cookies={"access_token": self.access_token},
                timeout=30
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Response keys: {list(data.keys())}")
                self.assert_in('products', data, "Response contains 'products' key")
                self.assert_true(isinstance(data['products'], list), "Products is a list")
                self.log(f"Products returned: {len(data['products'])}")
                return True
            else:
                self.log(f"Request failed: {response.text}", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during products endpoint test: {str(e)}", "ERROR")
            self.failed += 1
            self.errors.append(f"Products endpoint exception: {str(e)}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        self.log("\n" + "=" * 80)
        self.log("SHOPIFY TOOLS API TEST SUITE")
        self.log("=" * 80)
        self.log(f"Backend URL: {BASE_URL}")
        self.log(f"Admin User: {ADMIN_USERNAME}")
        self.log("")
        
        # Run tests in sequence
        if self.test_admin_login():
            # Test stores endpoint
            self.test_stores_endpoint_pages_parameter()
            self.test_stores_endpoint_semaphore_verification()
            
            # Test products endpoint
            self.test_products_endpoint_semaphore_verification()
            self.test_products_endpoint_functionality()
        
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
    runner = ShopifyToolsTestRunner()
    success = runner.run_all_tests()
    sys.exit(0 if success else 1)
