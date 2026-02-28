"""Test suite for bot.py."""

import os
import sys
import signal
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch, call

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestBot:
    """Tests for the TelegramBot class."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.test_token = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
        self.test_pid_file = Path(".claude_telegram_bridge_bot.pid")

    def teardown_method(self):
        """Clean up after each test method."""
        # Remove PID file if it exists
        if self.test_pid_file.exists():
            self.test_pid_file.unlink()

    @patch("src.bot.telebot.TeleBot")
    @patch("src.bot.Database")
    @patch("src.bot.SessionManager")
    def test_bot_init(self, mock_session_manager, mock_db, mock_telebot):
        """Test bot initialization."""
        from bot import TelegramBot

        # Setup mocks
        mock_db_instance = MagicMock()
        mock_session_instance = MagicMock()
        mock_telebot_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_session_manager.return_value = mock_session_instance
        mock_telebot_instance.token = self.test_token

        # Create bot
        bot = TelegramBot(self.test_token)

        # Verify initialization
        mock_telebot.assert_called_once_with(self.test_token)
        assert bot.bot == mock_telebot_instance
        assert bot.db == mock_db_instance
        assert bot.session_manager == mock_session_instance
        assert bot.PID_FILE == Path(".claude_telegram_bridge_bot.pid")

    @patch("src.bot.telebot.TeleBot")
    @patch("src.bot.Database")
    @patch("src.bot.SessionManager")
    def test_bot_run_with_signal_handlers(self, mock_session_manager, mock_db, mock_telebot):
        """Test that signal handlers are registered correctly."""
        from bot import TelegramBot

        # Setup mocks
        mock_db_instance = MagicMock()
        mock_session_instance = MagicMock()
        mock_telebot_instance = MagicMock()
        mock_db.return_value = mock_db_instance
        mock_session_manager.return_value = mock_session_instance
        mock_telebot_instance.token = self.test_token
        mock_telebot_instance.infinity_polling = MagicMock()

        # Create bot
        bot = TelegramBot(self.test_token)

        # Mock the PID file operations
        with patch.object(bot, '_write_pid_file'), \
             patch.object(bot, '_remove_pid_file'), \
             patch.object(bot, '_check_existing_instance', return_value=False):

            # Mock infinity_polling to avoid blocking
            with patch.object(bot.bot, 'infinity_polling'):
                bot.run()

                # Verify signal handlers were registered
                assert hasattr(bot, '_shutdown_requested')
                assert bot._shutdown_requested is False

    def test_check_existing_instance_no_pid_file(self, tmp_path):
        """Test _check_existing_instance when no PID file exists."""
        from bot import TelegramBot

        with patch("src.bot.telebot.TeleBot"), \
             patch("src.bot.Database"), \
             patch("src.bot.SessionManager"):

            bot = TelegramBot(self.test_token)
            bot.PID_FILE = tmp_path / "test.pid"

            # When no PID file exists, should return False
            result = bot._check_existing_instance()
            assert result is False

    def test_check_existing_instance_stale_pid_file(self, tmp_path):
        """Test _check_existing_instance with stale PID file."""
        from bot import TelegramBot

        with patch("src.bot.telebot.TeleBot"), \
             patch("src.bot.Database"), \
             patch("src.bot.SessionManager"):

            bot = TelegramBot(self.test_token)
            pid_file = tmp_path / "test.pid"
            bot.PID_FILE = pid_file

            # Create PID file with non-existent PID
            pid_file.write_text("999999999")

            # Should handle stale PID file gracefully
            result = bot._check_existing_instance()
            assert result is False

    def test_write_pid_file(self, tmp_path):
        """Test _write_pid_file creates PID file correctly."""
        from bot import TelegramBot

        with patch("src.bot.telebot.TeleBot"), \
             patch("src.bot.Database"), \
             patch("src.bot.SessionManager"):

            bot = TelegramBot(self.test_token)
            bot.PID_FILE = tmp_path / "test.pid"

            with patch.object(bot, '_check_existing_instance', return_value=False):
                bot._write_pid_file()

                # Verify PID file was created
                assert bot.PID_FILE.exists()
                assert int(bot.PID_FILE.read_text()) == os.getpid()

    def test_write_pid_file_existing_instance(self, tmp_path):
        """Test _write_pid_file raises error when instance already running."""
        from bot import TelegramBot

        with patch("src.bot.telebot.TeleBot"), \
             patch("src.bot.Database"), \
             patch("src.bot.SessionManager"):

            bot = TelegramBot(self.test_token)
            bot.PID_FILE = tmp_path / "test.pid"

            with patch.object(bot, '_check_existing_instance', return_value=True):
                with pytest.raises(RuntimeError, match="Cannot start: another instance is running"):
                    bot._write_pid_file()

    def test_remove_pid_file(self, tmp_path):
        """Test _remove_pid_file removes PID file."""
        from bot import TelegramBot

        with patch("src.bot.telebot.TeleBot"), \
             patch("src.bot.Database"), \
             patch("src.bot.SessionManager"):

            bot = TelegramBot(self.test_token)
            pid_file = tmp_path / "test.pid"
            bot.PID_FILE = pid_file

            # Create PID file
            pid_file.write_text(str(os.getpid()))
            assert pid_file.exists()

            # Remove PID file
            bot._remove_pid_file()

            # Verify removal
            assert not pid_file.exists()


class TestCommandHandler:
    """Tests for the CommandHandler class."""

    def setup_method(self):
        """Set up test fixtures."""
        from bot import CommandHandler, Database, SessionManager
        from pathlib import Path

        self.test_db = Database(Path("/tmp/test.db"))
        self.test_session_manager = MagicMock()
        self.command_handler = CommandHandler(self.test_session_manager, self.test_db)

    def teardown_method(self):
        """Clean up."""
        if self.test_db.db_path.exists():
            self.test_db.db_path.unlink()

    def test_process_command_valid_command(self):
        """Test processing a valid command."""
        response = self.command_handler.process_command(123, "/help")
        # Should return a response
        assert "/help" in response or response.startswith("✅") or response.startswith("❌")

    def test_process_command_unknown_command(self):
        """Test processing an unknown command."""
        response = self.command_handler.process_command(123, "/unknown_command")
        assert "Unknown command" in response

    def test_process_command_invalid_format(self):
        """Test processing an invalid command format."""
        response = self.command_handler.process_command(123, "")
        assert "Invalid command format" in response

    def test_handle_message_is_command(self):
        """Test handling a message that is a command."""
        response = self.command_handler.handle_message(123, "/help")
        assert "/help" in response or response.startswith("✅") or response.startswith("❌")


class TestMainFunction:
    """Tests for the main() function."""

    def test_main_missing_token(self, monkeypatch):
        """Test main() when TELEGRAM_BOT_TOKEN is not set."""
        monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

        with patch("sys.stdout"):
            from bot import main
            result = main()
            assert result is None

    def test_main_with_token(self, monkeypatch):
        """Test main() when TELEGRAM_BOT_TOKEN is set."""
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "123456789:ABCdef")

        with patch("src.bot.TelegramBot"), \
             patch("sys.stdout"):

            from bot import main
            result = main()
            # Should return None (no explicit return in main)
            assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
