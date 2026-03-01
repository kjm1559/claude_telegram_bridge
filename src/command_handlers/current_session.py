#!/usr/bin/env python3
"""Current session command handler for Claude Telegram Bridge."""

from typing import Tuple

from ..session_manager import SessionManager


class CurrentSessionCommand:
    """Handles the /current_session command."""

    def __init__(self, session_manager: SessionManager):
        """Initialize current session command handler.

        Args:
            session_manager: SessionManager instance.
        """
        self.session_manager = session_manager

    def handle(self, chat_id: int) -> Tuple[bool, str]:
        """Handle /current_session command.

        Args:
            chat_id: Telegram chat ID.

        Returns:
            Tuple of (success, response_message).
        """
        # Get selected session
        selected_session = self.session_manager.get_selected_session(chat_id)

        if not selected_session:
            return False, (
                "❌ No session selected.\n\n"
                "Select a session using `/sessions` and `/select_session {uuid}`.\n\n"
                "Use `/new_session` to create a new session."
            )

        # Get session info
        session_info = self.session_manager.get_session_info(selected_session)

        if not session_info:
            return False, (
                f"❌ Session `{selected_session}` not found or has expired.\n\n"
                "Please create a new session with `/new_session`."
            )

        # Format response
        response = (
            f"**Current Session:**\n\n"
            f"🆔 **Session ID:** `{selected_session}`\n\n"
            f"📁 **Working Directory:** `{session_info['cwd']}`\n\n"
            f"📅 **Created:** {session_info['created_at']}\n\n"
            f"🕐 **Last Used:** {session_info['last_used']}\n\n"
            f"✅ **Status:** {'Active' if session_info['is_active'] else 'Stopped'}\n\n"
            f"You can now send messages to this session."
        )

        # Update last_used timestamp
        self.session_manager.db.update_session_last_used(selected_session)

        return True, response

    def get_description(self) -> str:
        """Get command description for help."""
        return (
            "/current_session - Shows currently selected Claude session\n\n"
            "Usage: `/current_session`\n"
            "Displays information about the currently selected session."
        )
