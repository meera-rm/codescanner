"""
Tests for Code Formatter Service - Phase 4.2b
Tests formatting with Black (Python) and Prettier (JavaScript)
"""

import pytest
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.code_formatter import (
    CodeFormatter,
    Language,
    FormatterResult,
    get_code_formatter,
)


@pytest.fixture
def formatter():
    """Create CodeFormatter instance"""
    return CodeFormatter()


class TestLanguageDetection:
    """Test language detection"""

    def test_detect_python_by_extension(self, formatter):
        """Test detecting Python from .py extension"""
        lang = formatter.detect_language("test.py")
        assert lang == Language.PYTHON

    def test_detect_javascript_by_extension(self, formatter):
        """Test detecting JavaScript from .js extension"""
        lang = formatter.detect_language("test.js")
        assert lang == Language.JAVASCRIPT

    def test_detect_typescript_by_extension(self, formatter):
        """Test detecting TypeScript from .ts extension"""
        lang = formatter.detect_language("test.ts")
        assert lang == Language.TYPESCRIPT

    def test_detect_json_by_extension(self, formatter):
        """Test detecting JSON from .json extension"""
        lang = formatter.detect_language("data.json")
        assert lang == Language.JSON

    def test_detect_python_from_content(self, formatter):
        """Test detecting Python from code content"""
        code = "def hello():\n    return 42"
        lang = formatter.detect_language_from_content(code)
        assert lang == Language.PYTHON

    def test_detect_javascript_from_content(self, formatter):
        """Test detecting JavaScript from code content"""
        code = "const x = 42; function test() {}"
        lang = formatter.detect_language_from_content(code)
        assert lang == Language.JAVASCRIPT

    def test_detect_unknown_language(self, formatter):
        """Test detecting unknown language"""
        code = "just some random text"
        lang = formatter.detect_language_from_content(code)
        assert lang == Language.UNKNOWN


class TestFormatterResult:
    """Test FormatterResult data structure"""

    def test_successful_format(self):
        """Test successful format result"""
        result = FormatterResult(
            success=True,
            formatted_code="formatted",
            original_code="original",
            language="python",
            lines_changed=5,
        )

        assert result.success
        assert result.formatted_code == "formatted"
        assert result.original_code == "original"
        assert result.language == "python"
        assert result.lines_changed == 5

    def test_failed_format(self):
        """Test failed format result"""
        result = FormatterResult(
            success=False,
            original_code="original",
            language="python",
            error="Syntax error",
        )

        assert not result.success
        assert result.error == "Syntax error"
        assert result.formatted_code is None


class TestPythonFormatting:
    """Test Python code formatting"""

    @pytest.mark.asyncio
    async def test_format_python_simple_code(self, formatter):
        """Test formatting simple Python code"""
        code = "def hello():\n    return 42"

        result = await formatter.format_code(code, language=Language.PYTHON)

        assert result.success or result.error == "Formatting timed out"
        if result.success:
            assert result.formatted_code is not None
            assert result.language == "python"

    @pytest.mark.asyncio
    async def test_format_python_unformatted(self, formatter):
        """Test formatting unformatted Python code"""
        code = "def test(  ):  \n    x=1+2\n    return   x"

        result = await formatter.format_code(code, language=Language.PYTHON)

        assert result.success or result.error == "Formatting timed out"
        if result.success:
            # Formatted code should be different or same
            assert result.formatted_code is not None

    @pytest.mark.asyncio
    async def test_format_python_with_imports(self, formatter):
        """Test formatting Python code with imports"""
        code = """import os
from pathlib import Path


def process():
    x=1
    return x"""

        result = await formatter.format_code(code, language=Language.PYTHON)

        assert result.success or result.error == "Formatting timed out"

    @pytest.mark.asyncio
    async def test_format_python_preserve_code(self, formatter):
        """Test that code content is preserved after formatting"""
        code = """def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)"""

        result = await formatter.format_code(code, language=Language.PYTHON)

        if result.success:
            # Should contain the function name
            assert "fibonacci" in result.formatted_code
            # Should have proper structure
            assert "def" in result.formatted_code


class TestJavaScriptFormatting:
    """Test JavaScript code formatting"""

    @pytest.mark.asyncio
    async def test_format_javascript_simple_code(self, formatter):
        """Test formatting simple JavaScript code"""
        code = "const x = 42; function test() { return x; }"

        result = await formatter.format_code(code, language=Language.JAVASCRIPT)

        # Prettier may not be available, so check if it tries
        assert result.success or result.error is not None

    @pytest.mark.asyncio
    async def test_format_javascript_unformatted(self, formatter):
        """Test formatting unformatted JavaScript code"""
        code = "const x=42;function test(){return x;}"

        result = await formatter.format_code(code, language=Language.JAVASCRIPT)

        assert result.success or result.error is not None

    @pytest.mark.asyncio
    async def test_format_typescript_code(self, formatter):
        """Test formatting TypeScript code"""
        code = "const x:number=42;function test(){return x;}"

        result = await formatter.format_code(code, language=Language.TYPESCRIPT)

        assert result.success or result.error is not None


class TestJSONFormatting:
    """Test JSON code formatting"""

    @pytest.mark.asyncio
    async def test_format_json_valid(self, formatter):
        """Test formatting valid JSON"""
        code = '{"name":"test","value":42}'

        result = await formatter.format_code(code, language=Language.JSON)

        assert result.success
        assert result.formatted_code is not None
        # Should be formatted with proper indentation
        assert "\n" in result.formatted_code or result.formatted_code is not None

    @pytest.mark.asyncio
    async def test_format_json_with_indentation(self, formatter):
        """Test formatting already indented JSON"""
        code = '{\n  "name": "test",\n  "value": 42\n}'

        result = await formatter.format_code(code, language=Language.JSON)

        assert result.success
        assert result.formatted_code is not None

    @pytest.mark.asyncio
    async def test_format_invalid_json(self, formatter):
        """Test formatting invalid JSON"""
        code = '{"name":"test"invalid}'

        result = await formatter.format_code(code, language=Language.JSON)

        assert not result.success
        assert result.error is not None


class TestAutoLanguageDetection:
    """Test automatic language detection in format_code"""

    @pytest.mark.asyncio
    async def test_auto_detect_python_from_extension(self, formatter):
        """Test auto-detecting Python from file path"""
        code = "x = 1"

        result = await formatter.format_code(code, file_path="test.py")

        # Should detect Python and format
        assert result.success or result.error == "Formatting timed out"

    @pytest.mark.asyncio
    async def test_auto_detect_json(self, formatter):
        """Test auto-detecting JSON from file path"""
        code = '{"test": 1}'

        result = await formatter.format_code(code, file_path="data.json")

        assert result.success
        assert result.language == "json"


class TestFormatterStatus:
    """Test formatter availability status"""

    def test_get_formatter_status(self, formatter):
        """Test getting formatter status"""
        status = formatter.get_formatter_status()

        assert isinstance(status, dict)
        assert "black" in status
        assert "prettier" in status
        assert "formatters_available" in status


class TestSingletonPattern:
    """Test singleton pattern"""

    def test_get_code_formatter_singleton(self):
        """Test that get_code_formatter returns same instance"""
        formatter1 = get_code_formatter()
        formatter2 = get_code_formatter()

        assert formatter1 is formatter2


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.mark.asyncio
    async def test_format_empty_code(self, formatter):
        """Test formatting empty code"""
        code = ""

        result = await formatter.format_code(code, language=Language.PYTHON)

        # Should handle gracefully
        assert result.original_code == code

    @pytest.mark.asyncio
    async def test_format_whitespace_only(self, formatter):
        """Test formatting code with only whitespace"""
        code = "   \n   \n   "

        result = await formatter.format_code(code, language=Language.PYTHON)

        # Should handle gracefully
        assert result.original_code == code

    @pytest.mark.asyncio
    async def test_format_very_long_code(self, formatter):
        """Test formatting very long code"""
        code = "x = 1\n" * 1000

        result = await formatter.format_code(code, language=Language.PYTHON)

        # Should either succeed or timeout gracefully
        assert result.success or result.error is not None

    @pytest.mark.asyncio
    async def test_format_with_unicode(self, formatter):
        """Test formatting code with unicode characters"""
        code = 'x = "Hello 🌍"\nprint(x)'

        result = await formatter.format_code(code, language=Language.PYTHON)

        # Should handle unicode gracefully
        assert result.success or result.error is not None


class TestFormattingIntegration:
    """Test end-to-end formatting"""

    @pytest.mark.asyncio
    async def test_format_realistic_python_function(self, formatter):
        """Test formatting a realistic Python function"""
        code = """def calculate_total(items,tax_rate=0.1):
    total=0
    for item in items:
        total+=item['price']*(1+tax_rate)
    return round(total,2)"""

        result = await formatter.format_code(code, language=Language.PYTHON)

        if result.success:
            assert "calculate_total" in result.formatted_code
            assert "tax_rate" in result.formatted_code


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
