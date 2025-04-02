"""
Connection testing utilities for the Pine Time User Interface.
Handles connection verification and fallback to sample data.
"""

import streamlit as st
import logging
import time
from typing import Dict, Any, Callable, Optional, TypeVar, List

from utils.api import check_api_connection
from utils.db import is_demo_mode, test_database_connection, get_database_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("connection_utils")

# Type variable for generic function return type
T = TypeVar('T')

# Cache connection status to avoid repeated checks
if "connection_status" not in st.session_state:
    st.session_state["connection_status"] = None
if "last_connection_check" not in st.session_state:
    st.session_state["last_connection_check"] = 0

def verify_connection(force: bool = False) -> Dict[str, Any]:
    """
    Verify API and database connections.
    
    Args:
        force: If True, force a new connection check even if cached.
        
    Returns:
        Dict with connection status information.
    """
    # Use cached result if available and not forcing refresh
    current_time = time.time()
    if (not force and 
        "connection_status" in st.session_state and 
        st.session_state["connection_status"] is not None and
        "last_connection_check" in st.session_state and
        current_time - st.session_state["last_connection_check"] < 300):  # 5 minutes cache
        return st.session_state["connection_status"]
    
    # Check if we're in demo mode
    demo_mode = is_demo_mode()
    
    # Initialize result
    result = {
        "success": False,
        "api_connected": False,
        "db_connected": False,
        "db_type": None,
        "message": "",
        "is_demo": demo_mode
    }
    
    # If in demo mode, we don't need to check connections
    if demo_mode:
        result["success"] = True
        result["message"] = "Running in demo mode"
        st.session_state["connection_status"] = result
        st.session_state["last_connection_check"] = current_time
        return result
    
    # Check API connection
    api_status = check_api_connection()
    result["api_connected"] = api_status.get("success", False)
    result["api_message"] = api_status.get("message", "")
    
    # Check database connection
    try:
        db_config = get_database_config()
        result["db_type"] = db_config.get("database_type", "unknown")
        
        # Test database connection
        db_version = test_database_connection()
        if db_version:
            result["db_connected"] = True
            result["db_version"] = db_version
        else:
            result["message"] += "Database connection failed. "
    except Exception as e:
        result["message"] += f"Database error: {str(e)}. "
        logger.error(f"Database connection error: {str(e)}")
    
    # Set overall success
    # We consider the connection successful if either:
    # 1. Both API and database are connected
    # 2. Database is connected (we can work with sample data for API)
    result["success"] = result["db_connected"]
    
    # If API is not connected but database is, we can still work with sample data
    if not result["api_connected"] and result["db_connected"]:
        result["message"] += "API connection failed. Using sample data for API requests. "
        logger.warning("API connection failed. Using sample data for API requests.")
    elif result["api_connected"] and result["db_connected"]:
        result["message"] = f"Connected to API and {result['db_type'].upper()} database"
    
    # Cache the result
    st.session_state["connection_status"] = result
    st.session_state["last_connection_check"] = current_time
    
    # Log connection status
    if result["success"]:
        logger.info(f"Connection verified: {result['message']}")
    else:
        logger.warning(f"Connection issues: {result['message']}")
    
    return result

def show_connection_status():
    """Display connection status in the UI"""
    status = verify_connection()
    
    if is_demo_mode():
        st.info("🔌 Running in demo mode. Using sample data.")
        return
    
    if status["success"]:
        st.success(f"✅ Connected to API and {status['db_type'].upper()} database")
        if status.get("db_version"):
            st.caption(f"Database version: {status['db_version']}")
    else:
        if status["api_connected"]:
            st.warning(f"⚠️ API connected but {status['db_type'].upper()} database connection failed. Using sample data.")
            if status.get("db_message"):
                st.caption(f"Error: {status['db_message']}")
        else:
            st.error("❌ API connection failed. Using sample data.")
            if status.get("api_message"):
                st.caption(f"Error: {status['api_message']}")

def with_connection_fallback(fallback_func: Callable[..., T]) -> Callable:
    """
    Decorator to execute a function with connection fallback.
    
    Args:
        fallback_func: Function to execute if connection fails
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            # In demo mode, always use fallback
            if is_demo_mode():
                return fallback_func(*args, **kwargs)
            
            # Verify connection
            status = verify_connection()
            
            # If connection is successful, use the main function
            if status["success"]:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logger.error(f"Error executing function {func.__name__}: {str(e)}")
                    return fallback_func(*args, **kwargs)
            
            # Otherwise use fallback
            return fallback_func(*args, **kwargs)
        return wrapper
    return decorator

def get_sample_users(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """Get sample users data"""
    sample_users = [
        {
            "id": f"user_{i}",
            "username": f"user{i}",
            "email": f"user{i}@example.com",
            "full_name": f"User {i}",
            "points": 500 - i * 25,
            "created_at": "2025-01-01T00:00:00",
            "is_active": True,
            "user_type": "regular"
        }
        for i in range(1, 21)
    ]
    
    # Calculate pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    items = sample_users[start_idx:end_idx]
    total = len(sample_users)
    pages = (total + page_size - 1) // page_size
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": page_size,
        "pages": pages
    }

def get_sample_events(page: int = 1, page_size: int = 20) -> Dict[str, Any]:
    """Get sample events data"""
    event_types = ["Trivia Night", "Game Night", "Murder Mystery", "Hiking", "Workshop", "Social Mixer"]
    locations = ["Main Hall", "Garden Terrace", "Conference Room A", "Outdoor Pavilion", "Lounge"]
    
    sample_events = [
        {
            "id": f"event_{i}",
            "title": f"{event_types[i % len(event_types)]} #{i}",
            "description": f"Join us for an exciting {event_types[i % len(event_types)].lower()} event!",
            "event_type": event_types[i % len(event_types)],
            "location": locations[i % len(locations)],
            "start_time": f"2025-04-{i % 30 + 1:02d}T18:00:00",
            "end_time": f"2025-04-{i % 30 + 1:02d}T20:00:00",
            "points": (i % 5 + 1) * 10,
            "capacity": 20,
            "registered_count": i % 15,
            "is_active": True
        }
        for i in range(1, 31)
    ]
    
    # Calculate pagination
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    items = sample_events[start_idx:end_idx]
    total = len(sample_events)
    pages = (total + page_size - 1) // page_size
    
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": page_size,
        "pages": pages
    }

def get_sample_user_profile() -> Dict[str, Any]:
    """Get sample user profile data"""
    return {
        "id": "current_user",
        "username": "current_user",
        "email": "user@example.com",
        "full_name": "Current User",
        "points": 425,
        "streak_days": 5,
        "created_at": "2025-01-15T00:00:00",
        "is_active": True,
        "user_type": "regular",
        "preferences": {
            "event_types": ["Trivia Night", "Game Night"],
            "notifications": True
        }
    }

def get_sample_user_badges() -> List[Dict[str, Any]]:
    """Get sample user badges data"""
    return [
        {
            "id": "badge_1",
            "name": "First Timer",
            "description": "Attended your first event",
            "category": "attendance",
            "level": "bronze",
            "points": 10,
            "earned_at": "2025-01-20T19:30:00"
        },
        {
            "id": "badge_2",
            "name": "Trivia Master",
            "description": "Won a trivia night event",
            "category": "achievement",
            "level": "silver",
            "points": 25,
            "earned_at": "2025-02-05T20:15:00"
        },
        {
            "id": "badge_3",
            "name": "Social Butterfly",
            "description": "Attended 5 different event types",
            "category": "attendance",
            "level": "bronze",
            "points": 15,
            "earned_at": "2025-02-28T18:45:00"
        },
        {
            "id": "badge_5",
            "name": "3-Day Streak",
            "description": "Attended events 3 days in a row",
            "category": "streak",
            "level": "bronze",
            "points": 20,
            "earned_at": "2025-03-15T19:00:00"
        }
    ]

def get_sample_user_events() -> Dict[str, List[Dict[str, Any]]]:
    """Get sample user events data"""
    upcoming_events = [
        {
            "id": "event_1",
            "title": "Trivia Night #12",
            "description": "Join us for an exciting trivia night event!",
            "event_type": "Trivia Night",
            "location": "Main Hall",
            "start_time": "2025-04-05T18:00:00",
            "end_time": "2025-04-05T20:00:00",
            "points": 20,
            "status": "registered"
        },
        {
            "id": "event_2",
            "title": "Game Night #8",
            "description": "Join us for a fun game night with board games and more!",
            "event_type": "Game Night",
            "location": "Lounge",
            "start_time": "2025-04-12T18:00:00",
            "end_time": "2025-04-12T21:00:00",
            "points": 30,
            "status": "registered"
        }
    ]
    
    past_events = [
        {
            "id": "event_3",
            "title": "Murder Mystery #4",
            "description": "Solve the mystery and have fun!",
            "event_type": "Murder Mystery",
            "location": "Conference Room A",
            "start_time": "2025-03-15T18:00:00",
            "end_time": "2025-03-15T21:00:00",
            "points": 40,
            "status": "completed",
            "points_earned": 40
        },
        {
            "id": "event_4",
            "title": "Trivia Night #10",
            "description": "Test your knowledge and win prizes!",
            "event_type": "Trivia Night",
            "location": "Main Hall",
            "start_time": "2025-03-22T18:00:00",
            "end_time": "2025-03-22T20:00:00",
            "points": 20,
            "status": "completed",
            "points_earned": 30  # Bonus points for winning
        },
        {
            "id": "event_5",
            "title": "Social Mixer #6",
            "description": "Meet new people and make connections!",
            "event_type": "Social Mixer",
            "location": "Garden Terrace",
            "start_time": "2025-03-29T17:00:00",
            "end_time": "2025-03-29T19:00:00",
            "points": 15,
            "status": "completed",
            "points_earned": 15
        }
    ]
    
    return {
        "upcoming": upcoming_events,
        "past": past_events
    }

def get_sample_points_history() -> List[Dict[str, Any]]:
    """Get sample points history data"""
    return [
        {
            "id": "points_1",
            "user_id": "current_user",
            "points": 40,
            "reason": "Completed Murder Mystery #4",
            "timestamp": "2025-03-15T21:00:00"
        },
        {
            "id": "points_2",
            "user_id": "current_user",
            "points": 30,
            "reason": "Completed Trivia Night #10 with bonus",
            "timestamp": "2025-03-22T20:00:00"
        },
        {
            "id": "points_3",
            "user_id": "current_user",
            "points": 15,
            "reason": "Completed Social Mixer #6",
            "timestamp": "2025-03-29T19:00:00"
        },
        {
            "id": "points_4",
            "user_id": "current_user",
            "points": 20,
            "reason": "Earned 3-Day Streak badge",
            "timestamp": "2025-03-15T19:00:00"
        },
        {
            "id": "points_5",
            "user_id": "current_user",
            "points": 10,
            "reason": "Earned First Timer badge",
            "timestamp": "2025-01-20T19:30:00"
        }
    ]

def get_sample_leaderboard() -> List[Dict[str, Any]]:
    """Get sample leaderboard data"""
    return [
        {"rank": 1, "user_id": "user_1", "username": "user1", "full_name": "User 1", "points": 500},
        {"rank": 2, "user_id": "user_2", "username": "user2", "full_name": "User 2", "points": 475},
        {"rank": 3, "user_id": "user_3", "username": "user3", "full_name": "User 3", "points": 450},
        {"rank": 4, "user_id": "current_user", "username": "current_user", "full_name": "Current User", "points": 425},
        {"rank": 5, "user_id": "user_4", "username": "user4", "full_name": "User 4", "points": 400},
        {"rank": 6, "user_id": "user_5", "username": "user5", "full_name": "User 5", "points": 375},
        {"rank": 7, "user_id": "user_6", "username": "user6", "full_name": "User 6", "points": 350},
        {"rank": 8, "user_id": "user_7", "username": "user7", "full_name": "User 7", "points": 325},
        {"rank": 9, "user_id": "user_8", "username": "user8", "full_name": "User 8", "points": 300},
        {"rank": 10, "user_id": "user_9", "username": "user9", "full_name": "User 9", "points": 275}
    ]

def get_sample_badges() -> List[Dict[str, Any]]:
    """Get sample badges data"""
    return [
        {
            "id": "badge_1",
            "name": "First Timer",
            "description": "Attended your first event",
            "category": "attendance",
            "level": "bronze",
            "points": 10,
            "image_url": None
        },
        {
            "id": "badge_2",
            "name": "Trivia Master",
            "description": "Won a trivia night event",
            "category": "achievement",
            "level": "silver",
            "points": 25,
            "image_url": None
        },
        {
            "id": "badge_3",
            "name": "Social Butterfly",
            "description": "Attended 5 different event types",
            "category": "attendance",
            "level": "bronze",
            "points": 15,
            "image_url": None
        },
        {
            "id": "badge_4",
            "name": "Event Organizer",
            "description": "Helped organize an event",
            "category": "contribution",
            "level": "gold",
            "points": 50,
            "image_url": None
        },
        {
            "id": "badge_5",
            "name": "3-Day Streak",
            "description": "Attended events 3 days in a row",
            "category": "streak",
            "level": "bronze",
            "points": 20,
            "image_url": None
        },
        {
            "id": "badge_6",
            "name": "7-Day Streak",
            "description": "Attended events 7 days in a row",
            "category": "streak",
            "level": "silver",
            "points": 40,
            "image_url": None
        },
        {
            "id": "badge_7",
            "name": "30-Day Streak",
            "description": "Attended events 30 days in a row",
            "category": "streak",
            "level": "gold",
            "points": 100,
            "image_url": None
        },
        {
            "id": "badge_8",
            "name": "Community Champion",
            "description": "Reached 1000 points",
            "category": "achievement",
            "level": "gold",
            "points": 75,
            "image_url": None
        }
    ]
