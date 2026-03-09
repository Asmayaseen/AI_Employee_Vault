# Contract: Email MCP Server API

**Feature**: 002-silver-tier
**Created**: 2026-02-08
**Type**: MCP Tool Contract
**Server**: `MCP_Servers/email-mcp/index.js`

## Overview

Email MCP server provides Gmail integration via Model Context Protocol. All tools are callable by Claude Code as MCP tools.

## Tools

### send_email

**Purpose**: Send an email via Gmail

**Input**:
```json
{
  "to": "string (required) - recipient email",
  "subject": "string (required) - email subject",
  "body": "string (required) - email body (plain text or HTML)",
  "cc": "string (optional) - CC recipients",
  "bcc": "string (optional) - BCC recipients"
}
```

**Output**:
```json
{
  "success": true,
  "messageId": "string - Gmail message ID",
  "threadId": "string - Gmail thread ID"
}
```

**Errors**: `AuthError` (401), `RateLimitError` (429), `InvalidRecipient` (400)

### draft_email

**Purpose**: Create a draft email (does not send)

**Input**: Same as `send_email`

**Output**:
```json
{
  "success": true,
  "draftId": "string - Gmail draft ID"
}
```

### search_emails

**Purpose**: Search inbox with Gmail query syntax

**Input**:
```json
{
  "query": "string (required) - Gmail search query (e.g., 'is:unread from:client')",
  "max_results": "number (optional, default: 10)"
}
```

**Output**:
```json
{
  "emails": [
    {
      "id": "string",
      "threadId": "string",
      "from": "string",
      "subject": "string",
      "date": "string (ISO-8601)",
      "snippet": "string (preview)"
    }
  ],
  "total": "number"
}
```

### get_email

**Purpose**: Get full email content by ID

**Input**:
```json
{
  "id": "string (required) - Gmail message ID"
}
```

**Output**:
```json
{
  "id": "string",
  "from": "string",
  "to": "string",
  "subject": "string",
  "date": "string",
  "body": "string (full content)",
  "attachments": ["string (filenames)"]
}
```

## Authentication

- OAuth 2.0 with Gmail API scope: `gmail.modify`, `gmail.send`
- Credentials: `credentials.json` (OAuth client) + `token.json` (refresh token)
- Token auto-refresh on expiry

## Rate Limits

- Gmail API: 250 quota units/second per user
- send_email: 100 emails/day (Gmail limit)
- Application limit: 10 emails/hour (Constitution Principle VI)

## Invariants

1. All email operations MUST be logged to audit trail
2. send_email to new recipients MUST route through approval workflow
3. Bulk sends (>5 recipients) MUST require approval
4. All emails MUST include proper headers (no spoofing)
