"""Alert model - represents system alerts."""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Index
from api.db.database import Base


class Alert(Base):
    """System alerts triggered by anomalies or thresholds."""

    __tablename__ = "alerts"

    id = Column(String(36), primary_key=True)
    team_id = Column(String(255), ForeignKey("team_scores.team_id", ondelete="SET NULL"), nullable=False)

    # Alert content
    alert_type = Column(String(50), nullable=False)  # anomaly_detected, threshold_crossed, etc.
    title = Column(String(255), nullable=False)
    description = Column(String)
    severity = Column(String(20))  # info, warning, critical

    # Status
    triggered_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String(255))
    acknowledged_at = Column(DateTime)

    # Notification
    notification_sent_at = Column(DateTime)
    channels = Column(String)  # "email,slack,in-app"

    # Indexes
    __table_args__ = (
        Index('idx_alerts_acknowledged_date', 'team_id', 'acknowledged', 'triggered_at'),
        Index('idx_alerts_type_severity', 'alert_type', 'severity'),
    )

    def __repr__(self):
        return f"<Alert {self.team_id}:{self.alert_type} ({self.severity})>"
