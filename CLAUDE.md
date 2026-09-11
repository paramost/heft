# Heft — working agreement

Read `docs/heft-handoff.md`, then `docs/heft-decisions.md` in full, before proposing anything. The decision record holds constraints that took a long time to establish; several look arbitrary and are not.

The two rules the rest come from:

- **Whatever the player knows, they should have learned by playing.** Nothing in the interface may lock, hint, or indicate correctness.
- **Nothing is asserted that could be measured**, and the measurement is of the thing itself, not a proxy for it.

## Before starting work

Explain what you intend to do and get agreement first. That covers writing code, editing files, and running measurements — measuring is not free. Say what it would cost and what it would tell us.

A question is not a request to rebuild, and not a request to measure.

List the costs of a change before it is chosen, not after it ships.

## When play and analysis disagree, play wins

Dan tests by playing on a phone. That judgement has been right where confident analysis has been wrong, repeatedly. If a measurement says the drawing is fine and play says it isn't, the measurement is aimed at the wrong quantity.

If something feels wrong, check what was recently taken away before measuring what is still there.

## Shipping

The build string lives in three places: `const BUILD`, the `data-build` attribute on `<html>`, and an HTML comment in `<head>`. All three change in the same commit. Never reuse a number.

Commit and push only when asked.
