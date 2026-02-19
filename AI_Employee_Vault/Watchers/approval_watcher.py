"""
Approval Watcher - Human-in-the-Loop Workflow Manager.

Monitors the approval workflow folders:
- /Pending_Approval: Items waiting for human review
- /Approved: Human-approved items ready for execution
- /Rejected: Human-rejected items

When items are moved to /Approved, triggers the appropriate MCP action.

Features:
- Desktop notifications for new approval requests
- Timeout handling for stale approvals
- Audit logging of all approval decisions
- Integration with MCP servers for action execution
"""

import os
import json
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from base_watcher import BaseWatcher
from typing import Optional, Dict, Any

try:
    from plyer import notification
    NOTIFICATIONS_ENABLED = True
except ImportError:
    NOTIFICATIONS_ENABLED = False


class ApprovalWatcher(BaseWatcher):
    """
    Watches for approval workflow events and triggers actions.
    """

    def __init__(self, vault_path: str = None, check_interval: int = 5):
        super().__init__(vault_path, check_interval)

        # Approval workflow folders
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.rejected = self.vault_path / 'Rejected'
        self.done = self.vault_path / 'Done'

        # Ensure folders exist
        self.pending_approval.mkdir(exist_ok=True)
        self.approved.mkdir(exist_ok=True)
        self.rejected.mkdir(exist_ok=True)
        self.done.mkdir(exist_ok=True)

        # Track processed approvals
        self.processed_file = self.vault_path / '.processed_approvals'
        self.processed = self._load_processed()

        # Approval timeout (default 24 hours)
        self.timeout_hours = int(os.getenv('APPROVAL_TIMEOUT_HOURS', '24'))

        # Draft-only mode (Platinum: Cloud agent creates drafts but never executes)
        self.draft_only = os.getenv('AGENT_MODE', '').lower() == 'draft_only'

        # Restricted actions in draft-only mode (Cloud can only draft, not execute)
        self.draft_only_blocked = {
            'email_send', 'payment', 'linkedin_post',
            'facebook_post', 'instagram_post', 'twitter_post', 'social_post'
        }

        # Action handlers (can be extended with MCP integrations)
        self.action_handlers = {
            'email_send': self._handle_email_action,
            'payment': self._handle_payment_action,
            'social_post': self._handle_social_action,
            'linkedin_post': self._handle_linkedin_post_action,
            'facebook_post': self._handle_facebook_post_action,
            'instagram_post': self._handle_instagram_post_action,
            'twitter_post': self._handle_twitter_post_action,
            'general': self._handle_general_action
        }

        self.logger.info(f"Approval Watcher initialized")
        self.logger.info(f"Timeout: {self.timeout_hours} hours")
        self.logger.info(f"Mode: {'DRAFT-ONLY (Cloud)' if self.draft_only else 'FULL (Local)'}")
        self.logger.info(f"Notifications: {'enabled' if NOTIFICATIONS_ENABLED else 'disabled'}")

    def _load_processed(self) -> set:
        """Load processed approval IDs."""
        if self.processed_file.exists():
            return set(self.processed_file.read_text().splitlines())
        return set()

    def _save_processed(self):
        """Save processed approval IDs."""
        self.processed_file.write_text('\n'.join(self.processed))

    def _parse_approval_file(self, filepath: Path) -> Optional[Dict[str, Any]]:
        """Parse frontmatter from an approval file."""
        try:
            content = filepath.read_text(encoding='utf-8')

            # Parse YAML frontmatter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 3:
                    import yaml
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                    return {
                        'metadata': frontmatter,
                        'body': body,
                        'filepath': filepath
                    }

            # No frontmatter, return basic info
            return {
                'metadata': {'type': 'general'},
                'body': content,
                'filepath': filepath
            }

        except Exception as e:
            self.logger.error(f"Error parsing {filepath}: {e}")
            return None

    def _send_notification(self, title: str, message: str):
        """Send desktop notification if available."""
        if NOTIFICATIONS_ENABLED:
            try:
                notification.notify(
                    title=title,
                    message=message[:256],  # Limit message length
                    app_name='AI Employee',
                    timeout=10
                )
            except Exception as e:
                self.logger.warning(f"Notification failed: {e}")
        else:
            self.logger.info(f"NOTIFICATION: {title} - {message}")

    def check_for_updates(self) -> list:
        """Check for new items in approval workflow folders."""
        updates = []

        # Check for new pending approvals
        for filepath in self.pending_approval.glob('*.md'):
            if filepath.stem not in self.processed:
                approval = self._parse_approval_file(filepath)
                if approval:
                    updates.append({
                        'type': 'new_pending',
                        'data': approval
                    })
                    self._send_notification(
                        "New Approval Request",
                        f"Action required: {filepath.stem}"
                    )

        # Check for newly approved items
        for filepath in self.approved.glob('*.md'):
            if filepath.stem not in self.processed:
                approval = self._parse_approval_file(filepath)
                if approval:
                    updates.append({
                        'type': 'approved',
                        'data': approval
                    })

        # Check for timed out pending approvals
        for filepath in self.pending_approval.glob('*.md'):
            approval = self._parse_approval_file(filepath)
            if approval:
                metadata = approval.get('metadata', {})
                created_str = metadata.get('created')

                if created_str:
                    try:
                        created = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                        if datetime.now(created.tzinfo) > created + timedelta(hours=self.timeout_hours):
                            updates.append({
                                'type': 'timeout',
                                'data': approval
                            })
                    except:
                        pass

        return updates

    def create_action_file(self, item: dict) -> Path:
        """Process an approval workflow item."""
        item_type = item['type']
        data = item['data']
        filepath = data['filepath']
        metadata = data.get('metadata', {})

        if item_type == 'new_pending':
            # Log new pending approval
            self.log_action('approval_pending', {
                'file': filepath.name,
                'action_type': metadata.get('action', 'unknown')
            })
            self.processed.add(filepath.stem)
            self._save_processed()

        elif item_type == 'approved':
            # Execute the approved action
            self._execute_approved_action(data)
            self.processed.add(filepath.stem)
            self._save_processed()

        elif item_type == 'timeout':
            # Handle timeout
            self._handle_timeout(data)

        return filepath

    def _execute_approved_action(self, approval_data: dict):
        """Execute an approved action via appropriate handler."""
        filepath = approval_data['filepath']
        metadata = approval_data.get('metadata', {})
        action_type = metadata.get('action', 'general')

        # Also check 'type' field for auto-generated files (e.g. linkedin_post)
        if action_type == 'general':
            item_type = metadata.get('type', '')
            if item_type in self.action_handlers:
                action_type = item_type

        # Detect LinkedIn posts from filename pattern
        if action_type == 'general' and 'LINKEDIN' in filepath.name:
            action_type = 'linkedin_post'

        self.logger.info(f"Executing approved action: {filepath.name} (type: {action_type})")

        # Draft-only mode: Cloud agent blocks execution of send/post actions
        if self.draft_only and action_type in self.draft_only_blocked:
            self.logger.info(f"[DRAFT-ONLY] Blocked execution of {action_type} - requires Local agent")
            result = {
                'status': 'draft_only_blocked',
                'action': action_type,
                'message': 'Cloud agent in draft-only mode. Awaiting Local agent for execution.'
            }
            self.log_action('draft_only_blocked', {
                'file': filepath.name,
                'action_type': action_type
            })
            # Do NOT move to Done - leave in Approved for Local to pick up via vault sync
            return

        # Get handler for this action type
        handler = self.action_handlers.get(action_type, self._handle_general_action)

        try:
            if self.dry_run:
                self.logger.info(f"[DRY RUN] Would execute: {action_type}")
                result = {'status': 'dry_run', 'action': action_type}
            else:
                result = handler(approval_data)

            # Log success
            self.log_action('action_executed', {
                'file': filepath.name,
                'action_type': action_type,
                'result': result
            })

            # Move to Done
            self._move_to_done(filepath, 'approved', result)

        except Exception as e:
            self.logger.error(f"Action execution failed: {e}")
            self.log_action('action_failed', {
                'file': filepath.name,
                'action_type': action_type,
                'error': str(e)
            })

    def _handle_email_action(self, approval_data: dict) -> dict:
        """Handle email send action."""
        metadata = approval_data['metadata']

        # In production, this would call the Email MCP server
        self.logger.info(f"Sending email to: {metadata.get('to', 'unknown')}")

        # Placeholder for MCP integration
        # from mcp_client import EmailMCP
        # result = EmailMCP.send(
        #     to=metadata['to'],
        #     subject=metadata['subject'],
        #     body=metadata.get('body', '')
        # )

        return {
            'status': 'success',
            'action': 'email_send',
            'to': metadata.get('to'),
            'subject': metadata.get('subject')
        }

    def _handle_payment_action(self, approval_data: dict) -> dict:
        """Handle payment action (requires extra verification)."""
        metadata = approval_data['metadata']

        # Payments should NEVER be auto-executed
        # This should trigger a manual review even after approval
        self.logger.warning("PAYMENT ACTION - Manual verification required")

        return {
            'status': 'pending_manual_review',
            'action': 'payment',
            'amount': metadata.get('amount'),
            'recipient': metadata.get('recipient')
        }

    def _handle_social_action(self, approval_data: dict) -> dict:
        """Handle social media post action - routes to platform-specific handler."""
        metadata = approval_data['metadata']
        platform = metadata.get('platform', 'unknown').lower()
        body = approval_data.get('body', '')
        content = self._extract_post_content(body)

        self.logger.info(f"Social post action for platform: {platform}")

        dispatch = {
            'linkedin': self._handle_linkedin_post_action,
            'facebook': self._handle_facebook_post_action,
            'instagram': self._handle_instagram_post_action,
            'twitter': self._handle_twitter_post_action,
            'x': self._handle_twitter_post_action,
        }

        handler = dispatch.get(platform)
        if handler:
            return handler(approval_data)

        self.logger.warning(f"Unknown social platform: {platform}")
        return {
            'status': 'error',
            'action': 'social_post',
            'platform': platform,
            'message': f"Unsupported platform: {platform}"
        }

    def _handle_facebook_post_action(self, approval_data: dict) -> dict:
        """Handle Facebook post via Graph API."""
        body = approval_data.get('body', '')
        content = self._extract_post_content(body)

        if not content:
            return {'status': 'error', 'action': 'facebook_post', 'message': 'No content found'}

        self.logger.info(f"Facebook post ({len(content)} chars): {content[:80]}...")

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post to Facebook: {content[:80]}...")
            return {'status': 'dry_run', 'action': 'facebook_post', 'platform': 'facebook'}

        fb_token = os.getenv('FACEBOOK_PAGE_TOKEN')
        fb_page_id = os.getenv('FACEBOOK_PAGE_ID')
        if not fb_token or not fb_page_id:
            self.logger.warning("Facebook API not configured (FACEBOOK_PAGE_TOKEN / FACEBOOK_PAGE_ID)")
            return {
                'status': 'simulated',
                'action': 'facebook_post',
                'platform': 'facebook',
                'message': 'API not configured - post simulated',
                'content_preview': content[:100]
            }

        try:
            import urllib.request
            import urllib.parse
            url = f"https://graph.facebook.com/v19.0/{fb_page_id}/feed"
            data = urllib.parse.urlencode({
                'message': content,
                'access_token': fb_token
            }).encode()
            req = urllib.request.Request(url, data=data, method='POST')
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            self.logger.info(f"Facebook post published: {result.get('id')}")
            return {'status': 'success', 'action': 'facebook_post', 'platform': 'facebook',
                    'post_id': result.get('id')}
        except Exception as e:
            self.logger.error(f"Facebook post failed: {e}")
            return {'status': 'error', 'action': 'facebook_post', 'platform': 'facebook',
                    'message': str(e)}

    def _handle_instagram_post_action(self, approval_data: dict) -> dict:
        """Handle Instagram post via Graph API (requires image)."""
        body = approval_data.get('body', '')
        metadata = approval_data.get('metadata', {})
        content = self._extract_post_content(body)
        image_url = metadata.get('image_url', '')

        if not content:
            return {'status': 'error', 'action': 'instagram_post', 'message': 'No content found'}

        self.logger.info(f"Instagram post ({len(content)} chars): {content[:80]}...")

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post to Instagram: {content[:80]}...")
            return {'status': 'dry_run', 'action': 'instagram_post', 'platform': 'instagram'}

        ig_token = os.getenv('META_ACCESS_TOKEN')
        ig_account_id = os.getenv('INSTAGRAM_BUSINESS_ID')
        if not ig_token or not ig_account_id:
            self.logger.warning("Instagram API not configured (META_ACCESS_TOKEN / INSTAGRAM_BUSINESS_ID)")
            return {
                'status': 'simulated',
                'action': 'instagram_post',
                'platform': 'instagram',
                'message': 'API not configured - post simulated',
                'content_preview': content[:100]
            }

        if not image_url:
            self.logger.warning("Instagram requires image_url in metadata")
            return {
                'status': 'error',
                'action': 'instagram_post',
                'platform': 'instagram',
                'message': 'Instagram requires an image_url in post metadata'
            }

        try:
            import urllib.request
            import urllib.parse
            # Step 1: Create media container
            create_url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media"
            create_data = urllib.parse.urlencode({
                'image_url': image_url,
                'caption': content,
                'access_token': ig_token
            }).encode()
            req = urllib.request.Request(create_url, data=create_data, method='POST')
            with urllib.request.urlopen(req, timeout=30) as resp:
                container = json.loads(resp.read())
            container_id = container.get('id')
            if not container_id:
                return {'status': 'error', 'action': 'instagram_post', 'platform': 'instagram',
                        'message': f"Container creation failed: {container}"}

            # Step 1.5: Poll container status until FINISHED (max 30 attempts, 2s apart)
            import time as _time
            for _attempt in range(30):
                status_url = f"https://graph.facebook.com/v19.0/{container_id}?fields=status_code&access_token={ig_token}"
                status_req = urllib.request.Request(status_url)
                with urllib.request.urlopen(status_req, timeout=15) as status_resp:
                    status_data = json.loads(status_resp.read())
                status_code = status_data.get('status_code', '')
                if status_code == 'FINISHED':
                    break
                elif status_code == 'ERROR':
                    return {'status': 'error', 'action': 'instagram_post', 'platform': 'instagram',
                            'message': f"Container processing failed: {status_data}"}
                self.logger.debug(f"Instagram container status: {status_code}, waiting...")
                _time.sleep(2)
            else:
                return {'status': 'error', 'action': 'instagram_post', 'platform': 'instagram',
                        'message': 'Container processing timed out after 60 seconds'}

            # Step 2: Publish
            publish_url = f"https://graph.facebook.com/v19.0/{ig_account_id}/media_publish"
            publish_data = urllib.parse.urlencode({
                'creation_id': container_id,
                'access_token': ig_token
            }).encode()
            req = urllib.request.Request(publish_url, data=publish_data, method='POST')
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            self.logger.info(f"Instagram post published: {result.get('id')}")
            return {'status': 'success', 'action': 'instagram_post', 'platform': 'instagram',
                    'post_id': result.get('id')}
        except Exception as e:
            self.logger.error(f"Instagram post failed: {e}")
            return {'status': 'error', 'action': 'instagram_post', 'platform': 'instagram',
                    'message': str(e)}

    def _handle_twitter_post_action(self, approval_data: dict) -> dict:
        """Handle Twitter/X post via API v2."""
        body = approval_data.get('body', '')
        content = self._extract_post_content(body)

        if not content:
            return {'status': 'error', 'action': 'twitter_post', 'message': 'No content found'}

        # Twitter/X: 280 char limit
        if len(content) > 280:
            self.logger.warning(f"Twitter content truncated from {len(content)} to 280 chars")
            content = content[:277] + '...'

        self.logger.info(f"Twitter/X post ({len(content)} chars): {content[:80]}...")

        if self.dry_run:
            self.logger.info(f"[DRY RUN] Would post to Twitter/X: {content[:80]}...")
            return {'status': 'dry_run', 'action': 'twitter_post', 'platform': 'twitter'}

        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_secret = os.getenv('TWITTER_ACCESS_SECRET')

        if not all([bearer_token, api_key, api_secret, access_token, access_secret]):
            self.logger.warning("Twitter/X API not configured")
            return {
                'status': 'simulated',
                'action': 'twitter_post',
                'platform': 'twitter',
                'message': 'API not configured - post simulated',
                'content_preview': content[:100]
            }

        try:
            import urllib.request
            import urllib.parse
            import hashlib
            import hmac
            import base64
            import secrets
            import time as _time

            # OAuth 1.0a is REQUIRED for POST /2/tweets (bearer only works for reads)
            url = "https://api.twitter.com/2/tweets"
            body = json.dumps({"text": content})

            # Build OAuth 1.0a signature
            oauth_nonce = secrets.token_hex(16)
            oauth_timestamp = str(int(_time.time()))

            oauth_params = {
                'oauth_consumer_key': api_key,
                'oauth_nonce': oauth_nonce,
                'oauth_signature_method': 'HMAC-SHA1',
                'oauth_timestamp': oauth_timestamp,
                'oauth_token': access_token,
                'oauth_version': '1.0'
            }

            # For JSON body POSTs, only OAuth params go into signature base string
            param_string = '&'.join(
                f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
                for k, v in sorted(oauth_params.items())
            )
            base_string = f"POST&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"
            signing_key = f"{urllib.parse.quote(api_secret, safe='')}&{urllib.parse.quote(access_secret, safe='')}"
            signature = base64.b64encode(
                hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
            ).decode()

            oauth_params['oauth_signature'] = signature
            auth_header = 'OAuth ' + ', '.join(
                f'{k}="{urllib.parse.quote(v, safe="")}"'
                for k, v in sorted(oauth_params.items())
            )

            req = urllib.request.Request(url, data=body.encode(), method='POST')
            req.add_header('Content-Type', 'application/json')
            req.add_header('Authorization', auth_header)
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            tweet_id = result.get('data', {}).get('id')
            self.logger.info(f"Tweet published: {tweet_id}")
            return {'status': 'success', 'action': 'twitter_post', 'platform': 'twitter',
                    'tweet_id': tweet_id}
        except Exception as e:
            self.logger.error(f"Twitter/X post failed: {e}")
            return {'status': 'error', 'action': 'twitter_post', 'platform': 'twitter',
                    'message': str(e)}

    def _handle_linkedin_post_action(self, approval_data: dict) -> dict:
        """Handle LinkedIn post - extract content and publish via LinkedInWatcher."""
        body = approval_data.get('body', '')
        filepath = approval_data.get('filepath')

        # Extract post content from code block in the approval file
        content = self._extract_post_content(body)

        if not content:
            self.logger.error("No post content found in approval file")
            return {'status': 'error', 'message': 'No content found'}

        self.logger.info(f"LinkedIn post content ({len(content)} chars): {content[:80]}...")

        try:
            from linkedin_watcher import LinkedInWatcher
            watcher = LinkedInWatcher(vault_path=str(self.vault_path))
            result = watcher._execute_post(content)
            watcher.close()
            return {
                'status': result.get('status', 'error'),
                'action': 'linkedin_post',
                'platform': 'linkedin',
                'message': result.get('message', ''),
                'content_preview': content[:100]
            }
        except Exception as e:
            self.logger.error(f"LinkedIn posting failed: {e}")
            return {
                'status': 'error',
                'action': 'linkedin_post',
                'message': str(e)
            }

    def _extract_post_content(self, body: str) -> str:
        """Extract post content from approval file body (inside code blocks)."""
        import re

        # Try to find content inside ``` code blocks
        code_blocks = re.findall(r'```\n?(.*?)```', body, re.DOTALL)
        if code_blocks:
            # Return the first non-empty code block
            for block in code_blocks:
                content = block.strip()
                if content:
                    return content

        # Fallback: look for content between "## Post Content" / "## Generated Content" and next ##
        sections = re.split(r'^## ', body, flags=re.MULTILINE)
        for section in sections:
            if section.startswith('Post Content') or section.startswith('Generated Content'):
                # Remove the header line and code fences
                lines = section.split('\n')[1:]  # skip header
                content_lines = []
                in_fence = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_fence = not in_fence
                        continue
                    if line.startswith('## '):
                        break
                    if in_fence or (not in_fence and line.strip()):
                        content_lines.append(line)
                content = '\n'.join(content_lines).strip()
                if content:
                    return content

        return ''

    def _handle_general_action(self, approval_data: dict) -> dict:
        """Handle general/unknown action types."""
        self.logger.info("Processing general action")
        return {'status': 'acknowledged', 'action': 'general'}

    def _handle_timeout(self, approval_data: dict):
        """Handle timed out approval requests."""
        filepath = approval_data['filepath']

        self.logger.warning(f"Approval timeout: {filepath.name}")
        self._send_notification(
            "Approval Timeout",
            f"Action expired: {filepath.stem}"
        )

        # Move to rejected with timeout reason
        self._move_to_done(filepath, 'timeout', {'reason': 'timeout'})

        self.log_action('approval_timeout', {
            'file': filepath.name
        })

    def _move_to_done(self, filepath: Path, reason: str, result: dict):
        """Move processed file to Done folder with metadata."""
        try:
            # Read original content
            content = filepath.read_text(encoding='utf-8')

            # Add processing metadata
            timestamp = datetime.now().isoformat()
            processing_note = f"""

---
## Processing Result
- **Processed At:** {timestamp}
- **Resolution:** {reason}
- **Result:** {json.dumps(result, indent=2)}
"""
            # Write to Done folder
            done_path = self.done / f"{reason}_{filepath.name}"
            done_path.write_text(content + processing_note, encoding='utf-8')

            # Remove from original location
            filepath.unlink()

            self.logger.info(f"Moved {filepath.name} to Done ({reason})")

        except Exception as e:
            self.logger.error(f"Error moving file: {e}")

    def create_approval_request(
        self,
        action_type: str,
        title: str,
        details: dict,
        expires_hours: int = None
    ) -> Path:
        """
        Helper method to create an approval request file.

        Args:
            action_type: Type of action (email_send, payment, etc.)
            title: Human-readable title
            details: Action-specific details
            expires_hours: Override default timeout

        Returns:
            Path to created approval file
        """
        timestamp = datetime.now()
        expires = expires_hours or self.timeout_hours

        # Generate filename
        safe_title = title.replace(' ', '_')[:30]
        filename = f"APPROVAL_{timestamp.strftime('%Y%m%d_%H%M%S')}_{safe_title}.md"

        content = f"""---
action: {action_type}
title: {title}
created: {timestamp.isoformat()}
expires: {(timestamp + timedelta(hours=expires)).isoformat()}
status: pending
{self._format_details_yaml(details)}
---

# Approval Request: {title}

## Action Type
**{action_type}**

## Details
{self._format_details_markdown(details)}

## Expiration
This request will expire on {(timestamp + timedelta(hours=expires)).strftime('%Y-%m-%d %H:%M')}

---

## Instructions
- To **APPROVE**: Move this file to `/Approved/` folder
- To **REJECT**: Move this file to `/Rejected/` folder

---
*Created by AI Employee at {timestamp.strftime('%Y-%m-%d %H:%M:%S')}*
"""

        filepath = self.pending_approval / filename
        filepath.write_text(content, encoding='utf-8')

        self.logger.info(f"Created approval request: {filename}")
        self._send_notification("New Approval Request", title)

        return filepath

    def _format_details_yaml(self, details: dict) -> str:
        """Format details dict as YAML lines."""
        lines = []
        for key, value in details.items():
            if isinstance(value, str):
                lines.append(f"{key}: \"{value}\"")
            else:
                lines.append(f"{key}: {value}")
        return '\n'.join(lines)

    def _format_details_markdown(self, details: dict) -> str:
        """Format details dict as markdown."""
        lines = []
        for key, value in details.items():
            lines.append(f"- **{key}:** {value}")
        return '\n'.join(lines)


# Standalone execution
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Approval Watcher for AI Employee')
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--interval', '-i', type=int, default=5, help='Check interval in seconds')
    parser.add_argument('--once', action='store_true', help='Run once and exit')
    parser.add_argument('--create-test', action='store_true', help='Create a test approval request')

    args = parser.parse_args()

    vault_path = args.vault or os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')

    watcher = ApprovalWatcher(
        vault_path=vault_path,
        check_interval=args.interval
    )

    if args.create_test:
        # Create test approval request
        watcher.create_approval_request(
            action_type='email_send',
            title='Test Email Approval',
            details={
                'to': 'test@example.com',
                'subject': 'Test Email',
                'body': 'This is a test email body'
            }
        )
        print("Test approval request created in Pending_Approval folder")
    elif args.once:
        items = watcher.check_for_updates()
        for item in items:
            watcher.create_action_file(item)
    else:
        print(f"Starting Approval Watcher...")
        print(f"Vault: {vault_path}")
        print(f"Check interval: {args.interval}s")
        print("-" * 50)
        watcher.run()
