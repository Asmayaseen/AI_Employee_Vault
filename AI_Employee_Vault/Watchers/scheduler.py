"""
Scheduler - Task Scheduling for AI Employee.

Handles scheduled tasks like:
- Daily briefing generation (8:00 AM)
- Weekly reports (Monday 9:00 AM)
- Periodic health checks
- Vault cleanup
- LinkedIn post scheduling

Works with:
- Native Python scheduler (APScheduler)
- Cron (Linux/Mac) - generates crontab entries
- Task Scheduler (Windows) - generates XML task files

Usage:
    # Run built-in scheduler
    python scheduler.py --run

    # Generate cron entries
    python scheduler.py --generate-cron

    # Generate Windows Task Scheduler XML
    python scheduler.py --generate-windows

    # Run a specific task now
    python scheduler.py --task daily_briefing
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Callable
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

try:
    from apscheduler.schedulers.blocking import BlockingScheduler
    from apscheduler.triggers.cron import CronTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False


@dataclass
class ScheduledTask:
    """Definition of a scheduled task."""
    name: str
    description: str
    cron_expression: str  # minute hour day month day_of_week
    command: str
    enabled: bool = True


class AIEmployeeScheduler:
    """
    Manages scheduled tasks for the AI Employee.
    """

    # Task definitions
    TASKS = {
        'daily_briefing': ScheduledTask(
            name='Daily Briefing',
            description='Generate morning briefing at 8:00 AM',
            cron_expression='0 8 * * *',
            command='python claude_processor.py --briefing'
        ),
        'process_items': ScheduledTask(
            name='Process Action Items',
            description='Process pending items every hour',
            cron_expression='0 * * * *',
            command='python claude_processor.py --process-all'
        ),
        'health_check': ScheduledTask(
            name='Health Check',
            description='Check watcher health every 15 minutes',
            cron_expression='*/15 * * * *',
            command='python orchestrator.py --health-only'
        ),
        'vault_cleanup': ScheduledTask(
            name='Vault Cleanup',
            description='Clean old files daily at midnight',
            cron_expression='0 0 * * *',
            command='python scheduler.py --task vault_cleanup'
        ),
        'weekly_report': ScheduledTask(
            name='Weekly Report',
            description='Generate weekly report Monday 9:00 AM',
            cron_expression='0 9 * * 1',
            command='python scheduler.py --task weekly_report'
        ),
        'linkedin_post': ScheduledTask(
            name='LinkedIn Post Check',
            description='Check scheduled LinkedIn posts',
            cron_expression='0 */4 * * *',
            command='python scheduler.py --task linkedin_post_check'
        )
    }

    def __init__(self, vault_path: str = None):
        self.vault_path = Path(vault_path or os.getenv(
            'VAULT_PATH',
            '/mnt/d/Ai-Employee/AI_Employee_Vault'
        ))
        self.watchers_dir = self.vault_path / 'Watchers'
        self.logs_dir = self.vault_path / 'Logs'
        self.briefings_dir = self.vault_path / 'Briefings'
        self.done_dir = self.vault_path / 'Done'

        # Ensure directories
        self.logs_dir.mkdir(exist_ok=True)
        self.briefings_dir.mkdir(exist_ok=True)

        self.scheduler = None
        if APSCHEDULER_AVAILABLE:
            self.scheduler = BlockingScheduler()

    def _log(self, task_name: str, status: str, details: dict = None):
        """Log task execution."""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'task': task_name,
            'status': status,
            'details': details or {}
        }

        log_file = self.logs_dir / f"{datetime.now().strftime('%Y-%m-%d')}_scheduler.json"
        logs = []
        if log_file.exists():
            try:
                logs = json.loads(log_file.read_text())
            except:
                logs = []
        logs.append(log_entry)
        log_file.write_text(json.dumps(logs, indent=2))

    # ==================== Task Implementations ====================

    def task_daily_briefing(self):
        """Generate daily briefing."""
        print(f"[{datetime.now()}] Running: Daily Briefing")

        try:
            from claude_processor import ClaudeProcessor
            processor = ClaudeProcessor(vault_path=str(self.vault_path))
            briefing_path = processor.generate_briefing()

            self._log('daily_briefing', 'success', {'file': str(briefing_path)})
            print(f"Briefing generated: {briefing_path}")
            return True

        except Exception as e:
            self._log('daily_briefing', 'error', {'error': str(e)})
            print(f"Error: {e}")
            return False

    def task_process_items(self):
        """Process all pending items."""
        print(f"[{datetime.now()}] Running: Process Items")

        try:
            from claude_processor import ClaudeProcessor
            processor = ClaudeProcessor(vault_path=str(self.vault_path))
            results = processor.process_all()

            self._log('process_items', 'success', {'processed': len(results)})
            print(f"Processed {len(results)} items")
            return True

        except Exception as e:
            self._log('process_items', 'error', {'error': str(e)})
            print(f"Error: {e}")
            return False

    def task_health_check(self):
        """Run health check on watchers."""
        print(f"[{datetime.now()}] Running: Health Check")

        try:
            from orchestrator import Orchestrator
            orch = Orchestrator(vault_path=str(self.vault_path))
            health = orch.check_health()

            unhealthy = [k for k, v in health.items() if not v]

            self._log('health_check', 'success', {
                'healthy': list(health.keys()),
                'unhealthy': unhealthy
            })

            if unhealthy:
                print(f"⚠️ Unhealthy watchers: {unhealthy}")
            else:
                print("All watchers healthy")

            return len(unhealthy) == 0

        except Exception as e:
            self._log('health_check', 'error', {'error': str(e)})
            print(f"Error: {e}")
            return False

    def task_vault_cleanup(self):
        """Clean up old files in Done folder."""
        print(f"[{datetime.now()}] Running: Vault Cleanup")

        retention_days = int(os.getenv('CLEANUP_RETENTION_DAYS', '30'))
        cutoff = datetime.now() - timedelta(days=retention_days)

        cleaned = 0
        try:
            # Clean Done folder
            for filepath in self.done_dir.glob('*.md'):
                if datetime.fromtimestamp(filepath.stat().st_mtime) < cutoff:
                    # Move to archive instead of delete
                    archive_dir = self.vault_path / 'Archive' / cutoff.strftime('%Y-%m')
                    archive_dir.mkdir(parents=True, exist_ok=True)

                    archive_path = archive_dir / filepath.name
                    filepath.rename(archive_path)
                    cleaned += 1

            self._log('vault_cleanup', 'success', {
                'archived': cleaned,
                'retention_days': retention_days
            })
            print(f"Archived {cleaned} files older than {retention_days} days")
            return True

        except Exception as e:
            self._log('vault_cleanup', 'error', {'error': str(e)})
            print(f"Error: {e}")
            return False

    def task_weekly_report(self):
        """Generate weekly business report."""
        print(f"[{datetime.now()}] Running: Weekly Report")

        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)

            # Count completed items
            done_count = 0
            for filepath in self.done_dir.glob('*.md'):
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                if start_date <= mtime <= end_date:
                    done_count += 1

            # Count by type
            type_counts = {}
            for filepath in self.done_dir.glob('*.md'):
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                if start_date <= mtime <= end_date:
                    # Extract type from filename prefix
                    parts = filepath.stem.split('_')
                    item_type = parts[0] if parts else 'unknown'
                    type_counts[item_type] = type_counts.get(item_type, 0) + 1

            # Generate report
            report = f'''---
generated: {datetime.now().isoformat()}
type: weekly_report
period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}
---

# Weekly Report

## Period
{start_date.strftime('%B %d')} - {end_date.strftime('%B %d, %Y')}

## Summary

| Metric | Value |
|--------|-------|
| Total Completed | {done_count} |

## Breakdown by Type

'''
            for item_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
                report += f"- **{item_type}**: {count}\n"

            report += f'''

## Recommendations

- Review patterns in completed items
- Identify recurring task types for automation
- Consider process improvements

---
*Generated automatically by AI Employee*
'''

            filename = f"WEEKLY_{end_date.strftime('%Y-%m-%d')}.md"
            filepath = self.briefings_dir / filename
            filepath.write_text(report, encoding='utf-8')

            self._log('weekly_report', 'success', {
                'file': str(filepath),
                'items_count': done_count
            })
            print(f"Weekly report generated: {filename}")
            return True

        except Exception as e:
            self._log('weekly_report', 'error', {'error': str(e)})
            print(f"Error: {e}")
            return False

    def task_linkedin_post_check(self):
        """Check and execute scheduled LinkedIn posts."""
        print(f"[{datetime.now()}] Running: LinkedIn Post Check")

        try:
            queue_file = self.vault_path / 'Plans' / 'linkedin_posts_queue.json'

            if not queue_file.exists():
                print("No posts scheduled")
                return True

            queue = json.loads(queue_file.read_text())
            now = datetime.now()
            updated_queue = []
            posted = 0

            for post in queue:
                scheduled_time = datetime.fromisoformat(post['scheduled_time'])

                if post['status'] == 'pending' and scheduled_time <= now:
                    # Time to post - create approval request
                    from linkedin_watcher import LinkedInWatcher
                    watcher = LinkedInWatcher(vault_path=str(self.vault_path))
                    result = watcher._create_post_approval(post['content'])

                    post['status'] = 'pending_approval'
                    post['approval_file'] = result.get('file')
                    posted += 1

                updated_queue.append(post)

            # Save updated queue
            queue_file.write_text(json.dumps(updated_queue, indent=2))

            self._log('linkedin_post_check', 'success', {
                'posts_triggered': posted
            })
            print(f"Triggered {posted} scheduled posts")
            return True

        except Exception as e:
            self._log('linkedin_post_check', 'error', {'error': str(e)})
            print(f"Error: {e}")
            return False

    # ==================== Scheduler Methods ====================

    def run_task(self, task_name: str) -> bool:
        """Run a specific task immediately."""
        task_methods = {
            'daily_briefing': self.task_daily_briefing,
            'process_items': self.task_process_items,
            'health_check': self.task_health_check,
            'vault_cleanup': self.task_vault_cleanup,
            'weekly_report': self.task_weekly_report,
            'linkedin_post_check': self.task_linkedin_post_check
        }

        method = task_methods.get(task_name)
        if method:
            return method()
        else:
            print(f"Unknown task: {task_name}")
            return False

    def setup_scheduler(self):
        """Setup APScheduler with all tasks."""
        if not APSCHEDULER_AVAILABLE:
            print("APScheduler not available. Install with: pip install apscheduler")
            return

        task_methods = {
            'daily_briefing': self.task_daily_briefing,
            'process_items': self.task_process_items,
            'health_check': self.task_health_check,
            'vault_cleanup': self.task_vault_cleanup,
            'weekly_report': self.task_weekly_report,
            'linkedin_post_check': self.task_linkedin_post_check
        }

        for task_id, task_def in self.TASKS.items():
            if task_def.enabled and task_id in task_methods:
                parts = task_def.cron_expression.split()
                self.scheduler.add_job(
                    task_methods[task_id],
                    CronTrigger(
                        minute=parts[0],
                        hour=parts[1],
                        day=parts[2],
                        month=parts[3],
                        day_of_week=parts[4]
                    ),
                    id=task_id,
                    name=task_def.name
                )
                print(f"Scheduled: {task_def.name} ({task_def.cron_expression})")

    def run(self):
        """Run the scheduler."""
        if not APSCHEDULER_AVAILABLE:
            print("APScheduler required. Install with: pip install apscheduler")
            return

        self.setup_scheduler()

        print("\n" + "=" * 50)
        print("AI Employee Scheduler Running")
        print("=" * 50)
        print("Press Ctrl+C to stop\n")

        try:
            self.scheduler.start()
        except KeyboardInterrupt:
            print("\nScheduler stopped")

    # ==================== Cron/Windows Integration ====================

    def generate_cron(self) -> str:
        """Generate crontab entries for all tasks."""
        python_path = sys.executable
        script_dir = self.watchers_dir

        lines = [
            "# AI Employee Scheduled Tasks",
            f"# Generated: {datetime.now().isoformat()}",
            f"# Vault: {self.vault_path}",
            "",
            "# Environment",
            f"VAULT_PATH={self.vault_path}",
            ""
        ]

        for task_id, task_def in self.TASKS.items():
            if task_def.enabled:
                lines.append(f"# {task_def.description}")
                lines.append(f"{task_def.cron_expression} cd {script_dir} && {python_path} {task_def.command}")
                lines.append("")

        return '\n'.join(lines)

    def generate_windows_task(self, task_id: str) -> str:
        """Generate Windows Task Scheduler XML for a task."""
        task_def = self.TASKS.get(task_id)
        if not task_def:
            return ""

        # Parse cron expression
        parts = task_def.cron_expression.split()
        minute, hour, day, month, dow = parts

        # Convert to Windows trigger (simplified)
        trigger_xml = ""
        if dow != '*':
            # Weekly trigger
            days_map = {'0': 'Sunday', '1': 'Monday', '2': 'Tuesday', '3': 'Wednesday',
                        '4': 'Thursday', '5': 'Friday', '6': 'Saturday'}
            day_name = days_map.get(dow, 'Monday')
            trigger_xml = f'''
    <CalendarTrigger>
      <StartBoundary>{datetime.now().strftime('%Y-%m-%d')}T{hour.zfill(2)}:{minute.zfill(2)}:00</StartBoundary>
      <ScheduleByWeek>
        <DaysOfWeek><{day_name}/></DaysOfWeek>
        <WeeksInterval>1</WeeksInterval>
      </ScheduleByWeek>
    </CalendarTrigger>'''
        else:
            # Daily trigger
            trigger_xml = f'''
    <CalendarTrigger>
      <StartBoundary>{datetime.now().strftime('%Y-%m-%d')}T{hour.zfill(2)}:{minute.zfill(2)}:00</StartBoundary>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>'''

        xml = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.2" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>{task_def.description}</Description>
    <Author>AI Employee</Author>
  </RegistrationInfo>
  <Triggers>{trigger_xml}
  </Triggers>
  <Actions>
    <Exec>
      <Command>{sys.executable}</Command>
      <Arguments>{task_def.command}</Arguments>
      <WorkingDirectory>{self.watchers_dir}</WorkingDirectory>
    </Exec>
  </Actions>
  <Settings>
    <Enabled>true</Enabled>
    <AllowStartOnDemand>true</AllowStartOnDemand>
  </Settings>
</Task>'''

        return xml


# CLI execution
if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='AI Employee Scheduler')
    parser.add_argument('--vault', '-v', help='Path to vault')
    parser.add_argument('--run', action='store_true', help='Run scheduler')
    parser.add_argument('--task', help='Run specific task now')
    parser.add_argument('--list', action='store_true', help='List all tasks')
    parser.add_argument('--generate-cron', action='store_true', help='Generate crontab')
    parser.add_argument('--generate-windows', help='Generate Windows XML for task')

    args = parser.parse_args()

    vault_path = args.vault or os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')
    scheduler = AIEmployeeScheduler(vault_path=vault_path)

    if args.run:
        scheduler.run()

    elif args.task:
        success = scheduler.run_task(args.task)
        sys.exit(0 if success else 1)

    elif args.list:
        print("\nScheduled Tasks:")
        print("-" * 60)
        for task_id, task_def in AIEmployeeScheduler.TASKS.items():
            status = "✅" if task_def.enabled else "❌"
            print(f"{status} {task_id}")
            print(f"   {task_def.description}")
            print(f"   Cron: {task_def.cron_expression}")
            print()

    elif args.generate_cron:
        print(scheduler.generate_cron())

    elif args.generate_windows:
        xml = scheduler.generate_windows_task(args.generate_windows)
        if xml:
            print(xml)
        else:
            print(f"Unknown task: {args.generate_windows}")

    else:
        parser.print_help()
