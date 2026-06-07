from fastapi import APIRouter, Request, HTTPException
from api.services.architecture_service import ArchitectureAnalyzer
from api.services.git_analyzer import GitAnalyzer
from api.services.refactoring_service import RefactoringService

router = APIRouter(prefix="/api/v1/analysis", tags=["analysis"])


@router.post("/architecture")
async def analyze_architecture(req: Request, directory_path: str):
    """Analyze codebase architecture."""
    key_id = getattr(req.state, "key_id", None)

    try:
        analyzer = ArchitectureAnalyzer(directory_path)
        result = analyzer.analyze()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/git-history")
async def analyze_git_history(req: Request, directory_path: str):
    """Analyze git history and risk."""
    key_id = getattr(req.state, "key_id", None)

    try:
        analyzer = GitAnalyzer(directory_path)
        result = analyzer.analyze()
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/refactor-suggestions")
async def generate_refactor_suggestions(req: Request, issue: dict):
    """Generate refactoring suggestions for an issue."""
    key_id = getattr(req.state, "key_id", None)

    try:
        service = RefactoringService()
        result = service.generate_fix(issue)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/validate-fix")
async def validate_refactor_fix(req: Request, original_code: str, fixed_code: str):
    """Validate a refactor fix."""
    key_id = getattr(req.state, "key_id", None)

    try:
        service = RefactoringService()
        result = service.validate_fix(original_code, fixed_code)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
