# Field Notes — My Personal Setup

**This is NOT part of the method.** The AI Dev Exoskeleton is deliberately minimal and
tool-agnostic; nothing below is required to use it. These are the tools and habits I
personally run on top of it. Steal what's useful, ignore the rest.

Some of these are harness- or OS-specific (noted inline) — they break the agnosticism the
core keeps, which is exactly why they live here and not in the agents.

## Running many sessions at once

- **tmux** — I keep several agent sessions in split panes so I can see all of them at a
  glance. The exoskeleton's small, scoped sessions are what make this manageable.
- **Name every session** (`/rename` in Claude Code — harness-specific). When I context-switch
  between folders, the name reminds me instantly what that session is doing.
- **Pipelining** — while one agent implements a phase, I start building context for the
  next task in another session. The plan's phase boundaries make this safe: independent
  phases don't collide.

## Worktrees & diff review

- **Agent of Empires (AoE)** — I run agents in git worktrees so parallel sessions don't
  step on each other, and I can see which session is where and review each one's diff
  separately.

## Notifications

- **peon-ping** (Claude Code plugin — not agnostic) — plays a sound when something in a
  session needs me. Useful when I'm watching several at once and don't want to babysit.

## UI work

- **Impeccable** — I sketch a wireframe in plain HTML first, then have the implementer
  build against it. A concrete visual target beats describing the layout in prose.
