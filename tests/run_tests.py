"""
Test runner for Pine Time App.
Provides a convenient way to run all tests or specific test categories.
"""

import os
import sys
import argparse
import subprocess
import logging
from typing import List, Optional
from datetime import datetime

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

def run_pytest(test_paths: List[str], options: List[str]) -> int:
    """
    Run pytest with the specified test paths and options.
    
    Args:
        test_paths: List of test paths to run
        options: List of pytest options
        
    Returns:
        int: Exit code from pytest
    """
    # Build command
    cmd = ["pytest"] + options + test_paths
    
    # Log command
    logger.info(f"Running command: {' '.join(cmd)}")
    
    # Run pytest
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Log output
    logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    
    # Return exit code
    return result.returncode

def run_locust(host: str, users: int, spawn_rate: int, run_time: str, headless: bool = True, web_port: Optional[int] = None) -> int:
    """
    Run locust load tests with enhanced configuration and error handling.
    
    Args:
        host: Host to test
        users: Number of users to simulate
        spawn_rate: Rate at which to spawn users
        run_time: How long to run the test
        headless: Whether to run in headless mode or with web UI
        web_port: Port for web UI (if not headless)
        
    Returns:
        int: Exit code from locust
    """
    # Create timestamp for report filenames
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_html = f"load_test_report_{timestamp}.html"
    report_csv = f"load_test_stats_{timestamp}.csv"
    log_file = f"load_test_{timestamp}.log"
    
    # Build command
    cmd = [
        "locust",
        "-f", "tests/load/pine_time_resilience_test.py",
        "--host", host,
    ]
    
    # Add mode-specific options
    if headless:
        cmd.extend([
            "--headless",
            "-u", str(users),
            "-r", str(spawn_rate),
            "--run-time", run_time,
            "--html", report_html,
            "--csv", report_csv.replace(".csv", ""),  # Locust adds .csv extension
            "--logfile", log_file
        ])
    else:
        cmd.extend([
            "--web-host", "127.0.0.1"
        ])
        if web_port:
            cmd.extend(["--web-port", str(web_port)])
    
    # Log command
    logger.info(f"Running command: {' '.join(cmd)}")
    
    try:
        # First check if locust is installed
        subprocess.run(["locust", "--version"], check=True, capture_output=True, text=True)
        
        # Run locust
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Log output
        logger.info(result.stdout)
        if result.stderr:
            logger.error(result.stderr)
        
        # Provide summary of results if headless mode
        if headless and result.returncode == 0:
            logger.info(f"Load test completed successfully. Reports saved to:")
            logger.info(f"  HTML report: {report_html}")
            logger.info(f"  CSV stats: {report_csv}")
            logger.info(f"  Log file: {log_file}")
        elif not headless and result.returncode == 0:
            logger.info(f"Locust web interface started. Open http://127.0.0.1:{web_port or 8089} in your browser.")
        
        # Return exit code
        return result.returncode
    except FileNotFoundError:
        logger.error("Locust not found. Please install it with: pip install locust")
        logger.info("You can also run: python tests/setup_load_testing.py to set up the load testing environment")
        return 1
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking locust version: {e}")
        return 1

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run tests for Pine Time App")
    
    # Test selection
    parser.add_argument("--api", action="store_true", help="Run API tests")
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--frontend", action="store_true", help="Run frontend tests")
    parser.add_argument("--load", action="store_true", help="Run load tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    # Pytest options
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-x", "--exitfirst", action="store_true", help="Exit on first failure")
    parser.add_argument("--no-header", action="store_true", help="Don't show pytest header")
    parser.add_argument("--tb", choices=["auto", "long", "short", "line", "native", "no"], default="auto", help="Traceback print mode")
    
    # Load test options
    parser.add_argument("--host", default="http://localhost:8000", help="Host to test (for load tests)")
    parser.add_argument("--users", type=int, default=10, help="Number of users to simulate (for load tests)")
    parser.add_argument("--spawn-rate", type=int, default=1, help="Rate at which to spawn users (for load tests)")
    parser.add_argument("--run-time", default="1m", help="How long to run the test (for load tests)")
    parser.add_argument("--web-ui", action="store_true", help="Run Locust with web UI instead of headless mode")
    parser.add_argument("--web-port", type=int, default=8089, help="Port for Locust web UI")
    parser.add_argument("--setup-load-test", action="store_true", help="Run setup_load_testing.py before load tests")
    
    # Parse arguments
    args = parser.parse_args()
    
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
    
    # Run pytest tests
    if test_paths:
        logger.info(f"Running tests: {', '.join(test_paths)}")
        exit_code = run_pytest(test_paths, pytest_options)
        
        if exit_code != 0:
            logger.error(f"Tests failed with exit code {exit_code}")
            return exit_code
    
    # Run load tests
    if run_load:
        logger.info("Running load tests")
        
        # Run setup_load_testing.py if requested
        if args.setup_load_test:
            logger.info("Setting up load testing environment")
            setup_cmd = [sys.executable, "tests/setup_load_testing.py"]
            if args.host:
                setup_cmd.extend(["--api-url", args.host])
            if args.users:
                setup_cmd.extend(["--users", str(args.users)])
            if args.spawn_rate:
                setup_cmd.extend(["--spawn-rate", str(args.spawn_rate)])
            
            setup_result = subprocess.run(setup_cmd, capture_output=True, text=True)
            if setup_result.returncode != 0:
                logger.error(f"Failed to set up load testing environment: {setup_result.stderr}")
                return setup_result.returncode
            else:
                logger.info("Load testing environment set up successfully")
        
        # Run load tests
        exit_code = run_locust(
            host=args.host,
            users=args.users,
            spawn_rate=args.spawn_rate,
            run_time=args.run_time,
            headless=not args.web_ui,
            web_port=args.web_port
        )
        
        if exit_code != 0:
            logger.error(f"Load tests failed with exit code {exit_code}")
            return exit_code
        elif not args.web_ui:
            logger.info(f"Load tests completed successfully with {args.users} users at {args.spawn_rate} users/sec for {args.run_time}")
        else:
            logger.info(f"Locust web UI started at http://127.0.0.1:{args.web_port}")
    
    logger.info("All tests completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())