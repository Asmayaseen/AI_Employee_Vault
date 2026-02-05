"""
Gmail Watcher - Monitors Gmail for important/unread emails.

Requires:
1. Google Cloud Project with Gmail API enabled
2. OAuth credentials (credentials.json)
3. First run will open browser for authentication

Setup:
1. Place credentials.json in Watchers folder
2. Run: python gmail_watcher.py
3. Authenticate in browser (first time only)
"""

import os
import base64
import json
from pathlib import Path
from datetime import datetime
from email.utils import parsedate_to_datetime
from base_watcher import BaseWatcher

# Google API imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailWatcher(BaseWatcher):
    """
    Watches Gmail for unread/important emails.
    Creates action files in /Needs_Action for processing.
    """

    def __init__(self, vault_path: str = None, credentials_path: str = None, check_interval: int = 120):
        super().__init__(vault_path, check_interval)

        # Credentials paths
        self.credentials_path = Path(credentials_path or os.getenv(
            'GMAIL_CREDENTIALS_PATH',
            self.vault_path / 'Watchers' / 'credentials.json'
        ))
        self.token_path = self.vault_path / 'Watchers' / 'token.json'

        # Track processed emails
        self.processed_ids_file = self.vault_path / '.processed_emails'
        self.processed_ids = self._load_processed_ids()

        # Priority keywords
        self.priority_keywords = [
            'urgent', 'asap', 'important', 'critical',
            'invoice', 'payment', 'deadline', 'action required',
            'reply needed', 'follow up', 'reminder'
        ]

        # Initialize Gmail service
        self.service = None
        self._authenticate()

    def _load_processed_ids(self) -> set:
        """Load previously processed email IDs."""
        if self.processed_ids_file.exists():
            return set(self.processed_ids_file.read_text().splitlines())
        return set()

    def _save_processed_ids(self):
        """Save processed email IDs."""
        self.processed_ids_file.write_text('\n'.join(self.processed_ids))

    def _authenticate(self):
        """Authenticate with Gmail API."""
        creds = None

        # Load existing token
        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        # Refresh or get new credentials
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                self.logger.info("Refreshing expired credentials...")
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    self.logger.error(f"credentials.json not found at {self.credentials_path}")
                    self.logger.error("Please download from Google Cloud Console")
                    raise FileNotFoundError(f"Missing {self.credentials_path}")

                self.logger.info("Starting OAuth flow (browser will open)...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save token
            self.token_path.write_text(creds.to_json())
            self.logger.info(f"Token saved to {self.token_path}")

        # Build Gmail service
        self.service = build('gmail', 'v1', credentials=creds)
        self.logger.info("Gmail API authenticated successfully")

    def check_for_updates(self) -> list:
        """Check Gmail for unread important emails."""
        try:
            # Query for unread emails (can customize query)
            # Options: is:unread, is:important, label:INBOX, from:specific@email.com
            query = 'is:unread'

            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=10
            ).execute()

            messages = results.get('messages', [])

            # Filter out already processed
            new_messages = []
            for msg in messages:
                if msg['id'] not in self.processed_ids:
                    new_messages.append(msg)
                    self.logger.info(f"Found new email: {msg['id']}")

            return new_messages

        except HttpError as error:
            self.logger.error(f"Gmail API error: {error}")
            return []

    def create_action_file(self, message) -> Path:
        """Create action file for an email."""
        try:
            # Get full message details
            msg = self.service.users().messages().get(
                userId='me',
                id=message['id'],
                format='full'
            ).execute()

            # Extract headers
            headers = {}
            for header in msg['payload']['headers']:
                headers[header['name'].lower()] = header['value']

            sender = headers.get('from', 'Unknown')
            subject = headers.get('subject', 'No Subject')
            date_str = headers.get('date', '')

            # Parse date
            try:
                email_date = parsedate_to_datetime(date_str)
                date_formatted = email_date.strftime('%Y-%m-%d %H:%M')
            except:
                date_formatted = date_str

            # Get email snippet/body
            snippet = msg.get('snippet', '')

            # Determine priority
            priority = self._determine_priority(subject, snippet, msg.get('labelIds', []))

            # Create action file content
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            content = f'''---
type: email
source: gmail
message_id: {message['id']}
from: {sender}
subject: {subject}
received: {date_formatted}
processed: {datetime.now().isoformat()}
priority: {priority}
status: pending
labels: {', '.join(msg.get('labelIds', []))}
---

# Email: {subject}

## From
{sender}

## Date
{date_formatted}

## Preview
{snippet}

---

## Suggested Actions
- [ ] Read full email content
- [ ] Determine if reply needed
- [ ] Draft response (if needed)
- [ ] Forward to relevant party (if needed)
- [ ] Archive after processing

## Classification
- **Priority:** {priority}
- **Labels:** {', '.join(msg.get('labelIds', []))}

## Notes
> Add any notes about this email here

---
*Created by GmailWatcher*
'''

            # Save action file
            safe_subject = "".join(c for c in subject[:30] if c.isalnum() or c in ' -_').strip()
            safe_subject = safe_subject.replace(' ', '_')
            filename = f"EMAIL_{timestamp}_{safe_subject}.md"
            filepath = self.needs_action / filename
            filepath.write_text(content)

            # Mark as processed
            self.processed_ids.add(message['id'])
            self._save_processed_ids()

            # Log action
            self.log_action("email_received", {
                "message_id": message['id'],
                "from": sender,
                "subject": subject,
                "priority": priority,
                "action_file": str(filepath)
            })

            return filepath

        except HttpError as error:
            self.logger.error(f"Error fetching email {message['id']}: {error}")
            raise

    def _determine_priority(self, subject: str, body: str, labels: list) -> str:
        """Determine email priority based on content and labels."""
        text = f"{subject} {body}".lower()

        # Check for IMPORTANT label
        if 'IMPORTANT' in labels:
            return 'high'

        # Check for priority keywords
        for keyword in self.priority_keywords:
            if keyword in text:
                return 'high'

        # Check for STARRED
        if 'STARRED' in labels:
            return 'medium'

        return 'normal'

    def get_email_body(self, message_id: str) -> str:
        """Get full email body (useful for detailed processing)."""
        try:
            msg = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            # Extract body from payload
            payload = msg.get('payload', {})
            body = self._extract_body(payload)
            return body

        except HttpError as error:
            self.logger.error(f"Error getting email body: {error}")
            return ""

    def _extract_body(self, payload: dict) -> str:
        """Extract text body from email payload."""
        body = ""

        if 'body' in payload and payload['body'].get('data'):
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        elif 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if part['body'].get('data'):
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
                elif 'parts' in part:
                    body = self._extract_body(part)
                    if body:
                        break

        return body


def test_connection():
    """Test Gmail API connection."""
    print("Testing Gmail API connection...")
    print("=" * 50)

    vault_path = os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')

    try:
        watcher = GmailWatcher(vault_path=vault_path)
        print("Authentication successful!")

        # Try to fetch profile
        profile = watcher.service.users().getProfile(userId='me').execute()
        print(f"Connected as: {profile['emailAddress']}")
        print(f"Total messages: {profile['messagesTotal']}")

        print("\nRunning single check...")
        items = watcher.run_once()
        print(f"Found {len(items)} new unread email(s)")

        return True

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nSetup required:")
        print("1. Go to https://console.cloud.google.com/")
        print("2. Create project and enable Gmail API")
        print("3. Create OAuth credentials (Desktop App)")
        print("4. Download and save as: Watchers/credentials.json")
        return False

    except Exception as e:
        print(f"\nError: {e}")
        return False


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        test_connection()
    else:
        vault_path = os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')

        print("Starting Gmail Watcher...")
        print(f"Vault: {vault_path}")
        print("Press Ctrl+C to stop\n")

        try:
            watcher = GmailWatcher(vault_path=vault_path)
            watcher.run()
        except FileNotFoundError:
            print("\nPlease complete Gmail API setup first.")
            print("Run: python gmail_watcher.py --test")
