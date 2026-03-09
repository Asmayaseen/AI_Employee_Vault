# Contract: BaseWatcher Interface

**Feature**: 001-bronze-tier
**Created**: 2026-02-08
**Type**: Internal API Contract

## Overview

All watchers in the AI Employee system MUST implement this interface. The BaseWatcher abstract class defines the contract that enables the orchestrator to manage any watcher uniformly.

## Interface Definition

```python
class BaseWatcher(ABC):
    """Abstract base class - all watchers must implement."""

    def __init__(self, vault_path: str = None, check_interval: int = 60):
        """
        Args:
            vault_path: Path to Obsidian vault root
            check_interval: Seconds between check cycles
        """

    @abstractmethod
    def check_for_updates(self) -> list:
        """
        Check external source for new items.

        Returns:
            List of new items found (type varies by watcher)

        Raises:
            ConnectionError: If external source unreachable
            AuthenticationError: If credentials invalid
        """

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """
        Create a Markdown action file in /Needs_Action/.

        Args:
            item: Item from check_for_updates() to process

        Returns:
            Path to created .md file

        File Format:
            ---
            type: <source_type>
            from: <sender_identifier>
            subject: <brief_description>
            received: <ISO-8601 timestamp>
            priority: <high|medium|low>
            status: pending
            ---

            ## Content
            <item details>

            ## Suggested Actions
            - [ ] <action 1>
            - [ ] <action 2>
        """

    def log_action(self, action_type: str, details: dict):
        """Log to /Logs/YYYY-MM-DD.json (provided by base class)."""

    def run(self):
        """Main loop - check_for_updates() + create_action_file() in loop."""

    def run_once(self):
        """Single check cycle (for testing)."""
```

## Action File Naming Convention

| Source | Prefix | Example |
|--------|--------|---------|
| Filesystem | `FILE_` | `FILE_20260208_103000_invoice_pdf.md` |
| Gmail | `EMAIL_` | `EMAIL_20260208_083356_Subject_Line.md` |
| WhatsApp | `MSG_` | `MSG_20260208_143000_sender_name.md` |
| LinkedIn | `LINKEDIN_` | `LINKEDIN_20260208_150000_connection.md` |

## Frontmatter Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | YES | Source type: `file_drop`, `email`, `whatsapp_message`, `linkedin_message` |
| `from` | string | NO | Sender identifier |
| `subject` | string | NO | Brief description |
| `received` | string | YES | ISO-8601 timestamp |
| `priority` | string | YES | `high`, `medium`, or `low` |
| `status` | string | YES | Always `pending` on creation |

## Invariants

1. Every call to `create_action_file()` MUST produce exactly one `.md` file in `/Needs_Action/`
2. Action files MUST have valid YAML frontmatter
3. Duplicate items MUST be skipped (deduplication responsibility of each watcher)
4. All file operations MUST be logged via `log_action()`
5. Watchers MUST NOT modify files outside their designated folders
