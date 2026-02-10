"""
Facebook Adapter

Handles Facebook Graph API integration for page posting and messaging.
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

logger = logging.getLogger('FacebookAdapter')


class FacebookAdapter(BaseSocialAdapter):
    """
    Facebook Graph API adapter.

    Supports:
    - Page posting (text, images, links)
    - Page message inbox
    - Notifications (comments, reactions)
    - Basic analytics
    """

    # Character limits
    MAX_POST_LENGTH = 63206  # Facebook allows very long posts

    def __init__(self):
        """Initialize Facebook adapter."""
        super().__init__(Platform.FACEBOOK)
        self.config = config.facebook
        self.base_url = self.config.api_base_url
        self._session: Optional[aiohttp.ClientSession] = None

    @property
    def is_configured(self) -> bool:
        """Check if Facebook is configured."""
        return self.config.is_configured

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def _api_call(self, endpoint: str, method: str = 'GET',
                        params: Dict = None, data: Dict = None) -> Dict:
        """Make Facebook Graph API call."""
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint}"

        # Add access token
        if params is None:
            params = {}
        params['access_token'] = self.config.page_token or self.config.access_token

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
        """Test authentication by getting page info."""
        if not self.is_configured:
            return False

        result = await self._api_call('me', params={'fields': 'id,name'})
        if 'error' in result:
            logger.error(f"Authentication failed: {result['error']}")
            return False

        logger.info(f"Authenticated as: {result.get('name')}")
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
        Post content to Facebook page.

        Args:
            text: Post text
            media: List of media (images/videos)
            link: URL to attach
            hashtags: Hashtags to append
        """
        if not self.is_configured:
            return PostResult(
                success=False,
                platform='facebook',
                error='Facebook not configured'
            )

        # Build post content
        content = text
        if hashtags:
            content = f"{content}\n\n{self._format_hashtags(hashtags)}"

        content = self._truncate_text(content, self.MAX_POST_LENGTH)

        # Determine endpoint and data
        page_id = self.config.page_id or 'me'
        endpoint = f"{page_id}/feed"
        post_data = {'message': content}

        if link:
            post_data['link'] = link

        # Handle media
        if media and len(media) > 0:
            # For single image, use photos endpoint
            first_media = media[0]
            if first_media.get('type') == 'image':
                endpoint = f"{page_id}/photos"
                post_data['url'] = first_media.get('url')
                if first_media.get('alt_text'):
                    post_data['caption'] = content
                    del post_data['message']

        try:
            result = await self._api_call(endpoint, method='POST', data=post_data)

            if 'error' in result:
                return PostResult(
                    success=False,
                    platform='facebook',
                    error=result['error'].get('message', 'Unknown error')
                )

            post_id = result.get('id') or result.get('post_id')
            post_url = f"https://facebook.com/{post_id}" if post_id else None

            logger.info(f"Posted to Facebook: {post_id}")

            return PostResult(
                success=True,
                platform='facebook',
                post_id=post_id,
                url=post_url
            )

        except Exception as e:
            logger.error(f"Post failed: {e}")
            return PostResult(
                success=False,
                platform='facebook',
                error=str(e)
            )

    async def read_messages(
        self,
        unread_only: bool = True,
        since: str = None,
        limit: int = 50
    ) -> List[Message]:
        """Read Facebook Page inbox messages."""
        if not self.is_configured:
            return []

        messages = []
        page_id = self.config.page_id or 'me'

        try:
            # Get conversations
            params = {
                'fields': 'participants,messages{message,from,created_time,is_read}',
                'limit': limit
            }

            result = await self._api_call(f"{page_id}/conversations", params=params)

            if 'error' in result:
                logger.error(f"Error reading messages: {result['error']}")
                return []

            for conv in result.get('data', []):
                for msg_data in conv.get('messages', {}).get('data', []):
                    is_read = msg_data.get('is_read', True)

                    if unread_only and is_read:
                        continue

                    sender = msg_data.get('from', {})
                    messages.append(Message(
                        id=msg_data.get('id', ''),
                        platform='facebook',
                        sender_id=sender.get('id', ''),
                        sender_name=sender.get('name', 'Unknown'),
                        sender_username=sender.get('id', ''),
                        content=msg_data.get('message', ''),
                        timestamp=msg_data.get('created_time', ''),
                        is_read=is_read
                    ))

            logger.info(f"Retrieved {len(messages)} Facebook messages")

        except Exception as e:
            logger.error(f"Error reading messages: {e}")

        return messages[:limit]

    async def fetch_notifications(
        self,
        types: List[str] = None,
        since: str = None,
        limit: int = 50
    ) -> List[Notification]:
        """Fetch Facebook notifications (comments, reactions on page posts)."""
        if not self.is_configured:
            return []

        notifications = []
        page_id = self.config.page_id or 'me'

        try:
            # Get recent posts with their comments and reactions
            params = {
                'fields': 'id,message,comments{from,message,created_time},reactions{name,type}',
                'limit': 10
            }

            result = await self._api_call(f"{page_id}/posts", params=params)

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
                        platform='facebook',
                        type='comment',
                        actor_id=sender.get('id', ''),
                        actor_name=sender.get('name', 'Unknown'),
                        actor_username=sender.get('id', ''),
                        content=comment.get('message', ''),
                        target_post_id=post_id,
                        timestamp=comment.get('created_time', '')
                    ))

                # Process reactions
                for reaction in post.get('reactions', {}).get('data', []):
                    notifications.append(Notification(
                        id=f"{post_id}_{reaction.get('name', '')}",
                        platform='facebook',
                        type='like',
                        actor_id='',
                        actor_name=reaction.get('name', 'Someone'),
                        actor_username='',
                        content=f"Reacted with {reaction.get('type', 'LIKE')}",
                        target_post_id=post_id
                    ))

            # Filter by types if specified
            if types:
                notifications = [n for n in notifications if n.type in types]

            logger.info(f"Retrieved {len(notifications)} Facebook notifications")

        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")

        return notifications[:limit]

    async def get_analytics(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> Analytics:
        """Get Facebook page analytics."""
        analytics = Analytics(platform='facebook')

        if not self.is_configured:
            return analytics

        page_id = self.config.page_id or 'me'

        try:
            # Get page info
            params = {'fields': 'followers_count,fan_count'}
            result = await self._api_call(page_id, params=params)

            if 'error' not in result:
                analytics.followers = result.get('followers_count', 0) or result.get('fan_count', 0)

            # Get page insights (requires page insights permission)
            insights_params = {
                'metric': 'page_impressions,page_engaged_users',
                'period': 'day'
            }
            insights = await self._api_call(f"{page_id}/insights", params=insights_params)

            if 'data' in insights:
                for metric in insights['data']:
                    name = metric.get('name', '')
                    values = metric.get('values', [])
                    if values:
                        value = values[-1].get('value', 0)
                        if name == 'page_impressions':
                            analytics.impressions = value
                        elif name == 'page_engaged_users':
                            analytics.reach = value

            # Calculate engagement rate
            if analytics.impressions > 0:
                analytics.engagement_rate = (analytics.reach / analytics.impressions) * 100

            logger.info(f"Retrieved Facebook analytics: {analytics.followers} followers")

        except Exception as e:
            logger.error(f"Error getting analytics: {e}")

        return analytics

    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
