"""
Pine Time Application - Load Testing Runner
Provides a centralized script to run all load tests with appropriate configurations.
Follows project guidelines for proper PostgreSQL integration and API error handling.
"""

import os
import sys
import argparse
import logging
import subprocess
import json
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import load test configuration
from load_test_config import TEST_SCENARIOS, API_BASE_URL

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(f"pine_time_load_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    ]
)
logger = logging.getLogger("pine_time_load_test_runner")

def run_load_test(scenario_name: str, host: str = None, users: int = None, 
                 spawn_rate: int = None, run_time: str = None, headless: bool = True) -> int:
    """
    Run a load test scenario
    
    Args:
        scenario_name: Name of the test scenario
        host: API host URL (overrides default)
        users: Number of users to simulate (overrides default)
        spawn_rate: User spawn rate (overrides default)
        run_time: Test run time (overrides default)
        headless: Whether to run in headless mode
        
    Returns:
        int: Exit code from the load test process
    """
    # Get scenario configuration
    scenario = TEST_SCENARIOS.get(scenario_name)
    if not scenario:
        logger.error(f"Unknown test scenario: {scenario_name}")
        return 1
    
    # Get recommended settings
    settings = scenario["recommended_settings"]
    
    # Override with command line arguments if provided
    if host is None:
        host = API_BASE_URL
    if users is None:
        users = settings["users"]
    if spawn_rate is None:
        spawn_rate = settings["spawn_rate"]
    if run_time is None:
        run_time = settings["run_time"]
    
    # Build environment variables string
    env_vars = " && ".join([f"set {k}={v}" for k, v in settings["env_vars"].items()])
    
    # Build command
    cmd = f"{env_vars} && locust -f tests/load/{scenario['script']} --host={host} --users={users} --spawn-rate={spawn_rate} --run-time={run_time}"
    
    # Add headless flag if specified
    if headless:
        cmd += " --headless"
    
    # Log command
    logger.info(f"Running load test scenario: {scenario_name}")
    logger.info(f"Description: {scenario['description']}")
    logger.info(f"Command: {cmd}")
    
    # Run command
    try:
        start_time = datetime.now()
        process = subprocess.run(cmd, shell=True, check=False)
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Log result
        if process.returncode == 0:
            logger.info(f"Load test completed successfully in {duration:.2f} seconds")
        else:
            logger.error(f"Load test failed with exit code {process.returncode}")
        
        return process.returncode
    except Exception as e:
        logger.error(f"Error running load test: {str(e)}")
        return 1

def run_all_tests(host: str = None, headless: bool = True) -> Dict[str, int]:
    """
    Run all load test scenarios
    
    Args:
        host: API host URL (overrides default)
        headless: Whether to run in headless mode
        
    Returns:
        Dict[str, int]: Dictionary of scenario names and exit codes
    """
    results = {}
    
    logger.info("=== Running all Pine Time load test scenarios ===")
    
    for scenario_name in TEST_SCENARIOS.keys():
        logger.info(f"\n=== Running scenario: {scenario_name} ===")
        exit_code = run_load_test(scenario_name, host=host, headless=headless)
        results[scenario_name] = exit_code
    
    # Log summary
    logger.info("\n=== Load Test Summary ===")
    for scenario_name, exit_code in results.items():
        status = "SUCCESS" if exit_code == 0 else f"FAILED (code: {exit_code})"
        logger.info(f"{scenario_name}: {status}")
    
    return results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Pine Time Load Test Runner")
    
    # Add arguments
    parser.add_argument("--scenario", type=str, help="Test scenario to run (default: run all scenarios)")
    parser.add_argument("--host", type=str, default=API_BASE_URL, help=f"API host URL (default: {API_BASE_URL})")
    parser.add_argument("--users", type=int, help="Number of users to simulate (overrides default)")
    parser.add_argument("--spawn-rate", type=int, help="User spawn rate (overrides default)")
    parser.add_argument("--run-time", type=str, help="Test run time (overrides default)")
    parser.add_argument("--no-headless", action="store_true", help="Run with UI (default: headless)")
    parser.add_argument("--list", action="store_true", help="List available test scenarios")
    
    # Parse arguments
    args = parser.parse_args()
    
    # List scenarios if requested
    if args.list:
        print("\nAvailable test scenarios:")
        for name, scenario in TEST_SCENARIOS.items():
            settings = scenario["recommended_settings"]
            print(f"- {name}: {scenario['description']}")
            print(f"  Script: {scenario['script']}")
            print(f"  Recommended settings: {settings['users']} users, {settings['spawn_rate']} spawn rate, {settings['run_time']} run time")
            print()
        return 0
    
    # Run specified scenario or all scenarios
    if args.scenario:
        return run_load_test(
            args.scenario, 
            host=args.host, 
            users=args.users, 
            spawn_rate=args.spawn_rate, 
            run_time=args.run_time, 
            headless=not args.no_headless
        )
    else:
        results = run_all_tests(host=args.host, headless=not args.no_headless)
        # Return non-zero if any test failed
        return 1 if any(code != 0 for code in results.values()) else 0

if __name__ == "__main__":
    sys.exit(main())
