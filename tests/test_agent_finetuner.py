"""
Tests for Agent Fine-Tuner - Phase 6.1.2
"""

import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from api.services.agent_finetuner import (
    AgentFineTuner,
    AgentSpecialization,
    AgentProfile
)
from api.services.codebase_learner import (
    CodebaseIntelligence,
    CodePatternType
)


class TestAgentFineTuner:
    """Test agent fine-tuning system"""

    def test_create_agent_profile(self):
        """Test creating agent profile"""
        finetuner = AgentFineTuner()

        profile = finetuner.create_agent_profile(
            agent_name="SecurityAuditor",
            specialization=AgentSpecialization.SECURITY,
            language="python"
        )

        assert profile.agent_name == "SecurityAuditor"
        assert profile.specialization == AgentSpecialization.SECURITY
        assert profile.recommendation_accuracy == 0.0

    def test_train_agent_on_patterns(self):
        """Test training agent on codebase patterns"""
        finetuner = AgentFineTuner()

        # Create profile
        finetuner.create_agent_profile(
            agent_name="PerfOptimizer",
            specialization=AgentSpecialization.PERFORMANCE,
            language="python"
        )

        # Add patterns to intelligence
        pattern = finetuner.intelligence.extract_pattern(
            code="def process(): pass",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="process",
            complexity=2.0
        )

        # Record successful refactoring
        finetuner.intelligence.record_refactoring(
            pattern_id=pattern.pattern_id,
            original_code="def process(): pass",
            refactored_code="def process() -> None: pass",
            quality_improvement=0.2,
            complexity_change=0,
            performance_impact="improved"
        )

        # Train agent
        result = finetuner.train_agent("PerfOptimizer", "python")

        assert result["status"] == "success"
        assert result["patterns_trained"] >= 1
        assert result["accuracy"] > 0

    def test_personalized_recommendation(self):
        """Test getting personalized recommendation"""
        finetuner = AgentFineTuner()

        # Setup
        finetuner.create_agent_profile(
            agent_name="SecurityAuditor",
            specialization=AgentSpecialization.SECURITY,
            language="python"
        )

        code = "def check_user(username): return True"
        pattern = finetuner.intelligence.extract_pattern(
            code=code,
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="check_user",
            complexity=1.0
        )

        # Record successful refactoring
        finetuner.intelligence.record_refactoring(
            pattern_id=pattern.pattern_id,
            original_code=code,
            refactored_code="def check_user(username: str) -> bool: return len(username) > 0",
            quality_improvement=0.25,
            complexity_change=0,
            performance_impact="improved"
        )

        # Train first
        finetuner.train_agent("SecurityAuditor", "python")

        # Get recommendation
        recommendation = finetuner.get_personalized_recommendation(
            agent_name="SecurityAuditor",
            pattern_id=pattern.pattern_id,
            original_code=code,
            language="python"
        )

        assert recommendation is not None
        assert recommendation.improvement_score >= 0
        assert recommendation.confidence > 0

    def test_adapt_agent_weights(self):
        """Test adapting agent weights with feedback"""
        finetuner = AgentFineTuner()

        finetuner.create_agent_profile(
            agent_name="DocGenerator",
            specialization=AgentSpecialization.DOCUMENTATION,
            language="python"
        )

        pattern = finetuner.intelligence.extract_pattern(
            code="def foo(): pass",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="foo",
            complexity=1.0
        )

        # Train first
        finetuner.intelligence.record_refactoring(
            pattern_id=pattern.pattern_id,
            original_code="def foo(): pass",
            refactored_code='def foo():\n    """Does something"""\n    pass',
            quality_improvement=0.1,
            complexity_change=0,
            performance_impact="neutral"
        )

        finetuner.train_agent("DocGenerator", "python")

        # Get initial success rate
        initial_rate = finetuner.agent_profiles["DocGenerator"].pattern_successes[pattern.pattern_id]

        # Adapt with positive feedback
        result = finetuner.adapt_agent_weights(
            agent_name="DocGenerator",
            feedback_data={
                "pattern_id": pattern.pattern_id,
                "original_code": "def foo(): pass",
                "refactored_code": 'def foo():\n    """Does something"""\n    pass',
                "was_helpful": True,
                "rating": 0.8,
                "improvement": 0.15,
                "complexity_change": 0,
                "impact": "improved"
            }
        )

        assert result["status"] == "success"
        updated_rate = finetuner.agent_profiles["DocGenerator"].pattern_successes[pattern.pattern_id]
        assert updated_rate > initial_rate

    def test_get_agent_performance(self):
        """Test getting agent performance metrics"""
        finetuner = AgentFineTuner()

        finetuner.create_agent_profile(
            agent_name="ComplexityReducer",
            specialization=AgentSpecialization.COMPLEXITY,
            language="python"
        )

        # Add and train on patterns
        pattern = finetuner.intelligence.extract_pattern(
            code="def complex(): pass",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="complex",
            complexity=8.0
        )

        finetuner.intelligence.record_refactoring(
            pattern_id=pattern.pattern_id,
            original_code="def complex(): pass",
            refactored_code="def complex() -> None: pass",
            quality_improvement=0.3,
            complexity_change=-2,
            performance_impact="improved"
        )

        finetuner.train_agent("ComplexityReducer", "python")

        performance = finetuner.get_agent_performance("ComplexityReducer")

        assert performance is not None
        assert performance["agent_name"] == "ComplexityReducer"
        assert performance["accuracy"] >= 0
        assert performance["iterations"] == 1

    def test_agent_profile_to_dict(self):
        """Test agent profile serialization"""
        profile = AgentProfile(
            agent_name="TestAgent",
            specialization=AgentSpecialization.SECURITY,
            language="javascript",
            recommendation_accuracy=0.85,
            learning_iterations=5
        )

        profile_dict = profile.to_dict()

        assert profile_dict["agent_name"] == "TestAgent"
        assert profile_dict["specialization"] == "security"
        assert profile_dict["recommendation_accuracy"] == 0.85

    def test_compare_agents(self):
        """Test comparing agents performance"""
        finetuner = AgentFineTuner()

        # Create multiple agents
        finetuner.create_agent_profile(
            agent_name="Agent1",
            specialization=AgentSpecialization.SECURITY,
            language="python"
        )

        finetuner.create_agent_profile(
            agent_name="Agent2",
            specialization=AgentSpecialization.PERFORMANCE,
            language="python"
        )

        # Add patterns
        p1 = finetuner.intelligence.extract_pattern(
            code="code1",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="test1",
            complexity=1.0
        )

        finetuner.intelligence.record_refactoring(
            pattern_id=p1.pattern_id,
            original_code="code1",
            refactored_code="refactored1",
            quality_improvement=0.3,
            complexity_change=0,
            performance_impact="improved"
        )

        # Train both
        finetuner.train_agent("Agent1", "python")
        finetuner.train_agent("Agent2", "python")

        # Compare
        comparison = finetuner.compare_agents("python")

        assert len(comparison) == 2
        assert comparison[0]["accuracy"] >= comparison[1]["accuracy"]

    def test_confidence_calculation(self):
        """Test confidence score calculation"""
        finetuner = AgentFineTuner()

        pattern = finetuner.intelligence.extract_pattern(
            code="def test(): pass",
            pattern_type=CodePatternType.FUNCTION,
            language="python",
            name="test",
            complexity=1.0
        )

        # Record multiple successful refactorings
        for i in range(5):
            finetuner.intelligence.record_refactoring(
                pattern_id=pattern.pattern_id,
                original_code="def test(): pass",
                refactored_code="def test() -> None: pass",
                quality_improvement=0.2,
                complexity_change=0,
                performance_impact="neutral"
            )

        # Calculate confidence
        success_rate = finetuner.intelligence._calculate_success_rate(pattern.pattern_id)
        confidence = finetuner._calculate_confidence(pattern, success_rate)

        assert confidence > 0
        assert confidence <= 1.0
        assert confidence > success_rate * 0.7  # Should boost with occurrences

    def test_benefit_estimation(self):
        """Test benefit level estimation"""
        finetuner = AgentFineTuner()

        high = finetuner._estimate_benefit(0.4)
        medium = finetuner._estimate_benefit(0.15)
        low = finetuner._estimate_benefit(0.05)

        assert high == "high"
        assert medium == "medium"
        assert low == "low"

    def test_reasoning_generation(self):
        """Test reasoning text generation"""
        finetuner = AgentFineTuner()

        pattern = type('Pattern', (), {'complexity': 5.0})()
        recommendation = {"quality_improvement": 0.25}

        reasoning = finetuner._generate_reasoning(
            pattern,
            recommendation,
            AgentSpecialization.SECURITY
        )

        assert "security" in reasoning.lower()
        assert "25%" in reasoning

    def test_multiple_languages_training(self):
        """Test training agents on multiple languages"""
        finetuner = AgentFineTuner()

        for lang in ["python", "javascript", "go"]:
            finetuner.create_agent_profile(
                agent_name=f"Agent_{lang}",
                specialization=AgentSpecialization.PERFORMANCE,
                language=lang
            )

            pattern = finetuner.intelligence.extract_pattern(
                code=f"code_{lang}",
                pattern_type=CodePatternType.FUNCTION,
                language=lang,
                name=f"test_{lang}",
                complexity=2.0
            )

            finetuner.intelligence.record_refactoring(
                pattern_id=pattern.pattern_id,
                original_code=f"code_{lang}",
                refactored_code=f"refactored_{lang}",
                quality_improvement=0.2,
                complexity_change=0,
                performance_impact="improved"
            )

            finetuner.train_agent(f"Agent_{lang}", lang)

        # Verify training per language
        assert len(finetuner.agent_profiles) == 3
        for agent_name, profile in finetuner.agent_profiles.items():
            assert profile.learning_iterations == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
