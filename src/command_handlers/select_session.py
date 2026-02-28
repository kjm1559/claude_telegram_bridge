#!/usr/bin/env python3
"""Select session command handler for Claude Telegram Bridge."""

import re
from typing import Tuple, Optional

from session_manager import SessionManager


class SelectSessionCommand:
    """Handles the /select_session command."""

    def __init__(self, session_manager: SessionManager):
        """Initialize select session command handler.

        Args:
            session_manager: SessionManager instance.
        """
        self.session_manager = session_manager

    def handle(self, chat_id: int, message: str) -> Tuple[bool, str]:
        """Handle /select_session command.

        Args:
            chat_id: Telegram chat ID.
            message: Full message text (command + arguments).

        Returns:
            Tuple of (success, response_message).
        """
        # Parse UUID from message
        session_id = self._parse_uuid(message)

        if not session_id:
            return False, (
                "❌ Invalid session ID.\n\n"
                "Usage: `/select_session {uuid}`\n\n"
                "Where `{uuid}` is the session ID to select.\n"
                "Use `/sessions` to see available session IDs."
            )

        # Validate UUID format
        if not self._is_valid_uuid(session_id):
            return False, (
                f"❌ Invalid UUID format: `{session_id}`\n\n"
                "Session ID must be a valid UUID."
            )

        # Verify session exists and is active
        success, message = self.session_manager.select_session(chat_id, session_id)

        return success, message

    def _parse_uuid(self, message: str) -> Optional[str]:
        """Parse UUID from command message.

        Args:
            message: Full message text.

        Returns:
            UUID string or None.
        """
        # Remove command prefix
        message = message.strip()
        if message.startswith("/select_session"):
            message = re.sub(r"^/select_session\s*", "", message, flags=re.IGNORECASE)

        message = message.strip()

        # Check if it's a valid UUID format
        if self._is_valid_uuid(message):
            return message

        return None

    def _is_valid_uuid(self, value: str) -> bool:
        """Check if string is a valid UUID.

        Args:
            value: String to check.

        Returns:
            True if valid UUID, False otherwise.
        """
        uuid_pattern = re.compile(
            r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
            re.IGNORECASE
        )
        return bool(uuid_pattern.match(value))

    def get_description(self) -> str:
        """Get command description for help."""
        return (
            "/select_session {uuid} - Selects a session for chat messages\n\n"
            "Usage: `/select_session {uuid}`\n"
            "Selects a session to send chat messages to."
        )
