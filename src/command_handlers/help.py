#!/usr/bin/env python3
"""Help command handler for Claude Telegram Bridge."""

from typing import Tuple, Optional


class HelpCommand:
    """Handles the /help command."""

    def __init__(self):
        """Initialize help command handler."""
        self.commands = {
            "/new_session": self._new_session_help,
            "/sessions": self._sessions_help,
            "/end_session": self._end_session_help,
            "/current_session": self._current_session_help,
            "/interrupt": self._interrupt_help,
            "/help": self._help_help,
        }

    def handle(self, chat_id: int, command: Optional[str] = None) -> Tuple[bool, str]:
        """Handle /help command.

        Args:
            chat_id: Telegram chat ID.
            command: Optional specific command to get help for.

        Returns:
            Tuple of (success, response_message).
        """
        if command:
            # Show help for specific command
            # Normalize command: remove leading slash for matching
            normalized_cmd = command.strip()
            if not normalized_cmd.startswith('/'):
                normalized_cmd = '/' + normalized_cmd
            normalized_cmd = normalized_cmd.lower()

            # Find matching command (case-insensitive)
            matched_cmd = None
            for cmd_key in self.commands:
                if cmd_key.lower() == normalized_cmd:
                    matched_cmd = cmd_key
                    break

            if matched_cmd:
                return True, self.commands[matched_cmd]()
            else:
                return False, f"Command '{command}' not found. Type /help for all commands."
        else:
            # Show general help
            return True, self._get_general_help()

    def _get_general_help(self) -> str:
        """Get general help message in HTML format."""
        return (
            "<b>Available Commands</b>:\n\n"
            "<b>Session Management</b>:\n"
            "  <code>/new_session</code> - Creates a new Claude session\n"
            "  <code>/sessions</code> - Lists active sessions\n"
            "  <code>/end_session {uuid}</code> - Terminate a session\n"
            "  <code>/select_session {uuid}</code> - Select a session\n"
            "  <code>/current_session</code> - Show selected session\n\n"
            "<b>Interaction</b>:\n"
            "  <code>/interrupt</code> - Stop running processes\n"
            "  (Just type text to send messages)\n\n"
            "<b>Help</b>:\n"
            "  <code>/help</code> - Show all commands\n"
            "  <code>/help \u003ccommand\u003e</code> - Show specific help\n\n"
            "Type <code>/help</code> for details."
        )

    def _new_session_help(self) -> str:
        """Get help for /new_session in HTML format."""
        return (
            "<code>/new_session</code> - Creates a new Claude session\n\n"
            "Usage: <code>/new_session</code>\n\n"
            "Creates a new session with:\n"
            "- Unique UUID as session ID\n"
            "- New tmux session with same name\n"
            "- Launches Claude with session ID\n"
            "- Records in SQLite database\n\n"
            "Returns: Session ID and confirmation message."
        )

    def _sessions_help(self) -> str:
        """Get help for /sessions in HTML format."""
        return (
            "<code>/sessions</code> - Lists all active Claude sessions\n\n"
            "Usage: <code>/sessions</code>\n\n"
            "Lists all currently active sessions with:\n"
            "- Session ID (UUID)\n"
            "- Working directory\n"
            "- Creation time\n"
            "- Last used time\n"
            "- Active status\n\n"
            "Use this list to select a session."
        )

    def _end_session_help(self) -> str:
        """Get help for /end_session in HTML format."""
        return (
            "<code>/end_session {uuid}</code> - Terminates a Claude session\n\n"
            "Usage: <code>/end_session {uuid}</code>\n\n"
            "Arguments:\n"
            "- {uuid}: The session ID to terminate\n\n"
            "Terminates the specified tmux session and marks it as inactive.\n"
            "Use /sessions to see available session IDs."
        )

    def _current_session_help(self) -> str:
        """Get help for /current_session in HTML format."""
        return (
            "<code>/current_session</code> - Shows currently selected session\n\n"
            "Usage: <code>/current_session</code>\n\n"
            "Displays information about the selected session:\n"
            "- Session ID\n"
            "- Working directory\n"
            "- Creation and last used timestamps\n\n"
            "If no session is selected, prompts to select one."
        )

    def _interrupt_help(self) -> str:
        """Get help for /interrupt in HTML format."""
        return (
            "<code>/interrupt</code> - Sends interrupt signal\n\n"
            "Usage: <code>/interrupt</code>\n\n"
            "Sends Escape key to current tmux session.\n"
            "Requires a session to be selected first.\n\n"
            "Use when Claude is stuck."
        )

    def _help_help(self) -> str:
        """Get help for /help in HTML format."""
        return (
            "<code>/help</code> - Displays available commands\n\n"
            "Usage: <code>/help</code> or <code>/help \<command\></code>\n\n"
            "Without arguments: Shows all commands.\n"
            "With argument: Shows help for specific command.\n\n"
            "Examples:\n"
            "  <code>/help</code> - Show all commands\n"
            "  <code>/help new_session</code> - Show help for /new_session"
        )
