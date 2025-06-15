#!/bin/bash

set -e

echo "🔐 Setting up SSL/TLS certificates and secrets for DataMed..."
mkdir -p ssl
mkdir -p secrets
echo "🔑 Generating secure secrets..."
echo $(openssl rand -hex 32) > secrets/token_key.txt
echo $(openssl rand -hex 16) > secrets/postgres_password.txt
echo $(openssl rand -hex 16) > secrets/keycloak_admin_password.txt
echo "datamed_$(openssl rand -hex 8)" > secrets/minio_access_key.txt
echo $(openssl rand -hex 32) > secrets/minio_secret_key.txt
chmod 600 secrets/*.txt

echo "📝 Creating .env file with generated secrets..."
cat > .env << EOF
# Database Configuration
POSTGRES_USER=datamed
POSTGRES_DB=datamed

# Keycloak Configuration
KEYCLOAK_ADMIN=admin
KEYCLOAK_URL=http://keycloak:8080
KEYCLOAK_REALM=datamed
KEYCLOAK_CLIENT_ID=datamed-client
KEYCLOAK_CLIENT_SECRET=

# MinIO Configuration
MINIO_BUCKET=prescriptions

# The actual secrets are stored in Docker secrets, these are just placeholders
# Do NOT set POSTGRES_PASSWORD, KEYCLOAK_ADMIN_PASSWORD, TOKEN_KEY, MINIO_ACCESS_KEY, MINIO_SECRET_KEY here!

# File Upload Limits
MAX_FILE_SIZE=10485760
ALLOWED_EXTENSIONS=pdf
EOF

echo "🔐 Generating SSL certificates..."
openssl genrsa -out ssl/datamed.key 2048
openssl req -new -key ssl/datamed.key -out ssl/datamed.csr -subj "/C=PL/ST=Poland/L=Warsaw/O=DataMed/OU=IT/CN=localhost"
openssl x509 -req -days 365 -in ssl/datamed.csr -signkey ssl/datamed.key -out ssl/datamed.crt
openssl dhparam -out ssl/dhparam.pem 2048
chmod 600 ssl/datamed.key
chmod 644 ssl/datamed.crt ssl/dhparam.pem
rm ssl/datamed.csr
echo "✅ SSL certificates and secrets generated successfully!"
echo "📁 Certificates location: ./ssl/"
echo "🔑 Private key: ssl/datamed.key"
echo "📜 Certificate: ssl/datamed.crt"
echo "🔒 DH parameters: ssl/dhparam.pem"
echo "🗝️  Secrets location: ./secrets/"
echo ""
echo "🚀 Ready to start! Run: docker-compose up -d"
echo "🌐 Access your application at: https://localhost"
echo "🔧 MinIO Console at: https://localhost:9001"
echo ""
echo "⚠️  WARNING: These are self-signed certificates for development only!"
echo "   For production, obtain certificates from a trusted CA like Let's Encrypt"
echo ""
echo "📋 Next steps:"
echo "1. Run: docker-compose up -d"
echo "2. Wait for all services to start"
echo "3. Access https://localhost (accept the self-signed certificate warning)"
echo "4. Run ./security-test.sh to verify security settings"
