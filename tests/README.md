# Pine Time App Testing Framework

This testing framework provides comprehensive test coverage for the Pine Time application, ensuring API functionality, frontend integration, and performance under load.

## Test Components

The testing framework consists of several components:

1. **API Tests**: Verify that all API endpoints function correctly
2. **Integration Tests**: Test the interaction between different components
3. **Frontend Tests**: Validate the Streamlit interface functionality
4. **Load Tests**: Measure performance under high user load

## Setup

### Prerequisites

- Python 3.12
- PostgreSQL 17.4
- All dependencies listed in `requirements.txt`

### Installation

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Configure test environment variables in `.env`:

```
# Test Configuration
TEST_USERNAME=testuser
TEST_PASSWORD=testpassword
TEST_EMAIL=test@example.com
TEST_ADMIN_USERNAME=testadmin
TEST_ADMIN_PASSWORD=testadminpassword
TEST_ADMIN_EMAIL=testadmin@example.com
```

3. Ensure the PostgreSQL database is running and accessible

## Running Tests

### Using the Test Runner

The simplest way to run tests is using the test runner script:

```bash
# Run all tests except load tests
python tests/run_tests.py

# Run specific test categories
python tests/run_tests.py --api --integration
python tests/run_tests.py --frontend
python tests/run_tests.py --load

# Run all tests including load tests
python tests/run_tests.py --all

# Run with verbose output
python tests/run_tests.py --verbose

# Configure load tests
python tests/run_tests.py --load --users 50 --spawn-rate 10 --run-time 5m
```

### Running Tests Directly with pytest

You can also run tests directly with pytest:

```bash
# Run all tests
pytest tests/

# Run specific test categories
pytest tests/api/
pytest tests/integration/
pytest tests/frontend/

# Run with verbose output
pytest -v tests/

# Run a specific test file
pytest tests/api/test_auth_api.py
```

### Running Load Tests with Locust

Load tests can be run directly with Locust:

```bash
# Run in headless mode
locust -f tests/load/load_test.py --headless -u 10 -r 1 --run-time 1m --host http://localhost:8000

# Run with web interface
locust -f tests/load/load_test.py --host http://localhost:8000
```

Then open http://localhost:8089 in your browser to access the Locust web interface.

## Test Database

The tests use a transaction-based approach to ensure database integrity:

1. Each test function gets a fresh database transaction
2. All changes are rolled back after the test completes
3. This ensures tests don't interfere with each other

## Test Coverage

### API Tests

- Authentication (login, token refresh, verification)
- User management (registration, profile updates)
- Event management (creation, registration, check-in)
- Badge and points systems

### Integration Tests

- Complete user flows (registration → login → event registration → check-in)
- Error handling across components
- API response format handling

### Frontend Tests

- User interface functionality
- Page navigation
- Form submissions
- Data display

### Load Tests

- Concurrent user simulation
- Performance under load
- Response time measurement
- Error rate tracking

## Best Practices

1. **Isolation**: Each test should be independent and not rely on the state from other tests
2. **Mocking**: Use mocks for external services when appropriate
3. **Assertions**: Make specific assertions about expected outcomes
4. **Error Handling**: Test both success and failure scenarios
5. **Documentation**: Document the purpose of each test

## Troubleshooting

### Common Issues

- **Database Connection Errors**: Ensure PostgreSQL is running and credentials are correct
- **API Connection Errors**: Verify the API server is running on the expected host/port
- **Authentication Failures**: Check that test user credentials are valid
- **Missing Dependencies**: Ensure all requirements are installed

### Logs

Test logs are stored in:
- `test.log`: General test log
- `test_run_YYYYMMDD_HHMMSS.log`: Specific test run log
- `load_test.log`: Load test log
- `load_test_report_YYYYMMDD_HHMMSS.html`: Load test HTML report