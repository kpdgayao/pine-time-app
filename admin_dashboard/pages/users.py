"""
Users management page for Pine Time Admin Dashboard.
Handles user profile editing, points adjustment, and badge progress.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api import get_users, get_user, update_user, update_user_points, get_user_badges
from utils.auth import check_admin_access

def show_users():
    """Display users management interface"""
    # Check admin access
    check_admin_access()
    
    st.title("User Management")
    
    # Initialize session state for user management
    if "users_tab" not in st.session_state:
        st.session_state["users_tab"] = "list"
    if "selected_user" not in st.session_state:
        st.session_state["selected_user"] = None
    
    # Tabs for different user operations
    tabs = ["List Users", "User Details"]
    
    tab_index = 0
    if st.session_state["users_tab"] == "details" and st.session_state["selected_user"]:
        tab_index = 1
    
    selected_tab = st.tabs(tabs)[tab_index]
    
    # List Users Tab
    if tab_index == 0:
        with selected_tab:
            show_users_list()
    
    # User Details Tab
    elif tab_index == 1 and st.session_state["selected_user"]:
        with selected_tab:
            show_user_details(st.session_state["selected_user"])

def show_users_list():
    """Display list of users with actions"""
    # Fetch users
    users = get_users()
    
    # Filter controls
    col1, col2 = st.columns(2)
    with col1:
        role_filter = st.selectbox(
            "Filter by Role",
            ["All", "Admin", "User"],
            index=0
        )
    
    with col2:
        search_query = st.text_input("Search Users", "")
    
    # Apply filters
    filtered_users = users
    
    if role_filter != "All":
        filtered_users = [u for u in filtered_users if u.get('role', '').lower() == role_filter.lower()]
    
    if search_query:
        filtered_users = [
            u for u in filtered_users 
            if search_query.lower() in u.get('first_name', '').lower() or 
               search_query.lower() in u.get('last_name', '').lower() or
               search_query.lower() in u.get('email', '').lower() or
               search_query.lower() in u.get('username', '').lower()
        ]
    
    # Display users
    if not filtered_users:
        st.info("No users found matching your criteria.")
    else:
        # Convert to DataFrame for display
        users_data = []
        for user in filtered_users:
            users_data.append({
                "ID": user.get('id', ''),
                "Name": f"{user.get('first_name', '')} {user.get('last_name', '')}",
                "Username": user.get('username', ''),
                "Email": user.get('email', ''),
                "Role": user.get('role', 'user'),
                "Points": user.get('points', 0),
                "Joined": user.get('created_at', '')
            })
        
        df_users = pd.DataFrame(users_data)
        
        # Display users table
        st.dataframe(
            df_users,
            column_config={
                "ID": st.column_config.TextColumn("ID", width="small"),
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Username": st.column_config.TextColumn("Username", width="small"),
                "Email": st.column_config.TextColumn("Email", width="medium"),
                "Role": st.column_config.TextColumn("Role", width="small"),
                "Points": st.column_config.NumberColumn("Points", width="small"),
                "Joined": st.column_config.DateColumn("Joined", width="small")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # User actions
        st.subheader("User Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            selected_user_id = st.selectbox(
                "Select User",
                [user.get('id', '') for user in filtered_users],
                format_func=lambda x: next(
                    (f"{user.get('first_name', '')} {user.get('last_name', '')} ({user.get('email', '')})" 
                     for user in filtered_users if user.get('id', '') == x), 
                    x
                )
            )
        
        with col2:
            action = st.selectbox(
                "Action",
                ["View/Edit Profile", "Adjust Points", "View Badges"]
            )
        
        if st.button("Perform Action", key="perform_user_action"):
            st.session_state["selected_user"] = selected_user_id
            st.session_state["users_tab"] = "details"
            st.session_state["user_details_tab"] = action
            st.experimental_rerun()

def show_user_details(user_id):
    """Display detailed user information and actions"""
    # Fetch user details
    user = get_user(user_id)
    
    if not user:
        st.error("User not found")
        st.session_state["users_tab"] = "list"
        st.session_state["selected_user"] = None
        st.experimental_rerun()
        return
    
    st.subheader(f"User: {user.get('first_name', '')} {user.get('last_name', '')}")
    
    # Initialize user details tab if not set
    if "user_details_tab" not in st.session_state:
        st.session_state["user_details_tab"] = "View/Edit Profile"
    
    # Tabs for different user detail views
    tabs = ["Profile", "Points", "Badges"]
    
    tab_index = 0
    if st.session_state["user_details_tab"] == "Adjust Points":
        tab_index = 1
    elif st.session_state["user_details_tab"] == "View Badges":
        tab_index = 2
    
    selected_tab = st.tabs(tabs)[tab_index]
    
    # Profile Tab
    if tab_index == 0:
        with selected_tab:
            show_user_profile(user)
    
    # Points Tab
    elif tab_index == 1:
        with selected_tab:
            show_user_points(user)
    
    # Badges Tab
    elif tab_index == 2:
        with selected_tab:
            show_user_badges(user)
    
    # Back button
    if st.button("Back to Users List", key="back_to_users_list"):
        st.session_state["users_tab"] = "list"
        st.session_state["selected_user"] = None
        st.experimental_rerun()

def show_user_profile(user):
    """Display and edit user profile information"""
    st.write("### User Profile")
    
    with st.form("edit_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            first_name = st.text_input("First Name", value=user.get('first_name', ''))
            last_name = st.text_input("Last Name", value=user.get('last_name', ''))
            email = st.text_input("Email", value=user.get('email', ''))
        
        with col2:
            username = st.text_input("Username", value=user.get('username', ''))
            role = st.selectbox(
                "Role", 
                ["user", "admin"], 
                index=0 if user.get('role', 'user') == 'user' else 1
            )
            phone = st.text_input("Phone", value=user.get('phone', ''))
        
        bio = st.text_area("Bio", value=user.get('bio', ''))
        
        submit_button = st.form_submit_button("Update Profile")
        
        if submit_button:
            # Prepare user data
            user_data = {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "username": username,
                "role": role,
                "phone": phone,
                "bio": bio
            }
            
            # Update user
            if update_user(user.get('id', ''), user_data):
                st.success("User profile updated successfully!")
                st.experimental_rerun()
            else:
                st.error("Failed to update user profile. Please try again.")
    
    # User statistics
    st.write("### User Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Points", user.get('points', 0))
    
    with col2:
        st.metric("Events Attended", len(user.get('events_attended', [])))
    
    with col3:
        st.metric("Badges Earned", len(user.get('badges', [])))
    
    # Account information
    st.write("### Account Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Account Created:** {user.get('created_at', 'N/A')}")
        st.write(f"**Last Login:** {user.get('last_login', 'N/A')}")
    
    with col2:
        st.write(f"**Account Status:** {user.get('status', 'Active')}")
        st.write(f"**User ID:** {user.get('id', '')}")

def show_user_points(user):
    """Display and adjust user points"""
    st.write("### Points Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Current Points", user.get('points', 0))
    
    # Points history
    st.write("### Points History")
    
    # In a real app, this would come from the API
    points_history = user.get('points_history', [
        {"date": "2025-03-20", "amount": 50, "reason": "Completed Forest Hike"},
        {"date": "2025-03-15", "amount": 25, "reason": "Participated in Tree Planting"},
        {"date": "2025-03-10", "amount": 10, "reason": "Joined the platform"}
    ])
    
    if not points_history:
        st.info("No points history available.")
    else:
        # Convert to DataFrame for display
        df_points = pd.DataFrame(points_history)
        
        # Display points history
        st.dataframe(
            df_points,
            column_config={
                "date": st.column_config.DateColumn("Date"),
                "amount": st.column_config.NumberColumn("Points"),
                "reason": st.column_config.TextColumn("Reason")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Points visualization
        if len(points_history) > 1:
            # Create a line chart of points over time
            df_points_viz = df_points.copy()
            df_points_viz['date'] = pd.to_datetime(df_points_viz['date'])
            df_points_viz = df_points_viz.sort_values('date')
            df_points_viz['cumulative_points'] = df_points_viz['amount'].cumsum()
            
            fig = px.line(
                df_points_viz, 
                x='date', 
                y='cumulative_points',
                title='Points Accumulation Over Time',
                labels={'date': 'Date', 'cumulative_points': 'Total Points'},
                markers=True
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Adjust points
    st.write("### Adjust Points")
    
    with st.form("adjust_points_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            points_amount = st.number_input("Points Amount", min_value=-100, max_value=1000, value=0)
        
        with col2:
            points_reason = st.text_input("Reason", placeholder="e.g., Bonus for community contribution")
        
        submit_button = st.form_submit_button("Adjust Points")
        
        if submit_button:
            if points_amount == 0:
                st.warning("Please enter a non-zero points amount.")
            elif not points_reason:
                st.warning("Please provide a reason for the points adjustment.")
            else:
                # Update user points
                if update_user_points(user.get('id', ''), points_amount, points_reason):
                    st.success(f"Successfully {'added' if points_amount > 0 else 'deducted'} {abs(points_amount)} points!")
                    st.experimental_rerun()
                else:
                    st.error("Failed to adjust points. Please try again.")

def show_user_badges(user):
    """Display user badges and progress"""
    st.write("### User Badges")
    
    # Fetch user badges
    badges = get_user_badges(user.get('id', ''))
    
    if not badges:
        st.info("User has not earned any badges yet.")
    else:
        # Display badges in a grid
        cols = st.columns(3)
        
        for i, badge in enumerate(badges):
            with cols[i % 3]:
                st.image(
                    badge.get('image_url', 'https://via.placeholder.com/100?text=Badge'),
                    width=100
                )
                st.write(f"**{badge.get('name', '')}**")
                st.write(badge.get('description', ''))
                st.write(f"Earned: {badge.get('earned_date', 'N/A')}")
    
    # Badge progress
    st.write("### Badge Progress")
    
    # In a real app, this would come from the API
    badge_progress = [
        {"name": "Nature Explorer", "progress": 0.8, "requirements": "Attend 5 outdoor events"},
        {"name": "Community Leader", "progress": 0.4, "requirements": "Organize 3 community events"},
        {"name": "Sustainability Champion", "progress": 0.6, "requirements": "Complete 10 eco-friendly activities"}
    ]
    
    for badge in badge_progress:
        st.write(f"**{badge['name']}**")
        st.progress(badge['progress'])
        st.write(f"*{badge['requirements']}*")
        st.write(f"Progress: {int(badge['progress'] * 100)}%")
        st.write("---")
