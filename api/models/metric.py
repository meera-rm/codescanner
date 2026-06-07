"""Developer Metric ORM model (simplified for Phase I+1)."""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from api.db.database import Base


class Metric(Base):
    """Individual developer metric record."""
    __tablename__ = "metrics"

    id = Column(String, primary_key=True, index=True)
    developer_id = Column(String)
    team_id = Column(String, ForeignKey("team_scores.team_id"))
    security = Column(Float)
    complexity = Column(Float)
    documentation = Column(Float)
    testing = Column(Float)
    dependencies = Column(Float)
    maintainability = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
