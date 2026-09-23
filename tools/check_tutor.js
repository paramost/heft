// The tutorial board, checked rather than asserted (1.14.14). Lifts TUTOR_BOARDS out of
// index.html and answers the four things the teaching depends on:
//   - the stated solution really is level
//   - it is the ONLY level arrangement, so the lesson has one answer
//   - the obvious first try (lightest on the left) leans, and leans visibly
//   - one weight alone throws the arm to full tilt, which is the empty-hook lesson
// Run: node tools/check_tutor.js
const fs = require('fs');

const page = fs.readFileSync(__dirname + '/../index.html', 'utf8');
const m = page.match(/const TUTOR_BOARDS = \[([\s\S]*?)\];/);
if (!m) { console.error('TUTOR_BOARDS not found in index.html'); process.exit(1); }
const BOARDS = JSON.parse('[' + m[1].trim() + ']');

const MAX_TILT = 15;           // degrees, the shipped range
const FLOOR = 1.25;            // degrees, the shipped minimum lean for any non-zero imbalance

function mass(n, cur, vals) {
  return n.t === 'h' ? (cur[n.i] == null ? 0 : vals[cur[n.i]]) : mass(n.l, cur, vals) + mass(n.r, cur, vals);
}
// the arm's angle is its fractional torque imbalance, linear, with a floor under any non-zero one
function lean(n, cur, vals) {
  const tl = mass(n.l, cur, vals) * n.ld, tr = mass(n.r, cur, vals) * n.rd;
  if (tl + tr === 0) return 0;
  const f = (tr - tl) / (tr + tl);
  if (f === 0) return 0;
  const d = Math.abs(f) * MAX_TILT;
  return Math.sign(f) * Math.max(d, FLOOR);
}
function arms(n, out) { if (n.t === 'a') { out.push(n); arms(n.l, out); arms(n.r, out); } return out; }
function level(b, cur) { return arms(b.tree, []).every(function (a) { return lean(a, cur, b.vals) === 0; }); }

// every arrangement of the weights over the hooks, respecting cap
function every(b) {
  const out = [], cur = new Array(b.nh).fill(null), used = new Array(b.k).fill(0);
  (function rec(i) {
    if (i === b.nh) { out.push(cur.slice()); return; }
    for (let w = 0; w < b.k; w++) {
      if (used[w] >= b.cap) continue;
      used[w]++; cur[i] = w; rec(i + 1); used[w]--; cur[i] = null;
    }
  })(0);
  return out;
}

let bad = 0;
const say = function (ok, msg) { if (!ok) bad++; console.log((ok ? 'ok   ' : 'FAIL ') + msg); };

BOARDS.forEach(function (b, n) {
  console.log('--- tutorial board ' + (n + 1) + ': ' + b.nh + ' hooks, ' + b.k + ' weights, levers ' + b.tree.ld + ':' + b.tree.rd + ', values ' + b.vals.join('/') + ' ---');

  say(level(b, b.sol), 'the stated solution hangs level');

  const all = every(b), lev = all.filter(function (c) { return level(b, c); });
  say(lev.length === 1, 'exactly one arrangement hangs level (found ' + lev.length + ' of ' + all.length + ')');
  say(JSON.stringify(lev[0]) === JSON.stringify(b.sol), 'and it is the one recorded in sol');

  // the obvious first try: take the weights in rack order, left to right
  const naive = []; for (let i = 0; i < b.nh; i++) naive.push(i % b.k);
  const nl = lean(b.tree, naive, b.vals);
  say(Math.abs(nl) >= 3, 'lightest-first leans ' + Math.abs(nl).toFixed(1) + ' deg, well over the 1.25 floor');
  say(!level(b, naive), 'lightest-first is not accidentally the answer');

  // one weight alone: an empty hook is genuinely zero mass, so the arm goes to full tilt
  const one = new Array(b.nh).fill(null); one[0] = b.sol[0];
  say(Math.abs(lean(b.tree, one, b.vals)) === MAX_TILT, 'one weight alone throws the arm to the full ' + MAX_TILT + ' deg');

  // THE LESSON ITSELF: a swap is one weight lifted off one hook, so the obvious first try must be
  // repairable by changing exactly ONE hook. The first tutorial board failed this - two weights on
  // two hooks means the repair needs both, which is what made it teach the wrong unit.
  let oneChange = null;
  for (let i = 0; i < b.nh && !oneChange; i++) {
    for (let w = 0; w < b.k; w++) {
      if (w === naive[i]) continue;
      const t = naive.slice(); t[i] = w;
      const counts = new Array(b.k).fill(0); t.forEach(function (x) { counts[x]++; });
      if (counts.some(function (n) { return n > b.cap; })) continue;
      if (level(b, t)) { oneChange = [i, w]; break; }
    }
  }
  say(!!oneChange, oneChange ? 'one lift repairs the first try: hook ' + oneChange[0] + ' takes the ' + b.vals[oneChange[1]]
                             : 'NO single change repairs the first try - the board teaches the wrong unit');

  // and every wrong full arrangement is visible, or the board would lie
  const worst = Math.min.apply(null, all.filter(function (c) { return !level(b, c); })
    .map(function (c) { return Math.abs(lean(b.tree, c, b.vals)); }));
  say(worst >= FLOOR, 'the quietest wrong arrangement still leans ' + worst.toFixed(1) + ' deg');
});

console.log(bad ? '\n' + bad + ' FAILED' : '\nall checks pass');
process.exit(bad ? 1 : 0);
