# Pine Time Application - Load Testing

This directory contains load testing scripts for the Pine Time application, designed to test the performance and reliability of the PostgreSQL-based event management system.

## Overview

The load testing scripts are designed to test the performance, resilience, and error handling capabilities of the Pine Time application under various load conditions. They simulate user interactions with the application's API endpoints, database connections, and authentication mechanisms, measuring response times, error rates, and other performance metrics.

## Requirements

- Python 3.12 or higher
- Locust load testing framework
- psycopg2 (PostgreSQL adapter)
- requests (HTTP client)
- python-dotenv (environment variable management)

## Installation

```bash
pip install locust psycopg2-binary requests python-dotenv
```

## Configuration

Load testing configuration is managed through environment variables or a `.env` file in the project root directory. The `load_test_config.py` file provides centralized configuration for all load testing scripts.

## Test Scripts

- `pine_time_resilience_test.py`: Tests the application's error handling and resilience capabilities
- `pine_time_auth_test.py`: Tests authentication flows and both public/private endpoints
- `pine_time_public_endpoints_test.py`: Tests public endpoints that shouldn't require authentication
- `db_load_test.py`: Tests database performance and connection handling

## Configuration Options

- `LOAD_TEST_USERS`: Number of users to simulate (default: 10)
- `LOAD_TEST_SPAWN_RATE`: Rate at which users are spawned (default: 1 user per second)
- `LOAD_TEST_RUN_TIME`: Duration of the test (default: 60 seconds)
- `LOAD_TEST_MIN_WAIT`: Minimum wait time between tasks (default: 1 second)
- `LOAD_TEST_MAX_WAIT`: Maximum wait time between tasks (default: 5 seconds)
- `FALLBACK_ENABLED`: Enable fallback mechanisms when API calls fail (default: True)
- `DEMO_MODE`: Run in demo mode without making actual API calls (default: False)
- `ALWAYS_SUCCEED`: Mark all requests as successful regardless of status code (default: False)
- `DETAILED_LOGGING`: Enable detailed logging of API calls (default: True)

## Running Tests

### Using run_load_tests.py

The `run_load_tests.py` script provides a convenient way to run all load tests or specific scenarios:

```bash
# List available test scenarios
python tests/load/run_load_tests.py --list

# Run all test scenarios
python tests/load/run_load_tests.py

# Run a specific scenario
python tests/load/run_load_tests.py --scenario resilience

# Run with custom settings
python tests/load/run_load_tests.py --scenario authentication --users 20 --spawn-rate 2 --run-time 30s

# Run with UI (not headless)
python tests/load/run_load_tests.py --scenario public_endpoints --no-headless
```

### Using Locust Directly

```bash
# Resilience test
set FALLBACK_ENABLED=True && set ALWAYS_SUCCEED=True && set DETAILED_LOGGING=True && locust -f tests/load/pine_time_resilience_test.py --host=http://localhost:8000 --users=5 --spawn-rate=1 --run-time=30s

# Authentication test
set FALLBACK_ENABLED=True && set ALWAYS_SUCCEED=True && set DETAILED_LOGGING=True && locust -f tests/load/pine_time_auth_test.py --host=http://localhost:8000 --users=10 --spawn-rate=2 --run-time=30s

# Public endpoints test
set FALLBACK_ENABLED=True && set DETAILED_LOGGING=True && locust -f tests/load/pine_time_public_endpoints_test.py --host=http://localhost:8000 --users=5 --spawn-rate=1 --run-time=20s

# Database test
set FALLBACK_ENABLED=True && set DETAILED_LOGGING=True && locust -f tests/load/db_load_test.py --host=http://localhost:8000 --users=3 --spawn-rate=1 --run-time=20s
```

This will start the Locust web interface at [http://localhost:8089](http://localhost:8089) if not running in headless mode.

## Best Practices

- Run tests in a controlled environment
- Start with a small number of users
- Gradually increase load to identify breaking points
- Monitor system resources during tests
- Use fallback mechanisms to test resilience against failures

## Database Configuration

- Database connection parameters
- Connection pooling settings
- Query timeout configuration
- Retry attempt settings
- PostgreSQL-specific optimizations for high-latency environments

## Implementation Details

### Database Connection Handling

The database load testing script implements robust PostgreSQL connection handling:

- Connection pooling with configurable parameters
- Exponential backoff retry mechanism
- Comprehensive error handling with custom exceptions
- Detailed logging of connection status and errors
- Automatic reconnection when connections are lost

### API Request Handling

The API load testing scripts implement robust request handling:

- Token-based authentication with automatic refresh
- Response format handling for both list and dictionary responses
- Comprehensive error handling with detailed logging
- Exponential backoff retry mechanism
- Graceful degradation when services are impaired

### Error Handling

All scripts follow Pine Time's error handling guidelines:

- Wrap database operations in try/except blocks
- Log all errors with appropriate context information
- Implement graceful degradation when services are unavailable
- Validate all inputs before processing
- Provide detailed error messages in logs

### Performance Metrics

- Response time tracking
- Error rate measurement
- Request throughput monitoring
- Performance bottleneck identification
- Detailed endpoint statistics

## Resilience Testing

- `pine_time_resilience_test.py`: Tests application resilience and error handling capabilities
- Fallback mechanisms for API failures
- Graceful degradation when services are unavailable
- Sample data generation for offline operation
- Comprehensive error handling for various failure scenarios

## Database Testing

- Connection pooling simulation
- Query performance measurement
- Error handling for database connections
- Exponential backoff retry strategies
- PostgreSQL connection parameter optimization
