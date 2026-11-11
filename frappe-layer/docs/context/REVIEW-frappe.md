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
- Who else writes the data this change touches: other DocTypes' scripts, jobs, REST callers,
  inbound mail? Find every writer before making a field mandatory or changing who sets a
  status (Frappe audit A18 and B25, links below). A status has one owner.
- A patch that saves documents skips their DocType Event scripts (gotcha 11); an API script
  can take over a method path (gotcha 12).

## 4. Schema and migration

- DocType JSON changed: is `bench migrate` part of the plan and of the rollback?
- Renamed or removed fields: a patch moves the data, and it is safe to run twice.
- Custom Fields the app's code reads are created in code (`create_custom_fields` from
  `after_install` and `after_migrate`), not shipped as fixtures: a fixture carries no owner
  mark and overwrites the site's copy on every migrate (Frappe audit A08 and A09). A project
  that already uses fixtures says so in `docs/context/PATTERNS.md` and moves on its next change.

## 5. Performance

- No database call inside a loop over records; fetch once.
- A new filter or sort on a large table has an index.
- Long work goes to a background job (`frappe.enqueue`), not into the request.

## Evidence this list expects

For a finding about access or data, the Evidence section names the command or test that
showed it (a `run-tests` line, a REST call as a restricted user, a triage output), not only the
diff line.

## Commits after the review

Start `REVIEW.md` with the commit the review covered (`Reviewed: <sha>`). Fixes, test changes
and docs that land after it are reviewed again, `<sha>..HEAD` only, by a fresh reviewer, and the
line moves. A resumed session reads that line to know what is still unreviewed. The fixer is
never the reviewer who raised the finding. (Frappe's `ship-it` keeps the same marker in the PR.)

## Frappe's own audit rules cited here

Frappe publishes a full app audit in [`frappe/skills`](https://github.com/frappe/skills/tree/5dc2f984081f6d8e23559af03b0e7c2799245d79/skills/deep-app-audit)
(no licence file: read it there, do not copy it):
[A08](https://github.com/frappe/skills/blob/5dc2f984081f6d8e23559af03b0e7c2799245d79/skills/deep-app-audit/quality/A-customization/A08-custom-fields-in-code.md) custom fields in code,
[A09](https://github.com/frappe/skills/blob/5dc2f984081f6d8e23559af03b0e7c2799245d79/skills/deep-app-audit/quality/A-customization/A09-fixtures-overwrite-the-site.md) fixtures overwrite the site,
[A18](https://github.com/frappe/skills/blob/5dc2f984081f6d8e23559af03b0e7c2799245d79/skills/deep-app-audit/quality/A-customization/A18-check-every-writer.md) check every writer,
[B25](https://github.com/frappe/skills/blob/5dc2f984081f6d8e23559af03b0e7c2799245d79/skills/deep-app-audit/quality/B-correctness/B25-one-owner-writes-status.md) one owner writes a status.
When to run the whole audit: `FRAPPE.md`, "Two checks".
