---
created_at: 2026-06-12T18:16:43Z
title: Phase I+1 Implementation Roadmap
source: claude-code
project: codescanner
---

# Phase I+1: Advanced Analytics - Implementation Roadmap

**Status:** Starting implementation  
**Date:** 2026-06-06  
**Estimated Duration:** 1-2 weeks (20-30 hours)  
**Reference:** `PHASE_I+1_ADVANCED_ANALYTICS_CORRECTED.md`

---

## Week 1: Data Layer & Services

### Day 1: Database Schema & Models

**Checklist:**
```
[ ] Create migration file: migrations/add_anomaly_detection_tables.sql
[ ] Create ORM models:
    [ ] api/models/anomaly.py
    [ ] api/models/alert.py
    [ ] api/models/developer_metric.py
    [ ] api/models/peer_group.py
    [ ] api/models/benchmark.py
[ ] Run migration: alembic upgrade head
[ ] Verify tables created in database
[ ] Create indexes for performance
```

**Files to Create:**
```
api/models/anomaly.py          (50 lines)
api/models/alert.py            (60 lines)
api/models/developer_metric.py (50 lines)
api/models/peer_group.py       (40 lines)
api/models/benchmark.py        (40 lines)
migrations/add_anomaly_*.sql   (100+ lines)
```

**Verification:**
```bash
psql codepulse -c "\dt"  # List tables
# Should show: anomalies, alerts, developer_metrics, peer_groups, benchmarks

python3 << 'EOF'
from api.models.anomaly import Anomaly
from api.db.database import SessionLocal

db = SessionLocal()
result = db.query(Anomaly).count()
print(f"✅ Anomaly table accessible, count: {result}")
EOF
```

---

### Day 2: Anomaly Detection Service

**Checklist:**
```
[ ] Create: api/services/anomaly_detection.py
[ ] Implement AnomalyDetectionService class:
    [ ] MIN_HISTORY_POINTS = 3 constant
    [ ] detect_anomalies() with validation
    [ ] get_unreviewed_anomalies()
    [ ] mark_anomaly_reviewed()
    [ ] _validate_metric_range()
[ ] Add error handling & logging
[ ] Create: tests/test_anomaly_detection_corrected.py
[ ] Run tests: pytest tests/test_anomaly_detection_corrected.py -v
```

**Files to Create:**
```
api/services/anomaly_detection.py     (250+ lines)
tests/test_anomaly_detection_corrected.py (150+ lines)
```

**Key Implementation Points:**
- Check `len(history) >= MIN_HISTORY_POINTS` before detecting
- Use `ANOMALY_THRESHOLDS` dict for severity mapping
- Validate dimension scores (0-100 range)
- Return empty list if insufficient data

**Verification:**
```bash
pytest tests/test_anomaly_detection_corrected.py -v
# Expected: 6 tests passing
# ✅ test_insufficient_history_returns_empty
# ✅ test_detects_anomaly_above_threshold
# ✅ test_calculates_severity_correctly
# ✅ test_marks_anomaly_reviewed
# ✅ test_handles_no_history_gracefully
# ✅ test_validates_metric_range
```

---

### Day 3: Peer Comparison Service

**Checklist:**
```
[ ] Create: api/services/peer_comparison.py
[ ] Implement PeerComparisonService class:
    [ ] create_peer_group()
    [ ] get_peer_comparison() with validation
    [ ] calculate_percentile() function
    [ ] calculate_benchmarks()
[ ] Add null checks & error handling
[ ] Create: tests/test_peer_comparison_corrected.py
[ ] Run tests: pytest tests/test_peer_comparison_corrected.py -v
```

**Files to Create:**
```
api/services/peer_comparison.py     (200+ lines)
tests/test_peer_comparison_corrected.py (120+ lines)
```

**Key Implementation Points:**
- Validate peer_group exists before comparing
- Handle empty peer_scores list
- Implement percentile formula correctly
- Return error dict if no data available

**Verification:**
```bash
pytest tests/test_peer_comparison_corrected.py -v
# Expected: 6 tests passing
```

---

### Day 4: Developer Drill-Down Service

**Checklist:**
```
[ ] Create: api/services/developer_drill_down.py
[ ] Implement DeveloperDrillDownService class:
    [ ] calculate_developer_contributions() - FIXED: O(n) not O(n²)
    [ ] get_top_contributors()
    [ ] _calculate_deviation()
[ ] Query ALL team metrics once (not per developer)
[ ] Create: tests/test_developer_drill_down_corrected.py
[ ] Run tests: pytest tests/test_developer_drill_down_corrected.py -v
```

**Files to Create:**
```
api/services/developer_drill_down.py     (200+ lines)
tests/test_developer_drill_down_corrected.py (120+ lines)
```

**Key Implementation Points - CRITICAL:**
```python
# DO THIS (O(n)):
all_team_metrics = db.query(Metric).filter(...).all()  # Query once
for member in members:
    dev_metrics = [m for m in all_team_metrics if ...]  # Filter in memory

# NOT THIS (O(n²)):
for member in members:
    dev_metrics = db.query(Metric).filter(...).all()  # Query per member!
```

**Verification:**
```bash
pytest tests/test_developer_drill_down_corrected.py -v
# Expected: 5 tests passing
# ⚠️ Monitor: Should have 2-3 DB queries, not N+1
```

---

### Day 5: Alerting Service

**Checklist:**
```
[ ] Create: api/services/alerting_service.py
[ ] Implement AlertingService class:
    [ ] create_alert()
    [ ] send_alert() with delegation
    [ ] _send_email_alert() - FIXED: uses EmailDigestService
    [ ] _send_slack_alert() - FIXED: uses SlackIntegrationService
    [ ] acknowledge_alert()
    [ ] get_pending_alerts()
[ ] Create: tests/test_alerting_service_corrected.py
[ ] Run tests: pytest tests/test_alerting_service_corrected.py -v
```

**Files to Create:**
```
api/services/alerting_service.py     (180+ lines)
tests/test_alerting_service_corrected.py (100+ lines)
```

**Key Implementation Points:**
- Delegate to EmailDigestService for emails
- Delegate to SlackIntegrationService for Slack
- Update alert.notification_sent_at on success
- Log failures with context

**Verification:**
```bash
pytest tests/test_alerting_service_corrected.py -v
# Expected: 5 tests passing
```

---

## Week 2: REST API & Frontend

### Day 6: REST API Endpoints

**Checklist:**
```
[ ] Create: api/routes/advanced_analytics.py
[ ] Implement 5 endpoints:
    [ ] GET /api/v1/caqi/anomalies/{team_id}
    [ ] POST /api/v1/caqi/anomalies/{anomaly_id}/review
    [ ] GET /api/v1/caqi/peer-comparison/{team_id}
    [ ] GET /api/v1/caqi/benchmarks
    [ ] GET /api/v1/caqi/developer-metrics/{team_id}
    [ ] GET /api/v1/caqi/alerts/{team_id}
    [ ] POST /api/v1/caqi/alerts/{alert_id}/acknowledge
[ ] Add error handling & validation
[ ] Register router in api/main.py
[ ] Create: tests/test_advanced_analytics_api_corrected.py
[ ] Run tests: pytest tests/test_advanced_analytics_api_corrected.py -v
```

**Files to Create:**
```
api/routes/advanced_analytics.py     (250+ lines)
tests/test_advanced_analytics_api_corrected.py (150+ lines)
```

**In api/main.py, add:**
```python
from api.routes import advanced_analytics
# ...
app.include_router(advanced_analytics.router)
```

**Verification:**
```bash
pytest tests/test_advanced_analytics_api_corrected.py -v
# Expected: 7 tests passing

# Manual test:
curl http://localhost:8000/api/v1/caqi/anomalies/team-001
curl http://localhost:8000/api/v1/caqi/peer-comparison/team-001?peer_group=backend
```

---

### Day 7: Frontend Components

**Checklist:**
```
[ ] Create: frontend/src/components/AnomalyDetectionView.tsx
[ ] Create: frontend/src/components/PeerComparisonChart.tsx
[ ] Create: frontend/src/components/DeveloperBreakdownTable.tsx
[ ] Integrate into CAQIDashboard (add tabs or panels)
[ ] Create: frontend/src/__tests__/AnomalyDetectionView.test.tsx
[ ] Create: frontend/src/__tests__/PeerComparisonChart.test.tsx
[ ] Create: frontend/src/__tests__/DeveloperBreakdownTable.test.tsx
[ ] Run tests: npm test -- --watchAll=false
```

**Files to Create:**
```
frontend/src/components/AnomalyDetectionView.tsx       (200+ lines)
frontend/src/components/PeerComparisonChart.tsx        (250+ lines)
frontend/src/components/DeveloperBreakdownTable.tsx    (200+ lines)
frontend/src/__tests__/AnomalyDetectionView.test.tsx   (100+ lines)
frontend/src/__tests__/PeerComparisonChart.test.tsx    (120+ lines)
frontend/src/__tests__/DeveloperBreakdownTable.test.tsx (120+ lines)
```

**In CAQIDashboard, add tabs:**
```tsx
<Tab label="Anomalies">
  <AnomalyDetectionView teamId={selectedTeam} />
</Tab>
<Tab label="Peer Comparison">
  <PeerComparisonChart teamId={selectedTeam} />
</Tab>
<Tab label="Developer Metrics">
  <DeveloperBreakdownTable teamId={selectedTeam} />
</Tab>
```

**Verification:**
```bash
npm test -- --watchAll=false
# Expected: 59 + 15 = 74 total tests passing

npm run build
# Expected: 0 TypeScript errors
```

---

### Day 8-10: Testing & Integration

**Checklist:**
```
[ ] Run all Phase I+1 tests together
[ ] Verify test coverage ≥85%
[ ] Run frontend tests
[ ] Run backend tests
[ ] Test API endpoints manually
[ ] Test frontend integration
[ ] Verify no N+1 queries (use django-debug-toolbar or similar)
[ ] Check for memory leaks
[ ] Code review before merging
```

**Full Test Run:**
```bash
# Backend tests
pytest tests/test_anomaly_detection_corrected.py -v
pytest tests/test_peer_comparison_corrected.py -v
pytest tests/test_developer_drill_down_corrected.py -v
pytest tests/test_alerting_service_corrected.py -v
pytest tests/test_advanced_analytics_api_corrected.py -v

# Frontend tests
npm test -- --watchAll=false

# Coverage
pytest tests/ --cov=api --cov-report=html
coverage report

# Expected: 44+ tests passing, ≥85% coverage
```

---

## Daily Checklist Template

Use this for each day:

```
DAY X: [Component]

Morning:
[ ] Review corrected plan section
[ ] Create feature branch (if not already done)
[ ] Set up test file

Development:
[ ] Implement main class
[ ] Add error handling
[ ] Add logging
[ ] Implement tests
[ ] All tests passing
[ ] Code review-ready

Afternoon:
[ ] Integration check
[ ] Performance check (no N+1 queries)
[ ] Security review
[ ] Documentation updated
[ ] Ready for next day

Status: ✅ COMPLETE
```

---

## Weekly Standup (Every Friday)

**Week 1 (Data Layer):**
```
Completed:
- [ ] Database schema (Day 1)
- [ ] Anomaly detection service (Day 2)
- [ ] Peer comparison service (Day 3)
- [ ] Developer drill-down service (Day 4)
- [ ] Alerting service (Day 5)

Metrics:
- Tests: 24 passing
- Coverage: 85%+
- Queries: O(n), no N+1
- Status: ✅ ON TRACK

Next Week:
- REST API endpoints (Day 6)
- Frontend components (Day 7)
- Integration testing (Days 8-10)
```

---

## Quality Gates (Before Merge)

```
Code Quality:
[ ] All 44 tests passing
[ ] ≥85% test coverage
[ ] 0 TypeScript errors
[ ] 0 linting errors
[ ] No N+1 queries
[ ] No memory leaks

Security:
[ ] No SQL injection risks (using ORM)
[ ] No hardcoded secrets
[ ] Error messages don't leak info
[ ] Input validation on all endpoints

Performance:
[ ] API endpoints < 500ms
[ ] Leaderboard < 300ms
[ ] Peer comparison < 200ms
[ ] No timeouts

Documentation:
[ ] Code comments on complex logic
[ ] All functions have docstrings
[ ] README updated
[ ] API docs generated

Review:
[ ] Code review approved
[ ] Ready for production
```

---

## Getting Started Right Now

**Step 1: Create Feature Branch**
```bash
git checkout -b feature/phase-i+1-advanced-analytics
```

**Step 2: Start with Database**
```bash
# Create migration file
touch migrations/add_anomaly_detection_tables.sql

# Create models directory (if needed)
ls -la api/models/

# Copy schema from PHASE_I+1_ADVANCED_ANALYTICS_CORRECTED.md
# into migrations/add_anomaly_detection_tables.sql
```

**Step 3: Implement Models**
```bash
# Create model files
touch api/models/anomaly.py
touch api/models/alert.py
touch api/models/developer_metric.py
touch api/models/peer_group.py
touch api/models/benchmark.py

# Copy code from corrected plan
```

**Step 4: Test Models**
```bash
python3 << 'EOF'
from api.models.anomaly import Anomaly
print("✅ Models imported successfully")
EOF
```

**Then:** Create services → Create tests → Create API → Create frontend

---

## Success Metrics

**Phase I+1 is complete when:**
- ✅ 44 tests passing (100%)
- ✅ 85%+ code coverage
- ✅ 0 N+1 queries
- ✅ All 5 API endpoints working
- ✅ Frontend components rendering
- ✅ Code review approved
- ✅ Ready for production deployment

---

## Links to Reference

- Implementation details: `PHASE_I+1_ADVANCED_ANALYTICS_CORRECTED.md`
- Original design: `PHASE_I+1_ADVANCED_ANALYTICS_IMPLEMENTATION_PLAN.md`
- Review findings: `PHASE_I+1_I+2_I+3_REVIEW.md`
- All fixes: `PHASE_I+1_I+2_I+3_FIXES_COMPLETE.md`

---

**Ready to start? Begin with Day 1: Database Schema**

Good luck! 🚀
