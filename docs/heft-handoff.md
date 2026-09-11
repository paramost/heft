# Heft — start here

**This file contains no state.** No build numbers, no file lists, no what-shipped-when. All of that
lives in the repo itself and in `heft-decisions.md`, and every previous attempt to summarise it here
went stale within a day. If you are tempted to record a version number in this file, don't.

---

## 1. Get the real thing

```
git clone https://github.com/paramost/heft.git
```

Work from that clone. **Never** work from an attached file, a pasted copy, a project snapshot, or
your own memory of what the repo contains. Those have all been wrong before, sometimes for hours,
and the difference is invisible until it costs a session.

After any commit — yours or Dan's — clone again before saying anything about repo state. "It should
be there now" is not verification.

The live site is whatever `index.html` in `main` says it is. Vercel publishes automatically on
commit to the default branch.

## 2. Read before proposing

`docs/heft-decisions.md`, in full, before suggesting anything. It records constraints that took a
long time to establish, several of which look arbitrary and are not. Two entries carry the rest:

- **Whatever the player knows, they should have learned by playing.** Everything else follows from
  this, including that nothing in the interface may lock, hint, or indicate correctness.
- **Nothing is asserted that could be measured**, and the measurement is of the thing itself rather
  than a proxy for it.

Its *Working notes* section is the working agreement — how Dan wants this done. Read that too.

Then: `docs/heft-plan.md` for what comes next, `docs/heft-generation.md` for the board generator,
`docs/heft-publishing.md` for deploying and testing.

## 3. When something blocks you, fix the blockage

Do not build a careful argument on top of a proxy because the real thing is out of reach. Ask for
what you need, or go and get it. A confident answer about the wrong artifact is worse than no
answer, because nobody can tell the difference until it breaks.

This has been the single most expensive failure mode in this project's history. Every instance
looked reasonable at the time.

## 4. Before you start work

Explain what you intend to do and get agreement first. That covers writing code, editing files, and
running measurements — measuring is not free. Say what it would cost and what it would tell us.

A question is not a request to rebuild, and it is not a request to measure either.

## 5. When play and analysis disagree, play wins

Dan tests by playing on a phone. That judgement has been right where confident analysis has been
wrong, repeatedly and on the findings that mattered most. If a measurement says the drawing is fine
and play says it isn't, the measurement is aimed at the wrong quantity.

Corollary: if something feels wrong, check what was recently taken away before measuring what is
still there.

## 6. Bumping the build

The build string lives in three places: `const BUILD`, the `data-build` attribute on `<html>`, and
an HTML comment in `<head>`. The script checks all three agree and prints `· BUILD MISMATCH` beside
the build number if they don't. Bump all three in the same commit, and never reuse a number.
