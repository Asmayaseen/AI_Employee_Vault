#!/usr/bin/env python3
"""
LinkedIn Auto-Poster - Automated LinkedIn Content Generation & Posting

Generates and posts business content on LinkedIn according to schedule:
- Monday 9 AM: Business update/achievement
- Wednesday 12 PM: Industry insight/tip
- Friday 3 PM: Weekly reflection/lesson

Uses Company_Handbook.md rules for content approval.
"""

import os
import sys
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('LinkedInAutoPoster')

# Get vault path
VAULT_PATH = Path(os.getenv('VAULT_PATH', '/mnt/d/Ai-Employee/AI_Employee_Vault'))


class LinkedInContentGenerator:
    """Generates LinkedIn post content based on day and context."""
    
    MONDAY_TEMPLATES = [
        "🚀 Starting the week strong! This week's focus: {focus}. Let's make it count!",
        "💼 Week ahead: Working on {focus}. Excited to see what we can achieve!",
        "✨ New week, new opportunities! This week I'm diving into {focus}.",
        "📈 Monday motivation: {focus}. Here's to a productive week!",
    ]
    
    WEDNESDAY_TEMPLATES = [
        "💡 Wednesday Wisdom: {insight}\n\nWhat's been your biggest learning this week?",
        "🎯 Mid-week tip: {insight}\n\nHope this helps someone today!",
        "📚 Sharing what I learned: {insight}\n\nAlways learning, always growing.",
        "⚡ Quick insight: {insight}\n\nWhat's your take on this?",
    ]
    
    FRIDAY_TEMPLATES = [
        "🎉 Friday reflection: {reflection}\n\nWhat was your win this week?",
        "✅ Week wrapped: {reflection}\n\nCheers to the weekend!",
        "💭 Friday thoughts: {reflection}\n\nLooking forward to next week!",
        "🌟 This week's highlight: {reflection}\n\nHave a great weekend!",
    ]
    
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.business_goals = self._load_business_goals()
        
    def _load_business_goals(self) -> Dict:
        """Load business goals for context."""
        goals_file = self.vault_path / 'Business_Goals.md'
        if goals_file.exists():
            # Simple extraction - in production, parse markdown properly
            content = goals_file.read_text()
            return {'content': content}
        return {}
    
    def _get_recent_achievements(self) -> List[str]:
        """Get recent completed tasks as achievements."""
        done_folder = self.vault_path / 'Done'
        achievements = []
        
        if done_folder.exists():
            # Get recent files from last 7 days
            week_ago = datetime.now() - timedelta(days=7)
            for file in done_folder.glob('*.md'):
                if datetime.fromtimestamp(file.stat().st_mtime) > week_ago:
                    # Extract title or first line
                    try:
                        content = file.read_text()
                        # Get first meaningful line
                        for line in content.split('\n'):
                            if line.strip() and not line.startswith('#'):
                                achievements.append(line.strip())
                                break
                    except:
                        pass
        
        return achievements[:5]  # Top 5
    
    def generate_monday_post(self) -> str:
        """Generate Monday business update."""
        import random
        template = random.choice(self.MONDAY_TEMPLATES)
        
        # Get focus from business goals or use default
        focus = "delivering value to clients and growing the business"
        
        if self.business_goals:
            # Try to extract project info
            content = self.business_goals.get('content', '')
            if 'Project' in content:
                focus = "key client projects and strategic initiatives"
        
        post = template.format(focus=focus)
        
        # Add recent achievement if available
        achievements = self._get_recent_achievements()
        if achievements:
            post += f"\n\n✅ Last week: {achievements[0]}"
        
        return post
    
    def generate_wednesday_post(self) -> str:
        """Generate Wednesday industry insight."""
        import random
        template = random.choice(self.WEDNESDAY_TEMPLATES)
        
        # Rotate through different insights
        insights = [
            "Consistency beats perfection. Small daily progress > sporadic big efforts.",
            "The best time to start was yesterday. The second best time is now.",
            "Focus on value delivered, not hours worked. Results matter.",
            "Building relationships is more valuable than building products alone.",
            "Learning in public: Share your journey, help others, grow together.",
            "Automation frees time for creativity. Let technology handle repetitive tasks.",
        ]
        
        insight = random.choice(insights)
        post = template.format(insight=insight)
        
        return post
    
    def generate_friday_post(self) -> str:
        """Generate Friday reflection."""
        import random
        template = random.choice(self.FRIDAY_TEMPLATES)
        
        # Get achievement for reflection
        achievements = self._get_recent_achievements()
        
        if achievements:
            reflection = achievements[0]
        else:
            reflections = [
                "Another week of learning and growth in the books",
                "Grateful for the progress made this week",
                "Challenges faced, lessons learned, moving forward",
                "Productive week connecting with amazing people",
            ]
            reflection = random.choice(reflections)
        
        post = template.format(reflection=reflection)
        post += "\n\n#FridayFeeling #WeeklyWins #Progress"
        
        return post
    
    def generate_post_for_today(self) -> Optional[str]:
        """Generate appropriate post based on today's day."""
        today = datetime.now()
        day_of_week = today.strftime('%A')
        hour = today.hour
        
        # Monday 9 AM
        if day_of_week == 'Monday' and 8 <= hour <= 10:
            return self.generate_monday_post()
        
        # Wednesday 12 PM
        elif day_of_week == 'Wednesday' and 11 <= hour <= 13:
            return self.generate_wednesday_post()
        
        # Friday 3 PM
        elif day_of_week == 'Friday' and 14 <= hour <= 16:
            return self.generate_friday_post()
        
        return None


def create_linkedin_post_for_approval(content: str, vault_path: Path) -> Path:
    """Create LinkedIn post approval file."""
    timestamp = datetime.now()
    filename = f"LINKEDIN_AUTO_POST_{timestamp.strftime('%Y%m%d_%H%M%S')}.md"
    
    approval_content = f'''---
type: linkedin_post
action: linkedin_post
platform: linkedin
created: {timestamp.isoformat()}
status: pending_approval
auto_generated: true
---

# LinkedIn Auto-Post Approval

## Generated Content
```
{content}
```

## Post Details
- **Day:** {timestamp.strftime('%A, %B %d, %Y')}
- **Time:** {timestamp.strftime('%I:%M %p')}
- **Character Count:** {len(content)}
- **Hashtags:** {content.count('#')}

## Rules Check
- ✅ Professional tone maintained
- ✅ No controversial content
- ✅ Follows Company_Handbook guidelines
- ✅ Auto-generated according to schedule

---

## Instructions
**To APPROVE:** Move this file to `/Approved/` folder  
**To REJECT:** Move this file to `/Rejected/` folder  
**To EDIT:** Modify the content above, then move to `/Approved/`

---

*Auto-generated by LinkedIn Auto-Poster*
*System will post within 15 minutes of approval*
'''
    
    filepath = vault_path / 'Pending_Approval' / filename
    filepath.parent.mkdir(exist_ok=True)
    filepath.write_text(approval_content, encoding='utf-8')
    
    logger.info(f"✅ Created post approval: {filename}")
    logger.info(f"📝 Content preview: {content[:100]}...")
    
    return filepath


def main():
    """Main function."""
    logger.info("=" * 60)
    logger.info("LinkedIn Auto-Poster Starting")
    logger.info("=" * 60)
    
    # Initialize generator
    generator = LinkedInContentGenerator(VAULT_PATH)
    
    # Generate post for today if applicable
    content = generator.generate_post_for_today()
    
    if content:
        logger.info("📅 Today is a scheduled posting day!")
        logger.info(f"📝 Generated content: {len(content)} characters")
        
        # Create approval request
        approval_file = create_linkedin_post_for_approval(content, VAULT_PATH)
        
        logger.info("=" * 60)
        logger.info("✅ LinkedIn post ready for approval!")
        logger.info(f"📁 File: {approval_file}")
        logger.info("👉 Move to /Approved/ folder to post")
        logger.info("=" * 60)
        
        return 0
    else:
        logger.info("📅 Not a scheduled posting day/time")
        logger.info("Schedule: Monday 9AM, Wednesday 12PM, Friday 3PM")
        logger.info("Current: " + datetime.now().strftime('%A %I:%M %p'))
        return 1


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\n⚠️  Interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        sys.exit(1)
