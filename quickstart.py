#!/usr/bin/env python3
"""
Quick Start Guide - Run this to get started in 5 minutes!
"""

import os
import sys
import json
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_step(num, text):
    """Print a numbered step."""
    print(f"\n{num}️⃣  {text}")
    print("-" * 70)


def step_1_prerequisites():
    """Step 1: Check prerequisites."""
    print_step("1", "Checking Prerequisites")
    
    checks = {
        "Python 3.8+": sys.version_info >= (3, 8),
        "pip installed": os.path.exists("requirements.txt"),
        "config.py exists": Path("config.py").exists(),
    }
    
    all_good = True
    for check, result in checks.items():
        status = "✅" if result else "❌"
        print(f"  {status} {check}")
        all_good = all_good and result
    
    return all_good


def step_2_get_token():
    """Step 2: Get Discord token."""
    print_step("2", "Get Your Discord Bot Token")
    
    instructions = """
  1. Go to: https://discord.com/developers/applications
  2. Click "New Application" and name it "Code Quality Bot"
  3. Go to "Bot" tab → Click "Add Bot"
  4. Under TOKEN section, click "Copy" (copy the token!)
  5. Go to "OAuth2" → "URL Generator"
     - Scopes: "bot"
     - Permissions: "Send Messages", "Embed Links", "Read Message History"
     - Copy the Generated URL
  6. Open the URL in your browser and authorize the bot
  
  Your token should look like:
  MzI4MjUwODxtfxgxfI1ODA3MjI1ODA4LjEwMDEyOA.DHsqnw.Your-actual-token-here
    """
    
    print(instructions)
    
    token = input("\nPaste your token here: ").strip()
    
    if not token or len(token) < 50:
        print("❌ Invalid token format")
        return None
    
    return token


def step_3_get_ids():
    """Step 3: Get Discord user/channel IDs."""
    print_step("3", "Get Your Discord IDs")
    
    instructions = """
  1. In Discord, enable Developer Mode:
     Settings → Advanced → Developer Mode → Toggle ON
  
  2. Get your User ID:
     - Right-click your name in any server
     - Select "Copy User ID"
  
  3. Get Channel ID for leaderboard:
     - Right-click a channel (where to post rankings)
     - Select "Copy Channel ID"
    """
    
    print(instructions)
    
    user_id = input("\nEnter your Discord User ID (numbers only): ").strip()
    if not user_id.isdigit():
        print("❌ Invalid user ID")
        return None, None
    
    channel_id = input("Enter Channel ID for leaderboard: ").strip()
    if not channel_id.isdigit():
        print("❌ Invalid channel ID")
        return None, None
    
    return int(user_id), int(channel_id)


def step_4_configure():
    """Step 4: Update config.py."""
    print_step("4", "Configure the Bot")
    
    token = step_2_get_token()
    if not token:
        return False
    
    user_id, channel_id = step_3_get_ids()
    if not user_id or not channel_id:
        return False
    
    # Update config.py
    config_template = f'''"""
Configuration module for the Discord Code Quality Bot.
Centralized settings management for all bot operations.
"""

import os
from typing import List, Set

# DISCORD BOT TOKEN (from Discord Developer Portal)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "{token}")

# COMMAND PREFIX
COMMAND_PREFIX = "!"

# ============================================================================
# ADMIN CONFIGURATION
# ============================================================================

ADMIN_USER_IDS: List[int] = [
    {user_id},  # Your user ID
]

ADMIN_ROLE_ID: int = None

# ============================================================================
# CHANNEL CONFIGURATION
# ============================================================================

SUBMISSION_CHANNEL_ID: int = None
ANNOUNCEMENTS_CHANNEL_ID: int = {channel_id}  # Leaderboard channel
MODERATION_LOG_CHANNEL_ID: int = None

# ============================================================================
# SUPPORTED FILE EXTENSIONS
# ============================================================================

SUPPORTED_EXTENSIONS: Set[str] = {{
    ".py",
    ".js", ".ts",
    ".java",
    ".cpp", ".cc", ".cxx",
    ".c",
    ".go",
    ".rs",
}}

# ============================================================================
# SUBMISSION SETTINGS
# ============================================================================

MAX_CODE_SIZE = 50000  # 50KB
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# ============================================================================
# SCORING CONFIGURATION
# ============================================================================

SCORING_CONFIG = {{
    "base_score": 100,
    "syntax_error_penalty": 20,
    "pep8_violations_penalty": 15,
    "complexity_penalty": 10,
    "complexity_threshold": 10,
    "missing_docs_penalty": 15,
    "security_issues_penalty": 15,
    "duplication_penalty": 5,
    "duplication_threshold": 10,
    "type_hints_bonus": 5,
    "comprehensive_tests_bonus": 5,
    "well_documented_bonus": 5,
}}

PYLINT_THRESHOLDS = {{
    "excellent": 9.0,
    "good": 7.0,
    "acceptable": 5.0,
    "poor": 0.0,
}}

# ============================================================================
# RULE MONITORING
# ============================================================================

BANNED_WORDS: Set[str] = {{
    "spam",
}}

SPAM_CONFIG = {{
    "max_messages_per_minute": 5,
    "duplicate_threshold": 3,
    "caps_lock_threshold": 0.7,
}}

# ============================================================================
# WEEKLY RANKING SETTINGS
# ============================================================================

RANKING_DAY = 0  # Monday
RANKING_HOUR = 12  # Noon UTC
LEADERBOARD_SIZE = 10
MIN_SUBMISSIONS_FOR_LEADERBOARD = 1
EXCLUDE_ADMINS_FROM_LEADERBOARD = True

# ============================================================================
# DATABASE & OTHER
# ============================================================================

DATABASE_PATH = "discord_bot.db"
LOG_LEVEL = "INFO"
TIMEZONE = "UTC"
ANALYSIS_TIMEOUT = 30
MAX_CONCURRENT_ANALYSIS = 5
DEBUG_MODE = False
'''
    
    # Backup existing config if it exists
    if Path("config.py").exists():
        backup_path = Path("config.py.backup")
        import shutil
        shutil.copy("config.py", backup_path)
        print(f"  ✅ Backed up existing config to {backup_path}")
    
    # Write new config
    with open("config.py", "w") as f:
        f.write(config_template)
    
    print(f"  ✅ config.py created successfully")
    print(f"  Admin ID: {user_id}")
    print(f"  Leaderboard Channel: {channel_id}")
    print(f"  Token: {token[:20]}...")
    
    return True


def step_5_dependencies():
    """Step 5: Install dependencies."""
    print_step("5", "Install Dependencies")
    
    import subprocess
    
    try:
        print("  Installing packages... (this may take 1-2 minutes)")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("  ✅ All dependencies installed successfully")
            
            # Check for analysis tools
            try:
                import pylint
                print("  ✅ pylint installed")
            except:
                print("  ⚠️  pylint not found (optional, but recommended)")
            
            try:
                import radon
                print("  ✅ radon installed")
            except:
                print("  ⚠️  radon not found (optional, but recommended)")
            
            return True
        else:
            print("  ❌ Installation failed")
            print(result.stderr)
            return False
    
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False


def step_6_test():
    """Step 6: Test configuration."""
    print_step("6", "Test Configuration")
    
    try:
        import config
        
        tests = {
            "Token set": config.DISCORD_TOKEN and config.DISCORD_TOKEN != "your-token-here",
            "Admin IDs configured": len(config.ADMIN_USER_IDS) > 0,
            "Channel ID set": config.ANNOUNCEMENTS_CHANNEL_ID is not None,
        }
        
        all_good = True
        for test_name, result in tests.items():
            status = "✅" if result else "❌"
            print(f"  {status} {test_name}")
            all_good = all_good and result
        
        return all_good
    
    except Exception as e:
        print(f"  ❌ Error loading config: {e}")
        return False


def step_7_run():
    """Step 7: Run the bot."""
    print_step("7", "Run the Bot")
    
    print("""
  To start the bot, run:
  
    python main.py
  
  Expected output:
    2024-12-21 10:00:00 - bot - INFO - MyBot#1234 has connected to Discord
    2024-12-21 10:00:01 - bot - INFO - Bot is in 1 guild(s)
    2024-12-21 10:00:02 - bot - INFO - Background tasks started successfully
  
  Once running, test in Discord:
    !submit
    !leaderboard
    !mystats
    
  Admin commands:
    !violations
    !dbstats
    !help_admin
    """)


def main():
    """Run the quick start guide."""
    print_header("🚀 Discord Code Quality Bot - Quick Start Guide (5 minutes)")
    
    print("""
This guide will help you set up the bot for your Discord server.

You'll need:
  • Your Discord User ID
  • A Discord channel ID (for leaderboard)
  • A Discord bot token
  • Python 3.8+ and pip
    """)
    
    # Step 1: Prerequisites
    if not step_1_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above.")
        return False
    
    # Step 4: Configure
    print("\n⏳ Now I need some information from you...")
    if not step_4_configure():
        print("\n❌ Configuration cancelled.")
        return False
    
    # Step 5: Install dependencies
    if not step_5_dependencies():
        print("\n⚠️  Dependency installation had issues. Continuing anyway...")
    
    # Step 6: Test
    if not step_6_test():
        print("\n⚠️  Configuration test failed. Please check config.py")
        return False
    
    # Step 7: Run
    step_7_run()
    
    print_header("✅ Setup Complete!")
    
    print("""
Next steps:
  1. Run: python main.py
  2. Go to Discord and test:
     - Send: !submit
     - Send: !leaderboard
     - Send: !mystats
  
  3. For admin commands, try:
     - Send: !violations
     - Send: !help_admin
  
Questions or issues?
  • Check README.md for full documentation
  • Check IMPLEMENTATION.md for architecture details
  • Run: python setup.py  for detailed validation
  
Good luck! 🎉
    """)
    
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
