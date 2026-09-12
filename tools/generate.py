#!/usr/bin/env python3
"""
Heft board generator.

Generates a POOL of candidate boards and a PROPERTY TABLE, and applies only the constraints that
make a board valid. Difficulty, legibility and spacing are recorded as columns and applied later,
at selection time, where the decision is cheap and reversible. See docs/heft-generation.md.

Python 3 standard library only. No dependencies, no build step.

    python3 tools/generate.py --hooks 5 6 7 --k 4 5 --samples 200000 --out pool.jsonl
    python3 tools/generate.py --verify          # check the property code against the shipped bank

The key idea: the balancing weights are DERIVED, not searched for. An arm with lever units ld:rd
fixes the mass ratio of its two sides, so propagating from the root gives every hook's mass as a
fraction. Clear denominators, divide by the gcd, and that is the only multiset of weights that
balances the tree, in lowest terms. Then we check whether it has exactly k distinct values inside
the cap. Uniqueness is the only enumeration and it is small.
"""

import argparse, json, math, random, sys, itertools
from fractions import Fraction
from collections import Counter

U, DROP, HOOKDROP, R_GLYPH = 22.0, 56.0, 30.0, 21.0
MAX_TILT = math.radians(15)
FLOOR_DEG, JND_DEG = 1.25, 1.25
STAGE_W, STAGE_H = 366.0, 405.0          # a 390x844 phone, 48svh stage


# ---------------------------------------------------------------- tree shapes

def topologies(n):
    """Every binary tree shape with n leaves, as nested tuples. Catalan(n-1) of them."""
    if n == 1:
        return [None]
    out = []
    for i in range(1, n):
        for l in topologies(i):
            for r in topologies(n - i):
                out.append((l, r))
    return out


def build(shape, levers, counter):
    """Turn a shape plus a lever list into the game's tree format."""
    if shape is None:
        i = counter[0]; counter[0] += 1
        return {"t": "h", "i": i}
    ld, rd = levers.pop()
    l = build(shape[0], levers, counter)
    r = build(shape[1], levers, counter)
    return {"t": "a", "ld": ld, "rd": rd, "l": l, "r": r}


def arms(n, out=None):
    out = [] if out is None else out
    if n["t"] == "a":
        out.append(n); arms(n["l"], out); arms(n["r"], out)
    return out


def leaves(n, acc):
    if n["t"] == "h":
        acc.append(n["i"])
    else:
        leaves(n["l"], acc); leaves(n["r"], acc)
    return acc


def topo_string(n):
    return "h" if n["t"] == "h" else "(" + topo_string(n["l"]) + topo_string(n["r"]) + ")"


def depth(n, d=0):
    return d if n["t"] == "h" else max(depth(n["l"], d + 1), depth(n["r"], d + 1))


def forks(tree):
    return sum(1 for a in arms(tree) if a["l"]["t"] == "a" and a["r"]["t"] == "a")


# ------------------------------------------------------- the derived weights

def hook_masses(tree, nh):
    """The only weights that balance this tree, in lowest terms. None if degenerate."""
    m = [None] * nh

    def go(node, total):                       # total = mass of this subtree
        if node["t"] == "h":
            m[node["i"]] = total
            return
        # ld*left == rd*right and left+right == total
        left = total * Fraction(node["rd"], node["ld"] + node["rd"])
        go(node["l"], left)
        go(node["r"], total - left)

    go(tree, Fraction(1))
    den = 1
    for f in m:
        den = den * f.denominator // math.gcd(den, f.denominator)
    vals = [int(f * den) for f in m]
    g = 0
    for v in vals:
        g = math.gcd(g, v)
    if g == 0:
        return None
    return [v // g for v in vals]


# ---------------------------------------------------------------- validity

def balanced(tree, masses):
    for a in arms(tree):
        l = a["ld"] * sum(masses[i] for i in leaves(a["l"], []))
        r = a["rd"] * sum(masses[i] for i in leaves(a["r"], []))
        if l != r:
            return False
    return True


def unique_solution(tree, nh, vals, cap, sol):
    """No other assignment of vals respecting cap balances every arm."""
    k = len(vals)
    for combo in itertools.product(range(k), repeat=nh):
        if combo == tuple(sol):
            continue
        c = Counter(combo)
        if any(c[t] > cap for t in range(k)):
            continue
        if balanced(tree, [vals[t] for t in combo]):
            return False
    return True


def symmetrical(tree):
    """No 1:1 arms at all. Settled in v1 and enforced in the shipped bank (0 of 144 have one): a
    1:1 arm balances with any matching pair - 3.29 ways against 1.22 elsewhere - so a player
    balances it correctly, gets no response, and concludes they are wrong."""
    return any(a["ld"] == a["rd"] for a in arms(tree))


# ---------------------------------------------------------------- geometry

def scale(tree):
    pos = {}

    def walk(n, px, py):
        if n["t"] == "h":
            pos[n["i"]] = (px, px); return
        lx, rx = px - n["ld"] * U, px + n["rd"] * U
        pos["a%d" % id(n)] = (lx, rx)
        walk(n["l"], lx, py + DROP); walk(n["r"], rx, py + DROP)

    walk(tree, 0, 0)
    xs = [v for t in pos.values() for v in t]
    w = round(max(xs) - min(xs) + (R_GLYPH + 22) * 2)
    s = math.sin(MAX_TILT)

    def worst(n, py):
        if n["t"] == "h":
            return py + HOOKDROP
        return max(worst(n["l"], py + n["ld"] * U * s + DROP),
                   worst(n["r"], py + n["rd"] * U * s + DROP))

    return min(STAGE_W / w, STAGE_H / math.ceil(worst(tree, 0) + R_GLYPH + 44))


def drawn_angle(f):
    """Degrees, with the 1.25 deg floor: an arm that is not level never draws level."""
    if f == 0:
        return 0.0
    return max(15.0 * abs(f), FLOOR_DEG)


# ------------------------------------------------------- property columns

def columns(tree, nh, vals, cap, sol, deep=True):
    A = arms(tree)
    sub = {id(a): (leaves(a["l"], []), leaves(a["r"], []), leaves(a, [])) for a in A}
    masses = [vals[t] for t in sol]
    col = {
        "nh": nh, "k": len(vals), "cap": cap,
        "forks": forks(tree),
        "depth": depth(tree),
        "topo": topo_string(tree),
        "ratio": max(vals) / min(vals),
        "min_step": min(vals[i + 1] / vals[i] for i in range(len(vals) - 1)),
        "max_torque": max(a["ld"] * sum(masses[i] for i in sub[id(a)][0]) for a in A),
    }

    # leaf-arm imbalance floor: every reachable state of every leaf arm clears 20%
    ok = True
    for a in A:
        if not (a["l"]["t"] == "h" and a["r"]["t"] == "h"):
            continue
        for x in vals:
            for y in vals:
                f = (a["rd"] * y - a["ld"] * x) / (a["rd"] * y + a["ld"] * x)
                if 0 < abs(f) < 0.20:
                    ok = False
    col["leaf_floor_ok"] = ok

    if not deep:
        return col

    k = len(vals)
    low = n_read = 0
    inv = n_swap = 0
    conf = n_conf = 0

    for s in itertools.product(range(k), repeat=nh):
        c = Counter(s)
        if any(c[t] > cap for t in range(k)):
            continue
        m0 = [vals[t] for t in s]
        for a in A:
            L, Rr, _ = sub[id(a)]
            l = a["ld"] * sum(m0[i] for i in L); r = a["rd"] * sum(m0[i] for i in Rr)
            f = (r - l) / (r + l)
            if f != 0:
                n_read += 1
                if 15.0 * abs(f) < FLOOR_DEG:
                    low += 1
        for h in range(nh):
            for t2 in range(k):
                if t2 == s[h]:
                    continue
                s2 = list(s); s2[h] = t2
                c2 = Counter(s2)
                if any(c2[t] > cap for t in range(k)):
                    continue
                m1 = [vals[t] for t in s2]
                for a in A:
                    L, Rr, All = sub[id(a)]
                    if h not in All:
                        continue
                    l0 = a["ld"] * sum(m0[i] for i in L); r0 = a["rd"] * sum(m0[i] for i in Rr)
                    l1 = a["ld"] * sum(m1[i] for i in L); r1 = a["rd"] * sum(m1[i] for i in Rr)
                    f0 = (r0 - l0) / (r0 + l0); f1 = (r1 - l1) / (r1 + l1)
                    a0 = drawn_angle(f0) * (1 if f0 > 0 else -1)
                    a1 = drawn_angle(f1) * (1 if f1 > 0 else -1)
                    n_swap += 1
                    if abs(a0 - a1) < JND_DEG:
                        inv += 1

    # two DIFFERENT weights that look the same on a leaf arm
    for a in A:
        if not (a["l"]["t"] == "h" and a["r"]["t"] == "h"):
            continue
        for y in vals:
            for i in range(k):
                for j in range(i + 1, k):
                    f1 = (a["rd"] * y - a["ld"] * vals[i]) / (a["rd"] * y + a["ld"] * vals[i])
                    f2 = (a["rd"] * y - a["ld"] * vals[j]) / (a["rd"] * y + a["ld"] * vals[j])
                    d = abs(drawn_angle(f1) * (1 if f1 > 0 else -1)
                            - drawn_angle(f2) * (1 if f2 > 0 else -1))
                    n_conf += 1
                    if d < JND_DEG:
                        conf += 1

    col["sub_floor"] = low / n_read if n_read else 0.0
    col["invisible_swaps"] = inv / n_swap if n_swap else 0.0
    col["confusable"] = conf / n_conf if n_conf else 0.0
    return col


# ---------------------------------------------------------------- generation

def candidate(nh, k_want, cap, lever_max, shapes, rnd):
    shape = rnd.choice(shapes)
    n_arms = nh - 1
    levers = [(rnd.randint(1, lever_max), rnd.randint(1, lever_max)) for _ in range(n_arms)]
    tree = build(shape, list(levers), [0])
    masses = hook_masses(tree, nh)
    if masses is None:
        return None
    seen = sorted(set(masses))
    if len(seen) != k_want:
        return None
    counts = Counter(masses)
    if max(counts.values()) > cap:
        return None
    if symmetrical(tree):
        return None
    vals = seen
    sol = [vals.index(m) for m in masses]
    if not balanced(tree, masses):
        return None                          # should not happen; a guard on the derivation
    if not unique_solution(tree, nh, vals, cap, sol):
        return None
    return {"nh": nh, "k": k_want, "cap": cap, "tree": tree, "vals": vals, "sol": sol}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hooks", type=int, nargs="+", default=[5, 6, 7])
    ap.add_argument("--k", type=int, nargs="+", default=[4, 5])
    ap.add_argument("--cap", type=int, nargs="+", default=[2, 3])
    ap.add_argument("--lever-max", type=int, default=5)
    ap.add_argument("--samples", type=int, default=50000)
    ap.add_argument("--max-value", type=int, default=400,
                    help="reject boards whose heaviest weight exceeds this")
    ap.add_argument("--no-deep", action="store_true",
                    help="skip the enumeration-based columns (much faster)")
    ap.add_argument("--out", default="pool.jsonl")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--verify", action="store_true",
                    help="check the property code against an existing boards.js")
    ap.add_argument("--bank", default="boards.js")
    ap.add_argument("--root-fork", action="store_true",
                    help="only shapes whose root arm carries two arms - no lone hook at the top")
    args = ap.parse_args()

    if args.verify:
        src = open(args.bank).read()
        P = json.loads(src[src.index("["):src.rindex("]") + 1])
        f = Counter(forks(b["tree"]) for b in P)
        t = len(set(topo_string(b["tree"]) for b in P))
        bad = [i + 1 for i, b in enumerate(P)
               if not balanced(b["tree"], [b["vals"][x] for x in b["sol"]])]
        print("boards            :", len(P))
        print("forks             :", dict(sorted(f.items())), "  (expect {0: 29, 1: 101, 2: 14})")
        print("distinct topologies:", t, "  (expect 37)")
        print("unbalanced boards :", bad, "  (expect [])")
        return

    shapes = {n: topologies(n) for n in args.hooks}
    if args.root_fork:
        # a shape is a nested tuple; a leaf is not. The root forks when neither child is a leaf.
        shapes = {n: [s for s in ss if isinstance(s[0], tuple) and isinstance(s[1], tuple)]
                  for n, ss in shapes.items()}
        print("root-fork shapes:", {n: len(ss) for n, ss in shapes.items()})
    rnd = random.Random(args.seed)
    kept, seen_sig = [], set()
    for _ in range(args.samples):
        nh = rnd.choice(args.hooks)
        b = candidate(nh, rnd.choice(args.k), rnd.choice(args.cap),
                      args.lever_max, shapes[nh], rnd)
        if b is None:
            continue
        if max(b["vals"]) > args.max_value:
            continue
        sig = json.dumps([b["tree"], b["vals"]], sort_keys=True)
        if sig in seen_sig:
            continue
        seen_sig.add(sig)
        b["cols"] = columns(b["tree"], b["nh"], b["vals"], b["cap"], b["sol"],
                            deep=not args.no_deep)
        kept.append(b)

    with open(args.out, "w") as fh:
        for b in kept:
            fh.write(json.dumps(b, separators=(",", ":")) + "\n")

    print("kept %d boards from %d samples -> %s" % (len(kept), args.samples, args.out))
    for key in ("nh", "k", "cap", "forks", "depth"):
        print("  %-7s %s" % (key, dict(sorted(Counter(b["cols"][key] for b in kept).items()))))
    print("  topologies %d distinct" % len(set(b["cols"]["topo"] for b in kept)))


if __name__ == "__main__":
    main()
