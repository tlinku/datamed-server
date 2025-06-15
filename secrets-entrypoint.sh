#!/bin/sh
if [ -f /run/secrets/postgres_password ]; then
  export KC_DB_PASSWORD=$(cat /run/secrets/postgres_password)
fi
if [ -f /run/secrets/keycloak_admin_password ]; then
  export KEYCLOAK_ADMIN_PASSWORD=$(cat /run/secrets/keycloak_admin_password)
fi
if [ -f /run/secrets/minio_access_key ]; then
  export MINIO_ROOT_USER=$(cat /run/secrets/minio_access_key)
fi
if [ -f /run/secrets/minio_secret_key ]; then
  export MINIO_ROOT_PASSWORD=$(cat /run/secrets/minio_secret_key)
fi
if [ -f /run/secrets/token_key ]; then
  export TOKEN_KEY=$(cat /run/secrets/token_key)
fi
if [ "$1" = "keycloak" ]; then
  shift
  exec /opt/keycloak/bin/kc.sh "$@"
elif [ "$1" = "minio" ]; then
  shift
  exec minio "$@"
else
  exec "$@"
fi
