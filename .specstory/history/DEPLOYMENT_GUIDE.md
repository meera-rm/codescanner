---
created_at: 2026-06-12T18:16:43Z
title: Deployment Guide
source: claude-code
project: codescanner
---

# CodePulse AI - Deployment Guide

## Overview

This guide covers deploying CodePulse AI to production environments using Docker and Docker Compose.

---

## Quick Start (Local Docker)

### Prerequisites
- Docker 20.10+
- Docker Compose 1.29+
- 2GB RAM minimum
- 500MB disk space

### Step 1: Prepare Environment
```bash
# Clone repository
git clone https://github.com/company/codepulse.git
cd codepulse

# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### Step 2: Build and Run
```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Verify services are running
docker-compose ps

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Step 3: Access Application
- **Frontend:** http://localhost:3000
- **API:** http://localhost:8000/api/v1
- **Health Check:** http://localhost:8000/api/v1/analytics/health

### Step 4: Stop Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

---

## Production Deployment

### Prerequisites
- Docker 20.10+
- Docker Compose 1.29+
- Kubernetes 1.20+ (optional)
- PostgreSQL 12+ (recommended for production)
- SSL/TLS certificate

### Step 1: Environment Setup

#### Create `.env.production`
```bash
cp .env.example .env.production

# Edit with production values
nano .env.production
```

#### Critical Variables
```bash
# Security
SECRET_KEY=generate-long-random-string
DEBUG=false
CORS_ORIGINS=https://codepulse.company

# Database (use PostgreSQL)
DATABASE_URL=postgresql://user:password@postgres:5432/codepulse

# Monitoring
SENTRY_DSN=https://your-sentry-key@sentry.io/project-id
DATADOG_API_KEY=your-datadog-api-key

# API
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
```

### Step 2: Database Setup

#### Create PostgreSQL Database
```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE codepulse;
CREATE USER codepulse_user WITH PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE codepulse TO codepulse_user;

# Exit
\q
```

#### Run Migrations
```bash
# Using Docker
docker run --rm \
  -e DATABASE_URL=postgresql://user:pass@postgres:5432/codepulse \
  codepulse-backend \
  python -m alembic upgrade head
```

### Step 3: Configure SSL/TLS

#### With Let's Encrypt (Recommended)
```bash
# Generate certificate
certbot certonly --standalone \
  -d codepulse.company \
  -d api.codepulse.company
```

#### Update docker-compose.yml
```yaml
backend:
  environment:
    - SSL_CERT_PATH=/etc/letsencrypt/live/codepulse.company/fullchain.pem
    - SSL_KEY_PATH=/etc/letsencrypt/live/codepulse.company/privkey.pem
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

### Step 4: Deploy with Docker Compose

```bash
# Build production images
docker-compose -f docker-compose.yml build --no-cache

# Start services
docker-compose up -d

# Verify health
curl https://api.codepulse.company/api/v1/analytics/health

# Check logs
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Step 5: Configure Reverse Proxy (Nginx)

#### Create nginx.conf
```nginx
upstream backend {
    server backend:8000;
}

upstream frontend {
    server frontend:3000;
}

server {
    listen 80;
    server_name codepulse.company;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name codepulse.company;
    
    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/codepulse.company/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/codepulse.company/privkey.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Compress responses
    gzip on;
    gzip_types text/plain text/css text/xml text/javascript application/json;
    
    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API
    location /api/v1 {
        proxy_pass http://backend/api/v1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }
    
    # Health check
    location /health {
        proxy_pass http://backend/api/v1/analytics/health;
        access_log off;
    }
}
```

#### Run Nginx
```bash
docker run -d \
  --name codepulse-nginx \
  -p 80:80 -p 443:443 \
  -v /path/to/nginx.conf:/etc/nginx/conf.d/default.conf:ro \
  -v /etc/letsencrypt:/etc/letsencrypt:ro \
  nginx:alpine
```

---

## Kubernetes Deployment

### Step 1: Create Namespace
```bash
kubectl create namespace codepulse
```

### Step 2: Create Secrets
```bash
kubectl create secret generic codepulse-secrets \
  --from-literal=SECRET_KEY=your-secret-key \
  --from-literal=DATABASE_PASSWORD=db-password \
  -n codepulse
```

### Step 3: Deploy Backend
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codepulse-backend
  namespace: codepulse
spec:
  replicas: 2
  selector:
    matchLabels:
      app: codepulse-backend
  template:
    metadata:
      labels:
        app: codepulse-backend
    spec:
      containers:
      - name: backend
        image: codepulse-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: API_HOST
          value: "0.0.0.0"
        - name: API_PORT
          value: "8000"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: codepulse-secrets
              key: DATABASE_URL
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: codepulse-secrets
              key: SECRET_KEY
        livenessProbe:
          httpGet:
            path: /api/v1/analytics/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/analytics/health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: codepulse-backend
  namespace: codepulse
spec:
  selector:
    app: codepulse-backend
  ports:
  - protocol: TCP
    port: 8000
    targetPort: 8000
  type: ClusterIP
```

### Step 4: Deploy Frontend
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: codepulse-frontend
  namespace: codepulse
spec:
  replicas: 2
  selector:
    matchLabels:
      app: codepulse-frontend
  template:
    metadata:
      labels:
        app: codepulse-frontend
    spec:
      containers:
      - name: frontend
        image: codepulse-frontend:latest
        ports:
        - containerPort: 3000
        env:
        - name: REACT_APP_API_URL
          value: "https://api.codepulse.company/api/v1"
        - name: NODE_ENV
          value: "production"
        livenessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 10
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /
            port: 3000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "256Mi"
            cpu: "200m"
---
apiVersion: v1
kind: Service
metadata:
  name: codepulse-frontend
  namespace: codepulse
spec:
  selector:
    app: codepulse-frontend
  ports:
  - protocol: TCP
    port: 3000
    targetPort: 3000
  type: ClusterIP
```

### Step 5: Deploy with Kubectl
```bash
kubectl apply -f backend-deployment.yaml
kubectl apply -f frontend-deployment.yaml

# Verify deployment
kubectl get pods -n codepulse
kubectl get services -n codepulse
```

---

## Health Checks & Monitoring

### Health Check Endpoint
```bash
# Check API health
curl http://localhost:8000/api/v1/analytics/health

# Response
{
  "status": "ok"
}
```

### Docker Health Status
```bash
# Check container health
docker ps --format "table {{.Names}}\t{{.Status}}"

# Expected output
NAMES                 STATUS
codepulse-backend     Up 2 minutes (healthy)
codepulse-frontend    Up 2 minutes (healthy)
```

### Logs Monitoring
```bash
# View logs
docker-compose logs backend

# Follow logs
docker-compose logs -f backend

# Filter logs
docker-compose logs backend | grep "ERROR"
```

---

## Monitoring & Logging

### Setup Sentry (Error Tracking)
```bash
# 1. Create Sentry project
# 2. Get DSN from Sentry dashboard
# 3. Update .env
SENTRY_DSN=https://key@sentry.io/project-id

# 4. Errors are now tracked automatically
```

### Setup DataDog (Performance Monitoring)
```bash
# 1. Install DataDog agent
docker pull datadog/agent:latest

# 2. Start DataDog container
docker run -d \
  --name dd-agent \
  -e DD_API_KEY=your-api-key \
  -e DD_SITE=datadoghq.com \
  -v /var/run/docker.sock:/var/run/docker.sock:ro \
  datadog/agent:latest

# 3. Metrics are now collected
```

### View Logs
```bash
# All logs
docker-compose logs

# Backend logs
docker-compose logs backend

# Frontend logs
docker-compose logs frontend

# Real-time logs
docker-compose logs -f
```

---

## Backup & Recovery

### Database Backup
```bash
# Backup PostgreSQL
docker exec codepulse-postgres pg_dump -U codepulse_user codepulse > backup.sql

# Backup with timestamp
docker exec codepulse-postgres pg_dump -U codepulse_user codepulse > backup-$(date +%Y%m%d).sql
```

### Database Restore
```bash
# Restore from backup
docker exec -i codepulse-postgres psql -U codepulse_user codepulse < backup.sql
```

### Application Backup
```bash
# Backup volumes
docker run --rm \
  -v codepulse_data:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/data-backup.tar.gz -C /data .
```

---

## Scaling

### Scale Backend Services
```bash
# Increase backend replicas
docker-compose up -d --scale backend=3

# Or modify docker-compose.yml
# backend:
#   deploy:
#     replicas: 3
```

### Load Balancing
```bash
# With Nginx
upstream backend {
    server backend:8000;
    server backend:8000;
    server backend:8000;
}
```

---

## Troubleshooting

### Container Won't Start
```bash
# Check logs
docker-compose logs backend

# Check health
docker-compose ps

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### API Returning 500 Errors
```bash
# Check backend logs
docker-compose logs backend

# Check database connection
docker exec codepulse-backend \
  python -c "import psycopg2; psycopg2.connect('postgresql://...')"
```

### Frontend Not Loading
```bash
# Check frontend logs
docker-compose logs frontend

# Verify API URL
curl http://localhost:8000/api/v1/analytics/health

# Check browser console for errors
# DevTools → Console tab
```

### Performance Issues
```bash
# Check resource usage
docker stats

# Increase resource limits in docker-compose.yml
# Or scale services
docker-compose up -d --scale backend=3
```

---

## Deployment Checklist

- [ ] Environment variables configured (.env file created)
- [ ] Database initialized and migrated
- [ ] SSL/TLS certificates installed
- [ ] Nginx reverse proxy configured
- [ ] Health checks passing
- [ ] Monitoring tools configured (Sentry, DataDog)
- [ ] Backup strategy implemented
- [ ] Logs configured and monitored
- [ ] Security headers enabled
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Database backups scheduled
- [ ] Disaster recovery plan documented
- [ ] Team trained on deployment process
- [ ] Rollback plan documented

---

## Rollback Procedure

### Quick Rollback
```bash
# Stop current version
docker-compose down

# Switch to previous image tag
sed -i 's/image: codepulse-backend:v2/image: codepulse-backend:v1/' docker-compose.yml

# Start previous version
docker-compose up -d

# Verify
curl http://localhost:8000/api/v1/analytics/health
```

### Database Rollback
```bash
# Restore from backup
docker exec -i codepulse-postgres psql -U codepulse_user codepulse < backup-v1.sql

# Run migrations
docker-compose exec backend alembic downgrade -1
```

---

## Support & Troubleshooting

For deployment issues, check:
1. Docker/Docker Compose version compatibility
2. Environment variables are set correctly
3. Network connectivity between services
4. Database connection string
5. Sufficient disk space (5GB+ recommended)
6. Memory available (2GB+ recommended)

---

**Last Updated:** 2026-06-06
**Deployment Ready:** ✅
