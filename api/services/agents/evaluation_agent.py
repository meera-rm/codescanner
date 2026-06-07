"""Evaluation Agent: Scores and selects best refactoring suggestion."""

from dataclasses import dataclass
from typing import List, Optional
from .refactoring_agent import Suggestion


@dataclass
class ScoredSuggestion:
    """Suggestion with calculated score."""

    suggestion: Suggestion
    score: float
    breakdown: dict


class EvaluationAgent:
    """
    Evaluate and score refactoring suggestions.

    Scoring factors:
    - Complexity reduction: 30% weight
    - Risk of errors: 40% weight
    - Code clarity: 20% weight
    - Implementation time: 10% weight
    """

    # Scoring weights
    WEIGHTS = {
        "complexity_reduction": 0.30,
        "risk_level": 0.40,
        "clarity_improvement": 0.20,
        "implementation_time": 0.10,
    }

    def pick_best(self, suggestions: List[Suggestion]) -> Optional[Suggestion]:
        """
        Score all suggestions and return the best one.

        Returns highest scored suggestion, or None if no valid suggestions.
        """

        if not suggestions:
            return None

        # Score all suggestions
        scored = [self._score_suggestion(s) for s in suggestions]

        # Return suggestion with highest score
        best = max(scored, key=lambda x: x.score)
        return best.suggestion

    def pick_best_with_details(self, suggestions: List[Suggestion]) -> Optional[ScoredSuggestion]:
        """
        Score all suggestions and return the best with score breakdown.

        Useful for debugging and understanding why a suggestion was chosen.
        """

        if not suggestions:
            return None

        # Score all suggestions
        scored = [self._score_suggestion(s) for s in suggestions]

        # Return best with details
        best = max(scored, key=lambda x: x.score)
        return best

    def score_all(self, suggestions: List[Suggestion]) -> List[ScoredSuggestion]:
        """Score all suggestions without filtering."""
        return [self._score_suggestion(s) for s in suggestions]

    def _score_suggestion(self, suggestion: Suggestion) -> ScoredSuggestion:
        """Calculate composite score for a single suggestion."""

        breakdown = {}

        # 1. Complexity reduction (0-100)
        complexity_score = suggestion.complexity_reduction
        breakdown["complexity"] = (
            complexity_score * self.WEIGHTS["complexity_reduction"]
        )

        # 2. Risk level normalization
        risk_score = self._risk_to_score(suggestion.risk_level)
        breakdown["risk"] = risk_score * self.WEIGHTS["risk_level"]

        # 3. Clarity improvement normalization
        clarity_score = self._clarity_to_score(suggestion.clarity_improvement)
        breakdown["clarity"] = clarity_score * self.WEIGHTS["clarity_improvement"]

        # 4. Implementation time normalization
        time_score = self._time_to_score(suggestion.estimated_time)
        breakdown["time"] = time_score * self.WEIGHTS["implementation_time"]

        # Total weighted score
        total_score = sum(breakdown.values())

        return ScoredSuggestion(
            suggestion=suggestion,
            score=total_score,
            breakdown=breakdown
        )

    @staticmethod
    def _risk_to_score(risk: str) -> float:
        """
        Convert risk level to score (higher is better).

        low = 100 (safe)
        medium = 60 (acceptable)
        high = 20 (risky)
        """
        risk_map = {
            "low": 100,
            "medium": 60,
            "high": 20,
        }
        return risk_map.get(risk.lower(), 50)

    @staticmethod
    def _clarity_to_score(clarity: str) -> float:
        """
        Convert clarity level to score.

        excellent = 100
        good = 75
        ok = 50
        poor = 25
        """
        clarity_map = {
            "excellent": 100,
            "good": 75,
            "ok": 50,
            "poor": 25,
        }
        return clarity_map.get(clarity.lower(), 50)

    @staticmethod
    def _time_to_score(time_str: str) -> float:
        """
        Convert time estimate to score (prefer quick).

        quick = 100 (< 15 min)
        medium = 75 (15-30 min)
        slow = 50 (30-60 min)
        very slow = 20 (> 60 min)
        """
        time_str_lower = time_str.lower()

        if "quick" in time_str_lower:
            return 100
        elif "medium" in time_str_lower:
            return 75
        elif "very slow" in time_str_lower:
            return 20
        elif "slow" in time_str_lower:
            return 50
        else:
            return 50  # Default to medium
