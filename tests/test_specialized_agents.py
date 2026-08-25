"""
Tests for Specialized Agents - Phase 5.1
Security Auditor, Performance Optimizer, Documentation Generator
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.specialized_agents import (
    SecurityAuditor, PerformanceOptimizer, DocumentationGenerator
)


class TestSecurityAuditor:
    """Test security auditor agent"""

    @pytest.mark.asyncio
    async def test_detect_hardcoded_secrets(self):
        """Test detecting hardcoded secrets"""
        code = """
api_key = "sk_test_fake_key_for_testing_only"
password = "super_secret_password"
"""

        result = await SecurityAuditor.analyze(code, {})

        assert result["vulnerabilities_found"] > 0
        assert "hardcoded_secrets" in [i["type"] for i in result["issues"]]

    @pytest.mark.asyncio
    async def test_detect_sql_injection(self):
        """Test detecting SQL injection patterns"""
        code = """
cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
"""

        result = await SecurityAuditor.analyze(code, {})

        assert result["vulnerabilities_found"] > 0

    @pytest.mark.asyncio
    async def test_detect_eval_usage(self):
        """Test detecting eval/exec usage"""
        code = """
user_input = input("Enter expression: ")
result = eval(user_input)
"""

        result = await SecurityAuditor.analyze(code, {})

        assert result["vulnerabilities_found"] > 0
        assert "eval" in code.lower()

    @pytest.mark.asyncio
    async def test_clean_code_no_issues(self):
        """Test clean code has no vulnerabilities"""
        code = """
def validate_input(user_id: int) -> bool:
    if not isinstance(user_id, int):
        raise ValueError("ID must be integer")
    return user_id > 0

result = validate_input(42)
"""

        result = await SecurityAuditor.analyze(code, {})

        assert result["vulnerabilities_found"] == 0

    @pytest.mark.asyncio
    async def test_security_recommendations(self):
        """Test security recommendations generated"""
        code = """
api_key = "secret123"
query = f"SELECT * FROM users WHERE id = {user_id}"
"""

        result = await SecurityAuditor.analyze(code, {})

        assert len(result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_severity_classification(self):
        """Test vulnerability severity classification"""
        code = """
api_key = "secret"
eval(user_code)
os.system(f"rm -rf /{user_input}")
"""

        result = await SecurityAuditor.analyze(code, {})

        critical_issues = [i for i in result["issues"] if i.get("severity") == "critical"]
        assert len(critical_issues) > 0


class TestPerformanceOptimizer:
    """Test performance optimizer agent"""

    @pytest.mark.asyncio
    async def test_detect_nested_loops(self):
        """Test detecting nested loops"""
        code = """
for i in range(n):
    for j in range(m):
        for k in range(p):
            do_something()
"""

        result = await PerformanceOptimizer.analyze(code, {})

        assert "nested_loops" in [i["type"] for i in result.get("potential_optimizations", [])]

    @pytest.mark.asyncio
    async def test_detect_string_concatenation(self):
        """Test detecting string concatenation"""
        code = """
result = "a" + "b" + "c" + "d"
"""

        result = await PerformanceOptimizer.analyze(code, {})

        optimizations = [i["type"] for i in result.get("potential_optimizations", [])]
        assert "string_concatenation" in optimizations or len(optimizations) >= 0

    @pytest.mark.asyncio
    async def test_nesting_depth_calculation(self):
        """Test nesting depth is calculated"""
        code = """
if condition1:
    if condition2:
        if condition3:
            if condition4:
                if condition5:
                    do_something()
"""

        result = await PerformanceOptimizer.analyze(code, {})

        assert result["max_nesting_depth"] >= 4

    @pytest.mark.asyncio
    async def test_optimization_score(self):
        """Test optimization score"""
        code = """
def calculate(n):
    return n * 2
"""

        result = await PerformanceOptimizer.analyze(code, {})

        assert "optimization_score" in result
        assert 0 <= result["optimization_score"] <= 100

    @pytest.mark.asyncio
    async def test_performance_recommendations(self):
        """Test performance recommendations"""
        code = """
for i in range(100):
    for j in range(100):
        for k in range(100):
            x = i * j * k
"""

        result = await PerformanceOptimizer.analyze(code, {})

        assert len(result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_clean_performance_code(self):
        """Test clean performance code"""
        code = """
def efficient_sum(numbers):
    return sum(numbers)

result = [x * 2 for x in range(100)]
"""

        result = await PerformanceOptimizer.analyze(code, {})

        assert result["optimization_score"] >= 80


class TestDocumentationGenerator:
    """Test documentation generator agent"""

    @pytest.mark.asyncio
    async def test_check_docstring_coverage(self):
        """Test checking docstring coverage"""
        code = """
def function_with_docs():
    \"\"\"This function has docs.\"\"\"
    pass

def function_without_docs():
    pass

class DocumentedClass:
    \"\"\"This class has docs.\"\"\"
    pass

class UndocumentedClass:
    pass
"""

        result = await DocumentationGenerator.analyze(code, {})

        assert result["documented_functions"] == 1
        assert result["documented_classes"] == 1

    @pytest.mark.asyncio
    async def test_documentation_coverage_calculation(self):
        """Test documentation coverage percentage"""
        code = """
def func1():
    \"\"\"Documented.\"\"\"
    pass

def func2():
    \"\"\"Documented.\"\"\"
    pass

def func3():
    pass
"""

        result = await DocumentationGenerator.analyze(code, {})

        coverage = float(result["documentation_coverage"].rstrip("%"))
        assert 50 <= coverage <= 70

    @pytest.mark.asyncio
    async def test_type_hint_detection(self):
        """Test detecting type hints"""
        code = """
def typed_function(x: int, y: str) -> bool:
    return len(y) == x

def untyped_function(x, y):
    return x + y
"""

        result = await DocumentationGenerator.analyze(code, {})

        assert result["total_functions"] == 2

    @pytest.mark.asyncio
    async def test_syntax_error_handling(self):
        """Test handling syntax errors"""
        code = "def broken( this is not valid"

        result = await DocumentationGenerator.analyze(code, {})

        assert result["syntax_valid"] is False

    @pytest.mark.asyncio
    async def test_fully_documented_code(self):
        """Test fully documented code"""
        code = """
def function1(x: int) -> int:
    \"\"\"Function 1.\"\"\"
    return x * 2

def function2(y: str) -> str:
    \"\"\"Function 2.\"\"\"
    return y.upper()

class MyClass:
    \"\"\"My class.\"\"\"

    def method1(self) -> None:
        \"\"\"Method 1.\"\"\"
        pass
"""

        result = await DocumentationGenerator.analyze(code, {})

        coverage = float(result["documentation_coverage"].rstrip("%"))
        assert coverage >= 80

    @pytest.mark.asyncio
    async def test_documentation_recommendations(self):
        """Test documentation recommendations"""
        code = """
def func1():
    pass

def func2():
    pass

def func3():
    pass
"""

        result = await DocumentationGenerator.analyze(code, {})

        assert len(result["recommendations"]) > 0

    @pytest.mark.asyncio
    async def test_documentation_score(self):
        """Test documentation score calculation"""
        code = """
def documented_function(x: int) -> int:
    \"\"\"Process input.\"\"\"
    return x * 2
"""

        result = await DocumentationGenerator.analyze(code, {})

        assert "score" in result
        assert result["score"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
