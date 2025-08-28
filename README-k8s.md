# 🚀 URL Shortener - Kubernetes Deployment Guide

## 📋 Prerequisites

- Docker Desktop with Kubernetes enabled
- kubectl configured to use your cluster
- Ingress controller (optional, for external access)

## 🔧 Quick Deployment

### 1. Build the Docker Image
```bash
docker build -t url-shortener-web:latest .
```

### 2. Deploy to Kubernetes
```bash
# Make the deployment script executable (Linux/Mac)
chmod +x k8s-deploy.sh
./k8s-deploy.sh

# Or deploy manually (Windows/All platforms)
kubectl apply -f configmap.yml
kubectl apply -f postgres-deployment.yml
kubectl apply -f redis-deployment.yml
kubectl apply -f service.yml
kubectl apply -f deployment.yml
kubectl apply -f ingress.yml
```

### 3. Wait for Deployment
```bash
kubectl wait --for=condition=available --timeout=300s deployment/url-shortener-web
kubectl wait --for=condition=available --timeout=300s deployment/postgres-deployment
kubectl wait --for=condition=available --timeout=300s deployment/redis-deployment
```

## 🌐 Access the Application

### Option 1: NodePort (Default)
```bash
# Access via NodePort
http://localhost:30080
```

### Option 2: Port Forward
```bash
kubectl port-forward service/url-shortener-web-service 8080:80
# Then access: http://localhost:8080
```

### Option 3: Ingress (if configured)
```bash
# Add to /etc/hosts (Linux/Mac) or C:\Windows\System32\drivers\etc\hosts (Windows)
127.0.0.1 linksnap.local

# Then access: http://linksnap.local
```

## 🧪 Testing the Deployment

### Check Pod Status
```bash
kubectl get pods -l app=url-shortener
```

### Check Services
```bash
kubectl get services -l app=url-shortener
```

### View Logs
```bash
# Web application logs
kubectl logs -l app=url-shortener,component=web

# Database logs
kubectl logs -l app=url-shortener,component=database

# Cache logs
kubectl logs -l app=url-shortener,component=cache
```

### Test API Endpoints
```bash
# Register a user
curl -X POST http://localhost:30080/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'

# Login
curl -X POST http://localhost:30080/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"

# Shorten URL (replace TOKEN with actual token from login)
curl -X POST http://localhost:30080/shorten \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"target_url":"https://www.google.com"}'
```

## 🔧 Troubleshooting

### Common Issues

1. **Pods not starting**
   ```bash
   kubectl describe pod <pod-name>
   kubectl logs <pod-name>
   ```

2. **Database connection issues**
   ```bash
   kubectl exec -it deployment/postgres-deployment -- psql -U postgres -d url_shortener_db
   ```

3. **Service not accessible**
   ```bash
   kubectl get endpoints
   kubectl describe service url-shortener-web-service
   ```

### Scaling the Application
```bash
# Scale web pods
kubectl scale deployment url-shortener-web --replicas=3

# Check scaling status
kubectl get pods -l app=url-shortener,component=web
```

## 🧹 Cleanup

```bash
# Delete all resources
kubectl delete -f ingress.yml
kubectl delete -f deployment.yml
kubectl delete -f service.yml
kubectl delete -f redis-deployment.yml
kubectl delete -f postgres-deployment.yml
kubectl delete -f configmap.yml

# Or delete by label
kubectl delete all -l app=url-shortener
kubectl delete pvc -l app=url-shortener
```

## 📊 Monitoring

### Resource Usage
```bash
kubectl top pods -l app=url-shortener
kubectl top nodes
```

### Health Checks
The deployment includes:
- **Liveness probes**: Restart unhealthy containers
- **Readiness probes**: Route traffic only to ready containers
- **Resource limits**: Prevent resource exhaustion

## 🔒 Security Notes

- Change default passwords in production
- Use Kubernetes secrets for sensitive data
- Configure network policies for pod-to-pod communication
- Enable RBAC for proper access control

## 📈 Production Considerations

1. **Persistent Storage**: Configure proper storage classes
2. **Backup Strategy**: Set up database backups
3. **SSL/TLS**: Configure HTTPS with cert-manager
4. **Monitoring**: Add Prometheus/Grafana monitoring
5. **Logging**: Configure centralized logging