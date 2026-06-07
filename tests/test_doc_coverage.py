import tempfile
import os
from pathlib import Path
import sys

# Add scanner to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scanner"))

from doc_coverage import DocCoverageDetector, DocMetrics


class TestDocCoverageDetector:
    """Test suite for documentation coverage detection."""

    def test_all_functions_documented(self):
        """File where all functions have docstrings should have 100% coverage."""
        code = '''
"""Module docstring."""

def function_one():
    """Function one docstring."""
    return 1

def function_two():
    """Function two docstring."""
    return 2
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = DocCoverageDetector()
                metrics = detector.analyze(f.name)

                assert metrics is not None
                assert metrics.total_functions == 2
                assert metrics.documented_functions == 2
                assert metrics.coverage_ratio == 1.0
                assert metrics.has_module_docstring is True
                print(f"✓ 100% coverage: {metrics.documented_functions}/{metrics.total_functions}")
            finally:
                os.unlink(f.name)

    def test_no_functions_documented(self):
        """File where no functions have docstrings should have 0% coverage."""
        code = '''
def function_one():
    return 1

def function_two():
    return 2
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = DocCoverageDetector()
                metrics = detector.analyze(f.name)

                assert metrics is not None
                assert metrics.total_functions == 2
                assert metrics.documented_functions == 0
                assert metrics.coverage_ratio == 0.0
                assert metrics.has_module_docstring is False
                print(f"✓ 0% coverage: {metrics.documented_functions}/{metrics.total_functions}")
            finally:
                os.unlink(f.name)

    def test_partial_documentation(self):
        """File with some documented functions should have partial coverage."""
        code = '''
def function_one():
    """Documented."""
    return 1

def function_two():
    return 2

def function_three():
    """Documented."""
    return 3
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = DocCoverageDetector()
                metrics = detector.analyze(f.name)

                assert metrics is not None
                assert metrics.total_functions == 3
                assert metrics.documented_functions == 2
                assert abs(metrics.coverage_ratio - 2/3) < 0.01
                print(f"✓ Partial coverage: {metrics.coverage_ratio * 100:.1f}%")
            finally:
                os.unlink(f.name)

    def test_classes_with_docstrings(self):
        """Classes with docstrings should be counted as documented."""
        code = '''
class DocumentedClass:
    """Class with docstring."""
    def method(self):
        pass

class UndocumentedClass:
    def method(self):
        pass
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = DocCoverageDetector()
                metrics = detector.analyze(f.name)

                assert metrics is not None
                assert metrics.total_classes == 2
                assert metrics.documented_classes == 1
                print(f"✓ Class docstrings: {metrics.documented_classes}/{metrics.total_classes}")
            finally:
                os.unlink(f.name)

    def test_methods_in_classes(self):
        """Methods inside classes should be counted."""
        code = '''
class MyClass:
    """Class docstring."""

    def method_one(self):
        """Method docstring."""
        pass

    def method_two(self):
        pass

    def method_three(self):
        """Method docstring."""
        pass
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = DocCoverageDetector()
                metrics = detector.analyze(f.name)

                assert metrics is not None
                # 3 methods + 0 top-level functions = 3 total
                assert metrics.total_functions == 3
                assert metrics.documented_functions == 2  # 2 methods documented
                assert metrics.total_classes == 1
                assert metrics.documented_classes == 1
                print(f"✓ Methods counted: {metrics.total_functions} functions, {metrics.documented_functions} documented")
            finally:
                os.unlink(f.name)

    def test_module_docstring_detection(self):
        """Module-level docstring should be detected."""
        code_with_module_doc = '''
"""This is a module docstring."""

def function():
    pass
'''

        code_without_module_doc = '''
def function():
    pass
'''

        for code, expected_module_doc in [
            (code_with_module_doc, True),
            (code_without_module_doc, False),
        ]:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
                f.write(code)
                f.flush()
                try:
                    detector = DocCoverageDetector()
                    metrics = detector.analyze(f.name)

                    assert metrics.has_module_docstring == expected_module_doc
                finally:
                    os.unlink(f.name)

        print("✓ Module docstring detection working")

    def test_coverage_ratio_calculation(self):
        """Coverage ratio should be correctly calculated."""
        code = '''
def a():
    """Documented."""
    pass

def b():
    pass

def c():
    """Documented."""
    pass

def d():
    """Documented."""
    pass
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = DocCoverageDetector()
                metrics = detector.analyze(f.name)

                assert metrics.total_functions == 4
                assert metrics.documented_functions == 3
                expected_ratio = 3 / 4
                assert abs(metrics.coverage_ratio - expected_ratio) < 0.01
                print(f"✓ Coverage ratio: {metrics.coverage_ratio:.2f} ({3}/{4})")
            finally:
                os.unlink(f.name)

    def test_empty_file(self):
        """Empty file should return zero metrics."""
        code = ""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = DocCoverageDetector()
                metrics = detector.analyze(f.name)

                assert metrics is not None
                assert metrics.total_functions == 0
                assert metrics.documented_functions == 0
                assert metrics.coverage_ratio == 0.0
                print("✓ Empty file handled correctly")
            finally:
                os.unlink(f.name)

    def test_syntax_error_handling(self):
        """File with syntax error should return None gracefully."""
        code = "def broken(\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = DocCoverageDetector()
                metrics = detector.analyze(f.name)

                assert metrics is None
                print("✓ Syntax error handled gracefully")
            finally:
                os.unlink(f.name)

    def test_multiline_docstrings(self):
        """Multi-line docstrings should be recognized."""
        code = '''
def function():
    """
    This is a multi-line docstring.
    It spans multiple lines.
    And has multiple paragraphs.
    """
    pass
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = DocCoverageDetector()
                metrics = detector.analyze(f.name)

                assert metrics.total_functions == 1
                assert metrics.documented_functions == 1
                assert metrics.coverage_ratio == 1.0
                print("✓ Multi-line docstrings recognized")
            finally:
                os.unlink(f.name)

    def test_report_generation(self):
        """Report should include all required fields."""
        code = '''
"""Module doc."""

def function_one():
    """Documented."""
    pass

def function_two():
    pass
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = DocCoverageDetector()
                metrics = detector.analyze(f.name)
                report = detector.report(metrics)

                assert "coverage_ratio" in report
                assert "coverage_percentage" in report
                assert "total_functions" in report
                assert "documented_functions" in report
                assert "undocumented_functions" in report
                assert "total_classes" in report
                assert "documented_classes" in report
                assert "has_module_docstring" in report
                assert "summary" in report
                assert report["undocumented_functions"] == 1
                assert report["coverage_percentage"] == 50.0
                print(f"✓ Report generated: {report['summary']}")
            finally:
                os.unlink(f.name)

    def test_undocumented_details(self):
        """Details should list undocumented functions and classes."""
        code = '''
def documented():
    """Has doc."""
    pass

def undocumented():
    pass

class DocumentedClass:
    """Has doc."""
    pass

class UndocumentedClass:
    pass
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = DocCoverageDetector()
                metrics = detector.analyze(f.name)

                assert len(metrics.details["functions"]["undocumented"]) == 1
                assert metrics.details["functions"]["undocumented"][0]["name"] == "undocumented"
                assert len(metrics.details["classes"]["undocumented"]) == 1
                assert metrics.details["classes"]["undocumented"][0]["name"] == "UndocumentedClass"
                print("✓ Undocumented details tracked correctly")
            finally:
                os.unlink(f.name)

    def test_real_world_file(self):
        """Test on a realistic file with mixed documentation."""
        code = '''
"""Main application module."""

import os

def helper():
    """A documented helper."""
    return True

def another_helper():
    return False

class DataProcessor:
    """Handles data processing."""

    def __init__(self):
        """Initialize processor."""
        pass

    def process(self, data):
        return data

    def validate(self, data):
        """Validate data format."""
        return True

def main():
    """Entry point."""
    processor = DataProcessor()
    return processor.process([])
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = DocCoverageDetector()
                metrics = detector.analyze(f.name)

                # Count: helper, another_helper, main (3 top-level functions)
                #        __init__, process, validate (3 methods)
                # = 6 total
                assert metrics.total_functions == 6
                # Documented: helper, main, __init__, validate = 4
                assert metrics.documented_functions == 4
                assert metrics.coverage_ratio == 4 / 6
                assert metrics.total_classes == 1
                assert metrics.documented_classes == 1
                assert metrics.has_module_docstring is True

                report = detector.report(metrics)
                print(f"✓ Real-world file: {report['summary']}")
            finally:
                os.unlink(f.name)


if __name__ == "__main__":
    test = TestDocCoverageDetector()

    print("Running Doc Coverage Detector Tests...\n")
    test.test_all_functions_documented()
    test.test_no_functions_documented()
    test.test_partial_documentation()
    test.test_classes_with_docstrings()
    test.test_methods_in_classes()
    test.test_module_docstring_detection()
    test.test_coverage_ratio_calculation()
    test.test_empty_file()
    test.test_syntax_error_handling()
    test.test_multiline_docstrings()
    test.test_report_generation()
    test.test_undocumented_details()
    test.test_real_world_file()

    print("\n✅ All tests passed!")
