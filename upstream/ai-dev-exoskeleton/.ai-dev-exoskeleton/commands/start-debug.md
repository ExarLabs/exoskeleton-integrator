# /start-debug — Structured Debugging Session

One-shot root cause analysis with a defined output artifact. Diagnoses the bug and proposes options — **does NOT modify code**.

For the investigation methodology, follow the `../agents/debugger.md` agent's rules: hypothesis-driven, evidence-based, no fixes.

## Quick Rules
- NEVER modify or implement anything — diagnosis and proposals only
- NEVER add try/catch, suppress errors, or apply quick patches
- NEVER guess — trace the full call chain with evidence before concluding

## Done When
1. Root cause(s) identified with evidence (file paths, line numbers, call chain trace)
2. 2–3 solution proposals per root cause, presented in the output format below
3. Recommended option selected with reasoning

## Output Format

### Root Cause Analysis

For each root cause found:

```
TRACE: [entry point] → [function A] → [function B] → [FAILURE HERE]
ROOT CAUSE: <concise description of what is actually wrong>
EVIDENCE: <file:line references, data shapes, or logs that prove this>
```

### Solution Proposals

For each root cause, present solutions as a table:

| # | Approach | Complexity | Risk | Effort | Trade-offs |
|---|----------|-----------|------|--------|------------|
| 1 | ... | Low/Med/High | Low/Med/High | S/M/L | ... |
| 2 | ... | Low/Med/High | Low/Med/High | S/M/L | ... |
| 3 | ... | Low/Med/High | Low/Med/High | S/M/L | ... |

**Recommended:** #N — <reasoning why this is the best approach>

### Summary
Brief summary of all findings and the recommended path forward.

If `docs/context/overrides/<this file's name>` exists, read it — where it conflicts with this file, it wins.
