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
            if command in self.commands:
                return True, self.commands[command]()
            else:
                return False, f"Command '{command}' not found. Type /help for all commands."
        else:
            # Show general help
            return True, self._get_general_help()

    def _get_general_help(self) -> str:
        """Get general help message."""
        return (
            "*Available Commands*:\n\n"
            "*Session Management*:\n"
            "  `/new_session` - Creates a new Claude session with UUID, tmux session, and database update\n"
            "  `/sessions` - Lists all currently active Claude sessions\n"
            "  `/end_session {uuid}` - Terminates a specific Claude session by UUID and updates database\n"
            "  `/select_session {uuid}` - Selects a session for sending chat messages\n"
            "  `/current_session` - Displays currently selected Claude session information\n\n"
            "*Interaction*:\n"
            "  `/interrupt` - Sends interrupt signal (Escape key) to stop running Claude processes\n"
            "  (Just type text to send messages to selected session)\n\n"
            "*Help*:\n"
            "  `/help` - Displays this help message\n"
            "  `/help <command>` - Show detailed help for a specific command\n\n"
            "Type `/help <command>` for detailed information about a specific command."
        )

    def _new_session_help(self) -> str:
        """Get help for /new_session."""
        return (
            "/new_session - Creates a new Claude session\n\n"
            "Usage: `/new_session`\n\n"
            "Creates a new session with:\n"
            "- Unique UUID as session ID\n"
            "- New tmux session with same name\n"
            "- Launches Claude with session ID\n"
            "- Records in SQLite database\n\n"
            "Returns: Session ID and confirmation message."
        )

    def _sessions_help(self) -> str:
        """Get help for /sessions."""
        return (
            "/sessions - Lists all active Claude sessions\n\n"
            "Usage: `/sessions`\n\n"
            "Lists all currently active sessions with:\n"
            "- Session ID (UUID)\n"
            "- Working directory\n"
            "- Creation time\n"
            "- Last used time\n"
            "- Active status\n\n"
            "Use this list to select a session with /select_session."
        )

    def _end_session_help(self) -> str:
        """Get help for /end_session."""
        return (
            "/end_session {uuid} - Terminates a Claude session\n\n"
            "Usage: `/end_session {uuid}`\n\n"
            "Arguments:\n"
            "- `{uuid}`: The session ID to terminate\n\n"
            "Terminates the specified tmux session and marks it as inactive in database.\n"
            "Use `/sessions` to see available session IDs."
        )

    def _current_session_help(self) -> str:
        """Get help for /current_session."""
        return (
            "/current_session - Shows currently selected session\n\n"
            "Usage: `/current_session`\n\n"
            "Displays information about the session currently selected for sending messages:\n"
            "- Session ID\n"
            "- Working directory\n"
            "- Creation and last used timestamps\n\n"
            "If no session is selected, prompts you to select one."
        )

    def _interrupt_help(self) -> str:
        """Get help for /interrupt."""
        return (
            "/interrupt - Sends interrupt signal to stop running Claude processes\n\n"
            "Usage: `/interrupt`\n\n"
            "Sends Escape key to the current tmux session to interrupt running processes.\n"
            "Requires a session to be selected first.\n\n"
            "Use when Claude is stuck or you need to stop a long-running process."
        )

    def _help_help(self) -> str:
        """Get help for /help."""
        return (
            "/help - Displays available commands and help information\n\n"
            "Usage: `/help` or `/help <command>`\n\n"
            "Without arguments: Shows all available commands.\n"
            "With argument: Shows detailed help for specific command.\n\n"
            "Examples:\n"
            "  `/help` - Show all commands\n"
            "  `/help new_session` - Show help for /new_session"
        )
