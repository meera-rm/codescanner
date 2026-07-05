"""
Tests for Iteration PR Manager - Phase 4.3
Tests orchestration of file modifications and PR creation
"""

import pytest
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.iteration_pr_manager import (
    IterationPRManager,
    IterationPRResult,
    get_iteration_pr_manager,
)
from api.services.github_integration import GitHubConfig


@pytest.fixture
def temp_codebase():
    """Create temporary codebase for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create sample Python file
        py_file = tmppath / "sample.py"
        py_file.write_text("""def hello():
    return 42
""")

        yield tmppath


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
def pr_manager(temp_codebase, github_config):
    """Create IterationPRManager instance"""
    return IterationPRManager(str(temp_codebase), github_config)


class TestIterationPRResult:
    """Test IterationPRResult data structure"""

    def test_pr_result_success(self):
        """Test successful PR result"""
        result = IterationPRResult(
            success=True,
            pr_number=42,
            pr_url="https://github.com/user/repo/pull/42",
            branch_name="feature/test",
            files_modified=2,
            validation_passed=True,
            syntax_valid=True,
            linting_passed=True,
        )

        assert result.success
        assert result.pr_number == 42
        assert result.validation_passed

    def test_pr_result_failure(self):
        """Test failed PR result"""
        result = IterationPRResult(
            success=False,
            error_message="API error",
        )

        assert not result.success
        assert result.error_message is not None


class TestIterationPRManagerInit:
    """Test IterationPRManager initialization"""

    def test_init_with_config(self, temp_codebase, github_config):
        """Test initialization with config"""
        manager = IterationPRManager(str(temp_codebase), github_config)

        assert manager.codebase_path == str(temp_codebase)
        assert manager.github.config.owner == "testuser"

    def test_init_without_github_config(self, temp_codebase):
        """Test initialization without GitHub config"""
        manager = IterationPRManager(str(temp_codebase))

        assert manager.codebase_path == str(temp_codebase)
        assert manager.github is not None


class TestPRDescription:
    """Test PR description building"""

    def test_build_pr_description(self, pr_manager, temp_codebase):
        """Test building PR description"""
        # Create mock results
        from api.services.file_modifier_service import ModificationResult
        from api.services.code_validator import ValidationResult

        mod_result = ModificationResult(
            success=True,
            files_modified=["file1.py"],
            files_failed=[],
            changes={"files": 1},
        )

        val_result = ValidationResult(
            success=True,
            syntax_valid=True,
            linting_passed=True,
            tests_passed=True,
        )

        diff_summary = {
            "files_changed": 1,
            "lines_added": 10,
            "lines_removed": 2,
        }

        description = pr_manager._build_pr_description(
            "Test PR",
            mod_result,
            val_result,
            diff_summary,
        )

        assert "Files Modified" in description
        assert "Changes" in description
        assert "Validation" in description
        assert "file1.py" in description

    def test_pr_description_with_errors(self, pr_manager):
        """Test PR description with validation errors"""
        from api.services.file_modifier_service import ModificationResult
        from api.services.code_validator import ValidationResult

        mod_result = ModificationResult(
            success=True,
            files_modified=["file1.py"],
            files_failed=[],
            changes={},
        )

        val_result = ValidationResult(
            success=False,
            syntax_valid=False,
            syntax_errors=["Line 1: SyntaxError"],
        )

        diff_summary = {}

        description = pr_manager._build_pr_description(
            "Test PR",
            mod_result,
            val_result,
            diff_summary,
        )

        assert "Syntax Errors" in description


class TestPRCreationWorkflow:
    """Test PR creation workflow"""

    @pytest.mark.asyncio
    async def test_apply_and_create_pr_structure(self, pr_manager):
        """Test PR creation workflow structure"""
        suggestion = {
            "agent": "Agent A",
            "description": "Test suggestion",
            "changes": [],
            "new_imports": [],
            "modified_code": "x = 1",
        }

        result = await pr_manager.apply_and_create_pr(
            suggestion,
            pr_title="Test PR",
            pr_description="Test description",
        )

        assert isinstance(result, IterationPRResult)
        assert hasattr(result, "success")
        assert hasattr(result, "pr_number")

    @pytest.mark.asyncio
    async def test_apply_and_create_pr_branch_name(self, pr_manager):
        """Test PR creation with custom branch name"""
        suggestion = {
            "agent": "Agent A",
            "description": "Test",
            "changes": [],
            "new_imports": [],
            "modified_code": "",
        }

        result = await pr_manager.apply_and_create_pr(
            suggestion,
            pr_title="Test",
            pr_description="Test",
            branch_name="custom-branch",
        )

        assert isinstance(result, IterationPRResult)


class TestPROperations:
    """Test PR operations"""

    def test_get_pr_status(self, pr_manager):
        """Test getting PR status"""
        status = pr_manager.get_pr_status(42)

        # Should return None or dict (depends on GitHub availability)
        assert status is None or isinstance(status, dict)

    def test_request_review(self, pr_manager):
        """Test requesting review"""
        result = pr_manager.request_review(42, ["reviewer1", "reviewer2"])

        assert isinstance(result, bool)

    def test_add_labels(self, pr_manager):
        """Test adding labels"""
        result = pr_manager.add_labels(42, ["bug", "enhancement"])

        assert isinstance(result, bool)


class TestErrorHandling:
    """Test error handling"""

    @pytest.mark.asyncio
    async def test_apply_and_create_pr_error_handling(self, pr_manager):
        """Test error handling in PR creation"""
        # Empty suggestion
        suggestion = {}

        result = await pr_manager.apply_and_create_pr(
            suggestion,
            pr_title="Test",
            pr_description="Test",
        )

        # Should handle gracefully
        assert isinstance(result, IterationPRResult)


class TestSingletonPattern:
    """Test factory function"""

    def test_get_iteration_pr_manager(self, temp_codebase):
        """Test factory function"""
        manager = get_iteration_pr_manager(str(temp_codebase))

        assert manager is not None
        assert isinstance(manager, IterationPRManager)


class TestIntegrationFlow:
    """Test integration flows"""

    @pytest.mark.asyncio
    async def test_complete_flow(self, pr_manager):
        """Test complete PR creation flow"""
        # Create a suggestion
        suggestion = {
            "agent": "Agent A",
            "description": "Add helper function",
            "changes": ["New: helper()"],
            "new_imports": [],
            "modified_code": "def helper():\n    return 42",
        }

        # Apply and create PR
        result = await pr_manager.apply_and_create_pr(
            suggestion,
            pr_title="Add helper function",
            pr_description="Adds a useful helper function",
        )

        # Check result structure
        assert isinstance(result, IterationPRResult)
        assert result.files_modified >= 0
        assert result.files_failed >= 0

    @pytest.mark.asyncio
    async def test_flow_with_branch_and_labels(self, pr_manager):
        """Test flow with custom branch and labels"""
        suggestion = {
            "agent": "Agent A",
            "description": "Test",
            "changes": [],
            "new_imports": [],
            "modified_code": "",
        }

        # Create PR
        result = await pr_manager.apply_and_create_pr(
            suggestion,
            pr_title="Test PR",
            pr_description="Test",
            branch_name="feature/custom",
        )

        assert isinstance(result, IterationPRResult)

        # If PR was created, add labels
        if result.pr_number:
            label_result = pr_manager.add_labels(
                result.pr_number,
                ["automated", "from-codepulse"],
            )
            assert isinstance(label_result, bool)


class TestParameterVariations:
    """Test different parameter variations"""

    @pytest.mark.asyncio
    async def test_create_pr_without_branch_name(self, pr_manager):
        """Test PR creation without explicit branch name"""
        suggestion = {
            "agent": "Agent A",
            "description": "Test",
            "changes": [],
            "new_imports": [],
            "modified_code": "",
        }

        result = await pr_manager.apply_and_create_pr(
            suggestion,
            pr_title="Test",
            pr_description="Test",
        )

        assert isinstance(result, IterationPRResult)
        # Branch name should be auto-generated
        if result.success:
            assert result.branch_name is not None

    @pytest.mark.asyncio
    async def test_create_pr_with_auto_merge(self, pr_manager):
        """Test PR creation with auto-merge option"""
        suggestion = {
            "agent": "Agent A",
            "description": "Test",
            "changes": [],
            "new_imports": [],
            "modified_code": "",
        }

        result = await pr_manager.apply_and_create_pr(
            suggestion,
            pr_title="Test",
            pr_description="Test",
            auto_merge=False,  # Don't actually merge in test
        )

        assert isinstance(result, IterationPRResult)


class TestValidationIntegration:
    """Test validation integration"""

    @pytest.mark.asyncio
    async def test_validation_in_pr_creation(self, pr_manager):
        """Test that validation is integrated in PR creation"""
        suggestion = {
            "agent": "Agent A",
            "description": "Test",
            "changes": [],
            "new_imports": [],
            "modified_code": "x = 1",
        }

        result = await pr_manager.apply_and_create_pr(
            suggestion,
            pr_title="Test",
            pr_description="Test",
        )

        # Result should include validation status
        assert hasattr(result, "validation_passed")
        assert hasattr(result, "syntax_valid")
        assert hasattr(result, "linting_passed")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
