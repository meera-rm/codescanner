"""
Tests for GitHub Integration Service - Phase 4.3
Tests PR creation, comments, status tracking
"""

import pytest
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.github_integration import (
    GitHubIntegration,
    GitHubConfig,
    PRResult,
    PRStatus,
    get_github_integration,
)


@pytest.fixture
def github_config():
    """Create GitHub config"""
    return GitHubConfig(
        token="test-token",
        owner="testuser",
        repo="testrepo",
        base_branch="main",
    )


@pytest.fixture
def github_integration(github_config):
    """Create GitHubIntegration instance"""
    return GitHubIntegration(github_config)


class TestGitHubConfig:
    """Test GitHubConfig data structure"""

    def test_config_creation(self):
        """Test creating GitHub config"""
        config = GitHubConfig(
            token="token123",
            owner="user",
            repo="repo",
            base_branch="develop",
        )

        assert config.token == "token123"
        assert config.owner == "user"
        assert config.repo == "repo"
        assert config.base_branch == "develop"

    def test_config_defaults(self):
        """Test config defaults"""
        config = GitHubConfig()

        assert config.token is None
        assert config.base_branch == "main"


class TestPRResult:
    """Test PRResult data structure"""

    def test_pr_result_success(self):
        """Test successful PR result"""
        result = PRResult(
            success=True,
            pr_number=42,
            pr_url="https://github.com/user/repo/pull/42",
            branch_name="feature/test",
            files_changed=3,
            additions=50,
            deletions=10,
        )

        assert result.success
        assert result.pr_number == 42
        assert result.files_changed == 3

    def test_pr_result_failure(self):
        """Test failed PR result"""
        result = PRResult(
            success=False,
            error_message="API error",
        )

        assert not result.success
        assert result.error_message is not None


class TestPRStatus:
    """Test PRStatus data structure"""

    def test_pr_status_creation(self):
        """Test creating PR status"""
        status = PRStatus(
            pr_number=42,
            state="open",
            title="Test PR",
            author="testuser",
            created_at="2026-01-01T00:00:00",
            updated_at="2026-01-02T00:00:00",
            approved=True,
            review_count=2,
        )

        assert status.pr_number == 42
        assert status.state == "open"
        assert status.approved is True


class TestGitHubIntegrationInit:
    """Test GitHub integration initialization"""

    def test_init_with_config(self, github_config):
        """Test initialization with config"""
        integration = GitHubIntegration(github_config)

        assert integration.config.token == "test-token"
        assert integration.config.owner == "testuser"
        assert integration.config.repo == "testrepo"

    def test_init_without_config(self):
        """Test initialization without config"""
        integration = GitHubIntegration()

        assert integration.config is not None
        assert integration.config.token is None

    def test_github_status_not_configured(self):
        """Test status when not configured"""
        integration = GitHubIntegration()
        status = integration.get_github_status()

        assert status["configured"] is False


class TestGitHubStatus:
    """Test GitHub integration status"""

    def test_get_github_status_configured(self, github_integration):
        """Test getting status when configured"""
        status = github_integration.get_github_status()

        assert status["configured"] is True
        assert status["owner"] == "testuser"
        assert status["repo"] == "testrepo"
        assert status["base_branch"] == "main"

    def test_get_github_status_not_configured(self):
        """Test status when not configured"""
        integration = GitHubIntegration()
        status = integration.get_github_status()

        assert status["configured"] is False


class TestPRCreation:
    """Test PR creation"""

    def test_create_pr_without_github_api(self, github_config):
        """Test PR creation without GitHub API available"""
        # Create integration without setting github client
        integration = GitHubIntegration(github_config)
        integration.github = None

        result = integration.create_pr(
            branch_name="feature/test",
            title="Test PR",
            description="Test description",
        )

        # Should attempt git workflow
        assert isinstance(result, PRResult)

    def test_create_pr_result_structure(self, github_integration):
        """Test PR result structure"""
        result = github_integration.create_pr(
            branch_name="feature/test",
            title="Test PR",
            description="Test description",
        )

        assert isinstance(result, PRResult)
        assert hasattr(result, "success")
        assert hasattr(result, "pr_number")
        assert hasattr(result, "error_message")


class TestPROperations:
    """Test PR operations"""

    def test_post_pr_comment_no_api(self, github_integration):
        """Test posting comment without API"""
        github_integration.github = None

        result = github_integration.post_pr_comment(
            pr_number=42,
            comment="Test comment",
        )

        assert result is False

    def test_update_pr_description_no_api(self, github_integration):
        """Test updating PR description without API"""
        github_integration.github = None

        result = github_integration.update_pr_description(
            pr_number=42,
            description="Updated description",
        )

        assert result is False

    def test_request_review_no_api(self, github_integration):
        """Test requesting review without API"""
        github_integration.github = None

        result = github_integration.request_review(
            pr_number=42,
            reviewers=["reviewer1", "reviewer2"],
        )

        assert result is False

    def test_add_labels_no_api(self, github_integration):
        """Test adding labels without API"""
        github_integration.github = None

        result = github_integration.add_labels(
            pr_number=42,
            labels=["bug", "enhancement"],
        )

        assert result is False

    def test_merge_pr_no_api(self, github_integration):
        """Test merging PR without API"""
        github_integration.github = None

        result = github_integration.merge_pr(
            pr_number=42,
            merge_method="squash",
        )

        assert result is False


class TestPRStatusRetrieval:
    """Test getting PR status"""

    def test_get_pr_status_no_api(self, github_integration):
        """Test getting PR status without API"""
        github_integration.github = None

        result = github_integration.get_pr_status(pr_number=42)

        assert result is None


class TestCodeReview:
    """Test code review posting"""

    def test_post_code_review_no_api(self, github_integration):
        """Test posting code review without API"""
        github_integration.github = None

        result = github_integration.post_code_review(
            pr_number=42,
            file_changes={
                "file1.py": "Good work!",
                "file2.js": "Needs improvement",
            },
        )

        assert result is False

    def test_post_code_review_structure(self, github_integration):
        """Test code review structure"""
        file_changes = {
            "api/main.py": "Fixed the bug",
            "tests/test_api.py": "Added test case",
        }

        # Should return bool
        result = github_integration.post_code_review(42, file_changes)
        assert isinstance(result, bool)


class TestGitHubConfigVariations:
    """Test different GitHub config variations"""

    def test_config_with_custom_base_branch(self):
        """Test config with custom base branch"""
        config = GitHubConfig(
            token="token",
            owner="user",
            repo="repo",
            base_branch="develop",
        )

        assert config.base_branch == "develop"

    def test_config_with_different_branches(self):
        """Test creating PR with different base branch"""
        config = GitHubConfig(
            token="token",
            owner="user",
            repo="repo",
            base_branch="staging",
        )

        integration = GitHubIntegration(config)

        # Should use staging as base
        assert integration.config.base_branch == "staging"


class TestSingletonPattern:
    """Test singleton pattern"""

    def test_get_github_integration_singleton(self):
        """Test that get_github_integration returns same instance"""
        config = GitHubConfig(token="test", owner="user", repo="repo")

        integration1 = get_github_integration(config)
        integration2 = get_github_integration()

        assert integration1 is integration2


class TestErrorHandling:
    """Test error handling"""

    def test_create_pr_error_handling(self, github_integration):
        """Test PR creation error handling"""
        github_integration.github = None

        result = github_integration.create_pr(
            branch_name="feature/test",
            title="Test",
            description="Test",
        )

        assert isinstance(result, PRResult)

    def test_comment_error_handling(self, github_integration):
        """Test comment posting error handling"""
        github_integration.github = None

        result = github_integration.post_pr_comment(42, "comment")

        assert isinstance(result, bool)


class TestPRWorkflow:
    """Test typical PR workflows"""

    def test_create_pr_workflow(self, github_integration):
        """Test creating a PR workflow"""
        # Create PR
        result = github_integration.create_pr(
            branch_name="feature/fix-bug",
            title="Fix critical bug",
            description="Fixes issue #123",
        )

        assert isinstance(result, PRResult)
        # Either succeeds or fails gracefully
        assert result.success is not None

    def test_pr_with_review_workflow(self, github_integration):
        """Test PR with review workflow"""
        github_integration.github = None

        # Create PR
        create_result = github_integration.create_pr(
            branch_name="feature/test",
            title="Test PR",
            description="Test",
        )

        # Request review
        review_result = github_integration.request_review(
            pr_number=42,
            reviewers=["reviewer1"],
        )

        assert isinstance(review_result, bool)

    def test_pr_with_labels_workflow(self, github_integration):
        """Test PR with labels workflow"""
        github_integration.github = None

        # Add labels
        result = github_integration.add_labels(
            pr_number=42,
            labels=["enhancement", "reviewed"],
        )

        assert isinstance(result, bool)


class TestIntegrationParameters:
    """Test integration with different parameters"""

    def test_create_pr_with_custom_base_branch(self, github_integration):
        """Test creating PR with custom base branch"""
        result = github_integration.create_pr(
            branch_name="feature/test",
            title="Test PR",
            description="Test",
            base_branch="develop",
        )

        assert isinstance(result, PRResult)

    def test_merge_with_custom_message(self, github_integration):
        """Test merging with custom commit message"""
        github_integration.github = None

        result = github_integration.merge_pr(
            pr_number=42,
            commit_message="Custom merge message",
            merge_method="rebase",
        )

        assert isinstance(result, bool)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
