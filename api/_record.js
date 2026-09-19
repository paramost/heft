// The record, server side (1.13.0): the same pack / unpack / merge the page runs, so the server
// can merge what a device sends into what it holds. Keep the two in step - the page's copy is
// the one under "The record" in index.html. A leading underscore keeps this out of the routes.
//
// Merge rule, in one line: the base record stands on every tie. History is a union keyed by day
// and the first solve of a day is the one that counts; the streak follows the later last-solved
// day; preferences follow the newer change; the board follows the later day, then the finished
// one, then the one with more weights hung.

const HEX32 = /^[0-9a-f]{32}$/;

function pack(d) {
  const o = { v: 2, key: d.key || '', streak: d.streak || 0, lastSolved: d.lastSolved || 0, maxStreak: d.maxStreak || 0,
    solved: d.solved || 0, hist: d.hist || {}, notesOn: !!d.notesOn, scaleOff: !!d.scaleOff, prefAt: d.prefAt || 0,
    board: d.day ? { day: d.day, cur: d.cur || [], touches: d.touches || [], notes: d.notes || [], done: !!d.done, sig: d.sig || '' } : null };
  return Buffer.from(JSON.stringify(o)).toString('base64').replace(/[+]/g, '-').replace(/[/]/g, '_').replace(/=+$/, '');
}

function unpack(t) {
  t = String(t).replace(/-/g, '+').replace(/_/g, '/'); t += '='.repeat((4 - t.length % 4) % 4);
  const o = JSON.parse(Buffer.from(t, 'base64').toString('utf8'));
  if (!o || typeof o !== 'object' || Array.isArray(o)) throw new Error('bad record');
  const int = function (x, hi) { return Number.isInteger(x) && x >= 0 && x <= hi ? x : 0; };
  const r = { key: HEX32.test(o.key) ? o.key : '', streak: int(o.streak, 100000), lastSolved: int(o.lastSolved, 100000),
    maxStreak: int(o.maxStreak, 100000), solved: int(o.solved, 100000), hist: {},
    notesOn: o.notesOn === true, scaleOff: o.scaleOff === true, prefAt: int(o.prefAt, 1e13) };
  if (o.hist && typeof o.hist === 'object') {
    Object.keys(o.hist).slice(0, 5000).forEach(function (k) {
      const d = Number(k), v = o.hist[k];
      if (Number.isInteger(d) && d >= 1 && d <= 100000 && Number.isInteger(v) && v >= 0 && v <= 999) r.hist[d] = v;
    });
  }
  const b = o.board;
  if (b && typeof b === 'object' && !Array.isArray(b) && Number.isInteger(b.day) && b.day >= 1 && b.day <= 100000
      && Array.isArray(b.cur) && b.cur.length <= 12) {
    r.day = b.day; r.done = b.done === true; r.sig = typeof b.sig === 'string' ? b.sig.slice(0, 16) : '';
    r.cur = b.cur.map(function (x) { return (Number.isInteger(x) && x >= 0 && x <= 9) ? x : null; });
    r.touches = (Array.isArray(b.touches) ? b.touches : []).slice(0, 12).map(function (x) { return int(x, 999); });
    r.notes = (Array.isArray(b.notes) ? b.notes : []).slice(0, 12).map(function (x) { return typeof x === 'string' ? x.slice(0, 4) : ''; });
  }
  return r;
}

function run(h, L) { let n = 0; while (h[L - n] != null) n++; return n; }   // consecutive solved days ending at L

function merge(b, r) {                          // b is the record; r is arriving. On a tie, b stands.
  b.hist = b.hist || {};
  Object.keys(r.hist || {}).forEach(function (k) { if (!(k in b.hist)) b.hist[k] = r.hist[k]; });   // first solve of a day counts
  const bl = b.lastSolved || 0, rl = r.lastSolved || 0;
  if (rl > bl) {                                // the arriving record has played since: continue the streak if the days join
    const cont = (rl === bl + 1) ? (b.streak || 0) + 1 : 0;
    b.streak = Math.max(r.streak || 0, cont, run(b.hist, rl)); b.lastSolved = rl;
  } else {
    b.streak = Math.max(b.streak || 0, rl === bl ? (r.streak || 0) : 0, run(b.hist, bl));
  }
  b.maxStreak = Math.max(b.maxStreak || 0, r.maxStreak || 0, b.streak || 0);
  b.solved = Math.max(b.solved || 0, r.solved || 0, Object.keys(b.hist).length, b.streak || 0);
  if ((r.prefAt || 0) > (b.prefAt || 0)) { b.notesOn = !!r.notesOn; b.scaleOff = !!r.scaleOff; b.prefAt = r.prefAt; }
  else if (!b.prefAt && !r.prefAt) { b.notesOn = !!(b.notesOn || r.notesOn); b.scaleOff = !!(b.scaleOff || r.scaleOff); }
  if (r.day) {                                  // the board: later day, then the finished one, then the one further along
    const prog = function (c) { return (c || []).filter(function (x) { return x != null; }).length; };
    const bd = b.day || 0;
    if (r.day > bd || (r.day === bd && !b.done && (r.done || prog(r.cur) > prog(b.cur)))) {
      b.day = r.day; b.cur = (r.cur || []).slice(); b.touches = (r.touches || []).slice(); b.notes = (r.notes || []).slice(); b.done = !!r.done; b.sig = r.sig || '';
    }
  }
  if (!b.key && r.key) b.key = r.key;
  return b;
}

module.exports = { HEX32, pack, unpack, merge, run };
