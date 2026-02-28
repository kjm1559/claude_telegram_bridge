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
- tmux session not found
- JSONL file monitoring failures
- Interrupt command failures
- Help command failures

## Implementation Steps for /interrupt

1. **Session Check**
   - Verify that a session is currently selected
   - Retrieve session ID from user context

2. **Send Interrupt**
   - Execute `tmux send-keys -t {session_id} Escape`
   - Verify interrupt was sent successfully

3. **Return Response**
   - Send confirmation message
   - Include session information
   - Handle any errors appropriately

## Implementation Steps for /help

1. **Generate Help Content**
   - Compile list of all available commands
   - Add descriptions for each command
   - Format response for Telegram

2. **Handle Specific Command Help**
   - If command specified: Show detailed help for that command
   - If no command specified: Show general help

3. **Return Response**
   - Send formatted help message to user
   - Handle any errors appropriately

## Chat Input Handling

1. **Message Detection**
   - Detect non-command input (text that doesn't start with "/")
   - Determine if user has selected a session

2. **Session Routing**
   - If session selected: Route input to tmux session using `tmux send-keys`
   - If no session selected: Return prompt to select session

3. **Project Directory Resolution**
   - Resolve project directory based on cwd
   - Create project folder structure: `/home/user/path/-home-user-path`

4. **Session Data Tracking**
   - Monitor JSONL file for new messages
   - Track message index in database
   - Update database when new messages are detected

5. **Message Monitoring**
   - Monitor project directory for new Claude responses
   - When file size increases: Read new messages from end of file
   - Send new messages to Telegram
   - Update database with new message index

## Implementation Steps for /current_session

1. **Check Current Session**
   - Retrieve current session from user context
   - Validate session exists in database

2. **Display Session Info**
   - If session selected: Show session details (ID, cwd, timestamps, status)
   - If no session selected: Return prompt to select session

3. **Update Database**
   - Update last_used timestamp for the session
   - Handle database errors gracefully

4. **Return Response**
   - Send appropriate message to user
   - Handle any errors appropriately