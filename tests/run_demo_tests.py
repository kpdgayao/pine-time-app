"""
Demo Mode Test Runner for Pine Time App.
Runs tests with demo mode enabled to bypass API connection requirements.
"""

import os
import sys
import subprocess
import logging
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"demo_test_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("demo_test_runner")

def main():
    """Main function to run tests in demo mode."""
    # Set environment variables for demo mode
    os.environ["DEMO_MODE"] = "true"
    os.environ["API_BASE_URL"] = "http://localhost:8000"  # This won't be used in demo mode
    
    logger.info("Running tests in demo mode")
    
    # Build command to run tests
    cmd = [
        "pytest",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback
        "tests/frontend/test_streamlit_app.py::test_demo_mode",  # Start with demo mode test
    ]
    
    # Log command
    logger.info(f"Running command: {' '.join(cmd)}")
    
    # Run tests
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Log output
    logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    
    logger.info(f"Test completed with exit code: {result.returncode}")
    
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
