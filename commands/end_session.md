# /end_session Command

## Overview
The `/end_session` command terminates a specific Claude session by its UUID and updates the SQLite database to mark it as inactive.

## Command Syntax
```
/end_session {uuid}
```

## Functionality

1. **Session Validation**
   - Validates that the provided UUID exists in the database
   - Checks if the session is currently active
   - Ensures the session can be safely terminated

2. **tmux Session Termination**
   - Terminates the tmux session with the specified UUID
   - Uses `tmux kill-session -t {uuid}` command
   - Verifies session termination

3. **Database Update**
   - Updates the SQLite database record for the session
   - Sets `is_active` field to 0 (inactive)
   - Updates `last_used` timestamp to current time

4. **Confirmation**
   - Returns success message with session information
   - Indicates that the session has been terminated
   - Provides confirmation that database was updated

## Usage Example
```
/end_session 123e4567-e89b-12d3-a456-426614174000
```

## Response Format
Upon successful termination:
```
Session terminated successfully!
Session ID: 123e4567-e89b-12d3-a456-426614174000
tmux session closed
Database updated: session marked as inactive
```

## Error Handling
- If UUID not found: Returns "Session not found" message
- If tmux session termination fails: Returns error message
- If database update fails: Returns error message
- If session is already inactive: Returns appropriate message
- If UUID format is invalid: Returns validation error