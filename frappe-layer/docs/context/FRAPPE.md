# Frappe layer: what every Frappe project shares

Installed by **Exoskeleton Integrator**. Onboarding still writes this project's own
`ARCHITECTURE.md`, `PATTERNS.md` and the rest; this file and its siblings hold what is true on
any Frappe site, so onboarding does not have to rediscover it.

## Files

| File | Holds | Read it when |
|---|---|---|
| `FRAPPE.md` | This index, triage, rigor defaults | onboarding, any session start |
| `GOTCHAS-frappe.md` | Verified traps with source lines (permissions, Server Scripts, REST writes, tests) | planning, implementing, reviewing |
| `SAFE_EXEC-frappe.md` | Generated list of what a Server Script can call, per version | writing or reviewing a Server Script |
| `TESTING-frappe.md` | Seeing a test fail on a bench; what to test on Frappe | implementing, debugging |
| `REVIEW-frappe.md` | Where the reviewer looks on Frappe changes | reviewing |
| `overrides/PROPOSED-implementer.md` | Inert proposal for work without a test suite | when the project has no tests |

Add a row for this file to `docs/context/README.md` (the index onboarding writes).

## Triage first

Before the explorer or planner starts, record what you are working on. Output of either script
goes into the task's `CONTEXT.md`:

- **On a bench you can reach**, from the bench directory:
  `bench --site <site> console < apps/<app>/.exoskeleton-integrator/scripts/triage_console.py`
- **On a site you reach over REST**, from this repository:
  `python3 .exoskeleton-integrator/scripts/triage_rest.py --url https://<site>`
  (API key and secret from the `FRAPPE_API_KEY` and `FRAPPE_API_SECRET` environment
  variables; GET requests only). Add `--doctype "<DocType>"` to see what runs when that
  DocType is saved.

Both print versions, the Server Scripts on the site, and which DocTypes have `Custom DocPerm`
rows. The console version also prints installed apps, developer mode, `allow_tests` and
whether Server Scripts are enabled; REST cannot see those.

## Rigor defaults on Frappe

The Exoskeleton asks one question for light or heavy rigor: would you have asked another human
to review this change? On Frappe, these are heavy by default:

- permission changes (DocPerm, Custom DocPerm, permission query conditions, `has_permission`);
- anything that writes money, stock or a document's status;
- patches and data migrations;
- Server Scripts or REST writes on a live customer site;
- anything that touches customer data you did not create.

A new report, a print format, a UI tweak on a test site: light.

## Live sites

The agent does not run `bench migrate`, `bench drop-site`, `bench reinstall`, `bench restore`
or a REST write against a live site on its own. It proposes the command and waits for a
human. The plugin's Bash guard asks for confirmation when it sees these commands.
