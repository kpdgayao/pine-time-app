"""
Test runner for Pine Time App.
Implements robust error handling and follows project guidelines.
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("test_runner")

def run_command(cmd: List[str], cwd: Optional[str] = None) -> Dict[str, Any]:
    """
    Run a command and return the result.
    
    Args:
        cmd: Command to run
        cwd: Working directory
        
    Returns:
        Dict[str, Any]: Command result
    """
    try:
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
        
        # Log output
        logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)
        
        return {
            "success": result.returncode == 0,
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    except Exception as e:
        logger.error(f"Error running command: {str(e)}")
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": str(e)
        }

def run_integration_tests(verbose: bool = False) -> Dict[str, Any]:
    """
    Run integration tests.
    
    Args:
        verbose: Whether to enable verbose output
        
    Returns:
        Dict[str, Any]: Test results
    """
    logger.info("Running integration tests")
    
    # Set demo mode for testing
    os.environ["PINE_TIME_DEMO_MODE"] = "True"
    
    # Build command
    cmd = ["pytest"]
    if verbose:
        cmd.append("-v")
    cmd.append("--tb=short")
    cmd.append("tests/integration")
    
    # Run command
    return run_command(cmd)

def run_ui_tests(verbose: bool = False) -> Dict[str, Any]:
    """
    Run UI tests.
    
    Args:
        verbose: Whether to enable verbose output
        
    Returns:
        Dict[str, Any]: Test results
    """
    logger.info("Running UI tests")
    
    # Set demo mode for testing
    os.environ["PINE_TIME_DEMO_MODE"] = "True"
    os.environ["STREAMLIT_TEST_MODE"] = "True"
    
    # Build command
    cmd = ["pytest"]
    if verbose:
        cmd.append("-v")
    cmd.append("--tb=short")
    cmd.append("tests/frontend")
    
    # Run command
    return run_command(cmd)

def run_load_tests(host: str = "http://localhost:8000", users: int = 5, 
                  spawn_rate: int = 1, run_time: str = "30s") -> Dict[str, Any]:
    """
    Run load tests.
    
    Args:
        host: Host to test
        users: Number of users to simulate
        spawn_rate: Rate at which to spawn users
        run_time: How long to run the test
        
    Returns:
        Dict[str, Any]: Test results
    """
    logger.info("Running load tests")
    
    # Check if locust is installed
    locust_check = run_command(["locust", "--version"])
    if not locust_check["success"]:
        logger.error("Locust is not installed or not in PATH")
        return {
            "success": False,
            "exit_code": -1,
            "stdout": "",
            "stderr": "Locust is not installed or not in PATH"
        }
    
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
    
    # Run command
    result = run_command(cmd)
    
    # Add report file to result if successful
    if result["success"]:
        result["report_file"] = report_file
    
    return result

def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run tests for Pine Time App")
    
    # Test selection
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--ui", action="store_true", help="Run UI tests")
    parser.add_argument("--load", action="store_true", help="Run load tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    # Test options
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    
    # Load test options
    parser.add_argument("--host", default="http://localhost:8000", help="Host to test (for load tests)")
    parser.add_argument("--users", type=int, default=5, help="Number of users to simulate (for load tests)")
    parser.add_argument("--spawn-rate", type=int, default=1, help="Rate at which to spawn users (for load tests)")
    parser.add_argument("--run-time", default="30s", help="How long to run the test (for load tests)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Track overall success
    overall_success = True
    
    # Run tests
    if args.all or args.integration:
        logger.info("Running integration tests")
        integration_result = run_integration_tests(verbose=args.verbose)
        if not integration_result["success"]:
            logger.error("Integration tests failed")
            overall_success = False
    
    if args.all or args.ui:
        logger.info("Running UI tests")
        ui_result = run_ui_tests(verbose=args.verbose)
        if not ui_result["success"]:
            logger.error("UI tests failed")
            overall_success = False
    
    if args.all or args.load:
        logger.info("Running load tests")
        load_result = run_load_tests(
            host=args.host,
            users=args.users,
            spawn_rate=args.spawn_rate,
            run_time=args.run_time
        )
        if not load_result["success"]:
            logger.error("Load tests failed")
            overall_success = False
    
    if overall_success:
        logger.info("All tests completed successfully")
        return 0
    else:
        logger.error("Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
