"""
Pine Time Test Suite
A robust testing framework for the Pine Time application that follows project guidelines:
- Comprehensive error handling and logging
- Graceful degradation when services are unavailable
- Support for both PostgreSQL and demo mode testing
- Proper API response format handling
"""

import os
import sys
import logging
import argparse
import subprocess
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"pine_time_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("pine_time_test_suite")

# Add project root to path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import project modules (with try/except for graceful degradation)
try:
    from admin_dashboard.utils.db import test_database_connection, is_demo_mode
    from admin_dashboard.utils.api import APIClient, APIError
    from admin_dashboard.utils.connection import check_api_connection
except ImportError as e:
    logger.error(f"Failed to import project modules: {str(e)}")
    logger.warning("Some functionality may be limited")

class PineTimeTestRunner:
    """
    Test runner for Pine Time application with robust error handling.
    """
    
    def __init__(self, demo_mode: bool = False):
        """
        Initialize the test runner.
        
        Args:
            demo_mode: Whether to enable demo mode for testing
        """
        self.demo_mode = demo_mode
        if demo_mode:
            os.environ["PINE_TIME_DEMO_MODE"] = "True"
            logger.info("Demo mode enabled for testing")
        
        # Test results
        self.results = {
            "integration": {"success": False, "details": None},
            "ui": {"success": False, "details": None},
            "load": {"success": False, "details": None}
        }
    
    def safe_api_call(self, func_name: str, func: callable, *args, **kwargs) -> Dict[str, Any]:
        """
        Safely execute an API call with proper error handling.
        
        Args:
            func_name: Name of the function being called (for logging)
            func: Function to call
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function
            
        Returns:
            Dict[str, Any]: Result with success flag and data or error message
        """
        try:
            logger.info(f"Executing {func_name}")
            result = {"success": True, "data": None, "error": None}
            result["data"] = func(*args, **kwargs)
            return result
        except Exception as e:
            logger.error(f"Error in {func_name}: {str(e)}")
            return {"success": False, "data": None, "error": str(e)}
    
    def safe_process_run(self, cmd: List[str], cwd: Optional[str] = None, 
                        timeout: int = 300, max_retries: int = 2) -> Dict[str, Any]:
        """
        Safely run a subprocess with retry logic and proper error handling.
        
        Args:
            cmd: Command to run
            cwd: Working directory
            timeout: Timeout in seconds
            max_retries: Maximum number of retry attempts
            
        Returns:
            Dict[str, Any]: Result with success flag, exit code, and output
        """
        logger.info(f"Running command: {' '.join(cmd)}")
        
        for attempt in range(max_retries + 1):
            try:
                if attempt > 0:
                    logger.info(f"Retry attempt {attempt}/{max_retries}")
                    time.sleep(2)  # Add delay between retries
                
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    cwd=cwd,
                    timeout=timeout
                )
                
                # Log output
                if result.stdout:
                    logger.info(result.stdout)
                if result.stderr:
                    logger.error(result.stderr)
                
                return {
                    "success": result.returncode == 0,
                    "exit_code": result.returncode,
                    "stdout": result.stdout,
                    "stderr": result.stderr
                }
            except subprocess.TimeoutExpired:
                logger.error(f"Command timed out after {timeout} seconds")
                if attempt == max_retries:
                    return {
                        "success": False,
                        "exit_code": -1,
                        "stdout": "",
                        "stderr": f"Command timed out after {timeout} seconds"
                    }
            except Exception as e:
                logger.error(f"Error running command: {str(e)}")
                if attempt == max_retries:
                    return {
                        "success": False,
                        "exit_code": -1,
                        "stdout": "",
                        "stderr": str(e)
                    }
    
    def check_environment(self) -> Dict[str, bool]:
        """
        Check the testing environment.
        
        Returns:
            Dict[str, bool]: Environment status
        """
        environment = {
            "api_server": False,
            "database": False,
            "demo_mode": self.demo_mode
        }
        
        # Check API server
        try:
            api_status = self.safe_api_call(
                "check_api_connection", 
                check_api_connection if 'check_api_connection' in globals() else lambda: False
            )
            environment["api_server"] = api_status["success"] and api_status["data"]
        except Exception as e:
            logger.error(f"Error checking API server: {str(e)}")
        
        # Check database connection
        try:
            db_status = self.safe_api_call(
                "test_database_connection", 
                test_database_connection if 'test_database_connection' in globals() else lambda: False
            )
            environment["database"] = db_status["success"] and db_status["data"]
        except Exception as e:
            logger.error(f"Error checking database connection: {str(e)}")
        
        # Log environment status
        logger.info(f"Environment status: {json.dumps(environment, indent=2)}")
        
        return environment
    
    def run_integration_tests(self, verbose: bool = False, tb: str = "short") -> Dict[str, Any]:
        """
        Run integration tests with proper error handling.
        
        Args:
            verbose: Whether to enable verbose output
            tb: Traceback print mode
            
        Returns:
            Dict[str, Any]: Test results
        """
        logger.info("Running integration tests")
        
        # Build pytest options
        options = []
        if verbose:
            options.append("-v")
        options.append(f"--tb={tb}")
        
        # Run pytest
        cmd = ["pytest"] + options + ["tests/integration"]
        result = self.safe_process_run(cmd)
        
        # Store results
        self.results["integration"] = {
            "success": result["success"],
            "details": result
        }
        
        return result
    
    def run_ui_tests(self, verbose: bool = False, tb: str = "short") -> Dict[str, Any]:
        """
        Run UI tests with proper error handling.
        
        Args:
            verbose: Whether to enable verbose output
            tb: Traceback print mode
            
        Returns:
            Dict[str, Any]: Test results
        """
        logger.info("Running UI tests")
        
        # Set environment variable for testing mode
        os.environ["STREAMLIT_TEST_MODE"] = "True"
        
        # Build pytest options
        options = []
        if verbose:
            options.append("-v")
        options.append(f"--tb={tb}")
        
        # Run pytest
        cmd = ["pytest"] + options + ["tests/frontend"]
        result = self.safe_process_run(cmd)
        
        # Store results
        self.results["ui"] = {
            "success": result["success"],
            "details": result
        }
        
        return result
    
    def run_load_tests(self, host: str = "http://localhost:8000", 
                      users: int = 5, spawn_rate: int = 1, 
                      run_time: str = "30s") -> Dict[str, Any]:
        """
        Run load tests with proper error handling.
        
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
        locust_check = self.safe_process_run(["locust", "--version"])
        if not locust_check["success"]:
            logger.error("Locust is not installed or not in PATH")
            result = {
                "success": False,
                "exit_code": -1,
                "stdout": "",
                "stderr": "Locust is not installed or not in PATH",
                "error": "Missing dependency: locust"
            }
        else:
            # Build locust command
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
            
            # Run locust
            result = self.safe_process_run(cmd)
            
            # Add report file to result if successful
            if result["success"]:
                result["report_file"] = report_file
                logger.info(f"Load test report generated: {report_file}")
        
        # Store results
        self.results["load"] = {
            "success": result["success"],
            "details": result
        }
        
        return result
    
    def generate_report(self) -> str:
        """
        Generate a comprehensive test report.
        
        Returns:
            str: Test report
        """
        logger.info("Generating test report")
        
        # Check if any tests were run
        if not any(result["details"] for result in self.results.values()):
            return "No tests were run"
        
        # Build report
        report = []
        report.append("# Pine Time Test Report")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # Environment
        environment = self.check_environment()
        report.append("## Environment")
        report.append(f"- API Server: {'Available' if environment['api_server'] else 'Unavailable'}")
        report.append(f"- Database: {'Connected' if environment['database'] else 'Disconnected'}")
        report.append(f"- Demo Mode: {'Enabled' if environment['demo_mode'] else 'Disabled'}")
        report.append("")
        
        # Test results
        report.append("## Test Results")
        
        # Integration tests
        if self.results["integration"]["details"]:
            report.append("### Integration Tests")
            report.append(f"Status: {'✅ Passed' if self.results['integration']['success'] else '❌ Failed'}")
            if not self.results["integration"]["success"]:
                report.append("Errors:")
                report.append("```")
                report.append(self.results["integration"]["details"]["stderr"])
                report.append("```")
            report.append("")
        
        # UI tests
        if self.results["ui"]["details"]:
            report.append("### UI Tests")
            report.append(f"Status: {'✅ Passed' if self.results['ui']['success'] else '❌ Failed'}")
            if not self.results["ui"]["success"]:
                report.append("Errors:")
                report.append("```")
                report.append(self.results["ui"]["details"]["stderr"])
                report.append("```")
            report.append("")
        
        # Load tests
        if self.results["load"]["details"]:
            report.append("### Load Tests")
            report.append(f"Status: {'✅ Passed' if self.results['load']['success'] else '❌ Failed'}")
            if self.results["load"]["success"]:
                report.append(f"Report: {self.results['load']['details'].get('report_file', 'Not available')}")
            else:
                report.append("Errors:")
                report.append("```")
                report.append(self.results["load"]["details"]["stderr"])
                report.append("```")
            report.append("")
        
        # Summary
        report.append("## Summary")
        total_tests = sum(1 for result in self.results.values() if result["details"])
        passed_tests = sum(1 for result in self.results.values() if result["success"])
        report.append(f"Tests Run: {total_tests}")
        report.append(f"Tests Passed: {passed_tests}")
        report.append(f"Tests Failed: {total_tests - passed_tests}")
        report.append(f"Overall Status: {'✅ Passed' if passed_tests == total_tests else '❌ Failed'}")
        
        return "\n".join(report)
    
    def run_all_tests(self, verbose: bool = False, tb: str = "short", 
                     host: str = "http://localhost:8000", users: int = 5, 
                     spawn_rate: int = 1, run_time: str = "30s") -> Dict[str, Any]:
        """
        Run all tests with proper error handling.
        
        Args:
            verbose: Whether to enable verbose output
            tb: Traceback print mode
            host: Host to test for load tests
            users: Number of users to simulate for load tests
            spawn_rate: Rate at which to spawn users for load tests
            run_time: How long to run the load tests
            
        Returns:
            Dict[str, Any]: Test results
        """
        logger.info("Running all tests")
        
        # Check environment
        environment = self.check_environment()
        
        # Run integration tests
        integration_result = self.run_integration_tests(verbose, tb)
        logger.info(f"Integration tests {'passed' if integration_result['success'] else 'failed'}")
        
        # Run UI tests
        ui_result = self.run_ui_tests(verbose, tb)
        logger.info(f"UI tests {'passed' if ui_result['success'] else 'failed'}")
        
        # Run load tests
        load_result = self.run_load_tests(host, users, spawn_rate, run_time)
        logger.info(f"Load tests {'passed' if load_result['success'] else 'failed'}")
        
        # Generate report
        report = self.generate_report()
        
        # Save report
        report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, "w") as f:
            f.write(report)
        logger.info(f"Test report saved to {report_file}")
        
        # Return results
        return {
            "success": all(result["success"] for result in self.results.values() if result["details"]),
            "results": self.results,
            "report": report,
            "report_file": report_file
        }

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Run Pine Time tests with robust error handling")
    
    # Test selection
    parser.add_argument("--integration", action="store_true", help="Run integration tests")
    parser.add_argument("--ui", action="store_true", help="Run UI tests")
    parser.add_argument("--load", action="store_true", help="Run load tests")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    parser.add_argument("--demo-mode", action="store_true", help="Enable demo mode for testing")
    
    # Test options
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--tb", choices=["auto", "long", "short", "line", "native", "no"], default="short", help="Traceback print mode")
    
    # Load test options
    parser.add_argument("--host", default="http://localhost:8000", help="Host to test (for load tests)")
    parser.add_argument("--users", type=int, default=5, help="Number of users to simulate (for load tests)")
    parser.add_argument("--spawn-rate", type=int, default=1, help="Rate at which to spawn users (for load tests)")
    parser.add_argument("--run-time", default="30s", help="How long to run the test (for load tests)")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Create test runner
    runner = PineTimeTestRunner(demo_mode=args.demo_mode)
    
    # Run tests
    if args.all:
        result = runner.run_all_tests(
            verbose=args.verbose,
            tb=args.tb,
            host=args.host,
            users=args.users,
            spawn_rate=args.spawn_rate,
            run_time=args.run_time
        )
        print(result["report"])
        return 0 if result["success"] else 1
    else:
        # Run selected tests
        if args.integration:
            integration_result = runner.run_integration_tests(verbose=args.verbose, tb=args.tb)
            logger.info(f"Integration tests {'passed' if integration_result['success'] else 'failed'}")
        
        if args.ui:
            ui_result = runner.run_ui_tests(verbose=args.verbose, tb=args.tb)
            logger.info(f"UI tests {'passed' if ui_result['success'] else 'failed'}")
        
        if args.load:
            load_result = runner.run_load_tests(
                host=args.host,
                users=args.users,
                spawn_rate=args.spawn_rate,
                run_time=args.run_time
            )
            logger.info(f"Load tests {'passed' if load_result['success'] else 'failed'}")
        
        # Generate report if any tests were run
        if any(result["details"] for result in runner.results.values()):
            report = runner.generate_report()
            print(report)
            
            # Save report
            report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            with open(report_file, "w") as f:
                f.write(report)
            logger.info(f"Test report saved to {report_file}")
            
            # Return exit code
            return 0 if all(result["success"] for result in runner.results.values() if result["details"]) else 1
        else:
            logger.warning("No tests were run")
            return 0

if __name__ == "__main__":
    sys.exit(main())
