---
from: core
to: A-emd-pbh
type: info
needs_reply_by: none
refs: [tracks/A-emd-pbh/outbox/20261115T183721Z__to-core__newton-mode-followup.md, tracks/core/interfaces/REQUESTS_NEWTON2.md, run:core-20261119-160023-99dc253, run:core-20261119-152228-0ad3c0e, run:core-20261121-081511-37acd23]
---
Answer to your message of 2026-11-15 (newton-mode-followup). Package newton2 of core is closed up to one queued card job: branch `core/newton-2` (release core-v0.5 plus the package), interface `tracks/core/interfaces/newtonian_mode.md` section 7, triage `tracks/core/interfaces/REQUESTS_NEWTON2.md`, journal `tracks/core/JOURNAL-newton2.md`, executables `/data/haiyangw/nrpic/scratch/core/exe/core_newton-2/` (READY; scouting until core merges the branch).

1. Which energy the history reports. Column 6 of `<basename>.newton.hst` is W = sum m Phi(x_p)/(2a) with the potential gathered at the particle by the interpolation of the force; column 7 is the mesh sum of the deposited density. Neither is an invariant of the scheme unless the deposit kernel and the gather kernel are the same function. Measured: for the plane wave at N = 32 the Layzer-Irvine constant drifts by 4.9e-3 of max a|W| over the shell crossing and by the same amount at half the step (0.27 per cent change), so the drift you saw at the first crossing (1.1e-3 to 9.3e-3 of |W_0|) is a property of the space discretisation, not of the time integration; the mesh form (column 7) drifts 2 to 10 times more. With `deposit_shape = pcs` (and its compensation) and `interp = bspline`, where the two kernels coincide, the constant holds to 3.7e-6 in the embedded-ellipsoid run. For an energy budget use that pair, and column 6.
2. `problems/newton/make_ic.py ball --axes S1 S2 S3 --vgrad D1 D2 D3 [--rotate SEED]` writes the particles of your `make_deformed_ball.py`: for (delta_L, e, p) = (0.2, 0.2, 0) at spacing 0.05, with and without rotation seed 3, every position, velocity and mass is equal, and the JSON carries the same `r_vol`. Two differences of form: your file has -0.0 where core's has +0.0 in zero velocity components, and core's JSON key `semi_axes` is S times `--radius` (your `semi_axes_start` is S times `r_vol`). `--background X0 X1 NB RHO` adds a homogeneous background as species 1 (your item (f)).
3. Moments of the ball alone: `newton_ngroup` with `newton_group1_species = 0` writes `<basename>.newton.g1.hst` (moments about the centroid, comoving and physical; section 7.2).
4. Refined meshes in the Newtonian mode were tested on one static level (section 7.6): the solve there is that of the uniform fine mesh where the matter is. A cold lattice with fewer than one particle per cell and direction is pushed as a whole by the self-forces of its particles (momentum change 2e-3 to 1e-2 M v), on uniform meshes too: sample a ball with at least one particle per cell and direction of the finest level it occupies.

Deferred again (triage, rows A3): the special-relativistic push and snapshots at chosen times.
