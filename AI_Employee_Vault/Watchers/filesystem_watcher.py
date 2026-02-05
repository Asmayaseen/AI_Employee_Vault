"""
File System Watcher - Monitors a drop folder for new files.

This is the simplest watcher to get started with.
Drop any file into the /Inbox folder and it will be processed.
"""

import os
import shutil
from pathlib import Path
from datetime import datetime
from base_watcher import BaseWatcher


class FileSystemWatcher(BaseWatcher):
    """
    Watches the /Inbox folder for new files.
    When files are dropped, creates action items in /Needs_Action.
    """

    def __init__(self, vault_path: str = None, check_interval: int = 10):
        super().__init__(vault_path, check_interval)
        self.processed_files = set()

        # Load already processed files
        self._load_processed()

    def _load_processed(self):
        """Load list of already processed files to avoid duplicates."""
        processed_file = self.vault_path / '.processed_files'
        if processed_file.exists():
            self.processed_files = set(processed_file.read_text().splitlines())

    def _save_processed(self):
        """Save list of processed files."""
        processed_file = self.vault_path / '.processed_files'
        processed_file.write_text('\n'.join(self.processed_files))

    def check_for_updates(self) -> list:
        """Check Inbox folder for new files."""
        new_files = []

        for item in self.inbox.iterdir():
            if item.is_file() and item.name not in self.processed_files:
                # Skip hidden files and our own files
                if not item.name.startswith('.'):
                    new_files.append(item)
                    self.logger.info(f"Found new file: {item.name}")

        return new_files

    def create_action_file(self, file_path: Path) -> Path:
        """Create an action file for the dropped file."""

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # Determine file type and suggested actions
        file_ext = file_path.suffix.lower()
        file_type = self._get_file_type(file_ext)
        suggested_actions = self._get_suggested_actions(file_type)

        # Create metadata markdown file
        content = f'''---
type: file_drop
source: inbox
original_name: {file_path.name}
file_type: {file_type}
size_bytes: {file_path.stat().st_size}
received: {datetime.now().isoformat()}
priority: medium
status: pending
---

# New File: {file_path.name}

## File Details
- **Name:** {file_path.name}
- **Type:** {file_type}
- **Size:** {self._format_size(file_path.stat().st_size)}
- **Received:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Original Location
`{file_path.absolute()}`

## Suggested Actions
{suggested_actions}

## Notes
> Add any notes about this file here

---
*Created by FileSystemWatcher*
'''

        # Create action file
        action_filename = f"FILE_{timestamp}_{file_path.stem}.md"
        action_path = self.needs_action / action_filename
        action_path.write_text(content)

        # Mark as processed
        self.processed_files.add(file_path.name)
        self._save_processed()

        # Log the action
        self.log_action("file_received", {
            "filename": file_path.name,
            "file_type": file_type,
            "size": file_path.stat().st_size,
            "action_file": str(action_path)
        })

        return action_path

    def _get_file_type(self, ext: str) -> str:
        """Determine file type from extension."""
        type_map = {
            '.pdf': 'document',
            '.doc': 'document', '.docx': 'document',
            '.xls': 'spreadsheet', '.xlsx': 'spreadsheet',
            '.csv': 'data',
            '.jpg': 'image', '.jpeg': 'image', '.png': 'image', '.gif': 'image',
            '.mp3': 'audio', '.wav': 'audio',
            '.mp4': 'video', '.mov': 'video',
            '.txt': 'text',
            '.md': 'markdown',
            '.json': 'data',
            '.zip': 'archive', '.rar': 'archive',
        }
        return type_map.get(ext, 'unknown')

    def _get_suggested_actions(self, file_type: str) -> str:
        """Get suggested actions based on file type."""
        actions = {
            'document': '''- [ ] Review document content
- [ ] Extract key information
- [ ] File in appropriate folder
- [ ] Share with relevant party if needed''',

            'spreadsheet': '''- [ ] Review data
- [ ] Validate numbers
- [ ] Import to accounting if financial
- [ ] Create summary''',

            'data': '''- [ ] Parse and validate data
- [ ] Import to relevant system
- [ ] Create backup''',

            'image': '''- [ ] Review image
- [ ] Categorize (receipt, document, photo)
- [ ] Extract text if applicable (OCR)
- [ ] File appropriately''',

            'text': '''- [ ] Read content
- [ ] Determine purpose
- [ ] Take appropriate action''',

            'archive': '''- [ ] Extract contents
- [ ] Review files
- [ ] Process individual items''',
        }
        return actions.get(file_type, '''- [ ] Review file
- [ ] Determine appropriate action
- [ ] Process accordingly''')

    def _format_size(self, size_bytes: int) -> str:
        """Format file size for display."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"


if __name__ == "__main__":
    import sys

    # Get vault path from environment or argument
    vault_path = sys.argv[1] if len(sys.argv) > 1 else os.getenv('VAULT_PATH')

    if not vault_path:
        vault_path = Path(__file__).parent.parent

    print(f"Starting FileSystemWatcher...")
    print(f"Vault: {vault_path}")
    print(f"Drop files in: {Path(vault_path) / 'Inbox'}")
    print("Press Ctrl+C to stop\n")

    watcher = FileSystemWatcher(vault_path=str(vault_path))
    watcher.run()
