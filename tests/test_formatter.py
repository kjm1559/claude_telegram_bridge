#!/usr/bin/env python3
"""Unit tests for JSONL formatter."""

import unittest
from pathlib import Path
from src.formatter import JSONLFormatter, TelegramResponseFormatter


class TestJSONLFormatterMarkdownEscape(unittest.TestCase):
    """Test MarkdownV2 escape functionality."""

    def setUp(self):
        self.formatter = JSONLFormatter()

    def test_escape_underscore(self):
        """Test escaping underscore character."""
        text = "Hello_world"
        expected = "Hello\_world"
        self.assertEqual(self.formatter._escape_markdown_v2(text), expected)

    def test_escape_asterisk(self):
        """Test escaping asterisk character."""
        text = "Hello*World"
        expected = "Hello\*World"
        self.assertEqual(self.formatter._escape_markdown_v2(text), expected)

    def test_escape_brackets(self):
        """Test escaping brackets."""
        text = "[test]"
        expected = "\[test\]"
        self.assertEqual(self.formatter._escape_markdown_v2(text), expected)

    def test_escape_parentheses(self):
        """Test escaping parentheses."""
        text = "(test)"
        expected = "\(test\)"
        self.assertEqual(self.formatter._escape_markdown_v2(text), expected)

    def test_escape_pipe(self):
        """Test escaping pipe character."""
        text = "a|b"
        expected = "a\|b"
        self.assertEqual(self.formatter._escape_markdown_v2(text), expected)

    def test_escape_multiple_chars(self):
        """Test escaping multiple special characters."""
        text = "Hello *world_ [test] (example)!"
        escaped = self.formatter._escape_markdown_v2(text)
        self.assertIn("\\*", escaped)
        self.assertIn("\\_", escaped)
        self.assertIn("\\[", escaped)
        self.assertIn("\\]", escaped)
        self.assertIn("\\(", escaped)
        self.assertIn("\\)", escaped)
        self.assertIn("\\!", escaped)

    def test_no_escape_needed(self):
        """Test text without special characters."""
        text = "Hello World"
        self.assertEqual(self.formatter._escape_markdown_v2(text), text)


class TestJSONLFormatterTruncation(unittest.TestCase):
    """Test content truncation functionality."""

    def setUp(self):
        self.formatter = JSONLFormatter(max_content_length=50)

    def test_truncate_long_content(self):
        """Test truncation of long content."""
        long_text = "a" * 100
        result = self.formatter._truncate_content(long_text)
        self.assertIn("... (truncated)", result)
        self.assertLess(len(result), 100)

    def test_no_truncate_short_content(self):
        """Test no truncation of short content."""
        short_text = "Hello World"
        result = self.formatter._truncate_content(short_text)
        self.assertEqual(result, short_text)

    def test_truncate_with_escape(self):
        """Test truncation with escaping."""
        long_text = "*" * 100
        result = self.formatter._truncate_content(long_text)
        self.assertIn("\\*", result)

    def test_truncate_without_escape(self):
        """Test truncation without escaping."""
        long_text = "*" * 100
        result = self.formatter._truncate_content(long_text, escape=False)
        self.assertNotIn("\\*", result)


class TestJSONLFormatterMessageTypes(unittest.TestCase):
    """Test message formatting for different types."""

    def setUp(self):
        self.formatter = JSONLFormatter()

    def test_format_user_message(self):
        """Test user message formatting."""
        line = '{"role":"user","content":"Hello"}'
        result = self.formatter.format_message(line)
        self.assertIsNotNone(result)
        self.assertIn("📚 User:", result)
        self.assertIn("Hello", result)

    def test_filter_empty_content(self):
        """Test filtering empty content."""
        line = '{"role":"user","content":""}'
        result = self.formatter.format_message(line)
        self.assertIsNone(result)

    def test_filter_system_messages(self):
        """Test filtering system messages."""
        line = '{"role":"system","content":"test"}'
        result = self.formatter.format_message(line)
        self.assertIsNone(result)

    def test_filter_file_history_snapshot(self):
        """Test filtering file history snapshots."""
        line = '{"type":"file-history-snapshot","content":"test"}'
        result = self.formatter.format_message(line)
        self.assertIsNone(result)

    def test_format_tool_result(self):
        """Test tool result message formatting."""
        line = '{"role":"tool_result","content":"Result text"}'
        result = self.formatter.format_message(line)
        self.assertIsNotNone(result)
        self.assertIn("⚙️ Result:", result)

    def test_format_result_message(self):
        """Test result message formatting."""
        line = '{"role":"result","content":"Complete"}'
        result = self.formatter.format_message(line)
        self.assertIsNotNone(result)
        self.assertIn("✅", result)


class TestJSONLFormatterAssistantMessage(unittest.TestCase):
    """Test assistant message formatting."""

    def setUp(self):
        self.formatter = JSONLFormatter()

    def test_format_assistant_with_tool_call(self):
        """Test assistant message with tool call."""
        line = '''{
            "role":"assistant",
            "tool_calls":[
                {
                    "name":"read_file",
                    "arguments":{"file_path":"test.py"}
                }
            ],
            "content":"Response"
        }'''
        result = self.formatter.format_message(line)
        self.assertIsNotNone(result)
        self.assertIn("🔧 Tool:", result)
        self.assertIn("read_file", result)
        self.assertIn("file_path", result)

    def test_format_assistant_without_tool_call(self):
        """Test assistant message without tool call."""
        line = '{"role":"assistant","content":"Hello from assistant"}'
        result = self.formatter.format_message(line)
        self.assertIsNotNone(result)
        self.assertIn("🤖", result)


class TestJSONLFormatterConversation(unittest.TestCase):
    """Test conversation formatting."""

    def setUp(self):
        self.formatter = JSONLFormatter()

    def test_format_conversation(self):
        """Test full conversation formatting."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        result = self.formatter.format_conversation(messages)
        self.assertIsNotNone(result)
        self.assertIn("📚 User:", result)
        self.assertIn("🤖", result)

    def test_format_empty_conversation(self):
        """Test empty conversation formatting."""
        result = self.formatter.format_conversation([])
        self.assertEqual(result, "No conversation data found.")


class TestTelegramResponseFormatter(unittest.TestCase):
    """Test Telegram-specific formatter features."""

    def setUp(self):
        self.formatter = TelegramResponseFormatter()

    def test_typing_status_default(self):
        """Test typing status is initially False."""
        self.assertFalse(self.formatter.is_typing_active())

    def test_set_typing_active(self):
        """Test setting typing status to active."""
        self.formatter.set_typing(True)
        self.assertTrue(self.formatter.is_typing_active())

    def test_set_typing_inactive(self):
        """Test setting typing status to inactive."""
        self.formatter.set_typing(False)
        self.assertFalse(self.formatter.is_typing_active())


if __name__ == "__main__":
    unittest.main()
