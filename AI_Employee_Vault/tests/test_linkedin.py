"""
Tests for LinkedIn watcher, poster, and auto-poster.

Usage:
    python -m pytest tests/test_linkedin.py -v
    python tests/test_linkedin.py  # standalone
"""

import os
import sys
import json
import tempfile
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / 'Watchers'))


class TestLinkedInWatcher:
    """Tests for LinkedInWatcher (no browser required)."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.vault = Path(self.tmpdir)
        (self.vault / 'Needs_Action').mkdir()
        (self.vault / 'Inbox').mkdir()
        (self.vault / 'Logs').mkdir()
        os.environ['DRY_RUN'] = 'true'

    def test_init(self):
        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir, check_interval=60)
        assert watcher.vault_path == self.vault
        assert watcher.check_interval == 60
        assert watcher.session_path.exists()

    def test_lead_keywords_loaded(self):
        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir)
        assert 'pricing' in watcher.lead_keywords
        assert 'hire' in watcher.lead_keywords
        assert 'interested' in watcher.lead_keywords

    def test_load_processed_empty(self):
        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir)
        assert watcher.processed == set()

    def test_load_processed_existing(self):
        processed_file = self.vault / '.processed_linkedin'
        processed_file.write_text("MSG_John_20260216_10\nCONN_Jane_20260216")

        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir)
        assert len(watcher.processed) == 2
        assert 'MSG_John_20260216_10' in watcher.processed

    def test_save_processed_limits_to_500(self):
        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir)
        watcher.processed = {f"item_{i}" for i in range(600)}
        watcher._save_processed()

        lines = watcher.processed_file.read_text().splitlines()
        assert len(lines) == 500

    def test_create_message_action_file(self):
        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir)

        item = {
            'type': 'linkedin_message',
            'sender': 'John Doe',
            'preview': 'Interested in your services for a project',
            'is_potential_lead': True,
            'msg_id': 'MSG_John_Doe_20260216_10',
            'timestamp': datetime.now().isoformat()
        }

        filepath = watcher.create_action_file(item)
        assert filepath is not None
        assert filepath.exists()
        assert 'LINKEDIN_MSG' in filepath.name

        content = filepath.read_text()
        assert 'type: linkedin_message' in content
        assert 'John Doe' in content
        assert 'POTENTIAL LEAD' in content
        assert item['msg_id'] in watcher.processed

    def test_create_notification_action_file(self):
        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir)

        item = {
            'type': 'linkedin_notification',
            'text': 'Someone viewed your profile',
            'notif_id': 'NOTIF_12345_20260216',
            'timestamp': datetime.now().isoformat()
        }

        filepath = watcher.create_action_file(item)
        assert filepath is not None
        assert filepath.exists()
        assert 'LINKEDIN_NOTIF' in filepath.name

    def test_create_connection_action_file(self):
        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir)

        item = {
            'type': 'connection_request',
            'name': 'Jane Smith',
            'title': 'Software Engineer at Google',
            'invite_id': 'CONN_Jane_Smith_20260216',
            'timestamp': datetime.now().isoformat()
        }

        filepath = watcher.create_action_file(item)
        assert filepath is not None
        assert filepath.exists()
        assert 'LINKEDIN_CONN' in filepath.name

        content = filepath.read_text()
        assert 'Jane Smith' in content
        assert 'Software Engineer' in content

    def test_post_update_dry_run(self):
        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir)

        # requires_approval=False triggers _execute_post which checks dry_run
        result = watcher.post_update("Test post", requires_approval=False)
        assert result['status'] == 'dry_run'

    def test_post_update_creates_approval(self):
        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir)
        (self.vault / 'Pending_Approval').mkdir(exist_ok=True)

        result = watcher.post_update("Test post content", requires_approval=True)
        assert result['status'] == 'pending_approval'
        assert 'file' in result

    def test_schedule_post(self):
        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir)
        (self.vault / 'Plans').mkdir(exist_ok=True)

        post_time = datetime.now() + timedelta(hours=2)
        result = watcher.schedule_post("Future post", post_time)
        assert result['status'] == 'scheduled'

        queue = json.loads(watcher.posts_queue_file.read_text())
        assert len(queue) == 1
        assert queue[0]['content'] == 'Future post'

    def test_check_for_updates_without_playwright(self):
        """Verify graceful handling when Playwright unavailable."""
        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir)

        # Simulate playwright unavailable
        import linkedin_watcher
        original = linkedin_watcher.PLAYWRIGHT_AVAILABLE
        linkedin_watcher.PLAYWRIGHT_AVAILABLE = False

        result = watcher.check_for_updates()
        assert result == []

        linkedin_watcher.PLAYWRIGHT_AVAILABLE = original

    def test_cleanup_browser_safe_when_none(self):
        from linkedin_watcher import LinkedInWatcher
        watcher = LinkedInWatcher(vault_path=self.tmpdir)
        # Should not raise even when everything is None
        watcher._cleanup_browser()
        assert watcher._playwright is None
        assert watcher._browser is None
        assert watcher._page is None


class TestLinkedInPoster:
    """Tests for LinkedInPoster (consolidated poster)."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.vault = Path(self.tmpdir)
        for d in ['Pending_Approval', 'Approved', 'Done', 'Logs', 'Rejected']:
            (self.vault / d).mkdir()
        os.environ['DRY_RUN'] = 'true'

    def test_init(self):
        from linkedin_poster import LinkedInPoster
        poster = LinkedInPoster(vault_path=self.tmpdir)
        assert poster.vault_path == self.vault
        assert poster.dry_run is True

    def test_create_draft_post(self):
        from linkedin_poster import LinkedInPoster
        poster = LinkedInPoster(vault_path=self.tmpdir)

        filepath = poster.create_draft_post("Hello LinkedIn!")
        assert filepath.exists()
        assert 'LINKEDIN_POST' in filepath.name

        content = filepath.read_text()
        assert 'Hello LinkedIn!' in content
        assert 'type: linkedin_post' in content
        assert 'action: linkedin_post' in content
        assert 'platform: linkedin' in content

    def test_publish_post_dry_run(self):
        from linkedin_poster import LinkedInPoster
        poster = LinkedInPoster(vault_path=self.tmpdir)

        result = poster.publish_post("Test content")
        assert result['status'] == 'dry_run'

    def test_extract_content_from_code_block(self):
        from linkedin_poster import LinkedInPoster
        poster = LinkedInPoster(vault_path=self.tmpdir)

        # Create approval file with code block
        filepath = self.vault / 'Approved' / 'LINKEDIN_POST_test.md'
        filepath.write_text('''---
type: linkedin_post
---

## Post Content
```
Hello world! This is my post.
```

## Details
Some details
''')

        content = poster._extract_content(filepath)
        assert content == 'Hello world! This is my post.'

    def test_check_and_publish_approved_dry_run(self):
        from linkedin_poster import LinkedInPoster
        poster = LinkedInPoster(vault_path=self.tmpdir)

        # Create approved file
        filepath = self.vault / 'Approved' / 'LINKEDIN_POST_20260216_100000.md'
        filepath.write_text('''---
type: linkedin_post
---

## Post Content
```
Test approved post content!
```
''')

        count = poster.check_and_publish_approved()
        assert count == 1

        # Should be moved to Done
        assert not filepath.exists()
        done_files = list((self.vault / 'Done').glob('LINKEDIN_POST_*.md'))
        assert len(done_files) == 1

    def test_log_post(self):
        from linkedin_poster import LinkedInPoster
        poster = LinkedInPoster(vault_path=self.tmpdir)

        poster._log_post("Test content", "success")

        log_file = self.vault / 'Logs' / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        assert log_file.exists()
        logs = json.loads(log_file.read_text())
        assert len(logs) == 1
        assert logs[0]['action_type'] == 'linkedin_post'
        assert logs[0]['result'] == 'success'


class TestLinkedInAutoPosting:
    """Tests for LinkedIn auto-posting content generation."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.vault = Path(self.tmpdir)
        (self.vault / 'Pending_Approval').mkdir()

    def test_content_generator_init(self):
        from linkedin_auto_poster import LinkedInContentGenerator
        gen = LinkedInContentGenerator(self.vault)
        assert gen.vault_path == self.vault

    def test_generate_monday_post(self):
        from linkedin_auto_poster import LinkedInContentGenerator
        gen = LinkedInContentGenerator(self.vault)
        post = gen.generate_monday_post()
        assert post is not None
        assert len(post) > 0

    def test_generate_wednesday_post(self):
        from linkedin_auto_poster import LinkedInContentGenerator
        gen = LinkedInContentGenerator(self.vault)
        post = gen.generate_wednesday_post()
        assert post is not None
        assert len(post) > 0

    def test_generate_friday_post(self):
        from linkedin_auto_poster import LinkedInContentGenerator
        gen = LinkedInContentGenerator(self.vault)
        post = gen.generate_friday_post()
        assert post is not None
        assert '#FridayFeeling' in post

    def test_get_recent_achievements_empty(self):
        from linkedin_auto_poster import LinkedInContentGenerator
        gen = LinkedInContentGenerator(self.vault)
        achievements = gen._get_recent_achievements()
        assert achievements == []

    def test_get_recent_achievements_with_done_files(self):
        done_dir = self.vault / 'Done'
        done_dir.mkdir()
        (done_dir / 'task1.md').write_text('# Task\nCompleted the project successfully')

        from linkedin_auto_poster import LinkedInContentGenerator
        gen = LinkedInContentGenerator(self.vault)
        achievements = gen._get_recent_achievements()
        assert len(achievements) > 0

    def test_create_approval_file(self):
        from linkedin_auto_poster import create_linkedin_post_for_approval
        content = "Test post content"
        filepath = create_linkedin_post_for_approval(content, self.vault)

        assert filepath.exists()
        assert 'LINKEDIN_AUTO_POST' in filepath.name

        file_content = filepath.read_text()
        assert 'Test post content' in file_content
        assert 'type: linkedin_post' in file_content


class TestApprovalWatcherLinkedIn:
    """Tests for ApprovalWatcher LinkedIn integration."""

    def setup_method(self):
        self.tmpdir = tempfile.mkdtemp()
        self.vault = Path(self.tmpdir)
        for d in ['Pending_Approval', 'Approved', 'Done', 'Rejected',
                   'Inbox', 'Needs_Action', 'Logs']:
            (self.vault / d).mkdir()
        os.environ['DRY_RUN'] = 'true'

    def test_linkedin_post_handler_registered(self):
        from approval_watcher import ApprovalWatcher
        watcher = ApprovalWatcher(vault_path=self.tmpdir)
        assert 'linkedin_post' in watcher.action_handlers
        assert 'social_post' in watcher.action_handlers

    def test_extract_post_content_code_block(self):
        from approval_watcher import ApprovalWatcher
        watcher = ApprovalWatcher(vault_path=self.tmpdir)

        body = '''## Post Content
```
Hello LinkedIn! This is my amazing post.
```

## Details
Some details here'''

        content = watcher._extract_post_content(body)
        assert content == 'Hello LinkedIn! This is my amazing post.'

    def test_extract_post_content_generated_content_section(self):
        from approval_watcher import ApprovalWatcher
        watcher = ApprovalWatcher(vault_path=self.tmpdir)

        body = '''## Generated Content
```
Weekly update: Great progress this week!
```

## Post Details
- Day: Monday'''

        content = watcher._extract_post_content(body)
        assert 'Weekly update' in content

    def test_detect_linkedin_from_filename(self):
        """Approved file with LINKEDIN in name should route to LinkedIn handler."""
        from approval_watcher import ApprovalWatcher
        watcher = ApprovalWatcher(vault_path=self.tmpdir)

        # Create approved LinkedIn file
        filepath = self.vault / 'Approved' / 'LINKEDIN_AUTO_POST_20260216.md'
        filepath.write_text('''---
type: linkedin_post
auto_generated: true
created: 2026-02-16T09:00:00
---

## Generated Content
```
Monday motivation post!
```
''')

        items = watcher.check_for_updates()
        # Should detect the approved file
        approved_items = [i for i in items if i['type'] == 'approved']
        assert len(approved_items) >= 1


# Standalone runner
if __name__ == '__main__':
    import traceback

    test_classes = [
        TestLinkedInWatcher,
        TestLinkedInPoster,
        TestLinkedInAutoPosting,
        TestApprovalWatcherLinkedIn,
    ]
    total = 0
    passed = 0
    failed = 0

    for cls in test_classes:
        print(f"\n{'='*60}")
        print(f"  {cls.__name__}")
        print(f"{'='*60}")
        instance = cls()
        methods = sorted([m for m in dir(instance) if m.startswith('test_')])
        for method_name in methods:
            total += 1
            if hasattr(instance, 'setup_method'):
                instance.setup_method()
            try:
                getattr(instance, method_name)()
                passed += 1
                print(f"  [PASS] {method_name}")
            except Exception as e:
                failed += 1
                print(f"  [FAIL] {method_name}: {e}")
                traceback.print_exc()

    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} passed, {failed} failed")
    print(f"{'='*60}")
    sys.exit(1 if failed > 0 else 0)
