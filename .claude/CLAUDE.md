# Claude Telegram Bridge - Action Rules

## Project Structure

- **README.md** - Project description and quick start
- **`.claude/CLAUDE.md`** - Action rules for agent collaboration
- **`/doc`** - Technical documentation (architecture.md, usage.md, api.md)
- **`/tests`** - All test code files (pytest framework, test_*.py naming)
- **`/.claude/agents`** - Agent definition JSON files

## Team Structure

| Team | Agents | Responsibility |
|------|--------|----------------|
| **Planning (기획팀)** | Planer + Architect | Requirements analysis, implementation planning |
| **Development (개발팀)** | Architect + Executer | Code implementation |
| **QA (QA 팀)** | Cheaker + Executer | Testing and validation |
| **ContextManager** | - | Memory & context management (across all teams) |

## Mandatory Workflow

```
Planning Team → Development Team → QA Team
                    ↓
            (commit & push)
                    ↓
            (test & validate)
                    ↓
            PASSED → merge to main
            FAILED → back to Development
```

### Critical Rules

1. **Sequential Execution**: Planning → Development → QA (no skipping phases)
2. **Team Separation**:
   - Only Development Team modifies code
   - Only QA Team performs testing
3. **Git Commit After Every Change**:
   ```bash
   git add <files>
   git commit -m "<descriptive message>"
   git push origin <branch>
   ```
4. **No QA Skipping**: All changes require QA validation before merge

### Violations (금지 사항)

- ❌ Skip QA phase for any change
- ❌ Merge without QA approval
- ❌ Development agents performing QA tasks
- ❌ QA agents modifying production code
- ❌ Uncommitted code after development

## ContextManager Trigger Conditions

Activate when:
- Conversation exceeds ~50 turns
- Large code changes (>100 lines)
- Architectural decisions made
- Context grows too large mid-session

## Test Requirements

- All tests in `tests/` directory with `test_` prefix
- Use pytest framework
- Mock external services (Telegram API, Claude API)
- Tests must be deterministic and self-contained
