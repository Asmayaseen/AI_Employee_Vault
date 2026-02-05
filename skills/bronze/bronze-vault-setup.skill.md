# Agent Skill: Bronze Vault Setup

**Skill ID:** `bronze-vault-setup`
**Tier:** Bronze (Foundation)
**Estimated Time:** 1-2 hours
**Prerequisites:** Obsidian installed, Claude Code installed

## Purpose

Initialize the Obsidian vault structure with all required folders and foundational markdown files for the Personal AI Employee system.

## Success Criteria

- [ ] Obsidian vault created at specified path
- [ ] All required folders created with correct structure
- [ ] `Dashboard.md` created with real-time status template
- [ ] `Company_Handbook.md` created with rules of engagement
- [ ] `Business_Goals.md` created with quarterly objectives template
- [ ] All files contain valid markdown with proper frontmatter
- [ ] Vault can be opened successfully in Obsidian
- [ ] Claude Code can read from and write to the vault

## Vault Structure

```
AI_Employee_Vault/
├── Dashboard.md
├── Company_Handbook.md
├── Business_Goals.md
├── Needs_Action/
├── Plans/
├── Pending_Approval/
├── Approved/
├── Rejected/
├── Done/
├── Logs/
├── Briefings/
└── Accounting/
```

## Dashboard.md Template

```markdown
---
type: dashboard
last_updated: [AUTO_TIMESTAMP]
---

# AI Employee Dashboard

## Status Overview
- **System Status:** 🟢 Operational
- **Last Activity:** [TIMESTAMP]
- **Active Tasks:** 0

## Financial Summary
- **Current Balance:** $[AMOUNT]
- **Pending Transactions:** 0
- **This Month Revenue:** $0
- **This Month Expenses:** $0

## Communications
- **Unread Emails:** 0
- **Pending WhatsApp:** 0
- **Awaiting Response:** 0

## Active Projects
- No active projects

## Recent Activity
[Auto-populated by AI Employee]

## Alerts & Notifications
- No active alerts

---
*Last updated by AI Employee: [TIMESTAMP]*
```

## Company_Handbook.md Template

```markdown
---
type: handbook
version: 1.0.0
last_updated: [DATE]
---

# Company Handbook: Rules of Engagement

## Communication Guidelines

### Email Protocol
- **Response Time:** Reply to important emails within 24 hours
- **Tone:** Always professional and polite
- **Signature:** Use standard signature with contact details
- **Auto-Approve:** Known contacts for routine matters
- **Require Approval:** New contacts, bulk sends, sensitive topics

### WhatsApp Protocol
- **Response Time:** Urgent messages (<1 hour), routine messages (<4 hours)
- **Tone:** Friendly but professional
- **Keywords:** "urgent", "asap", "invoice", "payment", "help" trigger immediate action
- **Auto-Approve:** None (all require review)
- **Require Approval:** All outgoing messages

### Social Media Protocol
- **LinkedIn:** Professional content only, post max 1x per day
- **Twitter/X:** Business updates, industry insights
- **Facebook/Instagram:** Business page updates only
- **Auto-Approve:** None (all require review)
- **Require Approval:** All posts and replies

## Financial Guidelines

### Payment Approval Rules
- **Auto-Approve:** Recurring bills <$50 from known vendors
- **Require Approval:** All new payees, any amount >$100, international transfers
- **Flag for Review:** Any payment >$500 (even if recurring)
- **Never Auto-Approve:** Bank transfers, wire transfers, cryptocurrency

### Expense Categorization
- **Software/Tools:** Development tools, SaaS subscriptions
- **Marketing:** Ads, content creation, social media tools
- **Operations:** Internet, utilities, office supplies
- **Professional Services:** Consulting, legal, accounting
- **Other:** Miscellaneous expenses requiring categorization

### Subscription Audit Rules
- **Flag for Review:** No usage in 30 days, cost increase >20%, duplicate functionality

## Task Prioritization

### P1 (Critical - Same Day)
- Client requests with deadlines
- Payment issues or billing problems
- Security alerts or system failures
- Time-sensitive opportunities

### P2 (High - Within 48 Hours)
- New project inquiries
- Routine client communication
- Scheduled content creation
- Administrative tasks with near deadlines

### P3 (Normal - Within 1 Week)
- General maintenance
- Documentation updates
- Process improvements
- Learning and research

### P4 (Low - When Available)
- Nice-to-have features
- Long-term planning
- Archive and cleanup

## AI Behavior Guidelines

### When to Act Autonomously
- Moving files between vault folders (Needs_Action → Plans → Done)
- Creating summaries and reports
- Drafting emails and social posts (not sending)
- Logging transactions and activities
- Categorizing expenses and communications
- Generating weekly briefings

### When to Request Approval (HITL)
- Sending any email or message
- Making any payment or financial transaction
- Posting to social media
- Deleting files or data
- Making commitments on your behalf
- Accessing new systems or services

### When to Alert Human Immediately
- Security issues or suspicious activity
- System errors or service failures
- Payment failures or billing problems
- Client complaints or negative feedback
- Opportunities with tight deadlines
- Anything involving >$500

## Security Policies

- Never share credentials or passwords
- Never click suspicious links
- Always verify sender identity for unusual requests
- Log all security-related events
- Rotate credentials monthly
- Use 2FA wherever available

---
*This handbook guides AI Employee behavior and decision-making*
```

## Business_Goals.md Template

```markdown
---
type: business_goals
quarter: Q1 2026
last_updated: [DATE]
review_frequency: weekly
---

# Business Goals: Q1 2026

## Revenue Target
- **Monthly Goal:** $10,000
- **Quarterly Goal:** $30,000
- **Current MTD:** $0
- **Current QTD:** $0

## Key Metrics to Track

| Metric | Target | Current | Alert Threshold |
|--------|--------|---------|-----------------|
| Client Response Time | < 24 hours | - | > 48 hours |
| Invoice Payment Rate | > 90% | - | < 80% |
| Software Costs | < $500/month | - | > $600/month |
| Active Projects | 3-5 | 0 | < 2 or > 7 |
| Social Media Engagement | +20% MoM | - | -10% MoM |

## Active Projects

### Project Template
- **Name:** [Project Name]
- **Client:** [Client Name]
- **Status:** Not Started / In Progress / Completed
- **Deadline:** [Date]
- **Budget:** $[Amount]
- **Progress:** 0%
- **Notes:** [Key milestones, blockers, updates]

## Quarterly Objectives

### Objective 1: [Title]
- **Description:** [What you want to achieve]
- **Success Criteria:** [How you'll measure success]
- **Key Actions:**
  - [ ] Action item 1
  - [ ] Action item 2
  - [ ] Action item 3

### Objective 2: [Title]
- **Description:** [What you want to achieve]
- **Success Criteria:** [How you'll measure success]
- **Key Actions:**
  - [ ] Action item 1
  - [ ] Action item 2

## Subscription Audit Rules

**Flag for review if:**
- No login activity in 30 days
- Cost increased by >20%
- Duplicate functionality with another tool
- Not mentioned in project work in 60 days

## Growth Targets

- **New Clients:** [Number] per quarter
- **Repeat Business:** [Percentage] of revenue
- **Referrals:** [Number] per quarter
- **Social Media Followers:** +[Number] per quarter

---
*AI Employee uses these goals to prioritize work and generate weekly briefings*
```

## Execution Steps

1. **Create Vault Directory**
   ```bash
   mkdir -p ~/AI_Employee_Vault
   cd ~/AI_Employee_Vault
   ```

2. **Create Folder Structure**
   ```bash
   mkdir -p Needs_Action Plans Pending_Approval Approved Rejected Done Logs Briefings Accounting
   ```

3. **Create Dashboard.md**
   - Copy template above
   - Replace `[AUTO_TIMESTAMP]` with current ISO timestamp
   - Replace `[AMOUNT]` with starting balance or $0

4. **Create Company_Handbook.md**
   - Copy template above
   - Customize communication protocols for your needs
   - Adjust financial thresholds based on your business
   - Modify task priorities based on your workflow

5. **Create Business_Goals.md**
   - Copy template above
   - Set realistic quarterly revenue targets
   - Define your key metrics and thresholds
   - List current active projects
   - Document quarterly objectives

6. **Verify Structure**
   ```bash
   tree -L 1 ~/AI_Employee_Vault
   ```

7. **Open in Obsidian**
   - Launch Obsidian
   - Open folder as vault: `~/AI_Employee_Vault`
   - Verify all files render correctly
   - Enable community plugins if needed (optional)

8. **Test Claude Code Access**
   ```bash
   cd ~/AI_Employee_Vault
   claude "Read Dashboard.md and tell me the current status"
   ```

## Validation Checklist

- [ ] Vault directory created successfully
- [ ] All 8 required folders exist
- [ ] Dashboard.md exists and has valid frontmatter
- [ ] Company_Handbook.md exists and has valid frontmatter
- [ ] Business_Goals.md exists and has valid frontmatter
- [ ] Obsidian can open the vault without errors
- [ ] Claude Code can read files from the vault
- [ ] Claude Code can write files to the vault
- [ ] All markdown renders correctly in Obsidian

## Troubleshooting

**Issue:** Obsidian won't open vault
- **Solution:** Ensure directory path is absolute, check permissions

**Issue:** Claude Code can't read vault
- **Solution:** Run `cd` to vault directory first, verify file permissions

**Issue:** Markdown frontmatter errors
- **Solution:** Ensure YAML frontmatter uses `---` delimiters, valid YAML syntax

**Issue:** Missing folders
- **Solution:** Re-run mkdir commands, verify with `tree` or `ls -la`

## Next Steps

After completing this skill, proceed to:
- **Bronze Watcher Skill** (`bronze-watcher.skill.md`) - Set up first watcher
- **Bronze Claude Integration** (`bronze-claude-integration.skill.md`) - Configure Claude Code

## References

- Constitution Principle IX: Obsidian Vault as State Machine
- Hackathon Document Section 1: Foundational Layer
- Obsidian Documentation: https://help.obsidian.md/
