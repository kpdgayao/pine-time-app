"""
Pine Time Admin Dashboard - Main Application
"""

import streamlit as st
import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add utils directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "utils"))

# Import utilities
from utils.api import (
    get_users, get_events, get_event_popularity, get_user_engagement, 
    get_points_distribution, get_leaderboard, get_points_history, get_badges
)
from utils.auth import login, logout, check_authentication, check_admin_access

# Set page configuration
st.set_page_config(
    page_title="Pine Time Admin Dashboard",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown("""
<style>
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
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "is_authenticated" not in st.session_state:
    st.session_state["is_authenticated"] = False

def show_login_page():
    """Display login form"""
    st.title("Pine Time Admin Dashboard")
    
    with st.container():
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.image("https://via.placeholder.com/300x200?text=Pine+Time+Logo", width=300)
            
        with col2:
            st.subheader("Admin Login")
            
            # Show any error messages
            if "login_error" in st.session_state:
                st.error(st.session_state["login_error"])
                del st.session_state["login_error"]
            
            # Login form
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submit = st.form_submit_button("Login")
                
                if submit:
                    if username and password:
                        if login(username, password):
                            st.session_state["is_authenticated"] = True
                            st.rerun()
                    else:
                        st.error("Please enter both username and password")

def show_main_app():
    """Display main app with navigation"""
    # Check if user is authenticated
    if not check_authentication():
        st.session_state["is_authenticated"] = False
        st.rerun()
    
    # Sidebar navigation
    with st.sidebar:
        st.title("Pine Time Admin")
        
        # Show user info
        if "user_info" in st.session_state:
            user_info = st.session_state["user_info"]
            st.write(f"Welcome, **{user_info.get('first_name', '')} {user_info.get('last_name', '')}**")
            st.write(f"Role: **{user_info.get('role', 'admin').capitalize()}**")
        
        selected = st.sidebar.radio(
            "Navigation",
            ["Dashboard", "Events", "Users", "Analytics", "Logout"]
        )
        
        st.sidebar.markdown("---")
        st.sidebar.info(
            "Pine Time Admin Dashboard provides comprehensive management tools for the Pine Time Experience platform."
        )
    
    # Display selected page
    if selected == "Dashboard":
        show_dashboard()
    elif selected == "Events":
        show_events()
    elif selected == "Users":
        show_users()
    elif selected == "Analytics":
        show_analytics()
    elif selected == "Logout":
        logout()
        st.session_state["is_authenticated"] = False
        st.rerun()

def show_dashboard():
    """Display dashboard overview with key metrics"""
    st.title("Dashboard Overview")
    st.markdown("Welcome to the Pine Time Admin Dashboard. Here's an overview of key metrics.")
    
    # Fetch data for metrics
    try:
        users_data = get_users()
        events_data = get_events()
        leaderboard = get_leaderboard(limit=1)  # Get top user
        
        total_users = users_data.get("total", 0)
        active_events_count = sum(1 for event in events_data.get("items", []) 
                                if event.get("status", "").lower() == "active")
        
        # Calculate total registrations across all events
        total_registrations = sum(len(event.get("registrations", [])) 
                                for event in events_data.get("items", []))
        
        # Get total points from top user or default to 0
        total_points = leaderboard[0].get("points", 0) if leaderboard else 0
        
        # Display metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                label="Total Users",
                value=total_users,
                delta=None
            )
        
        with col2:
            st.metric(
                label="Active Events",
                value=active_events_count,
                delta=None
            )
        
        with col3:
            st.metric(
                label="Total Registrations",
                value=total_registrations,
                delta=None
            )
        
        with col4:
            st.metric(
                label="Top User Points",
                value=total_points,
                delta=None
            )
        
        st.markdown("---")
        
        # Recent activity feed from points history
        st.subheader("Recent Activity")
        
        points_history = get_points_history()
        if points_history:
            # Convert to activity feed format
            activity_data = []
            for entry in points_history[:10]:  # Show only 10 most recent entries
                user_name = f"{entry.get('user', {}).get('first_name', '')} {entry.get('user', {}).get('last_name', '')}"
                points = entry.get('points', 0)
                reason = entry.get('reason', '')
                timestamp = entry.get('timestamp', '')
                
                # Format timestamp
                try:
                    dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    time_ago = get_time_ago(dt)
                except:
                    time_ago = "recently"
                
                activity_type = "points_awarded" if points > 0 else "points_deducted"
                
                activity_data.append({
                    "type": activity_type,
                    "details": f"{abs(points)} points {'awarded to' if points > 0 else 'deducted from'} {user_name} for {reason}",
                    "time": time_ago
                })
            
            # Display activity feed
            for activity in activity_data:
                col1, col2 = st.columns([1, 4])
                with col1:
                    if activity["type"] == "points_awarded":
                        st.info("🏆")
                    elif activity["type"] == "points_deducted":
                        st.warning("⬇️")
                with col2:
                    st.write(f"**{activity['details']}** - {activity['time']}")
        else:
            st.info("No recent activity found")
    
    except Exception as e:
        st.error(f"Error loading dashboard data: {str(e)}")
        # Fallback to sample data
        show_dashboard_sample_data()

def show_dashboard_sample_data():
    """Display dashboard with sample data as fallback"""
    # Display metrics with sample data
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Users",
            value=350,
            delta=None
        )
    
    with col2:
        st.metric(
            label="Active Events",
            value=25,
            delta=None
        )
    
    with col3:
        st.metric(
            label="Total Registrations",
            value=520,
            delta=None
        )
    
    with col4:
        st.metric(
            label="Top User Points",
            value=1250,
            delta=None
        )
    
    st.markdown("---")
    
    # Sample activity feed
    st.subheader("Recent Activity")
    
    activity_data = [
        {"type": "points_awarded", "details": "50 points awarded to Sarah Smith for event completion", "time": "2 hours ago"},
        {"type": "points_awarded", "details": "25 points awarded to John Doe for check-in", "time": "5 hours ago"},
        {"type": "points_deducted", "details": "10 points deducted from Mike Johnson for missed event", "time": "1 day ago"},
    ]
    
    for activity in activity_data:
        col1, col2 = st.columns([1, 4])
        with col1:
            if activity["type"] == "points_awarded":
                st.info("🏆")
            elif activity["type"] == "points_deducted":
                st.warning("⬇️")
        with col2:
            st.write(f"**{activity['details']}** - {activity['time']}")

def show_events():
    """Import and show events page"""
    from pages.events import show_events
    show_events()

def show_users():
    """Import and show users page"""
    from pages.users import show_users
    show_users()

def show_analytics():
    """Import and show analytics page"""
    from pages.analytics import show_analytics
    show_analytics()

def get_time_ago(dt):
    """
    Convert datetime to human-readable time ago string
    
    Args:
        dt (datetime): Datetime to convert
        
    Returns:
        str: Human-readable time ago string
    """
    now = datetime.now()
    diff = now - dt
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "just now"

def main():
    """Main application entry point"""
    if st.session_state["is_authenticated"]:
        show_main_app()
    else:
        show_login_page()

if __name__ == "__main__":
    main()
