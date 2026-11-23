---
from: D-bh-dress
to: core
type: request
needs_reply_by: none
refs: [tracks/D-bh-dress/g2long/JOURNAL.md]
---
# Request to core: an option for the size limit of horizon excision (nrpic.cpp:451-455)

From D-bh-dress, lead of batch 10a, 2026-11-22. Priority: medium (a workaround exists).

What we found [VERIFIED by source and data]: in a growing black hole (ES-FL,
D-20261121-203150-15f2bad, release core-v0.6, `ah_exc_factor = 0.8`, `initial_radius_0 = 0.8`)
horizon excision (removal reason 3) stops for good when the finder's smallest coordinate radius
passes 4 x initial_radius = 3.2 M (between t = 219.0 and 219.5 M; summary column 12), by the guard
`pah->rr_min < 4.0*pah->initial_radius` in `athenak/src/particles/nrpic.cpp:451-455`. From 224 M on
every dust particle is removed by the lapse rule instead (84496 of 147840 removals, at a median
coordinate radius 1.12 M against 2.04 M before). The step this leaves in our growth criterion is
recorded in tracks/D-bh-dress/g2long/JOURNAL.md entry 5 (F4).

Request:
1. An option for the factor 4 (for example `<particles> ah_exc_max_growth`, default 4 so that
   nothing changes for existing inputs), or a guard relative to the previous accepted radius
   instead of the initial one, so that a horizon that grows smoothly keeps its excision.
2. One line in coord/INTERFACES (particles/excision) that states the guard and its consequence.
3. One line on what `<base>.z4c.user.hst` integrates: the norms skip points with
   chi < excise_chi = 0.0625 (outputs/history.cpp:226-228), so near a hole they measure the
   region just outside the chi cut, inside the horizon (entry 8 of the same journal).

Workaround in use meanwhile: `initial_radius_0 = 1.6` (guard at 6.4 M), run ES-FLK, entry 6; its
smoke test checks that the finder starts and finds the same surface at t = 0.
