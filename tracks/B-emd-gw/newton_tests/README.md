# newton_tests (helper package of B-emd-gw, wave 2)

The Newtonian baseline of Track B run in AthenaK's Newtonian mode (release core-v0.3,
`<particles> pusher = newton`, `coord/INTERFACES/newtonian_mode.md`), processor build
`.work/build_cpu_v03`: the plane-wave pancake against the exact Zel'dovich solution up to
shell crossing (P1, P2), the homogeneous ellipsoid with the quadrupole history against the
semi-analytic baseline of wave 1 (N1, model C of `../baseline/BASELINE.md` 4.2), and the
(2 alpha)^(7/2) scaling as exact self-similarity of the code (N3). N2 (embedded ellipsoid
in a periodic box) is not run: it needs a per-species history the mode lacks (Requests).
Predictions, outcomes and the failed predictions: `JOURNAL.md`. Labels: [VERIFIED] (run id
given), [JUDGEMENT], [TO VERIFY]. Units G = c = 1.

## Results

Registered analysis: ANALYSIS_RUN (outputs `results/pancake.json`,
`results/ellipsoid.json`, figures in `figs/`, each looked at).

RESULTS_BODY

## Files

| Path | Content |
|---|---|
| `JOURNAL.md` | predictions (written before each run) and outcomes, including the failed ones |
| `inputs/pancake.athinput` | periodic expanding box, numerics of `cosmo/newton/pm.py` in the verify_cosmo pancake (cubic cloud, compensation 1/6 and 7/15, cubic-spline force) |
| `inputs/ellipsoid.athinput` | isolated domain, multipole boundary of order 4, no expansion, cloud-in-cell, Catmull-Rom |
| `inputs/card_pancakes.list` | the 64^3 pancakes for one card (run B-20261115-163653-f6324ea, queued) |
| `scripts/make_particles.py` | particle files: `pancake-east` (the verify_cosmo particles, from `pm.east_particles`), `pancake-sin` (equal-mass Zel'dovich lattice that never wraps), `ellipsoid` (lattice inside the Zel'dovich ellipsoid at t_turn) |
| `scripts/run_case.sh` | one AthenaK run in `$NRPIC_RUN_DIR/<name>/`: generator, then the processor executable |
| `scripts/run_selfsim.sh` | the three rescaled ellipsoid runs of N3 (alpha = 0.05, 0.1, 0.2) |
| `scripts/analyze_pancake.py` | P1, P2, H1: trajectories and history against the exact solutions, pm.py, the discrete-Laplacian growth law |
| `scripts/analyze_ellipsoid.py` | N1, N3: crossing time, Q and its derivatives, P_GW, E against the ODE (nominal and equivalent ellipsoid), convergence, snapshots, self-similarity |
| `results/*.json` | copies of the analysis outputs |
| `figs/*.png` | copies of the figures (PDF in the run directory) |

## Runs (manifests in `tracks/B-emd-gw/runs/`, outputs in `scratch/B-emd-gw/<run id>/`)

| Run id | Content | Wall time |
|---|---|---|
| B-20261115-163556-ad5637f | P1 east pancake, n = 32, to a = 42 | 13 min, 1 core |
| B-20261115-163558-20244f2 | P2 sin pancake, n = 32, to a = 25 | 10 min |
| B-20261115-165349-81a17bc | H1d east pancake, n = 16 | 1 min |
| B-20261115-165351-b38db6f | H1d sin pancake, n = 16 | 1 min |
| B-20261115-163613-790095f | N1 ellipsoid, N = 32 (7 736 particles) | 1.5 min |
| B-20261115-163615-7bc8b30 | N1 ellipsoid, N = 64 (61 456 particles) | 8 min |
| B-20261115-163617-085c093 | N1 ellipsoid, N = 128 (491 344 particles) | about 63 min |
| B-20261115-163618-ea94065 | N1f ellipsoid, N = 64, step 0.01 | 16 min |
| B-20261115-163620-5b286c1 | N3 alpha = 0.05, 0.1, 0.2 at N = 32 | 4 min |
| B-20261115-163621-0ae44f1 | N3 alpha = 0.05, 0.1, 0.2 at N = 64 | 25 min |
| B-20261115-163629-a96748c | particle files of the 64^3 pancakes for the card | seconds |
| B-20261115-163653-f6324ea | card: P1 east and P2 sin at n = 64 (0.4 card-hours reserved) | QUEUED (Slurm job 4459) |
| ANALYSIS_RUN | analysis of all of the above except the card run | |

## Rerun

From the worktree root, with the worktree's `.venv` (`harness/bin/nrpic-env create
--no-kokkos`); every command below is what the manifests record.

    P=tracks/B-emd-gw/newton_tests
    S="harness/bin/nrpic-run submit --kind scouting --gate G1 --package $P --cores 1 --background"
    $S --purpose ... -- bash $P/scripts/run_case.sh east32 pancake-east "--n 32 --delta 0.05 --L 1" \
        $P/inputs/pancake.athinput particles/traj_ntrack=32
    $S --purpose ... -- bash $P/scripts/run_case.sh sin32 pancake-sin "--n 32 --delta 0.05 --L 1" \
        $P/inputs/pancake.athinput particles/traj_ntrack=0 particles/hist_dcycle=1 time/tlim=8.0
    # n = 16: add mesh/nx1=16 ... meshblock/nx1=8 ... particles/dt=0.015625 (traj_ntrack=16)
    $S --purpose ... -- bash $P/scripts/run_case.sh ell64 ellipsoid "--n 64 --half 12 --ppd 2" \
        $P/inputs/ellipsoid.athinput mesh/nx1=64 mesh/nx2=64 mesh/nx3=64 \
        meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32       # N = 32: meshblock 16
    $S --purpose ... -- bash $P/scripts/run_selfsim.sh 64
    ANALYSIS_COMMAND

When the card run has finished (`harness/bin/nrpic-run finish B-20261115-163653-f6324ea`),
add to the pancake analysis
`--east 64:scratch/B-emd-gw/B-20261115-163653-f6324ea/east64 --pm 64:scratch/B-emd-gw/B-emd-gw-20261115-115239-69ab1db/n64 --sin 64:scratch/B-emd-gw/B-20261115-163653-f6324ea/sin64`
(the particle file of those runs is the absolute path in the batch list; the analysis
reads `particles.json` from the case directory, so copy
`scratch/B-emd-gw/B-20261115-163629-a96748c/{east64,sin64}/particles.{json,nrp}` into the
two case directories first). Test H1b of `JOURNAL.md` is decided by that run.

## Requests

REQUESTS_BODY
