#!/usr/bin/env python3
"""
CEO Briefing Generator - Weekly Business Audit & Report

This script generates the "Monday Morning CEO Briefing" by:
1. Analyzing completed tasks from /Done folder
2. Reviewing business goals from Business_Goals.md
3. Checking pending items and bottlenecks
4. Generating a comprehensive briefing report

Scheduled to run: Sunday 8:00 PM (via cron)

Usage:
    python ceo_briefing_generator.py              # Generate this week's briefing
    python ceo_briefing_generator.py --preview    # Preview without saving
    python ceo_briefing_generator.py --period 14  # Custom period (days)
"""

import os
import re
import sys
import json
import asyncio
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from collections import defaultdict

# Add MCP paths for Odoo integration
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'MCP_Servers', 'odoo-mcp'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'MCP_Servers', 'social-mcp'))


@dataclass
class TaskInfo:
    """Information about a completed task."""
    filename: str
    title: str
    completed_date: datetime
    task_type: str  # email, file, plan, etc.
    priority: str = "normal"
    duration_days: int = 0


@dataclass
class BusinessGoals:
    """Business goals and metrics."""
    revenue_target: float = 0.0
    revenue_current: float = 0.0
    metrics: Dict[str, Dict] = field(default_factory=dict)
    active_projects: List[Dict] = field(default_factory=list)
    subscription_rules: List[str] = field(default_factory=list)


@dataclass
class AccountingData:
    """Financial data from Odoo for CEO briefing."""
    revenue_total: float = 0.0
    revenue_collected: float = 0.0
    expenses_total: float = 0.0
    net_profit: float = 0.0
    profit_margin: float = 0.0
    outstanding_receivables: float = 0.0
    overdue_receivables: float = 0.0
    invoice_count: int = 0
    top_customers: List[Dict] = field(default_factory=list)
    top_expenses: List[Dict] = field(default_factory=list)
    subscriptions: List[Dict] = field(default_factory=list)
    subscription_flags: List[Dict] = field(default_factory=list)
    available: bool = False
    error: Optional[str] = None


@dataclass
class BriefingData:
    """All data for CEO briefing."""
    period_start: datetime
    period_end: datetime
    completed_tasks: List[TaskInfo] = field(default_factory=list)
    pending_tasks: List[str] = field(default_factory=list)
    approval_waiting: List[str] = field(default_factory=list)
    bottlenecks: List[Dict] = field(default_factory=list)
    goals: BusinessGoals = field(default_factory=BusinessGoals)
    suggestions: List[str] = field(default_factory=list)
    accounting: AccountingData = field(default_factory=AccountingData)


class CEOBriefingGenerator:
    """Generates weekly CEO briefing reports."""

    def __init__(self, vault_path: str = None):
        """Initialize the generator."""
        self.vault_path = Path(vault_path or os.getenv(
            'VAULT_PATH',
            '/mnt/d/Ai-Employee/AI_Employee_Vault'
        ))
        self.briefings_dir = self.vault_path / 'Briefings'
        self.briefings_dir.mkdir(exist_ok=True)

        # Folder paths
        self.done_folder = self.vault_path / 'Done'
        self.needs_action = self.vault_path / 'Needs_Action'
        self.pending_approval = self.vault_path / 'Pending_Approval'
        self.plans_folder = self.vault_path / 'Plans'

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Parse YAML frontmatter from markdown file."""
        frontmatter = {}
        if content.startswith('---'):
            parts = content.split('---', 2)
            if len(parts) >= 3:
                yaml_content = parts[1].strip()
                for line in yaml_content.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        frontmatter[key.strip()] = value.strip()
        return frontmatter

    def _get_file_date(self, filepath: Path) -> datetime:
        """Get date from file (from name or modification time)."""
        # Try to extract date from filename
        filename = filepath.stem

        # Pattern: DATE_YYYYMMDD or YYYYMMDD or 2026-01-15
        date_patterns = [
            r'(\d{4})(\d{2})(\d{2})',  # YYYYMMDD
            r'(\d{4})-(\d{2})-(\d{2})',  # YYYY-MM-DD
        ]

        for pattern in date_patterns:
            match = re.search(pattern, filename)
            if match:
                try:
                    year, month, day = match.groups()
                    return datetime(int(year), int(month), int(day))
                except ValueError:
                    pass

        # Fall back to file modification time
        return datetime.fromtimestamp(filepath.stat().st_mtime)

    def _get_task_type(self, filename: str) -> str:
        """Determine task type from filename."""
        filename_lower = filename.lower()
        if 'email' in filename_lower:
            return 'email'
        elif 'file' in filename_lower:
            return 'file_processing'
        elif 'plan' in filename_lower:
            return 'planning'
        elif 'linkedin' in filename_lower:
            return 'social_media'
        elif 'whatsapp' in filename_lower:
            return 'messaging'
        elif 'approval' in filename_lower:
            return 'approval'
        else:
            return 'general'

    def _get_task_title(self, filepath: Path) -> str:
        """Extract title from task file."""
        try:
            content = filepath.read_text(encoding='utf-8')

            # Try to get title from frontmatter
            frontmatter = self._parse_frontmatter(content)
            if 'title' in frontmatter:
                return frontmatter['title']
            if 'subject' in frontmatter:
                return frontmatter['subject']

            # Try to get first heading
            for line in content.split('\n'):
                if line.startswith('# '):
                    return line[2:].strip()
                if line.startswith('## '):
                    return line[3:].strip()

            # Fall back to filename
            return filepath.stem.replace('_', ' ').title()

        except Exception:
            return filepath.stem.replace('_', ' ').title()

    def collect_completed_tasks(self, period_days: int = 7) -> List[TaskInfo]:
        """Collect tasks completed in the given period."""
        tasks = []
        cutoff_date = datetime.now() - timedelta(days=period_days)

        if not self.done_folder.exists():
            return tasks

        for filepath in self.done_folder.glob('*.md'):
            file_date = self._get_file_date(filepath)

            if file_date >= cutoff_date:
                task = TaskInfo(
                    filename=filepath.name,
                    title=self._get_task_title(filepath),
                    completed_date=file_date,
                    task_type=self._get_task_type(filepath.name)
                )
                tasks.append(task)

        # Sort by completion date (newest first)
        tasks.sort(key=lambda x: x.completed_date, reverse=True)
        return tasks

    def collect_pending_items(self) -> tuple[List[str], List[str]]:
        """Collect pending tasks and items awaiting approval."""
        pending = []
        approval = []

        # Needs Action items
        if self.needs_action.exists():
            for filepath in self.needs_action.glob('*.md'):
                title = self._get_task_title(filepath)
                pending.append(title)

        # Pending Approval items
        if self.pending_approval.exists():
            for filepath in self.pending_approval.glob('*.md'):
                title = self._get_task_title(filepath)
                approval.append(title)

        return pending, approval

    def load_business_goals(self) -> BusinessGoals:
        """Load business goals from Business_Goals.md."""
        goals = BusinessGoals()
        goals_file = self.vault_path / 'Business_Goals.md'

        if not goals_file.exists():
            # Create default business goals file
            self._create_default_goals_file(goals_file)
            return goals

        try:
            content = goals_file.read_text(encoding='utf-8')

            # Parse revenue target
            revenue_match = re.search(r'Monthly goal:\s*\$?([\d,]+)', content)
            if revenue_match:
                goals.revenue_target = float(revenue_match.group(1).replace(',', ''))

            # Parse current revenue
            current_match = re.search(r'Current MTD:\s*\$?([\d,]+)', content)
            if current_match:
                goals.revenue_current = float(current_match.group(1).replace(',', ''))

            # Parse active projects
            project_pattern = r'\d+\.\s+([^-]+)\s*-\s*Due\s+([^-]+)\s*-\s*Budget\s*\$?([\d,]+)'
            for match in re.finditer(project_pattern, content):
                goals.active_projects.append({
                    'name': match.group(1).strip(),
                    'due': match.group(2).strip(),
                    'budget': float(match.group(3).replace(',', ''))
                })

        except Exception as e:
            print(f"Warning: Error parsing Business_Goals.md: {e}")

        return goals

    def _create_default_goals_file(self, filepath: Path):
        """Create default Business_Goals.md file."""
        default_content = '''---
last_updated: {date}
review_frequency: weekly
---

# Business Goals

## Q1 2026 Objectives

### Revenue Target
- Monthly goal: $10,000
- Current MTD: $0

### Key Metrics to Track
| Metric | Target | Alert Threshold |
|--------|--------|-----------------|
| Client response time | < 24 hours | > 48 hours |
| Task completion rate | > 90% | < 80% |
| Pending items | < 10 | > 20 |

### Active Projects
1. Project Alpha - Due Jan 31 - Budget $5,000

### Subscription Audit Rules
Flag for review if:
- No activity in 30 days
- Cost increased > 20%
- Duplicate functionality
'''.format(date=datetime.now().strftime('%Y-%m-%d'))

        filepath.write_text(default_content)

    def identify_bottlenecks(self, tasks: List[TaskInfo]) -> List[Dict]:
        """Identify tasks that took too long."""
        bottlenecks = []

        # Define expected durations by task type (in days)
        expected_durations = {
            'email': 1,
            'file_processing': 1,
            'planning': 2,
            'social_media': 1,
            'messaging': 1,
            'approval': 2,
            'general': 2
        }

        for task in tasks:
            expected = expected_durations.get(task.task_type, 2)
            if task.duration_days > expected:
                bottlenecks.append({
                    'task': task.title,
                    'expected': f"{expected} days",
                    'actual': f"{task.duration_days} days",
                    'delay': f"+{task.duration_days - expected} days"
                })

        return bottlenecks

    def generate_suggestions(self, data: BriefingData) -> List[str]:
        """Generate proactive suggestions based on data."""
        suggestions = []

        # Pending items suggestion
        if len(data.pending_tasks) > 10:
            suggestions.append(
                f"High pending count ({len(data.pending_tasks)} items). "
                "Consider prioritizing or delegating some tasks."
            )

        # Approval backlog
        if len(data.approval_waiting) > 5:
            suggestions.append(
                f"Approval backlog detected ({len(data.approval_waiting)} items). "
                "Review /Pending_Approval folder to avoid delays."
            )

        # Revenue tracking
        if data.goals.revenue_target > 0:
            progress = (data.goals.revenue_current / data.goals.revenue_target) * 100
            day_of_month = datetime.now().day
            expected_progress = (day_of_month / 30) * 100

            if progress < expected_progress - 10:
                suggestions.append(
                    f"Revenue behind target ({progress:.0f}% vs expected {expected_progress:.0f}%). "
                    "Focus on closing pending deals."
                )

        # Project deadlines
        for project in data.goals.active_projects:
            try:
                # Parse due date
                due_str = project.get('due', '')
                # Try to parse various date formats
                for fmt in ['%b %d', '%Y-%m-%d', '%m/%d']:
                    try:
                        due_date = datetime.strptime(due_str, fmt)
                        if due_date.year == 1900:  # Year not specified
                            due_date = due_date.replace(year=datetime.now().year)

                        days_until = (due_date - datetime.now()).days
                        if 0 < days_until <= 7:
                            suggestions.append(
                                f"Upcoming deadline: {project['name']} due in {days_until} days"
                            )
                        break
                    except ValueError:
                        continue
            except Exception:
                pass

        # Bottleneck suggestion
        if len(data.bottlenecks) > 2:
            suggestions.append(
                f"Multiple bottlenecks detected ({len(data.bottlenecks)} tasks delayed). "
                "Review workflow for optimization opportunities."
            )

        # Accounting suggestions (from Odoo)
        if data.accounting.available:
            acct = data.accounting

            # Overdue receivables
            if acct.overdue_receivables > 0:
                suggestions.append(
                    f"Overdue receivables: ${acct.overdue_receivables:,.2f}. "
                    "Follow up on unpaid invoices to improve cash flow."
                )

            # Profit margin check
            if acct.profit_margin < 20 and acct.revenue_total > 0:
                suggestions.append(
                    f"Profit margin at {acct.profit_margin:.1f}% (below 20% target). "
                    "Review expenses or increase pricing."
                )

            # Subscription cost flags
            for flag in acct.subscription_flags[:2]:
                suggestions.append(
                    f"Subscription alert: {flag.get('message', 'Cost change detected')}"
                )

        return suggestions

    def collect_accounting_data(self) -> AccountingData:
        """Pull financial data from Odoo MCP for accounting audit."""
        acct = AccountingData()

        try:
            from tools.accounting_tools import get_financial_summary, get_subscription_audit

            # Get financial summary for this month
            summary_result = asyncio.get_event_loop().run_until_complete(
                get_financial_summary({'period': 'this_month'})
            )

            if summary_result.get('success'):
                revenue = summary_result.get('revenue', {})
                expenses = summary_result.get('expenses', {})
                profit = summary_result.get('profit', {})
                receivables = summary_result.get('receivables', {})

                acct.revenue_total = revenue.get('total', 0)
                acct.revenue_collected = revenue.get('collected', 0)
                acct.invoice_count = revenue.get('invoice_count', 0)
                acct.expenses_total = expenses.get('total', 0)
                acct.net_profit = profit.get('net', 0)
                acct.profit_margin = profit.get('margin', 0)
                acct.outstanding_receivables = receivables.get('total_outstanding', 0)
                acct.overdue_receivables = receivables.get('overdue', 0)
                acct.top_customers = summary_result.get('top_customers', [])
                acct.top_expenses = summary_result.get('top_expenses', [])
                acct.available = True

            # Get subscription audit
            audit_result = asyncio.get_event_loop().run_until_complete(
                get_subscription_audit({'months_back': 3})
            )

            if audit_result.get('success'):
                acct.subscriptions = audit_result.get('subscriptions', [])
                acct.subscription_flags = audit_result.get('flags', [])

        except ImportError:
            acct.error = "Odoo MCP not available - install and configure to enable accounting audit"
        except Exception as e:
            acct.error = f"Odoo connection error: {str(e)}"

        return acct

    def generate_briefing(self, period_days: int = 7, preview: bool = False) -> str:
        """Generate the CEO briefing report."""
        # Collect all data
        data = BriefingData(
            period_start=datetime.now() - timedelta(days=period_days),
            period_end=datetime.now()
        )

        data.completed_tasks = self.collect_completed_tasks(period_days)
        data.pending_tasks, data.approval_waiting = self.collect_pending_items()
        data.goals = self.load_business_goals()
        data.bottlenecks = self.identify_bottlenecks(data.completed_tasks)
        data.accounting = self.collect_accounting_data()
        data.suggestions = self.generate_suggestions(data)

        # Generate report content
        report = self._format_report(data)

        if not preview:
            # Save to file
            filename = f"{datetime.now().strftime('%Y-%m-%d')}_Monday_Briefing.md"
            filepath = self.briefings_dir / filename
            filepath.write_text(report, encoding='utf-8')
            print(f"✅ CEO Briefing saved to: {filepath}")

        return report

    def _format_report(self, data: BriefingData) -> str:
        """Format the briefing report as markdown."""
        now = datetime.now()

        # Executive summary
        task_count = len(data.completed_tasks)
        pending_count = len(data.pending_tasks)

        if task_count >= 10 and pending_count < 10:
            summary = "Excellent week! High productivity with manageable backlog."
        elif task_count >= 5:
            summary = "Good progress this week. Some items need attention."
        else:
            summary = "Light activity this period. Review priorities."

        # Revenue section
        revenue_section = ""
        if data.goals.revenue_target > 0:
            progress = (data.goals.revenue_current / data.goals.revenue_target) * 100
            trend = "On track" if progress >= 50 else "Needs attention"
            revenue_section = f"""
## Revenue
- **Monthly Target**: ${data.goals.revenue_target:,.2f}
- **Current MTD**: ${data.goals.revenue_current:,.2f} ({progress:.0f}% of target)
- **Trend**: {trend}
"""

        # Completed tasks
        completed_section = ""
        if data.completed_tasks:
            task_lines = []
            for task in data.completed_tasks[:15]:  # Limit to 15 tasks
                task_lines.append(f"- [x] {task.title}")
            completed_section = "\n## Completed Tasks\n" + "\n".join(task_lines)

        # Pending items
        pending_section = ""
        if data.pending_tasks:
            pending_lines = [f"- [ ] {task}" for task in data.pending_tasks[:10]]
            pending_section = f"\n## Pending Items ({len(data.pending_tasks)} total)\n" + "\n".join(pending_lines)

        # Approval waiting
        approval_section = ""
        if data.approval_waiting:
            approval_lines = [f"- ⏳ {item}" for item in data.approval_waiting]
            approval_section = f"\n## Awaiting Approval ({len(data.approval_waiting)})\n" + "\n".join(approval_lines)

        # Bottlenecks
        bottleneck_section = ""
        if data.bottlenecks:
            bottleneck_section = """
## Bottlenecks
| Task | Expected | Actual | Delay |
|------|----------|--------|-------|
"""
            for b in data.bottlenecks[:5]:
                bottleneck_section += f"| {b['task'][:30]} | {b['expected']} | {b['actual']} | {b['delay']} |\n"

        # Suggestions
        suggestions_section = ""
        if data.suggestions:
            suggestions_section = "\n## Proactive Suggestions\n"
            for i, suggestion in enumerate(data.suggestions, 1):
                suggestions_section += f"\n### {i}. Action Item\n{suggestion}\n"

        # Upcoming deadlines
        deadlines_section = ""
        if data.goals.active_projects:
            deadlines_section = "\n## Upcoming Deadlines\n"
            for project in data.goals.active_projects:
                deadlines_section += f"- {project['name']}: Due {project['due']} (Budget: ${project['budget']:,.0f})\n"

        # Accounting section (from Odoo)
        accounting_section = ""
        if data.accounting.available:
            acct = data.accounting
            accounting_section = f"""
## Financial Summary (Odoo)
| Metric | Amount |
|--------|--------|
| Revenue (MTD) | ${acct.revenue_total:,.2f} |
| Collected | ${acct.revenue_collected:,.2f} |
| Expenses (MTD) | ${acct.expenses_total:,.2f} |
| **Net Profit** | **${acct.net_profit:,.2f}** |
| Profit Margin | {acct.profit_margin:.1f}% |
| Outstanding Receivables | ${acct.outstanding_receivables:,.2f} |
| Overdue Receivables | ${acct.overdue_receivables:,.2f} |
| Invoices This Month | {acct.invoice_count} |
"""
            # Top customers
            if acct.top_customers:
                accounting_section += "\n### Top Customers\n"
                for c in acct.top_customers[:5]:
                    accounting_section += f"- {c.get('name', 'Unknown')}: ${c.get('revenue', 0):,.2f}\n"

            # Top expenses
            if acct.top_expenses:
                accounting_section += "\n### Top Expense Categories\n"
                for e in acct.top_expenses[:5]:
                    accounting_section += f"- {e.get('vendor', 'Unknown')}: ${e.get('amount', 0):,.2f}\n"

            # Subscription audit
            if acct.subscriptions:
                accounting_section += f"\n### Subscription Audit ({len(acct.subscriptions)} recurring)\n"
                accounting_section += "| Vendor | Monthly Cost | Occurrences |\n"
                accounting_section += "|--------|-------------|-------------|\n"
                for s in acct.subscriptions[:8]:
                    accounting_section += f"| {s.get('vendor', '?')} | ${s.get('avg_monthly_cost', 0):,.2f} | {s.get('occurrences', 0)} |\n"

            # Subscription flags
            if acct.subscription_flags:
                accounting_section += "\n### Cost Alerts\n"
                for f in acct.subscription_flags:
                    accounting_section += f"- {f.get('message', 'Unknown alert')}\n"

        elif data.accounting.error:
            accounting_section = f"\n## Financial Summary\n*{data.accounting.error}*\n"

        # Compose full report
        report = f'''---
generated: {now.isoformat()}
period: {data.period_start.strftime('%Y-%m-%d')} to {data.period_end.strftime('%Y-%m-%d')}
---

# Monday Morning CEO Briefing

**Week of {now.strftime('%B %d, %Y')}**

## Executive Summary
{summary}

| Metric | This Week |
|--------|-----------|
| Tasks Completed | {len(data.completed_tasks)} |
| Pending Items | {len(data.pending_tasks)} |
| Awaiting Approval | {len(data.approval_waiting)} |
| Bottlenecks | {len(data.bottlenecks)} |
{revenue_section}{accounting_section}{completed_section}{pending_section}{approval_section}{bottleneck_section}{suggestions_section}{deadlines_section}
---
*Generated by AI Employee v2.0 (Gold Tier) on {now.strftime('%Y-%m-%d %H:%M:%S')}*
'''
        return report


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Generate CEO Briefing Report')
    parser.add_argument('--vault', '-v', help='Path to Obsidian vault')
    parser.add_argument('--period', '-p', type=int, default=7, help='Period in days (default: 7)')
    parser.add_argument('--preview', action='store_true', help='Preview without saving')

    args = parser.parse_args()

    generator = CEOBriefingGenerator(vault_path=args.vault)

    print("=" * 50)
    print("  CEO Briefing Generator")
    print("=" * 50)
    print(f"Period: Last {args.period} days")
    print(f"Vault: {generator.vault_path}")
    print()

    report = generator.generate_briefing(period_days=args.period, preview=args.preview)

    if args.preview:
        print("\n" + "=" * 50)
        print("  PREVIEW")
        print("=" * 50)
        print(report)


if __name__ == '__main__':
    main()
