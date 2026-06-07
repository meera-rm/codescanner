from fastapi import APIRouter, HTTPException, BackgroundTasks, Request
from datetime import datetime
from pathlib import Path
import uuid
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "scanner"))

try:
    from creative_suite import CreativeSuiteOrchestrator
except ImportError:
    CreativeSuiteOrchestrator = None
from api.models.requests import CreativeSuiteRequest
from api.models.responses import JobResponse, CreativeSuiteResponse

router = APIRouter(prefix="/api/v1/creative-suite", tags=["creative-suite"])

jobs = {}
orchestrator = CreativeSuiteOrchestrator() if CreativeSuiteOrchestrator else None


@router.post("/analyze", response_model=JobResponse)
async def creative_suite_analyze(request: CreativeSuiteRequest, background_tasks: BackgroundTasks, req: Request):
    key_id = getattr(req.state, "key_id", None)

    path = Path(request.directory_path)
    if not path.exists():
        raise HTTPException(status_code=400, detail=f"Path does not exist: {request.directory_path}")

    job_id = f"creative_{uuid.uuid4().hex[:8]}"
    jobs[job_id] = {
        "status": "processing",
        "progress": 0,
        "created_at": datetime.utcnow().isoformat(),
        "path": str(path),
        "message": "Starting Creative Suite analysis...",
        "result": None,
    }

    background_tasks.add_task(
        _run_creative_suite_analysis,
        job_id=job_id,
        path=str(path)
    )

    return {
        "job_id": job_id,
        "status": "processing",
        "message": "Creative Suite analysis queued. Check /api/v1/status/{job_id}"
    }


@router.get("/{job_id}", response_model=CreativeSuiteResponse)
async def get_creative_suite_result(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=202, detail=f"Job still processing: {job['message']}")

    result = job.get("result")
    if result:
        return {
            "job_id": result.job_id,
            "status": result.status,
            "personality": result.personality,
            "letter": result.letter,
            "caqi": result.caqi,
            "html_files": result.html_files,
            "markdown_report": result.markdown_report,
        }
    raise HTTPException(status_code=500, detail="No result available")


@router.get("/{job_id}/personality")
async def get_personality(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=202, detail=f"Job still processing: {job['message']}")

    result = job.get("result")
    if result:
        return result.personality
    raise HTTPException(status_code=500, detail="No result available")


@router.get("/{job_id}/letter")
async def get_letter(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=202, detail=f"Job still processing: {job['message']}")

    result = job.get("result")
    if result:
        return result.letter
    raise HTTPException(status_code=500, detail="No result available")


@router.get("/{job_id}/caqi")
async def get_caqi(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail=f"Job not found: {job_id}")

    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=202, detail=f"Job still processing: {job['message']}")

    result = job.get("result")
    if result:
        return result.caqi
    raise HTTPException(status_code=500, detail="No result available")


async def _run_creative_suite_analysis(job_id: str, path: str):
    try:
        if not orchestrator:
            raise Exception("Creative Suite orchestrator not available")

        jobs[job_id]["message"] = "Analyzing code structure..."
        jobs[job_id]["progress"] = 25

        result = orchestrator.analyze(path, job_id)

        jobs[job_id]["result"] = result
        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["message"] = "Analysis complete"
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"
        jobs[job_id]["error"] = str(e)
