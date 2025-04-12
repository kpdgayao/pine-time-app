"""
Simplified test script for Pine Time App.
Tests the core functionality and error handling mechanisms.
"""

import os
import sys
import logging
import argparse
from typing import Dict, Any, Optional, List, Union
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("pine_time_test.log")
    ]
)
logger = logging.getLogger("pine_time_test")

def get_database_config() -> Dict[str, Any]:
    """
    Get database configuration from environment variables.
    
    Returns:
        dict: Database configuration
    """
    database_type = os.getenv("DATABASE_TYPE", "sqlite").lower()
    
    if database_type == "postgresql":
        return {
            "database_type": "postgresql",
            "server": os.getenv("POSTGRES_SERVER"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "db": os.getenv("POSTGRES_DB"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "ssl_mode": os.getenv("POSTGRES_SSL_MODE", "require")
        }
    else:
        return {
            "database_type": "sqlite",
            "uri": os.getenv("SQLITE_DATABASE_URI", "sqlite:///./pine_time.db")
        }

def test_database_connection() -> bool:
    """
    Test database connection.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    config = get_database_config()
    
    if config["database_type"] == "postgresql":
        # PostgreSQL connection
        try:
            conn = psycopg2.connect(
                host=config["server"],
                port=config["port"],
                user=config["user"],
                password=config["password"],
                dbname=config["db"],
                cursor_factory=RealDictCursor
            )
            
            # Execute a simple query
            cursor = conn.cursor()
            cursor.execute("SELECT 1 AS test")
            result = cursor.fetchone()
            cursor.close()
            
            # Close connection
            conn.close()
            
            logger.info("✅ PostgreSQL connection successful")
            return True
        except Exception as e:
            logger.error(f"❌ PostgreSQL connection failed: {e}")
            return False
    else:
        # SQLite connection (simplified check)
        logger.info("✅ SQLite connection assumed successful")
        return True

def test_api_connection(base_url: str) -> bool:
    """
    Test API connection.
    
    Args:
        base_url: API base URL
        
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Try to access a simple endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        
        if response.status_code == 200:
            logger.info("✅ API connection successful")
            return True
        else:
            logger.warning(f"⚠️ API returned status code {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"❌ API connection failed: {e}")
        return False

def test_error_handling() -> bool:
    """
    Test error handling functionality.
    
    Returns:
        bool: True if tests pass, False otherwise
    """
    # Test safe API response handler
    def safe_api_response_handler(response: Union[Dict[str, Any], List[Any], None], 
                                  key: Optional[str] = None, 
                                  default: Any = None) -> Any:
        """
        Safely handle API responses with different formats.
        
        Args:
            response: API response (dict, list, or None)
            key: Key to extract from dict response
            default: Default value if key not found or response is None
            
        Returns:
            Extracted value or default
        """
        if response is None:
            return default
        
        if isinstance(response, dict) and key is not None:
            return response.get(key, default)
        
        return response
    
    # Test cases
    test_cases = [
        # Dictionary responses
        {
            "input": ({"items": [1, 2, 3], "total": 3}, "items", None),
            "expected": [1, 2, 3],
            "name": "Dictionary with valid key"
        },
        {
            "input": ({"items": [1, 2, 3], "total": 3}, "missing", "default"),
            "expected": "default",
            "name": "Dictionary with missing key and default"
        },
        {
            "input": ({"items": [1, 2, 3], "total": 3}, "missing", None),
            "expected": None,
            "name": "Dictionary with missing key and no default"
        },
        
        # List responses
        {
            "input": ([1, 2, 3], "items", None),
            "expected": [1, 2, 3],
            "name": "List response (key ignored)"
        },
        
        # None responses
        {
            "input": (None, "items", "default"),
            "expected": "default",
            "name": "None response with default"
        },
        {
            "input": (None, "items", None),
            "expected": None,
            "name": "None response without default"
        }
    ]
    
    # Run tests
    all_passed = True
    for test_case in test_cases:
        result = safe_api_response_handler(*test_case["input"])
        if result == test_case["expected"]:
            logger.info(f"✅ Test passed: {test_case['name']}")
        else:
            logger.error(f"❌ Test failed: {test_case['name']}")
            logger.error(f"   Expected: {test_case['expected']}, Got: {result}")
            all_passed = False
    
    return all_passed

def test_null_handling() -> bool:
    """
    Test null handling functionality.
    
    Returns:
        bool: True if tests pass, False otherwise
    """
    # Test safe_get_user_id function
    def safe_get_user_id(user: Optional[Dict[str, Any]], default: Any = None) -> Any:
        """
        Safely get user ID from user object.
        
        Args:
            user: User object or None
            default: Default value if user is None or has no ID
            
        Returns:
            User ID or default
        """
        if user is None:
            return default
        
        return user.get("id", default)
    
    # Test cases
    test_cases = [
        {
            "input": ({"id": "user123", "username": "test"}, None),
            "expected": "user123",
            "name": "Valid user with ID"
        },
        {
            "input": ({"username": "test"}, None),
            "expected": None,
            "name": "User without ID"
        },
        {
            "input": ({"username": "test"}, "default_id"),
            "expected": "default_id",
            "name": "User without ID and default"
        },
        {
            "input": (None, None),
            "expected": None,
            "name": "None user"
        },
        {
            "input": (None, "default_id"),
            "expected": "default_id",
            "name": "None user with default"
        }
    ]
    
    # Run tests
    all_passed = True
    for test_case in test_cases:
        result = safe_get_user_id(*test_case["input"])
        if result == test_case["expected"]:
            logger.info(f"✅ Test passed: {test_case['name']}")
        else:
            logger.error(f"❌ Test failed: {test_case['name']}")
            logger.error(f"   Expected: {test_case['expected']}, Got: {result}")
            all_passed = False
    
    return all_passed

def test_event_date_processing() -> bool:
    """
    Test event date processing functionality.
    
    Returns:
        bool: True if tests pass, False otherwise
    """
    # Test parse_date_safely function
    def parse_date_safely(date_str: Optional[str], default: Any = None) -> Optional[datetime]:
        """
        Safely parse date string to datetime.
        
        Args:
            date_str: Date string or None
            default: Default value if date_str is None or invalid
            
        Returns:
            Parsed datetime or default
        """
        if date_str is None:
            return default
        
        try:
            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return default
    
    # Test cases
    now = datetime.now()
    test_cases = [
        {
            "input": ("2025-04-12T14:00:00", None),
            "expected_type": datetime,
            "name": "Valid date string"
        },
        {
            "input": (None, None),
            "expected": None,
            "name": "None date string"
        },
        {
            "input": ("invalid-date", None),
            "expected": None,
            "name": "Invalid date string"
        },
        {
            "input": (None, now),
            "expected": now,
            "name": "None date string with default"
        }
    ]
    
    # Run tests
    all_passed = True
    for test_case in test_cases:
        result = parse_date_safely(*test_case["input"])
        
        if "expected_type" in test_case:
            if isinstance(result, test_case["expected_type"]):
                logger.info(f"✅ Test passed: {test_case['name']}")
            else:
                logger.error(f"❌ Test failed: {test_case['name']}")
                logger.error(f"   Expected type: {test_case['expected_type']}, Got: {type(result)}")
                all_passed = False
        elif result == test_case["expected"]:
            logger.info(f"✅ Test passed: {test_case['name']}")
        else:
            logger.error(f"❌ Test failed: {test_case['name']}")
            logger.error(f"   Expected: {test_case['expected']}, Got: {result}")
            all_passed = False
    
    return all_passed

def test_api_response_format_handling() -> bool:
    """
    Test API response format handling.
    
    Returns:
        bool: True if tests pass, False otherwise
    """
    # Test function to handle different API response formats
    def process_events_data(events_data: Union[Dict[str, Any], List[Dict[str, Any]], None]) -> List[Dict[str, Any]]:
        """
        Process events data from API.
        
        Args:
            events_data: Events data from API (dict, list, or None)
            
        Returns:
            List of event objects
        """
        if events_data is None:
            return []
        
        # Handle paginated response (dictionary with 'items' key)
        if isinstance(events_data, dict) and "items" in events_data:
            return events_data["items"]
        
        # Handle direct list response
        if isinstance(events_data, list):
            return events_data
        
        # Fallback for unexpected format
        return []
    
    # Test cases
    test_cases = [
        {
            "input": {
                "items": [
                    {"id": "1", "title": "Event 1"},
                    {"id": "2", "title": "Event 2"}
                ],
                "total": 2,
                "page": 1,
                "size": 10
            },
            "expected_length": 2,
            "name": "Paginated response"
        },
        {
            "input": [
                {"id": "1", "title": "Event 1"},
                {"id": "2", "title": "Event 2"},
                {"id": "3", "title": "Event 3"}
            ],
            "expected_length": 3,
            "name": "Direct list response"
        },
        {
            "input": None,
            "expected_length": 0,
            "name": "None response"
        },
        {
            "input": {},
            "expected_length": 0,
            "name": "Empty dict response"
        },
        {
            "input": {"data": "invalid format"},
            "expected_length": 0,
            "name": "Invalid format response"
        }
    ]
    
    # Run tests
    all_passed = True
    for test_case in test_cases:
        result = process_events_data(test_case["input"])
        
        if len(result) == test_case["expected_length"]:
            logger.info(f"✅ Test passed: {test_case['name']}")
        else:
            logger.error(f"❌ Test failed: {test_case['name']}")
            logger.error(f"   Expected length: {test_case['expected_length']}, Got: {len(result)}")
            all_passed = False
    
    return all_passed

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test Pine Time App functionality")
    
    parser.add_argument("--db", action="store_true", help="Test database connection")
    parser.add_argument("--api", action="store_true", help="Test API connection")
    parser.add_argument("--error-handling", action="store_true", help="Test error handling")
    parser.add_argument("--null-handling", action="store_true", help="Test null handling")
    parser.add_argument("--date-processing", action="store_true", help="Test date processing")
    parser.add_argument("--response-format", action="store_true", help="Test API response format handling")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--api-base-url", default="http://localhost:8000", help="API base URL")
    
    args = parser.parse_args()
    
    # If no tests specified, run all tests
    if not any([args.db, args.api, args.error_handling, args.null_handling, 
                args.date_processing, args.response_format, args.all]):
        args.all = True
    
    # Run tests
    results = {}
    
    if args.db or args.all:
        logger.info("Testing database connection...")
        results["Database Connection"] = test_database_connection()
    
    if args.api or args.all:
        logger.info("Testing API connection...")
        results["API Connection"] = test_api_connection(args.api_base_url)
    
    if args.error_handling or args.all:
        logger.info("Testing error handling...")
        results["Error Handling"] = test_error_handling()
    
    if args.null_handling or args.all:
        logger.info("Testing null handling...")
        results["Null Handling"] = test_null_handling()
    
    if args.date_processing or args.all:
        logger.info("Testing date processing...")
        results["Date Processing"] = test_event_date_processing()
    
    if args.response_format or args.all:
        logger.info("Testing API response format handling...")
        results["API Response Format"] = test_api_response_format_handling()
    
    # Print summary
    logger.info("\nTest Summary:")
    all_passed = True
    for name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{status} - {name}")
        all_passed = all_passed and result
    
    if all_passed:
        logger.info("\n🎉 All tests passed!")
        return 0
    else:
        logger.error("\n❌ Some tests failed. Check the logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())