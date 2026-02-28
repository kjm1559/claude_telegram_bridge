# Claude Telegram Bridge - Action Rules

This document outlines the action rules for the Claude Telegram Bridge project, following a structured approach using three specialized sub-agents: Planer, Executer, and Cheaker.

## Documentation Structure

This project uses a structured documentation approach:

- **README.md** - Primary project description, overview, and quick start guide
- **`.claude/CLAUDE.md`** - Action rules for agent collaboration and workflow
- **`/doc`** - Detailed technical documentation:
  - `architecture.md` - Technical architecture and system design
  - `usage.md` - Usage guide and operational instructions
  - `api.md` - API documentation and interfaces
- **`/tests`** - All test code files must be placed in this directory

All specification documents are stored in the `/doc` directory of this project.
All test code files must be placed in the `/tests` directory of this project.

## Team Structure and Agent Allocation

This project uses a team-based development approach with three specialized teams. Each team is responsible for specific phases of the development lifecycle.

### Team Definitions

#### 1. Planning Team (기획팀)
**Responsibilities:**
- Analyze requirements and define project scope
- Create detailed implementation plans
- Identify potential risks and dependencies
- Coordinate with other teams on timeline and deliverables

**Assigned Agents:**
- **Planer** - Primary agent for requirements analysis and planning
- **Architect** - Provides high-level design input during planning

**When to Use:**
- At the start of any new feature or major change
- When requirements are unclear or need refinement
- When creating implementation strategies

#### 2. Development Team (개발팀)
**Responsibilities:**
- Implement features according to the plan
- Write clean, maintainable code
- Ensure code aligns with system architecture
- Handle technical challenges and bugs

**Assigned Agents:**
- **Architect** - Ensures architectural consistency and provides guidance
- **Executer** - Primary agent for code implementation

**When to Use:**
- After planning phase is complete and approved
- When implementing new features or refactoring
- When fixing bugs or implementing improvements

#### 3. QA Team (QA 팀)
**Responsibilities:**
- Review and validate implemented code
- Run tests and verify functionality
- Ensure code quality and adherence to standards
- Provide feedback for improvements

**Assigned Agents:**
- **Cheaker** - Primary agent for validation and quality assurance
- **Executer** - Assists with running tests and validating fixes

**When to Use:**
- After development phase is complete
- Before merging code to main branch
- When regression testing is needed

### Team Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                    PROJECT START                            │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              Planning Team (기획팀)                          │
│  Agents: Planer + Architect                                 │
│  Output: Detailed implementation plan                       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│             Development Team (개발팀)                        │
│  Agents: Architect + Executer                               │
│  Output: Implemented code                                   │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                 QA Team (QA 팀)                              │
│  Agents: Cheaker + Executer                                 │
│  Output: Validated code with feedback                       │
└─────────────────────────────────────────────────────────────┘
                           │
                           ▼
                  (Feedback Loop)
                  └───┐
                      │
                      ▼
              (Return to appropriate team)
```

### Team Activation Rules

1. **Sequential Activation**: Teams should generally work in sequence (Planning → Development → QA)
2. **Parallel Within Teams**: Multiple agents within a team can work in parallel
3. **Handoff Points**: Each team must complete their phase before the next team begins
4. **Feedback Integration**: QA feedback should be routed back to the appropriate team

### Agent Collaboration Guidelines

- **Architect** can participate in both Planning and Development teams
- **Executer** can participate in both Development and QA teams
- **Planer** focuses solely on Planning team activities
- **Cheaker** focuses solely on QA team activities

## Agent Definitions

Agent definitions are stored in the `/.claude/agents` directory of this project. This directory contains JSON files that define the structure and behavior of each agent, following the default agent format.

### Agent-to-Team Mapping

| Agent | Primary Team | Secondary Team | Role |
|-------|-------------|----------------|------|
| **Planer** | Planning Team | - | Requirements Analysis |
| **Architect** | Development Team | Planning Team | System Design |
| **Executer** | Development Team | QA Team | Implementation |
| **Cheaker** | QA Team | - | Validation |

### Agent JSON Files
Each agent has a corresponding JSON file in `.claude/agents/`:
- `planer.json` - Planning Team primary agent
- `architect.json` - Development Team lead agent
- `executer.json` - Development/QA Team implementation agent
- `cheaker.json` - QA Team validation agent

## Test Code Structure

All test code must be placed in the `tests/` directory at the root of the project.

### Test File Naming Convention
- Test files must be named with the `test_` prefix (e.g., `test_bot.py`, `test_command_handlers.py`)
- Each source file should have a corresponding test file (e.g., `src/bot.py` → `tests/test_bot.py`)

### Test Organization
- `tests/__init__.py` - Package initialization file
- `tests/test_*.py` - Individual test files for each module

### Test Requirements
- All tests must be written using pytest framework
- Tests must be self-contained and not require external dependencies beyond what's in the project
- Mock external services (Telegram API, Claude API) when writing tests
- Tests should be deterministic and not depend on timing or external state

## Main Handler Process

The main handler coordinates between teams to reach the project's goals. Teams work in sequence, with clear handoff points and feedback loops.

### Phase 1: Planning Team (기획팀)
**Agents:** Planer + Architect
**Activities:**
1. Architect reviews overall system design requirements
2. Planer analyzes user requirements and project goals
3. Planer creates detailed implementation plan
4. Both agents identify potential challenges and solutions
5. Plan documents are created and reviewed

**Deliverables:**
- Requirements analysis document
- Implementation plan with task breakdown
- Risk assessment
- Timeline estimate

### Phase 2: Development Team (개발팀)
**Agents:** Architect + Executer
**Activities:**
1. Architect reviews plan and validates implementation approach
2. Architect provides architectural guidance and patterns
3. Executer implements the plan
4. Executer writes code and handles technical challenges
5. Architect ensures code aligns with system architecture

**Deliverables:**
- Implemented code changes
- Documentation updates
- Initial test results

### Phase 3: QA Team (QA 팀)
**Agents:** Cheaker + Executer
**Activities:**
1. Cheaker reviews implemented code for correctness and quality
2. Cheaker verifies that requirements have been met
3. Cheaker runs tests and identifies any issues
4. Cheaker validates adherence to coding standards
5. Executer assists with test execution and fix validation

**Deliverables:**
- Code review report
- Test results
- Feedback and improvement suggestions
- Final validation confirmation

### Feedback Loop
If QA identifies issues:
1. Critical bugs → Return to Development Team
2. Design flaws → Return to Planning Team
3. Minor fixes → Development Team handles directly

This iterative process ensures continuous improvement and quality assurance throughout development.

## Team Coordination Rules

### Handoff Requirements
- **Planning → Development**: Detailed plan must be documented and approved
- **Development → QA**: Code must be functional with initial tests passing
- **QA → Development/Planning**: Clear feedback with issue classification

### Communication Guidelines
- Each team should document their progress and findings
- Handoff points should include summary of work completed
- Blockers and risks should be communicated immediately
- All teams should maintain awareness of overall project status

### Quality Gates
1. **Planning Gate**: Plan must be approved before development starts
2. **Development Gate**: Code must pass initial tests before QA review
3. **QA Gate**: All issues must be resolved before merge to main

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