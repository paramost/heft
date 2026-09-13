# Heft — decision record (v1.6, build 1.6.12)

A daily puzzle. A hanging mobile with empty hooks and a rack of weights. You never learn what
anything weighs. Fill every hook so the whole thing hangs level. Placing is free; replacing costs
you. Zero rehangs is perfect.

This document records **why** things are the way they are, so nobody has to re-derive it. Several
mistakes in the build sessions came from forgetting a constraint established an hour earlier.

---

## The central idea

**The tilt is the arithmetic.** Every arm's angle is directly proportional to its fractional torque
imbalance — linear, no curve shaping it. The mobile is not illustrating the puzzle, it *is* the
puzzle, and reading it is the whole skill.

This replaced an earlier design where branches locked when balanced. That version answered "is this
arm correct?" at the arm itself, which requires proof, which requires each arm to have exactly one
possible filling — which is the same thing as the arms being independent of each other. Verified: on
that build, all 56 boards could be solved bottom-up with **every step forced**. The tree was
decorative.

Tilt answers the question one level up, where the information already was. That makes the nesting
load-bearing for the first time.

---

## The rule the other rules come from

**Whatever the player knows, they should have learned by playing.** Dan's, 1.5.0. Every other rule
in this section is a consequence of it.

"Nothing locks, hints, or indicates correctness" is the special case: an indicator hands over a
conclusion the player did not reach. The tilt is the pure case in the other direction — it tells
you everything, but only in response to a placement. The rehang counter and the rack's used-dots
show you only what you did.

It is a sharper test than "is this a hint?", because it catches things that were never anyone's
decision. The rack rendered lightest-to-heaviest on all 144 boards, purely because `vals` was
stored ascending — no hint was intended, and the full ranking of the four weights was available
before the player touched anything. It is also permissive where it should be: a pattern you can
only notice by playing many boards is skill, not leakage, and the game should reward it.

Apply it to anything new by asking where the knowledge came from, not how it looks.

---

## Settled — do not re-litigate

**An arm can be level with the wrong weights on it, and that is fine.**
74% of arms can be levelled more than one way. Tilt resolves it structurally — a wrong-but-level arm
has the wrong total mass beneath it, so the arm above must lean.

**Verified exhaustively:** across 2,885 wrong-but-level cases, **zero** leave the mobile level.
Median lean produced elsewhere is 12° of a 15° range; the smallest is 3°; none under 2°.

**Nothing locks and nothing claims correctness.** No ledger, no hints, no correct-arm indicator.
Whatever the interface derives, the player doesn't — the lesson from Probe. The glow arrives only
when the whole mobile hangs level, spreading down from the anchor.

**The weights are ordered, and the rack is sorted to match.** Star, diamond, triangle, pentagon -
lightest to heaviest, on every board, in that position. This is the most important entry in this
section and it was got wrong once already.

Until 1.5.0, `stocks[i] = KEYS[(day*2 + i*3) % 6]` collided on every board and fell back to the
first four keys, so **pentagon was the lightest and triangle the heaviest on all 144 boards** -
and `buildRack` rendered in weight order, so the leftmost weight was always the lightest. Two
independent orderings, both fixed, for the whole life of the game. 1.5.0 read that as an
information leak and shuffled both.

It was not a leak. It was the vocabulary the game is played in. With it gone every swap became a
blind swap: you could no longer move one step heavier on purpose, only guess and look. Play
reported this as "weights not making a difference" and several sessions of measurement went into
the drawing looking for a cause that was not there - **the tilt maths is byte-identical to
1.2.16**. Restored in 1.5.7 (mapping) and 1.5.11 (rack order); the `rng`/`shuffled` helpers are
gone.

**What makes it not a leak, precisely:** the ordering is carried by how the shapes look, not by a
statement. Nothing on screen says which is heavier. The player forms a hypothesis from apparent
weight and has to hang something to test it. It also degrades gracefully - a player who does not
see the cue has lost nothing, where a stated ordering could not fail so quietly.

**The cue is apparent ink area, not compactness.** The four glyphs share one bounding height
(29 units) and one ink top (9.5), and their areas climb across the rack: star 392, diamond 420,
triangle 461, pentagon 609. Compactness was the original theory - 4*pi*A/P^2 - and it agrees at
the ends but **puts the triangle second and the diamond third, which play says is backwards**.
1.5.9 narrowed the triangle to force compactness to win; 1.5.12 reverted it. Do not re-derive the
order from compactness.

Equal *area* was tried in 1.5.7 and reverted in 1.5.8: height and area cannot both be equalised
across different shapes, and height is what the eye checks in a rack. The star keeps a 0.52
inner/outer ratio rather than 0.50 because thin points read lighter than their ink; 0.54 makes its
area pass the triangle's. The pentagon is deliberately not trimmed - at a fixed height, reducing a
pentagon's area also reduces its compactness, and it leads both.

**Do not strengthen the cue.** Exaggerated, apparent weight stops being a perception and becomes
the label this design avoids.

**The remaining rank signal is left alone deliberately.** Lighter weights are used more often in
solutions: rank 0 appears twice in 66 of 144 boards, rank 3 in only 9 (r = −0.31 against rank).
So "I have placed this one twice, so it is probably not the heaviest" is a real inference — and it
**passes** the rule above, because you cannot make it without having played. Shuffling cannot
touch it; only a generation constraint could. Do not close it without a reason better than
symmetry with the rack fix.

**Straight arms, and pulleys at the corners.** 1.5.5. The 2.5% bow is off by default; `?bow=0.025`
restores it. It carried no information and cost a great deal: about **5.7 deg of slope at each arm
end, 4.6x the entire 1.25 deg floor**, competing with the only thing an arm has to say. It was also
incoherent - the apex sat at the chord's midpoint regardless of the anchor, so on a 3:1 arm it
arched over a point a whole unit off the thing holding it up. Dan's observation, and correct.

Straight arms meet their risers at a true right angle, so the ends are now 4.5-unit **pulleys**:
an outlined wheel with a hub, sized between the 1.8-unit lever dots and the 15.5-unit socket. The
arm stops at the wheel's edge and the riser leaves its bottom, so the wire runs over the wheel
rather than through a corner. Chosen over a fillet because it spends none of the arm's length on
curvature - which matters most on the 53px arms, where a fillet would have consumed 40% of the
line - and because a pulley is a thing the object would actually have. They light with the arm.

**A physically accurate bow is not an option and was never on the table.** A real loaded arm's
tips deflect by different amounts, so a *balanced* arm would not draw horizontal. That destroys
the one invariant the game rests on. Only stylisations are available; the question is how much
curvature, not how accurate.

**An arm that is not level never draws level.** 1.5.3-1.5.4. Below about 1.25 deg the tilt used
to render as nothing, so 3.58% of complete-arm readings said "level" while being wrong - the one
thing this design refuses to do. `?floor=N` sets a minimum lean in degrees for any non-zero
imbalance; default 1.25, `?floor=0` restores 1.5.2. Nothing above the floor moves.

**The threshold is angular, not in pixels, and this was measured the wrong way first.** The floor
shipped in 1.5.3 as a per-arm minimum *pixel* throw, on the reasoning that pixels are what the eye
sees. Play said otherwise: board 122's 53px arm was readable at 1px (1.09 deg) while board 27's
140px arm was not readable at 1.5px (0.61 deg) and was at 3px (1.23 deg). Two arms differing 2.6x
in length, one threshold at about 1.1-1.2 deg. The eye judges an arm's slope against the risers
and arms around it, and that comparison is angular. Pixels were the proxy; the angle is the thing.

**The floor costs almost nothing in ambiguity.** Measured over 6.64M single-weight swaps on
complete boards: 40.4% of swaps already produce no visible change in the arm they affect, and the
floor moves that to 40.6%. It converts 3.58% of *false* readings into ambiguous ones, in a drawing
that is already ambiguous forty times more often elsewhere.

**A measurement that misled for several hours, recorded so it is not repeated.** Bounding boxes
were used to judge glyph size in 1.5.2 and the four were called consistent because their widths sat
within 6%. Their **ink areas differed by 51%** - the pentagon had half again the star's. This is
the decision record's own named failure (a glyph sized from its box rather than its ink) made again
while the entry was on screen. Measure the ink.

**Four shapes, one per weight.** 1.5.2. The ring was dropped: an empty socket is a circle, so a
circular weight was the one shape guaranteed to be confusable with the thing it hangs on. No weight
is round now, which retires that ambiguity rather than leaving it untested. The star was redrawn as
a five-pointer (outer 16, inner 8) replacing an eight-pointed burst. Ink widths now sit within
1.7 units of each other - pentagon 29.4, star 30.4, diamond 30.8, prism 31.2 - where the old star
was 35.8 and was the glyph the 44px weight size was constrained by. At the bank's closest hook pair
the tightest clearance improves from 11.2px to 15.4px.

**The shapes are pointy-topped for a reason.** The cord stops at the glyph's ink via `CELL_TOP`, so
a flat-topped shape meets the cord along an edge and reads as resting on it rather than hanging
from it. That constraint is why diamond and pentagon are similar - the same requirement producing
the same answer - and the star and triangle carry the differentiation.

**With four shapes and four weights the set no longer varies board to board.** Only the
rank-to-shape mapping and the rack order shuffle. Nothing leaks, but shape identity is now constant
across the bank.

**The `crescent` glyph drew nothing.** 1.5.1. its two arcs were identical -
`a13 13 0 1 1 0 26` down, `13 13 0 0 0 0-26` back - so the outline enclosed zero area. It had never
reached a screen, because the old shape formula `KEYS[(day*2+i*3)%6]` collided at i=0/i=2 and
i=1/i=3 on **every board**, so the duplicate check fired every time and the rack was always
pent/ring/star/prism. The bank's shape variety was entirely illusory until 1.5.0 exposed it.
Removed rather than repaired: a crescent anchored on the box's centre line is narrow, off-centre
and circle-like, and the ring-versus-socket confusion it would have joined has since been
removed outright. Verified all 144 boards render four distinct glyphs.

**Cap dots leak nothing.** `cap` is per board, not per weight — 2 on 122 boards, 3 on 22 — so every
weight shows the same number of dots.

**The score is rehangs, not corrections.** Renamed in 1.4.7. The count is `touches - 1` per hook:
it counts hanging a weight where one already hung. It does not know whether you fixed a mistake,
changed your mind, or were probing deliberately, and calling it a correction claimed knowledge the
interface does not have - in a game whose whole stance is that nothing tells you you are wrong.
To heft is to lift something to judge its weight; a rehang is picking it up again.

**Two honest signals.** An arm is tipped or it isn't; the whole board glows or it doesn't. Level
arms also draw at full stroke weight, which marks *exactly* level against *nearly*.

**Nothing moves except in response to you.** There was an idle sway; raising it to visibility made
it wrong, because constant motion contradicts a game about reading level as a fixed state. The tilt
spring snaps to its target rather than easing asymptotically. The adaptive frame (below) resizes
only in response to a placement.

**15° range, with a 20% imbalance floor.** 30° reads beautifully on one arm but a five-unit lever
throws its end 55px, and three levels of that collapses into a staircase. 15° halves the throw.
Boards are generated so **no wrong arrangement sits closer than 20% off** — at least 3° of lean.

**Partial arms tilt too.** An empty hook is genuinely zero mass, so one weight against nothing
really is a total imbalance. Suppressing that until an arm was full made the board silent for up to
5 placements of 6.

**Generate backwards, from levers to masses.** Forward generation produced 1 board per 400,000
draws; backwards produced 63 per 5,500.

**No symmetrical arms.** A 1:1 arm balances with any matching pair — 3.29 ways versus 1.22
elsewhere. Players balance them correctly, get no response, and conclude they're wrong.

**The bow scales with arm length — 2.5% of the arm.** A flat 4px bow made a short arm three times
more curved than a long one. See the correction to this entry under *Measured in the v1.2 session*.

**Tree shapes are enumerated, not hand-picked.** 14 skeletons at five hooks and 42 at six;
exhaustive enumeration over every five-hook skeleton and all 104,976 lever combinations yields
6,772 qualifying boards. Six hooks is sampled across all 42.

**Depth is a free dimension, and the deep shapes fit a phone better.** Depth-3 boards are 0.75
height-to-width, depth-4 are 1.01, depth-5 are 1.07.

**Sibling subtrees must clear each other entirely.** A looser test that only checked hook collisions
let arms cross straight through one another.

---

## Settled in the 1.6 session (five weights) — do not re-litigate

**The live game is the heavy rung: five weights on six hooks, shipped alone for feedback.**
Dan's framing: the four-weight game was easy mode, and a daily needs depth. 1.6.6 replaced the
bank rather than adding a selector, because a selector built before the daily would have to be
rebuilt around it. The four-weight bank comes back beside it as the light rung when the daily is
built — two named boards a day, not a toggle, so "today's board" stays unambiguous.

**Five glyphs, all regular polygons: diamond, triangle, hexagon, pentagon, house.** Lightest to
heaviest by ink area — 420, 438, 546, 609, 652 — on a shared 29-unit height with the cord meeting
the ink via a per-shape `CELL_TOP`. Every polygon has equal sides *and* equal angles: a hexagon
with equal sides and uneven corners looked wrong at 44px, and "regular" was chosen over
"square" once it was clear a hexagon cannot be regular, 29 tall and 30 wide — only two of those.
Consequences the eye has to accept: the triangle is equilateral at its shipped width, so 27.5
tall (ink top 10.23); the regular hexagon is 25.1 wide, the narrowest in the rack by four units,
and reads tall next to shapes that are all wider than tall. That was looked at three times and
kept. The house is the one shape that is not a regular polygon; it is the only one with vertical
edges. The star is gone: it was the shape carrying the differentiation against the triangle, and
this set differentiates by side count instead.

**Flat tops were tried and play chose against them.** 1.6.1 turned the set over — flat tops,
points down, the square in for the diamond — on the argument that the empty socket is a thin
circle the cord meets at its edge, so a weight meeting the cord the same way was the consistent
reading, not the odd one. Both sets shipped behind `?glyphs=` for the phone to compare, and the
pointed set won. It stays the default; `?glyphs=flat` keeps the other. The argument was sound and
the eye disagreed, which is the rule.

**The score is swaps, counted in the sockets.** The count is what it was as "rehangs" since 1.4.7
— hanging a weight where one already hung; zero is perfect — with two changes. The word: Dan
could not live with "rehang". And the rule is now taught by the hook: every empty socket shows
how many times something has hung there, which is what hanging there now will cost. A fresh
board says 0 everywhere, a lifted weight leaves a 1 behind, and the card's circles at the end
are a picture of those numbers. It passes the root rule — the socket says only what you did —
and it makes the scoring explain itself without a word of instruction. Known and accepted:
exchanging two hung weights costs two.

**Scoring by attempts was built and set aside.** An attempt is a full board; the score is how
many readings it took; the card is one row of arm marks per reading. It charges for the wrong
idea rather than for how many hooks the idea touched — which rehangs get wrong, and the record's
own numbers showed it: scores clustered at 0, 4 and 6, the shape of "rebuilt a branch". It lost
on the card: rows of arrows need a legend, and Dan could not read them without one. The per-hook
circles tell the story of the struggle and need no explanation. The branch `attempts` holds the
work at 1.7.1 in case it is wanted.

**The share is a share sheet, with the address as the last line of the text.** `navigator.share`
where the phone has a sheet, the clipboard elsewhere and at the same moment, so a paste always
works. Chrome on iOS was seen handing Messages only the page link when the share carried a `url`
field; the address as the last line of the text — with its scheme, or Messages will not unfurl
it — puts the card first and the preview beneath it. `icon-1.png` (180×180, drawn by
`tools/icon.py`) is the apple-touch-icon that preview shows; iMessage caches a preview per URL,
so a new design is a new filename. The title is HEFT, in caps.

**The wordmark's risers reach the letters, and the H hangs from its crossbar.** From 1.4 to
1.6.1 the risers stopped 5px short: the layout measured the letters with `getBBox()`, which on
SVG text returns the *font's* box — 25.8px for a 19.4px face whose capitals are 14px. A glyph
sized from its box, in the code written to avoid exactly that. The ink is now measured with
canvas `measureText`'s `actualBoundingBox*`, and each riser stops where ink begins on its own
column, found by drawing the letter and scanning down — which is what puts the H's cord on its
crossbar rather than in the gap between its stems. The face is 22px, from 19.4.

**The arms glow again.** The lit stroke on a level arm ran through the `#warm` blur, and a
filter's region is sized from the bounding box of what it is applied to: a level arm is a
horizontal line with no height, so the region was empty and the glow rendered as nothing — at
exactly the moment the arm settled. Straight arms (1.5.5) took the light away; the bow had been
giving the path its height. Nobody noticed for seven builds. The lit stroke now sits in a group
with two invisible ticks at the arm's ends, so the group has height and the blur has a region —
and it uses the weights' `#bloom`, so a solved mobile glows with one light. The vertical cord
from the ceiling does not light — Dan's call; the ceiling and the arms are the level surfaces.

**The header's gaps are measured from the ink, from the band's edge.** The H's left gap had been
measured from the mark's origin, which sat 12px inside the band — invisible while the mark was
drawn for a content column, plain once the header went edge to edge. The H is now 22.3 from
top, bottom and edge; the meta's ink — cap top, last baseline, widest line — is 12 from top,
bottom and edge, from 9.1px of header padding (its ink sits 2.9px inside the line box at both
ends). The header is 60.6px, from 53.4. The lit rule's glow is clipped to the header's width:
a blur bleeds sideways, which showed on an iPad and not on a phone.

**The result block's four lines sit on one 22px pitch**, the emoji row 6px further from the date
because emoji are taller than text.

---

## Measured in the v1.2 session

Everything here is measured over the shipped 144 boards, usually across every reachable state —
each hook empty or holding a weight, caps respected, about 5,553 states per board.

**The 20% floor is a property of complete arrangements, not of arms.** It guarantees that any full
wrong filling leans somewhere. It says nothing about the arm you just filled, and mid-play the arm
above is already pinned at full lean by its empty hooks, so the parent cannot resolve anything yet.
Across 3.6 million non-level arm readings, **0.79% draw under 1px** end to end and **2.28% under
2px**. A concrete case: board 26, the two middle weights on the 2:1 arm, 40 against 45 — 5.9% off, 0.88°,
**1.02px** between the arm ends.

**Extending the floor to cover this is not expensive, it is impossible.** 34% of all reachable
states have some arm sitting in the 0–20% band, and every one of the 144 boards has some; the
cleanest still has 10%. Survivors of an all-arms floor: **0 of 144**, at every threshold tried.
With thousands of torque ratios per board, some will land in any narrow band you name.

**Only a leaf-arm floor is affordable, and it fixes only the bottom rung.** Restricting the
constraint to arms whose two children are both hooks, at the same 20%: 34 of 144 survive (18% of
five-hook boards, 35% of six-hook). That still leaves roughly 1,200 five-hook boards in the 6,772
pool, so at five hooks it costs nothing you'd notice. Six hooks is sampled, so its cost is unknown
without a generator run. **Not implemented in v1.**

**The bow's ratio to the lean is fixed and length-independent:** sag / lean = 0.025 / sin(15° × f).
The bow equals the entire lean at **9.6% imbalance**, on every arm regardless of length. At the 20%
floor that ratio is 0.48 — which is exactly the 0.48 in the old record entry. **That number was
never a fact about the drawing; it was the generation floor restated**, and it only holds where the
floor holds. Mid-play the bow exceeds the whole lean in **3.9%** of non-level readings. The bow
carries no information — it is a constant — so it cannot mislead, but it sits on top of the one
quantity being read, and a level arm is a symmetric arc rather than a horizontal line.

**A nonlinear tilt map was built, measured and rejected as the default.** `|f|^0.5` removes the
sub-pixel band completely (0.00% under 1px, 0.01% under 2px) and leaves the 2.40% of readings that
are *exactly* level untouched. Its cost is the whole scale: the spread from a quarter-wrong to
entirely-wrong compresses from 11.3° to 7.5°. Proportionality was kept. **Retained as `?tilt=N`.**
`0.8` is the middle: 0.88% under 2px, 10.1° of spread.

**Strengthening the level mark would amplify a signal that is often not about correctness.** The
mark fires on 5.0% of full-subtree readings, and **34.6% of those firings are on wrong contents**
(20.5% on leaf arms). That is by design — the parent resolves it once the board fills — but the
louder the mark, the more it reads as *right* rather than *level*. Left as it is.

**Glyph ink is 36 of the 48-unit box at its widest**, not 48. The closest two hooks anywhere in the
bank, at any tilt, are 44px apart (board 108). At **S = 44** the widest glyph draws 33px, leaving
11px of clearance, and its half-height of 16.2px (18.6px at the peak of the solve pulse) stays
inside the box's 21-unit bottom reserve. 48px would also fit, with 8px.

**141 of 144 boards are width-limited.** Their scale is set by the stage's width, not its height.
Consequences: reclaiming vertical space does not enlarge the mobile (×1.027 at best), and the
43-unit side pad — 19–28% of the box — is the only lever that would (×1.11 at 22 units). The pad
exists so a hook's tap zone stays inside the element; hit testing has since moved to a delegated
distance test, so it may be reclaimable, but that is the coordinate-versus-pixel boundary that has
produced three tap bugs and it must be measured before it is touched.

**Hanging the mobile from the wordmark is blocked by the cord's position, not by the fit.** Board
x = 0 lands anywhere from 54px to 309px across a 366px stage; only 6 of 144 boards put it within
10px of centre. Pinning the cord to centre costs 25% of the mobile's scale (41% worst case).
Sliding the mark to meet the cord needs 254px of travel in a 366px header. The only version that
works is letting the *attachment point* move along an arc that spans the stage, with the letters
fixed — zero width penalty, no mark travel, and the mark does not grow, so it avoids the rack
squeeze that killed the first attempt. **Not built, and now not needed** — see *The header is the
ceiling* below. The measurement stands; the problem it was measuring was routed around rather
than solved.

---

## The header is the ceiling (1.4.1 - 1.4.6)

Dan's idea, and it dissolves the problem the wordmark measurement above was stuck on. The floating
`M-34 -38H34` ceiling bar is gone. The rule under the header is the ceiling, and the cord runs from
the top of the viewBox to meet it.

**Why it works where pinning to the wordmark did not.** Board x = 0 lands anywhere from 54px to
309px across the stage. A cord must meet a *point* on the mark, which costs either 25% of the scale
or 254px of travel. A line across the header's full width has no particular x, so the cord meets it
wherever it falls. Nothing is pinned and nothing travels.

**The join is exact, not approximate.** The viewBox's min-y is fixed at -44 and `reframe` sets the
stage height to exactly `h × k`, so the rendered scale is `k` and there is no vertical letterbox.
The anti-thrash gate's slack lands at the *bottom* of the box, never the top. Checked across all
144 boards on a 390×844 phone: zero gap above the cord, worst case 0.0000px.

**It buys no scale.** 141 of 144 boards are width-limited, so this is appearance, not size.

**It does not fix the Messages bug.** The header is what is lost up there, so the ceiling is lost
with it. No worse than before; no better.

**The risk that remains:** the header is `position:sticky`. Nothing scrolls today, but a ceiling
attached to a sticky element is a ceiling that can slide.

**The wordmark hangs from the header's top edge**, so every element on the page hangs from
something above it. The arc is gone; four risers run from y = 0 down to the letters, at the
mobile's cord weight and opacity so they read as the same kind of line.

- Drawn **1:1 in CSS pixels**. The old mark was a 340×74 drawing rendered at 132px — a 0.388 scale
  factor between it and the layout it now has to meet. That is the coordinate boundary that caused
  every real bug in v1, so the rewrite deleted the factor rather than adding a second one.
- **Absolutely positioned**, so it cannot feed back into the height it is centring inside. The meta
  block alone sets the header's height.
- The letters are centred on **measured ink**, not the text box, and the H's left gap is set equal
  to the top and bottom gaps — 19px each at the current 53px header. Sizing a glyph from its box
  cost v1 real time; the same mistake was available here and avoided.
- The body's top padding moved onto the header, so the header reaches the top of the page and the
  risers do not terminate in mid-air. Nothing below moves.

**The header centres on wide screens** (1.5.6, fixing 1.4.9). Taking the rule to the screen edges
used `align-self:stretch`, which overrides the body's `align-items:center`. On a phone the content
box is narrower than the 454px cap so it stretched edge to edge and looked right; on an iPad it
capped at 454 and sat hard left while the stage stayed centred. Now `align-self:center` with
`width:calc(100% + 24px)`. **Same class of bug as the boards.js silent failure: correct on the only
device being tested, wrong everywhere else, with nothing on screen to say so.**

**The rule spans the screen, not the content column** (1.4.9). The header keeps the 430px column
for its contents, via negative margins with matching padding, so nothing inside it moved. The
header's background reads as an edge-to-edge band, so a rule stopping 12px short of it looked
like it was failing to span.

**The rule lights on solve**, together with the cord from ceiling to root arm, revealing top-down.
Lit, it reaches a level arm's stroke weight and colour exactly — thickened downward with a solid
`box-shadow` rather than a wider border, so the layout does not shift when it fires.
This fires only on `boardProved()` — the signal the player already has — so it does not violate the
rule against indicating correctness. Without the cord lighting there is a dark gap between a lit
ceiling and a lit mobile. It retires the moment a weight comes off, like the Copy button.

**The header was compacted from 78px to 53px** across 1.4.3 - 1.4.4, in padding and leading rather
than by removing content. The meta now reads as the shared result does — the same `stamp()`, the
same U+2022 bullet — so the header and the clipboard cannot disagree. The rehang count turns
`--rest` orange above zero, the number only. The build line moved below the buttons.

**`?ink=N` lifts the wire off the background** (1.4.8): brightness and stroke weight only. **0 is
exactly the 1.4.7 drawing, 1 is the default, 2 is the ceiling**, and it prints beside the build
number when off default. At 1 the wire goes `#4d59a6` → `#7680bf` and strokes scale ×1.20; node
dots scale by √1.20, since a dot is all fill and scaling it linearly overpowers the lines.

**No opacity is touched by `ink`, and that is the point.** A level arm draws at full stroke and
full opacity where a leaning one draws at 1.6 and 0.7 — the level mark is carried by opacity as
well as weight, and lifting the floor would flatten a real signal to gain brightness. Brightness
comes from colour and weight only.

---

## Measured in the 1.6 session

**The generator was missing a settled constraint, and the pool was 78% unusable.** The v2 spec's
hard-constraint list dropped "sibling subtrees must clear each other entirely" and `generate.py`
was written to the spec, so a six-hook pool of 6,889 boards had hooks drawn on top of each other
and risers running through weights. The check is `tools/clearance.py`, now applied at generation:
hooks no closer than the shipped bank's worst, and no line entering the 44-unit box of a weight
it does not hold — the box, not the ink, because a line ends in a 4.5-unit pulley and board 16
of the 1.6.0 bank had one sitting on a square. Over **every reachable state**, not at level and
not at tilt corners: an arm is only at full tilt when one side of it is empty, so the corner
search over-counts, and its role is only to find which pairs need the enumeration.

**Two findings about the shipped 1.5.12 bank, from the same check.** The record's "closest hooks
44 units at any tilt" was measured at level; over reachable states the worst is **37.3** (board
51), and that is the threshold now. And **board 66** has a hairline arm-on-arm touch with
weights on hooks 3 and 5 only — reachable, never reported.

**Seven hooks with a forked root is closed at this geometry.** 1,213 root-forked seven-hook
boards, 9 usable: 825 fail at level. Two subtrees with two hooks each under one root need more
room than levers of 1–5 at 22 units give them once the 44-unit box takes its share. What would
reopen it — longer levers (wider mobiles, smaller scale) or a smaller weight box — is
measurable and not done.

**Three forks needs eight hooks, not seven.** The spec said seven. Max forks by hook count: 5→1,
6→2, 7→2, 8→3. Seven hooks buys twenty two-fork *shapes* against two at six; not a higher peak.

**Forks were scarce for a geometric reason, not a sampling one.** The spec blamed the bank's one
two-fork board on sampling and prescribed selecting across topologies. The cleared six-hook pool
has two-fork boards at 0.6%; the shipped bank had them at 0.7%. Same rate.

**A lone hook at the root is the same thing as "the root is a fork," and 28 of 42 six-hook shapes
have one.** Filling shape slots evenly (the spec's rule) turned that into a bank 69% lopsided.
Banning it keeps 14 shapes and draws ~17% smaller. The picker is now scored: forks and a forked
root score, each board taken from a shape discounts the next, lopsided boards capped at a
third. The 1.6.4 bank: 29 chains, 101 one-fork, 14 two-fork, 37 shapes, at most 10 per shape.

**Five weights draw smaller.** Weights at the median board: 39px on the shipped bank, 35px on
1.6.4. Honest clearance and forked shapes both cost width, and 141 of 144 boards were already
width-limited. Judged on the phone and accepted.

**The leaf floor is unaffordable at five values**, as the spec predicted for stacking: 25 leaf
pairs instead of 16. Six percent of the pool passes it.

**Backwards generation yields one board per ~30 draws at six hooks and ~360 at seven** — thirty
times the record's 1 per 11,000 — before clearance. After clearance, one per ~650 at six hooks.

---

## Measured in the v1.5 session

**No board in the bank is fully honest, and none could be.** Zero of 144 have both no readings
below the floor and no invisible single-weight swaps. The best board still has **15.4%** of swaps
invisible; the median is 35.1%, the worst 53.8%. Relaxing to "under 5% of readings below the floor
and under 20% of swaps invisible" keeps 8 boards. **This is not a selection problem.** Any arm
carrying a subtree has thousands of reachable torque values crammed into one 15 deg range, so some
always land within a degree of each other. No choice of four weights avoids it.

So full honesty was never available, in v1 either. What *is* honest, and now fully so, is the two
claims the game actually makes: **level means level** (guaranteed by the floor) and **more wrong
looks more wrong** (guaranteed by monotonicity). It does not promise to show *how much* more wrong.
Stop treating the invisible-swap rate as a defect to eliminate; it is the resolution limit of a
15 deg dial.

**Weight spacing, not just spread, can make two weights interchangeable.** Board 68's values are
4, 8, 80, 125 - adjacent ratios 2.00, 10.00, 1.56. On its 2:1 leaf arm, swapping 80 for 125 against
either light weight changes the arm by 0.2-0.5 deg, under the 1.25 deg threshold. Two of four
weights are interchangeable there. Found in play, not by measurement.

**But spacing does not predict the problem across the bank.** Smallest adjacent step correlates
only **+0.19** with confusable substitutions; max/min ratio correlates **+0.57**. Board 66 has the
widest spacing in the bank (step 3.00) and is second-worst for confusability. The mechanism in
every worst case is a small weight swapped for another small weight while a large one sits
opposite - top-of-range crowding again, not tight spacing. 101 of 144 boards have at least one
confusable substitution; 4.0% of leaf-arm substitutions on average.

**The two ends trade against each other roughly two-for-one, in favour of tighter weights.**

| weight ratio | boards | invisible swaps | readings needing the floor |
|---|---|---|---|
| 0-6 | 11 | 26.9% | 7.70% |
| 6-12 | 56 | 26.9% | 5.65% |
| 12-25 | 43 | 35.2% | 3.59% |
| 25-50 | 19 | 39.5% | 2.96% |
| 50+ | 15 | 48.3% | 1.86% |

A collapsed reading is merely ambiguous and the floor already handles it; an invisible swap is the
thing play has now run into three times. **The 6-25 window proposed in the v1.4 session is the
wrong shape** - it only moves invisible swaps 33.3% to 30.5%. A **6-12** window reaches 26.9%, and
keeps 56 boards rather than 99. That is a much heavier cut than previously recorded, and it is why
this belongs to Phase 1 regeneration rather than to the shipped bank.

**40% of single-weight swaps do not visibly move the arm.** Over 6.64M swaps, using the 1.25 deg
threshold play established. Split: away from the top of the range, 32.3% invisible; at the top,
**69.2%**. That is board 97's frustration quantified - not "I cannot fix this arm" but "I cannot
tell whether what I did helped". **Nobody has complained about it.** It is a number, not a
reported problem, and it is recorded here so it is not rediscovered and treated as urgent.

**The tilt exponent cannot fix the top end.** Sweeping 1.0 to 2.0 with the floor in place moves
invisible swaps only from 40.6% to 43.7%, and the top-end figure stays pinned near 70% at every
exponent and every range. Raising the exponent relabels which readings count as top-of-range
rather than making them distinguishable. Resolution is conserved; this confirms it empirically.

**Only the range helps, and roughly linearly.** Invisible swaps: 40.6% at 15 deg, 36.7% at 18,
34.6% at 20, 32.5% at 22, 30.1% at 25. The scale cost is smaller than expected - 20 deg costs
1.2% of mean scale and leaves 104 of 144 boards untouched, because they are width-limited. What
protects 15 deg is not size but the staircase: 30 deg was rejected because a five-unit lever
throws 55px and three levels of that stops reading as a mobile. At 20 deg it throws 37.6px.
**Unresolved, and deliberately left as `?tiltmax=N` rather than shipped.**

**The 70% at the top is not fixable by any mapping.** An arm leaning hard is one where a single
swap changes the torque ratio very little. Only different weights would change it - the ratio
window - which is the expensive, irreversible lever.

**Three measurement errors in this session, recorded because the pattern repeats.** A per-arm
pixel floor built on a proxy when the quantity was angular. A claim that the top end was "3.4x
more ambiguous" that was comparing how many readings sit in a band, not how ambiguous they are.
And a per-arm nearest-neighbour ambiguity measure that returned 100% in every band - degenerate,
because thousands of states are packed into 15 deg, so every state always has a close neighbour.
The measure that finally meant something was the one shaped like the player's actual move: swap
one weight, did the arm visibly change.

---

## Measured in the v1.4 session

**Weight ratio governs legibility; max torque does not.** A tester proposed bounding
`MAX(weight × distance)` so a board could be solved by mental arithmetic. Measured across the same
3.6M-reading enumeration: log(max torque) correlates **+0.14** with the share of readings at ≥0.9
imbalance and **+0.21** with the share drawing under 1px. It is orthogonal to what a player can
see, and it is not a proxy for weight spread either (**+0.18** against log ratio).

**The weight ratio — max/min of `vals` — correlates +0.96** with the share of complete-arm readings
at ≥0.9 imbalance, and **−0.28** with the share drawing under 1px. Two failure modes at opposite
ends of one axis:

| ratio | boards | ≥0.9 | under 1px |
|---|---|---|---|
| 0–6 | 11 | 0.0% | **3.08%** |
| 6–12 | 56 | 3.7% | 1.87% |
| 12–25 | 43 | 14.1% | 1.19% |
| 25–50 | 19 | 26.7% | 1.10% |
| 50+ | 15 | **35.7%** | 0.87% |

Squeeze the weights together and wrong arms whisper — over twice the bank's average rate of
sub-pixel leans. Spread them apart and a third of every complete-arm reading sits in the top tenth
of the range, where the tilt distinguishes wrong from level but not one wrong state from another.
A window of roughly 6–25 keeps 99 of 144 boards. **Not applied.** It is one measurement plus an
untested theory about perception, and filtering the bank is not reversible.

**60% of all non-level readings come from partial arms**, which sit at or near full tilt by
construction because an empty hook is genuinely zero mass. Any statistic over all readings is
mostly measuring emptiness. Restricted to complete arms the top-end share falls from 36–42% to
**14.3%** overall. Both numbers are correct; they answer different questions. Always say which.

**Neither end can be generated away entirely.** The bottom is the all-arms floor, already proved
impossible — 0 of 144 survive at every threshold. The top is empty hooks, which are the design
telling the truth. And the two ends are joined through the tilt map: with a fixed 15° range,
resolution is conserved, so `?tilt` moves it between the ends rather than creating any. The
achievable version is a leaf-arm floor at the bottom and a ratio window at the top.

**Rehangs are not a difficulty measure.** Dan's call, and it retires the plan's stated basis for
the difficulty curve. The count measures play style at least as much as the board: a player who
reasons the whole board out before touching anything scores zero on a board that took them ten
minutes, and a player who probes scores six on one they found easy. Time-to-solve is worse.
Abandonment is style-independent but coarse. This leaves the curve without a real-play signal, and
leaves open whether the game needs a curve at all.

---

## Current state — 1.6.12, the baseline for Phase 2

**What is live, at heftdaily.com:** 144 six-hook five-weight boards, the pointed glyph set,
swaps counted in the sockets, a share sheet with the address unfurling beneath the card, the
wordmark and arm glow fixed, the header measured. Three files deploy: `index.html`, `boards.js`,
`icon-1.png`. `tools/` holds the generator, the clearance check, the picker and the icon
renderer, none of it served. The paragraphs below describe **1.5.12** and are kept as the
history of how the drawing got here; where they disagree with the entries above, the entries
above win.

**1.5.12 was a deliberate stopping point.** The game is polished visually and mechanically; what it
lacks is persistence, the daily, and any measurement of whether people finish a board. Those are
Phase 2 and Phase 3. Nothing below is expected to change while that work happens, and a change to
any of it should be a decision rather than a side effect.

Two files deployed from GitHub via Vercel to `heftdaily.com`: `index.html` (~33 KB of code) and
`boards.js` (the 144-board bank, ~42 KB, one board per line). `tools/generate.py` is in the repo
but not served.

- **144 boards** — 96 at five hooks, 48 at six
- **Selection is random** on load and on "Another day", never the same board twice running.
  `?board=N` pins one. Ordering waits for the daily.
- Drawn from **14 five-hook skeletons** (all) and **18 six-hook skeletons** (of 42)
- Depths 3, 4 and 5 — 49, 62 and 33 boards
- Four weights per board, all used in the solution; shape-to-rank mapping fixed and the rack
  sorted lightest to heaviest, on every board
- Every board: unique solution, no symmetrical arms, nothing crossing, 20% imbalance floor
- Score is rehangs — hangs minus hooks
- Geometry: 22px per lever unit, 56px between arms, 30px riser, **44px weight glyphs**, 15° range
- Weight ratios in the shipped bank run from 3.4 to over 60; median band is 6–12

**The adaptive vertical frame.** The scale `k` is pinned once at load, from the stage width and
from the tallest the board can ever get (every arm thrown to full tilt — a cheap tree walk). It
never changes again while the board is up, so **no lean ever changes size mid-play**. Each frame,
only the viewBox's height and the stage element's height follow the live ink. Two rules make it
safe, and both were added after a measured failure:

- The stage height is derived from the *already-rounded* viewBox height. Rounding them
  independently let the scale drift 0.54% — precisely the failure the design existed to prevent.
- The anti-thrash gate is one-sided: the box grows immediately and shrinks lazily, so it is never
  too small, only ever a pixel too generous. A symmetric gate left a hook outside its own box on
  seven boards.

Reclaims 107px median on a 390×844 phone (405px fixed → 298px median), growing up to 70px mid-play
and never exceeding the old fixed height. The 80-unit bottom reserve is gone, replaced by a live
`R + 44`.

**Tap handling.** A tap is honoured if the finger travelled under 14px between `pointerdown` and
`pointerup`, rather than re-hit-testing on release — the box can move underneath the finger.

**The result, on screen and on the clipboard:**

```
⚖️ H E F T ⚖️
No 1 • Sept 6
🟡🟢🟢🟢🟢
1 Rehang
```

The Copy result button lights green (`#6ee7a0`) on solve, and retires — hidden, unlit, label reset —
whenever the board stops being solved. That last part fixed a bug present since 1.1.6: the button
used to sit there offering a result for a board no longer solved.

**Known non-features:** no persistence (refresh restarts), no daily ordering, fonts load from Google
and fall back gracefully. `No <n>` is a board index and means nothing to a reader — and since 1.4.4
it is the *first line of the header*, not just buried in the result. That is fine while one person
is playing and wrong the moment it is shared. Phase 2's date-seeded selection is what makes it
right.

**Opened from Messages, the top of the page is not painted.** Links tapped in Messages open in
Safari View Controller, which presents the page already scrolled down by roughly the height of its
chrome — the header and the mobile's ceiling bar fall off the top, and our page can't scroll, so
there is no way back up. Reloading fixes it; so does switching apps and returning.

**It is the platform, not us.** Reproduced on a 1KB static page with no script, no fonts, no SVG,
no sticky positioning and no adaptive sizing — and on that page, which *was* scrollable, you could
swipe up and recover the header. An Apple developer forum thread has described the same
presentation fault since 2017. No web-side fix is documented.

Six attempts failed, and they are recorded so nobody repeats them: `viewport-fit=cover` (the safe
area insets measure 0 on the device regardless); removing `html{height:100%}`; removing the sticky
header; re-asserting `scrollTo(0,0)` on `pageshow`; and giving the document a scroll range of 1px
and then 80px so that `scrollTo` would have something to act on. All were reverted. Note the
measurements were correct at every timestamp — `innerHeight`, `svh`, `dvh`, `scrollY`, the header's
`top` — which is why five of the six attempts chased geometry that was never wrong.

**Moving the wordmark into the board's SVG does not fix it**, and it is worth writing down why,
because it sounds like it should. What is lost is the top ~100px of the *page*, whatever occupies
it — the ceiling bar and the top of the root arm are already inside that band. Drawing the mark
above the ceiling bar puts it in the most-lost position on the page. Survival is decided by
vertical position, not by which element something lives in.

The proportionate response was to leave it: the game is fully playable from Messages, one referral
path loses a logo and a build number, and every fix on the table cost more than the bug. If v2's
wordmark-as-ceiling work lands, this may stop mattering as a side effect.

**Seven hooks is out of reach at four weights.** Zero from 420,000 draws. Reachable at five or six
weights at about 1 per 11,000. Eight hooks is impossible — zero from 111,000 draws across all 429
shapes.

**Five weights everywhere was considered and rejected.** It generates five times more easily and
opens far more six-hook skeletons, but fixing the rack at five removes a dimension that currently
varies. Mixed weight counts remain open.

---

## Tried and set aside

**Persistence and date-seeded selection.** Built in full and deliberately reverted — it was ahead of
where the game is. What it established, so v2 need not rediscover it: `localStorage` is sufficient
and needs no backend; a day's board should come from the date via days-since-epoch, counted from the
local Y-M-D read as UTC so daylight saving cannot bend it; **saving mid-board state is not optional**,
because without it a refresh silently erases your rehangs and the day becomes re-rollable; a
finished day should come back solved and frozen; and browsing boards must write nothing, or it
becomes a way off the daily. See `heft-plan.md`.

**Flat-topped weights.** Built, shipped behind a parameter, and beaten by the pointed set on a
phone. See *Settled in the 1.6 session*.

**Scoring by attempts, with a card of arm readings.** Built on the `attempts` branch (1.7.1), set
aside because the card needed a legend. See *Settled in the 1.6 session*.

**Hanging the mobile from the wordmark.** Routed around rather than solved — the rule under the
header is the ceiling, and a line has no particular x, so nothing needs pinning or travelling.
See *The header is the ceiling*. The measurement stands; the problem it measured is gone.

---

## Open questions

**Does the socket counter teach the scoring, or clutter the board?** Six dim zeros on a fresh
board is new ink on a screen the record kept quiet. Judged on one phone; a fresh player's phone
is the test.

**Do the 35px weights read?** The five-weight bank draws 10% smaller than the shipped one and
nobody but the author has played it.

**Is the colour scale right for five weights?** 🟢 0, 🟡 1, 🟠 2, 🔴 3+ per hook. With five values a
hook can take four wrong tries, so red may saturate. Leave it until a week of shares says which
way it fails; and when it is touched, fix the axis — green-to-red is the plan's flagged
colour-vision problem, and a single-hue ladder is available.

**Does the tilt read as progress or as fiddling?** Nobody has said in so many words whether they
read the mobile or fiddle with it.

**Is the ordering too generous?** The rack is sorted and the mapping fixed, as in v1. Whether that
makes the game too easy cannot be judged by anyone who already knows the mapping — it needs a
tester who has never played. Board 9, the only two-fork board, is the fairest test.

**Is `ink=1` the right value?** Built as a dial precisely because nobody knows. Compare 0, 1, 1.5
and 2 on a phone.

**Do people look up the tree?** The whole design rests on noticing that a level arm under a leaning
parent means the contents are wrong. If players read arm by arm instead, the resolution is present
but unused.

**Rehangs at five versus six hooks.** On the locking build the distribution was bimodal — 46% of
runs at zero, the rest clustered at four or six. Whether tilt changes that shape is unmeasured.

**Do people finish their first board?** The most useful metric from testers is how many stop before
completing one.

**Does the growing frame read as alive or as unsteady?** New in 1.2 and unanswered.

**Did restoring the ordering fix the reported problem?** Play reported swaps not making a
difference; the shuffle is the leading explanation and is now fully reverted. Unconfirmed on random
boards. If it persists, `?ink=0` is the next thing to check - 1.4.8 thickened every stroke and grew
the node dots, which could mask a small angular change.

**Tree shape is the difficulty axis, and the bank has almost none of it.** An arm with a "fork" -
both children arms - forces the player to hold two open questions at once. An arm with a leaf child
does not: the deepest arm solves alone, then each arm above has exactly one unknown. The bank is
**87 pure chains, 56 one-fork, 1 two-fork** (board 9). 60% is the easiest structure available and
there is effectively no hard end. Found from play, not from measurement: board 123 felt trivial and
is a chain. This is structural, computable without a solver estimate or play data, and monotone -
much better than anything else proposed for the curve. See `heft-generation.md`.

**Is the ratio window perceptible?** The measurement says the tilt carries less information on
high-ratio boards. It does not say anyone notices. Board 47 (ratio 3.4) against board 42 (ratio
60+) on a phone would settle it, and both are already live.

**Does the game need a difficulty curve at all?** Open, not committed. Random selection across a
bank filtered for legibility is a defensible design.

---

## Working notes

Dan's judgement from playing has been right every time; confident analysis has been wrong
repeatedly. Where the two conflict, play wins. Both of this session's real findings — the invisible
lean and the bow competing with it — came from him noticing something on a phone that no
measurement had been pointed at.

Verify by measuring the thing itself, not a proxy. This session produced three clean examples of
getting that wrong: glyph size was assessed from the 48-unit box instead of the ink inside it; a
path bounding box was computed with a parser that mishandled relative commands; and the adaptive
frame's scale invariant was asserted rather than checked until a test caught it drifting.

**Three separate tap bugs, one cause.** The tap zone is defined in board coordinates while the thing
that bounds it — the element's box — is defined in screen pixels. Anything touching input or layout
must be tested against a phone-sized, deliberately letterboxed box **with `getScreenCTM` and
`createSVGPoint` deleted**. The current code avoids both, and the test harness deletes them.

Tests that assert on the DOM in the same tick as a simulated tap read the *previous* frame. Wait a
frame.

The board is rebuilt as fresh DOM sixty times a second. Nothing on it can carry state or an event
listener across a frame.

**A question is not a request to rebuild, and it is not a request to measure either.** Both cost
time and usage. Explain the intended work and get approval before starting any of it.

**Say which population a statistic is over.** The v1.4 session produced two correct numbers for the
same thing — 36–42% and 14.3% — differing only in whether partial arms were included. A rate
without its denominator named is a number waiting to mislead.

**Costs raised after the fact are worse than costs raised badly.** The `boards.js` split was
proposed with two costs listed and a third unmentioned: it breaks the single-file preview. Dan found
that on his phone. List the costs of a change before it is chosen, not after it is shipped.
