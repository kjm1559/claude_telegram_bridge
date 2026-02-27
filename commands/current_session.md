# /current_session Command

## Overview
The `/current_session` command displays the currently selected Claude session and provides session information. When no session is selected, it prompts the user to select a session.

## Command Syntax
```
/current_session
```

## Functionality

1. **Session Check**
   - Checks if a session is currently selected
   - Retrieves the current session ID from the user's context

2. **Session Information Display**
   - If session is selected:
     - Displays session ID
     - Shows working directory (cwd)
     - Shows creation time
     - Shows last used time
     - Indicates session status (active/inactive)
   - If no session selected:
     - Returns prompt message asking user to select a session

3. **User Context Management**
   - Maintains session selection in user context
   - Updates last_used timestamp in database when session is accessed

## Usage Example
```
/current_session
```

## Response Format

### When Session is Selected:
```
Current Session:
Session ID: 123e4567-e89b-12d3-a456-426614174000
Working Directory: /home/user/project
Created: 2026-02-28 10:30:00
Last Used: 2026-02-28 11:15:00
Status: Active
```

### When No Session Selected:
```
No session selected.
Please select a session using /sessions and /select_session command.
```

## Database Integration
The command interacts with the SQLite database to:
- Retrieve current session information
- Update last_used timestamp when session is accessed
- Store session selection in user context

## Error Handling
- If database connection fails: Returns error message
- If session selection cannot be retrieved: Returns appropriate message
- If session not found in database: Returns "Session not found" message