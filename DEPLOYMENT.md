# CodePulse AI - Deployment Guide

## Overview

CodePulse AI is a comprehensive multi-agent code improvement platform. This guide covers deployment options from local development to production Kubernetes clusters.

## Table of Contents

1. [Local Development](#local-development)
2. [Docker](#docker)
3. [Kubernetes](#kubernetes)
4. [Production Checklist](#production-checklist)
5. [Monitoring & Maintenance](#monitoring--maintenance)

---

## Local Development

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker & Docker Compose (optional)

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/codepulse.git
cd codepulse

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements-dev.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Start development server
python -m flask run
```

### With Docker Compose

```bash
# Start all services (API, Database, Redis, Frontend)
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop services
docker-compose down
```

Access the application at `http://localhost:3000` (Frontend) and `http://localhost:5000` (API).

---

## Docker

### Building the Image

```bash
# Build Docker image
docker build -t codepulse:latest .

# Tag for registry
docker tag codepulse:latest your-registry/codepulse:latest

# Push to registry
docker push your-registry/codepulse:latest
```

### Running Container

```bash
# Run with environment variables
docker run -d \
  -p 5000:5000 \
  -e DATABASE_URL="postgresql://user:pass@db:5432/codepulse" \
  -e REDIS_URL="redis://redis:6379/0" \
  -e FLASK_ENV="production" \
  --name codepulse-api \
  codepulse:latest

# Check health
curl http://localhost:5000/api/v1/phase6/health
```

---

## Kubernetes

### Prerequisites

- Kubernetes cluster (v1.24+)
- kubectl configured
- Container registry access
- Persistent volume provisioner

### Installation

1. **Create namespace and secrets**

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl create secret generic codepulse-secrets \
  --from-literal=database-url="postgresql://codepulse:PASSWORD@postgres:5432/codepulse" \
  --from-literal=redis-url="redis://redis:6379/0" \
  --from-literal=secret-key="$(openssl rand -hex 32)" \
  --from-literal=postgres-password="SECURE_PASSWORD" \
  -n codepulse

# Create configmap
kubectl create configmap codepulse-config \
  --from-file=config/ \
  -n codepulse
```

2. **Deploy services**

```bash
# Deploy PostgreSQL
kubectl apply -f k8s/postgres-statefulset.yaml

# Wait for PostgreSQL to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n codepulse --timeout=300s

# Deploy API
kubectl apply -f k8s/api-deployment.yaml

# Deploy Redis
kubectl apply -f k8s/redis-deployment.yaml
```

3. **Verify deployment**

```bash
# Check pods
kubectl get pods -n codepulse

# Check services
kubectl get svc -n codepulse

# Check deployment status
kubectl rollout status deployment/codepulse-api -n codepulse
```

### Accessing the Application

```bash
# Port forward to local machine
kubectl port-forward svc/codepulse-api 5000:80 -n codepulse

# Access at http://localhost:5000
curl http://localhost:5000/api/v1/phase6/health
```

### Scaling

```bash
# Manual scaling
kubectl scale deployment codepulse-api --replicas=5 -n codepulse

# Check HPA status
kubectl get hpa -n codepulse
kubectl describe hpa codepulse-api -n codepulse
```

---

## Production Checklist

### Pre-Deployment

- [ ] Update container image registry URL
- [ ] Set secure passwords for databases
- [ ] Configure TLS certificates
- [ ] Set up monitoring (Prometheus, Grafana)
- [ ] Set up logging (ELK stack or similar)
- [ ] Configure backup strategy
- [ ] Security audit completed
- [ ] Load testing passed
- [ ] Documentation reviewed

### Configuration

```yaml
# Example production values
FLASK_ENV: production
LOG_LEVEL: INFO
WORKERS: 4
WORKER_CLASS: gevent
TIMEOUT: 120
KEEP_ALIVE: 5
```

### Security

```bash
# Use NetworkPolicy to restrict traffic
kubectl apply -f k8s/network-policy.yaml

# Set up Pod Security Policy
kubectl apply -f k8s/pod-security-policy.yaml

# Enable RBAC
kubectl apply -f k8s/rbac.yaml
```

### Ingress Configuration

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: codepulse-ingress
  namespace: codepulse
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
    nginx.ingress.kubernetes.io/ssl-redirect: "true"
spec:
  ingressClassName: nginx
  tls:
  - hosts:
    - api.codepulse.io
    secretName: codepulse-tls
  rules:
  - host: api.codepulse.io
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: codepulse-api
            port:
              number: 80
```

---

## Monitoring & Maintenance

### Logs

```bash
# View application logs
kubectl logs deployment/codepulse-api -n codepulse -f

# View logs from specific pod
kubectl logs codepulse-api-XXXXX -n codepulse

# Stream logs from all pods
kubectl logs -l app=codepulse-api -n codepulse -f --all-containers=true
```

### Health Checks

```bash
# Check API health
curl http://codepulse-api:80/api/v1/phase6/health

# Check database connectivity
kubectl exec -it postgres-0 -n codepulse -- psql -U codepulse -d codepulse -c "SELECT 1"

# Check Redis connectivity
kubectl exec -it redis-0 -n codepulse -- redis-cli ping
```

### Backup & Restore

```bash
# Backup PostgreSQL
kubectl exec -it postgres-0 -n codepulse -- pg_dump -U codepulse codepulse > backup.sql

# Restore PostgreSQL
kubectl exec -it postgres-0 -n codepulse -- psql -U codepulse codepulse < backup.sql

# Backup persistent volumes
kubectl get pvc -n codepulse
# Use your backup solution to backup the PVs
```

### Upgrades

```bash
# Update image
kubectl set image deployment/codepulse-api \
  codepulse-api=codepulse:v2.0.0 \
  -n codepulse

# Monitor rollout
kubectl rollout status deployment/codepulse-api -n codepulse

# Rollback if needed
kubectl rollout undo deployment/codepulse-api -n codepulse
```

---

## Troubleshooting

### Pods not starting

```bash
# Check pod events
kubectl describe pod codepulse-api-XXXXX -n codepulse

# Check logs
kubectl logs codepulse-api-XXXXX -n codepulse

# Check resource availability
kubectl top nodes
kubectl top pods -n codepulse
```

### Database connection issues

```bash
# Check if database is ready
kubectl get statefulset postgres -n codepulse

# Check database logs
kubectl logs postgres-0 -n codepulse

# Test connection
kubectl run -it --rm debug --image=postgres:15-alpine --restart=Never -n codepulse -- \
  psql -h postgres -U codepulse -d codepulse -c "SELECT 1"
```

### Out of resources

```bash
# Check node resources
kubectl top nodes

# Scale down replicas
kubectl scale deployment codepulse-api --replicas=1 -n codepulse

# Add more nodes to cluster
# (Depends on your cloud provider)
```

---

## Support & Documentation

- API Documentation: `/api/v1/docs`
- Health Check: `/api/v1/phase6/health`
- Metrics: `/api/v1/metrics`
- Logs: Check Kubernetes logs with `kubectl logs`

For additional help, visit the GitHub repository or contact support.
