"""Service for managing CI/CD scan history and metrics."""
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from api.db.models import CIScanHistory, CITrendMetrics


class CIHistoryService:
    """Manage CI/CD scan history and trend metrics."""

    @staticmethod
    def record_scan(
        db: Session,
        repository: str,
        branch: str,
        platform: str,
        event_type: str,
        status: str,
        critical_count: int,
        error_count: int,
        warning_count: int,
        info_count: int,
        files_scanned: int,
        languages: Dict[str, int],
        duration_ms: int = 0,
        commit_sha: str = None,
        triggered_by: str = None,
        report_json: dict = None,
        report_sarif: dict = None,
        report_junit: str = None,
        report_sonarqube: dict = None,
    ) -> CIScanHistory:
        """Record a new CI scan execution."""
        scan = CIScanHistory(
            id=str(uuid.uuid4()),
            repository=repository,
            branch=branch,
            platform=platform,
            event_type=event_type,
            status=status,
            critical_count=critical_count,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            total_findings=critical_count + error_count + warning_count + info_count,
            files_scanned=files_scanned,
            languages=languages,
            duration_ms=duration_ms,
            commit_sha=commit_sha,
            triggered_by=triggered_by,
            report_json=report_json,
            report_sarif=report_sarif,
            report_junit=report_junit,
            report_sonarqube=report_sonarqube,
            completed_at=datetime.utcnow(),
        )
        db.add(scan)
        db.commit()
        db.refresh(scan)

        # Update trend metrics
        CIHistoryService.update_trend_metrics(db, repository)

        return scan

    @staticmethod
    def get_scan_history(
        db: Session,
        repository: Optional[str] = None,
        platform: Optional[str] = None,
        status: Optional[str] = None,
        branch: Optional[str] = None,
        days: int = 30,
        limit: int = 100,
    ) -> List[CIScanHistory]:
        """Get scan history with optional filters."""
        query = db.query(CIScanHistory)

        # Apply filters
        if repository:
            query = query.filter(CIScanHistory.repository == repository)
        if platform:
            query = query.filter(CIScanHistory.platform == platform)
        if status:
            query = query.filter(CIScanHistory.status == status)
        if branch:
            query = query.filter(CIScanHistory.branch == branch)

        # Time filter
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(CIScanHistory.created_at >= cutoff)

        # Sort and limit
        results = query.order_by(CIScanHistory.created_at.desc()).limit(limit).all()
        return results

    @staticmethod
    def get_trend_metrics(
        db: Session,
        repository: str,
    ) -> Optional[CITrendMetrics]:
        """Get trend metrics for a repository."""
        return db.query(CITrendMetrics).filter(
            CITrendMetrics.repository == repository
        ).first()

    @staticmethod
    def update_trend_metrics(db: Session, repository: str) -> CITrendMetrics:
        """Update trend metrics for a repository."""
        # Get or create metrics record
        metrics = db.query(CITrendMetrics).filter(
            CITrendMetrics.repository == repository
        ).first()

        if not metrics:
            metrics = CITrendMetrics(id=str(uuid.uuid4()), repository=repository)

        # Get recent scans (30 days)
        cutoff = datetime.utcnow() - timedelta(days=30)
        recent_scans = db.query(CIScanHistory).filter(
            CIScanHistory.repository == repository,
            CIScanHistory.created_at >= cutoff,
        ).all()

        if not recent_scans:
            db.add(metrics)
            db.commit()
            return metrics

        # Calculate metrics
        total_scans = len(recent_scans)
        successful_scans = len([s for s in recent_scans if s.status == "success"])
        failed_scans = len([s for s in recent_scans if s.status == "failure"])

        metrics.last_scan_at = recent_scans[0].created_at
        metrics.total_scans = total_scans
        metrics.successful_scans = successful_scans
        metrics.failed_scans = failed_scans
        metrics.pass_rate = (successful_scans / total_scans * 100) if total_scans > 0 else 0

        # Calculate averages
        metrics.avg_critical_per_scan = sum(s.critical_count for s in recent_scans) / total_scans
        metrics.avg_error_per_scan = sum(s.error_count for s in recent_scans) / total_scans
        metrics.avg_warning_per_scan = sum(s.warning_count for s in recent_scans) / total_scans
        metrics.avg_scan_duration_ms = int(
            sum(s.duration_ms or 0 for s in recent_scans) / total_scans
        )

        # Build trends (aggregated by day)
        trends_by_day = {}
        for scan in recent_scans:
            day = scan.created_at.date()
            if day not in trends_by_day:
                trends_by_day[day] = {
                    'critical': 0,
                    'error': 0,
                    'warning': 0,
                    'scans': 0,
                }
            trends_by_day[day]['critical'] += scan.critical_count
            trends_by_day[day]['error'] += scan.error_count
            trends_by_day[day]['warning'] += scan.warning_count
            trends_by_day[day]['scans'] += 1

        # Convert to trend format
        sorted_days = sorted(trends_by_day.keys())
        metrics.critical_trend = [
            {'date': str(d), 'count': trends_by_day[d]['critical']}
            for d in sorted_days
        ]
        metrics.error_trend = [
            {'date': str(d), 'count': trends_by_day[d]['error']}
            for d in sorted_days
        ]
        metrics.warning_trend = [
            {'date': str(d), 'count': trends_by_day[d]['warning']}
            for d in sorted_days
        ]

        # Platform breakdown
        platform_counts = {}
        for scan in recent_scans:
            platform_counts[scan.platform] = platform_counts.get(scan.platform, 0) + 1
        metrics.platforms = platform_counts

        # Pass rate trend
        pass_rate_trend = []
        for day in sorted_days:
            day_scans = [s for s in recent_scans if s.created_at.date() == day]
            day_successful = len([s for s in day_scans if s.status == "success"])
            day_pass_rate = (day_successful / len(day_scans) * 100) if day_scans else 0
            pass_rate_trend.append({'date': str(day), 'pass_rate': day_pass_rate})
        metrics.pass_rate_trend = pass_rate_trend

        db.add(metrics)
        db.commit()
        db.refresh(metrics)
        return metrics

    @staticmethod
    def get_dashboard_summary(
        db: Session,
        days: int = 30,
    ) -> Dict[str, Any]:
        """Get overall dashboard summary for all repositories."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        # Get all scans in period
        all_scans = db.query(CIScanHistory).filter(
            CIScanHistory.created_at >= cutoff
        ).all()

        if not all_scans:
            return {
                'total_scans': 0,
                'successful_scans': 0,
                'failed_scans': 0,
                'pass_rate': 0.0,
                'total_critical': 0,
                'total_error': 0,
                'total_warning': 0,
                'repositories': [],
                'platforms': {},
            }

        # Aggregate statistics
        total_scans = len(all_scans)
        successful_scans = len([s for s in all_scans if s.status == "success"])
        failed_scans = len([s for s in all_scans if s.status == "failure"])
        total_critical = sum(s.critical_count for s in all_scans)
        total_error = sum(s.error_count for s in all_scans)
        total_warning = sum(s.warning_count for s in all_scans)

        # By repository
        repos = {}
        for scan in all_scans:
            if scan.repository not in repos:
                repos[scan.repository] = {
                    'scans': 0,
                    'critical': 0,
                    'error': 0,
                    'warning': 0,
                    'last_scan': None,
                    'last_status': None,
                }
            repos[scan.repository]['scans'] += 1
            repos[scan.repository]['critical'] += scan.critical_count
            repos[scan.repository]['error'] += scan.error_count
            repos[scan.repository]['warning'] += scan.warning_count
            if repos[scan.repository]['last_scan'] is None:
                repos[scan.repository]['last_scan'] = scan.created_at
                repos[scan.repository]['last_status'] = scan.status

        # By platform
        platforms = {}
        for scan in all_scans:
            platforms[scan.platform] = platforms.get(scan.platform, 0) + 1

        return {
            'total_scans': total_scans,
            'successful_scans': successful_scans,
            'failed_scans': failed_scans,
            'pass_rate': (successful_scans / total_scans * 100) if total_scans > 0 else 0.0,
            'total_critical': total_critical,
            'total_error': total_error,
            'total_warning': total_warning,
            'repositories': [
                {
                    'name': repo,
                    **stats
                }
                for repo, stats in repos.items()
            ],
            'platforms': platforms,
        }

    @staticmethod
    def delete_old_scans(db: Session, days: int = 90) -> int:
        """Delete scans older than specified days."""
        cutoff = datetime.utcnow() - timedelta(days=days)
        count = db.query(CIScanHistory).filter(
            CIScanHistory.created_at < cutoff
        ).delete()
        db.commit()
        return count
