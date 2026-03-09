"""
Plan model - represents a generated action plan in /Plans/.

Used by:
- claude_processor.py (generates plans)
- approval_watcher.py (references plans for execution)
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class PlanStep:
    """A single step in an action plan."""
    step_number: int
    description: str
    action_type: str  # auto, manual, approval_required
    tool: Optional[str] = None  # MCP tool to use (e.g., send_email, create_invoice)
    parameters: Dict[str, Any] = field(default_factory=dict)
    completed: bool = False


@dataclass
class Plan:
    """Represents a generated action plan."""
    plan_id: str
    title: str
    source_item: str  # Original Needs_Action filename
    item_type: str    # email, file_drop, whatsapp, etc.
    summary: str = ""
    steps: List[PlanStep] = field(default_factory=list)
    created: datetime = field(default_factory=datetime.now)
    requires_approval: bool = False
    priority: str = "medium"
    status: str = "draft"  # draft, pending_approval, approved, executing, done

    def to_markdown(self) -> str:
        """Generate Markdown file content for /Plans/."""
        lines = [
            "---",
            f"type: plan",
            f"source: {self.source_item}",
            f"item_type: {self.item_type}",
            f"priority: {self.priority}",
            f"created: {self.created.isoformat()}",
            f"requires_approval: {str(self.requires_approval).lower()}",
            f"status: {self.status}",
            "---",
            "",
            f"# Plan: {self.title}",
            "",
            f"**Source:** {self.source_item}",
            f"**Priority:** {self.priority}",
            f"**Status:** {self.status}",
            "",
            "## Summary",
            "",
            self.summary,
            "",
            "## Action Steps",
            "",
        ]
        for step in self.steps:
            checkbox = "x" if step.completed else " "
            tool_info = f" (via `{step.tool}`)" if step.tool else ""
            approval = " **[NEEDS APPROVAL]**" if step.action_type == "approval_required" else ""
            lines.append(f"- [{checkbox}] **Step {step.step_number}:** {step.description}{tool_info}{approval}")
        lines.append("")
        return "\n".join(lines)

    @property
    def completion_percentage(self) -> float:
        """Calculate plan completion percentage."""
        if not self.steps:
            return 0.0
        completed = sum(1 for s in self.steps if s.completed)
        return (completed / len(self.steps)) * 100
