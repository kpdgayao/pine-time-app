"""
Pine Time Application - API Load Testing Script
Uses Locust to simulate user load on the FastAPI backend with proper error handling.
"""

import os
import sys
import json
import logging
import time
import random
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from locust import HttpUser, task, between, events
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pine_time_api_test.log")
    ]
)
logger = logging.getLogger("pine_time_api_test")

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1_STR = "/api/v1"  # Match the FastAPI prefix

# Test configuration
CONFIG = {
    "users": {
        "min_wait": int(os.getenv("LOAD_TEST_MIN_WAIT", "1")),
        "max_wait": int(os.getenv("LOAD_TEST_MAX_WAIT", "5")),
        "count": int(os.getenv("LOAD_TEST_USER_COUNT", "10")),
        "spawn_rate": int(os.getenv("LOAD_TEST_SPAWN_RATE", "2")),
    },
    "auth": {
        "token_refresh_interval": int(os.getenv("TOKEN_REFRESH_INTERVAL", "1800")),
        "retry_attempts": int(os.getenv("AUTH_RETRY_ATTEMPTS", "3")),
        "retry_delay": int(os.getenv("AUTH_RETRY_DELAY", "2")),
    }
}

class PineTimeUser(HttpUser):
    """
    Simulated user for load testing the Pine Time API.
    """
    
    wait_time = between(CONFIG["users"]["min_wait"], CONFIG["users"]["max_wait"])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.user_id = None
        self.username = f"testuser{random.randint(1, 5)}"
        self.password = "password123"
        self.events_cache = []
        self.last_token_refresh = 0
    
    def on_start(self):
        """
        Called when a user starts.
        Login and store the token.
        """
        logger.info(f"Starting user simulation for {self.username}")
        self.login()
    
    def login(self):
        """
        Attempt to login with the test user.
        """
        try:
            with self.client.post(
                f"{API_V1_STR}/login/access-token",
                data={
                    "username": self.username,
                    "password": self.password
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                name="Login",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get('access_token')
                    self.last_token_refresh = datetime.now().timestamp()
                    logger.info(f"User {self.username} logged in successfully")
                    response.success()
                    
                    # Get user profile to get user_id
                    self.get_user_profile()
                    return True
                else:
                    logger.error(f"Login failed: {response.status_code} - {response.text}")
                    response.failure(f"Login failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Login exception: {str(e)}")
            return False
    
    def refresh_token_if_needed(self):
        """
        Check if token needs refreshing and refresh if necessary.
        """
        if not self.token:
            return self.login()
            
        current_time = datetime.now().timestamp()
        token_age = current_time - self.last_token_refresh
        
        if token_age > CONFIG["auth"]["token_refresh_interval"]:
            logger.info(f"Token age {token_age} seconds exceeds refresh interval, refreshing token")
            
            try:
                with self.client.post(
                    f"{API_V1_STR}/login/refresh-token",
                    headers={"Authorization": f"Bearer {self.token}"},
                    name="Refresh Token",
                    catch_response=True
                ) as response:
                    if response.status_code == 200:
                        data = response.json()
                        self.token = data.get('access_token')
                        self.last_token_refresh = current_time
                        logger.info(f"Token refreshed successfully for {self.username}")
                        response.success()
                        return True
                    else:
                        logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
                        response.failure(f"Token refresh failed: {response.status_code}")
                        return self.login()
            except Exception as e:
                logger.error(f"Token refresh exception: {str(e)}")
                return self.login()
        
        return True
    
    def get_user_profile(self):
        """
        Get user profile to retrieve user_id.
        """
        if not self.token:
            return False
            
        try:
            with self.client.get(
                f"{API_V1_STR}/users/me",
                headers={"Authorization": f"Bearer {self.token}"},
                name="Get Profile",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    self.user_id = data.get('id')
                    logger.info(f"Retrieved user profile for {self.username}, user_id: {self.user_id}")
                    response.success()
                    return True
                else:
                    logger.error(f"Get profile failed: {response.status_code} - {response.text}")
                    response.failure(f"Get profile failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Get profile exception: {str(e)}")
            return False
    
    @task(5)
    def view_events(self):
        """
        View events list.
        Higher weight (5) as this is a common operation.
        """
        if not self.refresh_token_if_needed():
            return
            
        with self.client.get(
            f"{API_V1_STR}/events",
            headers={"Authorization": f"Bearer {self.token}"},
            name="View Events",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Handle both list and dictionary response formats
                    if isinstance(data, dict) and 'items' in data:
                        events = data.get('items', [])
                    else:
                        events = data if isinstance(data, list) else []
                    
                    self.events_cache = events
                    events_count = len(events)
                    logger.info(f"Viewed {events_count} events")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing events: {str(e)}")
                    response.failure(f"Error processing events: {str(e)}")
            else:
                logger.error(f"View events failed: {response.status_code} - {response.text}")
                response.failure(f"View events failed: {response.status_code}")
    
    @task(3)
    def view_user_profile(self):
        """
        View user profile.
        Medium weight (3) as users check their profile regularly.
        """
        if not self.refresh_token_if_needed():
            return
            
        with self.client.get(
            f"{API_V1_STR}/users/me",
            headers={"Authorization": f"Bearer {self.token}"},
            name="View User Profile",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info(f"Viewed profile for {self.username}")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing profile: {str(e)}")
                    response.failure(f"Error processing profile: {str(e)}")
            else:
                logger.error(f"View profile failed: {response.status_code} - {response.text}")
                response.failure(f"View profile failed: {response.status_code}")
    
    @task(2)
    def view_user_badges(self):
        """
        View user badges.
        Lower weight (2) as this is checked less frequently.
        """
        if not self.refresh_token_if_needed() or not self.user_id:
            return
            
        with self.client.get(
            f"{API_V1_STR}/users/{self.user_id}/badges",
            headers={"Authorization": f"Bearer {self.token}"},
            name="View User Badges",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Handle both list and dictionary response formats
                    if isinstance(data, dict) and 'items' in data:
                        badges = data.get('items', [])
                    else:
                        badges = data if isinstance(data, list) else []
                    
                    badges_count = len(badges)
                    logger.info(f"Viewed {badges_count} badges for {self.username}")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing badges: {str(e)}")
                    response.failure(f"Error processing badges: {str(e)}")
            else:
                logger.error(f"View badges failed: {response.status_code} - {response.text}")
                response.failure(f"View badges failed: {response.status_code}")
    
    @task(2)
    def view_user_events(self):
        """
        View user events.
        Lower weight (2) as this is checked less frequently.
        """
        if not self.refresh_token_if_needed() or not self.user_id:
            return
            
        with self.client.get(
            f"{API_V1_STR}/users/{self.user_id}/events",
            headers={"Authorization": f"Bearer {self.token}"},
            name="View User Events",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Handle both list and dictionary response formats
                    if isinstance(data, dict) and 'items' in data:
                        events = data.get('items', [])
                    else:
                        events = data if isinstance(data, list) else []
                    
                    events_count = len(events)
                    logger.info(f"Viewed {events_count} events for {self.username}")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing user events: {str(e)}")
                    response.failure(f"Error processing user events: {str(e)}")
            else:
                logger.error(f"View user events failed: {response.status_code} - {response.text}")
                response.failure(f"View user events failed: {response.status_code}")
    
    @task(1)
    def view_leaderboard(self):
        """
        View points leaderboard.
        Lowest weight (1) as this is checked least frequently.
        """
        if not self.refresh_token_if_needed():
            return
            
        with self.client.get(
            f"{API_V1_STR}/points/leaderboard",
            headers={"Authorization": f"Bearer {self.token}"},
            name="View Leaderboard",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Handle both list and dictionary response formats
                    if isinstance(data, dict) and 'items' in data:
                        users = data.get('items', [])
                    else:
                        users = data if isinstance(data, list) else []
                    
                    users_count = len(users)
                    logger.info(f"Viewed leaderboard with {users_count} users")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing leaderboard: {str(e)}")
                    response.failure(f"Error processing leaderboard: {str(e)}")
            else:
                logger.error(f"View leaderboard failed: {response.status_code} - {response.text}")
                response.failure(f"View leaderboard failed: {response.status_code}")
    
    @task(1)
    def register_for_event(self):
        """
        Register for an event.
        Lowest weight (1) as this is done infrequently.
        """
        if not self.refresh_token_if_needed():
            return
            
        # If we don't have events cached, get them first
        if not self.events_cache:
            self.view_events()
            if not self.events_cache:
                logger.warning("No events available for registration")
                return
        
        # Filter for upcoming events
        upcoming_events = []
        for event in self.events_cache:
            start_time = event.get('start_time')
            if start_time:
                try:
                    # Handle different date formats
                    if 'T' in start_time:
                        event_date = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    else:
                        event_date = datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
                    
                    if event_date > datetime.now():
                        upcoming_events.append(event)
                except (ValueError, TypeError) as e:
                    logger.warning(f"Could not parse date {start_time}: {e}")
        
        if not upcoming_events:
            logger.warning("No upcoming events available for registration")
            return
        
        # Select a random event
        event = random.choice(upcoming_events)
        event_id = event.get('id')
        
        if not event_id:
            logger.warning("Selected event has no ID")
            return
        
        # Register for event
        with self.client.post(
            f"{API_V1_STR}/events/{event_id}/register",
            headers={"Authorization": f"Bearer {self.token}"},
            name="Register for Event",
            catch_response=True
        ) as response:
            if response.status_code in (200, 201):
                logger.info(f"Registered for event {event_id}")
                response.success()
            elif response.status_code == 400 and "already registered" in response.text.lower():
                logger.info(f"Already registered for event {event_id}")
                response.success()
            else:
                logger.error(f"Event registration failed: {response.status_code} - {response.text}")
                response.failure(f"Event registration failed: {response.status_code}")

class PineTimeAdminUser(HttpUser):
    """
    Simulated admin user for load testing the Pine Time API.
    """
    
    wait_time = between(3, 10)  # Admins perform fewer operations but they're more intensive
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.token = None
        self.username = "admin"
        self.password = "admin123"
        self.last_token_refresh = 0
    
    def on_start(self):
        """
        Called when a user starts.
        Login as admin and store the token.
        """
        logger.info(f"Starting admin user simulation for {self.username}")
        self.login()
    
    def login(self):
        """
        Attempt to login with the admin user.
        """
        try:
            with self.client.post(
                f"{API_V1_STR}/login/access-token",
                data={
                    "username": self.username,
                    "password": self.password
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                name="Admin Login",
                catch_response=True
            ) as response:
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get('access_token')
                    self.last_token_refresh = datetime.now().timestamp()
                    logger.info(f"Admin user {self.username} logged in successfully")
                    response.success()
                    return True
                else:
                    logger.error(f"Admin login failed: {response.status_code} - {response.text}")
                    response.failure(f"Admin login failed: {response.status_code}")
                    return False
        except Exception as e:
            logger.error(f"Admin login exception: {str(e)}")
            return False
    
    def refresh_token_if_needed(self):
        """
        Check if token needs refreshing and refresh if necessary.
        """
        if not self.token:
            return self.login()
            
        current_time = datetime.now().timestamp()
        token_age = current_time - self.last_token_refresh
        
        if token_age > CONFIG["auth"]["token_refresh_interval"]:
            logger.info(f"Admin token age {token_age} seconds exceeds refresh interval, refreshing token")
            
            try:
                with self.client.post(
                    f"{API_V1_STR}/login/refresh-token",
                    headers={"Authorization": f"Bearer {self.token}"},
                    name="Admin Refresh Token",
                    catch_response=True
                ) as response:
                    if response.status_code == 200:
                        data = response.json()
                        self.token = data.get('access_token')
                        self.last_token_refresh = current_time
                        logger.info(f"Admin token refreshed successfully")
                        response.success()
                        return True
                    else:
                        logger.error(f"Admin token refresh failed: {response.status_code} - {response.text}")
                        response.failure(f"Admin token refresh failed: {response.status_code}")
                        return self.login()
            except Exception as e:
                logger.error(f"Admin token refresh exception: {str(e)}")
                return self.login()
        
        return True
    
    @task(3)
    def view_all_users(self):
        """
        View all users.
        Higher weight (3) as admins check user lists regularly.
        """
        if not self.refresh_token_if_needed():
            return
            
        with self.client.get(
            f"{API_V1_STR}/users",
            headers={"Authorization": f"Bearer {self.token}"},
            name="Admin View Users",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    
                    # Handle both list and dictionary response formats
                    if isinstance(data, dict) and 'items' in data:
                        users = data.get('items', [])
                    else:
                        users = data if isinstance(data, list) else []
                    
                    users_count = len(users)
                    logger.info(f"Admin viewed {users_count} users")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing users: {str(e)}")
                    response.failure(f"Error processing users: {str(e)}")
            else:
                logger.error(f"Admin view users failed: {response.status_code} - {response.text}")
                response.failure(f"Admin view users failed: {response.status_code}")
    
    @task(2)
    def view_event_analytics(self):
        """
        View event analytics.
        Medium weight (2) as admins check analytics regularly.
        """
        if not self.refresh_token_if_needed():
            return
            
        with self.client.get(
            f"{API_V1_STR}/analytics/events/popularity",
            headers={"Authorization": f"Bearer {self.token}"},
            name="Admin View Event Analytics",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info("Admin viewed event analytics")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing event analytics: {str(e)}")
                    response.failure(f"Error processing event analytics: {str(e)}")
            else:
                logger.error(f"Admin view event analytics failed: {response.status_code} - {response.text}")
                response.failure(f"Admin view event analytics failed: {response.status_code}")
    
    @task(2)
    def view_user_analytics(self):
        """
        View user analytics.
        Medium weight (2) as admins check analytics regularly.
        """
        if not self.refresh_token_if_needed():
            return
            
        with self.client.get(
            f"{API_V1_STR}/analytics/users/engagement",
            headers={"Authorization": f"Bearer {self.token}"},
            name="Admin View User Analytics",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    logger.info("Admin viewed user analytics")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing user analytics: {str(e)}")
                    response.failure(f"Error processing user analytics: {str(e)}")
            else:
                logger.error(f"Admin view user analytics failed: {response.status_code} - {response.text}")
                response.failure(f"Admin view user analytics failed: {response.status_code}")
    
    @task(1)
    def create_event(self):
        """
        Create a new event.
        Lowest weight (1) as this is done infrequently.
        """
        if not self.refresh_token_if_needed():
            return
            
        # Generate random event data
        event_name = f"Test Event {random.randint(1000, 9999)}"
        start_date = datetime.now() + timedelta(days=random.randint(1, 30))
        end_date = start_date + timedelta(hours=random.randint(1, 8))
        
        event_data = {
            "name": event_name,
            "description": f"Description for {event_name}",
            "location": "Test Location",
            "start_time": start_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_date.strftime("%Y-%m-%d %H:%M:%S"),
            "max_capacity": random.randint(10, 100),
            "points": random.randint(5, 20)
        }
        
        with self.client.post(
            f"{API_V1_STR}/events",
            json=event_data,
            headers={"Authorization": f"Bearer {self.token}"},
            name="Admin Create Event",
            catch_response=True
        ) as response:
            if response.status_code in (200, 201):
                logger.info(f"Admin created event: {event_name}")
                response.success()
            else:
                logger.error(f"Admin create event failed: {response.status_code} - {response.text}")
                response.failure(f"Admin create event failed: {response.status_code}")

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """
    Called when Locust is initialized.
    """
    logger.info("Locust initialized")
    logger.info(f"API base URL: {API_BASE_URL}")
    logger.info(f"User configuration: {CONFIG['users']}")
    logger.info(f"Auth configuration: {CONFIG['auth']}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Called when the test is started.
    """
    logger.info("Load test starting")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Called when the test is stopped.
    """
    logger.info("Load test complete")
    
    # Calculate statistics
    stats = environment.stats
    
    # Total requests
    total_requests = stats.total.num_requests
    # Success rate
    success_rate = 0 if total_requests == 0 else (total_requests - stats.total.num_failures) / total_requests * 100
    # Average response time
    avg_response_time = stats.total.avg_response_time
    
    logger.info(f"Total requests: {total_requests}")
    logger.info(f"Success rate: {success_rate:.2f}%")
    logger.info(f"Average response time: {avg_response_time:.2f} ms")
    
    # Log detailed stats for each endpoint
    logger.info("Endpoint statistics:")
    for name, stat in stats.entries.items():
        logger.info(f"  {name}:")
        logger.info(f"    Requests: {stat.num_requests}")
        logger.info(f"    Failures: {stat.num_failures}")
        logger.info(f"    Median response time: {stat.median_response_time} ms")
        logger.info(f"    95th percentile: {stat.get_response_time_percentile(0.95)} ms")

if __name__ == "__main__":
    # This script is meant to be run with the Locust command-line interface
    logger.info("Pine Time API load test script loaded")
