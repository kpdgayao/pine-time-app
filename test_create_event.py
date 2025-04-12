"""
Test script to create an event with the correct field names.
This script bypasses the admin dashboard UI and directly calls the API.
"""

import os
import sys
import requests
import json
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("test_create_event")

# Add admin_dashboard to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin_dashboard"))
from utils.auth import login, get_auth_header
from config import API_ENDPOINTS

def test_create_event():
    """Test creating an event with the correct field names"""
    # Login to get authentication token
    username = input("Enter username: ")
    password = input("Enter password: ")
    
    if not login(username, password):
        logger.error("Login failed")
        return
    
    logger.info("Login successful")
    
    # Create event data with correct field names
    start_time = datetime.now() + timedelta(days=7)
    end_time = start_time + timedelta(hours=2)
    
    event_data = {
        "title": "Test Event",
        "description": "This is a test event",
        "event_type": "regular",
        "location": "Test Location",
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "max_participants": 20,
        "points_reward": 50,
        "status": "active",
        "tags": ["test", "demo"],
        "image_url": None
    }
    
    logger.info(f"Creating event with data: {json.dumps(event_data, indent=2)}")
    
    # Get authentication header
    auth_header = get_auth_header()
    
    # Make request to create event
    try:
        response = requests.post(
            API_ENDPOINTS["events"]["create"],
            json=event_data,
            headers=auth_header,
            timeout=10
        )
        
        logger.info(f"Response status code: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            logger.info("Event created successfully")
            logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            logger.error(f"Failed to create event: {response.status_code}")
            try:
                error_data = response.json()
                logger.error(f"Error details: {json.dumps(error_data, indent=2)}")
            except:
                logger.error(f"Error response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error creating event: {str(e)}")
        return False

if __name__ == "__main__":
    test_create_event()
