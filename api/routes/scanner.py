from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional
from api.models.requests import ScanRequest
from api.models.responses import ScanResponse, JobResponse
from api.services.scanner_service import ScannerService
from api.services.refactoring_service import RefactoringService
from api.services.remote_scanner_service import RemoteScannerService
from pathlib import Path
import tempfile
import shutil

router = APIRouter(prefix="/api/v1/scan", tags=["scanning"])
scanner_service = ScannerService()
refactoring_service = RefactoringService()
remote_scanner_service = RemoteScannerService()


class RefactorRequest(BaseModel):
    file_path: str
    refactored_code: str
    function_name: str


class BatchRefactorRequest(BaseModel):
    functions: List[dict]
    category: Optional[str] = None


class BatchRefactorApplyRequest(BaseModel):
    batch_id: str
    function_results: List[dict]


class SnippetAnalysisRequest(BaseModel):
    code: str
    language: str = 'python'


class GitHubScanRequest(BaseModel):
    github_url: str
    branch: str = 'main'
    language: str = 'python'


class GitHubInfoRequest(BaseModel):
    github_url: str
    branch: str = 'main'


@router.get("/search-paths/{query}")
async def search_paths(query: str):
    """Search for directories by name pattern (up to 10 levels deep)."""
    from pathlib import Path

    results = []
    documents = Path.home() / 'Documents'

    try:
        # Search in Documents directory (recursively, up to any depth)
        for path in documents.rglob('*'):
            if path.is_dir() and query.lower() in path.name.lower():
                results.append({
                    'name': path.name,
                    'path': str(path),
                    'relative': str(path.relative_to(documents))
                })
                if len(results) >= 20:  # Increased limit to 20 results
                    break
    except Exception as e:
        pass

    return {'query': query, 'results': results}


@router.post("/apply-refactor")
async def apply_refactor(request: RefactorRequest):
    """Apply refactored code and save to file."""
    if not request.file_path or not request.refactored_code:
        raise HTTPException(status_code=400, detail="Missing file_path or refactored_code")

    try:
        # Resolve the file path
        path = Path(request.file_path)
        if not path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")

        # Write refactored code to file
        with open(path, 'w', encoding='utf-8') as f:
            f.write(request.refactored_code)

        return {
            "status": "success",
            "message": f"Applied refactoring to {path.name}",
            "file_path": str(path),
            "function_name": request.function_name,
            "bytes_written": len(request.refactored_code)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply refactoring: {str(e)}")


@router.post("/sync")
async def scan_sync(request: ScanRequest, req: Request):
    from pathlib import Path

    key_id = getattr(req.state, "key_id", None)

    # Validate directory exists if provided
    if request.directory_path:
        path = Path(request.directory_path)
        # Check exact path
        if not path.exists():
            # Check common locations
            common_locations = [
                Path.home() / 'Documents' / request.directory_path,
                Path.home() / 'Documents' / 'assignments' / 'pursuit' / request.directory_path,
                Path.home() / 'Documents' / 'codescanner' / request.directory_path,
                Path.cwd() / request.directory_path,
            ]
            found = False
            for candidate in common_locations:
                if candidate.exists():
                    found = True
                    break
            if not found:
                raise HTTPException(
                    status_code=400,
                    detail=f"Path not found: {request.directory_path}. Try using the full absolute path (e.g., /Users/meera/Documents/codescanner)"
                )

    result = scanner_service.scan(
        code=request.code,
        directory_path=request.directory_path,
        language=request.language,
        options=request.options,
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])

    # Debug: Log findings count
    findings_count = len(result.get("findings", []))
    print(f"[DEBUG] Scan result: status={result['status']}, findings={findings_count}, language={request.language}", file=__import__('sys').stderr)

    return result


@router.post("/async", response_model=JobResponse)
async def scan_async(request: ScanRequest, req: Request):
    key_id = getattr(req.state, "key_id", None)

    result = scanner_service.scan(
        code=request.code,
        directory_path=request.directory_path,
        language=request.language,
        options=request.options,
    )

    return {"job_id": result["job_id"], "status": "processing"}


@router.get("/{job_id}", response_model=ScanResponse)
async def get_scan_result(job_id: str):
    result = scanner_service.get_scan_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Scan job not found")

    return result


@router.get("/{job_id}/findings")
async def get_scan_findings(job_id: str):
    result = scanner_service.get_scan_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Scan job not found")

    return {"job_id": job_id, "findings": result.get("findings", [])}


@router.get("/{job_id}/metrics")
async def get_scan_metrics(job_id: str):
    result = scanner_service.get_scan_result(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Scan job not found")

    return {"job_id": job_id, "metrics": result.get("metrics", {})}


@router.post("/batch-refactor")
async def batch_refactor(request: BatchRefactorRequest):
    """Start a batch refactoring job for multiple functions."""
    if not request.functions:
        raise HTTPException(status_code=400, detail="No functions provided")

    try:
        batch_job = refactoring_service.batch_refactor(request.functions, request.category)
        return {
            "batch_id": batch_job["batch_id"],
            "status": batch_job["status"],
            "total_functions": batch_job["total_functions"],
            "processed": batch_job["processed"],
            "results": batch_job["results"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch refactor failed: {str(e)}")


@router.get("/batch-refactor/{batch_id}/status")
async def get_batch_status(batch_id: str):
    """Get the status of a batch refactoring job."""
    batch_job = refactoring_service.get_batch_status(batch_id)
    if not batch_job:
        raise HTTPException(status_code=404, detail="Batch job not found")

    return {
        "batch_id": batch_id,
        "status": batch_job["status"],
        "category": batch_job.get("category"),
        "total_functions": batch_job["total_functions"],
        "processed": batch_job["processed"],
        "results": batch_job.get("results", []),
        "created_at": batch_job.get("created_at")
    }


@router.post("/batch-refactor/apply")
async def apply_batch_refactor(request: BatchRefactorApplyRequest):
    """Apply batch refactoring results to files."""
    try:
        applied_count = 0
        errors = []

        for result in request.function_results:
            if result.get("status") == "applied" and result.get("refactored_code"):
                file_path = result.get("file")
                refactored_code = result.get("refactored_code")

                try:
                    path = Path(file_path)
                    if not path.exists():
                        errors.append(f"File not found: {file_path}")
                        continue

                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(refactored_code)
                    applied_count += 1
                except Exception as e:
                    errors.append(f"Failed to apply {file_path}: {str(e)}")

        return {
            "batch_id": request.batch_id,
            "applied_count": applied_count,
            "total_requested": len(request.function_results),
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply batch refactoring: {str(e)}")


@router.post("/analyze-snippet")
async def analyze_snippet(request: SnippetAnalysisRequest):
    """Analyze a code snippet for real-time feedback (Phase 3.5)."""
    if not request.code or len(request.code.strip()) == 0:
        return {
            "code_length": 0,
            "quality_score": 100,
            "complexity": {"high": 0, "medium": 0, "low": 0},
            "security_issues": 0,
            "findings": []
        }

    try:
        result = scanner_service.scan(
            code=request.code,
            language=request.language,
            options={
                "security": True,
                "quality_score": True,
                "code_smells": True,
                "doc_coverage": False,
                "complexity": True,
            }
        )

        findings = result.get("findings", [])
        metrics = result.get("metrics", {})

        # Categorize findings by severity
        security_issues = len([f for f in findings if f.get("type", "").lower().find("security") >= 0])
        complexity_issues = [f for f in findings if "complexity" in f.get("type", "").lower()]

        complexity_breakdown = {
            "high": len([f for f in complexity_issues if f.get("severity") == "high"]),
            "medium": len([f for f in complexity_issues if f.get("severity") == "medium"]),
            "low": len([f for f in complexity_issues if f.get("severity") == "low"])
        }

        return {
            "code_length": len(request.code),
            "quality_score": metrics.get("quality_score", 100),
            "complexity": complexity_breakdown,
            "security_issues": security_issues,
            "total_issues": len(findings),
            "findings": [
                {
                    "line": f.get("line"),
                    "type": f.get("type"),
                    "message": f.get("message"),
                    "severity": f.get("severity")
                }
                for f in findings[:10]  # Limit to first 10
            ]
        }
    except Exception as e:
        return {
            "error": str(e),
            "code_length": len(request.code),
            "quality_score": 0,
            "complexity": {"high": 0, "medium": 0, "low": 0},
            "security_issues": 0,
            "findings": []
        }


# Phase 3.6: GitHub/ZIP Backend Integration

@router.post("/scan-github")
async def scan_github_repo(request: GitHubScanRequest):
    """Scan a GitHub repository (Phase 3.6)."""
    try:
        result = remote_scanner_service.scan_github_repo(
            github_url=request.github_url,
            branch=request.branch,
            language=request.language
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("error"))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"GitHub scan failed: {str(e)}")


@router.get("/github-info")
async def get_github_info(github_url: str, branch: str = "main"):
    """Get GitHub repository info without downloading (Phase 3.6)."""
    try:
        info = remote_scanner_service.get_github_repo_info(github_url, branch)

        if info.get("error"):
            raise HTTPException(status_code=400, detail=info.get("error"))

        return info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch repo info: {str(e)}")


@router.post("/scan-zip")
async def scan_zip_file(file: UploadFile = File(...), language: str = "python"):
    """Upload and scan a ZIP file (Phase 3.6)."""
    temp_zip_path = None

    try:
        # Validate file type
        if not file.filename.lower().endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only ZIP files are supported")

        # Save uploaded file to temp location
        temp_zip_path = None
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
            contents = await file.read()
            tmp.write(contents)
            temp_zip_path = tmp.name

        # Scan the ZIP
        result = remote_scanner_service.scan_zip_file(
            zip_file_path=temp_zip_path,
            language=language
        )

        if result.get("status") == "error":
            raise HTTPException(status_code=400, detail=result.get("error"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ZIP scan failed: {str(e)}")
    finally:
        # Cleanup temp ZIP file
        if temp_zip_path and Path(temp_zip_path).exists():
            try:
                Path(temp_zip_path).unlink()
            except Exception:
                pass


@router.delete("/cleanup/{job_id}")
async def cleanup_scan_temp_files(job_id: str):
    """Manually cleanup temporary files from a scan (Phase 3.6)."""
    try:
        # This would be called with the temp_path returned from scan results
        # For now, just return success - cleanup happens automatically
        return {"status": "success", "message": f"Cleanup request received for {job_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")
