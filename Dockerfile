# AI Employee - HuggingFace Spaces Deployment
# Simple Flask API (Cloud/draft-only mode)

FROM python:3.11-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copy only what's needed
COPY app.py /app/app.py
COPY AI_Employee_Vault/Watchers/ /app/AI_Employee_Vault/Watchers/
COPY AI_Employee_Vault/.env.example /app/AI_Employee_Vault/.env.example
COPY MCP_Servers/ /app/MCP_Servers/

# Create vault directories
RUN mkdir -p \
    /app/AI_Employee_Vault/Needs_Action/email \
    /app/AI_Employee_Vault/Needs_Action/social \
    /app/AI_Employee_Vault/Pending_Approval/email \
    /app/AI_Employee_Vault/Pending_Approval/social \
    /app/AI_Employee_Vault/Approved \
    /app/AI_Employee_Vault/Done \
    /app/AI_Employee_Vault/Logs \
    /app/AI_Employee_Vault/In_Progress/cloud \
    /app/AI_Employee_Vault/In_Progress/local

ENV VAULT_PATH=/app/AI_Employee_Vault
ENV PYTHONUNBUFFERED=1
ENV PORT=7860
ENV AGENT_MODE=draft_only
ENV AGENT_NAME=cloud
# DRY_RUN=false so cloud agent CAN create approval/draft files
# AGENT_MODE=draft_only ensures no direct sends/posts
ENV DRY_RUN=false

EXPOSE 7860

CMD ["python", "/app/app.py"]
