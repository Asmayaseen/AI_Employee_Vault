"""
Social Media Platform Adapters

This package contains adapters for different social media platforms.
"""

from .base import BaseSocialAdapter, PostResult, Message, Notification
from .facebook import FacebookAdapter
from .instagram import InstagramAdapter
from .twitter import TwitterAdapter

__all__ = [
    'BaseSocialAdapter',
    'PostResult',
    'Message',
    'Notification',
    'FacebookAdapter',
    'InstagramAdapter',
    'TwitterAdapter'
]
