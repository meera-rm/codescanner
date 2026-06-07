"""Peer group model - represents groups of teams for comparison."""
import json
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Index, UniqueConstraint
from api.db.database import Base


class PeerGroup(Base):
    """Groups of teams for peer comparison."""

    __tablename__ = "peer_groups"

    id = Column(String(36), primary_key=True)
    peer_group_name = Column(String(255), nullable=False)
    description = Column(String)

    # Team IDs stored as JSON array
    team_ids = Column(String)  # JSON: ["team-001", "team-002", ...]

    # Timestamp
    created_at = Column(DateTime, default=datetime.utcnow)

    # Constraints
    __table_args__ = (
        UniqueConstraint('peer_group_name', name='unique_peer_group_name'),
        Index('idx_peer_group_created', 'created_at'),
    )

    def get_team_ids(self) -> list:
        """Get list of team IDs."""
        if not self.team_ids:
            return []
        return json.loads(self.team_ids)

    def set_team_ids(self, team_ids: list) -> None:
        """Set list of team IDs."""
        self.team_ids = json.dumps(team_ids)

    def __repr__(self):
        return f"<PeerGroup {self.peer_group_name} ({len(self.get_team_ids())} teams)>"
