"""
Pine Time Core Functionality Tests

This script tests the core functionality of the Pine Time application
with proper handling of Streamlit context requirements and demo mode.

Following PEP 8 style guidelines and using type hints as per project requirements.
"""

import os
import sys
import pytest
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pine_time_core_test")

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Enable demo mode
os.environ["DEMO_MODE"] = "true"

# Import project modules
from admin_dashboard.utils.db import is_demo_mode

class TestPineTimeCore:
    """Test suite for Pine Time core functionality."""
    
    def test_demo_mode_enabled(self) -> None:
        """Test that demo mode is properly enabled."""
        assert is_demo_mode() == True, "Demo mode should be enabled"
    
    def test_database_config(self) -> None:
        """Test database configuration with proper error handling."""
        from admin_dashboard.utils.db import get_database_config
        
        # In demo mode, this should still return a valid configuration
        config = get_database_config()
        assert isinstance(config, dict), "Database config should be a dictionary"
        assert "database_type" in config, "Database config should include database_type"
    
    def test_api_endpoints_config(self) -> None:
        """Test API endpoints configuration."""
        # Import here to avoid Streamlit context issues
        sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin_dashboard"))
        from admin_dashboard.config import API_ENDPOINTS
        
        assert isinstance(API_ENDPOINTS, dict), "API_ENDPOINTS should be a dictionary"
        assert "auth" in API_ENDPOINTS, "API_ENDPOINTS should include auth endpoints"
        assert "users" in API_ENDPOINTS, "API_ENDPOINTS should include users endpoints"
        assert "events" in API_ENDPOINTS, "API_ENDPOINTS should include events endpoints"
    
    def test_sample_data_generation(self) -> None:
        """Test sample data generation for demo mode."""
        # Import here to avoid Streamlit context issues
        from admin_dashboard.utils.connection import get_sample_events, get_sample_badges
        
        # These functions don't require Streamlit context
        events = get_sample_events()
        assert isinstance(events, list), "Sample events should be a list"
        assert len(events) > 0, "Sample events should not be empty"
        
        badges = get_sample_badges()
        assert isinstance(badges, list), "Sample badges should be a list"
        assert len(badges) > 0, "Sample badges should not be empty"
    
    def test_error_handling(self) -> None:
        """Test error handling utilities."""
        from admin_dashboard.utils.api import APIError, PostgreSQLError
        
        # Test custom exception classes
        api_error = APIError("Test API error", 500)
        assert api_error.message == "Test API error", "APIError should store message"
        assert api_error.status_code == 500, "APIError should store status code"
        
        pg_error = PostgreSQLError("Test PostgreSQL error", 500, None, "23505")
        assert pg_error.message == "Test PostgreSQL error", "PostgreSQLError should store message"
        assert pg_error.pg_code == "23505", "PostgreSQLError should store PostgreSQL error code"
    
    def test_date_parsing(self) -> None:
        """Test date parsing utility with error handling."""
        from admin_dashboard.utils.api import parse_date_safely
        
        # Test valid date
        valid_date = "2025-04-12T15:00:00"
        parsed_date = parse_date_safely(valid_date)
        assert parsed_date is not None, "Valid date should be parsed successfully"
        assert parsed_date.year == 2025, "Parsed date should have correct year"
        
        # Test invalid date with fallback
        invalid_date = "not-a-date"
        default_date = datetime.now()
        parsed_invalid = parse_date_safely(invalid_date, default=default_date)
        assert parsed_invalid == default_date, "Invalid date should return default value"
    
    def test_database_uri_generation(self) -> None:
        """Test database URI generation."""
        from admin_dashboard.config import get_database_uri
        
        # This should work in demo mode
        uri = get_database_uri()
        assert isinstance(uri, str), "Database URI should be a string"
        assert uri.startswith("postgresql://") or uri.startswith("sqlite://"), "Database URI should have valid prefix"

if __name__ == "__main__":
    # Run tests
    pytest.main(["-xvs", __file__])
