# Command Documentation

## Overview
This directory contains documentation for all Telegram commands and input handling available in the Claude Telegram Bridge.

## Available Commands

### /new_session
- Creates a new Claude session with a unique UUID
- Starts a tmux session with that UUID
- Executes Claude with the session ID
- Updates SQLite database with session information

### /sessions
- Lists all currently active Claude sessions
- Shows session status information
- Indicates which sessions are active

### /end_session {uuid}
- Terminates a specific Claude session by UUID
- Closes the tmux session
- Updates SQLite database to mark session as inactive

### /current_session
- Displays currently selected Claude session information
- If no session selected, prompts user to select one

## Input Handling
### Chat Messages
- When user sends text (non-command input):
  - If session selected: Routes input to tmux session using `tmux send-keys`
  - If no session selected: Prompts user to select a session
- Monitors project directory for new Claude responses in JSONL files
- Sends new messages to Telegram when detected

## Command Structure
All commands follow the Telegram bot command format:
```
/{command_name}
```

## Command Implementation
Each command is implemented as a function that:
1. Processes the command input
2. Performs the required operations
3. Returns appropriate response
4. Handles errors gracefully

## Database Integration
Commands interact with the SQLite database to:
- Store session information
- Track active sessions
- Maintain session history
- Track command execution progress