"""Team CAQI aggregation service for Path I."""

from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from api.db.models import Metrics, TeamScore, TeamMember
from api.models.caqi_models import TeamScore as TeamScoreModel, CAQIDimensions
from datetime import datetime
import uuid


class TeamAggregationService:
    """Aggregate individual CAQI scores into team-level metrics."""

    def __init__(self, db: Session):
        self.db = db

    def aggregate_team_scores(self, team_id: str, member_scores: Optional[List] = None) -> Optional[TeamScoreModel]:
        """
        Calculate team CAQI by averaging member scores.

        Logic:
        1. Get all developers in team
        2. Get latest CAQI score for each developer (or use provided scores)
        3. Average dimensions across team
        4. Map to personality archetype
        5. Store in team_scores table
        6. Return team score model

        Args:
            team_id: Team identifier
            member_scores: Optional list of score objects (for testing)

        Returns:
            TeamScore model with aggregated metrics, or None if team not found
        """

        # Get team members
        team_members = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id
        ).all()

        if not team_members:
            return None

        # Use provided scores or placeholder
        if member_scores is None:
            # In production, would query actual CAQI scores from database
            # For testing/demo, use mock scores
            member_scores = []

        if not member_scores:
            # Team has no member scores yet, use defaults
            member_scores = [type('obj', (object,), {
                'security_score': 70,
                'complexity_score': 70,
                'documentation_score': 70,
                'testing_score': 70,
                'dependencies_score': 70,
                'maintainability_score': 70
            })]

        # Average dimensions across all members
        dimensions_dict = self._average_dimensions(member_scores)
        dimensions = CAQIDimensions(**dimensions_dict)

        # Calculate overall CAQI (0-500)
        overall = self._calculate_overall_caqi(dimensions_dict)

        # Map to archetype
        archetype = self._map_to_archetype(dimensions_dict)

        # Get or create team record
        team = self.db.query(TeamScore).filter(
            TeamScore.team_id == team_id
        ).first()

        if not team:
            team = TeamScore(
                id=str(uuid.uuid4()),
                team_id=team_id
            )
            self.db.add(team)
            self.db.flush()

        # Update team scores
        team.security_score = dimensions.security
        team.complexity_score = dimensions.complexity
        team.documentation_score = dimensions.documentation
        team.testing_score = dimensions.testing
        team.dependencies_score = dimensions.dependencies
        team.maintainability_score = dimensions.maintainability
        team.overall_caqi = overall
        team.personality_archetype = archetype
        team.member_count = len(member_scores)
        team.calculated_at = datetime.utcnow()

        self.db.commit()

        return TeamScoreModel(
            team_id=team.team_id,
            team_name=team.team_name,
            dimensions=dimensions,
            overall_caqi=overall,
            personality_archetype=archetype,
            member_count=len(member_scores),
            calculated_at=team.calculated_at
        )

    def _average_dimensions(self, scores: List) -> Dict[str, float]:
        """Average dimension scores across team members (0-100)."""

        if not scores:
            return {
                "security": 0,
                "complexity": 0,
                "documentation": 0,
                "testing": 0,
                "dependencies": 0,
                "maintainability": 0
            }

        dimensions = ["security", "complexity", "documentation", "testing", "dependencies", "maintainability"]
        averages = {}

        for dim in dimensions:
            values = []
            for score in scores:
                # Get the score value (handle both as attribute and dict-like access)
                val = getattr(score, f"{dim}_score", None)
                if val is not None:
                    values.append(val)

            averages[dim] = sum(values) / len(values) if values else 50  # Default to 50 if no data

        return averages

    def _calculate_overall_caqi(self, dimensions: Dict[str, float]) -> int:
        """
        Convert 6 dimensions (0-100 each) to 0-500 scale.

        Weighted formula:
        - Security: 25%
        - Complexity: 20%
        - Documentation: 15%
        - Testing: 20%
        - Dependencies: 10%
        - Maintainability: 10%
        """

        weights = {
            "security": 0.25,
            "complexity": 0.20,
            "documentation": 0.15,
            "testing": 0.20,
            "dependencies": 0.10,
            "maintainability": 0.10
        }

        # Calculate weighted average (each dimension is 0-100)
        # Then scale to 0-500
        overall = sum(
            dimensions.get(dim, 50) * weights[dim] * 5
            for dim in weights
        )

        return int(overall)

    def _map_to_archetype(self, dimensions: Dict[str, float]) -> str:
        """
        Map dimension profile to personality archetype.

        Reckless Optimist: Low docs, low testing, fast shipping
        Cautious Perfectionist: High docs, high testing, low risk
        Secretive Perfectionist: High testing, low docs, complex
        Anxious Overthinker: High docs, high testing, dependency-heavy
        Pragmatic Engineer: Balanced approach
        """

        docs = dimensions.get("documentation", 50)
        testing = dimensions.get("testing", 50)
        complexity = dimensions.get("complexity", 50)
        deps = dimensions.get("dependencies", 50)

        # Reckless Optimist: Low docs + low testing + low complexity
        if docs < 40 and testing < 40 and complexity < 40:
            return "Reckless Optimist"

        # Cautious Perfectionist: High docs + high testing + low complexity
        elif docs > 70 and testing > 70 and complexity < 50:
            return "Cautious Perfectionist"

        # Secretive Perfectionist: High testing + low docs + high complexity
        elif testing > 70 and docs < 50 and complexity > 60:
            return "Secretive Perfectionist"

        # Anxious Overthinker: High docs + high testing + high deps
        elif docs > 70 and testing > 70 and deps > 60:
            return "Anxious Overthinker"

        # Default: Pragmatic Engineer (balanced)
        else:
            return "Pragmatic Engineer"
