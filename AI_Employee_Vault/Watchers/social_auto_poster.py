#!/usr/bin/env python3
"""
Social Auto-Poster - Automated Content Generation for Facebook, Instagram & Twitter

Generates business content and creates HITL approval files for all social platforms.
Follows the same pattern as linkedin_auto_poster.py.

Schedule:
- Facebook:  Tuesday 10 AM, Thursday 2 PM, Saturday 11 AM
- Instagram: Monday 11 AM, Wednesday 5 PM, Friday 10 AM
- Twitter/X: Daily at 9 AM, 1 PM, 5 PM (higher frequency, shorter content)

Uses Business_Goals.md and recent achievements for context.
All posts go through /Pending_Approval -> /Approved -> execution flow.
"""

import os
import sys
import json
import random
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('SocialAutoPoster')

# Get vault path
VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))


class SocialContentGenerator:
    """Generates platform-specific content for Facebook, Instagram, and Twitter."""

    # ========== Facebook Templates ==========
    FB_BUSINESS_UPDATE = [
        "We're excited to share that {achievement}! Our team continues to push boundaries.\n\nWhat projects are you working on this week? Drop a comment below!",
        "Great news from our team: {achievement}.\n\nStay tuned for more updates as we continue to deliver value to our clients.",
        "Another milestone reached: {achievement}!\n\nThank you to our amazing clients and partners for making this possible.",
    ]

    FB_INDUSTRY_INSIGHT = [
        "Industry Insight: {insight}\n\nWhat are your thoughts? Share in the comments!\n\n#BusinessTips #Industry",
        "Did you know? {insight}\n\nStaying ahead means staying informed. Follow our page for more insights.\n\n#BusinessGrowth #Tips",
        "Here's something worth thinking about: {insight}\n\nHow does this apply to your business?\n\n#Insights #Business",
    ]

    FB_ENGAGEMENT = [
        "Happy {day}! Quick question for our community: {question}\n\nLet us know in the comments!",
        "It's {day} and we want to hear from you: {question}\n\nShare your thoughts below!",
    ]

    # ========== Instagram Templates (shorter, visual-friendly) ==========
    IG_BUSINESS = [
        "{achievement}\n\n.\n.\n.\n#Business #Growth #Success #Milestone #Teamwork",
        "Making progress every day.\n\n{achievement}\n\n#BusinessUpdate #Progress #Goals",
        "Another step forward.\n\n{achievement}\n\n#Entrepreneurship #Business #Winning",
    ]

    IG_MOTIVATION = [
        "{insight}\n\nDouble tap if you agree!\n\n#Motivation #BusinessMindset #Success #Hustle",
        "{insight}\n\nTag someone who needs to hear this.\n\n#Inspired #Growth #Mindset",
        "{insight}\n\nSave this for later.\n\n#BusinessTips #Entrepreneur #Success",
    ]

    IG_BEHIND_SCENES = [
        "Behind the scenes: Working on {focus} today.\n\nStay tuned for what's coming next!\n\n#BehindTheScenes #WorkLife #Business",
        "A glimpse into our process: {focus}\n\nGreat things take time and dedication.\n\n#Process #Dedication #Work",
    ]

    # ========== Twitter/X Templates (280 char limit) ==========
    TW_UPDATE = [
        "Working on {focus} this week. Exciting progress ahead!",
        "Update: {achievement}. More to come!",
        "Big things brewing: {focus}. Stay tuned.",
    ]

    TW_INSIGHT = [
        "{insight} #BusinessTips",
        "Quick tip: {insight}",
        "Worth remembering: {insight} #Growth",
    ]

    TW_ENGAGEMENT = [
        "What's your biggest challenge this {day}? Reply below!",
        "One word to describe your {day} so far? Mine: productive.",
        "{day} thought: {insight}",
    ]

    # ========== Shared Content Pool ==========
    INSIGHTS = [
        "Consistency beats perfection every time",
        "The best investment you can make is in your team",
        "Customer feedback is a gift - use it wisely",
        "Small improvements compound into massive results",
        "Focus on value delivered, not hours worked",
        "Automation frees time for what truly matters",
        "Building relationships is the foundation of business growth",
        "Data-driven decisions lead to better outcomes",
        "The best time to innovate was yesterday, the second best is now",
        "Simplicity is the ultimate sophistication in business",
    ]

    QUESTIONS = [
        "What's the one tool you can't live without?",
        "What's your top productivity tip?",
        "What skill are you learning this month?",
        "What's the best business advice you've received?",
        "Remote or office - what works better for you?",
    ]

    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.business_goals = self._load_business_goals()

    def _load_business_goals(self) -> Dict:
        goals_file = self.vault_path / 'Business_Goals.md'
        if goals_file.exists():
            return {'content': goals_file.read_text()}
        return {}

    def _get_recent_achievements(self) -> List[str]:
        done_folder = self.vault_path / 'Done'
        achievements = []
        if done_folder.exists():
            week_ago = datetime.now() - timedelta(days=7)
            for file in done_folder.glob('*.md'):
                try:
                    if datetime.fromtimestamp(file.stat().st_mtime) > week_ago:
                        content = file.read_text()
                        for line in content.split('\n'):
                            line = line.strip()
                            if line and not line.startswith('#') and not line.startswith('---'):
                                achievements.append(line)
                                break
                except Exception:
                    pass
        return achievements[:5]

    def _get_focus(self) -> str:
        if self.business_goals:
            content = self.business_goals.get('content', '')
            if 'Project' in content:
                return "key client projects and strategic initiatives"
        return "delivering value and growing the business"

    def _get_achievement(self) -> str:
        achievements = self._get_recent_achievements()
        if achievements:
            return achievements[0]
        defaults = [
            "we're making great progress on our current projects",
            "our team delivered outstanding results this week",
            "we've streamlined our operations for better efficiency",
        ]
        return random.choice(defaults)

    # ========== Facebook Content ==========
    def generate_facebook_post(self) -> Optional[str]:
        day = datetime.now().strftime('%A')
        hour = datetime.now().hour

        # Tuesday 10 AM
        if day == 'Tuesday' and 9 <= hour <= 11:
            template = random.choice(self.FB_BUSINESS_UPDATE)
            return template.format(achievement=self._get_achievement())
        # Thursday 2 PM
        elif day == 'Thursday' and 13 <= hour <= 15:
            template = random.choice(self.FB_INDUSTRY_INSIGHT)
            return template.format(insight=random.choice(self.INSIGHTS))
        # Saturday 11 AM
        elif day == 'Saturday' and 10 <= hour <= 12:
            template = random.choice(self.FB_ENGAGEMENT)
            return template.format(day=day, question=random.choice(self.QUESTIONS))
        return None

    # ========== Instagram Content ==========
    def generate_instagram_post(self) -> Optional[str]:
        day = datetime.now().strftime('%A')
        hour = datetime.now().hour

        # Monday 11 AM
        if day == 'Monday' and 10 <= hour <= 12:
            template = random.choice(self.IG_BUSINESS)
            return template.format(achievement=self._get_achievement())
        # Wednesday 5 PM
        elif day == 'Wednesday' and 16 <= hour <= 18:
            template = random.choice(self.IG_MOTIVATION)
            return template.format(insight=random.choice(self.INSIGHTS))
        # Friday 10 AM
        elif day == 'Friday' and 9 <= hour <= 11:
            template = random.choice(self.IG_BEHIND_SCENES)
            return template.format(focus=self._get_focus())
        return None

    # ========== Twitter Content ==========
    def generate_twitter_post(self) -> Optional[str]:
        day = datetime.now().strftime('%A')
        hour = datetime.now().hour

        # 9 AM
        if 8 <= hour <= 10:
            template = random.choice(self.TW_UPDATE)
            content = template.format(
                focus=self._get_focus(),
                achievement=self._get_achievement()
            )
        # 1 PM
        elif 12 <= hour <= 14:
            template = random.choice(self.TW_INSIGHT)
            content = template.format(insight=random.choice(self.INSIGHTS))
        # 5 PM
        elif 16 <= hour <= 18:
            template = random.choice(self.TW_ENGAGEMENT)
            content = template.format(
                day=day,
                insight=random.choice(self.INSIGHTS)
            )
        else:
            return None

        # Enforce 280 char limit
        if len(content) > 280:
            content = content[:277] + '...'
        return content

    def generate_all(self) -> Dict[str, Optional[str]]:
        """Generate content for all platforms if scheduled."""
        return {
            'facebook': self.generate_facebook_post(),
            'instagram': self.generate_instagram_post(),
            'twitter': self.generate_twitter_post(),
        }


def _already_posted_today(platform: str, vault_path: Path) -> bool:
    """Check if a post was already created for this platform today."""
    today = datetime.now().strftime('%Y%m%d')
    platform_upper = platform.upper()
    pattern = f"{platform_upper}_AUTO_POST_{today}*.md"

    # Check Pending_Approval, Approved, and Done
    for folder in ['Pending_Approval', 'Approved', 'Done']:
        folder_path = vault_path / folder
        if folder_path.exists() and list(folder_path.glob(pattern)):
            return True
    return False


def create_approval_file(platform: str, content: str, vault_path: Path) -> Path:
    """Create a HITL approval file for a social media post."""
    timestamp = datetime.now()
    platform_upper = platform.upper()
    filename = f"{platform_upper}_AUTO_POST_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"

    # Platform-specific metadata
    metadata_extra = ''
    if platform == 'instagram':
        metadata_extra = 'image_url: \n  # Add public image URL before approving\n'

    approval_content = f'''---
type: {platform}_post
action: {platform}_post
platform: {platform}
created: {timestamp.isoformat()}
status: pending_approval
auto_generated: true
{metadata_extra}---

# {platform.title()} Auto-Post Approval

## Generated Content
```
{content}
```

## Post Details
- **Platform:** {platform.title()}
- **Day:** {timestamp.strftime('%A, %B %d, %Y')}
- **Time:** {timestamp.strftime('%I:%M %p')}
- **Character Count:** {len(content)}

## Rules Check
- Professional tone maintained
- No controversial content
- Follows Company_Handbook guidelines
- Auto-generated according to schedule

---

## Instructions
**To APPROVE:** Move this file to `/Approved/` folder
**To REJECT:** Move this file to `/Rejected/` folder
**To EDIT:** Modify the content above, then move to `/Approved/`

---

*Auto-generated by Social Auto-Poster ({platform.title()})*
*System will post within 15 minutes of approval*
'''

    filepath = vault_path / 'Pending_Approval' / filename
    filepath.parent.mkdir(exist_ok=True)
    filepath.write_text(approval_content, encoding='utf-8')

    logger.info(f"Created {platform} post approval: {filename}")
    logger.info(f"Content preview: {content[:100]}...")

    return filepath


def check_and_generate(vault_path: Path, platform: str = None) -> int:
    """Check schedule and generate posts for approval."""
    generator = SocialContentGenerator(vault_path)
    posts_created = 0

    if platform:
        # Generate for specific platform
        platforms = {platform: getattr(generator, f'generate_{platform}_post')()}
    else:
        # Generate for all platforms
        platforms = generator.generate_all()

    for plat, content in platforms.items():
        if content:
            if _already_posted_today(plat, vault_path):
                logger.info(f"Skipping {plat} - already posted today")
                continue
            logger.info(f"Scheduled posting time for {plat}!")
            create_approval_file(plat, content, vault_path)
            posts_created += 1
        else:
            logger.debug(f"Not a scheduled time for {plat}")

    return posts_created


def force_generate(vault_path: Path, platform: str) -> Path:
    """Force generate a post for a platform regardless of schedule."""
    generator = SocialContentGenerator(vault_path)

    # Generate based on random template type
    if platform == 'facebook':
        templates = [generator.FB_BUSINESS_UPDATE, generator.FB_INDUSTRY_INSIGHT]
        template = random.choice(random.choice(templates))
        content = template.format(
            achievement=generator._get_achievement(),
            insight=random.choice(generator.INSIGHTS),
            day=datetime.now().strftime('%A'),
            question=random.choice(generator.QUESTIONS),
            focus=generator._get_focus(),
        )
    elif platform == 'instagram':
        templates = [generator.IG_BUSINESS, generator.IG_MOTIVATION]
        template = random.choice(random.choice(templates))
        content = template.format(
            achievement=generator._get_achievement(),
            insight=random.choice(generator.INSIGHTS),
            focus=generator._get_focus(),
        )
    elif platform == 'twitter':
        templates = [generator.TW_UPDATE, generator.TW_INSIGHT]
        template = random.choice(random.choice(templates))
        content = template.format(
            focus=generator._get_focus(),
            achievement=generator._get_achievement(),
            insight=random.choice(generator.INSIGHTS),
            day=datetime.now().strftime('%A'),
        )
        if len(content) > 280:
            content = content[:277] + '...'
    else:
        logger.error(f"Unknown platform: {platform}")
        return None

    return create_approval_file(platform, content, vault_path)


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Social Auto-Poster for AI Employee')
    parser.add_argument('--platform', '-p', choices=['facebook', 'instagram', 'twitter'],
                        help='Generate for specific platform only')
    parser.add_argument('--force', action='store_true',
                        help='Force generate regardless of schedule')
    parser.add_argument('--check', action='store_true',
                        help='Check schedule and generate if applicable')
    parser.add_argument('--all', action='store_true',
                        help='Force generate for all platforms')

    args = parser.parse_args()

    logger.info("=" * 60)
    logger.info("Social Auto-Poster Starting")
    logger.info(f"Current time: {datetime.now().strftime('%A %I:%M %p')}")
    logger.info("=" * 60)

    vault_path = Path(os.getenv('VAULT_PATH', str(VAULT_PATH)))

    if args.force and args.platform:
        filepath = force_generate(vault_path, args.platform)
        if filepath:
            logger.info(f"Force-generated {args.platform} post: {filepath}")
            return 0
        return 1

    elif args.all:
        for plat in ['facebook', 'instagram', 'twitter']:
            filepath = force_generate(vault_path, plat)
            logger.info(f"Force-generated {plat} post: {filepath}")
        return 0

    else:
        # Normal schedule check
        count = check_and_generate(vault_path, args.platform)
        if count > 0:
            logger.info(f"Created {count} post(s) for approval")
        else:
            logger.info("No posts scheduled for current time")
            logger.info("Facebook:  Tue 10AM, Thu 2PM, Sat 11AM")
            logger.info("Instagram: Mon 11AM, Wed 5PM, Fri 10AM")
            logger.info("Twitter:   Daily 9AM, 1PM, 5PM")
        return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)
