# Chat Input Handling

## Overview
When users send chat messages (non-command inputs), the system checks if a session is selected and routes the input appropriately to the selected tmux session. If no session is selected, it prompts the user to select one.

## Input Processing Flow

1. **Message Detection**
   - System detects non-command input (text that doesn't start with "/")
   - Determines if user has selected a session

2. **Session Check**
   - If session is selected:
     - Routes input to the selected tmux session
     - Uses command: `tmux send-keys -t <target> "input command" C-m`
   - If no session selected:
     - Returns prompt message asking user to select a session

3. **Project Directory Resolution**
   - Resolves project directory based on cwd:
     - cwd: `/home/user/path`
     - Project folder: `/home/user/path/-home-user-path`
   - Uses project directory structure to store session data

4. **Session Data Tracking**
   - For selected session, tracks command execution progress
   - Stores information in SQLite database:
     - session_id
     - last_processed_message_index (for tracking message progress)
     - last_updated timestamp

5. **Message Monitoring**
   - Monitors project directory for JSONL files created by Claude
   - Tracks file size changes to detect new messages
   - When file size increases:
     - Reads new messages from the end of the file
     - Sends new messages to Telegram
     - Updates database with new message index

## Implementation Details

### Command Routing
When a session is selected and user sends input:
```
tmux send-keys -t {session_id} "{user_input}" C-m
```

### Project Directory Structure
- cwd: `/home/user/path`
- Project folder: `/home/user/path/-home-user-path`
- Session JSONL file: `/home/user/path/-home-user-path/{session_id}.jsonl`

### Data Tracking
Database table structure for tracking session progress:
```sql
CREATE TABLE session_progress (
    session_id TEXT PRIMARY KEY,
    last_processed_message_index INTEGER DEFAULT 0,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Usage Example

### When Session Selected:
```
User: "What is the weather today?"
System: Routes input to tmux session
System: Sends command: tmux send-keys -t 123e4567-e89b-12d3-a456-426614174000 "What is the weather today?" C-m
```

### When No Session Selected:
```
User: "Hello"
System: Returns prompt
"Please select a session using /sessions and /select_session command."
```

## Error Handling
- If tmux session not found: Returns error message
- If session not selected: Returns selection prompt
- If database update fails: Logs error and continues
- If JSONL file monitoring fails: Returns appropriate error
- If command execution fails: Returns error message