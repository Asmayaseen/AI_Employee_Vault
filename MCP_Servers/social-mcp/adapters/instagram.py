"""
Instagram Adapter

Handles Instagram Graph API integration via Meta Business Suite.
"""

import logging
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime

from .base import (
    BaseSocialAdapter, Platform, PostResult,
    Message, Notification, Analytics
)

import sys
sys.path.append('..')
from config import config

logger = logging.getLogger('InstagramAdapter')


class InstagramAdapter(BaseSocialAdapter):
    """
    Instagram Graph API adapter (via Meta).

    Supports:
    - Feed posting (images, carousels)
    - Direct message inbox
    - Comment/mention notifications
    - Basic analytics

    Note: Requires Instagram Business/Creator account connected to Facebook Page.
    """

    # Character limits
    MAX_CAPTION_LENGTH = 2200
    MAX_HASHTAGS = 30

    def __init__(self):
        """Initialize Instagram adapter."""
        super().__init__(Platform.INSTAGRAM)
        self.config = config.instagram
        self.base_url = self.config.api_base_url
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def is_configured(self) -> bool:
        """Check if Instagram is configured."""
        return self.config.is_configured

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _api_call(self, endpoint: str, method: str = 'GET',
                        params: Dict = None, data: Dict = None) -> Dict:
        """Make Instagram Graph API call."""
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint}"

        if params is None:
            params = {}
        params['access_token'] = self.config.access_token

        try:
            if method == 'GET':
                async with session.get(url, params=params) as resp:
                    return await resp.json()
            elif method == 'POST':
                async with session.post(url, params=params, json=data) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return {'error': {'message': str(e)}}

    async def authenticate(self) -> bool:
        """Test authentication by getting account info."""
        if not self.is_configured:
            return False

        result = await self._api_call(
            self.config.business_id,
            params={'fields': 'id,username'}
        )

        if 'error' in result:
            logger.error(f"Authentication failed: {result['error']}")
            return False

        logger.info(f"Authenticated as: @{result.get('username')}")
        return True

    async def post_content(
        self,
        text: str,
        media: List[Dict] = None,
        link: str = None,
        hashtags: List[str] = None,
        **kwargs
    ) -> PostResult:
        """
        Post content to Instagram.

        Note: Instagram requires media for feed posts.
        For text-only content, consider using Stories (requires different API).

        Args:
            text: Caption text
            media: Required - at least one image
            link: Ignored (Instagram doesn't support links in posts)
            hashtags: Hashtags to append
            post_type: 'feed', 'story', or 'reel' (default: feed)
        """
        if not self.is_configured:
            return PostResult(
                success=False,
                platform='instagram',
                error='Instagram not configured'
            )

        # Instagram requires media
        if not media or len(media) == 0:
            return PostResult(
                success=False,
                platform='instagram',
                error='Instagram posts require at least one image'
            )

        # Build caption
        caption = text
        if hashtags:
            # Limit hashtags
            limited_hashtags = hashtags[:self.MAX_HASHTAGS]
            caption = f"{caption}\n\n{self._format_hashtags(limited_hashtags)}"

        caption = self._truncate_text(caption, self.MAX_CAPTION_LENGTH)

        try:
            ig_user_id = self.config.business_id

            # Step 1: Create media container
            media_url = media[0].get('url')
            container_params = {
                'image_url': media_url,
                'caption': caption
            }

            container_result = await self._api_call(
                f"{ig_user_id}/media",
                method='POST',
                data=container_params
            )

            if 'error' in container_result:
                return PostResult(
                    success=False,
                    platform='instagram',
                    error=container_result['error'].get('message', 'Container creation failed')
                )

            container_id = container_result.get('id')

            # Step 2: Publish the container
            publish_result = await self._api_call(
                f"{ig_user_id}/media_publish",
                method='POST',
                data={'creation_id': container_id}
            )

            if 'error' in publish_result:
                return PostResult(
                    success=False,
                    platform='instagram',
                    error=publish_result['error'].get('message', 'Publish failed')
                )

            post_id = publish_result.get('id')

            # Get permalink
            permalink_result = await self._api_call(
                post_id,
                params={'fields': 'permalink'}
            )
            post_url = permalink_result.get('permalink')

            logger.info(f"Posted to Instagram: {post_id}")

            return PostResult(
                success=True,
                platform='instagram',
                post_id=post_id,
                url=post_url
            )

        except Exception as e:
            logger.error(f"Post failed: {e}")
            return PostResult(
                success=False,
                platform='instagram',
                error=str(e)
            )

    async def read_messages(
        self,
        unread_only: bool = True,
        since: str = None,
        limit: int = 50
    ) -> List[Message]:
        """Read Instagram Direct messages."""
        if not self.is_configured:
            return []

        messages = []
        ig_user_id = self.config.business_id

        try:
            # Get conversations
            params = {
                'fields': 'participants,messages{message,from,timestamp}',
                'limit': limit
            }

            result = await self._api_call(f"{ig_user_id}/conversations", params=params)

            if 'error' in result:
                logger.error(f"Error reading messages: {result['error']}")
                return []

            for conv in result.get('data', []):
                for msg_data in conv.get('messages', {}).get('data', []):
                    sender = msg_data.get('from', {})
                    messages.append(Message(
                        id=msg_data.get('id', ''),
                        platform='instagram',
                        sender_id=sender.get('id', ''),
                        sender_name=sender.get('username', 'Unknown'),
                        sender_username=sender.get('username', ''),
                        content=msg_data.get('message', ''),
                        timestamp=msg_data.get('timestamp', ''),
                        is_read=False  # Instagram API doesn't expose read status easily
                    ))

            logger.info(f"Retrieved {len(messages)} Instagram messages")

        except Exception as e:
            logger.error(f"Error reading messages: {e}")

        return messages[:limit]

    async def fetch_notifications(
        self,
        types: List[str] = None,
        since: str = None,
        limit: int = 50
    ) -> List[Notification]:
        """Fetch Instagram notifications (comments, mentions)."""
        if not self.is_configured:
            return []

        notifications = []
        ig_user_id = self.config.business_id

        try:
            # Get recent media with comments
            params = {
                'fields': 'id,caption,comments{from,text,timestamp}',
                'limit': 10
            }

            result = await self._api_call(f"{ig_user_id}/media", params=params)

            if 'error' in result:
                logger.error(f"Error fetching notifications: {result['error']}")
                return []

            for post in result.get('data', []):
                post_id = post.get('id', '')

                # Process comments
                for comment in post.get('comments', {}).get('data', []):
                    sender = comment.get('from', {})
                    notifications.append(Notification(
                        id=comment.get('id', ''),
                        platform='instagram',
                        type='comment',
                        actor_id=sender.get('id', ''),
                        actor_name=sender.get('username', 'Unknown'),
                        actor_username=sender.get('username', ''),
                        content=comment.get('text', ''),
                        target_post_id=post_id,
                        timestamp=comment.get('timestamp', '')
                    ))

            # Get mentions
            mentions_result = await self._api_call(
                f"{ig_user_id}/tags",
                params={'fields': 'id,caption,permalink,timestamp'}
            )

            if 'data' in mentions_result:
                for mention in mentions_result['data']:
                    notifications.append(Notification(
                        id=mention.get('id', ''),
                        platform='instagram',
                        type='mention',
                        actor_id='',
                        actor_name='Someone',
                        actor_username='',
                        content=mention.get('caption', 'Mentioned you'),
                        url=mention.get('permalink'),
                        timestamp=mention.get('timestamp', '')
                    ))

            # Filter by types
            if types:
                notifications = [n for n in notifications if n.type in types]

            logger.info(f"Retrieved {len(notifications)} Instagram notifications")

        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")

        return notifications[:limit]

    async def get_analytics(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> Analytics:
        """Get Instagram analytics."""
        analytics = Analytics(platform='instagram')

        if not self.is_configured:
            return analytics

        ig_user_id = self.config.business_id

        try:
            # Get basic metrics
            params = {'fields': 'followers_count,media_count'}
            result = await self._api_call(ig_user_id, params=params)

            if 'error' not in result:
                analytics.followers = result.get('followers_count', 0)

            # Get insights (requires business account)
            insights_params = {
                'metric': 'impressions,reach',
                'period': 'day'
            }
            insights = await self._api_call(f"{ig_user_id}/insights", params=insights_params)

            if 'data' in insights:
                for metric in insights['data']:
                    name = metric.get('name', '')
                    values = metric.get('values', [])
                    if values:
                        value = values[-1].get('value', 0)
                        if name == 'impressions':
                            analytics.impressions = value
                        elif name == 'reach':
                            analytics.reach = value

            # Calculate engagement rate
            if analytics.impressions > 0:
                analytics.engagement_rate = (analytics.reach / analytics.impressions) * 100

            logger.info(f"Retrieved Instagram analytics: {analytics.followers} followers")

        except Exception as e:
            logger.error(f"Error getting analytics: {e}")

        return analytics

    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
