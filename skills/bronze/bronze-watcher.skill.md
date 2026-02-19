# Agent Skill: Bronze Watcher

**Skill ID:** `bronze-watcher`
**Tier:** Bronze (Foundation)
**Estimated Time:** 2-3 hours
**Prerequisites:** Bronze Vault Setup completed, Python 3.13+, Gmail API credentials OR filesystem to monitor

## Purpose

Implement the first watcher script following the Watcher pattern to continuously monitor Gmail OR filesystem and create actionable `.md` files in the vault's `/Needs_Action/` folder.

## Success Criteria

- [ ] Base watcher class (`BaseWatcher`) implemented
- [ ] One concrete watcher implemented (Gmail OR Filesystem)
- [ ] Watcher creates valid `.md` files in `/Needs_Action/` with structured frontmatter
- [ ] Watcher runs continuously without crashing
- [ ] Watcher logs health checks and errors
- [ ] Watcher can be stopped and restarted gracefully
- [ ] Process management configured (PM2 or manual)

## Architecture

### Base Watcher Pattern

All watchers inherit from `BaseWatcher` abstract class:

```python
# base_watcher.py
import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    """Base class for all watcher implementations"""

    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging to file and console"""
        log_dir = self.vault_path / 'Logs'
        log_dir.mkdir(exist_ok=True)

        log_file = log_dir / f'{self.__class__.__name__}.log'

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.INFO)

    @abstractmethod
    def check_for_updates(self) -> list:
        """Check external source for new items. Returns list of items to process."""
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        """Create .md file in Needs_Action folder. Returns path to created file."""
        pass

    def run(self):
        """Main loop - continuously checks for updates"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault path: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval} seconds')

        while True:
            try:
                items = self.check_for_updates()

                if items:
                    self.logger.info(f'Found {len(items)} new item(s)')
                    for item in items:
                        filepath = self.create_action_file(item)
                        self.logger.info(f'Created action file: {filepath.name}')
                else:
                    self.logger.debug('No new items found')

            except KeyboardInterrupt:
                self.logger.info('Received shutdown signal')
                break
            except Exception as e:
                self.logger.error(f'Error in main loop: {e}', exc_info=True)

            time.sleep(self.check_interval)

        self.logger.info(f'Stopped {self.__class__.__name__}')
```

## Option A: Gmail Watcher

### Prerequisites

1. **Enable Gmail API**
   - Go to https://console.cloud.google.com/
   - Create new project: "AI-Employee"
   - Enable Gmail API
   - Create OAuth 2.0 credentials
   - Download `credentials.json`

2. **Install Dependencies**
   ```bash
   pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
   ```

### Implementation

```python
# gmail_watcher.py
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from base_watcher import BaseWatcher
from datetime import datetime
from pathlib import Path
import base64
import os.path

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(BaseWatcher):
    """Watches Gmail for important unread emails"""

    def __init__(self, vault_path: str, credentials_path: str):
        super().__init__(vault_path, check_interval=120)  # Check every 2 minutes
        self.credentials_path = Path(credentials_path)
        self.token_path = self.credentials_path.parent / 'token.json'
        self.service = self._authenticate()
        self.processed_ids = set()

    def _authenticate(self):
        """Authenticate with Gmail API"""
        creds = None

        # Token file stores user's access and refresh tokens
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            self.token_path.write_text(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def check_for_updates(self) -> list:
        """Check for new important unread emails"""
        try:
            # Query for unread important emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])

            # Filter out already processed messages
            new_messages = [
                m for m in messages
                if m['id'] not in self.processed_ids
            ]

            return new_messages

        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            return []

    def create_action_file(self, message) -> Path:
        """Create markdown file for email in Needs_Action folder"""
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()

            # Extract headers
            headers = {
                h['name']: h['value']
                for h in msg['payload']['headers']
            }

            sender = headers.get('From', 'Unknown')
            subject = headers.get('Subject', 'No Subject')
            date = headers.get('Date', 'Unknown')

            # Get email body (simplified - may need to handle multipart)
            body = ''
            if 'parts' in msg['payload']:
                for part in msg['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = base64.urlsafe_b64decode(
                            part['body']['data']
                        ).decode('utf-8')
                        break
            elif 'body' in msg['payload'] and 'data' in msg['payload']['body']:
                body = base64.urlsafe_b64decode(
                    msg['payload']['body']['data']
                ).decode('utf-8')
            else:
                body = msg.get('snippet', '')

            # Create markdown content
            content = f'''---
type: email
message_id: {message['id']}
from: {sender}
subject: {subject}
received: {datetime.now().isoformat()}
date: {date}
priority: high
status: pending
---

## Email Content

{body[:1000]}  <!-- Truncated to first 1000 chars -->

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Flag for follow-up

## Notes
[AI Employee will add analysis and recommendations here]
'''

            # Create safe filename
            safe_subject = "".join(
                c if c.isalnum() or c in (' ', '-', '_') else '_'
                for c in subject
            )[:50]

            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'EMAIL_{timestamp}_{safe_subject}.md'
            filepath = self.needs_action / filename

            # Write file
            filepath.write_text(content, encoding='utf-8')

            # Mark as processed
            self.processed_ids.add(message['id'])

            return filepath

        except Exception as e:
            self.logger.error(f'Error creating action file: {e}')
            raise


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print('Usage: python gmail_watcher.py <vault_path> <credentials_path>')
        sys.exit(1)

    vault_path = sys.argv[1]
    credentials_path = sys.argv[2]

    watcher = GmailWatcher(vault_path, credentials_path)
    watcher.run()
```

### Setup Steps for Gmail Watcher

1. **Save base_watcher.py**
   ```bash
   mkdir -p ~/AI_Employee_Code/watchers
   cd ~/AI_Employee_Code/watchers
   # Save BaseWatcher code to base_watcher.py
   ```

2. **Save gmail_watcher.py**
   ```bash
   # Save GmailWatcher code to gmail_watcher.py
   ```

3. **Setup credentials**
   ```bash
   mkdir -p ~/AI_Employee_Code/credentials
   # Move downloaded credentials.json here
   ```

4. **First run (authenticate)**
   ```bash
   python gmail_watcher.py ~/AI_Employee_Vault ~/AI_Employee_Code/credentials/credentials.json
   # Browser will open for OAuth consent
   # token.json will be created after successful auth
   ```

## Option B: Filesystem Watcher

### Prerequisites

```bash
pip install watchdog
```

### Implementation

```python
# filesystem_watcher.py
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from base_watcher import BaseWatcher
from datetime import datetime
from pathlib import Path
import shutil
import time


class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events in the drop folder"""

    def __init__(self, watcher):
        self.watcher = watcher

    def on_created(self, event):
        """Called when a file is created in the watched folder"""
        if event.is_directory:
            return

        # Small delay to ensure file write is complete
        time.sleep(1)

        try:
            self.watcher.process_new_file(Path(event.src_path))
        except Exception as e:
            self.watcher.logger.error(f'Error processing file: {e}')


class FilesystemWatcher(BaseWatcher):
    """Watches a drop folder for new files"""

    def __init__(self, vault_path: str, watch_folder: str):
        super().__init__(vault_path, check_interval=10)
        self.watch_folder = Path(watch_folder)
        self.watch_folder.mkdir(parents=True, exist_ok=True)
        self.observer = Observer()
        self.processed_files = set()

    def check_for_updates(self) -> list:
        """Scan for any files that weren't caught by watchdog"""
        files = [
            f for f in self.watch_folder.iterdir()
            if f.is_file() and f.name not in self.processed_files
        ]
        return files

    def create_action_file(self, file_path: Path) -> Path:
        """Create metadata file and copy to Needs_Action"""
        return self.process_new_file(file_path)

    def process_new_file(self, source: Path) -> Path:
        """Process a newly detected file"""
        if source.name in self.processed_files:
            return None

        self.logger.info(f'Processing new file: {source.name}')

        # Copy file to Needs_Action
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest_name = f'FILE_{timestamp}_{source.name}'
        dest = self.needs_action / dest_name

        shutil.copy2(source, dest)

        # Create metadata file
        meta_content = f'''---
type: file_drop
original_name: {source.name}
original_path: {source}
size_bytes: {source.stat().st_size}
received: {datetime.now().isoformat()}
status: pending
---

## File Information

- **Original Name:** {source.name}
- **File Size:** {source.stat().st_size / 1024:.2f} KB
- **Received:** {datetime.now().isoformat()}
- **Location:** {dest}

## Suggested Actions
- [ ] Review file contents
- [ ] Process according to type
- [ ] Move to appropriate folder
- [ ] Delete original from drop folder

## Notes
[AI Employee will add analysis here]
'''

        meta_path = dest.with_suffix(dest.suffix + '.md')
        meta_path.write_text(meta_content, encoding='utf-8')

        # Mark as processed
        self.processed_files.add(source.name)

        # Optionally delete original
        # source.unlink()  # Uncomment to auto-delete from drop folder

        return meta_path

    def run(self):
        """Start watching the folder"""
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Watching: {self.watch_folder}')

        # Setup observer for real-time detection
        event_handler = DropFolderHandler(self)
        self.observer.schedule(event_handler, str(self.watch_folder), recursive=False)
        self.observer.start()

        try:
            # Also run periodic check (belt and suspenders)
            super().run()
        except KeyboardInterrupt:
            self.logger.info('Received shutdown signal')
        finally:
            self.observer.stop()
            self.observer.join()


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 3:
        print('Usage: python filesystem_watcher.py <vault_path> <watch_folder>')
        sys.exit(1)

    vault_path = sys.argv[1]
    watch_folder = sys.argv[2]

    watcher = FilesystemWatcher(vault_path, watch_folder)
    watcher.run()
```

### Setup Steps for Filesystem Watcher

1. **Create watch folder**
   ```bash
   mkdir -p ~/AI_Employee_Drop
   ```

2. **Run watcher**
   ```bash
   python filesystem_watcher.py ~/AI_Employee_Vault ~/AI_Employee_Drop
   ```

3. **Test by dropping a file**
   ```bash
   echo "Test content" > ~/AI_Employee_Drop/test.txt
   # Check ~/AI_Employee_Vault/Needs_Action/ for new files
   ```

## Process Management (Optional but Recommended)

### Using PM2 (Recommended)

```bash
# Install PM2
npm install -g pm2

# Start Gmail watcher
pm2 start gmail_watcher.py \
  --name "ai-employee-gmail" \
  --interpreter python3 \
  -- ~/AI_Employee_Vault ~/AI_Employee_Code/credentials/credentials.json

# OR start filesystem watcher
pm2 start filesystem_watcher.py \
  --name "ai-employee-files" \
  --interpreter python3 \
  -- ~/AI_Employee_Vault ~/AI_Employee_Drop

# Save configuration
pm2 save

# Setup auto-start on boot
pm2 startup

# Monitor logs
pm2 logs ai-employee-gmail

# Stop watcher
pm2 stop ai-employee-gmail

# Restart watcher
pm2 restart ai-employee-gmail
```

### Manual Process Management

```bash
# Run in background
nohup python gmail_watcher.py ~/AI_Employee_Vault ~/AI_Employee_Code/credentials/credentials.json > /tmp/gmail_watcher.log 2>&1 &

# Save PID
echo $! > /tmp/gmail_watcher.pid

# Stop process
kill $(cat /tmp/gmail_watcher.pid)
```

## Validation Checklist

- [ ] BaseWatcher class created and functional
- [ ] Chosen watcher (Gmail OR Filesystem) implemented
- [ ] Watcher creates `.md` files in `/Needs_Action/` with valid frontmatter
- [ ] Files include: type, timestamp, status, and content
- [ ] Watcher logs to `/Logs/` directory
- [ ] Watcher runs continuously without errors
- [ ] Can be stopped with Ctrl+C gracefully
- [ ] Process management configured (PM2 or systemd)
- [ ] Test files created successfully when trigger occurs

## Troubleshooting

**Gmail Issues:**
- `credentials.json` not found: Verify path is absolute
- OAuth fails: Ensure Gmail API is enabled in Google Cloud Console
- Token expired: Delete `token.json` and re-authenticate
- Rate limiting: Increase `check_interval` to 300+ seconds

**Filesystem Issues:**
- Files not detected: Verify watchdog installed: `pip show watchdog`
- Permission denied: Ensure watch folder has write permissions
- Duplicate processing: Check `processed_files` set is persisting

**General Issues:**
- Logs not appearing: Check `/Logs/` folder exists in vault
- Process dies: Use PM2 for auto-restart on crash
- High CPU usage: Increase `check_interval` value

## Next Steps

After completing this skill, proceed to:
- **Bronze Claude Integration** (`bronze-claude-integration.skill.md`) - Connect Claude Code to vault
- **Silver Multi-Watcher** (Silver tier) - Add more watchers

## References

- Constitution Principle VIII: Watcher Pattern for Continuous Perception
- Hackathon Document Section 2A: Perception (The "Watchers")
- Python watchdog docs: https://python-watchdog.readthedocs.io/
- Gmail API docs: https://developers.google.com/gmail/api
