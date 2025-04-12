"""
Pine Time App Standalone Tests

This module provides standalone tests for the Pine Time application's core functionality,
designed to work in both demo mode and with PostgreSQL connections.

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
logger = logging.getLogger("pine_time_standalone_test")

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Enable demo mode for testing
os.environ["DEMO_MODE"] = "true"

# Import project modules
from admin_dashboard.utils.db import is_demo_mode, get_database_config
from admin_dashboard.utils.api import APIError, PostgreSQLError, parse_date_safely
from admin_dashboard.config import API_ENDPOINTS

# Import sample data generators (these don't require Streamlit context)
from admin_dashboard.utils.connection import (
    get_sample_events,
    get_sample_badges,
    get_sample_users,
    get_sample_user_profile,
    get_sample_points_history
)

class TestPineTimeCore:
    """Test suite for Pine Time core functionality."""
    
    def test_demo_mode_enabled(self) -> None:
        """Test that demo mode is properly enabled."""
        assert is_demo_mode() == True, "Demo mode should be enabled"
    
    def test_database_config(self) -> None:
        """Test database configuration with proper error handling."""
        config = get_database_config()
        assert isinstance(config, dict), "Database config should be a dictionary"
        assert "database_type" in config, "Database config should include database_type"
        
        # Verify PostgreSQL configuration parameters
        if config["database_type"] == "postgresql":
            required_params = ["server", "user", "password", "db", "port"]
            for param in required_params:
                assert param in config, f"PostgreSQL config should include {param}"
    
    def test_api_endpoints_config(self) -> None:
        """Test API endpoints configuration."""
        assert isinstance(API_ENDPOINTS, dict), "API_ENDPOINTS should be a dictionary"
        
        # Verify required endpoint categories
        required_categories = ["auth", "users", "events", "points", "badges"]
        for category in required_categories:
            assert category in API_ENDPOINTS, f"API_ENDPOINTS should include {category} category"
        
        # Verify authentication endpoints
        assert "token" in API_ENDPOINTS["auth"], "Auth endpoints should include token endpoint"
        assert "refresh" in API_ENDPOINTS["auth"], "Auth endpoints should include refresh endpoint"
    
    def test_custom_exceptions(self) -> None:
        """Test custom exception classes for error handling."""
        # Test APIError
        api_error = APIError("Test API error", 500)
        assert api_error.message == "Test API error", "APIError should store message"
        assert api_error.status_code == 500, "APIError should store status code"
        
        # Test PostgreSQLError (extends APIError)
        pg_error = PostgreSQLError("Test PostgreSQL error", 500, None, "23505")
        assert pg_error.message == "Test PostgreSQL error", "PostgreSQLError should store message"
        assert pg_error.pg_code == "23505", "PostgreSQLError should store PostgreSQL error code"
        assert isinstance(pg_error, APIError), "PostgreSQLError should be a subclass of APIError"
    
    def test_date_parsing(self) -> None:
        """Test date parsing utility with error handling."""
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
    
    def test_sample_events_data(self) -> None:
        """Test sample events data generation for demo mode."""
        events = get_sample_events()
        assert isinstance(events, list), "Sample events should be a list"
        assert len(events) > 0, "Sample events should not be empty"
        
        # Verify event structure
        for event in events:
            assert "id" in event, "Event should have an ID"
            assert "title" in event, "Event should have a title"
            assert "description" in event, "Event should have a description"
            assert "start_time" in event, "Event should have a start time"
            assert "location" in event, "Event should have a location"
    
    def test_sample_badges_data(self) -> None:
        """Test sample badges data generation for demo mode."""
        badges = get_sample_badges()
        assert isinstance(badges, list), "Sample badges should be a list"
        assert len(badges) > 0, "Sample badges should not be empty"
        
        # Verify badge structure
        for badge in badges:
            assert "id" in badge, "Badge should have an ID"
            assert "name" in badge, "Badge should have a name"
            assert "description" in badge, "Badge should have a description"
            assert "category" in badge, "Badge should have a category"
    
    def test_sample_users_data(self) -> None:
        """Test sample users data generation for demo mode."""
        users = get_sample_users()
        assert isinstance(users, list), "Sample users should be a list"
        assert len(users) > 0, "Sample users should not be empty"
        
        # Verify user structure
        for user in users:
            assert "id" in user, "User should have an ID"
            assert "username" in user, "User should have a username"
            assert "email" in user, "User should have an email"
            assert "full_name" in user, "User should have a full name"
    
    def test_sample_profile_data(self) -> None:
        """Test sample user profile data generation for demo mode."""
        profile = get_sample_user_profile()
        assert isinstance(profile, dict), "Sample profile should be a dictionary"
        
        # Verify profile structure
        assert "id" in profile, "Profile should have an ID"
        assert "username" in profile, "Profile should have a username"
        assert "email" in profile, "Profile should have an email"
        assert "full_name" in profile, "Profile should have a full name"
        assert "points" in profile, "Profile should have points"
    
    def test_sample_points_history_data(self) -> None:
        """Test sample points history data generation for demo mode."""
        points_history = get_sample_points_history()
        assert isinstance(points_history, list), "Sample points history should be a list"
        assert len(points_history) > 0, "Sample points history should not be empty"
        
        # Verify points history structure
        for entry in points_history:
            assert "id" in entry, "Points entry should have an ID"
            assert "points" in entry, "Points entry should have points value"
            assert "reason" in entry, "Points entry should have a reason"
            assert "timestamp" in entry, "Points entry should have a timestamp"

def run_tests() -> None:
    """Run the standalone tests with proper error handling."""
    try:
        # Run the tests
        pytest.main(["-xvs", __file__])
    except Exception as e:
        logger.error(f"Error running tests: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
