"""
Odoo MCP Tools Package (Gold Tier)

Exports all tool handler functions for the MCP server.
Uses JSON-RPC based client and HITL approval integration.
"""

from .invoice_tools import (
    create_invoice,
    get_unpaid_invoices,
    post_invoice,
)

from .accounting_tools import (
    get_financial_summary,
    record_expense,
    get_subscription_audit,
    create_customer,
)

__all__ = [
    'create_invoice',
    'get_unpaid_invoices',
    'post_invoice',
    'get_financial_summary',
    'record_expense',
    'get_subscription_audit',
    'create_customer',
]
