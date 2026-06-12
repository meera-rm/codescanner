---
created_at: 2026-06-12T18:16:43Z
title: Phase I+2 Culture Interventions Corrected
source: claude-code
project: codescanner
---

# Phase I+2: Culture Interventions - CORRECTED IMPLEMENTATION PLAN

**Status:** ✅ CORRECTED - All critical issues fixed  
**Date:** 2026-06-06  
**Changes:** 6 critical fixes, database constraints, input validation

---

## CRITICAL FIXES IMPLEMENTED

### FIX 1: Suggestion Templates - Move to Database

**Issue:** Archetype suggestions hardcoded in Python, can't update without code  
**Solution:** Create suggestion_templates table

```sql
-- NEW TABLE
CREATE TABLE suggestion_templates (
    id VARCHAR(36) PRIMARY KEY,
    archetype VARCHAR(50) NOT NULL,
    dimension VARCHAR(50) NOT NULL,
    
    suggestion_text TEXT NOT NULL,
    implementation_steps TEXT,  -- JSON array
    estimated_effort VARCHAR(20),  -- low, medium, high
    estimated_impact FLOAT,  -- 0-100
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by VARCHAR(255),
    
    UNIQUE KEY unique_archetype_dimension (archetype, dimension),
    INDEX idx_archetype (archetype)
);

-- SEED DATA
INSERT INTO suggestion_templates VALUES
('uuid1', 'reckless_optimist', 'security', 'Security is lower than team average...', '[...]', 'medium', 25, NOW(), NOW(), 'system'),
('uuid2', 'reckless_optimist', 'testing', 'Testing coverage is low...', '[...]', 'high', 30, NOW(), NOW(), 'system'),
-- ... more templates
```

```python
# CORRECTED CODE
class SuggestionEngineService:
    @staticmethod
    def generate_suggestions(team_id: str, db: SessionLocal) -> List[Suggestion]:
        """Generate suggestions from database templates."""
        
        team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
        if not team:
            return []
        
        archetype = team.personality_archetype
        suggestions = []
        
        # FIXED: Load from database instead of hardcoded dict
        templates = db.query(SuggestionTemplate).filter(
            SuggestionTemplate.archetype == archetype
        ).all()
        
        if not templates:
            logger.warning(f"No templates found for archetype {archetype}")
            return []
        
        dimensions = ['security', 'complexity', 'documentation', 'testing', 'dependencies', 'maintainability']
        
        for dimension in dimensions:
            score = getattr(team, dimension, 0)
            
            if score < 70:  # Threshold
                # Find matching template
                template = next((t for t in templates if t.dimension == dimension), None)
                
                if not template:
                    continue
                
                priority = 5 - int(score / 20)
                
                suggestion = Suggestion(
                    id=str(uuid.uuid4()),
                    team_id=team_id,
                    archetype=archetype,
                    dimension=dimension,
                    current_score=score,
                    target_score=80,
                    suggestion_text=template.suggestion_text,
                    implementation_steps=template.implementation_steps,
                    estimated_effort=template.estimated_effort,
                    estimated_impact=template.estimated_impact,
                    priority=priority,
                    status='pending',
                    created_at=datetime.utcnow(),
                    created_by='system'
                )
                db.add(suggestion)
                suggestions.append(suggestion)
        
        db.commit()
        return suggestions
```

---

### FIX 2: A/B Testing - Add Statistical Rigor

**Issue:** Uses only p-value, ignores sample size and effect size  
**Solution:** Implement proper statistical testing

```python
# CORRECTED CODE
from scipy import stats
import numpy as np

class ABTestingService:
    MIN_SAMPLE_SIZE = 30  # Require 30+ observations
    MIN_EFFECT_SIZE = 0.2  # Cohen's d threshold
    
    @staticmethod
    def is_statistically_significant(control_data: List[float], 
                                     test_data: List[float]) -> tuple:
        """
        Check if test significantly outperforms control.
        
        Returns: (is_significant: bool, p_value: float, effect_size: float)
        """
        
        # FIXED: Check sample sizes
        if len(control_data) < ABTestingService.MIN_SAMPLE_SIZE:
            return False, None, None, f"Control: {len(control_data)} < {ABTestingService.MIN_SAMPLE_SIZE}"
        
        if len(test_data) < ABTestingService.MIN_SAMPLE_SIZE:
            return False, None, None, f"Test: {len(test_data)} < {ABTestingService.MIN_SAMPLE_SIZE}"
        
        # Perform t-test
        t_stat, p_value = stats.ttest_ind(control_data, test_data)
        
        # Calculate effect size (Cohen's d)
        pooled_std = np.sqrt(
            (np.std(control_data) ** 2 + np.std(test_data) ** 2) / 2
        )
        
        if pooled_std == 0:
            effect_size = 0
        else:
            effect_size = (np.mean(test_data) - np.mean(control_data)) / pooled_std
        
        # FIXED: Check both p-value AND effect size
        is_significant = (
            p_value < 0.05 and  # 95% confidence
            abs(effect_size) >= ABTestingService.MIN_EFFECT_SIZE  # Practical significance
        )
        
        return is_significant, p_value, effect_size, None
    
    @staticmethod
    def record_test_metrics(test_id: str, control_data: List[float], 
                           test_data: List[float], db: SessionLocal):
        """Record final metrics with proper statistical analysis."""
        
        test = db.query(ABTest).filter(ABTest.id == test_id).first()
        if not test:
            return
        
        is_significant, p_value, effect_size, error = ABTestingService.is_statistically_significant(
            control_data, test_data
        )
        
        if error:
            logger.warning(f"A/B test {test_id}: {error}")
            test.result = 'inconclusive'
        elif not is_significant:
            test.result = 'inconclusive'
        elif np.mean(test_data) > np.mean(control_data):
            test.result = 'winner_test'
        else:
            test.result = 'winner_control'
        
        test.control_final = np.mean(control_data)
        test.test_final = np.mean(test_data)
        test.p_value = p_value
        test.ended_at = datetime.utcnow()
        
        db.commit()
        
        # Award badge only if test wins with significance
        if test.result == 'winner_test':
            GamificationService.award_badge(
                team_id=test.team_id,
                badge_name='A/B Test Winner',
                badge_type='innovation',
                awarded_for=f'Test improved {test.metric} with p={p_value:.3f}, d={effect_size:.2f}',
                db=db
            )
```

---

### FIX 3: Gamification - Fix Streak Race Condition

**Issue:** Two concurrent processes might create duplicate streaks  
**Solution:** Use database-level UNIQUE constraint

```sql
-- CORRECTED TABLE
CREATE TABLE improvement_streaks (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    
    start_date DATE NOT NULL,
    end_date DATE,
    days_in_streak INT DEFAULT 1,
    
    dimension VARCHAR(50),
    improvement_threshold FLOAT,
    
    status VARCHAR(20),
    
    UNIQUE KEY unique_team_dimension_date (team_id, dimension, start_date),
    INDEX idx_team_active (team_id, status),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);
```

```python
# CORRECTED CODE - Use upsert pattern
class GamificationService:
    @staticmethod
    def check_and_award_improvement_streak(team_id: str, dimension: str = None, 
                                          threshold_percent: float = 5, db: SessionLocal):
        """Check improvement streak with race-condition handling."""
        
        today = datetime.utcnow().date()
        
        # FIXED: Atomic upsert using database constraints
        try:
            # Try to find active streak
            active_streak = db.query(ImprovementStreak).filter(
                ImprovementStreak.team_id == team_id,
                ImprovementStreak.dimension == dimension,
                ImprovementStreak.status == 'active'
            ).with_for_update().first()  # Lock the row
            
            # Check if improved
            today_score = get_today_score(team_id, dimension, db)
            yesterday_score = get_yesterday_score(team_id, dimension, db)
            
            if today_score is None or yesterday_score is None:
                return
            
            improvement_percent = ((today_score - yesterday_score) / yesterday_score * 100)
            
            if improvement_percent >= threshold_percent:
                if active_streak:
                    # Extend existing streak
                    active_streak.end_date = today
                    active_streak.days_in_streak += 1
                    db.commit()
                    
                    # Award milestone badges
                    if active_streak.days_in_streak == 7:
                        GamificationService.award_badge(...)
                    elif active_streak.days_in_streak == 30:
                        GamificationService.award_badge(...)
                else:
                    # Create new streak (UNIQUE constraint prevents duplicates)
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
        
        except IntegrityError:
            # FIXED: Handle race condition where another process created the streak
            db.rollback()
            active_streak = db.query(ImprovementStreak).filter(
                ImprovementStreak.team_id == team_id,
                ImprovementStreak.dimension == dimension,
                ImprovementStreak.status == 'active'
            ).first()
            
            if active_streak and improvement_percent >= threshold_percent:
                active_streak.end_date = today
                active_streak.days_in_streak += 1
                db.commit()
```

---

### FIX 4: Leaderboard - Eliminate N+1 Queries

**Issue:** Queries badges and streaks for each team  
**Solution:** Load all data once, aggregate in-memory

```python
# CORRECTED CODE
class GamificationService:
    @staticmethod
    def get_leaderboard(limit: int = 10, db: SessionLocal) -> List[Dict]:
        """Get leaderboard without N+1 queries."""
        
        # FIXED: Query all data once
        teams = db.query(TeamScore).all()
        all_badges = db.query(Badge).all()
        all_streaks = db.query(ImprovementStreak).filter(
            ImprovementStreak.status == 'active'
        ).all()
        
        # Aggregate in memory
        badge_counts = {}
        for badge in all_badges:
            badge_counts[badge.team_id] = badge_counts.get(badge.team_id, 0) + 1
        
        streak_lengths = {}
        for streak in all_streaks:
            streak_lengths[streak.team_id] = max(
                streak_lengths.get(streak.team_id, 0),
                streak.days_in_streak
            )
        
        # Build leaderboard
        leaderboard = []
        for team in teams:
            badges_count = badge_counts.get(team.team_id, 0)
            longest_streak = streak_lengths.get(team.team_id, 0)
            
            score = (badges_count * 10) + longest_streak
            
            leaderboard.append({
                'rank': 0,
                'team_id': team.team_id,
                'team_name': team.team_name,
                'badges_earned': badges_count,
                'current_streak': longest_streak,
                'leaderboard_score': score,
                'overall_caqi': team.overall_caqi
            })
        
        # Sort and rank
        leaderboard.sort(key=lambda x: x['leaderboard_score'], reverse=True)
        
        for i, entry in enumerate(leaderboard[:limit], 1):
            entry['rank'] = i
        
        return leaderboard[:limit]
```

---

### FIX 5: Intervention Impact - Add Validation

**Issue:** Team can provide any impact value (including 1000)  
**Solution:** Validate or calculate from metrics

```python
# CORRECTED CODE
class InterventionTrackingService:
    MAX_IMPACT_SCORE = 100  # Max points per dimension
    
    @staticmethod
    def complete_intervention(intervention_id: str, actual_dimension: str, 
                             actual_impact: float, calculated: bool = False,
                             db: SessionLocal = None):
        """Complete intervention with impact validation."""
        
        intervention = db.query(Intervention).filter(Intervention.id == intervention_id).first()
        if not intervention:
            raise ValueError(f"Intervention {intervention_id} not found")
        
        # FIXED: Validate impact score
        if not calculated:
            # Input provided by team
            if not 0 <= actual_impact <= InterventionTrackingService.MAX_IMPACT_SCORE:
                raise ValueError(f"Invalid impact: {actual_impact}. Must be 0-{InterventionTrackingService.MAX_IMPACT_SCORE}")
        else:
            # Calculate from actual metrics
            before_score = intervention.expected_before_score or 0
            after_score = get_dimension_score(intervention.team_id, actual_dimension, db)
            actual_impact = max(0, after_score - before_score)
        
        # Verify impact is reasonable
        if actual_impact > intervention.expected_impact_points * 3:
            logger.warning(f"Intervention {intervention_id}: impact {actual_impact} is 3x expected {intervention.expected_impact_points}")
        
        intervention.status = 'completed'
        intervention.completed_at = datetime.utcnow()
        intervention.actual_impact_dimension = actual_dimension
        intervention.actual_impact_points = actual_impact
        db.commit()
        
        # Award badge if impact meets 80% of expectations
        if actual_impact >= intervention.expected_impact_points * 0.8:
            GamificationService.award_badge(
                team_id=intervention.team_id,
                badge_name=f"Successful {actual_dimension.title()} Improvement",
                badge_type='improvement',
                awarded_for=f"Improved {actual_dimension} by {actual_impact:.0f} points",
                db=db
            )
```

---

### FIX 6: Interventions - Link to Root Cause

**Issue:** Interventions don't track what problem they're solving  
**Solution:** Add anomaly_id foreign key

```sql
-- ADD COLUMN
ALTER TABLE interventions
ADD COLUMN anomaly_id VARCHAR(36);

ALTER TABLE interventions
ADD CONSTRAINT fk_anomaly
FOREIGN KEY (anomaly_id) REFERENCES anomalies(id) ON DELETE SET NULL;

-- Create index for queries
CREATE INDEX idx_interventions_anomaly ON interventions(anomaly_id);
```

```python
# CORRECTED CODE
class InterventionTrackingService:
    @staticmethod
    def create_intervention_from_anomaly(anomaly_id: str, db: SessionLocal) -> Intervention:
        """Create intervention triggered by detected anomaly."""
        
        anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if not anomaly:
            raise ValueError(f"Anomaly {anomaly_id} not found")
        
        # Auto-create intervention from anomaly
        intervention = Intervention(
            id=str(uuid.uuid4()),
            team_id=anomaly.team_id,
            anomaly_id=anomaly_id,  # FIXED: Track root cause
            title=f"Address {anomaly.dimension} Drop",
            description=f"{anomaly.dimension} dropped {anomaly.change_percent:.1f}%",
            intervention_type=anomaly.dimension,
            status='not_started',
            expected_impact_dimension=anomaly.dimension,
            expected_impact_points=abs(anomaly.change_percent) * 0.5,  # Conservative estimate
            created_at=datetime.utcnow()
        )
        db.add(intervention)
        db.commit()
        return intervention
```

---

## REVISED DATABASE SCHEMA

```sql
-- Add these indexes for performance
CREATE INDEX idx_suggestions_status ON suggestions(team_id, status);
CREATE INDEX idx_interventions_status ON interventions(team_id, status);
CREATE INDEX idx_ab_tests_result ON ab_tests(team_id, result);
CREATE INDEX idx_badges_team_date ON badges(team_id, awarded_at DESC);
CREATE INDEX idx_streaks_active ON improvement_streaks(team_id, status);
```

---

## REVISED TESTING PLAN

```python
# Added test cases

def test_suggestion_templates_loadable():
    """Suggestions loaded from database, not hardcoded."""
    templates = db.query(SuggestionTemplate).filter(
        SuggestionTemplate.archetype == 'reckless_optimist'
    ).all()
    assert len(templates) > 0

def test_ab_test_requires_sample_size():
    """A/B test rejects insufficient samples."""
    control = [50] * 20  # Only 20 samples
    test = [55] * 20
    
    is_sig, p, d, error = ABTestingService.is_statistically_significant(control, test)
    assert error is not None
    assert not is_sig

def test_ab_test_requires_effect_size():
    """A/B test requires minimum effect size."""
    control = [50] * 100
    test = [50.5] * 100  # Tiny effect (d << 0.2)
    
    is_sig, p, d, error = ABTestingService.is_statistically_significant(control, test)
    assert abs(d) < 0.2
    assert not is_sig

def test_streak_no_duplicates():
    """UNIQUE constraint prevents duplicate streaks."""
    # Create streak
    streak1 = ImprovementStreak(
        team_id='team-001',
        dimension='security',
        start_date=date.today()
    )
    db.add(streak1)
    db.commit()
    
    # Try to create same streak
    streak2 = ImprovementStreak(
        team_id='team-001',
        dimension='security',
        start_date=date.today()
    )
    db.add(streak2)
    
    with pytest.raises(IntegrityError):
        db.commit()

def test_intervention_impact_validation():
    """Intervention impact must be 0-100."""
    intervention = Intervention(...)
    
    with pytest.raises(ValueError):
        InterventionTrackingService.complete_intervention(
            intervention_id=intervention.id,
            actual_dimension='security',
            actual_impact=1000,  # Invalid
            db=db
        )

def test_intervention_links_to_anomaly():
    """Interventions can link to root cause anomalies."""
    anomaly = Anomaly(team_id='team-001', dimension='security', ...)
    db.add(anomaly)
    db.commit()
    
    intervention = InterventionTrackingService.create_intervention_from_anomaly(
        anomaly_id=anomaly.id, db=db
    )
    
    assert intervention.anomaly_id == anomaly.id
```

---

## Summary of Fixes

✅ Suggestions: Moved to database, editable without code  
✅ A/B testing: Added sample size + effect size checks  
✅ Streaks: Fixed race condition with UNIQUE constraint  
✅ Leaderboard: O(n) instead of O(n²)  
✅ Impact validation: Bounds checking (0-100)  
✅ Anomaly linking: Added FK to track root causes  

**Status: Ready for implementation** ✅

