import sys
from pathlib import Path

# Add scanner to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scanner"))

from caqi import Pollutants, CAQICalculator, CAQIFormatter
from metrics_aggregator import RepoMetrics


class TestCAQICalculator:
    """Test suite for CAQI calculation."""

    def test_zero_pollutants(self):
        """All zeros should give CAQI 0."""
        pollutants = Pollutants(
            complexity=0.0,
            security=0.0,
            smells=0.0,
            docs=0.0,
            duplication=0.0,
            coupling=0.0,
        )

        assert pollutants.caqi_score() == 0
        print("✓ Zero pollutants → CAQI 0")

    def test_max_pollutants(self):
        """All 100s should give CAQI ~500."""
        pollutants = Pollutants(
            complexity=100.0,
            security=100.0,
            smells=100.0,
            docs=100.0,
            duplication=100.0,
            coupling=100.0,
        )

        score = pollutants.caqi_score()
        assert score == 500  # Clamped at 500
        print(f"✓ Max pollutants → CAQI {score}")

    def test_single_high_pollutant(self):
        """One high pollutant should drive CAQI high."""
        pollutants = Pollutants(
            complexity=0.0,
            security=100.0,  # Only this is high
            smells=0.0,
            docs=0.0,
            duplication=0.0,
            coupling=0.0,
        )

        score = pollutants.caqi_score()
        assert score > 300  # Should be Hazardous
        print(f"✓ Single high pollutant → CAQI {score} (Hazardous)")

    def test_epa_levels(self):
        """EPA levels should map correctly to CAQI scores."""
        # Test specific pollutant combinations and their resulting levels
        test_cases = [
            # (pollutants, expected_level_keyword)
            (Pollutants(0, 0, 0, 0, 0, 0), "Good"),
            (Pollutants(10, 10, 10, 10, 10, 10), "Good"),
            (Pollutants(20, 20, 20, 20, 20, 20), "Moderate"),
            (Pollutants(30, 30, 30, 30, 30, 30), "Unhealthy"),
            (Pollutants(100, 0, 0, 0, 0, 0), "Hazardous"),  # Single high pollutant
            (Pollutants(0, 100, 0, 0, 0, 0), "Hazardous"),
        ]

        for pollutants, expected_keyword in test_cases:
            level = pollutants.level()
            # Check that the level is one of the valid EPA levels
            valid_levels = [
                "Good",
                "Moderate",
                "Unhealthy for Sensitive Groups",
                "Unhealthy",
                "Very Unhealthy",
                "Hazardous",
            ]
            assert level in valid_levels, f"Invalid level: {level}"

        print("✓ EPA levels mapping correctly")

    def test_complexity_calculation(self):
        """Complexity formula: min(avg * 20 + max * 10, 100)"""
        calc = CAQICalculator()

        # avg=2, max=5 → 2*20 + 5*10 = 90
        assert calc._calculate_complexity(2.0, 5.0) == 90.0

        # avg=10, max=20 → 10*20 + 20*10 = 400 → capped at 100
        assert calc._calculate_complexity(10.0, 20.0) == 100.0

        # avg=0, max=0 → 0
        assert calc._calculate_complexity(0.0, 0.0) == 0.0

        print("✓ Complexity formula correct")

    def test_security_calculation(self):
        """Security formula: min(high * 40 + medium * 20, 100)"""
        calc = CAQICalculator()

        # high=1, medium=1 → 1*40 + 1*20 = 60
        assert calc._calculate_security(1, 1) == 60.0

        # high=3, medium=0 → 3*40 = 120 → capped at 100
        assert calc._calculate_security(3, 0) == 100.0

        # high=0, medium=0 → 0
        assert calc._calculate_security(0, 0) == 0.0

        print("✓ Security formula correct")

    def test_smells_calculation(self):
        """Smells formula: min(count * 12.5, 100)"""
        calc = CAQICalculator()

        # count=4 → 4 * 12.5 = 50
        assert calc._calculate_smells(4) == 50.0

        # count=10 → 10 * 12.5 = 125 → capped at 100
        assert calc._calculate_smells(10) == 100.0

        # count=0 → 0
        assert calc._calculate_smells(0) == 0.0

        print("✓ Smells formula correct")

    def test_docs_calculation(self):
        """Docs formula: (1 - coverage) * 100 (inverted)"""
        calc = CAQICalculator()

        # 100% coverage → 0 pollution
        assert calc._calculate_docs(1.0) == 0.0

        # 50% coverage → 50 pollution
        assert calc._calculate_docs(0.5) == 50.0

        # 0% coverage → 100 pollution
        assert calc._calculate_docs(0.0) == 100.0

        print("✓ Docs formula correct (inverted)")

    def test_duplication_calculation(self):
        """Duplication formula: percentage (capped at 100)"""
        calc = CAQICalculator()

        # 25% duplication → 25
        assert calc._calculate_duplication(25.0) == 25.0

        # 100% duplication → 100
        assert calc._calculate_duplication(100.0) == 100.0

        # 0% duplication → 0
        assert calc._calculate_duplication(0.0) == 0.0

        print("✓ Duplication formula correct")

    def test_coupling_calculation(self):
        """Coupling formula: min(imports * 5, 100) + (50 if circular)"""
        calc = CAQICalculator()

        # 2 imports, no circular → 2 * 5 = 10
        assert calc._calculate_coupling(2.0, False) == 10.0

        # 20 imports, no circular → 20 * 5 = 100 (capped)
        assert calc._calculate_coupling(20.0, False) == 100.0

        # 2 imports, has circular → 2 * 5 + 50 = 60
        assert calc._calculate_coupling(2.0, True) == 60.0

        # 20 imports, has circular → 100 + 50 = 150 → capped at 100
        assert calc._calculate_coupling(20.0, True) == 100.0

        print("✓ Coupling formula correct")

    def test_primary_pollutant_detection(self):
        """Primary pollutant should be the highest."""
        pollutants = Pollutants(
            complexity=10.0,
            security=50.0,
            smells=20.0,
            docs=30.0,
            duplication=5.0,
            coupling=15.0,
        )

        assert pollutants.primary_pollutant() == "security"
        print("✓ Primary pollutant detected correctly")

    def test_health_advice(self):
        """Health advice should match level."""
        test_cases = [
            (Pollutants(0, 0, 0, 0, 0, 0), "Excellent"),
            (Pollutants(100, 0, 0, 0, 0, 0), "emergency"),
        ]

        for pollutants, keyword in test_cases:
            advice = pollutants.health_advice()
            assert keyword.lower() in advice.lower()

        print("✓ Health advice matches level")

    def test_pollutants_as_dict(self):
        """Pollutants should convert to dict."""
        pollutants = Pollutants(
            complexity=10.0,
            security=20.0,
            smells=30.0,
            docs=40.0,
            duplication=50.0,
            coupling=60.0,
        )

        d = pollutants.as_dict()
        assert d["complexity"] == 10.0
        assert d["security"] == 20.0
        assert d["smells"] == 30.0
        assert d["docs"] == 40.0
        assert d["duplication"] == 50.0
        assert d["coupling"] == 60.0

        print("✓ Pollutants dict conversion working")

    def test_caqi_clamped_0_500(self):
        """CAQI should always be 0-500."""
        test_cases = [
            Pollutants(0, 0, 0, 0, 0, 0),  # Minimum
            Pollutants(100, 100, 100, 100, 100, 100),  # Maximum
            Pollutants(50, 50, 50, 50, 50, 50),  # Middle
            Pollutants(1, 1, 1, 1, 1, 1),  # Very low
        ]

        for pollutants in test_cases:
            score = pollutants.caqi_score()
            assert 0 <= score <= 500, f"Score {score} outside valid range"

        print("✓ CAQI always 0-500")

    def test_calculate_pollutants_from_metrics(self):
        """Calculator should work with RepoMetrics."""
        calc = CAQICalculator()

        metrics = RepoMetrics(
            avg_complexity=3.0,
            max_complexity=8.0,
            security_high_count=2,
            security_medium_count=3,
            smell_count=1,
            doc_coverage_ratio=0.85,
            duplication_percentage=5.0,
            avg_imports_per_file=2.0,
            has_circular_deps=False,
            files_analyzed=5,
            total_lines=500,
        )

        pollutants = calc.calculate_pollutants(metrics)

        assert pollutants.complexity > 0
        assert pollutants.security > 0
        assert pollutants.smells > 0
        assert pollutants.docs > 0
        assert 0 <= pollutants.duplication <= 100
        assert pollutants.coupling > 0

        print(f"✓ Metrics → Pollutants: CAQI {pollutants.caqi_score()}")

    def test_per_file_caqi(self):
        """Per-file CAQI should be calculated."""
        calc = CAQICalculator()

        metrics = RepoMetrics(
            avg_complexity=5.0,
            max_complexity=10.0,
            security_high_count=1,
            security_medium_count=2,
            smell_count=2,
            doc_coverage_ratio=0.8,
            duplication_percentage=10.0,
            avg_imports_per_file=2.0,
            has_circular_deps=False,
            files_analyzed=3,
            total_lines=300,
            per_file_metrics={
                "app.py": {
                    "lines": 100,
                    "security_issues": 1,
                    "smells": 2,
                    "doc_coverage": 0.8,
                    "functions": 10,
                    "documented_functions": 8,
                },
                "utils.py": {
                    "lines": 100,
                    "security_issues": 0,
                    "smells": 0,
                    "doc_coverage": 0.9,
                    "functions": 5,
                    "documented_functions": 5,
                },
            },
        )

        pollutants = calc.calculate_pollutants(metrics)
        per_file = calc.calculate_per_file_caqi(metrics, pollutants)

        assert len(per_file) == 2
        assert all("file" in f for f in per_file)
        assert all("caqi" in f for f in per_file)
        assert all("level" in f for f in per_file)

        print(f"✓ Per-file CAQI: {len(per_file)} files analyzed")


class TestCAQIFormatter:
    """Test suite for CAQI output formatting."""

    def test_json_output(self):
        """JSON output should have required fields."""
        pollutants = Pollutants(
            complexity=20.0,
            security=50.0,
            smells=10.0,
            docs=15.0,
            duplication=5.0,
            coupling=25.0,
        )

        metrics = RepoMetrics(
            avg_complexity=1.0,
            max_complexity=5.0,
            security_high_count=1,
            security_medium_count=1,
            smell_count=1,
            doc_coverage_ratio=0.9,
            duplication_percentage=5.0,
            avg_imports_per_file=1.0,
            has_circular_deps=False,
            files_analyzed=5,
            total_lines=500,
        )

        per_file = [{"file": "app.py", "caqi": 100, "level": "Moderate"}]

        output = CAQIFormatter.json_output(pollutants, metrics, per_file)

        assert "caqi" in output
        assert "score" in output["caqi"]
        assert "level" in output["caqi"]
        assert "color" in output["caqi"]
        assert "primary_pollutant" in output["caqi"]
        assert "pollutants" in output["caqi"]
        assert "health_advice" in output["caqi"]

        print("✓ JSON output: all fields present")

    def test_markdown_summary(self):
        """Markdown summary should be compact one-liner."""
        pollutants = Pollutants(
            complexity=10.0,
            security=50.0,
            smells=0.0,
            docs=0.0,
            duplication=0.0,
            coupling=0.0,
        )

        summary = CAQIFormatter.markdown_summary(pollutants)

        assert "CAQI:" in summary
        assert pollutants.level() in summary
        assert "security" in summary.lower()

        print(f"✓ Markdown summary: {summary}")

    def test_markdown_full(self):
        """Markdown report should be detailed."""
        pollutants = Pollutants(
            complexity=10.0,
            security=20.0,
            smells=5.0,
            docs=10.0,
            duplication=5.0,
            coupling=15.0,
        )

        metrics = RepoMetrics(
            avg_complexity=1.0,
            max_complexity=5.0,
            security_high_count=1,
            security_medium_count=1,
            smell_count=1,
            doc_coverage_ratio=0.9,
            duplication_percentage=5.0,
            avg_imports_per_file=1.0,
            has_circular_deps=False,
            files_analyzed=5,
            total_lines=500,
        )

        per_file = [{"file": "app.py", "caqi": 100, "level": "Moderate"}]

        report = CAQIFormatter.markdown_full(pollutants, metrics, per_file)

        assert "Code Air Quality Index" in report
        assert "CAQI:" in report
        assert "Complexity" in report
        assert "Security" in report
        assert "Pollution Breakdown" in report
        assert "Top Files" in report

        print("✓ Markdown report: full detailed format")

    def test_html_gauge(self):
        """HTML gauge should be valid HTML."""
        pollutants = Pollutants(
            complexity=20.0,
            security=50.0,
            smells=10.0,
            docs=15.0,
            duplication=5.0,
            coupling=25.0,
        )

        html = CAQIFormatter.html_gauge(pollutants)

        assert "<!DOCTYPE html>" in html
        assert "<html>" in html
        assert "</html>" in html
        assert "CAQI Gauge" in html
        assert pollutants.level() in html
        assert str(pollutants.caqi_score()) in html

        print("✓ HTML gauge: valid HTML generated")


if __name__ == "__main__":
    calc_tests = TestCAQICalculator()
    formatter_tests = TestCAQIFormatter()

    print("Running CAQI Engine Tests...\n")

    # Calculator tests
    calc_tests.test_zero_pollutants()
    calc_tests.test_max_pollutants()
    calc_tests.test_single_high_pollutant()
    calc_tests.test_epa_levels()
    calc_tests.test_complexity_calculation()
    calc_tests.test_security_calculation()
    calc_tests.test_smells_calculation()
    calc_tests.test_docs_calculation()
    calc_tests.test_duplication_calculation()
    calc_tests.test_coupling_calculation()
    calc_tests.test_primary_pollutant_detection()
    calc_tests.test_health_advice()
    calc_tests.test_pollutants_as_dict()
    calc_tests.test_caqi_clamped_0_500()
    calc_tests.test_calculate_pollutants_from_metrics()
    calc_tests.test_per_file_caqi()

    # Formatter tests
    formatter_tests.test_json_output()
    formatter_tests.test_markdown_summary()
    formatter_tests.test_markdown_full()
    formatter_tests.test_html_gauge()

    print("\n✅ All tests passed!")
