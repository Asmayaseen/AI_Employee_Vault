# Skill: Odoo Integration (Gold Tier)

## Overview
Integrate Odoo Community Edition (self-hosted) for accounting and business operations via JSON-RPC API through a dedicated MCP server.

## Prerequisites
- Odoo 17+ running locally (Docker or native)
- PostgreSQL database configured
- MCP Server infrastructure from Silver tier

## Capabilities
- **Invoice Generation**: Create and send invoices via Odoo API
- **Payment Tracking**: Monitor incoming/outgoing payments
- **Expense Categorization**: Auto-categorize expenses from bank feeds
- **Contact Management**: Sync contacts between vault and Odoo
- **Report Generation**: Pull financial reports for CEO briefings

## Implementation Details

### MCP Server: odoo-mcp
- Location: `MCP_Servers/odoo-mcp/`
- Protocol: JSON-RPC over HTTP
- Authentication: API key + database credentials

### Tools Provided
| Tool | Description |
|------|-------------|
| `odoo_create_invoice` | Create a new invoice in Odoo |
| `odoo_list_invoices` | List invoices with filters |
| `odoo_record_payment` | Record a payment against an invoice |
| `odoo_get_balance` | Get current account balance |
| `odoo_categorize_expense` | Categorize an expense entry |

### Error Handling
- Connection failures: Queue operations locally, retry with exponential backoff
- Authentication errors: Alert user, do not retry
- Data validation: Validate all fields before API call

### Testing
- Unit tests for each MCP tool
- Integration test with Odoo test database
- E2E test: create invoice -> record payment -> verify balance

## Acceptance Criteria
- [ ] Odoo Docker container starts and is accessible
- [ ] MCP server connects to Odoo via JSON-RPC
- [ ] Invoice creation works end-to-end
- [ ] Payment recording updates balances correctly
- [ ] Errors are handled gracefully with local queuing
