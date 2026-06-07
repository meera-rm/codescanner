# Iteration Until Clean - API Reference Guide

**Version:** 3.5.0  
**Base URL:** `http://localhost:8000/api/v1/iteration`  
**Content-Type:** `application/json`

---

## Quick Reference

| Method | Endpoint | Status | Purpose |
|--------|----------|--------|---------|
| POST | `/fix-until-clean` | 202 | Start iteration job |
| GET | `/{job_id}` | 200/404 | Get full status |
| GET | `/{job_id}/progress` | 200/404 | Get lightweight progress |
| GET | `/{job_id}/history` | 200/404 | Get detailed history |
| POST | `/{job_id}/cancel` | 202/400/404 | Cancel job |
| DELETE | `/{job_id}` | 204/400/404 | Delete job |

---

## Detailed Endpoint Reference

### 1. POST /fix-until-clean

**Start a new iteration until clean job**

#### Request

```http
POST /api/v1/iteration/fix-until-clean HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "directory_path": "/Users/meera/Documents/codescanner",
  "target_grade": "A",
  "max_iterations": 10
}
```

**Parameters:**
| Name | Type | Required | Default | Constraints |
|------|------|----------|---------|-------------|
| directory_path | string | Yes | - | Valid path to codebase |
| target_grade | string | No | "A" | Pattern: `^[A-F][+-]?$` (A, B-, B, B+, C, D, F) |
| max_iterations | integer | No | 10 | Range: 1-50 |

#### Response

**202 Accepted**
```json
{
  "job_id": "iterate_abc12345",
  "status": "processing",
  "message": "Starting iteration until A...",
  "created_at": "2026-06-06T14:30:00"
}
```

**Fields:**
| Field | Type | Description |
|-------|------|-------------|
| job_id | string | Unique identifier for tracking job |
| status | string | Always "processing" for new jobs |
| message | string | Human-readable status message |
| created_at | datetime | ISO 8601 timestamp when job created |

#### Errors

**422 Unprocessable Entity** - Invalid request
```json
{
  "detail": [
    {
      "loc": ["body", "target_grade"],
      "msg": "string should match pattern '^[A-F][+-]?$'",
      "type": "value_error.str.pattern"
    }
  ]
}
```

#### Examples

**cURL**
```bash
curl -X POST http://localhost:8000/api/v1/iteration/fix-until-clean \
  -H "Content-Type: application/json" \
  -d '{
    "directory_path": "/code",
    "target_grade": "A",
    "max_iterations": 10
  }'
```

**Python (requests)**
```python
import requests

response = requests.post(
    "http://localhost:8000/api/v1/iteration/fix-until-clean",
    json={
        "directory_path": "/code",
        "target_grade": "A",
        "max_iterations": 10
    }
)
job_id = response.json()["job_id"]
print(f"Job started: {job_id}")
```

**JavaScript (fetch)**
```javascript
const response = await fetch('http://localhost:8000/api/v1/iteration/fix-until-clean', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    directory_path: '/code',
    target_grade: 'A',
    max_iterations: 10
  })
});
const data = await response.json();
console.log(`Job ID: ${data.job_id}`);
```

---

### 2. GET /{job_id}

**Get full job status including history and metrics**

#### Request

```http
GET /api/v1/iteration/iterate_abc12345 HTTP/1.1
Host: localhost:8000
```

**Parameters:** None

#### Response

**200 OK**
```json
{
  "job_id": "iterate_abc12345",
  "status": "completed",
  "start_grade": "C",
  "final_grade": "A",
  "grade_improvement": 23,
  "iterations_count": 4,
  "max_iterations": 10,
  "current_iteration": 4,
  "target_grade": "A",
  "progress_percent": 100,
  "history": [
    {
      "iteration_number": 1,
      "grade_before": "C",
      "grade_after": "B-",
      "issues_fixed": 5,
      "agent_selected": "Agent A (Simplicity First)",
      "fix_description": "Extracted 3 helper functions from analyze_code()",
      "validation_passed": true,
      "applied_at": "2026-06-06T14:31:00",
      "changes": {
        "complexity_reduction": 60
      }
    },
    {
      "iteration_number": 2,
      "grade_before": "B-",
      "grade_after": "B",
      "issues_fixed": 6,
      "agent_selected": "Agent A (Simplicity First)",
      "fix_description": "Removed 45 lines of code duplication",
      "validation_passed": true,
      "applied_at": "2026-06-06T14:34:00",
      "changes": {
        "complexity_reduction": 45
      }
    },
    {
      "iteration_number": 3,
      "grade_before": "B",
      "grade_after": "A-",
      "issues_fixed": 10,
      "agent_selected": "Agent A (Simplicity First)",
      "fix_description": "Added type hints and restructured modules",
      "validation_passed": true,
      "applied_at": "2026-06-06T14:37:00",
      "changes": {
        "complexity_reduction": 50
      }
    },
    {
      "iteration_number": 4,
      "grade_before": "A-",
      "grade_after": "A",
      "issues_fixed": 2,
      "agent_selected": "Agent A (Simplicity First)",
      "fix_description": "Fixed final edge cases",
      "validation_passed": true,
      "applied_at": "2026-06-06T14:40:00",
      "changes": {
        "complexity_reduction": 40
      }
    }
  ],
  "metrics": {
    "total_iterations": 4,
    "total_issues_fixed": 23,
    "final_grade": "A",
    "complexity_reduction": "28 → 8 (71%)",
    "agents_used": [
      "Agent A (Simplicity First)"
    ]
  },
  "created_at": "2026-06-06T14:30:00",
  "started_at": "2026-06-06T14:30:05",
  "completed_at": "2026-06-06T14:45:00",
  "error_message": null
}
```

**Status Values:**
| Value | Meaning |
|-------|---------|
| processing | Job is currently running |
| completed | Job finished successfully |
| failed | Job encountered an error |
| cancelled | Job was cancelled by user |

#### Errors

**404 Not Found**
```json
{
  "detail": "Job not found"
}
```

#### Examples

**cURL**
```bash
curl http://localhost:8000/api/v1/iteration/iterate_abc12345
```

**Python**
```python
import requests

response = requests.get(
    "http://localhost:8000/api/v1/iteration/iterate_abc12345"
)
job = response.json()
print(f"Grade: {job['final_grade']}")
print(f"Iterations: {job['iterations_count']}")
```

---

### 3. GET /{job_id}/progress

**Get lightweight progress update (useful for polling)**

#### Request

```http
GET /api/v1/iteration/iterate_abc12345/progress HTTP/1.1
Host: localhost:8000
```

#### Response

**200 OK**
```json
{
  "job_id": "iterate_abc12345",
  "status": "processing",
  "current_iteration": 2,
  "max_iterations": 10,
  "current_grade": "B",
  "target_grade": "A",
  "progress_percent": 20,
  "estimated_remaining": "~8 minutes"
}
```

**Use Case:** Poll this endpoint instead of full `/api/v1/iteration/{job_id}` for lighter payloads.

#### Examples

**Python - Polling Loop**
```python
import time
import requests

job_id = "iterate_abc12345"

while True:
    response = requests.get(
        f"http://localhost:8000/api/v1/iteration/{job_id}/progress"
    )
    progress = response.json()
    
    print(f"Progress: {progress['progress_percent']}% - {progress['current_grade']}")
    
    if progress['status'] in ['completed', 'failed', 'cancelled']:
        break
    
    time.sleep(2)
```

---

### 4. GET /{job_id}/history

**Get detailed iteration history with summary**

#### Request

```http
GET /api/v1/iteration/iterate_abc12345/history HTTP/1.1
Host: localhost:8000
```

#### Response

**200 OK**
```json
{
  "job_id": "iterate_abc12345",
  "iterations": [
    {
      "iteration_number": 1,
      "grade_before": "C",
      "grade_after": "B-",
      "issues_fixed": 5,
      "agent_selected": "Agent A (Simplicity First)",
      "fix_description": "Extracted 3 helper functions from analyze_code()",
      "validation_passed": true,
      "applied_at": "2026-06-06T14:31:00",
      "changes": {
        "complexity_reduction": 60
      }
    }
  ],
  "summary": {
    "total_iterations": 4,
    "total_issues_fixed": 23,
    "agents_used": {
      "Agent A (Simplicity First)": 4,
      "Agent B (Architecture Focused)": 0,
      "Agent C (Performance Optimized)": 0
    },
    "final_grade": "A"
  }
}
```

#### Examples

**JavaScript - Parse History**
```javascript
const response = await fetch('http://localhost:8000/api/v1/iteration/iterate_abc12345/history');
const data = await response.json();

console.log(`Total iterations: ${data.summary.total_iterations}`);
console.log(`Issues fixed: ${data.summary.total_issues_fixed}`);
console.log(`Final grade: ${data.summary.final_grade}`);

// Print each iteration
data.iterations.forEach(it => {
  console.log(`\nIteration ${it.iteration_number}:`);
  console.log(`  ${it.grade_before} → ${it.grade_after}`);
  console.log(`  Fixed: ${it.issues_fixed} issues`);
  console.log(`  Agent: ${it.agent_selected}`);
});
```

---

### 5. POST /{job_id}/cancel

**Cancel a running or queued job**

#### Request

```http
POST /api/v1/iteration/iterate_abc12345/cancel HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "reason": "User requested cancellation"
}
```

**Parameters:**
| Name | Type | Required | Description |
|------|------|----------|-------------|
| reason | string | No | Optional reason for cancellation |

#### Response

**202 Accepted**
```json
{
  "job_id": "iterate_abc12345",
  "status": "cancelled",
  "message": "Job cancellation requested"
}
```

#### Errors

**400 Bad Request** - Job already completed
```json
{
  "detail": "Cannot cancel job in completed state"
}
```

**404 Not Found**
```json
{
  "detail": "Job not found"
}
```

#### Examples

**cURL**
```bash
curl -X POST http://localhost:8000/api/v1/iteration/iterate_abc12345/cancel \
  -H "Content-Type: application/json" \
  -d '{"reason": "User requested"}'
```

---

### 6. DELETE /{job_id}

**Delete a completed job and its history**

#### Request

```http
DELETE /api/v1/iteration/iterate_abc12345 HTTP/1.1
Host: localhost:8000
```

#### Response

**204 No Content**
(Empty response)

#### Errors

**400 Bad Request** - Job still processing
```json
{
  "detail": "Cannot delete job in processing state"
}
```

**404 Not Found**
```json
{
  "detail": "Job not found"
}
```

#### Examples

**cURL**
```bash
curl -X DELETE http://localhost:8000/api/v1/iteration/iterate_abc12345
```

**Python**
```python
import requests

requests.delete(
    "http://localhost:8000/api/v1/iteration/iterate_abc12345"
)
print("Job deleted successfully")
```

---

## Response Codes Reference

| Code | Name | When |
|------|------|------|
| 200 | OK | Successful GET request |
| 202 | Accepted | Job started or cancellation requested |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid state transition |
| 404 | Not Found | Job doesn't exist |
| 422 | Unprocessable Entity | Invalid request parameters |
| 500 | Internal Server Error | Server error (rare) |

---

## Rate Limiting

No rate limiting on iteration endpoints (uses global API key limits if auth enabled).

---

## Webhooks (Future)

Once implemented, you can subscribe to iteration events:
- `iteration.started`
- `iteration.step_completed`
- `iteration.completed`
- `iteration.failed`

---

## Best Practices

### 1. Polling Pattern
```python
import time
import requests

job_id = "iterate_abc12345"

# Poll progress every 5 seconds
while True:
    response = requests.get(
        f"http://localhost:8000/api/v1/iteration/{job_id}/progress"
    )
    if response.status_code == 404:
        print("Job not found")
        break
    
    progress = response.json()
    
    if progress['status'] == 'completed':
        # Get full results
        full = requests.get(
            f"http://localhost:8000/api/v1/iteration/{job_id}"
        ).json()
        print(f"Final grade: {full['final_grade']}")
        break
    elif progress['status'] == 'failed':
        print("Job failed")
        break
    
    print(f"{progress['progress_percent']}%")
    time.sleep(5)
```

### 2. Error Handling
```python
import requests

try:
    response = requests.post(
        "http://localhost:8000/api/v1/iteration/fix-until-clean",
        json={"directory_path": "/code"}
    )
    response.raise_for_status()  # Raise for 4xx/5xx
    job_id = response.json()["job_id"]
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
```

### 3. Cleanup
```python
import requests

# Always cleanup completed jobs
response = requests.get(
    f"http://localhost:8000/api/v1/iteration/{job_id}"
)
job = response.json()

if job['status'] in ['completed', 'failed', 'cancelled']:
    requests.delete(
        f"http://localhost:8000/api/v1/iteration/{job_id}"
    )
```

---

## Debugging

### Common Issues

**Job not found (404)**
- Check job_id spelling
- Job may have been deleted
- Use `/progress` instead of full endpoint

**Cannot cancel (400)**
- Job already completed/failed
- Use DELETE to remove completed jobs

**Invalid target_grade (422)**
- Must match pattern: `^[A-F][+-]?$`
- Valid examples: A, B-, B, B+, C, D-, F

---

## Changelog

### v3.5.0 (Current)
- Initial release
- 6 endpoints
- Full CRUD operations
- History tracking

