#!/bin/bash

# Navigate to the project root
cd "$(dirname "$0")/../.."

# Check if required packages are installed
echo "Checking for required Python packages..."
if ! python3 -c "import psycopg2" 2>/dev/null; then
    echo "Installing required Python packages..."
    pip3 install -r backend/requirements.txt
fi

# Check if Docker is running
echo "Checking if Docker is running..."
if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker is not running. Please start Docker and try again."
    exit 1
fi

echo "Running container tests..."
python3 -m backend.tests.test_containers

if [ $? -eq 0 ]; then
    echo "All container tests passed!"
    exit 0
else
    echo "Some container tests failed. Check the logs for details."
    exit 1
fi
