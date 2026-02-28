#!/usr/bin/env python3
"""Database module for Claude Telegram Bridge."""

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List, Any


class Database:
    """SQLite database handler for session management."""

    def __init__(self, db_path: Path):
        """Initialize database connection.

        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._ensure_directory()
        self._init_tables()

    def _ensure_directory(self):
        """Create database directory if it doesn't exist."""
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection.

        Returns:
            SQLite database connection.
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_tables(self):
        """Initialize database tables."""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    cwd TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active INTEGER DEFAULT 1
                )
            """)

            # User context table (stores selected session)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_context (
                    chat_id INTEGER PRIMARY KEY,
                    selected_session_id TEXT,
                    FOREIGN KEY (selected_session_id) REFERENCES sessions(session_id)
                )
            """)

            # Session progress tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_progress (
                    session_id TEXT PRIMARY KEY,
                    last_processed_message_index INTEGER DEFAULT 0,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (session_id) REFERENCES sessions(session_id)
                )
            """)

            conn.commit()

    def create_session(self, session_id: str, cwd: str) -> bool:
        """Create a new session record.

        Args:
            session_id: UUID of the session.
            cwd: Current working directory.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO sessions (session_id, cwd, created_at, last_used, is_active)
                    VALUES (?, ?, ?, ?, 1)
                """, (session_id, cwd, datetime.now(), datetime.now()))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error creating session: {e}")
            return False

    def delete_session(self, session_id: str) -> bool:
        """Delete a session record.

        Args:
            session_id: UUID of the session to delete.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
                cursor.execute("DELETE FROM session_progress WHERE session_id = ?", (session_id,))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error deleting session: {e}")
            return False

    def update_session_last_used(self, session_id: str) -> bool:
        """Update the last_used timestamp for a session.

        Args:
            session_id: UUID of the session.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions SET last_used = ? WHERE session_id = ?
                """, (datetime.now(), session_id))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error updating session: {e}")
            return False

    def deactivate_session(self, session_id: str) -> bool:
        """Mark a session as inactive.

        Args:
            session_id: UUID of the session.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE sessions SET is_active = 0 WHERE session_id = ?
                """, (session_id,))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error deactivating session: {e}")
            return False

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session information.

        Args:
            session_id: UUID of the session.

        Returns:
            Session data as dictionary or None if not found.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                if row:
                    return dict(row)
                return None
        except sqlite3.Error as e:
            print(f"Database error getting session: {e}")
            return None

    def get_all_sessions(self) -> List[Dict[str, Any]]:
        """Get all session records.

        Returns:
            List of session dictionaries.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions ORDER BY last_used DESC")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error getting all sessions: {e}")
            return []

    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """Get all active sessions.

        Returns:
            List of active session dictionaries.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM sessions WHERE is_active = 1 ORDER BY last_used DESC")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            print(f"Database error getting active sessions: {e}")
            return []

    def set_user_session(self, chat_id: int, session_id: str) -> bool:
        """Set selected session for a user.

        Args:
            chat_id: Telegram chat ID.
            session_id: UUID of the session to select.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO user_context (chat_id, selected_session_id)
                    VALUES (?, ?)
                    ON CONFLICT(chat_id) DO UPDATE SET selected_session_id = ?, last_used = CURRENT_TIMESTAMP
                """, (chat_id, session_id, session_id))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error setting user session: {e}")
            return False

    def get_user_session(self, chat_id: int) -> Optional[str]:
        """Get selected session for a user.

        Args:
            chat_id: Telegram chat ID.

        Returns:
            Session ID or None if not set.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT selected_session_id FROM user_context WHERE chat_id = ?", (chat_id,))
                row = cursor.fetchone()
                if row and row['selected_session_id']:
                    return row['selected_session_id']
                return None
        except sqlite3.Error as e:
            print(f"Database error getting user session: {e}")
            return None

    def update_session_progress(self, session_id: str, message_index: int) -> bool:
        """Update session progress tracking.

        Args:
            session_id: UUID of the session.
            message_index: Last processed message index.

        Returns:
            True if successful, False otherwise.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO session_progress (session_id, last_processed_message_index, last_updated)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(session_id) DO UPDATE SET
                        last_processed_message_index = excluded.last_processed_message_index,
                        last_updated = CURRENT_TIMESTAMP
                """, (session_id, message_index))
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error updating session progress: {e}")
            return False

    def get_session_progress(self, session_id: str) -> Optional[int]:
        """Get session progress.

        Args:
            session_id: UUID of the session.

        Returns:
            Last processed message index or None.
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT last_processed_message_index FROM session_progress WHERE session_id = ?",
                    (session_id,)
                )
                row = cursor.fetchone()
                if row:
                    return row['last_processed_message_index']
                return 0
        except sqlite3.Error as e:
            print(f"Database error getting session progress: {e}")
            return None
