# Odoo MCP Server

Model Context Protocol (MCP) server for integrating Odoo Community with the AI Employee system.

## Overview

This MCP server provides Claude Code with the ability to:
- Create and manage invoices
- Track unpaid/overdue invoices
- Manage customer records
- Get financial summaries
- Record business expenses

## Prerequisites

### Odoo Setup

1. **Install Odoo Community 19+**
   - Docker: `docker run -d -p 8069:8069 odoo:19`
   - Or install locally: https://www.odoo.com/documentation/19.0/administration/install.html

2. **Required Odoo Modules**
   - `account` (Invoicing) - Usually pre-installed
   - `contacts` (Customer management) - Usually pre-installed
   - `hr_expense` (Optional - for expense tracking)

3. **Create API User**
   - Go to Settings → Users & Companies → Users
   - Create a user with appropriate permissions
   - Note the username and password

### Environment Setup

Create a `.env` file in this directory:

```bash
# Required
ODOO_URL=http://localhost:8069
ODOO_DB=odoo
ODOO_USERNAME=admin
ODOO_PASSWORD=your_password

# Optional
ODOO_COMPANY_ID=1
ODOO_CURRENCY=USD
ODOO_APPROVAL_THRESHOLD=500
ODOO_LOG_LEVEL=INFO
```

## Installation

```bash
# Navigate to directory
cd /mnt/d/Ai-Employee/MCP_Servers/odoo-mcp

# Install dependencies
pip install -r requirements.txt

# Test connection
python test_connection.py
```

## Usage

### Test Connection

```bash
python test_connection.py
```

Expected output:
```
============================================================
     ODOO MCP SERVER - CONNECTION TEST
============================================================

  Configuration Check
  ✅ Configuration valid

  Connection Test
  ✅ Server reachable - Version: 19.0
  ✅ Authentication - User ID: 2

  Test Summary
  🎉 All tests passed! Odoo MCP server is ready.
```

### Test Individual Tools

```bash
# Test financial summary
python server.py --tool fetch_financial_summary

# Test invoice creation (dry run)
python server.py --tool create_invoice
```

### Run as MCP Server

The server runs in stdio mode for MCP integration:

```bash
python server.py
```

## Available Tools

### 1. create_invoice

Create a new customer invoice.

**Parameters:**
- `customer_name` (required): Customer name
- `customer_email`: Customer email
- `invoice_lines` (required): Array of line items
  - `product`: Product/service name
  - `quantity`: Quantity
  - `unit_price`: Price per unit
  - `description`: Line description
- `due_date`: Due date (YYYY-MM-DD)
- `notes`: Invoice notes

**Example:**
```json
{
  "customer_name": "Acme Corp",
  "customer_email": "billing@acme.com",
  "invoice_lines": [
    {
      "product": "Consulting",
      "quantity": 10,
      "unit_price": 150.00
    }
  ],
  "due_date": "2026-03-01"
}
```

### 2. list_unpaid_invoices

Get list of unpaid or overdue invoices.

**Parameters:**
- `status`: 'unpaid', 'overdue', or 'all'
- `customer_id`: Filter by customer
- `limit`: Max results (default: 50)

### 3. add_customer

Create or update customer record.

**Parameters:**
- `name` (required): Customer name
- `email`: Email address
- `phone`: Phone number
- `address`: Address object (street, city, country)
- `notes`: Internal notes
- `tags`: Array of tag names

### 4. fetch_financial_summary

Get financial summary for a period.

**Parameters:**
- `period`: 'this_month', 'last_month', 'this_quarter', 'this_year', 'custom'
- `start_date`: Start date for custom period
- `end_date`: End date for custom period

**Returns:**
- Revenue (total, invoiced, paid, outstanding)
- Expenses (total, by category)
- Profit
- Invoice/customer counts

### 5. record_expense

Record a business expense.

**Parameters:**
- `description` (required): Expense description
- `amount` (required): Amount
- `category` (required): office, travel, software, marketing, utilities, professional, equipment, meals, other
- `date`: Expense date
- `vendor`: Vendor name
- `receipt_ref`: Receipt reference
- `notes`: Additional notes

## Claude Code Integration

Add to your MCP configuration (`~/.config/claude-code/mcp.json`):

```json
{
  "servers": [
    {
      "name": "odoo",
      "command": "python",
      "args": ["/mnt/d/Ai-Employee/MCP_Servers/odoo-mcp/server.py"],
      "env": {
        "ODOO_URL": "http://localhost:8069",
        "ODOO_DB": "odoo",
        "ODOO_USERNAME": "admin",
        "ODOO_PASSWORD": "your_password"
      }
    }
  ]
}
```

## CEO Briefing Integration

The financial summary tool is designed to integrate with the CEO Briefing Generator:

```python
from tools import fetch_financial_summary

# Get this month's financial data
result = await fetch_financial_summary({'period': 'this_month'})

if result['success']:
    print(f"Revenue: ${result['revenue']['total']:,.2f}")
    print(f"Expenses: ${result['expenses']['total']:,.2f}")
    print(f"Profit: ${result['profit']:,.2f}")
```

## Troubleshooting

### Connection Failed

1. Check Odoo is running: `curl http://localhost:8069/web/database/list`
2. Verify credentials in `.env`
3. Check firewall/network access

### Authentication Failed

1. Verify username/password
2. Check user has API access
3. Try logging into Odoo web interface

### Permission Denied

1. Check user's access rights in Odoo
2. Ensure required modules are installed
3. Verify company assignment

## File Structure

```
odoo-mcp/
├── __init__.py           # Package init
├── config.py             # Configuration management
├── odoo_client.py        # XML-RPC client
├── server.py             # Main MCP server
├── tools/
│   ├── __init__.py
│   ├── invoice.py        # Invoice tools
│   ├── customer.py       # Customer tools
│   ├── financial.py      # Financial tools
│   └── expense.py        # Expense tools
├── test_connection.py    # Connection test script
├── requirements.txt      # Dependencies
└── README.md             # This file
```

## License

Part of AI Employee System - SpecifyPlus Methodology
