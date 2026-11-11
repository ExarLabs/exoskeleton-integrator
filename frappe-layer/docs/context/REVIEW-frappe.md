# Reviewing Frappe changes

Extra questions the Exoskeleton reviewer (`.ai-dev-exoskeleton/agents/reviewer.md`) asks on a
Frappe codebase. The reviewer's own format (Acceptance, Evidence, Risk; CRITICAL, WARNING,
NOTE) stays as it is; this list only says where to look. Most consequential first.

## 1. Silent data damage

- Can the change write wrong money, stock or status without raising? That is worse than a crash.
- `frappe.db.commit()` or `rollback()` inside a request or a hook: almost always wrong.
- `frappe.db.set_value` / `db_set` skip validation and hooks. Is skipping them intended and
  written down?
- A destructive call whose filter can be empty or `None` (`frappe.db.delete`, `set_value`
  with a name that may be missing) hits more rows than intended.

## 2. Access

- Every whitelisted method checks permission before it reads or writes, and takes identity from
  `frappe.session.user`, never from an argument.
- `allow_guest=True` only with a written reason.
- No SQL built by string formatting from user input; use `frappe.qb` or parameters.
- A JSON argument can arrive as a dict or list where a string is expected
  (`{"name": ["!=", ""]}` matches everything). Check types at the boundary.
- Permission changes: gotcha 1 (Custom DocPerm) and gotcha 8 (falsy query condition).

## 3. Server Scripts and site customizations

- Every `frappe.*` call exists in `SAFE_EXEC-frappe.md` for the target version (gotcha 2).
- No top-level helper functions calling each other (gotcha 3); no commit in DocType Events
  (gotcha 4); no `doc.save()` inside a save event (gotcha 6).
- Which other event scripts run on the same DocType, and in what order?

## 4. Schema and migration

- DocType JSON changed: is `bench migrate` part of the plan and of the rollback?
- Renamed or removed fields: a patch moves the data, and it is safe to run twice.
- Custom Fields: shipped as fixtures or created in `after_migrate`, one way per project, as
  `docs/context/PATTERNS.md` says.

## 5. Performance

- No database call inside a loop over records; fetch once.
- A new filter or sort on a large table has an index.
- Long work goes to a background job (`frappe.enqueue`), not into the request.

## Evidence this list expects

For a finding about access or data, the Evidence section names the command or test that
showed it (a `run-tests` line, a REST call as a restricted user, a triage output), not only the
diff line.
