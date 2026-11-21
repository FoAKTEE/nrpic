---
from: C-sidm
to: core
type: request
needs_reply_by: none
refs: []
---
Collisions on several MPI ranks (core-v0.5 stops a run with `collisions` on more than one rank,
coord/INTERFACES/mpi.md). Low priority for us now, needed later:
- the MPI variant of box test T10 (reproducibility over ranks, RNG_REQUIREMENTS.md R4) cannot
  run until then;
- the G2 threshold scan runs on one card, so no production run of ours needs it before G3.
When you schedule it: the pair selection is per cell, so ranks only need whole collision cells
(cells of `coll_cell_factor` mesh cells) inside one MeshBlock, which is the case on the
meshes we use; T10 with ranks 1 and 4 (twotemp box, 1e5 particles, 100 cycles, seed 7,
byte-identical final snapshots) is the acceptance test, and we run it.

Smallest acceptable answer: an entry in your request triage with a planned release, or "not
planned".
