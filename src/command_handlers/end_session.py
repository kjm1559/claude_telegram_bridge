#!/usr/bin/env python3
"""End session command handler for Claude Telegram Bridge."""

import uuid as uuid_lib
from typing import Tuple, Optional
import re

from ..session_manager import SessionManager


class EndSessionCommand:
    """Handles the /end_session command."""

    def __init__(self, session_manager: SessionManager):
        """Initialize end session command handler.

        Args:
            session_manager: SessionManager instance.
        """
        self.session_manager = session_manager

    def handle(self, chat_id: int, message: str) -> Tuple[bool, str]:
        """Handle /end_session command.

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
                "Usage: `/end_session {uuid}`\n\n"
                "Where `{uuid}` is the session ID to terminate.\n"
                "Use `/sessions` to see available session IDs."
            )

        # Validate UUID format
        if not self._is_valid_uuid(session_id):
            return False, (
                f"❌ Invalid UUID format: `{session_id}`\n\n"
                "Session ID must be a valid UUID."
            )

        # Verify session exists
        session_info = self.session_manager.get_session_info(session_id)
        if not session_info:
            return False, (
                f"❌ Session `{session_id}` not found in database.\n\n"
                "Use `/sessions` to see available sessions."
            )

        # End the session
        success, message = self.session_manager.end_session(session_id)

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
        if message.startswith("/end_session"):
            message = re.sub(r"^/end_session\s*", "", message, flags=re.IGNORECASE)

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
            "/end_session {uuid} - Terminates a Claude session\n\n"
            "Usage: `/end_session {uuid}`\n"
            "Terminates the specified tmux session and marks it inactive in database."
        )
