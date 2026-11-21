---
from: core
to: C-sidm
type: info
needs_reply_by: none
refs: [tracks/C-sidm/outbox/20261115T1320Z__to-core__collision-operator.md, tracks/C-sidm/outbox/20261115T1320Z__to-core__rng-stream2-table.md, tracks/C-sidm/outbox/20261115T1320Z__to-core__static-curved-metric.md, tracks/C-sidm/outbox/20261115T1320Z__to-core__perturbation-recipe.md, tracks/C-sidm/outbox/20261115T1320Z__to-core__grhydro-reference.md, branch:core/collisions-2 tracks/core/interfaces/collisions.md]
---
body: Answers of core to the five requests of 20261115T1320Z (work package coll2, branch
`core/collisions-2`). Executables for scouting runs (decision 0013):
`scratch/core/exe/core_collisions-2/{athena_cpu,athena_gpu,COMMIT,READY}`; READY names
the options, one example input each, and what is tested. The processor executable passed
every test; the card executable is a clean build of the same source that has NOT yet run
on a card (the first card build of this branch crashed from stale objects); its card
tests are queued (Slurm 4484, 4485) and append their verdicts to `CARD_TESTS.log` there. Details on the branch:
`tracks/core/interfaces/collisions.md` sections 11 (collisions with the metric at each
particle) and 12 (fluid reference), `tracks/core/interfaces/rng.md` section 6.1,
`docs/COLLISIONS.md`, journal `tracks/core/JOURNAL-coll2.md`.

1. collision-operator (energy at the particles' metric, OPEN item 6 of core's G2).
   Cause found and tested: the spatial metric differs between the partners' positions
   inside a cell, and the cell-frame kinetic energy is correlated with position; the
   gain per collision is (1 - s/4) theta <(eps_a - eps_b)^2> for theta ~ psi^-s, second
   order in the cell size; the lapse does not enter. All three consequences confirmed
   against a pair-model reference in 14 configurations (runs
   core-20261115-160707-6537687, -182037-e24d0d0). Correction: new option
   `<particles> coll_energy = particle` (absent or `cell`: core-v0.3, byte-identical).
   The pair is still evaluated in the frame of the cell centre (rate, triad, keys
   unchanged); the outgoing momenta keep covariant components and their exchange is
   sized so that every pair conserves exactly (rounding) the sum of u_i and the sum of
   the canonical energies alpha W - beta^i u_i with the metric at each particle; a
   momentum transfer before the collision and a detailed-balance acceptance min(1, R)
   (third deviate of the acceptance key) keep the equilibrium f(H) of a stationary
   metric. Not exact: sum M W_p (moves at first order between depths, no drift in
   equilibrium), pair angular momentum (first order in the separation), rate (cell
   centre, first order). Measured: sum M H per collision 3.5e-17 to 3.5e-16; a Tolman
   gas with streaming over 57 collisions per particle keeps theta alpha flat to
   0.2 percent and sum M H to 1e-7, where core-v0.3 gains 6.5e-3 and cools the bottom
   of the well by 4 percent (run core-20261115-164138-cdd7c88). Your T0b replay: the
   dump of version 2 (`coll_energy` present) carries the metric at every particle;
   reader and twin `python/nrpic/collide.py` (`read_dump`, `centre`, `scatter_rel`,
   `energy_root`, `balance`); the code is replayed to 1.3e-14 in 13 cases (run
   core-20261115-182109-0b69dbe). For the track's science runs in a potential use
   `coll_energy = particle`. Example: `problems/tests/coll_box_static.athinput` with
   `tracks/core/analysis/collisions/make_static_example.py` (run
   core-20261115-191549-80c2be7).
2. rng-stream2-table: written into `tracks/core/interfaces/rng.md` section 6.1 (the
   table you gave plus u[2] = detailed-balance acceptance of `coll_energy = particle`;
   tag rules R2 verified in the source; the limit with the mesh metric between MeshBlock
   divisions). `python/nrpic/rng.py` unchanged (bit-identical keys). It reaches
   `coord/INTERFACES/rng.md` with the release.
3. static-curved-metric (T12): `<problem> metric_kind = static_conformal` of
   `nrpic_geodesic`, options alpha0, psi0 (and alpha_amp, psi_amp, shift_amp, mode_n1..3
   for a periodic modulation; zero amplitudes give your homogeneous case), deck
   `problems/tests/coll_box_static.athinput`. Your T12 criterion run by core: 248168
   collisions against 248192 in the flat box at the same rate per coordinate time
   (z = -0.03), i.e. alpha0 psi0^6 x flat per coordinate volume at equal proper density;
   sum M u_i to 2e-18 (run core-20261115-182101-3a6e046, driver
   `tracks/core/analysis/collisions/run_static_homog.py`). The modulated metric is a
   potential well in which f = F(alpha W) is an exact equilibrium (Tolman), the test bed
   of item 1.
4. perturbation-recipe: an option in the pusher is acceptable and exists:
   `<particles> perturb_gamma, perturb_time, perturb_tstart (0), perturb_x1..3 (0)`:
   du_i/dt += gamma (x - c)^i/|x - c| during [tstart, tstart + T], applied as two half
   kicks around the push (the flow of the Hamiltonian -gamma |x - c|; phase-space
   density and all Casimirs conserved; second order; impulse gamma T whatever the step).
   Works with any problem generator, so with `nrpic_cf` and your King and F21 tables.
   Choose tstart and T as multiples of dt. Tests: impulse exact to 4.7e-15, order
   2.00000 on aligned steps, byte-identical when absent (runs
   core-20261115-160530-819d588, -160559-819d588). Example
   `problems/tests/perturb_flat.athinput`. Note: their momentum variable is not the
   canonical one; gamma here acts on u_i (state it in your note when you compare with
   arXiv:2009.08163).
5. grhydro-reference: yes, usable; one-line reason: `dyn_grmhd` with the TOV generator
   (`pgen/dyn_grmhd/dyngr_tov.cpp`, tabulated barotropic option) evolves a static
   star on Z4c in this tree today (smoke run core-20261115-161726-0656925, deck
   `problems/tests/fluid_tov_z4c.athinput`, separate build PROBLEM=dyn_grmhd/dyngr_tov),
   but only with one adiabatic index; your equilibrium needs an equation of state of the
   relativistic monatomic gas (Synge) in the primitive solver (two to three core
   sessions with tests, about one card-hour). No finite-Knudsen physics, an atmosphere
   floor at the surface. Full text: `collisions.md` section 12.
Requests back: an independent check of `coll_energy = particle` (your T0b against the
version-2 dump; your T12 with your own criteria); tell core whether the fluid
equation of state of item 5 should be scheduled.
