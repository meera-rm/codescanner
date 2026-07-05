"""
Language-Specific Validators - Phase 5.3
Validation (syntax, linting, type checking) for multiple languages
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import re
import ast

from .language_detector import Language


@dataclass
class ValidationIssue:
    """Single validation issue"""
    line: int
    column: int
    severity: str  # "error", "warning"
    code: str
    message: str


@dataclass
class ValidationResult:
    """Result of validation"""
    success: bool
    language: Language
    syntax_valid: bool
    issues: List[ValidationIssue]
    error: Optional[str]


class LanguageValidator:
    """Validates code in multiple languages"""

    @staticmethod
    async def validate_python(code: str) -> ValidationResult:
        """Validate Python code"""
        issues = []

        # Check syntax
        try:
            ast.parse(code)
            syntax_valid = True
        except SyntaxError as e:
            syntax_valid = False
            issues.append(ValidationIssue(
                line=e.lineno or 1,
                column=e.offset or 1,
                severity="error",
                code="E999",
                message=f"SyntaxError: {e.msg}"
            ))

        # Basic linting checks
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check trailing whitespace
            if line.rstrip() != line:
                issues.append(ValidationIssue(
                    line=i,
                    column=len(line.rstrip()) + 1,
                    severity="warning",
                    code="W291",
                    message="Trailing whitespace"
                ))

            # Check line length
            if len(line) > 100:
                issues.append(ValidationIssue(
                    line=i,
                    column=100,
                    severity="warning",
                    code="E501",
                    message="Line too long (> 100 characters)"
                ))

        return ValidationResult(
            success=len([i for i in issues if i.severity == "error"]) == 0,
            language=Language.PYTHON,
            syntax_valid=syntax_valid,
            issues=issues,
            error=None
        )

    @staticmethod
    async def validate_javascript(code: str) -> ValidationResult:
        """Validate JavaScript code"""
        issues = []

        # Check for common syntax errors
        # Check for unmatched braces/brackets/parens
        brace_count = code.count('{') - code.count('}')
        bracket_count = code.count('[') - code.count(']')
        paren_count = code.count('(') - code.count(')')

        if brace_count != 0:
            issues.append(ValidationIssue(
                line=1,
                column=1,
                severity="error",
                code="E001",
                message="Unmatched braces"
            ))

        if bracket_count != 0:
            issues.append(ValidationIssue(
                line=1,
                column=1,
                severity="error",
                code="E002",
                message="Unmatched brackets"
            ))

        if paren_count != 0:
            issues.append(ValidationIssue(
                line=1,
                column=1,
                severity="error",
                code="E003",
                message="Unmatched parentheses"
            ))

        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for console.log (warning in production)
            if 'console.log' in line:
                issues.append(ValidationIssue(
                    line=i,
                    column=line.index('console.log') + 1,
                    severity="warning",
                    code="W001",
                    message="console.log found (remove before production)"
                ))

            # Check trailing whitespace
            if line.rstrip() != line:
                issues.append(ValidationIssue(
                    line=i,
                    column=len(line.rstrip()) + 1,
                    severity="warning",
                    code="W291",
                    message="Trailing whitespace"
                ))

        return ValidationResult(
            success=len([i for i in issues if i.severity == "error"]) == 0,
            language=Language.JAVASCRIPT,
            syntax_valid=len([i for i in issues if i.severity == "error"]) == 0,
            issues=issues,
            error=None
        )

    @staticmethod
    async def validate_typescript(code: str) -> ValidationResult:
        """Validate TypeScript code"""
        # TypeScript validation includes JavaScript validation + type checking
        js_result = await LanguageValidator.validate_javascript(code)

        # Add TypeScript-specific checks
        issues = js_result.issues.copy()

        # Check for type annotations
        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for 'any' type (should avoid)
            if re.search(r':\s*any\b', line):
                issues.append(ValidationIssue(
                    line=i,
                    column=line.index('any') + 1,
                    severity="warning",
                    code="T001",
                    message="Avoid 'any' type - use specific types"
                ))

        return ValidationResult(
            success=js_result.success,
            language=Language.TYPESCRIPT,
            syntax_valid=js_result.syntax_valid,
            issues=issues,
            error=None
        )

    @staticmethod
    async def validate_go(code: str) -> ValidationResult:
        """Validate Go code"""
        issues = []

        # Check for package declaration
        if not re.search(r'^package\s+\w+', code, re.MULTILINE):
            issues.append(ValidationIssue(
                line=1,
                column=1,
                severity="error",
                code="G001",
                message="Missing package declaration"
            ))

        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for defer without context
            if 'defer' in line and 'err' not in code:
                issues.append(ValidationIssue(
                    line=i,
                    column=line.index('defer') + 1,
                    severity="warning",
                    code="G002",
                    message="Consider error handling with defer"
                ))

        return ValidationResult(
            success=len([i for i in issues if i.severity == "error"]) == 0,
            language=Language.GO,
            syntax_valid=len([i for i in issues if i.severity == "error"]) == 0,
            issues=issues,
            error=None
        )

    @staticmethod
    async def validate_java(code: str) -> ValidationResult:
        """Validate Java code"""
        issues = []

        # Check for class declaration
        if not re.search(r'(public\s+)?(class|interface)\s+\w+', code):
            issues.append(ValidationIssue(
                line=1,
                column=1,
                severity="error",
                code="J001",
                message="Missing class or interface declaration"
            ))

        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for proper import statements
            if line.strip().startswith('import ') and not line.strip().endswith(';'):
                issues.append(ValidationIssue(
                    line=i,
                    column=len(line),
                    severity="error",
                    code="J002",
                    message="Import statement missing semicolon"
                ))

        return ValidationResult(
            success=len([i for i in issues if i.severity == "error"]) == 0,
            language=Language.JAVA,
            syntax_valid=len([i for i in issues if i.severity == "error"]) == 0,
            issues=issues,
            error=None
        )

    @staticmethod
    async def validate_rust(code: str) -> ValidationResult:
        """Validate Rust code"""
        issues = []

        lines = code.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for unwrap (should avoid in production)
            if 'unwrap()' in line:
                issues.append(ValidationIssue(
                    line=i,
                    column=line.index('unwrap') + 1,
                    severity="warning",
                    code="R001",
                    message="Consider using ? operator instead of unwrap()"
                ))

            # Check for todo! macro
            if 'todo!' in line:
                issues.append(ValidationIssue(
                    line=i,
                    column=line.index('todo!') + 1,
                    severity="warning",
                    code="R002",
                    message="Unimplemented code found"
                ))

        return ValidationResult(
            success=len([i for i in issues if i.severity == "error"]) == 0,
            language=Language.RUST,
            syntax_valid=len([i for i in issues if i.severity == "error"]) == 0,
            issues=issues,
            error=None
        )

    @staticmethod
    async def validate(
        code: str,
        language: Language
    ) -> ValidationResult:
        """Validate code in specified language"""
        validators = {
            Language.PYTHON: LanguageValidator.validate_python,
            Language.JAVASCRIPT: LanguageValidator.validate_javascript,
            Language.TYPESCRIPT: LanguageValidator.validate_typescript,
            Language.GO: LanguageValidator.validate_go,
            Language.JAVA: LanguageValidator.validate_java,
            Language.RUST: LanguageValidator.validate_rust,
        }

        if language not in validators:
            return ValidationResult(
                success=False,
                language=language,
                syntax_valid=False,
                issues=[],
                error=f"Unsupported language: {language.value}"
            )

        validator = validators[language]
        return await validator(code)
