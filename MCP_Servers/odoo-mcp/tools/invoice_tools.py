"""
Invoice Tools for Odoo MCP Server (Gold Tier)

Handles invoice creation, listing, posting, and payment tracking
via Odoo JSON-RPC API with Human-in-the-Loop approval integration.
"""

import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, date, timedelta
from pathlib import Path

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from odoo_client import get_client, OdooResult
from config import config

logger = logging.getLogger('OdooInvoiceTools')

VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))


def _find_or_create_partner(client, name: str, email: str = None) -> Dict:
    """Find existing customer or create a new one."""
    domain = [('name', 'ilike', name), ('customer_rank', '>', 0)]
    result = client.search_read(
        'res.partner', domain,
        fields=['id', 'name', 'email'],
        limit=1
    )

    if result.success and result.data:
        return {'success': True, 'partner_id': result.data[0]['id'], 'is_new': False}

    # Try by email
    if email:
        result = client.search_read(
            'res.partner', [('email', '=', email)],
            fields=['id', 'name', 'email'],
            limit=1
        )
        if result.success and result.data:
            return {'success': True, 'partner_id': result.data[0]['id'], 'is_new': False}

    # Create new partner
    vals = {
        'name': name,
        'company_type': 'company',
        'customer_rank': 1
    }
    if email:
        vals['email'] = email

    create_result = client.create('res.partner', vals)
    if create_result.success:
        return {'success': True, 'partner_id': create_result.data, 'is_new': True}

    return {'success': False, 'error': create_result.error}


def _write_approval_file(invoice_data: Dict) -> str:
    """Write HITL approval file for invoice posting."""
    approval_dir = VAULT_PATH / 'Pending_Approval'
    approval_dir.mkdir(exist_ok=True)

    filename = f"INVOICE_POST_{invoice_data.get('invoice_number', 'DRAFT')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = approval_dir / filename

    total = invoice_data.get('total_amount', 0)
    customer = invoice_data.get('customer', 'Unknown')
    inv_num = invoice_data.get('invoice_number', 'DRAFT')

    content = f"""---
type: approval_request
action: post_invoice
invoice_id: {invoice_data.get('invoice_id')}
invoice_number: {inv_num}
customer: {customer}
amount: {total}
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(days=1)).isoformat()}
status: pending
---

## Invoice Posting Approval

**Invoice**: {inv_num}
**Customer**: {customer}
**Total Amount**: ${total:,.2f}
**Status**: Draft -> Ready to Post

### Line Items
"""
    for line in invoice_data.get('lines', []):
        content += f"- {line.get('product', 'Service')}: {line.get('quantity', 1)} x ${line.get('unit_price', 0):,.2f}\n"

    content += f"""
### To Approve
Move this file to `/Approved` folder.

### To Reject
Move this file to `/Rejected` folder.
"""
    filepath.write_text(content, encoding='utf-8')
    logger.info(f"Approval file created: {filepath}")
    return str(filepath)


async def create_invoice(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create a new customer invoice in Odoo (draft state).

    If the total exceeds the approval threshold, an HITL approval file
    is created in /Pending_Approval before the invoice can be posted.

    Args:
        params:
            customer_name (str): Required
            customer_email (str): Optional
            invoice_lines (list): Required - [{product, quantity, unit_price, description}]
            due_date (str): Optional YYYY-MM-DD
            notes (str): Optional

    Returns:
        Dict with invoice_id, invoice_number, total, status, approval info
    """
    client = get_client()

    customer_name = params.get('customer_name')
    customer_email = params.get('customer_email')
    invoice_lines = params.get('invoice_lines', [])
    due_date = params.get('due_date')
    notes = params.get('notes')

    if not customer_name:
        return {'success': False, 'error': 'customer_name is required'}
    if not invoice_lines:
        return {'success': False, 'error': 'At least one invoice line is required'}

    try:
        # Find or create customer
        partner_result = _find_or_create_partner(client, customer_name, customer_email)
        if not partner_result['success']:
            return partner_result

        partner_id = partner_result['partner_id']

        # Build Odoo invoice lines: (0, 0, {values})
        odoo_lines = []
        total_amount = 0.0
        line_details = []

        for line in invoice_lines:
            qty = float(line.get('quantity', 1))
            price = float(line.get('unit_price', 0))
            line_total = qty * price
            total_amount += line_total

            odoo_lines.append((0, 0, {
                'name': line.get('description') or line.get('product', 'Service'),
                'quantity': qty,
                'price_unit': price,
            }))
            line_details.append(line)

        # Invoice values
        vals = {
            'move_type': 'out_invoice',
            'partner_id': partner_id,
            'invoice_line_ids': odoo_lines,
            'company_id': config.default_company_id,
        }
        if due_date:
            vals['invoice_date_due'] = due_date
        if notes:
            vals['narration'] = notes

        # Create the invoice (draft)
        result = client.create('account.move', vals)
        if not result.success:
            return {'success': False, 'error': result.error, 'error_code': result.error_code}

        invoice_id = result.data

        # Read back details
        read_result = client.read(
            'account.move', [invoice_id],
            ['name', 'state', 'amount_total', 'invoice_date_due', 'partner_id']
        )
        inv_data = read_result.data[0] if (read_result.success and read_result.data) else {}

        response = {
            'success': True,
            'invoice_id': invoice_id,
            'invoice_number': inv_data.get('name', f'INV/{invoice_id}'),
            'total_amount': inv_data.get('amount_total', total_amount),
            'status': inv_data.get('state', 'draft'),
            'customer': customer_name,
            'due_date': due_date or 'Not set',
            'new_customer': partner_result.get('is_new', False),
            'lines': line_details,
        }

        # HITL: If amount exceeds threshold, create approval file
        if total_amount >= config.require_approval_above:
            approval_path = _write_approval_file(response)
            response['approval_required'] = True
            response['approval_file'] = approval_path
            response['message'] = (
                f"Invoice #{response['invoice_number']} created as draft. "
                f"Amount ${total_amount:,.2f} exceeds ${config.require_approval_above:,.2f} threshold. "
                "Approval required before posting."
            )
        else:
            response['approval_required'] = False
            response['message'] = f"Invoice #{response['invoice_number']} created successfully."

        logger.info(f"Created invoice {invoice_id} for {customer_name} (${total_amount:,.2f})")
        return response

    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        return {'success': False, 'error': str(e), 'error_code': 'CREATE_ERROR'}


async def get_unpaid_invoices(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get list of unpaid/overdue invoices from Odoo.

    Args:
        params:
            status (str): 'unpaid', 'overdue', or 'all' (default: 'unpaid')
            customer_id (int): Filter by partner ID
            limit (int): Max results (default: 20)

    Returns:
        Dict with list of invoices and summary
    """
    client = get_client()
    status = params.get('status', 'unpaid')
    customer_id = params.get('customer_id')
    limit = params.get('limit', 20)

    try:
        # Build domain
        domain = [('move_type', '=', 'out_invoice')]

        if status == 'unpaid':
            domain.append(('payment_state', 'in', ['not_paid', 'partial']))
        elif status == 'overdue':
            domain.append(('payment_state', 'in', ['not_paid', 'partial']))
            domain.append(('invoice_date_due', '<', date.today().isoformat()))
        # 'all' -> no extra filter

        if customer_id:
            domain.append(('partner_id', '=', customer_id))

        result = client.search_read(
            'account.move', domain,
            fields=[
                'name', 'partner_id', 'amount_total', 'amount_residual',
                'invoice_date', 'invoice_date_due', 'state', 'payment_state'
            ],
            limit=limit,
            order='invoice_date_due asc'
        )

        if not result.success:
            return {'success': False, 'error': result.error}

        invoices = []
        total_outstanding = 0.0

        for inv in result.data:
            residual = float(inv.get('amount_residual', 0))
            total_outstanding += residual

            due_date = inv.get('invoice_date_due')
            is_overdue = False
            if due_date:
                is_overdue = date.fromisoformat(str(due_date)) < date.today()

            invoices.append({
                'invoice_number': inv.get('name'),
                'customer': inv['partner_id'][1] if isinstance(inv.get('partner_id'), (list, tuple)) else str(inv.get('partner_id', '')),
                'total': float(inv.get('amount_total', 0)),
                'outstanding': residual,
                'due_date': str(due_date) if due_date else 'Not set',
                'is_overdue': is_overdue,
                'state': inv.get('state'),
                'payment_state': inv.get('payment_state'),
            })

        return {
            'success': True,
            'count': len(invoices),
            'total_outstanding': total_outstanding,
            'invoices': invoices,
            'filter': status
        }

    except Exception as e:
        logger.error(f"Error fetching invoices: {e}")
        return {'success': False, 'error': str(e), 'error_code': 'FETCH_ERROR'}


async def post_invoice(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post (confirm) a draft invoice in Odoo.

    This action is typically called after HITL approval.

    Args:
        params:
            invoice_id (int): Required - Odoo invoice ID

    Returns:
        Dict with updated invoice status
    """
    client = get_client()
    invoice_id = params.get('invoice_id')

    if not invoice_id:
        return {'success': False, 'error': 'invoice_id is required'}

    try:
        # Verify invoice exists and is in draft
        read_result = client.read(
            'account.move', [invoice_id],
            ['name', 'state', 'amount_total', 'partner_id']
        )

        if not read_result.success or not read_result.data:
            return {'success': False, 'error': f'Invoice {invoice_id} not found'}

        inv = read_result.data[0]
        if inv.get('state') != 'draft':
            return {
                'success': False,
                'error': f"Invoice {inv.get('name')} is not in draft state (current: {inv.get('state')})"
            }

        # Post the invoice using action_post
        result = client.execute('account.move', 'action_post', [invoice_id])

        if not result.success:
            return {'success': False, 'error': result.error}

        logger.info(f"Posted invoice {inv.get('name')}")
        return {
            'success': True,
            'invoice_id': invoice_id,
            'invoice_number': inv.get('name'),
            'status': 'posted',
            'amount': float(inv.get('amount_total', 0)),
            'message': f"Invoice {inv.get('name')} has been posted successfully."
        }

    except Exception as e:
        logger.error(f"Error posting invoice: {e}")
        return {'success': False, 'error': str(e), 'error_code': 'POST_ERROR'}
