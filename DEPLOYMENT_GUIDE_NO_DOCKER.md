# CodePulse AI - Deployment Guide (No Docker)

Traditional deployment guide for production servers without Docker.

---

## Prerequisites

### System Requirements
- **OS:** Ubuntu 20.04 LTS or similar Linux
- **RAM:** 2GB minimum (4GB+ recommended)
- **Storage:** 5GB minimum
- **CPU:** 2 cores minimum

### Software Requirements
- Python 3.10+
- Node.js 16+
- PostgreSQL 12+
- Nginx 1.18+
- Git
- Supervisor or systemd (for process management)

### Installation
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3.10 python3-pip python3-venv
sudo apt install -y nodejs npm
sudo apt install -y postgresql postgresql-contrib
sudo apt install -y nginx
sudo apt install -y git curl
```

---

## Installation Steps

### Step 1: Clone Repository
```bash
cd /opt
sudo git clone https://github.com/company/codepulse.git
sudo chown -R $USER:$USER codepulse
cd codepulse
```

### Step 2: Setup Backend

#### Create Virtual Environment
```bash
cd api
python3 -m venv venv
source venv/bin/activate
```

#### Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### Configure Environment
```bash
cp .env.example .env
nano .env
```

**Key variables to set:**
```bash
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=info
DATABASE_URL=postgresql://user:password@localhost:5432/codepulse
SECRET_KEY=generate-strong-random-string
```

#### Create Database
```bash
# Connect to PostgreSQL
sudo -u postgres psql

# In PostgreSQL:
CREATE DATABASE codepulse;
CREATE USER codepulse_user WITH PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE codepulse TO codepulse_user;
ALTER USER codepulse_user CREATEDB;
\q
```

#### Test Backend
```bash
# Activate virtual environment
source venv/bin/activate

# Run development server (test only)
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# In another terminal, test endpoint:
curl http://localhost:8000/api/v1/analytics/health
```

### Step 3: Setup Frontend

#### Install Dependencies
```bash
cd ../frontend
npm install
```

#### Configure Environment
```bash
cp .env.example .env.production
nano .env.production
```

**Key variables:**
```bash
REACT_APP_API_URL=https://api.yourdomain.com/api/v1
NODE_ENV=production
```

#### Build Production Bundle
```bash
npm run build

# Output: build/ directory with optimized files
```

### Step 4: Configure Nginx

#### Create Nginx Configuration
```bash
sudo nano /etc/nginx/sites-available/codepulse
```

**Content:**
```nginx
upstream api_backend {
    server 127.0.0.1:8000;
}

upstream frontend_app {
    server 127.0.0.1:3000;
}

# HTTP to HTTPS redirect
server {
    listen 80;
    server_name yourdomain.com api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

# HTTPS configuration
server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    # SSL certificates
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css text/javascript application/json;
    gzip_min_length 1000;

    # Serve frontend
    location / {
        root /opt/codepulse/frontend/build;
        try_files $uri /index.html;
        
        # Cache static assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # Proxy API requests
    location /api/v1 {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 60s;
    }

    # Health check endpoint
    location /health {
        proxy_pass http://api_backend/api/v1/analytics/health;
        access_log off;
    }
}

# API domain
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # API only
    location / {
        proxy_pass http://api_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### Enable Configuration
```bash
sudo ln -s /etc/nginx/sites-available/codepulse /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### Step 5: Setup SSL Certificate

#### Install Certbot
```bash
sudo apt install -y certbot python3-certbot-nginx
```

#### Generate Certificate
```bash
sudo certbot certonly --standalone \
  -d yourdomain.com \
  -d api.yourdomain.com

# Follow prompts and agree to terms
```

#### Auto-renewal
```bash
# Test renewal
sudo certbot renew --dry-run

# Auto-renewal happens automatically via systemd timer
sudo systemctl enable certbot.timer
```

---

## Process Management

### Option 1: Using Systemd (Recommended)

#### Create Backend Service
```bash
sudo nano /etc/systemd/system/codepulse-api.service
```

**Content:**
```ini
[Unit]
Description=CodePulse API
After=network.target postgresql.service

[Service]
Type=notify
User=codepulse
WorkingDirectory=/opt/codepulse/api
Environment="PATH=/opt/codepulse/api/venv/bin"
ExecStart=/opt/codepulse/api/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Create Frontend Service
```bash
sudo nano /etc/systemd/system/codepulse-web.service
```

**Content:**
```ini
[Unit]
Description=CodePulse Web Server
After=network.target

[Service]
Type=simple
User=codepulse
WorkingDirectory=/opt/codepulse/frontend
ExecStart=/usr/bin/npx serve -s build -l 3000
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Enable Services
```bash
# Create codepulse user
sudo useradd -m codepulse
sudo chown -R codepulse:codepulse /opt/codepulse

# Enable and start services
sudo systemctl daemon-reload
sudo systemctl enable codepulse-api
sudo systemctl enable codepulse-web
sudo systemctl start codepulse-api
sudo systemctl start codepulse-web

# Check status
sudo systemctl status codepulse-api
sudo systemctl status codepulse-web
```

### Option 2: Using Supervisor

#### Install Supervisor
```bash
sudo apt install -y supervisor
```

#### Create Backend Configuration
```bash
sudo nano /etc/supervisor/conf.d/codepulse-api.conf
```

**Content:**
```ini
[program:codepulse-api]
directory=/opt/codepulse/api
command=/opt/codepulse/api/venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
user=codepulse
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/codepulse-api.log
```

#### Create Frontend Configuration
```bash
sudo nano /etc/supervisor/conf.d/codepulse-web.conf
```

**Content:**
```ini
[program:codepulse-web]
directory=/opt/codepulse/frontend
command=/usr/bin/npx serve -s build -l 3000
user=codepulse
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/codepulse-web.log
```

#### Start Services
```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start codepulse-api
sudo supervisorctl start codepulse-web
```

---

## Database Setup

### Initial Setup
```bash
# Connect as postgres user
sudo -u postgres psql

# Create database
CREATE DATABASE codepulse;
CREATE USER codepulse_user WITH PASSWORD 'strong-password';
GRANT ALL PRIVILEGES ON DATABASE codepulse TO codepulse_user;
\q
```

### Configure PostgreSQL
```bash
# Edit postgresql.conf
sudo nano /etc/postgresql/12/main/postgresql.conf

# Set: listen_addresses = '*'
# For local only: listen_addresses = 'localhost'
```

### Backup Configuration
```bash
# Create backup user
sudo useradd -m backup

# Create backup script
sudo nano /usr/local/bin/backup-codepulse.sh
```

**Content:**
```bash
#!/bin/bash

BACKUP_DIR="/var/backups/codepulse"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory if not exists
mkdir -p $BACKUP_DIR

# Backup database
sudo -u postgres pg_dump codepulse | gzip > $BACKUP_DIR/codepulse_$DATE.sql.gz

# Backup application files
tar -czf $BACKUP_DIR/codepulse_app_$DATE.tar.gz /opt/codepulse

# Keep only last 7 backups
find $BACKUP_DIR -name "codepulse_*.sql.gz" -mtime +7 -delete
find $BACKUP_DIR -name "codepulse_app*.tar.gz" -mtime +7 -delete

echo "Backup completed at $DATE"
```

**Make executable:**
```bash
sudo chmod +x /usr/local/bin/backup-codepulse.sh
```

### Schedule Daily Backups
```bash
# Edit crontab
sudo crontab -e

# Add line: 0 2 * * * /usr/local/bin/backup-codepulse.sh
# This runs backup at 2 AM daily
```

---

## Monitoring

### Health Checks
```bash
# Manual health check
curl https://api.yourdomain.com/api/v1/analytics/health

# Check service status
sudo systemctl status codepulse-api
sudo systemctl status codepulse-web

# View logs
journalctl -u codepulse-api -f
journalctl -u codepulse-web -f
```

### Setup Log Monitoring
```bash
# Install logwatch
sudo apt install -y logwatch

# Configure for CodePulse logs
sudo nano /etc/logwatch/conf/logwatch.conf
```

### Performance Monitoring
```bash
# Install monitoring tools
sudo apt install -y htop iotop nethogs

# Monitor in real-time
htop
```

### Database Monitoring
```bash
# Check database size
sudo -u postgres psql -c "SELECT pg_database.datname, pg_size_pretty(pg_database_size(pg_database.datname)) FROM pg_database ORDER BY pg_database_size(pg_database.datname);"

# Check active connections
sudo -u postgres psql -c "SELECT datname, count(*) FROM pg_stat_activity GROUP BY datname;"
```

---

## Troubleshooting

### Service Won't Start
```bash
# Check logs
sudo journalctl -u codepulse-api -n 50

# Test Python environment
source /opt/codepulse/api/venv/bin/activate
python -c "import main"
```

### Database Connection Issues
```bash
# Test connection
sudo -u postgres psql -c "SELECT 1;"

# Check PostgreSQL is running
sudo systemctl status postgresql

# Check if listening on correct port
sudo ss -tlnp | grep postgres
```

### Nginx Issues
```bash
# Check configuration
sudo nginx -t

# Check if listening on port 80/443
sudo ss -tlnp | grep nginx

# Check error logs
sudo tail -50 /var/log/nginx/error.log
```

### Port Already in Use
```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>

# Or change port in config
```

---

## Updating Application

### Deploy New Version
```bash
# Pull latest code
cd /opt/codepulse
git pull origin main

# Update backend
cd api
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart codepulse-api

# Update frontend
cd ../frontend
npm install
npm run build
sudo systemctl restart codepulse-web

# Verify
curl https://api.yourdomain.com/api/v1/analytics/health
```

---

## Scaling (Advanced)

### Load Balancing with Multiple Backends
```nginx
upstream api_pool {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location /api/v1 {
        proxy_pass http://api_pool;
    }
}
```

### Run Multiple Backend Instances
```bash
# Start multiple instances on different ports
# Modify systemd service to use BACKEND_PORT environment variable
# Or create separate services for each port
```

---

## Security Hardening

### Firewall Setup
```bash
# Enable UFW
sudo ufw enable

# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Check rules
sudo ufw status
```

### SSH Security
```bash
# Disable password authentication
sudo nano /etc/ssh/sshd_config

# Set:
# PasswordAuthentication no
# PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart ssh
```

### Database Security
```bash
# Use strong passwords
# Create database user with limited permissions
# Disable public access (bind to localhost only)
```

---

## Checklist

- [ ] Repository cloned
- [ ] Python environment created
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Database created
- [ ] Environment variables configured
- [ ] SSL certificate obtained
- [ ] Nginx configured
- [ ] Services enabled
- [ ] Health check passing
- [ ] Backups scheduled
- [ ] Monitoring configured
- [ ] Firewall configured
- [ ] Team trained on operations

---

## Support

For issues, check:
1. Service logs: `journalctl -u codepulse-api`
2. Nginx logs: `/var/log/nginx/error.log`
3. Database connection: `psql postgresql://user:pass@localhost/codepulse`
4. Application health: `curl http://localhost:8000/api/v1/analytics/health`

---

**Last Updated:** 2026-06-06  
**Alternative to Docker:** Yes ✅
