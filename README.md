# Heft

A daily puzzle. A hanging mobile with empty hooks and a rack of weights — fill every hook so the
whole thing hangs level. You never learn what anything weighs.

**Live:** [heftdaily.com](https://heftdaily.com) · **Build:** 1.6.6 · **five weights** · **Boards:** 144, all six hooks

## How it works

Each arm's angle is directly proportional to its fractional torque imbalance — the tilt *is* the
arithmetic. The mobile hangs from the rule under the header, which is its ceiling and lights when
the board comes level. An arm can be level with the wrong weights on it, but then its subtree has the wrong
total mass, so the arm above must lean. Nothing in the interface locks, hints, or indicates
correctness.

Placing a weight is free. Replacing one costs a rehang. Zero is perfect.

The weights are ordered and the rack is sorted to match: **diamond, triangle, hexagon, pentagon,
house**, lightest to heaviest, on every board. Nothing states this — the glyphs share one height
and their ink areas climb, so it reads as apparent weight. You still have to hang something to
learn the ratios, which are the puzzle.

Five weights on six hooks is the **heavy** rung, shipped alone for feedback. The four-weight
bank it replaced (1.5.12, 96 boards at five hooks and 48 at six) is the easy rung and comes
back beside it when the daily is built.

## Repo

- `index.html` — the game. ~33 KB of code, no build step. Vercel serves it as-is.
- `boards.js` — the 144-board bank, one board per line, loaded before the game script.
- `tools/select.py` — picks a bank from a generator pool, applying the clearance and crossing
  checks the generator does not.
- `docs/` — decision record, project plan, generation spec, publishing notes.

- `vercel.json` — one header rule: `Cache-Control: public, max-age=0, must-revalidate` on every
  path, so a deploy is never served from a stale cache. This is what stops the two-file trap
  below from biting in practice.

- `tools/generate.py` — the board generator. Python 3, standard library only, no dependencies.

Earlier docs said generation lived in a separate private repo. **It never did** — no such repo
exists, and the code that produced the shipped 144 was not kept. `tools/generate.py` was written
fresh against `docs/heft-generation.md`; run `python3 tools/generate.py --verify` to check its
property code against `boards.js` before trusting it on new boards.

The bank was split out of `index.html` in 1.4.0. It had been a single 42 KB line — 63% of the
file — which made every one-line edit expensive and every diff unreadable. The game reads
`PUZZLES` as a global, so the load order matters and there is no module system involved.

## URL parameters

All six are testing affordances. None changes the default experience.

| parameter | default | effect |
|---|---|---|
| `?board=N` | random | opens on puzzle N (1–144) instead of a random one |
| `?tilt=N` | 1 | raises the imbalance to the power N before mapping to angle; 1 is proportional |
| `?bow=N` | 0 | arm curve as a fraction of arm length. Straight since 1.5.5; 0.025 restores the old sag |
| `?ink=N` | 1 | lifts the wire off the background — colour and stroke weight; 0 is the 1.4.7 drawing, 2 is the ceiling |
| `?floor=N` | 1.25 | minimum lean in **degrees** for an arm that is not level; 0 restores the 1.5.2 drawing |
| `?tiltmax=N` | 15 | the tilt range in degrees, 8–30. Widening reduces invisible swaps but risks the staircase 30° was rejected for |

A non-default `tilt`, `bow`, `ink`, `floor` or `tiltmax` prints next to the build number, so a screenshot always says which
version produced it.

## Deploying

Commit to the default branch; Vercel publishes automatically.

**Bump the build string in the same commit — it lives in three places:**

1. `const BUILD` in the script
2. `data-build` on the `<html>` element
3. an HTML comment near the top of `<head>`

The last two exist so the version can be read without running the page — by `curl`, by
view-source, by anything that strips scripts. The script checks all three agree and prints
`· BUILD MISMATCH` next to the build number if they don't, so a half-done bump announces itself
rather than lying. The build number renders under the buttons. Never reuse one: 1.3.x was
skipped deliberately.

Verify in a private tab, since browsers cache hard enough that a stale copy looks like a failed
deploy. With two files there is a new version of that trap — a cached `boards.js` against a fresh
`index.html` looks like a working game with the wrong bank, and nothing on screen says so.
