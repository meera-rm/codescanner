from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from sqlalchemy import func
from api.db.database import SessionLocal
from api.db.models import ScanJob, Metrics


class MetricsService:
    """Service for tracking and analyzing metrics over time."""

    def __init__(self):
        self.db = SessionLocal()

    def get_summary(self) -> Dict[str, Any]:
        """Get overall metrics summary."""
        recent_scans = self.db.query(ScanJob).filter(
            ScanJob.status == "completed"
        ).order_by(ScanJob.completed_at.desc()).limit(100).all()

        if not recent_scans:
            return self._empty_summary()

        quality_scores = [
            m.get("quality_score", 0)
            for s in recent_scans
            for m in [s.metrics] if m and "quality_score" in m
        ]

        total_findings = sum(
            m.get("total_findings", 0)
            for s in recent_scans
            for m in [s.metrics] if m
        )

        critical_count = sum(
            m.get("critical_count", 0)
            for s in recent_scans
            for m in [s.metrics] if m
        )

        return {
            "total_scans": len(recent_scans),
            "average_quality_score": sum(quality_scores) / len(quality_scores) if quality_scores else 0,
            "total_issues_found": total_findings,
            "critical_issues": critical_count,
            "average_scan_duration_ms": sum(
                s.duration_ms or 0 for s in recent_scans
            ) / len(recent_scans) if recent_scans else 0,
            "success_rate": len([s for s in recent_scans if s.status == "completed"]) / len(recent_scans) * 100,
        }

    def get_trends(self, days: int = 30) -> Dict[str, List[Dict]]:
        """Get quality trends over time."""
        threshold = datetime.utcnow() - timedelta(days=days)

        scans = self.db.query(ScanJob).filter(
            ScanJob.completed_at >= threshold,
            ScanJob.status == "completed",
        ).order_by(ScanJob.completed_at).all()

        daily_data = {}
        for scan in scans:
            if scan.completed_at:
                date_key = scan.completed_at.strftime("%Y-%m-%d")
                if date_key not in daily_data:
                    daily_data[date_key] = {
                        "date": date_key,
                        "scans": 0,
                        "avg_quality": 0,
                        "total_issues": 0,
                    }

                if scan.metrics:
                    daily_data[date_key]["scans"] += 1
                    daily_data[date_key]["avg_quality"] += scan.metrics.get("quality_score", 0)
                    daily_data[date_key]["total_issues"] += scan.metrics.get("total_findings", 0)

        for date_key in daily_data:
            if daily_data[date_key]["scans"] > 0:
                daily_data[date_key]["avg_quality"] /= daily_data[date_key]["scans"]

        return {"trends": list(daily_data.values())}

    def get_top_issues(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most common issues across all scans."""
        recent_scans = self.db.query(ScanJob).filter(
            ScanJob.status == "completed"
        ).order_by(ScanJob.completed_at.desc()).limit(50).all()

        issue_counts = {}
        for scan in recent_scans:
            if scan.findings:
                for finding in scan.findings:
                    issue_type = finding.get("type", "unknown")
                    if issue_type not in issue_counts:
                        issue_counts[issue_type] = {
                            "type": issue_type,
                            "count": 0,
                            "severity": finding.get("severity", "unknown"),
                        }
                    issue_counts[issue_type]["count"] += 1

        sorted_issues = sorted(
            issue_counts.values(), key=lambda x: x["count"], reverse=True
        )[:limit]

        return sorted_issues

    def get_team_stats(self) -> Dict[str, Any]:
        """Get team-level statistics."""
        total_scans = self.db.query(ScanJob).count()
        completed_scans = self.db.query(ScanJob).filter(
            ScanJob.status == "completed"
        ).count()

        avg_quality = 0
        quality_scores = [
            m.get("quality_score", 0)
            for s in self.db.query(ScanJob).filter(ScanJob.status == "completed").all()
            for m in [s.metrics] if m and "quality_score" in m
        ]

        if quality_scores:
            avg_quality = sum(quality_scores) / len(quality_scores)

        return {
            "total_scans": total_scans,
            "completed_scans": completed_scans,
            "average_quality_score": avg_quality,
            "success_rate": completed_scans / total_scans * 100 if total_scans > 0 else 0,
        }

    def _empty_summary(self) -> Dict[str, Any]:
        """Return empty summary when no data available."""
        return {
            "total_scans": 0,
            "average_quality_score": 0,
            "total_issues_found": 0,
            "critical_issues": 0,
            "average_scan_duration_ms": 0,
            "success_rate": 0,
        }

    def __del__(self):
        """Close database connection."""
        if self.db:
            self.db.close()
