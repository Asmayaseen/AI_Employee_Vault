"""
Social Media MCP Tools (Gold Tier)

Unified tool handlers for Facebook, Instagram, and Twitter
that wrap the platform adapters for MCP server integration.
"""

import logging
import os
from typing import Any, Dict, List
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import asdict

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from adapters import FacebookAdapter, InstagramAdapter, TwitterAdapter
from adapters.base import PostResult, Analytics
from config import config, VAULT_PATH

logger = logging.getLogger('SocialTools')

# Singleton adapter instances
_adapters = {}


def _get_adapter(platform: str):
    """Get or create adapter for platform."""
    if platform not in _adapters:
        if platform == 'facebook':
            _adapters[platform] = FacebookAdapter()
        elif platform == 'instagram':
            _adapters[platform] = InstagramAdapter()
        elif platform == 'twitter':
            _adapters[platform] = TwitterAdapter()
        else:
            return None
    return _adapters[platform]


def _write_approval_file(platform: str, action: str, content: str, metadata: Dict) -> str:
    """Create HITL approval file for social media actions."""
    approval_dir = Path(VAULT_PATH) / 'Pending_Approval'
    approval_dir.mkdir(exist_ok=True)

    ts = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"SOCIAL_{platform.upper()}_{action}_{ts}.md"
    filepath = approval_dir / filename

    md = f"""---
type: approval_request
action: social_{action}
platform: {platform}
created: {datetime.now().isoformat()}
expires: {(datetime.now() + timedelta(hours=24)).isoformat()}
status: pending
---

## Social Media {action.title()} Approval

**Platform**: {platform.title()}
**Action**: {action}

### Content
{content}

### Metadata
"""
    for k, v in metadata.items():
        md += f"- **{k}**: {v}\n"

    md += """
### To Approve
Move this file to `/Approved` folder.

### To Reject
Move this file to `/Rejected` folder.
"""
    filepath.write_text(md, encoding='utf-8')
    return str(filepath)


# ========== Facebook Tools ==========

async def fb_post_message(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post a message to Facebook page.

    Args:
        params:
            text (str): Post content
            link (str): Optional URL to attach
            hashtags (list): Optional hashtags
            require_approval (bool): Force HITL (default from config)

    Returns:
        Dict with post result or approval file path
    """
    adapter = _get_adapter('facebook')
    if not adapter or not adapter.is_configured:
        return {'success': False, 'error': 'Facebook not configured. Set META_ACCESS_TOKEN and FACEBOOK_PAGE_TOKEN.'}

    text = params.get('text', '')
    if not text:
        return {'success': False, 'error': 'text is required'}

    need_approval = params.get('require_approval', config.require_approval)

    if need_approval:
        path = _write_approval_file('facebook', 'post', text, {
            'link': params.get('link', ''),
            'hashtags': ', '.join(params.get('hashtags', [])),
        })
        return {
            'success': True,
            'status': 'pending_approval',
            'approval_file': path,
            'message': 'Facebook post queued for approval.'
        }

    result = await adapter.post_content(
        text=text,
        link=params.get('link'),
        hashtags=params.get('hashtags'),
    )

    return {
        'success': result.success,
        'platform': 'facebook',
        'post_id': result.post_id,
        'url': result.url,
        'error': result.error,
    }


async def fb_fetch_recent_posts(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch recent posts from Facebook page.

    Args:
        params:
            limit (int): Max posts (default 10)

    Returns:
        Dict with list of posts
    """
    adapter = _get_adapter('facebook')
    if not adapter or not adapter.is_configured:
        return {'success': False, 'error': 'Facebook not configured'}

    limit = params.get('limit', 10)

    try:
        page_id = adapter.config.page_id or 'me'
        result = await adapter._api_call(
            f"{page_id}/posts",
            params={
                'fields': 'id,message,created_time,shares,likes.summary(true),comments.summary(true)',
                'limit': limit
            }
        )

        if 'error' in result:
            return {'success': False, 'error': result['error'].get('message', 'API error')}

        posts = []
        for post in result.get('data', []):
            posts.append({
                'id': post.get('id'),
                'message': post.get('message', '')[:200],
                'created_time': post.get('created_time'),
                'likes': post.get('likes', {}).get('summary', {}).get('total_count', 0),
                'comments': post.get('comments', {}).get('summary', {}).get('total_count', 0),
                'shares': post.get('shares', {}).get('count', 0),
            })

        return {'success': True, 'platform': 'facebook', 'count': len(posts), 'posts': posts}

    except Exception as e:
        return {'success': False, 'error': str(e)}


async def fb_generate_summary(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate weekly Facebook performance summary.

    Args:
        params:
            days (int): Period in days (default 7)

    Returns:
        Dict with engagement metrics and summary text
    """
    adapter = _get_adapter('facebook')
    if not adapter or not adapter.is_configured:
        return {'success': False, 'error': 'Facebook not configured'}

    try:
        analytics = await adapter.get_analytics()
        posts_result = await fb_fetch_recent_posts({'limit': 20})

        total_likes = sum(p.get('likes', 0) for p in posts_result.get('posts', []))
        total_comments = sum(p.get('comments', 0) for p in posts_result.get('posts', []))
        total_shares = sum(p.get('shares', 0) for p in posts_result.get('posts', []))
        post_count = posts_result.get('count', 0)

        return {
            'success': True,
            'platform': 'facebook',
            'period_days': params.get('days', 7),
            'followers': analytics.followers,
            'posts_count': post_count,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'total_shares': total_shares,
            'engagement_rate': analytics.engagement_rate,
            'impressions': analytics.impressions,
            'summary': (
                f"Facebook: {analytics.followers} followers, {post_count} posts, "
                f"{total_likes} likes, {total_comments} comments, {total_shares} shares. "
                f"Engagement rate: {analytics.engagement_rate:.1f}%"
            )
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


# ========== Instagram Tools ==========

async def ig_post_image_caption(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post an image with caption to Instagram.

    Args:
        params:
            image_url (str): Public URL of the image (required)
            caption (str): Post caption
            hashtags (list): Optional hashtags
            require_approval (bool): Force HITL

    Returns:
        Dict with post result or approval file
    """
    adapter = _get_adapter('instagram')
    if not adapter or not adapter.is_configured:
        return {'success': False, 'error': 'Instagram not configured. Set INSTAGRAM_BUSINESS_ID and META_ACCESS_TOKEN.'}

    image_url = params.get('image_url')
    caption = params.get('caption', '')

    if not image_url:
        return {'success': False, 'error': 'image_url is required (must be publicly accessible)'}

    need_approval = params.get('require_approval', config.require_approval)

    if need_approval:
        path = _write_approval_file('instagram', 'post', caption, {
            'image_url': image_url,
            'hashtags': ', '.join(params.get('hashtags', [])),
        })
        return {
            'success': True,
            'status': 'pending_approval',
            'approval_file': path,
            'message': 'Instagram post queued for approval.'
        }

    result = await adapter.post_content(
        text=caption,
        media=[{'type': 'image', 'url': image_url}],
        hashtags=params.get('hashtags'),
    )

    return {
        'success': result.success,
        'platform': 'instagram',
        'post_id': result.post_id,
        'url': result.url,
        'error': result.error,
    }


async def ig_fetch_recent_posts(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch recent Instagram posts with engagement data.

    Args:
        params:
            limit (int): Max posts (default 10)

    Returns:
        Dict with posts and metrics
    """
    adapter = _get_adapter('instagram')
    if not adapter or not adapter.is_configured:
        return {'success': False, 'error': 'Instagram not configured'}

    limit = params.get('limit', 10)

    try:
        ig_id = adapter.config.business_id
        result = await adapter._api_call(
            f"{ig_id}/media",
            params={
                'fields': 'id,caption,timestamp,like_count,comments_count,permalink,media_type',
                'limit': limit
            }
        )

        if 'error' in result:
            return {'success': False, 'error': result['error'].get('message', 'API error')}

        posts = []
        for post in result.get('data', []):
            posts.append({
                'id': post.get('id'),
                'caption': (post.get('caption') or '')[:200],
                'timestamp': post.get('timestamp'),
                'likes': post.get('like_count', 0),
                'comments': post.get('comments_count', 0),
                'permalink': post.get('permalink'),
                'media_type': post.get('media_type'),
            })

        return {'success': True, 'platform': 'instagram', 'count': len(posts), 'posts': posts}

    except Exception as e:
        return {'success': False, 'error': str(e)}


async def ig_engagement_summary(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate Instagram engagement summary.

    Args:
        params:
            days (int): Period in days (default 7)

    Returns:
        Dict with engagement metrics
    """
    adapter = _get_adapter('instagram')
    if not adapter or not adapter.is_configured:
        return {'success': False, 'error': 'Instagram not configured'}

    try:
        analytics = await adapter.get_analytics()
        posts_result = await ig_fetch_recent_posts({'limit': 20})

        total_likes = sum(p.get('likes', 0) for p in posts_result.get('posts', []))
        total_comments = sum(p.get('comments', 0) for p in posts_result.get('posts', []))
        post_count = posts_result.get('count', 0)

        avg_likes = total_likes / post_count if post_count > 0 else 0
        avg_comments = total_comments / post_count if post_count > 0 else 0

        return {
            'success': True,
            'platform': 'instagram',
            'period_days': params.get('days', 7),
            'followers': analytics.followers,
            'posts_count': post_count,
            'total_likes': total_likes,
            'total_comments': total_comments,
            'avg_likes_per_post': round(avg_likes, 1),
            'avg_comments_per_post': round(avg_comments, 1),
            'engagement_rate': analytics.engagement_rate,
            'summary': (
                f"Instagram: {analytics.followers} followers, {post_count} posts, "
                f"avg {avg_likes:.0f} likes/post, {avg_comments:.0f} comments/post. "
                f"Engagement: {analytics.engagement_rate:.1f}%"
            )
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


# ========== Twitter/X Tools ==========

async def tw_post_tweet(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Post a tweet to Twitter/X.

    Args:
        params:
            text (str): Tweet content (max 280 chars)
            hashtags (list): Optional hashtags
            link (str): Optional URL
            reply_to (str): Optional tweet ID to reply to
            require_approval (bool): Force HITL

    Returns:
        Dict with tweet result or approval file
    """
    adapter = _get_adapter('twitter')
    if not adapter or not adapter.is_configured:
        return {'success': False, 'error': 'Twitter not configured. Set TWITTER_API_KEY and TWITTER_ACCESS_TOKEN.'}

    text = params.get('text', '')
    if not text:
        return {'success': False, 'error': 'text is required'}

    need_approval = params.get('require_approval', config.require_approval)

    if need_approval:
        path = _write_approval_file('twitter', 'tweet', text, {
            'link': params.get('link', ''),
            'hashtags': ', '.join(params.get('hashtags', [])),
            'reply_to': params.get('reply_to', ''),
        })
        return {
            'success': True,
            'status': 'pending_approval',
            'approval_file': path,
            'message': 'Tweet queued for approval.'
        }

    result = await adapter.post_content(
        text=text,
        link=params.get('link'),
        hashtags=params.get('hashtags'),
        reply_to=params.get('reply_to'),
    )

    return {
        'success': result.success,
        'platform': 'twitter',
        'post_id': result.post_id,
        'url': result.url,
        'error': result.error,
    }


async def tw_fetch_mentions(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fetch recent Twitter mentions.

    Args:
        params:
            limit (int): Max mentions (default 20)

    Returns:
        Dict with list of mentions
    """
    adapter = _get_adapter('twitter')
    if not adapter or not adapter.is_configured:
        return {'success': False, 'error': 'Twitter not configured'}

    limit = params.get('limit', 20)

    try:
        notifications = await adapter.fetch_notifications(
            types=['mention'],
            limit=limit
        )

        mentions = []
        for n in notifications:
            mentions.append({
                'id': n.id,
                'author_id': n.actor_id,
                'text': n.content,
                'timestamp': n.timestamp,
                'url': n.url,
            })

        return {'success': True, 'platform': 'twitter', 'count': len(mentions), 'mentions': mentions}

    except Exception as e:
        return {'success': False, 'error': str(e)}


async def tw_generate_weekly_summary(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate weekly Twitter/X performance summary.

    Args:
        params:
            days (int): Period in days (default 7)

    Returns:
        Dict with metrics and summary text
    """
    adapter = _get_adapter('twitter')
    if not adapter or not adapter.is_configured:
        return {'success': False, 'error': 'Twitter not configured'}

    try:
        analytics = await adapter.get_analytics()
        mentions_result = await tw_fetch_mentions({'limit': 50})
        mention_count = mentions_result.get('count', 0)

        return {
            'success': True,
            'platform': 'twitter',
            'period_days': params.get('days', 7),
            'followers': analytics.followers,
            'mentions': mention_count,
            'engagement_rate': analytics.engagement_rate,
            'summary': (
                f"Twitter/X: {analytics.followers} followers, "
                f"{mention_count} mentions this period. "
                f"Engagement: {analytics.engagement_rate:.1f}%"
            )
        }

    except Exception as e:
        return {'success': False, 'error': str(e)}


# ========== Cross-Platform Tools ==========

async def generate_all_summaries(params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate combined social media summary across all platforms.

    Args:
        params:
            days (int): Period (default 7)

    Returns:
        Dict with per-platform summaries and overall metrics
    """
    days = params.get('days', 7)
    summaries = {}
    total_followers = 0
    platforms_active = []

    # Try each platform
    for name, func in [
        ('facebook', fb_generate_summary),
        ('instagram', ig_engagement_summary),
        ('twitter', tw_generate_weekly_summary),
    ]:
        try:
            result = await func({'days': days})
            if result.get('success'):
                summaries[name] = result
                total_followers += result.get('followers', 0)
                platforms_active.append(name)
        except Exception:
            summaries[name] = {'success': False, 'error': 'Platform not available'}

    return {
        'success': True,
        'period_days': days,
        'platforms_active': platforms_active,
        'total_followers': total_followers,
        'platform_summaries': summaries,
        'overall_summary': (
            f"Social media ({len(platforms_active)} platforms active): "
            f"{total_followers} total followers across {', '.join(platforms_active) or 'none'}."
        )
    }
