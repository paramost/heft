// Read the daily counters back, protected by a token you set as the STATS_TOKEN env var.
//   /api/stats?token=YOURTOKEN            -> last 60 days
//   /api/stats?token=YOURTOKEN&days=200   -> more
//   /api/stats?token=YOURTOKEN&probe=1    -> the ?log=1 test namespace
// Returns { days, data: { <dayNo>: { opened, first_hang, solved, sw0, sw1, ... } } }, omitting
// zeros. finish rate for a day = solved / opened.

module.exports = async function handler(req, res) {
  const q = req.query || {};
  const want = process.env.STATS_TOKEN;
  if (!want || (q.token || '') !== want) { res.statusCode = 401; return res.end('unauthorized'); }

  const base = process.env.KV_REST_API_URL, tok = process.env.KV_REST_API_TOKEN;
  if (!base || !tok) { res.statusCode = 200; res.setHeader('Content-Type', 'application/json'); return res.end(JSON.stringify({ days: 0, data: {}, note: 'KV not connected yet' })); }

  const days = Math.min(Math.max(parseInt(q.days, 10) || 60, 1), 120);   // bound the pipeline size
  const pre = q.probe ? 't' : 'd';
  const cmds = [], meta = [];
  for (let d = 1; d <= days; d++) {
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

  const data = {};
  arr.forEach(function (x, i) {
    const v = x && x.result != null ? Number(x.result) : 0;
    if (!v) return;
    const d = meta[i][0], e = meta[i][1];
    (data[d] = data[d] || {})[e] = v;
  });

  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({ days: days, data: data }));
};
