import tempfile
import os
from pathlib import Path
import sys

# Add scanner to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scanner"))

from smells import SmellDetector, SmellFinding


class TestSmellDetector:
    """Test suite for code smell detection."""

    def test_detect_long_function(self):
        """Long function (>50 lines) should be detected."""
        code = '''
def long_function():
    """A function with 60 lines."""
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
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = SmellDetector()
                findings = detector.detect(f.name)

                assert len(findings) > 0, "Should detect long function"
                assert findings[0].smell_type == "long_function"
                assert findings[0].code_lines > 50
                print(f"✓ Long function detected: {findings[0].description}")
            finally:
                os.unlink(f.name)

    def test_detect_large_class(self):
        """Large class (>300 lines) should be detected."""
        # Generate a large class with 320+ lines
        method_defs = []
        for i in range(150):
            method_defs.append(f"    def method_{i}(self):")
            method_defs.append(f"        pass  # Method {i}")

        code = "class LargeClass:\n    \"\"\"A class with many methods.\"\"\"\n"
        code += "\n".join(method_defs)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = SmellDetector()
                findings = detector.detect(f.name)

                assert any(f.smell_type == "large_class" for f in findings), "Should detect large class"
                large_class_finding = [f for f in findings if f.smell_type == "large_class"][0]
                assert large_class_finding.code_lines > 300
                print(f"✓ Large class detected: {large_class_finding.description}")
            finally:
                os.unlink(f.name)

    def test_detect_long_parameter_list(self):
        """Function with >5 parameters should be detected."""
        code = '''
def function_with_many_params(a, b, c, d, e, f, g):
    return a + b + c + d + e + f + g
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = SmellDetector()
                findings = detector.detect(f.name)

                assert any(f.smell_type == "long_params" for f in findings), "Should detect long parameter list"
                params_finding = [f for f in findings if f.smell_type == "long_params"][0]
                assert params_finding.code_lines == 7
                print(f"✓ Long parameter list detected: {params_finding.description}")
            finally:
                os.unlink(f.name)

    def test_exclude_self_from_parameter_count(self):
        """Method parameter count should exclude 'self'."""
        code = '''
class MyClass:
    def method(self, a, b, c, d, e, f):
        return a + b + c + d + e + f
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = SmellDetector()
                findings = detector.detect(f.name)

                params_findings = [f for f in findings if f.smell_type == "long_params"]
                assert len(params_findings) > 0, "Should detect long parameter list excluding self"
                assert params_findings[0].code_lines == 6  # a,b,c,d,e,f (not self)
                print(f"✓ Parameter count excludes 'self': {params_findings[0].description}")
            finally:
                os.unlink(f.name)

    def test_detect_deep_nesting(self):
        """Code with >4 nesting levels should be detected."""
        code = '''
def deeply_nested():
    if True:
        if True:
            if True:
                if True:
                    if True:
                        print("Deep!")
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = SmellDetector()
                findings = detector.detect(f.name)

                assert any(f.smell_type == "deep_nesting" for f in findings), "Should detect deep nesting"
                nesting_finding = [f for f in findings if f.smell_type == "deep_nesting"][0]
                assert nesting_finding.code_lines > 4
                print(f"✓ Deep nesting detected: {nesting_finding.description}")
            finally:
                os.unlink(f.name)

    def test_short_function_not_flagged(self):
        """Short function (<50 lines) should not be flagged."""
        code = '''
def short_function(a, b):
    return a + b
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = SmellDetector()
                findings = detector.detect(f.name)

                long_func_findings = [f for f in findings if f.smell_type == "long_function"]
                assert len(long_func_findings) == 0, "Short function should not be flagged"
                print("✓ Short function not flagged")
            finally:
                os.unlink(f.name)

    def test_normal_parameters_not_flagged(self):
        """Function with ≤5 parameters should not be flagged."""
        code = '''
def function_with_normal_params(a, b, c, d, e):
    return a + b + c + d + e
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = SmellDetector()
                findings = detector.detect(f.name)

                params_findings = [f for f in findings if f.smell_type == "long_params"]
                assert len(params_findings) == 0, "Normal parameter list should not be flagged"
                print("✓ Normal parameters not flagged")
            finally:
                os.unlink(f.name)

    def test_shallow_nesting_not_flagged(self):
        """Code with ≤4 nesting levels should not be flagged."""
        code = '''
def shallow_nesting():
    if True:
        if True:
            if True:
                if True:
                    print("Shallow!")
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = SmellDetector()
                findings = detector.detect(f.name)

                nesting_findings = [f for f in findings if f.smell_type == "deep_nesting"]
                assert len(nesting_findings) == 0, "Shallow nesting should not be flagged"
                print("✓ Shallow nesting not flagged")
            finally:
                os.unlink(f.name)

    def test_empty_file(self):
        """Empty file should return no findings."""
        code = ""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = SmellDetector()
                findings = detector.detect(f.name)

                assert len(findings) == 0, "Empty file should have no findings"
                print("✓ Empty file handled correctly")
            finally:
                os.unlink(f.name)

    def test_syntax_error_handling(self):
        """File with syntax error should not crash."""
        code = "def broken(\n"

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = SmellDetector()
                findings = detector.detect(f.name)

                assert len(findings) == 0, "Syntax errors should be handled gracefully"
                print("✓ Syntax error handled gracefully")
            finally:
                os.unlink(f.name)

    def test_multiple_smells_in_one_file(self):
        """File with multiple smell types should report all."""
        code = '''
def long_and_messy(a, b, c, d, e, f, g):
    """Long function with long params and deep nesting."""
    x = 1
    y = 2
    z = 3
    if True:
        if True:
            if True:
                if True:
                    if True:
                        for i in range(100):
                            pass
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
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = SmellDetector()
                findings = detector.detect(f.name)

                smell_types = {f.smell_type for f in findings}
                assert len(smell_types) >= 2, "Should detect multiple smell types"
                assert "long_function" in smell_types
                assert "long_params" in smell_types
                print(f"✓ Multiple smells detected: {smell_types}")
            finally:
                os.unlink(f.name)

    def test_report_generation(self):
        """Report should aggregate findings by type."""
        code = '''
def long_function_1():
    """ 60 lines """
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

def func_many_params(a, b, c, d, e, f, g):
    return a + b
'''

        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write(code)
            f.flush()
            try:
                detector = SmellDetector()
                findings = detector.detect(f.name)

                report = detector.report(findings)
                assert "total_smells" in report
                assert "by_type" in report
                assert report["total_smells"] == 2
                assert "long_function" in report["by_type"]
                assert "long_params" in report["by_type"]
                print(f"✓ Report generated: {report['total_smells']} smells found")
            finally:
                os.unlink(f.name)


if __name__ == "__main__":
    test = TestSmellDetector()

    print("Running Smell Detector Tests...\n")
    test.test_detect_long_function()
    test.test_detect_large_class()
    test.test_detect_long_parameter_list()
    test.test_exclude_self_from_parameter_count()
    test.test_detect_deep_nesting()
    test.test_short_function_not_flagged()
    test.test_normal_parameters_not_flagged()
    test.test_shallow_nesting_not_flagged()
    test.test_empty_file()
    test.test_syntax_error_handling()
    test.test_multiple_smells_in_one_file()
    test.test_report_generation()

    print("\n✅ All tests passed!")
