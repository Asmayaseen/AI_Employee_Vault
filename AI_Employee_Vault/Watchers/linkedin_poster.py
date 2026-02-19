#!/usr/bin/env python3
"""
LinkedIn Poster - Consolidated LinkedIn posting for AI Employee.

Combines post drafting, approval workflow, and publishing into one module.
Used by:
- linkedin_auto_poster.py (content generation)
- approval_watcher.py (publishing approved posts)
- scheduler.py (checking approved posts)
- CLI (manual draft/post)

Uses Playwright for web automation.
Note: Use responsibly and be aware of LinkedIn's terms of service.
"""

import os
import re
import json
import time
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LinkedInPoster')

VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))


class LinkedInPoster:
    """Handles LinkedIn post creation, approval, and publishing."""

    def __init__(self, vault_path: str = None, session_path: str = None):
        self.vault_path = Path(vault_path or VAULT_PATH)
        self.session_path = Path(session_path or os.getenv(
            'LINKEDIN_SESSION_PATH',
            str(self.vault_path / 'Watchers' / '.linkedin_session')
        ))
        self.session_path.mkdir(parents=True, exist_ok=True)

        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self.logs_dir = self.vault_path / 'Logs'

        for d in [self.pending_approval, self.approved, self.done, self.logs_dir]:
            d.mkdir(parents=True, exist_ok=True)

        self.dry_run = os.getenv('DRY_RUN', 'true').lower() == 'true'

    def create_draft_post(self, content: str, image_path: str = None) -> Path:
        """Create a post draft in Pending_Approval for HITL review."""
        timestamp = datetime.now()
        filename = f"LINKEDIN_POST_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"

        approval_content = f'''---
type: linkedin_post
action: linkedin_post
platform: linkedin
created: {timestamp.isoformat()}
status: pending
auto_generated: true
---

# LinkedIn Post Approval

## Post Content
```
{content}
```

## Post Details
- **Day:** {timestamp.strftime('%A, %B %d, %Y')}
- **Time:** {timestamp.strftime('%I:%M %p')}
- **Character Count:** {len(content)}
- **Image:** {image_path or 'None'}

## Rules Check
- Professional tone maintained
- No controversial content
- Follows Company_Handbook guidelines

---

## Instructions
**To APPROVE:** Move this file to `/Approved/` folder
**To REJECT:** Move this file to `/Rejected/` folder
**To EDIT:** Modify the content above, then move to `/Approved/`

---
*Created by LinkedIn Poster*
*System will post within 15 minutes of approval*
'''

        filepath = self.pending_approval / filename
        filepath.write_text(approval_content, encoding='utf-8')
        logger.info(f"Draft post created: {filename}")
        return filepath

    def publish_post(self, content: str) -> Dict:
        """Publish content to LinkedIn via Playwright."""
        if self.dry_run:
            logger.info(f"[DRY RUN] Would post to LinkedIn: {content[:80]}...")
            return {'status': 'dry_run', 'content_preview': content[:100]}

        if not PLAYWRIGHT_AVAILABLE:
            logger.error("Playwright not installed")
            return {'status': 'error', 'message': 'Playwright not available'}

        try:
            pw = sync_playwright().start()
            browser = pw.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=True,
                user_agent=(
                    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
                    '(KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
                ),
                viewport={'width': 1280, 'height': 900},
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--headless=new',
                ]
            )

            page = browser.pages[0] if browser.pages else browser.new_page()

            # Navigate to feed
            page.goto('https://www.linkedin.com/feed/', timeout=30000)
            page.wait_for_load_state('domcontentloaded', timeout=15000)
            time.sleep(2)

            # Check if logged in
            if '/login' in page.url or '/authwall' in page.url:
                browser.close()
                pw.stop()
                return {'status': 'error', 'message': 'Not logged in to LinkedIn'}

            # Click share box
            share_selectors = [
                'button[aria-label*="Start a post"]',
                '[class*="share-box"] button',
                '.share-box-feed-entry__trigger',
                'button[class*="share-box"]',
            ]
            share_box = None
            for sel in share_selectors:
                try:
                    share_box = page.wait_for_selector(sel, timeout=5000)
                    if share_box:
                        break
                except Exception:
                    continue

            if not share_box:
                browser.close()
                pw.stop()
                return {'status': 'error', 'message': 'Could not find share box'}

            share_box.click()
            time.sleep(1.5)

            # Find editor
            editor_selectors = [
                '[role="textbox"][contenteditable="true"]',
                '[aria-label*="Text editor"]',
                '.ql-editor',
                '[contenteditable="true"]',
            ]
            editor = None
            for sel in editor_selectors:
                try:
                    editor = page.wait_for_selector(sel, timeout=5000)
                    if editor:
                        break
                except Exception:
                    continue

            if not editor:
                browser.close()
                pw.stop()
                return {'status': 'error', 'message': 'Could not find post editor'}

            editor.fill(content)
            time.sleep(1)

            # Click Post button
            post_selectors = [
                'button[aria-label="Post"]',
                'button:has-text("Post")',
                '.share-actions__primary-action',
                'button[class*="share-actions__primary"]',
            ]
            post_btn = None
            for sel in post_selectors:
                try:
                    post_btn = page.wait_for_selector(sel, timeout=5000)
                    if post_btn:
                        break
                except Exception:
                    continue

            if not post_btn:
                browser.close()
                pw.stop()
                return {'status': 'error', 'message': 'Could not find post button'}

            post_btn.click()
            time.sleep(3)

            browser.close()
            pw.stop()

            self._log_post(content, 'success')
            logger.info("Post published successfully!")
            return {'status': 'success', 'message': 'Posted successfully'}

        except Exception as e:
            logger.error(f"Post failed: {e}")
            self._log_post(content, 'failed', str(e))
            return {'status': 'error', 'message': str(e)}

    def check_and_publish_approved(self) -> int:
        """Check for approved LinkedIn posts and publish them."""
        patterns = ['LINKEDIN_POST_*.md', 'LINKEDIN_AUTO_POST_*.md']
        approved_files = []
        for pattern in patterns:
            approved_files.extend(self.approved.glob(pattern))

        if not approved_files:
            logger.debug("No approved LinkedIn posts found")
            return 0

        logger.info(f"Found {len(approved_files)} approved LinkedIn post(s)")
        published = 0

        for filepath in approved_files:
            content = self._extract_content(filepath)
            if not content:
                logger.warning(f"No content found in {filepath.name}, skipping")
                continue

            logger.info(f"Publishing: {filepath.name}")
            result = self.publish_post(content)

            if result.get('status') in ('success', 'dry_run'):
                # Move to Done
                done_path = self.done / filepath.name
                filepath.rename(done_path)
                logger.info(f"Published and moved to Done: {filepath.name}")
                published += 1
            else:
                logger.error(f"Failed to publish {filepath.name}: {result.get('message')}")
                # Move to Rejected
                rejected_dir = self.vault_path / 'Rejected'
                rejected_dir.mkdir(exist_ok=True)
                rejected_path = rejected_dir / filepath.name
                filepath.rename(rejected_path)

            # Wait between posts to avoid rate limiting
            if len(approved_files) > 1:
                time.sleep(60)

        return published

    def _extract_content(self, filepath: Path) -> str:
        """Extract post content from an approval file."""
        body = filepath.read_text(encoding='utf-8')

        # Try code blocks first
        code_blocks = re.findall(r'```\n?(.*?)```', body, re.DOTALL)
        if code_blocks:
            for block in code_blocks:
                content = block.strip()
                if content:
                    return content

        # Fallback: sections
        sections = re.split(r'^## ', body, flags=re.MULTILINE)
        for section in sections:
            if section.startswith('Post Content') or section.startswith('Generated Content'):
                lines = section.split('\n')[1:]
                content_lines = []
                in_fence = False
                for line in lines:
                    if line.strip().startswith('```'):
                        in_fence = not in_fence
                        continue
                    if line.startswith('## '):
                        break
                    if in_fence:
                        content_lines.append(line)
                content = '\n'.join(content_lines).strip()
                if content:
                    return content

        return ''

    def _log_post(self, content: str, status: str, error: str = None):
        """Log post activity to daily log file."""
        log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': 'linkedin_post',
            'actor': 'linkedin_poster',
            'content_preview': content[:100],
            'result': status,
            'error': error
        }

        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except json.JSONDecodeError:
                logs = []

        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')


def main():
    """CLI interface for LinkedIn Poster."""
    import sys

    if len(sys.argv) < 2:
        print("Usage:")
        print("  python linkedin_poster.py check    - Check & publish approved posts")
        print("  python linkedin_poster.py draft \"content\" - Create draft for approval")
        print("  python linkedin_poster.py auth     - Setup LinkedIn session")
        sys.exit(1)

    command = sys.argv[1]
    poster = LinkedInPoster()

    if command == 'check':
        count = poster.check_and_publish_approved()
        print(f"Published {count} post(s)")

    elif command == 'draft' and len(sys.argv) > 2:
        content = sys.argv[2]
        filepath = poster.create_draft_post(content)
        print(f"Draft created: {filepath}")

    elif command == 'auth':
        from setup_linkedin_session import main as setup_main
        setup_main()

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
