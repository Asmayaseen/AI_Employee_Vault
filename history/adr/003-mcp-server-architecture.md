# ADR-003: MCP Server Architecture for External Integrations

- **Status:** Accepted
- **Date:** 2026-02-08
- **Feature:** 002-silver-tier, 003-gold-tier
- **Context:** The AI Employee needs to interact with multiple external services (Gmail, Odoo accounting, social media platforms). Need a standardized, extensible integration pattern that allows Claude Code to execute actions while maintaining separation of concerns and independent testability.

## Decision

Use Model Context Protocol (MCP) servers as the standardized integration layer. Each external service gets its own MCP server with a tool-based interface callable by Claude Code:

- **email-mcp** (Node.js): Gmail integration - send_email, draft_email, read_inbox, search_emails
- **odoo-mcp** (Python): Odoo accounting - create_invoice, fetch_financial_summary, add_customer, record_expense
- **social-mcp** (Python): Social media - post_content, read_messages, fetch_notifications, get_analytics

Each MCP server:
- Runs as an independent process with its own dependencies
- Exposes tools via MCP stdio transport
- Has its own configuration (.env, config.py)
- Can be tested independently with its own test scripts
- Language choice based on best ecosystem fit (Node.js for email/OAuth, Python for XML-RPC/REST)

## Consequences

### Positive

- Standardized tool interface across all integrations - Claude Code calls all services the same way
- Language flexibility per server - use the best language for each integration
- Independent deployment and testing - can update one server without affecting others
- Native Claude Code integration via MCP protocol
- Easy to add new services - just create a new MCP server following the pattern
- Failure isolation - one server crashing doesn't affect others

### Negative

- Multiple runtime environments to manage (Node.js + Python)
- MCP protocol adds serialization overhead for each tool call
- Each server needs separate health monitoring and restart logic
- Debugging across MCP protocol boundaries is harder than direct function calls
- MCP SDK is relatively new, less community tooling available

## Alternatives Considered

- **Direct API calls from Claude Code**: Rejected because it creates tight coupling between reasoning and execution. Harder to test, harder to mock, and mixes concerns. Also, Claude Code sessions are ephemeral.
- **Single monolith server**: Rejected because coupling all integrations increases blast radius of failures. A bug in the social media adapter shouldn't bring down invoice creation.
- **REST API gateway**: Rejected because it doesn't integrate natively with Claude's tool system. Would require an extra translation layer between REST and MCP, adding complexity without benefit.

## References

- Feature Spec: `/specs/002-silver-tier/spec.md`, `/specs/003-gold-tier/spec.md`
- Implementation Plan: `/specs/003-gold-tier/plan.md`
- Constitution: `.specify/memory/constitution.md` (Principle IV: Agent Skills Standard)
