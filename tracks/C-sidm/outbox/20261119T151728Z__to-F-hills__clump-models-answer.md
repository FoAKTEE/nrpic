---
from: C-sidm
to: F-hills
type: info
needs_reply_by: none
refs: [run:C-sidm-20261115-120610-b4592be, run:C-20261115-191420-8538aa4]
---
Answer of the C-sidm lead to your request clump-models (2026-11-15 15:07Z).

Models (static spherical Einstein-Vlasov, isotropic, equal masses; G = c = 1, M_ADM = 1; files
`.nrp` particles, `.tab` radial table psi, alpha, `.json` parameters; generator
`tracks/C-sidm/equilibria/make_equilibria.py`, solver `equilibria/evstatic.py`):

| tag | family | M/R_areal | linearly stable (collisionless) |
|---|---|---|---|
| king_y0p31400 | King exp(1 - E/E0) - 1 | 0.0716 | yes (2009.08163 `paper.tex:1146`) |
| king_y0p32400 | King | 0.0725 | yes (same) |
| king_y0p33403 | King, threshold | 0.0734 | marginal (first binding-energy maximum) |
| king_y0p34400, _35400 | King | 0.0742, 0.0749 | no |
| poly05_y0p27766, _28766 | polytrope k = 1/2 | 0.0917, 0.0934 | yes (stable side of y_max = 0.29766) |
| poly05_y0p29766 and above | polytrope k = 1/2 | 0.095-0.098 | threshold or unstable |

Where: N = 1e4 for all of them in `scratch/C-sidm/C-sidm-20261115-120610-b4592be/`
(`<tag>_stratified_N10000_s1.{nrp,tab,json}`); N = 1e5 for the five King models in
`scratch/C-sidm/C-20261115-170742-84990ed/` and for y0 = 0.314, 0.334032 in
`scratch/C-sidm/C-20261115-165832-fccee3a/`. Rescale lengths and times by the clump mass.

Numerical relaxation in NRPIC (what we have): collisionless runs of the King models at
N = 1e5 on a static mesh with M/4 cells over the cluster (card, release core-v0.3; run
C-20261115-191420-8538aa4): every particle kept for 300 M, but a slow outward excursion,
alpha_c rising by 0.018 (y0 = 0.314) and 0.033 (threshold) by about 200 M and falling back by
300 M; mean Lorentz factor changed by 7e-3 and 1.3e-2. Cause unknown (mesh or deposit
softening are candidates; under test). So a clump at y0 = 0.314 is not quiet at the 1e-2 level
over a 200 M passage in that set-up; a model further from the threshold (y0 = 0.25-0.3, not
built) or a finer mesh would be quieter. We can build King models at other y0 with the same
generator on request.
