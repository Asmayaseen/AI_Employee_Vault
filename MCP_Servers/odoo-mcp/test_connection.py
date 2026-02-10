#!/usr/bin/env python3
"""
Odoo Connection Test Script

Tests connection to Odoo server and validates configuration.

Usage:
    python test_connection.py
    python test_connection.py --verbose
"""

import sys
import asyncio
from datetime import date

from config import config
from odoo_client import OdooClient


def print_header(title: str):
    """Print section header."""
    print()
    print("=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(test_name: str, success: bool, details: str = ""):
    """Print test result."""
    icon = "✅" if success else "❌"
    print(f"  {icon} {test_name}")
    if details:
        print(f"     {details}")


def test_configuration() -> bool:
    """Test configuration validity."""
    print_header("Configuration Check")

    valid, message = config.validate()
    print_result("Configuration valid", valid, message)

    if valid:
        print(f"\n  URL: {config.url}")
        print(f"  Database: {config.database}")
        print(f"  Username: {config.username}")
        print(f"  Password: {'*' * len(config.password)}")

    return valid


def test_connection() -> bool:
    """Test connection to Odoo."""
    print_header("Connection Test")

    client = OdooClient()

    # Test version endpoint (doesn't require auth)
    version_result = client.get_version()
    if version_result.success:
        version = version_result.data
        print_result(
            "Server reachable",
            True,
            f"Version: {version.get('server_version', 'Unknown')}"
        )
    else:
        print_result("Server reachable", False, version_result.error)
        return False

    # Test authentication
    auth_result = client.connect()
    if auth_result.success:
        print_result(
            "Authentication",
            True,
            f"User ID: {client.uid}"
        )
    else:
        print_result("Authentication", False, auth_result.error)
        return False

    return True


def test_models() -> bool:
    """Test access to required models."""
    print_header("Model Access Test")

    client = OdooClient()
    if not client.connect().success:
        print_result("Connection", False, "Could not connect")
        return False

    models_to_test = [
        ('res.partner', 'Customers'),
        ('account.move', 'Invoices'),
        ('product.product', 'Products'),
    ]

    all_passed = True
    for model, name in models_to_test:
        try:
            result = client.search(model, [], limit=1)
            if result.success:
                print_result(f"{name} ({model})", True, "Accessible")
            else:
                print_result(f"{name} ({model})", False, result.error)
                all_passed = False
        except Exception as e:
            print_result(f"{name} ({model})", False, str(e))
            all_passed = False

    # Optional models (may not be installed)
    optional_models = [
        ('hr.expense', 'Expenses (optional)'),
    ]

    for model, name in optional_models:
        try:
            result = client.search(model, [], limit=1)
            if result.success:
                print_result(f"{name}", True, "Available")
            else:
                print_result(f"{name}", False, "Not installed (OK)")
        except Exception:
            print_result(f"{name}", False, "Not installed (OK)")

    return all_passed


def test_sample_operations() -> bool:
    """Test sample read/write operations."""
    print_header("Sample Operations Test")

    client = OdooClient()
    if not client.connect().success:
        print_result("Connection", False, "Could not connect")
        return False

    all_passed = True

    # Test reading partners
    try:
        result = client.search_read(
            'res.partner',
            [('customer_rank', '>', 0)],
            fields=['name', 'email'],
            limit=3
        )
        if result.success:
            count = len(result.data)
            print_result(
                "Read customers",
                True,
                f"Found {count} customer(s)"
            )
        else:
            print_result("Read customers", False, result.error)
            all_passed = False
    except Exception as e:
        print_result("Read customers", False, str(e))
        all_passed = False

    # Test reading invoices
    try:
        result = client.search_read(
            'account.move',
            [('move_type', '=', 'out_invoice')],
            fields=['name', 'amount_total', 'state'],
            limit=3
        )
        if result.success:
            count = len(result.data)
            print_result(
                "Read invoices",
                True,
                f"Found {count} invoice(s)"
            )
        else:
            print_result("Read invoices", False, result.error)
            all_passed = False
    except Exception as e:
        print_result("Read invoices", False, str(e))
        all_passed = False

    return all_passed


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("     ODOO MCP SERVER - CONNECTION TEST")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Configuration", test_configuration()))

    if results[-1][1]:  # Only continue if config is valid
        results.append(("Connection", test_connection()))

        if results[-1][1]:  # Only continue if connected
            results.append(("Model Access", test_models()))
            results.append(("Sample Operations", test_sample_operations()))

    # Summary
    print_header("Test Summary")

    all_passed = True
    for test_name, passed in results:
        print_result(test_name, passed)
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("  🎉 All tests passed! Odoo MCP server is ready.")
    else:
        print("  ⚠️  Some tests failed. Please check configuration.")

    print()
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
