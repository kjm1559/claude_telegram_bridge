#!/usr/bin/env python3
"""Interrupt command handler for Claude Telegram Bridge."""

from typing import Tuple, Dict, Any


class InterruptCommand:
    """Handles the /interrupt command."""

    def __init__(self, session_manager, db):
        """Initialize interrupt command handler.

        Args:
            session_manager: SessionManager instance.
            db: Database instance.
        """
        self.session_manager = session_manager
        self.db = db

    def handle(self, chat_id: int) -> Tuple[bool, str]:
        """Handle /interrupt command.

        Args:
            chat_id: Telegram chat ID.

        Returns:
            Tuple of (success, response_message).
        """
        # Check if session is selected
        selected_session = self.session_manager.get_selected_session(chat_id)

        if not selected_session:
            return False, (
                "No session selected.\n"
                "Please select a session using /sessions and /select_session command."
            )

        # Send interrupt to session
        success, message = self.session_manager.send_interrupt(selected_session)

        return success, message

    def get_description(self) -> str:
        """Get command description for help."""
        return (
            "/interrupt - Sends interrupt signal (Escape key) to stop running Claude processes\n"
            "Usage: /interrupt\n"
            "Sends Escape key to the current tmux session to interrupt running processes."
            "Requires a session to be selected."
        )
