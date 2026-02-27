# claude_telegram_bridge

This project provides a bridge for running Claude in a tmux session with automatic session management and persistence.

## Basic Functionality

The project is designed to run Claude in tmux sessions with the following features:

1. **Session Management**:
   - Automatically generates UUIDs for session IDs using `uuidgen`
   - Uses the generated UUID as both the Claude session ID and tmux session name
   - Stores session information (session_id, cwd) in SQLite database

2. **Command Execution**:
   - Runs Claude with the command: `claude --session-id {uuid}`
   - Session ID is generated at startup and persisted across runs

3. **Data Persistence**:
   - Stores Claude session information in an SQLite database
   - Database records include session_id and current working directory (cwd)
   - Ensures session state is maintained between runs

## Usage

To use this bridge:
1. Ensure tmux is installed on your system
2. Run the bridge script which will:
   - Generate a UUID for the session
   - Start a tmux session with that UUID as the session name
   - Launch Claude with the session ID
   - Store session information in the SQLite database

## Requirements

- tmux
- Python 3.x
- Claude CLI
- sqlite3

## Documentation

Comprehensive documentation is available in the `/doc` directory:
- `architecture.md` - Technical architecture and system design
- `usage.md` - Usage guide and operational instructions
- `api.md` - API documentation and interfaces

## Project Structure

```
.
├── README.md
├── CLAUDE.md
├── doc/
│   ├── architecture.md
│   ├── usage.md
│   └── api.md
├── agents/
│   ├── planer.json
│   ├── executer.json
│   └── cheaker.json
└── ...
```
