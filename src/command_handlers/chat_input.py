#!/usr/bin/env python3
"""Chat input handler for Claude Telegram Bridge."""

from typing import Tuple

from ..session_manager import SessionManager


class ChatInputHandler:
    """Handles non-command chat messages."""

    def __init__(self, session_manager: SessionManager):
        """Initialize chat input handler.

        Args:
            session_manager: SessionManager instance.
        """
        self.session_manager = session_manager

    def handle(self, chat_id: int, text: str) -> Tuple[bool, str]:
        """Handle chat input (non-command text).

        Args:
            chat_id: Telegram chat ID.
            text: Message text to send.

        Returns:
            Tuple of (success, response_message).
        """
        # Filter out command keywords (even without /) to prevent them from reaching LLM
        # These should always be used with / prefix
        command_keywords = {
            'help', 'new_session', 'sessions', 'end_session',
            'current_session', 'interrupt', 'select_session'
        }
        text_lower = text.strip().lower()
        if text_lower in command_keywords or text_lower.startswith('help ') or text_lower.startswith('/'):
            return False, (
                "❌ This appears to be a command.\n"
                "Please use the `/` prefix for commands (e.g., `/help` instead of `help`).\n"
                "Use `/help` to see all available commands."
            )

        # Check if session is selected
        selected_session = self.session_manager.get_selected_session(chat_id)

        if not selected_session:
            return False, (
                "❌ No session selected.\n\n"
                "Please select a session first:\n"
                "1. Run `/sessions` to see available sessions\n"
                "2. Run `/select_session {uuid}` to select one\n\n"
                "Or create a new session with `/new_session`."
            )

        # Send text to tmux session
        success, message = self.session_manager.send_keys(selected_session, text)

        if success:
            message = f"✅ Message sent to session `{selected_session}`\n\n"
            message += f"`{text}`"

        return success, message

    def get_prompt_message(self) -> str:
        """Get message when no session is selected."""
        return (
            "❌ No session selected.\n\n"
            "Please select a session first:\n"
            "1. Run `/sessions` to see available sessions\n"
            "2. Run `/select_session {uuid}` to select one\n\n"
            "Or create a new session with `/new_session`."
        )
