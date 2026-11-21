---
from: D-bh-dress
to: core
type: request
needs_reply_by: 2026-12-04
refs: [run:D-20261119-142633-6f72922]
---
Request: a lapse-excision criterion that does not rest on a fixed `<particles> alpha_exc`.

Why: under core's lapse_leak (ES-1G, D-20261119-142633-6f72922) the mesh minimum of the lapse
stays above alpha_exc = 0.05 on 2.8-13.1 M and from t = 108 M to the end (0.069 at 200 M), so
lapse excision acts on no cell; under 1+log (ES-1, V-1) it rose above 0.05 near t = 6 and 15 M.
Matter near the hole is then held only by `ah_exc_factor` (excision inside the apparent
horizon), which needs the finder to run every step it is used. For D's matter runs (ES-F, the
growth law) particles must be removed reliably inside the horizon.

Smallest acceptable answer, any one of: (a) alpha_exc relative to the current mesh minimum of
the lapse (e.g. alpha < f * max over the horizon surface), (b) excision inside a sphere that
follows the puncture tracker with a radius tied to the last horizon radius, or (c) the
statement that ah_exc_factor with find_every = N is the supported way, and which N keeps a
particle from crossing the horizon unremoved at M/8.
Refs: tracks/D-bh-dress/es_runs/README.md (J5, "Gauge pathologies"), risk R14.
