"""
Tests for GitHub Integration - Phase 6.2.1
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.github_integration import (
    GitHubIntegration,
    GitHubEventType,
    PRCheckStatus
)


class TestGitHubIntegration:
    """Test GitHub integration"""

    def test_parse_pr_event(self):
        """Test parsing PR event"""
        integration = GitHubIntegration()

        payload = {
            "pull_request": {
                "number": 123,
                "title": "Add feature",
                "body": "This adds a new feature",
                "user": {"login": "testuser"},
                "head": {"sha": "abc123"},
                "base": {"sha": "def456"},
                "changed_files": 3,
                "additions": 50,
                "deletions": 10,
                "html_url": "https://github.com/test/repo/pull/123"
            },
            "repository": {
                "name": "repo",
                "owner": {"login": "testuser"}
            }
        }

        pr = integration.parse_webhook_event("pull_request", payload)

        assert pr is not None
        assert pr.pr_number == 123
        assert pr.title == "Add feature"
        assert pr.additions == 50

    def test_parse_push_event(self):
        """Test parsing push event"""
        integration = GitHubIntegration()

        payload = {
            "ref": "refs/heads/main",
            "before": "abc123",
            "after": "def456",
            "commits": [
                {
                    "author": {"name": "testuser"},
                    "modified": ["file1.py", "file2.py"]
                }
            ],
            "repository": {
                "name": "repo",
                "owner": {"login": "testuser"},
                "html_url": "https://github.com/test/repo"
            }
        }

        pr = integration.parse_webhook_event("push", payload)

        assert pr is not None
        assert pr.pr_number == 0
        assert pr.metadata["is_push"] is True

    def test_create_check_run(self):
        """Test creating check run"""
        integration = GitHubIntegration()

        check_run = integration.create_check_run(
            pr_number=123,
            repo_owner="testuser",
            repo_name="repo",
            title="Code Analysis",
            summary="All checks passed",
            annotations=[]
        )

        assert check_run.check_run_id.startswith("check_")
        assert check_run.pr_number == 123
        assert check_run.conclusion == "success"

    def test_generate_pr_comment(self):
        """Test generating PR comment"""
        integration = GitHubIntegration()

        comment = integration.generate_pr_comment(
            quality_score=85,
            findings=[
                {
                    "type": "UnnecessaryImport",
                    "line": 42,
                    "severity": "HIGH",
                    "message": "Unused import"
                }
            ],
            agent_recommendations=["Use list comprehension", "Add type hints"]
        )

        assert "85" in comment
        assert "UnnecessaryImport" in comment
        assert "list comprehension" in comment

    def test_webhook_logging(self):
        """Test webhook logging"""
        integration = GitHubIntegration()

        integration.log_webhook(
            "pull_request",
            "testuser",
            "repo",
            "processed",
            {"findings": 2}
        )

        logs = integration.get_webhook_logs()
        assert len(logs) == 1
        assert logs[0]["status"] == "processed"

    def test_integration_status(self):
        """Test integration status"""
        integration = GitHubIntegration(access_token="test_token")

        status = integration.get_integration_status()

        assert status["authenticated"] is True
        assert status["pull_requests_tracked"] == 0
        assert status["check_runs_created"] == 0

    def test_multiple_prs(self):
        """Test tracking multiple PRs"""
        integration = GitHubIntegration()

        for i in range(3):
            payload = {
                "pull_request": {
                    "number": 100 + i,
                    "title": f"PR {i}",
                    "body": f"Description {i}",
                    "user": {"login": "user"},
                    "head": {"sha": f"sha{i}"},
                    "base": {"sha": "base"},
                    "changed_files": 1,
                    "additions": 10,
                    "deletions": 0,
                    "html_url": f"http://github.com/test/repo/pull/{100+i}"
                },
                "repository": {
                    "name": "repo",
                    "owner": {"login": "user"}
                }
            }
            integration.parse_webhook_event("pull_request", payload)

        assert len(integration.pull_requests) == 3

    def test_check_run_with_annotations(self):
        """Test check run with annotations"""
        integration = GitHubIntegration()

        annotations = [
            {"line": 10, "message": "Issue 1"},
            {"line": 20, "message": "Issue 2"}
        ]

        check_run = integration.create_check_run(
            pr_number=123,
            repo_owner="testuser",
            repo_name="repo",
            title="Analysis",
            summary="Found issues",
            annotations=annotations
        )

        assert len(check_run.annotations) == 2
        assert check_run.conclusion == "neutral"

    def test_pr_to_dict(self):
        """Test PR serialization"""
        integration = GitHubIntegration()

        payload = {
            "pull_request": {
                "number": 123,
                "title": "Test",
                "body": "",
                "user": {"login": "user"},
                "head": {"sha": "abc"},
                "base": {"sha": "def"},
                "changed_files": 1,
                "additions": 5,
                "deletions": 0,
                "html_url": "http://github.com/test/repo/pull/123"
            },
            "repository": {
                "name": "repo",
                "owner": {"login": "user"}
            }
        }

        pr = integration.parse_webhook_event("pull_request", payload)
        pr_dict = pr.to_dict()

        assert pr_dict["pr_number"] == 123
        assert "user/repo" in pr_dict["repo"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
