"""CI/CD Integration API routes."""
import json
import os
from typing import Optional
from pathlib import Path

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel

router = APIRouter(prefix="/api/v1/ci", tags=["ci"])

# Import CLI modules
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.scanner import RepositoryScanner
from cli.formatter import ReportFormatter


class ScanRequest(BaseModel):
    """CI scan request."""
    repository: str = "."
    branch: str = "main"
    output_format: str = "json"
    fail_on_critical: bool = True
    fail_on_error: bool = False


class ScanResponse(BaseModel):
    """CI scan response."""
    status: str
    repository: str
    branch: str
    files_scanned: int
    files_by_language: dict
    summary: dict
    exit_code: int
    report: Optional[dict | list] = None


class BatchScanRequest(BaseModel):
    """Batch scan request."""
    repositories: list[str]
    output_format: str = "json"
    parallel: bool = True


class BatchScanResponse(BaseModel):
    """Batch scan response."""
    total: int
    completed: int
    failed: int
    results: list[ScanResponse]


@router.post("/scan", response_model=ScanResponse)
async def ci_scan(
    request: ScanRequest,
    background_tasks: BackgroundTasks,
) -> ScanResponse:
    """
    Scan a repository from CI/CD pipeline.

    **Parameters:**
    - `repository`: Path to repository (default: current directory)
    - `branch`: Branch name (for logging/reporting)
    - `output_format`: Report format (json, sarif, junit, sonarqube)
    - `fail_on_critical`: Exit with code 1 if critical issues found
    - `fail_on_error`: Exit with code 1 if error issues found

    **Returns:**
    - `status`: "completed" or "failed"
    - `exit_code`: 0 for success, 1 for failure
    - `summary`: Counts by severity
    - `report`: Formatted report (optional, based on output_format)

    **Example:**
    ```bash
    curl -X POST http://localhost:8000/api/v1/ci/scan \
      -H "Content-Type: application/json" \
      -d '{
        "repository": ".",
        "output_format": "sarif",
        "fail_on_critical": true
      }'
    ```
    """
    # Validate repository path
    repo_path = request.repository
    if not os.path.isdir(repo_path):
        raise HTTPException(
            status_code=400,
            detail=f"Repository path not found: {repo_path}"
        )

    try:
        # Run scanner
        scanner = RepositoryScanner(repo_path)
        scan_result = scanner.scan()

        # Determine exit code
        summary = scan_result.get('summary', {})
        exit_code = 0

        if request.fail_on_critical and summary.get('critical', 0) > 0:
            exit_code = 1
        elif request.fail_on_error and summary.get('error', 0) > 0:
            exit_code = 1

        # Format report if needed
        formatted_report = None
        if request.output_format != 'json':
            # Save JSON to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.json',
                delete=False
            ) as f:
                json.dump(scan_result, f)
                temp_path = f.name

            try:
                formatter = ReportFormatter(temp_path)

                if request.output_format == 'sarif':
                    formatted_report = formatter.to_sarif()
                elif request.output_format == 'sonarqube':
                    formatted_report = formatter.to_sonarqube()
                elif request.output_format == 'junit':
                    # Return as string for XML
                    formatted_report = {
                        'format': 'junit',
                        'content': formatter.to_junit()
                    }
            finally:
                os.unlink(temp_path)

        return ScanResponse(
            status="completed" if exit_code == 0 else "failed",
            repository=repo_path,
            branch=request.branch,
            files_scanned=scan_result.get('files_scanned', 0),
            files_by_language=scan_result.get('files_by_language', {}),
            summary=scan_result.get('summary', {}),
            exit_code=exit_code,
            report=formatted_report if formatted_report else {
                'findings_count': len(scan_result.get('findings', [])),
                'top_issues': scan_result.get('findings', [])[:5]
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch-scan", response_model=BatchScanResponse)
async def batch_ci_scan(request: BatchScanRequest) -> BatchScanResponse:
    """
    Scan multiple repositories in batch.

    **Parameters:**
    - `repositories`: List of repository paths
    - `output_format`: Report format for all scans
    - `parallel`: Run scans in parallel (default: true)

    **Returns:**
    - `total`: Total repositories scanned
    - `completed`: Successful scans
    - `failed`: Failed scans
    - `results`: Array of scan results

    **Example:**
    ```bash
    curl -X POST http://localhost:8000/api/v1/ci/batch-scan \
      -H "Content-Type: application/json" \
      -d '{
        "repositories": ["/path/to/repo1", "/path/to/repo2"],
        "output_format": "sarif",
        "parallel": true
      }'
    ```
    """
    results = []
    completed = 0
    failed = 0

    for repo_path in request.repositories:
        try:
            scan_req = ScanRequest(
                repository=repo_path,
                output_format=request.output_format,
            )

            # Reuse the single scan endpoint
            result = await ci_scan(scan_req, BackgroundTasks())
            results.append(result)
            completed += 1

        except Exception as e:
            results.append(
                ScanResponse(
                    status="failed",
                    repository=repo_path,
                    branch="unknown",
                    files_scanned=0,
                    files_by_language={},
                    summary={'error': 1},
                    exit_code=1,
                )
            )
            failed += 1

    return BatchScanResponse(
        total=len(request.repositories),
        completed=completed,
        failed=failed,
        results=results
    )


@router.get("/status")
async def ci_status() -> dict:
    """
    Check CI/CD integration status.

    **Returns:**
    - `status`: "healthy" or "unhealthy"
    - `version`: CodePulse version
    - `scanners`: Available scanners
    - `formats`: Supported output formats

    **Example:**
    ```bash
    curl http://localhost:8000/api/v1/ci/status
    ```
    """
    return {
        "status": "healthy",
        "version": "3.5.0",
        "scanners": {
            "python": {"status": "available", "version": "3.12+"},
            "javascript": {"status": "available", "version": "latest"},
            "sql": {"status": "available", "version": "latest"},
        },
        "formats": ["json", "sarif", "junit", "sonarqube"],
        "endpoints": {
            "scan": "/api/v1/ci/scan",
            "batch_scan": "/api/v1/ci/batch-scan",
            "status": "/api/v1/ci/status",
        }
    }


@router.post("/webhook")
async def ci_webhook(payload: dict) -> dict:
    """
    Webhook endpoint for CI/CD platforms to push events.

    **Supported Platforms:**
    - GitHub Actions
    - GitLab CI
    - Jenkins
    - CircleCI
    - TravisCI

    **Payload Format:**
    ```json
    {
        "platform": "github",
        "event": "push",
        "repository": "owner/repo",
        "branch": "main",
        "commit_hash": "abc123...",
        "callback_url": "https://..."
    }
    ```

    **Returns:**
    ```json
    {
        "status": "received",
        "webhook_id": "wh_xyz789",
        "scan_job_id": "job_123"
    }
    ```
    """
    platform = payload.get('platform', None)
    event = payload.get('event', None)

    if not platform or platform == 'unknown':
        raise HTTPException(status_code=400, detail="Missing platform")

    if not event or event == 'unknown':
        raise HTTPException(status_code=400, detail="Missing event")

    # Generate webhook ID
    import hashlib
    webhook_id = hashlib.md5(
        f"{platform}-{event}-{payload.get('repository', 'unknown')}".encode()
    ).hexdigest()[:12]

    # In production, this would queue a background job
    return {
        "status": "received",
        "platform": platform,
        "event": event,
        "webhook_id": f"wh_{webhook_id}",
        "scan_job_id": f"job_{webhook_id}",
        "message": f"Webhook from {platform} received for {event} event"
    }
