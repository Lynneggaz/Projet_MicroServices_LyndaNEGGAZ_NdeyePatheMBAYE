kubectl apply -f src/gateway-service/manifest/gateway-deploy.yamlkubectl apply -f src/gateway-service/manifest/gateway-deploy.yaml#!/bin/bash
set -e

echo "🚀 Building Docker images for microservices..."

# Configure to use Minikube's Docker daemon
eval $(minikube docker-env)

# Build auth-service
echo "Building auth-service..."
cd src/auth-service
docker build -t auth-service:local .
cd ../..

# Build gateway-service
echo "Building gateway-service..."
cd src/gateway-service
docker build -t gateway-service:local .
cd ../..

# Build converter-service
echo "Building converter-service..."
cd src/converter-service
docker build -t converter-service:local .
cd ../..

# Build notification-service
echo "Building notification-service..."
cd src/notification-service
docker build -t notification-service:local .
cd ../..

echo "✅ All Docker images built successfully!"
echo ""
echo "Listing images:"
docker images | grep -E "(auth-service|gateway-service|converter-service|notification-service)"
