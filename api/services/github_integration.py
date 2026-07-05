"""
GitHub Integration - Phase 6.2.1
Integrates CodePulse AI with GitHub for PR scanning and analysis
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time


class GitHubEventType(str, Enum):
    """GitHub webhook event types"""
    PULL_REQUEST = "pull_request"
    PUSH = "push"
    COMMIT_COMMENT = "commit_comment"
    WORKFLOW_RUN = "workflow_run"


class PRCheckStatus(str, Enum):
    """Pull request check status"""
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class GitHubPullRequest:
    """GitHub Pull Request metadata"""
    pr_number: int
    repo_owner: str
    repo_name: str
    title: str
    description: str
    author: str
    head_sha: str
    base_sha: str
    files_changed: int
    additions: int
    deletions: int
    url: str
    created_at: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pr_number": self.pr_number,
            "repo": f"{self.repo_owner}/{self.repo_name}",
            "title": self.title,
            "author": self.author,
            "files_changed": self.files_changed,
            "additions": self.additions,
            "deletions": self.deletions,
            "url": self.url
        }


@dataclass
class GitHubCheckRun:
    """GitHub Check Run for PR analysis"""
    check_run_id: str
    pr_number: int
    repo_owner: str
    repo_name: str
    status: PRCheckStatus
    title: str
    summary: str
    details_url: str
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    annotations: List[Dict[str, Any]] = field(default_factory=list)
    conclusion: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "check_run_id": self.check_run_id,
            "pr_number": self.pr_number,
            "status": self.status.value,
            "title": self.title,
            "conclusion": self.conclusion,
            "annotations_count": len(self.annotations)
        }


class GitHubIntegration:
    """Integrates CodePulse AI with GitHub"""

    def __init__(self, access_token: Optional[str] = None):
        self.access_token = access_token
        self.pull_requests: Dict[str, GitHubPullRequest] = {}
        self.check_runs: Dict[str, GitHubCheckRun] = {}
        self.webhook_logs: List[Dict[str, Any]] = []

    def parse_webhook_event(
        self,
        event_type: str,
        payload: Dict[str, Any]
    ) -> Optional[GitHubPullRequest]:
        """Parse GitHub webhook event"""
        if event_type == GitHubEventType.PULL_REQUEST.value:
            return self._parse_pr_event(payload)
        elif event_type == GitHubEventType.PUSH.value:
            return self._parse_push_event(payload)
        return None

    def _parse_pr_event(self, payload: Dict[str, Any]) -> Optional[GitHubPullRequest]:
        """Parse pull request event"""
        pr_data = payload.get("pull_request")
        if not pr_data:
            return None

        repo_data = payload.get("repository", {})
        pr = GitHubPullRequest(
            pr_number=pr_data.get("number"),
            repo_owner=repo_data.get("owner", {}).get("login", "unknown"),
            repo_name=repo_data.get("name", "unknown"),
            title=pr_data.get("title", ""),
            description=pr_data.get("body", ""),
            author=pr_data.get("user", {}).get("login", "unknown"),
            head_sha=pr_data.get("head", {}).get("sha", ""),
            base_sha=pr_data.get("base", {}).get("sha", ""),
            files_changed=pr_data.get("changed_files", 0),
            additions=pr_data.get("additions", 0),
            deletions=pr_data.get("deletions", 0),
            url=pr_data.get("html_url", "")
        )

        pr_key = f"{repo_data.get('owner', {}).get('login', 'unknown')}/{repo_data.get('name', 'unknown')}#{pr_data.get('number')}"
        self.pull_requests[pr_key] = pr
        return pr

    def _parse_push_event(self, payload: Dict[str, Any]) -> Optional[GitHubPullRequest]:
        """Parse push event"""
        commits = payload.get("commits", [])
        repo_data = payload.get("repository", {})
        
        if not commits:
            return None

        pr = GitHubPullRequest(
            pr_number=0,
            repo_owner=repo_data.get("owner", {}).get("login", "unknown"),
            repo_name=repo_data.get("name", "unknown"),
            title=f"Push to {payload.get('ref', '')}",
            description=f"{len(commits)} commits",
            author=commits[0].get("author", {}).get("name", "unknown"),
            head_sha=payload.get("after", ""),
            base_sha=payload.get("before", ""),
            files_changed=sum(len(c.get("modified", [])) for c in commits),
            additions=0,
            deletions=0,
            url=repo_data.get("html_url", ""),
            metadata={"is_push": True, "commits": len(commits)}
        )
        return pr

    def create_check_run(
        self,
        pr_number: int,
        repo_owner: str,
        repo_name: str,
        title: str,
        summary: str,
        annotations: List[Dict[str, Any]]
    ) -> GitHubCheckRun:
        """Create a check run for PR analysis"""
        import secrets

        check_run = GitHubCheckRun(
            check_run_id=f"check_{secrets.token_hex(8)}",
            pr_number=pr_number,
            repo_owner=repo_owner,
            repo_name=repo_name,
            status=PRCheckStatus.COMPLETED,
            title=title,
            summary=summary,
            details_url=f"https://github.com/{repo_owner}/{repo_name}/pull/{pr_number}/checks",
            annotations=annotations,
            conclusion="success" if len(annotations) == 0 else "neutral"
        )
        self.check_runs[check_run.check_run_id] = check_run
        return check_run

    def generate_pr_comment(
        self,
        quality_score: float,
        findings: List[Dict[str, Any]],
        agent_recommendations: List[str]
    ) -> str:
        """Generate GitHub PR comment with analysis"""
        comment = "## 🤖 CodePulse AI Analysis\n\n"
        score_emoji = "🟢" if quality_score >= 80 else "🟡" if quality_score >= 60 else "🔴"
        comment += f"{score_emoji} **Code Quality Score**: {quality_score:.0f}/100\n\n"

        if findings:
            comment += "### 🔍 Issues Found\n\n"
            for finding in findings[:10]:
                severity = finding.get("severity", "INFO")
                emoji = "🔴" if severity == "CRITICAL" else "🟠" if severity == "HIGH" else "🟡"
                comment += f"{emoji} **{finding.get('type')}** (Line {finding.get('line')})\n"
                comment += f"> {finding.get('message')}\n\n"
        else:
            comment += "✅ **No issues found!**\n\n"

        if agent_recommendations:
            comment += "### 💡 Agent Recommendations\n\n"
            for rec in agent_recommendations[:5]:
                comment += f"- {rec}\n"
            comment += "\n"

        return comment

    def log_webhook(
        self,
        event_type: str,
        repo_owner: str,
        repo_name: str,
        status: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log webhook event"""
        log_entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "repo": f"{repo_owner}/{repo_name}",
            "status": status,
            "details": details or {}
        }
        self.webhook_logs.append(log_entry)
        if len(self.webhook_logs) > 100:
            self.webhook_logs = self.webhook_logs[-100:]

    def get_integration_status(self) -> Dict[str, Any]:
        """Get integration status"""
        return {
            "authenticated": bool(self.access_token),
            "pull_requests_tracked": len(self.pull_requests),
            "check_runs_created": len(self.check_runs),
            "webhook_events_processed": len(self.webhook_logs)
        }


    def get_webhook_logs(self, limit: int = 20):
        """Get recent webhook logs"""
        return self.webhook_logs[-limit:]

_global_github_integration = GitHubIntegration()

def get_github_integration() -> GitHubIntegration:
    """Get global GitHub integration instance"""
    return _global_github_integration

    def get_webhook_logs(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent webhook logs"""
        return self.webhook_logs[-limit:]
