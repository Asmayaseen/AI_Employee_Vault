"""
WhatsApp Watcher - Monitors WhatsApp Web for important messages.

Uses Playwright for browser automation to detect new messages
containing priority keywords.

Setup:
1. Install: pip install playwright
2. Run: playwright install chromium
3. First run will require QR code scan for WhatsApp Web login
4. Session is persisted in WHATSAPP_SESSION_PATH

Note: Be aware of WhatsApp's terms of service regarding automation.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher

try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
except ImportError:
    print("Playwright not installed. Run: pip install playwright && playwright install chromium")
    raise


class WhatsAppWatcher(BaseWatcher):
    """
    Watches WhatsApp Web for messages containing priority keywords.
    Creates action files in /Needs_Action for processing.
    """

    def __init__(self, vault_path: str = None, session_path: str = None, check_interval: int = 30):
        super().__init__(vault_path, check_interval)

        # Session storage path for persistent login
        self.session_path = Path(session_path or os.getenv(
            'WHATSAPP_SESSION_PATH',
            self.vault_path / 'Watchers' / '.whatsapp_session'
        ))
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Priority keywords to watch for
        self.priority_keywords = [
            'urgent', 'asap', 'important', 'critical',
            'invoice', 'payment', 'deadline', 'help',
            'reply', 'call', 'meeting', 'price', 'quote',
            'order', 'delivery', 'emergency'
        ]

        # Track processed messages (by chat + timestamp)
        self.processed_file = self.vault_path / '.processed_whatsapp'
        self.processed_messages = self._load_processed()

        # Browser instance (lazy initialization)
        self._playwright = None
        self._browser = None
        self._page = None

        self.logger.info(f"WhatsApp session path: {self.session_path}")

    def _load_processed(self) -> set:
        """Load previously processed message identifiers."""
        if self.processed_file.exists():
            return set(self.processed_file.read_text().splitlines())
        return set()

    def _save_processed(self):
        """Save processed message identifiers."""
        # Keep only last 1000 entries to prevent file bloat
        recent = list(self.processed_messages)[-1000:]
        self.processed_file.write_text('\n'.join(recent))

    def _init_browser(self):
        """Initialize browser with persistent context."""
        if self._playwright is None:
            self._playwright = sync_playwright().start()

            # Use persistent context for session storage
            self._browser = self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=False,  # Must be False for first QR scan
                args=['--disable-blink-features=AutomationControlled']
            )

            self._page = self._browser.pages[0] if self._browser.pages else self._browser.new_page()
            self.logger.info("Browser initialized")

    def _ensure_logged_in(self) -> bool:
        """Ensure WhatsApp Web is logged in, wait for QR scan if needed."""
        try:
            self._page.goto('https://web.whatsapp.com', timeout=60000)

            # Wait for either QR code or chat list
            self.logger.info("Waiting for WhatsApp Web to load...")

            # Check if already logged in (chat list visible)
            try:
                self._page.wait_for_selector(
                    '[data-testid="chat-list"], [aria-label="Chat list"]',
                    timeout=10000
                )
                self.logger.info("Already logged in to WhatsApp Web")
                return True
            except PlaywrightTimeout:
                pass

            # Need to scan QR code
            self.logger.info("=" * 50)
            self.logger.info("SCAN QR CODE IN BROWSER TO LOGIN")
            self.logger.info("=" * 50)

            # Wait for login (up to 2 minutes for QR scan)
            self._page.wait_for_selector(
                '[data-testid="chat-list"], [aria-label="Chat list"]',
                timeout=120000
            )
            self.logger.info("Successfully logged in!")
            return True

        except PlaywrightTimeout:
            self.logger.error("Timeout waiting for WhatsApp Web login")
            return False
        except Exception as e:
            self.logger.error(f"Error during login: {e}")
            return False

    def check_for_updates(self) -> list:
        """Check WhatsApp for new messages with priority keywords."""
        try:
            self._init_browser()

            if not self._ensure_logged_in():
                return []

            # Find all chats with unread messages
            unread_chats = self._page.query_selector_all(
                '[data-testid="cell-frame-container"]:has([data-testid="icon-unread-count"])'
            )

            new_messages = []

            for chat in unread_chats[:10]:  # Limit to 10 chats per check
                try:
                    # Get chat name
                    name_el = chat.query_selector('[data-testid="cell-frame-title"] span')
                    chat_name = name_el.inner_text() if name_el else "Unknown"

                    # Get last message preview
                    preview_el = chat.query_selector('[data-testid="last-msg-status"]')
                    preview = preview_el.inner_text() if preview_el else ""

                    # Check if message contains priority keywords
                    preview_lower = preview.lower()
                    matching_keywords = [kw for kw in self.priority_keywords if kw in preview_lower]

                    if matching_keywords:
                        # Create unique message identifier
                        msg_id = f"{chat_name}_{datetime.now().strftime('%Y%m%d_%H%M')}"

                        if msg_id not in self.processed_messages:
                            new_messages.append({
                                'chat_name': chat_name,
                                'preview': preview,
                                'keywords': matching_keywords,
                                'timestamp': datetime.now().isoformat(),
                                'msg_id': msg_id
                            })
                            self.logger.info(f"Found priority message from {chat_name}: {matching_keywords}")

                except Exception as e:
                    self.logger.warning(f"Error processing chat: {e}")
                    continue

            return new_messages

        except Exception as e:
            self.logger.error(f"Error checking WhatsApp: {e}")
            return []

    def create_action_file(self, message: dict) -> Path:
        """Create action file for a WhatsApp message."""
        try:
            chat_name = message['chat_name']
            preview = message['preview']
            keywords = message['keywords']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # Sanitize chat name for filename
            safe_name = re.sub(r'[^\w\s-]', '', chat_name).strip().replace(' ', '_')[:30]

            # Determine priority level
            high_priority_keywords = ['urgent', 'asap', 'emergency', 'critical']
            priority = 'high' if any(kw in keywords for kw in high_priority_keywords) else 'medium'

            content = f'''---
type: whatsapp_message
source: whatsapp_web
chat_name: {chat_name}
received: {message['timestamp']}
processed: {datetime.now().isoformat()}
priority: {priority}
keywords: {', '.join(keywords)}
status: pending
---

# WhatsApp Message: {chat_name}

## From
{chat_name}

## Message Preview
{preview}

## Detected Keywords
{', '.join(keywords)}

## Priority
**{priority.upper()}**

---

## Suggested Actions
- [ ] Open WhatsApp and read full conversation
- [ ] Determine if response is needed
- [ ] Draft response (if needed)
- [ ] Forward to relevant team member (if applicable)
- [ ] Log any action items

## Notes
_Add notes here after processing_

---
*Created by WhatsApp Watcher at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
'''

            # Create file
            filename = f'WHATSAPP_{timestamp}_{safe_name}.md'
            filepath = self.needs_action / filename
            filepath.write_text(content, encoding='utf-8')

            # Mark as processed
            self.processed_messages.add(message['msg_id'])
            self._save_processed()

            # Log action
            self.log_action('whatsapp_message_detected', {
                'chat_name': chat_name,
                'keywords': keywords,
                'priority': priority,
                'file_created': str(filepath)
            })

            self.logger.info(f"Created action file: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"Error creating action file: {e}")
            return None

    def close(self):
        """Clean up browser resources."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        self.logger.info("Browser closed")

    def run(self):
        """Main run loop with cleanup on exit."""
        try:
            super().run()
        finally:
            self.close()


# Standalone execution
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='WhatsApp Watcher for AI Employee')
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--interval', '-i', type=int, default=30, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run once and exit')

    args = parser.parse_args()

    vault_path = args.vault or os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')

    watcher = WhatsAppWatcher(
        vault_path=vault_path,
        check_interval=args.interval
    )

    print(f"Starting WhatsApp Watcher...")
    print(f"Vault: {vault_path}")
    print(f"Check interval: {args.interval}s")
    print("-" * 50)

    if args.once:
        messages = watcher.check_for_updates()
        for msg in messages:
            watcher.create_action_file(msg)
        watcher.close()
    else:
        watcher.run()
