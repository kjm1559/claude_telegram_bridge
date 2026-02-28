#!/usr/bin/env python3
"""JSONL response formatter for Claude Telegram Bridge."""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple


class JSONLFormatter:
    """Formats Claude JSONL responses for Telegram display."""

    # Emoji icons for different message types
    EMOJI_USER = "📚 User:"
    EMOJI_ASSISTANT = "🤖"
    EMOJI_TOOL = "🔧"
    EMOJI_TOOL_RESULT = "⚙️ Result:"
    EMOJI_SYSTEM = "⚙️"
    EMOJI_COMPLETE = "✅"
    EMOJI_ERROR = "❌"

    # Message type filters
    FILTER_SYSTEM_MESSAGES = True
    FILTER_EMPTY_CONTENT = True

    def __init__(self, project_dir: Optional[Path] = None, max_content_length: int = 4000):
        """Initialize formatter.

        Args:
            project_dir: Project directory containing JSONL files.
            max_content_length: Maximum length for content display.
        """
        self.project_dir = project_dir or Path("~/.claude/projects").expanduser()
        self.max_content_length = max_content_length

    @staticmethod
    def _escape_markdown_v2(text: str) -> str:
        """Escape MarkdownV2 special characters.

        Telegram MarkdownV2 requires escaping these characters:
        _, *, [, ], (, ), ~, >, #, +, -, =, |, {, }, ., !

        Args:
            text: Text to escape.

        Returns:
            Escaped text safe for MarkdownV2.
        """
        # Escape characters in order (important for proper escaping)
        escape_chars = ['_', '*', '[', ']', '(', ')', '~', '>', '#', '+', '=', '|', '{', '}', '.', '!']
        for char in escape_chars:
            text = text.replace(char, f'\{char}')
        return text

    def _truncate_content(self, content: str, escape: bool = True) -> str:
        """Truncate content to max length with ellipsis.

        Args:
            content: Content to truncate.
            escape: Whether to escape MarkdownV2 characters.

        Returns:
            Truncated content with ellipsis if needed.
        """
        if len(content) <= self.max_content_length:
            result = content
        else:
            result = content[:self.max_content_length] + "\n... (truncated)"

        if escape:
            return self._escape_markdown_v2(result)
        return result

    def _format_tool_args(self, args: Dict[str, Any]) -> str:
        """Format tool arguments as pretty JSON.

        Args:
            args: Tool arguments dictionary.

        Returns:
            Formatted tool arguments string.
        """
        try:
            return json.dumps(args, indent=2, ensure_ascii=False)
        except (TypeError, ValueError):
            return str(args)

    def _parse_message_type(self, line: str) -> Optional[str]:
        """Parse message type from JSONL line.

        Args:
            line: JSONL line.

        Returns:
            Message type or None.
        """
        try:
            data = json.loads(line.strip())
            return data.get("type") or data.get("role")
        except json.JSONDecodeError:
            return None

    def format_message(self, line: str) -> Optional[str]:
        """Format a single JSONL message for Telegram.

        Args:
            line: JSONL line.

        Returns:
            Formatted message string or None if filtered.
        """
        message_type = self._parse_message_type(line)
        if not message_type:
            return None

        try:
            data = json.loads(line.strip())
        except json.JSONDecodeError:
            return None

        # Filter out file-history-snapshot messages
        if message_type == "file-history-snapshot":
            return None

        role = data.get("role")
        content = data.get("content", "")

        # Filter empty content
        if self.FILTER_EMPTY_CONTENT and not content:
            return None

        # Handle user messages
        if role == "user":
            return f"{self.EMOJI_USER} {self._truncate_content(content)}"

        # Handle assistant messages with tool calls
        if role == "assistant":
            return self._format_assistant_message(data)

        # Handle tool messages
        if role == "tool":
            return self._format_tool_message(data)

        # Handle tool_result messages
        if role == "tool_result":
            return f"{self.EMOJI_TOOL_RESULT} {self._truncate_content(content)}"

        # Handle result messages (final completion)
        if role == "result":
            return f"{self.EMOJI_COMPLETE} {self._truncate_content(content)}"

        # Handle system messages (not displayed by default)
        if role == "system" and self.FILTER_SYSTEM_MESSAGES:
            return None

        return None

    def _format_assistant_message(self, data: Dict[str, Any]) -> str:
        """Format assistant message, including tool calls.

        Args:
            data: Message data dictionary.

        Returns:
            Formatted assistant message.
        """
        tool_calls = data.get("tool_calls", [])
        content = data.get("content", "")

        if tool_calls:
            lines = [f"{self.EMOJI_ASSISTANT}"]
            for tool_call in tool_calls:
                tool_name = tool_call.get("name", "unknown")
                args = tool_call.get("arguments", {})
                lines.append(f"{self.EMOJI_TOOL} Tool: {tool_name}")
                lines.append(f"{self.EMOJI_ASSISTANT} Input:")
                lines.append(self._format_tool_args(args))
                lines.append("")
            if content:
                lines.append(f"{self.EMOJI_ASSISTANT} Response:")
                lines.append(self._truncate_content(content))
            return "\n".join(lines)
        else:
            return f"{self.EMOJI_ASSISTANT} {self._truncate_content(content)}"

    def _format_tool_message(self, data: Dict[str, Any]) -> str:
        """Format tool message.

        Args:
            data: Message data dictionary.

        Returns:
            Formatted tool message.
        """
        content = data.get("content", "")
        tool_call_id = data.get("tool_call_id", "")

        if content:
            return f"{self.EMOJI_TOOL_RESULT} {self._truncate_content(content)}"
        else:
            return f"{self.EMOJI_TOOL_RESULT} (tool call {tool_call_id} completed)"

    def format_conversation(self, conversation_data: List[Dict[str, Any]]) -> str:
        """Format a complete conversation for Telegram display.

        Args:
            conversation_data: List of conversation messages.

        Returns:
            Formatted conversation string.
        """
        formatted_messages = []
        has_content = False

        for message in conversation_data:
            formatted = self.format_message_json(message)
            if formatted:
                formatted_messages.append(formatted)
                has_content = True

        if not has_content:
            return "No conversation data found."

        return "\n\n---\n\n".join(formatted_messages)

    def format_message_json(self, message: Dict[str, Any]) -> Optional[str]:
        """Format a single message from JSON dict.

        Args:
            message: Message dictionary.

        Returns:
            Formatted message or None.
        """
        return self.format_message(json.dumps(message))

    def parse_jsonl_file(self, file_path: str) -> List[Dict[str, Any]]:
        """Parse JSONL file and return list of messages.

        Args:
            file_path: Path to JSONL file.

        Returns:
            List of message dictionaries.
        """
        messages = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('{"type":"file-history-snapshot'):
                        try:
                            data = json.loads(line)
                            messages.append(data)
                        except json.JSONDecodeError:
                            continue
        except FileNotFoundError:
            return []
        return messages

    def find_latest_jsonl(self, session_dir: Path) -> Optional[str]:
        """Find the latest JSONL file in a session directory.

        Args:
            session_dir: Directory containing JSONL files.

        Returns:
            Path to latest JSONL file or None.
        """
        if not session_dir.exists():
            return None

        jsonl_files = sorted(session_dir.glob("*.jsonl"), reverse=True)
        return str(jsonl_files[0]) if jsonl_files else None

    def get_conversation_from_session(self, session_id: str, cwd: str = "/tmp") -> str:
        """Get formatted conversation from a session directory.

        Args:
            session_id: Session UUID.
            cwd: Current working directory.

        Returns:
            Formatted conversation string.
        """
        project_dir = self.project_dir / f"-{cwd.split('/')[-1]}" / session_id
        jsonl_path = self.find_latest_jsonl(project_dir)

        if not jsonl_path:
            return "No conversation data found for session."

        messages = self.parse_jsonl_file(jsonl_path)
        return self.format_conversation(messages)


class TelegramResponseFormatter(JSONLFormatter):
    """Extension of JSONLFormatter with Telegram-specific features."""

    # Typing indicator status
    _typing_active = False

    @classmethod
    def set_typing(cls, active: bool):
        """Set typing indicator status.

        Args:
            active: True to show typing, False to hide.
        """
        cls._typing_active = active

    @classmethod
    def is_typing_active(cls) -> bool:
        """Check if typing indicator is active.

        Returns:
            True if typing is active.
        """
        return cls._typing_active

    def format_complete_response(self, session_id: str, cwd: str = "/tmp") -> Tuple[str, bool]:
        """Format complete response with completion check.

        Args:
            session_id: Session UUID.
            cwd: Current working directory.

        Returns:
            Tuple of (formatted response, has_complete_message).
        """
        conversation = self.format_conversation(self.get_conversation_data(session_id, cwd))
        result_content = "".join([msg.get("content", "") for msg in self.get_conversation_data(session_id, cwd) if msg.get("role") == "result"])
        has_complete = "✅ 작업이 종료되었습니다" in conversation or bool(result_content)
        return conversation, has_complete

    def get_conversation_data(self, session_id: str, cwd: str = "/tmp") -> List[Dict[str, Any]]:
        """Get conversation data as list of dictionaries.

        Args:
            session_id: Session UUID.
            cwd: Current working directory.

        Returns:
            List of message dictionaries.
        """
        project_dir = self.project_dir / f"-{cwd.split('/')[-1]}" / session_id
        return self.parse_jsonl_file(project_dir)


# Global formatter instance
formatter = TelegramResponseFormatter()
