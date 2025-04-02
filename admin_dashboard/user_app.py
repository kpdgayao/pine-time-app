"""
Pine Time User Interface - Main Application
"""

import streamlit as st
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import time
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

# Import utilities
from utils.api import (
    get_users, get_events, get_event_popularity, get_user_engagement, 
    get_points_distribution, get_leaderboard, get_points_history, get_badges,
    register_user
)
from utils.auth import login, logout, check_authentication, verify_token, ensure_valid_token

# Set page configuration
st.set_page_config(
    page_title="Pine Time Experience Baguio",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="collapsed"
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
    
    /* Card styling */
    .card {
        border-radius: 5px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: white;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Sidebar menu item styling */
    div[data-testid="stSidebarNav"] li {
        display: none !important;
    }
    
    /* Hide developer options in sidebar */
    section[data-testid="stSidebar"] > div.css-1outpf7 {
        display: none !important;
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
    /* Mobile responsive */
    @media (max-width: 768px) {
        .stApp {
            padding: 0.5rem;
        }
        .card {
            padding: 1rem;
        }
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

def show_login_page():
    """Display login form with option to register"""
    st.title("Pine Time Experience Baguio")
    
    with st.container():
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image("https://via.placeholder.com/300x200?text=Pine+Time+Logo", width=300)
            
        with col2:
            # Show registration success message if applicable
            if st.session_state.get("registration_success", False):
                st.success("Account created successfully! You can now login.")
                # Clear the flag after showing the message
                del st.session_state["registration_success"]
            
            # Toggle between login and registration
            if st.session_state.get("show_registration", False):
                st.subheader("Create an Account")
                show_registration_form()
                
                # Link to switch to login
                if st.button("Already have an account? Login here"):
                    st.session_state["show_registration"] = False
            else:
                st.subheader("User Login")
                
                # Show any error messages
                if "login_error" in st.session_state:
                    st.error(st.session_state["login_error"])
                    del st.session_state["login_error"]
                
                # Login form
                with st.form("login_form"):
                    username = st.text_input("Username or Email")
                    password = st.text_input("Password", type="password")
                    submit = st.form_submit_button("Login")
                    
                    if submit:
                        if username and password:
                            try:
                                # For demo purposes, use a simple login check
                                # In a real app, this would connect to the backend
                                if username == "demo" and password == "password":
                                    # Create a mock user_info
                                    st.session_state["user_info"] = {
                                        "id": "123",
                                        "username": username,
                                        "first_name": "Demo",
                                        "last_name": "User",
                                        "email": "demo@example.com",
                                        "points": 350,
                                        "role": "user"
                                    }
                                    st.session_state["is_authenticated"] = True
                                    st.session_state["login_successful"] = True
                                    st.success("Login successful!")
                                else:
                                    # Try the actual login if demo credentials don't match
                                    login_success = False
                                    try:
                                        login_success = login(username, password)
                                    except Exception as e:
                                        logger.error(f"Login error: {str(e)}")
                                        st.error(f"Backend connection error. Using demo mode for now.")
                                        st.warning("Use username 'demo' and password 'password' to login in demo mode.")
                                    
                                    if login_success:
                                        st.session_state["is_authenticated"] = True
                                        st.session_state["login_successful"] = True
                            except Exception as e:
                                st.error(f"Login error: {str(e)}")
                        else:
                            st.error("Please enter both username and password")
                
                # Link to switch to registration
                if st.button("Don't have an account? Register here"):
                    st.session_state["show_registration"] = True

def show_registration_form():
    """Display multi-step registration form"""
    # Multi-step registration process
    step = st.session_state.get("registration_step", 1)
    
    if step == 1:
        with st.form("registration_step1"):
            st.write("Step 1: Account Information")
            email = st.text_input("Email Address")
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            next_button = st.form_submit_button("Next")
            
            if next_button:
                if not (email and username and password and confirm_password):
                    st.error("All fields are required")
                elif password != confirm_password:
                    st.error("Passwords do not match")
                elif len(password) < 8:
                    st.error("Password must be at least 8 characters long")
                else:
                    # Store data in session state
                    st.session_state["reg_email"] = email
                    st.session_state["reg_username"] = username
                    st.session_state["reg_password"] = password
                    st.session_state["registration_step"] = 2
    
    elif step == 2:
        with st.form("registration_step2"):
            st.write("Step 2: Personal Information")
            first_name = st.text_input("First Name")
            last_name = st.text_input("Last Name")
            
            # Fix the date input to use fixed dates instead of relative dates
            # Allow ages between 10 and 100 years old
            min_date = datetime(1925, 1, 1).date()
            max_date = datetime(2015, 1, 1).date()
            default_date = datetime(1990, 1, 1).date()
            
            dob = st.date_input(
                "Date of Birth", 
                value=default_date,
                min_value=min_date,
                max_value=max_date
            )
            
            phone = st.text_input("Phone Number")
            
            col1, col2 = st.columns(2)
            with col1:
                back_button = st.form_submit_button("Back")
            with col2:
                next_button = st.form_submit_button("Next")
            
            if back_button:
                st.session_state["registration_step"] = 1
            
            if next_button:
                if not (first_name and last_name and phone):
                    st.error("First name, last name, and phone are required")
                else:
                    # Store data in session state
                    st.session_state["reg_first_name"] = first_name
                    st.session_state["reg_last_name"] = last_name
                    st.session_state["reg_dob"] = dob.strftime("%Y-%m-%d")
                    st.session_state["reg_phone"] = phone
                    st.session_state["registration_step"] = 3
    
    elif step == 3:
        with st.form("registration_step3"):
            st.write("Step 3: Preferences")
            location = st.text_input("Location")
            interests = st.multiselect(
                "Interests", 
                ["Hiking", "Camping", "Wildlife", "Photography", "Conservation", "Education", "Community Service"]
            )
            referral = st.selectbox(
                "How did you hear about us?",
                ["", "Friend", "Social Media", "Search Engine", "Advertisement", "Event", "Other"]
            )
            
            col1, col2 = st.columns(2)
            with col1:
                back_button = st.form_submit_button("Back")
            with col2:
                submit_button = st.form_submit_button("Create Account")
            
            if back_button:
                st.session_state["registration_step"] = 2
            
            if submit_button:
                # Prepare registration data
                registration_data = {
                    "email": st.session_state.get("reg_email"),
                    "username": st.session_state.get("reg_username"),
                    "password": st.session_state.get("reg_password"),
                    "first_name": st.session_state.get("reg_first_name"),
                    "last_name": st.session_state.get("reg_last_name"),
                    "dob": st.session_state.get("reg_dob"),
                    "phone": st.session_state.get("reg_phone"),
                    "location": location,
                    "interests": ",".join(interests) if interests else "",
                    "referral": referral
                }
                
                # Call API to register user
                try:
                    # Create a user object that matches the backend schema
                    user_create_data = {
                        "email": registration_data["email"],
                        "username": registration_data["username"],
                        "password": registration_data["password"],
                        "full_name": f"{registration_data['first_name']} {registration_data['last_name']}",
                        "is_active": True,
                        "is_superuser": False
                    }
                    
                    # Add additional fields as custom data
                    user_create_data["phone"] = registration_data["phone"]
                    user_create_data["dob"] = registration_data["dob"]
                    user_create_data["location"] = registration_data["location"]
                    user_create_data["interests"] = registration_data["interests"]
                    user_create_data["referral"] = registration_data["referral"]
                    
                    # Call the register_user function
                    with st.spinner("Creating your account..."):
                        result = register_user(user_create_data)
                    
                    if result:
                        st.session_state["registration_success"] = True
                        
                        # Reset registration state
                        st.session_state["show_registration"] = False
                        st.session_state["registration_step"] = 1
                        
                        # Clear registration data
                        for key in list(st.session_state.keys()):
                            if key.startswith("reg_"):
                                del st.session_state[key]
                        
                        st.success("Account created successfully! You can now login.")
                    else:
                        st.error("Registration failed. Please try again.")
                except Exception as e:
                    st.error(f"Registration failed: {str(e)}")

def show_main_app():
    """Display main app with navigation"""
    # Check if user is authenticated
    if not check_authentication():
        st.session_state["is_authenticated"] = False
    
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x100?text=Pine+Time+Logo", width=200)
        
        # User info display
        if "user_info" in st.session_state:
            user_info = st.session_state["user_info"]
            st.write(f"Welcome, **{user_info.get('first_name', '')}**!")
            st.write(f"Points: **{user_info.get('points', 0)}**")
        
        # Navigation options for regular users
        selected = st.radio(
            "Navigation",
            ["Home", "My Profile", "Leaderboard", "Badge Gallery", "Logout"],
            index=0
        )
    
    # Display selected page
    if selected == "Home":
        show_home_page()
    elif selected == "My Profile":
        show_profile_page()
    elif selected == "Leaderboard":
        show_leaderboard_page()
    elif selected == "Badge Gallery":
        show_badge_gallery()
    elif selected == "Logout":
        logout()
        st.session_state["is_authenticated"] = False

def show_home_page():
    """Display home page with upcoming events and filtering options"""
    st.title("Upcoming Events")
    
    # Event filtering options
    with st.expander("Filter Events", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            event_type = st.multiselect(
                "Event Type",
                ["Hiking", "Camping", "Workshop", "Clean-up", "Conservation", "Community", "Educational"]
            )
        
        with col2:
            location = st.multiselect(
                "Location",
                ["Baguio City", "La Trinidad", "Itogon", "Tuba", "Sablan", "Tublay", "Other"]
            )
        
        with col3:
            date_range = st.date_input(
                "Date Range",
                value=(datetime.now(), datetime.now() + timedelta(days=30)),
                min_value=datetime.now(),
                max_value=datetime.now() + timedelta(days=365)
            )
        
        apply_filter = st.button("Apply Filters")
    
    # Try to fetch events from API
    try:
        events_data = get_events()
        events = events_data.get("items", [])
        
        if not events:
            st.info("No events found. Check back later for upcoming activities!")
            # Show sample events as fallback
            show_sample_events()
        else:
            # Display events
            display_events(events)
    
    except Exception as e:
        st.error(f"Error loading events: {str(e)}")
        # Fallback to sample events
        show_sample_events()

def show_sample_events():
    """Display sample events as fallback"""
    st.subheader("Upcoming Events")
    
    sample_events = [
        {
            "id": "1",
            "title": "Weekend Hiking Adventure",
            "description": "Join us for a refreshing hike through the pine forests of Baguio. Perfect for beginners and experienced hikers alike.",
            "event_type": "Hiking",
            "location": "Baguio City",
            "date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            "time": "08:00 AM",
            "duration": "4 hours",
            "points": 50,
            "capacity": 20,
            "registered": 12
        },
        {
            "id": "2",
            "title": "Environmental Conservation Workshop",
            "description": "Learn about local conservation efforts and how you can contribute to preserving Baguio's natural beauty.",
            "event_type": "Workshop",
            "location": "La Trinidad",
            "date": (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d"),
            "time": "01:00 PM",
            "duration": "3 hours",
            "points": 40,
            "capacity": 30,
            "registered": 15
        },
        {
            "id": "3",
            "title": "Community Clean-up Drive",
            "description": "Help clean up our community parks and trails. Equipment and refreshments provided.",
            "event_type": "Clean-up",
            "location": "Baguio City",
            "date": (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d"),
            "time": "09:00 AM",
            "duration": "5 hours",
            "points": 75,
            "capacity": 50,
            "registered": 22
        }
    ]
    
    display_events(sample_events)

def display_events(events):
    """Display events in a visually appealing format"""
    for event in events:
        with st.container():
            st.markdown(f"""
            <div class="card event-card">
                <h3>{event.get('title')}</h3>
                <p><strong>Date:</strong> {event.get('date')} at {event.get('time')}</p>
                <p><strong>Location:</strong> {event.get('location')}</p>
                <p><strong>Type:</strong> {event.get('event_type')}</p>
                <p>{event.get('description')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                st.write(f"Duration: **{event.get('duration')}**")
            
            with col2:
                st.write(f"Points: **{event.get('points')}**")
            
            with col3:
                st.write(f"Spots: **{event.get('registered')}/{event.get('capacity')}**")
            
            # Check if user is already registered
            is_registered = False  # This would be checked via API in production
            
            if is_registered:
                st.success("You're registered for this event!")
                if st.button(f"Cancel Registration (Event {event.get('id')})", key=f"cancel_{event.get('id')}"):
                    # API call to cancel registration would go here
                    st.info("Registration cancelled. Refreshing...")
            else:
                if st.button(f"Register Now (Event {event.get('id')})", key=f"register_{event.get('id')}"):
                    # Show registration confirmation
                    st.session_state[f"confirm_reg_{event.get('id')}"] = True
            
            # Registration confirmation dialog
            if st.session_state.get(f"confirm_reg_{event.get('id')}", False):
                with st.expander("Confirm Registration", expanded=True):
                    st.write(f"You are about to register for **{event.get('title')}**")
                    st.write(f"Date: {event.get('date')} at {event.get('time')}")
                    st.write(f"Location: {event.get('location')}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Cancel", key=f"cancel_confirm_{event.get('id')}"):
                            del st.session_state[f"confirm_reg_{event.get('id')}"]
                    with col2:
                        if st.button("Confirm Registration", key=f"confirm_{event.get('id')}"):
                            # API call to register would go here
                            st.success(f"Successfully registered for {event.get('title')}!")
                            del st.session_state[f"confirm_reg_{event.get('id')}"]
            
            st.markdown("---")

def show_profile_page():
    """Display user profile with personal info, points, badges, and registered events"""
    st.title("My Profile")
    
    try:
        # In production, this would fetch the user's profile from the API
        # For now, use sample data or session state info
        user_info = st.session_state.get("user_info", {})
        
        if not user_info:
            st.error("Unable to load profile information. Please try again later.")
            show_sample_profile()
        else:
            # Display user information
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Profile picture (placeholder)
                st.image("https://via.placeholder.com/150", width=150)
                
                # Points display
                points = user_info.get("points", 0)
                st.markdown(f"""
                <div class="card" style="text-align: center;">
                    <h1 style="color: #2E7D32; font-size: 3rem;">{points}</h1>
                    <p>Total Points</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Personal information
                st.subheader("Personal Information")
                st.markdown(f"""
                <div class="card">
                    <p><strong>Name:</strong> {user_info.get('first_name', '')} {user_info.get('last_name', '')}</p>
                    <p><strong>Username:</strong> {user_info.get('username', '')}</p>
                    <p><strong>Email:</strong> {user_info.get('email', '')}</p>
                    <p><strong>Phone:</strong> {user_info.get('phone', '')}</p>
                    <p><strong>Location:</strong> {user_info.get('location', '')}</p>
                    <p><strong>Member Since:</strong> {user_info.get('created_at', '')}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Edit profile button
                if st.button("Edit Profile"):
                    st.session_state["show_edit_profile"] = True
            
            # Edit profile form
            if st.session_state.get("show_edit_profile", False):
                with st.expander("Edit Profile", expanded=True):
                    with st.form("edit_profile_form"):
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            first_name = st.text_input("First Name", value=user_info.get("first_name", ""))
                            email = st.text_input("Email", value=user_info.get("email", ""))
                            location = st.text_input("Location", value=user_info.get("location", ""))
                        
                        with col2:
                            last_name = st.text_input("Last Name", value=user_info.get("last_name", ""))
                            phone = st.text_input("Phone", value=user_info.get("phone", ""))
                            
                        submit = st.form_submit_button("Save Changes")
                        
                        if submit:
                            # API call to update profile would go here
                            st.success("Profile updated successfully!")
                            st.session_state["show_edit_profile"] = False
            
            # Display badges
            st.subheader("My Badges")
            try:
                # This would be an API call in production
                badges = get_user_badges(user_info.get("id", ""))
                if badges:
                    display_user_badges(badges)
                else:
                    st.info("You haven't earned any badges yet. Participate in events to earn your first badge!")
            except Exception as e:
                st.error(f"Error loading badges: {str(e)}")
                display_sample_user_badges()
            
            # Display registered events
            st.subheader("My Events")
            tabs = st.tabs(["Upcoming Events", "Past Events"])
            
            with tabs[0]:
                try:
                    # This would be an API call in production
                    # For now, use sample data
                    upcoming_events = []  # Would be fetched from API
                    if upcoming_events:
                        display_user_events(upcoming_events, is_past=False)
                    else:
                        st.info("You don't have any upcoming events. Check out the home page to register for events!")
                        display_sample_user_events(is_past=False)
                except Exception as e:
                    st.error(f"Error loading upcoming events: {str(e)}")
                    display_sample_user_events(is_past=False)
            
            with tabs[1]:
                try:
                    # This would be an API call in production
                    # For now, use sample data
                    past_events = []  # Would be fetched from API
                    if past_events:
                        display_user_events(past_events, is_past=True)
                    else:
                        st.info("You don't have any past events.")
                        display_sample_user_events(is_past=True)
                except Exception as e:
                    st.error(f"Error loading past events: {str(e)}")
                    display_sample_user_events(is_past=True)
            
            # Points history
            st.subheader("Points History")
            try:
                # This would be an API call in production
                points_history = get_points_history(user_id=user_info.get("id", ""))
                if points_history:
                    display_points_history(points_history)
                else:
                    st.info("No points history available.")
                    display_sample_points_history()
            except Exception as e:
                st.error(f"Error loading points history: {str(e)}")
                display_sample_points_history()
    
    except Exception as e:
        st.error(f"Error loading profile: {str(e)}")
        show_sample_profile()

def show_sample_profile():
    """Display sample profile as fallback"""
    # Sample user data
    user = {
        "id": "123",
        "username": "demo_user",
        "first_name": "Demo",
        "last_name": "User",
        "email": "demo@example.com",
        "phone": "123-456-7890",
        "dob": "1990-01-01",
        "location": "Baguio City",
        "interests": ["Trivia", "Games", "Mystery"],
        "points": 350,
        "streak": 3,  # Current weekly streak
        "joined_date": "2025-01-15"
    }
    
    # Display user profile
    st.header(f"{user['first_name']}'s Profile")
    
    # Profile overview
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://via.placeholder.com/150?text=Profile", width=150)
        
        # Show edit profile button
        if st.button("Edit Profile"):
            st.session_state["show_edit_profile"] = True
            st.rerun()
    
    with col2:
        st.subheader("Personal Information")
        st.write(f"**Name:** {user['first_name']} {user['last_name']}")
        st.write(f"**Username:** {user['username']}")
        st.write(f"**Email:** {user['email']}")
        st.write(f"**Phone:** {user['phone']}")
        st.write(f"**Location:** {user['location']}")
        st.write(f"**Interests:** {', '.join(user['interests'])}")
        st.write(f"**Member since:** {user['joined_date']}")
    
    # Points and streak information
    st.subheader("Points & Achievements")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <h1 style="color: #2E7D32; font-size: 3rem;">{user['points']}</h1>
            <p>Total Points</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <h1 style="color: #FF5722; font-size: 3rem;">{user['streak']}</h1>
            <p>Week Streak <span class="streak-indicator">🔥</span></p>
            <p style="font-size: 0.8rem;">Attend this week's event to maintain your streak!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show edit profile form if requested
    if st.session_state.get("show_edit_profile", False):
        st.markdown("---")
        st.subheader("Edit Profile")
        
        with st.form("edit_profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                first_name = st.text_input("First Name", value=user["first_name"])
                last_name = st.text_input("Last Name", value=user["last_name"])
                email = st.text_input("Email", value=user["email"])
            
            with col2:
                phone = st.text_input("Phone", value=user["phone"])
                location = st.text_input("Location", value=user["location"])
                interests = st.multiselect(
                    "Interests",
                    ["Trivia", "Games", "Mystery", "Hiking", "Photography", "Conservation", "Education", "Community Service"],
                    default=user["interests"]
                )
            
            col1, col2 = st.columns(2)
            with col1:
                cancel = st.form_submit_button("Cancel")
            with col2:
                submit = st.form_submit_button("Save Changes")
            
            if cancel:
                st.session_state["show_edit_profile"] = False
            
            if submit:
                # API call to update profile would go here
                st.success("Profile updated successfully!")
                st.session_state["show_edit_profile"] = False
    
    # Display badges
    st.subheader("My Badges")
    
    # Sample user badges for display
    user_badges = [
        {
            "id": 1,
            "name": "Trivia Master",
            "description": "Participate in 3 trivia nights",
            "category": "Trivia",
            "level": "bronze",
            "earned_date": "2025-02-15"
        },
        {
            "id": 4,
            "name": "Game Night Rookie",
            "description": "Participate in your first game night",
            "category": "Games",
            "level": "bronze",
            "earned_date": "2025-03-01"
        },
        {
            "id": 10,
            "name": "Weekly Streak",
            "description": "Attend events for 3 consecutive weeks",
            "category": "Attendance",
            "level": "bronze",
            "earned_date": "2025-03-20"
        }
    ]
    
    # Display badges with levels
    if not user_badges:
        st.info("You haven't earned any badges yet. Participate in events to earn badges!")
    else:
        cols = st.columns(3)
        for i, badge in enumerate(user_badges):
            col_idx = i % 3
            level = badge.get("level", "bronze").lower()
            
            with cols[col_idx]:
                st.markdown(f"""
                <div class="card">
                    <div class="badge badge-{level}">
                        <h3>{badge.get("name")}</h3>
                        <p>{badge.get("description")}</p>
                        <p><strong>Category:</strong> {badge.get("category")}</p>
                        <p><strong>Level:</strong> {level.capitalize()}</p>
                        <p><strong>Earned:</strong> {badge.get("earned_date")}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Points history
    st.subheader("Points History")
    display_sample_points_history()
    
    # Registered events
    tabs = st.tabs(["Upcoming Events", "Past Events"])
    
    with tabs[0]:
        st.subheader("My Upcoming Events")
        display_sample_user_events(is_past=False)
    
    with tabs[1]:
        st.subheader("My Past Events")
        display_sample_user_events(is_past=True)

def display_user_badges(badges):
    """Display user badges in a grid"""
    badge_cols = st.columns(4)
    
    for i, badge in enumerate(badges):
        with badge_cols[i % 4]:
            st.markdown(f"""
            <div style="text-align: center;">
                <img src="{badge.get('image_url', 'https://via.placeholder.com/100')}" width="80">
                <p><strong>{badge.get('name', '')}</strong></p>
                <p>{badge.get('description', '')}</p>
            </div>
            """, unsafe_allow_html=True)

def display_sample_user_badges():
    """Display sample user badges"""
    sample_badges = [
        {
            "id": "1",
            "name": "Nature Explorer",
            "description": "Completed 5 hiking events",
            "image_url": "https://via.placeholder.com/100?text=Explorer"
        },
        {
            "id": "2",
            "name": "Eco Warrior",
            "description": "Participated in 3 clean-up events",
            "image_url": "https://via.placeholder.com/100?text=Eco"
        }
    ]
    
    display_user_badges(sample_badges)

def display_user_events(events, is_past=False):
    """Display user's registered events"""
    for event in events:
        with st.container():
            st.markdown(f"""
            <div class="card event-card">
                <h3>{event.get('title')}</h3>
                <p><strong>Date:</strong> {event.get('date')} at {event.get('time')}</p>
                <p><strong>Location:</strong> {event.get('location')}</p>
                <p><strong>Type:</strong> {event.get('event_type')}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if not is_past:
                # Show cancel button for upcoming events
                if st.button(f"Cancel Registration (Event {event.get('id')})", key=f"cancel_reg_{event.get('id')}"):
                    # API call to cancel registration would go here
                    st.success("Registration cancelled successfully!")
            else:
                # Show points earned for past events
                st.write(f"Points earned: **{event.get('points_earned', 0)}**")
            
            st.markdown("---")

def display_sample_user_events(is_past=False):
    """Display sample user events"""
    if not is_past:
        # Sample upcoming events
        sample_events = [
            {
                "id": "1",
                "title": "Weekend Hiking Adventure",
                "description": "Join us for a refreshing hike through the pine forests of Baguio.",
                "event_type": "Hiking",
                "location": "Baguio City",
                "date": (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
                "time": "08:00 AM"
            }
        ]
    else:
        # Sample past events
        sample_events = [
            {
                "id": "2",
                "title": "Environmental Conservation Workshop",
                "description": "Learn about local conservation efforts.",
                "event_type": "Workshop",
                "location": "La Trinidad",
                "date": (datetime.now() - timedelta(days=10)).strftime("%Y-%m-%d"),
                "time": "01:00 PM",
                "points_earned": 40
            },
            {
                "id": "3",
                "title": "Community Clean-up Drive",
                "description": "Help clean up our community parks and trails.",
                "event_type": "Clean-up",
                "location": "Baguio City",
                "date": (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d"),
                "time": "09:00 AM",
                "points_earned": 75
            }
        ]
    
    display_user_events(sample_events, is_past)

def display_points_history(points_history):
    """Display points history in a table"""
    history_data = []
    
    for entry in points_history:
        # Format timestamp
        try:
            dt = datetime.fromisoformat(entry.get('timestamp', '').replace('Z', '+00:00'))
            date_str = dt.strftime("%Y-%m-%d %H:%M")
        except:
            date_str = entry.get('timestamp', '')
        
        history_data.append({
            "Date": date_str,
            "Points": entry.get('points', 0),
            "Reason": entry.get('reason', '')
        })
    
    if history_data:
        st.dataframe(pd.DataFrame(history_data), hide_index=True)
    else:
        st.info("No points history available.")

def display_sample_points_history():
    """Display sample points history"""
    sample_history = [
        {
            "timestamp": (datetime.now() - timedelta(days=5)).isoformat(),
            "points": 50,
            "reason": "Completed Weekend Hiking Adventure"
        },
        {
            "timestamp": (datetime.now() - timedelta(days=15)).isoformat(),
            "points": 40,
            "reason": "Attended Environmental Workshop"
        },
        {
            "timestamp": (datetime.now() - timedelta(days=30)).isoformat(),
            "points": 75,
            "reason": "Participated in Community Clean-up"
        }
    ]
    
    display_points_history(sample_history)

def show_leaderboard_page():
    """Display leaderboard with top users by points"""
    st.title("Community Leaderboard")
    
    try:
        # Try to fetch leaderboard data from API
        leaderboard_data = get_leaderboard(limit=20)
        
        if not leaderboard_data:
            st.info("Leaderboard data is not available at the moment.")
            show_sample_leaderboard()
        else:
            display_leaderboard(leaderboard_data)
    
    except Exception as e:
        st.error(f"Error loading leaderboard: {str(e)}")
        # Fallback to sample data
        show_sample_leaderboard()

def show_sample_leaderboard():
    """Display sample leaderboard as fallback"""
    sample_leaderboard = [
        {"rank": 1, "name": "Sarah Smith", "username": "naturewarrior", "points": 1250, "badges": 8},
        {"rank": 2, "name": "John Doe", "username": "johnd", "points": 980, "badges": 6},
        {"rank": 3, "name": "Maria Garcia", "username": "mgarcia", "points": 875, "badges": 5},
        {"rank": 4, "name": "David Lee", "username": "dlee", "points": 820, "badges": 7},
        {"rank": 5, "name": "Emma Wilson", "username": "ewilson", "points": 760, "badges": 4},
        {"rank": 6, "name": "Michael Brown", "username": "mbrown", "points": 740, "badges": 5},
        {"rank": 7, "name": "Sophia Martinez", "username": "smartinez", "points": 690, "badges": 4},
        {"rank": 8, "name": "James Johnson", "username": "jjohnson", "points": 650, "badges": 3},
        {"rank": 9, "name": "Olivia Davis", "username": "odavis", "points": 620, "badges": 4},
        {"rank": 10, "name": "William Miller", "username": "wmiller", "points": 590, "badges": 3}
    ]
    
    display_leaderboard(sample_leaderboard)

def display_leaderboard(leaderboard_data):
    """Display leaderboard in a visually appealing format"""
    # Top 3 users with special highlighting
    st.subheader("Top Participants")
    top_cols = st.columns(3)
    
    # Ensure we have at least 3 entries for the top display
    while len(leaderboard_data) < 3:
        leaderboard_data.append({"rank": len(leaderboard_data) + 1, "name": "---", "username": "---", "points": 0, "badges": 0})
    
    # Display top 3 with medals
    for i, user in enumerate(leaderboard_data[:3]):
        with top_cols[i]:
            medal = "🥇" if i == 0 else "🥈" if i == 1 else "🥉"
            
            st.markdown(f"""
            <div style="text-align: center;">
                <h1>{medal}</h1>
                <img src="https://via.placeholder.com/100?text={user.get('name', '').split()[0]}" width="80" style="border-radius: 50%;">
                <h3>{user.get('name', '')}</h3>
                <p><strong>{user.get('points', 0)}</strong> points</p>
                <p><strong>{user.get('badges', 0)}</strong> badges</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Display the rest of the leaderboard as a table
    st.subheader("Leaderboard")
    
    # Create DataFrame for display
    leaderboard_df = pd.DataFrame([
        {
            "Rank": user.get("rank", i+1),
            "Name": user.get("name", ""),
            "Username": user.get("username", ""),
            "Points": user.get("points", 0),
            "Badges": user.get("badges", 0)
        } for i, user in enumerate(leaderboard_data)
    ])
    
    # Highlight current user if in leaderboard
    current_username = st.session_state.get("user_info", {}).get("username", "")
    
    # Display as styled dataframe
    st.dataframe(
        leaderboard_df,
        column_config={
            "Rank": st.column_config.NumberColumn(format="%d"),
            "Points": st.column_config.NumberColumn(format="%d"),
            "Badges": st.column_config.NumberColumn(format="%d")
        },
        hide_index=True
    )
    
    # Motivational message
    st.info("Participate in more events to climb the leaderboard and earn badges!")

def show_badge_gallery():
    """Display badge gallery with all available badges and user progress"""
    st.title("Badge Gallery")
    
    try:
        # Try to fetch badges from API
        badges_data = get_badges()
        
        if not badges_data:
            st.info("Badge information is not available at the moment.")
            show_sample_badge_gallery()
        else:
            # Get user badges for comparison
            user_info = st.session_state.get("user_info", {})
            user_badges = []
            
            if user_info:
                try:
                    user_badges = get_user_badges(user_info.get("id", ""))
                except:
                    user_badges = []
            
            display_badge_gallery(badges_data, user_badges)
    
    except Exception as e:
        st.error(f"Error loading badges: {str(e)}")
        # Fallback to sample data
        show_sample_badge_gallery()

def show_sample_badge_gallery():
    """Display sample badge gallery as fallback"""
    # Sample badges with different levels (bronze, silver, gold)
    badges = [
        {
            "id": 1,
            "name": "Trivia Master",
            "description": "Participate in 3 trivia nights",
            "category": "Trivia",
            "level": "bronze",
            "points_value": 50,
            "requirements": "Participate in 3 trivia nights"
        },
        {
            "id": 2,
            "name": "Trivia Champion",
            "description": "Win a trivia night competition",
            "category": "Trivia",
            "level": "silver",
            "points_value": 100,
            "requirements": "Win a trivia night competition"
        },
        {
            "id": 3,
            "name": "Trivia Legend",
            "description": "Win 3 trivia night competitions",
            "category": "Trivia",
            "level": "gold",
            "points_value": 250,
            "requirements": "Win 3 trivia night competitions"
        },
        {
            "id": 4,
            "name": "Game Night Rookie",
            "description": "Participate in your first game night",
            "category": "Games",
            "level": "bronze",
            "points_value": 25,
            "requirements": "Participate in your first game night"
        },
        {
            "id": 5,
            "name": "Game Night Regular",
            "description": "Participate in 5 game nights",
            "category": "Games",
            "level": "silver",
            "points_value": 75,
            "requirements": "Participate in 5 game nights"
        },
        {
            "id": 6,
            "name": "Game Night Veteran",
            "description": "Participate in 10 game nights",
            "category": "Games",
            "level": "gold",
            "points_value": 150,
            "requirements": "Participate in 10 game nights"
        },
        {
            "id": 7,
            "name": "Mystery Solver",
            "description": "Solve your first murder mystery",
            "category": "Mystery",
            "level": "bronze",
            "points_value": 75,
            "requirements": "Solve your first murder mystery"
        },
        {
            "id": 8,
            "name": "Mystery Sleuth",
            "description": "Solve 3 murder mysteries",
            "category": "Mystery",
            "level": "silver",
            "points_value": 150,
            "requirements": "Solve 3 murder mysteries"
        },
        {
            "id": 9,
            "name": "Mystery Detective",
            "description": "Solve 5 murder mysteries",
            "category": "Mystery",
            "level": "gold",
            "points_value": 300,
            "requirements": "Solve 5 murder mysteries"
        },
        {
            "id": 10,
            "name": "Weekly Streak",
            "description": "Attend events for 3 consecutive weeks",
            "category": "Attendance",
            "level": "bronze",
            "points_value": 100,
            "requirements": "Attend events for 3 consecutive weeks"
        },
        {
            "id": 11,
            "name": "Monthly Dedication",
            "description": "Attend events for 2 consecutive months",
            "category": "Attendance",
            "level": "silver",
            "points_value": 200,
            "requirements": "Attend events for 2 consecutive months"
        },
        {
            "id": 12,
            "name": "Seasonal Enthusiast",
            "description": "Attend events for all 3 months of a season",
            "category": "Attendance",
            "level": "gold",
            "points_value": 500,
            "requirements": "Attend events for all 3 months of a season"
        }
    ]
    
    # Sample user badges (some earned)
    user_badges = [
        {
            "id": 1,
            "name": "Trivia Master",
            "description": "Participate in 3 trivia nights",
            "category": "Trivia",
            "level": "bronze",
            "earned_date": "2025-02-15"
        },
        {
            "id": 4,
            "name": "Game Night Rookie",
            "description": "Participate in your first game night",
            "category": "Games",
            "level": "bronze",
            "earned_date": "2025-03-01"
        },
        {
            "id": 10,
            "name": "Weekly Streak",
            "description": "Attend events for 3 consecutive weeks",
            "category": "Attendance",
            "level": "bronze",
            "earned_date": "2025-03-20"
        }
    ]
    
    # Display badge gallery
    display_badge_gallery(badges, user_badges)

def display_badge_gallery(badges, user_badges=[]):
    """Display all badges with user progress"""
    # Extract user badge IDs
    user_badge_ids = [badge.get("id") for badge in user_badges]
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        category_filter = st.multiselect(
            "Category",
            sorted(list(set([badge.get("category") for badge in badges if badge.get("category")])))
        )
    
    with col2:
        status_filter = st.radio(
            "Status",
            ["All", "Earned", "Not Earned"],
            horizontal=True
        )
    
    # Apply filters
    filtered_badges = badges
    
    if category_filter:
        filtered_badges = [badge for badge in filtered_badges if badge.get("category") in category_filter]
    
    if status_filter == "Earned":
        filtered_badges = [badge for badge in filtered_badges if badge.get("id") in user_badge_ids]
    elif status_filter == "Not Earned":
        filtered_badges = [badge for badge in filtered_badges if badge.get("id") not in user_badge_ids]
    
    # Display badges in a grid
    st.subheader("Badges")
    
    if not filtered_badges:
        st.info("No badges match your filter criteria.")
    else:
        # Create rows of 3 badges each
        cols = st.columns(3)
        
        for i, badge in enumerate(filtered_badges):
            col_idx = i % 3
            
            with cols[col_idx]:
                # Determine badge level class
                level = badge.get("level", "bronze").lower()
                badge_class = f"badge-{level}"
                
                # Create card with appropriate styling
                st.markdown(f"""
                <div class="card">
                    <div class="badge {badge_class}">
                        <h3>{badge.get("name")}</h3>
                        <p>{badge.get("description")}</p>
                        <p><strong>Category:</strong> {badge.get("category")}</p>
                        <p><strong>Level:</strong> {level.capitalize()}</p>
                        <p><strong>Points:</strong> {badge.get("points_value", 0)}</p>
                        <p><strong>Status:</strong> {"Earned" if badge.get("id") in user_badge_ids else "Not Earned"}</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# Main function
def main():
    """Main application entry point"""
    # Force authentication check at the start
    if "is_authenticated" not in st.session_state:
        st.session_state["is_authenticated"] = False
    
    # Direct login with demo credentials for testing
    # This is a temporary solution until the backend is available
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.checkbox("Quick Demo Login", value=False):
            st.session_state["user_info"] = {
                "id": "123",
                "username": "demo",
                "first_name": "Demo",
                "last_name": "User",
                "email": "demo@example.com",
                "points": 350,
                "role": "user"
            }
            st.session_state["is_authenticated"] = True
            st.success("Demo login successful!")
    
    # Check authentication and show appropriate page
    if st.session_state.get("is_authenticated", False):
        show_main_app()
    else:
        show_login_page()

# Run the app
if __name__ == "__main__":
    main()
