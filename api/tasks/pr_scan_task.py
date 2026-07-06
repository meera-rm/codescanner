"""PR scan task for background job queue."""
import os
import tempfile
import subprocess
from typing import Dict, Any
from sqlalchemy.orm import Session

from api.services.pr_scan_service import PRScanService
from api.services.github_service import GitHubService
from api.db.database import SessionLocal
from api.db.models import PRScan, GitHubRepository
import uuid
from datetime import datetime


async def scan_pr_task(job: Any) -> Dict[str, Any]:
    """
    Background task to scan a GitHub PR.

    Job data should contain:
    {
        'repo_name': 'owner/repo',
        'pr_number': 123,
        'access_token': 'github_token',
        'base_branch': 'main',
        'head_branch': 'feature-branch',
        'commit_sha': 'abc123',
        'installation_id': 123
    }
    """
    data = job.data
    repo_name = data['repo_name']
    pr_number = data['pr_number']
    access_token = data['access_token']
    base_branch = data.get('base_branch', 'main')
    head_branch = data.get('head_branch', 'HEAD')
    commit_sha = data.get('commit_sha', '')

    db = SessionLocal()
    github_service = GitHubService()

    try:
        # Update progress
        job.progress = 20

        # Get repository from database
        repo = (
            db.query(GitHubRepository)
            .filter(GitHubRepository.repo_name == repo_name)
            .first()
        )

        if not repo:
            raise Exception(f"Repository {repo_name} not found")

        if not repo.enabled:
            raise Exception(f"Repository {repo_name} scanning is disabled")

        job.progress = 30

        # Clone repo to temp directory
        with tempfile.TemporaryDirectory() as temp_dir:
            clone_url = f"https://{access_token}@github.com/{repo_name}.git"

            try:
                subprocess.run(
                    ["git", "clone", "--depth", "1", clone_url, temp_dir],
                    capture_output=True,
                    timeout=60
                )
            except Exception as e:
                raise Exception(f"Failed to clone repo: {str(e)}")

            job.progress = 50

            # Scan the PR
            scan_service = PRScanService(temp_dir, repo.id)
            scan_result = scan_service.scan_pr(
                base_branch=base_branch,
                head_branch=head_branch,
                pr_number=pr_number,
                repo_name=repo_name,
                db=db
            )

            if scan_result['status'] == 'error':
                raise Exception(scan_result.get('error', 'Unknown error'))

            job.progress = 70

            # Generate review comment
            comment = scan_service.generate_review_comment(
                scan_result['findings'],
                pr_number
            )

            # Post comment to PR
            if comment:
                github_service.post_pr_comment(
                    access_token,
                    repo_name,
                    pr_number,
                    comment
                )

            job.progress = 85

            # Determine if PR should be blocked
            should_block = scan_service.should_block_pr(
                scan_result['findings'],
                repo.fail_on_critical,
                repo.fail_on_error
            )

            # Set PR status
            status = "failure" if should_block else "success"
            description = f"CodePulse scan: {status.upper()}"

            if scan_result['summary']['critical'] > 0:
                description += f" - {scan_result['summary']['critical']} critical"

            github_service.set_pr_status(
                access_token,
                repo_name,
                commit_sha,
                status,
                context="codepulse/scan",
                description=description,
                target_url=f"https://codepulse.dev/pr/{pr_number}"
            )

            job.progress = 95

            # Save PR scan to database
            pr_scan = PRScan(
                id=str(uuid.uuid4()),
                repository_id=repo.id,
                pr_number=pr_number,
                branch=head_branch,
                commit_sha=commit_sha,
                findings=scan_result['findings'],
                status='completed',
                critical_count=scan_result['summary'].get('critical', 0),
                error_count=scan_result['summary'].get('error', 0),
                warning_count=scan_result['summary'].get('warning', 0),
                completed_at=datetime.utcnow()
            )

            db.add(pr_scan)
            db.commit()

            job.progress = 100

            return {
                'status': 'completed',
                'pr_number': pr_number,
                'repository': repo_name,
                'findings_count': len(scan_result['findings']),
                'critical': scan_result['summary'].get('critical', 0),
                'error': scan_result['summary'].get('error', 0),
                'warning': scan_result['summary'].get('warning', 0),
                'should_block': should_block,
                'comment_posted': True
            }

    except Exception as e:
        print(f"Error in PR scan task: {e}")
        raise

    finally:
        db.close()
