---
created_at: 2026-06-12T18:16:43Z
title: Api Design Specification
source: claude-code
project: codescanner
---

# CODEPULSE AI - Complete API Design Specification
**Version:** 1.0  
**Status:** Design Complete, Phase 1 Implementation Starting  
**Architecture:** Client-Service Model with REST API

---

## Executive Summary

Complete API specification for CODEPULSE AI enabling:
- Multiple clients (CLI, Web UI, IDE extensions)
- Scalable microservices architecture
- Incremental feature implementation
- Future-proof design

---

## API Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              CODEPULSE AI CLIENTS                   │
│  CLI | Web UI | IDE Extensions | CI/CD Integration │
└────────────────────┬────────────────────────────────┘
                     │
        ┌────────────▼────────────┐
        │  API Gateway / Router   │
        │  (FastAPI Application)  │
        └────────────┬────────────┘
                     │
    ┌────────────────┼────────────────┐
    │                │                │
┌───▼────────┐  ┌───▼────────┐  ┌───▼────────┐
│   Scanner  │  │  Creative  │  │ Onboarding │
│   Service  │  │    Suite   │  │  Service   │
│            │  │   Service  │  │            │
└────────────┘  └────────────┘  └────────────┘
    │                │                │
    └────────────────┼────────────────┘
                     │
        ┌────────────▼────────────┐
        │   Job Queue / Cache     │
        │   (Redis / In-Memory)   │
        └────────────────────────┘
```

---

## Core API Endpoints

### 1. Health & Status

#### GET /api/v1/health
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2026-06-06T12:00:00Z",
  "services": {
    "scanner": "healthy",
    "creative_suite": "healthy",
    "job_queue": "healthy"
  }
}
```

#### GET /api/v1/version
API version information

**Response:**
```json
{
  "api_version": "1.0.0",
  "scanner_version": "2.0.0",
  "features": ["creative-suite", "onboarding", "pre-commit"]
}
```

---

### 2. Core Scanning Service

#### POST /api/v1/scan/sync
Synchronous code scan (for small codebases)

**Request:**
```json
{
  "code": "python code as string",
  "language": "python",
  "options": {
    "security": true,
    "quality_score": true,
    "code_smells": true,
    "doc_coverage": true
  }
}
```

**Response:**
```json
{
  "job_id": "scan_123456",
  "status": "completed",
  "findings": [...],
  "metrics": {
    "quality_score": 75,
    "complexity": 2.5,
    "security_issues": 0
  },
  "duration_ms": 245
}
```

#### POST /api/v1/scan/async
Asynchronous scan (for large codebases)

**Request:**
```json
{
  "directory_path": "/path/to/code",
  "options": {
    "security": true,
    "quality_score": true,
    "code_smells": true,
    "doc_coverage": true
  },
  "callback_url": "https://example.com/webhook"
}
```

**Response:**
```json
{
  "job_id": "scan_789012",
  "status": "queued",
  "message": "Scan queued. Check status at /api/v1/status/scan_789012"
}
```

#### GET /api/v1/scan/{job_id}
Get scan results by job ID

**Response:**
```json
{
  "job_id": "scan_123456",
  "status": "completed",
  "progress": 100,
  "results": {
    "findings": [...],
    "metrics": {...}
  },
  "completed_at": "2026-06-06T12:05:00Z"
}
```

---

### 3. Creative Suite Service (Phase 1)

#### POST /api/v1/creative-suite/analyze
Unified Creative Suite analysis (Personality + Letter + CAQI)

**Request:**
```json
{
  "code_path": "/path/to/code",
  "analyses": ["personality", "letter", "caqi"],
  "options": {
    "include_html": true,
    "include_json": true,
    "include_markdown": true
  }
}
```

**Response:**
```json
{
  "job_id": "creative_123456",
  "status": "completed",
  "results": {
    "personality": {
      "archetype": "Anxious Overthinker",
      "traits": {...},
      "html": "<html>...</html>"
    },
    "letter": {
      "tone": "cautious",
      "sections": {...},
      "html": "<html>...</html>"
    },
    "caqi": {
      "score": 340,
      "band": "Moderate",
      "pollutants": {...},
      "html": "<html>...</html>"
    }
  },
  "files": {
    "personality.html": "...",
    "letter.html": "...",
    "caqi.html": "...",
    "dashboard.html": "..."
  }
}
```

#### GET /api/v1/creative-suite/{job_id}/personality
Get personality analysis

**Response:**
```json
{
  "archetype": "Anxious Overthinker",
  "emoji": "🤔",
  "traits": {
    "complexity": 75,
    "security": 40,
    "duplication": 60,
    "coupling": 55,
    "documentation": 70,
    "perfectionism": 85
  },
  "strengths": [...],
  "blindspots": [...]
}
```

#### GET /api/v1/creative-suite/{job_id}/letter
Get inheritance letter

**Response:**
```json
{
  "tone": "cautious",
  "sections": {
    "proud": [...],
    "not_proud": [...],
    "secrets": [...],
    "avoid": [...],
    "start_here": [...],
    "tips": [...]
  }
}
```

#### GET /api/v1/creative-suite/{job_id}/caqi
Get CAQI score

**Response:**
```json
{
  "score": 340,
  "band": "Moderate",
  "pollutants": {
    "complexity": 55,
    "security": 40,
    "duplication": 60,
    "coupling": 55,
    "documentation": 70,
    "error_handling": 50
  }
}
```

---

### 4. Onboarding Service (Phase 2)

#### POST /api/v1/onboarding/profile
Generate onboarding profile

**Request:**
```json
{
  "code_path": "/path/to/code",
  "tone": "neutral",
  "format": "html"
}
```

**Response:**
```json
{
  "job_id": "onboard_123456",
  "profile": {
    "overview": "...",
    "architecture": "...",
    "start_here": "...",
    "important_files": [...],
    "learning_path": [...]
  }
}
```

---

### 5. Job Management

#### GET /api/v1/status/{job_id}
Get job status and progress

**Response:**
```json
{
  "job_id": "scan_123456",
  "status": "processing",
  "progress": 65,
  "message": "Analyzing complexity metrics...",
  "started_at": "2026-06-06T12:00:00Z",
  "estimated_completion": "2026-06-06T12:05:00Z"
}
```

#### GET /api/v1/jobs
List all jobs for current user/session

**Response:**
```json
{
  "jobs": [
    {
      "job_id": "scan_123456",
      "type": "scan",
      "status": "completed",
      "created_at": "2026-06-06T12:00:00Z"
    }
  ],
  "total": 1,
  "limit": 10
}
```

#### DELETE /api/v1/jobs/{job_id}
Cancel or delete a job

**Response:**
```json
{
  "job_id": "scan_123456",
  "status": "cancelled",
  "message": "Job cancelled successfully"
}
```

---

### 6. Configuration (Phase 2)

#### GET /api/v1/config
Get current configuration

**Response:**
```json
{
  "ignore_patterns": ["test", "venv", "__pycache__"],
  "languages": ["python", "javascript"],
  "rules": {
    "security": "enabled",
    "quality": "enabled"
  }
}
```

#### POST /api/v1/config
Update configuration

**Request:**
```json
{
  "ignore_patterns": ["test", "venv"],
  "rules": {
    "security": true,
    "quality": true
  }
}
```

---

### 7. Future Endpoints (Ready but not implemented)

#### POST /api/v1/refactor/suggest (Phase 3)
AI-powered refactoring suggestions

#### POST /api/v1/architecture/analyze (Phase 3)
Architecture analysis and visualization

#### POST /api/v1/git/analyze (Phase 3)
Git history and risk analysis

#### POST /api/v1/pre-commit/setup (Phase 2)
Configure pre-commit hooks

---

## Data Models

### ScanRequest
```python
class ScanRequest(BaseModel):
    code: Optional[str] = None
    directory_path: Optional[str] = None
    language: str = "python"
    options: Dict[str, bool]
    callback_url: Optional[str] = None
```

### ScanResponse
```python
class ScanResponse(BaseModel):
    job_id: str
    status: str  # queued, processing, completed, failed
    findings: List[Finding]
    metrics: Dict[str, Any]
    duration_ms: Optional[int]
```

### CreativeSuiteResult
```python
class CreativeSuiteResult(BaseModel):
    personality: PersonalityResult
    letter: LetterResult
    caqi: CAQIResult
    files: Dict[str, str]  # HTML outputs
```

---

## Error Handling

### Error Response Format
```json
{
  "error": "INVALID_CODE",
  "message": "Code contains syntax errors",
  "details": {
    "line": 45,
    "column": 10,
    "error": "SyntaxError: unexpected EOF"
  },
  "status_code": 400
}
```

### Error Codes
- `400` - Bad Request (invalid input)
- `401` - Unauthorized (auth required)
- `404` - Not Found (job not found)
- `409` - Conflict (job already processing)
- `500` - Server Error
- `503` - Service Unavailable

---

## Authentication & Security

### Authentication Methods
- API Key (for CLI/tools)
- OAuth2 (for web clients)
- JWT tokens (for sessions)

### Request Headers
```
Authorization: Bearer <token>
Content-Type: application/json
User-Agent: codepulse-cli/1.0
```

### Rate Limiting
- 100 requests/minute per API key
- 1000 requests/hour per API key
- Webhook delivery: 3 retries with exponential backoff

---

## Webhook Events

### Job Completion
```json
{
  "event": "job.completed",
  "job_id": "scan_123456",
  "status": "completed",
  "results": {...},
  "timestamp": "2026-06-06T12:05:00Z"
}
```

### Job Failed
```json
{
  "event": "job.failed",
  "job_id": "scan_123456",
  "error": "Syntax error in code",
  "timestamp": "2026-06-06T12:05:00Z"
}
```

---

## Phase Implementation Roadmap

### Phase 1 (NOW)
- Core scanning endpoints
- Creative Suite (all three: Personality, Letter, CAQI)
- Job management
- Health/status endpoints

### Phase 2 (NEXT)
- Onboarding service
- Configuration endpoints
- Pre-commit integration
- Authentication (API keys)

### Phase 3 (FUTURE)
- Refactor suggestions (AI)
- Architecture analysis
- Git analysis
- Advanced caching

---

## Performance Targets

| Endpoint | Target |
|----------|--------|
| /health | <10ms |
| /scan (small file) | <500ms |
| /scan (async) | <100ms (queue time) |
| /creative-suite | <2s (all three) |
| Job status polling | <50ms |

---

## Deployment Architecture

```
┌─────────────────────────────────┐
│    Load Balancer (nginx)        │
└──────────────┬──────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼──┐  ┌───▼──┐  ┌───▼──┐
│ API  │  │ API  │  │ API  │
│  1   │  │  2   │  │  3   │
└───┬──┘  └───┬──┘  └───┬──┘
    │         │         │
    └─────────┼─────────┘
              │
    ┌─────────▼──────────┐
    │   Shared Services  │
    │  (Queue, Cache)    │
    └────────────────────┘
```

---

## Testing Strategy

- Unit tests: Each endpoint
- Integration tests: End-to-end workflows
- Load tests: Performance validation
- Security tests: Auth, rate limiting, injection

---

## Documentation

- OpenAPI/Swagger spec (auto-generated)
- Client libraries (Python, JavaScript)
- Example requests/responses
- Deployment guide
- Troubleshooting guide

---

**Status: Design Complete ✅**  
**Ready for Phase 1 Implementation**

All endpoints designed. Implementation starts with:
1. Unified CLI
2. Core scanning service
3. Creative Suite service
4. Job queue system
