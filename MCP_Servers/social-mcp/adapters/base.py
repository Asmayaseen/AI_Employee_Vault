"""
Base Social Media Adapter

Abstract base class for all social media platform adapters.
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime
from enum import Enum

logger = logging.getLogger('SocialAdapter')


class Platform(Enum):
    """Supported social media platforms."""
    FACEBOOK = 'facebook'
    INSTAGRAM = 'instagram'
    TWITTER = 'twitter'


@dataclass
class PostResult:
    """Result of a post operation."""
    success: bool
    platform: str
    post_id: Optional[str] = None
    url: Optional[str] = None
    error: Optional[str] = None
    scheduled_time: Optional[str] = None


@dataclass
class Message:
    """Social media direct message."""
    id: str
    platform: str
    sender_id: str
    sender_name: str
    sender_username: str
    content: str
    timestamp: str
    is_read: bool = False
    attachments: List[Dict] = field(default_factory=list)


@dataclass
class Notification:
    """Social media notification."""
    id: str
    platform: str
    type: str  # mention, like, comment, share, follow
    actor_id: str
    actor_name: str
    actor_username: str
    content: str
    target_post_id: Optional[str] = None
    timestamp: str = ""
    url: Optional[str] = None


@dataclass
class Analytics:
    """Platform analytics data."""
    platform: str
    followers: int = 0
    followers_change: int = 0
    impressions: int = 0
    reach: int = 0
    engagement_rate: float = 0.0
    top_post: Optional[Dict] = None


class BaseSocialAdapter(ABC):
    """
    Abstract base class for social media adapters.

    All platform-specific adapters must inherit from this class
    and implement the abstract methods.
    """

    def __init__(self, platform: Platform):
        """Initialize adapter."""
        self.platform = platform
        self.logger = logging.getLogger(f'SocialAdapter.{platform.value}')

    @property
    @abstractmethod
    def is_configured(self) -> bool:
        """Check if adapter is properly configured."""
        pass

    @abstractmethod
    async def authenticate(self) -> bool:
        """Authenticate with the platform."""
        pass

    @abstractmethod
    async def post_content(
        self,
        text: str,
        media: List[Dict] = None,
        link: str = None,
        hashtags: List[str] = None,
        **kwargs
    ) -> PostResult:
        """
        Post content to the platform.

        Args:
            text: Post text content
            media: List of media attachments (images/videos)
            link: URL to include
            hashtags: List of hashtags
            **kwargs: Platform-specific options

        Returns:
            PostResult with success status and details
        """
        pass

    @abstractmethod
    async def read_messages(
        self,
        unread_only: bool = True,
        since: str = None,
        limit: int = 50
    ) -> List[Message]:
        """
        Read direct messages.

        Args:
            unread_only: Only return unread messages
            since: ISO timestamp to filter from
            limit: Maximum messages to return

        Returns:
            List of Message objects
        """
        pass

    @abstractmethod
    async def fetch_notifications(
        self,
        types: List[str] = None,
        since: str = None,
        limit: int = 50
    ) -> List[Notification]:
        """
        Fetch notifications (mentions, likes, comments, etc.).

        Args:
            types: Filter by notification types
            since: ISO timestamp to filter from
            limit: Maximum notifications to return

        Returns:
            List of Notification objects
        """
        pass

    @abstractmethod
    async def get_analytics(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> Analytics:
        """
        Get platform analytics.

        Args:
            start_date: Start of analytics period
            end_date: End of analytics period

        Returns:
            Analytics object with metrics
        """
        pass

    def _format_hashtags(self, hashtags: List[str]) -> str:
        """Format hashtags for inclusion in post."""
        if not hashtags:
            return ""
        formatted = []
        for tag in hashtags:
            tag = tag.strip()
            if not tag.startswith('#'):
                tag = f"#{tag}"
            formatted.append(tag)
        return " ".join(formatted)

    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to platform limit."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
