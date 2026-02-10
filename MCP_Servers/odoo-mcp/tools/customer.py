"""
Customer Tools for Odoo MCP

Handles customer/partner management in Odoo.
"""

import logging
from typing import Dict, List, Optional, Any

import sys
sys.path.append('..')
from odoo_client import get_client, OdooResult

logger = logging.getLogger('OdooCustomer')


async def add_customer(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Create or update a customer record in Odoo.

    Args:
        params: Customer parameters
            - name (str): Customer name (required)
            - email (str): Email address (optional)
            - phone (str): Phone number (optional)
            - address (dict): Address details (optional)
                - street (str)
                - city (str)
                - country (str)
            - notes (str): Internal notes (optional)
            - tags (list): Tag names (optional)

    Returns:
        Dict with customer details or error
    """
    client = get_client()

    try:
        name = params.get('name')
        email = params.get('email')
        phone = params.get('phone')
        address = params.get('address', {})
        notes = params.get('notes')
        tags = params.get('tags', [])

        if not name:
            return {
                'success': False,
                'error': 'name is required'
            }

        # Check if customer exists
        domain = [('name', '=', name)]
        if email:
            domain = ['|', ('name', '=', name), ('email', '=', email)]

        existing = client.search_read(
            'res.partner',
            domain,
            fields=['id', 'name', 'email'],
            limit=1
        )

        is_new = True
        partner_id = None

        if existing.success and existing.data:
            # Update existing customer
            is_new = False
            partner_id = existing.data[0]['id']

            update_vals = {}
            if email and email != existing.data[0].get('email'):
                update_vals['email'] = email
            if phone:
                update_vals['phone'] = phone
            if address:
                if address.get('street'):
                    update_vals['street'] = address['street']
                if address.get('city'):
                    update_vals['city'] = address['city']
            if notes:
                update_vals['comment'] = notes

            if update_vals:
                client.write('res.partner', [partner_id], update_vals)

            logger.info(f"Updated customer {partner_id}: {name}")

        else:
            # Create new customer
            partner_vals = {
                'name': name,
                'company_type': 'company',
                'customer_rank': 1
            }

            if email:
                partner_vals['email'] = email
            if phone:
                partner_vals['phone'] = phone
            if address:
                if address.get('street'):
                    partner_vals['street'] = address['street']
                if address.get('city'):
                    partner_vals['city'] = address['city']
            if notes:
                partner_vals['comment'] = notes

            result = client.create('res.partner', partner_vals)

            if not result.success:
                return {
                    'success': False,
                    'error': result.error
                }

            partner_id = result.data
            logger.info(f"Created customer {partner_id}: {name}")

        # Handle tags if provided
        if tags and partner_id:
            await _apply_tags(client, partner_id, tags)

        return {
            'success': True,
            'customer_id': partner_id,
            'is_new': is_new,
            'message': f"Customer {'created' if is_new else 'updated'}: {name}"
        }

    except Exception as e:
        logger.error(f"Error managing customer: {e}")
        return {
            'success': False,
            'error': str(e),
            'error_code': 'CUSTOMER_ERROR'
        }


async def _apply_tags(client, partner_id: int, tag_names: List[str]):
    """Apply category tags to a partner."""
    try:
        for tag_name in tag_names:
            # Find or create tag
            tag_result = client.search_read(
                'res.partner.category',
                [('name', '=', tag_name)],
                fields=['id'],
                limit=1
            )

            if tag_result.success and tag_result.data:
                tag_id = tag_result.data[0]['id']
            else:
                # Create tag
                create_result = client.create(
                    'res.partner.category',
                    {'name': tag_name}
                )
                if create_result.success:
                    tag_id = create_result.data
                else:
                    continue

            # Link tag to partner
            client.write('res.partner', [partner_id], {
                'category_id': [(4, tag_id)]  # 4 = add
            })

    except Exception as e:
        logger.warning(f"Error applying tags: {e}")


async def search_customers(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Search for customers in Odoo.

    Args:
        params: Search parameters
            - query (str): Search query (name, email, phone)
            - limit (int): Max results (default: 20)

    Returns:
        Dict with list of matching customers
    """
    client = get_client()

    try:
        query = params.get('query', '')
        limit = params.get('limit', 20)

        if not query:
            return {
                'success': False,
                'error': 'query is required'
            }

        # Build domain - search in name, email, phone
        domain = [
            ('customer_rank', '>', 0),
            '|', '|',
            ('name', 'ilike', query),
            ('email', 'ilike', query),
            ('phone', 'ilike', query)
        ]

        result = client.search_read(
            'res.partner',
            domain,
            fields=['id', 'name', 'email', 'phone', 'city', 'country_id'],
            limit=limit,
            order='name asc'
        )

        if not result.success:
            return {
                'success': False,
                'error': result.error
            }

        customers = []
        for partner in result.data:
            customers.append({
                'id': partner['id'],
                'name': partner.get('name', ''),
                'email': partner.get('email', ''),
                'phone': partner.get('phone', ''),
                'city': partner.get('city', ''),
                'country': partner.get('country_id', [0, ''])[1] if partner.get('country_id') else ''
            })

        return {
            'success': True,
            'customers': customers,
            'count': len(customers)
        }

    except Exception as e:
        logger.error(f"Error searching customers: {e}")
        return {
            'success': False,
            'error': str(e),
            'error_code': 'SEARCH_ERROR'
        }
