"""
Tests for users API endpoints.
"""

import pytest
import logging
from typing import Dict, Any
import uuid

from admin_dashboard.config import API_ENDPOINTS
from admin_dashboard.utils.api import APIError

# Configure logging
logger = logging.getLogger("test_users_api")

def test_get_current_user(api_client, auth_headers):
    """Test getting current user profile."""
    # Act
    try:
        response = api_client.get(
            API_ENDPOINTS["users"]["profile"],
            headers=auth_headers
        )
        
        # Assert
        assert response is not None
        assert "id" in response
        assert "email" in response
        assert "username" in response
        assert "full_name" in response
        assert "is_active" in response
        assert "is_superuser" in response
        assert "created_at" in response
    except APIError as e:
        pytest.fail(f"Get current user failed with error: {str(e)}")

def test_get_user_points(api_client, auth_headers):
    """Test getting user points."""
    # First get current user ID
    user_response = api_client.get(
        API_ENDPOINTS["users"]["profile"],
        headers=auth_headers
    )
    user_id = user_response["id"]
    
    # Act
    try:
        response = api_client.get(
            API_ENDPOINTS["users"]["points"].format(user_id=user_id),
            headers=auth_headers
        )
        
        # Assert
        assert response is not None
        # Check if response is a list or has 'items' key (paginated)
        if isinstance(response, dict) and "items" in response:
            # Paginated response
            assert "items" in response
            assert "total" in response
            points_transactions = response["items"]
        else:
            # Direct list response
            points_transactions = response
        
        assert isinstance(points_transactions, list)
        
        # If points transactions exist, check structure
        if points_transactions:
            transaction = points_transactions[0]
            assert "id" in transaction
            assert "user_id" in transaction
            assert "points" in transaction
            assert "transaction_type" in transaction
            assert "description" in transaction
            assert "created_at" in transaction
    except APIError as e:
        pytest.fail(f"Get user points failed with error: {str(e)}")

def test_get_user_badges(api_client, auth_headers):
    """Test getting user badges."""
    # First get current user ID
    user_response = api_client.get(
        API_ENDPOINTS["users"]["profile"],
        headers=auth_headers
    )
    user_id = user_response["id"]
    
    # Act
    try:
        response = api_client.get(
            API_ENDPOINTS["users"]["badges"].format(user_id=user_id),
            headers=auth_headers
        )
        
        # Assert
        assert response is not None
        # Check if response is a list or has 'items' key (paginated)
        if isinstance(response, dict) and "items" in response:
            # Paginated response
            assert "items" in response
            badges = response["items"]
        else:
            # Direct list response
            badges = response
        
        assert isinstance(badges, list)
        
        # If badges exist, check structure
        if badges:
            badge = badges[0]
            assert "id" in badge
            assert "name" in badge
            assert "description" in badge
            assert "category" in badge
            assert "level" in badge
    except APIError as e:
        pytest.fail(f"Get user badges failed with error: {str(e)}")

def test_get_user_events(api_client, auth_headers):
    """Test getting user events."""
    # First get current user ID
    user_response = api_client.get(
        API_ENDPOINTS["users"]["profile"],
        headers=auth_headers
    )
    user_id = user_response["id"]
    
    # Act
    try:
        response = api_client.get(
            API_ENDPOINTS["users"]["events"].format(user_id=user_id),
            headers=auth_headers
        )
        
        # Assert
        assert response is not None
        # Check if response is a list or has 'items' key (paginated)
        if isinstance(response, dict) and "items" in response:
            # Paginated response
            assert "items" in response
            events = response["items"]
        else:
            # Direct list response
            events = response
        
        assert isinstance(events, list)
        
        # If events exist, check structure
        if events:
            event = events[0]
            assert "id" in event
            assert "title" in event
            assert "description" in event
            assert "start_time" in event
            assert "end_time" in event
    except APIError as e:
        pytest.fail(f"Get user events failed with error: {str(e)}")

def test_register_new_user(api_client, test_db_transaction):
    """Test registering a new user."""
    # Generate unique username and email
    unique_id = str(uuid.uuid4())[:8]
    username = f"testuser_{unique_id}"
    email = f"test_{unique_id}@example.com"
    
    # Arrange
    user_data = {
        "username": username,
        "email": email,
        "password": "Test@password123",
        "full_name": "Test User"
    }
    
    # Act
    try:
        response = api_client.post(
            API_ENDPOINTS["users"]["register"],
            json_data=user_data,
            with_auth=False
        )
        
        # Assert
        assert response is not None
        assert "id" in response
        assert "email" in response
        assert response["email"] == email
        assert "username" in response
        assert response["username"] == username
        assert "full_name" in response
        assert response["full_name"] == user_data["full_name"]
        assert "is_active" in response
        assert response["is_active"] is True
        assert "is_superuser" in response
        assert response["is_superuser"] is False
        assert "created_at" in response
        
        # Password should not be returned
        assert "password" not in response
        assert "hashed_password" not in response
    except APIError as e:
        pytest.fail(f"Register new user failed with error: {str(e)}")

def test_register_duplicate_user(api_client, test_user_credentials):
    """Test registering a user with duplicate username or email."""
    # Arrange
    user_data = {
        "username": test_user_credentials["username"],
        "email": test_user_credentials["email"],
        "password": "Test@password123",
        "full_name": "Duplicate Test User"
    }
    
    # Act & Assert
    with pytest.raises(APIError) as excinfo:
        api_client.post(
            API_ENDPOINTS["users"]["register"],
            json_data=user_data,
            with_auth=False
        )
    
    # Check status code
    assert excinfo.value.status_code == 400
    
    # Try with just duplicate email
    user_data["username"] = f"unique_{str(uuid.uuid4())[:8]}"
    
    with pytest.raises(APIError) as excinfo:
        api_client.post(
            API_ENDPOINTS["users"]["register"],
            json_data=user_data,
            with_auth=False
        )
    
    # Check status code
    assert excinfo.value.status_code == 400
    
    # Try with just duplicate username
    user_data["username"] = test_user_credentials["username"]
    user_data["email"] = f"unique_{str(uuid.uuid4())[:8]}@example.com"
    
    with pytest.raises(APIError) as excinfo:
        api_client.post(
            API_ENDPOINTS["users"]["register"],
            json_data=user_data,
            with_auth=False
        )
    
    # Check status code
    assert excinfo.value.status_code == 400

def test_update_user_profile(api_client, auth_headers):
    """Test updating user profile."""
    # First get current user ID
    user_response = api_client.get(
        API_ENDPOINTS["users"]["profile"],
        headers=auth_headers
    )
    user_id = user_response["id"]
    
    # Arrange
    update_data = {
        "full_name": f"Updated Name {str(uuid.uuid4())[:8]}"
    }
    
    # Act
    try:
        response = api_client.put(
            API_ENDPOINTS["users"]["update"].format(user_id=user_id),
            json_data=update_data,
            headers=auth_headers
        )
        
        # Assert
        assert response is not None
        assert "id" in response
        assert response["id"] == user_id
        assert "full_name" in response
        assert response["full_name"] == update_data["full_name"]
    except APIError as e:
        pytest.fail(f"Update user profile failed with error: {str(e)}")

def test_null_user_id_handling(api_client, auth_headers, test_db_transaction):
    """Test that the API properly handles null user_id values."""
    # First get a future event ID
    cursor = test_db_transaction.cursor()
    cursor.execute("""
        SELECT id FROM events 
        WHERE start_time > NOW() 
        ORDER BY start_time ASC 
        LIMIT 1
    """)
    result = cursor.fetchone()
    
    if not result:
        pytest.skip("No future events found in database")
    
    event_id = result["id"]
    
    # Act - Try to register with null user_id
    # This should use the current user from auth token
    try:
        response = api_client.post(
            API_ENDPOINTS["events"]["register"].format(event_id=event_id),
            json_data={"user_id": None},  # Explicitly set null
            headers=auth_headers
        )
        
        # Assert
        assert response is not None
        assert "id" in response
        assert "event_id" in response
        assert response["event_id"] == event_id
        assert "user_id" in response
        assert response["user_id"] is not None  # Should not be null
    except APIError as e:
        # Check if it's already registered error
        if e.status_code == 400 and "already registered" in str(e.message).lower():
            pytest.skip("User already registered for this event")
        # Check if it's a null constraint error
        elif e.status_code == 400 and "null" in str(e.message).lower():
            pytest.fail(f"API failed to handle null user_id: {str(e)}")
        else:
            pytest.fail(f"Register with null user_id failed with error: {str(e)}")