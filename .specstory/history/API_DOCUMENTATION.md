---
created_at: 2026-06-12T18:16:43Z
title: Api Documentation
source: claude-code
project: codescanner
---

# CodePulse AI - API Documentation

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
Currently no authentication required. In production, implement Bearer token authentication.

---

## Endpoints

### 1. Get Team CAQI Score
**Endpoint:** `GET /analytics/teams/{team_id}/caqi`

**Description:** Get current CAQI (Code Quality Index) score and dimension breakdown for a team.

**Parameters:**
- `team_id` (path, required): Team identifier (e.g., "backend-team")

**Response:** `200 OK`
```json
{
  "team_id": "backend-team",
  "overall_caqi": 380,
  "dimensions": {
    "security": 85,
    "complexity": 72,
    "documentation": 80,
    "testing": 88,
    "dependencies": 65,
    "maintainability": 78
  },
  "calculated_at": "2026-06-06T14:30:00Z"
}
```

**Status Codes:**
- `200`: Success
- `400`: Invalid team_id

---

### 2. Get Team Trends
**Endpoint:** `GET /analytics/teams/{team_id}/trends`

**Description:** Get CAQI score trends over time for a team.

**Parameters:**
- `team_id` (path, required): Team identifier
- `days` (query, optional): Number of days to retrieve (1-365, default: 30)

**Response:** `200 OK`
```json
[
  {
    "team_id": "backend-team",
    "dimension": "security",
    "scores": [
      {"date": "2026-05-07", "score": 75},
      {"date": "2026-05-14", "score": 78},
      {"date": "2026-05-21", "score": 80},
      {"date": "2026-05-28", "score": 82},
      {"date": "2026-06-04", "score": 85}
    ],
    "trend": "improving"
  }
]
```

**Status Codes:**
- `200`: Success
- `422`: Invalid days parameter (must be 1-365)

---

### 3. Get Anomalies
**Endpoint:** `GET /analytics/teams/{team_id}/anomalies`

**Description:** Get detected anomalies (significant score changes) for a team.

**Parameters:**
- `team_id` (path, required): Team identifier
- `severity` (query, optional): Filter by severity ("low", "medium", "high", "critical")
- `reviewed` (query, optional): Filter by review status (true/false)

**Response:** `200 OK`
```json
[
  {
    "id": "anom-1",
    "dimension": "security",
    "previousScore": 75,
    "currentScore": 85,
    "changePercent": 13.3,
    "severity": "high",
    "detectedAt": "2026-06-05T10:00:00Z",
    "reviewed": false
  },
  {
    "id": "anom-2",
    "dimension": "complexity",
    "previousScore": 70,
    "currentScore": 65,
    "changePercent": -7.1,
    "severity": "medium",
    "detectedAt": "2026-06-04T14:00:00Z",
    "reviewed": true,
    "reviewedBy": "user-1"
  }
]
```

**Status Codes:**
- `200`: Success
- `422`: Invalid severity parameter

---

### 4. Get Developer Contributions
**Endpoint:** `GET /analytics/teams/{team_id}/developers`

**Description:** Get individual developer contribution scores within a team.

**Parameters:**
- `team_id` (path, required): Team identifier
- `days` (query, optional): Analysis period in days (1-365, default: 30)

**Response:** `200 OK`
```json
[
  {
    "developerId": "dev-1",
    "teamId": "backend-team",
    "contributions": {
      "security": {
        "developerScore": 80,
        "teamAvg": 75,
        "contribution": 5.0
      },
      "complexity": {
        "developerScore": 72,
        "teamAvg": 70,
        "contribution": 2.0
      },
      "documentation": {
        "developerScore": 75,
        "teamAvg": 65,
        "contribution": 10.0
      },
      "testing": {
        "developerScore": 85,
        "teamAvg": 80,
        "contribution": 5.0
      },
      "dependencies": {
        "developerScore": 70,
        "teamAvg": 60,
        "contribution": 10.0
      },
      "maintainability": {
        "developerScore": 80,
        "teamAvg": 75,
        "contribution": 5.0
      }
    },
    "overallContribution": 6.17
  }
]
```

**Status Codes:**
- `200`: Success
- `422`: Invalid days parameter

---

### 5. Get Peer Comparison
**Endpoint:** `GET /analytics/teams/{team_id}/peer-comparison`

**Description:** Compare a team's score against peer teams for a specific dimension.

**Parameters:**
- `team_id` (path, required): Team identifier
- `dimension` (query, required): Dimension to compare ("security", "complexity", "documentation", "testing", "dependencies", "maintainability")

**Response:** `200 OK`
```json
{
  "team_id": "backend-team",
  "dimension": "security",
  "score": 85,
  "percentile": 75,
  "peerMedian": 80,
  "peerMin": 60,
  "peerMax": 95
}
```

**Status Codes:**
- `200`: Success
- `422`: Missing or invalid dimension parameter

---

### 6. Get Alerts
**Endpoint:** `GET /analytics/teams/{team_id}/alerts`

**Description:** Get alerts for significant quality issues.

**Parameters:**
- `team_id` (path, required): Team identifier
- `severity` (query, optional): Filter by severity ("low", "medium", "high", "critical")

**Response:** `200 OK`
```json
[
  {
    "id": "alert-1",
    "type": "regression",
    "severity": "high",
    "message": "Security score declined 10%",
    "createdAt": "2026-06-06T10:00:00Z",
    "acknowledged": false
  },
  {
    "id": "alert-2",
    "type": "trend",
    "severity": "medium",
    "message": "Testing dimension declining",
    "createdAt": "2026-06-05T14:00:00Z",
    "acknowledged": true
  }
]
```

**Status Codes:**
- `200`: Success
- `422`: Invalid severity parameter

---

### 7. Get Benchmarks
**Endpoint:** `GET /analytics/teams/{team_id}/benchmarks`

**Description:** Get benchmark data for performance targets and industry standards.

**Parameters:**
- `team_id` (path, required): Team identifier

**Response:** `200 OK`
```json
[
  {
    "dimension": "security",
    "target": 90,
    "current": 85,
    "industry_median": 80,
    "status": "on_track"
  }
]
```

**Status Codes:**
- `200`: Success
- `422`: Invalid team_id

---

### 8. Health Check
**Endpoint:** `GET /analytics/health`

**Description:** Check API health and connectivity.

**Parameters:** None

**Response:** `200 OK`
```json
{
  "status": "ok"
}
```

**Status Codes:**
- `200`: API is healthy

---

### 9. Review Anomaly
**Endpoint:** `POST /analytics/teams/{team_id}/anomalies/{anomaly_id}/review`

**Description:** Mark an anomaly as reviewed.

**Parameters:**
- `team_id` (path, required): Team identifier
- `anomaly_id` (path, required): Anomaly identifier
- `notes` (body, optional): Review notes

**Request Body:**
```json
{
  "notes": "Reviewed and confirmed - expected behavior"
}
```

**Response:** `200 OK`
```json
{
  "message": "Anomaly reviewed"
}
```

**Status Codes:**
- `200`: Success
- `404`: Anomaly not found
- `422`: Invalid request

---

## Data Models

### CAQI Score
- **Range:** 0-500
- **Grade Scale:**
  - A+ (450-500): Excellent code quality
  - A (400-449): Very good
  - B+ (350-399): Good
  - B (300-349): Acceptable
  - C+ (250-299): Fair
  - C (200-249): Poor
  - D+ (150-199): Very poor
  - D (100-149): Critical
  - F (0-99): Failing

### Dimensions
1. **Security** (0-100): Security vulnerability detection
2. **Complexity** (0-100): Code complexity analysis
3. **Documentation** (0-100): Code documentation quality
4. **Testing** (0-100): Test coverage and quality
5. **Dependencies** (0-100): Dependency management
6. **Maintainability** (0-100): Code maintainability

### Severity Levels
- **low**: Minor issue, can be addressed later
- **medium**: Moderate issue, should be addressed soon
- **high**: Significant issue, should be addressed promptly
- **critical**: Major issue, requires immediate attention

---

## Error Handling

All endpoints return proper HTTP status codes:

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 400 | Bad request (invalid parameters) |
| 404 | Resource not found |
| 422 | Validation error (invalid parameter values) |
| 500 | Server error |

**Error Response Format:**
```json
{
  "detail": "Description of the error"
}
```

---

## Rate Limiting

Currently unlimited. In production, implement rate limiting:
- 100 requests per minute per IP
- 1000 requests per hour per API key

---

## Pagination

Not currently implemented. Future enhancement for large result sets.

---

## Sorting

Query results are sorted by relevance/recency by default. Specific sort parameters coming in future versions.

---

## Filtering Examples

### Get critical anomalies only
```
GET /analytics/teams/backend-team/anomalies?severity=critical
```

### Get unreviewed anomalies
```
GET /analytics/teams/backend-team/anomalies?reviewed=false
```

### Get developer contributions for last 90 days
```
GET /analytics/teams/backend-team/developers?days=90
```

### Get alerts with high severity
```
GET /analytics/teams/backend-team/alerts?severity=high
```

---

## Integration Examples

### Frontend API Client Usage
```typescript
import { apiClient } from '@/services/apiClient';

// Load dashboard data
const caqi = await apiClient.getTeamCAQI('backend-team');
const anomalies = await apiClient.getAnomalies('backend-team');
const developers = await apiClient.getDeveloperContributions('backend-team');

// Filter anomalies
const criticalAnomalies = await apiClient.getAnomalies(
  'backend-team',
  'critical'
);

// Review anomaly
await apiClient.reviewAnomaly('backend-team', 'anom-1', 'Reviewed');

// Check API health
const health = await apiClient.health();
```

### cURL Examples
```bash
# Get CAQI score
curl http://localhost:8000/api/v1/analytics/teams/backend-team/caqi

# Get anomalies
curl http://localhost:8000/api/v1/analytics/teams/backend-team/anomalies

# Get anomalies with filter
curl "http://localhost:8000/api/v1/analytics/teams/backend-team/anomalies?severity=critical"

# Get developers
curl "http://localhost:8000/api/v1/analytics/teams/backend-team/developers?days=30"

# Review anomaly
curl -X POST http://localhost:8000/api/v1/analytics/teams/backend-team/anomalies/anom-1/review \
  -H "Content-Type: application/json" \
  -d '{"notes":"Reviewed"}'
```

---

## Version History

- **v1** (Current): Initial API release with 8 endpoints
  - CAQI endpoint
  - Trends endpoint
  - Anomalies endpoint
  - Developers endpoint
  - Peer comparison endpoint
  - Alerts endpoint
  - Benchmarks endpoint
  - Health endpoint

---

## Support & Feedback

For issues or feature requests, contact the development team.

**Last Updated:** 2026-06-06  
**API Version:** 1.0
