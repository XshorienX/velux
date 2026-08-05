#!/usr/bin/env python3
"""
Unit Test for Error Masking in /api/checker/run endpoint
Tests the exception handling logic directly by simulating exceptions
"""

import sys
import os
sys.path.insert(0, '/app/backend')

# Mock the database and dependencies before importing server
from unittest.mock import MagicMock, patch, AsyncMock
import asyncio

# Create mock database
mock_db = MagicMock()
mock_db.users = MagicMock()
mock_db.proxies = MagicMock()

# Mock user data
mock_user = {
    "_id": "test_user_id",
    "username": "testuser",
    "role": "admin",
    "plan": "premium",
    "credits": 1000,
    "status": "active"
}

async def mock_find_cursor():
    cursor = MagicMock()
    cursor.to_list = AsyncMock(return_value=[])
    return cursor

mock_db.proxies.find = MagicMock(return_value=mock_find_cursor())

class TestErrorMasking:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def log(self, message, level="INFO"):
        print(f"[{level}] {message}")
    
    def assert_true(self, condition, test_name, details=""):
        if condition:
            self.passed += 1
            self.log(f"✅ PASS: {test_name}", "PASS")
            return True
        else:
            self.failed += 1
            error_msg = f"❌ FAIL: {test_name}"
            if details:
                error_msg += f" - {details}"
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
            error_msg = f"❌ FAIL: {test_name} - '{value}' not found"
            self.log(error_msg, "FAIL")
            self.errors.append(error_msg)
            return False
    
    def assert_not_in(self, value, container, test_name):
        if value not in container:
            self.passed += 1
            self.log(f"✅ PASS: {test_name}", "PASS")
            return True
        else:
            self.failed += 1
            error_msg = f"❌ FAIL: {test_name} - '{value}' should not be present"
            self.log(error_msg, "FAIL")
            self.errors.append(error_msg)
            return False
    
    async def test_api_error_masking(self):
        """Test that exceptions containing 'api.barryxapi.xyz' are masked"""
        self.log("=" * 70)
        self.log("TEST: Exception with 'api.barryxapi.xyz' is masked")
        self.log("=" * 70)
        
        # Import server module with mocked dependencies
        with patch('server.db', mock_db):
            from server import run_checker, CheckerRequest
            
            # Mock requests to raise an exception with api.barryxapi.xyz in it
            with patch('server.requests') as mock_requests:
                # Simulate a connection error that includes the API URL
                mock_requests.get.side_effect = Exception("Connection failed to api.barryxapi.xyz: timeout")
                
                # Create request
                req = CheckerRequest(
                    gateway="stripe",
                    card="4111111111111111|12|2025|123",
                    sk_type="own_sk",
                    sk="sk_test_123",
                    no_proxy=True
                )
                
                # Call the endpoint
                result = await run_checker(req, mock_user)
                
                self.log(f"Result: {result}")
                
                # Verify the response
                self.assert_true("message" in result, "Response contains 'message' field")
                
                if "message" in result:
                    message = result["message"]
                    self.log(f"Error message: {message}")
                    
                    # Check that it's masked with "Api Error"
                    self.assert_in("Api Error", message, 
                                 "Error message starts with 'Api Error'")
                    
                    # Check that the URL is NOT exposed
                    self.assert_not_in("api.barryxapi.xyz", message,
                                     "URL 'api.barryxapi.xyz' is not exposed in error message")
                    
                    # Check for the masked message
                    self.assert_in("Gateway connection timeout or unavailable", message,
                                 "Contains masked error description")
                    
                    # Ensure it's NOT an "Engine Error"
                    self.assert_not_in("Engine Error", message,
                                     "Does not use 'Engine Error' prefix")
                
                return True
    
    async def test_other_error_not_masked(self):
        """Test that other exceptions are NOT masked and use Engine Error"""
        self.log("\n" + "=" * 70)
        self.log("TEST: Other exceptions use 'Engine Error' prefix")
        self.log("=" * 70)
        
        with patch('server.db', mock_db):
            from server import run_checker, CheckerRequest
            
            # Mock requests to raise a different exception
            with patch('server.requests') as mock_requests:
                mock_requests.get.side_effect = Exception("Some other error occurred")
                
                req = CheckerRequest(
                    gateway="stripe",
                    card="4111111111111111|12|2025|123",
                    sk_type="own_sk",
                    sk="sk_test_123",
                    no_proxy=True
                )
                
                result = await run_checker(req, mock_user)
                
                self.log(f"Result: {result}")
                
                if "message" in result:
                    message = result["message"]
                    self.log(f"Error message: {message}")
                    
                    # Should use "Engine Error" for non-API errors
                    self.assert_in("Engine Error", message,
                                 "Uses 'Engine Error' prefix for non-API errors")
                    
                    # Should contain the actual error message
                    self.assert_in("Some other error occurred", message,
                                 "Contains the actual error message")
                
                return True
    
    async def test_timeout_error_masking(self):
        """Test that timeout errors with API URL are masked"""
        self.log("\n" + "=" * 70)
        self.log("TEST: Timeout errors with API URL are masked")
        self.log("=" * 70)
        
        with patch('server.db', mock_db):
            from server import run_checker, CheckerRequest
            import requests
            
            # Mock requests to raise a timeout with API URL
            with patch('server.requests') as mock_requests:
                mock_requests.get.side_effect = requests.exceptions.Timeout(
                    "HTTPSConnectionPool(host='api.barryxapi.xyz', port=443): Read timed out."
                )
                
                req = CheckerRequest(
                    gateway="stripe",
                    card="4111111111111111|12|2025|123",
                    sk_type="own_sk",
                    sk="sk_test_123",
                    no_proxy=True
                )
                
                result = await run_checker(req, mock_user)
                
                self.log(f"Result: {result}")
                
                if "message" in result:
                    message = result["message"]
                    self.log(f"Error message: {message}")
                    
                    # Should be masked
                    self.assert_in("Api Error", message,
                                 "Timeout errors with API URL are masked")
                    
                    self.assert_not_in("api.barryxapi.xyz", message,
                                     "API URL is not exposed in timeout errors")
                
                return True
    
    async def run_all_tests(self):
        """Run all tests"""
        self.log("\n" + "=" * 80)
        self.log("UNIT TEST SUITE - Error Masking in /api/checker/run")
        self.log("=" * 80)
        self.log("Testing exception handling logic for API URL masking")
        self.log("")
        
        try:
            await self.test_api_error_masking()
            await self.test_other_error_not_masked()
            await self.test_timeout_error_masking()
        except Exception as e:
            self.log(f"Test execution error: {str(e)}", "ERROR")
            self.failed += 1
        
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
    tester = TestErrorMasking()
    success = asyncio.run(tester.run_all_tests())
    sys.exit(0 if success else 1)
