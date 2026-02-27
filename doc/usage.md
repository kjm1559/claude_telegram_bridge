# Claude Telegram Bridge - Usage Guide

## Overview

This guide explains how to use the Claude Telegram Bridge for running Claude in tmux sessions with automatic session management.

## Getting Started

1. **Prerequisites**
   - Ensure tmux is installed on your system
   - Ensure Python 3.x is installed
   - Ensure Claude CLI is installed and accessible

2. **Installation**
   - Clone the repository
   - Install required Python dependencies (if any)
   - Make sure the bridge script is executable

## Running the Bridge

### Basic Usage
```
python bridge.py
```

The bridge will:
1. Generate a UUID for the session
2. Create a tmux session with that UUID as the session name
3. Launch Claude with the session ID
4. Store session information in the SQLite database

### Session Management
- Sessions are automatically named with UUIDs
- Session information is persisted in SQLite
- You can manage sessions using standard tmux commands:
  - `tmux ls` - List all sessions
  - `tmux attach -t {session_id}` - Attach to a specific session
  - `tmux kill-session -t {session_id}` - Kill a specific session

## Database Information

The system maintains a SQLite database at:
```
~/.claude_telegram_bridge/sessions.db
```

The database contains session information including:
- session_id: UUID of the session
- cwd: Current working directory
- created_at: Timestamp when session was created
- last_used: Timestamp when session was last used

## Configuration

The bridge supports configuration through environment variables or configuration files:
- `CLAUDE_SESSION_DIR` - Directory for session storage
- `TMUX_SESSION_PREFIX` - Prefix for tmux session names
- `CLAUDE_BINARY` - Path to Claude binary

## Troubleshooting

### Common Issues
1. **tmux not found**: Ensure tmux is installed and in PATH
2. **Claude not found**: Ensure Claude CLI is installed and accessible
3. **Permission denied**: Ensure the bridge script has execute permissions

### Debugging
- Check database contents: `sqlite3 ~/.claude_telegram_bridge/sessions.db "SELECT * FROM sessions;"`
- View tmux sessions: `tmux ls`