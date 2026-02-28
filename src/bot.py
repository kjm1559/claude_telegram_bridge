#!/usr/bin/env python3
"""Telegram bot for Claude Bridge."""

import os
import logging
from pathlib import Path

try:
    import telebot
    from telebot import types
except ImportError:
    print("❌ Error: python-telegram-bot not installed")
    print("Install with: pip install python-telegram-bot")
    raise

from config import BASE_DIR, TELEGRAM_BOT_TOKEN
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

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


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

    def process_command(self, chat_id: int, message: str) -> str:
        """Process a Telegram command.

        Args:
            chat_id: Telegram chat ID.
            message: Full message text including command.

        Returns:
            Response message text.
        """
        parts = message.strip().split(None, 1)
        if not parts:
            return "❌ Invalid command format.\n\nType `/help` for available commands."

        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if command in self.commands:
            if command == "/help":
                target_cmd = args.strip() if args else None
                success, response = self.commands["/help"].handle(chat_id, target_cmd)
            elif command in ["/end_session", "/select_session"]:
                success, response = self.commands[command].handle(chat_id, message.strip())
            else:
                success, response = self.commands[command].handle(chat_id)

            if success:
                return f"✅ {response}"
            else:
                return f"❌ {response}"
        else:
            return f"❌ Unknown command: {command}.\n\nType `/help` for available commands."

    def process_chat_input(self, chat_id: int, text: str) -> str:
        """Process non-command chat input.

        Args:
            chat_id: Telegram chat ID.
            text: Message text.

        Returns:
            Response message text.
        """
        success, response = self.chat_input.handle(chat_id, text)
        return f"{'✅' if success else '❌'} {response}"

    def handle_message(self, chat_id: int, text: str) -> str:
        """Handle any incoming message.

        Args:
            chat_id: Telegram chat ID.
            text: Message text.

        Returns:
            Response message text.
        """
        if text.strip().startswith("/"):
            return self.process_command(chat_id, text)
        else:
            return self.process_chat_input(chat_id, text)


class TelegramBot:
    """Telegram Bot for Claude Bridge."""

    def __init__(self, bot_token: str):
        """Initialize Telegram Bot.

        Args:
            bot_token: Telegram bot API token.
        """
        self.bot = telebot.TeleBot(bot_token)
        self.db = Database(Path(BASE_DIR) / "sessions.db")
        self.session_manager = SessionManager(self.db)
        self.command_handler = CommandHandler(self.session_manager, self.db)

        # Register message handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register Telegram bot message handlers."""

        @self.bot.message_handler(commands=["start"])
        def handle_start(message):
            self.bot.send_message(
                message.chat.id,
                "👋 Welcome to Claude Telegram Bridge!\n\n"
                "Use the following commands to manage your Claude sessions:\n\n"
                "`/new_session` - Create a new session\n"
                "`/sessions` - List active sessions\n"
                "`/end_session {uuid}` - Terminate a session\n"
                "`/select_session {uuid}` - Select a session for messages\n"
                "`/current_session` - Show selected session\n"
                "`/interrupt` - Stop running processes\n"
                "`/help` - Show all commands\n\n"
                "Type `/help` to see all available commands."
            )

        @self.bot.message_handler(commands=["help"])
        def handle_help(message):
            text = message.text
            success, response = self.command_handler.process_command(message.chat.id, text)
            self.bot.send_message(message.chat.id, f"{response}")

        @self.bot.message_handler(commands=["new_session"])
        def handle_new_session(message):
            response = self.command_handler.process_command(message.chat.id, message.text)
            self.bot.send_message(message.chat.id, response)

        @self.bot.message_handler(commands=["sessions"])
        def handle_sessions(message):
            response = self.command_handler.process_command(message.chat.id, message.text)
            self.bot.send_message(message.chat.id, response)

        @self.bot.message_handler(commands=["end_session"])
        def handle_end_session(message):
            response = self.command_handler.process_command(message.chat.id, message.text)
            self.bot.send_message(message.chat.id, response)

        @self.bot.message_handler(commands=["current_session"])
        def handle_current_session(message):
            response = self.command_handler.process_command(message.chat.id, message.text)
            self.bot.send_message(message.chat.id, response)

        @self.bot.message_handler(commands=["interrupt"])
        def handle_interrupt(message):
            response = self.command_handler.process_command(message.chat.id, message.text)
            self.bot.send_message(message.chat.id, response)

        @self.bot.message_handler(commands=["select_session"])
        def handle_select_session(message):
            response = self.command_handler.process_command(message.chat.id, message.text)
            self.bot.send_message(message.chat.id, response)

        @self.bot.message_handler(func=lambda m: True)
        def handle_chat_message(message):
            response = self.command_handler.handle_message(message.chat.id, message.text)
            self.bot.send_message(message.chat.id, response)

    def run(self):
        """Run the bot."""
        logger.info("Starting Telegram Bot...")
        print("✅ Starting Telegram Bot...")
        print(f"   Bot Token: {self.bot.token[:15]}...")
        print("   Press Ctrl+C to stop")
        self.bot.infinity_polling()


def main():
    """Main entry point."""
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")

    if not bot_token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set")
        print("Please set your Telegram bot token:")
        print("export TELEGRAM_BOT_TOKEN=your_bot_token_here")
        return

    bot = TelegramBot(bot_token)
    bot.run()


if __name__ == "__main__":
    main()
