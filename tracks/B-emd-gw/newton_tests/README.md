# newton_tests (helper package of B-emd-gw, wave 2)

The Newtonian baseline of Track B run in AthenaK's Newtonian mode (release core-v0.3,
`<particles> pusher = newton`, `coord/INTERFACES/newtonian_mode.md`), processor build
`.work/build_cpu_v03`, one card run of the release card build: the plane-wave pancake
against the exact Zel'dovich solution up to shell crossing (P1, P2), the homogeneous
ellipsoid with the quadrupole history against the semi-analytic baseline of wave 1 (N1,
model C of `../baseline/BASELINE.md` 4.2), and the (2 alpha)^(7/2) scaling as an exact
self-similarity of the code (N3). N2 (embedded ellipsoid in a periodic box) is not run:
it needs a per-species history the mode lacks (Requests, item 1). Predictions, outcomes
and the failed predictions: `JOURNAL.md`. Units G = c = 1. Every number below is
[VERIFIED] with the run id given; interpretations are marked [JUDGEMENT].

## Results

Registered analyses: B-20261115-173904-a7297e3 (pancakes, `results/pancake.json`,
`figs/pancake_*.png`) and B-20261115-174405-af11300 (ellipsoid, `results/ellipsoid.json`,
`figs/ell_*.png`). Every figure was looked at.

### P1 Plane-wave pancake against Zel'dovich and pm.py (`figs/pancake_east.png`)

The particles of the verify_cosmo pancake (delta = 0.05, L = 1, one per cell, cubic
cloud with compensation, cubic-spline force, step L/(4n)); n = 16, 32 on processors,
n = 64 on a card (B-20261115-165349-81a17bc, B-20261115-163556-ad5637f,
B-20261115-163653-f6324ea). Largest sheet error against the continuum in units of the
displacement (a - 1) d/k:

| n | a = 2 | a = 5 | a = 10 | a = 15 | first sheet crossing |
|---|---|---|---|---|---|
| 16 | 5.64e-3 | 1.16e-2 | 1.84e-2 | 2.48e-2 | a = 21.87 |
| 32 | 1.39e-3 | 2.99e-3 | 4.42e-3 | 5.76e-3 | 21.34 |
| 64 | 3.51e-4 | 7.42e-4 | 1.20e-3 | 1.41e-3 | 21.16 |
| H1 prediction, n = 32 / 64 | 1.41e-3 / 3.51e-4 | 2.94e-3 / 7.33e-4 | 4.09e-3 / 1.02e-3 | 4.79e-3 / 1.19e-3 | |
| pm.py, n = 32 / 64 (run B-emd-gw-20261115-115239-69ab1db) | 1.1e-4 / 4.8e-5 | 6.1e-4 / 3.3e-4 | 2.1e-3 / 1.0e-3 | 1.7e-3 / 8.3e-4 | 21.55 / 21.22 |

- The error of the Newtonian mode before shell crossing is set by the seven-point
  Laplacian of the multigrid solve: the force on the fundamental mode is too strong by
  F - 1 = [(kh/2)/sin(kh/2)]^2 - 1 = (kh)^2/12 (3.2e-3 at n = 32), and linear theory
  with that force (hypothesis H1 of `JOURNAL.md`) predicts the measured error to 2 % at
  a <= 5 for n = 16, 32 and 64; it falls by four per doubling. H1 was formed after the
  n = 32 run and then tested by predictions written before the n = 16 and n = 64 runs.
  pm.py (spectral) does not have this error, so at n = 32 the mode's error is 5 to 13
  times pm.py's at a <= 5 (predictions P1a and P1b failed; they assumed that the
  lattice error dominates both codes). AthenaK - pm.py falls by 4.0 from n = 32 to 64.
- Plane symmetry is kept to 1.3e-15 L; the record times of AthenaK and pm.py agree
  exactly.

### P2 Second-moment history columns on an exact pancake (`figs/pancake_sin_moments.png`)

Equal-mass Zel'dovich lattice that never wraps (runs B-20261115-165351-b38db6f,
B-20261115-163558-20244f2, B-20261115-163653-f6324ea); exact I_xx = c0 + c1 a + c2 a^2
and d3I_xx = 3 c2 a^(1/2) for a = (1 + t/2)^2. Errors for 1.2 <= a <= 15:

| n | I_xx - c0 | dI_xx | d2I_xx (of the largest value) | d3I_xx rms relative |
|---|---|---|---|---|
| 16 | 8.1e-3 | 1.05e-2 | 6.4e-2 | 9.3 % |
| 32 | 2.0e-3 | 2.6e-3 | 1.6e-2 | 2.4 % |
| 64 | 5.1e-4 | 6.6e-4 | 3.9e-3 | 0.61 % |

All second order. H1 carries half to three quarters of the d3I error (mean signed
error 0.31 % against 0.17 % from H1 at 2 <= a <= 5, n = 64); the remainder is also of
second order and is not explained. Transverse and off-diagonal derivatives vanish to
4e-13 of max d2I_xx; the Layzer-Irvine constant holds to 2.9e-6, 7.9e-7, 2.1e-7 of
max a|W| (n = 16, 32, 64).

### N1 Static isolated ellipsoid against the ODE (model C) (`figs/ell_quadrupole.png`, `figs/ell_convergence.png`, `figs/ell_snapshots.png`)

The 2605.04487 benchmark ellipsoid at t_turn = 9.53 t_k, eight particles per cell,
box [-12, 12]^3, multipole boundary; N = 32, 64, 128 (7 736 to 491 344 particles; runs
B-20261115-163613-790095f, -163615-7bc8b30, -163617-085c093) and a step check
(-163618-ea94065). ODE: first x crossing 23.8524 t_k, E(t_turn -> t_x) = 4.9135e-4 M c^2.

| N | t_x / t_k | t_x error | E / M c^2 (raw d3I) | against the ODE | averaged against averaged ODE |
|---|---|---|---|---|---|
| 32 | 24.0659 | +0.90 % | 3.22e-4 | -34.4 % | -29.8 % |
| 64 | 23.8955 | +0.18 % | 4.01e-4 | -18.4 % | -13.2 % |
| 128 | 23.8604 | +0.034 % | 4.44e-4 | -9.7 % | -5.0 % |
| Richardson | 23.8513 (order 2.3) | -0.005 % | 4.95e-4 (order 0.88) | +0.7 % | |

- The crossing time converges at second order to the ODE value; Q and Q'' follow the
  ODE to 8e-4 and 7e-3 of their range at N = 64 (2e-4 and 1.6e-3 at N = 128) for
  t <= t_x - 1; Q''' averaged over 0.05 t_turn to 3 %.
- The quadrupole-formula energy to the first crossing converges at first order and is
  below the ODE at every N; the deficit comes from the last t_k before the crossing,
  where the thin axis spans a few cells (up to t_x - 1 the energy agrees to 1.5 % at
  N = 64 and 0.27 % at N = 128) [JUDGEMENT on the cause]. Averaging Q''' over
  0.05 t_turn biases the ODE energy itself by -7 %; compare raw with the exact ODE or
  averaged with averaged.
- Step 0.01 against 0.02: t_x within 2e-7, raw E within 1e-4 (averaged 7e-4). K + W holds to 5e-5 (N = 128)
  up to t_x - 1 and to 2e-3 up to t_x. Momentum, centre of mass and the off-diagonal
  quadrupole stay at rounding (the set-up is reflection-symmetric).
- The particles reproduce the factor of about ten between the energy to the first
  crossing and the Zel'dovich estimate on [t_turn, t_col] (5.15e-5 M c^2, BASELINE.md
  T4).

### N3 Self-similarity, the (2 alpha)^(7/2) law (`figs/ell_selfsim.png`)

Rescaled copies of the benchmark at alpha = 0.05, 0.1, 0.2 (runs
B-20261115-163620-5b286c1 at N = 32, -163621-0ae44f1 at N = 64): E/(M c^2 (2 alpha)^3.5)
= 0.061787 (N = 32), 0.076375 (N = 64) from the averaged Q''' (raw: 0.062059, 0.077205),
the same for all four alpha to 3e-14, and t_x/t_turn to 3e-15. The scaling of
2403.15126 (Omega ~ sigma^(7/2)) holds in the code exactly for the single patch; the
constant approaches the ODE's F_C = 0.09465 as N1 converges (computed from the N1
energies: raw, N = 128: 0.0855; Richardson 0.0954).

### What these results mean for Track B [JUDGEMENT]

- The mode is ready for the single-patch baseline: crossing times to well below 1 % at
  64 cells across the box, the quadrupole and its first two derivatives to 1e-3, the
  energy to the first crossing with a first-order error that needs N >= 128 or
  extrapolation for 10 % or better.
- In periodic boxes the Newtonian reference carries a second-order force error of
  (kh)^2/12 per mode; for a GR-against-Newton comparison wave number by wave number
  (BASELINE.md 4.3) that error has to be quoted or removed (Requests, item 2).

## Files

| Path | Content |
|---|---|
| `JOURNAL.md` | predictions (written before each run) and outcomes, including the failed ones |
| `inputs/pancake.athinput` | periodic expanding box, numerics of `cosmo/newton/pm.py` in the verify_cosmo pancake |
| `inputs/ellipsoid.athinput` | isolated domain, multipole boundary of order 4, no expansion, cloud-in-cell, Catmull-Rom |
| `inputs/card_pancakes.list` | the 64^3 pancakes for one card (batch list of run B-20261115-163653-f6324ea) |
| `scripts/make_particles.py` | particle files: `pancake-east` (verify_cosmo particles from `pm.east_particles`), `pancake-sin` (equal-mass Zel'dovich lattice that never wraps), `ellipsoid` (lattice inside the Zel'dovich ellipsoid at t_turn) |
| `scripts/run_case.sh` | one AthenaK run in `$NRPIC_RUN_DIR/<name>/`: generator, then the processor executable (`none` as input: particle file only) |
| `scripts/run_selfsim.sh` | the three rescaled ellipsoid runs of N3 |
| `scripts/analyze_pancake.py` | P1, P2, H1 |
| `scripts/analyze_ellipsoid.py` | N1, N3 |
| `results/pancake.json`, `results/ellipsoid.json` | copies of the analysis outputs |
| `figs/*.png` | copies of the figures (PDF in the run directories) |

## Runs (manifests in `tracks/B-emd-gw/runs/`, outputs in `scratch/B-emd-gw/<run id>/`)

| Run id | Content | Wall time |
|---|---|---|
| B-20261115-163556-ad5637f | P1 east pancake, n = 32, to a = 42 | 13 min, 1 core |
| B-20261115-163558-20244f2 | P2 sin pancake, n = 32, to a = 25 | 10 min, 1 core |
| B-20261115-165349-81a17bc | H1d east pancake, n = 16 | 1 min |
| B-20261115-165351-b38db6f | H1d sin pancake, n = 16 | 1 min |
| B-20261115-163629-a96748c | particle files of the 64^3 pancakes | 1 s |
| B-20261115-163653-f6324ea | card (Slurm job 4459): P1 east and P2 sin at n = 64 | 5.4 min, 0.089 card-hours |
| B-20261115-163613-790095f | N1 ellipsoid, N = 32 | 1.4 min |
| B-20261115-163615-7bc8b30 | N1 ellipsoid, N = 64 | 8.4 min |
| B-20261115-163617-085c093 | N1 ellipsoid, N = 128 | 64 min, 1 core |
| B-20261115-163618-ea94065 | N1f ellipsoid, N = 64, step 0.01 | 16 min |
| B-20261115-163620-5b286c1 | N3 at N = 32 | 4 min |
| B-20261115-163621-0ae44f1 | N3 at N = 64 | 24 min |
| B-20261115-170149-75036cf | pancake analysis, FAILED (relative scratch paths) | |
| B-20261115-170156-2d69627 | pancake analysis n = 16, 32 (superseded by -173904-) | |
| B-20261115-173904-a7297e3 | pancake analysis n = 16, 32, 64 (cited) | 6 s |
| B-20261115-174251-3698196 | ellipsoid analysis (superseded by -174405-, numbers identical) | |
| B-20261115-174405-af11300 | ellipsoid analysis (cited) | 8 s |

Card time used: 0.089 card-hours. Processor time of the registered runs: about 2.4
core-hours (plus unregistered smoke tests of a few minutes, `JOURNAL.md`).

## Rerun

From the worktree root, with the worktree's `.venv` (`harness/bin/nrpic-env create
--no-kokkos`); the manifests record every command exactly. Paths into `scratch/` must be
absolute (the worktree has no `scratch/`).

    P=tracks/B-emd-gw/newton_tests
    S=/data/haiyangw/nrpic/scratch/B-emd-gw
    R="harness/bin/nrpic-run submit --kind scouting --gate G1 --package $P --cores 1 --background"
    $R --purpose ... -- bash $P/scripts/run_case.sh east32 pancake-east "--n 32 --delta 0.05 --L 1" \
        $P/inputs/pancake.athinput particles/traj_ntrack=32
    $R --purpose ... -- bash $P/scripts/run_case.sh sin32 pancake-sin "--n 32 --delta 0.05 --L 1" \
        $P/inputs/pancake.athinput particles/traj_ntrack=0 particles/hist_dcycle=1 time/tlim=8.0
    # n = 16: add mesh/nx1=16 mesh/nx2=16 mesh/nx3=16 meshblock/nx1=8 ... particles/dt=0.015625
    # n = 64 on a card: run_case.sh <name> <kind> "<args>" none, then
    #   nrpic-run submit --launcher batch --list $P/inputs/card_pancakes.list --gpu-hours 0.4 ...
    $R --purpose ... -- bash $P/scripts/run_case.sh ell64 ellipsoid "--n 64 --half 12 --ppd 2" \
        $P/inputs/ellipsoid.athinput mesh/nx1=64 mesh/nx2=64 mesh/nx3=64 \
        meshblock/nx1=32 meshblock/nx2=32 meshblock/nx3=32      # N = 32: meshblock 16
    $R --purpose ... -- bash $P/scripts/run_selfsim.sh 64
    # analyses (local, foreground), as in manifests B-20261115-173904-a7297e3 and -174405-af11300:
    python3 $P/scripts/analyze_pancake.py --out $NRPIC_RUN_DIR \
        --east 16:$S/<run>/east16 --east 32:$S/<run>/east32 \
        --east 64:$S/B-20261115-163653-f6324ea/east64:$S/B-20261115-163629-a96748c/east64 \
        --pm 32:$S/B-emd-gw-20261115-115239-69ab1db/n32 --pm 64:$S/B-emd-gw-20261115-115239-69ab1db/n64 \
        --sin 16:... --sin 32:... --sin 64:<card dir>/sin64:<particle dir>/sin64
    python3 $P/scripts/analyze_ellipsoid.py --out $NRPIC_RUN_DIR --run 32:<dir> --run 64:<dir> \
        --run 128:<dir> --dtcheck 64:<dir> --selfsim 32:<dir> --selfsim 64:<dir>

`N:DIR:PARTDIR` names a directory holding `particles.json` and `particles.nrp` when the
run directory does not (card runs from a batch list).

## Requests

To core (Newtonian mode; the earlier request is
`tracks/B-emd-gw/outbox/20261115T1340Z__to-core__newtonian-mode-for-track-b.md`):
1. N2 cannot be run without a history of one particle species: time, a, the mass of the
   species, its centroid, and its second moment about that centroid in physical
   coordinates r = a x with the first three derivatives in cosmic time (or the comoving
   moments and their conformal-time derivatives, from which the physical ones follow).
   The present columns sum over all particles about the origin with wrapped positions,
   so a patch cannot be separated from its background. This repeats item 2 of the
   earlier request; it is now the only blocker of N2.
2. The seven-point Laplacian sets the error of the mode in the pancake at the
   resolutions Track B uses (H1 of `JOURNAL.md`, confirmed at n = 16, 32, 64): the force
   on a mode with kh = 2 pi/32 is too strong by (kh)^2/12 = 3.2e-3, giving 1.4e-3 of the
   displacement at a = 2, against 1.1e-4 for the spectral pm.py with the same particles;
   it also carries half to three quarters of the jerk (d3I) error. Request: say whether
   a fourth-order option on periodic uniform meshes is planned (for example a
   Mehrstellen stencil with source correction, or a spectral solve on the periodic root
   grid); otherwise Track B quotes this second-order error with every comparison of GR
   against the mode.
3. Low priority: when tlim is not a binary multiple of the step, the driver ends with a
   remainder step of about 2.4e-13 and the d3I columns of that last record are rounding
   over the step (seen in all ellipsoid runs; the analysis drops that record). Either skip
   the difference quotient after a step far below the nominal one or say so in
   `newtonian_mode.md`. Also worth a line there: with eight particles per cell the raw
   d3I column gives the quadrupole energy within 1 % of the averaged one (N = 64).

To the lead of B-emd-gw:
4. G1 criterion 2 (`stage/G1/STATUS.md`): the N-body part now exists in the code (N1, N3
   with P1, P2). The lead decides whether the first-order convergence of the energy to
   the first crossing (N1: -9.7 % at N = 128, Richardson +0.7 %) is enough or a finer
   mesh is wanted; refined meshes in the Newtonian mode are not verified
   (`newtonian_mode.md` section 6).
5. Not done here and still owed by the baseline: N2 (blocked by item 1), the ellipsoid
   with the background term (models A and B of BASELINE.md), and the large-box energy
   comparison G3 of BASELINE.md 4.3.

To orch: none. The harness commands (`nrpic-run submit` local and batch, `finish`) worked;
the one failed analysis run was a relative path of mine.
