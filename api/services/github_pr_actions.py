"""
GitHub PR Actions Service (originally Phase 4.3)
Create PRs, post comments, track status
"""

import logging
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import subprocess

logger = logging.getLogger(__name__)


@dataclass
class GitHubConfig:
    """GitHub configuration"""
    token: Optional[str] = None
    owner: Optional[str] = None
    repo: Optional[str] = None
    base_branch: str = "main"


@dataclass
class PRResult:
    """Result of PR creation"""
    success: bool
    pr_number: Optional[int] = None
    pr_url: Optional[str] = None
    branch_name: Optional[str] = None
    error_message: Optional[str] = None
    files_changed: int = 0
    additions: int = 0
    deletions: int = 0


@dataclass
class PRStatus:
    """Status of a PR"""
    pr_number: int
    state: str  # "open", "closed", "merged"
    title: str
    author: str
    created_at: str
    updated_at: str
    merge_status: Optional[str] = None  # "behind", "dirty", "clean", "unstable"
    review_count: int = 0
    approved: bool = False


class GitHubPRActions:
    """Integrate with GitHub for PR creation and management"""

    def __init__(self, config: Optional[GitHubConfig] = None):
        self.config = config or GitHubConfig()
        self.github = None
        self._init_github_client()

    def _init_github_client(self):
        """Initialize GitHub client"""
        try:
            from github import Github

            if self.config.token:
                self.github = Github(self.config.token)
            else:
                logger.warning("GitHub token not provided, using unauthenticated client")
                self.github = Github()
        except ImportError:
            logger.warning("PyGithub not installed, using git commands instead")
            self.github = None

    def _is_github_available(self) -> bool:
        """Check if GitHub is configured and available"""
        return self.github is not None and self.config.token is not None

    def create_pr(
        self,
        branch_name: str,
        title: str,
        description: str,
        base_branch: Optional[str] = None,
    ) -> PRResult:
        """
        Create a GitHub PR.

        Args:
            branch_name: Feature branch name
            title: PR title
            description: PR description/body
            base_branch: Target branch (defaults to main)

        Returns:
            PRResult with PR details
        """
        try:
            base_branch = base_branch or self.config.base_branch

            if self.github and self._is_github_available():
                return self._create_pr_with_api(
                    branch_name, title, description, base_branch
                )
            else:
                logger.warning("GitHub API not available, using git workflow")
                return self._create_pr_with_git(
                    branch_name, title, description, base_branch
                )

        except Exception as e:
            logger.error(f"Error creating PR: {e}")
            return PRResult(
                success=False,
                error_message=str(e),
            )

    def _create_pr_with_api(
        self,
        branch_name: str,
        title: str,
        description: str,
        base_branch: str,
    ) -> PRResult:
        """Create PR using GitHub API"""
        try:
            repo = self.github.get_user(self.config.owner).get_repo(self.config.repo)

            # Create PR
            pr = repo.create_pull(
                title=title,
                body=description,
                head=branch_name,
                base=base_branch,
            )

            logger.info(f"Created PR #{pr.number} ({branch_name} → {base_branch})")

            return PRResult(
                success=True,
                pr_number=pr.number,
                pr_url=pr.html_url,
                branch_name=branch_name,
            )

        except Exception as e:
            logger.error(f"Error creating PR with API: {e}")
            return PRResult(
                success=False,
                error_message=str(e),
            )

    def _create_pr_with_git(
        self,
        branch_name: str,
        title: str,
        description: str,
        base_branch: str,
    ) -> PRResult:
        """Create PR using git workflow (when API unavailable)"""
        try:
            # Create and push branch
            result = subprocess.run(
                ["git", "checkout", "-b", branch_name],
                capture_output=True,
                timeout=10,
            )

            if result.returncode != 0:
                return PRResult(
                    success=False,
                    error_message="Failed to create branch",
                )

            # Push branch
            result = subprocess.run(
                ["git", "push", "-u", "origin", branch_name],
                capture_output=True,
                timeout=30,
            )

            if result.returncode != 0:
                return PRResult(
                    success=False,
                    error_message="Failed to push branch",
                )

            logger.info(f"Pushed branch {branch_name}")

            return PRResult(
                success=True,
                branch_name=branch_name,
            )

        except subprocess.TimeoutExpired:
            logger.error("Git operation timed out")
            return PRResult(
                success=False,
                error_message="Git operation timed out",
            )
        except Exception as e:
            logger.error(f"Error creating PR with git: {e}")
            return PRResult(
                success=False,
                error_message=str(e),
            )

    def post_pr_comment(
        self,
        pr_number: int,
        comment: str,
    ) -> bool:
        """
        Post a comment on a PR.

        Args:
            pr_number: PR number
            comment: Comment text

        Returns:
            True if successful
        """
        try:
            if not self._is_github_available():
                logger.warning("GitHub API not available, skipping comment")
                return False

            repo = self.github.get_user(self.config.owner).get_repo(self.config.repo)
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(comment)

            logger.info(f"Posted comment on PR #{pr_number}")
            return True

        except Exception as e:
            logger.error(f"Error posting comment: {e}")
            return False

    def get_pr_status(self, pr_number: int) -> Optional[PRStatus]:
        """
        Get PR status.

        Args:
            pr_number: PR number

        Returns:
            PRStatus or None if not found
        """
        try:
            if not self._is_github_available():
                logger.warning("GitHub API not available")
                return None

            repo = self.github.get_user(self.config.owner).get_repo(self.config.repo)
            pr = repo.get_pull(pr_number)

            # Get review count
            reviews = pr.get_reviews()
            review_count = reviews.totalCount

            # Check if approved
            approved = any(r.state == "APPROVED" for r in reviews)

            return PRStatus(
                pr_number=pr.number,
                state=pr.state,
                title=pr.title,
                author=pr.user.login,
                created_at=pr.created_at.isoformat(),
                updated_at=pr.updated_at.isoformat(),
                merge_status=pr.mergeable_state,
                review_count=review_count,
                approved=approved,
            )

        except Exception as e:
            logger.error(f"Error getting PR status: {e}")
            return None

    def update_pr_description(
        self,
        pr_number: int,
        description: str,
    ) -> bool:
        """
        Update PR description.

        Args:
            pr_number: PR number
            description: New description

        Returns:
            True if successful
        """
        try:
            if not self._is_github_available():
                logger.warning("GitHub API not available")
                return False

            repo = self.github.get_user(self.config.owner).get_repo(self.config.repo)
            pr = repo.get_pull(pr_number)
            pr.edit(body=description)

            logger.info(f"Updated description for PR #{pr_number}")
            return True

        except Exception as e:
            logger.error(f"Error updating PR description: {e}")
            return False

    def post_code_review(
        self,
        pr_number: int,
        file_changes: Dict[str, str],
    ) -> bool:
        """
        Post a code review with file-level comments.

        Args:
            pr_number: PR number
            file_changes: Dict of {file_path: comment}

        Returns:
            True if successful
        """
        try:
            if not self._is_github_available():
                logger.warning("GitHub API not available")
                return False

            repo = self.github.get_user(self.config.owner).get_repo(self.config.repo)
            pr = repo.get_pull(pr_number)

            # Post comment for each file
            for file_path, comment in file_changes.items():
                self.post_pr_comment(pr_number, f"**{file_path}**\n{comment}")

            logger.info(f"Posted code review on PR #{pr_number}")
            return True

        except Exception as e:
            logger.error(f"Error posting code review: {e}")
            return False

    def merge_pr(
        self,
        pr_number: int,
        commit_message: Optional[str] = None,
        merge_method: str = "squash",
    ) -> bool:
        """
        Merge a PR.

        Args:
            pr_number: PR number
            commit_message: Custom commit message
            merge_method: "squash", "rebase", or "merge"

        Returns:
            True if successful
        """
        try:
            if not self._is_github_available():
                logger.warning("GitHub API not available")
                return False

            repo = self.github.get_user(self.config.owner).get_repo(self.config.repo)
            pr = repo.get_pull(pr_number)

            if not pr.mergeable:
                logger.error(f"PR #{pr_number} is not mergeable")
                return False

            pr.merge(
                commit_message=commit_message or pr.title,
                merge_method=merge_method,
            )

            logger.info(f"Merged PR #{pr_number}")
            return True

        except Exception as e:
            logger.error(f"Error merging PR: {e}")
            return False

    def request_review(
        self,
        pr_number: int,
        reviewers: List[str],
    ) -> bool:
        """
        Request reviewers on a PR.

        Args:
            pr_number: PR number
            reviewers: List of GitHub usernames

        Returns:
            True if successful
        """
        try:
            if not self._is_github_available():
                logger.warning("GitHub API not available")
                return False

            repo = self.github.get_user(self.config.owner).get_repo(self.config.repo)
            pr = repo.get_pull(pr_number)
            pr.create_review_request(reviewers=reviewers)

            logger.info(f"Requested review from {reviewers} on PR #{pr_number}")
            return True

        except Exception as e:
            logger.error(f"Error requesting review: {e}")
            return False

    def add_labels(
        self,
        pr_number: int,
        labels: List[str],
    ) -> bool:
        """
        Add labels to a PR.

        Args:
            pr_number: PR number
            labels: List of label names

        Returns:
            True if successful
        """
        try:
            if not self._is_github_available():
                logger.warning("GitHub API not available")
                return False

            repo = self.github.get_user(self.config.owner).get_repo(self.config.repo)
            pr = repo.get_pull(pr_number)
            pr.add_to_labels(*labels)

            logger.info(f"Added labels {labels} to PR #{pr_number}")
            return True

        except Exception as e:
            logger.error(f"Error adding labels: {e}")
            return False

    def get_github_status(self) -> Dict[str, Any]:
        """Get GitHub integration status"""
        return {
            "configured": self.config.token is not None,
            "api_available": self._is_github_available(),
            "owner": self.config.owner,
            "repo": self.config.repo,
            "base_branch": self.config.base_branch,
        }


# Singleton instance
_github_pr_actions = None


def get_github_pr_actions(
    config: Optional[GitHubConfig] = None,
) -> GitHubPRActions:
    """Get or create GitHubPRActions instance"""
    global _github_pr_actions
    if _github_pr_actions is None:
        _github_pr_actions = GitHubPRActions(config)
    return _github_pr_actions
