"""
Approval Watcher - Human-in-the-Loop Workflow Manager.

Monitors the approval workflow folders:
- /Pending_Approval: Items waiting for human review
- /Approved: Human-approved items ready for execution
- /Rejected: Human-rejected items

When items are moved to /Approved, triggers the appropriate MCP action.

Features:
- Desktop notifications for new approval requests
- Timeout handling for stale approvals
- Audit logging of all approval decisions
- Integration with MCP servers for action execution
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from base_watcher import BaseWatcher
from typing import Optional, Dict, Any

try:
    from plyer import notification
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False


class ApprovalWatcher(BaseWatcher):
    """
    Watches for approval workflow events and triggers actions.
    """

    def __init__(self, vault_path: str = None, check_interval: int = 5):
        super().__init__(vault_path, check_interval)

        # Approval workflow folders
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'

        # Ensure folders exist
        self.pending_approval.mkdir(exist_ok=True)
        self.approved.mkdir(exist_ok=True)
        self.rejected.mkdir(exist_ok=True)
        self.done.mkdir(exist_ok=True)

        # Track processed approvals
        self.processed_file = self.vault_path / '.processed_approvals'
        self.processed = self._load_processed()

        # Approval timeout (default 24 hours)
        self.timeout_hours = int(os.getenv('APPROVAL_TIMEOUT_HOURS', '24'))

        # Action handlers (can be extended with MCP integrations)
        self.action_handlers = {
            'email_send': self._handle_email_action,
            'payment': self._handle_payment_action,
            'social_post': self._handle_social_action,
            'general': self._handle_general_action
        }

        self.logger.info(f"Approval Watcher initialized")
        self.logger.info(f"Timeout: {self.timeout_hours} hours")
        self.logger.info(f"Notifications: {'enabled' if NOTIFICATIONS_ENABLED else 'disabled'}")

    def _load_processed(self) -> set:
        """Load processed approval IDs."""
        if self.processed_file.exists():
            return set(self.processed_file.read_text().splitlines())
        return set()

    def _save_processed(self):
        """Save processed approval IDs."""
        self.processed_file.write_text('\n'.join(self.processed))

    def _parse_approval_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """Parse frontmatter from an approval file."""
        try:
            content = filepath.read_text(encoding='utf-8')

            # Parse YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    import yaml
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                    return {
                        'metadata': frontmatter,
                        'body': body,
                        'filepath': filepath
                    }

            # No frontmatter, return basic info
            return {
                'metadata': {'type': 'general'},
                'body': content,
                'filepath': filepath
            }

        except Exception as e:
            self.logger.error(f"Error parsing {filepath}: {e}")
            return None

    def _send_notification(self, title: str, message: str):
        """Send desktop notification if available."""
        if NOTIFICATIONS_ENABLED:
            try:
                notification.notify(
                    title=title,
                    message=message[:256],  # Limit message length
                    app_name='AI Employee',
                    timeout=10
                )
            except Exception as e:
                self.logger.warning(f"Notification failed: {e}")
        else:
            self.logger.info(f"NOTIFICATION: {title} - {message}")

    def check_for_updates(self) -> list:
        """Check for new items in approval workflow folders."""
        updates = []

        # Check for new pending approvals
        for filepath in self.pending_approval.glob('*.md'):
            if filepath.stem not in self.processed:
                approval = self._parse_approval_file(filepath)
                if approval:
                    updates.append({
                        'type': 'new_pending',
                        'data': approval
                    })
                    self._send_notification(
                        "New Approval Request",
                        f"Action required: {filepath.stem}"
                    )

        # Check for newly approved items
        for filepath in self.approved.glob('*.md'):
            if filepath.stem not in self.processed:
                approval = self._parse_approval_file(filepath)
                if approval:
                    updates.append({
                        'type': 'approved',
                        'data': approval
                    })

        # Check for timed out pending approvals
        for filepath in self.pending_approval.glob('*.md'):
            approval = self._parse_approval_file(filepath)
            if approval:
                metadata = approval.get('metadata', {})
                created_str = metadata.get('created')

                if created_str:
                    try:
                        created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                        if datetime.now(created.tzinfo) > created + timedelta(hours=self.timeout_hours):
                            updates.append({
                                'type': 'timeout',
                                'data': approval
                            })
                    except:
                        pass

        return updates

    def create_action_file(self, item: dict) -> Path:
        """Process an approval workflow item."""
        item_type = item['type']
        data = item['data']
        filepath = data['filepath']
        metadata = data.get('metadata', {})

        if item_type == 'new_pending':
            # Log new pending approval
            self.log_action('approval_pending', {
                'file': filepath.name,
                'action_type': metadata.get('action', 'unknown')
            })
            self.processed.add(filepath.stem)
            self._save_processed()

        elif item_type == 'approved':
            # Execute the approved action
            self._execute_approved_action(data)
            self.processed.add(filepath.stem)
            self._save_processed()

        elif item_type == 'timeout':
            # Handle timeout
            self._handle_timeout(data)

        return filepath

    def _execute_approved_action(self, approval_data: dict):
        """Execute an approved action via appropriate handler."""
        filepath = approval_data['filepath']
        metadata = approval_data.get('metadata', {})
        action_type = metadata.get('action', 'general')

        self.logger.info(f"Executing approved action: {filepath.name}")

        # Get handler for this action type
        handler = self.action_handlers.get(action_type, self._handle_general_action)

        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would execute: {action_type}")
                result = {'status': 'dry_run', 'action': action_type}
            else:
                result = handler(approval_data)

            # Log success
            self.log_action('action_executed', {
                'file': filepath.name,
                'action_type': action_type,
                'result': result
            })

            # Move to Done
            self._move_to_done(filepath, 'approved', result)

        except Exception as e:
            self.logger.error(f"Action execution failed: {e}")
            self.log_action('action_failed', {
                'file': filepath.name,
                'action_type': action_type,
                'error': str(e)
            })

    def _handle_email_action(self, approval_data: dict) -> dict:
        """Handle email send action."""
        metadata = approval_data['metadata']

        # In production, this would call the Email MCP server
        self.logger.info(f"Sending email to: {metadata.get('to', 'unknown')}")

        # Placeholder for MCP integration
        # from mcp_client import EmailMCP
        # result = EmailMCP.send(
        #     to=metadata['to'],
        #     subject=metadata['subject'],
        #     body=metadata.get('body', '')
        # )

        return {
            'status': 'success',
            'action': 'email_send',
            'to': metadata.get('to'),
            'subject': metadata.get('subject')
        }

    def _handle_payment_action(self, approval_data: dict) -> dict:
        """Handle payment action (requires extra verification)."""
        metadata = approval_data['metadata']

        # Payments should NEVER be auto-executed
        # This should trigger a manual review even after approval
        self.logger.warning("PAYMENT ACTION - Manual verification required")

        return {
            'status': 'pending_manual_review',
            'action': 'payment',
            'amount': metadata.get('amount'),
            'recipient': metadata.get('recipient')
        }

    def _handle_social_action(self, approval_data: dict) -> dict:
        """Handle social media post action."""
        metadata = approval_data['metadata']

        # In production, this would call Social MCP
        self.logger.info(f"Posting to: {metadata.get('platform', 'unknown')}")

        return {
            'status': 'success',
            'action': 'social_post',
            'platform': metadata.get('platform')
        }

    def _handle_general_action(self, approval_data: dict) -> dict:
        """Handle general/unknown action types."""
        self.logger.info("Processing general action")
        return {'status': 'acknowledged', 'action': 'general'}

    def _handle_timeout(self, approval_data: dict):
        """Handle timed out approval requests."""
        filepath = approval_data['filepath']

        self.logger.warning(f"Approval timeout: {filepath.name}")
        self._send_notification(
            "Approval Timeout",
            f"Action expired: {filepath.stem}"
        )

        # Move to rejected with timeout reason
        self._move_to_done(filepath, 'timeout', {'reason': 'timeout'})

        self.log_action('approval_timeout', {
            'file': filepath.name
        })

    def _move_to_done(self, filepath: Path, reason: str, result: dict):
        """Move processed file to Done folder with metadata."""
        try:
            # Read original content
            content = filepath.read_text(encoding='utf-8')

            # Add processing metadata
            timestamp = datetime.now().isoformat()
            processing_note = f"""

---
## Processing Result
- **Processed At:** {timestamp}
- **Resolution:** {reason}
- **Result:** {json.dumps(result, indent=2)}
"""
            # Write to Done folder
            done_path = self.done / f"{reason}_{filepath.name}"
            done_path.write_text(content + processing_note, encoding='utf-8')

            # Remove from original location
            filepath.unlink()

            self.logger.info(f"Moved {filepath.name} to Done ({reason})")

        except Exception as e:
            self.logger.error(f"Error moving file: {e}")

    def create_approval_request(
        self,
        action_type: str,
        title: str,
        details: dict,
        expires_hours: int = None
    ) -> Path:
        """
        Helper method to create an approval request file.

        Args:
            action_type: Type of action (email_send, payment, etc.)
            title: Human-readable title
            details: Action-specific details
            expires_hours: Override default timeout

        Returns:
            Path to created approval file
        """
        timestamp = datetime.now()
        expires = expires_hours or self.timeout_hours

        # Generate filename
        safe_title = title.replace(' ', '_')[:30]
        filename = f"APPROVAL_{timestamp.strftime('%Y%m%d_%H%M%S')}_{safe_title}.md"

        content = f"""---
action: {action_type}
title: {title}
created: {timestamp.isoformat()}
expires: {(timestamp + timedelta(hours=expires)).isoformat()}
status: pending
{self._format_details_yaml(details)}
---

# Approval Request: {title}

## Action Type
**{action_type}**

## Details
{self._format_details_markdown(details)}

## Expiration
This request will expire on {(timestamp + timedelta(hours=expires)).strftime('%Y-%m-%d %H:%M')}

---

## Instructions
- To **APPROVE**: Move this file to `/Approved/` folder
- To **REJECT**: Move this file to `/Rejected/` folder

---
*Created by AI Employee at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}*
"""

        filepath = self.pending_approval / filename
        filepath.write_text(content, encoding='utf-8')

        self.logger.info(f"Created approval request: {filename}")
        self._send_notification("New Approval Request", title)

        return filepath

    def _format_details_yaml(self, details: dict) -> str:
        """Format details dict as YAML lines."""
        lines = []
        for key, value in details.items():
            if isinstance(value, str):
                lines.append(f"{key}: \"{value}\"")
            else:
                lines.append(f"{key}: {value}")
        return '\n'.join(lines)

    def _format_details_markdown(self, details: dict) -> str:
        """Format details dict as markdown."""
        lines = []
        for key, value in details.items():
            lines.append(f"- **{key}:** {value}")
        return '\n'.join(lines)


# Standalone execution
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Approval Watcher for AI Employee')
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--interval', '-i', type=int, default=5, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--create-test', action='store_true', help='Create a test approval request')

    args = parser.parse_args()

    vault_path = args.vault or os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')

    watcher = ApprovalWatcher(
        vault_path=vault_path,
        check_interval=args.interval
    )

    if args.create_test:
        # Create test approval request
        watcher.create_approval_request(
            action_type='email_send',
            title='Test Email Approval',
            details={
                'to': 'test@example.com',
                'subject': 'Test Email',
                'body': 'This is a test email body'
            }
        )
        print("Test approval request created in Pending_Approval folder")
    elif args.once:
        items = watcher.check_for_updates()
        for item in items:
            watcher.create_action_file(item)
    else:
        print(f"Starting Approval Watcher...")
        print(f"Vault: {vault_path}")
        print(f"Check interval: {args.interval}s")
        print("-" * 50)
        watcher.run()
