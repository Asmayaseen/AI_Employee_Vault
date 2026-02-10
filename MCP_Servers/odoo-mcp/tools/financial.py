"""
Financial Tools for Odoo MCP

Handles financial summaries and reporting from Odoo.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, date, timedelta
from calendar import monthrange

import sys
sys.path.append('..')
from odoo_client import get_client, OdooResult

logger = logging.getLogger('OdooFinancial')


async def fetch_financial_summary(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get financial summary for a period.

    Args:
        params: Query parameters
            - period (str): 'this_month', 'last_month', 'this_quarter',
                           'this_year', or 'custom'
            - start_date (str): Start date YYYY-MM-DD (for custom period)
            - end_date (str): End date YYYY-MM-DD (for custom period)

    Returns:
        Dict with financial summary data
    """
    client = get_client()

    try:
        period = params.get('period', 'this_month')
        start_date, end_date = _get_period_dates(
            period,
            params.get('start_date'),
            params.get('end_date')
        )

        logger.info(f"Fetching financial summary for {start_date} to {end_date}")

        # Get revenue data
        revenue = await _get_revenue_summary(client, start_date, end_date)

        # Get expense data
        expenses = await _get_expense_summary(client, start_date, end_date)

        # Get invoice counts
        invoice_stats = await _get_invoice_stats(client, start_date, end_date)

        # Get customer counts
        customer_count = await _get_customer_count(client, start_date, end_date)

        # Calculate profit
        profit = revenue.get('total', 0) - expenses.get('total', 0)

        return {
            'success': True,
            'period': {
                'start': start_date,
                'end': end_date,
                'name': period
            },
            'revenue': revenue,
            'expenses': expenses,
            'profit': profit,
            'invoice_count': invoice_stats.get('total', 0),
            'paid_invoice_count': invoice_stats.get('paid', 0),
            'unpaid_invoice_count': invoice_stats.get('unpaid', 0),
            'customer_count': customer_count,
            'summary': _generate_summary_text(revenue, expenses, profit)
        }

    except Exception as e:
        logger.error(f"Error fetching financial summary: {e}")
        return {
            'success': False,
            'error': str(e),
            'error_code': 'FINANCIAL_ERROR'
        }


def _get_period_dates(period: str, custom_start: str = None,
                      custom_end: str = None) -> tuple[str, str]:
    """Calculate start and end dates for a period."""
    today = date.today()

    if period == 'this_month':
        start = today.replace(day=1)
        _, last_day = monthrange(today.year, today.month)
        end = today.replace(day=last_day)

    elif period == 'last_month':
        first_of_this_month = today.replace(day=1)
        last_month_end = first_of_this_month - timedelta(days=1)
        start = last_month_end.replace(day=1)
        end = last_month_end

    elif period == 'this_quarter':
        quarter = (today.month - 1) // 3
        start_month = quarter * 3 + 1
        start = today.replace(month=start_month, day=1)
        end_month = start_month + 2
        _, last_day = monthrange(today.year, end_month)
        end = today.replace(month=end_month, day=last_day)

    elif period == 'this_year':
        start = today.replace(month=1, day=1)
        end = today.replace(month=12, day=31)

    elif period == 'custom' and custom_start and custom_end:
        start = datetime.strptime(custom_start, '%Y-%m-%d').date()
        end = datetime.strptime(custom_end, '%Y-%m-%d').date()

    else:
        # Default to this month
        start = today.replace(day=1)
        _, last_day = monthrange(today.year, today.month)
        end = today.replace(day=last_day)

    return start.isoformat(), end.isoformat()


async def _get_revenue_summary(client, start_date: str, end_date: str) -> Dict:
    """Get revenue summary from invoices."""
    try:
        # Get all customer invoices in period
        result = client.search_read(
            'account.move',
            [
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('state', '=', 'posted')
            ],
            fields=['amount_total', 'amount_residual', 'payment_state']
        )

        if not result.success:
            return {'total': 0, 'invoiced': 0, 'paid': 0, 'outstanding': 0}

        total_invoiced = 0.0
        total_paid = 0.0
        total_outstanding = 0.0

        for invoice in result.data:
            amount = invoice.get('amount_total', 0)
            residual = invoice.get('amount_residual', 0)

            total_invoiced += amount
            total_paid += (amount - residual)
            total_outstanding += residual

        return {
            'total': total_invoiced,
            'invoiced': total_invoiced,
            'paid': total_paid,
            'outstanding': total_outstanding
        }

    except Exception as e:
        logger.error(f"Error getting revenue: {e}")
        return {'total': 0, 'invoiced': 0, 'paid': 0, 'outstanding': 0}


async def _get_expense_summary(client, start_date: str, end_date: str) -> Dict:
    """Get expense summary."""
    try:
        # Get vendor bills in period
        result = client.search_read(
            'account.move',
            [
                ('move_type', '=', 'in_invoice'),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('state', '=', 'posted')
            ],
            fields=['amount_total']
        )

        total = 0.0
        if result.success:
            for bill in result.data:
                total += bill.get('amount_total', 0)

        # Also try to get expenses from hr.expense if module is installed
        expense_result = client.search_read(
            'hr.expense',
            [
                ('date', '>=', start_date),
                ('date', '<=', end_date),
                ('state', '=', 'done')
            ],
            fields=['total_amount', 'name']
        )

        by_category = {}
        if expense_result.success:
            for expense in expense_result.data:
                amount = expense.get('total_amount', 0)
                category = expense.get('name', 'Other')
                total += amount
                by_category[category] = by_category.get(category, 0) + amount

        return {
            'total': total,
            'by_category': by_category if by_category else {'General': total}
        }

    except Exception as e:
        logger.error(f"Error getting expenses: {e}")
        return {'total': 0, 'by_category': {}}


async def _get_invoice_stats(client, start_date: str, end_date: str) -> Dict:
    """Get invoice statistics."""
    try:
        # Total invoices
        total_result = client.search(
            'account.move',
            [
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('state', '=', 'posted')
            ]
        )

        # Paid invoices
        paid_result = client.search(
            'account.move',
            [
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('state', '=', 'posted'),
                ('payment_state', '=', 'paid')
            ]
        )

        total = len(total_result.data) if total_result.success else 0
        paid = len(paid_result.data) if paid_result.success else 0

        return {
            'total': total,
            'paid': paid,
            'unpaid': total - paid
        }

    except Exception as e:
        logger.error(f"Error getting invoice stats: {e}")
        return {'total': 0, 'paid': 0, 'unpaid': 0}


async def _get_customer_count(client, start_date: str, end_date: str) -> int:
    """Get count of active customers in period."""
    try:
        result = client.search_read(
            'account.move',
            [
                ('move_type', '=', 'out_invoice'),
                ('invoice_date', '>=', start_date),
                ('invoice_date', '<=', end_date),
                ('state', '=', 'posted')
            ],
            fields=['partner_id']
        )

        if result.success:
            unique_customers = set()
            for invoice in result.data:
                partner = invoice.get('partner_id')
                if partner:
                    unique_customers.add(partner[0])
            return len(unique_customers)

        return 0

    except Exception as e:
        logger.error(f"Error getting customer count: {e}")
        return 0


def _generate_summary_text(revenue: Dict, expenses: Dict, profit: float) -> str:
    """Generate human-readable summary text."""
    total_rev = revenue.get('total', 0)
    paid_rev = revenue.get('paid', 0)
    outstanding = revenue.get('outstanding', 0)
    total_exp = expenses.get('total', 0)

    collection_rate = (paid_rev / total_rev * 100) if total_rev > 0 else 0

    lines = [
        f"Total Revenue: ${total_rev:,.2f}",
        f"Collected: ${paid_rev:,.2f} ({collection_rate:.0f}%)",
        f"Outstanding: ${outstanding:,.2f}",
        f"Total Expenses: ${total_exp:,.2f}",
        f"Net Profit: ${profit:,.2f}"
    ]

    if profit > 0:
        lines.append("Status: Profitable")
    elif profit < 0:
        lines.append("Status: Operating at loss")
    else:
        lines.append("Status: Break-even")

    return "\n".join(lines)
