"""
Test to verify that check_givewp_stripe extracts and includes Charge ID or Payment Intent ID
in the response message when receiving 'succeeded' or 'requires_action' status from Stripe.
"""

import sys
import unittest
from unittest.mock import patch, MagicMock
sys.path.insert(0, '/app/backend')

from server import check_givewp_stripe


class TestChargeIdExtraction(unittest.TestCase):
    """Test Charge ID / Payment Intent ID extraction in approved responses"""
    
    @patch('server.requests.Session')
    def test_succeeded_status_with_charge_id_in_charges_data(self, mock_session_class):
        """Test that when status is 'succeeded' and charge ID is in charges.data[0].id, it's extracted and included in response"""
        # Mock the session and responses
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock Step 0 response (get donation form)
        mock_res0 = MagicMock()
        mock_res0.text = '''
        <script>
        window.givewpDonationFormExports = {"donateUrl": "https://changesbristol.org.uk/donate"};
        </script>
        '''
        
        # Mock Step 2 response (create payment intent)
        mock_res2 = MagicMock()
        mock_res2.json.return_value = {
            "data": {
                "clientSecret": "pi_test123_secret_abc",
                "returnUrl": "https://changesbristol.org.uk/return"
            }
        }
        
        # Mock Step 3 response (confirm payment) - SUCCEEDED with Charge ID in charges.data
        mock_res3 = MagicMock()
        mock_res3.json.return_value = {
            "status": "succeeded",
            "id": "pi_test123",
            "charges": {
                "data": [
                    {
                        "id": "ch_test456",
                        "amount": 500,
                        "status": "succeeded"
                    }
                ]
            }
        }
        
        # Configure mock session to return these responses in sequence
        mock_session.get.side_effect = [mock_res0, MagicMock()]  # Step 0 and Step 1
        mock_session.post.side_effect = [mock_res2, mock_res3]  # Step 2 and Step 3
        
        # Call the function
        result = check_givewp_stripe("4242424242424242|12|2025|123", "")
        
        # Verify the result
        self.assertEqual(result["result"]["status"], "APPROVED")
        self.assertIn("ID: ch_test456", result["result"]["message"])
        self.assertIn("Charged / Approved £5", result["result"]["message"])
        print(f"✓ Test 1 PASSED: Charge ID extracted from charges.data[0].id: {result['result']['message']}")
    
    @patch('server.requests.Session')
    def test_succeeded_status_with_payment_intent_id_fallback(self, mock_session_class):
        """Test that when status is 'succeeded' but no charge ID in charges.data, it falls back to payment intent ID"""
        # Mock the session and responses
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock Step 0 response
        mock_res0 = MagicMock()
        mock_res0.text = '''
        <script>
        window.givewpDonationFormExports = {"donateUrl": "https://changesbristol.org.uk/donate"};
        </script>
        '''
        
        # Mock Step 2 response
        mock_res2 = MagicMock()
        mock_res2.json.return_value = {
            "data": {
                "clientSecret": "pi_test789_secret_xyz",
                "returnUrl": "https://changesbristol.org.uk/return"
            }
        }
        
        # Mock Step 3 response - SUCCEEDED but no charges.data (fallback to payment intent ID)
        mock_res3 = MagicMock()
        mock_res3.json.return_value = {
            "status": "succeeded",
            "id": "pi_test789",
            "charges": {
                "data": []  # Empty charges array - should fallback to payment intent ID
            }
        }
        
        # Configure mock session
        mock_session.get.side_effect = [mock_res0, MagicMock()]
        mock_session.post.side_effect = [mock_res2, mock_res3]
        
        # Call the function
        result = check_givewp_stripe("4242424242424242|12|2025|123", "")
        
        # Verify the result
        self.assertEqual(result["result"]["status"], "APPROVED")
        self.assertIn("ID: pi_test789", result["result"]["message"])
        self.assertIn("Charged / Approved £5", result["result"]["message"])
        print(f"✓ Test 2 PASSED: Payment Intent ID used as fallback: {result['result']['message']}")
    
    @patch('server.requests.Session')
    def test_requires_action_status_with_charge_id(self, mock_session_class):
        """Test that when status is 'requires_action', charge ID is still extracted and included"""
        # Mock the session and responses
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock Step 0 response
        mock_res0 = MagicMock()
        mock_res0.text = '''
        <script>
        window.givewpDonationFormExports = {"donateUrl": "https://changesbristol.org.uk/donate"};
        </script>
        '''
        
        # Mock Step 2 response
        mock_res2 = MagicMock()
        mock_res2.json.return_value = {
            "data": {
                "clientSecret": "pi_test999_secret_zzz",
                "returnUrl": "https://changesbristol.org.uk/return"
            }
        }
        
        # Mock Step 3 response - REQUIRES_ACTION with Charge ID
        mock_res3 = MagicMock()
        mock_res3.json.return_value = {
            "status": "requires_action",
            "id": "pi_test999",
            "charges": {
                "data": [
                    {
                        "id": "ch_test888",
                        "amount": 500,
                        "status": "pending"
                    }
                ]
            }
        }
        
        # Configure mock session
        mock_session.get.side_effect = [mock_res0, MagicMock()]
        mock_session.post.side_effect = [mock_res2, mock_res3]
        
        # Call the function
        result = check_givewp_stripe("4242424242424242|12|2025|123", "")
        
        # Verify the result
        self.assertEqual(result["result"]["status"], "APPROVED")
        self.assertIn("ID: ch_test888", result["result"]["message"])
        self.assertIn("Charged / Approved £5", result["result"]["message"])
        print(f"✓ Test 3 PASSED: Charge ID extracted for 'requires_action' status: {result['result']['message']}")
    
    @patch('server.requests.Session')
    def test_succeeded_status_without_any_id(self, mock_session_class):
        """Test that when status is 'succeeded' but no IDs are available, message is still returned without ID"""
        # Mock the session and responses
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock Step 0 response
        mock_res0 = MagicMock()
        mock_res0.text = '''
        <script>
        window.givewpDonationFormExports = {"donateUrl": "https://changesbristol.org.uk/donate"};
        </script>
        '''
        
        # Mock Step 2 response
        mock_res2 = MagicMock()
        mock_res2.json.return_value = {
            "data": {
                "clientSecret": "pi_test111_secret_aaa",
                "returnUrl": "https://changesbristol.org.uk/return"
            }
        }
        
        # Mock Step 3 response - SUCCEEDED but no charges and no id field
        mock_res3 = MagicMock()
        mock_res3.json.return_value = {
            "status": "succeeded",
            # No "id" field
            # No "charges" field
        }
        
        # Configure mock session
        mock_session.get.side_effect = [mock_res0, MagicMock()]
        mock_session.post.side_effect = [mock_res2, mock_res3]
        
        # Call the function
        result = check_givewp_stripe("4242424242424242|12|2025|123", "")
        
        # Verify the result
        self.assertEqual(result["result"]["status"], "APPROVED")
        self.assertEqual(result["result"]["message"], "Charged / Approved £5")
        self.assertNotIn("ID:", result["result"]["message"])
        print(f"✓ Test 4 PASSED: Message without ID when no IDs available: {result['result']['message']}")
    
    @patch('server.requests.Session')
    def test_requires_action_with_payment_intent_id_only(self, mock_session_class):
        """Test that 'requires_action' status with only payment intent ID (no charges) uses fallback"""
        # Mock the session and responses
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Mock Step 0 response
        mock_res0 = MagicMock()
        mock_res0.text = '''
        <script>
        window.givewpDonationFormExports = {"donateUrl": "https://changesbristol.org.uk/donate"};
        </script>
        '''
        
        # Mock Step 2 response
        mock_res2 = MagicMock()
        mock_res2.json.return_value = {
            "data": {
                "clientSecret": "pi_test222_secret_bbb",
                "returnUrl": "https://changesbristol.org.uk/return"
            }
        }
        
        # Mock Step 3 response - REQUIRES_ACTION with only payment intent ID
        mock_res3 = MagicMock()
        mock_res3.json.return_value = {
            "status": "requires_action",
            "id": "pi_test222"
            # No "charges" field - should fallback to payment intent ID
        }
        
        # Configure mock session
        mock_session.get.side_effect = [mock_res0, MagicMock()]
        mock_session.post.side_effect = [mock_res2, mock_res3]
        
        # Call the function
        result = check_givewp_stripe("4242424242424242|12|2025|123", "")
        
        # Verify the result
        self.assertEqual(result["result"]["status"], "APPROVED")
        self.assertIn("ID: pi_test222", result["result"]["message"])
        self.assertIn("Charged / Approved £5", result["result"]["message"])
        print(f"✓ Test 5 PASSED: Payment Intent ID used for 'requires_action' when no charges: {result['result']['message']}")


if __name__ == "__main__":
    print("\n" + "="*80)
    print("Testing Charge ID / Payment Intent ID Extraction in check_givewp_stripe")
    print("="*80 + "\n")
    
    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestChargeIdExtraction)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print(f"Total tests: {result.testsRun}")
    print(f"Passed: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED - Charge ID / Payment Intent ID extraction is working correctly!")
        print("\nVERIFICATION COMPLETE:")
        print("1. When status is 'succeeded' or 'requires_action', the function extracts Charge ID from charges.data[0].id")
        print("2. If no Charge ID in charges.data, it falls back to Payment Intent ID from response.id")
        print("3. The extracted ID is dynamically included in the response message: 'Charged / Approved £5 (ID: {charge_id})'")
        print("4. If no ID is available, the message is returned without ID: 'Charged / Approved £5'")
    else:
        print("\n✗ SOME TESTS FAILED - Review the failures above")
    
    print("="*80 + "\n")
    
    sys.exit(0 if result.wasSuccessful() else 1)
