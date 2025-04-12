"""
Hybrid Test Runner for Pine Time App

This script provides a balanced approach to testing the Pine Time application,
supporting both proper PostgreSQL-based testing and demo mode fallbacks.

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
        logging.FileHandler(f"hybrid_test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("hybrid_test_runner")

def test_database_connection() -> bool:
    """
    Test connection to PostgreSQL database with proper error handling.
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        # Import here to avoid circular imports
        from admin_dashboard.utils.db import test_database_connection as db_test_connection
        
        # Test the connection with a timeout
        result = db_test_connection()
        
        if result:
            logger.info("PostgreSQL database connection successful")
            return True
        else:
            logger.warning("PostgreSQL database connection failed")
            return False
    except Exception as e:
        logger.error(f"Error testing database connection: {str(e)}")
        return False

def load_test_environment() -> Dict[str, str]:
    """
    Load test environment variables with validation of required parameters.
    
    Returns:
        Dict[str, str]: Environment variables
    """
    # Load test environment from .env.test file
    env_file = Path("tests/.env.test")
    if env_file.exists():
        logger.info(f"Loading test environment from {env_file}")
        load_dotenv(env_file)
    else:
        logger.warning(f"Test environment file {env_file} not found")
    
    # Get environment variables
    env_vars = {
        "DEMO_MODE": os.getenv("DEMO_MODE", "false").lower() in ("true", "1", "yes"),
        "DATABASE_TYPE": os.getenv("DATABASE_TYPE", "postgresql"),
        "POSTGRES_SERVER": os.getenv("POSTGRES_SERVER", "localhost"),
        "POSTGRES_PORT": os.getenv("POSTGRES_PORT", "5432"),
        "POSTGRES_USER": os.getenv("POSTGRES_USER", "postgres"),
        "POSTGRES_PASSWORD": os.getenv("POSTGRES_PASSWORD", "postgres"),
        "POSTGRES_DB": os.getenv("POSTGRES_DB", "pine_time"),
        "TEST_ADMIN_USERNAME": os.getenv("TEST_ADMIN_USERNAME", "testadmin"),
        "TEST_ADMIN_PASSWORD": os.getenv("TEST_ADMIN_PASSWORD", "testadminpassword"),
        "TEST_ADMIN_EMAIL": os.getenv("TEST_ADMIN_EMAIL", "testadmin@example.com")
    }
    
    # Log environment (without sensitive information)
    safe_env = env_vars.copy()
    if "POSTGRES_PASSWORD" in safe_env:
        safe_env["POSTGRES_PASSWORD"] = "********"
    if "TEST_ADMIN_PASSWORD" in safe_env:
        safe_env["TEST_ADMIN_PASSWORD"] = "********"
    
    logger.info(f"Test environment: {safe_env}")
    
    return env_vars

def run_test_command(cmd: List[str], description: str) -> Tuple[bool, str]:
    """
    Run a test command with proper error handling and logging.
    
    Args:
        cmd: Command to run
        description: Description of the test
        
    Returns:
        Tuple[bool, str]: Success flag and output
    """
    logger.info(f"Running {description}...")
    logger.info(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Log output with appropriate severity
        if result.stdout:
            logger.info(f"Test output:\n{result.stdout}")
        if result.stderr:
            logger.error(f"Test errors:\n{result.stderr}")
        
        success = result.returncode == 0
        if success:
            logger.info(f"{description} PASSED")
        else:
            logger.error(f"{description} FAILED")
        
        return success, result.stdout
    except Exception as e:
        logger.error(f"Error running {description}: {str(e)}")
        return False, str(e)

def run_tests_with_official_runner(test_types: List[str], verbose: bool = False) -> bool:
    """
    Run tests using the official test runner with proper error handling.
    
    Args:
        test_types: List of test types to run
        verbose: Whether to enable verbose output
        
    Returns:
        bool: True if all tests passed, False otherwise
    """
    # Build command
    cmd = ["python", "tests/run_tests.py"]
    
    # Add test types
    for test_type in test_types:
        cmd.append(f"--{test_type}")
    
    # Add verbose flag
    if verbose:
        cmd.append("--verbose")
    
    # Run command
    success, _ = run_test_command(cmd, "Official Test Runner")
    return success

def run_core_tests() -> bool:
    """
    Run core functionality tests with proper error handling.
    
    Returns:
        bool: True if tests passed, False otherwise
    """
    cmd = ["pytest", "-xvs", "test_pine_time_core.py"]
    success, _ = run_test_command(cmd, "Core Functionality Tests")
    return success

def run_specific_tests(test_path: str, description: str) -> bool:
    """
    Run specific tests with proper error handling.
    
    Args:
        test_path: Path to test file or directory
        description: Description of the tests
        
    Returns:
        bool: True if tests passed, False otherwise
    """
    cmd = ["pytest", "-xvs", test_path]
    success, _ = run_test_command(cmd, description)
    return success

def main() -> int:
    """
    Main function with comprehensive error handling and validation.
    
    Returns:
        int: Exit code
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Hybrid Test Runner for Pine Time App")
    parser.add_argument("--demo", action="store_true", help="Force demo mode")
    parser.add_argument("--postgres", action="store_true", help="Force PostgreSQL mode")
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--frontend", action="store_true", help="Run frontend tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()
    
    # Load test environment
    env_vars = load_test_environment()
    
    # Determine test mode
    use_demo_mode = args.demo or (env_vars["DEMO_MODE"] and not args.postgres)
    
    # Set environment variables
    if use_demo_mode:
        os.environ["DEMO_MODE"] = "true"
        logger.info("Running tests in DEMO MODE")
    else:
        os.environ["DEMO_MODE"] = "false"
        logger.info("Running tests in POSTGRESQL MODE")
    
    # Test database connection if not in demo mode
    if not use_demo_mode:
        db_connected = test_database_connection()
        if not db_connected:
            logger.warning("PostgreSQL connection failed. Falling back to demo mode.")
            os.environ["DEMO_MODE"] = "true"
            use_demo_mode = True
    
    # Determine which tests to run
    test_types = []
    if args.api:
        test_types.append("api")
    if args.frontend:
        test_types.append("frontend")
    if args.integration:
        test_types.append("integration")
    if args.all or not test_types:
        test_types = ["api", "frontend", "integration"]
    
    # Track test results
    results = {}
    
    # Always run core tests first
    results["core"] = run_core_tests()
    
    # Run tests based on mode
    if use_demo_mode:
        # In demo mode, run specific tests that work with demo mode
        if "frontend" in test_types:
            results["frontend_demo"] = run_specific_tests(
                "tests/frontend/test_streamlit_app.py::test_demo_mode",
                "Frontend Demo Tests"
            )
        
        if "api" in test_types:
            results["api_demo"] = run_specific_tests(
                "tests/api/test_auth_api.py::test_demo_mode_login",
                "API Demo Tests"
            )
    else:
        # In PostgreSQL mode, use the official test runner
        official_runner_result = run_tests_with_official_runner(test_types, args.verbose)
        results["official"] = official_runner_result
    
    # Print summary
    logger.info("\n=== Pine Time App Test Results ===")
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
