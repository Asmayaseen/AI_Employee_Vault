"""
ApprovalRequest model - represents an item in /Pending_Approval/.

Used by:
- claude_processor.py (creates approval requests)
- approval_watcher.py (monitors for approved/rejected items)
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ApprovalRequest:
    """Represents a pending approval request."""
    request_id: str
    action_type: str  # send_email, create_invoice, social_post, payment
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    source_item: Optional[str] = None  # Original Needs_Action filename
    priority: str = "medium"
    created: datetime = field(default_factory=datetime.now)
    status: str = "pending"  # pending, approved, rejected
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None
    risk_level: str = "medium"  # low, medium, high, critical
    estimated_cost: float = 0.0

    def to_markdown(self) -> str:
        """Generate Markdown file content for /Pending_Approval/."""
        lines = [
            "---",
            f"type: approval_request",
            f"action: {self.action_type}",
            f"priority: {self.priority}",
            f"risk_level: {self.risk_level}",
            f"created: {self.created.isoformat()}",
            f"status: {self.status}",
            f"source: {self.source_item or 'manual'}",
        ]
        if self.estimated_cost > 0:
            lines.append(f"estimated_cost: ${self.estimated_cost:.2f}")
        lines.append("---")
        lines.append("")
        lines.append(f"# Approval Request: {self.description}")
        lines.append("")
        lines.append(f"**Action Type:** {self.action_type}")
        lines.append(f"**Priority:** {self.priority}")
        lines.append(f"**Risk Level:** {self.risk_level}")
        lines.append("")
        lines.append("## Details")
        lines.append("")
        for key, value in self.parameters.items():
            lines.append(f"- **{key}:** {value}")
        lines.append("")
        lines.append("## Instructions")
        lines.append("")
        lines.append("To approve: Move this file to `/Approved/`")
        lines.append("To reject: Move this file to `/Rejected/`")
        lines.append("")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'request_id': self.request_id,
            'action_type': self.action_type,
            'description': self.description,
            'parameters': self.parameters,
            'source_item': self.source_item,
            'priority': self.priority,
            'created': self.created.isoformat(),
            'status': self.status,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'risk_level': self.risk_level,
            'estimated_cost': self.estimated_cost,
        }
