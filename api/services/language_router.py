"""
Language Router - Phase 5.3
Unified interface for multi-language code analysis
"""

from typing import Dict, Optional, Any
from dataclasses import dataclass
import asyncio

from .language_detector import Language, LanguageDetector
from .language_formatters import LanguageFormatter, FormattingResult
from .language_validators import LanguageValidator, ValidationResult


@dataclass
class LanguageAnalysisResult:
    """Complete analysis result for code"""
    language: Language
    confidence: float
    formatting: Optional[FormattingResult]
    validation: Optional[ValidationResult]
    language_info: Dict[str, Any]


class LanguageRouter:
    """Routes code analysis to appropriate language handlers"""

    def __init__(self):
        self.detector = LanguageDetector()
        self.formatter = LanguageFormatter()
        self.validator = LanguageValidator()

    async def analyze(
        self,
        code: str,
        file_path: Optional[str] = None,
        format_code: bool = True,
        validate_code: bool = True
    ) -> LanguageAnalysisResult:
        """
        Analyze code in any supported language

        Returns comprehensive analysis including detection, formatting, validation
        """
        # Detect language
        language, confidence = LanguageDetector.detect(code, file_path)

        # Get language info
        language_info = LanguageDetector.get_language_info(language)

        # Format code if requested and language is supported
        formatting = None
        if format_code and language != Language.UNKNOWN:
            formatting = await LanguageFormatter.format(code, language)

        # Validate code if requested and language is supported
        validation = None
        if validate_code and language != Language.UNKNOWN:
            validation = await LanguageValidator.validate(code, language)

        return LanguageAnalysisResult(
            language=language,
            confidence=confidence,
            formatting=formatting,
            validation=validation,
            language_info=language_info
        )

    async def format_code(
        self,
        code: str,
        language: Optional[Language] = None,
        file_path: Optional[str] = None
    ) -> FormattingResult:
        """Format code (auto-detect language if not specified)"""
        if language is None:
            language, _ = LanguageDetector.detect(code, file_path)

        if language == Language.UNKNOWN:
            return FormattingResult(
                success=False,
                formatted_code=None,
                error="Unable to detect language",
                changes_made=0,
                lines_changed=0
            )

        return await LanguageFormatter.format(code, language)

    async def validate_code(
        self,
        code: str,
        language: Optional[Language] = None,
        file_path: Optional[str] = None
    ) -> ValidationResult:
        """Validate code (auto-detect language if not specified)"""
        if language is None:
            language, _ = LanguageDetector.detect(code, file_path)

        if language == Language.UNKNOWN:
            return ValidationResult(
                success=False,
                language=Language.UNKNOWN,
                syntax_valid=False,
                issues=[],
                error="Unable to detect language"
            )

        return await LanguageValidator.validate(code, language)

    async def analyze_files(
        self,
        files: Dict[str, str]
    ) -> Dict[str, LanguageAnalysisResult]:
        """
        Analyze multiple files

        Args:
            files: Dict of {file_path: code}

        Returns:
            Dict of {file_path: LanguageAnalysisResult}
        """
        tasks = {
            file_path: self.analyze(code, file_path)
            for file_path, code in files.items()
        }

        results = await asyncio.gather(*tasks.values())
        return {
            file_path: result
            for file_path, result in zip(tasks.keys(), results)
        }

    def get_supported_languages(self) -> list:
        """Get list of supported languages"""
        return LanguageDetector.get_supported_languages()

    def get_language_info(self, language: Language) -> Dict[str, Any]:
        """Get information about a language"""
        return LanguageDetector.get_language_info(language)


# Global router instance
_global_router = LanguageRouter()


def get_language_router() -> LanguageRouter:
    """Get global language router"""
    return _global_router
