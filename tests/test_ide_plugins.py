"""
Tests for IDE Plugins - Phase 6.2.4
"""

import pytest
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.ide_plugins import (
    IDEPluginManager,
    IDEType,
    AnalysisType,
    PluginConfig
)


class TestIDEPluginManager:
    """Test IDE plugin manager"""

    def test_register_plugin(self):
        """Test registering IDE plugin"""
        manager = IDEPluginManager()

        session = manager.register_plugin(
            ide_type=IDEType.VS_CODE,
            version="1.0.0",
            user_id="user123"
        )

        assert session.session_id.startswith("session_")
        assert session.ide_type == IDEType.VS_CODE
        assert session.plugin_version == "1.0.0"
        assert session.is_active is True

    def test_register_multiple_plugins(self):
        """Test registering multiple plugins"""
        manager = IDEPluginManager()

        vscode = manager.register_plugin(IDEType.VS_CODE, "1.0.0")
        jetbrains = manager.register_plugin(IDEType.JETBRAINS, "2.0.0")
        sublime = manager.register_plugin(IDEType.SUBLIME, "1.5.0")

        assert len(manager.sessions) == 3
        assert vscode.ide_type == IDEType.VS_CODE
        assert jetbrains.ide_type == IDEType.JETBRAINS
        assert sublime.ide_type == IDEType.SUBLIME

    def test_configure_plugin(self):
        """Test configuring plugin settings"""
        manager = IDEPluginManager()

        session = manager.register_plugin(IDEType.VS_CODE, "1.0.0")

        config = manager.configure_plugin(
            session.session_id,
            auto_analysis=True,
            real_time_feedback=True,
            analysis_type=AnalysisType.COMPREHENSIVE,
            debounce_ms=1000
        )

        assert config is not None
        assert config.auto_analysis is True
        assert config.analysis_type == AnalysisType.COMPREHENSIVE
        assert config.debounce_ms == 1000

    def test_analyze_file(self):
        """Test analyzing a file"""
        manager = IDEPluginManager()

        session = manager.register_plugin(IDEType.VS_CODE, "1.0.0")

        code = """
def process_data(data):
    result = []
    for item in data:
        if item is not None:
            processed = item.strip().lower()
            result.append(processed)
    return result
"""

        result = manager.analyze_file(
            session.session_id,
            "utils.py",
            code,
            "python"
        )

        assert result is not None
        assert result.analysis_id.startswith("analysis_")
        assert result.language == "python"
        assert result.quality_score >= 0 and result.quality_score <= 100
        assert len(result.issues) >= 0
        assert len(result.suggestions) >= 0

    def test_quality_score_calculation(self):
        """Test quality score calculation"""
        manager = IDEPluginManager()

        session = manager.register_plugin(IDEType.VS_CODE, "1.0.0")

        # Simple, clean code
        clean_code = "def add(a, b):\n    return a + b"

        result = manager.analyze_file(
            session.session_id,
            "math.py",
            clean_code,
            "python"
        )

        assert result.quality_score > 80

    def test_quick_feedback(self):
        """Test quick feedback without full analysis"""
        manager = IDEPluginManager()

        session = manager.register_plugin(IDEType.VS_CODE, "1.0.0")

        code = "x = 1 \n"  # Trailing whitespace

        feedback = manager.get_quick_feedback(
            session.session_id,
            "test.py",
            code,
            "python"
        )

        assert feedback["file_path"] == "test.py"
        assert feedback["language"] == "python"
        assert feedback["issue_count"] >= 0

    def test_heartbeat(self):
        """Test session heartbeat"""
        manager = IDEPluginManager()

        session = manager.register_plugin(IDEType.VS_CODE, "1.0.0")
        initial_heartbeat = session.last_heartbeat

        time.sleep(0.1)
        success = manager.heartbeat(session.session_id)

        assert success is True
        assert session.last_heartbeat > initial_heartbeat

    def test_close_session(self):
        """Test closing session"""
        manager = IDEPluginManager()

        session = manager.register_plugin(IDEType.VS_CODE, "1.0.0")

        assert session.is_active is True
        success = manager.close_session(session.session_id)

        assert success is True
        assert session.is_active is False

    def test_session_status(self):
        """Test getting session status"""
        manager = IDEPluginManager()

        session = manager.register_plugin(IDEType.VS_CODE, "1.0.0")
        manager.configure_plugin(session.session_id, auto_analysis=True)

        status = manager.get_session_status(session.session_id)

        assert status is not None
        assert status["session"]["ide_type"] == "vscode"
        assert status["config"]["auto_analysis"] is True
        assert "is_connected" in status

    def test_analysis_history(self):
        """Test getting analysis history"""
        manager = IDEPluginManager()

        session = manager.register_plugin(IDEType.VS_CODE, "1.0.0")

        # Run multiple analyses
        for i in range(3):
            manager.analyze_file(
                session.session_id,
                f"file{i}.py",
                "x = 1",
                "python"
            )

        history = manager.get_analysis_history(session.session_id)

        assert len(history) >= 3

    def test_statistics(self):
        """Test getting statistics"""
        manager = IDEPluginManager()

        session1 = manager.register_plugin(IDEType.VS_CODE, "1.0.0")
        session2 = manager.register_plugin(IDEType.JETBRAINS, "2.0.0")

        # Run analyses
        manager.analyze_file(session1.session_id, "test.py", "x = 1", "python")
        manager.analyze_file(session2.session_id, "test.js", "var x = 1;", "javascript")

        stats = manager.get_statistics()

        assert stats["total_analyses"] == 2
        assert stats["active_sessions"] == 2
        assert "python" in stats["by_language"]
        assert "javascript" in stats["by_language"]

    def test_complexity_calculation(self):
        """Test complexity calculation"""
        manager = IDEPluginManager()

        simple = "x = 1"
        complex_code = """
if condition1:
    for item in items:
        while True:
            try:
                if check:
                    pass
            except:
                pass
"""

        simple_complexity = manager._calculate_complexity(simple)
        complex_complexity = manager._calculate_complexity(complex_code)

        assert complex_complexity > simple_complexity

    def test_issue_detection(self):
        """Test issue detection"""
        manager = IDEPluginManager()

        code_with_issues = """
def process():
    x = 1                                                                                                 
    y = 2  
"""

        issues = manager._detect_issues(code_with_issues, "python")

        assert len(issues) > 0
        assert any(i["code"] == "line-length" for i in issues)
        assert any(i["code"] == "trailing-whitespace" for i in issues)

    def test_metrics_calculation(self):
        """Test metrics calculation"""
        manager = IDEPluginManager()

        code = "def test():\n    pass\n\n"

        metrics = manager._calculate_metrics(code, "python")

        assert "lines_of_code" in metrics
        assert "cyclomatic_complexity" in metrics
        assert "avg_line_length" in metrics
        assert metrics["blank_line_ratio"] >= 0

    def test_plugin_config_serialization(self):
        """Test plugin config to dict"""
        config = PluginConfig(
            plugin_id="plugin_123",
            ide_type=IDEType.VS_CODE,
            auto_analysis=True,
            analysis_type=AnalysisType.COMPREHENSIVE
        )

        config_dict = config.to_dict()

        assert config_dict["plugin_id"] == "plugin_123"
        assert config_dict["ide_type"] == "vscode"
        assert config_dict["auto_analysis"] is True
        assert config_dict["analysis_type"] == "comprehensive"

    def test_invalid_session(self):
        """Test operations with invalid session"""
        manager = IDEPluginManager()

        result = manager.analyze_file("invalid_session", "test.py", "x=1", "python")
        assert result is None

        status = manager.get_session_status("invalid_session")
        assert status is None

    def test_all_ide_types(self):
        """Test all IDE types"""
        manager = IDEPluginManager()

        for ide_type in IDEType:
            session = manager.register_plugin(ide_type, "1.0.0")
            assert session.ide_type == ide_type

    def test_analysis_count_increment(self):
        """Test analysis count increments"""
        manager = IDEPluginManager()

        session = manager.register_plugin(IDEType.VS_CODE, "1.0.0")

        assert session.analysis_count == 0

        manager.analyze_file(session.session_id, "test.py", "x=1", "python")
        assert session.analysis_count == 1

        manager.analyze_file(session.session_id, "test.py", "x=1", "python")
        assert session.analysis_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
