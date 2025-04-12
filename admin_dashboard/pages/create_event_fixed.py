"""
Fixed event creation form for Pine Time Admin Dashboard.
This standalone script provides a form with the correct field names for the API.
"""

import streamlit as st
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.api import create_event
from utils.auth import check_admin_access

def show_create_event_form():
    """Display form to create a new event with correct API field names"""
    # Check admin access
    check_admin_access()
    
    st.title("Create New Event")
    st.markdown("This form uses the correct field names expected by the API.")
    
    with st.form("create_event_form"):
        title = st.text_input("Event Title*", placeholder="Forest Hike")
        description = st.text_area("Description*", placeholder="Join us for a guided hike through the forest...")
        
        col1, col2 = st.columns(2)
        with col1:
            event_type = st.selectbox("Event Type*", ["regular", "workshop", "seminar", "social", "other"])
            date = st.date_input("Event Date*", value=datetime.now() + timedelta(days=7))
            start_time = st.time_input("Start Time*", value=datetime.strptime("09:00", "%H:%M").time())
        
        with col2:
            location = st.text_input("Location*", placeholder="Pine Forest Park")
            max_participants = st.number_input("Max Participants", min_value=1, value=20)
            end_time = st.time_input("End Time*", value=datetime.strptime("11:00", "%H:%M").time())
        
        col1, col2 = st.columns(2)
        with col1:
            points_reward = st.number_input("Points Reward", min_value=0, value=50)
            price = st.number_input("Price", min_value=0.0, value=0.0, step=10.0)
        
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
                        "title": title,  # Correct field name for API
                        "description": description,
                        "event_type": event_type,  # Correct field name for API
                        "location": location,
                        "start_time": start_datetime.isoformat(),  # Correct field name for API
                        "end_time": end_datetime.isoformat(),  # Correct field name for API
                        "max_participants": max_participants,  # Correct field name for API
                        "points_reward": points_reward,  # Correct field name for API
                        "price": price,
                        "status": status,
                        "tags": [tag.strip() for tag in tags.split(",")] if tags else [],
                        "image_url": image_url if image_url else None
                    }
                    
                    # Log the event data for debugging
                    st.write("Sending the following data to the API:")
                    st.json(event_data)
                    
                    # Create event
                    result = create_event(event_data)
                    if result:
                        st.success("Event created successfully!")
                    else:
                        st.error("Failed to create event. Please try again.")
    
    # Back button
    if st.button("Back to Dashboard"):
        st.switch_page("app.py")

if __name__ == "__main__":
    show_create_event_form()
