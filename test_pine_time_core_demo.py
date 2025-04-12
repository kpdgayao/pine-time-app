"""
Pine Time App Core Demo Tests

This module provides standalone tests for the Pine Time application's core functionality
in demo mode, focusing on components that don't require Streamlit context or PostgreSQL connection.

Following PEP 8 style guidelines and using type hints as per project requirements.
"""

import os
import sys
import pytest
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import time

# Configure logging with appropriate severity levels
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pine_time_core_demo_test")

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set environment variables for demo mode
os.environ["DEMO_MODE"] = "true"

def test_demo_mode_enabled() -> None:
    """Test that demo mode is properly enabled."""
    # Import here to avoid import errors
    from admin_dashboard.utils.db import is_demo_mode
    assert is_demo_mode() == True, "Demo mode should be enabled"

def test_custom_exceptions() -> None:
    """Test custom exception classes for error handling."""
    # Import here to avoid import errors
    from admin_dashboard.utils.api import APIError, PostgreSQLError
    
    # Test APIError
    api_error = APIError("Test API error", 500)
    assert api_error.message == "Test API error", "APIError should store message"
    assert api_error.status_code == 500, "APIError should store status code"
    
    # Test PostgreSQLError (extends APIError)
    pg_error = PostgreSQLError("Test PostgreSQL error", 500, None, "23505")
    assert pg_error.message == "Test PostgreSQL error", "PostgreSQLError should store message"
    assert pg_error.pg_code == "23505", "PostgreSQLError should store PostgreSQL error code"
    assert isinstance(pg_error, APIError), "PostgreSQLError should be a subclass of APIError"

def test_date_parsing() -> None:
    """Test date parsing utility with error handling."""
    # Import here to avoid import errors
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
    
    # Test None input with fallback
    parsed_none = parse_date_safely(None, default=default_date)
    assert parsed_none == default_date, "None input should return default value"

def test_api_endpoints_config() -> None:
    """Test API endpoints configuration."""
    # Import here to avoid import errors
    from admin_dashboard.config import API_ENDPOINTS
    
    assert isinstance(API_ENDPOINTS, dict), "API_ENDPOINTS should be a dictionary"
    
    # Verify required endpoint categories
    required_categories = ["auth", "users", "events", "points", "badges"]
    for category in required_categories:
        assert category in API_ENDPOINTS, f"API_ENDPOINTS should include {category} category"
    
    # Verify authentication endpoints
    assert "token" in API_ENDPOINTS["auth"], "Auth endpoints should include token endpoint"
    assert "refresh" in API_ENDPOINTS["auth"], "Auth endpoints should include refresh endpoint"
    assert "verify" in API_ENDPOINTS["auth"], "Auth endpoints should include verify endpoint"

def test_sample_data_functions() -> None:
    """Test sample data generation functions."""
    # Import here to avoid import errors
    from admin_dashboard.utils.connection import (
        get_sample_events,
        get_sample_badges,
        get_sample_users,
        get_sample_leaderboard
    )
    
    # Test sample events
    events = get_sample_events()
    assert isinstance(events, list), "Sample events should be a list"
    assert len(events) > 0, "Sample events should not be empty"
    
    # Test sample badges
    badges = get_sample_badges()
    assert isinstance(badges, list), "Sample badges should be a list"
    assert len(badges) > 0, "Sample badges should not be empty"
    
    # Test sample users
    users = get_sample_users()
    assert isinstance(users, list), "Sample users should be a list"
    assert len(users) > 0, "Sample users should not be empty"
    
    # Test sample leaderboard
    leaderboard = get_sample_leaderboard()
    assert isinstance(leaderboard, list), "Sample leaderboard should be a list"
    assert len(leaderboard) > 0, "Sample leaderboard should not be empty"

def test_error_handling_utilities() -> None:
    """Test error handling utilities."""
    # Import here to avoid import errors
    from admin_dashboard.utils.api import APIError
    
    # Test custom exception with different parameters
    error1 = APIError("Test error")
    assert error1.status_code is None, "Status code should be None when not provided"
    
    error2 = APIError("Test error", 404)
    assert error2.status_code == 404, "Status code should be stored correctly"
    
    error3 = APIError("Test error", 500, {"detail": "Server error"})
    assert error3.response == {"detail": "Server error"}, "Response should be stored correctly"

def test_database_config_in_demo_mode() -> None:
    """Test database configuration in demo mode."""
    # Import here to avoid import errors
    from admin_dashboard.utils.db import get_database_config
    
    # In demo mode, this should still return a valid configuration
    config = get_database_config()
    assert isinstance(config, dict), "Database config should be a dictionary even in demo mode"
    assert "database_type" in config, "Database config should include database_type"

if __name__ == "__main__":
    # Set environment variables for demo mode
    os.environ["DEMO_MODE"] = "true"
    
    # Run the tests
    pytest.main(["-xvs", __file__])
