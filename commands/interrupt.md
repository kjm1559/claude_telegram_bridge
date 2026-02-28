# /interrupt Command

## Overview
The `/interrupt` command sends an interrupt signal to the currently active Claude session, stopping any running commands or processes in the tmux session.

## Command Syntax
```
/interrupt
```

## Functionality

1. **Session Check**
   - Verifies that a session is currently selected
   - Retrieves the current session ID from user context

2. **Interrupt Signal**
   - Sends interrupt signal to the tmux session using:
     ```
     tmux send-keys -t {session_id} Escape
     ```
   - The Escape key is sent to the tmux session to interrupt running processes

3. **Confirmation**
   - Returns success message confirming the interrupt was sent
   - Indicates which session was interrupted

## Usage Example
```
/interrupt
```

## Response Format
```
Interrupt signal sent to session: 123e4567-e89b-12d3-a456-426614174000
Current Claude process interrupted
```

## Error Handling
- If no session selected: Returns "No session selected" message
- If tmux session not found: Returns error message
- If command execution fails: Returns appropriate error information