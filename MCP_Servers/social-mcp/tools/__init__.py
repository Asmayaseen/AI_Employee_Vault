"""
Social MCP Tools Package (Gold Tier)

Exports all social media tool handlers for the MCP server.
"""

from .social_tools import (
    # Facebook
    fb_post_message,
    fb_fetch_recent_posts,
    fb_generate_summary,
    # Instagram
    ig_post_image_caption,
    ig_fetch_recent_posts,
    ig_engagement_summary,
    # Twitter/X
    tw_post_tweet,
    tw_fetch_mentions,
    tw_generate_weekly_summary,
    # Cross-platform
    generate_all_summaries,
)

__all__ = [
    'fb_post_message', 'fb_fetch_recent_posts', 'fb_generate_summary',
    'ig_post_image_caption', 'ig_fetch_recent_posts', 'ig_engagement_summary',
    'tw_post_tweet', 'tw_fetch_mentions', 'tw_generate_weekly_summary',
    'generate_all_summaries',
]
