"""Peer Comparison Service - compare team CAQI to peer groups and benchmarks."""
import logging
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional

from api.db.database import SessionLocal
from api.models.team_score import TeamScore
from api.models.peer_group import PeerGroup
from api.models.benchmark import Benchmark
from api.services.anomaly_detection import AnomalyDetectionService

logger = logging.getLogger(__name__)


class PeerComparisonService:
    """Compare team CAQI to peer groups and industry benchmarks."""

    @staticmethod
    def create_peer_group(
        name: str,
        team_ids: List[str],
        description: Optional[str] = None,
        db: SessionLocal = None
    ) -> PeerGroup:
        """
        Create a peer group for comparison.

        Args:
            name: Peer group name
            team_ids: List of team IDs in group
            description: Optional description
            db: Database session

        Returns:
            Created PeerGroup object
        """
        if not name:
            raise ValueError("Peer group name is required")

        if not team_ids:
            raise ValueError("At least one team ID is required")

        peer_group = PeerGroup(
            id=str(uuid.uuid4()),
            peer_group_name=name,
            description=description,
            created_at=datetime.utcnow()
        )
        peer_group.set_team_ids(team_ids)

        db.add(peer_group)
        db.commit()

        logger.info(f"Created peer group '{name}' with {len(team_ids)} teams")
        return peer_group

    @staticmethod
    def get_peer_comparison(
        team_id: str,
        peer_group_name: str,
        db: SessionLocal
    ) -> Dict:
        """
        Compare team to peer group with validation and error handling.

        CRITICAL FIXES:
        - Validates team exists
        - Validates peer group exists
        - Handles empty peer groups
        - Handles no peer data available
        - Returns error dict instead of crashing

        Args:
            team_id: Team to analyze
            peer_group_name: Name of peer group
            db: Database session

        Returns:
            Dictionary with comparison data or error message
        """
        # FIXED: Validate team exists
        team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
        if not team:
            logger.warning(f"Team {team_id} not found")
            raise ValueError(f"Team {team_id} not found")

        # FIXED: Validate peer group exists
        peer_group = db.query(PeerGroup).filter(
            PeerGroup.peer_group_name == peer_group_name
        ).first()

        if not peer_group:
            logger.warning(f"Peer group '{peer_group_name}' not found")
            raise ValueError(f"Peer group '{peer_group_name}' not found")

        peer_team_ids = peer_group.get_team_ids()

        # FIXED: Handle empty peer group
        if not peer_team_ids:
            logger.warning(f"Peer group '{peer_group_name}' is empty")
            return {
                'error': 'Peer group is empty',
                'team_id': team_id,
                'peer_group': peer_group_name
            }

        # Get peer scores (exclude self)
        peer_scores = db.query(TeamScore).filter(
            TeamScore.team_id.in_(peer_team_ids),
            TeamScore.team_id != team_id
        ).all()

        # FIXED: Handle no peers available
        if not peer_scores:
            logger.warning(f"No peer data available for group '{peer_group_name}'")
            return {
                'error': 'No peer data available',
                'team_id': team_id,
                'peer_group': peer_group_name
            }

        # Calculate comparison
        dimensions = [
            'security', 'complexity', 'documentation',
            'testing', 'dependencies', 'maintainability'
        ]

        comparison = {
            'team_id': team_id,
            'team_name': team.team_name,
            'team_caqi': team.overall_caqi,
            'peer_group': peer_group_name,
            'peer_count': len(peer_scores),
            'peer_avg_caqi': sum(s.overall_caqi for s in peer_scores) / len(peer_scores),
            'dimensions': {}
        }

        for dimension in dimensions:
            team_score = getattr(team, dimension)
            peer_values = [getattr(s, dimension) for s in peer_scores]
            peer_avg = sum(peer_values) / len(peer_values)

            # FIXED: Use corrected percentile calculation
            percentile = AnomalyDetectionService.calculate_percentile(team_score, peer_values)

            comparison['dimensions'][dimension] = {
                'team_score': round(team_score, 2),
                'peer_avg': round(peer_avg, 2),
                'percentile': percentile,
                'diff': round(team_score - peer_avg, 2)
            }

        logger.info(f"Comparison complete: {team_id} vs {peer_group_name}")
        return comparison

    @staticmethod
    def calculate_benchmarks(
        benchmark_type: str,
        db: SessionLocal
    ) -> Dict[str, Benchmark]:
        """
        Calculate benchmarks from all teams.

        Args:
            benchmark_type: Type of benchmark (industry, peer_group, company)
            db: Database session

        Returns:
            Dictionary of dimension -> Benchmark
        """
        teams = db.query(TeamScore).all()

        if not teams:
            logger.warning(f"No teams available for {benchmark_type} benchmark calculation")
            return {}

        dimensions = [
            'security', 'complexity', 'documentation',
            'testing', 'dependencies', 'maintainability'
        ]

        benchmarks = {}

        for dimension in dimensions:
            values = sorted([getattr(t, dimension) for t in teams if getattr(t, dimension)])

            if not values:
                continue

            # Calculate percentiles
            def get_percentile(p):
                index = int(len(values) * (p / 100))
                return values[min(index, len(values) - 1)]

            benchmark = Benchmark(
                id=str(uuid.uuid4()),
                benchmark_type=benchmark_type,
                dimension=dimension,
                percentile_10=get_percentile(10),
                percentile_25=get_percentile(25),
                percentile_50=get_percentile(50),  # Median
                percentile_75=get_percentile(75),
                percentile_90=get_percentile(90),
                sample_size=len(teams),
                calculated_at=datetime.utcnow()
            )

            db.add(benchmark)
            benchmarks[dimension] = benchmark

        db.commit()

        logger.info(
            f"Calculated {benchmark_type} benchmarks for {len(dimensions)} dimensions "
            f"from {len(teams)} teams"
        )
        return benchmarks

    @staticmethod
    def get_benchmarks(
        benchmark_type: str,
        db: SessionLocal
    ) -> Dict[str, Dict]:
        """
        Get calculated benchmarks for a type.

        Args:
            benchmark_type: Type of benchmark
            db: Database session

        Returns:
            Dictionary of dimension -> benchmark values
        """
        benchmarks = db.query(Benchmark).filter(
            Benchmark.benchmark_type == benchmark_type
        ).all()

        result = {}
        for b in benchmarks:
            result[b.dimension] = {
                'p10': b.percentile_10,
                'p25': b.percentile_25,
                'p50': b.percentile_50,
                'p75': b.percentile_75,
                'p90': b.percentile_90,
                'sample_size': b.sample_size
            }

        return result
