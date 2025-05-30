# Sendgrid Email Module Tests

This directory contains automated tests for the `viam-sendgrid-email` module, which integrates the SendGrid API with the Viam platform for sending emails.

## Test Organization

All tests use the `pytest` framework with asynchronous support via `pytest-asyncio`:

- `test_sendgrid_email.py`: Tests for the `sendgridEmail` class, covering initialization, configuration validation, and email sending functionality (basic emails, emails with attachments, preset messages, and error handling).
- `conftest.py`: Defines shared pytest fixtures for mocking the SendGrid API client, component configuration, and utility functions.
- `run_tests.py`: Runs all tests using `pytest`, providing a single entry point for test execution.
- `requirements-test.txt`: Specifies test dependencies.
- `pytest.ini`: Configures `pytest` for test discovery and asynchronous execution.

## Running Tests

There are several ways to run the tests:

### Using Make

The project includes several `make` targets for testing:

```bash
# Run all tests
make test
```

```bash
# Run individual test file
make test-individual
```

```bash
# Run tests with coverage reporting
make coverage
```

### Running Directly

You can run the tests directly using `pytest`:

```bash
# Run all tests with verbose output
pytest -xvs tests/ --asyncio-mode=auto
```

```bash
# Run specific test file
pytest -xvs tests/test_sendgrid_email.py --asyncio-mode=auto
```

```bash
# Run specific test functions
pytest -xvs tests/test_sendgrid_email.py::test_send_basic_email --asyncio-mode=auto
```

```bash
# Run tests matching a specific pattern
pytest -xvs tests/ -k "send_basic_email" --asyncio-mode=auto
```

Alternatively, use the provided test runner script, which invokes `pytest` internally:

```bash
python3 tests/run_tests.py
```

## Test Dependencies

The tests require the following packages, which should be installed in your virtual environment:

- `pytest==8.3.2`
- `pytest-asyncio==0.24.0`
- `pytest-cov==5.0.0`

Install dependencies via:

```bash
make install-test-deps
```

Or directly with:

```bash
pip install -r tests/requirements-test.txt
```

## Adding More Tests

When adding new tests:

- Create or update test files in the `tests/` directory named `test_*.py`.
- Follow the patterns in `test_sendgrid_email.py`, using `@pytest.mark.asyncio` for async tests.
- Use fixtures from `conftest.py` (e.g., `mock_sendgrid_client`, `mock_component_config`) for consistent mocking.
- Tests will be automatically discovered by `pytest`.

## Mock Strategy

For testing components that interact with external services:

- Use `unittest.mock.patch` to replace external dependencies like `SendGridAPIClient` and `struct_to_dict`.
- Use fixtures in `conftest.py` to provide reusable mocks (e.g., `mock_sendgrid_client` for SendGrid API calls).
- Mock the logger to capture and verify logging behavior without actual output.

## Coverage Reporting

To measure test coverage and identify untested code paths:

```bash
make coverage
```

This generates a coverage report and an HTML version in the `htmlcov/` directory.

## Notes

- Tests are designed to be isolated, using mocks to avoid real API calls to SendGrid.
- The `pytest.ini` file ensures proper test discovery and async execution with `asyncio-mode=auto`.
- For edge cases or new features (e.g., additional preset message scenarios), add new test functions to `test_sendgrid_email.py`.