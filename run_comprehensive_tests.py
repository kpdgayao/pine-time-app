"""
Comprehensive Test Runner for Pine Time App.
Runs all tests with appropriate configuration and demo mode enabled.
"""

import os
import sys
import subprocess
import logging
import shutil
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"comprehensive_test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("comprehensive_test_runner")

def setup_test_environment():
    """Set up the test environment with proper configuration."""
    # Set environment variables for testing
    os.environ["DEMO_MODE"] = "true"
    os.environ["API_BASE_URL"] = "http://localhost:8000"
    
    # Use the fixed test file
    fixed_test_file = Path("tests/frontend/test_streamlit_app_fixed.py")
    original_test_file = Path("tests/frontend/test_streamlit_app.py")
    
    if fixed_test_file.exists():
        logger.info("Using fixed test file for Streamlit tests")
        # Create a backup of the original file if it doesn't exist
        backup_file = Path("tests/frontend/test_streamlit_app.py.bak")
        if not backup_file.exists() and original_test_file.exists():
            shutil.copy2(original_test_file, backup_file)
            logger.info(f"Created backup of original test file at {backup_file}")
        
        # Replace the original file with the fixed version
        shutil.copy2(fixed_test_file, original_test_file)
        logger.info(f"Replaced {original_test_file} with fixed version")
    else:
        logger.warning("Fixed test file not found, using original test file")

def run_frontend_tests():
    """Run frontend tests with demo mode enabled."""
    logger.info("Running frontend tests in demo mode")
    
    cmd = [
        "pytest",
        "-v",
        "--tb=short",
        "tests/frontend"
    ]
    
    logger.info(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    
    return result.returncode == 0

def run_api_tests():
    """Run API tests with demo mode enabled."""
    logger.info("Running API tests in demo mode")
    
    cmd = [
        "pytest",
        "-v",
        "--tb=short",
        "tests/api"
    ]
    
    logger.info(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    
    return result.returncode == 0

def run_integration_tests():
    """Run integration tests with demo mode enabled."""
    logger.info("Running integration tests in demo mode")
    
    cmd = [
        "pytest",
        "-v",
        "--tb=short",
        "tests/integration"
    ]
    
    logger.info(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    
    return result.returncode == 0

def run_utility_tests():
    """Run utility tests."""
    logger.info("Running utility tests")
    
    cmd = [
        "pytest",
        "-v",
        "--tb=short",
        "tests/test_api_client.py",
        "tests/test_connection_utils.py",
        "tests/test_db_utils.py",
        "tests/test_safe_api_handling.py"
    ]
    
    logger.info(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    
    return result.returncode == 0

def main():
    """Main function to run comprehensive tests."""
    logger.info("Starting comprehensive test run")
    
    # Set up test environment
    setup_test_environment()
    
    # Track test results
    results = {
        "frontend": False,
        "api": False,
        "integration": False,
        "utility": False
    }
    
    # Run tests
    results["frontend"] = run_frontend_tests()
    results["api"] = run_api_tests()
    results["integration"] = run_integration_tests()
    results["utility"] = run_utility_tests()
    
    # Print summary
    logger.info("=== Comprehensive Test Results ===")
    for test_type, success in results.items():
        status = "PASSED" if success else "FAILED"
        logger.info(f"{test_type.upper()} Tests: {status}")
    
    # Overall result
    if all(results.values()):
        logger.info("All tests passed successfully!")
        return 0
    else:
        logger.error("Some tests failed. See log for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
