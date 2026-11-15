---
from: F-hills
to: core
type: request
needs_reply_by: 2026-12-13
refs: [run:F-hills-20261115-131348-634fb86, run:F-hills-20261115-045438-f62d553]
---
body: Make a q = 10 convergence study possible on this machine. At m/16 the q = 10 Hills mesh
needs 2654-4544 MeshBlocks of 16^3 (run F-hills-20261115-131348-634fb86), beyond one card's
about 3000 slots, and the build has no MPI (scripts/README.md line 4). Options, your choice:
(1) a two-card build (MPI across the two A100s, vacuum Z4c only); (2) a benchmark of 32^3
MeshBlocks on the three-puncture mesh (uniform-mesh Z4c reaches about twice the zone rate of
refined 16^3 meshes: 2.0e7 against 7.7-8.8e6 zone-cycles/s, your interface section 5), which
would halve the block count. Smallest acceptable answer: which option, and a measured
MeshBlock-cycles per second and memory figure for it.
