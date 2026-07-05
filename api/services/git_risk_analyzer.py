"""
Git Risk Analyzer - Phase 4.6
Analyze git history for risky changes and patterns
"""

import logging
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk level classification"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ChangeType(Enum):
    """Type of change"""
    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    RENAMED = "renamed"


@dataclass
class FileRisk:
    """Risk assessment for a file"""
    file_path: str
    risk_level: RiskLevel
    change_frequency: int  # Number of changes in period
    last_modified: Optional[str] = None
    contributors: int = 0
    recent_changes: int = 0  # Changes in last 30 days
    deletion_ratio: float = 0.0  # % of changes that were deletions
    large_changes: int = 0  # Changes with >500 lines


@dataclass
class CommitRisk:
    """Risk assessment for a commit"""
    commit_hash: str
    author: str
    timestamp: str
    message: str
    risk_level: RiskLevel
    files_changed: int
    lines_added: int
    lines_removed: int
    is_large: bool  # >500 lines changed
    is_merge: bool
    touched_risky_files: int


@dataclass
class GitRiskAnalysis:
    """Result of git risk analysis"""
    success: bool
    repository_path: str
    total_commits: int
    total_files: int
    analysis_period_days: int
    file_risks: List[FileRisk]
    commit_risks: List[CommitRisk]
    high_risk_files: List[str]
    high_risk_authors: List[Tuple[str, int]]  # (author, risk_score)
    ownership_map: Dict[str, str]  # file -> primary_author
    recommendations: List[str]
    error_message: Optional[str] = None


class GitRiskAnalyzer:
    """Analyze git repository for risk patterns"""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.analysis_days = 90  # Analyze last 90 days

    async def analyze(self) -> GitRiskAnalysis:
        """
        Analyze git repository for risks.

        Returns:
            GitRiskAnalysis with risk assessments
        """
        try:
            if not self._is_git_repo():
                return GitRiskAnalysis(
                    success=False,
                    repository_path=str(self.repo_path),
                    total_commits=0,
                    total_files=0,
                    analysis_period_days=self.analysis_days,
                    file_risks=[],
                    commit_risks=[],
                    high_risk_files=[],
                    high_risk_authors=[],
                    ownership_map={},
                    recommendations=[],
                    error_message="Not a git repository",
                )

            logger.info(f"Analyzing git repository: {self.repo_path}")

            # Step 1: Get commit history
            commits = self._get_commit_history()

            # Step 2: Analyze file changes
            file_stats = self._analyze_file_changes(commits)

            # Step 3: Calculate file risks
            file_risks = self._calculate_file_risks(file_stats)

            # Step 4: Calculate commit risks
            commit_risks = self._calculate_commit_risks(commits, file_stats)

            # Step 5: Identify high-risk files
            high_risk_files = self._identify_high_risk_files(file_risks)

            # Step 6: Track ownership
            ownership = self._track_code_ownership(commits, file_stats)

            # Step 7: Identify risky authors
            risky_authors = self._identify_risky_authors(commit_risks)

            # Step 8: Generate recommendations
            recommendations = self._generate_recommendations(
                file_risks, commit_risks, high_risk_files
            )

            logger.info(f"Git analysis complete: {len(commits)} commits, {len(file_stats)} files")

            return GitRiskAnalysis(
                success=True,
                repository_path=str(self.repo_path),
                total_commits=len(commits),
                total_files=len(file_stats),
                analysis_period_days=self.analysis_days,
                file_risks=file_risks,
                commit_risks=commit_risks,
                high_risk_files=high_risk_files,
                high_risk_authors=risky_authors,
                ownership_map=ownership,
                recommendations=recommendations,
            )

        except Exception as e:
            logger.error(f"Error analyzing git repository: {e}")
            return GitRiskAnalysis(
                success=False,
                repository_path=str(self.repo_path),
                total_commits=0,
                total_files=0,
                analysis_period_days=self.analysis_days,
                file_risks=[],
                commit_risks=[],
                high_risk_files=[],
                high_risk_authors=[],
                ownership_map={},
                recommendations=[],
                error_message=str(e),
            )

    def _is_git_repo(self) -> bool:
        """Check if directory is a git repository"""
        try:
            subprocess.run(
                ["git", "rev-parse", "--git-dir"],
                cwd=self.repo_path,
                capture_output=True,
                timeout=5,
            )
            return True
        except Exception:
            return False

    def _get_commit_history(self) -> List[Dict[str, Any]]:
        """Get commit history from git"""
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    f"--since={self.analysis_days} days ago",
                    "--format=%H|%an|%ai|%s|%b",
                    "--numstat",
                ],
                cwd=self.repo_path,
                capture_output=True,
                timeout=30,
                text=True,
            )

            commits = []
            current_commit = None

            for line in result.stdout.split("\n"):
                if "|" in line and not line.startswith("\t"):
                    # Commit header
                    parts = line.split("|", 4)
                    if len(parts) >= 4:
                        current_commit = {
                            "hash": parts[0],
                            "author": parts[1],
                            "timestamp": parts[2],
                            "message": parts[3],
                            "files": [],
                            "additions": 0,
                            "deletions": 0,
                        }
                        commits.append(current_commit)
                elif line.startswith("\t") and current_commit:
                    # File changes
                    parts = line.split("\t")
                    if len(parts) >= 3:
                        try:
                            additions = int(parts[0]) if parts[0] != "-" else 0
                            deletions = int(parts[1]) if parts[1] != "-" else 0
                            file_path = parts[2]

                            current_commit["files"].append(file_path)
                            current_commit["additions"] += additions
                            current_commit["deletions"] += deletions
                        except ValueError:
                            pass

            return commits

        except Exception as e:
            logger.error(f"Error getting commit history: {e}")
            return []

    def _analyze_file_changes(
        self, commits: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Analyze changes per file"""
        file_stats = {}

        for commit in commits:
            for file_path in commit["files"]:
                if file_path not in file_stats:
                    file_stats[file_path] = {
                        "change_count": 0,
                        "additions": 0,
                        "deletions": 0,
                        "contributors": set(),
                        "last_modified": commit["timestamp"],
                        "large_changes": 0,
                    }

                stats = file_stats[file_path]
                stats["change_count"] += 1
                stats["additions"] += commit["additions"]
                stats["deletions"] += commit["deletions"]
                stats["contributors"].add(commit["author"])

                # Track large changes
                total_change = commit["additions"] + commit["deletions"]
                if total_change > 500:
                    stats["large_changes"] += 1

                stats["last_modified"] = commit["timestamp"]

        return file_stats

    def _calculate_file_risks(
        self, file_stats: Dict[str, Dict[str, Any]]
    ) -> List[FileRisk]:
        """Calculate risk for each file"""
        file_risks = []

        for file_path, stats in file_stats.items():
            # Determine risk level
            risk_level = self._assess_file_risk_level(stats)

            deletion_ratio = (
                stats["deletions"] / (stats["additions"] + stats["deletions"])
                if (stats["additions"] + stats["deletions"]) > 0
                else 0.0
            )

            file_risk = FileRisk(
                file_path=file_path,
                risk_level=risk_level,
                change_frequency=stats["change_count"],
                last_modified=stats["last_modified"],
                contributors=len(stats["contributors"]),
                recent_changes=stats["change_count"],  # Simplified
                deletion_ratio=deletion_ratio,
                large_changes=stats["large_changes"],
            )
            file_risks.append(file_risk)

        return sorted(file_risks, key=lambda x: self._risk_score(x.risk_level), reverse=True)

    def _assess_file_risk_level(self, stats: Dict[str, Any]) -> RiskLevel:
        """Assess risk level for a file"""
        score = 0

        # High change frequency
        if stats["change_count"] > 10:
            score += 3
        elif stats["change_count"] > 5:
            score += 2
        elif stats["change_count"] > 0:
            score += 1

        # Large changes
        score += stats["large_changes"] * 2

        # Many contributors (churn)
        if len(stats["contributors"]) > 5:
            score += 2
        elif len(stats["contributors"]) > 2:
            score += 1

        # High deletion ratio
        total = stats["additions"] + stats["deletions"]
        if total > 0:
            deletion_ratio = stats["deletions"] / total
            if deletion_ratio > 0.5:
                score += 2

        # Classify
        if score >= 8:
            return RiskLevel.CRITICAL
        elif score >= 5:
            return RiskLevel.HIGH
        elif score >= 2:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW

    def _calculate_commit_risks(
        self,
        commits: List[Dict[str, Any]],
        file_stats: Dict[str, Dict[str, Any]],
    ) -> List[CommitRisk]:
        """Calculate risk for each commit"""
        commit_risks = []

        for commit in commits:
            is_merge = "Merge" in commit["message"]
            total_change = commit["additions"] + commit["deletions"]
            is_large = total_change > 500

            # Count risky files touched
            risky_count = sum(
                1 for file in commit["files"]
                if file in file_stats and file_stats[file]["change_count"] > 5
            )

            # Determine risk level
            if is_large and is_merge:
                risk_level = RiskLevel.CRITICAL
            elif is_large or risky_count > 3:
                risk_level = RiskLevel.HIGH
            elif is_merge or risky_count > 0:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW

            commit_risk = CommitRisk(
                commit_hash=commit["hash"],
                author=commit["author"],
                timestamp=commit["timestamp"],
                message=commit["message"],
                risk_level=risk_level,
                files_changed=len(commit["files"]),
                lines_added=commit["additions"],
                lines_removed=commit["deletions"],
                is_large=is_large,
                is_merge=is_merge,
                touched_risky_files=risky_count,
            )
            commit_risks.append(commit_risk)

        return sorted(commit_risks, key=lambda x: self._risk_score(x.risk_level), reverse=True)

    def _identify_high_risk_files(self, file_risks: List[FileRisk]) -> List[str]:
        """Identify files with high or critical risk"""
        return [
            f.file_path
            for f in file_risks
            if f.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]

    def _track_code_ownership(
        self,
        commits: List[Dict[str, Any]],
        file_stats: Dict[str, Dict[str, Any]],
    ) -> Dict[str, str]:
        """Track code ownership (primary author per file)"""
        ownership = {}

        for file_path in file_stats.keys():
            contributors = file_stats[file_path]["contributors"]
            if contributors:
                ownership[file_path] = sorted(contributors)[0]  # Alphabetically first

        return ownership

    def _identify_risky_authors(self, commit_risks: List[CommitRisk]) -> List[Tuple[str, int]]:
        """Identify authors with risky commit patterns"""
        author_scores = {}

        for commit in commit_risks:
            score = self._risk_score(commit.risk_level)
            if commit.author not in author_scores:
                author_scores[commit.author] = 0
            author_scores[commit.author] += score

        # Sort by score and return top risky authors
        return sorted(author_scores.items(), key=lambda x: x[1], reverse=True)[:5]

    def _generate_recommendations(
        self,
        file_risks: List[FileRisk],
        commit_risks: List[CommitRisk],
        high_risk_files: List[str],
    ) -> List[str]:
        """Generate risk mitigation recommendations"""
        recommendations = []

        # Recommend code review for high-risk files
        if high_risk_files:
            recommendations.append(
                f"Prioritize code reviews for {len(high_risk_files)} high-risk files: "
                f"{', '.join(high_risk_files[:3])}"
            )

        # Recommend refactoring for frequently changed files
        frequently_changed = [f for f in file_risks if f.change_frequency > 20]
        if frequently_changed:
            recommendations.append(
                f"Consider refactoring frequently changed files: "
                f"{', '.join(f.file_path for f in frequently_changed[:3])}"
            )

        # Recommend code ownership clarification
        files_with_many_contributors = [f for f in file_risks if f.contributors > 5]
        if files_with_many_contributors:
            recommendations.append(
                f"Clarify code ownership for files with many contributors"
            )

        # Recommend breaking up large changes
        large_commits = [c for c in commit_risks if c.is_large]
        if len(large_commits) > 5:
            recommendations.append(
                "Avoid large commits (>500 lines). Break into smaller, focused commits."
            )

        return recommendations

    def _risk_score(self, risk_level: RiskLevel) -> int:
        """Convert risk level to numeric score"""
        return {
            RiskLevel.LOW: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4,
        }.get(risk_level, 0)


# Factory function
def get_git_risk_analyzer(repo_path: str) -> GitRiskAnalyzer:
    """Create GitRiskAnalyzer instance"""
    return GitRiskAnalyzer(repo_path)
