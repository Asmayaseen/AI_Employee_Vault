#!/usr/bin/env python3
"""
Odoo MCP Server (Gold Tier)

Model Context Protocol server for Odoo Community integration
using JSON-RPC API (Odoo 17+/19+ compatible).

Tools:
    create_invoice      - Create customer invoice with HITL approval
    get_unpaid_invoices - List unpaid/overdue invoices
    post_invoice        - Confirm a draft invoice (post-approval)
    create_customer     - Create or update customer record
    get_financial_summary - Revenue, expenses, profit report
    record_expense      - Record vendor bill
    get_subscription_audit - Audit recurring expenses

Usage:
    python server.py                    # Run MCP server (stdio)
    python server.py --test             # Test Odoo connection
    python server.py --tool <name>      # Test a specific tool
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict

from config import (
    config, MCP_SERVER_NAME, MCP_SERVER_VERSION,
    MCP_SERVER_DESCRIPTION, LOG_LEVEL, LOG_FILE
)
from odoo_client import get_client
from tools import (
    create_invoice, get_unpaid_invoices, post_invoice,
    create_customer, get_financial_summary,
    record_expense, get_subscription_audit
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(LOG_FILE, mode='a')
    ]
)
logger = logging.getLogger('OdooMCP')


# ========== Tool Registry ==========

TOOLS = {
    'create_invoice': {
        'name': 'create_invoice',
        'description': (
            'Create a new customer invoice in Odoo (draft). '
            'Triggers HITL approval if amount exceeds threshold.'
        ),
        'inputSchema': {
            'type': 'object',
            'properties': {
                'customer_name': {'type': 'string', 'description': 'Customer name'},
                'customer_email': {'type': 'string', 'description': 'Customer email'},
                'invoice_lines': {
                    'type': 'array',
                    'description': 'Line items: [{product, quantity, unit_price, description}]',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'product': {'type': 'string'},
                            'quantity': {'type': 'number'},
                            'unit_price': {'type': 'number'},
                            'description': {'type': 'string'}
                        },
                        'required': ['product', 'quantity', 'unit_price']
                    }
                },
                'due_date': {'type': 'string', 'description': 'Due date YYYY-MM-DD'},
                'notes': {'type': 'string', 'description': 'Invoice notes'}
            },
            'required': ['customer_name', 'invoice_lines']
        },
        'handler': create_invoice
    },

    'get_unpaid_invoices': {
        'name': 'get_unpaid_invoices',
        'description': 'List unpaid or overdue customer invoices',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'status': {
                    'type': 'string',
                    'enum': ['unpaid', 'overdue', 'all'],
                    'description': 'Filter: unpaid, overdue, or all'
                },
                'customer_id': {'type': 'integer', 'description': 'Filter by customer ID'},
                'limit': {'type': 'integer', 'description': 'Max results (default 20)'}
            }
        },
        'handler': get_unpaid_invoices
    },

    'post_invoice': {
        'name': 'post_invoice',
        'description': 'Post (confirm) a draft invoice. Use after HITL approval.',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'invoice_id': {'type': 'integer', 'description': 'Odoo invoice ID to post'}
            },
            'required': ['invoice_id']
        },
        'handler': post_invoice
    },

    'create_customer': {
        'name': 'create_customer',
        'description': 'Create or update a customer record in Odoo',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'name': {'type': 'string', 'description': 'Customer name'},
                'email': {'type': 'string', 'description': 'Email address'},
                'phone': {'type': 'string', 'description': 'Phone number'},
                'address': {
                    'type': 'object',
                    'properties': {
                        'street': {'type': 'string'},
                        'city': {'type': 'string'},
                        'country': {'type': 'string'}
                    }
                },
                'notes': {'type': 'string'},
                'tags': {'type': 'array', 'items': {'type': 'string'}}
            },
            'required': ['name']
        },
        'handler': create_customer
    },

    'get_financial_summary': {
        'name': 'get_financial_summary',
        'description': (
            'Get financial summary: revenue, expenses, profit, receivables. '
            'Used by CEO Briefing for weekly accounting audit.'
        ),
        'inputSchema': {
            'type': 'object',
            'properties': {
                'period': {
                    'type': 'string',
                    'enum': ['this_week', 'this_month', 'last_month',
                             'this_quarter', 'this_year', 'custom'],
                    'description': 'Time period'
                },
                'start_date': {'type': 'string', 'description': 'YYYY-MM-DD (custom)'},
                'end_date': {'type': 'string', 'description': 'YYYY-MM-DD (custom)'}
            }
        },
        'handler': get_financial_summary
    },

    'record_expense': {
        'name': 'record_expense',
        'description': 'Record a business expense as a vendor bill',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'description': {'type': 'string', 'description': 'Expense description'},
                'amount': {'type': 'number', 'description': 'Amount'},
                'category': {
                    'type': 'string',
                    'enum': ['office', 'travel', 'software', 'marketing',
                             'utilities', 'professional', 'equipment', 'meals', 'other'],
                    'description': 'Expense category'
                },
                'date': {'type': 'string', 'description': 'YYYY-MM-DD'},
                'vendor': {'type': 'string', 'description': 'Vendor name'},
                'receipt_ref': {'type': 'string', 'description': 'Receipt reference'},
                'notes': {'type': 'string'}
            },
            'required': ['description', 'amount', 'category']
        },
        'handler': record_expense
    },

    'get_subscription_audit': {
        'name': 'get_subscription_audit',
        'description': (
            'Audit recurring subscriptions/expenses. Flags cost increases, '
            'unused subscriptions, duplicates. For CEO Briefing.'
        ),
        'inputSchema': {
            'type': 'object',
            'properties': {
                'months_back': {
                    'type': 'integer',
                    'description': 'Months to analyze (default 3)'
                }
            }
        },
        'handler': get_subscription_audit
    }
}


# ========== MCP Server ==========


# Platinum: tools blocked in draft-only mode (Cloud agent cannot execute these)
DRAFT_ONLY_BLOCKED_TOOLS = {'post_invoice', 'record_expense'}


class OdooMCPServer:
    """MCP Server for Odoo integration via JSON-RPC."""

    def __init__(self):
        self.client = get_client()
        self.draft_only = os.getenv('AGENT_MODE', '').lower() == 'draft_only'
        self.agent_name = os.getenv('AGENT_NAME', 'local')
        logger.info(f"Initializing {MCP_SERVER_NAME} v{MCP_SERVER_VERSION} (JSON-RPC)")
        logger.info(f"Agent mode: {'DRAFT-ONLY (Cloud)' if self.draft_only else 'FULL (Local)'}")

    async def handle_request(self, request: Dict) -> Dict:
        """Handle incoming MCP JSON-RPC request."""
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')

        logger.debug(f"Request: {method}")

        try:
            if method == 'initialize':
                return self._response(request_id, {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {'tools': {}},
                    'serverInfo': {
                        'name': MCP_SERVER_NAME,
                        'version': MCP_SERVER_VERSION,
                        'description': MCP_SERVER_DESCRIPTION,
                        'protocol': 'JSON-RPC'
                    }
                })

            elif method == 'notifications/initialized':
                return self._response(request_id, {})

            elif method == 'tools/list':
                tools_list = [
                    {
                        'name': t['name'],
                        'description': t['description'],
                        'inputSchema': t['inputSchema']
                    }
                    for t in TOOLS.values()
                ]
                return self._response(request_id, {'tools': tools_list})

            elif method == 'tools/call':
                tool_name = params.get('name')
                tool_args = params.get('arguments', {})

                if tool_name not in TOOLS:
                    return self._error(request_id, f"Unknown tool: {tool_name}", -32601)

                # Platinum: block irreversible tools in draft-only (Cloud) mode
                if self.draft_only and tool_name in DRAFT_ONLY_BLOCKED_TOOLS:
                    logger.warning(
                        f"[DRAFT-ONLY] Blocked tool '{tool_name}' — "
                        f"requires Local agent approval. Agent: {self.agent_name}"
                    )
                    return self._response(request_id, {
                        'content': [{
                            'type': 'text',
                            'text': json.dumps({
                                'status': 'blocked',
                                'reason': 'draft_only_mode',
                                'tool': tool_name,
                                'message': (
                                    f"Tool '{tool_name}' is blocked in draft-only mode. "
                                    f"This action requires Local agent approval. "
                                    f"Create an approval request in /Pending_Approval/accounting/ instead."
                                ),
                                'agent': self.agent_name
                            }, indent=2)
                        }]
                    })

                handler = TOOLS[tool_name]['handler']
                result = await handler(tool_args)

                return self._response(request_id, {
                    'content': [{
                        'type': 'text',
                        'text': json.dumps(result, indent=2, default=str)
                    }]
                })

            else:
                return self._error(request_id, f"Unknown method: {method}", -32601)

        except Exception as e:
            logger.error(f"Error handling {method}: {e}")
            return self._error(request_id, str(e), -32603)

    def _response(self, rid: Any, result: Any) -> Dict:
        return {'jsonrpc': '2.0', 'id': rid, 'result': result}

    def _error(self, rid: Any, message: str, code: int) -> Dict:
        return {'jsonrpc': '2.0', 'id': rid, 'error': {'code': code, 'message': message}}

    async def run_stdio(self):
        """Run server in stdio mode for Claude Code MCP integration."""
        logger.info("Odoo MCP server started (stdio, JSON-RPC)")

        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

        writer_transport, writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
            asyncio.streams.FlowControlMixin, sys.stdout
        )
        writer = asyncio.StreamWriter(
            writer_transport, writer_protocol, reader, asyncio.get_event_loop()
        )

        while True:
            try:
                line = await reader.readline()
                if not line:
                    break

                request = json.loads(line.decode())
                response = await self.handle_request(request)
                output = json.dumps(response) + '\n'
                writer.write(output.encode())
                await writer.drain()

            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
            except Exception as e:
                logger.error(f"Server loop error: {e}")
                break

        logger.info("Odoo MCP server shutting down")


# ========== CLI ==========

async def test_connection():
    """Test Odoo JSON-RPC connection."""
    print("=" * 50)
    print("  Odoo Connection Test (JSON-RPC)")
    print("=" * 50)

    valid, message = config.validate()
    print(f"Configuration: {message}")

    if not valid:
        print(f"\nConfiguration Error: {message}")
        print("\nRequired environment variables:")
        print("  ODOO_URL=http://localhost:8069")
        print("  ODOO_DB=odoo")
        print("  ODOO_USERNAME=admin")
        print("  ODOO_PASSWORD=admin")
        return False

    print(f"\nEndpoint: {config.jsonrpc_url}")
    print(f"Database: {config.database}")
    print(f"Username: {config.username}")

    client = get_client()
    result = client.test_connection()

    if result.success:
        print(f"\nConnection successful!")
        print(f"  Protocol: {result.data.get('protocol')}")
        print(f"  Server: {result.data.get('server_version')}")
        print(f"  UID: {result.data.get('uid')}")
        return True
    else:
        print(f"\nConnection failed: {result.error}")
        return False


async def test_tool(tool_name: str):
    """Test a specific MCP tool."""
    if tool_name not in TOOLS:
        print(f"Unknown tool: {tool_name}")
        print(f"Available: {', '.join(TOOLS.keys())}")
        return

    default_params = {
        'create_invoice': {
            'customer_name': 'Test Client',
            'invoice_lines': [{'product': 'Consulting', 'quantity': 2, 'unit_price': 150}]
        },
        'get_unpaid_invoices': {'status': 'unpaid', 'limit': 5},
        'post_invoice': {'invoice_id': 1},
        'create_customer': {'name': 'Test Corp', 'email': 'test@example.com'},
        'get_financial_summary': {'period': 'this_month'},
        'record_expense': {'description': 'Office supplies', 'amount': 45, 'category': 'office'},
        'get_subscription_audit': {'months_back': 3},
    }

    params = default_params.get(tool_name, {})
    print(f"\nTesting: {tool_name}")
    print(f"Params: {json.dumps(params, indent=2)}")

    handler = TOOLS[tool_name]['handler']
    result = await handler(params)
    print(f"\nResult:\n{json.dumps(result, indent=2, default=str)}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Odoo MCP Server (JSON-RPC)')
    parser.add_argument('--test', action='store_true', help='Test connection')
    parser.add_argument('--tool', type=str, help='Test specific tool')
    args = parser.parse_args()

    if args.test:
        asyncio.run(test_connection())
    elif args.tool:
        asyncio.run(test_tool(args.tool))
    else:
        server = OdooMCPServer()
        asyncio.run(server.run_stdio())


if __name__ == '__main__':
    main()
