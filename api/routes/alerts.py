"""Alert notification management routes."""
import uuid
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from api.db.database import get_db
from api.db.models import AlertPreference
from api.services.alert_service import AlertService

router = APIRouter(prefix="/api/v1/alerts", tags=["alerts"])


class AlertPreferenceRequest(BaseModel):
    """Alert preference configuration."""
    repository: str = "all"
    alert_on_critical: bool = True
    alert_on_error: bool = False
    critical_threshold: int = 1
    error_threshold: int = 5
    email_enabled: bool = True
    email_address: Optional[str] = None
    slack_enabled: bool = False
    slack_webhook: Optional[str] = None
    alert_frequency: str = "immediate"
    is_active: bool = True


class AlertPreferenceResponse(BaseModel):
    """Alert preference response."""
    id: str
    repository: str
    alert_on_critical: bool
    alert_on_error: bool
    critical_threshold: int
    error_threshold: int
    email_enabled: bool
    email_address: Optional[str] = None
    slack_enabled: bool
    slack_webhook: Optional[str] = None
    alert_frequency: str
    is_active: bool

    class Config:
        from_attributes = True


@router.post("/preferences", response_model=AlertPreferenceResponse)
async def create_alert_preference(
    request: AlertPreferenceRequest,
    db: Session = Depends(get_db),
) -> AlertPreferenceResponse:
    """
    Create or update alert preferences.

    **Parameters:**
    - `repository`: Repository to alert on (use "all" for all repos)
    - `alert_on_critical`: Alert when critical issues found
    - `alert_on_error`: Alert when errors found
    - `critical_threshold`: Minimum critical count to trigger alert
    - `email_enabled`: Send email alerts
    - `email_address`: Email to send alerts to
    - `slack_enabled`: Send Slack alerts
    - `slack_webhook`: Slack webhook URL
    - `alert_frequency`: "immediate", "daily", or "weekly"

    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/alerts/preferences" \\
      -H "Content-Type: application/json" \\
      -d '{
        "repository": "my-repo",
        "alert_on_critical": true,
        "email_enabled": true,
        "email_address": "dev@example.com",
        "slack_enabled": true,
        "slack_webhook": "https://hooks.slack.com/services/..."
      }'
    ```
    """
    # Check if preference exists
    existing = db.query(AlertPreference).filter(
        AlertPreference.repository == request.repository
    ).first()

    if existing:
        # Update
        existing.alert_on_critical = request.alert_on_critical
        existing.alert_on_error = request.alert_on_error
        existing.critical_threshold = request.critical_threshold
        existing.error_threshold = request.error_threshold
        existing.email_enabled = request.email_enabled
        existing.email_address = request.email_address
        existing.slack_enabled = request.slack_enabled
        existing.slack_webhook = request.slack_webhook
        existing.alert_frequency = request.alert_frequency
        existing.is_active = request.is_active
        db.commit()
        db.refresh(existing)
        return existing

    # Create new
    preference = AlertPreference(
        id=str(uuid.uuid4()),
        repository=request.repository,
        alert_on_critical=request.alert_on_critical,
        alert_on_error=request.alert_on_error,
        critical_threshold=request.critical_threshold,
        error_threshold=request.error_threshold,
        email_enabled=request.email_enabled,
        email_address=request.email_address,
        slack_enabled=request.slack_enabled,
        slack_webhook=request.slack_webhook,
        alert_frequency=request.alert_frequency,
        is_active=request.is_active,
    )
    db.add(preference)
    db.commit()
    db.refresh(preference)
    return preference


@router.get("/preferences", response_model=List[AlertPreferenceResponse])
async def list_alert_preferences(
    db: Session = Depends(get_db),
    repository: Optional[str] = Query(None),
) -> List[AlertPreferenceResponse]:
    """
    List all alert preferences.

    **Parameters:**
    - `repository`: Filter by repository (optional)

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/alerts/preferences"
    curl "http://localhost:8000/api/v1/alerts/preferences?repository=my-repo"
    ```
    """
    query = db.query(AlertPreference)

    if repository:
        query = query.filter(AlertPreference.repository == repository)

    return query.all()


@router.get("/preferences/{repository}", response_model=AlertPreferenceResponse)
async def get_alert_preference(
    repository: str,
    db: Session = Depends(get_db),
) -> AlertPreferenceResponse:
    """
    Get alert preferences for a specific repository.

    **Example:**
    ```bash
    curl "http://localhost:8000/api/v1/alerts/preferences/my-repo"
    ```
    """
    preference = db.query(AlertPreference).filter(
        AlertPreference.repository == repository
    ).first()

    if not preference:
        raise HTTPException(status_code=404, detail="Alert preference not found")

    return preference


@router.delete("/preferences/{repository}")
async def delete_alert_preference(
    repository: str,
    db: Session = Depends(get_db),
) -> dict:
    """
    Delete alert preferences for a repository.

    **Example:**
    ```bash
    curl -X DELETE "http://localhost:8000/api/v1/alerts/preferences/my-repo"
    ```
    """
    preference = db.query(AlertPreference).filter(
        AlertPreference.repository == repository
    ).first()

    if not preference:
        raise HTTPException(status_code=404, detail="Alert preference not found")

    db.delete(preference)
    db.commit()

    return {"message": f"Alert preferences for {repository} deleted"}


@router.post("/test/{repository}")
async def test_alert(
    repository: str,
    db: Session = Depends(get_db),
    channel: str = Query("email", description="Test 'email' or 'slack'"),
) -> dict:
    """
    Send a test alert to verify configuration.

    **Parameters:**
    - `channel`: "email" or "slack"

    **Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/alerts/test/my-repo?channel=email"
    ```
    """
    preference = db.query(AlertPreference).filter(
        AlertPreference.repository == repository
    ).first()

    if not preference:
        raise HTTPException(status_code=404, detail="Alert preference not found")

    # Create mock scan for testing
    from api.db.models import CIScanHistory
    from datetime import datetime

    test_scan = CIScanHistory(
        id="test-scan",
        repository=repository,
        branch="main",
        platform="github",
        event_type="push",
        status="success",
        critical_count=1,
        error_count=2,
        warning_count=15,
        info_count=5,
        total_findings=23,
        files_scanned=150,
        duration_ms=5000,
        created_at=datetime.utcnow(),
    )

    results = {"email_sent": False, "slack_sent": False}

    if channel in ["email", "both"] and preference.email_enabled and preference.email_address:
        results["email_sent"] = AlertService.send_email_alert(preference.email_address, test_scan)

    if channel in ["slack", "both"] and preference.slack_enabled and preference.slack_webhook:
        results["slack_sent"] = AlertService.send_slack_alert(preference.slack_webhook, test_scan)

    if not results.get("email_sent") and not results.get("slack_sent"):
        raise HTTPException(status_code=400, detail="Failed to send test alert")

    return results
