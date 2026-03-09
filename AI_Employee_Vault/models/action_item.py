"""
ActionItem model - represents an item from /Needs_Action/ folder.

Used by:
- claude_processor.py (reads and processes items)
- filesystem_watcher.py (creates items)
- gmail_watcher.py (creates items)
- whatsapp_watcher.py (creates items)
- linkedin_watcher.py (creates items)
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class ActionItem:
    """Represents an item from Needs_Action folder."""
    filepath: Path
    item_type: str  # email, whatsapp_message, linkedin_message, file_drop, general
    priority: str   # high, medium, low
    metadata: Dict[str, Any] = field(default_factory=dict)
    body: str = ""
    created: datetime = field(default_factory=datetime.now)
    source: str = ""  # gmail, whatsapp, linkedin, filesystem, manual
    status: str = "pending"  # pending, processing, done, failed

    @property
    def filename(self) -> str:
        """Get the filename without path."""
        return self.filepath.name

    @property
    def age_minutes(self) -> float:
        """Get item age in minutes."""
        return (datetime.now() - self.created).total_seconds() / 60

    def is_sensitive(self) -> bool:
        """Check if this item requires human approval."""
        sensitive_types = ['payment', 'bank_transfer', 'bulk_email', 'social_post']
        if self.item_type in sensitive_types:
            return True
        if self.priority == 'high' and self.item_type == 'email':
            return True
        # Check for financial keywords in body
        financial_keywords = ['invoice', 'payment', 'transfer', '$', 'amount due']
        return any(kw in self.body.lower() for kw in financial_keywords)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            'filepath': str(self.filepath),
            'item_type': self.item_type,
            'priority': self.priority,
            'metadata': self.metadata,
            'body': self.body,
            'created': self.created.isoformat(),
            'source': self.source,
            'status': self.status,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ActionItem':
        """Deserialize from dictionary."""
        data = data.copy()
        data['filepath'] = Path(data['filepath'])
        data['created'] = datetime.fromisoformat(data['created'])
        return cls(**data)
