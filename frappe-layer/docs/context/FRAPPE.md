# Frappe layer: what every Frappe project shares

Installed by **Exoskeleton Integrator**. Onboarding still writes this project's own
`ARCHITECTURE.md`, `PATTERNS.md` and the rest; this file and its siblings hold what is true on
any Frappe site, so onboarding does not have to rediscover it.

## Files

| File | Holds | Read it when |
|---|---|---|
| `FRAPPE.md` | This index, triage, rigor defaults | onboarding, any session start |
| `GOTCHAS-frappe.md` | Verified traps with source lines (permissions, Server Scripts, REST reads and writes, tests) | planning, implementing, reviewing |
| `GOTCHAS-frappe-crm.md` | Traps of the Frappe CRM app (deal status and `closed_date`, the "Won" name, Lost reason, forecasting) | any change that reads or writes `CRM Deal` or its statuses |
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

## Intent, at build-context

Before planning, write the intent in at most five numbered lines, each a behaviour a tester can
check, and at least one line that starts with **Must not:** (what the change leaves alone or
must never show). The owner confirms it; the numbers stay stable so tests and findings can cite
them (`intent #3`). It goes into `## Acceptance` of `PLAN.md`. Frappe's `ship-it` works the same
way ([steps/intent.md](https://github.com/frappe/skills/blob/5dc2f984081f6d8e23559af03b0e7c2799245d79/skills/ship-it/steps/intent.md)).

## A bug report

A report is not a specification: its guesses send you where the reporter looked. Have a
separate agent extract only the facts (symptom, expected, exact reproduction, verbatim errors,
environment, gaps), reproduce before fixing, then follow the Exoskeleton debugger. Frappe's
[`fix-issue`](https://github.com/frappe/skills/blob/5dc2f984081f6d8e23559af03b0e7c2799245d79/skills/fix-issue/SKILL.md)
does this; install it from there if you prefer it.

## Two checks: ours every time, Frappe's audit before a big release

They look at different things, so neither replaces the other.

- **Every change: triage and the gotchas.** Cheap, so never skipped. They look at the **site**:
  the Server Scripts, permission rows and Custom Fields that live there and not in any
  repository, and how the test site differs from the live one.
- **Before a big release, or an app's first delivery to a client: Frappe's `deep-app-audit`**
  from [`frappe/skills`](https://github.com/frappe/skills/tree/5dc2f984081f6d8e23559af03b0e7c2799245d79/skills/deep-app-audit),
  installed from there. It looks at the **app's code**, rule by rule (security, correctness,
  customization), with an independent verifier per finding. It starts many agents and costs
  accordingly; the owner decides when to run it.

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
