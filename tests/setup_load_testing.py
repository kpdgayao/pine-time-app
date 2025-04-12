#!/usr/bin/env python
"""
Setup script for load testing with Locust.
Installs required dependencies and configures the environment.
"""

import os
import sys
import subprocess
import logging
from typing import List, Optional
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("setup_load_testing")

def install_dependencies() -> bool:
    """
    Install required dependencies for load testing.
    
    Returns:
        bool: True if installation was successful, False otherwise
    """
    dependencies = [
        "locust>=2.15.0",
        "python-dotenv>=1.0.0",
        "requests>=2.28.0",
        "psycopg2-binary>=2.9.5"  # For PostgreSQL connection testing
    ]
    
    logger.info("Installing load testing dependencies...")
    
    try:
        # Install dependencies
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + dependencies)
        logger.info("Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        return False

def create_env_file() -> bool:
    """
    Create or update .env file with load testing configuration.
    
    Returns:
        bool: True if file was created/updated successfully, False otherwise
    """
    env_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env")
    
    # Load existing .env file if it exists
    env_vars = {}
    if os.path.exists(env_file_path):
        logger.info(f"Loading existing .env file from {env_file_path}")
        with open(env_file_path, "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    env_vars[key.strip()] = value.strip()
    
    # Add or update load testing configuration
    load_test_vars = {
        "API_BASE_URL": env_vars.get("API_BASE_URL", "http://localhost:8000"),
        "LOAD_TEST_MIN_WAIT": env_vars.get("LOAD_TEST_MIN_WAIT", "1"),
        "LOAD_TEST_MAX_WAIT": env_vars.get("LOAD_TEST_MAX_WAIT", "5"),
        "LOAD_TEST_USER_COUNT": env_vars.get("LOAD_TEST_USER_COUNT", "10"),
        "LOAD_TEST_SPAWN_RATE": env_vars.get("LOAD_TEST_SPAWN_RATE", "2"),
        "TOKEN_REFRESH_INTERVAL": env_vars.get("TOKEN_REFRESH_INTERVAL", "1800"),
        "AUTH_RETRY_ATTEMPTS": env_vars.get("AUTH_RETRY_ATTEMPTS", "3"),
        "AUTH_RETRY_DELAY": env_vars.get("AUTH_RETRY_DELAY", "2")
    }
    
    # Update env_vars with load_test_vars
    env_vars.update(load_test_vars)
    
    # Write to .env file
    try:
        with open(env_file_path, "w") as f:
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        
        logger.info(f"Load testing configuration written to {env_file_path}")
        return True
    except Exception as e:
        logger.error(f"Failed to write .env file: {e}")
        return False

def verify_installation() -> bool:
    """
    Verify that Locust is installed correctly.
    
    Returns:
        bool: True if verification was successful, False otherwise
    """
    try:
        # Check if locust is installed
        result = subprocess.run(
            ["locust", "--version"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info(f"Locust installed: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logger.error(f"Locust verification failed: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Setup load testing environment")
    parser.add_argument("--skip-install", action="store_true", help="Skip dependency installation")
    parser.add_argument("--skip-env", action="store_true", help="Skip .env file creation/update")
    parser.add_argument("--api-url", type=str, help="API base URL (e.g., http://localhost:8000)")
    parser.add_argument("--users", type=int, help="Number of users to simulate")
    parser.add_argument("--spawn-rate", type=int, help="Users per second to spawn")
    
    args = parser.parse_args()
    
    # Install dependencies
    if not args.skip_install:
        if not install_dependencies():
            logger.error("Failed to install dependencies")
            return 1
    
    # Create/update .env file
    if not args.skip_env:
        # Update environment variables from command line arguments
        env_vars = {}
        if args.api_url:
            env_vars["API_BASE_URL"] = args.api_url
        if args.users:
            env_vars["LOAD_TEST_USER_COUNT"] = str(args.users)
        if args.spawn_rate:
            env_vars["LOAD_TEST_SPAWN_RATE"] = str(args.spawn_rate)
        
        # Create/update .env file
        if not create_env_file():
            logger.error("Failed to create/update .env file")
            return 1
    
    # Verify installation
    if not verify_installation():
        logger.error("Failed to verify Locust installation")
        return 1
    
    logger.info("Load testing environment setup completed successfully")
    logger.info("To run load tests, use:")
    logger.info("  locust -f tests/load/load_test.py --host=http://localhost:8000")
    logger.info("  or")
    logger.info("  python tests/run_tests.py --load --host=http://localhost:8000 --users=10 --spawn-rate=2 --run-time=1m")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
