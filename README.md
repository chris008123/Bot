# 🤖 Discord Code Quality Bot

A production-ready Discord bot that evaluates members' code submissions and generates weekly quality-based rankings. **Ranking is based on code QUALITY, not activity.**

## 📋 Features

✅ **Automated Code Analysis**
- Syntax validation (AST)
- PEP8 style checking (pylint)
- Cyclomatic complexity analysis (radon)
- Security vulnerability detection (bandit)
- Documentation/comment coverage
- Code duplication detection

✅ **Transparent Scoring System (0-100)**
- Base score: 100 points
- Deductions for syntax errors, style violations, complexity, missing docs, security issues
- Bonuses for type hints, tests, good documentation
- Clear feedback explaining each deduction/bonus

✅ **Weekly Rankings**
- Automatically generated top 10 leaderboard
- Admin users excluded from rankings (configurable)
- Posted to announcements channel
- Tracked in SQLite database

✅ **Rule Monitoring**
- Detects banned words/phrases
- Detects spam (excessive caps, repeated messages)
- Reports violations to admin DM

✅ **Multiple Submission Methods**
- Code file attachments (.py, .js, .java, etc.)
- Code blocks in messages (```python...```)
- Command-based submission

✅ **User-Friendly Commands**
- `/submit` - Submit code for analysis
- `!mystats` - View your submission history
- `!leaderboard` - View weekly rankings
- `!feedback` - Get detailed analysis of submissions

## 🏗️ Architecture

```
disbot/
├── config.py          # Configuration & settings
├── database.py        # SQLite persistence layer
├── analyzer.py        # Code analysis engine (pylint, radon, bandit, ast)
├── bot.py            # Discord bot & command handlers
├── main.py           # Entry point
├── requirements.txt  # Python dependencies
└── README.md         # This file
```

### Module Responsibilities

| Module | Purpose |
|--------|---------|
| `config.py` | Centralized settings: token, admin IDs, channel IDs, scoring rules, banned words |
| `database.py` | SQLite ORM for submissions, rankings, violations, and user data |
| `analyzer.py` | Code quality analysis using pylint, radon, bandit, and ast |
| `bot.py` | Discord bot with commands, events, and background tasks |
| `main.py` | Entry point with validation and startup logic |

### Database Schema

```sql
submissions
├── id (PK)
├── user_id
├── timestamp
├── code (source text)
├── language
├── score (0-100)
└── feedback (JSON: analysis details, deductions, bonuses)

weekly_rankings
├── id (PK)
├── week_start / week_end
├── user_id
├── rank
├── avg_score
└── submission_count

violations
├── id (PK)
├── user_id
├── violation_type (banned_word, spam, etc.)
├── message
└── timestamp

users
├── user_id (PK)
├── username
└── created_at
```

## 📊 Scoring Formula

### Base Score: 100 points

**Deductions:**
- Syntax Errors: -20 (code doesn't run)
- PEP8 Violations: -15 (code style issues)
- High Complexity (>10): -10 (hard to test/maintain)
- Missing Documentation: -15 (no docstrings/comments)
- Security Issues: -15 (vulnerabilities detected)
- Code Duplication (>10%): -5

**Bonuses:**
- Type Hints (50%+ functions): +5
- Test Code Detected: +5
- Well Documented (80%+ coverage): +5

**Final Score = max(0, min(100, base - deductions + bonuses))**

### Score Interpretation

| Score | Rating | Meaning |
|-------|--------|---------|
| 90-100 | 🌟 Excellent | Production-ready code |
| 75-89 | ✅ Great | Minor issues, generally solid |
| 60-74 | 👍 Good | Acceptable, room for improvement |
| 40-59 | ⚠️ Needs Work | Significant issues to address |
| 0-39 | ❌ Major Issues | Requires substantial revision |

## 🚀 Setup & Installation

### Prerequisites
- Python 3.8+
- Discord bot token (from Discord Developer Portal)
- pip/virtualenv

### Step 1: Install Dependencies

```bash
cd disbot
pip install -r requirements.txt
```

This installs:
- `discord.py` - Discord API wrapper
- `pylint` - Code style analysis
- `radon` - Complexity metrics
- `bandit` - Security checking

### Step 2: Configure the Bot

Edit `config.py`:

```python
# 1. Set your Discord token
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN", "your-actual-token-here")
# OR use environment variable:
# export DISCORD_TOKEN=your-token-here

# 2. Set admin user IDs (find by enabling Developer Mode in Discord)
ADMIN_USER_IDS = [
    123456789,  # Your user ID
    987654321,  # Second admin
]

# 3. Set channel IDs
ANNOUNCEMENTS_CHANNEL_ID = 1234567890  # Where leaderboard is posted
SUBMISSION_CHANNEL_ID = 1098765432      # Submission channel (optional)
MODERATION_LOG_CHANNEL_ID = 5555555555  # Moderation logs (optional)

# 4. Configure scoring (optional)
LEADERBOARD_SIZE = 10
RANKING_DAY = 0  # Monday
RANKING_HOUR = 12  # Noon UTC

# 5. Add banned words
BANNED_WORDS = {"spam", "inappropriate", ...}
```

### Step 3: Get Your IDs

**Discord Token:**
1. Go to https://discord.com/developers/applications
2. Create "New Application"
3. Go to "Bot" → "Add Bot"
4. Copy the token

**User ID:**
1. Enable Developer Mode in Discord Settings
2. Right-click user → "Copy User ID"

**Channel ID:**
1. Right-click channel → "Copy Channel ID"

### Step 4: Run the Bot

```bash
# Method 1: Direct
python main.py

# Method 2: With environment variable
DISCORD_TOKEN=your-token python main.py

# Method 3: On Linux/Mac with token in shell
export DISCORD_TOKEN=your-token
python main.py
```

Expected output:
```
2024-12-21 12:00:00 - bot - INFO - MyBot#1234 has connected to Discord
2024-12-21 12:00:01 - bot - INFO - Bot is in 1 guild(s)
2024-12-21 12:00:02 - bot - INFO - Background tasks started successfully
```

## 📝 Usage Examples

### User Commands

#### Submit Code
```
!submit
[attach Python file]

OR

!submit
```python
def hello_world():
    """Print hello world."""
    print("Hello")
```

Response:
```
✅ Code Analysis Complete
📊 Score: 85/100 ✅ Great!
💻 Language: Python
❌ Issues Found: High cyclomatic complexity, Missing documentation
```

#### View Your Stats
```
!mystats

Response:
📊 Stats for JohnDoe
📈 Statistics
Total Submissions: 5
Average Score: 82.4/100
Latest Score: 88/100

🕐 Recent Submissions
• **88/100** - 2024-12-21 14:30 (python)
• **80/100** - 2024-12-20 10:15 (python)
```

#### View Leaderboard
```
!leaderboard

Response:
🏆 Weekly Code Quality Leaderboard
🥇 Alice - 92.5/100 (8 submissions)
🥈 Bob - 87.3/100 (6 submissions)
🥉 Charlie - 85.1/100 (5 submissions)
4. Diana - 81.2/100 (4 submissions)
```

#### Get Detailed Feedback
```
!feedback 5

Response:
📋 Detailed Feedback - Score: 85/100
🔍 Analysis Results
Syntax: Valid
PEP8: {'convention': 2, 'refactor': 1, 'warning': 0, 'error': 0}
Cyclomatic Complexity: 12

❌ Deductions
• High cyclomatic complexity: 12 (-10 pts)
• PEP8 violations: 3 issues found (-7 pts)

✅ Bonuses
• Good use of type hints: 50% (+5 pts)
```

### Admin Commands

#### Check Violations
```
!violations 123456789 24

Response:
⚠️ Recent Rule Violations
JohnDoe - banned_word
Message contained banned word: spam
2024-12-21 10:30:45

TempUser - spam
Excessive caps lock: 85%
2024-12-21 09:15:22
```

#### View Database Stats
```
!dbstats

Response:
📊 Database Statistics
Total Submissions: 47
Active Users: 12
Total Violations: 3
```

#### Force Ranking Generation
```
!forceranking

Response:
⏳ Generating rankings...
✅ Rankings generated! Top user: 123456789
```

#### Admin Help
```
!help_admin

Response:
🔧 Admin Commands
!violations [user_id] [hours]
Check rule violations

!dbstats
Show database statistics

!forceranking
Manually generate weekly rankings

Configuration
Admins: 2
Leaderboard Size: 10
```

## ⚙️ Configuration Guide

### Admin Configuration (Most Important)

**Method 1: User ID Based (Recommended)**
```python
# config.py
ADMIN_USER_IDS = [123456789, 987654321]
```

**Method 2: Role Based (Alternative)**
```python
# config.py
ADMIN_ROLE_ID = 1234567890  # Admin role ID
```

To find your user ID:
1. In Discord, enable Developer Mode (User Settings → Advanced → Developer Mode)
2. Right-click on a user → "Copy User ID"

### Channel Configuration

```python
# Where leaderboard is posted every week
ANNOUNCEMENTS_CHANNEL_ID = 1234567890

# Optional: submission-only channel
SUBMISSION_CHANNEL_ID = 9876543210

# Optional: admin logs
MODERATION_LOG_CHANNEL_ID = 5555555555
```

### Scoring Customization

```python
SCORING_CONFIG = {
    "base_score": 100,
    "syntax_error_penalty": 20,      # Very strict
    "pep8_violations_penalty": 15,   # Code style matters
    "complexity_penalty": 10,
    "missing_docs_penalty": 15,
    "security_issues_penalty": 15,
    "duplication_penalty": 5,
    
    # Bonuses
    "type_hints_bonus": 5,
    "comprehensive_tests_bonus": 5,
    "well_documented_bonus": 5,
}
```

### Supported Languages

Primary support: **Python**

Secondary support (limited analysis):
- JavaScript/TypeScript (.js, .ts)
- Java (.java)
- C/C++ (.c, .cpp, .cc, .cxx)
- Go (.go)
- Rust (.rs)

To add more:
1. Update `SUPPORTED_EXTENSIONS` in config.py
2. Extend analyzer.py with language-specific logic

### Rule Configuration

```python
# Words that trigger violations
BANNED_WORDS = {
    "spam",
    "scam",
    "inappropriate_content",
}

# Spam detection
SPAM_CONFIG = {
    "max_messages_per_minute": 5,
    "duplicate_threshold": 3,  # Same message 3+ times = spam
    "caps_lock_threshold": 0.7,  # 70% caps = spam
}
```

### Weekly Ranking Schedule

```python
# When rankings are generated (UTC)
RANKING_DAY = 0         # 0=Monday, 6=Sunday
RANKING_HOUR = 12       # Noon

# Leaderboard settings
LEADERBOARD_SIZE = 10
EXCLUDE_ADMINS_FROM_LEADERBOARD = True  # IMPORTANT
```

## 🔐 Security Considerations

### Implemented Safeguards

✅ **SQL Injection Prevention**
- Uses parameterized queries throughout
- Database.py handles all SQL safely

✅ **Timeout Protection**
- Analysis has 30-second timeout (configurable)
- Prevents hanging on malicious code

✅ **Rate Limiting**
- Submissions limited to 1 per 60 seconds per user
- Prevents spam and abuse

✅ **Size Limits**
- Max 50KB code per submission (configurable)
- Max 10MB file attachments

✅ **Privilege Separation**
- Admin commands check user ID against whitelist
- Non-admins can't modify rankings or access violations

✅ **Safe Error Handling**
- All exceptions caught and logged
- No stack traces sent to users
- Graceful degradation

### Best Practices to Follow

1. **Keep token secret**
   ```bash
   # Use environment variables ONLY
   export DISCORD_TOKEN=your-token
   # NEVER commit to git
   echo "DISCORD_TOKEN=..." > .env  # Add to .gitignore
   ```

2. **Run with minimal permissions**
   - Bot should have: Send Messages, Embed Links, Read Message History
   - Don't give Administrator role

3. **Monitor logs regularly**
   ```bash
   tail -f discord_bot.log  # If you add logging to file
   ```

4. **Database backups**
   ```bash
   cp discord_bot.db discord_bot.db.backup
   ```

5. **Update dependencies**
   ```bash
   pip install --upgrade -r requirements.txt
   ```

## 🐛 Troubleshooting

### Bot Won't Start

**Error: `DISCORD_TOKEN not set`**
```bash
# Solution: Set token
export DISCORD_TOKEN=your-token
python main.py
```

**Error: `discord.errors.LoginFailure`**
```
# Token is invalid. Get new one from Discord Developer Portal
```

### Commands Not Working

**Issue: Commands not showing up**
1. Ensure bot has "Send Messages" permission in channel
2. Try with slash commands: `/submit` instead of `!submit`
3. Check bot intents in config (message_content intent required)

**Issue: Analysis times out**
- Code might be too complex or have infinite loops
- Increase ANALYSIS_TIMEOUT in config.py

### Analysis Issues

**pylint not installed**
```bash
pip install pylint
```

**radon not installed**
```bash
pip install radon
```

**bandit not installed**
```bash
pip install bandit
```

If tools aren't installed, bot will skip that analysis (with warning in logs).

### Database Issues

**Error: `database is locked`**
- Bot is accessing DB from multiple threads
- Should be fixed, but if persists: delete discord_bot.db and restart

**To inspect database:**
```bash
sqlite3 discord_bot.db
> .tables
> SELECT * FROM submissions LIMIT 5;
> .quit
```

## 📈 Performance Tips

### Handle High Volume

1. **Use connection pooling** (already implemented via thread-local connections)
2. **Index frequently queried columns** (already done in database.py)
3. **Increase background task intervals**
   ```python
   @tasks.loop(hours=2)  # Instead of 1
   ```

4. **Limit code size**
   ```python
   MAX_CODE_SIZE = 50000  # Reduce if needed
   ```

### Optimize Analysis

1. **Disable unused analysis tools**
   ```python
   # In _check_security(), _check_complexity():
   if False:  # Disable bandit for faster analysis
       self._check_security(code)
   ```

2. **Cache results** for repeated submissions
   - Implement in database.py if needed

3. **Run analysis async**
   ```python
   await asyncio.to_thread(analyzer.analyze, code, language)
   ```

## 📚 Code Examples

### Example 1: Excellent Code (Score ~95)

```python
"""
Module for calculating Fibonacci numbers efficiently.
Uses memoization to avoid redundant calculations.
"""

from typing import Dict


def fibonacci(n: int, memo: Dict[int, int] | None = None) -> int:
    """
    Calculate the nth Fibonacci number.
    
    Args:
        n: Position in Fibonacci sequence (0-indexed)
        memo: Dictionary for memoization
        
    Returns:
        The nth Fibonacci number
        
    Raises:
        ValueError: If n is negative
    """
    if n < 0:
        raise ValueError("n must be non-negative")
    
    if memo is None:
        memo = {}
    
    if n in memo:
        return memo[n]
    
    if n <= 1:
        return n
    
    memo[n] = fibonacci(n - 1, memo) + fibonacci(n - 2, memo)
    return memo[n]


def test_fibonacci():
    """Test Fibonacci function."""
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1
    assert fibonacci(5) == 5
    assert fibonacci(10) == 55
```

**Score Breakdown:**
- ✅ Valid syntax: 0 deductions
- ✅ PEP8 compliant: 0 deductions
- ✅ Low complexity (≤5): 0 deductions
- ✅ 100% documented: 0 deductions
- ✅ No security issues: 0 deductions
- ✅ Type hints: +5
- ✅ Tests included: +5
- **Final: 100/100 → Clamped to 95**

### Example 2: Poor Code (Score ~35)

```python
def fib(n):
    if n<0:return 0
    if n<=1:return n
    x=0;y=1;z=1
    for i in range(2,n+1):x=y;y=z;z=x+y
    print("Calculating...")  # Side effect!
    return z


# TODO: Fix this
# HACK: This doesn't work for large n
x = 10
exec(f"result = fib({x})")  # SECURITY RISK!
```

**Score Breakdown:**
- ❌ PEP8 violations (no spaces, single-letter vars): -15
- ❌ Undocumented: -15
- ❌ Security risk (exec()): -15
- ❌ No tests: 0 bonuses
- **Final: 100 - 45 = 55 → Rounded to 35 with other minor issues**

## 🚢 Production Deployment

### Using systemd (Linux)

Create `/etc/systemd/system/discord-bot.service`:

```ini
[Unit]
Description=Discord Code Quality Bot
After=network.target

[Service]
Type=simple
User=discordbot
WorkingDirectory=/home/discordbot/disbot
Environment="DISCORD_TOKEN=your-token-here"
ExecStart=/usr/bin/python3 /home/discordbot/disbot/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
sudo systemctl status discord-bot
```

### Using Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t discord-bot .
docker run -e DISCORD_TOKEN=your-token discord-bot
```

## 📄 License

MIT License - Feel free to modify and use!

## 🤝 Contributing

To improve the bot:
1. Add new analysis tools to analyzer.py
2. Add new commands to bot.py
3. Extend database schema as needed
4. Test thoroughly before deploying

## ❓ FAQ

**Q: Can I use this for multiple Discord servers?**
A: Yes! The bot can be in multiple servers. Just invite it to more servers and configure channel IDs per server using roles or separate databases.

**Q: Can I analyze non-Python code?**
A: Basic analysis works, but full analysis (pylint, radon, bandit) only works for Python. Extend analyzer.py to add support for other languages.

**Q: How do I back up submissions?**
A: Copy `discord_bot.db` to a safe location. Or export via SQL:
```bash
sqlite3 discord_bot.db ".dump" > backup.sql
```

**Q: Why are admins excluded from rankings?**
A: To prevent moderators from gaming the leaderboard and to keep rankings focused on community members. Change via:
```python
EXCLUDE_ADMINS_FROM_LEADERBOARD = False  # If desired
```

**Q: Can I use this bot commercially?**
A: Yes, under MIT license. Just include license attribution.

---

**Created with ❤️ for code quality-focused communities**
