# Command Handler Implementation

## Overview
The command handler is responsible for processing Telegram commands and executing the appropriate actions.

## Structure
```
class CommandHandler:
    def __init__(self):
        self.commands = {
            '/new_session': self.handle_new_session,
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

## Error Handling
- UUID generation failures
- tmux session creation failures
- Claude execution failures
- Database connection/insertion failures