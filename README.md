# 🤖 AI Employee - Personal Autonomous FTE

[![Tier](https://img.shields.io/badge/Tier-Silver%20Complete-blue)](AI_Employee_Vault/SILVER_TIER_SETUP_GUIDE.md)
[![Status](https://img.shields.io/badge/Status-Ready%20for%20Setup-green)](AI_Employee_Vault/Dashboard.md)
[![Python](https://img.shields.io/badge/Python-3.13+-blue)](https://python.org)

> **Your life and business on autopilot.** A local-first, agent-driven, human-in-the-loop autonomous AI employee that manages personal and business affairs 24/7.

---

## 🌟 What is This?

This is a **Personal AI Employee** (Digital FTE) built using Claude Code and Obsidian. It proactively manages:

- **Personal Affairs:** Gmail, WhatsApp, file monitoring
- **Business Operations:** LinkedIn auto-posting, client management, scheduling
- **Intelligent Processing:** Autonomous reasoning with Plan.md generation
- **Safety First:** Human-in-the-loop approval for sensitive actions

---

## ✨ Silver Tier Complete

### 🔔 Watchers (4 Total)
- ✅ Gmail Watcher - Monitors emails
- ✅ WhatsApp Watcher - Tracks messages
- ✅ LinkedIn Watcher - Messages + auto-posting
- ✅ FileSystem Watcher - Monitors Inbox

### 🧠 Intelligence
- ✅ Claude Processor with Plan.md generation
- ✅ Reasoning loop for complex tasks
- ✅ Daily briefings

### 🤝 Safety
- ✅ Approval workflow (HITL)
- ✅ Audit logging
- ✅ Rate limiting
- ✅ Dry-run mode

### 🔧 Integration
- ✅ Email MCP Server
- ✅ Orchestrator
- ✅ Scheduler

---

## 🚀 Quick Start

```bash
# Navigate to watchers directory
cd AI_Employee_Vault/Watchers

# Run quick start script
./quick_start.sh

# OR manually install
pip install -r requirements.txt
playwright install chromium
python orchestrator.py
```

**📖 Full Setup Guide:** [`SILVER_TIER_SETUP_GUIDE.md`](AI_Employee_Vault/SILVER_TIER_SETUP_GUIDE.md)

---

## 📁 Key Files

| File | Description |
|------|-------------|
| [`SILVER_TIER_SETUP_GUIDE.md`](AI_Employee_Vault/SILVER_TIER_SETUP_GUIDE.md) | Complete setup instructions |
| [`Dashboard.md`](AI_Employee_Vault/Dashboard.md) | Real-time system status |
| [`0-hackathon.md`](0-hackathon.md) | Hackathon specification |
| [`.specify/memory/constitution.md`](.specify/memory/constitution.md) | System principles |

---

## 🎯 How It Works

1. **Watchers** detect events (email, WhatsApp, files)
2. **Claude Processor** creates Plan.md with action steps
3. **Approval workflow** for sensitive actions
4. **MCP servers** execute approved actions
5. **Everything logged** to audit trail

**Architecture Diagram:** See [`SILVER_TIER_SETUP_GUIDE.md`](AI_Employee_Vault/SILVER_TIER_SETUP_GUIDE.md)

---

## 🎓 Usage

### Process Pending Items
```bash
cd AI_Employee_Vault/Watchers
python claude_processor.py --process-all
```

### Generate Daily Briefing
```bash
python claude_processor.py --briefing
```

### Start All Watchers
```bash
python orchestrator.py
```

### Run with PM2 (Always-On)
```bash
pm2 start orchestrator.py --name "ai-employee" --interpreter python3
pm2 save
```

---

## 🏆 Tier Progress

- ✅ **Bronze Tier** - Foundation complete
- ✅ **Silver Tier** - Functional Assistant complete
- 🔜 **Gold Tier** - Autonomous Employee (Odoo, Social Media, CEO Briefing)
- 🚀 **Platinum Tier** - 24/7 Cloud deployment

---

## 📚 Resources

- **Weekly Meeting:** Wednesdays 10:00 PM - [Zoom Link](https://us06web.zoom.us/j/87188707642?pwd=a9XloCsinvn1JzICbPc2YGUvWTbOTr.1)
- **Hackathon Guide:** [`0-hackathon.md`](0-hackathon.md)
- **Claude Code:** https://claude.com/claude-code
- **MCP Protocol:** https://modelcontextprotocol.io

---

**Status:** Silver Tier Complete - Ready for Setup 🎉

**Last Updated:** 2026-02-07
