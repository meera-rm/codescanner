# Phase I+2: Culture Interventions - Implementation Plan

**Project:** CODEPULSE AI - Path I Culture Interventions  
**Feature:** Actionable Suggestions, Intervention Tracking, A/B Testing, Gamification  
**Status:** Planning  
**Timeline:** 15-20 hours of development  
**Target Completion:** 2-3 weeks (after Phase I+1 deployment)  
**Dependencies:** Phase I.0-I.5 + Phase I+1 (Advanced Analytics) complete and deployed

---

## Executive Summary

Transform Path I from **monitoring** (what's happening) to **improvement** (how to fix it):

1. **Smart Suggestions** — Archetype-specific recommendations to improve each dimension
2. **Intervention Tracking** — Record what changes teams make and measure impact
3. **A/B Testing** — Compare culture improvements across branches before merging
4. **Gamification** — Badges, leaderboards, streaks to motivate teams

**Impact:** Teams go from "we have a problem" to "here's exactly what to do" to "we did it and it worked."

---

## Architecture Overview

### Current Path I+1 Structure (Post-Advanced Analytics)
```
Path I+1: Advanced Analytics (Deployed)
├── Anomaly Detection ✅
├── Peer Comparison ✅
├── Developer Drill-Down ✅
└── Alerting ✅
```

### Phase I+2 Enhanced Structure
```
Path I+2: Culture Interventions (New)
├── Backend Services
│   ├── SuggestionEngineService (new)
│   │   ├── Archetype-specific rules
│   │   ├── Dimension-specific fixes
│   │   └── Impact estimation
│   ├── InterventionTrackingService (new)
│   │   ├── Record team actions
│   │   ├── Track implementation status
│   │   └── Measure outcomes
│   ├── ABTestingService (new)
│   │   ├── Setup test/control branches
│   │   ├── Compare CAQI trends
│   │   └── Statistical significance
│   └── GamificationService (new)
│       ├── Award badges
│       ├── Track streaks
│       └── Leaderboard ranking
├── REST API (6 new endpoints)
│   ├── /api/v1/caqi/suggestions/{team_id}
│   ├── /api/v1/caqi/interventions
│   ├── /api/v1/caqi/ab-tests
│   ├── /api/v1/caqi/gamification/badges
│   ├── /api/v1/caqi/gamification/leaderboard
│   └── /api/v1/caqi/gamification/streaks
├── Frontend Components (4 new)
│   ├── SuggestionsPanel
│   ├── InterventionTracker
│   ├── ABTestDashboard
│   └── GamificationLeaderboard
└── Data Tables (4 new)
    ├── suggestions
    ├── interventions
    ├── ab_tests
    └── badges
```

---

## Phase Breakdown

### Phase I+2.0: Data & Schema (3 hours)

#### 1. Database Schema Extensions

```sql
-- 1. Suggestions Table
CREATE TABLE suggestions (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    archetype VARCHAR(50) NOT NULL,  -- reckless_optimist, etc.
    
    dimension VARCHAR(50) NOT NULL,  -- security, complexity, etc.
    current_score FLOAT NOT NULL,
    target_score FLOAT NOT NULL,
    
    suggestion_text TEXT NOT NULL,
    implementation_steps TEXT,  -- JSON array
    estimated_effort VARCHAR(20),  -- low, medium, high
    estimated_impact FLOAT,  -- 0-100
    
    priority INT,  -- 1-5 (5 = highest)
    status VARCHAR(20) DEFAULT 'pending',  -- pending, in_progress, completed, dismissed
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    dismissed_at TIMESTAMP,
    dismissed_reason TEXT,
    
    INDEX idx_team_archetype (team_id, archetype),
    INDEX idx_status (status),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- 2. Interventions Table
CREATE TABLE interventions (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    suggestion_id VARCHAR(36),
    
    title VARCHAR(255) NOT NULL,
    description TEXT,
    intervention_type VARCHAR(50),  -- code_review, refactor, testing, documentation, etc.
    
    status VARCHAR(20) DEFAULT 'not_started',  -- not_started, in_progress, completed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    expected_impact_dimension VARCHAR(50),
    expected_impact_points FLOAT,
    actual_impact_dimension VARCHAR(50),
    actual_impact_points FLOAT,
    
    owner_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_team_status (team_id, status),
    INDEX idx_impact (expected_impact_points DESC),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE,
    FOREIGN KEY (suggestion_id) REFERENCES suggestions(id) ON DELETE SET NULL
);

-- 3. A/B Tests Table
CREATE TABLE ab_tests (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    
    test_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    control_branch VARCHAR(255) NOT NULL,
    test_branch VARCHAR(255) NOT NULL,
    
    hypothesis TEXT,
    metric VARCHAR(50),  -- overall_caqi, security, testing, etc.
    
    started_at TIMESTAMP NOT NULL,
    ended_at TIMESTAMP,
    duration_days INT,
    
    control_baseline FLOAT,
    control_final FLOAT,
    
    test_baseline FLOAT,
    test_final FLOAT,
    
    result VARCHAR(20),  -- not_started, in_progress, inconclusive, winner_control, winner_test
    p_value FLOAT,
    
    created_by VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_team_status (team_id, result),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- 4. Badges Table
CREATE TABLE badges (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    badge_name VARCHAR(255) NOT NULL,
    badge_type VARCHAR(50),  -- improvement, streak, collaboration, innovation
    
    description TEXT,
    icon_url VARCHAR(255),
    color VARCHAR(20),
    
    awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    awarded_for VARCHAR(255),  -- "improved security by 20%", "10-day improvement streak"
    
    INDEX idx_team_awarded (team_id, awarded_at DESC),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- 5. Improvement Streaks Table
CREATE TABLE improvement_streaks (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    
    start_date DATE NOT NULL,
    end_date DATE,
    days_in_streak INT DEFAULT 1,
    
    dimension VARCHAR(50),  -- null = overall, else specific dimension
    improvement_threshold FLOAT,  -- min % improvement per day to maintain streak
    
    status VARCHAR(20),  -- active, completed, broken
    
    INDEX idx_team_active (team_id, status),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_suggestions_team_status ON suggestions(team_id, status);
CREATE INDEX idx_interventions_team_date ON interventions(team_id, created_at DESC);
CREATE INDEX idx_ab_tests_team_result ON ab_tests(team_id, result);
CREATE INDEX idx_badges_team_date ON badges(team_id, awarded_at DESC);
CREATE INDEX idx_streaks_team_active ON improvement_streaks(team_id, status);
```

#### 2. Updated ORM Models

```python
# api/models/suggestion.py
class Suggestion(Base):
    __tablename__ = "suggestions"
    
    id = Column(String, primary_key=True)
    team_id = Column(String, ForeignKey("team_scores.team_id", ondelete="CASCADE"), nullable=False)
    archetype = Column(String, nullable=False)
    dimension = Column(String, nullable=False)
    
    current_score = Column(Float, nullable=False)
    target_score = Column(Float, nullable=False)
    
    suggestion_text = Column(String, nullable=False)
    implementation_steps = Column(String)  # JSON
    estimated_effort = Column(String)
    estimated_impact = Column(Float)
    
    priority = Column(Integer)
    status = Column(String, default="pending")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String)
    dismissed_at = Column(DateTime)
    dismissed_reason = Column(String)

# api/models/intervention.py, ab_test.py, badge.py, improvement_streak.py
# (Similar structure)
```

---

### Phase I+2.1: Suggestion Engine Service (4-5 hours)

**File:** `api/services/suggestion_engine.py`

```python
class SuggestionEngineService:
    """Generate archetype-specific suggestions for team improvement."""
    
    # Archetype-specific suggestion templates
    ARCHETYPE_SUGGESTIONS = {
        'reckless_optimist': {
            'security': {
                'template': 'Security is lower than team average. Implement security code reviews.',
                'steps': [
                    'Add security review checklist to PR template',
                    'Assign security champion per sprint',
                    'Run OWASP top 10 training'
                ],
                'effort': 'medium',
                'impact': 25
            },
            'testing': {
                'template': 'Testing coverage is low. Increase test coverage to 80%+.',
                'steps': [
                    'Set minimum coverage threshold in CI/CD',
                    'Pair test writing with feature development',
                    'Review untested code paths weekly'
                ],
                'effort': 'high',
                'impact': 30
            },
            # ... more dimensions
        },
        'cautious_perfectionist': {
            'complexity': {
                'template': 'Code is too complex. Refactor to reduce cyclomatic complexity.',
                'steps': [
                    'Identify functions with complexity > 10',
                    'Extract smaller functions (single responsibility)',
                    'Add unit tests for extracted functions'
                ],
                'effort': 'medium',
                'impact': 20
            },
            # ... more dimensions
        },
        # ... other archetypes
    }
    
    @staticmethod
    def generate_suggestions(team_id: str, db: SessionLocal) -> List[Suggestion]:
        """Generate personalized suggestions based on team archetype and weak dimensions."""
        
        # Get team data
        team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
        if not team:
            return []
        
        archetype = team.personality_archetype
        suggestions = []
        
        # Get archetype templates
        templates = SuggestionEngineService.ARCHETYPE_SUGGESTIONS.get(archetype, {})
        
        # Find weak dimensions (< 70)
        dimensions = ['security', 'complexity', 'documentation', 'testing', 'dependencies', 'maintainability']
        
        for dimension in dimensions:
            score = getattr(team, dimension, 0)
            
            if score < 70:  # Threshold for suggesting improvement
                template = templates.get(dimension, {})
                
                if not template:
                    continue
                
                # Calculate priority (lower score = higher priority)
                priority = 5 - int(score / 20)  # 1-5
                
                suggestion = Suggestion(
                    id=str(uuid.uuid4()),
                    team_id=team_id,
                    archetype=archetype,
                    dimension=dimension,
                    current_score=score,
                    target_score=80,  # Target all dimensions to 80+
                    suggestion_text=template['template'],
                    implementation_steps=json.dumps(template['steps']),
                    estimated_effort=template['effort'],
                    estimated_impact=template['impact'],
                    priority=priority,
                    status='pending',
                    created_at=datetime.utcnow(),
                    created_by='system'
                )
                db.add(suggestion)
                suggestions.append(suggestion)
        
        db.commit()
        return suggestions
    
    @staticmethod
    def dismiss_suggestion(suggestion_id: str, reason: str, db: SessionLocal):
        """Team lead dismisses a suggestion with reason."""
        suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
        if suggestion:
            suggestion.status = 'dismissed'
            suggestion.dismissed_at = datetime.utcnow()
            suggestion.dismissed_reason = reason
            db.commit()
    
    @staticmethod
    def accept_suggestion(suggestion_id: str, db: SessionLocal) -> Intervention:
        """Convert suggestion to intervention when team commits to it."""
        suggestion = db.query(Suggestion).filter(Suggestion.id == suggestion_id).first()
        
        if not suggestion:
            return None
        
        # Create intervention
        intervention = Intervention(
            id=str(uuid.uuid4()),
            team_id=suggestion.team_id,
            suggestion_id=suggestion_id,
            title=f"Improve {suggestion.dimension.title()}",
            description=suggestion.suggestion_text,
            intervention_type=suggestion.dimension,
            status='in_progress',
            started_at=datetime.utcnow(),
            expected_impact_dimension=suggestion.dimension,
            expected_impact_points=suggestion.estimated_impact,
            created_at=datetime.utcnow()
        )
        
        # Update suggestion
        suggestion.status = 'in_progress'
        
        db.add(intervention)
        db.commit()
        return intervention
```

**Tests:** `tests/test_suggestion_engine.py` (6 test cases)
- Generate suggestions for each archetype
- Dismiss suggestion
- Accept suggestion creates intervention
- Handle no weak dimensions
- Priority calculated correctly
- Implementation steps valid JSON

---

### Phase I+2.2: Intervention Tracking Service (3-4 hours)

**File:** `api/services/intervention_tracking.py`

```python
class InterventionTrackingService:
    """Track team interventions and measure outcomes."""
    
    @staticmethod
    def create_intervention(team_id: str, title: str, description: str, 
                           expected_dimension: str, expected_impact: float,
                           db: SessionLocal) -> Intervention:
        """Create manual intervention (not from suggestion)."""
        intervention = Intervention(
            id=str(uuid.uuid4()),
            team_id=team_id,
            title=title,
            description=description,
            intervention_type='custom',
            status='not_started',
            expected_impact_dimension=expected_dimension,
            expected_impact_points=expected_impact,
            created_at=datetime.utcnow()
        )
        db.add(intervention)
        db.commit()
        return intervention
    
    @staticmethod
    def start_intervention(intervention_id: str, owner_id: str, db: SessionLocal):
        """Mark intervention as in progress."""
        intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
        if intervention:
            intervention.status = 'in_progress'
            intervention.started_at = datetime.utcnow()
            intervention.owner_id = owner_id
            db.commit()
    
    @staticmethod
    def complete_intervention(intervention_id: str, actual_dimension: str, 
                             actual_impact: float, db: SessionLocal):
        """Mark intervention as complete and record actual impact."""
        intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
        if intervention:
            intervention.status = 'completed'
            intervention.completed_at = datetime.utcnow()
            intervention.actual_impact_dimension = actual_dimension
            intervention.actual_impact_points = actual_impact
            db.commit()
            
            # Check if impact met expectations
            if actual_impact >= intervention.expected_impact_points * 0.8:
                # Award badge for successful intervention
                GamificationService.award_badge(
                    team_id=intervention.team_id,
                    badge_name=f"Successful {actual_dimension.title()} Improvement",
                    badge_type='improvement',
                    awarded_for=f"Improved {actual_dimension} by {actual_impact:.1f} points",
                    db=db
                )
    
    @staticmethod
    def get_intervention_roi(team_id: str, db: SessionLocal) -> Dict:
        """Calculate return on investment for all interventions."""
        interventions = db.query(Intervention).filter(
            Intervention.team_id == team_id,
            Intervention.status == 'completed'
        ).all()
        
        if not interventions:
            return {'roi': 0, 'interventions': 0, 'total_expected': 0, 'total_actual': 0}
        
        total_expected = sum(i.expected_impact_points for i in interventions)
        total_actual = sum(i.actual_impact_points for i in interventions)
        
        roi = (total_actual - total_expected) / total_expected * 100 if total_expected > 0 else 0
        
        return {
            'roi': roi,
            'interventions_completed': len(interventions),
            'total_expected_impact': total_expected,
            'total_actual_impact': total_actual,
            'success_rate': len([i for i in interventions if i.actual_impact_points >= i.expected_impact_points * 0.8]) / len(interventions)
        }
```

**Tests:** `tests/test_intervention_tracking.py` (5 test cases)
- Create intervention
- Start intervention
- Complete intervention
- Calculate ROI
- Award badge on success

---

### Phase I+2.3: A/B Testing Service (4-5 hours)

**File:** `api/services/ab_testing_service.py`

```python
class ABTestingService:
    """Compare culture improvements across branches."""
    
    @staticmethod
    def create_test(team_id: str, test_name: str, hypothesis: str,
                   control_branch: str, test_branch: str,
                   metric: str, duration_days: int, db: SessionLocal) -> ABTest:
        """Setup A/B test for culture improvement."""
        
        # Get baseline metrics
        control_history = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= datetime.utcnow() - timedelta(days=1)
        ).order_by(CAQIHistory.recorded_at.desc()).first()
        
        test = ABTest(
            id=str(uuid.uuid4()),
            team_id=team_id,
            test_name=test_name,
            description=hypothesis,
            control_branch=control_branch,
            test_branch=test_branch,
            hypothesis=hypothesis,
            metric=metric,
            started_at=datetime.utcnow(),
            duration_days=duration_days,
            control_baseline=getattr(control_history, metric) if control_history else 0,
            result='in_progress',
            created_at=datetime.utcnow()
        )
        
        db.add(test)
        db.commit()
        return test
    
    @staticmethod
    def record_test_metrics(test_id: str, control_final: float, test_final: float, 
                           p_value: float, db: SessionLocal):
        """Record final metrics and determine winner."""
        test = db.query(ABTest).filter(ABTest.id == test_id).first()
        
        if not test:
            return
        
        test.control_final = control_final
        test.test_final = test_final
        test.p_value = p_value
        test.ended_at = datetime.utcnow()
        
        # Determine winner (statistically significant)
        if p_value < 0.05:  # 95% confidence
            if test_final > control_final:
                test.result = 'winner_test'
            else:
                test.result = 'winner_control'
        else:
            test.result = 'inconclusive'
        
        db.commit()
        
        # Award badge if test branch won
        if test.result == 'winner_test':
            GamificationService.award_badge(
                team_id=test.team_id,
                badge_name='A/B Test Winner',
                badge_type='innovation',
                awarded_for=f'Test branch improved {test.metric} from {control_final:.0f} to {test_final:.0f}',
                db=db
            )
    
    @staticmethod
    def get_active_tests(team_id: str, db: SessionLocal) -> List[ABTest]:
        """Get active A/B tests for team."""
        return db.query(ABTest).filter(
            ABTest.team_id == team_id,
            ABTest.result == 'in_progress'
        ).all()
```

**Tests:** `tests/test_ab_testing_service.py` (5 test cases)
- Create A/B test
- Record metrics
- Determine winner (p-value)
- Handle inconclusive results
- Award badge for winner

---

### Phase I+2.4: Gamification Service (3-4 hours)

**File:** `api/services/gamification_service.py`

```python
class GamificationService:
    """Award badges, track streaks, and build leaderboards."""
    
    @staticmethod
    def award_badge(team_id: str, badge_name: str, badge_type: str, 
                   awarded_for: str, db: SessionLocal) -> Badge:
        """Award badge to team."""
        badge = Badge(
            id=str(uuid.uuid4()),
            team_id=team_id,
            badge_name=badge_name,
            badge_type=badge_type,
            description=f"Awarded for: {awarded_for}",
            awarded_at=datetime.utcnow(),
            awarded_for=awarded_for
        )
        db.add(badge)
        db.commit()
        return badge
    
    @staticmethod
    def check_and_award_improvement_streak(team_id: str, dimension: str = None, 
                                          threshold_percent: float = 5, db: SessionLocal):
        """Check if team is on an improvement streak."""
        
        today = datetime.utcnow().date()
        
        # Get active streak
        active_streak = db.query(ImprovementStreak).filter(
            ImprovementStreak.team_id == team_id,
            ImprovementStreak.dimension == dimension,
            ImprovementStreak.status == 'active'
        ).first()
        
        # Get today's vs yesterday's score
        today_history = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= datetime(today.year, today.month, today.day)
        ).first()
        
        yesterday = today - timedelta(days=1)
        yesterday_history = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= datetime(yesterday.year, yesterday.month, yesterday.day),
            CAQIHistory.recorded_at < datetime(today.year, today.month, today.day)
        ).first()
        
        if not today_history or not yesterday_history:
            return
        
        # Check if improved
        today_score = today_history.overall_caqi if dimension is None else getattr(today_history, dimension)
        yesterday_score = yesterday_history.overall_caqi if dimension is None else getattr(yesterday_history, dimension)
        
        improvement_percent = ((today_score - yesterday_score) / yesterday_score * 100) if yesterday_score > 0 else 0
        
        if improvement_percent >= threshold_percent:
            if active_streak:
                active_streak.days_in_streak += 1
                active_streak.end_date = today
                db.commit()
                
                # Award milestone badges
                if active_streak.days_in_streak == 7:
                    GamificationService.award_badge(team_id, "Week on Fire", "streak", 
                                                   "7-day improvement streak", db)
                elif active_streak.days_in_streak == 30:
                    GamificationService.award_badge(team_id, "Month of Excellence", "streak",
                                                   "30-day improvement streak", db)
            else:
                # Start new streak
                streak = ImprovementStreak(
                    id=str(uuid.uuid4()),
                    team_id=team_id,
                    start_date=today,
                    end_date=today,
                    days_in_streak=1,
                    dimension=dimension,
                    improvement_threshold=threshold_percent,
                    status='active'
                )
                db.add(streak)
                db.commit()
        else:
            # Break streak
            if active_streak:
                active_streak.status = 'broken'
                db.commit()
    
    @staticmethod
    def get_leaderboard(limit: int = 10, db: SessionLocal) -> List[Dict]:
        """Get team leaderboard ranked by badges and streaks."""
        
        # Get all teams with their badges and streaks
        teams = db.query(TeamScore).all()
        
        leaderboard = []
        
        for team in teams:
            badges = db.query(Badge).filter(Badge.team_id == team.team_id).count()
            active_streaks = db.query(ImprovementStreak).filter(
                ImprovementStreak.team_id == team.team_id,
                ImprovementStreak.status == 'active'
            ).all()
            
            longest_streak = max([s.days_in_streak for s in active_streaks], default=0)
            
            # Calculate leaderboard score
            score = (badges * 10) + longest_streak
            
            leaderboard.append({
                'rank': 0,  # Will be set after sorting
                'team_id': team.team_id,
                'team_name': team.team_name,
                'badges_earned': badges,
                'current_streak': longest_streak,
                'leaderboard_score': score,
                'overall_caqi': team.overall_caqi
            })
        
        # Sort by score
        leaderboard.sort(key=lambda x: x['leaderboard_score'], reverse=True)
        
        # Add ranks
        for i, entry in enumerate(leaderboard[:limit], 1):
            entry['rank'] = i
        
        return leaderboard[:limit]
    
    @staticmethod
    def get_team_badges(team_id: str, db: SessionLocal) -> List[Badge]:
        """Get all badges earned by team."""
        return db.query(Badge).filter(
            Badge.team_id == team_id
        ).order_by(Badge.awarded_at.desc()).all()
```

**Tests:** `tests/test_gamification_service.py` (6 test cases)
- Award badge
- Check improvement streak
- Break streak
- Award milestone badges (7-day, 30-day)
- Get leaderboard (sorted)
- Get team badges

---

### Phase I+2.5: REST API Endpoints (4-5 hours)

**File:** `api/routes/culture_interventions.py` (new)

```python
from fastapi import APIRouter, HTTPException, Query, Depends
from api.services.suggestion_engine import SuggestionEngineService
from api.services.intervention_tracking import InterventionTrackingService
from api.services.ab_testing_service import ABTestingService
from api.services.gamification_service import GamificationService

router = APIRouter(prefix="/api/v1/caqi", tags=["culture-interventions"])

@router.get("/suggestions/{team_id}")
async def get_suggestions(team_id: str, db: SessionLocal = Depends(get_db)):
    """Get personalized suggestions for team."""
    suggestions = SuggestionEngineService.generate_suggestions(team_id, db)
    return {
        'team_id': team_id,
        'suggestion_count': len(suggestions),
        'suggestions': [
            {
                'id': s.id,
                'dimension': s.dimension,
                'current_score': s.current_score,
                'target_score': s.target_score,
                'suggestion': s.suggestion_text,
                'effort': s.estimated_effort,
                'impact': s.estimated_impact,
                'priority': s.priority,
                'steps': json.loads(s.implementation_steps) if s.implementation_steps else []
            }
            for s in suggestions
        ]
    }

@router.post("/suggestions/{suggestion_id}/dismiss")
async def dismiss_suggestion(suggestion_id: str, reason: str, db: SessionLocal = Depends(get_db)):
    """Dismiss suggestion."""
    SuggestionEngineService.dismiss_suggestion(suggestion_id, reason, db)
    return {'status': 'dismissed', 'suggestion_id': suggestion_id}

@router.post("/suggestions/{suggestion_id}/accept")
async def accept_suggestion(suggestion_id: str, db: SessionLocal = Depends(get_db)):
    """Convert suggestion to intervention."""
    intervention = SuggestionEngineService.accept_suggestion(suggestion_id, db)
    return {
        'status': 'accepted',
        'intervention_id': intervention.id,
        'started_at': intervention.started_at
    }

@router.get("/interventions/{team_id}")
async def get_interventions(team_id: str, status: str = None, db: SessionLocal = Depends(get_db)):
    """Get interventions for team."""
    query = db.query(Intervention).filter(Intervention.team_id == team_id)
    
    if status:
        query = query.filter(Intervention.status == status)
    
    interventions = query.order_by(Intervention.created_at.desc()).all()
    
    return {
        'team_id': team_id,
        'intervention_count': len(interventions),
        'interventions': [
            {
                'id': i.id,
                'title': i.title,
                'status': i.status,
                'expected_impact': i.expected_impact_points,
                'actual_impact': i.actual_impact_points
            }
            for i in interventions
        ]
    }

@router.get("/interventions/{team_id}/roi")
async def get_intervention_roi(team_id: str, db: SessionLocal = Depends(get_db)):
    """Get ROI of interventions."""
    roi = InterventionTrackingService.get_intervention_roi(team_id, db)
    return roi

@router.post("/ab-tests")
async def create_ab_test(team_id: str, test_name: str, hypothesis: str,
                        control_branch: str, test_branch: str,
                        metric: str, duration_days: int, 
                        db: SessionLocal = Depends(get_db)):
    """Create A/B test."""
    test = ABTestingService.create_test(team_id, test_name, hypothesis,
                                       control_branch, test_branch, metric, duration_days, db)
    return {
        'id': test.id,
        'test_name': test.test_name,
        'started_at': test.started_at,
        'duration_days': duration_days
    }

@router.get("/ab-tests/{team_id}")
async def get_ab_tests(team_id: str, db: SessionLocal = Depends(get_db)):
    """Get A/B tests for team."""
    tests = ABTestingService.get_active_tests(team_id, db)
    return {
        'team_id': team_id,
        'test_count': len(tests),
        'tests': [
            {
                'id': t.id,
                'name': t.test_name,
                'metric': t.metric,
                'result': t.result,
                'progress': f"{t.started_at} to {t.started_at + timedelta(days=t.duration_days)}"
            }
            for t in tests
        ]
    }

@router.get("/gamification/badges/{team_id}")
async def get_team_badges(team_id: str, db: SessionLocal = Depends(get_db)):
    """Get badges earned by team."""
    badges = GamificationService.get_team_badges(team_id, db)
    return {
        'team_id': team_id,
        'badge_count': len(badges),
        'badges': [
            {
                'id': b.id,
                'name': b.badge_name,
                'type': b.badge_type,
                'awarded_for': b.awarded_for,
                'awarded_at': b.awarded_at
            }
            for b in badges
        ]
    }

@router.get("/gamification/leaderboard")
async def get_leaderboard(limit: int = Query(10), db: SessionLocal = Depends(get_db)):
    """Get team leaderboard."""
    leaderboard = GamificationService.get_leaderboard(limit, db)
    return {
        'leaderboard': leaderboard,
        'total_teams': len(leaderboard)
    }

@router.post("/gamification/streaks/{team_id}/check")
async def check_streak(team_id: str, dimension: str = None, db: SessionLocal = Depends(get_db)):
    """Check and update improvement streaks."""
    GamificationService.check_and_award_improvement_streak(team_id, dimension, db=db)
    return {'status': 'streak_checked', 'team_id': team_id}
```

**API Endpoints Summary:**
```
GET    /api/v1/caqi/suggestions/{team_id}
POST   /api/v1/caqi/suggestions/{suggestion_id}/dismiss
POST   /api/v1/caqi/suggestions/{suggestion_id}/accept
GET    /api/v1/caqi/interventions/{team_id}
GET    /api/v1/caqi/interventions/{team_id}/roi
POST   /api/v1/caqi/ab-tests
GET    /api/v1/caqi/ab-tests/{team_id}
GET    /api/v1/caqi/gamification/badges/{team_id}
GET    /api/v1/caqi/gamification/leaderboard
POST   /api/v1/caqi/gamification/streaks/{team_id}/check
```

**Tests:** `tests/test_culture_interventions_api.py` (8 test cases)
- Get suggestions
- Dismiss/accept suggestion
- Get interventions
- Calculate ROI
- Create A/B test
- Get badges
- Get leaderboard
- Check streaks

---

### Phase I+2.6: Frontend Components (5-6 hours)

**Component 1:** `frontend/src/components/SuggestionsPanel.tsx`

```tsx
import React, { useEffect, useState } from 'react';
import { Lightbulb, ThumbsUp, X } from 'lucide-react';

interface SuggestionsPanelProps {
  teamId: string;
}

export const SuggestionsPanel: React.FC<SuggestionsPanelProps> = ({ teamId }) => {
  const [suggestions, setSuggestions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchSuggestions();
  }, [teamId]);

  const fetchSuggestions = async () => {
    try {
      const response = await fetch(`/api/v1/caqi/suggestions/${teamId}`);
      const data = await response.json();
      setSuggestions(data.suggestions);
    } finally {
      setLoading(false);
    }
  };

  const handleAccept = async (suggestionId: string) => {
    await fetch(`/api/v1/caqi/suggestions/${suggestionId}/accept`, { method: 'POST' });
    setSuggestions(s => s.filter(x => x.id !== suggestionId));
  };

  const handleDismiss = async (suggestionId: string) => {
    await fetch(`/api/v1/caqi/suggestions/${suggestionId}/dismiss?reason=not-relevant`, { method: 'POST' });
    setSuggestions(s => s.filter(x => x.id !== suggestionId));
  };

  if (loading) return <div>Loading suggestions...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Lightbulb size={24} color="#f59e0b" />
        Improvement Suggestions
      </h2>
      
      {suggestions.length === 0 ? (
        <p>✅ No suggestions at this time</p>
      ) : (
        suggestions.map(s => (
          <div
            key={s.id}
            style={{
              border: '1px solid #e5e7eb',
              borderRadius: '8px',
              padding: '16px',
              marginBottom: '12px',
              backgroundColor: '#f9fafb'
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
              <div>
                <div style={{ fontWeight: 'bold', fontSize: '16px' }}>
                  {s.dimension.charAt(0).toUpperCase() + s.dimension.slice(1)}
                </div>
                <p style={{ margin: '8px 0', color: '#4b5563' }}>{s.suggestion}</p>
                
                <div style={{ marginTop: '12px' }}>
                  <strong>Steps:</strong>
                  <ol style={{ marginTop: '8px', paddingLeft: '20px' }}>
                    {s.steps.map((step: string, i: number) => (
                      <li key={i} style={{ marginBottom: '4px' }}>{step}</li>
                    ))}
                  </ol>
                </div>
                
                <div style={{ display: 'flex', gap: '16px', marginTop: '12px', fontSize: '14px' }}>
                  <span>Effort: <strong>{s.effort}</strong></span>
                  <span>Impact: <strong>+{s.impact} points</strong></span>
                  <span>Priority: <strong>P{s.priority}</strong></span>
                </div>
              </div>
              
              <div style={{ display: 'flex', gap: '8px' }}>
                <button
                  onClick={() => handleAccept(s.id)}
                  style={{
                    backgroundColor: '#10b981',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '8px 12px',
                    cursor: 'pointer'
                  }}
                >
                  <ThumbsUp size={16} /> Accept
                </button>
                <button
                  onClick={() => handleDismiss(s.id)}
                  style={{
                    backgroundColor: '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    padding: '8px 12px',
                    cursor: 'pointer'
                  }}
                >
                  <X size={16} />
                </button>
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
};
```

**Component 2:** `frontend/src/components/InterventionTracker.tsx` (similar structure)

**Component 3:** `frontend/src/components/ABTestDashboard.tsx` (similar structure)

**Component 4:** `frontend/src/components/GamificationLeaderboard.tsx`

```tsx
import React, { useEffect, useState } from 'react';
import { Award, Trophy, Flame } from 'lucide-react';

export const GamificationLeaderboard: React.FC = () => {
  const [leaderboard, setLeaderboard] = useState<any[]>([]);

  useEffect(() => {
    fetchLeaderboard();
  }, []);

  const fetchLeaderboard = async () => {
    const response = await fetch('/api/v1/caqi/gamification/leaderboard');
    const data = await response.json();
    setLeaderboard(data.leaderboard);
  };

  const getMedalColor = (rank: number) => {
    switch (rank) {
      case 1: return '#fbbf24';  // Gold
      case 2: return '#d1d5db';  // Silver
      case 3: return '#d97706';  // Bronze
      default: return '#9ca3af';
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <Trophy size={24} color="#fbbf24" />
        Team Leaderboard
      </h2>
      
      <table style={{ width: '100%', borderCollapse: 'collapse' }}>
        <thead>
          <tr style={{ borderBottom: '2px solid #e5e7eb' }}>
            <th style={{ padding: '12px', textAlign: 'left' }}>Rank</th>
            <th style={{ padding: '12px', textAlign: 'left' }}>Team</th>
            <th style={{ padding: '12px', textAlign: 'right' }}>Badges</th>
            <th style={{ padding: '12px', textAlign: 'right' }}>Streak</th>
            <th style={{ padding: '12px', textAlign: 'right' }}>CAQI</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map(team => (
            <tr key={team.team_id} style={{ borderBottom: '1px solid #f3f4f6' }}>
              <td style={{ padding: '12px' }}>
                <span style={{ fontSize: '20px', color: getMedalColor(team.rank) }}>
                  {team.rank === 1 ? '🥇' : team.rank === 2 ? '🥈' : team.rank === 3 ? '🥉' : `#${team.rank}`}
                </span>
              </td>
              <td style={{ padding: '12px' }}>{team.team_name}</td>
              <td style={{ padding: '12px', textAlign: 'right' }}>
                <Award size={16} style={{ display: 'inline', marginRight: '4px' }} />
                {team.badges_earned}
              </td>
              <td style={{ padding: '12px', textAlign: 'right' }}>
                {team.current_streak > 0 && <Flame size={16} style={{ display: 'inline', marginRight: '4px' }} />}
                {team.current_streak}
              </td>
              <td style={{ padding: '12px', textAlign: 'right' }}>
                {team.overall_caqi.toFixed(0)}/500
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
```

**Tests:** `frontend/src/__tests__/CultureInterventions.test.tsx` (8 test cases)
- Render suggestions
- Accept/dismiss suggestions
- Render interventions
- Display intervention ROI
- Render A/B test dashboard
- Render leaderboard
- Sort leaderboard by score
- Display badges

---

### Phase I+2.7: Testing & Quality (3-4 hours)

**Test Coverage Target:** 85% (new files)

**Test Files:**
1. `tests/test_suggestion_engine.py` (6 tests)
2. `tests/test_intervention_tracking.py` (5 tests)
3. `tests/test_ab_testing_service.py` (5 tests)
4. `tests/test_gamification_service.py` (6 tests)
5. `tests/test_culture_interventions_api.py` (8 tests)
6. `frontend/src/__tests__/SuggestionsPanel.test.tsx` (5 tests)
7. `frontend/src/__tests__/InterventionTracker.test.tsx` (5 tests)
8. `frontend/src/__tests__/ABTestDashboard.test.tsx` (5 tests)
9. `frontend/src/__tests__/GamificationLeaderboard.test.tsx` (5 tests)

**Total: 50 new tests**

**Quality Metrics:**
```
New Backend Tests:   30
New Frontend Tests:  20
Total New Tests:     50

Target Coverage: 85% (statements)
Expected Time: 3-4 hours
```

---

## Deployment Checklist (Phase I+2)

### Pre-Deployment (3-4 days before)

- [ ] All 50 new tests passing
- [ ] Code review completed
- [ ] Suggestion engine validated (archetype-specific)
- [ ] Gamification badges configured
- [ ] Database migration tested on staging
- [ ] Email notifications working

### Deployment Day

1. **Database**
   ```bash
   alembic upgrade head
   ```

2. **Backend**
   ```bash
   pip install -r requirements.txt
   systemctl restart codepulse-api
   ```

3. **Frontend**
   ```bash
   npm run build
   ```

4. **Verify**
   ```bash
   curl http://api.example.com/api/v1/caqi/suggestions/team-001
   curl http://api.example.com/api/v1/caqi/gamification/leaderboard
   ```

### Post-Deployment (First Week)

- [ ] Suggestions generated correctly
- [ ] Teams accepting suggestions
- [ ] Interventions tracking properly
- [ ] A/B tests running
- [ ] Badges awarded correctly
- [ ] Leaderboard displaying
- [ ] No spam notifications

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| I+2.0 | 3h | Database schema, ORM models |
| I+2.1 | 4-5h | Suggestion engine service |
| I+2.2 | 3-4h | Intervention tracking |
| I+2.3 | 4-5h | A/B testing service |
| I+2.4 | 3-4h | Gamification service |
| I+2.5 | 4-5h | REST API (6 endpoints) |
| I+2.6 | 5-6h | Frontend components (4) |
| I+2.7 | 3-4h | Testing & quality |
| **TOTAL** | **15-20h** | **Production-ready** |

---

## Success Criteria

✅ **Code Quality:**
- 50 new tests, 100% passing
- 85% code coverage (new files)
- 0 TypeScript errors
- 0 security issues

✅ **Performance:**
- Suggestion generation < 500ms
- Leaderboard render < 300ms
- API endpoints < 500ms
- Badge awarding < 200ms

✅ **Functionality:**
- Suggestions generated per archetype
- Teams can accept suggestions
- Interventions track progress
- A/B tests compare branches
- Gamification badges awarded
- Leaderboard displays correctly

✅ **Engagement:**
- Teams accept 50%+ of suggestions
- Interventions improve scores
- A/B tests show winners
- Badges motivate participation
- Leaderboard drives competition

---

## Post-Phase I+2: Next Steps

**Phase I+3: Export & Reporting (10-15 hours)**
- PDF report generation
- Email digests (weekly/monthly)
- Slack integrations
- Executive dashboard
- Historical report exports

---

## Resources

**Related Documentation:**
- `PATH_I_CAQI_ENHANCED_IMPLEMENTATION_PLAN.md` — Phase I
- `PHASE_I+1_ADVANCED_ANALYTICS_IMPLEMENTATION_PLAN.md` — Advanced Analytics
- `DEPLOYMENT_SETUP.md` — Local setup
- `DATABASE_MIGRATION.md` — Migration strategy

**Dependencies:**
- Phase I.0-I.5 deployed
- Phase I+1 (Advanced Analytics) deployed
- Email service configured
- Notification system ready

---

**Status:** Ready to implement  
**Estimated Start:** 1 week after Phase I+1 deployment  
**Estimated Completion:** 2-3 weeks (15-20 hours)
