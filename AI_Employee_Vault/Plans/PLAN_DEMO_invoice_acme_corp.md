---
created: 2026-02-10T09:20:00Z
source_task: DEMO_EMAIL_acme_invoice_request.md
status: pending_approval
actor: claude_code
---

## Plan: Generate Invoice for Acme Corp

### Objective
Process client invoice request from Sarah Chen (Acme Corp) for January consulting work.

### Analysis
- Client: Acme Corp (existing customer in Odoo)
- Amount: $2,250.00 (exceeds $500 approval threshold)
- Line Items:
  - AI Strategy Consulting: 10 hrs x $150/hr = $1,500
  - Implementation Support: 5 hrs x $150/hr = $750
- PO Reference: PO-2026-0142
- Terms: Net 30
- Send to: billing@acmecorp.com

### Steps
- [x] Read and parse email request
- [x] Identify client: Acme Corp (existing in Odoo)
- [x] Calculate total: $2,250.00
- [x] Determine: Amount > $500 threshold -> HITL required
- [ ] Create draft invoice in Odoo via `create_invoice` MCP tool
- [ ] Generate approval request (amount exceeds threshold)
- [ ] Wait for human approval
- [ ] Post invoice via `post_invoice` MCP tool
- [ ] Send invoice via email MCP (second approval needed)
- [ ] Log completed transaction
- [ ] Move files to /Done

### Approval Required
Invoice amount $2,250.00 exceeds the $500 approval threshold.
See: `/Pending_Approval/DEMO_APPROVAL_INVOICE_ACME_2250.md`

### MCP Tools Required
1. `odoo.create_invoice` - Create draft in Odoo
2. `odoo.post_invoice` - Confirm after approval
3. `email.send_email` - Send to client after second approval
