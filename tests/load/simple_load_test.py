"""
Pine Time Application - Simple Load Testing Script
A simplified version for basic functionality testing
"""

import os
import sys
import logging
import random
from typing import Dict, Any
from datetime import datetime
from locust import HttpUser, task, between, events
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("simple_load_test.log")
    ]
)
logger = logging.getLogger("simple_load_test")

# Load environment variables
load_dotenv()

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

class PineTimeUser(HttpUser):
    """
    Simplified user for load testing the Pine Time API
    """
    
    wait_time = between(1, 3)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.auth_header = {}
        
    @task(1)
    def health_check(self):
        """Simple health check endpoint"""
        with self.client.get(
            "/health",
            name="Health Check",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                logger.info(f"Health check successful: {response.text}")
            else:
                response.failure(f"Health check failed: {response.status_code}")
                logger.error(f"Health check failed: {response.status_code} - {response.text}")
    
    @task(1)
    def get_events(self):
        """Get public events without authentication"""
        with self.client.get(
            "/events/public",
            name="Public Events",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    events_count = len(data) if isinstance(data, list) else 0
                    response.success()
                    logger.info(f"Got {events_count} public events")
                except Exception as e:
                    response.failure(f"Error processing events: {str(e)}")
                    logger.error(f"Error processing events: {str(e)}")
            else:
                response.failure(f"Failed to get public events: {response.status_code}")
                logger.error(f"Failed to get public events: {response.status_code} - {response.text}")

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

if __name__ == "__main__":
    # This script is meant to be run with the Locust command-line interface
    logger.info("Simple load test script loaded")
