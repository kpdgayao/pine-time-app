"""
Pine Time Application - Load Testing Script
Uses Locust to simulate user load on the API endpoints with proper error handling
and PostgreSQL connection verification.
"""

import os
import sys
import json
import logging
import time
import random
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
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
        logging.FileHandler("pine_time_load_test.log")
    ]
)
logger = logging.getLogger("pine_time_load_test")

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

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
    },
    "db": {
        "check_connection": os.getenv("LOAD_TEST_CHECK_DB", "True").lower() == "true",
        "connection_timeout": int(os.getenv("DB_CONNECTION_TIMEOUT", "5")),
    }
}

def get_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    """
    Create a requests session with retry capabilities
    
    Args:
        retries: Number of retries
        backoff_factor: Backoff factor for retries
        status_forcelist: Status codes to retry on
        session: Existing session to configure
        
    Returns:
        requests.Session: Configured session with retry capabilities
    """
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
        self.events_cache = []
    
    def on_start(self):
        """
        Called when a user starts.
        Login and store the token with retry logic.
        """
        logger.info(f"Starting user simulation for {self.username}")
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
                    name="/auth/token",
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
                            if 'user_id' in data:
                                self.user_id = data['user_id']
                                logger.info(f"User {self.username} logged in successfully with ID {self.user_id}")
                            else:
                                logger.info(f"User {self.username} logged in successfully but no user_id in response")
                            
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
                    name="/auth/refresh",
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
        logger.info(f"Stopping user simulation for {self.username}")
        self.auth_header = {}
    
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
                
                # Cache events for other operations
                self.events_cache = events
                
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
        # Ensure token is valid
        if not self.refresh_token_if_needed():
            return
        
        # Get user profile
        with self.client.get(
            f"{API_BASE_URL}/users/profile",
            headers=self.auth_header,
            name="/users/profile",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # Successfully got profile
                profile = response.json()
                
                # If we didn't have user_id before, get it from profile
                if not self.user_id and 'id' in profile:
                    self.user_id = profile['id']
                
                response.success()
                logger.debug(f"Got profile for user {self.username}")
            else:
                error_msg = f"Failed to get profile: {response.status_code} {response.text}"
                logger.error(error_msg)
                response.failure(error_msg)
    
    @task(2)
    def get_user_badges(self):
        """
        Get user badges.
        Lower weight (2) as this is checked less frequently.
        """
        # Ensure token is valid
        if not self.refresh_token_if_needed():
            return
        
        # Get user badges
        with self.client.get(
            f"{API_BASE_URL}/badges/user",
            headers=self.auth_header,
            name="/badges/user",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # Successfully got badges
                data = response.json()
                
                # Handle both list and dictionary response formats
                if isinstance(data, dict) and 'items' in data:
                    badges = data.get('items', [])
                else:
                    badges = data if isinstance(data, list) else []
                
                badges_count = len(badges)
                response.success()
                logger.debug(f"Got {badges_count} badges for user {self.username}")
            else:
                error_msg = f"Failed to get badges: {response.status_code} {response.text}"
                logger.error(error_msg)
                response.failure(error_msg)
    
    @task(2)
    def get_user_events(self):
        """
        Get user events.
        Lower weight (2) as this is checked less frequently.
        """
        # Ensure token is valid
        if not self.refresh_token_if_needed():
            return
        
        # Get user events
        with self.client.get(
            f"{API_BASE_URL}/events/user",
            headers=self.auth_header,
            name="/events/user",
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
                logger.debug(f"Got {events_count} events for user {self.username}")
            else:
                error_msg = f"Failed to get user events: {response.status_code} {response.text}"
                logger.error(error_msg)
                response.failure(error_msg)
    
    @task(1)
    def get_leaderboard(self):
        """
        Get leaderboard.
        Lowest weight (1) as this is checked least frequently.
        """
        # Ensure token is valid
        if not self.refresh_token_if_needed():
            return
        
        # Get leaderboard
        with self.client.get(
            f"{API_BASE_URL}/points/leaderboard",
            headers=self.auth_header,
            name="/points/leaderboard",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # Successfully got leaderboard
                data = response.json()
                
                # Handle both list and dictionary response formats
                if isinstance(data, dict) and 'items' in data:
                    users = data.get('items', [])
                else:
                    users = data if isinstance(data, list) else []
                
                users_count = len(users)
                response.success()
                logger.debug(f"Got leaderboard with {users_count} users")
            else:
                error_msg = f"Failed to get leaderboard: {response.status_code} {response.text}"
                logger.error(error_msg)
                response.failure(error_msg)
    
    @task(1)
    def register_for_random_event(self):
        """
        Register for a random event.
        Lowest weight (1) as this is done infrequently.
        """
        # Ensure token is valid
        if not self.refresh_token_if_needed():
            return
        
        # If we don't have events cached, get them first
        if not self.events_cache:
            self.get_events()
            if not self.events_cache:
                logger.warning("No events available for registration")
                return
        
        # Filter for upcoming events
        upcoming_events = [
            event for event in self.events_cache 
            if event.get('start_time') and datetime.fromisoformat(event['start_time'].replace('Z', '+00:00')) > datetime.now()
        ]
        
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
            f"{API_BASE_URL}/registrations",
            json={"event_id": event_id},
            headers=self.auth_header,
            name="/registrations",
            catch_response=True
        ) as response:
            if response.status_code in (200, 201):
                # Successfully registered
                response.success()
                logger.info(f"Registered for event {event_id}")
            elif response.status_code == 400 and "already registered" in response.text.lower():
                # Already registered - this is expected sometimes
                response.success()
                logger.info(f"Already registered for event {event_id}")
            else:
                error_msg = f"Failed to register for event {event_id}: {response.status_code} {response.text}"
                logger.error(error_msg)
                response.failure(error_msg)

class PineTimeAdminUser(HttpUser):
    """
    Simulated admin user for load testing the Pine Time API.
    """
    
    wait_time = between(3, 10)  # Admins perform fewer operations but they're more intensive
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_header = {}
        self.last_token_refresh = 0
        self.username = "testadmin"
        self.password = "adminpass123"
    
    def on_start(self):
        """
        Called when a user starts.
        Login as admin and store the token.
        """
        logger.info(f"Starting admin user simulation for {self.username}")
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
                    name="/auth/token (admin)",
                    catch_response=True
                ) as response:
                    if response.status_code == 200:
                        data = response.json()
                        token = data.get('access_token')
                        if token:
                            self.auth_header = {"Authorization": f"Bearer {token}"}
                            self.last_token_refresh = datetime.now().timestamp()
                            logger.info(f"Admin user {self.username} logged in successfully")
                            return True
                        else:
                            response.failure(f"Admin login succeeded but no token in response: {response.text}")
                    else:
                        response.failure(f"Admin login failed with status code {response.status_code}: {response.text}")
                        logger.warning(f"Admin login attempt {retry_count + 1} failed: {response.text}")
            except Exception as e:
                logger.error(f"Admin login attempt {retry_count + 1} failed with exception: {e}")
            
            # Increment retry count and wait before retrying
            retry_count += 1
            if retry_count < max_retries:
                # Use exponential backoff with jitter
                delay = retry_delay * (2 ** (retry_count - 1)) * (0.5 + random.random())
                time.sleep(delay)
        
        # All retries failed
        logger.error(f"Admin login failed after {max_retries} attempts")
        return False
    
    def refresh_token_if_needed(self):
        """
        Check if token needs refreshing and refresh if necessary.
        """
        # Check if token needs refreshing
        current_time = datetime.now().timestamp()
        token_age = current_time - self.last_token_refresh
        
        if token_age > CONFIG["auth"]["token_refresh_interval"]:
            logger.info(f"Admin token age {token_age} seconds exceeds refresh interval, refreshing token")
            
            try:
                # Refresh token
                with self.client.post(
                    f"{API_BASE_URL}/auth/refresh",
                    headers=self.auth_header,
                    name="/auth/refresh (admin)",
                    catch_response=True
                ) as response:
                    if response.status_code == 200:
                        data = response.json()
                        token = data.get('access_token')
                        if token:
                            self.auth_header = {"Authorization": f"Bearer {token}"}
                            self.last_token_refresh = current_time
                            logger.info("Admin token refreshed successfully")
                            return True
                        else:
                            response.failure(f"Admin token refresh succeeded but no token in response: {response.text}")
                            # Try to login again
                            return self.login_with_retry()
                    else:
                        response.failure(f"Admin token refresh failed with status code {response.status_code}: {response.text}")
                        logger.warning(f"Admin token refresh failed: {response.text}")
                        
                        # Try to login again
                        return self.login_with_retry()
            except Exception as e:
                logger.error(f"Admin token refresh failed with exception: {e}")
                # Try to login again
                return self.login_with_retry()
        
        return True
    
    @task(3)
    def get_all_users(self):
        """
        Get list of all users.
        Higher weight (3) as admins check user lists regularly.
        """
        # Ensure token is valid
        if not self.refresh_token_if_needed():
            return
        
        # Get all users
        with self.client.get(
            f"{API_BASE_URL}/users",
            headers=self.auth_header,
            name="/users (admin)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # Successfully got users
                data = response.json()
                
                # Handle both list and dictionary response formats
                if isinstance(data, dict) and 'items' in data:
                    users = data.get('items', [])
                else:
                    users = data if isinstance(data, list) else []
                
                users_count = len(users)
                response.success()
                logger.debug(f"Admin got {users_count} users")
            else:
                error_msg = f"Admin failed to get users: {response.status_code} {response.text}"
                logger.error(error_msg)
                response.failure(error_msg)
    
    @task(2)
    def get_event_analytics(self):
        """
        Get event analytics.
        Medium weight (2) as admins check analytics regularly.
        """
        # Ensure token is valid
        if not self.refresh_token_if_needed():
            return
        
        # Get event analytics
        with self.client.get(
            f"{API_BASE_URL}/analytics/events",
            headers=self.auth_header,
            name="/analytics/events (admin)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # Successfully got analytics
                response.success()
                logger.debug("Admin got event analytics")
            else:
                error_msg = f"Admin failed to get event analytics: {response.status_code} {response.text}"
                logger.error(error_msg)
                response.failure(error_msg)
    
    @task(2)
    def get_user_analytics(self):
        """
        Get user analytics.
        Medium weight (2) as admins check analytics regularly.
        """
        # Ensure token is valid
        if not self.refresh_token_if_needed():
            return
        
        # Get user analytics
        with self.client.get(
            f"{API_BASE_URL}/analytics/users",
            headers=self.auth_header,
            name="/analytics/users (admin)",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                # Successfully got analytics
                response.success()
                logger.debug("Admin got user analytics")
            else:
                error_msg = f"Admin failed to get user analytics: {response.status_code} {response.text}"
                logger.error(error_msg)
                response.failure(error_msg)

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
    client = get_retry_session()
    
    # Create test users
    try:
        if create_test_users(client):
            logger.info("Test users setup completed successfully")
        else:
            logger.warning("Failed to set up test users, but continuing with test")
    except Exception as e:
        logger.error(f"Error setting up test users: {e}")
        logger.warning("Continuing with test despite setup error")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Called when the test is started.
    """
    logger.info("Load test starting")
    
    # Check database connection if configured
    if CONFIG["db"]["check_connection"]:
        try:
            # Use a simple request to check if the API can connect to the database
            client = get_retry_session()
            response = client.get(
                f"{API_BASE_URL}/health/database", 
                timeout=CONFIG["db"]["connection_timeout"]
            )
            
            if response.status_code == 200:
                logger.info("Database connection check passed")
            else:
                logger.warning(f"Database connection check failed with status {response.status_code}: {response.text}")
        except Exception as e:
            logger.warning(f"Database connection check failed with exception: {e}")

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
    logger.info("Pine Time load test script loaded")
    logger.info(f"API base URL: {API_BASE_URL}")
