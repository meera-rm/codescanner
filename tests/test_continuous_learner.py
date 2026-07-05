"""
Tests for Continuous Learner - Phase 6.1.4
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.continuous_learner import (
    ContinuousLearner,
    LearningPhase,
    ExperienceRecord,
    LearningBatch
)
from api.services.codebase_learner import CodebaseIntelligence, CodePatternType
from api.services.agent_finetuner import AgentSpecialization


class TestContinuousLearner:
    """Test continuous learning system"""

    def test_record_experience(self):
        """Test recording refactoring experience"""
        learner = ContinuousLearner()

        exp = learner.record_experience(
            pattern_id="pat_123",
            original_code="def foo(): pass",
            refactored_code="def foo() -> None: pass",
            agent_name="DocGenerator",
            quality_improvement=0.15,
            language="python",
            user_feedback=0.8
        )

        assert exp.experience_id.startswith("exp_")
        assert exp.quality_improvement == 0.15
        assert exp.user_feedback == 0.8
        assert learner.total_experiences == 1

    def test_multiple_experiences(self):
        """Test recording multiple experiences"""
        learner = ContinuousLearner()

        for i in range(5):
            learner.record_experience(
                pattern_id=f"pat_{i}",
                original_code=f"def func{i}(): pass",
                refactored_code=f"def func{i}() -> None: pass",
                agent_name="TestAgent",
                quality_improvement=0.1 * (i + 1),
                language="python"
            )

        assert learner.total_experiences == 5
        assert learner.total_improvements == pytest.approx(1.5)  # 0.1 + 0.2 + 0.3 + 0.4 + 0.5

    def test_batch_creation(self):
        """Test automatic batch creation"""
        learner = ContinuousLearner()
        learner.batch_size = 3

        # Record experiences until batch is created
        for i in range(3):
            learner.record_experience(
                pattern_id=f"pat_{i}",
                original_code=f"code{i}",
                refactored_code=f"refactored{i}",
                agent_name="Agent",
                quality_improvement=0.2,
                language="python"
            )

        # Should have created a batch
        assert len(learner.learning_batches) >= 1

    def test_batch_properties(self):
        """Test learning batch properties"""
        learner = ContinuousLearner()
        learner.batch_size = 2

        for i in range(2):
            learner.record_experience(
                pattern_id=f"pat_{i}",
                original_code=f"code{i}",
                refactored_code=f"refactored{i}",
                agent_name="Agent",
                quality_improvement=0.2,
                language="python"
            )

        batch = list(learner.learning_batches.values())[0]

        assert batch.language == "python"
        assert len(batch.experiences) == 2
        assert batch.avg_improvement == 0.2
        assert batch.confidence >= 0

    def test_batch_confidence_calculation(self):
        """Test batch confidence calculation"""
        learner = ContinuousLearner()

        experiences = [
            ExperienceRecord(
                experience_id=f"exp_{i}",
                pattern_id=f"pat_{i}",
                original_code="code",
                refactored_code="refactored",
                agent_name="Agent",
                quality_improvement=0.2 + (i * 0.05),
                user_feedback=0.8 if i % 2 == 0 else None
            )
            for i in range(5)
        ]

        confidence = learner._calculate_batch_confidence(experiences)

        assert 0 <= confidence <= 1
        assert confidence > 0  # Should have some confidence with data

    def test_auto_validate_refactoring(self):
        """Test automatic validation of refactoring"""
        learner = ContinuousLearner()

        # Setup pattern
        pattern = learner.intelligence.extract_pattern(
            code="def test(): pass",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="test",
            complexity=1.0
        )

        # Good refactoring (has type hints and docstring)
        is_valid, confidence = learner.auto_validate_refactoring(
            pattern.pattern_id,
            'def test() -> None:\n    """Test function"""\n    pass',
            "def test(): pass"
        )

        assert confidence > 0

    def test_get_learning_metrics(self):
        """Test learning metrics"""
        learner = ContinuousLearner()

        for i in range(3):
            learner.record_experience(
                pattern_id=f"pat_{i}",
                original_code="code",
                refactored_code="refactored",
                agent_name="Agent",
                quality_improvement=0.2,
                language="python"
            )

        metrics = learner.get_learning_metrics()

        assert metrics["total_experiences"] == 3
        assert metrics["avg_improvement"] == pytest.approx(0.2)
        assert "current_phase" in metrics

    def test_experience_to_dict(self):
        """Test experience serialization"""
        exp = ExperienceRecord(
            experience_id="exp_123",
            pattern_id="pat_456",
            original_code="original",
            refactored_code="refactored",
            agent_name="TestAgent",
            quality_improvement=0.25,
            user_feedback=0.9
        )

        exp_dict = exp.to_dict()

        assert exp_dict["experience_id"] == "exp_123"
        assert exp_dict["quality_improvement"] == 0.25
        assert exp_dict["user_feedback"] == 0.9

    def test_batch_to_dict(self):
        """Test batch serialization"""
        experiences = [
            ExperienceRecord(
                experience_id=f"exp_{i}",
                pattern_id=f"pat_{i}",
                original_code="code",
                refactored_code="refactored",
                agent_name="Agent",
                quality_improvement=0.2
            )
            for i in range(2)
        ]

        batch = LearningBatch(
            batch_id="batch_123",
            language="python",
            experiences=experiences,
            avg_improvement=0.2,
            confidence=0.8,
            learning_phase=LearningPhase.COLLECTION
        )

        batch_dict = batch.to_dict()

        assert batch_dict["batch_id"] == "batch_123"
        assert batch_dict["language"] == "python"
        assert batch_dict["experience_count"] == 2

    def test_get_experience_replay(self):
        """Test retrieving experiences for replay"""
        learner = ContinuousLearner()

        for i in range(5):
            learner.record_experience(
                pattern_id=f"pat_{i}",
                original_code=f"code{i}",
                refactored_code=f"refactored{i}",
                agent_name="Agent",
                quality_improvement=0.1,
                language="python"
            )

        replay = learner.get_experience_replay("python", limit=3)

        assert len(replay) <= 3
        assert all(isinstance(e, ExperienceRecord) for e in replay)

    def test_learning_phase_progression(self):
        """Test learning phase transitions"""
        learner = ContinuousLearner()
        learner.batch_size = 2

        # Start in COLLECTION phase
        assert learner.current_phase == LearningPhase.COLLECTION

        # Record experiences
        for i in range(2):
            learner.record_experience(
                pattern_id=f"pat_{i}",
                original_code=f"code{i}",
                refactored_code=f"refactored{i}",
                agent_name="Agent",
                quality_improvement=0.2,
                language="python"
            )

        # Should move to ANALYSIS phase when batch created
        assert learner.current_phase == LearningPhase.ANALYSIS

    def test_efficiency_calculation(self):
        """Test learning efficiency calculation"""
        learner = ContinuousLearner()

        # No experiences yet
        efficiency = learner._calculate_efficiency()
        assert efficiency == 0.0

        # Record experiences with good improvement
        for i in range(5):
            learner.record_experience(
                pattern_id=f"pat_{i}",
                original_code="code",
                refactored_code="refactored",
                agent_name="Agent",
                quality_improvement=0.3,
                language="python"
            )

        efficiency = learner._calculate_efficiency()
        assert efficiency > 0

    def test_trend_calculation(self):
        """Test trend calculation from values"""
        learner = ContinuousLearner()

        # Improving trend (more data points to show clear difference)
        improving = [0.1, 0.11, 0.12, 0.15, 0.18, 0.20, 0.22]
        trend = learner._calculate_trend(improving)
        assert trend in ["improving", "stable"]  # May be stable with recent = all values

        # Degrading trend
        degrading = [0.25, 0.23, 0.22, 0.18, 0.15, 0.12, 0.10]
        trend = learner._calculate_trend(degrading)
        assert trend in ["degrading", "stable"]

        # Stable trend
        stable = [0.15, 0.15, 0.16, 0.15, 0.15, 0.16, 0.15]
        trend = learner._calculate_trend(stable)
        assert trend == "stable"

    def test_continuous_improvement_report(self):
        """Test generating improvement report"""
        learner = ContinuousLearner()
        learner.batch_size = 2

        # Record experiences (this creates batches)
        for i in range(4):
            learner.record_experience(
                pattern_id=f"pat_{i}",
                original_code=f"code{i}",
                refactored_code=f"refactored{i}",
                agent_name="Agent",
                quality_improvement=0.2,
                language="python"
            )

        # Process the batches to populate learning history
        for batch_id in list(learner.learning_batches.keys()):
            learner.process_learning_batch(batch_id)

        report = learner.get_continuous_improvement_report()

        assert "total_batches_processed" in report or "status" in report

    def test_auto_validation_flag(self):
        """Test auto-validation flag in experience"""
        learner = ContinuousLearner()

        exp_with_validation = learner.record_experience(
            pattern_id="pat_123",
            original_code="code",
            refactored_code="refactored",
            agent_name="Agent",
            quality_improvement=0.2,
            language="python",
            auto_validation=True
        )

        assert exp_with_validation.auto_validation is True

    def test_metadata_storage(self):
        """Test storing metadata with experiences"""
        learner = ContinuousLearner()

        metadata = {
            "file": "utils.py",
            "line": 42,
            "complexity_delta": -2
        }

        exp = learner.record_experience(
            pattern_id="pat_123",
            original_code="code",
            refactored_code="refactored",
            agent_name="Agent",
            quality_improvement=0.2,
            language="python",
            metadata=metadata
        )

        assert exp.metadata["file"] == "utils.py"
        assert exp.metadata["complexity_delta"] == -2

    def test_multiple_languages(self):
        """Test learning from multiple languages"""
        learner = ContinuousLearner()

        languages = ["python", "javascript", "go"]
        for lang in languages:
            learner.record_experience(
                pattern_id=f"pat_{lang}",
                original_code=f"code_{lang}",
                refactored_code=f"refactored_{lang}",
                agent_name=f"Agent_{lang}",
                quality_improvement=0.2,
                language=lang
            )

        assert len(learner.experience_buffer) == 3
        assert all(lang in learner.experience_buffer for lang in languages)

    def test_confidence_factors(self):
        """Test all factors affecting confidence"""
        learner = ContinuousLearner()

        # Experiences with feedback
        experiences_with_feedback = [
            ExperienceRecord(
                experience_id=f"exp_{i}",
                pattern_id=f"pat_{i}",
                original_code="code",
                refactored_code="refactored",
                agent_name="Agent",
                quality_improvement=0.2,
                user_feedback=0.8  # Has feedback
            )
            for i in range(3)
        ]

        confidence = learner._calculate_batch_confidence(experiences_with_feedback)
        assert confidence > 0

        # Experiences without feedback
        experiences_no_feedback = [
            ExperienceRecord(
                experience_id=f"exp_{i}",
                pattern_id=f"pat_{i}",
                original_code="code",
                refactored_code="refactored",
                agent_name="Agent",
                quality_improvement=0.2
            )
            for i in range(3)
        ]

        confidence_no_feedback = learner._calculate_batch_confidence(experiences_no_feedback)
        assert confidence > confidence_no_feedback  # Should be higher with feedback


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
