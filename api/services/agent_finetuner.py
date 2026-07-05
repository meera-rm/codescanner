"""
Agent Fine-Tuner - Phase 6.1.2
Fine-tunes agents based on codebase-specific patterns and refactoring history
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time

from .codebase_learner import (
    CodebaseIntelligence,
    CodePatternType,
    get_codebase_intelligence
)
from .agent_registry import AgentDefinition


class AgentSpecialization(str, Enum):
    """Agent specialization types"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    DOCUMENTATION = "documentation"
    COMPLEXITY = "complexity"
    STYLE = "style"


@dataclass
class AgentProfile:
    """Agent learning profile"""
    agent_name: str
    specialization: AgentSpecialization
    language: str
    pattern_successes: Dict[str, float] = field(default_factory=dict)  # pattern_id -> success_rate
    recommendation_accuracy: float = 0.0
    learning_iterations: int = 0
    last_trained: float = field(default_factory=time.time)
    confidence_scores: Dict[str, float] = field(default_factory=dict)  # pattern_id -> confidence

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "agent_name": self.agent_name,
            "specialization": self.specialization.value,
            "language": self.language,
            "pattern_successes": self.pattern_successes,
            "recommendation_accuracy": self.recommendation_accuracy,
            "learning_iterations": self.learning_iterations,
            "last_trained": self.last_trained,
            "confidence_scores": self.confidence_scores,
        }


@dataclass
class PersonalizedRecommendation:
    """Personalized code recommendation from fine-tuned agent"""
    pattern_id: str
    original_code: str
    recommended_code: str
    improvement_score: float
    confidence: float
    reasoning: str
    similar_patterns_used: int
    estimated_benefit: str  # "high", "medium", "low"


class AgentFineTuner:
    """Fine-tunes agents on codebase patterns"""

    def __init__(self):
        self.intelligence = get_codebase_intelligence()
        self.agent_profiles: Dict[str, AgentProfile] = {}

    def create_agent_profile(
        self,
        agent_name: str,
        specialization: AgentSpecialization,
        language: str
    ) -> AgentProfile:
        """Create learning profile for an agent"""
        profile = AgentProfile(
            agent_name=agent_name,
            specialization=specialization,
            language=language
        )

        self.agent_profiles[agent_name] = profile
        return profile

    def train_agent(
        self,
        agent_name: str,
        language: str
    ) -> Dict[str, Any]:
        """Train agent on codebase patterns"""
        profile = self.agent_profiles.get(agent_name)
        if not profile:
            return {"status": "error", "message": "Agent profile not found"}

        # Get all patterns for language
        patterns = [
            p for p in self.intelligence.patterns.values()
            if p.language == language
        ]

        # Calculate success rates per pattern
        for pattern in patterns:
            success_rate = self.intelligence._calculate_success_rate(pattern.pattern_id)
            confidence = self._calculate_confidence(pattern, success_rate)

            profile.pattern_successes[pattern.pattern_id] = success_rate
            profile.confidence_scores[pattern.pattern_id] = confidence

        # Update accuracy metric
        if profile.pattern_successes:
            profile.recommendation_accuracy = sum(
                profile.pattern_successes.values()
            ) / len(profile.pattern_successes)

        profile.learning_iterations += 1
        profile.last_trained = time.time()

        return {
            "status": "success",
            "agent_name": agent_name,
            "patterns_trained": len(patterns),
            "accuracy": profile.recommendation_accuracy,
            "iterations": profile.learning_iterations
        }

    def get_personalized_recommendation(
        self,
        agent_name: str,
        pattern_id: str,
        original_code: str,
        language: str
    ) -> Optional[PersonalizedRecommendation]:
        """Get personalized recommendation from fine-tuned agent"""
        profile = self.agent_profiles.get(agent_name)
        if not profile:
            return None

        pattern = self.intelligence.patterns.get(pattern_id)
        if not pattern:
            return None

        # Get recommendations from history
        recommendations = self.intelligence.get_pattern_recommendations(pattern_id)
        if not recommendations:
            return None

        # Pick best recommendation
        best = recommendations[0]
        confidence = profile.confidence_scores.get(pattern_id, 0.5)

        # Calculate improvement score
        improvement = best["quality_improvement"] * confidence
        estimated_benefit = self._estimate_benefit(improvement)

        # Find similar patterns used for training
        similar_patterns = self.intelligence.search_similar_patterns(
            original_code, language, limit=3
        )

        return PersonalizedRecommendation(
            pattern_id=pattern_id,
            original_code=original_code,
            recommended_code=best["refactored_code"],
            improvement_score=improvement,
            confidence=confidence,
            reasoning=self._generate_reasoning(
                pattern, best, profile.specialization
            ),
            similar_patterns_used=len(similar_patterns),
            estimated_benefit=estimated_benefit
        )

    def adapt_agent_weights(
        self,
        agent_name: str,
        feedback_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Adapt agent weights based on feedback"""
        profile = self.agent_profiles.get(agent_name)
        if not profile:
            return {"status": "error", "message": "Agent profile not found"}

        pattern_id = feedback_data.get("pattern_id")
        was_helpful = feedback_data.get("was_helpful", False)
        user_rating = feedback_data.get("rating", 0.5)  # 0-1

        if not pattern_id or pattern_id not in profile.pattern_successes:
            return {"status": "error", "message": "Pattern not found"}

        # Update success rate with feedback
        current_success = profile.pattern_successes[pattern_id]
        feedback_weight = 0.3  # Give 30% weight to user feedback

        if was_helpful:
            new_success = current_success + (1 - current_success) * feedback_weight * user_rating
        else:
            new_success = current_success * (1 - feedback_weight * (1 - user_rating))

        profile.pattern_successes[pattern_id] = max(0, min(1, new_success))

        # Record in history
        self.intelligence.record_refactoring(
            pattern_id=pattern_id,
            original_code=feedback_data.get("original_code", ""),
            refactored_code=feedback_data.get("refactored_code", ""),
            quality_improvement=feedback_data.get("improvement", 0),
            complexity_change=feedback_data.get("complexity_change", 0),
            performance_impact=feedback_data.get("impact", "neutral")
        )

        return {
            "status": "success",
            "agent_name": agent_name,
            "pattern_id": pattern_id,
            "updated_success_rate": profile.pattern_successes[pattern_id],
            "feedback_applied": True
        }

    def get_agent_performance(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get agent performance metrics"""
        profile = self.agent_profiles.get(agent_name)
        if not profile:
            return None

        successful_patterns = sum(
            1 for sr in profile.pattern_successes.values() if sr > 0.7
        )
        avg_confidence = (
            sum(profile.confidence_scores.values()) / len(profile.confidence_scores)
            if profile.confidence_scores else 0
        )

        return {
            "agent_name": agent_name,
            "specialization": profile.specialization.value,
            "accuracy": profile.recommendation_accuracy,
            "successful_patterns": successful_patterns,
            "total_patterns": len(profile.pattern_successes),
            "avg_confidence": avg_confidence,
            "iterations": profile.learning_iterations,
            "last_trained": profile.last_trained
        }

    def _calculate_confidence(
        self,
        pattern: Any,
        success_rate: float
    ) -> float:
        """Calculate confidence score for pattern"""
        # More occurrences = more confidence
        occurrence_factor = min(pattern.occurrences / 10, 1.0)
        # Success rate + occurrence factor
        confidence = (success_rate * 0.7 + occurrence_factor * 0.3)
        return confidence

    def _estimate_benefit(self, improvement: float) -> str:
        """Estimate benefit level"""
        if improvement > 0.3:
            return "high"
        elif improvement > 0.1:
            return "medium"
        else:
            return "low"

    def _generate_reasoning(
        self,
        pattern: Any,
        recommendation: Dict[str, Any],
        specialization: AgentSpecialization
    ) -> str:
        """Generate reasoning for recommendation"""
        reasoning_map = {
            AgentSpecialization.SECURITY: "Improves code security by removing potential vulnerabilities",
            AgentSpecialization.PERFORMANCE: "Optimizes code for better performance and efficiency",
            AgentSpecialization.DOCUMENTATION: "Adds missing documentation and type hints",
            AgentSpecialization.COMPLEXITY: "Reduces cyclomatic complexity for better maintainability",
            AgentSpecialization.STYLE: "Aligns code with best practices and style guidelines"
        }

        base = reasoning_map.get(specialization, "Improves code quality")
        improvement_pct = int(recommendation["quality_improvement"] * 100)

        return f"{base}. Expected improvement: {improvement_pct}%"

    def compare_agents(
        self,
        language: str
    ) -> List[Dict[str, Any]]:
        """Compare performance of all agents for a language"""
        comparisons = []

        for agent_name, profile in self.agent_profiles.items():
            if profile.language == language:
                perf = self.get_agent_performance(agent_name)
                if perf:
                    comparisons.append(perf)

        return sorted(
            comparisons,
            key=lambda x: x["accuracy"],
            reverse=True
        )


# Global instance
_global_agent_finetuner = AgentFineTuner()


def get_agent_finetuner() -> AgentFineTuner:
    """Get global agent fine-tuner instance"""
    return _global_agent_finetuner
