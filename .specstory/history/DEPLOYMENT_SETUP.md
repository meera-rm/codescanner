---
created_at: 2026-06-12T18:16:43Z
title: Deployment Setup
source: claude-code
project: codescanner
---

# Path I: Local Development & Deployment Setup Guide

**Status:** Production-Ready  
**Version:** Phase I.0 - Deployment Prep  
**Date:** 2026-06-06

---

## Quick Start (5 minutes)

### 1. Clone & Install

```bash
# Clone repository
git clone <repo-url>
cd codescanner

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r api/requirements.txt
pip install -r requirements-dev.txt

# Install Node dependencies (frontend)
cd frontend && npm install && cd ..
```

### 2. Configure Environment

```bash
# Copy template
cp .env.template .env

# Edit with your values
nano .env
# OR
open .env  # macOS
```

**Required for Path I:**
```env
TEAM_AGGREGATION_CACHE_TTL=3600          # Cache team scores for 1 hour
TREND_HISTORY_DAYS=90                    # Keep 90 days of trend data
CAQI_HISTORY_COMPRESSION=true            # Auto-compress old data
```

### 3. Initialize Database

```bash
# The database auto-initializes on first API start
# (SQLAlchemy creates tables if they don't exist)

# Verify database connection
python3 -c "from api.db.database import engine; print('✅ Database connected')"
```

### 4. Register a Team (Required!)

```bash
# Run the team registration script
python3 scripts/register_team.py

# OR manually register via Python
python3 << 'EOF'
from api.db.database import SessionLocal
from api.services.team_service import TeamService

db = SessionLocal()
team = TeamService.create_team(
    db=db,
    team_id="team-001",
    team_name="My Team",
    developer_ids=["dev1@example.com", "dev2@example.com"]
)
print(f"✅ Team created: {team.team_name} ({team.team_id})")
EOF
```

### 5. Start the Backend

```bash
# From root directory
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

### 6. Start the Frontend

```bash
cd frontend
npm start
```

**Expected output:**
```
Compiled successfully!
You can now view codescanner in the browser.
Local: http://localhost:3000
```

### 7. Verify Everything Works

```bash
# Check API health
curl http://localhost:8000/api/v1/health

# Check frontend loads
open http://localhost:3000
# OR
curl http://localhost:3000 | head -20
```

---

## Full Development Setup

### Prerequisites

**Required:**
- Python 3.8+ (tested on 3.12.2)
- Node.js 18+ (tested on npm 11.12.1)
- PostgreSQL 12+ OR SQLite (built-in)
- Redis 6+ (if using Celery tasks)

**Verify:**
```bash
python3 --version  # Should be 3.8+
node --version     # Should be 18+
npm --version      # Should be 8+
```

### Environment Variables (Detailed)

Create `.env` based on `.env.template`:

**Database Configuration:**
```env
# PostgreSQL (Production)
DATABASE_URL=postgresql://codepulse_user:password@localhost:5432/codepulse

# OR SQLite (Development)
DATABASE_URL=sqlite:///./codepulse.db
```

**API Server:**
```env
API_HOST=0.0.0.0              # Listen on all interfaces
API_PORT=8000                 # Port for API
DEBUG=false                   # Set to true for development
LOG_LEVEL=INFO                # Set to DEBUG for verbose logs
```

**Path I: CAQI Team Analytics (NEW)**
```env
# Team Aggregation
TEAM_AGGREGATION_CACHE_TTL=3600        # Cache team CAQI scores for 1 hour
                                        # Set to 300 for development (5 min)

# Trend Analysis
TREND_HISTORY_DAYS=90                  # Keep 90 days of history
                                        # For testing: use 30 DAYS

# Data Management
CAQI_HISTORY_COMPRESSION=true          # Auto-compress old monthly data
                                        # Reduces database size over time
```

**Optional Services:**
```env
# Redis (for Celery tasks)
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# AI/Claude API
ANTHROPIC_API_KEY=sk-xxx-your-key-here

# GitHub Integration (Phase 4)
# GITHUB_CLIENT_ID=xxx
# GITHUB_CLIENT_SECRET=xxx

# Slack Integration (Phase 4)
# SLACK_BOT_TOKEN=xoxb-xxx
# SLACK_SIGNING_SECRET=xxx
```

### Installation Steps

#### Step 1: Backend Setup

```bash
# Create venv
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r api/requirements.txt
pip install -r requirements-dev.txt

# Verify imports
python3 -c "from api.db.database import Base; print('✅ Backend ready')"
```

#### Step 2: Frontend Setup

```bash
cd frontend
npm install
npm run build  # Optional: verify build works
cd ..
```

#### Step 3: Database Setup

```bash
# For PostgreSQL (create user and database first):
createuser codepulse_user
createdb -O codepulse_user codepulse

# For SQLite: no setup needed, auto-created on first run

# Verify connection
python3 << 'EOF'
from api.db.database import engine
from sqlalchemy import text
result = engine.execute(text("SELECT 1"))
print("✅ Database connected")
EOF
```

#### Step 4: Initialize Database Tables

The API automatically creates tables on startup via SQLAlchemy:

```bash
# Tables are created when you first start the API server
# (Base.metadata.create_all(bind=engine) in api/main.py)

# You can also manually trigger:
python3 << 'EOF'
from api.db.database import engine, Base
Base.metadata.create_all(bind=engine)
print("✅ Database tables created")
EOF
```

#### Step 5: Team Registration

**Critical:** Teams must be registered before testing APIs.

```bash
# Option 1: Use registration script
python3 scripts/register_team.py

# Option 2: Manual registration
python3 << 'EOF'
from api.db.database import SessionLocal
from api.models.team import Team
from api.models.team_member import TeamMember

db = SessionLocal()

# Create team
team = Team(
    team_id="team-001",
    team_name="Engineering Team",
    created_at=datetime.utcnow()
)
db.add(team)
db.commit()

# Add team members
members = [
    TeamMember(team_id="team-001", developer_id="alice@example.com", role="lead"),
    TeamMember(team_id="team-001", developer_id="bob@example.com", role="contributor"),
]
db.add_all(members)
db.commit()

print(f"✅ Team registered: {team.team_name}")
EOF
```

---

## Running the Application

### Development Mode

```bash
# Terminal 1: Backend
source venv/bin/activate
python3 -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend && npm start

# Terminal 3: Optional - Run tests
pytest tests/ -v
npm test --prefix frontend
```

### Production Mode

```bash
# Backend (use Gunicorn for production)
gunicorn --workers 4 --bind 0.0.0.0:8000 api.main:app

# Frontend (build static assets)
cd frontend && npm run build
# Serve build/ via nginx or static file server
```

---

## Running Tests

### Backend Tests

```bash
# All tests
pytest tests/ -v

# Phase I.1 tests (services)
pytest tests/test_team_aggregation.py -v

# Phase I.2 tests (API)
pytest tests/test_caqi_api.py -v

# With coverage
pytest tests/ --cov=api --cov-report=html
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test

# With coverage
npm test -- --coverage

# Run specific test file
npm test CAQIRadarChart.test.tsx
```

### E2E Tests

```bash
cd frontend

# Run Playwright tests
npm run test:e2e

# Run specific test
npm run test:e2e -- dashboard.spec.ts

# Headed mode (see browser)
npm run test:e2e -- --headed
```

---

## Verification Checklist

After setup, verify each component:

### ✅ Backend

```bash
# API running?
curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy", "timestamp": "..."}

# Database connected?
curl -s http://localhost:8000/api/v1/caqi/team/team-001 -H "Authorization: Bearer test"
# Expected: 200 OK or team data

# Services initialized?
python3 -c "from api.services.team_aggregation import TeamAggregationService; print('✅')"
```

### ✅ Frontend

```bash
# Frontend loads?
open http://localhost:3000
# Expected: Dashboard page with tabs

# Tests pass?
npm test -- --watchAll=false
# Expected: 59 tests passed

# Build succeeds?
npm run build
# Expected: build/ folder created
```

### ✅ Database

```bash
# Tables created?
python3 << 'EOF'
from api.db.database import SessionLocal
from api.models.team import Team

db = SessionLocal()
teams = db.query(Team).all()
print(f"✅ {len(teams)} teams in database")
EOF

# Teams registered?
# Expected: At least 1 team from register_team.py
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'api'`

**Fix:**
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r api/requirements.txt
```

### Issue: Database connection refused

**Fix:**
```bash
# Check if DATABASE_URL is correct
cat .env | grep DATABASE_URL

# For SQLite: ensure it's not locked
rm codepulse.db
python3 << 'EOF'
from api.db.database import engine, Base
Base.metadata.create_all(bind=engine)
EOF

# For PostgreSQL: verify server is running
pg_isready -h localhost -p 5432
```

### Issue: Port 8000 already in use

**Fix:**
```bash
# Kill process using port 8000
lsof -i :8000
kill -9 <PID>

# OR use different port
python3 -m uvicorn api.main:app --port 8001
```

### Issue: Frontend can't reach API

**Fix:**
```bash
# Check CORS configuration in api/main.py
# Verify API is running on correct host/port

# Frontend uses http://localhost:8000
# If API is on different port, update frontend/.env:
echo "REACT_APP_API_URL=http://localhost:8000" > frontend/.env.local
```

### Issue: Tests failing with ResizeObserver error

**Fix:**
```bash
# Already handled in frontend/setupTests.ts
# If error persists, reinstall dependencies:
cd frontend && npm install && npm test
```

---

## Production Deployment

### Pre-Deployment (1 Week Before)

- [ ] All tests passing (86 tests: 59 frontend + 27 backend)
- [ ] CAQI scores verified on staging data
- [ ] Trend detection working correctly
- [ ] Database migration tested on staging backup
- [ ] Performance tested: API < 500ms, frontend < 2s load

### Deployment Day

1. **Backup database**
   ```bash
   pg_dump codepulse > codepulse_backup_2026-06-06.sql
   ```

2. **Migrate database** (if needed)
   ```bash
   # Current: Auto-migration via SQLAlchemy
   # No manual migration required—tables created on startup
   ```

3. **Deploy backend**
   ```bash
   git pull origin main
   source venv/bin/activate
   pip install -r api/requirements.txt
   gunicorn --workers 4 --bind 0.0.0.0:8000 api.main:app &
   ```

4. **Deploy frontend**
   ```bash
   cd frontend
   npm run build
   # Serve build/ via nginx or CDN
   ```

5. **Register production teams**
   ```bash
   python3 scripts/register_team.py --env production
   ```

6. **Verify endpoints**
   ```bash
   # Health check
   curl https://api.example.com/api/v1/health
   
   # CAQI endpoint
   curl https://api.example.com/api/v1/caqi/team/team-001
   ```

### Post-Deployment Monitoring (First Week)

- [ ] API response time < 500ms (check monitoring)
- [ ] No errors in logs (tail -f api.log)
- [ ] CAQI scores updating correctly
- [ ] Trend detection working (check last 7 days)
- [ ] Frontend loads < 2 seconds
- [ ] Team members can access dashboard

---

## Next Steps

1. **Local Development:** Follow Quick Start (5 min)
2. **Run Tests:** `pytest tests/` + `npm test` (verify everything works)
3. **Explore API:** `curl http://localhost:8000/docs` (Swagger UI)
4. **Review Documentation:**
   - `PATH_I_OVERVIEW.md` — Architecture overview
   - `CONVERSATION_SESSION_PHASE_I_0_SETUP.md` — Database schema
   - `CONVERSATION_SESSION_PHASE_I_1_DATA_LAYER.md` — Services
   - `TEST_RESULTS_SUMMARY.md` — All test results

---

## Questions?

See deployment checklist in `PATH_I_CAQI_ENHANCED_IMPLEMENTATION_PLAN.md` for detailed deployment procedure.

**Status:** ✅ Production-Ready  
**Last Updated:** 2026-06-06
