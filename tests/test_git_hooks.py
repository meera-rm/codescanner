"""
Tests for Git Hooks Integration - Phase 6.2.3
"""

import pytest
from pathlib import Path
import sys
import os
import tempfile

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.git_hooks import (
    GitHooksManager,
    HookType,
    HookStatus
)


class TestGitHooksManager:
    """Test git hooks manager"""

    def test_configure_hook(self):
        """Test hook configuration"""
        manager = GitHooksManager()

        config = manager.configure_hook(
            hook_type=HookType.PRE_COMMIT,
            enabled=True,
            fail_on_error=False,
            quality_threshold=70.0,
            auto_fix=True
        )

        assert config.hook_type == HookType.PRE_COMMIT
        assert config.enabled is True
        assert config.quality_threshold == 70.0
        assert config.auto_fix is True

    def test_record_execution(self):
        """Test recording hook execution"""
        manager = GitHooksManager()

        execution = manager.record_execution(
            hook_type=HookType.PRE_COMMIT,
            status=HookStatus.PASSED,
            duration_seconds=2.5,
            files_checked=5,
            issues_found=0,
            message="Pre-commit checks passed"
        )

        assert execution.execution_id.startswith("exec_")
        assert execution.status == HookStatus.PASSED
        assert execution.files_checked == 5

    def test_record_execution_failure(self):
        """Test recording failed execution"""
        manager = GitHooksManager()

        execution = manager.record_execution(
            hook_type=HookType.COMMIT_MSG,
            status=HookStatus.FAILED,
            duration_seconds=1.0,
            files_checked=0,
            issues_found=1,
            message="Commit message format invalid"
        )

        assert execution.status == HookStatus.FAILED
        assert execution.issues_found == 1

    def test_execution_history(self):
        """Test getting execution history"""
        manager = GitHooksManager()

        # Record multiple executions
        for i in range(5):
            manager.record_execution(
                hook_type=HookType.PRE_COMMIT,
                status=HookStatus.PASSED if i % 2 == 0 else HookStatus.FAILED,
                duration_seconds=float(i + 1),
                files_checked=i + 1,
                issues_found=i,
                message=f"Execution {i}"
            )

        history = manager.get_execution_history(limit=3)

        assert len(history) == 3
        assert all(e.hook_type == HookType.PRE_COMMIT for e in history)

    def test_execution_history_by_hook_type(self):
        """Test filtering execution history by hook type"""
        manager = GitHooksManager()

        # Record executions for different hook types
        manager.record_execution(
            hook_type=HookType.PRE_COMMIT,
            status=HookStatus.PASSED,
            duration_seconds=1.0,
            files_checked=3,
            issues_found=0,
            message="Pre-commit passed"
        )

        manager.record_execution(
            hook_type=HookType.COMMIT_MSG,
            status=HookStatus.PASSED,
            duration_seconds=0.5,
            files_checked=0,
            issues_found=0,
            message="Commit message valid"
        )

        pre_commit_history = manager.get_execution_history(hook_type=HookType.PRE_COMMIT)
        commit_msg_history = manager.get_execution_history(hook_type=HookType.COMMIT_MSG)

        assert len(pre_commit_history) == 1
        assert len(commit_msg_history) == 1

    def test_hook_status(self):
        """Test getting hook status"""
        manager = GitHooksManager()

        # Configure hooks
        manager.configure_hook(HookType.PRE_COMMIT, enabled=True)
        manager.configure_hook(HookType.COMMIT_MSG, enabled=True)

        # Record executions
        manager.record_execution(
            hook_type=HookType.PRE_COMMIT,
            status=HookStatus.PASSED,
            duration_seconds=1.0,
            files_checked=3,
            issues_found=0,
            message="Passed"
        )

        manager.record_execution(
            hook_type=HookType.COMMIT_MSG,
            status=HookStatus.FAILED,
            duration_seconds=0.5,
            files_checked=0,
            issues_found=1,
            message="Failed"
        )

        status = manager.get_hook_status()

        assert status["total_executions"] == 2
        assert status["passed"] == 1
        assert status["failed"] == 1

    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        manager = GitHooksManager()

        # Record 3 passed, 2 failed
        for i in range(3):
            manager.record_execution(
                hook_type=HookType.PRE_COMMIT,
                status=HookStatus.PASSED,
                duration_seconds=1.0,
                files_checked=1,
                issues_found=0,
                message="Passed"
            )

        for i in range(2):
            manager.record_execution(
                hook_type=HookType.PRE_COMMIT,
                status=HookStatus.FAILED,
                duration_seconds=1.0,
                files_checked=1,
                issues_found=1,
                message="Failed"
            )

        status = manager.get_hook_status()
        assert status["success_rate"] == pytest.approx(60.0)

    def test_hook_config_to_dict(self):
        """Test hook config serialization"""
        manager = GitHooksManager()

        config = manager.configure_hook(
            HookType.PRE_PUSH,
            enabled=True,
            fail_on_error=True,
            quality_threshold=75.0
        )

        config_dict = config.to_dict()

        assert config_dict["type"] == "pre-push"
        assert config_dict["enabled"] is True
        assert config_dict["quality_threshold"] == 75.0

    def test_hook_execution_to_dict(self):
        """Test hook execution serialization"""
        manager = GitHooksManager()

        execution = manager.record_execution(
            hook_type=HookType.PRE_COMMIT,
            status=HookStatus.PASSED,
            duration_seconds=3.2,
            files_checked=7,
            issues_found=2,
            message="Analysis complete"
        )

        exec_dict = execution.to_dict()

        assert exec_dict["hook_type"] == "pre-commit"
        assert exec_dict["status"] == "passed"
        assert exec_dict["files_checked"] == 7

    def test_pre_commit_hook_script(self):
        """Test pre-commit hook script generation"""
        manager = GitHooksManager()

        script = manager._get_pre_commit_hook()

        assert "#!/bin/bash" in script
        assert "CodePulse AI" in script
        assert "pre-commit" in script
        assert "codepulse analyze" in script

    def test_commit_msg_hook_script(self):
        """Test commit message hook script generation"""
        manager = GitHooksManager()

        script = manager._get_commit_msg_hook()

        assert "#!/bin/bash" in script
        assert "commit message" in script or "COMMIT_MSG" in script
        assert "72 characters" in script

    def test_all_hook_types(self):
        """Test all hook types are available"""
        manager = GitHooksManager()

        hook_types = [HookType.PRE_COMMIT, HookType.COMMIT_MSG, HookType.PRE_PUSH, HookType.POST_COMMIT]

        for hook_type in hook_types:
            config = manager.configure_hook(hook_type)
            assert config.hook_type == hook_type


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
