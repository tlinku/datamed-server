#!/bin/bash
kubectl delete pod -l io.kompose.service=keycloak
kubectl exec -it $(kubectl get pod -l io.kompose.service=postgres -o jsonpath='{.items[0].metadata.name}') -- psql -U postgres -c "DROP DATABASE IF EXISTS keycloak;"
kubectl exec -it $(kubectl get pod -l io.kompose.service=postgres -o jsonpath='{.items[0].metadata.name}') -- psql -U postgres -c "CREATE DATABASE keycloak;"
kubectl wait --for=condition=ready pod -l io.kompose.service=keycloak --timeout=180s
echo "Keycloak reset"
