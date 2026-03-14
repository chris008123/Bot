# 🚀 Implementation & Deployment Guide

## Overview

This document explains how the bot works internally, key design decisions, and how to deploy it to production.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Code Analysis Pipeline](#code-analysis-pipeline)
3. [Database Design](#database-design)
4. [Security Architecture](#security-architecture)
5. [Performance Optimization](#performance-optimization)
6. [Deployment Strategies](#deployment-strategies)
7. [Troubleshooting Guide](#troubleshooting-guide)

---

## System Architecture

### Component Interaction Flow

```
Discord User
    ↓
    ├─ Sends !submit command
    ↓
    └─→ bot.py:submit_code()
        ├─ Extracts code (file/block/reply)
        ├─ Validates size & format
        ├─ Calls analyzer.analyze()
        │   ├─ analyzer.py:_analyze_python()
        │   │   ├─ _check_syntax() [ast module]
        │   │   ├─ _check_pep8() [pylint subprocess]
        │   │   ├─ _check_complexity() [radon subprocess]
        │   │   ├─ _check_documentation() [ast]
        │   │   ├─ _check_security() [bandit subprocess]
        │   │   ├─ _check_duplication() [custom logic]
        │   │   ├─ _check_type_hints() [ast + bonus]
        │   │   └─ _check_tests() [heuristic + bonus]
        │   └─ Returns (score: int, feedback: dict)
        ├─ Stores in database.py:add_submission()
        │   └─ SQLite insert
        └─ Posts embed with results
```

### Data Flow

**Submission Flow:**
```
User Code
    ↓ (validator checks size, syntax)
    ↓ (multiple analysis tools run in subprocess)
    ↓ (scoring formula calculates 0-100)
Database (submissions table)
    ↓
Weekly Rankings (background task)
    ↓
Leaderboard Posted to Discord
```

**Monitoring Flow:**
```
Message Content
    ↓
Rule Monitor (background task hourly)
    ├─ Check banned words
    ├─ Check spam patterns
    ├─ Check caps lock spam
    ↓
Violations Table (database)
    ↓
Admin DM Alert
```

### Key Design Decisions

| Decision | Reasoning |
|----------|-----------|
| **Subprocess for external tools** | Safety & isolation; pylint/radon can hang on bad code |
| **30-second timeout** | Prevent bot freeze from complex code |
| **SQLite (not PostgreSQL)** | Simplicity, no server needed, production-ready |
| **Thread-local DB connections** | discord.py is async; thread-safe DB access |
| **Scoring formula exposed** | Transparency; users know exactly why score is X |
| **Admin whitelist (not role)** | More flexible; can add non-role admins |
| **Background tasks hourly** | Cheap CPU, reliable Discord message posting |

---

## Code Analysis Pipeline

### Detailed Analysis Process

#### 1. Syntax Validation (ast module)

```python
# Low-level, safe parsing of Python code
try:
    tree = ast.parse(code)
    # If this succeeds, code is syntactically valid
except SyntaxError as e:
    # Deduct 20 points
```

**Why ast?**
- Built-in, no external dependency
- Fast and safe
- Gives exact line numbers for errors

#### 2. Style Checking (pylint)

```python
# Runs pylint in subprocess (isolated)
result = subprocess.run(
    ['pylint', '--output-format=json', temp_file],
    timeout=30  # Safety timeout
)

# Parses JSON output for violations:
# - Convention (naming, spacing)
# - Refactor (complexity, duplication)
# - Warning (potential bugs)
# - Error (actual errors)
```

**Scoring Logic:**
- 0-5 violations: -7 points (half penalty)
- 6+ violations: -15 points (full penalty)

**Why pylint?**
- Industry standard for Python
- JSON output easy to parse
- Configurable rules

#### 3. Complexity Analysis (radon)

```python
# Measures cyclomatic complexity per function
result = subprocess.run(
    ['radon', 'cc', '-j', temp_file],
    timeout=30
)

# Find max complexity across all functions
# If max > 10: Deduct 10 points
```

**Cyclomatic Complexity Explained:**
```python
# Complexity 1 - straightforward
def add(a, b):
    return a + b

# Complexity 2 - one branch
def check(x):
    if x > 0:
        return "positive"
    return "non-positive"

# Complexity 5+ - hard to test
def complex_logic(a, b, c):
    if a > 0:
        if b > 0:
            if c > 0:
                return a + b + c
            return a + b
        return a
    return 0
```

**Why radon?**
- Python-specific
- Accurate metrics
- Visual output for learning

#### 4. Documentation Check (ast)

```python
tree = ast.parse(code)

# Count functions/classes with docstrings
total = count_functions() + count_classes()
documented = count_with_docstrings()
percentage = documented / total * 100

# Scoring:
# < 50%: -15 points
# 50-79%: -7 points
# 80%+: 0 deductions
# If 80%+: +5 bonus
```

**Docstring Quality:**
```python
# Good: Descriptive docstring
def calculate_fibonacci(n: int) -> int:
    """
    Calculate the nth Fibonacci number using memoization.
    
    Args:
        n: Position in sequence (0-indexed)
    
    Returns:
        The nth Fibonacci number
    """

# Poor: No docstring
def fib(n):
    if n <= 1: return n
    return fib(n-1) + fib(n-2)
```

#### 5. Security Check (bandit)

```python
# Scans for security issues
result = subprocess.run(
    ['bandit', '-f', 'json', temp_file],
    timeout=30
)

# Finds:
# - SQL injection risks (exec, eval)
# - Hardcoded credentials
# - Insecure algorithms
# - File permission issues
```

**Examples Bandit Catches:**
```python
# SECURITY RISK: exec() with user input
user_code = input("Enter code: ")
exec(user_code)  # Bandit flags this

# SECURITY RISK: SQL injection
query = f"SELECT * FROM users WHERE id={user_id}"
db.execute(query)  # Bandit flags this

# SECURITY RISK: Hardcoded password
PASSWORD = "admin123"  # Bandit flags this
```

#### 6. Code Duplication (Custom Logic)

```python
# Simple line-by-line comparison
lines = code.split('\n')
code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]

# Count repeated lines
line_counts = {}
for line in code_lines:
    line_counts[line] = line_counts.get(line, 0) + 1

# Calculate percentage
duplicates = sum(count - 1 for count in line_counts.values() if count > 1)
percentage = duplicates / len(code_lines) * 100

# Scoring:
# > 10%: -5 points
```

**Note:** This is intentionally simple to avoid false positives.

#### 7. Bonuses

```python
# Type Hints Bonus (+5)
# - Check if 50%+ of functions have annotations
def good(x: int) -> str:  # Has type hints
    return str(x)

# Test Detection Bonus (+5)
# - Look for unittest/pytest imports or test_ functions
import unittest
def test_my_function():
    pass

# Documentation Bonus (+5)
# - Awarded if documentation percentage >= 80%
```

### Scoring Algorithm

```
FINAL_SCORE = max(0, min(100, FORMULA))

where FORMULA = (
    BASE_SCORE (100)
    - SUM(deductions)
    + SUM(bonuses)
)

Example:
  Base: 100
  - Syntax Error: 20 → 80
  - PEP8: 15 → 65
  - No Docs: 15 → 50
  + Type Hints: 5 → 55
  + Tests: 5 → 60
  
  FINAL: 60/100 = 👍 Good
```

---

## Database Design

### Schema Overview

```sql
-- Submissions (main table)
CREATE TABLE submissions (
    id INTEGER PRIMARY KEY,           -- Unique submission ID
    user_id INTEGER NOT NULL,         -- Discord user ID
    timestamp DATETIME,               -- When submitted
    code TEXT NOT NULL,               -- Source code
    language TEXT NOT NULL,           -- "python", "javascript", etc.
    score INTEGER NOT NULL,           -- 0-100 score
    feedback TEXT NOT NULL            -- JSON feedback
);

-- Weekly Rankings (computed table)
CREATE TABLE weekly_rankings (
    id INTEGER PRIMARY KEY,
    week_start DATE,                  -- Monday of week
    user_id INTEGER,                  -- Discord user ID
    rank INTEGER,                     -- 1-10 (or more)
    avg_score REAL,                   -- Average score that week
    submission_count INTEGER          -- How many submissions
);

-- Rule Violations
CREATE TABLE violations (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    violation_type TEXT,              -- "banned_word", "spam", etc.
    message TEXT,                     -- Details
    timestamp DATETIME,
    resolved BOOLEAN DEFAULT 0        -- Admin resolved?
);

-- User Tracking
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    created_at DATETIME
);
```

### Indexing Strategy

```sql
-- For fast lookups by user
CREATE INDEX idx_submissions_user ON submissions(user_id);

-- For time-range queries (leaderboards, reports)
CREATE INDEX idx_submissions_timestamp ON submissions(timestamp);

-- For violation lookups
CREATE INDEX idx_violations_user ON violations(user_id);

-- For weekly ranking queries
CREATE INDEX idx_rankings_week ON weekly_rankings(week_start);
```

### Query Performance

**Most common query (weekly leaderboard):**
```sql
SELECT user_id, AVG(score) as avg_score, COUNT(*) as submission_count
FROM submissions
WHERE DATE(timestamp) BETWEEN ? AND ?
GROUP BY user_id
ORDER BY avg_score DESC
LIMIT 10;
```

- Uses index on `timestamp`
- Fast even with 10,000 submissions
- Executes in <50ms

**User stats query:**
```sql
SELECT AVG(score) FROM submissions WHERE user_id = ?;
```

- Uses index on `user_id`
- <10ms response time

### Data Retention

```python
# Optional: Delete old data monthly
def cleanup_old_data():
    db.clear_old_data(days=90)  # Delete >90 days old
```

**Backup Strategy:**
```bash
# Simple backup (copy database)
cp discord_bot.db discord_bot.db.backup

# SQL export (version control compatible)
sqlite3 discord_bot.db ".dump" > backup.sql

# Restore from backup
sqlite3 discord_bot.db < backup.sql
```

---

## Security Architecture

### Threat Model

| Threat | Mitigation |
|--------|-----------|
| **SQL Injection** | Parameterized queries everywhere |
| **Bot Token Exposure** | Environment variables only, .gitignore db |
| **Code Execution** | Subprocess with timeout, safe analysis tools |
| **DoS (Large Code)** | Size limits (50KB default) |
| **Privilege Escalation** | Admin ID whitelist checked on each command |
| **Data Leak** | Database encrypted at rest (todo for production) |
| **Malicious Code in Submissions** | Static analysis only, no execution |

### Secure Coding Practices

**1. Parameterized Queries (SQL Injection Prevention)**

✅ SAFE:
```python
cursor.execute(
    'SELECT * FROM users WHERE id = ?',
    (user_id,)  # Separate from query
)
```

❌ UNSAFE:
```python
cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')
```

**2. Admin Permission Checks**

✅ SAFE:
```python
@bot.command()
async def admin_command(ctx):
    if ctx.author.id not in config.ADMIN_USER_IDS:
        await ctx.send("❌ Permission denied")
        return
```

❌ UNSAFE:
```python
@commands.is_owner()  # Too broad, only checks bot owner
async def admin_command(ctx):
    pass
```

**3. Subprocess Safety**

✅ SAFE:
```python
result = subprocess.run(
    ['pylint', temp_file],
    timeout=30,
    capture_output=True
)
```

❌ UNSAFE:
```python
os.system(f'pylint {user_code_file}')  # Shell injection!
```

**4. File Handling**

✅ SAFE:
```python
with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
    f.write(code)
    temp_file = f.name
# ... use temp_file ...
Path(temp_file).unlink()  # Always cleanup
```

❌ UNSAFE:
```python
with open('code.py', 'w') as f:
    f.write(code)  # No cleanup, security risk
```

### Production Security Checklist

- [ ] Token stored in environment variable (not config.py)
- [ ] Database file has restrictive permissions (600)
- [ ] Regular backups encrypted
- [ ] Logs don't contain sensitive data
- [ ] Admin IDs verified (not defaults)
- [ ] Bot has minimal Discord permissions
- [ ] HTTPS used for any external APIs
- [ ] Deps updated: `pip install --upgrade -r requirements.txt`

---

## Performance Optimization

### Current Bottlenecks

```
Submission → Analysis (0-5 seconds)
            └─ Most time spent running pylint/radon/bandit

Background Tasks → Database queries (0.1 seconds)
```

### Optimization Strategies

#### 1. Analysis Parallelization

```python
# Current: Sequential
def analyze(code):
    check_syntax()        # 0.1s
    check_pep8()          # 2s
    check_complexity()    # 1s
    check_security()      # 1.5s
    # Total: ~4.5s

# Optimized: Parallel
async def analyze_parallel(code):
    results = await asyncio.gather(
        asyncio.to_thread(check_syntax),
        asyncio.to_thread(check_pep8),
        asyncio.to_thread(check_complexity),
        asyncio.to_thread(check_security),
    )
    # Total: ~2s (slowest task)
```

#### 2. Caching Results

```python
# Cache identical submissions
submission_cache = {}

def analyze(code):
    code_hash = hashlib.sha256(code.encode()).hexdigest()
    
    if code_hash in submission_cache:
        return submission_cache[code_hash]
    
    score, feedback = analyzer.analyze(code)
    submission_cache[code_hash] = (score, feedback)
    
    return score, feedback
```

#### 3. Lazy Tool Loading

```python
# Only run tools if needed
@property
def has_pylint(self):
    if not hasattr(self, '_has_pylint'):
        self._has_pylint = shutil.which('pylint') is not None
    return self._has_pylint

# Skip missing tools gracefully
if self.has_pylint:
    self._check_pep8(code)
```

#### 4. Database Query Optimization

```python
# Batch inserts (if adding multiple)
cursor.executemany(
    'INSERT INTO submissions VALUES (?, ?, ?)',
    [(user1, code1, score1), (user2, code2, score2)]
)

# Use LIMIT in queries
cursor.execute(
    'SELECT * FROM submissions WHERE user_id = ? LIMIT 10',
    (user_id,)
)
```

---

## Deployment Strategies

### Option 1: Local Machine (Development)

```bash
git clone <repo>
cd disbot
pip install -r requirements.txt
export DISCORD_TOKEN=your-token
python main.py
```

**Pros:** Simple, easy to debug
**Cons:** Requires keeping computer on 24/7

### Option 2: VPS (Recommended)

**On DigitalOcean, AWS, Linode, etc.**

```bash
# 1. Connect to VPS
ssh root@your-vps-ip

# 2. Install Python
apt-get update && apt-get install python3-pip python3-venv

# 3. Clone repo
git clone <repo> /opt/discord-bot
cd /opt/discord-bot

# 4. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 5. Install dependencies
pip install -r requirements.txt

# 6. Create systemd service
sudo nano /etc/systemd/system/discord-bot.service
```

**systemd Service File:**
```ini
[Unit]
Description=Discord Code Quality Bot
After=network.target

[Service]
Type=simple
User=discordbot
WorkingDirectory=/opt/discord-bot
Environment="DISCORD_TOKEN=your-token"
ExecStart=/opt/discord-bot/venv/bin/python main.py
Restart=on-failure
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Enable and Run:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl start discord-bot
sudo systemctl status discord-bot

# View logs
sudo journalctl -u discord-bot -f
```

**Pros:** Reliable 24/7, cheap ($5/month)
**Cons:** Need to manage server

### Option 3: Docker

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    pylint radon bandit \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code
COPY . .

# Run bot
CMD ["python", "main.py"]
```

**Build & Run:**
```bash
docker build -t discord-bot .
docker run -e DISCORD_TOKEN=your-token discord-bot
```

**With Docker Compose:**
```yaml
version: '3'
services:
  bot:
    build: .
    environment:
      - DISCORD_TOKEN=${DISCORD_TOKEN}
    volumes:
      - ./discord_bot.db:/app/discord_bot.db
    restart: unless-stopped
```

**Pros:** Consistent environment, easy deployment
**Cons:** Docker overhead, learning curve

### Option 4: Cloud Functions (Serverless)

Using Google Cloud Functions / AWS Lambda (not recommended for this use case as bot needs persistent connection).

---

## Troubleshooting Guide

### Bot Won't Start

**Problem:** `discord.errors.LoginFailure`

```python
# Check token
>>> import os
>>> os.getenv("DISCORD_TOKEN")
'your-token-here'  # Should show token, not None
```

**Solution:**
```bash
export DISCORD_TOKEN=your-actual-token
python main.py
```

### Commands Not Working

**Problem:** `CommandNotFound` errors

**Possible Causes:**
1. Missing intents
   ```python
   # bot.py should have:
   intents = discord.Intents.default()
   intents.message_content = True
   ```

2. Wrong command prefix
   ```python
   # Check config.COMMAND_PREFIX
   # Use !submit not /submit (unless slash commands)
   ```

3. Bot lacks permissions
   - Bot needs "Send Messages" in channel

**Solution:**
```bash
# Test with !help
# If that works, bot is fine
# If not, re-invite with correct permissions
```

### Submissions Timeout

**Problem:** "Analysis timed out" message

**Cause:** Code too complex or analysis tool hung

**Solutions:**
1. Increase timeout in config.py
   ```python
   ANALYSIS_TIMEOUT = 60  # Instead of 30
   ```

2. User's code has infinite loop
   - Not much we can do, code is buggy

3. System is overloaded
   - Reduce MAX_CONCURRENT_ANALYSIS

### Database Errors

**Problem:** `database is locked`

**Cause:** Multiple async tasks accessing DB simultaneously

**Solution:**
- Already fixed in database.py with thread-local connections
- If persists: `rm discord_bot.db` (creates new)

**Inspect Database:**
```bash
sqlite3 discord_bot.db
sqlite> .tables
sqlite> SELECT COUNT(*) FROM submissions;
sqlite> .quit
```

### Memory Leak

**Problem:** Bot uses increasing memory over time

**Cause:** Unclosed resources in subprocesses

**Solution:**
```python
# Ensure temp files are cleaned up
Path(temp_file).unlink(missing_ok=True)

# Monitor with:
ps aux | grep python
```

### Admin Commands Denied

**Problem:** "You lack permissions" for !violations

**Cause:** User ID not in ADMIN_USER_IDS

**Solution:**
1. Get correct user ID
   - Discord: User Settings → Advanced → Developer Mode
   - Right-click user → Copy User ID

2. Add to config.py
   ```python
   ADMIN_USER_IDS = [YOUR_ID_HERE, OTHER_ADMIN_ID]
   ```

3. Restart bot

### Leaderboard Not Posting

**Problem:** Weekly rankings don't appear

**Cause:** Wrong channel ID or bot can't send messages

**Solution:**
1. Check channel ID in config.py
   ```python
   ANNOUNCEMENTS_CHANNEL_ID = 1234567890
   ```

2. Verify bot has "Send Messages" permission in channel

3. Check logs for errors

---

## Monitoring & Maintenance

### Daily Checks

```bash
# Is bot running?
systemctl status discord-bot

# Check recent logs
journalctl -u discord-bot -n 50

# Database size
du -h discord_bot.db
```

### Weekly Tasks

```bash
# Backup database
cp discord_bot.db discord_bot.db.$(date +%Y%m%d).backup

# Check for errors
grep ERROR discord_bot.log | tail -20
```

### Monthly Tasks

```bash
# Update dependencies
pip install --upgrade -r requirements.txt

# Clean old data (optional)
python -c "from database import Database; Database().clear_old_data(days=90)"

# Review user violations
# Check admin moderation logs
```

### Yearly Tasks

- Audit admin IDs (remove inactive mods)
- Review and update scoring formula
- Consider adding new analysis tools
- Update Discord.py if major version released

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────┐
│                    Discord Server                       │
│  (Users send commands, receive results, view rankings)  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ↓
        ┌────────────────────────┐
        │    Discord Bot API     │
        │    (discord.py lib)    │
        └────────┬───────────────┘
                 │
    ┌────────────┼────────────┐
    ↓            ↓            ↓
┌────────┐  ┌─────────┐  ┌────────────┐
│ bot.py │  │config.py│  │ database.py│
│ Events │  │Settings │  │   SQLite   │
│Commands│  │AdminIDs │  │ Backups    │
└────┬───┘  └─────────┘  └────────────┘
     │
     ├─→ analyzer.py
     │   ├─ ast (syntax)
     │   ├─ pylint (style) ← subprocess
     │   ├─ radon (complexity) ← subprocess
     │   ├─ bandit (security) ← subprocess
     │   └─ custom (duplication, docs)
     │
     └─→ Background Tasks (1x/hour)
         ├─ Generate rankings
         └─ Report violations
```

---

## Contributing

To extend the bot:

1. **Add new analysis tool**
   - Add method to `analyzer.py`
   - Update scoring in formula
   - Test thoroughly

2. **Add new command**
   - Add method to `bot.py` with `@bot.command()`
   - Add admin checks if needed
   - Update README

3. **Add database feature**
   - Update schema in `database.py:_init_db()`
   - Add CRUD methods
   - Test with existing data

---

For production use, this architecture scales to:
- 100s of users
- 1000s of submissions
- Real-time rankings
- <5 second analysis time

For larger scale (1000s of users), consider:
- PostgreSQL instead of SQLite
- Caching layer (Redis)
- Async analysis workers
- Rate limiting per guild
