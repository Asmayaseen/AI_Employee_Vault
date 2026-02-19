"""
Claude Processor - Reasoning Loop for AI Employee.

This module enables Claude Code to:
1. Process items in /Needs_Action folder
2. Generate Plan.md files with action steps
3. Create approval requests for sensitive actions
4. Move completed items to /Done

This is the "brain" component that brings intelligence to the watchers.

Usage:
    # Run as standalone processor
    python claude_processor.py --process-all

    # Process single item
    python claude_processor.py --process FILE_20260205.md

    # Generate daily briefing
    python claude_processor.py --briefing
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class ActionItem:
    """Represents an item from Needs_Action folder."""
    filepath: Path
    item_type: str
    priority: str
    metadata: Dict[str, Any]
    body: str
    created: datetime


class ClaudeProcessor:
    """
    Claude's reasoning engine for processing action items.
    Generates plans, creates approvals, and coordinates actions.
    """

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path or os.getenv(
            'VAULT_PATH',
            '/mnt/d/Ai-Employee/AI_Employee_Vault'
        ))

        # Folders
        self.needs_action = self.vault_path / 'Needs_Action'
        self.plans = self.vault_path / 'Plans'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.done = self.vault_path / 'Done'
        self.briefings = self.vault_path / 'Briefings'

        # Ensure folders exist
        for folder in [self.needs_action, self.plans, self.pending_approval, self.done, self.briefings]:
            folder.mkdir(exist_ok=True)

        # Load handbook rules
        self.handbook = self._load_handbook()

        # Processing rules by type
        self.processors = {
            'email': self._process_email,
            'whatsapp_message': self._process_whatsapp,
            'linkedin_message': self._process_linkedin,
            'connection_request': self._process_connection,
            'file_drop': self._process_file,
            'general': self._process_general
        }

    def _load_handbook(self) -> Dict:
        """Load Company_Handbook.md rules."""
        handbook_path = self.vault_path / 'Company_Handbook.md'
        if handbook_path.exists():
            content = handbook_path.read_text(encoding='utf-8')
            # Parse rules (simplified - could use YAML frontmatter)
            return {
                'content': content,
                'auto_reply_threshold': 24,  # hours
                'payment_approval_threshold': 100,  # dollars
                'max_email_length': 500,  # characters for auto-draft
            }
        return {}

    def _parse_item(self, filepath: Path) -> Optional[ActionItem]:
        """Parse an action item file."""
        try:
            content = filepath.read_text(encoding='utf-8')

            # Parse YAML frontmatter
            metadata = {}
            body = content

            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    import yaml
                    try:
                        metadata = yaml.safe_load(parts[1]) or {}
                    except:
                        metadata = {}
                    body = parts[2].strip()

            # Determine item type
            item_type = metadata.get('type', 'general')
            priority = metadata.get('priority', 'medium')

            # Parse created date
            created_str = metadata.get('processed') or metadata.get('received')
            try:
                created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
            except:
                created = datetime.now()

            return ActionItem(
                filepath=filepath,
                item_type=item_type,
                priority=priority,
                metadata=metadata,
                body=body,
                created=created
            )

        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None

    def get_pending_items(self) -> List[ActionItem]:
        """Get all items in Needs_Action folder."""
        items = []
        for filepath in self.needs_action.glob('*.md'):
            item = self._parse_item(filepath)
            if item:
                items.append(item)

        # Sort by priority (high first) then by date (oldest first)
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        items.sort(key=lambda x: (priority_order.get(x.priority, 1), x.created))

        return items

    def process_item(self, item: ActionItem) -> Dict:
        """Process a single action item and generate a plan."""
        print(f"Processing: {item.filepath.name} (type: {item.item_type}, priority: {item.priority})")

        # Get processor for this type
        processor = self.processors.get(item.item_type, self._process_general)

        # Generate plan
        result = processor(item)

        return result

    def process_all(self) -> List[Dict]:
        """Process all pending items."""
        items = self.get_pending_items()
        results = []

        print(f"Found {len(items)} items to process")

        for item in items:
            result = self.process_item(item)
            results.append(result)

        return results

    def _create_plan(self, item: ActionItem, analysis: Dict, actions: List[Dict]) -> Path:
        """Create a Plan.md file for an item."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_name = item.filepath.stem[:30]

        # Build actions markdown
        actions_md = []
        for i, action in enumerate(actions, 1):
            checkbox = "[ ]"
            actions_md.append(f"- {checkbox} **Step {i}**: {action['description']}")
            if action.get('requires_approval'):
                actions_md.append(f"  - ⚠️ Requires human approval")
            if action.get('notes'):
                actions_md.append(f"  - Notes: {action['notes']}")

        content = f'''---
source_file: {item.filepath.name}
source_type: {item.item_type}
created: {datetime.now().isoformat()}
priority: {item.priority}
status: pending
---

# Plan: {analysis.get('title', item.filepath.stem)}

## Summary
{analysis.get('summary', 'No summary available')}

## Analysis
- **Type**: {item.item_type}
- **Priority**: {item.priority}
- **Urgency**: {analysis.get('urgency', 'Normal')}
- **Requires Response**: {analysis.get('requires_response', 'Unknown')}

## Context
{analysis.get('context', 'No additional context')}

## Action Plan

{chr(10).join(actions_md)}

## Expected Outcome
{analysis.get('expected_outcome', 'Task completed successfully')}

## Notes
_Add notes during execution_

---
*Generated by Claude Processor at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Source: {item.filepath.name}*
'''

        filename = f'PLAN_{timestamp}_{safe_name}.md'
        filepath = self.plans / filename
        filepath.write_text(content, encoding='utf-8')

        print(f"Created plan: {filename}")
        return filepath

    def _process_email(self, item: ActionItem) -> Dict:
        """Process an email item."""
        metadata = item.metadata
        sender = metadata.get('from', 'Unknown')
        subject = metadata.get('subject', 'No Subject')

        # Analyze email content
        analysis = {
            'title': f"Email from {sender}",
            'summary': f"Email regarding: {subject}",
            'urgency': 'High' if item.priority == 'high' else 'Normal',
            'requires_response': self._needs_response(item.body),
            'context': f"Received from {sender}"
        }

        # Determine actions
        actions = []

        if analysis['requires_response']:
            actions.append({
                'description': 'Read full email content',
                'requires_approval': False
            })
            actions.append({
                'description': 'Draft response based on context',
                'requires_approval': False,
                'notes': 'Use professional tone matching handbook guidelines'
            })
            actions.append({
                'description': 'Send response via Email MCP',
                'requires_approval': True,
                'notes': 'Email sending requires human approval'
            })
        else:
            actions.append({
                'description': 'Review email content',
                'requires_approval': False
            })
            actions.append({
                'description': 'Archive email (no response needed)',
                'requires_approval': False
            })

        actions.append({
            'description': 'Move to Done folder',
            'requires_approval': False
        })

        # Create plan
        plan_path = self._create_plan(item, analysis, actions)

        # If high priority and needs response, create draft approval
        if item.priority == 'high' and analysis['requires_response']:
            self._create_draft_approval(item, sender, subject)

        return {
            'status': 'planned',
            'item': item.filepath.name,
            'plan': plan_path.name,
            'actions_count': len(actions)
        }

    def _process_whatsapp(self, item: ActionItem) -> Dict:
        """Process a WhatsApp message item."""
        metadata = item.metadata
        sender = metadata.get('chat_name', 'Unknown')
        preview = item.body[:200]

        analysis = {
            'title': f"WhatsApp from {sender}",
            'summary': f"Message from {sender}: {preview[:100]}...",
            'urgency': 'High' if item.priority == 'high' else 'Normal',
            'requires_response': True,  # WhatsApp usually needs response
            'context': f"Keywords detected in message"
        }

        actions = [
            {'description': 'Open WhatsApp and read full conversation', 'requires_approval': False},
            {'description': 'Analyze conversation context and intent', 'requires_approval': False},
            {'description': 'Draft appropriate response', 'requires_approval': False},
            {'description': 'Send response (manual - WhatsApp automation limited)', 'requires_approval': True},
            {'description': 'Move to Done folder', 'requires_approval': False}
        ]

        plan_path = self._create_plan(item, analysis, actions)

        return {
            'status': 'planned',
            'item': item.filepath.name,
            'plan': plan_path.name
        }

    def _process_linkedin(self, item: ActionItem) -> Dict:
        """Process a LinkedIn message item."""
        metadata = item.metadata
        sender = metadata.get('sender', 'Unknown')
        is_lead = metadata.get('is_potential_lead', False)

        analysis = {
            'title': f"LinkedIn: {sender}",
            'summary': f"LinkedIn message from {sender}" + (" - POTENTIAL LEAD" if is_lead else ""),
            'urgency': 'High' if is_lead else 'Normal',
            'requires_response': True,
            'context': "Lead detected - prioritize response" if is_lead else "Standard LinkedIn message",
            'expected_outcome': "Convert lead to client" if is_lead else "Maintain professional relationship"
        }

        actions = [
            {'description': 'Open LinkedIn and review full message', 'requires_approval': False},
            {'description': 'Research sender profile and company', 'requires_approval': False},
        ]

        if is_lead:
            actions.extend([
                {'description': 'Draft personalized response addressing their needs', 'requires_approval': False},
                {'description': 'Propose call or meeting to discuss further', 'requires_approval': False},
                {'description': 'Add to CRM/lead tracking system', 'requires_approval': False}
            ])
        else:
            actions.append({'description': 'Draft appropriate response', 'requires_approval': False})

        actions.extend([
            {'description': 'Send response via LinkedIn', 'requires_approval': True},
            {'description': 'Move to Done folder', 'requires_approval': False}
        ])

        plan_path = self._create_plan(item, analysis, actions)

        return {
            'status': 'planned',
            'item': item.filepath.name,
            'plan': plan_path.name,
            'is_lead': is_lead
        }

    def _process_connection(self, item: ActionItem) -> Dict:
        """Process a LinkedIn connection request."""
        metadata = item.metadata
        name = metadata.get('name', 'Unknown')
        title = metadata.get('title', '')

        analysis = {
            'title': f"Connection: {name}",
            'summary': f"LinkedIn connection request from {name} ({title})",
            'urgency': 'Low',
            'requires_response': False,
            'context': f"Review profile before accepting"
        }

        actions = [
            {'description': 'Review sender profile on LinkedIn', 'requires_approval': False},
            {'description': 'Decide: Accept or Ignore connection', 'requires_approval': True},
            {'description': 'If accepted, send welcome message', 'requires_approval': False},
            {'description': 'Move to Done folder', 'requires_approval': False}
        ]

        plan_path = self._create_plan(item, analysis, actions)

        return {
            'status': 'planned',
            'item': item.filepath.name,
            'plan': plan_path.name
        }

    def _process_file(self, item: ActionItem) -> Dict:
        """Process a file drop item."""
        metadata = item.metadata
        filename = metadata.get('original_name', 'Unknown file')

        analysis = {
            'title': f"File: {filename}",
            'summary': f"New file dropped for processing: {filename}",
            'urgency': 'Normal',
            'requires_response': False,
            'context': "File requires categorization and action"
        }

        actions = [
            {'description': 'Identify file type and contents', 'requires_approval': False},
            {'description': 'Categorize file (invoice, document, image, etc.)', 'requires_approval': False},
            {'description': 'Take appropriate action based on type', 'requires_approval': False},
            {'description': 'Move to appropriate folder', 'requires_approval': False}
        ]

        plan_path = self._create_plan(item, analysis, actions)

        return {
            'status': 'planned',
            'item': item.filepath.name,
            'plan': plan_path.name
        }

    def _process_general(self, item: ActionItem) -> Dict:
        """Process a general/unknown item type."""
        analysis = {
            'title': f"Item: {item.filepath.stem}",
            'summary': f"Action item requiring review",
            'urgency': 'Normal' if item.priority != 'high' else 'High',
            'requires_response': True,
            'context': "Generic item - manual review recommended"
        }

        actions = [
            {'description': 'Review item content', 'requires_approval': False},
            {'description': 'Determine required action', 'requires_approval': False},
            {'description': 'Execute action (may require approval)', 'requires_approval': True},
            {'description': 'Move to Done folder', 'requires_approval': False}
        ]

        plan_path = self._create_plan(item, analysis, actions)

        return {
            'status': 'planned',
            'item': item.filepath.name,
            'plan': plan_path.name
        }

    def _needs_response(self, content: str) -> bool:
        """Determine if content needs a response."""
        response_indicators = [
            '?', 'please', 'could you', 'would you', 'can you',
            'reply', 'respond', 'let me know', 'get back',
            'waiting', 'asap', 'urgent'
        ]
        content_lower = content.lower()
        return any(indicator in content_lower for indicator in response_indicators)

    def _create_draft_approval(self, item: ActionItem, recipient: str, subject: str):
        """Create a draft email approval request."""
        timestamp = datetime.now()
        filename = f"EMAIL_DRAFT_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"

        content = f'''---
action: email_send
to: {recipient}
subject: "Re: {subject}"
created: {timestamp.isoformat()}
status: pending_draft
---

# Email Draft Approval

## To
{recipient}

## Subject
Re: {subject}

## Draft Body
_[AI will generate draft here based on context]_

---

## Instructions
1. Review and edit the draft
2. When satisfied, move to `/Approved/` to send
3. Or move to `/Rejected/` to discard

---
*Created by Claude Processor*
'''

        filepath = self.pending_approval / filename
        filepath.write_text(content, encoding='utf-8')

    def generate_briefing(self) -> Path:
        """Generate a daily/weekly briefing."""
        timestamp = datetime.now()

        # Gather statistics
        pending_items = len(list(self.needs_action.glob('*.md')))
        plans_count = len(list(self.plans.glob('*.md')))
        pending_approvals = len(list(self.pending_approval.glob('*.md')))
        done_today = len([
            f for f in self.done.glob('*.md')
            if f.stat().st_mtime > (datetime.now() - timedelta(days=1)).timestamp()
        ])

        content = f'''---
generated: {timestamp.isoformat()}
type: daily_briefing
---

# Daily Briefing - {timestamp.strftime('%Y-%m-%d')}

## 📊 Summary

| Metric | Count |
|--------|-------|
| Pending Actions | {pending_items} |
| Active Plans | {plans_count} |
| Awaiting Approval | {pending_approvals} |
| Completed Today | {done_today} |

## 🔴 High Priority Items
'''

        # Add high priority items
        high_priority = [
            item for item in self.get_pending_items()
            if item.priority == 'high'
        ]

        if high_priority:
            for item in high_priority[:5]:
                content += f"- {item.item_type}: {item.filepath.stem}\n"
        else:
            content += "_No high priority items_\n"

        content += f'''

## 📝 Pending Approvals

'''
        # List pending approvals
        approvals = list(self.pending_approval.glob('*.md'))
        if approvals:
            for approval in approvals[:5]:
                content += f"- {approval.name}\n"
        else:
            content += "_No pending approvals_\n"

        content += f'''

## 📈 Recommendations

- Review and process {pending_items} pending items
- Approve or reject {pending_approvals} pending requests
- Clear completed items from Plans folder

---
*Generated by Claude Processor at {timestamp.strftime('%H:%M:%S')}*
'''

        filename = f"BRIEFING_{timestamp.strftime('%Y-%m-%d')}.md"
        filepath = self.briefings / filename
        filepath.write_text(content, encoding='utf-8')

        print(f"Generated briefing: {filename}")
        return filepath


# CLI execution
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Claude Processor - AI Employee Brain')
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--process-all', action='store_true', help='Process all pending items')
    parser.add_argument('--process', help='Process a specific file')
    parser.add_argument('--briefing', action='store_true', help='Generate daily briefing')
    parser.add_argument('--list', action='store_true', help='List pending items')

    args = parser.parse_args()

    vault_path = args.vault or os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')
    processor = ClaudeProcessor(vault_path=vault_path)

    if args.process_all:
        results = processor.process_all()
        print(f"\nProcessed {len(results)} items")
        for r in results:
            print(f"  - {r.get('item')}: {r.get('status')}")

    elif args.process:
        filepath = processor.needs_action / args.process
        if filepath.exists():
            item = processor._parse_item(filepath)
            if item:
                result = processor.process_item(item)
                print(json.dumps(result, indent=2))
        else:
            print(f"File not found: {filepath}")

    elif args.briefing:
        briefing_path = processor.generate_briefing()
        print(f"Briefing created: {briefing_path}")

    elif args.list:
        items = processor.get_pending_items()
        print(f"\nPending items ({len(items)}):")
        for item in items:
            print(f"  [{item.priority}] {item.item_type}: {item.filepath.name}")

    else:
        parser.print_help()
