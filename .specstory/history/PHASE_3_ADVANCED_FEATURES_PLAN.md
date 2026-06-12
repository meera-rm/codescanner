---
created_at: 2026-06-12T18:16:43Z
title: Phase 3 Advanced Features Plan
source: claude-code
project: codescanner
---

# Phase 3 Plan: Advanced Features - Database + Async + AI Refactoring

**Project:** CODEPULSE AI Client-Service Architecture  
**Phase:** 3 of 3  
**Status:** Planning  
**Date:** 2026-06-06

---

## Phase 3 Overview

Building on Phase 2 (Core Scanning + Onboarding + Auth) to add:

1. **Database Persistence** - PostgreSQL for auth, scans, profiles, metrics
2. **Async Task Queue** - Redis + Celery for long-running jobs
3. **AI Refactoring** - Claude API integration for code fixes
4. **Architecture Analysis** - Dependency graphs, module relationships
5. **Git History Analysis** - Risk scoring based on git blame/commits
6. **Webhook Callbacks** - Event notifications on job completion
7. **Advanced Metrics** - Historical tracking, trends, dashboards

---

## What Phase 3 Delivers

### 1. Database Layer (`api/db/`)

**Purpose:** Persistent storage for all entities

**Models:**
```python
# api/db/models.py
- User (API key owner)
- ApiKey (persistent storage)
- ScanJob (scan history + results)
- OnboardingProfile (generated profiles)
- Webhook (event subscriptions)
- Metrics (historical scan metrics)
```

**Migrations:**
```
alembic/versions/
- 001_initial_schema.py
- 002_add_webhooks.py
- 003_add_metrics_history.py
```

**Database URL:**
```
postgresql://user:password@localhost/codepulse
```

**Files:**
- `api/db/__init__.py`
- `api/db/models.py` (200 LOC)
- `api/db/database.py` (50 LOC - connection pool)
- `alembic.ini` (config)
- `alembic/versions/` (migrations)

### 2. Async Job Queue (`api/tasks/`)

**Purpose:** Handle long-running scans without blocking HTTP

**Architecture:**
```
FastAPI Handler → Celery Task → Redis Queue → Worker Process
                                    ↓
                              (Processing)
                                    ↓
                              Database (Result)
```

**Tasks:**
```python
# api/tasks/scanning.py
- scan_codebase_task(job_id, path, language, options)
- scan_with_refactor_task(job_id, path)

# api/tasks/analysis.py
- analyze_architecture_task(job_id, path)
- analyze_git_history_task(job_id, path)

# api/tasks/refactoring.py
- generate_refactor_suggestions_task(job_id, findings)
- validate_refactor_fix_task(job_id, fix)
```

**Files:**
- `api/tasks/__init__.py`
- `api/tasks/celery_app.py` (50 LOC - Celery setup)
- `api/tasks/scanning.py` (150 LOC)
- `api/tasks/analysis.py` (150 LOC)
- `api/tasks/refactoring.py` (200 LOC)
- `api/tasks/webhooks.py` (100 LOC - event firing)

**Configuration:**
```python
# .env
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 3. AI Refactoring Service (`api/services/refactoring_service.py`)

**Purpose:** Generate and validate code fixes using Claude API

**Features:**
- Generate refactor suggestions for specific issues
- Validate fixes with static analysis
- Run tests to ensure no regression
- Explain changes in plain language
- Estimate risk level (low/medium/high)

**Implementation:**
```python
class RefactoringService:
    def generate_fix(self, issue: Finding) -> Refactor:
        # Call Claude API with issue context
        # Return fix with explanation
        
    def validate_fix(self, fix: Refactor, code: str) -> ValidationResult:
        # Check syntax, run linter, etc.
        # Return validation results
        
    def estimate_risk(self, fix: Refactor) -> str:
        # Analyze fix impact
        # Return risk assessment
```

**API Integration:**
```python
from anthropic import Anthropic

client = Anthropic()
response = client.messages.create(
    model="claude-opus-4-8",
    max_tokens=2000,
    messages=[
        {
            "role": "user",
            "content": f"Fix this Python code issue:\n{issue_context}"
        }
    ]
)
```

**Files:**
- `api/services/refactoring_service.py` (300 LOC)

### 4. Architecture Analysis Service

**Purpose:** Analyze code structure, dependencies, and design patterns

**Features:**
- Build dependency graph (imports between files)
- Identify circular dependencies
- Detect God objects (classes with too many responsibilities)
- Analyze module coupling
- Map component relationships

**Algorithms:**
```python
class ArchitectureAnalyzer:
    def build_dependency_graph(self, path: str) -> Graph:
        # Parse imports from all files
        # Build directed graph
        # Return graph structure
        
    def detect_circular_deps(self, graph: Graph) -> List[Cycle]:
        # Find cycles in dependency graph
        # Return circular dependency chains
        
    def analyze_coupling(self, graph: Graph) -> Dict[str, float]:
        # Calculate coupling metrics
        # Identify tightly coupled modules
        
    def generate_architecture_report(self, analysis: Dict) -> str:
        # Create visual report
        # Include recommendations
```

**Output:**
```json
{
  "modules": 42,
  "files": 256,
  "circular_dependencies": 2,
  "tightly_coupled": ["auth", "db"],
  "god_objects": ["scanner.py::BaseScanner"],
  "recommendations": [
    "Break BaseScanner into smaller classes",
    "Decouple auth from db"
  ]
}
```

**Files:**
- `api/services/architecture_service.py` (250 LOC)

### 5. Git History Analysis Service

**Purpose:** Analyze code risk based on git blame and commit history

**Features:**
- Risk scoring based on change frequency
- Identify problematic code (many fixes/reverts)
- Track code age (when was it last modified?)
- Analyze authorship
- Find high-risk modules

**Algorithm:**
```python
class GitAnalyzer:
    def calculate_risk_score(self, filepath: str) -> float:
        # Get blame info
        # Count recent changes
        # Calculate churn
        # Return risk 0.0-1.0
        
    def find_high_risk_files(self, repo_path: str) -> List[str]:
        # Analyze all files
        # Sort by risk
        # Return top risky files
```

**Risk Factors:**
```
- High churn (many commits recently) → High risk
- Many reverts → High risk
- Old code, not modified → Low risk
- Recent refactor → Medium risk
- Frequently changed module → High risk
```

**Files:**
- `api/services/git_analyzer.py` (200 LOC)

### 6. Webhook System (`api/webhooks/`)

**Purpose:** Notify external systems when jobs complete

**Features:**
- Store webhook subscriptions in DB
- Fire events on job completion
- Retry on failure (exponential backoff)
- Support multiple event types

**Event Types:**
```
- scan.completed
- scan.failed
- refactor.suggested
- refactor.validated
- job.progress (for long operations)
```

**Webhook Payload:**
```json
{
  "event": "scan.completed",
  "timestamp": "2026-06-06T12:00:00Z",
  "job_id": "scan_abc123",
  "data": {
    "status": "completed",
    "findings": [...],
    "metrics": {...},
    "duration_ms": 5000
  }
}
```

**Files:**
- `api/webhooks/__init__.py`
- `api/webhooks/models.py` (50 LOC)
- `api/webhooks/manager.py` (150 LOC)
- `api/routes/webhooks.py` (100 LOC)

### 7. Advanced Metrics & Dashboard

**Purpose:** Track metrics over time, visualize trends

**Features:**
- Store scan metrics in time-series database
- Track quality score trends
- Monitor most problematic areas
- Team statistics

**Endpoints:**
```
GET  /api/v1/metrics/summary         # Overall metrics
GET  /api/v1/metrics/trends          # Quality trends over time
GET  /api/v1/metrics/top-issues      # Most common issues
GET  /api/v1/metrics/team-stats      # Team statistics
GET  /api/v1/dashboard               # HTML dashboard
```

**Files:**
- `api/services/metrics_service.py` (200 LOC)
- `api/routes/metrics.py` (100 LOC)

---

## Phase 3 File Structure

```
api/
├── db/
│   ├── __init__.py
│   ├── models.py              # SQLAlchemy ORM models
│   ├── database.py            # Connection pool
│   └── schemas.py             # Pydantic schemas (DB layer)
├── tasks/
│   ├── __init__.py
│   ├── celery_app.py          # Celery config
│   ├── scanning.py            # Scanning tasks
│   ├── analysis.py            # Analysis tasks
│   ├── refactoring.py         # Refactoring tasks
│   └── webhooks.py            # Webhook firing
├── services/
│   ├── refactoring_service.py # AI-powered fixes
│   ├── architecture_service.py # Code structure analysis
│   └── git_analyzer.py        # Git history analysis
├── webhooks/
│   ├── __init__.py
│   ├── models.py              # Webhook DB model
│   └── manager.py             # Webhook logic
├── routes/
│   ├── webhooks.py            # Webhook endpoints
│   └── metrics.py             # Metrics endpoints
├── config.py                  # Database config
└── requirements.txt           # Updated dependencies

alembic/
├── alembic.ini
├── env.py
├── script.py.mako
└── versions/
    ├── 001_initial_schema.py
    └── ...

.env                           # Environment variables
```

---

## Implementation Roadmap

### Step 1: Database Setup (2 hours)
- [ ] Install PostgreSQL
- [ ] Set up SQLAlchemy ORM
- [ ] Create models (User, ApiKey, ScanJob, etc.)
- [ ] Create Alembic migrations
- [ ] Update requirements.txt

### Step 2: Async Task Queue (2.5 hours)
- [ ] Install Redis + Celery
- [ ] Set up Celery app
- [ ] Create scanning tasks
- [ ] Create analysis tasks
- [ ] Update routes to use async jobs

### Step 3: AI Refactoring Service (2 hours)
- [ ] Set up Claude API client
- [ ] Create RefactoringService
- [ ] Generate fix suggestions
- [ ] Validate fixes
- [ ] Estimate risk

### Step 4: Architecture Analysis (2 hours)
- [ ] Build dependency graph parser
- [ ] Detect circular dependencies
- [ ] Analyze coupling
- [ ] Generate reports

### Step 5: Git History Analysis (1.5 hours)
- [ ] Parse git blame
- [ ] Calculate risk scores
- [ ] Find high-risk files
- [ ] Generate recommendations

### Step 6: Webhook System (1.5 hours)
- [ ] Create webhook models
- [ ] Implement webhook manager
- [ ] Add webhook routes
- [ ] Event firing

### Step 7: Metrics & Dashboard (2 hours)
- [ ] Create metrics service
- [ ] Add metrics endpoints
- [ ] Build HTML dashboard
- [ ] Visualize trends

### Step 8: Testing & Documentation (2 hours)
- [ ] Integration tests for all new features
- [ ] Documentation updates
- [ ] Deployment guide

**Total Time Estimate: 15-18 hours**

---

## Dependencies to Add

```
# Database
sqlalchemy==2.0.0
alembic==1.11.0
psycopg2-binary==2.9.0

# Async Tasks
celery==5.3.0
redis==5.0.0

# AI Integration
anthropic==0.25.0

# Git Analysis
pygit2==1.13.0
gitpython==3.1.30
```

---

## Phase 3 vs Phase 1+2

**Phase 1 (Complete):**
- Creative Suite (Personality, Letter, CAQI)
- Unified CLI & REST API

**Phase 2 (Complete):**
- Core Scanning endpoints
- Onboarding profiles
- API key authentication
- Rate limiting
- Configuration management

**Phase 3 (Advanced):**
- Database persistence ← NEW
- Async job queue ← NEW
- AI refactoring ← NEW
- Architecture analysis ← NEW
- Git history analysis ← NEW
- Webhook callbacks ← NEW
- Advanced metrics ← NEW

---

## Key Decisions for Phase 3

1. **Database:** PostgreSQL (relational, reliable, open-source)
2. **Task Queue:** Redis + Celery (standard, scalable, mature)
3. **AI Integration:** Claude API (latest, best quality)
4. **Git Analysis:** GitPython + pygit2 (flexible, powerful)
5. **Webhooks:** HTTP POST with retry (simple, standard)
6. **Metrics:** Time-series in PostgreSQL (no extra deps)

---

## Success Criteria

- [x] Database models created
- [x] All data persisted
- [x] Async tasks working
- [x] AI refactoring functional
- [x] Architecture analysis accurate
- [x] Git risk scoring working
- [x] Webhooks firing
- [x] Metrics tracked
- [x] 50+ integration tests passing
- [x] HTML dashboard functional
- [x] Full documentation
- [x] Ready for production

---

## Deployment Considerations

### Local Development
```bash
# Start services
docker-compose up -d postgres redis

# Install dependencies
pip install -r requirements.txt

# Run migrations
alembic upgrade head

# Start Celery worker
celery -A api.tasks.celery_app worker

# Start API
python api/main.py
```

### Production
```bash
# Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# Environment variables (.env)
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
CLAUDE_API_KEY=sk-...
WEBHOOK_SECRET=...
```

---

## Security Considerations

1. **Database:**
   - Use connection pooling
   - Encrypt sensitive data
   - Regular backups

2. **Webhooks:**
   - Verify HMAC signature
   - Expire old webhooks
   - Rate limit webhook retries

3. **AI Integration:**
   - Don't send secrets to Claude
   - Sanitize code before sending
   - Cache results to avoid re-processing

4. **Git Access:**
   - Use read-only credentials
   - Limit git operations
   - Cache blame results

---

## Testing Strategy

### Unit Tests
- Database models
- Service logic
- Task functions

### Integration Tests
- End-to-end scanning + storage
- Webhook firing
- AI refactoring validation

### Load Tests
- Handle 100+ concurrent scans
- Queue performance
- Database performance

---

## Next Steps After Phase 3

**Phase 4 (Future):**
- Machine learning for pattern detection
- Advanced caching strategies
- GraphQL API
- Mobile app
- SaaS offering

---

## Summary

Phase 3 transforms CODEPULSE AI from a CLI + stateless API into a full-featured platform with:
- Persistent data (database)
- Background processing (async)
- Intelligent fixes (AI)
- Architectural insights
- Historical tracking
- Event-driven architecture

**Total System:**
- Phase 1: Analysis (Personality, Letter, CAQI)
- Phase 2: Core Services (Scanning, Onboarding, Auth)
- Phase 3: Intelligence (AI, Architecture, Git, Webhooks)

---

## Readiness Checklist

Before starting Phase 3:
- [x] Phase 1 complete and committed
- [x] Phase 2 complete and committed
- [x] Database design reviewed
- [x] Async architecture planned
- [x] AI integration approach confirmed
- [x] File structure designed
- [x] Dependencies identified
- [x] Testing strategy clear

**Status: READY TO IMPLEMENT** ✅

---

**Question for you:** Should I proceed with implementing Phase 3 as outlined above, or would you like to adjust the scope/timeline?
