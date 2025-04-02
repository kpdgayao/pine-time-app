"""
Dashboard overview page for Pine Time Admin Dashboard.
Displays key metrics and summary information.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api import get_users, get_events, get_event_popularity, get_user_engagement
from utils.auth import check_admin_access

def show_dashboard():
    """Display dashboard overview with key metrics"""
    # Check admin access
    check_admin_access()
    
    st.title("Dashboard Overview")
    st.markdown("Welcome to the Pine Time Admin Dashboard. Here's an overview of key metrics.")
    
    # Fetch data
    users = get_users()
    events = get_events()
    event_popularity = get_event_popularity()
    user_engagement = get_user_engagement()
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Users",
            value=len(users),
            delta=f"+{len([u for u in users if datetime.fromisoformat(u.get('created_at', datetime.now().isoformat()[:10])) > datetime.now() - timedelta(days=7)])}" if users else "+0",
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            label="Active Events",
            value=len([e for e in events if e.get('status') == 'active']) if events else 0,
            delta=None
        )
    
    with col3:
        total_registrations = sum(len(e.get('registrations', [])) for e in events) if events else 0
        st.metric(
            label="Total Registrations",
            value=total_registrations,
            delta=None
        )
    
    with col4:
        total_points = sum(u.get('points', 0) for u in users) if users else 0
        st.metric(
            label="Total Points Awarded",
            value=total_points,
            delta=None
        )
    
    st.markdown("---")
    
    # Display charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Recent Events")
        if events:
            # Create a dataframe for recent events
            recent_events = sorted(
                events, 
                key=lambda x: datetime.fromisoformat(x.get('date', datetime.now().isoformat()[:10])),
                reverse=True
            )[:5]
            
            df_events = pd.DataFrame(recent_events)
            if not df_events.empty and 'name' in df_events.columns and 'registrations' in df_events.columns:
                df_events['registration_count'] = df_events['registrations'].apply(len)
                fig = px.bar(
                    df_events,
                    x='name',
                    y='registration_count',
                    title="Recent Events by Registration",
                    labels={'name': 'Event Name', 'registration_count': 'Registrations'},
                    color_discrete_sequence=['#2E7D32']
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No recent event data available")
        else:
            st.info("No events data available")
    
    with col2:
        st.subheader("User Activity")
        if user_engagement:
            # Create a pie chart for user activity
            activity_data = user_engagement.get('activity_distribution', {})
            if activity_data:
                fig = go.Figure(data=[
                    go.Pie(
                        labels=list(activity_data.keys()),
                        values=list(activity_data.values()),
                        hole=.3,
                        marker_colors=['#2E7D32', '#4CAF50', '#8BC34A', '#CDDC39']
                    )
                ])
                fig.update_layout(title_text="User Activity Distribution")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No user activity data available")
        else:
            st.info("No user engagement data available")
    
    # Recent activity feed
    st.markdown("---")
    st.subheader("Recent Activity")
    
    # Create a sample activity feed (in a real app, this would come from the API)
    activity_data = [
        {"type": "event_created", "details": "New event 'Forest Hike' created", "time": "2 hours ago"},
        {"type": "user_joined", "details": "New user John Doe joined", "time": "5 hours ago"},
        {"type": "points_awarded", "details": "50 points awarded to Sarah Smith", "time": "1 day ago"},
        {"type": "event_completed", "details": "Event 'Tree Planting' marked as completed", "time": "2 days ago"},
    ]
    
    for activity in activity_data:
        col1, col2 = st.columns([1, 4])
        with col1:
            if activity["type"] == "event_created":
                st.info("📅")
            elif activity["type"] == "user_joined":
                st.info("👤")
            elif activity["type"] == "points_awarded":
                st.info("🏆")
            elif activity["type"] == "event_completed":
                st.info("✅")
        with col2:
            st.write(f"**{activity['details']}** - {activity['time']}")
    
    # Quick actions
    st.markdown("---")
    st.subheader("Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Create New Event", key="dashboard_new_event"):
            st.session_state["current_page"] = "events"
            st.session_state["create_event"] = True
            st.experimental_rerun()
    
    with col2:
        if st.button("Manage Users", key="dashboard_manage_users"):
            st.session_state["current_page"] = "users"
            st.experimental_rerun()
    
    with col3:
        if st.button("View Analytics", key="dashboard_view_analytics"):
            st.session_state["current_page"] = "analytics"
            st.experimental_rerun()
