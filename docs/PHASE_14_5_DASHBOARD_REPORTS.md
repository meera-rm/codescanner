# Phase 14.5: CI/CD Dashboard & Reports

**Status:** Complete  
**Deliverables:** Backend API + Frontend UI + Database models + Service layer + 21 tests

---

## Overview

Phase 14.5 provides a complete dashboard for tracking CI/CD scan history and trends with:

- **Scan History Tracking** - Record and retrieve all CI scan executions
- **Trend Analytics** - Critical/error/warning trends over time
- **Pass Rate Tracking** - Success/failure rates by repository
- **Platform Breakdown** - Usage statistics by CI platform
- **React Dashboard** - Interactive UI with charts and tables
- **REST API** - 7 endpoints for dashboard data

---

## Database Models

### CIScanHistory
Records every CI/CD scan execution with full details.

```python
CIScanHistory(
    id: UUID                    # Unique scan ID
    repository: str            # Repo path/name
    branch: str               # Git branch
    platform: str             # github, gitlab, jenkins, circleci
    event_type: str           # push, pull_request, schedule
    status: str               # success, failure, warning
    critical_count: int       # # of critical issues
    error_count: int          # # of error issues
    warning_count: int        # # of warnings
    files_scanned: int        # Total files scanned
    languages: dict           # {python: 50, javascript: 30}
    duration_ms: int          # Scan duration
    report_json: dict         # Full JSON report (optional)
    report_sarif: dict        # SARIF format (optional)
    report_junit: str         # JUnit XML (optional)
    report_sonarqube: dict    # SonarQube format (optional)
    created_at: datetime      # When scan started
    completed_at: datetime    # When scan finished
)
```

### CITrendMetrics
Aggregated metrics for trend analysis.

```python
CITrendMetrics(
    id: UUID                           # Unique metrics ID
    repository: str                   # Repository name
    last_scan_at: datetime           # Last execution
    total_scans: int                 # Total scans
    successful_scans: int            # Success count
    failed_scans: int                # Failure count
    pass_rate: float                 # 0-100%
    avg_critical_per_scan: float     # Average
    avg_error_per_scan: float        # Average
    avg_warning_per_scan: float      # Average
    avg_scan_duration_ms: int        # Average duration
    
    # Trend data
    critical_trend: list             # [{date, count}, ...]
    error_trend: list                # [{date, count}, ...]
    warning_trend: list              # [{date, count}, ...]
    pass_rate_trend: list            # [{date, pass_rate}, ...]
    platforms: dict                  # {github: 5, jenkins: 3}
)
```

---

## API Endpoints

### 1. Get Scan History

**Endpoint:** `GET /api/v1/ci-dashboard/history`

Retrieve scan history with optional filters.

**Query Parameters:**
| Name | Type | Default | Description |
|------|------|---------|-------------|
| `repository` | string | optional | Filter by repository |
| `platform` | string | optional | Filter by platform |
| `status` | string | optional | Filter by status |
| `branch` | string | optional | Filter by branch |
| `days` | integer | 30 | Look back period |
| `limit` | integer | 100 | Maximum results |

**Response:**
```json
[
  {
    "id": "uuid",
    "repository": "my-repo",
    "branch": "main",
    "platform": "github",
    "event_type": "push",
    "status": "success",
    "critical_count": 0,
    "error_count": 2,
    "warning_count": 15,
    "files_scanned": 150,
    "duration_ms": 5000,
    "created_at": "2026-07-06T10:00:00Z"
  }
]
```

---

### 2. Get Repository Trends

**Endpoint:** `GET /api/v1/ci-dashboard/trends/{repository}`

Get trend analytics for a specific repository.

**Response:**
```json
{
  "repository": "my-repo",
  "last_scan_at": "2026-07-06T10:00:00Z",
  "total_scans": 100,
  "successful_scans": 85,
  "failed_scans": 15,
  "pass_rate": 85.0,
  "avg_critical_per_scan": 0.5,
  "avg_error_per_scan": 2.1,
  "avg_warning_per_scan": 12.3,
  "avg_scan_duration_ms": 5200,
  "critical_trend": [
    {"date": "2026-07-01", "count": 2},
    {"date": "2026-07-02", "count": 1},
    {"date": "2026-07-03", "count": 0}
  ],
  "error_trend": [...],
  "warning_trend": [...],
  "pass_rate_trend": [...],
  "platforms": {"github": 60, "jenkins": 40}
}
```

---

### 3. Get Dashboard Summary

**Endpoint:** `GET /api/v1/ci-dashboard/summary`

Get overall summary across all repositories.

**Query Parameters:**
- `days` (int, default 30) - Period to summarize

**Response:**
```json
{
  "total_scans": 500,
  "successful_scans": 450,
  "failed_scans": 50,
  "pass_rate": 90.0,
  "total_critical": 5,
  "total_error": 25,
  "total_warning": 320,
  "repositories": [
    {
      "name": "repo-1",
      "scans": 100,
      "critical": 2,
      "error": 10,
      "warning": 80,
      "last_scan": "2026-07-06T10:00:00Z",
      "last_status": "success"
    }
  ],
  "platforms": {
    "github": 300,
    "gitlab": 100,
    "jenkins": 100
  }
}
```

---

### 4. Get Repository Statistics

**Endpoint:** `GET /api/v1/ci-dashboard/repository-stats/{repository}`

Detailed statistics for a single repository.

**Response:**
```json
{
  "repository": "my-repo",
  "total_scans": 100,
  "successful": 85,
  "failed": 15,
  "warnings": 0,
  "pass_rate": 85.0,
  "last_scan": {
    "timestamp": "2026-07-06T10:00:00Z",
    "status": "success",
    "critical": 0,
    "errors": 2
  },
  "total_issues": {
    "critical": 5,
    "error": 25,
    "warning": 320
  },
  "avg_duration_ms": 5200,
  "by_platform": {
    "github": {"success": 50, "failure": 10},
    "jenkins": {"success": 35, "failure": 5}
  },
  "languages": {
    "python": 50,
    "javascript": 30,
    "sql": 5
  }
}
```

---

### 5. Get Latest Scans

**Endpoint:** `GET /api/v1/ci-dashboard/latest-scans`

Get most recent scans across all repositories (activity feed).

**Query Parameters:**
- `limit` (int, default 10) - Number of scans

**Response:**
```json
[
  {
    "id": "uuid",
    "repository": "my-repo",
    "branch": "main",
    "platform": "github",
    "status": "success",
    "critical": 0,
    "errors": 2,
    "timestamp": "2026-07-06T10:00:00Z"
  }
]
```

---

### 6. Record Scan

**Endpoint:** `POST /api/v1/ci-dashboard/record-scan`

Record a new CI scan execution.

**Query Parameters:**
- `repository` (string, required)
- `branch` (string, default "main")
- `platform` (string, required)
- `event_type` (string, required)
- `status` (string, required)
- `critical_count` (int, default 0)
- `error_count` (int, default 0)
- `warning_count` (int, default 0)
- `files_scanned` (int, default 0)
- `duration_ms` (int, default 0)

**Example:**
```bash
curl -X POST "http://localhost:8000/api/v1/ci-dashboard/record-scan" \
  -d "repository=my-repo&platform=github&event_type=push&status=success&error_count=2&warning_count=15&files_scanned=150&duration_ms=5000"
```

---

### 7. Cleanup Old Scans

**Endpoint:** `DELETE /api/v1/ci-dashboard/cleanup-old-scans`

Delete scan history older than specified days.

**Query Parameters:**
- `days` (int, default 90) - Minimum age to delete

**Warning:** This operation is irreversible!

---

## Frontend Dashboard

### React Component: CIDashboard

Located at `frontend/src/pages/CIDashboard.tsx`

**Features:**
- **Summary Cards** - Total scans, pass rate, critical issues, repositories
- **Scan History Table** - Recent scans with status and issue counts
- **Repository Selector** - Choose repository to view trends
- **Trend Charts**
  - Line chart: Critical issues over time
  - Line chart: Pass rate trend
  - Bar chart: Average issues per scan
- **Platform Breakdown** - Usage by GitHub, GitLab, Jenkins, CircleCI

**Display:**
- Color-coded status badges (success=green, failure=red)
- Platform emojis (🐙 GitHub, 🦊 GitLab, 🔧 Jenkins)
- Time period selector (7/14/30/90 days)
- Real-time data refresh

---

## Integration with CI Scan API

The CI dashboard receives data from the CI Scan API:

1. **CI Scan API** runs scan → produces JSON report
2. **CI Scan API** calls `/api/v1/ci-dashboard/record-scan`
3. **Dashboard** stores scan in CIScanHistory
4. **Trend Service** updates CITrendMetrics
5. **Frontend** displays history and trends

Example integration in GitHub Actions:

```yaml
- name: Record Scan Results
  run: |
    curl -X POST "http://localhost:8000/api/v1/ci-dashboard/record-scan" \
      -d "repository=${{ github.repository }}" \
      -d "platform=github" \
      -d "event_type=push" \
      -d "status=success" \
      -d "critical_count=$CRITICAL" \
      -d "error_count=$ERRORS" \
      -d "warning_count=$WARNINGS" \
      -d "files_scanned=$FILES"
```

---

## Service Layer

### CIHistoryService

Provides business logic for dashboard operations:

```python
# Record a scan
scan = CIHistoryService.record_scan(
    db=session,
    repository="my-repo",
    platform="github",
    event_type="push",
    status="success",
    critical_count=0,
    error_count=2,
    warning_count=15,
    files_scanned=150,
    languages={"python": 50, "javascript": 30}
)

# Get history
history = CIHistoryService.get_scan_history(
    db=session,
    repository="my-repo",
    days=30,
    limit=100
)

# Update trends
metrics = CIHistoryService.update_trend_metrics(
    db=session,
    repository="my-repo"
)

# Get summary
summary = CIHistoryService.get_dashboard_summary(
    db=session,
    days=30
)

# Cleanup
deleted = CIHistoryService.delete_old_scans(
    db=session,
    days=90
)
```

---

## Test Coverage

**21 passing tests** covering:

### Dashboard Routes (11 tests)
- Scan history retrieval with/without filters
- Dashboard summary calculations
- Repository statistics
- Latest scans ordering
- Scan recording
- Old scan cleanup

### History Service (8 tests)
- Recording scans
- Filtering by repository/platform
- Updating metrics
- Getting trends
- Dashboard summary generation
- Old scan deletion
- Trend calculations

### Integration Tests (2 tests)
- Full workflow: record → update → fetch
- API and service consistency

---

## Success Criteria Checklist

- [x] CIScanHistory model stores all scan data
- [x] CITrendMetrics model aggregates data for trends
- [x] 7 API endpoints for dashboard data access
- [x] Service layer with business logic
- [x] React dashboard component with charts
- [x] Summary cards showing key metrics
- [x] Scan history table with filtering
- [x] Trend charts (critical, pass rate, issues)
- [x] Platform usage breakdown
- [x] Repository selection and trends
- [x] Time period filtering (7/14/30/90 days)
- [x] 21 passing tests
- [x] Integration with CI Scan API
- [x] Full documentation

---

## Usage Example

1. **Start the server:**
   ```bash
   uvicorn api.main:app --reload
   ```

2. **View dashboard:**
   ```
   http://localhost:3000/ci-dashboard
   ```

3. **Record a scan from CI/CD:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/ci-dashboard/record-scan \
     -d "repository=my-repo&platform=github&event_type=push&status=success&error_count=2&files_scanned=150&duration_ms=5000"
   ```

4. **Get scan history:**
   ```bash
   curl http://localhost:8000/api/v1/ci-dashboard/history?days=7
   ```

5. **View trends for repo:**
   ```bash
   curl http://localhost:8000/api/v1/ci-dashboard/trends/my-repo
   ```

---

## Performance

- **Scan Recording:** < 50ms (with index on repository)
- **History Retrieval:** < 200ms (30-day limit)
- **Trend Calculation:** < 1s (aggregates 30 days)
- **Frontend Charts:** Render in < 500ms

---

## Future Enhancements

1. **Real-time Updates** - WebSocket for live scan updates
2. **Email Alerts** - Notify on critical thresholds
3. **Integrations** - Slack, PagerDuty, Teams notifications
4. **Predictive Analytics** - Forecast trend lines
5. **Baselines** - Compare against historical averages
6. **Custom Reports** - PDF/CSV export

---

**Phase 14 Complete!** ✅

All CI/CD integration phases implemented:
- 14.1: GitHub Actions ✅
- 14.3: Jenkins Integration ✅
- 14.4: CI Scan API ✅
- 14.5: Dashboard & Reports ✅
