"""
Pine Time User Interface - Main Application
Integrated with PostgreSQL database backend
"""

import streamlit as st
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import time
import logging
from dotenv import load_dotenv
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("user_app.log")
    ]
)
logger = logging.getLogger("user_app")

# Load environment variables
load_dotenv()

# Comment out forced demo mode to use real database authentication
# os.environ["DEMO_MODE"] = "true"

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

# Import utilities
from utils.api import (
    get_users, get_events, get_event_popularity, get_user_engagement, 
    get_points_distribution, get_leaderboard, get_points_history, get_badges,
    api_client, check_api_connection, get_user_badges, APIError, get_user_events,
    register_for_event
)
from utils.auth import (
    logout, check_authentication, verify_token, ensure_valid_token,
    get_current_user, check_user_access
)
# Import login from auth module as auth_login to avoid conflict
from utils.auth import login as auth_login
from utils.db import is_demo_mode, test_database_connection, create_user_in_database, get_database_config
from utils.connection import (
    verify_connection, show_connection_status, with_connection_fallback,
    get_sample_users, get_sample_events, get_sample_user_profile,
    get_sample_user_badges, get_sample_user_events, get_sample_points_history,
    get_sample_leaderboard, get_sample_badges
)
from config import (
    PAGE_TITLE, PAGE_ICON, THEME_COLOR, DATABASE_TYPE,
    API_ENDPOINTS
)

# Utility function for safe API response handling
def safe_api_response_handler(response, key=None, default=None):
    """
    Safely handle API responses with different formats and error conditions.
    
    Args:
        response: The API response to process (could be dict, list, or None)
        key: Optional key to extract from dict response
        default: Default value to return if response is invalid or key not found
        
    Returns:
        Processed response data or default value
    """
    if default is None:
        default = []
        
    # Handle None response
    if response is None:
        return default
        
    try:
        # Handle list response
        if isinstance(response, list):
            return response
            
        # Handle dict response
        if isinstance(response, dict):
            # If a specific key is requested
            if key and key in response:
                return response[key]
                
            # Try common keys if the specific key wasn't found
            if key:
                common_keys = ['items', 'data', key + 's', key + '_list']
                for common_key in common_keys:
                    if common_key in response:
                        return response[common_key]
            
            # If no key specified or found, return the whole dict
            return response
            
        # For any other type, return as is
        return response
    except Exception as e:
        logger.error(f"Error processing API response: {str(e)}")
        return default

# Additional utility functions for improved error handling

def safe_get_current_user():
    """
    Safely get the current user with error handling.
    
    Returns:
        dict: User data or None if not available
    """
    try:
        return get_current_user()
    except Exception as e:
        logger.error(f"Error getting current user: {str(e)}")
        return None

def safe_get_user_id():
    """
    Safely get the current user ID with error handling.
    
    Returns:
        str: User ID or None if not available
    """
    user = safe_get_current_user()
    if not user:
        logger.warning("No user found when trying to get user ID")
        return None
        
    user_id = user.get("id")
    if not user_id:
        logger.warning("User ID not found in user data")
        return None
        
    return user_id

def safe_api_call(call_func, error_message="API call failed", default_return=None):
    """
    Wrapper for API calls to provide consistent error handling.
    
    Args:
        call_func: Function to call that makes the API request
        error_message: Message to log on error
        default_return: Value to return on error
        
    Returns:
        The result of call_func or default_return on error
    """
    if default_return is None:
        default_return = []
        
    try:
        return call_func()
    except APIError as e:
        # Handle 404 errors gracefully - might be an expected condition
        if e.status_code == 404:
            logger.info(f"{error_message}: Resource not found")
            # Don't show error to user for 404
            return default_return
        logger.error(f"{error_message}: {str(e)}")
        st.error(f"Error: {str(e)}")
        return default_return
    except Exception as e:
        logger.error(f"{error_message} (unexpected error): {str(e)}")
        st.error(f"Unexpected error: {str(e)}")
        return default_return

def parse_date_safely(date_str):
    """
    Parse a date string safely with error handling.
    
    Args:
        date_str: Date string to parse
        
    Returns:
        datetime.date: Parsed date or None if parsing failed
    """
    if not date_str or not isinstance(date_str, str) or date_str.strip() == '':
        return None
        
    try:
        # Try ISO format first
        return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
    except ValueError:
        try:
            # Try common formats
            for fmt in ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%b %d, %Y"]:
                try:
                    return datetime.strptime(date_str, fmt).date()
                except ValueError:
                    continue
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Error parsing date '{date_str}': {str(e)}")
        
    return None

# Set page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
    /* Pine Time green theme */
    :root {
        --primary-color: #2E7D32;
        --background-color: #f5f5f5;
        --secondary-background-color: #e0e0e0;
        --text-color: #333333;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom sidebar styling */
    .css-1d391kg {
        background-color: var(--primary-color);
        color: white;
    }
    
    /* Custom button styling */
    .stButton>button {
        background-color: var(--primary-color);
        color: white;
    }
    
    /* Sidebar menu item styling */
    div[data-testid="stSidebarNav"] li {
        padding: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Hide developer options in sidebar */
    section[data-testid="stSidebar"] > div.css-1outpf7 {
        display: none !important;
    }
    
    /* Sidebar navigation buttons */
    .sidebar-nav-button {
        width: 100%;
        text-align: left;
        margin-bottom: 0.5rem;
    }
    
    .stApp {
        max-width: 1200px;
        margin: 0 auto;
    }
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    h1, h2, h3 {
        color: #2E7D32;
    }
    .stButton button {
        background-color: #2E7D32;
        color: white;
    }
    .stProgress .st-bo {
        background-color: #2E7D32;
    }
    /* Loading animation */
    .loading-spinner {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 100px;
    }
    /* Error message */
    .error-message {
        color: #D32F2F;
        padding: 10px;
        border-radius: 5px;
        background-color: #FFEBEE;
        margin: 10px 0;
    }
    /* Success message */
    .success-message {
        color: #388E3C;
        padding: 10px;
        border-radius: 5px;
        background-color: #E8F5E9;
        margin: 10px 0;
    }
    /* Card styling */
    .card {
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        background-color: white;
    }
    /* Badge styling */
    .badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
        font-weight: bold;
        background-color: #E8F5E9;
        color: #2E7D32;
    }
    /* Badge levels */
    .badge-bronze {
        background-color: #CD7F32;
        color: white;
    }
    
    .badge-silver {
        background-color: #C0C0C0;
        color: white;
    }
    
    .badge-gold {
        background-color: #FFD700;
        color: black;
    }
    /* Event card styling */
    .event-card {
        border-left: 5px solid #2E7D32;
        padding-left: 1rem;
    }
    /* Streak indicator */
    .streak-indicator {
        font-size: 0.8rem;
        padding: 3px 8px;
        border-radius: 10px;
        background-color: #FF5722;
        color: white;
        display: inline-block;
        margin-left: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "is_authenticated" not in st.session_state:
    st.session_state["is_authenticated"] = False
if "registration_step" not in st.session_state:
    st.session_state["registration_step"] = 1
if "show_registration" not in st.session_state:
    st.session_state["show_registration"] = False
if "login_successful" not in st.session_state:
    st.session_state["login_successful"] = False
if "connection_verified" not in st.session_state:
    st.session_state["connection_verified"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"

def show_login_page():
    """Display login form with option to register"""
    st.title("Pine Time Experience Baguio")
    
    with st.container():
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image("https://via.placeholder.com/300x200?text=Pine+Time+Logo", width=300)
            
            # Add a brief description
            st.markdown("""
            ### Welcome to Pine Time Experience
            
            Join our community and participate in exciting events around Baguio City.
            Track your points, earn badges, and connect with other enthusiasts!
            """)
            
        with col2:
            # Show registration success message if applicable
            if st.session_state.get("registration_success", False):
                st.success("Account created successfully! You can now login.")
                st.session_state["registration_success"] = False
            
            # Login form
            with st.form("login_form"):
                st.subheader("Login")
                username = st.text_input("Email or Username")
                password = st.text_input("Password", type="password")
                
                # Display connection status inside the form
                connection_status = verify_connection()
                if not connection_status["success"] and not is_demo_mode():
                    st.warning("⚠️ Database connection is unavailable. Login may not work properly.")
                
                # Add a checkbox for demo mode login
                demo_login = st.checkbox("Use demo login", value=is_demo_mode())
                
                submit_button = st.form_submit_button("Login")
                
                if submit_button:
                    if not username or not password:
                        st.error("Please enter both username and password")
                    else:
                        # If demo login is checked, force demo mode temporarily
                        if demo_login:
                            os.environ["DEMO_MODE"] = "true"
                            
                        with st.spinner("Logging in..."):
                            if login(username, password):
                                st.session_state["login_successful"] = True
                                st.success("Login successful! Redirecting...")
                                time.sleep(1)
                                st.rerun()
                            elif demo_login:
                                # If demo login failed, try with demo credentials
                                if login("demo@pinetimeexperience.com", "demo"):
                                    st.session_state["login_successful"] = True
                                    st.success("Demo login successful! Redirecting...")
                                    time.sleep(1)
                                    st.rerun()
                        
                        # Reset demo mode if it was temporarily enabled
                        if demo_login and not is_demo_mode():
                            os.environ["DEMO_MODE"] = "false"
            
            # Register option
            st.markdown("---")
            st.write("Don't have an account?")
            if st.button("Register"):
                st.session_state["show_registration"] = True
                st.rerun()
    
    # Show connection status
    with st.expander("Connection Status", expanded=False):
        show_connection_status()
        
        # Show database type
        db_config = get_database_config()
        db_type = db_config.get("database_type", "unknown").upper()
        st.write(f"Database: {db_type}")
        
        # Demo mode toggle
        demo_mode = is_demo_mode()
        if st.checkbox("Demo Mode", value=demo_mode):
            if not demo_mode:
                st.warning("Enabling demo mode will use sample data instead of connecting to the database.")
                if st.button("Enable Demo Mode"):
                    os.environ["DEMO_MODE"] = "true"
                    st.success("Demo mode enabled. Restarting application...")
                    time.sleep(1)
                    st.rerun()
        else:
            if demo_mode:
                if st.button("Disable Demo Mode"):
                    os.environ["DEMO_MODE"] = "false"
                    st.success("Demo mode disabled. Restarting application...")
                    time.sleep(1)
                    st.rerun()

def show_registration_form():
    """Display multi-step registration form"""
    st.title("Create Your Pine Time Account")
    
    # Back button
    if st.button("← Back to Login"):
        st.session_state["show_registration"] = False
        st.session_state["registration_step"] = 1
        st.rerun()
    
    # Progress bar
    progress = st.progress((st.session_state["registration_step"] - 1) / 3)
    
    # Check database connection
    connection_status = verify_connection()
    if not connection_status["success"] and not is_demo_mode():
        st.warning("""
        ⚠️ Database connection is unavailable. Registration will be processed in demo mode.
        Your account will be stored locally but may not sync with the main system.
        """)
    
    # Step 1: Account Information
    if st.session_state["registration_step"] == 1:
        st.subheader("Step 1: Account Information")
        
        with st.form("registration_step1"):
            email = st.text_input("Email Address")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password", 
                                    help="Password should be at least 8 characters long")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            submit_button = st.form_submit_button("Next")
            
            if submit_button:
                # Validate inputs
                if not email or not username or not password:
                    st.error("Please fill in all fields")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif "@" not in email:
                    st.error("Please enter a valid email address")
                elif len(password) < 8:
                    st.error("Password should be at least 8 characters long")
                else:
                    # Store in session state
                    st.session_state["reg_email"] = email
                    st.session_state["reg_username"] = username
                    st.session_state["reg_password"] = password
                    
                    # Move to next step
                    st.session_state["registration_step"] = 2
                    st.rerun()
    
    # Step 2: Personal Information
    elif st.session_state["registration_step"] == 2:
        st.subheader("Step 2: Personal Information")
        
        with st.form("registration_step2"):
            full_name = st.text_input("Full Name")
            
            # Calculate date ranges for 18+ users
            today = datetime.now().date()
            min_date = today.replace(year=today.year - 100)  # 100 years ago
            max_date = today.replace(year=today.year - 18)   # 18 years ago
            
            birth_date = st.date_input("Birth Date", value=max_date, min_value=min_date, max_value=max_date)
            
            phone = st.text_input("Phone Number (optional)")
            address = st.text_area("Address (optional)")
            
            submit_button = st.form_submit_button("Next")
            
            if submit_button:
                # Validate inputs
                if not full_name:
                    st.error("Please enter your full name")
                else:
                    # Store in session state
                    st.session_state["reg_full_name"] = full_name
                    st.session_state["reg_birth_date"] = birth_date.isoformat()
                    st.session_state["reg_phone"] = phone
                    st.session_state["reg_address"] = address
                    
                    # Move to next step
                    st.session_state["registration_step"] = 3
                    st.rerun()
    
    # Step 3: Preferences
    elif st.session_state["registration_step"] == 3:
        st.subheader("Step 3: Preferences")
        
        with st.form("registration_step3"):
            event_types = st.multiselect(
                "What types of events are you interested in?",
                ["Trivia Night", "Game Night", "Murder Mystery", "Hiking", "Workshop", "Social Mixer"]
            )
            
            notifications = st.checkbox("Receive email notifications about new events", value=True)
            
            terms = st.checkbox("I agree to the Terms and Conditions")
            
            # Add a checkbox for demo mode registration
            if not is_demo_mode():
                demo_registration = st.checkbox("Register in demo mode", value=False,
                                              help="Enable this if you're having trouble connecting to the database")
            else:
                demo_registration = True
            
            submit_button = st.form_submit_button("Create Account")
            
            if submit_button:
                # Validate inputs
                if not event_types:
                    st.warning("Please select at least one event type")
                if not terms:
                    st.error("You must agree to the Terms and Conditions")
                
                if event_types and terms:
                    # Store in session state
                    st.session_state["reg_event_types"] = event_types
                    st.session_state["reg_notifications"] = notifications
                    
                    # Attempt to register user
                    try:
                        # Prepare registration data
                        registration_data = {
                            "email": st.session_state["reg_email"],
                            "username": st.session_state["reg_username"],
                            "password": st.session_state["reg_password"],
                            "full_name": st.session_state["reg_full_name"],
                            "birth_date": st.session_state["reg_birth_date"],
                            "phone": st.session_state["reg_phone"],
                            "address": st.session_state["reg_address"],
                            "preferences": {
                                "event_types": st.session_state["reg_event_types"],
                                "notifications": st.session_state["reg_notifications"]
                            }
                        }
                        
                        # If demo registration is checked, temporarily enable demo mode
                        if demo_registration and not is_demo_mode():
                            os.environ["DEMO_MODE"] = "true"
                            st.info("Registering in demo mode...")
                        
                        with st.spinner("Creating your account..."):
                            # Register user
                            if register_user(registration_data):
                                st.success("Account created successfully!")
                                time.sleep(1)
                                
                                # Reset registration state
                                st.session_state["show_registration"] = False
                                st.session_state["registration_step"] = 1
                                st.session_state["registration_success"] = True
                                
                                # Clean up registration data
                                for key in list(st.session_state.keys()):
                                    if key.startswith("reg_"):
                                        del st.session_state[key]
                                
                                # Reset demo mode if it was temporarily enabled
                                if demo_registration and not is_demo_mode():
                                    os.environ["DEMO_MODE"] = "false"
                                
                                st.rerun()
                    except Exception as e:
                        st.error(f"Registration failed: {str(e)}")
                        logger.error(f"Registration error: {str(e)}")
                        
                        # If we're not in demo mode, suggest trying demo mode
                        if not is_demo_mode():
                            if st.button("Try registering in demo mode"):
                                os.environ["DEMO_MODE"] = "true"
                                st.rerun()

def show_main_app():
    """Display main app after login"""
    # Sidebar menu
    with st.sidebar:
        st.image("https://via.placeholder.com/150", width=150)
        
        # User info
        user = get_current_user()
        
        # Fallback to session state user if get_current_user returns None
        if not user:
            user = st.session_state.get("user")
        
        if user:
            st.write(f"Welcome, {user.get('full_name', user.get('username', 'User'))}")
            st.write(f"Points: {user.get('points', 0)}")
            
            # Navigation
            st.markdown("---")
            st.subheader("Navigation")
            
            # Initialize page in session state if not present
            if "current_page" not in st.session_state:
                st.session_state["current_page"] = "Home"
            
            # Navigation buttons with custom styling
            pages = ["Home", "Profile", "Leaderboard", "Badges"]
            for page in pages:
                if st.button(page, key=f"nav_{page.lower()}", use_container_width=True):
                    st.session_state["current_page"] = page
                    st.rerun()
            
            # Logout option
            st.markdown("---")
            if st.button("Logout", use_container_width=True):
                logout()
                st.rerun()
        else:
            st.warning("User information not available")
            if st.button("Return to Login"):
                st.session_state["login_successful"] = False
                st.rerun()
    
    # Get current page from session state
    page = st.session_state.get("current_page", "Home")
    
    # Display selected page
    if page == "Home":
        show_home_page()
    elif page == "Profile":
        show_profile_page()
    elif page == "Leaderboard":
        show_leaderboard_page()
    elif page == "Badges":
        show_badge_gallery()
    
    # Show connection status in footer
    status = verify_connection()
    if is_demo_mode():
        st.markdown(
            """<div class="connection-status demo">Demo Mode</div>""",
            unsafe_allow_html=True
        )
    elif status["success"]:
        db_type = status.get('db_type')
        if db_type:
            st.markdown(
                f"""<div class="connection-status connected">Connected to {db_type.upper()}</div>""",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                """<div class="connection-status connected">Connected to database (type unknown)</div>""",
                unsafe_allow_html=True
            )
    else:
        st.markdown(
            """<div class="connection-status disconnected">Using Sample Data</div>""",
            unsafe_allow_html=True
        )

def show_home_page():
    """Display home page with event discovery"""
    st.title("Discover Events")
    
    # Filters
    with st.expander("Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            event_type = st.selectbox(
                "Event Type",
                ["All Types", "Trivia Night", "Game Night", "Murder Mystery", "Hiking", "Workshop", "Social Mixer"]
            )
        
        with col2:
            location = st.selectbox(
                "Location",
                ["All Locations", "Pine Time Cafe", "Outdoor", "Conference Room", "Virtual"]
            )
        
        with col3:
            date_filter = st.selectbox(
                "Date",
                ["All Upcoming", "This Week", "This Month", "Next Month"]
            )
    
    # Get events with fallback to sample data
    @with_connection_fallback(get_sample_events)
    @st.cache_data(ttl=60)
    def fetch_events():
        # Get all events first
        events_data = get_events()
        
        # Handle both list and dictionary responses for events
        if not events_data:
            return events_data
            
        # Filter events manually
        if isinstance(events_data, dict):
            filtered_items = events_data.get('items', [])
        else:
            # If events_data is a list, use it directly
            filtered_items = events_data
        
        # Apply filters
        if event_type != "All Types":
            filtered_items = [e for e in filtered_items if e.get('event_type') == event_type]
        if location != "All Locations":
            filtered_items = [e for e in filtered_items if e.get('location') == location]
            
        # Date filtering
        today = datetime.now().date()
        
        # Process dates and handle missing or invalid date fields
        def get_event_date(event):
            # Try start_time first (preferred format)
            if event.get('start_time'):
                try:
                    date_str = event.get('start_time')
                    # Handle empty strings
                    if not date_str or date_str.strip() == '':
                        return None
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                except (ValueError, TypeError):
                    pass
                    
            # Fall back to date field
            if event.get('date'):
                try:
                    date_str = event.get('date')
                    # Handle empty strings
                    if not date_str or date_str.strip() == '':
                        return None
                    return datetime.fromisoformat(date_str.replace('Z', '+00:00')).date()
                except (ValueError, TypeError):
                    pass
            
            # If we get here, we couldn't parse a date
            return None
        
        # Filter by date range if applicable
        if date_filter == "This Week":
            start_date = today
            end_date = today + timedelta(days=7)
            filtered_items = [e for e in filtered_items if 
                            (event_date := get_event_date(e)) is not None and 
                            start_date <= event_date <= end_date]
        elif date_filter == "This Month":
            start_date = today
            end_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            filtered_items = [e for e in filtered_items if 
                            (event_date := get_event_date(e)) is not None and 
                            start_date <= event_date <= end_date]
        elif date_filter == "Next Month":
            next_month = (today.replace(day=1) + timedelta(days=32)).replace(day=1)
            start_date = next_month
            end_date = (next_month + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            filtered_items = [e for e in filtered_items if 
                            (event_date := get_event_date(e)) is not None and 
                            start_date <= event_date <= end_date]
        elif date_filter == "All Upcoming":
            filtered_items = [e for e in filtered_items if 
                            (event_date := get_event_date(e)) is not None and 
                            today <= event_date]
            
        # Return the filtered items in the same format as the input
        if isinstance(events_data, dict):
            events_data['items'] = filtered_items
            return events_data
        else:
            # If the original data was a list, return the filtered list directly
            return filtered_items
    
    events = fetch_events()
    
    # Handle both list and dictionary responses for events
    if not events:
        st.info("No events found matching your filters.")
    else:
        # If events is a dictionary with 'items' key, use that, otherwise use the list directly
        items = events.get('items', []) if isinstance(events, dict) else events
        
        if not items:
            st.info("No events found matching your filters.")
        else:
            st.subheader(f"Found {len(items)} events")
        
        # Create rows of 3 events each
        for i in range(0, len(items), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(items):
                    event = items[i + j]
                    with cols[j]:
                        with st.container():
                            st.markdown(f"""
                            <div class="card event-card">
                                <h3>{event['title']}</h3>
                                <p><strong>Type:</strong> {event['event_type']}</p>
                                <p><strong>Date:</strong> {event.get('start_time', '').split('T')[0]}</p>
                                <p><strong>Location:</strong> {event['location']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # View details button
                            if st.button("View Details", key=f"view_{event['id']}"):
                                st.session_state["selected_event"] = event
                                st.session_state["show_event_details"] = True
                                st.rerun()
    
    # Event details modal
    if st.session_state.get("show_event_details", False):
        event = st.session_state["selected_event"]
        
        with st.container():
            st.subheader(event['title'])
            st.write(f"**Type:** {event['event_type']}")
            st.write(f"**Date:** {event.get('start_time', '').split('T')[0]}")
            st.write(f"**Time:** {event.get('start_time', '').split('T')[1]} - {event.get('end_time', '9:00 PM')}")
            st.write(f"**Location:** {event['location']}")
            st.write(f"**Points:** {event.get('points', 100)}")
            
            st.markdown("---")
            st.write(event.get('description', 'No description available.'))
            
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Close"):
                    st.session_state["show_event_details"] = False
                    st.rerun()
            
            with col2:
                # Register for event
                if st.button("Register for Event"):
                    try:
                        # In demo mode, simulate registration
                        if is_demo_mode():
                            st.success(f"Successfully registered for {event['title']}!")
                            st.session_state["show_event_details"] = False
                            time.sleep(1)
                            st.rerun()
                        else:
                            # Use our new register_for_event function
                            with st.spinner("Registering..."):
                                # Get current user ID
                                user_id = safe_get_user_id()
                                
                                # Register for the event
                                success = register_for_event(event['id'], user_id)
                                
                                if success:
                                    st.success(f"Successfully registered for {event['title']}!")
                                    st.session_state["show_event_details"] = False
                                    time.sleep(1)
                                    st.rerun()
                    except Exception as e:
                        st.error(f"Registration failed: {str(e)}")
                        logger.error(f"Event registration error: {str(e)}")

def show_profile_page():
    """Display user profile with points, badges, and registered events"""
    st.title("My Profile")
    
    # Get user profile with fallback to sample data
    @with_connection_fallback(get_sample_user_profile)
    def fetch_user_profile():
        user_id = get_current_user().get("id")
        return api_client.get(
            API_ENDPOINTS["users"]["profile"].format(user_id=user_id),
            with_auth=True
        )
    
    # Get user badges with fallback to sample data
    @with_connection_fallback(get_sample_user_badges)
    def fetch_user_badges():
        # Use our safe utility function to get user ID
        user_id = safe_get_user_id()
        if not user_id:
            logger.warning("No user ID found when fetching user badges")
            return []
        
        try:
            # Use our improved get_user_badges function that handles errors and fallbacks
            badges = get_user_badges(user_id)
            
            # If we got badges back, return them
            if badges:
                return badges
            
            # If no badges were returned, log and return empty list
            logger.info(f"No badges found for user {user_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching user badges: {str(e)}")
            return []
    
    # Get user events with fallback to sample data
    @with_connection_fallback(get_sample_user_events)
    def fetch_user_events():
        # Get current user safely
        user_id = safe_get_user_id()
        if not user_id:
            logger.warning("No user ID found when fetching user events")
            return []
        
        try:
            # Use our improved get_user_events function that handles errors and fallbacks
            events = get_user_events(user_id)
            
            # If we got events back, return them
            if events:
                return events
            
            # If no events were returned, log and return empty list
            logger.info(f"No events found for user {user_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching user events: {str(e)}")
            return []
    
    # Get points history with fallback to sample data
    @with_connection_fallback(get_sample_points_history)
    def fetch_points_history():
        # Get current user safely
        user_id = safe_get_user_id()
        if not user_id:
            logger.warning("No user ID found when fetching points history")
            return []
        
        try:
            # Use our improved get_points_history function that handles errors and fallbacks
            history = get_points_history(user_id)
            
            # If we got history back, return it
            if history:
                return history
            
            # If no history was returned, log and return empty list
            logger.info(f"No points history found for user {user_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching points history: {str(e)}")
            return []
    
    # Fetch all data
    profile = fetch_user_profile()
    
    # Get badges with proper format handling
    badges_response = fetch_user_badges()
    # Handle different response formats
    if isinstance(badges_response, dict) and 'badges' in badges_response:
        badges = badges_response.get('badges', [])
    elif isinstance(badges_response, list):
        badges = badges_response
    else:
        logger.warning(f"Unexpected badges format: {type(badges_response)}")
        badges = []
    
    events = fetch_user_events()
    points_history = fetch_points_history()
    
    # Display user info
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://via.placeholder.com/150", width=150)
        
        # Edit profile button
        if st.button("Edit Profile"):
            st.session_state["show_edit_profile"] = True
            st.rerun()
    
    with col2:
        st.subheader(profile.get("full_name", "User"))
        st.write(f"Username: {profile.get('username', 'N/A')}")
        st.write(f"Email: {profile.get('email', 'N/A')}")
        st.write(f"Member since: {profile.get('created_at', 'N/A')}")
        
        # Points and streak
        points = profile.get("points", 0)
        streak = profile.get("streak", 0)
        
        st.markdown(f"""
        <div class="card">
            <h3>Points: {points}</h3>
            <p>Current Streak: {streak} days {' <span class="streak-indicator">🔥</span>' if streak > 0 else ''}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabs for different sections
    tab1, tab2, tab3 = st.tabs(["Badges", "Registered Events", "Points History"])
    
    with tab1:
        if not badges:
            st.info("You haven't earned any badges yet. Attend events to earn badges!")
        else:
            st.subheader(f"Badges Earned ({len(badges)})")
            
            # Create rows of 4 badges each
            for i in range(0, len(badges), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(badges):
                        badge = badges[i + j]
                        with cols[j]:
                            level = badge.get("level", "bronze").lower()
                            st.markdown(f"""
                            <div class="badge badge-{level}">
                                {badge.get('name', 'Badge')}
                            </div>
                            """, unsafe_allow_html=True)
                            st.write(badge.get("description", ""))
    
    with tab2:
        # Handle both list and dictionary responses for events
        if not events:
            st.info("You haven't registered for any events yet.")
        else:
            # If events is a dictionary with 'items' key, use that, otherwise use the list directly
            items = events.get('items', []) if isinstance(events, dict) else events
            
            if not items:
                st.info("You haven't registered for any events yet.")
            else:
                st.subheader(f"Registered Events ({len(items)})")            
                # Sort events by date
                items.sort(key=lambda x: x.get("start_date", "") if isinstance(x, dict) else "")
            
            # Separate upcoming and past events
            today = datetime.now().date().isoformat()
            upcoming_events = [e for e in items if e.get("start_date", "") >= today]
            past_events = [e for e in items if e.get("start_date", "") < today]
            
            # Display upcoming events
            if upcoming_events:
                st.write("### Upcoming Events")
                for event in upcoming_events:
                    st.markdown(f"""
                    <div class="card event-card">
                        <h4>{event.get('title', 'Event')}</h4>
                        <p><strong>Date:</strong> {event.get('start_date', 'N/A')}</p>
                        <p><strong>Location:</strong> {event.get('location', 'N/A')}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Display past events
            if past_events:
                st.write("### Past Events")
                for event in past_events:
                    attended = event.get("attended", False)
                    st.markdown(f"""
                    <div class="card event-card">
                        <h4>{event.get('title', 'Event')}</h4>
                        <p><strong>Date:</strong> {event.get('start_date', 'N/A')}</p>
                        <p><strong>Status:</strong> {"Attended" if attended else "Registered"}</p>
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab3:
        # Handle both list and dictionary formats for points_history
        if isinstance(points_history, list):
            points_items = points_history
        else:
            points_items = points_history.get('items', []) if points_history else []
            
        if not points_items:
            st.info("No points history available.")
        else:
            st.subheader("Points History")
            
            # Create DataFrame for points history
            df = pd.DataFrame(points_items)
            
            # Check if we have timestamp or date column
            date_column = None
            if 'timestamp' in df.columns:
                date_column = 'timestamp'
            elif 'date' in df.columns:
                date_column = 'date'
                
            if date_column:
                df["date"] = pd.to_datetime(df[date_column])
                df = df.sort_values("date", ascending=False)
                
                # Determine which columns to display
                display_columns = ["date"]
                if "description" in df.columns:
                    display_columns.append("description")
                elif "reason" in df.columns:
                    display_columns.append("reason")
                    
                display_columns.append("points")
                
                # Configure column display names
                column_config = {
                    "date": "Date",
                    "points": "Points"
                }
                
                if "description" in df.columns:
                    column_config["description"] = "Activity"
                elif "reason" in df.columns:
                    column_config["reason"] = "Activity"
                
                # Display as table
                st.dataframe(
                    df[display_columns],
                    column_config=column_config,
                    hide_index=True
                )
                
                # Points over time chart
                if len(df) > 1:
                    st.subheader("Points Over Time")
                    df_chart = df.sort_values("date")
                    df_chart["cumulative_points"] = df_chart["points"].cumsum()
                    
                    st.line_chart(df_chart.set_index("date")["cumulative_points"])
            else:
                st.info("Points history data format is invalid.")

def show_leaderboard_page():
    """Display leaderboard with top users"""
    st.title("Leaderboard")
    
    # Get leaderboard with fallback to sample data
    @with_connection_fallback(get_sample_leaderboard)
    def fetch_leaderboard():
        return get_leaderboard()
    
    leaderboard = fetch_leaderboard()
    
    # Handle both list and dictionary formats
    if isinstance(leaderboard, list):
        items = leaderboard
    else:
        items = leaderboard.get('items', []) if leaderboard else []
    
    if not items:
        st.info("Leaderboard data not available.")
    else:
        # Top 3 users
        st.subheader("Top Pine Time Enthusiasts")
        
        top_users = items[:3] if len(items) >= 3 else items
        cols = st.columns(3)
        
        for i, user in enumerate(top_users):
            with cols[i]:
                # Position styling
                position_emoji = ["🥇", "🥈", "🥉"][i]
                
                st.markdown(f"""
                <div class="card" style="text-align: center;">
                    <h1>{position_emoji}</h1>
                    <img src="https://via.placeholder.com/100" width="100" style="border-radius: 50%;">
                    <h3>{user.get('full_name', 'User')}</h3>
                    <p><strong>Points:</strong> {user.get('points', 0)}</p>
                    <p><strong>Events Attended:</strong> {user.get('events_attended', 0)}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Rest of the leaderboard as a table
        st.subheader("Leaderboard")
        
        # Create DataFrame for leaderboard
        df = pd.DataFrame(items)
        
        if not df.empty:
            # Add rank column if it doesn't already exist
            if "rank" not in df.columns:
                df.insert(0, "rank", range(1, len(df) + 1))
            
            # Highlight current user
            current_user = get_current_user()
            if current_user:
                current_user_id = current_user.get("id")
                
                # Find user's position
                user_position = None
                for i, user in enumerate(items):
                    if user.get("id") == current_user_id:
                        user_position = i + 1
                        break
                
                if user_position:
                    st.info(f"Your current position: #{user_position}")
            
            # Determine which columns to display based on what's available
            display_columns = ["rank"]
            column_config = {"rank": "Rank"}
            
            # Add columns if they exist
            if "full_name" in df.columns:
                display_columns.append("full_name")
                column_config["full_name"] = "Name"
            elif "username" in df.columns:
                display_columns.append("username")
                column_config["username"] = "Username"
                
            if "points" in df.columns:
                display_columns.append("points")
                column_config["points"] = "Points"
                
            if "events_attended" in df.columns:
                display_columns.append("events_attended")
                column_config["events_attended"] = "Events"
                
            if "badges_earned" in df.columns:
                display_columns.append("badges_earned")
                column_config["badges_earned"] = "Badges"
            
            # Display as table
            st.dataframe(
                df[display_columns],
                column_config=column_config,
                hide_index=True
            )
        else:
            st.info("Leaderboard data format is invalid.")

def show_badge_gallery():
    """Display all available badges with user progress"""
    st.title("Badge Gallery")
    
    # Get all badges with fallback to sample data
    @with_connection_fallback(get_sample_badges)
    def fetch_all_badges():
        return get_badges()
    
    # Get user badges with fallback to sample data
    @with_connection_fallback(get_sample_user_badges)
    def fetch_user_badges():
        # Use our safe utility function to get user ID
        user_id = safe_get_user_id()
        if not user_id:
            logger.warning("No user ID found when fetching user badges")
            return []
        
        try:
            # Use our improved get_user_badges function that handles errors and fallbacks
            badges = get_user_badges(user_id)
            
            # If we got badges back, return them
            if badges:
                return badges
            
            # If no badges were returned, log and return empty list
            logger.info(f"No badges found for user {user_id}")
            return []
        except Exception as e:
            logger.error(f"Error fetching user badges: {str(e)}")
            return []
    
    all_badges = fetch_all_badges()
    user_badges = fetch_user_badges()
    
    # Handle both list and dictionary formats for all_badges
    if isinstance(all_badges, list):
        badge_items = all_badges
    else:
        badge_items = all_badges.get('items', []) if all_badges else []
    
    # Handle both list and dictionary formats for user_badges
    user_badge_items = user_badges if isinstance(user_badges, list) else user_badges.get('items', [])
    user_badge_ids = {badge.get("id") for badge in user_badge_items}
    
    # Filters
    col1, col2 = st.columns(2)
    
    with col1:
        category = st.selectbox(
            "Category",
            ["All Categories", "Attendance", "Streak", "Special", "Achievement"]
        )
    
    with col2:
        status = st.selectbox(
            "Status",
            ["All Badges", "Earned", "Not Earned"]
        )
    
    # Filter badges
    filtered_badges = badge_items
    
    if category != "All Categories":
        filtered_badges = [b for b in filtered_badges if b.get("category") == category]
    
    if status == "Earned":
        filtered_badges = [b for b in filtered_badges if b.get("id") in user_badge_ids]
    elif status == "Not Earned":
        filtered_badges = [b for b in filtered_badges if b.get("id") not in user_badge_ids]
    
    # Display badges
    if not filtered_badges:
        st.info("No badges found matching your filters.")
    else:
        st.subheader(f"Found {len(filtered_badges)} badges")
        
        # Create rows of 3 badges each
        for i in range(0, len(filtered_badges), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(filtered_badges):
                    badge = filtered_badges[i + j]
                    with cols[j]:
                        # Check if user has earned this badge
                        earned = badge.get("id") in user_badge_ids
                        
                        # Badge level
                        level = badge.get("level", "bronze").lower()
                        
                        st.markdown(f"""
                        <div class="card" style="text-align: center; {'opacity: 0.6;' if not earned else ''}">
                            <div class="badge badge-{level}" style="margin: 0 auto;">
                                {badge.get('name', 'Badge')}
                            </div>
                            <p>{badge.get('description', '')}</p>
                            <p><strong>Category:</strong> {badge.get('category', 'General')}</p>
                            <p><strong>Status:</strong> {"Earned" if earned else "Not Earned"}</p>
                        </div>
                        """, unsafe_allow_html=True)

def register_user(user_data: Dict[str, Any]) -> bool:
    """
    Register a new user with the API or directly to the database in demo mode.
    
    Args:
        user_data: User registration data
        
    Returns:
        bool: True if registration successful, False otherwise
    """
    try:
        # Check if we're in demo mode
        if is_demo_mode():
            logger.info("Registering user in demo mode")
            # In demo mode, write directly to the database
            from utils.db import create_user_in_database
            success = create_user_in_database(user_data)
            if success:
                logger.info(f"User {user_data.get('username')} registered successfully in demo mode")
                return True
            else:
                error_msg = "Failed to create user in database"
                logger.error(error_msg)
                raise Exception(error_msg)
        
        # Check if we have a valid API connection
        connection_status = verify_connection()
        if not connection_status.get("api_connected", False):
            logger.warning("API connection is not available. Attempting direct database registration.")
            # Try direct database registration
            from utils.db import create_user_in_database
            success = create_user_in_database(user_data)
            if success:
                logger.info(f"User {user_data.get('username')} registered directly in database due to API unavailability")
                return True
            else:
                error_msg = "Failed to create user in database"
                logger.error(error_msg)
                raise Exception(error_msg)
        
        # Make API request to register user
        logger.info(f"Attempting to register user {user_data.get('username')} via API")
        response = api_client.post(
            API_ENDPOINTS["users"]["register"],
            json_data=user_data,
            with_auth=False
        )
        
        if isinstance(response, dict) and response.get("id"):
            logger.info(f"User {user_data.get('username')} registered successfully via API")
            return True
        else:
            error_msg = "API registration failed with unknown response"
            logger.error(f"{error_msg}: {response}")
            raise Exception(error_msg)
            
    except Exception as e:
        error_msg = str(e)
        
        # Check if this is a connection error
        if "Connection" in error_msg and "refused" in error_msg:
            # Enable demo mode automatically
            os.environ["DEMO_MODE"] = "true"
            
            # Log the switch to demo mode
            logger.warning(f"API connection failed during registration. Switching to demo mode: {error_msg}")
            
            # Try to write directly to the database
            try:
                from utils.db import create_user_in_database
                if create_user_in_database(user_data):
                    # Show a warning to the user
                    st.warning("API server is not available. Registration completed in demo mode.")
                    time.sleep(2)  # Give user time to read the message
                    return True
                else:
                    raise Exception("Failed to create user in database")
            except Exception as db_error:
                logger.error(f"Database registration error: {str(db_error)}")
                raise Exception(f"Registration failed: {str(db_error)}")
        
        # For other errors, raise the exception
        logger.error(f"Registration error: {error_msg}")
        raise Exception(f"Registration failed: {error_msg}")

def login(username: str, password: str) -> bool:
    """
    Authenticate user with API.
    
    Args:
        username: User's username or email
        password: User's password
        
    Returns:
        bool: True if login successful, False otherwise
    """
    try:
        logger.info(f"Calling auth_login for user: {username}")
        
        # Use the auth module's login function
        login_success = auth_login(username, password)
        
        if login_success:
            # Set additional session state variables for compatibility
            st.session_state["login_successful"] = True
            
            # If user_info exists in session state, copy it to user for compatibility
            if "user_info" in st.session_state and "user" not in st.session_state:
                st.session_state["user"] = st.session_state["user_info"]
                
            logger.info(f"Login successful for user: {username}")
            return True
        else:
            logger.warning(f"Login failed for user: {username}")
            return False
            
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Login exception: {error_msg}")
        
        # Check if this is a connection error
        if "Connection" in error_msg and "refused" in error_msg:
            # Enable demo mode automatically
            os.environ["DEMO_MODE"] = "true"
            logger.warning(f"API connection failed. Switching to demo mode: {error_msg}")
            
            # Try login again (will use demo mode now)
            return auth_login(username, password)
        
        # For other errors, show the error message
        st.error(f"Login failed: {error_msg}")
        logger.error(f"Login error: {error_msg}")
        return False

# Main app logic

# Initialize session state variables if they don't exist
if "registration_step" not in st.session_state:
    st.session_state["registration_step"] = 1
if "show_registration" not in st.session_state:
    st.session_state["show_registration"] = False
if "login_successful" not in st.session_state:
    st.session_state["login_successful"] = False
if "connection_verified" not in st.session_state:
    st.session_state["connection_verified"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Home"
if "user" not in st.session_state:
    st.session_state["user"] = None
if "user_info" not in st.session_state:
    st.session_state["user_info"] = None
if "is_authenticated" not in st.session_state:
    st.session_state["is_authenticated"] = False

# Verify connection on first load
if not st.session_state.get("connection_verified", False):
    status = verify_connection(force=True)
    st.session_state["connection_verified"] = True
    
    # Log connection status
    if status["success"]:
        db_type = status.get('db_type')
        if db_type:
            logger.info(f"Connected to {db_type.upper()} database")
        else:
            logger.info("Connected to database (type unknown)")
    else:
        if is_demo_mode():
            logger.info("Running in demo mode")
        else:
            logger.warning(f"Connection issues: {status.get('message', 'Unknown error')}")

# Create a two-column layout for the entire app
col1, col2 = st.columns([1, 4])

# Sidebar navigation in the first column
with col1:
    st.image("https://via.placeholder.com/150", width=150)
    
    # Check if user is logged in
    if st.session_state.get("login_successful", False):
        # Get user info
        user_data = st.session_state.get("user") or st.session_state.get("user_info")
        
        if user_data:
            st.write(f"Welcome, {user_data.get('full_name', user_data.get('username', 'User'))}")
            st.write(f"Points: {user_data.get('points', 0)}")
            
            # Navigation menu
            st.markdown("---")
            st.subheader("Navigation")
            
            # Navigation buttons
            if st.button("🏠 Home", key="nav_home", use_container_width=True):
                st.session_state["current_page"] = "Home"
                st.rerun()
            
            if st.button("👤 My Profile", key="nav_profile", use_container_width=True):
                st.session_state["current_page"] = "Profile"
                st.rerun()
            
            if st.button("🏆 Leaderboard", key="nav_leaderboard", use_container_width=True):
                st.session_state["current_page"] = "Leaderboard"
                st.rerun()
            
            if st.button("🥇 Badge Gallery", key="nav_badges", use_container_width=True):
                st.session_state["current_page"] = "Badges"
                st.rerun()
            
            # Logout option
            st.markdown("---")
            if st.button("Logout", use_container_width=True):
                logout()
                st.rerun()
        else:
            st.warning("User information not available")
            if st.button("Return to Login"):
                st.session_state["login_successful"] = False
                st.rerun()
    else:
        # Show login button if not logged in
        if st.button("Login", use_container_width=True):
            st.session_state["login_successful"] = False
            st.rerun()
        
        # Show register button if not logged in
        if st.button("Register", use_container_width=True):
            st.session_state["show_registration"] = True
            st.rerun()

# Main content in the second column
with col2:
    # Check if we need to show registration form
    if st.session_state.get("show_registration", False):
        show_registration_form()
    # Check if user is logged in
    elif st.session_state.get("login_successful", False):
        # Get current page from session state
        page = st.session_state.get("current_page", "Home")
        
        # Display selected page
        if page == "Home":
            show_home_page()
        elif page == "Profile":
            show_profile_page()
        elif page == "Leaderboard":
            show_leaderboard_page()
        elif page == "Badges":
            show_badge_gallery()
    # Otherwise show login page
    else:
        show_login_page()

# Auto-login for demo mode
if is_demo_mode() and not st.session_state.get("login_successful", False):
    # Create demo user data
    user_data = {
        "id": "demo-user-id",
        "username": "demo",
        "email": "demo@pinetimeexperience.com",
        "full_name": "Demo User",
        "is_active": True,
        "is_superuser": False,
        "access_token": "demo-token",
        "token_type": "bearer",
        "points": 500,
        "created_at": datetime.now().isoformat(),
        "role": "user"
    }
    
    # Set session state variables
    st.session_state["user"] = user_data
    st.session_state["user_info"] = user_data
    st.session_state["is_authenticated"] = True
    st.session_state["login_successful"] = True
    st.rerun()
