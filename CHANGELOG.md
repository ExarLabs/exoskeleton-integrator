# Changelog

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
