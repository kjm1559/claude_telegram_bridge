#!/usr/bin/env python3
"""Main entry point for Claude Telegram Bridge."""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config import BASE_DIR, DATABASE_PATH
from database import Database
from session_manager import SessionManager
from command_handlers import (
    NewSessionCommand,
    SessionsCommand,
    EndSessionCommand,
    CurrentSessionCommand,
    InterruptCommand,
    HelpCommand,
    ChatInputHandler,
    SelectSessionCommand,
)


class CommandHandler:
    """Handles Telegram commands and messages."""

    def __init__(self, session_manager: SessionManager, db: Database):
        """Initialize command handler.

        Args:
            session_manager: SessionManager instance.
            db: Database instance.
        """
        self.session_manager = session_manager
        self.db = db

        # Initialize command handlers
        self.commands = {
            "/new_session": NewSessionCommand(session_manager),
            "/sessions": SessionsCommand(session_manager, db),
            "/end_session": EndSessionCommand(session_manager),
            "/current_session": CurrentSessionCommand(session_manager),
            "/interrupt": InterruptCommand(session_manager, db),
            "/help": HelpCommand(),
            "/select_session": SelectSessionCommand(session_manager),
        }

        self.chat_input = ChatInputHandler(session_manager)

    def process_command(self, chat_id: int, message: str) -> tuple:
        """Process a Telegram command.

        Args:
            chat_id: Telegram chat ID.
            message: Full message text including command.

        Returns:
            Tuple of (success, response_message).
        """
        # Extract command and arguments
        parts = message.strip().split(None, 1)
        if not parts:
            return False, "Invalid command format."

        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        # Route to appropriate handler
        if command in self.commands:
            if command == "/help":
                # /help can take optional command argument
                target_cmd = args.strip() if args else None
                return self.commands["/help"].handle(chat_id, target_cmd)
            elif command in ["/end_session", "/select_session"]:
                return self.commands[command].handle(chat_id, message.strip())
            else:
                return self.commands[command].handle(chat_id)
        else:
            return False, f"Unknown command: {command}. Type /help for available commands."

    def process_chat_input(self, chat_id: int, text: str) -> tuple:
        """Process non-command chat input.

        Args:
            chat_id: Telegram chat ID.
            text: Message text.

        Returns:
            Tuple of (success, response_message).
        """
        return self.chat_input.handle(chat_id, text)

    def handle_message(self, chat_id: int, text: str) -> tuple:
        """Handle any incoming message.

        Args:
            chat_id: Telegram chat ID.
            text: Message text.

        Returns:
            Tuple of (success, response_message).
        """
        # Check if it's a command (starts with /)
        if text.strip().startswith("/"):
            return self.process_command(chat_id, text)
        else:
            return self.process_chat_input(chat_id, text)


class TelegramBridge:
    """Main Telegram Bridge class."""

    def __init__(self, bot_token: str):
        """Initialize Telegram Bridge.

        Args:
            bot_token: Telegram bot API token.
        """
        self.bot_token = bot_token
        self.db = Database(DATABASE_PATH)
        self.session_manager = SessionManager(self.db)
        self.command_handler = CommandHandler(self.session_manager, self.db)

    def get_active_sessions(self) -> list:
        """Get list of active sessions.

        Returns:
            List of active session dictionaries.
        """
        return self.db.get_active_sessions()

    def handle_update(self, chat_id: int, text: str) -> str:
        """Handle incoming update.

        Args:
            chat_id: Telegram chat ID.
            text: Message text.

        Returns:
            Response message text.
        """
        success, response = self.command_handler.handle_message(chat_id, text)

        if success:
            return f"✅ {response}"
        else:
            return f"❌ {response}"


def main():
    """Main entry point for CLI usage."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set")
        print("Please set your Telegram bot token and try again.")
        sys.exit(1)

    bridge = TelegramBridge(bot_token)
    print("✅ Claude Telegram Bridge initialized successfully")
    print(f"   Database: {DATABASE_PATH}")
    print(f"   Active sessions: {len(bridge.get_active_sessions())}")


if __name__ == "__main__":
    main()
