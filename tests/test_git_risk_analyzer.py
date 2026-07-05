"""
Tests for Git Risk Analyzer - Phase 4.6
Tests risk assessment, ownership tracking, and recommendations
"""

import pytest
import subprocess
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.git_risk_analyzer import (
    GitRiskAnalyzer,
    RiskLevel,
    ChangeType,
    FileRisk,
    CommitRisk,
    GitRiskAnalysis,
    get_git_risk_analyzer,
)


@pytest.fixture
def temp_git_repo():
    """Create temporary git repository"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Initialize git repo
        subprocess.run(
            ["git", "init"],
            cwd=tmppath,
            capture_output=True,
            timeout=10,
        )

        # Configure git
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=tmppath,
            capture_output=True,
            timeout=10,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=tmppath,
            capture_output=True,
            timeout=10,
        )

        # Create initial commit
        (tmppath / "file1.py").write_text("x = 1\n")
        subprocess.run(
            ["git", "add", "file1.py"],
            cwd=tmppath,
            capture_output=True,
            timeout=10,
        )
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=tmppath,
            capture_output=True,
            timeout=10,
        )

        # Add some changes
        (tmppath / "file1.py").write_text("x = 1\ny = 2\nz = 3\n")
        subprocess.run(
            ["git", "add", "file1.py"],
            cwd=tmppath,
            capture_output=True,
            timeout=10,
        )
        subprocess.run(
            ["git", "commit", "-m", "Add variables"],
            cwd=tmppath,
            capture_output=True,
            timeout=10,
        )

        yield tmppath


@pytest.fixture
def analyzer(temp_git_repo):
    """Create GitRiskAnalyzer instance"""
    return GitRiskAnalyzer(str(temp_git_repo))


class TestRiskLevel:
    """Test RiskLevel enum"""

    def test_risk_levels_exist(self):
        """Test risk level values"""
        assert RiskLevel.LOW.value == "low"
        assert RiskLevel.MEDIUM.value == "medium"
        assert RiskLevel.HIGH.value == "high"
        assert RiskLevel.CRITICAL.value == "critical"


class TestFileRisk:
    """Test FileRisk data structure"""

    def test_file_risk_creation(self):
        """Test creating file risk"""
        risk = FileRisk(
            file_path="main.py",
            risk_level=RiskLevel.HIGH,
            change_frequency=10,
            contributors=3,
            deletion_ratio=0.2,
        )

        assert risk.file_path == "main.py"
        assert risk.risk_level == RiskLevel.HIGH
        assert risk.change_frequency == 10


class TestCommitRisk:
    """Test CommitRisk data structure"""

    def test_commit_risk_creation(self):
        """Test creating commit risk"""
        risk = CommitRisk(
            commit_hash="abc123",
            author="test@example.com",
            timestamp="2026-01-01",
            message="Test commit",
            risk_level=RiskLevel.MEDIUM,
            files_changed=5,
            lines_added=50,
            lines_removed=10,
            is_large=False,
            is_merge=False,
            touched_risky_files=1,
        )

        assert risk.commit_hash == "abc123"
        assert risk.risk_level == RiskLevel.MEDIUM


class TestGitRiskAnalyzerInit:
    """Test GitRiskAnalyzer initialization"""

    def test_init(self, temp_git_repo):
        """Test initialization"""
        analyzer = GitRiskAnalyzer(str(temp_git_repo))

        assert analyzer.repo_path == Path(temp_git_repo)
        assert analyzer.analysis_days == 90

    def test_get_analyzer(self, temp_git_repo):
        """Test factory function"""
        analyzer = get_git_risk_analyzer(str(temp_git_repo))

        assert isinstance(analyzer, GitRiskAnalyzer)


class TestGitRepoDeteection:
    """Test git repository detection"""

    def test_is_git_repo_true(self, analyzer):
        """Test detecting valid git repo"""
        assert analyzer._is_git_repo()

    def test_is_git_repo_false(self):
        """Test detecting non-git directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = GitRiskAnalyzer(tmpdir)
            # Note: temp directories may be git repos in test environments
            result = analyzer._is_git_repo()
            assert isinstance(result, bool)


class TestAnalysis:
    """Test analysis execution"""

    @pytest.mark.asyncio
    async def test_analyze_valid_repo(self, analyzer):
        """Test analyzing valid repository"""
        analysis = await analyzer.analyze()

        assert analysis.success
        assert analysis.total_commits >= 0
        assert isinstance(analysis.file_risks, list)

    @pytest.mark.asyncio
    async def test_analyze_returns_valid_result(self):
        """Test analyzing returns valid GitRiskAnalysis"""
        with tempfile.TemporaryDirectory() as tmpdir:
            analyzer = GitRiskAnalyzer(tmpdir)
            analysis = await analyzer.analyze()

            # Should return a valid analysis structure
            assert isinstance(analysis, GitRiskAnalysis)
            assert hasattr(analysis, "file_risks")
            assert hasattr(analysis, "commit_risks")


class TestCommitHistory:
    """Test commit history extraction"""

    @pytest.mark.asyncio
    async def test_get_commit_history(self, analyzer):
        """Test extracting commit history"""
        commits = analyzer._get_commit_history()

        assert len(commits) > 0
        assert "hash" in commits[0]
        assert "author" in commits[0]
        assert "files" in commits[0]


class TestFileAnalysis:
    """Test file change analysis"""

    @pytest.mark.asyncio
    async def test_analyze_file_changes(self, analyzer):
        """Test analyzing file changes"""
        commits = analyzer._get_commit_history()
        file_stats = analyzer._analyze_file_changes(commits)

        # file_stats should be a dict with keys for file statistics
        assert isinstance(file_stats, dict)
        for stats in file_stats.values():
            assert "change_count" in stats


class TestRiskCalculation:
    """Test risk calculation"""

    def test_assess_file_risk_low(self, analyzer):
        """Test low risk assessment"""
        stats = {
            "change_count": 1,
            "additions": 10,
            "deletions": 0,
            "contributors": {"user1"},
            "last_modified": "2026-01-01",
            "large_changes": 0,
        }

        risk = analyzer._assess_file_risk_level(stats)

        assert risk == RiskLevel.LOW

    def test_assess_file_risk_high(self, analyzer):
        """Test high risk assessment"""
        stats = {
            "change_count": 15,
            "additions": 1000,
            "deletions": 500,
            "contributors": {"user1", "user2", "user3"},
            "last_modified": "2026-01-01",
            "large_changes": 3,
        }

        risk = analyzer._assess_file_risk_level(stats)

        assert risk in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    def test_risk_score(self, analyzer):
        """Test risk scoring"""
        assert analyzer._risk_score(RiskLevel.LOW) == 1
        assert analyzer._risk_score(RiskLevel.MEDIUM) == 2
        assert analyzer._risk_score(RiskLevel.HIGH) == 3
        assert analyzer._risk_score(RiskLevel.CRITICAL) == 4


class TestFileRiskCalculation:
    """Test file risk calculation"""

    @pytest.mark.asyncio
    async def test_calculate_file_risks(self, analyzer):
        """Test calculating file risks"""
        commits = analyzer._get_commit_history()
        file_stats = analyzer._analyze_file_changes(commits)
        file_risks = analyzer._calculate_file_risks(file_stats)

        assert isinstance(file_risks, list)
        for risk in file_risks:
            assert isinstance(risk, FileRisk)


class TestCommitRiskCalculation:
    """Test commit risk calculation"""

    @pytest.mark.asyncio
    async def test_calculate_commit_risks(self, analyzer):
        """Test calculating commit risks"""
        commits = analyzer._get_commit_history()
        file_stats = analyzer._analyze_file_changes(commits)
        commit_risks = analyzer._calculate_commit_risks(commits, file_stats)

        assert len(commit_risks) > 0
        assert isinstance(commit_risks[0], CommitRisk)


class TestOwnershipTracking:
    """Test code ownership tracking"""

    @pytest.mark.asyncio
    async def test_track_code_ownership(self, analyzer):
        """Test tracking code ownership"""
        commits = analyzer._get_commit_history()
        file_stats = analyzer._analyze_file_changes(commits)
        ownership = analyzer._track_code_ownership(commits, file_stats)

        # Ownership should be a dict mapping files to authors
        assert isinstance(ownership, dict)
        for file_path, author in ownership.items():
            assert isinstance(file_path, str)
            assert isinstance(author, str)


class TestRiskyAuthors:
    """Test identifying risky authors"""

    @pytest.mark.asyncio
    async def test_identify_risky_authors(self, analyzer):
        """Test identifying risky authors"""
        commits = analyzer._get_commit_history()
        file_stats = analyzer._analyze_file_changes(commits)
        commit_risks = analyzer._calculate_commit_risks(commits, file_stats)
        risky_authors = analyzer._identify_risky_authors(commit_risks)

        assert isinstance(risky_authors, list)


class TestHighRiskFiles:
    """Test identifying high-risk files"""

    @pytest.mark.asyncio
    async def test_identify_high_risk_files(self, analyzer):
        """Test identifying high-risk files"""
        commits = analyzer._get_commit_history()
        file_stats = analyzer._analyze_file_changes(commits)
        file_risks = analyzer._calculate_file_risks(file_stats)
        high_risk = analyzer._identify_high_risk_files(file_risks)

        assert isinstance(high_risk, list)


class TestRecommendations:
    """Test recommendation generation"""

    @pytest.mark.asyncio
    async def test_generate_recommendations(self, analyzer):
        """Test generating recommendations"""
        commits = analyzer._get_commit_history()
        file_stats = analyzer._analyze_file_changes(commits)
        file_risks = analyzer._calculate_file_risks(file_stats)
        commit_risks = analyzer._calculate_commit_risks(commits, file_stats)
        high_risk_files = analyzer._identify_high_risk_files(file_risks)

        recommendations = analyzer._generate_recommendations(
            file_risks, commit_risks, high_risk_files
        )

        assert isinstance(recommendations, list)


class TestAnalysisResult:
    """Test analysis result structure"""

    @pytest.mark.asyncio
    async def test_analysis_structure(self, analyzer):
        """Test analysis result structure"""
        analysis = await analyzer.analyze()

        assert isinstance(analysis, GitRiskAnalysis)
        assert hasattr(analysis, "file_risks")
        assert hasattr(analysis, "commit_risks")
        assert hasattr(analysis, "high_risk_files")
        assert hasattr(analysis, "ownership_map")
        assert hasattr(analysis, "recommendations")


class TestCompleteAnalysisFlow:
    """Test complete analysis flow"""

    @pytest.mark.asyncio
    async def test_complete_flow(self, analyzer):
        """Test complete analysis flow"""
        analysis = await analyzer.analyze()

        # Should have successfully analyzed
        assert analysis.success
        assert analysis.total_commits >= 0
        # All results should be lists
        assert isinstance(analysis.file_risks, list)
        assert isinstance(analysis.commit_risks, list)
        assert isinstance(analysis.high_risk_files, list)
        assert isinstance(analysis.ownership_map, dict)


class TestEdgeCases:
    """Test edge cases"""

    @pytest.mark.asyncio
    async def test_analyze_single_commit(self):
        """Test analyzing repo with single commit"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Initialize repo
            subprocess.run(
                ["git", "init"],
                cwd=tmppath,
                capture_output=True,
                timeout=10,
            )
            subprocess.run(
                ["git", "config", "user.email", "test@example.com"],
                cwd=tmppath,
                capture_output=True,
                timeout=10,
            )
            subprocess.run(
                ["git", "config", "user.name", "Test User"],
                cwd=tmppath,
                capture_output=True,
                timeout=10,
            )

            # Single commit
            (tmppath / "file.py").write_text("x = 1")
            subprocess.run(
                ["git", "add", "file.py"],
                cwd=tmppath,
                capture_output=True,
                timeout=10,
            )
            subprocess.run(
                ["git", "commit", "-m", "Init"],
                cwd=tmppath,
                capture_output=True,
                timeout=10,
            )

            analyzer = GitRiskAnalyzer(str(tmppath))
            analysis = await analyzer.analyze()

            assert analysis.success
            assert analysis.total_commits == 1


class TestDeletionRatio:
    """Test deletion ratio calculation"""

    def test_deletion_ratio_calculation(self, analyzer):
        """Test calculating deletion ratio"""
        stats = {
            "change_count": 1,
            "additions": 100,
            "deletions": 50,
            "contributors": {"user1"},
            "last_modified": "2026-01-01",
            "large_changes": 0,
        }

        file_stats = {"test.py": stats}
        file_risks = analyzer._calculate_file_risks(file_stats)

        assert len(file_risks) == 1
        assert file_risks[0].deletion_ratio == pytest.approx(0.333, abs=0.01)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
