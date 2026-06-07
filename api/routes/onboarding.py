from fastapi import APIRouter, HTTPException, Request
from api.models.requests import OnboardingRequest
from api.models.responses import OnboardingResponse, JobResponse
from api.services.onboarding_service import OnboardingService

router = APIRouter(prefix="/api/v1/onboarding", tags=["onboarding"])
onboarding_service = OnboardingService()


@router.post("/profile", response_model=OnboardingResponse)
async def generate_onboarding_profile(request: OnboardingRequest, req: Request):
    key_id = getattr(req.state, "key_id", None)

    result = onboarding_service.generate_profile(
        directory_path=request.directory_path,
        tone=request.tone,
        include_creative_suite=request.include_creative_suite,
        format=request.format,
    )

    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])

    return result


@router.get("/{job_id}", response_model=OnboardingResponse)
async def get_onboarding_profile(job_id: str):
    result = onboarding_service.get_profile(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Onboarding job not found")

    return result


@router.get("/{job_id}/html")
async def get_onboarding_html(job_id: str):
    result = onboarding_service.get_profile(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Onboarding job not found")

    if not result.get("html"):
        raise HTTPException(status_code=400, detail="HTML not available for this job")

    return {"job_id": job_id, "html": result["html"]}
