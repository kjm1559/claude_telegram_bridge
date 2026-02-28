#!/usr/bin/env python3
"""Sessions command handler for Claude Telegram Bridge."""

from typing import Tuple, List, Dict, Any

from session_manager import SessionManager


class SessionsCommand:
    """Handles the /sessions command."""

    def __init__(self, session_manager: SessionManager, db):
        """Initialize sessions command handler.

        Args:
            session_manager: SessionManager instance.
            db: Database instance.
        """
        self.session_manager = session_manager
        self.db = db

    def handle(self, chat_id: int) -> Tuple[bool, str]:
        """Handle /sessions command.

        Args:
            chat_id: Telegram chat ID.

        Returns:
            Tuple of (success, response_message).
        """
        # Get all sessions from database
        all_sessions = self.db.get_all_sessions()

        if not all_sessions:
            return True, (
                "❌ No sessions found.\n\n"
                "Create a new session using `/new_session`."
            )

        # Get active tmux sessions
        active_tmux_sessions = set(self.session_manager.get_all_active_sessions())

        # Format session list
        sessions_text = "**Active Sessions**:\n\n"
        inactive_count = 0

        for session in all_sessions:
            session_id = session["session_id"]
            is_active = session["is_active"] == 1
            tmux_active = session_id in active_tmux_sessions

            if not is_active:
                inactive_count += 1
                continue

            # Get formatted time
            created_at = session["created_at"]
            last_used = session["last_used"]

            sessions_text += f"🔹 **{session_id}**\n"
            sessions_text += f"   Directory: `{session['cwd']}`\n"
            sessions_text += f"   Created: {created_at}\n"
            sessions_text += f"   Last used: {last_used}\n"
            sessions_text += f"   Status: {'✅ Active' if tmux_active else '⏸️ Stopped'}\n\n"

        # Add inactive sessions info
        if inactive_count > 0:
            sessions_text += f"\n{inactive_count} inactive sessions hidden.\n"

        sessions_text += "\nUse `/select_session {uuid}` to select a session for messages."

        return True, sessions_text

    def get_description(self) -> str:
        """Get command description for help."""
        return (
            "/sessions - Lists all active Claude sessions\n\n"
            "Usage: `/sessions`\n"
            "Lists all currently active sessions with their IDs, directories, and status."
        )
