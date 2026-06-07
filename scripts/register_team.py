#!/usr/bin/env python3
"""
Path I: Team Registration Script
Registers teams in the database for CAQI Enhanced team analytics.

CRITICAL: Teams must be registered before testing CAQI API endpoints.
Without teams, all /api/v1/caqi/team/{team_id} calls will return 404.

Usage:
    python3 scripts/register_team.py                    # Interactive mode
    python3 scripts/register_team.py --env production   # Production teams
    python3 scripts/register_team.py --sample           # Register sample teams
"""

import sys
import argparse
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.db.database import SessionLocal
from api.models.team import Team
from api.models.team_member import TeamMember
from api.models.team_score import TeamScore
from api.models.metric import Metric


def register_team_interactive():
    """Interactive team registration."""
    print("\n" + "="*70)
    print("TEAM REGISTRATION — Path I: CAQI Enhanced")
    print("="*70)

    db = SessionLocal()

    try:
        # Get team info
        team_id = input("\nTeam ID (e.g., team-001): ").strip()
        team_name = input("Team Name (e.g., Engineering Team): ").strip()

        if not team_id or not team_name:
            print("❌ Team ID and Name are required")
            return False

        # Check if team exists
        existing = db.query(Team).filter(Team.team_id == team_id).first()
        if existing:
            print(f"\n⚠️  Team '{team_id}' already exists")
            return False

        # Create team
        team = Team(
            team_id=team_id,
            team_name=team_name,
            created_at=datetime.utcnow()
        )
        db.add(team)
        db.commit()
        print(f"\n✅ Team created: {team_name} ({team_id})")

        # Add team members
        while True:
            dev_id = input("Developer email (or 'done' to finish): ").strip()
            if dev_id.lower() == 'done':
                break

            if '@' not in dev_id:
                print("❌ Invalid email format")
                continue

            member = TeamMember(
                team_id=team_id,
                developer_id=dev_id,
                role="contributor",
                joined_at=datetime.utcnow()
            )
            db.add(member)
            db.commit()
            print(f"  ✅ Added {dev_id}")

        # Initialize team score
        team_score = TeamScore(
            team_id=team_id,
            overall_caqi=0,
            security=0,
            complexity=0,
            documentation=0,
            testing=0,
            dependencies=0,
            maintainability=0,
            calculated_at=datetime.utcnow()
        )
        db.add(team_score)
        db.commit()
        print(f"\n✅ Team score initialized: {team_name}")

        print("\n" + "="*70)
        print("REGISTRATION COMPLETE")
        print("="*70)
        print(f"Team ID: {team_id}")
        print(f"Name: {team_name}")
        print(f"Members: {db.query(TeamMember).filter(TeamMember.team_id == team_id).count()}")
        print("\nYou can now test the API:")
        print(f"  curl http://localhost:8000/api/v1/caqi/team/{team_id}")
        print("="*70 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def register_sample_teams():
    """Register sample teams for testing."""
    print("\n" + "="*70)
    print("REGISTERING SAMPLE TEAMS")
    print("="*70)

    db = SessionLocal()

    sample_teams = [
        {
            "team_id": "engineering",
            "team_name": "Engineering Team",
            "members": ["alice@example.com", "bob@example.com", "charlie@example.com"],
        },
        {
            "team_id": "platform",
            "team_name": "Platform Team",
            "members": ["diana@example.com", "eve@example.com"],
        },
        {
            "team_id": "data",
            "team_name": "Data Team",
            "members": ["frank@example.com", "grace@example.com", "henry@example.com"],
        },
    ]

    try:
        for team_data in sample_teams:
            team_id = team_data["team_id"]

            # Skip if exists
            existing = db.query(Team).filter(Team.team_id == team_id).first()
            if existing:
                print(f"⏭️  Skipping {team_id} (already exists)")
                continue

            # Create team
            team = Team(
                team_id=team_id,
                team_name=team_data["team_name"],
                created_at=datetime.utcnow()
            )
            db.add(team)
            db.commit()

            # Add members
            for dev_id in team_data["members"]:
                member = TeamMember(
                    team_id=team_id,
                    developer_id=dev_id,
                    role="contributor",
                    joined_at=datetime.utcnow()
                )
                db.add(member)
            db.commit()

            # Initialize score
            team_score = TeamScore(
                team_id=team_id,
                overall_caqi=350 + (hash(team_id) % 100),  # Random score
                security=75 + (hash(team_id) % 25),
                complexity=70 + (hash(team_id) % 30),
                documentation=65 + (hash(team_id) % 35),
                testing=80 + (hash(team_id) % 20),
                dependencies=60 + (hash(team_id) % 40),
                maintainability=75 + (hash(team_id) % 25),
                calculated_at=datetime.utcnow()
            )
            db.add(team_score)
            db.commit()

            print(f"✅ Registered {team_data['team_name']} ({team_id})")
            print(f"   Members: {', '.join(team_data['members'])}")

        print("\n" + "="*70)
        print("SAMPLE TEAMS CREATED")
        print("="*70)
        print("\nTest the API:")
        print("  curl http://localhost:8000/api/v1/caqi/team/engineering")
        print("  curl http://localhost:8000/api/v1/caqi/comparison")
        print("="*70 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ Error: {e}")
        db.rollback()
        return False
    finally:
        db.close()


def register_production_teams():
    """Register production teams."""
    print("\n" + "="*70)
    print("REGISTERING PRODUCTION TEAMS")
    print("="*70)
    print("\nThis is a placeholder for your production teams.")
    print("Update this function with your actual team configuration.")
    print("\nExample teams to add:")
    print("  - Team IDs from your organization")
    print("  - Developer email addresses")
    print("  - Team names and roles")
    print("\nThen run: python3 scripts/register_team.py --env production")
    print("="*70 + "\n")
    return False


def verify_teams():
    """List all registered teams."""
    print("\n" + "="*70)
    print("REGISTERED TEAMS")
    print("="*70)

    db = SessionLocal()

    try:
        teams = db.query(Team).all()

        if not teams:
            print("\n⚠️  No teams registered yet")
            print("\nRegister your first team:")
            print("  python3 scripts/register_team.py")
            return

        for team in teams:
            members = db.query(TeamMember).filter(TeamMember.team_id == team.team_id).all()
            score = db.query(TeamScore).filter(TeamScore.team_id == team.team_id).first()

            print(f"\n📊 Team: {team.team_name}")
            print(f"   ID: {team.team_id}")
            print(f"   Members: {len(members)}")
            if members:
                for m in members:
                    print(f"     - {m.developer_id}")
            if score:
                print(f"   CAQI Score: {score.overall_caqi:.0f}/500")
                print(f"   Dimensions: S={score.security} C={score.complexity} D={score.documentation} T={score.testing} Dep={score.dependencies} M={score.maintainability}")

        print("\n" + "="*70)
        print(f"Total teams: {len(teams)}")
        print("="*70 + "\n")

    finally:
        db.close()


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Register teams for CAQI Enhanced team analytics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/register_team.py              # Interactive registration
  python3 scripts/register_team.py --sample     # Register sample teams
  python3 scripts/register_team.py --env prod   # Production teams
  python3 scripts/register_team.py --verify     # List all teams
        """
    )

    parser.add_argument(
        "--env",
        choices=["development", "staging", "production"],
        default="development",
        help="Environment for registration (default: development)"
    )
    parser.add_argument(
        "--sample",
        action="store_true",
        help="Register sample teams (engineering, platform, data)"
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="List all registered teams"
    )

    args = parser.parse_args()

    # Handle verify first
    if args.verify:
        verify_teams()
        return 0

    # Handle sample teams
    if args.sample:
        success = register_sample_teams()
        return 0 if success else 1

    # Handle production
    if args.env == "production":
        success = register_production_teams()
        return 0 if success else 1

    # Interactive mode
    success = register_team_interactive()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
