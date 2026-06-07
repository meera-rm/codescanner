"""Personality archetype mapping for Path I."""

from typing import Dict, List


class PersonalityMappingService:
    """Map CAQI dimensions to personality archetypes."""

    ARCHETYPES = {
        "Reckless Optimist": {
            "description": "Ships fast, refines later. Low process overhead, high velocity.",
            "characteristics": [
                "Minimal documentation",
                "Limited test coverage",
                "Quick iteration cycles",
                "Low dependency awareness"
            ],
            "dimension_profile": {
                "documentation": "low",
                "testing": "low",
                "complexity": "low",
                "dependencies": "variable"
            },
            "strengths": ["Speed to market", "Innovation", "Agility"],
            "risks": ["Technical debt", "Regressions", "Maintainability"]
        },
        "Cautious Perfectionist": {
            "description": "High quality, thorough process. Everything documented and tested.",
            "characteristics": [
                "Comprehensive documentation",
                "High test coverage",
                "Careful change management",
                "Low complexity through decomposition"
            ],
            "dimension_profile": {
                "documentation": "high",
                "testing": "high",
                "complexity": "low",
                "dependencies": "low"
            },
            "strengths": ["Reliability", "Maintainability", "Knowledge sharing"],
            "risks": ["Slower velocity", "Over-engineering"]
        },
        "Secretive Perfectionist": {
            "description": "High quality code, poor communication. Great code, hard to understand.",
            "characteristics": [
                "Minimal documentation",
                "High test coverage",
                "Complex implementations",
                "Works in isolation"
            ],
            "dimension_profile": {
                "documentation": "low",
                "testing": "high",
                "complexity": "high",
                "dependencies": "variable"
            },
            "strengths": ["Code quality", "Reliability", "Robustness"],
            "risks": ["Knowledge silos", "Onboarding friction", "Bus factor"]
        },
        "Anxious Overthinker": {
            "description": "Manages every risk. Highly defensive coding practices.",
            "characteristics": [
                "Comprehensive documentation",
                "Very high test coverage",
                "Dependency management obsession",
                "Complex defensive code"
            ],
            "dimension_profile": {
                "documentation": "high",
                "testing": "high",
                "dependencies": "high",
                "complexity": "high"
            },
            "strengths": ["Risk mitigation", "Stability", "Thoroughness"],
            "risks": ["Velocity", "Complexity", "Overengineering"]
        },
        "Pragmatic Engineer": {
            "description": "Balanced approach. Makes trade-offs based on context.",
            "characteristics": [
                "Reasonable documentation",
                "Good test coverage",
                "Managed complexity",
                "Thoughtful dependency choices"
            ],
            "dimension_profile": {
                "documentation": "medium",
                "testing": "medium",
                "complexity": "medium",
                "dependencies": "medium"
            },
            "strengths": ["Balance", "Adaptability", "Sustainability"],
            "risks": ["None apparent - this is the target state"]
        }
    }

    @staticmethod
    def get_archetype_profile(archetype: str) -> Dict:
        """Get detailed profile for an archetype."""
        return PersonalityMappingService.ARCHETYPES.get(
            archetype,
            PersonalityMappingService.ARCHETYPES["Pragmatic Engineer"]
        )

    @staticmethod
    def get_archetype_description(archetype: str) -> str:
        """Get human-readable description of archetype."""
        profile = PersonalityMappingService.get_archetype_profile(archetype)
        return profile["description"]

    @staticmethod
    def suggest_improvements(archetype: str, current_dimensions: Dict) -> List[str]:
        """
        Suggest improvements based on archetype profile and current state.

        Args:
            archetype: Current personality archetype
            current_dimensions: Dict with current dimension scores

        Returns:
            List of improvement suggestions
        """

        suggestions = []
        docs = current_dimensions.get("documentation", 50)
        testing = current_dimensions.get("testing", 50)
        complexity = current_dimensions.get("complexity", 50)
        deps = current_dimensions.get("dependencies", 50)

        if archetype == "Reckless Optimist":
            suggestions.extend([
                "Increase test coverage (currently low: {:.0f}%)".format(testing),
                "Document critical APIs and data models",
                "Implement code review process to catch regressions",
                "Create architectural decision records (ADRs)"
            ])

        elif archetype == "Secretive Perfectionist":
            suggestions.extend([
                "Increase code documentation (currently low: {:.0f}%)".format(docs),
                "Add inline comments explaining complex logic",
                "Pair program or do knowledge transfer sessions",
                "Simplify implementations where possible (current complexity: {:.0f}%)".format(complexity)
            ])

        elif archetype == "Anxious Overthinker":
            suggestions.extend([
                "Focus on high-impact dependencies (currently all: {:.0f}%)".format(deps),
                "Simplify testing to focus on critical paths",
                "Document the 'why' behind defensive practices",
                "Balance perfection with velocity - set 'good enough' thresholds"
            ])

        elif archetype == "Pragmatic Engineer":
            suggestions.extend([
                "Continue current approach - this is the target state",
                "Monitor trend to ensure balance is maintained",
                "Document decisions to help team maintain pragmatism"
            ])

        return suggestions

    @staticmethod
    def get_team_profile_summary(archetype: str) -> Dict:
        """Get full team profile summary for an archetype."""
        profile = PersonalityMappingService.get_archetype_profile(archetype)
        return {
            "archetype": archetype,
            "description": profile["description"],
            "characteristics": profile["characteristics"],
            "strengths": profile["strengths"],
            "risks": profile["risks"],
            "dimension_profile": profile["dimension_profile"]
        }

    @staticmethod
    def compare_archetypes(archetype1: str, archetype2: str) -> Dict:
        """
        Compare two archetypes to understand differences.

        Args:
            archetype1: First archetype
            archetype2: Second archetype

        Returns:
            Comparison dict with strengths/risks of each
        """

        profile1 = PersonalityMappingService.get_archetype_profile(archetype1)
        profile2 = PersonalityMappingService.get_archetype_profile(archetype2)

        return {
            archetype1: {
                "description": profile1["description"],
                "strengths": profile1["strengths"],
                "risks": profile1["risks"]
            },
            archetype2: {
                "description": profile2["description"],
                "strengths": profile2["strengths"],
                "risks": profile2["risks"]
            },
            "note": f"Moving from {archetype1} to {archetype2}..."
        }
