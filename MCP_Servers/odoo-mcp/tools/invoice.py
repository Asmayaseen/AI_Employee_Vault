"""
Invoice Tools for Odoo MCP

Handles invoice creation and management in Odoo.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from dataclasses import dataclass, asdict

import sys
sys.path.append('..')
from odoo_client import get_client, OdooResult
from config import config

logger = logging.getLogger('OdooInvoice')


@dataclass
class InvoiceLine:
    """Invoice line item."""
    product: str
    quantity: float
    unit_price: float
    description: Optional[str] = None


@dataclass
class InvoiceRequest:
    """Invoice creation request."""
    customer_name: str
    customer_email: Optional[str] = None
    invoice_lines: List[Dict] = None
    due_date: Optional[str] = None
    notes: Optional[str] = None


async def create_invoice(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new invoice in Odoo.

    Args:
        params: Invoice parameters
            - customer_name (str): Customer name (required)
            - customer_email (str): Customer email (optional)
            - invoice_lines (list): List of line items
            - due_date (str): Due date YYYY-MM-DD (optional)
            - notes (str): Invoice notes (optional)

    Returns:
        Dict with invoice details or error
    """
    client = get_client()

    try:
        # Extract parameters
        customer_name = params.get('customer_name')
        customer_email = params.get('customer_email')
        invoice_lines = params.get('invoice_lines', [])
        due_date = params.get('due_date')
        notes = params.get('notes')

        if not customer_name:
            return {
                'success': False,
                'error': 'customer_name is required'
            }

        if not invoice_lines:
            return {
                'success': False,
                'error': 'At least one invoice line is required'
            }

        # Find or create customer
        customer_result = await _find_or_create_customer(
            client, customer_name, customer_email
        )
        if not customer_result['success']:
            return customer_result

        partner_id = customer_result['partner_id']

        # Prepare invoice lines
        odoo_lines = []
        total_amount = 0.0

        for line in invoice_lines:
            quantity = float(line.get('quantity', 1))
            unit_price = float(line.get('unit_price', 0))
            line_total = quantity * unit_price
            total_amount += line_total

            odoo_lines.append((0, 0, {
                'name': line.get('description') or line.get('product', 'Service'),
                'quantity': quantity,
                'price_unit': unit_price,
            }))

        # Prepare invoice values
        invoice_vals = {
            'move_type': 'out_invoice',  # Customer invoice
            'partner_id': partner_id,
            'invoice_line_ids': odoo_lines,
            'company_id': config.default_company_id,
        }

        # Add due date if provided
        if due_date:
            invoice_vals['invoice_date_due'] = due_date

        # Add notes if provided
        if notes:
            invoice_vals['narration'] = notes

        # Create invoice
        result = client.create('account.move', invoice_vals)

        if not result.success:
            return {
                'success': False,
                'error': result.error,
                'error_code': result.error_code
            }

        invoice_id = result.data

        # Read back invoice details
        read_result = client.read(
            'account.move',
            [invoice_id],
            ['name', 'state', 'amount_total', 'invoice_date_due']
        )

        invoice_data = read_result.data[0] if read_result.success else {}

        logger.info(f"Created invoice {invoice_id} for {customer_name}")

        return {
            'success': True,
            'invoice_id': invoice_id,
            'invoice_number': invoice_data.get('name', f'INV/{invoice_id}'),
            'total_amount': invoice_data.get('amount_total', total_amount),
            'status': invoice_data.get('state', 'draft'),
            'customer': customer_name,
            'due_date': due_date or 'Not set'
        }

    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        return {
            'success': False,
            'error': str(e),
            'error_code': 'CREATE_ERROR'
        }


async def _find_or_create_customer(client, name: str, email: str = None) -> Dict:
    """Find existing customer or create new one."""
    # Search for existing customer
    domain = [('name', '=', name)]
    if email:
        domain = ['|', ('name', '=', name), ('email', '=', email)]

    search_result = client.search_read(
        'res.partner',
        domain,
        fields=['id', 'name', 'email'],
        limit=1
    )

    if search_result.success and search_result.data:
        # Customer exists
        return {
            'success': True,
            'partner_id': search_result.data[0]['id'],
            'is_new': False
        }

    # Create new customer
    partner_vals = {
        'name': name,
        'company_type': 'company',
        'customer_rank': 1
    }
    if email:
        partner_vals['email'] = email

    create_result = client.create('res.partner', partner_vals)

    if create_result.success:
        return {
            'success': True,
            'partner_id': create_result.data,
            'is_new': True
        }
    else:
        return {
            'success': False,
            'error': create_result.error
        }


async def list_unpaid_invoices(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List unpaid or overdue invoices.

    Args:
        params: Query parameters
            - status (str): 'unpaid', 'overdue', or 'all'
            - customer_id (int): Filter by customer (optional)
            - limit (int): Max results (default: 50)

    Returns:
        Dict with list of invoices
    """
    client = get_client()

    try:
        status = params.get('status', 'unpaid')
        customer_id = params.get('customer_id')
        limit = params.get('limit', 50)

        # Build domain
        domain = [
            ('move_type', '=', 'out_invoice'),
            ('state', '=', 'posted'),
            ('payment_state', 'in', ['not_paid', 'partial'])
        ]

        if status == 'overdue':
            today = date.today().isoformat()
            domain.append(('invoice_date_due', '<', today))

        if customer_id:
            domain.append(('partner_id', '=', customer_id))

        # Search invoices
        result = client.search_read(
            'account.move',
            domain,
            fields=[
                'name', 'partner_id', 'amount_total', 'amount_residual',
                'invoice_date_due', 'state', 'payment_state'
            ],
            limit=limit,
            order='invoice_date_due asc'
        )

        if not result.success:
            return {
                'success': False,
                'error': result.error
            }

        # Process results
        invoices = []
        total_outstanding = 0.0
        today = date.today()

        for inv in result.data:
            due_date = inv.get('invoice_date_due')
            days_overdue = 0

            if due_date:
                due = datetime.strptime(due_date, '%Y-%m-%d').date()
                days_overdue = (today - due).days if today > due else 0

            amount = inv.get('amount_residual', inv.get('amount_total', 0))
            total_outstanding += amount

            invoices.append({
                'id': inv['id'],
                'number': inv.get('name', ''),
                'customer': inv.get('partner_id', [0, 'Unknown'])[1],
                'amount': amount,
                'due_date': due_date,
                'days_overdue': days_overdue,
                'status': 'overdue' if days_overdue > 0 else 'unpaid'
            })

        logger.info(f"Found {len(invoices)} unpaid invoices")

        return {
            'success': True,
            'invoices': invoices,
            'total_outstanding': total_outstanding,
            'count': len(invoices)
        }

    except Exception as e:
        logger.error(f"Error listing invoices: {e}")
        return {
            'success': False,
            'error': str(e),
            'error_code': 'LIST_ERROR'
        }
