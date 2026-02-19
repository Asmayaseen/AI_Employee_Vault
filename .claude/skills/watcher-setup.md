# watcher-setup

Configure your first watcher (Gmail OR Filesystem) to continuously monitor and create action files in the vault.

## What you do

Implement a watcher script following the BaseWatcher pattern to detect new events and create `.md` files in `/Needs_Action/`.

## Choose Your Watcher

### Option A: Gmail Watcher (Monitors important emails)
### Option B: Filesystem Watcher (Monitors drop folder)

## Prerequisites

```bash
# For Gmail
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client

# For Filesystem
pip install watchdog
```

## Instructions

### Step 1: Create Base Watcher Class

```bash
mkdir -p ~/AI_Employee_Code/watchers
cd ~/AI_Employee_Code/watchers
```

Create `base_watcher.py`:

```python
import time
import logging
from pathlib import Path
from abc import ABC, abstractmethod
from datetime import datetime


class BaseWatcher(ABC):
    def __init__(self, vault_path: str, check_interval: int = 60):
        self.vault_path = Path(vault_path)
        self.needs_action = self.vault_path / 'Needs_Action'
        self.check_interval = check_interval
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logging()

    def _setup_logging(self):
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
        pass

    @abstractmethod
    def create_action_file(self, item) -> Path:
        pass

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Vault: {self.vault_path}')
        self.logger.info(f'Check interval: {self.check_interval}s')

        while True:
            try:
                items = self.check_for_updates()

                if items:
                    self.logger.info(f'Found {len(items)} new item(s)')
                    for item in items:
                        filepath = self.create_action_file(item)
                        self.logger.info(f'Created: {filepath.name}')
                else:
                    self.logger.debug('No new items')

            except KeyboardInterrupt:
                self.logger.info('Shutdown signal received')
                break
            except Exception as e:
                self.logger.error(f'Error: {e}', exc_info=True)

            time.sleep(self.check_interval)

        self.logger.info(f'Stopped {self.__class__.__name__}')
```

### Step 2A: Gmail Watcher (Choose this OR Filesystem)

#### Setup Gmail API

1. Go to https://console.cloud.google.com/
2. Create project: "AI-Employee"
3. Enable Gmail API
4. Create OAuth 2.0 credentials
5. Download `credentials.json`

#### Create gmail_watcher.py

```python
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from base_watcher import BaseWatcher
from datetime import datetime
from pathlib import Path
import base64

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(BaseWatcher):
    def __init__(self, vault_path: str, credentials_path: str):
        super().__init__(vault_path, check_interval=120)
        self.credentials_path = Path(credentials_path)
        self.token_path = self.credentials_path.parent / 'token.json'
        self.service = self._authenticate()
        self.processed_ids = set()

    def _authenticate(self):
        creds = None
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            self.token_path.write_text(creds.to_json())

        return build('gmail', 'v1', credentials=creds)

    def check_for_updates(self) -> list:
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread is:important',
                maxResults=10
            ).execute()

            messages = results.get('messages', [])
            return [m for m in messages if m['id'] not in self.processed_ids]
        except Exception as e:
            self.logger.error(f'Error checking Gmail: {e}')
            return []

    def create_action_file(self, message) -> Path:
        msg = self.service.users().messages().get(
            userId='me', id=message['id'], format='full'
        ).execute()

        headers = {h['name']: h['value'] for h in msg['payload']['headers']}
        sender = headers.get('From', 'Unknown')
        subject = headers.get('Subject', 'No Subject')

        body = msg.get('snippet', '')

        content = f'''---
type: email
message_id: {message['id']}
from: {sender}
subject: {subject}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Email Content

{body[:1000]}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing

## Notes
[AI Employee will add analysis here]
'''

        safe_subject = "".join(
            c if c.isalnum() or c in (' ', '-', '_') else '_'
            for c in subject
        )[:50]

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'EMAIL_{timestamp}_{safe_subject}.md'
        filepath = self.needs_action / filename

        filepath.write_text(content, encoding='utf-8')
        self.processed_ids.add(message['id'])

        return filepath


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

#### Run Gmail Watcher

```bash
# Setup credentials
mkdir -p ~/AI_Employee_Code/credentials
# Move credentials.json here

# First run (authenticate)
python gmail_watcher.py ~/AI_Employee_Vault ~/AI_Employee_Code/credentials/credentials.json
```

### Step 2B: Filesystem Watcher (Choose this OR Gmail)

#### Create filesystem_watcher.py

```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from base_watcher import BaseWatcher
from datetime import datetime
from pathlib import Path
import shutil
import time


class DropFolderHandler(FileSystemEventHandler):
    def __init__(self, watcher):
        self.watcher = watcher

    def on_created(self, event):
        if event.is_directory:
            return
        time.sleep(1)
        try:
            self.watcher.process_new_file(Path(event.src_path))
        except Exception as e:
            self.watcher.logger.error(f'Error: {e}')


class FilesystemWatcher(BaseWatcher):
    def __init__(self, vault_path: str, watch_folder: str):
        super().__init__(vault_path, check_interval=10)
        self.watch_folder = Path(watch_folder)
        self.watch_folder.mkdir(parents=True, exist_ok=True)
        self.observer = Observer()
        self.processed_files = set()

    def check_for_updates(self) -> list:
        files = [
            f for f in self.watch_folder.iterdir()
            if f.is_file() and f.name not in self.processed_files
        ]
        return files

    def create_action_file(self, file_path: Path) -> Path:
        return self.process_new_file(file_path)

    def process_new_file(self, source: Path) -> Path:
        if source.name in self.processed_files:
            return None

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        dest_name = f'FILE_{timestamp}_{source.name}'
        dest = self.needs_action / dest_name

        shutil.copy2(source, dest)

        meta_content = f'''---
type: file_drop
original_name: {source.name}
size_bytes: {source.stat().st_size}
received: {datetime.now().isoformat()}
status: pending
---

## File Information
- **Name:** {source.name}
- **Size:** {source.stat().st_size / 1024:.2f} KB
- **Received:** {datetime.now().isoformat()}

## Suggested Actions
- [ ] Review file contents
- [ ] Process according to type
- [ ] Move to appropriate folder

## Notes
[AI Employee will add analysis here]
'''

        meta_path = dest.with_suffix(dest.suffix + '.md')
        meta_path.write_text(meta_content, encoding='utf-8')

        self.processed_files.add(source.name)
        return meta_path

    def run(self):
        self.logger.info(f'Starting {self.__class__.__name__}')
        self.logger.info(f'Watching: {self.watch_folder}')

        event_handler = DropFolderHandler(self)
        self.observer.schedule(event_handler, str(self.watch_folder), recursive=False)
        self.observer.start()

        try:
            super().run()
        except KeyboardInterrupt:
            self.logger.info('Shutdown')
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

#### Run Filesystem Watcher

```bash
# Create watch folder
mkdir -p ~/AI_Employee_Drop

# Run watcher
python filesystem_watcher.py ~/AI_Employee_Vault ~/AI_Employee_Drop

# Test by dropping a file
echo "Test content" > ~/AI_Employee_Drop/test.txt
```

### Step 3: Process Management with PM2

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

# Setup auto-start
pm2 startup

# Monitor
pm2 logs ai-employee-gmail

# Stop
pm2 stop ai-employee-gmail
```

## Success Criteria

- [ ] BaseWatcher created
- [ ] Chosen watcher implemented
- [ ] Creates `.md` files in `/Needs_Action/`
- [ ] Valid frontmatter
- [ ] Logs to `/Logs/`
- [ ] Runs continuously
- [ ] PM2 configured

## Troubleshooting

**Gmail:**
- OAuth fails: Enable Gmail API in console
- Token expired: Delete token.json, re-auth
- Rate limit: Increase check_interval to 300+

**Filesystem:**
- Files not detected: Check watchdog installed
- Permission denied: Check folder permissions

## Next Steps

- `/claude-integration` - Connect Claude Code
- `/bronze-demo` - Record demo video
