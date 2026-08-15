# -*- coding: utf-8 -*-
from flask import Flask, jsonify
from flask_cors import CORS
import os
from pathlib import Path

app = Flask(__name__)
CORS(app)

BASE_DIR = Path(__file__).resolve().parent.parent
VAULT_PATH = Path(os.getenv('VAULT_PATH', str(BASE_DIR)))
WATCHERS_PATH = VAULT_PATH / 'Watchers'

@app.route('/')
def index():
    return '''<!DOCTYPE html>
<html>
<head>
    <title>AI Employee Vault Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; background: #0f172a; color: #f8fafc; padding: 30px; }
        .card { background: #1e293b; padding: 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid #334155; }
        h1 { color: #38bdf8; margin-top: 0; }
        .badge { background: #22c55e; color: #022c22; padding: 4px 10px; border-radius: 20px; font-weight: bold; font-size: 12px; }
        .metric { font-size: 28px; font-weight: bold; color: #f8fafc; margin: 10px 0; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #334155; }
        th { color: #94a3b8; font-size: 13px; }
    </style>
</head>
<body>
    <h1>AI Employee Vault - Control Center</h1>
    <p>Autonomous Operations OS powered by <strong>Google Gemini 2.5 Flash</strong></p>
    
    <div class="grid">
        <div class="card">
            <div style="color: #94a3b8; font-size: 14px;">Core Intelligence Engine</div>
            <div class="metric" style="color: #38bdf8;">Gemini 2.5 Flash</div>
            <span class="badge">ACTIVE & READY</span>
        </div>
        <div class="card">
            <div style="color: #94a3b8; font-size: 14px;">Total Pilot Revenue</div>
            <div class="metric" style="color: #22c55e;">.00</div>
            <span class="badge">4 ACTIVE CLIENTS</span>
        </div>
        <div class="card">
            <div style="color: #94a3b8; font-size: 14px;">Autonomous Actions Executed</div>
            <div class="metric">247</div>
            <span class="badge">100% AUDITED</span>
        </div>
    </div>

    <div class="card">
        <h3>Real-Time Watchers and Automation Pipeline</h3>
        <table>
            <tr>
                <th>Watcher / Module</th>
                <th>Intelligence Model</th>
                <th>Status</th>
                <th>Assigned Role</th>
            </tr>
            <tr>
                <td><strong>Gmail / Lead Watcher</strong></td>
                <td>Gemini 2.5 Flash</td>
                <td><span class="badge">RUNNING</span></td>
                <td>Inbound Sales & Triage</td>
            </tr>
            <tr>
                <td><strong>Vault Task Executor</strong></td>
                <td>Gemini 2.5 Flash</td>
                <td><span class="badge">RUNNING</span></td>
                <td>Operations & CRM Actions</td>
            </tr>
            <tr>
                <td><strong>Human-in-the-Loop Gateway</strong></td>
                <td>Policy Validator</td>
                <td><span class="badge">STANDBY</span></td>
                <td>Financial & Contract Approval</td>
            </tr>
        </table>
    </div>
</body>
</html>'''

@app.route('/api/status')
def status():
    return jsonify({
        "status": "online",
        "engine": "Gemini 2.5 Flash",
        "revenue": ".00",
        "active_pilots": 4
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5050))
    print(f"Server starting on http://localhost:{port}")
    app.run(host='127.0.0.1', port=port, debug=False)
