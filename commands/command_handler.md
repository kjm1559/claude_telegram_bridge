# Command Handler Implementation

## Overview
The command handler is responsible for processing Telegram commands and executing the appropriate actions.

## Structure
```
class CommandHandler:
    def __init__(self):
        self.commands = {
            '/new_session': self.handle_new_session,
            '/sessions': self.handle_sessions,
            '/end_session': self.handle_end_session,
            # Additional commands will be added here
        }

    def handle_command(self, command, message):
        """Process incoming Telegram command"""
        if command in self.commands:
            return self.commands[command](message)
        else:
            return self.handle_unknown_command(command)

    def handle_new_session(self, message):
        """Handle /new_session command"""
        # Implementation details here
        pass

    def handle_sessions(self, message):
        """Handle /sessions command"""
        # Implementation details here
        pass

    def handle_end_session(self, message):
        """Handle /end_session command"""
        # Implementation details here
        pass

    def handle_unknown_command(self, command):
        """Handle unknown commands"""
        return f"Unknown command: {command}"
```

## Implementation Steps for /new_session

1. **Generate UUID**
   - Use `uuidgen` to create unique session ID
   - Validate UUID generation

2. **Create tmux Session**
   - Execute `tmux new-session -d -s {uuid}`
   - Verify session creation

3. **Launch Claude**
   - Execute `claude --session-id {uuid}`
   - Ensure proper session handling

4. **Update Database**
   - Connect to SQLite database
   - Insert session record with session_id, cwd, timestamps
   - Handle database errors gracefully

5. **Return Response**
   - Send success message to user
   - Include session information
   - Handle any errors appropriately

## Implementation Steps for /sessions

1. **Query Database**
   - Connect to SQLite database
   - Retrieve all session records
   - Check active status of each session

2. **Check tmux Status**
   - Verify which tmux sessions are currently active
   - Update database `is_active` field accordingly

3. **Format Response**
   - Organize session information
   - Show active sessions first
   - Include session details and status

4. **Return Response**
   - Send formatted session list to user
   - Handle any database or query errors

## Implementation Steps for /end_session

1. **Validate Input**
   - Parse UUID from command message
   - Validate UUID format
   - Check if session exists in database

2. **Terminate tmux Session**
   - Execute `tmux kill-session -t {uuid}`
   - Verify session termination

3. **Update Database**
   - Connect to SQLite database
   - Set `is_active` field to 0 for the session
   - Update `last_used` timestamp
   - Handle database errors gracefully

4. **Return Response**
   - Send success message to user
   - Include session information
   - Handle any errors appropriately

## Error Handling
- UUID generation failures
- tmux session creation failures
- Claude execution failures
- Database connection/insertion failures
- Session termination failures
- Invalid UUID format