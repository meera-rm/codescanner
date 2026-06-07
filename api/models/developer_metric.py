"""Developer metrics model - tracks individual developer contributions."""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Index, UniqueConstraint
from api.db.database import Base


class DeveloperMetric(Base):
    """Individual developer contribution metrics."""

    __tablename__ = "developer_metrics"

    id = Column(String(36), primary_key=True)
    developer_id = Column(String(255), nullable=False)
    team_id = Column(String(255), ForeignKey("team_scores.team_id", ondelete="CASCADE"), nullable=False)

    # Dimension contributions (-100 to +100)
    security_contribution = Column(Float, default=0)
    complexity_contribution = Column(Float, default=0)
    documentation_contribution = Column(Float, default=0)
    testing_contribution = Column(Float, default=0)
    dependencies_contribution = Column(Float, default=0)
    maintainability_contribution = Column(Float, default=0)

    # Overall contribution
    overall_contribution = Column(Float, default=0)

    # Timestamp
    calculated_at = Column(DateTime, default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        UniqueConstraint('developer_id', 'team_id', 'calculated_at', name='unique_dev_team_date'),
        Index('idx_developer_metrics_date', 'team_id', 'calculated_at'),
    )

    def __repr__(self):
        return f"<DeveloperMetric {self.developer_id}:{self.team_id} overall={self.overall_contribution:+.1f}>"
