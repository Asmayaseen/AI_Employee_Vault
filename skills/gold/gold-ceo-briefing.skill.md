# Skill: CEO Briefing Generation (Gold Tier)

## Overview
Generate weekly business intelligence briefings that summarize tasks completed, financial status, engagement metrics, and proactive recommendations.

## Prerequisites
- Audit logger operational (Gold tier)
- Odoo integration for financial data
- Social media integration for engagement data
- Vault structure with historical data

## Capabilities
- **Task Analysis**: Summarize weekly completed tasks by category
- **Financial Overview**: Revenue vs targets, expense trends
- **Engagement Metrics**: Social media performance summary
- **Bottleneck Detection**: Identify stuck items and blockers
- **Proactive Suggestions**: AI-generated recommendations
- **Report Generation**: Formatted Monday morning briefing

## Implementation Details

### Generator: ceo_briefing_generator.py
- Location: `AI_Employee_Vault/Watchers/ceo_briefing_generator.py`
- Schedule: Every Monday at 7:00 AM
- Output: `AI_Employee_Vault/Briefings/`

### Report Sections
1. **Executive Summary** - 3-5 bullet highlights
2. **Tasks Completed** - Categorized list with counts
3. **Financial Snapshot** - Revenue, expenses, outstanding invoices
4. **Engagement Report** - Social media metrics
5. **Attention Required** - Items needing CEO decision
6. **Recommendations** - AI-suggested next actions

### Data Sources
| Source | Data |
|--------|------|
| Vault/Done/ | Completed tasks |
| Vault/Needs_Action/ | Pending items |
| Vault/Logs/ | Activity history |
| Odoo API | Financial data |
| Social MCP | Engagement metrics |

## Acceptance Criteria
- [ ] Briefing generates on schedule
- [ ] All data sources are queried correctly
- [ ] Report is formatted and readable
- [ ] Missing data sources degrade gracefully
- [ ] Briefing saved to Briefings/ folder
