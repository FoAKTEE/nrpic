# Work package `newton` of track A (A-pre-3 under decision 0010)

The Newtonian precursor of the threshold scan. Wave 1 (2026-11-15, morning) wrote the
semi-analytic references, their validation and the scan design; wave 2 (same day,
afternoon) ran the first cases in AthenaK's Newtonian mode (`<particles> pusher =
newton`, release `core-v0.3`, `coord/INTERFACES/newtonian_mode.md`) with the release
processor executable and one card job. No simulation code is written here (decision 0010):
the gravity, deposit and push are AthenaK's; this directory holds references, a particle
file writer that feeds the code, the run driver, the analysis and the results.

## Contents

| File | What it is |
|---|---|
| `PAPER_SETUP.md` | the set-up of arXiv:2605.04487 (homogeneous ball, Zel'dovich deformation, EdS background) with source line numbers |
| `SCAN.md` | design of the scan (sections 1-6, wave 1); results of the first points in the code (section 7) and the proposed range of the full-relativity scan (section 8, wave 2) |
| `tophat.py`, `ellipsoid.py` | references: the cycloid through any (R, dR/dt); the cold homogeneous ellipsoid (isolated, embedded, added placements; end-point SR estimate; hoop proxy) |
| `validate.py`, `scan_refs.py` | wave 1: checks P1-P7 of the references; reference tables over (e, p) |
| `compare_snapshots.py` | wave 1: semi-axes from AthenaK snapshots; self-test on synthetic snapshots |
| `make_deformed_ball.py` | wave 2: writes the Zel'dovich-deformed homogeneous ball in the existing particle format (`.nrp`) with a JSON of the references of the sampled ball; the work-around for what the generators lack (below) |
| `newton_campaign.py` | wave 2: the cases (top-hat, scan, card), particle files, AthenaK command lines (release processor executable, `problems/newton/isolated.athinput` plus overrides), runs them in parallel; `--prepare-only` writes the list of a card batch |
| `analyze_newton.py` | wave 2: reads `newton.newton.hst` of each case; radius or semi-axes from the second-moment tensor about the centre of mass; turnaround, infall and collapse times against the cycloid; first collapse, axes, hoop ratio against the isolated ellipsoid; tables and figures |
| `gr_range.py` | wave 2: the proposed range of the full-relativity scan (hoop amplitude, ball-radius limit, SR delay, infall speed, seeds) |
| `register.py` | wave 2: registers a run by hand (manifest under `../runs/<run_id>/`) when `harness/bin/nrpic-run` refuses (see Requests) |
| `run_and_register.py` | wave 1: registers runs of the reference scripts |
| `figs/`, `tables/` | figures and tables copied from the registered runs (wave-2 files are named `*newton*` and `gr_scan_range.csv`) |
| `manifests/` | wave-1 copies of manifests (the ignore rule is fixed on main; manifests now live in `../runs/`) |
| `JOURNAL.md` | predictions before each test and outcomes after it (entries 1-4 wave 1, 5-8 wave 2) |

## What the particle generators lack for the deformed ball (wave 2, exact)

Neither generator of the repository can write the initial data of the scan:

1. `problems/newton/make_ic.py` (core's Newtonian test generator) has the models `point`,
   `ball`, `wave` (line 46). Its `ball` is a lattice ball at rest with an optional uniform
   velocity and rigid rotation, `u = velocity + omega x (x - c)` (line 84). It lacks:
   (a) an anisotropic position map x_i = a0 (1 - a0 lambda_i) xi_i (the Zel'dovich
   deformation); (b) a velocity field linear in position with a diagonal, non-isotropic
   matrix, v_i = H0 a0 (1 - 2 a0 lambda_i) xi_i (Hubble flow plus peculiar velocity); a
   rigid rotation is antisymmetric and a uniform velocity is constant, so neither can
   express it; (c) parameters in (delta_L, e, p) or (alpha, beta, gamma) with the start
   a0 = 1/(2 alpha) and t0 = t_k a0^(3/2); (d) a random rotation of the lattice against the
   deformation axes; (e) the volume radius of the sampled lattice ball in the metadata,
   which the references need (it moves the cycloid collapse time by +0.31 per cent for
   lattice spacing 0.05, JOURNAL entry 5); (f) an optional background shell with Hubble
   velocity and a species id (SCAN.md section 1; not needed for the first points).
2. `problems/ic/make_ic.py` (relativistic generator) has `os`, `st`, `prolate`, `jeans`
   (line 67); its ball sampler `python/nrpic/sampling.py` sample_os (line 117) is Oppenheimer-Snyder dust at rest (u_i = 0). For the
   full-relativity deformed ball it lacks the same map and velocities, the covariant u_i
   of the A-pre-1 slicing, and the constraint solve after the deformation (core's wave-2
   initial-data work, decision 0010 item 4).

Work-around in this directory: `make_deformed_ball.py` writes the existing `.nrp` format
(`python/nrpic/io.py` write_nrp) with (a)-(e) and centring (centre of mass and net
momentum removed). It feeds the code; it does not simulate. The smallest change to
core's generator that would replace it: two options of `ball`, `--axes S1 S2 S3`
(x = c + S xi) and `--vgrad D1 D2 D3` (v = D xi), plus `--rotate SEED` and the volume
radius in the JSON (Requests).

## Rerun

From the worktree root (`.venv` of the worktree: numpy, scipy, matplotlib):

    # processors (one core per case; J cases at once); output in $NRPIC_RUN_DIR or --out
    .venv/bin/python tracks/A-emd-pbh/newton/register.py local --purpose "..." --cores 6 \
        -- .venv/bin/python tracks/A-emd-pbh/newton/newton_campaign.py --campaign tophat --jobs 6
    .venv/bin/python tracks/A-emd-pbh/newton/register.py local --purpose "..." --cores 5 \
        -- .venv/bin/python tracks/A-emd-pbh/newton/newton_campaign.py --campaign scan --jobs 5
    # card: particle files and batch list, then one Slurm job (25 min limit)
    .venv/bin/python tracks/A-emd-pbh/newton/register.py local --purpose "..." \
        -- .venv/bin/python tracks/A-emd-pbh/newton/newton_campaign.py --campaign card --prepare-only
    .venv/bin/python tracks/A-emd-pbh/newton/register.py batch --purpose "..." \
        --list <prepare run dir>/batch.list --wall 00:25:00
    .venv/bin/python tracks/A-emd-pbh/newton/register.py finish <batch run id>
    # analysis and range (seconds)
    .venv/bin/python tracks/A-emd-pbh/newton/register.py local --purpose "..." -- \
        .venv/bin/python tracks/A-emd-pbh/newton/analyze_newton.py \
        --tophat <tophat run dir> [<card run dir>] --scan <scan run dir> [<card run dir>] \
        --prep <prepare run dir> --out <dir>
    .venv/bin/python tracks/A-emd-pbh/newton/gr_range.py --results <dir>/newton_results.json --out <dir>

With `harness/bin/nrpic-run submit --launcher local` instead of `register.py local` when the
worktree is clean (the cost run was registered that way). Wave-1 reruns: `run_and_register.py`.

## Runs (wave 2)

RUNS_TABLE

## What was established (wave 2)

ESTABLISHED

## What was established (wave 1, unchanged)

1. Top-hat reference: the cycloid through Zel'dovich data matches direct integration to
   5e-12 in the turnaround and collapse times (run A-emd-pbh-20261115-113103-9832afd).
2. Ellipsoid reference: coefficients equal the spheroid closed forms to 1.3e-13; spherical
   limit equals the cycloid to 1e-11; plane limit converges to Zel'dovich as 10^-k; the
   Zel'dovich hoop of 1609.01588 reproduced to 3e-15; the problem with the paper's start
   is scale free to 1e-13 (same run).
3. The start convention of 2605.04487 reproduces its four printed start times; its two
   printed event times are matched to +0.9 and +0.1 per cent only by the "added" placement
   [JUDGEMENT on the paper's code; `PAPER_SETUP.md`, JOURNAL entry 3].
4. Newtonian hoop line delta_L,th = h_1 delta_L (isolated, p = 0): 0.089 at e = 0.01,
   0.359 at 0.05, 0.592 at 0.1, 0.855 at 0.2, 0.968 at 0.3 (run
   A-emd-pbh-20261115-113152-cd9539e).
5. End-point SR kinematics delays the first collapse by 0.7-0.9, 1.4-1.8, 4-5 and 13-17
   per cent at delta_L = 0.05, 0.1, 0.3, 1 (same run, `tables/sr_estimate.csv`).
6. The snapshot analysis recovers the first-collapse time of a synthetic run to 1.2e-5
   (run A-emd-pbh-20261115-113822-87cba08).

## Open

OPEN

## Requests

REQUESTS
