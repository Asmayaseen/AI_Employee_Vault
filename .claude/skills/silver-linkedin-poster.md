# silver-linkedin-poster

Automatically post business updates to LinkedIn to generate sales leads - Silver Tier requirement.

## What you do

Set up automated LinkedIn posting using Playwright for web automation. Create post templates, implement approval workflow, and schedule regular business updates.

## Prerequisites

- Bronze tier complete
- LinkedIn account
- Playwright installed
- Python 3.13+

## Strategy

LinkedIn's official API has strict access requirements. For hackathon purposes, we'll use Playwright for web automation.

**Important:** Use responsibly, respect LinkedIn's Terms of Service, and keep posting frequency reasonable (1-2 posts per day max).

## Instructions

### Step 1: Install Playwright

```bash
# Install Playwright
pip install playwright

# Install chromium browser
playwright install chromium

# Verify installation
playwright --version
```

### Step 2: Create LinkedIn Poster Script

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

# Create linkedin_poster.py
```

Create file with this content:

```python
#!/usr/bin/env python3
"""
LinkedIn Auto-Poster for AI Employee
Uses Playwright for web automation
Requires HITL approval per constitution
"""

from playwright.sync_api import sync_playwright
from pathlib import Path
from datetime import datetime
import logging
import json
import time


class LinkedInPoster:
    def __init__(self, vault_path: str, session_path: str):
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path)
        self.session_path.mkdir(parents=True, exist_ok=True)
        self.templates_dir = self.vault_path / 'Templates' / 'LinkedIn'
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.approved = self.vault_path / 'Approved'
        self.done = self.vault_path / 'Done'
        self._setup_logging()

    def _setup_logging(self):
        log_dir = self.vault_path / 'Logs'
        log_file = log_dir / 'LinkedInPoster.log'

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('LinkedInPoster')

    def authenticate_first_time(self):
        """First-time setup: Manual LinkedIn login"""
        self.logger.info('Starting first-time LinkedIn authentication')

        with sync_playwright() as p:
            browser = p.chromium.launch_persistent_context(
                str(self.session_path),
                headless=False,
                viewport={'width': 1280, 'height': 720}
            )

            page = browser.pages[0]
            page.goto('https://www.linkedin.com/login')

            self.logger.info('Please log in manually in the browser window')
            input('Press Enter after you have logged in successfully...')

            # Verify login successful
            page.goto('https://www.linkedin.com/feed/')
            time.sleep(2)

            if 'feed' not in page.url:
                self.logger.error('Login may have failed - not on feed page')
            else:
                self.logger.info('Login successful! Session saved.')

            browser.close()

    def create_draft_post(self, content: str, image_path: str = None):
        """Create draft post and request approval"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'LINKEDIN_POST_{timestamp}.md'

        approval_content = f'''---
type: approval_request
action: linkedin_post
created: {datetime.now().isoformat()}
status: pending
priority: medium
---

# Approval Request: LinkedIn Post

## Post Content

```
{content}
```

## Image
{f'Attached: {image_path}' if image_path else 'No image'}

## Target Audience
- Business professionals
- Potential clients
- Industry connections

## Expected Impact
- Brand visibility
- Lead generation
- Thought leadership

## To Approve
1. Review post content above
2. Modify if needed (edit content section)
3. Move this file to `/Approved/` folder

## To Reject
Move this file to `/Rejected/` folder

## Post Scheduling
After approval, post will be published to LinkedIn within 1 hour.

## Compliance
✅ Per Company Handbook: Social media posts require approval
✅ Per Constitution Principle II: HITL for external communications
✅ Content reviewed for professionalism

---

*Created by LinkedIn Auto-Poster*
*AI Employee Silver Tier Feature*
'''

        approval_file = self.pending_approval / filename
        approval_file.write_text(approval_content, encoding='utf-8')
        self.logger.info(f'Draft post created: {filename}')

        return approval_file

    def post_approved_content(self, approval_file: Path):
        """Post approved content to LinkedIn"""
        self.logger.info(f'Posting approved content from: {approval_file.name}')

        # Extract content from approval file
        content_lines = []
        in_content = False

        for line in approval_file.read_text(encoding='utf-8').split('\\n'):
            if line.strip() == '```' and not in_content:
                in_content = True
                continue
            elif line.strip() == '```' and in_content:
                break
            elif in_content:
                content_lines.append(line)

        content = '\\n'.join(content_lines).strip()

        if not content:
            self.logger.error('No content found in approval file')
            return False

        # Post to LinkedIn
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch_persistent_context(
                    str(self.session_path),
                    headless=True
                )

                page = browser.pages[0]
                page.goto('https://www.linkedin.com/feed/')
                time.sleep(2)

                # Click "Start a post"
                page.click('button[class*="share-box-feed-entry__trigger"]')
                time.sleep(1)

                # Type content
                editor = page.locator('div[role="textbox"][contenteditable="true"]').first
                editor.click()
                editor.fill(content)
                time.sleep(1)

                # Click Post button
                page.click('button[class*="share-actions__primary-action"]')
                time.sleep(3)

                browser.close()

                self.logger.info('Post published successfully!')

                # Log to vault
                self._log_post(content, 'success')

                # Move approval file to Done
                done_file = self.done / approval_file.name
                approval_file.rename(done_file)

                return True

        except Exception as e:
            self.logger.error(f'Failed to post: {e}')
            self._log_post(content, 'failed', str(e))
            return False

    def _log_post(self, content: str, status: str, error: str = None):
        """Log post activity"""
        log_file = self.vault_path / 'Logs' / f'{datetime.now().strftime("%Y-%m-%d")}.json'

        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': 'linkedin_post',
            'actor': 'linkedin_auto_poster',
            'content_preview': content[:100] + '...',
            'result': status,
            'error': error
        }

        # Append to daily log
        if log_file.exists():
            logs = json.loads(log_file.read_text())
            logs.append(log_entry)
        else:
            logs = [log_entry]

        log_file.write_text(json.dumps(logs, indent=2), encoding='utf-8')

    def check_approved_posts(self):
        """Check for approved posts and publish them"""
        linkedin_files = list(self.approved.glob('LINKEDIN_POST_*.md'))

        if not linkedin_files:
            self.logger.debug('No approved LinkedIn posts found')
            return

        self.logger.info(f'Found {len(linkedin_files)} approved post(s)')

        for file in linkedin_files:
            self.logger.info(f'Processing: {file.name}')
            success = self.post_approved_content(file)

            if success:
                self.logger.info(f'Successfully posted: {file.name}')
            else:
                self.logger.error(f'Failed to post: {file.name}')
                # Move to Rejected with error note
                rejected_file = self.vault_path / 'Rejected' / file.name
                file.rename(rejected_file)

            # Wait between posts to avoid rate limiting
            time.sleep(60)

    def generate_business_post(self, topic: str):
        """Generate business-related post content"""
        # Read Business_Goals.md for context
        goals_file = self.vault_path / 'Business_Goals.md'

        if not goals_file.exists():
            self.logger.warning('Business_Goals.md not found')
            return None

        # Template-based post generation
        templates = {
            'milestone': '''🎯 Milestone Alert!

We're excited to share that {achievement}.

This progress reflects our commitment to {value_proposition}.

Key highlights:
• {highlight_1}
• {highlight_2}
• {highlight_3}

Looking forward to continuing this journey!

#BusinessGrowth #Milestones #Success''',

            'service': '''🚀 Service Spotlight

At {company_name}, we specialize in {service_description}.

What makes us different:
✅ {differentiator_1}
✅ {differentiator_2}
✅ {differentiator_3}

Ready to elevate your {industry}? Let's connect!

#Business #Services #Growth''',

            'insight': '''💡 Industry Insight

{insight_statement}

Here's what we're seeing:
• {trend_1}
• {trend_2}
• {trend_3}

How is this impacting your business? Let's discuss!

#Industry #Trends #BusinessStrategy''',

            'tips': '''🎓 Quick Tips

{topic_introduction}

Here are our top tips:
1️⃣ {tip_1}
2️⃣ {tip_2}
3️⃣ {tip_3}

Which one will you implement first?

#BusinessTips #Growth #Strategy'''
        }

        template = templates.get(topic, templates['insight'])

        # Fill template variables from Business_Goals.md context
        goals_content = goals_file.read_text(encoding='utf-8')
        filled = self._fill_template_from_context(template, goals_content, topic)

        return self.create_draft_post(filled)

    def _fill_template_from_context(self, template: str, context: str, topic: str):
        """Fill template placeholders using business context."""
        import re
        # Extract meaningful lines from context
        lines = [l.strip() for l in context.split('\n')
                 if l.strip() and not l.startswith('#') and len(l.strip()) > 10]
        highlights = lines[:5] if lines else ['Delivering value to clients']

        # Build substitution map with sensible defaults
        subs = {
            'achievement': highlights[0] if highlights else 'making great progress',
            'value_proposition': 'delivering quality and innovation',
            'highlight_1': highlights[0] if len(highlights) > 0 else 'Quality delivery',
            'highlight_2': highlights[1] if len(highlights) > 1 else 'Client satisfaction',
            'highlight_3': highlights[2] if len(highlights) > 2 else 'Continuous improvement',
            'company_name': 'our team',
            'service_description': highlights[0] if highlights else 'professional services',
            'differentiator_1': 'Client-focused approach',
            'differentiator_2': 'Technical excellence',
            'differentiator_3': 'Reliable delivery',
            'industry': 'business',
            'insight_statement': highlights[0] if highlights else 'Adapt and grow',
            'trend_1': highlights[0] if len(highlights) > 0 else 'Automation is key',
            'trend_2': highlights[1] if len(highlights) > 1 else 'Quality over quantity',
            'trend_3': highlights[2] if len(highlights) > 2 else 'Continuous learning',
            'topic_introduction': f'Quick tips on {topic}',
            'tip_1': 'Start with clear goals',
            'tip_2': 'Measure what matters',
            'tip_3': 'Iterate and improve',
        }

        # Fill placeholders
        result = template
        for key, value in subs.items():
            result = result.replace('{' + key + '}', value)

        return result


def main():
    import sys

    if len(sys.argv) < 2:
        print('Usage:')
        print('  Authenticate: python linkedin_poster.py auth')
        print('  Check approved: python linkedin_poster.py check')
        print('  Draft post: python linkedin_poster.py draft "Your post content"')
        sys.exit(1)

    vault_path = '/mnt/d/Ai-Employee/AI_Employee_Vault'
    session_path = '/mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/.linkedin_session'

    poster = LinkedInPoster(vault_path, session_path)

    command = sys.argv[1]

    if command == 'auth':
        poster.authenticate_first_time()
    elif command == 'check':
        poster.check_approved_posts()
    elif command == 'draft' and len(sys.argv) > 2:
        content = sys.argv[2]
        poster.create_draft_post(content)
    elif command == 'generate' and len(sys.argv) > 2:
        topic = sys.argv[2]
        poster.generate_business_post(topic)
    else:
        print('Invalid command')


if __name__ == '__main__':
    main()
```

Make executable:
```bash
chmod +x linkedin_poster.py
```

### Step 3: First-Time Authentication

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

# Authenticate (browser will open)
python linkedin_poster.py auth

# In the browser:
# 1. Log into LinkedIn
# 2. Navigate to feed to confirm login
# 3. Return to terminal and press Enter

# Session is now saved in linkedin_session/ directory
```

### Step 4: Create Post Templates

```bash
mkdir -p /mnt/d/Ai-Employee/AI_Employee_Vault/Templates/LinkedIn

# Create example template
cat > /mnt/d/Ai-Employee/AI_Employee_Vault/Templates/LinkedIn/business_update.md << 'EOF'
---
template: business_update
frequency: weekly
---

🚀 Weekly Business Update

This week we:
• {achievement_1}
• {achievement_2}
• {achievement_3}

What we're working on next:
{next_goals}

#Business #Growth #Success
EOF
```

### Step 5: Test Draft Creation

```bash
# Create a test draft post
python linkedin_poster.py draft "🎯 Test post from AI Employee system! Excited to share our progress on automation. #AI #Automation #Business"

# Verify draft created
ls -la /mnt/d/Ai-Employee/AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md

# Open in Obsidian to review
```

### Step 6: Test Approval Workflow

```bash
# In Obsidian or via terminal:
# 1. Review the post in /Pending_Approval/
# 2. If approved, move to /Approved/

mv /mnt/d/Ai-Employee/AI_Employee_Vault/Pending_Approval/LINKEDIN_POST_*.md \
   /mnt/d/Ai-Employee/AI_Employee_Vault/Approved/

# Check approved posts and publish
python linkedin_poster.py check

# Verify post appears on your LinkedIn feed
```

### Step 7: Schedule Automated Posting

#### Option A: Cron (Linux/Mac)

```bash
# Edit crontab
crontab -e

# Add daily post check at 9 AM and 3 PM
0 9 * * * cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers && python linkedin_poster.py check >> /mnt/d/Ai-Employee/AI_Employee_Vault/Logs/linkedin_cron.log 2>&1
0 15 * * * cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers && python linkedin_poster.py check >> /mnt/d/Ai-Employee/AI_Employee_Vault/Logs/linkedin_cron.log 2>&1
```

#### Option B: PM2 (Cross-platform)

Create scheduler script:

```python
# linkedin_scheduler.py
import time
from linkedin_poster import LinkedInPoster
from datetime import datetime

vault_path = '/mnt/d/Ai-Employee/AI_Employee_Vault'
session_path = '/mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/linkedin_session'

poster = LinkedInPoster(vault_path, session_path)

while True:
    current_hour = datetime.now().hour

    # Check for approved posts at 9 AM and 3 PM
    if current_hour in [9, 15]:
        poster.logger.info('Scheduled check for approved posts')
        poster.check_approved_posts()
        time.sleep(3600)  # Sleep 1 hour to avoid multiple checks

    time.sleep(300)  # Check every 5 minutes
```

Run with PM2:
```bash
pm2 start linkedin_scheduler.py \
  --name "ai-employee-linkedin" \
  --interpreter python3

pm2 save
```

### Step 8: Integrate with Claude for Content Generation

Update Company_Handbook.md:

```markdown
## LinkedIn Posting Strategy

### Frequency
- Post 1-2 times per day
- Best times: 9 AM, 3 PM (business hours)

### Content Types
1. **Business Updates** (2x/week)
   - Milestones achieved
   - New services/products
   - Team highlights

2. **Industry Insights** (2x/week)
   - Market trends
   - Professional tips
   - Thought leadership

3. **Engagement Posts** (1x/week)
   - Questions to audience
   - Polls
   - Discussion starters

### Tone
- Professional yet approachable
- Value-focused
- Avoid excessive self-promotion
- Use relevant hashtags (3-5 max)

### Approval Required
✅ ALL LinkedIn posts require human approval before publishing
```

Create skill for Claude to generate posts:

```bash
# Tell Claude to generate LinkedIn posts
claude "Based on our Business_Goals.md and recent activity in Dashboard.md, generate a professional LinkedIn post highlighting our progress. Use the linkedin_poster.py script to create a draft for approval."
```

## Advanced Features

### Weekly Business Post Automation

Create script:

```python
# weekly_linkedin_post.py
from linkedin_poster import LinkedInPoster
from pathlib import Path

vault_path = Path('/mnt/d/Ai-Employee/AI_Employee_Vault')
poster = LinkedInPoster(str(vault_path), str(vault_path / 'Watchers' / 'linkedin_session'))

# Read Dashboard for weekly summary
dashboard = (vault_path / 'Dashboard.md').read_text()

# Extract metrics
# TODO: Parse dashboard for actual metrics

# Generate post
content = f'''🎯 Weekly Business Update

This week's highlights:
• {metric_1}
• {metric_2}
• {metric_3}

Excited about the progress we're making!

#BusinessGrowth #Progress #Success
'''

poster.create_draft_post(content)
```

Schedule weekly:
```bash
# Cron: Every Monday at 9 AM
0 9 * * 1 cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers && python weekly_linkedin_post.py
```

## Success Criteria

- [ ] Playwright installed and chromium browser ready
- [ ] LinkedIn authentication successful (session saved)
- [ ] linkedin_poster.py script functional
- [ ] Draft post creation works
- [ ] Approval workflow tested (Pending → Approved → Posted)
- [ ] Test post appears on LinkedIn feed
- [ ] Scheduled posting configured (cron or PM2)
- [ ] Templates directory created
- [ ] Integration with Claude for content generation
- [ ] Logging to /Logs/ working

## Security & Compliance

### LinkedIn Terms of Service
- ⚠️ LinkedIn may restrict automated posting
- ⚠️ Keep frequency reasonable (1-2 posts/day max)
- ⚠️ Use session approach (not API scraping)
- ✅ Human approval required (HITL compliance)
- ✅ Session data in .gitignore

### Best Practices
1. **Frequency:** Don't overpost (max 2/day)
2. **Quality:** Always review content before approval
3. **Engagement:** Monitor post performance manually
4. **Session:** Re-authenticate if login fails
5. **Backup:** Keep session in secure location

## Troubleshooting

### Issue: "Session expired" or login required
**Solution:**
```bash
# Re-authenticate
python linkedin_poster.py auth
```

### Issue: "Element not found" errors
**Solution:**
- LinkedIn changed their UI - update selectors in code
- Run in non-headless mode to debug:
  - Edit linkedin_poster.py: `headless=False`
  - Manually verify steps

### Issue: "Post didn't appear"
**Solution:**
1. Check LinkedIn for post (may take 1-2 minutes)
2. Verify approval file was moved to Done/
3. Check logs: `Logs/LinkedInPoster.log`
4. Try posting manually to verify account isn't restricted

### Issue: Playwright browser won't launch
**Solution:**
```bash
# Reinstall browsers
playwright install --force chromium

# Check permissions
ls -la $(playwright cache-dir)
```

## Monitoring

### Daily Checks
```bash
# Check scheduler status
pm2 status ai-employee-linkedin

# View logs
pm2 logs ai-employee-linkedin

# Check approved posts waiting
ls -la /mnt/d/Ai-Employee/AI_Employee_Vault/Approved/LINKEDIN_POST_*.md
```

### Weekly Review
1. Review posts that were published
2. Check LinkedIn analytics manually
3. Adjust content strategy based on engagement
4. Update templates in vault

## Next Steps

After LinkedIn poster is working:
1. `/silver-mcp-email` - Email MCP server
2. Integrate content generation with Claude
3. Create more post templates
4. Set up WhatsApp watcher
5. Complete Silver tier integration testing

## References

- Playwright: https://playwright.dev/python/
- LinkedIn Best Practices: https://business.linkedin.com/marketing-solutions/blog/linkedin-b2b-marketing/2021/the-best-times-to-post-on-linkedin
- Web Automation Ethics: https://playwright.dev/docs/best-practices

---

*Skill: silver-linkedin-poster*
*Tier: Silver*
*Estimated Time: 1-2 hours*
*Dependencies: Bronze tier, Playwright*
