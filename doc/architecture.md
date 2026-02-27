# Claude Telegram Bridge - Technical Documentation

## Overview

This document provides technical details about the Claude Telegram Bridge project, which facilitates running Claude in tmux sessions with automatic session management and persistence.

## Architecture

The system consists of:
1. **Session Management Layer** - Handles UUID generation and tmux session creation
2. **Claude Integration Layer** - Executes Claude with proper session IDs
3. **Persistence Layer** - Stores session information in SQLite database

## Session Management

### UUID Generation
- Session IDs are generated using `uuidgen` command
- The UUID is used as both:
  - Claude session ID (`claude --session-id {uuid}`)
  - tmux session name
- This ensures consistency across the system

### Database Storage
Session information is stored in SQLite database with the following schema:
- `session_id` (UUID): Unique identifier for the session
- `cwd` (string): Current working directory when session was created
- `created_at` (timestamp): When the session was created
- `last_used` (timestamp): When the session was last used

## Command Execution

The system executes Claude with the following command pattern:
```
claude --session-id {uuid}
```

Where `{uuid}` is the generated session ID.

## tmux Integration

The bridge creates and manages tmux sessions with the following characteristics:
- Session name matches the generated UUID
- Session persists across terminal sessions
- Session can be easily identified and managed using tmux commands

## Requirements

### System Requirements
- tmux
- Python 3.x
- Claude CLI
- sqlite3

### Dependencies
- uuidgen (typically part of util-linux package)
- sqlite3 Python module