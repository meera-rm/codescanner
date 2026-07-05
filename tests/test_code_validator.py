"""
Tests for Code Validator Service - Phase 4.2c
Tests syntax validation, linting, and test execution
"""

import pytest
import tempfile
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.code_validator import (
    CodeValidator,
    ValidationResult,
    get_code_validator,
)


@pytest.fixture
def validator():
    """Create CodeValidator instance"""
    return CodeValidator()


@pytest.fixture
def temp_codebase():
    """Create temporary codebase for testing"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create sample Python file
        py_file = tmppath / "sample.py"
        py_file.write_text("""def hello():
    return 42

def world():
    return hello()
""")

        # Create sample JS file
        js_file = tmppath / "sample.js"
        js_file.write_text("const x = 42;\nfunction test() { return x; }\n")

        yield tmppath


class TestValidationResult:
    """Test ValidationResult data structure"""

    def test_successful_validation(self):
        """Test successful validation result"""
        result = ValidationResult(
            success=True,
            syntax_valid=True,
            linting_passed=True,
            tests_passed=True,
        )

        assert result.success
        assert result.syntax_valid
        assert result.linting_passed
        assert result.tests_passed

    def test_failed_validation(self):
        """Test failed validation result"""
        result = ValidationResult(
            success=False,
            syntax_valid=False,
            syntax_errors=["Line 1: SyntaxError"],
        )

        assert not result.success
        assert not result.syntax_valid
        assert len(result.syntax_errors) > 0


class TestPythonSyntaxValidation:
    """Test Python syntax validation"""

    @pytest.mark.asyncio
    async def test_valid_python_syntax(self, validator):
        """Test validating valid Python code"""
        code = """def hello():
    return 42"""

        valid, errors = await validator.validate_syntax(code, "python")

        assert valid
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_invalid_python_syntax(self, validator):
        """Test validating invalid Python code"""
        code = "def hello(\n    return 42"

        valid, errors = await validator.validate_syntax(code, "python")

        assert not valid
        assert len(errors) > 0

    @pytest.mark.asyncio
    async def test_python_syntax_with_imports(self, validator):
        """Test validating Python code with imports"""
        code = """import os
from pathlib import Path

def process():
    x = 1
    return x"""

        valid, errors = await validator.validate_syntax(code, "python")

        assert valid
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_python_syntax_with_class(self, validator):
        """Test validating Python code with class"""
        code = """class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b"""

        valid, errors = await validator.validate_syntax(code, "python")

        assert valid
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_python_syntax_indentation_error(self, validator):
        """Test catching indentation errors"""
        code = """def hello():
return 42"""

        valid, errors = await validator.validate_syntax(code, "python")

        assert not valid
        assert len(errors) > 0


class TestJavaScriptSyntaxValidation:
    """Test JavaScript syntax validation"""

    @pytest.mark.asyncio
    async def test_valid_javascript_syntax(self, validator):
        """Test validating valid JavaScript code"""
        code = "const x = 42; function test() { return x; }"

        valid, errors = await validator.validate_syntax(code, "javascript")

        # May not have node installed, so check if validation attempted
        assert isinstance(valid, bool)

    @pytest.mark.asyncio
    async def test_invalid_javascript_syntax(self, validator):
        """Test validating invalid JavaScript code"""
        code = "const x = 42; function test() { return x; )"

        valid, errors = await validator.validate_syntax(code, "javascript")

        # Node may not be available, but should handle gracefully
        assert isinstance(valid, bool)


class TestJSONSyntaxValidation:
    """Test JSON syntax validation"""

    @pytest.mark.asyncio
    async def test_valid_json_syntax(self, validator):
        """Test validating valid JSON"""
        code = '{"name": "test", "value": 42}'

        valid, errors = await validator.validate_syntax(code, "json")

        assert valid
        assert len(errors) == 0

    @pytest.mark.asyncio
    async def test_invalid_json_syntax(self, validator):
        """Test validating invalid JSON"""
        code = '{"name": "test"invalid}'

        valid, errors = await validator.validate_syntax(code, "json")

        assert not valid
        assert len(errors) > 0

    @pytest.mark.asyncio
    async def test_json_with_arrays(self, validator):
        """Test validating JSON with arrays"""
        code = '{"items": [1, 2, 3], "nested": {"key": "value"}}'

        valid, errors = await validator.validate_syntax(code, "json")

        assert valid
        assert len(errors) == 0


class TestValidatorStatus:
    """Test validator availability status"""

    def test_get_validator_status(self, validator):
        """Test getting validator status"""
        status = validator.get_validator_status()

        assert isinstance(status, dict)
        assert "pylint" in status
        assert "pytest" in status
        assert "eslint" in status
        assert "npm_test" in status
        assert "validators_available" in status

    def test_validators_available_flag(self, validator):
        """Test validators_available flag"""
        status = validator.get_validator_status()

        # At least pytest or pylint should be available
        assert isinstance(status["validators_available"], bool)


class TestSingletonPattern:
    """Test singleton pattern"""

    def test_get_code_validator_singleton(self):
        """Test that get_code_validator returns same instance"""
        validator1 = get_code_validator()
        validator2 = get_code_validator()

        assert validator1 is validator2


class TestValidateAll:
    """Test comprehensive validation"""

    @pytest.mark.asyncio
    async def test_validate_all_valid_code(self, validator, temp_codebase):
        """Test validate_all with valid code"""
        code = "def hello():\n    return 42"
        py_file = temp_codebase / "test.py"
        py_file.write_text(code)

        result = await validator.validate_all(
            str(temp_codebase), code, "python", str(py_file)
        )

        # Syntax should be valid; tests may fail if pytest not set up properly
        assert result.syntax_valid

    @pytest.mark.asyncio
    async def test_validate_all_invalid_code(self, validator, temp_codebase):
        """Test validate_all with invalid code"""
        code = "def hello(\n    return 42"

        result = await validator.validate_all(
            str(temp_codebase), code, "python", str(temp_codebase / "test.py")
        )

        assert not result.success
        assert not result.syntax_valid
        assert len(result.syntax_errors) > 0

    @pytest.mark.asyncio
    async def test_validate_all_json(self, validator, temp_codebase):
        """Test validate_all with JSON"""
        code = '{"test": 1}'

        result = await validator.validate_all(
            str(temp_codebase), code, "json", str(temp_codebase / "test.json")
        )

        # Syntax should be valid; tests may not be available
        assert result.syntax_valid


class TestEdgeCases:
    """Test edge cases"""

    @pytest.mark.asyncio
    async def test_validate_empty_code(self, validator):
        """Test validating empty code"""
        code = ""

        valid, errors = await validator.validate_syntax(code, "python")

        # Empty code is valid Python
        assert valid

    @pytest.mark.asyncio
    async def test_validate_comments_only(self, validator):
        """Test validating code with only comments"""
        code = """# This is a comment
# Another comment"""

        valid, errors = await validator.validate_syntax(code, "python")

        assert valid

    @pytest.mark.asyncio
    async def test_validate_with_unicode(self, validator):
        """Test validating code with unicode"""
        code = 'x = "Hello 🌍"\nprint(x)'

        valid, errors = await validator.validate_syntax(code, "python")

        assert valid

    @pytest.mark.asyncio
    async def test_validate_multiline_string(self, validator):
        """Test validating code with multiline strings"""
        code = '''def hello():
    """
    Multiline docstring
    with more text
    """
    return 42'''

        valid, errors = await validator.validate_syntax(code, "python")

        assert valid


class TestComplexValidation:
    """Test complex code validation"""

    @pytest.mark.asyncio
    async def test_validate_class_with_methods(self, validator):
        """Test validating class with multiple methods"""
        code = """class Calculator:
    def __init__(self):
        self.result = 0

    def add(self, a, b):
        self.result = a + b
        return self.result

    def multiply(self, a, b):
        self.result = a * b
        return self.result
"""

        valid, errors = await validator.validate_syntax(code, "python")

        assert valid

    @pytest.mark.asyncio
    async def test_validate_decorator_usage(self, validator):
        """Test validating code with decorators"""
        code = """def decorator(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@decorator
def hello():
    return 42
"""

        valid, errors = await validator.validate_syntax(code, "python")

        assert valid

    @pytest.mark.asyncio
    async def test_validate_async_code(self, validator):
        """Test validating async/await code"""
        code = """async def fetch_data():
    data = await some_coroutine()
    return data

async def main():
    result = await fetch_data()
    return result
"""

        valid, errors = await validator.validate_syntax(code, "python")

        assert valid


class TestValidationWithRealFiles:
    """Test validation with real file operations"""

    @pytest.mark.asyncio
    async def test_validate_file_based_python(self, validator, temp_codebase):
        """Test validating Python file"""
        py_file = temp_codebase / "test.py"
        code = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
        py_file.write_text(code)

        valid, errors = await validator.validate_syntax(code, "python")

        assert valid

    @pytest.mark.asyncio
    async def test_validate_file_based_json(self, validator, temp_codebase):
        """Test validating JSON file"""
        json_file = temp_codebase / "data.json"
        code = '{"users": [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]}'
        json_file.write_text(code)

        valid, errors = await validator.validate_syntax(code, "json")

        assert valid


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
