"""Anomaly model - represents detected CAQI anomalies."""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey, Index
from api.db.database import Base


class Anomaly(Base):
    """Detected anomalies in team CAQI scores."""

    __tablename__ = "anomalies"

    id = Column(String(36), primary_key=True)
    team_id = Column(String(255), ForeignKey("team_scores.team_id", ondelete="SET NULL"), nullable=False)

    # Dimension and score change
    dimension = Column(String(50), nullable=False)  # security, complexity, etc.
    previous_score = Column(Float, nullable=False)
    current_score = Column(Float, nullable=False)
    change_percent = Column(Float, nullable=False)
    severity = Column(String(20))  # low, medium, high, critical

    # Detection and review
    detected_at = Column(DateTime, default=datetime.utcnow)
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(String(255))
    reviewed_at = Column(DateTime)
    notes = Column(String)

    # Indexes
    __table_args__ = (
        Index('idx_anomalies_reviewed_date', 'team_id', 'reviewed', 'detected_at'),
        Index('idx_anomalies_severity', 'severity'),
    )

    def __repr__(self):
        return f"<Anomaly {self.team_id}:{self.dimension} {self.change_percent:+.1f}% ({self.severity})>"
