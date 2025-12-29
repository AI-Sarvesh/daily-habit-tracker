"""
Database layer for habit tracker
Handles all SQLite operations with multi-user support
"""

import sqlite3
from datetime import date, datetime, timedelta
from typing import List, Dict, Optional
import os


class HabitDatabase:
    def __init__(self, db_path: str = "data/habits.db"):
        """Initialize database connection"""
        self.db_path = db_path
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        self._create_tables()
        self._migrate_tables()
    
    def _get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_path)
    
    def _create_tables(self):
        """Create necessary tables if they don't exist"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Habits table (with user_id for multi-user support)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL DEFAULT 'default',
                name TEXT NOT NULL,
                description TEXT,
                created_at DATE NOT NULL,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Habit logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER NOT NULL,
                log_date DATE NOT NULL,
                completed BOOLEAN DEFAULT 0,
                FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
                UNIQUE(habit_id, log_date)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def _migrate_tables(self):
        """Migrate existing tables to add user_id column if needed"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check if user_id column exists
        cursor.execute("PRAGMA table_info(habits)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'user_id' not in columns:
            cursor.execute("ALTER TABLE habits ADD COLUMN user_id TEXT NOT NULL DEFAULT 'default'")
            conn.commit()
        
        conn.close()
    
    # ===== HABIT OPERATIONS =====
    
    def add_habit(self, name: str, description: str = "", user_id: str = "default") -> int:
        """Add a new habit for a user"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO habits (user_id, name, description, created_at, is_active)
            VALUES (?, ?, ?, ?, 1)
        """, (user_id, name, description, date.today()))
        
        habit_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return habit_id
    
    def get_all_habits(self, active_only: bool = True, user_id: str = "default") -> List[Dict]:
        """Get all habits for a user"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if active_only:
            cursor.execute("""
                SELECT * FROM habits WHERE is_active = 1 AND user_id = ? ORDER BY created_at
            """, (user_id,))
        else:
            cursor.execute("SELECT * FROM habits WHERE user_id = ? ORDER BY created_at", (user_id,))
        
        habits = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return habits
    
    def get_habit(self, habit_id: int) -> Optional[Dict]:
        """Get a specific habit"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM habits WHERE id = ?", (habit_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_habit(self, habit_id: int, name: str, description: str):
        """Update habit details"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE habits 
            SET name = ?, description = ?
            WHERE id = ?
        """, (name, description, habit_id))
        
        conn.commit()
        conn.close()
    
    def delete_habit(self, habit_id: int):
        """Soft delete a habit"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE habits SET is_active = 0 WHERE id = ?
        """, (habit_id,))
        
        conn.commit()
        conn.close()
    
    def hard_delete_habit(self, habit_id: int):
        """Permanently delete a habit and all its logs"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM habit_logs WHERE habit_id = ?", (habit_id,))
        cursor.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
        
        conn.commit()
        conn.close()
    
    # ===== HABIT LOG OPERATIONS =====
    
    def log_habit(self, habit_id: int, log_date: date, completed: bool):
        """Log a habit for a specific date"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO habit_logs (habit_id, log_date, completed)
            VALUES (?, ?, ?)
            ON CONFLICT(habit_id, log_date) 
            DO UPDATE SET completed = ?
        """, (habit_id, log_date, completed, completed))
        
        conn.commit()
        conn.close()
    
    def get_logs_for_date(self, log_date: date, user_id: str = "default") -> List[Dict]:
        """Get all habit logs for a specific date for a user"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT h.id as habit_id, h.name, h.description,
                   COALESCE(hl.completed, 0) as completed
            FROM habits h
            LEFT JOIN habit_logs hl ON h.id = hl.habit_id AND hl.log_date = ?
            WHERE h.is_active = 1 AND h.user_id = ?
            ORDER BY h.created_at
        """, (log_date, user_id))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return logs
    
    def get_habit_logs(self, habit_id: int, start_date: date = None, 
                       end_date: date = None) -> List[Dict]:
        """Get logs for a specific habit within date range"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute("""
                SELECT * FROM habit_logs 
                WHERE habit_id = ? AND log_date BETWEEN ? AND ?
                ORDER BY log_date DESC
            """, (habit_id, start_date, end_date))
        else:
            cursor.execute("""
                SELECT * FROM habit_logs 
                WHERE habit_id = ?
                ORDER BY log_date DESC
            """, (habit_id,))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return logs
    
    def get_all_logs(self, start_date: date = None, end_date: date = None, user_id: str = "default") -> List[Dict]:
        """Get all logs within date range for a user"""
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if start_date and end_date:
            cursor.execute("""
                SELECT hl.*, h.name as habit_name
                FROM habit_logs hl
                JOIN habits h ON hl.habit_id = h.id
                WHERE hl.log_date BETWEEN ? AND ? AND h.is_active = 1 AND h.user_id = ?
                ORDER BY hl.log_date DESC, h.name
            """, (start_date, end_date, user_id))
        else:
            cursor.execute("""
                SELECT hl.*, h.name as habit_name
                FROM habit_logs hl
                JOIN habits h ON hl.habit_id = h.id
                WHERE h.is_active = 1 AND h.user_id = ?
                ORDER BY hl.log_date DESC, h.name
            """, (user_id,))
        
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return logs
    
    # ===== LEADERBOARD / MULTI-USER STATS =====
    
    def get_user_stats(self, user_id: str, start_date: date = None, end_date: date = None) -> Dict:
        """Get statistics for a specific user"""
        if not start_date:
            start_date = date.today() - timedelta(days=6)
        if not end_date:
            end_date = date.today()
        
        habits = self.get_all_habits(user_id=user_id)
        if not habits:
            return {
                "total_habits": 0,
                "completion_rate": 0,
                "completed_today": False,
                "current_streak": 0
            }
        
        # Get logs for date range
        conn = self._get_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as completed
            FROM habit_logs hl
            JOIN habits h ON hl.habit_id = h.id
            WHERE h.user_id = ? AND hl.completed = 1 
            AND hl.log_date BETWEEN ? AND ? AND h.is_active = 1
        """, (user_id, start_date, end_date))
        
        completed = cursor.fetchone()['completed']
        
        total_possible = len(habits) * ((end_date - start_date).days + 1)
        completion_rate = (completed / total_possible * 100) if total_possible > 0 else 0
        
        # Check if completed today
        cursor.execute("""
            SELECT COUNT(*) as completed_today
            FROM habit_logs hl
            JOIN habits h ON hl.habit_id = h.id
            WHERE h.user_id = ? AND hl.log_date = ? AND hl.completed = 1 AND h.is_active = 1
        """, (user_id, date.today()))
        
        completed_today_count = cursor.fetchone()['completed_today']
        completed_today = completed_today_count == len(habits) if habits else False
        
        # Calculate streak (consecutive days with all habits completed)
        current_streak = 0
        check_date = date.today()
        
        while True:
            cursor.execute("""
                SELECT COUNT(*) as completed
                FROM habit_logs hl
                JOIN habits h ON hl.habit_id = h.id
                WHERE h.user_id = ? AND hl.log_date = ? AND hl.completed = 1 AND h.is_active = 1
            """, (user_id, check_date))
            
            day_completed = cursor.fetchone()['completed']
            
            if day_completed == len(habits) and len(habits) > 0:
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break
            
            # Safety limit
            if current_streak > 365:
                break
        
        conn.close()
        
        return {
            "total_habits": len(habits),
            "completion_rate": round(completion_rate, 1),
            "completed_today": completed_today,
            "current_streak": current_streak
        }
    
    def get_all_users_from_habits(self) -> List[str]:
        """Get list of all users who have habits"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT user_id FROM habits WHERE is_active = 1")
        users = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return users
