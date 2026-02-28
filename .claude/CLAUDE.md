# Claude Telegram Bridge - Action Rules

This document outlines the action rules for the Claude Telegram Bridge project, following a structured approach using three specialized sub-agents: Planer, Executer, and Cheaker.

## Documentation Structure

All specification documents are stored in the `/doc` directory of this project. This directory serves as the central location for all project documentation including:
- Technical specifications
- API documentation
- User guides
- Development guidelines
- Process documentation

## Agent Definitions

Agent definitions are stored in the `/.claude/agents` directory of this project. This directory contains JSON files that define the structure and behavior of each agent, following the default agent format. The base agent definitions are documented in CLAUDE.md.

### Available Agents

1. **Architect** - Responsible for designing the overall system structure and high-level implementation strategies
2. **Planer** - Responsible for analyzing requirements and creating detailed implementation plans
3. **Executer** - Implements the plans created by the Planer agent
4. **Cheaker** - Validates the work produced by the Executer agent

Each agent has a corresponding JSON file in the agents directory that defines:
- Agent name and description
- Core responsibilities
- Specializations
- tools used

## Step 1: Planer Agent
The Planer agent is responsible for analyzing requirements and creating detailed implementation plans.

### Responsibilities:
- Analyze user requirements and project goals
- Break down complex tasks into manageable components
- Create detailed implementation strategies
- Identify potential challenges and solutions
- Review existing codebase structure and patterns
- Document the planned approach for implementation

## Step 2: Architect & Executer Collaboration
The Architect and Executer agents work together to implement the system design and execute the implementation plan.

### Responsibilities:
- **Architect Agent**:
  - Review and validate implementation approaches
  - Ensure code aligns with overall system architecture
  - Provide guidance on architectural patterns and best practices
  - Coordinate implementation with system design

- **Executer Agent**:
  - Execute the implementation plan
  - Write or modify code files
  - Run tests and validate functionality
  - Ensure code quality and adherence to project standards
  - Document implementation details
  - Handle any issues that arise during execution

## Step 3: Cheaker Agent
The Cheaker agent validates the work produced by the Executer agent.

### Responsibilities:
- Review implemented code for correctness and quality
- Verify that requirements have been met
- Test functionality and identify any issues
- Validate adherence to coding standards
- Provide feedback and suggestions for improvement
- Confirm that the implementation is complete and working

## Main Handler Process
The main handler coordinates between these agents to reach the project's goals:

1. **Architecture Phase**: The Architect agent designs the overall system structure and high-level strategies
2. **Requirement Analysis**: The Planer agent analyzes the task requirements
3. **Planning Phase**: The Planer agent creates a detailed plan
4. **Architecture & Execution Collaboration**: The Architect and Executer agents collaborate to implement the system design
5. **Validation Phase**: The Cheaker agent reviews and validates the implementation
6. **Feedback Loop**: Any issues identified are addressed through further planning and execution cycles

## Agent Coordination
- The Architect agent must complete the system design before the Planer agent begins detailed planning
- The Planer agent must complete its analysis before the Executer agent begins work
- The Executer agent must complete implementation before the Cheaker agent validates
- The Cheaker agent's feedback should be incorporated back into the Planer agent for potential revisions
- All agents should communicate clearly about their progress and any issues encountered

## Quality Assurance
- Each phase should be completed before moving to the next
- All code changes should be reviewed and validated
- The process should be iterative, allowing for refinement based on feedback
- Documentation should be maintained throughout all phases

## Agent Workflow
The agents work in a coordinated sequence:
1. **Architect Agent** - Designs overall system structure and high-level strategies
2. **Planer Agent** - Analyzes requirements and creates implementation plans
3. **Architect & Executer Agents** - Collaborate to implement the system design and execute the plan
4. **Cheaker Agent** - Validates the work produced by the Executer agent

The feedback loop ensures continuous improvement and quality assurance throughout the development process.

## Git Workflow and Documentation
All changes are committed to the git repository with descriptive commit messages that summarize the work done. This creates a detailed history that serves as long-term memory for the project.

### Commit Practices
- Each commit should include a clear, descriptive message summarizing the work completed
- Changes should be committed and pushed after each significant task or feature implementation
- Commit messages should be concise but informative about what was accomplished

### Long-term Memory Access
The git history serves as a comprehensive record of:
- All implemented features and functionality
- Development decisions and approaches
- System architecture evolution
- Problem-solving processes and solutions

### Usage Example
To access the project history for reference:
```
git log --oneline
git show <commit-hash>
```

This approach ensures that all work is properly documented and can be referenced for future development, troubleshooting, or knowledge sharing.

## Command Structure
The system supports Telegram commands using the format `/command_name`:
- `/new_session` - Creates a new Claude session with UUID, tmux session, and database update
- `/sessions` - Lists all currently active Claude sessions
- `/end_session {uuid}` - Terminates a specific Claude session by UUID and updates database
- `/current_session` - Displays currently selected Claude session information
- `/interrupt` - Sends interrupt signal to stop running Claude processes
- `/help` - Displays available commands and their usage

## Chat Input Handling
When users send chat messages (non-command inputs):
- If a session is selected: Routes input to the tmux session using `tmux send-keys`
- If no session is selected: Prompts user to select a session
- Monitors project directory for new Claude responses in JSONL files
- Sends new messages to Telegram when detected

## Command Structure
The system supports Telegram commands using the format `/command_name`:
- `/new_session` - Creates a new Claude session with UUID, tmux session, and database update