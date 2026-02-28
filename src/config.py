# Claude Telegram Bridge Configuration

import os
from pathlib import Path

# Base directory
BASE_DIR = Path.home() / ".claude_telegram_bridge"

# Database configuration
DATABASE_PATH = BASE_DIR / "sessions.db"

# Project directory template
# cwd: /home/user/path
# Project folder: /home/user/path/-home-user-path
PROJECT_DIR_TEMPLATE = "{cwd}/-{cwd_name}"
PROJECT_DIR_NAME = "{cwd_name}"

# Environment variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_ALLOWED_CHAT_IDS = os.getenv("TELEGRAM_ALLOWED_CHAT_IDS", "")
CLAUDE_BINARY = os.getenv("CLAUDE_BINARY", "claude")
TMUX_SESSION_PREFIX = os.getenv("TMUX_SESSION_PREFIX", "")
CLAUDE_SESSION_DIR = os.getenv("CLAUDE_SESSION_DIR", str(BASE_DIR))

# Authorized chat IDs (comma-separated)
# Format: 123456789,987654321,555666777
# If empty, all users can use the bot
ALLOWED_CHAT_IDS = [int(cid.strip()) for cid in TELEGRAM_ALLOWED_CHAT_IDS.split(",") if cid.strip()] if TELEGRAM_ALLOWED_CHAT_IDS else []


def is_chat_allowed(chat_id: int) -> bool:
    """Check if a chat ID is allowed to use the bot.

    Args:
        chat_id: Telegram chat ID to check.

    Returns:
        True if chat is allowed, False otherwise.
        If no chat IDs are configured, all chats are allowed.
    """
    return chat_id in ALLOWED_CHAT_IDS if ALLOWED_CHAT_IDS else True
