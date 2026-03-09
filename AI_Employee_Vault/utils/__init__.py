"""
AI Employee Shared Utilities.

Common helper functions used across watchers, processors, and MCP servers.
"""

from utils.vault_helpers import get_vault_path, ensure_vault_dirs, read_frontmatter
from utils.file_helpers import safe_write, atomic_move, generate_filename
from utils.config import load_config, get_env_or_fail

__all__ = [
    'get_vault_path',
    'ensure_vault_dirs',
    'read_frontmatter',
    'safe_write',
    'atomic_move',
    'generate_filename',
    'load_config',
    'get_env_or_fail',
]
