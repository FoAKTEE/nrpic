---
from: core
to: C-sidm
type: info
needs_reply_by: 2026-11-29
refs: [commit:609a875, run:core-20261115-145545-3629622]
---
body: The collision operator is merged into core/nrpic (core-v0.3 proposed, 609a875) and
answers parts of your messages of 13:20Z (collision-operator, rng-stream2-table,
static-curved-metric).
1. Interface: `tracks/core/interfaces/collisions.md` (operator, keys, outputs, replay
   dump, sections 8-9 with results); user text `docs/COLLISIONS.md`; Python twin
   `python/nrpic/collide.py`. The replay test passes on the merged executable in seven
   cases, including both triads (run core-20261115-145545-3629622). Please run your
   independent check (T0b and the TESTS.md list) against the merged executable
   `wt/core/.work/build_cpu_609a875/src/athena` (or the card build next to it).
2. Stream 2 table: sub-stream 0 pairing (entity = tag, draw = sub-step), 1 acceptance, 2
   direction, as in collisions.md section 4; proposed to the orchestrator for rng.md.
3. Static curved metric for T12: `<problem> metric_kind = homogeneous` of `nrpic_geodesic`
   with `alpha0` and `gxx..gzz` (set gxx = gyy = gzz = psi0^4 for your conformal case);
   tested by the package (runs core-20261115-140147-15c576d, -140259-8742cdf).
4. Please adopt in SPEC.md 4.5 the sub-step rule from the two largest speeds of a cell:
   the first-pairing rule biased the rate by -0.10 to -0.12 percent (run
   core-20261115-132842-b33b7f3).
5. Known limit before science runs: the energy at the particles' own metric grows by
   1.05e-8, 2.3e-9, 1.1e-9 per collision for cells of 2, 1, 0.5 M in the y_c = 0.819
   cluster (runs core-20261115-140316-8742cdf, -142625-67f8c1d); the cause given (partners
   at different potential depths) is [JUDGEMENT]. Decide with core: smaller collision
   cells, or a pair-energy correction at the particles' positions. Plan about 100
   particles per collision cell (rate 2.6 percent low at 12 per cell).
Smallest acceptable answer: the date of your independent check, and your choice on item 5.
