"""
Tests for safe API response handling in the Pine Time App.
These tests focus on the safe_api_response_handler utility and related functions.
"""

import os
import sys
import unittest
import logging
from typing import Dict, Any, List, Optional, Union

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_safe_api_handling.log")
    ]
)
logger = logging.getLogger("test_safe_api_handling")

class TestSafeAPIHandling(unittest.TestCase):
    """Test safe API response handling."""
    
    def test_safe_api_response_handler_dict(self):
        """Test safe_api_response_handler with dictionary response."""
        # Import the function from user_app_postgres.py
        from admin_dashboard.user_app_postgres import safe_api_response_handler
        
        # Test with dictionary response
        response = {
            "items": [
                {"id": "1", "name": "Item 1"},
                {"id": "2", "name": "Item 2"}
            ],
            "total": 2,
            "page": 1,
            "size": 10
        }
        
        # Test with no key specified (should return the whole response)
        result = safe_api_response_handler(response)
        self.assertEqual(result, response)
        
        # Test with key specified
        result = safe_api_response_handler(response, key="items")
        self.assertEqual(result, response["items"])
        
        # Test with non-existent key
        result = safe_api_response_handler(response, key="non_existent")
        self.assertEqual(result, None)
        
        # Test with non-existent key and default value
        result = safe_api_response_handler(response, key="non_existent", default=[])
        self.assertEqual(result, [])
    
    def test_safe_api_response_handler_list(self):
        """Test safe_api_response_handler with list response."""
        # Import the function from user_app_postgres.py
        from admin_dashboard.user_app_postgres import safe_api_response_handler
        
        # Test with list response
        response = [
            {"id": "1", "name": "Item 1"},
            {"id": "2", "name": "Item 2"}
        ]
        
        # Test with no key specified (should return the whole response)
        result = safe_api_response_handler(response)
        self.assertEqual(result, response)
        
        # Test with key specified (should be ignored for list responses)
        result = safe_api_response_handler(response, key="items")
        self.assertEqual(result, response)
    
    def test_safe_api_response_handler_none(self):
        """Test safe_api_response_handler with None response."""
        # Import the function from user_app_postgres.py
        from admin_dashboard.user_app_postgres import safe_api_response_handler
        
        # Test with None response
        response = None
        
        # Test with no default specified
        result = safe_api_response_handler(response)
        self.assertEqual(result, None)
        
        # Test with default specified
        result = safe_api_response_handler(response, default=[])
        self.assertEqual(result, [])
    
    def test_safe_api_response_handler_empty(self):
        """Test safe_api_response_handler with empty response."""
        # Import the function from user_app_postgres.py
        from admin_dashboard.user_app_postgres import safe_api_response_handler
        
        # Test with empty dict
        response = {}
        
        # Test with key specified
        result = safe_api_response_handler(response, key="items")
        self.assertEqual(result, None)
        
        # Test with key specified and default
        result = safe_api_response_handler(response, key="items", default=[])
        self.assertEqual(result, [])
        
        # Test with empty list
        response = []
        
        # Test with no key specified
        result = safe_api_response_handler(response)
        self.assertEqual(result, [])
        
        # Test with default specified
        result = safe_api_response_handler(response, default=None)
        self.assertEqual(result, [])  # Should still return the empty list, not the default
    
    def test_safe_get_user_id(self):
        """Test safe_get_user_id function."""
        # Import the function if it exists
        try:
            from admin_dashboard.user_app_postgres import safe_get_user_id
            
            # Test with valid user object
            user = {"id": "user123"}
            result = safe_get_user_id(user)
            self.assertEqual(result, "user123")
            
            # Test with None user
            result = safe_get_user_id(None)
            self.assertEqual(result, None)
            
            # Test with user object missing id
            user = {"username": "testuser"}
            result = safe_get_user_id(user)
            self.assertEqual(result, None)
            
            # Test with default value
            result = safe_get_user_id(None, default="default_user")
            self.assertEqual(result, "default_user")
        except ImportError:
            # Function might not exist, skip test
            self.skipTest("safe_get_user_id function not found")
    
    def test_safe_get_current_user(self):
        """Test safe_get_current_user function."""
        # Import the function if it exists
        try:
            from admin_dashboard.user_app_postgres import safe_get_current_user
            
            # Mock streamlit session state
            import streamlit as st
            
            # Save original session state
            original_session_state = getattr(st, "session_state", {})
            
            try:
                # Set up mock session state
                st.session_state = {
                    "user": {
                        "id": "user123",
                        "username": "testuser"
                    }
                }
                
                # Test with user in session state
                result = safe_get_current_user()
                self.assertEqual(result["id"], "user123")
                self.assertEqual(result["username"], "testuser")
                
                # Test with no user in session state
                st.session_state = {}
                result = safe_get_current_user()
                self.assertEqual(result, None)
                
                # Test with default value
                default_user = {"id": "default", "username": "default"}
                result = safe_get_current_user(default=default_user)
                self.assertEqual(result, default_user)
            finally:
                # Restore original session state
                st.session_state = original_session_state
        except ImportError:
            # Function might not exist, skip test
            self.skipTest("safe_get_current_user function not found")
    
    def test_event_date_processing(self):
        """Test event date processing with null handling."""
        # This test checks the application's ability to handle null dates in events
        # Import the function if it exists
        try:
            from admin_dashboard.user_app_postgres import parse_date_safely
            
            # Test with valid date string
            result = parse_date_safely("2025-04-12T14:00:00")
            self.assertIsNotNone(result)
            
            # Test with None date
            result = parse_date_safely(None)
            self.assertIsNone(result)
            
            # Test with invalid date string
            result = parse_date_safely("invalid-date")
            self.assertIsNone(result)
            
            # Test with default value
            import datetime
            default_date = datetime.datetime.now()
            result = parse_date_safely(None, default=default_date)
            self.assertEqual(result, default_date)
        except ImportError:
            # Function might not exist, skip test
            self.skipTest("parse_date_safely function not found")

if __name__ == "__main__":
    unittest.main()