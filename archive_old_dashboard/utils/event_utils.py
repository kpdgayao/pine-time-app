"""
Event utilities for the Pine Time Admin Dashboard.
Handles event data processing, validation, and specialized operations.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union, Tuple

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("event_utils")

def validate_event_data(event_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate event data before creating or updating an event.
    
    Args:
        event_data: Event data to validate
        
    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)
    """
    required_fields = ['title', 'description', 'start_time', 'end_time', 'location']
    missing_fields = [field for field in required_fields if not event_data.get(field)]
    
    if missing_fields:
        return False, f"Missing required fields: {', '.join(missing_fields)}"
    
    # Validate dates
    try:
        start_time = datetime.fromisoformat(event_data['start_time'].replace('Z', '+00:00'))
        end_time = datetime.fromisoformat(event_data['end_time'].replace('Z', '+00:00'))
        
        if end_time <= start_time:
            return False, "End time must be after start time"
    except ValueError:
        return False, "Invalid date format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
    
    # Validate points (if provided)
    if 'points_reward' in event_data:
        try:
            points = int(event_data['points_reward'])
            if points < 0:
                return False, "Points reward cannot be negative"
        except ValueError:
            return False, "Points reward must be a number"
    
    # Validate capacity (if provided)
    if 'capacity' in event_data:
        try:
            capacity = int(event_data['capacity'])
            if capacity < 1:
                return False, "Capacity must be at least 1"
        except ValueError:
            return False, "Capacity must be a number"
    
    return True, None

def format_event_for_display(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format event data for display in the UI.
    
    Args:
        event: Raw event data from API
        
    Returns:
        Dict[str, Any]: Formatted event data
    """
    if not event:
        return {}
    
    # Format dates for display
    start_time = event.get('start_time', '')
    end_time = event.get('end_time', '')
    
    try:
        if start_time:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            formatted_start = start_dt.strftime('%Y-%m-%d %H:%M')
        else:
            formatted_start = ''
            
        if end_time:
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            formatted_end = end_dt.strftime('%Y-%m-%d %H:%M')
        else:
            formatted_end = ''
    except ValueError:
        formatted_start = start_time
        formatted_end = end_time
    
    # Create formatted event
    formatted_event = {
        'id': event.get('id', ''),
        'title': event.get('title', ''),
        'description': event.get('description', ''),
        'start_time': start_time,  # Keep original for form
        'end_time': end_time,      # Keep original for form
        'formatted_start': formatted_start,
        'formatted_end': formatted_end,
        'location': event.get('location', ''),
        'status': event.get('status', 'active'),
        'event_type': event.get('event_type', ''),
        'capacity': event.get('capacity', 0),
        'points_reward': event.get('points_reward', 0),
        'registration_deadline': event.get('registration_deadline', ''),
        'image_url': event.get('image_url', ''),
        'registrations': event.get('registrations', []),
        'registration_count': len(event.get('registrations', [])),
        'is_full': len(event.get('registrations', [])) >= event.get('capacity', 0) if event.get('capacity', 0) > 0 else False
    }
    
    return formatted_event

def get_event_status_options() -> List[Dict[str, str]]:
    """
    Get list of event status options.
    
    Returns:
        List[Dict[str, str]]: List of status options with id and name
    """
    return [
        {'id': 'active', 'name': 'Active'},
        {'id': 'completed', 'name': 'Completed'},
        {'id': 'cancelled', 'name': 'Cancelled'},
        {'id': 'draft', 'name': 'Draft'}
    ]

def get_event_type_options() -> List[Dict[str, str]]:
    """
    Get list of event type options.
    
    Returns:
        List[Dict[str, str]]: List of event type options with id and name
    """
    return [
        {'id': 'workshop', 'name': 'Workshop'},
        {'id': 'seminar', 'name': 'Seminar'},
        {'id': 'conference', 'name': 'Conference'},
        {'id': 'meetup', 'name': 'Meetup'},
        {'id': 'volunteering', 'name': 'Volunteering'},
        {'id': 'outdoor', 'name': 'Outdoor Activity'},
        {'id': 'social', 'name': 'Social Gathering'},
        {'id': 'other', 'name': 'Other'}
    ]

def calculate_event_statistics(events: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate statistics from a list of events.
    
    Args:
        events: List of event data
        
    Returns:
        Dict[str, Any]: Event statistics
    """
    if not events:
        return {
            'total_events': 0,
            'active_events': 0,
            'completed_events': 0,
            'cancelled_events': 0,
            'total_registrations': 0,
            'average_registrations': 0,
            'upcoming_events': 0,
            'past_events': 0,
            'events_by_type': {},
            'registrations_by_month': {}
        }
    
    # Initialize counters
    stats = {
        'total_events': len(events),
        'active_events': 0,
        'completed_events': 0,
        'cancelled_events': 0,
        'total_registrations': 0,
        'events_by_type': {},
        'registrations_by_month': {}
    }
    
    now = datetime.now()
    
    # Process each event
    for event in events:
        # Count by status
        status = event.get('status', '').lower()
        if status == 'active':
            stats['active_events'] += 1
        elif status == 'completed':
            stats['completed_events'] += 1
        elif status == 'cancelled':
            stats['cancelled_events'] += 1
        
        # Count registrations
        registrations = event.get('registrations', [])
        reg_count = len(registrations)
        stats['total_registrations'] += reg_count
        
        # Count by event type
        event_type = event.get('event_type', 'other')
        if event_type in stats['events_by_type']:
            stats['events_by_type'][event_type] += 1
        else:
            stats['events_by_type'][event_type] = 1
        
        # Count upcoming/past events
        try:
            start_time = datetime.fromisoformat(event.get('start_time', '').replace('Z', '+00:00'))
            if start_time > now:
                stats['upcoming_events'] = stats.get('upcoming_events', 0) + 1
            else:
                stats['past_events'] = stats.get('past_events', 0) + 1
                
            # Group registrations by month
            month_key = start_time.strftime('%Y-%m')
            if month_key in stats['registrations_by_month']:
                stats['registrations_by_month'][month_key] += reg_count
            else:
                stats['registrations_by_month'][month_key] = reg_count
        except (ValueError, TypeError):
            # Skip events with invalid dates
            pass
    
    # Calculate average registrations
    stats['average_registrations'] = round(stats['total_registrations'] / stats['total_events'], 1) if stats['total_events'] > 0 else 0
    
    return stats

def filter_events(events: List[Dict[str, Any]], filters: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Filter events based on provided criteria.
    
    Args:
        events: List of events to filter
        filters: Dictionary of filter criteria
        
    Returns:
        List[Dict[str, Any]]: Filtered events
    """
    if not events:
        return []
    
    filtered_events = events
    
    # Filter by status
    if filters.get('status') and filters['status'] != 'all':
        filtered_events = [
            e for e in filtered_events 
            if e.get('status', '').lower() == filters['status'].lower()
        ]
    
    # Filter by event type
    if filters.get('event_type') and filters['event_type'] != 'all':
        filtered_events = [
            e for e in filtered_events 
            if e.get('event_type', '').lower() == filters['event_type'].lower()
        ]
    
    # Filter by date range
    if filters.get('date_range'):
        date_range = filters['date_range']
        now = datetime.now()
        
        if date_range == 'upcoming':
            filtered_events = [
                e for e in filtered_events 
                if datetime.fromisoformat(e.get('start_time', now.isoformat()).replace('Z', '+00:00')) > now
            ]
        elif date_range == 'past':
            filtered_events = [
                e for e in filtered_events 
                if datetime.fromisoformat(e.get('start_time', now.isoformat()).replace('Z', '+00:00')) < now
            ]
        elif date_range == 'today':
            today = now.date()
            filtered_events = [
                e for e in filtered_events 
                if datetime.fromisoformat(e.get('start_time', now.isoformat()).replace('Z', '+00:00')).date() == today
            ]
        elif date_range == 'this_week':
            week_start = now.date() - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6)
            filtered_events = [
                e for e in filtered_events 
                if week_start <= datetime.fromisoformat(e.get('start_time', now.isoformat()).replace('Z', '+00:00')).date() <= week_end
            ]
        elif date_range == 'this_month':
            month_start = now.date().replace(day=1)
            next_month = month_start.replace(month=month_start.month % 12 + 1, year=month_start.year + (month_start.month == 12))
            month_end = next_month - timedelta(days=1)
            filtered_events = [
                e for e in filtered_events 
                if month_start <= datetime.fromisoformat(e.get('start_time', now.isoformat()).replace('Z', '+00:00')).date() <= month_end
            ]
    
    # Filter by search query
    if filters.get('search'):
        search = filters['search'].lower()
        filtered_events = [
            e for e in filtered_events 
            if search in e.get('title', '').lower() or 
               search in e.get('description', '').lower() or
               search in e.get('location', '').lower()
        ]
    
    return filtered_events
