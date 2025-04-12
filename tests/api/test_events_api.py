"""
Tests for events API endpoints.
"""

import pytest
import logging
from typing import Dict, Any
from datetime import datetime, timedelta

from admin_dashboard.config import API_ENDPOINTS
from admin_dashboard.utils.api import APIError

# Configure logging
logger = logging.getLogger("test_events_api")

def test_list_events(api_client, auth_headers):
    """Test listing events."""
    # Act
    try:
        response = api_client.get(
            API_ENDPOINTS["events"]["list"],
            headers=auth_headers
        )
        
        # Assert
        assert response is not None
        # Check if response is a list or has 'items' key (paginated)
        if isinstance(response, dict) and "items" in response:
            # Paginated response
            assert "items" in response
            assert "total" in response
            assert "page" in response
            assert "size" in response
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
        pytest.fail(f"List events failed with error: {str(e)}")

def test_get_event_detail(api_client, auth_headers, test_db_connection):
    """Test getting event detail."""
    # First, get an event ID
    cursor = test_db_connection.cursor()
    cursor.execute("SELECT id FROM events LIMIT 1")
    result = cursor.fetchone()
    
    if not result:
        pytest.skip("No events found in database")
    
    event_id = result["id"]
    
    # Act
    try:
        response = api_client.get(
            API_ENDPOINTS["events"]["detail"].format(event_id=event_id),
            headers=auth_headers
        )
        
        # Assert
        assert response is not None
        assert "id" in response
        assert "title" in response
        assert "description" in response
        assert "start_time" in response
        assert "end_time" in response
        assert "location" in response
        assert "max_participants" in response
        assert response["id"] == event_id
    except APIError as e:
        pytest.fail(f"Get event detail failed with error: {str(e)}")

def test_create_event(api_client, admin_auth_headers, test_db_transaction):
    """Test creating an event."""
    # Arrange
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)
    
    event_data = {
        "title": "Test Event",
        "description": "This is a test event",
        "event_type": "workshop",
        "location": "Test Location",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "max_participants": 20,
        "points_reward": 10
    }
    
    # Act
    try:
        response = api_client.post(
            API_ENDPOINTS["events"]["create"],
            json_data=event_data,
            headers=admin_auth_headers
        )
        
        # Assert
        assert response is not None
        assert "id" in response
        assert "title" in response
        assert response["title"] == event_data["title"]
        assert "description" in response
        assert response["description"] == event_data["description"]
        assert "start_time" in response
        assert "end_time" in response
        assert "location" in response
        assert response["location"] == event_data["location"]
        assert "max_participants" in response
        assert response["max_participants"] == event_data["max_participants"]
        assert "points_reward" in response
        assert response["points_reward"] == event_data["points_reward"]
    except APIError as e:
        pytest.fail(f"Create event failed with error: {str(e)}")

def test_register_for_event(api_client, auth_headers, test_db_transaction):
    """Test registering for an event."""
    # First, get a future event ID
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
    
    # Act
    try:
        response = api_client.post(
            API_ENDPOINTS["events"]["register"].format(event_id=event_id),
            headers=auth_headers
        )
        
        # Assert
        assert response is not None
        assert "id" in response
        assert "event_id" in response
        assert response["event_id"] == event_id
        assert "user_id" in response
        assert "registration_date" in response
        assert "status" in response
    except APIError as e:
        # Check if it's already registered error
        if e.status_code == 400 and "already registered" in str(e.message).lower():
            pytest.skip("User already registered for this event")
        else:
            pytest.fail(f"Register for event failed with error: {str(e)}")

def test_register_for_past_event(api_client, auth_headers, test_db_transaction):
    """Test registering for a past event (should fail)."""
    # First, get a past event ID
    cursor = test_db_transaction.cursor()
    cursor.execute("""
        SELECT id FROM events 
        WHERE start_time < NOW() 
        ORDER BY start_time DESC 
        LIMIT 1
    """)
    result = cursor.fetchone()
    
    if not result:
        pytest.skip("No past events found in database")
    
    event_id = result["id"]
    
    # Act & Assert
    with pytest.raises(APIError) as excinfo:
        api_client.post(
            API_ENDPOINTS["events"]["register"].format(event_id=event_id),
            headers=auth_headers
        )
    
    # Check status code and error message
    assert excinfo.value.status_code == 400
    assert "past" in str(excinfo.value.message).lower()

def test_check_in_for_event(api_client, admin_auth_headers, test_db_transaction):
    """Test checking in for an event."""
    # First, get a current or future event ID and a user ID
    cursor = test_db_transaction.cursor()
    
    # Get event
    cursor.execute("""
        SELECT id FROM events 
        WHERE start_time <= NOW() + INTERVAL '1 hour' AND end_time >= NOW()
        LIMIT 1
    """)
    event_result = cursor.fetchone()
    
    if not event_result:
        pytest.skip("No current events found in database")
    
    event_id = event_result["id"]
    
    # Get a user
    cursor.execute("SELECT id FROM users LIMIT 1")
    user_result = cursor.fetchone()
    
    if not user_result:
        pytest.skip("No users found in database")
    
    user_id = user_result["id"]
    
    # Check if user is registered
    cursor.execute("""
        SELECT id FROM registrations
        WHERE event_id = %s AND user_id = %s
    """, (event_id, user_id))
    
    if not cursor.fetchone():
        # Register user
        cursor.execute("""
            INSERT INTO registrations (event_id, user_id, registration_date, status)
            VALUES (%s, %s, NOW(), 'registered')
        """, (event_id, user_id))
    
    # Act
    try:
        response = api_client.post(
            API_ENDPOINTS["events"]["check_in"].format(event_id=event_id),
            json_data={"user_id": user_id},
            headers=admin_auth_headers
        )
        
        # Assert
        assert response is not None
        assert "success" in response
        assert response["success"] is True
        assert "message" in response
        assert "points_awarded" in response
    except APIError as e:
        # Check if it's already checked in error
        if e.status_code == 400 and "already checked in" in str(e.message).lower():
            pytest.skip("User already checked in for this event")
        else:
            pytest.fail(f"Check in for event failed with error: {str(e)}")

def test_event_response_format_handling(api_client, auth_headers):
    """Test that the API client handles different response formats correctly."""
    # Act
    try:
        response = api_client.get(
            API_ENDPOINTS["events"]["list"],
            headers=auth_headers
        )
        
        # Assert
        assert response is not None
        
        # Check if response is a list or has 'items' key (paginated)
        if isinstance(response, dict) and "items" in response:
            # Paginated response
            assert "items" in response
            assert isinstance(response["items"], list)
        else:
            # Direct list response
            assert isinstance(response, list)
            
    except APIError as e:
        pytest.fail(f"Event response format test failed with error: {str(e)}")