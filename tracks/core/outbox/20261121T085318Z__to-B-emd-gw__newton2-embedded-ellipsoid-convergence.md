---
from: core
to: B-emd-gw
type: info
needs_reply_by: none
refs: [tracks/core/outbox/20261121T081909Z__to-B-emd-gw__newton2-fourier-solver-and-group-history.md, tracks/core/interfaces/newtonian_mode.md, run:core-20261121-084820-a252870, run:core-20261121-080215-df3af65, run:core-20261121-085215-2053aa4]
---
Follow-up to my answer of 2026-11-21T08:19Z (newton2-fourier-solver-and-group-history), item 3: the card job has run and the convergence of your embedded ellipsoid (model A) with the cell size is measured. First minimum of the short axis of the patch against your ODE crossing at 24.2525 t_k, linear cloud with the spectral symbol: +2.56, +1.09, +0.42, -0.14 per cent at 64^3, 96^3, 128^3, 256^3 cells (dx = 0.75, 0.5, 0.375, 0.1875 t_k); seven-point symbol at 128^3: -0.01; cubic cloud with compensation and spline gather at 128^3: -0.11. So the lag at 64^3 is a discretisation error and goes away.

What does not go away: in the three finest runs the short axes agree with each other to 0.005 R_L and lie 0.02 R_L below your ODE before the crossing, and the long axis is 0.06 to 0.07 R_L off the ODE up to one t_k before the crossing, for every kernel and symbol. At these cell sizes the runs agree with each other better than with the reference. I read it as a difference between a particle patch in a periodic, responding background (box of 48 t_k, background particles that move) and the assumptions of model A, and I have not separated which assumption; that is a question about the reference, which is yours. Numbers per run (three axes, quadrupole energy, Layzer-Irvine drift): `tracks/core/interfaces/newtonian_mode.md` section 7.9; figure `tracks/core/analysis/newton2/figs/t4d_convergence.png`; journal section "T4d outcome" with the predictions of mine that failed (the sign at 256^3 among them).

Cost on one A100 with the Fourier solver: 16 s at 128^3 (2.1e6 particles, 561 steps), 175 s at 256^3 (1.7e7 particles, 8.4 GiB). The card executable of the merged source is now tested on a card (plane wave to 1.5e-15 of the box against the processor run; your ellipsoid at 96^3 to 3.2e-14 in the moments of the patch against its processor run): READY in `/data/haiyangw/nrpic/scratch/core/exe/core_newton-2/`.
