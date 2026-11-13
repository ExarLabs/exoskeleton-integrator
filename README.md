# Exoskeleton Integrator

**The [AI Dev Exoskeleton](https://github.com/matemajoros/ai-dev-exoskeleton), with a layer for
teams that build and change Frappe and ERPNext sites for clients.** Built for Frappe.

> Version 0.1.0, early. The project name is a working name and may change.

AI coding assistants write Frappe code that looks right and fails on a live site: a Server
Script that calls a function the sandbox does not have, a permission row that silently locks
out every other role, a one-field REST update that fires half a dozen event scripts. This
package puts two things in front of the agent: a disciplined way of working, and the Frappe
traps that method needs to know about, each one checked against the framework source.

## Built on the AI Dev Exoskeleton

The way of working is **Máté Majoros's [AI Dev Exoskeleton](https://github.com/matemajoros/ai-dev-exoskeleton)**
(MIT): five plain-markdown roles (explorer, planner, implementer, reviewer, debugger), two gates
where a human must be present (building the context, and testing the result by hand), light
or heavy rigor, evidence-based review, and "no behaviour ships without a test you have seen
fail on it". Read its README first; everything there applies here.

We ship its install payload **unchanged** in [`upstream/ai-dev-exoskeleton/`](upstream/ai-dev-exoskeleton/)
(version 0.3.0, upstream commit `77d90b4`), with its license. We do not edit the method. The
Frappe layer uses the extension points the Exoskeleton provides: project knowledge in
`docs/context/`, and rule changes as inert `docs/context/overrides/PROPOSED-*` files a human
activates.

## What this adds

| Part | What it does |
|---|---|
| [`frappe-layer/docs/context/GOTCHAS-frappe.md`](frappe-layer/docs/context/GOTCHAS-frappe.md) | Twelve traps from live sites (Custom DocPerm, the Server Script sandbox, REST writes, child table lists, permission query conditions, test classes, Server Scripts in migrate and on method paths), each with how to find it,, each with source lines at pinned v15 and v16 commits |
| [`frappe-layer/docs/context/GOTCHAS-frappe-crm.md`](frappe-layer/docs/context/GOTCHAS-frappe-crm.md) | Traps of the Frappe CRM app: a Won-type status overwrites the signing date, the "Won" name is hard-coded, Lost needs a reason, forecasting makes fields mandatory; pinned to a `frappe/crm` commit |
| [`frappe-layer/docs/context/SAFE_EXEC-frappe.md`](frappe-layer/docs/context/SAFE_EXEC-frappe.md) | What a Server Script can call on v15 and v16, **generated** from `frappe/utils/safe_exec.py`, not written by hand |
| [`frappe-layer/docs/context/TESTING-frappe.md`](frappe-layer/docs/context/TESTING-frappe.md) | Seeing a test fail on a bench; testing permissions as a real role; refusals, not only success |
| [`frappe-layer/docs/context/REVIEW-frappe.md`](frappe-layer/docs/context/REVIEW-frappe.md) | Where the reviewer looks on a Frappe change, most consequential first |
| [`frappe-layer/docs/context/FRAPPE.md`](frappe-layer/docs/context/FRAPPE.md) | Index, triage, which Frappe work is heavy by default, rules for live sites |
| [`frappe-layer/docs/context/overrides/PROPOSED-implementer.md`](frappe-layer/docs/context/overrides/PROPOSED-implementer.md) | The test rule for site customizations that have no test suite: the scenario is the test, seen failing on a test site first |
| [`scripts/triage_console.py`](scripts/triage_console.py) | Read-only triage inside a bench: versions, apps, developer mode, Server Script switch, Server Scripts, DocTypes with Custom DocPerm rows |
| [`scripts/triage_rest.py`](scripts/triage_rest.py) | The same over REST (GET only), and `--doctype` to see what runs when a DocType is saved, before you write to it |
| [`scripts/safe_exec_names.py`](scripts/safe_exec_names.py) | Regenerates the Server Script namespace from any Frappe branch or file |
| [`hooks/`](hooks/) (Claude Code plugin) | Bench context at session start; a `bench migrate` reminder after DocType JSON or `hooks.py` edits; a human confirmation before dropping a site, writing to a live site over REST, or running migrate on a non-local site |

## Install

```bash
git clone https://github.com/ExarLabs/exoskeleton-integrator.git
./exoskeleton-integrator/install.sh /path/to/your-frappe-app
```

The installer copies the Exoskeleton payload, the Frappe layer and the scripts into your app
repository and **never overwrites** a file that exists; it lists what it skipped. Then run the
Exoskeleton onboarding (`.ai-dev-exoskeleton/guides/workflows/new-project-onboarding.md`) and
add `docs/context/FRAPPE.md` to the index onboarding writes.

Claude Code users can add the hooks as a plugin:

```
/plugin marketplace add ExarLabs/exoskeleton-integrator
/plugin install exoskeleton-integrator@exarlabs
```

The hooks need `python3` and nothing else. The bench is found from the working directory, or
from `FRAPPE_BENCH_PATH`; set `FRAPPE_SITE` to choose a site.

## Works with Frappe's official skills

Frappe Technologies publishes [`frappe/skills`](https://github.com/frappe/skills): framework
knowledge and the review checklist Frappe's own maintainers use. For framework knowledge, use
those. This package does not copy them. It covers a different case: client work on existing
sites, where the change is often a Server Script, a permission or a REST integration rather
than an app with a test suite.

## What we can and cannot prove

- Every gotcha links to the source lines it rests on, at pinned commits. If Frappe changes,
  the link still shows what we read.
- The scripts and hooks have unit tests (`pytest`), and each test was seen failing against a
  deliberately broken version. `triage_rest.py` has been run against a live Frappe v16 site.
  `triage_console.py` has not yet been run in CI against a bench; that is next.
- We have no measured speed-up to report. The Exoskeleton README says what its author can and
  cannot prove about speed; we add no number of our own.

## Staying current

`python3 scripts/watch_sources.py` (read-only, run weekly) checks every file the Frappe layer
cites at a pinned commit: has its branch changed that file since? It also reports new commits,
releases and licence changes in the repositories listed in `watch/sources.json`. A changed file
is a prompt to re-read the trap that cites it, not proof the trap is wrong.

`python3 scripts/discover_sources.py` finds candidates for that list: repositories that keep
agent instructions (SKILL.md, AGENTS.md, CLAUDE.md) about Frappe, ranked by Frappe
specificity, whether the repository is itself a Frappe app, and sustained recent activity.
Stars are left out on purpose: in a field this young, early packages collected stars and then
stopped, while small, active client apps hold the rules learned on real work.

## Contributing

Issues are welcome, most of all "I tried this on my site and here is where it broke", and new
traps with a source line. Keep `GOTCHAS-frappe.md` current rather than cumulative.

## Trademarks

Frappe and ERPNext are trademarks of Frappe Technologies Pvt. Ltd. This project is not
affiliated with or endorsed by Frappe Technologies. "Built for Frappe" describes what it is for.

## License

MIT, see [LICENSE](LICENSE). Third-party parts and their licenses are listed in
[NOTICE.md](NOTICE.md). Maintained by [ExarLabs](https://exarlabs.com), Romania.
