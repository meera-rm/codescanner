# Path I: Database Migration Guide

**Status:** Production-Ready  
**Version:** Phase I.0 - Deployment Prep  
**Date:** 2026-06-06  
**Approach:** SQLAlchemy Auto-Migration (Development) → Alembic (Production-Ready)

---

## Overview

Path I uses SQLAlchemy ORM with two migration strategies:

1. **Auto-Migration** (Development): Tables created automatically on startup
2. **Alembic** (Production): Manual version control for database changes

Current deployment uses **auto-migration** for simplicity. For production with multiple environments, migrate to **Alembic**.

---

## Current Approach: SQLAlchemy Auto-Migration

### How It Works

**Database tables are created automatically when the API starts:**

```python
# api/main.py (line 73)
Base.metadata.create_all(bind=engine)
```

**This:**
- ✅ Creates all tables if they don't exist
- ✅ Adds new columns if ORM models change
- ✅ Zero downtime deployment
- ✅ Works with SQLite and PostgreSQL

**Limitations:**
- ❌ Cannot drop columns automatically
- ❌ Cannot rename tables automatically
- ❌ No version history
- ❌ Risky for large databases with concurrent access

---

## Path I Database Schema

### Tables Created

**1. teams** — Team definitions
```sql
CREATE TABLE teams (
    team_id VARCHAR PRIMARY KEY,
    team_name VARCHAR NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**2. team_members** — Team membership
```sql
CREATE TABLE team_members (
    id SERIAL PRIMARY KEY,
    team_id VARCHAR NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    developer_id VARCHAR NOT NULL,
    role VARCHAR DEFAULT 'contributor',
    joined_at TIMESTAMP NOT NULL,
    UNIQUE(team_id, developer_id)
);
```

**3. metrics** — Individual developer metrics
```sql
CREATE TABLE metrics (
    id SERIAL PRIMARY KEY,
    developer_id VARCHAR NOT NULL,
    team_id VARCHAR REFERENCES teams(team_id) ON DELETE CASCADE,
    security INTEGER DEFAULT 50,
    complexity INTEGER DEFAULT 50,
    documentation INTEGER DEFAULT 50,
    testing INTEGER DEFAULT 50,
    dependencies INTEGER DEFAULT 50,
    maintainability INTEGER DEFAULT 50,
    recorded_at TIMESTAMP NOT NULL,
    UNIQUE(developer_id, team_id, recorded_at)
);
```

**4. team_scores** — Team-level CAQI scores
```sql
CREATE TABLE team_scores (
    id SERIAL PRIMARY KEY,
    team_id VARCHAR NOT NULL UNIQUE REFERENCES teams(team_id) ON DELETE CASCADE,
    overall_caqi FLOAT DEFAULT 0,
    security FLOAT DEFAULT 0,
    complexity FLOAT DEFAULT 0,
    documentation FLOAT DEFAULT 0,
    testing FLOAT DEFAULT 0,
    dependencies FLOAT DEFAULT 0,
    maintainability FLOAT DEFAULT 0,
    calculated_at TIMESTAMP NOT NULL
);
```

**5. caqi_history** — Historical CAQI scores (90-day rolling window)
```sql
CREATE TABLE caqi_history (
    id SERIAL PRIMARY KEY,
    team_id VARCHAR NOT NULL REFERENCES teams(team_id) ON DELETE CASCADE,
    overall_caqi FLOAT NOT NULL,
    security FLOAT NOT NULL,
    complexity FLOAT NOT NULL,
    documentation FLOAT NOT NULL,
    testing FLOAT NOT NULL,
    dependencies FLOAT NOT NULL,
    maintainability FLOAT NOT NULL,
    recorded_at TIMESTAMP NOT NULL,
    is_compressed BOOLEAN DEFAULT FALSE,
    UNIQUE(team_id, recorded_at)
);

CREATE INDEX idx_caqi_history_team_date ON caqi_history(team_id, recorded_at DESC);
```

### Relationships

```
teams (1) ──→ (many) team_members
teams (1) ──→ (many) metrics
teams (1) ──→ (1) team_scores
teams (1) ──→ (many) caqi_history
```

**Cascade Delete:** Removing a team deletes all related metrics, scores, and history automatically.

---

## Deployment Scenarios

### Scenario 1: Fresh Deployment (New Database)

**Step 1: Create database**
```bash
# PostgreSQL
createdb codepulse
createuser codepulse_user
psql codepulse -c "ALTER USER codepulse_user WITH PASSWORD 'password'"
psql codepulse -c "GRANT ALL PRIVILEGES ON DATABASE codepulse TO codepulse_user"

# SQLite: auto-created
```

**Step 2: Start API (tables auto-created)**
```bash
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Step 3: Verify**
```bash
# Check tables created
python3 << 'EOF'
from api.db.database import engine, Base
from sqlalchemy import inspect

inspector = inspect(engine)
tables = inspector.get_table_names()
print(f"✅ Tables created: {tables}")
EOF
```

### Scenario 2: Existing Database (Upgrade)

**Step 1: Backup**
```bash
# PostgreSQL
pg_dump codepulse > codepulse_backup_2026-06-06.sql

# SQLite
cp codepulse.db codepulse_backup_2026-06-06.db
```

**Step 2: Stop API**
```bash
# Kill running uvicorn process
pkill -f uvicorn
```

**Step 3: Deploy new code**
```bash
git pull origin main
pip install -r api/requirements.txt
```

**Step 4: Start API (tables auto-upgraded)**
```bash
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

**Step 5: Verify**
```bash
# Check all tables exist
python3 << 'EOF'
from api.db.database import SessionLocal
from api.models.team import Team

db = SessionLocal()
teams = db.query(Team).count()
print(f"✅ Database ready: {teams} teams")
db.close()
EOF
```

### Scenario 3: Rollback (If Migration Fails)

**Step 1: Stop API**
```bash
pkill -f uvicorn
```

**Step 2: Restore backup**
```bash
# PostgreSQL
psql codepulse < codepulse_backup_2026-06-06.sql

# SQLite
rm codepulse.db && cp codepulse_backup_2026-06-06.db codepulse.db
```

**Step 3: Revert code**
```bash
git reset --hard <previous-commit-sha>
pip install -r api/requirements.txt
```

**Step 4: Restart**
```bash
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000
```

---

## Upgrading to Alembic (Recommended for Production)

As the database grows, use **Alembic** for version-controlled migrations.

### Setup Alembic

```bash
# Install Alembic
pip install alembic

# Initialize Alembic
alembic init migrations

# Configure database URL in migrations/env.py
```

### Create Initial Migration

```bash
# Generate migration from current ORM models
alembic revision --autogenerate -m "Initial Path I schema"

# Review generated migration
cat migrations/versions/<timestamp>_initial_path_i_schema.py

# Apply migration
alembic upgrade head
```

### Workflow for Future Changes

```bash
# 1. Update ORM model in api/models/
# 2. Generate migration
alembic revision --autogenerate -m "Add new_field to team_scores"

# 3. Review migration file
# 4. Test on staging
alembic upgrade head

# 5. Deploy to production
alembic upgrade head
```

### Example: Adding a New Column

**1. Update ORM model:**
```python
# api/models/team_score.py
class TeamScore(Base):
    ...
    last_updated_by = Column(String, nullable=True)  # New field
```

**2. Generate migration:**
```bash
alembic revision --autogenerate -m "Add last_updated_by to team_scores"
```

**3. Review migration:**
```python
# migrations/versions/2026_06_06_add_last_updated_by.py
def upgrade():
    op.add_column('team_scores', sa.Column('last_updated_by', sa.String(), nullable=True))

def downgrade():
    op.drop_column('team_scores', 'last_updated_by')
```

**4. Test:**
```bash
alembic upgrade head
# Verify new column exists
```

**5. Deploy:**
```bash
# Code deployed with migration
# Run on production: alembic upgrade head
```

---

## Data Preservation During Migration

### Backup Strategy

**Daily backups:**
```bash
# Create daily backup script
cat > /usr/local/bin/backup_codepulse.sh << 'EOF'
#!/bin/bash
TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
pg_dump codepulse > /backups/codepulse_$TIMESTAMP.sql
gzip /backups/codepulse_$TIMESTAMP.sql
# Keep last 30 days
find /backups -name "codepulse_*.sql.gz" -mtime +30 -delete
EOF

chmod +x /usr/local/bin/backup_codepulse.sh
```

**Schedule in crontab:**
```bash
crontab -e
# Add: 0 2 * * * /usr/local/bin/backup_codepulse.sh
```

### Restore Procedure

```bash
# List available backups
ls -lh /backups/codepulse_*.sql.gz

# Restore from specific backup
gunzip -c /backups/codepulse_2026-06-05.sql.gz | psql codepulse

# Verify
psql codepulse -c "SELECT COUNT(*) FROM teams"
```

---

## Testing Migrations

### Local Testing

```bash
# Create test database
createdb codepulse_test

# Copy schema from production (optional)
pg_dump -s codepulse > schema.sql
psql codepulse_test < schema.sql

# Run migrations
alembic upgrade head

# Verify
psql codepulse_test -c "SELECT * FROM team_scores LIMIT 1"
```

### Staging Testing (Before Production)

```bash
# 1. Refresh staging database from production backup
pg_restore -d codepulse_staging codepulse_backup_2026-06-05.dump

# 2. Run migrations
alembic upgrade head

# 3. Run test suite
pytest tests/test_caqi_api.py -v

# 4. Verify API endpoints
curl http://localhost:8000/api/v1/caqi/team/team-001

# 5. Check performance
# - Query time < 100ms
# - API response time < 500ms
```

---

## Monitoring After Migration

### Verify Tables & Indexes

```bash
# Check all tables exist
psql codepulse -c "\dt"

# Check indexes
psql codepulse -c "\di"

# Check data integrity
psql codepulse << 'EOF'
SELECT 
    COUNT(*) as total_teams,
    COUNT(DISTINCT team_id) as unique_teams
FROM teams;

SELECT 
    COUNT(*) as total_scores,
    COUNT(DISTINCT team_id) as teams_with_scores
FROM team_scores;

SELECT 
    COUNT(*) as total_history,
    COUNT(DISTINCT team_id) as teams_with_history
FROM caqi_history;
EOF
```

### Performance Check

```python
# Check query performance
import time
from api.db.database import SessionLocal
from api.models.team_score import TeamScore

db = SessionLocal()

start = time.time()
scores = db.query(TeamScore).all()
elapsed = (time.time() - start) * 1000

print(f"Query time: {elapsed:.2f}ms")
print(f"Expected: < 100ms")
print(f"Status: {'✅ PASS' if elapsed < 100 else '❌ SLOW'}")
```

---

## Migration Checklist

### Before Migration

- [ ] Database backup created and tested
- [ ] Backup stored in secure location
- [ ] Rollback procedure documented
- [ ] All tests passing (86 tests)
- [ ] Staging environment ready
- [ ] Team notified of maintenance window

### During Migration

- [ ] Stop API (0 downtime if using auto-migration)
- [ ] Verify database changes
- [ ] Verify tables created
- [ ] Restart API

### After Migration

- [ ] All endpoints responding
- [ ] Health check passing
- [ ] CAQI endpoints working
- [ ] Teams registered
- [ ] Dashboard loading
- [ ] Monitor logs for errors

---

## Troubleshooting

### Issue: `Column does not exist` error after migration

**Cause:** Auto-migration didn't pick up ORM change

**Fix:**
```python
# Force table recreation
from api.db.database import engine, Base
Base.metadata.drop_all(bind=engine)  # ⚠️ WARNING: Deletes all data
Base.metadata.create_all(bind=engine)  # Recreate with new schema
```

**Better fix:** Use Alembic for controlled migrations

### Issue: `Foreign key constraint violation`

**Cause:** Deleting a team doesn't cascade to related records

**Fix:** Verify `ondelete="CASCADE"` in models
```python
# api/models/team_member.py
team_id = Column(String, ForeignKey('teams.team_id', ondelete='CASCADE'))
```

### Issue: Data loss during upgrade

**Cause:** Didn't backup before migration

**Fix:** Always backup first
```bash
pg_dump codepulse > backup_BEFORE_migration.sql
```

---

## Next Steps

1. **Verify Current Migration:** Run `DEPLOYMENT_SETUP.md` quick start
2. **Setup Backup:** Implement daily backup script
3. **Plan Alembic:** When adding new migrations, switch to Alembic
4. **Test Rollback:** Practice restore procedure on staging

---

## Reference

**ORM Models:**
- `api/models/team.py` — Team
- `api/models/team_member.py` — TeamMember
- `api/models/metric.py` — Metric
- `api/models/team_score.py` — TeamScore
- `api/models/caqi_history.py` — CAQIHistory

**Related Docs:**
- `DEPLOYMENT_SETUP.md` — Full deployment guide
- `PATH_I_CAQI_ENHANCED_IMPLEMENTATION_PLAN.md` — Deployment checklist

---

**Status:** ✅ Production-Ready  
**Last Updated:** 2026-06-06
