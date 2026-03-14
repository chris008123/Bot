"""
QUICK REFERENCE CARD
Print this or keep it open while developing
"""

# ============================================================================
# BOT COMMANDS REFERENCE
# ============================================================================

"""
USER COMMANDS:
  !submit              Submit code (file/block/reply)
  !mystats             View your stats
  !leaderboard         View top 10 rankings
  !feedback [id]       Get detailed analysis
  !help                Show all commands

ADMIN COMMANDS (requires ADMIN_USER_IDS):
  !violations [id]     View violations
  !dbstats             Database statistics
  !forceranking        Force generate rankings
  !help_admin          Show admin commands

SCORES:
  🌟 90-100: Excellent
  ✅ 75-89:  Great
  👍 60-74:  Good
  ⚠️  40-59:  Needs Work
  ❌ 0-39:   Major Issues
"""

# ============================================================================
# SCORING FORMULA QUICK REFERENCE
# ============================================================================

SCORING_BREAKDOWN = {
    "Base Points": 100,
    
    "Deductions": {
        "Syntax Error": -20,
        "PEP8 Violations": -15,
        "High Complexity": -10,
        "Missing Docs": -15,
        "Security Issues": -15,
        "Code Duplication": -5,
    },
    
    "Bonuses": {
        "Type Hints (50%+)": +5,
        "Test Code": +5,
        "Well Documented (80%+)": +5,
    },
}

# Example: Base 100 - 20 (syntax) - 15 (style) + 5 (hints) = 70/100 ✅

# ============================================================================
# CONFIGURATION CHECKLIST
# ============================================================================

CONFIG_CHECKLIST = """
MUST SET (bot won't work without these):
  [ ] DISCORD_TOKEN = "your-token-from-discord-dev-portal"
  [ ] ADMIN_USER_IDS = [your-user-id-here]
  [ ] ANNOUNCEMENTS_CHANNEL_ID = your-channel-id

SHOULD SET (recommended):
  [ ] Add more admin IDs if multiple mods
  [ ] Add banned words if moderation needed
  [ ] Adjust scoring if different community

OPTIONAL (works with defaults):
  [ ] LEADERBOARD_SIZE, RANKING_DAY, RANKING_HOUR
  [ ] SPAM_CONFIG thresholds
  [ ] MAX_CODE_SIZE limits
"""

# ============================================================================
# FILE PURPOSES
# ============================================================================

FILE_MAP = {
    "config.py": "All settings - EDIT THIS to customize",
    "bot.py": "Discord commands & events - DO NOT EDIT unless extending",
    "analyzer.py": "Code analysis logic - DO NOT EDIT unless adding tools",
    "database.py": "SQLite manager - DO NOT EDIT unless adding fields",
    "main.py": "Startup - Run this: python main.py",
    "requirements.txt": "Dependencies - pip install -r requirements.txt",
    "README.md": "User guide & examples",
    "IMPLEMENTATION.md": "Architecture & deep dive",
    "quickstart.py": "Interactive setup - python quickstart.py",
    "setup.py": "Configuration validator",
}

# ============================================================================
# COMMON CUSTOMIZATIONS
# ============================================================================

"""
CHANGE ADMIN USERS:
  config.py line ~25
  ADMIN_USER_IDS = [123456789, 987654321]

CHANGE BANNED WORDS:
  config.py line ~60
  BANNED_WORDS = {"spam", "bad_word", ...}

CHANGE SCORING:
  config.py line ~45
  SCORING_CONFIG = {...}

CHANGE LEADERBOARD:
  config.py line ~70
  LEADERBOARD_SIZE = 20
  RANKING_DAY = 4  (0=Mon, 4=Fri, 6=Sun)
  RANKING_HOUR = 18

CHANGE COMMAND PREFIX:
  config.py line ~14
  COMMAND_PREFIX = "?"  (instead of !)

ADD CHANNEL:
  config.py line ~30
  SUBMISSION_CHANNEL_ID = 123456789
"""

# ============================================================================
# TROUBLESHOOTING FLOW
# ============================================================================

"""
BOT WON'T START
  └─ Check: export DISCORD_TOKEN=your-token
  
COMMANDS NOT WORKING
  └─ Check: !help works? 
     └─ Yes: Bot is fine, check channel permissions
     └─ No: Check command prefix in config.py

ANALYSIS FAILS
  └─ Check logs for error
  └─ Missing tool? pip install pylint radon bandit

DATABASE ERROR
  └─ rm discord_bot.db (creates new)

NOT POSTING LEADERBOARD
  └─ Check: ANNOUNCEMENTS_CHANNEL_ID set correctly
  └─ Check: Bot has Send Messages permission
  └─ Wait until ranking time (RANKING_DAY + RANKING_HOUR)
"""

# ============================================================================
# DISCORD SETUP FLOW
# ============================================================================

"""
1. CREATE BOT
   https://discord.com/developers/applications
   → New Application
   → Bot tab → Add Bot
   → Copy TOKEN

2. GET PERMISSIONS
   → OAuth2 → URL Generator
   → Scopes: "bot"
   → Permissions: Send Messages, Embed Links, Read History
   → Copy URL and open in browser
   → Select server → Authorize

3. GET YOUR ID
   Discord Settings → Advanced → Developer Mode ON
   → Right-click your name → Copy User ID

4. GET CHANNEL ID
   Right-click channel → Copy Channel ID

5. UPDATE CONFIG
   config.py:
   DISCORD_TOKEN = "token-from-step-1"
   ADMIN_USER_IDS = [id-from-step-3]
   ANNOUNCEMENTS_CHANNEL_ID = id-from-step-4
"""

# ============================================================================
# QUICK SETUP (5 MINUTES)
# ============================================================================

"""
1. pip install -r requirements.txt
2. python quickstart.py  (or manually edit config.py)
3. python main.py
4. In Discord: !submit, !leaderboard, !mystats
5. Done! 🎉
"""

# ============================================================================
# ADMIN OPERATIONS
# ============================================================================

"""
DAILY:
  - Monitor !violations in admin DM

WEEKLY:
  - Leaderboard auto-posts (set RANKING_DAY/HOUR)
  - Review top performers

MONTHLY:
  - Backup database: cp discord_bot.db discord_bot.db.backup
  - Update deps: pip install --upgrade -r requirements.txt

YEARLY:
  - Audit admin IDs (remove inactive mods)
  - Review scoring rules
  - Consider new analysis tools
"""

# ============================================================================
# PYTHON CODE EXAMPLES FOR TESTING
# ============================================================================

EXCELLENT_CODE_EXAMPLE = '''"""Module docstring."""

from typing import List


def fibonacci(n: int) -> int:
    """
    Calculate nth Fibonacci number.
    
    Args:
        n: Position in sequence
    
    Returns:
        The nth Fibonacci number
    
    Raises:
        ValueError: If n < 0
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)


def test_fibonacci():
    """Test Fibonacci function."""
    assert fibonacci(0) == 0
    assert fibonacci(5) == 5
'''
# Expected Score: 90-100 🌟

POOR_CODE_EXAMPLE = '''def fib(n):
    if n<0:return 0
    if n<=1:return n
    return fib(n-1)+fib(n-2)

x=10
print(fib(x))
'''
# Expected Score: 35-50 ⚠️

# ============================================================================
# DEPLOYMENT OPTIONS
# ============================================================================

"""
LOCAL (Development):
  python main.py

VPS (Recommended):
  1. ssh root@vps
  2. git clone <repo>
  3. pip install -r requirements.txt
  4. Create systemd service (see IMPLEMENTATION.md)
  5. systemctl enable discord-bot && systemctl start discord-bot

DOCKER:
  docker build -t discord-bot .
  docker run -e DISCORD_TOKEN=token discord-bot

CLOUD (AWS/GCP/DigitalOcean):
  Same as VPS, just using cloud provider
"""

# ============================================================================
# KEY CLASSES & METHODS
# ============================================================================

"""
database.Database:
  .add_submission(user_id, code, language, score, feedback)
  .get_user_submissions(user_id, limit=None)
  .get_user_avg_score(user_id)
  .generate_weekly_rankings()
  .add_violation(user_id, violation_type, message)
  .get_database_stats()

analyzer.CodeAnalyzer:
  .analyze(code, language="python")
  → Returns: (score: int, feedback: dict)

bot.py Commands:
  @bot.command(name='submit') - User submission
  @bot.command(name='mystats') - User stats
  @bot.command(name='violations') - Admin violations
  @bot.command(name='forceranking') - Admin manual ranking
"""

# ============================================================================
# DEBUGGING TIPS
# ============================================================================

"""
CHECK BOT STATUS:
  import discord
  print(bot.user)  # Should show bot name

CHECK DATABASE:
  sqlite3 discord_bot.db
  > SELECT COUNT(*) FROM submissions;
  > .quit

CHECK CONFIG:
  python -c "import config; print(config.ADMIN_USER_IDS)"

CHECK DISCORD SETUP:
  Right-click bot message → Copy Message ID
  If bot can send messages, it's connected

VIEW LOGS:
  python main.py 2>&1 | tee bot.log  # Save logs
  tail -f bot.log  # Follow logs live
"""

# ============================================================================
# USEFUL DISCORD TIPS
# ============================================================================

"""
ENABLE DEVELOPER MODE:
  User Settings → Advanced → Developer Mode → Toggle ON

COPY IDs:
  - Bot: Right-click bot → App ID
  - User: Right-click name → Copy User ID
  - Channel: Right-click channel → Copy Channel ID
  - Role: Right-click role → Copy Role ID
  - Message: Right-click message → Copy Message Link

PERMISSIONS CALCULATOR:
  https://discordapi.com/permissions.html
  Use for Bot Permissions configuration
"""

# ============================================================================
# BACKUP & MAINTENANCE
# ============================================================================

"""
DAILY BACKUP:
  cp discord_bot.db discord_bot.db.$(date +%Y%m%d).bak

RESTORE FROM BACKUP:
  cp discord_bot.db.20240101.bak discord_bot.db

CLEAN OLD DATA:
  python -c "from database import Database; Database().clear_old_data(90)"

EXPORT TO SQL:
  sqlite3 discord_bot.db ".dump" > backup.sql

IMPORT FROM SQL:
  sqlite3 discord_bot.db < backup.sql
"""

# ============================================================================
# PERFORMANCE TIPS
# ============================================================================

"""
CODE ANALYSIS TAKES TOO LONG:
  → Increase MAX_CONCURRENT_ANALYSIS in config.py
  → Or reduce analysis tools if unneeded

DATABASE SLOW:
  → Indexes are created automatically
  → Check with: sqlite3 discord_bot.db ".indices"

BOT USING TOO MUCH MEMORY:
  → Cleanup old submissions regularly
  → Reduce MAX_CODE_SIZE if possible

TOO MANY BACKGROUND TASK ERRORS:
  → Check logs for specific errors
  → Increase timeout values in config.py
"""

# ============================================================================
# WHEN THINGS GO WRONG
# ============================================================================

"""
IMMEDIATE:
  1. Stop bot: Ctrl+C
  2. Check error message
  3. See which file/command failed
  4. Check logs for traceback

DIAGNOSIS:
  1. Is it config issue? Check config.py
  2. Is it dependency? pip install -r requirements.txt
  3. Is it database? rm discord_bot.db
  4. Is it Discord permissions? Check bot role

RECOVERY:
  1. Backup database (always!)
  2. Fix the issue
  3. Restart bot
  4. Test commands
  5. Done!
"""

# ============================================================================

if __name__ == "__main__":
    print(__doc__)
    print(QUICK_SETUP)
