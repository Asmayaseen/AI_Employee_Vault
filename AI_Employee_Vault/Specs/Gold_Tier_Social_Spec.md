# Gold Tier: Social Media Integration Specification

**Document Version:** 1.0
**Created:** 2026-02-09
**Status:** READY FOR IMPLEMENTATION
**Priority:** P2 - MEDIUM

---

## 1. Overview

### 1.1 Purpose
Integrate Facebook, Instagram, and Twitter (X) with the AI Employee system for automated social media management, monitoring, and content posting.

### 1.2 Business Value
- Automated social media presence
- Cross-platform content distribution
- Social engagement monitoring
- Lead capture from social channels
- Brand mention tracking

---

## 2. Architecture

### 2.1 High-Level Integration

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                      SOCIAL MEDIA INTEGRATION ARCHITECTURE                      │
└─────────────────────────────────────────────────────────────────────────────────┘

    AI Employee                   social-mcp                    Platforms
    ═══════════                  ══════════                    ═════════

    ┌─────────────┐
    │   Claude    │
    │   Code      │
    └──────┬──────┘
           │
           │ (1) Tool Call
           │     post_content({...})
           ▼
    ┌─────────────────────────────────────┐
    │       MCP_Servers/social-mcp/       │
    │                                     │
    │  ┌─────────────────────────────┐   │
    │  │     Platform Adapters       │   │
    │  │  - FacebookAdapter          │   │
    │  │  - InstagramAdapter         │   │
    │  │  - TwitterAdapter           │   │
    │  └──────────────┬──────────────┘   │
    │                 │                   │
    │  ┌──────────────▼──────────────┐   │
    │  │     Tool Handlers           │   │
    │  │  - post_content             │   │
    │  │  - read_messages            │   │
    │  │  - fetch_notifications      │   │
    │  │  - get_analytics            │   │
    │  │  - schedule_post            │   │
    │  └─────────────────────────────┘   │
    └───────────────┬─────────────────────┘
                    │
        ┌───────────┼───────────┐
        │           │           │
        ▼           ▼           ▼
    ┌─────────┐ ┌─────────┐ ┌─────────┐
    │Facebook │ │Instagram│ │ Twitter │
    │Graph API│ │Graph API│ │ API v2  │
    └─────────┘ └─────────┘ └─────────┘
```

### 2.2 File Structure

```
MCP_Servers/
└── social-mcp/
    ├── __init__.py
    ├── server.py               # Main MCP server
    ├── adapters/
    │   ├── __init__.py
    │   ├── base.py             # Base adapter class
    │   ├── facebook.py         # Facebook Graph API
    │   ├── instagram.py        # Instagram Graph API
    │   └── twitter.py          # Twitter API v2
    ├── tools/
    │   ├── __init__.py
    │   ├── post.py             # Content posting
    │   ├── messages.py         # Message handling
    │   ├── notifications.py    # Notification fetching
    │   └── analytics.py        # Analytics retrieval
    ├── config.py               # Configuration
    ├── requirements.txt        # Dependencies
    ├── README.md               # Documentation
    └── test_connections.py     # Connection tests

AI_Employee_Vault/Watchers/
├── facebook_watcher.py         # Facebook monitoring
├── instagram_watcher.py        # Instagram monitoring
└── twitter_watcher.py          # Twitter monitoring
```

---

## 3. MCP Tools Specification

### 3.1 post_content

**Purpose:** Post content to one or more social platforms

**Input Schema:**
```json
{
  "platforms": ["facebook", "instagram", "twitter"],
  "content": {
    "text": "string (required)",
    "media": [
      {
        "type": "image|video",
        "url": "string",
        "alt_text": "string (optional)"
      }
    ],
    "link": "string (optional)",
    "hashtags": ["string"]
  },
  "schedule": {
    "enabled": "boolean",
    "datetime": "string (ISO 8601, optional)"
  },
  "options": {
    "facebook": {
      "page_id": "string (optional)",
      "audience": "public|friends"
    },
    "instagram": {
      "post_type": "feed|story|reel"
    },
    "twitter": {
      "reply_to": "string (optional)"
    }
  }
}
```

**Output Schema:**
```json
{
  "success": "boolean",
  "results": {
    "facebook": {
      "success": "boolean",
      "post_id": "string",
      "url": "string",
      "error": "string (if failed)"
    },
    "instagram": {
      "success": "boolean",
      "post_id": "string",
      "url": "string",
      "error": "string (if failed)"
    },
    "twitter": {
      "success": "boolean",
      "tweet_id": "string",
      "url": "string",
      "error": "string (if failed)"
    }
  },
  "scheduled": "boolean",
  "scheduled_time": "string (if scheduled)"
}
```

### 3.2 read_messages

**Purpose:** Read direct messages from social platforms

**Input Schema:**
```json
{
  "platform": "facebook|instagram|twitter|all",
  "filter": {
    "unread_only": "boolean (default: true)",
    "since": "string (ISO 8601, optional)",
    "limit": "number (default: 50)"
  },
  "include_sender_info": "boolean (default: true)"
}
```

**Output Schema:**
```json
{
  "messages": [
    {
      "platform": "string",
      "id": "string",
      "sender": {
        "id": "string",
        "name": "string",
        "username": "string"
      },
      "content": "string",
      "timestamp": "string",
      "is_read": "boolean",
      "attachments": [
        {
          "type": "string",
          "url": "string"
        }
      ]
    }
  ],
  "total_count": "number",
  "unread_count": "number"
}
```

### 3.3 fetch_notifications

**Purpose:** Get notifications (mentions, likes, comments, etc.)

**Input Schema:**
```json
{
  "platform": "facebook|instagram|twitter|all",
  "types": ["mention", "like", "comment", "share", "follow"],
  "since": "string (ISO 8601, optional)",
  "limit": "number (default: 50)"
}
```

**Output Schema:**
```json
{
  "notifications": [
    {
      "platform": "string",
      "type": "string",
      "id": "string",
      "actor": {
        "id": "string",
        "name": "string",
        "username": "string"
      },
      "content": "string",
      "target_post_id": "string (if applicable)",
      "timestamp": "string",
      "url": "string"
    }
  ],
  "summary": {
    "mentions": "number",
    "likes": "number",
    "comments": "number",
    "shares": "number",
    "follows": "number"
  }
}
```

### 3.4 get_analytics

**Purpose:** Get social media analytics and metrics

**Input Schema:**
```json
{
  "platform": "facebook|instagram|twitter|all",
  "period": "today|week|month|custom",
  "start_date": "string (YYYY-MM-DD, for custom)",
  "end_date": "string (YYYY-MM-DD, for custom)",
  "metrics": ["impressions", "reach", "engagement", "followers"]
}
```

**Output Schema:**
```json
{
  "period": {
    "start": "string",
    "end": "string"
  },
  "platforms": {
    "facebook": {
      "followers": "number",
      "followers_change": "number",
      "impressions": "number",
      "reach": "number",
      "engagement_rate": "number",
      "top_post": {
        "id": "string",
        "content": "string",
        "engagement": "number"
      }
    },
    "instagram": { ... },
    "twitter": { ... }
  },
  "totals": {
    "total_followers": "number",
    "total_impressions": "number",
    "total_engagement": "number"
  }
}
```

### 3.5 schedule_post

**Purpose:** Schedule content for future posting

**Input Schema:**
```json
{
  "platforms": ["facebook", "instagram", "twitter"],
  "content": {
    "text": "string",
    "media": [...],
    "hashtags": [...]
  },
  "schedule_time": "string (ISO 8601)",
  "timezone": "string (default: UTC)"
}
```

**Output Schema:**
```json
{
  "success": "boolean",
  "scheduled_id": "string",
  "scheduled_time": "string",
  "platforms": ["string"],
  "can_edit_until": "string"
}
```

---

## 4. Watcher Specifications

### 4.1 Facebook Watcher

```python
# facebook_watcher.py

class FacebookWatcher(BaseWatcher):
    """Monitor Facebook for business-relevant activity."""

    def __init__(self, vault_path: str):
        super().__init__(vault_path, check_interval=300)  # 5 minutes
        self.keywords = ['pricing', 'quote', 'help', 'contact', 'service']

    def check_for_updates(self) -> list:
        """
        Check for:
        - New page messages
        - Comments on posts
        - Mentions of business
        - New followers (business page)
        """

    def create_action_file(self, item) -> Path:
        """Create /Needs_Action/FB_*.md file"""
```

### 4.2 Instagram Watcher

```python
# instagram_watcher.py

class InstagramWatcher(BaseWatcher):
    """Monitor Instagram for business-relevant activity."""

    def __init__(self, vault_path: str):
        super().__init__(vault_path, check_interval=300)
        self.keywords = ['dm', 'order', 'price', 'available']

    def check_for_updates(self) -> list:
        """
        Check for:
        - New direct messages
        - Comments on posts
        - Story mentions
        - New followers
        """
```

### 4.3 Twitter Watcher

```python
# twitter_watcher.py

class TwitterWatcher(BaseWatcher):
    """Monitor Twitter for business-relevant activity."""

    def __init__(self, vault_path: str):
        super().__init__(vault_path, check_interval=180)  # 3 minutes
        self.keywords = ['help', 'support', 'interested', 'pricing']

    def check_for_updates(self) -> list:
        """
        Check for:
        - Direct messages
        - Mentions
        - Quote tweets
        - Relevant keyword tweets
        """
```

---

## 5. API Configuration

### 5.1 Facebook/Instagram (Meta)

```bash
# .env configuration

# Meta App Credentials
META_APP_ID=your_app_id
META_APP_SECRET=your_app_secret
META_ACCESS_TOKEN=your_access_token

# Facebook Page
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_PAGE_TOKEN=your_page_token

# Instagram Business
INSTAGRAM_BUSINESS_ID=your_business_id
```

**Required Permissions:**
- `pages_manage_posts`
- `pages_read_engagement`
- `pages_messaging`
- `instagram_basic`
- `instagram_content_publish`
- `instagram_manage_messages`

### 5.2 Twitter (X)

```bash
# .env configuration

# Twitter API v2 Credentials
TWITTER_API_KEY=your_api_key
TWITTER_API_SECRET=your_api_secret
TWITTER_ACCESS_TOKEN=your_access_token
TWITTER_ACCESS_SECRET=your_access_secret
TWITTER_BEARER_TOKEN=your_bearer_token
```

**Required Access Level:**
- Elevated access for full API features
- Read and write permissions

---

## 6. Implementation Plan

### Phase 1: Social MCP Server (Day 1)
1. Create server structure
2. Implement base adapter class
3. Add configuration management

### Phase 2: Platform Adapters (Day 2-3)
1. Implement FacebookAdapter
2. Implement InstagramAdapter
3. Implement TwitterAdapter
4. Add authentication handling

### Phase 3: MCP Tools (Day 3-4)
1. Implement post_content
2. Implement read_messages
3. Implement fetch_notifications
4. Implement get_analytics

### Phase 4: Watchers (Day 4-5)
1. Implement facebook_watcher.py
2. Implement instagram_watcher.py
3. Implement twitter_watcher.py
4. Update orchestrator.py

### Phase 5: Integration (Day 5)
1. Add watchers to orchestrator
2. Update cron schedule
3. Add social summary to CEO Briefing

---

## 7. Human-in-the-Loop Integration

### 7.1 Approval Required For
- Posts with external links
- Posts mentioning prices/offers
- Direct message replies
- Scheduled posts

### 7.2 Approval File Format

```markdown
---
type: social_approval_request
action: post_content
platforms: [facebook, instagram, twitter]
created: 2026-02-09T10:30:00
expires: 2026-02-10T10:30:00
status: pending
---

# Social Media Post Approval

## Content Preview
"Excited to announce our new AI Employee service!
Automate your business operations with cutting-edge AI.

Learn more: https://example.com

#AI #Automation #Business"

## Platforms
- [x] Facebook
- [x] Instagram
- [x] Twitter

## Media
- image_1.jpg (attached)

## Schedule
- Immediate posting after approval

---

## To Approve
Move this file to /Approved/

## To Reject
Move this file to /Rejected/
```

---

## 8. CEO Briefing Integration

### 8.1 Social Section (New)

```markdown
## Social Media Summary

### Engagement This Week
| Platform | Followers | Change | Impressions | Engagement |
|----------|-----------|--------|-------------|------------|
| Facebook | 1,234 | +45 | 5,600 | 8.2% |
| Instagram | 890 | +32 | 3,200 | 12.4% |
| Twitter | 567 | +18 | 2,100 | 6.7% |

### Top Performing Post
- Platform: Instagram
- Engagement: 156 interactions
- Content: "New product launch..."

### Messages Requiring Attention
- 3 Facebook messages (2 about pricing)
- 1 Instagram DM (service inquiry)
- 5 Twitter mentions

### Scheduled Content
- Monday 9:00 AM: LinkedIn business tip
- Wednesday 12:00 PM: Product feature highlight
- Friday 3:00 PM: Week in review
```

---

## 9. Testing Plan

### 9.1 Unit Tests
- [ ] Platform adapter authentication
- [ ] Post creation (each platform)
- [ ] Message retrieval
- [ ] Notification parsing

### 9.2 Integration Tests
- [ ] Cross-platform posting
- [ ] Watcher to vault flow
- [ ] Approval workflow
- [ ] CEO Briefing social section

### 9.3 Test Commands
```bash
# Test all connections
python test_connections.py

# Test posting (dry run)
python -m pytest tests/test_post.py --dry-run

# Test watchers
python -m pytest tests/test_watchers.py
```

---

## 10. Rate Limiting

### 10.1 Platform Limits

| Platform | Limit | Window |
|----------|-------|--------|
| Facebook | 200 posts/day | 24 hours |
| Instagram | 25 posts/day | 24 hours |
| Twitter | 300 tweets/day | 24 hours |

### 10.2 Watcher Intervals

| Watcher | Interval | Reason |
|---------|----------|--------|
| Facebook | 5 min | API rate limits |
| Instagram | 5 min | Shared with Facebook |
| Twitter | 3 min | More lenient limits |

---

## 11. Acceptance Criteria

### Must Have
- [ ] post_content works for all 3 platforms
- [ ] read_messages retrieves DMs
- [ ] fetch_notifications gets mentions
- [ ] All 3 watchers create vault files

### Should Have
- [ ] get_analytics returns basic metrics
- [ ] schedule_post works
- [ ] CEO Briefing social section

### Nice to Have
- [ ] Media upload support
- [ ] Story/Reel posting
- [ ] Advanced analytics

---

*Specification created using SpecifyPlus methodology*
