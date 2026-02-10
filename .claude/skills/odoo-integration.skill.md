# odoo-integration

Odoo Community accounting and business management integration for the AI Employee system.

## What you do

You are the Odoo Integration Manager. You can create invoices, manage customers, track expenses, and generate financial reports using Odoo Community's accounting system.

## When to use

- When creating invoices for clients
- When adding or updating customer records
- When recording business expenses
- When generating financial summaries for CEO briefings
- When checking unpaid or overdue invoices

## Prerequisites

- Odoo Community 19+ installed and running
- Database created and configured
- API user with appropriate permissions
- Environment variables configured in `.env`

## Setup Instructions

### 1. Install Odoo Community

**Option A: Docker (Recommended)**
```bash
docker run -d -p 8069:8069 -p 8072:8072 \
  -e POSTGRES_USER=odoo \
  -e POSTGRES_PASSWORD=odoo \
  -e POSTGRES_DB=postgres \
  --name odoo \
  odoo:19
```

**Option B: Local Installation**
Follow: https://www.odoo.com/documentation/19.0/administration/install.html

### 2. Configure Environment

```bash
cd /mnt/d/Ai-Employee/MCP_Servers/odoo-mcp
cp .env.example .env
# Edit .env with your Odoo credentials
```

### 3. Test Connection

```bash
python test_connection.py
```

## Available Tools

### create_invoice
Create a new customer invoice.

```bash
# Example via Claude Code
Use odoo.create_invoice with:
- customer_name: "Acme Corp"
- invoice_lines: [{product: "Consulting", quantity: 10, unit_price: 150}]
- due_date: "2026-03-01"
```

### list_unpaid_invoices
Get unpaid or overdue invoices.

```bash
# Get overdue invoices
Use odoo.list_unpaid_invoices with:
- status: "overdue"
- limit: 10
```

### add_customer
Create or update customer records.

```bash
# Add new customer
Use odoo.add_customer with:
- name: "New Client Inc"
- email: "contact@newclient.com"
- phone: "+1-555-0123"
```

### fetch_financial_summary
Get financial summary for a period.

```bash
# Get this month's summary
Use odoo.fetch_financial_summary with:
- period: "this_month"
```

### record_expense
Record business expenses.

```bash
# Record expense
Use odoo.record_expense with:
- description: "Office Supplies"
- amount: 150.00
- category: "office"
```

## CEO Briefing Integration

The financial summary integrates with CEO Briefing Generator:

```markdown
## Financial Summary (from Odoo)

### Revenue
- Monthly Target: $10,000
- Invoiced: $8,500
- Collected: $6,200
- Outstanding: $2,300

### Expenses
- Total: $2,100
- Office: $500
- Software: $350
- Marketing: $1,250

### Profit
- Net Profit: $4,100
```

## Troubleshooting

### Connection Issues
```bash
# Check Odoo is running
curl http://localhost:8069/web/database/list

# Check credentials
python test_connection.py --verbose
```

### Permission Errors
1. Log into Odoo web interface
2. Go to Settings → Users
3. Ensure user has access to Invoicing module
4. Check company assignment

## Related Skills

- ceo-briefing.skill.md - Uses Odoo data for briefings
- approval-monitor.skill.md - Approves high-value invoices
