"""
Pine Time App Demo Mode Test Runner

This script runs the Pine Time app tests in demo mode, which bypasses the need for
actual API and PostgreSQL connections. This is useful for testing the core functionality
without requiring a full backend setup.
"""

import os
import sys
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"demo_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("pine_time_test_runner")

def main():
    """Run Pine Time app tests in demo mode."""
    # Set environment variables for demo mode
    os.environ["DEMO_MODE"] = "true"
    
    logger.info("Running Pine Time app tests in demo mode")
    
    # Run a simple test to verify demo mode is working
    cmd = [
        "python", "-c", 
        "import os; from admin_dashboard.utils.db import is_demo_mode; "
        "print(f'Demo mode enabled: {is_demo_mode()}')"
    ]
    
    logger.info("Verifying demo mode configuration...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    logger.info(result.stdout.strip())
    
    # Run utility tests first (these should work in demo mode)
    logger.info("Running utility tests...")
    util_cmd = ["pytest", "-xvs", "tests/test_db_utils.py::test_is_demo_mode"]
    util_result = subprocess.run(util_cmd, capture_output=True, text=True)
    
    logger.info(util_result.stdout)
    if util_result.stderr:
        logger.error(util_result.stderr)
    
    # If utility tests pass, try running frontend tests
    if util_result.returncode == 0:
        logger.info("Utility tests passed. Running frontend tests...")
        frontend_cmd = ["pytest", "-xvs", "tests/frontend"]
        frontend_result = subprocess.run(frontend_cmd, capture_output=True, text=True)
        
        logger.info(frontend_result.stdout)
        if frontend_result.stderr:
            logger.error(frontend_result.stderr)
        
        return frontend_result.returncode
    else:
        logger.error("Utility tests failed. Please check configuration.")
        return util_result.returncode

if __name__ == "__main__":
    sys.exit(main())
