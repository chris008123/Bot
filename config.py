"""
Configuration module for the Discord Code Quality Bot.
Centralized settings management for all bot operations.
"""

import os
from typing import List, Set
from dotenv import load_dotenv

# ============================================================================
# DISCORD BOT CONFIGURATION
# ============================================================================

load_dotenv()

# Bot token (use environment variable in production)
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")

# Command prefix (also supports slash commands)
COMMAND_PREFIX = "!"

# ============================================================================
# ADMIN CONFIGURATION
# ============================================================================

# Method 1: Specific user IDs (recommended for production)
ADMIN_USER_IDS: List[int] = [
    1401906822268457161,  # Replace with actual Discord user ID
    1408911831279472640,  # Second admin
]

# Method 2: Admin role ID (alternative, but Method 1 is more flexible)
# If you prefer role-based admin detection, set this:
ADMIN_ROLE_ID: int = 1401906822268457161  # Set to role ID if using roles, e.g., 1234567890

# Whether to exclude admins from leaderboard
EXCLUDE_ADMINS_FROM_LEADERBOARD = True

# ============================================================================
# CHANNEL CONFIGURATION
# ============================================================================

# Channel where members submit code
SUBMISSION_CHANNEL_ID: int = 1452474657184682142  # Set your submission channel ID

# Channel where leaderboard is posted
ANNOUNCEMENTS_CHANNEL_ID: int = 1452474774659010692  # Set your announcements channel ID

# Moderation log channel
MODERATION_LOG_CHANNEL_ID: int = 1452474916409446605  # Set your moderation channel ID

# ============================================================================
# SUBMISSION SETTINGS
# ============================================================================

# Supported code file extensions
SUPPORTED_EXTENSIONS: Set[str] = {
    ".py",  # Python
    ".js", ".ts",  # JavaScript/TypeScript
    ".java",  # Java
    ".cpp", ".cc", ".cxx",  # C++
    ".c",  # C
    ".go",  # Go
    ".rs",  # Rust
}

# Maximum code size in characters (prevent abuse)
MAX_CODE_SIZE = 50000  # 50KB

# Maximum file attachment size in bytes
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# ============================================================================
# SCORING CONFIGURATION
# ============================================================================

# Scoring rubric (weights and thresholds)
SCORING_CONFIG = {
    "base_score": 100,
    "syntax_error_penalty": 20,
    "pep8_violations_penalty": 15,
    "complexity_penalty": 10,
    "complexity_threshold": 10,  # Cyclomatic complexity limit
    "missing_docs_penalty": 15,
    "security_issues_penalty": 15,
    "duplication_penalty": 5,
    "duplication_threshold": 10,  # % of duplicated code
    
    # Bonuses
    "type_hints_bonus": 5,
    "comprehensive_tests_bonus": 5,
    "well_documented_bonus": 5,
}

# Pylint score thresholds (out of 10)
PYLINT_THRESHOLDS = {
    "excellent": 9.0,  # 9.0+
    "good": 7.0,        # 7.0-8.9
    "acceptable": 5.0,  # 5.0-6.9
    "poor": 0.0,        # Below 5.0
}

# ============================================================================
# RULE MONITORING CONFIGURATION
# ============================================================================

# Banned words/phrases (case-insensitive)
BANNED_WORDS: Set[str] = {
    "spam",
    "scam",
    "fuck",  # Add actual banned words
    "fucking",
    "shit",
    "sex",
    "nigga",
    "negro",
}

# Spam detection thresholds
SPAM_CONFIG = {
    "max_messages_per_minute": 5,
    "duplicate_threshold": 3,  # Same message 3+ times in 5 minutes
    "caps_lock_threshold": 0.7,  # 70% caps = spam
}

# ============================================================================
# WEEKLY RANKING SETTINGS
# ============================================================================

# Day to generate rankings (0=Monday, 6=Sunday)
RANKING_DAY = 0  # Monday

# Time to generate rankings (24-hour format)
RANKING_HOUR = 7  # Noon

# Number of users in top leaderboard
LEADERBOARD_SIZE = 10

# Minimum submissions to appear on leaderboard
MIN_SUBMISSIONS_FOR_LEADERBOARD = 1

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================

# SQLite database file path
DATABASE_PATH = "discord_bot.db"

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

LOG_LEVEL = "INFO"

# Timezone for timestamps
TIMEZONE = "UTC"

# ============================================================================
# SAFETY & PERFORMANCE
# ============================================================================

# Timeout for code analysis (seconds)
ANALYSIS_TIMEOUT = 30

# Maximum concurrent analysis tasks
MAX_CONCURRENT_ANALYSIS = 5

# Enable detailed error logging
DEBUG_MODE = False

# Database connection timeout (seconds)
DB_TIMEOUT = 5

# Discord API call timeout (seconds)
DISCORD_API_TIMEOUT = 10

# Maximum temporary file size in bytes (prevents abuse)
MAX_TEMP_FILE_SIZE = 1024 * 1024  # 1MB

# Code analysis memory limit (for subprocess calls)
# Set via ulimit or process group limits
ANALYSIS_MEMORY_LIMIT = None  # In bytes, None = no limit
