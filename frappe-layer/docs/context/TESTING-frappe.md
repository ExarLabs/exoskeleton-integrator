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

## When there is no test suite

Customer-site work often has none: a Server Script, a Custom Field, a permission change made
on the site itself. The rule still holds in a different form, see
[`overrides/PROPOSED-implementer.md`](overrides/PROPOSED-implementer.md): reproduce the
behaviour on a test site, record the failing state, change, record the passing state.
