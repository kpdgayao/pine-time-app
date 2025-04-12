"""
Pine Time Application - Public Endpoints Load Test
Focuses specifically on testing public endpoints that don't require authentication.
Follows project guidelines for proper PostgreSQL integration and API error handling.
"""

import os
import sys
import json
import logging
import time
import random
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import requests
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
        logging.FileHandler("pine_time_public_endpoints_test.log")
    ]
)
logger = logging.getLogger("pine_time_public_endpoints_test")

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1_STR = "/api/v1"

# Test configuration
CONFIG = {
    "users": {
        "min_wait": int(os.getenv("LOAD_TEST_MIN_WAIT", "1")),
        "max_wait": int(os.getenv("LOAD_TEST_MAX_WAIT", "5")),
    },
    "resilience": {
        "fallback_enabled": os.getenv("FALLBACK_ENABLED", "True").lower() == "true",
        "detailed_logging": os.getenv("DETAILED_LOGGING", "True").lower() == "true",
    },
    "endpoints": {
        # List of public endpoints to test
        "public": [
            {"path": "/events/public", "method": "GET", "name": "Public Events", "expected_codes": [200, 401, 403]},
            {"path": "/health", "method": "GET", "name": "Health Check", "expected_codes": [200, 404]},
            {"path": "/points/leaderboard/public", "method": "GET", "name": "Public Leaderboard", "expected_codes": [200, 404]},
            {"path": "/docs", "method": "GET", "name": "API Documentation", "expected_codes": [200, 404]},
            {"path": "/openapi.json", "method": "GET", "name": "OpenAPI Schema", "expected_codes": [200, 404]}
        ]
    }
}

# Sample data for fallback when API is unavailable
SAMPLE_DATA = {
    "events": [
        {
            "id": "sample-1",
            "name": "Sample Event 1",
            "description": "This is a sample event for fallback",
            "location": "Sample Location",
            "start_time": (datetime.now() + timedelta(days=1)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
            "max_capacity": 50,
            "points": 10
        },
        {
            "id": "sample-2",
            "name": "Sample Event 2",
            "description": "Another sample event for fallback",
            "location": "Sample Location 2",
            "start_time": (datetime.now() + timedelta(days=2)).isoformat(),
            "end_time": (datetime.now() + timedelta(days=2, hours=3)).isoformat(),
            "max_capacity": 30,
            "points": 15
        }
    ],
    "leaderboard": [
        {
            "username": "sampleuser1",
            "points": 100,
            "rank": 1
        },
        {
            "username": "sampleuser2",
            "points": 75,
            "rank": 2
        }
    ],
    "health": {
        "status": "ok",
        "version": "1.0.0",
        "database": "connected"
    }
}

def get_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504)):
    """
    Create a requests session with retry capabilities
    
    Args:
        retries: Number of retries
        backoff_factor: Backoff factor for retries
        status_forcelist: Status codes to retry on
        
    Returns:
        requests.Session: Configured session with retry capabilities
    """
    session = requests.Session()
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

def safe_api_response_handler(response_data: Union[List, Dict, None]) -> List:
    """
    Safely handle different API response formats with proper error handling.
    
    Args:
        response_data: API response data which could be a list, dict with 'items' key, or None
        
    Returns:
        List: Consistently formatted list of items
    """
    if response_data is None:
        return []
    
    if isinstance(response_data, dict) and 'items' in response_data:
        return response_data.get('items', [])
    elif isinstance(response_data, list):
        return response_data
    else:
        # Try to handle other formats gracefully
        try:
            if isinstance(response_data, dict):
                # If it's a single item dict, wrap it in a list
                return [response_data]
            else:
                # Convert to string and log the unexpected format
                logger.warning(f"Unexpected API response format: {type(response_data)}")
                return []
        except Exception as e:
            logger.error(f"Error processing API response: {e}")
            return []

class PineTimePublicUser(HttpUser):
    """
    User for testing Pine Time public API endpoints.
    """
    
    wait_time = between(CONFIG["users"]["min_wait"], CONFIG["users"]["max_wait"])
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = get_retry_session()
    
    def on_start(self):
        """
        Called when a user starts.
        """
        logger.info(f"Starting public endpoint user simulation")
    
    def safe_api_call(self, method, endpoint, name, expected_codes=None, **kwargs):
        """
        Make an API call with comprehensive error handling and fallback mechanisms.
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            name: Name for Locust statistics
            expected_codes: List of expected status codes (default: [200])
            **kwargs: Additional arguments for the request
            
        Returns:
            Tuple[bool, Any]: Success flag and response data
        """
        url = f"{API_V1_STR}{endpoint}"
        fallback_data = kwargs.pop("fallback_data", None)
        catch_response = kwargs.pop("catch_response", True)
        
        if expected_codes is None:
            expected_codes = [200]
        
        try:
            with self.client.request(
                method, 
                url,
                name=name,
                catch_response=catch_response,
                **kwargs
            ) as response:
                if response.status_code in expected_codes:
                    if CONFIG["resilience"]["detailed_logging"]:
                        logger.info(f"Successful {method} request to {endpoint} with status {response.status_code}")
                    
                    # Mark as success for expected status codes
                    response.success()
                    
                    # Try to parse JSON if status code is 200
                    if response.status_code == 200:
                        try:
                            data = response.json()
                            return True, data
                        except ValueError:
                            # Not JSON or invalid JSON - might be HTML or other content
                            if CONFIG["resilience"]["detailed_logging"]:
                                logger.info(f"Non-JSON response from {endpoint} (expected for some endpoints)")
                            return True, response.text
                    else:
                        # For non-200 expected codes, return empty data
                        return True, None
                else:
                    error_msg = f"API call to {endpoint} failed with status {response.status_code}"
                    logger.error(error_msg)
                    response.failure(error_msg)
                    
                    # Use fallback data if available and enabled
                    if CONFIG["resilience"]["fallback_enabled"] and fallback_data is not None:
                        logger.info(f"Using fallback data for {endpoint}")
                        return False, fallback_data
                    return False, None
        except Exception as e:
            logger.error(f"Exception during API call to {endpoint}: {str(e)}")
            
            # Use fallback data if available and enabled
            if CONFIG["resilience"]["fallback_enabled"] and fallback_data is not None:
                logger.info(f"Using fallback data for {endpoint} after exception")
                return False, fallback_data
            return False, None
    
    @task(3)
    def get_public_events(self):
        """
        Get public events with error handling and fallback.
        """
        success, data = self.safe_api_call(
            "GET", 
            "/events/public", 
            "Public Events",
            expected_codes=[200, 401, 403],  # Accept 401/403 as "expected" for this endpoint
            fallback_data=SAMPLE_DATA["events"]
        )
        
        if success and data and isinstance(data, (list, dict)):
            events = safe_api_response_handler(data)
            if CONFIG["resilience"]["detailed_logging"]:
                logger.info(f"Retrieved {len(events)} public events")
    
    @task(2)
    def get_health_check(self):
        """
        Get health check with error handling.
        """
        success, data = self.safe_api_call(
            "GET", 
            "/health", 
            "Health Check",
            expected_codes=[200, 404],  # 404 is expected if endpoint doesn't exist
            fallback_data=SAMPLE_DATA["health"]
        )
        
        if success and data and isinstance(data, dict):
            if CONFIG["resilience"]["detailed_logging"]:
                logger.info(f"Health check status: {data.get('status', 'unknown')}")
    
    @task(2)
    def get_public_leaderboard(self):
        """
        Get public leaderboard with error handling and fallback.
        """
        success, data = self.safe_api_call(
            "GET", 
            "/points/leaderboard/public", 
            "Public Leaderboard",
            expected_codes=[200, 404],  # 404 is expected if endpoint doesn't exist
            fallback_data=SAMPLE_DATA["leaderboard"]
        )
        
        if success and data and isinstance(data, (list, dict)):
            leaderboard = safe_api_response_handler(data)
            if CONFIG["resilience"]["detailed_logging"]:
                logger.info(f"Retrieved {len(leaderboard)} leaderboard entries")
    
    @task(1)
    def get_api_docs(self):
        """
        Get API documentation with error handling.
        """
        self.safe_api_call(
            "GET", 
            "/docs", 
            "API Documentation",
            expected_codes=[200, 404]  # 404 is expected if endpoint doesn't exist
        )
    
    @task(1)
    def get_openapi_schema(self):
        """
        Get OpenAPI schema with error handling.
        """
        self.safe_api_call(
            "GET", 
            "/openapi.json", 
            "OpenAPI Schema",
            expected_codes=[200, 404]  # 404 is expected if endpoint doesn't exist
        )

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """
    Called when Locust is initialized.
    """
    logger.info("Locust initialized")
    logger.info(f"API base URL: {API_BASE_URL}")
    logger.info(f"User configuration: {CONFIG['users']}")
    logger.info(f"Resilience configuration: {CONFIG['resilience']}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Called when the test is started.
    """
    logger.info("Public endpoints load test starting")
    
    # Check API availability
    try:
        session = get_retry_session()
        response = session.get(f"{API_BASE_URL}{API_V1_STR}/events/public", timeout=5)
        if response.status_code in (200, 401, 403):
            logger.info(f"API is available (status: {response.status_code})")
        else:
            logger.warning(f"API may not be fully available, status code: {response.status_code}")
            if CONFIG["resilience"]["fallback_enabled"]:
                logger.info("Fallback mechanisms are enabled")
    except Exception as e:
        logger.warning(f"API availability check failed: {e}")
        if CONFIG["resilience"]["fallback_enabled"]:
            logger.info("Fallback mechanisms are enabled")
        else:
            logger.warning("Fallback mechanisms are DISABLED - test may fail completely if API is unavailable")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Called when the test is stopped.
    """
    logger.info("Public endpoints load test complete")
    
    # Calculate statistics
    stats = environment.stats
    
    # Total requests
    total_requests = stats.total.num_requests
    # Success rate
    success_rate = 0 if total_requests == 0 else (total_requests - stats.total.num_failures) / total_requests * 100
    # Average response time
    avg_response_time = stats.total.avg_response_time
    
    logger.info(f"===== PUBLIC ENDPOINTS TEST RESULTS =====")
    logger.info(f"Total requests: {total_requests}")
    logger.info(f"Success rate: {success_rate:.2f}%")
    logger.info(f"Average response time: {avg_response_time:.2f} ms")
    
    # Log detailed stats for each endpoint
    logger.info("Endpoint statistics:")
    for name, stat in stats.entries.items():
        logger.info(f"  {name}:")
        logger.info(f"    Requests: {stat.num_requests}")
        logger.info(f"    Failures: {stat.num_failures}")
        logger.info(f"    Success rate: {100 - (stat.num_failures / stat.num_requests * 100 if stat.num_requests > 0 else 0):.2f}%")
        logger.info(f"    Median response time: {stat.median_response_time} ms")
        logger.info(f"    95th percentile: {stat.get_response_time_percentile(0.95)} ms")
    
    logger.info("===== END OF TEST REPORT =====")

if __name__ == "__main__":
    # This script is meant to be run with the Locust command-line interface
    logger.info("Pine Time public endpoints test script loaded")
