#!/usr/bin/env python3
"""Telegram bot for Claude Bridge."""

import os
import logging as py_logging
import signal
import time
from pathlib import Path

# Completely disable telebot logging BEFORE importing telebot
# This prevents 409 error messages from appearing
py_logging.getLogger('telebot').setLevel(py_logging.CRITICAL)
py_logging.getLogger('TeleBot').setLevel(py_logging.CRITICAL)
py_logging.getLogger('telebot').handlers = []
py_logging.getLogger('TeleBot').handlers = []

try:
    import telebot
    from telebot import types
except ImportError:
    print("❌ Error: python-telegram-bot not installed")
    print("Install with: pip install python-telegram-bot")
    raise

# Use logging module alias for the rest of the code
logging = py_logging

# Import configuration
from .config import BASE_DIR, MONITOR_ENABLED, is_chat_allowed

# Import local modules
from .database import Database
from .session_manager import SessionManager
from .command_handlers import (
    NewSessionCommand,
    SessionsCommand,
    EndSessionCommand,
    CurrentSessionCommand,
    InterruptCommand,
    HelpCommand,
    ChatInputHandler,
    SelectSessionCommand,
)
from .formatter import formatter
from .message_monitor import JSONLMessageMonitor

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

    def _check_authorization(self, chat_id: int) -> bool:
        """Check if chat is authorized to use the bot.

        Args:
            chat_id: Telegram chat ID.

        Returns:
            True if authorized, False otherwise.
        """
        if is_chat_allowed(chat_id):
            return True
        logger.warning(f"Unauthorized chat attempt from chat_id: {chat_id}")
        return False

    def _get_unauthorized_response(self) -> str:
        """Get unauthorized access response message.

        Returns:
            Response message text.
        """
        return ("❌ Access denied. This bot is restricted to authorized users only.\n"
                "Please contact the administrator.")

    def process_command(self, chat_id: int, message: str) -> str:
        """Process a Telegram command.

        Args:
            chat_id: Telegram chat ID.
            message: Full message text including command.

        Returns:
            Response message text.
        """
        logger.debug(f"[BOT] process_command called for chat_id={chat_id}, message={message[:50]}")
        parts = message.strip().split(None, 1)
        if not parts:
            logger.warning(f"[BOT] Empty command from chat_id={chat_id}")
            return "❌ Invalid command format.\n\nType `/help` for available commands."

        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        logger.info(f"[BOT] COMMAND: {command} (chat_id={chat_id}, args='{args}')")

        if command in self.commands:
            logger.debug(f"[BOT] Found command handler for {command}")
            if command == "/help":
                target_cmd = args.strip() if args else None
                logger.info(f"[BOT] Processing /help command, target_cmd={target_cmd}")
                success, response = self.commands["/help"].handle(chat_id, target_cmd)
            elif command in ["/end_session", "/select_session"]:
                logger.info(f"[BOT] Processing {command} with full message")
                success, response = self.commands[command].handle(chat_id, message.strip())
            else:
                logger.info(f"[BOT] Processing {command} (no args)")
                success, response = self.commands[command].handle(chat_id)

            logger.debug(f"[BOT] Command {command} result: success={success}")
            if success:
                # Help command returns formatted text, don't add prefix
                if command == "/help":
                    return response
                return f"✅ {response}"
            else:
                return f"❌ {response}"
        else:
            logger.warning(f"[BOT] Unknown command: {command}")
            return f"❌ Unknown command: {command}.\n\nType `/help` for available commands."

    def process_chat_input(self, chat_id: int, text: str) -> str:
        """Process non-command chat input.

        Args:
            chat_id: Telegram chat ID.
            text: Message text.

        Returns:
            Response message text.
        """
        logger.info(f"[BOT] CHAT_INPUT: chat_id={chat_id}, text={text[:100]}")
        success, response = self.chat_input.handle(chat_id, text)
        logger.debug(f"[BOT] Chat input result: success={success}")
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

    PID_FILE = Path(BASE_DIR) / ".claude_telegram_bridge_bot.pid"

    def __init__(self, bot_token: str):
        """Initialize Telegram Bot.

        Args:
            bot_token: Telegram bot API token.
        """
        self.bot = telebot.TeleBot(bot_token)
        self.db = Database(Path(BASE_DIR) / "sessions.db")

        # Initialize message monitor
        self.message_monitor = None
        if MONITOR_ENABLED:
            self.message_monitor = JSONLMessageMonitor(self.bot, formatter, self.db)

        # Initialize session manager with message monitor
        self.session_manager = SessionManager(self.db, message_monitor=self.message_monitor)

        # Update message_monitor with session_manager for bidirectional communication
        if self.message_monitor:
            self.message_monitor.session_manager = self.session_manager

        # Register response handlers for Claude requests
        if self.message_monitor:
            self.bot.callback_query_handler(func=lambda call: True)(self.message_monitor.handle_callback_query)

        self.command_handler = CommandHandler(self.session_manager, self.db)

        # Register message handlers
        self._register_handlers()

    def _register_handlers(self):
        """Register Telegram bot message handlers."""

        @self.bot.message_handler(commands=["start"])
        def handle_start(message):
            if not self.command_handler._check_authorization(message.chat.id):
                return
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
                "Type `/help` to see all available commands.",
                parse_mode="MarkdownV2"
            )

        # Individual command handlers removed - all commands now handled by handle_chat_message

        @self.bot.message_handler(
            commands=["start", "help", "new_session", "sessions", "end_session",
                      "current_session", "interrupt", "select_session"],
            func=lambda m: m.text is not None
        )
        def handle_chat_message(message):
            # Log that handler was called
            logger.info(f"[BOT] handle_chat_message CALLED: chat_id={message.chat.id}")

            if not self.command_handler._check_authorization(message.chat.id):
                self.bot.send_message(message.chat.id, self.command_handler._get_unauthorized_response(), parse_mode="MarkdownV2")
                return

            text = message.text.strip()
            logger.info(f"[BOT] handle_chat_message: chat_id={message.chat.id}, text='{text[:50]}'")

            # Start typing indicator
            self.bot.send_chat_action(message.chat.id, "typing")

            # Handle commands starting with /
            if text.startswith('/'):
                logger.info(f"[BOT] Command detected in handle_chat_message: '{text[:50]}'")
                response = self.command_handler.handle_message(message.chat.id, text)
                self.bot.send_message(message.chat.id, response, parse_mode="MarkdownV2")
                self.bot.stop_chat_action(message.chat.id)
                return

            # First, check if this is a response to a Claude request
            if self.message_monitor:
                if self.message_monitor.handle_user_message(message.chat.id, text):
                    # Response handled by message_monitor
                    self.bot.stop_chat_action(message.chat.id)
                    return

            # Otherwise, process as a regular message
            response = self.command_handler.handle_message(message.chat.id, text)
            self.bot.send_message(message.chat.id, response, parse_mode="MarkdownV2")

            # Stop typing indicator
            self.bot.stop_chat_action(message.chat.id)

    def _check_existing_instance(self) -> bool:
        """Check if another bot instance is already running.

        Returns:
            True if another instance is running, False otherwise.
        """
        if self.PID_FILE.exists():
            try:
                with open(self.PID_FILE, "r") as f:
                    old_pid = int(f.read().strip())
                # Check if process is still running
                try:
                    os.kill(old_pid, 0)
                    logger.error(f"Another bot instance is already running (PID: {old_pid})")
                    print(f"❌ Another bot instance is already running (PID: {old_pid})")
                    return True
                except ProcessLookupError:
                    # Process is not running, can remove stale PID file
                    logger.info(f"Found stale PID file for non-running process ({old_pid})")
            except (ValueError, IOError) as e:
                logger.warning(f"Error reading PID file: {e}")
        return False

    def _write_pid_file(self):
        """Write PID file for process locking.

        Raises:
            RuntimeError: If another instance appears to be running.
        """
        if self._check_existing_instance():
            raise RuntimeError("Cannot start: another instance is running")

        with open(self.PID_FILE, "w") as f:
            f.write(str(os.getpid()))
        logger.info(f"PID file created: {self.PID_FILE} (PID: {os.getpid()})")

    def _remove_pid_file(self):
        """Remove PID file on shutdown."""
        if self.PID_FILE.exists():
            try:
                self.PID_FILE.unlink()
                logger.info(f"PID file removed: {self.PID_FILE}")
            except IOError as e:
                logger.warning(f"Error removing PID file: {e}")

    def run(self):
        """Run the bot with conflict detection and graceful handling."""
        logger.info("Starting Telegram Bot...")
        print("\u2705 Starting Telegram Bot...")
        print(f"   Bot Token: {self.bot.token[:15]}...")
        if MONITOR_ENABLED:
            print("   Message monitoring: ENABLED")
        print("   Press Ctrl+C to stop")

        # Write PID file for process locking
        try:
            self._write_pid_file()
        except RuntimeError as e:
            logger.error(f"{e}")
            return

        # Start message monitor if enabled
        if self.message_monitor:
            self.message_monitor.start()

        # Handle graceful shutdown
        self._shutdown_requested = False

        def shutdown_handler(signum, frame):
            logger.info("Shutdown signal received. Stopping bot...")
            self._shutdown_requested = True
            self.bot.stop_polling()
            # Stop message monitor
            if self.message_monitor:
                self.message_monitor.stop()

        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        # Suppress ALL telebot logging to hide 409 errors
        import logging as py_logging
        # telebot uses both 'telebot' and 'TeleBot' loggers
        telebot_logger1 = py_logging.getLogger('telebot')
        telebot_logger2 = py_logging.getLogger('TeleBot')
        original_level1 = telebot_logger1.level
        original_level2 = telebot_logger2.level
        telebot_logger1.setLevel(logging.CRITICAL)
        telebot_logger2.setLevel(logging.CRITICAL)
        telebot_logger1.handlers = []
        telebot_logger2.handlers = []
        # Also suppress root logger warnings during init
        root_logger = py_logging.getLogger()
        root_logger.setLevel(logging.WARNING)

        # Reset last_update_id to force Telegram to give us the next update
        # This prevents 409 conflicts from stale update offsets
        self.bot.last_update_id = 0

        try:
            # Wait a moment to let Telegram clear any previous session state
            logger.info("Waiting for Telegram to clear previous session state...")
            time.sleep(2)

            # Start polling with proper conflict handling
            # allowed_updates=['message'] enables all message handlers including commands
            self.bot.infinity_polling(timeout=60, allowed_updates=['message'])
        except telebot.apihelper.ApiTelegramException as e:
            error_code = None
            if e.result:
                error_code = e.result.get("error_code")

            # Handle conflict errors (Error 409) - retry once, then exit gracefully
            if error_code == 409:
                logger.warning("Bot conflict (409): Telegram session conflict detected")
                print("\n⚠️  Bot conflict detected (Error 409). Retrying once...")
                time.sleep(3)  # Wait longer before retry
                try:
                    self.bot.infinity_polling(timeout=60, allowed_updates=['message'])
                except telebot.apihelper.ApiTelegramException as e2:
                    if e2.result and e2.result.get("error_code") == 409:
                        print("\n❌ Persistent bot conflict (Error 409). This means:")
                        print("   - Another bot instance might still be running")
                        print("   - Telegram terminated this bot's polling")
                        print("\nExiting gracefully. Please ensure only one bot instance is running.")
                        return
                    else:
                        raise
            else:
                logger.error(f"Telegram API error (code: {error_code}): {e}")
                raise
        except Exception as e:
            logger.error(f"Bot polling error: {e}")
            raise
        finally:
            # Restore telebot logger levels
            telebot_logger1.setLevel(original_level1)
            telebot_logger2.setLevel(original_level2)
            # Stop message monitor
            if self.message_monitor:
                self.message_monitor.stop()
            # Clean up PID file
            self._remove_pid_file()


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
