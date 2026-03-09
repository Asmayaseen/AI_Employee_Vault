# Skill: Social Media Integration (Gold Tier)

## Overview
Integrate Facebook, Instagram, and Twitter/X platforms for automated posting, engagement tracking, and summary generation with human-in-the-loop approval.

## Prerequisites
- Facebook/Instagram Graph API credentials
- Twitter/X API v2 credentials
- Social MCP server infrastructure

## Capabilities
- **Auto-Post**: Draft and post business updates (with approval)
- **Engagement Tracking**: Monitor likes, comments, shares
- **Summary Generation**: Weekly cross-platform engagement reports
- **Content Calendar**: Schedule posts for optimal times
- **Mention Monitoring**: Track brand mentions and replies

## Implementation Details

### MCP Server: social-mcp
- Location: `MCP_Servers/social-mcp/`
- Adapters: Facebook, Instagram, Twitter (pluggable)
- Approval flow: Posts go to Pending_Approval before publishing

### Tools Provided
| Tool | Description |
|------|-------------|
| `fb_post_message` | Post to Facebook page |
| `fb_fetch_recent_posts` | Fetch recent Facebook posts |
| `ig_post_image_caption` | Post image to Instagram |
| `ig_engagement_summary` | Instagram engagement report |
| `tw_post_tweet` | Post a tweet |
| `tw_fetch_mentions` | Fetch Twitter mentions |
| `generate_all_summaries` | Cross-platform combined summary |

### Approval Flow
1. AI drafts post content
2. Post saved to `Pending_Approval/` with platform metadata
3. User approves or rejects via dashboard
4. Approved posts are published to target platform
5. Results logged to audit trail

### Error Handling
- Rate limit exceeded: Backoff and retry after window
- Auth token expired: Notify user, queue posts
- Platform API down: Queue locally, monitor for recovery

### Auto-Poster System
- **LinkedIn Auto-Poster**: `Watchers/linkedin_auto_poster.py` — Mon 9AM, Wed 12PM, Fri 3PM
- **Social Auto-Poster**: `Watchers/social_auto_poster.py` — Unified FB/IG/TW poster
  - Facebook: Tue 10AM, Thu 2PM, Sat 11AM
  - Instagram: Mon 11AM, Wed 5PM, Fri 10AM
  - Twitter/X: Daily 9AM, 1PM, 5PM
- Content generated from Business_Goals.md + recent achievements
- All posts go through HITL `/Pending_Approval/` -> `/Approved/` flow

### Key Files
| File | Role |
|------|------|
| `Watchers/social_auto_poster.py` | Multi-platform content generation |
| `Watchers/facebook_watcher.py` | Monitor Facebook inbox/comments |
| `Watchers/instagram_watcher.py` | Monitor Instagram DMs/mentions |
| `Watchers/twitter_watcher.py` | Monitor Twitter DMs/mentions |
| `Watchers/approval_watcher.py` | Execute approved posts via API |
| `MCP_Servers/social-mcp/server.py` | MCP server with 10 tools |
| `MCP_Servers/social-mcp/adapters/` | Platform API adapters |

### Dashboard Integration
- All 3 social watchers visible in dashboard status
- Statistics tracking: processed_facebook, processed_instagram, processed_twitter
- Start/stop controls for each social watcher

### CEO Briefing Integration
- Cross-platform social media summary section
- Task type detection for facebook/instagram/twitter items
- Integrates `generate_all_summaries` from social-mcp

## Acceptance Criteria
- [x] Each platform adapter initializes with credentials
- [x] Posts require approval before publishing
- [x] Weekly summaries generate correctly
- [x] Auto-poster generates content for all platforms on schedule
- [x] Dashboard monitors all social watchers
- [x] CEO briefing includes cross-platform social summary
- [ ] Rate limits are respected (config exists, enforcement pending)
- [ ] Failures are queued and retried (graceful degradation active)
