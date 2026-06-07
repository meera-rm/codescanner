from fastapi import APIRouter, HTTPException, Request
from api.models.requests import ScanRequest
from api.models.responses import ScanResponse, JobResponse
from api.services.scanner_service import ScannerService

router = APIRouter(prefix="/api/v1/scan", tags=["scanning"])
scanner_service = ScannerService()


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
