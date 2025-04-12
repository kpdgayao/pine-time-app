"""
Enhanced Test Runner for Pine Time App

This script provides a comprehensive approach to testing the Pine Time application,
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
        logging.FileHandler(f"enhanced_test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("enhanced_test_runner")

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

def run_db_tests(demo_mode: bool) -> bool:
    """
    Run database utility tests with proper error handling.
    
    Args:
        demo_mode: Whether to run in demo mode
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    # Select appropriate tests based on mode
    if demo_mode:
        test_path = "tests/test_db_utils.py::test_is_demo_mode"
    else:
        test_path = "tests/test_db_utils.py"
    
    # Run tests
    cmd = ["pytest", "-xvs", test_path]
    success, _ = run_command(cmd, "Database Utility Tests")
    return success

def run_api_tests(demo_mode: bool) -> bool:
    """
    Run API tests with proper error handling.
    
    Args:
        demo_mode: Whether to run in demo mode
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    # In demo mode, run only tests that work without API connection
    if demo_mode:
        # Create a temporary script to test API utilities in demo mode
        test_script = """
import os
import sys
import pytest
from pathlib import Path

# Set demo mode
os.environ["DEMO_MODE"] = "true"

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import API utilities
from admin_dashboard.utils.api import APIClient, get_events, get_badges

def test_api_client_demo_mode():
    \"\"\"Test APIClient in demo mode.\"\"\"
    client = APIClient()
    assert client is not None

def test_get_events_demo_mode():
    \"\"\"Test get_events in demo mode.\"\"\"
    events = get_events()
    assert isinstance(events, list)
    assert len(events) > 0

def test_get_badges_demo_mode():
    \"\"\"Test get_badges in demo mode.\"\"\"
    badges = get_badges()
    assert isinstance(badges, list)
    assert len(badges) > 0
"""
        # Write the test script
        demo_test_path = Path("tests/temp_api_demo_test.py")
        demo_test_path.write_text(test_script)
        
        # Run the demo tests
        cmd = ["pytest", "-xvs", str(demo_test_path)]
        success, _ = run_command(cmd, "API Demo Tests")
        
        # Clean up
        if demo_test_path.exists():
            demo_test_path.unlink()
        
        return success
    else:
        # Run the full API tests
        cmd = ["pytest", "-xvs", "tests/api"]
        success, _ = run_command(cmd, "API Tests")
        return success

def run_frontend_tests(demo_mode: bool) -> bool:
    """
    Run frontend tests with proper error handling.
    
    Args:
        demo_mode: Whether to run in demo mode
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    # In demo mode, create a simplified test that doesn't require Streamlit context
    if demo_mode:
        # Create a temporary script to test frontend utilities in demo mode
        test_script = """
import os
import sys
import pytest
from pathlib import Path

# Set demo mode
os.environ["DEMO_MODE"] = "true"

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import frontend utilities
from admin_dashboard.utils.db import is_demo_mode
from admin_dashboard.utils.auth import AuthError

def test_demo_mode_enabled():
    \"\"\"Test that demo mode is enabled.\"\"\"
    assert is_demo_mode() == True

def test_auth_error_class():
    \"\"\"Test AuthError class.\"\"\"
    error = AuthError("Test error")
    assert str(error) == "Test error"
"""
        # Write the test script
        demo_test_path = Path("tests/temp_frontend_demo_test.py")
        demo_test_path.write_text(test_script)
        
        # Run the demo tests
        cmd = ["pytest", "-xvs", str(demo_test_path)]
        success, _ = run_command(cmd, "Frontend Demo Tests")
        
        # Clean up
        if demo_test_path.exists():
            demo_test_path.unlink()
        
        return success
    else:
        # Run the full frontend tests
        cmd = ["pytest", "-xvs", "tests/frontend"]
        success, _ = run_command(cmd, "Frontend Tests")
        return success

def run_integration_tests(demo_mode: bool) -> bool:
    """
    Run integration tests with proper error handling.
    
    Args:
        demo_mode: Whether to run in demo mode
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    # In demo mode, create a simplified integration test
    if demo_mode:
        # Create a temporary script to test integration in demo mode
        test_script = """
import os
import sys
import pytest
from pathlib import Path

# Set demo mode
os.environ["DEMO_MODE"] = "true"

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import utilities
from admin_dashboard.utils.db import is_demo_mode
from admin_dashboard.utils.api import get_events, get_badges
from admin_dashboard.utils.auth import login, logout

def test_integration_demo_mode():
    \"\"\"Test basic integration in demo mode.\"\"\"
    # Verify demo mode
    assert is_demo_mode() == True
    
    # Test login with demo credentials
    result = login("demo@pinetimeexperience.com", "demo")
    assert result == True
    
    # Test API functions
    events = get_events()
    assert isinstance(events, list)
    
    badges = get_badges()
    assert isinstance(badges, list)
    
    # Test logout
    logout()
"""
        # Write the test script
        demo_test_path = Path("tests/temp_integration_demo_test.py")
        demo_test_path.write_text(test_script)
        
        # Run the demo tests
        cmd = ["pytest", "-xvs", str(demo_test_path)]
        success, _ = run_command(cmd, "Integration Demo Tests")
        
        # Clean up
        if demo_test_path.exists():
            demo_test_path.unlink()
        
        return success
    else:
        # Run the full integration tests
        cmd = ["pytest", "-xvs", "tests/integration"]
        success, _ = run_command(cmd, "Integration Tests")
        return success

def run_official_tests(test_types: List[str], verbose: bool) -> bool:
    """
    Run tests using the official test runner.
    
    Args:
        test_types: List of test types to run
        verbose: Whether to enable verbose output
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    # Build command
    cmd = ["python", "tests/run_tests.py"]
    
    # Add test types
    for test_type in test_types:
        cmd.append(f"--{test_type}")
    
    # Add verbose flag
    if verbose:
        cmd.append("--verbose")
    
    # Run the official tests
    success, _ = run_command(cmd, "Official Tests")
    return success

def main() -> int:
    """
    Main function with comprehensive error handling and validation.
    
    Returns:
        int: Exit code
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Enhanced Test Runner for Pine Time App")
    parser.add_argument("--demo", action="store_true", help="Force demo mode")
    parser.add_argument("--postgres", action="store_true", help="Force PostgreSQL mode (will fail if not available)")
    parser.add_argument("--db", action="store_true", help="Run database tests")
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--frontend", action="store_true", help="Run frontend tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--official", action="store_true", help="Use the official test runner")
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
    run_db = args.db or args.all
    run_api = args.api or args.all
    run_frontend = args.frontend or args.all
    run_integration = args.integration or args.all
    
    # If no specific tests are selected, run all
    if not (run_db or run_api or run_frontend or run_integration or args.official):
        run_db = run_api = run_frontend = run_integration = True
    
    # Track test results
    results = {}
    
    # Run tests based on mode and selection
    if args.official and not demo_mode:
        # Use the official test runner in PostgreSQL mode
        test_types = []
        if args.api:
            test_types.append("api")
        if args.frontend:
            test_types.append("frontend")
        if args.integration:
            test_types.append("integration")
        if args.all or not test_types:
            test_types = ["api", "frontend", "integration"]
        
        results["official"] = run_official_tests(test_types, args.verbose)
    else:
        # Run individual test categories
        if run_db:
            results["db"] = run_db_tests(demo_mode)
        
        if run_api:
            results["api"] = run_api_tests(demo_mode)
        
        if run_frontend:
            results["frontend"] = run_frontend_tests(demo_mode)
        
        if run_integration:
            results["integration"] = run_integration_tests(demo_mode)
    
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
