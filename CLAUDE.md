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

Agent definitions are stored in the `/agents` directory of this project. This directory contains JSON files that define the structure and behavior of each agent, following the default agent format. The base agent definitions are documented in CLAUDE.md.

## Step 1: Planer Agent
The Planer agent is responsible for analyzing requirements and creating detailed implementation plans.

### Responsibilities:
- Analyze user requirements and project goals
- Break down complex tasks into manageable components
- Create detailed implementation strategies
- Identify potential challenges and solutions
- Review existing codebase structure and patterns
- Document the planned approach for implementation

## Step 2: Executer Agent
The Executer agent implements the plans created by the Planer agent.

### Responsibilities:
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
The main handler coordinates between these three agents to reach the project's goals:

1. **Requirement Analysis**: The Planer agent analyzes the task requirements
2. **Planning Phase**: The Planer agent creates a detailed plan
3. **Execution Phase**: The Executer agent implements the plan
4. **Validation Phase**: The Cheaker agent reviews and validates the implementation
5. **Feedback Loop**: Any issues identified are addressed through further planning and execution cycles

## Agent Coordination
- The Planer agent must complete its analysis before the Executer agent begins work
- The Executer agent must complete implementation before the Cheaker agent validates
- The Cheaker agent's feedback should be incorporated back into the Planer agent for potential revisions
- All agents should communicate clearly about their progress and any issues encountered

## Quality Assurance
- Each phase should be completed before moving to the next
- All code changes should be reviewed and validated
- The process should be iterative, allowing for refinement based on feedback
- Documentation should be maintained throughout all phases