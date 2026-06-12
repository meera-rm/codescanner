# Phase I+1: Advanced Analytics - Implementation Plan

**Project:** CODEPULSE AI - Path I Advanced Analytics  
**Feature:** Anomaly Detection, Peer Comparison, Developer Drill-Down, Automated Alerts  
**Status:** Planning  
**Timeline:** 20-30 hours of development  
**Target Completion:** 2-3 weeks (after Phase I deployment)  
**Dependencies:** Phase I.0-I.5 complete and deployed

---

## Executive Summary

Extend Path I (CAQI Enhanced) with advanced analytics capabilities that help teams understand:

1. **Anomaly Detection** — Alert when team CAQI unexpectedly drops > 10%
2. **Peer Comparison** — Compare team CAQI to peer teams and industry benchmarks
3. **Developer Drill-Down** — See which developers drive dimension changes
4. **Automated Alerts** — Email/Slack notifications on significant changes

**Impact:** Engineering leaders get proactive insights into culture changes and can correlate code quality changes with team events (new hires, migrations, tech debt paydown).

---

## Architecture Overview

### Current Path I Structure (Post-Deployment)
```
Path I: CAQI Enhanced (Deployed)
├── Backend Services
│   ├── TeamAggregationService ✅
│   ├── TrendService ✅
│   └── PersonalityMappingService ✅
├── REST API (8 endpoints) ✅
└── Frontend (3 components + dashboard) ✅
```

### Phase I+1 Enhanced Structure
```
Path I+1: Advanced Analytics (New)
├── Backend Services
│   ├── AnomalyDetectionService (new)
│   ├── PeerComparisonService (new)
│   ├── DeveloperDrillDownService (new)
│   └── AlertingService (new)
├── REST API (5 new endpoints)
│   ├── /api/v1/caqi/anomalies
│   ├── /api/v1/caqi/peer-comparison
│   ├── /api/v1/caqi/developer-metrics
│   ├── /api/v1/caqi/alerts
│   └── /api/v1/caqi/benchmarks
├── Frontend Components (3 new)
│   ├── AnomalyDetectionView
│   ├── PeerComparisonChart
│   └── DeveloperBreakdownTable
├── Background Jobs (2 new)
│   ├── DailyAnomalyDetectionJob
│   └── AlertNotificationJob
└── Data Tables (2 new)
    ├── anomalies
    └── alerts
```

---

## Phase Breakdown

### Phase I+1.0: Data & Schema (3-4 hours)

#### 1. Database Schema Extensions

```sql
-- 1. Anomalies Table
CREATE TABLE anomalies (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    
    dimension VARCHAR(50) NOT NULL,  -- security, complexity, documentation, testing, dependencies, maintainability
    previous_score FLOAT NOT NULL,
    current_score FLOAT NOT NULL,
    change_percent FLOAT NOT NULL,
    severity VARCHAR(20),  -- low, medium, high, critical
    
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed BOOLEAN DEFAULT FALSE,
    reviewed_by VARCHAR(255),
    reviewed_at TIMESTAMP,
    notes TEXT,
    
    INDEX idx_team_detected (team_id, detected_at DESC),
    INDEX idx_severity (severity),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- 2. Alerts Table
CREATE TABLE alerts (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    alert_type VARCHAR(50) NOT NULL,  -- anomaly_detected, threshold_crossed, peer_lagging
    
    title VARCHAR(255) NOT NULL,
    description TEXT,
    severity VARCHAR(20),  -- info, warning, critical
    
    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    acknowledged BOOLEAN DEFAULT FALSE,
    acknowledged_by VARCHAR(255),
    acknowledged_at TIMESTAMP,
    
    notification_sent_at TIMESTAMP,
    channels TEXT,  -- "email,slack,in-app"
    
    INDEX idx_team_triggered (team_id, triggered_at DESC),
    INDEX idx_type_severity (alert_type, severity),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- 3. Developer Metrics Table
CREATE TABLE developer_metrics (
    id VARCHAR(36) PRIMARY KEY,
    developer_id VARCHAR(255) NOT NULL,
    team_id VARCHAR(255) NOT NULL,
    
    security_contribution FLOAT DEFAULT 0,  -- -100 to +100
    complexity_contribution FLOAT DEFAULT 0,
    documentation_contribution FLOAT DEFAULT 0,
    testing_contribution FLOAT DEFAULT 0,
    dependencies_contribution FLOAT DEFAULT 0,
    maintainability_contribution FLOAT DEFAULT 0,
    
    overall_contribution FLOAT DEFAULT 0,
    
    calculated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_dev_team_date (developer_id, team_id, calculated_at),
    INDEX idx_team_date (team_id, calculated_at DESC),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- 4. Peer Groups Table
CREATE TABLE peer_groups (
    id VARCHAR(36) PRIMARY KEY,
    peer_group_name VARCHAR(255) NOT NULL,
    description TEXT,
    
    team_ids TEXT,  -- JSON array: ["team-001", "team-002", ...]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_peer_group_name (peer_group_name),
    INDEX idx_created (created_at)
);

-- 5. Benchmarks Table
CREATE TABLE benchmarks (
    id VARCHAR(36) PRIMARY KEY,
    benchmark_type VARCHAR(50) NOT NULL,  -- industry, peer_group, company
    
    dimension VARCHAR(50) NOT NULL,
    percentile_10 FLOAT,
    percentile_25 FLOAT,
    percentile_50 FLOAT,  -- median
    percentile_75 FLOAT,
    percentile_90 FLOAT,
    
    sample_size INT,
    calculated_at TIMESTAMP,
    
    UNIQUE KEY unique_benchmark (benchmark_type, dimension),
    INDEX idx_type (benchmark_type)
);

-- Indexes for performance
CREATE INDEX idx_anomalies_team_date ON anomalies(team_id, detected_at DESC);
CREATE INDEX idx_alerts_team_date ON alerts(team_id, triggered_at DESC);
CREATE INDEX idx_developer_metrics_team ON developer_metrics(team_id, calculated_at DESC);
CREATE INDEX idx_benchmarks_type ON benchmarks(benchmark_type, dimension);
```

#### 2. Updated ORM Models

**File:** `api/models/anomaly.py` (new)
```python
from sqlalchemy import Column, String, Float, DateTime, Boolean, ForeignKey
from api.db.database import Base

class Anomaly(Base):
    __tablename__ = "anomalies"
    
    id = Column(String, primary_key=True)
    team_id = Column(String, ForeignKey("team_scores.team_id", ondelete="CASCADE"), nullable=False)
    
    dimension = Column(String, nullable=False)  # security, complexity, etc.
    previous_score = Column(Float, nullable=False)
    current_score = Column(Float, nullable=False)
    change_percent = Column(Float, nullable=False)
    severity = Column(String)  # low, medium, high, critical
    
    detected_at = Column(DateTime, default=datetime.utcnow)
    reviewed = Column(Boolean, default=False)
    reviewed_by = Column(String)
    reviewed_at = Column(DateTime)
    notes = Column(String)
```

**File:** `api/models/alert.py` (new)
```python
class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(String, primary_key=True)
    team_id = Column(String, ForeignKey("team_scores.team_id", ondelete="CASCADE"), nullable=False)
    
    alert_type = Column(String, nullable=False)  # anomaly_detected, threshold_crossed, etc.
    title = Column(String, nullable=False)
    description = Column(String)
    severity = Column(String)  # info, warning, critical
    
    triggered_at = Column(DateTime, default=datetime.utcnow)
    acknowledged = Column(Boolean, default=False)
    acknowledged_by = Column(String)
    acknowledged_at = Column(DateTime)
    
    notification_sent_at = Column(DateTime)
    channels = Column(String)  # "email,slack,in-app"
```

**Similar models:**
- `api/models/developer_metric.py`
- `api/models/peer_group.py`
- `api/models/benchmark.py`

#### 3. Data Migration

```bash
# Option A: SQL Migration
psql codepulse_production < migrations/add_advanced_analytics_tables.sql

# Option B: Alembic
alembic revision --autogenerate -m "Add advanced analytics tables (anomalies, alerts, developer_metrics)"
alembic upgrade head
```

---

### Phase I+1.1: Anomaly Detection Service (5-6 hours)

**File:** `api/services/anomaly_detection.py`

```python
from datetime import datetime, timedelta
from api.db.database import SessionLocal
from api.models.anomaly import Anomaly
from api.models.team_score import TeamScore
from api.models.caqi_history import CAQIHistory

class AnomalyDetectionService:
    """Detect unexpected changes in team CAQI scores."""
    
    ANOMALY_THRESHOLDS = {
        'low': 5,      # 5% change
        'medium': 10,  # 10% change
        'high': 15,    # 15% change
        'critical': 20 # 20% change
    }
    
    @staticmethod
    def detect_anomalies(team_id: str, db: SessionLocal) -> List[Anomaly]:
        """
        Compare current score to 7-day average.
        Flag if difference > threshold.
        """
        # Get current score
        current = db.query(TeamScore).filter(
            TeamScore.team_id == team_id
        ).first()
        
        if not current:
            return []
        
        # Get 7-day history
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        history = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= seven_days_ago
        ).order_by(CAQIHistory.recorded_at).all()
        
        if not history:
            return []
        
        anomalies = []
        dimensions = ['security', 'complexity', 'documentation', 'testing', 'dependencies', 'maintainability']
        
        for dimension in dimensions:
            current_val = getattr(current, dimension)
            avg_historical = sum(getattr(h, dimension) for h in history) / len(history)
            
            # Calculate change percent
            if avg_historical == 0:
                change_percent = 0
            else:
                change_percent = ((current_val - avg_historical) / avg_historical) * 100
            
            # Check if anomaly
            abs_change = abs(change_percent)
            if abs_change > self.ANOMALY_THRESHOLDS['low']:
                # Determine severity
                if abs_change > self.ANOMALY_THRESHOLDS['critical']:
                    severity = 'critical'
                elif abs_change > self.ANOMALY_THRESHOLDS['high']:
                    severity = 'high'
                elif abs_change > self.ANOMALY_THRESHOLDS['medium']:
                    severity = 'medium'
                else:
                    severity = 'low'
                
                # Create anomaly record
                anomaly = Anomaly(
                    id=str(uuid.uuid4()),
                    team_id=team_id,
                    dimension=dimension,
                    previous_score=avg_historical,
                    current_score=current_val,
                    change_percent=change_percent,
                    severity=severity,
                    detected_at=datetime.utcnow()
                )
                db.add(anomaly)
                anomalies.append(anomaly)
        
        db.commit()
        return anomalies
    
    @staticmethod
    def get_unreviewed_anomalies(team_id: str, db: SessionLocal) -> List[Anomaly]:
        """Get anomalies that haven't been acknowledged yet."""
        return db.query(Anomaly).filter(
            Anomaly.team_id == team_id,
            Anomaly.reviewed == False
        ).order_by(Anomaly.detected_at.desc()).all()
    
    @staticmethod
    def mark_anomaly_reviewed(anomaly_id: str, reviewed_by: str, notes: str, db: SessionLocal):
        """Mark anomaly as reviewed by team lead."""
        anomaly = db.query(Anomaly).filter(Anomaly.id == anomaly_id).first()
        if anomaly:
            anomaly.reviewed = True
            anomaly.reviewed_by = reviewed_by
            anomaly.reviewed_at = datetime.utcnow()
            anomaly.notes = notes
            db.commit()
```

**Tests:** `tests/test_anomaly_detection.py` (6 test cases)
- Detect 10% drop in security score
- Ignore < 5% changes
- Mark critical (20%+) anomalies
- Get unreviewed anomalies
- Mark anomaly reviewed
- Handle no history gracefully

---

### Phase I+1.2: Peer Comparison Service (5-6 hours)

**File:** `api/services/peer_comparison.py`

```python
class PeerComparisonService:
    """Compare team CAQI to peer teams and benchmarks."""
    
    @staticmethod
    def create_peer_group(name: str, team_ids: List[str], db: SessionLocal) -> PeerGroup:
        """Create a peer group (e.g., 'backend-teams', 'frontend-teams')."""
        peer_group = PeerGroup(
            id=str(uuid.uuid4()),
            peer_group_name=name,
            team_ids=json.dumps(team_ids),
            created_at=datetime.utcnow()
        )
        db.add(peer_group)
        db.commit()
        return peer_group
    
    @staticmethod
    def get_peer_comparison(team_id: str, peer_group_name: str, db: SessionLocal) -> Dict:
        """Get team's CAQI vs. peer group averages."""
        # Get team score
        team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
        
        # Get peer group
        peer_group = db.query(PeerGroup).filter(
            PeerGroup.peer_group_name == peer_group_name
        ).first()
        
        peer_team_ids = json.loads(peer_group.team_ids)
        
        # Get peer scores
        peer_scores = db.query(TeamScore).filter(
            TeamScore.team_id.in_(peer_team_ids)
        ).all()
        
        if not peer_scores:
            return {}
        
        # Calculate peer averages
        dimensions = ['security', 'complexity', 'documentation', 'testing', 'dependencies', 'maintainability']
        peer_avgs = {}
        
        for dimension in dimensions:
            values = [getattr(s, dimension) for s in peer_scores]
            peer_avgs[dimension] = sum(values) / len(values)
        
        # Compare
        return {
            'team_id': team_id,
            'team_name': team.team_name,
            'team_caqi': team.overall_caqi,
            'peer_group': peer_group_name,
            'peer_count': len(peer_scores),
            'peer_avg_caqi': sum(s.overall_caqi for s in peer_scores) / len(peer_scores),
            'dimensions': {
                dimension: {
                    'team_score': getattr(team, dimension),
                    'peer_avg': peer_avgs[dimension],
                    'percentile': calculate_percentile(getattr(team, dimension), 
                                                       [getattr(s, dimension) for s in peer_scores])
                }
                for dimension in dimensions
            }
        }
    
    @staticmethod
    def calculate_benchmarks(benchmark_type: str, db: SessionLocal):
        """Calculate industry/company benchmarks from all teams."""
        teams = db.query(TeamScore).all()
        
        if not teams:
            return {}
        
        dimensions = ['security', 'complexity', 'documentation', 'testing', 'dependencies', 'maintainability']
        
        for dimension in dimensions:
            values = [getattr(t, dimension) for t in teams]
            values.sort()
            
            benchmark = Benchmark(
                id=str(uuid.uuid4()),
                benchmark_type=benchmark_type,
                dimension=dimension,
                percentile_10=values[int(len(values) * 0.1)],
                percentile_25=values[int(len(values) * 0.25)],
                percentile_50=values[int(len(values) * 0.5)],
                percentile_75=values[int(len(values) * 0.75)],
                percentile_90=values[int(len(values) * 0.9)],
                sample_size=len(teams),
                calculated_at=datetime.utcnow()
            )
            db.add(benchmark)
        
        db.commit()
```

**Tests:** `tests/test_peer_comparison.py` (6 test cases)
- Create peer group
- Get peer comparison
- Calculate percentiles
- Handle missing peers
- Update benchmarks
- Get benchmark data

---

### Phase I+1.3: Developer Drill-Down Service (5-6 hours)

**File:** `api/services/developer_drill_down.py`

```python
class DeveloperDrillDownService:
    """Attribute CAQI dimension changes to individual developers."""
    
    @staticmethod
    def calculate_developer_contributions(team_id: str, days: int = 30, db: SessionLocal) -> List[Dict]:
        """
        Estimate which developers drove dimension changes.
        
        Approach:
        1. Get team's metric data for each developer
        2. Compare developer's avg to team avg for each dimension
        3. Weight by team contribution to overall CAQI
        """
        # Get team members
        members = db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
        
        if not members:
            return []
        
        # Get metrics for each developer over last N days
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        developer_contributions = []
        
        for member in members:
            metrics = db.query(Metric).filter(
                Metric.developer_id == member.developer_id,
                Metric.team_id == team_id,
                Metric.recorded_at >= cutoff_date
            ).all()
            
            if not metrics:
                continue
            
            # Average developer metrics
            dimensions = ['security', 'complexity', 'documentation', 'testing', 'dependencies', 'maintainability']
            
            dev_contribution = {
                'developer_id': member.developer_id,
                'team_id': team_id,
                'contributions': {}
            }
            
            for dimension in dimensions:
                dev_avg = sum(getattr(m, dimension) for m in metrics) / len(metrics)
                
                # Get team average for dimension
                team_metrics = db.query(Metric).filter(
                    Metric.team_id == team_id,
                    Metric.recorded_at >= cutoff_date
                ).all()
                
                team_avg = sum(getattr(m, dimension) for m in team_metrics) / len(team_metrics) if team_metrics else 0
                
                # Calculate contribution (deviation from team average)
                contribution = dev_avg - team_avg
                
                dev_contribution['contributions'][dimension] = {
                    'developer_score': dev_avg,
                    'team_avg': team_avg,
                    'contribution': contribution
                }
            
            # Calculate overall contribution
            overall = sum(v['contribution'] for v in dev_contribution['contributions'].values()) / len(dimensions)
            dev_contribution['overall_contribution'] = overall
            
            developer_contributions.append(dev_contribution)
        
        # Sort by overall contribution (highest impact first)
        return sorted(developer_contributions, key=lambda x: abs(x['overall_contribution']), reverse=True)
    
    @staticmethod
    def get_top_contributors(team_id: str, dimension: str, limit: int = 5, db: SessionLocal) -> List[Dict]:
        """Get developers who most improve a specific dimension."""
        # Similar to above but filtered to one dimension
        pass
```

**Tests:** `tests/test_developer_drill_down.py` (5 test cases)
- Calculate developer contributions
- Identify top contributors
- Handle single developer team
- Filter by dimension
- Handle no metrics gracefully

---

### Phase I+1.4: Alerting Service (4-5 hours)

**File:** `api/services/alerting_service.py`

```python
class AlertingService:
    """Create and send alerts for anomalies and threshold crossings."""
    
    @staticmethod
    def create_alert(team_id: str, alert_type: str, title: str, description: str, 
                    severity: str, db: SessionLocal) -> Alert:
        """Create an alert."""
        alert = Alert(
            id=str(uuid.uuid4()),
            team_id=team_id,
            alert_type=alert_type,
            title=title,
            description=description,
            severity=severity,
            triggered_at=datetime.utcnow()
        )
        db.add(alert)
        db.commit()
        return alert
    
    @staticmethod
    def send_alert(alert_id: str, channels: List[str], db: SessionLocal):
        """
        Send alert via multiple channels.
        
        channels: ['email', 'slack', 'in-app']
        """
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        
        if not alert:
            return False
        
        # Get team and team lead email
        team = db.query(TeamScore).filter(TeamScore.team_id == alert.team_id).first()
        
        try:
            if 'email' in channels:
                send_email_alert(alert, team)
            
            if 'slack' in channels:
                send_slack_alert(alert, team)
            
            if 'in-app' in channels:
                # Mark as notification (frontend will show)
                pass
            
            # Update alert
            alert.notification_sent_at = datetime.utcnow()
            alert.channels = ','.join(channels)
            db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Failed to send alert {alert_id}: {e}")
            return False
    
    @staticmethod
    def acknowledge_alert(alert_id: str, acknowledged_by: str, db: SessionLocal):
        """Team lead acknowledges alert."""
        alert = db.query(Alert).filter(Alert.id == alert_id).first()
        if alert:
            alert.acknowledged = True
            alert.acknowledged_by = acknowledged_by
            alert.acknowledged_at = datetime.utcnow()
            db.commit()
```

**Tests:** `tests/test_alerting_service.py` (5 test cases)
- Create alert
- Send email alert
- Send Slack alert
- Acknowledge alert
- Get pending alerts

---

### Phase I+1.5: REST API Endpoints (4-5 hours)

**File:** `api/routes/advanced_analytics.py` (new)

```python
from fastapi import APIRouter, HTTPException, Query
from api.services.anomaly_detection import AnomalyDetectionService
from api.services.peer_comparison import PeerComparisonService
from api.services.developer_drill_down import DeveloperDrillDownService
from api.services.alerting_service import AlertingService

router = APIRouter(prefix="/api/v1/caqi", tags=["advanced-analytics"])

@router.get("/anomalies/{team_id}")
async def get_anomalies(team_id: str, db: SessionLocal = Depends(get_db)):
    """Get detected anomalies for a team."""
    anomalies = AnomalyDetectionService.get_unreviewed_anomalies(team_id, db)
    return {
        'team_id': team_id,
        'count': len(anomalies),
        'anomalies': [
            {
                'id': a.id,
                'dimension': a.dimension,
                'previous_score': a.previous_score,
                'current_score': a.current_score,
                'change_percent': a.change_percent,
                'severity': a.severity,
                'detected_at': a.detected_at
            }
            for a in anomalies
        ]
    }

@router.post("/anomalies/{anomaly_id}/review")
async def review_anomaly(anomaly_id: str, reviewed_by: str, notes: str, db: SessionLocal = Depends(get_db)):
    """Mark anomaly as reviewed."""
    AnomalyDetectionService.mark_anomaly_reviewed(anomaly_id, reviewed_by, notes, db)
    return {'status': 'reviewed', 'anomaly_id': anomaly_id}

@router.get("/peer-comparison/{team_id}")
async def get_peer_comparison(team_id: str, peer_group: str = Query(...), db: SessionLocal = Depends(get_db)):
    """Compare team to peer group."""
    comparison = PeerComparisonService.get_peer_comparison(team_id, peer_group, db)
    return comparison

@router.get("/benchmarks")
async def get_benchmarks(benchmark_type: str = 'company', db: SessionLocal = Depends(get_db)):
    """Get industry/company benchmarks."""
    benchmarks = db.query(Benchmark).filter(Benchmark.benchmark_type == benchmark_type).all()
    return {
        'benchmark_type': benchmark_type,
        'benchmarks': [
            {
                'dimension': b.dimension,
                'p10': b.percentile_10,
                'p25': b.percentile_25,
                'p50': b.percentile_50,
                'p75': b.percentile_75,
                'p90': b.percentile_90,
                'sample_size': b.sample_size
            }
            for b in benchmarks
        ]
    }

@router.get("/developer-metrics/{team_id}")
async def get_developer_metrics(team_id: str, days: int = Query(30), db: SessionLocal = Depends(get_db)):
    """Get developer contributions to CAQI changes."""
    contributions = DeveloperDrillDownService.calculate_developer_contributions(team_id, days, db)
    return {
        'team_id': team_id,
        'days': days,
        'developer_count': len(contributions),
        'developers': contributions
    }

@router.get("/alerts/{team_id}")
async def get_alerts(team_id: str, unacknowledged_only: bool = True, db: SessionLocal = Depends(get_db)):
    """Get alerts for a team."""
    query = db.query(Alert).filter(Alert.team_id == team_id)
    
    if unacknowledged_only:
        query = query.filter(Alert.acknowledged == False)
    
    alerts = query.order_by(Alert.triggered_at.desc()).all()
    
    return {
        'team_id': team_id,
        'count': len(alerts),
        'alerts': [
            {
                'id': a.id,
                'type': a.alert_type,
                'title': a.title,
                'severity': a.severity,
                'triggered_at': a.triggered_at,
                'acknowledged': a.acknowledged
            }
            for a in alerts
        ]
    }

@router.post("/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, acknowledged_by: str, db: SessionLocal = Depends(get_db)):
    """Acknowledge an alert."""
    AlertingService.acknowledge_alert(alert_id, acknowledged_by, db)
    return {'status': 'acknowledged', 'alert_id': alert_id}
```

**API Endpoints Summary:**
```
POST   /api/v1/caqi/anomalies/{team_id}           → Get anomalies
POST   /api/v1/caqi/anomalies/{anomaly_id}/review → Mark reviewed
GET    /api/v1/caqi/peer-comparison/{team_id}     → Peer comparison
GET    /api/v1/caqi/benchmarks                     → Get benchmarks
GET    /api/v1/caqi/developer-metrics/{team_id}   → Developer contributions
GET    /api/v1/caqi/alerts/{team_id}              → Get alerts
POST   /api/v1/caqi/alerts/{alert_id}/acknowledge → Acknowledge alert
```

**Tests:** `tests/test_advanced_analytics_api.py` (7 test cases)
- Get anomalies for team
- Review anomaly
- Get peer comparison
- Get benchmarks
- Get developer metrics
- Get alerts
- Acknowledge alert

---

### Phase I+1.6: Background Jobs (3-4 hours)

**File:** `api/tasks/anomaly_detection_tasks.py` (new)

```python
from celery import shared_task
from api.services.anomaly_detection import AnomalyDetectionService
from api.services.alerting_service import AlertingService
from api.db.database import SessionLocal

@shared_task
def detect_anomalies_daily():
    """Run daily anomaly detection for all teams."""
    db = SessionLocal()
    
    try:
        teams = db.query(TeamScore).all()
        
        for team in teams:
            anomalies = AnomalyDetectionService.detect_anomalies(team.team_id, db)
            
            for anomaly in anomalies:
                # Create alert for critical anomalies
                if anomaly.severity in ['high', 'critical']:
                    alert = AlertingService.create_alert(
                        team_id=team.team_id,
                        alert_type='anomaly_detected',
                        title=f'{anomaly.dimension.title()} Score Drop Detected',
                        description=f'{anomaly.dimension.title()} dropped {anomaly.change_percent:.1f}% (from {anomaly.previous_score:.0f} to {anomaly.current_score:.0f})',
                        severity=anomaly.severity,
                        db=db
                    )
                    
                    # Send alert
                    AlertingService.send_alert(alert.id, ['email', 'slack'], db)
        
        return {'status': 'success', 'teams_checked': len(teams)}
    
    finally:
        db.close()

@shared_task
def recalculate_benchmarks_weekly():
    """Recalculate benchmarks weekly (every Monday)."""
    db = SessionLocal()
    
    try:
        PeerComparisonService.calculate_benchmarks('company', db)
        return {'status': 'success', 'benchmarks_updated': 6}
    
    finally:
        db.close()
```

**Celery Beat Schedule:**
```python
# config/celery_config.py
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'detect-anomalies-daily': {
        'task': 'api.tasks.anomaly_detection_tasks.detect_anomalies_daily',
        'schedule': crontab(hour=2, minute=0),  # 2 AM daily
    },
    'recalculate-benchmarks-weekly': {
        'task': 'api.tasks.anomaly_detection_tasks.recalculate_benchmarks_weekly',
        'schedule': crontab(day_of_week=1, hour=3, minute=0),  # Monday 3 AM
    },
}
```

---

### Phase I+1.7: Frontend Components (5-6 hours)

**Component 1:** `frontend/src/components/AnomalyDetectionView.tsx`

```tsx
import React, { useEffect, useState } from 'react';
import { Alert, AlertCircle, CheckCircle } from 'lucide-react';

interface AnomalyDetectionViewProps {
  teamId: string;
}

export const AnomalyDetectionView: React.FC<AnomalyDetectionViewProps> = ({ teamId }) => {
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnomalies();
  }, [teamId]);

  const fetchAnomalies = async () => {
    try {
      const response = await fetch(`/api/v1/caqi/anomalies/${teamId}`);
      const data = await response.json();
      setAnomalies(data.anomalies);
    } finally {
      setLoading(false);
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#dc2626';
      case 'high': return '#f97316';
      case 'medium': return '#eab308';
      case 'low': return '#3b82f6';
      default: return '#6b7280';
    }
  };

  if (loading) return <div>Loading anomalies...</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h2>Anomaly Detection</h2>
      {anomalies.length === 0 ? (
        <p>✅ No anomalies detected</p>
      ) : (
        <div>
          {anomalies.map(anomaly => (
            <div
              key={anomaly.id}
              style={{
                borderLeft: `4px solid ${getSeverityColor(anomaly.severity)}`,
                padding: '12px',
                marginBottom: '12px',
                backgroundColor: '#f3f4f6'
              }}
            >
              <div style={{ fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px' }}>
                <AlertCircle size={18} color={getSeverityColor(anomaly.severity)} />
                {anomaly.dimension.charAt(0).toUpperCase() + anomaly.dimension.slice(1)} Drop
              </div>
              <p style={{ margin: '4px 0', fontSize: '14px' }}>
                {anomaly.previous_score.toFixed(1)} → {anomaly.current_score.toFixed(1)}
                <span style={{ color: '#ef4444', marginLeft: '8px' }}>
                  ({anomaly.change_percent > 0 ? '+' : ''}{anomaly.change_percent.toFixed(1)}%)
                </span>
              </p>
              <small style={{ color: '#6b7280' }}>
                {new Date(anomaly.detected_at).toLocaleDateString()}
              </small>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
```

**Component 2:** `frontend/src/components/PeerComparisonChart.tsx` (similar structure)

**Component 3:** `frontend/src/components/DeveloperBreakdownTable.tsx` (similar structure)

**Tests:** `frontend/src/__tests__/AnomalyDetectionView.test.tsx` (5 test cases)
- Render anomalies
- Display severity colors
- Handle no anomalies
- Format date correctly
- Display change percentage

---

### Phase I+1.8: Testing & Quality (3-4 hours)

**Test Coverage Target:** 85% (new files)

**Test Files:**
1. `tests/test_anomaly_detection.py` (6 tests)
2. `tests/test_peer_comparison.py` (6 tests)
3. `tests/test_developer_drill_down.py` (5 tests)
4. `tests/test_alerting_service.py` (5 tests)
5. `tests/test_advanced_analytics_api.py` (7 tests)
6. `frontend/src/__tests__/AnomalyDetectionView.test.tsx` (5 tests)
7. `frontend/src/__tests__/PeerComparisonChart.test.tsx` (5 tests)
8. `frontend/src/__tests__/DeveloperBreakdownTable.test.tsx` (5 tests)

**Total: 44 new tests**

**Quality Metrics:**
```
New Backend Tests:   24
New Frontend Tests:  15
New E2E Tests:       5
Total New Tests:     44

Target Coverage: 85% (statements)
Expected Time: 3-4 hours
```

---

## Deployment Checklist (Phase I+1)

### Pre-Deployment (3-4 days before)

- [ ] All 44 new tests passing
- [ ] Code review completed
- [ ] Performance tested (< 200ms anomaly detection per team)
- [ ] Database migration tested on staging
- [ ] Alerting channels configured (email, Slack)
- [ ] Celery/Redis running

### Deployment Day

1. **Database**
   ```bash
   alembic upgrade head
   # Or: psql codepulse_production < migrations/add_advanced_analytics.sql
   ```

2. **Backend**
   ```bash
   pip install -r requirements.txt
   systemctl restart codepulse-api
   systemctl restart codepulse-celery  # For background jobs
   ```

3. **Frontend**
   ```bash
   npm run build
   # Deploy build/ to production
   ```

4. **Verify**
   ```bash
   curl http://api.example.com/api/v1/caqi/anomalies/team-001
   curl http://api.example.com/api/v1/caqi/peer-comparison/team-001?peer_group=backend
   curl http://api.example.com/api/v1/caqi/developer-metrics/team-001
   ```

5. **Test Alerts**
   ```bash
   # Manually trigger test alert
   python3 << 'EOF'
   from api.services.alerting_service import AlertingService
   from api.db.database import SessionLocal
   
   db = SessionLocal()
   AlertingService.create_alert(
       team_id='team-001',
       alert_type='test',
       title='Test Alert',
       description='This is a test alert',
       severity='info',
       db=db
   )
   EOF
   ```

### Post-Deployment (First Week)

- [ ] Anomalies detected correctly (day 1)
- [ ] No alert spam (< 2 alerts per team per day)
- [ ] Peer comparisons accurate
- [ ] Developer metrics reasonable
- [ ] Background jobs running (check logs)
- [ ] Celery tasks completing successfully

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| I+1.0 | 3-4h | Database schema, ORM models |
| I+1.1 | 5-6h | Anomaly detection service |
| I+1.2 | 5-6h | Peer comparison service |
| I+1.3 | 5-6h | Developer drill-down service |
| I+1.4 | 4-5h | Alerting service |
| I+1.5 | 4-5h | REST API (5 endpoints) |
| I+1.6 | 3-4h | Background jobs (2 Celery tasks) |
| I+1.7 | 5-6h | Frontend components (3) |
| I+1.8 | 3-4h | Testing & quality |
| **TOTAL** | **20-30h** | **Production-ready** |

---

## Success Criteria

✅ **Code Quality:**
- 44 new tests, 100% passing
- 85% code coverage (new files)
- 0 TypeScript errors
- 0 security issues

✅ **Performance:**
- Anomaly detection < 200ms per team
- API endpoints < 500ms
- Peer comparisons < 300ms
- Background jobs < 5s per team

✅ **Functionality:**
- Anomalies detected daily
- Alerts sent (email + Slack)
- Peer comparison working
- Developer contributions calculated
- Frontend displays data correctly

✅ **Reliability:**
- Celery jobs complete successfully
- No alert spam (< 2/team/day)
- Background jobs logged
- Error handling graceful

---

## Post-Phase I+1: Next Steps

**Phase I+2: Culture Interventions (15-20 hours)**
- Suggestion engine (per archetype)
- A/B testing framework (branch vs. main)
- Gamification (badges, leaderboards)
- Team improvement tracking

**Phase I+3: Export & Reporting (10-15 hours)**
- PDF report generation
- Email digests (weekly/monthly)
- Slack integrations
- Executive dashboard

---

## Resources

**Related Documentation:**
- `PATH_I_CAQI_ENHANCED_IMPLEMENTATION_PLAN.md` — Phase I plan
- `DEPLOYMENT_SETUP.md` — Local setup guide
- `DATABASE_MIGRATION.md` — Migration strategy
- `TEST_RESULTS_SUMMARY.md` — Phase I test results

**Dependencies:**
- Phase I.0-I.5 deployed and working
- Celery + Redis running
- Email service configured
- Slack webhook available

---

**Status:** Ready to implement  
**Estimated Start:** 1 week after Phase I deployment  
**Estimated Completion:** 2-3 weeks (20-30 hours)
