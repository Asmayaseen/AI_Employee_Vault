#!/usr/bin/env python3
"""
Social Media MCP Server (Gold Tier)

Model Context Protocol server for Facebook, Instagram, and Twitter/X.
Provides posting, fetching, and summary generation with HITL approval.

Tools:
    fb_post_message         - Post to Facebook page
    fb_fetch_recent_posts   - Fetch recent Facebook posts
    fb_generate_summary     - Weekly Facebook summary
    ig_post_image_caption   - Post image to Instagram
    ig_fetch_recent_posts   - Fetch recent Instagram posts
    ig_engagement_summary   - Instagram engagement report
    tw_post_tweet           - Post tweet
    tw_fetch_mentions       - Fetch Twitter mentions
    tw_generate_weekly_summary - Twitter weekly summary
    generate_all_summaries  - Cross-platform combined summary

Usage:
    python server.py              # Run MCP server (stdio)
    python server.py --test       # Check configured platforms
    python server.py --tool <name> # Test specific tool
"""

import asyncio
import json
import logging
import sys
from typing import Any, Dict

from config import (
    config, MCP_SERVER_NAME, MCP_SERVER_VERSION,
    MCP_SERVER_DESCRIPTION, LOG_LEVEL, LOG_FILE
)
from tools import (
    fb_post_message, fb_fetch_recent_posts, fb_generate_summary,
    ig_post_image_caption, ig_fetch_recent_posts, ig_engagement_summary,
    tw_post_tweet, tw_fetch_mentions, tw_generate_weekly_summary,
    generate_all_summaries,
)

# Logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(LOG_FILE, mode='a')
    ]
)
logger = logging.getLogger('SocialMCP')


# ========== Tool Registry ==========

TOOLS = {
    'fb_post_message': {
        'name': 'fb_post_message',
        'description': 'Post a message to Facebook page (with optional HITL approval)',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'text': {'type': 'string', 'description': 'Post content'},
                'link': {'type': 'string', 'description': 'URL to attach'},
                'hashtags': {'type': 'array', 'items': {'type': 'string'}},
                'require_approval': {'type': 'boolean', 'description': 'Force HITL approval'}
            },
            'required': ['text']
        },
        'handler': fb_post_message
    },
    'fb_fetch_recent_posts': {
        'name': 'fb_fetch_recent_posts',
        'description': 'Fetch recent posts from Facebook page with engagement data',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'limit': {'type': 'integer', 'description': 'Max posts (default 10)'}
            }
        },
        'handler': fb_fetch_recent_posts
    },
    'fb_generate_summary': {
        'name': 'fb_generate_summary',
        'description': 'Generate weekly Facebook performance summary for CEO briefing',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'days': {'type': 'integer', 'description': 'Period in days (default 7)'}
            }
        },
        'handler': fb_generate_summary
    },
    'ig_post_image_caption': {
        'name': 'ig_post_image_caption',
        'description': 'Post an image with caption to Instagram (requires public image URL)',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'image_url': {'type': 'string', 'description': 'Public URL of image'},
                'caption': {'type': 'string', 'description': 'Post caption'},
                'hashtags': {'type': 'array', 'items': {'type': 'string'}},
                'require_approval': {'type': 'boolean'}
            },
            'required': ['image_url']
        },
        'handler': ig_post_image_caption
    },
    'ig_fetch_recent_posts': {
        'name': 'ig_fetch_recent_posts',
        'description': 'Fetch recent Instagram posts with likes and comments',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'limit': {'type': 'integer', 'description': 'Max posts (default 10)'}
            }
        },
        'handler': ig_fetch_recent_posts
    },
    'ig_engagement_summary': {
        'name': 'ig_engagement_summary',
        'description': 'Generate Instagram engagement summary for CEO briefing',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'days': {'type': 'integer', 'description': 'Period (default 7)'}
            }
        },
        'handler': ig_engagement_summary
    },
    'tw_post_tweet': {
        'name': 'tw_post_tweet',
        'description': 'Post a tweet to Twitter/X (max 280 chars, with optional HITL)',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'text': {'type': 'string', 'description': 'Tweet text (max 280 chars)'},
                'hashtags': {'type': 'array', 'items': {'type': 'string'}},
                'link': {'type': 'string', 'description': 'URL to include'},
                'reply_to': {'type': 'string', 'description': 'Tweet ID to reply to'},
                'require_approval': {'type': 'boolean'}
            },
            'required': ['text']
        },
        'handler': tw_post_tweet
    },
    'tw_fetch_mentions': {
        'name': 'tw_fetch_mentions',
        'description': 'Fetch recent Twitter mentions of your account',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'limit': {'type': 'integer', 'description': 'Max mentions (default 20)'}
            }
        },
        'handler': tw_fetch_mentions
    },
    'tw_generate_weekly_summary': {
        'name': 'tw_generate_weekly_summary',
        'description': 'Generate weekly Twitter/X performance summary',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'days': {'type': 'integer', 'description': 'Period (default 7)'}
            }
        },
        'handler': tw_generate_weekly_summary
    },
    'generate_all_summaries': {
        'name': 'generate_all_summaries',
        'description': 'Generate combined social media summary across all platforms for CEO briefing',
        'inputSchema': {
            'type': 'object',
            'properties': {
                'days': {'type': 'integer', 'description': 'Period (default 7)'}
            }
        },
        'handler': generate_all_summaries
    },
}


# ========== MCP Server ==========

class SocialMCPServer:
    """MCP Server for social media integration."""

    def __init__(self):
        logger.info(f"Initializing {MCP_SERVER_NAME} v{MCP_SERVER_VERSION}")
        platforms = config.get_configured_platforms()
        logger.info(f"Configured platforms: {platforms or 'none'}")

    async def handle_request(self, request: Dict) -> Dict:
        method = request.get('method')
        params = request.get('params', {})
        rid = request.get('id')

        try:
            if method == 'initialize':
                return self._ok(rid, {
                    'protocolVersion': '2024-11-05',
                    'capabilities': {'tools': {}},
                    'serverInfo': {
                        'name': MCP_SERVER_NAME,
                        'version': MCP_SERVER_VERSION,
                        'description': MCP_SERVER_DESCRIPTION,
                    }
                })

            elif method == 'notifications/initialized':
                return self._ok(rid, {})

            elif method == 'tools/list':
                return self._ok(rid, {'tools': [
                    {'name': t['name'], 'description': t['description'], 'inputSchema': t['inputSchema']}
                    for t in TOOLS.values()
                ]})

            elif method == 'tools/call':
                tool_name = params.get('name')
                tool_args = params.get('arguments', {})

                if tool_name not in TOOLS:
                    return self._err(rid, f"Unknown tool: {tool_name}", -32601)

                result = await TOOLS[tool_name]['handler'](tool_args)
                return self._ok(rid, {
                    'content': [{'type': 'text', 'text': json.dumps(result, indent=2, default=str)}]
                })

            else:
                return self._err(rid, f"Unknown method: {method}", -32601)

        except Exception as e:
            logger.error(f"Error: {e}")
            return self._err(rid, str(e), -32603)

    def _ok(self, rid, result):
        return {'jsonrpc': '2.0', 'id': rid, 'result': result}

    def _err(self, rid, msg, code):
        return {'jsonrpc': '2.0', 'id': rid, 'error': {'code': code, 'message': msg}}

    async def run_stdio(self):
        logger.info("Social MCP server started (stdio)")

        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)

        wt, wp = await asyncio.get_event_loop().connect_write_pipe(
            asyncio.streams.FlowControlMixin, sys.stdout
        )
        writer = asyncio.StreamWriter(wt, wp, reader, asyncio.get_event_loop())

        while True:
            try:
                line = await reader.readline()
                if not line:
                    break
                request = json.loads(line.decode())
                response = await self.handle_request(request)
                writer.write((json.dumps(response) + '\n').encode())
                await writer.drain()
            except json.JSONDecodeError as e:
                logger.error(f"JSON error: {e}")
            except Exception as e:
                logger.error(f"Loop error: {e}")
                break

        logger.info("Social MCP server shutting down")


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Social Media MCP Server')
    parser.add_argument('--test', action='store_true', help='Check configured platforms')
    parser.add_argument('--tool', type=str, help='Test specific tool')
    args = parser.parse_args()

    if args.test:
        valid, msg = config.validate()
        print(f"Status: {msg}")
        print(f"Platforms: {config.get_configured_platforms() or 'None configured'}")
        print(f"Approval required: {config.require_approval}")
    elif args.tool:
        if args.tool not in TOOLS:
            print(f"Unknown tool. Available: {', '.join(TOOLS.keys())}")
            return
        result = asyncio.run(TOOLS[args.tool]['handler']({}))
        print(json.dumps(result, indent=2, default=str))
    else:
        server = SocialMCPServer()
        asyncio.run(server.run_stdio())


if __name__ == '__main__':
    main()
