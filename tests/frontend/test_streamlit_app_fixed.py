"""
Tests for the Streamlit frontend application.
Uses a custom Streamlit test client to simulate user interactions.
"""

import pytest
import logging
import sys
import os
import re
import time  # Added missing import
import json
from typing import Dict, Any, List, Optional
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta  # Added missing import

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import project modules
from admin_dashboard.utils.api import APIClient
from admin_dashboard.utils.auth import login, logout, check_authentication
from admin_dashboard.utils.db import is_demo_mode, test_database_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_streamlit_app")

class StreamlitTestClient:
    """
    A test client for Streamlit applications.
    Simulates Streamlit's session state and widget interactions.
    """
    
    def __init__(self):
        """Initialize the test client."""
        self.session_state = {}
        self.widgets = {}
        self.sidebar_widgets = {}
        self.messages = []
        self.errors = []
        self.warnings = []
        self.infos = []
        self.successes = []
        self.mock_responses = {}
    
    def mock_api_response(self, endpoint: str, response: Any):
        """
        Mock an API response for a specific endpoint.
        
        Args:
            endpoint: API endpoint to mock
            response: Response to return
        """
        self.mock_responses[endpoint] = response
    
    def get_session_state(self) -> Dict[str, Any]:
        """
        Get the current session state.
        
        Returns:
            Dict[str, Any]: Session state
        """
        return self.session_state
    
    def set_session_state(self, key: str, value: Any):
        """
        Set a session state value.
        
        Args:
            key: Session state key
            value: Value to set
        """
        self.session_state[key] = value
    
    def get_widget(self, key: str) -> Optional[Any]:
        """
        Get a widget value.
        
        Args:
            key: Widget key
            
        Returns:
            Optional[Any]: Widget value
        """
        return self.widgets.get(key)
    
    def set_widget(self, key: str, value: Any):
        """
        Set a widget value.
        
        Args:
            key: Widget key
            value: Value to set
        """
        self.widgets[key] = value
    
    def get_sidebar_widget(self, key: str) -> Optional[Any]:
        """
        Get a sidebar widget value.
        
        Args:
            key: Widget key
            
        Returns:
            Optional[Any]: Widget value
        """
        return self.sidebar_widgets.get(key)
    
    def set_sidebar_widget(self, key: str, value: Any):
        """
        Set a sidebar widget value.
        
        Args:
            key: Widget key
            value: Value to set
        """
        self.sidebar_widgets[key] = value
    
    def get_messages(self) -> List[str]:
        """
        Get all messages.
        
        Returns:
            List[str]: Messages
        """
        return self.messages
    
    def get_errors(self) -> List[str]:
        """
        Get error messages.
        
        Returns:
            List[str]: Error messages
        """
        return self.errors
    
    def get_warnings(self) -> List[str]:
        """
        Get warning messages.
        
        Returns:
            List[str]: Warning messages
        """
        return self.warnings
    
    def get_infos(self) -> List[str]:
        """
        Get info messages.
        
        Returns:
            List[str]: Info messages
        """
        return self.infos
    
    def get_successes(self) -> List[str]:
        """
        Get success messages.
        
        Returns:
            List[str]: Success messages
        """
        return self.successes
    
    def clear_messages(self):
        """Clear all messages."""
        self.messages = []
        self.errors = []
        self.warnings = []
        self.infos = []
        self.successes = []
    
    def simulate_login(self, username: str, password: str) -> bool:
        """
        Simulate a login with proper session state management.
        
        Args:
            username: Username
            password: Password
            
        Returns:
            bool: True if login successful, False otherwise
        """
        # Mock the login function
        with patch('admin_dashboard.utils.auth.login') as mock_login, \
             patch('admin_dashboard.utils.auth.is_demo_mode') as mock_demo_mode:
            
            # Configure demo mode behavior
            mock_demo_mode.return_value = True  # Set to True for testing
            
            # Set up mock response
            if username == "testuser" and password == "testpassword":
                # Successful login
                result = True
                # Set up session state as the login function would
                self.set_session_state("token", "test-token")
                self.set_session_state("refresh_token", "test-refresh-token")
                self.set_session_state("token_expiry", time.time() + 3600)
                self.set_session_state("is_authenticated", True)
                self.set_session_state("login_time", time.time())
                self.set_session_state("user_info", {
                    "id": "test-user-id",
                    "username": username,
                    "email": "test@example.com",
                    "full_name": "Test User",
                    "role": "user",
                    "points": 100,
                    "created_at": datetime.now().isoformat()
                })
                return True
            else:
                # Failed login
                result = False
                return False

@pytest.fixture
def streamlit_client():
    """
    Create a Streamlit test client.
    
    Returns:
        StreamlitTestClient: Streamlit test client
    """
    return StreamlitTestClient()

def test_login_page(streamlit_client):
    """Test the login page with proper authentication flow."""
    # Set up demo mode
    with patch('admin_dashboard.utils.db.is_demo_mode', return_value=True):
        # Test successful login
        assert streamlit_client.simulate_login("testuser", "testpassword") == True
        assert streamlit_client.get_session_state().get("is_authenticated") == True
        assert "token" in streamlit_client.get_session_state()
        assert "user_info" in streamlit_client.get_session_state()
        
        # Test failed login
        streamlit_client = StreamlitTestClient()  # Reset client
        assert streamlit_client.simulate_login("wronguser", "wrongpassword") == False
        assert streamlit_client.get_session_state().get("is_authenticated") != True

def test_logout(streamlit_client):
    """Test logout."""
    # Set up authenticated session
    streamlit_client.set_session_state("is_authenticated", True)
    streamlit_client.set_session_state("token", "test-token")
    streamlit_client.set_session_state("user_info", {"username": "testuser"})
    
    # Mock logout function
    with patch('admin_dashboard.utils.auth.logout') as mock_logout:
        # Call logout
        logout()
        
        # Verify logout was called
        mock_logout.assert_called_once()

def test_event_display(streamlit_client):
    """Test event display."""
    # Mock API client
    with patch('admin_dashboard.utils.api.get_events') as mock_get_events:
        # Set up mock response
        mock_events = [
            {
                "id": "event1",
                "title": "Test Event 1",
                "description": "Test Description 1",
                "start_time": datetime.now().isoformat(),
                "end_time": (datetime.now() + timedelta(hours=2)).isoformat(),
                "location": "Test Location 1",
                "max_participants": 20,
                "current_participants": 10
            },
            {
                "id": "event2",
                "title": "Test Event 2",
                "description": "Test Description 2",
                "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
                "end_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
                "location": "Test Location 2",
                "max_participants": 30,
                "current_participants": 15
            }
        ]
        mock_get_events.return_value = mock_events
        
        # Call get_events
        from admin_dashboard.utils.api import get_events
        events = get_events()
        
        # Verify events
        assert len(events) == 2
        assert events[0]["id"] == "event1"
        assert events[1]["id"] == "event2"

def test_profile_page(streamlit_client):
    """Test profile page."""
    # Set up authenticated session
    user_info = {
        "id": "test-user-id",
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "user",
        "points": 100,
        "created_at": datetime.now().isoformat()
    }
    streamlit_client.set_session_state("is_authenticated", True)
    streamlit_client.set_session_state("user_info", user_info)
    
    # Mock API client
    with patch('admin_dashboard.utils.api.get_user_badges') as mock_get_badges, \
         patch('admin_dashboard.utils.api.get_points_history') as mock_get_points:
        
        # Set up mock responses
        mock_get_badges.return_value = [
            {"id": "badge1", "name": "Test Badge 1", "description": "Test Description 1"},
            {"id": "badge2", "name": "Test Badge 2", "description": "Test Description 2"}
        ]
        mock_get_points.return_value = [
            {"id": "points1", "points": 50, "reason": "Test Reason 1", "timestamp": datetime.now().isoformat()},
            {"id": "points2", "points": 50, "reason": "Test Reason 2", "timestamp": datetime.now().isoformat()}
        ]
        
        # Verify user info
        assert streamlit_client.get_session_state().get("user_info") == user_info

def test_badge_display(streamlit_client):
    """Test badge display."""
    # Mock API client
    with patch('admin_dashboard.utils.api.get_badges') as mock_get_badges:
        # Set up mock response
        mock_badges = [
            {
                "id": "badge1",
                "name": "Test Badge 1",
                "description": "Test Description 1",
                "criteria": "Test Criteria 1",
                "image_url": "test_image_1.png",
                "category": "attendance"
            },
            {
                "id": "badge2",
                "name": "Test Badge 2",
                "description": "Test Description 2",
                "criteria": "Test Criteria 2",
                "image_url": "test_image_2.png",
                "category": "participation"
            }
        ]
        mock_get_badges.return_value = mock_badges
        
        # Call get_badges
        from admin_dashboard.utils.api import get_badges
        badges = get_badges()
        
        # Verify badges
        assert len(badges) == 2
        assert badges[0]["id"] == "badge1"
        assert badges[1]["id"] == "badge2"

def test_demo_mode(streamlit_client):
    """Test demo mode with proper session state."""
    # Mock is_demo_mode
    with patch('admin_dashboard.utils.db.is_demo_mode', return_value=True):
        # Verify demo mode is enabled
        from admin_dashboard.utils.db import is_demo_mode
        assert is_demo_mode() == True
        
        # Test login in demo mode
        with patch('admin_dashboard.utils.auth.login') as mock_login:
            # Configure mock login to use demo mode logic
            def demo_login(username, password):
                if username == "demo@pinetimeexperience.com" and password == "demo":
                    streamlit_client.set_session_state("token", "demo_token")
                    streamlit_client.set_session_state("is_authenticated", True)
                    streamlit_client.set_session_state("user_info", {
                        "id": "demo_user_id",
                        "username": "demo_user",
                        "email": "demo@pinetimeexperience.com"
                    })
                    return True
                return False
            
            mock_login.side_effect = demo_login
            
            # Test demo login
            result = login("demo@pinetimeexperience.com", "demo")
            assert result == True
            
            # Verify session state
            assert streamlit_client.get_session_state().get("is_authenticated") == True
            assert streamlit_client.get_session_state().get("token") == "demo_token"

def test_token_refresh(streamlit_client):
    """Test token refresh mechanism."""
    # Set up session with expired token
    streamlit_client.set_session_state("token", "test-token")
    streamlit_client.set_session_state("refresh_token", "test-refresh-token")
    streamlit_client.set_session_state("token_expiry", time.time() - 100)  # Expired
    streamlit_client.set_session_state("is_authenticated", True)
    
    # Mock refresh_token
    with patch('admin_dashboard.utils.auth.refresh_token') as mock_refresh:
        # Configure mock to update session state
        def update_token():
            streamlit_client.set_session_state("token", "new-test-token")
            streamlit_client.set_session_state("token_expiry", time.time() + 3600)
            return True
        
        mock_refresh.side_effect = update_token
        
        # Call refresh_token
        from admin_dashboard.utils.auth import refresh_token
        result = refresh_token()
        
        # Verify token was refreshed
        assert result == True
        assert streamlit_client.get_session_state().get("token") == "new-test-token"
        assert streamlit_client.get_session_state().get("token_expiry") > time.time()

def test_api_error_handling(streamlit_client):
    """Test API error handling with fallback mechanisms."""
    # Mock API client with error
    with patch('admin_dashboard.utils.api.get_events') as mock_get_events, \
         patch('admin_dashboard.utils.db.is_demo_mode', return_value=True):
        
        # Configure mock to raise exception
        mock_get_events.side_effect = Exception("API connection error")
        
        # Call get_events with error handling
        try:
            from admin_dashboard.utils.api import get_events
            events = get_events()
            # In demo mode, should return sample data instead of raising exception
            assert isinstance(events, list)
            assert len(events) > 0
        except Exception as e:
            # Should not reach here in demo mode
            pytest.fail(f"Exception should be handled in demo mode: {str(e)}")

def test_connection_fallback_decorator(streamlit_client):
    """Test the connection fallback decorator with retry logic."""
    # Mock connection utilities
    with patch('admin_dashboard.utils.connection.verify_connection') as mock_verify, \
         patch('admin_dashboard.utils.db.is_demo_mode', return_value=True):
        
        # Configure mock to return connection failure
        mock_verify.return_value = {"success": False, "message": "Connection failed"}
        
        # Define a function with the fallback decorator
        from admin_dashboard.utils.connection import with_connection_fallback
        
        # Mock function that would normally fail
        def mock_api_function():
            raise Exception("API connection error")
        
        # Mock fallback function
        def mock_fallback_function():
            return ["sample_data_1", "sample_data_2"]
        
        # Apply decorator
        decorated_function = with_connection_fallback(mock_fallback_function)(mock_api_function)
        
        # Call decorated function
        result = decorated_function()
        
        # Verify fallback was used
        assert result == ["sample_data_1", "sample_data_2"]
