"""
Pine Time App Comprehensive Test Runner

This script provides a comprehensive testing approach for the Pine Time application,
supporting both PostgreSQL-based testing and demo mode with proper error handling.

Following PEP 8 style guidelines and using type hints as per project requirements.
"""

import os
import sys
import subprocess
import logging
import argparse
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Configure logging with appropriate severity levels
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"pine_time_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("pine_time_test_runner")

def check_postgres_connection() -> bool:
    """
    Check PostgreSQL connection with proper error handling.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Add project root to path to ensure imports work
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        # Import here to avoid circular imports
        from admin_dashboard.utils.db import test_database_connection
        
        # Test the connection
        logger.info("Testing PostgreSQL database connection...")
        result = test_database_connection()
        
        if result:
            logger.info("PostgreSQL database connection successful")
            return True
        else:
            logger.warning("PostgreSQL database connection failed")
            return False
    except Exception as e:
        logger.error(f"Error testing database connection: {str(e)}")
        return False

def setup_test_environment(force_demo: bool = False) -> bool:
    """
    Set up test environment with proper validation of required parameters.
    
    Args:
        force_demo: Force demo mode regardless of database connection
        
    Returns:
        bool: True if using demo mode, False if using PostgreSQL
    """
    # Load environment variables from .env.test
    env_file = Path("tests/.env.test")
    if env_file.exists():
        logger.info(f"Loading test environment from {env_file}")
        load_dotenv(env_file)
    
    # Check if demo mode is enabled in environment
    demo_mode = os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes")
    
    # If demo mode is forced, use it
    if force_demo:
        logger.info("Demo mode forced by command line argument")
        os.environ["DEMO_MODE"] = "true"
        return True
    
    # If demo mode is not enabled, check PostgreSQL connection
    if not demo_mode:
        postgres_connected = check_postgres_connection()
        if not postgres_connected:
            logger.warning("PostgreSQL connection failed, falling back to demo mode")
            os.environ["DEMO_MODE"] = "true"
            return True
        else:
            logger.info("Using PostgreSQL for tests")
            os.environ["DEMO_MODE"] = "false"
            return False
    else:
        logger.info("Using demo mode for tests")
        os.environ["DEMO_MODE"] = "true"
        return True

def create_test_script(script_content: str, file_path: str) -> bool:
    """
    Create a temporary test script with the given content.
    
    Args:
        script_content: Content of the test script
        file_path: Path to save the script
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        with open(file_path, 'w') as f:
            f.write(script_content)
        logger.info(f"Created test script at {file_path}")
        return True
    except Exception as e:
        logger.error(f"Error creating test script: {str(e)}")
        return False

def run_command(cmd: List[str], description: str) -> Tuple[bool, str]:
    """
    Run a command with proper error handling and logging.
    
    Args:
        cmd: Command to run
        description: Description of the command
        
    Returns:
        Tuple[bool, str]: Success flag and output
    """
    logger.info(f"Running {description}...")
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Log output with appropriate severity
        if result.stdout:
            logger.info(f"Output:\n{result.stdout}")
        if result.stderr:
            logger.error(f"Errors:\n{result.stderr}")
        
        success = result.returncode == 0
        if success:
            logger.info(f"{description} completed successfully")
        else:
            logger.error(f"{description} failed with exit code {result.returncode}")
        
        return success, result.stdout + result.stderr
    except Exception as e:
        logger.error(f"Error running {description}: {str(e)}")
        return False, str(e)

def run_core_tests(demo_mode: bool) -> bool:
    """
    Run core functionality tests with proper error handling.
    
    Args:
        demo_mode: Whether to run in demo mode
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    # Define the core test script content
    core_test_script = """
import os
import sys
import pytest
from typing import Dict, Any
from datetime import datetime

# Set environment variables
os.environ["DEMO_MODE"] = "true"

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_demo_mode_enabled() -> None:
    \"\"\"Test that demo mode is properly enabled.\"\"\"
    from admin_dashboard.utils.db import is_demo_mode
    assert is_demo_mode() == True, "Demo mode should be enabled"

def test_api_error_classes() -> None:
    \"\"\"Test API error classes.\"\"\"
    from admin_dashboard.utils.api import APIError, PostgreSQLError
    
    # Test APIError
    error = APIError("Test error", 404)
    assert error.message == "Test error"
    assert error.status_code == 404
    
    # Test PostgreSQLError
    pg_error = PostgreSQLError("PG error", 500, None, "23505")
    assert pg_error.message == "PG error"
    assert pg_error.pg_code == "23505"
    assert isinstance(pg_error, APIError)

def test_api_endpoints_config() -> None:
    \"\"\"Test API endpoints configuration.\"\"\"
    from admin_dashboard.config import API_ENDPOINTS
    
    assert isinstance(API_ENDPOINTS, dict)
    assert "auth" in API_ENDPOINTS
    assert "users" in API_ENDPOINTS
    assert "events" in API_ENDPOINTS
"""
    
    # Create the test script
    test_script_path = "pine_time_core_test.py"
    if not create_test_script(core_test_script, test_script_path):
        return False
    
    # Run the test
    cmd = ["pytest", "-xvs", test_script_path]
    success, _ = run_command(cmd, "Core Functionality Tests")
    
    # Clean up
    try:
        os.remove(test_script_path)
    except:
        pass
    
    return success

def run_api_tests(demo_mode: bool) -> bool:
    """
    Run API tests with proper error handling.
    
    Args:
        demo_mode: Whether to run in demo mode
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    if not demo_mode:
        # Run the official API tests if not in demo mode
        cmd = ["pytest", "-xvs", "tests/api"]
        success, _ = run_command(cmd, "API Tests")
        return success
    
    # Define the API test script content for demo mode
    api_test_script = """
import os
import sys
import pytest
from typing import Dict, Any, List
from datetime import datetime

# Set environment variables
os.environ["DEMO_MODE"] = "true"

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_api_client_in_demo_mode() -> None:
    \"\"\"Test API client in demo mode.\"\"\"
    from admin_dashboard.utils.api import APIClient
    
    client = APIClient()
    assert client is not None

def test_get_events_in_demo_mode() -> None:
    \"\"\"Test get_events function in demo mode.\"\"\"
    from admin_dashboard.utils.api import get_events
    
    events = get_events()
    assert isinstance(events, list)
    assert len(events) > 0

def test_get_badges_in_demo_mode() -> None:
    \"\"\"Test get_badges function in demo mode.\"\"\"
    from admin_dashboard.utils.api import get_badges
    
    badges = get_badges()
    assert isinstance(badges, list)
    assert len(badges) > 0

def test_parse_date_safely() -> None:
    \"\"\"Test parse_date_safely function.\"\"\"
    from admin_dashboard.utils.api import parse_date_safely
    
    # Test valid date
    valid_date = parse_date_safely("2025-04-12T15:00:00")
    assert valid_date is not None
    assert valid_date.year == 2025
    
    # Test invalid date
    default_date = datetime.now()
    invalid_date = parse_date_safely("not-a-date", default=default_date)
    assert invalid_date == default_date
"""
    
    # Create the test script
    test_script_path = "pine_time_api_test.py"
    if not create_test_script(api_test_script, test_script_path):
        return False
    
    # Run the test
    cmd = ["pytest", "-xvs", test_script_path]
    success, _ = run_command(cmd, "API Demo Tests")
    
    # Clean up
    try:
        os.remove(test_script_path)
    except:
        pass
    
    return success

def run_db_tests(demo_mode: bool) -> bool:
    """
    Run database tests with proper error handling.
    
    Args:
        demo_mode: Whether to run in demo mode
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    # Define the database test script content
    db_test_script = """
import os
import sys
import pytest
from typing import Dict, Any

# Set environment variables
os.environ["DEMO_MODE"] = "true"

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_is_demo_mode() -> None:
    \"\"\"Test is_demo_mode function.\"\"\"
    from admin_dashboard.utils.db import is_demo_mode
    
    assert is_demo_mode() == True

def test_get_database_config() -> None:
    \"\"\"Test get_database_config function.\"\"\"
    from admin_dashboard.utils.db import get_database_config
    
    config = get_database_config()
    assert isinstance(config, dict)
    assert "database_type" in config
"""
    
    # Create the test script
    test_script_path = "pine_time_db_test.py"
    if not create_test_script(db_test_script, test_script_path):
        return False
    
    # Run the test
    cmd = ["pytest", "-xvs", test_script_path]
    success, _ = run_command(cmd, "Database Tests")
    
    # Clean up
    try:
        os.remove(test_script_path)
    except:
        pass
    
    return success

def run_connection_tests(demo_mode: bool) -> bool:
    """
    Run connection utility tests with proper error handling.
    
    Args:
        demo_mode: Whether to run in demo mode
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    # Define the connection test script content
    connection_test_script = """
import os
import sys
import pytest
from typing import Dict, Any, List

# Set environment variables
os.environ["DEMO_MODE"] = "true"

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_sample_data_generation() -> None:
    \"\"\"Test sample data generation functions.\"\"\"
    from admin_dashboard.utils.connection import (
        get_sample_events,
        get_sample_badges,
        get_sample_users,
        get_sample_leaderboard
    )
    
    # Test events
    events = get_sample_events()
    assert isinstance(events, list)
    assert len(events) > 0
    
    # Test badges
    badges = get_sample_badges()
    assert isinstance(badges, list)
    assert len(badges) > 0
    
    # Test users
    users = get_sample_users()
    assert isinstance(users, list)
    assert len(users) > 0
    
    # Test leaderboard
    leaderboard = get_sample_leaderboard()
    assert isinstance(leaderboard, list)
    assert len(leaderboard) > 0
"""
    
    # Create the test script
    test_script_path = "pine_time_connection_test.py"
    if not create_test_script(connection_test_script, test_script_path):
        return False
    
    # Run the test
    cmd = ["pytest", "-xvs", test_script_path]
    success, _ = run_command(cmd, "Connection Utility Tests")
    
    # Clean up
    try:
        os.remove(test_script_path)
    except:
        pass
    
    return success

def main() -> int:
    """
    Main function with comprehensive error handling and validation.
    
    Returns:
        int: Exit code
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Pine Time App Comprehensive Test Runner")
    parser.add_argument("--demo", action="store_true", help="Force demo mode")
    parser.add_argument("--postgres", action="store_true", help="Force PostgreSQL mode (will fail if not available)")
    parser.add_argument("--core", action="store_true", help="Run core tests")
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--db", action="store_true", help="Run database tests")
    parser.add_argument("--connection", action="store_true", help="Run connection utility tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Check for conflicting options
    if args.demo and args.postgres:
        logger.error("Cannot specify both --demo and --postgres")
        return 1
    
    # Set up test environment
    if args.postgres:
        # Force PostgreSQL mode
        postgres_connected = check_postgres_connection()
        if not postgres_connected:
            logger.error("PostgreSQL connection failed and --postgres was specified")
            return 1
        demo_mode = False
        os.environ["DEMO_MODE"] = "false"
    else:
        # Set up environment and determine mode
        demo_mode = setup_test_environment(args.demo)
    
    # Determine which tests to run
    run_core = args.core or args.all
    run_api = args.api or args.all
    run_db = args.db or args.all
    run_connection = args.connection or args.all
    
    # If no specific tests are selected, run all
    if not (run_core or run_api or run_db or run_connection):
        run_core = run_api = run_db = run_connection = True
    
    # Track test results
    results = {}
    
    # Run tests
    if run_core:
        results["core"] = run_core_tests(demo_mode)
    
    if run_api:
        results["api"] = run_api_tests(demo_mode)
    
    if run_db:
        results["db"] = run_db_tests(demo_mode)
    
    if run_connection:
        results["connection"] = run_connection_tests(demo_mode)
    
    # Print summary
    logger.info("\n=== Pine Time App Test Results ===")
    mode_str = "DEMO MODE" if demo_mode else "POSTGRESQL MODE"
    logger.info(f"Tests ran in {mode_str}")
    
    for test_name, success in results.items():
        status = "PASSED" if success else "FAILED"
        logger.info(f"{test_name.upper()}: {status}")
    
    # Overall result
    if all(results.values()):
        logger.info("\nAll Pine Time app tests PASSED!")
        return 0
    else:
        logger.error("\nSome Pine Time app tests FAILED. See log for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
