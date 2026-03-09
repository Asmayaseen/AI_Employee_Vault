"""
Configuration utilities.

Centralized config loading for the AI Employee system.
Follows Constitution Principle VI: Security Boundaries.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional
from dotenv import load_dotenv


# Load .env from vault root
_vault_env = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')) / '.env'
if _vault_env.exists():
    load_dotenv(_vault_env)


def load_config() -> Dict[str, Any]:
    """
    Load full system configuration from environment.

    Returns:
        Dictionary of configuration values.
    """
    return {
        # Vault paths
        'vault_path': os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'),

        # Operation mode
        'dry_run': os.getenv('DRY_RUN', 'true').lower() == 'true',
        'debug': os.getenv('DEBUG', 'false').lower() == 'true',

        # Watcher intervals (seconds)
        'gmail_interval': int(os.getenv('GMAIL_CHECK_INTERVAL', '120')),
        'whatsapp_interval': int(os.getenv('WHATSAPP_CHECK_INTERVAL', '30')),
        'linkedin_interval': int(os.getenv('LINKEDIN_CHECK_INTERVAL', '900')),
        'filesystem_interval': int(os.getenv('FILESYSTEM_CHECK_INTERVAL', '10')),
        'approval_interval': int(os.getenv('APPROVAL_CHECK_INTERVAL', '5')),

        # Rate limits (Constitution Principle VI)
        'max_emails_per_hour': int(os.getenv('MAX_EMAILS_PER_HOUR', '10')),
        'max_payments_per_day': int(os.getenv('MAX_PAYMENTS_PER_DAY', '3')),

        # Audit (Constitution Principle III)
        'log_retention_days': int(os.getenv('LOG_RETENTION_DAYS', '90')),

        # MCP Servers
        'odoo_url': os.getenv('ODOO_URL', 'http://localhost:8069'),
        'odoo_db': os.getenv('ODOO_DB', 'odoo'),
        'odoo_username': os.getenv('ODOO_USERNAME', ''),
        'odoo_password': os.getenv('ODOO_PASSWORD', ''),

        # Dashboard
        'dashboard_port': int(os.getenv('DASHBOARD_PORT', '9000')),
    }


def get_env_or_fail(key: str, description: str = "") -> str:
    """
    Get a required environment variable or raise an error.

    Args:
        key: Environment variable name.
        description: Human-readable description for error message.

    Returns:
        The environment variable value.

    Raises:
        EnvironmentError: If the variable is not set.
    """
    value = os.getenv(key)
    if not value:
        desc = f" ({description})" if description else ""
        raise EnvironmentError(
            f"Required environment variable '{key}'{desc} is not set. "
            f"Add it to your .env file or export it."
        )
    return value
