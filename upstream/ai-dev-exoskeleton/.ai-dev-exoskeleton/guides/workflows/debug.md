# Workflow: Debugging

> Systematic debugging that finds root causes on the first attempt.

## The Prompt
```
MODE: debug
SCOPE: [service/directory where the error occurs]
ERROR: [paste exact error/traceback/unexpected behavior]
CONTEXT: [what you were doing when this happened]
CONSTRAINT: Trace the root cause FIRST. Do NOT change any code until I confirm your analysis.
DONE WHEN: Root cause identified with evidence, fix proposed but not applied.

Use @.ai-dev-exoskeleton/agents/debugger.md
```

## After AI Provides Root Cause Analysis
If you agree with the analysis:
```
Your analysis is correct. Implement the fix. Run tests after.
```

If you disagree:
```
I don't think that's the root cause because [reason]. Check [alternative hypothesis].
```

## For Cross-Service Bugs
```
MODE: debug
SCOPE: [service A directory] AND [service B directory]
ERROR: [paste error]
CONTEXT: This involves communication between [service A] and [service B] via [Redis/HTTP/etc]
CONSTRAINT: Use parallel agents to trace both sides simultaneously. Show me the data at the service boundary. Do NOT change code yet.
DONE WHEN: Root cause identified with evidence showing which service owns the bug.

Use @.ai-dev-exoskeleton/agents/debugger.md
```

## Common Traps to Avoid
- If the AI says "let me try this fix" without a trace → STOP IT. Say "trace first."
- If the AI fixes ONE instance of a pattern → STOP IT. Say "is this the root cause or a symptom?"
- If the AI guesses CLI flags or API methods → STOP IT. Say "read the actual source/docs."
