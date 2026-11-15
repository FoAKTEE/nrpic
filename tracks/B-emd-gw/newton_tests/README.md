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

To core (Newtonian mode; the earlier request is
`tracks/B-emd-gw/outbox/20261115T1340Z__to-core__newtonian-mode-for-track-b.md`):
1. N2 cannot be run without a history of one particle species: time, a, the mass of the
   species, its centroid, and its second moment about that centroid in physical
   coordinates r = a x with the first three derivatives in cosmic time (or the
   comoving moments and their conformal-time derivatives, from which this package can
   form the physical ones). The current columns sum over all particles about the origin
   with wrapped positions, so a patch cannot be separated from its background. Repeats
   item 2 of the earlier request; it is now the only blocker of N2.
2. The seven-point Laplacian sets the error of the mode in the pancake at the
   resolutions Track B will use (H1 of `JOURNAL.md`, confirmed at n = 16 and 32): the
   force on a mode with kh = 2 pi/32 is too strong by (kh)^2/12 = 3.2e-3, which gives
   1.4e-3 of the displacement at a = 2 and 2.4 % rms in the jerk d3I_xx, against
   1.1e-4 for the spectral pm.py with the same particles. Request: say whether a
   fourth-order option on periodic uniform meshes is planned (a Mehrstellen stencil
   with source correction, or a spectral solve for the periodic root grid), so that
   the Newtonian reference does not carry a larger error than the GR run it is
   compared with; otherwise Track B quotes the second-order error with every
   comparison.
3. Low priority, documentation: the history's d3I is the one-step difference quotient;
   for the ellipsoid with eight particles per cell the averaged and the raw quadrupole
   energies differ by under 1 % (N = 64), so the raw column is usable there; with one
   particle per cell core's note 5.4 found 8.6 % rms. Worth a line in
   `newtonian_mode.md` that the particle number per cell, not the step, sets it.

To the lead of B-emd-gw:
4. The card run B-20261115-163653-f6324ea (P1 and P2 at n = 64, 0.4 card-hours reserved,
   Slurm job 4459) was still queued when this package closed. When it has run:
   `harness/bin/nrpic-run finish B-20261115-163653-f6324ea`, then the pancake analysis
   with the n = 64 cases (command under Rerun). It decides H1b (predicted error 3.5e-4
   and 7.3e-4 of the displacement at a = 2 and 5).
5. G1 criterion 2 of `stage/G1/STATUS.md` ("the Newtonian baseline reproduces the scaling
   of the literature"): the N-body part now exists in the code (N1, N3 here); the lead
   decides whether the first-order convergence of the energy to the first crossing
   (N1) is enough for the criterion or whether a finer mesh is wanted (refined meshes
   in the Newtonian mode are not verified, `newtonian_mode.md` section 6).
6. The 2605.04487 benchmark as N-body: N1 gives the crossing time to 0.2 % and the
   energy to the first crossing to about 20 % at N = 64 in a few minutes of one
   processor; the semi-analytic factor of about ten between the ODE energy and the
   Zel'dovich estimate on [t_turn, t_col] (BASELINE.md T4) is reproduced by particles
   (N1 values against 5.15e-5 M c^2).

To orch: none (the harness commands worked; the one failed analysis run was a relative
path of mine).
