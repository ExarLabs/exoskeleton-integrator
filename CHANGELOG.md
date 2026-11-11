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
