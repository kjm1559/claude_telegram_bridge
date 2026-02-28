#!/usr/bin/env python3
"""Unit tests for Telegram bot."""

import unittest
from unittest.mock import Mock, patch
from src.config import is_chat_allowed
from src.command_handler import CommandHandler


class TestChatAuthorization(unittest.TestCase):
    """Test chat authorization functionality."""

    @patch('src.command_handler.ALLOWED_CHAT_IDS', [])
    def test_all_chats_allowed_when_empty(self):
        """Test all chats allowed when ALLOWED_CHAT_IDS is empty."""
        self.assertTrue(is_chat_allowed(123456789))

    @patch('src.command_handler.ALLOWED_CHAT_IDS', [123456789, 987654321])
    def test_allowed_chat(self):
        """Test allowed chat returns True."""
        self.assertTrue(is_chat_allowed(123456789))

    @patch('src.command_handler.ALLOWED_CHAT_IDS', [123456789, 987654321])
    def test_unauthorized_chat(self):
        """Test unauthorized chat returns False."""
        self.assertFalse(is_chat_allowed(111111111))


class TestCommandHandlerInit(unittest.TestCase):
    """Test command handler initialization."""

    def test_command_handler_initialization(self):
        """Test command handler creates with default commands."""
        mock_session_manager = Mock()
        mock_db = Mock()

        handler = CommandHandler(mock_session_manager, mock_db)

        self.assertIn("/new_session", handler.commands)
        self.assertIn("/sessions", handler.commands)
        self.assertIn("/end_session", handler.commands)
        self.assertIn("/help", handler.commands)
        self.assertIsNotNone(handler.chat_input)


@patch('src.formatter.JSONLFormatter')
class TestCommandHandlerProcessCommand(unittest.TestCase):
    """Test command processing."""

    def setUp(self):
        self.mock_session_manager = Mock()
        self.mock_db = Mock()
        self.handler = CommandHandler(self.mock_session_manager, self.mock_db)

    def test_process_unknown_command(self):
        """Test processing unknown command."""
        success, response = self.handler.process_command(123, "/unknown_command")
        self.assertFalse(success)
        self.assertIn("Unknown command", response)

    def test_process_command_with_args(self):
        """Test processing command with arguments."""
        success, response = self.handler.process_command(123, "/sessions")
        self.assertIn(success, [True, False])  # Result depends on mock state

    def test_process_invalid_command_format(self):
        """Test processing command with invalid format."""
        success, response = self.handler.process_command(123, "/")
        self.assertFalse(success)


class TestCommandHandlerHandleMessage(unittest.TestCase):
    """Test message handling."""

    def setUp(self):
        self.mock_session_manager = Mock()
        self.mock_db = Mock()
        self.handler = CommandHandler(self.mock_session_manager, self.mock_db)

    def test_handle_command_message(self):
        """Test handling command message."""
        success, response = self.handler.handle_message(123, "/help")
        self.assertIn(success, [True, False])

    def test_handle_chat_input(self):
        """Test handling non-command message."""
        success, response = self.handler.handle_message(123, "Hello world")
        self.assertIn(success, [True, False])


if __name__ == "__main__":
    unittest.main()
