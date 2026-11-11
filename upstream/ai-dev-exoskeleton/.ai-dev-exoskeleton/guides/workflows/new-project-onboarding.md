# Workflow: New Project Onboarding

> How to set up your agentic engineering system when you join a new project.
> Goal: Go from zero to productive in 20-90 minutes (legacy stacks take longer).

## What You Bring (no changes needed)

Your `.ai-dev-exoskeleton/agents/*.md` files are universal — they work on any project, any language, any stack.
Your `.ai-dev-exoskeleton/guides/workflows/*.md` and `.ai-dev-exoskeleton/guides/checklists/*.md` are also universal.

## What You Rebuild (project-specific)

- `docs/context/` — structured architecture, patterns, and gotchas for this codebase.
  **This is the entire per-project fill-in** — everything the agents need to know
  about THIS project lives here, and the universal agents read it by pointer.
- `AGENTS.md` (and the `CLAUDE.md` / `GEMINI.md` pointers) — the repo entry file
- `docs/tasks/` — task folders for plans, notes, and work artifacts

---

## Session 1: Set Up the Exoskeleton
```
From the ai-dev-exoskeleton repository, copy into the root of your project repository:
  1. the .ai-dev-exoskeleton/ folder (the universal system)
  2. AGENTS.md (describes the system and the prompt scaffold — generic, nothing repo-specific)
  3. CLAUDE.md and/or GEMINI.md if you use those harnesses (thin pointers to AGENTS.md)

Do NOT copy docs/ — that is the exoskeleton repo's own project knowledge. Session 2
writes yours, and extends AGENTS.md with this project's specifics.
```

## Session 2: Explore & Generate Project Context (5-30 min)

```
MODE: explore
SCOPE: the entire repo root
CONTEXT: I'm new to this project. I don't know the codebase.
  Explore the codebase, then produce structured documentation.
CONSTRAINT: Do NOT change any source code. Only read, report, and create
  the output files below.
DONE WHEN: The following files are created:

  1. docs/context/ARCHITECTURE.md — high-level architecture map containing:
     - Directory structure and what each top-level dir does
     - Architecture pattern (monolith, microservices, hexagonal, MVC, etc.)
     - Module boundaries and dependency flow between layers
     - Entry points (main files, API routes, CLI commands)
     - Service boundaries and communication methods
     - Deploy process (CI/CD, environments)
     - ASCII diagram of the architecture if useful
     - A last `## Exposure` section: what the platform publishes by default, whether or
       not this code calls it. One line per surface: `[surface] — protected | unprotected | unknown — [evidence]`;
       `none — [why]` is a complete answer. Work the questions in "What the platform
       exposes by default" below before writing it

  2. docs/context/PATTERNS.md — coding conventions and patterns:
     - Code style conventions (tabs/spaces, formatting, linting)
     - Naming conventions (files, classes, functions, variables)
     - Import/module patterns
     - How services/components are structured
     - Exception/error handling patterns
     - DTO/data transfer patterns
     - Test patterns and test framework usage

  3. docs/context/DATA_MODEL.md — data layer documentation:
     - Key entities and their relationships
     - Database/schema overview
     - ORM/data access patterns used
     - Migration approach (if applicable)
     - Data flow across service boundaries

  4. docs/context/API_SURFACE.md — interface documentation:
     - REST/GraphQL/gRPC endpoints and their purpose
     - CLI commands (if applicable)
     - Request/response patterns
     - Authentication/authorization approach
     - External API integrations

  5. docs/context/DEPENDENCIES.md — dependency and config documentation:
     - Tech stack (languages, frameworks, databases, infra) with versions
     - Key external dependencies and what they're used for
     - Key config files and their purpose
     - Environment variables
     - How to run the app locally (dev commands)
     - How to run tests (test commands, test framework)

  6. docs/context/README.md — the index every agent starts from. One table row per
     context file: what it holds, and when to read it. Every agent is instructed to
     read this index first, so it MUST exist. Leave the **Default rigor** line as a
     placeholder — the human fills it. Template:

     ```markdown
     # Project Context — Index

     Project-specific knowledge for this codebase. The agents in
     `.ai-dev-exoskeleton/` are universal; everything specific to THIS project is here.

     | File | Holds | Read it when |
     |------|-------|--------------|
     | `ARCHITECTURE.md` | [one line] | planning, reviewing, cross-service debugging, a phase creates a new place data lives |
     | `PATTERNS.md` | [one line] | implementing, reviewing |
     | `DATA_MODEL.md` | [one line] | planning, data-layer work |
     | `API_SURFACE.md` | [one line] | API work, integration debugging |
     | `DEPENDENCIES.md` | [one line] | onboarding, debugging, setup |

     **Default rigor:** light | heavy — [why, for this project as a whole]

     On a small repo, reading all of these is cheap — do that. On a large repo, scope
     down to what the task needs. Every claim cites a source (`file:line`).

     Keep these current, not cumulative. Before adding a claim, find the claim it replaces or
     contradicts and update that one — a file that only ever grows stops being read, by you and
     by the agent. Describe what is true now, never what used to be true. History lives in git.
     If a file passes ~200 lines, split it by domain
     (`PATTERNS-api.md`, `PATTERNS-frontend.md`) and update this index.
     ```

  7. AGENTS.md — EXTEND the AGENTS.md already in the repo root (copied in Session 1).
     Keep everything that's there — it describes the system and the prompt scaffold, and is
     the single source of truth for that. Retitle the top line to `# Project: [Name]`
     and APPEND the project-specific sections below:

     ```markdown
     ## Quick Overview
     [2-3 sentences about what the project does]

     ## Tech Stack
     - [Language] [version], [Framework] [version]
     - [Database], [ORM/data layer]
     - [Other key technologies]

     ## Build & Run
     [commands to build and run the project locally]

     ## Test Commands
     # Unit tests
     [command]

     # Integration tests (prerequisites: [list any needed services])
     [command]

     # Single test file
     [command]

     ## Project Structure
     See docs/context/ARCHITECTURE.md for detailed architecture.

     ## Coding Conventions
     See docs/context/PATTERNS.md for patterns and conventions.

     ## Key Files
     - [path] — [brief description]
     - [path] — [brief description]

     ## Environment Variables
     - [VAR_NAME] — [purpose]

     ## Important Context
     - docs/context/ARCHITECTURE.md
     - docs/context/PATTERNS.md
     - docs/context/DATA_MODEL.md
     - docs/context/API_SURFACE.md
     - docs/context/DEPENDENCIES.md

     ## Common Gotchas
     - [gotcha discovered during explore]

     ## Rules
     - Always follow existing patterns — check similar code before creating new
     - [project-specific rules]
     ```

Use @.ai-dev-exoskeleton/agents/explorer.md
```

`AGENTS.md` is the canonical entry file. Add thin `CLAUDE.md` and `GEMINI.md` pointers
(each just says "read @AGENTS.md") so Claude Code and Gemini CLI auto-discover it from a
single source of truth.

Then fill the index's **Default rigor** line yourself. It is the answer `build-context`
offers on every task, so decide it once, for the typical change here (PLAYBOOK,
`## Light or heavy`).

Then read the `## Exposure` list and correct what is wrong about this project: the
platform's defaults are the agent's half, a decommissioned bucket or a surface that was
never built is yours. Walk any click path the agent wrote. Nothing waits on this.

### What the platform exposes by default

Answer these from the repository, for the developer — never ask them what their platform
exposes; that is the knowledge they lack. Then write `## Exposure`.

```
1. For every place data lives or a request arrives — table, collection, bucket, queue,
   topic, cache, search index, endpoint, function, file share, webhook receiver, admin
   console — does the platform publish an interface to it that nobody in this repo wrote, or
   did you write one and leave it unguarded because nobody outside was expected to find it?
2. Which credentials ship inside something a user holds: a web bundle, a mobile binary, a
   desktop app, a CLI, a published image, public config? Assume each one is readable. What
   can its holder reach?
3. For each surface, what denies an unauthorized caller, and which file here says so?
4. With nothing configured, is that surface's default deny or allow?
5. Does a server-side admin or service credential hide the question?
   **"We don't call that API" is not "that API isn't exposed."**

Anything questions 1-4 cannot settle from a file in this repo is `unknown` and gets a
click path.
```

`## Exposure` is the last section of `docs/context/ARCHITECTURE.md`. It records what the
platform and infrastructure publish by default, whether or not this code calls it, one
line per surface the platform serves **separately**: if it serves per table, collection or
bucket, that is one line each — a single line for the API hides the case this section
exists for:

```
[surface name] — protected | unprotected | unknown — [evidence]
```

- `protected` requires a `file:line` in this repo that enforces **this surface's own access path**
  — a policy or rules file, a migration that grants or revokes, an IaC resource, a
  firewall rule — and it must be **in force for that surface**: a rule that exists but is
  not enabled, attached or applied is `unknown`, not `protected`. Guarding another path is not evidence: app- or route-level auth does not
  protect a surface the platform serves directly, and a server-side admin or service
  credential is never evidence, because it hides the question. No citation means `unknown`,
  never `protected`.
- `unprotected`: the surface is served, this repo holds no guard for its own access path,
  and the platform's default for it is allow. The evidence is the absence — say what you
  looked for and where. It is a defect to close, not a state to live with: open a task for it.
- `unknown`: the answer lives in a console or setting you cannot read from the repo. It
  carries its click path and means "go look". A recorded `unknown` is a success — the gap
  is written down instead of assumed away.
- When the repo shows no guard and you did not have to look outside it to know that, the
  honest status is `unprotected`, not `unknown`: `unknown` is for what you cannot see, not
  for what you would rather not call a defect.

| Concept | The word | Avoid |
|---|---|---|
| One thing the platform serves | **surface** | endpoint, resource, asset, boundary, perimeter |
| Its state | `protected` · `unprotected` · `unknown` | open/closed, secure/insecure, public/private, safe/unsafe — and never `exposed` as a status: every surface in the list is exposed, that is why it is listed |

What only a console can answer gets a **click path** — five minutes, no expertise, no staging
environment, and never a probe against production:

```
unknown — open [the provider console] → [the screen] → [the setting]; protected looks like
[what you should see]. Write the answer back on this line, dated YYYY-MM-DD.
```

A repo that publishes nothing is the fast path — the whole section is one line:

```
## Exposure

none — [what was checked, and why nothing is published]
```

This file is committed. Surface names and statuses only. Never a key, an id, a URL, a payload or a row of data.

Scope: what the platform serves without being asked — not secrets, not dependency CVEs, not a threat model.

**Optional, where a local emulator exists.** A probe that tries each surface as an
unauthenticated caller belongs to this project: write it in the project's own language,
inside its own tree, never in `.ai-dev-exoskeleton/`. It runs against the emulator, never
against staging and never against production. Record it under `## Quality gates` in
`docs/context/DEPENDENCIES.md`, after which the implementer and reviewer gate steps run it
and nothing else changes:

```
exposure — [command] — 0 unprotected surfaces
```

## Session 3: Establish Feedback Loop (5-30 min)

The agent can only verify its own work if it can run tests, and can only skip a numeric
checklist if a tool checks the same thing. This session finds both before you start real
tasks.

```
MODE: explore
SCOPE: the entire repo root
CONTEXT: I need to verify that all test suites run from the command line.
  Try running unit tests, integration tests, and any other test suites
  you can find. Document what works and what doesn't.
CONSTRAINT: Do NOT change any source code. Only run tests, diagnose
  blockers, and update documentation.
DONE WHEN: The following are confirmed and documented in AGENTS.md:

  1. Unit tests — working CLI command that runs unit tests
  2. Integration tests — working CLI command (if they exist), plus any
     prerequisites (Docker containers, env vars, test databases, etc.)
  3. E2E tests — working CLI command (if they exist)
  4. Any blockers — tests that fail, missing dependencies, environment
     issues that need manual setup

  5. Quality gates — lint, complexity, coverage, dependency-rule and mutation
     tooling: what the project already runs, what would install in under an
     hour (name it, don't install it), and what is unavailable for this stack.
     Record the gates that run today in docs/context/DEPENDENCIES.md under
     ## Quality gates, one line each: [kind] — [command] — [threshold].
     If none run: none available — [why]. Record the under-an-hour ones as
     candidates: [tool] — [what it would check], so the list survives today.

  If any test suite cannot run without manual intervention, document
  what's needed so we can fix it.

Use @.ai-dev-exoskeleton/agents/explorer.md
```

"None available" is a valid outcome, not a blocker: the agents fall back to
`.ai-dev-exoskeleton/references/code-quality.md` and the method continues in prose mode.

### If tests don't run cleanly
Fix environment issues in a follow-up implementation session before proceeding:

```
MODE: implement
SCOPE: test configuration, docker-compose, CI config
CONTEXT: Test suite doesn't run cleanly. Fix the blockers identified
  in the previous session.
CONSTRAINT: Only fix test infrastructure — do not change application code.
DONE WHEN: Test commands documented in AGENTS.md run successfully.
```

### Optional: E2E verification for UI projects
If the project has a frontend, consider setting up E2E verification. Choose
the technique that fits your stack:

- **Playwright** — browser automation, good for complex UI flows
- **Chrome MCP / browser tools** — lightweight, good for visual verification
- **API-level testing** — if the UI is thin, test the API directly
- **Screenshot comparison** — for visual regression testing

Document the chosen approach and commands in AGENTS.md.

### Optional: Dependency rules for heavy projects with several modules
Skip this on single-module code, or where heavy tasks are rare — there it is ceremony.
Where it pays, a reviewer reading for layer violations is guessing; a checker isn't, and a
violation it reports gets resolved rather than commented on.

```
MODE: implement
SCOPE: docs/context/ARCHITECTURE.md, docs/context/DEPENDENCIES.md, the checker's
  path in the project tree
CONTEXT: Make this project's module dependency direction checkable.
CONSTRAINT: Do NOT change application code. Write the checker in the project's
  own language, inside the project's tree — never in .ai-dev-exoskeleton/.
DONE WHEN:
  1. ARCHITECTURE.md has a ## Dependency rules section: which module may
     depend on which
  2. One command runs the checker and reports violations against those rules
  3. DEPENDENCIES.md records it under ## Quality gates:
     dependency rules — [command] — 0 violations
```

## Session 4: Conventions, Gotchas & Overrides (5-30 min)

Session 2 produced `docs/context/`. This session sharpens `PATTERNS.md` — the file the
agents lean on most during real work — because conventions and known gotchas are what keep
the agent inside the project's grain. It also proposes overrides where a method rule can't
hold here.

```
MODE: explore
SCOPE: docs/context/PATTERNS.md, docs/context/overrides/
CONTEXT: Sharpen this project's conventions and known gotchas so the universal agents
  behave correctly here. Use the codebase and docs/context/ as source material.
CONSTRAINT: Do NOT modify .ai-dev-exoskeleton/ files — those are universal.
  Only edit docs/context/ files.
DONE WHEN:
  PATTERNS.md contains:
  1. Code style + import/naming conventions specific to this project
  2. Test patterns and how the test suite is structured
  3. Stack-specific gotchas (framework quirks, API surprises, common error patterns)
  4. At least one concrete example from this codebase per convention

  Where a rule in .ai-dev-exoskeleton/ cannot hold on this project, write
  docs/context/overrides/PROPOSED-<file name> — at most three. Each states the
  rule it overrides (file:line), the fact that contradicts it (file:line), and
  what applies instead. A differing threshold or convention is not an override;
  it belongs in PATTERNS.md. Writing none is a valid outcome.

  The session summary lists every proposal with a one-line reason.
```

Add gotchas as you hit them: symptom → cause → the rule, with a `file:line` reference.
Every bug that costs more than one round is worth a line here.

Proposals are inert: agents read `docs/context/overrides/<file name>`, never `PROPOSED-*`.
A wrong override silently disables a rule, so activation is a deliberate rename (drop the
prefix); delete the ones that are wrong. Nothing waits on this — decide whenever you read the
summary. See PLAYBOOK, `## Adapting a rule without forking`.

## Session 5 (Optional): First Real Task as Validation

Onboarding is done — from here on it's ordinary development. Pick a small, low-risk
task and run it through a real workflow rather than a one-off prompt. The point is to
exercise the setup end to end while the stakes are low, so pick whichever workflow
matches the work in front of you:

| The work is… | Use | Path |
|---|---|---|
| A new feature or a change to an existing one | Feature workflow | `.ai-dev-exoskeleton/guides/workflows/feature.md` |
| A bug, an error, or something behaving wrongly | Debug workflow | `.ai-dev-exoskeleton/guides/workflows/debug.md` |
| Moving, renaming, or restructuring existing code | Refactor workflow | `.ai-dev-exoskeleton/guides/workflows/refactor.md` |

Keep the first one small: one feature phase, one bug, or one contained refactor. You are
validating the context you just built, not shipping the roadmap.

If none of the three fits, fall back to a single scoped session using the pre-session
checklist (`.ai-dev-exoskeleton/guides/checklists/pre-session.md`) — it holds copy-paste
session openers for plan, implement, and debug.

After this session, do a post-session review (.ai-dev-exoskeleton/guides/checklists/post-session.md):
- Did AGENTS.md provide enough context?
- Did the docs/context/ files give the agent enough architectural understanding?
- Did PATTERNS.md catch the project-specific gotchas you hit?
- What's missing? Update AGENTS.md and docs/context/ accordingly.

---

## Checklist Summary

- [ ] Session 1: Copy .ai-dev-exoskeleton/ into your project repo
- [ ] Session 2: Explore + docs/context/ (incl. its README.md index) + AGENTS.md — structured documentation created
- [ ] Session 2: CLAUDE.md / GEMINI.md pointers to AGENTS.md — added
- [ ] Session 2: Default rigor line in the index — filled in by you
- [ ] Session 2: `## Exposure` recorded in ARCHITECTURE.md — `none` and a standing `unknown` are both valid
- [ ] Session 3: Feedback loop — test commands verified and documented in AGENTS.md;
      quality gates recorded in DEPENDENCIES.md (or "none available")
- [ ] Optional (heavy, several modules): dependency rules + checker, recorded as a gate
- [ ] Optional (local emulator exists): exposure probe, recorded as a gate
- [ ] Session 4: Conventions, gotchas & overrides — PATTERNS.md sharpened, at most three
      PROPOSED- overrides listed (rename one to activate it)
- [ ] Session 5: Validation — first real task completed successfully
- [ ] Post-session review — gaps identified and filled

## Time Estimate

| Session | Duration | Output |
|---------|----------|--------|
| Set up exoskeleton | 5 min | .ai-dev-exoskeleton/ folder in your project repo |
| Explore + docs/context/ + AGENTS.md | 5-30 min | 5 context docs (exposure recorded in ARCHITECTURE.md) + index + project entry file |
| Feedback loop | 5-30 min (legacy: more) | Verified test commands in AGENTS.md; quality gates in DEPENDENCIES.md |
| Dependency rules (optional, heavy + several modules) | not counted | Dependency rules + checker, recorded as a gate |
| Conventions, gotchas & overrides | 5-30 min | Sharpened PATTERNS.md, ≤3 PROPOSED- overrides |
| Validation (optional) | 15-20 min | First completed task |
| **Total** | **~20-90 min** — a small repo lands at the low end | **Ready to ship** |

## Tips for Large Legacy Codebases

- Don't try to understand everything in Session 2. Focus on the area you'll work in first.
- If the repo is huge (>1000 files), scope the explore session to one module/service at a time. Create docs/context/ files for each module incrementally rather than trying to document everything at once.
- Ask the team for their "if you could only read 5 files, which ones?" — add those to AGENTS.md Key Files.
- Legacy projects often have undocumented conventions. As you discover them, add to docs/context/PATTERNS.md immediately.
- If there are no tests, your first real task should be adding test infrastructure — agentic engineering without tests is flying blind.
- Start with ARCHITECTURE.md and DEPENDENCIES.md — they give the most immediate value.
