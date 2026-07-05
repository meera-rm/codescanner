"""
Code Formatter Service - Phase 4.2b
Formats code using language-specific formatters (Black, Prettier)
"""

import subprocess
import asyncio
import logging
from pathlib import Path
from typing import Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)


class Language(Enum):
    """Supported languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    JSON = "json"
    UNKNOWN = "unknown"


class FormatterResult:
    """Result of code formatting"""
    def __init__(
        self,
        success: bool,
        formatted_code: Optional[str] = None,
        original_code: Optional[str] = None,
        language: str = None,
        error: Optional[str] = None,
        lines_changed: int = 0,
    ):
        self.success = success
        self.formatted_code = formatted_code
        self.original_code = original_code
        self.language = language
        self.error = error
        self.lines_changed = lines_changed


class CodeFormatter:
    """Format code using language-specific formatters"""

    def __init__(self):
        self.black_available = self._check_black_available()
        self.prettier_available = self._check_prettier_available()

    def _check_black_available(self) -> bool:
        """Check if black is installed"""
        try:
            subprocess.run(
                ["black", "--version"],
                capture_output=True,
                timeout=5,
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Black formatter not available")
            return False

    def _check_prettier_available(self) -> bool:
        """Check if prettier is installed"""
        try:
            subprocess.run(
                ["prettier", "--version"],
                capture_output=True,
                timeout=5,
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Prettier formatter not available")
            return False

    def detect_language(self, file_path: str) -> Language:
        """Detect language from file extension"""
        path = Path(file_path)
        ext = path.suffix.lower()

        extension_map = {
            ".py": Language.PYTHON,
            ".pyw": Language.PYTHON,
            ".js": Language.JAVASCRIPT,
            ".jsx": Language.JAVASCRIPT,
            ".ts": Language.TYPESCRIPT,
            ".tsx": Language.TYPESCRIPT,
            ".json": Language.JSON,
        }

        return extension_map.get(ext, Language.UNKNOWN)

    def detect_language_from_content(self, code: str) -> Language:
        """Detect language from code content"""
        # Check for Python indicators
        if any(indicator in code for indicator in ["def ", "import ", "class ", "from "]):
            return Language.PYTHON

        # Check for JavaScript/TypeScript indicators
        if any(indicator in code for indicator in ["function ", "const ", "let ", "var "]):
            return Language.JAVASCRIPT

        return Language.UNKNOWN

    async def format_code(
        self,
        code: str,
        language: Optional[Language] = None,
        file_path: Optional[str] = None,
    ) -> FormatterResult:
        """
        Format code using appropriate formatter.

        Args:
            code: Code to format
            language: Language (auto-detect if not provided)
            file_path: File path (used for language detection)

        Returns:
            FormatterResult with formatted code
        """
        try:
            # Detect language if not provided
            if language is None:
                if file_path:
                    language = self.detect_language(file_path)
                if language == Language.UNKNOWN:
                    language = self.detect_language_from_content(code)

            # Format based on language
            if language == Language.PYTHON:
                return await self._format_python(code)
            elif language in [Language.JAVASCRIPT, Language.TYPESCRIPT]:
                return await self._format_javascript(code)
            elif language == Language.JSON:
                return await self._format_json(code)
            else:
                return FormatterResult(
                    success=False,
                    original_code=code,
                    error="Unable to detect language",
                )

        except Exception as e:
            logger.error(f"Error formatting code: {e}")
            return FormatterResult(
                success=False,
                original_code=code,
                error=str(e),
            )

    async def _format_python(self, code: str) -> FormatterResult:
        """Format Python code using Black"""
        try:
            if not self.black_available:
                logger.warning("Black not available, returning unformatted code")
                return FormatterResult(
                    success=True,
                    formatted_code=code,
                    original_code=code,
                    language="python",
                )

            # Run black in subprocess
            result = await asyncio.to_thread(
                self._run_black,
                code,
            )

            return result

        except Exception as e:
            logger.error(f"Error formatting Python code: {e}")
            return FormatterResult(
                success=False,
                original_code=code,
                language="python",
                error=str(e),
            )

    def _run_black(self, code: str) -> FormatterResult:
        """Run black formatter (subprocess)"""
        try:
            # Write code to temp file for formatting
            import tempfile
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
            ) as f:
                f.write(code)
                temp_path = f.name

            try:
                # Run black
                subprocess.run(
                    ["black", temp_path, "--quiet"],
                    capture_output=True,
                    timeout=10,
                    check=False,
                )

                # Read formatted code
                with open(temp_path, "r") as f:
                    formatted = f.read()

                lines_changed = abs(len(code.split("\n")) - len(formatted.split("\n")))

                return FormatterResult(
                    success=True,
                    formatted_code=formatted,
                    original_code=code,
                    language="python",
                    lines_changed=lines_changed,
                )

            finally:
                # Clean up temp file
                import os
                try:
                    os.unlink(temp_path)
                except:
                    pass

        except subprocess.TimeoutExpired:
            logger.error("Black formatting timed out")
            return FormatterResult(
                success=False,
                original_code=code,
                language="python",
                error="Formatting timed out",
            )
        except Exception as e:
            logger.error(f"Error running black: {e}")
            return FormatterResult(
                success=False,
                original_code=code,
                language="python",
                error=str(e),
            )

    async def _format_javascript(self, code: str) -> FormatterResult:
        """Format JavaScript code using Prettier"""
        try:
            if not self.prettier_available:
                logger.warning("Prettier not available, returning unformatted code")
                return FormatterResult(
                    success=True,
                    formatted_code=code,
                    original_code=code,
                    language="javascript",
                )

            # Run prettier in subprocess
            result = await asyncio.to_thread(
                self._run_prettier,
                code,
            )

            return result

        except Exception as e:
            logger.error(f"Error formatting JavaScript code: {e}")
            return FormatterResult(
                success=False,
                original_code=code,
                language="javascript",
                error=str(e),
            )

    def _run_prettier(self, code: str) -> FormatterResult:
        """Run prettier formatter (subprocess)"""
        try:
            # Run prettier on stdin
            result = subprocess.run(
                ["prettier", "--parser", "babel"],
                input=code.encode("utf-8"),
                capture_output=True,
                timeout=10,
            )

            if result.returncode != 0:
                error = result.stderr.decode("utf-8", errors="replace")
                logger.error(f"Prettier error: {error}")
                return FormatterResult(
                    success=False,
                    original_code=code,
                    language="javascript",
                    error=error,
                )

            formatted = result.stdout.decode("utf-8")
            lines_changed = abs(len(code.split("\n")) - len(formatted.split("\n")))

            return FormatterResult(
                success=True,
                formatted_code=formatted,
                original_code=code,
                language="javascript",
                lines_changed=lines_changed,
            )

        except subprocess.TimeoutExpired:
            logger.error("Prettier formatting timed out")
            return FormatterResult(
                success=False,
                original_code=code,
                language="javascript",
                error="Formatting timed out",
            )
        except Exception as e:
            logger.error(f"Error running prettier: {e}")
            return FormatterResult(
                success=False,
                original_code=code,
                language="javascript",
                error=str(e),
            )

    async def _format_json(self, code: str) -> FormatterResult:
        """Format JSON code"""
        try:
            import json

            # Parse and re-format JSON
            data = json.loads(code)
            formatted = json.dumps(data, indent=2, sort_keys=True)

            lines_changed = abs(len(code.split("\n")) - len(formatted.split("\n")))

            return FormatterResult(
                success=True,
                formatted_code=formatted,
                original_code=code,
                language="json",
                lines_changed=lines_changed,
            )

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            return FormatterResult(
                success=False,
                original_code=code,
                language="json",
                error=f"Invalid JSON: {e}",
            )
        except Exception as e:
            logger.error(f"Error formatting JSON: {e}")
            return FormatterResult(
                success=False,
                original_code=code,
                language="json",
                error=str(e),
            )

    def get_formatter_status(self) -> dict:
        """Get status of available formatters"""
        return {
            "black": self.black_available,
            "prettier": self.prettier_available,
            "formatters_available": self.black_available or self.prettier_available,
        }


# Singleton instance
_code_formatter = None


def get_code_formatter() -> CodeFormatter:
    """Get or create CodeFormatter instance"""
    global _code_formatter
    if _code_formatter is None:
        _code_formatter = CodeFormatter()
    return _code_formatter
