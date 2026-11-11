# Reference: Heavy Mode

> Read only when `CONTEXT.md`'s `## Rigor` is `heavy`. Each role reads its own section.

**Why this isn't the default.** The gates below catch defects nearly disjoint from what the
manual test catches: they don't shorten today's fix round, they buy down a future regression.
How long the code will live decides whether that pays — long-lived, multi-person, money- or
permission-touching work, yes; an MVP or a handover, no.

## Planner
End the plan with a hardening phase — the pass below, depending on the last implementation
phase, scoped to test files only. It is a phase like any other, so it carries its own
checkbox, `Verify` and `Rollback`, and a skipped one is visible in `PLAN.md`. When you hand
over a heavy plan, name the next step: the plan review, plus `adversarial-review` in a
different model.

## Implementer
Don't stop at green tests. Loop until every gate recorded under `## Quality gates` in
`docs/context/DEPENDENCIES.md` is green too, the way Law 4 loops on tests.

When the phase you were given is the hardening phase, follow the pass below and nothing else:
no production code, no new behaviour.

A disclosed risk, not a prohibition: a hard threshold is an optimization target, and the
cheapest way to lower a score is sometimes worse code — three badly named functions instead of
one clear one. The net is still positive because a gamed metric shows in the diff.

## Hardening pass
A session believes its own tests, which is why this is the plan's own last phase, ideally in a
fresh session: it checks whether the tests would notice a wrong behaviour. Add tests only —
never change production code to make a check pass.

- **A mutation tester is recorded:** run it. Every surviving mutant is a missing test; write it.
- **None is recorded:** for each acceptance item, introduce one specific wrong behaviour,
  confirm a test goes red, then revert. A change that stays green is a missing test.

This gate is partial. A mutation score can be gamed by asserting on the mutated value instead
of the intended behaviour — the tautological test again — and no tool detects that.

## Reviewer
- **A dependency-rules checker is recorded:** its output replaces your layer-boundary judgment
  in the pattern-consistency step. A violation is CRITICAL — it gets resolved (invert the
  dependency, insert an interface, split the module), not discussed.
- Every gate's output goes into `### Evidence`.
- A rename or split made only to move a score, not to clarify the code → WARNING.
- Heavy, but the plan's hardening phase is unticked or left no trace (no mutants, no
  broken-behaviour runs) → WARNING.
