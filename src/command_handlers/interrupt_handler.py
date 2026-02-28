#!/usr/bin/env python3
"""Interrupt command handler for Claude Telegram Bridge."""

from typing import Tuple


class InterruptHandler:
    """Handles /interrupt command."""

    def __init__(self, session_manager, db):
        """Initialize interrupt handler.

        Args:
            session_manager: SessionManager instance.
            db: Database instance.
        """
        self.session_manager = session_manager
        self.db = db

    def handle(self, chat_id: int, session_id: str) -> Tuple[bool, str]:
        """Handle interrupt command.

        Args:
            chat_id: Telegram chat ID.
            session_id: UUID of the session to interrupt.

        Returns:
            Tuple of (success, message).
        """
        # Send interrupt signal
        success, message = self.session_manager.send_interrupt(session_id)

        return success, message

    def send_interrupt_signal(self, session_id: str) -> Tuple[bool, str]:
        """Send interrupt signal to session.

        Args:
            session_id: UUID of the session.

        Returns:
            Tuple of (success, message).
        """
        # Check if session exists and is active
        if not self.session_manager.is_session_active(session_id):
            return False, f"Session {session_id} is not active or does not exist"

        # Send Escape key
        return self.session_manager.send_interrupt(session_id)
