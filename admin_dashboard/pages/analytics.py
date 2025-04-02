"""
Analytics page for Pine Time Admin Dashboard.
Displays event popularity, user engagement, and points distribution.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os
import random  # For demo data generation

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api import (
    get_event_popularity, get_user_engagement, get_points_distribution,
    get_events, get_users
)
from utils.auth import check_admin_access

def show_analytics():
    """Display analytics dashboard with charts and insights"""
    # Check admin access
    check_admin_access()
    
    st.title("Analytics Dashboard")
    
    # Date range filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now() - timedelta(days=30)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now()
        )
    
    if start_date > end_date:
        st.error("Start date must be before end date")
        return
    
    # Fetch analytics data
    event_popularity = get_event_popularity()
    user_engagement = get_user_engagement()
    points_distribution = get_points_distribution()
    
    # If API doesn't return data, generate sample data for demonstration
    if not event_popularity or not user_engagement or not points_distribution:
        st.info("Using sample data for demonstration. In production, this would use real data from the API.")
        event_popularity, user_engagement, points_distribution = generate_sample_data()
    
    # Create tabs for different analytics views
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview", "Event Analytics", "User Analytics", "Points Analytics"
    ])
    
    # Overview Tab
    with tab1:
        show_overview_analytics(event_popularity, user_engagement, points_distribution)
    
    # Event Analytics Tab
    with tab2:
        show_event_analytics(event_popularity)
    
    # User Analytics Tab
    with tab3:
        show_user_analytics(user_engagement)
    
    # Points Analytics Tab
    with tab4:
        show_points_analytics(points_distribution)

def show_overview_analytics(event_popularity, user_engagement, points_distribution):
    """Display overview analytics with key metrics and trends"""
    st.header("Analytics Overview")
    st.write("Key metrics and trends across the Pine Time platform")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_events = event_popularity.get('total_events', 0)
        st.metric(
            label="Total Events",
            value=total_events,
            delta=event_popularity.get('new_events_last_month', 0)
        )
    
    with col2:
        total_users = user_engagement.get('total_users', 0)
        st.metric(
            label="Total Users",
            value=total_users,
            delta=user_engagement.get('new_users_last_month', 0)
        )
    
    with col3:
        avg_attendance = event_popularity.get('average_attendance', 0)
        st.metric(
            label="Avg. Attendance",
            value=f"{avg_attendance:.1f}",
            delta=event_popularity.get('attendance_change', 0)
        )
    
    with col4:
        total_points = points_distribution.get('total_points_awarded', 0)
        st.metric(
            label="Total Points",
            value=total_points,
            delta=points_distribution.get('points_change', 0)
        )
    
    st.markdown("---")
    
    # Platform activity trend
    st.subheader("Platform Activity Trend")
    
    # Create sample activity trend data
    activity_dates = pd.date_range(end=datetime.now(), periods=30).tolist()
    activity_data = {
        'date': activity_dates,
        'events': [random.randint(1, 5) for _ in range(30)],
        'registrations': [random.randint(5, 20) for _ in range(30)],
        'completions': [random.randint(3, 15) for _ in range(30)]
    }
    df_activity = pd.DataFrame(activity_data)
    
    # Create line chart
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_activity['date'], 
        y=df_activity['events'],
        mode='lines+markers',
        name='Events',
        line=dict(color='#2E7D32', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df_activity['date'], 
        y=df_activity['registrations'],
        mode='lines+markers',
        name='Registrations',
        line=dict(color='#1976D2', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=df_activity['date'], 
        y=df_activity['completions'],
        mode='lines+markers',
        name='Completions',
        line=dict(color='#FFA000', width=2)
    ))
    
    fig.update_layout(
        title='Daily Platform Activity',
        xaxis_title='Date',
        yaxis_title='Count',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Key insights
    st.subheader("Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info(
            "**User Engagement Insight**\n\n"
            f"User engagement has {'increased' if user_engagement.get('engagement_change', 0) > 0 else 'decreased'} "
            f"by {abs(user_engagement.get('engagement_change', 0))}% in the last month. "
            f"The most active day is {user_engagement.get('most_active_day', 'Saturday')}."
        )
    
    with col2:
        st.info(
            "**Event Popularity Insight**\n\n"
            f"The most popular event category is '{event_popularity.get('most_popular_category', 'Outdoor')}' "
            f"with an average attendance of {event_popularity.get('category_attendance', {}).get('Outdoor', 0)} users per event."
        )

def show_event_analytics(event_popularity):
    """Display detailed event analytics"""
    st.header("Event Analytics")
    st.write("Detailed analysis of event performance and attendance")
    
    # Event popularity by category
    st.subheader("Event Popularity by Category")
    
    category_data = event_popularity.get('category_attendance', {})
    if category_data:
        df_categories = pd.DataFrame({
            'Category': list(category_data.keys()),
            'Average Attendance': list(category_data.values())
        })
        
        fig = px.bar(
            df_categories,
            x='Category',
            y='Average Attendance',
            title='Average Attendance by Event Category',
            color='Average Attendance',
            color_continuous_scale='Viridis',
            text='Average Attendance'
        )
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No category attendance data available")
    
    # Event completion rate
    st.subheader("Event Completion Rate")
    
    completion_data = event_popularity.get('completion_rate', {})
    if completion_data:
        df_completion = pd.DataFrame({
            'Event': list(completion_data.keys()),
            'Completion Rate (%)': [rate * 100 for rate in completion_data.values()]
        })
        
        df_completion = df_completion.sort_values('Completion Rate (%)', ascending=False)
        
        fig = px.bar(
            df_completion,
            x='Event',
            y='Completion Rate (%)',
            title='Event Completion Rate',
            color='Completion Rate (%)',
            color_continuous_scale='RdYlGn',
            text='Completion Rate (%)'
        )
        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No completion rate data available")
    
    # Event attendance trend
    st.subheader("Event Attendance Trend")
    
    attendance_trend = event_popularity.get('attendance_trend', {})
    if attendance_trend:
        df_trend = pd.DataFrame({
            'Month': list(attendance_trend.keys()),
            'Average Attendance': list(attendance_trend.values())
        })
        
        fig = px.line(
            df_trend,
            x='Month',
            y='Average Attendance',
            title='Monthly Average Event Attendance',
            markers=True,
            line_shape='spline'
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No attendance trend data available")
    
    # Event location heatmap
    st.subheader("Event Locations")
    
    # This would normally come from the API
    # For demo, we'll create sample location data
    locations = [
        {"name": "Pine Forest Park", "lat": 37.7749, "lon": -122.4194, "events": 12},
        {"name": "Mountain View Trail", "lat": 37.3861, "lon": -122.0839, "events": 8},
        {"name": "Redwood Heights", "lat": 37.8044, "lon": -122.2212, "events": 5},
        {"name": "Coastal Reserve", "lat": 37.8199, "lon": -122.4783, "events": 10},
        {"name": "Valley Gardens", "lat": 37.4419, "lon": -122.1430, "events": 7}
    ]
    
    df_locations = pd.DataFrame(locations)
    
    fig = px.scatter_mapbox(
        df_locations,
        lat="lat",
        lon="lon",
        size="events",
        color="events",
        hover_name="name",
        zoom=8,
        height=400,
        color_continuous_scale=px.colors.sequential.Viridis
    )
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    st.plotly_chart(fig, use_container_width=True)

def show_user_analytics(user_engagement):
    """Display detailed user analytics"""
    st.header("User Analytics")
    st.write("Detailed analysis of user engagement and behavior")
    
    # User activity distribution
    st.subheader("User Activity Distribution")
    
    activity_data = user_engagement.get('activity_distribution', {})
    if activity_data:
        fig = go.Figure(data=[
            go.Pie(
                labels=list(activity_data.keys()),
                values=list(activity_data.values()),
                hole=.4,
                textinfo='label+percent',
                marker=dict(colors=['#2E7D32', '#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B'])
            )
        ])
        fig.update_layout(title_text="User Activity Distribution")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No user activity distribution data available")
    
    # User retention
    st.subheader("User Retention")
    
    retention_data = user_engagement.get('retention_rate', {})
    if retention_data:
        months = list(retention_data.keys())
        rates = [rate * 100 for rate in retention_data.values()]
        
        fig = px.line(
            x=months,
            y=rates,
            markers=True,
            title="Monthly User Retention Rate",
            labels={"x": "Month", "y": "Retention Rate (%)"}
        )
        fig.update_traces(line=dict(color="#2E7D32", width=3))
        fig.add_shape(
            type="line",
            x0=months[0],
            y0=75,
            x1=months[-1],
            y1=75,
            line=dict(color="green", width=2, dash="dash"),
        )
        fig.add_annotation(
            x=months[1],
            y=76,
            text="Target (75%)",
            showarrow=False,
            yshift=10
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No user retention data available")
    
    # User growth
    st.subheader("User Growth")
    
    growth_data = user_engagement.get('user_growth', {})
    if growth_data:
        months = list(growth_data.keys())
        new_users = list(growth_data.values())
        
        # Calculate cumulative users
        cumulative_users = []
        total = 0
        for users in new_users:
            total += users
            cumulative_users.append(total)
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=months,
            y=new_users,
            name='New Users',
            marker_color='#4CAF50'
        ))
        fig.add_trace(go.Scatter(
            x=months,
            y=cumulative_users,
            name='Total Users',
            marker_color='#2E7D32',
            mode='lines+markers'
        ))
        
        fig.update_layout(
            title='User Growth Over Time',
            xaxis_title='Month',
            yaxis_title='Users',
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No user growth data available")
    
    # User demographics
    st.subheader("User Demographics")
    
    # This would normally come from the API
    # For demo, we'll create sample demographic data
    age_groups = ['18-24', '25-34', '35-44', '45-54', '55+']
    age_distribution = [15, 35, 25, 15, 10]
    
    fig = px.bar(
        x=age_groups,
        y=age_distribution,
        title="Age Distribution",
        labels={"x": "Age Group", "y": "Percentage (%)"},
        color=age_distribution,
        color_continuous_scale='Viridis',
        text=age_distribution
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    
    st.plotly_chart(fig, use_container_width=True)

def show_points_analytics(points_distribution):
    """Display detailed points analytics"""
    st.header("Points Analytics")
    st.write("Detailed analysis of points distribution and rewards")
    
    # Points distribution by user tier
    st.subheader("Points Distribution by User Tier")
    
    tier_data = points_distribution.get('tier_distribution', {})
    if tier_data:
        tiers = list(tier_data.keys())
        points = list(tier_data.values())
        
        fig = px.pie(
            names=tiers,
            values=points,
            title="Points Distribution by User Tier",
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No tier distribution data available")
    
    # Points awarded by event type
    st.subheader("Points Awarded by Event Type")
    
    event_points = points_distribution.get('event_type_points', {})
    if event_points:
        event_types = list(event_points.keys())
        points_values = list(event_points.values())
        
        fig = px.bar(
            x=event_types,
            y=points_values,
            title="Points Awarded by Event Type",
            labels={"x": "Event Type", "y": "Total Points"},
            color=points_values,
            color_continuous_scale='Viridis',
            text=points_values
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No event type points data available")
    
    # Monthly points trend
    st.subheader("Monthly Points Trend")
    
    monthly_points = points_distribution.get('monthly_points', {})
    if monthly_points:
        months = list(monthly_points.keys())
        points_values = list(monthly_points.values())
        
        fig = px.line(
            x=months,
            y=points_values,
            title="Monthly Points Awarded",
            labels={"x": "Month", "y": "Total Points"},
            markers=True,
            line_shape='spline'
        )
        fig.update_traces(line=dict(color="#2E7D32", width=3))
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No monthly points data available")
    
    # Top earners
    st.subheader("Top Point Earners")
    
    # This would normally come from the API
    # For demo, we'll create sample top earners data
    top_earners = [
        {"name": "John Smith", "points": 1250, "events_completed": 15},
        {"name": "Emma Johnson", "points": 980, "events_completed": 12},
        {"name": "Michael Brown", "points": 875, "events_completed": 10},
        {"name": "Sophia Davis", "points": 820, "events_completed": 9},
        {"name": "William Wilson", "points": 760, "events_completed": 8},
        {"name": "Olivia Moore", "points": 720, "events_completed": 8},
        {"name": "James Taylor", "points": 690, "events_completed": 7},
        {"name": "Ava Anderson", "points": 650, "events_completed": 7},
        {"name": "Benjamin Thomas", "points": 620, "events_completed": 6},
        {"name": "Mia Jackson", "points": 590, "events_completed": 6}
    ]
    
    df_top_earners = pd.DataFrame(top_earners)
    
    fig = px.bar(
        df_top_earners,
        x='name',
        y='points',
        title="Top 10 Point Earners",
        color='points',
        color_continuous_scale='Viridis',
        text='points',
        hover_data=['events_completed']
    )
    fig.update_traces(texttemplate='%{text}', textposition='outside')
    fig.update_xaxes(title="User")
    fig.update_yaxes(title="Total Points")
    
    st.plotly_chart(fig, use_container_width=True)

def generate_sample_data():
    """Generate sample data for demonstration purposes"""
    # Sample event popularity data
    event_popularity = {
        "total_events": 45,
        "new_events_last_month": 8,
        "average_attendance": 18.5,
        "attendance_change": 2.3,
        "most_popular_category": "Outdoor",
        "category_attendance": {
            "Outdoor": 22.3,
            "Conservation": 19.8,
            "Education": 15.2,
            "Community": 17.5,
            "Wellness": 14.1
        },
        "completion_rate": {
            "Forest Hike": 0.92,
            "Tree Planting": 0.88,
            "Nature Photography": 0.76,
            "Bird Watching": 0.85,
            "Beach Cleanup": 0.90,
            "Sustainable Gardening": 0.82,
            "Wildlife Conservation": 0.79
        },
        "attendance_trend": {
            "Jan": 12.5,
            "Feb": 13.8,
            "Mar": 15.2,
            "Apr": 16.7,
            "May": 18.3,
            "Jun": 19.5
        }
    }
    
    # Sample user engagement data
    user_engagement = {
        "total_users": 350,
        "new_users_last_month": 42,
        "engagement_change": 5.7,
        "most_active_day": "Saturday",
        "activity_distribution": {
            "Highly Active": 0.25,
            "Active": 0.35,
            "Occasional": 0.28,
            "Inactive": 0.12
        },
        "retention_rate": {
            "Jan": 0.82,
            "Feb": 0.79,
            "Mar": 0.81,
            "Apr": 0.83,
            "May": 0.85,
            "Jun": 0.87
        },
        "user_growth": {
            "Jan": 35,
            "Feb": 42,
            "Mar": 38,
            "Apr": 45,
            "May": 52,
            "Jun": 42
        }
    }
    
    # Sample points distribution data
    points_distribution = {
        "total_points_awarded": 28500,
        "points_change": 3200,
        "tier_distribution": {
            "Bronze": 8500,
            "Silver": 12000,
            "Gold": 6000,
            "Platinum": 2000
        },
        "event_type_points": {
            "Outdoor": 9500,
            "Conservation": 7800,
            "Education": 5200,
            "Community": 4000,
            "Wellness": 2000
        },
        "monthly_points": {
            "Jan": 3500,
            "Feb": 4200,
            "Mar": 4800,
            "Apr": 5100,
            "May": 5400,
            "Jun": 5500
        }
    }
    
    return event_popularity, user_engagement, points_distribution
