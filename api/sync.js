// Sync (1.13.0): one record per anonymous key, so a player's devices share it. GET ?key= hands
// the record back; POST {key, rec} merges what a device sends into what is held and hands the
// merged record back - the server merges too, so a stale device can never overwrite a newer one.
// The key is 128 random bits the player's devices hold; there is no name, no email, no id but
// that. Records are capped at 4KB and expire after 400 days without a write. Reads and writes
// are capped at sixty a minute per address, by a hashed IP that itself expires in a minute.

const crypto = require('crypto');
const R = require('./_record.js');
const TTL = 400 * 86400, PER_MIN = 60;

module.exports = async function handler(req, res) {
  const base = process.env.KV_REST_API_URL, tok = process.env.KV_REST_API_TOKEN;
  if (!base || !tok) { res.statusCode = 503; return res.end(); }
  async function kv(cmds) {
    const r = await fetch(base + '/pipeline', { method: 'POST', headers: { Authorization: 'Bearer ' + tok, 'Content-Type': 'application/json' }, body: JSON.stringify(cmds) });
    const a = await r.json(); if (!Array.isArray(a)) throw new Error('kv');
    return a.map(function (x) { return x && x.result; });
  }
  const json = function (code, obj) { res.statusCode = code; res.setHeader('Content-Type', 'application/json'); res.setHeader('Cache-Control', 'no-store'); res.end(JSON.stringify(obj)); };

  try {
    const ip = String((req.headers['x-forwarded-for'] || '').split(',')[0] || req.socket && req.socket.remoteAddress || '');
    const rk = 'rs:' + crypto.createHash('sha256').update(ip).digest('hex').slice(0, 16);
    const n = await kv([['INCR', rk], ['EXPIRE', rk, '60']]);
    if (Number(n[0]) > PER_MIN) return json(429, { error: 'slow down' });

    if (req.method === 'GET') {
      const key = String((req.query || {}).key || '');
      if (!R.HEX32.test(key)) return json(400, { error: 'bad key' });
      const got = await kv([['GET', 's:' + key]]);
      if (!got[0]) return json(404, { error: 'no record' });
      return json(200, { rec: got[0] });
    }
    if (req.method === 'POST') {
      let b = req.body; if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } } b = b || {};
      const key = String(b.key || ''), rec = b.rec;
      if (!R.HEX32.test(key)) return json(400, { error: 'bad key' });
      if (typeof rec !== 'string' || rec.length < 8 || rec.length > 4096 || !/^[A-Za-z0-9_-]+$/.test(rec)) return json(400, { error: 'bad record' });
      let incoming; try { incoming = R.unpack(rec); } catch (e) { return json(400, { error: 'bad record' }); }
      const got = await kv([['GET', 's:' + key]]);
      let held = null; if (got[0]) { try { held = R.unpack(got[0]); } catch (e) { held = null; } }
      const merged = held ? R.merge(held, incoming) : incoming;
      merged.key = key;
      const packed = R.pack(merged);
      if (packed.length > 4096) return json(413, { error: 'record too large' });
      await kv([['SET', 's:' + key, packed, 'EX', String(TTL)]]);
      return json(200, { rec: packed });
    }
    res.statusCode = 405; res.end();
  } catch (e) { res.statusCode = 502; res.end(); }
};
