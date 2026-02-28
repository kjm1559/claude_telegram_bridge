# /help Command

## Overview
The `/help` command displays a list of all available commands with brief descriptions of their functionality.

## Command Syntax
```
/help
```

## Functionality

1. **Command Listing**
   - Displays all available Telegram commands
   - Provides brief description for each command
   - Shows command syntax where applicable

2. **Information Format**
   - Lists commands in a readable format
   - Includes command name and purpose
   - Shows usage examples where relevant

## Usage Example
```
/help
```

## Response Format
```
Available Commands:
/new_session - Creates a new Claude session with UUID, tmux session, and database update
/sessions - Lists all currently active Claude sessions
/end_session {uuid} - Terminates a specific Claude session by UUID and updates database
/current_session - Displays currently selected Claude session information
/interrupt - Sends interrupt signal to stop running Claude processes
/help - Displays this help message

Type /help <command> for detailed information about a specific command.
````

## Detailed Help
When a specific command is requested:
```
/help interrupt
```

Response:
```
/interrupt - Sends interrupt signal to stop running Claude processes
Usage: /interrupt
Sends Escape key to the current tmux session to interrupt running processes.
````

## Error Handling
- If command parsing fails: Returns default help message
- If specific command not found: Returns "Command not found" message