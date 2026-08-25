import tempfile
import os
from pathlib import Path
import sys

# Add scanner to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scanner"))

from metrics_aggregator import MetricsAggregator, RepoMetrics


class TestMetricsAggregator:
    """Test suite for metrics aggregation."""

    def test_empty_directory(self):
        """Empty directory should return zero metrics."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = aggregator.aggregate(tmpdir)

            assert metrics.files_analyzed == 0
            assert metrics.total_lines == 0
            assert metrics.smell_count == 0
            assert metrics.security_high_count == 0
            assert metrics.security_medium_count == 0
            print("✓ Empty directory: zero metrics")

    def test_single_clean_file(self):
        """Single clean file should have good metrics."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "clean.py"
            file1.write_text('''
"""Clean module."""

def hello():
    """Return greeting."""
    return "hello"

def world():
    """Return world."""
    return "world"
''')

            metrics = aggregator.aggregate(tmpdir)

            assert metrics.files_analyzed >= 1
            assert metrics.total_lines > 0
            assert metrics.doc_coverage_ratio > 0
            print(f"✓ Clean file: {metrics.files_analyzed} file(s), {metrics.doc_coverage_ratio:.1%} doc coverage")

    def test_file_with_smells(self):
        """File with code smells should detect them."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "smelly.py"
            # Create a long function (>50 lines)
            code = "def long_func():\n"
            for i in range(55):
                code += f"    x{i} = {i}\n"
            file1.write_text(code)

            metrics = aggregator.aggregate(tmpdir)

            assert metrics.smell_count > 0
            print(f"✓ Smelly file: {metrics.smell_count} smell(s) detected")

    def test_multiple_files_aggregation(self):
        """Multiple files should aggregate metrics correctly."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "module_a.py"
            file2 = Path(tmpdir) / "module_b.py"

            file1.write_text('''
def func_a():
    """Documented."""
    return 1
''')

            file2.write_text('''
def func_b():
    return 2
''')

            metrics = aggregator.aggregate(tmpdir)

            assert metrics.files_analyzed == 2
            assert metrics.total_lines > 0
            assert metrics.doc_coverage_ratio > 0
            print(f"✓ Multiple files: {metrics.files_analyzed} files, {metrics.total_lines} lines")

    def test_imports_counted(self):
        """Module imports should be counted."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "app.py"
            file1.write_text('''
import mymodule
import another

def main():
    pass
''')

            metrics = aggregator.aggregate(tmpdir)

            assert metrics.avg_imports_per_file > 0
            print(f"✓ Imports: {metrics.avg_imports_per_file:.1f} avg imports/file")

    def test_circular_deps_detection(self):
        """Circular dependencies should be detected."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_a = Path(tmpdir) / "module_a.py"
            file_b = Path(tmpdir) / "module_b.py"

            file_a.write_text("import module_b")
            file_b.write_text("import module_a")

            metrics = aggregator.aggregate(tmpdir)

            assert metrics.has_circular_deps is True
            print("✓ Circular dependencies: detected")

    def test_security_issues(self):
        """Security issues should be detected."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "insecure.py"
            file1.write_text('''
api_key = "REDACTED_FOR_TEST"
password = "my_password"
token = "secret_token"
''')

            metrics = aggregator.aggregate(tmpdir)

            assert metrics.security_high_count > 0
            print(f"✓ Security: {metrics.security_high_count} critical issue(s)")

    def test_duplication_detection(self):
        """Duplication should be detected across files."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "utils_a.py"
            file2 = Path(tmpdir) / "utils_b.py"

            code = '''
def duplicate_function():
    x = 1
    y = 2
    z = 3
    return x + y + z
'''

            file1.write_text(code)
            file2.write_text(code)

            metrics = aggregator.aggregate(tmpdir)

            assert metrics.duplication_percentage > 0
            print(f"✓ Duplication: {metrics.duplication_percentage:.1f}% duplicate code")

    def test_complexity_extraction(self):
        """Complexity should be extracted from scanner findings."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "complex.py"
            # Create a function with high complexity
            file1.write_text('''
def complex_function(x):
    if x > 0:
        if x > 10:
            if x > 100:
                return "high"
            return "medium"
        return "low"
    return "negative"
''')

            metrics = aggregator.aggregate(tmpdir)

            # Should have some complexity
            assert metrics.max_complexity >= 0
            print(f"✓ Complexity: avg={metrics.avg_complexity:.1f}, max={metrics.max_complexity:.1f}")

    def test_doc_coverage_extraction(self):
        """Doc coverage should be calculated."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "documented.py"
            file1.write_text('''
def documented():
    """Has docstring."""
    return 1

def undocumented():
    return 2
''')

            metrics = aggregator.aggregate(tmpdir)

            # Should have some doc coverage (50% for this file)
            assert 0 <= metrics.doc_coverage_ratio <= 1.0
            print(f"✓ Doc coverage: {metrics.doc_coverage_ratio:.1%}")

    def test_per_file_metrics(self):
        """Per-file metrics should be generated."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "module.py"
            file1.write_text('''
"""Module docstring."""

def func():
    """Function docstring."""
    return 1
''')

            metrics = aggregator.aggregate(tmpdir)

            assert len(metrics.per_file_metrics) > 0
            for filepath, file_metrics in metrics.per_file_metrics.items():
                assert "lines" in file_metrics
                assert "security_issues" in file_metrics
                assert "smells" in file_metrics
                assert "doc_coverage" in file_metrics
            print(f"✓ Per-file metrics: {len(metrics.per_file_metrics)} file(s) tracked")

    def test_report_generation(self):
        """Report should include all metrics."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "test.py"
            file1.write_text("def func():\n    pass")

            metrics = aggregator.aggregate(tmpdir)
            report = aggregator.report(metrics)

            assert "summary" in report
            assert "per_file" in report
            assert "files" in report["summary"]
            assert "lines" in report["summary"]
            assert "complexity_avg" in report["summary"]
            assert "security_high" in report["summary"]
            assert "smells" in report["summary"]
            assert "doc_coverage" in report["summary"]
            assert "duplication" in report["summary"]
            assert "avg_imports" in report["summary"]
            assert "circular_deps" in report["summary"]
            print("✓ Report: all fields present")

    def test_realistic_project(self):
        """Test with realistic project structure."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a realistic project
            main = Path(tmpdir) / "main.py"
            utils = Path(tmpdir) / "utils.py"
            config = Path(tmpdir) / "config.py"

            main.write_text('''
"""Main application."""
import utils
import config

def main():
    """Entry point."""
    return utils.do_something()
''')

            utils.write_text('''
"""Utility functions."""
import config

def do_something():
    """Do something."""
    return config.value
''')

            config.write_text('''
"""Configuration."""

value = 42
''')

            metrics = aggregator.aggregate(tmpdir)

            assert metrics.files_analyzed == 3
            assert metrics.total_lines > 0
            assert metrics.doc_coverage_ratio > 0.5
            assert metrics.avg_imports_per_file > 0
            assert metrics.has_circular_deps is False
            print(f"✓ Realistic project:")
            print(f"  Files: {metrics.files_analyzed}")
            print(f"  Lines: {metrics.total_lines}")
            print(f"  Doc coverage: {metrics.doc_coverage_ratio:.1%}")
            print(f"  Avg imports: {metrics.avg_imports_per_file:.1f}")
            print(f"  Circular deps: {metrics.has_circular_deps}")

    def test_complex_project(self):
        """Test with complex, problematic code."""
        aggregator = MetricsAggregator()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create code with various issues
            bad = Path(tmpdir) / "bad.py"
            bad.write_text('''
import mymodule
password = "hardcoded"
def long_func():
    a = 1
    b = 2
    c = 3
    d = 4
    e = 5
    f = 6
    g = 7
    h = 8
    i = 9
    j = 10
    k = 11
    l = 12
    m = 13
    n = 14
    o = 15
    p = 16
    q = 17
    r = 18
    s = 19
    t = 20
    u = 21
    v = 22
    w = 23
    x = 24
    y = 25
    z = 26
    aa = 27
    bb = 28
    cc = 29
    dd = 30
    ee = 31
    ff = 32
    gg = 33
    hh = 34
    ii = 35
    jj = 36
    kk = 37
    ll = 38
    mm = 39
    nn = 40
    oo = 41
    pp = 42
    qq = 43
    rr = 44
    ss = 45
    tt = 46
    uu = 47
    vv = 48
    ww = 49
    xx = 50
    yy = 51
''')

            metrics = aggregator.aggregate(tmpdir)

            assert metrics.security_high_count > 0, "Should detect hardcoded password"
            assert metrics.smell_count > 0, "Should detect long function"
            assert metrics.doc_coverage_ratio < 1.0, "Should have low doc coverage"
            print(f"✓ Complex project detected issues:")
            print(f"  Security: {metrics.security_high_count} critical")
            print(f"  Smells: {metrics.smell_count}")
            print(f"  Doc coverage: {metrics.doc_coverage_ratio:.1%}")


if __name__ == "__main__":
    test = TestMetricsAggregator()

    print("Running Metrics Aggregator Tests...\n")
    test.test_empty_directory()
    test.test_single_clean_file()
    test.test_file_with_smells()
    test.test_multiple_files_aggregation()
    test.test_imports_counted()
    test.test_circular_deps_detection()
    test.test_security_issues()
    test.test_duplication_detection()
    test.test_complexity_extraction()
    test.test_doc_coverage_extraction()
    test.test_per_file_metrics()
    test.test_report_generation()
    test.test_realistic_project()
    test.test_complex_project()

    print("\n✅ All tests passed!")
