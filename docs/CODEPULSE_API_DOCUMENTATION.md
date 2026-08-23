# CodePulse AI - API Documentation

## Overview

CodePulse AI is a multi-agent code improvement platform that automatically analyzes, suggests improvements, and creates pull requests for code refactoring.

**Version:** 1.0.0  
**Status:** Production Ready  
**Last Updated:** 2026-07-05

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Core API Endpoints](#core-api-endpoints)
3. [Data Models](#data-models)
4. [Workflows](#workflows)
5. [Error Handling](#error-handling)
6. [Authentication](#authentication)
7. [Rate Limiting](#rate-limiting)
8. [Examples](#examples)

---

## Getting Started

### Installation

```bash
pip install codepulse-ai
```

### Basic Usage

```python
from codepulse import CodePulseClient

client = CodePulseClient(
    api_key="your-api-key",
    github_token="your-github-token"
)

# Start analysis
result = client.analyze_and_improve(
    repo_path="/path/to/repo",
    create_pr=True
)
```

---

## Core API Endpoints

### 1. File Modification API

**Endpoint:** `POST /api/v1/files/modify`

**Request:**
```json
{
    "file_path": "src/main.py",
    "suggestion": {
        "agent": "Agent A",
        "description": "Extract helper functions",
        "changes": ["New: check_valid()"],
        "new_imports": ["ast"],
        "modified_code": "def check_valid(code):\n    ...",
        "complexity_reduction": 30,
        "risk_level": "low"
    },
    "dry_run": false
}
```

**Response:**
```json
{
    "success": true,
    "files_modified": ["src/main.py"],
    "changes": {
        "files": 1,
        "lines_added": 42,
        "lines_removed": 18,
        "imports_added": ["ast"]
    }
}
```

### 2. Code Formatting API

**Endpoint:** `POST /api/v1/code/format`

**Request:**
```json
{
    "code": "def hello():\n    x=1\n    return x",
    "language": "python",
    "file_path": "main.py"
}
```

**Response:**
```json
{
    "success": true,
    "formatted_code": "def hello():\n    x = 1\n    return x",
    "language": "python",
    "lines_changed": 1
}
```

### 3. Code Validation API

**Endpoint:** `POST /api/v1/code/validate`

**Request:**
```json
{
    "code": "def hello():\n    return 42",
    "language": "python",
    "checks": ["syntax", "linting", "tests"]
}
```

**Response:**
```json
{
    "success": true,
    "syntax_valid": true,
    "linting_passed": true,
    "tests_passed": true,
    "errors": []
}
```

### 4. Parallel Improvement API

**Endpoint:** `POST /api/v1/improvements/parallel`

**Request:**
```json
{
    "code": "def process():\n    ...",
    "create_individual_prs": false,
    "auto_merge": true
}
```

**Response:**
```json
{
    "success": true,
    "total_agents": 3,
    "successful_agents": 3,
    "suggestions": [...],
    "merged_suggestion": {...},
    "pr_url": "https://github.com/org/repo/pull/123"
}
```

### 5. Architecture Analysis API

**Endpoint:** `GET /api/v1/codebase/{repo_id}/architecture`

**Response:**
```json
{
    "success": true,
    "modules": [...],
    "dependencies": [...],
    "patterns": ["mvc", "layered"],
    "metrics": {
        "coupling": 0.25,
        "cohesion": 0.85,
        "complexity": 2.5
    },
    "issues": ["High coupling in api.py"],
    "recommendations": [...]
}
```

### 6. Git Risk Analysis API

**Endpoint:** `GET /api/v1/repository/{repo_id}/git-risk`

**Response:**
```json
{
    "success": true,
    "file_risks": [
        {
            "file_path": "api.py",
            "risk_level": "critical",
            "change_frequency": 23,
            "contributors": 6,
            "deletion_ratio": 0.45
        }
    ],
    "high_risk_files": [...],
    "risky_authors": [...],
    "ownership": {...},
    "recommendations": [...]
}
```

---

## Data Models

### Suggestion

```python
{
    "agent": str,                      # Agent name
    "description": str,                # Improvement description
    "changes": List[str],              # List of changes
    "new_imports": List[str],          # Imports to add
    "modified_code": str,              # Modified code
    "complexity_reduction": int,       # Complexity improvement (%)
    "risk_level": str,                 # "low", "medium", "high"
    "clarity_improvement": str,        # "poor", "fair", "good", "excellent"
    "estimated_time": str,             # "quick", "moderate", "lengthy"
    "confidence_score": float,         # 0-1 confidence
    "rationale": str                   # Why this improvement
}
```

### FileRisk

```python
{
    "file_path": str,
    "risk_level": str,                 # "low", "medium", "high", "critical"
    "change_frequency": int,           # Number of changes
    "last_modified": str,              # ISO timestamp
    "contributors": int,               # Number of authors
    "deletion_ratio": float,           # % of deletions
    "large_changes": int               # Number of large changes
}
```

### ArchitectureMetrics

```python
{
    "total_modules": int,
    "total_classes": int,
    "total_functions": int,
    "total_lines_of_code": int,
    "average_module_size": float,
    "coupling": float,                 # 0-1, lower is better
    "cohesion": float,                 # 0-1, higher is better
    "cyclomatic_complexity": float,    # Lower is better
    "code_duplication_ratio": float    # % of duplicated code
}
```

---

## Workflows

### Workflow 1: Code Improvement

```
1. Analyze codebase → Architecture + Git Risk
2. Run parallel agents → Get suggestions
3. Modify files → Apply changes
4. Format code → Black/Prettier
5. Validate → Syntax + Linting + Tests
6. Generate diff → Show changes
7. Create PR → Push to GitHub
```

### Workflow 2: Risk Assessment

```
1. Extract git history → Last 90 days
2. Analyze changes → Per-file statistics
3. Calculate risk scores → Low/Medium/High/Critical
4. Track ownership → Primary author per file
5. Identify risky authors → Risk scoring
6. Generate recommendations → Actionable items
```

### Workflow 3: Architecture Analysis

```
1. Discover modules → Scan for .py files
2. Extract dependencies → Import analysis
3. Detect patterns → MVC/Layered/Microservices
4. Find design patterns → Singleton/Factory/etc
5. Calculate metrics → Coupling/Cohesion/Complexity
6. Identify issues → High coupling, large modules
7. Generate recommendations → Refactoring suggestions
```

---

## Error Handling

### Error Codes

| Code | Description | Resolution |
|------|-------------|-----------|
| 400 | Bad Request | Check request format |
| 401 | Unauthorized | Verify API key |
| 403 | Forbidden | Check permissions |
| 404 | Not Found | Verify file/repo path |
| 409 | Conflict | Merge conflict in PR |
| 429 | Too Many Requests | Wait before retrying |
| 500 | Internal Server Error | Check logs |
| 503 | Service Unavailable | Retry later |

### Error Response Format

```json
{
    "success": false,
    "error": "Description of error",
    "error_code": "ERROR_CODE",
    "details": {
        "field": "additional context"
    }
}
```

---

## Authentication

### API Key Authentication

```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://api.codepulse.ai/v1/code/format
```

### GitHub Token

Required for PR creation:

```python
client = CodePulseClient(
    api_key="your-api-key",
    github_token="ghp_xxxxxxxxxxxx"
)
```

---

## Rate Limiting

### Limits

- **Requests:** 1,000 per hour
- **Files:** 100 per request
- **Code size:** 10MB per request

### Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1625097600
```

---

## Examples

### Example 1: Improve Code Quality

```python
from codepulse import CodePulseClient

client = CodePulseClient(api_key="your-key")

# Analyze and improve
result = client.analyze_and_improve(
    repo_path="/path/to/repo",
    create_pr=True,
    auto_merge=False
)

print(f"PR created: {result.pr_url}")
print(f"Files improved: {len(result.files_modified)}")
```

### Example 2: Analyze Architecture

```python
from codepulse.architecture import ArchitectureAnalyzer

analyzer = ArchitectureAnalyzer("/path/to/repo")
analysis = analyzer.analyze()

print(f"Modules: {analysis.metrics.total_modules}")
print(f"Coupling: {analysis.metrics.coupling:.2%}")
print(f"Cohesion: {analysis.metrics.cohesion:.2%}")

for pattern in analysis.detected_patterns:
    print(f"Pattern: {pattern}")
```

### Example 3: Assess Git Risk

```python
from codepulse.git_risk import GitRiskAnalyzer

analyzer = GitRiskAnalyzer("/path/to/repo")
analysis = analyzer.analyze()

for file_risk in analysis.high_risk_files:
    print(f"Risk file: {file_risk.file_path} ({file_risk.risk_level})")

for author, score in analysis.high_risk_authors:
    print(f"Risky author: {author} (score: {score})")
```

---

## Configuration

### Environment Variables

```bash
# API Configuration
CODEPULSE_API_KEY=your-api-key
CODEPULSE_API_URL=https://api.codepulse.ai

# GitHub Integration
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_OWNER=your-org
GITHUB_REPO=your-repo

# Analysis Configuration
ANALYSIS_DAYS=90
MAX_AGENTS=3
AUTO_MERGE=false
```

### Configuration File

```yaml
# codepulse.yml
codepulse:
  api_key: ${CODEPULSE_API_KEY}
  github_token: ${GITHUB_TOKEN}

analysis:
  days: 90
  languages:
    - python
    - javascript

agents:
  max_concurrent: 3
  timeout: 60

formatting:
  python:
    formatter: black
  javascript:
    formatter: prettier

validation:
  syntax: true
  linting: true
  tests: true
```

---

## Monitoring & Alerts

### Metrics to Monitor

- **Pipeline latency:** < 2 seconds
- **Success rate:** > 99%
- **Agent execution time:** < 60 seconds each
- **Error rate:** < 0.1%

### Alert Thresholds

- Pipeline latency > 5 seconds
- Success rate < 95%
- Error rate > 1%
- Memory usage > 80%

### Health Check

```bash
curl https://api.codepulse.ai/health

# Response
{
    "status": "healthy",
    "components": {
        "formatter": "ok",
        "validator": "ok",
        "github": "ok",
        "database": "ok"
    }
}
```

---

## Support & Troubleshooting

### Common Issues

**Q: PR creation fails with 401**
A: Check GitHub token is valid and has `repo` scope

**Q: Formatting takes too long**
A: Check code size < 10MB; split large files

**Q: Validation fails on valid code**
A: Ensure linters/formatters are installed

---

## API Changelog

### v1.0.0 (2026-07-05)
- Initial release
- File modification API
- Code formatting API
- Code validation API
- Parallel improvement API
- Architecture analysis API
- Git risk analysis API

---

## License

CodePulse AI is licensed under the Apache 2.0 License.
