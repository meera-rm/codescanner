"""
Language-Specific Formatters - Phase 5.3
Formatting code in multiple languages
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
import re

from .language_detector import Language


@dataclass
class FormattingResult:
    """Result of formatting operation"""
    success: bool
    formatted_code: Optional[str]
    error: Optional[str]
    changes_made: int
    lines_changed: int


class LanguageFormatter:
    """Base formatter for all languages"""

    @staticmethod
    async def format_python(code: str, config: Optional[Dict] = None) -> FormattingResult:
        """Format Python code (Black style)"""
        try:
            # Simulate Black formatting
            lines = code.split('\n')
            formatted = []
            changes = 0

            for line in lines:
                original = line
                # Remove trailing whitespace
                line = line.rstrip()
                # Ensure consistent indentation (4 spaces)
                if line and line[0] == ' ':
                    indent = len(line) - len(line.lstrip())
                    if indent % 4 != 0:
                        # Adjust indent to nearest 4-space boundary
                        new_indent = (indent // 4) * 4
                        line = ' ' * new_indent + line.lstrip()
                        changes += 1

                formatted.append(line)
                if original != line:
                    changes += 1

            result = '\n'.join(formatted)

            return FormattingResult(
                success=True,
                formatted_code=result,
                error=None,
                changes_made=changes,
                lines_changed=len([l for l in formatted if l != original])
            )

        except Exception as e:
            return FormattingResult(
                success=False,
                formatted_code=None,
                error=str(e),
                changes_made=0,
                lines_changed=0
            )

    @staticmethod
    async def format_javascript(code: str, config: Optional[Dict] = None) -> FormattingResult:
        """Format JavaScript code (Prettier style)"""
        try:
            lines = code.split('\n')
            formatted = []
            changes = 0

            for line in lines:
                original = line
                # Remove trailing whitespace
                line = line.rstrip()
                # Ensure 2-space indentation
                if line and line[0] == ' ':
                    indent = len(line) - len(line.lstrip())
                    if indent % 2 != 0:
                        new_indent = (indent // 2) * 2
                        line = ' ' * new_indent + line.lstrip()
                        changes += 1

                formatted.append(line)

            result = '\n'.join(formatted)

            return FormattingResult(
                success=True,
                formatted_code=result,
                error=None,
                changes_made=changes,
                lines_changed=changes
            )

        except Exception as e:
            return FormattingResult(
                success=False,
                formatted_code=None,
                error=str(e),
                changes_made=0,
                lines_changed=0
            )

    @staticmethod
    async def format_typescript(code: str, config: Optional[Dict] = None) -> FormattingResult:
        """Format TypeScript code (Prettier style)"""
        # TypeScript uses same formatting as JavaScript
        return await LanguageFormatter.format_javascript(code, config)

    @staticmethod
    async def format_go(code: str, config: Optional[Dict] = None) -> FormattingResult:
        """Format Go code (gofmt style)"""
        try:
            lines = code.split('\n')
            formatted = []
            changes = 0

            for line in lines:
                original = line
                line = line.rstrip()
                # Go uses tabs for indentation
                if line and line[0] == ' ':
                    # Convert spaces to tabs
                    indent = len(line) - len(line.lstrip())
                    tab_count = indent // 8
                    line = '\t' * tab_count + line.lstrip()
                    changes += 1

                formatted.append(line)

            result = '\n'.join(formatted)

            return FormattingResult(
                success=True,
                formatted_code=result,
                error=None,
                changes_made=changes,
                lines_changed=changes
            )

        except Exception as e:
            return FormattingResult(
                success=False,
                formatted_code=None,
                error=str(e),
                changes_made=0,
                lines_changed=0
            )

    @staticmethod
    async def format_java(code: str, config: Optional[Dict] = None) -> FormattingResult:
        """Format Java code (Google Java Format style)"""
        try:
            lines = code.split('\n')
            formatted = []
            changes = 0

            for line in lines:
                original = line
                line = line.rstrip()
                # Java uses 4-space indentation
                if line and line[0] == ' ':
                    indent = len(line) - len(line.lstrip())
                    if indent % 4 != 0:
                        new_indent = (indent // 4) * 4
                        line = ' ' * new_indent + line.lstrip()
                        changes += 1

                formatted.append(line)

            result = '\n'.join(formatted)

            return FormattingResult(
                success=True,
                formatted_code=result,
                error=None,
                changes_made=changes,
                lines_changed=changes
            )

        except Exception as e:
            return FormattingResult(
                success=False,
                formatted_code=None,
                error=str(e),
                changes_made=0,
                lines_changed=0
            )

    @staticmethod
    async def format_rust(code: str, config: Optional[Dict] = None) -> FormattingResult:
        """Format Rust code (rustfmt style)"""
        try:
            lines = code.split('\n')
            formatted = []
            changes = 0

            for line in lines:
                original = line
                line = line.rstrip()
                # Rust uses 4-space indentation
                if line and line[0] == ' ':
                    indent = len(line) - len(line.lstrip())
                    if indent % 4 != 0:
                        new_indent = (indent // 4) * 4
                        line = ' ' * new_indent + line.lstrip()
                        changes += 1

                formatted.append(line)

            result = '\n'.join(formatted)

            return FormattingResult(
                success=True,
                formatted_code=result,
                error=None,
                changes_made=changes,
                lines_changed=changes
            )

        except Exception as e:
            return FormattingResult(
                success=False,
                formatted_code=None,
                error=str(e),
                changes_made=0,
                lines_changed=0
            )

    @staticmethod
    async def format(
        code: str,
        language: Language,
        config: Optional[Dict] = None
    ) -> FormattingResult:
        """Format code in specified language"""
        formatters = {
            Language.PYTHON: LanguageFormatter.format_python,
            Language.JAVASCRIPT: LanguageFormatter.format_javascript,
            Language.TYPESCRIPT: LanguageFormatter.format_typescript,
            Language.GO: LanguageFormatter.format_go,
            Language.JAVA: LanguageFormatter.format_java,
            Language.RUST: LanguageFormatter.format_rust,
        }

        if language not in formatters:
            return FormattingResult(
                success=False,
                formatted_code=None,
                error=f"Unsupported language: {language.value}",
                changes_made=0,
                lines_changed=0
            )

        formatter = formatters[language]
        return await formatter(code, config)
