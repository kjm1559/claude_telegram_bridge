# Claude Telegram Bridge - API Documentation

## Overview

This document describes the API endpoints and interfaces available in the Claude Telegram Bridge project.

## Session Management API

### Create Session
```
POST /sessions
```

Creates a new Claude session with a generated UUID.

**Response**
```json
{
  "session_id": "uuid-string",
  "tmux_session": "uuid-string",
  "cwd": "/current/working/directory",
  "created_at": "timestamp"
}
```

### Get Session
```
GET /sessions/{session_id}
```

Retrieves information about a specific session.

**Response**
```json
{
  "session_id": "uuid-string",
  "tmux_session": "uuid-string",
  "cwd": "/current/working/directory",
  "created_at": "timestamp",
  "last_used": "timestamp"
}
```

### List Sessions
```
GET /sessions
```

Retrieves a list of all sessions.

**Response**
```json
[
  {
    "session_id": "uuid-string",
    "tmux_session": "uuid-string",
    "cwd": "/current/working/directory",
    "created_at": "timestamp",
    "last_used": "timestamp"
  }
]
```

### Delete Session
```
DELETE /sessions/{session_id}
```

Deletes a specific session.

## Claude Integration API

### Start Claude
```
POST /claude/start
```

Starts Claude with the specified session ID.

**Request**
```json
{
  "session_id": "uuid-string"
}
```

### Stop Claude
```
POST /claude/stop
```

Stops Claude for the specified session.

**Request**
```json
{
  "session_id": "uuid-string"
}
```

## Database Interface

### Session Storage
All session information is stored in an SQLite database with the following structure:

```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    cwd TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Command Line Interface

The bridge also provides a command line interface for basic operations:

### Usage
```
claude-bridge [command] [options]
```

### Commands
- `start` - Start a new Claude session
- `stop` - Stop a Claude session
- `list` - List all sessions
- `attach` - Attach to a session
- `help` - Show help information