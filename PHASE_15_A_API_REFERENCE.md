# Phase 15.A: Complete API Reference

## Overview

All new API endpoints added in Phase 15.A with examples and documentation.

**Base URL:** `http://localhost:8000/api/v1`  
**Swagger UI:** `http://localhost:8000/docs`  
**OpenAPI Schema:** `http://localhost:8000/openapi.json`

---

## 📋 Table of Contents

1. [Search API](#search-api)
2. [Alert Notifications API](#alert-notifications-api)
3. [Report Export API](#report-export-api)
4. [WebSocket API](#websocket-api)
5. [Cache Management API](#cache-management-api)

---

## Search API

### 1. Search Scans

**Endpoint:** `GET /api/v1/search/scans`

**Description:** Full-text search on scans with advanced filtering

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| q | string | null | Full-text search query (repository, branch, platform) |
| repository | string | null | Filter by repository name |
| platform | string | null | Filter by platform (github, jenkins, gitlab, circleci) |
| status | string | null | Filter by status (success, failure, warning) |
| branch | string | null | Filter by branch name |
| min_critical | integer | null | Minimum critical count |
| max_critical | integer | null | Maximum critical count |
| min_errors | integer | null | Minimum error count |
| max_errors | integer | null | Maximum error count |
| days | integer | 30 | Look back period in days |
| limit | integer | 50 | Results per page |
| offset | integer | 0 | Pagination offset |

**Examples:**

```bash
# Basic search
curl "http://localhost:8000/api/v1/search/scans?q=my-repo"

# Filter by platform
curl "http://localhost:8000/api/v1/search/scans?platform=github"

# Complex query
curl "http://localhost:8000/api/v1/search/scans?repository=production&platform=github&status=failure&min_critical=1"

# With pagination
curl "http://localhost:8000/api/v1/search/scans?limit=100&offset=50"
```

**Response:**

```json
{
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "repository": "my-repo",
      "branch": "main",
      "platform": "github",
      "event_type": "push",
      "status": "success",
      "critical_count": 0,
      "error_count": 2,
      "warning_count": 15,
      "info_count": 10,
      "total_findings": 27,
      "files_scanned": 150,
      "duration_ms": 5000,
      "created_at": "2026-07-06T12:30:45.123Z",
      "completed_at": "2026-07-06T12:30:50.123Z"
    }
  ],
  "total": 142,
  "limit": 50,
  "offset": 0
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid parameters
- `500` - Server error

---

### 2. Get Filter Options

**Endpoint:** `GET /api/v1/search/filters`

**Description:** Get available filter options for dropdowns (cached 1 hour)

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| force_refresh | boolean | false | Skip cache, fetch fresh data |

**Examples:**

```bash
# Get filter options (cached)
curl "http://localhost:8000/api/v1/search/filters"

# Force refresh
curl "http://localhost:8000/api/v1/search/filters?force_refresh=true"
```

**Response:**

```json
{
  "repositories": [
    "my-repo",
    "backend",
    "frontend",
    "production-api"
  ],
  "platforms": [
    "github",
    "jenkins",
    "gitlab",
    "circleci"
  ],
  "branches": [
    "main",
    "develop",
    "feature/new-ui",
    "hotfix/bug-123"
  ],
  "statuses": [
    "success",
    "failure",
    "warning"
  ]
}
```

---

### 3. Get Search Suggestions

**Endpoint:** `GET /api/v1/search/suggestions`

**Description:** Get autocomplete suggestions (cached 1 hour)

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | Query prefix |
| field | string | Yes | Field to search (repository, branch, platform) |
| force_refresh | boolean | No | Skip cache |

**Examples:**

```bash
# Repository suggestions
curl "http://localhost:8000/api/v1/search/suggestions?q=my&field=repository"

# Branch suggestions
curl "http://localhost:8000/api/v1/search/suggestions?q=main&field=branch"

# Platform suggestions
curl "http://localhost:8000/api/v1/search/suggestions?q=git&field=platform"
```

**Response:**

```json
{
  "suggestions": [
    "my-repo",
    "my-backend",
    "my-frontend"
  ]
}
```

---

## Alert Notifications API

### 1. Create/Update Alert Preference

**Endpoint:** `POST /api/v1/alerts/preferences`

**Description:** Create or update alert notification preferences

**Request Body:**

```json
{
  "repository": "all",
  "alert_on_critical": true,
  "alert_on_error": false,
  "critical_threshold": 1,
  "error_threshold": 5,
  "email_enabled": true,
  "email_address": "team@company.com",
  "slack_enabled": true,
  "slack_webhook": "https://hooks.slack.com/services/T000/B000/XXX",
  "alert_frequency": "immediate",
  "is_active": true
}
```

**Parameters:**

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| repository | string | "all" | Repository name or "all" for global alerts |
| alert_on_critical | boolean | true | Alert when critical issues found |
| alert_on_error | boolean | false | Alert when errors found |
| critical_threshold | integer | 1 | Minimum critical count to trigger alert |
| error_threshold | integer | 5 | Minimum error count to trigger alert |
| email_enabled | boolean | true | Send email alerts |
| email_address | string | null | Email to send to |
| slack_enabled | boolean | false | Send Slack alerts |
| slack_webhook | string | null | Slack webhook URL |
| alert_frequency | string | "immediate" | immediate, daily, or weekly |
| is_active | boolean | true | Enable/disable alerts |

**Examples:**

```bash
# Create alert for all repos, email only
curl -X POST "http://localhost:8000/api/v1/alerts/preferences" \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "all",
    "alert_on_critical": true,
    "email_enabled": true,
    "email_address": "team@company.com",
    "is_active": true
  }'

# Create alert for production repo, email + Slack
curl -X POST "http://localhost:8000/api/v1/alerts/preferences" \
  -H "Content-Type: application/json" \
  -d '{
    "repository": "production-api",
    "alert_on_critical": true,
    "alert_on_error": true,
    "critical_threshold": 1,
    "error_threshold": 5,
    "email_enabled": true,
    "email_address": "oncall@company.com",
    "slack_enabled": true,
    "slack_webhook": "https://hooks.slack.com/services/...",
    "is_active": true
  }'
```

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "repository": "all",
  "alert_on_critical": true,
  "alert_on_error": false,
  "critical_threshold": 1,
  "error_threshold": 5,
  "email_enabled": true,
  "email_address": "team@company.com",
  "slack_enabled": false,
  "slack_webhook": null,
  "alert_frequency": "immediate",
  "is_active": true
}
```

---

### 2. List Alert Preferences

**Endpoint:** `GET /api/v1/alerts/preferences`

**Description:** Get all alert preferences

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| repository | string | Filter by repository (optional) |

**Examples:**

```bash
# Get all preferences
curl "http://localhost:8000/api/v1/alerts/preferences"

# Get preferences for specific repo
curl "http://localhost:8000/api/v1/alerts/preferences?repository=my-repo"
```

**Response:**

```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "repository": "all",
    "alert_on_critical": true,
    "email_enabled": true,
    "email_address": "team@company.com",
    "slack_enabled": false,
    "is_active": true
  },
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "repository": "production-api",
    "alert_on_critical": true,
    "email_enabled": true,
    "email_address": "oncall@company.com",
    "slack_enabled": true,
    "is_active": true
  }
]
```

---

### 3. Get Alert Preference

**Endpoint:** `GET /api/v1/alerts/preferences/{repository}`

**Description:** Get alert preferences for specific repository

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| repository | string | Repository name |

**Examples:**

```bash
curl "http://localhost:8000/api/v1/alerts/preferences/my-repo"
```

**Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "repository": "my-repo",
  "alert_on_critical": true,
  "email_enabled": true,
  "email_address": "dev@company.com",
  "is_active": true
}
```

---

### 4. Delete Alert Preference

**Endpoint:** `DELETE /api/v1/alerts/preferences/{repository}`

**Description:** Delete alert preferences

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| repository | string | Repository name |

**Examples:**

```bash
curl -X DELETE "http://localhost:8000/api/v1/alerts/preferences/my-repo"
```

**Response:**

```json
{
  "message": "Alert preferences for my-repo deleted"
}
```

---

### 5. Test Alert

**Endpoint:** `POST /api/v1/alerts/test/{repository}`

**Description:** Send test alert to verify configuration

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| repository | string | Repository name |

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| channel | string | "email" | Channel to test (email, slack, both) |

**Examples:**

```bash
# Test email
curl -X POST "http://localhost:8000/api/v1/alerts/test/my-repo?channel=email"

# Test Slack
curl -X POST "http://localhost:8000/api/v1/alerts/test/my-repo?channel=slack"

# Test both
curl -X POST "http://localhost:8000/api/v1/alerts/test/my-repo?channel=both"
```

**Response:**

```json
{
  "email_sent": true,
  "slack_sent": false
}
```

---

## Report Export API

### 1. Export as CSV

**Endpoint:** `GET /api/v1/ci-dashboard/export/csv`

**Description:** Export scan history as CSV file

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| repository | string | null | Filter by repository |
| platform | string | null | Filter by platform |
| days | integer | 30 | Look back period |

**Examples:**

```bash
# Export all scans
curl "http://localhost:8000/api/v1/ci-dashboard/export/csv" \
  -o scans-report.csv

# Export specific repo, last 7 days
curl "http://localhost:8000/api/v1/ci-dashboard/export/csv?repository=my-repo&days=7" \
  -o my-repo-7days.csv

# Export GitHub scans only
curl "http://localhost:8000/api/v1/ci-dashboard/export/csv?platform=github" \
  -o github-scans.csv
```

**Response:**
- Content-Type: `text/csv`
- Headers: `Content-Disposition: attachment; filename=codepulse-scans-YYYYMMDD-HHMMSS.csv`

**CSV Columns:**
```
Repository,Branch,Platform,Event Type,Status,Critical,Error,Warning,Info,Total Findings,Files Scanned,Duration (ms),Timestamp
```

---

### 2. Export as PDF

**Endpoint:** `GET /api/v1/ci-dashboard/export/pdf`

**Description:** Export scan report as PDF with summary and analysis

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| repository | string | null | Filter by repository |
| platform | string | null | Filter by platform |
| days | integer | 30 | Look back period |

**Examples:**

```bash
# Export PDF report
curl "http://localhost:8000/api/v1/ci-dashboard/export/pdf" \
  -o scan-report.pdf

# Production repo, last 7 days
curl "http://localhost:8000/api/v1/ci-dashboard/export/pdf?repository=production&days=7" \
  -o production-weekly.pdf
```

**Response:**
- Content-Type: `application/pdf`
- Headers: `Content-Disposition: attachment; filename=codepulse-report-YYYYMMDD-HHMMSS.pdf`

**PDF Contents:**
- Executive Summary (totals, pass rate, issues)
- Repository Breakdown (per-repo statistics)
- Platform Analysis (per-platform metrics)
- Detailed Scan Results (last 50 scans)

---

## WebSocket API

### 1. Dashboard Updates

**Endpoint:** `WS /api/v1/ws/dashboard`

**Description:** Real-time dashboard updates (scan completions, refresh signals)

**Connection:**

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/dashboard');

ws.onopen = () => console.log('Connected');

ws.onmessage = (event) => {
  const msg = JSON.parse(event.data);
  console.log('Message:', msg.type, msg);
};

ws.onerror = (error) => console.error('Error:', error);
ws.onclose = () => console.log('Disconnected');
```

**Message Types:**

#### scan_complete
```json
{
  "type": "scan_complete",
  "timestamp": "2026-07-06T12:34:56.789Z",
  "data": {
    "id": "scan-uuid",
    "repository": "my-repo",
    "branch": "main",
    "platform": "github",
    "status": "success",
    "critical_count": 0,
    "error_count": 2,
    "warning_count": 15,
    "total_findings": 17,
    "files_scanned": 150,
    "duration_ms": 5000
  }
}
```

#### dashboard_refresh
```json
{
  "type": "dashboard_refresh",
  "timestamp": "2026-07-06T12:34:56.789Z",
  "data": {
    "total_scans": 487,
    "successful_scans": 450,
    "failed_scans": 37,
    "pass_rate": 92.4,
    "total_critical": 5,
    "total_error": 23,
    "total_warning": 156
  }
}
```

#### heartbeat
```json
{
  "type": "heartbeat",
  "timestamp": "2026-07-06T12:34:56.789Z"
}
```

---

### 2. Scan Updates (Repository-Specific)

**Endpoint:** `WS /api/v1/ws/scans?repository={name}`

**Description:** Real-time updates for specific repository scans

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| repository | string | "all" | Repository to subscribe to |

**Connection:**

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws/scans?repository=my-repo');
```

---

### 3. WebSocket Stats

**Endpoint:** `GET /api/v1/ws/stats`

**Description:** Get current WebSocket connection statistics

**Examples:**

```bash
curl "http://localhost:8000/api/v1/ws/stats"
```

**Response:**

```json
{
  "total_connections": 5,
  "subscriptions": {
    "all": 3,
    "my-repo": 2,
    "production-api": 1
  }
}
```

---

## Cache Management API

### 1. Get Cache Statistics

**Endpoint:** `GET /api/v1/cache/stats`

**Description:** Get Redis cache statistics

**Examples:**

```bash
curl "http://localhost:8000/api/v1/cache/stats"
```

**Response:**

```json
{
  "status": "available",
  "used_memory": "2.34M",
  "used_memory_human": "2.34M",
  "connected_clients": 1,
  "keys_total": 156,
  "expires_keys": 150,
  "uptime_seconds": 3600,
  "hits": 1245,
  "misses": 98,
  "hit_rate": 92.6
}
```

---

### 2. Get Detailed Cache Info

**Endpoint:** `GET /api/v1/cache/info`

**Description:** Get detailed Redis information

**Examples:**

```bash
curl "http://localhost:8000/api/v1/cache/info"
```

**Response:**

```json
{
  "redis_version": "7.0.0",
  "uptime_seconds": 3600,
  "total_commands_processed": 2500,
  "instantaneous_ops_per_sec": 15,
  "total_net_input_bytes": 125000,
  "total_net_output_bytes": 250000,
  "used_memory": "2457600",
  "used_memory_human": "2.34M",
  "used_memory_rss": "5000000",
  "mem_fragmentation_ratio": 2.03,
  "keyspace": {
    "0": {
      "keys": 156,
      "expires": 150,
      "avg_ttl": 450000
    }
  }
}
```

---

### 3. Cache Health Check

**Endpoint:** `POST /api/v1/cache/health`

**Description:** Check Redis connection health and latency

**Examples:**

```bash
curl -X POST "http://localhost:8000/api/v1/cache/health"
```

**Response:**

```json
{
  "healthy": true,
  "message": "Redis is healthy",
  "latency_ms": 0.45,
  "response_time": "2026-07-06T12:34:56.789Z"
}
```

---

### 4. Clear Cache

**Endpoint:** `POST /api/v1/cache/clear`

**Description:** Clear cache by scope

**Query Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| scope | string | "all" | Scope to clear: all, dashboard, search, trends |

**Examples:**

```bash
# Clear all cache
curl -X POST "http://localhost:8000/api/v1/cache/clear?scope=all"

# Clear dashboard cache only
curl -X POST "http://localhost:8000/api/v1/cache/clear?scope=dashboard"

# Clear search cache
curl -X POST "http://localhost:8000/api/v1/cache/clear?scope=search"

# Clear trends cache
curl -X POST "http://localhost:8000/api/v1/cache/clear?scope=trends"
```

**Response:**

```json
{
  "message": "Cache cleared for scope: all",
  "keys_cleared": 156
}
```

---

## Common Response Codes

| Code | Description |
|------|-------------|
| `200` | Success |
| `201` | Created |
| `400` | Bad Request (invalid parameters) |
| `404` | Not Found (resource doesn't exist) |
| `500` | Server Error |

---

## Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

**Example:**

```bash
curl "http://localhost:8000/api/v1/alerts/preferences/nonexistent"
```

```json
{
  "detail": "Alert preference not found"
}
```

---

## Authentication

Currently, no authentication is required. In production, consider adding:
- API key authentication
- JWT token authentication
- OAuth2 integration

---

## Rate Limiting

No rate limiting currently implemented. Consider adding:
- Per-IP rate limiting
- Per-API-key rate limiting
- Burst allowance for spikes

---

## Pagination

Supported in Search API:

```bash
# Get page 1 (50 results)
curl "http://localhost:8000/api/v1/search/scans?limit=50&offset=0"

# Get page 2 (results 50-100)
curl "http://localhost:8000/api/v1/search/scans?limit=50&offset=50"

# Get page 3 (results 100-150)
curl "http://localhost:8000/api/v1/search/scans?limit=50&offset=100"
```

---

## Caching Behavior

| Endpoint | Cache TTL | Force Refresh |
|----------|-----------|---------------|
| `/search/filters` | 1 hour | `?force_refresh=true` |
| `/search/suggestions` | 1 hour | `?force_refresh=true` |
| `/ci-dashboard/summary` | 5 minutes | `?force_refresh=true` |
| `/ci-dashboard/trends/*` | 15 minutes | `?force_refresh=true` |

---

## Summary

**Total Endpoints Added:** 15+

- **Search:** 3 endpoints
- **Alerts:** 5 endpoints
- **Reports:** 2 endpoints
- **WebSocket:** 3 endpoints
- **Cache:** 4 endpoints

All endpoints are documented in Swagger at: **http://localhost:8000/docs**

---

**Last Updated:** July 6, 2026  
**Phase:** 15.A (Complete)  
**Status:** Production Ready ✅

