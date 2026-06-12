---
created_at: 2026-06-12T18:16:43Z
title: Phase I+3 Export Reporting Implementation Plan
source: claude-code
project: codescanner
---

# Phase I+3: Export & Reporting - Implementation Plan

**Project:** CODEPULSE AI - Path I Export & Reporting  
**Feature:** PDF Reports, Email Digests, Slack Integration, Executive Dashboard  
**Status:** Planning  
**Timeline:** 10-15 hours of development  
**Target Completion:** 1-2 weeks (after Phase I+2 deployment)  
**Dependencies:** Phase I.0-I.5 + Phase I+1 + Phase I+2 complete and deployed

---

## Executive Summary

Transform insights into **actionable reports** for different stakeholders:

1. **PDF Reports** — Download trend analysis, culture snapshots, improvement history
2. **Email Digests** — Weekly/monthly summaries automatically sent to team leads
3. **Slack Integration** — Real-time alerts and daily digest messages
4. **Executive Dashboard** — High-level company CAQI, trends, and peer benchmarks

**Impact:** Executives see company health at a glance. Team leads get weekly actionable insights. Teams stay informed without logging into dashboards.

---

## Architecture Overview

### Current Path I+2 Structure (Post-Culture Interventions)
```
Path I+2: Culture Interventions (Deployed)
├── Suggestions ✅
├── Interventions ✅
├── A/B Testing ✅
└── Gamification ✅
```

### Phase I+3 Enhanced Structure
```
Path I+3: Export & Reporting (New)
├── Backend Services
│   ├── ReportGenerationService (new)
│   │   ├── PDF rendering (ReportLab)
│   │   ├── CSV export
│   │   └── JSON serialization
│   ├── EmailDigestService (new)
│   │   ├── Weekly digest templates
│   │   ├── Monthly digest templates
│   │   └── Scheduled send
│   ├── SlackIntegrationService (new)
│   │   ├── Webhook notifications
│   │   ├── Interactive messages
│   │   └── Digest posting
│   └── ExecutiveDashboardService (new)
│       ├── Company-level aggregation
│       ├── Department summaries
│       └── Trend comparisons
├── REST API (6 new endpoints)
│   ├── /api/v1/caqi/reports/team/{team_id}/pdf
│   ├── /api/v1/caqi/reports/team/{team_id}/csv
│   ├── /api/v1/caqi/reports/executive
│   ├── /api/v1/caqi/digests/{team_id}/configure
│   ├── /api/v1/caqi/integrations/slack/setup
│   └── /api/v1/caqi/integrations/slack/status
├── Frontend Components (2 new)
│   ├── ReportDownloadPanel
│   └── ExecutiveDashboard
├── Background Jobs (3 new)
│   ├── WeeklyDigestJob
│   ├── MonthlyDigestJob
│   └── SlackDailyDigestJob
└── Data Tables (2 new)
    ├── email_digest_subscriptions
    └── slack_integrations
```

---

## Phase Breakdown

### Phase I+3.0: Data & Schema (2-3 hours)

#### 1. Database Schema Extensions

```sql
-- 1. Email Digest Subscriptions
CREATE TABLE email_digest_subscriptions (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    
    recipient_email VARCHAR(255) NOT NULL,
    recipient_name VARCHAR(255),
    role VARCHAR(50),  -- team_lead, engineer, manager, executive
    
    digest_frequency VARCHAR(20) NOT NULL,  -- weekly, monthly, none
    digest_day INT,  -- 0=Sunday, 1=Monday, etc.
    digest_time VARCHAR(10),  -- HH:MM format
    
    include_suggestions BOOLEAN DEFAULT TRUE,
    include_interventions BOOLEAN DEFAULT TRUE,
    include_anomalies BOOLEAN DEFAULT TRUE,
    include_badges BOOLEAN DEFAULT TRUE,
    include_leaderboard BOOLEAN DEFAULT FALSE,
    
    last_sent_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    INDEX idx_team_email (team_id, recipient_email),
    INDEX idx_next_send (digest_frequency, digest_day),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- 2. Slack Integrations
CREATE TABLE slack_integrations (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    
    workspace_name VARCHAR(255) NOT NULL,
    channel_id VARCHAR(255) NOT NULL,
    channel_name VARCHAR(255),
    webhook_url VARCHAR(255) NOT NULL,  -- Encrypted
    
    enabled BOOLEAN DEFAULT TRUE,
    
    -- Notification preferences
    notify_anomalies BOOLEAN DEFAULT TRUE,
    notify_alerts BOOLEAN DEFAULT TRUE,
    notify_suggestion_accepted BOOLEAN DEFAULT TRUE,
    notify_badges BOOLEAN DEFAULT TRUE,
    notify_daily_digest BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    installed_by VARCHAR(255),
    installed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_notified_at TIMESTAMP,
    
    INDEX idx_team_channel (team_id, channel_id),
    INDEX idx_enabled (enabled),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- 3. Report Exports Log
CREATE TABLE report_exports (
    id VARCHAR(36) PRIMARY KEY,
    team_id VARCHAR(255) NOT NULL,
    
    report_type VARCHAR(50) NOT NULL,  -- trend_analysis, culture_snapshot, improvement_history, executive
    format VARCHAR(20) NOT NULL,  -- pdf, csv, json
    
    generated_by VARCHAR(255),
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    file_size_bytes INT,
    download_count INT DEFAULT 0,
    last_downloaded_at TIMESTAMP,
    
    retention_days INT DEFAULT 90,
    
    INDEX idx_team_type (team_id, report_type),
    INDEX idx_generated (generated_at DESC),
    FOREIGN KEY (team_id) REFERENCES team_scores(team_id) ON DELETE CASCADE
);

-- Indexes for performance
CREATE INDEX idx_digest_subscriptions_team ON email_digest_subscriptions(team_id, digest_frequency);
CREATE INDEX idx_slack_integrations_team ON slack_integrations(team_id, enabled);
CREATE INDEX idx_report_exports_team ON report_exports(team_id, generated_at DESC);
```

#### 2. Updated ORM Models

```python
# api/models/email_digest_subscription.py
class EmailDigestSubscription(Base):
    __tablename__ = "email_digest_subscriptions"
    
    id = Column(String, primary_key=True)
    team_id = Column(String, ForeignKey("team_scores.team_id", ondelete="CASCADE"), nullable=False)
    
    recipient_email = Column(String, nullable=False)
    recipient_name = Column(String)
    role = Column(String)
    
    digest_frequency = Column(String, nullable=False)
    digest_day = Column(Integer)
    digest_time = Column(String)
    
    include_suggestions = Column(Boolean, default=True)
    include_interventions = Column(Boolean, default=True)
    include_anomalies = Column(Boolean, default=True)
    include_badges = Column(Boolean, default=True)
    include_leaderboard = Column(Boolean, default=False)
    
    last_sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# api/models/slack_integration.py, report_export.py
# (Similar structure)
```

---

### Phase I+3.1: Report Generation Service (3-4 hours)

**File:** `api/services/report_generation.py`

```python
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import csv

class ReportGenerationService:
    """Generate PDF, CSV, and JSON reports of CAQI data."""
    
    @staticmethod
    def generate_trend_report_pdf(team_id: str, days: int = 90, db: SessionLocal) -> BytesIO:
        """Generate PDF trend analysis report."""
        
        team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
        history = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= datetime.utcnow() - timedelta(days=days)
        ).order_by(CAQIHistory.recorded_at).all()
        
        if not team or not history:
            raise ValueError(f"No data found for team {team_id}")
        
        # Create PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30
        )
        
        # Title
        story.append(Paragraph(f"CAQI Trend Report: {team.team_name}", title_style))
        story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%B %d, %Y')}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Summary
        story.append(Paragraph("Summary", styles['Heading2']))
        summary_data = [
            ['Metric', 'Current', 'Average', 'Trend'],
            ['Overall CAQI', f"{team.overall_caqi:.0f}", f"{sum(h.overall_caqi for h in history)/len(history):.0f}", 'up'],
            ['Security', f"{team.security:.0f}", f"{sum(h.security for h in history)/len(history):.0f}", 'stable'],
            ['Complexity', f"{team.complexity:.0f}", f"{sum(h.complexity for h in history)/len(history):.0f}", 'down'],
            # ... more dimensions
        ]
        
        summary_table = Table(summary_data)
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # History Table
        story.append(Paragraph("90-Day History", styles['Heading2']))
        history_data = [['Date', 'CAQI', 'Security', 'Complexity', 'Documentation', 'Testing', 'Dependencies', 'Maintainability']]
        
        for h in history[-30:]:  # Last 30 days for brevity
            history_data.append([
                h.recorded_at.strftime('%m/%d'),
                f"{h.overall_caqi:.0f}",
                f"{h.security:.0f}",
                f"{h.complexity:.0f}",
                f"{h.documentation:.0f}",
                f"{h.testing:.0f}",
                f"{h.dependencies:.0f}",
                f"{h.maintainability:.0f}",
            ])
        
        history_table = Table(history_data)
        history_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#374151')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
        ]))
        story.append(history_table)
        
        # Build PDF
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_culture_snapshot_pdf(team_id: str, db: SessionLocal) -> BytesIO:
        """Generate PDF snapshot of team culture (archetype, badges, streaks)."""
        
        team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
        badges = db.query(Badge).filter(Badge.team_id == team_id).all()
        streaks = db.query(ImprovementStreak).filter(
            ImprovementStreak.team_id == team_id,
            ImprovementStreak.status == 'active'
        ).all()
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        styles = getSampleStyleSheet()
        
        # Similar structure to trend_report_pdf but focused on culture metrics
        story.append(Paragraph(f"Culture Snapshot: {team.team_name}", styles['Heading1']))
        story.append(Paragraph(f"Archetype: {team.personality_archetype}", styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Badges section
        story.append(Paragraph("Recent Badges", styles['Heading2']))
        badges_text = ', '.join([b.badge_name for b in badges[-5:]]) if badges else "No badges yet"
        story.append(Paragraph(badges_text, styles['Normal']))
        story.append(Spacer(1, 12))
        
        # Streaks section
        story.append(Paragraph("Active Improvement Streaks", styles['Heading2']))
        for streak in streaks:
            story.append(Paragraph(f"• {streak.days_in_streak}-day streak on {streak.dimension or 'overall'}", styles['Normal']))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_csv_export(team_id: str, days: int = 90, db: SessionLocal) -> BytesIO:
        """Generate CSV export of team CAQI history."""
        
        history = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= datetime.utcnow() - timedelta(days=days)
        ).order_by(CAQIHistory.recorded_at).all()
        
        buffer = BytesIO()
        wrapper = TextIOWrapper(buffer, encoding='utf-8', write_through=True)
        writer = csv.writer(wrapper)
        
        # Header
        writer.writerow([
            'Date', 'Overall CAQI', 'Security', 'Complexity', 'Documentation',
            'Testing', 'Dependencies', 'Maintainability'
        ])
        
        # Data rows
        for h in history:
            writer.writerow([
                h.recorded_at.strftime('%Y-%m-%d'),
                h.overall_caqi,
                h.security,
                h.complexity,
                h.documentation,
                h.testing,
                h.dependencies,
                h.maintainability
            ])
        
        wrapper.flush()
        buffer.seek(0)
        return buffer
    
    @staticmethod
    def generate_json_export(team_id: str, days: int = 90, db: SessionLocal) -> Dict:
        """Generate JSON export of team data."""
        
        team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
        history = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= datetime.utcnow() - timedelta(days=days)
        ).order_by(CAQIHistory.recorded_at).all()
        
        return {
            'team_id': team.team_id,
            'team_name': team.team_name,
            'archetype': team.personality_archetype,
            'current_caqi': team.overall_caqi,
            'current_dimensions': {
                'security': team.security,
                'complexity': team.complexity,
                'documentation': team.documentation,
                'testing': team.testing,
                'dependencies': team.dependencies,
                'maintainability': team.maintainability
            },
            'history': [
                {
                    'date': h.recorded_at.strftime('%Y-%m-%d'),
                    'overall_caqi': h.overall_caqi,
                    'dimensions': {
                        'security': h.security,
                        'complexity': h.complexity,
                        'documentation': h.documentation,
                        'testing': h.testing,
                        'dependencies': h.dependencies,
                        'maintainability': h.maintainability
                    }
                }
                for h in history
            ],
            'generated_at': datetime.utcnow().isoformat()
        }
```

**Tests:** `tests/test_report_generation.py` (6 test cases)
- Generate trend PDF
- Generate culture snapshot PDF
- Generate CSV export
- Generate JSON export
- Handle missing data gracefully
- File format validation

---

### Phase I+3.2: Email Digest Service (3-4 hours)

**File:** `api/services/email_digest_service.py`

```python
from jinja2 import Template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailDigestService:
    """Generate and send email digests (weekly/monthly)."""
    
    WEEKLY_DIGEST_TEMPLATE = """
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2>Weekly CAQI Digest: {{ team_name }}</h2>
            <p>Week of {{ week_start }} - {{ week_end }}</p>
            
            <h3>📊 Current Status</h3>
            <ul>
                <li><strong>Overall CAQI:</strong> {{ current_caqi }}/500</li>
                <li><strong>Archetype:</strong> {{ archetype }}</li>
                <li><strong>Weekly Change:</strong> {{ weekly_change }}%</li>
            </ul>
            
            {% if anomalies %}
            <h3>⚠️ Anomalies Detected</h3>
            <ul>
            {% for anomaly in anomalies %}
                <li>{{ anomaly.dimension }}: {{ anomaly.change_percent }}% drop ({{ anomaly.severity }})</li>
            {% endfor %}
            </ul>
            {% endif %}
            
            {% if suggestions %}
            <h3>💡 New Suggestions</h3>
            <ul>
            {% for suggestion in suggestions %}
                <li><strong>{{ suggestion.dimension }}</strong>: {{ suggestion.suggestion_text }}</li>
            {% endfor %}
            </ul>
            {% endif %}
            
            {% if interventions %}
            <h3>✅ Interventions in Progress</h3>
            <ul>
            {% for intervention in interventions %}
                <li>{{ intervention.title }} ({{ intervention.status }})</li>
            {% endfor %}
            </ul>
            {% endif %}
            
            {% if badges %}
            <h3>🏅 New Badges</h3>
            <p>{{ badges | join(', ') }}</p>
            {% endif %}
            
            <hr>
            <p><a href="https://example.com/dashboard/{{ team_id }}">View Full Dashboard</a></p>
            <p style="font-size: 12px; color: #999;">
                You received this email because you're subscribed to {{ team_name }} digest.
                <a href="https://example.com/unsubscribe/{{ subscription_id }}">Unsubscribe</a>
            </p>
        </body>
    </html>
    """
    
    @staticmethod
    def generate_weekly_digest(team_id: str, db: SessionLocal) -> Dict:
        """Generate weekly digest content."""
        
        team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
        
        # Get this week's data
        week_start = datetime.utcnow() - timedelta(days=7)
        week_end = datetime.utcnow()
        
        history = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= week_start,
            CAQIHistory.recorded_at <= week_end
        ).order_by(CAQIHistory.recorded_at).all()
        
        week_start_score = history[0].overall_caqi if history else 0
        week_end_score = history[-1].overall_caqi if history else 0
        weekly_change = ((week_end_score - week_start_score) / week_start_score * 100) if week_start_score > 0 else 0
        
        # Get anomalies, suggestions, interventions, badges from this week
        anomalies = db.query(Anomaly).filter(
            Anomaly.team_id == team_id,
            Anomaly.detected_at >= week_start
        ).all()
        
        suggestions = db.query(Suggestion).filter(
            Suggestion.team_id == team_id,
            Suggestion.created_at >= week_start,
            Suggestion.status == 'pending'
        ).all()
        
        interventions = db.query(Intervention).filter(
            Intervention.team_id == team_id,
            Intervention.status.in_(['in_progress', 'completed']),
            Intervention.created_at >= week_start
        ).all()
        
        badges = db.query(Badge).filter(
            Badge.team_id == team_id,
            Badge.awarded_at >= week_start
        ).all()
        
        return {
            'team_name': team.team_name,
            'team_id': team_id,
            'current_caqi': team.overall_caqi,
            'archetype': team.personality_archetype,
            'weekly_change': weekly_change,
            'week_start': week_start.strftime('%B %d'),
            'week_end': week_end.strftime('%B %d'),
            'anomalies': anomalies,
            'suggestions': suggestions,
            'interventions': interventions,
            'badges': [b.badge_name for b in badges]
        }
    
    @staticmethod
    def send_digest(team_id: str, subscription_id: str, recipient_email: str, 
                   digest_type: str, db: SessionLocal) -> bool:
        """Send digest email."""
        
        # Generate content
        if digest_type == 'weekly':
            content = EmailDigestService.generate_weekly_digest(team_id, db)
        else:
            # monthly
            content = EmailDigestService.generate_monthly_digest(team_id, db)
        
        # Render template
        template = Template(EmailDigestService.WEEKLY_DIGEST_TEMPLATE)
        html_body = template.render(**content, subscription_id=subscription_id)
        
        # Send email
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Weekly CAQI Digest: {content['team_name']}"
            msg['From'] = os.getenv('EMAIL_FROM', 'noreply@codepulse.ai')
            msg['To'] = recipient_email
            
            msg.attach(MIMEText(html_body, 'html'))
            
            # Send via SMTP
            with smtplib.SMTP(os.getenv('SMTP_HOST'), int(os.getenv('SMTP_PORT', 587))) as server:
                server.starttls()
                server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
                server.send_message(msg)
            
            # Update last sent
            subscription = db.query(EmailDigestSubscription).filter(
                EmailDigestSubscription.id == subscription_id
            ).first()
            if subscription:
                subscription.last_sent_at = datetime.utcnow()
                db.commit()
            
            return True
        except Exception as e:
            logger.error(f"Failed to send digest {subscription_id}: {e}")
            return False
    
    @staticmethod
    def generate_monthly_digest(team_id: str, db: SessionLocal) -> Dict:
        """Generate monthly digest content (similar to weekly but aggregated)."""
        # Implementation similar to weekly_digest but for 30-day period
        pass
```

**Tests:** `tests/test_email_digest_service.py` (5 test cases)
- Generate weekly digest
- Generate monthly digest
- Send digest email
- Update last_sent_at
- Handle missing SMTP config

---

### Phase I+3.3: Slack Integration Service (3-4 hours)

**File:** `api/services/slack_integration_service.py`

```python
import requests
import hmac
import hashlib

class SlackIntegrationService:
    """Send notifications and digests to Slack."""
    
    @staticmethod
    def send_notification(team_id: str, message: str, color: str = '#3b82f6', db: SessionLocal) -> bool:
        """Send formatted Slack notification."""
        
        integration = db.query(SlackIntegration).filter(
            SlackIntegration.team_id == team_id,
            SlackIntegration.enabled == True
        ).first()
        
        if not integration:
            return False
        
        payload = {
            'attachments': [
                {
                    'color': color,
                    'text': message,
                    'ts': int(datetime.utcnow().timestamp())
                }
            ]
        }
        
        try:
            response = requests.post(integration.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                integration.last_notified_at = datetime.utcnow()
                db.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
        
        return False
    
    @staticmethod
    def send_daily_digest_to_slack(team_id: str, db: SessionLocal) -> bool:
        """Send daily digest to Slack channel."""
        
        integration = db.query(SlackIntegration).filter(
            SlackIntegration.team_id == team_id,
            SlackIntegration.enabled == True,
            SlackIntegration.notify_daily_digest == True
        ).first()
        
        if not integration:
            return False
        
        # Get today's data
        today = datetime.utcnow().date()
        today_start = datetime(today.year, today.month, today.day)
        
        team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
        history = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= today_start
        ).all()
        
        if not history:
            return False
        
        current = history[-1]
        previous = history[0] if len(history) > 1 else None
        
        # Calculate change
        if previous:
            change = current.overall_caqi - previous.overall_caqi
            change_pct = (change / previous.overall_caqi * 100) if previous.overall_caqi > 0 else 0
            emoji = '📈' if change > 0 else '📉' if change < 0 else '➡️'
        else:
            change = 0
            change_pct = 0
            emoji = '✨'
        
        # Get alerts and badges from today
        alerts = db.query(Alert).filter(
            Alert.team_id == team_id,
            Alert.triggered_at >= today_start
        ).all()
        
        badges = db.query(Badge).filter(
            Badge.team_id == team_id,
            Badge.awarded_at >= today_start
        ).all()
        
        # Format message
        message = f"""
*{emoji} Daily Update: {team.team_name}*
Current CAQI: {current.overall_caqi:.0f}/500
Change: {change:+.0f} ({change_pct:+.1f}%)

*Dimensions:*
• Security: {current.security:.0f}
• Complexity: {current.complexity:.0f}
• Documentation: {current.documentation:.0f}
• Testing: {current.testing:.0f}
• Dependencies: {current.dependencies:.0f}
• Maintainability: {current.maintainability:.0f}
"""
        
        if alerts:
            message += f"\n⚠️ {len(alerts)} alerts today"
        
        if badges:
            message += f"\n🏅 {len(badges)} badges: {', '.join([b.badge_name for b in badges])}"
        
        # Send
        payload = {
            'text': message
        }
        
        try:
            response = requests.post(integration.webhook_url, json=payload, timeout=10)
            
            if response.status_code == 200:
                integration.last_notified_at = datetime.utcnow()
                db.commit()
                return True
        except Exception as e:
            logger.error(f"Failed to send Slack digest: {e}")
        
        return False
    
    @staticmethod
    def verify_slack_request(request_body: str, signature: str, timestamp: str) -> bool:
        """Verify Slack request authenticity."""
        
        if not signature or not timestamp:
            return False
        
        # Check timestamp is recent (within 5 minutes)
        try:
            ts = int(timestamp)
        except ValueError:
            return False
        
        if abs(int(datetime.utcnow().timestamp()) - ts) > 300:
            return False
        
        # Verify signature
        signing_secret = os.getenv('SLACK_SIGNING_SECRET', '')
        base_string = f"v0:{timestamp}:{request_body}"
        
        my_signature = 'v0=' + hmac.new(
            signing_secret.encode(),
            base_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(my_signature, signature)
```

**Tests:** `tests/test_slack_integration_service.py` (5 test cases)
- Send notification
- Send daily digest
- Verify Slack request signature
- Handle webhook errors
- Update last_notified_at

---

### Phase I+3.4: Executive Dashboard Service (2-3 hours)

**File:** `api/services/executive_dashboard_service.py`

```python
class ExecutiveDashboardService:
    """Aggregate data for executive-level dashboards."""
    
    @staticmethod
    def get_company_overview(db: SessionLocal) -> Dict:
        """Get company-level CAQI overview."""
        
        teams = db.query(TeamScore).all()
        
        if not teams:
            return {}
        
        # Calculate company averages
        company_caqi = sum(t.overall_caqi for t in teams) / len(teams)
        
        dimensions = ['security', 'complexity', 'documentation', 'testing', 'dependencies', 'maintainability']
        company_dimensions = {
            dim: sum(getattr(t, dim) for t in teams) / len(teams)
            for dim in dimensions
        }
        
        # Get teams at risk (CAQI < 300)
        at_risk = [t for t in teams if t.overall_caqi < 300]
        
        # Get top performing teams
        top_teams = sorted(teams, key=lambda t: t.overall_caqi, reverse=True)[:5]
        
        return {
            'company_caqi': company_caqi,
            'team_count': len(teams),
            'at_risk_count': len(at_risk),
            'dimensions': company_dimensions,
            'top_teams': [
                {'team_id': t.team_id, 'team_name': t.team_name, 'caqi': t.overall_caqi}
                for t in top_teams
            ],
            'at_risk_teams': [
                {'team_id': t.team_id, 'team_name': t.team_name, 'caqi': t.overall_caqi}
                for t in at_risk
            ]
        }
    
    @staticmethod
    def get_department_summary(department_id: str, team_ids: List[str], db: SessionLocal) -> Dict:
        """Get department-level summary."""
        
        teams = db.query(TeamScore).filter(TeamScore.team_id.in_(team_ids)).all()
        
        if not teams:
            return {}
        
        return {
            'department_id': department_id,
            'team_count': len(teams),
            'avg_caqi': sum(t.overall_caqi for t in teams) / len(teams),
            'min_caqi': min(t.overall_caqi for t in teams),
            'max_caqi': max(t.overall_caqi for t in teams),
            'teams': [
                {'team_id': t.team_id, 'team_name': t.team_name, 'caqi': t.overall_caqi, 'archetype': t.personality_archetype}
                for t in sorted(teams, key=lambda t: t.overall_caqi)
            ]
        }
    
    @staticmethod
    def get_trend_comparison(team_id1: str, team_id2: str, days: int = 90, db: SessionLocal) -> Dict:
        """Compare trends between two teams."""
        
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        history1 = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id1,
            CAQIHistory.recorded_at >= cutoff
        ).order_by(CAQIHistory.recorded_at).all()
        
        history2 = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id2,
            CAQIHistory.recorded_at >= cutoff
        ).order_by(CAQIHistory.recorded_at).all()
        
        return {
            'team1_id': team_id1,
            'team1_start': history1[0].overall_caqi if history1 else 0,
            'team1_end': history1[-1].overall_caqi if history1 else 0,
            'team2_id': team_id2,
            'team2_start': history2[0].overall_caqi if history2 else 0,
            'team2_end': history2[-1].overall_caqi if history2 else 0
        }
```

**Tests:** `tests/test_executive_dashboard_service.py` (4 test cases)
- Get company overview
- Get department summary
- Get trend comparison
- Handle no teams

---

### Phase I+3.5: REST API Endpoints (3-4 hours)

**File:** `api/routes/export_reporting.py` (new)

```python
from fastapi import APIRouter, HTTPException, Depends, Query
from api.services.report_generation import ReportGenerationService
from api.services.email_digest_service import EmailDigestService
from api.services.slack_integration_service import SlackIntegrationService
from api.services.executive_dashboard_service import ExecutiveDashboardService

router = APIRouter(prefix="/api/v1/caqi", tags=["export-reporting"])

@router.get("/reports/team/{team_id}/pdf")
async def download_trend_report_pdf(team_id: str, days: int = Query(90), db: SessionLocal = Depends(get_db)):
    """Download trend analysis PDF report."""
    try:
        pdf_buffer = ReportGenerationService.generate_trend_report_pdf(team_id, days, db)
        
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=caqi_report_{team_id}.pdf"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/reports/team/{team_id}/csv")
async def download_caqi_csv(team_id: str, days: int = Query(90), db: SessionLocal = Depends(get_db)):
    """Download CAQI history as CSV."""
    try:
        csv_buffer = ReportGenerationService.generate_csv_export(team_id, days, db)
        
        return StreamingResponse(
            iter([csv_buffer.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=caqi_history_{team_id}.csv"}
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/reports/team/{team_id}/json")
async def download_caqi_json(team_id: str, days: int = Query(90), db: SessionLocal = Depends(get_db)):
    """Download CAQI data as JSON."""
    return ReportGenerationService.generate_json_export(team_id, days, db)

@router.get("/reports/executive")
async def get_executive_dashboard(db: SessionLocal = Depends(get_db)):
    """Get executive-level dashboard."""
    overview = ExecutiveDashboardService.get_company_overview(db)
    return overview

@router.post("/digests/{team_id}/configure")
async def configure_digest(team_id: str, recipient_email: str, digest_frequency: str,
                          db: SessionLocal = Depends(get_db)):
    """Configure email digest subscription."""
    subscription = EmailDigestSubscription(
        id=str(uuid.uuid4()),
        team_id=team_id,
        recipient_email=recipient_email,
        digest_frequency=digest_frequency,
        created_at=datetime.utcnow()
    )
    db.add(subscription)
    db.commit()
    
    return {
        'status': 'configured',
        'subscription_id': subscription.id,
        'frequency': digest_frequency
    }

@router.get("/digests/{team_id}/status")
async def get_digest_status(team_id: str, db: SessionLocal = Depends(get_db)):
    """Get digest subscription status."""
    subscriptions = db.query(EmailDigestSubscription).filter(
        EmailDigestSubscription.team_id == team_id
    ).all()
    
    return {
        'team_id': team_id,
        'subscription_count': len(subscriptions),
        'subscriptions': [
            {
                'id': s.id,
                'email': s.recipient_email,
                'frequency': s.digest_frequency,
                'last_sent': s.last_sent_at
            }
            for s in subscriptions
        ]
    }

@router.post("/integrations/slack/setup")
async def setup_slack_integration(team_id: str, webhook_url: str, channel_name: str,
                                 db: SessionLocal = Depends(get_db)):
    """Setup Slack webhook integration."""
    integration = SlackIntegration(
        id=str(uuid.uuid4()),
        team_id=team_id,
        webhook_url=webhook_url,
        channel_name=channel_name,
        installed_at=datetime.utcnow()
    )
    db.add(integration)
    db.commit()
    
    return {
        'status': 'installed',
        'integration_id': integration.id,
        'channel': channel_name
    }

@router.get("/integrations/slack/status")
async def get_slack_status(team_id: str, db: SessionLocal = Depends(get_db)):
    """Get Slack integration status."""
    integration = db.query(SlackIntegration).filter(
        SlackIntegration.team_id == team_id
    ).first()
    
    if not integration:
        return {'status': 'not_installed'}
    
    return {
        'status': 'installed',
        'channel': integration.channel_name,
        'enabled': integration.enabled,
        'last_notified': integration.last_notified_at
    }

@router.post("/integrations/slack/test")
async def test_slack_integration(team_id: str, db: SessionLocal = Depends(get_db)):
    """Send test Slack notification."""
    success = SlackIntegrationService.send_notification(
        team_id,
        "🧪 Test message from CAQI",
        "#3b82f6",
        db
    )
    
    return {
        'status': 'sent' if success else 'failed',
        'team_id': team_id
    }
```

**API Endpoints Summary:**
```
GET    /api/v1/caqi/reports/team/{team_id}/pdf
GET    /api/v1/caqi/reports/team/{team_id}/csv
GET    /api/v1/caqi/reports/team/{team_id}/json
GET    /api/v1/caqi/reports/executive
POST   /api/v1/caqi/digests/{team_id}/configure
GET    /api/v1/caqi/digests/{team_id}/status
POST   /api/v1/caqi/integrations/slack/setup
GET    /api/v1/caqi/integrations/slack/status
POST   /api/v1/caqi/integrations/slack/test
```

**Tests:** `tests/test_export_reporting_api.py` (7 test cases)
- Download PDF report
- Download CSV export
- Download JSON export
- Get executive dashboard
- Configure digest
- Setup Slack integration
- Test Slack webhook

---

### Phase I+3.6: Background Jobs (2-3 hours)

**File:** `api/tasks/reporting_tasks.py` (new)

```python
from celery import shared_task
from api.services.email_digest_service import EmailDigestService
from api.services.slack_integration_service import SlackIntegrationService
from api.db.database import SessionLocal

@shared_task
def send_weekly_digests():
    """Send weekly digests on Monday morning."""
    db = SessionLocal()
    
    try:
        # Get all weekly subscriptions for today
        subscriptions = db.query(EmailDigestSubscription).filter(
            EmailDigestSubscription.digest_frequency == 'weekly'
        ).all()
        
        for sub in subscriptions:
            if sub.last_sent_at is None or (datetime.utcnow() - sub.last_sent_at).days >= 7:
                EmailDigestService.send_digest(
                    sub.team_id,
                    sub.id,
                    sub.recipient_email,
                    'weekly',
                    db
                )
        
        return {'status': 'success', 'digests_sent': len(subscriptions)}
    
    finally:
        db.close()

@shared_task
def send_monthly_digests():
    """Send monthly digests on the first of each month."""
    db = SessionLocal()
    
    try:
        subscriptions = db.query(EmailDigestSubscription).filter(
            EmailDigestSubscription.digest_frequency == 'monthly'
        ).all()
        
        for sub in subscriptions:
            EmailDigestService.send_digest(
                sub.team_id,
                sub.id,
                sub.recipient_email,
                'monthly',
                db
            )
        
        return {'status': 'success', 'digests_sent': len(subscriptions)}
    
    finally:
        db.close()

@shared_task
def send_daily_slack_digests():
    """Send daily Slack digests to integrated channels."""
    db = SessionLocal()
    
    try:
        integrations = db.query(SlackIntegration).filter(
            SlackIntegration.enabled == True,
            SlackIntegration.notify_daily_digest == True
        ).all()
        
        for integration in integrations:
            SlackIntegrationService.send_daily_digest_to_slack(integration.team_id, db)
        
        return {'status': 'success', 'digests_sent': len(integrations)}
    
    finally:
        db.close()
```

**Celery Beat Schedule:**
```python
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'send-weekly-digests': {
        'task': 'api.tasks.reporting_tasks.send_weekly_digests',
        'schedule': crontab(day_of_week=1, hour=8, minute=0),  # Monday 8 AM
    },
    'send-monthly-digests': {
        'task': 'api.tasks.reporting_tasks.send_monthly_digests',
        'schedule': crontab(day_of_month=1, hour=8, minute=0),  # 1st of month, 8 AM
    },
    'send-daily-slack-digests': {
        'task': 'api.tasks.reporting_tasks.send_daily_slack_digests',
        'schedule': crontab(hour=9, minute=0),  # Daily 9 AM
    },
}
```

---

### Phase I+3.7: Frontend Components (2-3 hours)

**Component 1:** `frontend/src/components/ReportDownloadPanel.tsx`

```tsx
import React, { useState } from 'react';
import { Download, FileText } from 'lucide-react';

interface ReportDownloadPanelProps {
  teamId: string;
}

export const ReportDownloadPanel: React.FC<ReportDownloadPanelProps> = ({ teamId }) => {
  const [downloading, setDownloading] = useState<string | null>(null);

  const downloadReport = async (format: 'pdf' | 'csv' | 'json') => {
    setDownloading(format);
    
    try {
      const response = await fetch(`/api/v1/caqi/reports/team/${teamId}/${format}`);
      const blob = await response.blob();
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `caqi_report_${teamId}.${format}`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } finally {
      setDownloading(null);
    }
  };

  return (
    <div style={{ padding: '20px', border: '1px solid #e5e7eb', borderRadius: '8px' }}>
      <h3 style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <FileText size={20} />
        Download Reports
      </h3>
      
      <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
        <button
          onClick={() => downloadReport('pdf')}
          disabled={downloading === 'pdf'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 16px',
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            opacity: downloading === 'pdf' ? 0.5 : 1
          }}
        >
          <Download size={16} />
          {downloading === 'pdf' ? 'Downloading...' : 'PDF Report'}
        </button>
        
        <button
          onClick={() => downloadReport('csv')}
          disabled={downloading === 'csv'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 16px',
            backgroundColor: '#10b981',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            opacity: downloading === 'csv' ? 0.5 : 1
          }}
        >
          <Download size={16} />
          {downloading === 'csv' ? 'Downloading...' : 'CSV Export'}
        </button>
        
        <button
          onClick={() => downloadReport('json')}
          disabled={downloading === 'json'}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 16px',
            backgroundColor: '#f59e0b',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            cursor: 'pointer',
            opacity: downloading === 'json' ? 0.5 : 1
          }}
        >
          <Download size={16} />
          {downloading === 'json' ? 'Downloading...' : 'JSON Export'}
        </button>
      </div>
    </div>
  );
};
```

**Component 2:** `frontend/src/components/ExecutiveDashboard.tsx`

```tsx
import React, { useEffect, useState } from 'react';
import { TrendingUp, AlertTriangle } from 'lucide-react';

export const ExecutiveDashboard: React.FC = () => {
  const [overview, setOverview] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchOverview();
  }, []);

  const fetchOverview = async () => {
    try {
      const response = await fetch('/api/v1/caqi/reports/executive');
      const data = await response.json();
      setOverview(data);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading dashboard...</div>;
  if (!overview) return <div>No data available</div>;

  return (
    <div style={{ padding: '20px' }}>
      <h1>Executive Dashboard</h1>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '16px', marginBottom: '24px' }}>
        <div style={{ backgroundColor: '#f3f4f6', padding: '16px', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280' }}>Company CAQI</div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#1f2937' }}>
            {overview.company_caqi.toFixed(0)}/500
          </div>
        </div>
        
        <div style={{ backgroundColor: '#f3f4f6', padding: '16px', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280' }}>Teams</div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#1f2937' }}>
            {overview.team_count}
          </div>
        </div>
        
        <div style={{ backgroundColor: '#fef2f2', padding: '16px', borderRadius: '8px' }}>
          <div style={{ fontSize: '12px', color: '#6b7280', display: 'flex', alignItems: 'center', gap: '4px' }}>
            <AlertTriangle size={14} /> At Risk
          </div>
          <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#dc2626' }}>
            {overview.at_risk_count}
          </div>
        </div>
      </div>
      
      <h2>Top Performing Teams</h2>
      <ul>
        {overview.top_teams.map((team: any) => (
          <li key={team.team_id}>
            {team.team_name}: {team.caqi.toFixed(0)}/500
          </li>
        ))}
      </ul>
      
      {overview.at_risk_count > 0 && (
        <>
          <h2 style={{ marginTop: '24px', color: '#dc2626' }}>Teams at Risk</h2>
          <ul>
            {overview.at_risk_teams.map((team: any) => (
              <li key={team.team_id}>
                {team.team_name}: {team.caqi.toFixed(0)}/500
              </li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
};
```

**Tests:** `frontend/src/__tests__/ExportReporting.test.tsx` (5 test cases)
- Render report download panel
- Download PDF/CSV/JSON
- Render executive dashboard
- Display at-risk teams
- Handle loading state

---

### Phase I+3.8: Testing & Quality (2-3 hours)

**Test Coverage Target:** 80% (new files)

**Test Files:**
1. `tests/test_report_generation.py` (6 tests)
2. `tests/test_email_digest_service.py` (5 tests)
3. `tests/test_slack_integration_service.py` (5 tests)
4. `tests/test_executive_dashboard_service.py` (4 tests)
5. `tests/test_export_reporting_api.py` (7 tests)
6. `frontend/src/__tests__/ReportDownloadPanel.test.tsx` (4 tests)
7. `frontend/src/__tests__/ExecutiveDashboard.test.tsx` (4 tests)

**Total: 35 new tests**

**Quality Metrics:**
```
New Backend Tests:   20
New Frontend Tests:  8
Total New Tests:     35

Target Coverage: 80% (statements)
Expected Time: 2-3 hours
```

---

## Deployment Checklist (Phase I+3)

### Pre-Deployment (2-3 days before)

- [ ] All 35 new tests passing
- [ ] Code review completed
- [ ] Email service configured (SMTP)
- [ ] Slack webhook configured
- [ ] PDF rendering tested
- [ ] CSV export validated

### Deployment Day

1. **Database**
   ```bash
   alembic upgrade head
   ```

2. **Backend**
   ```bash
   pip install reportlab jinja2
   pip install -r requirements.txt
   systemctl restart codepulse-api
   systemctl restart codepulse-celery
   ```

3. **Frontend**
   ```bash
   npm run build
   ```

4. **Configure Services**
   ```bash
   # Set environment variables
   export SMTP_HOST=smtp.example.com
   export SMTP_PORT=587
   export SMTP_USER=noreply@codepulse.ai
   export SMTP_PASSWORD=xxx
   export SLACK_SIGNING_SECRET=xxx
   ```

5. **Verify**
   ```bash
   curl http://api.example.com/api/v1/caqi/reports/team/team-001/pdf -o test.pdf
   curl http://api.example.com/api/v1/caqi/reports/executive
   ```

### Post-Deployment (First Week)

- [ ] PDF reports generating correctly
- [ ] Email digests sending on schedule
- [ ] Slack notifications working
- [ ] Executive dashboard displaying data
- [ ] No SMTP/Slack errors in logs
- [ ] CSV exports valid

---

## Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| I+3.0 | 2-3h | Database schema, ORM models |
| I+3.1 | 3-4h | Report generation service |
| I+3.2 | 3-4h | Email digest service |
| I+3.3 | 3-4h | Slack integration |
| I+3.4 | 2-3h | Executive dashboard |
| I+3.5 | 3-4h | REST API (6 endpoints) |
| I+3.6 | 2-3h | Background jobs (3) |
| I+3.7 | 2-3h | Frontend components (2) |
| I+3.8 | 2-3h | Testing & quality |
| **TOTAL** | **10-15h** | **Production-ready** |

---

## Success Criteria

✅ **Code Quality:**
- 35 new tests, 100% passing
- 80% code coverage (new files)
- 0 TypeScript errors
- 0 security issues

✅ **Performance:**
- PDF generation < 5s
- Digest send < 2s per email
- Slack webhook < 1s
- API endpoints < 500ms

✅ **Functionality:**
- PDF reports download correctly
- CSV exports valid
- Emails send on schedule
- Slack notifications working
- Executive dashboard displays data

✅ **Reliability:**
- Email queue resilient
- Slack retries on failure
- Report caching working
- Background jobs complete

---

## Post-Phase I+3: Complete Path I

**Path I is now complete with all phases:**
- ✅ Phase I.0: Setup & Database
- ✅ Phase I.1: Data Layer Services
- ✅ Phase I.2: REST API Endpoints
- ✅ Phase I.3: Frontend Components
- ✅ Phase I.4: Testing & Quality
- ✅ Phase I+1: Advanced Analytics
- ✅ Phase I+2: Culture Interventions
- ✅ Phase I+3: Export & Reporting

**Next: Path II, III, IV** (as outlined in roadmap)

---

## Resources

**Related Documentation:**
- `PATH_I_CAQI_ENHANCED_IMPLEMENTATION_PLAN.md` — Phase I
- `PHASE_I+1_ADVANCED_ANALYTICS_IMPLEMENTATION_PLAN.md` — Advanced Analytics
- `PHASE_I+2_CULTURE_INTERVENTIONS_IMPLEMENTATION_PLAN.md` — Culture Interventions
- `DEPLOYMENT_SETUP.md` — Local setup
- `DATABASE_MIGRATION.md` — Migration strategy

**Dependencies:**
- Phase I.0-I.5 deployed
- Phase I+1 (Advanced Analytics) deployed
- Phase I+2 (Culture Interventions) deployed
- Email service configured (SMTP)
- Slack workspace access

**Libraries:**
- ReportLab (PDF generation)
- Jinja2 (Email templates)
- requests (Slack webhooks)

---

**Status:** Ready to implement  
**Estimated Start:** 1 week after Phase I+2 deployment  
**Estimated Completion:** 1-2 weeks (10-15 hours)

**Path I Completion: ~60-75 hours total development time across all phases**
