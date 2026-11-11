# Pre-Session Checklist

> Human-optional. I don't personally run this every time — once the habit is internalized,
> you just do it. But it's a useful scaffold when you're new to the method or onboarding a
> team, so it's kept here.

Before starting ANY AI coding session, answer these 6 questions:

## 1. What is the ONE outcome?
Write it in one sentence. If you need "and" — split into two sessions.
```
Example BAD:  "Migrate Redis pub/sub to streams AND update all handlers"
Example GOOD: "Create the RedisStreamPublisher adapter"
```

## 2. Which mode?
- [ ] **Plan** — produce a plan document; never touches source code
- [ ] **Implement** — change the codebase (code, tests, config) following a plan
- [ ] **Debug** — find the root cause of a specific bug; fix only after it's confirmed
- [ ] **Review** — analyze a change and report findings; never touches source code
- [ ] **Explore** — read the codebase to answer questions or document it; never touches
      source code

Note: "never touches source code" is the boundary that matters — plan, review, and explore
all *write their own markdown artifacts* (a plan, a review, `docs/context/` docs). What
they don't do is modify the project itself. Onboarding runs in explore mode for exactly
this reason: it reads all the code and writes only documentation.

## 3. What's in scope?
List the directories/files. Everything else is OFF LIMITS.
```
SCOPE: app/services/profile_service.py, app/interfaces/profile/repo.py, tests/test_profile_service.py
```

## 4. What must it NOT do?

The most valuable line in most prompts. A stop condition says when to finish; a constraint
keeps the agent out of the ditch on the way there. Be specific and negative:
```
CONSTRAINT: don't refactor existing code
CONSTRAINT: no code yet — analysis only
CONSTRAINT: don't change the API surface or rename anything
CONSTRAINT: don't add new dependencies
CONSTRAINT: don't touch the migration files
```
If a previous session went wrong in a way you can name, that name is your next constraint.

## 5. What does "done" look like?
```
Example: "Unit test for get_or_create_profile passes"
Example: "Plan document written to docs/tasks/20260304-redis-migration/PLAN.md"
Example: "Root cause identified with evidence, fix not yet applied"
```

## 6. Does this fit in one session?

Don't calibrate on minutes or message counts — those shift with every model generation.
Calibrate on **units of work and the context window you have**:

- **The unit is a phase**: one scope, one verifiable "done" you can state in a single
  sentence without "and."
- **How many phases per session depends on the window:** one on ~200k, several on ~1M.
- **Too big** for any window if: you can't describe "done" without a list, or you find
  yourself planning mid-implementation.
- **Too small** if: it finishes in a couple of exchanges with nothing to verify — fold it
  into the neighbouring piece.

**Then watch for context rot as you go** — Law 1 lists the symptoms and when ending costs nothing.

---

## Quick-Start Templates

### Feature Session (start here)
```
Read @.ai-dev-exoskeleton/commands/build-context.md and follow it.
I want to build [feature description].
```
This begins the feature workflow at context-building; see
`.ai-dev-exoskeleton/guides/workflows/feature.md` for the full session sequence.

### Planning Session
```
I need a plan for [X]. Read @.ai-dev-exoskeleton/agents/planner.md and follow it.
SCOPE: [directories to analyze]
Create a task folder at docs/tasks/[yyyymmdd-task-name]/ and write the plan to PLAN.md.
Do NOT implement anything.
```

### Implementation Session
```
Implement Phase [N] from docs/tasks/[yyyymmdd-task-name]/PLAN.md. Read @.ai-dev-exoskeleton/agents/implementer.md and follow it.
SCOPE: [files from the plan]
No behaviour without a test you've seen fail. Run tests after.
```

### Debug Session
```
Debug this error. Read @.ai-dev-exoskeleton/agents/debugger.md and follow it.
SCOPE: [directory]
ERROR: [paste traceback]
Trace the root cause first. Do NOT change code until I confirm.
```
