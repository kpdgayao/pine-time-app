"""
Test runner for Pine Time App in Demo Mode.
Runs tests with demo mode enabled to bypass database connection requirements.
"""

import os
import sys
import subprocess
import logging
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"test_run_demo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("test_runner_demo")

def main():
    """Main function to run tests in demo mode."""
    # Load test environment variables
    env_file = os.path.join(os.path.dirname(__file__), ".env.test")
    load_dotenv(env_file)
    
    # Ensure demo mode is enabled
    os.environ["DEMO_MODE"] = "true"
    
    logger.info("Running tests in demo mode with demo mode enabled")
    
    # Build command to run tests
    cmd = [
        "pytest",
        "-v",  # Verbose output
        "--tb=short",  # Short traceback
        "tests/frontend",  # Start with frontend tests which should work in demo mode
    ]
    
    # Log command
    logger.info(f"Running command: {' '.join(cmd)}")
    
    # Run tests
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Log output
    logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)
    
    # Return exit code
    return result.returncode

if __name__ == "__main__":
    sys.exit(main())
