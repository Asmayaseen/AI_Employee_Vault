"""
Social MCP Server Configuration

Configuration management for Facebook, Instagram, and Twitter integrations.
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class FacebookConfig:
    """Facebook/Meta configuration."""
    app_id: str = os.getenv('META_APP_ID', '')
    app_secret: str = os.getenv('META_APP_SECRET', '')
    access_token: str = os.getenv('META_ACCESS_TOKEN', '')
    page_id: str = os.getenv('FACEBOOK_PAGE_ID', '')
    page_token: str = os.getenv('FACEBOOK_PAGE_TOKEN', '')

    @property
    def is_configured(self) -> bool:
        return bool(self.page_token or self.access_token)

    @property
    def api_base_url(self) -> str:
        return "https://graph.facebook.com/v18.0"


@dataclass
class InstagramConfig:
    """Instagram configuration (via Meta Graph API)."""
    business_id: str = os.getenv('INSTAGRAM_BUSINESS_ID', '')
    access_token: str = os.getenv('META_ACCESS_TOKEN', '')  # Shared with Facebook

    @property
    def is_configured(self) -> bool:
        return bool(self.business_id and self.access_token)

    @property
    def api_base_url(self) -> str:
        return "https://graph.facebook.com/v18.0"


@dataclass
class TwitterConfig:
    """Twitter/X configuration."""
    api_key: str = os.getenv('TWITTER_API_KEY', '')
    api_secret: str = os.getenv('TWITTER_API_SECRET', '')
    access_token: str = os.getenv('TWITTER_ACCESS_TOKEN', '')
    access_secret: str = os.getenv('TWITTER_ACCESS_SECRET', '')
    bearer_token: str = os.getenv('TWITTER_BEARER_TOKEN', '')

    @property
    def is_configured(self) -> bool:
        return bool(self.bearer_token or (self.api_key and self.access_token))

    @property
    def api_base_url(self) -> str:
        return "https://api.twitter.com/2"


@dataclass
class SocialConfig:
    """Main social media configuration."""
    facebook: FacebookConfig = field(default_factory=FacebookConfig)
    instagram: InstagramConfig = field(default_factory=InstagramConfig)
    twitter: TwitterConfig = field(default_factory=TwitterConfig)

    # Rate limiting
    post_cooldown_minutes: int = int(os.getenv('SOCIAL_POST_COOLDOWN', '5'))

    # Approval settings
    require_approval: bool = os.getenv('SOCIAL_REQUIRE_APPROVAL', 'true').lower() == 'true'

    def get_configured_platforms(self) -> List[str]:
        """Get list of configured platforms."""
        platforms = []
        if self.facebook.is_configured:
            platforms.append('facebook')
        if self.instagram.is_configured:
            platforms.append('instagram')
        if self.twitter.is_configured:
            platforms.append('twitter')
        return platforms

    def validate(self) -> tuple[bool, str]:
        """Validate at least one platform is configured."""
        platforms = self.get_configured_platforms()
        if not platforms:
            return False, "No social platforms configured. Set API credentials in .env"
        return True, f"Configured platforms: {', '.join(platforms)}"


# Global configuration instance
config = SocialConfig()

# MCP Server settings
MCP_SERVER_NAME = "social-mcp"
MCP_SERVER_VERSION = "1.0.0"
MCP_SERVER_DESCRIPTION = "Social media integration for AI Employee"

# Logging
LOG_LEVEL = os.getenv('SOCIAL_LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('SOCIAL_LOG_FILE', '/mnt/d/Ai-Employee/AI_Employee_Vault/Logs/social_mcp.log')

# Vault path for storing scheduled posts
VAULT_PATH = os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault')
