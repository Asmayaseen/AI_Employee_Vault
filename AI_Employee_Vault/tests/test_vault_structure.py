"""
Tests for vault folder structure validation.

Validates that all required directories and files exist
per Constitution Principle IX (Obsidian Vault as State Machine).

Usage:
    python -m pytest tests/test_vault_structure.py -v
    python tests/test_vault_structure.py  # standalone
"""

import os
import sys
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))


# Required directories per Constitution Principle IX
REQUIRED_DIRS = [
    'Inbox',
    'Needs_Action',
    'Plans',
    'Pending_Approval',
    'Approved',
    'Rejected',
    'Done',
    'Logs',
    'Briefings',
    'Accounting',
    'Queued_Actions',
]

# Required root files per Constitution
REQUIRED_FILES = [
    'Dashboard.md',
    'Company_Handbook.md',
    'Business_Goals.md',
]

# Code directories (Gold Tier)
CODE_DIRS = [
    'Watchers',
    'models',
    'utils',
    'tests',
    'scripts',
    'schedulers',
]


class TestVaultStructure:
    """Validate vault folder structure."""

    def test_vault_exists(self):
        assert VAULT_PATH.exists(), f"Vault not found at {VAULT_PATH}"

    def test_required_directories_exist(self):
        missing = []
        for dir_name in REQUIRED_DIRS:
            if not (VAULT_PATH / dir_name).exists():
                missing.append(dir_name)
        assert not missing, f"Missing required directories: {missing}"

    def test_code_directories_exist(self):
        missing = []
        for dir_name in CODE_DIRS:
            if not (VAULT_PATH / dir_name).exists():
                missing.append(dir_name)
        assert not missing, f"Missing code directories: {missing}"

    def test_watchers_directory_has_files(self):
        watchers = VAULT_PATH / 'Watchers'
        assert watchers.exists(), "Watchers directory missing"
        py_files = list(watchers.glob('*.py'))
        assert len(py_files) > 0, "No Python files in Watchers/"

    def test_required_watcher_files(self):
        watchers = VAULT_PATH / 'Watchers'
        required = [
            'base_watcher.py',
            'orchestrator.py',
            'claude_processor.py',
            'filesystem_watcher.py',
            'gmail_watcher.py',
        ]
        missing = [f for f in required if not (watchers / f).exists()]
        assert not missing, f"Missing watcher files: {missing}"

    def test_gold_tier_files(self):
        watchers = VAULT_PATH / 'Watchers'
        gold_files = [
            'audit_logger.py',
            'retry_handler.py',
            'graceful_degradation.py',
            'watchdog.py',
            'test_pipeline.py',
            'ceo_briefing_generator.py',
        ]
        missing = [f for f in gold_files if not (watchers / f).exists()]
        assert not missing, f"Missing Gold tier files: {missing}"

    def test_env_file_exists(self):
        env_file = VAULT_PATH / '.env'
        env_example = VAULT_PATH / '.env.example'
        assert env_file.exists() or env_example.exists(), \
            "Neither .env nor .env.example found"

    def test_gitignore_exists(self):
        gitignore = VAULT_PATH / '.gitignore'
        assert gitignore.exists(), ".gitignore missing from vault"

    def test_models_directory_populated(self):
        models = VAULT_PATH / 'models'
        assert models.exists(), "models/ directory missing"
        py_files = list(models.glob('*.py'))
        assert len(py_files) > 0, "No Python files in models/"

    def test_utils_directory_populated(self):
        utils = VAULT_PATH / 'utils'
        assert utils.exists(), "utils/ directory missing"
        py_files = list(utils.glob('*.py'))
        assert len(py_files) > 0, "No Python files in utils/"


# Standalone runner
if __name__ == '__main__':
    instance = TestVaultStructure()
    methods = [m for m in dir(instance) if m.startswith('test_')]

    total = 0
    passed = 0
    failed = 0

    print(f"\nValidating vault at: {VAULT_PATH}\n")

    for method_name in sorted(methods):
        total += 1
        try:
            getattr(instance, method_name)()
            passed += 1
            print(f"  [PASS] {method_name}")
        except AssertionError as e:
            failed += 1
            print(f"  [FAIL] {method_name}: {e}")
        except Exception as e:
            failed += 1
            print(f"  [ERROR] {method_name}: {e}")

    print(f"\nResults: {passed}/{total} passed, {failed} failed")
    sys.exit(1 if failed > 0 else 0)
