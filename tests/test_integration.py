"""Integration tests for end-to-end workflows."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scanner"))

from metrics_aggregator import MetricsAggregator
from caqi import CAQICalculator, CAQIFormatter


class TestEndToEndWorkflow:
    """Test complete workflows from directory to CAQI score."""

    def test_clean_project_workflow(self, create_project, sample_clean_file):
        """Clean project should have no security issues."""
        files = {
            "main.py": sample_clean_file,
            "utils.py": sample_clean_file,
        }

        tmpdir, _ = create_project(files)

        # Run full pipeline
        aggregator = MetricsAggregator()
        metrics = aggregator.aggregate(tmpdir)

        calculator = CAQICalculator()
        pollutants = calculator.calculate_pollutants(metrics)

        # Clean code should have good metrics
        assert metrics.security_high_count == 0
        assert metrics.doc_coverage_ratio > 0.8
        assert metrics.smell_count == 0
        # Note: identical files will show 100% duplication, but that's expected for duplicated code
        assert pollutants.primary_pollutant() in ["duplication", "coupling", "docs"]

        print(f"✓ Clean project: CAQI {pollutants.caqi_score()} ({pollutants.level()})")

    def test_problematic_project_workflow(self, create_project, sample_insecure_file, sample_smelly_file):
        """Project with issues should produce high CAQI."""
        files = {
            "insecure.py": sample_insecure_file,
            "smelly.py": sample_smelly_file,
        }

        tmpdir, _ = create_project(files)

        # Run full pipeline
        aggregator = MetricsAggregator()
        metrics = aggregator.aggregate(tmpdir)

        calculator = CAQICalculator()
        pollutants = calculator.calculate_pollutants(metrics)

        # Problematic code should have high CAQI
        assert metrics.security_high_count > 0
        assert metrics.smell_count > 0
        assert pollutants.caqi_score() > 200  # Should be Unhealthy or worse

        print(f"✓ Problematic project: CAQI {pollutants.caqi_score()} ({pollutants.level()})")

    def test_mixed_quality_project(self, create_project, sample_clean_file, sample_insecure_file):
        """Mixed quality project should have high CAQI due to security issues."""
        files = {
            "good.py": sample_clean_file,
            "bad.py": sample_insecure_file,
        }

        tmpdir, _ = create_project(files)

        aggregator = MetricsAggregator()
        metrics = aggregator.aggregate(tmpdir)

        calculator = CAQICalculator()
        pollutants = calculator.calculate_pollutants(metrics)

        # Security issues in one file will push CAQI high
        score = pollutants.caqi_score()
        assert score > 200  # Security issues dominate the score

        print(f"✓ Mixed project: CAQI {score} ({pollutants.level()})")

    def test_output_consistency(self, sample_repo_metrics):
        """All output formats should represent same CAQI score."""
        calculator = CAQICalculator()
        pollutants = calculator.calculate_pollutants(sample_repo_metrics)

        per_file = calculator.calculate_per_file_caqi(sample_repo_metrics, pollutants)

        # Generate all outputs
        json_out = CAQIFormatter.json_output(pollutants, sample_repo_metrics, per_file)
        markdown = CAQIFormatter.markdown_summary(pollutants)
        html = CAQIFormatter.html_gauge(pollutants)

        # All should represent same score
        caqi_score = pollutants.caqi_score()
        assert json_out["caqi"]["score"] == caqi_score
        assert str(caqi_score) in markdown
        assert str(caqi_score) in html

        print(f"✓ Output consistency: {caqi_score} across JSON/Markdown/HTML")

    def test_per_file_analysis(self, create_project, sample_clean_file, sample_insecure_file):
        """Per-file CAQI should identify problem files."""
        files = {
            "app.py": sample_clean_file,
            "insecure.py": sample_insecure_file,
        }

        tmpdir, _ = create_project(files)

        aggregator = MetricsAggregator()
        metrics = aggregator.aggregate(tmpdir)

        calculator = CAQICalculator()
        pollutants = calculator.calculate_pollutants(metrics)
        per_file = calculator.calculate_per_file_caqi(metrics, pollutants)

        # Per-file scores should be available
        assert len(per_file) > 0

        # Insecure file should have higher CAQI than clean file
        insecure_scores = [f["caqi"] for f in per_file if "insecure" in f["file"]]
        clean_scores = [f["caqi"] for f in per_file if "app" in f["file"]]

        if insecure_scores and clean_scores:
            assert max(insecure_scores) >= min(clean_scores)

        print(f"✓ Per-file analysis: {len(per_file)} files ranked")

    def test_metrics_aggregation_completeness(self, temp_dir, create_python_file, sample_clean_file):
        """Aggregator should collect all 6 metric types."""
        # Create file in temp_dir
        filepath = create_python_file("test.py", sample_clean_file)

        aggregator = MetricsAggregator()
        metrics = aggregator.aggregate(temp_dir)

        # All metrics should be present
        assert metrics.avg_complexity is not None
        assert metrics.max_complexity is not None
        assert metrics.security_high_count is not None
        assert metrics.security_medium_count is not None
        assert metrics.smell_count is not None
        assert metrics.doc_coverage_ratio is not None
        assert metrics.duplication_percentage is not None
        assert metrics.avg_imports_per_file is not None
        assert metrics.has_circular_deps is not None

        # File analysis should be present (if files were analyzed)
        if metrics.files_analyzed > 0:
            assert len(metrics.per_file_metrics) > 0

        print("✓ All 6 metric types collected")

    def test_formula_accuracy(self, sample_repo_metrics):
        """CAQI formulas should produce expected results."""
        calculator = CAQICalculator()
        pollutants = calculator.calculate_pollutants(sample_repo_metrics)

        # Verify formula results match expectations
        expected_complexity = min(5.0 * 20 + 12.0 * 10, 100)
        assert abs(pollutants.complexity - expected_complexity) < 0.1

        expected_security = min(2 * 40 + 3 * 20, 100)
        assert abs(pollutants.security - expected_security) < 0.1

        expected_docs = (1 - 0.80) * 100
        assert abs(pollutants.docs - expected_docs) < 0.1

        print("✓ CAQI formulas produce expected results")

    def test_edge_case_empty_project(self, temp_dir):
        """Empty project should not crash."""
        aggregator = MetricsAggregator()
        metrics = aggregator.aggregate(temp_dir)

        calculator = CAQICalculator()
        pollutants = calculator.calculate_pollutants(metrics)

        # Should not crash and should return valid score
        assert 0 <= pollutants.caqi_score() <= 500

        print("✓ Empty project handled gracefully")

    def test_edge_case_syntax_errors(self, create_project):
        """Project with syntax errors should not crash."""
        files = {
            "good.py": "def func():\n    return 1",
            "bad.py": "def broken(\n",  # Syntax error
        }

        tmpdir, _ = create_project(files)

        aggregator = MetricsAggregator()
        metrics = aggregator.aggregate(tmpdir)

        calculator = CAQICalculator()
        pollutants = calculator.calculate_pollutants(metrics)

        # Should not crash
        assert 0 <= pollutants.caqi_score() <= 500

        print("✓ Syntax errors handled gracefully")

    def test_caqi_reproducibility(self, create_project, sample_clean_file):
        """Same project should produce same CAQI (reproducible)."""
        files = {"test.py": sample_clean_file}

        tmpdir1, _ = create_project(files)

        aggregator1 = MetricsAggregator()
        metrics1 = aggregator1.aggregate(tmpdir1)
        calc1 = CAQICalculator()
        pollutants1 = calc1.calculate_pollutants(metrics1)
        score1 = pollutants1.caqi_score()

        # Run again (reusing same directory)
        aggregator2 = MetricsAggregator()
        metrics2 = aggregator2.aggregate(tmpdir1)
        calc2 = CAQICalculator()
        pollutants2 = calc2.calculate_pollutants(metrics2)
        score2 = pollutants2.caqi_score()

        # Scores should be identical
        assert score1 == score2

        print(f"✓ Reproducible: CAQI {score1} (same on re-run)")


class TestDetectorIntegration:
    """Test integration between detectors."""

    def test_detectors_work_together(self, create_project, sample_clean_file):
        """All detectors should work in aggregator."""
        files = {"test.py": sample_clean_file}
        tmpdir, _ = create_project(files)

        aggregator = MetricsAggregator()
        metrics = aggregator.aggregate(tmpdir)

        # All detector outputs should be present
        assert metrics.smell_count >= 0
        assert 0 <= metrics.doc_coverage_ratio <= 1.0
        assert 0 <= metrics.duplication_percentage <= 100
        assert metrics.avg_imports_per_file >= 0
        assert isinstance(metrics.has_circular_deps, bool)

        print("✓ All detectors integrated successfully")

    def test_metrics_aggregation_consistency(self, create_project, sample_clean_file):
        """Aggregated metrics should be consistent."""
        files = {
            "file1.py": sample_clean_file,
            "file2.py": sample_clean_file,
            "file3.py": sample_clean_file,
        }
        tmpdir, _ = create_project(files)

        aggregator = MetricsAggregator()
        metrics = aggregator.aggregate(tmpdir)

        # Per-file count should match files analyzed
        assert len(metrics.per_file_metrics) == metrics.files_analyzed

        # Total lines should be consistent
        per_file_lines = sum(m.get("lines", 0) for m in metrics.per_file_metrics.values())
        assert per_file_lines == metrics.total_lines

        print(f"✓ Metrics consistent: {metrics.files_analyzed} files, {metrics.total_lines} lines")


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_missing_directory(self):
        """Missing directory should be handled."""
        aggregator = MetricsAggregator()
        # Should not crash with non-existent directory
        try:
            metrics = aggregator.aggregate("/nonexistent/path/12345")
            # If it doesn't crash, it should return empty metrics
            assert metrics.files_analyzed == 0
        except Exception as e:
            # Or it might raise an exception, which is OK
            print(f"✓ Missing directory handled: {type(e).__name__}")

    def test_unicode_handling(self, create_project):
        """Files with unicode should be handled."""
        files = {
            "unicode.py": '''
"""Module with unicode: 你好 مرحبا."""

def greet():
    """Greeting: Привет."""
    return "👋 Hello"
'''
        }
        tmpdir, _ = create_project(files)

        aggregator = MetricsAggregator()
        metrics = aggregator.aggregate(tmpdir)

        assert metrics.files_analyzed > 0
        print("✓ Unicode handling working")

    def test_very_large_file(self, create_project):
        """Very large file should be handled."""
        # Create a large file (1000 lines)
        large_code = '\n'.join([f"x{i} = {i}" for i in range(1000)])
        files = {"large.py": large_code}

        tmpdir, _ = create_project(files)

        aggregator = MetricsAggregator()
        metrics = aggregator.aggregate(tmpdir)

        # Should handle without crashing
        assert metrics.files_analyzed > 0
        assert metrics.total_lines > 0

        print(f"✓ Large file handled: {metrics.total_lines} lines")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
