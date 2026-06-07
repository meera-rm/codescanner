"""CAQI History ORM model (simplified for Phase I+1)."""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from api.db.database import Base


class CAQIHistory(Base):
    """Historical CAQI score record."""
    __tablename__ = "caqi_history"

    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("team_scores.team_id"))
    overall_caqi = Column(Float)
    security = Column(Float)
    complexity = Column(Float)
    documentation = Column(Float)
    testing = Column(Float)
    dependencies = Column(Float)
    maintainability = Column(Float)
    recorded_at = Column(DateTime, default=datetime.utcnow)
