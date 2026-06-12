---
created_at: 2026-06-12T18:16:43Z
title: Api Batch-Refactor Analyze-Snippet Github Zip
source: claude-code
project: codescanner
---

# CodeScanner API Reference

**Base URL:** `http://localhost:8000/api/v1/scan`

---

## Endpoints Overview

| Method | Endpoint | Phase | Purpose |
|--------|----------|-------|---------|
| POST | `/sync` | Phase 1 | Scan directory (synchronous) |
| POST | `/async` | Phase 1 | Scan directory (asynchronous) |
| GET | `/{job_id}` | Phase 1 | Get scan results |
| GET | `/{job_id}/findings` | Phase 1 | Get findings only |
| GET | `/{job_id}/metrics` | Phase 1 | Get metrics only |
| POST | `/apply-refactor` | Phase 1 | Apply single refactoring |
| POST | `/batch-refactor` | Phase 3.4 | Start batch refactoring |
| GET | `/batch-refactor/{batch_id}/status` | Phase 3.4 | Get batch status |
| POST | `/batch-refactor/apply` | Phase 3.4 | Apply batch results |
| POST | `/analyze-snippet` | Phase 3.5 | Analyze code snippet |
| POST | `/scan-github` | Phase 3.6 | Scan GitHub repo |
| POST | `/scan-zip` | Phase 3.6 | Scan ZIP file |
| GET | `/github-info` | Phase 3.6 | Get GitHub repo info |
| DELETE | `/cleanup/{job_id}` | Phase 3.6 | Manual temp cleanup |

---

## Phase 1: Core Scanning

### POST /sync - Synchronous Scan

Scan a directory or code snippet synchronously.

**Request:**
```json
{
  "directory_path": "/path/to/project",
  "language": "python",
  "code": null,
  "options": {
    "security": true,
    "quality_score": true,
    "code_smells": true,
    "doc_coverage": true,
    "complexity": true
  }
}
```

**Parameters:**
- `directory_path` (string, optional) - Path to scan
- `language` (string) - "python", "javascript", "sql" (auto-detect if not specified)
- `code` (string, optional) - Code snippet to scan
- `options` (object, optional) - Analysis options

**Response:**
```json
{
  "job_id": "scan_37cc114225e5",
  "status": "completed",
  "findings": [
    {
      "file": "/path/to/file.py",
      "line": 42,
      "column": 8,
      "type": "complexity_high",
      "message": "Function has high cyclomatic complexity",
      "severity": "high",
      "language": "python"
    }
  ],
  "metrics": {
    "quality_score": 75.5,
    "complexity": {
      "high_complexity_functions": 3,
      "total_issues": 8,
      "rating": "high"
    }
  },
  "duration_ms": 1243,
  "timestamp": "2026-06-11T13:15:30.145218",
  "scanned_files": [
    {
      "name": "main.py",
      "path": "/path/to/main.py",
      "language": "python",
      "loc": 245
    }
  ],
  "function_metrics": [
    {
      "name": "process_data()",
      "file": "/path/to/file.py",
      "line": 10,
      "complexity": 8,
      "severity": "medium"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid path or options
- `500` - Server error

---

### GET /{job_id} - Get Scan Result

Retrieve scan results by job ID.

**Request:**
```
GET /scan_37cc114225e5
```

**Response:**
Same as `/sync` response above

**Status Codes:**
- `200` - Success
- `404` - Job not found

---

### GET /{job_id}/findings - Get Findings Only

Get just the findings from a scan.

**Response:**
```json
{
  "job_id": "scan_37cc114225e5",
  "findings": [...]
}
```

---

### GET /{job_id}/metrics - Get Metrics Only

Get just the metrics from a scan.

**Response:**
```json
{
  "job_id": "scan_37cc114225e5",
  "metrics": {
    "quality_score": 75.5,
    "complexity": {...}
  }
}
```

---

## Phase 3.4: Batch Refactoring

### POST /batch-refactor - Start Batch Refactoring

Request refactoring for multiple functions at once.

**Request:**
```json
{
  "functions": [
    {
      "name": "calculate_sum()",
      "file": "/path/to/file.py",
      "line": 1,
      "code": "def calculate_sum(numbers):\n    result = 0\n    for num in numbers:\n        result += num\n    return result",
      "complexity": 6,
      "severity": "medium"
    },
    {
      "name": "process_data()",
      "file": "/path/to/file.py",
      "line": 10,
      "code": "def process_data(data):\n    ...",
      "complexity": 8,
      "severity": "medium"
    }
  ],
  "category": "complexity"
}
```

**Parameters:**
- `functions` (array) - List of functions to refactor
  - `name` (string) - Function name
  - `file` (string) - File path
  - `line` (number) - Line number
  - `code` (string) - Function code
  - `complexity` (number) - Complexity metric
  - `severity` (string) - "low", "medium", "high"
- `category` (string) - "general", "complexity", "security", "style"

**Response:**
```json
{
  "batch_id": "batch_92bc6f0be0d5",
  "status": "completed",
  "total_functions": 2,
  "processed": 2,
  "results": [
    {
      "function_name": "calculate_sum()",
      "file": "/path/to/file.py",
      "line": 1,
      "original_code": "def calculate_sum(numbers):\n    result = 0\n    for num in numbers:\n        result += num\n    return result",
      "refactored_code": "def calculate_sum(numbers):\n    return sum(numbers)",
      "explanation": "Simplified to use built-in sum() function",
      "risk_level": "low",
      "status": "completed"
    },
    {
      "function_name": "process_data()",
      "file": "/path/to/file.py",
      "line": 10,
      "original_code": "...",
      "refactored_code": "...",
      "explanation": "...",
      "risk_level": "medium",
      "status": "completed"
    }
  ]
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid request
- `500` - Processing error

---

### GET /batch-refactor/{batch_id}/status - Get Batch Status

Check the status of a batch refactoring job.

**Request:**
```
GET /batch-refactor/batch_92bc6f0be0d5/status
```

**Response:**
```json
{
  "batch_id": "batch_92bc6f0be0d5",
  "status": "completed",
  "category": "complexity",
  "total_functions": 2,
  "processed": 2,
  "results": [...],
  "created_at": "2026-06-11T13:15:30.145218"
}
```

**Status Values:**
- `processing` - Currently processing
- `completed` - All functions processed
- `error` - Processing failed

---

### POST /batch-refactor/apply - Apply Batch Results

Apply batch refactoring results to files.

**Request:**
```json
{
  "batch_id": "batch_92bc6f0be0d5",
  "function_results": [
    {
      "function_name": "calculate_sum()",
      "file": "/path/to/file.py",
      "line": 1,
      "refactored_code": "def calculate_sum(numbers):\n    return sum(numbers)",
      "status": "applied"
    },
    {
      "function_name": "process_data()",
      "file": "/path/to/file.py",
      "line": 10,
      "refactored_code": "...",
      "status": "applied"
    }
  ]
}
```

**Parameters:**
- `batch_id` (string) - Batch job ID
- `function_results` (array) - Results to apply
  - `function_name` (string) - Function name
  - `file` (string) - File path
  - `refactored_code` (string) - New code to write
  - `status` (string) - "applied" to apply, "rejected" to skip

**Response:**
```json
{
  "batch_id": "batch_92bc6f0be0d5",
  "applied_count": 2,
  "total_requested": 2,
  "errors": []
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid request
- `500` - Apply failed

---

## Phase 3.5: Live Analysis

### POST /analyze-snippet - Analyze Code Snippet

Analyze a code snippet for real-time feedback.

**Request:**
```json
{
  "code": "def calculate(data):\n    result = 0\n    if len(data) > 0:\n        for item in data:\n            if isinstance(item, int):\n                result += item\n    return result",
  "language": "python"
}
```

**Parameters:**
- `code` (string) - Code to analyze
- `language` (string) - "python", "javascript", "sql"

**Response:**
```json
{
  "code_length": 142,
  "quality_score": 72,
  "complexity": {
    "high": 0,
    "medium": 1,
    "low": 0
  },
  "security_issues": 0,
  "total_issues": 1,
  "findings": [
    {
      "line": 3,
      "type": "complexity_high",
      "message": "Too many nested conditions",
      "severity": "medium"
    }
  ]
}
```

**Notes:**
- Empty code returns quality_score of 100
- Results are cached by code hash
- Cache TTL is 5 minutes

**Status Codes:**
- `200` - Success
- `400` - Invalid language
- `500` - Analysis error

---

## Phase 3.6: GitHub/ZIP Backend

### GET /github-info - Get GitHub Repo Info

Get repository information without downloading.

**Request:**
```
GET /github-info?github_url=https://github.com/django/django&branch=main
```

**Parameters:**
- `github_url` (string) - GitHub repository URL
- `branch` (string, optional) - Branch name (default: main)

**Response:**
```json
{
  "repo": "django",
  "description": "The Web framework for perfectionists with deadlines",
  "size_mb": 273.9,
  "language": "Python",
  "stars": 87814,
  "branch": "main",
  "scannable": true
}
```

**Status Codes:**
- `200` - Success
- `400` - Invalid URL
- `404` - Repository not found
- `500` - API error

---

### POST /scan-github - Scan GitHub Repository

Download and scan a GitHub repository.

**Request:**
```json
{
  "github_url": "https://github.com/django/django",
  "branch": "main",
  "language": "python"
}
```

**Parameters:**
- `github_url` (string) - GitHub repository URL
- `branch` (string, optional) - Branch to scan (default: main)
- `language` (string, optional) - Language (auto-detected if not specified)

**Response:**
Same as `/sync` response, with additional fields:
```json
{
  ...scan results...,
  "source": "github",
  "github_url": "https://github.com/django/django",
  "branch": "main",
  "temp_path": "/tmp/codescanner_abc123/extracted"
}
```

**Notes:**
- Maximum file size: 500MB (configurable)
- Download timeout: 60 seconds (configurable)
- Temp files cleaned after 1 hour
- Supports multiple GitHub URL formats

**Status Codes:**
- `200` - Success
- `400` - Invalid URL or too large
- `404` - Repository not found
- `504` - Download timeout

---

### POST /scan-zip - Scan ZIP File

Upload and scan a ZIP file.

**Request:**
```
Content-Type: multipart/form-data

file: <binary ZIP data>
language: python (optional)
```

**Parameters:**
- `file` (file) - ZIP file to upload
- `language` (string, optional) - Language (auto-detected if not specified)

**Response:**
Same as `/sync` response, with additional fields:
```json
{
  ...scan results...,
  "source": "zip",
  "filename": "myproject.zip",
  "temp_path": "/tmp/codescanner_xyz789/extracted"
}
```

**Notes:**
- Only ZIP files accepted (.zip extension)
- Maximum file size: 500MB (configurable)
- Single top-level directory is flattened
- Temp files cleaned after 1 hour

**Status Codes:**
- `200` - Success
- `400` - Invalid file type or too large
- `422` - ZIP extraction error
- `500` - Processing error

---

### DELETE /cleanup/{job_id} - Manual Cleanup

Manually remove temporary files from a scan.

**Request:**
```
DELETE /cleanup/scan_37cc114225e5
```

**Response:**
```json
{
  "status": "success",
  "message": "Cleanup request received"
}
```

**Notes:**
- Cleanup is automatic after 1 hour
- This endpoint allows manual cleanup
- Safe to call multiple times

---

## Error Responses

All endpoints may return error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid input: missing directory_path"
}
```

### 404 Not Found
```json
{
  "detail": "Scan job not found: scan_invalid"
}
```

### 413 Payload Too Large
```json
{
  "detail": "File too large (520MB > 500MB limit)"
}
```

### 422 Unprocessable Entity
```json
{
  "detail": "ZIP extraction failed: Invalid archive format"
}
```

### 504 Gateway Timeout
```json
{
  "detail": "Download failed: Request timeout after 60 seconds"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Unexpected error: [error description]"
}
```

---

## Rate Limiting

No rate limiting in Phase 3. Planned for Phase 4.

---

## Pagination

No pagination implemented. All results returned at once.

---

## Caching

- **Live Analysis:** Results cached by code hash, 5-minute TTL
- **GitHub Repo Info:** No caching (fresh on each request)
- **Scan Results:** Stored in job history, 24-hour retention

---

## Example Workflows

### Complete Local Scan

```bash
# 1. Scan directory
curl -X POST http://localhost:8000/api/v1/scan/sync \
  -H "Content-Type: application/json" \
  -d '{
    "directory_path": "/path/to/project",
    "language": "python"
  }'

# Response includes job_id: "scan_abc123"

# 2. Get full results
curl http://localhost:8000/api/v1/scan/scan_abc123

# 3. Export in different format (client-side)
# Use results from step 2 to generate HTML/CSV/etc
```

### Batch Refactoring Workflow

```bash
# 1. Extract functions from scan results
# Functions available in response.function_metrics

# 2. Start batch refactoring
curl -X POST http://localhost:8000/api/v1/scan/batch-refactor \
  -H "Content-Type: application/json" \
  -d '{
    "functions": [/*functions from step 1*/],
    "category": "complexity"
  }'

# Response includes batch_id: "batch_xyz789"

# 3. Check status (if async)
curl http://localhost:8000/api/v1/scan/batch-refactor/batch_xyz789/status

# 4. Apply results
curl -X POST http://localhost:8000/api/v1/scan/batch-refactor/apply \
  -H "Content-Type: application/json" \
  -d '{
    "batch_id": "batch_xyz789",
    "function_results": [/*modified results*/]
  }'
```

### GitHub Repo Scanning Workflow

```bash
# 1. Check repo info (pre-flight)
curl "http://localhost:8000/api/v1/scan/github-info?github_url=https://github.com/django/django"

# 2. Scan GitHub repo
curl -X POST http://localhost:8000/api/v1/scan/scan-github \
  -H "Content-Type: application/json" \
  -d '{
    "github_url": "https://github.com/django/django",
    "branch": "main",
    "language": "python"
  }'

# Response includes results + temp_path

# 3. (Optional) Manual cleanup
curl -X DELETE http://localhost:8000/api/v1/scan/cleanup/scan_abc123
```

---

## Testing Endpoints

### Using curl

```bash
# Test server health
curl http://localhost:8000/api/v1/scan/

# Test with example data
curl -X POST http://localhost:8000/api/v1/scan/analyze-snippet \
  -H "Content-Type: application/json" \
  -d '{
    "code": "def test(): pass",
    "language": "python"
  }'
```

### Using Python requests

```python
import requests

# Analyze snippet
response = requests.post(
    'http://localhost:8000/api/v1/scan/analyze-snippet',
    json={'code': 'def test(): pass', 'language': 'python'}
)
print(response.json())

# Scan GitHub
response = requests.post(
    'http://localhost:8000/api/v1/scan/scan-github',
    json={'github_url': 'https://github.com/django/django'}
)
print(response.json())
```

### Using JavaScript/TypeScript

```typescript
// Analyze snippet
const response = await fetch('http://localhost:8000/api/v1/scan/analyze-snippet', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ code: 'def test(): pass', language: 'python' })
});
const data = await response.json();
console.log(data);
```

---

**Last Updated:** June 2026  
**API Version:** 3.6  
**Status:** Production Ready
