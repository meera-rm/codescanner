"""Team Score ORM model (simplified for Phase I+1)."""
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime
from api.db.database import Base


class TeamScore(Base):
    """Aggregated team CAQI score."""
    __tablename__ = "team_scores"

    team_id = Column(String, primary_key=True, index=True)
    team_name = Column(String)
    overall_caqi = Column(Float)
    security = Column(Float)
    complexity = Column(Float)
    documentation = Column(Float)
    testing = Column(Float)
    dependencies = Column(Float)
    maintainability = Column(Float)
    calculated_at = Column(DateTime, default=datetime.utcnow)
