"""
Comprehensive test runner for Pine Time App.
Implements robust error handling and fallback mechanisms as per project guidelines.
"""

import os
import sys
import argparse
import subprocess
import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("comprehensive_test_runner")

def safe_api_call(func_name: str, *args, **kwargs) -> Dict[str, Any]:
    """
    Safely execute an API call with proper error handling.
    
    Args:
        func_name: Name of the function being called (for logging)
        *args: Positional arguments to pass to the function
        **kwargs: Keyword arguments to pass to the function
        
    Returns:
        Dict[str, Any]: Result with success flag and data or error message
    """
    try:
        result = {"success": True, "data": None, "error": None}
        # Execute the actual function call
        result["data"] = kwargs.get("func", lambda: None)(*args)
        return result
    except Exception as e:
        logger.error(f"Error in {func_name}: {str(e)}")
        return {"success": False, "data": None, "error": str(e)}

def run_pytest(test_paths: List[str], options: List[str], max_retries: int = 2) -> Dict[str, Any]:
    """
    Run pytest with the specified test paths and options with retry logic.
    
    Args:
        test_paths: List of test paths to run
        options: List of pytest options
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dict[str, Any]: Result with success flag, exit code, and output
    """
    # Build command
    cmd = ["pytest"] + options + test_paths
    
    # Log command
    logger.info(f"Running command: {' '.join(cmd)}")
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}/{max_retries}")
                time.sleep(2)  # Add delay between retries
                
            # Run pytest
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Log output
            logger.info(result.stdout)
            if result.stderr:
                logger.error(result.stderr)
            
            # Return result
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            logger.error(f"Error running pytest: {str(e)}")
            if attempt == max_retries:
                return {
                    "success": False,
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": str(e)
                }

def run_locust(host: str, users: int, spawn_rate: int, run_time: str, max_retries: int = 2) -> Dict[str, Any]:
    """
    Run locust load tests with retry logic.
    
    Args:
        host: Host to test
        users: Number of users to simulate
        spawn_rate: Rate at which to spawn users
        run_time: How long to run the test
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dict[str, Any]: Result with success flag, exit code, and output
    """
    # Build command
    report_file = f"load_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    cmd = [
        "locust",
        "-f", "tests/load/load_test.py",
        "--host", host,
        "--headless",
        "-u", str(users),
        "-r", str(spawn_rate),
        "--run-time", run_time,
        "--html", report_file
    ]
    
    # Log command
    logger.info(f"Running command: {' '.join(cmd)}")
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}/{max_retries}")
                time.sleep(2)  # Add delay between retries
                
            # Run locust
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Log output
            logger.info(result.stdout)
            if result.stderr:
                logger.error(result.stderr)
            
            # Return result
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "report_file": report_file if result.returncode == 0 else None
            }
        except Exception as e:
            logger.error(f"Error running locust: {str(e)}")
            if attempt == max_retries:
                return {
                    "success": False,
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": str(e),
                    "report_file": None
                }

def run_streamlit_tests(test_paths: List[str], options: List[str], max_retries: int = 2) -> Dict[str, Any]:
    """
    Run Streamlit frontend tests with retry logic.
    
    Args:
        test_paths: List of test paths to run
        options: List of pytest options
        max_retries: Maximum number of retry attempts
        
    Returns:
        Dict[str, Any]: Result with success flag, exit code, and output
    """
    # Set environment variable for testing mode
    os.environ["STREAMLIT_TEST_MODE"] = "True"
    
    # Build command
    cmd = ["pytest"] + options + test_paths
    
    # Log command
    logger.info(f"Running Streamlit tests: {' '.join(cmd)}")
    
    for attempt in range(max_retries + 1):
        try:
            if attempt > 0:
                logger.info(f"Retry attempt {attempt}/{max_retries}")
                time.sleep(2)  # Add delay between retries
                
            # Run pytest for Streamlit tests
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Log output
            logger.info(result.stdout)
            if result.stderr:
                logger.error(result.stderr)
            
            # Return result
            return {
                "success": result.returncode == 0,
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            logger.error(f"Error running Streamlit tests: {str(e)}")
            if attempt == max_retries:
                return {
                    "success": False,
                    "exit_code": -1,
                    "stdout": "",
                    "stderr": str(e)
                }

def check_api_server(host: str = "http://localhost:8000", timeout: int = 5) -> bool:
    """
    Check if the API server is running.
    
    Args:
        host: API server host
        timeout: Connection timeout in seconds
        
    Returns:
        bool: True if API server is running, False otherwise
    """
    import requests
    
    try:
        logger.info(f"Checking API server at {host}")
        response = requests.get(f"{host}/health", timeout=timeout)
        if response.status_code == 200:
            logger.info("API server is running")
            return True
        else:
            logger.warning(f"API server returned status code {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        logger.warning(f"API server check failed: {str(e)}")
        return False

def check_database_connection() -> bool:
    """
    Check if the database connection is working.
    
    Returns:
        bool: True if database connection is working, False otherwise
    """
    try:
        # Import here to avoid circular imports
        from admin_dashboard.utils.db import test_database_connection
        
        logger.info("Checking database connection")
        result = test_database_connection()
        if result:
            logger.info(f"Database connection successful: {result}")
            return True
        else:
            logger.warning("Database connection failed")
            return False
    except Exception as e:
        logger.warning(f"Database connection check failed: {str(e)}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run comprehensive tests for Pine Time App")
    
    # Test selection
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--frontend", action="store_true", help="Run frontend tests")
    parser.add_argument("--load", action="store_true", help="Run load tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--demo-mode", action="store_true", help="Enable demo mode for testing")
    
    # Pytest options
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-x", "--exitfirst", action="store_true", help="Exit on first failure")
    parser.add_argument("--no-header", action="store_true", help="Don't show pytest header")
    parser.add_argument("--tb", choices=["auto", "long", "short", "line", "native", "no"], default="short", help="Traceback print mode")
    
    # Load test options
    parser.add_argument("--host", default="http://localhost:8000", help="Host to test (for load tests)")
    parser.add_argument("--users", type=int, default=10, help="Number of users to simulate (for load tests)")
    parser.add_argument("--spawn-rate", type=int, default=1, help="Rate at which to spawn users (for load tests)")
    parser.add_argument("--run-time", default="1m", help="How long to run the test (for load tests)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Enable demo mode if requested
    if args.demo_mode:
        os.environ["PINE_TIME_DEMO_MODE"] = "True"
        logger.info("Demo mode enabled for testing")
    
    # Check API server and database connection
    api_server_running = check_api_server(args.host)
    db_connection_working = check_database_connection()
    
    if not api_server_running:
        logger.warning("API server is not running or not accessible")
        if not args.demo_mode:
            logger.warning("Consider enabling demo mode with --demo-mode")
    
    if not db_connection_working:
        logger.warning("Database connection is not working")
        if not args.demo_mode:
            logger.warning("Consider enabling demo mode with --demo-mode")
    
    # Build pytest options
    pytest_options = []
    if args.verbose:
        pytest_options.append("-v")
    if args.exitfirst:
        pytest_options.append("-x")
    if args.no_header:
        pytest_options.append("--no-header")
    pytest_options.append(f"--tb={args.tb}")
    
    # Determine which tests to run
    test_paths = []
    
    if args.all or (not args.api and not args.integration and not args.frontend and not args.load):
        # Run all tests except load tests by default
        test_paths = ["tests/api", "tests/integration", "tests/frontend"]
        run_load = args.all or args.load
    else:
        # Run specific tests
        if args.api:
            test_paths.append("tests/api")
        if args.integration:
            test_paths.append("tests/integration")
        if args.frontend:
            test_paths.append("tests/frontend")
        run_load = args.load
    
    # Track overall success
    overall_success = True
    
    # Run pytest tests
    if test_paths:
        for test_path in test_paths:
            logger.info(f"Running tests: {test_path}")
            
            if "integration" in test_path:
                logger.info("Running integration tests")
                result = run_pytest([test_path], pytest_options)
                if not result["success"]:
                    logger.error(f"Integration tests failed with exit code {result['exit_code']}")
                    overall_success = False
            elif "frontend" in test_path:
                logger.info("Running frontend tests")
                result = run_streamlit_tests([test_path], pytest_options)
                if not result["success"]:
                    logger.error(f"Frontend tests failed with exit code {result['exit_code']}")
                    overall_success = False
            else:
                logger.info(f"Running {test_path} tests")
                result = run_pytest([test_path], pytest_options)
                if not result["success"]:
                    logger.error(f"Tests in {test_path} failed with exit code {result['exit_code']}")
                    overall_success = False
    
    # Run load tests
    if run_load:
        logger.info("Running load tests")
        result = run_locust(args.host, args.users, args.spawn_rate, args.run_time)
        
        if not result["success"]:
            logger.error(f"Load tests failed with exit code {result['exit_code']}")
            overall_success = False
        else:
            logger.info(f"Load test report generated: {result['report_file']}")
    
    if overall_success:
        logger.info("All tests completed successfully")
        return 0
    else:
        logger.error("Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
