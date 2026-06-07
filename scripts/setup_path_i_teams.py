#!/usr/bin/env python
"""
Path I.0 Setup Script: Register Teams

Run this ONCE during initial setup to register all teams in your organization.

Usage:
    python scripts/setup_path_i_teams.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.services.team_service import TeamService
from api.db.database import SessionLocal


def setup_teams():
    """Register default teams (customize for your organization)."""

    teams = [
        {
            "team_id": "backend-team",
            "team_name": "Backend Engineering",
            "developers": ["alice@company.com", "bob@company.com", "charlie@company.com"]
        },
        {
            "team_id": "frontend-team",
            "team_name": "Frontend Engineering",
            "developers": ["david@company.com", "eve@company.com"]
        },
        {
            "team_id": "data-team",
            "team_name": "Data Engineering",
            "developers": ["frank@company.com", "grace@company.com", "henry@company.com"]
        }
    ]

    print("🚀 Setting up Path I teams...\n")

    for team_config in teams:
        try:
            team = TeamService.create_team(
                team_id=team_config["team_id"],
                team_name=team_config["team_name"],
                developer_ids=team_config["developers"]
            )
            print(f"✅ {team.team_name:25} ({team.member_count} members)")
        except ValueError as e:
            if "already exists" in str(e):
                print(f"⏭️  {team_config['team_name']:25} (already registered)")
            else:
                print(f"❌ {team_config['team_name']:25} Error: {e}")
                return False
        except Exception as e:
            print(f"❌ {team_config['team_name']:25} Error: {e}")
            return False

    print("\n✅ Team setup complete!")

    # Show summary
    print("\n📊 Registered Teams:")
    teams_list = TeamService.get_all_teams()
    for team in teams_list:
        members = TeamService.get_team_members(team.team_id)
        print(f"  • {team.team_name} (ID: {team.team_id})")
        print(f"    Members: {', '.join([m.developer_id for m in members])}")

    return True


if __name__ == "__main__":
    try:
        success = setup_teams()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        sys.exit(1)
