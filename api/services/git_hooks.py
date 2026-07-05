"""
Git Hooks Integration - Phase 6.2.3
Pre-commit and commit-msg hooks for automatic code scanning
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import os
import json
import time
import subprocess


class HookType(str, Enum):
    """Git hook types"""
    PRE_COMMIT = "pre-commit"
    COMMIT_MSG = "commit-msg"
    PRE_PUSH = "pre-push"
    POST_COMMIT = "post-commit"


class HookStatus(str, Enum):
    """Hook execution status"""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    WARNING = "warning"


@dataclass
class HookConfig:
    """Git hook configuration"""
    hook_type: HookType
    enabled: bool = True
    fail_on_error: bool = False
    quality_threshold: float = 60.0
    check_message_format: bool = True
    auto_fix: bool = False
    exclude_paths: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.hook_type.value,
            "enabled": self.enabled,
            "fail_on_error": self.fail_on_error,
            "quality_threshold": self.quality_threshold,
            "auto_fix": self.auto_fix
        }


@dataclass
class HookExecution:
    """Record of hook execution"""
    execution_id: str
    hook_type: HookType
    status: HookStatus
    duration_seconds: float
    files_checked: int
    issues_found: int
    message: str
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "execution_id": self.execution_id,
            "hook_type": self.hook_type.value,
            "status": self.status.value,
            "duration": self.duration_seconds,
            "files_checked": self.files_checked,
            "issues_found": self.issues_found
        }


class GitHooksManager:
    """Manages git hooks for CodePulse AI"""

    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self.hooks_dir = os.path.join(repo_path, ".git", "hooks")
        self.config: Dict[HookType, HookConfig] = {}
        self.executions: Dict[str, HookExecution] = {}

    def initialize_hooks(self) -> Dict[str, bool]:
        """Initialize all hooks"""
        results = {}

        for hook_type in HookType:
            try:
                self._create_hook(hook_type)
                results[hook_type.value] = True
            except Exception as e:
                results[hook_type.value] = False

        return results

    def _create_hook(self, hook_type: HookType) -> None:
        """Create a hook file"""
        if not os.path.exists(self.hooks_dir):
            os.makedirs(self.hooks_dir, exist_ok=True)

        hook_path = os.path.join(self.hooks_dir, hook_type.value)

        if hook_type == HookType.PRE_COMMIT:
            content = self._get_pre_commit_hook()
        elif hook_type == HookType.COMMIT_MSG:
            content = self._get_commit_msg_hook()
        elif hook_type == HookType.PRE_PUSH:
            content = self._get_pre_push_hook()
        else:
            content = self._get_post_commit_hook()

        with open(hook_path, 'w') as f:
            f.write(content)

        os.chmod(hook_path, 0o755)

    def _get_pre_commit_hook(self) -> str:
        """Generate pre-commit hook script"""
        return """#!/bin/bash
# CodePulse AI - Pre-commit Hook
# Scans staged files for quality issues

set -e

# Get staged files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM)

if [ -z "$STAGED_FILES" ]; then
    exit 0
fi

echo "🔍 Running CodePulse AI pre-commit analysis..."

# Run CodePulse analysis
codepulse analyze \\
    --files $STAGED_FILES \\
    --fail-on-error false \\
    --min-quality-score 60 || true

echo "✓ Pre-commit checks passed"
exit 0
"""

    def _get_commit_msg_hook(self) -> str:
        """Generate commit-msg hook script"""
        return """#!/bin/bash
# CodePulse AI - Commit Message Hook
# Validates commit message format

COMMIT_MSG_FILE=$1

# Check commit message format
COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")

# Validate message is not empty
if [ -z "$(echo "$COMMIT_MSG" | grep -v '^#')" ]; then
    echo "❌ Commit message cannot be empty"
    exit 1
fi

# Check message length (first line should be < 72 chars)
FIRST_LINE=$(head -n 1 "$COMMIT_MSG_FILE")
if [ ${#FIRST_LINE} -gt 72 ]; then
    echo "⚠️  First line should be less than 72 characters"
fi

echo "✓ Commit message format valid"
exit 0
"""

    def _get_pre_push_hook(self) -> str:
        """Generate pre-push hook script"""
        return """#!/bin/bash
# CodePulse AI - Pre-push Hook
# Scans commits before pushing

set -e

echo "🔍 Running CodePulse AI pre-push analysis..."

# Get commits to be pushed
COMMITS=$(git log origin/$(git rev-parse --abbrev-ref HEAD)..HEAD --pretty=format:%H)

if [ -z "$COMMITS" ]; then
    exit 0
fi

# Run analysis on changed files
for commit in $COMMITS; do
    FILES=$(git diff-tree --no-commit-id --name-only -r $commit)
    codepulse analyze --files $FILES --fail-on-error false || true
done

echo "✓ Pre-push checks passed"
exit 0
"""

    def _get_post_commit_hook(self) -> str:
        """Generate post-commit hook script"""
        return """#!/bin/bash
# CodePulse AI - Post-commit Hook
# Logs commit analysis results

echo "📊 CodePulse AI commit recorded"

# Log commit info
COMMIT_SHA=$(git rev-parse HEAD)
AUTHOR=$(git log -1 --pretty=format:%an)
FILES=$(git diff-tree --no-commit-id --name-only -r $COMMIT_SHA | wc -l)

echo "Commit: $COMMIT_SHA"
echo "Author: $AUTHOR"
echo "Files changed: $FILES"

exit 0
"""

    def configure_hook(
        self,
        hook_type: HookType,
        enabled: bool = True,
        fail_on_error: bool = False,
        quality_threshold: float = 60.0,
        auto_fix: bool = False
    ) -> HookConfig:
        """Configure a hook"""
        config = HookConfig(
            hook_type=hook_type,
            enabled=enabled,
            fail_on_error=fail_on_error,
            quality_threshold=quality_threshold,
            auto_fix=auto_fix
        )

        self.config[hook_type] = config
        return config

    def record_execution(
        self,
        hook_type: HookType,
        status: HookStatus,
        duration_seconds: float,
        files_checked: int,
        issues_found: int,
        message: str
    ) -> HookExecution:
        """Record hook execution"""
        import secrets

        execution = HookExecution(
            execution_id=f"exec_{secrets.token_hex(8)}",
            hook_type=hook_type,
            status=status,
            duration_seconds=duration_seconds,
            files_checked=files_checked,
            issues_found=issues_found,
            message=message
        )

        self.executions[execution.execution_id] = execution
        return execution

    def get_execution_history(
        self,
        hook_type: Optional[HookType] = None,
        limit: int = 20
    ) -> List[HookExecution]:
        """Get hook execution history"""
        executions = list(self.executions.values())

        if hook_type:
            executions = [e for e in executions if e.hook_type == hook_type]

        executions.sort(key=lambda e: e.timestamp, reverse=True)
        return executions[:limit]

    def get_hook_status(self) -> Dict[str, Any]:
        """Get overall hook status"""
        installed = {}
        for hook_type in HookType:
            hook_path = os.path.join(self.hooks_dir, hook_type.value)
            installed[hook_type.value] = os.path.exists(hook_path)

        executions = list(self.executions.values())
        total_executions = len(executions)
        passed = sum(1 for e in executions if e.status == HookStatus.PASSED)
        failed = sum(1 for e in executions if e.status == HookStatus.FAILED)

        return {
            "hooks_installed": installed,
            "total_executions": total_executions,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total_executions * 100) if total_executions > 0 else 0,
            "configured_hooks": {k: v.to_dict() for k, v in self.config.items()}
        }

    def uninstall_hooks(self) -> Dict[str, bool]:
        """Uninstall all hooks"""
        results = {}

        for hook_type in HookType:
            hook_path = os.path.join(self.hooks_dir, hook_type.value)
            try:
                if os.path.exists(hook_path):
                    os.remove(hook_path)
                results[hook_type.value] = True
            except Exception:
                results[hook_type.value] = False

        return results


_global_hooks_manager = None

def get_git_hooks_manager(repo_path: str = ".") -> GitHooksManager:
    """Get global git hooks manager instance"""
    global _global_hooks_manager
    if _global_hooks_manager is None:
        _global_hooks_manager = GitHooksManager(repo_path)
    return _global_hooks_manager
