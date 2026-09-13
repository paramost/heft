#!/usr/bin/env python3
"""
Does a board draw cleanly in every state a player can reach?

Two rules from the decision record that the generator's schema does not express:

- **Hooks must clear each other.** The closest pair of hooks, over every reachable state, must be
  no closer than the shipped bank's worst case (37.3 board units, measured the same way). Glyph
  ink is 31.8 units wide at most.
- **Nothing crosses.** No arm, riser or cord may intersect another it does not meet at a joint,
  and no line may enter the 44-unit box of a weight it does not hold - the box, not the ink,
  because a line ends in a 4.5-unit pulley (board 16 of the 1.6.0 bank had one sitting on a
  square).

Three passes: level first, since most failures show there; then every arm at -15/0/+15 - a
superset of what play can reach, since an arm is only at full tilt when one side of it is empty -
to find which pairs of lines or hooks could ever meet; then, only for what that flagged, every
reachable state (each hook empty or holding a weight, caps respected) with the angles the game
would actually draw. Checked against the shipped 1.5.12 bank: 143 of 144 pass; board 66 has a
hairline arm-on-arm touch with weights on hooks 3 and 5 only.

Used by generate.py at generation time and by select.py at selection time. Standard library only.
"""

import itertools, math
from collections import Counter
from geometry import U, DROP, HOOKDROP, MAX_TILT, FLOOR_DEG

MIN_HOOK_GAP = 37.3      # the shipped bank's worst case over reachable states (board 51), same measure
GLYPH_HALF_W = 14.6      # 31.8 units of ink at S/48, halved - glyph against glyph
GLYPH_HALF_H = 13.3      # 29 units of ink at S/48, halved
BOX_HALF = 22.0          # the weight's whole 44-unit box - nothing drawn may enter it
PUL = 4.5                # pulley radius: a line ends in a wheel, which is why the box, not the ink


# ---------------------------------------------------------------- geometry, as index.html draws it

def layout(tree, tilts):
    """Segments and hook centres for one tilt state. Mirrors positions() in index.html.
    Each segment carries the set of joints it belongs to; two segments that share a joint meet
    there by construction and are never a crossing."""
    segs, hooks = [], []
    it = iter(tilts)

    def walk(n, px, py):
        if n["t"] == "h":
            h = (px, py + HOOKDROP)
            hooks.append(h)
            hid = ("h", len(hooks) - 1)
            # the cord from the riser's end to the top of the weight
            segs.append(((px, py), (h[0], h[1] - GLYPH_HALF_H), "cord", {hid}))
            return hid
        th = next(it)
        c, s = math.cos(th), math.sin(th)
        l = (px - n["ld"] * U * c, py - n["ld"] * U * s)
        r = (px + n["rd"] * U * c, py + n["rd"] * U * s)
        aid = ("a", id(n))
        segs.append((l, r, "arm", {aid}))
        for end, child in ((l, n["l"]), (r, n["r"])):
            top = (end[0], end[1] + PUL)
            bottom = (end[0], end[1] + DROP)
            cid = walk(child, bottom[0], bottom[1])
            segs.append((top, bottom, "riser", {aid, cid}))
        return aid

    walk(tree, 0.0, 0.0)
    return segs, hooks


def _orient(a, b, c):
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def intersects(p1, p2, p3, p4):
    d1, d2 = _orient(p3, p4, p1), _orient(p3, p4, p2)
    d3, d4 = _orient(p1, p2, p3), _orient(p1, p2, p4)
    return ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)) and d1 != 0 and d2 != 0 and d3 != 0 and d4 != 0


def seg_point_dist(a, b, p):
    dx, dy = b[0] - a[0], b[1] - a[1]
    if dx == 0 and dy == 0:
        return math.dist(a, p)
    t = max(0.0, min(1.0, ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.dist((a[0] + t * dx, a[1] + t * dy), p)


def arm_index(tree):
    """Arms in the order layout() consumes tilts (pre-order), each with its lever units and the
    hook indices under each side."""
    out = []

    def hooks_under(n):
        return [n["i"]] if n["t"] == "h" else hooks_under(n["l"]) + hooks_under(n["r"])

    def walk(n):
        if n["t"] != "a":
            return
        out.append((n["ld"], n["rd"], hooks_under(n["l"]), hooks_under(n["r"])))
        walk(n["l"]); walk(n["r"])

    walk(tree)
    return out


def reachable_states(nh, k, cap):
    """Every assignment of hooks to weights (or empty) that respects the cap."""
    for st in itertools.product(range(-1, k), repeat=nh):
        c = Counter(x for x in st if x >= 0)
        if not c or max(c.values()) <= cap:
            yield st


def drawn_tilts(arms, masses):
    """The angle each arm actually draws for these hook masses, floor included."""
    out = []
    for ld, rd, L, R in arms:
        l = ld * sum(masses[i] for i in L)
        r = rd * sum(masses[i] for i in R)
        f = 0.0 if l == 0 and r == 0 else (r - l) / (r + l)
        if f == 0:
            out.append(0.0)
        else:
            out.append(math.copysign(max(MAX_TILT * abs(f), math.radians(FLOOR_DEG)), f))
    return out


def _violations(segs, hooks, seg_pairs, hook_pairs, ink_pairs):
    """Which of the watched pairs fail in this layout."""
    half_diag = math.hypot(BOX_HALF, BOX_HALF)
    for i, j in hook_pairs:
        if math.dist(hooks[i], hooks[j]) < MIN_HOOK_GAP:
            return "gap"
    for i, j in seg_pairs:
        if intersects(segs[i][0], segs[i][1], segs[j][0], segs[j][1]):
            return "cross"
    for i, k in ink_pairs:
        a1, a2 = segs[i][0], segs[i][1]
        h = hooks[k]
        if seg_point_dist(a1, a2, h) >= half_diag:
            continue
        dx, dy = a2[0] - a1[0], a2[1] - a1[1]
        L2 = dx * dx + dy * dy or 1.0
        t = max(0.0, min(1.0, ((h[0] - a1[0]) * dx + (h[1] - a1[1]) * dy) / L2))
        cx, cy = a1[0] + t * dx, a1[1] + t * dy
        if abs(cx - h[0]) < BOX_HALF and abs(cy - h[1]) < BOX_HALF:
            return "ink"
    return None


def clear(tree, nh, vals, cap):
    """Does this board draw cleanly in every state a player can reach?

    Three passes. Level first, because most failures show there. Then every arm at -15/0/+15 -
    a superset of what play can reach, since an arm is only at full tilt when one side of it is
    empty - to find which pairs of lines or hooks could ever meet. Then, only for what that
    flagged, every reachable state with the angles the game would actually draw. Returns the
    reason for failure, or None."""
    segs0, hooks0 = layout(tree, [0.0] * (nh - 1))
    n_seg = len(segs0)
    all_seg_pairs = [(i, j) for i in range(n_seg) for j in range(i + 1, n_seg)
                     if not (segs0[i][3] & segs0[j][3])]
    all_hook_pairs = [(i, j) for i in range(nh) for j in range(i + 1, nh)]
    all_ink_pairs = [(i, k) for i in range(n_seg) for k in range(nh) if ("h", k) not in segs0[i][3]]

    v = _violations(segs0, hooks0, all_seg_pairs, all_hook_pairs, all_ink_pairs)
    if v:
        return v + " at level"

    seg_pairs, hook_pairs, ink_pairs = set(), set(), set()
    for tilts in itertools.product((-MAX_TILT, 0.0, MAX_TILT), repeat=nh - 1):
        segs, hooks = layout(tree, tilts)
        for i, j in all_hook_pairs:
            if math.dist(hooks[i], hooks[j]) < MIN_HOOK_GAP:
                hook_pairs.add((i, j))
        for i, j in all_seg_pairs:
            if intersects(segs[i][0], segs[i][1], segs[j][0], segs[j][1]):
                seg_pairs.add((i, j))
        for i, k in all_ink_pairs:
            if _violations(segs, hooks, [], [], [(i, k)]):
                ink_pairs.add((i, k))
    if not (seg_pairs or hook_pairs or ink_pairs):
        return None

    arms = arm_index(tree)
    for st in reachable_states(nh, len(vals), cap):
        masses = [0 if x < 0 else vals[x] for x in st]
        segs, hooks = layout(tree, drawn_tilts(arms, masses))
        v = _violations(segs, hooks, seg_pairs, hook_pairs, ink_pairs)
        if v:
            return v + " in play"
    return None


