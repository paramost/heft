#!/usr/bin/env python3
"""Can replace-only strand a player?  (proposed 22 Sept 2026)

Under replace-only a weight is never taken off a hook: you pick one from the rack and tap a
hook, and whatever was there goes back.  The first weight on a hook is free; changing it costs
one.  That removes an action, so it can remove a way out, and this asks whether it ever does -
over every reachable state of every board in the bank, not over a sample.

Three things have to hold on every board:

  1. NO DEAD END.  Every reachable state has at least one legal move.  A legal move needs some
     weight to be free in the rack, so this fails exactly when every weight's cap is used up.
  2. THE SOLUTION STAYS REACHABLE.  Filling is one-way - a filled hook is never empty again -
     so the full arrangements are a closed world, and the player has to be able to walk from
     whichever one they built to the right one by changing a hook at a time.
  3. THE BOARD CAN ALWAYS BE FILLED.  From any partial state the remaining hooks can still be
     filled without exceeding any weight's cap.

Run: python tools/check_replace.py            (the shipped bank)
     python tools/check_replace.py --tutor    (also the tutorial board in index.html)
"""
import json, os, re, sys
from collections import deque
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)


def load_bank():
    src = open(os.path.join(ROOT, 'boards.js'), encoding='utf-8').read()
    return [json.loads(m) for m in re.findall(r'^\{.*\}', src, re.M)]


def load_tutor():
    src = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    m = re.search(r'const TUTOR_BOARDS = \[(.*?)\];', src, re.S)
    if not m:
        return []
    return [json.loads(x) for x in re.findall(r'\{.*\}', m.group(1))]


def arms(n, out):
    if n['t'] == 'a':
        out.append(n)
        arms(n['l'], out)
        arms(n['r'], out)
    return out


def mass(n, cur, vals):
    if n['t'] == 'h':
        w = cur[n['i']]
        return 0 if w is None else vals[w]
    return mass(n['l'], cur, vals) + mass(n['r'], cur, vals)


def is_level(b, cur, arm_list):
    for a in arm_list:
        if mass(a['l'], cur, b['vals']) * a['ld'] != mass(a['r'], cur, b['vals']) * a['rd']:
            return False
    return True


def full_states(b):
    """Every all-hooks-filled arrangement that respects cap."""
    out = []
    for c in product(range(b['k']), repeat=b['nh']):
        ok = True
        for w in range(b['k']):
            if c.count(w) > b['cap']:
                ok = False
                break
        if ok:
            out.append(c)
    return out


def check(b, name):
    nh, k, cap = b['nh'], b['k'], b['cap']
    arm_list = arms(b['tree'], [])
    fails = []

    # ---- 3. the board can always be filled, whatever is on it already ----
    # placing (nh - filled) more weights needs that much room left, and the room left is
    # k*cap - filled, so the condition does not depend on which weights are where
    if k * cap < nh:
        fails.append('capacity %d < %d hooks: the board cannot even be filled' % (k * cap, nh))

    # ---- 1. no dead end ----
    # a state offers no move only when every weight is capped out, which needs filled >= k*cap;
    # the most that can ever be on the board is nh, so slack = k*cap - nh decides it outright
    if k * cap <= nh:
        fails.append('no slack: with %d hooks and %d x cap %d a full board leaves the rack empty' % (nh, k, cap))

    # ---- 2. the solution stays reachable from every full arrangement ----
    # filling is one-way, so once the board is full the player can only change hooks. Changing a
    # hook is its own inverse (the weight that leaves goes back to the rack), so this level of
    # the graph is undirected and reachability is one breadth-first walk from the solution.
    states = full_states(b)
    index = {s: i for i, s in enumerate(states)}
    sol = tuple(b['sol'])
    if sol not in index:
        fails.append('the recorded solution breaks its own cap')
    elif not is_level(b, list(sol), arm_list):
        fails.append('the recorded solution does not hang level')
    else:
        seen = {index[sol]}
        q = deque([sol])
        while q:
            cur = q.popleft()
            for i in range(nh):
                counts = [0] * k
                for j, w in enumerate(cur):
                    if j != i:
                        counts[w] += 1
                for w in range(k):
                    if w == cur[i] or counts[w] >= cap:
                        continue
                    nxt = cur[:i] + (w,) + cur[i + 1:]
                    j = index[nxt]
                    if j not in seen:
                        seen.add(j)
                        q.append(nxt)
        if len(seen) != len(states):
            fails.append('%d of %d full arrangements cannot reach the solution' % (len(states) - len(seen), len(states)))

    return fails, len(states)


def main():
    boards = []
    if '--tutor' in sys.argv:
        boards += [(b, 'tutorial %d' % (i + 1)) for i, b in enumerate(load_tutor())]
    boards += [(b, 'board %d' % (i + 1)) for i, b in enumerate(load_bank())]

    bad, total_states = 0, 0
    for b, name in boards:
        fails, n = check(b, name)
        total_states += n
        if fails:
            bad += 1
            for f in fails:
                print('FAIL %-14s %s' % (name, f))

    print('\n%d boards, %d full arrangements examined' % (len(boards), total_states))
    print('FAILED on %d board(s)' % bad if bad else 'No board can strand a player: every state has a move, '
          'every full arrangement reaches the solution, every board can be filled.')
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
