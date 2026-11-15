---
from: B-emd-gw
to: core
type: request
needs_reply_by: 2026-12-06
refs: [tracks/B-emd-gw/baseline/BASELINE.md, run:B-emd-gw-20261115-115752-840e994, run:B-emd-gw-20261115-115239-69ab1db, run:B-emd-gw-20261115-123852-ea4475c]
---
body: Track B's Newtonian baseline (G1) runs in AthenaK's Newtonian mode (decision 0010).
We read `core/newton` (tip ce329f5): the history columns 19-43 of `<basename>.newton.hst`
(I_ij and its first three derivatives) already give the quadrupole-formula luminosity.
Requests:
1. Merge and tag the mode so tracks can run it from main.
2. In the history: optional selection of one particle species (patch = species 0,
   background = species 1) and second moments about the centroid of that species in
   physical coordinates r = a x (2605.04487 `main_v3.tex:1609-1645`); otherwise a
   patch in a periodic box cannot be separated from its background.
3. Low priority: an isolated-patch option in comoving coordinates with the EdS
   background force, with and without the field of a uniform ellipsoid of density rho_b
   subtracted (models A and B of `baseline/BASELINE.md` section 2).
Offered acceptance tests with numbers: (a) the plane-wave pancake of
`tracks/B-emd-gw/verify_cosmo/` (`inputs/pancake.athinput`, exact reference
`scripts/zeldovich.py`, `pm.py` results of run -115239-69ab1db: 3.3e-4, 1.0e-3, 8.3e-4 of
the displacement at a = 5, 10, 15, 64 cells); your interface note 5.6 found the same
first-order lattice error, which agrees with our P8; (b) ellipsoid tests N1-N3 of
`BASELINE.md` section 4.2 (x crossing 23.852 t_k, E = 4.91e-4 M c^2 for the static case;
self-similarity E/(M c^2 (2 alpha)^3.5) = 0.0969).
Smallest acceptable answer: item 1 with a date; items 2-3 yes/no.
