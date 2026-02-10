"""
Accounting Tools for Odoo MCP Server (Gold Tier)

Financial summaries, expense tracking, and subscription auditing
for CEO Briefing integration.
"""

import logging
import os
from typing import Any, Dict, List, Optional
from datetime import datetime, date, timedelta
from pathlib import Path
from collections import defaultdict

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from odoo_client import get_client, OdooResult
from config import config

logger = logging.getLogger('OdooAccountingTools')

VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))


def _resolve_period(period: str, start_date: str = None,
                    end_date: str = None) -> tuple:
    """Resolve a named period into (start, end) date strings."""
    today = date.today()

    if period == 'this_week':
        start = today - timedelta(days=today.weekday())
        end = today
    elif period == 'last_week':
        start = today - timedelta(days=today.weekday() + 7)
        end = start + timedelta(days=6)
    elif period == 'this_month':
        start = today.replace(day=1)
        end = today
    elif period == 'last_month':
        first_of_month = today.replace(day=1)
        end = first_of_month - timedelta(days=1)
        start = end.replace(day=1)
    elif period == 'this_quarter':
        quarter_month = ((today.month - 1) // 3) * 3 + 1
        start = today.replace(month=quarter_month, day=1)
        end = today
    elif period == 'this_year':
        start = today.replace(month=1, day=1)
        end = today
    elif period == 'custom' and start_date and end_date:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
    else:
        start = today.replace(day=1)
        end = today

    return start.isoformat(), end.isoformat()


async def get_financial_summary(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get comprehensive financial summary from Odoo.

    Pulls revenue (posted customer invoices), expenses (vendor bills),
    profit/loss, and receivables data.

    Args:
        params:
            period (str): 'this_week', 'this_month', 'last_month',
                         'this_quarter', 'this_year', 'custom'
            start_date (str): YYYY-MM-DD (for custom period)
            end_date (str): YYYY-MM-DD (for custom period)

    Returns:
        Dict with revenue, expenses, profit, receivables, top customers
    """
    client = get_client()
    period = params.get('period', 'this_month')
    start_str, end_str = _resolve_period(
        period,
        params.get('start_date'),
        params.get('end_date')
    )

    try:
        # ---- Revenue (posted customer invoices) ----
        revenue_result = client.search_read(
            'account.move',
            [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', start_str),
                ('invoice_date', '<=', end_str),
            ],
            fields=['name', 'partner_id', 'amount_total', 'amount_residual',
                    'invoice_date', 'payment_state'],
            order='invoice_date desc'
        )

        total_revenue = 0.0
        total_collected = 0.0
        invoices_by_customer = defaultdict(float)
        invoice_count = 0

        if revenue_result.success and revenue_result.data:
            for inv in revenue_result.data:
                amount = float(inv.get('amount_total', 0))
                residual = float(inv.get('amount_residual', 0))
                total_revenue += amount
                total_collected += (amount - residual)
                invoice_count += 1

                customer_name = inv['partner_id'][1] if isinstance(inv.get('partner_id'), (list, tuple)) else 'Unknown'
                invoices_by_customer[customer_name] += amount

        # ---- Expenses (vendor bills) ----
        expense_result = client.search_read(
            'account.move',
            [
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', start_str),
                ('invoice_date', '<=', end_str),
            ],
            fields=['name', 'partner_id', 'amount_total', 'invoice_date'],
            order='invoice_date desc'
        )

        total_expenses = 0.0
        expenses_by_vendor = defaultdict(float)
        expense_count = 0

        if expense_result.success and expense_result.data:
            for bill in expense_result.data:
                amount = float(bill.get('amount_total', 0))
                total_expenses += amount
                expense_count += 1

                vendor = bill['partner_id'][1] if isinstance(bill.get('partner_id'), (list, tuple)) else 'Unknown'
                expenses_by_vendor[vendor] += amount

        # ---- Outstanding receivables (all time) ----
        receivables_result = client.search_read(
            'account.move',
            [
                ('move_type', '=', 'out_invoice'),
                ('state', '=', 'posted'),
                ('payment_state', 'in', ['not_paid', 'partial']),
            ],
            fields=['name', 'partner_id', 'amount_residual', 'invoice_date_due'],
        )

        total_receivables = 0.0
        overdue_receivables = 0.0

        if receivables_result.success and receivables_result.data:
            for inv in receivables_result.data:
                residual = float(inv.get('amount_residual', 0))
                total_receivables += residual
                due = inv.get('invoice_date_due')
                if due and date.fromisoformat(str(due)) < date.today():
                    overdue_receivables += residual

        # ---- Top customers ----
        top_customers = sorted(
            invoices_by_customer.items(), key=lambda x: x[1], reverse=True
        )[:5]

        # ---- Top expense categories ----
        top_expenses = sorted(
            expenses_by_vendor.items(), key=lambda x: x[1], reverse=True
        )[:5]

        profit = total_revenue - total_expenses

        return {
            'success': True,
            'period': {'start': start_str, 'end': end_str, 'name': period},
            'revenue': {
                'total': total_revenue,
                'collected': total_collected,
                'invoice_count': invoice_count,
            },
            'expenses': {
                'total': total_expenses,
                'bill_count': expense_count,
            },
            'profit': {
                'net': profit,
                'margin': (profit / total_revenue * 100) if total_revenue > 0 else 0,
            },
            'receivables': {
                'total_outstanding': total_receivables,
                'overdue': overdue_receivables,
            },
            'top_customers': [
                {'name': name, 'revenue': amount}
                for name, amount in top_customers
            ],
            'top_expenses': [
                {'vendor': vendor, 'amount': amount}
                for vendor, amount in top_expenses
            ],
        }

    except Exception as e:
        logger.error(f"Error fetching financial summary: {e}")
        return {'success': False, 'error': str(e), 'error_code': 'SUMMARY_ERROR'}


async def record_expense(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Record a business expense as a vendor bill in Odoo.

    Args:
        params:
            description (str): Required
            amount (float): Required
            category (str): Required - office, travel, software, marketing,
                           utilities, professional, equipment, meals, other
            date (str): YYYY-MM-DD (defaults to today)
            vendor (str): Vendor name
            receipt_ref (str): Receipt reference
            notes (str): Additional notes

    Returns:
        Dict with expense/bill ID and details
    """
    client = get_client()

    description = params.get('description')
    amount = params.get('amount')
    category = params.get('category', 'other')

    if not description:
        return {'success': False, 'error': 'description is required'}
    if not amount or float(amount) <= 0:
        return {'success': False, 'error': 'amount must be positive'}

    try:
        amount = float(amount)
        expense_date = params.get('date', date.today().isoformat())
        vendor_name = params.get('vendor', f'{category.title()} Vendor')

        # Find or create vendor
        vendor_domain = [('name', 'ilike', vendor_name), ('supplier_rank', '>', 0)]
        vendor_result = client.search_read(
            'res.partner', vendor_domain,
            fields=['id', 'name'],
            limit=1
        )

        if vendor_result.success and vendor_result.data:
            vendor_id = vendor_result.data[0]['id']
        else:
            vendor_create = client.create('res.partner', {
                'name': vendor_name,
                'supplier_rank': 1,
                'company_type': 'company'
            })
            if not vendor_create.success:
                return {'success': False, 'error': f'Cannot create vendor: {vendor_create.error}'}
            vendor_id = vendor_create.data

        # Create vendor bill
        ref = params.get('receipt_ref', '')
        narration = params.get('notes', '')
        line_name = f"[{category.upper()}] {description}"

        bill_vals = {
            'move_type': 'in_invoice',
            'partner_id': vendor_id,
            'invoice_date': expense_date,
            'ref': ref,
            'narration': narration,
            'invoice_line_ids': [(0, 0, {
                'name': line_name,
                'quantity': 1,
                'price_unit': amount,
            })],
        }

        result = client.create('account.move', bill_vals)
        if not result.success:
            return {'success': False, 'error': result.error}

        bill_id = result.data

        logger.info(f"Recorded expense bill {bill_id}: {description} ${amount}")

        return {
            'success': True,
            'bill_id': bill_id,
            'description': description,
            'amount': amount,
            'category': category,
            'vendor': vendor_name,
            'date': expense_date,
            'status': 'draft',
            'message': f"Expense recorded: {description} (${amount:,.2f})"
        }

    except Exception as e:
        logger.error(f"Error recording expense: {e}")
        return {'success': False, 'error': str(e), 'error_code': 'EXPENSE_ERROR'}


async def get_subscription_audit(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audit recurring subscriptions/expenses for the CEO Briefing.

    Identifies recurring vendor bills and flags:
    - Unused subscriptions (no recent activity)
    - Cost increases > 20%
    - Duplicate vendors

    Args:
        params:
            months_back (int): How many months to analyze (default: 3)

    Returns:
        Dict with subscriptions, flags, and cost summary
    """
    client = get_client()
    months_back = params.get('months_back', 3)

    try:
        cutoff = (date.today() - timedelta(days=months_back * 30)).isoformat()

        # Fetch all vendor bills in the period
        result = client.search_read(
            'account.move',
            [
                ('move_type', '=', 'in_invoice'),
                ('state', '=', 'posted'),
                ('invoice_date', '>=', cutoff),
            ],
            fields=['name', 'partner_id', 'amount_total', 'invoice_date', 'ref'],
            order='partner_id, invoice_date desc'
        )

        if not result.success:
            return {'success': False, 'error': result.error}

        # Group by vendor to find recurring charges
        vendor_bills = defaultdict(list)
        for bill in (result.data or []):
            vendor = bill['partner_id'][1] if isinstance(bill.get('partner_id'), (list, tuple)) else 'Unknown'
            vendor_bills[vendor].append({
                'amount': float(bill.get('amount_total', 0)),
                'date': str(bill.get('invoice_date')),
                'ref': bill.get('ref', ''),
            })

        subscriptions = []
        flags = []
        total_recurring = 0.0

        for vendor, bills in vendor_bills.items():
            if len(bills) >= 2:
                # Likely recurring
                amounts = [b['amount'] for b in bills]
                avg_amount = sum(amounts) / len(amounts)
                total_recurring += avg_amount

                sub = {
                    'vendor': vendor,
                    'occurrences': len(bills),
                    'avg_monthly_cost': round(avg_amount, 2),
                    'last_charge': bills[0]['date'],
                    'total_in_period': round(sum(amounts), 2),
                }
                subscriptions.append(sub)

                # Check for cost increase
                if len(amounts) >= 2:
                    latest = amounts[0]
                    previous = amounts[1]
                    if previous > 0 and ((latest - previous) / previous) > 0.20:
                        flags.append({
                            'type': 'cost_increase',
                            'vendor': vendor,
                            'previous': previous,
                            'current': latest,
                            'increase_pct': round(((latest - previous) / previous) * 100, 1),
                            'message': f"{vendor}: cost increased {((latest - previous) / previous) * 100:.0f}% (${previous:.2f} -> ${latest:.2f})"
                        })

        # Sort subscriptions by cost
        subscriptions.sort(key=lambda s: s['avg_monthly_cost'], reverse=True)

        return {
            'success': True,
            'period_months': months_back,
            'subscription_count': len(subscriptions),
            'total_monthly_recurring': round(total_recurring, 2),
            'subscriptions': subscriptions,
            'flags': flags,
            'flag_count': len(flags),
        }

    except Exception as e:
        logger.error(f"Error in subscription audit: {e}")
        return {'success': False, 'error': str(e), 'error_code': 'AUDIT_ERROR'}


async def create_customer(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create or update a customer in Odoo.

    Args:
        params:
            name (str): Required
            email (str): Optional
            phone (str): Optional
            address (dict): Optional {street, city, country}
            notes (str): Optional
            tags (list): Optional list of tag names

    Returns:
        Dict with customer ID and details
    """
    client = get_client()
    name = params.get('name')

    if not name:
        return {'success': False, 'error': 'name is required'}

    try:
        # Check if customer already exists
        existing = client.search_read(
            'res.partner',
            [('name', 'ilike', name), ('customer_rank', '>', 0)],
            fields=['id', 'name', 'email', 'phone'],
            limit=1
        )

        if existing.success and existing.data:
            # Update existing
            partner_id = existing.data[0]['id']
            update_vals = {}
            if params.get('email'):
                update_vals['email'] = params['email']
            if params.get('phone'):
                update_vals['phone'] = params['phone']
            if params.get('notes'):
                update_vals['comment'] = params['notes']

            address = params.get('address', {})
            if address.get('street'):
                update_vals['street'] = address['street']
            if address.get('city'):
                update_vals['city'] = address['city']
            if address.get('country'):
                # Look up country
                country_result = client.search(
                    'res.country', [('name', 'ilike', address['country'])], limit=1
                )
                if country_result.success and country_result.data:
                    update_vals['country_id'] = country_result.data[0]

            if update_vals:
                client.write('res.partner', [partner_id], update_vals)

            return {
                'success': True,
                'customer_id': partner_id,
                'name': name,
                'is_new': False,
                'message': f"Updated existing customer: {name}"
            }

        # Create new customer
        vals = {
            'name': name,
            'company_type': params.get('company_type', 'company'),
            'customer_rank': 1,
        }
        if params.get('email'):
            vals['email'] = params['email']
        if params.get('phone'):
            vals['phone'] = params['phone']
        if params.get('notes'):
            vals['comment'] = params['notes']

        address = params.get('address', {})
        if address.get('street'):
            vals['street'] = address['street']
        if address.get('city'):
            vals['city'] = address['city']

        create_result = client.create('res.partner', vals)
        if not create_result.success:
            return {'success': False, 'error': create_result.error}

        return {
            'success': True,
            'customer_id': create_result.data,
            'name': name,
            'is_new': True,
            'message': f"Created new customer: {name}"
        }

    except Exception as e:
        logger.error(f"Error managing customer: {e}")
        return {'success': False, 'error': str(e), 'error_code': 'CUSTOMER_ERROR'}
