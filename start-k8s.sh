#!/bin/bash
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

set -e

echo -e "${BLUE}🚀 Starting DataMed Kubernetes deployment...${NC}"
echo -e "${YELLOW}📋 Checking prerequisites...${NC}"
if ! command -v kubectl >/dev/null 2>&1; then
    echo -e "${RED}❌ kubectl is not installed${NC}"
    exit 1
fi

if ! kubectl cluster-info >/dev/null 2>&1; then
    echo -e "${RED}❌ Kubernetes cluster is not accessible${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"
wait_for_pods() {
    local service=$1
    local timeout=${2:-120}
    echo -e "${YELLOW}⏳ Waiting for $service pods to be ready (timeout: ${timeout}s)...${NC}"
    
    if kubectl wait --for=condition=ready pod -l io.kompose.service=$service --timeout=${timeout}s 2>/dev/null; then
        echo -e "${GREEN}✅ $service pods are ready${NC}"
        return 0
    else
        echo -e "${RED}❌ $service pods failed to start within ${timeout}s${NC}"
        echo -e "${YELLOW}📊 Pod status:${NC}"
        kubectl get pods -l io.kompose.service=$service
        echo -e "${YELLOW}📝 Recent events:${NC}"
        kubectl get events --sort-by='.lastTimestamp' | tail -5
        return 1
    fi
}
validate_passwords() {
    echo -e "${YELLOW}🔐 Validating passwords in secrets...${NC}"
    if ! kubectl get secret app-secrets >/dev/null 2>&1; then
        echo -e "${RED}❌ Secret 'app-secrets' not found${NC}"
        return 1
    fi
    local postgres_password=$(kubectl get secret app-secrets -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d | tr -d '\n\r')
    local password_length=${#postgres_password}
    
    echo -e "${BLUE}📏 PostgreSQL password length: $password_length characters${NC}"
    
    if [ $password_length -lt 10 ]; then
        echo -e "${RED}❌ PostgreSQL password seems too short${NC}"
        return 1
    fi
    if echo "$postgres_password" | grep -q $'\n\r'; then
        echo -e "${YELLOW}⚠️  Password contains newline characters, fixing...${NC}"
        fix_passwords
        return $?
    fi
    
    echo -e "${GREEN}✅ Passwords validation passed${NC}"
    return 0
}
fix_passwords() {
    echo -e "${YELLOW}🔧 Fixing password encoding...${NC}"
    local postgres_password=$(kubectl get secret app-secrets -o jsonpath='{.data.POSTGRES_PASSWORD}' | base64 -d | tr -d '\n\r')
    local clean_postgres_password=$(echo -n "$postgres_password" | base64)
    local keycloak_admin_password=$(echo -n "admin" | base64)
    kubectl patch secret app-secrets -p="{\"data\":{\"POSTGRES_PASSWORD\":\"$clean_postgres_password\",\"KEYCLOAK_ADMIN_PASSWORD\":\"$keycloak_admin_password\"}}"
    
    echo -e "${GREEN}✅ Password encoding fixed${NC}"
    echo -e "${BLUE}🔑 Keycloak admin password set to: admin${NC}"
}
echo -e "${BLUE}📦 Deploying base resources...${NC}"
kubectl apply -f kubernetes/base/config/ || {
    echo -e "${RED}Failed to apply base config${NC}"
    exit 1
}

kubectl apply -f kubernetes/base/configmap.yaml || {
    echo -e "${RED}Failed to apply configmap${NC}"
    exit 1
}
validate_passwords || {
    echo -e "${RED}Password validation failed${NC}"
    exit 1
}
echo -e "${BLUE}Deploying PVCs...${NC}"
kubectl apply -f kubernetes/pvcs.yaml || {
    echo -e "${RED}Failed to apply PVCs${NC}"
    exit 1
}
echo -e "${BLUE}Deploying Services...${NC}"
kubectl apply -f kubernetes/services.yaml || {
    echo -e "${RED}❌ Failed to apply Services${NC}"
    exit 1
}
echo -e "${BLUE}🚢 Deploying applications...${NC}"
echo -e "${YELLOW}🗄️  Deploying PostgreSQL...${NC}"
kubectl apply -f kubernetes/fixed/postgres-init-configmap.yaml
kubectl apply -f kubernetes/fixed/postgres-deployment.yaml
wait_for_pods "postgres" 180
echo -e "${YELLOW}📁 Deploying MinIO...${NC}"
kubectl apply -f kubernetes/fixed/minio-deployment.yaml
wait_for_pods "minio" 120
echo -e "${YELLOW}🔐 Deploying Keycloak...${NC}"
kubectl apply -f kubernetes/fixed/keycloak-realm-configmap.yaml
kubectl apply -f kubernetes/fixed/keycloak-deployment.yaml
wait_for_pods "keycloak" 240
echo -e "${YELLOW}⚙️  Deploying Backend...${NC}"
kubectl apply -f kubernetes/fixed/backend-deployment.yaml
wait_for_pods "backend" 180
echo -e "${YELLOW}🎨 Deploying Frontend...${NC}"
kubectl apply -f kubernetes/fixed/frontend-deployment.yaml
wait_for_pods "frontend" 120
echo -e "${BLUE}📊 Deploying HPA...${NC}"
kubectl apply -f kubernetes/hpa.yaml || {
    echo -e "${YELLOW}⚠️  HPA deployment failed (Metrics Server might not be available)${NC}"
}
echo -e "${BLUE}🌍 Deploying Ingress...${NC}"
kubectl apply -f kubernetes/working-ingress.yaml || {
    echo -e "${YELLOW}⚠️  Ingress deployment failed (Ingress Controller might not be available)${NC}"
}
echo -e "${BLUE}🔧 Configuring Keycloak...${NC}"
POSTGRES_POD=$(kubectl get pod -l io.kompose.service=postgres -o jsonpath='{.items[0].metadata.name}')
echo -e "${YELLOW}🔌 Testing database connection...${NC}"
if kubectl exec $POSTGRES_POD -- pg_isready -U postgres >/dev/null 2>&1; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    exit 1
fi
echo -e "${YELLOW}🔍 Checking Keycloak client configuration...${NC}"
CLIENT_CONFIG=$(kubectl exec $POSTGRES_POD -- psql -U postgres -d keycloak -c "SELECT public_client FROM client WHERE client_id='datamed-client';" -t 2>/dev/null | tr -d ' \n\r' || echo "")

if [ "$CLIENT_CONFIG" = "f" ]; then
    echo -e "${YELLOW}🔧 Updating Keycloak client to public...${NC}"
    kubectl exec $POSTGRES_POD -- psql -U postgres -d keycloak -c "UPDATE client SET public_client = true, direct_access_grants_enabled = true WHERE client_id = 'datamed-client';" >/dev/null
    kubectl rollout restart deployment/keycloak
    wait_for_pods "keycloak" 120
    echo -e "${GREEN}✅ Keycloak client updated to public${NC}"
elif [ "$CLIENT_CONFIG" = "t" ]; then
    echo -e "${GREEN}✅ Keycloak client already configured correctly${NC}"
else
    echo -e "${YELLOW}⚠️  Could not determine Keycloak client configuration (client might not exist yet)${NC}"
fi
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${BLUE}📊 Final status:${NC}"
kubectl get pods -o wide
echo ""
echo -e "${BLUE}🌐 Services:${NC}"
kubectl get services
echo ""
echo -e "${BLUE}🔗 Ingress:${NC}"
kubectl get ingress
echo ""
echo -e "${GREEN}✅ DataMed is ready!${NC}"
echo -e "${YELLOW}📝 Access URLs:${NC}"
echo -e "   🏠 Frontend: https://localhost"
echo -e "   🔐 Keycloak: https://localhost/auth"
echo -e "   📁 MinIO: https://minio.localhost"
echo -e "   🔧 API Health: https://localhost/api/health"
echo ""
echo -e "${BLUE}💡 To check logs: kubectl logs -f deployment/backend${NC}"
echo -e "${BLUE}💡 To scale: kubectl scale deployment/backend --replicas=5${NC}"
