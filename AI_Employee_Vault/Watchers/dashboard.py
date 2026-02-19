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
        'approval': {'name': 'Approval Watcher', 'script': 'approval_watcher.py', 'status': 'stopped'},
        'facebook': {'name': 'Facebook Watcher', 'script': 'facebook_watcher.py', 'status': 'stopped'},
        'instagram': {'name': 'Instagram Watcher', 'script': 'instagram_watcher.py', 'status': 'stopped'},
        'twitter': {'name': 'Twitter Watcher', 'script': 'twitter_watcher.py', 'status': 'stopped'}
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
        'processed_linkedin': 0,
        'processed_facebook': 0,
        'processed_instagram': 0,
        'processed_twitter': 0
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
            elif 'FACEBOOK' in file.name:
                stats['actions_by_type']['facebook'] = stats['actions_by_type'].get('facebook', 0) + 1
            elif 'INSTAGRAM' in file.name:
                stats['actions_by_type']['instagram'] = stats['actions_by_type'].get('instagram', 0) + 1
            elif 'TWITTER' in file.name:
                stats['actions_by_type']['twitter'] = stats['actions_by_type'].get('twitter', 0) + 1
            elif 'FILE' in file.name:
                stats['actions_by_type']['file'] = stats['actions_by_type'].get('file', 0) + 1

    # Count processed items
    processed_emails = WATCHERS_PATH / '.processed_emails'
    if processed_emails.exists():
        stats['processed_emails'] = len(processed_emails.read_text().splitlines())

    processed_linkedin = WATCHERS_PATH / '.processed_linkedin'
    if processed_linkedin.exists():
        stats['processed_linkedin'] = len(processed_linkedin.read_text().splitlines())

    processed_facebook = VAULT_PATH / '.processed_facebook'
    if processed_facebook.exists():
        stats['processed_facebook'] = len(processed_facebook.read_text().splitlines())

    processed_instagram = VAULT_PATH / '.processed_instagram'
    if processed_instagram.exists():
        stats['processed_instagram'] = len(processed_instagram.read_text().splitlines())

    processed_twitter = VAULT_PATH / '.processed_twitter'
    if processed_twitter.exists():
        stats['processed_twitter'] = len(processed_twitter.read_text().splitlines())

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


# ===== Approval Endpoints =====

@app.route('/api/approvals')
def api_approvals():
    """List files pending approval with content preview."""
    pending_dir = VAULT_PATH / 'Pending_Approval'
    if not pending_dir.exists():
        return jsonify({'approvals': []})

    approvals = []
    for file in sorted(pending_dir.glob('*.md'), key=lambda x: x.stat().st_mtime, reverse=True):
        try:
            content = file.read_text(encoding='utf-8')
            approvals.append({
                'filename': file.name,
                'content': content,
                'preview': content[:500],
                'created': datetime.fromtimestamp(file.stat().st_mtime).isoformat(),
                'size': file.stat().st_size
            })
        except Exception as e:
            print(f"Error reading approval file {file}: {e}")

    return jsonify({'approvals': approvals, 'timestamp': datetime.now().isoformat()})


@app.route('/api/approvals/approve', methods=['POST'])
def api_approve():
    """Move a file from Pending_Approval to Approved."""
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'filename required'}), 400

    filename = Path(data['filename']).name  # sanitize
    src = VAULT_PATH / 'Pending_Approval' / filename
    dst_dir = VAULT_PATH / 'Approved'
    dst_dir.mkdir(exist_ok=True)
    dst = dst_dir / filename

    if not src.exists():
        return jsonify({'error': 'File not found'}), 404

    try:
        import shutil
        shutil.move(str(src), str(dst))
        return jsonify({'status': 'approved', 'filename': filename, 'destination': str(dst)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/approvals/reject', methods=['POST'])
def api_reject():
    """Move a file from Pending_Approval to Rejected."""
    data = request.get_json()
    if not data or 'filename' not in data:
        return jsonify({'error': 'filename required'}), 400

    filename = Path(data['filename']).name  # sanitize
    src = VAULT_PATH / 'Pending_Approval' / filename
    dst_dir = VAULT_PATH / 'Rejected'
    dst_dir.mkdir(exist_ok=True)
    dst = dst_dir / filename

    if not src.exists():
        return jsonify({'error': 'File not found'}), 404

    try:
        import shutil
        shutil.move(str(src), str(dst))
        return jsonify({'status': 'rejected', 'filename': filename, 'destination': str(dst)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== Vault Browser Endpoints =====

ALLOWED_VAULT_FOLDERS = [
    'Inbox', 'Needs_Action', 'Plans', 'Pending_Approval',
    'Approved', 'Rejected', 'Done', 'Logs', 'Briefings',
    'Accounting', 'Queued_Actions', 'In_Progress', 'Updates', 'Signals'
]


@app.route('/api/vault/<folder>')
def api_vault_folder(folder):
    """List files in a vault folder."""
    if folder not in ALLOWED_VAULT_FOLDERS:
        return jsonify({'error': 'Folder not allowed'}), 403

    folder_path = VAULT_PATH / folder
    if not folder_path.exists():
        return jsonify({'files': [], 'folder': folder})

    files = []
    for file in sorted(folder_path.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True):
        if file.is_file():
            files.append({
                'filename': file.name,
                'size': file.stat().st_size,
                'modified': datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })

    return jsonify({'files': files, 'folder': folder, 'count': len(files)})


@app.route('/api/vault/file/<path:filepath>')
def api_vault_file(filepath):
    """Read a specific file from allowed vault folders."""
    # Sanitize: ensure the path stays within vault
    safe_path = VAULT_PATH / filepath
    try:
        safe_path = safe_path.resolve()
        vault_resolved = VAULT_PATH.resolve()
        if not str(safe_path).startswith(str(vault_resolved)):
            return jsonify({'error': 'Access denied'}), 403
    except Exception:
        return jsonify({'error': 'Invalid path'}), 400

    if not safe_path.exists() or not safe_path.is_file():
        return jsonify({'error': 'File not found'}), 404

    try:
        content = safe_path.read_text(encoding='utf-8')
        return jsonify({
            'filename': safe_path.name,
            'path': filepath,
            'content': content,
            'size': safe_path.stat().st_size,
            'modified': datetime.fromtimestamp(safe_path.stat().st_mtime).isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== Health Endpoint =====

@app.route('/api/health')
def api_health():
    """Service health check with degradation manager status."""
    health = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'services': {}
    }

    # Check watchers
    watchers = get_watcher_status()
    running_count = sum(1 for w in watchers.values() if w['status'] == 'running')
    health['services']['watchers'] = {
        'running': running_count,
        'total': len(watchers),
        'status': 'healthy' if running_count > 0 else 'degraded'
    }

    # Check vault accessibility
    health['services']['vault'] = {
        'accessible': VAULT_PATH.exists(),
        'status': 'healthy' if VAULT_PATH.exists() else 'unavailable'
    }

    # Check degradation manager state file
    degradation_state = VAULT_PATH / 'Queued_Actions' / 'degradation_state.json'
    if degradation_state.exists():
        try:
            state_data = json.loads(degradation_state.read_text(encoding='utf-8'))
            health['services']['degradation_manager'] = {
                'status': 'active',
                'services_tracked': len(state_data) if isinstance(state_data, dict) else 0
            }
        except Exception:
            health['services']['degradation_manager'] = {'status': 'unknown'}
    else:
        health['services']['degradation_manager'] = {'status': 'not_initialized'}

    # Check disk space
    disk = psutil.disk_usage('/')
    health['services']['disk'] = {
        'percent_used': disk.percent,
        'status': 'healthy' if disk.percent < 90 else 'warning'
    }

    # Overall status
    statuses = [s.get('status', 'unknown') for s in health['services'].values()]
    if 'unavailable' in statuses:
        health['status'] = 'unhealthy'
    elif 'degraded' in statuses or 'warning' in statuses:
        health['status'] = 'degraded'

    return jsonify(health)


# ===== Logs by Date Endpoint =====

@app.route('/api/logs/<date>')
def api_logs_by_date(date):
    """Get logs for a specific date (YYYY-MM-DD)."""
    logs_dir = VAULT_PATH / 'Logs'
    log_file = logs_dir / f'{date}.json'

    if not log_file.exists():
        return jsonify({'logs': [], 'date': date})

    try:
        logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    entry = json.loads(line.strip())
                    logs.append(entry)
                except json.JSONDecodeError:
                    pass

        # Filter by action_type if provided
        action_type = request.args.get('action_type')
        if action_type:
            logs = [l for l in logs if l.get('action_type') == action_type]

        return jsonify({'logs': logs, 'date': date, 'count': len(logs)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== Vault Folder Summary =====

@app.route('/api/vault/summary')
def api_vault_summary():
    """Get item counts for all vault folders."""
    summary = {}
    for folder in ALLOWED_VAULT_FOLDERS:
        folder_path = VAULT_PATH / folder
        if folder_path.exists():
            count = sum(1 for f in folder_path.iterdir() if f.is_file())
            summary[folder] = count
        else:
            summary[folder] = 0
    return jsonify({'summary': summary, 'timestamp': datetime.now().isoformat()})


# ===== Platinum Tier Endpoints =====

@app.route('/api/vault/sync/status')
def api_vault_sync_status():
    """Get vault sync status."""
    try:
        sys.path.insert(0, str(VAULT_PATH / 'utils'))
        from vault_sync import get_sync_status
        return jsonify(get_sync_status())
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'unavailable'}), 500


@app.route('/api/vault/sync/trigger', methods=['POST'])
def api_vault_sync_trigger():
    """Trigger a manual vault sync."""
    try:
        sys.path.insert(0, str(VAULT_PATH / 'utils'))
        from vault_sync import sync_vault
        result = sync_vault()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'failed'}), 500


@app.route('/api/zones/status')
def api_zones_status():
    """Get work zone status."""
    try:
        sys.path.insert(0, str(VAULT_PATH / 'utils'))
        from work_zones import get_zone_status
        return jsonify(get_zone_status())
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'unavailable'}), 500


@app.route('/api/zones/switch', methods=['POST'])
def api_zones_switch():
    """Switch active work zone."""
    data = request.get_json()
    if not data or 'zone' not in data:
        return jsonify({'error': 'zone required (local or cloud)'}), 400

    try:
        sys.path.insert(0, str(VAULT_PATH / 'utils'))
        from work_zones import set_active_zone
        result = set_active_zone(data['zone'])
        return jsonify(result)
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/zones/health')
def api_zones_health():
    """Check health of all zones."""
    try:
        sys.path.insert(0, str(VAULT_PATH / 'utils'))
        from work_zones import check_zone_health
        return jsonify({
            'local': check_zone_health('local'),
            'cloud': check_zone_health('cloud'),
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/health/detailed')
def api_health_detailed():
    """Get detailed health from health monitor."""
    try:
        sys.path.insert(0, str(VAULT_PATH / 'Watchers'))
        from health_monitor import get_health_summary, run_health_check
        refresh = request.args.get('refresh', 'false').lower() == 'true'
        if refresh:
            return jsonify(run_health_check())
        return jsonify(get_health_summary())
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'unavailable'}), 500


@app.route('/api/alerts')
def api_alerts():
    """Get recent alerts."""
    try:
        sys.path.insert(0, str(VAULT_PATH / 'utils'))
        from alert_manager import get_recent_alerts
        limit = request.args.get('limit', 50, type=int)
        return jsonify({'alerts': get_recent_alerts(limit), 'timestamp': datetime.now().isoformat()})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/claims')
def api_claims():
    """Get task claim status (Platinum multi-agent)."""
    try:
        sys.path.insert(0, str(VAULT_PATH / 'utils'))
        from claim_task import TaskClaimer
        claimer = TaskClaimer(str(VAULT_PATH))
        return jsonify({
            'all_claims': claimer.get_all_claims(),
            'available': [str(p.name) for p in claimer.list_available()],
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/platinum/status')
def api_platinum_status():
    """Get overall Platinum tier status."""
    status = {
        'tier': 'platinum',
        'timestamp': datetime.now().isoformat(),
        'modules': {}
    }

    # Vault Sync
    try:
        sys.path.insert(0, str(VAULT_PATH / 'utils'))
        from vault_sync import get_sync_status
        sync = get_sync_status()
        status['modules']['vault_sync'] = {'status': 'active', 'last_sync': sync.get('last_sync')}
    except Exception:
        status['modules']['vault_sync'] = {'status': 'unavailable'}

    # Work Zones
    try:
        from work_zones import get_zone_status
        zones = get_zone_status()
        status['modules']['work_zones'] = {'status': 'active', 'active_zone': zones.get('active_zone')}
    except Exception:
        status['modules']['work_zones'] = {'status': 'unavailable'}

    # Health Monitor
    try:
        from health_monitor import get_health_summary
        health = get_health_summary()
        status['modules']['health_monitor'] = {'status': 'active', 'healthy': health.get('overall_healthy')}
    except Exception:
        status['modules']['health_monitor'] = {'status': 'unavailable'}

    # Claim System
    try:
        from claim_task import TaskClaimer
        claimer = TaskClaimer(str(VAULT_PATH))
        claims = claimer.get_all_claims()
        status['modules']['claim_system'] = {'status': 'active', 'active_claims': sum(len(v) for v in claims.values())}
    except Exception:
        status['modules']['claim_system'] = {'status': 'unavailable'}

    # Draft-Only Mode
    agent_mode = os.getenv('AGENT_MODE', '')
    status['modules']['agent_mode'] = {'mode': agent_mode or 'full', 'draft_only': agent_mode.lower() == 'draft_only'}

    return jsonify(status)


if __name__ == '__main__':
    import sys

    print("=" * 70)
    print("AI Employee Dashboard")
    print("=" * 70)
    print(f"\n  Vault Path: {VAULT_PATH}")
    print(f"  Watchers Path: {WATCHERS_PATH}")
    print(f"\n  Dashboard URL: http://localhost:9000")
    print("\n  Starting server...")
    print("=" * 70)

    port = int(os.getenv('PORT', 9000))
    app.run(host='0.0.0.0', port=port, debug=False)
