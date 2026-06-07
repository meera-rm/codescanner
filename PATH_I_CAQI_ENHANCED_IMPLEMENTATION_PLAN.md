# Path I: CAQI Enhanced - Implementation Plan

**Project:** CODEPULSE AI - Path I Enhancement  
**Feature:** Team Dynamics Visualization, Trend Tracking, Radar Charts  
**Status:** Planning  
**Timeline:** 50-70 hours of development  
**Target Completion:** 3-4 weeks  

---

## Executive Summary

Enhance Path I (CAQI) to add team-level analytics and historical trend tracking:

1. **Radar Chart** — Visual representation of 6 CAQI dimensions (Security, Complexity, Documentation, Testing, Dependencies, Maintainability)
2. **Team Comparison** — View different teams' CAQI profiles side-by-side with personality archetypes
3. **Trend Tracking** — Measure CAQI evolution over time (January → February → March)

**Impact:** Engineering leaders can measure team engineering culture and track culture changes over time. Individual developers can see how their team compares to norms.

---

## Architecture Overview

### Current Path I Structure
```
Path I: CAQI
├── Backend: CAQI Scoring Engine
│   └── Calculate 6-dimension score (0-500)
├── Frontend: CAQI Dashboard
│   └── Display individual score gauge
└── Data: CAQI results stored per scan
```

### Enhanced Path I Structure
```
Path I: CAQI Enhanced
├── Backend
│   ├── CAQI Scoring Engine (existing)
│   ├── + TeamAggregationService (new)
│   ├── + TrendService (new)
│   └── + PersonalityMappingService (new)
├── Frontend
│   ├── Individual CAQI Dashboard (existing)
│   ├── + Radar Chart Component (new)
│   ├── + Team Comparison View (new)
│   ├── + Trend Timeline View (new)
│   └── + Team Dashboard (new)
└── Data
    ├── caqi_scores table (enhanced with team_id, timestamp)
    ├── team_scores table (new - aggregated)
    └── caqi_history table (new - time series)
```

---

## Phase Breakdown

### Phase I.0: Setup & Configuration (2-3 hours)

**⚠️ CRITICAL FOR DEPLOYMENT - HANDLE EARLY**

#### 1. Local Development Setup Guide

```bash
# Clone and setup
git clone <repo>
cd codescanner
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install sqlalchemy alembic  # New for migrations

# Database setup
python -c "from api.db.database import Base, engine; Base.metadata.create_all(bind=engine)"

# Run server
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Access: http://localhost:8000/docs
```

**What developers need to know:**
- Redis must be running (for Celery)
- PostgreSQL connection string in .env
- ANTHROPIC_API_KEY set
- Team ID needed for testing

#### 2. Database Migration Script

**Option A: Direct SQL (Simple)**

```sql
-- Run this once to add team features to existing database

-- 1. Add columns to existing caqi_scores table
ALTER TABLE caqi_scores 
ADD COLUMN team_id VARCHAR(255),
ADD COLUMN scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP;

CREATE INDEX idx_caqi_team_scanned ON caqi_scores(team_id, scanned_at);

-- 2. Create team aggregation table
CREATE TABLE team_scores (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL UNIQUE,
    team_name VARCHAR(255),
    
    security_score FLOAT,
    complexity_score FLOAT,
    documentation_score FLOAT,
    testing_score FLOAT,
    dependencies_score FLOAT,
    maintainability_score FLOAT,
    
    overall_caqi INT,
    personality_archetype VARCHAR(50),
    member_count INT,
    
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_team_id (team_id),
    INDEX idx_calculated_at (calculated_at)
);

-- 3. Create history table for trends
CREATE TABLE caqi_history (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    
    security_score FLOAT,
    complexity_score FLOAT,
    documentation_score FLOAT,
    testing_score FLOAT,
    dependencies_score FLOAT,
    maintainability_score FLOAT,
    overall_caqi INT,
    
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_team_recorded (team_id, recorded_at),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- 4. Create team membership table
CREATE TABLE team_members (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    developer_id VARCHAR(255) NOT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_team_member (team_id, developer_id),
    INDEX idx_team_id (team_id),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);
```

**Option B: Alembic Migration (Proper)**

```bash
# Generate migration
alembic revision --autogenerate -m "Add team features to CAQI"

# Review generated migration in alembic/versions/
# Then run:
alembic upgrade head
```

#### 3. Environment Variables (.env Template)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/codepulse
# Or for SQLite (dev only):
# DATABASE_URL=sqlite:///./codepulse.db

# API Server
API_HOST=0.0.0.0
API_PORT=8000

# Celery & Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Claude API
ANTHROPIC_API_KEY=sk-xxx

# Path I (CAQI Team Features)
TEAM_AGGREGATION_CACHE_TTL=3600  # Cache team scores for 1 hour
TREND_HISTORY_DAYS=90             # Keep 90 days of trend history
CAQI_HISTORY_COMPRESSION=true     # Compress historical data monthly

# Logging
LOG_LEVEL=INFO
DEBUG=false
```

#### 4. Team Registration Flow

**How teams get created in the system:**

```python
# api/services/team_service.py

class TeamService:
    """Manage team creation and membership."""
    
    @staticmethod
    def create_team(team_id: str, team_name: str, developer_ids: List[str]) -> TeamScore:
        """
        Create a new team and register developers.
        
        Called once per team during setup.
        
        Example:
            TeamService.create_team(
                team_id="backend-team",
                team_name="Backend Engineering",
                developer_ids=["alice@company.com", "bob@company.com", "charlie@company.com"]
            )
        """
        db = SessionLocal()
        
        # Create team record
        team = TeamScore(
            id=str(uuid.uuid4()),
            team_id=team_id,
            team_name=team_name,
            member_count=len(developer_ids)
        )
        db.add(team)
        db.commit()
        
        # Register team members
        for dev_id in developer_ids:
            member = TeamMember(
                id=str(uuid.uuid4()),
                team_id=team_id,
                developer_id=dev_id
            )
            db.add(member)
        
        db.commit()
        db.close()
        
        return team
```

**One-time setup command:**

```bash
# Run this once to register all teams
python -c "
from api.services.team_service import TeamService

# Backend Team
TeamService.create_team(
    team_id='backend-team',
    team_name='Backend Engineering',
    developer_ids=['alice@company.com', 'bob@company.com', 'charlie@company.com']
)

# Frontend Team
TeamService.create_team(
    team_id='frontend-team',
    team_name='Frontend Engineering',
    developer_ids=['david@company.com', 'eve@company.com']
)

# Data Team
TeamService.create_team(
    team_id='data-team',
    team_name='Data Engineering',
    developer_ids=['frank@company.com', 'grace@company.com', 'henry@company.com']
)

print('Teams registered successfully')
"
```

---

### Phase I.1: Data Layer (8-10 hours)

#### Database Schema Changes

**Enhance existing `caqi_scores` table:**
```sql
-- Add to existing table
ALTER TABLE caqi_scores ADD COLUMN team_id VARCHAR(255);
ALTER TABLE caqi_scores ADD COLUMN scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP;
ALTER TABLE caqi_scores ADD INDEX idx_team_scanned (team_id, scanned_at);
```

**Create new tables:**

```sql
-- Aggregated team scores
CREATE TABLE team_scores (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL UNIQUE,
    team_name VARCHAR(255),
    
    -- Dimensions (0-100 each, then weighted to 0-500)
    security_score FLOAT,
    complexity_score FLOAT,
    documentation_score FLOAT,
    testing_score FLOAT,
    dependencies_score FLOAT,
    maintainability_score FLOAT,
    
    -- Aggregated
    overall_caqi INT,  -- 0-500
    personality_archetype VARCHAR(50),  -- "Reckless Optimist", etc.
    member_count INT,
    
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_team_id (team_id),
    INDEX idx_calculated_at (calculated_at)
);

-- Historical trend data
CREATE TABLE caqi_history (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    
    security_score FLOAT,
    complexity_score FLOAT,
    documentation_score FLOAT,
    testing_score FLOAT,
    dependencies_score FLOAT,
    maintainability_score FLOAT,
    overall_caqi INT,
    
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_team_recorded (team_id, recorded_at),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- Team membership mapping
CREATE TABLE team_members (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    developer_id VARCHAR(255) NOT NULL,
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_team_member (team_id, developer_id),
    INDEX idx_team_id (team_id),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);
```

#### Pydantic Models

```python
# api/models/caqi_models.py

from typing import Optional, Dict, List
from pydantic import BaseModel
from datetime import datetime

class CAQIDimensions(BaseModel):
    """6-dimensional CAQI score breakdown."""
    security: float  # 0-100
    complexity: float
    documentation: float
    testing: float
    dependencies: float
    maintainability: float

class TeamScore(BaseModel):
    """Aggregated team CAQI score."""
    team_id: str
    team_name: str
    dimensions: CAQIDimensions
    overall_caqi: int  # 0-500
    personality_archetype: str
    member_count: int
    calculated_at: datetime

class CAQIHistoryEntry(BaseModel):
    """Point in time for trend tracking."""
    dimensions: CAQIDimensions
    overall_caqi: int
    recorded_at: datetime

class CAQITrend(BaseModel):
    """Historical trend for one team."""
    team_id: str
    history: List[CAQIHistoryEntry]
    trend_direction: str  # "improving", "stable", "declining"
    change_percent: float
```

#### SQLAlchemy ORM Models

```python
# api/db/models.py - ADD TO EXISTING

from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

class TeamScore(Base):
    """Aggregated team CAQI scores."""
    __tablename__ = "team_scores"
    
    id = Column(String(36), primary_key=True)
    team_id = Column(String(255), unique=True, index=True)
    team_name = Column(String(255))
    
    # Dimensions
    security_score = Column(Float)
    complexity_score = Column(Float)
    documentation_score = Column(Float)
    testing_score = Column(Float)
    dependencies_score = Column(Float)
    maintainability_score = Column(Float)
    
    # Aggregated
    overall_caqi = Column(Integer)
    personality_archetype = Column(String(50))
    member_count = Column(Integer)
    
    calculated_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    history = relationship("CAQIHistory", back_populates="team", cascade="all, delete-orphan")
    members = relationship("TeamMember", back_populates="team", cascade="all, delete-orphan")

class CAQIHistory(Base):
    """Historical CAQI scores for trend tracking."""
    __tablename__ = "caqi_history"
    
    id = Column(String(36), primary_key=True)
    team_id = Column(String(255), ForeignKey("team_scores.team_id"), index=True)
    
    security_score = Column(Float)
    complexity_score = Column(Float)
    documentation_score = Column(Float)
    testing_score = Column(Float)
    dependencies_score = Column(Float)
    maintainability_score = Column(Float)
    overall_caqi = Column(Integer)
    
    recorded_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    team = relationship("TeamScore", back_populates="history")

class TeamMember(Base):
    """Team membership mapping."""
    __tablename__ = "team_members"
    
    id = Column(String(36), primary_key=True)
    team_id = Column(String(255), ForeignKey("team_scores.team_id"), index=True)
    developer_id = Column(String(255), index=True)
    added_at = Column(DateTime, default=datetime.utcnow)
    
    team = relationship("TeamScore", back_populates="members")
    
    __table_args__ = (
        UniqueConstraint("team_id", "developer_id", name="unique_team_member"),
    )
```

---

### Phase I.2: Backend Services (15-20 hours)

#### TeamAggregationService

```python
# api/services/team_aggregation_service.py

from typing import List, Dict
from sqlalchemy.orm import Session
from api.db.models import CAQIScore, TeamScore, CAQIDimensions
from api.models.caqi_models import TeamScore as TeamScoreModel
from datetime import datetime
import uuid

class TeamAggregationService:
    """Aggregate individual CAQI scores into team-level metrics."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def aggregate_team_scores(self, team_id: str) -> TeamScoreModel:
        """
        Calculate team CAQI by averaging member scores.
        
        Logic:
        1. Get all developers in team
        2. Get latest CAQI score for each developer
        3. Average dimensions across team
        4. Map to personality archetype
        5. Store in team_scores table
        """
        
        # Get team members
        team_members = self.db.query(TeamMember).filter(
            TeamMember.team_id == team_id
        ).all()
        
        if not team_members:
            return None
        
        # Get latest score for each member
        member_scores = []
        for member in team_members:
            latest = self.db.query(CAQIScore).filter(
                CAQIScore.developer_id == member.developer_id
            ).order_by(CAQIScore.scanned_at.desc()).first()
            
            if latest:
                member_scores.append(latest)
        
        # Average dimensions
        dimensions = self._average_dimensions(member_scores)
        
        # Calculate overall CAQI
        overall = self._calculate_overall_caqi(dimensions)
        
        # Map to archetype
        archetype = self._map_to_archetype(dimensions)
        
        # Store result
        team_score = TeamScore(
            id=str(uuid.uuid4()),
            team_id=team_id,
            security_score=dimensions.security,
            complexity_score=dimensions.complexity,
            documentation_score=dimensions.documentation,
            testing_score=dimensions.testing,
            dependencies_score=dimensions.dependencies,
            maintainability_score=dimensions.maintainability,
            overall_caqi=overall,
            personality_archetype=archetype,
            member_count=len(member_scores),
            calculated_at=datetime.utcnow()
        )
        
        self.db.add(team_score)
        self.db.commit()
        
        return self._to_model(team_score)
    
    def _average_dimensions(self, scores: List) -> Dict[str, float]:
        """Average dimension scores across team members."""
        if not scores:
            return {}
        
        dimensions = ["security", "complexity", "documentation", "testing", "dependencies", "maintainability"]
        averages = {}
        
        for dim in dimensions:
            values = [getattr(score, f"{dim}_score", 0) for score in scores]
            averages[dim] = sum(values) / len(values)
        
        return averages
    
    def _calculate_overall_caqi(self, dimensions: Dict) -> int:
        """Convert 6 dimensions (0-100 each) to 0-500 scale."""
        # Weighted average: each dimension worth up to 500/6 ≈ 83.3 points
        weights = {
            "security": 0.25,        # 25% weight
            "complexity": 0.20,      # 20% weight
            "documentation": 0.15,   # 15% weight
            "testing": 0.20,         # 20% weight
            "dependencies": 0.10,    # 10% weight
            "maintainability": 0.10  # 10% weight
        }
        
        overall = sum(
            dimensions.get(dim, 0) * (weights[dim] / 100) * 500
            for dim in weights
        )
        
        return int(overall)
    
    def _map_to_archetype(self, dimensions: Dict) -> str:
        """Map dimension profile to personality archetype."""
        
        # Scoring logic based on dimension patterns
        complexity = dimensions.get("complexity", 50)
        documentation = dimensions.get("documentation", 50)
        testing = dimensions.get("testing", 50)
        dependencies = dimensions.get("dependencies", 50)
        
        # Reckless Optimist: Low complexity, low docs, low testing, risky
        if complexity < 40 and documentation < 40 and testing < 40:
            return "Reckless Optimist"
        
        # Cautious Perfectionist: High docs, high testing, low risk
        elif documentation > 70 and testing > 70 and dependencies < 40:
            return "Cautious Perfectionist"
        
        # Anxious Overthinker: High testing, high dependencies, complex
        elif testing > 70 and dependencies > 70:
            return "Anxious Overthinker"
        
        # Secretive Perfectionist: High quality but less communication
        elif testing > 70 and documentation < 50:
            return "Secretive Perfectionist"
        
        # Default: Balanced team
        else:
            return "Pragmatic Engineer"
    
    def _to_model(self, db_obj) -> TeamScoreModel:
        """Convert ORM object to Pydantic model."""
        return TeamScoreModel(
            team_id=db_obj.team_id,
            team_name=db_obj.team_name,
            dimensions={
                "security": db_obj.security_score,
                "complexity": db_obj.complexity_score,
                "documentation": db_obj.documentation_score,
                "testing": db_obj.testing_score,
                "dependencies": db_obj.dependencies_score,
                "maintainability": db_obj.maintainability_score,
            },
            overall_caqi=db_obj.overall_caqi,
            personality_archetype=db_obj.personality_archetype,
            member_count=db_obj.member_count,
            calculated_at=db_obj.calculated_at
        )
```

#### TrendService

```python
# api/services/trend_service.py

from typing import List, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from api.db.models import CAQIHistory, TeamScore
from api.models.caqi_models import CAQITrend, CAQIHistoryEntry
import uuid

class TrendService:
    """Track CAQI trends over time."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def record_team_snapshot(self, team_id: str, dimensions: Dict, overall: int) -> None:
        """
        Record a point-in-time snapshot of team CAQI for trend tracking.
        Called after each team aggregation.
        """
        
        history_entry = CAQIHistory(
            id=str(uuid.uuid4()),
            team_id=team_id,
            security_score=dimensions["security"],
            complexity_score=dimensions["complexity"],
            documentation_score=dimensions["documentation"],
            testing_score=dimensions["testing"],
            dependencies_score=dimensions["dependencies"],
            maintainability_score=dimensions["maintainability"],
            overall_caqi=overall,
            recorded_at=datetime.utcnow()
        )
        
        self.db.add(history_entry)
        self.db.commit()
    
    def get_trend(self, team_id: str, days: int = 90) -> CAQITrend:
        """
        Get historical trend for a team over N days.
        
        Args:
            team_id: Team identifier
            days: How many days back to look (default 90)
        
        Returns:
            CAQITrend with history entries and trend direction
        """
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        history = self.db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= cutoff_date
        ).order_by(CAQIHistory.recorded_at.asc()).all()
        
        if not history:
            return None
        
        # Convert to models
        entries = [
            CAQIHistoryEntry(
                dimensions={
                    "security": h.security_score,
                    "complexity": h.complexity_score,
                    "documentation": h.documentation_score,
                    "testing": h.testing_score,
                    "dependencies": h.dependencies_score,
                    "maintainability": h.maintainability_score,
                },
                overall_caqi=h.overall_caqi,
                recorded_at=h.recorded_at
            )
            for h in history
        ]
        
        # Calculate trend
        trend_direction, change_percent = self._calculate_trend(history)
        
        return CAQITrend(
            team_id=team_id,
            history=entries,
            trend_direction=trend_direction,
            change_percent=change_percent
        )
    
    def _calculate_trend(self, history: List) -> Tuple[str, float]:
        """Determine if trend is improving, stable, or declining."""
        
        if len(history) < 2:
            return "stable", 0.0
        
        first_score = history[0].overall_caqi
        last_score = history[-1].overall_caqi
        
        change = last_score - first_score
        change_percent = (change / first_score * 100) if first_score > 0 else 0
        
        if change_percent > 5:
            trend = "improving"
        elif change_percent < -5:
            trend = "declining"
        else:
            trend = "stable"
        
        return trend, change_percent
    
    def get_monthly_snapshot(self, team_id: str, year: int, month: int) -> CAQIHistoryEntry:
        """Get snapshot for a specific month (e.g., January 2026)."""
        
        from_date = datetime(year, month, 1)
        to_date = datetime(year, month + 1, 1) if month < 12 else datetime(year + 1, 1, 1)
        
        # Get latest score in that month
        entry = self.db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= from_date,
            CAQIHistory.recorded_at < to_date
        ).order_by(CAQIHistory.recorded_at.desc()).first()
        
        if not entry:
            return None
        
        return CAQIHistoryEntry(
            dimensions={
                "security": entry.security_score,
                "complexity": entry.complexity_score,
                "documentation": entry.documentation_score,
                "testing": entry.testing_score,
                "dependencies": entry.dependencies_score,
                "maintainability": entry.maintainability_score,
            },
            overall_caqi=entry.overall_caqi,
            recorded_at=entry.recorded_at
        )
```

#### PersonalityMappingService

```python
# api/services/personality_mapping_service.py

from typing import Dict

class PersonalityMappingService:
    """Map CAQI dimensions to personality archetypes."""
    
    ARCHETYPES = {
        "Reckless Optimist": {
            "description": "Ships fast, refines later. Low process overhead, high velocity.",
            "characteristics": [
                "Minimal documentation",
                "Limited test coverage",
                "Quick iteration cycles",
                "Low dependency awareness"
            ],
            "dimension_profile": {
                "documentation": "low",
                "testing": "low",
                "complexity": "low",
                "dependencies": "variable"
            }
        },
        "Cautious Perfectionist": {
            "description": "High quality, thorough process. Everything documented and tested.",
            "characteristics": [
                "Comprehensive documentation",
                "High test coverage",
                "Careful change management",
                "Low complexity through decomposition"
            ],
            "dimension_profile": {
                "documentation": "high",
                "testing": "high",
                "complexity": "low",
                "dependencies": "low"
            }
        },
        "Secretive Perfectionist": {
            "description": "High quality code, poor communication. Great code, hard to understand.",
            "characteristics": [
                "Minimal documentation",
                "High test coverage",
                "Complex implementations",
                "Works in isolation"
            ],
            "dimension_profile": {
                "documentation": "low",
                "testing": "high",
                "complexity": "high",
                "dependencies": "variable"
            }
        },
        "Anxious Overthinker": {
            "description": "Manages every risk. Highly defensive coding practices.",
            "characteristics": [
                "Comprehensive documentation",
                "Very high test coverage",
                "Dependency management obsession",
                "Complex defensive code"
            ],
            "dimension_profile": {
                "documentation": "high",
                "testing": "high",
                "dependencies": "high",
                "complexity": "high"
            }
        },
        "Pragmatic Engineer": {
            "description": "Balanced approach. Makes trade-offs based on context.",
            "characteristics": [
                "Reasonable documentation",
                "Good test coverage",
                "Managed complexity",
                "Thoughtful dependency choices"
            ],
            "dimension_profile": {
                "documentation": "medium",
                "testing": "medium",
                "complexity": "medium",
                "dependencies": "medium"
            }
        }
    }
    
    def get_archetype_profile(self, archetype: str) -> Dict:
        """Get detailed profile for an archetype."""
        return self.ARCHETYPES.get(archetype, self.ARCHETYPES["Pragmatic Engineer"])
    
    def get_archetype_description(self, archetype: str) -> str:
        """Get human-readable description of archetype."""
        profile = self.get_archetype_profile(archetype)
        return profile["description"]
    
    def suggest_improvements(self, archetype: str, current_dimensions: Dict) -> List[str]:
        """Suggest improvements based on archetype profile."""
        
        suggestions = []
        
        if archetype == "Reckless Optimist":
            suggestions.extend([
                "Increase test coverage to reduce risk",
                "Document critical paths and APIs",
                "Implement code review process"
            ])
        elif archetype == "Secretive Perfectionist":
            suggestions.extend([
                "Improve code documentation",
                "Add code review and pair programming",
                "Simplify complex implementations"
            ])
        elif archetype == "Anxious Overthinker":
            suggestions.extend([
                "Prioritize high-impact dependencies",
                "Simplify testing to focus on critical paths",
                "Balance perfection with velocity"
            ])
        
        return suggestions
```

---

### Phase I.3: API Endpoints (10-12 hours)

```python
# api/routes/caqi_enhanced.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.db.database import get_db
from api.services.team_aggregation_service import TeamAggregationService
from api.services.trend_service import TrendService
from api.services.personality_mapping_service import PersonalityMappingService
from api.models.caqi_models import TeamScore, CAQITrend
from typing import List, Optional

router = APIRouter(prefix="/api/v1/caqi", tags=["caqi"])

# ===== TEAM ENDPOINTS =====

@router.get("/team/{team_id}")
async def get_team_caqi(
    team_id: str,
    db: Session = Depends(get_db)
) -> TeamScore:
    """Get current CAQI score for a team."""
    service = TeamAggregationService(db)
    result = service.aggregate_team_scores(team_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Team not found")
    
    return result

@router.get("/team/{team_id}/comparison")
async def compare_teams(
    team_ids: str,  # Comma-separated: team1,team2,team3
    db: Session = Depends(get_db)
) -> List[TeamScore]:
    """Compare CAQI scores across multiple teams."""
    service = TeamAggregationService(db)
    teams = team_ids.split(",")
    
    results = []
    for team_id in teams:
        result = service.aggregate_team_scores(team_id)
        if result:
            results.append(result)
    
    return results

# ===== TREND ENDPOINTS =====

@router.get("/team/{team_id}/trend")
async def get_team_trend(
    team_id: str,
    days: int = 90,
    db: Session = Depends(get_db)
) -> CAQITrend:
    """Get historical trend for a team (90 days by default)."""
    service = TrendService(db)
    trend = service.get_trend(team_id, days)
    
    if not trend:
        raise HTTPException(status_code=404, detail="No trend data found")
    
    return trend

@router.get("/team/{team_id}/monthly/{year}/{month}")
async def get_monthly_snapshot(
    team_id: str,
    year: int,
    month: int,
    db: Session = Depends(get_db)
):
    """Get CAQI snapshot for a specific month (e.g., January 2026)."""
    service = TrendService(db)
    snapshot = service.get_monthly_snapshot(team_id, year, month)
    
    if not snapshot:
        raise HTTPException(
            status_code=404,
            detail=f"No data for {year}-{month:02d}"
        )
    
    return snapshot

# ===== PERSONALITY ENDPOINTS =====

@router.get("/archetype/{archetype}")
async def get_archetype_profile(archetype: str):
    """Get personality archetype profile and improvement suggestions."""
    service = PersonalityMappingService()
    profile = service.get_archetype_profile(archetype)
    
    if not profile:
        raise HTTPException(status_code=404, detail="Unknown archetype")
    
    return profile

@router.get("/team/{team_id}/suggestions")
async def get_improvement_suggestions(
    team_id: str,
    db: Session = Depends(get_db)
) -> List[str]:
    """Get improvement suggestions based on team's archetype."""
    agg_service = TeamAggregationService(db)
    pers_service = PersonalityMappingService()
    
    team_score = agg_service.aggregate_team_scores(team_id)
    if not team_score:
        raise HTTPException(status_code=404, detail="Team not found")
    
    suggestions = pers_service.suggest_improvements(
        team_score.personality_archetype,
        team_score.dimensions
    )
    
    return suggestions
```

---

### Phase I.4: Frontend Components (20-25 hours)

#### Radar Chart Component

```jsx
// frontend/src/components/RadarChart.tsx

import React from 'react';
import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, 
         ResponsiveContainer, Legend, Tooltip } from 'recharts';

interface RadarChartProps {
  data: {
    security: number;
    complexity: number;
    documentation: number;
    testing: number;
    dependencies: number;
    maintainability: number;
  };
  teamName: string;
  archetype: string;
}

export const CAQIRadarChart: React.FC<RadarChartProps> = ({ data, teamName, archetype }) => {
  const chartData = [
    { dimension: 'Security', value: data.security },
    { dimension: 'Complexity', value: data.complexity },
    { dimension: 'Documentation', value: data.documentation },
    { dimension: 'Testing', value: data.testing },
    { dimension: 'Dependencies', value: data.dependencies },
    { dimension: 'Maintainability', value: data.maintainability },
  ];

  return (
    <div className="radar-container">
      <h2>{teamName}</h2>
      <p className="archetype">{archetype}</p>
      
      <ResponsiveContainer width="100%" height={400}>
        <RadarChart data={chartData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="dimension" />
          <PolarRadiusAxis angle={90} domain={[0, 100]} />
          <Radar 
            name="Score" 
            dataKey="value" 
            stroke="#8884d8" 
            fill="#8884d8" 
            fillOpacity={0.6} 
          />
          <Legend />
          <Tooltip />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
};
```

#### Team Comparison Component

```jsx
// frontend/src/components/TeamComparison.tsx

import React, { useState } from 'react';
import { CAQIRadarChart } from './RadarChart';

interface Team {
  team_id: string;
  team_name: string;
  dimensions: {
    security: number;
    complexity: number;
    documentation: number;
    testing: number;
    dependencies: number;
    maintainability: number;
  };
  personality_archetype: string;
  member_count: number;
}

export const TeamComparison: React.FC<{ teams: Team[] }> = ({ teams }) => {
  return (
    <div className="team-comparison">
      <h1>Team Comparison</h1>
      
      <div className="teams-grid">
        {teams.map((team) => (
          <div key={team.team_id} className="team-card">
            <CAQIRadarChart 
              data={team.dimensions}
              teamName={team.team_name}
              archetype={team.personality_archetype}
            />
            <div className="team-stats">
              <p>Members: {team.member_count}</p>
              <p>Overall CAQI: {team.overall_caqi}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

#### Trend Timeline Component

```jsx
// frontend/src/components/TrendTimeline.tsx

import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, 
         Legend, ResponsiveContainer } from 'recharts';

interface TrendData {
  month: string;
  caqi: number;
  archetype: string;
}

export const TrendTimeline: React.FC<{ teamName: string; data: TrendData[] }> = ({ teamName, data }) => {
  return (
    <div className="trend-container">
      <h2>{teamName} - 3-Month Trend</h2>
      
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data}>
          <CartesianGrid />
          <XAxis dataKey="month" />
          <YAxis domain={[0, 500]} />
          <Tooltip 
            formatter={(value) => `CAQI: ${value}`}
            labelFormatter={(label) => `${label}`}
          />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="caqi" 
            stroke="#82ca9d" 
            dot={{ fill: '#82ca9d', r: 6 }}
          />
        </LineChart>
      </ResponsiveContainer>
      
      <div className="trend-summary">
        <div className="trend-item">
          <h4>January</h4>
          <p className="archetype">{data[0]?.archetype}</p>
          <p className="score">{data[0]?.caqi}</p>
        </div>
        <div className="trend-item">
          <h4>February</h4>
          <p className="archetype">{data[1]?.archetype}</p>
          <p className="score">{data[1]?.caqi}</p>
        </div>
        <div className="trend-item">
          <h4>March</h4>
          <p className="archetype">{data[2]?.archetype}</p>
          <p className="score">{data[2]?.caqi}</p>
        </div>
      </div>
    </div>
  );
};
```

#### Dashboard Integration

```jsx
// frontend/src/pages/CAQIDashboard.tsx

import React, { useState, useEffect } from 'react';
import { CAQIRadarChart } from '../components/RadarChart';
import { TeamComparison } from '../components/TeamComparison';
import { TrendTimeline } from '../components/TrendTimeline';

export const CAQIDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState('radar');
  const [teams, setTeams] = useState([]);
  const [trends, setTrends] = useState({});

  useEffect(() => {
    // Fetch team comparison data
    fetch('/api/v1/caqi/team/backend-team,frontend-team,data-team/comparison')
      .then(r => r.json())
      .then(setTeams);

    // Fetch trends
    fetch('/api/v1/caqi/team/backend-team/trend')
      .then(r => r.json())
      .then(trend => setTrends(prev => ({ ...prev, 'backend-team': trend })));
  }, []);

  return (
    <div className="caqi-dashboard">
      <h1>Engineering Culture Dashboard</h1>
      
      <div className="tabs">
        <button 
          className={activeTab === 'radar' ? 'active' : ''}
          onClick={() => setActiveTab('radar')}
        >
          Team Comparison
        </button>
        <button 
          className={activeTab === 'trend' ? 'active' : ''}
          onClick={() => setActiveTab('trend')}
        >
          Trends Over Time
        </button>
      </div>

      {activeTab === 'radar' && <TeamComparison teams={teams} />}
      {activeTab === 'trend' && <TrendTimeline teamName="Backend Team" data={trends['backend-team']?.history || []} />}
    </div>
  );
};
```

---

### Phase I.5: Testing (8-10 hours)

#### Unit Tests

```python
# tests/test_team_aggregation.py

import pytest
from api.services.team_aggregation_service import TeamAggregationService
from api.db.models import CAQIScore, TeamMember
from datetime import datetime

@pytest.mark.asyncio
async def test_team_aggregation_averages_scores(db):
    """Test that team scores are correctly averaged from members."""
    service = TeamAggregationService(db)
    
    # Create test data
    members = ["dev1", "dev2", "dev3"]
    for dev in members:
        db.add(TeamMember(team_id="test-team", developer_id=dev))
    
    # Add CAQI scores
    scores = [
        CAQIScore(developer_id="dev1", security_score=80, complexity_score=70, ...),
        CAQIScore(developer_id="dev2", security_score=90, complexity_score=80, ...),
        CAQIScore(developer_id="dev3", security_score=70, complexity_score=60, ...),
    ]
    for score in scores:
        db.add(score)
    db.commit()
    
    # Aggregate
    result = service.aggregate_team_scores("test-team")
    
    # Verify average
    assert result.dimensions.security == 80  # (80 + 90 + 70) / 3
    assert result.dimensions.complexity == 70  # (70 + 80 + 60) / 3

@pytest.mark.asyncio
async def test_archetype_mapping():
    """Test personality archetype mapping."""
    service = TeamAggregationService(None)
    
    dimensions = {
        "security": 30,
        "complexity": 30,
        "documentation": 30,
        "testing": 30,
        "dependencies": 50,
        "maintainability": 40
    }
    
    archetype = service._map_to_archetype(dimensions)
    assert archetype == "Reckless Optimist"
```

#### Integration Tests

```python
# tests/test_caqi_api.py

def test_get_team_caqi(client, db):
    """Test GET /api/v1/caqi/team/{team_id}"""
    response = client.get("/api/v1/caqi/team/backend-team")
    assert response.status_code == 200
    data = response.json()
    assert "dimensions" in data
    assert "personality_archetype" in data

def test_compare_teams(client, db):
    """Test comparing multiple teams."""
    response = client.get("/api/v1/caqi/team/backend-team/comparison?team_ids=backend-team,frontend-team")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2

def test_get_trend(client, db):
    """Test trend retrieval."""
    response = client.get("/api/v1/caqi/team/backend-team/trend?days=90")
    assert response.status_code == 200
    data = response.json()
    assert "history" in data
    assert "trend_direction" in data
```

#### Frontend Tests

```jsx
// frontend/src/__tests__/RadarChart.test.tsx

import { render, screen } from '@testing-library/react';
import { CAQIRadarChart } from '../components/RadarChart';

test('renders radar chart with team name', () => {
  const data = {
    security: 80,
    complexity: 70,
    documentation: 75,
    testing: 85,
    dependencies: 60,
    maintainability: 80,
  };

  render(
    <CAQIRadarChart 
      data={data} 
      teamName="Backend Team" 
      archetype="Pragmatic Engineer"
    />
  );

  expect(screen.getByText('Backend Team')).toBeInTheDocument();
  expect(screen.getByText('Pragmatic Engineer')).toBeInTheDocument();
});
```

---

## Implementation Timeline

### Week 1: Data Layer & Core Services (15-17 hours)
- **Day 1-2:** Database schema (migrations, ORM models)
- **Day 3-4:** TeamAggregationService implementation
- **Day 5:** TrendService implementation

### Week 2: API & Services (15-18 hours)
- **Day 1-2:** PersonalityMappingService
- **Day 3-4:** REST API endpoints (6 new endpoints)
- **Day 5:** Integration tests

### Week 3: Frontend & Polish (20-25 hours)
- **Day 1-2:** RadarChart component
- **Day 2-3:** TeamComparison component
- **Day 3-4:** TrendTimeline component
- **Day 5:** Dashboard integration & styling

### Week 4: Testing & Deployment (5-10 hours)
- **Day 1:** Unit tests
- **Day 2-3:** End-to-end tests
- **Day 4-5:** Performance optimization, deployment

---

## Effort Breakdown

| Component | Hours | Status |
|-----------|-------|--------|
| Data Layer | 8-10 | 🔄 |
| Backend Services | 15-20 | 🔄 |
| API Endpoints | 10-12 | 🔄 |
| Frontend Components | 20-25 | 🔄 |
| Testing | 8-10 | 🔄 |
| **Total** | **50-70** | 🔄 |

---

## Success Criteria

### Functional
- ✅ Radar chart displays 6 CAQI dimensions correctly
- ✅ Team comparison shows side-by-side profiles
- ✅ Trend timeline accurately tracks 90-day history
- ✅ Personality archetype mapping works correctly
- ✅ All 6 API endpoints functional

### Performance
- ✅ Dashboard loads in < 2 seconds
- ✅ API responses < 100ms
- ✅ Radar chart renders smoothly (60 FPS)

### Quality
- ✅ 85%+ code coverage on services
- ✅ All integration tests passing
- ✅ Frontend component tests passing
- ✅ Zero console errors/warnings

---

## Architecture Decisions

### Why Aggregate at Service Layer?
**Decision:** Calculate team CAQI from individual scores in `TeamAggregationService`, not in database views.

**Rationale:**
- Easier to test (no complex SQL)
- Easier to modify averaging logic
- Better performance (queries N individual scores, compute once)
- Flexible for future weighting schemes

### Why Store Historical Data Separately?
**Decision:** `CAQIHistory` table separate from `TeamScore`.

**Rationale:**
- Allows efficient time-series queries
- Keeps current state lightweight
- Easy to add compression/archival policies
- Better query patterns (range scans by date)

### Why Map to Archetypes?
**Decision:** Personality archetypes are deterministic from dimension profile.

**Rationale:**
- Easy for leaders to understand
- Provides immediately actionable insights
- Differentiates this from raw numbers
- Can improve mapping logic over time

---

## Future Enhancements

### Phase I+1: Advanced Analytics (20-30 hours)
- Anomaly detection (when team CAQI suddenly drops)
- Peer comparison (how does your team compare to industry average?)
- Drill-down to individual developers
- Automated alerts when trend reverses

### Phase I+2: Culture Interventions (15-20 hours)
- Suggest specific improvements per archetype
- Track team's response to interventions
- A/B test culture changes (branch vs. main)
- Gamification (score badges, leaderboards)

### Phase I+3: Export & Reporting (10-15 hours)
- Export trend reports (PDF, CSV)
- Email weekly/monthly digests
- Slack notifications on culture changes
- Executive dashboard view

---

## Implementation Notes

### Database Indexes
```sql
CREATE INDEX idx_caqi_history_team_date ON caqi_history(team_id, recorded_at);
CREATE INDEX idx_team_scores_archetype ON team_scores(personality_archetype);
CREATE INDEX idx_team_members_team ON team_members(team_id);
```

### Caching Strategy
```python
# Cache team aggregation for 1 hour
@cache.cached(timeout=3600, key_prefix="team_caqi_")
def aggregate_team_scores(team_id):
    ...

# Invalidate on new scan
def record_caqi_score(score):
    cache.delete(f"team_caqi_{score.team_id}")
    ...
```

### Data Retention
- Keep individual CAQI scores: 2 years
- Keep aggregated team scores: 3 years
- Keep historical snapshots: indefinitely (compress monthly)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Slow trend queries on large datasets | High | Add indexes, implement data compression |
| Archetype mapping too rigid | Medium | Add admin panel to customize mapping |
| Team membership changes not tracked | Medium | Add audit log, snapshot membership at aggregation time |
| Frontend performance with many teams | Medium | Pagination, lazy loading, memoization |

---

## Go/No-Go Criteria

**GO Conditions:**
- ✅ All unit tests passing
- ✅ All integration tests passing
- ✅ Dashboard loads < 2s
- ✅ Zero critical bugs
- ✅ Documentation complete

**NO-GO Triggers:**
- Slow queries (> 500ms)
- Data inconsistency issues
- UI rendering bugs (radar chart broken)
- Test coverage < 80%

---

---

## ⚠️ DEPLOYMENT CHECKLIST (CRITICAL - DO NOT SKIP)

**These items from Phase I.0 MUST be handled when deploying to production.**

### Pre-Deployment (Week Before Go-Live)

- [ ] **Database Migration Script Tested**
  - [ ] Migration script tested on staging database
  - [ ] Rollback procedure documented
  - [ ] Backup taken before running migration
  - [ ] All tables created successfully
  - [ ] Indexes created and verified

- [ ] **Environment Variables Configured**
  - [ ] DATABASE_URL points to production database
  - [ ] ANTHROPIC_API_KEY set and verified
  - [ ] Redis connection tested (CELERY_BROKER_URL)
  - [ ] TEAM_AGGREGATION_CACHE_TTL set appropriately
  - [ ] LOG_LEVEL set to INFO (not DEBUG)
  - [ ] All .env variables reviewed for security

- [ ] **Teams Registered in Production**
  - [ ] All teams created via TeamService.create_team()
  - [ ] Team IDs match your organization structure
  - [ ] All developer IDs added correctly
  - [ ] Verify: SELECT * FROM team_scores (should see all teams)

- [ ] **Local Development Setup Verified**
  - [ ] Developers can run local setup guide without errors
  - [ ] Test database works
  - [ ] API docs accessible at /docs
  - [ ] All endpoints responding

### Deployment Day

- [ ] **Run Database Migration**
  ```bash
  python -c "from api.db.database import Base, engine; Base.metadata.create_all(bind=engine)"
  # OR
  alembic upgrade head
  ```

- [ ] **Verify Team Data**
  ```sql
  SELECT team_id, team_name, member_count FROM team_scores;
  -- Should see all teams
  ```

- [ ] **Test APIs in Production**
  ```bash
  curl https://api.codepulse.ai/api/v1/caqi/team/backend-team
  # Should return 200 with team data
  ```

- [ ] **Check Logs**
  - [ ] No errors in application logs
  - [ ] No database connection errors
  - [ ] Trend snapshots recording successfully

### Post-Deployment (First Week)

- [ ] **Monitor for Errors**
  - [ ] Set up alerting on API endpoints
  - [ ] Monitor database query performance
  - [ ] Check trend recording (runs daily)
  - [ ] Verify caching works (response times should drop after first call)

- [ ] **Validate Data Quality**
  - [ ] Team aggregation scores are reasonable (0-500 range)
  - [ ] Archetype mappings make sense
  - [ ] Historical snapshots recording daily
  - [ ] No orphaned records in caqi_history

- [ ] **Team Onboarding**
  - [ ] Teams know how to access dashboards
  - [ ] Teams understand personality archetypes
  - [ ] Teams can interpret radar charts
  - [ ] Support channel set up for questions

---

## 🧠 MENTAL NOTES FOR CLAUDE (DEPLOYMENT PHASE)

**When deploying Path I enhancements, remember:**

1. **Database Schema MUST Exist**
   - Phase I.0 migration script must run FIRST
   - Cannot proceed without team_scores, caqi_history, team_members tables
   - Test on staging before production

2. **Teams Must Be Registered**
   - Every team needs an entry in team_scores
   - Every developer needs entry in team_members
   - Use TeamService.create_team() one-time setup
   - Don't skip this step—APIs will 404 without teams

3. **Environment Variables CRITICAL**
   - DATABASE_URL must be set (points to right database)
   - ANTHROPIC_API_KEY needed for AI suggestions
   - Redis must be running (CELERY_BROKER_URL)
   - TEAM_AGGREGATION_CACHE_TTL should match your aggregation schedule

4. **Three Tables, Three Purposes**
   - `team_scores` — Current team CAQI (updated when TeamAggregationService runs)
   - `caqi_history` — Time-series data (one entry per day per team)
   - `team_members` — Team membership (static, set during registration)

5. **Daily Background Job Needed**
   - Trend snapshots recorded daily (add to Celery scheduler)
   - Without this, trend tracking won't work
   - Set up: daily aggregation + snapshot to caqi_history

6. **Monitoring Points**
   - API response time (should be < 100ms)
   - Team aggregation time (should be < 5s per team)
   - Database query time (< 50ms)
   - Alert if trends not updated for > 24 hours

7. **Rollback Plan**
   - Keep database backup before migration
   - If migration fails: restore from backup
   - If APIs fail: check environment variables first
   - If trends not recording: check Celery worker logs

**When Claude is asked to help with Path I deployment, check this list first.**

---

**Implementation Ready ✅**

Estimated start: 1 week (after Phase 3.5 stabilization complete)  
Estimated completion: 4 weeks (1 day setup + 3 weeks development)  
Team size: 1-2 developers  

**⚠️ Critical Path:** Phase I.0 (setup) → Phase I.1 (data) → Phase I.2 (services) → Phase I.3 (API) → Phase I.4 (frontend) → Phase I.5 (testing) → **DEPLOYMENT CHECKLIST**

