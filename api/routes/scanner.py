from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from api.models.requests import ScanRequest
from api.models.responses import ScanResponse, JobResponse
from api.services.scanner_service import ScannerService
from pathlib import Path

router = APIRouter(prefix="/api/v1/scan", tags=["scanning"])
scanner_service = ScannerService()


class RefactorRequest(BaseModel):
    file_path: str
    refactored_code: str
    function_name: str


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
