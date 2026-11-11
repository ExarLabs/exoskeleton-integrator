# Workflow: Refactoring

> Safe refactoring with consumer analysis and rollback safety.

## Session 1: Impact Analysis (Plan Only)
```
MODE: plan
SCOPE: [what you want to refactor]
CONTEXT: I want to refactor [X] to [Y] because [reason]
CONSTRAINT: Do NOT change any code. Analyze all consumers first.
DONE WHEN: Impact analysis written to docs/tasks/[yyyymmdd-task-name]/PLAN.md

Steps:
1. Find ALL consumers of [thing being refactored] using grep/search across entire codebase
2. List every file that imports, calls, or references it
3. Categorize: direct users, indirect users, test references
4. Identify the safe order of changes (leaf consumers first)
5. Propose phases where each phase maintains backward compatibility

Use @.ai-dev-exoskeleton/agents/planner.md
```

## Session 2-N: Implement Each Phase
```
MODE: implement
SCOPE: [files in this phase]
CONTEXT: Implementing Phase [N] of refactoring plan
CONSTRAINT: Maintain backward compatibility within this phase. Do NOT remove old interfaces until ALL consumers are migrated. Run tests after each change.
DONE WHEN: Tests pass, old and new code coexist.

Use @.ai-dev-exoskeleton/agents/implementer.md
```

## Final Session: Remove Old Code
```
MODE: implement
SCOPE: [old files/functions to remove]
CONTEXT: All consumers have been migrated. Removing old interfaces.
CONSTRAINT: Before deleting ANYTHING, run one final grep to confirm zero remaining consumers. Run full test suite after removal.
DONE WHEN: Old code removed, all tests pass.
```

## Critical Rules
- NEVER remove a function/export until ALL consumers are migrated
- ALWAYS run `grep` for the function name before deletion
- Keep old and new code coexisting during migration phases
- Each phase must leave the codebase in a working state
