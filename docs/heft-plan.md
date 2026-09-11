# Heft — project plan (v2)

**Where things stand:** **v1.5 baseline, build 1.5.12** — a deliberate stopping point, and the
starting point for persistence. Build 1.5.2, deployed from GitHub via Vercel to `heftdaily.com`. 144
boards, selected at random. Proportional tilt, 2.5% bow, 44px weights, adaptive vertical frame. No
persistence and no daily ordering — both were built during v1 and deliberately reverted as
premature.

The 1.4.x builds were structural and visual, not mechanical: the board bank moved to `boards.js`,
the mobile now hangs from a rule under the header, the wordmark hangs from the top of the header,
the header was compacted, and the rule lights on solve. `?ink=N` was added as a fourth testing
parameter. 1.5.0 is the exception that did touch the puzzle: shapes and rack positions are now
shuffled per board, closing a leak that gave away the full ranking of the four weights.

Ordered by what unblocks what, not by effort. **Nothing here is approved. Each item needs to be
explained and agreed before any work — including measurement — begins.**

---

## Phase 1 — deepen the bank

This comes first now, because it changes what every later decision is choosing between.

**Generate a lot more boards.** The five-hook pool has 6,772 qualifying boards already enumerated
and only 96 are shipped. Six-hook is sampled across 18 of 42 skeletons. This is background compute
in `tools/generate.py`, not design work, and it is the prerequisite for both the difficulty curve
and any tightening of the generation constraints.

**Decide whether the leaf-arm imbalance floor goes in.** Measured in v1: applying the 20% floor to
arms whose children are both hooks costs 82% of the shipped bank but still leaves roughly 1,200
five-hook boards in the pool, so at five hooks it is close to free. Six-hook cost is unknown without
a run. It closes the case where a wrong pair sits a pixel off level — and only that case; the same
trap one level up cannot be closed at any price. See the decision record.

---

## Phase 2 — the daily · **next**

All of this was built once and reverted. The design is known; the work is redoing it deliberately.

**Date-seeded selection.** Board from days-since-epoch, so everyone plays the same puzzle on the
same day. Count from the local Y-M-D read as UTC so daylight saving cannot bend the day count.
Decide what happens when the bank runs out — wrapping is fine if the numbering keeps counting.

**Persistence, in `localStorage`, no backend.** Three things: which day you last played, your result
for it, and your streak — **plus mid-board state**, which is not optional. Without it a refresh
erases your rehangs and the day becomes re-rollable. A finished day should come back solved and
frozen.

**Retire the random browse.** Random selection and "Another day" exist because there is no daily.
Once there is one, browsing must write nothing, or it is a way off the daily board. `?board=N` can
stay as a testing pin.

**Fix the result stamp.** `No <n>` is currently a board index and means nothing to a reader. It
should be the day number.

---

## Phase 3 — knowing whether it works

The current feedback loop captures finishers and nothing else. The most valuable number is how many
open the link and never finish a board, and it cannot be reconstructed after the fact.

**Anonymous event logging.** Board opened, first weight hung, each rehang, solved or abandoned.
A Vercel serverless function writing to a simple store. Worth building before sharing widely.

**Four questions worth asking testers**, each tied to something genuinely unknown: did you work out
what to do without being told; did you look at the arm *above* when one arm went level; did the tilt
feel informative or fiddly; was there a moment you thought it was broken.

**Add a fifth now:** does the mobile growing and shrinking as you hang weights read as alive or as
unsteady? New in 1.2 and unanswered.

---

## Phase 4 — open design questions

**Reclaim the 43-unit side pad.** The only lever that makes the mobile bigger — ×1.11 at 22 units,
×1.17 at 10 — since 141 of 144 boards are width-limited. The pad exists so a hook's tap zone stays
inside the element, and hit testing has since moved to a delegated distance test, so it may no
longer earn its keep. Must be tested against a letterboxed phone-sized box before it is believed.

**Balancing weight usage across ranks.** Lighter weights are used more often in solutions
(r = −0.31 against rank). It is a real inference but one that can only be drawn from play, so it
passes the guiding rule in the decision record. Listed so it is not "fixed" without a reason.

**Mixed weight counts.** Some boards four weights, some five. More variety, and it opens 10 of 42
six-hook skeletons rather than 4. But a five-weight rack is a wider search and a different
difficulty, so it wants its own rung rather than being mixed in blind.

**Seven hooks.** Reachable only at five or six weights, about 1 board per 11,000 draws. Expensive
and probably not worth it before the simpler variety is exhausted.

**Difficulty curve — now without a signal.** The original plan was to build it from rehang
counts once persistence existed. Rehangs have since been rejected as a difficulty measure: they
track play style at least as much as the board. Time-to-solve is worse; abandonment is
style-independent but coarse. What remains is structural — search size, how far up the tree
resolution requires you to look, how many arms are ambiguous at once — which is solver-side, and
the wariness about solver estimates was specifically about preferring real play. **Whether the game
needs a curve at all is open.**

**Board generation, rewritten.** `heft-generation.md` is the spec: generate a large pool, record
every property as a column, select afterwards. Fork count is the headline finding - the bank has
one two-fork board out of 144. This is now the main line of work, not Phase 1's original
deepen-the-bank framing.

**A wider tilt range.** `?tiltmax=N` exists and defaults to 15. Widening to 20 would cut invisible
single-weight swaps from 40.6% to 34.6% for about 1.2% of mean scale, but risks the staircase that
got 30 deg rejected. Left as a parameter deliberately: it changes the core feel of the game, it was
arrived at by analysis rather than by anyone complaining, and this project's rule is to distrust
that. Play first.

**A weight-ratio window — now the main generation lever.** Play has pointed at the weight
distribution three separate times. The 1.5 measurements say a **6–12** window is the right shape,
not the 6–25 first proposed: it takes invisible single-weight swaps from 33.3% to 26.9%, where
6–25 only reaches 30.5%. It keeps 56 of 144 boards, which is why it belongs to regeneration rather
than to filtering the shipped bank. Cheap to compute, no generator run needed to evaluate, and a candidate for either a
generation constraint or an ordering axis. **Do not filter the shipped bank on it yet** — it rests
on one measurement and an untested claim about perception. See the decision record.

**Record board properties as columns, not gates.** Whatever Phase 1 generates should carry its
ratio, max torque, leaf-floor pass and any structural difficulty measure alongside each board.
Computing them is arithmetic the generator already does; the value is that every later filtering
decision stays reversible. Filter first and you never see what you removed.

**Colourblind-safe result grid.** Green-to-red is the worst possible axis, and the grid is the part
people paste in public.

**The top of the page is not painted when opened from Messages.** A Safari View Controller
presentation fault, reproduced on a 1KB static page, with no documented web-side fix. Six attempts
failed and are recorded in the decision record so they are not repeated. Left alone deliberately —
the game plays fine, one route in loses the wordmark and the build number. The 1.4 wordmark work
did **not** dissolve it, as had been hoped: the header is what is lost up there, so moving things
into the header moves them into the lost band.

**A copyright notice.** Drafted and skipped in v1 pending the rights-holder's name and confirmation
of the first-publication year. It buys one thing — defeating an innocent-infringement defence — and
only if the name is right.

**An `og:image` for link previews.** Mocked up in v1 from the game's own drawing code, not
implemented. Needs a real PNG at 1200×630 as a second file in the repo, which breaks the
one-self-contained-file property. iMessage caches per URL, so version the filename.

---

## Not doing

**Eight hooks.** Zero valid boards from 111,000 draws across all 429 shapes.

**Anything that locks or hints.** Whatever the interface derives, the player doesn't.

**A nonlinear tilt map as the default.** Measured, built, rejected. It fixes under 1% of readings by
compressing the whole scale. It survives as `?tilt=N`.

**An all-arms imbalance floor.** Not expensive — impossible. Zero of 144 boards survive it.

**A/B against the locking build.** Not possible: `heft-locking.html` no longer exists and cannot be
regenerated. The reasoning is kept anyway — testing both designs against the same people measures
which they saw first, not which is better.

---

## Files

- `index.html` — the game
- `boards.js` — the 144-board bank, one board per line
- `tools/generate.py` — the board generator. Python 3, standard library only
- `docs/heft-decisions.md` — why the mechanics are the way they are
- `docs/heft-generation.md` — the generation spec the generator was written against
- `docs/heft-publishing.md` — how to host and gather feedback

---

## Still true, and now with a second file

The bank split means a cached `boards.js` against a fresh `index.html` renders a header, an empty
stage and the default prompt — a working-looking game with no mobile in it, and nothing on screen
saying why. An on-screen guard when `PUZZLES` is missing is about three lines and has not been
built.

---

## One recurring failure worth naming

Every real bug this session came from a quantity defined in one coordinate space being bounded by
something defined in another, or from a number being asserted instead of measured. Three tap bugs,
a 0.54% scale drift, a box a pixel short of its own ink, a glyph sized from its box instead of its
ink. Anything touching input, layout or scale gets tested against a deliberately letterboxed,
phone-sized box before it is believed.
