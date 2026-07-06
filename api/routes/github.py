"""GitHub integration routes for OAuth and webhooks."""
from fastapi import APIRouter, Request, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.db.models import GitHubInstallation, GitHubRepository, User
from api.services.github_service import GitHubService
import uuid
from datetime import datetime

router = APIRouter(prefix="/api/v1/github", tags=["github"])

github_service = GitHubService()


@router.get("/authorize")
async def authorize_github(code: str = Query(...), state: str = Query(...)):
    """OAuth callback endpoint."""
    try:
        # Exchange code for token
        token_data = github_service.exchange_code_for_token(code)
        if not token_data:
            raise HTTPException(status_code=400, detail="Failed to exchange code")

        access_token = token_data["access_token"]

        # Get user info
        user_info = github_service.get_user(access_token)
        if not user_info:
            raise HTTPException(status_code=400, detail="Failed to get user info")

        return {
            "status": "authorized",
            "user": {
                "id": user_info.get("id"),
                "login": user_info.get("login"),
                "name": user_info.get("name"),
                "avatar": user_info.get("avatar_url"),
            },
            "access_token": access_token,
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/installations")
async def save_installation(
    request: Request,
    installation_id: int,
    user_id: str,
    db: Session = Depends(get_db),
):
    """Save GitHub App installation."""
    try:
        # Get installation access token
        token = github_service.get_installation_access_token(installation_id)
        if not token:
            raise HTTPException(status_code=400, detail="Failed to get installation token")

        # Encrypt token
        encrypted_token = github_service.encrypt_token(token)

        # Create installation record
        install = GitHubInstallation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            installation_id=installation_id,
            token=encrypted_token,
            is_active=True,
        )

        db.add(install)
        db.commit()

        return {
            "status": "installed",
            "installation_id": installation_id,
            "message": "GitHub App installed successfully",
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/installations/{user_id}")
async def get_installations(user_id: str, db: Session = Depends(get_db)):
    """Get GitHub installations for user."""
    try:
        installations = (
            db.query(GitHubInstallation).filter(
                GitHubInstallation.user_id == user_id
            ).all()
        )

        return {
            "installations": [
                {
                    "id": inst.id,
                    "installation_id": inst.installation_id,
                    "is_active": inst.is_active,
                    "repositories": len(inst.repositories),
                    "created_at": inst.created_at.isoformat(),
                }
                for inst in installations
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/repositories/{installation_id}")
async def get_repositories(
    installation_id: int, access_token: str = Query(...)
):
    """Get repositories from GitHub installation."""
    try:
        repos = github_service.get_user_repos(access_token)
        if not repos:
            raise HTTPException(status_code=400, detail="Failed to get repositories")

        return {
            "repositories": [
                {
                    "id": repo["id"],
                    "name": repo["name"],
                    "full_name": repo["full_name"],
                    "url": repo["html_url"],
                    "description": repo.get("description", ""),
                    "language": repo.get("language", ""),
                    "is_private": repo["private"],
                }
                for repo in repos
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/repositories")
async def add_repository(
    installation_id: str,
    repo_id: int,
    repo_name: str,
    fail_on_critical: bool = True,
    fail_on_error: bool = False,
    db: Session = Depends(get_db),
):
    """Add GitHub repository to CodePulse."""
    try:
        # Check if installation exists
        install = (
            db.query(GitHubInstallation)
            .filter(GitHubInstallation.id == installation_id)
            .first()
        )
        if not install:
            raise HTTPException(status_code=404, detail="Installation not found")

        # Create repository record
        repo = GitHubRepository(
            id=str(uuid.uuid4()),
            installation_id=installation_id,
            repo_name=repo_name,
            repo_id=repo_id,
            fail_on_critical=fail_on_critical,
            fail_on_error=fail_on_error,
            enabled=True,
        )

        db.add(repo)
        db.commit()

        return {
            "status": "added",
            "repository": {
                "id": repo.id,
                "name": repo.repo_name,
                "enabled": repo.enabled,
            },
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/repositories/{repo_id}")
async def get_repository(repo_id: str, db: Session = Depends(get_db)):
    """Get repository configuration."""
    try:
        repo = db.query(GitHubRepository).filter(
            GitHubRepository.id == repo_id
        ).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

        return {
            "id": repo.id,
            "name": repo.repo_name,
            "repo_id": repo.repo_id,
            "enabled": repo.enabled,
            "fail_on_critical": repo.fail_on_critical,
            "fail_on_error": repo.fail_on_error,
            "pr_scans": len(repo.pr_scans),
            "created_at": repo.created_at.isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/repositories/{repo_id}")
async def update_repository(
    repo_id: str,
    enabled: bool = None,
    fail_on_critical: bool = None,
    fail_on_error: bool = None,
    db: Session = Depends(get_db),
):
    """Update repository configuration."""
    try:
        repo = db.query(GitHubRepository).filter(
            GitHubRepository.id == repo_id
        ).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")

        if enabled is not None:
            repo.enabled = enabled
        if fail_on_critical is not None:
            repo.fail_on_critical = fail_on_critical
        if fail_on_error is not None:
            repo.fail_on_error = fail_on_error

        db.commit()

        return {
            "status": "updated",
            "repository": {
                "id": repo.id,
                "name": repo.repo_name,
                "enabled": repo.enabled,
            },
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def handle_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle GitHub webhook events."""
    try:
        # Get raw body for signature verification
        body = await request.body()
        signature = request.headers.get("X-Hub-Signature-256", "")

        # Verify signature
        if not github_service.verify_webhook_signature(body, signature):
            raise HTTPException(status_code=401, detail="Invalid signature")

        payload = await request.json()
        event = request.headers.get("X-GitHub-Event")

        # Handle PR events
        if event == "pull_request":
            action = payload.get("action")
            if action in ["opened", "synchronize"]:
                pr_data = payload.get("pull_request", {})
                repo_data = payload.get("repository", {})

                return {
                    "status": "received",
                    "event": event,
                    "action": action,
                    "message": "PR scan will be triggered",
                    "pr": {
                        "number": pr_data.get("number"),
                        "repository": repo_data.get("full_name"),
                    },
                }

        return {"status": "acknowledged", "event": event}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
