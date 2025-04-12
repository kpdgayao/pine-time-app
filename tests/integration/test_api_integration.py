"""
Integration tests for API and database interactions.
Tests the complete flow from API to database and back.
"""

import pytest
import logging
from typing import Dict, Any
import uuid
from datetime import datetime, timedelta

from admin_dashboard.config import API_ENDPOINTS
from admin_dashboard.utils.api import APIError

# Configure logging
logger = logging.getLogger("test_api_integration")

def test_event_registration_flow(api_client, admin_auth_headers, auth_headers, test_db_transaction):
    """Test the complete event registration flow."""
    # Step 1: Admin creates a new event
    start_time = datetime.now() + timedelta(days=1)
    end_time = start_time + timedelta(hours=2)
    
    event_data = {
        "title": f"Integration Test Event {uuid.uuid4()}",
        "description": "This is an integration test event",
        "event_type": "workshop",
        "location": "Test Location",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "max_participants": 20,
        "points_reward": 10
    }
    
    # Create event
    event = api_client.post(
        API_ENDPOINTS["events"]["create"],
        json_data=event_data,
        headers=admin_auth_headers
    )
    
    assert event is not None
    assert "id" in event
    event_id = event["id"]
    
    # Step 2: User registers for the event
    registration = api_client.post(
        API_ENDPOINTS["events"]["register"].format(event_id=event_id),
        headers=auth_headers
    )
    
    assert registration is not None
    assert "id" in registration
    assert "event_id" in registration
    assert registration["event_id"] == event_id
    assert "user_id" in registration
    assert "registration_date" in registration
    
    # Step 3: Verify the event appears in the user's events
    user_profile = api_client.get(
        API_ENDPOINTS["users"]["profile"],
        headers=auth_headers
    )
    user_id = user_profile["id"]
    
    user_events = api_client.get(
        API_ENDPOINTS["users"]["events"].format(user_id=user_id),
        headers=auth_headers
    )
    
    # Handle both paginated and non-paginated responses
    if isinstance(user_events, dict) and "items" in user_events:
        events_list = user_events["items"]
    else:
        events_list = user_events
    
    # Find our event in the list
    found_event = False
    for user_event in events_list:
        if user_event["id"] == event_id:
            found_event = True
            break
    
    assert found_event, "Event not found in user's events"
    
    # Step 4: Admin checks in the user
    checkin_response = api_client.post(
        API_ENDPOINTS["events"]["check_in"].format(event_id=event_id),
        json_data={"user_id": user_id},
        headers=admin_auth_headers
    )
    
    assert checkin_response is not None
    assert "success" in checkin_response
    assert checkin_response["success"] is True
    assert "points_awarded" in checkin_response
    
    # Step 5: Verify points were awarded
    points_history = api_client.get(
        API_ENDPOINTS["users"]["points"].format(user_id=user_id),
        headers=auth_headers
    )
    
    # Handle both paginated and non-paginated responses
    if isinstance(points_history, dict) and "items" in points_history:
        transactions = points_history["items"]
    else:
        transactions = points_history
    
    # Find the points transaction for our event
    found_transaction = False
    for transaction in transactions:
        if transaction["description"] and event_id in transaction["description"]:
            found_transaction = True
            assert transaction["points"] > 0
            break
    
    assert found_transaction, "Points transaction not found for event check-in"

def test_badge_award_flow(api_client, admin_auth_headers, auth_headers, test_db_transaction):
    """Test the badge award flow."""
    # Step 1: Get current user
    user_profile = api_client.get(
        API_ENDPOINTS["users"]["profile"],
        headers=auth_headers
    )
    user_id = user_profile["id"]
    
    # Step 2: Get available badges
    badges = api_client.get(
        API_ENDPOINTS["badges"]["list"],
        headers=auth_headers
    )
    
    # Handle both paginated and non-paginated responses
    if isinstance(badges, dict) and "items" in badges:
        badges_list = badges["items"]
    else:
        badges_list = badges
    
    assert len(badges_list) > 0, "No badges available for testing"
    
    # Select a badge
    test_badge = badges_list[0]
    badge_id = test_badge["id"]
    
    # Step 3: Admin awards badge to user
    award_data = {
        "user_id": user_id,
        "badge_id": badge_id
    }
    
    award_response = api_client.post(
        API_ENDPOINTS["badges"]["award"],
        json_data=award_data,
        headers=admin_auth_headers
    )
    
    assert award_response is not None
    assert "success" in award_response
    assert award_response["success"] is True
    
    # Step 4: Verify badge appears in user's badges
    user_badges = api_client.get(
        API_ENDPOINTS["users"]["badges"].format(user_id=user_id),
        headers=auth_headers
    )
    
    # Handle both paginated and non-paginated responses
    if isinstance(user_badges, dict) and "items" in user_badges:
        badges_list = user_badges["items"]
    else:
        badges_list = user_badges
    
    # Find our badge in the list
    found_badge = False
    for user_badge in badges_list:
        if user_badge["id"] == badge_id:
            found_badge = True
            break
    
    assert found_badge, "Badge not found in user's badges"
    
    # Step 5: Verify points were awarded for the badge
    points_history = api_client.get(
        API_ENDPOINTS["users"]["points"].format(user_id=user_id),
        headers=auth_headers
    )
    
    # Handle both paginated and non-paginated responses
    if isinstance(points_history, dict) and "items" in points_history:
        transactions = points_history["items"]
    else:
        transactions = points_history
    
    # Find the points transaction for our badge
    found_transaction = False
    for transaction in transactions:
        if transaction["description"] and "badge" in transaction["description"].lower() and badge_id in transaction["description"]:
            found_transaction = True
            assert transaction["points"] > 0
            break
    
    assert found_transaction, "Points transaction not found for badge award"

def test_error_handling_integration(api_client, auth_headers):
    """Test error handling across the API integration."""
    # Test 1: Try to access non-existent event
    non_existent_id = str(uuid.uuid4())
    
    with pytest.raises(APIError) as excinfo:
        api_client.get(
            API_ENDPOINTS["events"]["detail"].format(event_id=non_existent_id),
            headers=auth_headers
        )
    
    assert excinfo.value.status_code == 404
    
    # Test 2: Try to register for non-existent event
    with pytest.raises(APIError) as excinfo:
        api_client.post(
            API_ENDPOINTS["events"]["register"].format(event_id=non_existent_id),
            headers=auth_headers
        )
    
    assert excinfo.value.status_code == 404
    
    # Test 3: Try to check in for non-existent event
    user_profile = api_client.get(
        API_ENDPOINTS["users"]["profile"],
        headers=auth_headers
    )
    user_id = user_profile["id"]
    
    with pytest.raises(APIError) as excinfo:
        api_client.post(
            API_ENDPOINTS["events"]["check_in"].format(event_id=non_existent_id),
            json_data={"user_id": user_id},
            headers=auth_headers
        )
    
    assert excinfo.value.status_code == 404

def test_api_response_format_handling(api_client, auth_headers):
    """Test that the API client correctly handles different response formats."""
    # Test with events endpoint
    events_response = api_client.get(
        API_ENDPOINTS["events"]["list"],
        headers=auth_headers
    )
    
    # Handle both paginated and non-paginated responses
    if isinstance(events_response, dict) and "items" in events_response:
        # Paginated response
        assert "items" in events_response
        assert isinstance(events_response["items"], list)
        events = events_response["items"]
    else:
        # Direct list response
        assert isinstance(events_response, list)
        events = events_response
    
    # Test with badges endpoint
    badges_response = api_client.get(
        API_ENDPOINTS["badges"]["list"],
        headers=auth_headers
    )
    
    # Handle both paginated and non-paginated responses
    if isinstance(badges_response, dict) and "items" in badges_response:
        # Paginated response
        assert "items" in badges_response
        assert isinstance(badges_response["items"], list)
        badges = badges_response["items"]
    else:
        # Direct list response
        assert isinstance(badges_response, list)
        badges = badges_response
    
    # Test with users endpoint (if admin)
    try:
        users_response = api_client.get(
            API_ENDPOINTS["users"]["list"],
            headers=auth_headers
        )
        
        # Handle both paginated and non-paginated responses
        if isinstance(users_response, dict) and "items" in users_response:
            # Paginated response
            assert "items" in users_response
            assert isinstance(users_response["items"], list)
        else:
            # Direct list response
            assert isinstance(users_response, list)
    except APIError as e:
        # May fail if not admin, that's OK
        if e.status_code != 403:
            raise