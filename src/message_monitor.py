#!/usr/bin/env python3
"""JSONL message monitor for Claude Telegram Bridge."""

import json
import logging
import re
import time
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any

from .config import MONITOR_INTERVAL, CLAUDE_PROJECTS_DIR

logger = logging.getLogger(__name__)

# Request type constants
REQUEST_NONE = "none"
REQUEST_YESNO = "yesno"
REQUEST_CHOICE = "choice"
REQUEST_TEXT = "text"


class ClaudeRequest:
    """Represents a Claude request awaiting user response."""
    def __init__(self, request_type: str, content: str, options: List[str] = None):
        self.request_type = request_type
        self.content = content
        self.options = options or []
        self.created_at = time.time()


class JSONLMessageMonitor:
    """Monitors JSONL session files for new messages.

    This class provides background polling of Claude JSONL session files
    to detect new messages and forward them to Telegram.
    """

    def __init__(self, bot, formatter, db, session_manager=None):
        """Initialize message monitor.

        Args:
            bot: Telegram bot instance for sending messages.
            formatter: Formatter instance for formatting messages.
            db: Database instance for session information.
            session_manager: Optional SessionManager for sending responses.
        """
        self.bot = bot
        self.formatter = formatter
        self.db = db
        self.session_manager = session_manager
        self.active_sessions: Dict[str, dict] = {}  # session_id -> {chat_id, file_path, last_line_count, cwd}
        self.pending_requests: Dict[str, ClaudeRequest] = {}  # session_id -> ClaudeRequest
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def start(self):
        """Start monitoring thread."""
        if self.running:
            logger.info("Message monitor already running")
            return

        logger.info("Starting message monitor...")
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop monitoring thread."""
        if not self.running:
            return

        logger.info("Stopping message monitor...")
        self.running = False
        if self.thread:
            self.thread.join(timeout=5.0)
            self.thread = None
        logger.info("Message monitor stopped")

    def register_session(self, session_id: str, chat_id: int, cwd: str):
        """Register a session for monitoring.

        Args:
            session_id: UUID of the session.
            chat_id: Telegram chat ID to send messages to.
            cwd: Working directory of the session.
        """
        with self._lock:
            file_path = self._get_session_file_path(session_id, cwd)
            last_line_count = self._count_lines(file_path)

            self.active_sessions[session_id] = {
                'chat_id': chat_id,
                'file_path': file_path,
                'last_line_count': last_line_count,
                'cwd': cwd
            }
            logger.info(f"Registered session {session_id} for monitoring (file: {file_path})")

    def unregister_session(self, session_id: str):
        """Unregister a session from monitoring.

        Args:
            session_id: UUID of the session.
        """
        with self._lock:
            if session_id in self.active_sessions:
                del self.active_sessions[session_id]
                logger.info(f"Unregistered session {session_id} from monitoring")

            # Also clear any pending requests
            if session_id in self.pending_requests:
                del self.pending_requests[session_id]

    def _detect_claude_request(self, content: str) -> ClaudeRequest:
        """Detect if content contains a Claude request.

        Args:
            content: Message content to analyze.

        Returns:
            ClaudeRequest if a request is detected, None otherwise.
        """
        if not content:
            return None

        content_lower = content.lower()

        # Check for yes/no requests
        if re.search(r'\((y/n)|\(yes/no\)|\[y/n\]', content_lower):
            # Extract the question text
            match = re.search(r'([^.\n]+\?)\s*\([yn]\)', content, re.IGNORECASE)
            question = match.group(1).strip() if match else content
            return ClaudeRequest(REQUEST_YESNO, question, ['yes', 'no'])

        # Check for numbered choices (1. 2. 3.)
        choices = re.findall(r'^(\d+)\.\s*(.+?)(?=\n\d+\.|$)', content, re.MULTILINE | re.DOTALL)
        if choices:
            choices = [text.strip() for _, text in choices]
            if len(choices) >= 2:
                return ClaudeRequest(REQUEST_CHOICE, content, choices)

        # Check for text input prompts (ending with colon or >)
        if re.search(r':\s*$|>\s*$', content):
            return ClaudeRequest(REQUEST_TEXT, content, [])

        return None

    def _get_session_file_path(self, session_id: str, cwd: str) -> Path:
        """Compute the path to a session's JSONL file.

        Args:
            session_id: UUID of the session.
            cwd: Working directory of the session.

        Returns:
            Path to the JSONL file.
        """
        # Extract project name from cwd
        # e.g., /home/mj/claude_telegram_bridge -> -home-mj-claude-telegram-bridge
        project_path = Path(cwd)

        # Build folder name: -<path-with-hyphens>
        path_parts = [p.replace(" ", "-") for p in project_path.parts]
        folder_name = "-" + "-".join(path_parts)

        return CLAUDE_PROJECTS_DIR / folder_name / f"{session_id}.jsonl"

    def _count_lines(self, file_path: Path) -> int:
        """Count the number of lines in a file.

        Args:
            file_path: Path to the file.

        Returns:
            Number of lines in the file, or 0 if file doesn't exist.
        """
        try:
            if not file_path.exists():
                return 0
            with open(file_path, 'r', encoding='utf-8') as f:
                return sum(1 for _ in f)
        except (IOError, OSError) as e:
            logger.warning(f"Error counting lines in {file_path}: {e}")
            return 0

    def _read_new_lines(self, file_path: Path, start_line: int) -> List[str]:
        """Read new lines from a file starting after start_line.

        Args:
            file_path: Path to the file.
            start_line: Line number to start reading from (0-indexed).

        Returns:
            List of new lines.
        """
        try:
            if not file_path.exists():
                return []
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                return lines[start_line:] if len(lines) > start_line else []
        except (IOError, OSError) as e:
            logger.warning(f"Error reading lines from {file_path}: {e}")
            return []

    def _monitor_loop(self):
        """Main monitoring loop - polls all active sessions."""
        logger.info("Message monitor loop started")
        while self.running:
            try:
                self._check_all_sessions()
            except Exception as e:
                logger.error(f"Monitor loop error: {e}")
            time.sleep(MONITOR_INTERVAL)
        logger.info("Message monitor loop stopped")

    def _check_all_sessions(self):
        """Check all active sessions for new messages."""
        with self._lock:
            sessions_copy = dict(self.active_sessions)

        for session_id, info in sessions_copy.items():
            self._check_for_new_messages(session_id, info)

    def _check_for_new_messages(self, session_id: str, info: dict):
        """Check a single session for new messages.

        Args:
            session_id: UUID of the session.
            info: Session info dictionary.
        """
        file_path = info['file_path']
        current_line_count = self._count_lines(file_path)

        if current_line_count > info['last_line_count']:
            # Read new lines and send formatted messages
            new_lines = self._read_new_lines(file_path, info['last_line_count'])

            for line in new_lines:
                line = line.strip()
                if not line:
                    continue

                # Skip file-history-snapshot messages
                if line.startswith('{"type":"file-history-snapshot'):
                    continue

                try:
                    # Parse and validate JSON
                    data = json.loads(line)

                    # Filter out file-history-snapshot
                    if data.get("type") == "file-history-snapshot":
                        continue

                    # Get message content
                    content = data.get("content", "")
                    role = data.get("role", "")

                    # Only process assistant messages
                    if role != "assistant" or not content:
                        continue

                    # Check for Claude requests
                    request = self._detect_claude_request(content)
                    if request:
                        # Clear any previous pending request
                        with self._lock:
                            self.pending_requests[session_id] = request

                        # Format and send request with keyboard
                        formatted = self._format_request_message(session_id, request)
                        keyboard = self._create_request_keyboard(session_id, request)
                        self._send_message(info['chat_id'], formatted, keyboard)
                    else:
                        # Regular message
                        formatted = self.formatter.format_message(line)
                        if formatted:
                            # Clear pending request for regular messages
                            with self._lock:
                                if session_id in self.pending_requests:
                                    del self.pending_requests[session_id]
                            self._send_message(info['chat_id'], formatted)

                except json.JSONDecodeError:
                    # Skip invalid JSON lines
                    continue
                except Exception as e:
                    logger.warning(f"Error processing line: {e}")
                    continue

            # Update last line count
            with self._lock:
                if session_id in self.active_sessions:
                    self.active_sessions[session_id]['last_line_count'] = current_line_count

    def _send_message(self, chat_id: int, text: str, reply_markup=None):
        """Send a message to a Telegram chat.

        Args:
            chat_id: Telegram chat ID.
            text: Message text to send.
            reply_markup: Optional inline keyboard.
        """
        try:
            self.bot.send_message(chat_id, text, parse_mode="MarkdownV2", reply_markup=reply_markup)
        except Exception as e:
            logger.error(f"Error sending message to chat {chat_id}: {e}")

    def _create_request_keyboard(self, session_id: str, request: ClaudeRequest):
        """Create inline keyboard for Claude request.

        Args:
            session_id: UUID of the session.
            request: ClaudeRequest object.

        Returns:
            InlineKeyboardMarkup or None.
        """
        try:
            from telebot import types
            keyboard = types.InlineKeyboardButton
            markup = types.InlineKeyboardMarkup()

            if request.request_type == REQUEST_YESNO:
                # Yes/No buttons
                markup.add(keyboard("✅ Yes", callback_data=f"req_{session_id}_yes"))
                markup.add(keyboard("❌ No", callback_data=f"req_{session_id}_no"))

            elif request.request_type == REQUEST_CHOICE and len(request.options) <= 5:
                # Choice buttons for up to 5 options
                for i, option in enumerate(request.options[:5]):
                    # Truncate long option text
                    short_option = option[:20] + "..." if len(option) > 20 else option
                    markup.add(keyboard(f"{i+1}. {short_option}", callback_data=f"req_{session_id}_{i+1}"))

            # Return None for text input or too many choices
            return markup

        except Exception as e:
            logger.warning(f"Error creating keyboard: {e}")
            return None

    def _format_request_message(self, session_id: str, request: ClaudeRequest) -> str:
        """Format a request message for Telegram.

        Args:
            session_id: UUID of the session.
            request: ClaudeRequest object.

        Returns:
            Formatted message text.
        """
        if request.request_type == REQUEST_YESNO:
            return f"🤖 Claude is asking:\n\n{request.content}\n\n_Please use the buttons below to respond._"

        elif request.request_type == REQUEST_CHOICE:
            choices_text = "\n".join([f"{i+1}. {opt}" for i, opt in enumerate(request.options[:10])])
            if len(request.options) > 5:
                # For more than 5 choices, add instruction to type number
                return f"🤖 Claude is asking:\n\n{request.content}\n\n{choices_text}\n\n_Type the number of your choice and send as a message._"
            else:
                return f"🤖 Claude is asking:\n\n{request.content}\n\n{choices_text}\n\n_Please use the buttons below or type the number._"

        elif request.request_type == REQUEST_TEXT:
            return f"🤖 Claude is asking:\n\n{request.content}\n\n_Type your response and send as a message._"

        return request.content

    def handle_callback_query(self, callback_query):
        """Handle inline keyboard button callbacks.

        Args:
            callback_query: Telegram callback query object.
        """
        data = callback_query.data
        chat_id = callback_query.message.chat.id

        # Parse callback data: req_{session_id}_{response}
        parts = data.split("_")
        if len(parts) < 3:
            return

        session_id = "_".join(parts[1:-1])
        response = parts[-1]

        # Map response values
        if response == "yes":
            response = "y"
        elif response == "no":
            response = "n"

        # Send response to tmux session
        self._send_response_to_session(session_id, chat_id, response)

        # Clear pending request
        with self._lock:
            if session_id in self.pending_requests:
                del self.pending_requests[session_id]

        # Acknowledge callback
        try:
            self.bot.answer_callback_query(callback_query.id)
        except Exception as e:
            logger.warning(f"Error answering callback: {e}")

    def handle_user_message(self, chat_id: int, text: str):
        """Handle text message as response to Claude request.

        Args:
            chat_id: Telegram chat ID.
            text: User's text response.
        """
        # Find session for this chat
        session_id = self.db.get_user_session(chat_id)
        if not session_id:
            return False

        # Check if there's a pending request
        with self._lock:
            request = self.pending_requests.get(session_id)

        if not request:
            return False

        # Validate response based on request type
        if request.request_type == REQUEST_CHOICE:
            # Check if response is a valid choice number
            if text.strip() and text.strip().isdigit():
                choice_num = int(text.strip())
                if 1 <= choice_num <= len(request.options):
                    self._send_response_to_session(session_id, chat_id, text)
                    with self._lock:
                        del self.pending_requests[session_id]
                    return True

        elif request.request_type == REQUEST_TEXT:
            # Accept any text for text input
            self._send_response_to_session(session_id, chat_id, text)
            with self._lock:
                del self.pending_requests[session_id]
            return True

        return False

    def _send_response_to_session(self, session_id: str, chat_id: int, response: str):
        """Send user response to tmux session.

        Args:
            session_id: UUID of the session.
            chat_id: Telegram chat ID.
            response: User's response text.
        """
        if self.session_manager:
            try:
                # Send response with Enter key
                success, message = self.session_manager.send_keys(session_id, response)
                if success:
                    logger.info(f"Sent response '{response}' to session {session_id}")
            except Exception as e:
                logger.error(f"Error sending response to session: {e}")