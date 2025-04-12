"""
Load testing script for Pine Time API endpoints.
Uses locust to simulate multiple users accessing the API simultaneously.
"""

import os
import sys
import json
import logging
import time
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from locust import HttpUser, task, between, events
from dotenv import load_dotenv

# Configure retry strategy for requests
def get_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    """Create a requests session with retry capabilities"""
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("load_test.log")
    ]
)
logger = logging.getLogger("load_test")

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1_STR = "/api/v1"

# Test configuration
CONFIG = {
    "users": {
        "min_wait": int(os.getenv("LOAD_TEST_MIN_WAIT", "1")),  # Minimum wait time between tasks (seconds)
        "max_wait": int(os.getenv("LOAD_TEST_MAX_WAIT", "5")),  # Maximum wait time between tasks (seconds)
        "count": int(os.getenv("LOAD_TEST_USER_COUNT", "10")),  # Number of users to simulate
        "spawn_rate": int(os.getenv("LOAD_TEST_SPAWN_RATE", "2")),  # Users per second to spawn
    },
    "auth": {
        "token_refresh_interval": int(os.getenv("TOKEN_REFRESH_INTERVAL", "1800")),  # Refresh token every 30 minutes
        "retry_attempts": int(os.getenv("AUTH_RETRY_ATTEMPTS", "3")),  # Number of login retry attempts
        "retry_delay": int(os.getenv("AUTH_RETRY_DELAY", "2")),  # Delay between retries (seconds)
    }
}

# Test user credentials
TEST_USERS = [
    {"username": "loadtest1", "password": "testpassword", "token": None, "refresh_token": None, "token_expiry": 0},
    {"username": "loadtest2", "password": "testpassword", "token": None, "refresh_token": None, "token_expiry": 0},
    {"username": "loadtest3", "password": "testpassword", "token": None, "refresh_token": None, "token_expiry": 0},
    {"username": "loadtest4", "password": "testpassword", "token": None, "refresh_token": None, "token_expiry": 0},
    {"username": "loadtest5", "password": "testpassword", "token": None, "refresh_token": None, "token_expiry": 0},
    {"username": "loadtest6", "password": "testpassword", "token": None, "refresh_token": None, "token_expiry": 0},
    {"username": "loadtest7", "password": "testpassword", "token": None, "refresh_token": None, "token_expiry": 0},
    {"username": "loadtest8", "password": "testpassword", "token": None, "refresh_token": None, "token_expiry": 0},
    {"username": "loadtest9", "password": "testpassword", "token": None, "refresh_token": None, "token_expiry": 0},
    {"username": "loadtest10", "password": "testpassword", "token": None, "refresh_token": None, "token_expiry": 0},
]

# Test admin credentials
ADMIN_USER = {"username": "admin", "password": "adminpassword", "token": None, "refresh_token": None, "token_expiry": 0}

class PineTimeUser(HttpUser):
    """
    Simulated user for load testing the Pine Time API with enhanced authentication.
    Implements token refresh and proper error handling.
    """
    
    wait_time = between(CONFIG["users"]["min_wait"], CONFIG["users"]["max_wait"])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_header = {}
        self.login_attempts = 0
        self.last_token_refresh = 0
        self.user_id = None
        self.username = f"testuser{random.randint(1, 5)}"
        self.password = "password123"
    
    def on_start(self):
        """
        Called when a user starts.
        Login and store the token with retry logic.
        """
        # Select a random test user that's not already in use
        available_users = [user for user in TEST_USERS if user["token"] is None]
        if not available_users:
            # If all users are in use, select a random one anyway
            self.user = random.choice(TEST_USERS)
            logger.warning(f"All test users are in use, reusing {self.user['username']}")
        else:
            self.user = random.choice(available_users)
        
        # Try to login with retry logic
        self.login_with_retry()
    
    def login_with_retry(self):
        """
        Attempt to login with retry logic.
        """
        retry_count = 0
        max_retries = CONFIG["auth"]["retry_attempts"]
        retry_delay = CONFIG["auth"]["retry_delay"]
        
        while retry_count < max_retries:
            try:
                # Attempt login
                with self.client.post(
                    f"{API_BASE_URL}/auth/token",
                    json={
                        "username": self.username,
                        "password": self.password
                    },
                    name="/auth/token",  # Name for Locust statistics
                    catch_response=True
                ) as response:
                    if response.status_code == 200:
                        data = response.json()
                        token = data.get('access_token')
                        if token:
                            self.auth_header = {"Authorization": f"Bearer {token}"}
                            self.last_token_refresh = datetime.now().timestamp()
                            self.login_attempts = 0
                            
                            # Try to get user ID
                            try:
                                if 'user_id' in data:
                                    self.user_id = data['user_id']
                                    logger.info(f"User {self.username} logged in successfully with ID {self.user_id}")
                                else:
                                    # Fetch user profile to get ID
                                    self.get_user_profile()
                            except Exception as e:
                                logger.warning(f"Could not get user ID: {e}")
                                
                            return True
                        else:
                            response.failure(f"Login succeeded but no token in response: {response.text}")
                    else:
                        response.failure(f"Login failed with status code {response.status_code}: {response.text}")
                        logger.warning(f"Login attempt {retry_count + 1} failed: {response.text}")
            except Exception as e:
                logger.error(f"Login attempt {retry_count + 1} failed with exception: {e}")
            
            # Increment retry count and wait before retrying
            retry_count += 1
            if retry_count < max_retries:
                # Use exponential backoff with jitter
                delay = retry_delay * (2 ** (retry_count - 1)) * (0.5 + random.random())
                time.sleep(delay)
        
        # All retries failed
        self.login_attempts += 1
        logger.error(f"Login failed after {max_retries} attempts for user {self.username}")
        return False
    
    def refresh_token_if_needed(self):
        """
        Check if token needs refreshing and refresh if necessary.
        """
        # Check if token needs refreshing
        current_time = datetime.now().timestamp()
        token_age = current_time - self.last_token_refresh
        
        if token_age > CONFIG["auth"]["token_refresh_interval"]:
            logger.info(f"Token age {token_age} seconds exceeds refresh interval, refreshing token for {self.username}")
            
            try:
                # Refresh token
                with self.client.post(
                    f"{API_BASE_URL}/auth/refresh",
                    headers=self.auth_header,
                    name="/auth/refresh",  # Name for Locust statistics
                    catch_response=True
                ) as response:
                    if response.status_code == 200:
                        data = response.json()
                        token = data.get('access_token')
                        if token:
                            self.auth_header = {"Authorization": f"Bearer {token}"}
                            self.last_token_refresh = current_time
                            logger.info(f"Token refreshed successfully for {self.username}")
                            return True
                        else:
                            response.failure(f"Token refresh succeeded but no token in response: {response.text}")
                            # Try to login again
                            return self.login_with_retry()
                    else:
                        response.failure(f"Token refresh failed with status code {response.status_code}: {response.text}")
                        logger.warning(f"Token refresh failed for {self.username}: {response.text}")
                        
                        # Try to login again
                        return self.login_with_retry()
            except Exception as e:
                logger.error(f"Token refresh failed with exception for {self.username}: {e}")
                # Try to login again
                return self.login_with_retry()
        
        return True
    
    def on_stop(self):
        """
        Called when a user stops.
        Clear the token to make the user available for reuse.
        """
        if hasattr(self, 'user'):
            self.user["token"] = None
            self.user["refresh_token"] = None
            self.user["token_expiry"] = 0
            logger.info(f"User {self.user['username']} stopped and released")
    
    @task(5)
    def get_events(self):
        """
        Get list of events.
        Higher weight (5) as this is a common operation.
        """
        # Ensure token is valid
        if not self.refresh_token_if_needed():
            return
        
        with self.client.get(
            f"{API_BASE_URL}/events",
            headers=self.auth_header,
            name="/events",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # Successfully got events
                data = response.json()
                
                # Handle both list and dictionary response formats
                if isinstance(data, dict) and 'items' in data:
                    events = data.get('items', [])
                else:
                    events = data if isinstance(data, list) else []
                
                events_count = len(events)
                response.success()
                logger.debug(f"Got {events_count} events")
            else:
                error_msg = f"Failed to get events: {response.status_code} {response.text}"
                logger.error(error_msg)
                response.failure(error_msg)
    
    @task(3)
    def get_user_profile(self):
        """
        Get user profile.
        Medium weight (3) as users check their profile regularly.
        """
        # Refresh token if needed
        if not self.refresh_token_if_needed():
            return
        
        with self.client.get(
            f"{API_V1_STR}/users/me",
            headers=self.auth_header,
            catch_response=True,
            name="/users/me"
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                # Unauthorized - try to refresh token and retry
                response.failure("Unauthorized - token may be expired")
                if self.login_with_retry():
                    # Retry the request with new token
                    self.get_user_profile()
            else:
                response.failure(f"Failed to get user profile: {response.status_code}")
    
    @task(2)
    def get_user_badges(self):
        """
        Get user badges.
        Lower weight (2) as this is checked less frequently.
        """
        self.client.get(
            f"{API_V1_STR}/users/me/badges",
            headers=self.auth_header,
            name="/users/me/badges"
        )
    
    @task(2)
    def get_user_events(self):
        """
        Get user events.
        Lower weight (2) as this is checked less frequently.
        """
        self.client.get(
            f"{API_V1_STR}/users/me/events",
            headers=self.auth_header,
            name="/users/me/events"
        )
    
    @task(1)
    def get_leaderboard(self):
        """
        Get leaderboard.
        Lowest weight (1) as this is checked least frequently.
        """
        self.client.get(
            f"{API_V1_STR}/points/leaderboard",
            headers=self.auth_header,
            name="/points/leaderboard"
        )
    
    @task(1)
    def register_for_random_event(self):
        """
        Register for a random event.
        Lowest weight (1) as this is done infrequently.
        """
        # Refresh token if needed
        if not self.refresh_token_if_needed():
            return
        
        # First get list of events
        with self.client.get(
            f"{API_V1_STR}/events",
            headers=self.auth_header,
            catch_response=True,
            name="/events (for registration)"
        ) as events_response:
            if events_response.status_code != 200:
                events_response.failure(f"Failed to get events: {events_response.text}")
                return
            
            try:
                events_data = events_response.json()
                events_response.success()
            except Exception as e:
                events_response.failure(f"Error parsing events response: {str(e)}")
                return
        
        # Handle both list and paginated responses
        if isinstance(events_data, dict) and "items" in events_data:
            events = events_data["items"]
        else:
            events = events_data
        
        # Filter for future events
        future_events = []
        now = datetime.now().isoformat()
        
        for event in events:
            if "start_time" in event and event["start_time"] > now:
                future_events.append(event)
        
        if not future_events:
            logger.warning("No future events available for registration")
            return
        
        # Select a random event
        random_event = random.choice(future_events)
        
        # Register for the event
        with self.client.post(
            f"{API_V1_STR}/events/{random_event['id']}/register",
            headers=self.auth_header,
            catch_response=True,
            name="/events/{id}/register"
        ) as response:
            if response.status_code == 200 or response.status_code == 201:
                response.success()
                logger.info(f"Successfully registered for event {random_event['id']}")
            elif response.status_code == 409:
                # Already registered - this is expected sometimes
                response.success()
                logger.info(f"Already registered for event {random_event['id']}")
            elif response.status_code == 401:
                # Unauthorized - try to refresh token and retry
                response.failure("Unauthorized - token may be expired")
                if self.login_with_retry():
                    # Retry the request with new token
                    self.register_for_random_event()
            else:
                response.failure(f"Failed to register for event: {response.status_code} - {response.text}")

class PineTimeAdminUser(HttpUser):
    """
    Simulated admin user for load testing the Pine Time API.
    """
    
    wait_time = between(2, 8)  # Wait between 2 and 8 seconds between tasks
    
    def on_start(self):
        """
        Called when a user starts.
        Login as admin and store the token.
        """
        # Login as admin
        response = self.client.post(
            f"{API_V1_STR}/login/access-token",
            data={"username": ADMIN_USER["username"], "password": ADMIN_USER["password"]},
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            result = response.json()
            ADMIN_USER["token"] = result["access_token"]
            self.auth_header = {"Authorization": f"Bearer {ADMIN_USER['token']}"}
            logger.info(f"Admin user logged in successfully")
        else:
            logger.error(f"Failed to login as admin: {response.text}")
            self.auth_header = {}
    
    @task(3)
    def get_all_users(self):
        """
        Get list of all users.
        Higher weight (3) as admins check user lists regularly.
        """
        self.client.get(
            f"{API_V1_STR}/users",
            headers=self.auth_header,
            name="/users (admin)"
        )
    
    @task(2)
    def get_event_analytics(self):
        """
        Get event analytics.
        Medium weight (2) as admins check analytics regularly.
        """
        self.client.get(
            f"{API_V1_STR}/analytics/events/popularity",
            headers=self.auth_header,
            name="/analytics/events/popularity"
        )
    
    @task(2)
    def get_user_analytics(self):
        """
        Get user analytics.
        Medium weight (2) as admins check analytics regularly.
        """
        self.client.get(
            f"{API_V1_STR}/analytics/users/engagement",
            headers=self.auth_header,
            name="/analytics/users/engagement"
        )
    
    @task(1)
    def create_event(self):
        """
        Create a new event.
        Lowest weight (1) as this is done infrequently.
        """
        # Generate random event data
        start_time = datetime.now() + timedelta(days=random.randint(1, 30))
        end_time = start_time + timedelta(hours=random.randint(1, 4))
        
        event_types = ["workshop", "social", "trivia", "game_night", "networking"]
        locations = ["Main Hall", "Conference Room A", "Conference Room B", "Outdoor Pavilion", "Virtual"]
        
        event_data = {
            "title": f"Load Test Event {datetime.now().strftime('%Y%m%d%H%M%S')}",
            "description": "This is a test event created by the load testing script",
            "event_type": random.choice(event_types),
            "location": random.choice(locations),
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "max_participants": random.randint(10, 50),
            "points_reward": random.randint(5, 20)
        }
        
        self.client.post(
            f"{API_V1_STR}/events",
            json=event_data,
            headers=self.auth_header,
            name="/events (create)"
        )

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """
    Called when Locust is initialized.
    """
    logger.info("Locust initialized")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Called when the test is started.
    """
    logger.info("Load test started")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Called when the test is stopped.
    """
    logger.info("Load test stopped")
    
    # Log statistics
    stats = environment.stats
    
    # Calculate total requests
    total_requests = 0
    total_failures = 0
    
    for name, stat in stats.entries.items():
        total_requests += stat.num_requests
        total_failures += stat.num_failures
    
    logger.info(f"Total requests: {total_requests}")
    logger.info(f"Total failures: {total_failures}")
    logger.info(f"Failure percentage: {(total_failures / total_requests) * 100 if total_requests > 0 else 0:.2f}%")
    
    # Log response times
    if environment.stats.total.avg_response_time:
        logger.info(f"Average response time: {environment.stats.total.avg_response_time:.2f}ms")
    if environment.stats.total.min_response_time:
        logger.info(f"Min response time: {environment.stats.total.min_response_time}ms")
    if environment.stats.total.max_response_time:
        logger.info(f"Max response time: {environment.stats.total.max_response_time}ms")
    if environment.stats.total.median_response_time:
        logger.info(f"Median response time: {environment.stats.total.median_response_time}ms")
    if environment.stats.total.percentile(0.95):
        logger.info(f"95th percentile response time: {environment.stats.total.percentile(0.95)}ms")

# Helper function to create test users if they don't exist
def create_test_users(client):
    """
    Create test users if they don't exist.
    
    Args:
        client: A requests.Session object for making API calls
        
    Returns:
        bool: True if users were created or already exist, False on error
    """
    try:
        # Check if API is available first
        try:
            health_check = client.get(f"{API_BASE_URL}/health", timeout=5)
            if health_check.status_code != 200:
                logger.warning(f"API health check failed with status {health_check.status_code}")
                logger.warning("Skipping test user creation as API may not be available")
                return False
        except Exception as e:
            logger.warning(f"API health check failed: {e}")
            logger.warning("Skipping test user creation as API may not be available")
            return False
            
        # Create regular test users
        for i in range(1, 6):
            username = f"testuser{i}"
            password = "password123"
            email = f"testuser{i}@example.com"
            
            # Check if user exists
            try:
                response = client.get(
                    f"{API_BASE_URL}/users?username={username}",
                    timeout=10
                )
                
                if response.status_code == 200 and response.json():
                    logger.info(f"User {username} already exists")
                    continue
            except Exception as e:
                logger.warning(f"Error checking if user {username} exists: {e}")
                continue
                
            # Create user
            user_data = {
                "username": username,
                "password": password,
                "email": email,
                "full_name": f"Test User {i}"
            }
            
            try:
                response = client.post(
                    f"{API_BASE_URL}/users",
                    json=user_data,
                    timeout=10
                )
                
                if response.status_code == 201:
                    logger.info(f"Created test user: {username}")
                else:
                    logger.warning(f"Failed to create test user {username}: {response.text}")
            except Exception as e:
                logger.warning(f"Error creating test user {username}: {e}")
        
        # Create admin test user
        admin_username = "testadmin"
        admin_password = "adminpass123"
        admin_email = "testadmin@example.com"
        
        # Check if admin user exists
        try:
            response = client.get(
                f"{API_BASE_URL}/users?username={admin_username}",
                timeout=10
            )
            
            if response.status_code != 200 or not response.json():
                # Create admin user
                admin_data = {
                    "username": admin_username,
                    "password": admin_password,
                    "email": admin_email,
                    "full_name": "Test Admin",
                    "is_admin": True
                }
                
                response = client.post(
                    f"{API_BASE_URL}/users",
                    json=admin_data,
                    timeout=10
                )
                
                if response.status_code == 201:
                    logger.info(f"Created admin test user: {admin_username}")
                else:
                    logger.warning(f"Failed to create admin test user: {response.text}")
            else:
                logger.info(f"Admin user {admin_username} already exists")
        except Exception as e:
            logger.warning(f"Error creating admin test user: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Error creating test users: {e}")
        return False

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """
    Called when Locust is initialized.
    Create test users if they don't exist.
    """
    logger.info("Locust initialized")
    logger.info("Initializing load test environment")
    
    logger.info(f"API base URL: {API_BASE_URL}")
    logger.info(f"User configuration: {CONFIG['users']}")
    logger.info(f"Auth configuration: {CONFIG['auth']}")
    
    # Create a client for setup operations
    import requests
    session = requests.Session()
    client = requests.Session()
    
    # Create test users
    try:
        if create_test_users(client):
            logger.info("Test users setup completed successfully")
        else:
            logger.warning("Failed to set up test users, but continuing with test")
    except Exception as e:
        logger.error(f"Error setting up test users: {e}")
        logger.warning("Continuing with test despite setup error")

if __name__ == "__main__":
    # This script is meant to be run with the Locust command-line interface
    logger.info("Load test script loaded")
    logger.info(f"API base URL: {API_BASE_URL}")
    logger.info(f"API version: {API_V1_STR}")
    logger.info(f"Test users: {len(TEST_USERS)}")