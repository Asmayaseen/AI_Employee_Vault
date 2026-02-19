#!/bin/bash
# WhatsApp Watcher Startup Script

export DISPLAY=:0
cd /mnt/d/Ai-Employee/AI_Employee_Vault/Watchers

echo "Starting WhatsApp Watcher..."
python3 -u whatsapp_watcher.py --interval 60
