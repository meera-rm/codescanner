"""
Tests for Codebase Learner - Phase 6.1.1
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.codebase_learner import (
    CodebaseIntelligence,
    CodePatternType,
    CodePattern,
    RefactoringHistory
)


class TestCodebaseIntelligence:
    """Test codebase intelligence and pattern learning"""

    def test_extract_pattern(self):
        """Test extracting code pattern"""
        intelligence = CodebaseIntelligence()

        code = """def process_data(items):
    for item in items:
        if item['status'] == 'active':
            print(item['name'])
"""

        pattern = intelligence.extract_pattern(
            code=code,
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="process_data",
            complexity=5.2
        )

        assert pattern.pattern_id.startswith("pat_")
        assert pattern.name == "process_data"
        assert pattern.language == "python"
        assert pattern.complexity == 5.2

    def test_duplicate_pattern_detection(self):
        """Test detecting duplicate patterns"""
        intelligence = CodebaseIntelligence()

        code = "def hello(): return 'world'"

        pattern1 = intelligence.extract_pattern(
            code=code,
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="hello",
            complexity=1.0
        )

        pattern2 = intelligence.extract_pattern(
            code=code,
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="hello",
            complexity=1.0
        )

        assert pattern1.pattern_id == pattern2.pattern_id
        assert pattern1.occurrences == 2

    def test_record_refactoring(self):
        """Test recording refactoring outcome"""
        intelligence = CodebaseIntelligence()

        code = "def foo(): pass"
        pattern = intelligence.extract_pattern(
            code=code,
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="foo",
            complexity=1.0
        )

        history = intelligence.record_refactoring(
            pattern_id=pattern.pattern_id,
            original_code=code,
            refactored_code="def foo() -> None: pass",
            quality_improvement=0.15,
            complexity_change=-0.5,
            performance_impact="neutral"
        )

        assert history.history_id.startswith("hist_")
        assert history.quality_improvement == 0.15
        assert history.complexity_change == -0.5

    def test_get_pattern_recommendations(self):
        """Test getting recommendations for pattern"""
        intelligence = CodebaseIntelligence()

        code = "def process(): pass"
        pattern = intelligence.extract_pattern(
            code=code,
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="process",
            complexity=2.0
        )

        # Record successful refactoring
        intelligence.record_refactoring(
            pattern_id=pattern.pattern_id,
            original_code=code,
            refactored_code="def process() -> None: pass",
            quality_improvement=0.25,
            complexity_change=0,
            performance_impact="improved"
        )

        recommendations = intelligence.get_pattern_recommendations(pattern.pattern_id)

        assert len(recommendations) > 0
        assert recommendations[0]["quality_improvement"] == 0.25
        assert recommendations[0]["performance_impact"] == "improved"

    def test_search_similar_patterns(self):
        """Test finding similar patterns"""
        intelligence = CodebaseIntelligence()

        code1 = """def filter_items(items):
    result = []
    for item in items:
        if item['status'] == 'active':
            result.append(item)
    return result
"""

        code2 = """def find_active(data):
    output = []
    for entry in data:
        if entry['status'] == 'active':
            output.append(entry)
    return output
"""

        p1 = intelligence.extract_pattern(
            code=code1,
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="filter_items",
            complexity=5.0
        )

        p2 = intelligence.extract_pattern(
            code=code2,
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="find_active",
            complexity=5.0
        )

        similar = intelligence.search_similar_patterns(code1, "python", limit=5)

        assert len(similar) > 0
        assert any(s["pattern_id"] == p2.pattern_id for s in similar)

    def test_language_stats(self):
        """Test language statistics tracking"""
        intelligence = CodebaseIntelligence()

        intelligence.extract_pattern(
            code="def foo(): pass",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="foo",
            complexity=1.0
        )

        intelligence.extract_pattern(
            code="def bar(): pass",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="bar",
            complexity=2.0
        )

        stats = intelligence.language_stats["python"]

        assert stats["total_patterns"] == 2
        assert stats["avg_complexity"] == 1.5

    def test_codebase_insights(self):
        """Test codebase insights generation"""
        intelligence = CodebaseIntelligence()

        intelligence.extract_pattern(
            code="def process(): pass",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="process",
            complexity=3.0
        )

        insights = intelligence.get_codebase_insights("python")

        assert insights["language"] == "python"
        assert insights["total_patterns"] == 1
        assert insights["avg_complexity"] == 3.0

    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        intelligence = CodebaseIntelligence()

        pattern = intelligence.extract_pattern(
            code="def test(): pass",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="test",
            complexity=1.0
        )

        # Record successful refactorings
        intelligence.record_refactoring(
            pattern_id=pattern.pattern_id,
            original_code="def test(): pass",
            refactored_code="def test() -> None: pass",
            quality_improvement=0.2,
            complexity_change=0,
            performance_impact="neutral"
        )

        intelligence.record_refactoring(
            pattern_id=pattern.pattern_id,
            original_code="def test(): pass",
            refactored_code="def test() -> None: pass",
            quality_improvement=0.3,
            complexity_change=0,
            performance_impact="improved"
        )

        # Record failed refactoring
        intelligence.record_refactoring(
            pattern_id=pattern.pattern_id,
            original_code="def test(): pass",
            refactored_code="def test_new(): pass",
            quality_improvement=-0.1,
            complexity_change=1,
            performance_impact="degraded"
        )

        success_rate = intelligence._calculate_success_rate(pattern.pattern_id)

        assert success_rate == pytest.approx(2/3, rel=0.01)

    def test_pattern_metadata(self):
        """Test pattern metadata storage"""
        intelligence = CodebaseIntelligence()

        metadata = {
            "file": "utils.py",
            "line_number": 42,
            "cyclomatic_complexity": 5
        }

        pattern = intelligence.extract_pattern(
            code="def helper(): pass",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="helper",
            complexity=1.0,
            metadata=metadata
        )

        assert pattern.metadata["file"] == "utils.py"
        assert pattern.metadata["line_number"] == 42

    def test_pattern_to_dict(self):
        """Test pattern serialization"""
        intelligence = CodebaseIntelligence()

        pattern = intelligence.extract_pattern(
            code="def test(): pass",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="test",
            complexity=1.0
        )

        pattern_dict = pattern.to_dict()

        assert pattern_dict["pattern_type"] == "function"
        assert pattern_dict["name"] == "test"
        assert "fingerprint" in pattern_dict

    def test_multiple_languages(self):
        """Test handling multiple languages"""
        intelligence = CodebaseIntelligence()

        # Python pattern
        intelligence.extract_pattern(
            code="def foo(): pass",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="foo",
            complexity=1.0
        )

        # JavaScript pattern
        intelligence.extract_pattern(
            code="function bar() {}",
            pattern_type=CodePatternType.FUNCTION,
            language="javascript",
            name="bar",
            complexity=1.0
        )

        # TypeScript pattern
        intelligence.extract_pattern(
            code="function baz(): void {}",
            pattern_type=CodePatternType.FUNCTION,
            language="typescript",
            name="baz",
            complexity=1.0
        )

        python_stats = intelligence.language_stats.get("python")
        js_stats = intelligence.language_stats.get("javascript")
        ts_stats = intelligence.language_stats.get("typescript")

        assert python_stats["total_patterns"] == 1
        assert js_stats["total_patterns"] == 1
        assert ts_stats["total_patterns"] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
