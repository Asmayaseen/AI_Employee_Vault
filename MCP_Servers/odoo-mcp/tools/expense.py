"""
Expense Tools for Odoo MCP

Handles expense recording and management in Odoo.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date

import sys
sys.path.append('..')
from odoo_client import get_client, OdooResult
from config import config

logger = logging.getLogger('OdooExpense')


# Default expense categories
DEFAULT_CATEGORIES = {
    'office': 'Office Supplies',
    'travel': 'Travel & Transportation',
    'software': 'Software & Subscriptions',
    'marketing': 'Marketing & Advertising',
    'utilities': 'Utilities',
    'professional': 'Professional Services',
    'equipment': 'Equipment',
    'meals': 'Meals & Entertainment',
    'other': 'Other Expenses'
}


async def record_expense(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Record a business expense in Odoo.

    Args:
        params: Expense parameters
            - description (str): Expense description (required)
            - amount (float): Expense amount (required)
            - category (str): Expense category (required)
            - date (str): Expense date YYYY-MM-DD (optional, defaults to today)
            - vendor (str): Vendor name (optional)
            - receipt_ref (str): Receipt reference number (optional)
            - notes (str): Additional notes (optional)

    Returns:
        Dict with expense details or error
    """
    client = get_client()

    try:
        description = params.get('description')
        amount = params.get('amount')
        category = params.get('category', 'other')
        expense_date = params.get('date', date.today().isoformat())
        vendor = params.get('vendor')
        receipt_ref = params.get('receipt_ref')
        notes = params.get('notes')

        # Validate required fields
        if not description:
            return {
                'success': False,
                'error': 'description is required'
            }

        if amount is None or amount <= 0:
            return {
                'success': False,
                'error': 'amount must be a positive number'
            }

        # Check if amount requires approval
        requires_approval = float(amount) >= config.require_approval_above

        # Get or create expense product
        product_id = await _get_expense_product(client, category)

        # Get employee (default to admin user's employee)
        employee_id = await _get_default_employee(client)

        if not employee_id:
            # Try creating expense as vendor bill instead
            return await _create_as_vendor_bill(
                client, description, amount, category,
                expense_date, vendor, notes
            )

        # Prepare expense values
        expense_vals = {
            'name': description,
            'product_id': product_id,
            'total_amount': float(amount),
            'date': expense_date,
            'employee_id': employee_id,
        }

        if vendor:
            expense_vals['reference'] = f"Vendor: {vendor}"
        if receipt_ref:
            expense_vals['reference'] = f"{expense_vals.get('reference', '')} Ref: {receipt_ref}".strip()
        if notes:
            expense_vals['description'] = notes

        # Create expense
        result = client.create('hr.expense', expense_vals)

        if not result.success:
            # Fall back to vendor bill
            return await _create_as_vendor_bill(
                client, description, amount, category,
                expense_date, vendor, notes
            )

        expense_id = result.data
        logger.info(f"Created expense {expense_id}: {description} - ${amount}")

        return {
            'success': True,
            'expense_id': expense_id,
            'type': 'hr_expense',
            'description': description,
            'amount': float(amount),
            'category': DEFAULT_CATEGORIES.get(category, category),
            'date': expense_date,
            'requires_approval': requires_approval,
            'message': f"Expense recorded: {description}"
        }

    except Exception as e:
        logger.error(f"Error recording expense: {e}")
        return {
            'success': False,
            'error': str(e),
            'error_code': 'EXPENSE_ERROR'
        }


async def _get_expense_product(client, category: str) -> int:
    """Get or create expense product for category."""
    try:
        category_name = DEFAULT_CATEGORIES.get(category, category)

        # Search for existing product
        result = client.search_read(
            'product.product',
            [
                ('name', '=', category_name),
                ('can_be_expensed', '=', True)
            ],
            fields=['id'],
            limit=1
        )

        if result.success and result.data:
            return result.data[0]['id']

        # Create new expense product
        product_vals = {
            'name': category_name,
            'can_be_expensed': True,
            'type': 'service',
            'list_price': 0,
            'standard_price': 0
        }

        create_result = client.create('product.product', product_vals)
        if create_result.success:
            return create_result.data

        # Return default product ID (usually 1)
        return 1

    except Exception as e:
        logger.warning(f"Error getting expense product: {e}")
        return 1


async def _get_default_employee(client) -> Optional[int]:
    """Get default employee for expense."""
    try:
        # Try to find an employee
        result = client.search(
            'hr.employee',
            [],
            limit=1
        )

        if result.success and result.data:
            return result.data[0]

        return None

    except Exception as e:
        logger.warning(f"Error getting employee: {e}")
        return None


async def _create_as_vendor_bill(client, description: str, amount: float,
                                  category: str, expense_date: str,
                                  vendor: str = None, notes: str = None) -> Dict:
    """Create expense as vendor bill (fallback if hr.expense not available)."""
    try:
        # Find or create vendor
        vendor_id = None
        if vendor:
            vendor_result = client.search_read(
                'res.partner',
                [('name', '=', vendor), ('supplier_rank', '>', 0)],
                fields=['id'],
                limit=1
            )
            if vendor_result.success and vendor_result.data:
                vendor_id = vendor_result.data[0]['id']
            else:
                # Create vendor
                create_result = client.create('res.partner', {
                    'name': vendor,
                    'supplier_rank': 1
                })
                if create_result.success:
                    vendor_id = create_result.data

        # Create vendor bill
        bill_vals = {
            'move_type': 'in_invoice',
            'invoice_date': expense_date,
            'invoice_line_ids': [(0, 0, {
                'name': f"{DEFAULT_CATEGORIES.get(category, category)}: {description}",
                'quantity': 1,
                'price_unit': float(amount)
            })]
        }

        if vendor_id:
            bill_vals['partner_id'] = vendor_id

        if notes:
            bill_vals['narration'] = notes

        result = client.create('account.move', bill_vals)

        if result.success:
            logger.info(f"Created vendor bill {result.data} for expense: {description}")
            return {
                'success': True,
                'expense_id': result.data,
                'type': 'vendor_bill',
                'description': description,
                'amount': float(amount),
                'category': DEFAULT_CATEGORIES.get(category, category),
                'date': expense_date,
                'message': f"Expense recorded as vendor bill: {description}"
            }
        else:
            return {
                'success': False,
                'error': result.error
            }

    except Exception as e:
        logger.error(f"Error creating vendor bill: {e}")
        return {
            'success': False,
            'error': str(e)
        }


async def list_expenses(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    List expenses for a period.

    Args:
        params: Query parameters
            - period (str): 'this_month', 'last_month', or 'custom'
            - start_date (str): Start date for custom period
            - end_date (str): End date for custom period
            - category (str): Filter by category
            - limit (int): Max results

    Returns:
        Dict with list of expenses
    """
    client = get_client()

    try:
        start_date = params.get('start_date', date.today().replace(day=1).isoformat())
        end_date = params.get('end_date', date.today().isoformat())
        category = params.get('category')
        limit = params.get('limit', 100)

        # Get from hr.expense
        expense_domain = [
            ('date', '>=', start_date),
            ('date', '<=', end_date)
        ]

        expenses_result = client.search_read(
            'hr.expense',
            expense_domain,
            fields=['name', 'total_amount', 'date', 'state'],
            limit=limit,
            order='date desc'
        )

        expenses = []
        total = 0.0

        if expenses_result.success:
            for exp in expenses_result.data:
                amount = exp.get('total_amount', 0)
                total += amount
                expenses.append({
                    'id': exp['id'],
                    'description': exp.get('name', ''),
                    'amount': amount,
                    'date': exp.get('date', ''),
                    'status': exp.get('state', 'draft'),
                    'type': 'expense'
                })

        # Also get vendor bills
        bill_domain = [
            ('move_type', '=', 'in_invoice'),
            ('invoice_date', '>=', start_date),
            ('invoice_date', '<=', end_date),
            ('state', '=', 'posted')
        ]

        bills_result = client.search_read(
            'account.move',
            bill_domain,
            fields=['name', 'amount_total', 'invoice_date', 'partner_id'],
            limit=limit,
            order='invoice_date desc'
        )

        if bills_result.success:
            for bill in bills_result.data:
                amount = bill.get('amount_total', 0)
                total += amount
                vendor = bill.get('partner_id', [0, 'Unknown'])
                expenses.append({
                    'id': bill['id'],
                    'description': f"Bill: {vendor[1] if vendor else 'Unknown'}",
                    'amount': amount,
                    'date': bill.get('invoice_date', ''),
                    'status': 'posted',
                    'type': 'vendor_bill'
                })

        # Sort by date
        expenses.sort(key=lambda x: x.get('date', ''), reverse=True)

        return {
            'success': True,
            'expenses': expenses[:limit],
            'total': total,
            'count': len(expenses)
        }

    except Exception as e:
        logger.error(f"Error listing expenses: {e}")
        return {
            'success': False,
            'error': str(e)
        }
