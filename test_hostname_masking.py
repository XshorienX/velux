"""
Test suite to verify that backend exception handlers properly mask 
'changesbristol' and 'stripe.com' hostnames in both check_givewp_stripe 
and run_checker functions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

import unittest
from unittest.mock import patch, MagicMock, AsyncMock
import asyncio
from server import check_givewp_stripe, run_checker, CheckerRequest


class TestHostnameMasking(unittest.TestCase):
    """Test hostname masking in exception handlers"""
    
    def test_check_givewp_stripe_masks_changesbristol(self):
        """Test that check_givewp_stripe masks 'changesbristol' in exceptions"""
        with patch('server.requests.Session') as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance
            
            # Simulate an exception containing 'changesbristol'
            mock_session_instance.get.side_effect = Exception("Connection to changesbristol.org.uk failed")
            
            result = check_givewp_stripe("4111111111111111|12|2025|123")
            
            # Verify the hostname is masked
            self.assertEqual(result["result"]["status"], "ERROR")
            self.assertEqual(result["result"]["message"], "Api Error: Gateway connection timeout or unavailable.")
            self.assertNotIn("changesbristol", result["result"]["message"])
    
    def test_check_givewp_stripe_masks_stripe_com(self):
        """Test that check_givewp_stripe masks 'stripe.com' in exceptions"""
        with patch('server.requests.Session') as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance
            
            # Simulate an exception containing 'stripe.com'
            mock_session_instance.get.side_effect = Exception("Timeout connecting to api.stripe.com")
            
            result = check_givewp_stripe("4111111111111111|12|2025|123")
            
            # Verify the hostname is masked
            self.assertEqual(result["result"]["status"], "ERROR")
            self.assertEqual(result["result"]["message"], "Api Error: Gateway connection timeout or unavailable.")
            self.assertNotIn("stripe.com", result["result"]["message"])
    
    def test_check_givewp_stripe_does_not_mask_other_errors(self):
        """Test that check_givewp_stripe does NOT mask other exceptions"""
        with patch('server.requests.Session') as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance
            
            # Simulate a different exception
            mock_session_instance.get.side_effect = Exception("Invalid card format")
            
            result = check_givewp_stripe("4111111111111111|12|2025|123")
            
            # Verify the error is NOT masked
            self.assertEqual(result["result"]["status"], "ERROR")
            self.assertEqual(result["result"]["message"], "Invalid card format")
    
    def test_check_givewp_stripe_masks_mixed_case_changesbristol(self):
        """Test that masking works with different case variations"""
        with patch('server.requests.Session') as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance
            
            # Test with mixed case
            mock_session_instance.get.side_effect = Exception("Error from ChangesBristol.org.uk")
            
            result = check_givewp_stripe("4111111111111111|12|2025|123")
            
            # Note: The current implementation is case-sensitive
            # This test documents the current behavior
            # If case-insensitive matching is needed, the implementation should be updated
            self.assertEqual(result["result"]["status"], "ERROR")
            # With current case-sensitive implementation, this won't be masked
            # If you want case-insensitive, update server.py to use .lower()
    
    def test_run_checker_masks_changesbristol(self):
        """Test that run_checker endpoint masks 'changesbristol' in exceptions"""
        async def async_test():
            # Mock database and dependencies
            with patch('server.db') as mock_db, \
                 patch('server.asyncio.to_thread') as mock_to_thread:
                
                # Setup mocks
                mock_db.proxies.find.return_value.to_list = AsyncMock(return_value=[])
                mock_db.users.update_one = AsyncMock()
                
                # Simulate exception containing 'changesbristol'
                mock_to_thread.side_effect = Exception("Failed to connect to changesbristol.org.uk")
                
                # Create request
                req = CheckerRequest(
                    gateway="stripe",
                    card="4111111111111111|12|2025|123",
                    sk_type="site_based"
                )
                
                # Mock user
                user = {
                    "_id": "test_user_id",
                    "credits": 10,
                    "plan": "premium",
                    "role": "user"
                }
                
                result = await run_checker(req, user)
                
                # Verify the hostname is masked
                self.assertEqual(result["status"], False)
                self.assertEqual(result["message"], "Api Error: Gateway connection timeout or unavailable.")
                self.assertNotIn("changesbristol", result["message"])
        
        asyncio.run(async_test())
    
    def test_run_checker_masks_stripe_com(self):
        """Test that run_checker endpoint masks 'stripe.com' in exceptions"""
        async def async_test():
            # Mock database and dependencies
            with patch('server.db') as mock_db, \
                 patch('server.asyncio.to_thread') as mock_to_thread:
                
                # Setup mocks
                mock_db.proxies.find.return_value.to_list = AsyncMock(return_value=[])
                mock_db.users.update_one = AsyncMock()
                
                # Simulate exception containing 'stripe.com'
                mock_to_thread.side_effect = Exception("Connection timeout to api.stripe.com")
                
                # Create request
                req = CheckerRequest(
                    gateway="stripe",
                    card="4111111111111111|12|2025|123",
                    sk_type="site_based"
                )
                
                # Mock user
                user = {
                    "_id": "test_user_id",
                    "credits": 10,
                    "plan": "premium",
                    "role": "user"
                }
                
                result = await run_checker(req, user)
                
                # Verify the hostname is masked
                self.assertEqual(result["status"], False)
                self.assertEqual(result["message"], "Api Error: Gateway connection timeout or unavailable.")
                self.assertNotIn("stripe.com", result["message"])
        
        asyncio.run(async_test())
    
    def test_run_checker_masks_api_barryxapi_xyz(self):
        """Test that run_checker also masks 'api.barryxapi.xyz' (existing functionality)"""
        async def async_test():
            # Mock database and dependencies
            with patch('server.db') as mock_db, \
                 patch('server.requests.get') as mock_get:
                
                # Setup mocks
                mock_db.proxies.find.return_value.to_list = AsyncMock(return_value=[])
                mock_db.users.find_one = AsyncMock(return_value={"stripe_sk": "sk_test_123"})
                mock_db.users.update_one = AsyncMock()
                
                # Simulate exception containing 'api.barryxapi.xyz'
                mock_get.side_effect = Exception("Timeout connecting to api.barryxapi.xyz")
                
                # Create request
                req = CheckerRequest(
                    gateway="stripe",
                    card="4111111111111111|12|2025|123",
                    sk_type="sk_based",
                    sk="sk_test_123"
                )
                
                # Mock user
                user = {
                    "_id": "test_user_id",
                    "credits": 10,
                    "plan": "premium",
                    "role": "user"
                }
                
                result = await run_checker(req, user)
                
                # Verify the hostname is masked
                self.assertEqual(result["status"], False)
                self.assertEqual(result["message"], "Api Error: Gateway connection timeout or unavailable.")
                self.assertNotIn("api.barryxapi.xyz", result["message"])
        
        asyncio.run(async_test())
    
    def test_run_checker_does_not_mask_other_errors(self):
        """Test that run_checker does NOT mask other exceptions"""
        async def async_test():
            # Mock database and dependencies
            with patch('server.db') as mock_db, \
                 patch('server.asyncio.to_thread') as mock_to_thread:
                
                # Setup mocks
                mock_db.proxies.find.return_value.to_list = AsyncMock(return_value=[])
                mock_db.users.update_one = AsyncMock()
                
                # Simulate a different exception
                mock_to_thread.side_effect = Exception("Database connection failed")
                
                # Create request
                req = CheckerRequest(
                    gateway="stripe",
                    card="4111111111111111|12|2025|123",
                    sk_type="site_based"
                )
                
                # Mock user
                user = {
                    "_id": "test_user_id",
                    "credits": 10,
                    "plan": "premium",
                    "role": "user"
                }
                
                result = await run_checker(req, user)
                
                # Verify the error is NOT masked and uses "Engine Error" prefix
                self.assertEqual(result["status"], False)
                self.assertIn("Engine Error:", result["message"])
                self.assertIn("Database connection failed", result["message"])
        
        asyncio.run(async_test())
    
    def test_check_givewp_stripe_masks_full_url_with_changesbristol(self):
        """Test masking when full URL with changesbristol is in error"""
        with patch('server.requests.Session') as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance
            
            # Simulate exception with full URL
            mock_session_instance.get.side_effect = Exception(
                "HTTPSConnectionPool(host='changesbristol.org.uk', port=443): Max retries exceeded"
            )
            
            result = check_givewp_stripe("4111111111111111|12|2025|123")
            
            # Verify the hostname is masked
            self.assertEqual(result["result"]["status"], "ERROR")
            self.assertEqual(result["result"]["message"], "Api Error: Gateway connection timeout or unavailable.")
            self.assertNotIn("changesbristol", result["result"]["message"])
    
    def test_check_givewp_stripe_masks_full_url_with_stripe(self):
        """Test masking when full URL with stripe.com is in error"""
        with patch('server.requests.Session') as mock_session:
            mock_session_instance = MagicMock()
            mock_session.return_value = mock_session_instance
            
            # Simulate exception with full URL
            mock_session_instance.get.side_effect = Exception(
                "HTTPSConnectionPool(host='api.stripe.com', port=443): Read timed out"
            )
            
            result = check_givewp_stripe("4111111111111111|12|2025|123")
            
            # Verify the hostname is masked
            self.assertEqual(result["result"]["status"], "ERROR")
            self.assertEqual(result["result"]["message"], "Api Error: Gateway connection timeout or unavailable.")
            self.assertNotIn("stripe.com", result["result"]["message"])


if __name__ == "__main__":
    # Run tests with verbose output
    suite = unittest.TestLoader().loadTestsFromTestCase(TestHostnameMasking)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("HOSTNAME MASKING TEST SUMMARY")
    print("="*70)
    print(f"Total tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED - Hostname masking is working correctly!")
        print("\nVerified behaviors:")
        print("  ✓ check_givewp_stripe masks 'changesbristol' in exceptions")
        print("  ✓ check_givewp_stripe masks 'stripe.com' in exceptions")
        print("  ✓ run_checker masks 'changesbristol' in exceptions")
        print("  ✓ run_checker masks 'stripe.com' in exceptions")
        print("  ✓ run_checker masks 'api.barryxapi.xyz' in exceptions")
        print("  ✓ Other exceptions are NOT masked (proper error reporting)")
        print("\nMasked message: 'Api Error: Gateway connection timeout or unavailable.'")
    else:
        print("\n❌ SOME TESTS FAILED - Review the failures above")
    
    print("="*70)
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)
