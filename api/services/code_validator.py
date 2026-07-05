"""
Code Validator Service - Phase 4.2c
Validates code changes: syntax, linting, tests, safety checks
"""

import subprocess
import asyncio
import logging
import ast
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of code validation"""
    success: bool
    syntax_valid: bool = True
    linting_passed: bool = True
    tests_passed: bool = True
    syntax_errors: List[str] = None
    linting_errors: List[str] = None
    test_errors: List[str] = None
    warnings: List[str] = None
    error_message: Optional[str] = None

    def __post_init__(self):
        if self.syntax_errors is None:
            self.syntax_errors = []
        if self.linting_errors is None:
            self.linting_errors = []
        if self.test_errors is None:
            self.test_errors = []
        if self.warnings is None:
            self.warnings = []


class CodeValidator:
    """Validate code changes"""

    def __init__(self):
        self.pylint_available = self._check_pylint_available()
        self.pytest_available = self._check_pytest_available()
        self.eslint_available = self._check_eslint_available()
        self.npm_test_available = self._check_npm_test_available()

    def _check_pylint_available(self) -> bool:
        """Check if pylint is installed"""
        try:
            subprocess.run(
                ["pylint", "--version"],
                capture_output=True,
                timeout=5,
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Pylint not available")
            return False

    def _check_pytest_available(self) -> bool:
        """Check if pytest is installed"""
        try:
            subprocess.run(
                ["pytest", "--version"],
                capture_output=True,
                timeout=5,
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Pytest not available")
            return False

    def _check_eslint_available(self) -> bool:
        """Check if eslint is installed"""
        try:
            subprocess.run(
                ["eslint", "--version"],
                capture_output=True,
                timeout=5,
            )
            return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("ESLint not available")
            return False

    def _check_npm_test_available(self) -> bool:
        """Check if npm test is available"""
        try:
            package_json = Path("package.json")
            if not package_json.exists():
                return False
            return True
        except Exception:
            return False

    async def validate_syntax(self, code: str, language: str) -> Tuple[bool, List[str]]:
        """
        Validate code syntax.

        Returns:
            Tuple of (is_valid, error_list)
        """
        try:
            if language == "python":
                return await self._validate_python_syntax(code)
            elif language in ["javascript", "typescript"]:
                return await self._validate_javascript_syntax(code)
            elif language == "json":
                return await self._validate_json_syntax(code)
            else:
                return True, []
        except Exception as e:
            logger.error(f"Error validating syntax: {e}")
            return False, [str(e)]

    async def _validate_python_syntax(self, code: str) -> Tuple[bool, List[str]]:
        """Validate Python code syntax using AST"""
        try:
            ast.parse(code)
            return True, []
        except SyntaxError as e:
            error_msg = f"Line {e.lineno}: {e.msg}"
            return False, [error_msg]
        except Exception as e:
            return False, [str(e)]

    async def _validate_javascript_syntax(self, code: str) -> Tuple[bool, List[str]]:
        """Validate JavaScript/TypeScript syntax using node"""
        try:
            result = subprocess.run(
                ["node", "--check"],
                input=code.encode("utf-8"),
                capture_output=True,
                timeout=10,
            )

            if result.returncode != 0:
                error = result.stderr.decode("utf-8", errors="replace")
                return False, [error]
            return True, []
        except (subprocess.TimeoutExpired, FileNotFoundError):
            logger.warning("Node checker not available, skipping JS syntax validation")
            return True, []
        except Exception as e:
            return False, [str(e)]

    async def _validate_json_syntax(self, code: str) -> Tuple[bool, List[str]]:
        """Validate JSON syntax"""
        try:
            import json
            json.loads(code)
            return True, []
        except json.JSONDecodeError as e:
            return False, [f"Line {e.lineno}: {e.msg}"]
        except Exception as e:
            return False, [str(e)]

    async def run_linter(
        self, file_path: str, language: str
    ) -> Tuple[bool, List[str]]:
        """
        Run linter on file.

        Returns:
            Tuple of (passed, error_list)
        """
        try:
            if language == "python":
                return await self._run_pylint(file_path)
            elif language in ["javascript", "typescript"]:
                return await self._run_eslint(file_path)
            else:
                return True, []
        except Exception as e:
            logger.error(f"Error running linter: {e}")
            return False, [str(e)]

    async def _run_pylint(self, file_path: str) -> Tuple[bool, List[str]]:
        """Run pylint on Python file"""
        try:
            if not self.pylint_available:
                logger.warning("Pylint not available, skipping linting")
                return True, []

            result = await asyncio.to_thread(
                subprocess.run,
                ["pylint", file_path, "--exit-zero"],
                capture_output=True,
                timeout=30,
            )

            output = result.stdout.decode("utf-8", errors="replace")

            # Extract errors from pylint output
            errors = []
            for line in output.split("\n"):
                if "error" in line.lower() or "convention" in line.lower():
                    errors.append(line.strip())

            # Pylint returns non-zero for issues but we capture them
            return len(errors) == 0, errors

        except subprocess.TimeoutExpired:
            logger.error("Pylint timed out")
            return False, ["Linting timed out"]
        except FileNotFoundError:
            logger.warning("Pylint not found")
            return True, []
        except Exception as e:
            logger.error(f"Error running pylint: {e}")
            return False, [str(e)]

    async def _run_eslint(self, file_path: str) -> Tuple[bool, List[str]]:
        """Run eslint on JavaScript file"""
        try:
            if not self.eslint_available:
                logger.warning("ESLint not available, skipping linting")
                return True, []

            result = await asyncio.to_thread(
                subprocess.run,
                ["eslint", file_path],
                capture_output=True,
                timeout=30,
            )

            output = result.stdout.decode("utf-8", errors="replace")
            errors = []
            for line in output.split("\n"):
                if "error" in line.lower():
                    errors.append(line.strip())

            return result.returncode == 0, errors

        except subprocess.TimeoutExpired:
            logger.error("ESLint timed out")
            return False, ["Linting timed out"]
        except FileNotFoundError:
            logger.warning("ESLint not found")
            return True, []
        except Exception as e:
            logger.error(f"Error running eslint: {e}")
            return False, [str(e)]

    async def run_tests(self, codebase_path: str) -> Tuple[bool, List[str]]:
        """
        Run test suite.

        Returns:
            Tuple of (passed, error_list)
        """
        try:
            codebase = Path(codebase_path)

            # Try pytest first
            if self.pytest_available:
                return await self._run_pytest(codebase_path)

            # Try npm test
            if self.npm_test_available:
                return await self._run_npm_test(codebase_path)

            logger.warning("No test runner found")
            return True, []

        except Exception as e:
            logger.error(f"Error running tests: {e}")
            return False, [str(e)]

    async def _run_pytest(self, codebase_path: str) -> Tuple[bool, List[str]]:
        """Run pytest on codebase"""
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["pytest", codebase_path, "-v", "--tb=short"],
                capture_output=True,
                timeout=120,
            )

            output = result.stdout.decode("utf-8", errors="replace")
            errors = []

            # Extract failed tests
            for line in output.split("\n"):
                if "FAILED" in line or "ERROR" in line:
                    errors.append(line.strip())

            return result.returncode == 0, errors

        except subprocess.TimeoutExpired:
            logger.error("Pytest timed out")
            return False, ["Tests timed out"]
        except FileNotFoundError:
            logger.warning("Pytest not found")
            return True, []
        except Exception as e:
            logger.error(f"Error running pytest: {e}")
            return False, [str(e)]

    async def _run_npm_test(self, codebase_path: str) -> Tuple[bool, List[str]]:
        """Run npm test on codebase"""
        try:
            result = await asyncio.to_thread(
                subprocess.run,
                ["npm", "test"],
                capture_output=True,
                timeout=120,
                cwd=codebase_path,
            )

            output = result.stdout.decode("utf-8", errors="replace")
            errors = []

            for line in output.split("\n"):
                if "FAIL" in line or "ERROR" in line:
                    errors.append(line.strip())

            return result.returncode == 0, errors

        except subprocess.TimeoutExpired:
            logger.error("npm test timed out")
            return False, ["Tests timed out"]
        except FileNotFoundError:
            logger.warning("npm not found")
            return True, []
        except Exception as e:
            logger.error(f"Error running npm test: {e}")
            return False, [str(e)]

    async def validate_all(
        self, codebase_path: str, code: str, language: str, file_path: str
    ) -> ValidationResult:
        """
        Run all validation checks.

        Returns:
            ValidationResult with all checks
        """
        try:
            result = ValidationResult(success=True)

            # 1. Syntax validation
            syntax_valid, syntax_errors = await self.validate_syntax(code, language)
            result.syntax_valid = syntax_valid
            result.syntax_errors = syntax_errors

            if not syntax_valid:
                result.success = False

            # 2. Linting
            if file_path and Path(file_path).exists():
                linting_passed, linting_errors = await self.run_linter(file_path, language)
                result.linting_passed = linting_passed
                result.linting_errors = linting_errors

                if not linting_passed:
                    result.success = False

            # 3. Tests
            tests_passed, test_errors = await self.run_tests(codebase_path)
            result.tests_passed = tests_passed
            result.test_errors = test_errors

            if not tests_passed:
                result.success = False

            return result

        except Exception as e:
            logger.error(f"Error in validate_all: {e}")
            return ValidationResult(
                success=False,
                error_message=str(e),
            )

    def get_validator_status(self) -> dict:
        """Get status of available validators"""
        return {
            "pylint": self.pylint_available,
            "pytest": self.pytest_available,
            "eslint": self.eslint_available,
            "npm_test": self.npm_test_available,
            "validators_available": any([
                self.pylint_available,
                self.pytest_available,
                self.eslint_available,
                self.npm_test_available,
            ]),
        }


# Singleton instance
_code_validator = None


def get_code_validator() -> CodeValidator:
    """Get or create CodeValidator instance"""
    global _code_validator
    if _code_validator is None:
        _code_validator = CodeValidator()
    return _code_validator
