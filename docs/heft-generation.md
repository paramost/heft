# Heft — board generation spec (v2)

Written against build 1.5.12. This replaces the ad-hoc constraint list the v1 generator was given.
Implemented as **`tools/generate.py`** — Python 3, standard library only, no dependencies.

    python3 tools/generate.py --verify                     # check property code against boards.js
    python3 tools/generate.py --hooks 6 7 --k 4 5 \
        --samples 40000 --no-deep --out pool.jsonl         # fast structural pass
    python3 tools/generate.py --hooks 6 7 --k 4 5 \
        --samples 5000 --out pool.jsonl                    # with the enumeration columns

`--verify` recomputes every property over the shipped bank and prints forks 29/101/14 and 37
topologies. Run it first: it checks the measuring code against answers already known.

**Earlier docs claimed generation lived in a separate private repo. It never did.** The code that
produced the shipped 144 was not kept, so this is a build, not an edit.

## The change in framing

**Generate wide, record everything, select later.**

v1 baked its constraints into generation, so a rejected board was gone and every constraint
question ("what would a leaf-arm floor cost?") needed a fresh run. Several of tonight's findings
would have been unanswerable that way.

So: the generator emits a **large pool** and a **property table**, and applies only the constraints
that define a *valid* board. Everything else — difficulty, legibility, weight spacing — is recorded
as a column and applied at selection time, where it is cheap to revise and reversible.

Corollary: the pool wants to be big enough that a heavy selection still leaves a usable bank. The
leaf-arm floor alone cost 82% of the shipped bank; stacking it with a ratio band and a fork
requirement could plausibly cost 95%+, and **nobody knows, because it has never been generated with
any of them**. Aim high and find out from the table rather than from a rerun.

## Board schema (unchanged)

```json
{"nh":6, "k":4, "cap":2,
 "vals":[3,9,16,32],
 "sol":[3,2,2,3,0,1],
 "tree":{"t":"a","ld":5,"rd":4,
         "l":{"t":"a","ld":1,"rd":2,"l":{"t":"h","i":0},"r":{"t":"h","i":1}},
         "r":{...}}}
```

- `nh` hooks, `k` distinct weight values, `cap` copies of each value available
- `vals` **ascending**; `sol[i]` indexes `vals` for hook `i`
- `tree` nodes are `t:"a"` arms with integer lever units `ld`/`rd` and children `l`/`r`, or
  `t:"h"` hooks with index `i`
- Hook indices are assigned in tree traversal order, not screen order

**What v1 used:** `nh` 5 or 6 (96/48), `k` always 4, `cap` 2 or 3 (122/22), lever units 1–5,
depth 3–5, values 1–315.

## Hard constraints — a board is invalid without these

1. **Every arm balances** under `sol`: `ld × mass(left) == rd × mass(right)`, exactly, in integers.
2. **The solution is unique.** No other assignment respecting `cap` balances every arm. This is the
   expensive check and should stay last.
3. **All `k` values are used** in the solution.
4. **`vals` in lowest terms** — no common factor across all four. v1's bank already satisfies this
   and it matters: a player solving on paper recovers ratios, not masses, and a fractional result
   is their signal that they picked the wrong unit.
5. **No 1:1 arms.** Settled in v1: a 1:1 arm balances with any matching pair — 3.29 ways against
   1.22 elsewhere — so a player balances it correctly, gets no response, and concludes they are
   wrong. Reject the arm outright, not just the case where both children are equal hooks.

## Properties to record — columns, not gates

Per board:

| column | why it matters |
|---|---|
| `forks` | arms whose **both** children are arms. **The difficulty axis.** |
| `depth` | longest root-to-hook path |
| `nh`, `k`, `cap` | as now |
| `ratio` | `max(vals)/min(vals)` |
| `min_step` | smallest adjacent ratio in `vals` |
| `max_torque` | largest `ld × mass(left)` over arms |
| `leaf_floor_ok` | true if every **leaf** arm's imbalance, over all reachable states, clears 20% |
| `invisible_swaps` | share of single-weight swaps changing the affected arm by < 1.25° |
| `sub_floor` | share of complete-arm readings below 1.25° |
| `confusable` | share of leaf-arm substitutions of two *different* weights differing by < 1.25° |

`invisible_swaps`, `sub_floor` and `confusable` need a state enumeration per board — a few seconds
each at `nh` 5–6, so budget for it rather than skipping it. They are the columns that actually
predict what play complains about.

## Open the parameter box

The v1 box is small and it is the reason boards feel alike and cap out in difficulty. `k` is
**always 4**. `nh` is 5 or 6. `cap` is 2 or 3, depth 3–5, lever units 1–5. 144 boards inside that
box will resemble each other however they are selected.

**Widen it. Each of these adds difficulty and variety at the same time:**

| | v1 | v2 |
|---|---|---|
| `nh` hooks | 5–6 | **5–7** |
| `k` values | 4 | **4–5** |
| depth | 3–5 | **3–6** |
| `cap` | 2–3 | 2–3 (unchanged) |
| levers | 1–5 | 1–5 (unchanged) |

Hooks matter most, because the topology space is Catalan in `nh`: **14 shapes at 5 hooks, 42 at 6,
132 at 7**. Nearly all the structural variety the game could have is sitting one hook away.

Two costs to check rather than assume:

- **The rack grows.** `k=5` puts five glyphs in the row, and there are only four ordered shapes.
  A fifth is a design question, not a generation one — do not assume it is free.
- **Enumeration gets slower.** State space is roughly `(k+1)^nh`: 15,625 at nh=6/k=4 today,
  **279,936** at nh=7/k=5. The per-board property columns below are still affordable, but budget
  for ~18× the compute per board at the top of the range.

## Diversity is a requirement, not an outcome

The shipped bank has **32 distinct topologies across 144 boards** — 4.5 boards per shape, and twelve
shapes account for 84 of them. Nothing is a literal duplicate (all 144 topology+lever signatures are
unique, 126 of 144 weight sets are distinct), but at the level a player perceives a board — its
silhouette — each shape recurs four or five times.

Worse, the branchy shapes are the rare ones. `((hh)((hh)(hh)))` and `(((hh)h)((hh)h))` appear
**once each**, while chain-like shapes appear seven times.

**Requirements:**

1. **Cap repeats per topology.** No shape should account for more than ~2–3 boards in a 144-board
   bank. With 132 topologies available at 7 hooks this stops being a constraint and starts being
   free.
2. **Select across topologies before selecting within them.** Fill the shape slots first, then
   choose the best board for each slot on the other columns. Selecting on quality first will
   re-concentrate on whatever shape happens to score well.
3. **Record the topology string** (`(h(h(hh)))` form, levers omitted) as a column so repeats are
   countable rather than eyeballed.

## Selection targets — what the bank should look like

**Fork count is the headline.** The shipped bank is 87 pure chains, 56 one-fork, **1 two-fork**. A
chain hands the player a forced sequence: the deepest arm has two leaves and solves alone, then
every arm above it has exactly one unknown. You never hold two open questions at once. 60% of the
bank is the easiest structure available and there is effectively no hard end.

Wanted: a real spread, with enough two-fork and three-fork boards to build a top. At 7 hooks a
three-fork board is possible; at 6 it is the rare `((hh)((hh)(hh)))` shape. Whether they exist in
quantity is the first thing the pool will tell us.

**A caution on judging this.** Difficulty reports from someone who has played the game for months
are not calibrated to a new player. "Still too easy" from that source is an argument for making a
hard end *exist*, not evidence that current boards are too easy for anyone else. The curve's low
end should be set by a fresh tester, not by the author.

**Weight ratio around 6–12.** Invisible swaps run 26.9% in that band against 35.2% at 12–25 and
48.3% above 50. The 6–25 window proposed earlier is the wrong shape — it only reaches 30.5%.
Recorded rather than enforced, but this is the band to prefer.

**Leaf-arm imbalance floor at 20%.** The original Phase 1 question, still uncosted at six hooks.
With the floor as a column it can be answered from the table.

**Do not chase full honesty.** Zero of 144 boards have both no sub-floor readings and no invisible
swaps, and none could: any arm carrying a subtree has thousands of reachable torque values inside a
15° range. The game promises *level means level* and *more wrong looks more wrong*, and both hold.
Fine gradation was never promised.

## Output

- `boards.js` stays the deploy format: one board per line, `const PUZZLES = [...]`, 149 lines for
  144 boards. Generated from the selection, not from the pool.
- The **pool** and the **property table** live in the generator repo. They are the thing worth
  keeping; the bank is a view over them.

## What to report back

Three numbers decide the shape of everything else:

1. How many **two-fork and three-fork** boards exist at all, per hook count — and how many
   distinct topologies are reachable at 7 hooks with a unique solution.
2. What the **leaf floor** costs at six hooks.
3. What fraction of the pool survives **fork spread + ratio 6–12 + leaf floor together**.

If (3) is tiny, the constraints have to be ranked rather than stacked, and fork count should win —
it is the one that matches what play reported.
