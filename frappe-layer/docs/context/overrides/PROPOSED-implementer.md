# PROPOSED override: implementer.md

> Inert. Agents read `docs/context/overrides/implementer.md`, never a `PROPOSED-` file.
> Activating this one is a rename, and the rename is a human's call
> (`.ai-dev-exoskeleton/guides/PLAYBOOK.md`, "Adapting a rule without forking").
> Shipped by Exoskeleton Integrator for Frappe projects whose change lives on a site, not in an
> app's test suite.

## Rule overridden

`implementer.md` rule 2: "No behaviour ships without a test you have seen fail on it", and the
steps built on it (Step 3's tests and Step 5's full test-suite run).

## The fact that contradicts it

Part of the work is configuration on a site: a Server Script, a Custom Field, a Property
Setter, a permission row, a workflow. There is no app and no test module to put a test in, and
`run-tests` must not run on a live site (`TESTING-frappe.md`).

## What applies instead

- **The scenario is the test.** Each `PLAN.md` phase states the scenario as steps with the
  expected result, including at least one refusal for any access change.
- **See it fail first.** Run the scenario on a test site (a copy of the customer site, or a
  fresh site with the same apps and versions) before the change, and record the wrong result
  (output, screenshot, or the REST response).
- **See it pass.** Apply the change on the test site, run the same scenario, record the result.
  Only then propose the change for the live site, as a separate step a human approves.
- **Triage both sites.** `.exoskeleton-integrator/scripts/triage_console.py` or `.exoskeleton-integrator/scripts/triage_rest.py` output for
  the test site and the live site goes into `CONTEXT.md`; differences in versions, Server
  Scripts or Custom DocPerm rows are named before the change ships.
- Everything else in `implementer.md` stands.
