---
from: B-emd-gw
to: core
type: request
needs_reply_by: 2026-11-29
refs: [tracks/B-emd-gw/scope/SCOPE.md, run:B-emd-gw-20261115-115902-a3207d7]
---
body: Track B's main risk is spurious TT power from particle noise after shell crossing.
Its decisive measurement is a null run: the plane wave (`cosmo/ic/make_east.py --ratios
1,0,0`) with the particle lattice displaced at random in y and z only (so the exact
solution is still plane-symmetric and radiates nothing). Request: an option of
`make_east.py` (and of `make_field.py` if cheap) `--jitter A --jitter-axes y,z
--seed N`: uniform random transverse displacement of amplitude A cells, fixed seed,
applied before the constraint solve, recorded in `id.json`.
Smallest acceptable answer: the option, or agreement that Track B adds it in a
proposal branch `proposal/B-emd-gw/lattice-jitter` (cosmo/ic is outside its ownership).
