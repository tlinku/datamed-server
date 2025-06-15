#!/bin/bash
set -e

echo "🚀 DataMed Quick Start with SSL & Docker Secrets"
echo "================================================="

if ! docker info >/dev/null 2>&1; then
    echo "Docker is not running"
    exit 1
fi

if ! command -v docker-compose >/dev/null 2>&1; then
    echo "docker-compose is not installed"
    exit 1
fi

echo "Docker ready to work"

if [ ! -f "ssl/datamed.crt" ] || [ ! -f "ssl/datamed.key" ] || [ ! -d "secrets" ]; then
    echo "Setting up SSL certificates and secrets..."
    ./setup-ssl.sh
else
    echo "SSL certificates and secrets already exist"
fi

echo "Starting Containers"
docker-compose up -d --build
wait_for_service() {
    local service_name=$1
    local max_attempts=30
    local attempt=1
    while [ $attempt -le $max_attempts ]; do
        if docker-compose ps | grep "$service_name" | grep -q "healthy\|Up"; then
            echo "✅ $service_name is ready"
            return 0
        fi
        sleep 10
        attempt=$((attempt + 1))
    done
    
    echo "$service_name failed to start"
    return 1
}
wait_for_service "postgres"
wait_for_service "minio"
wait_for_service "keycloak"
wait_for_service "backend"
wait_for_service "frontend"
wait_for_service "nginx"

echo ""
echo "Datamed is now working"
echo "================================================="
echo ""
echo "Frontend:     https://localhost"
echo "🔧 MinIO:        https://localhost:9001"
echo "Keycloak:       https://localhost/auth/admin"
docker-compose ps
