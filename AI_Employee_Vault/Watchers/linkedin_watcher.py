"""
LinkedIn Watcher - Monitors LinkedIn and enables auto-posting.

Features:
- Monitor LinkedIn messages/notifications
- Auto-post business updates
- Lead capture from inquiries
- Connection request monitoring

Uses Playwright for web automation.
Note: Use responsibly and be aware of LinkedIn's terms of service.

Setup:
1. Install: pip install playwright
2. Run: playwright install chromium
3. First run will require LinkedIn login
4. Session is persisted for subsequent runs
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher
from typing import Optional, Dict, List

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not installed. Run: pip install playwright && playwright install chromium")


class LinkedInWatcher(BaseWatcher):
    """
    Watches LinkedIn for messages, notifications, and enables posting.
    Creates action files in /Needs_Action for processing.
    """

    def __init__(self, vault_path: str = None, session_path: str = None, check_interval: int = 300):
        super().__init__(vault_path, check_interval)

        # Session storage for persistent login
        self.session_path = Path(session_path or os.getenv(
            'LINKEDIN_SESSION_PATH',
            self.vault_path / 'Watchers' / '.linkedin_session'
        ))
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Priority keywords for lead capture
        self.lead_keywords = [
            'interested', 'pricing', 'services', 'hire', 'project',
            'consultant', 'developer', 'quote', 'proposal', 'budget',
            'opportunity', 'collaboration', 'partnership'
        ]

        # Track processed items
        self.processed_file = self.vault_path / '.processed_linkedin'
        self.processed = self._load_processed()

        # Scheduled posts queue
        self.posts_queue_file = self.vault_path / 'Plans' / 'linkedin_posts_queue.json'

        # Browser instance
        self._playwright = None
        self._browser = None
        self._page = None

        self.logger.info(f"LinkedIn Watcher initialized")
        self.logger.info(f"Session path: {self.session_path}")

    def _load_processed(self) -> set:
        """Load processed item identifiers."""
        if self.processed_file.exists():
            return set(self.processed_file.read_text().splitlines())
        return set()

    def _save_processed(self):
        """Save processed items."""
        recent = list(self.processed)[-500:]
        self.processed_file.write_text('\n'.join(recent))

    def _init_browser(self):
        """Initialize browser with persistent context."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available")

        if self._playwright is None:
            self._playwright = sync_playwright().start()

            self._browser = self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=False,  # Must be False for initial login
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox'
                ],
                viewport={'width': 1280, 'height': 800}
            )

            self._page = self._browser.pages[0] if self._browser.pages else self._browser.new_page()
            self.logger.info("Browser initialized")

    def _ensure_logged_in(self) -> bool:
        """Ensure logged in to LinkedIn."""
        try:
            self._page.goto('https://www.linkedin.com/feed/', timeout=60000)

            # Check if already logged in
            try:
                self._page.wait_for_selector(
                    '[data-control-name="nav.homepage"], .feed-identity-module',
                    timeout=10000
                )
                self.logger.info("Already logged in to LinkedIn")
                return True
            except PlaywrightTimeout:
                pass

            # Need to log in
            self.logger.info("=" * 50)
            self.logger.info("PLEASE LOG IN TO LINKEDIN IN THE BROWSER")
            self.logger.info("=" * 50)

            # Wait for login (up to 3 minutes)
            self._page.wait_for_selector(
                '[data-control-name="nav.homepage"], .feed-identity-module',
                timeout=180000
            )
            self.logger.info("Successfully logged in!")
            return True

        except PlaywrightTimeout:
            self.logger.error("Timeout waiting for LinkedIn login")
            return False
        except Exception as e:
            self.logger.error(f"Login error: {e}")
            return False

    def check_for_updates(self) -> list:
        """Check LinkedIn for new messages and notifications."""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not available")
            return []

        try:
            self._init_browser()

            if not self._ensure_logged_in():
                return []

            updates = []

            # Check messages
            messages = self._check_messages()
            updates.extend(messages)

            # Check notifications
            notifications = self._check_notifications()
            updates.extend(notifications)

            # Check connection requests
            connections = self._check_connection_requests()
            updates.extend(connections)

            return updates

        except Exception as e:
            self.logger.error(f"Error checking LinkedIn: {e}")
            return []

    def _check_messages(self) -> list:
        """Check for new LinkedIn messages."""
        messages = []

        try:
            # Go to messaging
            self._page.goto('https://www.linkedin.com/messaging/', timeout=30000)
            self._page.wait_for_selector('.msg-conversations-container', timeout=10000)

            # Find unread conversations
            unread_convos = self._page.query_selector_all(
                '.msg-conversation-card--unread, .msg-conversation-listitem--unread'
            )

            for convo in unread_convos[:5]:  # Limit to 5
                try:
                    # Get sender name
                    name_el = convo.query_selector('.msg-conversation-card__participant-names')
                    sender = name_el.inner_text() if name_el else "Unknown"

                    # Get preview
                    preview_el = convo.query_selector('.msg-conversation-card__message-snippet')
                    preview = preview_el.inner_text() if preview_el else ""

                    # Create identifier
                    msg_id = f"MSG_{sender}_{datetime.now().strftime('%Y%m%d_%H')}"

                    if msg_id not in self.processed:
                        # Check for lead keywords
                        is_lead = any(kw in preview.lower() for kw in self.lead_keywords)

                        messages.append({
                            'type': 'linkedin_message',
                            'sender': sender,
                            'preview': preview,
                            'is_potential_lead': is_lead,
                            'msg_id': msg_id,
                            'timestamp': datetime.now().isoformat()
                        })
                        self.logger.info(f"Found message from {sender}")

                except Exception as e:
                    self.logger.warning(f"Error processing message: {e}")

        except Exception as e:
            self.logger.error(f"Error checking messages: {e}")

        return messages

    def _check_notifications(self) -> list:
        """Check LinkedIn notifications."""
        notifications = []

        try:
            # Go to notifications
            self._page.goto('https://www.linkedin.com/notifications/', timeout=30000)
            self._page.wait_for_selector('.nt-card', timeout=10000)

            # Get recent notifications
            notif_cards = self._page.query_selector_all('.nt-card')

            for card in notif_cards[:10]:
                try:
                    text = card.inner_text()

                    # Check for important notifications
                    if any(keyword in text.lower() for keyword in [
                        'viewed your profile', 'mentioned you', 'commented',
                        'endorsed', 'connection request'
                    ]):
                        notif_id = f"NOTIF_{hash(text[:50])}_{datetime.now().strftime('%Y%m%d')}"

                        if notif_id not in self.processed:
                            notifications.append({
                                'type': 'linkedin_notification',
                                'text': text[:200],
                                'notif_id': notif_id,
                                'timestamp': datetime.now().isoformat()
                            })

                except Exception as e:
                    continue

        except Exception as e:
            self.logger.warning(f"Error checking notifications: {e}")

        return notifications

    def _check_connection_requests(self) -> list:
        """Check for pending connection requests."""
        requests = []

        try:
            # Go to network/invitations
            self._page.goto('https://www.linkedin.com/mynetwork/invitation-manager/', timeout=30000)

            # Wait and get invitations
            self._page.wait_for_selector('.invitation-card', timeout=10000)
            invitations = self._page.query_selector_all('.invitation-card')

            for invite in invitations[:10]:
                try:
                    name_el = invite.query_selector('.invitation-card__name')
                    title_el = invite.query_selector('.invitation-card__subtitle')

                    name = name_el.inner_text() if name_el else "Unknown"
                    title = title_el.inner_text() if title_el else ""

                    invite_id = f"CONN_{name}_{datetime.now().strftime('%Y%m%d')}"

                    if invite_id not in self.processed:
                        requests.append({
                            'type': 'connection_request',
                            'name': name,
                            'title': title,
                            'invite_id': invite_id,
                            'timestamp': datetime.now().isoformat()
                        })

                except Exception as e:
                    continue

        except Exception as e:
            self.logger.warning(f"Error checking connection requests: {e}")

        return requests

    def create_action_file(self, item: dict) -> Path:
        """Create action file for LinkedIn item."""
        try:
            item_type = item['type']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            if item_type == 'linkedin_message':
                return self._create_message_action(item, timestamp)
            elif item_type == 'linkedin_notification':
                return self._create_notification_action(item, timestamp)
            elif item_type == 'connection_request':
                return self._create_connection_action(item, timestamp)

        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None

    def _create_message_action(self, item: dict, timestamp: str) -> Path:
        """Create action file for LinkedIn message."""
        sender = item['sender']
        safe_sender = re.sub(r'[^\w\s-]', '', sender).strip().replace(' ', '_')[:20]

        priority = 'high' if item.get('is_potential_lead') else 'medium'

        content = f'''---
type: linkedin_message
source: linkedin
sender: {sender}
received: {item['timestamp']}
processed: {datetime.now().isoformat()}
priority: {priority}
is_potential_lead: {item.get('is_potential_lead', False)}
status: pending
---

# LinkedIn Message: {sender}

## From
{sender}

## Message Preview
{item.get('preview', 'No preview available')}

## Lead Status
**{'🔥 POTENTIAL LEAD' if item.get('is_potential_lead') else 'Regular message'}**

---

## Suggested Actions
- [ ] Open LinkedIn and read full message
- [ ] Evaluate if response is needed
- [ ] Draft response (if potential lead, respond within 24h)
- [ ] Update CRM/lead tracking (if applicable)

## Notes
_Add notes after processing_

---
*Created by LinkedIn Watcher at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
'''

        filename = f'LINKEDIN_MSG_{timestamp}_{safe_sender}.md'
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')

        self.processed.add(item['msg_id'])
        self._save_processed()

        self.log_action('linkedin_message_detected', {
            'sender': sender,
            'is_lead': item.get('is_potential_lead'),
            'file': str(filepath)
        })

        self.logger.info(f"Created action file: {filename}")
        return filepath

    def _create_notification_action(self, item: dict, timestamp: str) -> Path:
        """Create action file for LinkedIn notification."""
        content = f'''---
type: linkedin_notification
source: linkedin
received: {item['timestamp']}
processed: {datetime.now().isoformat()}
priority: low
status: pending
---

# LinkedIn Notification

## Details
{item.get('text', 'No details')}

---

## Suggested Actions
- [ ] Review on LinkedIn
- [ ] Take action if needed

---
*Created by LinkedIn Watcher*
'''

        filename = f'LINKEDIN_NOTIF_{timestamp}.md'
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')

        self.processed.add(item['notif_id'])
        self._save_processed()

        return filepath

    def _create_connection_action(self, item: dict, timestamp: str) -> Path:
        """Create action file for connection request."""
        name = item['name']
        safe_name = re.sub(r'[^\w\s-]', '', name).strip().replace(' ', '_')[:20]

        content = f'''---
type: connection_request
source: linkedin
name: {name}
title: {item.get('title', '')}
received: {item['timestamp']}
processed: {datetime.now().isoformat()}
priority: medium
status: pending
---

# LinkedIn Connection Request

## From
**{name}**

## Title/Role
{item.get('title', 'Not specified')}

---

## Suggested Actions
- [ ] Review profile on LinkedIn
- [ ] Accept or ignore connection
- [ ] Send welcome message if accepted

---
*Created by LinkedIn Watcher*
'''

        filename = f'LINKEDIN_CONN_{timestamp}_{safe_name}.md'
        filepath = self.needs_action / filename
        filepath.write_text(content, encoding='utf-8')

        self.processed.add(item['invite_id'])
        self._save_processed()

        return filepath

    def post_update(self, content: str, requires_approval: bool = True) -> Dict:
        """
        Post an update to LinkedIn.

        Args:
            content: The post text
            requires_approval: Whether to create approval request first

        Returns:
            Result dictionary
        """
        self.logger.info("Post update requested")

        if requires_approval:
            return self._create_post_approval(content)

        return self._execute_post(content)

    def _create_post_approval(self, content: str) -> Dict:
        """Create approval request for LinkedIn post."""
        timestamp = datetime.now()
        filename = f"LINKEDIN_POST_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"

        approval_content = f'''---
action: social_post
platform: linkedin
created: {timestamp.isoformat()}
expires: {(timestamp + timedelta(hours=24)).isoformat()}
status: pending
---

# LinkedIn Post Approval

## Post Content
```
{content}
```

## Character Count
{len(content)} characters

---

## Instructions
- To **APPROVE**: Move this file to `/Approved/` folder
- To **REJECT**: Move this file to `/Rejected/` folder

---
*Created by LinkedIn Watcher*
'''

        filepath = self.vault_path / 'Pending_Approval' / filename
        filepath.write_text(approval_content, encoding='utf-8')

        self.logger.info(f"Created post approval request: {filename}")
        return {
            'status': 'pending_approval',
            'file': str(filepath)
        }

    def _execute_post(self, content: str) -> Dict:
        """Actually post to LinkedIn."""
        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post: {content[:50]}...")
            return {'status': 'dry_run'}

        try:
            self._init_browser()

            if not self._ensure_logged_in():
                return {'status': 'error', 'message': 'Not logged in'}

            # Go to home feed
            self._page.goto('https://www.linkedin.com/feed/', timeout=30000)

            # Click on share box
            share_box = self._page.wait_for_selector(
                '.share-box-feed-entry__trigger, [data-control-name="share.initial_entry_point"]',
                timeout=10000
            )
            share_box.click()

            # Wait for editor
            editor = self._page.wait_for_selector(
                '.ql-editor, [contenteditable="true"]',
                timeout=10000
            )

            # Type content
            editor.fill(content)

            # Click post button
            post_btn = self._page.wait_for_selector(
                '.share-actions__primary-action, button[data-control-name="share.post"]',
                timeout=5000
            )
            post_btn.click()

            # Wait for post to complete
            self._page.wait_for_timeout(3000)

            self.log_action('linkedin_post_created', {
                'content_preview': content[:100]
            })

            return {'status': 'success', 'message': 'Posted successfully'}

        except Exception as e:
            self.logger.error(f"Post failed: {e}")
            return {'status': 'error', 'message': str(e)}

    def schedule_post(self, content: str, post_time: datetime) -> Dict:
        """
        Schedule a post for later.

        Args:
            content: Post content
            post_time: When to post

        Returns:
            Result dictionary
        """
        # Load existing queue
        queue = []
        if self.posts_queue_file.exists():
            queue = json.loads(self.posts_queue_file.read_text())

        # Add new post
        queue.append({
            'content': content,
            'scheduled_time': post_time.isoformat(),
            'created': datetime.now().isoformat(),
            'status': 'pending'
        })

        # Save queue
        self.posts_queue_file.parent.mkdir(exist_ok=True)
        self.posts_queue_file.write_text(json.dumps(queue, indent=2))

        self.logger.info(f"Scheduled post for {post_time}")
        return {
            'status': 'scheduled',
            'scheduled_time': post_time.isoformat()
        }

    def close(self):
        """Clean up browser resources."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self.logger.info("Browser closed")


# Import timedelta for post approval
from datetime import timedelta


# Standalone execution
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='LinkedIn Watcher for AI Employee')
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--interval', '-i', type=int, default=300, help='Check interval (seconds)')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--post', help='Create a post (will require approval)')

    args = parser.parse_args()

    vault_path = args.vault or os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')

    watcher = LinkedInWatcher(
        vault_path=vault_path,
        check_interval=args.interval
    )

    if args.post:
        result = watcher.post_update(args.post)
        print(json.dumps(result, indent=2))
    elif args.once:
        items = watcher.check_for_updates()
        for item in items:
            watcher.create_action_file(item)
        watcher.close()
    else:
        print(f"Starting LinkedIn Watcher...")
        print(f"Vault: {vault_path}")
        print(f"Check interval: {args.interval}s")
        print("-" * 50)

        try:
            watcher.run()
        finally:
            watcher.close()
