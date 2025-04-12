"""
Tests for the API client in the Pine Time App.
These tests focus on the API client functionality and error handling.
"""

import os
import sys
import unittest
import logging
from unittest.mock import patch, MagicMock
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from admin_dashboard.utils.api import APIClient, APIError, PostgreSQLError
from admin_dashboard.config import API_ENDPOINTS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_api_client.log")
    ]
)
logger = logging.getLogger("test_api_client")

class TestAPIClient(unittest.TestCase):
    """Test API client functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.api_client = APIClient()
    
    @patch('requests.Session.request')
    def test_get_request(self, mock_request):
        """Test GET request."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"test": "data"}
        mock_request.return_value = mock_response
        
        # Make request
        result = self.api_client.get(
            API_ENDPOINTS["users"]["list"],
            params={"page": 1, "size": 10},
            headers={"Authorization": "Bearer test_token"},
            error_message="Test error message"
        )
        
        # Check result
        self.assertEqual(result, {"test": "data"})
        
        # Check that request was called with correct arguments
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "GET")
        self.assertTrue(API_ENDPOINTS["users"]["list"] in args[1])
        self.assertEqual(kwargs["params"], {"page": 1, "size": 10})
        self.assertIn("Authorization", kwargs["headers"])
    
    @patch('requests.Session.request')
    def test_post_request(self, mock_request):
        """Test POST request."""
        # Mock response
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": "new_item", "name": "Test Item"}
        mock_request.return_value = mock_response
        
        # Make request
        result = self.api_client.post(
            API_ENDPOINTS["events"]["create"],
            json_data={"name": "Test Item", "description": "Test Description"},
            headers={"Authorization": "Bearer test_token"},
            error_message="Test error message"
        )
        
        # Check result
        self.assertEqual(result, {"id": "new_item", "name": "Test Item"})
        
        # Check that request was called with correct arguments
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        self.assertEqual(args[0], "POST")
        self.assertTrue(API_ENDPOINTS["events"]["create"] in args[1])
        self.assertEqual(kwargs["json"], {"name": "Test Item", "description": "Test Description"})
        self.assertIn("Authorization", kwargs["headers"])
    
    @patch('requests.Session.request')
    def test_error_handling(self, mock_request):
        """Test error handling."""
        # Mock error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Validation error"}
        mock_request.return_value = mock_response
        
        # Make request and check for exception
        with self.assertRaises(APIError) as context:
            self.api_client.get(
                API_ENDPOINTS["users"]["list"],
                error_message="Test error message"
            )
        
        # Check exception details
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Test error message", str(context.exception))
        self.assertIn("Validation error", str(context.exception))
    
    @patch('requests.Session.request')
    def test_postgresql_error_handling(self, mock_request):
        """Test PostgreSQL error handling."""
        # Mock PostgreSQL error response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {
            "detail": "Database error",
            "pg_code": "23505",  # Unique violation
            "pg_message": "duplicate key value violates unique constraint"
        }
        mock_request.return_value = mock_response
        
        # Make request and check for exception
        with self.assertRaises(PostgreSQLError) as context:
            self.api_client.post(
                API_ENDPOINTS["users"]["create"],
                json_data={"username": "duplicate", "email": "duplicate@example.com"},
                error_message="Test PostgreSQL error"
            )
        
        # Check exception details
        self.assertEqual(context.exception.status_code, 400)
        self.assertIn("Test PostgreSQL error", str(context.exception))
        self.assertIn("Database error", str(context.exception))
        self.assertEqual(context.exception.pg_code, "23505")
    
    @patch('requests.Session.request')
    def test_response_format_handling(self, mock_request):
        """Test response format handling."""
        # Test with list response
        mock_response_list = MagicMock()
        mock_response_list.status_code = 200
        mock_response_list.json.return_value = [
            {"id": "1", "name": "Item 1"},
            {"id": "2", "name": "Item 2"}
        ]
        mock_request.return_value = mock_response_list
        
        # Make request
        result = self.api_client.get(API_ENDPOINTS["events"]["list"])
        
        # Check result
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        
        # Test with paginated response
        mock_response_paginated = MagicMock()
        mock_response_paginated.status_code = 200
        mock_response_paginated.json.return_value = {
            "items": [
                {"id": "1", "name": "Item 1"},
                {"id": "2", "name": "Item 2"}
            ],
            "total": 2,
            "page": 1,
            "size": 10
        }
        mock_request.return_value = mock_response_paginated
        
        # Make request
        result = self.api_client.get(API_ENDPOINTS["events"]["list"])
        
        # Check result
        self.assertIsInstance(result, dict)
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)
        self.assertEqual(len(result["items"]), 2)
    
    @patch('requests.Session.request')
    def test_retry_mechanism(self, mock_request):
        """Test retry mechanism."""
        # Mock a series of responses
        mock_response_1 = MagicMock()
        mock_response_1.status_code = 500
        mock_response_1.json.side_effect = Exception("Server error")
        
        mock_response_2 = MagicMock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = {"test": "data"}
        
        # Set up the mock to return different responses on successive calls
        mock_request.side_effect = [mock_response_1, mock_response_2]
        
        # Make request
        result = self.api_client.get(
            API_ENDPOINTS["users"]["list"],
            retry_count=1,  # Only retry once
            error_message="Test retry"
        )
        
        # Check result
        self.assertEqual(result, {"test": "data"})
        
        # Check that request was called twice
        self.assertEqual(mock_request.call_count, 2)

if __name__ == "__main__":
    unittest.main()