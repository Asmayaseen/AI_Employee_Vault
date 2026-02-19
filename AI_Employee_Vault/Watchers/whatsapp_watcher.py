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

    def _start_virtual_display(self):
        """Start Xvfb virtual display for headed mode in WSL2."""
        if os.environ.get('DISPLAY'):
            self.logger.info(f"DISPLAY already set: {os.environ['DISPLAY']}")
            return True

        # Try xvfb-run style: start Xvfb directly
        try:
            import subprocess
            # Check if Xvfb is installed
            result = subprocess.run(['which', 'xvfb-run'], capture_output=True, text=True)
            if result.returncode == 0:
                self.logger.info("Xvfb available - will use virtual display")

            # Start Xvfb on display :99
            self._xvfb_process = subprocess.Popen(
                ['Xvfb', ':99', '-screen', '0', '1280x900x24', '-ac'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            os.environ['DISPLAY'] = ':99'
            import time
            time.sleep(1)  # Give Xvfb time to start
            self.logger.info("Started Xvfb virtual display on :99")
            return True
        except FileNotFoundError:
            self.logger.info("Xvfb not installed, will use headless mode")
        except Exception as e:
            self.logger.warning(f"Could not start Xvfb: {e}")

        # Try pyvirtualdisplay as backup
        try:
            from pyvirtualdisplay import Display
            self._virtual_display = Display(visible=0, size=(1280, 900))
            self._virtual_display.start()
            self.logger.info("Started virtual display via pyvirtualdisplay")
            return True
        except ImportError:
            pass
        except Exception as e:
            self.logger.warning(f"pyvirtualdisplay failed: {e}")

        return False

    def _apply_stealth(self, page):
        """Apply anti-detection patches to avoid WhatsApp blocking."""
        stealth_js = """
        // Override webdriver detection
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});

        // Override plugins to look like real browser
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });

        // Override languages
        Object.defineProperty(navigator, 'languages', {
            get: () => ['en-US', 'en']
        });

        // Override permissions
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );

        // Remove automation indicators
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;

        // Chrome runtime
        window.chrome = { runtime: {} };
        """
        page.add_init_script(stealth_js)
        self.logger.info("Applied browser stealth patches")

    def _init_browser(self):
        """Initialize browser with persistent context.

        Strategy: Try headed mode with Xvfb first (best for WhatsApp).
        Fall back to headless with stealth patches if Xvfb unavailable.
        """
        if self._playwright is None:
            # Try to get a virtual display for headed mode
            has_display = self._start_virtual_display()
            use_headless = not has_display

            if use_headless:
                self.logger.info("Using headless mode (no display available)")
                self.logger.info("TIP: Install Xvfb for better QR detection:")
                self.logger.info("  sudo apt-get install -y xvfb")
            else:
                self.logger.info("Using headed mode with virtual display (best for WhatsApp)")

            self._playwright = sync_playwright().start()

            user_agent = (
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                '(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
            )

            launch_args = [
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-gpu',
                '--disable-software-rasterizer',
                '--disable-extensions',
                '--disable-default-apps',
                '--disable-infobars',
            ]
            if use_headless:
                launch_args.append('--headless=new')  # New headless mode (Chrome 112+)

            self._browser = self._playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=use_headless,
                user_agent=user_agent,
                viewport={'width': 1280, 'height': 900},
                locale='en-US',
                timezone_id='America/New_York',
                args=launch_args
            )

            self._page = self._browser.pages[0] if self._browser.pages else self._browser.new_page()
            self._apply_stealth(self._page)
            self.logger.info(f"Browser initialized (headless={use_headless})")

    def _save_qr_screenshot(self):
        """Save QR code as PNG file for manual scanning.

        Takes multiple screenshots with retries to ensure QR is captured.
        """
        qr_path = self.vault_path / 'Watchers' / 'whatsapp_qr.png'
        debug_path = self.vault_path / 'Watchers' / 'whatsapp_debug.png'

        try:
            # Always save a full page debug screenshot first
            self._page.screenshot(path=str(debug_path), full_page=False)
            self.logger.info(f"Debug screenshot saved: {debug_path}")

            # Log the page title and URL for debugging
            self.logger.info(f"Page title: {self._page.title()}")
            self.logger.info(f"Page URL: {self._page.url}")

            # Try to find QR code with multiple selectors and retries
            qr_selectors = [
                'canvas',                       # WhatsApp renders QR on canvas
                '[data-testid="qrcode"]',       # Direct QR test ID
                'div[data-ref]',                # QR container with ref
                '._akau',                       # WhatsApp QR class
                '[aria-label="Scan this QR code to link a device!"]',
                'div._aoac',                    # Another WhatsApp QR wrapper
            ]

            qr_element = None
            for attempt in range(3):  # Retry up to 3 times
                for selector in qr_selectors:
                    try:
                        qr_element = self._page.query_selector(selector)
                        if qr_element and qr_element.is_visible():
                            self.logger.info(f"Found QR with selector: {selector} (attempt {attempt+1})")
                            break
                    except:
                        continue
                if qr_element:
                    break
                self.logger.info(f"QR not found yet, waiting 3s (attempt {attempt+1}/3)...")
                self._page.wait_for_timeout(3000)

            if qr_element:
                qr_element.screenshot(path=str(qr_path))
                self.logger.info("QR element screenshot saved!")
            else:
                # Fallback: full page screenshot
                self._page.screenshot(path=str(qr_path), full_page=False)
                self.logger.warning("QR element not found - saved full page screenshot")
                self.logger.info("Check whatsapp_debug.png for page state")

            # Print path prominently
            msg = f"""
{'='*60}
  QR CODE SAVED!
  Open this file to scan with your phone:
  >>> {qr_path}

  Debug screenshot (full page):
  >>> {debug_path}

  If QR is blank, try: sudo apt-get install -y xvfb
  Then run again - it will use virtual display automatically.
{'='*60}
"""
            print(msg)
            self.logger.info(f"QR saved to: {qr_path}")
            return True

        except Exception as e:
            self.logger.error(f"Failed to save QR screenshot: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def _ensure_logged_in(self) -> bool:
        """Ensure WhatsApp Web is logged in, wait for QR scan if needed."""
        try:
            self.logger.info("Navigating to WhatsApp Web...")
            self._page.goto('https://web.whatsapp.com', timeout=60000)

            # Wait for page to fully load
            self.logger.info("Waiting for WhatsApp Web to load...")
            self._page.wait_for_load_state('networkidle', timeout=30000)

            # Check if already logged in (chat list visible)
            try:
                self._page.wait_for_selector(
                    '[data-testid="chat-list"], [aria-label="Chat list"]',
                    timeout=15000
                )
                self.logger.info("Already logged in to WhatsApp Web")
                return True
            except PlaywrightTimeout:
                pass

            # Not logged in - need QR code
            self.logger.info("Not logged in - waiting for QR code to render...")

            # Wait for page content to settle (WhatsApp loads JS dynamically)
            self._page.wait_for_timeout(10000)

            # Log what we see on the page for debugging
            try:
                page_text = self._page.inner_text('body')
                if page_text:
                    preview = page_text[:200].replace('\n', ' ')
                    self.logger.info(f"Page content preview: {preview}")
            except:
                pass

            # Save QR code screenshot (with retries built in)
            self._save_qr_screenshot()

            # Now wait for user to scan - re-screenshot every 20 seconds
            self.logger.info("Waiting for you to scan the QR code...")
            self.logger.info("(You have 3 minutes to scan)")
            self.logger.info("QR code will be re-saved every 20 seconds in case it refreshes")

            for i in range(9):  # 9 * 20s = 3 minutes
                try:
                    self._page.wait_for_selector(
                        '[data-testid="chat-list"], [aria-label="Chat list"]',
                        timeout=20000
                    )
                    self.logger.info("Successfully logged in!")
                    return True
                except PlaywrightTimeout:
                    # Re-save QR in case it refreshed
                    self._save_qr_screenshot()
                    self.logger.info(f"Still waiting for QR scan... ({(i+1)*20}s elapsed)")

            self.logger.error("Timeout waiting for WhatsApp Web login (3 minutes)")
            self.logger.info("TIP: Make sure you scanned the QR code from whatsapp_qr.png")
            return False

        except Exception as e:
            self.logger.error(f"Error during login: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
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
        """Clean up browser resources and virtual display."""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()
        # Clean up Xvfb if we started it
        if hasattr(self, '_xvfb_process') and self._xvfb_process:
            self._xvfb_process.terminate()
            self.logger.info("Xvfb virtual display stopped")
        if hasattr(self, '_virtual_display') and self._virtual_display:
            self._virtual_display.stop()
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
