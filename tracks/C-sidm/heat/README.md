# heat: heat conduction with the collision operator (tests T6-T8 of collide/TESTS.md)

Helper package of C-sidm, wave 3a (2026-11-19). The heat-conduction tests T6 (temperature
step between two reservoirs at the long and the short mean-free-path end), T7
(conductivity from the isobaric mode) and T8 (convergence in time step, pair probability
and cell size) of `../collide/TESTS.md`, which nobody had run, with core's executables of
branch core/collisions-2 (`/data/haiyangw/nrpic/scratch/core/exe/core_collisions-2/`,
commit f46f159; `coll_energy = particle`, the corrected operator). Predictions and
outcomes, failed ones included: `JOURNAL.md`. No simulation code is written here
(decision 0010): the package has reference solutions, drivers, analysis and figures.

State: see "Results" (filled as runs finish) and "Pending runs".

## Contents

| Path | What |
|---|---|
| `inputs/heat.athinput` | periodic Minkowski box at x0 = 10 (flat Kerr-Schild functor), `nrpic_geodesic`, collision options of collisions.md on core/collisions-2; the drivers set mesh, step, sigma, seed, snapshots on the command line |
| `inputs/card_*.list` | card runs (batch launcher), written by `run_mode.py prep` |
| `scripts/heatlib.py` | paths, particle files (`../collide/analysis/make_box.py`), running the executable, reducing snapshots to slab sums or Fourier sums while a run goes on |
| `scripts/isobaric.py` | reference: nonlinear isobaric heat conduction in 1D (Lagrangian, kappa = f kappa_1(T), relativistic c_p, uniform pressure from the box volume); self-test |
| `scripts/design.py` | design numbers and predictions (windows, amplitude bias, fit error by Monte Carlo, cost) |
| `scripts/smoke.py` | S0: the deck runs; cost per particle and collision time; `particle` vs `cell` |
| `scripts/run_step.py` | T6 runs (parts a, b, c) on processors |
| `scripts/run_mode.py` | T7/T8 mode runs: `local` (processors), `prep` + list (card), `reduce` (card output) |
| `scripts/t2nosub.py` | T8 part 2: T2(b) at max P = 0.5 with and without sub-cycling |
| `scripts/an_step2.py` | T6 analysis (a: collisionless curve, slopes; b: f and literal statistic; c: transition) |
| `scripts/an_mode.py` | T7/T8 analysis (entropy-mode fit, f against the nonlinear reference, extrapolation in (k lambda)^2; collisionless check) |
| `results/` | JSON outputs copied from the run directories (run id in the name) |
| `figs/` | figures copied from the run directories (each looked at) |
| `JOURNAL.md` | predictions before each run, outcomes after |

## How to rerun

From the worktree root, with the worktree's `.venv`; every run registered with
`--package tracks/C-sidm/heat`:

    E=/data/haiyangw/nrpic/scratch/core/exe/core_collisions-2
    S="harness/bin/nrpic-run submit --kind scouting --gate G2 --package tracks/C-sidm/heat"
    $S --cores 2 --purpose "S0"     -- python3 tracks/C-sidm/heat/scripts/smoke.py
    $S --cores 2 --purpose "design" -- python3 tracks/C-sidm/heat/scripts/design.py
    $S --cores 2 --purpose "T6b"    -- python3 tracks/C-sidm/heat/scripts/run_step.py --part b --seeds 1 2 --nproc 2
    $S --cores 6 --purpose "T7"     -- python3 tracks/C-sidm/heat/scripts/run_mode.py local \
        --theta 0.003 --eps 0.2 --kl 0.4 0.2 0.1 --seeds 1 2 3 4 --n 400000 --nproc 6 --tag T7_
    $S --cores 4 --purpose "T6a"    -- python3 tracks/C-sidm/heat/scripts/run_step.py --part a --seeds 1 2 --nproc 4
    $S --cores 3 --purpose "T6c"    -- python3 tracks/C-sidm/heat/scripts/run_step.py --part c --seeds 1 --nproc 3
    $S --cores 2 --purpose "T8 T2b" -- python3 tracks/C-sidm/heat/scripts/t2nosub.py
    # analysis (one core each); run ids are resolved under scratch/C-sidm/
    $S --cores 1 --purpose "T7 analysis" -- python3 tracks/C-sidm/heat/scripts/an_mode.py T7 - <run_id> [<run_id> ...]   ("-": the run directory)

## Results

(filled below as the runs finish)

## Pending runs

(see the end of the package)

## Requests

(see the end of the package)
