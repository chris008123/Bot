"""
Example configurations for different use cases.
Copy and modify for your specific needs.
"""

# ============================================================================
# EXAMPLE 1: Small Community Server (10-50 members)
# ============================================================================

EXAMPLE_SMALL_COMMUNITY = """
# Small community - everyone is admin or trusted
DISCORD_TOKEN = "your-token-here"
COMMAND_PREFIX = "!"

ADMIN_USER_IDS = [
    123456789,  # Owner
    987654321,  # Moderator
]

ADMIN_ROLE_ID = None  # No role-based admins

# Channels
ANNOUNCEMENTS_CHANNEL_ID = 1111111111
SUBMISSION_CHANNEL_ID = 2222222222
MODERATION_LOG_CHANNEL_ID = 3333333333

# Scoring - More forgiving for small communities
SCORING_CONFIG = {
    "base_score": 100,
    "syntax_error_penalty": 15,      # Less strict
    "pep8_violations_penalty": 10,
    "complexity_penalty": 5,
    "missing_docs_penalty": 10,
    "security_issues_penalty": 10,
    "duplication_penalty": 3,
    "type_hints_bonus": 5,
    "comprehensive_tests_bonus": 5,
    "well_documented_bonus": 5,
}

# Leaderboard
LEADERBOARD_SIZE = 10
EXCLUDE_ADMINS_FROM_LEADERBOARD = True
RANKING_DAY = 0  # Monday
RANKING_HOUR = 12  # Noon UTC

# Rules
BANNED_WORDS = {"spam"}
SPAM_CONFIG = {
    "max_messages_per_minute": 10,
    "duplicate_threshold": 5,
    "caps_lock_threshold": 0.8,
}
"""


# ============================================================================
# EXAMPLE 2: Large Community Server (100+ members)
# ============================================================================

EXAMPLE_LARGE_COMMUNITY = """
# Large community - strict admins only, role-based
DISCORD_TOKEN = "your-token-here"
COMMAND_PREFIX = "!"

ADMIN_USER_IDS = []  # Use role instead
ADMIN_ROLE_ID = 1234567890  # "Moderators" role

# Channels
ANNOUNCEMENTS_CHANNEL_ID = 1111111111
SUBMISSION_CHANNEL_ID = 2222222222  # Restrict submissions
MODERATION_LOG_CHANNEL_ID = 3333333333

# Scoring - More strict for quality
SCORING_CONFIG = {
    "base_score": 100,
    "syntax_error_penalty": 25,  # No errors tolerated
    "pep8_violations_penalty": 20,
    "complexity_penalty": 15,
    "missing_docs_penalty": 20,
    "security_issues_penalty": 25,
    "duplication_penalty": 10,
    "type_hints_bonus": 10,  # Reward best practices
    "comprehensive_tests_bonus": 10,
    "well_documented_bonus": 10,
}

# Leaderboard
LEADERBOARD_SIZE = 20  # More competitive
EXCLUDE_ADMINS_FROM_LEADERBOARD = True
RANKING_DAY = 4  # Friday (more time to prepare)
RANKING_HOUR = 18  # 6 PM UTC

# Rules - More strict
BANNED_WORDS = {
    "spam", "scam", "hate", "inappropriate",
    "violence", "harassment",
}
SPAM_CONFIG = {
    "max_messages_per_minute": 3,
    "duplicate_threshold": 2,
    "caps_lock_threshold": 0.6,
}
"""


# ============================================================================
# EXAMPLE 3: Educational/University Setting
# ============================================================================

EXAMPLE_EDUCATIONAL = """
# Educational setting - focus on learning
DISCORD_TOKEN = "your-token-here"
COMMAND_PREFIX = "!"

ADMIN_USER_IDS = [
    111111111,  # Instructor
    222222222,  # TA
]

ADMIN_ROLE_ID = None

# Channels
ANNOUNCEMENTS_CHANNEL_ID = 1111111111
SUBMISSION_CHANNEL_ID = 2222222222  # Assignment submission
MODERATION_LOG_CHANNEL_ID = 3333333333

# Scoring - Educational feedback focused
SCORING_CONFIG = {
    "base_score": 100,
    "syntax_error_penalty": 20,
    "pep8_violations_penalty": 15,  # Code style teaching
    "complexity_penalty": 10,
    "missing_docs_penalty": 20,     # Docs crucial in education
    "security_issues_penalty": 15,
    "duplication_penalty": 5,
    "type_hints_bonus": 10,         # Reward good practices
    "comprehensive_tests_bonus": 15, # Tests very important
    "well_documented_bonus": 10,
}

# Leaderboard
LEADERBOARD_SIZE = 10
EXCLUDE_ADMINS_FROM_LEADERBOARD = True
RANKING_DAY = 3  # Wednesday (middle of week)
RANKING_HOUR = 14  # 2 PM UTC

# Rules - Focused on learning
BANNED_WORDS = {"spam", "cheat", "plagiarism"}
SPAM_CONFIG = {
    "max_messages_per_minute": 5,
    "duplicate_threshold": 3,
    "caps_lock_threshold": 0.7,
}

# Smaller size limit for student projects
MAX_CODE_SIZE = 25000  # 25KB
"""


# ============================================================================
# EXAMPLE 4: Competitive Coding Server (Leetcode, HackerRank)
# ============================================================================

EXAMPLE_COMPETITIVE = """
# Competitive coding - quality over quantity
DISCORD_TOKEN = "your-token-here"
COMMAND_PREFIX = "!"

ADMIN_USER_IDS = [999999999]  # Minimal admin

ADMIN_ROLE_ID = None

# Channels
ANNOUNCEMENTS_CHANNEL_ID = 1111111111
SUBMISSION_CHANNEL_ID = None  # Allow everywhere
MODERATION_LOG_CHANNEL_ID = None  # Less moderation needed

# Scoring - Focus on algo quality
SCORING_CONFIG = {
    "base_score": 100,
    "syntax_error_penalty": 30,  # Must compile
    "pep8_violations_penalty": 5,  # Less important
    "complexity_penalty": 20,     # O(n) vs O(n²) matters!
    "missing_docs_penalty": 5,    # Less docs needed
    "security_issues_penalty": 10,
    "duplication_penalty": 10,
    "type_hints_bonus": 3,
    "comprehensive_tests_bonus": 10,
    "well_documented_bonus": 3,
}

# Leaderboard - Weekly competition
LEADERBOARD_SIZE = 50  # Top 50
EXCLUDE_ADMINS_FROM_LEADERBOARD = False  # Admins can compete
RANKING_DAY = 6  # Sunday
RANKING_HOUR = 20  # 8 PM UTC

# Rules - Minimal restrictions
BANNED_WORDS = {"spam"}
SPAM_CONFIG = {
    "max_messages_per_minute": 10,
    "duplicate_threshold": 5,
    "caps_lock_threshold": 0.9,
}

# Larger size for algorithm submissions
MAX_CODE_SIZE = 100000  # 100KB
"""


# ============================================================================
# EXAMPLE 5: Open Source Project Community
# ============================================================================

EXAMPLE_OPENSOURCE = """
# Open source project - high quality standards
DISCORD_TOKEN = "your-token-here"
COMMAND_PREFIX = "!"

ADMIN_USER_IDS = [
    111111111,  # Project lead
    222222222,  # Lead dev
    333333333,  # Code reviewer
]

ADMIN_ROLE_ID = 5555555555  # "Maintainers" role

# Channels
ANNOUNCEMENTS_CHANNEL_ID = 1111111111
SUBMISSION_CHANNEL_ID = 2222222222  # Code review channel
MODERATION_LOG_CHANNEL_ID = 3333333333

# Scoring - Production quality
SCORING_CONFIG = {
    "base_score": 100,
    "syntax_error_penalty": 30,
    "pep8_violations_penalty": 20,  # Follow conventions
    "complexity_penalty": 20,       # Maintainability key
    "missing_docs_penalty": 25,     # Docs essential
    "security_issues_penalty": 30,  # Production security
    "duplication_penalty": 15,      # DRY principle
    "type_hints_bonus": 15,         # Modern Python
    "comprehensive_tests_bonus": 20,
    "well_documented_bonus": 15,
}

# Leaderboard - Recognition
LEADERBOARD_SIZE = 20
EXCLUDE_ADMINS_FROM_LEADERBOARD = False
RANKING_DAY = 4  # Friday releases
RANKING_HOUR = 17  # 5 PM UTC

# Rules
BANNED_WORDS = {"spam", "harassment"}
SPAM_CONFIG = {
    "max_messages_per_minute": 5,
    "duplicate_threshold": 3,
    "caps_lock_threshold": 0.7,
}

# GitHub integration (future)
# GITHUB_TOKEN = "your-github-token"
"""


# ============================================================================
# EXAMPLE 6: Minimalist Setup (Testing)
# ============================================================================

EXAMPLE_MINIMAL = """
# Minimal setup for testing/development
DISCORD_TOKEN = "your-test-token"
COMMAND_PREFIX = "!"

ADMIN_USER_IDS = [YOUR_USER_ID_HERE]

ADMIN_ROLE_ID = None

# Just one channel needed
ANNOUNCEMENTS_CHANNEL_ID = YOUR_CHANNEL_ID_HERE
SUBMISSION_CHANNEL_ID = None
MODERATION_LOG_CHANNEL_ID = None

# Default scoring
LEADERBOARD_SIZE = 10
EXCLUDE_ADMINS_FROM_LEADERBOARD = True
RANKING_DAY = 0
RANKING_HOUR = 12

BANNED_WORDS = {"spam"}

# All other settings use defaults from config.py
"""


if __name__ == "__main__":
    print("Configuration Examples")
    print("=" * 60)
    print("\nChoose which example matches your use case:")
    print("1. Small Community (10-50 members)")
    print("2. Large Community (100+ members)")
    print("3. Educational/University")
    print("4. Competitive Coding")
    print("5. Open Source Project")
    print("6. Minimal Setup (Testing)")
    
    choice = input("\nEnter choice (1-6): ")
    
    examples = {
        "1": ("Small Community", EXAMPLE_SMALL_COMMUNITY),
        "2": ("Large Community", EXAMPLE_LARGE_COMMUNITY),
        "3": ("Educational", EXAMPLE_EDUCATIONAL),
        "4": ("Competitive", EXAMPLE_COMPETITIVE),
        "5": ("Open Source", EXAMPLE_OPENSOURCE),
        "6": ("Minimal", EXAMPLE_MINIMAL),
    }
    
    if choice in examples:
        name, config = examples[choice]
        print(f"\n{name} Configuration:\n")
        print(config)
        print("\nCopy the above configuration and add to config.py")
    else:
        print("Invalid choice")
