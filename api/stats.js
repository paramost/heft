// Read the daily counters back, protected by a token you set as the STATS_TOKEN env var.
//   /api/stats?token=YOURTOKEN            -> the last 60 days, ending today
//   /api/stats?token=YOURTOKEN&days=120   -> more (capped at 120)
//   /api/stats?token=YOURTOKEN&probe=1    -> the ?log=1 test namespace
// Returns { from, to, data: { <dayNo>: { opened, first_hang, solved, sw0, sw1, ... } } },
// omitting zeros. finish rate for a day = solved / opened.

const EPOCH = Date.UTC(2026, 8, 15);     // must match index.html's EPOCH (No 1 = 15 Sept 2026)
function todayNo() { const t = new Date(); return Math.floor((Date.UTC(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate()) - EPOCH) / 86400000) + 1; }

module.exports = async function handler(req, res) {
  const q = req.query || {};
  const want = process.env.STATS_TOKEN;
  if (!want || (q.token || '') !== want) { res.statusCode = 401; return res.end('unauthorized'); }

  const base = process.env.KV_REST_API_URL, tok = process.env.KV_REST_API_TOKEN;
  if (!base || !tok) { res.statusCode = 200; res.setHeader('Content-Type', 'application/json'); return res.end(JSON.stringify({ days: 0, data: {}, note: 'KV not connected yet' })); }

  const days = Math.min(Math.max(parseInt(q.days, 10) || 60, 1), 120);   // bound the pipeline size
  const pre = q.probe ? 't' : 'd';
  const to = todayNo() + 1;              // +1 so a player ahead of UTC still has today included
  const from = Math.max(1, to - days + 1);   // a window that ends at today, not a fixed range from day 1
  const cmds = [], meta = [];
  for (let d = from; d <= to; d++) {
    ['opened', 'first_hang', 'solved'].forEach(function (e) { cmds.push(['GET', pre + ':' + d + ':' + e]); meta.push([d, e]); });
    for (let sw = 0; sw <= 30; sw++) { cmds.push(['GET', pre + ':' + d + ':sw:' + sw]); meta.push([d, 'sw' + sw]); }
  }

  let arr = [];
  try {
    const r = await fetch(base + '/pipeline', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + tok, 'Content-Type': 'application/json' },
      body: JSON.stringify(cmds)
    });
    arr = await r.json();
  } catch (e) { res.statusCode = 502; return res.end('kv error'); }
  if (!Array.isArray(arr)) { res.statusCode = 502; return res.end('kv error'); }   // KV returned an error object, not a result array

  const data = {};
  arr.forEach(function (x, i) {
    const v = x && x.result != null ? Number(x.result) : 0;
    if (!v) return;
    const d = meta[i][0], e = meta[i][1];
    (data[d] = data[d] || {})[e] = v;
  });

  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({ from: from, to: to, data: data }));
};
