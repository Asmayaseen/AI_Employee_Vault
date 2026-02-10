"""
Odoo MCP Server Configuration

This module handles configuration for the Odoo MCP server.
All sensitive values are loaded from environment variables.
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class OdooConfig:
    """Configuration for Odoo connection."""

    # Connection settings
    url: str = os.getenv('ODOO_URL', 'http://localhost:8069')
    database: str = os.getenv('ODOO_DB', 'odoo')
    username: str = os.getenv('ODOO_USERNAME', 'admin')
    password: str = os.getenv('ODOO_PASSWORD', '')

    # API settings
    api_version: int = int(os.getenv('ODOO_API_VERSION', '2'))
    timeout: int = int(os.getenv('ODOO_TIMEOUT', '30'))

    # Default values
    default_company_id: int = int(os.getenv('ODOO_COMPANY_ID', '1'))
    default_currency: str = os.getenv('ODOO_CURRENCY', 'USD')

    # Feature flags
    require_approval_above: float = float(os.getenv('ODOO_APPROVAL_THRESHOLD', '500'))

    def validate(self) -> tuple[bool, str]:
        """Validate configuration."""
        if not self.url:
            return False, "ODOO_URL is required"
        if not self.database:
            return False, "ODOO_DB is required"
        if not self.username:
            return False, "ODOO_USERNAME is required"
        if not self.password:
            return False, "ODOO_PASSWORD is required"
        return True, "Configuration valid"

    @property
    def jsonrpc_url(self) -> str:
        """Get JSON-RPC endpoint URL (Odoo 17+/19+)."""
        return f"{self.url}/jsonrpc"

    @property
    def web_session_url(self) -> str:
        """Get web session endpoint URL."""
        return f"{self.url}/web/session/authenticate"


# Global configuration instance
config = OdooConfig()


# MCP Server settings
MCP_SERVER_NAME = "odoo-mcp"
MCP_SERVER_VERSION = "1.0.0"
MCP_SERVER_DESCRIPTION = "Odoo Community integration for AI Employee"

# Logging
LOG_LEVEL = os.getenv('ODOO_LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('ODOO_LOG_FILE', '/mnt/d/Ai-Employee/AI_Employee_Vault/Logs/odoo_mcp.log')
