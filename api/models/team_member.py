"""Team Member ORM model (simplified for Phase I+1)."""
from sqlalchemy import Column, String, ForeignKey
from api.db.database import Base


class TeamMember(Base):
    """Team member record."""
    __tablename__ = "team_members"

    id = Column(String, primary_key=True, index=True)
    team_id = Column(String, ForeignKey("team_scores.team_id"))
    developer_id = Column(String)

    def __init__(self, team_id, developer_id, **kwargs):
        self.team_id = team_id
        self.developer_id = developer_id
        super().__init__(**kwargs)
