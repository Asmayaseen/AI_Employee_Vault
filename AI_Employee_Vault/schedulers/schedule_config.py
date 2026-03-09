"""
Schedule Configuration - Defines all scheduled tasks and their timing.

This is the single source of truth for task schedules.
Referenced by Watchers/scheduler.py for execution.

Constitution Reference:
- Principle III (Audit Logging): Log cleanup scheduled daily
- Principle V (Graceful Degradation): Health checks every 15 min
- Principle VIII (Watcher Pattern): Managed by process supervisor
"""

# Schedule definitions: name -> (cron_expression, description, command)
# Cron format: minute hour day_of_month month day_of_week

SCHEDULES = {
    # ============ Daily Tasks ============
    'daily_briefing': {
        'cron': '0 8 * * *',
        'description': 'Generate CEO morning briefing at 8:00 AM',
        'command': 'python Watchers/ceo_briefing_generator.py',
        'enabled': True,
        'tier': 'gold',
    },
    'process_items': {
        'cron': '0 * * * *',
        'description': 'Process pending action items every hour',
        'command': 'python Watchers/claude_processor.py --process-all',
        'enabled': True,
        'tier': 'silver',
    },
    'vault_cleanup': {
        'cron': '0 0 * * *',
        'description': 'Clean old files daily at midnight',
        'command': 'python scripts/vault_cleanup.py --execute',
        'enabled': True,
        'tier': 'gold',
    },

    # ============ Periodic Tasks ============
    'health_check': {
        'cron': '*/15 * * * *',
        'description': 'Check watcher health every 15 minutes',
        'command': 'python Watchers/orchestrator.py --health-only',
        'enabled': True,
        'tier': 'silver',
    },
    'log_export': {
        'cron': '0 23 * * 0',
        'description': 'Weekly log export Sunday 11 PM',
        'command': 'python scripts/export_logs.py --days 7 --format csv',
        'enabled': False,
        'tier': 'gold',
    },

    # ============ Weekly Tasks ============
    'weekly_report': {
        'cron': '0 9 * * 1',
        'description': 'Generate weekly report Monday 9:00 AM',
        'command': 'python Watchers/scheduler.py --task weekly_report',
        'enabled': True,
        'tier': 'silver',
    },
    'linkedin_post': {
        'cron': '0 */4 * * *',
        'description': 'Check scheduled LinkedIn posts',
        'command': 'python Watchers/scheduler.py --task linkedin_post_check',
        'enabled': True,
        'tier': 'silver',
    },
}


def get_enabled_schedules(tier: str = 'gold') -> dict:
    """
    Get all enabled schedules up to and including the specified tier.

    Args:
        tier: Maximum tier level ('bronze', 'silver', 'gold', 'platinum').

    Returns:
        Dictionary of enabled schedule configs.
    """
    tier_order = {'bronze': 0, 'silver': 1, 'gold': 2, 'platinum': 3}
    max_level = tier_order.get(tier, 2)

    return {
        name: config
        for name, config in SCHEDULES.items()
        if config['enabled'] and tier_order.get(config['tier'], 0) <= max_level
    }


def generate_crontab(tier: str = 'gold', python_path: str = 'python3') -> str:
    """
    Generate crontab entries for all enabled schedules.

    Args:
        tier: Maximum tier level.
        python_path: Path to Python interpreter.

    Returns:
        Crontab-formatted string.
    """
    lines = [
        f"# AI Employee Scheduled Tasks - Generated {__import__('datetime').datetime.now().isoformat()}",
        f"# Tier: {tier}",
        "",
    ]

    for name, config in get_enabled_schedules(tier).items():
        command = config['command'].replace('python', python_path)
        lines.append(f"# {config['description']}")
        lines.append(f"{config['cron']} cd /mnt/d/Ai-Employee/AI_Employee_Vault && {command}")
        lines.append("")

    return "\n".join(lines)
