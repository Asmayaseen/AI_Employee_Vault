# linkedin-monitor

Monitor LinkedIn for messages, notifications, and auto-post business updates.

## What you do

You monitor LinkedIn for new messages and notifications, and automatically post business updates according to the schedule defined in Company_Handbook.md.

## When to use

- When user asks to "check LinkedIn" or "post to LinkedIn"
- When scheduled auto-posting time arrives (Mon 9AM, Wed 12PM, Fri 3PM)
- To monitor LinkedIn messages and connection requests
- As part of social media management workflow

## Prerequisites

- Playwright installed: `playwright install chromium`
- LinkedIn session authenticated
- Python LinkedIn watcher/poster scripts available

## Instructions

### Step 1: Check LinkedIn Session

Verify LinkedIn authentication:

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
test -d .linkedin_session && echo "✅ Session exists" || echo "❌ Need setup"
```

If not set up:
```bash
python setup_linkedin_session.py
# Login once in the browser window that opens
```

### Step 2: Monitor LinkedIn Messages

Check for new messages and notifications:

```bash
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers
python linkedin_watcher.py --check-messages
```

This will:
1. Open LinkedIn in headless browser
2. Check for unread messages
3. Check notifications
4. Extract message content
5. Create action files for important messages

### Step 3: Auto-Post Updates

According to Company_Handbook.md schedule:
- **Monday 9:00 AM:** Business update, achievement, or milestone
- **Wednesday 12:00 PM:** Industry insight, tip, or educational content
- **Friday 3:00 PM:** Weekly reflection, lesson learned, or motivation

```bash
python linkedin_auto_poster.py --generate-post
```

The system will:
1. Generate appropriate content based on day/time
2. Create draft in `/Pending_Approval/`
3. Wait for human approval
4. Post once approved

### Step 4: Content Guidelines Check

Before posting, verify against Company_Handbook.md rules:

✅ **Allowed:**
- Professional achievements and milestones
- Industry insights and helpful tips
- Client success stories (with permission)
- Business updates and announcements

❌ **Not Allowed:**
- Political opinions or controversial topics
- Personal complaints or negativity
- Unverified news or information
- Competitor criticism

### Step 5: Post Approval Workflow

```bash
# Draft created in /Pending_Approval/LINKEDIN_POST_[date].md
# Human reviews content
# Move to /Approved/ to publish
# Orchestrator detects and posts via linkedin_auto_poster.py
```

## Output format

### For Messages:
```
LinkedIn Check Complete:
- New messages: X
- New notifications: Y
- Connection requests: Z

New Messages:
1. From: [Name] - "[preview...]"
2. From: [Name] - "[preview...]"

Action files created in: /Needs_Action/
```

### For Auto-Posting:
```
LinkedIn Post Draft Created:
- Day: Monday
- Time: 9:00 AM
- Type: Business milestone
- Content: "[post preview...]"

📝 Draft saved to: /Pending_Approval/LINKEDIN_POST_20260208.md
⏳ Waiting for approval...

To approve: Move file to /Approved/
```

## Error handling

**Session expired:**
```bash
rm -rf .linkedin_session
python setup_linkedin_session.py
```

**Rate limit hit:**
- Wait 1 hour before next post
- LinkedIn limits: ~10 posts/day
- Respect platform guidelines

**Content too long:**
- LinkedIn max: 3000 characters
- Trim content and add "..." or link

**Post failed:**
- Save draft for manual posting
- Log error to `/Logs/linkedin.log`
- Alert user

## Examples

**Example 1: Monday morning auto-post**
```
Time: Monday 9:00 AM
→ Trigger: linkedin-monitor skill
→ Generate business milestone post
→ Draft created: "Excited to announce we completed 5 projects this month!"
→ Saved to /Pending_Approval/
→ User approves
→ Posted to LinkedIn
→ Logged to /Done/
```

**Example 2: New message received**
```
LinkedIn message: "Hi, interested in your services. Can we schedule a call?"
→ Detected: potential lead
→ Created: LINKEDIN_MSG_20260208_JohnDoe.md
→ Priority: HIGH (sales inquiry)
→ Claude processes: Creates response draft
→ Saved to /Pending_Approval/ for review
```

## Content generation

The auto-poster uses context from:
- `/Plans/` folder - Recent completed projects
- `/Done/` folder - Achievements this week
- `Business_Goals.md` - Company milestones
- Recent client work (anonymized)

### Post types by day:

**Monday (Business Update):**
- Project completions
- New client onboarding
- Revenue milestones
- Team achievements

**Wednesday (Industry Insight):**
- Tech tips and best practices
- Industry trends
- Educational content
- Problem-solving approaches

**Friday (Reflection):**
- Lessons learned this week
- Challenges overcome
- Friday motivation
- Weekend reading recommendations

## Integration points

- **Orchestrator**: Triggers at scheduled times
- **Claude Processor**: Generates post content
- **Company Handbook**: Follows posting rules
- **Dashboard**: Updates social media stats

## Success criteria

✅ LinkedIn session authenticated
✅ Messages monitored successfully
✅ Auto-posts generated on schedule
✅ Content follows guidelines
✅ Approval workflow working
✅ Posts successfully published
✅ Analytics tracked

## Rate limits

- Posts: Max 10/day
- Messages: Max 20/day
- Connection requests: Max 100/week
- Stay well below limits for safety

---

**Skill Type:** Watcher + Poster
**Tier:** Silver
**Automation:** Scheduled (Mon/Wed/Fri) + continuous monitoring
**Platform:** LinkedIn
