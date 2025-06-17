#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
safe_delete() {
    local resource_type=$1
    local resource_name=$2
    
    if kubectl get $resource_type $resource_name >/dev/null 2>&1; then
        echo -e "${YELLOW} Deleting $resource_type: $resource_name${NC}"
        kubectl delete $resource_type $resource_name --timeout=60s
    else
        echo -e "${BLUE}  $resource_type $resource_name does not exist${NC}"
    fi
}
echo -e "${BLUE} Removing HPA...${NC}"
safe_delete "hpa" "backend-hpa"
safe_delete "hpa" "frontend-hpa"

echo -e "${BLUE} Removing Ingress...${NC}"
safe_delete "ingress" "datamed-working-ingress"
safe_delete "ingress" "datamed-main-ingress"
safe_delete "ingress" "datamed-api-ingress"

echo -e "${BLUE} Removing Deployments...${NC}"
safe_delete "deployment" "backend"
safe_delete "deployment" "frontend" 
safe_delete "deployment" "postgres"
safe_delete "deployment" "keycloak"
safe_delete "deployment" "minio"
safe_delete "deployment" "backend-debug"

echo -e "${BLUE} Removing Services...${NC}"
safe_delete "service" "backend"
safe_delete "service" "frontend"
safe_delete "service" "postgres"
safe_delete "service" "keycloak"
safe_delete "service" "minio"

echo -e "${BLUE} Removing ConfigMaps...${NC}"
safe_delete "configmap" "app-config"
safe_delete "configmap" "postgres-init-scripts"
safe_delete "configmap" "keycloak-realm"

echo -e "${YELLOW} Do you want to remove secrets? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    safe_delete "secret" "app-secrets"
    safe_delete "secret" "datamed-tls"
fi

echo -e "${YELLOW} Do you want to remove PVCs (this will delete all data)? (y/N)${NC}"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    safe_delete "pvc" "postgres-data"
    safe_delete "pvc" "minio-data"
    safe_delete "pvc" "backend-logs"
fi

echo -e "${GREEN} Cleanup completed!${NC}"
echo -e "${BLUE} Remaining resources:${NC}"
kubectl get all | grep -E "(datamed|backend|frontend|postgres|keycloak|minio)" || echo "No DataMed resources found"
