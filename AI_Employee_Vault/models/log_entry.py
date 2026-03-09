"""
LogEntry and AuditEntry models.

Used by:
- audit_logger.py (writes structured audit logs)
- base_watcher.py (writes watcher logs)
- scheduler.py (writes task execution logs)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class LogEntry:
    """Generic log entry for watcher and scheduler logs."""
    timestamp: datetime = field(default_factory=datetime.now)
    watcher: str = ""
    action_type: str = ""
    dry_run: bool = True
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary for JSON storage."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'watcher': self.watcher,
            'action_type': self.action_type,
            'dry_run': self.dry_run,
            **self.details,
        }


@dataclass
class AuditEntry:
    """
    Structured audit log entry per Constitution Principle III.

    Schema from constitution.md:
    {
        "timestamp": "ISO-8601",
        "action_type": "email_send|payment|post|file_operation",
        "actor": "claude_code|watcher|orchestrator",
        "target": "recipient_identifier",
        "parameters": {},
        "approval_status": "approved|rejected|auto_approved",
        "approved_by": "human|system_rule",
        "result": "success|failure|pending",
        "error_detail": "optional"
    }
    """
    timestamp: datetime = field(default_factory=datetime.now)
    action_type: str = ""      # email_send, payment, post, file_operation, etc.
    actor: str = ""            # claude_code, watcher, orchestrator
    domain: str = ""           # gmail, odoo, social, filesystem
    target: str = ""           # recipient/target identifier
    parameters: Dict[str, Any] = field(default_factory=dict)
    approval_status: str = ""  # approved, rejected, auto_approved
    approved_by: str = ""      # human, system_rule
    result: str = ""           # success, failure, pending
    error_detail: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary matching constitution schema."""
        entry = {
            'timestamp': self.timestamp.isoformat(),
            'action_type': self.action_type,
            'actor': self.actor,
            'domain': self.domain,
            'target': self.target,
            'parameters': self.parameters,
            'approval_status': self.approval_status,
            'approved_by': self.approved_by,
            'result': self.result,
        }
        if self.error_detail:
            entry['error'] = self.error_detail
        return entry

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AuditEntry':
        """Deserialize from dictionary."""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        data['error_detail'] = data.pop('error', None)
        return cls(**data)
