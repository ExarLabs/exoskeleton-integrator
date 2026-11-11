# Testing on Frappe

How the Exoskeleton's test rule ("no behaviour ships without a test you have seen fail on it",
`.ai-dev-exoskeleton/agents/implementer.md`) applies on a Frappe bench. Source pins as in
[`GOTCHAS-frappe.md`](GOTCHAS-frappe.md).

## Before the first test

- **Know the version.** Triage prints it. Base classes differ (gotcha 9):
  - v15: `from frappe.tests.utils import FrappeTestCase`
  - v16: `from frappe.tests import IntegrationTestCase, UnitTestCase`
- **Use a test site, never a live one.** `run-tests` refuses to run unless the site allows it
  ([v15 commands/utils.py#L804-L809](https://github.com/frappe/frappe/blob/2e9ecdc03fa5b5b8d1ba05224a1aff7dad832bd0/frappe/commands/utils.py#L804-L809),
  [v16 commands/testing.py#L350-L355](https://github.com/frappe/frappe/blob/49789a1711d4dde2be9c6888efe35651465f4b64/frappe/commands/testing.py#L350-L355)).
  Set it only on a throwaway site: `bench --site test.localhost set-config allow_tests true`.
  If a site you did not create already has `allow_tests` on, stop and ask.

## Seeing it fail

```
bench --site test.localhost run-tests --app <app> --module <app>.<module>.doctype.<doctype>.test_<doctype>
```

1. Write the test. Run it. It must fail, for the reason you expect (read the assertion, not
   just the red).
2. Implement. Run it again. It passes.
3. For a bug fix, also run it once against the old code (stash the fix) and see it fail. A
   test that passes both ways proves nothing.

## What to test on Frappe

- **Permissions as a real role.** Create a user with only the role in question and run the
  action with `frappe.set_user(...)`. Administrator bypasses most checks, so a test as
  Administrator proves nothing about access. Reset with `frappe.set_user("Administrator")`.
- **Denial, not only success.** For every endpoint, report or list a change opens, add one test
  that a user without access is refused (the Exoskeleton planner's Guard rule). Repeat the same
  call as an allowed user, so you know the refusal came from the guard and not from a broken
  call.
- **The save chain.** When your change sits in a hook or a Server Script, test through
  `doc.save()` or the REST call, not by calling your function directly (gotcha 7).
- **Migrations.** A patch runs once per site. Test it on a copy of real data shape, and make it
  safe to run twice.

## The agent's live run, before the human's manual test

The manual test stays the human's gate. Before handing over, the agent drives each intent line
itself on the running site (browser for UI, the command for an API), on the test site that
holds a copy of the live data, not on the `run-tests` site:

- one scenario per intent line, named after it (`intent #2`);
- evidence the human can see without running anything, saved in the task folder: a screenshot
  for a state, a short video (or a screenshot per step) for drag and drop or a multi-step flow,
  the command and the relevant output for an API;
- **live** only when driven against the running site in this run. A unit test, a mock or
  reading the code is not live. "Not tested, because ..." beats a guessed pass.

The human then tests with the evidence in hand. Frappe's `ship-it` has the same step
([steps/test.md](https://github.com/frappe/skills/blob/5dc2f984081f6d8e23559af03b0e7c2799245d79/skills/ship-it/steps/test.md)).

## Work in the bench's own checkout

The bench loads an app from `apps/<app>`. A `git worktree` or a second clone elsewhere is
invisible to it, so a change made there is never what the site runs (Frappe's `ship-it` says
the same). Edit, test and commit in `apps/<app>`, and say in `CONTEXT.md` which checkout the
bench runs.

## When there is no test suite

Customer-site work often has none: a Server Script, a Custom Field, a permission change made
on the site itself. The rule still holds in a different form, see
[`overrides/PROPOSED-implementer.md`](overrides/PROPOSED-implementer.md): reproduce the
behaviour on a test site, record the failing state, change, record the passing state.
