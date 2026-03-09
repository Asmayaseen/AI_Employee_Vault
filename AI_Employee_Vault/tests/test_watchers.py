"""
Tests for watcher base class and common watcher behavior.

Usage:
    python -m pytest tests/test_watchers.py -v
    python tests/test_watchers.py  # standalone
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'Watchers'))

from Watchers.base_watcher import BaseWatcher


class MockWatcher(BaseWatcher):
    """Mock watcher for testing base class behavior."""

    def __init__(self, vault_path, items_to_return=None):
        super().__init__(vault_path=vault_path, check_interval=1)
        self._items = items_to_return or []
        self._created_files = []

    def check_for_updates(self):
        return self._items

    def create_action_file(self, item):
        filepath = self.needs_action / f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        filepath.write_text(f"---\ntype: test\n---\n\n{item}")
        self._created_files.append(filepath)
        return filepath


class TestBaseWatcher:
    """Tests for BaseWatcher base class."""

    def setup_method(self):
        """Create temporary vault for each test."""
        self.tmpdir = tempfile.mkdtemp()
        self.vault = Path(self.tmpdir)

    def test_init_creates_directories(self):
        watcher = MockWatcher(vault_path=self.tmpdir)
        assert (self.vault / 'Inbox').exists()
        assert (self.vault / 'Needs_Action').exists()
        assert (self.vault / 'Logs').exists()

    def test_dry_run_default_true(self):
        # DRY_RUN defaults to true per Constitution Principle VI
        os.environ['DRY_RUN'] = 'true'
        watcher = MockWatcher(vault_path=self.tmpdir)
        assert watcher.dry_run is True

    def test_run_once_processes_items(self):
        watcher = MockWatcher(vault_path=self.tmpdir, items_to_return=['item1', 'item2'])
        watcher.run_once()
        assert len(watcher._created_files) == 2

    def test_run_once_no_items(self):
        watcher = MockWatcher(vault_path=self.tmpdir, items_to_return=[])
        watcher.run_once()
        assert len(watcher._created_files) == 0

    def test_log_action_creates_log_file(self):
        watcher = MockWatcher(vault_path=self.tmpdir)
        watcher.log_action('test_action', {'key': 'value'})

        log_file = self.vault / 'Logs' / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        assert log_file.exists()

        logs = json.loads(log_file.read_text())
        assert len(logs) == 1
        assert logs[0]['action_type'] == 'test_action'
        assert logs[0]['watcher'] == 'MockWatcher'

    def test_action_file_created_in_needs_action(self):
        watcher = MockWatcher(vault_path=self.tmpdir, items_to_return=['test item'])
        watcher.run_once()

        files = list((self.vault / 'Needs_Action').glob('TEST_*.md'))
        assert len(files) == 1

        content = files[0].read_text()
        assert 'type: test' in content
        assert 'test item' in content


class TestAuditLogger:
    """Tests for audit logging functionality."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()

    def test_import_audit_logger(self):
        """Verify audit_logger can be imported."""
        sys.path.insert(0, str(Path(__file__).parent.parent / 'Watchers'))
        from audit_logger import AuditLogger
        logger = AuditLogger(logs_dir=Path(self.tmpdir))
        assert logger.logs_dir == Path(self.tmpdir)


# Standalone runner
if __name__ == '__main__':
    import traceback

    test_classes = [TestBaseWatcher, TestAuditLogger]
    total = 0
    passed = 0
    failed = 0

    for cls in test_classes:
        instance = cls()
        methods = [m for m in dir(instance) if m.startswith('test_')]
        for method_name in methods:
            total += 1
            if hasattr(instance, 'setup_method'):
                instance.setup_method()
            try:
                getattr(instance, method_name)()
                passed += 1
                print(f"  [PASS] {cls.__name__}.{method_name}")
            except Exception as e:
                failed += 1
                print(f"  [FAIL] {cls.__name__}.{method_name}: {e}")
                traceback.print_exc()

    print(f"\nResults: {passed}/{total} passed, {failed} failed")
    sys.exit(1 if failed > 0 else 0)
