# Workflow: New Feature

> Small, testable, incremental steps. Each phase is independently testable, and if something
> goes wrong, the task folder has everything needed to recover.
>
> **How these map onto sessions is up to you and your context window.** With a large window
> you can carry several of these steps in one session. What I'd recommend: keep **one main
> session** that holds the thread, and spawn subagents from it for the heavy lifting if your
> harness supports them. Watch for context rot either way (see Law 1).

---

### Step 0: Build Context (align first)

Before any planning, get you and the agent to a shared understanding of the feature.
This front-loaded alignment is what makes everything after it fast — do it well once
and later steps only need you to check the output.

```
Read @.ai-dev-exoskeleton/commands/build-context.md and follow it.
I want to build [feature description].
```

Output: `docs/tasks/[yyyymmdd-task-name]/CONTEXT.md` — the business and technical
decisions, in and out of scope. This file lets any later session rebuild context without
re-doing the Q&A. Its last question is the task's rigor, and your answer is recorded there
under `## Rigor`; every later step reads it.

### Step 1: Plan

**If you just built context properly, the prompt is trivial.** Everything the planner needs
is already in the conversation and in `CONTEXT.md` — don't re-type it as a giant structured
prompt:

```
Based on everything we discussed, follow @.ai-dev-exoskeleton/agents/planner.md
and write the PLAN.md.
```

That's genuinely enough. The context you built is doing the work.

<details>
<summary><b>If you skipped or rushed the context step</b>, you need the full prompt instead:</summary>

```
MODE: plan
SCOPE: [all relevant directories]
CONTEXT: Building [feature description]. Read docs/context/ first
  (start at docs/context/README.md) to understand existing architecture.
CONSTRAINT: Do NOT implement. Only create a plan document.
DONE WHEN: docs/tasks/[yyyymmdd-task-name]/PLAN.md created with a phased
  breakdown — each phase has Scope, Depends on, Verify, and Rollback.

Use @.ai-dev-exoskeleton/agents/planner.md
```

</details>

Review the plan. Adjust phases. Each phase should be independently testable.

### Step 2 (heavy): Review the Plan

**Mandatory when the task is heavy, skipped when light** (see "Light or heavy" in
`PLAYBOOK.md`). Nothing has been built yet, so this is the cheapest place to catch a wrong
plan:

```
MODE: plan
SCOPE: docs/tasks/[yyyymmdd-task-name]/PLAN.md + all source files it references
CONTEXT: Review this plan against the actual codebase before we implement.
  Read docs/context/ for architecture and pattern rules.
CONSTRAINT: Do NOT implement anything. Only analyze and update the plan.
DONE WHEN: Plan updated. Specifically check:
  1. Inconsistencies — does anything contradict existing behavior or docs?
  2. Underspecified behavior — edge cases, error scenarios, state transitions?
  3. Architecture conflicts — does it violate docs/context/PATTERNS.md or ARCHITECTURE.md?
  4. Code reuse — existing utilities/services to reuse instead of building fresh?
  5. Missing acceptance criteria — what does "done" look like that isn't captured?
  Ask clarifying questions for anything ambiguous, then update the plan.

Use @.ai-dev-exoskeleton/agents/planner.md
```

Heavy also means a second opinion from outside: run `adversarial-review` on the same plan in
a **different model or harness** (see `.ai-dev-exoskeleton/commands/adversarial-review.md`).
The planner says so when it hands you a heavy plan, so you don't have to remember it.

### Step 3: Implement the Phases

```
MODE: implement
SCOPE: [files listed in this phase of the plan]
CONTEXT: Implementing Phase [N] of docs/tasks/[yyyymmdd-task-name]/PLAN.md
CONSTRAINT: Only change files listed in this phase. No behaviour without a test you've seen fail.
DONE WHEN: All tests pass, including existing ones. On a heavy task, the recorded gates are
  green too.

Use @.ai-dev-exoskeleton/agents/implementer.md
```

**Parallelise here if your harness can.** Hand independent work to subagents running
concurrently — and a subagent doesn't have to be limited to a single phase. Give one
subagent a whole chain of dependent phases if that chain is independent of what the others
are doing.

The rule that makes it safe is the same either way: **two units of work can run in parallel
only if they share no files and neither depends on the other.** That's exactly what the
`Scope` and `Depends on` fields in the plan are for. Without a harness that supports
subagents, use separate sessions in separate git worktrees (Law 5).

**A heavy plan ends with a hardening phase**, where the implementer only writes tests and
checks that they would catch a wrong behaviour. Run it like any other phase — ideally in its
own session, so the agent isn't grading tests it just wrote.

### Step 4: Integration Review

```
MODE: review
SCOPE: All files changed across all phases
CONTEXT: Reviewing the complete [feature name] implementation
CONSTRAINT: Do NOT fix anything. Only report issues.
DONE WHEN: REVIEW.md written: acceptance rulings, findings by severity, evidence, risk.

Use @.ai-dev-exoskeleton/agents/reviewer.md
```

### Step 5: Fix Review Findings

```
MODE: implement
SCOPE: Files with findings from REVIEW.md
CONTEXT: Fixing issues found in review.
CONSTRAINT: Fix everything you can resolve on your own — anything where the right
  action is self-evident from the finding. Do NOT decide anything that needs my
  judgement: if a finding involves a design trade-off, an ambiguous requirement, or
  a change beyond the reported issue, leave it and list it for me instead. Do not
  refactor beyond what the findings call for.
DONE WHEN: Every self-evident finding is fixed and tests pass, plus a short list of
  the findings you deliberately left for my decision, each with what you'd recommend.
```

Then decide the ones it left you. `review-walkthrough` is useful here if you want to go
through them one at a time (see `.ai-dev-exoskeleton/commands/review-walkthrough.md`).

### Finally: Test It Yourself

Once the review fixes land, **you** exercise the feature — click it, call it, run it. Not
the agent, and not the test suite alone. A green suite means the code does what the tests
say; only you can tell whether it does what you actually wanted.

Walk `PLAN.md`'s `## Acceptance`, starting from the reviewer's met / not met / partial
rulings — a ruling says where to look first, not that you can skip looking. Then the diff:
low risk with a filled `### Evidence` means the reviewed diff need not be read; anything
else, read it. Step 5's own changes came after the review — read those either way.

This is the last human gate, and it's where the whole loop closes. Anything it turns up
goes back through debug → fix, not into a "we'll catch it later" pile.

---

## Key Principles
- **Plan before you implement.** Not necessarily in a separate session — but always as a
  separate, finished step, with the plan written down before code starts.
- **Good context makes the later prompts short.** If you have to write an elaborate prompt
  to get a decent plan, that's a sign the context step was rushed.
- **Parallelise only what shares no files and has no dependency.** Subagents if your harness
  has them, separate worktrees if it doesn't.
- **Two gates need you; four decisions come to you.** Be genuinely present during Step 0
  (context) — the highest-leverage step in the workflow — and test the result yourself at the
  end. Between them, the plan, a root-cause analysis, the review findings left for you and a
  new test seam (which proceeds unless you stop it) each come back as a one-line decision.
