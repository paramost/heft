# Heft — project plan (v2)

**Where things stand:** **build 1.11.12** — the daily is live at heftdaily.com. Five weights on
six hooks (the heavy rung), a date-seeded board from an epoch of 15 Sept 2026 (No 1), persisted
in `localStorage` with a streak, shared as a card with a link that unfurls. Anonymous
aggregate logging (opened / first_hang / solved / swap histogram) writes per-day counts to
Vercel KV via `api/event.js`; `api/stats.js` reads them behind `STATS_TOKEN`. A `?practice` URL
gives random boards on the live build for testing. The Light (four-weight) rung is built in the
bank's lineage but deliberately held back until there is real data on the heavy-only form; it
returns as a second board per day when the numbers say a newcomer on-ramp is needed.

Phase 1 is done in the sense that matters: the generator exists, applies the clearance rule it
was missing, and its pools are honest. What it found reshaped the phases below — seven hooks is
closed at this geometry, and the fork axis lives at six hooks.

Ordered by what unblocks what, not by effort. **Nothing here is approved. Each item needs to be
explained and agreed before any work — including measurement — begins.**

---

## Phase 1 — deepen the bank · **done, with findings**

`tools/generate.py` makes pools; `tools/clearance.py` keeps only boards that draw cleanly in
every reachable state; `tools/select.py` picks a bank by score — forks and a forked root count,
each board from a shape discounts the next, lopsided boards capped. Run `--verify` first.

What the pools said, all in the decision record: forks are geometrically scarce, not
under-sampled; a lone hook at the root is the same thing as an unforked root and 28 of 42
six-hook shapes have one; seven hooks with a forked root yields 9 boards in 1,213 at this
geometry; the leaf floor is unaffordable at five values. The deep columns (`invisible_swaps`,
`sub_floor`, `confusable`) have still never been computed over a real pool — about 46,000
states a board at six hooks and five weights — and would inform the next bank.

## Phase 2 — the daily · **done, live in 1.8.0**

Built once in v1 and reverted; rebuilt deliberately and shipped. Date-seeded board, localStorage
persistence with mid-board save, streak on the card from 1 up, random browse retired, the stamp is
the day number. Decisions taken: epoch 15 Sept 2026 (No 1), streak on the card, a missed day
resets. The items below record how it was built.

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

**Decisions to take before building** (raised 13 Sept 2026, not yet taken): the epoch — which
date is No 1; whether the streak goes on the card as a fifth line or stays in the header; and
that a missed day ends the streak. Stage on a branch preview first: a persistence bug erases
someone's streak.

**The light rung.** The four-weight bank (1.5.12's 144, drawn with the first four of the new
glyphs) comes back as a second board per day — Light beside Heavy — rather than a toggle, so
the day's board is never ambiguous. Both banks in one `boards.js`.

---

## Phase 3 — knowing whether it works

The current feedback loop captures finishers and nothing else. The most valuable number is how many
open the link and never finish a board, and it cannot be reconstructed after the fact.

**Anonymous event logging — built (1.7.8–1.8.0).** `api/event.js` increments per-day counters in
Vercel KV (opened / first_hang / solved / swap histogram); `api/stats.js` reads them behind
`STATS_TOKEN`. Counts only, no id/IP. Abandonment = opened − solved. The tester questions below
remain.

**What No 1 taught (15 Sept 2026).** The pipeline was blind on launch day: `STATS_TOKEN` had
been set for Preview and Development only, so Production answered 401 until it was added there
and redeployed. Then three real finishes read back as one - the other two were played on the
branch-preview URL, which was a fully working daily (persistence, streak, a card linking to
heftdaily.com) that logged nothing because only the live hostname logged. Since 1.8.4 every
other host writes the test namespace instead, so a tester on a preview is visible under
`?probe=1` and cannot touch the live counts; and `vercel.json` redirects the production
`vercel.app` alias to heftdaily.com. Read the funnel with this in mind: day 1 on the live
site was 4 opened, 1 first hang, 1 solved. The Upstash credentials are flagged for rotation in
the Vercel dashboard; rotate, then redeploy, then re-probe - a rotated token the function has
not been redeployed with drops every event silently.

**Four questions worth asking testers**, each tied to something genuinely unknown: did you work out
what to do without being told; did you look at the arm *above* when one arm went level; did the tilt
feel informative or fiddly; was there a moment you thought it was broken.

**Add a fifth now:** does the mobile growing and shrinking as you hang weights read as alive or as
unsteady? New in 1.2 and unanswered.

---

## Phase 4 — open design questions

**Seasonal glyphs.** Dan wants festive weight sets for Halloween, Thanksgiving and Christmas,
soon. Same constraints as the regular set — five shapes, a readable lightest-to-heaviest order by
apparent weight, pointed tops so they hang from the cord, distinct silhouettes at 44px — just
themed (pumpkin/bat/ghost…, turkey/leaf/acorn…, tree/bell/star…). A date-driven switch could
select the set, alongside the daily's date logic. The apparent-weight ordering is the hard part,
as it was for the base set; measure the ink, judge on a phone.

**Personal persistence — the ladder.** Everything that makes the game feel like *my* Heft is
built from one record: `hist`, which day and how many swaps, keyed by day number, written on
the first solve of a day since 1.9.4. Keyed by day so that two records — two tabs now, two
devices later — merge by union with no arithmetic. It starts the day it ships and cannot be
backfilled, which is why it shipped before anything that displays it. In order of value per
cost: a stats panel (days solved, streaks, perfects, average swaps, a 0/1/2/3+ distribution)
with milestones on the card; "your N swaps beat X% of today's players", from the swap
histogram logging already collects; a calendar. The countdown shipped in 1.11.0 on the result
card - the card that replaced the share-formatted text as the on-screen result: "Level" in the
wordmark's face over a lit level arm, Swaps and Streak, the circles, Share and My HEFT inside
the card, the record in a line beneath, "Next board in 17m at midnight". Only a swap figure
takes a colour, its worst hook's; the share's score line lost its colons. The transfer shipped
in 1.10.0-1.10.2. First as a link (`?restore=` carrying the packed record, handed to the share
sheet) - which Dan found unintuitive: texting yourself a link is a developer's mental model.
So, a four-digit code: `api/transfer.js` parks the packed record in KV under the code for ten
minutes and hands it back once; the other device types it into My HEFT and gets "Your HEFT is
here." over the merged record. Guesses are capped at ten a minute per address, by a hashed IP
that expires in a minute - the only thing about a person the server ever holds, and the first
time a player's record touches it at all: transiently, with no id. The link path remains as
plumbing. A copy, not a sync. Live cross-device sync is
an anonymous key mirrored to KV — a per-person record, with the size caps, abuse limits and
privacy note that implies — held until the player count earns it. Accounts are not planned.

**The practice URL is a standing feature.** `heftdaily.com/?practice` must always play random
boards on the *current live build*, with a Next button, writing and logging nothing — a way to
test the shipped game without touching the daily or its data. Preserve it through future builds.

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

**Seven hooks.** Closed at this geometry: with a forked root, 9 usable boards in 1,213; 825 fail
at level. Reopening it means longer levers (`--lever-max 7`, measurable, costs scale) or a
smaller weight box. Neither tried.

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
- `icon-2.png` — the apple-touch-icon a link preview shows; drawn by `tools/icon.py`
- `tools/generate.py` — the board generator. Python 3, standard library only
- `tools/clearance.py` — hooks apart, nothing crossing, in every reachable state
- `tools/select.py` — picks a bank from a pool by score
- `tools/geometry.py` — the drawing constants the three share
- `tools/icon.py` — renders the icon
- `docs/heft-handoff.md` — start here: how to work on this, and nothing that can go stale
- `docs/heft-decisions.md` — why the mechanics are the way they are
- `docs/heft-generation.md` — the generation spec the generator was written against
- `docs/heft-plan.md` — this file
- `docs/heft-publishing.md` — how to host and gather feedback

---

## Still true, and now with a third file

The bank split means a cached `boards.js` against a fresh `index.html` renders a header, an empty
stage and the default prompt — a working-looking game with no mobile in it, and nothing on screen
saying why. Since 1.8.4 the page says so - the prompt reads "The board file did not load" and
the script stops - rather than drawing an empty stage. The third file, `icon-2.png`, can go
stale harmlessly; a stale bank cannot.

Also since 1.8.4: a saved board carries a fingerprint of the board it was made on, and a
restore with a different fingerprint drops the board and keeps the streak. Regenerating the
bank is therefore safe for players mid-day (deferred from the 1.8.0 review; built now).

---

## One recurring failure worth naming

Every real bug this session came from a quantity defined in one coordinate space being bounded by
something defined in another, or from a number being asserted instead of measured. Three tap bugs,
a 0.54% scale drift, a box a pixel short of its own ink, a glyph sized from its box instead of its
ink. Anything touching input, layout or scale gets tested against a deliberately letterboxed,
phone-sized box before it is believed.
