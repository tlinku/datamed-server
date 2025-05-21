import unittest
import subprocess
import requests
import psycopg2
import time
from minio import Minio
from minio.error import S3Error
import os
import sys
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend/tests/logs/container_tests.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ContainerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        logger.info("Setting up test environment")
        try:
            subprocess.run(["docker-compose", "up", "-d"], check=True)
            time.sleep(10)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start containers: {e}")
            raise

    def test_containers_running(self):
        logger.info("Testing if all containers are running")
        result = subprocess.run(
            ["docker-compose", "ps", "-q"],
            capture_output=True,
            text=True,
            check=True
        )

        container_ids = result.stdout.strip().split('\n')
        container_count = len([cid for cid in container_ids if cid])

        self.assertEqual(container_count, 5, f"Expected 5 containers, but found {container_count}")

        services = ["backend", "frontend", "postgres", "minio", "keycloak"]
        for service in services:
            result = subprocess.run(
                ["docker-compose", "ps", service],
                capture_output=True,
                text=True,
                check=True
            )
            self.assertIn("Up", result.stdout, f"Container {service} is not running")
            logger.info(f"Container {service} is running")

    def test_backend_api(self):
        logger.info("Testing backend API")

        try:
            response = requests.get("http://localhost:5000/health", timeout=5)
            self.assertEqual(response.status_code, 200, f"Backend API returned status code {response.status_code}")
            data = response.json()
            self.assertEqual(data.get('status'), 'healthy', "Backend API did not return expected health status")
            logger.info("Backend API is accessible and healthy")
        except requests.RequestException as e:
            self.fail(f"Backend API request failed: {e}")
        except ValueError as e:
            self.fail(f"Backend API returned invalid JSON: {e}")

    def test_frontend_service(self):
        logger.info("Testing frontend service")

        try:
            response = requests.get("http://localhost:3000", timeout=5)
            self.assertIn(response.status_code, [200, 404], f"Frontend service returned unexpected status code {response.status_code}")
            logger.info(f"Frontend service is accessible (status code: {response.status_code})")
        except requests.RequestException as e:
            self.fail(f"Frontend service request failed: {e}")

    def test_postgres_connection(self):
        logger.info("Testing PostgreSQL connection")

        try:
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="datamed",
                user="postgres",
                password="postgres"
            )

            cursor = conn.cursor()

            cursor.execute("SELECT 1")
            result = cursor.fetchone()

            cursor.close()
            conn.close()

            self.assertEqual(result[0], 1, "PostgreSQL query did not return expected result")
            logger.info("PostgreSQL connection successful")
        except psycopg2.Error as e:
            self.fail(f"PostgreSQL connection failed: {e}")

    def test_minio_connection(self):
        logger.info("Testing MinIO connection")

        try:
            minio_client = Minio(
                "localhost:9000",
                access_key="minioadmin",
                secret_key="minioadmin",
                secure=False
            )

            bucket_name = "prescriptions"
            if not minio_client.bucket_exists(bucket_name):
                minio_client.make_bucket(bucket_name)
                logger.info(f"Bucket '{bucket_name}' created")

            self.assertTrue(minio_client.bucket_exists(bucket_name), f"Bucket '{bucket_name}' does not exist")
            logger.info("MinIO connection successful")
        except S3Error as e:
            self.fail(f"MinIO connection failed: {e}")

    def test_keycloak_service(self):
        logger.info("Testing Keycloak service")

        try:
            response = requests.get("http://localhost:8080/realms/datamed", timeout=5)
            self.assertIn(response.status_code, [200, 301, 302, 401, 403, 404], 
                         f"Keycloak service returned unexpected status code {response.status_code}")
            logger.info(f"Keycloak service is accessible (status code: {response.status_code})")
        except requests.RequestException as e:
            try:
                response = requests.get("http://localhost:8080", timeout=5)
                self.assertIn(response.status_code, [200, 301, 302, 404], 
                             f"Keycloak service returned unexpected status code {response.status_code}")
                logger.info(f"Keycloak service is accessible (status code: {response.status_code})")
            except requests.RequestException as e2:
                self.fail(f"Keycloak service request failed: {e2}")

    @classmethod
    def tearDownClass(cls):
        logger.info("Cleaning up test environment")

if __name__ == "__main__":
    unittest.main()
