"""
Database module for the Discord Code Quality Bot.
Handles all SQLite operations for storing submissions, rankings, and violations.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import threading
import time

import config


@dataclass
class Submission:
    """Data class representing a code submission."""
    id: int
    user_id: int
    timestamp: datetime
    code: str
    language: str
    score: int
    feedback: Dict


@dataclass
class WeeklyRanking:
    """Data class representing a user's weekly ranking."""
    rank: int
    user_id: int
    avg_score: float
    submission_count: int


class Database:
    """
    SQLite database manager for the Discord bot.
    Handles submissions, rankings, and rule violations.
    Includes simple caching for performance optimization.
    """
    
    def __init__(self, db_path: str = config.DATABASE_PATH):
        """Initialize database connection with thread safety and caching."""
        self.db_path = db_path
        self.local = threading.local()
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes cache TTL
        self._init_db()
    
    def get_connection(self):
        """Get thread-local database connection."""
        if not hasattr(self.local, 'connection'):
            self.local.connection = sqlite3.connect(self.db_path, timeout=config.DB_TIMEOUT)
            self.local.connection.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrent access
            self.local.connection.execute('PRAGMA journal_mode=WAL')
            # Set busy timeout
            self.local.connection.execute(f'PRAGMA busy_timeout = {int(config.DB_TIMEOUT * 1000)}')
        return self.local.connection
    
    def _get_cache(self, key: str) -> Optional[any]:
        """Get cached value if not expired."""
        if key in self._cache:
            value, timestamp = self._cache[key]
            if time.time() - timestamp < self._cache_ttl:
                return value
            else:
                del self._cache[key]
        return None
    
    def _set_cache(self, key: str, value: any):
        """Cache a value with timestamp."""
        self._cache[key] = (value, time.time())
    
    def _invalidate_cache(self, pattern: str = None):
        """Invalidate cache entries matching pattern."""
        if pattern is None:
            self._cache.clear()
        else:
            keys_to_delete = [k for k in self._cache.keys() if pattern in k]
            for k in keys_to_delete:
                del self._cache[k]
    
    def _init_db(self):
        """Initialize database tables if they don't exist."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Submissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                code TEXT NOT NULL,
                language TEXT NOT NULL,
                score INTEGER NOT NULL,
                feedback TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Users table (for tracking)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Violations table (for rule monitoring)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS violations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                violation_type TEXT NOT NULL,
                message TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                resolved BOOLEAN DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Weekly rankings cache
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weekly_rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                week_start DATE NOT NULL,
                week_end DATE NOT NULL,
                user_id INTEGER NOT NULL,
                rank INTEGER NOT NULL,
                avg_score REAL NOT NULL,
                submission_count INTEGER NOT NULL,
                UNIQUE(week_start, user_id),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        ''')
        
        # Create indexes for performance
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_submissions_user ON submissions(user_id)'
        )
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_submissions_timestamp ON submissions(timestamp)'
        )
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_violations_user ON violations(user_id)'
        )
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_rankings_week ON weekly_rankings(week_start)'
        )
        
        conn.commit()
    
    # ========================================================================
    # SUBMISSION OPERATIONS
    # ========================================================================
    
    def add_submission(
        self,
        user_id: int,
        code: str,
        language: str,
        score: int,
        feedback: Dict
    ) -> int:
        """
        Store a new code submission.
        
        Args:
            user_id: Discord user ID
            code: Source code text
            language: Programming language
            score: Quality score (0-100)
            feedback: Analysis feedback as dict
        
        Returns:
            Submission ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Ensure user exists
        self._ensure_user_exists(user_id, f"User{user_id}")
        
        # Store feedback as JSON
        feedback_json = json.dumps(feedback)
        
        cursor.execute('''
            INSERT INTO submissions (user_id, code, language, score, feedback)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, code, language, score, feedback_json))
        
        conn.commit()
        
        # Invalidate cache for this user
        self._invalidate_cache(f'avg_score_{user_id}')
        
        return cursor.lastrowid
    
    def get_submission(self, submission_id: int) -> Optional[Submission]:
        """Retrieve a submission by ID."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, user_id, timestamp, code, language, score, feedback
            FROM submissions WHERE id = ?
        ''', (submission_id,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return Submission(
            id=row['id'],
            user_id=row['user_id'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            code=row['code'],
            language=row['language'],
            score=row['score'],
            feedback=json.loads(row['feedback'])
        )
    
    def get_user_submissions(
        self,
        user_id: int,
        limit: Optional[int] = None
    ) -> List[Submission]:
        """Get all submissions by a user, most recent first."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, user_id, timestamp, code, language, score, feedback
            FROM submissions
            WHERE user_id = ?
            ORDER BY timestamp DESC
        '''
        
        if limit:
            # Use parameterized query to prevent SQL injection
            query += ' LIMIT ?'
            cursor.execute(query, (user_id, limit))
        else:
            cursor.execute(query, (user_id,))
        
        submissions = []
        for row in cursor.fetchall():
            submissions.append(Submission(
                id=row['id'],
                user_id=row['user_id'],
                timestamp=datetime.fromisoformat(row['timestamp']),
                code=row['code'],
                language=row['language'],
                score=row['score'],
                feedback=json.loads(row['feedback'])
            ))
        
        return submissions
    
    def get_user_avg_score(self, user_id: int) -> float:
        """Calculate average score for a user (with caching)."""
        cache_key = f'avg_score_{user_id}'
        cached_result = self._get_cache(cache_key)
        if cached_result is not None:
            return cached_result
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT AVG(score) as avg_score
            FROM submissions
            WHERE user_id = ?
        ''', (user_id,))
        
        row = cursor.fetchone()
        avg = row['avg_score'] if row['avg_score'] else 0.0
        result = float(avg)
        
        self._set_cache(cache_key, result)
        return result
    
    def get_submission_count(self, user_id: int) -> int:
        """Get number of submissions by a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT COUNT(*) as count
            FROM submissions
            WHERE user_id = ?
        ''', (user_id,))
        
        return cursor.fetchone()['count']
    
    # ========================================================================
    # RANKING OPERATIONS
    # ========================================================================
    
    def generate_weekly_rankings(self) -> List[WeeklyRanking]:
        """
        Generate and store weekly rankings.
        Excludes admins if configured.
        Returns top LEADERBOARD_SIZE users.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Calculate date range (week boundaries)
        today = datetime.now().date()
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)
        
        # Query to get average scores per user for this week
        query = '''
            SELECT 
                user_id,
                AVG(score) as avg_score,
                COUNT(*) as submission_count
            FROM submissions
            WHERE DATE(timestamp) BETWEEN ? AND ?
            GROUP BY user_id
            ORDER BY avg_score DESC
            LIMIT ?
        '''
        
        cursor.execute(query, (week_start, week_end, config.LEADERBOARD_SIZE))
        rows = cursor.fetchall()
        
        rankings = []
        rank = 1
        
        for row in rows:
            user_id = row['user_id']
            
            # Skip admins if configured
            if config.EXCLUDE_ADMINS_FROM_LEADERBOARD:
                if user_id in config.ADMIN_USER_IDS:
                    continue
            
            ranking = WeeklyRanking(
                rank=rank,
                user_id=user_id,
                avg_score=float(row['avg_score']),
                submission_count=row['submission_count']
            )
            rankings.append(ranking)
            rank += 1
        
        # Store rankings in database
        for ranking in rankings:
            cursor.execute('''
                INSERT OR REPLACE INTO weekly_rankings 
                (week_start, week_end, user_id, rank, avg_score, submission_count)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                week_start,
                week_end,
                ranking.user_id,
                ranking.rank,
                ranking.avg_score,
                ranking.submission_count
            ))
        
        conn.commit()
        return rankings
    
    def get_latest_rankings(self) -> List[WeeklyRanking]:
        """Retrieve the most recent weekly rankings."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT week_start, MAX(week_start) as latest_week
            FROM weekly_rankings
            GROUP BY week_start
            ORDER BY week_start DESC
            LIMIT 1
        ''')
        
        result = cursor.fetchone()
        if not result:
            return []
        
        latest_week = result['week_start']
        
        cursor.execute('''
            SELECT rank, user_id, avg_score, submission_count
            FROM weekly_rankings
            WHERE week_start = ?
            ORDER BY rank ASC
        ''', (latest_week,))
        
        rankings = []
        for row in cursor.fetchall():
            rankings.append(WeeklyRanking(
                rank=row['rank'],
                user_id=row['user_id'],
                avg_score=float(row['avg_score']),
                submission_count=row['submission_count']
            ))
        
        return rankings
    
    # ========================================================================
    # VIOLATION OPERATIONS
    # ========================================================================
    
    def add_violation(
        self,
        user_id: int,
        violation_type: str,
        message: Optional[str] = None
    ) -> int:
        """
        Record a rule violation.
        
        Args:
            user_id: Discord user ID
            violation_type: Type of violation (e.g., 'banned_word', 'spam')
            message: Violation details
        
        Returns:
            Violation ID
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Ensure user exists
        self._ensure_user_exists(user_id, f"User{user_id}")
        
        cursor.execute('''
            INSERT INTO violations (user_id, violation_type, message)
            VALUES (?, ?, ?)
        ''', (user_id, violation_type, message))
        
        conn.commit()
        return cursor.lastrowid
    
    def get_user_violations(
        self,
        user_id: int,
        unresolved_only: bool = False
    ) -> List[Dict]:
        """Get violations for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT id, user_id, violation_type, message, timestamp, resolved
            FROM violations
            WHERE user_id = ?
        '''
        
        if unresolved_only:
            query += ' AND resolved = 0'
        
        query += ' ORDER BY timestamp DESC'
        
        cursor.execute(query, (user_id,))
        
        violations = []
        for row in cursor.fetchall():
            violations.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'type': row['violation_type'],
                'message': row['message'],
                'timestamp': datetime.fromisoformat(row['timestamp']),
                'resolved': bool(row['resolved'])
            })
        
        return violations
    
    def get_recent_violations(self, hours: int = 24) -> List[Dict]:
        """Get violations from the last N hours."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        cursor.execute('''
            SELECT id, user_id, violation_type, message, timestamp, resolved
            FROM violations
            WHERE timestamp > ?
            ORDER BY timestamp DESC
        ''', (cutoff_time.isoformat(),))
        
        violations = []
        for row in cursor.fetchall():
            violations.append({
                'id': row['id'],
                'user_id': row['user_id'],
                'type': row['violation_type'],
                'message': row['message'],
                'timestamp': datetime.fromisoformat(row['timestamp']),
                'resolved': bool(row['resolved'])
            })
        
        return violations
    
    def resolve_violation(self, violation_id: int) -> bool:
        """Mark a violation as resolved."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE violations
            SET resolved = 1
            WHERE id = ?
        ''', (violation_id,))
        
        conn.commit()
        return cursor.rowcount > 0
    
    # ========================================================================
    # USER OPERATIONS
    # ========================================================================
    
    def _ensure_user_exists(self, user_id: int, username: str):
        """Ensure a user record exists in the database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT user_id FROM users WHERE user_id = ?',
            (user_id,)
        )
        
        if not cursor.fetchone():
            cursor.execute('''
                INSERT INTO users (user_id, username)
                VALUES (?, ?)
            ''', (user_id, username))
            conn.commit()
    
    def update_username(self, user_id: int, username: str):
        """Update or create user record."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username)
            VALUES (?, ?)
        ''', (user_id, username))
        
        conn.commit()
    
    # ========================================================================
    # UTILITY OPERATIONS
    # ========================================================================
    
    def clear_old_data(self, days: int = 90):
        """Delete submissions and violations older than N days (maintenance)."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        cursor.execute(
            'DELETE FROM submissions WHERE timestamp < ?',
            (cutoff_date.isoformat(),)
        )
        
        cursor.execute(
            'DELETE FROM violations WHERE timestamp < ?',
            (cutoff_date.isoformat(),)
        )
        
        conn.commit()
    
    def get_database_stats(self) -> Dict:
        """Get database statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) as count FROM submissions')
        submission_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(DISTINCT user_id) as count FROM submissions')
        user_count = cursor.fetchone()['count']
        
        cursor.execute('SELECT COUNT(*) as count FROM violations')
        violation_count = cursor.fetchone()['count']
        
        return {
            'total_submissions': submission_count,
            'total_users': user_count,
            'total_violations': violation_count
        }
