"""
Codebase Learner - Phase 6.1.1
Extracts, indexes, and learns from codebase patterns
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import time
import json


class CodePatternType(str, Enum):
    """Types of code patterns"""
    FUNCTION = "function"
    CLASS = "class"
    MODULE = "module"
    ERROR_PATTERN = "error_pattern"
    REFACTORING = "refactoring"


@dataclass
class CodePattern:
    """Extracted code pattern"""
    pattern_id: str
    pattern_type: CodePatternType
    language: str
    name: str
    fingerprint: str  # Hash of pattern content
    complexity: float
    lines_of_code: int
    occurrences: int = 1
    first_seen: float = field(default_factory=time.time)
    last_seen: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "pattern_id": self.pattern_id,
            "pattern_type": self.pattern_type.value,
            "language": self.language,
            "name": self.name,
            "fingerprint": self.fingerprint,
            "complexity": self.complexity,
            "lines_of_code": self.lines_of_code,
            "occurrences": self.occurrences,
            "first_seen": self.first_seen,
            "last_seen": self.last_seen,
            "metadata": self.metadata,
        }


@dataclass
class RefactoringHistory:
    """Track refactoring outcomes"""
    history_id: str
    pattern_id: str
    original_code: str
    refactored_code: str
    quality_improvement: float  # -1.0 to 1.0
    complexity_change: float  # Change in complexity
    performance_impact: str  # "improved", "degraded", "neutral"
    timestamp: float = field(default_factory=time.time)
    feedback_score: Optional[float] = None  # User feedback 0-1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "history_id": self.history_id,
            "pattern_id": self.pattern_id,
            "original_code": self.original_code,
            "refactored_code": self.refactored_code,
            "quality_improvement": self.quality_improvement,
            "complexity_change": self.complexity_change,
            "performance_impact": self.performance_impact,
            "timestamp": self.timestamp,
            "feedback_score": self.feedback_score,
        }


@dataclass
class SemanticIndex:
    """Semantic search index entry"""
    index_id: str
    pattern_id: str
    tokens: List[str]  # Tokenized code
    embeddings: List[float] = field(default_factory=list)  # Vector embeddings
    keywords: List[str] = field(default_factory=list)  # Extracted keywords
    similar_patterns: List[str] = field(default_factory=list)  # Similar pattern IDs


class CodebaseIntelligence:
    """Learn and index codebase patterns"""

    def __init__(self):
        self.patterns: Dict[str, CodePattern] = {}
        self.refactoring_history: Dict[str, RefactoringHistory] = {}
        self.semantic_index: Dict[str, SemanticIndex] = {}
        self.language_stats: Dict[str, Dict[str, Any]] = {}

    def extract_pattern(
        self,
        code: str,
        pattern_type: CodePatternType,
        language: str,
        name: str,
        complexity: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> CodePattern:
        """Extract and store a code pattern"""
        import secrets

        # Generate fingerprint (content hash)
        fingerprint = hashlib.sha256(code.encode()).hexdigest()[:16]

        # Check if pattern already exists
        for pattern in self.patterns.values():
            if pattern.fingerprint == fingerprint and pattern.language == language:
                pattern.occurrences += 1
                pattern.last_seen = time.time()
                return pattern

        # Create new pattern
        pattern_id = f"pat_{secrets.token_hex(8)}"
        pattern = CodePattern(
            pattern_id=pattern_id,
            pattern_type=pattern_type,
            language=language,
            name=name,
            fingerprint=fingerprint,
            complexity=complexity,
            lines_of_code=len(code.split('\n')),
            metadata=metadata or {}
        )

        self.patterns[pattern_id] = pattern
        self._update_language_stats(language, pattern)
        self._index_pattern(pattern, code)

        return pattern

    def _index_pattern(self, pattern: CodePattern, code: str) -> None:
        """Create semantic index for pattern"""
        import secrets

        # Simple tokenization
        tokens = self._tokenize_code(code)
        keywords = self._extract_keywords(code, pattern.language)

        index = SemanticIndex(
            index_id=f"idx_{secrets.token_hex(8)}",
            pattern_id=pattern.pattern_id,
            tokens=tokens,
            keywords=keywords
        )

        self.semantic_index[pattern.pattern_id] = index

    def record_refactoring(
        self,
        pattern_id: str,
        original_code: str,
        refactored_code: str,
        quality_improvement: float,
        complexity_change: float,
        performance_impact: str
    ) -> RefactoringHistory:
        """Record refactoring outcome"""
        import secrets

        history_id = f"hist_{secrets.token_hex(8)}"
        history = RefactoringHistory(
            history_id=history_id,
            pattern_id=pattern_id,
            original_code=original_code,
            refactored_code=refactored_code,
            quality_improvement=quality_improvement,
            complexity_change=complexity_change,
            performance_impact=performance_impact
        )

        self.refactoring_history[history_id] = history
        return history

    def get_pattern_recommendations(self, pattern_id: str) -> List[Dict[str, Any]]:
        """Get refactoring recommendations based on history"""
        pattern = self.patterns.get(pattern_id)
        if not pattern:
            return []

        # Find successful refactorings of similar patterns
        recommendations = []
        for history in self.refactoring_history.values():
            if history.pattern_id == pattern_id and history.quality_improvement > 0.1:
                recommendations.append({
                    "refactored_code": history.refactored_code,
                    "quality_improvement": history.quality_improvement,
                    "complexity_change": history.complexity_change,
                    "performance_impact": history.performance_impact,
                    "feedback_score": history.feedback_score,
                    "success_rate": self._calculate_success_rate(pattern_id)
                })

        return sorted(recommendations, key=lambda x: x["quality_improvement"], reverse=True)

    def search_similar_patterns(
        self,
        code: str,
        language: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Find similar patterns in codebase"""
        tokens = self._tokenize_code(code)
        keywords = self._extract_keywords(code, language)

        similarities = []
        for pattern_id, index in self.semantic_index.items():
            pattern = self.patterns[pattern_id]
            if pattern.language != language:
                continue

            # Simple similarity: shared tokens and keywords
            shared_tokens = len(set(tokens) & set(index.tokens))
            shared_keywords = len(set(keywords) & set(index.keywords))
            similarity = (shared_tokens + shared_keywords * 2) / (len(tokens) + len(keywords) + 1)

            if similarity > 0.2:
                similarities.append({
                    "pattern_id": pattern_id,
                    "name": pattern.name,
                    "similarity": similarity,
                    "complexity": pattern.complexity,
                    "occurrences": pattern.occurrences
                })

        return sorted(similarities, key=lambda x: x["similarity"], reverse=True)[:limit]

    def get_codebase_insights(self, language: str) -> Dict[str, Any]:
        """Get insights for a language in codebase"""
        stats = self.language_stats.get(language, {})

        return {
            "language": language,
            "total_patterns": stats.get("total_patterns", 0),
            "avg_complexity": stats.get("avg_complexity", 0),
            "refactoring_history_count": len([
                h for h in self.refactoring_history.values()
                if self.patterns.get(h.pattern_id, {}).language == language
            ]),
            "improvement_rate": self._calculate_improvement_rate(language),
            "common_issues": self._get_common_issues(language)
        }

    def _tokenize_code(self, code: str) -> List[str]:
        """Simple code tokenization"""
        import re
        # Split on whitespace and common punctuation
        tokens = re.findall(r'\b\w+\b', code.lower())
        return tokens

    def _extract_keywords(self, code: str, language: str) -> List[str]:
        """Extract meaningful keywords from code"""
        keywords_by_lang = {
            "python": ["def", "class", "import", "return", "if", "for", "while"],
            "javascript": ["function", "const", "let", "return", "if", "for", "async"],
            "typescript": ["function", "const", "let", "return", "if", "for", "async", "type"],
            "go": ["func", "type", "struct", "return", "if", "for"],
            "java": ["public", "class", "void", "return", "if", "for"],
            "rust": ["fn", "struct", "impl", "return", "if", "for"]
        }

        keywords = keywords_by_lang.get(language, [])
        found = [k for k in keywords if k in code.lower()]
        return found

    def _update_language_stats(self, language: str, pattern: CodePattern) -> None:
        """Update language statistics"""
        if language not in self.language_stats:
            self.language_stats[language] = {
                "total_patterns": 0,
                "total_complexity": 0,
                "avg_complexity": 0
            }

        stats = self.language_stats[language]
        stats["total_patterns"] += 1
        stats["total_complexity"] += pattern.complexity
        stats["avg_complexity"] = stats["total_complexity"] / stats["total_patterns"]

    def _calculate_success_rate(self, pattern_id: str) -> float:
        """Calculate success rate of refactorings for a pattern"""
        histories = [h for h in self.refactoring_history.values() if h.pattern_id == pattern_id]
        if not histories:
            return 0.0

        successful = len([h for h in histories if h.quality_improvement > 0.1])
        return successful / len(histories)

    def _calculate_improvement_rate(self, language: str) -> float:
        """Calculate overall improvement rate for language"""
        histories = [
            h for h in self.refactoring_history.values()
            if self.patterns.get(h.pattern_id, {}).language == language
        ]
        if not histories:
            return 0.0

        avg_improvement = sum(h.quality_improvement for h in histories) / len(histories)
        return avg_improvement

    def _get_common_issues(self, language: str) -> List[str]:
        """Get most common issues in language"""
        issues = {}
        for pattern in self.patterns.values():
            if pattern.language == language and pattern.complexity > 10:
                issue = f"High complexity ({pattern.complexity:.1f})"
                issues[issue] = issues.get(issue, 0) + 1

        return sorted(issues.keys(), key=lambda x: issues[x], reverse=True)[:5]


# Global instance
_global_codebase_intelligence = CodebaseIntelligence()


def get_codebase_intelligence() -> CodebaseIntelligence:
    """Get global codebase intelligence instance"""
    return _global_codebase_intelligence
