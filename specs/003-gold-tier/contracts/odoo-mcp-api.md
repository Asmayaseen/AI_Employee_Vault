# Contract: Odoo MCP Server API

**Feature**: 003-gold-tier
**Created**: 2026-02-09
**Type**: MCP Tool Contract
**Server**: `MCP_Servers/odoo-mcp/server.py`

## Overview

Odoo MCP server provides accounting and business management integration via Model Context Protocol. Connects to Odoo Community 19+ via XML-RPC.

## Tools

### create_invoice

**Purpose**: Create a new customer invoice in Odoo

**Input**:
```json
{
  "customer_name": "string (required)",
  "customer_email": "string (optional)",
  "invoice_lines": [
    {
      "product": "string (required)",
      "quantity": "number (required)",
      "unit_price": "number (required)",
      "description": "string (optional)"
    }
  ],
  "due_date": "string (YYYY-MM-DD, optional)",
  "notes": "string (optional)"
}
```

**Output**:
```json
{
  "success": true,
  "invoice_id": "number",
  "invoice_number": "string (e.g., INV/2026/0001)",
  "total_amount": "number",
  "status": "draft",
  "customer_id": "number"
}
```

**Errors**: `ConnectionError` (Odoo unreachable), `ValidationError` (missing fields), `AuthError` (bad credentials)

**Approval**: REQUIRED - all invoice creation routes through `/Pending_Approval/`

---

### list_unpaid_invoices

**Purpose**: List all unpaid invoices

**Input**:
```json
{
  "customer_name": "string (optional, filter by customer)",
  "due_before": "string (YYYY-MM-DD, optional)",
  "limit": "number (optional, default: 50)"
}
```

**Output**:
```json
{
  "invoices": [
    {
      "id": "number",
      "number": "string",
      "customer": "string",
      "amount_total": "number",
      "amount_due": "number",
      "due_date": "string",
      "state": "string (draft|posted)"
    }
  ],
  "total_outstanding": "number",
  "count": "number"
}
```

---

### fetch_financial_summary

**Purpose**: Get financial summary for a time period

**Input**:
```json
{
  "period": "string (this_month|last_month|this_quarter|this_year|custom)",
  "start_date": "string (YYYY-MM-DD, required if period=custom)",
  "end_date": "string (YYYY-MM-DD, required if period=custom)"
}
```

**Output**:
```json
{
  "period": { "start": "string", "end": "string" },
  "revenue": {
    "total": "number",
    "invoiced": "number",
    "paid": "number",
    "outstanding": "number"
  },
  "expenses": {
    "total": "number",
    "by_category": { "category_name": "number" }
  },
  "profit": "number",
  "invoice_count": "number",
  "customer_count": "number"
}
```

---

### add_customer

**Purpose**: Create or update customer in Odoo

**Input**:
```json
{
  "name": "string (required)",
  "email": "string (optional)",
  "phone": "string (optional)",
  "company": "string (optional)",
  "address": "string (optional)"
}
```

**Output**:
```json
{
  "success": true,
  "customer_id": "number",
  "is_new": "boolean (true if created, false if updated)"
}
```

---

### record_expense

**Purpose**: Record a business expense

**Input**:
```json
{
  "description": "string (required)",
  "amount": "number (required)",
  "category": "string (required, e.g., travel, supplies, software)",
  "date": "string (YYYY-MM-DD, optional, defaults to today)",
  "receipt_reference": "string (optional)"
}
```

**Output**:
```json
{
  "success": true,
  "expense_id": "number",
  "status": "draft"
}
```

**Approval**: REQUIRED - all expense recording routes through `/Pending_Approval/`

## Connection Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `ODOO_URL` | `http://localhost:8069` | Odoo server URL |
| `ODOO_DB` | `odoo` | Database name |
| `ODOO_USERNAME` | - | Login username |
| `ODOO_PASSWORD` | - | Login password |

## Odoo Models Used

| Model | Purpose |
|-------|---------|
| `account.move` | Invoices and credit notes |
| `account.move.line` | Invoice line items |
| `res.partner` | Customers and contacts |
| `hr.expense` | Business expenses |
| `account.account` | Chart of accounts |

## Invariants

1. All write operations (create_invoice, add_customer, record_expense) MUST be logged to audit trail
2. Invoice creation and expense recording MUST route through approval workflow
3. Read operations (list_unpaid, fetch_summary) do NOT require approval
4. Connection failures MUST be handled by retry_handler with exponential backoff
5. Odoo unavailability MUST be tracked by graceful_degradation manager
