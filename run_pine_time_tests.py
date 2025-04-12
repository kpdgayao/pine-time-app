"""
Pine Time App Comprehensive Test Runner

This script runs tests for the Pine Time application with proper configuration
for demo mode, which bypasses the need for actual PostgreSQL connections.

Features:
- Enables demo mode for all tests
- Focuses on testing core functionality
- Handles missing dependencies
- Provides detailed logging
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"pine_time_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("pine_time_test_runner")

def run_test(test_path, description):
    """Run a specific test with proper environment setup."""
    logger.info(f"Running {description}...")
    
    # Set environment variables for demo mode
    os.environ["DEMO_MODE"] = "true"
    
    # Run the test
    cmd = ["pytest", "-xvs", test_path]
    logger.info(f"Command: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Log the output
    if result.stdout:
        logger.info(f"Test output:\n{result.stdout}")
    if result.stderr:
        logger.error(f"Test errors:\n{result.stderr}")
    
    # Return success/failure
    if result.returncode == 0:
        logger.info(f"{description} PASSED")
        return True
    else:
        logger.error(f"{description} FAILED")
        return False

def main():
    """Main function to run Pine Time app tests."""
    logger.info("Starting Pine Time app tests in demo mode")
    
    # Ensure demo mode is enabled
    os.environ["DEMO_MODE"] = "true"
    
    # Track test results
    results = {}
    
    # Test 1: Verify demo mode is enabled
    results["demo_mode"] = run_test(
        "test_pine_time_demo.py::test_demo_mode_enabled",
        "Demo Mode Verification"
    )
    
    # If demo mode is working, run the core functionality tests
    if results["demo_mode"]:
        # Test 2: Test login with demo credentials
        results["login"] = run_test(
            "test_pine_time_demo.py::test_login_demo_credentials",
            "Demo Login Test"
        )
        
        # Test 3: Test events API with demo data
        results["events"] = run_test(
            "test_pine_time_demo.py::test_get_events_demo_data",
            "Events API Test"
        )
        
        # Test 4: Test badges API with demo data
        results["badges"] = run_test(
            "test_pine_time_demo.py::test_get_badges_demo_data",
            "Badges API Test"
        )
        
        # Test 5: Test connection fallback decorator
        results["fallback"] = run_test(
            "test_pine_time_demo.py::test_connection_fallback_decorator",
            "Connection Fallback Test"
        )
        
        # Test 6: Test connection verification in demo mode
        results["connection"] = run_test(
            "test_pine_time_demo.py::test_verify_connection_demo_mode",
            "Connection Verification Test"
        )
    
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
