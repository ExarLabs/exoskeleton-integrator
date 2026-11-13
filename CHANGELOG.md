# Changelog

## Unreleased (0.2.0)

Lessons from a real Frappe v16 + Frappe CRM build (plan: `docs/tasks/20261111-frappe-layer-v0.2/`).

- `GOTCHAS-frappe.md` trap 10: a child table list needs `parent=<Parent DocType>`, over
  `/api/resource` as well as `frappe.client.get_list`; source lines at both pinned commits,
  behaviour checked on a live v16.26.3 site.
- New `GOTCHAS-frappe-crm.md`: four Frappe CRM traps pinned to `frappe/crm` v1.77.3
  (`ead04d4`).
- `tests/test_docs_pins.py`: every `github.com/frappe` link in the layer points to a full
  commit, and every context file is listed in `FRAPPE.md`.
- Learned from Frappe's own `deep-app-audit` (`frappe/skills` `5dc2f98`, cited, not copied):
  - every trap gains a **Find it.** line, and a test keeps it so;
  - traps 11 (DocType Event scripts skip install and migrate) and 12 (an API script can take
    over a method path), source lines at both pinned commits;
  - `REVIEW-frappe.md`: find every writer, one owner per status, Custom Fields in code rather
    than fixtures (audit rules A08, A09, A18, B25);
  - `FRAPPE.md`: "Two checks", our triage on every change and Frappe's audit before a big
    release.
- Learned from Frappe's `ship-it` and `fix-issue` (same commit, cited, not copied):
  - `FRAPPE.md`: intent in at most five numbered lines with a **Must not:** line, confirmed by
    the owner; bug reports go through a fact-only extract and a reproduction first;
  - `TESTING-frappe.md`: the agent's live run with evidence per intent line before the human's
    manual test; work in the bench's own checkout, not a worktree;
  - `REVIEW-frappe.md`: a `Reviewed: <sha>` line, and commits after it get a fresh review.
- `scripts/watch_sources.py` and `watch/sources.json`: a read-only weekly check of what this
  package learns from. For every file the layer cites at a pinned commit, has its branch changed
  that file since? Plus new commits, releases, licence changes and archived repositories in the
  watched sources. Tests with a fake GitHub; a test keeps every pinned commit mapped to a branch.
- `scripts/discover_sources.py`: finds new sources for that list. GitHub code search for agent
  files mentioning Frappe, mirrors filtered out, ranked without stars: Frappe specificity,
  whether the repository is a Frappe app, months active in the last six, commits and authors in
  the last 90 days. First run (2026-11-12): about 1,500 repositories found, about 470 of them
  Frappe-specific; the top of the list is Frappe's own apps and small, active client apps.

## 0.1.0 (2026-11-11)

First version.

- AI Dev Exoskeleton 0.3.0 install payload, unchanged (upstream commit `77d90b4`).
- Frappe layer for `docs/context/`: `FRAPPE.md`, `GOTCHAS-frappe.md` (nine traps with source
  lines at pinned v15 and v16 commits), `SAFE_EXEC-frappe.md` (generated), `TESTING-frappe.md`,
  `REVIEW-frappe.md`, `overrides/PROPOSED-implementer.md`.
- Scripts: `safe_exec_names.py`, `triage_console.py`, `triage_rest.py`.
- Claude Code plugin with three hooks: session context, migrate reminder, Bash guard.
- `install.sh` that never overwrites existing files.
- Tests for the generator, the hooks and the REST triage.
