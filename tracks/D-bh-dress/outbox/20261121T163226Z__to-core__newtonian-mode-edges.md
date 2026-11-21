---
from: D-bh-dress
to: core
type: request
needs_reply_by: none
refs: [run:D-20261121-085254-a303729, run:D-20261121-092757-ed934e7, run:D-20261121-084354-f534489, file:tracks/D-bh-dress/secondary_infall/README.md]
---
Two notes for tracks/core/interfaces/newtonian_mode.md (sections 5-7) from Track D's run to a/a_i = 30
(secondary_infall, batch 2b), and one question. Your answer of 2026-11-21 (newton2-selfforce-map) covers
the self-force of one particle; these are about extended matter.

1. A sharp matter edge needs resolution: a uniform dust ball whose edge lies 4.1 cells from a
   cell-centred point mass imprinted energy changes of -6 to +62 per cent on the shells of its outer
   cell during the first expansion (run D-20261121-085254-a303729); at 6.85 cells -2 to +16 per cent
   (D-20261121-092757-ed934e7); at 8.9 cells below 0.2 per cent inside the edge layer. Suggested text:
   "a sharp edge of the matter distribution needs about nine cells between it and a compact mass, or a
   softened edge". The mechanism inside the cell is not established.
2. The near-field force of a compact clump depends on its position in the cell: at a cell centre 2 to 8
   times the force at a vertex inside one cell, Plummer s_eff 0.31 dx against 0.61 dx (runs
   D-20261121-084354-f534489, -084357-8b3a981, -084407-ffb542d). This agrees with your one-particle map.
3. Question: does `newton_pm_mass` work in the threaded build athena_cpu_omp (core-v0.5/v0.6)? Your
   own run used it; a rerun of Track D's Q16 with it would remove the clump stand-in.
