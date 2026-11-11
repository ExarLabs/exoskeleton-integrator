# Frappe gotchas (verified)

Traps that cost us real time on live Frappe sites. Each one cites the framework source at a
pinned commit, so you can check it yourself:

- **v15** = `frappe/frappe` branch `version-15` at [`2e9ecdc`](https://github.com/frappe/frappe/tree/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0)
- **v16** = `frappe/frappe` branch `version-16` at [`49789a1`](https://github.com/frappe/frappe/tree/49789a1711d4dde2be9c6888efe35651465f4b64)

Read this file when planning, implementing or reviewing anything that touches permissions,
Server Scripts, REST writes or tests. Keep it current: when a new trap costs you time, add it
here with its source line, and remove one that no longer holds.

---

## 1. One Custom DocPerm row replaces all standard permissions of that DocType

**What happens.** When a DocType has at least one `Custom DocPerm` row, Frappe uses only the
`Custom DocPerm` rows for it. The standard `DocPerm` rows of that DocType stop counting.
([v15 permissions.py#L480-L495](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/permissions.py#L480-L495),
[v16 permissions.py#L507-L527](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/permissions.py#L507-L527))

The Role Permission Manager and `frappe.permissions.add_permission` protect you: they first
copy the standard rows into `Custom DocPerm` (`setup_custom_perms`,
[v15 #L660-L664](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/permissions.py#L660-L664),
[v16 #L695-L699](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/permissions.py#L695-L699)).
A row inserted any other way (REST, fixture, patch, `frappe.get_doc(...).insert()`) does not,
and every role without a custom row loses access to that DocType.

**Do this.**
- Prefer `add_permission` / `update_permission_property` or the Role Permission Manager.
- If you write `Custom DocPerm` rows directly, write one row for **every** role that needs the
  DocType (System Manager and integration users included), and set every right field
  explicitly (`read`, `write`, `create`, `delete`, `submit`, `cancel`, `amend`, `report`,
  `export`, `print`, `email`, `share`) so the row says what it means.
- After the change, test access as each role, not as Administrator.

## 2. Server Scripts see a restricted namespace

**What happens.** A Server Script runs with globals built in `frappe/utils/safe_exec.py`, not
with normal imports. Bare helper names (`flt`, `nowdate`, `add_days`) are not defined, and
several familiar `frappe.*` functions are missing:

| Assumed name | v15 | v16 |
|---|---|---|
| `frappe.get_roles` | missing | missing |
| `frappe.has_permission` | missing | missing |
| `frappe.generate_hash` | use `frappe.utils.generate_hash` | use `frappe.utils.generate_hash` |
| `frappe.parse_json` | missing (use `json.loads`) | use `frappe.utils.parse_json` |
| `frappe.cache` | missing | missing |
| `frappe.get_traceback` | missing | missing |
| `flt`, `cint`, `nowdate` (bare) | use `frappe.utils.flt` etc. | use `frappe.utils.flt` etc. |

The full, generated list is in [`SAFE_EXEC-frappe.md`](SAFE_EXEC-frappe.md). Regenerate it
with `python3 .exoskeleton-integrator/scripts/safe_exec_names.py --branch version-15 --branch version-16` instead of
editing it by hand.

**Do this.** Before writing or reviewing a Server Script, check every `frappe.*` and
`frappe.utils.*` call against `SAFE_EXEC-frappe.md`. To get the current user's roles, read the
`Has Role` child table (`frappe.get_all("Has Role", filters={"parent": frappe.session.user,
"parenttype": "User"}, pluck="role")`), and test it as a non-admin user.

## 3. Top-level functions in a Server Script cannot call each other

**What happens.** The script runs as `exec(code, globals, locals)` with two separate
dictionaries ([v15 safe_exec.py#L123-L127](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/utils/safe_exec.py#L123-L127),
[v16 #L126](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/utils/safe_exec.py#L126));
DocType Event scripts get `_locals={"doc": doc}`
([v15 server_script.py#L163-L174](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/core/doctype/server_script/server_script.py#L163-L174)).
A function defined at the top of the script lands in `locals`; inside another function,
Python looks the name up in `globals`, so the call raises `NameError` (an HTTP 500 on API
scripts). Reading a top-level variable from inside a function fails the same way.

**Do this.** Write the script top to bottom without helper functions, or define a helper
inside the function that uses it, or pass values in as arguments. Run the script once on a
test site before saving it on a live one.

## 4. DocType Event scripts cannot commit

**What happens.** For DocType Event scripts Frappe calls `safe_exec(...,
restrict_commit_rollback=True)`
([v15 server_script.py#L172](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/core/doctype/server_script/server_script.py#L172),
[v16 #L198](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/core/doctype/server_script/server_script.py#L198)),
which removes `frappe.db.commit`, `frappe.db.rollback` and `frappe.db.add_index`
([v15 safe_exec.py#L111-L115](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/utils/safe_exec.py#L111-L115),
[v16 #L114-L118](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/utils/safe_exec.py#L114-L118)).

**Do this.** Let the request's transaction commit. If work must happen outside it, enqueue it.

## 5. Server Scripts are off unless the bench turns them on

**What happens.** `server_script_enabled` is read from `common_site_config.json` only, never
from a site config
([v15 safe_exec.py#L83-L85](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/utils/safe_exec.py#L83-L85),
[v16 #L86-L88](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/utils/safe_exec.py#L86-L88)).
A script that works on one bench can be dead on another.

**Do this.** Check it in triage (`.exoskeleton-integrator/scripts/triage_console.py` prints it). Enabling it is a
bench-wide security decision: `bench set-config -g server_script_enabled 1`, with the owner's yes.

## 6. "Before Save" in the UI is the `validate` event

**What happens.** The Server Script event names map to controller methods: "Before Save" is
`validate`, "After Save" is `on_update`
([v15 server_script_utils.py#L10-L11](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/core/doctype/server_script/server_script_utils.py#L10-L11),
[v16 #L10-L11](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/core/doctype/server_script/server_script_utils.py#L10-L11)).
A "Before Save" script therefore runs before the controller's `before_save`.

**Do this.** Never call `doc.save()` inside a Before Save or After Save script: set fields on
`doc` and let the running save persist them.

## 7. A REST update runs the whole save chain, even for one field

**What happens.** `PUT /api/resource/<doctype>/<name>` (v1) and the v2 equivalent load the
document, apply your fields and call `doc.save()`; for a child row they also save the parent
([v15 api/v1.py#L49-L65](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/api/v1.py#L49-L65),
[v15 api/v2.py#L112-L127](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/api/v2.py#L112-L127),
[v16 api/v1.py#L50-L67](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/api/v1.py#L50-L67),
[v16 api/v2.py#L196-L212](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/api/v2.py#L196-L212)).
`save()` runs every controller hook, and each hook also runs the matching Server Scripts
(`run_method`,
[v15 document.py#L1149-L1168](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/model/document.py#L1149-L1168),
[v16 #L1514-L1533](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/model/document.py#L1514-L1533)).
Writing one field, even an empty one, can send emails, change other fields or fail on
validation that has nothing to do with your field.

**Do this.** Before any REST write to a live site, list the DocType's event scripts
(`python3 .exoskeleton-integrator/scripts/triage_rest.py --doctype "<DocType>"`), read what each does, and predict the
effect. Try the write on a test record first.

## 8. A falsy permission query condition filters nothing

**What happens.** `permission_query_conditions` hooks and Permission Query Server Scripts are
collected with `if c := ...: conditions.append(c)`. An empty string, `None` or `False` adds
no condition, so the list shows **every** record
([v15 db_query.py#L1504-L1517](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/model/db_query.py#L1504-L1517),
[v16 #L1173-L1201](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/model/db_query.py#L1173-L1201)).

**Do this.** To deny all, return a condition that is always false, such as `"1=0"`. Test the
list view as a restricted user.

## 9. Test base classes differ between v15 and v16

**What happens.** v15 has `FrappeTestCase` in `frappe/tests/utils.py`
([v15 #L20](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/tests/utils.py#L20)).
v16 exports `IntegrationTestCase` and `UnitTestCase` from `frappe.tests`
([v16 tests/__init__.py#L3](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/tests/__init__.py#L3),
classes in `frappe/tests/classes/`). The v16 classes do not exist on v15.

**Do this.** Check the bench version in triage before writing a test, and see
[`TESTING-frappe.md`](TESTING-frappe.md).

## 10. A child table list needs its parent DocType

**What happens.** Listing a child table (`Dynamic Link`, `Has Role`, any `istable` DocType)
without saying whose child it is fails with `PermissionError` (HTTP 403), even for a user who
can read every parent. The list query checks read permission with
`parent_doctype=parent_doctype or self.doctype`, so with no parent it asks whether the child
is its own parent
([v15 db_query.py#L904-L913](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/model/db_query.py#L904-L912),
[v16 #L630-L638](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/model/db_query.py#L630-L639)),
and the child permission check refuses that
([v15 permissions.py#L800-L820](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/permissions.py#L800-L819),
[v16 #L839-L860](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/permissions.py#L839-L861)).

The fix is one parameter, `parent=<Parent DocType>`. `frappe.client.get_list` takes it
([v15 client.py#L28-L55](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/client.py#L28-L55),
[v16 #L27-L52](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/client.py#L27-L52)),
and `GET /api/resource/<child>` passes its query string straight to it
([v15 api/v1.py#L31](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/api/v1.py#L31),
[v16 #L32](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/api/v1.py#L32)),
so `?parent=Contact` works there too. Checked on a v16.26.3 site with an API user (2026-11-11):
`/api/resource/Dynamic Link` gave 403, the same call with `parent=Contact` gave 200, and
`parent=User` (not a parent of `Dynamic Link`) gave 403 again.

`parent` names whose permission is checked; it is not documented as a row filter. On that
site `parent=Address` returned only rows with `parenttype` Address, but the pinned sources
do not show one clear place that guarantees it.

**Do this.** Pass `parent=<Parent DocType>` and, when the child table belongs to several
parents, also filter `parenttype` yourself
(`filters=[["parenttype", "=", "Contact"]]`). Inside Python on the bench, `frappe.get_all`
skips permissions and needs neither.
