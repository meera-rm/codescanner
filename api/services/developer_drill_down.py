"""Developer Drill-Down Service - attribute CAQI changes to individual developers."""
import logging
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Optional

from api.db.database import SessionLocal
from api.models.team_score import TeamScore
from api.models.team_member import TeamMember
from api.models.metric import Metric

logger = logging.getLogger(__name__)


class DeveloperDrillDownService:
    """Estimate which developers drove dimension changes."""

    @staticmethod
    def calculate_developer_contributions(
        team_id: str,
        days: int = 30,
        db: SessionLocal = None
    ) -> List[Dict]:
        """
        Calculate developer contributions to team CAQI changes.

        CRITICAL FIX:
        - Query ALL team metrics ONCE (not per developer) - O(n) instead of O(n²)
        - Filter in memory instead of database queries
        - Prevents N+1 query problem

        Args:
            team_id: Team to analyze
            days: Number of days to analyze
            db: Database session

        Returns:
            List of developer contributions, sorted by impact (highest first)
        """
        # Get team members
        members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()

        if not members:
            logger.warning(f"No team members found for {team_id}")
            return []

        cutoff_date = datetime.utcnow() - timedelta(days=days)

        # CRITICAL FIX: Query ALL team metrics ONCE (not per developer)
        all_team_metrics = db.query(Metric).filter(
            Metric.team_id == team_id,
            Metric.recorded_at >= cutoff_date
        ).all()

        if not all_team_metrics:
            logger.warning(f"No metrics found for team {team_id} in last {days} days")
            return []

        # Calculate team average (once)
        dimensions = [
            'security', 'complexity', 'documentation',
            'testing', 'dependencies', 'maintainability'
        ]
        team_avg = {}

        for dimension in dimensions:
            values = [getattr(m, dimension) for m in all_team_metrics]
            team_avg[dimension] = sum(values) / len(values) if values else 0

        developer_contributions = []

        # CRITICAL FIX: Filter in memory instead of querying per developer
        for member in members:
            # Get developer's metrics from already-loaded data (not a new query!)
            dev_metrics = [m for m in all_team_metrics if m.developer_id == member.developer_id]

            if not dev_metrics:
                logger.debug(f"No metrics for {member.developer_id}")
                continue

            contributions = {}
            overall = 0

            for dimension in dimensions:
                dev_values = [getattr(m, dimension) for m in dev_metrics]
                dev_avg = sum(dev_values) / len(dev_values)
                contribution = dev_avg - team_avg[dimension]
                contributions[dimension] = {
                    'developer_score': round(dev_avg, 2),
                    'team_avg': round(team_avg[dimension], 2),
                    'contribution': round(contribution, 2)
                }
                overall += contribution

            overall_contribution = overall / len(dimensions) if dimensions else 0

            developer_contributions.append({
                'developer_id': member.developer_id,
                'team_id': team_id,
                'contributions': contributions,
                'overall_contribution': round(overall_contribution, 2)
            })

        # Sort by impact (highest absolute contribution first)
        developer_contributions.sort(
            key=lambda x: abs(x['overall_contribution']),
            reverse=True
        )

        logger.info(
            f"Calculated contributions for {len(developer_contributions)} developers "
            f"on team {team_id} (analyzed {len(all_team_metrics)} metrics)"
        )

        return developer_contributions

    @staticmethod
    def get_top_contributors(
        team_id: str,
        dimension: Optional[str] = None,
        limit: int = 5,
        db: SessionLocal = None
    ) -> List[Dict]:
        """
        Get developers who most impact a specific dimension.

        Args:
            team_id: Team to analyze
            dimension: Specific dimension to focus on (or None for overall)
            limit: Max developers to return
            db: Database session

        Returns:
            List of top contributors
        """
        # Get all contributions
        contributions = DeveloperDrillDownService.calculate_developer_contributions(
            team_id, db=db
        )

        if not contributions:
            return []

        # Sort by dimension-specific or overall contribution
        if dimension:
            contributions.sort(
                key=lambda x: abs(x['contributions'][dimension]['contribution']),
                reverse=True
            )
        else:
            contributions.sort(
                key=lambda x: abs(x['overall_contribution']),
                reverse=True
            )

        return contributions[:limit]

    @staticmethod
    def get_developer_metrics(
        team_id: str,
        developer_id: str,
        days: int = 30,
        db: SessionLocal = None
    ) -> Dict:
        """
        Get detailed metrics for specific developer.

        Args:
            team_id: Team ID
            developer_id: Developer to analyze
            days: Number of days to look back
            db: Database session

        Returns:
            Dictionary with developer's metrics
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        metrics = db.query(Metric).filter(
            Metric.developer_id == developer_id,
            Metric.team_id == team_id,
            Metric.recorded_at >= cutoff_date
        ).order_by(Metric.recorded_at).all()

        if not metrics:
            logger.warning(f"No metrics for {developer_id} on {team_id}")
            return {
                'developer_id': developer_id,
                'team_id': team_id,
                'metrics': []
            }

        dimensions = [
            'security', 'complexity', 'documentation',
            'testing', 'dependencies', 'maintainability'
        ]

        metric_history = []
        for metric in metrics:
            metric_history.append({
                'date': metric.recorded_at.isoformat(),
                'dimensions': {
                    dim: round(getattr(metric, dim), 2) for dim in dimensions
                }
            })

        # Calculate averages
        averages = {}
        for dimension in dimensions:
            values = [getattr(m, dimension) for m in metrics]
            averages[dimension] = round(sum(values) / len(values), 2)

        return {
            'developer_id': developer_id,
            'team_id': team_id,
            'period_days': days,
            'metric_count': len(metrics),
            'averages': averages,
            'history': metric_history
        }
