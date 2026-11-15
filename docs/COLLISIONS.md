# Collisions between the particles (self-interacting species)

`athenak/src/particles/nrpic_collide.{hpp,cpp}` adds elastic, isotropic two-body
scattering between the massive particles of the NRPIC module: a Monte Carlo collision
step in the orthonormal frame of the normal observer of each mesh cell, after the push
and before the deposit. The contract (algorithm, random-number keys, history columns,
dump format, what is verified, limits) is `tracks/core/interfaces/collisions.md`
(proposal for `coord/INTERFACES/collisions.md`). This file says how to switch it on and
how to rerun its tests.

## Use

Input file, block `<particles>` (without `collisions` nothing changes, not even the
parameter list written to restart files):

    collisions       = true
    coll_sigma       = 6.75        # cross-section per unit mass, code units (a length)
    coll_cell_factor = 4           # collision cell = 4^3 mesh cells (1, 2 or 4)
    coll_pmax        = 0.1         # largest pair probability per sub-step aimed at
    coll_budget      = true        # optional: energy with the metric at the particles
    coll_energy      = particle    # in a gravitational field: see below

and `<job> rng_seed = N` (members of an ensemble differ in the seed only). All colliding
particles must have the same rest mass (`coll_weights = equal`, the default; a run with
unequal masses stops with an error). `coll_weights = nanbu` accepts unequal masses and
conserves energy and momentum on average only.

Units: G = c = 1. sigma [code] = sigma [cm^2/g] x (unit mass [g]) / (unit length [cm])^2.
Knudsen number of a cluster of central rest-mass density rho_c and radius R:
Kn = 1/(rho_c sigma R).

Output: `<basename>.coll.hst`, one record per step: collisions, expected collisions
(`sum_P`), sub-steps, particles per collision cell (`min_N`, `mean_N`), largest cell size
over mean free path (`max_dx_mfp`), sums of energy and momentum, pair defects. Reader:
`nrpic.collide.read_history` (Python).

What to watch in a production run:

- `mean_N`: the number of collisions is right at any occupation of the cells, but a
  relaxation rate was 2.6 percent low at 12 particles per collision cell and 7.5 percent
  low at 1.5; about 100 gave one percent. Raise `coll_cell_factor` or the particle
  number.
- `max_dx_mfp`: a collision cell should be smaller than the mean free path.
- `n_trunc` must stay zero (a pair probability above one); `max_nsub` shows how much
  the cells sub-cycle.
- The step enters at first order: a rate nu is high by nu^2 dt_c/2, dt_c = dt/n_sub.
- In a gravitational field set `coll_energy = particle`. Without it (the operator of
  release core-v0.3, `coll_energy = cell`) a pair conserves its energy with the metric
  of the cell centre only, and the collision steps raise the energy of the particles
  steadily: in the cluster test by 1.05e-8, 2.3e-9 and 1.1e-9 of the particle energy
  per collision for collision cells of 2, 1 and 0.5 M, and the energy at infinity
  (alpha W - beta^i u_i) by 1.5 times as much; they also carry heat out of a potential
  well in equilibrium. With `coll_energy = particle` every pair conserves the sum of
  u_i and the sum of alpha W - beta^i u_i with the metric at each particle to rounding,
  and an equilibrium of a static metric stays an equilibrium (interface text, section
  11). The option costs one metric reconstruction per colliding particle and step.
  Watch `n_noroot` (pairs left unscattered) and `n_balance` (collisions rejected for
  detailed balance): both should stay small against `n_coll`. The option is read only
  if present; its presence adds history columns 32 to 36 (`dH_particles`: the change of
  the canonical energy in the collision step, with `coll_budget = true`).

## Tests

All drivers are in `tracks/core/analysis/collisions/`; each writes `summary.json`
(field `ok`) and its figures into the directory it is given. Run them registered:

    cd <worktree>
    R=tracks/core/analysis/rng/runreg.py; C=tracks/core/analysis/collisions
    python3 $R --purpose "..." --cores 8 -- python3 {repo}/$C/run_rate.py {out} --nproc 8

| Driver | What | Processor time |
|---|---|---|
| `run_kernel_test.py` | kernels against 60-digit vectors of track C | 3 s |
| `run_replay.py` | one collision step against the Python twin `nrpic.collide.replay` | 4 min |
| `run_rate.py` | collision rate at four temperatures, conservation, null runs | 4 min, 8 cores |
| `run_relax.py` | relaxation to Maxwell-Juttner, entropy | 2.5 min, 4 cores |
| `run_conv_dt.py` | first-order convergence in the time step | 2 min, 8 cores |
| `run_cells.py` | cell size and `coll_cell_factor` in a homogeneous gas | 1 min, 8 cores |
| `run_smr.py` | one refined octant | 10 s |
| `run_repro.py` | MeshBlock divisions, restart, seed | 1 min, 6 cores |
| `run_unequal.py` | unequal masses | 1.5 min, 5 cores |
| `run_curved_box.py` | homogeneous curved metric on the mesh | 7 min, 3 cores (20 s on a card) |
| `run_cluster.py` | relativistic cluster with and without collisions; `--energy cell,particle` runs both values of `coll_energy` | card: 4.3 min per run |
| `gradient_ref.py`, `scbox.py` | reference of the pair model in the static metric with a gradient (no file of the code is read) | 10 min per group of cases |
| `run_gradient.py` | one collision step on frozen particles in that metric, both values of `coll_energy`, against the reference | 30 min, 6 cores |
| `run_tolman.py` | equilibrium in a potential well with streaming and collisions, both values | card: seconds; processor: 15 min at 1e5 particles |
| `run_static_homog.py` | constant lapse and conformal factor (test T12 of track C); the two values of `coll_energy` coincide | 5 min, 4 cores |
| `run_perturb.py` | the perturbing force `perturb_gamma` | 2 s |
| `rerun_wave1.py` | reruns the box tests with a new executable and compares all output files with wave 1 or with the release executable | 20 min |

Card: `sbatch -p preempt --gres=gpu:1 -c 2 -t 00:30:00 $C/gpu_job.sh <A|B|C|D> <card
executable> <baseline card executable>` from the root of the worktree (two cores: the
node has four in all).

Decks: `problems/tests/coll_box.athinput` (periodic Minkowski box: `nrpic_geodesic` with
the analytic Kerr-Schild functor at `bh_mass = 0`), `problems/tests/coll_box_curved.athinput`
(the same box with `<problem> metric_kind = homogeneous`: constant lapse and constant
non-diagonal spatial metric on the mesh), `problems/tests/coll_box_static.athinput`
(`<problem> metric_kind = static_conformal`: lapse alpha0 (1 + alpha_amp cos phi),
conformal factor psi0 (1 + psi_amp cos phi), shift beta^x = shift_amp sin phi, periodic
in the box; all amplitudes zero: a constant lapse and conformal factor),
`problems/tests/coll_box_ks.athinput` (analytic Kerr-Schild metric of a mass, for the
kinematics in a metric with shift that is not conformally flat).

## Perturbing an equilibrium (`perturb_gamma`)

`athenak/src/particles/nrpic_perturb.cpp`: during `[perturb_tstart, perturb_tstart +
perturb_time]` every particle with rest mass feels the radial force
du_i/dt = perturb_gamma (x - c)^i/|x - c| about the centre `perturb_x1..3` (outwards for
a positive value). It is the perturbation of the characteristic system of
arXiv:2009.08163 (`paper.tex` line 848) in the canonical variables of the pushers: the
flow of the added Hamiltonian -perturb_gamma |x - c|, which conserves the phase-space
density and hence every Casimir functional; no new initial data are needed. The force
is applied as two half kicks around the push (second order; the impulse over a run is
perturb_gamma x perturb_time whatever the step). Choose `perturb_tstart` and
`perturb_time` as multiples of the step: otherwise the last, partial kick adds an error
of second order with an irregular coefficient. Absent or zero: no effect at all.
Example: `problems/tests/perturb_flat.athinput`; test `run_perturb.py`.
