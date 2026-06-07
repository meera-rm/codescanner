"""Team registration and management for Path I (CAQI Team Analytics)."""

from typing import List, Optional
from sqlalchemy.orm import Session
from api.db.database import SessionLocal
from api.db.models import TeamScore, TeamMember
from datetime import datetime
import uuid


class TeamService:
    """Manage team creation, registration, and membership."""

    @staticmethod
    def create_team(
        team_id: str,
        team_name: str,
        developer_ids: List[str],
        db: Optional[Session] = None
    ) -> TeamScore:
        """
        Create a new team and register developers.

        Called once per team during initial setup.

        Args:
            team_id: Unique identifier for the team (e.g., "backend-team")
            team_name: Human-readable team name (e.g., "Backend Engineering")
            developer_ids: List of developer identifiers (emails, user IDs, etc.)
            db: Database session (creates new if not provided)

        Returns:
            TeamScore object with team created

        Example:
            TeamService.create_team(
                team_id="backend-team",
                team_name="Backend Engineering",
                developer_ids=["alice@company.com", "bob@company.com"]
            )
        """
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        try:
            # Check if team already exists
            existing = db.query(TeamScore).filter(
                TeamScore.team_id == team_id
            ).first()

            if existing:
                raise ValueError(f"Team '{team_id}' already exists")

            # Create team record
            team = TeamScore(
                id=str(uuid.uuid4()),
                team_id=team_id,
                team_name=team_name,
                member_count=len(developer_ids),
                calculated_at=datetime.utcnow()
            )

            db.add(team)
            db.flush()  # Ensure team is created before adding members

            # Register team members
            for dev_id in developer_ids:
                # Check for duplicates
                existing_member = db.query(TeamMember).filter(
                    TeamMember.team_id == team_id,
                    TeamMember.developer_id == dev_id
                ).first()

                if not existing_member:
                    member = TeamMember(
                        id=str(uuid.uuid4()),
                        team_id=team_id,
                        developer_id=dev_id,
                        added_at=datetime.utcnow()
                    )
                    db.add(member)

            db.commit()
            db.refresh(team)  # Ensure team object is still valid
            return team

        except Exception as e:
            db.rollback()
            raise
        finally:
            if should_close:
                db.close()

    @staticmethod
    def add_team_member(
        team_id: str,
        developer_id: str,
        db: Optional[Session] = None
    ) -> TeamMember:
        """Add a developer to an existing team."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        try:
            # Verify team exists
            team = db.query(TeamScore).filter(
                TeamScore.team_id == team_id
            ).first()

            if not team:
                raise ValueError(f"Team '{team_id}' not found")

            # Check if already a member
            existing = db.query(TeamMember).filter(
                TeamMember.team_id == team_id,
                TeamMember.developer_id == developer_id
            ).first()

            if existing:
                raise ValueError(f"Developer '{developer_id}' already in team")

            # Add member
            member = TeamMember(
                id=str(uuid.uuid4()),
                team_id=team_id,
                developer_id=developer_id,
                added_at=datetime.utcnow()
            )

            db.add(member)
            db.commit()

            return member

        except Exception as e:
            db.rollback()
            raise
        finally:
            if should_close:
                db.close()

    @staticmethod
    def get_team(team_id: str, db: Optional[Session] = None) -> Optional[TeamScore]:
        """Get team by ID."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        try:
            return db.query(TeamScore).filter(
                TeamScore.team_id == team_id
            ).first()
        finally:
            if should_close:
                db.close()

    @staticmethod
    def get_all_teams(db: Optional[Session] = None) -> List[TeamScore]:
        """Get all registered teams."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        try:
            return db.query(TeamScore).all()
        finally:
            if should_close:
                db.close()

    @staticmethod
    def get_team_members(team_id: str, db: Optional[Session] = None) -> List[TeamMember]:
        """Get all members of a team."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        try:
            return db.query(TeamMember).filter(
                TeamMember.team_id == team_id
            ).all()
        finally:
            if should_close:
                db.close()

    @staticmethod
    def delete_team(team_id: str, db: Optional[Session] = None) -> None:
        """Delete a team and all associated data (cascade)."""
        should_close = False
        if db is None:
            db = SessionLocal()
            should_close = True

        try:
            team = db.query(TeamScore).filter(
                TeamScore.team_id == team_id
            ).first()

            if not team:
                raise ValueError(f"Team '{team_id}' not found")

            db.delete(team)
            db.commit()
        except Exception as e:
            db.rollback()
            raise
        finally:
            if should_close:
                db.close()
