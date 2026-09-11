# Heft — publishing for testing

Everything needed to put Heft in front of testers. Assumes no build tools and no command line.

---

## 1. What ships

**`index.html`** and **`boards.js`** at the repo root are the game. No build step, no server logic;
Vercel serves both as-is. `index.html` is ~24 KB of code and reads `PUZZLES` as a global, so
`boards.js` must load first. Also in the repo: `/docs`.

**Also in this repo:** `tools/generate.py`, the board generator. It is not served — Vercel ignores
it — and the boards it produces are public in `boards.js` anyway, solutions included, so there is
nothing in it worth hiding. The game has to
be public; the thing that makes new boards does not, and it is the part worth protecting. Anyone can
copy 144 boards — making the 145th means rebuilding the reasoning behind them.

Also excluded: the design reference sheets. They are history rather than product.

---

## 2. Deploying

The repo is at `github.com/<you>/heft`, deployed by Vercel to **heftdaily.com**.

**To ship a change:** commit to the default branch. Vercel builds and publishes automatically.
Editing `index.html` in GitHub's web editor works from a phone.

**Always bump the build string in the same commit — it is in three places:** `const BUILD`, the
`data-build` attribute on `<html>`, and an HTML comment in `<head>`. The last two can be read
without running the page. The script checks all three agree and prints `· BUILD MISMATCH` beside
the build number if they don't. It renders under the buttons. Never reuse a number; 1.3.x was
skipped deliberately.

**To verify a deploy:** open the site in a private tab, or append `?v=<something>`. Check the
mobile is actually drawn, not just that the build number is right — a stale cached `boards.js`
against a fresh `index.html` gives you a header, an empty stage and the default prompt, with no
error anywhere.

**Editing from a phone.** GitHub's mobile editor sometimes will not enable *Commit changes* after a
large paste: the text is on screen but no change event fired. Type a character and delete it, or
use `github.dev` (press `.` on the repo page), which handles it. `boards.js` should be 149 lines —
three comment lines, the opening bracket, 144 boards, the closing bracket.

**Rolling back:** Vercel keeps every deployment. Promote a previous one from the dashboard.

**The old Netlify subdomains** (`heftdaily.netlify.app`, `heftdailygame.netlify.app`) are stale and
still serving an old build — one of them cost a testing session's confusion in the v1.2 work.
Retire them, and nudge anyone holding an old link.

---

## 3. Testing parameters

Three URL parameters exist for testing. They print next to the build number when off default, so a
screenshot always identifies itself.

- `?board=N` — pin puzzle N (1–144). Selection is otherwise random.
- `?tilt=N` — 1 is proportional (the default). Lower compresses the top of the range and lifts small
  imbalances out of the sub-pixel band; 0.5 removes that band entirely.
- `?bow=N` — 0 is the default: arms are straight, with pulleys at the corners. 0.025 restores the
  curved arms used up to 1.5.4.
- `?ink=N` — 1 is the default. 0 reproduces the dimmer 1.4.7 drawing; 2 is as bright and heavy as
  it goes. Colour and stroke weight only, never opacity.
- `?floor=N` — 1.25 is the default, in degrees. The smallest lean an arm that is not level is
  allowed to draw. 0 restores the 1.5.2 drawing, where a near-level arm could look level.
- `?tiltmax=N` — 15 is the default tilt range in degrees. Not shipped as anything else; 20 reads
  as a candidate on paper but has not been judged on a phone.

Comparison links point at the same board so only one thing differs:
`heftdaily.com/?board=26&tilt=1&bow=0` against `heftdaily.com/?board=26&tilt=1&bow=0.025`

---

## 4. Before you send it

Open the link on a phone yourself and check four things, because these are the failure modes that
make a tester quit rather than complain:

- **The wordmark renders in a heavy sans.** If it looks like a default serif, the fonts didn't load.
- **Tapping a weight in the rack lifts it**, and tapping a hook hangs it there.
- **Tapping a hung weight takes it back off.** This one broke once and was subtle.
- **The board resizes as you hang weights and the mobile never changes size.** The frame follows the
  ink; the scale is pinned. If the mobile itself grows or shrinks, something is wrong.

---

## 5. What to tell testers

Keep it to three lines. The game is meant to explain itself and any instruction you add is a
confound — if you have to say it, that's a finding.

> Fill every hook so the whole mobile hangs level. You never find out what anything weighs.
> Placing is free, changing your mind costs you. Send me your result when you finish one.

Warn them about the prototype's limits so they report the game rather than the scaffolding:

- **It doesn't remember anything.** Refreshing starts over.
- **It isn't a daily yet.** Boards come up at random; "Another day" gives you a different one.
- **The number in the header and the result is a board index**, not a day. It won't match anyone
  else's — and since 1.4.4 it is the first line of the header, so it is the first thing they see.
- **Nobody needs to reach the end.** There are 144 boards. One or two is a useful session.

---

## 6. What to collect

The **Copy result** button after a solve — it lights green — produces exactly the artifact you want:

```
⚖️ H E F T ⚖️
No 23 • Sept 7
🟢🟠🟢🟠🟡
5 Rehangs
```

Board number, score, and a per-hook picture of where they struggled. Ask for that plus one sentence.

Five questions worth asking specifically, because each maps to something currently unknown:

1. **Did you work out what to do without being told?** The whole design bets on the object teaching
   its own rules.
2. **Did you look at the arm above when one arm went level?** The game's core resolution depends on
   this. If people read arm by arm instead, it's present but unused.
3. **Did the tilt feel like it was telling you something, or like fidgeting?**
4. **Was there a point you thought it was broken?** With one weight hung the mobile leans hard.
5. **Did the board growing and shrinking as you played read as alive, or as unsteady?** New in 1.2.

**The most valuable number isn't in any answer:** how many people open the link and never finish a
board. Nobody writes "I didn't understand it" — they just close the tab.

---

## 7. Known limits to expect in feedback

Things that are already understood, so they don't need re-diagnosing when someone raises them:

- **No persistence, no daily.** Both are Phase 2 and were deliberately reverted from v1.
- **Green-to-red share grid** is the worst axis for colourblind players. Outstanding.
- **A wrong arm can sit a pixel off level.** Measured: 0.79% of non-level readings draw under 1px.
  It is a property of the 20% floor covering complete arrangements only, and it cannot be
  generated away except on leaf arms. See the decision record.
- **Five and six hooks only.** Seven doesn't generate; it isn't an oversight.
- **The rack is ordered lightest to heaviest**, left to right, on every board. Nothing says so;
  the shapes are drawn to look it.
- **Four weight shapes, one per weight.** Until 1.5.1 the same four appeared on every board by
  accident; a fifth drew nothing at all. The ring was dropped in 1.5.2, so no weight is a circle
  and an empty socket is the only round thing on the board.
- **A diamond and a pentagon** are the closest two shapes at small size, and since 1.5.2 both
  appear on every board. Still untested with a fresh player.
- **No link preview.** Sharing the URL gives a bare link with a favicon.
- **Some boards' weights are far apart and some are close together**, and it measurably changes how
  much the tilt tells you. Boards with a wide spread pin more arms near full lean; boards with a
  narrow spread draw more leans under a pixel. Measured, not filtered. See the decision record.
- **Opened from a text message, the top of the page is missing** — the wordmark, and the top of the
  mobile. Safari View Controller presents the page pre-scrolled and our page can't scroll back.
  A reload fixes it. It's a platform fault, reproduced on a static page with nothing in it, and
  there is no known fix. If you send testers a link by SMS, expect it, and tell them to reload.
