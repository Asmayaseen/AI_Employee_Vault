"""
AI Employee Web Dashboard
Runs on localhost:9000

Features:
- Real-time watcher status
- Pending actions display
- System logs viewer
- Start/Stop controls
- Activity statistics
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os
import json
import psutil
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import signal

app = Flask(__name__)
CORS(app)

# Configuration
VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))
WATCHERS_PATH = VAULT_PATH / 'Watchers'

# Track running processes
running_processes = {}


def get_watcher_status():
    """Get status of all watchers."""
    watchers = {
        'gmail': {'name': 'Gmail Watcher', 'script': 'gmail_watcher.py', 'status': 'stopped'},
        'linkedin': {'name': 'LinkedIn Watcher', 'script': 'linkedin_watcher.py', 'status': 'stopped'},
        'whatsapp': {'name': 'WhatsApp Watcher', 'script': 'whatsapp_watcher.py', 'status': 'stopped'},
        'filesystem': {'name': 'FileSystem Watcher', 'script': 'filesystem_watcher.py', 'status': 'stopped'},
        'approval': {'name': 'Approval Watcher', 'script': 'approval_watcher.py', 'status': 'stopped'}
    }

    # Check if processes are running
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline', [])
            if cmdline and 'python' in cmdline[0].lower():
                for watcher_id, watcher in watchers.items():
                    if watcher['script'] in ' '.join(cmdline):
                        watchers[watcher_id]['status'] = 'running'
                        watchers[watcher_id]['pid'] = proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    return watchers


def get_pending_actions():
    """Get pending action files."""
    needs_action = VAULT_PATH / 'Needs_Action'
    if not needs_action.exists():
        return []

    actions = []
    for file in sorted(needs_action.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            content = file.read_text(encoding='utf-8')
            lines = content.split('\n')

            # Extract metadata
            action_type = 'unknown'
            priority = 'medium'
            source = 'unknown'

            if content.startswith('---'):
                metadata_end = content.find('---', 3)
                if metadata_end > 0:
                    metadata = content[3:metadata_end]
                    for line in metadata.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            key = key.strip()
                            value = value.strip()
                            if key == 'type':
                                action_type = value
                            elif key == 'priority':
                                priority = value
                            elif key == 'source':
                                source = value

            # Get title
            title = file.stem
            for line in lines:
                if line.startswith('# '):
                    title = line[2:].strip()
                    break

            actions.append({
                'filename': file.name,
                'title': title,
                'type': action_type,
                'priority': priority,
                'source': source,
                'created': datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                'size': file.stat().st_size
            })
        except Exception as e:
            print(f"Error reading {file}: {e}")

    return actions


def get_recent_logs():
    """Get recent log entries."""
    logs_dir = VAULT_PATH / 'Logs'
    if not logs_dir.exists():
        return []

    # Get today's log file
    today = datetime.now().strftime('%Y-%m-%d')
    log_file = logs_dir / f'{today}.json'

    if not log_file.exists():
        return []

    try:
        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    log_entry = json.loads(line.strip())
                    logs.append(log_entry)
                except json.JSONDecodeError:
                    pass

        # Return last 50 entries
        return logs[-50:]
    except Exception as e:
        print(f"Error reading logs: {e}")
        return []


def get_statistics():
    """Get system statistics."""
    stats = {
        'total_actions': 0,
        'actions_by_type': {},
        'actions_by_priority': {'high': 0, 'medium': 0, 'low': 0},
        'logs_today': 0,
        'processed_emails': 0,
        'processed_linkedin': 0
    }

    # Count actions
    needs_action = VAULT_PATH / 'Needs_Action'
    if needs_action.exists():
        for file in needs_action.glob('*.md'):
            stats['total_actions'] += 1

            # Count by type
            if 'EMAIL' in file.name:
                stats['actions_by_type']['email'] = stats['actions_by_type'].get('email', 0) + 1
            elif 'LINKEDIN' in file.name:
                stats['actions_by_type']['linkedin'] = stats['actions_by_type'].get('linkedin', 0) + 1
            elif 'WHATSAPP' in file.name:
                stats['actions_by_type']['whatsapp'] = stats['actions_by_type'].get('whatsapp', 0) + 1
            elif 'FILE' in file.name:
                stats['actions_by_type']['file'] = stats['actions_by_type'].get('file', 0) + 1

    # Count processed items
    processed_emails = WATCHERS_PATH / '.processed_emails'
    if processed_emails.exists():
        stats['processed_emails'] = len(processed_emails.read_text().splitlines())

    processed_linkedin = WATCHERS_PATH / '.processed_linkedin'
    if processed_linkedin.exists():
        stats['processed_linkedin'] = len(processed_linkedin.read_text().splitlines())

    # Count today's logs
    logs = get_recent_logs()
    stats['logs_today'] = len(logs)

    return stats


@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/status')
def api_status():
    """Get system status."""
    return jsonify({
        'watchers': get_watcher_status(),
        'pending_actions': get_pending_actions(),
        'statistics': get_statistics(),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/logs')
def api_logs():
    """Get recent logs."""
    return jsonify({
        'logs': get_recent_logs(),
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/actions/<filename>')
def api_action_detail(filename):
    """Get action file content."""
    needs_action = VAULT_PATH / 'Needs_Action'
    file_path = needs_action / filename

    if not file_path.exists():
        return jsonify({'error': 'File not found'}), 404

    try:
        content = file_path.read_text(encoding='utf-8')
        return jsonify({
            'filename': filename,
            'content': content,
            'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/watcher/<watcher_id>/start', methods=['POST'])
def api_start_watcher(watcher_id):
    """Start a watcher."""
    watchers = get_watcher_status()

    if watcher_id not in watchers:
        return jsonify({'error': 'Unknown watcher'}), 404

    if watchers[watcher_id]['status'] == 'running':
        return jsonify({'error': 'Already running'}), 400

    try:
        script = watchers[watcher_id]['script']
        script_path = WATCHERS_PATH / script

        if not script_path.exists():
            return jsonify({'error': f'Script not found: {script}'}), 404

        # Start process
        process = subprocess.Popen(
            ['python', str(script_path), str(VAULT_PATH)],
            cwd=str(WATCHERS_PATH),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        running_processes[watcher_id] = process

        return jsonify({
            'status': 'started',
            'pid': process.pid,
            'watcher': watcher_id
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/watcher/<watcher_id>/stop', methods=['POST'])
def api_stop_watcher(watcher_id):
    """Stop a watcher."""
    watchers = get_watcher_status()

    if watcher_id not in watchers:
        return jsonify({'error': 'Unknown watcher'}), 404

    if watchers[watcher_id]['status'] != 'running':
        return jsonify({'error': 'Not running'}), 400

    try:
        pid = watchers[watcher_id].get('pid')
        if pid:
            os.kill(pid, signal.SIGTERM)
            return jsonify({
                'status': 'stopped',
                'watcher': watcher_id
            })
        else:
            return jsonify({'error': 'PID not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/system')
def api_system():
    """Get system information."""
    return jsonify({
        'cpu_percent': psutil.cpu_percent(interval=1),
        'memory_percent': psutil.virtual_memory().percent,
        'disk_percent': psutil.disk_usage('/').percent,
        'uptime': datetime.now().isoformat(),
        'vault_path': str(VAULT_PATH),
        'watchers_path': str(WATCHERS_PATH)
    })


if __name__ == '__main__':
    print("=" * 70)
    print("🤖 AI Employee Dashboard")
    print("=" * 70)
    print(f"\n📁 Vault Path: {VAULT_PATH}")
    print(f"🔧 Watchers Path: {WATCHERS_PATH}")
    print(f"\n🌐 Dashboard URL: http://localhost:9000")
    print("\n⚡ Starting server...")
    print("=" * 70)

    app.run(host='0.0.0.0', port=9000, debug=True)
