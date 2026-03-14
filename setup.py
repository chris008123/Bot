"""
Quick setup and reference guide.
Run this to validate your configuration.
"""

import os
import sys
from pathlib import Path

def check_config():
    """Validate configuration setup."""
    print("\n" + "="*60)
    print("🤖 Discord Code Quality Bot - Configuration Check")
    print("="*60 + "\n")
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Token
    print("1️⃣  Discord Token")
    token = os.getenv("DISCORD_TOKEN")
    if token:
        checks_passed += 1
        print("   ✅ Token found in environment variable")
    else:
        print("   ⚠️  Token not in environment variable")
        print("   Solution: export DISCORD_TOKEN=your-token")
    checks_total += 1
    
    # Check 2: Config file
    print("\n2️⃣  Configuration File")
    if Path("config.py").exists():
        checks_passed += 1
        print("   ✅ config.py exists")
        
        import config
        
        # Check admin IDs
        if config.ADMIN_USER_IDS and config.ADMIN_USER_IDS[0] != 123456789:
            checks_passed += 1
            print("   ✅ Admin user IDs configured")
        else:
            print("   ⚠️  No admin user IDs set")
            print(f"   Current: {config.ADMIN_USER_IDS}")
            print("   Solution: Edit config.py ADMIN_USER_IDS")
        checks_total += 1
        
        # Check channel IDs
        if config.ANNOUNCEMENTS_CHANNEL_ID:
            checks_passed += 1
            print("   ✅ Announcements channel configured")
        else:
            print("   ⚠️  Announcements channel not set")
            print("   This is needed for posting leaderboards")
        checks_total += 1
        
    else:
        print("   ❌ config.py not found")
    checks_total += 1
    
    # Check 3: Dependencies
    print("\n3️⃣  Dependencies")
    dependencies = [
        ("discord", "discord.py"),
        ("pylint", "pylint"),
        ("radon", "radon"),
        ("bandit", "bandit"),
    ]
    
    missing = []
    for module, name in dependencies:
        try:
            __import__(module)
            print(f"   ✅ {name} installed")
            checks_passed += 1
        except ImportError:
            print(f"   ❌ {name} NOT installed")
            missing.append(name)
        checks_total += 1
    
    if missing:
        print(f"\n   Solution: pip install {' '.join(missing)}")
    
    # Check 4: Database
    print("\n4️⃣  Database")
    if Path("discord_bot.db").exists():
        checks_passed += 1
        print("   ✅ Database file exists")
    else:
        print("   ℹ️  Database will be created on first run")
    checks_total += 1
    
    # Summary
    print("\n" + "="*60)
    print(f"✅ {checks_passed}/{checks_total} checks passed")
    print("="*60 + "\n")
    
    if checks_passed == checks_total:
        print("🎉 You're ready to run: python main.py\n")
        return True
    else:
        print("⚠️  Fix the issues above before running the bot\n")
        return False


def show_config_template():
    """Show configuration template."""
    print("\n" + "="*60)
    print("📝 Configuration Template - Add to config.py")
    print("="*60 + "\n")
    
    template = '''
# MINIMUM REQUIRED CONFIG

# 1. Discord Token (from Discord Developer Portal)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "your-token-here")

# 2. Admin User IDs (use Developer Mode to find your ID)
ADMIN_USER_IDS = [
    123456789,  # Your user ID here
]

# 3. Channel IDs (right-click channel -> Copy ID)
ANNOUNCEMENTS_CHANNEL_ID = 999888777666  # Where leaderboard is posted

# OPTIONAL BUT RECOMMENDED

# 4. More detailed configuration
SUBMISSION_CHANNEL_ID = None  # Restrict submissions to channel
LEADERBOARD_SIZE = 10
EXCLUDE_ADMINS_FROM_LEADERBOARD = True
RANKING_DAY = 0  # Monday
RANKING_HOUR = 12  # Noon UTC

# 5. Rule monitoring
BANNED_WORDS = {
    "spam",
    "inappropriate_word",
}

# 6. Scoring tuning
SCORING_CONFIG = {
    "base_score": 100,
    "syntax_error_penalty": 20,
    "pep8_violations_penalty": 15,
    "complexity_penalty": 10,
    # ... more options in config.py
}
    '''
    
    print(template)


def show_discord_setup():
    """Show Discord setup instructions."""
    print("\n" + "="*60)
    print("🎮 Discord Setup Instructions")
    print("="*60 + "\n")
    
    instructions = '''
STEP 1: Create Discord Application
  1. Go to https://discord.com/developers/applications
  2. Click "New Application"
  3. Give it a name: "Code Quality Bot"
  4. Go to "Bot" → "Add Bot"
  5. Copy the TOKEN

STEP 2: Set Bot Permissions
  1. Go to "OAuth2" → "URL Generator"
  2. Select scopes: "bot"
  3. Select permissions:
     - Send Messages
     - Read Messages/View Channels
     - Embed Links
     - Attach Files
     - Read Message History
  4. Copy the generated URL and open in browser
  5. Select your server and authorize

STEP 3: Get Your User ID
  1. In Discord Settings → Advanced → Enable "Developer Mode"
  2. Right-click on a user → "Copy User ID"
  3. Add this ID to ADMIN_USER_IDS in config.py

STEP 4: Get Channel IDs
  1. Right-click on a channel → "Copy Channel ID"
  2. Add to ANNOUNCEMENTS_CHANNEL_ID in config.py

STEP 5: Invite Bot to Server
  1. Use the OAuth2 URL from Step 2
  2. Or go to: https://discord.com/api/oauth2/authorize?client_id=YOUR_CLIENT_ID&permissions=274877908992&scope=bot
  3. Replace YOUR_CLIENT_ID with your bot's ID
    '''
    
    print(instructions)


def show_quick_commands():
    """Show quick command reference."""
    print("\n" + "="*60)
    print("⚡ Quick Command Reference")
    print("="*60 + "\n")
    
    commands = '''
USER COMMANDS:
  !submit              - Submit code for analysis
  !mystats             - View your submission history
  !leaderboard         - View weekly rankings
  !feedback [id]       - Get detailed feedback

ADMIN COMMANDS:
  !violations [id]     - Check rule violations
  !dbstats             - Database statistics
  !forceranking        - Manually generate rankings
  !help_admin          - Show admin commands

SCORING LEGEND:
  🌟 90-100: Excellent
  ✅ 75-89:  Great
  👍 60-74:  Good
  ⚠️  40-59:  Needs Work
  ❌ 0-39:   Major Issues
    '''
    
    print(commands)


if __name__ == "__main__":
    print("\n")
    
    # Check configuration
    if not check_config():
        choice = input("Would you like to see the configuration template? (y/n): ").lower()
        if choice == 'y':
            show_config_template()
    
    # Show additional help
    choice = input("\nShow Discord setup instructions? (y/n): ").lower()
    if choice == 'y':
        show_discord_setup()
    
    choice = input("\nShow quick command reference? (y/n): ").lower()
    if choice == 'y':
        show_quick_commands()
    
    print("\n✅ Setup complete! Run: python main.py\n")
