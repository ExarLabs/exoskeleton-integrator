# Working in this repo

This project uses the **AI Dev Exoskeleton**: a minimal, project- and
LLM-agnostic set of plain-markdown agents, commands, and guides that live in
`.ai-dev-exoskeleton/`. No runtime, no dependencies — the files are text a
coding agent reads, and they happen to contain behavioral instructions.

This is disciplined **agentic engineering**: constraint-driven, evidence-based. Two points
where your presence is mandatory — the work stops without you: **building the context** at
the start, and **manually testing** the result at the end. Between them, an agent brings you
four decisions you can hand back in a line: **the plan**, before implementation starts;
**a root-cause analysis**, before any debugging fix is applied; **the review findings**
the fix session left you; and **a new test seam**, when the implementer declares one — it
proceeds without waiting; a line from you stops it.

Every constraint here is a convention the agent is asked to follow, not a hard-enforced
sandbox — the human stays responsible for holding the line.

## Prompt scaffold (optional)

Use it when a session keeps drifting; skip it if you already write tight prompts.

```
MODE:       plan | implement | review | debug | explore
SCOPE:      which files/dirs are in play (everything else is off-limits)
CONSTRAINT: what NOT to do (don't refactor, don't touch the API, no code yet)
DONE WHEN:  the specific exit condition
```

See the Laws in `.ai-dev-exoskeleton/guides/PLAYBOOK.md`.

## Where things are

- **Agents (roles)** — `.ai-dev-exoskeleton/agents/` — universal role + process
  definitions: `planner` · `implementer` · `reviewer` · `explorer` · `debugger`.
  Invoke by asking the agent to read one, e.g. `read .ai-dev-exoskeleton/agents/planner.md`.
  These are plain markdown, not harness-native subagent configs. Never edit them
  per project. (In Claude Code and Gemini CLI, `@path` auto-expands the file;
  in other harnesses just ask the agent to open the path.)
- **Commands** — `.ai-dev-exoskeleton/commands/` — reusable prompts:
  `build-context`, `start-debug`, `review-walkthrough`, `adversarial-review`.
  These are markdown you paste or reference; they are not native slash-commands
  unless you install them into your harness's command directory.
- **References** — `.ai-dev-exoskeleton/references/` — opened by an agent only when a
  condition matches: no lint or complexity gate recorded → `code-quality.md`; heavy task →
  `heavy-mode.md`. Nobody reads them day to day.
- **Guides (for the human)** — `.ai-dev-exoskeleton/guides/` — PLAYBOOK, workflows,
  checklists, and `field-notes.md` (a personal tool setup, not part of the method).
- **Version** — `.ai-dev-exoskeleton/VERSION`, the release this copy came from.
- **Project knowledge** — `docs/context/` — architecture, patterns, and traps for
  THIS codebase, generated during onboarding. Start at the index `docs/context/README.md`;
  on large repos, scope down to what the mode needs. A method rule that can't hold here is
  adapted in `docs/context/overrides/` (PLAYBOOK, "Adapting a rule without forking").
- **Task work** — `docs/tasks/[yyyymmdd-task-name]/` — CONTEXT.md, PLAN.md, REVIEW.md
  per feature. This is the session-recovery record.

**Commit `docs/tasks/` or ignore it?** Either works; decide once, per repo. Committing
gives the team a durable record of why each change was made and lets any session resume
after a crash — at the cost of folders accumulating over time (prune old ones
periodically). Ignoring it keeps history clean but the recovery record is local to whoever
ran the session. Teams doing review-heavy work usually commit it.

## Safety and permissions

The agent will read your whole codebase and, in implement/debug modes, run your test suite.
Some ground rules worth setting before you start:

- **Use your harness's permission controls.** Approve shell commands rather than granting
  blanket execution, at least until you trust a workflow. This system assumes a human is
  watching; it does not sandbox anything itself.
- **Keep secrets out of `docs/context/`.** Onboarding documents environment variable
  *names* and config file *purposes* — never their values. These docs get committed.

## How work flows

`build-context` (align on the feature) → `planner` (PLAN.md) → `implementer`
(per phase, tested) → `reviewer` (REVIEW.md) → fix cycle → you test it yourself.

New to this repo? Run onboarding first — see
`.ai-dev-exoskeleton/guides/workflows/new-project-onboarding.md`.
