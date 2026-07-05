"""
Audit Logger - Phase 5.4
Audit logging for compliance and tracking
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import time
import json


class AuditAction(str, Enum):
    """Audit action types"""
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"
    API_KEY_USED = "api_key_used"
    SUBSCRIPTION_CREATED = "subscription_created"
    SUBSCRIPTION_UPGRADED = "subscription_upgraded"
    SUBSCRIPTION_CANCELLED = "subscription_cancelled"
    INVOICE_CREATED = "invoice_created"
    INVOICE_PAID = "invoice_paid"
    USER_ADDED = "user_added"
    USER_REMOVED = "user_removed"
    SETTINGS_CHANGED = "settings_changed"
    CODE_ANALYZED = "code_analyzed"
    PR_CREATED = "pr_created"


class AuditSeverity(str, Enum):
    """Audit severity"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class AuditEntry:
    """Audit log entry"""
    entry_id: str
    team_id: str
    action: AuditAction
    severity: AuditSeverity
    actor: str  # User ID or system
    timestamp: float = field(default_factory=time.time)
    resource: str = ""  # What was affected
    change_details: Dict[str, Any] = field(default_factory=dict)
    status: str = "success"  # "success", "failure"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "entry_id": self.entry_id,
            "team_id": self.team_id,
            "action": self.action.value,
            "severity": self.severity.value,
            "actor": self.actor,
            "timestamp": self.timestamp,
            "resource": self.resource,
            "change_details": self.change_details,
            "status": self.status,
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
        }


class AuditLogger:
    """Audit logging for compliance"""

    def __init__(self):
        self.entries: List[AuditEntry] = []
        self.entries_by_team: Dict[str, List[AuditEntry]] = {}

    def log_action(
        self,
        team_id: str,
        action: AuditAction,
        actor: str,
        severity: AuditSeverity = AuditSeverity.INFO,
        resource: str = "",
        change_details: Optional[Dict[str, Any]] = None,
        status: str = "success",
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditEntry:
        """Log audit action"""
        import secrets

        entry_id = f"audit_{secrets.token_hex(8)}"

        entry = AuditEntry(
            entry_id=entry_id,
            team_id=team_id,
            action=action,
            severity=severity,
            actor=actor,
            resource=resource,
            change_details=change_details or {},
            status=status,
            ip_address=ip_address,
            user_agent=user_agent
        )

        self.entries.append(entry)

        if team_id not in self.entries_by_team:
            self.entries_by_team[team_id] = []

        self.entries_by_team[team_id].append(entry)

        return entry

    def get_entries(
        self,
        team_id: str,
        days: int = 30,
        action: Optional[AuditAction] = None
    ) -> List[AuditEntry]:
        """Get audit entries for team"""
        now = time.time()
        period_start = now - (days * 86400)

        entries = self.entries_by_team.get(team_id, [])
        entries = [e for e in entries if e.timestamp >= period_start]

        if action:
            entries = [e for e in entries if e.action == action]

        return sorted(entries, key=lambda e: e.timestamp, reverse=True)

    def get_entry(self, entry_id: str) -> Optional[AuditEntry]:
        """Get specific audit entry"""
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry

        return None

    def get_team_summary(self, team_id: str, days: int = 30) -> Dict[str, Any]:
        """Get audit summary for team"""
        entries = self.get_entries(team_id, days)

        action_counts = {}
        severity_counts = {}

        for entry in entries:
            action = entry.action.value
            severity = entry.severity.value

            action_counts[action] = action_counts.get(action, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "team_id": team_id,
            "period_days": days,
            "total_entries": len(entries),
            "actions": action_counts,
            "severities": severity_counts,
            "latest_action": entries[0].action.value if entries else None,
            "latest_timestamp": entries[0].timestamp if entries else None,
        }

    def export_audit_log(self, team_id: str, days: int = 30) -> str:
        """Export audit log as JSON"""
        entries = self.get_entries(team_id, days)
        return json.dumps([e.to_dict() for e in entries], indent=2)

    def get_critical_events(self, team_id: str, days: int = 30) -> List[AuditEntry]:
        """Get critical audit events"""
        entries = self.get_entries(team_id, days)
        return [e for e in entries if e.severity == AuditSeverity.CRITICAL]

    def get_failed_actions(self, team_id: str, days: int = 30) -> List[AuditEntry]:
        """Get failed actions"""
        entries = self.get_entries(team_id, days)
        return [e for e in entries if e.status == "failure"]


# Global audit logger
_global_audit_logger = AuditLogger()


def get_audit_logger() -> AuditLogger:
    """Get global audit logger"""
    return _global_audit_logger
