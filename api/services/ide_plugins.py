"""
IDE Plugins Integration - Phase 6.2.4
Support for VS Code, JetBrains, and other IDE extensions
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
import secrets
from collections import defaultdict

from .codebase_learner import (
    CodebaseIntelligence,
    get_codebase_intelligence
)
from .predictive_analyzer import (
    PredictiveAnalyzer,
    get_predictive_analyzer
)


class IDEType(str, Enum):
    """Supported IDE types"""
    VS_CODE = "vscode"
    JETBRAINS = "jetbrains"
    SUBLIME = "sublime"
    NEOVIM = "neovim"


class AnalysisType(str, Enum):
    """Types of analysis to run"""
    QUICK = "quick"  # Fast syntax/style checks
    COMPREHENSIVE = "comprehensive"  # Full analysis
    INCREMENTAL = "incremental"  # Only changed files


@dataclass
class PluginConfig:
    """Plugin configuration"""
    plugin_id: str
    ide_type: IDEType
    enabled: bool = True
    auto_analysis: bool = True
    real_time_feedback: bool = True
    analysis_type: AnalysisType = AnalysisType.QUICK
    debounce_ms: int = 500  # Debounce before triggering analysis
    max_file_size_kb: int = 500
    custom_settings: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "plugin_id": self.plugin_id,
            "ide_type": self.ide_type.value,
            "enabled": self.enabled,
            "auto_analysis": self.auto_analysis,
            "real_time_feedback": self.real_time_feedback,
            "analysis_type": self.analysis_type.value,
            "debounce_ms": self.debounce_ms,
            "max_file_size_kb": self.max_file_size_kb,
        }


@dataclass
class AnalysisResult:
    """IDE analysis result"""
    analysis_id: str
    file_path: str
    language: str
    issues: List[Dict[str, Any]]  # Line, column, severity, message
    suggestions: List[Dict[str, Any]]  # Refactoring suggestions
    metrics: Dict[str, float]  # Complexity, maintainability, etc
    quality_score: float  # 0-100
    estimated_fix_time_minutes: int
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "analysis_id": self.analysis_id,
            "file_path": self.file_path,
            "language": self.language,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "metrics": self.metrics,
            "quality_score": self.quality_score,
            "estimated_fix_time_minutes": self.estimated_fix_time_minutes,
            "timestamp": self.timestamp,
        }


@dataclass
class IDESession:
    """IDE plugin session"""
    session_id: str
    ide_type: IDEType
    plugin_version: str
    user_id: Optional[str] = None
    project_path: Optional[str] = None
    is_active: bool = True
    last_heartbeat: float = field(default_factory=time.time)
    analysis_count: int = 0
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "session_id": self.session_id,
            "ide_type": self.ide_type.value,
            "plugin_version": self.plugin_version,
            "is_active": self.is_active,
            "analysis_count": self.analysis_count,
            "uptime_seconds": time.time() - self.created_at,
        }


class IDEPluginManager:
    """Manages IDE plugin integrations"""

    def __init__(self):
        self.intelligence = get_codebase_intelligence()
        self.analyzer = get_predictive_analyzer()

        # Plugin management
        self.plugins: Dict[str, PluginConfig] = {}
        self.sessions: Dict[str, IDESession] = {}
        self.analysis_results: Dict[str, AnalysisResult] = {}

        # Statistics
        self.stats: Dict[str, Any] = {
            "total_analyses": 0,
            "total_issues_found": 0,
            "total_suggestions": 0,
            "avg_analysis_time_ms": 0,
            "by_language": defaultdict(int),
        }

    def register_plugin(
        self,
        ide_type: IDEType,
        version: str,
        user_id: Optional[str] = None,
        project_path: Optional[str] = None
    ) -> IDESession:
        """Register a new IDE plugin session"""
        session_id = f"session_{secrets.token_hex(8)}"
        session = IDESession(
            session_id=session_id,
            ide_type=ide_type,
            plugin_version=version,
            user_id=user_id,
            project_path=project_path
        )

        self.sessions[session_id] = session

        # Auto-create default config
        plugin_id = f"plugin_{ide_type.value}_{session_id}"
        self.plugins[plugin_id] = PluginConfig(
            plugin_id=plugin_id,
            ide_type=ide_type
        )

        return session

    def configure_plugin(
        self,
        session_id: str,
        auto_analysis: bool = True,
        real_time_feedback: bool = True,
        analysis_type: AnalysisType = AnalysisType.QUICK,
        debounce_ms: int = 500
    ) -> Optional[PluginConfig]:
        """Configure plugin settings"""
        session = self.sessions.get(session_id)
        if not session:
            return None

        plugin_id = f"plugin_{session.ide_type.value}_{session_id}"
        if plugin_id not in self.plugins:
            return None

        config = self.plugins[plugin_id]
        config.auto_analysis = auto_analysis
        config.real_time_feedback = real_time_feedback
        config.analysis_type = analysis_type
        config.debounce_ms = debounce_ms

        return config

    def analyze_file(
        self,
        session_id: str,
        file_path: str,
        code: str,
        language: str
    ) -> Optional[AnalysisResult]:
        """Analyze a file from IDE"""
        session = self.sessions.get(session_id)
        if not session:
            return None

        analysis_id = f"analysis_{secrets.token_hex(8)}"
        start_time = time.time()

        # Extract pattern
        pattern = self.intelligence.extract_pattern(
            code=code,
            pattern_type="file",
            language=language,
            name=file_path.split("/")[-1],
            complexity=self._calculate_complexity(code)
        )

        # Get quality metrics
        issues = self._detect_issues(code, language)
        suggestions = self._generate_suggestions(pattern, language)
        metrics = self._calculate_metrics(code, language)
        quality_score = self._calculate_quality_score(metrics, issues)

        result = AnalysisResult(
            analysis_id=analysis_id,
            file_path=file_path,
            language=language,
            issues=issues,
            suggestions=suggestions,
            metrics=metrics,
            quality_score=quality_score,
            estimated_fix_time_minutes=self._estimate_fix_time(issues, suggestions)
        )

        # Store result
        self.analysis_results[analysis_id] = result

        # Update session
        session.analysis_count += 1
        session.last_heartbeat = time.time()

        # Update stats
        self._update_stats(result, time.time() - start_time)

        return result

    def get_quick_feedback(
        self,
        session_id: str,
        file_path: str,
        code: str,
        language: str
    ) -> Dict[str, Any]:
        """Get quick feedback without full analysis"""
        issues = self._detect_issues(code, language, quick=True)
        
        return {
            "file_path": file_path,
            "language": language,
            "issue_count": len(issues),
            "has_critical": any(i["severity"] == "critical" for i in issues),
            "issues": issues[:5],  # Top 5 issues only
        }

    def heartbeat(self, session_id: str) -> bool:
        """Update session heartbeat"""
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.last_heartbeat = time.time()
        return True

    def close_session(self, session_id: str) -> bool:
        """Close IDE session"""
        session = self.sessions.get(session_id)
        if not session:
            return False

        session.is_active = False
        return True

    def get_session_status(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session status"""
        session = self.sessions.get(session_id)
        if not session:
            return None

        plugin_id = f"plugin_{session.ide_type.value}_{session_id}"
        config = self.plugins.get(plugin_id)

        return {
            "session": session.to_dict(),
            "config": config.to_dict() if config else None,
            "is_connected": time.time() - session.last_heartbeat < 30,
        }

    def get_analysis_history(
        self,
        session_id: str,
        limit: int = 20
    ) -> List[AnalysisResult]:
        """Get analysis history for session"""
        session = self.sessions.get(session_id)
        if not session:
            return []

        # Return recent analyses (simplified - in production would query by session)
        results = list(self.analysis_results.values())
        results.sort(key=lambda x: x.timestamp, reverse=True)
        return results[:limit]

    def get_statistics(self) -> Dict[str, Any]:
        """Get overall statistics"""
        active_sessions = sum(1 for s in self.sessions.values() if s.is_active)

        return {
            "total_analyses": self.stats["total_analyses"],
            "total_issues_found": self.stats["total_issues_found"],
            "total_suggestions": self.stats["total_suggestions"],
            "avg_analysis_time_ms": self.stats["avg_analysis_time_ms"],
            "active_sessions": active_sessions,
            "total_sessions": len(self.sessions),
            "by_language": dict(self.stats["by_language"]),
        }

    # Helper methods

    def _calculate_complexity(self, code: str) -> float:
        """Calculate code complexity"""
        lines = code.split("\n")
        complexity = 1.0
        
        # Count control flow
        for line in lines:
            if any(keyword in line for keyword in ["if", "for", "while", "try"]):
                complexity += 1
            if "def " in line or "class " in line:
                complexity += 0.5
        
        return min(complexity, 20.0)

    def _detect_issues(
        self,
        code: str,
        language: str,
        quick: bool = False
    ) -> List[Dict[str, Any]]:
        """Detect code issues"""
        issues = []

        lines = code.split("\n")
        for line_num, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 100:
                issues.append({
                    "line": line_num,
                    "column": 100,
                    "severity": "warning",
                    "message": "Line too long (> 100 chars)",
                    "code": "line-length"
                })

            # Trailing whitespace
            if line != line.rstrip():
                issues.append({
                    "line": line_num,
                    "column": len(line.rstrip()),
                    "severity": "info",
                    "message": "Trailing whitespace",
                    "code": "trailing-whitespace"
                })

            # Complex conditions
            if line.count(" and ") > 2 or line.count(" or ") > 2:
                issues.append({
                    "line": line_num,
                    "column": 0,
                    "severity": "warning",
                    "message": "Complex condition - consider extracting",
                    "code": "complex-condition"
                })

            if quick and len(issues) >= 5:
                break

        return issues

    def _generate_suggestions(
        self,
        pattern: Any,
        language: str
    ) -> List[Dict[str, Any]]:
        """Generate refactoring suggestions"""
        suggestions = []

        if pattern.complexity > 10:
            suggestions.append({
                "type": "complexity",
                "priority": "high",
                "title": "Reduce complexity",
                "description": f"This function has complexity of {pattern.complexity:.1f}. Consider breaking it into smaller functions.",
                "estimated_improvement": 0.25
            })

        if pattern.lines_of_code > 100:
            suggestions.append({
                "type": "size",
                "priority": "medium",
                "title": "Function too long",
                "description": "Consider splitting this function into smaller, focused functions.",
                "estimated_improvement": 0.15
            })

        return suggestions

    def _calculate_metrics(self, code: str, language: str) -> Dict[str, float]:
        """Calculate code metrics"""
        lines = code.split("\n")
        non_empty_lines = len([l for l in lines if l.strip()])

        return {
            "lines_of_code": non_empty_lines,
            "cyclomatic_complexity": self._calculate_complexity(code),
            "avg_line_length": sum(len(l) for l in lines) / len(lines) if lines else 0,
            "blank_line_ratio": (len(lines) - non_empty_lines) / len(lines) if lines else 0,
        }

    def _calculate_quality_score(
        self,
        metrics: Dict[str, float],
        issues: List[Dict[str, Any]]
    ) -> float:
        """Calculate overall quality score (0-100)"""
        score = 100.0

        # Deduct for complexity
        score -= min(metrics["cyclomatic_complexity"] * 5, 30)

        # Deduct for issues
        critical_issues = sum(1 for i in issues if i["severity"] == "critical")
        warning_issues = sum(1 for i in issues if i["severity"] == "warning")
        
        score -= critical_issues * 5
        score -= warning_issues * 2

        return max(0, score)

    def _estimate_fix_time(
        self,
        issues: List[Dict[str, Any]],
        suggestions: List[Dict[str, Any]]
    ) -> int:
        """Estimate time to fix all issues"""
        time_minutes = 0

        # ~5 min per critical issue
        critical_count = sum(1 for i in issues if i["severity"] == "critical")
        time_minutes += critical_count * 5

        # ~2 min per warning
        warning_count = sum(1 for i in issues if i["severity"] == "warning")
        time_minutes += warning_count * 2

        # ~15 min per major suggestion
        for suggestion in suggestions:
            if suggestion.get("priority") == "high":
                time_minutes += 15
            elif suggestion.get("priority") == "medium":
                time_minutes += 10

        return time_minutes

    def _update_stats(self, result: AnalysisResult, duration_ms: float) -> None:
        """Update statistics"""
        self.stats["total_analyses"] += 1
        self.stats["total_issues_found"] += len(result.issues)
        self.stats["total_suggestions"] += len(result.suggestions)
        self.stats["by_language"][result.language] += 1

        # Update average time
        prev_avg = self.stats["avg_analysis_time_ms"]
        count = self.stats["total_analyses"]
        self.stats["avg_analysis_time_ms"] = (
            (prev_avg * (count - 1) + duration_ms) / count
        )


# Global instance
_global_ide_manager = IDEPluginManager()


def get_ide_plugin_manager() -> IDEPluginManager:
    """Get global IDE plugin manager"""
    return _global_ide_manager
