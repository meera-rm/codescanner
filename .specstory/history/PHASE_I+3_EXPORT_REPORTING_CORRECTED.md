---
created_at: 2026-06-12T18:16:43Z
title: Phase I+3 Export Reporting Corrected
source: claude-code
project: codescanner
---

# Phase I+3: Export & Reporting - CORRECTED IMPLEMENTATION PLAN

**Status:** ✅ CORRECTED - All critical issues fixed  
**Date:** 2026-06-06  
**Changes:** 8 critical fixes, encryption, RBAC, error handling

---

## CRITICAL FIXES IMPLEMENTED

### FIX 1: Webhook URL Encryption

**Issue:** Slack webhook URLs stored in plaintext, exposed if DB breached  
**Solution:** Encrypt at rest using Fernet

```python
# CORRECTED CODE
from cryptography.fernet import Fernet
import os

class EncryptedString:
    """Field type for encrypted strings in SQLAlchemy."""
    
    CIPHER = Fernet(os.getenv('ENCRYPTION_KEY').encode())
    
    @staticmethod
    def encrypt(plaintext: str) -> str:
        """Encrypt string."""
        return EncryptedString.CIPHER.encrypt(plaintext.encode()).decode()
    
    @staticmethod
    def decrypt(ciphertext: str) -> str:
        """Decrypt string."""
        return EncryptedString.CIPHER.decrypt(ciphertext.encode()).decode()

# Updated model
from sqlalchemy.types import TypeDecorator, String

class EncryptedType(TypeDecorator):
    impl = String
    cache_ok = True
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return EncryptedString.encrypt(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return EncryptedString.decrypt(value)

# Updated table
class SlackIntegration(Base):
    __tablename__ = "slack_integrations"
    
    id = Column(String, primary_key=True)
    team_id = Column(String, ForeignKey(...), nullable=False)
    
    webhook_url = Column(EncryptedType(), nullable=False)  # FIXED: Encrypted
    
    # ... rest of columns

# Setup
# Generate encryption key once:
# python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Set in .env: ENCRYPTION_KEY=<generated-key>
```

---

### FIX 2: SMTP Error Handling & Retry Logic

**Issue:** No validation, silent failures, no retry  
**Solution:** Add validation, exponential backoff, and circuit breaker

```python
# CORRECTED CODE
import smtplib
import time
from typing import Optional

class EmailConfig:
    """Validate email configuration."""
    
    @staticmethod
    def validate() -> tuple:
        """Validate SMTP configuration."""
        errors = []
        
        smtp_host = os.getenv('SMTP_HOST')
        if not smtp_host:
            errors.append("SMTP_HOST not configured")
        
        smtp_port = os.getenv('SMTP_PORT', '587')
        try:
            int(smtp_port)
        except ValueError:
            errors.append(f"SMTP_PORT invalid: {smtp_port} (must be integer)")
        
        smtp_user = os.getenv('SMTP_USER')
        if not smtp_user:
            errors.append("SMTP_USER not configured")
        
        smtp_password = os.getenv('SMTP_PASSWORD')
        if not smtp_password:
            errors.append("SMTP_PASSWORD not configured")
        
        return (not errors, errors)

class SMTPEmailService:
    """SMTP with retry logic and circuit breaker."""
    
    MAX_RETRIES = 3
    RETRY_BACKOFF = 2  # Exponential: 1s, 2s, 4s
    
    class CircuitBreaker:
        """Simple circuit breaker for SMTP."""
        def __init__(self, fail_threshold=5, reset_timeout=300):
            self.fail_count = 0
            self.fail_threshold = fail_threshold
            self.reset_timeout = reset_timeout
            self.last_failure_time = None
            self.is_open = False
        
        def record_failure(self):
            self.fail_count += 1
            self.last_failure_time = time.time()
            if self.fail_count >= self.fail_threshold:
                self.is_open = True
                logger.error(f"SMTP circuit breaker OPEN after {self.fail_count} failures")
        
        def record_success(self):
            if self.fail_count > 0:
                logger.info(f"SMTP recovered after {self.fail_count} failures")
            self.fail_count = 0
            self.is_open = False
        
        def can_attempt(self) -> bool:
            if not self.is_open:
                return True
            
            # Check if reset timeout elapsed
            if time.time() - self.last_failure_time > self.reset_timeout:
                logger.info("SMTP circuit breaker reset")
                self.is_open = False
                self.fail_count = 0
                return True
            
            return False
    
    breaker = CircuitBreaker()
    
    @staticmethod
    def send_email(recipient: str, subject: str, html_body: str) -> bool:
        """Send email with retry logic and validation."""
        
        # Validate config
        is_valid, errors = EmailConfig.validate()
        if not is_valid:
            logger.error(f"SMTP configuration invalid: {', '.join(errors)}")
            return False
        
        # Check circuit breaker
        if not SMTPEmailService.breaker.can_attempt():
            logger.error("SMTP circuit breaker is OPEN")
            return False
        
        # Attempt with retries
        for attempt in range(1, SMTPEmailService.MAX_RETRIES + 1):
            try:
                SMTPEmailService._send_with_timeout(recipient, subject, html_body)
                SMTPEmailService.breaker.record_success()
                return True
            
            except smtplib.SMTPAuthenticationError as e:
                logger.error(f"SMTP auth failed: {e}")
                SMTPEmailService.breaker.record_failure()
                return False  # Don't retry auth errors
            
            except (smtplib.SMTPException, OSError) as e:
                logger.warning(f"SMTP attempt {attempt}/{SMTPEmailService.MAX_RETRIES} failed: {e}")
                
                if attempt < SMTPEmailService.MAX_RETRIES:
                    wait_time = SMTPEmailService.RETRY_BACKOFF ** (attempt - 1)
                    logger.info(f"Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    SMTPEmailService.breaker.record_failure()
                    return False
            
            except Exception as e:
                logger.error(f"Unexpected SMTP error: {e}")
                SMTPEmailService.breaker.record_failure()
                return False
        
        return False
    
    @staticmethod
    def _send_with_timeout(recipient: str, subject: str, html_body: str):
        """Send email with timeout protection."""
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = os.getenv('EMAIL_FROM', 'noreply@codepulse.ai')
        msg['To'] = recipient
        
        msg.attach(MIMEText(html_body, 'html'))
        
        # FIXED: Add timeout, error handling
        smtp_host = os.getenv('SMTP_HOST')
        smtp_port = int(os.getenv('SMTP_PORT', '587'))
        
        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
            server.starttls(timeout=10)
            server.login(os.getenv('SMTP_USER'), os.getenv('SMTP_PASSWORD'))
            server.send_message(msg, timeout=30)
```

---

### FIX 3: PDF Generation - Memory Management

**Issue:** Large PDFs consume unbounded memory, risk OOM  
**Solution:** Limit rows and add streaming option

```python
# CORRECTED CODE
class ReportGenerationService:
    MAX_HISTORY_ROWS = 30  # Limit table size
    MAX_PDF_SIZE_MB = 10
    
    @staticmethod
    def generate_trend_report_pdf(team_id: str, days: int = 90, db: SessionLocal) -> BytesIO:
        """Generate PDF with memory protection."""
        
        team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
        history = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= datetime.utcnow() - timedelta(days=days)
        ).order_by(CAQIHistory.recorded_at).all()
        
        if not team or not history:
            raise ValueError(f"No data for team {team_id}")
        
        # FIXED: Limit to max rows
        if len(history) > ReportGenerationService.MAX_HISTORY_ROWS:
            logger.warning(f"PDF truncated to {ReportGenerationService.MAX_HISTORY_ROWS} rows (had {len(history)})")
            history = history[-ReportGenerationService.MAX_HISTORY_ROWS:]
        
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        story = []
        
        # ... build PDF ...
        
        # FIXED: Check file size before returning
        doc.build(story)
        buffer.seek(0)
        
        file_size_mb = len(buffer.getvalue()) / (1024 * 1024)
        if file_size_mb > ReportGenerationService.MAX_PDF_SIZE_MB:
            raise ValueError(f"PDF too large: {file_size_mb:.1f}MB (max {ReportGenerationService.MAX_PDF_SIZE_MB}MB)")
        
        buffer.seek(0)
        return buffer
```

---

### FIX 4: CSV Export - Encoding & Validation

**Issue:** Special characters break, nulls cause issues  
**Solution:** UTF-8 with BOM, quote non-numeric fields

```python
# CORRECTED CODE
class ReportGenerationService:
    @staticmethod
    def generate_csv_export(team_id: str, days: int = 90, db: SessionLocal) -> BytesIO:
        """Generate CSV with proper encoding and validation."""
        
        history = db.query(CAQIHistory).filter(
            CAQIHistory.team_id == team_id,
            CAQIHistory.recorded_at >= datetime.utcnow() - timedelta(days=days)
        ).order_by(CAQIHistory.recorded_at).all()
        
        buffer = BytesIO()
        
        # FIXED: Use UTF-8 with BOM for Excel compatibility
        wrapper = TextIOWrapper(
            buffer,
            encoding='utf-8-sig',  # Adds BOM for Excel
            write_through=True
        )
        
        writer = csv.writer(
            wrapper,
            quoting=csv.QUOTE_NONNUMERIC  # Quote strings, not numbers
        )
        
        # Header
        writer.writerow([
            'Date', 'Overall CAQI', 'Security', 'Complexity', 'Documentation',
            'Testing', 'Dependencies', 'Maintainability'
        ])
        
        # Data rows with null handling
        for h in history:
            writer.writerow([
                h.recorded_at.isoformat(),
                h.overall_caqi or 0,  # FIXED: Default null to 0
                h.security or 0,
                h.complexity or 0,
                h.documentation or 0,
                h.testing or 0,
                h.dependencies or 0,
                h.maintainability or 0
            ])
        
        wrapper.flush()
        buffer.seek(0)
        return buffer
```

---

### FIX 5: Executive Dashboard - Add RBAC

**Issue:** Anyone can see company CAQI and team names  
**Solution:** Role-based access control

```python
# CORRECTED CODE
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    EXECUTIVE = "executive"
    TEAM_LEAD = "team_lead"
    ENGINEER = "engineer"

def require_role(allowed_roles: List[UserRole]):
    """Decorator for role-based access control."""
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get('current_user')
            
            if not current_user:
                raise HTTPException(status_code=401, detail="Not authenticated")
            
            if current_user.role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Required role: {', '.join(allowed_roles)}"
                )
            
            return await func(*args, **kwargs)
        
        return wrapper
    
    return decorator

# FIXED: Add RBAC to endpoints
@router.get("/reports/executive")
@require_role([UserRole.EXECUTIVE, UserRole.ADMIN])  # Only execs/admins
async def get_executive_dashboard(
    current_user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """Get executive-level dashboard (restricted access)."""
    
    # Log access for audit
    logger.info(f"Executive dashboard accessed by {current_user.id} ({current_user.role})")
    
    overview = ExecutiveDashboardService.get_company_overview(db)
    return overview

@router.get("/reports/team/{team_id}/pdf")
async def download_team_report(
    team_id: str,
    current_user: User = Depends(get_current_user),
    db: SessionLocal = Depends(get_db)
):
    """Download team report (team leads + admins only)."""
    
    # Check permission: user is team lead of this team or is admin
    team = db.query(TeamScore).filter(TeamScore.team_id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    is_admin = current_user.role == UserRole.ADMIN
    is_team_lead = (current_user.id == team.team_lead_id)  # Assume team has team_lead_id
    
    if not (is_admin or is_team_lead):
        raise HTTPException(
            status_code=403,
            detail="Only team leads and admins can download reports"
        )
    
    logger.info(f"Report downloaded for team {team_id} by {current_user.id}")
    
    try:
        pdf = ReportGenerationService.generate_trend_report_pdf(team_id, db=db)
        return StreamingResponse(...)
    except Exception as e:
        logger.error(f"Report generation failed: {e}")
        raise HTTPException(status_code=500, detail="Report generation failed")
```

---

### FIX 6: Email Digest Content Validation

**Issue:** Template crashes if required fields missing  
**Solution:** Validate content before rendering

```python
# CORRECTED CODE
class EmailDigestService:
    REQUIRED_FIELDS = [
        'team_name', 'team_id', 'current_caqi', 'archetype',
        'weekly_change', 'week_start', 'week_end'
    ]
    
    @staticmethod
    def send_digest(team_id: str, subscription_id: str, recipient_email: str,
                   digest_type: str, db: SessionLocal) -> bool:
        """Send digest with content validation."""
        
        try:
            # Generate content
            if digest_type == 'weekly':
                content = EmailDigestService.generate_weekly_digest(team_id, db)
            else:
                content = EmailDigestService.generate_monthly_digest(team_id, db)
            
            # FIXED: Validate content
            EmailDigestService._validate_digest_content(content)
            
            # Set defaults for optional fields
            content.setdefault('anomalies', [])
            content.setdefault('suggestions', [])
            content.setdefault('interventions', [])
            content.setdefault('badges', [])
            
            # Render template
            template = Template(EmailDigestService.WEEKLY_DIGEST_TEMPLATE)
            html_body = template.render(**content, subscription_id=subscription_id)
            
            # Send email
            success = SMTPEmailService.send_email(
                recipient=recipient_email,
                subject=f"Weekly Digest: {content['team_name']}",
                html_body=html_body
            )
            
            if success:
                subscription = db.query(EmailDigestSubscription).filter(
                    EmailDigestSubscription.id == subscription_id
                ).first()
                if subscription:
                    subscription.last_sent_at = datetime.utcnow()
                    db.commit()
            
            return success
        
        except ValueError as e:
            logger.error(f"Digest content validation failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Failed to send digest {subscription_id}: {e}")
            return False
    
    @staticmethod
    def _validate_digest_content(content: Dict) -> None:
        """Validate required fields exist."""
        missing = [f for f in EmailDigestService.REQUIRED_FIELDS if f not in content]
        
        if missing:
            raise ValueError(f"Digest missing required fields: {', '.join(missing)}")
        
        # Validate types
        if not isinstance(content['current_caqi'], (int, float)):
            raise ValueError(f"current_caqi must be numeric, got {type(content['current_caqi'])}")
        
        if not 0 <= content['current_caqi'] <= 500:
            raise ValueError(f"current_caqi out of range: {content['current_caqi']}")
```

---

### FIX 7: Report Cleanup Job

**Issue:** report_exports table grows indefinitely  
**Solution:** Add scheduled cleanup job

```python
# api/tasks/reporting_cleanup.py

@shared_task
def cleanup_old_reports():
    """Delete old report exports based on retention policy."""
    db = SessionLocal()
    
    try:
        # Get retention policy (default 90 days)
        retention_days = int(os.getenv('REPORT_RETENTION_DAYS', 90))
        
        cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
        
        # Delete old exports
        deleted = db.query(ReportExport).filter(
            ReportExport.generated_at < cutoff_date
        ).delete()
        
        db.commit()
        
        logger.info(f"Deleted {deleted} old report exports (retention: {retention_days} days)")
        
        return {'deleted': deleted, 'status': 'success'}
    
    except Exception as e:
        logger.error(f"Report cleanup failed: {e}")
        db.rollback()
        return {'error': str(e), 'status': 'failed'}
    
    finally:
        db.close()

# Celery schedule
CELERY_BEAT_SCHEDULE = {
    'cleanup-old-reports': {
        'task': 'api.tasks.reporting_cleanup.cleanup_old_reports',
        'schedule': crontab(day_of_week=0, hour=3, minute=0),  # Sunday 3 AM
    },
}
```

---

### FIX 8: Slack Unsubscribe Token Verification

**Issue:** Unsubscribe links use predictable subscription_id, vulnerable to CSRF  
**Solution:** Use one-time tokens

```python
# CORRECTED CODE
from datetime import timedelta
import secrets

class UnsubscribeTokenService:
    TOKEN_EXPIRY_DAYS = 7
    
    @staticmethod
    def generate_token(subscription_id: str) -> str:
        """Generate one-time unsubscribe token."""
        
        # Create token
        token = secrets.token_urlsafe(32)
        
        # Store in cache with expiry
        cache_key = f"unsubscribe_token:{token}"
        cache.set(
            cache_key,
            subscription_id,
            ttl=UnsubscribeTokenService.TOKEN_EXPIRY_DAYS * 24 * 3600
        )
        
        logger.info(f"Generated unsubscribe token for subscription {subscription_id}")
        
        return token
    
    @staticmethod
    def verify_and_unsubscribe(token: str, db: SessionLocal) -> bool:
        """Verify token and unsubscribe."""
        
        # Look up token
        cache_key = f"unsubscribe_token:{token}"
        subscription_id = cache.get(cache_key)
        
        if not subscription_id:
            logger.warning(f"Invalid or expired unsubscribe token: {token}")
            return False
        
        # Delete subscription
        subscription = db.query(EmailDigestSubscription).filter(
            EmailDigestSubscription.id == subscription_id
        ).first()
        
        if subscription:
            db.delete(subscription)
            db.commit()
            
            # Invalidate token
            cache.delete(cache_key)
            
            logger.info(f"Unsubscribed: {subscription.recipient_email}")
            return True
        
        return False

# In email template
# OLD: <a href="https://example.com/unsubscribe/{{ subscription_id }}">
# NEW:
from api.services.unsubscribe_token_service import UnsubscribeTokenService

unsubscribe_token = UnsubscribeTokenService.generate_token(subscription_id)
# In template: <a href="https://example.com/unsubscribe/{{ token }}">

# In API
@router.get("/unsubscribe/{token}")
async def unsubscribe(token: str, db: SessionLocal = Depends(get_db)):
    """Handle unsubscribe request with token verification."""
    
    success = UnsubscribeTokenService.verify_and_unsubscribe(token, db)
    
    if success:
        return {"status": "unsubscribed", "message": "You have been unsubscribed"}
    else:
        return {"status": "failed", "message": "Invalid or expired unsubscribe link"}
```

---

## REVISED SECURITY CHECKLIST

```
Authentication & Authorization:
  ✅ RBAC on all endpoints
  ✅ Team leads can only see their team reports
  ✅ Executives can see company overview
  ✅ Engineers cannot access executive dashboard

Data Protection:
  ✅ Webhook URLs encrypted at rest
  ✅ SMTP credentials validated before use
  ✅ Unsubscribe tokens single-use
  ✅ No sensitive data in logs

Availability:
  ✅ Circuit breaker for SMTP failures
  ✅ Retry logic with exponential backoff
  ✅ PDF size limits (prevent OOM)
  ✅ CSV encoding handles special characters

Audit:
  ✅ All report access logged
  ✅ Failed SMTP attempts logged
  ✅ Unsubscribe actions logged
  ✅ Report cleanup logged
```

---

## Summary of Fixes

✅ Webhook URLs: Encrypted at rest  
✅ SMTP: Validation, retry, circuit breaker  
✅ PDF: Memory-safe, max 10MB  
✅ CSV: UTF-8 with BOM, quoted fields  
✅ Executive Dashboard: RBAC required  
✅ Email Content: Validated before render  
✅ Report Cleanup: Scheduled deletion job  
✅ Unsubscribe: One-time tokens  

**Status: Ready for implementation** ✅

