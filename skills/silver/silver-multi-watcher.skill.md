# Agent Skill: Silver Multi-Watcher

**Skill ID:** `silver-multi-watcher`
**Tier:** Silver (Functional Assistant)
**Estimated Time:** 3-4 hours
**Prerequisites:** Bronze tier complete, one watcher operational

## Purpose

Expand perception layer by adding multiple watchers (Gmail + WhatsApp/LinkedIn) running simultaneously, coordinated by an orchestrator.

## Success Criteria

- [ ] At least 2 watchers running concurrently
- [ ] Orchestrator script managing all watchers
- [ ] Each watcher creates properly tagged action files
- [ ] No duplicate processing
- [ ] All watchers log independently
- [ ] PM2 managing all processes
- [ ] Graceful shutdown and restart

## Architecture

```
Orchestrator (orchestrator.py)
    ├── Gmail Watcher (port 5001)
    ├── WhatsApp Watcher (port 5002)
    └── LinkedIn Watcher (port 5003 - optional)

All write to → ~/AI_Employee_Vault/Needs_Action/
All log to → ~/AI_Employee_Vault/Logs/
```

## Implementation

### Step 1: Create Orchestrator

Create `orchestrator.py`:

```python
import subprocess
import time
import logging
from pathlib import Path
from datetime import datetime
import signal
import sys

class WatcherOrchestrator:
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.watchers = {}
        self.running = True
        self.logger = self._setup_logging()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _setup_logging(self):
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / 'Orchestrator.log'

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        logger = logging.getLogger('Orchestrator')
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)

        return logger

    def _signal_handler(self, signum, frame):
        self.logger.info(f'Received signal {signum}, shutting down...')
        self.running = False

    def register_watcher(self, name: str, script_path: str, args: list):
        """Register a watcher process"""
        self.watchers[name] = {
            'script': script_path,
            'args': args,
            'process': None,
            'restarts': 0,
            'last_start': None
        }
        self.logger.info(f'Registered watcher: {name}')

    def start_watcher(self, name: str):
        """Start a specific watcher"""
        if name not in self.watchers:
            self.logger.error(f'Watcher {name} not registered')
            return False

        watcher = self.watchers[name]
        cmd = ['python3', watcher['script']] + watcher['args']

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            watcher['process'] = process
            watcher['last_start'] = datetime.now()
            watcher['restarts'] += 1

            self.logger.info(f'Started {name} (PID: {process.pid})')
            return True

        except Exception as e:
            self.logger.error(f'Failed to start {name}: {e}')
            return False

    def check_watcher_health(self, name: str) -> bool:
        """Check if watcher is still running"""
        if name not in self.watchers:
            return False

        watcher = self.watchers[name]
        if watcher['process'] is None:
            return False

        # Check if process is still alive
        poll = watcher['process'].poll()
        return poll is None  # None means still running

    def restart_watcher(self, name: str):
        """Restart a failed watcher"""
        self.logger.warning(f'Restarting {name}...')

        watcher = self.watchers[name]

        # Try to terminate gracefully
        if watcher['process']:
            try:
                watcher['process'].terminate()
                watcher['process'].wait(timeout=5)
            except:
                watcher['process'].kill()

        # Wait a bit before restart
        time.sleep(2)

        # Restart
        self.start_watcher(name)

    def run(self):
        """Main orchestrator loop"""
        self.logger.info('Starting Watcher Orchestrator')

        # Start all registered watchers
        for name in self.watchers:
            self.start_watcher(name)

        # Monitor loop
        while self.running:
            try:
                for name in list(self.watchers.keys()):
                    if not self.check_watcher_health(name):
                        self.logger.error(f'{name} is not running!')
                        self.restart_watcher(name)

                # Health check every 30 seconds
                time.sleep(30)

            except Exception as e:
                self.logger.error(f'Orchestrator error: {e}')

        # Shutdown all watchers
        self.logger.info('Shutting down all watchers...')
        for name, watcher in self.watchers.items():
            if watcher['process']:
                try:
                    watcher['process'].terminate()
                    watcher['process'].wait(timeout=5)
                    self.logger.info(f'Stopped {name}')
                except:
                    watcher['process'].kill()
                    self.logger.warning(f'Force killed {name}')

        self.logger.info('Orchestrator shutdown complete')


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print('Usage: python orchestrator.py <vault_path>')
        sys.exit(1)

    vault_path = sys.argv[1]

    orchestrator = WatcherOrchestrator(vault_path)

    # Register watchers (adjust paths to your setup)
    orchestrator.register_watcher(
        'gmail',
        'watchers/gmail_watcher.py',
        [vault_path, 'credentials/credentials.json']
    )

    orchestrator.register_watcher(
        'whatsapp',
        'watchers/whatsapp_watcher.py',
        [vault_path, 'credentials/whatsapp_session']
    )

    # Optional: LinkedIn watcher
    # orchestrator.register_watcher(
    #     'linkedin',
    #     'watchers/linkedin_watcher.py',
    #     [vault_path]
    # )

    orchestrator.run()
```

### Step 2: Create WhatsApp Watcher

Create `whatsapp_watcher.py`:

```python
from playwright.sync_api import sync_playwright
from base_watcher import BaseWatcher
from pathlib import Path
from datetime import datetime
import time


class WhatsAppWatcher(BaseWatcher):
    """Watches WhatsApp Web for urgent messages"""

    def __init__(self, vault_path: str, session_path: str):
        super().__init__(vault_path, check_interval=30)
        self.session_path = Path(session_path)
        self.keywords = ['urgent', 'asap', 'invoice', 'payment', 'help', 'emergency']
        self.processed_messages = set()

    def check_for_updates(self) -> list:
        """Check WhatsApp Web for unread messages with keywords"""
        try:
            with sync_playwright() as p:
                # Launch with persistent session to stay logged in
                browser = p.chromium.launch_persistent_context(
                    self.session_path,
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )

                page = browser.pages[0] if browser.pages else browser.new_page()
                page.goto('https://web.whatsapp.com', timeout=60000)

                # Wait for WhatsApp to load
                try:
                    page.wait_for_selector('[data-testid="chat-list"]', timeout=30000)
                except:
                    self.logger.error('WhatsApp did not load in time')
                    browser.close()
                    return []

                # Find unread chats
                unread_chats = page.query_selector_all('[aria-label*="unread"]')

                messages = []
                for chat in unread_chats[:10]:  # Process max 10 at once
                    try:
                        # Get chat name
                        chat_name_elem = chat.query_selector('[dir="auto"]')
                        chat_name = chat_name_elem.inner_text() if chat_name_elem else 'Unknown'

                        # Click to open chat
                        chat.click()
                        time.sleep(1)

                        # Get latest message
                        message_elems = page.query_selector_all('[data-testid="msg-container"]')
                        if message_elems:
                            last_msg = message_elems[-1]
                            msg_text = last_msg.inner_text().lower()

                            # Check for keywords
                            if any(kw in msg_text for kw in self.keywords):
                                msg_id = f'{chat_name}_{datetime.now().timestamp()}'

                                if msg_id not in self.processed_messages:
                                    messages.append({
                                        'id': msg_id,
                                        'from': chat_name,
                                        'text': last_msg.inner_text(),
                                        'timestamp': datetime.now().isoformat()
                                    })

                    except Exception as e:
                        self.logger.warning(f'Error processing chat: {e}')

                browser.close()
                return messages

        except Exception as e:
            self.logger.error(f'WhatsApp check error: {e}')
            return []

    def create_action_file(self, message) -> Path:
        """Create action file for WhatsApp message"""
        content = f'''---
type: whatsapp
message_id: {message['id']}
from: {message['from']}
received: {message['timestamp']}
priority: high
status: pending
keywords_matched: urgent
---

## Message Content

{message['text']}

## Suggested Actions
- [ ] Read full conversation context
- [ ] Draft appropriate response
- [ ] Create approval request for sending reply
- [ ] Mark as handled

## HITL Required
⚠️ All WhatsApp replies require human approval before sending.

## Notes
[AI Employee will add analysis here]
'''

        safe_from = "".join(
            c if c.isalnum() or c in (' ', '-', '_') else '_'
            for c in message['from']
        )[:30]

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'WHATSAPP_{timestamp}_{safe_from}.md'
        filepath = self.needs_action / filename

        filepath.write_text(content, encoding='utf-8')
        self.processed_messages.add(message['id'])

        return filepath


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print('Usage: python whatsapp_watcher.py <vault_path> <session_path>')
        sys.exit(1)

    vault_path = sys.argv[1]
    session_path = sys.argv[2]

    watcher = WhatsAppWatcher(vault_path, session_path)
    watcher.run()
```

### Step 3: Setup WhatsApp Session

```bash
# Install playwright
pip install playwright
python -m playwright install chromium

# Create session directory
mkdir -p ~/AI_Employee_Code/credentials/whatsapp_session

# First-time setup (manual QR code scan)
# You'll need to scan QR code once to establish session
python -c "
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch_persistent_context(
        '~/AI_Employee_Code/credentials/whatsapp_session',
        headless=False
    )
    page = browser.pages[0]
    page.goto('https://web.whatsapp.com')
    print('Scan QR code in the browser window...')
    time.sleep(60)  # Wait for scan
    browser.close()
"
```

### Step 4: Run Orchestrator with PM2

```bash
cd ~/AI_Employee_Code

# Start orchestrator
pm2 start orchestrator.py \
  --name "ai-employee-orchestrator" \
  --interpreter python3 \
  -- ~/AI_Employee_Vault

# Monitor all watchers
pm2 logs ai-employee-orchestrator

# Check status
pm2 status

# Save configuration
pm2 save
pm2 startup
```

### Step 5: Test Multi-Watcher System

```bash
# Send test email (Gmail watcher should detect)
# Send test WhatsApp with keyword "urgent" (WhatsApp watcher should detect)

# Watch Needs_Action folder
watch -n 2 "ls -lt ~/AI_Employee_Vault/Needs_Action/ | head -20"

# Monitor logs
tail -f ~/AI_Employee_Vault/Logs/*.log
```

## Validation Checklist

- [ ] Orchestrator starts all watchers
- [ ] Gmail watcher creates EMAIL_*.md files
- [ ] WhatsApp watcher creates WHATSAPP_*.md files
- [ ] No duplicate file creation
- [ ] Each watcher logs independently
- [ ] Orchestrator restarts failed watchers
- [ ] Graceful shutdown with Ctrl+C
- [ ] PM2 shows all processes running
- [ ] Can handle 5+ simultaneous events

## Troubleshooting

**WhatsApp session lost:**
- Re-run QR code scan setup
- Check session directory exists
- Verify browser profile not corrupted

**Orchestrator doesn't restart watchers:**
- Check health check interval (30s)
- Verify watcher scripts have correct paths
- Check logs for specific errors

**High CPU usage:**
- Increase check_interval for each watcher
- Use headless mode for browsers
- Limit max messages processed per cycle

## Next Steps

- `/silver-mcp-email` - Implement email MCP server
- `/silver-hitl-workflow` - Automate approval workflow
- `/silver-scheduler` - Add cron scheduling

## References

- Constitution Principle VIII: Watcher Pattern
- Hackathon Section 2A: Perception Layer
- Silver Tier Requirements (20-30 hours)
