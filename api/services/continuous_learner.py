"""
Continuous Learner - Phase 6.1.4
Automatic learning loop from refactoring feedback and outcomes
"""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import time
from collections import deque
from statistics import mean

from .codebase_learner import (
    CodebaseIntelligence,
    get_codebase_intelligence
)
from .agent_finetuner import (
    AgentFineTuner,
    AgentSpecialization,
    get_agent_finetuner
)
from .predictive_analyzer import (
    PredictiveAnalyzer,
    get_predictive_analyzer
)


class LearningPhase(str, Enum):
    """Phases of learning"""
    COLLECTION = "collection"  # Gathering feedback
    ANALYSIS = "analysis"      # Analyzing patterns
    OPTIMIZATION = "optimization"  # Updating models
    VALIDATION = "validation"  # Testing improvements


@dataclass
class ExperienceRecord:
    """Single learning experience"""
    experience_id: str
    pattern_id: str
    original_code: str
    refactored_code: str
    agent_name: str
    quality_improvement: float
    user_feedback: Optional[float] = None  # 0-1, from user
    auto_validation: bool = False
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "experience_id": self.experience_id,
            "pattern_id": self.pattern_id,
            "agent_name": self.agent_name,
            "quality_improvement": self.quality_improvement,
            "user_feedback": self.user_feedback,
            "auto_validation": self.auto_validation,
            "timestamp": self.timestamp,
        }


@dataclass
class LearningBatch:
    """Batch of experiences for learning"""
    batch_id: str
    language: str
    experiences: List[ExperienceRecord]
    avg_improvement: float
    confidence: float
    learning_phase: LearningPhase
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "batch_id": self.batch_id,
            "language": self.language,
            "experience_count": len(self.experiences),
            "avg_improvement": self.avg_improvement,
            "confidence": self.confidence,
            "phase": self.learning_phase.value,
            "created_at": self.created_at,
        }


class ContinuousLearner:
    """Automatically learns and improves from refactoring experiences"""

    def __init__(self):
        self.intelligence = get_codebase_intelligence()
        self.finetuner = get_agent_finetuner()
        self.analyzer = get_predictive_analyzer()

        # Experience management
        self.experience_buffer: Dict[str, deque] = {}  # language -> experiences
        self.learning_batches: Dict[str, LearningBatch] = {}
        self.learning_history: List[Dict[str, Any]] = []

        # Configuration
        self.batch_size = 10  # Experiences before training
        self.confidence_threshold = 0.7
        self.improvement_threshold = 0.1

        # State
        self.current_phase = LearningPhase.COLLECTION
        self.total_experiences = 0
        self.total_improvements = 0.0

    def record_experience(
        self,
        pattern_id: str,
        original_code: str,
        refactored_code: str,
        agent_name: str,
        quality_improvement: float,
        language: str,
        user_feedback: Optional[float] = None,
        auto_validation: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> ExperienceRecord:
        """Record a refactoring experience for learning"""
        import secrets

        experience_id = f"exp_{secrets.token_hex(8)}"
        experience = ExperienceRecord(
            experience_id=experience_id,
            pattern_id=pattern_id,
            original_code=original_code,
            refactored_code=refactored_code,
            agent_name=agent_name,
            quality_improvement=quality_improvement,
            user_feedback=user_feedback,
            auto_validation=auto_validation,
            metadata=metadata or {}
        )

        # Add to buffer
        if language not in self.experience_buffer:
            self.experience_buffer[language] = deque(maxlen=100)

        self.experience_buffer[language].append(experience)
        self.total_experiences += 1
        self.total_improvements += quality_improvement

        # Check if we should create a batch
        if len(self.experience_buffer[language]) >= self.batch_size:
            self._create_learning_batch(language)

        return experience

    def _create_learning_batch(self, language: str) -> LearningBatch:
        """Create a learning batch from buffered experiences"""
        import secrets

        experiences = list(self.experience_buffer[language])
        if not experiences:
            return None

        avg_improvement = mean(e.quality_improvement for e in experiences)
        confidence = self._calculate_batch_confidence(experiences)

        batch_id = f"batch_{secrets.token_hex(8)}"
        batch = LearningBatch(
            batch_id=batch_id,
            language=language,
            experiences=experiences,
            avg_improvement=avg_improvement,
            confidence=confidence,
            learning_phase=LearningPhase.COLLECTION
        )

        self.learning_batches[batch_id] = batch
        self.current_phase = LearningPhase.ANALYSIS

        return batch

    def process_learning_batch(self, batch_id: str) -> Dict[str, Any]:
        """Process a batch and improve models"""
        batch = self.learning_batches.get(batch_id)
        if not batch:
            return {"status": "error", "message": "Batch not found"}

        # Validate batch
        if batch.confidence < self.confidence_threshold:
            return {
                "status": "error",
                "message": f"Batch confidence {batch.confidence} below threshold"
            }

        # Analyze experiences
        analysis = self._analyze_batch(batch)

        # Train agents
        training_results = self._train_on_batch(batch)

        # Validate improvements
        validation = self._validate_improvements(batch, training_results)

        # Update phase
        batch.learning_phase = LearningPhase.OPTIMIZATION

        # Record in history
        self.learning_history.append({
            "batch_id": batch_id,
            "timestamp": time.time(),
            "analysis": analysis,
            "training": training_results,
            "validation": validation
        })

        return {
            "status": "success",
            "batch_id": batch_id,
            "analysis": analysis,
            "training_results": training_results,
            "validation": validation
        }

    def _analyze_batch(self, batch: LearningBatch) -> Dict[str, Any]:
        """Analyze experiences in batch"""
        improvements_by_agent = {}
        improvements_by_pattern = {}

        for exp in batch.experiences:
            # By agent
            if exp.agent_name not in improvements_by_agent:
                improvements_by_agent[exp.agent_name] = []
            improvements_by_agent[exp.agent_name].append(exp.quality_improvement)

            # By pattern
            if exp.pattern_id not in improvements_by_pattern:
                improvements_by_pattern[exp.pattern_id] = []
            improvements_by_pattern[exp.pattern_id].append(exp.quality_improvement)

        return {
            "total_experiences": len(batch.experiences),
            "avg_improvement": batch.avg_improvement,
            "agents_trained": len(improvements_by_agent),
            "patterns_improved": len(improvements_by_pattern),
            "best_agent": max(
                improvements_by_agent.keys(),
                key=lambda a: mean(improvements_by_agent[a])
            ) if improvements_by_agent else None,
            "worst_performing_pattern": min(
                improvements_by_pattern.keys(),
                key=lambda p: mean(improvements_by_pattern[p])
            ) if improvements_by_pattern else None
        }

    def _train_on_batch(self, batch: LearningBatch) -> Dict[str, Any]:
        """Train agents on batch experiences"""
        results = {}

        # Group by agent
        by_agent = {}
        for exp in batch.experiences:
            if exp.agent_name not in by_agent:
                by_agent[exp.agent_name] = []
            by_agent[exp.agent_name].append(exp)

        # Train each agent
        for agent_name, experiences in by_agent.items():
            agent_profile = self.finetuner.agent_profiles.get(agent_name)
            if not agent_profile:
                continue

            # Record all experiences as feedback
            for exp in experiences:
                feedback_data = {
                    "pattern_id": exp.pattern_id,
                    "original_code": exp.original_code,
                    "refactored_code": exp.refactored_code,
                    "was_helpful": exp.quality_improvement > 0.1,
                    "rating": exp.user_feedback or 0.5,
                    "improvement": exp.quality_improvement,
                    "complexity_change": 0,
                    "impact": "improved" if exp.quality_improvement > 0 else "degraded"
                }

                self.finetuner.adapt_agent_weights(agent_name, feedback_data)

            # Retrain agent
            train_result = self.finetuner.train_agent(agent_name, batch.language)
            results[agent_name] = train_result

        return results

    def _validate_improvements(
        self,
        batch: LearningBatch,
        training_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate that improvements actually occurred"""
        agents_improved = 0
        agents_degraded = 0

        for agent_name, train_result in training_results.items():
            if train_result.get("status") == "success":
                accuracy = train_result.get("accuracy", 0)
                if accuracy > 0.6:
                    agents_improved += 1
                else:
                    agents_degraded += 1

        return {
            "agents_improved": agents_improved,
            "agents_degraded": agents_degraded,
            "success_rate": agents_improved / max(1, agents_improved + agents_degraded)
        }

    def auto_validate_refactoring(
        self,
        pattern_id: str,
        refactored_code: str,
        original_code: str
    ) -> Tuple[bool, float]:
        """Auto-validate refactoring without user input"""
        # Use predictive analyzer to assess quality
        analyzer = self.analyzer

        # Calculate predicted improvement
        pattern = self.intelligence.patterns.get(pattern_id)
        if not pattern:
            return False, 0.0

        # Simple validation: check if refactored code is similar length or longer
        # (maintains functionality) and follows better patterns
        is_longer = len(refactored_code) >= len(original_code) * 0.9
        has_type_hints = ":" in refactored_code and "->" in refactored_code
        has_docstring = '"""' in refactored_code or "'''" in refactored_code

        confidence = 0.0
        if is_longer:
            confidence += 0.3
        if has_type_hints:
            confidence += 0.3
        if has_docstring:
            confidence += 0.2

        is_valid = confidence > 0.4
        return is_valid, confidence

    def get_learning_metrics(self) -> Dict[str, Any]:
        """Get overall learning metrics"""
        avg_improvement = (
            self.total_improvements / self.total_experiences
            if self.total_experiences > 0
            else 0
        )

        agents_data = {}
        for agent_name, profile in self.finetuner.agent_profiles.items():
            agents_data[agent_name] = {
                "accuracy": profile.recommendation_accuracy,
                "iterations": profile.learning_iterations,
                "patterns_trained": len(profile.pattern_successes)
            }

        return {
            "total_experiences": self.total_experiences,
            "avg_improvement": avg_improvement,
            "batches_processed": len(self.learning_history),
            "current_phase": self.current_phase.value,
            "agents_metrics": agents_data,
            "learning_efficiency": self._calculate_efficiency()
        }

    def get_experience_replay(self, language: str, limit: int = 10) -> List[ExperienceRecord]:
        """Get recent experiences for replay learning"""
        buffer = self.experience_buffer.get(language)
        if not buffer:
            return []

        return list(buffer)[-limit:]

    def replay_experiences(self, language: str) -> Dict[str, Any]:
        """Replay past experiences to reinforce learning"""
        experiences = self.get_experience_replay(language, limit=20)
        if not experiences:
            return {"status": "no_experiences"}

        # Re-train on past experiences
        agents_trained = set()
        for exp in experiences:
            agents_trained.add(exp.agent_name)

        results = {}
        for agent_name in agents_trained:
            profile = self.finetuner.agent_profiles.get(agent_name)
            if profile:
                old_accuracy = profile.recommendation_accuracy
                self.finetuner.train_agent(agent_name, language)
                new_accuracy = profile.recommendation_accuracy

                results[agent_name] = {
                    "old_accuracy": old_accuracy,
                    "new_accuracy": new_accuracy,
                    "improvement": new_accuracy - old_accuracy
                }

        return {
            "status": "success",
            "experiences_replayed": len(experiences),
            "agents_trained": len(results),
            "results": results
        }

    def get_continuous_improvement_report(self) -> Dict[str, Any]:
        """Generate continuous improvement report"""
        if not self.learning_history:
            return {
                "status": "no_learning_history",
                "message": "No learning batches processed yet"
            }

        # Analyze learning history
        total_batches = len(self.learning_history)
        successful_batches = sum(
            1 for record in self.learning_history
            if record.get("training") and len(record["training"]) > 0
        )

        # Calculate improvement trajectory
        improvements = []
        for record in self.learning_history:
            analysis = record.get("analysis", {})
            improvements.append(analysis.get("avg_improvement", 0))

        avg_batch_improvement = mean(improvements) if improvements else 0

        return {
            "total_batches_processed": total_batches,
            "successful_batches": successful_batches,
            "success_rate": successful_batches / total_batches if total_batches > 0 else 0,
            "avg_improvement_per_batch": avg_batch_improvement,
            "improvement_trend": self._calculate_trend(improvements),
            "last_batch_time": self.learning_history[-1].get("timestamp")
        }

    def _calculate_batch_confidence(self, experiences: List[ExperienceRecord]) -> float:
        """Calculate confidence in a batch"""
        if not experiences:
            return 0.0

        # More experiences = higher confidence
        size_factor = min(len(experiences) / self.batch_size, 1.0)

        # More consistent improvements = higher confidence
        improvements = [e.quality_improvement for e in experiences]
        avg = mean(improvements)

        # Calculate variance
        if len(improvements) > 1:
            variance = sum((x - avg) ** 2 for x in improvements) / len(improvements)
            consistency = 1.0 / (1.0 + variance)
        else:
            consistency = 0.5

        # Feedback factor
        has_feedback = sum(1 for e in experiences if e.user_feedback is not None)
        feedback_factor = min(has_feedback / len(experiences), 1.0)

        confidence = (size_factor * 0.4 + consistency * 0.4 + feedback_factor * 0.2)
        return confidence

    def _calculate_efficiency(self) -> float:
        """Calculate learning efficiency"""
        if self.total_experiences == 0:
            return 0.0

        # Efficiency = avg improvement / number of experiences
        # More improvement with fewer experiences = better efficiency
        efficiency = (self.total_improvements / self.total_experiences) * 100
        return min(100, efficiency)

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction"""
        if len(values) < 2:
            return "insufficient_data"

        recent = values[-5:] if len(values) >= 5 else values
        older = values[:-5] if len(values) >= 5 else values

        recent_avg = mean(recent)
        older_avg = mean(older) if older else recent_avg

        # Use 5% threshold for trend detection
        if recent_avg > older_avg * 1.05:
            return "improving"
        elif recent_avg < older_avg * 0.95:
            return "degrading"
        else:
            return "stable"


# Global instance
_global_continuous_learner = ContinuousLearner()


def get_continuous_learner() -> ContinuousLearner:
    """Get global continuous learner instance"""
    return _global_continuous_learner
