"""
Email MCP Server - Gmail Integration for AI Employee.

This MCP server provides email capabilities to Claude Code:
- Send emails
- Create drafts
- Search emails
- Reply to emails

Implements rate limiting, audit logging, and approval workflow integration.

Usage:
    python email_mcp.py  # Start MCP server (for Claude Code integration)

MCP Configuration (claude mcp settings):
    {
        "servers": [{
            "name": "email",
            "command": "python",
            "args": ["/path/to/email_mcp.py"],
            "env": {"VAULT_PATH": "/path/to/vault"}
        }]
    }
"""

import os
import sys
import json
import base64
import logging
from pathlib import Path
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from dotenv import load_dotenv

# Google API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    print("Gmail API not installed. Run: pip install google-api-python-client google-auth-oauthlib")

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('EmailMCP')

# Gmail scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify'
]


@dataclass
class RateLimitConfig:
    """Rate limiting configuration."""
    max_per_hour: int = 20
    max_per_day: int = 100
    cooldown_minutes: int = 5


class EmailMCP:
    """
    Email MCP Server for Claude Code integration.
    Provides Gmail capabilities with safety guardrails.
    """

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path or os.getenv(
            'VAULT_PATH',
            '/mnt/d/Ai-Employee/AI_Employee_Vault'
        ))

        # Paths
        self.credentials_path = Path(os.getenv(
            'GMAIL_CREDENTIALS_PATH',
            self.vault_path / 'Watchers' / 'credentials.json'
        ))
        self.token_path = self.vault_path / 'Watchers' / 'token_send.json'
        self.logs_dir = self.vault_path / 'Logs'
        self.pending_approval = self.vault_path / 'Pending_Approval'

        # Ensure directories exist
        self.logs_dir.mkdir(exist_ok=True)
        self.pending_approval.mkdir(exist_ok=True)

        # Rate limiting
        self.rate_config = RateLimitConfig()
        self.send_history: List[datetime] = []

        # Known contacts (auto-approve replies)
        self.known_contacts_file = self.vault_path / 'known_contacts.json'
        self.known_contacts = self._load_known_contacts()

        # Gmail service
        self.service = None
        self._dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

        if GMAIL_AVAILABLE:
            self._authenticate()

        logger.info(f"Email MCP initialized (dry_run={self._dry_run})")

    def _load_known_contacts(self) -> set:
        """Load known/trusted contacts."""
        if self.known_contacts_file.exists():
            data = json.loads(self.known_contacts_file.read_text())
            return set(data.get('contacts', []))
        return set()

    def _save_known_contacts(self):
        """Save known contacts."""
        self.known_contacts_file.write_text(json.dumps({
            'contacts': list(self.known_contacts),
            'updated': datetime.now().isoformat()
        }, indent=2))

    def add_known_contact(self, email: str):
        """Add a contact to the known/trusted list."""
        self.known_contacts.add(email.lower())
        self._save_known_contacts()
        logger.info(f"Added known contact: {email}")

    def _authenticate(self):
        """Authenticate with Gmail API."""
        if not GMAIL_AVAILABLE:
            logger.error("Gmail API not available")
            return

        creds = None

        if self.token_path.exists():
            creds = Credentials.from_authorized_user_file(str(self.token_path), SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                logger.info("Refreshing credentials...")
                creds.refresh(Request())
            else:
                if not self.credentials_path.exists():
                    logger.error(f"Credentials not found: {self.credentials_path}")
                    return

                logger.info("Starting OAuth flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_path), SCOPES
                )
                creds = flow.run_local_server(port=0)

            self.token_path.write_text(creds.to_json())
            logger.info("Token saved")

        self.service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API authenticated")

    def _check_rate_limit(self) -> tuple[bool, str]:
        """Check if we're within rate limits."""
        now = datetime.now()

        # Clean old entries
        self.send_history = [
            t for t in self.send_history
            if now - t < timedelta(days=1)
        ]

        # Check hourly limit
        recent_hour = [t for t in self.send_history if now - t < timedelta(hours=1)]
        if len(recent_hour) >= self.rate_config.max_per_hour:
            return False, f"Hourly limit reached ({self.rate_config.max_per_hour})"

        # Check daily limit
        if len(self.send_history) >= self.rate_config.max_per_day:
            return False, f"Daily limit reached ({self.rate_config.max_per_day})"

        return True, "OK"

    def _log_action(self, action: str, details: dict):
        """Log email action."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "dry_run": self._dry_run,
            **details
        }

        log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}_email.json"
        try:
            logs = []
            if log_file.exists():
                logs = json.loads(log_file.read_text())
            logs.append(log_entry)
            log_file.write_text(json.dumps(logs, indent=2))
        except Exception as e:
            logger.error(f"Log write failed: {e}")

    def _create_approval_request(self, action: str, to: str, subject: str, body: str) -> Path:
        """Create an approval request file for email sending."""
        timestamp = datetime.now()
        safe_subject = subject.replace(' ', '_')[:20]
        filename = f"EMAIL_{timestamp.strftime('%Y%m%d_%H%M%S')}_{safe_subject}.md"

        content = f"""---
action: email_send
to: {to}
subject: "{subject}"
created: {timestamp.isoformat()}
expires: {(timestamp + timedelta(hours=24)).isoformat()}
status: pending
---

# Email Approval Request

## Recipient
**{to}**

## Subject
{subject}

## Body
```
{body}
```

---

## Instructions
- To **APPROVE**: Move this file to `/Approved/` folder
- To **REJECT**: Move this file to `/Rejected/` folder

---
*Created by Email MCP at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}*
"""

        filepath = self.pending_approval / filename
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Created approval request: {filename}")
        return filepath

    def _requires_approval(self, to: str) -> bool:
        """Determine if an email requires approval."""
        # Always approve in dry run
        if self._dry_run:
            return True

        # Known contacts don't need approval for replies
        if to.lower() in self.known_contacts:
            return False

        # New contacts always need approval
        return True

    def send_email(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str = None,
        force_approval: bool = False
    ) -> Dict[str, Any]:
        """
        Send an email.

        Args:
            to: Recipient email address
            subject: Email subject
            body: Plain text body
            html_body: Optional HTML body
            force_approval: Force approval even for known contacts

        Returns:
            Result dictionary with status and details
        """
        logger.info(f"Send email request: to={to}, subject={subject}")

        # Check rate limits
        allowed, reason = self._check_rate_limit()
        if not allowed:
            return {
                'status': 'rate_limited',
                'message': reason
            }

        # Check if approval required
        if force_approval or self._requires_approval(to):
            filepath = self._create_approval_request('send', to, subject, body)
            self._log_action('email_approval_requested', {
                'to': to,
                'subject': subject,
                'approval_file': str(filepath)
            })
            return {
                'status': 'pending_approval',
                'message': f'Approval request created: {filepath.name}',
                'approval_file': str(filepath)
            }

        # Execute send
        return self._execute_send(to, subject, body, html_body)

    def _execute_send(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str = None
    ) -> Dict[str, Any]:
        """Actually send the email via Gmail API."""
        if self._dry_run:
            logger.info(f"[DRY RUN] Would send email to {to}")
            self._log_action('email_dry_run', {'to': to, 'subject': subject})
            return {
                'status': 'dry_run',
                'message': f'Would send to {to}',
                'to': to,
                'subject': subject
            }

        if not self.service:
            return {'status': 'error', 'message': 'Gmail service not initialized'}

        try:
            # Create message
            if html_body:
                message = MIMEMultipart('alternative')
                message.attach(MIMEText(body, 'plain'))
                message.attach(MIMEText(html_body, 'html'))
            else:
                message = MIMEText(body)

            message['to'] = to
            message['subject'] = subject

            # Encode and send
            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw}
            ).execute()

            # Track for rate limiting
            self.send_history.append(datetime.now())

            # Log success
            self._log_action('email_sent', {
                'to': to,
                'subject': subject,
                'message_id': result.get('id')
            })

            logger.info(f"Email sent successfully to {to}")
            return {
                'status': 'success',
                'message_id': result.get('id'),
                'to': to,
                'subject': subject
            }

        except HttpError as e:
            logger.error(f"Gmail API error: {e}")
            self._log_action('email_error', {'to': to, 'error': str(e)})
            return {'status': 'error', 'message': str(e)}

    def create_draft(
        self,
        to: str,
        subject: str,
        body: str,
        html_body: str = None
    ) -> Dict[str, Any]:
        """
        Create an email draft (doesn't send).

        Args:
            to: Recipient email
            subject: Email subject
            body: Email body

        Returns:
            Result with draft ID
        """
        logger.info(f"Create draft: to={to}, subject={subject}")

        if self._dry_run:
            self._log_action('draft_dry_run', {'to': to, 'subject': subject})
            return {
                'status': 'dry_run',
                'message': f'Would create draft for {to}'
            }

        if not self.service:
            return {'status': 'error', 'message': 'Gmail service not initialized'}

        try:
            if html_body:
                message = MIMEMultipart('alternative')
                message.attach(MIMEText(body, 'plain'))
                message.attach(MIMEText(html_body, 'html'))
            else:
                message = MIMEText(body)

            message['to'] = to
            message['subject'] = subject

            raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw}}
            ).execute()

            self._log_action('draft_created', {
                'to': to,
                'subject': subject,
                'draft_id': draft.get('id')
            })

            return {
                'status': 'success',
                'draft_id': draft.get('id'),
                'to': to,
                'subject': subject
            }

        except HttpError as e:
            logger.error(f"Draft creation error: {e}")
            return {'status': 'error', 'message': str(e)}

    def search_emails(
        self,
        query: str,
        max_results: int = 10
    ) -> Dict[str, Any]:
        """
        Search emails.

        Args:
            query: Gmail search query (e.g., "from:someone@example.com")
            max_results: Maximum results to return

        Returns:
            List of matching emails
        """
        if not self.service:
            return {'status': 'error', 'message': 'Gmail service not initialized'}

        try:
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])
            emails = []

            for msg in messages[:max_results]:
                full_msg = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'Subject', 'Date']
                ).execute()

                headers = {
                    h['name']: h['value']
                    for h in full_msg['payload']['headers']
                }

                emails.append({
                    'id': msg['id'],
                    'from': headers.get('From', ''),
                    'subject': headers.get('Subject', ''),
                    'date': headers.get('Date', ''),
                    'snippet': full_msg.get('snippet', '')
                })

            return {
                'status': 'success',
                'count': len(emails),
                'emails': emails
            }

        except HttpError as e:
            logger.error(f"Search error: {e}")
            return {'status': 'error', 'message': str(e)}

    def get_capabilities(self) -> Dict[str, Any]:
        """Return MCP server capabilities."""
        return {
            'name': 'email-mcp',
            'version': '1.0.0',
            'capabilities': {
                'send_email': {
                    'description': 'Send an email (may require approval)',
                    'params': ['to', 'subject', 'body', 'html_body']
                },
                'create_draft': {
                    'description': 'Create email draft without sending',
                    'params': ['to', 'subject', 'body', 'html_body']
                },
                'search_emails': {
                    'description': 'Search emails with Gmail query',
                    'params': ['query', 'max_results']
                },
                'add_known_contact': {
                    'description': 'Add trusted contact (auto-approve)',
                    'params': ['email']
                }
            },
            'rate_limits': {
                'per_hour': self.rate_config.max_per_hour,
                'per_day': self.rate_config.max_per_day
            },
            'dry_run': self._dry_run
        }


# MCP Server Protocol Handler
def run_mcp_server():
    """Run as MCP server for Claude Code integration."""
    import sys

    mcp = EmailMCP()
    logger.info("Email MCP Server started")
    logger.info(f"Capabilities: {json.dumps(mcp.get_capabilities(), indent=2)}")

    # Simple JSON-RPC style message handling
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            method = request.get('method')
            params = request.get('params', {})

            if method == 'send_email':
                result = mcp.send_email(**params)
            elif method == 'create_draft':
                result = mcp.create_draft(**params)
            elif method == 'search_emails':
                result = mcp.search_emails(**params)
            elif method == 'add_known_contact':
                mcp.add_known_contact(params.get('email'))
                result = {'status': 'success'}
            elif method == 'capabilities':
                result = mcp.get_capabilities()
            else:
                result = {'status': 'error', 'message': f'Unknown method: {method}'}

            print(json.dumps(result))
            sys.stdout.flush()

        except json.JSONDecodeError as e:
            print(json.dumps({'status': 'error', 'message': f'Invalid JSON: {e}'}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({'status': 'error', 'message': str(e)}))
            sys.stdout.flush()


# CLI interface
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Email MCP Server')
    parser.add_argument('--server', action='store_true', help='Run as MCP server')
    parser.add_argument('--send', nargs=3, metavar=('TO', 'SUBJECT', 'BODY'), help='Send email')
    parser.add_argument('--draft', nargs=3, metavar=('TO', 'SUBJECT', 'BODY'), help='Create draft')
    parser.add_argument('--search', help='Search emails')
    parser.add_argument('--capabilities', action='store_true', help='Show capabilities')

    args = parser.parse_args()

    if args.server:
        run_mcp_server()
    else:
        mcp = EmailMCP()

        if args.capabilities:
            print(json.dumps(mcp.get_capabilities(), indent=2))
        elif args.send:
            result = mcp.send_email(args.send[0], args.send[1], args.send[2])
            print(json.dumps(result, indent=2))
        elif args.draft:
            result = mcp.create_draft(args.draft[0], args.draft[1], args.draft[2])
            print(json.dumps(result, indent=2))
        elif args.search:
            result = mcp.search_emails(args.search)
            print(json.dumps(result, indent=2))
        else:
            parser.print_help()
