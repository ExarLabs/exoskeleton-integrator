# Reference: Code Quality Fallback

> Read only when `docs/context/DEPENDENCIES.md` records no lint or complexity gate. A tool returning
> an exit code beats a model estimating the same number; this list is the prose stand-in.

**Scope: only lines this change added or modified.** Pre-existing conditions in a touched
file are not yours to fix; the reviewer flags a dangerous one once, as a NOTE.

**The numbers are defaults, not laws.** They were chosen for human working memory, and nobody
has calibrated them for code that agents write and agents maintain. If
`docs/context/PATTERNS.md` states the project's values, those win. One data point, not a
default: Robert Martin's experimental calibration puts complexity at ~4 for humans and 6–8
for agents.

The suffix is the reviewer's severity; the implementer fixes the item and ignores it.

- A function longer than ~40 lines → WARNING
- A function taking more than ~5 parameters — group them or rethink the interface → WARNING
- Nesting deeper than ~2 levels (if/for/try) — extract the inner logic to a named function
  → WARNING
- Magic numbers or strings instead of named constants → WARNING
- 3+ lines duplicated from elsewhere — extract a shared, unit-tested function → WARNING
- Nested if/else chains that could be guard clauses (early return) → WARNING
- Unused imports or variables left behind → WARNING
- Inconsistent return types — one path returns a value, another implicitly returns nothing
  → WARNING
