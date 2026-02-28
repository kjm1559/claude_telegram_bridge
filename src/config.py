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
CLAUDE_BINARY = os.getenv("CLAUDE_BINARY", "claude")
TMUX_SESSION_PREFIX = os.getenv("TMUX_SESSION_PREFIX", "")
CLAUDE_SESSION_DIR = os.getenv("CLAUDE_SESSION_DIR", str(BASE_DIR))
