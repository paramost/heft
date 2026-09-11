# Heft — handoff prompt

Paste this at the start of a new chat, with `index.html`, `boards.js`, `heft-decisions.md`,
`heft-plan.md` and `heft-publishing.md` attached.

---

I'm building Heft, a daily puzzle game. It lives at heftdaily.com, deployed from a GitHub repo via
Vercel. The current build is **1.5.12**, which is a deliberate stopping point: the game is polished
visually and mechanically, and the next work is **persistence and the daily** (Phase 2 of the plan).

The repo is two files at the root — `index.html` (~24 KB of code, no build step, no server) and
`boards.js` (the 144-board bank, one board per line), and `tools/generate.py` (the board
generator — Python 3, stdlib only).

I've attached the build and three documents: `heft-decisions.md` (why the mechanics are the way
they are, what must not be re-litigated, and everything measured so far), `heft-plan.md` (what
comes next, in four phases), and `heft-publishing.md` (hosting and gathering feedback).

**Read `heft-decisions.md` before proposing anything.** It records constraints that took a long
time to establish, several of which look arbitrary but aren't. Two matter most:

- **Whatever the player knows, they should have learned by playing.** Everything else follows from
  this — including that nothing in the interface may lock, hint, or indicate correctness.
- **Nothing is asserted that could be measured**, and the measurement is of the thing itself rather
  than a proxy for it.

## How I work

Do not start any work before explaining what you intend to do and getting my go-ahead. That covers
writing code, editing files, and running measurements. Measuring is not free — it costs time and
usage, and I want to choose what we spend it on. Tell me what you'd do, what it would cost, and
what it would tell us. Then wait.

A question is not a request to rebuild. If I ask whether something is possible, tell me and stop.

I test by playing on a phone, and my judgement from playing has been right where confident analysis
has been wrong. When they conflict, play wins.

Measure things rather than asserting them, and measure the thing itself rather than a proxy for it.
When a theory fails twice, stop generating theories and build the smallest thing that distinguishes
them.

Say when you don't know, and say when a fix is a guess rather than a diagnosis. Don't offer options
you don't believe in. **List the costs of a change before I choose it, not after it ships.**

Say which population a statistic is over. The same quantity gave 36–42% and 14.3% depending only on
whether partial arms were counted.

## Bumping the build

The build string lives in **three** places — `const BUILD`, the `data-build` attribute on `<html>`,
and an HTML comment in `<head>` — so it can be read without running the page. The script checks all
three agree and prints `· BUILD MISMATCH` beside the build number if they don't. **Bump all three
in the same commit, and never reuse a number.** 1.3.x was skipped deliberately.

## What 1.5.12 ends with

- 144 boards, selected at random on load and on "Another day"
- Tilt proportional to fractional torque imbalance, 15° at full imbalance
- An arm that is not level never draws level: a 1.25° floor on any non-zero imbalance
- An adaptive vertical frame: scale pinned at load, box height tracks the live ink
- The mobile hangs from a rule under the header, which spans the screen and lights on solve
- The wordmark hangs from the top of the header, drawn 1:1 in CSS pixels
- Four weight shapes — star, diamond, triangle, pentagon — **ordered lightest to heaviest**, in
  that rack position, on every board. Nothing states the order; the glyphs share one height and
  their ink areas climb, so it reads as apparent weight and still has to be tested by hanging
  something. **No weight is a circle**, so an empty socket is the only round thing on the board
- Straight arms with pulleys at the corners; the old 2.5% bow is `?bow=0.025`
- The score is **rehangs**, not corrections
- Six testing parameters: `?board=N`, `?tilt=N`, `?bow=N`, `?ink=N`, `?floor=N`, `?tiltmax=N` — all print next to the build
  number when off default, so a screenshot always says which version produced it
- **No persistence, no daily ordering.** Both were built in v1 and deliberately reverted as
  premature; what that work established is recorded in the decision record and the plan
- One known platform bug: opened from Messages, the top of the page isn't painted. Six fixes
  failed, all reverted, all recorded. Don't start there

## Two things nobody has answered

Three need playing, not building: whether `?ink=1` is the right brightness, whether the scrambled
rack costs anything ergonomically mid-board, and whether a wider tilt range (`?tiltmax=20`) still
reads as a mobile on the deepest boards rather than a staircase.

And one thing measured but **not** reported by anyone: 40% of single-weight swaps do not visibly
move the arm they affect, 69% at the top of the tilt range. Recorded in the decision record. Do
not treat it as urgent unless a player raises it.

## The most useful thing to know before proposing anything

Between 1.5.0 and 1.5.11 the shape-to-weight ordering was shuffled, because a fixed ordering looked
like an information leak. It was not a leak — it was the vocabulary the game is played in, and
without it every swap was a blind swap. Play reported this as "the weights don't make a
difference", and hours went into measuring the *drawing* — floors, tilt exponents, tilt ranges,
weight windows — looking for a cause that was never there. **The tilt maths has been unchanged
since 1.2.16 throughout.**

If something feels wrong, check what was recently taken away before measuring what is still there.

## Where we're going

**Phase 2 — persistence and the daily.** Date-seeded selection, `localStorage` with mid-board
state, retiring the random browse, and fixing the result stamp so `No <n>` is a day rather than a
board index. The design is known; the work is redoing it deliberately. Read the plan first.

Nothing in that plan is approved — treat it as a menu, not a queue, and ask me before starting on
any of it.
