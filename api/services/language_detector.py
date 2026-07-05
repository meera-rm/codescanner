"""
Language Detector - Phase 5.3
Detects programming language from code or file path
"""

from typing import Optional, Dict, List, Tuple
from enum import Enum
import re


class Language(str, Enum):
    """Supported programming languages"""
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    GO = "go"
    JAVA = "java"
    RUST = "rust"
    UNKNOWN = "unknown"


class LanguageDetector:
    """Detects programming language"""

    # File extensions mapping
    EXTENSIONS_MAP = {
        # Python
        ".py": Language.PYTHON,
        ".pyw": Language.PYTHON,
        ".pyx": Language.PYTHON,
        ".pyi": Language.PYTHON,

        # JavaScript
        ".js": Language.JAVASCRIPT,
        ".jsx": Language.JAVASCRIPT,
        ".mjs": Language.JAVASCRIPT,

        # TypeScript
        ".ts": Language.TYPESCRIPT,
        ".tsx": Language.TYPESCRIPT,

        # Go
        ".go": Language.GO,

        # Java
        ".java": Language.JAVA,

        # Rust
        ".rs": Language.RUST,
    }

    # Language-specific patterns
    PATTERNS = {
        Language.PYTHON: [
            r"^#!/usr/bin/env python",
            r"^import\s+\w+",
            r"^from\s+\w+\s+import",
            r"^def\s+\w+\(",
            r"^class\s+\w+",
            r"^\s+self\.",
            r"if\s+__name__\s*==\s*['\"]__main__['\"]",
        ],
        Language.JAVASCRIPT: [
            r"^\s*const\s+\w+\s*=",
            r"^\s*let\s+\w+\s*=",
            r"^\s*var\s+\w+\s*=",
            r"^\s*function\s+\w+\s*\(",
            r"=>\s*\{",
            r"require\(['\"]",
            r"module\.exports",
            r"console\.log",
        ],
        Language.TYPESCRIPT: [
            r":\s*(string|number|boolean|any|void|interface|type)",
            r"interface\s+\w+\s*\{",
            r"type\s+\w+\s*=",
            r"<\w+>",  # Generics
            r"async\s+function",
            r"await\s+",
        ],
        Language.GO: [
            r"^package\s+\w+",
            r"^import\s*\(",
            r"func\s+\w+\s*\(",
            r"func\s+\(\w+\s+\*?\w+\)",
            r":=",
            r"interface\s*\{\}",
        ],
        Language.JAVA: [
            r"^package\s+",
            r"^import\s+",
            r"^(public|private|protected)\s+(static\s+)?class\s+",
            r"^(public|private|protected)\s+(static\s+)?(void|int|String|boolean)\s+\w+\s*\(",
            r"new\s+\w+\s*\(",
            r"@Override",
        ],
        Language.RUST: [
            r"^fn\s+\w+\(",
            r"let\s+\w+\s*:",
            r"match\s+",
            r"impl\s+\w+",
            r"pub\s+(fn|struct|enum|trait)",
            r"use\s+\w+::",
            r"cargo",
        ],
    }

    @staticmethod
    def detect_from_path(file_path: str) -> Language:
        """Detect language from file path"""
        # Get file extension
        for ext, lang in LanguageDetector.EXTENSIONS_MAP.items():
            if file_path.lower().endswith(ext):
                return lang

        return Language.UNKNOWN

    @staticmethod
    def detect_from_content(code: str) -> Language:
        """Detect language from code content"""
        lines = code.split('\n')[:50]  # Check first 50 lines
        code_sample = '\n'.join(lines)

        scores = {}

        for lang, patterns in LanguageDetector.PATTERNS.items():
            matches = 0
            for pattern in patterns:
                if re.search(pattern, code_sample, re.MULTILINE):
                    matches += 1

            if matches > 0:
                scores[lang] = matches

        if not scores:
            return Language.UNKNOWN

        return max(scores, key=scores.get)

    @staticmethod
    def detect(
        code: str,
        file_path: Optional[str] = None
    ) -> Tuple[Language, float]:
        """
        Detect language from code and optional file path

        Returns: (Language, confidence_score)
        """
        confidence = 0.5

        # Try path-based detection first (highest confidence)
        if file_path:
            path_lang = LanguageDetector.detect_from_path(file_path)
            if path_lang != Language.UNKNOWN:
                return path_lang, 0.95

        # Fall back to content-based detection
        content_lang = LanguageDetector.detect_from_content(code)

        if content_lang != Language.UNKNOWN:
            return content_lang, 0.80

        return Language.UNKNOWN, 0.0

    @staticmethod
    def get_language_info(lang: Language) -> Dict[str, any]:
        """Get information about a language"""
        info_map = {
            Language.PYTHON: {
                "name": "Python",
                "version": "3.8+",
                "formatter": "black",
                "linter": "pylint",
                "type_checker": "mypy",
                "extensions": [".py", ".pyw", ".pyx", ".pyi"],
            },
            Language.JAVASCRIPT: {
                "name": "JavaScript",
                "version": "ES6+",
                "formatter": "prettier",
                "linter": "eslint",
                "type_checker": None,
                "extensions": [".js", ".jsx", ".mjs"],
            },
            Language.TYPESCRIPT: {
                "name": "TypeScript",
                "version": "4.0+",
                "formatter": "prettier",
                "linter": "eslint",
                "type_checker": "tsc",
                "extensions": [".ts", ".tsx"],
            },
            Language.GO: {
                "name": "Go",
                "version": "1.16+",
                "formatter": "gofmt",
                "linter": "golangci-lint",
                "type_checker": None,
                "extensions": [".go"],
            },
            Language.JAVA: {
                "name": "Java",
                "version": "11+",
                "formatter": "google-java-format",
                "linter": "checkstyle",
                "type_checker": None,
                "extensions": [".java"],
            },
            Language.RUST: {
                "name": "Rust",
                "version": "1.50+",
                "formatter": "rustfmt",
                "linter": "clippy",
                "type_checker": None,
                "extensions": [".rs"],
            },
        }

        return info_map.get(lang, {
            "name": "Unknown",
            "version": None,
            "formatter": None,
            "linter": None,
            "type_checker": None,
            "extensions": [],
        })

    @staticmethod
    def get_supported_languages() -> List[Language]:
        """Get list of supported languages"""
        return [
            Language.PYTHON,
            Language.JAVASCRIPT,
            Language.TYPESCRIPT,
            Language.GO,
            Language.JAVA,
            Language.RUST,
        ]
