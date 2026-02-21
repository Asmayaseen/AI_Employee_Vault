"""
Twitter/X Adapter

Handles Twitter API v2 integration for posting, DMs, and notifications.
"""

import logging
import aiohttp
import hashlib
import hmac
import base64
import time
import urllib.parse
from typing import Dict, List, Optional
from datetime import datetime

from .base import (
    BaseSocialAdapter, Platform, PostResult,
    Message, Notification, Analytics
)

import sys
sys.path.append('..')
from config import config

logger = logging.getLogger('TwitterAdapter')


class TwitterAdapter(BaseSocialAdapter):
    """
    Twitter API v2 adapter.

    Supports:
    - Tweet posting (text, media)
    - Direct messages
    - Mentions and notifications
    - Basic analytics

    Requires Twitter Developer Account with Elevated access for full features.
    """

    # Character limits
    MAX_TWEET_LENGTH = 280
    MAX_DM_LENGTH = 10000

    def __init__(self):
        """Initialize Twitter adapter."""
        super().__init__(Platform.TWITTER)
        self.config = config.twitter
        self.base_url = self.config.api_base_url
        self._session: Optional[aiohttp.ClientSession] = None
        self._user_id: Optional[str] = None
        self._username: Optional[str] = None

    @property
    def is_configured(self) -> bool:
        """Check if Twitter is configured."""
        return self.config.is_configured

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create HTTP session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    def _get_oauth_header(self, method: str, url: str, params: Dict = None) -> str:
        """Generate OAuth 1.0a authorization header."""
        oauth_params = {
            'oauth_consumer_key': self.config.api_key,
            'oauth_token': self.config.access_token,
            'oauth_signature_method': 'HMAC-SHA1',
            'oauth_timestamp': str(int(time.time())),
            'oauth_nonce': hashlib.md5(str(time.time()).encode()).hexdigest(),
            'oauth_version': '1.0'
        }

        # Combine all params for signature
        all_params = {**oauth_params}
        if params:
            all_params.update(params)

        # Create signature base string
        sorted_params = sorted(all_params.items())
        param_string = '&'.join(f"{k}={urllib.parse.quote(str(v), safe='')}"
                                for k, v in sorted_params)

        base_string = f"{method}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(param_string, safe='')}"

        # Create signing key
        signing_key = f"{urllib.parse.quote(self.config.api_secret, safe='')}&{urllib.parse.quote(self.config.access_secret, safe='')}"

        # Generate signature
        signature = base64.b64encode(
            hmac.new(
                signing_key.encode(),
                base_string.encode(),
                hashlib.sha1
            ).digest()
        ).decode()

        oauth_params['oauth_signature'] = signature

        # Build header
        header_params = ', '.join(
            f'{k}="{urllib.parse.quote(str(v), safe="")}"'
            for k, v in sorted(oauth_params.items())
        )

        return f"OAuth {header_params}"

    async def _api_call(self, endpoint: str, method: str = 'GET',
                        params: Dict = None, data: Dict = None,
                        use_bearer: bool = False) -> Dict:
        """Make Twitter API v2 call."""
        session = await self._get_session()
        url = f"{self.base_url}/{endpoint}"

        headers = {}
        if use_bearer:
            headers['Authorization'] = f"Bearer {self.config.bearer_token}"
        else:
            headers['Authorization'] = self._get_oauth_header(method, url, params)

        headers['Content-Type'] = 'application/json'

        try:
            if method == 'GET':
                async with session.get(url, headers=headers, params=params) as resp:
                    return await resp.json()
            elif method == 'POST':
                async with session.post(url, headers=headers, json=data) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error(f"API call failed: {e}")
            return {'errors': [{'message': str(e)}]}

    async def authenticate(self) -> bool:
        """Test authentication by getting current user."""
        if not self.is_configured:
            return False

        # users/me requires OAuth 1.0a User Context, not App-only Bearer token
        result = await self._api_call('users/me', use_bearer=False)

        if 'errors' in result:
            logger.error(f"Authentication failed: {result['errors']}")
            return False

        user_data = result.get('data', {})
        self._user_id = user_data.get('id')
        self._username = user_data.get('username', '')
        logger.info(f"Authenticated as: @{self._username} (id={self._user_id})")
        return bool(self._user_id)

    async def post_content(
        self,
        text: str,
        media: List[Dict] = None,
        link: str = None,
        hashtags: List[str] = None,
        **kwargs
    ) -> PostResult:
        """
        Post a tweet.

        Args:
            text: Tweet text
            media: List of media (requires media upload - simplified here)
            link: URL to include (counts toward character limit)
            hashtags: Hashtags to append
            reply_to: Tweet ID to reply to
        """
        if not self.is_configured:
            return PostResult(
                success=False,
                platform='twitter',
                error='Twitter not configured'
            )

        # Build tweet content
        content = text

        # Add link
        if link:
            content = f"{content} {link}"

        # Add hashtags (if room)
        if hashtags:
            hashtag_str = self._format_hashtags(hashtags)
            if len(content) + len(hashtag_str) + 1 <= self.MAX_TWEET_LENGTH:
                content = f"{content} {hashtag_str}"

        content = self._truncate_text(content, self.MAX_TWEET_LENGTH)

        try:
            tweet_data = {'text': content}

            # Handle reply
            reply_to = kwargs.get('reply_to')
            if reply_to:
                tweet_data['reply'] = {'in_reply_to_tweet_id': reply_to}

            result = await self._api_call('tweets', method='POST', data=tweet_data)

            if 'errors' in result:
                return PostResult(
                    success=False,
                    platform='twitter',
                    error=result['errors'][0].get('message', 'Unknown error')
                )

            tweet_data = result.get('data', {})
            tweet_id = tweet_data.get('id')
            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}" if tweet_id else None

            logger.info(f"Posted tweet: {tweet_id}")

            return PostResult(
                success=True,
                platform='twitter',
                post_id=tweet_id,
                url=tweet_url
            )

        except Exception as e:
            logger.error(f"Tweet failed: {e}")
            return PostResult(
                success=False,
                platform='twitter',
                error=str(e)
            )

    async def read_messages(
        self,
        unread_only: bool = True,
        since: str = None,
        limit: int = 50
    ) -> List[Message]:
        """Read Twitter Direct Messages."""
        if not self.is_configured:
            return []

        messages = []

        try:
            # Get DM events
            params = {'dm_event.fields': 'text,sender_id,created_at'}
            if limit:
                params['max_results'] = min(limit, 100)

            # dm_events requires OAuth 1.0a User Context, not App-only Bearer token
            result = await self._api_call('dm_events', params=params, use_bearer=False)

            if 'errors' in result:
                logger.error(f"Error reading DMs: {result['errors']}")
                return []

            for dm in result.get('data', []):
                messages.append(Message(
                    id=dm.get('id', ''),
                    platform='twitter',
                    sender_id=dm.get('sender_id', ''),
                    sender_name='Twitter User',  # Would need user lookup
                    sender_username='',
                    content=dm.get('text', ''),
                    timestamp=dm.get('created_at', ''),
                    is_read=False
                ))

            logger.info(f"Retrieved {len(messages)} Twitter DMs")

        except Exception as e:
            logger.error(f"Error reading DMs: {e}")

        return messages[:limit]

    async def fetch_notifications(
        self,
        types: List[str] = None,
        since: str = None,
        limit: int = 50
    ) -> List[Notification]:
        """Fetch Twitter mentions and interactions."""
        if not self.is_configured:
            return []

        notifications = []

        try:
            # Get user ID if not cached
            if not self._user_id:
                await self.authenticate()

            if not self._user_id:
                return []

            # Get mentions
            params = {
                'tweet.fields': 'author_id,created_at,text',
                'max_results': min(limit, 100)
            }

            result = await self._api_call(
                f"users/{self._user_id}/mentions",
                params=params,
                use_bearer=True
            )

            if 'errors' in result:
                logger.error(f"Error fetching mentions: {result['errors']}")
                return []

            for tweet in result.get('data', []):
                notifications.append(Notification(
                    id=tweet.get('id', ''),
                    platform='twitter',
                    type='mention',
                    actor_id=tweet.get('author_id', ''),
                    actor_name='Twitter User',
                    actor_username='',
                    content=tweet.get('text', ''),
                    timestamp=tweet.get('created_at', ''),
                    url=f"https://twitter.com/i/web/status/{tweet.get('id')}"
                ))

            # Filter by types
            if types:
                notifications = [n for n in notifications if n.type in types]

            logger.info(f"Retrieved {len(notifications)} Twitter notifications")

        except Exception as e:
            logger.error(f"Error fetching notifications: {e}")

        return notifications[:limit]

    async def get_analytics(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> Analytics:
        """Get Twitter analytics."""
        analytics = Analytics(platform='twitter')

        if not self.is_configured:
            return analytics

        try:
            # Get user info
            # users/me requires OAuth 1.0a User Context, not App-only Bearer token
            result = await self._api_call(
                'users/me',
                params={'user.fields': 'public_metrics'},
                use_bearer=False
            )

            if 'data' in result:
                user_data = result['data']
                metrics = user_data.get('public_metrics', {})
                analytics.followers = metrics.get('followers_count', 0)

            # Twitter API v2 doesn't provide impressions/reach without Analytics API
            # which requires additional permissions

            logger.info(f"Retrieved Twitter analytics: {analytics.followers} followers")

        except Exception as e:
            logger.error(f"Error getting analytics: {e}")

        return analytics

    async def close(self):
        """Close HTTP session."""
        if self._session and not self._session.closed:
            await self._session.close()
