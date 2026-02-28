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

## JSONL Response Formatting

Claude responses are stored in JSONL format and formatted for Telegram display.

### Input JSONL Format

Claude stores conversations in JSONL files with the following structure:

```json
{"role":"user","content":"message text"}
{"role":"assistant","content":"...","tool_calls":[{"name":"tool_name","arguments":{...}}]}
{"role":"tool","content":"...","tool_call_id":"..."}
{"role":"result","content":"..."}
```

### Output Format for Telegram

#### 1. User Messages
- Display the `content.text` value
- Prefix: `👤 User:`

#### 2. Assistant Messages (with Tool Calls)
- Identify the tool being called
- Display tool name and input parameters
- Format:
```
🔧 Tool: tool_name
📝 Input:
{param1: value1, param2: value2}
```

#### 3. Tool Results
- Display the `content.text` value from the result
- Prefix: `⚙️ Result:`

#### 4. System Messages
- Not displayed (filtered out)

#### 5. Final Results
- When a `result` role message is received, display:
```
✅ 작업이 종료되었습니다
```

### Telegram Integration

#### Typing Indicators
- **Start**: When displaying new response, send `chat_action: typing`
- **End**: When final result is reached, stop sending `typing` action

#### Example Flow

**User Input**:
```
👤 User: 다음 코드 리팩토링해줘
```

**Tool Call**:
```
🔧 Tool: read_file
📝 Input:
{file_path: "src/main.py"}
```

**Tool Result**:
```
⚙️ Result:
def main():
    ... (file contents)
```

**Final Result**:
```
✅ 작업이 종료되었습니다
```