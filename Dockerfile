# Multi-stage Dockerfile for AI Employee System
# Stage 1: Build Next.js frontend
# Stage 2: Python backend + serve frontend

# ---- Stage 1: Build Frontend ----
FROM node:20-alpine AS frontend-builder

WORKDIR /app/web-ui
COPY AI_Employee_Vault/web-ui/package.json AI_Employee_Vault/web-ui/package-lock.json* ./
RUN npm ci
COPY AI_Employee_Vault/web-ui/ ./
RUN npm run build

# ---- Stage 2: Python Backend + Frontend ----
FROM python:3.11-slim

WORKDIR /app

# Install Node.js for serving Next.js
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY AI_Employee_Vault/Watchers/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy vault structure
COPY AI_Employee_Vault/ /app/AI_Employee_Vault/

# Copy built frontend
COPY --from=frontend-builder /app/web-ui/.next /app/AI_Employee_Vault/web-ui/.next
COPY --from=frontend-builder /app/web-ui/node_modules /app/AI_Employee_Vault/web-ui/node_modules
COPY --from=frontend-builder /app/web-ui/package.json /app/AI_Employee_Vault/web-ui/package.json
COPY --from=frontend-builder /app/web-ui/public /app/AI_Employee_Vault/web-ui/public

# Copy MCP servers
COPY MCP_Servers/ /app/MCP_Servers/

# Environment
ENV VAULT_PATH=/app/AI_Employee_Vault
ENV LOG_PATH=/app/AI_Employee_Vault/Logs
ENV PYTHONUNBUFFERED=1
# HuggingFace Spaces uses port 7860
ENV PORT=7860
ENV AGENT_MODE=draft_only
ENV AGENT_NAME=cloud
ENV DRY_RUN=true

# Create required vault directories
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

# HuggingFace Spaces port
EXPOSE 7860

# Default: start dashboard
CMD ["python", "/app/AI_Employee_Vault/Watchers/dashboard.py"]
