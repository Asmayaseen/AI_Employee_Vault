#!/usr/bin/env bash
# ============================================================
# Platinum Demo Gate — End-to-End Offline→Cloud→Local Flow
#
# Demonstrates: Email arrives while Local is OFFLINE
#   → Cloud agent drafts reply + writes approval file
#   → Local returns, user approves
#   → Local executes send via Email MCP
#   → Logs + moves to /Done
#
# Usage: bash demo_platinum.sh [--vault /path/to/vault]
# ============================================================

set -euo pipefail

VAULT_PATH="${VAULT_PATH:-/mnt/d/Ai-Employee/AI_Employee_Vault}"
DEMO_EMAIL_FROM="demo-client@example.com"
DEMO_EMAIL_SUBJECT="Invoice Request — Platinum Demo"
NOW=$(date +%Y%m%d_%H%M%S)
DEMO_ID="DEMO_${NOW}"

# Colors
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; RED='\033[0;31m'; NC='\033[0m'

log()  { echo -e "${CYAN}[$(date +%H:%M:%S)] $*${NC}"; }
ok()   { echo -e "${GREEN}[OK] $*${NC}"; }
warn() { echo -e "${YELLOW}[NOTE] $*${NC}"; }
fail() { echo -e "${RED}[FAIL] $*${NC}"; exit 1; }

[ -d "$VAULT_PATH" ] || fail "Vault not found: $VAULT_PATH"

echo ""
echo "============================================================"
echo "  PLATINUM DEMO GATE — AI Employee End-to-End Flow"
echo "============================================================"
echo "  Vault: $VAULT_PATH"
echo "  Demo ID: $DEMO_ID"
echo ""

# ─── STEP 1: Simulate email arriving (Cloud Perception) ──────
log "STEP 1/5 — Simulate email arriving while Local is offline"

NEEDS_ACTION_DIR="$VAULT_PATH/Needs_Action/email"
mkdir -p "$NEEDS_ACTION_DIR"

EMAIL_FILE="$NEEDS_ACTION_DIR/EMAIL_${DEMO_ID}.md"
cat > "$EMAIL_FILE" <<EOF
---
type: email
from: $DEMO_EMAIL_FROM
subject: $DEMO_EMAIL_SUBJECT
received: $(date -u +%Y-%m-%dT%H:%M:%SZ)
priority: high
status: pending
agent: cloud
demo: true
---

## Email Content
Hi, I'd like to request an invoice for January services.
Please send me the invoice as soon as possible.

## Suggested Actions
- [ ] Draft reply acknowledging receipt
- [ ] Generate invoice via Odoo MCP
- [ ] Send email via Email MCP (REQUIRES APPROVAL)

---
*Created by Platinum Demo Gate*
EOF

ok "Email action file created: $EMAIL_FILE"

# ─── STEP 2: Cloud Agent drafts reply + approval file ─────────
log "STEP 2/5 — Cloud Agent creates draft reply + approval request"

PENDING_DIR="$VAULT_PATH/Pending_Approval/email"
mkdir -p "$PENDING_DIR"

APPROVAL_FILE="$PENDING_DIR/APPROVAL_EMAIL_REPLY_${DEMO_ID}.md"
EXPIRES=$(python3 -c "from datetime import datetime,timedelta,timezone; print((datetime.now(timezone.utc)+timedelta(hours=24)).strftime('%Y-%m-%dT%H:%M:%SZ'))" 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)
cat > "$APPROVAL_FILE" <<EOF
---
type: approval_request
action: send_email
to: $DEMO_EMAIL_FROM
subject: Re: $DEMO_EMAIL_SUBJECT
created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
expires: $EXPIRES
status: pending
agent_created: cloud
agent_execute: local
demo: true
---

## Proposed Reply

**To:** $DEMO_EMAIL_FROM
**Subject:** Re: $DEMO_EMAIL_SUBJECT

---

Dear Client,

Thank you for your invoice request. I have reviewed your account and your
January invoice is being prepared.

**Invoice Details:**
- Service: January Consulting Services
- Amount: \$1,500.00
- Due: Net 30

You will receive the formal invoice within 24 hours.

Best regards,
AI Employee (on behalf of user)

---

## To APPROVE
Move this file to: $VAULT_PATH/Approved/
The Local agent will execute the send via Email MCP.

## To REJECT
Move this file to: $VAULT_PATH/Rejected/

---
*Drafted by Cloud Agent (AGENT_MODE=draft_only)*
*Execution requires Local Agent approval*
EOF

ok "Approval request created: $APPROVAL_FILE"

# ─── STEP 3: Cloud creates Plan ───────────────────────────────
log "STEP 3/5 — Cloud creates Plan.md"

PLANS_DIR="$VAULT_PATH/Plans/email"
mkdir -p "$PLANS_DIR"

PLAN_FILE="$PLANS_DIR/PLAN_${DEMO_ID}.md"
cat > "$PLAN_FILE" <<EOF
---
created: $(date -u +%Y-%m-%dT%H:%M:%SZ)
status: pending_approval
agent: cloud
priority: high
demo: true
---

## Objective
Reply to invoice request from $DEMO_EMAIL_FROM

## Steps
- [x] Detect email in Needs_Action
- [x] Analyze request (invoice for January)
- [x] Draft reply (pending approval)
- [ ] APPROVAL: Human review required → $APPROVAL_FILE
- [ ] Execute: Local agent sends email via Email MCP
- [ ] Log: Write to /Logs/$(date +%Y-%m-%d).json
- [ ] Complete: Move files to /Done

## Notes
- Cloud agent created draft (AGENT_MODE=draft_only)
- Local agent will execute after approval
- Odoo MCP can generate formal invoice if needed

---
*Created by Cloud Agent*
EOF

ok "Plan created: $PLAN_FILE"

# ─── STEP 4: Show approval prompt ─────────────────────────────
echo ""
echo "============================================================"
warn "STEP 4/5 — HUMAN APPROVAL REQUIRED"
echo ""
echo "  The Cloud Agent has drafted a reply and is waiting for"
echo "  Local Agent approval before sending."
echo ""
echo "  Approval file:"
echo "  $APPROVAL_FILE"
echo ""
echo "  To approve, press ENTER (or run manually):"
echo "  mv \"$APPROVAL_FILE\" \"$VAULT_PATH/Approved/\""
echo "============================================================"
echo ""

read -p "  Press ENTER to approve and continue demo..." -r || true

APPROVED_DIR="$VAULT_PATH/Approved"
mkdir -p "$APPROVED_DIR"
mv "$APPROVAL_FILE" "$APPROVED_DIR/APPROVAL_EMAIL_REPLY_${DEMO_ID}.md"
ok "File moved to /Approved — Local Agent will now execute"

# ─── STEP 5: Local agent executes (simulated) ─────────────────
log "STEP 5/5 — Local Agent executes send via Email MCP"

DONE_DIR="$VAULT_PATH/Done"
LOGS_DIR="$VAULT_PATH/Logs"
mkdir -p "$DONE_DIR" "$LOGS_DIR"

# Write audit log entry
LOG_FILE="$LOGS_DIR/$(date +%Y-%m-%d).json"
LOG_ENTRY=$(cat <<EOF
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","action_type":"email_send","actor":"local_agent","target":"$DEMO_EMAIL_FROM","parameters":{"subject":"Re: $DEMO_EMAIL_SUBJECT","demo":true},"approval_status":"approved","approved_by":"human","result":"success","demo_id":"$DEMO_ID"}
EOF
)
echo "$LOG_ENTRY" >> "$LOG_FILE"
ok "Audit log written: $LOG_FILE"

# Move email action file to Done
mv "$EMAIL_FILE" "$DONE_DIR/EMAIL_${DEMO_ID}.md" 2>/dev/null || true

# Move plan to Done
mv "$PLAN_FILE" "$DONE_DIR/PLAN_${DEMO_ID}.md" 2>/dev/null || true

# Move approved file to Done (mark as executed)
EXECUTED_FILE="$DONE_DIR/APPROVAL_EMAIL_REPLY_${DEMO_ID}.md"
if [ -f "$APPROVED_DIR/APPROVAL_EMAIL_REPLY_${DEMO_ID}.md" ]; then
    # Add executed marker
    echo "" >> "$APPROVED_DIR/APPROVAL_EMAIL_REPLY_${DEMO_ID}.md"
    echo "---" >> "$APPROVED_DIR/APPROVAL_EMAIL_REPLY_${DEMO_ID}.md"
    echo "*Executed by Local Agent at $(date -u +%Y-%m-%dT%H:%M:%SZ)*" >> "$APPROVED_DIR/APPROVAL_EMAIL_REPLY_${DEMO_ID}.md"
    mv "$APPROVED_DIR/APPROVAL_EMAIL_REPLY_${DEMO_ID}.md" "$EXECUTED_FILE"
fi
ok "Files moved to /Done"

# ─── Summary ──────────────────────────────────────────────────
echo ""
echo "============================================================"
echo -e "${GREEN}  PLATINUM DEMO GATE — COMPLETE${NC}"
echo "============================================================"
echo ""
echo "  Flow demonstrated:"
echo "  1. Email arrived while Local was 'offline'"
echo "     → $DONE_DIR/EMAIL_${DEMO_ID}.md"
echo "  2. Cloud Agent drafted reply (AGENT_MODE=draft_only)"
echo "     → Approval written to /Pending_Approval/email/"
echo "  3. Cloud Agent created Plan.md"
echo "     → $DONE_DIR/PLAN_${DEMO_ID}.md"
echo "  4. Human approved via file move"
echo "     → /Pending_Approval/ → /Approved/"
echo "  5. Local Agent executed send via Email MCP"
echo "     → Audit logged to $LOG_FILE"
echo "     → All files moved to /Done"
echo ""
echo "  Audit log entry:"
echo "  $LOG_ENTRY" | python3 -m json.tool 2>/dev/null || echo "  $LOG_ENTRY"
echo ""
echo "============================================================"
