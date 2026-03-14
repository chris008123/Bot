"""
Main entry point for the Discord Code Quality Bot.
Run this file to start the bot.
"""

import os
import sys
import logging
from flask import Flask
from threading import Thread

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Flask app for Render port binding
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


def main():
    """Start the Discord bot and web server."""

    # Start web server thread (for Render port requirement)
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    # Import after logging setup
    from bot import bot
    import config

    # Get token from environment
    token = os.environ.get("DISCORD_TOKEN", config.DISCORD_TOKEN)

    if not token:
        logger.error("❌ DISCORD_TOKEN not found!")
        sys.exit(1)

    if not config.ADMIN_USER_IDS or config.ADMIN_USER_IDS[0] == 123456789:
        logger.warning("⚠️ No admin user IDs configured.")

    if not config.ANNOUNCEMENTS_CHANNEL_ID:
        logger.warning("⚠️ ANNOUNCEMENTS_CHANNEL_ID not set.")

    logger.info("🤖 Starting Discord bot...")

    try:
        bot.run(token)
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()