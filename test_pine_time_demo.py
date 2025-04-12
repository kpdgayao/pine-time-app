"""
Pine Time App Demo Mode Test Script

This script tests core functionality of the Pine Time app in demo mode,
which bypasses the need for actual PostgreSQL database connections.
"""

import os
import sys
import logging
import pytest
from datetime import datetime, timedelta
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("pine_time_demo_test")

# Set environment variables for demo mode
os.environ["DEMO_MODE"] = "true"

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
from admin_dashboard.utils.db import is_demo_mode, test_database_connection
from admin_dashboard.utils.auth import login, logout, check_authentication
from admin_dashboard.utils.api import get_events, get_badges, get_user_badges
from admin_dashboard.utils.connection import verify_connection, with_connection_fallback

def test_demo_mode_enabled():
    """Test that demo mode is properly enabled."""
    assert is_demo_mode() == True, "Demo mode should be enabled"

def test_login_demo_credentials():
    """Test login with demo credentials."""
    # In demo mode, these credentials should work
    result = login("demo@pinetimeexperience.com", "demo")
    assert result == True, "Demo login should succeed"

def test_get_events_demo_data():
    """Test that get_events returns sample data in demo mode."""
    events = get_events()
    assert isinstance(events, list), "Events should be a list"
    assert len(events) > 0, "Events list should not be empty in demo mode"
    
    # Check event structure
    for event in events:
        assert "id" in event, "Event should have an ID"
        assert "title" in event, "Event should have a title"
        assert "start_time" in event, "Event should have a start time"

def test_get_badges_demo_data():
    """Test that get_badges returns sample data in demo mode."""
    badges = get_badges()
    assert isinstance(badges, list), "Badges should be a list"
    assert len(badges) > 0, "Badges list should not be empty in demo mode"
    
    # Check badge structure
    for badge in badges:
        assert "id" in badge, "Badge should have an ID"
        assert "name" in badge, "Badge should have a name"
        assert "description" in badge, "Badge should have a description"

def test_connection_fallback_decorator():
    """Test the connection fallback decorator with demo mode."""
    # Define a function that would normally fail
    def api_function():
        raise Exception("API connection error")
    
    # Define a fallback function
    def fallback_function():
        return ["sample_data_1", "sample_data_2"]
    
    # Apply decorator
    decorated_function = with_connection_fallback(fallback_function)(api_function)
    
    # Call decorated function - should use fallback in demo mode
    result = decorated_function()
    assert result == ["sample_data_1", "sample_data_2"], "Fallback function should be used"

def test_verify_connection_demo_mode():
    """Test that verify_connection works in demo mode."""
    connection_status = verify_connection(force=True)
    assert connection_status["demo_mode"] == True, "Connection status should indicate demo mode"
    
    # In demo mode, we should still get a success status
    assert connection_status["success"] == True, "Connection verification should succeed in demo mode"

if __name__ == "__main__":
    # Run tests
    pytest.main(["-xvs", __file__])
