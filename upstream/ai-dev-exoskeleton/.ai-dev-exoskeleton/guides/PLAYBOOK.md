# Agentic Engineering Playbook

> Universal principles for AI-assisted development. Works with Claude Code, OpenCode, KiloCode, Codex, Gemini CLI.
> Based on analysis of hundreds of sessions.

## The Mental Model

Everything below follows from one picture:

> **The AI is a brilliant but amnesiac intern.** It codes faster than you do. It knows
> nothing about your project. It forgets everything between conversations. And when it
> doesn't know something, it is prone to make something up rather than tell you it doesn't
> know.

**You are the senior architect now; it is the junior who writes the code.** The decisions,
the direction, and the responsibility are yours. Your job is no longer typing.

**Context is holy.** Bad context, bad code — however smart the model is. Output quality is
directly proportional to what you hand it.

### Your four jobs

Each one answers a specific property of that intern:

| Job | Because |
|-----|---------|
| **Give it context** | it doesn't know your project |
| **Narrow the task** | otherwise it wanders |
| **Verify its work** | it is confidently wrong |
| **Keep its memory fresh** | it forgets — new task, new conversation |

Every Law below is one of these four, made concrete.

---

## The 5 Laws of Agentic Engineering

### Law 1: Size the Session to the Context Window
A session should produce testable, deployable results — and how much fits in one depends on
how much context you actually have.

- **On a ~200k context window, aim for one atomic outcome per session.** One phase, one
  testable result. Packing several phases in is what breaks it.
- **On a ~1M context window you can carry several phases in one session** — the constraint
  loosens with the window.

**Bad (on 200k):** "Migrate the entire profile service across 4 phases"
**Good (on 200k):** "Implement only the first phase of the migration plan file."

**What actually limits you is context rot, not the phase count.** As a window fills, quality
degrades before it runs out — in my experience it becomes noticeable somewhere around
60–70% utilisation: the agent starts losing earlier decisions, re-reading files it already
read, and drifting from constraints stated at the top. Watch for those symptoms rather than
the token counter. When they appear, end the session and start a fresh one from the plan
and the task folder — that is exactly what those artifacts are for.

**So the question at a session boundary is not "how full is the window?" but "is the
artifact layer current enough that ending here costs nothing?"** If the phase checkboxes are
ticked and `CONTEXT.md` still describes the work, ending the session is routine hygiene, not
a loss to put off.

### Law 2: Always Give a Stop Condition — and Say What NOT to Do
Two things belong in every prompt, and the second one is the underrated half:

- **DONE WHEN** — a clear, checkable stop condition. Without one the agent decides for
  itself when it's finished, and it will usually decide too late.
- **CONSTRAINT** — the things it must *not* do. This is where most of the leverage is.

**Telling the agent what to avoid often does more than a stop condition ever will.** A
weak "DONE WHEN: the feature works" leaves the whole solution space open — the agent can
refactor three unrelated files, invent an abstraction, and swap your test framework, and
still claim it met the condition. `CONSTRAINT: don't touch anything outside
app/services/, don't refactor existing code, no new dependencies` closes off the expensive
failure modes directly. A stop condition tells it when to stop; a constraint keeps it out
of the ditch on the way there.

Good constraints are specific and negative: *don't change the API surface* · *no code yet,
analysis only* · *don't add error handling for cases we haven't seen* · *don't rename
anything* · *don't touch the migration files*. If a past session went wrong in a way you
can name, that name is your next constraint.

**Bad:** "Fix the Redis streaming issue"
**Good:** "MODE: debug. SCOPE: app/infrastructure/transport/. CONSTRAINT: don't change any
code, don't propose a fix until the trace is complete. DONE WHEN: root cause identified and
explained with the call chain."

Why: In my session analysis, 26 wrong-approach corrections traced back to the agent not
knowing my intent — and in most of them, one sentence about what to leave alone would have
prevented the whole detour.

### Law 3: Trace Before You Touch
For debugging, ALWAYS require a full trace before any fix. Never let the AI patch symptoms.

**Template:** "Trace the full call chain from [entry point] to [error]. State your hypothesis. Do NOT change any code until I confirm."

Why: A datetime serialization bug took me 3 rounds and a Redis issue several wrong guesses — one upfront trace would have saved all of it.

### Law 4: Tests Are the Loop Condition
The AI must run tests after every change. No behaviour ships without a test you have seen fail on it — either before the code exists, or by breaking the code on purpose and watching the test go red. A test that has never failed may be unable to.

**Prerequisite:** The feedback loop must be established before real work begins — verify that test commands actually run from the CLI during onboarding (see Session 3 in the [onboarding workflow](workflows/new-project-onboarding.md)). Without a working test command, this law can't be enforced.

**Template:** "Cover [expected behavior] with a test at the highest level this project can run — end-to-end where it exists, unit tests beneath — and see it fail on that behaviour. Implement the minimal fix. Run tests. If red, analyze why — don't guess." The level matters because unit tests pass happily while the product behaviour they were meant to guard stays broken.

Why: A test is the only thing that lets the agent know it's wrong without you telling it. Test-gated agent loops are the single biggest productivity multiplier — no test, no self-correction.

### Law 5: Parallel by Default
Independent work should run concurrently, not one thing at a time. There are **two
different kinds of parallelism** here, and they are not interchangeable:

**1. Multi-session parallelism (universal — works in every harness).**
Run 2–3 agent sessions at once, each on an independent phase, **each in its own git
worktree**. The worktree is what makes this safe: separate working directories mean two
sessions cannot corrupt each other's files, and you review each one's diff on its own.
This is the form that actually multiplies a single developer's throughput.

Discipline it requires:
- One session per phase, and only phases with **no shared files and no dependency** on each
  other (this is why every plan phase declares `Scope` and `Depends on`).
- One worktree per session; merge each one back after its tests pass.
- Name your sessions so you know which is which when you switch between them.
- Two sessions that both edit `docs/context/` meet as an ordinary git conflict, which you
  resolve. That is intended: the alternative is the second silently overwriting the first.

**2. Subagent parallelism (harness-dependent).**
Some harnesses can fan out subagents inside a single session; others can't, or do it
differently. Where available it's excellent for read-only fan-out — exploring several
services or tracing both sides of a service boundary at once.

**Template (subagent form):** "Use parallel agents: Agent 1 handles [service A], Agent 2
handles [service B]. Each reads existing code first, then implements, then runs tests
independently."

---

## The Plan Is Where Mistakes Are Free

Planning is a separate step from implementing for one reason: **you fix things on the plan
while fixing is still free** — before a single line of code exists. A wrong assumption costs
one sentence to correct in `PLAN.md`, and an afternoon to correct in a merged branch.

This is why the planner never writes code, why every phase declares its `Scope`, `Verify`
and `Rollback` up front, and why reviewing the plan against the real codebase is worth its
own session.

---

## Light or heavy

A process too heavy for a small change gets abandoned, so every task runs at one of two
rigors, decided by one question:

> **Would you have asked another human to review this change?** Yes means heavy; no means light.

It tracks blast radius, not size: three lines in a permission check are heavy, a large
internal admin screen may be light.

- **Light** is the default, and most work stays there. A one-phase plan is fine; skip the
  plan-review session.
- **Heavy** adds the plan review, an `adversarial-review`, and the gates in
  `.ai-dev-exoskeleton/references/heavy-mode.md`, which buy down future regressions — worth
  it on long-lived, shared, money- or permission-touching code, not on throwaway work.

**You pick, not the agent.** The project's default sits in the `docs/context/` index as
`**Default rigor:**`, decided once instead of re-argued while tired; `build-context` offers
it at the end and records the task's answer under `## Rigor` in `CONTEXT.md`. The agent may
argue for heavier, never for lighter.

The switch covers the feature workflow, where `build-context` asks for it. A bugfix or a
refactor has no recorded rigor: there, the blast radius of the fix itself tells you whether
to add a review pass by hand.

`REVIEW.md` ends with `### Risk`: `low | medium | high`, and why. **Low risk plus real
evidence — a filled `### Evidence` — means the reviewed diff need not be read. Anything else
means it must be.** The fix session's own diff was never reviewed or rated: read that one.

---

## Session Templates

### Before ANY Session
Answer the six questions in `checklists/pre-session.md` — above all, **what must it NOT do?**

### Prompt Scaffold (optional)
```
MODE: [plan|implement|debug|review|explore]
SCOPE: [files or directories]
CONSTRAINT: [what NOT to do]
DONE WHEN: [specific exit condition]
```

Add `CONTEXT:` (a sentence or two of what and why) in any mode, and `ERROR:` (the pasted
traceback) in debug mode.

This helps most if you tend to ramble at the AI instead of getting to the point — I used
to, and the fields forced me to decide what I actually wanted before I started typing. If
you already write tight prompts, skip it.

---

## Anti-Patterns You Must Stop

### 1. The "Fix It" Anti-Pattern
**You say:** "Fix this error" (pastes traceback)
**AI does:** Patches the symptom, breaks something else
**Instead:** "Trace this error from entry to failure. What is the root cause? Show me the call chain. No code changes."

### 2. The "Do Everything" Anti-Pattern
**You say:** "Migrate the Redis pub/sub to streams, update all handlers, and test it"
**AI does:** Gets 60% done, hits rate limit, leaves half-migrated code
**Instead:** Session 1: "Create the stream publisher adapter." Session 2: "Swap the DI wiring to use streams." Session 3: "Update handlers and run integration tests."

### 3. The "Free Text" Anti-Pattern
**You say:** "Let's work on the profile service"
**AI does:** Starts reading random files, guesses what you want
**Instead:** "MODE: implement. SCOPE: app/services/profile_service.py. Add a `get_or_create_profile` method that calls the shared-data-service. CONSTRAINT: don't touch the repository layer, don't refactor existing methods. DONE WHEN: unit test passes."

### 4. The "Let It Guess" Anti-Pattern
**You say:** Nothing about your tech stack constraints
**AI does:** Guesses wrong framework CLI flags, wrong ORM methods, wrong imports
**Instead:** Always include tech stack context or point to AGENTS.md and docs/context/ files

### 5. The Doom-Loop
**You say:** "no, that's wrong" — for the third time
**AI does:** Keeps producing variations of the same wrong answer, while every failed attempt
pollutes the context further
**Instead:** **After the third correction, stop.** The context is degrading and more rounds
will not fix it. Take over: either start a fresh session with what you learned, or solve the
problem yourself. Your own repeated corrections are the earliest and clearest signal of
context rot.

### 6. Taking Claims at Face Value
**You say:** nothing — the answer sounded confident
**AI does:** hallucinates. Invents an API that doesn't exist, a config flag that was never
added, a function signature it half-remembers
**Instead:** When it matters, **ask it to back the claim with concrete evidence** — the
actual file and line, the real documentation, the command output. "Show me where that's
defined" costs one message and catches what confidence hides.

---

## Progress Tracking

After each session, run `checklists/post-session.md` — above all, ask what you would
constrain differently next time.

---

## Adapting a rule without forking

Editing `.ai-dev-exoskeleton/` for one project loses the edit on the next upgrade. What you
learned goes in one of three places, and they are not interchangeable:

| What you learned | Where it goes |
|---|---|
| A fact about the project | `docs/context/*.md` |
| A threshold or convention that differs from the defaults | `docs/context/PATTERNS.md` |
| A rule of the method that cannot hold on this project | `docs/context/overrides/<file name>` |

Every agent and command file reads its override last, and the override wins. Keep that row
rare. Legitimate: no test suite this quarter, so the test rule gives way to what the project
can run. Illegitimate: "we prefer 120-line functions" — that is row two, and routing it here
grows a per-project fork back under a new name. Onboarding proposes at most three, as inert
`PROPOSED-` files; renaming one activates it.

Two open risks. An LLM resolves the conflict between two prose files at inference time — the
soft convention `README.md` admits models violate. And a team inside one harness already has
native settings hierarchies for this; for them the layer is dead weight.

---

## The AI Wrote It. You Commit It.

Which means **you own it.** The reviewer produces findings — CRITICAL, WARNING, NOTE — but
every decision on them is yours. Nothing here transfers responsibility for the code to the
model, and no review artifact makes a change someone else's fault.

The practical form of that rule: **if you don't understand the code, you don't get to press
enter.** Not because understanding is a virtue, but because you are the one who will be
asked why it works, and the one who will fix it at 2am when it doesn't.

Owning it includes deciding what to read. When the review rates the risk low and a filled
`### Evidence` backs it, that reviewed diff need not be read — an owner's call, and the
result is still yours. At medium or high risk, and on whatever the fix session changed after
the review, the rule above stands.

## What to Delegate, and What Never To

> **What is mechanical in us, the machine does better. What is human, it doesn't.**

- **Mechanical** — boilerplate, syntax, copying a known pattern for the fiftieth time,
  wiring, translation between formats. Hand it over without sentiment.
- **Human** — taste, judgment, decomposing a problem, deciding *what* to build and *why*,
  and communicating it to other people. These do not delegate, and the better the models
  get, the more of your value sits here.

The exoskeleton exists to move as much of the first column off your desk as possible, so
you have room for the second.
