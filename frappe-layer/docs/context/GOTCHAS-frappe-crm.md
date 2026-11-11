# Frappe CRM gotchas (verified)

Traps of the **Frappe CRM app** (`frappe/crm`), not of the framework; those are in
[`GOTCHAS-frappe.md`](GOTCHAS-frappe.md). Each cites the app source at a pinned commit:

- **crm v1.77.3** = `frappe/crm` tag `v1.77.3` at [`ead04d4`](https://github.com/frappe/crm/tree/ead04d4b95455f1673b477cfb4b4ac017ce3d4e9)

Read this file when your change reads or writes `CRM Deal` (status, dates, value), adds or
renames a `CRM Deal Status`, or mirrors another sales system's stages into the CRM. Keep it to
traps that cost real time; this is not a CRM manual.

---

## 1. Every change to a Won-type status overwrites `closed_date`, also on insert

**What happens.** In `CRM Deal.validate`, when `status` changed and the new status has type
`Won`, `closed_date` is set to today
([crm_deal.py#L90-L93](https://github.com/frappe/crm/blob/ead04d4b95455f1673b477cfb4b4ac017ce3d4e9/crm/fcrm/doctype/crm_deal/crm_deal.py#L90-L93)).
It does not look at the value already there. So:

- moving a deal from one Won-type status to another (for example from "Won" to a
  "Delivery" status you added with type Won) replaces the signing date with today;
- inserting a deal that already has a Won-type status and a `closed_date` replaces that date
  too (a new document counts as changed). Test fixtures that create won deals with a past
  date get today's date instead.

**Find it.** List the statuses with their type (`GET /api/resource/CRM Deal Status` with fields `name`, `type`): more than one Won-type status is the risk. In code: `rg -n "closed_date" --type py`.

**Do this.**
- If your pipeline has more than one Won-type status, keep the date in a `validate` hook of
  your app (`doc_events`, which runs after the controller's `validate`): when the status before
  the save was also Won-type, put the old `closed_date` back. Test both directions.
- In tests, set `closed_date` with `frappe.db.set_value` after the insert, not in the insert.
- Never write a deal's `status` from a second place (another DocType's script, a sync job)
  without reading this first: the CRM controller is the status owner. Frappe's own audit has
  the general rule as B25, "one owner writes a status field"
  ([frappe/skills](https://github.com/frappe/skills/blob/5dc2f984081f6d8e23559af03b0e7c2799245d79/skills/deep-app-audit/quality/B-correctness/B25-one-owner-writes-status.md)).

## 2. One helper checks the status *name* "Won", not its type

**What happens.** `update_closed_date` fills an empty `closed_date` only when
`self.status == "Won"`, comparing the name
([crm_deal.py#L220-L225](https://github.com/frappe/crm/blob/ead04d4b95455f1673b477cfb4b4ac017ce3d4e9/crm/fcrm/doctype/crm_deal/crm_deal.py#L220-L225)),
while trap 1 uses the type. A Won-type status with another name ("Signed", "Megnyert") gets a
date when the status changes, but an empty date is never filled on a later save.

**Find it.** The same list: is there a status named exactly "Won"? In code: `rg -n '"Won"' --type py`.

**Do this.** Do not rename the standard "Won" status; add new statuses next to it. When you
mirror another system's stages, map its won stage onto "Won".

## 3. A Lost-type status cannot be saved without a reason

**What happens.** When the status has type `Lost`, `lost_reason` is required, and if the
reason is "Other", `lost_notes` is required too; otherwise the save raises `ValidationError`
([crm_deal.py#L255-L263](https://github.com/frappe/crm/blob/ead04d4b95455f1673b477cfb4b4ac017ce3d4e9/crm/fcrm/doctype/crm_deal/crm_deal.py#L255-L263)).
A status change from a list, a board or a REST call that sends only `status` fails.

**Find it.** Every path that sets `status` on a `CRM Deal` (UI actions, REST calls, Server Scripts, hooks): does it also send `lost_reason`?

**Do this.** Any UI or API you build that can move a deal to a Lost-type status asks for the
reason (and the notes for "Other") in the same step and sends them with the status. Test the
refusal without a reason, and the "Other" case.

## 4. Forecasting, when on, makes value and closure date mandatory

**What happens.** If `FCRM Settings.enable_forecasting` is set, every deal save needs
`expected_deal_value` (non-zero) and `expected_closure_date`
([crm_deal.py#L249-L253](https://github.com/frappe/crm/blob/ead04d4b95455f1673b477cfb4b4ac017ce3d4e9/crm/fcrm/doctype/crm_deal/crm_deal.py#L249-L253)).
Code that works on a site with forecasting off fails on one with it on.

**Find it.** `GET /api/resource/FCRM Settings/FCRM Settings`, field `enable_forecasting`, on every site.

**Do this.** Read the setting in triage on every site the change will run on, and set both
fields in test fixtures so the tests pass either way.
