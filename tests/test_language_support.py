"""
Tests for Multi-language Support - Phase 5.3
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.language_detector import Language, LanguageDetector
from api.services.language_formatters import LanguageFormatter, FormattingResult
from api.services.language_validators import LanguageValidator
from api.services.language_router import LanguageRouter, get_language_router


class TestLanguageDetector:
    """Test language detection"""

    def test_detect_python_by_extension(self):
        """Test detecting Python by file extension"""
        lang = LanguageDetector.detect_from_path("script.py")
        assert lang == Language.PYTHON

    def test_detect_javascript_by_extension(self):
        """Test detecting JavaScript by file extension"""
        lang = LanguageDetector.detect_from_path("app.js")
        assert lang == Language.JAVASCRIPT

    def test_detect_typescript_by_extension(self):
        """Test detecting TypeScript by file extension"""
        lang = LanguageDetector.detect_from_path("component.tsx")
        assert lang == Language.TYPESCRIPT

    def test_detect_go_by_extension(self):
        """Test detecting Go by file extension"""
        lang = LanguageDetector.detect_from_path("main.go")
        assert lang == Language.GO

    def test_detect_java_by_extension(self):
        """Test detecting Java by file extension"""
        lang = LanguageDetector.detect_from_path("Main.java")
        assert lang == Language.JAVA

    def test_detect_rust_by_extension(self):
        """Test detecting Rust by file extension"""
        lang = LanguageDetector.detect_from_path("lib.rs")
        assert lang == Language.RUST

    def test_detect_python_by_content(self):
        """Test detecting Python by code content"""
        code = """
def hello(name):
    print(f"Hello {name}")

if __name__ == "__main__":
    hello("World")
"""
        lang = LanguageDetector.detect_from_content(code)
        assert lang == Language.PYTHON

    def test_detect_javascript_by_content(self):
        """Test detecting JavaScript by code content"""
        code = """
function hello(name) {
    console.log(`Hello ${name}`);
}

module.exports = hello;
"""
        lang = LanguageDetector.detect_from_content(code)
        assert lang == Language.JAVASCRIPT

    def test_detect_go_by_content(self):
        """Test detecting Go by code content"""
        code = """
package main

import "fmt"

func main() {
    fmt.Println("Hello")
}
"""
        lang = LanguageDetector.detect_from_content(code)
        assert lang == Language.GO

    def test_detect_with_path_priority(self):
        """Test that path detection has priority over content"""
        code = "def hello(): pass"  # Python code
        lang, conf = LanguageDetector.detect(code, "script.js")
        # Path says JavaScript, so should detect JS
        assert lang == Language.JAVASCRIPT
        assert conf > 0.9

    def test_get_language_info(self):
        """Test getting language information"""
        info = LanguageDetector.get_language_info(Language.PYTHON)

        assert info["name"] == "Python"
        assert info["formatter"] == "black"
        assert info["linter"] == "pylint"
        assert ".py" in info["extensions"]

    def test_get_supported_languages(self):
        """Test getting list of supported languages"""
        langs = LanguageDetector.get_supported_languages()

        assert Language.PYTHON in langs
        assert Language.JAVASCRIPT in langs
        assert Language.TYPESCRIPT in langs
        assert Language.GO in langs
        assert Language.JAVA in langs
        assert Language.RUST in langs


class TestLanguageFormatters:
    """Test language-specific formatters"""

    @pytest.mark.asyncio
    async def test_format_python(self):
        """Test Python formatting"""
        code = "def hello():\n  return 42"

        result = await LanguageFormatter.format_python(code)

        assert result.success is True
        assert result.formatted_code is not None

    @pytest.mark.asyncio
    async def test_format_javascript(self):
        """Test JavaScript formatting"""
        code = "function hello() {\n  return 42;\n}"

        result = await LanguageFormatter.format_javascript(code)

        assert result.success is True
        assert result.formatted_code is not None

    @pytest.mark.asyncio
    async def test_format_typescript(self):
        """Test TypeScript formatting"""
        code = "const x: number = 42;"

        result = await LanguageFormatter.format_typescript(code)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_format_go(self):
        """Test Go formatting"""
        code = "func main() {\n  fmt.Println(\"Hello\")\n}"

        result = await LanguageFormatter.format_go(code)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_format_java(self):
        """Test Java formatting"""
        code = "public class Main {\n  public static void main(String[] args) {}\n}"

        result = await LanguageFormatter.format_java(code)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_format_rust(self):
        """Test Rust formatting"""
        code = "fn main() {\n  println!(\"Hello\");\n}"

        result = await LanguageFormatter.format_rust(code)

        assert result.success is True

    @pytest.mark.asyncio
    async def test_format_with_language_routing(self):
        """Test formatting with language parameter"""
        code = "def hello(): return 42"

        result = await LanguageFormatter.format(code, Language.PYTHON)

        assert result.success is True


class TestLanguageValidators:
    """Test language-specific validators"""

    @pytest.mark.asyncio
    async def test_validate_python_syntax(self):
        """Test Python syntax validation"""
        valid_code = "def hello():\n    return 42"

        result = await LanguageValidator.validate_python(valid_code)

        assert result.syntax_valid is True
        assert result.success is True

    @pytest.mark.asyncio
    async def test_validate_python_invalid_syntax(self):
        """Test Python invalid syntax detection"""
        invalid_code = "def hello(\n    return 42"

        result = await LanguageValidator.validate_python(invalid_code)

        assert result.syntax_valid is False
        assert len(result.issues) > 0

    @pytest.mark.asyncio
    async def test_validate_javascript(self):
        """Test JavaScript validation"""
        code = "const x = 42; console.log(x);"

        result = await LanguageValidator.validate_javascript(code)

        assert result.language == Language.JAVASCRIPT
        # Should have warning about console.log
        console_issues = [i for i in result.issues if "console.log" in i.message]
        assert len(console_issues) > 0

    @pytest.mark.asyncio
    async def test_validate_typescript(self):
        """Test TypeScript validation"""
        code = "let x: any = 42;"

        result = await LanguageValidator.validate_typescript(code)

        assert result.language == Language.TYPESCRIPT
        # Should warn about 'any' type
        any_issues = [i for i in result.issues if "any" in i.message]
        assert len(any_issues) > 0

    @pytest.mark.asyncio
    async def test_validate_go(self):
        """Test Go validation"""
        code = "package main\n\nfunc main() {}"

        result = await LanguageValidator.validate_go(code)

        assert result.language == Language.GO

    @pytest.mark.asyncio
    async def test_validate_java(self):
        """Test Java validation"""
        code = "public class Main {\n  public static void main(String[] args) {}\n}"

        result = await LanguageValidator.validate_java(code)

        assert result.language == Language.JAVA

    @pytest.mark.asyncio
    async def test_validate_rust(self):
        """Test Rust validation"""
        code = "fn main() {\n  let x = Some(42).unwrap();\n}"

        result = await LanguageValidator.validate_rust(code)

        assert result.language == Language.RUST
        # Should warn about unwrap
        unwrap_issues = [i for i in result.issues if "unwrap" in i.message]
        assert len(unwrap_issues) > 0


class TestLanguageRouter:
    """Test language router"""

    @pytest.mark.asyncio
    async def test_analyze_python_code(self):
        """Test analyzing Python code"""
        router = LanguageRouter()

        code = "def hello():\n    return 42"

        result = await router.analyze(code, file_path="script.py")

        assert result.language == Language.PYTHON
        assert result.confidence > 0.8
        assert result.formatting is not None
        assert result.validation is not None

    @pytest.mark.asyncio
    async def test_analyze_javascript_code(self):
        """Test analyzing JavaScript code"""
        router = LanguageRouter()

        code = "function hello() { return 42; }"

        result = await router.analyze(code, file_path="app.js")

        assert result.language == Language.JAVASCRIPT
        assert result.formatting is not None
        assert result.validation is not None

    @pytest.mark.asyncio
    async def test_format_code_auto_detect(self):
        """Test formatting with auto-detected language"""
        router = LanguageRouter()

        code = "def hello():\n  return 42"

        result = await router.format_code(code, file_path="test.py")

        assert result.success is True
        assert result.formatted_code is not None

    @pytest.mark.asyncio
    async def test_validate_code_auto_detect(self):
        """Test validation with auto-detected language"""
        router = LanguageRouter()

        code = "const x = 42;"

        result = await router.validate_code(code, file_path="app.js")

        assert result.language == Language.JAVASCRIPT

    @pytest.mark.asyncio
    async def test_analyze_multiple_files(self):
        """Test analyzing multiple files"""
        router = LanguageRouter()

        files = {
            "test.py": "def hello(): return 42",
            "app.js": "function hello() { return 42; }",
            "main.go": "package main; func main() {}",
        }

        results = await router.analyze_files(files)

        assert len(results) == 3
        assert results["test.py"].language == Language.PYTHON
        assert results["app.js"].language == Language.JAVASCRIPT
        assert results["main.go"].language == Language.GO

    def test_get_supported_languages(self):
        """Test getting supported languages"""
        router = LanguageRouter()

        langs = router.get_supported_languages()

        assert len(langs) == 6  # 6 languages supported
        assert Language.PYTHON in langs
        assert Language.RUST in langs

    def test_global_router(self):
        """Test global router instance"""
        router = get_language_router()

        assert router is not None
        assert len(router.get_supported_languages()) == 6


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
