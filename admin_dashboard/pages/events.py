"""
Events management page for Pine Time Admin Dashboard.
Handles CRUD operations for events, check-ins, and completion marking.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api import (
    get_events, get_event, create_event, update_event, delete_event, 
    check_in_user, mark_event_complete, get_users
)
from utils.auth import check_admin_access

def show_events():
    """Display events management interface"""
    # Check admin access
    check_admin_access()
    
    st.title("Event Management")
    
    # Initialize session state for event management
    if "events_tab" not in st.session_state:
        st.session_state["events_tab"] = "list"
    if "selected_event" not in st.session_state:
        st.session_state["selected_event"] = None
    if "create_event" in st.session_state and st.session_state["create_event"]:
        st.session_state["events_tab"] = "create"
        st.session_state["create_event"] = False
    
    # Tabs for different event operations
    tabs = ["List Events", "Create Event"]
    if st.session_state["selected_event"]:
        tabs.append("Edit Event")
        tabs.append("Manage Participants")
    
    tab_index = 0
    if st.session_state["events_tab"] == "create":
        tab_index = 1
    elif st.session_state["events_tab"] == "edit" and st.session_state["selected_event"]:
        tab_index = 2
    elif st.session_state["events_tab"] == "participants" and st.session_state["selected_event"]:
        tab_index = 3
    
    selected_tab = st.tabs(tabs)[tab_index]
    
    # List Events Tab
    if tab_index == 0:
        with selected_tab:
            show_events_list()
    
    # Create Event Tab
    elif tab_index == 1:
        with selected_tab:
            show_create_event_form()
    
    # Edit Event Tab
    elif tab_index == 2 and st.session_state["selected_event"]:
        with selected_tab:
            show_edit_event_form(st.session_state["selected_event"])
    
    # Manage Participants Tab
    elif tab_index == 3 and st.session_state["selected_event"]:
        with selected_tab:
            show_manage_participants(st.session_state["selected_event"])

def show_events_list():
    """Display list of events with actions"""
    # Fetch events
    events = get_events()
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    with col1:
        status_filter = st.selectbox(
            "Filter by Status",
            ["All", "Active", "Completed", "Cancelled"],
            index=0
        )
    
    with col2:
        date_filter = st.selectbox(
            "Filter by Date",
            ["All", "Upcoming", "Past", "Today"],
            index=0
        )
    
    with col3:
        search_query = st.text_input("Search Events", "")
    
    # Apply filters
    filtered_events = events.get("items", [])
    
    if status_filter != "All":
        filtered_events = [e for e in filtered_events if isinstance(e, dict) and e.get('status', '').lower() == status_filter.lower()]
    
    if date_filter != "All":
        today = datetime.now().date()
        if date_filter == "Upcoming":
            filtered_events = [
                e for e in filtered_events 
                if isinstance(e, dict) and datetime.fromisoformat(e.get('start_time', today.isoformat())).date() > today
            ]
        elif date_filter == "Past":
            filtered_events = [
                e for e in filtered_events 
                if isinstance(e, dict) and datetime.fromisoformat(e.get('start_time', today.isoformat())).date() < today
            ]
        elif date_filter == "Today":
            filtered_events = [
                e for e in filtered_events 
                if isinstance(e, dict) and datetime.fromisoformat(e.get('start_time', today.isoformat())).date() == today
            ]
    
    if search_query:
        filtered_events = [
            e for e in filtered_events 
            if isinstance(e, dict) and (
                search_query.lower() in e.get('title', '').lower() or 
                search_query.lower() in e.get('description', '').lower() or
                search_query.lower() in e.get('location', '').lower()
            )
        ]
    
    # Create new event button
    if st.button("➕ Create New Event", key="create_new_event"):
        st.session_state["events_tab"] = "create"
        st.experimental_rerun()
    
    # Display events
    if not filtered_events:
        st.info("No events found matching your criteria.")
    else:
        # Convert to DataFrame for display
        events_data = []
        for event in filtered_events:
            # Handle both dictionary and string/primitive types
            if isinstance(event, dict):
                # If event is a dictionary, use get() method with fallbacks for different field names
                # This handles both API field names and UI field names
                event_data = {
                    "ID": event.get('id', ''),
                    "Name": event.get('title', event.get('name', '')),  # Try both 'title' and 'name'
                    "Date": event.get('start_time', event.get('date', '')),  # Try both 'start_time' and 'date'
                    "Location": event.get('location', ''),
                    "Status": event.get('status', ''),
                    "Registrations": len(event.get('registrations', [])),
                    "Points": event.get('points_reward', event.get('points', 0))  # Try both 'points_reward' and 'points'
                }
            else:
                # If event is a string or other primitive type, create a basic entry
                event_data = {
                    "ID": str(event),
                    "Name": "Unknown",
                    "Date": "",
                    "Location": "",
                    "Status": "",
                    "Registrations": 0,
                    "Points": 0
                }
            events_data.append(event_data)
        
        df_events = pd.DataFrame(events_data)
        
        # Display events table
        st.dataframe(
            df_events,
            column_config={
                "ID": st.column_config.TextColumn("ID", width="small"),
                "Name": st.column_config.TextColumn("Name", width="medium"),
                "Date": st.column_config.DateColumn("Date", width="small"),
                "Location": st.column_config.TextColumn("Location", width="medium"),
                "Status": st.column_config.TextColumn("Status", width="small"),
                "Registrations": st.column_config.NumberColumn("Registrations", width="small"),
                "Points": st.column_config.NumberColumn("Points", width="small")
            },
            hide_index=True,
            use_container_width=True
        )
        
        # Event actions
        st.subheader("Event Actions")
        
        col1, col2 = st.columns(2)
        with col1:
            # Create a list of event IDs with safe type checking
            event_ids = []
            for event in filtered_events:
                if isinstance(event, dict):
                    event_ids.append(event.get('id', ''))
                else:
                    event_ids.append(str(event))
                    
            # Create a safe format function
            def safe_format_event_name(event_id):
                for event in filtered_events:
                    if isinstance(event, dict) and event.get('id', '') == event_id:
                        # Try both 'title' and 'name' field names
                        return event.get('title', event.get('name', event_id))
                return event_id
                
            selected_event_id = st.selectbox(
                "Select Event",
                event_ids,
                format_func=safe_format_event_name
            )
        
        with col2:
            action = st.selectbox(
                "Action",
                ["View/Edit Details", "Manage Participants", "Delete Event"]
            )
        
        if st.button("Perform Action", key="perform_event_action"):
            if action == "View/Edit Details":
                st.session_state["selected_event"] = selected_event_id
                st.session_state["events_tab"] = "edit"
                st.experimental_rerun()
            elif action == "Manage Participants":
                st.session_state["selected_event"] = selected_event_id
                st.session_state["events_tab"] = "participants"
                st.experimental_rerun()
            elif action == "Delete Event":
                if delete_event(selected_event_id):
                    st.success(f"Event deleted successfully")
                    st.experimental_rerun()
                else:
                    st.error("Failed to delete event")

def show_create_event_form():
    """Display form to create a new event"""
    st.subheader("Create New Event")
    
    with st.form("create_event_form"):
        title = st.text_input("Event Title*", placeholder="Forest Hike")  # Changed from 'Event Name' to 'Event Title'
        description = st.text_area("Description*", placeholder="Join us for a guided hike through the forest...")
        
        col1, col2 = st.columns(2)
        with col1:
            event_type = st.selectbox("Event Type*", ["regular", "workshop", "seminar", "social", "other"])  # Added Event Type field
            date = st.date_input("Event Date*", value=datetime.now() + timedelta(days=7))
            start_time = st.time_input("Start Time*", value=datetime.strptime("09:00", "%H:%M").time())  # Changed from 'Event Time' to 'Start Time'
        
        with col2:
            location = st.text_input("Location*", placeholder="Pine Forest Park")
            max_participants = st.number_input("Max Participants", min_value=1, value=20)  # Changed from 'Capacity' to 'Max Participants'
            end_time = st.time_input("End Time*", value=datetime.strptime("11:00", "%H:%M").time())  # Added End Time field
        
        col1, col2 = st.columns(2)
        with col1:
            points_reward = st.number_input("Points Reward", min_value=0, value=50)  # Changed from 'Points' to 'Points Reward'
            price = st.number_input("Price", min_value=0.0, value=0.0, step=10.0)  # Added Price field
        
        with col2:
            status = st.selectbox("Status", ["draft", "active", "completed", "cancelled"], index=1)
            tags = st.text_input("Tags (comma separated)", placeholder="hiking, nature, outdoor")
        
        image_url = st.text_input("Image URL", placeholder="https://example.com/image.jpg")
        
        submit_button = st.form_submit_button("Create Event")
        
        if submit_button:
            if not title or not description or not location:
                st.error("Please fill in all required fields")
            else:
                # Format start and end times
                start_datetime = datetime.combine(date, start_time)
                end_datetime = datetime.combine(date, end_time)
                
                # Ensure end time is after start time
                if end_datetime <= start_datetime:
                    st.error("End time must be after start time")
                else:
                    # Prepare event data with correct field names
                    event_data = {
                        "title": title,  # Using correct API field name
                        "description": description,
                        "event_type": event_type,  # Using correct API field name
                        "location": location,
                        "start_time": start_datetime.isoformat(),  # Using correct API field name
                        "end_time": end_datetime.isoformat(),  # Using correct API field name
                        "max_participants": max_participants,  # Using correct API field name
                        "points_reward": points_reward,  # Using correct API field name
                        "price": price,
                        "status": status,
                        "tags": [tag.strip() for tag in tags.split(",")] if tags else [],
                        "image_url": image_url if image_url else None
                    }
                    
                    # Create event
                    result = create_event(event_data)
                    if result:
                        st.success("Event created successfully!")
                        st.session_state["events_tab"] = "list"
                        st.experimental_rerun()
                    else:
                        st.error("Failed to create event. Please try again.")
    
    # Cancel button
    if st.button("Cancel", key="cancel_create_event"):
        st.session_state["events_tab"] = "list"
        st.experimental_rerun()

def show_edit_event_form(event_id):
    """Display form to edit an existing event"""
    st.subheader("Edit Event")
    
    # Fetch event details
    event = get_event(event_id)
    if not event:
        st.error("Event not found")
        return
    
    # Extract event details
    with st.form("edit_event_form"):
        title = st.text_input("Event Title*", value=event.get("title", ""))  # Changed from "name" to "title"
        description = st.text_area("Description*", value=event.get("description", ""))
        
        # Parse dates
        try:
            start_datetime = datetime.fromisoformat(event.get("start_time", ""))  # Changed from "date" to "start_time"
            end_datetime = datetime.fromisoformat(event.get("end_time", ""))  # Added end_time parsing
            event_date = start_datetime.date()
            start_time_val = start_datetime.time()
            end_time_val = end_datetime.time()
        except (ValueError, TypeError):
            event_date = datetime.now().date()
            start_time_val = datetime.strptime("09:00", "%H:%M").time()
            end_time_val = datetime.strptime("11:00", "%H:%M").time()
        
        col1, col2 = st.columns(2)
        with col1:
            event_type = st.selectbox(
                "Event Type*", 
                ["regular", "workshop", "seminar", "social", "other"],
                index=["regular", "workshop", "seminar", "social", "other"].index(event.get("event_type", "regular"))
            )  # Added Event Type field
            date = st.date_input("Event Date*", value=event_date)
            start_time = st.time_input("Start Time*", value=start_time_val)  # Changed from "Event Time" to "Start Time"
        
        with col2:
            location = st.text_input("Location*", value=event.get("location", ""))
            max_participants = st.number_input("Max Participants", min_value=1, value=event.get("max_participants", 20))  # Changed from "capacity" to "max_participants"
            end_time = st.time_input("End Time*", value=end_time_val)  # Added End Time field
        
        col1, col2 = st.columns(2)
        with col1:
            points_reward = st.number_input("Points Reward", min_value=0, value=event.get("points_reward", 0))  # Changed from "points" to "points_reward"
            price = st.number_input("Price", min_value=0.0, value=event.get("price", 0.0), step=10.0)  # Added Price field
        
        with col2:
            status = st.selectbox(
                "Status", 
                ["draft", "active", "completed", "cancelled"],
                index=["draft", "active", "completed", "cancelled"].index(event.get("status", "active"))
            )
            # Handle tags as comma-separated string
            tags_str = ", ".join(event.get("tags", []))
            tags = st.text_input("Tags (comma separated)", value=tags_str)
        
        image_url = st.text_input("Image URL", value=event.get("image_url", ""))
        
        submit_button = st.form_submit_button("Update Event")
        
        if submit_button:
            if not title or not description or not location:
                st.error("Please fill in all required fields")
            else:
                # Format start and end times
                start_datetime = datetime.combine(date, start_time)
                end_datetime = datetime.combine(date, end_time)
                
                # Ensure end time is after start time
                if end_datetime <= start_datetime:
                    st.error("End time must be after start time")
                else:
                    # Prepare event data with correct field names
                    event_data = {
                        "title": title,
                        "description": description,
                        "event_type": event_type,
                        "location": location,
                        "start_time": start_datetime.isoformat(),
                        "end_time": end_datetime.isoformat(),
                        "max_participants": max_participants,
                        "points_reward": points_reward,
                        "price": price,
                        "status": status,
                        "tags": [tag.strip() for tag in tags.split(",")] if tags else [],
                        "image_url": image_url if image_url else None
                    }
                    
                    # Update event
                    if update_event(event_id, event_data):
                        st.success("Event updated successfully!")
                        st.session_state["events_tab"] = "list"
                        st.experimental_rerun()
                    else:
                        st.error("Failed to update event. Please try again.")
    
    # Cancel button
    if st.button("Cancel", key="cancel_edit_event"):
        st.session_state["events_tab"] = "list"
        st.experimental_rerun()

def show_manage_participants(event_id):
    """Display interface to manage event participants"""
    st.subheader("Manage Participants")
    
    # Fetch event details
    event = get_event(event_id)
    if not event:
        st.error("Event not found")
        return
    
    # Display event info
    st.write(f"**Event:** {event.get('title', '')}")  # Changed from "name" to "title"
    st.write(f"**Date:** {event.get('start_time', '')}")  # Changed from "date" to "start_time"
    st.write(f"**Location:** {event.get('location', '')}")
    
    # Get registrations
    registrations = event.get("registrations", [])
    
    if not registrations:
        st.info("No registrations for this event yet.")
    else:
        # Display registrations
        st.write(f"**Total Registrations:** {len(registrations)}")
        
        # Convert to DataFrame for display
        registrations_data = []
        for reg in registrations:
            if isinstance(reg, dict):
                user_id = reg.get("user_id", "")
                user_name = reg.get("user_name", "Unknown")
                status = reg.get("status", "registered")
                checked_in = reg.get("checked_in", False)
                completed = reg.get("completed", False)
                
                registrations_data.append({
                    "User ID": user_id,
                    "Name": user_name,
                    "Status": status,
                    "Checked In": "✅" if checked_in else "❌",
                    "Completed": "✅" if completed else "❌"
                })
        
        if registrations_data:
            df_registrations = pd.DataFrame(registrations_data)
            st.dataframe(df_registrations, hide_index=True, use_container_width=True)
            
            # Participant actions
            st.subheader("Participant Actions")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                selected_user = st.selectbox(
                    "Select Participant",
                    [reg["User ID"] for reg in registrations_data],
                    format_func=lambda x: next((reg["Name"] for reg in registrations_data if reg["User ID"] == x), x)
                )
            
            with col2:
                action = st.selectbox(
                    "Action",
                    ["Check In", "Mark as Completed", "Remove Registration"]
                )
            
            with col3:
                if st.button("Perform Action", key="perform_participant_action"):
                    if action == "Check In":
                        if check_in_user(event_id, selected_user):
                            st.success(f"User checked in successfully")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to check in user")
                    elif action == "Mark as Completed":
                        if mark_event_complete(event_id, selected_user):
                            st.success(f"Event marked as completed for user")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to mark event as completed")
                    elif action == "Remove Registration":
                        # TODO: Implement remove registration functionality
                        st.error("Remove registration functionality not implemented yet")
        else:
            st.info("No valid registration data available.")
    
    # Add participant section
    st.subheader("Add Participant")
    
    # Get all users
    users_response = get_users()
    users = users_response.get("items", [])
    
    # Filter out users already registered
    registered_user_ids = [reg.get("user_id") for reg in registrations if isinstance(reg, dict)]
    available_users = [u for u in users if isinstance(u, dict) and u.get("id") not in registered_user_ids]
    
    if not available_users:
        st.info("No more users available to register.")
    else:
        col1, col2 = st.columns(2)
        with col1:
            # Create a safe format function for user display
            def format_user_display(user_id):
                for user in available_users:
                    if user.get("id") == user_id:
                        return f"{user.get('first_name', '')} {user.get('last_name', '')} ({user.get('email', '')})"
                return user_id
            
            selected_user_id = st.selectbox(
                "Select User",
                [u.get("id") for u in available_users],
                format_func=format_user_display
            )
        
        with col2:
            if st.button("Register User", key="register_user"):
                # TODO: Implement register user functionality
                st.error("Register user functionality not implemented yet")
    
    # Back button
    if st.button("Back to Events List", key="back_to_events"):
        st.session_state["events_tab"] = "list"
        st.experimental_rerun()
