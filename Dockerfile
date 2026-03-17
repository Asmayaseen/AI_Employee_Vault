# AI Employee — HuggingFace Spaces / Cloud Deployment
# Runs: Flask dashboard (port 7860) + Cloud Agent orchestrator
# Mode: draft_only — creates files, never sends directly

FROM python:3.11-slim

WORKDIR /app

# System packages: supervisor (multi-process) + chromium deps for playwright
RUN apt-get update -qq && apt-get install -y -qq --no-install-recommends \
    supervisor curl \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Install Playwright + Chromium (needed for LinkedIn/WhatsApp watchers)
# Install system deps only; skip actual browser on HF (no GUI)
RUN playwright install-deps chromium 2>/dev/null || true
RUN playwright install chromium 2>/dev/null || true

# Copy application files
COPY app.py /app/app.py
COPY AI_Employee_Vault/Watchers/      /app/AI_Employee_Vault/Watchers/
COPY AI_Employee_Vault/.env.example   /app/AI_Employee_Vault/.env.example
COPY AI_Employee_Vault/zones.json     /app/AI_Employee_Vault/zones.json
COPY MCP_Servers/                     /app/MCP_Servers/

# Create full vault directory structure
RUN mkdir -p \
    /app/AI_Employee_Vault/Inbox \
    /app/AI_Employee_Vault/Needs_Action/email \
    /app/AI_Employee_Vault/Needs_Action/social \
    /app/AI_Employee_Vault/Needs_Action/accounting \
    /app/AI_Employee_Vault/Needs_Action/general \
    /app/AI_Employee_Vault/Plans/email \
    /app/AI_Employee_Vault/Plans/social \
    /app/AI_Employee_Vault/Plans/accounting \
    /app/AI_Employee_Vault/Plans/general \
    /app/AI_Employee_Vault/Pending_Approval/email \
    /app/AI_Employee_Vault/Pending_Approval/social \
    /app/AI_Employee_Vault/Pending_Approval/accounting \
    /app/AI_Employee_Vault/Pending_Approval/general \
    /app/AI_Employee_Vault/Approved \
    /app/AI_Employee_Vault/Rejected \
    /app/AI_Employee_Vault/Done \
    /app/AI_Employee_Vault/Logs/health \
    /app/AI_Employee_Vault/Briefings \
    /app/AI_Employee_Vault/Updates \
    /app/AI_Employee_Vault/Signals \
    /app/AI_Employee_Vault/In_Progress/cloud \
    /app/AI_Employee_Vault/In_Progress/local \
    /app/AI_Employee_Vault/Queued_Actions \
    /app/AI_Employee_Vault/Reports

# Supervisor config — runs dashboard + orchestrator together
RUN mkdir -p /etc/supervisor/conf.d
COPY supervisord.conf /etc/supervisor/conf.d/ai-employee.conf

# Environment
ENV VAULT_PATH=/app/AI_Employee_Vault
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV AGENT_MODE=draft_only
ENV AGENT_NAME=cloud
# DRY_RUN=false: cloud agent creates draft/approval files (never sends directly)
ENV DRY_RUN=false

EXPOSE 7860

# Supervisor runs both processes
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/ai-employee.conf"]
