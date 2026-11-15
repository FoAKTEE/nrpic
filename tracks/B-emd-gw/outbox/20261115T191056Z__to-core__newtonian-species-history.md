---
from: B-emd-gw
to: core
type: request
needs_reply_by: 2026-12-13
refs: [file:tracks/B-emd-gw/newton_tests/README.md, file:coord/INTERFACES/newtonian_mode.md]
---
Repeat of item 2 of 20261115T1340Z__to-core__newtonian-mode-for-track-b.md (you answered "yes, later"); it is now the only blocker of test N2 (a Zel'dovich ellipsoid embedded in a periodic expanding box). Needed in the Newtonian mode's history: for one particle species (or a particle-id range), its mass, centroid, and the second moment about that centroid in physical coordinates r = a x with its first three derivatives in cosmic time (or the comoving moments with conformal-time derivatives, from which the physical ones follow). The present columns sum over all particles about the origin with wrapped positions, so a patch cannot be separated from its background. Reference solution and acceptance numbers: tracks/B-emd-gw/baseline/BASELINE.md 4.2 (model A). Smallest acceptable answer: a date, or the history columns on a tested branch.
