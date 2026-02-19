"""
Twitter/X Watcher - Monitors Twitter mentions and DMs via API v2.

Uses the social-mcp TwitterAdapter for API calls.
No browser automation needed - pure API-based.

Setup:
1. Twitter Developer Account with Elevated access
2. Create Project + App at https://developer.twitter.com/en/portal/dashboard
3. Set env vars: TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_ACCESS_TOKEN, etc.

Required access: Read + Write + Direct Messages
"""

import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

# Add social-mcp to path for adapter reuse
SOCIAL_MCP_PATH = Path(__file__).resolve().parent.parent.parent / 'MCP_Servers' / 'social-mcp'
sys.path.insert(0, str(SOCIAL_MCP_PATH))


class TwitterWatcher(BaseWatcher):
    """
    Watches Twitter mentions and DMs via API v2.
    Creates action files in /Needs_Action for processing.
    """

    def __init__(self, vault_path: str = None, check_interval: int = 300):
        super().__init__(vault_path, check_interval)

        # Track processed IDs
        self.processed_ids_file = self.vault_path / '.processed_twitter'
        self.processed_ids = self._load_processed_ids()

        # Priority keywords
        self.priority_keywords = [
            'urgent', 'asap', 'important', 'critical',
            'invoice', 'payment', 'deadline', 'action required',
            'reply needed', 'follow up', 'reminder',
            'order', 'quote', 'price', 'help', 'dm'
        ]

        # Adapter (lazy init)
        self._adapter = None

        # Check configuration
        self._configured = bool(
            os.getenv('TWITTER_BEARER_TOKEN') or
            (os.getenv('TWITTER_API_KEY') and os.getenv('TWITTER_ACCESS_TOKEN'))
        )
        if not self._configured:
            self.logger.warning(
                "Twitter not configured. Set TWITTER_BEARER_TOKEN in .env"
            )

    def _load_processed_ids(self) -> set:
        """Load previously processed IDs."""
        if self.processed_ids_file.exists():
            return set(self.processed_ids_file.read_text().splitlines())
        return set()

    def _save_processed_ids(self):
        """Save processed IDs (keep last 2000)."""
        recent = list(self.processed_ids)[-2000:]
        self.processed_ids_file.write_text('\n'.join(recent))

    def _get_adapter(self):
        """Lazy-initialize the Twitter adapter."""
        if self._adapter is None:
            try:
                from adapters.twitter import TwitterAdapter
                self._adapter = TwitterAdapter()
            except ImportError:
                self.logger.error("Could not import TwitterAdapter from social-mcp")
                raise
        return self._adapter

    def _run_async(self, coro):
        """Run an async coroutine synchronously."""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    return pool.submit(asyncio.run, coro).result()
            else:
                return loop.run_until_complete(coro)
        except RuntimeError:
            return asyncio.run(coro)

    def check_for_updates(self) -> list:
        """Check Twitter for new mentions and DMs."""
        if not self._configured:
            return []

        new_items = []

        try:
            adapter = self._get_adapter()

            # Check DMs
            messages = self._run_async(
                adapter.read_messages(unread_only=True, limit=20)
            )
            for msg in messages:
                if msg.id not in self.processed_ids:
                    new_items.append({
                        'item_type': 'social_message',
                        'id': msg.id,
                        'sender_name': msg.sender_name,
                        'sender_username': msg.sender_username,
                        'content': msg.content,
                        'timestamp': msg.timestamp,
                    })
                    self.logger.info(f"New Twitter DM from {msg.sender_name}")

            # Check mentions
            notifications = self._run_async(
                adapter.fetch_notifications(types=['mention'], limit=20)
            )
            for notif in notifications:
                if notif.id not in self.processed_ids:
                    new_items.append({
                        'item_type': 'social_mention',
                        'id': notif.id,
                        'sender_name': notif.actor_name,
                        'sender_username': notif.actor_username,
                        'content': notif.content,
                        'timestamp': notif.timestamp,
                        'target_post_id': notif.target_post_id,
                    })
                    self.logger.info(f"New Twitter mention from {notif.actor_name}")

        except Exception as e:
            self.logger.error(f"Error checking Twitter: {e}")

        return new_items

    def create_action_file(self, item: dict) -> Path:
        """Create action file for a Twitter mention or DM."""
        try:
            item_type = item['item_type']
            sender_name = item.get('sender_name', 'Unknown')
            sender_username = item.get('sender_username', '')
            content = item.get('content', '')
            received = item.get('timestamp', '')
            now = datetime.now()
            timestamp = now.strftime('%Y%m%d_%H%M%S')

            # Determine priority
            priority = self._determine_priority(content)

            # Content preview for filename
            preview = content[:50].strip() if content else 'No_content'
            safe_preview = "".join(
                c for c in preview[:30] if c.isalnum() or c in ' -_'
            ).strip().replace(' ', '_')

            file_content = f'''---
type: {item_type}
source: twitter
message_id: {item['id']}
from: {sender_name}
subject: {safe_preview}
received: {received}
processed: {now.isoformat()}
priority: {priority}
status: pending
---

# Twitter: {safe_preview}

## From
{sender_name} (@{sender_username})

## Content
{content}

## Suggested Actions
- [ ] Read full message
- [ ] Determine if reply needed
- [ ] Draft response (if needed)

---
*Created by TwitterWatcher*
'''

            filename = f"TWITTER_{timestamp}_{safe_preview}.md"
            filepath = self.needs_action / filename
            filepath.write_text(file_content, encoding='utf-8')

            # Mark as processed
            self.processed_ids.add(item['id'])
            self._save_processed_ids()

            # Log action
            self.log_action('twitter_item_received', {
                'item_type': item_type,
                'message_id': item['id'],
                'from': sender_name,
                'priority': priority,
                'action_file': str(filepath)
            })

            return filepath

        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None

    def _determine_priority(self, text: str) -> str:
        """Determine priority based on content keywords."""
        text_lower = text.lower()
        high_keywords = ['urgent', 'asap', 'critical', 'emergency']
        for kw in high_keywords:
            if kw in text_lower:
                return 'high'
        for kw in self.priority_keywords:
            if kw in text_lower:
                return 'medium'
        return 'normal'


def test_watcher():
    """Test Twitter watcher (graceful skip if not configured)."""
    print("Testing Twitter Watcher...")
    print("=" * 50)

    vault_path = os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')

    try:
        watcher = TwitterWatcher(vault_path=vault_path)

        if not watcher._configured:
            print("Twitter not configured - skipping API test")
            print("Set TWITTER_BEARER_TOKEN in .env")
            print("Test PASSED (graceful skip)")
            return True

        print("Configuration found, running single check...")
        items = watcher.run_once()
        print(f"Found {len(items)} new item(s)")
        print("Test PASSED")
        return True

    except Exception as e:
        print(f"Test error: {e}")
        return False


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Twitter Watcher for AI Employee')
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--interval', '-i', type=int, default=300, help='Check interval in seconds')
    parser.add_argument('--test', action='store_true', help='Run test and exit')
    parser.add_argument('--once', action='store_true', help='Run once and exit')

    args = parser.parse_args()

    if args.test:
        test_watcher()
    else:
        vault_path = args.vault or os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')

        print(f"Starting Twitter Watcher...")
        print(f"Vault: {vault_path}")
        print(f"Check interval: {args.interval}s")
        print("Press Ctrl+C to stop\n")

        watcher = TwitterWatcher(
            vault_path=vault_path,
            check_interval=args.interval
        )

        if args.once:
            watcher.run_once()
        else:
            watcher.run()
