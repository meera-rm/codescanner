import tempfile
import os
from pathlib import Path
import sys

# Add scanner to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scanner"))

from coupling import CouplingDetector, CouplingMetrics


class TestCouplingDetector:
    """Test suite for coupling detection."""

    def test_simple_imports(self):
        """Simple imports should be detected."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "module_a.py"
            file2 = Path(tmpdir) / "module_b.py"

            file1.write_text('''
import json
import os
import custom_module
''')

            file2.write_text('''
import sys
import module_a
''')

            metrics = detector.analyze_directory(tmpdir)

            assert metrics.files_analyzed >= 1
            assert metrics.total_imports > 0
            assert metrics.avg_imports_per_file > 0
            print(f"✓ Simple imports: {metrics.total_imports} imports, avg {metrics.avg_imports_per_file:.1f}/file")

    def test_from_imports(self):
        """from X import Y style imports should be detected."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "main.py"

            file1.write_text('''
from os import path
from pathlib import Path
from mymodule import helper
from another.module import func
''')

            metrics = detector.analyze_directory(tmpdir)

            assert metrics.total_imports > 0
            print(f"✓ From imports: {metrics.total_imports} imports detected")

    def test_stdlib_filtering(self):
        """Standard library imports should be filtered out."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "app.py"

            file1.write_text('''
import os
import sys
import json
import my_custom_module
import another_custom
''')

            metrics = detector.analyze_directory(tmpdir)

            # Should only count custom_module and another_custom
            # os, sys, json are stdlib and filtered
            assert metrics.total_imports == 2
            print(f"✓ Stdlib filtering: {metrics.total_imports} custom imports (stdlib filtered)")

    def test_no_imports(self):
        """File with no imports should be handled."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "standalone.py"

            file1.write_text('''
def function():
    return 42
''')

            metrics = detector.analyze_directory(tmpdir)

            assert metrics.files_analyzed >= 1
            assert metrics.total_imports == 0
            assert metrics.avg_imports_per_file == 0
            print("✓ No imports: handled correctly")

    def test_multiple_files_import_count(self):
        """Import count should be aggregated across files."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "file1.py"
            file2 = Path(tmpdir) / "file2.py"
            file3 = Path(tmpdir) / "file3.py"

            file1.write_text("import moduleA\nimport moduleB")
            file2.write_text("import moduleC")
            file3.write_text("import moduleD\nimport moduleE\nimport moduleF")

            metrics = detector.analyze_directory(tmpdir)

            # Total: 2 + 1 + 3 = 6 custom imports
            assert metrics.files_analyzed == 3
            assert metrics.total_imports == 6
            assert metrics.avg_imports_per_file == 2.0
            print(f"✓ Multiple files: {metrics.total_imports} total, avg {metrics.avg_imports_per_file:.1f}/file")

    def test_circular_dependency_detection(self):
        """Circular dependencies should be detected."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_a = Path(tmpdir) / "module_a.py"
            file_b = Path(tmpdir) / "module_b.py"

            # A imports B
            file_a.write_text('''
import module_b

def func_a():
    pass
''')

            # B imports A (cycle!)
            file_b.write_text('''
import module_a

def func_b():
    pass
''')

            metrics = detector.analyze_directory(tmpdir)

            assert metrics.has_circular_deps is True
            assert len(metrics.circular_deps) > 0
            print(f"✓ Circular dependency detected: {len(metrics.circular_deps)} cycle(s)")

    def test_no_circular_dependencies(self):
        """Clean dependency tree should have no cycles."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_a = Path(tmpdir) / "module_a.py"
            file_b = Path(tmpdir) / "module_b.py"
            file_c = Path(tmpdir) / "module_c.py"

            # Linear dependency: A -> B -> C (no cycle)
            file_a.write_text("import module_b")
            file_b.write_text("import module_c")
            file_c.write_text("")

            metrics = detector.analyze_directory(tmpdir)

            assert metrics.has_circular_deps is False
            assert len(metrics.circular_deps) == 0
            print("✓ No circular dependencies: clean tree")

    def test_complex_circular_dependency(self):
        """Complex circular dependency (A -> B -> C -> A) should be detected."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_a = Path(tmpdir) / "module_a.py"
            file_b = Path(tmpdir) / "module_b.py"
            file_c = Path(tmpdir) / "module_c.py"

            # Circular: A -> B -> C -> A
            file_a.write_text("import module_b")
            file_b.write_text("import module_c")
            file_c.write_text("import module_a")

            metrics = detector.analyze_directory(tmpdir)

            assert metrics.has_circular_deps is True
            assert len(metrics.circular_deps) > 0
            print(f"✓ Complex cycle detected: {len(metrics.circular_deps)} edges")

    def test_max_min_imports(self):
        """Max and min imports should be calculated."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_a = Path(tmpdir) / "file_a.py"
            file_b = Path(tmpdir) / "file_b.py"

            file_a.write_text("import m1\nimport m2\nimport m3")  # 3 imports
            file_b.write_text("import m4")  # 1 import

            metrics = detector.analyze_directory(tmpdir)

            assert metrics.max_imports_in_file == 3
            assert metrics.min_imports_in_file == 1
            print(f"✓ Max/min imports: max={metrics.max_imports_in_file}, min={metrics.min_imports_in_file}")

    def test_empty_directory(self):
        """Empty directory should be handled."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            metrics = detector.analyze_directory(tmpdir)

            assert metrics.files_analyzed == 0
            assert metrics.total_imports == 0
            print("✓ Empty directory: handled correctly")

    def test_syntax_error_handling(self):
        """Files with syntax errors should be skipped."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file_good = Path(tmpdir) / "good.py"
            file_bad = Path(tmpdir) / "bad.py"

            file_good.write_text("import mymodule")
            file_bad.write_text("import broken\n(")

            metrics = detector.analyze_directory(tmpdir)

            assert metrics.files_analyzed >= 1
            assert metrics.total_imports >= 1
            print("✓ Syntax error: skipped gracefully")

    def test_report_generation(self):
        """Report should include all required fields."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "module.py"
            file1.write_text("import mymodule")

            metrics = detector.analyze_directory(tmpdir)
            report = detector.report(metrics)

            assert "files_analyzed" in report
            assert "total_imports" in report
            assert "avg_imports_per_file" in report
            assert "max_imports" in report
            assert "min_imports" in report
            assert "has_circular_deps" in report
            assert "circular_deps_count" in report
            assert "circular_deps" in report
            assert "summary" in report

            print(f"✓ Report generated: {report['summary']}")

    def test_import_graph_structure(self):
        """Import graph should correctly map files to imports."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            file1 = Path(tmpdir) / "main.py"
            file2 = Path(tmpdir) / "utils.py"

            file1.write_text("import utils\nimport helpers")
            file2.write_text("import os")  # os is filtered out

            metrics = detector.analyze_directory(tmpdir)

            # Check that import_graph exists
            assert metrics.import_graph is not None
            assert len(metrics.import_graph) > 0

            print(f"✓ Import graph: {len(metrics.import_graph)} modules tracked")

    def test_real_world_scenario(self):
        """Test with realistic project structure."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Simulate a small project
            main = Path(tmpdir) / "main.py"
            config = Path(tmpdir) / "config.py"
            database = Path(tmpdir) / "database.py"
            utils = Path(tmpdir) / "utils.py"

            main.write_text('''
import config
import database
import utils
''')

            config.write_text('''
import os
import json
''')

            database.write_text('''
import sqlite3
import utils
''')

            utils.write_text('''
import logging
import json
''')

            metrics = detector.analyze_directory(tmpdir)

            assert metrics.files_analyzed == 4
            # main: 3, config: 0, database: 1, utils: 0
            assert metrics.total_imports == 4
            assert metrics.has_circular_deps is False

            print(f"✓ Real-world scenario: {metrics.files_analyzed} files, {metrics.total_imports} custom imports")

    def test_coupling_level_classification(self):
        """Low coupling should be < 3 avg imports."""
        detector = CouplingDetector()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Create files with low import coupling
            for i in range(3):
                file = Path(tmpdir) / f"module_{i}.py"
                file.write_text("import lib")  # Each file imports 1 module

            metrics = detector.analyze_directory(tmpdir)

            assert metrics.avg_imports_per_file <= 1.0
            report = detector.report(metrics)
            assert "Low coupling" in report["summary"]

            print(f"✓ Coupling classification: {report['summary']}")


if __name__ == "__main__":
    test = TestCouplingDetector()

    print("Running Coupling Detector Tests...\n")
    test.test_simple_imports()
    test.test_from_imports()
    test.test_stdlib_filtering()
    test.test_no_imports()
    test.test_multiple_files_import_count()
    test.test_circular_dependency_detection()
    test.test_no_circular_dependencies()
    test.test_complex_circular_dependency()
    test.test_max_min_imports()
    test.test_empty_directory()
    test.test_syntax_error_handling()
    test.test_report_generation()
    test.test_import_graph_structure()
    test.test_real_world_scenario()
    test.test_coupling_level_classification()

    print("\n✅ All tests passed!")
