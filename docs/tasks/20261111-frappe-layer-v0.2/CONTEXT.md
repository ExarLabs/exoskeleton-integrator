# Frappe layer v0.2, lessons from a real Frappe build: Context

## Jira / Ticket
none (the retrospective it rests on is internal)

## Business Requirements
- ExarLabs wants its own Frappe-based package built on the AI Dev Exoskeleton, tailored to
  Frappe development, and grown from our own work rather than from guesses.
- The first source of lessons is a real build: a sales pipeline screen in a Frappe app
  (an internal app on a Frappe v16 + Frappe CRM site), shipped in three releases on 2026-11-10/11.
  Twelve cases were reviewed; the ones that belong in a Frappe layer are below.
- The package first speeds up our own work. Publishing more widely is a later question.

## Technical Decisions
- The Exoskeleton payload in `upstream/` stays unchanged. All additions use its extension
  points: `docs/context/` files and inert `overrides/PROPOSED-*` files.
- Every new trap cites the source it rests on at a pinned commit, as in v0.1.
- Scripts stay read-only against sites (GET only, console without writes) and get unit tests
  that were seen failing.
- Frappe CRM (the `crm` app) gets its own gotchas file: it is an app, not the framework, and
  is pinned to its own commit.

## The cases this version answers
1. A local test site lacked 25 Custom Fields of the live site; a `meta.has_field` guard silently
   skipped a filter, so the screen showed 56 records locally and 2 on live. Triage compared
   versions, Server Scripts and Custom DocPerm rows, not Custom Fields.
2. A live Server Script on another DocType (an order, After Save) wrote the deal status back.
   `triage_rest.py --doctype` lists only the scripts *on* the DocType, not the scripts that
   *write* it.
3. Frappe CRM sets `closed_date` to today on every change to a Won-type status, also on insert,
   and checks the literal name "Won"; a Lost-type status needs `lost_reason`, and "Other" also
   needs `lost_notes`.
4. `/api/resource/<child table>` refuses a list (403); `frappe.client.get_list` needs `parent`.
5. The manual test gate ran on sample data; the junk records the user cared about only showed
   up on a copy of live data, two releases later.
6. `run-tests` and the human's manual test ran on the same site.
7. The change mirrored another system (Salesforce stages) and was first built from a month-old
   note instead of the live system.

## Open Questions That Were Resolved
- Q: New repo or this one? → A: this one (`ExarLabs/exoskeleton-integrator`); it already is the
  Frappe-tailored Exoskeleton.
- Q: Edit the method files? → A: no; extension points only.

## Exclusions
- No change to `upstream/`.
- No script writes to a site. A live-data mirror is described as a procedure, not shipped as a
  tool in this version.
- No install into a client or colleague repository in this task (the first pilot in our internal app
  needs its owner).
- Harness traps (Windows paths, large heredocs) are not Frappe and stay out.
- No push or release without the owner's yes.

## Rigor
light (proposed): docs and read-only scripts with unit tests; nothing writes to a site. The
owner decides.
