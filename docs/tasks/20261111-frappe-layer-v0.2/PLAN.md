# Frappe layer v0.2

## Goal
Turn the lessons of a real Frappe build into the Frappe layer: three new verified traps, a
triage that sees Custom Fields and the scripts that write a DocType, a way to compare a test
site with a live one, and a manual test gate that runs on a copy of live data.

## Current State
- `frappe-layer/docs/context/`: nine framework traps (`GOTCHAS-frappe.md`), the generated
  Server Script namespace, testing, review and the index (`FRAPPE.md`), one inert override.
- `scripts/triage_rest.py` and `scripts/triage_console.py`: versions, Server Scripts, DocTypes
  with Custom DocPerm rows; `--doctype` lists that DocType's own event scripts and permission rows.
- Nothing about Frappe CRM. Nothing compares two sites.

## Target State
- `GOTCHAS-frappe.md` gains trap 10 (child-table lists over REST).
- New `GOTCHAS-frappe-crm.md`: the Frappe CRM traps (Won-type status and `closed_date`, the
  literal "Won", Lost needs a reason), pinned to a `frappe/crm` commit.
- Triage prints Custom Fields and Property Setters per DocType, and with `--doctype` also the
  Server Scripts on *other* DocTypes whose code mentions the DocType. `--json` output.
- New `scripts/triage_diff.py`: two triage JSON files in, the differences that change behaviour
  out (versions, Server Scripts, Custom DocPerm DocTypes, Custom Fields).
- `TESTING-frappe.md` and the override say: the manual gate runs on a copy of live data, on a
  site that is not the `run-tests` site; how to make that copy read-only from live.
- `FRAPPE.md` gains three context questions for `build-context`.

Avoid: calling the copy a "backup" (it is a read-only mirror), or the diff a "sync".

## Phases

### Phase 1: Verified traps (docs)
**Scope:** `frappe-layer/docs/context/GOTCHAS-frappe.md`, `frappe-layer/docs/context/GOTCHAS-frappe-crm.md` (new), `frappe-layer/docs/context/FRAPPE.md`, `tests/test_docs_pins.py` (new), `README.md`, `CHANGELOG.md`
**Changes:**
- [x] GOTCHAS-frappe.md: trap 10, a child table over REST: `/api/resource/<child>` refuses the
      list; `frappe.client.get_list(doctype=<child>, parent=<parent doctype>)` works. Source lines
      at the pinned v15 and v16 commits (the parent check in `db_query`/`client.get_list`).
- [x] GOTCHAS-frappe-crm.md (new): (a) every change to a Won-type status sets `closed_date` to
      today, also on insert; moving Won → another Won-type status overwrites the signing date;
      (b) `update_closed_date` checks the literal name "Won", so renaming the status breaks it;
      (c) a Lost-type status needs `lost_reason`, "Other" also `lost_notes`; (d) forecasting, when
      on, requires expected value and closure date. Pinned to `frappe/crm` at `ead04d4` (v1.77.3),
      each with its line.
- [x] FRAPPE.md: a row for the CRM file in the index.
- [x] tests/test_docs_pins.py: every github.com/frappe link in `frappe-layer/` points to a
      40-character commit, never a branch (seen failing on a branch link first).
**Verify:** `python -m pytest -q`; open every new source link and read the cited lines.
**Rollback:** revert the commit; docs only.
**Depends on:** none

### Phase 2: Triage sees Custom Fields and cross-writers
**Scope:** `scripts/triage_rest.py`, `scripts/triage_console.py`, `tests/test_triage_rest.py`, `tests/test_triage_console.py` (new if needed), `frappe-layer/docs/context/FRAPPE.md`
**Changes:**
- [ ] triage_rest.py: site block adds Custom Fields and Property Setters counted per DocType;
      `--doctype` adds that DocType's Custom Fields (fieldname, type) and the Server Scripts on
      other DocTypes whose script text names it ("may write this DocType"); `--json`.
- [ ] triage_console.py: the same, inside a bench.
- [ ] Tests with recorded responses, each seen red against the old output.
**Verify:** `python -m pytest -q`; a GET-only run against our live CRM site with `--doctype "CRM Deal"` lists the order script that writes the deal as a cross-writer.
**Rollback:** revert; the old output format stays the default without `--json`.
**Depends on:** none

### Phase 3: Compare two sites
**Scope:** `scripts/triage_diff.py` (new), `tests/test_triage_diff.py` (new), `frappe-layer/docs/context/overrides/PROPOSED-implementer.md`, `frappe-layer/docs/context/FRAPPE.md`
**Changes:**
- [ ] triage_diff.py: two `--json` files in; prints what differs and would change behaviour
      (versions, apps, Server Scripts by name and event, Custom DocPerm DocTypes, Custom Fields);
      exit code 1 when something differs, so a plan step can gate on it.
- [ ] PROPOSED-implementer.md: "Triage both sites" names the diff script and Custom Fields.
**Verify:** `python -m pytest -q`; run it on the triage of a local site and of the live site and
see the missing Custom Fields listed (the case that cost us a release).
**Rollback:** delete the script; nothing else depends on it.
**Depends on:** Phase 2 (`--json`)

### Phase 4: The manual gate on live-shaped data
**Scope:** `frappe-layer/docs/context/TESTING-frappe.md`, `frappe-layer/docs/context/FRAPPE.md`
**Changes:**
- [ ] TESTING-frappe.md: two sites, never one: `run-tests` on a throwaway test site; the human's
      manual test on a site that holds a read-only copy of the live data the change reads.
- [ ] TESTING-frappe.md: how to make that copy: read over REST with GET only; create the live
      site's Custom Fields first (Phase 3 shows which); insert rows without hooks
      (`db_insert`) so nothing fires; never copy User records, passwords or keys; mute emails
      and pause the scheduler on the copy; delete the transfer files afterwards.
- [ ] FRAPPE.md: three context questions for `build-context` on a Frappe task: Does the change
      follow another system (CRM stages, an authority's rules)? Then read that system live.
      Which sites will see it, and do they differ (Phase 3)? Who writes this data today, people or
      agents, and does the change alter that?
**Verify:** read-through by the owner; the procedure matches what was done on 2026-11-11.
**Rollback:** revert; docs only.
**Depends on:** Phase 3 (it names the diff)

## Acceptance
- [ ] WHEN an agent plans a status change on a Frappe CRM deal → THEN `GOTCHAS-frappe-crm.md`
      tells it that the signing date is overwritten, with the source line.
- [ ] WHEN `triage_rest.py --doctype "CRM Deal"` runs against a site where an order's After Save
      script writes the deal → THEN that script is listed as a possible writer.
- [ ] WHEN the triage of a local site and a live site is compared and the local one lacks Custom
      Fields → THEN `triage_diff.py` names each missing field and exits non-zero.
- [ ] WHEN a gotcha links to a branch instead of a commit → THEN the test suite fails.
- [ ] WHEN the triage runs with a key that cannot read Custom Field → THEN it says so and still
      prints the rest, not a stack trace.

## Risks
- A text search for a DocType name in script code finds mentions that do not write: label them
  "mentions", not "writes".
- Pinned line numbers drift on newer releases: the pin is the point; the test keeps pins pinned.
- The CRM file grows into a CRM manual: keep it to traps that cost real time, as the framework
  file does.

## Open Questions
- Máté's view on the CRM file living here or in a separate package. Resolved 2026-11-11: he agreed to the public package; the file stays here.
- Whether the first pilot in our internal app happens before or after this version
  Resolved 2026-11-11: the app owner agreed; timing is ours.
