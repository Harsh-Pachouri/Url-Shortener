#!/bin/bash

# URL Shortener Kubernetes Deployment Script

echo "🚀 Deploying URL Shortener to Kubernetes..."

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t url-shortener-web:latest .

# Apply Kubernetes manifests in order
echo "🔧 Applying Kubernetes manifests..."

# 1. ConfigMap and Secrets first
kubectl apply -f configmap.yml

# 2. Persistent Volume Claims
kubectl apply -f postgres-deployment.yml
kubectl apply -f redis-deployment.yml

# 3. Services
kubectl apply -f service.yml

# 4. Main application deployment
kubectl apply -f deployment.yml

# 5. Ingress (optional)
kubectl apply -f ingress.yml

echo "⏳ Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/postgres-deployment
kubectl wait --for=condition=available --timeout=300s deployment/redis-deployment
kubectl wait --for=condition=available --timeout=300s deployment/url-shortener-web

echo "📊 Checking deployment status..."
kubectl get pods -l app=url-shortener
kubectl get services -l app=url-shortener

echo "🌐 Getting service URLs..."
echo "Web Service: $(kubectl get service url-shortener-web-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 2>/dev/null || echo 'localhost:30080')"

echo "✅ Deployment complete!"
echo ""
echo "🧪 To test the application:"
echo "1. If using NodePort: http://localhost:30080"
echo "2. If using LoadBalancer: Check the external IP above"
echo "3. If using Ingress: Add '127.0.0.1 linksnap.local' to /etc/hosts and visit http://linksnap.local"
echo ""
echo "📋 Useful commands:"
echo "  kubectl get pods -l app=url-shortener"
echo "  kubectl logs -l app=url-shortener,component=web"
echo "  kubectl port-forward service/url-shortener-web-service 8080:80"