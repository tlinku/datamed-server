#!/bin/bash
echo "Waiting for Keycloak to be ready..."
until curl -s http://keycloak:8080 > /dev/null; do
    sleep 5
done
echo "Keycloak is ready!"
echo "Getting admin token..."
ADMIN_TOKEN=$(curl -s -X POST http://keycloak:8080/realms/master/protocol/openid-connect/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin" \
  -d "password=admin" \
  -d "grant_type=password" \
  -d "client_id=admin-cli" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$ADMIN_TOKEN" ]; then
  echo "Failed to get admin token"
  exit 1
fi

echo "Admin token obtained successfully"
echo "Checking if realm exists..."
REALM_EXISTS=$(curl -s -o /dev/null -w "%{http_code}" http://keycloak:8080/admin/realms/datamed \
  -H "Authorization: Bearer $ADMIN_TOKEN")

if [ "$REALM_EXISTS" == "404" ]; then
  echo "Creating realm..."
  curl -s -X POST http://keycloak:8080/admin/realms \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"realm":"datamed","enabled":true}'

  echo "Realm created successfully"
else
  echo "Realm already exists"
fi
echo "Checking if client exists..."
CLIENT_EXISTS=$(curl -s http://keycloak:8080/admin/realms/datamed/clients \
  -H "Authorization: Bearer $ADMIN_TOKEN" | grep -c "datamed-client" || true)

if [ "$CLIENT_EXISTS" == "0" ]; then
  echo "Creating client..."
  curl -s -X POST http://keycloak:8080/admin/realms/datamed/clients \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
      "clientId": "datamed-client",
      "publicClient": true,
      "redirectUris": ["http://localhost:3000/*"],
      "webOrigins": ["http://localhost:3000"],
      "directAccessGrantsEnabled": true,
      "standardFlowEnabled": true
    }'

  echo "Client created successfully"
else
  echo "Client already exists"
fi

echo "Keycloak initialization completed!"
