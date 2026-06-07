# Phase 3.5 Deployment Guide

**Target:** Production deployment of Iteration Until Clean service

---

## Prerequisites

### System Requirements
- Python 3.10+
- Redis (for Celery message broker)
- PostgreSQL 12+ (recommended) or SQLite (development)
- 2GB+ RAM minimum (4GB+ recommended for large jobs)
- 10GB+ disk space for codebases

### Software Dependencies
```bash
pip install fastapi==0.104.1
pip install uvicorn==0.24.0
pip install sqlalchemy==2.0.0
pip install celery==5.3.0
pip install redis==5.0.0
pip install pydantic==2.0.0
pip install anthropic==0.25.0
```

### Full Requirements
```bash
pip install -r requirements.txt
```

---

## Development Setup

### 1. Install Dependencies

```bash
cd /Users/meera/Documents/codescanner
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file:
```env
# Database
DATABASE_URL=sqlite:///./codepulse.db  # Or: postgresql://user:pass@localhost/codepulse

# API
API_HOST=0.0.0.0
API_PORT=8000

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Claude API (for refactoring suggestions)
ANTHROPIC_API_KEY=sk-...

# Logging
LOG_LEVEL=INFO
```

### 3. Initialize Database

```bash
python -c "from api.db.database import Base, engine; Base.metadata.create_all(bind=engine)"
```

### 4. Start Services (Development)

**Terminal 1: Redis**
```bash
redis-server
```

**Terminal 2: Celery Worker**
```bash
celery -A api.tasks.celery_app worker --loglevel=info
```

**Terminal 3: FastAPI Server**
```bash
python api/main.py
# Or with auto-reload:
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Access:** http://localhost:8000/docs (Swagger UI)

---

## Production Setup

### 1. Use PostgreSQL

Production requires a proper database. SQLite is development-only.

```bash
# Install PostgreSQL
brew install postgresql@15  # macOS
# or
sudo apt-get install postgresql-15  # Linux

# Create database
createdb codepulse
createuser codepulse_user
psql -c "ALTER USER codepulse_user WITH PASSWORD 'secure_password';"
psql -c "GRANT ALL PRIVILEGES ON DATABASE codepulse TO codepulse_user;"
```

**Update `.env`:**
```env
DATABASE_URL=postgresql://codepulse_user:secure_password@localhost:5432/codepulse
```

### 2. Use Gunicorn for ASGI Server

Development server is not suitable for production.

```bash
pip install gunicorn
gunicorn api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --timeout 300 \
  --access-logfile - \
  --error-logfile -
```

### 3. Configure Celery with Supervisor

Create `/etc/supervisor/conf.d/celery.conf`:

```ini
[program:celery]
command=celery -A api.tasks.celery_app worker --loglevel=info
directory=/var/www/codepulse
user=www-data
group=www-data
autostart=true
autorestart=true
startsecs=10
stopwaitsecs=600
stderr_logfile=/var/log/celery/celery.err.log
stdout_logfile=/var/log/celery/celery.out.log
```

Start:
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start celery
```

### 4. Configure Nginx as Reverse Proxy

Create `/etc/nginx/sites-available/codepulse`:

```nginx
upstream codepulse {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name api.codepulse.ai;

    client_max_body_size 100M;

    location / {
        proxy_pass http://codepulse;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    # Static files
    location /docs {
        proxy_pass http://codepulse/docs;
    }

    location /openapi.json {
        proxy_pass http://codepulse/openapi.json;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/codepulse /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 5. SSL with Let's Encrypt

```bash
sudo apt-get install certbot python3-certbot-nginx
sudo certbot --nginx -d api.codepulse.ai
```

---

## Docker Deployment (Recommended)

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY api/ api/
COPY scanner/ scanner/

# Expose port
EXPOSE 8000

# Run FastAPI
CMD ["gunicorn", "api.main:app", \
     "--workers=4", \
     "--worker-class=uvicorn.workers.UvicornWorker", \
     "--bind=0.0.0.0:8000"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: codepulse
      POSTGRES_USER: codepulse_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  api:
    build: .
    environment:
      DATABASE_URL: postgresql://codepulse_user:secure_password@postgres:5432/codepulse
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
    command: >
      sh -c "python -c 'from api.db.database import Base, engine; Base.metadata.create_all(bind=engine)' &&
             gunicorn api.main:app --workers=4 --worker-class=uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000"

  celery:
    build: .
    environment:
      DATABASE_URL: postgresql://codepulse_user:secure_password@postgres:5432/codepulse
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/0
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    depends_on:
      - postgres
      - redis
    command: celery -A api.tasks.celery_app worker --loglevel=info

volumes:
  postgres_data:
```

**Deploy:**
```bash
docker-compose up -d
docker-compose logs -f api
```

---

## Health Checks

### API Health
```bash
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-06-06T14:30:00",
  "version": "3.5.0"
}
```

### Database Health
```bash
python -c "from api.db.database import SessionLocal; SessionLocal().execute('SELECT 1')"
```

### Celery Health
```bash
celery -A api.tasks.celery_app inspect active
```

---

## Monitoring & Logging

### Application Logging

Configure in `api/main.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Monitoring Tools

**Prometheus Metrics** (optional):
```bash
pip install prometheus-client
pip install prometheus-fastapi-instrumentator
```

**Add to `api/main.py`:**
```python
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)
```

Access metrics: http://localhost:8000/metrics

**Health Monitoring:**
```bash
# Watch system resources
watch -n 1 'redis-cli info stats | grep connected_clients'
watch -n 1 'celery -A api.tasks.celery_app inspect active'
```

---

## Scaling

### Horizontal Scaling

**Multiple Workers:**
```bash
# Start 8 Celery workers
celery -A api.tasks.celery_app worker --concurrency=8 --loglevel=info
```

**Load Balancing:**
```nginx
upstream codepulse {
    server api1.internal:8000;
    server api2.internal:8000;
    server api3.internal:8000;
}
```

### Queue Management

**Check queue depth:**
```bash
redis-cli LLEN celery
```

**Purge queue (DANGER - removes all pending jobs):**
```bash
celery -A api.tasks.celery_app purge
```

---

## Backup & Recovery

### Database Backup

```bash
# PostgreSQL
pg_dump -U codepulse_user codepulse > backup_$(date +%Y%m%d).sql

# Restore
psql -U codepulse_user codepulse < backup_20260606.sql
```

### Redis Persistence

Redis snapshots saved automatically. Verify:
```bash
redis-cli BGSAVE
redis-cli LASTSAVE
```

---

## Troubleshooting

### Issue: "Connection refused" on Redis

```bash
# Check Redis is running
redis-cli ping
# Output should be: PONG

# If not running, start it
redis-server
```

### Issue: Database migration fails

```bash
# Check database connection
python -c "from api.db.database import engine; print(engine.execute('SELECT 1'))"

# Recreate tables
python -c "from api.db.database import Base, engine; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
```

### Issue: Celery workers not processing

```bash
# Check worker status
celery -A api.tasks.celery_app inspect active

# View logs
celery -A api.tasks.celery_app inspect revoked

# Restart workers
pkill -f celery
celery -A api.tasks.celery_app worker --loglevel=debug
```

### Issue: Jobs stuck in "processing"

```bash
# Check Redis for stuck tasks
redis-cli KEYS '*'

# Purge queue (if safe)
celery -A api.tasks.celery_app purge
```

---

## Performance Tuning

### Database

```sql
-- Create indexes for faster queries
CREATE INDEX idx_iteration_jobs_status ON iteration_jobs(status);
CREATE INDEX idx_iteration_jobs_created ON iteration_jobs(created_at);
CREATE INDEX idx_iteration_history_job_id ON iteration_history(job_id);
```

### Redis

```bash
# Check memory usage
redis-cli INFO memory

# Increase max memory if needed
redis-cli CONFIG SET maxmemory 2gb
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

### Celery

```bash
# Tune worker concurrency based on CPU cores
celery -A api.tasks.celery_app worker --concurrency=4  # Match CPU count

# Use prefork for better stability
celery -A api.tasks.celery_app worker --pool=prefork
```

---

## Security Checklist

- [ ] Set strong `ANTHROPIC_API_KEY`
- [ ] Enable HTTPS with valid certificate
- [ ] Configure database password (strong)
- [ ] Restrict Redis to localhost only
- [ ] Enable API authentication (when added)
- [ ] Set up firewall rules (allow 80, 443 only)
- [ ] Regular database backups
- [ ] Log monitoring and alerting
- [ ] Rate limiting enabled
- [ ] CORS properly configured

---

## Upgrade Path

### From Development to Production

1. ✅ Test in staging environment
2. ✅ Backup production database
3. ✅ Run database migrations
4. ✅ Deploy new code
5. ✅ Restart services
6. ✅ Verify health checks
7. ✅ Monitor error logs

**Zero-Downtime Deployment:**
```bash
# 1. Start new workers in parallel
celery -A api.tasks.celery_app worker --hostname=new_worker@%h

# 2. Drain old workers
celery -A api.tasks.celery_app control shutdown new_worker

# 3. Deploy new code
git pull origin main

# 4. Restart old workers
celery -A api.tasks.celery_app worker
```

---

## Support

For issues, check:
1. Application logs: `docker-compose logs api`
2. Celery logs: `docker-compose logs celery`
3. Database logs: `docker-compose logs postgres`
4. Redis logs: `docker-compose logs redis`

---

**Deployment Complete ✅**

Monitor dashboard: http://your-domain.com/docs

