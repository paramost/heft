// Anonymous, aggregate-only event logging for the daily. The page sends {day, event, swaps?}
// at most once per day per device; this increments per-day counters in Vercel KV (Upstash Redis)
// over its REST API - no npm dependency, no rows, no id, no IP. The worst an abuser can do is
// inflate counts; there is nothing personal here to leak. Rate limiting is deliberately omitted
// for v1 (see the security review notes) - if counts get spammed, add a hashed-IP cap here.
//
// Keys: d:<day>:<event> and d:<day>:sw:<swaps> for the live daily; t:<...> for ?log=1 probes.

// tutorial_offer is the card being shown, tutorial_start a player taking it, tutorial_done
// finishing it - the only way to tell whether the teaching works or is being skipped (1.14.14)
const EVENTS = { opened: 1, first_hang: 1, solved: 1, tutorial_offer: 1, tutorial_start: 1, tutorial_done: 1 };

module.exports = async function handler(req, res) {
  if (req.method !== 'POST') { res.statusCode = 405; return res.end(); }

  const base = process.env.KV_REST_API_URL, tok = process.env.KV_REST_API_TOKEN;
  // Before the KV store is connected (or if it ever drops), silently no-op rather than error.
  if (!base || !tok) { res.statusCode = 204; return res.end(); }

  try {
    let b = req.body;
    if (typeof b === 'string') { try { b = JSON.parse(b); } catch (e) { b = {}; } }
    b = b || {};

    const day = Number(b.day);
    if (!Number.isInteger(day) || day < 1 || day > 100000) { res.statusCode = 204; return res.end(); }
    if (!Object.prototype.hasOwnProperty.call(EVENTS, b.event)) { res.statusCode = 204; return res.end(); }  // own keys only, not inherited (constructor, __proto__, ...)

    const pre = b.probe ? 't' : 'd';
    const cmds = [['INCR', pre + ':' + day + ':' + b.event]];
    if (b.event === 'solved') {
      let sw = Number(b.swaps);
      if (!Number.isInteger(sw) || sw < 0) sw = 0;
      if (sw > 30) sw = 30;                       // bounded bucket set: no arbitrary keys
      cmds.push(['INCR', pre + ':' + day + ':sw:' + sw]);
    }

    await fetch(base + '/pipeline', {
      method: 'POST',
      headers: { Authorization: 'Bearer ' + tok, 'Content-Type': 'application/json' },
      body: JSON.stringify(cmds)
    });
  } catch (e) { /* never surface an error to the client */ }

  res.statusCode = 204;
  res.end();
};
