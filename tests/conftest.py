"""
Test configuration for Pine Time App.
Contains fixtures and configuration for pytest.
"""

import os
import sys
import pytest
import logging
from dotenv import load_dotenv
from typing import Dict, Any, Generator
import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules
from admin_dashboard.utils.db import get_database_config, get_postgres_connection_params
from admin_dashboard.utils.api import APIClient
from admin_dashboard.config import API_ENDPOINTS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test.log")
    ]
)
logger = logging.getLogger("test")

# Load environment variables
load_dotenv()

# Set test environment
os.environ["TESTING"] = "true"

@pytest.fixture(scope="session")
def api_client() -> APIClient:
    """
    Create an API client for testing.
    
    Returns:
        APIClient: Configured API client
    """
    client = APIClient()
    return client

@pytest.fixture(scope="session")
def test_db_connection() -> Generator:
    """
    Create a test database connection.
    
    Yields:
        Connection: Database connection
    """
    # Get connection parameters
    params = get_postgres_connection_params()
    
    # Create connection
    conn = psycopg2.connect(
        host=params.get("server"),
        port=params.get("port"),
        user=params.get("user"),
        password=params.get("password"),
        dbname=params.get("db"),
        cursor_factory=RealDictCursor
    )
    
    # Set isolation level to autocommit
    conn.set_session(autocommit=True)
    
    # Yield connection
    yield conn
    
    # Close connection
    conn.close()

@pytest.fixture(scope="function")
def test_db_transaction(test_db_connection) -> Generator:
    """
    Create a test database transaction that will be rolled back after the test.
    
    Args:
        test_db_connection: Database connection
        
    Yields:
        Connection: Database connection with transaction
    """
    # Begin transaction
    test_db_connection.set_session(autocommit=False)
    
    # Yield connection
    yield test_db_connection
    
    # Rollback transaction
    test_db_connection.rollback()
    
    # Reset to autocommit
    test_db_connection.set_session(autocommit=True)

@pytest.fixture(scope="session")
def test_user_credentials() -> Dict[str, str]:
    """
    Get test user credentials.
    
    Returns:
        Dict[str, str]: Test user credentials
    """
    return {
        "username": os.getenv("TEST_USERNAME", "testuser"),
        "password": os.getenv("TEST_PASSWORD", "testpassword"),
        "email": os.getenv("TEST_EMAIL", "test@example.com")
    }

@pytest.fixture(scope="session")
def test_admin_credentials() -> Dict[str, str]:
    """
    Get test admin credentials.
    
    Returns:
        Dict[str, str]: Test admin credentials
    """
    return {
        "username": os.getenv("TEST_ADMIN_USERNAME", "testadmin"),
        "password": os.getenv("TEST_ADMIN_PASSWORD", "testadminpassword"),
        "email": os.getenv("TEST_ADMIN_EMAIL", "testadmin@example.com")
    }

@pytest.fixture(scope="function")
def auth_headers(api_client, test_user_credentials) -> Dict[str, str]:
    """
    Get authentication headers for a test user.
    
    Args:
        api_client: API client
        test_user_credentials: Test user credentials
        
    Returns:
        Dict[str, str]: Authentication headers
    """
    # Login
    response = api_client.post(
        API_ENDPOINTS["auth"]["token"],
        json_data={
            "username": test_user_credentials["username"],
            "password": test_user_credentials["password"]
        },
        with_auth=False
    )
    
    # Return headers
    return {
        "Authorization": f"Bearer {response.get('access_token')}"
    }

@pytest.fixture(scope="function")
def admin_auth_headers(api_client, test_admin_credentials) -> Dict[str, str]:
    """
    Get authentication headers for a test admin.
    
    Args:
        api_client: API client
        test_admin_credentials: Test admin credentials
        
    Returns:
        Dict[str, str]: Authentication headers
    """
    # Login
    response = api_client.post(
        API_ENDPOINTS["auth"]["token"],
        json_data={
            "username": test_admin_credentials["username"],
            "password": test_admin_credentials["password"]
        },
        with_auth=False
    )
    
    # Return headers
    return {
        "Authorization": f"Bearer {response.get('access_token')}"
    }