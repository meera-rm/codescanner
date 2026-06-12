# Path I: Deployment Checklist

**Status:** Production-Ready  
**Version:** Phase I.0 - Deployment Prep  
**Date:** 2026-06-06  
**Target:** All phases I.0 through I.4 complete and tested

---

## Pre-Deployment Phase (1 Week Before)

### Code & Testing

- [ ] **All tests passing**
  ```bash
  pytest tests/ -v              # 27 backend tests
  npm test --prefix frontend   # 59 frontend tests
  # Expected: 86 tests, 100% pass rate
  ```

- [ ] **TypeScript strict mode**
  ```bash
  cd frontend && npx tsc --noEmit
  # Expected: 0 errors
  ```

- [ ] **Build succeeds**
  ```bash
  cd frontend && npm run build
  # Expected: build/ folder created, no errors
  ```

- [ ] **No security vulnerabilities**
  ```bash
  npm audit --prefix frontend        # Check npm packages
  pip install safety && safety check  # Check pip packages
  # Expected: 0 vulnerabilities
  ```

- [ ] **Code review completed**
  - [ ] Backend services reviewed
  - [ ] REST API contract reviewed
  - [ ] Frontend components reviewed
  - [ ] Database migrations reviewed

### Documentation

- [ ] **DEPLOYMENT_SETUP.md reviewed** (local setup works end-to-end)
- [ ] **DATABASE_MIGRATION.md reviewed** (backup/restore tested on staging)
- [ ] **README.md updated** with Path I info
- [ ] **API docs generated** (`/docs` endpoint works)
- [ ] **Team onboarding guide ready**

### Infrastructure

- [ ] **Production database created**
  ```bash
  createdb codepulse_production
  createuser codepulse_prod_user
  ```

- [ ] **Database backup tested**
  ```bash
  pg_dump codepulse_production > backup_pre_deploy.sql
  # Verify can restore: psql codepulse_test < backup_pre_deploy.sql
  ```

- [ ] **Environment variables configured** (.env prepared)
- [ ] **API server ready** (port 8000, or configured)
- [ ] **Frontend hosting ready** (Vercel, nginx, or CDN)
- [ ] **SSL certificates installed** (if using HTTPS)

### Monitoring & Logging

- [ ] **Error logging configured**
- [ ] **Performance monitoring ready** (track API latency)
- [ ] **Health check endpoint verified** (`/api/v1/health`)
- [ ] **Deployment rollback procedure documented**

---

## Deployment Day (2-3 hours)

### 1. Pre-Deployment Verification (30 minutes)

```bash
# 1. Verify backup exists
ls -lh codepulse_production_backup*.sql
# Expected: Recent backup file

# 2. Verify code is ready
git status
# Expected: Clean working directory

# 3. Verify tests still pass
pytest tests/ -q && npm test --prefix frontend --watchAll=false
# Expected: All tests pass

# 4. Stop current API (if running)
pkill -f uvicorn
sleep 5

# 5. Stop current frontend (if running)
pkill -f "npm start"
sleep 5
```

### 2. Backend Deployment (30 minutes)

```bash
# 1. Pull latest code
git pull origin main

# 2. Install/update dependencies
source venv/bin/activate
pip install -r api/requirements.txt
pip install -r requirements-dev.txt

# 3. Verify database migrations (auto-creates tables)
python3 << 'EOF'
from api.db.database import engine, Base
print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("✅ Tables created/verified")
EOF

# 4. Verify database connection
python3 -c "from api.db.database import SessionLocal; db = SessionLocal(); print('✅ Database connected')"

# 5. Start API server
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
sleep 5

# 6. Verify API is running
curl http://localhost:8000/api/v1/health
# Expected: {"status": "healthy", ...}
```

### 3. Team Registration (15 minutes)

**CRITICAL: Teams must be registered before testing CAQI APIs**

```bash
# Option 1: Interactive registration
python3 scripts/register_team.py

# Option 2: Sample teams (for testing)
python3 scripts/register_team.py --sample

# Option 3: Production teams (edit script first)
python3 scripts/register_team.py --env production

# Verify teams registered
python3 scripts/register_team.py --verify
# Expected: At least 1 team listed
```

### 4. Frontend Deployment (30 minutes)

```bash
# 1. Build frontend
cd frontend
npm run build
# Expected: build/ folder created

# 2. Test build locally
npm install -g serve
serve -s build -l 3000 &
sleep 5

# 3. Verify frontend loads
curl http://localhost:3000 | head -10
# Expected: HTML content

# 4. Deploy to production
# (Exact process depends on your hosting)
# Examples:
#   - Vercel: vercel deploy --prod
#   - Nginx: cp -r build/* /var/www/html/
#   - S3: aws s3 sync build/ s3://bucket-name/

# 5. Kill local serve
pkill -f "serve -s"
```

### 5. Smoke Tests (15 minutes)

```bash
# Check API endpoints
echo "Testing API endpoints..."

# Health check
curl http://api.example.com/api/v1/health | jq .
# Expected: {"status": "healthy"}

# Get first team
curl http://api.example.com/api/v1/caqi/team/team-001 | jq .
# Expected: Team data with CAQI score

# Get team comparison
curl http://api.example.com/api/v1/caqi/comparison | jq .
# Expected: Comparison of all teams

# Get trend analysis
curl http://api.example.com/api/v1/caqi/trend/team-001 | jq .
# Expected: Trend data for last 90 days

# Get archetype profiles
curl http://api.example.com/api/v1/caqi/archetype/reckless-optimist | jq .
# Expected: Archetype definition and team members

# Frontend check
curl https://example.com | grep -q "CAQI Dashboard"
# Expected: Dashboard HTML returned
```

---

## Post-Deployment Phase (First Week)

### Day 1: Monitoring

```bash
# Every 1 hour for first 8 hours:

# 1. Check API health
curl -s http://api.example.com/api/v1/health | jq .

# 2. Check error logs
tail -50 /var/log/codepulse/api.log | grep ERROR

# 3. Check frontend loads
curl -s https://example.com | wc -c  # Should be > 10KB

# 4. Check API response time
time curl http://api.example.com/api/v1/caqi/comparison > /dev/null
# Expected: < 500ms
```

### Days 2-7: Validation

- [ ] **CAQI scores updating** (check team_scores table daily)
  ```bash
  psql codepulse_production -c "SELECT team_id, overall_caqi, calculated_at FROM team_scores ORDER BY calculated_at DESC LIMIT 5"
  # Expected: Scores updated in last 24 hours
  ```

- [ ] **Trend detection working** (new data points every day)
  ```bash
  psql codepulse_production -c "SELECT COUNT(*) FROM caqi_history WHERE recorded_at > NOW() - INTERVAL '1 day'"
  # Expected: At least 1 new record per team per day
  ```

- [ ] **No API errors** (check logs)
  ```bash
  grep ERROR /var/log/codepulse/api.log | wc -l
  # Expected: 0 or very low count
  ```

- [ ] **Frontend performance good** (monitor load time)
  ```bash
  # Test from production domain
  curl -o /dev/null -s -w "%{time_total}s\n" https://example.com
  # Expected: < 2 seconds
  ```

- [ ] **Team members can access** (test with real users)
  - [ ] Can load dashboard
  - [ ] Can see CAQI scores
  - [ ] Can view trends
  - [ ] Can see team comparison

### Week 1: Full Validation

- [ ] **All 86 tests pass** (re-run on production code)
- [ ] **Zero critical errors** in logs
- [ ] **API latency < 500ms** (check metrics)
- [ ] **Frontend load time < 2s** (check RUM metrics)
- [ ] **Database size reasonable** (not growing unexpectedly)
- [ ] **Team engagement** (teams registered, accessing dashboard)

---

## Rollback Procedure (If Something Breaks)

### Immediate Actions

```bash
# 1. Alert team
echo "⚠️  ROLLBACK IN PROGRESS - notify @oncall"

# 2. Stop current services
pkill -f uvicorn
pkill -f "npm start"
sleep 5

# 3. Restore database from backup
psql -c "DROP DATABASE codepulse_production"
psql -f codepulse_production_backup_YYYY-MM-DD.sql
# Verify
psql codepulse_production -c "SELECT COUNT(*) FROM teams"

# 4. Revert code
git reset --hard <previous-working-commit>
pip install -r api/requirements.txt

# 5. Restart services
python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8000 &
# Deploy previous frontend version

# 6. Run smoke tests
curl http://localhost:8000/api/v1/health
```

### Post-Rollback Investigation

- [ ] Identify what broke
- [ ] Review deployment logs
- [ ] Check Git diff from last working version
- [ ] Run tests locally to reproduce issue
- [ ] Fix issue in development
- [ ] Re-test on staging before redeployment

---

## Deployment Checklist

### Pre-Deployment

- [ ] All 86 tests passing (59 frontend + 27 backend)
- [ ] 0 TypeScript errors
- [ ] 0 security vulnerabilities
- [ ] Code review completed
- [ ] Documentation reviewed
- [ ] Database backup tested
- [ ] Environment variables prepared
- [ ] Rollback procedure documented

### Deployment Day

- [ ] Backend code deployed
- [ ] Database migrations applied
- [ ] Tables verified created
- [ ] Teams registered
- [ ] Frontend code deployed
- [ ] Smoke tests passing
- [ ] Health check passing
- [ ] CAQI endpoints working

### Post-Deployment

- [ ] Monitoring active
- [ ] No critical errors
- [ ] API latency < 500ms
- [ ] Frontend load time < 2s
- [ ] Teams registered and using dashboard
- [ ] Trend detection working
- [ ] Database growing normally
- [ ] Team notified of completion

---

## Estimated Timeline

| Phase | Duration | Tasks |
|-------|----------|-------|
| Pre-Deployment | 1 week | Testing, docs, infra setup |
| Deployment | 2-3 hours | Code, DB, team registration |
| Smoke Tests | 15 min | Verify all endpoints |
| Day 1 Monitoring | 8 hours | Hourly health checks |
| Days 2-7 | Ongoing | Daily validation |
| Week 1+ | Ongoing | Production monitoring |

---

## Contact & Escalation

**Deployment Team:**
- Backend Lead: [Name]
- Frontend Lead: [Name]
- DevOps: [Name]
- On-Call: [Slack channel] #oncall

**Escalation Path:**
1. Check logs
2. Review recent changes
3. Rollback if critical
4. Notify team

---

## Success Criteria

✅ **Deployment is successful when:**

1. All endpoints responding (< 500ms)
2. No errors in logs (first hour)
3. Teams registered and accessing dashboard
4. CAQI scores visible on dashboard
5. Trends updating correctly
6. Frontend load time < 2 seconds
7. Zero critical issues reported

✅ **Path I is production-ready when:**

1. ✅ All 86 tests passing
2. ✅ 93.58% frontend coverage
3. ✅ 100% backend service coverage
4. ✅ 0 TypeScript errors
5. ✅ 0 security vulnerabilities
6. ✅ Database migrations verified
7. ✅ Documentation complete
8. ✅ Team registration working
9. ✅ Deployment checklist complete

---

## After Deployment: Next Steps

**Phase I is complete.** Path forward:

- **Phase II:** Advanced analytics (architecture analysis, git metrics)
- **Phase III:** AI-powered suggestions (auto-fix, refactoring)
- **Phase IV:** Multi-agent system (collaborative analysis)

See `PATH_I_CAQI_ENHANCED_IMPLEMENTATION_PLAN.md` for full roadmap.

---

**Status:** ✅ Production-Ready  
**Last Updated:** 2026-06-06
