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
    Verify API and database connections with enhanced error handling and detailed diagnostics.
    
    Args:
        force: If True, force a new connection check even if cached.
        
    Returns:
        Dict with connection status information.
    """
    # Track verification time for performance monitoring
    verification_start = time.time()
    
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
    
    # Initialize result with detailed diagnostics
    result = {
        "success": False,
        "api_connected": False,
        "db_connected": False,
        "db_type": None,
        "message": "",
        "is_demo": demo_mode,
        "diagnostics": {
            "api": {},
            "database": {},
            "verification_time": 0
        }
    }
    
    # If in demo mode, we don't need to check connections
    if demo_mode:
        result["success"] = True
        result["message"] = "Running in demo mode"
        result["diagnostics"]["verification_time"] = time.time() - verification_start
        st.session_state["connection_status"] = result
        st.session_state["last_connection_check"] = current_time
        return result
    
    # Check API connection with timeout
    try:
        api_status = check_api_connection()
        result["api_connected"] = api_status.get("success", False)
        result["api_message"] = api_status.get("message", "")
        result["diagnostics"]["api"] = api_status
    except Exception as e:
        logger.error(f"Error checking API connection: {str(e)}")
        result["api_message"] = f"Error checking API: {str(e)}"
        result["diagnostics"]["api"]["error"] = str(e)
    
    # Check database connection with detailed diagnostics
    try:
        db_config = get_database_config()
        result["db_type"] = db_config.get("database_type", "unknown")
        result["diagnostics"]["database"]["type"] = result["db_type"]
        
        # Test database connection
        db_connection_start = time.time()
        db_version = test_database_connection()
        db_connection_time = time.time() - db_connection_start
        result["diagnostics"]["database"]["connection_time"] = db_connection_time
        
        if db_version:
            result["db_connected"] = True
            result["db_version"] = db_version
            result["diagnostics"]["database"]["version"] = db_version
            logger.info(f"Database connection successful in {db_connection_time:.2f}s")
        else:
            result["message"] += "Database connection failed. "
            result["diagnostics"]["database"]["error"] = "Connection test returned no version"
            logger.warning(f"Database connection failed after {db_connection_time:.2f}s")
            
            # Try to get more specific database error information
            if result["db_type"] == "postgresql":
                try:
                    import psycopg2
                    params = get_postgres_connection_params()
                    conn = psycopg2.connect(**params, connect_timeout=5)
                    conn.close()
                except Exception as db_e:
                    result["diagnostics"]["database"]["specific_error"] = str(db_e)
                    logger.error(f"PostgreSQL specific error: {str(db_e)}")
    except Exception as e:
        result["message"] += f"Database error: {str(e)}. "
        result["diagnostics"]["database"]["error"] = str(e)
        logger.error(f"Database connection error: {str(e)}")
    
    # Set overall success with fallback strategy
    # We consider the connection successful if either:
    # 1. Both API and database are connected (ideal)
    # 2. Database is connected (we can work with sample data for API)
    # 3. API is connected but database isn't (we can use in-memory storage)
    if result["db_connected"]:
        result["success"] = True
    elif result["api_connected"]:
        # Fallback to in-memory storage if API is available but database isn't
        result["success"] = True
        result["message"] += "Database connection failed. Using in-memory storage as fallback. "
        logger.warning("Database connection failed. Using in-memory storage as fallback.")
        result["diagnostics"]["fallback"] = "in_memory_storage"
    
    # Provide detailed status messages
    if not result["api_connected"] and result["db_connected"]:
        result["message"] += "API connection failed. Using sample data for API requests. "
        logger.warning("API connection failed. Using sample data for API requests.")
        result["diagnostics"]["fallback"] = "sample_api_data"
    elif result["api_connected"] and result["db_connected"]:
        result["message"] = f"Connected to API and {result['db_type'].upper()} database"
    elif not result["api_connected"] and not result["db_connected"]:
        result["message"] = "All connections failed. Using demo mode as fallback."
        logger.error("All connections failed. Using demo mode as fallback.")
        result["is_demo"] = True  # Force demo mode as ultimate fallback
        result["success"] = True  # Consider successful with demo fallback
        result["diagnostics"]["fallback"] = "forced_demo_mode"
    
    # Record verification time
    result["diagnostics"]["verification_time"] = time.time() - verification_start
    
    # Cache the result
    st.session_state["connection_status"] = result
    st.session_state["last_connection_check"] = current_time
    
    # Log connection status
    if result["success"]:
        logger.info(f"Connection verified in {result['diagnostics']['verification_time']:.2f}s: {result['message']}")
    else:
        logger.warning(f"Connection issues after {result['diagnostics']['verification_time']:.2f}s: {result['message']}")
    
    return result

def show_connection_status(show_details: bool = False):
    """
    Display connection status in the UI with enhanced diagnostics.
    
    Args:
        show_details: If True, show detailed diagnostics information
    """
    status = verify_connection()
    
    if is_demo_mode():
        st.info("🔌 Running in demo mode. Using sample data.")
        return
    
    if status["success"]:
        if status.get("is_demo") and status.get("diagnostics", {}).get("fallback") == "forced_demo_mode":
            # Special case: forced demo mode due to all connections failing
            st.warning("⚠️ All connections failed. Running in fallback demo mode.")
            st.caption("Limited functionality available. Some features may not work properly.")
        elif status["api_connected"] and status["db_connected"]:
            # Ideal case: both API and database connected
            st.success(f"✅ Connected to API and {status['db_type'].upper()} database")
            if status.get("db_version"):
                st.caption(f"Database version: {status['db_version']}")
        elif status["db_connected"] and not status["api_connected"]:
            # Database connected but API failed
            st.warning(f"⚠️ {status['db_type'].upper()} database connected but API connection failed.")
            st.caption("Using sample data for API requests. Some features may be limited.")
        elif status["api_connected"] and not status["db_connected"]:
            # API connected but database failed
            st.warning(f"⚠️ API connected but {status['db_type'].upper()} database connection failed.")
            st.caption("Using in-memory storage as fallback. Data will not be persisted.")
    else:
        # Complete failure case
        st.error("❌ All connections failed. Application functionality will be severely limited.")
        if status.get("api_message"):
            st.caption(f"API Error: {status['api_message']}")
        if status.get("message"):
            st.caption(f"Details: {status['message']}")
    
    # Show detailed diagnostics if requested
    if show_details and "diagnostics" in status:
        with st.expander("Connection Diagnostics"):
            st.markdown("### Connection Diagnostics")
            st.markdown(f"**Verification Time:** {status['diagnostics'].get('verification_time', 0):.2f} seconds")
            
            st.markdown("#### API Connection")
            api_diag = status['diagnostics'].get('api', {})
            st.markdown(f"**Connected:** {status['api_connected']}")
            for key, value in api_diag.items():
                if key != 'success':
                    st.markdown(f"**{key.capitalize()}:** {value}")
            
            st.markdown("#### Database Connection")
            db_diag = status['diagnostics'].get('database', {})
            st.markdown(f"**Connected:** {status['db_connected']}")
            st.markdown(f"**Type:** {status['db_type']}")
            for key, value in db_diag.items():
                if key not in ['type', 'version']:
                    st.markdown(f"**{key.capitalize()}:** {value}")
            
            if "fallback" in status['diagnostics']:
                st.markdown(f"**Fallback Strategy:** {status['diagnostics']['fallback']}")

def with_connection_fallback(fallback_func: Callable[..., T], max_retries: int = 1, retry_delay: float = 0.5) -> Callable:
    """
    Enhanced decorator to execute a function with connection fallback and retry logic.
    
    Args:
        fallback_func: Function to execute if connection fails
        max_retries: Maximum number of retries before using fallback
        retry_delay: Delay between retries in seconds
        
    Returns:
        Decorated function
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        def wrapper(*args, **kwargs) -> T:
            # Track function execution for logging
            func_name = func.__name__
            start_time = time.time()
            
            # In demo mode, always use fallback
            if is_demo_mode():
                logger.info(f"Demo mode active, using fallback for {func_name}")
                return fallback_func(*args, **kwargs)
            
            # Verify connection
            status = verify_connection()
            
            # If connection is successful, try the main function with retries
            if status["success"]:
                retries = 0
                last_error = None
                
                while retries <= max_retries:
                    try:
                        if retries > 0:
                            logger.info(f"Retry {retries}/{max_retries} for {func_name}")
                        
                        result = func(*args, **kwargs)
                        
                        # Log successful execution time
                        execution_time = time.time() - start_time
                        logger.debug(f"Function {func_name} executed successfully in {execution_time:.2f}s")
                        
                        return result
                    except Exception as e:
                        last_error = e
                        retries += 1
                        
                        # Log the error
                        logger.warning(f"Error executing {func_name} (attempt {retries}/{max_retries+1}): {str(e)}")
                        
                        # Wait before retrying (unless it's the last attempt)
                        if retries <= max_retries:
                            time.sleep(retry_delay * retries)  # Exponential backoff
                
                # If we've exhausted retries, log and use fallback
                logger.error(f"All {max_retries+1} attempts failed for {func_name}: {str(last_error)}")
                
                # Show a warning to the user about the fallback
                st.warning(f"⚠️ Using fallback data due to errors. Some information may be limited.")
                
                # Use fallback function
                return fallback_func(*args, **kwargs)
            
            # If connection check failed, use fallback immediately
            logger.info(f"Connection check failed, using fallback for {func_name}")
            return fallback_func(*args, **kwargs)
        
        # Preserve function metadata
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        
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
