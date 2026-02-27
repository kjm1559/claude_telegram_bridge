# /sessions Command

## Overview
The `/sessions` command lists all currently active Claude sessions with their status information.

## Command Syntax
```
/sessions
```

## Functionality

1. **Session Retrieval**
   - Queries the SQLite database for all stored sessions
   - Retrieves session information including:
     - `session_id`: UUID of the session
     - `cwd`: Current working directory
     - `created_at`: Timestamp when session was created
     - `last_used`: Timestamp when session was last used
     - `is_active`: Boolean indicating if session is currently active

2. **Active Session Detection**
   - Checks tmux sessions to determine current activity status
   - Updates the `is_active` field in the database
   - Displays active sessions first in the output

3. **Output Format**
   - Lists all sessions in a readable format
   - Shows session ID, working directory, creation time, and activity status
   - Indicates which sessions are currently active

## Usage Example
```
/sessions
```

## Response Format
```
Active Sessions:
1. Session ID: 123e4567-e89b-12d3-a456-426614174000
   Working Directory: /home/user/project
   Created: 2026-02-28 10:30:00
   Status: Active

2. Session ID: 5678e456-789b-12d3-a456-426614174001
   Working Directory: /home/user/documents
   Created: 2026-02-28 09:15:00
   Status: Inactive

Total Sessions: 2
Active Sessions: 1
```

## Database Integration
The command queries the SQLite database table structure:
```sql
CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    cwd TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT 0
);
```

## Error Handling
- If database connection fails: Returns error message
- If no sessions found: Returns "No sessions found" message
- If query fails: Returns appropriate error information