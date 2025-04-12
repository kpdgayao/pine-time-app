"""
Tests for connection utilities in the Pine Time App.
These tests focus on the connection verification and fallback mechanisms.
"""

import os
import sys
import unittest
import logging
from unittest.mock import patch, MagicMock
from typing import Dict, Any, Callable

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from admin_dashboard.utils.connection import (
    verify_connection, with_connection_fallback,
    get_sample_users, get_sample_events, get_sample_user_profile,
    get_sample_user_badges, get_sample_user_events, get_sample_points_history,
    get_sample_leaderboard, get_sample_badges
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_connection_utils.log")
    ]
)
logger = logging.getLogger("test_connection_utils")

class TestConnectionUtils(unittest.TestCase):
    """Test connection utilities."""
    
    def setUp(self):
        """Set up test environment."""
        # Create a mock session state
        self.mock_session_state = {}
        
        # Create patch for st.session_state
        self.session_state_patch = patch('streamlit.session_state', self.mock_session_state)
        self.session_state_patch.start()
    
    def tearDown(self):
        """Tear down test environment."""
        # Stop patch
        self.session_state_patch.stop()
    
    @patch('admin_dashboard.utils.connection.check_api_connection')
    @patch('admin_dashboard.utils.connection.test_database_connection')
    def test_verify_connection(self, mock_test_db, mock_check_api):
        """Test connection verification."""
        # Mock successful connections
        mock_test_db.return_value = True
        mock_check_api.return_value = True
        
        # Test with force=True to bypass caching
        result = verify_connection(force=True)
        
        # Check result
        self.assertIsInstance(result, dict)
        self.assertTrue(result["success"])
        self.assertTrue(result["api_connected"])
        self.assertTrue(result["db_connected"])
        
        # Mock failed connections
        mock_test_db.return_value = False
        mock_check_api.return_value = False
        
        # Test with force=True to bypass caching
        result = verify_connection(force=True)
        
        # Check result
        self.assertIsInstance(result, dict)
        self.assertFalse(result["success"])
        self.assertFalse(result["api_connected"])
        self.assertFalse(result["db_connected"])
    
    def test_with_connection_fallback_decorator(self):
        """Test connection fallback decorator."""
        # Create a test function
        @with_connection_fallback
        def test_function(param1, param2=None):
            return {"param1": param1, "param2": param2, "source": "original"}
        
        # Create a mock verify_connection function
        def mock_verify_connection(force=False):
            return {"success": True, "api_connected": True, "db_connected": True}
        
        # Patch verify_connection
        with patch('admin_dashboard.utils.connection.verify_connection', mock_verify_connection):
            # Test with successful connection
            result = test_function("test1", param2="test2")
            
            # Check result
            self.assertEqual(result["param1"], "test1")
            self.assertEqual(result["param2"], "test2")
            self.assertEqual(result["source"], "original")
        
        # Create a mock verify_connection function that fails
        def mock_verify_connection_fail(force=False):
            return {"success": False, "api_connected": False, "db_connected": False}
        
        # Patch verify_connection and get_sample_data
        with patch('admin_dashboard.utils.connection.verify_connection', mock_verify_connection_fail):
            # We need to mock the sample data generator that would be called
            # This will depend on the function name
            sample_data = {"param1": "sample1", "param2": "sample2", "source": "sample"}
            
            # For test_function, the fallback would look for a sample data generator
            # with a name like get_sample_<function_name>
            with patch('admin_dashboard.utils.connection.get_sample_test_function', return_value=sample_data):
                # Test with failed connection
                result = test_function("test1", param2="test2")
                
                # Check result - should be the sample data
                self.assertEqual(result["param1"], "sample1")
                self.assertEqual(result["param2"], "sample2")
                self.assertEqual(result["source"], "sample")
    
    def test_sample_data_generators(self):
        """Test sample data generators."""
        # Test each sample data generator
        sample_users = get_sample_users()
        self.assertIsInstance(sample_users, list)
        self.assertTrue(len(sample_users) > 0)
        
        sample_events = get_sample_events()
        self.assertIsInstance(sample_events, list)
        self.assertTrue(len(sample_events) > 0)
        
        sample_profile = get_sample_user_profile()
        self.assertIsInstance(sample_profile, dict)
        self.assertIn("username", sample_profile)
        
        sample_badges = get_sample_user_badges()
        self.assertIsInstance(sample_badges, list)
        self.assertTrue(len(sample_badges) > 0)
        
        sample_user_events = get_sample_user_events()
        self.assertIsInstance(sample_user_events, list)
        self.assertTrue(len(sample_user_events) > 0)
        
        sample_points = get_sample_points_history()
        self.assertIsInstance(sample_points, list)
        self.assertTrue(len(sample_points) > 0)
        
        sample_leaderboard = get_sample_leaderboard()
        self.assertIsInstance(sample_leaderboard, list)
        self.assertTrue(len(sample_leaderboard) > 0)
        
        all_badges = get_sample_badges()
        self.assertIsInstance(all_badges, list)
        self.assertTrue(len(all_badges) > 0)

if __name__ == "__main__":
    unittest.main()