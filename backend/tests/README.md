# Container Tests

This directory contains tests to validate if all the containers in the datamed-server project are working properly.

## Test Files

- `test_containers.py`: Tests to check if all containers are running and functioning correctly.

## What the Tests Check

The container tests verify:

1. **Container Status**: Checks if all containers (backend, frontend, postgres, minio, keycloak) are running.
2. **Backend API**: Verifies that the Flask backend API is accessible.
3. **Frontend Service**: Confirms that the React frontend service is accessible.
4. **PostgreSQL Database**: Tests connectivity to the PostgreSQL database.
5. **MinIO Storage**: Validates access to the MinIO object storage service.
6. **Keycloak Authentication**: Checks if the Keycloak authentication service is accessible.

## Prerequisites

Before running the tests, make sure you have:

1. Docker and Docker Compose installed
2. All required Python packages installed (see requirements.txt in the backend directory)

## How to Run the Tests

1. Make sure you're in the project root directory (datamed-server)
2. Run the tests using one of the following methods:

### Using the Shell Script (Recommended)

```bash
./backend/tests/run_tests.sh
```

### Using Python Directly

```bash
python -m backend.tests.test_containers
```

### Using unittest

```bash
python -m unittest backend.tests.test_containers
```

## Test Logs

Logs are written to:
- Console (stdout)
- `backend/tests/logs/container_tests.log`

## Notes

- The tests will automatically start the containers if they're not already running.
- By default, the tests will not stop the containers after completion to allow for manual inspection.
- To stop the containers after testing, uncomment the line in the `tearDownClass` method in `test_containers.py`.
