"""
Core functionality tests for Pine Time App.
Tests the error handling, connection management, and API response handling.
"""

import os
import sys
import unittest
import logging
from unittest.mock import patch, MagicMock
from typing import Dict, Any, List, Optional, Union

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_pine_time_core.log")
    ]
)
logger = logging.getLogger("test_pine_time_core")

class TestPineTimeCore(unittest.TestCase):
    """Test core functionality of Pine Time App."""
    
    def setUp(self):
        """Set up test environment."""
        # Import modules from the project
        from admin_dashboard.utils.db import get_database_config, is_demo_mode
        
        # Store references to imported functions
        self.get_database_config = get_database_config
        self.is_demo_mode = is_demo_mode
        
        # Save original environment variables
        self.original_env = {}
        for key in ["DATABASE_TYPE", "DEMO_MODE"]:
            self.original_env[key] = os.environ.get(key)
    
    def tearDown(self):
        """Tear down test environment."""
        # Restore original environment variables
        for key, value in self.original_env.items():
            if value is not None:
                os.environ[key] = value
            elif key in os.environ:
                del os.environ[key]
    
    def test_database_config(self):
        """Test database configuration."""
        # Test PostgreSQL configuration
        os.environ["DATABASE_TYPE"] = "postgresql"
        config = self.get_database_config()
        
        self.assertEqual(config["database_type"], "postgresql")
        self.assertIn("server", config)
        self.assertIn("user", config)
        self.assertIn("password", config)
        self.assertIn("db", config)
        
        # Test SQLite configuration
        os.environ["DATABASE_TYPE"] = "sqlite"
        config = self.get_database_config()
        
        self.assertEqual(config["database_type"], "sqlite")
        self.assertIn("uri", config)
    
    def test_demo_mode(self):
        """Test demo mode functionality."""
        # Test with demo mode enabled
        os.environ["DEMO_MODE"] = "true"
        self.assertTrue(self.is_demo_mode())
        
        # Test with demo mode disabled
        os.environ["DEMO_MODE"] = "false"
        self.assertFalse(self.is_demo_mode())
    
    @patch('admin_dashboard.utils.api.requests.Session.request')
    def test_api_error_handling(self, mock_request):
        """Test API error handling."""
        # Import the APIClient and APIError classes
        from admin_dashboard.utils.api import APIClient, APIError
        
        # Create API client
        api_client = APIClient()
        
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Validation error"}
        mock_request.return_value = mock_response
        
        # Test error handling
        with self.assertRaises(APIError) as context:
            api_client.get("http://example.com/api/test", error_message="Test error")
        
        # Check exception details
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Test error", str(context.exception))
        self.assertIn("Validation error", str(context.exception))
    
    @patch('admin_dashboard.utils.api.requests.Session.request')
    def test_postgresql_error_handling(self, mock_request):
        """Test PostgreSQL error handling."""
        # Import the APIClient and PostgreSQLError classes
        from admin_dashboard.utils.api import APIClient, PostgreSQLError
        
        # Create API client
        api_client = APIClient()
        
        # Mock PostgreSQL error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "detail": "Database error",
            "pg_code": "23505",  # Unique violation
            "pg_message": "duplicate key value violates unique constraint"
        }
        mock_request.return_value = mock_response
        
        # Test error handling
        with self.assertRaises(PostgreSQLError) as context:
            api_client.post("http://example.com/api/test", json_data={"test": "data"}, error_message="Test PostgreSQL error")
        
        # Check exception details
        self.assertEqual(context.exception.status_code, 400)
        self.assertEqual(context.exception.pg_code, "23505")
        self.assertIn("Test PostgreSQL error", str(context.exception))
        self.assertIn("Database error", str(context.exception))
    
    def test_safe_api_response_handler(self):
        """Test safe API response handler."""
        # Define a simple safe_api_response_handler function similar to the one in the app
        def safe_api_response_handler(response, key=None, default=None):
            """Safely handle API responses with different formats."""
            if response is None:
                return default
            
            if isinstance(response, dict) and key is not None:
                return response.get(key, default)
            
            return response
        
        # Test with dictionary response
        response_dict = {
            "items": [
                {"id": "1", "name": "Item 1"},
                {"id": "2", "name": "Item 2"}
            ],
            "total": 2
        }
        
        # Test with key specified
        result = safe_api_response_handler(response_dict, key="items")
        self.assertEqual(result, response_dict["items"])
        
        # Test with non-existent key
        result = safe_api_response_handler(response_dict, key="non_existent")
        self.assertIsNone(result)
        
        # Test with non-existent key and default
        result = safe_api_response_handler(response_dict, key="non_existent", default=[])
        self.assertEqual(result, [])
        
        # Test with list response
        response_list = [
            {"id": "1", "name": "Item 1"},
            {"id": "2", "name": "Item 2"}
        ]
        
        # Test with no key specified
        result = safe_api_response_handler(response_list)
        self.assertEqual(result, response_list)
        
        # Test with None response
        result = safe_api_response_handler(None, default=[])
        self.assertEqual(result, [])
    
    @patch('admin_dashboard.utils.connection.check_api_connection')
    @patch('admin_dashboard.utils.connection.test_database_connection')
    @patch('admin_dashboard.utils.connection.is_demo_mode')
    def test_connection_verification(self, mock_is_demo, mock_test_db, mock_check_api):
        """Test connection verification."""
        # Import verify_connection function
        from admin_dashboard.utils.connection import verify_connection
        
        # Create a mock session state
        with patch('streamlit.session_state', {}):
            # Test with demo mode
            mock_is_demo.return_value = True
            
            result = verify_connection(force=True)
            self.assertTrue(result["success"])
            self.assertTrue(result["is_demo"])
            
            # Test with successful connections
            mock_is_demo.return_value = False
            mock_test_db.return_value = True
            mock_check_api.return_value = True
            
            result = verify_connection(force=True)
            self.assertTrue(result["success"])
            self.assertTrue(result["api_connected"])
            self.assertTrue(result["db_connected"])
            
            # Test with failed connections
            mock_test_db.return_value = False
            mock_check_api.return_value = False
            
            result = verify_connection(force=True)
            self.assertFalse(result["success"])
            self.assertFalse(result["api_connected"])
            self.assertFalse(result["db_connected"])
    
    def test_connection_fallback_decorator(self):
        """Test connection fallback decorator."""
        # Import with_connection_fallback decorator
        from admin_dashboard.utils.connection import with_connection_fallback
        
        # Define a test function
        @with_connection_fallback
        def test_function(param1, param2=None):
            return {"param1": param1, "param2": param2, "source": "original"}
        
        # Mock verify_connection function
        with patch('admin_dashboard.utils.connection.verify_connection') as mock_verify:
            # Test with successful connection
            mock_verify.return_value = {"success": True}
            
            result = test_function("test1", param2="test2")
            self.assertEqual(result["param1"], "test1")
            self.assertEqual(result["param2"], "test2")
            self.assertEqual(result["source"], "original")
            
            # Test with failed connection
            mock_verify.return_value = {"success": False}
            
            # We need to mock the sample data generator
            with patch('admin_dashboard.utils.connection.get_sample_test_function') as mock_sample:
                mock_sample.return_value = {"param1": "sample1", "param2": "sample2", "source": "sample"}
                
                result = test_function("test1", param2="test2")
                self.assertEqual(result["param1"], "sample1")
                self.assertEqual(result["param2"], "sample2")
                self.assertEqual(result["source"], "sample")
    
    def test_sample_data_generators(self):
        """Test sample data generators."""
        # Import sample data generators
        from admin_dashboard.utils.connection import (
            get_sample_users, get_sample_events, get_sample_user_profile,
            get_sample_user_badges, get_sample_user_events, get_sample_points_history,
            get_sample_leaderboard, get_sample_badges
        )
        
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