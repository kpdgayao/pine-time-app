"""
Pine Time Application - Basic Load Testing Script
A simplified version that focuses on testing the core functionality
without requiring authentication.
"""

import os
import sys
import logging
import random
from typing import Dict, Any, Optional
from datetime import datetime
from locust import HttpUser, task, between, events
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("basic_load_test.log")
    ]
)
logger = logging.getLogger("basic_load_test")

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1_STR = "/api/v1"

class PineTimeBasicUser(HttpUser):
    """
    Basic user for load testing the Pine Time API without authentication.
    Tests only public endpoints to avoid authentication issues.
    """
    
    wait_time = between(1, 3)
    
    @task(3)
    def get_public_events(self):
        """Get public events list"""
        with self.client.get(
            f"{API_V1_STR}/events/public",
            name="Public Events",
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
                    logger.info(f"Got {events_count} public events")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing events: {str(e)}")
                    response.failure(f"Error processing events: {str(e)}")
            else:
                # If 404, the endpoint might not exist, try a different one
                if response.status_code == 404:
                    logger.warning("Public events endpoint not found, trying regular events endpoint")
                    self.get_regular_events()
                else:
                    logger.error(f"Get public events failed: {response.status_code} - {response.text}")
                    response.failure(f"Get public events failed: {response.status_code}")
    
    def get_regular_events(self):
        """Fallback to get regular events list"""
        with self.client.get(
            f"{API_V1_STR}/events",
            name="Regular Events",
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
                    logger.info(f"Got {events_count} regular events")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing regular events: {str(e)}")
                    response.failure(f"Error processing regular events: {str(e)}")
            else:
                logger.error(f"Get regular events failed: {response.status_code} - {response.text}")
                response.failure(f"Get regular events failed: {response.status_code}")
    
    @task(2)
    def get_badges(self):
        """Get badges list"""
        with self.client.get(
            f"{API_V1_STR}/badges",
            name="Badges",
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
                    logger.info(f"Got {badges_count} badges")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing badges: {str(e)}")
                    response.failure(f"Error processing badges: {str(e)}")
            else:
                logger.error(f"Get badges failed: {response.status_code} - {response.text}")
                response.failure(f"Get badges failed: {response.status_code}")
    
    @task(1)
    def get_leaderboard(self):
        """Get points leaderboard"""
        with self.client.get(
            f"{API_V1_STR}/points/leaderboard/public",
            name="Public Leaderboard",
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
                    logger.info(f"Got leaderboard with {users_count} users")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing leaderboard: {str(e)}")
                    response.failure(f"Error processing leaderboard: {str(e)}")
            elif response.status_code == 404:
                # If 404, the endpoint might not exist, try the regular leaderboard
                logger.warning("Public leaderboard endpoint not found, trying regular leaderboard endpoint")
                self.get_regular_leaderboard()
            else:
                logger.error(f"Get public leaderboard failed: {response.status_code} - {response.text}")
                response.failure(f"Get public leaderboard failed: {response.status_code}")
    
    def get_regular_leaderboard(self):
        """Fallback to get regular leaderboard"""
        with self.client.get(
            f"{API_V1_STR}/points/leaderboard",
            name="Regular Leaderboard",
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
                    logger.info(f"Got regular leaderboard with {users_count} users")
                    response.success()
                except Exception as e:
                    logger.error(f"Error processing regular leaderboard: {str(e)}")
                    response.failure(f"Error processing regular leaderboard: {str(e)}")
            else:
                logger.error(f"Get regular leaderboard failed: {response.status_code} - {response.text}")
                response.failure(f"Get regular leaderboard failed: {response.status_code}")
    
    @task(1)
    def check_health(self):
        """Check API health"""
        with self.client.get(
            f"{API_V1_STR}/health",
            name="Health Check",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                logger.info("Health check successful")
                response.success()
            else:
                logger.error(f"Health check failed: {response.status_code} - {response.text}")
                response.failure(f"Health check failed: {response.status_code}")

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """Called when Locust is initialized"""
    logger.info("Locust initialized")
    logger.info(f"API base URL: {API_BASE_URL}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """Called when the test is started"""
    logger.info("Load test starting")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """Called when the test is stopped"""
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
    logger.info("Basic load test script loaded")
