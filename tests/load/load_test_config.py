"""
Pine Time Application - Load Testing Configuration
Provides centralized configuration for all load testing scripts.
Follows project guidelines for proper PostgreSQL integration and API error handling.
"""

import os
import logging
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pine_time_load_test.log")
    ]
)
logger = logging.getLogger("pine_time_load_test_config")

# API configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1_STR = "/api/v1"

# Database configuration
DB_CONFIG = {
    "host": os.getenv("POSTGRES_SERVER", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "database": os.getenv("POSTGRES_DB", "pine_time"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "pool_size": int(os.getenv("POOL_SIZE", "5")),
    "pool_pre_ping": os.getenv("POOL_PRE_PING", "True").lower() == "true",
    "max_overflow": int(os.getenv("MAX_OVERFLOW", "10")),
    "pool_recycle": int(os.getenv("POOL_RECYCLE", "3600")),
    "pool_timeout": int(os.getenv("POOL_TIMEOUT", "30")),
}

# Test user configuration
TEST_USERS = [
    {"username": "kpdgayao", "password": "Pogiako@1234"},  # Primary test user
    {"username": "testuser1", "password": "password123"},
    {"username": "testuser2", "password": "password123"},
    {"username": "testuser3", "password": "password123"},
    {"username": "testuser4", "password": "password123"},
    {"username": "testuser5", "password": "password123"}
]

# Load test configuration
LOAD_TEST_CONFIG = {
    "users": {
        "min_wait": int(os.getenv("LOAD_TEST_MIN_WAIT", "1")),
        "max_wait": int(os.getenv("LOAD_TEST_MAX_WAIT", "5")),
        "test_users": TEST_USERS
    },
    "auth": {
        "token_refresh_interval": int(os.getenv("TOKEN_REFRESH_INTERVAL", "1800")),
        "retry_attempts": int(os.getenv("AUTH_RETRY_ATTEMPTS", "3")),
        "retry_delay": int(os.getenv("AUTH_RETRY_DELAY", "2")),
    },
    "resilience": {
        "fallback_enabled": os.getenv("FALLBACK_ENABLED", "True").lower() == "true",
        "demo_mode": os.getenv("DEMO_MODE", "False").lower() == "true",
        "always_succeed": os.getenv("ALWAYS_SUCCEED", "False").lower() == "true",
        "detailed_logging": os.getenv("DETAILED_LOGGING", "True").lower() == "true",
    },
    "endpoints": {
        # Public endpoints that don't require authentication
        "public": [
            {"path": "/events/public", "method": "GET", "name": "Public Events", "expected_codes": [200, 401, 403]},
            {"path": "/health", "method": "GET", "name": "Health Check", "expected_codes": [200, 404]},
            {"path": "/points/leaderboard/public", "method": "GET", "name": "Public Leaderboard", "expected_codes": [200, 404]},
            {"path": "/docs", "method": "GET", "name": "API Documentation", "expected_codes": [200]},
            {"path": "/openapi.json", "method": "GET", "name": "OpenAPI Schema", "expected_codes": [200]}
        ],
        # Authenticated endpoints that require a valid token
        "authenticated": [
            {"path": "/users/me", "method": "GET", "name": "Get User Profile", "expected_codes": [200, 401, 403]},
            {"path": "/events", "method": "GET", "name": "Get Events", "expected_codes": [200, 401, 403]},
            {"path": "/badges", "method": "GET", "name": "Get Badges", "expected_codes": [200, 401, 403]},
            {"path": "/points/leaderboard", "method": "GET", "name": "Get Leaderboard", "expected_codes": [200, 401, 403]}
        ]
    },
    "database": {
        "connection_timeout": int(os.getenv("DB_CONNECTION_TIMEOUT", "5")),
        "command_timeout": int(os.getenv("DB_COMMAND_TIMEOUT", "30")),
        "max_retries": int(os.getenv("DB_MAX_RETRIES", "3")),
        "retry_delay": int(os.getenv("DB_RETRY_DELAY", "1")),
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
            "start_time": "2025-05-01T10:00:00",
            "end_time": "2025-05-01T12:00:00",
            "max_capacity": 50,
            "points": 10
        },
        {
            "id": "sample-2",
            "name": "Sample Event 2",
            "description": "Another sample event for fallback",
            "location": "Sample Location 2",
            "start_time": "2025-05-02T14:00:00",
            "end_time": "2025-05-02T17:00:00",
            "max_capacity": 30,
            "points": 15
        }
    ],
    "users": [
        {
            "id": "sample-user-1",
            "username": "sampleuser1",
            "email": "sample1@example.com",
            "full_name": "Sample User 1",
            "points": 100
        }
    ],
    "badges": [
        {
            "id": "sample-badge-1",
            "name": "Sample Badge 1",
            "description": "A sample badge for fallback",
            "points_required": 50
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

# Test scenarios
TEST_SCENARIOS = {
    "resilience": {
        "script": "pine_time_resilience_test.py",
        "description": "Tests the application's error handling and resilience capabilities",
        "recommended_settings": {
            "users": 5,
            "spawn_rate": 1,
            "run_time": "30s",
            "env_vars": {
                "FALLBACK_ENABLED": "True",
                "ALWAYS_SUCCEED": "True",
                "DETAILED_LOGGING": "True"
            }
        }
    },
    "authentication": {
        "script": "pine_time_auth_test.py",
        "description": "Tests authentication flows and both public/private endpoints",
        "recommended_settings": {
            "users": 10,
            "spawn_rate": 2,
            "run_time": "30s",
            "env_vars": {
                "FALLBACK_ENABLED": "True",
                "ALWAYS_SUCCEED": "True",
                "DETAILED_LOGGING": "True"
            }
        }
    },
    "public_endpoints": {
        "script": "pine_time_public_endpoints_test.py",
        "description": "Tests public endpoints that shouldn't require authentication",
        "recommended_settings": {
            "users": 5,
            "spawn_rate": 1,
            "run_time": "20s",
            "env_vars": {
                "FALLBACK_ENABLED": "True",
                "DETAILED_LOGGING": "True"
            }
        }
    },
    "database": {
        "script": "db_load_test.py",
        "description": "Tests database performance and connection handling",
        "recommended_settings": {
            "users": 3,
            "spawn_rate": 1,
            "run_time": "20s",
            "env_vars": {
                "FALLBACK_ENABLED": "True",
                "DETAILED_LOGGING": "True"
            }
        }
    }
}

def get_test_scenario(scenario_name: str) -> Dict[str, Any]:
    """
    Get configuration for a specific test scenario
    
    Args:
        scenario_name: Name of the test scenario
        
    Returns:
        Dict[str, Any]: Test scenario configuration
    """
    return TEST_SCENARIOS.get(scenario_name, {})

def get_sample_data(data_type: str) -> Any:
    """
    Get sample data for fallback
    
    Args:
        data_type: Type of sample data to retrieve
        
    Returns:
        Any: Sample data for the specified type
    """
    return SAMPLE_DATA.get(data_type, {})

def get_db_config() -> Dict[str, Any]:
    """
    Get database configuration
    
    Returns:
        Dict[str, Any]: Database configuration
    """
    return DB_CONFIG

def get_load_test_config() -> Dict[str, Any]:
    """
    Get load test configuration
    
    Returns:
        Dict[str, Any]: Load test configuration
    """
    return LOAD_TEST_CONFIG

if __name__ == "__main__":
    # Print configuration for reference
    import json
    
    logger.info("Pine Time Load Test Configuration")
    logger.info(f"API base URL: {API_BASE_URL}")
    logger.info(f"Load test configuration: {json.dumps(LOAD_TEST_CONFIG, indent=2, default=str)}")
    logger.info(f"Available test scenarios: {list(TEST_SCENARIOS.keys())}")
    
    # Print command examples
    logger.info("\nExample commands:")
    for name, scenario in TEST_SCENARIOS.items():
        settings = scenario["recommended_settings"]
        env_vars = " && ".join([f"set {k}={v}" for k, v in settings["env_vars"].items()])
        cmd = f"{env_vars} && locust -f tests/load/{scenario['script']} --host={API_BASE_URL} --users={settings['users']} --spawn-rate={settings['spawn_rate']} --run-time={settings['run_time']} --headless"
        logger.info(f"- {name}: {cmd}")
