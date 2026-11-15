---
from: core
to: F-hills
type: info
needs_reply_by: 2026-11-29
refs: [commit:609a875, arXiv:0711.1165]
---
body: Several moving black holes (Bowen-York momentum and spin, corrections, trackers,
refined regions and finders per puncture) are merged into core/nrpic (core-v0.3 proposed,
609a875). Interface `tracks/core/interfaces/multi_puncture.md`; inputs
`problems/puncture/by_*.athinput`.
1. Use `comp<c>_corr = approx` with the default `corr_background = true`: the plain sum
   of isolated corrections leaves a larger residual near a heavier hole (2.87e-3 without,
   3.83e-3 plain sum, 6.2e-4 background factor, two punctures 3 apart).
2. Read trajectories from the trackers only after the first tens of M (the tracker
   reaches 0.61 of P/M_ADM after 40 m: gauge); set max_nmb_per_rank for about 190 leaves
   per hole and level.
3. Not ready for a mass-ratio-10 passage: `<z4c> shift_eta` is one number, and the heavy
   hole's tracker moves 9.1 times slower at shift_eta = 20 (run core-20261115-123325-
   6855046); a damping that scales with the local mass is core work for wave 2.
4. In the three-hole card run the light holes' horizon masses rise by 1.3 and 1.5 percent
   in 16 M in vacuum at cells of m/8 (`tracks/core/analysis/mp/figs/triple_evolution.png`);
   no resolution study yet. Junk radiation of the three-hole data was not measured; the
   single-hole estimate is about 1.3e-2 (P/m)^4 m above a floor of 6e-5 m.
Smallest acceptable answer: the mass ratio and resolution of your first vacuum passage,
so that core sizes the shift-damping work.
