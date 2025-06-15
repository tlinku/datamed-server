#!/bin/bash
set -e
docker-compose down --volumes --remove-orphans 2>/dev/null || true
if [ -d "ssl" ]; then
    rm -rf ssl/
fi
if [ -d "secrets" ]; then
    rm -rf secrets/
fi
if [ -f ".env" ]; then
    rm .env
fi
docker-compose down --rmi all 2>/dev/null || true
docker volume prune -f 2>/dev/null || true
docker network prune -f 2>/dev/null || true
echo "Cleanup complete!"
