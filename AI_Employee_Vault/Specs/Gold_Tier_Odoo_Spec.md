# Gold Tier: Odoo Integration Specification

**Document Version:** 1.0
**Created:** 2026-02-09
**Status:** READY FOR IMPLEMENTATION
**Priority:** P1 - HIGH

---

## 1. Overview

### 1.1 Purpose
Integrate Odoo Community (19+) with the AI Employee system to enable automated accounting, invoicing, and financial reporting capabilities.

### 1.2 Business Value
- Automated invoice creation and management
- Real-time financial data in CEO Briefings
- Customer relationship tracking
- Expense monitoring and alerts

---

## 2. Architecture

### 2.1 High-Level Integration

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         ODOO INTEGRATION ARCHITECTURE                           │
└─────────────────────────────────────────────────────────────────────────────────┘

    AI Employee                    odoo-mcp                       Odoo
    ═══════════                   ════════                       ════

    ┌─────────────┐
    │   Claude    │
    │   Code      │
    └──────┬──────┘
           │
           │ (1) Tool Call
           │     create_invoice({...})
           ▼
    ┌─────────────────────────────────────┐
    │         MCP_Servers/odoo-mcp/       │
    │                                     │
    │  ┌─────────────────────────────┐   │
    │  │     JSON-RPC Client         │   │
    │  │     (Python xmlrpc.client)  │   │
    │  └──────────────┬──────────────┘   │
    │                 │                   │
    │  ┌──────────────▼──────────────┐   │
    │  │     Tool Handlers           │   │
    │  │  - create_invoice           │   │
    │  │  - fetch_financial_summary  │   │
    │  │  - add_customer             │   │
    │  │  - list_unpaid_invoices     │   │
    │  │  - record_expense           │   │
    │  └─────────────────────────────┘   │
    └──────────────────┬──────────────────┘
                       │
                       │ (2) XML-RPC / JSON-RPC
                       ▼
    ┌─────────────────────────────────────┐
    │         Odoo Community 19+          │
    │                                     │
    │  ┌─────────────────────────────┐   │
    │  │     Models:                  │   │
    │  │  - account.move (invoices)   │   │
    │  │  - res.partner (customers)   │   │
    │  │  - account.account (GL)      │   │
    │  │  - hr.expense (expenses)     │   │
    │  └─────────────────────────────┘   │
    │                                     │
    │  Database: PostgreSQL               │
    │  Port: 8069 (default)               │
    └─────────────────────────────────────┘
```

### 2.2 File Structure

```
MCP_Servers/
└── odoo-mcp/
    ├── __init__.py
    ├── server.py              # Main MCP server
    ├── odoo_client.py         # JSON-RPC client
    ├── tools/
    │   ├── __init__.py
    │   ├── invoice.py         # Invoice operations
    │   ├── customer.py        # Customer operations
    │   ├── financial.py       # Financial summaries
    │   └── expense.py         # Expense operations
    ├── config.py              # Configuration
    ├── requirements.txt       # Dependencies
    ├── README.md              # Documentation
    └── test_connection.py     # Connection test
```

---

## 3. MCP Tools Specification

### 3.1 create_invoice

**Purpose:** Create a new invoice in Odoo

**Input Schema:**
```json
{
  "customer_name": "string (required)",
  "customer_email": "string (optional)",
  "invoice_lines": [
    {
      "product": "string",
      "quantity": "number",
      "unit_price": "number",
      "description": "string (optional)"
    }
  ],
  "due_date": "string (YYYY-MM-DD, optional)",
  "notes": "string (optional)"
}
```

**Output Schema:**
```json
{
  "success": "boolean",
  "invoice_id": "number",
  "invoice_number": "string",
  "total_amount": "number",
  "status": "string (draft|posted)",
  "pdf_url": "string (optional)"
}
```

**Example:**
```python
result = await create_invoice({
    "customer_name": "Acme Corp",
    "customer_email": "billing@acme.com",
    "invoice_lines": [
        {
            "product": "Consulting Services",
            "quantity": 10,
            "unit_price": 150.00,
            "description": "January consulting hours"
        }
    ],
    "due_date": "2026-03-01"
})
```

### 3.2 fetch_financial_summary

**Purpose:** Get financial summary for a period

**Input Schema:**
```json
{
  "period": "string (this_month|last_month|this_quarter|this_year|custom)",
  "start_date": "string (YYYY-MM-DD, required if period=custom)",
  "end_date": "string (YYYY-MM-DD, required if period=custom)"
}
```

**Output Schema:**
```json
{
  "period": {
    "start": "string",
    "end": "string"
  },
  "revenue": {
    "total": "number",
    "invoiced": "number",
    "paid": "number",
    "outstanding": "number"
  },
  "expenses": {
    "total": "number",
    "by_category": {
      "category_name": "number"
    }
  },
  "profit": "number",
  "invoice_count": "number",
  "customer_count": "number"
}
```

### 3.3 add_customer

**Purpose:** Create or update customer record

**Input Schema:**
```json
{
  "name": "string (required)",
  "email": "string (optional)",
  "phone": "string (optional)",
  "address": {
    "street": "string",
    "city": "string",
    "country": "string"
  },
  "notes": "string (optional)",
  "tags": ["string"]
}
```

**Output Schema:**
```json
{
  "success": "boolean",
  "customer_id": "number",
  "is_new": "boolean",
  "message": "string"
}
```

### 3.4 list_unpaid_invoices

**Purpose:** Get list of unpaid/overdue invoices

**Input Schema:**
```json
{
  "status": "string (unpaid|overdue|all)",
  "customer_id": "number (optional)",
  "limit": "number (default: 50)"
}
```

**Output Schema:**
```json
{
  "invoices": [
    {
      "id": "number",
      "number": "string",
      "customer": "string",
      "amount": "number",
      "due_date": "string",
      "days_overdue": "number",
      "status": "string"
    }
  ],
  "total_outstanding": "number",
  "count": "number"
}
```

### 3.5 record_expense

**Purpose:** Record a business expense

**Input Schema:**
```json
{
  "description": "string (required)",
  "amount": "number (required)",
  "category": "string (required)",
  "date": "string (YYYY-MM-DD)",
  "vendor": "string (optional)",
  "receipt_ref": "string (optional)",
  "notes": "string (optional)"
}
```

**Output Schema:**
```json
{
  "success": "boolean",
  "expense_id": "number",
  "message": "string"
}
```

---

## 4. Implementation Plan

### Phase 1: Core Setup (Day 1)
1. Create MCP server structure
2. Implement Odoo JSON-RPC client
3. Add connection testing
4. Configure environment variables

### Phase 2: Invoice Tools (Day 1-2)
1. Implement create_invoice
2. Implement list_unpaid_invoices
3. Add invoice search functionality

### Phase 3: Customer Tools (Day 2)
1. Implement add_customer
2. Add customer search/lookup

### Phase 4: Financial Tools (Day 2-3)
1. Implement fetch_financial_summary
2. Implement record_expense
3. Add expense categorization

### Phase 5: CEO Briefing Integration (Day 3)
1. Update ceo_briefing_generator.py
2. Add financial section to briefing
3. Add revenue tracking

---

## 5. Configuration

### 5.1 Environment Variables

```bash
# .env file for odoo-mcp

# Odoo Connection
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee_db
ODOO_USERNAME=admin
ODOO_PASSWORD=admin_password

# API Settings
ODOO_API_VERSION=2

# Default Settings
DEFAULT_COMPANY_ID=1
DEFAULT_CURRENCY=USD
```

### 5.2 Odoo Setup Requirements

**Minimum Odoo Configuration:**
- Odoo Community Edition 19.0+
- PostgreSQL 14+
- Modules required:
  - `account` (Invoicing)
  - `contacts` (Customer management)
  - `hr_expense` (Expense tracking)

**API Access:**
- Enable XML-RPC (default enabled)
- Create API user with appropriate permissions
- Enable web services

---

## 6. Security Considerations

### 6.1 Credential Management
- Store credentials in `.env` file
- Never commit credentials to git
- Use environment variables in production

### 6.2 Permission Model
```
Odoo User Permissions:
├── account.move: create, read, write
├── res.partner: create, read, write
├── account.account: read only
├── hr.expense: create, read
└── report: read only
```

### 6.3 Human-in-the-Loop
For sensitive operations:
- Invoices > $500 require approval
- Customer deletions require approval
- Large expenses require approval

---

## 7. Integration with Existing System

### 7.1 CEO Briefing Enhancement

**Current Briefing:**
```markdown
## Revenue
- Monthly Target: $10,000
- Current MTD: $4,500 (manual)
```

**Enhanced Briefing (with Odoo):**
```markdown
## Revenue (from Odoo)
- Monthly Target: $10,000
- Invoiced This Month: $8,500
- Paid This Month: $6,200
- Outstanding: $2,300
- Collection Rate: 73%

## Cash Flow
- Beginning Balance: $15,000
- Income: +$6,200
- Expenses: -$2,100
- Current Balance: $19,100

## Accounts Receivable
- 0-30 days: $1,500
- 31-60 days: $500
- 61-90 days: $300
- 90+ days: $0

## Top Unpaid Invoices
| Customer | Invoice | Amount | Days Overdue |
|----------|---------|--------|--------------|
| Acme Corp | INV-001 | $800 | 15 |
| Beta Inc | INV-002 | $700 | 5 |
```

### 7.2 Watcher Integration

**New capability:** Finance Watcher
- Monitor new invoices created
- Track payment status changes
- Alert on overdue invoices

---

## 8. Testing Plan

### 8.1 Unit Tests
- [ ] Connection test
- [ ] Invoice creation
- [ ] Customer creation
- [ ] Financial summary
- [ ] Expense recording

### 8.2 Integration Tests
- [ ] End-to-end invoice flow
- [ ] CEO Briefing with real data
- [ ] Approval workflow for invoices

### 8.3 Test Commands
```bash
# Test connection
python test_connection.py

# Test invoice creation
python -m pytest tests/test_invoice.py

# Test financial summary
python -m pytest tests/test_financial.py
```

---

## 9. Acceptance Criteria

### Must Have
- [ ] create_invoice working with basic fields
- [ ] fetch_financial_summary returns accurate data
- [ ] add_customer creates/updates records
- [ ] list_unpaid_invoices shows overdue items
- [ ] CEO Briefing shows Odoo data

### Should Have
- [ ] record_expense working
- [ ] Invoice PDF generation
- [ ] Customer search functionality

### Nice to Have
- [ ] Recurring invoice support
- [ ] Payment recording
- [ ] Bank reconciliation

---

## 10. Rollback Plan

If Odoo integration fails:
1. CEO Briefing falls back to manual Business_Goals.md
2. Invoice creation falls back to approval file
3. System continues without accounting automation

---

*Specification created using SpecifyPlus methodology*
