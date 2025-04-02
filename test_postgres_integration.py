"""
Test script for verifying PostgreSQL integration with the Streamlit app
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("postgres_test.log")
    ]
)
logger = logging.getLogger("postgres_test")

# Load environment variables
load_dotenv()

# Add admin_dashboard directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "admin_dashboard"))

# Import utilities
from admin_dashboard.utils.db import (
    get_database_config, get_database_uri, test_database_connection,
    is_demo_mode, get_postgres_connection_params
)
from admin_dashboard.utils.api import (
    api_client, check_api_connection, APIError
)
from admin_dashboard.utils.connection import (
    verify_connection, get_sample_users, get_sample_events
)
from admin_dashboard.config import (
    API_ENDPOINTS, DATABASE_TYPE
)

def print_separator(title=""):
    """Print a separator line with optional title"""
    width = 80
    if title:
        print(f"\n{'-' * ((width - len(title) - 2) // 2)} {title} {'-' * ((width - len(title) - 2) // 2)}\n")
    else:
        print(f"\n{'-' * width}\n")

def test_database_config():
    """Test database configuration retrieval"""
    print_separator("Testing Database Configuration")
    
    try:
        # Get database configuration
        config = get_database_config()
        print(f"Database Type: {config.get('database_type', 'unknown').upper()}")
        
        # Check if PostgreSQL is configured
        if config.get('database_type') == 'postgresql':
            print("PostgreSQL configuration:")
            for key, value in config.items():
                if key != 'password' and key != 'database_type':
                    print(f"  {key}: {value}")
            print("  password: ********")
            
            # Get database URI
            uri = get_database_uri()
            masked_uri = uri.replace(config.get('password', ''), '********')
            print(f"Database URI: {masked_uri}")
            
            return True
        else:
            print(f"WARNING: Database type is not PostgreSQL, found: {config.get('database_type', 'unknown')}")
            return False
    except Exception as e:
        logger.error(f"Error testing database configuration: {str(e)}")
        print(f"ERROR: {str(e)}")
        return False

def test_postgres_connection():
    """Test direct connection to PostgreSQL database"""
    print_separator("Testing PostgreSQL Connection")
    
    try:
        # Test database connection
        start_time = time.time()
        result = test_database_connection()
        end_time = time.time()
        
        if result.get('success'):
            print(f"✅ Successfully connected to PostgreSQL database")
            print(f"Connection time: {(end_time - start_time) * 1000:.2f}ms")
            print(f"Database version: {result.get('version', 'unknown')}")
            return True
        else:
            print(f"❌ Failed to connect to PostgreSQL database")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        logger.error(f"Error testing PostgreSQL connection: {str(e)}")
        print(f"ERROR: {str(e)}")
        return False

def test_api_connection():
    """Test connection to FastAPI backend"""
    print_separator("Testing API Connection")
    
    try:
        # Test API connection
        start_time = time.time()
        result = check_api_connection()
        end_time = time.time()
        
        if result.get('success'):
            print(f"✅ Successfully connected to API")
            print(f"Connection time: {(end_time - start_time) * 1000:.2f}ms")
            print(f"API version: {result.get('version', 'unknown')}")
            return True
        else:
            print(f"❌ Failed to connect to API")
            print(f"Error: {result.get('error', 'Unknown error')}")
            return False
    except Exception as e:
        logger.error(f"Error testing API connection: {str(e)}")
        print(f"ERROR: {str(e)}")
        return False

def test_sample_data():
    """Test sample data generation for fallback"""
    print_separator("Testing Sample Data Generation")
    
    try:
        # Get sample users
        users = get_sample_users()
        print(f"Sample users generated: {len(users.get('items', []))}")
        if users.get('items'):
            print(f"First user: {users['items'][0].get('username')} ({users['items'][0].get('email')})")
        
        # Get sample events
        events = get_sample_events()
        print(f"Sample events generated: {len(events.get('items', []))}")
        if events.get('items'):
            print(f"First event: {events['items'][0].get('title')} ({events['items'][0].get('event_type')})")
        
        return True
    except Exception as e:
        logger.error(f"Error testing sample data generation: {str(e)}")
        print(f"ERROR: {str(e)}")
        return False

def test_api_endpoints():
    """Test API endpoints with authentication"""
    print_separator("Testing API Endpoints")
    
    # Skip if in demo mode
    if is_demo_mode():
        print("Demo mode is enabled, skipping API endpoint tests")
        return None
    
    try:
        # Try to login with test credentials
        print("Attempting to login with test credentials...")
        
        try:
            response = api_client.post(
                API_ENDPOINTS["auth"]["login"],
                json_data={
                    "username": "testuser",
                    "password": "testpassword"
                },
                with_auth=False
            )
            
            print("✅ Login successful")
            print(f"Token received: {response.get('access_token', '')[:10]}...")
            
            # Try to get users
            print("\nFetching users...")
            users = api_client.get(
                API_ENDPOINTS["users"]["list"],
                with_auth=True
            )
            
            print(f"✅ Successfully retrieved {len(users)} users")
            
            # Try to get events
            print("\nFetching events...")
            events = api_client.get(
                API_ENDPOINTS["events"]["list"],
                with_auth=True
            )
            
            print(f"✅ Successfully retrieved {len(events)} events")
            
            return True
        except APIError as e:
            print(f"❌ API Error: {str(e)}")
            return False
    except Exception as e:
        logger.error(f"Error testing API endpoints: {str(e)}")
        print(f"ERROR: {str(e)}")
        return False

def test_connection_verification():
    """Test connection verification function"""
    print_separator("Testing Connection Verification")
    
    try:
        # Verify connection
        start_time = time.time()
        result = verify_connection(force=True)
        end_time = time.time()
        
        print(f"Connection verification time: {(end_time - start_time) * 1000:.2f}ms")
        print(f"Connection status: {'✅ Connected' if result.get('success') else '❌ Disconnected'}")
        print(f"Database type: {result.get('db_type', 'unknown').upper()}")
        print(f"API status: {'✅ Connected' if result.get('api_connected') else '❌ Disconnected'}")
        print(f"Database status: {'✅ Connected' if result.get('db_connected') else '❌ Disconnected'}")
        
        if not result.get('success'):
            if not result.get('api_connected'):
                print(f"API Error: {result.get('api_message', 'Unknown error')}")
            if not result.get('db_connected'):
                print(f"Database Error: {result.get('db_message', 'Unknown error')}")
        
        return result.get('success')
    except Exception as e:
        logger.error(f"Error testing connection verification: {str(e)}")
        print(f"ERROR: {str(e)}")
        return False

def main():
    """Main test function"""
    print_separator("PostgreSQL Integration Test")
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Database type from environment: {DATABASE_TYPE.upper()}")
    print(f"Demo mode: {'Enabled' if is_demo_mode() else 'Disabled'}")
    
    # Run tests
    db_config_success = test_database_config()
    postgres_conn_success = test_postgres_connection()
    api_conn_success = test_api_connection()
    sample_data_success = test_sample_data()
    api_endpoints_success = test_api_endpoints()
    connection_verify_success = test_connection_verification()
    
    # Print summary
    print_separator("Test Summary")
    print(f"Database Configuration: {'✅ Success' if db_config_success else '❌ Failed'}")
    print(f"PostgreSQL Connection: {'✅ Success' if postgres_conn_success else '❌ Failed'}")
    print(f"API Connection: {'✅ Success' if api_conn_success else '❌ Failed'}")
    print(f"Sample Data Generation: {'✅ Success' if sample_data_success else '❌ Failed'}")
    print(f"API Endpoints: {'✅ Success' if api_endpoints_success else '❌ Failed' if api_endpoints_success is not None else '⚠️ Skipped (Demo Mode)'}")
    print(f"Connection Verification: {'✅ Success' if connection_verify_success else '❌ Failed'}")
    
    # Overall result
    required_tests = [db_config_success, postgres_conn_success, sample_data_success]
    if all(required_tests):
        print("\n✅ All required tests passed! The PostgreSQL integration is working correctly.")
        print("Note: API connection failures are expected if the API server is not running.")
    else:
        print("\n❌ Some required tests failed. Please check the logs for more information.")

if __name__ == "__main__":
    main()
