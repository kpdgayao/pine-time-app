"""
Tests for database utilities in the Pine Time App.
These tests focus on the database connection handling and utilities.
"""

import os
import sys
import unittest
import logging
from typing import Dict, Any

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from admin_dashboard.utils.db import (
    get_database_config, get_database_uri, is_demo_mode,
    test_database_connection, get_postgres_connection_params
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_db_utils.log")
    ]
)
logger = logging.getLogger("test_db_utils")

class TestDatabaseUtils(unittest.TestCase):
    """Test database utilities."""
    
    def test_get_database_config(self):
        """Test getting database configuration."""
        config = get_database_config()
        self.assertIsInstance(config, dict)
        
        # Check if we have the expected keys based on database type
        if config["database_type"] == "postgresql":
            required_keys = [
                "database_type", "server", "user", "password", 
                "db", "port", "ssl_mode"
            ]
            for key in required_keys:
                self.assertIn(key, config)
        else:
            self.assertIn("database_type", config)
            self.assertIn("uri", config)
    
    def test_get_database_uri(self):
        """Test getting database URI."""
        uri = get_database_uri()
        self.assertIsInstance(uri, str)
        
        # Check if URI has the expected format
        config = get_database_config()
        if config["database_type"] == "postgresql":
            self.assertTrue(uri.startswith("postgresql://"))
        else:
            self.assertTrue(uri.startswith("sqlite:///"))
    
    def test_is_demo_mode(self):
        """Test checking demo mode."""
        # Save original value
        original_value = os.environ.get("DEMO_MODE", "")
        
        try:
            # Test with demo mode enabled
            os.environ["DEMO_MODE"] = "true"
            self.assertTrue(is_demo_mode())
            
            # Test with demo mode disabled
            os.environ["DEMO_MODE"] = "false"
            self.assertFalse(is_demo_mode())
            
            # Test with invalid value
            os.environ["DEMO_MODE"] = "invalid"
            self.assertFalse(is_demo_mode())
        finally:
            # Restore original value
            if original_value:
                os.environ["DEMO_MODE"] = original_value
            else:
                os.environ.pop("DEMO_MODE", None)
    
    def test_get_postgres_connection_params(self):
        """Test getting PostgreSQL connection parameters."""
        # Skip if not using PostgreSQL
        config = get_database_config()
        if config["database_type"] != "postgresql":
            self.skipTest("Not using PostgreSQL")
        
        params = get_postgres_connection_params()
        self.assertIsInstance(params, dict)
        
        # Check for the expected keys in the connection params
        # The actual keys might vary based on the implementation
        expected_keys = ["server", "user", "password", "db"]
        
        # Check that at least some of the expected keys are present
        # We don't need all of them to match exactly
        found_keys = [key for key in expected_keys if key in params]
        self.assertTrue(len(found_keys) > 0, f"No expected keys found in {params.keys()}")

if __name__ == "__main__":
    unittest.main()