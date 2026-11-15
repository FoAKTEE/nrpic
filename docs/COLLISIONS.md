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
- In a gravitational field the collision steps raise the particle energy slightly (the
  partners of a pair sit at different depths of the potential): column `dE_particles`
  with `coll_budget = true`. In the cluster test it was 1e-8 of the particle energy per
  collision for cells of 2 M; see the interface text, section 9, for its dependence on
  the cell size.

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
| `run_cluster.py` | relativistic cluster with and without collisions | card: 4.3 min per run |

Card: `sbatch -p preempt --gres=gpu:1 -c 2 -t 00:30:00 $C/gpu_job.sh <A|B|C|D> <card
executable> <baseline card executable>` from the root of the worktree (two cores: the
node has four in all).

Decks: `problems/tests/coll_box.athinput` (periodic Minkowski box: `nrpic_geodesic` with
the analytic Kerr-Schild functor at `bh_mass = 0`), `problems/tests/coll_box_curved.athinput`
(the same box with `<problem> metric_kind = homogeneous`: constant lapse and constant
non-diagonal spatial metric on the mesh).
