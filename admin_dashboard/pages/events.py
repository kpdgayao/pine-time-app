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
    filtered_events = events
    
    if status_filter != "All":
        filtered_events = [e for e in filtered_events if e.get('status', '').lower() == status_filter.lower()]
    
    if date_filter != "All":
        today = datetime.now().date()
        if date_filter == "Upcoming":
            filtered_events = [
                e for e in filtered_events 
                if datetime.fromisoformat(e.get('date', today.isoformat())).date() > today
            ]
        elif date_filter == "Past":
            filtered_events = [
                e for e in filtered_events 
                if datetime.fromisoformat(e.get('date', today.isoformat())).date() < today
            ]
        elif date_filter == "Today":
            filtered_events = [
                e for e in filtered_events 
                if datetime.fromisoformat(e.get('date', today.isoformat())).date() == today
            ]
    
    if search_query:
        filtered_events = [
            e for e in filtered_events 
            if search_query.lower() in e.get('name', '').lower() or 
               search_query.lower() in e.get('description', '').lower() or
               search_query.lower() in e.get('location', '').lower()
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
            events_data.append({
                "ID": event.get('id', ''),
                "Name": event.get('name', ''),
                "Date": event.get('date', ''),
                "Location": event.get('location', ''),
                "Status": event.get('status', ''),
                "Registrations": len(event.get('registrations', [])),
                "Points": event.get('points', 0)
            })
        
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
            selected_event_id = st.selectbox(
                "Select Event",
                [event.get('id', '') for event in filtered_events],
                format_func=lambda x: next((e.get('name', '') for e in filtered_events if e.get('id', '') == x), x)
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
        name = st.text_input("Event Name*", placeholder="Forest Hike")
        description = st.text_area("Description*", placeholder="Join us for a guided hike through the forest...")
        
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Event Date*", value=datetime.now() + timedelta(days=7))
            time = st.time_input("Event Time*", value=datetime.strptime("09:00", "%H:%M").time())
        
        with col2:
            location = st.text_input("Location*", placeholder="Pine Forest Park")
            capacity = st.number_input("Capacity", min_value=1, value=20)
        
        col1, col2 = st.columns(2)
        with col1:
            points = st.number_input("Points Reward", min_value=0, value=50)
            duration = st.number_input("Duration (hours)", min_value=0.5, value=2.0, step=0.5)
        
        with col2:
            status = st.selectbox("Status", ["draft", "active", "completed", "cancelled"], index=1)
            tags = st.text_input("Tags (comma separated)", placeholder="hiking, nature, outdoor")
        
        image_url = st.text_input("Image URL", placeholder="https://example.com/image.jpg")
        
        submit_button = st.form_submit_button("Create Event")
        
        if submit_button:
            if not name or not description or not location:
                st.error("Please fill in all required fields")
            else:
                # Format date and time
                event_datetime = datetime.combine(date, time)
                
                # Prepare event data
                event_data = {
                    "name": name,
                    "description": description,
                    "date": event_datetime.isoformat(),
                    "location": location,
                    "capacity": capacity,
                    "points": points,
                    "duration": duration,
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
    # Fetch event details
    event = get_event(event_id)
    
    if not event:
        st.error("Event not found")
        st.session_state["events_tab"] = "list"
        st.session_state["selected_event"] = None
        st.experimental_rerun()
        return
    
    st.subheader(f"Edit Event: {event.get('name', '')}")
    
    # Parse event date and time
    event_datetime = datetime.fromisoformat(event.get('date', datetime.now().isoformat()))
    event_date = event_datetime.date()
    event_time = event_datetime.time()
    
    with st.form("edit_event_form"):
        name = st.text_input("Event Name*", value=event.get('name', ''))
        description = st.text_area("Description*", value=event.get('description', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            date = st.date_input("Event Date*", value=event_date)
            time = st.time_input("Event Time*", value=event_time)
        
        with col2:
            location = st.text_input("Location*", value=event.get('location', ''))
            capacity = st.number_input("Capacity", min_value=1, value=event.get('capacity', 20))
        
        col1, col2 = st.columns(2)
        with col1:
            points = st.number_input("Points Reward", min_value=0, value=event.get('points', 50))
            duration = st.number_input("Duration (hours)", min_value=0.5, value=event.get('duration', 2.0), step=0.5)
        
        with col2:
            status = st.selectbox(
                "Status", 
                ["draft", "active", "completed", "cancelled"], 
                index=["draft", "active", "completed", "cancelled"].index(event.get('status', 'active'))
            )
            tags = st.text_input(
                "Tags (comma separated)", 
                value=", ".join(event.get('tags', []))
            )
        
        image_url = st.text_input("Image URL", value=event.get('image_url', ''))
        
        submit_button = st.form_submit_button("Update Event")
        
        if submit_button:
            if not name or not description or not location:
                st.error("Please fill in all required fields")
            else:
                # Format date and time
                event_datetime = datetime.combine(date, time)
                
                # Prepare event data
                event_data = {
                    "name": name,
                    "description": description,
                    "date": event_datetime.isoformat(),
                    "location": location,
                    "capacity": capacity,
                    "points": points,
                    "duration": duration,
                    "status": status,
                    "tags": [tag.strip() for tag in tags.split(",")] if tags else [],
                    "image_url": image_url if image_url else None
                }
                
                # Update event
                if update_event(event_id, event_data):
                    st.success("Event updated successfully!")
                    st.session_state["events_tab"] = "list"
                    st.session_state["selected_event"] = None
                    st.experimental_rerun()
                else:
                    st.error("Failed to update event. Please try again.")
    
    # Cancel button
    if st.button("Cancel", key="cancel_edit_event"):
        st.session_state["events_tab"] = "list"
        st.session_state["selected_event"] = None
        st.experimental_rerun()

def show_manage_participants(event_id):
    """Display interface to manage event participants"""
    # Fetch event details
    event = get_event(event_id)
    
    if not event:
        st.error("Event not found")
        st.session_state["events_tab"] = "list"
        st.session_state["selected_event"] = None
        st.experimental_rerun()
        return
    
    st.subheader(f"Manage Participants: {event.get('name', '')}")
    
    # Event details
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Capacity", event.get('capacity', 0))
    with col2:
        st.metric("Registrations", len(event.get('registrations', [])))
    with col3:
        st.metric("Completed", len([r for r in event.get('registrations', []) if r.get('completed', False)]))
    
    # Tabs for registrations and check-ins
    tab1, tab2 = st.tabs(["Registrations", "Check-ins & Completion"])
    
    # Registrations tab
    with tab1:
        st.subheader("Current Registrations")
        
        if not event.get('registrations', []):
            st.info("No registrations for this event yet.")
        else:
            # Fetch user details for all registered users
            users = get_users()
            user_map = {user.get('id', ''): user for user in users}
            
            # Create registrations data
            registrations_data = []
            for reg in event.get('registrations', []):
                user_id = reg.get('user_id', '')
                user = user_map.get(user_id, {})
                
                registrations_data.append({
                    "User ID": user_id,
                    "Name": f"{user.get('first_name', '')} {user.get('last_name', '')}",
                    "Email": user.get('email', ''),
                    "Registration Date": reg.get('registration_date', ''),
                    "Checked In": "Yes" if reg.get('checked_in', False) else "No",
                    "Completed": "Yes" if reg.get('completed', False) else "No"
                })
            
            # Display registrations table
            df_registrations = pd.DataFrame(registrations_data)
            st.dataframe(
                df_registrations,
                hide_index=True,
                use_container_width=True
            )
    
    # Check-ins and completion tab
    with tab2:
        st.subheader("Check-in & Mark Completion")
        
        # Fetch users
        users = get_users()
        
        # Get registered user IDs
        registered_user_ids = [reg.get('user_id', '') for reg in event.get('registrations', [])]
        
        # Filter users to those who are registered
        registered_users = [user for user in users if user.get('id', '') in registered_user_ids]
        
        if not registered_users:
            st.info("No registered users to check in or mark as completed.")
        else:
            col1, col2 = st.columns(2)
            
            # Check-in section
            with col1:
                st.write("### Check-in User")
                
                # Get users who are not checked in yet
                not_checked_in_regs = [
                    reg for reg in event.get('registrations', []) 
                    if not reg.get('checked_in', False)
                ]
                not_checked_in_user_ids = [reg.get('user_id', '') for reg in not_checked_in_regs]
                not_checked_in_users = [user for user in registered_users if user.get('id', '') in not_checked_in_user_ids]
                
                if not not_checked_in_users:
                    st.info("All registered users are already checked in.")
                else:
                    selected_user_id_checkin = st.selectbox(
                        "Select User to Check In",
                        [user.get('id', '') for user in not_checked_in_users],
                        format_func=lambda x: next(
                            (f"{user.get('first_name', '')} {user.get('last_name', '')}" 
                             for user in not_checked_in_users if user.get('id', '') == x), 
                            x
                        )
                    )
                    
                    if st.button("Check In User", key="check_in_user"):
                        if check_in_user(event_id, selected_user_id_checkin):
                            st.success("User checked in successfully!")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to check in user. Please try again.")
            
            # Mark completion section
            with col2:
                st.write("### Mark Completion")
                
                # Get users who are checked in but not completed
                checked_in_not_completed_regs = [
                    reg for reg in event.get('registrations', []) 
                    if reg.get('checked_in', False) and not reg.get('completed', False)
                ]
                checked_in_not_completed_user_ids = [reg.get('user_id', '') for reg in checked_in_not_completed_regs]
                checked_in_not_completed_users = [
                    user for user in registered_users 
                    if user.get('id', '') in checked_in_not_completed_user_ids
                ]
                
                if not checked_in_not_completed_users:
                    st.info("No checked-in users pending completion.")
                else:
                    selected_user_id_complete = st.selectbox(
                        "Select User to Mark as Completed",
                        [user.get('id', '') for user in checked_in_not_completed_users],
                        format_func=lambda x: next(
                            (f"{user.get('first_name', '')} {user.get('last_name', '')}" 
                             for user in checked_in_not_completed_users if user.get('id', '') == x), 
                            x
                        )
                    )
                    
                    if st.button("Mark as Completed", key="mark_completed"):
                        if mark_event_complete(event_id, selected_user_id_complete):
                            st.success("User marked as completed successfully!")
                            st.experimental_rerun()
                        else:
                            st.error("Failed to mark user as completed. Please try again.")
    
    # Back button
    if st.button("Back to Events List", key="back_to_events_list"):
        st.session_state["events_tab"] = "list"
        st.session_state["selected_event"] = None
        st.experimental_rerun()
