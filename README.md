# Datamed Server - Dockerized Application

**Author:** Jan Szymański  
**Project:** Protokoły sieci web

This repository contains a dockerized version of the Datamed Server application, which includes:

- Backend (Flask)
- Frontend (React)
- PostgreSQL database
- MinIO for PDF storage
- Keycloak for authentication

## Prerequisites

- Docker
- Docker Compose

## Getting Started

1. Clone the repository:
   ```
   git clone <repository-url>
   cd datamed-server
   ```

2. Start the application:
   ```
   docker-compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:5000
   - MinIO Console: http://localhost:9001 (login with minioadmin/minioadmin)
   - Keycloak Admin Console: http://localhost:8080 (login with admin/admin)

## Services

### Backend

The backend is a Flask application that provides the API for the frontend. It connects to the PostgreSQL database and uses MinIO for PDF storage.

Environment variables:
- `FLASK_ENV`: Development or production environment
- `DATABASE_URL`: PostgreSQL connection string
- `TOKEN_KEY`: Secret key for JWT token generation
- `MINIO_URL`: MinIO server URL
- `MINIO_ACCESS_KEY`: MinIO access key
- `MINIO_SECRET_KEY`: MinIO secret key
- `MINIO_BUCKET`: MinIO bucket name for PDF storage

### Frontend

The frontend is a React application that provides the user interface for the application.

Environment variables:
- `REACT_APP_API_URL`: Backend API URL
- `REACT_APP_KEYCLOAK_URL`: Keycloak server URL
- `REACT_APP_KEYCLOAK_REALM`: Keycloak realm name
- `REACT_APP_KEYCLOAK_CLIENT_ID`: Keycloak client ID

### PostgreSQL

The PostgreSQL database stores the application data.

Environment variables:
- `POSTGRES_USER`: Database username
- `POSTGRES_PASSWORD`: Database password
- `POSTGRES_DB`: Database name

### MinIO

MinIO is used for storing PDF files uploaded by users.

Environment variables:
- `MINIO_ROOT_USER`: MinIO root username
- `MINIO_ROOT_PASSWORD`: MinIO root password

### Keycloak

Keycloak is used for authentication and authorization.

Environment variables:
- `KEYCLOAK_ADMIN`: Keycloak admin username
- `KEYCLOAK_ADMIN_PASSWORD`: Keycloak admin password
- `KC_DB`: Database type
- `KC_DB_URL`: Database connection string
- `KC_DB_USERNAME`: Database username
- `KC_DB_PASSWORD`: Database password

## Keycloak Integration

Keycloak is fully integrated with the application for authentication and authorization:

### Keycloak Setup

1. A Keycloak server is included in the docker-compose.yml file
2. On first run, you need to create a new realm in Keycloak called "datamed"
3. Create a new client in the realm called "datamed-client"
4. Configure the client:
   - Access Type: public
   - Valid Redirect URIs: http://localhost:3000/*
   - Web Origins: http://localhost:3000
5. Create roles for the application (e.g., user, admin)
6. Create users and assign roles

### Frontend Integration

The frontend uses Keycloak for authentication:
1. The Keycloak JavaScript adapter (keycloak-js) is integrated
2. Authentication is handled by redirecting to the Keycloak login page
3. Tokens are automatically managed by the Keycloak adapter
4. User roles from Keycloak are used for authorization

### Backend Integration

The backend validates Keycloak tokens:
1. Token signatures are verified using Keycloak's public key
2. User information is extracted from the token
3. Roles from the token are used for authorization
4. The `keycloak_token_required` decorator protects API endpoints

### Multi-Platform Support

The application supports multiple platforms:
1. Both backend and frontend can be built for linux/amd64 and linux/arm64
2. Docker images are optimized for size and security
3. Multi-stage builds are used to reduce image size
4. Health checks are implemented for container monitoring

## Data Persistence

The application uses Docker volumes for data persistence:
- `postgres_data`: PostgreSQL data
- `minio_data`: MinIO data
- `backend_logs`: Backend logs

## Testing

### Container Tests

The project includes tests to validate if all containers are working properly. These tests check:

1. If all containers are running
2. Backend API accessibility
3. Frontend service availability
4. PostgreSQL database connectivity
5. MinIO storage accessibility
6. Keycloak authentication service functionality

To run the container tests:

```bash
./backend/tests/run_tests.sh
```

For more details about the tests, see the [backend/tests/README.md](backend/tests/README.md) file.

## Troubleshooting

- If the frontend can't connect to the backend, check that the `REACT_APP_API_URL` environment variable is set correctly.
- If the backend can't connect to the database, check that the `DATABASE_URL` environment variable is set correctly.
- If the backend can't connect to MinIO, check that the MinIO service is running and the environment variables are set correctly.
- If Keycloak can't connect to the database, check that the database service is running and the environment variables are set correctly.
- If the container tests fail, check the logs in `backend/tests/logs/container_tests.log` for more details.
