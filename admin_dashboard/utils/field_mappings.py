"""
Field mapping utilities for the Pine Time Admin Dashboard.
Handles consistent field name transformations between UI and API.
"""

from typing import Dict, Any
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("field_mappings")

# Define field mappings for different entity types
# UI field name -> API field name
UI_TO_API_FIELD_MAPPINGS = {
    "name": "title",
    "date": "start_time",
    "capacity": "max_participants",
    "points": "points_reward"
}

# API field name -> UI field name
API_TO_UI_FIELD_MAPPINGS = {
    "title": "name",
    "start_time": "date",
    "max_participants": "capacity",
    "points_reward": "points"
}

def transform_event_data_for_api(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform event data from UI field names to API field names.
    
    Args:
        event_data: Event data with UI field names
        
    Returns:
        Dict[str, Any]: Event data with API field names
    """
    transformed_data = {}
    
    # Copy all fields, transforming names as needed
    for key, value in event_data.items():
        if key in UI_TO_API_FIELD_MAPPINGS:
            # Transform UI field name to API field name
            transformed_data[UI_TO_API_FIELD_MAPPINGS[key]] = value
        else:
            # Keep the field name as is if not in mapping
            transformed_data[key] = value
    
    # Ensure required fields are present
    if "title" not in transformed_data and "name" in event_data:
        transformed_data["title"] = event_data["name"]
        
    if "event_type" not in transformed_data:
        transformed_data["event_type"] = "regular"
        
    if "start_time" not in transformed_data and "date" in event_data:
        transformed_data["start_time"] = event_data["date"]
        
    if "end_time" not in transformed_data:
        # Try to calculate end_time from start_time and duration
        if "date" in event_data and "duration" in event_data:
            try:
                start_time = datetime.fromisoformat(event_data["date"])
                duration_hours = float(event_data["duration"])
                end_time = start_time + timedelta(hours=duration_hours)
                transformed_data["end_time"] = end_time.isoformat()
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not calculate end_time from date and duration: {str(e)}")
                
        # If we still don't have end_time, use start_time + 2 hours
        if "end_time" not in transformed_data and "start_time" in transformed_data:
            try:
                start_time = datetime.fromisoformat(transformed_data["start_time"])
                end_time = start_time + timedelta(hours=2)
                transformed_data["end_time"] = end_time.isoformat()
            except (ValueError, TypeError) as e:
                logger.warning(f"Could not calculate end_time from start_time: {str(e)}")
                
        # Last resort: use current time + 2 hours
        if "end_time" not in transformed_data:
            end_time = datetime.now() + timedelta(hours=2)
            transformed_data["end_time"] = end_time.isoformat()
    
    # Log the transformation for debugging
    logger.info(f"Original event data: {event_data}")
    logger.info(f"Transformed event data: {transformed_data}")
    
    return transformed_data

def transform_event_data_for_ui(event_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform event data from API field names to UI field names.
    
    Args:
        event_data: Event data with API field names
        
    Returns:
        Dict[str, Any]: Event data with UI field names
    """
    transformed_data = {}
    
    # Copy all fields, transforming names as needed
    for key, value in event_data.items():
        if key in API_TO_UI_FIELD_MAPPINGS:
            # Transform API field name to UI field name
            transformed_data[API_TO_UI_FIELD_MAPPINGS[key]] = value
        else:
            # Keep the field name as is if not in mapping
            transformed_data[key] = value
    
    # Log the transformation for debugging
    logger.info(f"API data: {event_data}")
    logger.info(f"Transformed for UI: {transformed_data}")
    
    return transformed_data
