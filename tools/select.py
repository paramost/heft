#!/usr/bin/env python3
"""
Select a bank from a generator pool and write it as boards.js.

    python3 tools/select.py --pool pool.jsonl --out boards.js --n 144

The clearance and crossing checks (tools/clearance.py) run here on any board the pool has not
already marked as checked, so a pool made before the generator applied them can still be used.

Selection is a scored greedy pick. A board scores on fork count, on whether its root forks (no
lone hook at the top), on its weight-ratio band (6-12 first) and on the leaf floor; each board
already taken from a shape discounts the next one from that shape; and boards with a lone hook
at the root are allowed up to a share of the bank (--lone-root-max) rather than banned. The
1.6.0 bank was filled one board per shape in rotation, which made 28 lopsided shapes into 69%
of the bank; this is the flexible version of that.

Python 3 standard library only.
"""

import argparse, itertools, json, math, random, sys, os
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from clearance import clear, MIN_HOOK_GAP

# ---------------------------------------------------------------- selection

def band_rank(r):
    return 0 if 6 <= r < 12 else 1 if 12 <= r < 25 else 2 if r < 6 else 3 if r < 50 else 4


def leaves(n):
    return 1 if n["t"] == "h" else leaves(n["l"]) + leaves(n["r"])


def lone_root(tree):
    """A lone hook on one side of the root arm: 5 of 6 weights hang from the other side."""
    return min(leaves(tree["l"]), leaves(tree["r"])) == 1


def score(b, w):
    c = b["cols"]
    return (w["fork"] * c["forks"]
            + (0 if lone_root(b["tree"]) else w["root"])
            + [1.0, 0.5, 0.3, 0.2, 0.0][band_rank(c["ratio"])] * w["ratio"]
            + (w["floor"] if c["leaf_floor_ok"] else 0))


def choose(ok, n, w, topo_penalty, lone_max, rnd):
    """Greedy: the best-scoring board, each shape discounted by how many of it are already in,
    lopsided boards allowed up to a share of the bank. Flexible where the old per-shape cap was
    rigid: a strong shape can contribute six boards, a weak one none."""
    for b in ok:
        b["_s"] = score(b, w) + rnd.random() * 0.01          # the jitter only breaks ties
    chosen, per_topo, lone = [], Counter(), 0
    pool = list(ok)
    while pool and len(chosen) < n:
        cap_hit = lone >= lone_max * n
        best, best_v = None, -1e9
        for b in pool:
            if cap_hit and lone_root(b["tree"]):
                continue
            v = b["_s"] - topo_penalty * per_topo[b["cols"]["topo"]]
            if v > best_v:
                best, best_v = b, v
        if best is None:
            break
        pool.remove(best); chosen.append(best)
        per_topo[best["cols"]["topo"]] += 1
        lone += lone_root(best["tree"])
    for b in ok:
        b.pop("_s", None)
    return chosen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", required=True, nargs="+")
    ap.add_argument("--out", default="boards.js")
    ap.add_argument("--n", type=int, default=144)
    ap.add_argument("--topo-penalty", type=float, default=0.8,
                    help="score discount per board already taken from the same shape")
    ap.add_argument("--lone-root-max", type=float, default=0.33,
                    help="largest share of the bank with a lone hook at the root (1 = no cap)")
    ap.add_argument("--w-fork", type=float, default=1.5)
    ap.add_argument("--w-root", type=float, default=1.0)
    ap.add_argument("--w-ratio", type=float, default=1.0)
    ap.add_argument("--w-floor", type=float, default=0.3)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--source", default="", help="how the pool was made, for the file header")
    ap.add_argument("--checked", default="", help="also write the boards that pass the checks here")
    args = ap.parse_args()

    pool = []
    for f in args.pool:
        pool += [json.loads(l) for l in open(f) if l.strip()]
    rnd = random.Random(args.seed)
    ok, why = [], Counter()
    for b in pool:
        if b.get("_ok"):
            ok.append(b); continue
        v = clear(b["tree"], b["nh"], b["vals"], b["cap"])
        if v:
            why[v] += 1
        else:
            b["_ok"] = True
            ok.append(b)
    print("pool %d: %d usable; dropped %s" % (len(pool), len(ok), dict(why)))
    if args.checked:
        with open(args.checked, "w") as fh:
            for b in ok:
                fh.write(json.dumps(b, separators=(",", ":")) + "\n")
    print("usable: hooks %s, forks %s, %d topologies, %d with a lone hook at the root" % (
        dict(sorted(Counter(b["nh"] for b in ok).items())),
        dict(sorted(Counter(b["cols"]["forks"] for b in ok).items())),
        len(set(b["cols"]["topo"] for b in ok)), sum(lone_root(b["tree"]) for b in ok)))

    w = {"fork": args.w_fork, "root": args.w_root, "ratio": args.w_ratio, "floor": args.w_floor}
    chosen = choose(ok, args.n, w, args.topo_penalty, args.lone_root_max, rnd)
    if len(chosen) < args.n:
        print("WARNING: only %d boards" % len(chosen))
    rnd.shuffle(chosen)

    nh = Counter(b["nh"] for b in chosen)
    forks = Counter(b["cols"]["forks"] for b in chosen)
    topo_n = len(set(b["cols"]["topo"] for b in chosen))
    per = Counter(b["cols"]["topo"] for b in chosen)
    k = Counter(b["k"] for b in chosen)
    lone = sum(lone_root(b["tree"]) for b in chosen)
    print("selected %d: hooks %s, weights %s, forks %s, %d topologies (max %d per shape), %d lone-root (%.0f%%)" %
          (len(chosen), dict(sorted(nh.items())), dict(sorted(k.items())), dict(sorted(forks.items())),
           topo_n, max(per.values()) if per else 0, lone, 100 * lone / max(1, len(chosen))))

    lines = []
    for b in chosen:
        out = {kk: b[kk] for kk in ("nh", "k", "cap", "tree", "vals", "sol")}
        lines.append(json.dumps(out, separators=(",", ":")))
    hooks_txt = ", ".join("%d at %s hooks" % (v, {5: "five", 6: "six", 7: "seven"}.get(h, h)) for h, v in sorted(nh.items()))
    header = ("/* Heft — the board bank. %d boards: %s; %s.\n"
              "      One board per line. Selected by tools/select.py from a tools/generate.py pool%s —\n"
              "      regenerate there, not by hand. Every board clears the hook-gap and crossing checks in select.py.\n"
              "   Loaded before the game script, which reads PUZZLES as a global. */\n"
              % (len(chosen), hooks_txt,
                 ", ".join("%d at %d weights" % (v, kk) for kk, v in sorted(k.items())),
                 (" (" + args.source + ")") if args.source else ""))
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(header + "const PUZZLES = [\n" + ",\n".join(lines) + "\n];\n")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
