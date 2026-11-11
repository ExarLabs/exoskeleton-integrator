# /adversarial-review — Cross-Model Adversarial Review

Get an independent, skeptical second opinion on a plan, a diff, or a design — from a
**different model or harness than the one that produced it**. The reviewer's job is to
find what's wrong, weak, or self-deceiving, not to praise. This is how you catch the
"confident but wrong" output a single model can't see in its own work.

## When to use

- After a plan is written, before implementing (highest leverage — mistakes are free here).
- After a large or risky change, before merging.
- On any decision where being wrong is expensive and the first model was too agreeable.

## The rule that makes it work

**Run the review in a different model/harness than the one that wrote the artifact.**
A model reviewing its own output shares its own blind spots. The whole value is the
independence — Claude plans, a different model attacks; or vice versa.

## Quick Rules

- The reviewer is READ-ONLY. It audits; it does not fix, so the findings stay honest.
- Rank findings by severity: CRITICAL > WARNING > NOTE.
- Every finding: the specific problem, why it matters, and a concrete recommendation.
- Default to skepticism. If the reviewer is uncertain, it says "unverified" rather than
  waving the claim through.
- No praise padding. A finding-free section gets one line, not a paragraph of reassurance.

## Process

1. **Give the reviewer the artifact and the context.** Paste or point to the plan/diff,
   plus what it's trying to achieve and any hard constraints. State explicitly:
   "Adversarial audit. Find what's wrong. Do not modify anything."
2. **Ask for severity-ranked findings** in the format below, ending with the 2–3 decisions
   worth reconsidering before another line is written — that forces prioritization.
3. **Reconcile.** Read the findings against the original. Accept what's real, reject what
   isn't (and note why). The point is a better artifact, not blind obedience to the critic.

## Output Format

```
## Adversarial Review: [what was reviewed]

### CRITICAL
- [problem] — why it matters — [concrete recommendation]

### WARNING
- ...

### NOTE
- ...

### Decisions to reconsider before proceeding
1. ...
2. ...
```

If `docs/context/overrides/<this file's name>` exists, read it — where it conflicts with this file, it wins.
