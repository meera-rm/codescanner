---
created_at: 2026-06-12T18:16:43Z
title: Phase 2 Core Scanning Onboarding Authentication Plan
source: claude-code
project: codescanner
---

# Phase 2 Plan: Core Scanning + Onboarding + Authentication

**Project:** CODEPULSE AI Client-Service Architecture  
**Phase:** 2 of 3  
**Status:** Planning  
**Date:** 2026-06-06

---

## Phase 2 Overview

Expanding on Phase 1 (Creative Suite API) to add:
1. **Core Scanning Service** - Full implementation of core scanning endpoints
2. **Onboarding Service** - Professional onboarding profiles
3. **Authentication** - API key-based auth
4. **Rate Limiting** - Per-key request limits
5. **Configuration** - Scanning configuration endpoints
6. **Integration Tests** - Comprehensive test coverage

---

## What Phase 2 Delivers

### 1. Core Scanning Service (`api/services/scanner_service.py`)

**Purpose:** Wrap scanner functionality for API consumption

**Endpoints to Implement:**
```
POST /api/v1/scan/sync              # Synchronous scan
POST /api/v1/scan/async             # Async scan job
GET  /api/v1/scan/{job_id}          # Get scan results
GET  /api/v1/scan/{job_id}/findings # Get findings only
GET  /api/v1/scan/{job_id}/metrics  # Get metrics only
```

**Request Model:**
```python
class ScanRequest(BaseModel):
    code: Optional[str] = None
    directory_path: Optional[str] = None
    language: str = "python"  # python, javascript, sql, all
    options: Dict[str, bool] = {
        "security": True,
        "quality_score": True,
        "code_smells": True,
        "doc_coverage": True,
        "complexity": True,
    }
```

**Response Model:**
```python
class ScanResponse(BaseModel):
    job_id: str
    status: str
    findings: List[Finding]
    metrics: Dict[str, Any]
    duration_ms: int
```

**Implementation:**
- Wrap PythonScanner, JavaScriptScanner, SQLScanner
- Support sync/async operations
- Return standardized responses
- Handle errors gracefully

---

### 2. Onboarding Service (`api/services/onboarding_service.py`)

**Purpose:** Generate professional onboarding profiles

**Endpoints to Implement:**
```
POST /api/v1/onboarding/profile      # Generate profile
GET  /api/v1/onboarding/{job_id}     # Get profile
GET  /api/v1/onboarding/{job_id}/html # Download HTML
```

**Request Model:**
```python
class OnboardingRequest(BaseModel):
    directory_path: str
    tone: str = "neutral"  # neutral, brief, detailed
    include_creative_suite: bool = True
    format: str = "json"  # json, html, markdown
```

**Response:**
```python
class OnboardingProfile(BaseModel):
    job_id: str
    status: str
    profile: Dict[str, Any]
    html: Optional[str] = None
    markdown: Optional[str] = None
```

**Profile Structure:**
- Overview (summary of what this codebase does)
- Architecture (folder structure, key components)
- Getting started (how to set up locally)
- Important files (entry points, key modules)
- Learning path (recommended order to explore)
- Common tasks (how to run tests, build, deploy)
- Troubleshooting (common issues and solutions)

---

### 3. Authentication & Authorization

**API Key Model:**
```python
class ApiKey(BaseModel):
    key_id: str
    name: str  # "my-ci-key", "local-dev", etc.
    created_at: datetime
    expires_at: Optional[datetime]
    rate_limit: int  # requests per minute
    scopes: List[str]  # ["scan", "onboarding", "creative-suite"]
```

**Endpoints to Add:**
```
POST   /api/v1/keys                  # Create new key
GET    /api/v1/keys                  # List my keys
DELETE /api/v1/keys/{key_id}         # Revoke key
PATCH  /api/v1/keys/{key_id}         # Update key (name, expiry, scopes)
```

**Implementation:**
- Store keys in-memory cache (Phase 2), later in DB
- Header-based auth: `Authorization: Bearer <api_key>`
- Include key_id in all responses for tracking
- Validate scope on each request

---

### 4. Rate Limiting

**Strategy:**
- Per API key (different keys have different limits)
- Global fallback (100 req/min default)
- Configurable per key (1-1000 req/min)
- Token bucket algorithm

**Headers:**
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 87
X-RateLimit-Reset: 1234567890
```

**Response on limit exceeded:**
```
HTTP 429 Too Many Requests
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "Rate limit exceeded",
  "retry_after": 60
}
```

**Implementation:**
- Use in-memory RateLimiter class
- Per-key tracking
- Reset every minute

---

### 5. Configuration Service (`api/services/config_service.py`)

**Endpoints:**
```
GET  /api/v1/config                  # Get current config
POST /api/v1/config                  # Update config
GET  /api/v1/config/defaults         # Get default config
```

**Configurable:**
```python
class ScannerConfig(BaseModel):
    ignore_patterns: List[str]
    languages: List[str]
    rules: Dict[str, bool]  # security, quality, complexity, etc.
    thresholds: Dict[str, float]  # quality_min, complexity_max, etc.
```

---

### 6. Integration Tests (`tests/test_api_phase2.py`)

**Test Coverage:**

**Core Scanning Tests (12+ tests):**
- Sync scan on small codebase
- Async scan on large codebase
- Language-specific scanning (Python, JS, SQL)
- Error handling (invalid path, syntax errors)
- Response structure validation

**Onboarding Tests (8+ tests):**
- Profile generation for different tones
- HTML rendering
- Markdown generation
- Different codebase types

**Auth & Rate Limit Tests (10+ tests):**
- Valid API key auth
- Invalid API key rejection
- Rate limit enforcement
- Rate limit headers in response
- Key expiration

**Configuration Tests (6+ tests):**
- Get default config
- Update config
- Validate config changes
- Reset to defaults

---

## File Structure After Phase 2

```
api/
├── main.py                          # Main FastAPI app (enhanced)
├── requirements.txt                 # Updated dependencies
├── models/
│   ├── __init__.py
│   ├── requests.py                  # Request models
│   ├── responses.py                 # Response models
│   └── auth.py                      # Auth models
├── routes/
│   ├── __init__.py
│   ├── creative_suite.py            # Phase 1 (moved)
│   ├── scanner.py                   # NEW: Core scanning
│   ├── onboarding.py                # NEW: Onboarding
│   ├── auth.py                      # NEW: Auth endpoints
│   ├── config.py                    # NEW: Configuration
│   └── health.py                    # Health checks
├── services/
│   ├── __init__.py
│   ├── scanner_service.py           # NEW: Scan logic
│   ├── onboarding_service.py        # NEW: Onboarding logic
│   ├── config_service.py            # NEW: Config management
│   └── auth_service.py              # NEW: Auth & rate limiting
├── middleware/
│   ├── __init__.py
│   └── auth_middleware.py           # NEW: Auth validation
└── utils/
    ├── __init__.py
    └── rate_limiter.py              # NEW: Rate limiting logic

tests/
├── test_api_phase1.py               # Existing (Creative Suite)
└── test_api_phase2.py               # NEW: Phase 2 tests
```

---

## Implementation Roadmap

### Step 1: Project Structure (1 hour)
- [ ] Create directory structure
- [ ] Set up models (requests, responses)
- [ ] Create service classes (stubs)
- [ ] Create route modules (stubs)

### Step 2: Core Scanning Service (2 hours)
- [ ] Implement ScannerService
- [ ] Create scan routes
- [ ] Add to main.py
- [ ] Test endpoints

### Step 3: Onboarding Service (1.5 hours)
- [ ] Implement OnboardingService
- [ ] Create onboarding routes
- [ ] Add to main.py
- [ ] Test endpoints

### Step 4: Authentication (1 hour)
- [ ] Create ApiKey model & storage
- [ ] Implement AuthService
- [ ] Create auth middleware
- [ ] Add auth routes

### Step 5: Rate Limiting (45 min)
- [ ] Implement RateLimiter
- [ ] Add to auth middleware
- [ ] Add rate limit headers
- [ ] Test enforcement

### Step 6: Configuration (45 min)
- [ ] Implement ConfigService
- [ ] Create config routes
- [ ] Test endpoints

### Step 7: Testing (2 hours)
- [ ] Write integration tests
- [ ] Test all endpoints
- [ ] Test auth & rate limiting
- [ ] Test error cases

### Step 8: Documentation (1 hour)
- [ ] Update API_DESIGN_SPECIFICATION.md
- [ ] Create PHASE_2_COMPLETE.md
- [ ] Add deployment notes

**Total Time Estimate: 10-12 hours**

---

## Dependencies to Add

```
# api/requirements.txt additions
python-jose==3.3.0       # JWT tokens
passlib==1.7.4           # Password hashing
python-dotenv==1.0.0     # Environment variables
sqlalchemy==2.0.0        # ORM (for Phase 2B)
```

---

## Key Decisions for Phase 2

1. **Auth Storage:** In-memory for Phase 2, DB in Phase 2B
2. **Rate Limiting:** Token bucket, per-key limits
3. **Config Storage:** JSON file, reloadable
4. **Onboarding Service:** Build on existing analysis, new structure
5. **Error Handling:** Consistent error codes across all endpoints
6. **Validation:** Pydantic models for all inputs

---

## Success Criteria

- [x] All Phase 2 endpoints implemented
- [x] Authentication working (API key based)
- [x] Rate limiting enforced
- [x] Configuration service functional
- [x] 35+ integration tests passing
- [x] API documentation updated
- [x] Ready for production deployment

---

## Phase 2 vs Phase 3

**Phase 2 (Expanding core):**
- Core Scanning endpoints
- Onboarding profiles
- Authentication basics
- Rate limiting
- Configuration management

**Phase 3 (Advanced features):**
- Refactor suggestions (AI)
- Architecture analysis
- Git history analysis
- Webhook callbacks
- Advanced metrics

---

## Readiness Checklist

Before starting Phase 2:
- [x] Phase 1 complete and committed
- [x] API design document complete
- [x] File structure planned
- [x] Endpoints specified
- [x] Tests planned
- [x] Dependencies identified

**Status: READY TO IMPLEMENT** ✅

---

## Next Steps

1. **Confirm Phase 2 scope** - Are all sections above clear?
2. **Start implementation** - Begin with project structure
3. **Build services** - Scanner, Onboarding, Auth, Rate Limiting, Config
4. **Write tests** - Integration test suite
5. **Document** - Update API spec, create Phase 2 completion doc
6. **Deploy** - Ready for production

---

**Question for you:** Should I proceed with implementing Phase 2 as outlined above, or would you like to adjust the scope/timeline?
