# CodePulse AI - Architecture & Deployment Guide

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    CodePulse Frontend                    │
│              (Real-time Progress Dashboard)              │
└─────────────────────┬───────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────┐
│                    FastAPI Gateway                       │
│         (Request routing, authentication)                │
└─────────────────────┬───────────────────────────────────┘
                      │
        ┌─────────────┼─────────────┐
        │             │             │
        ▼             ▼             ▼
    ┌────────┐   ┌────────┐   ┌────────────┐
    │Celery  │   │Redis   │   │PostgreSQL  │
    │Tasks   │   │Cache   │   │Database    │
    └────────┘   └────────┘   └────────────┘
        │
        ▼
    ┌─────────────────────────────────────┐
    │  Service Layer (Multi-Agent Core)   │
    ├─────────────────────────────────────┤
    │ • ParallelAgentExecutor             │
    │ • FileModifierService               │
    │ • CodeFormatterService              │
    │ • CodeValidatorService              │
    │ • GitHubIntegrationService          │
    │ • ArchitectureAnalyzerService       │
    │ • GitRiskAnalyzerService            │
    └─────────────────────────────────────┘
        │
        ├─────────────────┬──────────────────┐
        │                 │                  │
        ▼                 ▼                  ▼
    ┌────────┐      ┌──────────┐      ┌──────────┐
    │Black   │      │Prettier  │      │GitHub    │
    │        │      │          │      │API       │
    └────────┘      └──────────┘      └──────────┘
```

### Component Breakdown

#### 1. Frontend Layer
- **React Dashboard** (Phase 4.1)
- Real-time iteration progress
- Interactive charts and metrics
- Dark mode support

#### 2. API Gateway
- FastAPI-based REST API
- Request validation
- Authentication/authorization
- Rate limiting

#### 3. Background Processing
- **Celery** for async jobs
- **Redis** for caching and broker
- Long-running task management

#### 4. Service Layer
- **File Modification Service** (Phase 4.2a)
- **Code Formatter** (Phase 4.2b)
- **Code Validator** (Phase 4.2c)
- **Diff Generator** (Phase 4.2d)
- **GitHub Integration** (Phase 4.3)
- **Parallel Agent Executor** (Phase 4.4)
- **Architecture Analyzer** (Phase 4.5)
- **Git Risk Analyzer** (Phase 4.6)

#### 5. External Integrations
- **Black** - Python formatter
- **Prettier** - JavaScript formatter
- **Pylint** - Python linter
- **ESLint** - JavaScript linter
- **GitHub API** - PR creation

---

## Data Flow

### Complete Improvement Pipeline

```
User Request
    ↓
Scan Code
    ↓
Parallel Agents (3x) → Analysis
    ├─ Agent A (Simplicity)
    ├─ Agent B (Architecture)
    └─ Agent C (Performance)
    ↓
Merge Suggestions
    ↓
Modify Files → Format → Validate
    ↓
Generate Diff
    ↓
Create GitHub PR
    ↓
Architecture Analysis
    ↓
Git Risk Analysis
    ↓
Dashboard Update
    ↓
Success Response
```

---

## Deployment Architecture

### Deployment Topology

```
┌──────────────────────────────────────────────────────────┐
│                  Load Balancer (Nginx)                   │
└──────────────────────┬───────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
        ▼              ▼              ▼
    ┌─────────┐  ┌─────────┐  ┌─────────┐
    │ API     │  │ API     │  │ API     │
    │ Server  │  │ Server  │  │ Server  │
    │ (Uvicorn)│  │ (Uvicorn)│  │ (Uvicorn)│
    └────┬────┘  └────┬────┘  └────┬────┘
         │            │            │
         └────────────┼────────────┘
                      │
        ┌─────────────┼──────────────┐
        │             │              │
        ▼             ▼              ▼
    ┌────────┐   ┌────────┐   ┌──────────┐
    │Celery  │   │Redis   │   │PostgreSQL│
    │Worker  │   │        │   │          │
    │(2x)    │   │        │   │(Primary) │
    └────────┘   └────────┘   └──────────┘
        │                          │
        │                          ▼
        │                      ┌──────────┐
        │                      │PostgreSQL│
        │                      │(Replica) │
        │                      └──────────┘
        ▼
    External Services
    ├─ Black (Python Formatter)
    ├─ Prettier (JS Formatter)
    ├─ GitHub API
    └─ Lint Services
```

---

## Performance Characteristics

### Latency SLAs

| Operation | Target | Typical |
|-----------|--------|---------|
| Format code | < 500ms | 100-200ms |
| Validate syntax | < 200ms | 50-100ms |
| Parallel agents (3x) | < 2s | 500-800ms |
| Architecture analysis | < 1s | 200-500ms |
| Git risk analysis | < 1s | 300-600ms |
| Complete pipeline | < 3s | 1-2s |

### Throughput

- **Requests/second:** 100+ (3 servers)
- **Agents/second:** 300+ (concurrent)
- **Files/second:** 50+ (modification)
- **LOC/second:** 50K+ (analysis)

### Resource Usage

- **Memory per request:** 50-100MB
- **CPU per request:** 100-200ms
- **Disk per request:** 10-50MB (temp)

---

## Security

### API Security

- **Authentication:** Bearer tokens (JWT)
- **Authorization:** RBAC per repository
- **Rate limiting:** 1000 req/hour per token
- **HTTPS:** TLS 1.2+
- **CORS:** Configured per domain

### Data Security

- **Encryption:** AES-256 at rest
- **Backup:** Daily, encrypted
- **Audit logging:** All API calls logged
- **Code access:** No storage of user code
- **GitHub tokens:** Encrypted storage

### Network Security

- **Firewall:** Whitelist external APIs
- **VPC:** Private subnet for databases
- **Secrets:** AWS Secrets Manager
- **DDoS protection:** CloudFlare

---

## Monitoring & Observability

### Metrics

```
codepulse_api_requests_total
codepulse_api_latency_seconds
codepulse_api_errors_total
codepulse_agent_execution_time
codepulse_file_modification_count
codepulse_pr_creation_count
```

### Logs

```
[INFO] 2026-07-05 10:30:45 - Pipeline started (job_id=abc123)
[INFO] 2026-07-05 10:30:50 - Agent A completed (score=0.9)
[INFO] 2026-07-05 10:30:52 - Formatting complete (lines=150)
[INFO] 2026-07-05 10:30:53 - Validation passed (checks=3)
[INFO] 2026-07-05 10:30:55 - PR created (url=...)
```

### Alerts

- Pipeline latency > 5 seconds
- Success rate < 95%
- Memory usage > 80%
- Disk usage > 90%
- Database replication lag > 10s

---

## Disaster Recovery

### Backup Strategy

- **Frequency:** Daily at 2 AM UTC
- **Retention:** 30 days
- **Location:** S3 with cross-region replication
- **Testing:** Weekly restore drills

### Failover

- **RTO:** < 15 minutes
- **RPO:** < 1 hour
- **Database:** Primary → Replica failover (automatic)
- **API:** Load balancer health checks (10s)

### Recovery Procedures

1. **Database failure:**
   - Promote replica to primary
   - Update DNS/connection strings
   - Verify all services

2. **API server failure:**
   - Load balancer removes unhealthy instances
   - New instances auto-scale up
   - Minimal impact to active requests

3. **GitHub token compromise:**
   - Revoke token immediately
   - Generate new token
   - Update secrets
   - No data breach possible (tokens only)

---

## Scaling Strategy

### Horizontal Scaling

- **API servers:** Add horizontal replicas
- **Celery workers:** Scale based on queue depth
- **Redis:** Add shards for distributed cache
- **PostgreSQL:** Read replicas for queries

### Vertical Scaling

- **API servers:** Increase CPU/memory per pod
- **Workers:** Increase timeout for large jobs
- **Database:** Larger instance type

### Auto-scaling Triggers

- CPU > 70% → Add 1 API server
- Memory > 75% → Add 1 Celery worker
- Queue depth > 100 → Add 2 workers
- Response time > 2s → Add 1 API server

---

## Cost Optimization

### Resource Allocation

| Component | Size | Count | Cost/month |
|-----------|------|-------|-----------|
| API Servers | t3.medium | 3 | $90 |
| Celery Workers | t3.small | 2 | $30 |
| Redis | t3.micro | 1 | $10 |
| PostgreSQL | t3.small | 2 | $60 |
| Load Balancer | ALB | 1 | $20 |
| **Total** | — | — | **$210** |

### Cost-Saving Options

- Use spot instances for workers (60% savings)
- Reserved instances for baseline (30% savings)
- Auto-scaling to zero during off-hours

---

## Deployment Checklist

### Pre-Deployment

- [ ] Run all tests (unit + integration)
- [ ] Update API version
- [ ] Update CHANGELOG
- [ ] Run security scan
- [ ] Performance baseline

### Deployment

- [ ] Tag release in git
- [ ] Build release artifact
- [ ] Push to registry
- [ ] Deploy to staging
- [ ] Run smoke tests
- [ ] Deploy to production
- [ ] Monitor metrics

### Post-Deployment

- [ ] Verify all services healthy
- [ ] Check error rates
- [ ] Monitor latency
- [ ] Run synthetic tests
- [ ] Update status page

---

## Support & SLOs

### Service Level Objectives

- **Availability:** 99.9% uptime
- **Latency:** 95th percentile < 1 second
- **Error rate:** < 0.1%
- **Support response:** < 1 hour

### Escalation Path

1. **Level 1:** On-call engineer (2am response)
2. **Level 2:** Engineering lead (15min response)
3. **Level 3:** Director of Engineering (30min response)

---

## Timeline Summary

- **Phase 4.1-4.7:** 108 hours of development
- **Phase 4.8:** 8 hours of documentation (current)
- **Total Phase 4:** 116 hours
- **Production Ready:** 2026-07-05

---

## License

CodePulse AI is licensed under the Apache 2.0 License.
