// The transfer code (1.10.2): a player's record, parked for ten minutes under a four-digit code
// so it can be typed into another device. POST {rec} parks it and answers {code}; GET ?code=
// hands it back once and deletes it. The record is the packed string the page already makes for
// ?restore= (streak, best, solved, hist - no id, no name), capped at 4KB. Guessing is capped at
// ten a minute per address: a hashed IP that itself expires in sixty seconds is the only thing
// about a person this server ever holds. A guessed code within its ten minutes wins a streak the
// guesser can only show themselves.

const crypto = require('crypto');
const TTL = 600, GUESSES = 10;

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
    if (req.method === 'POST') {
      let b = req.body; if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } } b = b || {};
      const rec = b.rec;
      if (typeof rec !== 'string' || rec.length < 8 || rec.length > 4096 || !/^[A-Za-z0-9_-]+$/.test(rec)) return json(400, { error: 'bad record' });
      for (let i = 0; i < 6; i++) {                                   // a fresh code; retry on the rare collision
        const code = String(1000 + crypto.randomInt(9000));
        const ok = await kv([['SET', 'x:' + code, rec, 'EX', String(TTL), 'NX']]);
        if (ok[0] === 'OK') return json(200, { code: code, ttl: TTL });
      }
      return json(503, { error: 'busy' });
    }
    if (req.method === 'GET') {
      const ip = String((req.headers['x-forwarded-for'] || '').split(',')[0] || req.socket && req.socket.remoteAddress || '');
      const rk = 'rl:' + crypto.createHash('sha256').update(ip).digest('hex').slice(0, 16);
      const n = await kv([['INCR', rk], ['EXPIRE', rk, '60']]);
      if (Number(n[0]) > GUESSES) return json(429, { error: 'slow down' });
      const code = String((req.query || {}).code || '');
      if (!/^[0-9]{4}$/.test(code)) return json(400, { error: 'bad code' });
      const got = await kv([['GET', 'x:' + code], ['DEL', 'x:' + code]]);   // read once, then gone
      if (!got[0]) return json(404, { error: 'no such code' });
      return json(200, { rec: got[0] });
    }
    res.statusCode = 405; res.end();
  } catch (e) { res.statusCode = 502; res.end(); }
};
