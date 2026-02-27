# /new_session Command

## Overview
The `/new_session` command creates a new Claude session with a unique UUID, starts a tmux session with that UUID, executes Claude with the session ID, and updates the SQLite database with session information.

## Command Syntax
```
/new_session
```

## Functionality

1. **UUID Generation**
   - Generates a unique UUID using `uuidgen` command
   - The UUID serves as both:
     - Claude session ID (`claude --session-id {uuid}`)
     - tmux session name

2. **tmux Session Creation**
   - Creates a new tmux session with the generated UUID as session name
   - Session persists across terminal sessions

3. **Claude Execution**
   - Executes Claude with the command: `claude --session-id {uuid}`
   - Session ID is passed as parameter to Claude

4. **Database Update**
   - Updates SQLite database with session information:
     - `session_id`: Generated UUID
     - `cwd`: Current working directory
     - `created_at`: Timestamp when session was created
     - `last_used`: Timestamp when session was last used

## Usage Example
```
/new_session
```

## Response Format
Upon successful execution, the command returns:
```
Session created successfully!
Session ID: 123e4567-e89b-12d3-a456-426614174000
tmux session: 123e4567-e89b-12d3-a456-426614174000
Claude started with session ID: 123e4567-e89b-12d3-a456-426614174000
```

## Error Handling
- If UUID generation fails: Returns error message
- If tmux session creation fails: Returns error message
- If Claude execution fails: Returns error message
- If database update fails: Returns error message

## Database Schema
The SQLite database table structure:
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    cwd TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Requirements
- `uuidgen` command available
- `tmux` installed and available
- `claude` CLI installed and available
- SQLite3 database access