// The record, server side (1.13.0): the same pack / unpack / merge the page runs, so the server
// can merge what a device sends into what it holds. Keep the two in step - the page's copy is
// the one under "The record" in index.html. A leading underscore keeps this out of the routes.
//
// Merge rule, in one line: the base record stands on every tie. History is a union keyed by day
// and the first solve of a day is the one that counts; preferences follow the newer change; the
// board follows the later day, then the finished one, then the one with more weights hung. No
// counters are kept or merged: the page computes every stat from the history (1.14.0).

const HEX32 = /^[0-9a-f]{32}$/;

function pack(d) {
  const o = { v: 3, key: d.key || '', hist: d.hist || {}, devices: (d.devices || []).slice(0, 10), notesOn: !!d.notesOn, scaleOff: !!d.scaleOff, prefAt: d.prefAt || 0,
    board: d.day ? { day: d.day, cur: d.cur || [], touches: d.touches || [], notes: d.notes || [], done: !!d.done, sig: d.sig || '' } : null };
  return Buffer.from(JSON.stringify(o)).toString('base64').replace(/[+]/g, '-').replace(/[/]/g, '_').replace(/=+$/, '');
}

function unpack(t) {
  t = String(t).replace(/-/g, '+').replace(/_/g, '/'); t += '='.repeat((4 - t.length % 4) % 4);
  const o = JSON.parse(Buffer.from(t, 'base64').toString('utf8'));
  if (!o || typeof o !== 'object' || Array.isArray(o)) throw new Error('bad record');
  const int = function (x, hi) { return Number.isInteger(x) && x >= 0 && x <= hi ? x : 0; };
  const r = { key: HEX32.test(o.key) ? o.key : '', hist: {}, notesOn: o.notesOn === true, scaleOff: o.scaleOff === true, prefAt: int(o.prefAt, 1e13),
    devices: (Array.isArray(o.devices) ? o.devices : []).filter(function (x) { return HEX32.test(x); }).slice(0, 10) };
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

function merge(b, r) {                          // b is the record; r is arriving. On a tie, b stands.
  b.hist = b.hist || {};
  Object.keys(r.hist || {}).forEach(function (k) { if (!(k in b.hist)) b.hist[k] = r.hist[k]; });   // a union of days; the first solve of a day counts
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
  b.devices = (b.devices || []).slice();
  (r.devices || []).forEach(function (x) { if (b.devices.indexOf(x) < 0 && b.devices.length < 10) b.devices.push(x); });
  return b;
}

module.exports = { HEX32, pack, unpack, merge };
