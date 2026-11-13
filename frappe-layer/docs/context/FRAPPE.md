# Frappe layer: what every Frappe project shares

Installed by **Exoskeleton Integrator**. Onboarding still writes this project's own
`ARCHITECTURE.md`, `PATTERNS.md` and the rest; this file and its siblings hold what is true on
any Frappe site, so onboarding does not have to rediscover it.

## Files

| File | Holds | Read it when |
|---|---|---|
| `FRAPPE.md` | This index, triage, the light way before any build, rigor defaults | onboarding, any session start, before planning |
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

## The light way, at build-context

Writing a new app with AI is cheap; owning one is not: Frappe upgrades, its own permission
surface, its own deploy, one more screen people have to learn. So before planning anything that
adds code, write once in the task's `CONTEXT.md`, under `## Light way`, how far the site's
existing modules get without code:

1. **What it uses.** Settings and records only: roles and DocPerm, Custom Fields (unique where a
   duplicate must be refused), Workflow, Web Form, Report Builder and Query Report, Number Card
   and Dashboard, Notification, Assignment Rule, Workspace and Desktop Icon; in Frappe CRM its
   statuses, field layouts, form scripts and dropdown items.
2. **Intent coverage.** One line per intent line: covered, or not and why
   (`intent #3: not covered, tiered commission is a calculation`).
3. **The owner chooses**, at the same gate as the intent. Choosing the build is fine; skipping the
   comparison is not. A light first round that runs until the rules are known (a trial, a pilot)
   is often the right answer, and the build follows when they are.

When the light way is not enough, take the lowest step that is:

- **Settings**, while the intent is records, statuses and permissions, the users are internal and
  the standard screens will do. Code is needed for a calculation with rules (tiers, proration),
  for matching against other records (normalised names, a tax ID across DocTypes), for outside
  people who log in, and for money or permissions that need tests.
- **A module in an app we already own**, while it shares that app's client, team, release rhythm
  and audience. A module lives only in an app we own, never inside Frappe, ERPNext or Frappe CRM.
- **A separate app**, when at least one is true: it will be installed at more than one client;
  another team or release rhythm; another audience or risk (outside people log in); it must be
  removable without a trace (an experiment); another owner (our reusable knowledge goes in our
  app, the client's own process in the client's). A separate app that leans on another app's
  login, templates or deploy is a module in practice: lift the shared part out first, or call it
  a module.

### Where the screens can change (Frappe v16.26.3, Frappe CRM v1.77.3)

- **Desk.** Desktop icons and workspace sidebars are records (`Desktop Icon`,
  `Workspace Sidebar`). An app ships its own icon and sidebar, links a sidebar item to its own
  desk Page, a report or a URL, and other icons are hidden by role or Module Profile. Editing
  another app's sidebar on a site works until that app ships a newer file, which replaces the
  edit on migrate (`frappe/modules/import_file.py`, the `modified` comparison): ship your own
  sidebar instead. The desk frame (top bar, sidebar) stays Frappe's; restyling it through
  `app_include_css` breaks on upgrades.
- **Frappe CRM (`/crm`).** A prebuilt Vue app. Its left sidebar is fixed in code
  (`frontend/src/components/Layouts/AppSidebar.vue`) and its shell loads no other app's CSS or
  JS. Without a fork: fields, field layouts (`CRM Fields Layout`), statuses, form scripts with
  buttons on the lead and deal pages (`CRM Form Script`), brand name and logo, and items in the
  user dropdown (`FCRM Settings`, dropdown items), which open a route or URL. A link to your own
  screen fits in that dropdown, not in the sidebar.
- **A designed screen of your own** is a web page (`www/` or a `page_renderer`) on its own
  template, outside the desk.

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

## Where we differ from Frappe's `frappe-app-dev`

Install Frappe's [`frappe-app-dev`](https://github.com/frappe/skills/tree/5dc2f984081f6d8e23559af03b0e7c2799245d79/skills/frappe-app-dev)
for framework knowledge; this layer does not repeat it. On client sites, three of its points
lose to ours:

- **Check the version.** It says not to run discovery commands. On a client site the version
  decides the test classes, the APIs and the traps, so triage prints it first.
- **Custom Fields in code, not fixtures.** Its `hooks.md` shows `fixtures = ["Custom Field"]`;
  Frappe's own audit (A08, A09) and `REVIEW-frappe.md` say create them in code.
- **Tests on v15.** It shows only the v16 classes; on v15 use `FrappeTestCase` (gotcha 9).

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
