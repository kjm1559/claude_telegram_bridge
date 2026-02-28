# claude_telegram_bridge

A Telegram bot that provides a bridge for running Claude in tmux sessions with automatic session management and persistence.

## Features

- **Session Management**: Create, list, select, and terminate Claude sessions
- **tmux Integration**: All Claude sessions run in persistent tmux sessions
- **SQLite Persistence**: Session state is persisted across bot restarts
- **Command Interface**: Easy-to-use Telegram commands for session management
- **Chat Input**: Send messages directly to active sessions
- **Interrupt Support**: Send interrupt signals to stop running processes

## Basic Functionality

The system runs Claude in tmux sessions with the following features:

1. **Session Management**:
   - Automatically generates UUIDs for session IDs using Python's `uuid` module
   - Uses the generated UUID as both the Claude session ID and tmux session name
   - Stores session information in SQLite database

2. **Command Execution**:
   - Runs Claude with the command: `claude --session-id {uuid}`
   - Session ID is generated at startup and persisted across runs

3. **Data Persistence**:
   - SQLite database at `~/.claude_telegram_bridge/sessions.db`
   - Tracks: session_id, cwd, created_at, last_used, is_active

## Requirements

- Python 3.8+
- tmux
- Claude CLI (optional, for full functionality)
- SQLite3 (included with Python)

## Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd claude_telegram_bridge
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set environment variables**
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
export CLAUDE_BINARY="claude"  # optional, default: claude
```

4. **Run the bot**
```bash
python src/bot.py
```

## Commands

The system supports Telegram commands using the format `/command_name`:

### Session Management
- `/new_session` - Creates a new Claude session with UUID, tmux session, and database update
- `/sessions` - Lists all currently active Claude sessions
- `/end_session {uuid}` - Terminates a specific Claude session by UUID
- `/select_session {uuid}` - Selects a session for sending chat messages
- `/current_session` - Displays currently selected Claude session information

### Interaction
- `/interrupt` - Sends interrupt signal (Escape key) to stop running Claude processes
- `/help` - Displays available commands and usage information

### Chat Input
- Send text messages directly to the selected session (after using `/select_session`)
- If no session is selected, you'll be prompted to select one

## Project Structure

```
.
├── README.md
├── requirements.txt
├── .claude/
│   ├── CLAUDE.md
│   └── agents/
├── commands/
│   ├── new_session.md
│   ├── sessions.md
│   ├── end_session.md
│   ├── current_session.md
│   ├── interrupt.md
│   ├── help.md
│   └── command_handler.md
├── doc/
│   ├── architecture.md
│   ├── usage.md
│   └── api.md
├── src/
│   ├── config.py
│   ├── database.py
│   ├── session_manager.py
│   ├── bot.py
│   ├── main.py
│   └── command_handlers/
│       ├── __init__.py
│       ├── new_session.py
│       ├── sessions.py
│       ├── end_session.py
│       ├── current_session.py
│       ├── interrupt.py
│       ├── help.py
│       └── chat_input.py
└── data/
    └── sessions.db
```

## Command Details

### `/new_session`
Creates a new Claude session with:
- Unique UUID generated using Python's uuid module
- New tmux session with the same name
- Records in SQLite database
- Auto-selects the new session for messaging

### `/sessions`
Lists all active sessions showing:
- Session ID (UUID)
- Working directory
- Creation timestamp
- Last used timestamp
- Active status

### `/end_session {uuid}`
Terminates a specific session:
- Kills the tmux session
- Marks it as inactive in the database
- Requires valid UUID format

### `/current_session`
Shows the currently selected session:
- Session ID
- Working directory
- Created and last used timestamps
- Status information

### `/interrupt`
Stops running processes:
- Sends Escape key to the tmux session
- Requires a session to be selected
- Useful when Claude is stuck

### `/help`
Displays available commands:
- General help with all commands
- Detailed help for specific commands using `/help {command}`

### `/select_session {uuid}`
Selects a session for messages:
- Choose from active sessions
- Required before sending chat input
- Updates last_used timestamp

## Chat Input Handling

When users send chat messages (non-command inputs):
- If a session is selected: Routes input to the tmux session using `tmux send-keys`
- If no session is selected: Prompts user to select a session
- Can monitor project directory for new Claude responses in JSONL files
- Sends new messages to Telegram when detected

## Configuration

Environment variables:
- `TELEGRAM_BOT_TOKEN` - Required: Your Telegram bot API token
- `CLAUDE_BINARY` - Optional: Path to Claude binary (default: "claude")
- `TMUX_SESSION_PREFIX` - Optional: Prefix for tmux session names
- `CLAUDE_SESSION_DIR` - Optional: Directory for session storage (default: ~/.claude_telegram_bridge)

## Troubleshooting

### Common Issues

1. **tmux not found**:
   ```bash
   # Ensure tmux is installed
   sudo apt-get install tmux
   ```

2. **Telegram bot not working**:
   - Check TELEGRAM_BOT_TOKEN is set correctly
   - Verify bot token from @BotFather

3. **Session not found**:
   - Run `/sessions` to see active sessions
   - Create new session with `/new_session`

4. **Permission denied**:
   - Ensure bot has execute permissions
   - Check file permissions

### Debugging

- View database contents:
  ```bash
  sqlite3 ~/.claude_telegram_bridge/sessions.db "SELECT * FROM sessions;"
  ```

- View tmux sessions:
  ```bash
  tmux ls
  ```

## Documentation

Comprehensive documentation is available:
- `/doc/architecture.md` - Technical architecture and system design
- `/doc/usage.md` - Usage guide and operational instructions
- `/doc/api.md` - API documentation and interfaces
- `/commands/*.md` - Individual command documentation

## License

[Your License Here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
