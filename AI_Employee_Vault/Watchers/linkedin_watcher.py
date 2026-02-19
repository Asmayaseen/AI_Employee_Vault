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

    def _start_virtual_display(self):
        """Start Xvfb virtual display for headed mode in WSL2."""
        if os.environ.get('DISPLAY'):
            self.logger.info(f"DISPLAY already set: {os.environ['DISPLAY']}")
            return True

        # Try Xvfb directly
        try:
            import subprocess
            self._xvfb_process = subprocess.Popen(
                ['Xvfb', ':98', '-screen', '0', '1280x900x24', '-ac'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            os.environ['DISPLAY'] = ':98'
            import time
            time.sleep(1)
            self.logger.info("Started Xvfb virtual display on :98")
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
        """Apply anti-detection patches to avoid LinkedIn blocking."""
        stealth_js = """
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
        Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
        const originalQuery = window.navigator.permissions.query;
        window.navigator.permissions.query = (parameters) => (
            parameters.name === 'notifications' ?
                Promise.resolve({ state: Notification.permission }) :
                originalQuery(parameters)
        );
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Array;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Promise;
        delete window.cdc_adoQpoasnfa76pfcZLmcfl_Symbol;
        window.chrome = { runtime: {} };
        """
        page.add_init_script(stealth_js)
        self.logger.info("Applied browser stealth patches")

    def _find_element(self, selectors: list, timeout: int = 5000, retries: int = 2, description: str = "element"):
        """Try multiple selectors with retries, return first match or None."""
        for attempt in range(retries):
            for selector in selectors:
                try:
                    el = self._page.wait_for_selector(selector, timeout=timeout)
                    if el:
                        self.logger.info(f"Found {description} with selector: {selector}")
                        return el
                except PlaywrightTimeout:
                    continue
                except Exception:
                    continue
            if attempt < retries - 1:
                self.logger.debug(f"Retry {attempt + 1}/{retries} for {description}")
                self._page.wait_for_timeout(1000)
        self.logger.warning(f"Could not find {description} with any selector")
        return None

    def _find_all_elements(self, selectors: list, timeout: int = 5000, description: str = "elements"):
        """Try multiple selectors, return list of all matches from first successful selector."""
        for selector in selectors:
            try:
                self._page.wait_for_selector(selector, timeout=timeout)
                elements = self._page.query_selector_all(selector)
                if elements:
                    self.logger.info(f"Found {len(elements)} {description} with selector: {selector}")
                    return elements
            except PlaywrightTimeout:
                continue
            except Exception:
                continue
        self.logger.warning(f"Could not find any {description}")
        return []

    def _debug_screenshot(self, label: str):
        """Save timestamped debug screenshot for troubleshooting."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            path = self.vault_path / 'Watchers' / f'debug_{label}_{timestamp}.png'
            self._page.screenshot(path=str(path), full_page=False)
            self.logger.info(f"Debug screenshot saved: {path}")
        except Exception as e:
            self.logger.warning(f"Failed to save debug screenshot '{label}': {e}")

    def _save_login_screenshot(self):
        """Save login page screenshot for manual login."""
        screenshot_path = self.vault_path / 'Watchers' / 'linkedin_login.png'
        debug_path = self.vault_path / 'Watchers' / 'linkedin_debug.png'

        try:
            self._page.screenshot(path=str(debug_path), full_page=False)
            self.logger.info(f"Debug screenshot: {debug_path}")
            self.logger.info(f"Page title: {self._page.title()}")
            self.logger.info(f"Page URL: {self._page.url}")

            self._page.screenshot(path=str(screenshot_path), full_page=False)

            msg = f"""
{'='*60}
  LINKEDIN LOGIN PAGE SAVED!
  Open this file to see the login page:
  >>> {screenshot_path}

  Debug screenshot (full page):
  >>> {debug_path}

  If blank, try: sudo apt-get install -y xvfb
{'='*60}
"""
            print(msg)
            return True
        except Exception as e:
            self.logger.error(f"Failed to save screenshot: {e}")
            return False

    def _cleanup_browser(self):
        """Safely clean up browser resources for re-initialization."""
        try:
            if self._browser:
                self._browser.close()
        except Exception:
            pass
        try:
            if self._playwright:
                self._playwright.stop()
        except Exception:
            pass
        self._browser = None
        self._playwright = None
        self._page = None

    def _init_browser(self):
        """Initialize browser with persistent context.

        Strategy: Try headed mode with Xvfb first (best for LinkedIn).
        Fall back to headless with stealth patches if Xvfb unavailable.
        On failure, cleans up all state so next call can retry cleanly.
        """
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available")

        # Already initialized and healthy
        if self._playwright is not None and self._page is not None:
            return

        # Clean up any partial state from previous failed attempt
        if self._playwright is not None or self._browser is not None:
            self.logger.info("Cleaning up partial browser state before retry")
            self._cleanup_browser()

        try:
            # Try to get a virtual display for headed mode
            has_display = self._start_virtual_display()
            use_headless = not has_display

            if use_headless:
                self.logger.info("Using headless mode (no display available)")
                self.logger.info("TIP: Install Xvfb for better compatibility:")
                self.logger.info("  sudo apt-get install -y xvfb")
            else:
                self.logger.info("Using headed mode with virtual display")

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
                launch_args.append('--headless=new')

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

        except Exception as e:
            self.logger.error(f"Browser initialization failed: {e}")
            self._cleanup_browser()
            raise

    def _is_logged_in(self) -> bool:
        """Check if currently logged in using URL + fallback selectors."""
        current_url = self._page.url
        # Primary: URL-based detection (most reliable)
        if '/feed' in current_url or '/mynetwork' in current_url:
            self.logger.info(f"Logged in (URL check): {current_url}")
            return True

        # Fallback: aria-label / role / structural selectors
        login_selectors = [
            'nav[aria-label="Primary"]',
            'input[aria-label="Search"]',
            '.global-nav',
            '[class*="global-nav"]',
            'header nav',
        ]
        el = self._find_element(login_selectors, timeout=5000, retries=1, description="nav bar")
        if el:
            return True

        return False

    def _ensure_logged_in(self) -> bool:
        """Ensure logged in to LinkedIn."""
        try:
            self.logger.info("Navigating to LinkedIn...")
            self._page.goto('https://www.linkedin.com/feed/', timeout=60000)
            self._page.wait_for_load_state('domcontentloaded', timeout=30000)
            self._page.wait_for_timeout(3000)

            # Check if already logged in
            if self._is_logged_in():
                self.logger.info("Already logged in to LinkedIn")
                return True

            # Not logged in - save screenshot of login page
            self.logger.info("Not logged in - saving login page screenshot...")
            self._debug_screenshot('login_page')

            # Log page content for debugging
            try:
                page_text = self._page.inner_text('body')
                if page_text:
                    preview = page_text[:200].replace('\n', ' ')
                    self.logger.info(f"Page content: {preview}")
            except:
                pass

            self._save_login_screenshot()

            # Wait for login - re-screenshot every 20 seconds
            self.logger.info("Waiting for you to log in to LinkedIn...")
            self.logger.info("(You have 3 minutes)")
            self.logger.info("Login page screenshot will be re-saved every 20 seconds")

            for i in range(9):  # 9 * 20s = 3 minutes
                self._page.wait_for_timeout(20000)
                if self._is_logged_in():
                    self.logger.info("Successfully logged in!")
                    return True
                self._save_login_screenshot()
                self.logger.info(f"Still waiting for login... ({(i+1)*20}s elapsed)")

            self.logger.error("Timeout waiting for LinkedIn login (3 minutes)")
            return False

        except Exception as e:
            self.logger.error(f"Login error: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return False

    def check_for_updates(self) -> list:
        """Check LinkedIn for new messages and notifications."""
        if not PLAYWRIGHT_AVAILABLE:
            self.logger.error("Playwright not available")
            return []

        try:
            self._init_browser()
        except Exception as e:
            self.logger.error(f"Cannot initialize browser: {e}")
            self.logger.info("Will retry browser init on next check cycle")
            return []

        try:
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
            # If page crashed, reset browser for clean retry
            if self._page:
                try:
                    self._page.url  # test if page is still alive
                except Exception:
                    self.logger.warning("Browser page crashed, resetting for next cycle")
                    self._cleanup_browser()
            return []

    def _check_messages(self) -> list:
        """Check for new LinkedIn messages."""
        messages = []

        try:
            # Go to messaging
            self._page.goto('https://www.linkedin.com/messaging/', timeout=30000)
            self._page.wait_for_load_state('domcontentloaded', timeout=15000)
            self._page.wait_for_timeout(3000)

            # Wait for conversation list to load with resilient selectors
            container_selectors = [
                '.scaffold-layout__list',
                '[class*="msg-conversations-container"]',
                '[role="list"][aria-label]',
                'main ul',
            ]
            container = self._find_element(container_selectors, timeout=10000, description="message container")
            if not container:
                self._debug_screenshot('messages_no_container')
                self.logger.warning("Could not find message container")
                return messages

            # Take a debug screenshot to understand page state
            self._debug_screenshot('messages_page')

            # Find ALL conversation items inside the container first,
            # then filter for unread. The broad li:has(.notification-badge)
            # was matching non-message elements outside the conversation list.
            all_convo_selectors = [
                '.scaffold-layout__list li[class*="msg-conversation"]',
                '.scaffold-layout__list > li',
                '[class*="msg-conversations-container"] li',
                '[class*="msg-conversation-listitem"]',
                '[class*="msg-conversation-card"]',
            ]
            all_convos = self._find_all_elements(all_convo_selectors, timeout=8000, description="conversation items")

            if not all_convos:
                self.logger.info("No conversation items found")
                return messages

            # Filter for unread: check class attribute for "unread" keyword,
            # or look for a notification badge child element
            unread_convos = []
            for convo in all_convos:
                try:
                    class_attr = convo.get_attribute('class') or ''
                    if 'unread' in class_attr.lower():
                        unread_convos.append(convo)
                        continue
                    # Check for notification badge inside this conversation item
                    badge = convo.query_selector('.notification-badge, [class*="notification-badge"], [class*="unread-count"]')
                    if badge:
                        unread_convos.append(convo)
                except Exception:
                    continue

            self.logger.info(f"Found {len(all_convos)} conversations, {len(unread_convos)} unread")

            if not unread_convos:
                self.logger.info("No unread messages found")
                return messages

            for convo in unread_convos[:5]:  # Limit to 5
                try:
                    # Get sender name - prefer participant-name classes, then structural
                    name_selectors = [
                        '[class*="participant-name"]',
                        '[class*="msg-conversation-card__participant"]',
                        'h3 span',
                        'h3',
                        'a[href*="/in/"] span',
                        'a[href*="/in/"]',
                    ]
                    sender = "Unknown"
                    for sel in name_selectors:
                        name_el = convo.query_selector(sel)
                        if name_el:
                            text = name_el.inner_text().strip()
                            # Filter out non-name text (common noise patterns)
                            if text and len(text) < 80 and 'notification' not in text.lower() and 'update' not in text.lower():
                                sender = text
                                break

                    # Get preview - prefer snippet classes, then structural
                    preview_selectors = [
                        '[class*="message-snippet"]',
                        '[class*="msg-conversation-card__message"]',
                        'p',
                        'p span',
                    ]
                    preview = ""
                    for sel in preview_selectors:
                        preview_el = convo.query_selector(sel)
                        if preview_el:
                            text = preview_el.inner_text().strip()
                            if text and text != sender and len(text) > 1:
                                preview = text
                                break

                    self.logger.info(f"Message - sender: '{sender}', preview: '{preview[:60]}'")

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
            self._debug_screenshot('messages_error')

        return messages

    def _check_notifications(self) -> list:
        """Check LinkedIn notifications."""
        notifications = []

        try:
            # Go to notifications
            self._page.goto('https://www.linkedin.com/notifications/', timeout=30000)
            self._page.wait_for_load_state('domcontentloaded', timeout=15000)
            self._page.wait_for_timeout(3000)

            # Get recent notifications with resilient selectors
            card_selectors = [
                'article.nt-card',
                '[data-finite-scroll-hotkey-item]',
                'main [role="region"] article',
                '[class*="nt-card"]',
                'main section article',
                '.nt-card',
            ]
            notif_cards = self._find_all_elements(card_selectors, timeout=10000, description="notification cards")

            if not notif_cards:
                self._debug_screenshot('notifications_empty')
                self.logger.info("No notification cards found")
                return notifications

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
            self._debug_screenshot('notifications_error')

        return notifications

    def _check_connection_requests(self) -> list:
        """Check for pending connection requests."""
        requests = []

        try:
            # Go to network/invitations
            self._page.goto('https://www.linkedin.com/mynetwork/invitation-manager/', timeout=30000)
            self._page.wait_for_load_state('domcontentloaded', timeout=15000)
            self._page.wait_for_timeout(3000)

            # Scroll down to ensure invitation list loads
            self._page.evaluate('window.scrollBy(0, 300)')
            self._page.wait_for_timeout(2000)

            # Use JavaScript to find invitation cards by locating "Accept" buttons
            # and walking up to their card containers. This bypasses LinkedIn's
            # obfuscated CSS class names which break all CSS selector approaches.
            invitation_data = self._page.evaluate('''() => {
                // Find all buttons whose text is "Accept"
                const allButtons = [...document.querySelectorAll('button')];
                const acceptButtons = allButtons.filter(b => b.textContent.trim() === 'Accept');

                return acceptButtons.map(btn => {
                    // Walk up to find the card container (the <li> parent)
                    let card = btn;
                    let listItem = null;
                    for (let i = 0; i < 10; i++) {
                        card = card.parentElement;
                        if (!card) break;
                        if (card.tagName === 'LI') {
                            listItem = card;
                            break;
                        }
                    }
                    if (!listItem) {
                        // Fallback: go up 5 levels from the button
                        card = btn;
                        for (let i = 0; i < 5; i++) {
                            if (card.parentElement) card = card.parentElement;
                        }
                        listItem = card;
                    }

                    const text = listItem.innerText || '';
                    const html = listItem.innerHTML ? listItem.innerHTML.substring(0, 800) : '';

                    // Try to find name via link to profile
                    let nameFromLink = '';
                    const profileLink = listItem.querySelector('a[href*="/in/"]');
                    if (profileLink) {
                        // Get the visible text from the link (usually the name)
                        const spans = profileLink.querySelectorAll('span');
                        for (const s of spans) {
                            const t = s.textContent.trim();
                            if (t && t.length > 1 && t.length < 80) {
                                nameFromLink = t;
                                break;
                            }
                        }
                        if (!nameFromLink) {
                            nameFromLink = profileLink.textContent.trim().split('\\n')[0].trim();
                        }
                    }

                    return {
                        text: text.substring(0, 500),
                        html: html,
                        nameFromLink: nameFromLink
                    };
                });
            }''')

            if not invitation_data:
                self._debug_screenshot('connections_empty')
                self.logger.info("No connection requests found (no Accept buttons)")
                return requests

            self.logger.info(f"Found {len(invitation_data)} invitation cards via JS Accept-button approach")
            self._debug_screenshot('connections_page')

            button_words = {'accept', 'ignore', 'message', 'decline', 'withdraw', 'connect'}

            for idx, card_data in enumerate(invitation_data[:10]):
                try:
                    raw_text = card_data.get('text', '')
                    name_from_link = card_data.get('nameFromLink', '').strip()
                    self.logger.info(f"Invitation card {idx} raw text: {raw_text[:200]}")
                    if idx < 2:
                        self.logger.info(f"Invitation card {idx} nameFromLink: '{name_from_link}'")
                        self.logger.info(f"Invitation card {idx} HTML: {card_data.get('html', '')[:400]}")

                    # --- Extract name ---
                    name = "Unknown"

                    # Strategy 1: Profile link text (most reliable)
                    if name_from_link and len(name_from_link) < 80 and name_from_link.lower() not in button_words:
                        name = name_from_link

                    # Strategy 2: inner_text() parsing - first non-button line
                    if name == "Unknown":
                        lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                        candidate_lines = [l for l in lines if l.lower() not in button_words and len(l) < 80]
                        if candidate_lines:
                            name = candidate_lines[0]

                    self.logger.info(f"  Name: '{name}'")

                    # --- Extract title/subtitle ---
                    title = ""
                    lines = [l.strip() for l in raw_text.split('\n') if l.strip()]
                    candidate_lines = [l for l in lines if l.lower() not in button_words and len(l) < 80]

                    # Title is typically the 2nd non-button, non-name line
                    for line in candidate_lines:
                        if line == name:
                            continue
                        # Skip time references
                        if re.match(r'^\d+\s+(day|week|month|hour|minute|second)s?\s+ago$', line, re.IGNORECASE):
                            continue
                        # Skip mutual connections count
                        if re.match(r'^\d+\s+mutual\s+connection', line, re.IGNORECASE):
                            continue
                        title = line
                        break

                    self.logger.info(f"  Title: '{title[:60]}'")
                    self.logger.info(f"Connection - name: '{name}', title: '{title[:60]}'")

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
                    self.logger.warning(f"Error processing invitation {idx}: {e}")
                    continue

        except Exception as e:
            self.logger.warning(f"Error checking connection requests: {e}")
            self._debug_screenshot('connections_error')

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
            self._page.wait_for_load_state('domcontentloaded', timeout=15000)
            self._page.wait_for_timeout(2000)

            # Click on share box with resilient selectors
            share_selectors = [
                'button[aria-label*="Start a post"]',
                '[class*="share-box"] button',
                '.share-box-feed-entry__trigger',
                'button[class*="share-box"]',
            ]
            share_box = self._find_element(share_selectors, timeout=10000, description="share box")
            if not share_box:
                self._debug_screenshot('post_no_share_box')
                return {'status': 'error', 'message': 'Could not find share box'}
            share_box.click()
            self._page.wait_for_timeout(1500)

            # Wait for editor with resilient selectors
            editor_selectors = [
                '[role="textbox"][contenteditable="true"]',
                '[aria-label*="Text editor"]',
                '.ql-editor',
                '[contenteditable="true"]',
            ]
            editor = self._find_element(editor_selectors, timeout=10000, description="post editor")
            if not editor:
                self._debug_screenshot('post_no_editor')
                return {'status': 'error', 'message': 'Could not find post editor'}

            # Type content
            editor.fill(content)
            self._page.wait_for_timeout(1000)

            # Click post button with resilient selectors
            post_btn_selectors = [
                'button[aria-label="Post"]',
                'button:has-text("Post")',
                '.share-actions__primary-action',
                'button[class*="share-actions__primary"]',
            ]
            post_btn = self._find_element(post_btn_selectors, timeout=5000, description="post button")
            if not post_btn:
                self._debug_screenshot('post_no_button')
                return {'status': 'error', 'message': 'Could not find post button'}
            post_btn.click()

            # Wait for post to complete
            self._page.wait_for_timeout(3000)

            self.log_action('linkedin_post_created', {
                'content_preview': content[:100]
            })

            return {'status': 'success', 'message': 'Posted successfully'}

        except Exception as e:
            self.logger.error(f"Post failed: {e}")
            self._debug_screenshot('post_error')
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
        """Clean up browser resources and virtual display."""
        self._cleanup_browser()
        # Clean up Xvfb if we started it
        if hasattr(self, '_xvfb_process') and self._xvfb_process:
            self._xvfb_process.terminate()
            self.logger.info("Xvfb virtual display stopped")
        if hasattr(self, '_virtual_display') and self._virtual_display:
            self._virtual_display.stop()
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
