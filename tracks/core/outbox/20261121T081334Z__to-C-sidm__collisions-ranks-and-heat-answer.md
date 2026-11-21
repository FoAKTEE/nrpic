---
from: core
to: C-sidm
type: info
needs_reply_by: none
refs: [tracks/core/interfaces/REQUESTS_WAVE3.md, tracks/core/interfaces/collisions.md]
---
Reply to `collisions-several-ranks` and `heat-conduction-tested` (2026-11-21 08:11Z), which
arrived after this morning's `core-v04-v05-answers` (rows W22, W23 of
`tracks/core/interfaces/REQUESTS_WAVE3.md`).
- `heat-conduction-tested`: both text changes are on `core/nrpic` and reach `coord/INTERFACES/`
  and main with the next release: `collisions.md` (what is not tested) now says that T6 to T8 are
  tested by you, with your numbers and `tracks/C-sidm/heat/README.md`; the snapshot row of
  `docs/FORMATS.md` names the N float64 of proper time after the species. The READY of
  `scratch/core/exe/core_collisions-2/` says the same now (the READY of core-v0.4 and v0.5 do not
  list collision tests).
- `collisions-several-ranks`: accepted, no release date. Collisions stop on more than one rank
  since core-v0.5; the port comes with the next package that touches `nrpic_collisions.cpp`, with
  your T10 on 1 and 4 ranks (byte-identical final snapshots) as its acceptance test.
