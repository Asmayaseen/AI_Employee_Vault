# ceo-briefing

Generate weekly CEO briefing reports that summarize business performance, completed tasks, bottlenecks, and proactive suggestions.

## What you do

You are the CEO Briefing Generator. You analyze the week's activity, review business goals, and create a comprehensive Monday Morning briefing that helps the business owner understand:
- What was accomplished
- What needs attention
- Revenue progress
- Upcoming deadlines
- Proactive suggestions

## When to use

- Every Sunday night (8 PM) via cron
- When user asks for a business summary
- Before important meetings to get current status
- When planning the upcoming week

## Prerequisites

- Business_Goals.md file in vault root (will be created if missing)
- /Done folder with completed tasks
- /Needs_Action and /Pending_Approval for pending items

## Instructions

### Generate Weekly Briefing

```bash
# Generate and save this week's briefing
python3 /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/ceo_briefing_generator.py

# Preview without saving
python3 /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/ceo_briefing_generator.py --preview

# Custom period (14 days)
python3 /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/ceo_briefing_generator.py --period 14
```

### Briefing Sections

The generated briefing includes:

1. **Executive Summary** - High-level week assessment
2. **Revenue** - Monthly target vs actual with trend
3. **Completed Tasks** - List of finished items
4. **Pending Items** - Tasks needing attention
5. **Awaiting Approval** - Items in Human-in-the-Loop queue
6. **Bottlenecks** - Tasks that took longer than expected
7. **Proactive Suggestions** - AI-generated recommendations
8. **Upcoming Deadlines** - Project due dates

### Output Location

Briefings are saved to:
```
/AI_Employee_Vault/Briefings/YYYY-MM-DD_Monday_Briefing.md
```

### Update Business Goals

Edit `/AI_Employee_Vault/Business_Goals.md` to customize:
- Revenue targets
- Key metrics
- Active projects with deadlines
- Subscription audit rules

### Cron Schedule

The briefing runs automatically every Sunday at 8 PM:
```
0 20 * * 0 cd $VAULT_PATH/Watchers && python3 ceo_briefing_generator.py
```

## Example Output

```markdown
# Monday Morning CEO Briefing
**Week of February 09, 2026**

## Executive Summary
Good progress this week. Some items need attention.

| Metric | This Week |
|--------|-----------|
| Tasks Completed | 12 |
| Pending Items | 21 |
| Awaiting Approval | 4 |
| Bottlenecks | 1 |

## Revenue
- Monthly Target: $10,000.00
- Current MTD: $4,500.00 (45% of target)
- Trend: Needs attention

## Proactive Suggestions
1. High pending count (21 items). Consider prioritizing.
2. Upcoming deadline: AI Employee Development due in 19 days
```

## Related Skills

- ralph-loop.skill.md - For autonomous processing
- orchestrator.skill.md - System management
- approval-monitor.skill.md - Approval workflow
