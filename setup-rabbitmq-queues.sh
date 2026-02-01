#!/bin/bash
set -e

echo "🐰 Setting up RabbitMQ queues..."

# Get RabbitMQ pod name
RABBITMQ_POD=$(kubectl get pods -l app=rabbitmq -o jsonpath='{.items[0].metadata.name}')

if [ -z "$RABBITMQ_POD" ]; then
    echo "❌ Error: RabbitMQ pod not found"
    exit 1
fi

echo "Found RabbitMQ pod: $RABBITMQ_POD"

# Wait for RabbitMQ to be ready
echo "Waiting for RabbitMQ to be ready..."
kubectl wait --for=condition=ready pod/$RABBITMQ_POD --timeout=60s

# Create queues
echo "Creating 'video' queue..."
kubectl exec -it $RABBITMQ_POD -- rabbitmqadmin declare queue name=video durable=true || true

echo "Creating 'mp3' queue..."
kubectl exec -it $RABBITMQ_POD -- rabbitmqadmin declare queue name=mp3 durable=true || true

# List queues to verify
echo ""
echo "✅ Queues created! Listing all queues:"
kubectl exec -it $RABBITMQ_POD -- rabbitmqadmin list queues

echo ""
echo "🔄 Restarting converter and notification services..."
kubectl rollout restart deployment/converter
kubectl rollout restart deployment/notification

echo ""
echo "✅ Setup complete!"
echo ""
echo "To verify, access RabbitMQ Management UI:"
echo "http://$(minikube ip):30004"
echo "Username: guest"
echo "Password: guest"
