# Work package `newton` of track A (A-pre-3 under decision 0010)

The Newtonian precursor of the threshold scan, without a standalone N-body code: the
scan itself runs in AthenaK's Newtonian mode once core has written it (`core/newton`);
this directory holds the set-up of the reference paper, the semi-analytic references the
scan is judged against, their validation, an analysis script for the code's snapshots,
and the design of the first scan. No simulation code is written or run here. There was
no earlier content in this directory (it was empty at the start of this package), so no
earlier N-body script exists to keep.

## Contents

| File | What it is |
|---|---|
| `PAPER_SETUP.md` | the set-up of arXiv:2605.04487 (homogeneous ball, Zel'dovich deformation, EdS background) with source line numbers, the numbers it prints, and what our references say about it |
| `SCAN.md` | design of the first scan in the code: grid, particle numbers, ball radius, mesh, inputs (what `problems/ic/make_ic.py` lacks), quantities to record, acceptance tests, cost from measured costs |
| `tophat.py` | spherical top-hat in EdS: the exact cycloid through any (R, dR/dt) (turnaround, collapse), Zel'dovich spherical data, EdS growing-mode constants |
| `ellipsoid.py` | cold homogeneous ellipsoid in EdS: axis equations with Carlson R_D coefficients, three placements of the patch (isolated, embedded, added), optional end-point special-relativistic kinematics, collapse events with pass-through, hoop proxy, Zel'dovich hoop of 1609.01588 |
| `validate.py` | predictions P1-P7 of `JOURNAL.md` as checks; figures `figs/fig_tophat`, `fig_alphas`, `fig_plane_limit`, `fig_paper_cases` |
| `scan_refs.py` | reference tables over (e, p) at delta_L = 1 (scale free): `tables/ellipsoid_first_collapse.csv`, `tophat.csv`, `sr_estimate.csv`; figures `figs/fig_scan_hoop_time`, `fig_scan_hoop_ratio` |
| `compare_snapshots.py` | reads AthenaK particle snapshots (NRPSNAP1), semi-axes from second moments, collapse times, hoop proxy, against the reference; `--selftest` on synthetic snapshots |
| `run_and_register.py` | runs one of the scripts into `scratch/A-emd-pbh/<run_id>/` and writes the manifest |
| `manifests/` | copies of the run manifests of this package (see "Open" for why) |
| `figs/`, `tables/` | figures and tables copied from the registered runs below |
| `JOURNAL.md` | predictions before each test and outcomes after it |

## Rerun

From the worktree root (one core, seconds each; numpy, scipy, matplotlib of the system
Python suffice):

    python3 tracks/A-emd-pbh/newton/run_and_register.py validate.py "<purpose>"
    python3 tracks/A-emd-pbh/newton/run_and_register.py scan_refs.py "<purpose>"
    python3 tracks/A-emd-pbh/newton/run_and_register.py compare_snapshots.py "<purpose>" --selftest

On a run of the code: `python3 tracks/A-emd-pbh/newton/compare_snapshots.py --snaps
'<dir>/<base>.part.*.bin' --abg ALPHA BETA GAMMA --model isolated --length-unit 2
--out <dir>` (length unit 2 for files in the NRPIC001 convention M = 1; the time origin
defaults to the reference start t_0).

## Runs

| Run id | What | Wall time |
|---|---|---|
| A-emd-pbh-20261115-113103-9832afd | validation P1-P7 | 4.9 s |
| A-emd-pbh-20261115-113152-cd9539e | reference tables and figures (supersedes ...113108-9832afd, same numbers) | 10.3 s |
| A-emd-pbh-20261115-113822-87cba08 | snapshot-analysis self-test (supersedes ...113807-e02c969, same numbers) | 1.5 s |

All on the login node, one core, no card time.

## What was established

1. Top-hat reference: the cycloid through Zel'dovich data matches direct integration to
   5e-12 in the turnaround and collapse times; started early, the linear contrasts at
   turnaround and collapse converge linearly in a_0 lambda to 1.0624 and 1.6865 (run
   ...113103, `figs/fig_tophat.png`).
2. Ellipsoid reference: coefficients equal the spheroid closed forms to 1.3e-13; the
   spherical limit equals the cycloid to 1e-11; the plane limit of the embedded
   placement converges to the exact Zel'dovich collapse as 10^-k down to 1.5e-7; the
   Zel'dovich hoop of 1609.01588 is reproduced to 3e-15; the Newtonian problem with the
   paper's start is scale free to 1e-13 (run ...113103).
3. The start convention of 2605.04487 (a_0 = 1/(2 alpha), t_0 = t_k a_0^(3/2)) reproduces
   its four printed start times (run ...113103).
4. Its two printed event times (first collapse 22.536 t_k, second 29.097 t_k) are matched
   to +0.9 and +0.1 percent only by the "added" placement (patch mass on top of the
   background deceleration); the consistent placements are 6 to 10 percent late, and SR
   kinematics and softening would delay them further. Reading: the paper's code evolves
   an effective density rho_b + rho_patch [JUDGEMENT; one of three appendix cases
   does not fit; `PAPER_SETUP.md`, `JOURNAL.md` entry 3].
5. Newtonian hoop line (amplitude at which the pancake's hoop equals 2 pi r_g at the
   first collapse): delta_L,th = 7 to 9.5 e for e <= 0.05 (isolated, p = 0: 0.089 at e = 0.01,
   0.359 at 0.05, 0.592 at 0.1, 0.855 at 0.2); the ellipsoid pancake is 0.64 to 0.91 of
   the Zel'dovich one, so this line lies below that of 1609.01588 (run ...113152,
   `figs/fig_scan_hoop_time.png`, `fig_scan_hoop_ratio.png`).
6. Special-relativistic kinematics (end-point estimate) delays the first collapse by
   0.7-0.9, 1.4-1.8, 4-5 and 13-17 percent at delta_L = 0.05, 0.1, 0.3, 1 (e = 0.05 to
   0.4, p = 0; run ...113152, `tables/sr_estimate.csv`).
7. The snapshot analysis recovers the first-collapse time of a synthetic run to 1.2e-5
   and the axis correctly (run ...113822, `figs/fig_axes_selftest.png`).

## Open

- The scan has not run: the Newtonian mode is not in the source (`core/newton` had no
  commit beyond `main`), and the particle generator lacks the deformed ball (SCAN.md,
  section 4). No card time was used; pending runs: the 32 runs of SCAN.md, section 2.
- The appendix case (0.16, 0.10, 0.04) and the sigma = 0.01 case do not fit the "added"
  reading as well as the main case (+7.7 percent and -3.5 percent on the first
  collapse); whether their snapshot times are event times is unknown [TO VERIFY].
- The end-point SR model is an estimate (a relativistic patch does not stay
  homogeneous); the softening of the paper's force is not modelled.
- The run manifests in `tracks/A-emd-pbh/runs/` are not in git: the pattern `runs/` of
  the repository's `.gitignore` (line 12) also matches `tracks/*/runs/`, and CLAUDE.md
  forbids committing ignored paths. The manifests are on disk there and copied to
  `manifests/` here.
- Not done: the glass-plus-whitening particle load of the paper (not needed for the
  references; SCAN.md proposes the lattice).

## Requests

- core (`core/newton`): Newtonian gravity for the same particles with isolated boundary
  values (the multigrid of `athenak/src/multigrid` with multipole boundaries); an
  optional external acceleration -(4 pi/3) G rho_b(t) r, rho_b = 1/(6 pi G t^2),
  t = t_0 + run time, to reproduce 2605.04487; optional special-relativistic push
  (u = gamma v); particle snapshots at chosen times; optionally the second-moment tensor
  per species in the history. Acceptance tests this package will run on it: SCAN.md,
  section 5.
- core (`problems/ic/make_ic.py`): a model for the Zel'dovich-deformed homogeneous ball
  with optional background shell, as specified in SCAN.md, section 4, item 2.
- kb: check in the code of 2605.04487 (its reference "escriva_github") whether the pair
  force sums the full patch mass while the comoving equation keeps the background term
  (our item 4); index its code if the knowledge base covers code (K6-K7).
- orch: anchor the ignore pattern (`/runs/` instead of `runs/`) so that
  `tracks/<ID>/runs/*/manifest.json` can be committed, or say where manifests belong.
- A lead / expball helper: choose the construction of the deformed ball for the GR scan
  (compensated patch in a shell, SCAN.md section 1) and note the horizon limit on the ball
  radius (SCAN.md section 3).
