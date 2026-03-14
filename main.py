
"""
Main entry point for the Discord Code Quality Bot.
Run this file to start the bot.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Start the Discord bot."""
    # Import bot after logging is configured
    from bot import bot
    import config
    
    # Validate configuration
    if config.DISCORD_TOKEN == 'your-token-here':
        logger.error('❌ DISCORD_TOKEN not set in config.py or environment!')
        logger.error('Set it using: DISCORD_TOKEN=your-token python main.py')
        sys.exit(1)
    
    if not config.ADMIN_USER_IDS or config.ADMIN_USER_IDS[0] == 123456789:
        logger.warning('⚠️  No admin user IDs configured. Update config.py to set admins.')
    
    if not config.ANNOUNCEMENTS_CHANNEL_ID:
        logger.warning('⚠️  ANNOUNCEMENTS_CHANNEL_ID not set. Leaderboard won\'t be posted.')
    
    # Start bot
    logger.info('🤖 Starting Discord bot...')
    try:
        bot.run(config.DISCORD_TOKEN)
    except Exception as e:
        logger.error(f'❌ Failed to start bot: {e}')
        sys.exit(1)


if __name__ == '__main__':
    main()
