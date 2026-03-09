# Demo Video Script — Personal AI Employee
# Duration: 4–5 minutes | Gold Tier Submission

---

## BEFORE YOU START RECORDING

**Open these in advance:**
1. VS Code / file explorer at `/mnt/d/Ai-Employee/AI_Employee_Vault/`
2. Terminal at `/mnt/d/Ai-Employee/AI_Employee_Vault/Watchers/`
3. Browser tab: HuggingFace Space URL
4. Browser tab: LinkedIn feed (`linkedin.com/feed/`)
5. Gmail inbox (for watcher demo)

**Files to pre-stage:**
- A test file ready to drop in `/Inbox/` (e.g., `invoice_demo.md`)
- A plan file open in editor (one of the 300+ in `/Plans/`)

---

## INTRO [0:00 – 0:30]

> "Hi, I'm Muhammad Yaseen and this is my Personal AI Employee — built for the hackathon Gold Tier.
>
> The idea is simple: instead of you managing emails, WhatsApp messages, LinkedIn, and business files — your AI Employee does it. It reads everything, makes a plan, asks for your approval, and then acts.
>
> Let me show you how it works in under 5 minutes."

**Show on screen:** The `AI_Employee_Vault/` folder structure. Briefly point out the key folders: Inbox, Plans, Approved, Done.

---

## PART 1 — The Core Loop [0:30 – 1:30]

**Show:** File explorer at `AI_Employee_Vault/Plans/` — scroll through slowly.

> "First — proof this is real. These 300-plus PLAN files were generated autonomously. Every email, every WhatsApp message, every file dropped in the Inbox — the AI read it, reasoned about it, and wrote a structured action plan. No manual work."

**Open one PLAN file** (e.g., a Gmail plan). Read 2–3 lines aloud.

> "Each plan has a source, a type, a priority, and step-by-step checkboxes. The AI doesn't just detect — it thinks."

**Show:** `AI_Employee_Vault/Pending_Approval/` folder.

> "Here's the human-in-the-loop part. Before anything gets executed, it lands here. I review it, move it to Approved — and the approval watcher runs the action. That's the safety layer."

---

## PART 2 — Live Demo: File Drop [1:30 – 2:15]

**Open terminal. Open file explorer side-by-side.**

> "Let me show the system live. I'm dropping a new file into the Inbox right now."

```bash
# In terminal:
cp ~/invoice_demo.md AI_Employee_Vault/Inbox/
```

> "The file system watcher detects it — watch the Needs_Action folder."

**Wait 3–5 seconds — show the file appear in `Needs_Action/`.**

> "The Claude processor picks it up, analyzes the content, and generates a plan. That plan goes straight to Plans."

**Show the new PLAN file that appears — open it.**

> "Fully structured, with source metadata, priority, and action steps. In under 5 seconds. No human touched it."

---

## PART 3 — Watchers Overview [2:15 – 3:00]

**Show terminal. Run:**
```bash
python orchestrator.py --status
```

> "The orchestrator manages all watchers. Here you can see the full stack — Gmail, WhatsApp, LinkedIn, File System, Approval — all running."

**Then switch to showing the Watchers directory in file explorer — scroll through the .py files.**

> "31 Python scripts. Gmail watcher uses OAuth 2.0. WhatsApp uses Playwright to keep a browser session alive — completely headless. LinkedIn does the same — let me show you the live session."

**Switch to browser tab — LinkedIn feed.**

> "This is a live, authenticated LinkedIn session. The watcher monitors my feed and notifications. The auto-poster drafts content, puts it in Pending_Approval, and posts only after I approve."

---

## PART 4 — Odoo ERP + CEO Briefing [3:00 – 3:45]

**Show `MCP_Servers/odoo-mcp/` in file explorer. Open `server.py` briefly.**

> "Gold Tier adds business intelligence. Odoo 18 runs in Docker — it's our accounting layer. The Odoo MCP server gives Claude 7 tools: create invoices, fetch financial summaries, list unpaid invoices, record expenses."

**Show `docker-compose.yml` — scroll to the Odoo section.**

> "Odoo 18 plus Postgres 16, fully configured. One docker compose up and the ERP is live."

**Open a Briefing file from `/Briefings/`.**

> "Every week, the CEO Briefing Generator pulls data from Odoo, summarizes all completed tasks, flags pending approvals, and produces this report. This is what a real AI Employee delivers — not just task management, but business insight."

---

## PART 5 — HuggingFace Deployment + Known Issues [3:45 – 4:30]

**Switch to HuggingFace browser tab.**

> "The Flask dashboard is deployed live on HuggingFace. You can see real-time vault activity, plan counts, and watcher status from any browser."

**Show the dashboard briefly.**

> "Now I want to be honest about two things I couldn't verify.
>
> Twitter — my account got locked during development. The code is written, OAuth 1.0a is implemented, credentials are in the env file. Zero code changes needed once the account is restored.
>
> Meta — Facebook and Instagram require developer verification that isn't available from Pakistan. No credit card accepted, SMS loop broken. All the watcher code and token management scripts are written. One verification call away from working.
>
> Both are documented in KNOWN_ISSUES.md and JUDGES_NOTE.md in the repo. This is infrastructure — not implementation."

---

## CLOSE [4:30 – 4:45]

> "That's the Personal AI Employee — Gold Tier.
>
> Five working integrations: Gmail, WhatsApp, LinkedIn, Odoo ERP, and the file system. 31 Python scripts. 3 MCP servers. 300-plus plans generated in production. Human-in-the-loop approval on everything. Deployed on HuggingFace.
>
> The code for Twitter and Meta is also in the repo — just waiting on platform access.
>
> Thanks for watching."

**End on:** GitHub repo page or HuggingFace Space URL visible on screen.

---

## RECORDING TIPS

- **Resolution:** 1920x1080 minimum
- **Font size:** Increase terminal + editor font to 16–18pt before recording
- **Speed:** Don't rush the file drop demo — let the watcher detection be visible
- **No dead air:** If the orchestrator takes a moment, narrate what's happening
- **Trim silences** in editing before uploading

## WHAT TO RECORD WITH

- OBS Studio (free) — best for screen + mic
- Or: Windows Game Bar (Win + G) for quick capture

## UPLOAD TO

- YouTube (unlisted) → paste link in hackathon submission form
- Or Google Drive → share link

---

*Script matches project state as of 2026-03-09*
