# Claude Telegram Bridge - Usage Guide

## Overview

This guide explains how to use the Claude Telegram Bridge for running Claude in tmux sessions with automatic session management and real-time message monitoring.

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
~/.claude/projects/claude_telegram_bridge/data/sessions.db
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

### Real-time Message Monitoring

The bridge can monitor Claude session JSONL files for new messages and automatically send them to Telegram.

#### JSONL File Path Structure

Claude stores session messages in JSONL files at:
```
~/.claude/projects/<project_folder>/<session_id>.jsonl
```

For example:
- **Project path**: `/home/mj/claude_telegram_bridge`
- **Folder name**: `-home-mj-claude-telegram-bridge`
- **Session file**: `~/.claude/projects/-home-mj-claude-telegram-bridge/6f1e0b88-af22-4134-ad8c-872c659dacf7.jsonl`

The folder name is constructed by:
1. Taking the full path components
2. Replacing spaces with hyphens
3. Joining with hyphens and prepending a hyphen

#### Monitoring Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `MONITOR_ENABLED` | `true` | Enable/disable message monitoring. Set to `false` to disable. |
| `MONITOR_INTERVAL` | `2.0` | Polling interval in seconds. Lower values = faster updates but more resource usage. |

#### How Monitoring Works

1. When a session is created or selected, the monitor starts polling the corresponding JSONL file
2. The monitor tracks the line count of the file
3. When new lines are detected, they are parsed and formatted for Telegram
4. Formatted messages are sent to the Telegram chat associated with the session
5. When a session is ended, monitoring stops automatically

#### Behavior

- **Automatic Registration**: Sessions are automatically registered for monitoring when created via `/new_session`
- **Message Filtering**: System messages and empty content are filtered out by default
- **MarkdownV2 Formatting**: Messages are formatted using Telegram's MarkdownV2 parse mode
- **Graceful Handling**: Missing files or JSON parse errors are handled gracefully without stopping the monitor
- `MONITOR_ENABLED` - Enable/disable real-time message monitoring (default: "true")
- `MONITOR_INTERVAL` - Polling interval for message monitoring in seconds (default: "2.0")

## Real-time Message Monitoring

### Overview

The bridge can monitor Claude session JSONL files and automatically send new messages to Telegram. This feature enables real-time interaction with Claude sessions without manual polling.

### Session File Path Structure

Claude stores session messages in JSONL files at:
```
~/.claude/projects/<project_folder>/<session_id>.jsonl
```

The project folder is derived from the working directory path:
- Example: `/home/mj/claude_telegram_bridge` → `-home-mj-claude-telegram-bridge`
- Full path: `~/.claude/projects/-home-mj-claude-telegram-bridge/6f1e0b88-af22-4134-ad8c-872c659dacf7.jsonl`

### Monitoring Behavior

1. When a session is created or selected, the monitor starts tracking its JSONL file
2. The monitor polls the file at configurable intervals (default: 2 seconds)
3. New messages are automatically formatted and sent to Telegram
4. When a session is ended, monitoring stops automatically

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `MONITOR_ENABLED` | `true` | Enable/disable monitoring feature |
| `MONITOR_INTERVAL` | `2.0` | Polling interval in seconds |

### Usage Examples

```bash
# Start bot with monitoring enabled (default)
python main.py

# Disable monitoring
MONITOR_ENABLED=false python main.py

# Set custom polling interval
MONITOR_INTERVAL=5.0 python main.py
```

## Troubleshooting

### Common Issues
1. **tmux not found**: Ensure tmux is installed and in PATH
2. **Claude not found**: Ensure Claude CLI is installed and accessible
3. **Permission denied**: Ensure the bridge script has execute permissions

### Debugging
- Check database contents: `sqlite3 ~/.claude/projects/claude_telegram_bridge/data/sessions.db "SELECT * FROM sessions;"`
- View tmux sessions: `tmux ls`
- Check monitoring: `ls -la ~/.claude/projects/` to see active session folders
- View session JSONL: `tail -f ~/.claude/projects/-home-mj-claude-telegram-bridge/<session_id>.jsonl`