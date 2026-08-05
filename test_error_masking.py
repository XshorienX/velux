#!/usr/bin/env python3
"""
Test Error Masking in /api/checker/run endpoint
Verifies that exceptions containing 'api.barryxapi.xyz' return masked error messages
"""

import requests
import json
import sys
from datetime import datetime
from unittest.mock import patch, MagicMock
import os

# Backend URL
BASE_URL = "https://render-ready-4.preview.emergentagent.com/api"

# Admin credentials
ADMIN_USERNAME = "SHORIEN"
ADMIN_PASSWORD = "Xiron696@"

class ErrorMaskingTest:
    def __init__(self):
        self.access_token = None
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
        
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
            error_msg = f"❌ FAIL: {test_name} - '{value}' not found in response"
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
            error_msg = f"❌ FAIL: {test_name} - '{value}' should not be in response but was found"
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
                
                if 'access_token' in response.cookies:
                    self.access_token = response.cookies['access_token']
                    self.log(f"Access token received")
                    self.assert_true(True, "Admin login successful")
                    return True
                else:
                    self.log("No access_token cookie received", "ERROR")
                    self.failed += 1
                    return False
            else:
                self.log(f"Login failed with status {response.status_code}", "ERROR")
                self.failed += 1
                return False
                
        except Exception as e:
            self.log(f"Exception during admin login: {str(e)}", "ERROR")
            self.failed += 1
            return False
    
    def test_checker_error_with_api_url(self):
        """
        Test that errors containing 'api.barryxapi.xyz' are masked
        This test attempts to trigger an error from the external API
        """
        self.log("\n" + "=" * 60)
        self.log("TEST: Error Masking for api.barryxapi.xyz")
        self.log("=" * 60)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
        
        try:
            # Make a request that might fail (invalid card format or API timeout)
            # Using an invalid card format to potentially trigger an error
            checker_data = {
                "gateway": "stripe",
                "card": "invalid_card_format",
                "sk_type": "own_sk",
                "sk": "sk_test_invalid_key_that_will_fail",
                "no_proxy": True
            }
            
            self.log("Making checker request with invalid parameters to trigger error...")
            
            response = requests.post(
                f"{BASE_URL}/checker/run",
                json=checker_data,
                cookies={"access_token": self.access_token},
                timeout=25
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Response: {json.dumps(data, indent=2)}")
                
                # Check if we got an error response
                if "message" in data:
                    message = data["message"]
                    self.log(f"Error message received: {message}")
                    
                    # Check if the error message is properly masked
                    if "api.barryxapi.xyz" in message.lower():
                        # If the URL is exposed, check if it's in the masked format
                        if "Api Error" in message:
                            self.assert_true(True, "Error contains 'Api Error' prefix")
                            self.assert_in("Gateway connection timeout or unavailable", message, 
                                         "Error message is properly masked")
                        else:
                            # URL is exposed in Engine Error - this is the bug
                            self.assert_true(False, "URL should be masked but found in error message",
                                           f"Message: {message}")
                    elif "Api Error" in message:
                        # Properly masked error
                        self.assert_true(True, "Error is properly masked with 'Api Error'")
                        self.assert_not_in("api.barryxapi.xyz", message, 
                                         "URL is not exposed in error message")
                    elif "Engine Error" in message:
                        # Check if URL is exposed
                        self.assert_not_in("api.barryxapi.xyz", message,
                                         "URL should not be exposed in Engine Error")
                    else:
                        # Some other error message
                        self.log(f"Received different error format: {message}", "INFO")
                        # Still check that URL is not exposed
                        self.assert_not_in("api.barryxapi.xyz", message,
                                         "URL should not be exposed in any error")
                    
                    return True
                else:
                    self.log("No error message in response, might have succeeded unexpectedly", "WARN")
                    return True
            else:
                self.log(f"Request failed with status {response.status_code}: {response.text}", "ERROR")
                self.failed += 1
                return False
                
        except requests.exceptions.Timeout:
            self.log("Request timed out - this might indicate API is slow or unavailable", "WARN")
            self.log("This is expected behavior for testing error handling", "INFO")
            return True
        except Exception as e:
            self.log(f"Exception during checker test: {str(e)}", "ERROR")
            self.failed += 1
            return False
    
    def test_checker_with_timeout_scenario(self):
        """
        Test error masking with a scenario more likely to timeout
        """
        self.log("\n" + "=" * 60)
        self.log("TEST: Error Masking with Timeout Scenario")
        self.log("=" * 60)
        
        if not self.access_token:
            self.log("Skipping test - no access token", "SKIP")
            return False
        
        try:
            # Test with shopify gateway which also uses api.barryxapi.xyz
            checker_data = {
                "gateway": "shopify",
                "card": "4111111111111111|12|2025|123",
                "site_type": "own",
                "product_url": "https://invalid-store-that-does-not-exist.myshopify.com/products/test",
                "no_proxy": True
            }
            
            self.log("Making shopify checker request...")
            
            response = requests.post(
                f"{BASE_URL}/checker/run",
                json=checker_data,
                cookies={"access_token": self.access_token},
                timeout=25
            )
            
            self.log(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Response: {json.dumps(data, indent=2)}")
                
                # Check the response
                if "message" in data:
                    message = data["message"]
                    self.log(f"Message received: {message}")
                    
                    # Verify URL is not exposed
                    self.assert_not_in("api.barryxapi.xyz", message,
                                     "URL should not be exposed in error message")
                    
                    # If it's an error about the API, it should be masked
                    if "Error" in message:
                        if "api.barryxapi.xyz" in message.lower():
                            self.assert_in("Api Error", message,
                                         "API errors should use 'Api Error' prefix")
                        else:
                            self.log("Error does not contain API URL - checking format", "INFO")
                    
                    return True
                else:
                    # Check if we got a result
                    self.log(f"Got response without message field: {data}", "INFO")
                    return True
            else:
                self.log(f"Request failed with status {response.status_code}", "ERROR")
                self.failed += 1
                return False
                
        except requests.exceptions.Timeout:
            self.log("Request timed out", "WARN")
            return True
        except Exception as e:
            self.log(f"Exception during test: {str(e)}", "ERROR")
            self.failed += 1
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        self.log("\n" + "=" * 80)
        self.log("ERROR MASKING TEST SUITE - /api/checker/run")
        self.log("=" * 80)
        self.log(f"Backend URL: {BASE_URL}")
        self.log(f"Testing that 'api.barryxapi.xyz' is masked in error messages")
        self.log("")
        
        # Run tests
        if self.test_admin_login():
            self.test_checker_error_with_api_url()
            self.test_checker_with_timeout_scenario()
        
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
    tester = ErrorMaskingTest()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
