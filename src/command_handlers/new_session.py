#!/usr/bin/env python3
"""New session command handler for Claude Telegram Bridge."""

import os
from typing import Tuple

from ..session_manager import SessionManager


class NewSessionCommand:
    """Handles the /new_session command."""

    def __init__(self, session_manager: SessionManager):
        """Initialize new session command handler.

        Args:
            session_manager: SessionManager instance.
        """
        self.session_manager = session_manager

    def handle(self, chat_id: int) -> Tuple[bool, str]:
        """Handle /new_session command.

        Args:
            chat_id: Telegram chat ID.

        Returns:
            Tuple of (success, response_message).
        """
        # Generate new UUID
        session_id = self.session_manager.generate_uuid()

        # Get current working directory
        cwd = os.getcwd()

        # Create new session
        success, message = self.session_manager.create_session(session_id, cwd)

        if success:
            # Auto-select the new session
            self.session_manager.select_session(chat_id, session_id)
            message = (
                f"✅ New session created!\n\n"
                f"Session ID: `{session_id}`\n"
                f"Working Directory: `{cwd}`\n\n"
                f"You can now send messages to this session.\n"
                f"Use `/current_session` to check status."
            )

        return success, message

    def get_description(self) -> str:
        """Get command description for help."""
        return (
            "/new_session - Creates a new Claude session\n\n"
            "Usage: `/new_session`\n"
            "Creates a new session with unique UUID, tmux session, and database record."
        )
