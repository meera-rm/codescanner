import os
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime, timedelta
from collections import defaultdict


class GitAnalyzer:
    """Analyze code risk based on git blame and commit history."""

    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        self.is_git_repo = (self.repo_path / ".git").exists()

    def analyze(self) -> Dict[str, Any]:
        """Run full git analysis."""
        if not self.is_git_repo:
            return {
                "is_git_repo": False,
                "high_risk_files": [],
                "churn_analysis": {},
                "recommendations": ["Initialize git repository to enable git analysis"],
            }

        high_risk_files = self._find_high_risk_files()
        churn = self._analyze_churn()

        return {
            "is_git_repo": True,
            "high_risk_files": high_risk_files,
            "churn_analysis": churn,
            "recommendations": self._generate_recommendations(high_risk_files, churn),
        }

    def _find_high_risk_files(self) -> List[Tuple[str, float]]:
        """Find files with high risk based on churn and changes."""
        risk_scores = {}

        try:
            result = subprocess.run(
                ["git", "log", "--pretty=format:%H", "--name-only"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                file_change_count = defaultdict(int)

                for line in lines:
                    if line and not line.startswith("commit"):
                        file_change_count[line] += 1

                for filepath, count in file_change_count.items():
                    if filepath.endswith(".py"):
                        risk_scores[filepath] = min(count / 10, 1.0)

                sorted_by_risk = sorted(risk_scores.items(), key=lambda x: x[1], reverse=True)
                return sorted_by_risk[:10]

        except Exception:
            pass

        return []

    def _analyze_churn(self) -> Dict[str, Any]:
        """Analyze code churn (change frequency)."""
        churn_metrics = {
            "total_commits": 0,
            "recent_commits_30d": 0,
            "files_changed": 0,
            "average_commit_size": 0,
        }

        try:
            result = subprocess.run(
                ["git", "rev-list", "--count", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                churn_metrics["total_commits"] = int(result.stdout.strip())

            result = subprocess.run(
                ["git", "log", "--since=30.days.ago", "--pretty=format:%H"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                churn_metrics["recent_commits_30d"] = len(result.stdout.strip().split("\n"))

        except Exception:
            pass

        return churn_metrics

    def _calculate_file_risk(self, filepath: str) -> float:
        """Calculate risk score for a file (0.0-1.0)."""
        risk = 0.0

        try:
            result = subprocess.run(
                ["git", "log", "--follow", "--pretty=format:%aI", filepath],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=5,
            )

            if result.returncode == 0:
                commits = result.stdout.strip().split("\n")
                recent_commits = len([c for c in commits if self._is_recent(c)])
                total_commits = len(commits)

                if total_commits > 0:
                    churn_ratio = recent_commits / total_commits
                    risk += churn_ratio * 0.5

                if total_commits > 20:
                    risk += 0.3

                if recent_commits > 5:
                    risk += 0.2

        except Exception:
            pass

        return min(risk, 1.0)

    def _is_recent(self, timestamp_str: str) -> bool:
        """Check if timestamp is within last 30 days."""
        try:
            timestamp = datetime.fromisoformat(timestamp_str.replace("Z", "+00:00"))
            threshold = datetime.now(timestamp.tzinfo) - timedelta(days=30)
            return timestamp > threshold
        except Exception:
            return False

    def _generate_recommendations(self, high_risk_files: List, churn: Dict) -> List[str]:
        """Generate recommendations based on analysis."""
        recommendations = []

        if high_risk_files:
            top_files = [f[0] for f in high_risk_files[:3]]
            recommendations.append(f"Review high-risk files: {', '.join(top_files)}")

        if churn.get("recent_commits_30d", 0) > 50:
            recommendations.append("High churn detected - consider refactoring frequently-changed code")

        if churn.get("total_commits", 0) < 10:
            recommendations.append("Repository is new - focus on establishing patterns early")

        if not recommendations:
            recommendations.append("Git history looks healthy")

        return recommendations
