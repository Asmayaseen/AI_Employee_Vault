# Contract: Social Media MCP Server API

**Feature**: 003-gold-tier
**Created**: 2026-02-09
**Type**: MCP Tool Contract
**Server**: `MCP_Servers/social-mcp/server.py`

## Overview

Social Media MCP server provides cross-platform social media management via Model Context Protocol. Supports Facebook, Instagram, and Twitter through platform-specific adapters.

## Tools

### post_content

**Purpose**: Post content to one or more social platforms

**Input**:
```json
{
  "platforms": ["facebook", "instagram", "twitter"],
  "content": {
    "text": "string (required)",
    "media": [
      {
        "type": "image|video",
        "url": "string (local path or URL)",
        "alt_text": "string (optional)"
      }
    ],
    "link": "string (optional)",
    "hashtags": ["string"]
  },
  "schedule": {
    "enabled": "boolean (default: false)",
    "datetime": "string (ISO-8601, required if enabled=true)"
  }
}
```

**Output**:
```json
{
  "success": true,
  "results": {
    "facebook": { "success": true, "post_id": "string", "url": "string" },
    "instagram": { "success": true, "post_id": "string", "url": "string" },
    "twitter": { "success": true, "tweet_id": "string", "url": "string" }
  },
  "scheduled": false
}
```

**Approval**: REQUIRED - all social posts route through `/Pending_Approval/`

---

### read_messages

**Purpose**: Read direct messages from social platforms

**Input**:
```json
{
  "platform": "facebook|instagram|twitter|all",
  "filter": {
    "unread_only": "boolean (default: true)",
    "since": "string (ISO-8601, optional)",
    "limit": "number (default: 50)"
  }
}
```

**Output**:
```json
{
  "messages": [
    {
      "platform": "string",
      "id": "string",
      "sender": { "id": "string", "name": "string" },
      "text": "string",
      "timestamp": "string (ISO-8601)",
      "read": false
    }
  ],
  "total": "number"
}
```

---

### fetch_notifications

**Purpose**: Get recent notifications across platforms

**Input**:
```json
{
  "platform": "facebook|instagram|twitter|all",
  "limit": "number (default: 20)"
}
```

**Output**:
```json
{
  "notifications": [
    {
      "platform": "string",
      "type": "like|comment|mention|follow|share",
      "from": "string",
      "content": "string",
      "timestamp": "string",
      "post_id": "string (optional)"
    }
  ]
}
```

---

### get_analytics

**Purpose**: Get engagement analytics per platform

**Input**:
```json
{
  "platform": "facebook|instagram|twitter|all",
  "period": "string (7d|30d|90d, default: 7d)"
}
```

**Output**:
```json
{
  "analytics": {
    "facebook": {
      "followers": "number",
      "posts": "number",
      "engagement_rate": "number (%)",
      "top_post": { "id": "string", "likes": "number" }
    },
    "instagram": { "...same structure..." },
    "twitter": { "...same structure..." }
  }
}
```

## Platform Adapter Interface

```python
class BaseSocialAdapter(ABC):
    """All platform adapters must implement."""

    @abstractmethod
    async def post(self, content: dict) -> dict:
        """Post content. Returns {success, post_id, url}."""

    @abstractmethod
    async def read_messages(self, filter: dict) -> list:
        """Read DMs. Returns list of message dicts."""

    @abstractmethod
    async def get_notifications(self, limit: int) -> list:
        """Get notifications. Returns list of notification dicts."""

    @abstractmethod
    async def get_analytics(self, period: str) -> dict:
        """Get analytics. Returns metrics dict."""
```

## Platform Authentication

| Platform | Auth Method | Env Variables |
|----------|------------|---------------|
| Facebook | OAuth 2.0 (Graph API) | `FACEBOOK_PAGE_ID`, `FACEBOOK_ACCESS_TOKEN` |
| Instagram | OAuth 2.0 (Graph API) | `INSTAGRAM_BUSINESS_ID`, `INSTAGRAM_ACCESS_TOKEN` |
| Twitter | OAuth 2.0 (API v2) | `TWITTER_API_KEY`, `TWITTER_API_SECRET`, `TWITTER_ACCESS_TOKEN`, `TWITTER_ACCESS_SECRET` |

## Rate Limits

| Platform | Posts/day | API calls/15min |
|----------|-----------|-----------------|
| Facebook | 25 | 200 |
| Instagram | 25 | 200 |
| Twitter | 50 tweets | 300 |

## Invariants

1. All post_content calls MUST route through approval workflow
2. All API calls MUST be logged to audit trail
3. Platform failures MUST be handled independently (one failing doesn't block others)
4. Rate limits MUST be tracked per-platform to avoid API bans
5. Connection failures MUST use retry_handler with exponential backoff
6. Platform unavailability MUST be tracked by graceful_degradation manager
